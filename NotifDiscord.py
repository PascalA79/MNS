from Twitch import Twitch
from app.models import Streamer, DiscordUser, User, CheckUser, DiscordStreamer, DiscordApp
from app.constants import ApiConstant
import discord
from discord.ext import commands
from datetime import datetime, timezone, timedelta
from utility import convert_to_int_if_possible
from typing import Callable

class CurrentStreamer:
    def __init__(self, streamer_data:dict) -> None:
        if not isinstance(streamer_data, dict):
            streamer_data = {}
        self.name = streamer_data.get('user_name')
        self.id_twitch = streamer_data.get('user_id')
        self.title = streamer_data.get('title')
        self.description = streamer_data.get('description')
        self.game = streamer_data.get('game_name')
        self.game_id = streamer_data.get('game_id')
        self.viewer_count = streamer_data.get('viewer_count')
        self.started_at = streamer_data.get('started_at')
        self.thumbnail_url = streamer_data.get('thumbnail_url')
        self.url = f"https://www.twitch.tv/{self.name}" if self.name else None
        self.description = streamer_data.get('description')
        self.stream_id = streamer_data.get('id')

class StreamerData:
    def __init__(self) -> None:
        # data structure
        {
            'id_streamer' : {
                'streamer' : CurrentStreamer,
                'discord':{
                    'id_discord' : {
                        'id_stream' : int,
                        'id_game' : int
                    }
                }
            }
        }
        self.__data = {}

    def update_stream_id_if_new(self, id_streamer:int, id_discord:int, id_stream:int, id_game:int)->bool:
        stream = self.__data.get(id_streamer, {}).get('discord', {}).get(id_discord, {})
        if stream.get('id_stream', None) == id_stream and stream.get('id_game', None) == id_game:
            return False
        self.set_id_stream(id_streamer, id_discord, id_stream, id_game)
        return True

    def set_id_stream(self, id_streamer:int, id_discord:int, id_stream:int, id_game:int)->None:
        self.__data[id_streamer] = self.__data.get(id_streamer, {})
        self.__data[id_streamer]['discord'] = self.__data[id_streamer].get('discord', {})
        self.__data[id_streamer]['discord'][id_discord] = self.__data[id_streamer]['discord'].get(id_discord, {})
        self.__data[id_streamer]['discord'][id_discord]['id_stream'] = id_stream
        self.__data[id_streamer]['discord'][id_discord]['id_game'] = id_game


class Message:
    streamer = {
        ApiConstant.Errors.NOT_FOUND: lambda streamer_name: f"Le streamer {streamer_name} n'existe pas",
        ApiConstant.Errors.NOT_FOUND_ON_TWITCH: lambda streamer_name: f"Le streamer {streamer_name} n'existe pas sur Twitch",
        ApiConstant.Errors.UNIQUE_CONSTRAINT_VIOLATION: lambda streamer_name: f"Le streamer {streamer_name} existe déjà",
        ApiConstant.Errors.MISSING_REQUIRED_FIELD: lambda streamer_name: f"Veuillez spécifier le nom du streamer",
        'added': lambda streamer_name: f"Le streamer {streamer_name} a été ajouté",
        'deleted': lambda streamer_name: f"Le streamer {streamer_name} a été supprimé",
        'updated': lambda streamer_name: f"Le streamer {streamer_name} a été mis à jour",
    }

class Permissions:
    def __init__(self, *roles) -> None:
        self.roles = roles

    def has_permission(self, user:User)->bool:
        return any([role in user.roles for role in self.roles])

class Function:
    def __init__(self, name:str, function:Callable, help:dict = None, *permissions:Permissions) -> None:
        if not help:
            help = {}
        self.__name = name
        self.__function = function
        self.__help = help
        self.__permissions = permissions

    def run(self, ctx:commands.Context):
        pass

