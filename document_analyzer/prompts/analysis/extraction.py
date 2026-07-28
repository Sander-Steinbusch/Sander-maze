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
        "- Validity Period: how long the offer/quotation remains valid, "
        "taken literally from the document.\n"
        "- Payment Term: the payment condition, taken literally from the "
        "document.\n"
        "- VAT: the VAT statement or rate as written in the document.\n"
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
    images: list[str], start_index: int = 0, page_texts: list[str] | None = None
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
        "- Reference: the post or item number the price line belongs to, "
        "e.g. 'Post 278'. Take it from the nearest such heading above the "
        "price line. Every new post or item number starts a new context: "
        "never carry an earlier reference into a later line item, and never "
        "put more than one reference in a single line item.\n"
        "- Section Id: the id of the specification block that governs this "
        "price line, referring to the sections list described below. Never "
        "repeat the specification text itself on the line item.\n"
        "- Extra Info: only the descriptive text of this line's own post "
        "heading, e.g. 'Korven 50 cm dik = 500 m³'. This resets at every new "
        "post or item number. Never put text from another post here, and "
        "never put the specification block here.\n"
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
        "- sections: list of the technical specification blocks in the "
        "document. A specification block is a heading block stating product "
        "type, mesh type, coating, wire diameter and similar, and it governs "
        "every price line below it, across several posts, until a new "
        "specification block starts. Give each one an id 's1', 's2', ... in "
        "document order, and its verbatim text in 'spec'. List each block "
        "once, no matter how many line items refer to it.\n"
        "- lineItems: list of extracted items, each including its reference, "
        "its sectionId and the fields listed above\n"
        "- totalCount: number of items extracted\n\n"
        "**Instructions:**\n"
        "- Only extract genuine priced line items; ignore page headers, footers and totals.\n"
        "- First count every line in the document that carries a price. The "
        "number of line items you return MUST equal that count, and "
        "totalCount MUST equal it too. Two lines with identical text and an "
        "identical price are still two separate line items: never collapse "
        "them, and never combine their headings into one Extra Info.\n"
        "- Always use the literal text only, do not paraphrase.\n"
        "- Never translate the text, use the original language.\n"
        "- Use the full visual layout of the pages to reason about the structure.\n"
        "- Make sure 'Price minus Reduction' only uses the unit price, not the total.\n"
        "- All numbers must be unformatted and use dots as decimal separators."
        "\n\n**Example: three identical price lines under three different "
        "posts are three line items, not one.**\n"
        "  Post 282: MATRASSEN 5 x 7 - 25 cm dik\n"
        "  3 x 2 x 0,3 m        73,75 EUR/stuk\n"
        "  Post 283: MATRASSEN 6 x 8 - 17 cm dik\n"
        "  3 x 2 x 0,3 m        73,75 EUR/stuk\n"
        "-> Two line items. Both have description '3 x 2 x 0,3 m', unit "
        "'stuk' and price 73.75, but reference 'Post 282' and 'Post 283' "
        "respectively. Never a single item that mentions both posts."
    )

    content = [
        {
            "type": "text",
            "text": "Extract all line items from the following page image(s):",
        },
        *_image_blocks(images),
    ]

    if page_texts:
        content.append(
            {
                "type": "text",
                "text": (
                    "Below is the verbatim text layer of the same pages, in "
                    "reading order. Use it to determine HOW MANY price lines "
                    "there are: every line carrying a price is one line item, "
                    "even when several such lines are textually identical. Use "
                    "the page images to determine the structure: which heading "
                    "and which specification block belongs to which price line. "
                    "Where the two disagree about the number of price lines, "
                    "the text layer wins.\n\n"
                    + "\n\n".join(page_texts)
                ),
            }
        )

    return [
        SystemMessage(content=system),
        HumanMessage(content=content),
    ]
