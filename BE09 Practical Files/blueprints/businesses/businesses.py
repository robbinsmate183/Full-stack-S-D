from flask import Blueprint, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId
from decorators import jwt_required, admin_required

businesses_bp = Blueprint("businesses_bp", __name__)
client = MongoClient("mongodb://127.0.0.1:27017")
businesses = client.bizDB.biz

def error(message, status=404):
    return make_response(jsonify({"error": message}), status)

def valid_rating(value):
    try:
        return str(int(value)) == str(value).strip() and 1 <= int(value) <= 5
    except (TypeError, ValueError):
        return False

def format_business(business):
    business["_id"] = str(business["_id"])
    for review in business.get("reviews", []):
        review["_id"] = str(review["_id"])
    return business

def get_business(bid):
    if not ObjectId.is_valid(bid):
        return None
    return businesses.find_one({"_id": ObjectId(bid)})

@businesses_bp.route("/api/v1.0/businesses", methods=["GET"])
def show_all_businesses():
    try:
        page_num = int(request.args.get("pn", 1))
        page_size = int(request.args.get("ps", 10))
    except ValueError:
        return error("Page number and page size must be integers", 400)
    if page_num < 1 or page_size < 1:
        return error("Page number and page size must be positive", 400)
    results = [format_business(b) for b in businesses.find().skip(page_size * (page_num - 1)).limit(page_size)]
    return make_response(jsonify(results), 200)

@businesses_bp.route("/api/v1.0/businesses/<string:id>", methods=["GET"])
def show_one_business(id):
    business = get_business(id)
    if business is None:
        return error("Invalid business ID")
    return make_response(jsonify(format_business(business)), 200)

@businesses_bp.route("/api/v1.0/businesses", methods=["POST"])
@jwt_required
def add_business():
    if not all(field in request.form for field in ("name", "town", "rating")):
        return error("Missing form data", 400)
    if not valid_rating(request.form["rating"]):
        return error("Rating must be between 1 and 5", 400)
    new_business = {"name": request.form["name"], "town": request.form["town"], "rating": int(request.form["rating"]), "reviews": []}
    result = businesses.insert_one(new_business)
    url = request.url_root.rstrip("/") + "/api/v1.0/businesses/" + str(result.inserted_id)
    return make_response(jsonify({"url": url}), 201)

@businesses_bp.route("/api/v1.0/businesses/<string:id>", methods=["PUT"])
@jwt_required
def edit_business(id):
    if get_business(id) is None:
        return error("Invalid business ID")
    if not all(field in request.form for field in ("name", "town", "rating")):
        return error("Missing form data", 400)
    if not valid_rating(request.form["rating"]):
        return error("Rating must be between 1 and 5", 400)
    updated = {"name": request.form["name"], "town": request.form["town"], "rating": int(request.form["rating"])}
    businesses.update_one({"_id": ObjectId(id)}, {"$set": updated})
    url = request.url_root.rstrip("/") + "/api/v1.0/businesses/" + id
    return make_response(jsonify({"url": url}), 200)

@businesses_bp.route("/api/v1.0/businesses/<string:id>", methods=["DELETE"])
@jwt_required
@admin_required
def delete_business(id):
    if not ObjectId.is_valid(id):
        return error("Invalid business ID")
    result = businesses.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        return error("Invalid business ID")
    return make_response("", 204)
