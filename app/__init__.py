from flask import Flask
from flask_cors import CORS
from app.models import db
from NotifDiscord import NotifDiscord

notif_discord:NotifDiscord = None

def create_app():
    global notif_discord 
    notif_discord = NotifDiscord()
    app = Flask(__name__, static_folder='static', template_folder='templates')
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database
    db.init_app(app)
    return app


        



