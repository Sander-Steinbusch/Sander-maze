from document_analyzer.configuration import get_configuration
from langchain.utils.env import get_from_env
from typing import List
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, DocumentStyle
#from azure.ai.formrecognizer import AnalyzeResult, DocumentStyle


def init_document_analysis_client():
    configuration = get_configuration("azure")

    return DocumentIntelligenceClient(
        endpoint=configuration["cognitive_services_url"],
        credential=_get_azure_credentials(),
    )


def _get_azure_credentials():
    key = get_from_env("azure_cogs_key", "AZURE_COGS_KEY")

    return AzureKeyCredential(key)


def group_by_background(input: AnalyzeResult) -> List[str]:
    if (input.styles is None) or (input.styles == []):
        return [input.content]

    background_styles = [
        style for style in input.styles if style.background_color is not None
    ]
    return list(map(_extract_by_style_from(input.content), background_styles))


def _extract_by_style_from(content):
    return lambda style: _extract_content_by_style(content, style)


def _extract_content_by_style(content: str, style: DocumentStyle) -> str:
    span_contents = [
        content[span.offset : span.offset + span.length] for span in style.spans
    ]
    return " ".join(span_contents)
