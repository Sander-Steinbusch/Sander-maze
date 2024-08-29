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
			"You are a resume parser for resumes in the field of IT. \n"
			"You will extract data from resumes in multiple requests, \n"
			"each request contains a specific subset of the data contained in the resume. \n"
			"This is the text content of the resume you will analyze: \n"
			"{document} \n"
			"{output_structure} \n"
			"But do not include this json metadata in the response. \n"
			"Do not add any fields to the response that are not in the specified structure. \n"
			"Do not paraphrase texts, only use the text found in the given resume. \n"
			"Return all dates in the unified format 'YYYY-MM-DD'. \n"
			"For the values in this JSON object, \n"
			"keep the following restrictions in mind: \n"
			"For a field where its type is a list, \n"
			"but no elements for that list are found, \n"
			"give an empty list for that field. \n"
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