from flask import Blueprint, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId
from decorators import jwt_required, admin_required

reviews_bp = Blueprint("reviews_bp", __name__)
client = MongoClient("mongodb://127.0.0.1:27017")
businesses = client.bizDB.biz

def error(message, status=404):
    return make_response(jsonify({"error": message}), status)

def get_business(bid):
    if not ObjectId.is_valid(bid):
        return None
    return businesses.find_one({"_id": ObjectId(bid)})

def valid_rating(value):
    try:
        return str(int(value)) == str(value).strip() and 1 <= int(value) <= 5
    except (TypeError, ValueError):
        return False

def format_review(review):
    review["_id"] = str(review["_id"])
    return review

@reviews_bp.route("/api/v1.0/businesses/<string:bid>/reviews", methods=["GET"])
def fetch_all_reviews(bid):
    business = get_business(bid)
    if business is None:
        return error("Invalid business ID")
    return make_response(jsonify([format_review(r) for r in business.get("reviews", [])]), 200)

@reviews_bp.route("/api/v1.0/businesses/<string:bid>/reviews/<string:rid>", methods=["GET"])
def fetch_one_review(bid, rid):
    business = get_business(bid)
    if business is None:
        return error("Invalid business ID")
    if not ObjectId.is_valid(rid):
        return error("Invalid review ID")
    for review in business.get("reviews", []):
        if review["_id"] == ObjectId(rid):
            return make_response(jsonify(format_review(review)), 200)
    return error("Invalid review ID")

@reviews_bp.route("/api/v1.0/businesses/<string:bid>/reviews", methods=["POST"])
@jwt_required
def add_new_review(bid):
    if get_business(bid) is None:
        return error("Invalid business ID")
    if not all(field in request.form for field in ("username", "comment", "stars")):
        return error("Missing form data", 400)
    if not valid_rating(request.form["stars"]):
        return error("Stars must be between 1 and 5", 400)
    review = {"_id": ObjectId(), "username": request.form["username"], "comment": request.form["comment"], "stars": int(request.form["stars"])}
    businesses.update_one({"_id": ObjectId(bid)}, {"$push": {"reviews": review}})
    url = request.url_root.rstrip("/") + "/api/v1.0/businesses/" + bid + "/reviews/" + str(review["_id"])
    return make_response(jsonify({"url": url}), 201)

@reviews_bp.route("/api/v1.0/businesses/<string:bid>/reviews/<string:rid>", methods=["PUT"])
@jwt_required
def edit_review(bid, rid):
    if get_business(bid) is None:
        return error("Invalid business ID")
    if not ObjectId.is_valid(rid):
        return error("Invalid review ID")
    if not all(field in request.form for field in ("username", "comment", "stars")):
        return error("Missing form data", 400)
    if not valid_rating(request.form["stars"]):
        return error("Stars must be between 1 and 5", 400)
    updated = {"reviews.$.username": request.form["username"], "reviews.$.comment": request.form["comment"], "reviews.$.stars": int(request.form["stars"])}
    result = businesses.update_one({"_id": ObjectId(bid), "reviews._id": ObjectId(rid)}, {"$set": updated})
    if result.matched_count == 0:
        return error("Invalid review ID")
    url = request.url_root.rstrip("/") + "/api/v1.0/businesses/" + bid + "/reviews/" + rid
    return make_response(jsonify({"url": url}), 200)

@reviews_bp.route("/api/v1.0/businesses/<string:bid>/reviews/<string:rid>", methods=["DELETE"])
@jwt_required
@admin_required
def delete_review(bid, rid):
    if get_business(bid) is None:
        return error("Invalid business ID")
    if not ObjectId.is_valid(rid):
        return error("Invalid review ID")
    result = businesses.update_one({"_id": ObjectId(bid), "reviews._id": ObjectId(rid)}, {"$pull": {"reviews": {"_id": ObjectId(rid)}}})
    if result.matched_count == 0:
        return error("Invalid review ID")
    return make_response("", 204)
