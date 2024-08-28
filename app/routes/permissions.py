from flask import Flask, request, send_from_directory, render_template, abort
from jinja2 import TemplateNotFound
from app.models import Token
from app.constants import ApiConstant

def get_info_user():
    token = request.cookies.get('token')
    registration = Token().getOne(token)
    info = {
        'pseudo':registration.user.pseudo if registration else '',
        'roles':[user_role.role.name for user_role in registration.user.user_roles] if registration else []
    }
    return info

def register_static(app:Flask):
    
    @app.route('/<path:filename>')
    def serve_static(filename:str):
        if not filename.startswith('scripts') and not filename.startswith('favicon.ico') and not filename.startswith('css'):
            info = get_info_user()
            try:
                if filename.startswith('admin') and not 'admin' in info['roles'] and not 'verified' in info['roles']:
                    abort(ApiConstant.Http.FORBIDDEN)

                if filename.startswith('user') and not 'verified' in info['roles']:
                    abort(ApiConstant.Http.UNAUTHORIZED)
                return render_template(filename, **info) 
            except TemplateNotFound as e:
                pass
        return send_from_directory(app.static_folder, filename)
    