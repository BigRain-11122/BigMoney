# -*- coding: utf-8 -*-
"""Heal the W325 editor's plain-digit face (r1168/r1208 family, 6th live instance).

The wave-token map only reaches W-prefixed tokens; the registry/config KEYS are
plain digits, so the cloned editor still wrote 324 into the pf row / cfg entry and
shadowed the registered W324 face (n1 selftest aborted at the W324 block).
"""
import io

p = "results/_w325bmc_freeze_edits.py"
t = io.open(p, encoding="utf-8", newline="").read()
PAIRS = [
    ('''pf_row = (f'{ROW_I}324: {{"a": ''', '''pf_row = (f'{ROW_I}325: {{"a": '''),
    ('''    f'324: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit"''',
     '''    f'325: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit"'''),
    ('''    f'{CFG_I}324: {{"batch": "PERPETUAL-N1-W325",\'''',
     '''    f'{CFG_I}325: {{"batch": "PERPETUAL-N1-W325",\''''),
    ('''assert new_cfg.count('324: {"batch": "PERPETUAL-N1-W325"') == 1''',
     '''assert new_cfg.count('325: {"batch": "PERPETUAL-N1-W325"') == 1'''),
    ('''assert n1_t4.count('324: {"batch": "PERPETUAL-N1-W325"') == 1''',
     '''assert n1_t4.count('325: {"batch": "PERPETUAL-N1-W325"') == 1'''),
]
for old, new in PAIRS:
    c = t.count(old)
    assert c == 1, (c, old[:60])
    t = t.replace(old, new)
io.open(p, "w", encoding="utf-8", newline="").write(t)
import py_compile
py_compile.compile(p, doraise=True)
print("healed + py_compile green")
# verify no plain 324 key remains
for probe in ("""'{ROW_I}324:""", """f'324: {{"a\"""", """'{CFG_I}324:"""):
    print("probe", probe, t.count(probe))