from flask import Blueprint, request, make_response
from app.models import Streamer, Token
from Twitch import Twitch
import uuid
from app.constants import ApiConstant
streamer_blueprint = Blueprint('streamer', __name__, url_prefix='/api/streamers')

@streamer_blueprint.route('/', methods=['POST'])
def addStreamer():
    token = request.cookies.get('token')
    registration = Token().getOne(token)
    if not registration.user.is_admin:
        return make_response(
            {
                'errors':{
                    'user_id':ApiConstant.Errors.FORBIDDEN
                },
                'status':False
            }, ApiConstant.Http)
    streamer = Streamer()
    data = dict(request.form)
    pseudo = data.get('pseudo')
    errors = Streamer.create_api_errors()
    if pseudo:
        try:
            twitch = Twitch()
            twitch_id, streamer_name = twitch.get_user_id(pseudo)
            if twitch_id:
                data['id_twitch'] = twitch_id
                data['pseudo'] = streamer_name
            else:
                errors['pseudo'] = ApiConstant.Errors.NOT_FOUND_ON_TWITCH
        except Exception as e:
            errors['id_twitch'] = ApiConstant.Errors.SERVICE_UNAVAILIABLE
            return make_response({'errors': errors, 'status':False}, ApiConstant.Http.SERVICE_UNAVAILIABLE)
    else:
        errors['pseudo'] = ApiConstant.Errors.MISSING_REQUIRED_FIELD
    new_streamer, errors = streamer.insert(data, errors)
    if errors:       
        errors.pop('id_twitch', None)
        return make_response({'errors': errors, 'status':False}, ApiConstant.Http.BAD_REQUEST)
    return make_response({'streamer_id': new_streamer.id_public, 'status':True}, ApiConstant.Http.CREATED)

@streamer_blueprint.route('/<uuid:streamer_id>', methods=['GET'])
def getStreamer(streamer_id:uuid):
    streamers = Streamer().getOne(streamer_id)
    if not streamers:
        return make_response(
            {
                'errors':{
                    'streamer_id':ApiConstant.Errors.NOT_FOUND
                },
                'status':False
            }, ApiConstant.Http.NOT_FOUND)
    return {'streamer':dict(streamers), 'status':True}

@streamer_blueprint.route('/', methods=['GET'])
def getStreamers():
    streamer = Streamer()
    filters = request.args.to_dict()
    streamers = streamer.getAll(**filters)
    streamer_list = [dict(streamer) for streamer in streamers]
    return {'streamers':streamer_list, 'status':True}

@streamer_blueprint.route('/<uuid:streamer_id>', methods=['DELETE'])
def deleteStreamer(streamer_id:uuid):
    token = request.cookies.get('token')
    registration = Token().getOne(token)
    if not registration.user.is_admin:
        return make_response(
            {
                'errors':{
                    'user_id':ApiConstant.Errors.FORBIDDEN
                },
                'status':False
            }, ApiConstant.Http)
    streamer = Streamer().getOne(streamer_id)
    for discord_streamer in streamer.discord_streamers:
        discord_streamer.delete(discord_streamer.id_public)
    result =  streamer.delete(streamer_id)
    return make_response({'status': result}, ApiConstant.Http.OK if result else ApiConstant.Http.NOT_FOUND)

@streamer_blueprint.route('/<uuid:streamer_id>', methods=['PATCH'])
def updateStreamer(streamer_id:uuid):
    token = request.cookies.get('token')
    registration = Token().getOne(token)
    if not registration.user.is_admin:
        return make_response(
            {
                'errors':{
                    'user_id':ApiConstant.Errors.FORBIDDEN
                },
                'status':False
            }, ApiConstant.Http)
    streamer = Streamer().getOne(str(streamer_id))
    if streamer:
        data = {}
        errors = Streamer.create_api_errors()
        try:
            twitch = Twitch()
            
            twitch_id, streamer_name = twitch.get_user_from_id(streamer.id_twitch)
            if twitch_id:
                data['pseudo'] = streamer_name
            else:
                errors['id_twitch'] = ApiConstant.Errors.NOT_FOUND_ON_TWITCH
        except Exception as e:
            errors['id_twitch'] = ApiConstant.Errors.SERVICE_UNAVAILIABLE
            return make_response({'errors': errors, 'status':False}, ApiConstant.Http.SERVICE_UNAVAILIABLE)
    Streamer().update(str(streamer_id),data, errors)
    return make_response({'status': bool(streamer)}, ApiConstant.Http.OK if streamer else ApiConstant.Http.NOT_FOUND)

