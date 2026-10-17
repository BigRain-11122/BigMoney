# -*- coding: utf-8 -*-
# r1084-continuation PRE-SPLICE needle-heal v2 (IDEMPOTENT: v1 applied E1-E4
# and wrote the file; v1's final aggregate assert used a PLAIN-quote needle
# for the mirror-b face which in DST source bytes is ESCAPED
# (\"b_exit_seed_base\") -- needle-count-0 abort, zero file damage, edits
# already landed + py_compile green. v2 = verify-focused + re-runnable.)
# Defect family = W264 post-splice heal r1076 H1/H2/H3 (un-rolled _set_wave +
# self-check indexes), healed here PRE-splice one generation earlier.
import py_compile

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_w265bmc_freeze_edits_TOL.py"
t = open(P, "rb").read().decode("utf-8")

edits = [
    ('  "machine": "bm-c", "wave": 263,',
     '  "machine": "bm-c", "wave": 265,'),
    ('"    _set_wave(263)",',
     '"    _set_wave(265)",'),
    ('WAVE_CONFIGS[264]["a_seed_base"] == {a_lo} == {w264_b_tail} + 1',
     'WAVE_CONFIGS[265]["a_seed_base"] == {a_lo} == {w264_b_tail} + 1'),
    ('WAVE_CONFIGS[264]["b_exit_seed_base"] == {b_lo} == {a_hi} + 1',
     'WAVE_CONFIGS[265]["b_exit_seed_base"] == {b_lo} == {a_hi} + 1'),
]
for old, new in edits:
    c = t.count(old)
    if c == 1:
        t = t.replace(old, new, 1)
        assert t.count(old) == 0, "old survived replace: %r" % old[:60]
    elif c == 0:
        assert t.count(new) == 1, "neither old nor healed form: %r" % old[:60]
    else:
        raise SystemExit("HEAL ABORT ambiguous count %d for %r" % (c, old[:60]))

open(P, "wb").write(t.encode("utf-8"))
py_compile.compile(P, doraise=True)

# load-bearing verification (exact)
assert t.count('"    _set_wave(265)",') == 1
assert t.count('"    _set_wave(263)",') == 0
assert t.count('WAVE_CONFIGS[265]["a_seed_base"] == {a_lo}') == 1
assert t.count('WAVE_CONFIGS[265]["b_exit_seed_base"] == {b_lo}') == 1
assert t.count('WAVE_CONFIGS[264]["a_seed_base"] == {a_lo}') == 0
assert t.count('WAVE_CONFIGS[264]["b_exit_seed_base"] == {b_lo}') == 0
assert t.count('"wave": 265,') == 1 and t.count('"wave": 263,') == 0
# upstream mirrors intact (mirror-a plain-quoted source string; b/owner escaped)
assert t.count('WAVE_CONFIGS[264]["a_seed_base"] == pf.N1_BANDS[264]["a"][0]') == 1
print("mirror aggregate: WAVE_CONFIGS[264] x%d (expect 3: a/b/owner mirrors), "
      "WAVE_CONFIGS[265] x%d (expect 2: self-checks)" % (
      t.count("WAVE_CONFIGS[264]"), t.count("WAVE_CONFIGS[265]")))
# family-6 verbatim-carry faces preserved
assert t.count("registered wave below 263 composes") >= 1
assert t.count("holds wave-263 bands, disclosed") >= 1
print("HEAL/VERIFY OK (idempotent v2): 4 faces healed pre-splice; py_compile green")
