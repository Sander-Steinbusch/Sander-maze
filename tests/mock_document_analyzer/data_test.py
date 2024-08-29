from document_analyzer.models.resume_response import ResumeResponse
from mock_document_analyzer.data import get_test_data

def test_data_conforms_to_model():
    data: dict = get_test_data()

    model = ResumeResponse.validate(data)

    assert model is not None
