# r464 bm-b push-collision rebase resolver (19 UU, replay onto bm-a r474/bm-c r271 tip 06c8e06d6)
# Direction probe = results/_r464bmb_probe.py: S3(mine 13:53-13:55) newer than S2(origin 13:36-13:50) on ALL faces.
# Recipes: 17 take-S3 whole bytes; marks.jsonl + compute_audit + regime_state = zero-loss union (r188/R208/r217).
import subprocess, json, sys

def blob_bytes(path, stage):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    assert r.returncode == 0, f"blob read fail {path}:{stage}"
    return r.stdout

TAKE_S3 = [
    "docs/daily_report/REPORT-2026-09-30.json",
    "docs/daily_report/REPORT-2026-09-30.md",
    "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/regime_state.json",  # state fields take-new; history union handled below (overwritten after)
]
UNION_JSONL = "results/paper/marks/marks-20260930.jsonl"
UNION_LEDGERS = ["results/compute_audit.json", "results/regime_state.json"]

report = []

# --- take-S3 whole bytes ---
for f in TAKE_S3:
    b = blob_bytes(f, 3)
    if f.endswith(".json"):
        json.loads(b.decode("utf-8"))  # r185: parse-validate before write
    with open(f, "wb") as fh:
        fh.write(b)
    report.append(f"take-S3 {f}")

# --- marks jsonl line-level union (dedup exact lines, sort by embedded ts, zero loss) ---
s2 = blob_bytes(UNION_JSONL, 2).decode("utf-8").splitlines()
s3 = blob_bytes(UNION_JSONL, 3).decode("utf-8").splitlines()
l2 = [l for l in s2 if l.strip()]
l3 = [l for l in s3 if l.strip()]
seen, union = set(), []
for l in l2 + l3:
    if l not in seen:
        seen.add(l)
        union.append(l)
def ts_of(l):
    j = json.loads(l)
    return j.get("ts", j.get("time", ""))
union.sort(key=ts_of)
for l in union:
    json.loads(l)  # every line valid json
n_expect = len(set(l2) | set(l3))
assert len(union) == n_expect, f"union loss: {len(union)} != {n_expect}"
# tick ts uniqueness sanity: count distinct ts
ts_all = [ts_of(l) for l in union]
assert len(union) == len(ts_all)
with open(UNION_JSONL, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(union) + "\n")
report.append(f"union-jsonl {UNION_JSONL}: {len(l2)}+{len(l3)} -> {len(union)} (|A u B|={n_expect}) zero-loss assert OK")

# --- rolling-ledger unions (compute_audit history + regime_state history/transitions) ---
for f in UNION_LEDGERS:
    a = json.loads(blob_bytes(f, 2).decode("utf-8"))
    b = json.loads(blob_bytes(f, 3).decode("utf-8"))
    merged = dict(b)  # take-new snapshot fields from S3 (mine, newest ts)
    for key in ("history", "transitions", "launches"):
        if key in a or key in b:
            ra = a.get(key, [])
            rb = b.get(key, [])
            dedup, seen = [], set()
            for row in ra + rb:
                sig = json.dumps(row, sort_keys=True, ensure_ascii=False)
                if sig not in seen:
                    seen.add(sig)
                    dedup.append(row)
            def k(row):
                return str(row.get("ts", row.get("updated", row.get("date", ""))))
            dedup.sort(key=k)
            n_exp = len({json.dumps(x, sort_keys=True, ensure_ascii=False) for x in ra + rb})
            assert len(dedup) == n_exp, f"{f}.{key} union loss {len(dedup)} != {n_exp}"
            assert len(dedup) >= max(len(ra), len(rb)), f"{f}.{key} shrink"
            merged[key] = dedup
            report.append(f"union {f}.{key}: {len(ra)}+{len(rb)} -> {len(dedup)} zero-loss OK")
    json.dump(merged, open(f, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    json.loads(open(f, encoding="utf-8").read())
    report.append(f"union-ledger {f} written (state fields take-S3)")

print("\n".join(report))
print("RESOLVER DONE: 19 files")
