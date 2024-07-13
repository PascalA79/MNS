from app.models import db, ApiModel, Game, DiscordApp
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, UniqueConstraint

class DiscordGame(ApiModel):
    __tablename__ = 'discord_game'
    app_id = db.Column(db.Integer, ForeignKey('discord_apps.id'), nullable=False)
    game_id = db.Column(db.Integer, ForeignKey('games.id'), nullable=False)
    
    __table_args__ = (UniqueConstraint('app_id', 'game_id', name='_app_game_uc'),)
    
    discord_app = relationship("DiscordApp", backref="discord_games", foreign_keys=[app_id])
    game = relationship('Game', backref="discord_games", foreign_keys=[game_id])
    @classmethod
    def insert(cls, id_guild, game_id, errors = None):
        if not errors:
            errors = DiscordGame.create_api_errors()
        discord_app = DiscordApp.getOne(id_guild)
        game = Game.getOne(game_id)
        return super().insert(data=
            {
                'app_id': discord_app.id if discord_app else None,
                'game_id': game.id if game else None
            },
            errors = errors
        )
    def get_by_id_twitch(cls, id_twitch)->'DiscordGame':
        return cls.query.join(Game).filter(Game.id_twitch == id_twitch).first()
