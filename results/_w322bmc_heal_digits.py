# -*- coding: utf-8 -*-
# r1226 window: heal the PLAIN-DIGIT faces in the cloned W322 splice editor
# (r1171/r1186/r1206/r1208 law: row numbers / cfg keys / setwave labels are NOT
# on the wave-token cascade and must be written as TARGET values directly).
import io

p = "results/_w322bmc_freeze_edits.py"
t = io.open(p, encoding="utf-8", newline="").read()

REP = [
    # pf registry row number (own wave, plain digit)
    ("pf_row = (f'{ROW_I}321: {{\"a\": ", "pf_row = (f'{ROW_I}322: {{\"a\": "),
    ("f'321: {{\"a\": ({fmt(a_lo)}, {fmt(a_hi)}), \"b_exit\"",
     "f'322: {{\"a\": ({fmt(a_lo)}, {fmt(a_hi)}), \"b_exit\""),
    # WAVE_CONFIGS key (own wave, plain digit)
    ("f'{CFG_I}321: {{\"batch\": \"PERPETUAL-N1-W322\",",
     "f'{CFG_I}322: {{\"batch\": \"PERPETUAL-N1-W322\","),
    # post-edit count gates must name the same key they write
    ('assert new_cfg.count(\'321: {"batch": "PERPETUAL-N1-W322"\') == 1',
     'assert new_cfg.count(\'322: {"batch": "PERPETUAL-N1-W322"\') == 1'),
    ('assert n1_t4.count(\'321: {"batch": "PERPETUAL-N1-W322"\') == 1',
     'assert n1_t4.count(\'322: {"batch": "PERPETUAL-N1-W322"\') == 1'),
    # cfg prose label of the own wave (inherited lag in the upstream entry)
    ('"wave 320: "', '"wave 322: "'),
    # seat-window round label (own seat was published in the r1225 window)
    ("origin \" + SEAT_ORIGIN + \" (r1224, queue-head seat-first supply",
     "origin \" + SEAT_ORIGIN + \" (r1225, queue-head seat-first supply"),
    # upstream freeze sha grep must match the real commit subject
    ('"--grep", "W321 five-face splice"', '"--grep", "W321 five-face freeze splice"'),
]
for o, n in REP:
    c = t.count(o)
    assert c == 1, (c, o[:70])
    t = t.replace(o, n)
io.open(p, "w", encoding="utf-8", newline="").write(t)
import py_compile
py_compile.compile(p, doraise=True)
print("plain-digit faces healed; py_compile green")