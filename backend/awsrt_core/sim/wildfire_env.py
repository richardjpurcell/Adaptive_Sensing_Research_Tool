import numpy as np
from typing import Optional

def step(state_t: np.ndarray, q: float, rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """Toy 4-neighbour Bernoulli spread with prob q; burning cells stay burning."""
    if rng is None:
        rng = np.random.default_rng()

    s = state_t.astype(np.uint8)
    up    = np.zeros_like(s); up[1:,  :]  = s[:-1, :]
    down  = np.zeros_like(s); down[:-1, :] = s[1:,  :]
    left  = np.zeros_like(s); left[:, 1:] = s[:, :-1]
    right = np.zeros_like(s); right[:, :-1] = s[:, 1:]

    neigh_on = (up | down | left | right).astype(bool)
    out = s.copy()

    mask = (~out.astype(bool)) & neigh_on
    if q > 0.0:
        ignite = (rng.random(size=out.shape) < q) & mask
        out[ignite] = 1
    return out
