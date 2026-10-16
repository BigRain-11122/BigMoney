# -*- coding: utf-8 -*-
# r1062 bm-c: E257 splice-anchor uniqueness probe (builder preflight).
import io
t = io.open("results/_w257bmc_derive_editor.py", encoding="utf-8", newline="").read()
anchors = [
 "# ============ P1: structural faces", "# ============ P5a: numeric/anchor",
 "# ============ P5b: extraction count faces", "_PARFULL_W255 = ",
 "# ============ P5c: band literals", "# ============ P5d: ordinal/leg0",
 "# ============ P5e: A/B face structural", "# ============ P5f: probe-receipt date face",
 "# ============ structural output gates", "import io, os, subprocess, sys",
 "# age_prev255(): the W255 editor", "def rep(old, new, expect=None, tag=",
 "# mk(): build a chunk NEW text", "rep(age(_PARFULL_W256),",
 "rep(age(_LEGS_W256),", "rep(age(_DROP_W256),", "rep(age(_RCPTNOTE_W256),",
 "chunk(age(_HDR_W256),", "chunk(age(_BANDFACTS_W256),", "rep(age(_A_BASE_W256),",
 "rep(age(_A_FLOOR_W256),", "rep(age(_B_BASE_W256),", "rep(age(_RA_GATE_W256),",
 "chunk(age(_PFCMT_W256),", "chunk(age(_PRE_W256),", "rep(age(_MEM_A_W256),",
 "rep(age(_MEM_B_W256),", "chunk(age(_TAILCMT_W256),", "rep(age(_TAIL_AMSG_W256),",
 "rep(age(_EXCL_W256),", "chunk(age(_PRCHUNK_W256),", "rep(age(_SEM_A_W256),",
 "rep(age(_SEM_B_W256),", "rep(age(_DOWNSTREAM_W256),", "age(age_prev(age_prev255(",
 '1, "P5b-parfull")', '1, "P5b-legs-assert")', '1, "P5b-dropped-assert")', '1, "P5b-rcpt-note")',
 '"P5e-hdr"), "P5e-hdr")', '"P5e-pfcmt"), "P5e-pfcmt")', '"P5e-pre"), "P5e-pre")',
 '"P5e-tailcmt"), "P5e-tailcmt")', '"P5e-bandfacts"), "P5e-bandfacts")', '"P5e-pr"), "P5e-pr")',
 'mk(age(_PFCMT_W256), [', 'mk(age(_HDR_W256), [', 'mk(age(_RCPTNOTE_W256), [',
 'assert blob_wt == "ba18d525d40b20c3a151c17c7933812deaf414f2"',
 '"_w257bmc_freeze_edits.py"', '"_w257bmc_derive_editor_log.txt"', '"_w256bmc_freeze_edits.py"',
 'HEAD:results/_w256bmc_freeze_edits.py', '# downstream W258+ projection face',
 '# needle narrowed to the pre-registration numeric face', '# needle narrowed likewise',
 'W257 facts from the probe receipt',
]
for a in anchors:
    print(t.count(a), "|", a[:56])
