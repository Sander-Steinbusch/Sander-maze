from typing import Type
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel
from langchain_core.runnables import RunnableLambda, Runnable
from langchain_core.prompt_values import PromptValue


def build_prompt_arguments(text: str) -> dict:
    return {
        'document': text
    }


def build_prompt(data_model: Type[BaseModel]) -> PromptTemplate:
    template = (
        # persona
        "you are a"
        "The main goal is to extract pricing information. These need to be complete and include at least a description, "
        "unit price and a unit of measure. Don't add an item if it's incomplete."
        "The name of the item can be in front or after the pricing."
        "These items can be exact duplicates, still add all of them."
        "Return all dates in the unified format 'DD-MM-YYYY'."
        "Return all numbers in a Belgian number format."
		"Replace all symbols or abbreviations of SI units, by their full name in dutch."
        "For example cm by centimeter, ml by milliliter etc."
        "This is the text content of the invoice or offer you will analyze:"
        "{document}"
        "And this is the output structure:"
        "{output_structure}"
        "At the end of doing everything double check if you have all the items."
        "Add the ones you missed and apply all the above rules."
        "Count the items, you've added. put the number in totalCount"
    )
    parser = JsonOutputParser(pydantic_object=data_model)

    return PromptTemplate(
        template=template,
        input_variables=["document"],
        partial_variables={"output_structure": parser.get_format_instructions()})


def build_document_main_prompt(data_model: Type[BaseModel]) -> Runnable[str, PromptValue]:
    return (
            RunnableLambda(build_prompt_arguments)
            | build_prompt(data_model)
    )
