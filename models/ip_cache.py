import datetime
from object_SQLAlchemy import db
from logging_util import resource_logger as logger


class IpCache(db.Model):
    __tablename__ = "ip_cache"

    ip = db.Column(db.String(80), primary_key=True, unique=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, **kwargs):
        super(IpCache, self).__init__(**kwargs)

    def json(self):
        return {
            "ip": self.ip,
            "created": self.created,
        }

    @classmethod
    def get_all(cls):
        return [obj.ip for obj in cls.query.all()]

    def save_to_db(self):
        res = IpCache.query.filter_by(ip=self.ip).all()
        if not res:
            db.session.add(self)
            db.session.commit()
            logger.debug("Created ip: {}".format(str(self.json())))
            return True
        logger.debug("Ip already exists: {}".format(str(self.json())))
        return False

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
        logger.debug("Deleted ip: {}".format(str(self.json())))
