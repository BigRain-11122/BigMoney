# -*- coding: utf-8 -*-
"""r832 bm-c: probe the fleet-ized copyright generator's C-machine entries."""
import io
import re

SRC = r"K:\Fluxgroup\FluxGroup\软著申请材料\generate_copyright.py"
OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r832bmc_copyright_probe.txt"

src = io.open(SRC, encoding="utf-8").read()

lines = []
lines.append("len=%d src_rel_hits=%d" % (len(src), src.count("src_rel")))

m = re.search(r"SRC_ROOTS = \[(.*?)\]", src, re.S)
if m:
    lines.append("SRC_ROOTS block:")
    for r in m.group(1).strip().splitlines():
        lines.append("  " + r.strip())

lines.append("")
lines.append("--- C-machine / target keys ---")
for km in re.finditer(r'"(G\d+\w*|P\d+|FluxVerse)"\s*:\s*\{', src):
    key = km.group(1)
    start = km.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
        i += 1
    body = src[start:i - 1]
    flat = " ".join(body.split())
    if ("C机" in flat) or key in ("G02", "G09Y", "G10", "G12"):
        lines.append(key + " => " + flat[:420])
        lines.append("")

io.open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print("probe written:", OUT)
