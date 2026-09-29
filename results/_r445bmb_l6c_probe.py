# -*- coding: utf-8 -*-
"""_r445bmb_l6c_probe.py -- extract the selftest segment st_ exactly as
the surgeon builds it (segment + prior st_ mutations), then dump the raw
repr of the L6c / L9b / L12-mask text so anchors can be fixed against
ground truth. Read-only."""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
src = open("scripts/trial_labor_w11.py", encoding="utf-8").read()


def segment(s, a, b, ia=True, ib=False):
    i = s.find(a)
    j = s.find(b, i + len(a))
    return s[i if ia else i + len(a): j + len(b) if ib else j], i, j


st_, a, b = segment(src, "def cmd_selftest() -> int:", "def _build_parser():")
print("st_ len", len(st_), "span", a, b)
# apply the exact prior mutations the surgeon applies to st_ (docstring,
# L6a, L6b) -- taken verbatim from the surgeon source
D_OLD = ("    zero cell evaluation): MOM causality / 139-bar "
         "warmup / NaN\n    comparison-artifact leg (pit-95 "
         "batch-95 + r431 erratum face) /\n    mom=none "
         "identity / eight-gate intersection / G-MOM probe "
         "anchors\n    (incl. eight-gate 256-cell 111/145 + "
         "extreme days 2/7 + core48\n    spread) / grammar "
         "structure / draw determinism / 20-source\n    "
         "exclusion loader / engine double-run determinism legs "
         "/ funnel\n    faces (dispatch / null-cell engine path "
         "/ CSV contract) + pit-95\n    finalize guards.\"\"\"")
D_NEW = ("    zero cell evaluation): MOM causality / 139-bar "
         "warmup / NaN\n    comparison-artifact leg (pit-95 "
         "batch-95 + r431 erratum face) /\n    mom=none "
         "identity / eight-gate intersection / G-MOM probe "
         "anchors\n    (incl. eight-gate 256-cell 111/145 + "
         "extreme days 2/7 + core48\n    spread) / G-RSQR probe "
         "anchors (nine-gate 512-cell 124/388 +\n    slope split "
         "213/128 + core48 spread) / grammar structure / draw\n"
         "    determinism / 24-source exclusion loader / engine "
         "double-run\n    determinism legs / funnel faces "
         "(dispatch / null-cell engine path /\n    CSV "
         "contract) + pit-95 finalize guards.\"\"\"")
A_OLD = ('    _ok("L6a axis_combos == 31,352,832 (10,450,944 x 3 '
         'std-axis "\n        "values; W10 mom-face combos x '
         'len(AXIS_STD))",\n        g["axis_combos"] == 31352832'
         '\n        == tl10.AXIS_COMBOS * len(AXIS_STD))')
A_NEW = ('    _ok("L6a axis_combos == 94,058,496 (31,352,832 x 3 '
         'rsqr-axis "\n        "values; W11 std-face combos x '
         'len(AXIS_RSQR))",\n        g["axis_combos"] == 94058496'
         '\n        == tl11.AXIS_COMBOS * len(AXIS_RSQR))')
B_OLD = ('    _ok("L6b fourteen axes present, mom == frozen '
         'binary",\n        len(g["axes"]) == 14 and '
         'g["axes"]["mom"] == AXIS_MOM)')
B_NEW = ('    _ok("L6b fifteen axes present, rsqr == frozen '
         'three-value",\n        len(g["axes"]) == 15 and '
         'g["axes"]["rsqr"] == AXIS_RSQR)')
for nm, o in (("docstring", D_OLD), ("L6a", A_OLD), ("L6b", B_OLD)):
    c = st_.count(o)
    print(nm, "count in st_ =", c)
st_ = st_.replace(D_OLD, D_NEW).replace(A_OLD, A_NEW).replace(B_OLD, B_NEW)
i = st_.find("L6c")
print("--- L6c region raw ---")
print(repr(st_[i - 10:i + 170]))
i = st_.find("generate-time re-declare window")
print("--- L9b region raw ---")
print(repr(st_[i - 120:i + 200]) if i >= 0 else "NOT FOUND in st_")
i = st_.find('        "none", "none", "none", "none", "none", gs3')
print("--- L12 mask region raw ---")
print(repr(st_[i - 260:i + 120]) if i >= 0 else "L12 raw NOT FOUND in st_")
print("L12 count in st_ =",
      st_.count('"none", "none", "none", "none", "none", gs3, vs3, ys3, cs3'))
print("L12 count in src =",
      src.count('"none", "none", "none", "none", "none", gs3, vs3, ys3, cs3'))
