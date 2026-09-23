"""Re-render the report from saved fold records + live genome (no WF re-run)."""
import json

import config as C
import data as D
import evolve as EV
import report as RP
import regime as RG

out_dir = C.RESULTS_DIR / "20260918"
records = []
for p in sorted(out_dir.glob("fold_*.json")):
    records.append(json.loads(p.read_text(encoding="utf-8")))
live = json.loads((C.RESULTS_DIR / "live_genome.json").read_text(encoding="utf-8"))
cache = D.load_cache()
reg = RG.compute(cache["bench_sse"], cache["breadth"])
res = {"records": records, "live": live, "cache": cache, "regime": reg,
       "out_dir": out_dir}
m = RP.make_report(res)
print("portfolio OOS:", {k: round(v, 4) for k, v in m.items() if isinstance(v, float)})
