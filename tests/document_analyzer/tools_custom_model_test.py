from unittest.mock import Mock, patch, mock_open
from pytest import fixture
from azure.ai.formrecognizer import DocumentAnalysisClient
from document_analyzer.tools.custom.model import CustomTextExtractorTool


@patch("builtins.open", new_callable=mock_open)
class TestGivenCustomTextExtractorToolWhenRun:
    @fixture
    def document_analysis_client(self, analyze_result_with_styles_null):
        poller = Mock()
        poller.result = Mock(return_value=analyze_result_with_styles_null)

        document_analysis_client = Mock(DocumentAnalysisClient)
        document_analysis_client.begin_analyze_document = Mock(return_value=poller)

        return document_analysis_client

    @fixture
    def system_under_test(self, document_analysis_client) -> CustomTextExtractorTool:
        return CustomTextExtractorTool(document_analysis_client)

    def test_then_begin_analyze_document_is_called(
        self, mock_file, document_analysis_client, system_under_test
    ):
        _ = system_under_test.run("document_name.pdf")

        document_analysis_client.begin_analyze_document.assert_called_with(
            model_id="prebuilt-document", document=mock_file(), features=["styleFont"]
        )

    def test_then_file_is_opened(self, mock_file, system_under_test):
        _ = system_under_test.run("document_name.pdf")

        mock_file.assert_called_with("document_name.pdf", "rb")

    def test_then_returns_expected_result(self, _, analyze_result_with_styles_null, system_under_test):
        actual = system_under_test.run("document_name.pdf")

        assert actual == analyze_result_with_styles_null.content
