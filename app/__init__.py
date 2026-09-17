from flask import Flask

from app.config import Config
from app.database import Base, SessionLocal, engine


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app import models  # noqa: F401  registra los modelos en Base

    Base.metadata.create_all(bind=engine)

    @app.teardown_appcontext
    def remove_session(exception=None):
        SessionLocal.remove()

    from app.controllers.base_controller import base_bp

    app.register_blueprint(base_bp)

    return app
