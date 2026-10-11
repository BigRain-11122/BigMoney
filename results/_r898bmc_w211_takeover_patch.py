# -*- coding: utf-8 -*-
# r898: W211 freeze editor takeover-compatibility patch (W210 bm-b->bm-c takeover
# landed @ d5ec83b72; per the W209 editor's W208-takeover precedent the upstream
# gate must accept the transferred owner with commit verification + live-derive
# ordinal re-anchor. Fail-closed: every anchor must hit exactly once.)
import io, sys

P = 'results/_w211bmc_freeze_edits.py'
t = io.open(P, encoding='utf-8', newline='').read()
EOL = '\r\n' if t.count('\r\n') > (t.count('\n') - t.count('\r\n')) else '\n'

def patch(old, new, what):
    global t
    old = old.replace('\n', EOL)
    new = new.replace('\n', EOL)
    n = t.count(old)
    assert n == 1, f"anchor {what}: count {n} != 1"
    t = t.replace(old, new, 1)
    print("patched:", what)

# P1: gate0.5 upstream owner assert -> takeover-compatible + commit verify
patch(
 'assert W210.get("engine_owner") == "bm-b", \\\n'
 '    f"W210 row not landed as declared (bm-b seat owner expected): {W210} -- five-face freeze missing;" \\\n'
 '    " if a takeover face exists the freeze window MUST re-derive this editor honestly"',
 'assert W210.get("engine_owner") in ("bm-b", "bm-c"), \\\n'
 '    f"W210 row not landed as declared (bm-b seat owner expected; bm-c r898 takeover face allowed): {W210} -- five-face freeze missing;" \\\n'
 '    " if a takeover face exists the freeze window MUST re-derive this editor honestly"\n'
 'if W210.get("engine_owner") == "bm-c":\n'
 '    tk = git("cat-file", "-t", "d5ec83b72")\n'
 '    assert tk.returncode == 0 and tk.stdout.decode().strip() == "commit", \\\n'
 '        "W210 takeover commit d5ec83b72 missing -- ownership face unverified, abort"',
 'P1 gate0.5 owner assert')

# P2: ordinal re-anchor (post-W210 registration: owner 201; bmc 40 under takeover)
patch(
 'assert len(owner_rows_live) == 200 and len(bmc_rows_live) == 39, \\\n'
 '    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bmc={len(bmc_rows_live)} (expect 200/39 post-W208+W209+W210 registration)"',
 '_expected_bmc = 40 if W210.get("engine_owner") == "bm-c" else 39\n'
 'assert len(owner_rows_live) == 201 and len(bmc_rows_live) == _expected_bmc, \\\n'
 '    f"leg0 ordinal drift at freeze time: owner={len(owner_rows_live)} bmc={len(bmc_rows_live)} (expect 201/{_expected_bmc} post-W208+W209+W210 registration; W210 takeover r898 face: bm-c 40th own wave, this candidate = 41st, live derive governs r587/r359)"',
 'P2 ordinal assert')

# P3: gate0.5 print narrative -> dynamic owner + 41st ordinal disclosure
patch(
 'print(f"gate0.5 OK: W210 landed (freeze {w210_freeze_sha[:10]}, owner=bm-b), W210+W209+W208 finalize products present "\n'
 '      f"(W210 ledger head {w210_total}, merged n={w210_merged_n}); owner rows {len(owner_rows_live)} + candidate, "\n'
 '      f"bm-c rows {len(bmc_rows_live)} + candidate (40th own wave, attempt-continuity face; probe receipt leg0 "\n'
 '      f"bmc_ordinal=40 == rows+1 EXACT)")',
 'print(f"gate0.5 OK: W210 landed (freeze {w210_freeze_sha[:10]}, owner={W210.get(\'engine_owner\')} "\n'
 '      f"[r898 takeover face, commit d5ec83b72 verified when bm-c]), W210+W209+W208 finalize products present "\n'
 '      f"(W210 ledger head {w210_total}, merged n={w210_merged_n}); owner rows {len(owner_rows_live)} + candidate, "\n'
 '      f"bm-c rows {len(bmc_rows_live)} + candidate (41st own wave per the W210 takeover r898 re-derive; "\n'
 '      f"probe receipt leg0 bmc_ordinal=40 seat-time face disclosed -- the takeover shifted the own-ordinal +1, "\n'
 '      f"live derive at freeze time governs r587/r359)")',
 'P3 gate0.5 print narrative')

