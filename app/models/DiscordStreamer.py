from app.models import db, ApiModel, Streamer, DiscordApp
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, UniqueConstraint

class DiscordStreamer(ApiModel):
    __tablename__ = 'discord_streamers'
    app_id = db.Column(db.Integer, ForeignKey('discord_apps.id'), nullable=False)
    streamer_id = db.Column(db.Integer, ForeignKey('streamers.id'), nullable=False)
    
    __table_args__ = (UniqueConstraint('app_id', 'streamer_id', name='_app_streamer_uc'),)
    
    discord_app = relationship("DiscordApp", backref="discord_streamers", foreign_keys=[app_id])
    streamer = relationship('Streamer', backref="discord_streamers", foreign_keys=[streamer_id])
    @classmethod
    def insert(cls, id_guild, streamer_id, errors = None):
        if not errors:
            errors = DiscordStreamer.create_api_errors()
        discord_app = DiscordApp.DiscordApp.getOne(id_guild)
        streamer = Streamer.getOne(streamer_id)
        return super().insert(data=
            {
                'app_id': discord_app.id if discord_app else None,
                'streamer_id': streamer.id if streamer else None
            },
            errors = errors
        )
    
    @classmethod
    def get_by_id_twitch(cls, id_twitch)->'DiscordStreamer':
        return cls.query.join(Streamer).filter(Streamer.id_twitch == id_twitch).all()
    