from langchain.pydantic_v1 import BaseModel, Field
from typing import List

from document_analyzer.models import (
    BasisInfo,
    Lijnitem,
    descriptions
)

class Offerte(BaseModel):
    basis: List[BasisInfo] = Field(
        description=descriptions.basis
    )
    totaalIncl: str = Field(
        description=descriptions.totaalIncl
    )
    munteenheid: str = Field(
        description=descriptions.munteenheid
    )
    lijnitems: List[Lijnitem] = Field(
        description=descriptions.lijnitems
    )
    rawOutput: str = Field(
        description=descriptions.raw
    )