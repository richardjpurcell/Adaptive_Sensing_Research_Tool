import numpy as np
from awsrt_core.schemas.manifests import EnvironmentManifest, FireManifest

def state_from_ignitions(env: EnvironmentManifest, fire: FireManifest) -> np.ndarray:
    H, W = env.grid.H, env.grid.W
    s0 = np.zeros((H, W), dtype=np.uint8)
    for loc in fire.ignitions.locations:
        if 0 <= loc.row < H and 0 <= loc.col < W:
            s0[loc.row, loc.col] = 1
    return s0
