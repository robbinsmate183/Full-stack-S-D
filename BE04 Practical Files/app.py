from flask import Flask, jsonify, make_response, request
import uuid
import random

app = Flask(__name__)

businesses = {}


def generate_dummy_data():
    towns = ['Coleraine', 'Banbridge', 'Belfast', 'Lisburn', 'Ballymena',
             'Derry', 'Newry', 'Enniskillen', 'Omagh', 'Ballymoney']
    business_dict = {}

    for i in range(100):
        business_id = str(uuid.uuid1())
        business_dict[business_id] = {
            'name': 'Biz ' + str(i),
            'town': random.choice(towns),
            'rating': random.randint(1, 5),
            'reviews': {}
        }

    return business_dict


def error(message, status=404):
    return make_response(jsonify({'error': message}), status)


def valid_rating(value):
    try:
        return 1 <= int(value) <= 5
    except (TypeError, ValueError):
        return False


def pagination(data):
    try:
        page_num = int(request.args.get('pn', 1))
        page_size = int(request.args.get('ps', 10))
    except ValueError:
        return None, error('Page number and page size must be integers', 400)

    if page_num < 1 or page_size < 1:
        return None, error('Page number and page size must be positive', 400)

    start = page_size * (page_num - 1)
    entries = [{key: value} for key, value in data.items()]
    return entries[start:start + page_size], None


@app.route('/api/v1.0/businesses', methods=['GET'])
def show_all_businesses():
    results, failure = pagination(businesses)

    if failure is not None:
        return failure

    return make_response(jsonify(results), 200)


@app.route('/api/v1.0/businesses/<string:id>', methods=['GET'])
def show_one_business(id):
    if id not in businesses:
        return error('Invalid business ID')

    return make_response(jsonify(businesses[id]), 200)


@app.route('/api/v1.0/businesses', methods=['POST'])
def add_business():
    if not all(field in request.form for field in ('name', 'town', 'rating')):
        return error('Missing form data', 400)

    if not valid_rating(request.form['rating']):
        return error('Rating must be an integer between 1 and 5', 400)

    business_id = str(uuid.uuid1())

    new_business = {
        'name': request.form['name'],
        'town': request.form['town'],
        'rating': int(request.form['rating']),
        'reviews': {}
    }

    businesses[business_id] = new_business

    return make_response(jsonify({business_id: new_business}), 201)


@app.route('/api/v1.0/businesses/<string:id>', methods=['PUT'])
def edit_business(id):
    if id not in businesses:
        return error('Invalid business ID')

    print("PUT BUSINESS DATA RECEIVED:", request.form.to_dict())

    if not any(field in request.form for field in ('name', 'town', 'rating')):
        return error('Missing form data', 400)

    if 'rating' in request.form and not valid_rating(request.form['rating']):
        return error('Rating must be an integer between 1 and 5', 400)

    businesses[id]['name'] = request.form.get(
        'name', businesses[id]['name']
    )

    businesses[id]['town'] = request.form.get(
        'town', businesses[id]['town']
    )

    if 'rating' in request.form:
        businesses[id]['rating'] = int(request.form['rating'])

    return make_response(jsonify({id: businesses[id]}), 200)


@app.route('/api/v1.0/businesses/<string:id>', methods=['DELETE'])
def delete_business(id):
    if id not in businesses:
        return error('Invalid business ID')

    del businesses[id]

    return make_response('', 204)


@app.route('/api/v1.0/businesses/<string:b_id>/reviews', methods=['GET'])
def fetch_all_reviews(b_id):
    if b_id not in businesses:
        return error('Invalid business ID')

    results, failure = pagination(businesses[b_id]['reviews'])

    if failure is not None:
        return failure

    return make_response(jsonify(results), 200)


@app.route('/api/v1.0/businesses/<string:b_id>/reviews', methods=['POST'])
def add_new_review(b_id):
    if b_id not in businesses:
        return error('Invalid business ID')

    if not all(field in request.form for field in ('username', 'comment', 'stars')):
        return error('Missing form data', 400)

    if not valid_rating(request.form['stars']):
        return error('Stars must be an integer between 1 and 5', 400)

    review_id = str(uuid.uuid1())

    new_review = {
        'username': request.form['username'],
        'comment': request.form['comment'],
        'stars': int(request.form['stars'])
    }

    businesses[b_id]['reviews'][review_id] = new_review

    return make_response(jsonify({review_id: new_review}), 201)



@app.route('/api/v1.0/businesses/<string:b_id>/reviews/<string:r_id>', methods=['GET'])
def fetch_one_review(b_id, r_id):
    if b_id not in businesses:
        return error('Invalid business ID')

    reviews = businesses[b_id]['reviews']

    if r_id not in reviews:
        return error('Invalid review ID')

    return make_response(jsonify(reviews[r_id]), 200)


@app.route('/api/v1.0/businesses/<string:b_id>/reviews/<string:r_id>', methods=['PUT'])
def edit_review(b_id, r_id):
    if b_id not in businesses:
        return error('Invalid business ID')

    reviews = businesses[b_id]['reviews']

    if r_id not in reviews:
        return error('Invalid review ID')

    if not any(field in request.form for field in ('username', 'comment', 'stars')):
        return error('Missing form data', 400)

    if 'stars' in request.form and not valid_rating(request.form['stars']):
        return error('Stars must be an integer between 1 and 5', 400)

    if 'username' in request.form:
        reviews[r_id]['username'] = request.form['username']

    if 'comment' in request.form:
        reviews[r_id]['comment'] = request.form['comment']

    if 'stars' in request.form:
        reviews[r_id]['stars'] = int(request.form['stars'])

    return make_response(jsonify({r_id: reviews[r_id]}), 200)


@app.route('/api/v1.0/businesses/<string:b_id>/reviews/<string:r_id>', methods=['DELETE'])
def delete_review(b_id, r_id):
    if b_id not in businesses:
        return error('Invalid business ID')

    reviews = businesses[b_id]['reviews']

    if r_id not in reviews:
        return error('Invalid review ID')

    del reviews[r_id]

    return make_response('', 204)


businesses = generate_dummy_data()


if __name__ == '__main__':
    app.run(debug=True)