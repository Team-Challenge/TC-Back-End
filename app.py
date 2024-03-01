
import psutil
from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint
from prometheus_client import Gauge, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from config import Config
from dependencies import cache, db, jwt, ma, migrate, registry
from models import accounts, categories, orders, products, shops
from routes.accounts import accounts
from routes.categories import categories
from routes.orders import orders
from routes.products import products
from routes.shops import shops


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

    app.register_blueprint(accounts)
    app.register_blueprint(orders)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    app.register_blueprint(shops)
    app.register_blueprint(categories)
    app.register_blueprint(products)

    return app

def create_testing_app(config_class=Config) -> Flask:
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/healthcheck': make_wsgi_app(registry=registry)
        })

    app.config.from_object(config_class)

    # db.init_app(app)  # To delay database initialization

    migrate.init_app(app, db)
    ma.init_app(app)
    cache.init_app(app)
    jwt.init_app(app)

    SWAGGER_URL = "/swagger"
    API_URL = "/static/swaggerAuth.json"
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL, API_URL, config={"app_name": "Authentication API"}
    )

    app.register_blueprint(accounts)
    app.register_blueprint(orders)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    app.register_blueprint(shops)
    app.register_blueprint(categories)

    return app
