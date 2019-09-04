"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from models import db, User, Product, Address, BillingAddress, Picture

from flask_jwt_simple import (
    JWTManager, jwt_required, create_jwt, get_jwt_identity
)

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)

# /////////////////////////////////////// JWT configuration///////////////////////////////////////
# Setup the Flask-JWT-Simple extension
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)


# Provide a method to create access tokens. The create_jwt()
# function is used to actually generate the token
@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    params = request.get_json()
    userName = params.get('userName', None)
    email = params.get('email', None)

    if not userName:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not email:
        return jsonify({"msg": "Missing password parameter"}), 400
    usercheck = User.query.filter_by(userName=userName, email=email).first()
    if usercheck == None:
        return jsonify({"msg": "Bad username or email"}), 401
    # if username != 'test' or password != 'test':
    #     return jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    ret = {'jwt': create_jwt(identity=userName)}
    return jsonify(ret), 200

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

    # //////////////////////////// Create Person Endpoints //////////////////////////////////////////////////

@app.route('/user', methods=['POST', 'GET'])
def handle_person():
    """
    Create person and retrieve all persons
    """

    # POST request
    if request.method == 'POST':
        body = request.get_json()

        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)
        if 'userName' not in body:
            raise APIException('You need to specify the username', status_code=400)
        if 'email' not in body:
            raise APIException('You need to specify the email', status_code=400)
        if 'password' not in body:
            raise APIException('You need to enter your password', status_code=400)

        user1 = User(userFirstName=body['userFirstName'], userLastName=body['userLastName'], userName=body['userName'], email=body['email'], password=body['password'], addresses=body['addresses'])
        db.session.add(user1)
        db.session.commit()
        return "ok", 200

    # GET request
    if request.method == 'GET':
        all_people = User.query.all()
        all_people = list(map(lambda x: x.serialize(), all_people))
        return jsonify(all_people), 200

    return "Invalid Method", 404


@app.route('/user/<int:person_id>', methods=['PUT', 'GET', 'DELETE'])
@jwt_required #this decorator makes this requires to be logged in
def get_single_person(person_id):
    """
    Single person
    """

    # PUT request
    if request.method == 'PUT':
        body = request.get_json()
        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)

        user1 = User.query.get(person_id)
        if user1 is None:
            raise APIException('User not found', status_code=404)

        if "username" in body:
            user1.username = body["username"]
        if "email" in body:
            user1.email = body["email"]
        db.session.commit()

        return jsonify(user1.serialize()), 200

    # GET request
    if request.method == 'GET':
        user1 = User.query.get(person_id)
        if user1 is None:
            raise APIException('User not found', status_code=404)
        return jsonify(user1.serialize()), 200

    # DELETE request
    if request.method == 'DELETE':
        user1 = User.query.get(person_id)
        if user1 is None:
            raise APIException('User not found', status_code=404)
        db.session.delete(user1)
        db.session.commit()
        return "ok", 200

    return "Invalid Method", 404

    # //////////////////////////////////////////////////// Create Products end points  /////////////////////////////////

@app.route('/product', methods=['POST', 'GET'])
def handle_product():
    """
    Create product and retrieve all products
    """

    # POST request
    if request.method == 'POST':
        body = request.get_json()

        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)
        if 'productName' not in body:
            raise APIException('You need to specify the product name', status_code=400)
        if 'productPrice' not in body:
            raise APIException('You need to specify the product price', status_code=400)

        product1 = Product(productName=body['productName'], productDescription=body['productDescription'], productPrice=body['productPrice'], productCategory=body['productCategory'], productAgeRange=body['productAgeRange'])
        db.session.add(product1)
        db.session.commit()
        return "ok", 200

    # GET request
    if request.method == 'GET':
        all_products = Product.query.all()
        all_products = list(map(lambda x: x.serialize(), all_products))
        return jsonify(all_products), 200

    return "Invalid Method", 404


