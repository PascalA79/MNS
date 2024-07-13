from app.models import db, ApiModel

class DiscordApp(ApiModel):
    __tablename__ = 'discord_apps'
    name = db.Column(db.String(80), unique=True, nullable=False)
    id_guild = db.Column(db.Integer, nullable=False, unique=True)
    id_channel = db.Column(db.Integer, nullable=False, unique=True)


    