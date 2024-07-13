from flask import Blueprint, request, make_response
from app.models import Game, Token
from Twitch import Twitch
import uuid
from app.constants import ApiConstant
game_blueprint = Blueprint('game', __name__, url_prefix='/api/games')

@game_blueprint.route('/', methods=['POST'])
def addGame():
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
    game = Game()
    data = dict(request.form)
    game_name = data.get('name')
    errors = Game.create_api_errors()
    if game_name:
        try:
            twitch = Twitch()
            twitch_id, game_name = twitch.get_id_game(game_name)
            if twitch_id:
                data['id_twitch'] = twitch_id
                data['name'] = game_name
            else:
                errors['name'] = ApiConstant.Errors.NOT_FOUND_ON_TWITCH
        except Exception as e:
            errors['id_twitch'] = ApiConstant.Errors.SERVICE_UNAVAILIABLE
            return make_response({'errors': errors, 'status':False}, ApiConstant.Http.SERVICE_UNAVAILIABLE)
    else:
        errors['pseudo'] = ApiConstant.Errors.MISSING_REQUIRED_FIELD
    new_game, errors = game.insert(data, errors)
    if errors:       
        errors.pop('id_twitch', None)
        return make_response({'errors': errors, 'status':False}, ApiConstant.Http.BAD_REQUEST)
    return make_response({'game_id': new_game.id_public, 'status':True}, ApiConstant.Http.CREATED)

@game_blueprint.route('/<uuid:game_id>', methods=['GET'])
def getGame(game_id:uuid):
    game = Game().getOne(game_id)
    if not game:
        return make_response(
            {
                'errors':{
                    'game_id':ApiConstant.Errors.NOT_FOUND
                },
                'status':False
            }, ApiConstant.Http.NOT_FOUND)
    return {'game':dict(game), 'status':True}

@game_blueprint.route('/', methods=['GET'])
def getGames():
    game = Game()
    filters = request.args.to_dict()
    games = game.getAll(**filters)
    game_list = [dict(game) for game in games]
    return {'games':game_list, 'status':True}

@game_blueprint.route('/<uuid:game_id>', methods=['DELETE'])
def deleteGame(game_id:uuid):
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
    game = Game.getOne(game_id)
    for discord_game in game.discord_games:
        discord_game.delete(discord_game.id_public)
    result =  game.delete(game_id)
    return make_response({'status': result}, ApiConstant.Http.OK if result else ApiConstant.Http.NOT_FOUND)

@game_blueprint.route('/<uuid:game_id>', methods=['PATCH'])
def updateGame(game_id:uuid):
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
    game = Game.getOne(str(game_id))
    if game:
        data = {}
        errors = Game.create_api_errors()
        try:
            twitch = Twitch()
            
            twitch_id, game_name = twitch.get_id_game(game.id_twitch)
            if twitch_id:
                data['pseudo'] = game_name
            else:
                errors['id_twitch'] = ApiConstant.Errors.NOT_FOUND_ON_TWITCH
        except Exception as e:
            errors['id_twitch'] = ApiConstant.Errors.SERVICE_UNAVAILIABLE
            return make_response({'errors': errors, 'status':False}, ApiConstant.Http.SERVICE_UNAVAILIABLE)
    Game.update(game,data, errors)
    return make_response({'status': bool(game)}, ApiConstant.Http.OK if game else ApiConstant.Http.NOT_FOUND)