class NotifDiscord:
    __token = None
    __public_key = None
    def __init__(self, token=None, public_key=None) -> None:
        self.__streamer = Streamer()
        self.__twitch = Twitch()
        self.__intents = discord.Intents.default()
        self.__intents.message_content = True
        self.__client = commands.Bot(command_prefix='!', intents=self.__intents)
        self.__token = token if token else __class__.__token
        self.__public_key = public_key if public_key else __class__.__public_key
        self.__currents_streamers = StreamerData()
        self.is_connected = False


    async def check_streamers(self):
        if not self.is_connected:
            return
        
        if not(self.__client.is_ready() and not self.__client.is_closed()):
            return
        
        streamers = self.__streamer.getAll()
        current_streamers =  self.__twitch.get_streaming_streamers([streamer.id_twitch for streamer in streamers])
        current_time = datetime.now(timezone.utc)
        for current_streamer in current_streamers:
            current_streamer = CurrentStreamer(current_streamer)
            stream_start_time = datetime.fromisoformat(current_streamer.started_at.rstrip("Z")).replace(tzinfo=timezone.utc)
            is_stream_start_at_least_1_30_minutes = (current_time - stream_start_time) >= timedelta(minutes=1, seconds=30)
            if not is_stream_start_at_least_1_30_minutes:
                continue
            streamer = DiscordStreamer.get_by_id_twitch(current_streamer.id_twitch)
            if not streamer:
                continue
            streamer_id = current_streamer.id_twitch
            stream_id = current_streamer.stream_id
            for discord_streamer in streamer:

                guild = discord_streamer.discord_app
                games_allowed = [game.game.id_twitch for game in guild.discord_games]
                if convert_to_int_if_possible(current_streamer.game_id) not in games_allowed:
                    continue
                if self.__currents_streamers.update_stream_id_if_new(streamer_id, guild.id, stream_id, current_streamer.game_id):
                    nom_échappé = current_streamer.name.replace('_', '\\_')
                    thumbnail_url = self.__twitch.get_profile_image(current_streamer.name)
                    embed = discord.Embed(title=current_streamer.title, description=current_streamer.description, color=discord.Colour.green())
                    embed.set_image(url=thumbnail_url)
                    embed.set_author(name=current_streamer.name, url=current_streamer.url)
                    embed.add_field(name="Jeu", value=current_streamer.game)
                    message = f"<@&860185805241581608>\n {nom_échappé} est présentement en direct <{current_streamer.url}>"
                    await self.send_message(guild.id_guild, guild.id_channel, embed=embed, content=message)

    @classmethod
    def set_token(cls, token):
        cls.__token = token
    @classmethod
    def set_public_key(cls, public_key):
        cls.__public_key = public_key

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


    async def add_streamer(self, ctx:commands.Context):
        info = __class__.get_info(ctx)
        if not 860052731972681740 in [role.id for role in info['author'].roles] and info['guild'].id != 860051225398214677:
            if not info['guild'].id != 860051225398214677:
                await ctx.send("Vous n'avez pas les permissions nécessaires pour effectuer cette action")
                return
        if len(info['args']) < 1:
            await ctx.send("Veuillez spécifier un nom de streamer")
            return
        streamer_name = None
        if len(info['args']) > 2:
            streamer_name = info['args'][2]

        twitch_id, streamer_name_twitch = self.__twitch.get_user_id(streamer_name)
        streamer:list[Streamer] = Streamer.getAll(**{'pseudo':f"={streamer_name_twitch}"})
        streamer = streamer.pop(0) if streamer else None
        errors = None
        if not streamer:
            streamer, errors = Streamer.insert({'id_twitch': twitch_id, 'pseudo': streamer_name_twitch})
        id_guild = info['guild'].id
        guild = DiscordApp.getAll(**{'id_guild':f"={id_guild}"})
        guild = guild.pop(0) if guild else None
        if streamer and guild:
            _, errors = DiscordStreamer.insert(guild.id_public, streamer.id_public, errors)

        if errors:
            message = ''
            if not streamer_name:
                message += f"{Message.streamer['MISSING_REQUIRED_FIELD'](streamer_name)}\n"
                pass
            if not twitch_id:
                message += f"{Message.streamer['NOT_FOUND_ON_TWITCH'](streamer_name)}\n"
            else:
                message += f"{Message.streamer[ApiConstant.Errors.UNIQUE_CONSTRAINT_VIOLATION](streamer_name)}\n"
            await ctx.send(message)
        else:
            await ctx.send(f"{Message.streamer['added'](streamer_name)}")

    async def delete_streamer(self, ctx:commands.Context):
        info = __class__.get_info(ctx)
        if not 860052731972681740 in [role.id for role in info['author'].roles] and info['guild'].id != 860051225398214677:
            return
        message = ''
        streamer_name = None
        if len(info['args']) > 2:
            streamer_name = info['args'][2]
        else:
            message+=f"{Message.streamer['MISSING_REQUIRED_FIELD'](streamer_name)}\n"
        streamer = None
        if streamer_name:
            streamer = Streamer.getAll(**{'pseudo':f"={streamer_name}"})
        streamer:Streamer = streamer[0] if streamer else None

        if streamer_name:
            if not streamer:
                message+=f"{Message.streamer[ApiConstant.Errors.NOT_FOUND](streamer_name)}\n"
            else:
                streamer = DiscordStreamer.get_by_id_twitch(streamer.id_twitch)
                if not len(streamer):
                    message+=f"{Message.streamer[ApiConstant.Errors.NOT_FOUND](streamer_name)}\n"
                else:
                    streamer = streamer[0]
                    streamer.delete(streamer.id_public)
                    message+=f"{Message.streamer['deleted'](streamer_name)}\n"

        await ctx.send(message)

    async def get_streamers(self, ctx:commands.Context)->str:
        id_discord = ctx.message.guild.id
        discord_app = DiscordApp.getAll(**{'id_guild':f"={id_discord}"})
        discord_app = discord_app.pop(0) if discord_app else None
        if not discord_app:
            return
        streamers = {}
        for streamer in discord_app.discord_streamers:
            streamers[streamer.streamer.id_twitch] = streamer.streamer
        streamer_live = self.__twitch.get_streaming_streamers([id_twitch for id_twitch, _ in streamers.items()])
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

        if not streamer_response:
            await ctx.send("Aucun streamer est enregistré")
        else:
            await ctx.send('\n'.join(streamer_response).replace('_', '\\_'))
            
    async def run(self):
        @self.__client.event
        async def on_ready():
            self.is_connected = True
            print(f'{self.__client.user} est connecté à Discord!')

        @self.__client.event
        async def on_disconnect(self):
            print(f'{self.__client.user} has disconnected from Discord.')
            self.is_connected = False
            await self.reconnect()

        async def reconnect(self):
            print('Attempting to reconnect...')
            try:
                await self.__client.close()
            except Exception as e:
                print(f'Error closing the client: {e}')
            finally:
                try:
                    await self.__client.start(self.__token)
                    print('Reconnected to Discord.')
                except Exception as e:
                    print(f'Error reconnecting: {e}')

        @self.__client.command()
        async def test(ctx: commands.Context):
            await ctx.send("Test")

        @self.__client.command()
        async def login(ctx:commands.Context):
            discord_user = DiscordUser()
            info = __class__.get_info(ctx)
            if len(info['args']) <= 1:
                await ctx.send("Veuillez spécifier votre pseudo")
                return
            if len(info['args']) <= 2:
                await ctx.send("Veuillez spécifier votre code")
                return
            pseudo = info['args'][1]
            code = info['args'][2]
            user = User.getAll(**{'pseudo':f"={pseudo}"})
            if len(user) == 0:
                await ctx.send("Utilisateur introuvable")
                return
            user = user[0]
            _, errors = CheckUser.check_code(user.id_public, code)
            if errors:
                if errors.get('user_id'):
                    await ctx.send("Vous êtes déjà vérifié")
                    return
                if errors.get('code'):
                    await ctx.send("Code incorrect")
                    return
                else:
                    await ctx.send("Erreur inconnue")
                    return
            _, errors = discord_user.insert({'user_id': user.id, 'discord_id': info['author'].id})
            await ctx.send("Vous êtes vérifié")

            ...

        @self.__client.command(name='streamer')
        async def streamer(ctx: commands.Context):
            args = ctx.message.content.split(' ')
            args.pop(0)

            fonction_name = 'get'
            if len(args) >= 1:
                fonction_name = args.pop(0)
            case = {
                'add': self.add_streamer,
                'del': self.delete_streamer,
                'get' : self.get_streamers
            }
            if fonction_name in case:
                if self.__client.is_ready() and not self.__client.is_closed():
                    await case[fonction_name](ctx)
            else:
                await ctx.send("Commande inconnue")
        await self.__client.start(self.__token)
    # fonction qui envoie un message sur discord
    async def send_message(self, guild_id, channel_id, *args, **kwargs):
        try:
            guild = self.__client.get_guild(guild_id)
            if guild is None:
                print(f"Guild with ID {guild_id} not found.")
                return
            channel = guild.get_channel(channel_id)
            if channel is None:
                print(f"Channel with ID {channel_id} not found in guild {guild.name}.")
                return
            if self.__client.is_ready() and not self.__client.is_closed():
                await channel.send(*args, **kwargs)
        except Exception as e:
            print(e)
