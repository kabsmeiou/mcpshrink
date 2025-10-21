from pydantic import BaseModel, Field

# class for model_name, temperature, max_tokens
class ModelConfig(BaseModel):
    model_name: str = Field(..., description="Name of the model")
    temperature: float = Field(..., description="Temperature setting for the model")
    max_tokens: int = Field(..., description="Maximum tokens for the model response")
