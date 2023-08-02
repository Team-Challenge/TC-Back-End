from flask import Flask, current_app
from config import Config
from route.userRoute import user_route
from route.authRoute import auth_route
from route.testRoute import test_route
from flasgger import Swagger

def create_app(config_class = Config) -> Flask:
    app = Flask(__name__)
    swagger = Swagger(app)

    app.config['JWT_SECRET_KEY'] = 'super-secret'

    app.config.from_object(config_class)

    app.register_blueprint(user_route)
    app.register_blueprint(auth_route)
    app.register_blueprint(test_route)

    app.config['SECRET_KEY'] = 'fds'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/oranwela/apps/TC-Back-End/api/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    return app