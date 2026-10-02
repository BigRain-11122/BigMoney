# -*- coding: utf-8 -*-
"""r577 bm-a W87 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening.

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W86, bm-a's own);
  every registered row signature survives exactly; exactly one new W87
  signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.

W87 = SEVENTY-SEVENTH engine wave by MACHINE-DERIVE (engine_owner rows 76 +
candidate), bm-a's TWENTY-THIRD owned (engine_owner==bm-a rows 22 +
candidate). First free number after the registered W86 row (single-state
gate: W85+W86 both registered, zero published-but-unregistered seats, zero
W87 seat MSGs on origin per gate leg0b). Seat published=reserved
MSG-20261002-1345-bma PUSHED before this freeze (r565 early-visibility law).
Bands: A 217_004..219_003 (arithmetic continuation from W86 A tail, CLEAN)
/ B 55_501..55_700 (arithmetic 55_401..55_600 REFUSED in-band at
SEED_REGISTRY grid_p1=55_500 median position 99/199 non-endpoint ->
D-20261002-05 pin: past-hit restart hit+1; window-step-chain reading
55_601..55_800 BANNED; W68-B positive anchor; ADMIT receipt
results/_r577bma_w87_band_gate.py rc0).
W1..W86 finalizes ALL LANDED at this freeze (net head 553,748 = W85 bm-b
r577 + W86 bm-a r577, K=187,120; ZERO in-flight upstream seats -- first
fully-caught-up freeze window since W53). W88+ projection: A
219_004..221_003 CLEAN / B 55_701..55_900 CLEAN (next freezer re-derives).
"""
import subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREAT = 0x08000000

def git(*a):
    r = subprocess.run(['git', '-C', REPO] + list(a), capture_output=True,
                       creationflags=CREAT)
    if r.returncode != 0:
        sys.exit('GIT FAIL %s -> %s' % (a[:3], r.stderr.decode('utf-8', 'replace')))
    return r.stdout

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

# ---------------- FIX-A: origin-blob freshness (pre-edit) --------------------
git('fetch', 'origin')
TARGETS = ['scripts/perpetual_faces.py', 'scripts/perpetual_faces_n1.py',
           'research/PERPETUAL_FACES.md']
for p in TARGETS:
    r = subprocess.run(['git', '-C', REPO, 'diff', 'origin/main', '--numstat', '--', p],
                       capture_output=True, creationflags=CREAT)
    for line in r.stdout.decode('utf-8', 'replace').strip().splitlines():
        add, dele, path = line.split('\t')
        if int(dele) > 0:
            sys.exit(f'STALE BASE (FIX-A abort): {p} shows {dele} deleted lines vs '
                     f'origin/main (another machine landed edits -- re-derive first)')
print('FIX-A: all 3 tracked edit targets fresh vs origin/main (zero deletions)')

