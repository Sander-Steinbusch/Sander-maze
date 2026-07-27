import asyncio
import logging
import math
import re

from langchain_openai import AzureChatOpenAI
from langchain_openai.chat_models import ChatOpenAI

from document_analyzer.prompts.analysis.extraction import (
    build_basis_info_prompt,
    build_line_items_prompt,
)
from document_analyzer.prompts.analysis.extraction_enrich_chapter import (
    build_extraction_enrich_chapter_prompt,
)
from document_analyzer.tools.pdf_images import (
    extract_text_layer,
    render_document_to_images,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Number of page images sent to the model per line-item extraction call. Chunking
# by pages keeps large documents within the model's context window while still
# giving the model the full visual context of each page it reasons over.
DEFAULT_PAGE_CHUNK_SIZE = 4

# A text layer with fewer than this many characters per page (on average) is
# treated as a scan: nothing useful to send, so behaviour is left unchanged.
MIN_TEXT_LAYER_CHARS_PER_PAGE = 100

# Matches a price occurrence such as "73,75 EUR" or "85.55 €". Used only as a
# heuristic count check against the number of extracted line items.
PRICE_PATTERN = re.compile(r"\d+[.,]\d{2}\s*(?:EUR|€)")

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
                    "sectionSpec": {"type": "string"},
                    "extraInfo": {"type": "string"},
                    "quantity": {"type": ["number", "string"]},
                    "unit": {"type": "string"},
                    "price": {"type": "number"},
                    "reduction": {"type": "string"},
                    "priceMinusReduction": {"type": ["number", "string"]},
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
    options: dict | None = None,
):
    """Extract structured data by letting the model reason over the page images.

    The document is rendered to one image per page (preserving the full visual
    layout of the invoice/offer) and passed directly to the vision-capable model,
    replacing the previous Document Intelligence OCR-to-flat-text step.

    ``options`` selects run variants (page_chunk_size, text_layer, debug). Returns
    a ``(results, diagnostics)`` tuple; ``diagnostics`` is always computed and the
    caller decides whether to surface it.
    """
    options = options or {}
    page_chunk_size = options.get("page_chunk_size", DEFAULT_PAGE_CHUNK_SIZE)
    text_layer_mode = options.get("text_layer", "off")

    try:
        logger.info("Rendering document to page images: %s", filename)
        images = await asyncio.to_thread(render_document_to_images, filename)

        if not images:
            raise ValueError(f"No pages could be rendered from {filename}")

        # Optional: read the embedded text layer (no OCR). Only send it along when
        # it holds real text; a scan falls through and behaviour is unchanged.
        page_texts = None
        text_layer_chars = []
        if text_layer_mode == "auto":
            page_texts_all = await asyncio.to_thread(extract_text_layer, filename)
            text_layer_chars = [len(t) for t in page_texts_all]
            avg_chars = sum(text_layer_chars) / len(page_texts_all) if page_texts_all else 0
            if avg_chars > MIN_TEXT_LAYER_CHARS_PER_PAGE:
                page_texts = page_texts_all

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
        line_items_per_chunk = []
        for chunk_number in range(total_chunks):
            start = chunk_number * page_chunk_size
            chunk_images = images[start:start + page_chunk_size]
            # Slice the text layer on the same indices so it stays aligned.
            chunk_texts = page_texts[start:start + page_chunk_size] if page_texts else None
            logger.info(f"Processing page chunk {chunk_number + 1}/{total_chunks}")
            prompt = build_line_items_prompt(chunk_images, offset, chunk_texts)
            result = await asyncio.to_thread(line_item_model.invoke, prompt)
            results.append(result)
            count = len(result.get("lineItems", [])) if isinstance(result, dict) else 0
            line_items_per_chunk.append(count)
            offset += count

        # Heuristic count check (only when a text layer was actually sent).
        line_item_count = sum(line_items_per_chunk)
        price_occurrence_count = None
        if page_texts:
            price_occurrence_count = len(PRICE_PATTERN.findall("\n".join(page_texts)))
            if price_occurrence_count != line_item_count:
                logger.warning(
                    "Price-occurrence count (%d) does not match extracted line "
                    "items (%d) for %s",
                    price_occurrence_count, line_item_count, filename,
                )

        diagnostics = {
            "options": {
                "page_chunk_size": page_chunk_size,
                "text_layer": text_layer_mode,
                "debug": options.get("debug", False),
            },
            "text_layer_chars_per_page": text_layer_chars,
            "text_layer_sent": page_texts is not None,
            "num_chunks": total_chunks,
            "line_items_per_chunk": line_items_per_chunk,
            "price_occurrence_count": price_occurrence_count,
            "line_item_count": line_item_count,
        }

        return results, diagnostics

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

    # totalCount is the number of items we actually merged, not the model's
    # (per-chunk) self-report.
    merged["totalCount"] = len(merged["lineItems"])

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
