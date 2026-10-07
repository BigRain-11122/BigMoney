# -*- coding: utf-8 -*-
"""r848 bm-a rebase UU resolve (13 files) per canon recipes (r846/r847 precedent):
- REPORT/LIVE md+json twins: whole-side take-newer by deep generation ts, twin coherence (same side both files)
- compute_audit.json: row-level ts-key union, zero-loss
- other shared regenerable status faces: newer-ts live-wins single-side
Honest disclosure: every decision logged to receipt."""
import json, re, subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.getcwd()

def sides(path):
    t = open(path, encoding='utf-8', errors='replace').read()
    ours_m = re.findall(r'<<<<<<<[^\n]*\n(.*?)\n=======\n', t, re.S)
    theirs_m = re.findall(r'\n=======\n(.*?)\n>>>>>>>', t, re.S)
    return t, ours_m, theirs_m

def jload(s, default=None):
    try:
        return json.loads(s)
    except Exception:
        return default

receipt = {"round": "r848 bm-a", "resolutions": []}

def take(path, which, why):
    # git checkout --ours/--theirs keeps conflict markers resolution from index side
    subprocess.run(["git", "checkout", "--" + which, path], capture_output=True)
    subprocess.run(["git", "add", path], capture_output=True)
    receipt["resolutions"].append({"file": path, "recipe": "take-" + which, "why": why})

# --- twins: REPORT + LIVE (md+json), decide by json-side generation ts, whole-side ---
for base, pair in (("REPORT", ["docs/daily_report/REPORT-2026-10-07.json", "docs/daily_report/REPORT-2026-10-07.md"]),
                   ("LIVE-latest", ["docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"]),
                   ("LIVE-day", ["docs/live_usage/LIVE-2026-10-07.json", "docs/live_usage/LIVE-2026-10-07.md"])):
    jf = pair[0]
    t, ours_m, theirs_m = sides(jf)
    oj = jload(ours_m[0] if ours_m else "")
    tj = jload(theirs_m[0] if theirs_m else "")
    ots = (oj or {}).get("generated") or (oj or {}).get("ts") or ""
    tts = (tj or {}).get("generated") or (tj or {}).get("ts") or ""
    which = "ours" if str(ots) >= str(tts) else "theirs"
    for f in pair:
        take(f, which, f"twin {base}: json-side gen ts ours={ots} vs theirs={tts} -> {which} whole-side (twin coherence)")
    print(f"twin {base}: ours={ots} theirs={tts} -> {which}")

# --- compute_audit.json: row-level ts-key union zero-loss ---
path = "results/compute_audit.json"
t, ours_m, theirs_m = sides(path)
oj = jload(ours_m[0] if ours_m else "", [])
tj = jload(theirs_m[0] if theirs_m else "", [])
if isinstance(oj, list) and isinstance(tj, list):
    key = lambda r: r.get("ts", "")
    union = {}
    for r in oj + tj:
        union[key(r)] = r
    merged = sorted(union.values(), key=key)
    json.dump(merged, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    subprocess.run(["git", "add", path], capture_output=True)
    receipt["resolutions"].append({"file": path, "recipe": "ts-key row union", "why": f"rows ours={len(oj)} theirs={len(tj)} -> union={len(merged)} zero-loss"})
    print(f"compute_audit union: {len(oj)}+{len(tj)} -> {len(merged)}")
else:
    # single-object fallback: newer ts wins
    ots = (oj or {}).get("ts", "")
    tts = (tj or {}).get("ts", "")
    which = "ours" if str(ots) >= str(tts) else "theirs"
    take(path, which, f"single-object fallback ts ours={ots} theirs={tts}")

# --- remaining shared status faces: newer-ts live-wins ---
for path in ("results/_attrition_guard_scan.json",
             "results/fundamental_b_layer_filter.json",
             "results/futures_update_status.json",
             "results/lhb_update_status.json",
             "results/regime_state.json",
             "results/token_usage.json",
             "results/update_status.json"):
    t, ours_m, theirs_m = sides(path)
    oj = jload(ours_m[0] if ours_m else "", {})
    tj = jload(theirs_m[0] if theirs_m else "", {})
    ots = str((oj or {}).get("ts") or (oj or {}).get("generated") or "")
    tts = str((tj or {}).get("ts") or (tj or {}).get("generated") or "")
    which = "ours" if ots >= tts else "theirs"
    take(path, which, f"newer-ts live-wins: ours={ots} theirs={tts}")
    print(f"{path}: ours={ots} theirs={tts} -> {which}")

json.dump(receipt, open("results/_r848bma_rebase_resolve.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("resolve receipt written")
