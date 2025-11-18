from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel
from typing import List
from pathlib import Path
import uuid, json

from awsrt_core.schemas.run import (
    InitRunRequest, InitRunResponse,
    StepResponse, LatestResponse,
)
from awsrt_core.io.manifests import load_environment, load_fire
from awsrt_core.sim.fire_model import state_from_ignitions
from awsrt_core.sim.belief import init_belief_with_priors
from awsrt_core.sim.wildfire_env import step as step_model
from awsrt_core.io.fields import create_or_open_zarr, append_state, append_belief
from awsrt_core.io.renders import state_to_png, belief_to_png, legend_belief_png
from awsrt_core.io.paths import run_renders_dir, run_fields_dir, FIELDS

import zarr
import numpy as np

router = APIRouter()

# ----------------------------
# Helpers
# ----------------------------

def _config_path(run_id: str) -> Path:
    return run_fields_dir(run_id) / "run_config.json"

def _write_config(run_id: str, cfg: dict):
    p = _config_path(run_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(cfg, indent=2))

def _read_config(run_id: str) -> dict:
    p = _config_path(run_id)
    if not p.exists():
        raise HTTPException(404, f"run_config.json not found for {run_id}")
    return json.loads(p.read_text())

def _rng_for(run_id: str, t: int) -> np.random.Generator:
    # deterministic per (run_id, t) for exact replay; simple stable hash to seed
    seed = (hash(run_id) ^ (t * 0x9E3779B97F4A7C15)) & 0xFFFFFFFF
    return np.random.default_rng(seed)

# ----------------------------
# Init (t=0)
# ----------------------------

@router.post("/init", response_model=InitRunResponse)
def init_run(req: InitRunRequest):
    # Load manifests
    try:
        env = load_environment(req.env_id)
    except Exception:
        raise HTTPException(404, f"Environment {req.env_id} not found")
    try:
        fire = load_fire(req.fire_id)
    except Exception:
        raise HTTPException(404, f"Fire {req.fire_id} not found")

    H, W = env.grid.H, env.grid.W

    # Compute t=0 arrays
    s0 = state_from_ignitions(env, fire)      # uint8 {0,1}
    b0 = init_belief_with_priors(env, fire)   # float32 [0,1]

    # Create Zarr, append t=0
    run_id = f"run-{uuid.uuid4().hex[:8]}"
    root = create_or_open_zarr(run_id=run_id, H=H, W=W)
    t_state = append_state(root, s0)
    t_belief = append_belief(root, b0)
    assert t_state == 0 and t_belief == 0

    # Persist run config
    cfg = dict(
        run_id=run_id,
        env_id=req.env_id,
        fire_id=req.fire_id,
        run_name=req.run_name,
        dt_seconds=req.dt_seconds,
        horizon_steps=req.horizon_steps,
        spread_prob=req.spread_prob,
    )
    _write_config(run_id, cfg)

    # Warm renders directory (optional)
    run_renders_dir(run_id, 0).mkdir(parents=True, exist_ok=True)

    return InitRunResponse(run_id=run_id, t=0, dt_seconds=req.dt_seconds, horizon_steps=req.horizon_steps)

# ----------------------------
# Replay helpers
# ----------------------------

class RunMeta(BaseModel):
    run_id: str
    H: int
    W: int
    T: int  # number of time slices available

@router.get("/list")
def list_runs() -> List[str]:
    if not FIELDS.exists():
        return []
    runs: List[str] = []
    for p in FIELDS.iterdir():
        if p.is_dir():
            # minimal check: Zarr group contains datasets
            if (p / ".zgroup").exists() or (p / "state").exists():
                runs.append(p.name)
    runs.sort()
    return runs

