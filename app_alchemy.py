import os
from flask import Flask, render_template
from flask_jwt import JWT
from flask_restful import Api

from resources.items_alchemy import Item, ItemList
from resources.users_alchemy import User_register
from security_alchemy import authenticate, identity
from resources.store_alchemy import Store, StoreList
from resources.contacts_resource import Contact, ContactList
from resources.error_handlers import api_errors

app = Flask(__name__, template_folder=".", static_folder="assets")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///DATA.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'andrej2154'
api = Api(app, errors=api_errors)

jwt = JWT(app, authenticate, identity)

api.add_resource(Item, '/item/<string:name>')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(StoreList, '/stores')
api.add_resource(User_register, '/register')
api.add_resource(Contact, "/call_me/<string:name>")
api.add_resource(ContactList, "/contacts")


@app.route("/", methods=["GET"])
def render_cv():
    return render_template("index.html")


if __name__ == '__main__':
    from object_SQLAlchemy import db
    db.init_app(app)
    app.run(port=5000)

