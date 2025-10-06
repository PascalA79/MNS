from dotenv import load_dotenv
import os

load_dotenv()
DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
DISCORD_ADMIN_ID = os.getenv("DISCORD_ADMIN_ID")
LEVEL_IMAGE_FILE = os.getenv("LEVEL_IMAGE_FILE")
CREATOR_IMAGE_FILE = os.getenv("CREATOR_IMAGE_FILE")

class Config:
    @staticmethod
    def create_default_data():
        from app.models import Role, User, UserRole, DiscordUser
        role = Role()
        user = User()
        user_role = UserRole()
        discord_user = DiscordUser()
        role.insert({'name':'admin'})
        role.insert({'name':'modo'})
        role.insert({'name':'organisateur'})
        role.insert({'name':'discord owner'})
        user.insert({'pseudo':'admin', 'password':'qwerty123!'}) 

        admin = user.getAll(**{'pseudo':'admin'}).pop(0)
        admin_role = role.getAll(**{'name':'admin'}).pop(0)

        user_role.insert(admin.id_public,admin_role.id_public)
        discord_user.insert({'user_id':admin.id, 'id_discord': DISCORD_ADMIN_ID})
        
    @staticmethod
    def default(migration:bool=False) -> None:
        from app.models import Streamer, Role, User, UserRole, CheckUser, DiscordUser, DiscordApp, DiscordStreamer, Game, DiscordGame, UserStreamer
        from app.models import Event, EventLevel, Level, Player, PlayerTimer
        from app.models import Commande, CommandeGuild, CommandeGuildPermission
        from Twitch import Twitch
        from NotifDiscord import NotifDiscord
        Twitch.set_default_client(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
        NotifDiscord.set_token(DISCORD_TOKEN)
        NotifDiscord.set_public_key(DISCORD_PUBLIC_KEY)
        Level.set_level_image_file(LEVEL_IMAGE_FILE)
        Level.set_creator_image_file(CREATOR_IMAGE_FILE)
        Streamer.set_is_in_migration(migration)
        
        Streamer.set_dict_key(
            {
                'streamer_id': 'id_public',
                'pseudo': 'pseudo',
                'id_twitch': 'id_twitch',
            }
        )
        Streamer.set_sub_resource_key(
            {
                'pseudo': 'pseudo',
                'id_twitch': 'id_twitch',
            }
        )
        Role.set_dict_key(
            {
                'role_id': 'id_public',
                'name': 'name'
            }
        )
        Role.set_sub_resource_key(
            {
                'name': 'name'
            }
        )
        User.set_dict_key(
            {
                'user_id': 'id_public',
                'pseudo': 'pseudo'
            }
        )
        User.set_sub_resource_key(
            {
                'pseudo': 'pseudo'
            }
        )

        UserStreamer.set_dict_key(
            {
                'user_streamer_id': 'id_public',
                'user_id': 'user.id_public',
                'streamer_id': 'streamer.id_public'
            }
        )
        UserStreamer.set_sub_resource_key(
            {
                'user_id': 'user.id_public',
                'streamer_id': 'streamer.id_public',
                'pseudo': 'user.pseudo',
                'id_twitch': 'streamer.id_twitch',
                'pseudo_streamer': 'streamer.pseudo'
            }
        )

        UserRole.set_dict_key(
            {
                'user_role_id':'id_public',
                'user_id': 'user.id_public',
                'role_id': 'role.id_public'
            }
        )
        UserRole.set_sub_resource_key(
            {
                'user_id': 'user.id_public',
                'role_id': 'role.id_public',
                'pseudo': 'user.pseudo',
                'role_name':'role.name'
            }
        )
        CheckUser.set_dict_key(
            {
                'check_user_id':'id_public',
                'user_id': 'user.id_public',
                'code': 'code'
            }
        )
        CheckUser.set_sub_resource_key(
            {
                'pseudo': 'user.pseudo',
                'code': 'code'
            }
        )
        DiscordUser.set_dict_key(
            {
                'discord_user_id':'id_public',
                'user_id': 'user.id_public',
                'id_discord': 'id_discord'
            }
        )
        DiscordUser.set_sub_resource_key(
            {
                'pseudo': 'user.pseudo',
                'id_discord': 'id_discord'
            }
        )
        DiscordStreamer.set_dict_key(
            {
                'discord_streamer_id':'id_public',
                'app_id': 'discord_app.id_public',
                'streamer_id': 'streamer.id_public'
            }
        )
        DiscordStreamer.set_sub_resource_key(
            {
                'pseudo': 'streamer.pseudo',
                'id_twitch': 'streamer.id_twitch',
                'streamer_id': 'streamer.id_public',
                'discord_app_id': 'discord_app.id_public',
            }
        )
        DiscordApp.set_dict_key(
            {
                'discord_app_id':'id_public',
                'id_guild': 'id_guild',
                'id_channel': 'id_channel'
            }
        )
        DiscordApp.set_sub_resource_key(
            {
                'id_guild': 'id_guild',
                'id_channel': 'id_channel'
            }
        )
        Game.set_dict_key(
            {
                'game_id':'id_public',
                'id_twitch': 'id_twitch',
                'name': 'name'
            }
        )
        Game.set_sub_resource_key(
            {
                'id_twitch': 'id_twitch',
                'name': 'name'
            }
        )
        DiscordGame.set_dict_key(
            {
                'discord_game_id':'id_public',
                'app_id': 'discord_app.id_public',
                'game_id': 'game.id_public'
            }
        )
        DiscordGame.set_sub_resource_key(
            {
                'game_id': 'game.id_public',
                'discord_app_id': 'discord_app.id_public',
                'game_name': 'game.name',
            }
        )
        Event.set_dict_key(
            {
                'event_id':'id_public',
                'name': 'name',
                'description': 'description',
                'start_date': 'start_date',
                'user_id': 'user.id_public'
            }
        )
        Event.set_sub_resource_key(
            {
                'name': 'name',
                'description': 'description',
                'start_date': 'start_date',
                'user_id': 'user.id_public',
                'pseudo': 'user.pseudo'
            }
        )
        Level.set_dict_key(
            {
                'level_id':'id_public',
                'code' : 'code',
                'description': 'description',
                'name': 'name',
                'creator': 'creator',
                'thumbnail_url_level': 'level_image_path',
                'thumbnail_url_creator': 'creator_image_path'
            }
        )
        Level.set_sub_resource_key(
            {
                'code': 'code',
                'name': 'name',
                'description': 'description',
                'creator': 'creator',
                'thumbnail_url_level': 'level_image_path',
                'thumbnail_url_creator': 'creator_image_path'
            }
        )
        EventLevel.set_dict_key(
            {
                'event_level_id':'id_public',
                'event_id': 'event.id_public',
                'level_id': 'level.id_public'
            }
        )
        EventLevel.set_sub_resource_key(
            {
                'event_name': 'event.name',
                'level_code': 'level.code',
                'event_id': 'event.id_public',
                'level_id': 'level.id_public'
            }
        )
        Player.set_dict_key(
            {
                'player_id':'id_public',
                'user_id': 'user.id_public',
                'event_id': 'event.id_public'
            }
        )
        Player.set_sub_resource_key(
            {
                'pseudo': 'user.pseudo',
                'event_name': 'event.name',
                'event_id': 'event.id_public',
                'user_id': 'user.id_public'
            }
        )
        PlayerTimer.set_dict_key(
            {
                'timer_id':'id_public',
                'level_id': 'level.id_public',
                'player_id': 'player.id_public',
                'timer': 'timer'
            }
        )
        PlayerTimer.set_sub_resource_key(
            {
                'level_id': 'level.id_public',
                'level_code': 'level.code',
                'player_id': 'player.id_public',
                'timer': 'timer'
            }
        )
        Commande.set_dict_key(
            {
                'commande_id':'id_public',
                'name': 'name'
            })
        Commande.set_sub_resource_key(
            {
                'name': 'name'
            }
        )
        CommandeGuild.set_dict_key(
            {
                'command_guild_id':'id_public',
                'command_id': 'commande.id_public',
                'guild_id': 'discord_app.id_public'
            }
        )
        CommandeGuild.set_sub_resource_key(
            {
                'command_id': 'commande.id_public',
                'guild_id': 'discord_app.id_public',
                'id_guild': 'discord_app.id_guild'
            }
        )
        CommandeGuildPermission.set_dict_key(
            {
                'commande_guild_permission_id':'id_public',
                'permission': 'permission',
                'allow_permission': 'allow_permission',
                'command_guild_id': 'commande_guild.id_public'
            }
        )
        CommandeGuildPermission.set_sub_resource_key(
            {
                'command_guild_id': 'commande_guild.id_public',
                'permission': 'permission',
                'allow_permission': 'allow_permission',
            }
        )

