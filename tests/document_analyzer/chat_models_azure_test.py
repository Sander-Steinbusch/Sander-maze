from document_analyzer.chat_models.azure import init_azure_chat


def test_can_initialize_model():
    model = init_azure_chat()

    assert model is not None
