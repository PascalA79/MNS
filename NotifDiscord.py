from Twitch import Twitch
from app.models import Streamer, User, DiscordStreamer, DiscordApp, Role, UserRole, Commande, CommandeGuild, CommandeGuildPermission
from app.constants import ApiConstant
import discord
from discord.ext import commands
from datetime import datetime, timezone, timedelta
from utility import convert_to_int_if_possible
from DiscordCommand import Command, CommandKarg, Message
from ListDiscordCommand import ListDiscordCommand
from CurrentStreamer import CurrentStreamer
import json
import random
import string

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

class NotifDiscord:
    __token = None
    __public_key = None
    def __init__(self, token=None, public_key=None) -> None:
        self.__streamer = Streamer()
        self.__twitch = Twitch()
        self.__intents = discord.Intents.default()
        self.__intents.members = True
        self.__intents.message_content = True
        self.__client = commands.Bot(command_prefix='!', intents=self.__intents)
        self.__token = token if token else __class__.__token
        self.__public_key = public_key if public_key else __class__.__public_key
        self.__currents_streamers = StreamerData()
        self.is_connected = False

    def get_client(self):
        return self.__client

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
                    current_streamer.name = current_streamer.name.replace('_', '\\_')
                    current_streamer.thumbnail_url = self.__twitch.get_profile_image(current_streamer.name)
                    embed = discord.Embed(title=current_streamer.title, description=current_streamer.description, color=discord.Colour.green())
                    embed.set_image(url=current_streamer.thumbnail_url)
                    embed.set_author(name=current_streamer.name, url=current_streamer.url)
                    embed.add_field(name="Jeu", value=current_streamer.game)
                    message = f"<@&860185805241581608>\n {current_streamer.name} est présentement en direct <{current_streamer.url}>"
                    await self.send_message(guild.id_guild, guild.id_channel, embed=embed, content=message)

    
    def parse_current_streamer(self, current_streamer:CurrentStreamer, text:str)->dict:
        """
        Replaces placeholders in the given text with the corresponding attributes of the current streamer.

        Args:
            current_streamer (CurrentStreamer): The current streamer object containing streamer details.
            text (str): The text containing placeholders to be replaced.

        Returns:
            dict: The text with placeholders replaced by the current streamer's attributes.

        Example:
            current_streamer = CurrentStreamer({
                'name': 'StreamerName',
                'title': 'Stream Title',
                'description': 'Stream Description',
                'game': 'Game Name',
                'viewer_count': '100',
                'started_at': '2023-10-10T10:00:00Z',
                'thumbnail_url': 'http://example.com/thumbnail.jpg',
                'url': 'http://twitch.tv/StreamerName'
            })
            text = "Watch {name} playing {game} at {url}"
            result = parse_current_streamer(current_streamer, text)
            # result: "Watch StreamerName playing Game Name at http://twitch.tv/StreamerName"
        """
        text = text.replace('{name}', current_streamer.name)
        text = text.replace('{title}', current_streamer.title)
        text = text.replace('{description}', current_streamer.description)
        text = text.replace('{game}', current_streamer.game)
        text = text.replace('{viewer_count}', current_streamer.viewer_count)
        text = text.replace('{started_at}', current_streamer.started_at)
        text = text.replace('{thumbnail_url}', current_streamer.thumbnail_url)
        text = text.replace('{url}', current_streamer.url)
        return text

    def create_message_notif(self, guild:DiscordApp, current_streamer:CurrentStreamer, notif_role_list:list[str], message:str, embed_parameter:str)->str:
        embed_param = json.loads(self.parse_current_streamer(current_streamer,embed_parameter))
        if 'color' in embed_param:
            embed_parameter['color'] = discord.Colour.to_rgb(embed_param['color'])
        embed = discord.Embed(**embed_param)
        
        message = self.parse_current_streamer(current_streamer, message)
        message = f"{' '.join(notif_role_list)}\n{message}"
        return self.send_message(guild.id_guild, guild.id_channel, embed=embed, content=message)

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

        @self.__client.event
        async def on_join(self, guild):
            # celui qui a invité le bot

            owner_id = guild.owner_id
            owner = await guild.fetch_member(owner_id)
            user_name = owner.name
            discord_app = DiscordApp.insert({'id_guild':guild.id})
            discord_owner_role = Role.getAll(**{'name':'discord owner'})
            discord_owner_role = discord_owner_role.pop(0)
            host_user = User.insert({'pseudo':owner.name, 'password':password})
            UserRole.insert({'user_id':host_user.id_public, 'role_id':discord_owner_role.id_public})

            password = ''.join([random.choice(string.ascii_letters + string.digits + string.digits + string.punctuation) for i in range(12)])
            await owner.send(f"Bonjour {owner.name},\n" + 
                            f"Vous pouvez vous connecter au site <http://pascala79.ca/login.html>\n" +
                            f"Voici vos identifiants:\n" +
                            f"Nom d'utilisateur: {user_name}\nMot de passe: {password}\n" +
                            f"Pour des raisons de sécurité, nous vous conseillons de changer votre mot de passe dès votre première connexion.")
            

        @self.__client.event
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

        streamer_commands = Command('streamer', 'Commande pour gérer les streamers', None)
        add_streamer_command = Command('add', 'Ajoute un streamer avec son pseudo Twitch', ListDiscordCommand.add_streamer(), [CommandKarg('pseudos', True)])
        delete_streamer_command = Command('del', 'Supprime un streamer avec son pseudo Twitch', ListDiscordCommand.delete_streamer(), [CommandKarg('pseudos', True)])
        get_streamer_command = Command('get', 'Récupère les streamers en ligne', ListDiscordCommand.get_streamer())
        # test_command = Command('test', 'Test command', ListDiscordCommand.test())
        streamer_commands.add_command(add_streamer_command)
        streamer_commands.add_command(delete_streamer_command)
        streamer_commands.add_command(get_streamer_command)
        # test_command.add(self.__client)
        streamer_commands.add(self.__client)
        
        all_current_commandes = Commande.getAll()
        all_current_commandes = {commande for commande in all_current_commandes}
        all_commandes = list(self.__client.all_commands.keys())
        commands_to_delete = []
        for current_command in all_current_commandes:
            if current_command.name not in all_commandes:
                commands_to_delete.append(current_command)

        # Supprimer les commandes qui ne sont plus dans le client
        for command_to_delete in commands_to_delete:
            commandes_guild = command_to_delete.commandes_guild 
            for commande_guild in commandes_guild:
                pass
                CommandeGuildPermission.delete_where(**{'id_commandes_guild':commande_guild.id})
                CommandeGuild.delete_where(**{'id_commande':commande_guild.id})
            Commande.delete_where(**{'id_public':command_to_delete.id_public})

        # Ajouter les commandes qui sont dans le client mais pas dans la base de données
        for command_name in all_commandes:
            if command_name not in all_current_commandes:
                Commande.insert({'name': command_name})

        # Ajouter les commande de permission aux commandes
        permission_command = Command(
            'permission', 
            'Gère les permissions des commandes, la commande en snake_case.', 
            ListDiscordCommand.permission(), 
            [
                CommandKarg('permission', True, lambda value: value.lower() in ['allow', 'deny', 'reset', 'get']), 
                CommandKarg('command_name', True,  lambda value: value.strip().lower().replace('_', ' ') in [command.name for command in all_current_commandes]),
                CommandKarg('mentions', False , lambda value: value.startswith('<@') and value.endswith('>') and len(value) > 2 and value[2:-1].isdigit() or value.startswith('<@&') and value.endswith('>') and len(value) > 3 and value[3:-1].isdigit() or value == '@everyone') # valide les mentions de discord
            ]
            , {
                'mentions' : lambda command: not command['permission'] in ['reset', 'get'] # command.args.get('permission', None) == 'get' else True
            }
        )
        permission_command.add(self.__client)

        all_discord_apps = DiscordApp.getAll()
        all_commandes = Commande.getAll()
        for discord_app in all_discord_apps:
            for commande in all_commandes:
                CommandeGuild.insert({'id_guild': discord_app.id, 'id_commande': commande.id})

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
