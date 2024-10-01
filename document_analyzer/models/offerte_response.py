from langchain.pydantic_v1 import BaseModel, Field
from typing import List

from document_analyzer.models import (
    BasisInfo,
    LineItem,
    descriptions
)

class Offerte(BaseModel):
    basis: List[BasisInfo] = Field(
        description=descriptions.basis
    )
    totaalIncl: str = Field(
        description=descriptions.total
    )
    currency: str = Field(
        description=descriptions.currency
    )
    lineItems: List[LineItem] = Field(
        description=descriptions.items
    )