from math import exp
from unittest.mock import patch, MagicMock, call
from document_analyzer.json.string_processing import remove_trailing_commas, remove_trailing_commas_from_message
from tests.document_analyzer.json.string_fixtures import *
from langchain_core.messages import AIMessage


class TestWhenRemovingTrailingCommas:

	def test_with_trailing_comma_in_json(self):
		input = minimal_json_string_with_trailing_comma_at_end()
		expected = minimal_json_string_valid()

		actual = remove_trailing_commas(input)

		assert actual == expected

	def test_should_not_have_side_effects(self):
		input = minimal_json_string_with_trailing_comma_at_end()
		expected = minimal_json_string_with_trailing_comma_at_end()

		remove_trailing_commas(input)

		assert input == expected

	def test_with_valid_json(self):
		input = minimal_json_string_valid()
		expected = minimal_json_string_valid()

		actual = remove_trailing_commas(input)

		assert actual == expected

	def test_with_empty_string(self):
		input = ""
		expected = ""

		actual = remove_trailing_commas(input)

		assert actual == expected

	def test_with_empty_json_object(self):
		input = empty_json_object()
		expected = empty_json_object()

		actual = remove_trailing_commas(input)

		assert actual == expected

	def test_with_trailing_comma_after_object_field(self):
		input = json_string_with_object_at_end_with_trailing_comma()
		expected = json_string_with_object_at_end_valid()

		actual = remove_trailing_commas(input)

		assert actual == expected

	def test_with_trailing_comma_after_string_field(self):
		input = json_string_with_string_at_end_with_trailing_comma()
		expected = json_string_with_string_at_end_valid()

		actual = remove_trailing_commas(input)

		assert actual == expected

	def test_with_trailing_comma_in_nested_object(self):
		input = minimal_json_string_with_trailing_comma_in_nested_object()
		expected = minimal_json_string_valid()

		actual = remove_trailing_commas(input)

		assert actual == expected

	def test_with_trailing_comma_in_nested_list(self):
		input = minimal_json_string_with_trailing_comma_in_nested_list()
		expected = minimal_json_string_valid()

		actual = remove_trailing_commas(input)

		assert actual == expected

	def test_with_multiple_trailing_commas(self):
		input = minimal_json_string_with_multiple_trailing_commas()
		expected = minimal_json_string_valid()

		actual = remove_trailing_commas(input)

		assert actual == expected

	def test_with_identical_matches(self):
		input = minimal_json_string_with_trailing_comma_in_nested_lists()
		expected = minimal_json_string_valid()
		actual = remove_trailing_commas(input)

		assert actual == expected

	def test_with_multiple_trailing_commas_and_no_whitespace(self):
		input = json_string_with_no_whitspace_with_trailing_comma()
		expected = json_string_with_no_whitespace_valid()

		actual = remove_trailing_commas(input)

		assert actual == expected
		
class TestWhenRemovingTrailingCommasFromMessage:
	
	@patch("document_analyzer.json.string_processing.remove_trailing_commas")
	def test_apply_to_content(self, remove_trailing_commas_mock: MagicMock):
		remove_trailing_commas_mock.return_value = "response"
		expected = "content"
		message = AIMessage(expected)
		
		remove_trailing_commas_from_message(message)
		
		assert remove_trailing_commas_mock.called
		assert remove_trailing_commas_mock.call_args == call(expected)

	@patch("document_analyzer.json.string_processing.remove_trailing_commas")
	def test_return_message_with_expected_content(self, remove_trailing_commas_mock: MagicMock):
		expected = "response"
		remove_trailing_commas_mock.return_value = expected
		message = AIMessage("content")
		
		actual = remove_trailing_commas_from_message(message)
		
		assert isinstance(actual, AIMessage)
		assert actual.content == expected