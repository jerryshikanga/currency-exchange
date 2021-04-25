import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy(session_options={"autoflush": False})


def get_secret_key():
    if os.environ.get('SECRET_KEY'):
        return os.environ.get('SECRET_KEY')
    else:
        import hashlib
        import datetime
        s = str(datetime.datetime.now())
        return hashlib.md5(s.encode()).hexdigest()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = get_secret_key()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # api keys and other stuff required by libs or external apis
    app.config['FIXER_SECRET_KEY'] = os.environ.get('FIXER_SECRET_KEY')

    # instructions here https://flask-migrate.readthedocs.io/en/latest/
    db.init_app(app)
    Migrate(app, db)

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

    # set up logging to std console using gunicorn
    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(logging.WARNING)

    # register blue prints
    # blueprint for auth routes in our app
    from currencyexchange.views.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for currency exchange routes in our app
    from currencyexchange.views.fxrates import fxrates as fxrates_blueprint
    app.register_blueprint(fxrates_blueprint)

    # blueprint for non-auth parts of app
    from currencyexchange.views.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # transactions app
    from currencyexchange.views.transactions import transactions as txn_bp
    app.register_blueprint(txn_bp)

    return app
