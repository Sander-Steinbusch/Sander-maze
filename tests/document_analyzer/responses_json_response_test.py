from pytest import fixture
from document_analyzer.responses.json_response import build_json_response


@fixture
def dictionary():
    return {"key": "value"}


def test_build_json_response_expected_body_value(dictionary):
    response = build_json_response(dictionary)

    assert response.response == [b'{"key": "value"}']


def test_build_json_response_is_json(dictionary):
    response = build_json_response(dictionary)

    assert response.is_json


def test_build_json_response_expected_content_type_header(dictionary):
    response = build_json_response(dictionary)

    assert response.headers["Content-Type"] == "application/json"
