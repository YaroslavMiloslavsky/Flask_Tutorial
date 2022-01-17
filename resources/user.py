from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import(create_access_token, 
                            create_refresh_token, 
                            jwt_required,
                            get_jwt_identity,
                            get_jwt)

from models.user import UserModel

from blacklist import BLACKLIST

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


class User(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help='Username must not be blank!')
    parser.add_argument('password', type=str, required=True, help='Username must not be blank!')

    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if user:
            return user.json(), 200
        return {'msg': 'No user was found'}, 404
    

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        
        try:
            user.delete_from_db()
        except:
            return {'msg': 'Error while deleteing'}, 500

        return {'msg': 'User was deleted'}, 200
    

class UserList(Resource):
    def get(self):
         return {'users': list(map(lambda x: x.json() , UserModel.find_all()))}, 200 


class UserLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help='Username must not be blank!')
    parser.add_argument('password', type=str, required=True, help='Username must not be blank!') 

    @classmethod
    def post(cls):
        data = cls.parser.parse_args()
        user = UserModel.find_by_username(data['username'])
        if user and safe_str_cmp(data['password'], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200 
        else:
            return {'msg':'Error: username or password are not correct'}, 401


class UserLogout(Resource):

    @classmethod
    @jwt_required()
    def post(cls):
        jti = get_jwt()['jti']
        BLACKLIST.add(jti)
        return {'msg':'Successfully logged out'}, 200
        

class UserRefresh(Resource):

    @classmethod 
    @jwt_required(refresh=True)
    def post(cls):
        current_user_id = get_jwt_identity()
        new_token = create_access_token(identity=current_user_id, fresh=False)
        return {
            'access_token': new_token
        }, 200