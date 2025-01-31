from flask import Blueprint, request, jsonify, g
import datetime
import jwt
from . import users_collection, exercise_collection
from werkzeug.security import generate_password_hash, check_password_hash
import os
from .models import User, Exercise
from .utils import token_required
from bson import ObjectId


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


@main_blueprint.route('/exercise/create', methods=['POST'])
@token_required
def create_exercise():
    data = request.get_json()
    name = data.get('name')
    duration = data.get('duration')
    description = data.get('description')
    user_id = g.user_id
    
    if not name or not duration:
        return jsonify({'message': 'Name and duration are required'}), 400
    
    exercise = Exercise(name, duration, description, user_id)
    inserted_exercise = exercise_collection.insert_one(exercise.to_dict())
    return jsonify({'message': 'Exercise created', 'exercise_id': str(inserted_exercise.inserted_id)}), 201

@main_blueprint.route('/exercise/update/<string:id>', methods=['PUT'])
@token_required
def update_exercise(id):
    data = request.get_json()
    user_id = g.user_id
    
    exercise = exercise_collection.find_one({'_id': ObjectId(id), 'user_id': ObjectId(user_id)})
    if not exercise:
        return jsonify({'message': 'Exercise not found'}), 404
    
    update_fields = {}
    if 'name' in data:
        update_fields['name'] = data['name']
    if 'duration' in data:
        update_fields['duration'] = data['duration']
    if 'description' in data:
        update_fields['description'] = data['description']
    
    if update_fields:
        exercise_collection.update_one({'_id': ObjectId(id)}, {'$set': update_fields})
    
    return jsonify({'message': 'Exercise updated successfully'}), 200

@main_blueprint.route('/exercise/list', methods=['GET'])
@token_required
def get_exercises():
    user_id = g.user_id
    exercises = list(exercise_collection.find({'user_id': ObjectId(user_id)}))
    
    for exercise in exercises:
        exercise['_id'] = str(exercise['_id'])
    
    return jsonify({'exercises': exercises}), 200

@main_blueprint.route('/exercise/delete/<string:id>', methods=['DELETE'])
@token_required
def delete_exercise(id):
    user_id = g.user_id
    
    exercise = exercise_collection.find_one({'_id': ObjectId(id), 'user_id': ObjectId(user_id)})
    if not exercise:
        return jsonify({'message': 'Exercise not found'}), 404
    
    exercise_collection.delete_one({'_id': ObjectId(id)})
    return jsonify({'message': 'Exercise deleted successfully'}), 200
