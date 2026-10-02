# -*- coding: utf-8 -*-
"""r580 bm-a W94 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening.

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W92, bm-c r370);
  every registered row signature survives exactly; exactly one new W94
  signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.

W94 = EIGHTY-FOURTH engine wave by MACHINE-DERIVE (engine_owner rows 82 +
in-flight W93 seat + candidate), bm-a's TWENTY-FIFTH owned (engine_owner==
bm-a rows 24 + candidate). First free number after the registered W92 row,
SKIPPING the bm-b published W93 seat (MSG-20261002-1510-bmb; published=
reserved r518-1). Prior seat yield: W93 zero-cost yield to bm-b per r511
commit-order (bands bitwise identical = deterministic cross-validation);
yield receipt + W94 seat = MSG-20261002-1514-bma PUSHED before this freeze
(r565 early-visibility law, origin 5d2daedc0).
Bands (DUAL-STATE CONVERGENT gate, W90 r579 precedent):
  A 231_004..233_003 (state A skip-past-published chain from the W92 tail
     over the W93 published band; state B arithmetic continuation from the
     W93 registered tails -- both states converge) CLEAN.
  B 57_301..57_500 (same convergence face) CLEAN.
  ADMIT receipt results/_r580bma_w94_band_gate.py rc0 state A.
W1..W91 finalizes ALL LANDED at this freeze (landed chain head 564,748 =
W91 bm-b r579 one-pass; K=198,120 merged pool). TWO in-flight upstream seats
(W92 bm-c burning + W93 bm-b freeze in flight) -- finalize merge loop stays
FAIL-CLOSED r307 at run time. W95+ projection: A 233_004..235_003 CLEAN /
B 57_501..57_700 CLEAN (next freezer re-derives).
"""
import subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def git(*a):
    r = subprocess.run(['git', '-C', REPO] + list(a), capture_output=True)
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
                       capture_output=True)
    for line in r.stdout.decode('utf-8', 'replace').strip().splitlines():
        add, dele, path = line.split('\t')
        if int(dele) > 0:
            sys.exit(f'STALE BASE (FIX-A abort): {p} shows {dele} deleted lines vs '
                     f'origin/main (another machine landed edits -- re-derive first)')
print('FIX-A: all 3 tracked edit targets fresh vs origin/main (zero deletions)')

