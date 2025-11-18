import numpy as np
from typing import Optional

def step(state_t: np.ndarray, q: float, rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """
    Toy spread: each burning cell can ignite its 4-neighbours with prob q (Bernoulli).
    Cells stay 'on' once lit. Stateless aside from RNG; easy to swap for a richer model later.
    """
    if rng is None:
        rng = np.random.default_rng()

    H, W = state_t.shape
    s = state_t.astype(np.uint8)

    # 4-neighbour shifts
    up    = np.zeros_like(s); up[1:,  :] = s[:-1, :]
    down  = np.zeros_like(s); down[:-1,:] = s[1:,  :]
    left  = np.zeros_like(s); left[:, 1:] = s[:, :-1]
    right = np.zeros_like(s); right[:, :-1] = s[:, 1:]

    # any neighbour burning → candidate to ignite
    neigh_on = (up | down | left | right).astype(bool)

    # already burning remain burning
    out = s.copy()

    # candidate new ignitions with prob q (don’t relight already-on)
    mask = (~out.astype(bool)) & neigh_on
    if q > 0.0:
        draws = rng.random(size=out.shape)
        ignite = (draws < q) & mask
        out[ignite] = 1

    return out
