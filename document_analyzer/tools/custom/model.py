from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from document_analyzer.tools.custom.helpers import init_document_analysis_client
from langchain_core.runnables import Runnable, RunnableConfig
from typing import Optional, Any

def init_custom_ocr_tool():
	return CustomTextExtractorTool(
		document_intelligence_client=init_document_analysis_client()
	)


class CustomTextExtractorTool(Runnable[str, str]):

	document_intelligence_client: DocumentIntelligenceClient

	def __init__(self, document_intelligence_client):
		self.document_intelligence_client = document_intelligence_client

	def run(self, document) -> AnalyzeResult:
		analyze_result = self.analyze_document(document)

		return analyze_result

	def analyze_document(self, document_path) -> AnalyzeResult:
		with open(document_path, "rb") as document:
			poller = self.document_intelligence_client.begin_analyze_document(
				"prebuilt-invoice", analyze_request=document, content_type="application/octet-stream"
			)
		return poller.result()

	# --- Runnable ---

	def invoke(
		self,
		input: str,
		config: Optional[RunnableConfig] = None,
		**kwargs: Any,
	) -> str:
		return self.run(input)