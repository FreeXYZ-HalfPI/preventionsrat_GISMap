"""Select the Stadtbezirk to work on: DISTRICT=<slug> (default buchholz-kleefeld), see config/districts.json."""
import json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "config" / "districts.json").read_text())
CONFIG = {k: v for k, v in CONFIG.items() if not k.startswith("_")}
SLUG = os.environ.get("DISTRICT", "buchholz-kleefeld")
D = CONFIG[SLUG]
DATA = ROOT / D["data_dir"]
