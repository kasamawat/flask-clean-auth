from flask import Flask, jsonify
from config import Config
from flask_migrate import Migrate
from src.frameworks.db import db
from src.adapters.repositories.sqlalchemy_user_repo import SQLAlchemyUserRepository
from src.adapters.repositories.sqlalchemy_refresh_repo import SQLAlchemyRefreshTokenRepository
from src.utils.security_wrapper import SecurityWrapper

from src.controllers import auth_controller, user_controller

import os

def create_app(config_class=Config):
    app = Flask(__name__)
    
    @app.route("/")
    def home():
        return jsonify(message="Hello from Cloud Run!")
    
    @app.route("/version")
    def version():
        try:
            with open(".deploy_sha") as f:
                return {"version": f.read().strip()}
        except FileNotFoundError:
            return {"version": "unknown"}
    
    app.config.from_object(config_class)
    
    # connect db
    db.init_app(app)
    
    # add migrate
    migrate = Migrate(app, db)
    
    # instantiate adapters and wrappers
    with app.app_context():
        # create security wrapper
        security = SecurityWrapper(app)
        security.init_app(app) # Important: register to app.extensions
        
        # register repo
        user_repo = SQLAlchemyUserRepository()
        refresh_repo = SQLAlchemyRefreshTokenRepository()
        
        # set for auth_decorator is working
        app.extensions["user_repo"] = user_repo
        app.extensions["refresh_repo"] = refresh_repo
        app.extensions["security"] = security
        
        # inject to controllers
        auth_controller.init_app(app, user_repo=user_repo, refresh_repo=refresh_repo, security=security)
        user_controller.init_app(app, user_repo=user_repo, refresh_repo=refresh_repo, security=security)
    
    return app