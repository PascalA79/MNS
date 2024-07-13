from flask import Blueprint, make_response, request
from app.models import User, UserRole, Token,  db, CheckUser
import uuid
from app.constants import ApiConstant
user_blueprint = Blueprint('user', __name__, url_prefix='/api/users')

@user_blueprint.route('/', methods=['POST'])
def addUser():
    token = request.cookies.get('token')
    registration = Token().getOne(token)
    if not registration.user.is_admin:
        return make_response(
            {
                'errors':{
                    'user_id':ApiConstant.Errors.FORBIDDEN
                },
                'status':False
            }, ApiConstant.Http.FORBIDDEN)
    user = User()
    form = request.form

    new_user, errors = user.insert(form)
    if errors:
        return make_response({'status':False,'errors': errors}, ApiConstant.Http.BAD_REQUEST)
    user_role_model = UserRole()
    roles = form.getlist('roles')
    role_errors = user_role_model.create_api_errors()
    for role_id in roles:
        user_role, role_errors = user_role_model.insert(new_user.id_public,role_id, role_errors)

    return make_response({'status':True, 'user_id': new_user.id_public}, ApiConstant.Http.CREATED)

@user_blueprint.route('/<uuid:user_id>', methods=['DELETE'])
def deleteUser(user_id:uuid):
    token = request.cookies.get('token')
    registration = Token().getOne(token)
    if not registration.user.is_admin:
        return make_response(
            {
                'errors':{
                    'user_id':ApiConstant.Errors.FORBIDDEN
                },
                'status':False
            }, ApiConstant.Http.FORBIDDEN)
    user = User()
    result =  user.delete(str(user_id))
    return make_response({'status': result}, ApiConstant.Http.OK if result else ApiConstant.Http.NOT_FOUND)

@user_blueprint.route('/<uuid:user_id>', methods=['GET'])
def getUser(user_id:uuid):
    token = request.cookies.get('token')
    registration = Token().getOne(token)
    if not registration.user.is_admin:
        return make_response(
            {
                'errors':{
                    'user_id':ApiConstant.Errors.FORBIDDEN
                },
                'status':False
            }, ApiConstant.Http.FORBIDDEN)
    user = User().getOne(user_id)
    if not user:
        return make_response(
            {
                'status':False, 
                'errors':{'user_id': ApiConstant.Errors.NOT_FOUND}
            },
            ApiConstant.Http.NOT_FOUND
        )
    user_roles = {}
    discord_users = {}
    for user_role in user.user_roles:
        user_roles.update(user_role.to_sub_resource())
    for discord_user in user.discord_user:
        discord_users.update(discord_user.to_sub_resource())
    return {'users':dict(user), 'status':True, 'user_roles': user_roles, 'discord_users': discord_users}

@user_blueprint.route('/', methods=['GET'])
def getUsers():
    token = request.cookies.get('token')
    registration = Token().getOne(token)
    if not registration:
        return make_response(
            {
                'errors':{
                    'user_id':ApiConstant.Errors.UNAUTHORIZED
                },
                'status':False
            }, ApiConstant.Http.UNAUTHORIZED)
    if not registration.user.is_admin:
        return make_response(
            {
                'errors':{
                    'user_id':ApiConstant.Errors.FORBIDDEN
                },
                'status':False
            }, ApiConstant.Http.FORBIDDEN)
    filters = request.args.to_dict()
    users = User().getAll(**filters)
    user_roles = {}
    discord_users = {}
    for user in users:
        for user_role in user.user_roles:
            user_roles.update(user_role.to_sub_resource())
        for discord_user in user.discord_users:
            discord_users.update(discord_user.to_sub_resource())
        
    return {'users':[dict(user) for user in users], 'user_roles': user_roles, 'discord_users': discord_users, 'status':True}

@user_blueprint.route('/<uuid:user_id>', methods=['PATCH'])
def updateUser(user_id:uuid):
    token = request.cookies.get('token')
    registration = Token().getOne(token)
    if not registration.user.is_admin:
        return make_response(
            {
                'errors':{
                    'user_id':ApiConstant.Errors.FORBIDDEN
                },
                'status':False
            }, ApiConstant.Http.FORBIDDEN)
    user:User = User().getOne(str(user_id))
    if user:
        user_role_model = UserRole()
        current_roles =  user.user_roles
        for role in current_roles:
            db.session.delete(role)
            db.session.commit()
        errors = UserRole.create_api_errors()
        new_roles = request.form.getlist('roles')
        for role_id in new_roles:
            user_role, role_errors = user_role_model.insert(user.id_public,role_id)
            if role_errors:
                errors.update(role_errors)
        data = dict(request.form)
        new_user, user_errors = user.update(user.id_public, data)
        if user_errors:
            errors.update(user_errors)
        if errors:
            return {'status': False, 'errors': errors}
        return {'status': True}
    return make_response({'status': False, 'user_id': ApiConstant.Errors.NOT_FOUND}, ApiConstant.Http.NOT_FOUND)

@user_blueprint.route('/self', methods=['POST'])
def addUserSelf():
    user = User()
    form = request.form
    new_user, errors, check_user = user.insert_self(form)
    if errors:
        return make_response({'status':False,'errors': errors}, ApiConstant.Http.BAD_REQUEST)
    
    return make_response({'status':True, 'user_id': new_user.id_public, 'code': check_user.code}, ApiConstant.Http.CREATED)
