import json, re, subprocess

TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")

st = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.splitlines()
uu = [l[3:].strip().strip('"') for l in st if l.startswith("UU")]

def stage(path, n):
    return subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True).stdout

def max_ts(text):
    tss = TS_RE.findall(text.decode("utf-8", "replace"))
    return max(tss) if tss else ""

for f in uu:
    ours, theirs = stage(f, 2), stage(f, 3)
    pick, reason = ours, "ours"
    if f.endswith(".jsonl"):
        o = ours.decode("utf-8", "replace").splitlines()
        t = theirs.decode("utf-8", "replace").splitlines()
        seen = set(o)
        extra = [l for l in t if l not in seen and l.strip()]
        merged = [l for l in o if l.strip()] + extra
        body = "\n".join(merged) + ("\n" if merged else "")
        open(f, "w", encoding="utf-8", newline="\n").write(body)
        print(f"JSONL {f}: ours {len(o)} + theirs-new {len(extra)}")
        continue
    try:
        json.loads(ours)
        ours_ok = True
    except Exception:
        ours_ok = False
    if ours_ok:
        try:
            json.loads(theirs)
            to, tt = max_ts(ours), max_ts(theirs)
            if tt > to:
                pick, reason = theirs, "theirs newer"
        except Exception:
            pass
    else:
        try:
            json.loads(theirs)
            pick, reason = theirs, "ours unparseable"
        except Exception:
            pass
    open(f, "wb").write(pick)
    print(f"JSON  {f}: {reason}")
print("DONE", len(uu), "files")
