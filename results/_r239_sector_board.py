# -*- coding: utf-8 -*-
"""r239 T-74 s1: sector momentum board per frozen L2 (core48 mechanical subset,
blend 0.5*r20 + 0.5*r60, as of last complete bar). Read-only derivation."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "daily")
BROAD = {"510050", "510300", "510310", "510330", "510500", "510880"}
CASH = {"511010", "511090", "511260"}

rows = []
for fn in sorted(os.listdir(D)):
    sym = fn[:-4]
    if "_" in sym or sym.startswith("sh") or sym.startswith("sz"):
        continue  # core48 = no-prefix face only
    if sym in BROAD or sym in CASH:
        continue
    lines = io.open(os.path.join(D, fn), encoding="utf-8").read().splitlines()
    closes = [float(l.split(",")[4]) for l in lines[1:] if l.strip()]
    if len(closes) < 61:
        continue
    r20 = closes[-1] / closes[-21] - 1
    r60 = closes[-1] / closes[-61] - 1
    rows.append((sym, closes[-1], r20, r60, 0.5 * r20 + 0.5 * r60, lines[-1].split(",")[0]))

rows.sort(key=lambda x: -x[4])
print("as-of:", rows[0][5], "| sector faces:", len(rows))
for i, (sym, c, r20, r60, b, d) in enumerate(rows, 1):
    print(f"{i:2d} {sym} close={c:.3f} r20={r20*100:+.2f}% r60={r60*100:+.2f}% blend={b*100:+.2f}%")
