from app.models import db, ApiModel

class DiscordOwnerEvent(ApiModel):
    __tablename__ = 'discord_owner_event'
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='discord_owner_event', lazy=True)
    event = db.relationship('Event', backref='discord_owner_event', lazy=True)