
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_swagger_ui import get_swaggerui_blueprint
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config


db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()
cors = CORS()



def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    cors.init_app(app)

    jwt.init_app(app)

    CORS(app, origins=["http://localhost:3000", "http://localhost", "http://127.0.0.1", 
                        "http://0.0.0.0", "https://*ondigitalocean.app", 
                        "http://*ondigitalocean.app"])


    from routes.accounts_route import accounts_route
    from routes.error_handlers import error_handlers
    from routes.test_route import test_route
    from routes.users import users_route

    SWAGGER_URL = "/swagger"
    API_URL = "/static/swaggerAuth.json"
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL, API_URL, config={"app_name": "Authentication API"}
    )

    app.register_blueprint(accounts_route)
    app.register_blueprint(test_route)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    app.register_blueprint(error_handlers)
    app.register_blueprint(users_route)


    return app


db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
app = create_app()
