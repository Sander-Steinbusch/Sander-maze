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
        description="conditions and information pertaining the delivery of goods and/or service."
    )
    
