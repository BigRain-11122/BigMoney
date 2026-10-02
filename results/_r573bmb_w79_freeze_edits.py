# -*- coding: utf-8 -*-
"""r573 bm-b W79 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r566 lineage).

FIX-A (origin-blob freshness): every tracked edit target must be content-equal
  to origin/main BEFORE any edit runs. Kills the r559 stale-base clobber.
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W78, bm-c's),
  and after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W79 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W79 = SIXTY-EIGHTH engine wave, bm-b's TWENTY-SIXTH owned per machine-derive
(engine_owner==bm-b rows 25 + candidate). Seat declared published=reserved
(MSG-20261002-1151-bmb, r518-1 law, PUSHED to origin BEFORE this freeze per
r565 early-visibility lesson; never-dry standing step under CEO de-throttle
order O-20261001-2355 sec.2 own-continuous-series; wave 79 = first free
number after the registered W78 row, r511 tail-lock, origin vacancy
machine-checked).
BANDS: BOTH SIDES plain ARITHMETIC CONTINUATION from the registered W78
tail -- A 201_004..203_003 (= W78 A end 201_003 + 1), B 53_401..53_600
(= W78 B end 53_400 + 1); zero skip both sides, single reading, no fork
face (F-20261002-03 skip-semantics divergence not triggered; the
j13v2_mill pair 53_000/53_100 sits BELOW the B window).
W1..W76 finalizes ALL LANDED (net chain head 531,748, K=165,120, bm-b r573
same window); W77 bm-a (burned 12/12, finalize pending) + W78 bm-c (burn
in flight, finalize pending) = TWO in-flight upstream seats at this
freeze (FAIL-CLOSED r307).
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
TARGETS = [
    'scripts/perpetual_faces.py',
    'scripts/perpetual_faces_n1.py',
    'research/PERPETUAL_FACES.md',
]
for p in TARGETS:
    r = subprocess.run(['git', '-C', REPO, 'diff', 'origin/main', '--numstat', '--', p],
                       capture_output=True)
    out = r.stdout.decode('utf-8', 'replace').strip()
    if r.returncode != 0:
        sys.exit(f'FIX-A git fail on {p}')
    for line in out.splitlines():
        add, dele, path = line.split('\t')
        if int(dele) > 0:
            sys.exit(f'STALE BASE (FIX-A abort): {p} shows {dele} deleted lines vs '
                     f'origin/main -- checkout origin version first '
                     f'(r559 clobber cure)')
print('FIX-A: all 3 tracked edit targets show zero deletions vs origin/main (fresh base)')

# ---------------- survival signature baseline (FIX-B) ------------------------
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20,
             21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
             37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52,
             53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68,
             69, 70, 71, 72, 73, 74, 75, 76, 77, 78]
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face')
       for w in range(59, 79)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 79)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[79] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '79: {"a": (201_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    78: {"a": (199_004, 201_003), "b_exit": (53_201, 53_400),\n'
          '         "engine_owner": "bm-c"},\n'
          '}\n')
    NEW = ('    78: {"a": (199_004, 201_003), "b_exit": (53_201, 53_400),\n'
           '         "engine_owner": "bm-c"},\n'
           '    # SIXTY-EIGHTH ENGINE-OWNED WAVE (r573 bm-b freeze): bm-b\'s\n'
           '    # TWENTY-SIXTH owned per machine-derive (engine_owner==bm-b\n'
           '    # rows 25 + candidate). Wave 79 = next free number after the\n'
           '    # registered W78 row (seat declared published=reserved\n'
           '    # MSG-20261002-1151-bmb PUSHED to origin BEFORE this freeze\n'
           '    # per r565 early-visibility lesson, r518-1 law; never-dry\n'
           '    # standing step under CEO de-throttle order O-20261001-2355\n'
           '    # sec.2).\n'
           '    # W1..W76 finalizes ALL LANDED (net head 531,748, K=165,120,\n'
           '    # bm-b r573); W77 bm-a (burned 12/12, finalize pending) +\n'
           '    # W78 bm-c (burn in flight, finalize pending) = TWO\n'
           '    # in-flight upstream seats at this freeze (FAIL-CLOSED\n'
           '    # r307).\n'
           '    # BOTH SIDES ARITHMETIC CONTINUATION from the W78 row tail,\n'
           '    # zero skip: A 201_004..203_003 (= W78 A end 201_003 + 1),\n'
           '    # B 53_401..53_600 (= W78 B end 53_400 + 1); single reading,\n'
           '    # no fork face (F-20261002-03 not triggered; the j13v2_mill\n'
           '    # pair 53_000/53_100 sits BELOW the B window).\n'
           '    # Machine-verified at prereg time\n'
           '    # (results/_r573bmb_w79_band_gate.py ADMIT receipt vs the\n'
           '    # 76-row pre-W79 table + live SEED_REGISTRY values + probe\n'
           '    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin\n'
           '    # slot vacancy machine-checked). NOT a re-pick (R250: W79\n'
           '    # bands were never assigned).\n'
           '    79: {"a": (201_004, 203_003), "b_exit": (53_401, 53_600),\n'
           '         "engine_owner": "bm-b"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[79] landed (anchor=W78 row, insert)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[79] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '79: {"batch": "PERPETUAL-N1-W79"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('"shard_subdir": "n1_w78", "out_name": "n1_w78_results.json",\n'
          '                            "engine_owner": "bm-c"},\n'
          '                       }')
    NEW2 = ('"shard_subdir": "n1_w78", "out_name": "n1_w78_results.json",\n'
            '                            "engine_owner": "bm-c"},\n'
            '                       79: {"batch": "PERPETUAL-N1-W79",\n'
            '                            "prereg": ("research/PERPETUAL_N1_W79_PREREG.md (wave-level frozen "\n'
            '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
            '                                       "new seed bands only; SIXTY-EIGHTH ENGINE-OWNED WAVE, "\n'
            '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
            '                                       "(first-free-number law over the registered W78 row; "\n'
            '                                       "seat declared published=reserved MSG-20261002-1151-bmb "\n'
            '                                       "PUSHED to origin BEFORE this freeze per r565 "\n'
            '                                       "early-visibility lesson), "\n'
            '                                       "engine_owner=bm-b, wave 79 BOTH SIDES ARITHMETIC "\n'
            '                                       "CONTINUATION zero skip (A 201_004..203_003 CLEAN + "\n'
            '                                       "B 53_401..53_600 CLEAN; single reading, no fork "\n'
            '                                       "face, F-20261002-03 not triggered; j13v2_mill pair "\n'
            '                                       "53_000/53_100 BELOW the B window); "\n'
            '                                       "W1..W76 finalizes ALL LANDED at this freeze (net "\n'
            '                                       "chain head 531,748, K=165,120, bm-b r573), W77 bm-a + "\n'
            '                                       "W78 bm-c = TWO in-flight upstream seats "\n'
            '                                       "(finalize chain-pending FAIL-CLOSED r307)"),\n'
            '                            "a_seed_base": 201_004,        # law sec.4 W79 A: 201_004..203_003 (arithmetic continuation)\n'
            '                            "b_exit_seed_base": 53_401,   # law sec.4 W79 B: 53_401..53_600 (arithmetic continuation)\n'
            '                            "shard_subdir": "n1_w79", "out_name": "n1_w79_results.json",\n'
            '                            "engine_owner": "bm-b"},\n'
            '                       }')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[79] landed (anchor=W78 entry tail, insert)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W79 leg --------------
LEG79 = '''
    # --- W79 materializer face (r573 bm-b freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2):
    #     bm-b's TWENTY-SIXTH owned per machine-derive (engine_owner==bm-b
    #     rows 25 + candidate); wave 79 = first free number after the
    #     registered W78 row (seat declared published=reserved
    #     MSG-20261002-1151-bmb pushed to origin BEFORE the freeze;
    #     never-dry standing step).
    #     W1..W76 finalizes ALL LANDED (net chain head 531,748, K=165,120,
    #     bm-b r573); W77 bm-a (burned 12/12, finalize pending) + W78 bm-c
    #     (burn in flight, finalize pending) = TWO in-flight upstream
    #     seats at this freeze (FAIL-CLOSED r307).
    #     BOTH SIDES ARITHMETIC CONTINUATION from the W78 tail no skip
    #     (A 201_004..203_003 CLEAN + B 53_401..53_600 CLEAN; single
    #     reading, no fork face; ADMIT receipt
    #     results/_r573bmb_w79_band_gate.py; not a re-pick -- R250) --
    _set_wave(79)
    try:
        assert WAVE_CONFIGS[79]["a_seed_base"] == pf.N1_BANDS[79]["a"][0], \\
            "W79 A band drift vs law mirror"
        assert WAVE_CONFIGS[79]["b_exit_seed_base"] == \\
            pf.N1_BANDS[79]["b_exit"][0], "W79 B band drift vs law mirror"
        assert WAVE_CONFIGS[79].get("engine_owner") == \\
            pf.N1_BANDS[79].get("engine_owner") == "bm-b", \\
            "W79 engine_owner drift (law mirror parity)"
        w79_a = {A_SEED_BASE + j for j in range(A_N)}
        w79_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w79_a & w79_b), "W79 A/B band overlap"
        assert not (w79_a & reg_ints) and not (w79_b & reg_ints), \\
            "W79 hits SEED_REGISTRY"
        for nm, band in (("A", w79_a), ("B", w79_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W79 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W79 {nm} hits W1"
            assert not (band & probes), f"W79 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W68..W78
        # are REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly.
        assert pf.N1_BANDS[68] == {"a": (179_004, 181_003),
                                   "b_exit": (50_501, 50_700),
                                   "engine_owner": "bm-a"}, \\
            "registered W68 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[69] == {"a": (181_004, 183_003),
                                   "b_exit": (50_701, 50_900),
                                   "engine_owner": "bm-c"}, \\
            "registered W69 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[70] == {"a": (183_004, 185_003),
                                   "b_exit": (51_001, 51_200),
                                   "engine_owner": "bm-b"}, \\
            "registered W70 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[71] == {"a": (185_004, 187_003),
                                   "b_exit": (51_201, 51_400),
                                   "engine_owner": "bm-c"}, \\
            "registered W71 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[72] == {"a": (187_004, 189_003),
                                   "b_exit": (51_401, 51_600),
                                   "engine_owner": "bm-b"}, \\
            "registered W72 row parity drift (r307 two-state)"
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
            "registered W77 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[78] == {"a": (199_004, 201_003),
                                   "b_exit": (53_201, 53_400),
                                   "engine_owner": "bm-c"}, \\
            "registered W78 row parity drift (r307 two-state)"
        # prior-wave disjointness incl. W48..W78 (all registered; W77/W78
        # in flight -- coexist by band disjointness per r531).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                      70, 71, 72, 73, 74, 75, 76, 77, 78):
            assert not (w79_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W79 A hits W{wprev}"
            assert not (w79_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W79 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W79 clears it.
        n3r1_used79 = set(range(70_000, 70_006))
        assert not (w79_a & n3r1_used79) and not (w79_b & n3r1_used79), \\
            "W79 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w79_a & lfc_actual12) and not (w79_b & lfc_actual12), \\
            "W79 bands must clear the lfc actual draw range"
        assert not (w79_a & options_actual12) and \\
            not (w79_b & options_actual12), \\
            "W79 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W79 row, r573): BOTH SIDES ARITHMETIC
        # CONTINUATION from the registered W78 tail (zero skip) --
        # the arithmetic windows are CLEAN vs the full reserved
        # universe (no refusal point inside either window; single
        # reading, no fork face, F-20261002-03 not triggered).
        assert WAVE_CONFIGS[79]["a_seed_base"] == 201_004 == 201_003 + 1, \\
            "W79 A must start at the registered W78 A end + 1 " \\
            "(arithmetic continuation window 201_004..203_003 CLEAN)"
        assert WAVE_CONFIGS[79]["b_exit_seed_base"] == 53_401 == 53_400 + 1, \\
            "W79 B must start at the registered W78 B end + 1 " \\
            "(arithmetic continuation window 53_401..53_600 CLEAN)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W79-SHARD-0",
                                          "n1w79-0of12"), "W79 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W79-SHARD-11",
                                          "n1w79-11of12")
        assert SHARD_DIR.endswith("n1_w79") and OUT.endswith(
            "n1_w79_results.json"), "W79 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                      70, 71, 72, 73, 74, 75, 76, 77, 78):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W79 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W79_PREREG.md")), \\
            "W79 per-wave prereg missing (materializer requirement)"
        # W79 finalize cumulative deps: W17..W76 outputs ALL PRESENT
        # (static landed seats; chain head 531,748 = W76 bm-b r573
        # K=165,120; W77 bm-a + W78 bm-c = TWO in-flight upstream
        # seats -- the finalize merge loop derives the wave set from
        # registry keys at run time and stays FAIL-CLOSED on the
        # not-yet-finalized seats, r307 two-state law).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                      43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
                      56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68,
                      69, 70, 71, 72, 73, 74, 75, 76):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W79 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 79 (no 15; incl.
        # 48..78 -- all registered, W77/W78 finalize in flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 79) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
             65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78], \\
            "W79 prior-wave set must derive from registry keys (no 15, " \\
            "incl. 48..78)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W79 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG79.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W79 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 5th face) ------
t2c, eol2c = load(FP2)
if '+ W79 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('r363 bm-c] "\n'
          '          "+ T-141 s2 ')
    SEG79 = ('r363 bm-c] "\n'
             '          "+ W79 materializer face [same guard set, dep=W17..W76 "\n'
             '          "outputs ALL PRESENT (landed chain head 531,748, "\n'
             '          "K=165,120, bm-b r573 same window), W77 bm-a + W78 bm-c = "\n'
             '          "TWO in-flight upstream seats (FAIL-CLOSED r307 at run "\n'
             '          "time), SIXTY-EIGHTH ENGINE-OWNED WAVE bm-b\'s "\n'
             '          "TWENTY-SIXTH owned claim per machine-derive "\n'
             '          "(engine_owner==bm-b rows 25 + candidate), "\n'
             '          "engine_owner=bm-b per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series (wave 79 = "\n'
             '          "first FREE number after the registered W78 row; seat "\n'
             '          "declared published=reserved MSG-20261002-1151-bmb pushed "\n'
             '          "to origin BEFORE the freeze per r565 early-visibility "\n'
             '          "lesson), BOTH SIDES ARITHMETIC CONTINUATION from the "\n'
             '          "W78 tail no skip (A 201_004..203_003 CLEAN + B "\n'
             '          "53_401..53_600 CLEAN; single reading, no fork face, "\n'
             '          "F-20261002-03 not triggered; j13v2_mill pair "\n'
             '          "53_000/53_100 BELOW the B window; ADMIT receipt "\n'
             '          "results/_r573bmb_w79_band_gate.py; not a "\n'
             '          "free pick -- R250), N3-R1 used-seed leg, probe-seed "\n'
             '          "cluster leg, law sec.4 W79 row, r573 bm-b] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG79, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W79 segment landed (insert after W78 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W79 row -------------------
ROW79 = """
- N1 波79（r573 bm-b 冻·prereg 时展行）：**第六十八枚引擎波·bm-b 第二十六枚自有波〔机面 derive：engine_owner==bm-b 行 25+本候选〕**·engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W78 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-b 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启免做·W55/W56/W59/W61/W65/W67/W70/W72/W74/W76 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 79=注册表 W78 行后首个自由号**·席位公示=MSG-20261002-1151-bmb（published=reserved r518-① 律·**先于冻结 commit 推 origin=r565 early-visibility 律〔三机活跃窗撞面预防〕**·W48/W49/W55/W62/W65/W67/W68/W69/W70/W71/W72/W73/W74/W75/W78 先例）·r511 表尾锁例冻结前 fetch 实核表尾时 W79 号位净空·origin 侧 vacancy 机验】·**带位=双侧算术续带零跳位（单读法零分叉面）**：W78 行携带 W79+ 警示投影 **A 201_004..203_003 CLEAN／B 53_401..53_600 CLEAN**（bm-c r363 gate 投影腿机证）→本波 **r573 bm-b gate 机闸独立 derive 复核逐字同**（r302 陈旧指针证伪律下非 prose 转抄——机闸 derive 为唯一 derive 面·prose 交叉核对；r363 镜面教训=W77 行 prose 投影曾 STALE 靠 gate 拒绝事实腿抓回=本波同腿强制）→本波 **A-ext seed=201_004..203_003**（**A 面算术续带**==W78 A 尾 201_003+1·步长逐字·零跳位）；**B-ext exit seed=53_401..53_600**（**B 面算术续带**==W78 B 尾 53_400+1·步长逐字·零跳位·SEED_REGISTRY j13v2_mill_ic1=53_000/j13v2_mill_ic2=53_100 均在窗下方净空·双侧算术窗零拒绝点=单读法零分叉〔F-20261002-03 跳位语义分叉面不触发〕·R250：W79 带从未指派·测量面零结果可钓）。【机证净空——leg0 七十七键（76 注册行+候选）+leg0b W78 行 W79+ 警示 prose 在场校验+leg1-A 算术位 CLEAN 机证+leg1-B 算术位 CLEAN 机证+leg2 双侧首净窗==候选逐位+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验·**MSG-0640 三修工具**（FIX-A 编辑前 origin-blob 等值断言+FIX-B 锚=最后注册行+行存活核查+FIX-C 推送前纯增量 diff 断言）〕·ADMIT 回执=results/_r573bmb_w79_band_gate.py·r573 bm-b 起草窗实跑·非重挑 R250。扫描面=pre-W79 七十六行 N1 带表【含 **W76 行 195_004..197_003/52_401..52_600〔bm-b r572 冻·finalize 已落账 K=165,120·链头 531,748·bm-b r573 本窗〕**·**W77 行 197_004..199_003/52_601..52_800〔bm-a r572 冻·烧录 12/12 已交付·finalize 未落账〕**·**W78 行 199_004..201_003/53_201..53_400〔bm-c r363 冻·烧录在飞·finalize 未落账〕**】·**两在飞上游席披露：本波 finalize 链序前置=W77 bm-a＋W78 bm-c——FAIL-CLOSED r307 两态律·两席均落账后 one-pass**。W79 行 **W80+ 投影（gate 投影腿机证·W80 prereg 窗机闸复核 r335 律）**：**A 203_004..205_003 CLEAN／B 53_601..53_800 CLEAN**（A 算术续带==W79 A 尾 203_003+1·B 算术续带==W79 B 尾 53_600+1）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce279\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW79.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W79 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    79: {"a": (201_004') == 1, 'FIX-B FAIL: W79 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W79"') == 1, 'FIX-B FAIL: W79 config not exactly once'
for w in range(59, 79):
    assert n11.count(f'W{w} materializer face') == 2, f'FIX-B FAIL: W{w} leg lost'
assert n11.count('W79 materializer face') == 2, \
    'FIX-B FAIL: W79 leg+summary must be exactly 2'
for w in range(48, 79):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce279\uff08') == 1, 'FIX-B FAIL: canon W79 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W79 added per face')

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
print('FREEZE_EDITS_OK')