# P4: W210 pf row owner line assert -> takeover-compatible
patch(
 'assert \'"engine_owner": "bm-b"\' in w210_own_line, \\\n'
 '    f"W210 owner line unexpected bytes: {w210_own_line!r}"',
 'assert (\'"engine_owner": "bm-b"\' in w210_own_line) or (\'"engine_owner": "bm-c"\' in w210_own_line), \\\n'
 '    f"W210 owner line unexpected bytes: {w210_own_line!r}"\n'
 'if \'"engine_owner": "bm-c"\' in w210_own_line:\n'
 '    assert "takeover r898" in w210_own_line, "W210 bm-c owner line lacks the takeover r898 annotation"',
 'P4 W210 owner line assert')

# P5/P6: dynamic full-line replacement (marker unique -> whole line swapped)
def patch_line(marker, must_contain, new_line, what):
    global t
    n = t.count(marker)
    assert n == 1, f"{what}: marker count {n} != 1"
    ls = t.rfind(EOL, 0, t.find(marker)) + len(EOL)
    le = t.find(EOL, ls)
    old_line = t[ls:le]
    assert must_contain in old_line, f"{what}: must_contain missing in {old_line!r}"
    t = t[:ls] + new_line + t[le:]
    print("patched:", what)

# P5: w210_leg generated row -> live owner derive (f-string line)
patch_line(
    '"engine_owner": "bm-b"},',
    'engine_owner',
    'f\'                                    "engine_owner": "{W210.get("engine_owner")}", \\\\\',',
    'P5 w210_leg live owner')

# P5b: w210_leg error narrative -> takeover disclosure
patch_line(
    '"registered W210 row parity drift (r307; bm-b five-face freeze)"',
    'parity drift',
    '\'            "registered W210 row parity drift (r307; bm-b five-face freeze; r898 takeover bm-b->bm-c face disclosed)"\',',
    'P5b w210_leg narrative')

# P6: W211 block upstream mirror owner assert -> live derive (f-string line)
patch_line(
    'pf.N1_BANDS[210].get("engine_owner") == "bm-b"',
    'pf.N1_BANDS[210]',
    'f\'            pf.N1_BANDS[210].get("engine_owner") == "{W210.get("engine_owner")}", \\\\\',',
    'P6 W211 mirror owner assert')

# P6b: mirror drift error narrative -> takeover disclosure
patch_line(
    '"W211 upstream W210 engine_owner mirror drift (law-mirror parity)"',
    'law-mirror parity',
    '\'            "W211 upstream W210 engine_owner mirror drift (law-mirror parity; r898 takeover bm-b->bm-c face disclosed)"\',',
    'P6b mirror narrative')

# P7: PRE narrative "bm-b five-face freeze" -> takeover disclosure
patch_line(
    'number law after the REGISTERED W210 row bm-b five-face freeze',
    'REGISTERED W210 row',
    ' "number law after the REGISTERED W210 row five-face freeze (seat published by bm-b MSG-20261011-0319; r898 TAKEOVER: bm-b armed lane stalled 94min >> 20min GM re-assignment gate -> bm-c executed the freeze, engine_owner bm-b->bm-c, bands unchanged R250, notice MSG-2026-10-12-0020 @ c64bc2287 pre-pushed), ",',
    'P7 PRE narrative')

# P8: hdr narrative -> takeover disclosure
patch_line(
    'REGISTERED W210 row (bm-b five-face freeze',
    'REGISTERED',
    'f"    #     REGISTERED W210 row (five-face freeze {w210_freeze_sha[:10]}; seat published by bm-b, r898 TAKEOVER: bm-b hb-stall 94min -> bm-c executed per GM re-assignment + CEO fill-order standing, bands unchanged R250, notice MSG-2026-10-12-0020 @ c64bc2287; engine_owner at W211 freeze governs) --",',
    'P8 hdr narrative')

# P9: gate0.5 header-comment narrative
patch(
 '# ---------- gate 0.5: W210 five-face landed + W210 finalize product present ----------',
 '# ---------- gate 0.5: W210 five-face landed + W210 finalize product present ----------\n'
 '# (r898 takeover face: the W210 freeze was executed by bm-c per GM re-assignment;\n'
 '#  owner accepted in (bm-b, bm-c) with takeover-commit verification, W208-takeover\n'
 '#  gate0.5 precedent applied verbatim)',
 'P9 gate0.5 header comment')

io.open(P, 'w', encoding='utf-8', newline='').write(t)
import py_compile
py_compile.compile(P, doraise=True)
print('compile OK -- all 9 patches landed')
