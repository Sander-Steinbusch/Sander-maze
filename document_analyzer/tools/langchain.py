from document_analyzer.configuration import get_configuration
from langchain.tools.azure_cognitive_services import AzureCogsFormRecognizerTool


def init_langchain_ocr_tool():
    configuration = get_configuration("azure")

    return AzureCogsFormRecognizerTool(
        azure_cogs_endpoint=configuration["cognitive_services_url"],
    )
