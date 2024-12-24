from app.models import db, ApiModel

class Player(ApiModel):
    __tablename__ = 'players'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user = db.relationship('User', backref='users', foreign_keys=[user_id])
    event = db.relationship('Event', backref='players', foreign_keys=[event_id])
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='unique_players'), )

    @classmethod
    def insert(cls, event_id, user_id, errors=None):
        if not errors:
            errors = Player.create_api_errors()
        from app.models import Event, User
        event = Event.getOne(event_id)
        user = User.getOne(user_id)
        player, errors =  super().insert(data={
            'event_id': event.id if event else None,
            'user_id': user.id if user else None
        }, errors=errors)
        # if not errors:
        #     from app.models.events import PlayerTimer
        #     for level in event.levels:
        #         PlayerTimer.PlayerTimer.insert({
        #             'level_id': level.id,
        #             'player_id': player.id
        #         })

        return player, errors
    @classmethod
    def delete(cls, id_public):
        player = cls.getOne(id_public)
        # for timer in player.timers:
        #     timer.delete(timer.id_public)
        return super().delete(id_public)
    
    
