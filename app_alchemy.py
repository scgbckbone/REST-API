from flask import Flask
from flask_jwt import JWT
from flask_restful import Api

from resources.items_alchemy import Item, ItemList
from resources.users_alchemy import User_register
from security_alchemy import authenticate, identity
from resources.store_alchemy import Store, StoreList

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///DATA.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'andrej2154'
api = Api(app)

jwt = JWT(app, authenticate, identity)

api.add_resource(Item, '/item/<string:name>')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(StoreList, '/stores')
api.add_resource(User_register, '/register')

if __name__ == '__main__':
    from object_SQLAlchemy import db
    db.init_app(app)
    app.run(port=5000, debug=True)

