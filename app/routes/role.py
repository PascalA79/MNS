from flask import Blueprint,  request, make_response
from app.models import Role, db
from app.constants import ApiConstant
import uuid
role_blueprint = Blueprint('role', __name__, url_prefix='/api/roles')


@role_blueprint.route('/', methods=['POST'])
def addRole():
    role = Role()
    new_role, errors = role.insert(request.form)
    if errors:
        return make_response({'errors': errors, 'status':False}, 400)
    return {'role_id': new_role.id_public}

@role_blueprint.route('/<uuid:role_id>', methods=['GET'])
def getRole(role_id:uuid):
    role = Role.getOne(role_id)
    record = Role.query.filter_by(id_public=role_id).first()
    if not role:
        return make_response(
            {
                'status':False, 
                'errors':{'role_id': ApiConstant.Errors.NOT_FOUND}
            },
            ApiConstant.Http.NOT_FOUND
        )
    return dict(role)
@role_blueprint.route('/<string:role_name>', methods=['GET'])
def getRoleName(role_name:str):
    record = Role.query.filter_by(name=role_name).first()
    if not record:
        return make_response(
            {
                'status':False, 
                'errors':{'role_id': ApiConstant.Errors.NOT_FOUND}
            },
            ApiConstant.Http.NOT_FOUND
        )
    return dict(record)
@role_blueprint.route('/', methods=['GET'])
def getRoles():
    role = Role()
    filters = request.args.to_dict()
    roles = role.getAll(**filters)
    return {'roles':[dict(role) for role in roles], 'status':True}

@role_blueprint.route('/<uuid:role_id>', methods=['DELETE'])
def deleteRole(role_id:uuid):
    role = Role()
    result =  role.delete(role_id)
    return make_response({'status': result}, ApiConstant.Http.OK if result else ApiConstant.Http.NOT_FOUND)
