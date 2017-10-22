from flask_restful import reqparse, Resource
from models.contacts import Contacts
from flask_jwt import jwt_required
from .utils import throttling


class Contact(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        'contact_no',
        type=str,
        required=True,
        help="This field cannot be left blank"
    )

    def get(self, name):
        contact = Contacts.findbyname(name)
        if contact:
            return contact.json()
        return {"message": "Contact does not exist."}, 404

    @throttling.Throttle("10/m", strategy=2)
    def post(self, name):
        if Contacts.findbyname(name):
            return {
                'message': "Contact with name '{}' already exists.".format(name)
            }, 400
        data = Contact.parser.parse_args()
        contact = Contacts(name, **data)
        try:
            contact.save_to_db()
        except:
            return {"message": "An error occurred inserting the contact"}, 500

        return contact.json(), 201

    @jwt_required()
    def delete(self, name):
        contact = Contacts.findbyname(name)
        if contact:
            try:
                contact.delete_from_db()
            except:
                return {"message": "An error occurred deleting the contact"}, 500
            else:
                return {"message": "Item deleted"}
        return {"message": "Contact does not exist."}, 404

    @jwt_required()
    def put(self, name):
        data = Contact.parser.parse_args()
        contact = Contacts.findbyname(name)

        if contact is None:
            try:
                contact = Contacts(name, **data)
            except:
                return {"message": "An error occurred inserting the contact"}, 500
            else:
                try:
                    contact.save_to_db()
                except:
                    return {
                        "message": "An error occurred inserting the contact"
                    }, 500
        contact.contact_no = data["contact_no"]
        try:
            contact.save_to_db()
        except:
            return {"message": "An error occurred inserting the contact"}, 500
        else:
            return contact.json(), 201


class ContactList(Resource):
    @jwt_required()
    def get(self):
        return {
            "contacts": [contact.json() for contact in Contacts.query.all()]
        }