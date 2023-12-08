
import google.oauth2.credentials
import google_auth_oauthlib.flow

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

flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/drive.metadata.readonly'])

flow.redirect_uri = 'https://www.example.com/oauth2callback'

authorization_url, state = flow.authorization_url(
    access_type='offline',
    include_granted_scopes='true')