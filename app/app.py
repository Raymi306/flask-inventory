try:
    import tomllib
except ImportError:
    import tomli as tomllib

from flask import Flask

from . import db, models
from .blueprints import blueprints


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)

    if config is None:
        app.config.from_file("app_config.toml", load=tomllib.load, text=False)
    else:
        app.config.from_mapping(config)

    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
    )

    db.setup_app(app)
    models.setup_app(app)

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    @app.route("/heartbeat")
    def heartbeat():
        return ""

    @app.after_request
    def apply_security_headers(response):
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        return response

    return app
