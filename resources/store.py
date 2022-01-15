from importlib.resources import Resource
from models.store import StoreModel
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

class Store(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name',type=str, required=True, help='This field must not be blank')

    @jwt_required()
    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return {'store': store.json()}, 200
        return {'msg': 'Store was not found'}, 404

    def post(self, name):
        if StoreModel.find_by_name(name):
            return {'msg' : 'Store already exists'}, 400
        
        new_store = StoreModel(name)
        try:
            new_store.save_to_db()
        except:
            return {'msg' : 'Error while inserting'}, 500

        return {'store': new_store.json()}

    def delete(self, name):
        store = StoreModel.find_by_name(name)

        if store is None:
            return {'msg' : 'Store does not exist'}, 404
        
        try:
            store.delete_from_db()
        except:
            return {'msg' : 'Error while deleteing'}, 500
        
        return {'msg': 'store was deleted'}, 200
        

    def update(self, name):
        pass

class StoreList(Resource):

    def get(self):
        return {'stores': list(map(lambda x: x.json() , StoreModel.query.all()))}, 200

