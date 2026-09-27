# -*- coding: utf-8 -*-
"""r334 bm-b round-3 inspect: CODELY + archive + autofill three-way structure."""
import io
import json
import subprocess


def blob(stage, path):
    return subprocess.run(["git", "show", f"{stage}:{path}"],
                          capture_output=True).stdout


for tag, s in (("ours:2", ":2"), ("theirs:3", ":3")):
    c = blob(s, "CODELY.md").decode("utf-8")
    print(f"--- CODELY {tag}: {len(c.encode())}B batches_present:",
          [b for b in ("十六批", "十七批", "十八批", "十九批", "二十批", "二十一") if b in c])
    a = blob(s, r"research/memory-archive/202609.md").decode("utf-8")
    secs = [l for l in a.splitlines() if l.startswith("## ")]
    print(f"--- ARCHIVE {tag}: {len(a.encode())}B last-3-sections:")
    for sec in secs[-3:]:
        print("   ", sec[:80])
    f = blob(s, "results/autofill_state.json").decode("utf-8")
    d = json.loads(f)
    L = d.get("launches", [])
    lt = d.get("last_tick")
    print(f"--- AUTOFILL {tag}: launches={len(L)} last={json.dumps(L[-1], ensure_ascii=False)[:160] if L else '-'} last_tick.ts={lt.get('ts') if isinstance(lt, dict) else lt}")

# my commit's CODELY/archive added lines (genuine additions)
for path in ("CODELY.md", "research/memory-archive/202609.md"):
    diff = subprocess.run(["git", "diff", "6ab7aefb^", "6ab7aefb", "--", path],
                          capture_output=True).stdout.decode("utf-8")
    added = [l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    removed = [l[1:] for l in diff.splitlines() if l.startswith("-") and not l.startswith("---")]
    print(f"\nMY 6ab7aefb {path}: +{len(added)} -{len(removed)}")
    for l in added[:6]:
        print("  +", l[:110])
