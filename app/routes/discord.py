from flask import Blueprint,  request, make_response
from app.models import DiscordApp, DiscordStreamer, Streamer, db, Game, DiscordGame
from app.constants import ApiConstant
import uuid
discord_blueprint = Blueprint('discord', __name__, url_prefix='/api/discord')

@discord_blueprint.route('/guild', methods=['POST'])
def create_guild():
    discord_app = DiscordApp()
    new_guild, errors = discord_app.insert(request.form)
    streamers = request.form.getlist('streamers')
    games = request.form.getlist('games')
    if streamers:
        for streamer_id in streamers:
            streamer = Streamer.getOne(streamer_id)
            if streamer:
                DiscordStreamer.insert(new_guild.id_public, streamer.id_public)
    if games:
        for game_id in games:
            game = Game.getOne(game_id)
            if game:
                DiscordGame.insert(new_guild.id_public, game.id_public)
    if errors:
        return make_response({'errors': errors, 'status':False}, 400)
    return {'guild_id': new_guild.id_guild}

@discord_blueprint.route('/guild/<uuid:id_guild>', methods=['GET'])
def get_guild(id_guild:uuid):
    discord_app = DiscordApp.getOne(id_guild)
    if not discord_app:
        return make_response(
            {
                'status':False, 
                'errors':{'guild_id': ApiConstant.Errors.NOT_FOUND}
            },
            ApiConstant.Http.NOT_FOUND
        )
    discord_streamers_data = {}
    discord_games_data = {}
    for discord_streamer in discord_app.discord_streamers:
        discord_streamers_data.update(discord_streamer.to_sub_resource())
    for discord_game in discord_app.discord_games:
        discord_games_data.update(discord_game.to_sub_resource())

    return {
        'guild':dict(discord_app),
        'streamers':discord_streamers_data,
        'games':discord_games_data,
        'status':True
    }

@discord_blueprint.route('/guild', methods=['GET'])
def get_guilds():
    discord_app = DiscordApp()
    filters = request.args.to_dict()
    guilds = discord_app.getAll(**filters)
    discord_streamers_data = {}
    discord_games_data = {}
    for guild in guilds:
        for discord_streamer in guild.discord_streamers:
            discord_streamers_data.update(discord_streamer.to_sub_resource())
        for discord_game in guild.discord_games:
            discord_games_data.update(discord_game.to_sub_resource())

    return make_response( {
        'guilds':[dict(guild) for guild in guilds],
        'streamers':discord_streamers_data,
        'games':discord_games_data,
        'status':True
    }, ApiConstant.Http.OK)

@discord_blueprint.route('/guild/<uuid:id_guild>', methods=['DELETE'])
def delete_guild(id_guild:uuid):
    discord_app = DiscordApp()
    discord_app = discord_app.getOne(id_guild)
    if not discord_app:
        return make_response(
            {
                'status':False, 
                'errors':{'guild_id': ApiConstant.Errors.NOT_FOUND}
            },
            ApiConstant.Http.NOT_FOUND
        )
    for discord_streamer in discord_app.discord_streamers:
        discord_streamer.delete(discord_streamer.id_public)
    for discord_game in discord_app.discord_games:
        discord_game.delete(discord_game.id_public)
    result =  discord_app.delete(id_guild)
    return make_response({'status': result}, ApiConstant.Http.OK if result else ApiConstant.Http.NOT_FOUND)

@discord_blueprint.route('/guild/<uuid:id_guild>/', methods=['PATCH'])
def update_guild(id_guild:uuid):
    discord_app = DiscordApp()
    discord_app:DiscordApp = DiscordApp().getOne(id_guild)
    if discord_app:
        discord_streamers_model = DiscordStreamer()
        current_discord_streamers = discord_app.discord_streamers
        for discord_streamer in current_discord_streamers:
            db.session.delete(discord_streamer)
            db.session.commit()
        discord_games_model = DiscordGame()
        current_discord_games = discord_app.discord_games
        for discord_game in current_discord_games:
            db.session.delete(discord_game)
            db.session.commit()

        errors = DiscordStreamer.create_api_errors()
        news_streamers = request.form.getlist('streamers')
        news_games = request.form.getlist('games')
        for streamer_id in news_streamers:
            discord_streamer, streamer_errors = discord_streamers_model.insert(discord_app.id_public,streamer_id)
            if streamer_errors:
                errors.update(streamer_errors)
        
        for game_id in news_games:
            discord_game, game_errors = discord_games_model.insert(discord_app.id_public, game_id)
            if game_errors:
                errors.update(game_errors)
        data = dict(request.form)
        new_discord_app, discord_app_errors = discord_app.update(discord_app.id_public, data)
        if discord_app_errors:
            errors.update(discord_app_errors)
        if errors:
            return {'status': False, 'errors': errors}
        return {'status': True}
    return make_response({'status': False, 'discord_app_id': ApiConstant.Errors.NOT_FOUND}, ApiConstant.Http.NOT_FOUND)
