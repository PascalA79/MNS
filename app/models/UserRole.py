from app.models import db, ApiModel, Role, User
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, UniqueConstraint

class UserRole(ApiModel):
    __tablename__ = 'userroles'
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, ForeignKey('roles.id'), nullable=False)

    # Ajoutez ces lignes pour définir les relations
    user = relationship("User", backref="user_roles", foreign_keys=[user_id])
    role = relationship('Role', backref="user_roles", foreign_keys=[role_id])
    # token = relationship('Token', back_populates='user_roles')

    __table_args__ = (UniqueConstraint('user_id', 'role_id', name='unique_user_role'), )

    @classmethod
    def insert(cls, user_id, role_id, errors = None):
        if not errors:
            errors = UserRole.create_api_errors()
        user = User.User.getOne(user_id)
        role = Role.Role.getOne(role_id)
        return super().insert(data=
            {
                'user_id': user.id if user else None,
                'role_id': role.id if role else None
            },
            errors = errors
        )