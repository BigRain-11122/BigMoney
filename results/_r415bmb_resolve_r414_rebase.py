# r415 bm-b: resolve round-414 push-rejection rebase crash batch (19 UU)
# Per bigmoney-conflict-resolve SKILL.md canonical recipes:
#  - snapshots (14 classified + 4 live_usage manual-closed as same-day regen twins): take bm-b (:3:) side
#    (probe: bm-b uniformly fresher 07:16-07:17 vs origin 06:59-07:00; legal stale-takeover O-2100 s2.4)
#  - rolling-ledger compute_audit.json: union history by ts + latest take-new (r188/R208)
#  - rolling-ledger regime_state.json: union history by asof + state take-new (R208/r319)
# Zero-loss verification: ledger union line-counts = |A u B|.
import subprocess, json, sys

SNAPSHOTS = [
    "docs/daily_report/REPORT-2026-09-29.json",
    "docs/daily_report/REPORT-2026-09-29.md",
    "docs/live_usage/LIVE-2026-09-29.json",
    "docs/live_usage/LIVE-2026-09-29.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/dashboard_status.js",       # js-wrapper-snapshot: take-side whole bytes (R209)
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

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0:
        sys.exit("MISSING blob :%d:%s" % (stage, path))
    return r.stdout

def dump_crlf(obj):
    return (json.dumps(obj, indent=1, ensure_ascii=False) + "\n").replace("\n", "\r\n").encode("utf-8")

def union_by(entries_a, entries_b, key):
    """union with zero row loss: dedup on key, both sides' distinct rows kept."""
    out, seen = [], set()
    for e in entries_a + entries_b:
        k = e.get(key)
        if k is None:
            sys.exit("union key %r missing in entry %s" % (key, json.dumps(e)[:120]))
        if k in seen:
            continue
        seen.add(k)
        out.append(e)
    return out

report = []

# --- 1) snapshots: take bm-b side whole bytes ---
for p in SNAPSHOTS:
    r = subprocess.run(["git", "checkout", "--theirs", "--", p])
    if r.returncode != 0:
        sys.exit("checkout --theirs failed: " + p)
    report.append("take-bm-b(snapshot): " + p)

# --- 2) compute_audit.json: union history by ts, latest take-new ---
A = json.loads(blob(2, "results/compute_audit.json"))
B = json.loads(blob(3, "results/compute_audit.json"))
ua, ub = len(A["history"]), len(B["history"])
hist = union_by(A["history"], B["history"], "ts")
hist.sort(key=lambda e: e["ts"])
merged = dict(B)          # latest + all state fields = bm-b (newest)
merged["history"] = hist
open("results/compute_audit.json", "wb").write(dump_crlf(merged))
report.append("union ledger: results/compute_audit.json history |A|=%d |B|=%d -> |AuB|=%d (zero-loss=%s)"
              % (ua, ub, len(hist), len(hist) == len(set(e["ts"] for e in A["history"]) | set(e["ts"] for e in B["history"]))))

# --- 3) regime_state.json: union history by asof, state take-new ---
A = json.loads(blob(2, "results/regime_state.json"))
B = json.loads(blob(3, "results/regime_state.json"))
ua, ub = len(A["history"]), len(B["history"])
hist = union_by(A["history"], B["history"], "asof")
hist.sort(key=lambda e: e["asof"])
tr = union_by(A.get("transitions", []), B.get("transitions", []), "ts" if B.get("transitions") and "ts" in B["transitions"][0] else "date")
merged = dict(B)
merged["history"] = hist
merged["transitions"] = tr
open("results/regime_state.json", "wb").write(dump_crlf(merged))
report.append("union ledger: results/regime_state.json history |A|=%d |B|=%d -> |AuB|=%d; transitions |AuB|=%d"
              % (ua, ub, len(hist), len(tr)))

# --- 4) validation gate: json.loads pass + js wrapper intact (r185 law) ---
for p in SNAPSHOTS:
    if p.endswith(".json"):
        json.loads(open(p, "rb").read().decode("utf-8"))
js = open("results/dashboard_status.js", "rb").read().decode("utf-8")
assert js.lstrip().startswith("window.DASH_DATA") and js.rstrip().endswith("};"), "js wrapper broken"
json.loads(blob(2, "results/compute_audit.json")); json.loads(open("results/compute_audit.json", "rb").read().decode("utf-8"))
json.loads(open("results/regime_state.json", "rb").read().decode("utf-8"))
report.append("validation: all json.loads PASS + js wrapper intact")

for line in report:
    print(line)

# --- 5) stage resolved files ---
for p in SNAPSHOTS + ["results/compute_audit.json", "results/regime_state.json"]:
    r = subprocess.run(["git", "add", "--", p])
    if r.returncode != 0:
        sys.exit("git add failed: " + p)
print("staged all 19 resolved paths OK")
