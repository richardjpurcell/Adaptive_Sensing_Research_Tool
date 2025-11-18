from pydantic import BaseModel, Field
from typing import Optional

class InitRunRequest(BaseModel):
    env_id: str
    fire_id: str
    run_name: str = "run"
    # timing
    dt_seconds: int = Field(3600, ge=1)         # 1 hour default
    horizon_steps: int = Field(24, ge=1)        # 24 frames
    # simple spread parameter for toy model
    spread_prob: float = Field(0.3, ge=0.0, le=1.0)

class InitRunResponse(BaseModel):
    run_id: str
    t: int = 0
    dt_seconds: int
    horizon_steps: int

class StepResponse(BaseModel):
    run_id: str
    t: int
    done: bool

class LatestResponse(BaseModel):
    run_id: str
    t_latest: int
