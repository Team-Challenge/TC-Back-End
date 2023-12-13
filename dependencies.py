
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow

from flask_jwt_extended import JWTManager
from flask_caching import Cache
from prometheus_client import CollectorRegistry
from authlib.integrations.flask_client import OAuth


db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
registry = CollectorRegistry()
oauth = OAuth()
