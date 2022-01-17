import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_restful import Api

from resources.item import Item, ItemList
from resources.user import (UserRegister, User, UserList, UserLogin, UserRefresh, UserLogout)
from resources.store import Store, StoreList

from flask_jwt_extended import JWTManager

from db import db
from blacklist import BLACKLIST

app = Flask(__name__)
api = Api(app)

env_path = os.path.join('../env_data', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print('Error loading credentials')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
SECRET_KEY = os.getenv('SECRET_KEY')
ADMIN_NAME = os.environ.get('ADMIN_NAME',os.getenv('ADMIN_NAME'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL', f'postgresql://{USER}:{PASSWORD}@localhost'
                                                                       f':5432/user_stores')
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = os.environ.get('SECRET', SECRET_KEY)


jwt = JWTManager(app)

@app.before_first_request
def create_tables():
    db.create_all()

@jwt.token_in_blocklist_loader
def check_token_in_blacklist(jwt_headers, jwt_payload):
    return jwt_payload['jti'] in BLACKLIST # To blacklist a user -> ['sub']

@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    from models.user import UserModel
    admin = UserModel.find_who_is_admin()
    if identity == admin.id: 
        return {'is_admin': True}
    return {'is_admin': False}

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'description': 'The token has expired',
        'error': 'token_expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(jwt_header):
    return jsonify({
        'description': 'The token is invalid',
        'error': 'invalid_token'
    }), 401

@jwt.unauthorized_loader
def unauthorized_token_callback(jwt_header):
    return jsonify({
        'description': 'The token is missing',
        'error': 'unauthorized_token'
    }), 401

@jwt.needs_fresh_token_loader
def need_fresh_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'description': 'The token is not fresh',
        'error': 'unfresh_token'
    }), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'description': 'The token was revoked',
        'error': 'revoked_token'
    }), 401

api.add_resource(User, '/user/<int:user_id>')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/user-register')
api.add_resource(StoreList, '/stores')
api.add_resource(UserList, '/users')
api.add_resource(UserLogin, '/login')
api.add_resource(UserRefresh, '/refresh')
api.add_resource(UserLogout, '/logout')

if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)
