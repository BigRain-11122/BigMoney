# -*- coding: utf-8 -*-
# r651 bm-c: fund-trio progress watch (read-only; bm-b rightful burner lane)
import json, os, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {"probe": "r651 bm-c trio watch", "trio": {}}
for fam in ("value", "quality", "divlowvol"):
    for f in sorted(glob.glob(os.path.join(ROOT, "results", "fund_%s_p1" % fam, "nulls.jsonl"))):
        n = 0
        with open(f, encoding="utf-8") as fh:
            for _line in fh:
                n += 1
        out["trio"][fam] = {"nulls_lines": n, "target": 2000, "complete": n >= 2000}
# pool ready entries
p = json.load(open(os.path.join(ROOT, "results", "runnable_pool.json"), encoding="utf-8-sig"))
ready = []
for e in p.get("entries", []):
    st = e.get("status")
    if st in ("ready", "waiting"):
        ready.append((e.get("id") or e.get("entry_id"), st))
out["pool_ready_or_waiting"] = ready
with open(os.path.join(ROOT, "results", "_r651bmc_trio_watch.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print(json.dumps(out, ensure_ascii=False))
