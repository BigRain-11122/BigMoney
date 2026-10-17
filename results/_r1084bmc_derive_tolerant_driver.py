# -*- coding: utf-8 -*-
# r1084 bm-c: tolerant full-pass driver for results/_w265bmc_derive_editor.py.
# Purpose: surface ALL needle expectation mismatches in ONE run instead of
# one fail-closed assert at a time. Read-only w.r.t. the real DST (writes to
# _TOL scratch paths). Heal law: measure -> fix expectations -> strict run.
# Anchored textual surgery only (zero transcription: anchors are exact lines
# read from the editor source this window).
import io

SRC = "results/_w265bmc_derive_editor.py"
OUT = "results/_r1084bmc_derive_tolerant.py"
s = io.open(SRC, encoding="utf-8", newline="").read()

def sub1(a, b):
    global s
    n = s.count(a)
    assert n == 1, f"anchor not unique: {a[:60]!r} count {n}"
    s = s.replace(a, b)

# 1) DST/LOG to scratch paths
sub1('DST = "results/_w265bmc_freeze_edits.py"',
     'DST = "results/_w265bmc_freeze_edits_TOL.py"')
sub1('LOG = "results/_r1084bmc_derive_editor_log.txt"',
     'LOG = "results/_r1084bmc_derive_tolerant_log.txt"')

# 2) tolerant rep(): log mismatch, still replace (deterministic propagation)
sub1('    assert n == expect, f"[{tag}] count {n} != {expect}: {old[:100]!r}"',
     '    if n != expect:\n'
     '        log.append(f"MISMATCH [{tag}] count {n} != expect {expect}: {old[:80]!r}")')

# 3) tolerant residual sweep
sub1('    assert t.count(gone) == 0, f"residual sweep FAIL: {gone!r} count {t.count(gone)}"',
     '    if t.count(gone) != 0:\n'
     '        log.append(f"MISMATCH residual {gone!r} count {t.count(gone)}")')

# 4) tolerant presence gates
sub1('        assert c > 0, f"presence gate FAIL: {k!r} count 0"',
     '        if c == 0:\n'
     '            log.append(f"MISMATCH presence {k!r} count 0")')
sub1('        assert c == v, f"presence gate FAIL: {k!r} count {c} != {v}"',
     '        if c != v:\n'
     '            log.append(f"MISMATCH presence {k!r} count {c} != {v}")')

# 5) tolerant py_compile (log, don't raise, so LOG still gets written)
sub1('py_compile.compile(DST, doraise=True)',
     'try:\n'
     '    py_compile.compile(DST, doraise=True)\n'
     'except Exception as _e:\n'
     '    log.append(f"MISMATCH py_compile: {_e}")')

# 6) tail: print full mismatch summary
sub1('print("\\n".join(log[-4:]))',
     'mm = [ln for ln in log if ln.startswith("MISMATCH")]\n'
     'print("MISMATCH COUNT:", len(mm))\n'
     'print("\\n".join(mm))')

io.open(OUT, "w", encoding="utf-8", newline="").write(s)
print("tolerant driver written:", OUT)
