from typing import Type
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.pydantic_v1 import BaseModel
from langchain_core.runnables import RunnableLambda, Runnable
from langchain_core.prompt_values import PromptValue

def build_prompt_arguments(text: str) -> dict:
	return {
		'document': text
	}

def build_prompt(data_model: Type[BaseModel]) -> PromptTemplate:
	template = (
		# persona
		"You are an invoice and offer parser in the field of construction works. \n"
		"The main goal is to extract pricing information. These need to be complete and include at least a description, "
		"unit price and a unit of measure. Don't add an item if it's incomplete. \n"
		"When there is a symbol of SI units, Please search for their full name in dutch and replace them. \n"
		"For example, 350ML becomes 350 milliliter. 350mm becomes 350 millimeter and so on. \n"
		"Return all dates in the unified format 'DD-MM-YYYY'. \n"
		"Return all numbers in a Belgian number format.\n"
		"You can look up any extra information if requested. \n"
		"This is the text content of the invoice or offer you will analyze: \n"
		"{document} \n"
		"{output_structure} \n"
		"Do not add any fields to the response that are not in the specified structure. \n"
		"Whenever a description and the price of a lineItem are exactly the same, merge them and add up the numbers in quantity"
		"Please look up the description of each lijnitem, with reference to the author inside basis. \n"
		"Add a summary, in Dutch, of any extra information you can find on a new sentence after the text within the extraInfo block. \n"
	)
	parser = JsonOutputParser(pydantic_object=data_model)

	return PromptTemplate(
		template=template,
		input_variables=["document"],
		partial_variables={"output_structure": parser.get_format_instructions()})

def build_offerte_prompt(data_model: Type[BaseModel]) -> Runnable[str, PromptValue]:
	return (
		RunnableLambda(build_prompt_arguments)
		| build_prompt(data_model)
	)