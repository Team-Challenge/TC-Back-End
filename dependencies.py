
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow

from flask_jwt_extended import JWTManager
from flask_caching import Cache


db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})