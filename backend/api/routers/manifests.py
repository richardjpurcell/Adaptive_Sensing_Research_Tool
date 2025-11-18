# backend/api/routers/manifests.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from awsrt_core.schemas.manifests import GridSpec, IgnitionSpec, EnvironmentManifest, FireManifest
from awsrt_core.io.manifests import save_environment, save_fire, load_environment
from awsrt_core.io.paths import MANIFESTS

router = APIRouter()

# ---------- Request models ----------

class NewEnvironment(BaseModel):
    grid: GridSpec
    seed: int = 0
    terrain_elev_path: str | None = None
    feasibility_mask_path: str | None = None

class NewFire(BaseModel):
    env_id: str
    ignitions: IgnitionSpec
    model: str = "E2_base"
    seed: int = 0

# ---------- Response models (for nice OpenAPI) ----------

class EnvRow(BaseModel):
    env_id: str
    H: int
    W: int
    cell_size: float
    crs_code: str

class FireRow(BaseModel):
    fire_id: str
    env_id: str
    model: str
    n_ignitions: int

# ---------- Routes ----------

@router.post("/environment")
def create_environment(req: NewEnvironment):
    env_id = save_environment(req.grid, req.seed, req.terrain_elev_path, req.feasibility_mask_path)
    return {"env_id": env_id}

@router.post("/fire")
def create_fire(req: NewFire):
    # Validate env exists
    try:
        _ = load_environment(req.env_id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Environment {req.env_id} not found")
    fire_id = save_fire(req.env_id, req.ignitions, req.model, req.seed)
    return {"fire_id": fire_id}

@router.get("/environments", response_model=List[EnvRow])
def list_environments():
    """Return [{env_id, H, W, cell_size, crs_code}] for all saved environments."""
    out: list[EnvRow] = []
    if MANIFESTS.exists():
        for p in MANIFESTS.glob("env-*.json"):
            try:
                m = EnvironmentManifest.model_validate_json(p.read_text())
                out.append(EnvRow(
                    env_id=m.env_id,
                    H=m.grid.H,
                    W=m.grid.W,
                    cell_size=m.grid.cell_size,
                    crs_code=m.grid.crs_code,
                ))
            except Exception:
                continue
    # sort by id for stable UI dropdowns
    return sorted(out, key=lambda d: d.env_id)

@router.get("/fires", response_model=List[FireRow])
def list_fires():
    """Return [{fire_id, env_id, model, n_ignitions}] for all saved fires."""
    out: list[FireRow] = []
    if MANIFESTS.exists():
        for p in MANIFESTS.glob("fire-*.json"):
            try:
                m = FireManifest.model_validate_json(p.read_text())
                out.append(FireRow(
                    fire_id=m.fire_id,
                    env_id=m.env_id,
                    model=m.model,
                    n_ignitions=len(m.ignitions.locations),
                ))
            except Exception:
                continue
    return sorted(out, key=lambda d: d.fire_id)
