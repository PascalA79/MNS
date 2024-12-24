from app.models import db, ApiModel

class Event(ApiModel):
    __tablename__ = 'events'
    name = db.Column(db.String(80), unique=True, nullable=False)   
    description = db.Column(db.String(128), nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='events')
