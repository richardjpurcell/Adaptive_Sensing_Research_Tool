from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict

class Grid(BaseModel):
    H: int
    W: int
    cell_m: int

class EnvironmentManifest(BaseModel):
    name: str
    grid: Grid
    wind: Dict[str, float] = Field(default_factory=dict)
    seed: int = 0
    env_id: Optional[str]

class FireManifest(BaseModel):
    name: str
    ignitions: Dict[str, object] = Field(default_factory=dict)
    model: Dict[str, object] = Field(default_factory=dict)
    seed: int = 0
    fire_id: Optional[str]

class SensorsManifest(BaseModel):
    name: str
    fleet: Dict[str, object] = Field(default_factory=dict)
    seed: int = 0
    sensors_id: Optional[str]

class RunConfig(BaseModel):
    policy: Literal["greedy","uncertainty","thompson","rl"] = "thompson"
    budget: Dict[str, object] = Field(default_factory=dict)
    impairments: Dict[str, float] = Field(default_factory=lambda: {"epsilon":0.0,"rho":0.0,"tau":0.0})
    alignment: Literal["calibration","registration_ops"] = "calibration"
    steps: int = 100
    seed: int = 0
    run_id: Optional[str]
