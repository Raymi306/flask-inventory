from http import HTTPStatus

from pydantic_core import ValidationError

from app.db import NotFoundError


def validation_error_handler(error):
    return error.errors(include_url=False), HTTPStatus.BAD_REQUEST


def not_found_error_handler(error):
    return "", HTTPStatus.NOT_FOUND


def setup_app(app):
    app.register_error_handler(ValidationError, validation_error_handler)
    app.register_error_handler(NotFoundError, not_found_error_handler)
