from pydantic import BaseModel, Field
from typing import List
from .tools import Tool


class TemplateQuery(BaseModel):
    tool: Tool = Field(..., description="The tool for which the template is generated")
    template: str = Field(..., description="The generated template query")
    mcp_server: str | None = Field(default=None, description="Optional MCP server name the tool belongs to")


class GeneratedQuery(BaseModel):
    template: TemplateQuery = Field(..., description="The template query used to generate this query")
    expanded_query: str = Field(..., description="The expanded query based on the template")


class AugmentedQuery(BaseModel):
    generated_query: GeneratedQuery = Field(..., description="The generated query")
    augmented_query: str = Field(..., description="The augmented query")
    augmentation_technique: str = Field(..., description="The augmentation technique used")
