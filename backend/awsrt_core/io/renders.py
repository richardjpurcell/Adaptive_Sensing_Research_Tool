from io import BytesIO
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

def _to_png_bytes(fig) -> bytes:
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return buf.read()

def belief_to_png(belief: np.ndarray, cmap="viridis", vmin=0.0, vmax=1.0, quality="fast") -> bytes:
    fig = plt.figure(figsize=(belief.shape[1]/128, belief.shape[0]/128), dpi=128 if quality=="fast" else 200)
    ax = fig.add_axes([0,0,1,1])
    ax.imshow(belief, cmap=cmap, vmin=vmin, vmax=vmax, origin="upper", interpolation="nearest" if quality=="fast" else "bilinear")
    ax.axis("off")
    return _to_png_bytes(fig)

def state_to_png(state01: np.ndarray, quality="fast") -> bytes:
    # Map 0 -> light gray, 1 -> red
    h, w = state01.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    rgb[:, :, :] = (220, 220, 220)  # background
    mask = state01.astype(bool)
    rgb[mask] = (200, 30, 30)
    img = Image.fromarray(rgb, mode="RGB")
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()

def legend_belief_png(vmin=0.0, vmax=1.0, cmap="viridis") -> bytes:
    fig, ax = plt.subplots(figsize=(3, 0.35), dpi=200)
    fig.subplots_adjust(bottom=0.5)
    norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
    cb = matplotlib.colorbar.ColorbarBase(ax, cmap=plt.get_cmap(cmap), norm=norm, orientation='horizontal')
    cb.set_label("Belief (probability)")
    return _to_png_bytes(fig)
