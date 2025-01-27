import asyncio
from typing import Type, Any

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableSerializable, RunnableLambda, RunnableParallel
from langchain_openai.chat_models import ChatOpenAI
from pydantic import BaseModel

from document_analyzer.json.string_processing import remove_trailing_commas_from_message
from document_analyzer.models.document_response import Document
from document_analyzer.prompts.analysis.extraction_enrich_chapter import build_extraction_enrich_chapter_prompt
from document_analyzer.prompts.analysis.extraction_erich_sum import build_extraction_enrich_sum_prompt
from document_analyzer.prompts.analysis.document_main import build_document_main_prompt
from document_analyzer.tools.custom.model import CustomTextExtractorTool

from document_analyzer.prompts.analysis.extraction import build_extraction_prompt
from document_analyzer.prompts.analysis.extraction_enrich_abbreviation import build_extraction_enrich_abbreviation_prompt


async def parse_extraction_prompt(filename: str, chat_model: ChatOpenAI, ocr: CustomTextExtractorTool):
    file_text = await ocr.run(filename)
    extraction_prompt = build_extraction_prompt(file_text)
    chat_model.bind(response_format={"type": "json_object"})
    result = await asyncio.to_thread(chat_model.invoke, extraction_prompt)
    return result

async def parse_enrich_abbreviation(json: str, chat_model: ChatOpenAI):
    abbreviation_prompt = build_extraction_enrich_abbreviation_prompt(json)
    result = await asyncio.to_thread(chat_model.invoke, abbreviation_prompt)
    return result

async def parse_enrich_sum(json: str, chat_model: ChatOpenAI):
    sum_prompt = build_extraction_enrich_sum_prompt(json)
    result = await asyncio.to_thread(chat_model.invoke, sum_prompt)
    return result

async def parse_enrich_chapter(json: str, chat_model: ChatOpenAI):
    chapter_prompt = build_extraction_enrich_chapter_prompt(json)
    result = await asyncio.to_thread(chat_model.invoke, chapter_prompt)
    return result


def build_chain(requested_data: Type[BaseModel], model: ChatOpenAI) -> RunnableSerializable[str, Any]:
    return (
            build_document_main_prompt(data_model=requested_data)
            | model
            | RunnableLambda(remove_trailing_commas_from_message)
            | JsonOutputParser(pydantic_object=requested_data)
    )


def parse_document_main(text: str, model: ChatOpenAI) -> dict:
    chain = (
            RunnableParallel(
                offerte=build_chain(Document, model)
            )
            | RunnableLambda(lambda x: x["offerte"])
    )

    return chain.invoke(text)


def parse_document_main_file(filename: str, model: ChatOpenAI, ocr: CustomTextExtractorTool):
    file_text = ocr.run(filename)
    return parse_document_main(file_text, model)
