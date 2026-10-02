# -*- coding: utf-8 -*-
"""r363 bm-c W78 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r561/r566/r568/r570/r571 lineage).

FIX-A (origin-blob freshness): every tracked edit target must show zero
  deleted lines vs origin/main BEFORE any edit runs (r559 stale-base cure).
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W77, bm-a's);
  after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W78 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W78 = SIXTY-SEVENTH engine wave, bm-c's TWENTY-FOURTH owned per
machine-derive (engine_owner==bm-c rows 23 + candidate). r565
yield-then-reoccupy, SECOND re-occupation this window: W76 draft yielded
to bm-b r572 (bitwise cross-validation #11; 12/12 local twin shards
discarded pre-push, zero pollution) and W77 draft yielded to bm-a r572
(bitwise cross-validation #12; FIX-A intercepted the freeze-edits run
pre-edit = zero edit zero burn). Seat published=reserved
MSG-20261002-1150-bmc PUSHED to origin BEFORE this freeze (r565
early-visibility lesson); its B-band projection 53_001..53_200 was
prose-transcribed from the W77 row and is STALE vs the live registry
(j13v2_mill_ic2=53_100 inside it, bm-b J13V2 IC2 claim ac8a58490) --
corrected per the machine gate (results/_r363bmc_w78_band_gate.py
leg1-B2 refusal-facts identity) to the chained double-hit window
53_201..53_400 (W63-B in-register precedent family; fork 53_101..53_300
disclosed not taken, r566 face); correction receipt
MSG-20261002-1155-bmc (r535 machine-derive law).

Bands: A 199_004..201_003 (== W77 A end 199_003 + 1, arithmetic
continuation zero skip, CLEAN) / B 53_201..53_400 (chained double-hit
skip past j13v2_mill_ic1=53_000 + j13v2_mill_ic2=53_100). TWO in-flight
upstream seats at this freeze: W76 bm-b (burn in flight) + W77 bm-a
(burn in flight) -- finalize chain-pending FAIL-CLOSED r307.
W1..W75 finalizes ALL LANDED (net head 529,548, K=162,920 -- bm-a r572).
ADMIT receipt results/_r363bmc_w78_band_gate.py.
"""
import subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREAT = 0x08000000  # CREATE_NO_WINDOW (session-host flash guard)

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
TARGETS = [
    'scripts/perpetual_faces.py',
    'scripts/perpetual_faces_n1.py',
    'research/PERPETUAL_FACES.md',
]
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

