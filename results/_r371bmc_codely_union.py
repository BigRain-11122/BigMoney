# -*- coding: utf-8 -*-
"""r371 bm-c CODELY.md conflict union resolver (bytes in/out per r530 law).

Union semantics: keep BOTH sides (HEAD = origin's bm-a r580 entries, then
theirs = this round's r371 entries), drop the diff3 base section and all
marker lines. Byte-level, encoding-proof.
"""
p = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\CODELY.md"
with open(p, "rb") as fh:
    data = fh.read()
lines = data.split(b"\n")
out = []
in_base = False
dropped = {"head": 0, "base": 0, "sep": 0, "end": 0}
for ln in lines:
    if ln.startswith(b"<<<<<<< "):
        dropped["head"] += 1
        continue
    if ln.startswith(b"||||||| "):
        in_base = True
        dropped["base"] += 1
        continue
    if ln == b"=======" or ln.startswith(b"======= "):
        in_base = False
        dropped["sep"] += 1
        continue
    if ln.startswith(b">>>>>>> "):
        dropped["end"] += 1
        continue
    if in_base:
        continue
    out.append(ln)
res = b"\n".join(out)
with open(p, "wb") as fh:
    fh.write(res)
print("union resolved: markers dropped=%s lines_in=%d lines_out=%d"
      % (dropped, len(lines), len(out)))
assert dropped["head"] == 1 and dropped["end"] == 1 and dropped["sep"] == 1, dropped
