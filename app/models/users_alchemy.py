from object_SQLAlchemy import db
from werkzeug.security import generate_password_hash
from logging_util import resource_logger as logger


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(120))

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password=password)

    def json(self):
        return {
            "username": self.username,
            "id": self.id
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        logger.debug("Created user: {}".format(str(self.json())))

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
        logger.debug("Deleted user: {}".format(str(self.json())))

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def get_all_users(cls):
        return cls.query.all()
