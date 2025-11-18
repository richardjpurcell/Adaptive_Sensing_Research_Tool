# backend/api/routers/preview.py
from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from awsrt_core.io.manifests import load_environment
from awsrt_core.sim.belief import init_belief
from awsrt_core.io.renders import belief_to_png

router = APIRouter()

class BeliefPreviewPayload(BaseModel):
    env_id: str
    prior: Literal["uniform"] = "uniform"
    prior_strength: float = Field(1.0, ge=0.0)
    cmap: str = "viridis"
    vmin: float = 0.0
    vmax: float = 1.0
    quality: Literal["fast","pub"] = "fast"

@router.post("/belief.png")
def preview_belief(p: BeliefPreviewPayload):
    try:
        env = load_environment(p.env_id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Environment {p.env_id} not found")
    arr = init_belief(env, p.prior, p.prior_strength)
    png = belief_to_png(arr, cmap=p.cmap, vmin=p.vmin, vmax=p.vmax, quality=p.quality)
    return Response(content=png, media_type="image/png")
