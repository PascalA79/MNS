from app.models import db, ApiModel, Role, User, UserRole
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from app.constants import ApiConstant
import random

class CheckUser(ApiModel):
    __tablename__ = 'checkusers'
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    code = db.Column(db.Integer, nullable=False)
    user = relationship("User", backref="check_users", foreign_keys=[user_id])

    __code_length:int = 4

    @classmethod
    def set_code_length(cls,code_length:int):
        if code_length >= 1:
            raise ValueError(f"code_length must be greater than 0")
        cls.__code_length = code_length

    @classmethod
    def insert(cls, user_id, errors = None):
        if not errors:
            errors = CheckUser.create_api_errors()
        user:User = User.User.getOne(user_id)
        code = random.randint(10**(cls.__code_length-1), 10**cls.__code_length-1)
        return super().insert(data=
            {
                'user_id': user.id if user else None,
                'code': code,
                'errors' : errors
            },
        )
    
    @classmethod
    def check_code(cls, user_id, code):
        errors = CheckUser.create_api_errors()
        user:User = User.User.getOne(user_id)
        if not user:
            errors['user_id'] = ApiConstant.Errors.NOT_FOUND
            return None, errors
        check_user:CheckUser = CheckUser.query.filter_by(user_id=user.id, code=code).first()
        if not check_user:
            errors['code'] = ApiConstant.Errors.NOT_FOUND
            return None, errors
        try:
            verified_role = Role.Role.getAll(**{'name':f"={'verified'}"})[0]
            user_role, errors_user_role = UserRole.UserRole.insert(user.id_public, verified_role.id_public)
            errors['roles'] = errors_user_role
        except Exception as e:
            db.session.rollback()
            return None, errors
        db.session.commit()
        
        return cls.delete(check_user.id_public)     
        
    

