from enum import Enum
from sqlalchemy import func
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.query import Query
from flask_sqlalchemy.model import Model
from datetime import datetime
import re

class Enum(Enum):
    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)
    
    def __ne__(self, other):
        if isinstance(other, str):
            return self.value != other
        return super().__ne__(other)
        
    @classmethod
    def values(cls):
        values = [member.value for member in cls.__members__.values()]
        return values
    
class QueryObject:
    STRING_SEPATATOR = ','

    def __init__(self, field:str, query:str) -> None:
        self.field = field
        self.type = DecoderQuery.AllowedType.STR.value
        self.tri = DecoderQuery.AllowedTri.ASC.value
        self.operator = DecoderQuery.AllowedOperator.EQUAL.value
        self.case_sensitive = False
        query_part:list[str] = query.split(self.STRING_SEPATATOR)
        self.value = query_part.pop(0)
        if not self.value:
            self.value = None

        for part in query_part:
            if '=' not in part:
                continue
            key, value = part.split('=',1)
            key = key.lower()
            value = value.lower()
            if key == DecoderQuery.AllowedKeyWord.TYPE:
                if value not in DecoderQuery.AllowedType.values():
                    continue
                self.type = value
            elif key == DecoderQuery.AllowedKeyWord.TRI:
                if value not in DecoderQuery.AllowedTri.values():
                    continue
                self.tri = value
            elif key == DecoderQuery.AllowedKeyWord.OPERATOR:
                if value in DecoderQuery.AllowedOperator.values():
                    self.operator = value
            elif key == DecoderQuery.AllowedKeyWord.CASE_SENSITIVE:
                self.case_sensitive = value == DecoderQuery.AllowedCaseSensitive.TRUE
            
class DecoderQuery:

        class AllowedKeyWord(Enum):
            TYPE = 'type'
            TRI = 'tri'
            OPERATOR = 'op'
            CASE_SENSITIVE = 'case_sensitive'

        class AllowedType(Enum):
            STR = 'str'
            INT = 'int'
            BOOL = 'bool'
            FLOAT = 'float'
            DATETIME = 'datetime'

        class AllowedTri(Enum): 
            ASC = 'asc'
            DESC = 'desc'
        
        class AllowedOperator(Enum):
            EQUAL = '='
            GREATER = '>'
            GREATER_EQUAL = '>='
            LESS = '<'
            LESS_EQUAL = '<='
            NOT_EQUAL = '!='
            LIKE = '*'

        class AllowedCaseSensitive(Enum):
            TRUE = 'true'
            FALSE = 'false'

        def __init__(self,model:Model):
            self.__model = model
            self.__query:Query = self.__model.query

            
        def add_query(self, query_object:QueryObject)->bool:
            if not hasattr(self.__model, query_object.field):
                return False
            model_attr:InstrumentedAttribute = getattr(self.__model, query_object.field)

            # type
            if query_object.type == __class__.AllowedType.STR.value:
                if not query_object.case_sensitive:
                    model_attr = func.lower(model_attr)
                    if query_object.value:
                       query_object.value = str(query_object.value).lower()
            elif query_object.type == __class__.AllowedType.BOOL.value:
                if not query_object.value:
                    query_object.value = False
                query_object.value = bool(query_object.value)
            elif query_object.type == __class__.AllowedType.DATETIME.value:
                query_object.value = datetime.fromisoformat(query_object.value)
            elif query_object.type == __class__.AllowedType.INT.value:
                if not query_object.value:
                    query_object.value = 0
                if query_object.value.isdecimal():
                    query_object.value = int(query_object.value)
            elif query_object.type == __class__.AllowedType.FLOAT.value:
                if not query_object.value:
                    query_object.value = 0.0
                    if query_object.value.isdecimal():
                        query_object.value = float(query_object.value)
            
            if query_object.value:
                # operator
                if query_object.operator == __class__.AllowedOperator.EQUAL.value:
                    self.__query = self.__query.filter(model_attr == query_object.value)
                elif query_object.operator == __class__.AllowedOperator.GREATER.value:
                    self.__query = self.__query.filter(model_attr > query_object.value)
                elif query_object.operator == __class__.AllowedOperator.GREATER_EQUAL.value:
                    self.__query = self.__query.filter(model_attr >= query_object.value)
                elif query_object.operator == __class__.AllowedOperator.LESS.value:
                    self.__query = self.__query.filter(model_attr < query_object.value)
                elif query_object.operator == __class__.AllowedOperator.LESS_EQUAL.value:
                    self.__query = self.__query.filter(model_attr <= query_object.value)
                elif query_object.operator == __class__.AllowedOperator.NOT_EQUAL.value:
                    self.__query = self.__query.filter(model_attr != query_object.value)
                elif query_object.operator == __class__.AllowedOperator.LIKE.value:
                    self.__query = self.__query.filter(model_attr.op('regexp')(query_object.value))
            # tri
            if query_object.tri == __class__.AllowedTri.ASC.value:
                self.__query = self.__query.order_by(model_attr.asc())
            elif query_object.tri == __class__.AllowedTri.DESC.value:
                self.__query = self.__query.order_by(model_attr.desc())
            return True
        
        def search(self)->list[Model]:
            return self.__query.all()
            
if __name__ == '__main__':
    from flask import Flask
    from app.models import Streamer, db

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    db.init_app(app)

    with app.app_context():
        db.create_all()
        query_decoder = DecoderQuery(Streamer)
        query_decoder.add_query(QueryObject('created_at','2024-06-29,tri=asc,type=datetime,op=>'))
        query_decoder.add_query(QueryObject('id_twitch','100000000,type=int,op=>'))
        query_decoder.add_query(QueryObject('pseudo','^m.*,op=*,type=str,case_sensitive=false'))
        responce = query_decoder.search()
        for res in responce:
            obj = dict(res)
            print(obj.get('pseudo').ljust(20), str(obj.get('id_twitch')).ljust(12), obj.get('created_at'))
        exit()
