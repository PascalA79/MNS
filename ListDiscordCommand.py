from app.models import Streamer, DiscordUser, User, CheckUser, DiscordStreamer, DiscordApp
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
                    message+=f"{Message.streamer[ApiConstant.Errors.NOT_FOUND](pseudo)}\n"
                else:
                    streamer = streamer[0]
                    streamer.delete(streamer.id_public)
                    message+=f"{Message.streamer['deleted'](pseudo)}\n"
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
