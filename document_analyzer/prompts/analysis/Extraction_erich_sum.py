from langchain_core.messages import SystemMessage, HumanMessage


def build_extraction_enrich_sum_prompt(document: str) -> list[SystemMessage | HumanMessage]:
    template = (
        # persona
        "you will get a text in json format."
        "inside this json there will be an array called lineItems"
        "When the objects inside this array are identical, merge them together and sum their quantity"
        "leave out the JSON markdown and answer in one JSON object"
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
