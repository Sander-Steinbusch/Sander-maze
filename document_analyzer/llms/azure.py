from langchain_openai import AzureOpenAI
from document_analyzer.configuration import get_configuration

def init_azure_llm() -> AzureOpenAI:
    configuration = get_configuration("azure")

    return AzureOpenAI(
        azure_endpoint=configuration["openai_api_base"],
        openai_api_version=configuration["openai_api_version"],
        deployment_name=configuration["deployment_name"],
        temperature=0,
    )
