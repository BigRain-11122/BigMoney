"""r1078 rebase conflict resolver: x2_watch_log line-union + max-ts newer-wins (r986/r1028 law)."""
import json, re, subprocess, sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
conflicted = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
                           cwd=REPO, capture_output=True, text=True).stdout.split()

TS_RE = re.compile(r'"(?:ts|updated|updated_at|generated|generated_at|asof|cutoff|clock|last_run|time|stamp)"\s*:\s*"?(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})')

def blob(path, rev):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=REPO, capture_output=True)
    return r.stdout.decode("utf-8", "replace")

def max_ts(text):
    found = TS_RE.findall(text)
    return max(found) if found else ""

resolved, unioned, tie_theirs, tie_ours = [], [], [], []
for f in conflicted:
    ours = blob(f, "HEAD")       # origin/main side
    theirs = blob(f, "REBASE_HEAD")  # my pre-absorb side
    if f.endswith(".jsonl"):
        keep, seen = [], set()
        for line in ours.splitlines() + theirs.splitlines():
            if line.strip() and line not in seen:
                seen.add(line); keep.append(line)
        new = "\n".join(keep) + "\n"
        open(f, "w", encoding="utf-8", newline="\n").write(new)
        unioned.append(f); resolved.append(f); continue
    to, tt = max_ts(ours), max_ts(theirs)
    if tt > to:
        pick, side = theirs, "theirs"
    elif to > tt:
        pick, side = ours, "ours"
    else:
        pick, side = theirs, "theirs-tie"
        (tie_theirs if not tt else tie_ours).append(f)
    open(f, "w", encoding="utf-8", newline="").write(pick)
    resolved.append(f)

print(json.dumps({"resolved": len(resolved), "unioned": unioned,
                  "newer_ours": [f for f in resolved if f not in unioned and f not in tie_theirs and max_ts(blob(f,'HEAD')) > max_ts(blob(f,'REBASE_HEAD'))],
                  "tie_no_ts": tie_theirs, "faces": conflicted}, ensure_ascii=False, indent=1))
