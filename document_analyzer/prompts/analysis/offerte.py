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
		"You will extract data from invoices and offers in multiple requests, \n"
		"each request contains a specific subset of the data contained in the invoices and offers. \n"
		"The main goal is to extract pricing information. These need to be complete and include at least a description, unit price and a unit of measure.\n"
		"This is the text content of the invoice or offer you will analyze: \n"
		"{document} \n"
		"{output_structure} \n"
		# restrictions
		"But do not include this json metadata in the response. \n"
		"Do not add any fields to the response that are not in the specified structure. \n"
		"Do not paraphrase texts, only use the text found in the given resume. \n"
		"Do not leave out words or phrases. \n"
		"Return all dates in the unified format 'DD-MM-YYYY'. \n"
		"Return all numbers in a Belgian number format.\n"
		"For the values in this JSON object, \n"
		"keep the following restrictions in mind: \n"
		"For a field where its type is a list, \n"
		"but no elements for that list are found, \n"
		"give an empty list for that field. \n"
		"After completing all the instructions there is some extra things you need to do:\n"
		"Please remove all the '\n' you can find. Replace them with a space. \n"
		"If within lijnitem the prijs field is empty, delete the whole item.\n"
		"If the omschrijving of a lijnitem is a tax or levy, delete the whole item.\n"
		"If within lijnitem there is a symbols of SI units, Please search for their full name, in dutch and replace them.\n"
		"If within lijnitem the prijs field contains a decimal number, change the notation of that number to european standards.\n"
		"For example, 350ML becomes 350 milliliter. 350mm becomes 350 millimeter and so on.\n"
		"Please also correct any spelling mistake you might encounter.\n"
		"Please look up the omschrijving of each lijnitem, with reference to the author of the document."
		"Add a summary, in Dutch, of any extra information you can find on a new sentence after the text within the extraInfo block."
		"\n"
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