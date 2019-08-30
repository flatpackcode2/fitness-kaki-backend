from flask import Flask, Blueprint, jsonify, make_response, request
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from models.user import User
from datetime import datetime, timedelta


sessions_api_blueprint = Blueprint('sessions_api', __name__)

@sessions_api_blueprint.route('/login', methods=['POST'])
def new():
    username = request.json.get('username')
    password = request.json.get('password')

    user = User.get_or_none(User.username == username)

    if user==None:
        response = {'message': 'No such user'}
        return make_response(jsonify(response), 400)

    if check_password_hash(user.password, password):
        user_details = {
            'id':user.id,
            'username':user.username,
            'profile_image_url':user.profile_image_url,
            'first_name':user.first_name,
            'last_name':user.last_name,
            'email':user.email
        }
        expires = timedelta(days=30)
        access_token = create_access_token(identity = user.id, expires_delta=expires)
        response = {'message': 'Login successful', 'auth_token':access_token, 'user':user_details}
        return make_response(jsonify(response),201)

    else:
        response = {'message':'invalid password'}
        return make_response(jsonify(response), 401)