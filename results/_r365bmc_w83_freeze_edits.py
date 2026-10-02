# -*- coding: utf-8 -*-
"""r365 bm-c W82-HEAL + W83 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening.

PART 1 (W82 HEAL, r540/r519 family 9th-occurrence cure): bm-a r574 commit
e3215a98e (add -A whole-tree "phantom-D") reverted bm-b 45e05a67c's ALREADY
PUSHED W82 freeze content inside SHARED files; bm-a hotfix 5ff066442 restored
17 standalone files but MISSED the 4 shared-file content blocks:
  (A) n1.py WAVE_CONFIGS[82] entry (26 lines)
  (B) n1.py W82 selftest materializer leg (160 lines)
  (C) n1.py W82 selftest SUMMARY segment
  (D) research/PERPETUAL_FACES.md canon W82 row
All four byte-restored verbatim from the holding commit 45e05a67c (bm-b
r574 freeze). Attribution = bm-b; restorer = bm-c r365. Impact if unfixed:
bm-b W82 finalize would KeyError (WAVE_CONFIGS[82] missing) + every later
wave's selftest leg disjointness loop would KeyError on W82. Zero science
loss (no measurement data touched; W82 burn state on bm-b side per their
engine, no finalize ever ran on the broken tree).

PART 2 (W83 FREEZE): MSG-0640 FIX-A/B/C pure-insertion lineage.
W83 = SEVENTY-THIRD engine wave by MACHINE-DERIVE (engine_owner rows
72 + candidate; live prose comment-sequence carried a -1 drift at least
since W80 -- machine: W80=70th/W81=71st/W82=72nd, bm-b r574's SEVENTY-SECOND
was CORRECT, bm-a r574's "correction" was itself the wrong side; r359
counts-from-gate law), bm-c's TWENTY-SIXTH owned (rows 25 + candidate).
First free number after the registered W82 row (bm-b r574 freeze, landed
origin). Seat published=reserved MSG-20261002-1231-bmc PUSHED to origin
BEFORE this freeze (r565 law, commit 165f18f2c).

Bands: A 209_004..211_003 (== W82 A end 209_003 + 1, arithmetic
continuation zero skip, CLEAN) / B 54_401..54_600 (== W82 B end 54_400 + 1,
arithmetic continuation zero skip, CLEAN). ADMIT receipt
results/_r365bmc_w83_band_gate.py. ONE in-flight upstream seat at this
freeze: W82 bm-b (burn in flight) -- finalize chain-pending FAIL-CLOSED
r307. W1..W81 finalizes ALL LANDED (net head 542,748, K=176,120 -- W81
bm-a r574 this window). W84+ gate projection: A 211_004..213_003 CLEAN;
B 54_601..54_800 CLEAN.
"""
import subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREAT = 0x08000000  # CREATE_NO_WINDOW (session-host flash guard)
HOLD = '45e05a67c'   # bm-b r574 W82 freeze commit (holding commit for heal blocks)

def git(*a):
    r = subprocess.run(['git', '-C', REPO] + list(a), capture_output=True,
                       creationflags=CREAT)
    if r.returncode != 0:
        sys.exit('GIT FAIL %s -> %s' % (a[:3], r.stderr.decode('utf-8', 'replace')))
    return r.stdout

def show(ref, path):
    return subprocess.check_output(['git', '-C', REPO, 'show', ref + ':' + path],
                                   creationflags=CREAT).decode('utf-8', 'replace')

def load(fp):
    b = open(fp, 'rb').read()
    t = b.decode('utf-8')
    eol = '\r\n' if t.count('\r\n') * 2 > t.count('\n') else '\n'
    return t, eol

def save(fp, t):
    open(fp, 'wb').write(t.encode('utf-8'))

def rep(t, old, new, eol, tag):
    oldX = old.replace('\n', eol)
    newX = new.replace('\n', eol)
    assert t.count(oldX) == 1, f"{tag}: anchor not unique ({t.count(oldX)})"
    return t.replace(oldX, newX)

def lines_of(text):
    return text.split('\n')

