from langchain.pydantic_v1 import BaseModel, Field
from datetime import date

class BasisInfo(BaseModel):
    auteur: str = Field(
        description="name of a company that is the sender of the document"
    )
    datum: date = Field(
        description="the date at which the quotation was issued or sent"
    )
    documentNummer: str = Field(
        description="a unique identifier or reference for the quotation"
    )
    typeDocument: str = Field(
        description="Type of invoice. usually called offerte or factuur"
    )
    leveringsconditie: str = Field(
        description=(
            "conditions pertaining the delivery of goods and/or service."
            "these are often not directly written in the document but have to be distilled from the delivery information"
            "Please asses which of the following options is most likely for the given document. "
            "Levering op de werf"
            "Niet van toepassing"
            "Af fabriek - transport ten laste van de koper"
            "Levering op de werf"
            "Onbekend"
                     )
    )
    
