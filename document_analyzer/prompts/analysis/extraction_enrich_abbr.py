from langchain_core.messages import SystemMessage, HumanMessage


def build_extraction_enrich_abbr_prompt(document: str) -> list[SystemMessage | HumanMessage]:
    template = (
        # persona
        "you will get a text in json format."
        "look for all abbreviations and replace them with their Dutch full length counterpart."
        "for example: cm becomes centimeter, ml becomes milliliter etc"
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
