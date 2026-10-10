# -*- coding: utf-8 -*-
# r845 rebase resolver: 13 UU shared regen faces -> per-file ts newer-wins (facts-driven), md twins follow json side (r939 twin-consistency)
import subprocess, json, re, sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
UU = [
    "docs/daily_report/REPORT-2026-10-11.json", "docs/daily_report/REPORT-2026-10-11.md",
    "docs/live_usage/LIVE-2026-10-11.json", "docs/live_usage/LIVE-2026-10-11.md",
    "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json", "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
    "results/regime_state.json", "results/token_usage.json", "results/update_status.json",
]

def stage_bytes(stage, path):
    r = subprocess.run(["git", "-C", REPO, "show", f":{stage}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None

def ts_of(raw):
    if raw is None:
        return None
    try:
        d = json.loads(raw.decode("utf-8", "replace"))
    except Exception:
        # md files: try first ts-ish marker line
        m = re.search(rb'"?ts"?[:=]\s*"?(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})', raw[:4096])
        if m:
            return m.group(1).decode()
        m2 = re.search(rb'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}(:\d{2})?)', raw[:4096])
        return m2.group(1).decode() if m2 else None
    def dig(o):
        for k in ("ts", "generated_at", "updated_at", "asof", "cutoff"):
            if isinstance(o, dict) and k in o and isinstance(o[k], (str, int, float)):
                return str(o[k])
        if isinstance(o, dict):
            for v in o.values():
                r = dig(v)
                if r:
                    return r
        return None
    return dig(d)

def resolve(path, side):
    flag = "--ours" if side == 2 else "--theirs"
    subprocess.run(["git", "-C", REPO, "checkout", flag, "--", path], check=True)
    subprocess.run(["git", "-C", REPO, "add", path], check=True)

report = []
# decide sides for json faces first; md twins follow their json twin
json_side = {}
for p in UU:
    if not p.endswith(".json"):
        continue
    ours, theirs = ts_of(stage_bytes(2, p)), ts_of(stage_bytes(3, p))
    if ours is None and theirs is None:
        side = 2  # unparseable both -> ours (commit content as authored)
        why = "no-ts-both->ours"
    elif theirs is None:
        side, why = 2, "theirs-no-ts->ours"
    elif ours is None:
        side, why = 3, "ours-no-ts->theirs"
    else:
        o, t = str(ours), str(theirs)
        side = 2 if o >= t else 3
        why = f"ts ours={o} theirs={t} -> {'ours' if side==2 else 'theirs'}"
    json_side[p] = side
    resolve(p, side)
    report.append((p, why))

for p in UU:
    if p.endswith(".md"):
        twin = p[:-3] + ".json"
        side = json_side.get(twin, 2)
        resolve(p, side)
        report.append((p, f"twin-follows {twin} -> {'ours' if side==2 else 'theirs'}"))

for p, why in report:
    print(f"{p}: {why}")
print(f"RESOLVED {len(report)} files")
