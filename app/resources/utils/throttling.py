import redis
from functools import wraps
from datetime import datetime, timedelta
from flask import request
import hashlib

redis_host = "127.0.0.1"
redis_port = 6379
redis_db = 13


class Throttle(object):
    """
    Decorator that prevents a function from being called more than once every
    time period or number of times for time period.
    If 'strategy' parameter is 1 - time between consequent request is defined.
    if 'strategy' parameter is 2 - number of request for time span is defined.

    To create a function that cannot be called more than once a minute:
        @Throttle('1/m', strategy=1)
        def my_function():
            pass

    To create a function that can be called only 23 times in 1 minute
        @Throttle('23/m', strategy=2)
        def my_function():
            pass
    """
    class InvalidPeriodicityArgumentError(Exception):
        """Invalid periodicity parameter. Correct form 'number/s|m|h'"""

    class RedisOperationalError(Exception):
        """Failed to insert/get data into/from Redis"""

    class BoundaryReachedError(Exception):
        """Api call periodic limit reached."""

    acro_sec_map = {
        "s": 1,
        "m": 60,
        "h": 60 * 60,
        "d": 60 * 60 * 24
    }
    dt_format = "%Y-%m-%d %H:%M:%S"

    def __init__(self, periodicity, strategy=2):
        self.periodicity = periodicity
        self.throttle_period = timedelta(
            seconds=self.parse_periodicity_param()[1]
        )
        self.strategy = strategy
        self.count_exp = self.parse_periodicity_param()[2]
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db
        )

    def parse_time_delta(self):
        """
        Parses 'self.throttle_period' and returns readable representation
        of throttling interval.
        :return: str
        """
        parsed = []
        template = {0: "hour/s", 1: "minute/s", 2: "second/s"}
        args = str(self.throttle_period).split(":")

        for index, k in enumerate(args):
            if int(k) > 0:
                parsed.append(k + " " + template[index])

        return " ".join(parsed)

    def parse_periodicity_param(self):
        """
        Parses periodicity parameter, checks whether it is in a correct form
        and returns a dictionary with two keys (1,2) that correlates to
        possible strategies.
        :return: dict
        """
        try:
            no, acronym = self.periodicity.split("/")
        except Exception:
            raise self.InvalidPeriodicityArgumentError()
        else:
            if acronym not in self.acro_sec_map:
                raise self.InvalidPeriodicityArgumentError(
                    "Wrong acronym. Options s|m|h"
                )
            if int(no) > self.acro_sec_map[acronym]:
                raise self.InvalidPeriodicityArgumentError(
                    "Provided number too big."
                )
            return {
                1: self.acro_sec_map[acronym] / float(no),
                2: {"counter": int(no), "expire": self.acro_sec_map[acronym]}
            }

    @staticmethod
    def hashed_key(key):
        return hashlib.sha256(key.encode()).hexdigest()

    @staticmethod
    def create_redis_key_from_tp(tp_name, func_name):
        """
        Creates key to be stored in redis from team space name and api function
        name. Separator between the two is colon ':'.
        :param tp_name: str: team space name
        :param func_name: str: decorated function name
        :return: str
        """
        return Throttle.hashed_key(tp_name + ":" + func_name)

    def get_last_call_time(self, tp_name, func_name):
        """
        Takes in team space name and decorated function name, creates redis key
        from them, check if it is in redis, if yes - value is returned, if not -
        None is returned.
        :param tp_name: str: team space name
        :param func_name: str: name of decorated function
        :return: datetime or None
        """
        key = Throttle.create_redis_key_from_tp(tp_name, func_name)
        try:
            dt = self.redis_client.get(key)
        except Exception as e:
            raise self.RedisOperationalError(e)
        if not dt:
            return datetime.min
        else:
            dt = dt.decode()
            dt = datetime.strptime(dt, self.dt_format)
            return dt

    def save_call_time_to_redis(self, tp_name, dt, func_name):
        """
        Takes in team space name and datetime object and saves it to redis.
        If saving was not successful error message is printed.
        :param tp_name: str: team space name
        :param dt: datetime
        :param func_name: str: name of decorated function
        :return:
        """
        key = Throttle.create_redis_key_from_tp(tp_name, func_name)
        dt = dt.strftime(self.dt_format)
        try:
            self.redis_client.set(
                key, dt, ex=self.throttle_period.seconds
            )
        except Exception as e:
            raise self.RedisOperationalError(e)

    def save_counter_to_redis(self, tp_name, func_name):
        """
        Saves key value pair into redis. Key is team space name +':'+ func_name.
        Value consists of two more key value pairs:
            dt: datetime when this object was saved to redis
            counter: initially 1
        :param tp_name: str: team space name
        :param func_name: str: name of decorated function
        :return: None
        """
        key = Throttle.create_redis_key_from_tp(tp_name, func_name)
        now = datetime.utcnow().strftime(self.dt_format)
        mapping = {"dt": now, "counter": 1}
        try:
            self.redis_client.hmset(key, mapping)
            self.redis_client.expire(key, self.count_exp["expire"])
        except Exception as e:
            raise self.RedisOperationalError(e)

    def get_check_adjust_counter(self, tp_name, func_name):
        """
        Get value from redis based on key(team_space:func_name), check whether
        counter value is in limits and if yes increments counter.
        :param tp_name: str: team space name
        :param func_name: str: name of decorated function
        :return: bool or datetime
        """
        key = Throttle.create_redis_key_from_tp(tp_name, func_name)
        try:
            is_there = self.redis_client.hgetall(key)
        except Exception as e:
            raise self.RedisOperationalError(e)
        if not is_there:
            return False
        else:
            is_there = {k.decode(): v.decode() for k, v in is_there.items()}
            if int(is_there["counter"]) < self.count_exp["counter"]:
                try:
                    self.redis_client.hincrby(key, "counter")
                except Exception as e:
                    raise self.RedisOperationalError(e)
                return True
            expire_td = timedelta(seconds=self.count_exp["expire"])
            set_dt = datetime.strptime(is_there["dt"], self.dt_format)
            return set_dt + expire_td

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.strategy == 1:
                now = datetime.utcnow()
                t_of_last_call = self.get_last_call_time(
                    request.remote_addr, func.__name__
                )
                time_since_last_call = now - t_of_last_call

                if time_since_last_call > self.throttle_period:
                    self.save_call_time_to_redis(
                        request.remote_addr, now, func.__name__
                    )
                    return func(*args, **kwargs)
                else:
                    raise self.BoundaryReachedError((
                        "Max limit reached. "
                        "This method can only be called once in {} interval."
                    ).format(self.parse_time_delta()))
            elif self.strategy == 2:
                can_call = self.get_check_adjust_counter(
                    request.remote_addr, func.__name__
                )
                if isinstance(can_call, datetime):
                    raise self.BoundaryReachedError((
                        "Max limit reached. Limit: {} (no. calls/per interval)"
                        "\nNext window opens at {}\tcurrent time: {}"
                    ).format(
                        self.periodicity, can_call,
                        datetime.utcnow().strftime(self.dt_format)
                    ))
                elif can_call is True:
                    return func(*args, **kwargs)
                elif can_call is False:
                    self.save_counter_to_redis(
                        request.remote_addr, func.__name__
                    )
                    return func(*args, **kwargs)

        return wrapper
