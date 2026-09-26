"""r245 bm-b rebase replay resolver -- step-2 batch (26 UU incl. autofill
from step 1; this script handles the remaining 25 minus already-resolved).

Context: bm-b S7 push rejected (bm-a landed bc50b6b2 mid-round = same-
window double S6-chain run, r242 13-UU family enlarged). Classifier: 12
auto-classified + 14 UNKNOWN manually classified below (fail-closed
honored: every UNKNOWN individually probed, ts keys read from real blobs
-- r242 probe-first law).

Stage semantics during rebase: :2 ours = bm-a/main face (S6 stamps
12:12-12:13), :3 theirs = bm-b replayed face (S6 stamps 12:16-12:17 =
newer everywhere).

Disposition (probe evidence per file):
  TAKE-S3 whole blob (newest-state semantics, blob bytes verbatim =
  EOL/wrapper/format preserved): daily_report pair (json generated_at
  12:17:46>12:13:36, md same side as json twin -- r242 precedent),
  daily_scorecard.json (as_of 12:17>12:13), paper/*_paper.json x6
  (updated), paper_export pair (derived state_updated stamps only,
  positions identical), prospect _summary pair (generated),
  t35_open_fill_verify.json (ts), futures/heat/lhb/update_status.json
  (updated/ts), fundamental_b_layer_filter.json (updated),
  token_usage.json (generated), dashboard_status.json (meta.
  generated_at 12:17:48>12:13:38) + dashboard_status.js (same side by
  TWIN meta, wrapper bytes preserved -- R209/r226 law).
  UNION: compute_audit.json (history union zero-loss + take-new state),
  regime_state.json (history/transitions union), x2_watch_log.jsonl
  (line-level union -- r188/r217).
  ANCHOR-INSERT: HANDOVER.md -- bm-a origin-first row keeps its slot;
  bm-b latecomer row appended after (zero-loss line union, R210 spirit).
"""
import json
import subprocess
import sys

def blob(spec: str) -> bytes:
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"git show {spec} failed: {r.stderr.decode()[:200]}")
    return r.stdout

TAKE_S3 = [
    "docs/daily_report/REPORT-2026-09-26.json",
    "docs/daily_report/REPORT-2026-09-26.md",
    "results/daily_scorecard.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-24.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/t35_open_fill_verify.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/update_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/token_usage.json",
    "results/dashboard_status.json",
    "results/dashboard_status.js",
]

report = {"take_s3": [], "union": {}, "handover": None}

# ---- 1. take-side whole blob (bytes verbatim: EOL+wrapper preserved)
for p in TAKE_S3:
    raw = blob(f":3:{p}")
    with open(p, "wb") as fh:
        fh.write(raw)
    report["take_s3"].append(p)

# ---- 2a. compute_audit.json: history union + take-new state fields
p = "results/compute_audit.json"
ours = json.loads(blob(f":2:{p}").decode("utf-8-sig"))
theirs = json.loads(blob(f":3:{p}").decode("utf-8-sig"))
base_raw = blob(f":1:{p}")
out = dict(theirs)                              # newer snapshot face
ho = ours.get("history", [])
ht = theirs.get("history", [])
seen, union = set(), []
for rec in ho + ht:
    key = json.dumps(rec, sort_keys=True, default=str)
    if key not in seen:
        seen.add(key)
        union.append(rec)
union.sort(key=lambda r: str(r.get("ts", r.get("generated", ""))))
out["history"] = union
crlf = b"\r\n" in base_raw
with open(p, "w", encoding="utf-8", newline="") as fh:
    fh.write(json.dumps(out, ensure_ascii=False, indent=2,
                       default=str) + ("\r\n" if crlf else "\n"))
report["union"][p] = {"history": f"{len(ho)}+{len(ht)}->{len(union)}",
                      "eol": "CRLF" if crlf else "LF"}

# ---- 2b. regime_state.json: history/transitions union + take-new state
p = "results/regime_state.json"
ours = json.loads(blob(f":2:{p}").decode("utf-8-sig"))
theirs = json.loads(blob(f":3:{p}").decode("utf-8-sig"))
base_raw = blob(f":1:{p}")
out = dict(theirs)
for key in ("history", "transitions"):
    lo, lt = ours.get(key, []), theirs.get(key, [])
    seen, uni = set(), []
    for rec in lo + lt:
        k = json.dumps(rec, sort_keys=True, default=str)
        if k not in seen:
            seen.add(k)
            uni.append(rec)
    out[key] = uni
    report["union"].setdefault(p, {})[key] = f"{len(lo)}+{len(lt)}->{len(uni)}"
crlf = b"\r\n" in base_raw
with open(p, "w", encoding="utf-8", newline="") as fh:
    fh.write(json.dumps(out, ensure_ascii=False, indent=2,
                       default=str) + ("\r\n" if crlf else "\n"))
report["union"][p]["eol"] = "CRLF" if crlf else "LF"

# ---- 2c. x2_watch_log.jsonl: line-level union zero-loss
p = "results/x2_watch_log.jsonl"
lo = blob(f":2:{p}").decode("utf-8-sig").splitlines()
lt = blob(f":3:{p}").decode("utf-8-sig").splitlines()
base_raw = blob(f":1:{p}")
uni, seen = [], set()
for ln in lo + lt:
    if ln.strip() and ln not in seen:
        seen.add(ln)
        uni.append(ln)
crlf = b"\r\n" in base_raw
with open(p, "w", encoding="utf-8", newline="") as fh:
    fh.write(("\r\n" if crlf else "\n").join(uni) +
             ("\r\n" if crlf else "\n"))
report["union"][p] = {"lines": f"{len(lo)}+{len(lt)}->{len(uni)}"}

# ---- 3. HANDOVER.md: ours (bm-a row in slot) + bm-b row appended after
p = "research/HANDOVER.md"
ours_txt = blob(f":2:{p}").decode("utf-8-sig")
theirs_txt = blob(f":3:{p}").decode("utf-8-sig")
base_raw = blob(f":1:{p}")
ours_lines = ours_txt.splitlines()
theirs_lines = theirs_txt.splitlines()
mine = [l for l in theirs_lines
        if l.startswith("- 开发队列增量窗（接续版）**round 245 bm-b")]
assert len(mine) == 1, f"bm-b r245 row not unique: {len(mine)}"
# strip a single trailing blank/cleanup, append bm-b row at end
while ours_lines and not ours_lines[-1].strip():
    ours_lines.pop()
crlf = b"\r\n" in base_raw
eol = "\r\n" if crlf else "\n"
res = ours_lines + [mine[0]]
with open(p, "w", encoding="utf-8", newline="") as fh:
    fh.write(eol.join(res) + eol)
report["handover"] = {"bm_a_row_kept": True, "bm_b_row_appended": True,
                      "eol": "CRLF" if crlf else "LF"}

# ---- parse-verify every written JSON (r185 law)
verify = []
for f in TAKE_S3 + ["results/compute_audit.json",
                    "results/regime_state.json"]:
    if f.endswith(".json"):
        json.load(open(f, encoding="utf-8-sig"))
        verify.append(f)
for f in ["docs/daily_report/REPORT-2026-09-26.json"]:
    json.load(open(f, encoding="utf-8-sig"))
report["parse_verify"] = f"OK ({len(verify) + 1} json files)"

print(json.dumps(report, ensure_ascii=False, indent=1))
