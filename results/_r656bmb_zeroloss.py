# -*- coding: utf-8 -*-
# r656 zero-loss check: auto-merged append jsonl faces must contain every
# line of BOTH merge parents (r188 union law; git auto-merge of tail appends
# can silently drop lines).
import io
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
CREATE = 0x08000000
FACES = [
    "results/post_review.jsonl",
    "results/fund_divlowvol_p1/nulls.jsonl",
    "results/fund_quality_p1/nulls.jsonl",
    "results/fund_value_p1/nulls.jsonl",
]


def blob(rev, path):
    p = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                       capture_output=True, creationflags=CREATE)
    return p.stdout if p.returncode == 0 else None


bad = 0
for f in FACES:
    m = blob(":0", f)
    o = blob("HEAD", f)
    t = blob("origin/main", f)
    if m is None or o is None or t is None:
        print("MISSING", f, m is None, o is None, t is None)
        bad += 1
        continue
    canon = lambda b: {ln.rstrip(b"\r") for ln in b.split(b"\n") if ln.strip()}
    ms, os_, ts_ = canon(m), canon(o), canon(t)
    lost_o = len(os_ - ms)
    lost_t = len(ts_ - ms)
    print("%s merged=%d ours=%d theirs=%d lost_ours=%d lost_theirs=%d"
          % (f, len(ms), len(os_), len(ts_), lost_o, lost_t))
    if lost_o or lost_t:
        bad += 1
print("zero-loss:", "PASS" if bad == 0 else "FAIL=%d" % bad)
sys.exit(1 if bad else 0)
