from flask import Flask
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()
uri = os.getenv("MONGO_URI")
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['FitnessTracker']
users_collection = db['users']

def create_app():
    app = Flask(__name__)

    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    
   
    
    with app.app_context():
        from .routes import main_blueprint
        app.register_blueprint(main_blueprint)

    print("app initialised")
    print(client)
    return app
