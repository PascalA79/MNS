from app.models import db, ApiModel, User
from app.constants import ApiConstant
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from utility import generate_bearer_token
from datetime import datetime, timedelta
from flask import request

class Token(ApiModel):
    __tablename__ = 'tokens'
    __expiration = timedelta(days=7)

    value = db.Column(db.String(32), unique=True, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    expiration = Column(DateTime, nullable=True)

    # Ajoutez ces lignes pour définir les relations
    user = relationship("User", backref="tokens", foreign_keys=[user_id])

    @classmethod
    def getOne(cls, token:str):
        if token:
            token = token.removeprefix('Bearer ')
        return db.session.query(cls).where(cls.value == token).first()

    @classmethod
    def set_expiration(cls, days=0, seconds=0,minutes=0, hours=0, weeks=0):
        """
        Définit la durée d'expiration pour un objet de la classe.
        
        Args:
            days (int): Nombre de jours.
            seconds (int): Nombre de secondes.
            minutes (int): Nombre de minutes.
            hours (int): Nombre d'heures.
            weeks (int): Nombre de semaines.

        Returns:
            None
        """
        cls.__expiration = timedelta(days=days, seconds=seconds, minutes=minutes, hours=hours, weeks=weeks)
    
    # def get_expiration(cls):
    #     expiration_date = cls.updated_at + __class__.__expiration
    #     return expiration_date

    @classmethod
    def insert(cls, pseudo, password):
        errors = ApiModel.create_api_errors()
        user = User.check_credentials(pseudo, password)
        data = {}
        if user:
            data['user_id'] = user.id
            data['value'] = generate_bearer_token()
            data['expiration'] = datetime.now() + cls.__expiration
        else:
            errors['pseudo'] = ApiConstant.Errors.NOT_FOUND
        new_token, errors = super().insert(data, errors)
        return new_token, errors
    
    @classmethod
    def update(cls, token:str):
        errors = cls.create_api_errors()
        token.removeprefix('Bearer ')
        item = db.session.query(cls).where(value=token)
        if not item:
            errors['value'] = ApiConstant.Errors.NOT_FOUND
        return super().update(item.id,{'expiration' : datetime.now() + cls.__expiration}, errors)
    
    @classmethod
    def is_valid(cls, token:str = None):
        if token:
            token.removeprefix('Bearer ')
        the_token, errors = cls.update(token)
        print(the_token, errors)

    @classmethod
    def clean(cls):
        now = datetime.now()
        Token().delete_where(cls.expiration <=now)

    def allows_connected():
        headers = request.headers
        authorization = headers.get('Authorization')
        token = __class__().getOne(authorization)
        return True

    def allows_roles(*roles):
        headers = request.headers
        authorization = headers.get('Authorization')

