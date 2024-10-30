from http import HTTPStatus


def test_heartbeat(client):
    response = client.get("/heartbeat")
    assert response.status_code == HTTPStatus.OK
    assert b"" == response.data
