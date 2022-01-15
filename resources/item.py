from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',type=float, required=True, help='This field must not be blank')
    parser.add_argument('store_id',type=int, required=True, help='This field must not be blank')

    @jwt_required()
    def get(self, name):
        item = ItemModel.get_item_by_name(name)

        if item:
            return {'item': item.json()}, 200
        return {'msg': f'Item does not exist'}, 404

    def post(self, name):
        item = ItemModel.get_item_by_name(name)       
        data = Item.parser.parse_args()
        
        if item:
            return {'msg':'item already exists'}, 400

        new_item = ItemModel(name, **data)

        try:
            new_item.save_to_db()
        except:
            return {'msg': 'An error accured during insertion'}, 500

        return {'item': new_item.json()}, 201

    def delete(self, name):
        item = ItemModel.get_item_by_name(name)
        if item:
            item.delete_from_db() 
        return {'msg':'item has been deleted'}

    def put(self, name):
        item = ItemModel.get_item_by_name(name)
        data = Item.parser.parse_args()

        if item is None:
            item = ItemModel(name,**data)
        else:
            item.price = data['price']
            item.store_id = data['store_id']
        
        item.save_to_db()

        return {'item': item.json()}, 202

class ItemList(Resource):
    def get(self):
        return {'items': list(map(lambda x: x.json() , ItemModel.query.all()))}, 200 