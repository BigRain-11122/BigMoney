# -*- coding: utf-8 -*-
"""r239 push-collision rebase resolver: T-74/T-75 claim race adjudication.
Law: fleet/README s4 commit-time order -> bm-a claim 09:58:58 precedes bm-b
10:05 -> bm-b YIELDS. Stage2 (rebase HEAD=origin) = bm-a side (canonical);
stage3 = bm-b claim (drops). Yield note appended; parse-verify before write."""
import json
import subprocess
import sys

ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"


def _stage(n, path):
    out = subprocess.run(["git", "-C", ROOT, "show", ":%d:%s" % (n, path)],
                         capture_output=True)
    assert out.returncode == 0, out.stderr.decode("utf-8", "replace")
    return out.stdout.decode("utf-8")


for tid in ("74", "75"):
    p = "fleet/tasks/T-2026-09-26-%s-P1.json" % tid
    s2 = _stage(2, p)
    s3 = _stage(3, p)
    d2 = json.loads(s2)
    d3 = json.loads(s3)
    print("== T-%s ==" % tid)
    print("  stage2(origin/bm-a): status=%s claimed_by=%s" % (
        d2.get("status"), str(d2.get("claimed_by"))[:110]))
    print("  stage3(bm-b claim) : status=%s claimed_by=%s" % (
        d3.get("status"), str(d3.get("claimed_by"))[:110]))
    print("  stage2 extra keys:", [k for k in d2 if k.startswith(("progress", "result", "yield"))])
