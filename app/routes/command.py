from flask import Blueprint,  request, make_response, render_template
from app.models import Commande, DiscordApp, CommandeGuildPermission, CommandeGuild, db
from app.constants import ApiConstant
import uuid
import app as init
command_blueprint = Blueprint('command', __name__, url_prefix='/api/commands')

@command_blueprint.route('/', methods=['GET'])
def get_commands():
    filters = request.args.to_dict()
    commands = Commande.getAll(**filters)
    command_guilds = []
    command_guild_permissions_data = {}
    discord_names = {}
    commands_data = {}
    all_mentions = {}      

    for cmd in commands:
        commands_data.update(cmd.to_sub_resource())
        for cmd_guild in cmd.commandes_guild:
            command_guilds.append(dict(cmd_guild))
            for perm in cmd_guild.commandes_guild_permissions:
                perm_sub_resource = perm.to_sub_resource()
                perm_sub_resource[perm.id_public]['allow_permission'] = bool(perm.allow_permission)

                command_guild_permissions_data.update(perm_sub_resource)

    discord_client = init.notif_discord.get_client()
    for app_discord in discord_client.guilds:
        guild_obj = None
        for g in DiscordApp.getAll():
            if str(g.id_guild) == str(app_discord.id):
                guild_obj = g
                break
        if guild_obj:
            discord_names[guild_obj.id_public] = app_discord.name
            all_mentions[guild_obj.id_public] = {
                **{f'{user.mention}': user.name for user in app_discord.members},
                **{f'{role.mention}': f'&{role.name}' for role in app_discord.roles}
            }

    return make_response(
        {
            'commands': commands_data,
            'command_guilds': [dict(cmd_guild) for cmd_guild in command_guilds],
            'command_guild_permissions': command_guild_permissions_data,
            'discord_names': discord_names,
            'all_mentions': all_mentions
        },
        ApiConstant.Http.OK,
        {'ETag': CommandeGuildPermission.get_eTag()}
    )

@command_blueprint.route('/guild/<uuid:id_guild>', methods=['GET'])
def get_command_guild(id_guild:uuid):
    guild = DiscordApp.getOne(id_guild)
    if not guild:
        return make_response(
            {
                'status':False, 
                'errors':{'guild_id': ApiConstant.Errors.NOT_FOUND}
            },
            ApiConstant.Http.NOT_FOUND
        )
    command_guilds = []
    command_guild_permissions_data = {}
    discord_names = {}
    commands_data = {}
    all_mentions = {}

    discord_client = init.notif_discord.get_client()
    app_guild = next((g for g in discord_client.guilds if str(g.id) == str(guild.id_guild)), None)
    if app_guild:
        discord_names[guild.id_public] = app_guild.name
        all_mentions[guild.id_public] = {
            **{f'{user.mention}': user.name for user in app_guild.members},
            **{f'{role.mention}': role.name for role in app_guild.roles}
        }

    for cmd_guild in guild.commandes_guild:
        command_guilds.append(dict(cmd_guild))
        commands_data.update(cmd_guild.commande.to_sub_resource())
        for perm in cmd_guild.commandes_guild_permissions:
            # Ajout du nom du rôle ou user pour chaque permission
            perm_dict = perm.to_sub_resource()
            mention = perm.permission
            name = all_mentions.get(guild.id_public, {}).get(mention, None)
            perm_dict['name'] = name
            perm_sub_resource = perm.to_sub_resource()
            perm_sub_resource[perm.id_public]['allow_permission'] = bool(perm.allow_permission)

            command_guild_permissions_data.update(perm_sub_resource)

    return make_response(
        {
            'command_guilds': command_guilds,
            'command_guild_permissions': command_guild_permissions_data,
            'discord_names': discord_names,
            'all_mentions': all_mentions,
            'commands': commands_data
        },
        ApiConstant.Http.OK,
        {'ETag': CommandeGuildPermission.get_eTag()}
    )
@command_blueprint.route('/<uuid:id_command_guild>/', methods=['PATCH'])
def update_commands(id_command_guild: uuid):
    command_guild = CommandeGuild.getOne(id_command_guild)
    if not command_guild:
        return make_response(
            {
                'status': False,
                'errors': {'command_guild_id': ApiConstant.Errors.NOT_FOUND}
            },
            ApiConstant.Http.NOT_FOUND
        )
    allow_permissions = request.form.getlist('allow_permissions')
    deny_permissions = request.form.getlist('deny_permissions')

    allow_permissions_exist = bool(request.form.get('allow_permissions'))
    deny_permissions_exist = bool(request.form.get('deny_permissions'))

    CommandeGuildPermission.delete_where(**{'id_commandes_guild': command_guild.id})
    error = None
    if allow_permissions_exist:
        for allow_permission in allow_permissions:
            _, error = CommandeGuildPermission.insert(
                {
                    'id_commandes_guild': command_guild.id,
                    'permission': allow_permission,
                    'allow_permission': True
                }
            )
    if deny_permissions_exist:
        for deny_permission in deny_permissions:
            _, error = CommandeGuildPermission.insert(
                {
                    'id_commandes_guild': command_guild.id,
                    'permission': deny_permission,
                    'allow_permission': False
                }
            )

    if error:
        return make_response(
            {
                'status': False,
                'errors': {'command_guild_permission': error}
            },
            ApiConstant.Http.BAD_REQUEST
        )

    return make_response(
        {
            'status': True
        },
        ApiConstant.Http.OK,
        {'ETag': CommandeGuildPermission.get_eTag()}
    )

@command_blueprint.route('/', methods=['HEAD'])
def headCommandes():
    return make_response('', ApiConstant.Http.OK, {'ETag': CommandeGuildPermission.get_eTag()})

@command_blueprint.route('/guild/<uuid:id_guild>', methods=['HEAD'])
def headCommandsGuild(id_guild: uuid):
    return make_response('', ApiConstant.Http.OK, {'ETag': CommandeGuildPermission.get_eTag(id_guild)})
