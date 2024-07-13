# from app.models import db, ApiModel
# from sqlalchemy.orm import relationship
# from sqlalchemy import ForeignKey
# from NotifDiscord import CurrentStreamer

# # guide pour afficher les notifications sur les discord
# class Template(ApiModel):
#     __tablename__ = 'templates'
#     discord_id = db.Column(db.String(80), ForeignKey('discords.id'), nullable=False)
#     template = db.Column(db.String(MAX), nullable=True)

#     discord = relationship("Discord", backref="templates", foreign_keys=[discord_id])

#     @classmethod
#     def create_template(cls, template_id, current_streamer:CurrentStreamer):
#         template = cls.getOne(template_id)
