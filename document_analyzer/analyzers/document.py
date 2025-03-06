import asyncio
import logging

from typing import Type, Any
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableSerializable, RunnableLambda, RunnableParallel
from langchain_openai import AzureChatOpenAI
from langchain_openai.chat_models import ChatOpenAI
from pydantic import BaseModel
from document_analyzer.json.string_processing import remove_trailing_commas_from_message
from document_analyzer.models.document_response import Document
from document_analyzer.prompts.analysis.extraction_enrich_chapter import build_extraction_enrich_chapter_prompt
from document_analyzer.prompts.analysis.extraction_erich_sum import build_extraction_enrich_sum_prompt
from document_analyzer.prompts.analysis.document_main import build_document_main_prompt
from document_analyzer.tools.custom.model import CustomTextExtractorTool
from document_analyzer.prompts.analysis.extraction import build_extraction_prompt_with_schema
from document_analyzer.prompts.analysis.extraction_enrich_abbreviation import \
    build_extraction_enrich_abbreviation_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

json_schema = {
    "title": "Document",
    "description": "Schema for document details.",
    "type": "object",
    "properties": {
        "basis": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "author": {"type": "string"},
                    "documentDate": {"type": "string"},
                    "documentNumber": {"type": "string"},
                    "documentType": {"type": "string"}
                },
                "required": ["author", "documentDate", "documentNumber", "documentType"]
            }
        },
        "currency": {"type": "string"},
        "totalCount": {"type": "string"},
        "lineItems": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "extraInfo": {"type": "string"},
                    "quantity": {"type": "string"},
                    "unit": {"type": "string"},
                    "price": {"type": "string"},
                    "reduction": {"type": "string"},
                    "priceMinusReduction": {"type": "string"},
                    "delivery": {"type": "string"},
                    "chapter": {"type": "string"}
                },
                "required": ["description", "quantity", "unit", "price"]
            }
        }
    },
    "required": ["basis", "currency", "totalCount", "lineItems"]
}

params = {
    "store": True
}

async def parse_extraction_prompt(filename: str, chat_model: AzureChatOpenAI, ocr: CustomTextExtractorTool):
    try:
        logger.info("Starting parse_extraction_prompt")
        file_text = await ocr.run(filename)
        extraction_prompt = build_extraction_prompt_with_schema(file_text)
        chat_model_structured = chat_model.with_structured_output(json_schema)
        result = await asyncio.to_thread(chat_model_structured.invoke, extraction_prompt, **params)
        return result
    except Exception as e:
        logger.error(f"Error in parse_extraction_prompt: {e}")
        raise


async def parse_enrich_abbreviation(json: str, chat_model: ChatOpenAI):
    try:
        logger.info("Starting parse_enrich_abbreviation")
        abbreviation_prompt = build_extraction_enrich_abbreviation_prompt(json)
        result = await asyncio.to_thread(chat_model.invoke, abbreviation_prompt, **params)
        return result
    except Exception as e:
        logger.error(f"Error in parse_enrich_abbreviation: {e}")
        raise


async def parse_enrich_sum(json: str, chat_model: ChatOpenAI):
    try:
        logger.info("Starting parse_enrich_sum")
        sum_prompt = build_extraction_enrich_sum_prompt(json)
        result = await asyncio.to_thread(chat_model.invoke, sum_prompt, **params)
        return result
    except Exception as e:
        logger.error(f"Error in parse_enrich_sum: {e}")
        raise


async def parse_enrich_chapter(json: str, chat_model: ChatOpenAI):
    try:
        logger.info("Starting parse_enrich_chapter")
        chapter_prompt = build_extraction_enrich_chapter_prompt(json)
        result = await asyncio.to_thread(chat_model.invoke, chapter_prompt, **params)
        return result
    except Exception as e:
        logger.error(f"Error in parse_enrich_chapter: {e}")
        raise


def build_chain(requested_data: Type[BaseModel], model: ChatOpenAI) -> RunnableSerializable[str, Any]:
    try:
        return (
                build_document_main_prompt(data_model=requested_data)
                | model
                | RunnableLambda(remove_trailing_commas_from_message)
                | JsonOutputParser(pydantic_object=requested_data)
        )
    except Exception as e:
        logger.error(f"Error in build_chain: {e}")
        raise

#not used, evaluate and possibly delete
def parse_document_main(text: str, model: ChatOpenAI) -> dict:
    try:
        chain = (
                RunnableParallel(
                    offerte=build_chain(Document, model)
                )
                | RunnableLambda(lambda x: x["offerte"])
        )
        return chain.invoke(text)
    except Exception as e:
        logger.error(f"Error in parse_document_main: {e}")
        raise
