from unittest.mock import MagicMock
from document_analyzer.tools.custom.model import CustomTextExtractorTool


class CustomTextExtractorToolMockBuilder:

	def __init__(self):
		self.mock = MagicMock(spec=CustomTextExtractorTool)

	def with_run(self, response: str):
		self.mock.run.return_value = response
	
		return self
	
	def build(self) -> CustomTextExtractorTool:
		return self.mock