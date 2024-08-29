from langchain.pydantic_v1 import BaseModel, Field

class Lijnitem(BaseModel):
    omschrijving: str = Field(
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
            "additional info about the good and/or service provided by the company."
            "Often in a separate line, area or table cell."
            "Sometimes this is placed between brackets or parenthesis after the initial description."
        )
    )
    aantal: str = Field(
        description=(
            "the quantity of the good and/or service provided by the company."
            "Often called: aantal or hoeveelheid."
        )
    )
    eenheid: str = Field(
        description="the unit of measure of the good and/or service provided by the company."
    )
    prijs: str = Field(
        description=(
            "the unit price of the good and/or service provided by the company."
            "this can be the same as the total amount when the quantity of the good is one."
            "usually called: eenheidsprijs, eenh. prijs, unit price, eenh. pr."
            "The decimal sign is always a comma, and needs to be replaced by a comma when it isn't."
            "The thousands separator is always a dot, and need to be replaced by a dot when it isn't."
        )
    )
    korting: str = Field(
        description=(
            "A reduction, usually in the form of a percentage."
            "If there is none to be found, or if it's o, return an empty string."
        )
    )
    prijsKorting: str = Field(
        description=(
            "the unit price of the good and/or service provided by the company."
            "reduced with the reduction found in the document."
            "this reduction can be specific per unit price, but can also apply on the whole document."
            "Please calculate this yourself with the found reduction and unit price, since this price is never present in the document."
            "Only execute this when there is a reduction found in the document."
            "if the calculated number is the same as the price, return an empty string here."
        )    
    )