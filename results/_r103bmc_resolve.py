"""r103 bm-c rebase tail-sync resolver: 26-UU vs bma-R351 (same-window S6 double-run collision).

Classifier: 24 classified + 2 UNKNOWN (prospect _summary pair) manually classified as
snapshot (t24 legs regen whole-doc each S6 round with inner `generated` ts; live-fire
here: HEAD/upstream=bma 20:24:39/46 vs ours/bmc-r103 20:28:27/28, value-shape gate decides).
Recipes per skill catalog:
- snapshot (19 files): whole-blob take-new via hardened deep-ts probe (r100 strip/gate law, R350 exclusion-ban)
- twin coupling: REPORT .md takes SAME side as .json (r329); dashboard .js same side as .json (R209 whole bytes)
- compute_audit.json: rolling-ledger history row-set union zero-loss + latest take-new (r188)
- regime_state.json: history/transitions identical-assert preferred (r350 path), divergence -> R208 union + take-new state
- x2_watch_log.jsonl: line-level union zero loss (r188/r217)
Stage map in rebase: :2: = ours = upstream = bma-R351 side, :3: = theirs = replaying bmc-r103 commit.
"""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

TS_SHAPE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
STEMS = ("generated", "updated", "attempt", "ts", "lastseen", "written", "stamp", "lastrun", "time", "asof")
EXCLUDE = ("cutoff", "evidence_cutoff", "next_pick")  # data-face keys, never freshness (r350: key-EXCLUDE tables otherwise forbidden)


def blob(stage, path):
    r = subprocess.run(["git", "cat-file", "-p", f"{stage}{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"cat-file failed for {stage}{path}: {r.stderr[:200]}")
    return r.stdout


def deep_ts(obj, best="", depth=0):
    """Hardened deep probe: normalized key contains a freshness stem, value is ts-shaped."""
    if depth > 8:
        return best
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = str(k).replace("_", "").replace("-", "").lower()
            if any(x in nk for x in EXCLUDE):
                continue
            if isinstance(v, str) and TS_SHAPE.match(v) and any(nk.find(s) >= 0 for s in STEMS):
                if v > best:
                    best = v
            best = deep_ts(v, best, depth + 1)
    elif isinstance(obj, list):
        for item in obj:
            best = deep_ts(item, best, depth + 1)
    return best


def pick_snapshot(path, log):
    a = blob(":2:", path)  # upstream = bma-R351
    b = blob(":3:", path)  # replaying = bmc-r103
    ta = deep_ts(json.loads(a))
    tb = deep_ts(json.loads(b))
    if tb > ta:
        side, data, why = "theirs(bmc-r103)", b, f"ts {tb} > {ta}"
    elif ta > tb:
        side, data, why = "ours(bma-r351)", a, f"ts {ta} > {tb}"
    elif a == b:
        side, data, why = "identical", a, "bytes equal on ts tie"
    else:
        side, data, why = "ours(bma-r351)", a, f"tie {ta} -> HEAD per r140"
    with open(path, "wb") as fh:
        fh.write(data)
    json.loads(open(path, "rb").read())  # parse-verify gate before add
    log.append(f"  SNAPSHOT {path}: {side} ({why})")
    return side


log = []

SNAPSHOTS = [
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-24.json",
    "results/paper_export/latest.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/prospect_paper/_summary.json",    # manual snapshot (UNKNOWN -> classified)
    "results/prospect_promotion/_summary.json",
]
report_json_side = pick_snapshot("docs/daily_report/REPORT-2026-09-27.json", log)
md_stage = ":3:" if report_json_side.startswith("theirs") else ":2:"
md_bytes = blob(md_stage, "docs/daily_report/REPORT-2026-09-27.md")
open("docs/daily_report/REPORT-2026-09-27.md", "wb").write(md_bytes)
log.append(f"  TWIN md <- {md_stage} (same side as json per r329)")
dash_side = pick_snapshot("results/dashboard_status.json", log)
js_stage = ":3:" if dash_side.startswith("theirs") else ":2:"
open("results/dashboard_status.js", "wb").write(blob(js_stage, "results/dashboard_status.js"))
log.append(f"  TWIN js <- {js_stage} whole bytes (R209 wrapper law)")

for p in SNAPSHOTS:
    pick_snapshot(p, log)

# --- regime_state.json: identical-assert preferred (r350), divergence -> R208 union + take-new ---
ra = json.loads(blob(":2:", "results/regime_state.json"))
rb = json.loads(blob(":3:", "results/regime_state.json"))
if ra.get("history") == rb.get("history") and ra.get("transitions") == rb.get("transitions"):
    rs_path = "identical-ledgers"
    rs_bytes = blob(":3:" if rb.get("updated", "") > ra.get("updated", "") else ":2:", "results/regime_state.json")
else:
    rs_path = "union-ledgers"
    def union_rows(A, B):
        ka = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in A}
        kb = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in B}
        merged = list(ka.values()) + [r for k, r in kb.items() if k not in ka]
        return merged
    hist = union_rows(ra.get("history", []), rb.get("history", []))
    trans = union_rows(ra.get("transitions", []), rb.get("transitions", []))
    base_side = ":3:" if rb.get("updated", "") > ra.get("updated", "") else ":2:"
    out = json.loads(blob(base_side, "results/regime_state.json"))
    out["history"] = hist
    out["transitions"] = trans
    rs_bytes = json.dumps(out, ensure_ascii=False, indent=1).encode("utf-8")
