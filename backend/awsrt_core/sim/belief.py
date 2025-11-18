import numpy as np
from awsrt_core.schemas.manifests import EnvironmentManifest, FireManifest

def init_belief(env: EnvironmentManifest, prior: str = "uniform", strength: float = 1.0) -> np.ndarray:
    H, W = env.grid.H, env.grid.W
    if prior == "uniform":
        return np.full((H, W), 0.5, dtype=np.float32)
    # extend with other priors later
    return np.full((H, W), 0.5, dtype=np.float32)

def init_belief_with_priors(env: EnvironmentManifest, fire: FireManifest) -> np.ndarray:
    # Minimal version: same as uniform for now; later we can nudge ignition cells
    return init_belief(env, "uniform", 1.0)
