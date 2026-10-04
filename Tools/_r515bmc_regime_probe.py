# -*- coding: utf-8 -*-
"""r515 bm-c regime_state.json conflict diagnosis probe (read-only).
Merge-mode stages: :1: base, :2: ours, :3: theirs (r701-iii law).
Compare stage blobs vs working-tree diff3 segment rebuild to find the
rebuild divergence. CREATE_NO_WINDOW git children."""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
REL = "results/regime_state.json"


def git_show(spec):
    r = subprocess.run(["git", "show", spec], cwd=ROOT, capture_output=True,
                       creationflags=CREATE)
    return (r.stdout or b"").decode("utf-8", "replace")


for stage, label in ((1, "base"), (2, "ours"), (3, "theirs")):
    txt = git_show(":%d:%s" % (stage, REL))
    try:
        json.loads(txt)
        ok = "PARSE-OK"
        keys = sorted(json.loads(txt).keys())
    except ValueError as e:
        ok = "PARSE-FAIL %s" % e
        keys = []
    nlines = len(txt.splitlines())
    print("STAGE:%d (%s) lines=%d %s top_keys=%s" % (stage, label, nlines, ok, keys))

# marker map of working tree
wt = open(os.path.join(ROOT, REL), encoding="utf-8").read()
lines = wt.split("\n")
for i, ln in enumerate(lines, 1):
    if ln.startswith(("<<<<<<<", "=======", ">>>>>>>", "|||||||")):
        print("WT-L%d: %s" % (i, ln[:50]))

# segment rebuild (same logic as resolver) and compare with :2:
segs = []
cur = []
mode = None
for ln in lines:
    if ln.startswith("<<<<<<< "):
        segs.append(("text", cur)); cur = []
        mode = "ours"; segs.append(("open", None)); continue
    if ln.startswith("||||||| "):
        segs.append(("ours", cur)); cur = []
        mode = "base"; continue
    if ln.startswith("======="):
        segs.append(("base", cur)); cur = []
        mode = "theirs"; continue
    if ln.startswith(">>>>>>> "):
        segs.append(("theirs", cur)); cur = []
        mode = None; continue
    cur.append(ln)
segs.append(("tail", cur))

rebuilt_ours = []
for kind, payload in segs:
    if kind == "text":
        rebuilt_ours.extend(payload)
    elif kind == "ours":
        rebuilt_ours.extend(payload)
    elif kind == "tail":
        rebuilt_ours.extend(payload)
rebuilt_ours_txt = "\n".join(rebuilt_ours)

stage2 = git_show(":2:" + REL)
print("REBUILT_OURS lines=%d  STAGE2 lines=%d  equal=%s"
      % (len(rebuilt_ours_txt.splitlines()), len(stage2.splitlines()),
         rebuilt_ours_txt == stage2))
# first divergence point
s2 = stage2.splitlines()
ro = rebuilt_ours_txt.splitlines()
for i in range(max(len(s2), len(ro))):
    a = s2[i] if i < len(s2) else "<EOF>"
    b = ro[i] if i < len(ro) else "<EOF>"
    if a != b:
        print("FIRST-DIVERGE line %d:\n  stage2: %r\n  rebuilt: %r" % (i + 1, a[:70], b[:70]))
        break
