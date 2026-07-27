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
        "- Unit: the unit the price applies to (the pricing basis). Derive it "
        "from how the price is written: in '85,55 EUR/stuk', '12,40 €/m³' or "
        "'per lopende meter', the part after the currency symbol or after "
        "'per' IS the unit. Put only the numeric value in Price and that unit "
        "in Unit. If the document has a separate quantity/unit column, use "
        "that column instead.\n"
        "- Price (per unit)\n"
        "- Reduction (percentage, if available)\n"
        "- Price minus Reduction (unit price after reduction)\n"
        "- Delivery terms\n"
        "- Chapter (leave blank)\n\n"
        "Return a JSON object with:\n"
        "- lineItems: list of extracted items\n"
        "- totalCount: number of items extracted\n\n"
        "**Instructions:**\n"
        "- Only extract genuine priced line items; ignore page headers, footers and totals.\n"
        "- Create one line item per price occurrence in the document. Never "
        "merge two occurrences, even when description, unit and price are "
        "identical: repeated identical prices under different headings are "
        "separate line items.\n"
        "- A price line inherits context from the headings above it. Repeat "
        "that context in Extra Info for every line item under it, including "
        "technical specification blocks that appear several lines higher, "
        "not only the nearest post or item reference.\n"
        "- Always use the literal text only, do not paraphrase.\n"
        "- Never translate the text, use the original language.\n"
        "- Use the full visual layout of the pages to reason about the structure.\n"
        "- Make sure 'Price minus Reduction' only uses the unit price, not the total.\n"
        "- All numbers must be unformatted and use dots as decimal separators."
        "\n\n**Example of a non-tabular layout:**\n"
        "  MAASTYPE 80 x 100 - DRAADDIAMETER 3,00 mm\n"
        "  Post 278 - Korven 50 cm dik = 500 m³\n"
        "  4 x 1 x 0,5 m        85,55 EUR/stuk\n"
        "-> description: '4 x 1 x 0,5 m'\n"
        "   extraInfo: 'MAASTYPE 80 x 100 - DRAADDIAMETER 3,00 mm | "
        "Post 278 - Korven 50 cm dik = 500 m³'\n"
        "   quantity: ''\n"
        "   unit: 'stuk'\n"
        "   price: 85.55"
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
