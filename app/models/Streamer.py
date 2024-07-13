from app.models import db, ApiModel

class Streamer(ApiModel):
    __tablename__ = 'streamers'
    pseudo = db.Column(db.String(80), unique=True, nullable=False)
    id_twitch = db.Column(db.Integer, unique=True, nullable=True)    
