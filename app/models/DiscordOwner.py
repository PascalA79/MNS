from app.models import db, ApiModel, User
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class DiscordOwner(ApiModel):
    __tablename__ = 'discord_owners'
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    discord_app_id = db.Column(db.String(80), ForeignKey('discord_apps.id'), nullable=False)

    user = relationship("User", backref="discord_owners", foreign_keys=[user_id])
    discord_app = relationship("DiscordApp", backref="discord_apps", foreign_keys=[discord_app_id])

    @classmethod
    def getOne(cls, user_name):
        user = User.getAll(pseudo=user_name)
        user = user[0] if user else None
        if user and user.discord_user:
            return user.discord_user[0]
        return None
            
