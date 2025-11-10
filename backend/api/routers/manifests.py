from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

router = APIRouter()
ROOT = Path(__file__).resolve().parents[3]  # .../adaptive_sensing_research_tool
MANI = ROOT / "data" / "manifests"

@router.get("/list")
def list_manifests():
    MANI.mkdir(parents=True, exist_ok=True)
    files = sorted(MANI.glob("*.json"))
    out = []
    for f in files:
        try:
            with f.open() as fh:
                j = json.load(fh)
            out.append({"file": f.name, "name": j.get("name"), "id": j.get("env_id") or j.get("fire_id") or j.get("sensors_id")})
        except Exception:
            out.append({"file": f.name, "name": None, "id": None})
    return {"manifests": out}
