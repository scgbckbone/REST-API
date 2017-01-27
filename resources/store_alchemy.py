from flask_restful import Resource
from models.store_alchemy import StoreModel

class Store(Resource):

    def get(self, name):
        store = StoreModel.findbyname(name)
        if store:
            return store.json()    # 200 - but it is default so we do not have to return it
        return {"message": "Store not found"}, 404

    def post(self, name):
        if StoreModel.findbyname(name):
            return {'message': "Store with name '{}' already exists.".format(name)}, 400

        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            return {"message": "An error occurred while creating the store"}, 500
        return store.json(), 201

    def delete(self, name):
        store = StoreModel.findbyname(name)
        if store:
            try:
                store.delete_from_db()
            except:
                return {"message": "An error ocurred while deleting the store"}, 500
        return {"message": "Store deleted"}



class StoreList(Resource):
    def get(self):
        return {"stores": [store.json() for store in StoreModel.query.all()]}
