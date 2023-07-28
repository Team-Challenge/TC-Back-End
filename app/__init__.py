from flask import Flask
from flask_migrate import Migrate
from config import Config
from flask_sqlalchemy import SQLAlchemy
from app.extensions import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    from app.models import user
    with app.app_context():
        db.create_all()

    #app.config['SECRET_KEY']='004f2af45d3a4e161a7dd2d17fdae47f'
    #app.config['SQLALCHEMY_DATABASE_URI']='sqlite://///home/oranwela/apps/TC-Back-End/marketplace.db'
    #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    #db = SQLAlchemy(app)

    #migrate = Migrate(app,  db)

    # Initialize Flask extensions here

    # Register blueprints here
    from app.auth import bp as main_bp
    app.register_blueprint(main_bp)

    @app.route('/test/')
    def test_page():
        return 'abababbabab'

    return app