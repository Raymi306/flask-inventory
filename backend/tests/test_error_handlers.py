from http import HTTPStatus

from flask import Flask
from pydantic import BaseModel

from app import error_handlers


def test_error_handlers():
    app = Flask("test")
    error_handlers.setup_app(app)

    class Model(BaseModel):
        field: str

    @app.route("/testing")
    def testing():
        Model(foo="bar")

    response = app.test_client().get("/testing")
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.mimetype == "application/json"
    expected_text = (
        '[{"input":{"foo":"bar"},"loc":["field"],"msg":"Field required","type":"missing"}]\n'
    )
    assert response.text == expected_text
