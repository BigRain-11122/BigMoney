# _r460bmb_resolve.py -- resume-resolver for interrupted r460 rebase replay (19 UU)
# Canon: bigmoney-conflict-resolve SKILL.md (classifier 9/10 + manual classification)
# Direction: rebase replay of our r460 (7aaa32058) onto base 9fdec68fb:
#   :2 ours   = NEW base (bm-a r471 / bm-c r269 lineage, S6 outputs 12:47-12:49)
#   :3 theirs = our r460 commit (S6 outputs 12:54-12:55)  <-- NEWER snapshots
# Resolution map:
#   rolling-ledger union : compute_audit.json (history union by ts, latest=take-new)
#                          regime_state.json (history/transitions union, state=take-new)
#   snapshot take-new    : 15 files -- stage3 newer on every named ts probe
#   js-wrapper-snapshot  : dashboard_status.js -- whole-blob take stage3 (R209: no json.dumps rewrite)
# Zero-loss proof: compute_audit union row count printed; every resolved json json.loads-verified.
import subprocess, json, sys

def blob(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"FATAL: cannot read {rev}:{path}")
    return r.stdout

def write_bytes(path, b):
    with open(path, "wb") as f:
        f.write(b)

TAKE3 = [  # snapshot take-new (stage3 newer by named ts)
 "docs/daily_report/REPORT-2026-09-30.json",
 "docs/daily_report/REPORT-2026-09-30.md",
 "docs/live_usage/LIVE-2026-09-30.json",
 "docs/live_usage/LIVE-2026-09-30.md",
 "docs/live_usage/LIVE-latest.json",
 "docs/live_usage/LIVE-latest.md",
 "results/_attrition_guard_scan.json",
 "results/dashboard_status.json",
 "results/fundamental_b_layer_filter.json",
 "results/futures_update_status.json",
 "results/lhb_update_status.json",
 "results/prospect_promotion/_summary.json",
 "results/scorecard_v1.json",
 "results/strategy_scorecard.json",
 "results/token_usage.json",
 "results/update_status.json",
]
TAKE3_JS = ["results/dashboard_status.js"]  # js-wrapper: whole bytes, no rewrite

report = []

# --- snapshots: take stage3 whole bytes (write via raw bytes, no encoding translation) ---
for p in TAKE3 + TAKE3_JS:
    b = blob(":3", p)
    write_bytes(p, b)
    if p.endswith(".json"):
        json.loads(b)  # parse-verify before add (r185 law)
    report.append(f"take3 {p} ({len(b)}B)")

# --- compute_audit.json: history union by ts, latest take-new ---
p = "results/compute_audit.json"
d2 = json.loads(blob(":2", p).decode("utf-8"))
d3 = json.loads(blob(":3", p).decode("utf-8"))
h2, h3 = d2["history"], d3["history"]
seen, union = {}, []
for r in h2 + h3:  # base first, ours second -> same-second tie keeps base (r140 law)
    k = r.get("ts")
    if k not in seen:
        seen[k] = r
        union.append(r)
union.sort(key=lambda r: r.get("ts", ""))
n_only2 = len({r.get("ts") for r in h2} - {r.get("ts") for r in h3})
n_only3 = len({r.get("ts") for r in h3} - {r.get("ts") for r in h2})
assert len(union) == len(h2) + n_only3, f"union loss: {len(union)} vs {len(h2)}+{n_only3}"
merged = dict(d3)          # latest = take-new (ours 12:54:15 > base 12:47:29)
merged["history"] = union
out = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8")
json.loads(out)
write_bytes(p, out)
report.append(f"union compute_audit history |{len(h2)}|+|{len(h3)}| -> {len(union)} rows (base-only {n_only2}, ours-only {n_only3}, zero loss)")

# --- regime_state.json: history/transitions union, state fields take-new ---
p = "results/regime_state.json"
d2 = json.loads(blob(":2", p).decode("utf-8"))
d3 = json.loads(blob(":3", p).decode("utf-8"))
def union_rows(a, b, key):
    seen = {}
    for r in a + b:
        k = json.dumps({kk: r[kk] for kk in sorted(r)}, ensure_ascii=False)
        if k not in seen:
            seen[k] = r
    return sorted(seen.values(), key=lambda r: r.get("asof", r.get("ts", "")))
merged = dict(d3)  # state take-new (updated 12:54:24 > 12:47:38; state=ORANGE identical)
merged["history"] = union_rows(d2["history"], d3["history"], "asof")
merged["transitions"] = union_rows(d2["transitions"], d3["transitions"], "ts")
out = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8")
json.loads(out)
write_bytes(p, out)
report.append(f"union regime_state history {len(d2['history'])}/{len(d3['history'])}->{len(merged['history'])} transitions->{len(merged['transitions'])} state={merged['state']}")

for line in report:
    print(line)
print("RESOLVE-OK")
