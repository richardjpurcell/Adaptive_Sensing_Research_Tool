import json, uuid, hashlib
from pathlib import Path
from typing import Tuple
from .paths import MANIFESTS, ensure_dirs
from awsrt_core.schemas.manifests import EnvironmentManifest, FireManifest, GridSpec, IgnitionSpec, IgnitionCell

def _hash_payload(d: dict) -> str:
    b = json.dumps(d, sort_keys=True).encode("utf-8")
    return hashlib.sha1(b).hexdigest()[:10]

def save_environment(grid: GridSpec, seed: int, terrain_elev_path=None, feasibility_mask_path=None) -> str:
    ensure_dirs()
    payload = dict(grid=grid.model_dump(), seed=seed,
                   terrain_elev_path=terrain_elev_path, feasibility_mask_path=feasibility_mask_path)
    env_id = f"env-{_hash_payload(payload)}-{uuid.uuid4().hex[:6]}"
    manifest = EnvironmentManifest(env_id=env_id, grid=grid, seed=seed,
                                   terrain_elev_path=terrain_elev_path,
                                   feasibility_mask_path=feasibility_mask_path)
    path = MANIFESTS / f"{env_id}.json"
    path.write_text(json.dumps(manifest.model_dump(), indent=2))
    return env_id

def load_environment(env_id: str) -> EnvironmentManifest:
    path = MANIFESTS / f"{env_id}.json"
    return EnvironmentManifest.model_validate_json(path.read_text())

def save_fire(env_id: str, ignitions: IgnitionSpec, model: str, seed: int) -> str:
    ensure_dirs()
    payload = dict(env_id=env_id, ignitions=ignitions.model_dump(), model=model, seed=seed)
    fire_id = f"fire-{_hash_payload(payload)}-{uuid.uuid4().hex[:6]}"
    mf = FireManifest(fire_id=fire_id, env_id=env_id, ignitions=ignitions, model=model, seed=seed)
    (MANIFESTS / f"{fire_id}.json").write_text(json.dumps(mf.model_dump(), indent=2))
    return fire_id

def load_fire(fire_id: str) -> FireManifest:
    path = MANIFESTS / f"{fire_id}.json"
    return FireManifest.model_validate_json(path.read_text())
