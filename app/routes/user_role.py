from flask import Blueprint, request, make_response
from app.models import UserRole, User, Role
from app.constants import ApiConstant
import uuid
user_role_blueprint = Blueprint('user_role', __name__, url_prefix='/api/user_roles')


@user_role_blueprint.route('/', methods=['POST'])
def addUserRole():
    user_role = UserRole()
    new_user_role, errors = user_role.insert(**request.form)
    if errors:
        return {'errors': errors, 'status':False}
    return make_response(
        {
            'user_role_id': new_user_role.id_public, 
            'status':True
        }
        , ApiConstant.Http.CREATED
    )

@user_role_blueprint.route('/<uuid:user_role_id>', methods=['GET'])
def getUserRole(user_role_id:uuid):
    user_role = UserRole().getOne(str(user_role_id))
    if not user_role:
        return make_response(
            {
                'status':False, 
                'errors':{'user_role_id': ApiConstant.Errors.NOT_FOUND}
            },
            ApiConstant.Http.NOT_FOUND
        )
    users = {}
    roles = {}
    users.update(user_role.user.to_sub_resource())
    roles.update(user_role.role.to_sub_resource())
    return {
        'user_roles':dict(user_role),
        'users': users,
        'roles': roles,
        'status':True
    }

@user_role_blueprint.route('/user/<uuid:user_id>', methods=['GET'])
def getRole_User(user_id:uuid):
    user = User().getOne(user_id)
    if not user:
        return make_response(
            {
                'status':False, 
                'errors':{'user_id': ApiConstant.Errors.NOT_FOUND}
            },
            ApiConstant.Http.NOT_FOUND
        )
    user_roles = UserRole().getAll(**{'user_id':f"{user.id}"})
    if not user_roles:
        return make_response(
            {
                'status':False, 
                'errors':{'user_role_id': ApiConstant.Errors.NOT_FOUND}
            },
            ApiConstant.Http.NOT_FOUND
        )
    users = {}
    roles = {}
    for user_role in user_roles:
        users.update(user_role.user.to_sub_resource())
        roles.update(user_role.role.to_sub_resource())
    return {
        'user_roles':[dict(user_role) for user_role in user_roles],
        'users': users,
        'roles': roles,
        'status':True
    }

@user_role_blueprint.route('/role/<uuid:role_id>', methods=['GET'])
def getUser_Role(role_id:uuid):
    role = Role().getOne(role_id)
    if not role:
        return make_response({
            'status':False,
            'errors':{'role_id':ApiConstant.Errors.NOT_FOUND}
        },
        ApiConstant.Http.NOT_FOUND)
    user_roles = UserRole().getAll(**{'role_id':f"{role.id}"})
    if not user_roles:
        return make_response(
            {
                'status':False, 
                'errors':{'user_role_id': ApiConstant.Errors.NOT_FOUND}
            },
            ApiConstant.Http.NOT_FOUND
        )
    user_roles_set = set(user_roles)
    users = {}
    roles = {}
    for user_role in user_roles:
        users.update(user_role.user.to_sub_resource())
        for user_role_user in user_role.user.user_roles:
            user_roles_set.add(user_role_user)
        for role in user_role.user.user_roles:
            if not str(role.id_public) in roles.keys():
                roles.update(role.role.to_sub_resource())
    return {
        'user_roles':[dict(user_role) for user_role in user_roles_set],
        'users': users,
        'roles': roles,
        'status':True
    }

@user_role_blueprint.route('/', methods=['GET'])
def getUserRoles():
    user_role = UserRole()
    filters = request.args.to_dict()
    user_roles = user_role.getAll(**filters)
    users = {}
    roles = {}
    for user_role in user_roles:
        users.update(user_role.user.to_sub_resource())
        roles.update(user_role.role.to_sub_resource())
    return {
        'user_roles':[dict(user_role) for user_role in user_roles],
        'users': users,
        'roles': roles,
        'status':True
    }
