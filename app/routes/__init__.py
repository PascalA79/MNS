from flask import Flask, jsonify, make_response, request, redirect
from app.constants import ApiConstant

from .streamer import streamer_blueprint
from .user import user_blueprint
from .role import role_blueprint
from .user_role import user_role_blueprint
from .token import token_blueprint
from .permissions import register_static, get_info_user
from .discord import discord_blueprint
from .game import game_blueprint

from dotenv import load_dotenv
import os

load_dotenv()

def register_routes(app: Flask):

    @app.errorhandler(ApiConstant.Http.UNAUTHORIZED)
    def unauthorized_error(error):
        response = jsonify({"status": False, "errors": ApiConstant.Errors.UNAUTHORIZED})
        return make_response(response, ApiConstant.Http.UNAUTHORIZED)

    @app.errorhandler(ApiConstant.Http.FORBIDDEN)
    def forbidden_error(error):
        response = jsonify({"status": False, "errors": ApiConstant.Errors.FORBIDDEN})
        return make_response(response, ApiConstant.Http.FORBIDDEN)

    @app.errorhandler(ApiConstant.Http.NOT_FOUND)
    def not_found_error(error):
        response = jsonify({"status": False, "errors": ApiConstant.Errors.NOT_FOUND})
        return make_response(response, ApiConstant.Http.NOT_FOUND)
    
    # Pour d'autres types d'erreurs personnalisées
    @app.errorhandler(ApiConstant.Http.INTERNAL_SERVER_ERROR)
    def custom_error(error):
        response = jsonify({"status": False, "errors": str(error)})
        return make_response(response, ApiConstant.Http.INTERNAL_SERVER_ERROR)
    
    @app.route('/')
    def index():
        info = get_info_user()
        roles = info['roles']
        url_redirect = '/index.html'
        if 'verified' in roles:
            url_redirect = '/user/index.html'
        return redirect(url_redirect)

    app.register_blueprint(streamer_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(role_blueprint)
    app.register_blueprint(user_role_blueprint)
    app.register_blueprint(token_blueprint)
    app.register_blueprint(discord_blueprint)
    app.register_blueprint(game_blueprint)
    register_static(app)
