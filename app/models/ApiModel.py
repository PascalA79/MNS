from app.models import db
from app.constants import ApiConstant
import uuid
from utility import dict_merge, split_string, convert_to_int_if_possible, get_attribute, has_attribute, get_all_subclasses, to_pascal_case, delete_keys
from sqlalchemy.schema import UniqueConstraint
import re
      
class ApiModel(db.Model):
    
    @staticmethod
    def create_api_errors():
        return ApiModel.__ErrorsDict()
    
    class __ErrorsDict(dict):
        
        class ErrorsList(list):
            def __setitem__(self, index, value):
                raise TypeError("Cannot modify the errors")
        def __setitem__(self, __key, item):
            if not hasattr(ApiConstant.Errors(),(str(item))):
                raise ValueError("Invalid error: {}".format(item))

            if isinstance(self.get(__key), list):
                if item not in self[__key]:
                    new_value = self.get(__key) + __class__.ErrorsList([item])
            else:
                new_value = __class__.ErrorsList([item])

            super().__setitem__(__key, new_value)  

        def is_empty(self)->bool:
            return bool(self)

    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    id_public = db.Column(db.String, unique=True, index=True, nullable=False, default=None)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())
    # deleted_at = db.Column(db.DateTime, default=None, nullable=True)

    __column_dict:dict = None
    __column_sub_resource:dict = None

    @classmethod
    def validate_convert_column(cls,convert_column:dict):
        subs_class = get_all_subclasses(db.Model)
        subs_class.update([db.Model])
        subs_class = list(subs_class)
        for column in convert_column.values():
            attributes = column.split('.')
            if not has_attribute(cls, column):
                for index, current_attribut in enumerate(attributes):
                    current_attributs = '.'.join(attributes[index + 1:])
                    if current_attributs:
                        for sub_class in subs_class:
                            if sub_class.__name__ == to_pascal_case(current_attribut):
                                if has_attribute(sub_class, current_attributs):
                                    break  # Sortir de la boucle interne si l'attribut est trouvé
                        else:
                            continue  # Continuer à parcourir les sous-classes si l'attribut n'est pas trouvé
                        break  # Sortir de la boucle externe si l'attribut est trouvé
                else:
                    raise ValueError(f"{column} does not exist in {cls.__name__}")

    @classmethod
    def set_dict_key(cls,convert_column:dict):
        cls.validate_convert_column(convert_column)
        cls.__column_dict = convert_column

    @classmethod
    def set_sub_resource_key(cls, convert_column):
        cls.validate_convert_column(convert_column)
        cls.__column_sub_resource = convert_column
    
    def to_sub_resource(self):
        class_column = self.__class__.__column_sub_resource
        if class_column:
            return {str(self.id_public):{column_name: str(get_attribute(self, column)) for column_name, column in class_column.items()}}
        else:
            return {self.id_public:{column.name: str(getattr(self, column.name)) for column in self.__table__.columns}}

    def __to_dict(self):
        """
        Convertit l'objet en un dictionnaire.
        """
        class_column = self.__class__.__column_dict
        if class_column:
            return {column_name: str(get_attribute(self, column)) for column_name, column in class_column.items()}
        else:
            return {column.name: str(getattr(self, column.name)) for column in self.__table__.columns}
    
    def __iter__(self):
        return iter(self.__to_dict().items())

    @classmethod
    def getOne(cls, id_public):
        result = cls.query.filter_by(id_public=str(id_public)).first()
        return result    
    
    @classmethod
    def getAll(cls, **conditions)->'list[ApiModel]':
        allowed_operators = ['=', '>=', '<=', '<', '>', '!=', '*']
        other_operator = []
        query = db.session.query(cls)
        for field, condition in conditions.items():
            operator, search_value = split_string(condition, allowed_operators)
            if operator and search_value:
                search_value = convert_to_int_if_possible(search_value)
                value = get_attribute(cls, field) if has_attribute(cls, field) else None
                if operator == '=':
                    query = query.where(value == search_value)
                elif operator == '>':
                    query = query.where(value > search_value)
                elif operator == '>=':
                    query = query.where(value >= search_value)
                elif operator == '<':
                    query = query.where(value < search_value)
                elif operator == '<=':
                    query = query.where(value <= search_value)
                elif operator == '!=':
                    query = query.where(value != search_value)
                else :
                    other_operator.append((field, operator,search_value))
            else:
                query = query.where(None)
        results = [item[0] for item in db.session.execute(query).all()]
        # for field, operator, search_value in other_operator:
        #     if operator == '*':
        #         regex_pattern = re.compile(search_value,re.IGNORECASE)
        #         results = filter(lambda x: regex_pattern.match(getattr(x, field) if hasattr(x, field) else None), results)
        return list(results)


    @classmethod
    def insert(cls, data, errors:__ErrorsDict = None):
        data =dict(data)
        if errors is None:
            errors = ApiModel.create_api_errors()
        delete_keys(data, 
            'created_at',
            'updated_at',
            'id',
            'id_public'
        )
        # mettre à null les champs vides
        for column in cls.__table__.columns:
            column_name = column.name
            if not data.get(column_name):
                data[column_name] = None

        data['id_public'] = str(uuid.uuid4())
        errors_validate = cls.validate(cls,data)
        errors = dict_merge(errors,errors_validate)
        new_item = None
        if not errors:
            class_props = vars(cls).keys()
            new_data = {key: value for key, value in data.items() if key in class_props}
            new_item = cls(**new_data)
            db.session.add(new_item)
            db.session.commit()
        else:
            db.session.rollback()
        return new_item, errors

    @classmethod
    def update(cls, id_public, data, errors:__ErrorsDict = None, force_update_all = False):
        if errors is None:
            errors = ApiModel.create_api_errors()
        item = cls.getOne(str(id_public))
        if item:
            data = dict(data)
            if not force_update_all:
                delete_keys(data, 
                    'created_at',
                    'updated_at',
                    'id',
                    'id_public'
                )

            for key, value in data.items():
                setattr(item, key, value)
            item.updated_at = db.func.current_timestamp()
            error_validate = cls.validate(cls,data,str(id_public))
            errors = dict_merge(errors,error_validate)
            if not errors:
                db.session.commit()
            else:
                db.session.rollback()
        else:
            errors['id'] = ApiConstant.Errors.NOT_FOUND 
        return item, errors
    @classmethod
    def delete(cls, id_public):
        item = cls.getOne(id_public)
        if item == None:
            db.session.rollback()
            return False
        db.session.delete(item)
        db.session.commit()
        return bool(item)
    
    def delete_where(cls, **condition):
        """
        Supprime les enregistrements de la table qui satisfont à la condition donnée.
        :param condition: Condition SQLAlchemy pour filtrer les enregistrements à supprimer.
        :return: Le nombre d'enregistrements supprimés.
        """
        items = cls.query.filter(condition).all()
        for item in items:
            db.session.delete(item)
            # item.deleted_at = db.func.current_timestamp()
        db.session.commit()
        return len(items)
    
    def validate(self, data:dict, item_id = None):
        errors = ApiModel.create_api_errors()
        for column in self.__table__.columns:
            column_name = column.name
            if not item_id and column_name not in ['id', 'id_public', 'created_at', 'updated_at'] and not column.nullable and (column_name not in data or data.get(column_name) == None):
                errors[column_name] = ApiConstant.Errors.MISSING_REQUIRED_FIELD
            if column_name in data:
                column_type = column.type.python_type
                column_value = data[column_name]

                if not isinstance(column_value, column_type):
                    if column.nullable and column_value != None:
                        errors[column_name] = ApiConstant.Errors.INVALID_DATA_TYPE
                if column.foreign_keys:
                    for fk in column.foreign_keys:
                        fk_column_name = str(fk.column.name)
                        fk_model = fk.column.table
                        fk_value = data.get(column_name)
                        if fk_value is not None:
                            referenced_item = db.session.query(fk_model).filter_by(**{fk_column_name: fk_value}).first()
                            if not referenced_item:
                                errors[column_name] = ApiConstant.Errors.FOREIGN_KEY_CONSTRAINT_VIOLATION

        constraints = self.__table__.constraints
        for constraint in constraints if constraints else []:
            if isinstance(constraint, UniqueConstraint):
                identifiant = {}
                for column in constraint.columns:
                    identifiant[column.name] = data.get(column.name, None)
                search = identifiant
                existing_item = None
                try:
                    existing_item = self.query.filter_by(**search).first()
                except Exception as e:
                    print(e)
                if existing_item and item_id and existing_item.id_public == item_id:
                    continue
                if existing_item:
                    for field in constraint.columns.keys():
                        if len(constraint.columns) == 1:
                            errors[field] = ApiConstant.Errors.UNIQUE_CONSTRAINT_VIOLATION 
                        else:
                            errors[field] = ApiConstant.Errors.MULTIPLE_UNIQUE_CONSTRAINT_VIOLATION
        return errors


