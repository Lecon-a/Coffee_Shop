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

@app.route("/drinks-detail")
@requires_auth
def get_drinks_detail(can):
    try:
        if can == 'get:drinks-detail':
            seletion = Drink.query.order_by(Drink.id).all()
            drinks = [drink.long() for drink in seletion]
            return jsonify({
                'success': True,
                'drinks': drinks
            })
        else:
            abort(401)
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
@requires_auth
def create_new_drink(can):
    try:
        new_title = request.drink['title']
        new_recipe = request.drink['recipe']
        if can == 'post:drinks':
            drink = Drink(new_title, new_recipe)
            drink.insert()
            drinks = Drink.query.order_by(Drink.id).all()
            return jsonify({
                'success': True,
                'drinks': [drink.long() for drink in drinks]
            })
        else:
            abort(401)
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

@app.route("/drinks/<int:drink_id>", methods=['PATCH', 'DELETE'])
@requires_auth
def update(can, drink_id):
    try:

        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        if request.method == 'PATCH' and can == 'patch:drinks':
            drink.title = request.drink['title']
            drink.recipe = request.drink['recipe']
            drink.update()
            # fetch all drinks
            drinks = Drink.query.order_by(Drink.id).all()
            return jsonify({
                'success': True,
                'drinks': [drink.long() for drink in drinks]
            })
        elif request.method == 'DELETE' and can == 'delete:drinks':
            delete_drink = drink.long()
            drink = Drink(
                title=delete_drink['title'],
                recipe=delete_drink['recipe']
            )
            drink.delete()
            # return {'success': True, 'delete':drink_id}
            return jsonify({
                'success': True,
                'delete': drink_id
            })
        else:
            abort(401)

    except:
        abort(422)

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

# Error Handling
'''
Example error handling for unprocessable entity
'''

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

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

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


if __name__ == "__main__":
    app.debug = True
    app.run()
