from app.models import db, ApiModel
from sqlalchemy.orm import relationship

class Role(ApiModel):
    __tablename__ = 'roles'
    name = db.Column(db.String(80), unique=True, nullable=False)
    
    def delete(cls, id_public):
        role = cls.getOne(id_public)
        if not role:
            return False
        for user_role in role.user_roles:
            db.session.delete(user_role)
        return super().delete(id_public)