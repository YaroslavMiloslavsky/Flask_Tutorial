import os
from dotenv import load_dotenv
from flask import Flask
from flask_restful import Api

from resources.item import Item, ItemList
from resources.user import UserRegister
from resources.store import Store, StoreList

from security import authenticate, identify
from flask_jwt import JWT

from db import db

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

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL', f'postgresql://{USER}:{PASSWORD}@localhost'
                                                                       f':5432/user_stores')
app.config['JWT_AUTH_URL_RULE'] = '/login'
app.secret_key = os.environ.get('SECRET', SECRET_KEY)


jwt = JWT(app, authenticate, identify)

@app.before_first_request
def create_tables():
    db.create_all()

api.add_resource(Store, '/store/<string:name>')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/user-register')
api.add_resource(StoreList, '/stores')

if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)
