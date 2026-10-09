# r942 bm-a: rebase conflict resolver for 13 S6-generated shared faces (newest-internal-ts wins, fallback theirs=ours-r942-run)
import subprocess, json, re, os

GIT = r"C:\Program Files\Git\cmd\git.exe"

def stage(n, f):
    r = subprocess.run([GIT, "show", f":{n}:{f}"], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")

def ts_of(content, path):
    # extract the newest timestamp-looking scalar from the face
    best = None
    for m in re.finditer(r'"(?:ts|generated|asof|updated|updated_at|generated_at|time)"\s*:\s*"([^"]+)"', content):
        v = m.group(1)
        if best is None or v > best:
            best = v
    for m in re.finditer(r"\b(2026-10-1\d[T ][0-9:.+]+)", content):
        v = m.group(1)
        if best is None or v > best:
            best = v
    return best or ""

files = subprocess.run([GIT, "diff", "--name-only", "--diff-filter=U"],
                       capture_output=True).stdout.decode().split()
assert files, "no UU files?"

for f in files:
    ours = stage(2, f)
    theirs = stage(3, f)
    if ours == theirs:
        pick = "same"
        out = ours
    else:
        to, tt = ts_of(ours, f), ts_of(theirs, f)
        if tt >= to:
            pick, out = f"theirs({tt}>={to})", theirs
        else:
            pick, out = f"ours({to}>{tt})", ours
    with open(f, "w", encoding="utf-8", newline="") as fh:
        fh.write(out)
    subprocess.run([GIT, "add", f], capture_output=True)
    print(f"{f}: {pick}")
print("resolved", len(files), "faces")