@app.route('/product/<int:product_id>', methods=['PUT', 'GET', 'DELETE'])
def get_single_product(product_id):
    """
    Single product
    """

    # PUT request
    if request.method == 'PUT':
        body = request.get_json()
        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)

        product1 = Product.query.get(product_id)
        if product1 is None:
            raise APIException('Product not found', status_code=404)

        if "productName" in body:
            product1.productName = body["productName"]
        if "productPrice" in body:
            product1.productPrice = body["productPrice"]
        db.session.commit()

        return jsonify(product1.serialize()), 200

    # GET request
    if request.method == 'GET':
        product1 = Product.query.get(product_id)
        if product1 is None:
            raise APIException('Product not found', status_code=404)
        return jsonify(product1.serialize()), 200

    # DELETE request
    if request.method == 'DELETE':
        product1 = Product.query.get(product_id)
        if product1 is None:
            raise APIException('Product not found', status_code=404)
        db.session.delete(product1)
        db.session.commit()
        return "ok", 200

    return "Invalid Method", 404

# ////////////////////////////////// User Address end points ///////////////////////////////////
@app.route('/address', methods=['POST', 'GET'])
def handle_address():
    """
    Create address and retrieve all address
    """

    # POST request
    if request.method == 'POST':
        body = request.get_json()

        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)
        if 'userStreet' not in body:
            raise APIException('You need to specify the street', status_code=400)
        if 'userNumber' not in body:
            raise APIException('You need to specify the address number', status_code=400)
        if 'userCity' not in body:
            raise APIException('You need to specify the city', status_code=400)
        if 'userState' not in body:
            raise APIException('You need to specify the state', status_code=400)
        if 'userZipCode' not in body:
            raise APIException('You need to specify the Zip Code', status_code=400)

        address1 = Address(userStreet=body['userStreet'], userNumber=body['userNumber'], userCity=body['userCity'], userState=body['userState'], userZipCode=body['userZipCode'], isBillingAddress=body['isBillingAddress'], person_id=body['person_id'])
        db.session.add(address1)
        db.session.commit()
        return "ok", 200

    # GET request
    if request.method == 'GET':
        all_address = Address.query.all()
        all_address = list(map(lambda x: x.serialize(), all_address))
        return jsonify(all_address), 200

    return "Invalid Method", 404


@app.route('/address/<int:address_id>', methods=['PUT', 'GET', 'DELETE'])
def get_single_address(address_id):
    """
    Single address
    """

    # PUT request
    if request.method == 'PUT':
        body = request.get_json()
        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)

        address1 = Address.query.get(address_id)
        if address1 is None:
            raise APIException('address not found', status_code=404)

        if "userStreet" in body:
            address1.userStreet = body["userStreet"]
        if "userNumber" in body:
            address1.userNumber = body["userNumber"]
        if "userCity" in body:
            address1.userCity = body["userCity"]
        if "userState" in body:
            address1.userState = body["userState"]
        if "userZipCode" in body:
            address1.userZipCode = body["userZipCode"]
        db.session.commit()

        return jsonify(address1.serialize()), 200

    # GET request
    if request.method == 'GET':
        address1 = Address.query.get(address_id)
        if address1 is None:
            raise APIException('Address not found', status_code=404)
        return jsonify(address1.serialize()), 200

    # DELETE request
    if request.method == 'DELETE':
        address1 = Address.query.get(address_id)
        if address1 is None:
            raise APIException('address not found', status_code=404)
        db.session.delete(address1)
        db.session.commit()
        return "ok", 200

    return "Invalid Method", 404

