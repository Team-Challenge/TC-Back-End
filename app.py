
import threading
import time
import psutil

from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint
from config import Config
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from prometheus_client import Gauge
from prometheus_client import CollectorRegistry
from routes.accounts_route import accounts_route
from routes.orders_route import orders_route
from routes.error_handlers import error_handlers
from routes.users import users_route
from dependencies import db, migrate, ma, jwt, cache


def gather_data(registry):

    ram_metric = Gauge("memory_usage_percent", "Memory usage in percent.",
                       registry=registry)
    cpu_metric = Gauge("cpu_usage_percent", "CPU usage percent.",
                       registry=registry)

    while True:
        time.sleep(1)

        ram = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)

        ram_metric.set(ram.percent)
        cpu_metric.set(cpu)

def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)

    registry = CollectorRegistry()

    thread = threading.Thread(target=gather_data, args=(registry, ))
    thread.start()

    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/health': make_wsgi_app(registry=registry)
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

    return app