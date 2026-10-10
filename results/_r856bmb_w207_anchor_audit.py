# -*- coding: utf-8 -*-
# r856 bm-b: W207 staged splice editor -- full anchor/needle audit probe
# (post-W206-finalize execution window; catches every physical-byte needle
# drift against the LIVE files in one pass before the splice re-run)
import re

n1_t = open('scripts/perpetual_faces_n1.py', 'rb').read().decode('utf-8')
pf_t = open('scripts/perpetual_faces.py', 'rb').read().decode('utf-8')

def line_indent_of(t, needle, which='first'):
    ms = [m.start() for m in re.finditer(re.escape(needle), t)]
    if not ms:
        return None, 0
    p = ms[0] if which == 'first' else ms[-1]
    ls = t.rfind('\n', 0, p) + 1
    line = t[ls:t.find('\n', ls)]
    return line[:len(line) - len(line.lstrip(' '))], len(ms)

checks = []
# --- n1 needles used by the staged editor ---
for nm, needle in [
    ("CFG_I  '206: {\"batch\"'", '206: {"batch"'),
    ("PRE_KEY_I  prereg W206", '"prereg": ("research/PERPETUAL_N1_W206_PREREG.md'),
    ("PRE_I  pre-run first-occ", '"pre-run; design = frozen v1 null calibration verbatim, "'),
    ("MEM_I  a_seed_base 468_004 (STAGED EXPECTED)", '"a_seed_base": 468_004'),
    ("MEM_I  a_seed_base 468004 (LANDED ACTUAL)", '"a_seed_base": 468004'),
]:
    ind, cnt = line_indent_of(n1_t, needle)
    checks.append((nm, ind, cnt))
# PRE indent: W206 entry's own pre-run line vs first occurrence
w206_pre = [m.start() for m in re.finditer(re.escape('"pre-run; design = frozen v1 null calibration verbatim, "'), n1_t)]
w206_positions = [m.start() for m in re.finditer(re.escape('206: {"batch"'), n1_t)]
if w206_positions:
    p0 = w206_positions[0]
    own = [p for p in w206_pre if p > p0]
    if own:
        ls = n1_t.rfind('\n', 0, own[0]) + 1
        line = n1_t[ls:n1_t.find('\n', ls)]
        checks.append(("PRE_I  W206-own pre-run indent (should match first-occ indent)", line[:len(line)-len(line.lstrip(' '))], len(w206_pre)))
# --- n1 cfg close anchor (both EOL conventions) ---
for cand in ('\n', '\r\n'):
    s = ('                       }' + cand + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
    checks.append((f"cfg close anchor EOL={'CRLF' if cand==chr(13)+chr(10) else 'LF'} count", None, n1_t.count(s)))
# --- n1 block anchors ---
for nm, needle, want in [
    ("T-141 marker count", '    # --- T-141 s2 lane face', 1),
    ("print '+ T-141 s2  count", '          "+ T-141 s2 ', 1),
    ("W205 materializer block", '    # --- W205 materializer face', 1),
    ("W206 materializer block", '    # --- W206 materializer face', 1),
    ("parity marker", '        # registered row parity (r307 pinned constants, recent estate)', None),
    ("leg204", '        assert pf.N1_BANDS[204] == {', None),
]:
    ind, cnt = line_indent_of(n1_t, needle)
    checks.append((nm, ind, cnt))
# --- pf needles ---
for nm, needle in [
    ("ROW_I  '206: {\"a\"'", '206: {"a"'),
    ("ROWC_I owner first-occ", '"engine_owner": "bm-c"},'),
]:
    ind, cnt = line_indent_of(pf_t, needle)
    checks.append((nm, ind, cnt))
# pf owner indent of the W206 row specifically
p206 = pf_t.find('206: {"a"')
if p206 > 0:
    own = pf_t.find('"engine_owner": "bm-c"},', p206)
    ls = pf_t.rfind('\n', 0, own) + 1
    line = pf_t[ls:pf_t.find('\n', ls)]
    checks.append(("ROWC_I  W206-own owner indent", line[:len(line)-len(line.lstrip(' '))], 1))
# pf close anchor both EOL conventions
for cand in ('\n', '\r\n'):
    s = ('         "engine_owner": "bm-c"},' + cand + '}' + cand + '# v1 + ext(wave-1) in-use bands')
    checks.append((f"pf close anchor EOL={'CRLF' if cand==chr(13)+chr(10) else 'LF'} count", None, pf_t.count(s)))

for nm, ind, cnt in checks:
    print(f"{nm!r:70s} indent={ind!r} count={cnt}")
