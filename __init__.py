from flask import Flask
from .config import config_by_name
#from flask_login import LoginManager

#login_manager = LoginManager()

def create_app(config_name):
    # create and configure the app
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    #login_manager.init_app(app)
    return app