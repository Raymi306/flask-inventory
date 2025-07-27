from pydantic_core import ValidationError


def validation_error_handler(error):
    return error.errors(include_url=False), 400


def setup_app(app):
    app.register_error_handler(ValidationError, validation_error_handler)
