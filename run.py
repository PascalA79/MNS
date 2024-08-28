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

Config.default()
app = init.create_app()
register_routes(app)

async def main():
    notif_discord = NotifDiscord()
    await asyncio.gather(
        # for development purposes
        check_streamers_periodically(notif_discord),
        notif_discord.run(),
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