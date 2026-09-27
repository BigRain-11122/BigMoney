# -*- coding: utf-8 -*-
"""R313 resolver pass 2: archive diff + small-face ts decisions."""
import json, os, re, subprocess

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    return r.stdout

DUMP = os.path.join(os.environ.get("TEMP", "."), "_r313bma_conflict")

# ---- memory-archive/202609.md divergence ----
a = blob(2, "research/memory-archive/202609.md").decode("utf-8")
b = blob(3, "research/memory-archive/202609.md").decode("utf-8")
la, lb = a.splitlines(), b.splitlines()
# common prefix
i = 0
while i < min(len(la), len(lb)) and la[i] == lb[i]:
    i += 1
j = 0
while j < min(len(la), len(lb)) - i and la[len(la)-1-j] == lb[len(lb)-1-j]:
    j += 1
mid_a, mid_b = la[i:len(la)-j], lb[i:len(lb)-j]
print("PREFIX lines:", i, "SUFFIX lines:", j, "| mid_a:", len(mid_a), "mid_b:", len(mid_b))
print("== MID_A (bm-b side) headers ==")
for L in mid_a:
    if L.strip().startswith("#") or L.strip().startswith("- ["):
        print("  A:", L[:150])
print("== MID_B (bm-a side) headers ==")
for L in mid_b:
    if L.strip().startswith("#") or L.strip().startswith("- ["):
        print("  B:", L[:150])
# overlap check: lines of mid_a present in mid_b
seta = set(l.strip() for l in mid_a if l.strip())
setb = set(l.strip() for l in mid_b if l.strip())
inter = seta & setb
print("identical-line overlap between mids:", len(inter))
with open(os.path.join(DUMP, "mid_a.md"), "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(mid_a))
with open(os.path.join(DUMP, "mid_b.md"), "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(mid_b))

# ---- regime_state both sides ----
for side, st in (("ours", 2), ("theirs", 3)):
    print("== regime_state %s ==" % side, blob(st, "results/regime_state.json").decode("utf-8"))

# ---- compute_audit latest + history key sample ----
for side, st in (("ours", 2), ("theirs", 3)):
    d = json.loads(blob(st, "results/compute_audit.json").decode("utf-8"))
    print("compute_audit %s: history=%d latest.ts=%s latest keys=%s" % (
        side, len(d["history"]), d["latest"].get("ts"), sorted(d["latest"].keys())[:8]))
    print("  hist sample keys:", sorted(d["history"][0].keys())[:8], "| first ts:", d["history"][0].get("ts"), "| last ts:", d["history"][-1].get("ts"))
    ts_a = [h.get("ts") for h in d["history"]]
    print("  ts uniq:", len(set(ts_a)), "of", len(ts_a))

# ---- files missing ts: updated/now/meta ----
for p, keys in [("results/fundamental_b_layer_filter.json", ["updated"]),
                ("results/heat_update_status.json", ["updated"]),
                ("results/lhb_update_status.json", ["updated"]),
                ("results/update_status.json", ["now", "data_cutoff"]),
                ("results/dashboard_status.json", ["meta"])]:
    for side, st in (("ours", 2), ("theirs", 3)):
        d = json.loads(blob(st, p).decode("utf-8"))
        vals = {}
        for k in keys:
            v = d.get(k)
            if isinstance(v, dict):
                v = {kk: v[kk] for kk in list(v)[:6]}
            vals[k] = v
        print(p, side, json.dumps(vals, ensure_ascii=False)[:300])
