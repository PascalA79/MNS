from app.models import db, ApiModel
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, UniqueConstraint

class CommandeGuildPermission(ApiModel):
    __tablename__ = 'commandes_guild_permissions'
    id_commandes_guild = db.Column(db.Integer, db.ForeignKey('commandes_guild.id'))
    permission = db.Column(db.String(100))
    allow_permission = db.Column(db.Boolean)

    __table_args__ = (UniqueConstraint('id_commandes_guild', 'permission', name='uq_commandes_guild_permissions'),)

    commande_guild = relationship("CommandeGuild", backref="commandes_guild_permissions", foreign_keys=[id_commandes_guild])