@router.get("/{run_id}/meta", response_model=RunMeta)
def get_run_meta(run_id: str):
    root = zarr.open_group(str(run_fields_dir(run_id)), mode="r")
    if "state" not in root or "belief" not in root:
        raise HTTPException(404, f"Run {run_id} missing datasets")
    st = root["state"]; bl = root["belief"]
    if st.shape != bl.shape:
        raise HTTPException(409, f"Dataset shape mismatch for {run_id}: state={st.shape}, belief={bl.shape}")
    T, H, W = st.shape
    return RunMeta(run_id=run_id, H=H, W=W, T=T)

@router.get("/{run_id}/latest", response_model=LatestResponse)
def get_latest(run_id: str):
    root = zarr.open_group(str(run_fields_dir(run_id)), mode="r")
    if "state" not in root:
        raise HTTPException(404, f"Run {run_id} missing datasets")
    T = root["state"].shape[0]
    return LatestResponse(run_id=run_id, t_latest=max(0, T - 1))

# ----------------------------
# Time stepping
# ----------------------------

@router.post("/{run_id}/step", response_model=StepResponse)
def post_step(run_id: str):
    cfg = _read_config(run_id)
    root = zarr.open_group(str(run_fields_dir(run_id)), mode="a")

    if "state" not in root or "belief" not in root:
        raise HTTPException(404, f"Run {run_id} missing datasets")

    st = root["state"]; bl = root["belief"]
    t_cur = st.shape[0] - 1
    horizon = int(cfg.get("horizon_steps", 1))
    if t_cur + 1 >= horizon:
        return StepResponse(run_id=run_id, t=t_cur, done=True)

    s_t = st[t_cur, :, :]
    b_t = bl[t_cur, :, :]   # unchanged for now (no observations)

    # Step the hidden state with deterministic RNG for this (run_id, t_cur)
    rng = _rng_for(run_id, t_cur)
    q = float(cfg.get("spread_prob", 0.3))
    s_next = step_model(s_t, q=q, rng=rng)

    # Append next
    from awsrt_core.io.fields import append_state, append_belief
    t1 = append_state(root, s_next)
    _ = append_belief(root, b_t)  # carry belief forward unchanged (until sensors)

    done = (t1 + 1 >= horizon)
    return StepResponse(run_id=run_id, t=t1, done=done)

@router.post("/{run_id}/advance", response_model=StepResponse)
def post_advance(run_id: str, n: int = 1):
    """
    Advance up to n steps or until horizon. Returns the final t.
    """
    if n < 1:
        raise HTTPException(400, "n must be >= 1")
    last = None
    for _ in range(n):
        last = post_step(run_id)
        if last.done:
            break
    return last

# ----------------------------
# Image endpoints (unchanged)
# ----------------------------

@router.get("/{run_id}/t/{t}/state.png")
def get_state_png(run_id: str, t: int):
    root = zarr.open_group(str(run_fields_dir(run_id)), mode="r")
    if "state" not in root or t < 0 or t >= root["state"].shape[0]:
        raise HTTPException(404, f"No state at t={t} for {run_id}")
    arr = root["state"][t, :, :]
    png = state_to_png(arr)
    return Response(content=png, media_type="image/png")

@router.get("/{run_id}/t/{t}/belief.png")
def get_belief_png(run_id: str, t: int, vmin: float = 0.0, vmax: float = 1.0, cmap: str = "viridis", quality: str = "fast"):
    root = zarr.open_group(str(run_fields_dir(run_id)), mode="r")
    if "belief" not in root or t < 0 or t >= root["belief"].shape[0]:
        raise HTTPException(404, f"No belief at t={t} for {run_id}")
    arr = root["belief"][t, :, :]
    png = belief_to_png(arr, cmap=cmap, vmin=vmin, vmax=vmax, quality=quality)
    return Response(content=png, media_type="image/png")

@router.get("/{run_id}/legend/belief.png")
def get_belief_legend(run_id: str, vmin: float = 0.0, vmax: float = 1.0, cmap: str = "viridis"):
    png = legend_belief_png(vmin=vmin, vmax=vmax, cmap=cmap)
    return Response(content=png, media_type="image/png")
