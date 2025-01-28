from pydantic import BaseModel, Field
from datetime import date

class BasisInfo(BaseModel):
    author: str = Field(
        description="name of a company that is the sender of the document"
    )
    documentDate: date = Field(
        description="the date at which the quotation was issued or sent"
    )
    documentNumber: str = Field(
        description="a unique identifier or reference for the quotation"
    )
    documentType: str = Field(
        description="Type of invoice. usually called offerte or factuur"
    )