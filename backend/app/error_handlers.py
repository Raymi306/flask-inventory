from http import HTTPStatus

from pydantic_core import ValidationError

from app.db import NotFoundError, DuplicateError


HANDLER_MAP = {
    ValidationError: (lambda error: (error.errors(include_url=False), HTTPStatus.BAD_REQUEST)),
    NotFoundError: (lambda _: ("", HTTPStatus.NOT_FOUND)),
    DuplicateError: (lambda _: ("", HTTPStatus.CONFLICT)),
}

def setup_app(app):
    for error_type, func in HANDLER_MAP.items():
        app.register_error_handler(error_type, func)
