from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_swagger_ui import get_swaggerui_blueprint

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    from route.accounts_route import accounts_route
    from route.testRoute import test_route

    app.register_blueprint(accounts_route)
    app.register_blueprint(test_route)

    
    SWAGGER_URL = "/swagger"
    API_URL = "/static/swaggerAuth.json"
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL, API_URL, config={"app_name": "Authentication API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app
