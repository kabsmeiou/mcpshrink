from typing import Optional, Any
from pydantic import BaseModel

class ExpandedRecord(BaseModel):
    original_template: str
    expanded_template: str
    tool_name: str
    mcp_server: Optional[Any] = None
