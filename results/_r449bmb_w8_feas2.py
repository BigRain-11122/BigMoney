"""Compare replay full-metrics vs frozen T-27 member face (COMPOSITE-CE-01 x1)."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from iv6_portfolio import member_run_iv6, _init_worker

_init_worker()
r = member_run_iv6("COMPOSITE-CE-01", None)
print("REPLAY full:", json.dumps(r.get("full", {}), ensure_ascii=False))
print("REPLAY n_entries:", r.get("n_entries"), "| cutoff:", r.get("cutoff"))
frozen = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "portfolio_blend_tournament.json"), encoding="utf-8"))
f = frozen["members"]["COMPOSITE-CE-01"]["x1"]["full"]
print("FROZEN full:", json.dumps(f, ensure_ascii=False))
