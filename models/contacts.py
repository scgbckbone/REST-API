from object_SQLAlchemy import db


class Contacts(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    contact_no = db.Column(db.String(80))

    def __init__(self, name, contact_no):
        self.name = name
        self.contact_no = contact_no

    def json(self):
        return {"name": self.name, "contact": self.contact_no}

    @classmethod
    def findbyname(cls, name):
        return cls.query.filter_by(
            name=name).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()