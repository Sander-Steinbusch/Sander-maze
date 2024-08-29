from unittest.mock import MagicMock

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import AIMessage

class ChatOpenAIMockBuilder:
	
	def __init__(self):
		self.mock = MagicMock(spec=AzureChatOpenAI)

	def with_invoke(self, message_content):
		response_message = AIMessage(message_content)
		self.mock.invoke.return_value = response_message

		return self

	def build(self) -> AzureChatOpenAI:
		return self.mock