import logging

from langchain_core.prompt_values import PromptValue
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)

def build_extraction_prompt_with_schema(document: str, chunk_number: int, chunk_size: int) -> PromptValue:
    start_item = (chunk_number - 1) * chunk_size + 1
    end_item = chunk_number * chunk_size

    logger.info(f"start item: {start_item}")
    logger.info(f"end item: {end_item}")

    promptTemplate = ChatPromptTemplate.from_messages([
        ("system",
         f"You are a document analysis assistant. Your task is to extract structured pricing data from documents such as invoices, offers, and price lists.\n\n"
         f"---\n"
         f"**Extract the following information:**\n"
         f"**Basis Information (only once, from the full document):**\n"
         f"- Author: The company name.\n"
         f"- Document Date: The date of the document. \n"
         f"- Document Number: The reference number of the document.\n"
         f"- Document Type: The type of document.\n"
         f"- Currency: Identify the currency used in the document.\n"
         f"- Include a field called `processedRange` in the output, indicating the range of line items you processed (e.g., 'Items 1–25').\n\n"
         f"**Line Items (starting from item {start_item} up to and including item {end_item}):**\n"
         f"For each line item, extract:\n"
         f"- lineItemNumber: The sequential number of the item, starting from {start_item}.\n"
         f"- Description\n"
         f"- Extra Info (if available)\n"
         f"- Quantity\n"
         f"- Unit (use symbols, e.g., 'm' for meter)\n"
         f"- Price (per unit)\n"
         f"- Reduction (percentage, if available)\n"
         f"- Price minus Reduction (unit price after reduction)\n"
         f"- Delivery terms\n"
         f"- Chapter (leave blank)\n\n"
         f"**Instructions:**\n"
         f"- You must extract exactly {chunk_size} line items, unless there are fewer remaining in the document.\n"
         f"- Only extract line items from item {start_item} up to and including item {end_item}.\n"         
         f"- If there are no more line items in this range, return an empty list for `lineItems` and set `totalCount` to 0.\n"
         f"- Include a field called `processedRange` in the output, indicating the range of line items you processed (e.g., 'Items {start_item}–{end_item}').\n"
         f"- Leave out the JSON markdown and answer in one JSON object.\n"
         f"- Use the full document text to reason about the structure.\n"
         f"- Make sure 'Price minus Reduction' only uses the unit price, not the total.\n"
         f"- All numbers must be unformatted and use dots as decimal separators.\n"
         f"- All dates must be formatted as DD-MM-YYYY.\n"
         f"- Documents type is either 'Factuur' or 'Offerte', if not one of those leave it blank.\n"
         f"- At the end, include the number of line items extracted as 'totalCount'.\n"
         f"- This is chunk {chunk_number}. Continue from where the previous chunk ended."
        ),
        ("user", f"Extract the necessary info from the following document:\n\n{document}")
    ])
    return promptTemplate.invoke({"document": document})


def build_basis_info_prompt(document: str) -> PromptValue:
    promptTemplate = ChatPromptTemplate.from_messages([
        ("system",
         f"You are a document analysis assistant. Your task is to analyze the following document and extract the basis information.\n"
         f"You will never translate anything and use the original document language.\n\n"
         f"**Extract the following information:**\n"
         f"**Basis Information (only once, from the full document):**\n"
         f"- Author: The company name.\n"
         f"- Document Date: The date of the document, format as DD-MM-YYYY.\n"
         f"- Document Number: The reference number of the document.\n"
         f"- Document Type: The type of document.\n"
         f"- Currency: Identify the currency used in the document.\n"
         f"**Instructions:**\n"
         f"- Always use the literal text, do not paraphrase\n"
         f"- Never translate the text, use the original language.\n"
         f"- Leave out the JSON markdown and answer in one JSON object.\n"
         f"- Use the full document text to reason about the structure.\n"
         f"- All dates must be formatted as DD-MM-YYYY.\n"
         f"- Documents type is either 'Factuur' or 'Offerte', if not one of those leave it blank.\n"
        ),
        ("user", f"Extract the necessary info from the following document:\n\n{document}")
    ])
    return promptTemplate.invoke({"document": document})


def build_table_chunk_prompt(table_rows: list, chunk_number: int, chunk_size: int) -> PromptValue:
    start_index = (chunk_number - 1) * chunk_size
    end_index = chunk_number * chunk_size
    chunk = table_rows[start_index:end_index]

    table_text = "\n".join(["\t".join(row) for row in chunk])

    promptTemplate = ChatPromptTemplate.from_messages([
        ("system",
         f"You are a document analysis assistant. You will extract structured line item data from a table.\n"
         f"You will never translate anything and use the original document language.\n"
         f"You will never add anything to the data, only use the literal text and data you found.\n\n"
         f"Mostly, each row represents a line item and contains fields like description, quantity, unit, and price.\n"
         f"It is possible a line item will span multiple rows.\n"
         f"Extract the following fields for each row, leave the field blank if you can't find anything for a certain field:\n"
         f"- lineItemNumber (starting from {start_index + 1})\n"
         f"- Description\n"
         f"- Extra Info (if available)\n"
         f"- Quantity\n"
         f"- Unit (use symbols, e.g., 'm' for meter)\n"
         f"- Price (per unit)\n"
         f"- Reduction (percentage, if available)\n"
         f"- Price minus Reduction (unit price after reduction)\n"
         f"- Delivery terms\n"
         f"- Chapter (leave blank)\n\n"
         f"Return a JSON object with:\n"
         f"- lineItems: list of extracted items\n"
         f"- totalCount: number of items extracted\n"
         f"- processedRange: 'Items {start_index + 1}–{min(end_index, len(table_rows))}'"
         f"**Instructions:**\n"
         f"- Always use the literal text only, do not paraphrase\n"         
         f"- Never translate the text, use the original language.\n"         
         f"- Leave out the JSON markdown and answer in one JSON object.\n"
         f"- Use the full document text to reason about the structure.\n"
         f"- Make sure 'Price minus Reduction' only uses the unit price, not the total.\n"
         f"- All numbers must be unformatted and use dots as decimal separators.\n"
        ),
        ("user", f"Here are the table rows:\n\n{table_text}")
    ])
    return promptTemplate.invoke({"table_text": table_text})