from flask import Flask
from flask_cors import CORS
from app.models import db

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database
    db.init_app(app)

    return app


        



