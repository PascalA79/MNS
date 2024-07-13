from config import Config
from flask import Flask
from NotifDiscord import NotifDiscord
import asyncio
# link: https://discord.com/oauth2/authorize?client_id=1251916526122959040&permissions=67584&integration_type=0&scope=bot
app = Flask(__name__)
Config.default()
async def check_notif(notif:NotifDiscord):
    while True:
        await asyncio.sleep(5)
        if notif:
            ...
            # await notif.send_message('tester', 477079662913126412)
async def main():
    notif_discord = NotifDiscord()
    await asyncio.gather(
        notif_discord.run(),
        check_notif(notif_discord)
    )
with app.app_context():
    asyncio.run(main())
app.run()