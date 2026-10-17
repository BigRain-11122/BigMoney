# -*- coding: utf-8 -*-
# r1084 bm-c: W265 derive ctxdump3 (final faces before authoring)
import io
t = io.open("results/_w264bmc_freeze_edits.py", encoding="utf-8", newline="").read()
lines = t.split("\n")
print("w263bma_paths =", t.count("_w263bma_"))
print("w262bmc_paths =", t.count("_w262bmc_"))
print("n1w263dash =", t.count("n1w263-"))
print("w262lc =", t.count("w262_"))
for i, l in enumerate(lines):
    s = l.strip()
    if "io.open(" in s and (", \"w\"" in s or "io.open" in s and "\"w\"" in s):
        print("FACE L%d: %s" % (i + 1, s[:185]))
for i, l in enumerate(lines):
    if "rev-parse" in l or "rev_list" in l:
        print("GATE L%d: %s" % (i + 1, l.strip()[:185]))
for l in lines:
    if "bm-a own seat executed at" in l:
        print("OWNSEAT FULL: %s" % l.strip()[:400])
for i, l in enumerate(lines):
    if "finalize one-pass bm-a" in l:
        print("FIN L%d: %s" % (i + 1, l.strip()[:185]))
for i, l in enumerate(lines):
    if "(bm-a r1038" in l or "splice generation r1038" in l:
        print("NOTE L%d: %s" % (i + 1, l.strip()[:185]))
for i, l in enumerate(lines):
    if "w263_freeze_sha" in l or "w263_prereg_sha" in l or "w264_prereg_sha" in l:
        print("VAR L%d: %s" % (i + 1, l.strip()[:185]))
