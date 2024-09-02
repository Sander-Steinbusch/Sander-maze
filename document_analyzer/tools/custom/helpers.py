from document_analyzer.configuration import get_configuration
from langchain.utils.env import get_from_env
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

def init_document_analysis_client():
    configuration = get_configuration("azure")

    return DocumentIntelligenceClient(
        endpoint=configuration["cognitive_services_url"],
        credential=_get_azure_credentials(),
    )

def _get_azure_credentials():
    key = get_from_env("azure_cogs_key", "AZURE_COGS_KEY")

    return AzureKeyCredential(key)