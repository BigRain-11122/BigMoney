# -*- coding: utf-8 -*-
# r641 bm-b main-tree surgery (r630/r640 recipe): after net-path delivery,
# reset local main to new origin tip, targeted-checkout all differing faces
# EXCEPT daemon live-write faces (8) + post_review_criteria orphan, then
# remove worktree. Preserves live burns; syncs everything else to tip.
import os, subprocess, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def g(args, check=True):
    r = subprocess.run(["git"] + args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        sys.exit("GIT FAIL %s -> %s" % (args[:4], r.stderr[-300:]))
    return r.stdout

PRESERVE = {
    "results/autofill_state.bm-b.json",
    "results/fund_quality_p1/nulls.jsonl",
    "results/fund_value_p1/nulls.jsonl",
    "results/fund_divlowvol_p1/nulls.jsonl",
    "results/p1d_gates.json",
    "results/saturation_engine/face_bm-b.json",
    "results/saturation_engine/history_bm-b.jsonl",
    "results/saturation_engine/state_bm-b.json",
    "results/post_review_criteria.bm-b.json",
}

g(["fetch", "origin"])
before = g(["rev-parse", "--abbrev-ref", "HEAD"]).strip()
g(["reset", "--mixed", "origin/main"])
st = g(["status", "--porcelain"])
lines = [l for l in st.splitlines() if l.strip()]
checkout, preserved = [], []
for l in lines:
    path = l[3:].strip().strip('"')
    tag = l[:2]
    if path in PRESERVE:
        preserved.append((tag, path))
        continue
    if tag.strip() == "??":
        continue
    checkout.append(path)
if checkout:
    for i in range(0, len(checkout), 40):
        g(["checkout", "--"] + checkout[i:i + 40])
print("checked out %d faces; preserved %d:" % (len(checkout), len(preserved)))
for t, p in preserved:
    print("  PRESERVE", t, p)
st2 = g(["status", "--porcelain"])
print("--- post-surgery status ---")
print(st2.strip() or "(clean)")
wt = os.path.join(os.environ.get("TEMP", "."), "bmb-wt-r641")
r = subprocess.run(["git", "worktree", "remove", "--force", wt], capture_output=True, text=True)
print("worktree removed rc=%d" % r.returncode)
tip = g(["rev-parse", "HEAD"]).strip()
remote = g(["ls-remote", "origin", "main"]).split()[0]
print("MAIN TREE: HEAD=%s remote=%s equal=%s" % (tip[:9], remote[:9], tip == remote))
