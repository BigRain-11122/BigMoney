import json, subprocess, sys

GIT = r"C:\Program Files\Git\cmd\git.exe"
ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
FILES = [
    "results/compute_audit.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]

def blob(rev, path):
    out = subprocess.run([GIT, "-C", ROOT, "show", f"{rev}:{path}"],
                         capture_output=True)
    if out.returncode != 0:
        return None
    return out.stdout

def ts_of(data):
    try:
        d = json.loads(data.decode("utf-8-sig"))
    except Exception:
        return None
    for k in ("ts", "generated", "generated_at", "updated", "asof"):
        v = d.get(k)
        if isinstance(v, str):
            return v
    for k in ("last_run", "meta"):
        sub = d.get(k)
        if isinstance(sub, dict):
            for kk in ("ts", "generated"):
                v = sub.get(kk)
                if isinstance(v, str):
                    return v
    return None

resolved, notes = [], []
for f in FILES:
    ours = blob(":2", f)   # HEAD side (origin tip state)
    theirs = blob(":3", f) # incoming pick side (my absorb)
    if theirs is None and ours is None:
        notes.append(f"{f}: BOTH-None (deleted-deleted?)")
        continue
    if theirs is None:
        winner, side = ours, "ours"
    elif ours is None:
        winner, side = theirs, "theirs"
    else:
        t_ours, t_theirs = ts_of(ours) or "", ts_of(theirs) or ""
        side = "theirs" if t_theirs >= t_ours else "ours"
        winner = theirs if side == "theirs" else ours
        notes.append(f"{f}: ours ts={t_ours} theirs ts={t_theirs} -> {side}")
    with open(f"{ROOT}\\{f}", "wb") as fh:
        fh.write(winner)
    resolved.append(f)

print(json.dumps({"resolved": resolved, "notes": notes}, ensure_ascii=False, indent=1))
