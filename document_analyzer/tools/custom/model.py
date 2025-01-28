from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from document_analyzer.tools.custom.helpers import init_document_analysis_client
from langchain_core.runnables import Runnable, RunnableConfig
from typing import Optional, Any
import aiofiles

async def init_custom_ocr_tool():
    document_intelligence_client = await init_document_analysis_client()
    return CustomTextExtractorTool(document_intelligence_client=document_intelligence_client)

class CustomTextExtractorTool(Runnable[str, str]):

    document_intelligence_client: DocumentIntelligenceClient

    def __init__(self, document_intelligence_client):
        self.document_intelligence_client = document_intelligence_client

    async def run(self, document) -> str:
        analyze_result = await self.analyze_document(document)
        return analyze_result

    async def analyze_document(self, document_path) -> str:
        async with aiofiles.open(document_path, "rb") as document:
            content = await document.read() # Read the file content as bytes
            poller = await self.document_intelligence_client.begin_analyze_document(
                "prebuilt-read", analyze_request=content, content_type="application/octet-stream"
            )
            result = await poller.result()  # Await the result of the long-running operation
        return result.content

    async def close(self):
        await self.document_intelligence_client.close()  # Ensure the client session is closed
    # --- Runnable ---

    async def invoke(
        self,
        input: str,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> str:
        return await self.run(input)