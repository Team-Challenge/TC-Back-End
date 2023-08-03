from flask import Flask, current_app
from config import Config
from route.accountsRoute import accounts_route
from route.testRoute import test_route
from flasgger import Swagger

def create_app(config_class = Config) -> Flask:
    app = Flask(__name__)
    swagger = Swagger(app)

    app.config['JWT_SECRET_KEY'] = 'super-secret'

    app.config.from_object(config_class)

    app.register_blueprint(accounts_route)
    app.register_blueprint(test_route)

    app.config['SECRET_KEY'] = 'fds'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/kyrylo/TC-Back-End/market.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    return app