from flask import Blueprint,  request, make_response, render_template
from app.models import DiscordApp, DiscordStreamer, Streamer, db, Game, DiscordGame, DiscordApp, Token, DiscordOwner
from app.constants import ApiConstant
import uuid
import app as init
from discord import ChannelType
discord_blueprint = Blueprint('discord', __name__, url_prefix='/api/discord')

@discord_blueprint.route('/bot',methods=['POST'])
def create_bot():
    form = dict(request.form)
    token = request.cookies.get('token')
    registration = Token().getOne(token)
    if not registration:
        return make_response(
            {
                'errors':{
                    'user_id':ApiConstant.Errors.FORBIDDEN
                },
                'status':False
            }, ApiConstant.Http.FORBIDDEN
        )
    
    user = registration.user
    discord_name = form.get('guild_name')
    id_guild = form.get('id_guild')
    id_channel = form.get('id_channel')

    # create DiscordApp
    discord_app, errors = DiscordApp.insert({'name': discord_name, 'id_guild': id_guild, 'id_channel': id_channel})
    # create DiscordOwner
    discord_owner, errors = DiscordOwner.insert({'user_id': user.id, 'discord_app_id': discord_app.id}, errors)
    if errors:
        return make_response(
            {
                'status':False, 
                'errors': errors
            },
            ApiConstant.Http.BAD_REQUEST
        )
    
    return make_response(
        {
            'status': True,
            'owner_id': discord_owner.id_public,
            'discord_app_id': discord_app.id_public
        },
        ApiConstant.Http.CREATED
    )

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
    name_discord = {}

    for discord_streamer in discord_app.discord_streamers:
        discord_streamers_data.update(discord_streamer.to_sub_resource())
    for discord_game in discord_app.discord_games:
        discord_games_data.update(discord_game.to_sub_resource())
    discord_client = init.notif_discord.get_client()
    role_discord = {}
    channel_discord = {}
    for guild in discord_client.guilds:
        role_discord[discord_app.id_public] = {}
        channel_discord[discord_app.id_public] = {}
        for role in guild.roles:
            role_discord[discord_app.id_public][role.id] = role.name
        for channel in guild.channels:
            if channel.type == ChannelType.text:
                channel_discord[discord_app.id_public][channel.id] = channel.name
        name_discord[discord_app.id_public][guild.id] = guild.name
    return {
        'guild':dict(discord_app),
        'streamers':discord_streamers_data,
        'games':discord_games_data,
        'discord_roles': role_discord,
        'discord_names': name_discord,
        'discord_channels': channel_discord,
        'status':True
    }

@discord_blueprint.route('/guild', methods=['GET'])
def get_guilds():
    discord_app = DiscordApp()
    filters = request.args.to_dict()
    guilds = discord_app.getAll(**filters)
    discord_streamers_data = {}
    discord_games_data = {}
    name_discord = {}
    for guild in guilds:
        for discord_streamer in guild.discord_streamers:
            discord_streamers_data.update(discord_streamer.to_sub_resource())
        for discord_game in guild.discord_games:
            discord_games_data.update(discord_game.to_sub_resource())

    discord_client = init.notif_discord.get_client()
    role_discord = {}
    channel_discord = {}
    for guild in discord_client.guilds:
        guild_id_public = DiscordApp.getAll(**{'id_guild':str(guild.id)})
        if not guild_id_public:
            continue
        guild_id_public = guild_id_public[0].id_public
        role_discord[guild_id_public] = {}
        channel_discord[guild_id_public] = {}
        name_discord[guild_id_public] = {}
        for role in guild.roles:
            role_discord[guild_id_public][role.id] = role.name
        for channel in guild.channels:
            if channel.type == ChannelType.text:
                channel_discord[guild_id_public][channel.id] = channel.name
        name_discord[guild_id_public][guild.id] = guild.name

    result = {
        'guilds':[dict(guild) for guild in guilds],
        'streamers':discord_streamers_data,
        'games':discord_games_data,
        'discord_roles': role_discord,
        'discord_channels': channel_discord,
        'discord_names': name_discord,
        'status':True
    }
    return make_response( result, ApiConstant.Http.OK, {'ETag': DiscordApp.get_eTag()})

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
        discord_games_model = DiscordGame()
        current_discord_games = discord_app.discord_games
        for discord_game in current_discord_games:
            db.session.delete(discord_game)

        errors = DiscordStreamer.create_api_errors()
        news_streamers = request.form.getlist('streamers')
        news_games = request.form.getlist('games')
        for streamer_id in news_streamers:
            if streamer_id:
                discord_streamer, streamer_errors = discord_streamers_model.insert(discord_app.id_public,streamer_id)
                if streamer_errors:
                    errors.update(streamer_errors)
        
        for game_id in news_games:
            if game_id:
                discord_game, game_errors = discord_games_model.insert(discord_app.id_public, game_id)
                if game_errors:
                    errors.update(game_errors)
        data = dict(request.form)
        new_discord_app, discord_app_errors = discord_app.update(discord_app.id_public, data)
        if discord_app_errors:
            errors.update(discord_app_errors)
        if errors:
            db.session.rollback()
            return {'status': False, 'errors': errors}
        return {'status': True}
    db.session.commit()
    return make_response({'status': False, 'discord_app_id': ApiConstant.Errors.NOT_FOUND}, ApiConstant.Http.NOT_FOUND)
