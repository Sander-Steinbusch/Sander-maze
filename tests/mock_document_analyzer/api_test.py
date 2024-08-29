from pytest import fixture
from mock_document_analyzer.api import mock_api
from mock_document_analyzer.data import get_test_data
from json import dumps

@fixture
def app():
    mock_api.config.update({
        "TESTING": True
    })

    return mock_api

@fixture
def client(app):
    return app.test_client()

def test_analyze(client):
    expected_body = dumps(get_test_data()).encode()

    response = client.post("/analyze")

    assert response is not None
    assert response.content_type == "application/json"
    assert response.data == expected_body

