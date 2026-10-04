# -*- coding: utf-8 -*-
"""r515 bm-c regime_state conflict probe-2: structural three-way compare.
Dump stage2/stage3 key regions + array lens. Read-only, CREATE_NO_WINDOW."""
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


docs = {}
for stage, label in ((1, "base"), (2, "ours"), (3, "theirs")):
    txt = git_show(":%d:%s" % (stage, REL))
    docs[label] = json.loads(txt)
    h = docs[label].get("history", [])
    tg = docs[label].get("triggers", [])
    tr = docs[label].get("transitions", [])
    print("%s: updated=%s history_n=%d triggers_n=%d transitions_n=%d"
          % (label, docs[label].get("updated"), len(h), len(tg), len(tr)))
    if h:
        print("  history_last_ts=%r" % (h[-1].get("ts") if isinstance(h[-1], dict) else h[-1]))
    if tg:
        last_tg = tg[-1]
        print("  triggers_last=%r" % (json.dumps(last_tg, ensure_ascii=False)[:160]))

print()
print("=== stage2 (ours) lines 44-70 ===")
for i, ln in enumerate(git_show(":2:" + REL).splitlines(), 1):
    if 44 <= i <= 70:
        print("S2-%d: %s" % (i, ln[:80]))
print()
print("=== stage3 (theirs) lines 20-48 ===")
for i, ln in enumerate(git_show(":3:" + REL).splitlines(), 1):
    if 20 <= i <= 48:
        print("S3-%d: %s" % (i, ln[:80]))
print()
print("=== working tree lines 115-130 ===")
wt = open(os.path.join(ROOT, REL), encoding="utf-8").read().splitlines()
for i in range(114, min(130, len(wt))):
    print("WT-%d: %s" % (i + 1, wt[i][:80]))
