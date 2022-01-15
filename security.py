from models.user import UserModel
from werkzeug.security import safe_str_cmp

def authenticate(username, password):
    user = UserModel.find_by_username(username)
    if user and safe_str_cmp(user.password, password):
        return user


def identify(payload):
    user_id = payload['identity']  # JWT
    return UserModel.find_by_id(user_id)
