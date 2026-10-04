import json
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
TS_KEYS = ["ts", "generated", "generated_at", "updated", "updated_at",
           "probe_ts", "scan_ts", "asof"]


def git_bytes(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT,
                       capture_output=True, timeout=30)
    if r.returncode != 0:
        return None
    return r.stdout


def face_ts(obj):
    for k in TS_KEYS:
        if k in obj and isinstance(obj[k], (str, int, float)):
            return k, str(obj[k])[:19]
    for holder in ("latest", "status", "state"):
        sub = obj.get(holder) if isinstance(obj, dict) else None
        if isinstance(sub, dict):
            for k in TS_KEYS:
                if k in sub and isinstance(sub[k], (str, int, float)):
                    return f"{holder}.{k}", str(sub[k])[:19]
    return None, None


JSON_FACES = [
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/futures_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
]
for path in JSON_FACES:
    out = []
    for rev in ("HEAD", "MERGE_HEAD"):
        b = git_bytes(rev, path)
        if b is None:
            out.append(f"{rev}=ABSENT")
            continue
        try:
            d = json.loads(b.decode("utf-8"))
        except Exception as e:
            out.append(f"{rev}=PARSE-ERR {str(e)[:40]}")
            continue
        k, v = face_ts(d)
        out.append(f"{rev}={k}:{v}")
    print(path, "|", " vs ".join(out))

print()
b_o = git_bytes("HEAD", "results/x2_watch_log.jsonl")
b_t = git_bytes("MERGE_HEAD", "results/x2_watch_log.jsonl")
o_lines = [ln for ln in b_o.decode("utf-8").split("\n") if ln.strip()]
t_lines = [ln for ln in b_t.decode("utf-8").split("\n") if ln.strip()]
print("x2 ours lines", len(o_lines), "theirs", len(t_lines))
print("ours-only:", len([l for l in o_lines if l not in t_lines]))
print("theirs-only:", len([l for l in t_lines if l not in o_lines]))
for l in [l for l in t_lines if l not in o_lines][:3]:
    print("  T-ONLY:", l[:170])
for l in [l for l in o_lines if l not in t_lines][:3]:
    print("  O-ONLY:", l[:170])
b = git_bytes("HEAD", "results/dashboard_status.js")
print()
print("dashboard_status.js head:", b.decode("utf-8", "replace")[:150])