if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    from app.models import Role, User, UserRole
    # Initialise la base de données avec l'application Flask
    db.init_app(app)

    # Crée toutes les tables dans la base de données
    with app.app_context():
        db.create_all()

    # Crée un utilisateur, un rôle et une relation entre eux pour tester
    with app.app_context():
        # Supprimer tous les enregistrements de la table User
        db.session.query(User).delete()
        db.session.commit()

        # Supprimer tous les enregistrements de la table Role
        db.session.query(Role).delete()
        db.session.commit()

        # Supprimer tous les enregistrements de la table UserRole
        db.session.query(UserRole).delete()
        db.session.commit()
        # Crée un utilisateur
        user = User(pseudo='john_doe')
        db.session.add(user)
        db.session.commit()

        # Crée un rôle
        role = Role(name='admin')
        db.session.add(role)
        db.session.commit()

        # Crée une relation entre l'utilisateur et le rôle
        user_role = UserRole(user_id=user.id, role_id=role.id)
        db.session.add(user_role)
        db.session.commit()

        # Supression
        user


    # Affiche les données dans la console
    with app.app_context():
        users = User.query.all()
        roles = Role.query.all()
        user_roles = UserRole.query.all()

        print("Utilisateurs:")
        for u in users:
            print(f"ID: {u.id}, Pseudo: {u.pseudo}")

        print("\nRôles:")
        for r in roles:
            print(f"ID: {r.id}, Nom: {r.name}")

        print("\nRelations Utilisateur-Rôle:")
        for ur in user_roles:
            print(f"ID: {ur.id}, Utilisateur ID: {ur.user_id}, Rôle ID: {ur.role_id}")



        user_to_delete = User.query.filter_by(pseudo='john_doe').first()

        if user_to_delete:
            User.delete(user_to_delete.id)
            #db.session.delete(user_to_delete)
            #db.session.commit()



