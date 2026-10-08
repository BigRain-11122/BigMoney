# -*- coding: utf-8 -*-
"""r893 bm-a DRY-debug3: enumerate every r892 occurrence (context) in the
tokenized+rolled W191 draft to reconcile the residual count."""
import ast
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
blob = open(r"results/_r893bma_w191_prereg_src.txt", "rb").read().decode("utf-8")
# replicate S88 + BACK211 rolls minimally: run the buildgen's logic by
# importing its constants is complex; instead re-run the whole buildgen
# logic in-process is not possible (it asserts).  Simplest: re-execute
# the emitted tool's transform on a COPY (no write) by reusing the
# buildgen source through exec with the DRY portion only.
# -- here: exec the buildgen but stop before the r892-count assert by
#    monkeypatching: easier to just re-derive by running the buildgen's
#    steps via exec of its source with a guard.
src = io.open(r"results/_r893bma_w191_buildgen.py", encoding="utf-8").read()
# cut the file at the r892 assert, exec everything before it
idx = src.find('assert _n892 == 17')
assert idx > 0
code = src[:idx]
ns = {"__name__": "_drydbg"}
exec(compile(code, "_r893bma_w191_buildgen_partial", "exec"), ns)
out_t = ns["out_t"]
n = 0
for m in re.finditer(r"r892", out_t):
    n += 1
    i = m.start()
    print("#%d @%d:" % (n, i), out_t[max(0, i - 55):i + 30]
          .encode("unicode_escape").decode("ascii"))
print("total:", n)
print("r893:", out_t.count("r893"))
