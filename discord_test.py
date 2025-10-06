from config import Config
from flask import Flask
import asyncio
from app import create_app 
import app as init
from config import Config
from NotifDiscord import NotifDiscord
from discord import ChannelType
from time import time
# link: https://discord.com/oauth2/authorize?client_id=1251916526122959040&permissions=67584&integration_type=0&scope=bot
Config.default()
app = create_app()
Config.default()

async def test(notif: NotifDiscord):
    while True:
        client = notif.get_client()
        for guild in client.guilds:
            print('-'*20)
            print(guild.name)
            for channel in guild.channels:
                if channel.type == ChannelType.text:
                    padded_name = channel.name.ljust(40)
                    print(padded_name, channel.id)
            print('+'*20)
            for role in guild.roles:
                padded_name = role.name.ljust(40)
                print(padded_name, role.id)
            print('-'*20)
        await asyncio.sleep(5)
async def main():
    await asyncio.gather(
        init.notif_discord.run(),
        test(init.notif_discord)
    )
with app.app_context():
    asyncio.run(main())
app.run()