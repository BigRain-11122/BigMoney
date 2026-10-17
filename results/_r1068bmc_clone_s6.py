# -*- coding: utf-8 -*-
"""r1068 bm-c: clone the S6 canon driver Tools/_r1063bmc_s6.py -> Tools/_r1068bmc_s6.py.

Byte-exact leg list; only the docstring header, log filename and the log-line round
label change. ASCII-only replacements; docstring replaced as a whole block.
"""
import io

SRC = "Tools/_r1063bmc_s6.py"
DST = "Tools/_r1068bmc_s6.py"

with io.open(SRC, "r", encoding="utf-8", newline="") as f:
    src = f.read()

old_doc_open = '"""r1063 bm-c S6 chain driver (canon clone of r1062): '
i0 = src.index(old_doc_open)
i1 = src.index('"""', i0 + 3) + 3
old_doc = src[i0:i1]

new_doc = '''"""r1068 bm-c S6 chain driver (canon clone of r1063; r838 canon lineage): standing-leg canon clone -- identical leg list, leg count derived at runtime honest count. Full log to results/_r1068bmc_s6_log.txt. MUST run under the SYSTEM python (Python313): embedded ComfyUI python has no pandas/akshare (r516 lesson). Every leg subprocess passes CREATE_NO_WINDOW (U060 silence law). Saturday 17:3x run -- bars cutoff 10-16 current and fully consumed by r1055/r1061 chains; next trading day Monday 10-19 15:30 => update_daily/papers legs expected honest weekend no-ops; bm-a/bm-b-owned lanes honest no-op on this machine per R31 lane guards. r1068 window = 58th-gen absorb continuation: dead r1068 window (17:17-17:23) landed W262 five-face splice e1a94b335 + engine self-burn 12/12 (06dcd6c23+b83318440) + sixgate PRE-FINALIZE ALL PASS 24th consecutive + finalize one-pass 1,000,735/K=574,320 EXACT; THIS window machine-verified estate then completed fivekeys 6/6 + sec.7/8 backfill placeholders=0 (W262 CYCLE COMPLETE; W263 seat = bm-a window per chain-order). S0.5 dual-delta FALSE both (probe 17:3x, unacked=0); smoke 49/49."""'''

assert src.count(old_doc) == 1
src = src.replace(old_doc, new_doc)
assert src.count("_r1063bmc_s6_log.txt") == 1
src = src.replace("_r1063bmc_s6_log.txt", "_r1068bmc_s6_log.txt")
old_line = 'log.write("r1062 bm-c S6 chain run %s legs=%d\\n" % (started, len(LEGS)))'
assert src.count(old_line) == 1, "log-line anchor not found"
src = src.replace(old_line, 'log.write("r1068 bm-c S6 chain run %s legs=%d\\n" % (started, len(LEGS)))')

with io.open(DST, "w", encoding="utf-8", newline="") as f:
    f.write(src)

# verify: legs identical
def legs_of(text):
    i = text.index("LEGS = [")
    j = text.index("]\n", i) + 1
    return text[i:j]
assert legs_of(src) == legs_of(io.open(SRC, encoding="utf-8").read()), "leg list drifted"
print("CLONE-OK -> %s (%d bytes)" % (DST, len(src.encode('utf-8'))))
