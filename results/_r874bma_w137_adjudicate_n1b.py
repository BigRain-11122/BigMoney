# -*- coding: utf-8 -*-
"""r874 bm-a n1-selftest W137 arith_b carve-out (W99 arith_b99 r726
pattern, third leg of the same adjudication)."""
import io
import ast

N1 = r"scripts/perpetual_faces_n1.py"
src = io.open(N1, encoding="utf-8", newline="").read()
NL = "\r\n"

old = (
    '        arith_b137 = set(range(94_001, 94_201))' + NL +
    '        assert not (arith_b137 & reg_ints), \\' + NL +
    '            "W137 B window must be CLEAN (honest forward-walk ADMIT face)"'
)
new = (
    '        arith_b137 = set(range(94_001, 94_201))' + NL +
    '        # r874 adjudication (see the w137_adjudicated disclosure above):' + NL +
    '        # the window WAS clean at the r742 freeze; the' + NL +
    '        # regime5_validation_p1_null_base=94_100 point landed LATER' + NL +
    '        # (r870) -- same adjudicated exception face.' + NL +
    '        assert not (arith_b137 & (reg_ints - w137_adjudicated)), \\' + NL +
    '            "W137 B window must be CLEAN (honest forward-walk ADMIT face)"'
)
assert src.count(old) == 1, "n1 arith_b137 anchor not unique: %d" % src.count(old)
src = src.replace(old, new, 1)
io.open(N1, "w", encoding="utf-8", newline="").write(src)
ast.parse(src)
print("n1 arith_b137 carve-out landed, AST OK,", len(src), "bytes")
