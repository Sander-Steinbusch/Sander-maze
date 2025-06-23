import logging

from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from document_analyzer.tools.custom.helpers import init_document_analysis_client
from langchain_core.runnables import Runnable, RunnableConfig
from typing import Optional, Any
import aiofiles

logger = logging.getLogger(__name__)

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

    async def analyze_document(self, document_path) -> dict:
        async with aiofiles.open(document_path, "rb") as document:
            content = await document.read()
            poller = await self.document_intelligence_client.begin_analyze_document(
                model_id="prebuilt-layout",
                analyze_request=content,
                content_type="application/octet-stream"
            )
            result = await poller.result()

        # Extract full text
        full_text = " ".join([line.content for page in result.pages for line in page.lines])

        # Extract table rows
        table_rows = []
        for table in result.tables:
            max_row = max(cell.row_index for cell in table.cells)
            row_map = {i: [] for i in range(max_row + 1)}
            for cell in table.cells:
                row_map[cell.row_index].append((cell.column_index, cell.content))
            for row_index in sorted(row_map.keys()):
                sorted_row = [content for _, content in sorted(row_map[row_index])]
                table_rows.append(sorted_row)

        #logger.info(table_rows)

        return {
            "text": full_text,
            "table": table_rows
        }

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