# r247 bm-a push-collision probe (12th family run): per-file ts exploration of
# :2 (origin/bm-b) vs :3 (bm-a replayed) per r242 key-probing law (no guessed
# take-sides, no None-tie silent defaults).
import json
import subprocess

def blob(rev):
    p = subprocess.run(["git", "show", rev], capture_output=True)
    return p.stdout if p.returncode == 0 else None

def probe_ts(d):
    """Probe candidate ts keys, return {key: value} of first-found non-null."""
    out = {}
    if not isinstance(d, dict):
        return out
    for k in ("generated_at", "generated", "updated", "ts", "as_of",
              "last_attempt", "time", "datetime"):
        v = d.get(k)
        if v is not None:
            out[k] = v
    return out

FILES = [
    "docs/daily_report/REPORT-2026-09-26.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.js", "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json", "results/heat_update_status.json",
    "results/lhb_update_status.json", "results/update_status.json",
    "results/token_usage.json", "results/t35_open_fill_verify.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/paper_export/export-2026-09-24.json",
    "results/paper_export/latest.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/compute_audit.json", "results/regime_state.json",
    "results/autofill_state.json",
]

for f in FILES:
    b2, b3 = blob(f":2:{f}"), blob(f":3:{f}")
    row = {"file": f}
    for tag, b in ((":2", b2), (":3", b3)):
        try:
            j = json.loads(b)
        except Exception:
            j = None
        if f.endswith(".js") and j is None:
            m = b.decode("utf-8", "replace")
            i = m.find("{")
            try:
                j = json.loads(m[i:m.rfind("}") + 1])
            except Exception:
                j = None
        row[tag] = probe_ts(j) if isinstance(j, dict) else "parse-fail-or-list"
        if f == "results/autofill_state.json" and isinstance(j, dict):
            lt = j.get("last_tick")
            row[tag + ".last_tick_ts"] = probe_ts(lt) if isinstance(lt, dict) else lt
            row[tag + ".n_launches"] = len(j.get("launches", []))
            row[tag + ".keys"] = sorted(j.keys())
    print(json.dumps(row, ensure_ascii=False))

# CODELY line-diff shape
c2 = blob(":2:CODELY.md").decode("utf-8").splitlines()
c3 = blob(":3:CODELY.md").decode("utf-8").splitlines()
s2, s3 = set(c2), set(c3)
print(json.dumps({"codely": {"|L2|": len(c2), "|L3|": len(c3),
                            "only_in_3": [l[:60] for l in c3 if l not in s2],
                            "only_in_2_count": len([l for l in c2 if l not in s3])}},
                 ensure_ascii=False))
# md twin of daily_report: side decision follows json twin (same-side law)
b2j = json.loads(blob(":2:docs/daily_report/REPORT-2026-09-26.json"))
b3j = json.loads(blob(":3:docs/daily_report/REPORT-2026-09-26.json"))
print("report json twin ts:", probe_ts(b2j), "vs", probe_ts(b3j))
