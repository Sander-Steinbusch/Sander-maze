import logging

from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


def _image_blocks(images: list[str]) -> list[dict]:
    return [{"type": "image_url", "image_url": {"url": uri}} for uri in images]


def build_basis_info_prompt(images: list[str]) -> list[SystemMessage | HumanMessage]:
    system = (
        "You are a document analysis assistant. You are given the page images of an "
        "invoice or offer and must extract the basis (header) information.\n"
        "You will never translate anything and use the original document language.\n\n"
        "**Extract the following information:**\n"
        "**Basis Information (only once, from the whole document):**\n"
        "- Author: The company name that issued the document.\n"
        "- Document Date: The date of the document, format as DD-MM-YYYY.\n"
        "- Document Number: The reference number of the document.\n"
        "- Document Type: The type of document.\n"
        "- Currency: Identify the currency used in the document.\n"
        "**Instructions:**\n"
        "- Always use the literal text, do not paraphrase.\n"
        "- Never translate the text, use the original language.\n"
        "- Use the full visual layout of the pages to reason about the structure.\n"
        "- All dates must be formatted as DD-MM-YYYY.\n"
        "- Document type is either 'Factuur' or 'Offerte', if not one of those leave it blank."
    )

    return [
        SystemMessage(content=system),
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "Extract the basis information from the following page image(s):",
                },
                *_image_blocks(images),
            ]
        ),
    ]


def build_line_items_prompt(
    images: list[str], start_index: int = 0
) -> list[SystemMessage | HumanMessage]:
    system = (
        "You are a document analysis assistant. You are given the page images of an "
        "invoice or offer and must extract the structured line item (pricing) data.\n"
        "You will never translate anything and use the original document language.\n"
        "You will never add anything to the data, only use the literal text and data "
        "that is visible in the document.\n\n"
        "Each line item usually represents a priced good or service and contains fields "
        "such as description, quantity, unit and price. A single line item can span "
        "multiple visual rows.\n"
        "Extract the following fields for each line item, leave a field blank if you "
        "cannot find anything for it:\n"
        f"- lineItemNumber (continue the sequential numbering starting from {start_index + 1})\n"
        "- Description\n"
        "- Extra Info (if available)\n"
        "- Quantity\n"
        "- Unit (use symbols, e.g. 'm' for meter)\n"
        "- Price (per unit)\n"
        "- Reduction (percentage, if available)\n"
        "- Price minus Reduction (unit price after reduction)\n"
        "- Delivery terms\n"
        "- Chapter (leave blank)\n\n"
        "Return a JSON object with:\n"
        "- currency: the currency used in the document\n"
        "- lineItems: list of extracted items\n"
        "- totalCount: number of items extracted\n\n"
        "**Instructions:**\n"
        "- Only extract genuine priced line items; ignore page headers, footers and totals.\n"
        "- Always use the literal text only, do not paraphrase.\n"
        "- Never translate the text, use the original language.\n"
        "- Use the full visual layout of the pages to reason about the structure.\n"
        "- Make sure 'Price minus Reduction' only uses the unit price, not the total.\n"
        "- All numbers must be unformatted and use dots as decimal separators."
    )

    return [
        SystemMessage(content=system),
        HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "Extract all line items from the following page image(s):",
                },
                *_image_blocks(images),
            ]
        ),
    ]
