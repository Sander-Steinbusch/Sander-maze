from unittest.mock import MagicMock, call, patch
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from document_analyzer.translators.azure import (
	replace_with_translations,
	build_post_processor,
	translate_texts
)

class TestWhenReplaceWithTranslations:

	input = {
		"language": "french",
		"texts": [
			{
				"id": "123",
				"text": "original text 1"
			},
			{
				"id": "456",
				"text": "orginal text 2"
			}
		]
	}
	response = AIMessage(content="""translated text 1\n\ntranslated text 2""")

	def test_replaces_texts_in_order(self):
		expected = [
			{
				"id": "123",
				"text": "translated text 1"
			},
			{
				"id": "456",
				"text": "translated text 2"
			}
		]
		
		actual = replace_with_translations(self.input, self.response)

		assert actual == expected


class TestWhenBuildPostProcessor:

	input = {
		"language": "french",
		"texts": [
			{
				"id": "123",
				"text": "original text 1"
			},
			{
				"id": "456",
				"text": "orginal text 2"
			}
		]
	}

	def test_returns_value(self):
		actual = build_post_processor(self.input)
		
		assert actual is not None

	def test_returns_expected_type(self):
		actual = build_post_processor(self.input)
		
		assert isinstance(actual, Runnable)
		

class TestWhenTranslateTexts:

	input = {
		"language": "french",
		"texts": [
			{
				"id": "123",
				"text": "original text 1"
			},
			{
				"id": "456",
				"text": "orginal text 2"
			}
		]
	}

	modelMock = MagicMock(spec=ChatOpenAI)

	@patch("document_analyzer.translators.azure.build_messages")
	def test_build_messages_is_called(self, build_messages_mock: MagicMock):
		translate_texts(self.modelMock, self.input)

		assert build_messages_mock.called

	@patch("document_analyzer.translators.azure.build_messages")
	def test_build_messages_with_expected_input(self, build_messages_mock: MagicMock):
		translate_texts(self.modelMock, self.input)

		assert build_messages_mock.call_args == call(self.input)

	def test_invokes_model(self):
		translate_texts(self.modelMock, self.input)

		assert self.modelMock.invoke.called

	@patch("document_analyzer.translators.azure.build_messages")
	def test_invokes_model_with_expected_messages(self, build_messages_mock: MagicMock):
		expected_messages = [HumanMessage(content="message content")]
		build_messages_mock.return_value = expected_messages

		translate_texts(self.modelMock, self.input)

		assert self.modelMock.invoke.call_args[0][0] == expected_messages

	def test_returns_expected_result(self):
		response = AIMessage(content="""translated text 1\n\ntranslated text 2""")
		self.modelMock.invoke.return_value = response
		expected = [
			{
				"id": "123",
				"text": "translated text 1"
			},
			{
				"id": "456",
				"text": "translated text 2"
			}
		]

		actual = translate_texts(self.modelMock, self.input)

		assert actual == expected
