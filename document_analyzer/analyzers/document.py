import asyncio
import logging
import math

from langchain_openai import AzureChatOpenAI
from langchain_openai.chat_models import ChatOpenAI

from document_analyzer.prompts.analysis.extraction import (
    build_basis_info_prompt,
    build_line_items_prompt,
)
from document_analyzer.prompts.analysis.extraction_enrich_chapter import (
    build_extraction_enrich_chapter_prompt,
)
from document_analyzer.tools.pdf_images import render_document_to_images

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Number of page images sent to the model per line-item extraction call. Chunking
# by pages keeps large documents within the model's context window while still
# giving the model the full visual context of each page it reasons over.
DEFAULT_PAGE_CHUNK_SIZE = 4

json_schema = {
    "title": "Document",
    "description": "Schema for document details.",
    "type": "object",
    "properties": {
        "totalCount": {"type": "number"},
        "lineItems": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "lineItemNumber": {"type": "number"},
                    "description": {"type": "string"},
                    "reference": {"type": "string"},
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
    "required": ["totalCount", "lineItems"]
}


basis_information_schema = {
    "title": "basisInformation",
    "description": "Schema for document basis information.",
    "type": "object",
    "properties": {
        "currency": {"type": "string"},
        "basis": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "author": {"type": "string"},
                    "documentDate": {"type": "string"},
                    "documentNumber": {"type": "string"},
                    "documentType": {"type": "string"},
                    "validityPeriod": {"type": "string"},
                    "paymentTerm": {"type": "string"},
                    "vat": {"type": "string"}
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


async def parse_visual_extraction(
    filename: str,
    chat_model: AzureChatOpenAI,
    page_chunk_size: int = DEFAULT_PAGE_CHUNK_SIZE,
):
    """Extract structured data by letting the model reason over the page images.

    The document is rendered to one image per page (preserving the full visual
    layout of the invoice/offer) and passed directly to the vision-capable model,
    replacing the previous Document Intelligence OCR-to-flat-text step.
    """
    try:
        logger.info("Rendering document to page images: %s", filename)
        images = await asyncio.to_thread(render_document_to_images, filename)

        if not images:
            raise ValueError(f"No pages could be rendered from {filename}")

        results = []

        # Step 1: Extract basis information from the first page(s).
        basis_model = chat_model.with_structured_output(basis_information_schema)
        basis_prompt = build_basis_info_prompt(images[: min(2, len(images))])
        basis_result = await asyncio.to_thread(basis_model.invoke, basis_prompt)
        results.append(basis_result)

        # Step 2: Extract line items, chunking by pages to respect context limits.
        line_item_model = chat_model.with_structured_output(json_schema)
        total_chunks = math.ceil(len(images) / page_chunk_size)
        offset = 0
        for chunk_number in range(total_chunks):
            start = chunk_number * page_chunk_size
            chunk_images = images[start:start + page_chunk_size]
            logger.info(f"Processing page chunk {chunk_number + 1}/{total_chunks}")
            prompt = build_line_items_prompt(chunk_images, offset)
            result = await asyncio.to_thread(line_item_model.invoke, prompt)
            results.append(result)
            if isinstance(result, dict):
                offset += len(result.get("lineItems", []))

        return results

    except Exception as e:
        logger.error(f"Error in parse_visual_extraction: {e}")
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


async def parse_enrich_chapter(json: str, chat_model: ChatOpenAI):
    try:
        logger.info("Starting parse_enrich_chapter")
        chapter_prompt = build_extraction_enrich_chapter_prompt(json)
        result = await asyncio.to_thread(chat_model.invoke, chapter_prompt, **params)
        return result
    except Exception as e:
        logger.error(f"Error in parse_enrich_chapter: {e}")
        raise
