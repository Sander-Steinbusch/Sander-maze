from typing import Type
from langchain.prompts import PromptTemplate
from langchain.pydantic_v1 import BaseModel
from langchain_core.runnables import RunnableLambda, Runnable
from langchain_core.prompt_values import PromptValue


def enrich_prompt_arguments(text: str) -> dict:
    return {
        'json': text
    }

def enrich_prompt() -> PromptTemplate:
    template = (
        # persona
        "You will get json data, please enrich the existing data. \n"
        "{json}"
        "Whenever a description and the price of a lineItem are exactly the same, merge them and add up the numbers in quantity"
		"Please look up the description of each lijnitem, with reference to the author inside basis. "
		"Add a summary, in Dutch, of any extra information you can find on a new sentence after the text within the extraInfo block. \n"
    )


    return PromptTemplate(
        template=template,
        input_variables=["json"])


def enrich_offerte_prompt() -> Runnable[str, PromptValue]:
    return (
            RunnableLambda(enrich_prompt_arguments)
            | enrich_prompt()
    )
