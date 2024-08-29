from langchain_core.messages import SystemMessage, HumanMessage
from unittest.mock import patch, MagicMock

from document_analyzer.prompts.translation import build_persona_message, build_messages


class TestWhenBuildPersonaMessage:
    input = "french"

    def test_returns_expected_type(self):
        actual = build_persona_message(self.input)

        assert isinstance(actual, SystemMessage)

    def test_returns_expected_content(self):
        expected = """
You will translate all following messages to French.
Your tasks is as follows:
1. Translate each message to French.
2. Maintain the original order of messages in the response.
3. Separate each translated message with two empty lines.
4. If a message is already in French, return the original message.
5. If the original language cannot be determined or the text is nonsensical,
return the original text.
6. Do not add any additional context.
"""

        actual = build_persona_message(self.input)

        assert actual.content == expected


class TestWhenBuildMessages:
    input = {"language": "french", "texts": [{"id": "123", "text": "original text"}]}

    def test_returns_expected_number_of_messages(self):
        actual = build_messages(self.input)

        assert len(actual) == len(self.input["texts"]) + 1

    @patch("document_analyzer.prompts.translation.build_persona_message")
    def test_first_message_is_persona_message(self, persona_message_mock: MagicMock):
        persona_message = SystemMessage(content="persona message")
        persona_message_mock.return_value = persona_message

        actual = build_messages(self.input)

        assert actual[0] == persona_message

    def test_contains_message_for_each_text_in_input(self):
        expected = [HumanMessage(content=text["text"]) for text in self.input["texts"]]

        actual = build_messages(self.input)

        assert actual[1:] == expected
