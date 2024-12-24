from app.models import db, ApiModel

class PlayerTimer(ApiModel):
    __tablename__ = 'player_timers'
    level_id = db.Column(db.Integer, db.ForeignKey('levels.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    timer = db.Column(db.Integer, nullable=True)
    __table_args__ = (db.UniqueConstraint('level_id', 'player_id', name='unique_user_level'), )

    level = db.relationship('Level', backref='user_levels', lazy=True, foreign_keys=[level_id])
    player = db.relationship('Player', backref='timers', lazy=True, foreign_keys=[player_id])  

    @classmethod
    def insert(cls, level_id, player_id, errors=None):
        if not errors:
            errors = PlayerTimer.create_api_errors()
        from app.models.events import Level, Player
        level = Level.Level.getOne(level_id)
        player = Player.Player.getOne(player_id)
        player_timer, errors = super().insert(data={
            'level_id': level.id if level else None,
            'player_id': player.id if player else None,
            'timer': 0
        }, errors=errors)
        return player_timer, errors
