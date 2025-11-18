from pydantic import BaseModel, Field
from typing import Optional, Literal

class BeliefPreviewRequest(BaseModel):
    env_id: str
    prior: Literal["uniform"] = "uniform"
    prior_strength: float = Field(1.0, ge=0.0)

class FieldImageParams(BaseModel):
    cmap: str = "viridis"
    vmin: float = 0.0
    vmax: float = 1.0
    quality: Literal["fast", "pub"] = "fast"
