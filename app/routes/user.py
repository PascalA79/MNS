from flask import Blueprint, make_response, request
from Twitch import Twitch
from app.models import User, UserRole, Token, UserStreamer,  db, CheckUser, Streamer
import uuid
from app.constants import ApiConstant
user_blueprint = Blueprint('user', __name__, url_prefix='/api/users')
from uuid import UUID

@user_blueprint.route('/', methods=['POST'])
def addUser():
    token = request.cookies.get('token')
    registration = Token().getOne(token)
    if not (registration.user.is_admin or registration.user.is_modo):
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

    streamer_id = form.get('streamer')
    if streamer_id:
        user_streamer = UserStreamer()
        _, errors = user_streamer.insert(new_user.id_public, streamer_id, errors)
    if errors:
        db.session.rollback()
        return make_response({'status':False,'errors': errors}, ApiConstant.Http.BAD_REQUEST)

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
    is_self = registration.user.id_public == str(user_id)

    if not (registration.user.is_admin or registration.user.is_modo or is_self):
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
    streamers = {}
    for user_role in user.user_roles:
        user_roles.update(user_role.to_sub_resource())
    for discord_user in user.discord_users:
        discord_users.update(discord_user.to_sub_resource())
    for streamer_user in user.user_streamers:
        streamers.update(streamer_user.to_sub_resource())
    return {'users':dict(user), 'status':True, 'user_roles': user_roles, 'discord_users': discord_users, 'streamers': streamers}

@user_blueprint.route('/', methods=['GET'])
def getUsers():
    token = request.cookies.get('token')
    registration = Token().getOne(token)
    if not (registration.user.is_admin or registration.user.is_modo):
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
    streamers = {}
    for user in users:
        for user_role in user.user_roles:
            user_roles.update(user_role.to_sub_resource())
        for discord_user in user.discord_users:
            discord_users.update(discord_user.to_sub_resource())
        for streamer in user.user_streamers:
            streamers.update(streamer.to_sub_resource())
        
    result = {
        'users':[dict(user) for user in users],
        'user_roles': user_roles,
        'discord_users': discord_users,
        'streamers': streamers,
        'status':True
        }
    return make_response(result, ApiConstant.Http.OK, {'ETag': User.get_eTag()})

@user_blueprint.route('/<uuid:user_id>', methods=['PATCH'])
def updateUser(user_id:uuid):
    token = request.cookies.get('token')
    registration = Token().getOne(token)
    is_admin = registration.user.is_admin
    is_self = registration.user.id_public == str(user_id)
    if not is_admin and not is_self:
        return make_response(
            {
                'errors':{
                    'user_id':ApiConstant.Errors.FORBIDDEN
                },
                'status':False
            }, ApiConstant.Http.FORBIDDEN)
    
    user:User = User().getOne(str(user_id))
    if not user:
        return make_response({'status': False, 'user_id': ApiConstant.Errors.NOT_FOUND}, ApiConstant.Http.NOT_FOUND)

    errors = User.create_api_errors()
    data = dict(request.form)
    user_streamer = UserStreamer()
    streamer_id = request.form.get('streamer')

    user_streamer.delete_where(user_id=user.id)
    if streamer_id:
        try:
            UUID(streamer_id, version=4)
        except ValueError:
            streamer = Streamer()
            try:
                twitch = Twitch()
                twitch_id, streamer_name = twitch.get_user_id(streamer_id)
                if not twitch_id:
                    errors['streamer'] = ApiConstant.Errors.NOT_FOUND_ON_TWITCH
                new_streamer, _ = streamer.insert({
                    'pseudo': streamer_name,
                    'id_twitch': twitch_id
                }, errors)
                if new_streamer:
                    streamer_id = new_streamer.id_public
            except Exception as e:
                errors['streamer'] = ApiConstant.Errors.SERVICE_UNAVAILIABLE

    user_streamer = UserStreamer()
    if not errors and streamer_id:
        _, errors = user_streamer.insert(user.id_public, streamer_id, errors)

    if is_self and '/profile.html' in request.referrer :
        if not errors:
            new_user, errors = User.update(user_id, request.form, force_update_all=True, errors=errors)
        if errors:
            db.session.rollback()
            return make_response({'status':False,'errors': errors}, ApiConstant.Http.BAD_REQUEST)
        else:
            return {'status': True}
    user_role_model = UserRole()
    current_roles =  user.user_roles
    for role in current_roles:
        db.session.delete(role)
    errors = UserRole.create_api_errors()
    new_roles = request.form.getlist('roles')
    for role_id in new_roles:
        if role_id:
            _, errors = user_role_model.insert(user.id_public, role_id, errors)
    
    new_user, errors = user.update(user.id_public, data, errors)

    if errors:
        db.session.rollback()
        return make_response({'status': False, 'errors': errors}, ApiConstant.Http.BAD_REQUEST)
    else:
        db.session.commit()
        return {'status': True}

@user_blueprint.route('/', methods=['HEAD'])
def headUsers():
    return make_response('', ApiConstant.Http.OK, {'ETag': User.get_eTag()})

@user_blueprint.route('/<uuid:user_id>', methods=['HEAD'])
def headUser(user_id:uuid):
    return make_response('', ApiConstant.Http.OK, {'ETag': User.get_eTag()})
