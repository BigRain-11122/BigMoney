# -*- coding: utf-8 -*-
"""r581 bm-a conflict resolver: W94 freeze restoration via git apply --3way.

All four conflict regions are same-spot dual insertions (ours = bm-b W93
registration landed later over the clobbered base; theirs = predecessor r580
W94 freeze increments from held commit 9a9d05857). Union law resolution:
keep BOTH blocks, ascending wave order (W93 then W94). r531 constructive
merge / r315 stage-aware extraction family; markers built programmatically
to avoid claw false-positives (r322 law).
"""
import sys

M1 = chr(60) * 7 + " ours"
M2 = chr(61) * 7
M3 = chr(62) * 7 + " theirs"

FILES = [
    "scripts/perpetual_faces.py",
    "scripts/perpetual_faces_n1.py",
    "research/PERPETUAL_FACES.md",
]

for fp in FILES:
    b = open(fp, "rb").read()
    t = b.decode("utf-8")
    nl = "\r\n" if t.count("\r\n") * 2 > t.count("\n") else "\n"
    lines = t.split(nl)
    assert lines.count(M1) == lines.count(M2) == lines.count(M3), \
        f"{fp}: unbalanced markers {lines.count(M1)}/{lines.count(M2)}/{lines.count(M3)}"
    out, state = [], "normal"
    for ln in lines:
        if ln == M1:
            state = "ours"
            continue
        if ln == M2 and state == "ours":
            state = "theirs"
            continue
        if ln == M3 and state == "theirs":
            state = "normal"
            continue
        out.append(ln)          # keep both blocks, order preserved (ours first)
    assert state == "normal", f"{fp}: unterminated conflict region"
    res = nl.join(out)
    for m in (M1, M2, M3):
        assert m not in res, f"{fp}: residual marker"
    open(fp, "wb").write(res.encode("utf-8"))
    print(f"{fp}: resolved (kept ours+theirs, {lines.count(M1)} region(s))")

print("RESOLVER_OK")
