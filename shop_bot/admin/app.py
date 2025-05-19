from flask import Flask, request, redirect, url_for
from flask_login import LoginManager, current_user
from sqlalchemy import select
import sys
import os

from config_flask import config

abs_path = os.path.abspath('.')
if abs_path not in sys.path:
    sys.path.insert(0, abs_path)

from logging_config import setup_logging
setup_logging()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    from admin.routes import routes_bp
    app.register_blueprint(routes_bp)

    login_manager = LoginManager()
    login_manager.login_view = 'admin.login'
    login_manager.init_app(app)

    from db.init import sync_session
    from db.models import Admin

    @login_manager.user_loader
    def load_admin(admin_id):
        with sync_session() as session:
            admin = session.scalar(select(Admin).where(Admin.id==admin_id))
        return admin

    return app

app = create_app('dev')

@app.before_request
def require_login():
    public_endpoints = [
        'admin.login',
        'static',
    ]

    if current_user.is_authenticated and current_user.is_active:
        return

    if request.endpoint in public_endpoints:
        return

    return redirect(url_for('admin.login'))

if __name__ == '__main__':
    app.run(debug=True)
