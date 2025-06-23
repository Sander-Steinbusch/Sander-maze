import asyncio
import json
import logging
import math

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
from document_analyzer.prompts.analysis.extraction import build_extraction_prompt_with_schema, \
    build_table_chunk_prompt, build_basis_info_prompt
from document_analyzer.prompts.analysis.extraction_enrich_abbreviation import \
    build_extraction_enrich_abbreviation_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

json_schema = {
    "title": "Document",
    "description": "Schema for document details.",
    "type": "object",
    "properties": {
        "currency": {"type": "string"},
        "totalCount": {"type": "number"},
        "lineItems": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "lineItemNumber": {"type": "number"},
                    "description": {"type": "string"},
                    "extraInfo": {"type": "string"},
                    "quantity": {"type": "number"},
                    "unit": {"type": "string"},
                    "price": {"type": "number"},
                    "reduction": {"type": "string"},
                    "priceMinusReduction": {"type": "number"},
                    "delivery": {"type": "string"},
                    "chapter": {"type": "string"}
                },
                "required": ["description", "quantity", "unit", "price"]
            }
        }
    },
    "required": ["basis", "currency", "totalCount", "lineItems"]
}


basis_information_schema = {
    "title": "basisInformation",
    "description": "Schema for document basis information.",
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
    },
    "required": ["basis"]
}


params = {
    "store": True
}


async def parse_table_based_extraction(filename: str, chat_model: AzureChatOpenAI, ocr, chunk_size=25):
    try:
        logger.info("Running OCR and extracting tables")
        result = await ocr.analyze_document(filename)
        table_rows = result["table"]
        full_text = result["text"]
        total_items = len(table_rows)

        results = []

        # Step 1: Extract basis information
        basis_model = chat_model.with_structured_output(basis_information_schema)
        basis_prompt = build_basis_info_prompt(full_text)
        basis_result = await asyncio.to_thread(basis_model.invoke,basis_prompt)

        results.append(basis_result)

        # Step 2: Extract lineItems in chunks
        chat_model_structured = chat_model.with_structured_output(json_schema)

        total_chunks = math.ceil(total_items / chunk_size)
        for chunk_number in range(1, total_chunks + 1):
            logger.info(f"Processing chunk {chunk_number}/{total_chunks}")
            prompt = build_table_chunk_prompt(table_rows, chunk_number, chunk_size)
            result = await asyncio.to_thread(chat_model_structured.invoke, prompt)
            results.append(result)

        return results

    except Exception as e:
        logger.error(f"Error in parse_table_based_extraction: {e}")
        raise

def merge_extraction_results(results):
    merged = {
        "basis": [],
        "lineItems": [],
        "currency": None,
        "totalCount": 0
    }

    basis_added = False  # Flag to ensure basis is only added once

    for result in results:
        if not isinstance(result, dict):
            continue

        # Add basis only from the first valid chunk
        if not basis_added and "basis" in result:
            merged["basis"].extend(result["basis"])
            basis_added = True

        # Merge lineItems
        merged["lineItems"].extend(result.get("lineItems", []))

        # Set scalar fields if not already set
        if not merged["currency"] and result.get("currency"):
            merged["currency"] = result["currency"]

        try:
            count = result.get("totalCount", 0)
        except ValueError:
            count = len(result.get("lineItems", []))

        merged["totalCount"] += count

    return merged


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
