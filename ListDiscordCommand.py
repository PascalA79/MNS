from app.models import Streamer, DiscordStreamer, DiscordApp, Commande, CommandeGuild, CommandeGuildPermission
from DiscordCommand import Message
from typing import Callable
from discord.ext import commands
from Twitch import Twitch
from app.constants import ApiConstant
from CurrentStreamer import CurrentStreamer

class ListDiscordCommand:
    @staticmethod
    def get_info(ctx:commands.Context)->dict:
        args = ctx.message.content.split(' ')
        args.pop(0)
        info = {
            'author': ctx.message.author,
            'channel': ctx.message.channel,
            'guild': ctx.message.guild,
            'content': ctx.message.content,
            'args': tuple(ctx.message.content.split(' ')),
        }
        return info
    
    @classmethod
    def add_streamer(cls)->Callable[[commands.Context, list[str]], str]:
        def add_streamers(ctx:commands.Context, pseudos:list[str])->str:
            message:list[str] = []
            twitch = Twitch()
            info = __class__.get_info(ctx)
            for pseudo in pseudos:
                twitch_id, streamer_name_twitch = twitch.get_user_id(pseudo)
                if not twitch_id:
                    message.append(Message.streamer[ApiConstant.Errors.NOT_FOUND_ON_TWITCH](pseudo))
                    continue
                streamer:list[Streamer] = Streamer.getAll(**{'pseudo':f"{streamer_name_twitch}"})
                streamer = streamer.pop(0) if streamer else None
                errors = None
                if not streamer:
                    streamer, errors = Streamer.insert({'id_twitch': twitch_id, 'pseudo': streamer_name_twitch})
                id_guild = info['guild'].id
                guild = DiscordApp.getAll(**{'id_guild':f"{id_guild}"})
                guild = guild.pop(0) if guild else None
                if streamer and guild:
                    new_streamer, errors = DiscordStreamer.insert(guild.id_public, streamer.id_public, errors)
                    if new_streamer:
                        message.append(Message.streamer['added'](new_streamer.streamer.pseudo))
                    else:
                        message.append(Message.streamer[ApiConstant.Errors.UNIQUE_CONSTRAINT_VIOLATION](pseudo))
            return '\n'.join(message)
            
        return add_streamers
    
    @classmethod
    def delete_streamer(cls)->Callable[[commands.Context, list[str]], str]:
        def delete_streamers(ctx:commands.Context, pseudos:list[str])->str:
            message:list[str] = []
            streamer = Streamer()
            for pseudo in pseudos:
                streamer:list[Streamer] = Streamer.getAll(**{'pseudo':f"{pseudo}"})
                streamer = streamer.pop(0) if streamer else None
                streamer = DiscordStreamer.get_by_id_twitch(streamer.id_twitch)
                if not len(streamer):
                    message.append(f"{Message.streamer[ApiConstant.Errors.NOT_FOUND](pseudo)}\n")
                else:
                    streamer = streamer[0]
                    streamer.delete(streamer.id_public)
                    message.append(f"{Message.streamer['deleted'](pseudo)}\n")
            return '\n'.join(message)
        return delete_streamers
    
    @classmethod
    def get_streamer(cls)->Callable[[commands.Context], str]:
        def get_streamers(ctx:commands.Context)->str:
            twitch = Twitch()
            id_discord = ctx.message.guild.id
            discord_app = DiscordApp.getAll(**{'id_guild':f"{id_discord}"})
            discord_app = discord_app.pop(0) if discord_app else None
            if not discord_app:
                return
            streamers = {}
            for streamer in discord_app.discord_streamers:
                streamers[streamer.streamer.id_twitch] = streamer.streamer
            streamer_live = twitch.get_streaming_streamers([id_twitch for id_twitch, _ in streamers.items()])
            streamer_dict = {}
            for streamer_data in streamer_live:
                streamer_dict[streamer_data['user_name']] = CurrentStreamer(streamer_data)

            streamer_response = []
            games_allowed = [game.game.id_twitch for game in discord_app.discord_games]
            for id_twitch, streamer in streamers.items():
                pseudo = streamer.pseudo
                if pseudo in streamer_dict.keys() and int(streamer_dict.get(pseudo, {}).game_id) in games_allowed:
                    streamer_response.append(f"{pseudo} est en ligne et joue à {streamer_dict.get(pseudo, {}).game}")
                else:
                    streamer_response.append(f"{pseudo} est hors ligne")
            return '\n'.join(streamer_response)
        return get_streamers
    @classmethod
    def test(cls)->Callable[[commands.Context], str]:
        async def test(ctx:commands.Context)->str:
            info = __class__.get_info(ctx)
            guild = info['guild']
            members = []
            async for member in guild.fetch_members(limit=None):
                if not member.bot:
                    members.append(member)
            return '\n'.join([f"{member.name} {member.id}" for member in members])

        return test
    @classmethod
    def add_permission(cls)->Callable[[commands.Context, str, list[str]], str]:
        def add_permission(ctx:commands.Context, command_name:str, mentions:list[str])->str:
            info = __class__.get_info(ctx)
            guild = info['guild']
            guild.owner.mention == ctx.message.author.mention
            if guild.owner.mention != ctx.message.author.mention:
                return Message.command[ApiConstant.Errors.FORBIDDEN](__class__.add_permission.__name__)
            
            message:list[str] = []
            command_name = command_name.strip().lower().replace('_', ' ')
            command = Commande.getAll(**{'name':f"{command_name}"})
            command = command.pop(0) if command else None
            guild = DiscordApp.getAll(**{'id_guild':f"{guild.id}"})
            guild = guild.pop(0) if guild else None
            if not command or not guild:
                raise Exception(f"Commande ou guild non trouvée")
            for i, mention in enumerate(mentions):
                if mention == '@everyone':
                    mentions[i] = info['guild'].default_role.mention
            commandes_guild = CommandeGuild.getAll(**{'id_commande':command.id, 'id_guild':guild.id})
            commandes_guild = commandes_guild.pop(0) if commandes_guild else None
            if not commandes_guild:
                raise Exception(f"Commandes guild non trouvée")
            for mention in mentions:
                CommandeGuildPermission.delete_where(**{
                    'id_commandes_guild':commandes_guild.id,
                    'permission':mention,
                })
                CommandeGuildPermission.insert({
                    'id_commandes_guild': commandes_guild.id,
                    'permission': mention,
                    'allow_permission': True
                })
                message.append(f"Autorisation de la commande `{command_name}` pour {mention}")
            return '\n'.join(message)
        return add_permission
    
    @classmethod
    def remove_permission(cls)->Callable[[commands.Context, str, list[str]], str]:
        def remove_permission(ctx:commands.Context, command_name:str, mentions:list[str])->str:
            info = __class__.get_info(ctx)
            guild = info['guild']
            guild.owner.mention == ctx.message.author.mention
            if guild.owner.mention != ctx.message.author.mention:
                return Message.command[ApiConstant.Errors.FORBIDDEN](__class__.remove_permission.__name__)

            message:list[str] = []
            command_name = command_name.strip().lower().replace('_', ' ')
            command = Commande.getAll(**{'name':f"{command_name}"})
            command = command.pop(0) if command else None
            guild = DiscordApp.getAll(**{'id_guild':f"{guild.id}"})
            guild = guild.pop(0) if guild else None
            if not command or not guild:
                raise Exception(f"Commande ou guild non trouvée")
            for i, mention in enumerate(mentions):
                if mention == '@everyone':
                    mentions[i] = info['guild'].default_role.mention
            commandes_guild = CommandeGuild.getAll(**{'id_commande':command.id, 'id_guild':guild.id})
            commandes_guild = commandes_guild.pop(0) if commandes_guild else None
            if not commandes_guild:
                raise Exception(f"Commandes guild non trouvée")
            for mention in mentions:
                CommandeGuildPermission.delete_where(**{
                    'id_commandes_guild':commandes_guild.id,
                    'permission':mention,
                })
                message.append(f"Interdiction de la commande `{command_name}` pour {mention}")
            return '\n'.join(message)
        return remove_permission
    
    @classmethod
    def reset_permission(cls)->Callable[[commands.Context, str, list[str]], str]:
        def reset_permission(ctx:commands.Context, command_name:str, mentions:list[str])->str:
            info = __class__.get_info(ctx)
            guild = info['guild']
            guild.owner.mention == ctx.message.author.mention
            if guild.owner.mention != ctx.message.author.mention:
                return Message.command[ApiConstant.Errors.FORBIDDEN](__class__.reset_permission.__name__)
            
            message:list[str] = []
            command_name = command_name.strip().lower().replace('_', ' ')
            command = Commande.getAll(**{'name':f"{command_name}"})
            command = command.pop(0) if command else None
            guild = DiscordApp.getAll(**{'id_guild':f"{guild.id}"})
            guild = guild.pop(0) if guild else None
            if not command or not guild:
                raise Exception(f"Commande ou guild non trouvée")
            for i, mention in enumerate(mentions):
                if mention == '@everyone':
                    mentions[i] = info['guild'].default_role.mention
            commandes_guild = CommandeGuild.getAll(**{'id_commande':command.id, 'id_guild':guild.id})
            commandes_guild = commandes_guild.pop(0) if commandes_guild else None
            if not commandes_guild:
                raise Exception(f"Commandes guild non trouvée")
            for mention in mentions:
                CommandeGuildPermission.delete_where(**{
                    'id_commandes_guild':commandes_guild.id,
                    'permission':mention,
                })
                message.append(f"Réinitialisation des permissions pour la commande `{command_name}` pour {mention}")
            return '\n'.join(message)
        return reset_permission
    
    @classmethod
    def get_permission(cls)->Callable[[commands.Context, str], str]:
        def get_permission(ctx:commands.Context, command_name:str)->str:
            info = __class__.get_info(ctx)
            guild = info['guild']
            guild.owner.mention == ctx.message.author.mention
            if guild.owner.mention != ctx.message.author.mention:
                return Message.command[ApiConstant.Errors.FORBIDDEN](__class__.get_permission.__name__)

            command_name = command_name.strip().lower().replace('_', ' ')
            command = Commande.getAll(**{'name':f"{command_name}"})
            command = command.pop(0) if command else None
            guild = DiscordApp.getAll(**{'id_guild':f"{guild.id}"})
            guild = guild.pop(0) if guild else None
            if not command or not guild:
                raise Exception(f"Commande ou guild non trouvée")
            return command
        return get_permission

    @classmethod
    def permission(cls)->Callable[[commands.Context, str, str, list[str]], str]:
        def permission(ctx:commands.Context, permission:str, command_name:str, mentions:list[str])->str:
            info = __class__.get_info(ctx)
            guild = info['guild']
            guild.owner.mention == ctx.message.author.mention
            if guild.owner.mention != ctx.message.author.mention:
                return Message.command[ApiConstant.Errors.FORBIDDEN](__class__.allow.__name__)
            
            message:list[str] = []
            command_name = command_name.strip().lower().replace('_', ' ')
            command = Commande.getAll(**{'name':f"{command_name}"})
            command = command.pop(0) if command else None
            guild = DiscordApp.getAll(**{'id_guild':f"{guild.id}"})
            guild = guild.pop(0) if guild else None
            if not command or not guild:
                raise Exception(f"Commande ou guild non trouvée")
            for i, mention in enumerate(mentions):
                if mention == '@everyone':
                    mentions[i] = info['guild'].default_role.mention
            commandes_guild = CommandeGuild.getAll(**{'id_commande':command.id, 'id_guild':guild.id})
            commandes_guild = commandes_guild.pop(0) if commandes_guild else None
            if not commandes_guild:
                raise Exception(f"Commandes guild non trouvée")
            if permission != 'get':
                for mention in mentions:
                    CommandeGuildPermission.delete_where(**{
                        'id_commandes_guild':commandes_guild.id,
                        'permission':mention,
                    })
                    if permission != 'reset':
                        is_allowed = True if permission.lower() == 'allow' else False
                        CommandeGuildPermission.insert({
                            'id_commandes_guild': commandes_guild.id,
                            'permission': mention,
                            'allow_permission': is_allowed
                        })
                        message.append(f"{'Autorisation' if is_allowed else 'Interdiction'} de la commande `{command_name}` pour les mentions suivantes :")
                        for mention in mentions:
                            message.append(f" - {mention}")
                        return '\n'.join(message)
                    else:
                        CommandeGuildPermission.delete_where(**{
                            'id_commandes_guild':commandes_guild.id,
                        })
                        message.append(f"Réinitialisation des permissions pour la commande `{command_name}`")

            else:
                mention_allowed = []
                mention_denyed = []
                permissions = CommandeGuildPermission.getAll(**{
                    'id_commandes_guild': commandes_guild.id,
                })
                if not permissions:
                    return f"Aucune permission définie pour la commande `{command_name}`"
                for local_permission in permissions:
                    is_allowed = local_permission.allow_permission
                    if is_allowed:
                        mention_allowed.append(local_permission.permission)
                    else:
                        mention_denyed.append(local_permission.permission)

                message.append(f"Autorisation de la commande `{command_name}` pour la mention {', '.join(mention_allowed)}" if mention_allowed else "")
                message.append(f"Interdiction de la commande `{command_name}` pour la mention {', '.join(mention_denyed)}" if mention_denyed else "")
            return '\n'.join(message)
        return permission
