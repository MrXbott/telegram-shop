from flask import Flask
from .config_flask import config

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    from admin.routes import routes_bp
    app.register_blueprint(routes_bp)

    return app
