# -*- coding: utf-8 -*-
# r942 diag driver: run a non-fatal copy of the W226 derive editor to expose ALL
# count mismatches (shifts + pairs + phase-4) in one pass. Real editor untouched.
import io, os, re, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "_w226bmc_derive_editor.py")
DST = os.path.join(HERE, "_r942bmc_editor_diag.py")

src = io.open(SRC, encoding="utf-8", newline="").read()

subs = [
    # 1) shift assert -> warn + proceed (replace-all regardless, so downstream
    #    state stays the real post-shift text)
    ('    assert c == mn, f"SHIFT FAIL count {c} != {mn}: {old!r}"\n    t = t.replace(old, new)',
     '    if c != mn: print(f"SHIFT MISS {c} != {mn}: {old[:70]!r}")\n    t = t.replace(old, new)'),
    # 2) rep/pair assert -> warn + return (both defs share identical assert text)
    ('    assert c == n, f"PAIR FAIL count {c} != {n}: {old[:110]!r}"\n    t = t.replace(old, new)',
     '    if c != n:\n        print(f"PAIR MISS {c} != {n}: {old[:80]!r}")\n        return\n    t = t.replace(old, new)'),
    # 3) stale/must-one asserts -> warn
    ('    assert c == 0, f"STALE TOKEN {s!r} count {c} != 0"',
     '    if c != 0: print(f"STALE VIOL {s!r} count {c}")'),
    ('    assert c == 1, f" MUST-ONE {s!r} count {c} != 1"',
     '    if c != 1: print(f"MUST-ONE VIOL {s!r} count {c}")'),
    # 4) diag output path (never touch the real editor target)
    ('OUT  = os.path.join(HERE, "_w226bmc_freeze_edits.py")',
     'OUT  = os.path.join(HERE, "_r942bmc_diag_out.py")'),
    # 5) save final text BEFORE phase-4 (stale/must_one loops + tail asserts
    #    only COUNT, never mutate t -- so the pre-save == final text)
    ('stale = [',
     '_PS = open(OUT, "w", encoding="utf-8", newline=""); _PS.write(t); _PS.close()\nstale = ['),
]
for old, new in subs:
    n = src.count(old)
    assert n >= 1, f"patch anchor missing: {old[:60]!r}"
    src = src.replace(old, new)

io.open(DST, "w", encoding="utf-8", newline="").write(src)

import runpy
print("=== DIAG RUN ===")
try:
    g = runpy.run_path(DST, run_name="__main__")
    t = g.get("t", "")
    print("=== TERRITORY DUMPS (post-all-phases text) ===")
    for mark in ["69 estate", "rows: estate", "PERPETUAL-N1-W22", "_estate_ws"]:
        for m in re.finditer(re.escape(mark), t):
            a, b = max(0, m.start() - 130), min(len(t), m.end() + 130)
            print(f"--- [{mark}] @{m.start()}:")
            print(t[a:b].replace("\n", "\\n"))
            break  # first hit per mark is enough
except SystemExit:
    print("=== DIAG END (SystemExit) ===")
except Exception:
    print("=== DIAG END (tail assert/error) ===")
    print(traceback.format_exc().splitlines()[-1])
