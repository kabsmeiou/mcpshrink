from pydantic import BaseModel, Field
from typing import List
from .configs import ModelConfig


# this is the input to the teacher extraction service
# each record for the teacher will consist of:
# id, query, is_augmented(bool), technique(str | None), 
# tool_name, mcp_server (str | None)
class TeacherPrompt(BaseModel):
    id: int = Field(..., description="Unique identifier for the query")
    query: str = Field(..., description="The query string")
    is_augmented: bool = Field(..., description="Whether the query is augmented")
    augmentation_technique: str | None = Field(..., description="The technique used for augmentation")
    tool_name: str = Field(..., description="The name of the tool used")
    mcp_server: str | None = Field(..., description="The MCP server used")


# this is the output from the teacher extraction service
class StudentDataset(BaseModel):
    id: int = Field(..., description="Unique identifier for the record")
    query: TeacherPrompt = Field(..., description="The original teacher prompt")
    response: str = Field(..., description="The response from the teacher model")
    tool_calls: List[str] = Field(..., description="List of tool calls made by the teacher model in order")
    model_config: ModelConfig = Field(..., description="Configuration of the model used for extraction")
    