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
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "spec": {"type": "string"}
                },
                "required": ["id", "spec"]
            }
        },
        "lineItems": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "lineItemNumber": {"type": "number"},
                    "description": {"type": "string"},
                    "reference": {"type": "string"},
                    "sectionId": {"type": "string"},
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

# A chunk is only count-checked / retried when its own text layer clears the
# same threshold as the document level, and it gets at most this many attempts.
MAX_CHUNK_ATTEMPTS = 5


def count_price_occurrences(page_texts):
    """Count price occurrences across the given page texts. Used for both the
    per-chunk count check and the whole-document count check, so the two can
    never diverge."""
    return len(PRICE_PATTERN.findall("\n".join(page_texts)))


def _chunk_has_text_layer(chunk_texts):
    """True when this chunk carries a real text layer (same >100 chars/page
    threshold as the document level), i.e. a reliable price count is available."""
    if not chunk_texts:
        return False
    avg_chars = sum(len(t) for t in chunk_texts) / len(chunk_texts)
    return avg_chars > MIN_TEXT_LAYER_CHARS_PER_PAGE


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
    max_attempts_option = options.get("max_attempts", MAX_CHUNK_ATTEMPTS)

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
        # include_raw exposes finish_reason / token usage so early stops are
        # visible instead of assumed; the parsed schema result is under "parsed".
        line_item_model = chat_model.with_structured_output(json_schema, include_raw=True)
        total_chunks = math.ceil(len(images) / page_chunk_size)
        offset = 0
        line_items_per_chunk = []
        chunk_diagnostics = []
        total_attempts = 0
        for chunk_number in range(total_chunks):
            start = chunk_number * page_chunk_size
            chunk_images = images[start:start + page_chunk_size]
            # Slice the text layer on the same indices so it stays aligned.
            chunk_texts = page_texts[start:start + page_chunk_size] if page_texts else None

            # Only chunks with a real text layer get a reliable price count and
            # therefore a retry; scans run once (no vain triple runs).
            expected_prices = count_price_occurrences(chunk_texts) if _chunk_has_text_layer(chunk_texts) else None
            max_attempts = max_attempts_option if expected_prices is not None else 1

            logger.info(f"Processing page chunk {chunk_number + 1}/{total_chunks}")
            # Build the prompt once: every retry re-runs the SAME chunk with the
            # SAME start_index. offset only advances after a result is accepted.
            prompt = build_line_items_prompt(chunk_images, offset, chunk_texts)

            items_per_attempt = []
            best = {"parsed": None, "raw": None, "error": None, "count": -1}
            accepted = False
            for attempt in range(max_attempts):
                total_attempts += 1
                raw_result = await asyncio.to_thread(line_item_model.invoke, prompt)
                parsed = raw_result.get("parsed") if isinstance(raw_result, dict) else None
                raw_message = raw_result.get("raw") if isinstance(raw_result, dict) else None
                parsing_error = raw_result.get("parsing_error") if isinstance(raw_result, dict) else None
                count = len(parsed.get("lineItems", [])) if isinstance(parsed, dict) else 0
                items_per_attempt.append(count)

                if parsing_error:
                    logger.warning(
                        "Structured-output parsing error on chunk %d attempt %d for %s: %s",
                        chunk_number + 1, attempt + 1, filename, parsing_error,
                    )

                # Keep the attempt with the most line items as the fallback, and
                # accept immediately on a count match (or when there is no count).
                if count > best["count"] or (expected_prices is not None and count == expected_prices):
                    best = {"parsed": parsed, "raw": raw_message, "error": parsing_error, "count": count}
                if expected_prices is None or count == expected_prices:
                    accepted = True
                    break

            chunk_mismatch = expected_prices is not None and not accepted
            if chunk_mismatch:
                logger.warning(
                    "Chunk %d still mismatched after %d attempts for %s: expected %d, best %d",
                    chunk_number + 1, len(items_per_attempt), filename, expected_prices, best["count"],
                )

            parsed = best["parsed"]
            raw_message = best["raw"]
            parsing_error = best["error"]
            count = max(best["count"], 0)

            # Only the accepted (or best) attempt is used and advances the offset;
            # failed attempts never shift the numbering.
            results.append(parsed)
            line_items_per_chunk.append(count)
            offset += count

            finish_reason = None
            usage = None
            if raw_message is not None:
                finish_reason = (getattr(raw_message, "response_metadata", None) or {}).get("finish_reason")
                usage = getattr(raw_message, "usage_metadata", None) or None

            logger.info(
                "Chunk %d accepted after %d attempt(s) finish_reason=%s output_tokens=%s items=%d",
                chunk_number + 1, len(items_per_attempt), finish_reason,
                (usage or {}).get("output_tokens"), count,
            )

            chunk_diagnostics.append({
                "chunk": chunk_number + 1,
                "attempts": len(items_per_attempt),
                "items_per_attempt": items_per_attempt,
                "expected_price_lines": expected_prices,
                "finish_reason": finish_reason,
                "input_tokens": (usage or {}).get("input_tokens"),
                "output_tokens": (usage or {}).get("output_tokens"),
                "output_token_details": (usage or {}).get("output_token_details"),
                "line_items": count,
                "parsing_error": str(parsing_error) if parsing_error else None,
            })

        # Document-level count check (only when a text layer was actually sent).
        # A persistent mismatch flags the merged result via a sentinel that
        # merge_extraction_results turns into needsReview / reviewReason.
        line_item_count = sum(line_items_per_chunk)
        price_occurrence_count = None
        if page_texts:
            price_occurrence_count = count_price_occurrences(page_texts)
            if price_occurrence_count != line_item_count:
                logger.warning(
                    "Price-occurrence count (%d) does not match extracted line "
                    "items (%d) for %s after retries",
                    price_occurrence_count, line_item_count, filename,
                )
                results.append({"_review": {
                    "needsReview": True,
                    "reviewReason": {
                        "expectedPriceLines": price_occurrence_count,
                        "extractedLineItems": line_item_count,
                    },
                }})

        diagnostics = {
            "options": {
                "page_chunk_size": page_chunk_size,
                "text_layer": text_layer_mode,
                "debug": options.get("debug", False),
                "max_attempts": max_attempts_option,
            },
            "text_layer_chars_per_page": text_layer_chars,
            "text_layer_sent": page_texts is not None,
            "num_chunks": total_chunks,
            "total_attempts": total_attempts,
            "line_items_per_chunk": line_items_per_chunk,
            "chunks": chunk_diagnostics,
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
        "sections": [],
        "lineItems": [],
        "currency": None,
        "totalCount": 0
    }

    basis_added = False  # Flag to ensure basis is only added once
    chunk_index = 0

    for result in results:
        if not isinstance(result, dict):
            continue

        # Review sentinel: a persistent count mismatch after retries. Surface it
        # as a real, always-present result field (not stripped like _diagnostics).
        if "_review" in result:
            review = result["_review"]
            if review.get("needsReview"):
                merged["needsReview"] = True
                merged["reviewReason"] = review.get("reviewReason")
            continue

        # Add basis only from the first valid chunk
        if not basis_added and "basis" in result:
            merged["basis"].extend(result["basis"])
            basis_added = True
            if not merged["currency"] and result.get("currency"):
                merged["currency"] = result["currency"]
            continue

        # Line-item chunk. Each chunk numbers its sections from s1, so prefix
        # them per chunk (c1-s1, c2-s1, ...) to avoid collisions, and rewrite
        # the sectionId on this chunk's line items to match. Sections are never
        # deduplicated on text: an identical block in two chunks stays twice.
        chunk_index += 1
        prefix = f"c{chunk_index}-"
        id_map = {}
        for section in result.get("sections", []):
            old_id = section.get("id")
            new_id = f"{prefix}{old_id}" if old_id is not None else old_id
            if old_id is not None:
                id_map[old_id] = new_id
            merged["sections"].append({**section, "id": new_id})

        for item in result.get("lineItems", []):
            section_id = item.get("sectionId")
            if section_id in id_map:
                item = {**item, "sectionId": id_map[section_id]}
            merged["lineItems"].append(item)

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