# //////////////////////////////////////////////Billing Address end points creation //////////////////////////////
@app.route('/billingaddress', methods=['POST', 'GET'])
def handle_billingaddress():
    """
    Create billing address and retrieve all address
    """

    # POST request
    if request.method == 'POST':
        body = request.get_json()

        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)
        if 'billingStreet' not in body:
            raise APIException('You need to specify the billing street', status_code=400)
        if 'billingNumber' not in body:
            raise APIException('You need to specify the billing address number', status_code=400)
        if 'billingCity' not in body:
            raise APIException('You need to specify the billing city', status_code=400)
        if 'billingState' not in body:
            raise APIException('You need to specify the billing state', status_code=400)
        if 'billingZipCode' not in body:
            raise APIException('You need to specify the billing Zip Code', status_code=400)

        address1 = BillingAddress(billingStreet=body['billingStreet'], billingNumber=body['billingNumber'], billingCity=body['billingCity'],  billingState=body['billingState'], billingZipCode=body['billingZipCode'], person_id=body['person_id'])
        db.session.add(address1)
        db.session.commit()
        return "ok", 200

    # GET request
    if request.method == 'GET':
        all_billingaddress = BillingAddress.query.all()
        all_billingaddress = list(map(lambda x: x.serialize(), all_billingaddress))
        return jsonify(all_billingaddress), 200

    return "Invalid Method", 404


@app.route('/billingaddress/<int:billingaddress_id>', methods=['PUT', 'GET', 'DELETE'])
def get_single_billingaddress(billingaddress_id):
    """
    Single billing address
    """

    # PUT request
    if request.method == 'PUT':
        body = request.get_json()
        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)

        address1 = BillingAddress.query.get(billingaddress_id)
        if address1 is None:
            raise APIException('address not found', status_code=404)

        if "billingStreet" in body:
            address1.userStreet = body["billingStreet"]
        if "billingNumber" in body:
            address1.userNumber = body["billingNumber"]
        if "billingCity" in body:
            address1.billingCity = body["billingCity"]
        if "billingState" in body:
            address1.billingState = body["billingState"]
        if "billingZipCode" in body:
            address1.billingZipCode = body["billingZipCode"]
        db.session.commit()

        return jsonify(address1.serialize()), 200

    # GET request
    if request.method == 'GET':
        address1 = BillingAddress.query.get(billingaddress_id)
        if address1 is None:
            raise APIException('Billing Address not found', status_code=404)
        return jsonify(address1.serialize()), 200

    # DELETE request
    if request.method == 'DELETE':
        address1 = BillingAddress.query.get(billingaddress_id)
        if address1 is None:
            raise APIException('Billing Address not found', status_code=404)
        db.session.delete(address1)
        db.session.commit()
        return "ok", 200

    return "Invalid Method", 404

# //////////////////////////////////////////// Picture End Point ////////////////////////////////
@app.route('/picture', methods=['POST', 'GET'])
def handle_picture():
    """
    Create picture URL and retrieve all pictures
    """

    # POST request
    if request.method == 'POST':
        body = request.get_json()

        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)
        if 'picture_url' not in body:
            raise APIException('You need to specify the picture URL', status_code=400)

        address1 = Picture(picture_url=body['picture_url'], photos_id=body['photos_id'])
        db.session.add(address1)
        db.session.commit()
        return "ok", 200

    # GET request
    if request.method == 'GET':
        all_pictures = Picture.query.all()
        all_pictures = list(map(lambda x: x.serialize(), all_pictures))
        return jsonify(all_pictures), 200

    return "Invalid Method", 404


@app.route('/picture/<int:picture_id>', methods=['PUT', 'GET', 'DELETE'])
def get_single_picture(picture_id):
    """
    Single picture
    """

    # PUT request
    if request.method == 'PUT':
        body = request.get_json()
        if body is None:
            raise APIException("You need to specify the request body as a json object", status_code=400)

        address1 = Picture.query.get(picture_id)
        if address1 is None:
            raise APIException('picture not found', status_code=404)

        db.session.commit()

        return jsonify(address1.serialize()), 200

    # GET request
    if request.method == 'GET':
        address1 = Picture.query.get(picture_id)
        if address1 is None:
            raise APIException('picture not found', status_code=404)
        return jsonify(address1.serialize()), 200

    # DELETE request
    if request.method == 'DELETE':
        address1 = Picture.query.get(picture_id)
        if address1 is None:
            raise APIException('picture not found', status_code=404)
        db.session.delete(address1)
        db.session.commit()
        return "ok", 200

    return "Invalid Method", 404

# /////////////////////////////////////// Start Server //////////////////////////////
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT)