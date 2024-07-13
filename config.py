from dotenv import load_dotenv
import os

load_dotenv()
DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
DISCORD_ADMIN_ID = os.getenv("DISCORD_ADMIN_ID")

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
        role.insert({'name':'verified'})
        role.insert({'name':'sudo'})
        role.insert({'name':'owner'})
        user.insert({'pseudo':'admin', 'password':'qwerty123!'})

        admin = user.getAll(**{'pseudo':'=admin'}).pop(0)
        admin_role = role.getAll(**{'name':'=admin'}).pop(0)
        verified_role = role.getAll(**{'name':'=verified'}).pop(0)

        user_role.insert(admin.id_public,admin_role.id_public)
        user_role.insert(admin.id_public,verified_role.id_public)
        discord_user.insert({'user_id':admin.id, 'discord_id': DISCORD_ADMIN_ID})
        
    @staticmethod
    def default() -> None:
        from app.models import Streamer, Role, User, UserRole, CheckUser, DiscordUser, DiscordApp, DiscordStreamer, Game, DiscordGame
        from Twitch import Twitch
        from NotifDiscord import NotifDiscord
        Twitch.set_default_client(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)
        NotifDiscord.set_token(DISCORD_TOKEN)
        NotifDiscord.set_public_key(DISCORD_PUBLIC_KEY)
        
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
        UserRole.set_dict_key(
            {
                'user_role_id':'id_public',
                'user_id': 'user.id_public',
                'role_id': 'role.id_public'
            }
        )
        UserRole.set_sub_resource_key(
            {
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
                'discord_id': 'discord_id'
            }
        )
        DiscordUser.set_sub_resource_key(
            {
                'pseudo': 'user.pseudo',
                'discord_id': 'discord_id'
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
                'discord_app_name': 'discord_app.name',
            }
        )
        DiscordApp.set_dict_key(
            {
                'discord_app_id':'id_public',
                'name': 'name',
                'id_guild': 'id_guild',
                'id_channel': 'id_channel'
            }
        )
        DiscordApp.set_sub_resource_key(
            {
                'name': 'name',
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
                'discord_app_name': 'discord_app.name',
                'game_name': 'game.name',
            }
        )

