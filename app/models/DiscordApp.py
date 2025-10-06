from app.models import db, ApiModel
from sqlalchemy import UniqueConstraint

class DiscordApp(ApiModel):
    __tablename__ = 'discord_apps'
    id_guild = db.Column(db.Integer, nullable=False, unique=True)
    id_channel = db.Column(db.Integer, nullable=False, unique=True)

    __table_args__ = (UniqueConstraint('id_guild', 'id_channel', name='uq_discord_apps'),)


    