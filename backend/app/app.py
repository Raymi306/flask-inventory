from dataclasses import asdict, is_dataclass

import tomllib
from flask import Flask
from flask_cors import CORS

from . import db, error_handlers, models
from .blueprints import blueprints


class FlaskApp(Flask):
    def make_response(self, rv):
        if is_dataclass(rv):
            rv = asdict(rv)
        return super().make_response(rv)


def create_app(config=None):
    app = FlaskApp(__name__, instance_relative_config=True)
    CORS(app, supports_credentials=True)

    if config is None:
        app.config.from_file("app_config.toml", load=tomllib.load, text=False)
    else:
        app.config.from_mapping(config)

    app.config.update(
        #SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=False,
        #SESSION_COOKIE_SAMESITE="Strict",
        #SESSION_COOKIE_DOMAIN="127.0.0.1",
    )

    db.setup_app(app)
    models.setup_app(app)
    error_handlers.setup_app(app)

    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    @app.route("/heartbeat")
    def heartbeat():
        return ""

    @app.after_request
    def apply_security_headers(response):
        #response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        #response.headers["Content-Security-Policy"] = "default-src 'self'"
        #response.headers["X-Content-Type-Options"] = "nosniff"
        #response.headers["X-Frame-Options"] = "SAMEORIGIN"
        return response

    return app
