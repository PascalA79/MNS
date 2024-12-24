from app.models import db, ApiModel
import re
from app.constants import ApiConstant
from Smm2Info import Smm2Info
from utility import save_image_from_url, remove_image


class Level(ApiModel):
    __tablename__ = 'levels'
    __level_file_image = None

    creator = db.Column(db.String(80), nullable=True)
    code = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=True)
    description = db.Column(db.String(128), nullable=True)
    level_image_path = db.Column(db.String(128), nullable=False)
    creator_image_path = db.Column(db.String(128), nullable=True)

    event_levels = db.relationship('EventLevel', backref='level', lazy=True)

    @staticmethod
    def is_valid_code(code):
        return re.match(r'^(?=.{9}$|(?=.{11}$))[A-Za-z0-9]{3}-?[A-Za-z0-9]{3}-?[A-Za-z0-9]{3}$', code)
    
    @staticmethod
    def convert_code(code:str):
        return code.replace('-', '').upper()

    @classmethod
    def set_level_image_file(cls, default_file):
        cls.__level_file_image = default_file
    
    @classmethod
    def set_creator_image_file(cls, default_file):
        cls.__creator_file_image = default_file

    @classmethod
    def insert(cls, data, errors = None):
        data = dict(data)
        level_code = data.get('code', None)
        errors = Level.create_api_errors()
        if not level_code:
            errors['code'] = ApiConstant.Errors.MISSING_REQUIRED_FIELD
        elif not Level.is_valid_code(level_code):
            errors['code'] = ApiConstant.Errors.INVALID_FIELD_VALUE
        else:
            info_level = Smm2Info().get_level(level_code)
            if not info_level:
                errors['code'] = ApiConstant.Errors.NOT_FOUND_ON_SMM2
            else:
                data['code'] = Level.convert_code(info_level['level']['code'])
                data['name'] = info_level['level']['name']
                data['description'] = info_level['level']['description']
                data['creator'] = info_level['creator']['name']
                level_image_url = info_level['level']['one_screen_thumbnail_url']
                level_path = f"{cls.__level_file_image}/{data['code']}.png"
                data['level_image_path'] = level_path.removeprefix('app/static')
                creator_image_url = info_level['creator']['mii_image']
                creator_path = f"{cls.__creator_file_image}/{info_level['creator']['code']}.png"
                data['creator_image_path'] = creator_path.removeprefix('app/static')
                level_response = save_image_from_url(level_image_url, level_path, size=(640, 360), format='PNG')
                creator_response = save_image_from_url(creator_image_url, creator_path, size=(256, 256), format='PNG')
                if not level_response or not creator_response:
                    errors['code'] = ApiConstant.Errors.SERVICE_UNAVAILIABLE

        return super().insert(data, errors)

    @classmethod
    def delete(cls, id_public):
        level = cls.getOne(id_public)
        if level:
            level_path = '/app/static' + level.level_image_path
            creator_path = '/app/static' + level.creator_image_path
            try:
                remove_image(level_path)
                remove_image( creator_path)
            except FileNotFoundError:
                pass
        return super().delete(id_public)
        
