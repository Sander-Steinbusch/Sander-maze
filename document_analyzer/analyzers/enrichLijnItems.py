from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableLambda, RunnableSerializable, RunnableParallel
from typing import Any, Type
from langchain.pydantic_v1 import BaseModel

from document_analyzer.models.enrich_response import Json
from document_analyzer.prompts.analysis.enrichLijnItems import enrich_offerte_prompt


#SUGGESTION: make this chain a dedicated class/object
def build_chain(requested_data: Type[BaseModel], model: ChatOpenAI) -> RunnableSerializable[str, Any]:
    return (
            enrich_offerte_prompt()
            | model
            | JsonOutputParser(pydantic_object=requested_data)
    )


def parse_json(text: str, model: ChatOpenAI) -> dict:
    chain = (
            RunnableParallel(
                json=build_chain(Json, model)
            )
            | RunnableLambda(lambda x: x["json"])
    )

    return chain.invoke(text)
