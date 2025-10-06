from app.models import db, ApiModel

class Commande(ApiModel):
    __tablename__ = 'commandes'
    name = db.Column(db.String(100), nullable=False, unique=True)
