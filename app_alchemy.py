import os
import config
import traceback
import simplejson
from object_SQLAlchemy import db
from flask import Flask, render_template, jsonify, request, make_response
from flask_jwt import JWT, jwt_required, JWTError
from flask_restful import Api
from threading import Thread

from resources.users_alchemy import UserRegister
from security_alchemy import authenticate, identity
from resources.contacts_resource import Contact, ContactList
from resources.error_handlers import api_errors
from models.ip_cache import IpCache
from post_man import SMTPPostMan
from logging_util import email_logger, err_log


app = Flask(__name__, template_folder=".", static_folder="assets")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    config.db_conn_str
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = config.app_secret_key
api = Api(app, errors=api_errors)

if config.debug_local:
    db.init_app(app=app)

jwt = JWT(app, authentication_handler=authenticate, identity_handler=identity)


api.add_resource(UserRegister, '/register')
api.add_resource(Contact, "/call_me/<string:name>")
api.add_resource(ContactList, "/contacts")


mailer = SMTPPostMan(
    smtp_host=config.smtp_host,
    smtp_port=config.smtp_port,
    addr=config.addr_email,
    pwd=config.pwd_email
)


class BaseApiException(Exception):
    def __init__(self, msg, code):
        self.msg = msg
        self.code = code


class BadRequestError(BaseApiException):
    """400 Bad Request"""
    def __init__(self, msg):
        super().__init__(msg=msg, code=400)


class NotFoundError(BaseApiException):
    """404 Not Found"""
    def __init__(self, msg):
        super().__init__(msg=msg, code=404)


def async_exec(f):
    def wrapper(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs)
        t.start()
    return wrapper


@async_exec
def send_async_email(exc_traceback):
    with app.app_context():
        try:
            mailer.send_email(
                send_to=["virgovica@gmail.com"],
                subject="Critical Error",
                text=exc_traceback
            )
        except Exception:
            email_logger.critical("Failed to send email", exc_info=True)


@app.errorhandler(Exception)
def handle_error_app(e):
    err_log.critical("big trap", exc_info=True)
    send_async_email(traceback.format_exc())
    return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify(message="Not found.", status_code=404), 404


@app.errorhandler(BadRequestError)
def bad_request(e):
    return jsonify(message=e.msg, status_code=e.code), 400


@app.errorhandler(JWTError)
def jwt_error(e):
    return jsonify(message=e.msg, status_code=e.code)


@app.route("/", methods=["GET"])
def render_cv():
    visitor_ip = get_real_ip(req_obj=request)
    new_ip = IpCache(ip=visitor_ip)
    new_ip.save_to_db()
    resp = make_response(render_template("index.html"))
    resp.cache_control.public = True
    resp.cache_control.max_age = 300
    return resp


def get_real_ip(req_obj):
    return req_obj.environ.get(
        'HTTP_X_FORWARDED_FOR', req_obj.environ.get(
            "X_FORWARDED_FOR", req_obj.environ.get(
                "X-Forwarded-For", req_obj.remote_addr
            )
        )
    )


@app.route("/raise", methods=["GET"])
def raise_it():
    raise RuntimeError()


@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    return jsonify(
        get_real_ip(req_obj=request)
    ), 200


@app.route("/getipset", methods=["GET"])
@jwt_required()
def get_ip_set():
    return jsonify(
        ips=IpCache.get_all()
    ), 200


@app.route("/addip", methods=["POST"])
@jwt_required()
def add_ip():
    new_ip = simplejson.loads(request.data).get("ip", None)
    if not new_ip:
        raise BadRequestError("Parameter 'ip' unfilled.")
    if not isinstance(new_ip, str):
        raise BadRequestError("Parameter 'ip' must be string.")
    new_ip_obj = IpCache(ip=new_ip)
    if new_ip_obj.save_to_db():
        return jsonify(message="{} added.".format(new_ip_obj.ip)), 201

    return jsonify(message="ip already in set"), 200


if config.debug_local:
    @app.before_first_request
    def create_tables():
        db.create_all()


if __name__ == '__main__':
    app.run(port=5000)

