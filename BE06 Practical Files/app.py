from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.bizDB
businesses = db.biz


def error(message, status=404):
    return make_response(jsonify({"error": message}), status)


def valid_id(value):
    return ObjectId.is_valid(value)


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


def format_review(review):
    review["_id"] = str(review["_id"])
    return review


def get_business(bid):
    if not valid_id(bid):
        return None

    return businesses.find_one({"_id": ObjectId(bid)})


@app.route("/api/v1.0/businesses", methods=["GET"])
def show_all_businesses():
    try:
        page_num = int(request.args.get("pn", 1))
        page_size = int(request.args.get("ps", 10))
    except ValueError:
        return error("Page number and page size must be integers", 400)

    if page_num < 1 or page_size < 1:
        return error("Page number and page size must be positive", 400)

    page_start = page_size * (page_num - 1)

    results = []

    for business in businesses.find().skip(page_start).limit(page_size):
        results.append(format_business(business))

    return make_response(jsonify(results), 200)


@app.route("/api/v1.0/businesses/<string:id>", methods=["GET"])
def show_one_business(id):
    business = get_business(id)

    if business is None:
        return error("Invalid business ID")

    return make_response(jsonify(format_business(business)), 200)


@app.route("/api/v1.0/businesses", methods=["POST"])
def add_business():
    if not all(field in request.form for field in ("name", "town", "rating")):
        return error("Missing form data", 400)

    if not valid_rating(request.form["rating"]):
        return error("Rating must be between 1 and 5", 400)

    new_business = {
        "name": request.form["name"],
        "town": request.form["town"],
        "rating": int(request.form["rating"]),
        "reviews": []
    }

    result = businesses.insert_one(new_business)

    url = request.url_root.rstrip("/") + \
        "/api/v1.0/businesses/" + str(result.inserted_id)

    return make_response(jsonify({"url": url}), 201)


@app.route("/api/v1.0/businesses/<string:id>", methods=["PUT"])
def edit_business(id):
    if get_business(id) is None:
        return error("Invalid business ID")

    if not all(field in request.form for field in ("name", "town", "rating")):
        return error("Missing form data", 400)

    if not valid_rating(request.form["rating"]):
        return error("Rating must be between 1 and 5", 400)

    updated_business = {
        "name": request.form["name"],
        "town": request.form["town"],
        "rating": int(request.form["rating"])
    }

    businesses.update_one(
        {"_id": ObjectId(id)},
        {"$set": updated_business}
    )

    url = request.url_root.rstrip("/") + \
        "/api/v1.0/businesses/" + id

    return make_response(jsonify({"url": url}), 200)


@app.route("/api/v1.0/businesses/<string:id>", methods=["DELETE"])
def delete_business(id):
    if not valid_id(id):
        return error("Invalid business ID")

    result = businesses.delete_one({"_id": ObjectId(id)})

    if result.deleted_count == 0:
        return error("Invalid business ID")

    return make_response("", 204)


@app.route("/api/v1.0/businesses/<string:bid>/reviews", methods=["POST"])
def add_new_review(bid):
    if get_business(bid) is None:
        return error("Invalid business ID")

    if not all(field in request.form for field in ("username", "comment", "stars")):
        return error("Missing form data", 400)

    if not valid_rating(request.form["stars"]):
        return error("Stars must be between 1 and 5", 400)

    new_review = {
        "_id": ObjectId(),
        "username": request.form["username"],
        "comment": request.form["comment"],
        "stars": int(request.form["stars"])
    }

    businesses.update_one(
        {"_id": ObjectId(bid)},
        {"$push": {"reviews": new_review}}
    )

    url = request.url_root.rstrip("/") + \
        "/api/v1.0/businesses/" + bid + \
        "/reviews/" + str(new_review["_id"])

    return make_response(jsonify({"url": url}), 201)


@app.route("/api/v1.0/businesses/<string:bid>/reviews", methods=["GET"])
def fetch_all_reviews(bid):
    business = get_business(bid)

    if business is None:
        return error("Invalid business ID")

    reviews = [
        format_review(review)
        for review in business.get("reviews", [])
    ]

    return make_response(jsonify(reviews), 200)


@app.route("/api/v1.0/businesses/<string:bid>/reviews/<string:rid>", methods=["GET"])
def fetch_one_review(bid, rid):
    business = get_business(bid)

    if business is None:
        return error("Invalid business ID")

    if not valid_id(rid):
        return error("Invalid review ID")

    for review in business.get("reviews", []):
        if review["_id"] == ObjectId(rid):
            return make_response(jsonify(format_review(review)), 200)

    return error("Invalid review ID")


@app.route("/api/v1.0/businesses/<string:bid>/reviews/<string:rid>", methods=["PUT"])
def edit_review(bid, rid):
    if get_business(bid) is None:
        return error("Invalid business ID")

    if not valid_id(rid):
        return error("Invalid review ID")

    if not all(field in request.form for field in ("username", "comment", "stars")):
        return error("Missing form data", 400)

    if not valid_rating(request.form["stars"]):
        return error("Stars must be between 1 and 5", 400)

    updated_review = {
        "reviews.$.username": request.form["username"],
        "reviews.$.comment": request.form["comment"],
        "reviews.$.stars": int(request.form["stars"])
    }

    result = businesses.update_one(
        {
            "_id": ObjectId(bid),
            "reviews._id": ObjectId(rid)
        },
        {"$set": updated_review}
    )

    if result.matched_count == 0:
        return error("Invalid review ID")

    url = request.url_root.rstrip("/") + \
        "/api/v1.0/businesses/" + bid + "/reviews/" + rid

    return make_response(jsonify({"url": url}), 200)


@app.route("/api/v1.0/businesses/<string:bid>/reviews/<string:rid>", methods=["DELETE"])
def delete_review(bid, rid):
    if get_business(bid) is None:
        return error("Invalid business ID")

    if not valid_id(rid):
        return error("Invalid review ID")

    result = businesses.update_one(
        {
            "_id": ObjectId(bid),
            "reviews._id": ObjectId(rid)
        },
        {
            "$pull": {
                "reviews": {"_id": ObjectId(rid)}
            }
        }
    )

    if result.matched_count == 0:
        return error("Invalid review ID")

    return make_response("", 204)


if __name__ == "__main__":
    app.run(debug=True, port=5001)