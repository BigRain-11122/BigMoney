"""Negative controls for smoke_red_root_cause (r2062 bm-c).

Two behaviours claimed by the face, each fired on a real input:
  A. same receipts, hand-edited markdown -> CHECK FAILED rc1 (r1934: this is not drift)
  B. the json face removed -> STALE face missing rc3, and `run` restores it byte-identical

Nothing outside results/_r2062bmc_* is touched.
"""
import importlib.util
import io
import os
import sys
import contextlib

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location(
    "srrc", os.path.join(BASE, "scripts", "smoke_red_root_cause.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

fails = []


def ok(cond, name):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        fails.append(name)


def run_check():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = mod.cmd_check()
    return rc, buf.getvalue()


md_backup = open(mod.MD, "rb").read()
js_backup = open(mod.OUT, "rb").read()

# A: hand-edit one character of the markdown
text = md_backup.decode("utf-8")
tampered = text.replace("| 29 |", "| 28 |", 1)
assert tampered != text
open(mod.MD, "w", encoding="utf-8", newline="\n").write(tampered)
rc, out = run_check()
ok(rc == 1 and "CHECK FAILED" in out and "STALE" not in out.split("CHECK FAILED")[0],
   "A hand-edited md -> rc1 CHECK FAILED without a STALE prefix (%r)" % out.strip()[:90])
open(mod.MD, "wb").write(md_backup)

# B: remove the json face
os.remove(mod.OUT)
rc, out = run_check()
ok(rc == 3 and "STALE face missing" in out, "B missing json -> rc3 STALE face missing (%r)"
   % out.strip()[:90])
rc_run = mod.cmd_run()
ok(rc_run == 0 and open(mod.OUT, "rb").read() == js_backup,
   "B run restores the json byte-identical")
rc, out = run_check()
ok(rc == 0, "B check green again after restore (%r)" % out.strip()[:60])

md_now = open(mod.MD, "rb").read()
ok(md_now == md_backup, "markdown byte-identical after the whole exercise")

print("SUMMARY %d/%d" % (6 - len(fails), 6))
sys.exit(1 if fails else 0)
