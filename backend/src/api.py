import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()

# ROUTES


# get drink menu
@app.route('/drinks', methods=['GET'])
def drinks():
    # get all drinks
    Alldrinks = Drink.query.all()
    drinks = [drink.short() for drink in Alldrinks]
    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200


# get all drinks detail
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(payload):

    # get all drinks detail
    Alldrinks = Drink.query.all()
    drinks = [drink.long() for drink in Alldrinks]
    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200


# add new drink
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):

    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    if ((title == '') or (recipe == '')):
        abort(422)
    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
        Alldrinks = Drink.query.all()
        drinks = [drink.long() for drink in Alldrinks]
        return jsonify({
            "success": True,
            "drinks": drinks
        }), 200
    except AuthError as auth_error:
        print(auth_error)
        abort(422)
    except Exception as error:
        print(error)
        abort(422)


# ubdate a drink
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    body = request.get_json()

    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)
    try:
        recipe = body.get('recipe', None)

        if recipe:
            drink.recipe = json.dumps(recipe)

        drink.update()

        Alldrinks = Drink.query.all()
        drinks = [drink.long() for drink in Alldrinks]
        return jsonify({
            "success": True,
            "drinks": drinks
        }), 200
    except AuthError as auth_error:
        print(auth_error)
        abort(401)
    except Exception as error:
        print(error)
        abort(401)


# delete a drink by manager
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)

    try:
        drink.delete()

        return jsonify({
            "success": True,
            "delete": id
        }), 200
    except AuthError as auth_error:
        print(auth_error)
        abort(422)
    except Exception as error:
        print(error)
        abort(422)


# Error Handling

'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
