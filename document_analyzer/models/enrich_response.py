from langchain.pydantic_v1 import BaseModel, Field

from document_analyzer.models import (
    descriptions
)

class Json(BaseModel):
    rawOutput: str = Field(
        description=descriptions.raw
    )