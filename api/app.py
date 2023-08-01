from flask import Flask
from config import Config
from route.userRoute import user_route
from route.authRoute import auth_route
from route.testRoute import test_route
#from database import db
from flaskBcrypt import flask_bcrypt


def create_app(config_class = Config) -> Flask:
    app = Flask(__name__)

    app.config['JWT_SECRET_KEY'] = 'super-secret'

    app.config.from_object(config_class)

    app.register_blueprint(user_route)
    app.register_blueprint(auth_route)
    app.register_blueprint(test_route)

    app.config['SECRET_KEY'] = 'fds'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/oranwela/apps/TC-Back-End/api/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    flask_bcrypt.init_app(app)

    return app