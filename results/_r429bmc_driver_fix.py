# -*- coding: utf-8 -*-
"""_r429bmc_driver_fix.py -- r429 bm-c repair receipt (in-session, read-modify-write).

Bug: r429 driver adaptation replaced only the forward-slash docstring form
('results/_r428bmc_s6_log.txt') while the real LOG line uses the os.path.join
segmented literal ("results", "_r428bmc_s6_log.txt") -- .Replace() no-match fell
through silently and the 'adapted: True' Select-String self-check hit the
docstring, not the LOG line (needle-hit-furniture false positive). The r429 S6
run therefore wrote its log into results/_r428bmc_s6_log.txt (r428's evidence
name). Fix: byte-level literal replace on the LOG line, restore the r428 log
from the HEAD blob (python raw bytes, D-19 law), then rerun the chain with the
fixed driver so _r429bmc_s6_log.txt is written by the committed form.
"""
import hashlib
import subprocess

def gitb(args):
    return subprocess.check_output(["git"] + args, creationflags=0x08000000)

# 1) byte-fix driver LOG literal (segmented form, exactly 1 occurrence)
p = "Tools/_r429bmc_s6.py"
b = open(p, "rb").read()
needle = b'"_r428bmc_s6_log.txt"'
n = b.count(needle)
assert n == 1, "expect exactly 1 (LOG line); docstring already _r429, got %d" % n
b2 = b.replace(needle, b'"_r429bmc_s6_log.txt"')
open(p, "wb").write(b2)
s = b2.decode("utf-8")
log_line = [l for l in s.splitlines() if l.startswith("LOG =")][0].strip()
hdr_line = [l.strip() for l in s.splitlines() if "bm-c start" in l][0]
assert "_r429bmc_s6_log.txt" in log_line, log_line
print("LOG line now:", log_line)
print("hdr line now:", hdr_line[:80])

# 2) restore r428 evidence log from HEAD blob (raw bytes)
orig = gitb(["show", "HEAD:results/_r428bmc_s6_log.txt"])
open("results/_r428bmc_s6_log.txt", "wb").write(orig)
h_work = hashlib.sha256(open("results/_r428bmc_s6_log.txt", "rb").read()).hexdigest()
h_head = hashlib.sha256(orig).hexdigest()
assert h_work == h_head
print("r428 log restored from HEAD, work==HEAD blob sha256=%s... True" % h_head[:16])
print("FIX_DONE")
