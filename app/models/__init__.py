from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

from .ApiModel import ApiModel
from .User import User
from .Role import Role
from .UserRole import UserRole
from .Streamer import Streamer
from .Token import Token
from .CheckUser import CheckUser
from .DiscordUser import DiscordUser
from .DiscordStreamer import DiscordStreamer
from .DiscordApp import DiscordApp
from .Game import Game
from .DiscordGame import DiscordGame
from .DiscordOwner import DiscordOwner

__all__ = [
    'ApiModel',
    'bcrypt',
    'db',
    'User',
    'Role',
    'UserRole',
    'Streamer',
    'Token',
    'CheckUser',
    'DiscordUser',
    'DiscordStreamer',
    'DiscordApp',
    'Game',
    'DiscordGame',
    'DiscordOwner'
]
