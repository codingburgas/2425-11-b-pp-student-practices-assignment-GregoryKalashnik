from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app.models import User
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    from app.routes import main, auth
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    
    return app
