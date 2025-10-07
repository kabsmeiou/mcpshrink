from pydantic import BaseModel, Field


class Tool(BaseModel):
    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Description of the tool")
    parameters: dict = Field(default_factory=dict, description="Parameters for the tool")
    output_schema: dict | None = Field(default=None, description="Output schema for the tool")