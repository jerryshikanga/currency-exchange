import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy(session_options={"autoflush": False})


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # api keys and other stuff required by libs or external apis
    app.config['FIXER_SECRET_KEY'] = os.environ.get('FIXER_SECRET_KEY')

    db.init_app(app)

    # flask login session tracking
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from currencyexchange.database.auth import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table,
        # use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from currencyexchange.views.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for currency exchange routes in our app
    from currencyexchange.views.fxrates import fxrates as fxrates_blueprint
    app.register_blueprint(fxrates_blueprint)

    # blueprint for non-auth parts of app
    from currencyexchange.views.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
