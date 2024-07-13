from flask import Blueprint,  render_template, request
from app.models import DiscordApp, Token, DiscordOwner

bot_blueprint = Blueprint('bot', __name__, url_prefix='/')
@bot_blueprint.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@bot_blueprint.route('/',methods=['POST'])
def create_bot():
    form = dict(request.form)
    token = request.cookies.get('token')
    registration = Token().getOne(token)
    if not registration:
        return
    user = registration.user
    name = form.get('guild_name')
    id_guild = form.get('id_guild')
    id_channel = form.get('id_channel')

    # create DiscordApp
    discord_app = DiscordApp.insert({'name': name, 'id_guild': id_guild, 'id_channel': id_channel})
    # create DiscordOwner
    discord_owner = DiscordOwner.insert({'user_id': user.id, 'discord_app_id': discord_app.id})


