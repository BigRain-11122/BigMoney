# r946 bm-b: stash-vs-disk live-wins verification for the 4 daemon tick faces
import json, io, subprocess, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACES = [
    "results/saturation_engine/face_bm-b.json",
    "results/saturation_engine/history_bm-b.jsonl",
    "results/saturation_engine/state_bm-b.json",
    "results/autofill_state.bm-b.json",
]

# stash content per file
r = subprocess.run(["git", "stash", "show", "-p", "stash@{0}"], cwd=ROOT, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
cur = None
stash_ts = {}
for line in r.stdout.splitlines():
    m = re.match(r"^\+\+\+ b/(.+)$", line)
    if m:
        cur = m.group(1)
        continue
    if cur and line.startswith("+"):
        mm = re.search(r'"(?:ts|last_tick|updated)"\s*:\s*"?([^",}\n]+)', line)
        if mm and cur not in stash_ts:
            stash_ts[cur] = mm.group(1).strip()[:25]

def newest_ts(path):
    try:
        d = json.load(io.open(os.path.join(ROOT, path), encoding="utf-8"))
    except Exception:
        lines = io.open(os.path.join(ROOT, path), encoding="utf-8", errors="replace").read().strip().splitlines()
        d = json.loads(lines[-1]) if lines else {}
    for k in ("ts", "last_tick", "updated", "now"):
        if k in d:
            return str(d[k])[:25]
    return "?"

verdict = {}
for p in FACES:
    s = stash_ts.get(p, "?")
    dsk = newest_ts(p)
    verdict[p] = (s, dsk, "DISK-NEWER" if dsk >= s else "STASH-NEWER")
    print("%-52s stash=%-25s disk=%-25s %s" % (p, s, dsk, verdict[p][2]))

bad = [p for p in FACES if verdict[p][2] != "DISK-NEWER"]
print("LIVE_WINS_SAFE" if not bad else "MANUAL_REVIEW_NEEDED: %s" % bad)
