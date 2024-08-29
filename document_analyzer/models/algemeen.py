from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional

class Algemeen(BaseModel):
    auteur: str = Field(
        description="name of a company or person that is the sender of the document"
    )
    leveringsconditie: Optional[str] = Field(
        description="conditions and information partaining the delivery of goods and/or service "
    )
    totaalIncl: float = Field(
        description="total amount issued including taxes of the offer without the currency symbol"
    )
    munteenheid: str = Field(
        description="the currency in which all the prices are issued"
    )