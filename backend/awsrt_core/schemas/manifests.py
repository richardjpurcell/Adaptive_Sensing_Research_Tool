from __future__ import annotations
from pydantic import BaseModel, Field, PositiveInt, model_validator
from typing import Optional, List, Literal

class GridSpec(BaseModel):
    H: PositiveInt
    W: PositiveInt
    cell_size: float = Field(..., gt=0.0, description="meters")
    crs_code: str = "EPSG:32612"

class EnvironmentManifest(BaseModel):
    env_id: str
    grid: GridSpec
    seed: int = 0
    terrain_elev_path: Optional[str] = None
    feasibility_mask_path: Optional[str] = None

class IgnitionCell(BaseModel):
    row: int
    col: int

class IgnitionSpec(BaseModel):
    type: Literal["point"] = "point"
    locations: List[IgnitionCell]
    t0: int = 0

    @model_validator(mode="after")
    def non_empty(self):
        if not self.locations:
            raise ValueError("Ignitions must contain at least one location.")
        return self

class FireManifest(BaseModel):
    fire_id: str
    env_id: str
    ignitions: IgnitionSpec
    model: str = "E2_base"
    seed: int = 0
