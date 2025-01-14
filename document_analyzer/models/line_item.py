from langchain.pydantic_v1 import BaseModel, Field

class LineItem(BaseModel):
    description: str = Field(
        description=(
            "description of a good and/or a service provided by the company."
            "this can span multiple lines."
            "sometimes it's a full sentence."
            "this means that you cannot mix up sentences."
            "Information regarding the location has to be left out."
            )
    )
    extraInfo: str = Field(
        description=(
            "additional info about the good and/or service."
            "Often on a separate line. Or in a separate area or table cell."
            "Sometimes this is placed between brackets or parenthesis after the initial description."
            "Don't include delivery details."
            "If you don't find anything leave this empty"
        )
    )
    quantity: str = Field(
        description=(
            "the quantity of the good and/or service provided by the company."
            "Often called: aantal or hoeveelheid."
        )
    )
    unit: str = Field(
        description="the unit of measure of the good and/or service provided by the company."
    )
    price: str = Field(
        description=(
            "the unit price of the good and/or service provided by the company."
            "this can be the same as the total amount when the quantity of the good is one."
            "usually called: eenheidsprijs, eenh. prijs, unit price, eenh. pr."
        )
    )
    reduction: str = Field(
        description=(
            "A reduction, usually in the form of a percentage."
            "If there is none to be found, or if it's 0, return an empty string."
        )
    )
    priceReduction: str = Field(
        description=(
            "the unit price of the good and/or service provided by the company."
            "reduced with the reduction found in the document."
            "this reduction can be specific per unit price, but can also apply on the whole document."
            "Please calculate this yourself with the found reduction and unit price, since this price is never present in the document."
            "Only execute this when there is a reduction found in the document."
            "if the calculated number is the same as the price, return an empty string here."
        )    
    )
    delivery: str = Field(
        description=(
            "conditions pertaining the delivery of goods and/or service."
            "these are often not directly written in the document but have to be distilled from the delivery information"
            "Please assess which of the following options is most likely for the given document. "
            "Levering op de werf"
            "Niet van toepassing"
            "Af fabriek - transport ten laste van de koper"
            "Levering op de werf"
            "Onbekend"
        )
    )
    chapter: str = Field(
        description= "empty field"
    )