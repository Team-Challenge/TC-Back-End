from flask import Flask
from flask_migrate import Migrate
from config import Config
from flask_sqlalchemy import SQLAlchemy
from app.extensions import db, api
from flask_restx import Resource, Api
from app.auth.routes import ns

def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    api.init_app(app)
    db.init_app(app)
     
    from app.models import user
    with app.app_context():
        db.create_all()

    #db = SQLAlchemy(app)

    #migrate = Migrate(app,  db)

    # Initialize Flask extensions here

    # Register blueprints here
    from app.auth import bp as main_bp

    app.register_blueprint(main_bp)
    api.add_namespace(ns)

    @app.route('/test/')
    def test_page():
        return 'abababbabab'

    return app