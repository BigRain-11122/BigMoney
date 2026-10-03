# r616 bm-b merge-conflict resolver (19 UU faces, same-window dual-derive vs bm-c r413)
# Law: bigmoney-conflict-resolve skill (r188/R208/R209/R216/r220), parse-verify before write-back,
# same-second tie -> HEAD (r140). Blob reads via git subprocess bytes (no PS redirect, r209/r617).
# Adjudication basis: ours (bm-b r616 S6, 11:43-11:47) newer than theirs (bm-c r413 S6, 11:39-11:41)
# on every ts-bearing face -> snapshot faces take-ours; token_usage = per-machine key max-merge
# (append-only byte counters, larger = fresher view; preserves bm-c r413 self-count); compute_audit =
# history whole-row union zero-loss + latest take-ours.
import json
import subprocess
import sys

TAKE_OURS = [
    "docs/daily_report/REPORT-2026-10-03.json", "docs/daily_report/REPORT-2026-10-03.md",
    "docs/live_usage/LIVE-2026-10-03.json", "docs/live_usage/LIVE-2026-10-03.md",
    "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.js", "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
    "results/lhb_update_status.json", "results/prospect_promotion/_summary.json",
    "results/regime_state.json", "results/scorecard_v1.json",
    "results/strategy_scorecard.json", "results/update_status.json",
]
UNION_LEDGER = ["results/compute_audit.json"]
MACHINE_MAX = ["results/token_usage.json"]


def blob(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        sys.exit("BLOBFAIL " + spec + ": " + r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout


def write(path, data):
    with open(path, "wb") as f:
        f.write(data)


receipt = []

# 1) plain take-ours faces (json parse-verify where json; md/js byte-verbatim)
for p in TAKE_OURS:
    b = blob(":2:" + p)
    if p.endswith(".json"):
        json.loads(b.decode("utf-8"))  # parse-verify before write-back
    write(p, b)
    receipt.append("TAKE_OURS " + p)

# 2) compute_audit.json: history whole-row union + latest take-ours (r188/R208)
p = "results/compute_audit.json"
ours = json.loads(blob(":2:" + p).decode("utf-8"))
theirs = json.loads(blob(":3:" + p).decode("utf-8"))
oh, th = ours.get("history", []), theirs.get("history", [])
seen = set()
merged = []
for row in list(oh) + list(th):
    key = json.dumps(row, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key)
        merged.append(row)
# stable order: keep ours order first then theirs-only rows appended (append-only ledger order)
final = dict(ours)
final["history"] = merged
assert isinstance(final.get("latest"), dict)
json.loads(json.dumps(final, ensure_ascii=False))  # roundtrip sanity
write(p, json.dumps(final, ensure_ascii=False, indent=1).encode("utf-8"))
receipt.append("UNION history %d+%d->%d latest=ours" % (len(oh), len(th), len(merged)))

# 3) token_usage.json: per-machine key max-merge (byte counters monotone for append-only faces)
p = "results/token_usage.json"
ours = json.loads(blob(":2:" + p).decode("utf-8"))
theirs = json.loads(blob(":3:" + p).decode("utf-8"))
om, tm = ours.get("machines", {}), theirs.get("machines", {})
merged_machines = {}
for k in sorted(set(om) | set(tm)):
    a, b = om.get(k), tm.get(k)
    if a is None:
        merged_machines[k] = b
    elif b is None:
        merged_machines[k] = a
    else:
        # numeric fields: max (append-only growth); non-numeric: ours
        mk = {}
        for f in sorted(set(a) | set(b)):
            av, bv = a.get(f), b.get(f)
            if isinstance(av, (int, float)) and isinstance(bv, (int, float)):
                mk[f] = av if av >= bv else bv
            else:
                mk[f] = av if av is not None else bv
        merged_machines[k] = mk
final = dict(ours)  # scalars/generated/method/per_round_context = ours (newest scan envelope)
final["machines"] = merged_machines
write(p, json.dumps(final, ensure_ascii=False, indent=1).encode("utf-8"))
receipt.append("TOKEN machines key-max-merge %d keys (scalars=ours 11:46:31)" % len(merged_machines))

for r in receipt:
    print("RESOLVED", r)
print("ALL 19 FACES RESOLVED")
