from flask import Flask
from flask_wtf import CSRFProtect

from app.config import Config
from app.database import Base, SessionLocal, engine

csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app import models  # noqa: F401  registra los modelos en Base

    Base.metadata.create_all(bind=engine)

    @app.teardown_appcontext
    def remove_session(exception=None):
        SessionLocal.remove()

    from app.controllers.assets_controller import assets_bp
    from app.controllers.base_controller import base_bp
    from app.controllers.personal_controller import personal_bp

    app.register_blueprint(base_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(personal_bp)

    from app import auth, i18n, template_helpers

    csrf.init_app(app)
    auth.init_app(app)
    i18n.init_app(app)
    template_helpers.init_app(app)

    return app
