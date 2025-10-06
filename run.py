from app.models import *
from config import Config
import app as init
from app.routes import register_routes
from NotifDiscord import NotifDiscord
import asyncio
from threading import Thread

async def check_streamers_periodically(notif_discord:NotifDiscord):
    with app.app_context():
        while True:
            await notif_discord.check_streamers()
            await asyncio.sleep(30)

async def clean_token_periodically():
    with app.app_context():
        while True:
            Token.delete_expired_tokens()
            await asyncio.sleep(60*5)

Config.default()
app = init.create_app()
register_routes(app)

async def main():
    await asyncio.gather(
        check_streamers_periodically(init.notif_discord),
        clean_token_periodically(),
        init.notif_discord.run(),
    )

def run_asyncio_loop():
    with app.app_context():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
        loop.close()

with app.app_context():
    db.create_all()
    Config.create_default_data()
thread = Thread(target=run_asyncio_loop)
thread.start()

app.run(host='0.0.0.0', port=3000,debug=False)