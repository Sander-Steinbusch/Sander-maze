from langchain_openai.chat_models import ChatOpenAI

from document_analyzer.prompts.analysis.extraction_enrich_chapter import build_extraction_enrich_chapter_prompt
from document_analyzer.prompts.analysis.extraction_erich_sum import build_extraction_enrich_sum_prompt
from document_analyzer.tools.custom.model import CustomTextExtractorTool

from document_analyzer.prompts.analysis.extraction import build_extraction_prompt
from document_analyzer.prompts.analysis.extraction_enrich_abbr import build_extraction_enrich_abbr_prompt


def parse_extraction_prompt(filename: str, chat_model: ChatOpenAI, ocr: CustomTextExtractorTool):
    file_text = ocr.run(filename)
    extraction_prompt = build_extraction_prompt(file_text)
    chat_model.bind(response_format={"type": "json_object"})
    return chat_model.invoke(extraction_prompt)

def parse_enrich_abbr(json: str, chat_model: ChatOpenAI):
    abbr_prompt = build_extraction_enrich_abbr_prompt(json)
    return chat_model.invoke(abbr_prompt)

def parse_enrich_sum(json: str, chat_model: ChatOpenAI):
    sum_prompt = build_extraction_enrich_sum_prompt(json)
    return chat_model.invoke(sum_prompt)

def parse_enrich_chapter(json: str, chat_model: ChatOpenAI):
    chapter_prompt = build_extraction_enrich_chapter_prompt(json)
    return chat_model.invoke(chapter_prompt)