FP_PF = os.path.join(REPO, 'scripts', 'perpetual_faces.py')
FP_N1 = os.path.join(REPO, 'scripts', 'perpetual_faces_n1.py')
FP_CANON = os.path.join(REPO, 'research', 'PERPETUAL_FACES.md')
TARGETS = ['scripts/perpetual_faces.py', 'scripts/perpetual_faces_n1.py',
           'research/PERPETUAL_FACES.md']

# ---------------- FIX-A: origin-blob freshness (pre-edit) --------------------
git('fetch', 'origin')
for p in TARGETS:
    r = subprocess.run(['git', '-C', REPO, 'diff', 'origin/main', '--numstat', '--', p],
                       capture_output=True, creationflags=CREAT)
    out = r.stdout.decode('utf-8', 'replace').strip()
    if r.returncode != 0:
        sys.exit(f'FIX-A git fail on {p}')
    for line in out.splitlines():
        add, dele, path = line.split('\t')
        if int(dele) > 0:
            sys.exit(f'STALE BASE (FIX-A abort): {p} shows {dele} deleted lines vs '
                     f'origin/main -- checkout origin version first (r559 clobber cure)')
print('FIX-A: all 3 tracked edit targets show zero deletions vs origin/main (fresh base)')

# ---------------- PART 1: W82 heal (byte-exact from holding commit) ---------
old_n1 = show(HOLD, 'scripts/perpetual_faces_n1.py')
old_canon = show(HOLD, 'research/PERPETUAL_FACES.md')
ol = lines_of(old_n1)

def block(lines, start_pred, end_pred, tag):
    s = None
    for i, ln in enumerate(lines):
        if start_pred(ln):
            s = i
            break
    assert s is not None, f'{tag}: start marker not found in holding commit'
    e = None
    for j in range(s + 1, len(lines)):
        if end_pred(lines[j], j, s):
            e = j
            break
    assert e is not None, f'{tag}: end marker not found'
    return '\n'.join(lines[s:e + 1]) + '\n'

# Block A: WAVE_CONFIGS[82] entry
blkA = block(ol, lambda ln: ln.strip().startswith('82: {"batch": "PERPETUAL-N1-W82"'),
             lambda ln, j, s: ln.strip().endswith('"engine_owner": "bm-b"},'),
             'W82-config')
assert blkA.count('"batch": "PERPETUAL-N1-W82"') == 1 and 'n1_w82' in blkA
# Block B: W82 selftest materializer leg
s_leg = next(i for i, ln in enumerate(ol) if ln.strip().startswith('# --- W82 materializer face'))
s_fin = next(j for j in range(s_leg, len(ol)) if ol[j].rstrip() == '    finally:')
assert ol[s_fin + 1].strip() == '_set_wave(2)'
blkB = '\n'.join(ol[s_leg:s_fin + 2]) + '\n'
assert blkB.count('W82 materializer face') >= 1 and len(blkB.split('\n')) > 100
# Block C: W82 summary segment
s_seg = next(i for i, ln in enumerate(ol) if ln.strip().startswith('"') and 'W82 materializer face' in ln)
e_seg = next(j for j in range(s_seg, len(ol)) if 'T-141 s2' in ol[j])
blkC = '\n'.join(ol[s_seg:e_seg])
assert 'W82 materializer face' in blkC and 'T-141 s2' not in blkC
# Block D: canon W82 row (single bullet line)
cl = lines_of(old_canon)
s_row = next(i for i, ln in enumerate(cl) if ln.startswith('- N1 \u6ce282\uff08'))
assert cl[s_row + 1].strip() == '', 'canon W82 row not followed by blank line'
blkD = cl[s_row] + '\n'
assert blkD.count('- N1 \u6ce282\uff08') == 1

# --- heal edit A: n1.py WAVE_CONFIGS[82] --------------------------------------
t_n1, eol_n1 = load(FP_N1)
if '"batch": "PERPETUAL-N1-W82"' in t_n1:
    print('heal-A already landed (idempotent skip)')
else:
    A_anchor = ('                            "shard_subdir": "n1_w81", "out_name": "n1_w81_results.json",\n'
                '                            "engine_owner": "bm-a"},\n')
    t_n1 = rep(t_n1, A_anchor, A_anchor + blkA, eol_n1, 'heal-A')
    save(FP_N1, t_n1)
    print('heal-A n1.py WAVE_CONFIGS[82] byte-restored (26 lines, from ' + HOLD + ')')

