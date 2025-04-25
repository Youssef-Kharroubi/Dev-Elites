from flask import Flask
from flask_cors import CORS
from .routes import init_routes

def create_app(model_path):
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
    init_routes(app, model_path)
    return app