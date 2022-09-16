import bcrypt
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

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks")
def get_drinks():
    try:
        selection = Drink.query.order_by(Drink.id).all()
        drinks = [drink.short() for drink in selection]
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(422)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

can = "get:drinks-detail"


@app.route("/drinks-detail")
@requires_auth(can)
def get_drinks_detail(can):
    try:
        seletion = Drink.query.order_by(Drink.id).all()
        drinks = [drink.long() for drink in seletion]
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(422)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=['POST'])
@requires_auth("post:drinks")
def create_new_drink(can):
    try:
        body = request.get_json()
        # The issue lies here
        new_title = body.get('title', None)
        new_recipe = str(body.get('recipe', None))

        drink_exist = Drink.query.filter(
            Drink.title == new_title).one_or_none()

        if drink_exist is None:
            drink = Drink(title=new_title, recipe=new_recipe)
            drink.insert()
        else:
            abort(409)

        drinks = Drink.query.order_by(Drink.id).all()

        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        })
    except:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<int:drink_id>", methods=['PATCH', 'DELETE'])
@requires_auth("patch:drinks" or "delete:drinks")
def update(can, drink_id):
    try:
        body = request.get_json()
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        if request.method == 'PATCH':
            # here lies issue
            if 'title' in body:
                drink.title = body.get('title')
            drink.update()
            # fetch all drinks
            drinks = Drink.query.order_by(Drink.id).all()
            return jsonify({
                'success': True,
                'drinks': [drink.long() for drink in drinks]
            })
        elif request.method == 'DELETE':
            drink.delete()
            return jsonify({
                'success': True,
                'delete': drink_id
            })
        else:
            abort(401)

    except:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(409)
def information(error):
    return jsonify({
        "success": False,
        "error": 409,
        "message": "Drink already exist"
    }), 409


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(400)
def permissionNotIncluded(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Permissions not included in JWT.'
    })


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': 'Permission not found.'
    }), 403


if __name__ == "__main__":
    app.debug = True
    app.run()
