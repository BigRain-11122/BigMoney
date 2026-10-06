# -*- coding: utf-8 -*-
p = "results/_r769bma_w156_band_gate.py"
src = open(p, encoding="utf-8").read()
src = src.replace(
    "MSG-2026-10-06-0943-bma-w156-seat.md",
    "MSG-2026-10-06-1009-bma-w156-seat.md")
old_note = ('"seat_commit": "1fedffbe4 published (r769 pre-seat push, '
            'r565 law; W155 finalize products + bm-c r610 merge absorbed '
            'in the same push)"')
new_note = ('"seat_commit": "ffce2936f published (r769 pre-seat push, '
            'r565 law; W155 finalize products + bm-c r611 wave '
            'merge-absorbed in the same-window push d27177b43)"')
assert src.count(old_note) == 1, src.count(old_note)
src = src.replace(old_note, new_note)
open(p, "w", encoding="utf-8", newline="\n").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("gate patched + compiled")
