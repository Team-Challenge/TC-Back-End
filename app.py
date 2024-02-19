
import psutil

from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint
from config import Config
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from prometheus_client import Gauge
from routes.accounts_route import accounts_route
from routes.orders_route import orders_route
from routes.error_handlers import error_handlers
from routes.users import users_route
from routes.shops_route import shops_route
from routes.categories_route import categories_route
from routes.products_route import products_route
from dependencies import db, migrate, ma, jwt, cache, registry


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__,static_folder='static',static_url_path='/static')

    ram_metric = Gauge("memory_usage_percent", "Memory usage in percent.",
                       registry=registry)
    cpu_metric = Gauge("cpu_usage_percent", "CPU usage percent.",
                       registry=registry)

    ram_metric.set_function(lambda: psutil.virtual_memory().percent)
    cpu_metric.set_function(lambda: psutil.cpu_percent(interval=1))

    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/healthcheck': make_wsgi_app(registry=registry)
        })

    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    cache.init_app(app)
    jwt.init_app(app)

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
    app.register_blueprint(shops_route)
    app.register_blueprint(categories_route)
    app.register_blueprint(products_route)

    return app