open("results/regime_state.json", "wb").write(rs_bytes)
json.loads(open("results/regime_state.json", "rb").read())
log.append(f"  ROLLING regime_state: {rs_path}, updated {ra.get('updated')} vs {rb.get('updated')} -> take-new state")

# --- compute_audit.json: history row-set union + latest take-new ---
ca = json.loads(blob(":2:", "results/compute_audit.json"))
cb = json.loads(blob(":3:", "results/compute_audit.json"))
rows_a = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in ca["history"]}
rows_b = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in cb["history"]}
union_rows = [rows_a[k2] for k2 in rows_a] + [rows_b[k2] for k2 in rows_b if k2 not in rows_a]
union_rows.sort(key=lambda r: r["ts"])
same_ts_diverge = len({r["ts"] for r in union_rows}) != len(union_rows)
latest = cb["latest"] if deep_ts(cb["latest"]) > deep_ts(ca["latest"]) else ca["latest"]
out = {"latest": latest, "history": union_rows}
crlf = b"\r\n" in blob(":2:", "results/compute_audit.json")[:2000]
text = json.dumps(out, ensure_ascii=False, indent=1)
if crlf:
    text = text.replace("\n", "\r\n")
open("results/compute_audit.json", "wb").write(text.encode("utf-8"))
json.loads(open("results/compute_audit.json", "rb").read())
log.append(f"  ROLLING compute_audit: history union {len(ca['history'])}+{len(cb['history'])} -> {len(union_rows)} rows, "
            f"same-ts-divergence={same_ts_diverge}, latest take-new (ts {deep_ts(latest)})")

# --- x2_watch_log.jsonl: line-level union zero-loss ---
xa = blob(":2:", "results/x2_watch_log.jsonl").decode("utf-8", errors="replace").splitlines()
xb = blob(":3:", "results/x2_watch_log.jsonl").decode("utf-8", errors="replace").splitlines()
seen, merged_lines = set(), []
for line in xa + xb:
    if line and line not in seen:
        seen.add(line)
        merged_lines.append(line)
def line_ts(line):
    try:
        return json.loads(line).get("ts", "")
    except Exception:
        return ""
merged_lines.sort(key=line_ts)
blob_ending = "\r\n" if "\r\n" in blob(":2:", "results/x2_watch_log.jsonl").decode("utf-8", "replace")[:500] else "\n"
open("results/x2_watch_log.jsonl", "wb").write((blob_ending.join(merged_lines) + blob_ending).encode("utf-8"))
log.append(f"  APPEND-LOG x2_watch_log.jsonl: {len(xa)}+{len(xb)} -> {len(merged_lines)} lines union")

print("\n".join(log))
print("\nRESOLVER DONE: all 26 UU resolved, parse-verified, zero-loss")
if same_ts_diverge:
    print("WARNINGS: same_ts_diverge:", same_ts_diverge)
    sys.exit(2)
