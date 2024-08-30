from unittest.mock import MagicMock, patch
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import Runnable

from document_analyzer.prompts.analysis.offerte import (
	build_prompt,
	build_prompt_arguments,
	build_offerte_prompt
)


class TestWhenBuildPromptArguments:

	def test_return_expected_dict(self):
		actual = build_prompt_arguments("text")

		assert actual.keys().__contains__("document")

	def test_sets_expected_value(self):
		expected = "text"

		actual = build_prompt_arguments(expected)

		assert actual["document"] == expected

class TestWhenBuildPrompt:
	

	   
	def test_returns_PromptTemplate(self):
		actual = build_prompt(self.data_model)

		assert isinstance(actual, PromptTemplate)

	def test_sets_expected_template(self):
		expected = (
		"You are an invoice and offer parser in the field of construction works. \n"
		"You will extract data from invoices and offers in multiple requests, \n"
		"each request contains a specific subset of the data contained in the invoices and offers. \n"
		"The main goal is to extract pricing information. These need to be complete and include at least a description, unit price and a unit of measure.\n"
		"This is the text content of the invoice or offer you will analyze: \n"
		"{document} \n"
		"{output_structure} \n"
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
		
		actual = build_prompt(self.data_model)

		assert actual.template == expected

	def test_sets_expected_input_variables(self):
		actual = build_prompt(self.data_model)

		assert actual.input_variables == ["document"]

	@patch("document_analyzer.prompts.analysis.segmented.JsonOutputParser")
	def test_instantiates_JsonOutputParser(self, parserMock: MagicMock):
		build_prompt(self.data_model)

		assert parserMock.called

	@patch("document_analyzer.prompts.analysis.segmented.JsonOutputParser")
	def test_gets_format_instructions_from_parser(self, parserMock: MagicMock):
		parser = MagicMock(spec=JsonOutputParser)
		parserMock.return_value = parser
		
		build_prompt(self.data_model)

		assert parser.get_format_instructions.called

	@patch("document_analyzer.prompts.analysis.segmented.JsonOutputParser")
	def test_uses_format_instructions_as_partial_variable(self, parserMock: MagicMock):
		parser = MagicMock(spec=JsonOutputParser)
		expected = "requested structure"
		parser.get_format_instructions = MagicMock(return_value = expected)
		parserMock.return_value = parser
		
		actual = build_prompt(self.data_model)

		assert actual.partial_variables["output_structure"] == expected

class TestWhenBuildSegmentedPrompt:


	def test_returns_value(self):
		actual = build_offerte_prompt(self.data_model)

		assert actual is not None

	def test_returns_expected_type(self):
		actual = build_offerte_prompt(self.data_model)

		assert isinstance(actual, Runnable)