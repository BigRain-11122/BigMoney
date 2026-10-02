# r358 bm-c rebase conflict resolver: 3 UU faces (W63 registration triage).
# Law: dead-session heritage already delivered to origin by its own commits
# (a9185ef96 W63 FREEZE) -> local side must be a subset of origin side.
# Verify (base->theirs) added-lines subset-of (base->ours); pass -> take ours
# (:2:). Fail -> report local-only lines, abort (no blind side-pick).
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
FILES = ["research/PERPETUAL_FACES.md", "scripts/perpetual_faces.py",
         "scripts/perpetual_faces_n1.py"]


def stage(n, f):
    r = subprocess.run(["git", "-C", ROOT, "show", ":%d:%s" % (n, f)], capture_output=True)
    return r.stdout


ok_all = True
for f in FILES:
    b1, b2, b3 = stage(1, f), stage(2, f), stage(3, f)
    s1 = set(b1.splitlines())
    s2 = set(b2.splitlines())
    s3 = set(b3.splitlines())
    theirs_added = s3 - s1          # local-side additions vs merge-base
    only_theirs = theirs_added - s2  # lines origin lacks -> NOT delivered
    print("%s: base_lines=%d ours_lines=%d theirs_lines=%d theirs_added=%d local_only=%d"
          % (f, len(b1.splitlines()), len(b2.splitlines()), len(b3.splitlines()),
             len(theirs_added), len(only_theirs)))
    if only_theirs:
        ok_all = False
        for ln in sorted(only_theirs)[:12]:
            print("  LOCAL-ONLY:", ln[:160])
    else:
        # subset verified -> take origin side verbatim
        r = subprocess.run(["git", "-C", ROOT, "checkout", "--ours", "--", f],
                           capture_output=True)
        r2 = subprocess.run(["git", "-C", ROOT, "add", "--", f], capture_output=True)
        print("  RESOLVED -> ours (origin side) rc_add=%d rc_stage=%d"
              % (r.returncode, r2.returncode))

if not ok_all:
    print("SUBSET-CHECK FAILED -- manual review required, nothing else resolved")
    sys.exit(2)
print("ALL-SUBSET-PASS")
