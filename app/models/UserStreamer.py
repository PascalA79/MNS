from app.models import db, ApiModel
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, UniqueConstraint


class UserStreamer(ApiModel):
    __tablename__ = 'userstreamers'
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    streamer_id = db.Column(db.Integer, ForeignKey('streamers.id'), nullable=False)
    user = relationship("User", backref="user_streamers", foreign_keys=[user_id])
    streamer = relationship('Streamer', backref="user_streamers", foreign_keys=[streamer_id])

    __table_args__ = (UniqueConstraint('user_id', 'streamer_id', name='unique_user_streamer'), )

    @classmethod
    def insert(cls, user_id, streamer_id, errors):
        from app.models import User, Streamer
        user = User.getOne(user_id)
        streamer = Streamer.getOne(streamer_id)
        return super().insert(data=
            {
                'user_id': user.id if user else None,
                'streamer_id': streamer.id if streamer else None
            },
            errors = errors
        )
