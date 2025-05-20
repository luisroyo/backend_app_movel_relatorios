# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager # <--- Importar JWTManager
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
jwt = JWTManager() # <--- Criar instância do JWTManager

def create_app(config_class=None):
    app = Flask(__name__)

    if config_class:
        app.config.from_object(config_class)
    else:
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma_chave_secreta_muito_dificil_de_adivinhar')
        # Configuração específica para Flask-JWT-Extended
        app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY', 'outra_chave_secreta_para_jwt') # <--- Chave para JWT
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app) # <--- Inicializar JWTManager com a app

    from app.api import api_bp
    app.register_blueprint(api_bp)

    with app.app_context():
        from . import routes # Suas rotas web
        # from . import models # Geralmente não é preciso importar modelos aqui

    return app