# --- heal edit B: n1.py W82 selftest leg -------------------------------------
t_n1, eol_n1 = load(FP_N1)
if '# --- W82 materializer face' in t_n1:
    print('heal-B already landed (idempotent skip)')
else:
    A3 = '\n    # --- T-141 s2 lane face'
    A3X = A3.replace('\n', eol_n1)
    assert t_n1.count(A3X) == 1, f'heal-B anchor not unique: {t_n1.count(A3X)}'
    t_n1 = t_n1.replace(A3X, '\n' + blkB.replace('\n', eol_n1) + A3X)
    save(FP_N1, t_n1)
    print('heal-B n1.py W82 selftest leg byte-restored (160 lines)')

# --- heal edit C: n1.py W82 summary segment ----------------------------------
t_n1, eol_n1 = load(FP_N1)
if '+ W82 materializer face' in t_n1:
    print('heal-C already landed (idempotent skip)')
else:
    ANCH = '\n          "+ T-141 s2 '
    ANCHX = ANCH.replace('\n', eol_n1)
    assert t_n1.count(ANCHX) == 1, f'heal-C anchor not unique: {t_n1.count(ANCHX)}'
    t_n1 = t_n1.replace(ANCHX, '\n' + blkC.replace('\n', eol_n1) + ANCHX)
    save(FP_N1, t_n1)
    print('heal-C n1.py W82 summary segment byte-restored')

# --- heal edit D: canon W82 row ----------------------------------------------
t_canon, eol_canon = load(FP_CANON)
if '- N1 \u6ce282\uff08' in t_canon:
    print('heal-D already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol_canon)
    assert t_canon.count(A4X) == 1, f'heal-D anchor not unique: {t_canon.count(A4X)}'
    t_canon = t_canon.replace(A4X, '\n' + blkD.replace('\n', eol_canon) + A4X)
    save(FP_CANON, t_canon)
    print('heal-D canon W82 row byte-restored')

# --- heal edit E: pf.py N1_BANDS[82] row (phantom-D reverted it too) ---------
old_pf = show(HOLD, 'scripts/perpetual_faces.py')
pl = lines_of(old_pf)
row_idx = next(i for i, ln in enumerate(pl) if ln.strip().startswith('82: {"a": (207_004'))
s_e = row_idx
while s_e > 0 and pl[s_e - 1].strip().startswith('#'):
    s_e -= 1
e_e = row_idx
while not pl[e_e].strip().endswith('"engine_owner": "bm-b"},'):
    e_e += 1
blkE = '\n'.join(pl[s_e:e_e + 1]) + '\n'
assert blkE.count('82: {"a": (207_004') == 1
t_pf, eol_pf = load(FP_PF)
if '82: {"a": (207_004' in t_pf:
    print('heal-E already landed (idempotent skip)')
else:
    AE = ('    81: {"a": (205_004, 207_003), "b_exit": (54_001, 54_200),\n'
          '         "engine_owner": "bm-a"},\n')
    t_pf = rep(t_pf, AE, AE + blkE, eol_pf, 'heal-E')
    save(FP_PF, t_pf)
    print('heal-E pf.py N1_BANDS[82] row byte-restored (comment+row, from ' + HOLD + ')')

# ---------------- PART 2: W83 freeze edits -----------------------------------
# --- edit 1: perpetual_faces.py N1_BANDS[83] ----------------------------------
FP1 = FP_PF
t1, eol1 = load(FP1)
if '83: {"a": (209_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    82: {"a": (207_004, 209_003), "b_exit": (54_201, 54_400),\n'
          '         "engine_owner": "bm-b"},\n')
    NEW = ('    82: {"a": (207_004, 209_003), "b_exit": (54_201, 54_400),\n'
           '         "engine_owner": "bm-b"},\n'
           '    # SEVENTY-THIRD ENGINE-OWNED WAVE by machine-derive (r365 bm-c\n'
           '    # freeze): engine_owner rows 72 + candidate; live prose comment\n'
           '    # ordinals carried a -1 drift at least since W80 (machine:\n'
           '    # W80=70th/W81=71st/W82=72nd -- bm-b r574 SEVENTY-SECOND was\n'
           '    # correct, bm-a r574 correction was the wrong side; r359 law).\n'
           '    # bm-c\'s TWENTY-SIXTH owned per machine-derive\n'
           '    # (engine_owner==bm-c rows 25 + candidate). Wave 83 = first free\n'
           '    # number after the registered W82 row (r511 tail-lock,\n'
           '    # fetch-checked vacancy incl. prereg path; seat published=\n'
           '    # reserved MSG-20261002-1231-bmc PUSHED to origin BEFORE this\n'
           '    # freeze per r565 early-visibility law, commit 165f18f2c).\n'
           '    # W1..W81 finalizes ALL LANDED (net head 542,748, K=176,120,\n'
           '    # W81 bm-a r574 this window); W82 bm-b (burn in flight) = ONE\n'
           '    # in-flight upstream seat at this freeze (finalize\n'
           '    # chain-pending FAIL-CLOSED r307).\n'
           '    # BOTH SIDES ARITHMETIC CONTINUATION from the W82 row tail,\n'
           '    # zero skip: A 209_004..211_003 (= W82 A end 209_003 + 1)\n'
           '    # CLEAN + B 54_401..54_600 (= W82 B end 54_400 + 1) CLEAN\n'
           '    # (single reading, no fork face, F-20261002-03 not triggered;\n'
           '    # D-20261002-05 group pin = jump-past-hit -- zero-skip here so\n'
           '    # the pin is not exercised).\n'
           '    # Machine-verified at prereg time\n'
           '    # (results/_r365bmc_w83_band_gate.py ADMIT receipt vs the\n'
           '    # 80-row pre-W83 table + live SEED_REGISTRY values + probe\n'
           '    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin\n'
           '    # slot vacancy machine-checked incl. prereg path). W84+\n'
           '    # gate projection: A 211_004..213_003 CLEAN; B 54_601..54_800\n'
           '    # CLEAN. NOT a re-pick (R250: W83 bands were never assigned).\n'
           '    83: {"a": (209_004, 211_003), "b_exit": (54_401, 54_600),\n'
           '         "engine_owner": "bm-c"},\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[83] landed (anchor=W82 row, insert after)')

