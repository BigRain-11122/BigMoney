# -*- coding: utf-8 -*-
# r1065 bm-c: builder preflight probe -- verify structural markers + true needle forms
# on BOTH the canon editor (_w259bmc_derive_editor.py) and T0 (_w259bmc_freeze_edits.py).
import io

CANON = "results/_w259bmc_derive_editor.py"
T0 = "results/_w259bmc_freeze_edits.py"
ce = io.open(CANON, encoding="utf-8", newline="").read()
t0 = io.open(T0, encoding="utf-8", newline="").read()

print("=== canon editor: sect markers / family vars ===")
for m in [
    "import io, os, subprocess, sys",
    "# age_prev255(): the W255 editor",
    "def rep(old, new, expect=None, tag=",
    "# mk(): build a chunk NEW text",
    "def mk(needle, repls, tag):",
    "# ============ P1: structural faces",
    "# ============ P5a: numeric/anchor",
    "# ============ P5b: extraction count faces",
    "_PARFULL_W255 = ",
    'rep(age("# prereg sec.3 mandate split:',
    '# receipt note (single big face: counts + generation stamp)',
    "# ============ P5c: band literals",
    "# ============ P5d: ordinal/leg0",
    "# ============ P5e: A/B face structural",
    "# ============ P5f: probe-receipt date face",
    "# ============ structural output gates",
    'io.open(DST, "w", encoding="utf-8", newline="").write(t)',
    "def age_prev3(s):",
    "def age(s):",
    "def mk258(",
    '# downstream W260+ projection face',
    '"_w259bmc_freeze_edits.py"',
    '"_w259bmc_derive_editor_log.txt"',
    '"_w258bmc_freeze_edits.py"',
    'HEAD:results/_w258bmc_freeze_edits.py',
    'assert blob_wt == "aa9ae1bf918593902cfd90b301edcfac390d2d50"',
    "_HDR_W258", "_BANDFACTS_W258", "_A_BASE_W258", "_A_FLOOR_W258", "_B_BASE_W258",
    "_RA_GATE_W258", "_PFCMT_W258", "_PRE_W258", "_MEM_A_W258", "_MEM_B_W258",
    "_TAILCMT_W258", "_TAIL_AMSG_W258", "_EXCL_W258", "_PRCHUNK_W258",
    "_SEM_A_W258", "_SEM_B_W258", "_DOWNSTREAM_W258",
    "_PARFULL_W258", "_LEGS_W258", "_DROP_W258", "_RCPTNOTE_W258",
    "age_prev3(age_prev2(age_prev(age_prev255(",
    "2026-10-17 07:3x bm-c r1063 freeze window",
    "P5a-header-window",
]:
    print("%d\t%s" % (ce.count(m), m[:110]))

print()
print("=== T0: true forms of zero-count needles ===")
import re
for pat in [r".{0,70}live-read.{0,70}", r".{0,90}leg boundary not found inside.{0,60}",
            r".{0,60}materializer face.{0,40}", r"W259\+W25\d\.\.W24\d finalize products present.{0,10}"]:
    hits = re.findall(pat, t0)
    for h in set(hits):
        print(repr(h[:170]))
    if not hits:
        print("(no hit for %s)" % pat[:40])

print()
print("=== T0: kept-assert block exact text ===")
i = t0.find('assert legs_kept.count("assert pf.N1_BANDS[") == 30')
print(repr(t0[i-30:i+260]) if i >= 0 else "NOT FOUND ==30 form")
i = t0.find('for _w in range(241, 259):')
print("fresh-loop:", repr(t0[i-20:i+60]) if i >= 0 else "NOT FOUND")
i = t0.find("m241 = re.search")
print("m241 face:", repr(t0[i-10:i+120]) if i >= 0 else "NOT FOUND")

print()
print("=== T0: P5b-direct comment block exact lines ===")
for needle in ["# block's own W241..W257 legs (17 rows) do NOT enter the estate path;",
               "# after extraction, fresh W241..W258 legs (18 rows) are added,",
               "# prereg mandate; the W259 block appends fresh W241..W258 legs (18,"]:
    i = t0.find(needle)
    print("count=%d\t%s" % (t0.count(needle), needle[:80]))

print()
print("=== canon editor: split-assert + family final-call spot checks ===")
i = ce.find('assert m241,')
print("canon split-assert:", repr(ce[i:i+140]) if i >= 0 else "NOT FOUND")
i = ce.find('rep(age(_PARFULL_W258),')
print("canon PARFULL final:", repr(ce[i:i+120]) if i >= 0 else "NOT FOUND")
i = ce.find('chunk(age(_HDR_W258),')
print("canon HDR final:", repr(ce[i:i+120]) if i >= 0 else "NOT FOUND")