# ---------------- survival baseline (FIX-B) -----------------------------------
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 87))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 87)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 87)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[87] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '87: {"a": (217_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    86: {"a": (215_004, 217_003), "b_exit": (55_201, 55_400),\n'
          '         "engine_owner": "bm-a"},\n'
          '}\n')
    NEW = ('    86: {"a": (215_004, 217_003), "b_exit": (55_201, 55_400),\n'
           '         "engine_owner": "bm-a"},\n'
           '    # SEVENTY-SEVENTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r577 bm-a\n'
           '    # freeze): engine_owner rows 76 + candidate; bm-a\'s\n'
           '    # twenty-third owned per machine-derive (engine_owner==bm-a\n'
           '    # rows 22 + candidate). Wave 87 = first free number after the\n'
           '    # registered W86 row (single-state gate: W85+W86 both\n'
           '    # registered, zero published-but-unregistered seats, zero W87\n'
           '    # seat MSGs on origin per gate leg0b; r511 tail-lock\n'
           '    # fetch-checked vacancy; seat published=reserved\n'
           '    # MSG-20261002-1345-bma PUSHED to origin before this freeze\n'
           '    # per r565 early-visibility law).\n'
           '    # W1..W86 finalizes ALL LANDED at this freeze (net head\n'
           '    # 553,748 = W85 bm-b r577 551,548 + W86 bm-a r577 one-pass;\n'
           '    # K=187,120 merged pool; ZERO in-flight upstream seats --\n'
           '    # first fully-caught-up freeze window since W53; finalize\n'
           '    # merge loop stays FAIL-CLOSED r307 at run time).\n'
           '    # A-SIDE ARITHMETIC CONTINUATION from the registered W86 row\n'
           '    # tail, zero skip: A 217_004..217_003+2_000 = 217_004..219_003\n'
           '    # (= W86 A end 217_003 + 1) CLEAN. B-SIDE MEDIAN-HIT PIN CHAIN:\n'
           '    # arithmetic 55_401..55_600 REFUSED in-band at SEED_REGISTRY\n'
           '    # grid_p1=55_500 (median position 99/199, non-endpoint) ->\n'
           '    # D-20261002-05 pin: PAST-HIT start-window hit+1 restart\n'
           '    # 55_501..55_700 CLEAN (window-step-chain reading 55_601..55_800\n'
           '    # BANNED by the pin; W68-B positive anchor, pf.py selftest\n'
           '    # leg-9 pin leg).\n'
           '    # Machine-verified at prereg time\n'
           '    # (results/_r577bma_w87_band_gate.py ADMIT receipt vs the\n'
           '    # 84-row pre-W87 table + live SEED_REGISTRY values + probe\n'
           '    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin slot\n'
           '    # vacancy machine-checked). W88+ projection: A 219_004..221_003\n'
           '    # CLEAN; B 55_701..55_900 CLEAN (next freezer must re-derive,\n'
           '    # never transcribe).\n'
           '    # NOT a re-pick (R250: W87 bands were never assigned).\n'
           '    87: {"a": (217_004, 219_003), "b_exit": (55_501, 55_700),\n'
           '         "engine_owner": "bm-a"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[87] landed (anchor=W86 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[87] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '87: {"batch": "PERPETUAL-N1-W87"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w86", "out_name": "n1_w86_results.json",\n'
          '                            "engine_owner": "bm-a"},\n')
    NEW2 = A2 + (
        '                       87: {"batch": "PERPETUAL-N1-W87",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W87_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; SEVENTY-SEVENTH ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 76 + candidate; prose "\n'
        '                                       "ordinal -1 drift disclosed since W80, r359 law), "\n'
        '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
        '                                       "(first-free-number law over the registered W86 row; "\n'
        '                                       "seat published=reserved MSG-20261002-1345-bma PUSHED "\n'
        '                                       "to origin BEFORE this freeze per r565 early-visibility "\n'
        '                                       "law), engine_owner=bm-a, wave 87: A-SIDE ARITHMETIC "\n'
        '                                       "CONTINUATION zero skip (A 217_004..219_003 CLEAN) + "\n'
        '                                       "B-SIDE MEDIAN-HIT PIN CHAIN (arithmetic 55_401..55_600 "\n'
        '                                       "REFUSED in-band at SEED_REGISTRY grid_p1=55_500 median "\n'
        '                                       "position 99/199 non-endpoint -> D-20261002-05 pin: "\n'
        '                                       "past-hit restart 55_501..55_700 CLEAN; window-step-chain "\n'
        '                                       "reading 55_601..55_800 BANNED; W68-B positive anchor; "\n'
        '                                       "ADMIT receipt results/_r577bma_w87_band_gate.py; W88+ "\n'
        '                                       "projection: A 219_004..221_003 CLEAN / B 55_701..55_900 "\n'
        '                                       "CLEAN, disclosed for the next freezer); W1..W86 "\n'
        '                                       "finalizes ALL LANDED at this freeze (net chain head "\n'
        '                                       "553,748 = W85 bm-b r577 + W86 bm-a r577 one-pass, "\n'
        '                                       "K=187,120 merged pool; ZERO in-flight upstream seats "\n'
        '                                       "-- first fully-caught-up freeze window since W53; "\n'
        '                                       "finalize merge loop stays FAIL-CLOSED r307 at run "\n'
        '                                       "time)"),\n'
        '                            "a_seed_base": 217_004,        # law sec.4 W87 A: 217_004..219_003 (arithmetic continuation)\n'
        '                            "b_exit_seed_base": 55_501,   # law sec.4 W87 B: 55_501..55_700 (median-hit pin D-20261002-05)\n'
        '                            "shard_subdir": "n1_w87", "out_name": "n1_w87_results.json",\n'
        '                            "engine_owner": "bm-a"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[87] landed (anchor=W86 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W87 leg --------------
REG_WAVES_ALL = '[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 87)]'
LEG87 = '''
    # --- W87 materializer face (r577 bm-a freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-a's
    #     twenty-third owned per machine-derive (engine_owner==bm-a
    #     rows 22 + candidate); wave 87 = first free number after the
    #     registered W86 row (single-state gate: W85+W86 both
    #     registered, zero published seats, zero W87 seat MSGs on
    #     origin per gate leg0b). SEVENTY-SEVENTH engine wave BY
    #     MACHINE-DERIVE (engine_owner rows 76 + candidate; prose
    #     ordinal -1 drift disclosed since W80, r359 law). Seat
    #     published=reserved MSG-20261002-1345-bma pushed to origin
    #     BEFORE this freeze (r565 early-visibility law). W1..W86
    #     finalizes ALL LANDED at this freeze (net head 553,748 =
    #     W85 bm-b r577 + W86 bm-a r577 one-pass, K=187,120; ZERO
    #     in-flight upstream seats -- first fully-caught-up freeze
    #     window since W53; FAIL-CLOSED r307 at run time). ADMIT
    #     receipt results/_r577bma_w87_band_gate.py; not a re-pick --
    #     R250: W87 bands were never assigned --
    _set_wave(87)
    try:
        assert WAVE_CONFIGS[87]["a_seed_base"] == pf.N1_BANDS[87]["a"][0], \\
            "W87 A band drift vs law mirror"
        assert WAVE_CONFIGS[87]["b_exit_seed_base"] == \\
            pf.N1_BANDS[87]["b_exit"][0], "W87 B band drift vs law mirror"
        assert WAVE_CONFIGS[87].get("engine_owner") == \\
            pf.N1_BANDS[87].get("engine_owner") == "bm-a", \\
            "W87 engine_owner drift (law mirror parity)"
        w87_a = {A_SEED_BASE + j for j in range(A_N)}
        w87_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w87_a & w87_b), "W87 A/B band overlap"
        assert not (w87_a & reg_ints) and not (w87_b & reg_ints), \\
            "W87 hits SEED_REGISTRY"
        for nm, band in (("A", w87_a), ("B", w87_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W87 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W87 {nm} hits W1"
            assert not (band & probes), f"W87 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W73..W86 are
        # REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly (W85 bm-b r576; W86 bm-a r576).
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
        assert pf.N1_BANDS[83] == {"a": (209_004, 211_003),
                                   "b_exit": (54_401, 54_600),
                                   "engine_owner": "bm-c"}, \\
            "registered W83 row parity drift (r307 two-state; bm-c r365)"
        assert pf.N1_BANDS[84] == {"a": (211_004, 213_003),
                                   "b_exit": (54_601, 54_800),
                                   "engine_owner": "bm-a"}, \\
            "registered W84 row parity drift (r307 two-state; bm-a r575)"
        assert pf.N1_BANDS[85] == {"a": (213_004, 215_003),
                                   "b_exit": (55_001, 55_200),
                                   "engine_owner": "bm-b"}, \\
            "registered W85 row parity drift (r307 two-state; bm-b r576)"
        assert pf.N1_BANDS[86] == {"a": (215_004, 217_003),
                                   "b_exit": (55_201, 55_400),
                                   "engine_owner": "bm-a"}, \\
            "registered W86 row parity drift (r307 two-state; bm-a r576)"
        # prior-wave disjointness incl. W48..W86 (all registered; the
        # W86 row is the direct arithmetic upstream of W87's A band).
        for wprev in REG_WAVES_ALL:
            assert not (w87_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W87 A hits W{wprev}"
            assert not (w87_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W87 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W87 clears it.
        n3r1_used87 = set(range(70_000, 70_006))
        assert not (w87_a & n3r1_used87) and not (w87_b & n3r1_used87), \\
            "W87 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w87_a & lfc_actual12) and not (w87_b & lfc_actual12), \\
            "W87 bands must clear the lfc actual draw range"
        assert not (w87_a & options_actual12) and \\
            not (w87_b & options_actual12), \\
            "W87 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W87 row, r577): A-SIDE ARITHMETIC
        # CONTINUATION from the registered W86 tail, zero skip.
        assert WAVE_CONFIGS[87]["a_seed_base"] == 217_004 == \\
            pf.N1_BANDS[86]["a"][1] + 1, \\
            "W87 A must start at the registered W86 A end + 1 " \\
            "(arithmetic continuation window 217_004..219_003 CLEAN)"
        arith_a87 = set(range(217_004, 219_004))
        assert not (arith_a87 & reg_ints), \\
            "W87 A arithmetic window must be CLEAN (zero-skip ADMIT face)"
        # B-SIDE MEDIAN-HIT PIN CHAIN (D-20261002-05): arithmetic
        # 55_401..55_600 refused in-band at grid_p1=55_500 (median
        # position 99/199, non-endpoint) -> past-hit restart 55_501.
        # The window-step-chain reading 55_601 is BANNED by the pin.
        assert WAVE_CONFIGS[87]["b_exit_seed_base"] == 55_501 == 55_500 + 1, \\
            "W87 B must start at the 55_500 hit + 1 (D-20261002-05 pin: " \\
            "past-hit start-window; arithmetic window 55_401..55_600 " \\
            "REFUSED in-band at grid_p1=55_500 median, non-endpoint)"
        assert WAVE_CONFIGS[87]["b_exit_seed_base"] != 55_601, \\
            "W87 B window-step-chain reading 55_601..55_800 is BANNED " \\
            "by D-20261002-05 (past-hit start-window pinned; W68-B anchor)"
        assert 55_500 in reg_ints, "grid_p1=55_500 must be a live registry point"
        arith_b87 = set(range(55_401, 55_601))
        assert (arith_b87 & reg_ints) == {55_500}, \\
            "W87 B arithmetic window must hit exactly {55_500} (grid_p1)"
        assert not (w87_b & reg_ints), \\
            "W87 B restart window 55_501..55_700 must be CLEAN"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W87-SHARD-0",
                                          "n1w87-0of12"), "W87 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W87-SHARD-11",
                                          "n1w87-11of12")
        assert SHARD_DIR.endswith("n1_w87") and OUT.endswith(
            "n1_w87_results.json"), "W87 path drift"
        for wprev in REG_WAVES_ALL:
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W87 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W87_PREREG.md")), \\
            "W87 per-wave prereg missing (materializer requirement)"
        # W87 finalize cumulative deps: W17..W86 outputs ALL PRESENT
        # (landed chain head 553,748, K=187,120, W85 bm-b r577 + W86
        # bm-a r577 both landed; ZERO in-flight upstream seats at this
        # freeze -- first fully-caught-up window since W53; the
        # finalize merge loop derives the wave set from registry keys
        # at run time and stays FAIL-CLOSED, r307 two-state law).
        for _depw in range(17, 87):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W87 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law):
        # prior-wave set derives from registry keys below 87 (no 15,
        # incl. 48..86 -- all registered and landed).
        assert sorted(w for w in WAVE_CONFIGS if w < 87) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 87)], \\
            "W87 prior-wave set must derive from registry keys (no 15; " \\
            "incl. 48..86 -- all registered, all landed)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W87 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    LEG87X = LEG87.replace('REG_WAVES_ALL', REG_WAVES_ALL)
    t2b = t2b.replace(rep_probe, LEG87X.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W87 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment ----------------------
t2c, eol2c = load(FP2)
if '+ W87 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('          "r576 bm-a] "\n'
          '          "+ T-141 s2 ')
    SEG87 = ('          "r576 bm-a] "\n'
             '          "+ W87 materializer face [same guard set, dep=W17..W86 "\n'
             '          "outputs ALL PRESENT (landed chain head 553,748 = W85 "\n'
             '          "bm-b r577 + W86 bm-a r577 one-pass, K=187,120, ZERO "\n'
             '          "in-flight upstream seats -- first fully-caught-up freeze "\n'
             '          "window since W53, FAIL-CLOSED r307 at run time), "\n'
             '          "SEVENTY-SEVENTH ENGINE-OWNED WAVE BY MACHINE-DERIVE "\n'
             '          "(engine_owner rows 76 + candidate; prose ordinal -1 "\n'
             '          "drift disclosed since W80, r359 law) bm-a\'s twenty-third "\n'
             '          "owned claim per machine-derive (engine_owner==bm-a rows "\n'
             '          "22 + candidate), engine_owner=bm-a per engine de-throttle "\n'
             '          "law O-20261001-2355 sec.2 own-continuous-series (wave 87 "\n'
             '          "= first FREE number after the registered W86 row; seat "\n'
             '          "published=reserved MSG-20261002-1345-bma pushed to origin "\n'
             '          "BEFORE this freeze, r565 law), A-SIDE ARITHMETIC "\n'
             '          "CONTINUATION zero skip (A 217_004..219_003 CLEAN) + "\n'
             '          "B-SIDE MEDIAN-HIT PIN CHAIN (arithmetic 55_401..55_600 "\n'
             '          "REFUSED in-band at SEED_REGISTRY grid_p1=55_500 median "\n'
             '          "position 99/199 non-endpoint -> D-20261002-05 pin: "\n'
             '          "past-hit restart 55_501..55_700 CLEAN; window-step-chain "\n'
             '          "reading 55_601..55_800 BANNED, W68-B positive anchor; "\n'
             '          "W88+ projection A 219_004..221_003 CLEAN / B "\n'
             '          "55_701..55_900 CLEAN disclosed for the next freezer; "\n'
             '          "ADMIT receipt results/_r577bma_w87_band_gate.py; not "\n'
             '          "a free pick -- R250), N3-R1 used-seed leg, "\n'
             '          "probe-seed cluster leg, law sec.4 W87 row, "\n'
             '          "r577 bm-a] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG87, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W87 segment landed (insert after W86 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W87 row -------------------
ROW87 = """
- N1 波87（r577 bm-a 冻·prereg 时展行）：**第七十七枚引擎波·bm-a 第二十三枚自有波〔机面 derive：engine_owner 行 76+本候选／engine_owner==bm-a 行 22+本候选〕**·engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 同 W10-W86 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-a 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启免做·W44/W45/W48/W54/W57/W62/W64/W68/W73/W75/W77/W81/W84/W86 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 87=注册表 W86 行后首个自由号**（r511 表尾锁例冻结前 fetch 实核表尾时 W87 号位净空·pf 行+prereg 路径双查+**leg0b 全 inbox+processed/ 扫描零 W87 席位 MSG 机验**；**W86=表尾行 bm-a r576 冻·r577 本窗烧毕 12/12+finalize 已落账**；**席位公示=MSG-20261002-1345-bma**〔published=reserved r518-① 律·先于冻结 commit 推 origin=r565 早可见性律〕）·本窗实况=**W1..W86 finalize 全落账（净链头 553,748=W85 bm-b r577〔551,548〕+W86 bm-a r577 one-pass〔553,748〕·K=187,120 合并池·零在飞上游席=本波 finalize 无 FAIL-CLOSED 前置·W53 以来首个全追平冻结窗·跑时 registry 键 derive 复核恒在）**·**带位（r535 机闸 derive 律·活注册表机证·单态门·ADMIT 回执=results/_r577bma_w87_band_gate.py rc0）**：**A-ext seed=217_004..219_003**（**A 面算术续带零跳位**==W86 行 A 尾 217_003+1·步长 2_000·CLEAN 零拒绝点）；**B-ext exit seed=55_501..55_700**（**B 侧中位命中钉死链**：算术位 55_401..55_600 于带内中位〔位置 99/199 非边缘端点〕撞 **SEED_REGISTRY grid_p1=55_500**→**D-20261002-05 集团钉死=越 hit 起窗** 55_501..55_700 CLEAN〔窗步链读法 55_601..55_800=钉死行所禁读法·W68-B 正锚·pf selftest 第 9 腿 pin leg 正反断言·两读法分叉面由钉死行唯一裁定〕）·【机证净空——leg0 八十四行注册表形（84 注册行·表尾=W86 bm-a r576）+leg0b 零 W87 席位 MSG 机验+leg1 双侧算术位/钉死链 CLEAN+leg2 A/B 首净窗==候选恒等+leg3 origin 号位净空机验（pf 行+WAVE_CONFIGS+prereg 路径三查）+SEED_REGISTRY 全键 160 值+N3-R1 已用种子带腿（70_000..70_005·MSG-183x r529 强制）+探针种子簇腿（95_000..95_003·r335 强制）+N2/N4+N2-W15 探针点+lfc/options 实际流腿】·**W88+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 219_004..221_003 **CLEAN**；B 55_701..55_900 **CLEAN**（双侧算术预期零拒绝点）。R250：W87 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W87 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W87_PREREG.md（冻结件）·本波 §5 锚=W86 finalize 实测值（锚滚动律·单波跨锚自 W76 滚动至 W86）·finalize 链序前置=起草窗零在飞上游席（FAIL-CLOSED r307 两态律跑时复核）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce287\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW87.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W87 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    87: {"a": (217_004') == 1, 'FIX-B FAIL: W87 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W87"') == 1, 'FIX-B FAIL: W87 config not exactly once'
for w in range(58, 87):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W87 materializer face') == 2, \
    'FIX-B FAIL: W87 leg+summary must be exactly 2'
for w in range(48, 87):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce287\uff08') == 1, 'FIX-B FAIL: canon W87 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W87 added per face')

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
print('FREEZE_EDITS_OK 87')
