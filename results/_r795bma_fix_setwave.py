# -*- coding: utf-8 -*-
"""r795 bm-a surgical fix: W165 materializer block _set_wave(164) -> (165).
r794 deriv generator vmap-coverage gap (4th value bug this window): r792
W164 freeze advanced 163->164 (f7d34e5a7 evidence); r794 freeze_edits TOK
table missed this needle so the a3 block-replay left the stale call. Single
occurrence in the whole file, inside the new W165 mat block only."""
import io
N1 = r"scripts/perpetual_faces_n1.py"
src = io.open(N1, encoding="utf-8", newline="").read()
old = "_set_wave(164)"
n = src.count(old)
assert n == 1, f"expected 1 occurrence, got {n}"
w2 = src.find("# --- W165 materializer face")
i = src.find(old)
assert w2 > 0 and w2 < i, "the stale _set_wave(164) is not inside the W165 block"
src2 = src.replace(old, "_set_wave(165)", 1)
io.open(N1, "w", encoding="utf-8", newline="").write(src2)
import ast
ast.parse(src2)
print("surgical fix landed: _set_wave(165) in W165 mat block; AST PASS; bytes", len(src2))
