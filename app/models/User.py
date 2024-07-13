from app.models import db, bcrypt, ApiModel, CheckUser, Role, User
from utility import delete_keys

class User(ApiModel):
    __tablename__ = 'users'
    pseudo = db.Column(db.String(80), unique=True, nullable=False)   
    password = db.Column(db.String(128), nullable=False)

    @classmethod
    def insert_self(cls, data):
        new_data = dict(data)
        user, errors = cls.insert(new_data)
        try:
            if user:
                check_user_model = CheckUser.CheckUser()
                check_user, errors = check_user_model.insert(user.id_public, None)
                return user, None, check_user
            return None, errors, None
        except Exception as e:
            db.session.rollback()
            user.delete(user.id_public)
            return None, e, None

    @classmethod
    def validate_self(cls, user_id, code):
        check_user, errors = CheckUser.check_code(user_id, code)
        if not check_user:
            return False, errors
        user:User = cls.getOne(user_id)

        user.roles.append(Role.query.filter_by(name='verified').first())
        db.session.commit()
        return True, errors

    @classmethod
    def insert(cls, data):
        new_data = dict(data)
        if 'password' in data and data['password']:
            new_data['password'] = bcrypt.generate_password_hash(new_data['password']).decode('utf-8')
        else:
            new_data['password'] = None
        return super().insert(new_data)
    
    @classmethod
    def update(cls, id_public, data, errors = None, force_update_all=False):
        new_data = dict(data)
        if not force_update_all:
            delete_keys(new_data, 'password')
        return super().update(id_public, new_data, errors, force_update_all)
    
    @classmethod
    def check_credentials(cls, pseudo, password):
        user = cls.query.filter_by(pseudo=pseudo).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        return None
    
    @classmethod
    def delete(cls, id_public):
        user = cls.getOne(id_public)
        for user_role in user.user_roles:
            db.session.delete(user_role)
        for token in user.token:
            db.session.delete(token)
        for discord_user in user.discord_user:
            db.session.delete(discord_user)
        for check_user in user.check_users:
            db.session.delete(check_user)
        db.session.commit()
        return super().delete(id_public)
    @property
    def is_verified(self):
        return 'verified' in [role.role.name for role in self.user_roles]
    @property
    def is_admin(self):
        return 'admin' in [role.role.name for role in self.user_roles]
    @property
    def is_modo(self):
        return 'modo' in [role.role.name for role in self.user_roles]
    @property
    def is_sudo(self):
        return 'sudo' in [role.role.name for role in self.user_roles]
    
