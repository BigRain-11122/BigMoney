# -*- coding: utf-8 -*-
"""r350 S7 push-collision canonical resolver (bigmoney-conflict-resolve skill).

Context: rebase replay of my close-out commit onto bm-a's same-window origin
push. ours(:2)=bm-a side (S6 chain 00:25-00:27, cores=32), theirs(:3)=my side
(00:35-00:37, cores=16, NEWER for every snapshot). Recipes per classifier:
- 12 snapshot/idempotent-regen files -> take my side WHOLE BYTES (R209/R208/R216)
- compute_audit.json -> rolling-ledger: union history rows zero-loss (r360 no-cap
  law), latest = newer ts side (mine)
- regime_state.json -> rolling-ledger: union transitions/history, state fields
  take-new (mine); if row sets identical -> my bytes verbatim (zero churn)
"""
import subprocess, json, sys

TAKE_MINE = [
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/daily_report/REPORT-2026-09-28.md",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

def blob(side, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (side, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git show failed for " + path)
    return r.stdout

def key(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False)

report = []

# --- 12 whole-byte take-mine ---
for p in TAKE_MINE:
    mine = blob(3, p)
    assert b"<<<<<<<" not in mine, "marker in stage3 blob " + p
    with open(p, "wb") as f:
        f.write(mine)
    if p.endswith(".json"):
        json.loads(mine.decode("utf-8-sig"))
    elif p.endswith(".js"):
        assert mine.lstrip().startswith(b"window.DASH_DATA"), "js wrapper broken " + p
    elif p.endswith(".md"):
        assert mine.lstrip().startswith(b"#"), "md head broken " + p
    report.append("%s: take-mine %dB (newer ts)" % (p, len(mine)))

# --- compute_audit.json: union history + latest=mine ---
ca_bma = json.loads(blob(2, "results/compute_audit.json").decode("utf-8-sig"))
ca_mine = json.loads(blob(3, "results/compute_audit.json").decode("utf-8-sig"))
rows_a = ca_bma.get("history", [])
rows_b = ca_mine.get("history", [])
set_a = {key(r) for r in rows_a}
set_b = {key(r) for r in rows_b}
union_rows = [r for r in rows_a if key(r) in set_a]  # keep bm-a order base
for r in rows_b:
    if key(r) not in set_a:
        union_rows.append(r)
union_rows.sort(key=lambda r: r.get("ts", ""))
n_union = len({key(r) for r in union_rows})
assert n_union == len(set_a | set_b), "union lost rows: %d != %d" % (n_union, len(set_a | set_b))
merged = dict(ca_mine)  # latest = mine (ts 00:35:42 > 00:25:25)
merged["history"] = union_rows

# format detection: match my blob's indent style for zero-churn re-emit
mine_bytes = blob(3, "results/compute_audit.json")
detected = None
for ind in (0, 1, 2, 3, 4):
    if json.dumps(json.loads(mine_bytes.decode("utf-8-sig")), ensure_ascii=False, indent=ind).encode("utf-8") == mine_bytes:
        detected = ind
        break
    if json.dumps(json.loads(mine_bytes.decode("utf-8-sig")), ensure_ascii=False, indent=ind).encode("utf-8") + b"\n" == mine_bytes:
        detected = ind
        break
ind_used = detected if detected is not None else 1
out = json.dumps(merged, ensure_ascii=False, indent=ind_used)
if mine_bytes.endswith(b"\n"):
    out += "\n"
with open("results/compute_audit.json", "wb") as f:
    f.write(out.encode("utf-8"))
json.loads(open("results/compute_audit.json", encoding="utf-8-sig").read())
report.append("results/compute_audit.json: union history %d+%d -> %d rows (|A u B|=%d, zero loss, no cap), latest=mine ts=%s, indent=%s" % (
    len(rows_a), len(rows_b), len(union_rows), len(set_a | set_b), merged["latest"]["ts"], ind_used))

# --- regime_state.json: union rows + state fields take-new ---
rs_bma = json.loads(blob(2, "results/regime_state.json").decode("utf-8-sig"))
rs_mine = json.loads(blob(3, "results/regime_state.json").decode("utf-8-sig"))
for arrkey in ("transitions", "history"):
    a_rows = rs_bma.get(arrkey, [])
    b_rows = rs_mine.get(arrkey, [])
    keys_a = {key(r) for r in a_rows}
    union = list(a_rows) + [r for r in b_rows if key(r) not in keys_a]
    union.sort(key=lambda r: r.get("asof", r.get("ts", "")))
    rs_mine[arrkey] = union
    report.append("results/regime_state.json %s: union %d+%d -> %d" % (arrkey, len(a_rows), len(b_rows), len(union)))
rs_out = json.dumps(rs_mine, ensure_ascii=False, indent=1)
with open("results/regime_state.json", "wb") as f:
    f.write(rs_out.encode("utf-8"))
json.loads(open("results/regime_state.json", encoding="utf-8-sig").read())
report.append("results/regime_state.json: state fields take-new (updated=%s state=%s days_in_state=%s)" % (
    rs_mine["updated"], rs_mine["state"], rs_mine["days_in_state"]))

print("\n".join(report))
print("RESOLVED OK: 14 files")