# --- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[83] --------------------------
FP2 = FP_N1
t2, eol2 = load(FP2)
if '83: {"batch": "PERPETUAL-N1-W83"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w82", "out_name": "n1_w82_results.json",\n'
          '                            "engine_owner": "bm-b"},\n')
    NEW2 = A2 + (
        '                       83: {"batch": "PERPETUAL-N1-W83",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W83_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; SEVENTY-THIRD ENGINE-OWNED WAVE "\n'
        '                                       "by machine-derive (rows 72 + candidate; prose ordinal "\n'
        '                                       "drift disclosed), own-series continuation per "\n'
        '                                       "O-20261001-2355 sec.2 (first-free-number law over the "\n'
        '                                       "registered W82 row; seat published=reserved "\n'
        '                                       "MSG-20261002-1231-bmc PUSHED to origin BEFORE this "\n'
        '                                       "freeze per r565 early-visibility lesson, commit "\n'
        '                                       "165f18f2c), engine_owner=bm-c, wave 83 BOTH SIDES "\n'
        '                                       "ARITHMETIC CONTINUATION zero skip (A 209_004..211_003 "\n'
        '                                       "CLEAN + B 54_401..54_600 CLEAN; single reading, no "\n'
        '                                       "fork face, F-20261002-03 not triggered; W84+ "\n'
        '                                       "projection: A 211_004..213_003 CLEAN / B 54_601.."\n'
        '                                       "54_800 CLEAN disclosed for the next freezer); "\n'
        '                                       "W1..W81 finalizes ALL LANDED at this freeze (net "\n'
        '                                       "chain head 542,748, K=176,120, W81 bm-a r574 this "\n'
        '                                       "window); W82 bm-b = ONE in-flight upstream seat "\n'
        '                                       "(finalize chain-pending FAIL-CLOSED r307)"),\n'
        '                            "a_seed_base": 209_004,        # law sec.4 W83 A: 209_004..211_003 (arithmetic continuation)\n'
        '                            "b_exit_seed_base": 54_401,   # law sec.4 W83 B: 54_401..54_600 (arithmetic continuation)\n'
        '                            "shard_subdir": "n1_w83", "out_name": "n1_w83_results.json",\n'
        '                            "engine_owner": "bm-c"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[83] landed (anchor=W82 entry tail, insert after)')

