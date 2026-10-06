"""r628 bm-c needle probe (r612 DERIVATION LAW: every needle OLD value must be
probe-verified from ACTUAL r627 produced files BEFORE writing the r628
lineage copy -- zero off-by-one needles). Dumps all lines containing
round-tokens / chain-MD5 tokens from the 10 needle faces.
"""
import re
import os

SCR = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\.codely-cli\scratch"
OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r628bmc_needle_probe.txt"

FACES = [
    "_r627bmc_s05.py",
    "_r627bmc_s6_chain.py",
    "_r627bmc_legdiff.py",
    "_r627bmc_s7probe.py",
    "_r627bmc_s6facts.py",
    "_r627bmc_ca_probe.py",
    "_r627bmc_s7_second_scan.py",
    "_r627bmc_s6_ignite.py",
    "_r627bmc_qa_ignite.py",
    "_r627bmc_qa_poll.py",
]

PAT = re.compile(r"r62[4-8]|_r62[4-8]bmc|2137DC42|DF703B2C|59DB84C4|R62[67]_CHAIN")

lines_out = []
for f in FACES:
    p = os.path.join(SCR, f)
    if not os.path.exists(p):
        lines_out.append("!! MISSING %s" % f)
        continue
    text = open(p, encoding="utf-8").read()
    lines_out.append("===== %s =====" % f)
    for i, ln in enumerate(text.splitlines(), 1):
        if PAT.search(ln):
            lines_out.append("L%03d: %s" % (i, ln.rstrip()))

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(lines_out) + "\n")
print("WROTE %s lines=%d" % (OUT, len(lines_out)))
