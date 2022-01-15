from flask_restful import Resource, reqparse

from models.user import UserModel

class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help='Username must not be blank!')
    parser.add_argument('password', type=str, required=True, help='Username must not be blank!')

    def post(self):
        data = UserRegister.parser.parse_args()
        if UserModel.find_by_username(data['username']):
            return {'msg': 'Username already exists'}, 400
        
        user = UserModel(**data)
        try:
            user.save_to_db()
        except:
            return {'msg':'An error accured during insertion'}, 500

        return {'user': user.json()}, 201



