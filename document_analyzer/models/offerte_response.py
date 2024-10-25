from langchain.pydantic_v1 import BaseModel, Field
from typing import List

from document_analyzer.models import (
    BasisInfo,
    LineItem,
    descriptions,
)

class Offerte(BaseModel):
    basis: List[BasisInfo] = Field(
        description=descriptions.basis
    )
    currency: str = Field(
        description=descriptions.currency
    )
    totalCount:int = Field(
        description=descriptions.totalCount
    )
    lineItems: List[LineItem] = Field(
        description=descriptions.items
    )
    rawOutput: str = Field(
        description=descriptions.raw
    )