from flask_restful import reqparse, Resource
from flask_jwt import jwt_required
from models.items_alchemy import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
             type=float,
             required=True,
             help="This field cannot be left blank"
    )
    parser.add_argument('store_id',
             type=int,
             required=True,
             help="Every item need a store id"
    )

    @jwt_required()
    def get(self, name):
        item = ItemModel.findbyname(name)
        if item:
            return item.json()
        return {"message": "Item does not exist"}, 404


    def post(self, name):
        if ItemModel.findbyname(name):
            return {'message': "An item with name '{}' already exists.".format(name)}, 400
        data = Item.parser.parse_args()
        item = ItemModel(name, **data)
        try:
            item.save_to_db()
        except:
            return {"message": "An error occurred inserting the item"}, 500   # internal server error

        return item.json(), 201

    def delete(self, name):
        item = ItemModel.findbyname(name)
        if item:
            item.delete_from_db()
        return {"message": "Item deleted"}


    def put(self, name):
        data = Item.parser.parse_args()
        item = ItemModel.findbyname(name)

        if item is None:
            try:
                item = ItemModel(name, **data)
            except:
                return {"message": "An error occurred inserting the item"}, 500
        else:
            try:
                item.price = data['price']
            except:
                return {"message": "An error occurred inserting the item"}, 500


        item.save_to_db()
        return item.json()


class ItemList(Resource):
    def get(self):
        return {"items": [item.json() for item in ItemModel.query.all()]}  # or {"items": list(map(lambda x: x.json(), ItemModel.query.all()))
