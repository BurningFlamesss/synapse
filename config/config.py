import os
from pathlib import Path

from pydantic import BaseModel, Field

class ModelConfig(BaseModel):
    name: str = "openai/gpt-oss-120b:free"
    temperature: float = Field(default=1, ge=0.0, le=2.0)
    context_window: int | None = None

class Config(BaseModel):
    model: ModelConfig = Field(default_factory=ModelConfig)
    cwd: Path = Field(default_factory=Path.cwd)
    max_turns: int = 100
    max_tool_output_tokens: int = 50_000
    
    developer_instructions: str | None = None
    user_instructions: str | None = None
    
    debug: bool = False
    
    @property
    def api_key(self) -> str | None:
        return os.environ.get("API_KEY")
    
    