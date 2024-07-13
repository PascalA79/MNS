from app.models import db, ApiModel, User
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class DiscordUser(ApiModel):
    __tablename__ = 'discordusers'
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False, unique=True)
    discord_id = db.Column(db.String(80), unique=True, nullable=False)

    user = relationship("User", backref="discord_users", foreign_keys=[user_id])

    @classmethod
    def getOne(cls, user_name):
        user = User.getAll(pseudo=user_name)
        user = user[0] if user else None
        if user and user.discord_user:
            return user.discord_user[0]
        return None
            
