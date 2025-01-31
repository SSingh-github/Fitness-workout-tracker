from flask import Blueprint, request, jsonify, g
import datetime
import jwt
from . import users_collection, exercise_collection, workout_collection, comment_collection
from werkzeug.security import generate_password_hash, check_password_hash
import os
from .models import User, Exercise, Comment, Workout
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


@main_blueprint.route('/workout/create', methods=['POST'])
@token_required
def create_workout():
    data = request.get_json()
    user_id = g.user_id
    name = data.get('name')
    start_date_time = data.get('start_date_time')
    exercises = data.get('exercises', [])
    
    if not name or not start_date_time:
        return jsonify({'message': 'Name and start_date_time are required'}), 400
    
    workout = Workout(user_id, name, 'pending', start_date_time)
    workout.exercises = [ObjectId(ex_id) for ex_id in exercises]
    inserted_workout = workout_collection.insert_one(workout.to_dict())
    return jsonify({'message': 'Workout created', 'workout_id': str(inserted_workout.inserted_id)}), 201

@main_blueprint.route('/workout/update/<string:id>', methods=['PUT'])
@token_required
def update_workout(id):
    data = request.get_json()
    user_id = g.user_id
    
    workout = workout_collection.find_one({'_id': ObjectId(id), 'user_id': ObjectId(user_id)})
    if not workout:
        return jsonify({'message': 'Workout not found'}), 404
    
    update_fields = {}
    if 'name' in data:
        update_fields['name'] = data['name']
    if 'start_date_time' in data:
        update_fields['start_date_time'] = datetime.datetime.strptime(data['start_date_time'], "%Y-%m-%d %H:%M:%S")
    if 'exercises' in data:
        update_fields['exercises'] = [ObjectId(ex_id) for ex_id in data['exercises']]
    
    if update_fields:
        workout_collection.update_one({'_id': ObjectId(id)}, {'$set': update_fields})
    
    return jsonify({'message': 'Workout updated successfully'}), 200

@main_blueprint.route('/workout/update_status/<string:id>', methods=['PUT'])
@token_required
def update_workout_status(id):
    user_id = g.user_id
    workout = workout_collection.find_one({'_id': ObjectId(id), 'user_id': ObjectId(user_id)})
    if not workout:
        return jsonify({'message': 'Workout not found'}), 404
    
    new_status = 'done' if workout['status'] == 'pending' else 'pending'
    workout_collection.update_one({'_id': ObjectId(id)}, {'$set': {'status': new_status}})
    
    return jsonify({'message': 'Workout status updated', 'status': new_status}), 200

@main_blueprint.route('/workout/list', methods=['GET'])
@token_required
def get_workout_list():
    user_id = g.user_id
    workouts = list(workout_collection.find({'user_id': ObjectId(user_id)}).sort('start_date_time', 1))
    
    for workout in workouts:
        workout['_id'] = str(workout['_id'])
    
    return jsonify({'workouts': workouts}), 200

@main_blueprint.route('/workout/comment/<string:id>', methods=['POST'])
@token_required
def post_comment(id):
    data = request.get_json()
    user_id = g.user_id
    text = data.get('text')
    
    if not text:
        return jsonify({'message': 'Comment text is required'}), 400
    
    workout = workout_collection.find_one({'_id': ObjectId(id), 'user_id': ObjectId(user_id)})
    if not workout:
        return jsonify({'message': 'Workout not found'}), 404
    
    comment = Comment(text, id)
    inserted_comment = comment_collection.insert_one(comment.to_dict())
    workout_collection.update_one({'_id': ObjectId(id)}, {'$push': {'comments': inserted_comment.inserted_id}})
    
    return jsonify({'message': 'Comment added', 'comment_id': str(inserted_comment.inserted_id)}), 201

@main_blueprint.route('/workout/report', methods=['GET'])
@token_required
def get_report():
    user_id = g.user_id
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({'message': 'Start date and end date are required'}), 400
    
    start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    
    total_workouts = workout_collection.count_documents({'user_id': ObjectId(user_id), 'start_date_time': {'$gte': start_dt, '$lte': end_dt}})
    completed_workouts = workout_collection.count_documents({'user_id': ObjectId(user_id), 'start_date_time': {'$gte': start_dt, '$lte': end_dt}, 'status': 'done'})
    
    completion_percentage = (completed_workouts / total_workouts * 100) if total_workouts > 0 else 0
    
    return jsonify({'total_workouts': total_workouts, 'completed_workouts': completed_workouts, 'completion_percentage': completion_percentage}), 200
