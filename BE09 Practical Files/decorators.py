from functools import wraps
from flask import request, jsonify, make_response
from pymongo import MongoClient
import jwt
import globals

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.bizDB
blacklist = db.blacklist

def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("x-access-token")
        if not token:
            return make_response(jsonify({"message": "Token is missing"}), 401)
        try:
            jwt.decode(token, globals.secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return make_response(jsonify({"message": "Token has expired"}), 401)
        except jwt.InvalidTokenError:
            return make_response(jsonify({"message": "Token is invalid"}), 401)
        if blacklist.find_one({"token": token}):
            return make_response(jsonify({"message": "Token has been cancelled"}), 401)
        return func(*args, **kwargs)
    return wrapper

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("x-access-token")
        if not token:
            return make_response(jsonify({"message": "Token is missing"}), 401)
        try:
            data = jwt.decode(token, globals.secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return make_response(jsonify({"message": "Token has expired"}), 401)
        except jwt.InvalidTokenError:
            return make_response(jsonify({"message": "Token is invalid"}), 401)
        if blacklist.find_one({"token": token}):
            return make_response(jsonify({"message": "Token has been cancelled"}), 401)
        if not data.get("admin", False):
            return make_response(jsonify({"message": "Admin access required"}), 403)
        return func(*args, **kwargs)
    return wrapper
