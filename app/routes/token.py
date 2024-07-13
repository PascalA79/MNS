from flask import Blueprint, request, make_response
from app.models import Token
from app.constants import ApiConstant
token_blueprint = Blueprint('token', __name__, url_prefix='/token')

@token_blueprint.route('/', methods=['POST'])
def getToken():
    pseudo = request.form.get('pseudo')
    password = request.form.get('password')
    token, errors = Token().insert(pseudo, password)
    if errors:
        return make_response(
            {
                'errors': errors,
                'status':False
            },
            ApiConstant.Http.BAD_REQUEST
        )
    if not token:
        return make_response(
            {
                'status':False
            },
            ApiConstant.Http.INTERNAL_SERVER_ERROR
        )
    return make_response(
        {
            'value': 'Bearer ' + token.value, 
            'status': True
        }
        , ApiConstant.Http.CREATED
    )
@token_blueprint.route('/', methods=['GET'])
def getInfo():
    Token.allows_connected()
    return {'status':True}