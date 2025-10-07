from pydantic import BaseModel, Field
from typing import Dict, Any

class Tool(BaseModel):
    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Description of the tool")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the tool")
    output_schema: Dict[str, Any] | None = Field(default=None, description="Output schema for the tool")