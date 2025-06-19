from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
 
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
 
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['UPLOAD_FOLDER'] = 'uploads/'
    app.config['MODEL_FOLDER'] = 'models/'
    app.config['PLOTS_FOLDER'] = 'static/plots/'

    db.init_app(app)
    login_manager.init_app(app)

    from models import User
    from auth.routes import auth_bp
    from main.routes import main_bp

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)

    return app

 
# Стартиране
if __name__ == '__main__':
    app = create_app()
 
    with app.app_context():
        db.create_all()
 
app.run(debug=True)