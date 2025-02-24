from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompt_values import PromptValue
from langchain_core.prompts import ChatPromptTemplate

def build_extraction_prompt_with_schema(document: str) -> PromptValue:
    promptTemplate = ChatPromptTemplate.from_messages([
        ("system", "You will extract the following info from the provided document:"
                   "Basis Information:"
                   "Author: The company name."
                   "Document Date: The date of the document."
                   "Document Number: The reference number of the document."
                   "Document Type: The type of document."
                   "Currency: Identify the currency used in the document."
                   "Line Items: For each line item, extract:"
                   "Description: The description of the item."
                   "Extra Info: Any additional information( if available)."
                   "Quantity: The quantity of the item."
                   "Unit: The unit of measurement."
                   "Price: The price per unit."
                   "Reduction: percentage of reduction applied( if available)."
                   "Price minus Reduction: The unit price after reduction( if available)."
                   "Delivery: The delivery terms."
                   "Chapter: Any chapter information( if available)."
                   "Total Count: Count the total number of line items."
                   
                   "leave out the JSON markdown and answer in one JSON object"
                   "Use the provided text to fill in the details accordingly."
                   "At the end, count the number of line items again and double check the totalCount of line items."
         ),
        ("user", f"Extract the necessary info from the provided document:{document}")
    ])
    return promptTemplate.invoke({"document": document})

def build_extraction_prompt(document: str) -> list[SystemMessage | HumanMessage]:
    template = (
        # persona
        "Basis Information:"
        "Author: The company name."
        "Document Date: The date of the document."
        "Document Number: The reference number of the document."
        "Document Type: The type of document."
        "Currency: Identify the currency used in the document."        
        "Line Items: For each line item, extract:"
        "Description: The description of the item."
        "Extra Info: Any additional information( if available)."
        "Quantity: The quantity of the item."
        "Unit: The unit of measurement."
        "Price: The price per unit."
        "Reduction: percentage of reduction applied( if available)."
        "Price minus Reduction: The unit price after reduction( if available)."
        "Delivery: The delivery terms."
        "Chapter: Any chapter information( if available)."
        "Total Count: Count the total number of line items."

        "Format the extracted information as follows:"

        "{\"basis\": ["
        "{\"author\": \"Author Name\","
        "\"documentDate\": \"DD-MM-YYYY\","
        "\"documentNumber\": \"Document Number\","
        "\"documentType\": \"Document Type\"}],"
        "\"currency\": \"Currency\","
        "\"totalCount\": \"Number of line items\","
        "\"lineItems\": ["
        "{\"description\": \"Item Description\","
        "\"extraInfo\": \"Extra Information\","
        "\"quantity\": \"Quantity\","
        "\"unit\": \"Unit\","
        "\"price\": \"Price\","
        "\"reduction\": \"Reduction\","
        "\"priceMinusReduction\": \"Unit price after Reduction\","
        "\"delivery\": \"Delivery Terms\","
        "\"chapter\": \"Chapter Information\"}"
        "// Repeat for each line item"
        "]"
        "}"
        
        "leave out the JSON markdown and answer in one JSON object"
        "Use the provided text to fill in the details accordingly."
        "At the end, count the number of line items again and double check the totalCount of line items."
    )

    return [
        SystemMessage(
            content=template
        ),
        HumanMessage(
            content=[
                {"type": "text", "text": document},

            ]
        )
    ]
