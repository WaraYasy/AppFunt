"""Flask application factory."""

from flask import Flask
from flask_wtf import CSRFProtect

from app.config import Config
from app.database import Base, SessionLocal, engine

csrf = CSRFProtect()


def create_app(config_class=Config):
    """Create and configure the Flask app: extensions, blueprints, and tables."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app import models  # noqa: F401  register the models with Base

    Base.metadata.create_all(bind=engine)

    @app.teardown_appcontext
    def remove_session(exception=None):
        SessionLocal.remove()

    from app.controllers.assets_controller import assets_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.base_controller import base_bp
    from app.controllers.personas_controller import personas_bp
    from app.controllers.settings_controller import settings_bp

    app.register_blueprint(base_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(personas_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(auth_bp)

    from app import auth, commands, i18n, template_helpers, theme

    csrf.init_app(app)
    auth.init_app(app)
    commands.init_app(app)
    i18n.init_app(app)
    template_helpers.init_app(app)
    theme.init_app(app)

    return app
