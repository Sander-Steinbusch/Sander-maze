from langchain_core.messages import SystemMessage, HumanMessage


def build_extraction_prompt(document: str) -> list[SystemMessage | HumanMessage]:
    template = (
        # persona
        "Basis Information:"
        "Author: The company name."
        "Document Date: The date of the document."
        "Document Number: The reference number of the document."
        "Document Type: The type of document."
        "Currency: Identify the currency used in the document."
        "Total Count: Count the total number of line items."
        "Line Items: For each line item, extract:"
        "Description: The description of the item."
        "Extra Info: Any additional information( if available)."
        "Quantity: The quantity of the item."
        "Unit: The unit of measurement."
        "Price: The price per unit."
        "Reduction: percentage of reduction applied( if available)."
        "Price Reduction: The price after reduction( if available)."
        "Delivery: The delivery terms."
        "Chapter: Any chapter information( if available)."

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
        "\"priceReduction\": \"Price after Reduction\","
        "\"delivery\": \"Delivery Terms\","
        "\"chapter\": \"Chapter Information\"}"
        "// Repeat for each line item"
        "]"
        "}"
        
        "leave out the JSON markdown and answer in one JSON object"
        "Use the provided text to fill in the details accordingly."
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
