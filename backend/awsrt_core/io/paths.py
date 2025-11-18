from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # .../adaptive_sensing_research_tool
DATA = ROOT / "data"
MANIFESTS = DATA / "manifests"
FIELDS = DATA / "fields"
RENDERS = DATA / "renders"
LOGS = DATA / "logs"

def ensure_dirs():
    for p in (DATA, MANIFESTS, FIELDS, RENDERS, LOGS):
        p.mkdir(parents=True, exist_ok=True)

def run_fields_dir(run_id: str) -> Path:
    return FIELDS / run_id

def run_renders_dir(run_id: str, t: int) -> Path:
    return RENDERS / run_id / f"t{t:03d}"
