from flask import Blueprint, request, jsonify, make_response
from pymongo import MongoClient
import jwt
import bcrypt
import datetime
import globals
from decorators import jwt_required

auth_bp = Blueprint("auth_bp", __name__)
client = MongoClient("mongodb://127.0.0.1:27017")
db = client.bizDB
users = db.users
blacklist = db.blacklist

@auth_bp.route("/api/v1.0/login", methods=["GET"])
def login():
    auth = request.authorization
    if not auth or not auth.username or auth.password is None:
        return make_response(jsonify({"message": "Authentication required"}), 401)
    user = users.find_one({"username": auth.username})
    if user is None:
        return make_response(jsonify({"message": "Bad username"}), 401)
    if not bcrypt.checkpw(auth.password.encode("utf-8"), user["password"]):
        return make_response(jsonify({"message": "Bad password"}), 401)
    token = jwt.encode({
        "user": auth.username,
        "admin": user["admin"],
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
    }, globals.secret_key, algorithm="HS256")
    return make_response(jsonify({"token": token}), 200)

@auth_bp.route("/api/v1.0/logout", methods=["GET"])
@jwt_required
def logout():
    token = request.headers["x-access-token"]
    blacklist.insert_one({"token": token})
    return make_response(jsonify({"message": "Logout successful"}), 200)
