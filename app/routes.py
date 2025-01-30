from flask import Blueprint, request, jsonify
import datetime
import jwt
from . import users_collection
from werkzeug.security import generate_password_hash, check_password_hash
import os
from .models import User

main_blueprint = Blueprint('main', __name__)



@main_blueprint.route('/users/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    
    if users_collection.find_one({'email': email}):
        return jsonify({'message': 'User already exists'}), 400
    
    user = User(email, name, password)
    inserted_user = users_collection.insert_one(user.to_dict())
    user_id = str(inserted_user.inserted_id)
    
    token = jwt.encode({'id': user_id, 'email': email, 
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, 
                        str(os.getenv('SECRET_KEY')), algorithm='HS256')
    
    return jsonify({'message': 'User created successfully', 'token': token}), 200


@main_blueprint.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = users_collection.find_one({'email': email})
    
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    token = jwt.encode({'id': str(user['_id']), 'email': email, 
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, 
                        str(os.getenv('SECRET_KEY')), algorithm='HS256')
    
    return jsonify({'message': 'Login successful', 'token': token}), 200