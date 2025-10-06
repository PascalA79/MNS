from app.models import db, ApiModel
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint, ForeignKey

class CommandeGuild(ApiModel):
    __tablename__ = 'commandes_guild'
    id_guild = db.Column(db.Integer, ForeignKey('discord_apps.id'), nullable=False)
    id_commande = db.Column(db.Integer, ForeignKey('commandes.id'), nullable=False)

    __table_args__ = (UniqueConstraint('id_guild', 'id_commande', name='uq_commandes_guild'),)

    discord_app = relationship("DiscordApp", backref="commandes_guild", foreign_keys=[id_guild])
    commande = relationship("Commande", backref="commandes_guild", foreign_keys=[id_commande])

    def get_permission(command_name: str, id_guild: int):
        from app.models import Commande, DiscordApp
        commande = Commande.getAll(**{'name':command_name})
        guild = DiscordApp.getAll(**{'id_guild':id_guild})
        if not (commande and guild):
            return []
        command = commande[0]
        guild = guild[0]
        command_guild = CommandeGuild.getAll(**{'id_commande':command.id, 'id_guild':guild.id})
        if not command_guild:
            return []
        return command_guild[0].commandes_guild_permissions
    