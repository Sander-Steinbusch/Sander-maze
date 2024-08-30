from document_analyzer.models.offerte_response import Offerte
from mock_document_analyzer.data import get_test_data

def test_data_conforms_to_model():
    data: dict = get_test_data()

    model = Offerte.model_validate(data)

    assert model is not None
