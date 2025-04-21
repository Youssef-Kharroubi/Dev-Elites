from flask import Flask
from flask_cors import CORS
from .routes import init_routes

app = Flask(__name__)
init_routes(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)