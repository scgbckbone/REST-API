from object_SQLAlchemy import db
from logging_util import resource_logger as logger


class Contacts(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    contact_no = db.Column(db.String(80))
    btc_address_1 = db.Column(db.String(80))
    btc_address_2 = db.Column(db.String(80))

    def __init__(self, name, contact_no, btc1, btc2):
        self.name = name
        self.contact_no = contact_no
        self.btc_address_1 = btc1
        self.btc_address_2 = btc2

    def json(self):
        return {
            "name": self.name,
            "contact": self.contact_no,
            "btc_address_1": self.btc_address_1,
            "btc_address_2": self.btc_address_2
        }

    @classmethod
    def findbyname(cls, name):
        return cls.query.filter_by(
            name=name).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        logger.debug("Saved contact: {}".format(str(self.json())))

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
        logger.debug("Deleted contact: {}".format(str(self.json())))