# --- edit 3: perpetual_faces_n1.py selftest W83 leg ---------------------------
LEG83 = '''
    # --- W83 materializer face (r365 bm-c freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-c's
    #     twenty-sixth owned per machine-derive (engine_owner==bm-c
    #     rows 25 + candidate); wave 83 = first free number after the
    #     registered W82 row (bm-b r574). SEVENTY-THIRD engine wave by
    #     MACHINE-DERIVE (engine_owner rows 72 + candidate; live prose
    #     comment ordinals carried a -1 drift at least since W80 --
    #     machine: W80=70th/W81=71st/W82=72nd, bm-b r574 was correct,
    #     r359 counts-from-gate law). Seat published=reserved
    #     MSG-20261002-1231-bmc pushed to origin BEFORE this freeze
    #     (commit 165f18f2c, r565 early-visibility law). ONE in-flight
    #     upstream seat at this freeze: W82 bm-b (burn in flight) --
    #     finalize chain-pending FAIL-CLOSED r307 at run time. W1..W81
    #     finalizes ALL LANDED (net head 542,748, K=176,120, W81 bm-a
    #     r574 this window). ADMIT receipt
    #     results/_r365bmc_w83_band_gate.py; not a re-pick -- R250:
    #     W83 bands were never assigned --
    _set_wave(83)
    try:
        assert WAVE_CONFIGS[83]["a_seed_base"] == pf.N1_BANDS[83]["a"][0], \\
            "W83 A band drift vs law mirror"
        assert WAVE_CONFIGS[83]["b_exit_seed_base"] == \\
            pf.N1_BANDS[83]["b_exit"][0], "W83 B band drift vs law mirror"
        assert WAVE_CONFIGS[83].get("engine_owner") == \\
            pf.N1_BANDS[83].get("engine_owner") == "bm-c", \\
            "W83 engine_owner drift (law mirror parity)"
        w83_a = {A_SEED_BASE + j for j in range(A_N)}
        w83_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w83_a & w83_b), "W83 A/B band overlap"
        assert not (w83_a & reg_ints) and not (w83_b & reg_ints), \\
            "W83 hits SEED_REGISTRY"
        for nm, band in (("A", w83_a), ("B", w83_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W83 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W83 {nm} hits W1"
            assert not (band & probes), f"W83 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W73..W82 are
        # REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly (W80 bm-c r364; W81 bm-a r574;
        # W82 bm-b r574, whose in-file blocks were byte-healed by
        # r365 bm-c after the r519-family 9th-occurrence phantom-D
        # reversion; holding commit 45e05a67c).
        assert pf.N1_BANDS[73] == {"a": (189_004, 191_003),
                                   "b_exit": (51_601, 51_800),
                                   "engine_owner": "bm-a"}, \\
            "registered W73 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[74] == {"a": (191_004, 193_003),
                                   "b_exit": (52_001, 52_200),
                                   "engine_owner": "bm-b"}, \\
            "registered W74 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[75] == {"a": (193_004, 195_003),
                                   "b_exit": (52_201, 52_400),
                                   "engine_owner": "bm-a"}, \\
            "registered W75 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[76] == {"a": (195_004, 197_003),
                                   "b_exit": (52_401, 52_600),
                                   "engine_owner": "bm-b"}, \\
            "registered W76 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[77] == {"a": (197_004, 199_003),
                                   "b_exit": (52_601, 52_800),
                                   "engine_owner": "bm-a"}, \\
            "registered W77 row parity drift (r307 two-state; bm-a r572)"
        assert pf.N1_BANDS[78] == {"a": (199_004, 201_003),
                                   "b_exit": (53_201, 53_400),
                                   "engine_owner": "bm-c"}, \\
            "registered W78 row parity drift (r307 two-state; bm-c r363)"
        assert pf.N1_BANDS[79] == {"a": (201_004, 203_003),
                                   "b_exit": (53_401, 53_600),
                                   "engine_owner": "bm-b"}, \\
            "registered W79 row parity drift (r307 two-state; bm-b r573)"
        assert pf.N1_BANDS[80] == {"a": (203_004, 205_003),
                                   "b_exit": (53_601, 53_800),
                                   "engine_owner": "bm-c"}, \\
            "registered W80 row parity drift (r307 two-state; bm-c r364)"
        assert pf.N1_BANDS[81] == {"a": (205_004, 207_003),
                                   "b_exit": (54_001, 54_200),
                                   "engine_owner": "bm-a"}, \\
            "registered W81 row parity drift (r307 two-state; bm-a r574)"
        assert pf.N1_BANDS[82] == {"a": (207_004, 209_003),
                                   "b_exit": (54_201, 54_400),
                                   "engine_owner": "bm-b"}, \\
            "registered W82 row parity drift (r307 two-state; bm-b r574)"
        # prior-wave disjointness incl. W48..W82 (all registered; the
        # W82 row is the direct arithmetic upstream of W83's bands).
        for wprev in REG_WAVES_ALL:
            assert not (w83_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W83 A hits W{wprev}"
            assert not (w83_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W83 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W83 clears it.
        n3r1_used83 = set(range(70_000, 70_006))
        assert not (w83_a & n3r1_used83) and not (w83_b & n3r1_used83), \\
            "W83 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w83_a & lfc_actual12) and not (w83_b & lfc_actual12), \\
            "W83 bands must clear the lfc actual draw range"
        assert not (w83_a & options_actual12) and \\
            not (w83_b & options_actual12), \\
            "W83 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W83 row, r365): BOTH SIDES ARITHMETIC
        # CONTINUATION from the registered W82 tail, zero skip -- the
        # arithmetic windows must be CLEAN (no registry points inside;
        # the skip-free face is forced by the ADMIT receipt, refusal
        # facts empty).
        assert WAVE_CONFIGS[83]["a_seed_base"] == 209_004 == \\
            pf.N1_BANDS[82]["a"][1] + 1, \\
            "W83 A must start at the registered W82 A end + 1 " \\
            "(arithmetic continuation window 209_004..211_003 CLEAN)"
        assert WAVE_CONFIGS[83]["b_exit_seed_base"] == 54_401 == \\
            pf.N1_BANDS[82]["b_exit"][1] + 1, \\
            "W83 B must start at the registered W82 B end + 1 " \\
            "(arithmetic continuation window 54_401..54_600 CLEAN)"
        arith_a83 = set(range(209_004, 211_004))
        arith_b83 = set(range(54_401, 54_601))
        assert not (arith_a83 & reg_ints) and not (arith_b83 & reg_ints), \\
            "W83 arithmetic windows must be CLEAN (zero-skip ADMIT face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W83-SHARD-0",
                                          "n1w83-0of12"), "W83 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W83-SHARD-11",
                                          "n1w83-11of12")
        assert SHARD_DIR.endswith("n1_w83") and OUT.endswith(
            "n1_w83_results.json"), "W83 path drift"
        for wprev in REG_WAVES_ALL:
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W83 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W83_PREREG.md")), \\
            "W83 per-wave prereg missing (materializer requirement)"
        # W83 finalize cumulative deps: W17..W81 outputs ALL PRESENT
        # (landed chain head 542,748, K=176,120, W81 bm-a r574 this
        # window; W82 bm-b = ONE in-flight upstream seat -- the
        # finalize merge loop derives the wave set from registry keys
        # at run time and stays FAIL-CLOSED on the not-yet-finalized
        # seat, r307 two-state law).
        for _depw in range(17, 82):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W83 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law):
        # prior-wave set derives from registry keys below 83 (no 15,
        # incl. 48..82 -- all registered, W82 in-flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 83) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 83)], \\
            "W83 prior-wave set must derive from registry keys (no 15; " \\
            "incl. 48..82 -- W82 registered, in-flight, FAIL-CLOSED)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W83 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    REG_WAVES_ALL = '[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 83)]'
    LEG83 = LEG83.replace('REG_WAVES_ALL', REG_WAVES_ALL)
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG83.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W83 leg landed (insert before T-141 lane face)')

# --- edit 5: n1.py selftest SUMMARY segment (the 5th face) --------------------
t2c, eol2c = load(FP2)
if '+ W83 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('\n          "+ T-141 s2 ')
    SEG83 = ('\n          "+ W83 materializer face [same guard set, dep=W17..W81 "\n'
             '          "outputs ALL PRESENT (landed chain head 542,748, "\n'
             '          "K=176,120, W81 bm-a r574 this window), W82 bm-b = ONE "\n'
             '          "in-flight upstream seat (FAIL-CLOSED r307 at run "\n'
             '          "time), SEVENTY-THIRD ENGINE-OWNED WAVE BY "\n'
             '          "MACHINE-DERIVE (engine_owner rows 72 + candidate; "\n'
             '          "prose ordinal -1 drift disclosed, r359 law) bm-c\'s "\n'
             '          "twenty-sixth owned claim per machine-derive "\n'
             '          "(engine_owner==bm-c rows 25 + candidate), "\n'
             '          "engine_owner=bm-c per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series "\n'
             '          "(wave 83 = first FREE number after the registered "\n'
             '          "W82 row; seat published=reserved "\n'
             '          "MSG-20261002-1231-bmc pushed to origin BEFORE "\n'
             '          "this freeze, commit 165f18f2c, r565 law), BOTH "\n'
             '          "SIDES ARITHMETIC CONTINUATION zero skip (A "\n'
             '          "209_004..211_003 CLEAN + B 54_401..54_600 CLEAN, "\n'
             '          "single reading, no fork face; W84+ projection "\n'
             '          "A 211_004..213_003 CLEAN / B 54_601..54_800 CLEAN "\n'
             '          "disclosed for the next freezer; ADMIT receipt "\n'
             '          "results/_r365bmc_w83_band_gate.py; not a "\n'
             '          "free pick -- R250), N3-R1 used-seed leg, "\n'
             '          "probe-seed cluster leg, law sec.4 W83 row, "\n'
             '          "r365 bm-c] "')
    A5X = A5.replace('\n', eol2c)
    assert t2c.count(A5X) == 1, f'summary anchor not unique: {t2c.count(A5X)}'
    t2c = t2c.replace(A5X, SEG83.replace('\n', eol2c) + A5X)
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W83 segment landed (insert before T-141 s2 segment)')

# --- edit 4: PERPETUAL_FACES.md canon W83 row ---------------------------------
ROW83 = """
- N1 波83（r365 bm-c 冻·prereg 时展行）：**第七十三枚引擎波〔机面 derive：engine_owner 行 72+本候选——live prose 注释序自 W80 起带 −1 漂移（机面：W80=第 70 枚/W81=第 71 枚/W82=第 72 枚·bm-b r574 的 SEVENTY-SECOND 实为正确·bm-a r574 勘正自身为错侧）·r359 律以机面为准如实披露〕·bm-c 第二十六枚自有波〔机面 derive：engine_owner==bm-c 行 25+本候选〕**·engine_owner=bm-c·SATURATION_ENGINE_LAW §1/§2 同 W10-W82 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-c 实例=常驻架构 v0.4 per-tick 重读（D-20261002-03 修法·W59/W60/W61/W66/W69/W71/W78/W80 同窗实证——冻结编辑落工作树后下一 tick 重读活树自见新行自燃=免杀重启免做·点火验证唯一证据=2 tick 内产物增长面 r325 律·state queue 面不信）】·【never-dry 供给律常设步·**波号 83=注册表 W82 行后首个自由号**（r511 表尾锁例冻结前 fetch 实核表尾时 W83 号位净空〔pf 行+prereg 路径双查〕·origin 侧 vacancy 机验）·**席位公示=MSG-20261002-1231-bmc（published=reserved r518-① 律·先于冻结 commit 推 origin=r565 早可见性律·commit 165f18f2c）**·本窗实况=W81 finalize 已落账（bm-a r574·**542,748 净链头**·K=176,120）→W82 bm-b finalize 链序解锁（本波 W83 finalize 前置=W82 落账·FAIL-CLOSED r307）〕·**W82 愈合注记（r519 族第 9 犯·bm-c r365 同窗治愈）**：bm-a r574 commit e3215a98e（add -A 整树面 phantom-D）把 bm-b 45e05a67c 已推 origin 的 W82 冻结包**共享文件内容四块**（n1 WAVE_CONFIGS[82]+selftest materializer leg+summary 段+canon W82 行）整面回退蒸发——bm-a hotfix 5ff066442 只恢复 17 个独立件漏共享文件内插入段；r365 按 r540 律从持有 commit 45e05a67c 字节恢复四块（attribution=bm-b·restorer=bm-c r365·零科学损失：W82 finalize 从未在坏树上跑过）·**带位（r535 机闸 derive 律·活注册表机证·ADMIT 回执=results/_r365bmc_w83_band_gate.py）**：**A-ext seed=209_004..211_003**（**A 面算术续带零跳位**==W82 A 尾 209_003+1·步长逐字·CLEAN）；**B-ext exit seed=54_401..54_600**（**B 面算术续带零跳位**==W82 B 尾 54_400+1·步长逐字·CLEAN·双侧算术窗零拒绝点=单读法零分叉〔F-20261002-03 跳位语义分叉面不触发·D-20261002-05 集团钉死=越 hit 起窗——本波零跳位不触发〕）·【机证净空——leg0 八十行注册表形（80 注册行·表尾=W82 bm-b r574）+leg1-A/B 双侧算术位 CLEAN 零拒绝点+leg2 A/B 首净窗==算术位恒等+leg3 origin 号位净空机验（pf 行+prereg 路径双查）+SEED_REGISTRY 全键 160 值+N3-R1 已用种子带腿（70_000..70_005·MSG-183x r529 强制）+探针种子簇腿（95_000..95_003·r335 强制）+N2/N4+N2-W15 探针点+lfc/options 实际流腿】·**W84+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 211_004..213_003 **CLEAN**；B 54_601..54_800 **CLEAN**·R250：W83 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W83 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W83_PREREG.md（冻结件）·本波 §5 锚=W81 finalize 实测值（锚滚动律）·finalize 链序前置=W82 bm-b 唯一在飞上游席（FAIL-CLOSED r307 两态律）。
"""
FP4 = FP_CANON
t4, eol4 = load(FP4)
if '- N1 \u6ce283\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW83.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W83 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 83))
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    83: {"a": (209_004') == 1, 'FIX-B FAIL: W83 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W83"') == 1, 'FIX-B FAIL: W83 config not exactly once'
for w in range(58, 84):
    leg = f'W{w} materializer face'
    exp = 2
    assert n11.count(leg) == exp, f'FIX-B FAIL: {leg} count={n11.count(leg)} (expect 2: leg+summary)'
assert n11.count('W82 materializer face') == 2, \
    'FIX-B FAIL: healed W82 leg+summary must be exactly 2'
assert n11.count('W83 materializer face') == 2, \
    'FIX-B FAIL: W83 leg+summary must be exactly 2'
for w in range(48, 84):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost or duplicated'
print('FIX-B: all registered row signatures survive; W82 healed + W83 added exactly once per face')

# ---------------- FIX-C: pure-insertion delta vs origin -----------------------
for p in TARGETS:
    out = git('diff', 'origin/main', '--numstat', '--', p).decode('utf-8').strip()
    if not out:
        sys.exit(f'FIX-C FAIL: no diff shown for {p} (edits missing?)')
    for line in out.splitlines():
        add, dele, path = line.split('\t')
        assert int(dele) == 0, f'FIX-C FAIL: {p} shows {dele} deleted lines ' \
                               f'(pure insertion violated -- r519 content-variant abort)'
        print(f'FIX-C: {p} +{add} -0 (pure insertion)')
print('FREEZE_EDITS_OK 83 (+W82 heal)')
