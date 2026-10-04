# r683 (bm-b): pool/fuse/autofill tri-face read for W3-JUDGE-SHARD-1 done-flip decision (r668 law)
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {}

# 1) runnable_pool entries for w3-judge
pool = json.load(open(os.path.join(ROOT, "results", "runnable_pool.json"), encoding="utf-8"))
entries = pool.get("entries", [])
w3 = [e for e in entries if "w3-judge" in json.dumps(e.get("id", "")) or "W3-JUDGE" in json.dumps(e.get("id", ""))]
out["pool_w3_entries"] = [
    {k: e.get(k) for k in ("id", "status", "owner", "owner_since", "keepalive_ts", "note", "shards", "result_ref")}
    for e in w3
]
out["pool_total_entries"] = len(entries)

# 2) autofill state (bm-b lane face)
af = json.load(open(os.path.join(ROOT, "results", "autofill_state.bm-b.json"), encoding="utf-8"))
out["autofill_bmb_keys"] = sorted(af.keys())
for k in ("last_tick", "last_entry", "active", "in_flight", "claims"):
    if k in af:
        out["af_" + k] = af[k]

# 3) crash fuse
for fname in ("results/crash_fuse.json", "results/crash_fuse.bm-b.json"):
    p = os.path.join(ROOT, fname)
    if os.path.exists(p):
        cf = json.load(open(p, encoding="utf-8"))
        out[fname.replace("/", "_").replace(".", "_")] = {k: cf.get(k) for k in sorted(cf.keys())[:14]}

# 4) shard-1 last line integrity
SH = os.path.join(ROOT, "results", "mass_trial", "w3_judge_shard_1of4.jsonl")
lines = [ln for ln in open(SH, "rb").read().split(b"\n") if ln.strip()]
last = json.loads(lines[-1])
out["shard1_rows"] = len(lines)
out["shard1_last_row_core"] = {k: last.get(k) for k in ("candidate_id", "cell_id", "i", "family", "dual_nulls", "sample_sufficient") if k in last}
# row-level sanity: distinct candidate ids
cids = set()
for ln in lines:
    try:
        cids.add(json.loads(ln).get("candidate_id"))
    except Exception:
        pass
out["shard1_distinct_candidates"] = len(cids)

# 5) w3_judge_state / enrollment faces if present
for fname in ("results/mass_trial/w3_judge_state.json", "results/w3_judge_state.json"):
    p = os.path.join(ROOT, fname)
    if os.path.exists(p):
        s = json.load(open(p, encoding="utf-8"))
        out[fname.replace("/", "_").replace(".", "_")] = s if len(json.dumps(s)) < 2000 else "LARGE"

print(json.dumps(out, ensure_ascii=True, indent=1))
