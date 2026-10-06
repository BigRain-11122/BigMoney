import subprocess, json

def ks_at(sha):
    out = subprocess.run(
        ["git", "show", f"{sha}:results/fund_value_p1/nulls.jsonl"],
        capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    ks = set()
    for ln in out.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            ks.add(json.loads(ln)["k"])
        except Exception:
            pass
    return ks

commits = subprocess.run(
    ["git", "log", "--format=%H %s", "--", "results/fund_value_p1/nulls.jsonl"],
    capture_output=True, text=True, encoding="utf-8").stdout.splitlines()

# chronological order (oldest first), LAST 20 commits
tail = [l for l in commits if l.strip()]
commits = list(reversed(tail[:20]))
prev = None
for line in commits:
    sha, msg = line.split(" ", 1)
    ks = ks_at(sha)
    missing = set(range(2000)) - ks
    gained = (prev_missing - missing) if prev is not None else None  # filled since last
    removed = (prev_ks - ks) if prev is not None else None           # REMOVED = row loss!
    tag = ""
    if removed:
        tag = f" *** ROWS REMOVED: {sorted(removed)[:20]}"
    print(f"{sha[:9]} have={len(ks):4d} missing={len(missing):3d}{tag}")
    print(f"    msg: {msg[:95]}")
    if prev is not None and removed:
        print(f"    removed ks: {sorted(removed)}")
    prev, prev_missing, prev_ks = sha, missing, ks
