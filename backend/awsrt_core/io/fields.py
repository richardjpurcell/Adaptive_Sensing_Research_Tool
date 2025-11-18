from pathlib import Path
import numpy as np
import zarr
from numcodecs import Blosc
from .paths import ensure_dirs, run_fields_dir

CODEC = Blosc(cname="zstd", clevel=5, shuffle=Blosc.BITSHUFFLE)

def create_or_open_zarr(run_id: str, H: int, W: int):
    ensure_dirs()
    root = zarr.open_group(str(run_fields_dir(run_id)), mode="a")
    if "state" not in root:
        root.create_dataset("state", shape=(0, H, W), chunks=(1, 256, 256), dtype="u1", compressor=CODEC, overwrite=False)
    if "belief" not in root:
        root.create_dataset("belief", shape=(0, H, W), chunks=(1, 256, 256), dtype="f4", compressor=CODEC, overwrite=False)
    return root

def append_state(root, arr_t: np.ndarray):
    ds = root["state"]
    t = ds.shape[0]
    ds.resize(t+1, ds.shape[1], ds.shape[2])
    ds[t, :, :] = arr_t.astype(np.uint8)
    return t

def append_belief(root, arr_t: np.ndarray):
    ds = root["belief"]
    t = ds.shape[0]
    ds.resize(t+1, ds.shape[1], ds.shape[2])
    ds[t, :, :] = arr_t.astype(np.float32)
    return t
