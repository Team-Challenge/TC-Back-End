
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_swagger_ui import get_swaggerui_blueprint
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from config import Config
import redis


db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    cache.init_app(app)

    jwt.init_app(app)

    from routes.accounts_route import accounts_route
    from routes.orders_route import orders_route
    from routes.error_handlers import error_handlers
    from routes.users import users_route

    SWAGGER_URL = "/swagger"
    API_URL = "/static/swaggerAuth.json"
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL, API_URL, config={"app_name": "Authentication API"}
    )

    app.register_blueprint(accounts_route)
    app.register_blueprint(orders_route)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    app.register_blueprint(error_handlers)
    app.register_blueprint(users_route)


    return app


db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
app = create_app()
