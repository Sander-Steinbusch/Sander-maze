from langchain_openai.chat_models import AzureChatOpenAI
from openai import AzureOpenAI

from document_analyzer.configuration import get_configuration


async def init_azure_chat() -> AzureChatOpenAI:
    configuration = get_configuration("azure")

    return AzureChatOpenAI(
        azure_endpoint=configuration["openai_api_base"],
        openai_api_version=configuration["openai_api_version"],
        deployment_name=configuration["deployment_name"],
        #reasoning_effort= "medium",
        temperature=0,
        store=True
    )

def init_open_ai_client() -> AzureOpenAI:
    configuration = get_configuration("azure")

    return AzureOpenAI(
        azure_endpoint= configuration["openai_api_base"],
        api_version = configuration["openai_api_version"],
    )