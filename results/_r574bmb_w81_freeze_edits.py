# -*- coding: utf-8 -*-
"""r574 bm-b W81 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r566 lineage).

FIX-A (origin-blob freshness): every tracked edit target must be content-equal
  to origin/main BEFORE any edit runs. Kills the r559 stale-base clobber.
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W80, bm-c's),
  and after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W81 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W81 = SEVENTY-FIRST engine wave, bm-b's TWENTY-SEVENTH owned per
machine-derive (engine_owner==bm-b rows 26 + candidate). Seat declared
published=reserved (MSG-20261002-1220-bmb, r518-1 law, PUSHED to origin
BEFORE this freeze per r565 early-visibility lesson, commit d0f450cb5;
same-window W80 YIELD to bm-c r364 7fbeadb2e first-land per r511
commit-order law + same-window next-seat re-occupation per r565 law;
never-dry standing step under CEO de-throttle order O-20261001-2355
sec.2 own-continuous-series).
BANDS: A ARITHMETIC CONTINUATION from the registered W80 tail --
205_004..207_003 (= W80 A end 205_003 + 1), CLEAN; B PAST-HIT RESTART
-- the arithmetic window 53_801..54_000 is REFUSED at the upper-edge
point SEED_REGISTRY t18_deep_axis=54_000, first clean window
54_001..54_200 (W74-B upper-edge family, both readings coincide, no
fork face; F-20261002-03 skip-semantics divergence not triggered).
W1..W79 finalizes ALL LANDED (net chain head 538,348, K=171,720, bm-b
r574 same window); W80 bm-c (registered r364, burn in flight) = ONE
in-flight upstream seat at this freeze (FAIL-CLOSED r307).
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
             69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80]
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face')
       for w in range(59, 81)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 81)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[81] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '81: {"a": (205_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    80: {"a": (203_004, 205_003), "b_exit": (53_601, 53_800),\n'
          '         "engine_owner": "bm-c"},\n'
          '}\n')
    NEW = ('    80: {"a": (203_004, 205_003), "b_exit": (53_601, 53_800),\n'
           '         "engine_owner": "bm-c"},\n'
           '    # SEVENTY-FIRST ENGINE-OWNED WAVE (r574 bm-b freeze): bm-b\'s\n'
           '    # TWENTY-SEVENTH owned per machine-derive (engine_owner==bm-b\n'
           '    # rows 26 + candidate). Wave 81 = first free number after the\n'
           '    # registered W80 row; same-window W80 YIELD to bm-c r364\n'
           '    # (7fbeadb2e first-land 12:07:03 per r511 commit-order law,\n'
           '    # receipt MSG-20261002-1220-bmb) + next-seat re-occupation\n'
           '    # per r565 law. Seat declared published=reserved\n'
           '    # MSG-20261002-1220-bmb PUSHED to origin before this freeze\n'
           '    # per r565 early-visibility law, commit d0f450cb5; never-dry\n'
           '    # standing step under CEO de-throttle order O-20261001-2355\n'
           '    # sec.2.\n'
           '    # W1..W79 finalizes ALL LANDED (net chain head 538,348,\n'
           '    # K=171,720, bm-b r574 this window); W80 bm-c (registered\n'
           '    # r364, burn in flight) = ONE in-flight upstream seat at\n'
           '    # this freeze (FAIL-CLOSED r307).\n'
           '    # A = ARITHMETIC CONTINUATION from the W80 row tail, zero\n'
           '    # skip: 205_004..207_003 (= W80 A end 205_003 + 1), CLEAN.\n'
           '    # B = PAST-HIT RESTART: arithmetic 53_801..54_000 REFUSED\n'
           '    # at the upper-edge point SEED_REGISTRY t18_deep_axis=54_000\n'
           '    # -> first clean window 54_001..54_200 (W74-B upper-edge\n'
           '    # family; both readings coincide = single reading, no fork\n'
           '    # face, F-20261002-03 not triggered).\n'
           '    # Machine-verified at prereg time\n'
           '    # (results/_r574bmb_w81_band_gate.py ADMIT receipt vs the\n'
           '    # 78-row pre-W81 table + live SEED_REGISTRY values + probe\n'
           '    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin\n'
           '    # slot vacancy machine-checked). NOT a re-pick (R250: W81\n'
           '    # bands were never assigned).\n'
           '    81: {"a": (205_004, 207_003), "b_exit": (54_001, 54_200),\n'
           '         "engine_owner": "bm-b"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[81] landed (anchor=W80 row, insert)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[81] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '81: {"batch": "PERPETUAL-N1-W81"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('"shard_subdir": "n1_w80", "out_name": "n1_w80_results.json",\n'
          '                            "engine_owner": "bm-c"},\n'
          '                       }')
    NEW2 = ('"shard_subdir": "n1_w80", "out_name": "n1_w80_results.json",\n'
            '                            "engine_owner": "bm-c"},\n'
            '                       81: {"batch": "PERPETUAL-N1-W81",\n'
            '                            "prereg": ("research/PERPETUAL_N1_W81_PREREG.md (wave-level frozen "\n'
            '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
            '                                       "new seed bands only; SEVENTY-FIRST ENGINE-OWNED WAVE, "\n'
            '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
            '                                       "(first-free-number law over the registered W80 row; "\n'
            '                                       "same-window W80 YIELD to bm-c r364 7fbeadb2e first-land "\n'
            '                                       "per r511 commit-order law + next-seat re-occupation "\n'
            '                                       "per r565 law; seat declared published=reserved "\n'
            '                                       "MSG-20261002-1220-bmb PUSHED to origin BEFORE this "\n'
            '                                       "freeze per r565 early-visibility lesson, commit "\n'
            '                                       "d0f450cb5), "\n'
            '                                       "engine_owner=bm-b, wave 81 A ARITHMETIC CONTINUATION "\n'
            '                                       "zero skip (A 205_004..207_003 CLEAN) + B PAST-HIT "\n'
            '                                       "RESTART (arithmetic 53_801..54_000 REFUSED at the "\n'
            '                                       "upper-edge point SEED_REGISTRY t18_deep_axis=54_000 "\n'
            '                                       "-> first clean window 54_001..54_200; W74-B upper-edge "\n'
            '                                       "family, both readings coincide = single reading, no "\n'
            '                                       "fork face, F-20261002-03 not triggered); "\n'
            '                                       "W1..W79 finalizes ALL LANDED at this freeze (net "\n'
            '                                       "chain head 538,348, K=171,720, bm-b r574 this "\n'
            '                                       "window), W80 bm-c = ONE in-flight upstream seat "\n'
            '                                       "(finalize chain-pending FAIL-CLOSED r307)"),\n'
            '                            "a_seed_base": 205_004,        # law sec.4 W81 A: 205_004..207_003 (arithmetic continuation)\n'
            '                            "b_exit_seed_base": 54_001,   # law sec.4 W81 B: 54_001..54_200 (past-hit restart over t18_deep_axis=54_000)\n'
            '                            "shard_subdir": "n1_w81", "out_name": "n1_w81_results.json",\n'
            '                            "engine_owner": "bm-b"},\n'
            '                       }')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[81] landed (anchor=W80 entry tail, insert)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W81 leg --------------
LEG81 = '''
    # --- W81 materializer face (r574 bm-b freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2):
    #     bm-b's TWENTY-SEVENTH owned per machine-derive (engine_owner==bm-b
    #     rows 26 + candidate); wave 81 = first free number after the
    #     registered W80 row (same-window W80 yield to bm-c r364
    #     7fbeadb2e first-land per r511 commit-order law; seat declared
    #     published=reserved MSG-20261002-1220-bmb pushed to origin
    #     BEFORE the freeze; never-dry standing step).
    #     W1..W79 finalizes ALL LANDED (net chain head 538,348, K=171,720,
    #     bm-b r574); W80 bm-c (registered r364, burn in flight) = ONE
    #     in-flight upstream seat at this freeze (FAIL-CLOSED r307).
    #     A = ARITHMETIC CONTINUATION from the W80 tail no skip
    #     (205_004..207_003 CLEAN) + B = PAST-HIT RESTART (arithmetic
    #     53_801..54_000 REFUSED at the upper-edge point SEED_REGISTRY
    #     t18_deep_axis=54_000 -> first clean window 54_001..54_200;
    #     W74-B upper-edge family, both readings coincide, single
    #     reading no fork face; ADMIT receipt
    #     results/_r574bmb_w81_band_gate.py) --
    _set_wave(81)
    try:
        assert WAVE_CONFIGS[81]["a_seed_base"] == pf.N1_BANDS[81]["a"][0], \\
            "W81 A band drift vs law mirror"
        assert WAVE_CONFIGS[81]["b_exit_seed_base"] == \\
            pf.N1_BANDS[81]["b_exit"][0], "W81 B band drift vs law mirror"
        assert WAVE_CONFIGS[81].get("engine_owner") == \\
            pf.N1_BANDS[81].get("engine_owner") == "bm-b", \\
            "W81 engine_owner drift (law mirror parity)"
        w81_a = {A_SEED_BASE + j for j in range(A_N)}
        w81_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w81_a & w81_b), "W81 A/B band overlap"
        assert not (w81_a & reg_ints) and not (w81_b & reg_ints), \\
            "W81 hits SEED_REGISTRY"
        for nm, band in (("A", w81_a), ("B", w81_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W81 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W81 {nm} hits W1"
            assert not (band & probes), f"W81 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W70..W80
        # are REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly.
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
        assert pf.N1_BANDS[79] == {"a": (201_004, 203_003),
                                   "b_exit": (53_401, 53_600),
                                   "engine_owner": "bm-b"}, \\
            "registered W79 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[80] == {"a": (203_004, 205_003),
                                   "b_exit": (53_601, 53_800),
                                   "engine_owner": "bm-c"}, \\
            "registered W80 row parity drift (r307 two-state)"
        # prior-wave disjointness incl. W48..W80 (all registered; W80
        # in flight -- coexists by band disjointness per r531).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                      70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80):
            assert not (w81_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W81 A hits W{wprev}"
            assert not (w81_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W81 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W81 clears it.
        n3r1_used81 = set(range(70_000, 70_006))
        assert not (w81_a & n3r1_used81) and not (w81_b & n3r1_used81), \\
            "W81 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w81_a & lfc_actual12) and not (w81_b & lfc_actual12), \\
            "W81 bands must clear the lfc actual draw range"
        assert not (w81_a & options_actual12) and \\
            not (w81_b & options_actual12), \\
            "W81 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W81 row, r574): A ARITHMETIC
        # CONTINUATION from the registered W80 tail (zero skip); B
        # PAST-HIT RESTART over the upper-edge refusal point
        # t18_deep_axis=54_000 (both readings coincide, single
        # reading, no fork face).
        assert WAVE_CONFIGS[81]["a_seed_base"] == 205_004 == 205_003 + 1, \\
            "W81 A must start at the registered W80 A end + 1 " \\
            "(arithmetic continuation window 205_004..207_003 CLEAN)"
        assert WAVE_CONFIGS[81]["b_exit_seed_base"] == 54_001 == 54_000 + 1, \\
            "W81 B must start at the refusal point 54_000 + 1 " \\
            "(past-hit restart window 54_001..54_200, W74-B family)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W81-SHARD-0",
                                          "n1w81-0of12"), "W81 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W81-SHARD-11",
                                          "n1w81-11of12")
        assert SHARD_DIR.endswith("n1_w81") and OUT.endswith(
            "n1_w81_results.json"), "W81 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                      70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W81 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W81_PREREG.md")), \\
            "W81 per-wave prereg missing (materializer requirement)"
        # W81 finalize cumulative deps: W17..W79 outputs ALL PRESENT
        # (static landed seats; chain head 538,348 = W79 bm-b r574
        # K=171,720; W80 bm-c = ONE in-flight upstream seat -- the
        # finalize merge loop derives the wave set from registry keys
        # at run time and stays FAIL-CLOSED on the not-yet-finalized
        # seat, r307 two-state law).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                      43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
                      56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68,
                      69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W81 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 81 (no 15; incl.
        # 48..80 -- all registered, W80 finalize in flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 81) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
             65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
             80], \\
            "W81 prior-wave set must derive from registry keys (no 15, " \\
            "incl. 48..80)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W81 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG81.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W81 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 5th face) ------
t2c, eol2c = load(FP2)
if '+ W81 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('r364 bm-c] "\n'
          '          "+ T-141 s2 ')
    SEG81 = ('r364 bm-c] "\n'
             '          "+ W81 materializer face [same guard set, dep=W17..W79 "\n'
             '          "outputs ALL PRESENT (landed chain head 538,348, "\n'
             '          "K=171,720, bm-b r574 same window), W80 bm-c = ONE "\n'
             '          "in-flight upstream seat (FAIL-CLOSED r307 at run "\n'
             '          "time), SEVENTY-FIRST ENGINE-OWNED WAVE bm-b\'s "\n'
             '          "TWENTY-SEVENTH owned claim per machine-derive "\n'
             '          "(engine_owner==bm-b rows 26 + candidate), "\n'
             '          "engine_owner=bm-b per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series (wave 81 = "\n'
             '          "first FREE number after the registered W80 row; "\n'
             '          "same-window W80 YIELD to bm-c r364 7fbeadb2e first-land "\n'
             '          "per r511 commit-order law + next-seat re-occupation per "\n'
             '          "r565 law; seat declared published=reserved "\n'
             '          "MSG-20261002-1220-bmb pushed to origin BEFORE the "\n'
             '          "freeze per r565 early-visibility lesson), A "\n'
             '          "ARITHMETIC CONTINUATION from the W80 tail no skip "\n'
             '          "(205_004..207_003 CLEAN) + B PAST-HIT RESTART "\n'
             '          "(arithmetic 53_801..54_000 REFUSED at the "\n'
             '          "upper-edge point SEED_REGISTRY t18_deep_axis=54_000 -> "\n'
             '          "first clean window 54_001..54_200; W74-B upper-edge "\n'
             '          "family, both readings coincide = single reading, no "\n'
             '          "fork face, F-20261002-03 not triggered; ADMIT receipt "\n'
             '          "results/_r574bmb_w81_band_gate.py; not a "\n'
             '          "free pick -- R250), N3-R1 used-seed leg, probe-seed "\n'
             '          "cluster leg, law sec.4 W81 row, r574 bm-b] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG81, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W81 segment landed (insert after W80 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W81 row -------------------
ROW81 = """
- N1 波81（r574 bm-b 冻·prereg 时展行）：**第七十一枚引擎波·bm-b 第二十七枚自有波〔机面 derive：engine_owner==bm-b 行 26+本候选〕**·engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W80 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-b 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启免做·W55/W56/W59/W61/W65/W67/W70/W72/W74/W76/W79 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 81=注册表 W80 行后首个自由号**·**W80 让路注记：本机 W80 席位 MSG-1210-bmb 后到于 bm-c 席位 MSG-1204-bmc＋冻结 7fbeadb2e（12:07:03 first-land）→按 r511 commit 时序律让路撤席（回执 MSG-20261002-1220-bmb·零成本：零冻结编辑零烧录零 finalize）·同窗下一席位再占位=r565 律**·席位公示=MSG-20261002-1220-bmb（published=reserved r518-① 律·**先于冻结 commit 推 origin=r565 early-visibility 律〔三机活跃窗撞面预防〕**·W48/W49/W55/W62/W65/W67/W68/W69/W70/W71/W72/W73/W74/W75/W78/W79 先例）·r511 表尾锁例冻结前 fetch 实核表尾时 W81 号位净空·origin 侧 vacancy 机验】·**带位=A 算术续带＋B past-hit restart（单读法零分叉面）**：W80 行携带 W81+ 警示投影尾 **A 205_004..207_003 CLEAN／B 53_801..54_000 REFUSED at SEED_REGISTRY 54_000**（bm-c r364 gate 投影腿机证）→本波 **r574 bm-b gate 机闸独立 derive 复核逐字同**（r302 陈旧指针证伪律下非 prose 转抄——机闸 derive 为唯一 derive 面·prose 交叉核对；r363 镜面教训=w77 行 prose 投影曾 STALE 靠 gate 拒绝事实腿抓回=本波同腿强制）→本波 **A-ext seed=205_004..207_003**（**A 面算术续带**==W80 A 尾 205_003+1·步长逐字·零跳位）；**B-ext exit seed=54_001..54_200**（**B 面 past-hit restart 续带**：B 算术窗 53_801..54_000 于上缘尾点被 SEED_REGISTRY **t18_deep_axis=54_000** 拒绝→首净窗 **54_001..54_200**〔W74-B 上缘点族先例·两读法恒同=单读法零分叉·F-20261002-03 跳位语义分叉面不触发〕·R250：W81 带从未指派·测量面零结果可钓）。【机证净空——leg0 七十九键（78 注册行+候选）+leg0b W80 行 W81+ 警示 prose 在场校验+leg1-A 算术位 CLEAN 机证+leg1-B 算术位拒绝事实==[54_000] 机证+leg2 双侧首净窗==候选逐位+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验·**MSG-0640 三修工具**（FIX-A 编辑前 origin-blob 等值断言+FIX-B 锚=最后注册行+行存活核查+FIX-C 推送前纯增量 diff 断言）〕·ADMIT 回执=results/_r574bmb_w81_band_gate.py·r574 bm-b 起草窗实跑·非重挑 R250。扫描面=pre-W81 七十八行 N1 带表【含 **W78 行 199_004..201_003/53_201..53_400〔bm-c r363 冻·finalize 已落账 K=169,520·链头 536,148·bm-c r364〕**·**W79 行 201_004..203_003/53_401..53_600〔bm-b r573 冻·finalize 已落账 K=171,720·链头 538,348·bm-b r574 本窗〕**·**W80 行 203_004..205_003/53_601..53_800〔bm-c r364 冻·烧录在飞·finalize 未落账〕**】·**一在飞上游席披露：本波 finalize 链序前置=W80 bm-c——FAIL-CLOSED r307 两态律·该席落账后 one-pass**。W81 行 **W82+ 投影（gate 投影腿机证·W82 prereg 窗机闸复核 r335 律）**：**A 207_004..209_003 CLEAN／B 54_201..54_400 CLEAN**（A 算术续带==W81 A 尾 207_003+1·B +200 续带==W81 B 尾 54_200+1·双侧零拒绝点·单读法零分叉）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce281\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW81.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W81 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    81: {"a": (205_004') == 1, 'FIX-B FAIL: W81 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W81"') == 1, 'FIX-B FAIL: W81 config not exactly once'
for w in range(59, 81):
    assert n11.count(f'W{w} materializer face') == 2, f'FIX-B FAIL: W{w} leg lost'
assert n11.count('W81 materializer face') == 2, \
    'FIX-B FAIL: W81 leg+summary must be exactly 2'
for w in range(48, 81):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce281\uff08') == 1, 'FIX-B FAIL: canon W81 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W81 added per face')

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
