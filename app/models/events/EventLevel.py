from app.models import db, ApiModel

class EventLevel(ApiModel):
    __tablename__ = 'event_levels'
    level_id = db.Column(db.Integer, db.ForeignKey('levels.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    # level = db.relationship('Level', backref='event_levels', foreign_keys=[level_id])
    event = db.relationship('Event', backref='event_levels', foreign_keys=[event_id])
    __table_args__ = (db.UniqueConstraint('level_id', 'event_id', name='unique_event_level'), )

    @classmethod
    def insert(cls, event_id, level_id, errors=None):
        if not errors:
            errors = EventLevel.create_api_errors()
        from app.models.events import Event, Level, PlayerTimer
        event = Event.Event.getOne(event_id)
        level = Level.Level.getOne(level_id)
        event_level, errors = super().insert(data={
            'event_id': event.id if event else None,
            'level_id': level.id if level else None
        }, errors=errors)
        # if not errors:
        #     for player in event.players:
        #         PlayerTimer.PlayerTimer.insert({
        #             'level_id': level.id,
        #             'player_id': player.id
        #         })
        return event_level, errors

    @classmethod
    def delete(cls, id_public):
        event_level = cls.getOne(id_public)
        # for player_timer in event_level.level.player_timers:
        #     player_timer.delete(player_timer.id_public)
        return super().delete(id_public)
