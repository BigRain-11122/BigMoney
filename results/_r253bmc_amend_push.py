#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r253 bm-c: amend tip commit with round-2 rebase receipt, push."""
import os, subprocess, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

msg = ("bm-c r253 absorb runtime state drift (dispatcher, pre-rebase) [via bm-c]\n"
       "\n"
       "REBASE-MERGE r253 round-2 receipt (pre-push amend window): replayed onto c94d8e972 "
       "(bm-a r458 window) -- 12 derived faces took origin side (r458 S6 state); "
       "x2_watch_log union 1854 lines both runs' 6+6 ts-distinct entries kept (r443 raw_decode guard); "
       "compute_audit history union 210 latest 04:54:58; "
       "CODELY merged origin r458 base + my r252 lesson entry, over-line 10320B -> r457 bm-a cold-move "
       "same-window (9989B<10240B, archive r253 bm-c section now moved 2: r455+r457 lost 0); "
       "archive +r252/+r253 bm-c sections verbatim; my dup r249/r455 cold ptrs deduped to origin's "
       "(r459 bm-a sections carry same laws). Zero-loss verified line-level.")
mf = os.path.join(ROOT, "results", "_r253bmc_amend_msg2.txt")
with open(mf, "w", encoding="utf-8", newline="\n") as f:
    f.write(msg)
subprocess.run(["git", "commit", "--amend", "-F", mf], cwd=ROOT, check=True, capture_output=True)
os.remove(mf)
r = subprocess.run(["git", "push"], capture_output=True, cwd=ROOT)
print("push rc=%d" % r.returncode)
err = r.stderr.decode("utf-8", "replace")
print(err[-500:])
