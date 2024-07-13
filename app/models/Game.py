from app.models import db, ApiModel

class Game(ApiModel):
    __tablename__ = 'games'
    name = db.Column(db.String(80), unique=True, nullable=False)
    id_twitch = db.Column(db.Integer, unique=True, nullable=True)  