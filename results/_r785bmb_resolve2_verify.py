# r785 bm-b post-resolve-2 verification: parse/marker/twin/union asserts on 16 faces (r185 law).
import subprocess, json, hashlib, re

FACES = {
 "docs/daily_report/REPORT-2026-10-06.json": "json",
 "docs/daily_report/REPORT-2026-10-06.md": "text_theirs",
 "docs/live_usage/LIVE-2026-10-06.json": "json",
 "docs/live_usage/LIVE-2026-10-06.md": "text_theirs",
 "docs/live_usage/LIVE-latest.json": "json",
 "docs/live_usage/LIVE-latest.md": "text_theirs",
 "results/_attrition_guard_scan.json": "json",
 "results/compute_audit.json": "json",
 "results/fundamental_b_layer_filter.json": "json",
 "results/futures_update_status.json": "json",
 "results/lhb_update_status.json": "json",
 "results/regime_state.json": "json",
 "results/scorecard_v1.json": "json",
 "results/strategy_scorecard.json": "json",
 "results/token_usage.json": "json",
 "results/update_status.json": "json",
}
MARK = re.compile(r"^(<{7}|={7}|>{7})", re.M)
report, fails = {}, []

def blob(stage, path):
    h = subprocess.run(["git", "rev-parse", "-q", "--verify", f":{stage}:{path}"],
                       capture_output=True, text=True).stdout.strip()
    return subprocess.run(["git", "cat-file", "blob", h], capture_output=True).stdout if h else None

for p, kind in FACES.items():
    raw = open(p, "rb").read()
    text = raw.decode("utf-8", "replace")
    entry = {"bytes": len(raw), "sha16": hashlib.sha256(raw).hexdigest()[:16],
             "conflict_markers": len(MARK.findall(text))}
    if entry["conflict_markers"]:
        fails.append((p, "conflict markers"))
    if kind == "json":
        try:
            json.loads(text)
        except Exception as e:
            fails.append((p, f"json parse: {e}"))
    elif kind == "text_theirs":
        ob = blob(3, p)
        if raw != ob:
            fails.append((p, "not byte-identical to stage3"))
    report[p] = entry

# twin same-side asserts
for a, b in [("docs/live_usage/LIVE-2026-10-06.json", "docs/live_usage/LIVE-latest.json"),
             ("docs/live_usage/LIVE-2026-10-06.md", "docs/live_usage/LIVE-latest.md")]:
    same = open(a, "rb").read() == open(b, "rb").read()
    report[f"twin_same::{a}"] = same
    if not same:
        fails.append((f"{a}!={b}", "twins differ"))

# compute_audit zero-loss: union superset of both sides
b2 = json.loads(blob(2, "results/compute_audit.json"))
b3 = json.loads(blob(3, "results/compute_audit.json"))
wt = json.loads(open("results/compute_audit.json", encoding="utf-8").read())
s2 = {json.dumps(r, sort_keys=True) for r in b2.get("history", [])}
s3 = {json.dumps(r, sort_keys=True) for r in b3.get("history", [])}
sw = {json.dumps(r, sort_keys=True) for r in wt.get("history", [])}
report["compute_audit::zero_loss"] = {"superset": (s2 | s3) <= sw, "wt_rows": len(sw)}
if not (s2 | s3) <= sw:
    fails.append(("compute_audit", "zero-loss violated"))

with open("results/_r785bmb_resolve2_verify.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump({"report": report, "fails": fails}, f, ensure_ascii=False, indent=1)
print("FAILS:", fails if fails else "NONE - all 16 faces verified")