# ---------------- survival signature baseline (FIX-B) ------------------------
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 78))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in
       range(58, 78)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 78)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[78] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '78: {"a": (199_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    77: {"a": (197_004, 199_003), "b_exit": (52_601, 52_800),\n'
          '         "engine_owner": "bm-a"},\n')
    NEW = ('    77: {"a": (197_004, 199_003), "b_exit": (52_601, 52_800),\n'
           '         "engine_owner": "bm-a"},\n'
           '    # SIXTY-SEVENTH ENGINE-OWNED WAVE (r363 bm-c freeze): bm-c\'s\n'
           '    # twenty-fourth owned per machine-derive (engine_owner==bm-c\n'
           '    # rows 23 + candidate). Wave 78 = first free number after the\n'
           '    # registered W77 row (r511 tail-lock, fetch-checked vacancy).\n'
           '    # r565 yield-then-reoccupy SECOND re-occupation this window:\n'
           '    # W76 draft yielded to bm-b r572 (bitwise cross-validation\n'
           '    # #11; 12/12 local twin shards discarded pre-push, zero\n'
           '    # pollution) + W77 draft yielded to bm-a r572 (bitwise\n'
           '    # cross-validation #12; FIX-A intercepted the freeze-edits\n'
           '    # run pre-edit = zero edit zero burn). Seat published=\n'
           '    # reserved MSG-20261002-1150-bmc PUSHED to origin before\n'
           '    # this freeze; its B-band prose projection 53_001..53_200\n'
           '    # was STALE vs the live registry (j13v2_mill_ic2=53_100\n'
           '    # inside it, bm-b J13V2 IC2 claim ac8a58490) -- corrected\n'
           '    # per the machine gate (leg1-B2 refusal-facts identity)\n'
           '    # to the chained double-hit window 53_201..53_400 (W63-B\n'
           '    # in-register precedent family; fork 53_101..53_300\n'
           '    # disclosed not taken, r566 face); correction receipt\n'
           '    # MSG-20261002-1155-bmc (r535 machine-derive law).\n'
           '    # Bands: A 199_004..201_003 == W77 A end 199_003 + 1\n'
           '    # (arithmetic continuation, CLEAN); B 53_201..53_400\n'
           '    # (chained double-hit skip past j13v2_mill_ic1=53_000 +\n'
           '    # j13v2_mill_ic2=53_100). W1..W75 finalizes ALL LANDED\n'
           '    # (net head 529,548, K=162,920 -- W75 bm-a r572); W76 bm-b\n'
           '    # (burn in flight) + W77 bm-a (burn in flight) = TWO\n'
           '    # in-flight upstream seats at this freeze (finalize\n'
           '    # chain-pending FAIL-CLOSED r307).\n'
           '    # ADMIT receipt results/_r363bmc_w78_band_gate.py;\n'
           '    # NOT a re-pick (R250: W78 bands were never assigned).\n'
           '    78: {"a": (199_004, 201_003), "b_exit": (53_201, 53_400),\n'
           '         "engine_owner": "bm-c"},\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[78] landed (anchor=W77 row, insert after)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[78] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '78: {"batch": "PERPETUAL-N1-W78"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w77", "out_name": "n1_w77_results.json",\n'
          '                            "engine_owner": "bm-a"},\n')
    NEW2 = A2 + (
        '                       78: {"batch": "PERPETUAL-N1-W78",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W78_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; SIXTY-SEVENTH ENGINE-OWNED WAVE, "\n'
        '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
        '                                       "(first-free-number law over the registered W77 row; "\n'
        '                                       "r565 second yield-then-reoccupy this window: W76 "\n'
        '                                       "yielded to bm-b r572 24ec53190, W77 yielded to "\n'
        '                                       "bm-a r572 034c81887 per r511 commit-order, both "\n'
        '                                       "bitwise cross-validations; seat published=reserved "\n'
        '                                       "MSG-20261002-1150-bmc pushed to origin BEFORE this "\n'
        '                                       "freeze, its B prose projection corrected by "\n'
        '                                       "MSG-20261002-1155-bmc: j13v2_mill_ic2=53_100 inside "\n'
        '                                       "the stale 53_001..53_200 window, r535 machine-"\n'
        '                                       "derive law); bands: A 199_004..201_003 arithmetic "\n'
        '                                       "continuation zero skip + B 53_201..53_400 chained "\n'
        '                                       "double-hit skip past j13v2_mill_ic1=53_000 + "\n'
        '                                       "j13v2_mill_ic2=53_100 (W63-B in-register family, "\n'
        '                                       "fork 53_101..53_300 disclosed not taken, r566 "\n'
        '                                       "face); TWO in-flight upstream seats W76 bm-b + "\n'
        '                                       "W77 bm-a -- FAIL-CLOSED r307), "\n'
        '                                       "engine_owner=bm-c; W1..W75 finalizes ALL LANDED at "\n'
        '                                       "this freeze (net chain head 529,548, K=162,920, "\n'
        '                                       "bm-a r572)"),\n'
        '                            "a_seed_base": 199_004,        # law sec.4 W78 A: 199_004..201_003 (arithmetic continuation)\n'
        '                            "b_exit_seed_base": 53_201,   # law sec.4 W78 B: 53_201..53_400 (chained double-hit skip, W63 family)\n'
        '                            "shard_subdir": "n1_w78", "out_name": "n1_w78_results.json",\n'
        '                            "engine_owner": "bm-c"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[78] landed (anchor=W77 entry tail, insert after)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W78 leg --------------
LEG78 = '''
    # --- W78 materializer face (r363 bm-c freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-c's
    #     twenty-fourth owned per machine-derive (engine_owner==bm-c
    #     rows 23 + candidate); wave 78 = first free number after the
    #     registered W77 row. r565 SECOND yield-then-reoccupy this
    #     window: W76 draft yielded to bm-b r572 (bitwise
    #     cross-validation #11; 12/12 local twin shards discarded
    #     pre-push, zero pollution) + W77 draft yielded to bm-a r572
    #     (bitwise cross-validation #12; FIX-A intercepted the freeze
    #     run pre-edit = zero edit zero burn). Seat published=reserved
    #     MSG-20261002-1150-bmc pushed to origin BEFORE this freeze;
    #     its B prose projection 53_001..53_200 was STALE vs the live
    #     registry (j13v2_mill_ic2=53_100 inside it) -- corrected per
    #     the machine gate to the chained double-hit window
    #     53_201..53_400 (W63-B in-register family; fork 53_101..53_300
    #     disclosed not taken, r566 face; correction receipt
    #     MSG-20261002-1155-bmc, r535 machine-derive law). TWO
    #     in-flight upstream seats at this freeze: W76 bm-b (burn in
    #     flight) + W77 bm-a (burn in flight) (finalize chain-pending
    #     FAIL-CLOSED r307 at run time). ADMIT receipt
    #     results/_r363bmc_w78_band_gate.py; not a re-pick -- R250:
    #     W78 bands were never assigned --
    _set_wave(78)
    try:
        assert WAVE_CONFIGS[78]["a_seed_base"] == pf.N1_BANDS[78]["a"][0], \\
            "W78 A band drift vs law mirror"
        assert WAVE_CONFIGS[78]["b_exit_seed_base"] == \\
            pf.N1_BANDS[78]["b_exit"][0], "W78 B band drift vs law mirror"
        assert WAVE_CONFIGS[78].get("engine_owner") == \\
            pf.N1_BANDS[78].get("engine_owner") == "bm-c", \\
            "W78 engine_owner drift (law mirror parity)"
        w78_a = {A_SEED_BASE + j for j in range(A_N)}
        w78_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w78_a & w78_b), "W78 A/B band overlap"
        assert not (w78_a & reg_ints) and not (w78_b & reg_ints), \\
            "W78 hits SEED_REGISTRY"
        for nm, band in (("A", w78_a), ("B", w78_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W78 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W78 {nm} hits W1"
            assert not (band & probes), f"W78 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W71..W77 are
        # REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly (W76 == bm-b r572; W77 == bm-a r572).
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
            "registered W76 row parity drift (r307 two-state; bm-b r572 " \\
            "landed bitwise == this machine's yielded W76 draft)"
        assert pf.N1_BANDS[77] == {"a": (197_004, 199_003),
                                   "b_exit": (52_601, 52_800),
                                   "engine_owner": "bm-a"}, \\
            "registered W77 row parity drift (r307 two-state; bm-a r572 " \\
            "landed bitwise == this machine's yielded W77 draft)"
        # prior-wave disjointness incl. W48..W77 (all registered; the
        # W77 row is the direct arithmetic upstream of W78's A band).
        for wprev in REG_WAVES_ALL:
            assert not (w78_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W78 A hits W{wprev}"
            assert not (w78_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W78 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W78 clears it.
        n3r1_used78 = set(range(70_000, 70_006))
        assert not (w78_a & n3r1_used78) and not (w78_b & n3r1_used78), \\
            "W78 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w78_a & lfc_actual12) and not (w78_b & lfc_actual12), \\
            "W78 bands must clear the lfc actual draw range"
        assert not (w78_a & options_actual12) and \\
            not (w78_b & options_actual12), \\
            "W78 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W78 row, r363): A = ARITHMETIC
        # CONTINUATION from the registered W77 tail (zero skip);
        # B = CHAINED DOUBLE-HIT SKIP (W63-B in-register family):
        # arithmetic window 52_801..53_000 refused at edge point
        # j13v2_mill_ic1=53_000; chained window 53_001..53_200 refused
        # at mid point j13v2_mill_ic2=53_100; chained first clean =
        # 53_201..53_400. Refusal facts identity machine-proven
        # (r494 law); fork 53_101..53_300 disclosed not taken (r566
        # face, F-20261002-03 pin pending).
        assert WAVE_CONFIGS[78]["a_seed_base"] == 199_004 == \\
            pf.N1_BANDS[77]["a"][1] + 1, \\
            "W78 A must start at the registered W77 A end + 1 " \\
            "(arithmetic continuation window 199_004..201_003 CLEAN)"
        assert WAVE_CONFIGS[78]["b_exit_seed_base"] == 53_201, \\
            "W78 B must start at the chained double-hit first clean " \\
            "window 53_201..53_400 (52_801..53_000 + 53_001..53_200 " \\
            "both refused, W63 family)"
        assert 53_000 in reg_ints and 53_100 in reg_ints, \\
            "W78 B skip must be forced (both refusal points must live " \\
            "in SEED_REGISTRY: j13v2_mill_ic1=53_000, j13v2_mill_ic2=53_100)"
        arith_b78 = set(range(52_801, 53_001))
        chained_b78 = set(range(53_001, 53_201))
        assert (arith_b78 & reg_ints) and (chained_b78 & reg_ints), \\
            "W78 B skip must be forced (arithmetic window AND chained " \\
            "window must each hit a registry point)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W78-SHARD-0",
                                          "n1w78-0of12"), "W78 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W78-SHARD-11",
                                          "n1w78-11of12")
        assert SHARD_DIR.endswith("n1_w78") and OUT.endswith(
            "n1_w78_results.json"), "W78 path drift"
        for wprev in REG_WAVES_ALL:
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W78 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W78_PREREG.md")), \\
            "W78 per-wave prereg missing (materializer requirement)"
        # W78 finalize cumulative deps: W17..W75 outputs ALL PRESENT
        # (static landed seats; chain head 529,548 = W75 bm-a r572
        # K=162,920; W76 bm-b + W77 bm-a = TWO in-flight upstream
        # seats -- the finalize merge loop derives the wave set from
        # registry keys at run time and stays FAIL-CLOSED on the
        # not-yet-finalized seats, r307 two-state law).
        for _depw in range(17, 76):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W78 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law):
        # prior-wave set derives from registry keys below 78 (no 15,
        # incl. 48..77 -- all registered, W76/W77 in-flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 78) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 78)], \\
            "W78 prior-wave set must derive from registry keys (no 15; " \\
            "incl. 48..77 -- W76/W77 registered before this freeze landed)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W78 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    REG_WAVES_ALL = '[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 78)]'
    LEG78 = LEG78.replace('REG_WAVES_ALL', REG_WAVES_ALL)
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG78.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W78 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 5th face) ------
t2c, eol2c = load(FP2)
if '+ W78 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('probe-seed cluster leg, law sec.4 W77 row, r572 "\n'
          '          "bm-a] "\n'
          '          "+ T-141 s2 ')
    SEG78 = ('probe-seed cluster leg, law sec.4 W77 row, r572 "\n'
             '          "bm-a] "\n'
             '          "+ W78 materializer face [same guard set, dep=W17..W75 "\n'
             '          "outputs ALL PRESENT (landed chain head 529,548, "\n'
             '          "K=162,920, bm-a r572), W76 bm-b + W77 bm-a = TWO "\n'
             '          "in-flight upstream seats (FAIL-CLOSED r307 at run "\n'
             '          "time), SIXTY-SEVENTH ENGINE-OWNED WAVE bm-c\'s "\n'
             '          "twenty-fourth owned claim per machine-derive "\n'
             '          "(engine_owner==bm-c rows 23 + candidate), "\n'
             '          "engine_owner=bm-c per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series "\n'
             '          "(wave 78 = first FREE number after the registered "\n'
             '          "W77 row; r565 SECOND yield-then-reoccupy this "\n'
             '          "window after the W76 yield to bm-b r572 and the "\n'
             '          "W77 yield to bm-a r572 per r511 commit-order, "\n'
             '          "both bitwise cross-validations; seat published="\n'
             '          "reserved MSG-20261002-1150-bmc pushed to origin "\n'
             '          "BEFORE this freeze, its B prose projection "\n'
             '          "53_001..53_200 corrected per the live-registry "\n'
             '          "machine gate to the chained double-hit window "\n'
             '          "53_201..53_400 (j13v2_mill_ic2=53_100 inside the "\n'
             '          "stale window, r535 machine-derive law; W63-B "\n'
             '          "in-register family; fork 53_101..53_300 "\n'
             '          "disclosed not taken, r566 face; correction "\n'
             '          "receipt MSG-20261002-1155-bmc; ADMIT receipt "\n'
             '          "results/_r363bmc_w78_band_gate.py; not a "\n'
             '          "free pick -- R250), N3-R1 used-seed leg, "\n'
             '          "probe-seed cluster leg, law sec.4 W78 row, "\n'
             '          "r363 bm-c] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG78, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W78 segment landed (insert after W77 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W78 row -------------------
ROW78 = """
- N1 波78（r363 bm-c 冻·prereg 时展行）：**第六十七枚引擎波·bm-c 第二十四枚自有波〔机面 derive：engine_owner==bm-c 行 23+本候选〕**·engine_owner=bm-c·SATURATION_ENGINE_LAW §1/§2 同 W10-W77 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-c 实例=常驻架构 v0.4 per-tick 重读（D-20261002-03 修法·W59/W60/W61/W66/W69/W71 同窗实证——冻结 commit 后常驻实例下一 tick 重读活树自见新行自燃=免杀重启免做·点火验证唯一证据=2 tick 内产物增长面 r325 律·state queue 面不信）】·【never-dry 供给律常设步·**波号 78=注册表 W77 行后首个自由号**·**r565 让路-同窗再占位律第二次执行**——本窗连环让路两枚：W76 号位本机先起草（gate ADMIT=results/_r363bmc_w76_band_gate.py·候选 **A 195_004..197_003／B 52_401..52_600**·席位公示 MSG-1145 本地未推=对侧不可见如实披露）→bm-b r572 同窗先落（24ec53190）=正主→**12/12 孪生分片（引擎 r359 自燃律已烧·audit.machine=bm-c 验属）随 reset 弃置·finalize 从未跑·账本零触碰=r530 族第 11 例逐位同交叉验证+零污染让路**；W77 再占位起草（gate ADMIT=results/_r363bmc_w77_band_gate.py·候选 **A 197_004..199_003／B 52_601..52_800**）→bm-a r572 同窗先落（034c81887·席位 MSG-1131-bma）=正主→**FIX-A 编辑前 origin-blob 断言当场拦截=零编辑零烧录=r530 族第 12 例逐位同交叉验证+纯草稿零成本让路**·**席位公示=MSG-20261002-1150-bmc（published=reserved r518-① 律·本轮已先推 origin 后冻结=r565 早可见性教训执行）**·r511 表尾锁例冻结前 fetch 实核表尾时 W78 号位净空·origin 侧 vacancy 机验】·**带位（r535 机闸 derive 律·活注册表机证）**：**A-ext seed=199_004..201_003**（**A 面算术续带零跳位**==W77 A 尾 199_003+1·步长逐字·CLEAN==W77 行 W78+ 投影 A 侧逐字）；**B-ext exit seed=53_201..53_400**（**双点链跳位族 W63-B 在册先例**：算术续带 52_801..53_000 撞 SEED_REGISTRY **j13v2_mill_ic1=53_000** 带上边缘端点→连锁窗 53_001..53_200 撞 **j13v2_mill_ic2=53_100**（bm-b J13V2 IC2 claim ac8a58490 注册·**W77 行 W78+ prose 投影「首净窗 53_001..53_200」相对活注册表过期=本机带闸 leg1-B2 refusal facts 恒等机证当场抓出**——r535 律实证：净空宣称必须机证 derive 非 prose 转抄·修正回执=MSG-20261002-1155-bmc·席位 MSG-1150 B 面投影同步如实修正）→链跳首净窗 **53_201..53_400**·**分叉面如实披露**：越 hit 起窗读法 53_101..53_300 亦机证净空、不采〔W63 双点链族 vs W68 单点越 hit 族——法典 §4 跳位语义钉死行待 HQ-FEEDBACK F-20261002-03·裁定前=冻结方机闸 derive+分叉披露强制〕·跳位被迫非自由挑·R250：W78 带从未指派·测量面零结果可钓）·【机证净空——leg0 七十六键（75 注册行+候选）+leg0b W77 行 W78+ 投影 prose 软校验+leg1-A 算术位 CLEAN 机证+leg1-B 算术位 REFUSED 恒等 refusal facts=[53_000] 机证+leg1-B2 连锁窗 REFUSED 恒等 refusal facts=[53_100] 机证+leg2 A 侧首净窗==算术位／B 侧链跳首净窗==候选+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验·**MSG-0640 三修工具**（FIX-A 编辑前 origin-blob 等值断言+FIX-B 锚=最后注册行 W77+行存活核查+FIX-C 推送前纯增量 diff 断言）〕·ADMIT 回执=results/_r363bmc_w78_band_gate.py·r363 bm-c 起草窗实跑】·扫描面=pre-W78 七十五行 N1 带表【含 **W73 行 189_004..191_003/51_601..51_800〔bm-a r570·finalize 已落账 K=158,520〕**·**W74 行 191_004..193_003/52_001..52_200〔bm-b r571·finalize 已落账 K=160,720〕**·**W75 行 193_004..195_003/52_201..52_400〔bm-a r571·finalize 已落账 K=162,920·净链头 529,548·bm-a r572 本窗〕**·**W76 行 195_004..197_003/52_401..52_600〔bm-b r572·烧录在飞〕**·**W77 行 197_004..199_003/52_601..52_800〔bm-a r572·烧录在飞〕**】·**两在飞上游席披露：W76 bm-b（烧录在飞）+W77 bm-a（烧录在飞）→本波 finalize 链序前置=W76+W77 双落账·FAIL-CLOSED r307 两态律**·带域不相交·W1 ext·v1 在用带·SEED_REGISTRY 全键（160 int 值·LOWAMP-P1/P2/P3 键 20.33M 域零交集）·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行②强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·lfc 实际流 30_000..30_099·options_wave2 实际流 63_000..63_049（leg-3e 实际流避让腿）·**W79+ 投影（gate 投影腿机证=results/_r363bmc_w78_band_gate.py 尾投影·W79 prereg 窗机闸复核 r335 律）：A 201_004..203_003 CLEAN／B 53_401..53_600 CLEAN（两侧均照例以届时带闸 derive 为准）**·prereg=PERPETUAL_N1_W78_PREREG.md 冻结〔S5 锚=W75 实测（锚滚动律自 W74 滚至 W75）：merged mu −0.092271/W75-only mu −0.104350/sigma 0.245868/A-p95 0.3088/K-lift −0.0001·累计池投影 171,520（含 W76+W77 在飞 4,400）〕·burn 由本机常驻引擎 v0.4 per-tick 自燃·finalize=活链头 derive one-pass（r538 一过律·链序前置=W76+W77 双落账）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce278\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW78.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W78 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    78: {"a": (199_004') == 1, 'FIX-B FAIL: W78 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W78"') == 1, 'FIX-B FAIL: W78 config not exactly once'
for w in range(58, 78):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W78 materializer face') == 2, \
    'FIX-B FAIL: W78 leg+summary must be exactly 2'
for w in range(48, 78):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce278\uff08') == 1, 'FIX-B FAIL: canon W78 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W78 added per face')

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
