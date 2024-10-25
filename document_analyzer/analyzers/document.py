from langchain_openai.chat_models import ChatOpenAI
from document_analyzer.tools.custom.model import CustomTextExtractorTool

from document_analyzer.prompts.analysis.extraction import build_extraction_prompt


def parse_prompt(filename: str, chat_model: ChatOpenAI, ocr: CustomTextExtractorTool):
    file_text = ocr.run(filename)
    extraction_prompt = build_extraction_prompt(file_text)
    chat_model.bind(response_format={"type": "json_object"})
    return chat_model.invoke(extraction_prompt)