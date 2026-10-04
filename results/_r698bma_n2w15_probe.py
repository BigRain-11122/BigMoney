# -*- coding: utf-8 -*-
"""r698 bm-a N2-W15 pool + prep-state probe (read-only)."""
import json, io, os

out = io.StringIO()
with open("results/runnable_pool.json", encoding="utf-8-sig") as fh:
    pool = json.load(fh)

for e in pool.get("entries", []):
    if "N2" in str(e.get("id")) or "W15" in str(e.get("id")) or "w15" in str(e.get("id")).lower():
        print("=== ENTRY", e.get("id"), "status=", e.get("status"), "===", file=out)
        for k, v in e.items():
            if k == "shards":
                for s in v:
                    print("  shard:", json.dumps(s, ensure_ascii=False)[:500], file=out)
            else:
                print("  %s: %s" % (k, str(v)[:500]), file=out)

# n2_w15_prep_state.json tail
p = "results/n2_w15_prep_state.json"
if os.path.exists(p):
    with open(p, encoding="utf-8-sig") as fh:
        st = json.load(fh)
    print(file=out)
    print("=== n2_w15_prep_state keys ===", file=out)
    for k, v in st.items():
        print("  %s: %s" % (k, str(v)[:200]), file=out)

# candidates count
c = "results/n2_w15_candidates.json"
if os.path.exists(c):
    with open(c, encoding="utf-8-sig") as fh:
        cand = json.load(fh)
    if isinstance(cand, dict):
        for k, v in cand.items():
            if isinstance(v, list):
                print("cand[%s] len=%d" % (k, len(v)), file=out)
            else:
                print("cand[%s]=%s" % (k, str(v)[:120]), file=out)
    elif isinstance(cand, list):
        print("candidates list len=%d" % len(cand), file=out)
        if cand:
            print("first keys:", sorted(cand[0].keys()), file=out)

with open("results/_r698bma_n2w15_probe.txt", "w", encoding="utf-8", newline="") as fh:
    fh.write(out.getvalue())
print(out.getvalue())