# ---------------- survival baseline (FIX-B) -----------------------------------
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 93))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 93)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 93)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[94] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '94: {"a": (231_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    92: {"a": (227_004, 229_003), "b_exit": (56_701, 56_900),\n'
          '         "engine_owner": "bm-c"},\n'
          '}\n')
    NEW = ('    92: {"a": (227_004, 229_003), "b_exit": (56_701, 56_900),\n'
           '         "engine_owner": "bm-c"},\n'
           '    # EIGHTY-FOURTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r580 bm-a\n'
           '    # freeze): engine_owner rows 82 + in-flight W93 seat (bm-b) +\n'
           '    # candidate; bm-a\'s twenty-fifth owned per machine-derive\n'
           '    # (engine_owner==bm-a rows 24 + candidate). Wave 94 = first\n'
           '    # free number after the registered W92 row SKIPPING the bm-b\n'
           '    # published W93 seat (MSG-20261002-1510-bmb; published=\n'
           '    # reserved r518-1; prior seat yield: W93 zero-cost yield to\n'
           '    # bm-b per r511 commit-order, bands bitwise identical =\n'
           '    # deterministic cross-validation; yield receipt + W94 seat\n'
           '    # = MSG-20261002-1514-bma PUSHED to origin before this freeze\n'
           '    # per r565 early-visibility law).\n'
           '    # W1..W91 finalizes ALL LANDED at this freeze (landed chain\n'
           '    # head 564,748 = W91 bm-b r579 one-pass; K=198,120 merged\n'
           '    # pool). TWO in-flight upstream seats (W92 bm-c burning +\n'
           '    # W93 bm-b freeze in flight) -- finalize merge loop stays\n'
           '    # FAIL-CLOSED r307 at run time).\n'
           '    # BOTH SIDES SKIP-PAST-PUBLISHED CHAIN, DUAL-STATE CONVERGENT\n'
           '    # (W90 r579 precedent): state A = W93 seat-published-\n'
           '    # unregistered (skip-past-published from the W92 tails over\n'
           '    # the W93 published bands); state B = W93 registered\n'
           '    # (arithmetic continuation from the W93 tails) -- both\n'
           '    # states derive the same bands bitwise.\n'
           '    # A-SIDE: first clean window 231_004..233_003 (W92 A end\n'
           '    # 229_003 + 1 -> W93 published band 229_004..231_003 refused\n'
           '    # -> 231_004..233_003) CLEAN zero refusal points.\n'
           '    # B-SIDE: first clean window 57_301..57_500 (W92 B end\n'
           '    # 56_900 + 1 -> W93 published band 57_101..57_300 refused\n'
           '    # -> 57_301..57_500) CLEAN zero refusal points.\n'
           '    # Machine-verified at prereg time\n'
           '    # (results/_r580bma_w94_band_gate.py ADMIT receipt rc0 state A\n'
           '    # vs the 90-row pre-W94 table + W93 published seat + live\n'
           '    # SEED_REGISTRY values + probe cluster 95_000..95_003 r335\n'
           '    # discovery leg + N3-R1 used-seed band 70_000..70_005\n'
           '    # MSG-183x r529 mandatory leg; origin slot vacancy machine-\n'
           '    # checked). W95+ projection: A 233_004..235_003 CLEAN; B\n'
           '    # 57_501..57_700 CLEAN (next freezer must re-derive, never\n'
           '    # transcribe).\n'
           '    # NOT a re-pick (R250: W94 bands were never assigned).\n'
           '    94: {"a": (231_004, 233_003), "b_exit": (57_301, 57_500),\n'
           '         "engine_owner": "bm-a"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[94] landed (anchor=W92 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[94] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '94: {"batch": "PERPETUAL-N1-W94"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w92", "out_name": "n1_w92_results.json",\n'
          '                            "engine_owner": "bm-c"},\n')
    NEW2 = A2 + (
        '                       94: {"batch": "PERPETUAL-N1-W94",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W94_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; EIGHTY-FOURTH ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 82 + in-flight W93 "\n'
        '                                       "seat + candidate; prose ordinal -1 drift disclosed since "\n'
        '                                       "W80, r359 law), own-series continuation per O-20261001-2355 "\n'
        '                                       "sec.2 (first-free-number law over the registered W92 row "\n'
        '                                       "SKIPPING the bm-b published W93 seat; W93 zero-cost yield "\n'
        '                                       "per r511 commit-order, bands bitwise identical; yield "\n'
        '                                       "receipt + seat published=reserved MSG-20261002-1514-bma "\n'
        '                                       "PUSHED to origin BEFORE this freeze per r565 early-"\n'
        '                                       "visibility law), engine_owner=bm-a, wave 94: BOTH SIDES "\n'
        '                                       "SKIP-PAST-PUBLISHED CHAIN DUAL-STATE CONVERGENT (W90 "\n'
        '                                       "r579 precedent: state A skip-past-published over the W93 "\n'
        '                                       "seat bands / state B arithmetic continuation from the "\n'
        '                                       "W93 registered tails -- same bands bitwise; A "\n'
        '                                       "231_004..233_003 CLEAN + B 57_301..57_500 CLEAN zero "\n'
        '                                       "refusal points; ADMIT receipt results/_r580bma_w94_band_"\n'
        '                                       "gate.py; W95+ projection: A 233_004..235_003 CLEAN / B "\n'
        '                                       "57_501..57_700 CLEAN, disclosed for the next freezer); "\n'
        '                                       "W1..W91 finalizes ALL LANDED at this freeze (landed chain "\n'
        '                                       "head 564,748 = W91 bm-b r579 one-pass, K=198,120 merged "\n'
        '                                       "pool; TWO in-flight upstream seats W92 bm-c burning + "\n'
        '                                       "W93 bm-b freeze in flight -- finalize merge loop stays "\n'
        '                                       "FAIL-CLOSED r307 at run time)"),\n'
        '                            "a_seed_base": 231_004,        # law sec.4 W94 A: 231_004..233_003 (skip-past-published chain)\n'
        '                            "b_exit_seed_base": 57_301,   # law sec.4 W94 B: 57_301..57_500 (skip-past-published chain)\n'
        '                            "shard_subdir": "n1_w94", "out_name": "n1_w94_results.json",\n'
        '                            "engine_owner": "bm-a"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[94] landed (anchor=W92 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W94 leg --------------
REG_WAVES_ALL = '[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 94) if w in WAVE_CONFIGS]'
LEG94 = '''
    # --- W94 materializer face (r580 bm-a freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-a's
    #     twenty-fifth owned per machine-derive (engine_owner==bm-a
    #     rows 24 + candidate); wave 94 = first free number after the
    #     registered W92 row SKIPPING the bm-b published W93 seat
    #     (MSG-20261002-1510-bmb; published=reserved r518-1). W93
    #     zero-cost yield to bm-b per r511 commit-order (bands bitwise
    #     identical = deterministic cross-validation; yield receipt +
    #     W94 seat = MSG-20261002-1514-bma pushed to origin BEFORE this
    #     freeze, r565 law). EIGHTY-FOURTH engine wave BY MACHINE-DERIVE
    #     (engine_owner rows 82 + in-flight W93 seat + candidate; prose
    #     ordinal -1 drift disclosed since W80, r359 law). W1..W91
    #     finalizes ALL LANDED at this freeze (landed chain head
    #     564,748 = W91 bm-b r579 one-pass, K=198,120; TWO in-flight
    #     upstream seats W92 bm-c burning + W93 bm-b freeze in flight
    #     -- FAIL-CLOSED r307 at run time). ADMIT receipt
    #     results/_r580bma_w94_band_gate.py; not a re-pick --
    #     R250: W94 bands were never assigned --
    _set_wave(94)
    try:
        assert WAVE_CONFIGS[94]["a_seed_base"] == pf.N1_BANDS[94]["a"][0], \\
            "W94 A band drift vs law mirror"
        assert WAVE_CONFIGS[94]["b_exit_seed_base"] == \\
            pf.N1_BANDS[94]["b_exit"][0], "W94 B band drift vs law mirror"
        assert WAVE_CONFIGS[94].get("engine_owner") == \\
            pf.N1_BANDS[94].get("engine_owner") == "bm-a", \\
            "W94 engine_owner drift (law mirror parity)"
        w94_a = {A_SEED_BASE + j for j in range(A_N)}
        w94_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w94_a & w94_b), "W94 A/B band overlap"
        assert not (w94_a & reg_ints) and not (w94_b & reg_ints), \\
            "W94 hits SEED_REGISTRY"
        for nm, band in (("A", w94_a), ("B", w94_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W94 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W94 {nm} hits W1"
            assert not (band & probes), f"W94 {nm} hits probe seeds"
        # W93 published-seat disjointness (r518-1; dual-state: holds
        # whether W93 is registered or seat-published only).
        w93_pub_a = set(range(229_004, 231_004))
        w93_pub_b = set(range(57_101, 57_301))
        assert not (w94_a & w93_pub_a) and not (w94_b & w93_pub_b), \\
            "W94 bands hit the bm-b W93 published seat bands (r518-1)"
        # registered declared-band parity (r307 two-state): recent
        # registered rows are pinned constants (W89 bm-b r578 estate;
        # W90 bm-a r579; W91 bm-b r578; W92 bm-c r370).
        assert pf.N1_BANDS[88] == {"a": (219_004, 221_003),
                                   "b_exit": (55_701, 55_900),
                                   "engine_owner": "bm-c"}, \\
            "registered W88 row parity drift (r307 two-state; bm-c r368)"
        assert pf.N1_BANDS[89] == {"a": (221_004, 223_003),
                                   "b_exit": (56_001, 56_200),
                                   "engine_owner": "bm-b"}, \\
            "registered W89 row parity drift (r307 two-state; bm-b r578)"
        assert pf.N1_BANDS[90] == {"a": (223_004, 225_003),
                                   "b_exit": (56_201, 56_400),
                                   "engine_owner": "bm-a"}, \\
            "registered W90 row parity drift (r307 two-state; bm-a r579)"
        assert pf.N1_BANDS[91] == {"a": (225_004, 227_003),
                                   "b_exit": (56_501, 56_700),
                                   "engine_owner": "bm-b"}, \\
            "registered W91 row parity drift (r307 two-state; bm-b r578)"
        assert pf.N1_BANDS[92] == {"a": (227_004, 229_003),
                                   "b_exit": (56_701, 56_900),
                                   "engine_owner": "bm-c"}, \\
            "registered W92 row parity drift (r307 two-state; bm-c r370)"
        # prior-wave disjointness incl. W48..W92 (all registered at this
        # freeze; the W92 row is the registered upstream of W94's
        # skip-past-published chain; W93 in-flight seats excluded here
        # and covered by the published-seat disjointness leg above).
        for wprev in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
                [w for w in range(16, 93)]:
            assert not (w94_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W94 A hits W{wprev}"
            assert not (w94_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W94 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W94 clears it.
        n3r1_used94 = set(range(70_000, 70_006))
        assert not (w94_a & n3r1_used94) and not (w94_b & n3r1_used94), \\
            "W94 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w94_a & lfc_actual12) and not (w94_b & lfc_actual12), \\
            "W94 bands must clear the lfc actual draw range"
        assert not (w94_a & options_actual12) and \\
            not (w94_b & options_actual12), \\
            "W94 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W94 row, r580): BOTH SIDES
        # SKIP-PAST-PUBLISHED CHAIN, DUAL-STATE CONVERGENT (W90 r579
        # precedent). A starts at W93 published A end + 1; B starts at
        # W93 published B end + 1 -- identical to the state-B arithmetic
        # continuation from the W93 registered tails.
        assert WAVE_CONFIGS[94]["a_seed_base"] == 231_004 == 231_003 + 1, \\
            "W94 A must start at the W93 published band A end + 1 " \\
            "(skip-past-published chain window 231_004..233_003 CLEAN; " \\
            "dual-state convergent with the W93-registered continuation)"
        assert WAVE_CONFIGS[94]["b_exit_seed_base"] == 57_301 == 57_300 + 1, \\
            "W94 B must start at the W93 published band B end + 1 " \\
            "(skip-past-published chain window 57_301..57_500 CLEAN; " \\
            "dual-state convergent with the W93-registered continuation)"
        arith_a94 = set(range(231_004, 233_004))
        assert not (arith_a94 & reg_ints), \\
            "W94 A window must be CLEAN (zero-skip ADMIT face)"
        arith_b94 = set(range(57_301, 57_501))
        assert not (arith_b94 & reg_ints), \\
            "W94 B window must be CLEAN (zero-skip ADMIT face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W94-SHARD-0",
                                          "n1w94-0of12"), "W94 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W94-SHARD-11",
                                          "n1w94-11of12")
        assert SHARD_DIR.endswith("n1_w94") and OUT.endswith(
            "n1_w94_results.json"), "W94 path drift"
        for wprev in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
                [w for w in range(16, 93)]:
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W94 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W94_PREREG.md")), \\
            "W94 per-wave prereg missing (materializer requirement)"
        # W94 finalize cumulative deps: W17..W91 outputs ALL PRESENT
        # (landed chain head 564,748 = W91 bm-b r579 one-pass,
        # K=198,120). W92 (bm-c burning) + W93 (bm-b freeze in
        # flight) are in-flight upstream seats -- NOT asserted here
        # (honest two-state face); the finalize merge loop derives the
        # wave set from registry keys at run time and stays
        # FAIL-CLOSED, r307 two-state law.
        for _depw in range(17, 92):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W94 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law):
        # prior-wave set derives from registry keys below 94 (no 15;
        # W92 registered at this freeze; W93 in-flight joins at run
        # time -- FAIL-CLOSED composes it).
        assert sorted(w for w in WAVE_CONFIGS if w < 94) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 93)], \\
            "W94 prior-wave set must derive from registry keys (no 15; " \\
            "W2..W92 registered at this freeze; in-flight W93 joins " \\
            "at run time FAIL-CLOSED)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W94 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    A3 = ('_set_wave(2)\n'
          '\n'
          '\n'
          '\n'
          '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim')
    A3X = A3.replace('\n', eol2b)
    assert t2b.count(A3X) == 1, f'selftest anchor not unique: {t2b.count(A3X)}'
    LEG94X = LEG94.replace('REG_WAVES_ALL', REG_WAVES_ALL)
    t2b = t2b.replace(A3X, '_set_wave(2)' + eol2b * 3 + LEG94X.replace('\n', eol2b) + A3X)
    save(FP2, t2b)
    print('edit3 selftest W94 leg landed (insert before T-141 selftest lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment ----------------------
t2c, eol2c = load(FP2)
if '+ W94 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('          "cluster leg, law sec.4 W90 row, r579 bm-a] "\n'
          '          "+ T-141 s2 ')
    SEG94 = ('          "cluster leg, law sec.4 W90 row, r579 bm-a] "\n'
             '          "+ W94 materializer face [same guard set, dep=W17..W91 "\n'
             '          "outputs ALL PRESENT (landed chain head 564,748 = W91 "\n'
             '          "bm-b r579 one-pass, K=198,120; TWO in-flight upstream "\n'
             '          "seats W92 bm-c burning + W93 bm-b freeze in flight -- "\n'
             '          "FAIL-CLOSED r307 at run time), EIGHTY-FOURTH ENGINE-"\n'
             '          "OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 82 + "\n'
             '          "in-flight W93 seat + candidate; prose ordinal -1 drift "\n'
             '          "disclosed since W80, r359 law) bm-a\'s twenty-fifth "\n'
             '          "owned claim per machine-derive (engine_owner==bm-a rows "\n'
             '          "24 + candidate), engine_owner=bm-a per engine de-throttle "\n'
             '          "law O-20261001-2355 sec.2 own-continuous-series (wave 94 "\n'
             '          "= first FREE number after the registered W92 row SKIPPING "\n'
             '          "the bm-b published W93 seat; W93 zero-cost yield per r511 "\n'
             '          "commit-order, bands bitwise identical; seat published="\n'
             '          "reserved MSG-20261002-1514-bma pushed to origin BEFORE "\n'
             '          "this freeze, r565 law), BOTH SIDES SKIP-PAST-PUBLISHED "\n'
             '          "CHAIN DUAL-STATE CONVERGENT (W90 r579 precedent: A "\n'
             '          "231_004..233_003 CLEAN + B 57_301..57_500 CLEAN zero "\n'
             '          "refusal points; ADMIT receipt results/_r580bma_w94_band_"\n'
             '          "gate.py; W95+ projection A 233_004..235_003 CLEAN / B "\n'
             '          "57_501..57_700 CLEAN disclosed for the next freezer; not "\n'
             '          "a free pick -- R250), N3-R1 used-seed leg, probe-seed "\n'
             '          "cluster leg, law sec.4 W94 row, r580 bm-a] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG94, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W94 segment landed (insert after W90 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W94 row -------------------
ROW94 = """
- N1 波94（r580 bm-a 冻·prereg 时展行）：**第八十四枚引擎波·bm-a 第二十五枚自有波〔机面 derive：engine_owner 行 82+在飞 W93 席+本候选／engine_owner==bm-a 行 24+本候选〕**·engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 同 W10-W92 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-a 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启免做·W44/W45/W48/W54/W57/W62/W64/W68/W73/W75/W77/W81/W84/W86/W87/W90 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 94=注册表 W92 行后首个自由号·跳过 bm-b 已公示 W93 席**〔published=reserved r518-① 律·**前席让路**：本机 W93 机闸独立 derive 与 bm-b 席位带逐位同带→r511 commit-order 后到 zero-cost 让路〔零烧零冻结零 finalize·gate 回执 results/_r580bma_w93_band_gate.py 留档〕·**席位公示=MSG-20261002-1514-bma**〔让路回执+占位一体·先于冻结 commit 推 origin 5d2daedc0=r565 早可见性律〕）·本窗实况=**W1..W91 finalize 全落账（净链头 564,748=W91 bm-b r579 one-pass〔562,548→564,748〕·K=198,120 合并池）+双在飞上游席（W92 bm-c 烧录在飞+W93 bm-b 席位公示冻结在飞）=本波 finalize 时 FAIL-CLOSED 前置双空档**（跑时复核 r307 两态律恒在）·**带位（r580 机闸 derive 律·活注册表机证·双态收敛门 W90 r579 先例·ADMIT 回执=results/_r580bma_w94_band_gate.py rc0 state A 实跑）**：**A-ext seed=231_004..233_003**（**A 面 skip-past-published 链**==W92 行 A 尾 229_003+1 起→W93 席位带 229_004..231_003 拒→首净窗·步长 2_000·CLEAN 零拒绝点·**双态收敛**=state B W93 注册后算术续带同带逐位）；**B-ext exit seed=57_301..57_500**（==W92 行 B 尾 56_900+1 起→W93 席位带 57_101..57_300 拒→首净窗·步长 200·CLEAN 零拒绝点·双态收敛同上）。R250：W94 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W94 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W94_PREREG.md（冻结件·锚=W91 finalize 实测值〔锚滚动律·单波跨锚自 W76 滚动至 W91〕）·**W95+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 233_004..235_003 **CLEAN**；B 57_501..57_700 **CLEAN**（双侧算术预期零拒绝点）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce294\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW94.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W94 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    94: {"a": (231_004') == 1, 'FIX-B FAIL: W94 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W94"') == 1, 'FIX-B FAIL: W94 config not exactly once'
for w in range(58, 93):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W94 materializer face') == 2, \
    'FIX-B FAIL: W94 leg+summary must be exactly 2'
for w in range(48, 93):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce294\uff08') == 1, 'FIX-B FAIL: canon W94 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W94 added per face')

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
print('FREEZE_EDITS_OK 94')
