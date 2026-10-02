# -*- coding: utf-8 -*-
"""r570 bm-b W72 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r566 lineage).

FIX-A (origin-blob freshness): every tracked edit target must be content-equal
  to origin/main BEFORE any edit runs. Kills the r559 stale-base clobber.
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W71, bm-c's),
  and after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W72 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W72 = SIXTY-FIRST engine wave, bm-b's TWENTY-THIRD owned per machine-derive
(engine_owner==bm-b rows 22 + candidate). Seat declared published=reserved
(MSG-20261002-1028-bmb, r518-1 law; never-dry standing step under CEO
de-throttle order O-20261001-2355 sec.2 own-continuous-series; wave 72 =
first free number after the registered W71 row, r511 tail-lock, origin
vacancy machine-checked). NOTE: bm-a r569 published a W71 seat that was
same-window taken by bm-c r361 (seat publication = de-confliction
mechanism, NOT an adjudication mechanism -- r566 law, 2nd live proof);
this wave derives from the REGISTERED W71 tail only.
BOTH SIDES = plain ARITHMETIC CONTINUATION from the registered W71 tail,
zero skip, no fork face this wave: A 187_004..189_003 / B 51_401..51_600.
W68 finalize LANDED (bm-a r569, net chain head 514,148, K=147,520); W69
bm-c (12/12 burned, finalize pending) + W70 bm-b (12/12 burned, finalize
pending, chain-ordered after W69) + W71 bm-c (burn in flight) = THREE
in-flight upstream seats at this freeze (FAIL-CLOSED r307).
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
             69, 70, 71]
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face')
       for w in (59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in (48, 49, 50, 51, 52, 53, 54, 55, 56,
                                                    57, 58, 59, 60, 61, 62, 63, 64, 65, 66,
                                                    67, 68, 69, 70, 71)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[72] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '72: {"a": (187_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    71: {"a": (185_004, 187_003), "b_exit": (51_201, 51_400),\n'
          '         "engine_owner": "bm-c"},\n'
          '}\n')
    NEW = ('    71: {"a": (185_004, 187_003), "b_exit": (51_201, 51_400),\n'
           '         "engine_owner": "bm-c"},\n'
           '    # SIXTY-FIRST ENGINE-OWNED WAVE (r570 bm-b freeze): bm-b\'s\n'
           '    # TWENTY-THIRD owned per machine-derive (engine_owner==bm-b\n'
           '    # rows 22 + candidate). Wave 72 = next free number after the\n'
           '    # registered W71 row (seat declared published=reserved\n'
           '    # MSG-20261002-1028-bmb, r518-1 law; never-dry standing step\n'
           '    # under CEO de-throttle order O-20261001-2355 sec.2).\n'
           '    # W1..W68 finalizes ALL LANDED (net head 514,148, K=147,520,\n'
           '    # bm-a r569); W69 bm-c (12/12 burned, finalize pending) +\n'
           '    # W70 bm-b (12/12 burned, finalize pending) + W71 bm-c\n'
           '    # (burn in flight) = THREE in-flight upstream seats at this\n'
           '    # freeze (FAIL-CLOSED r307).\n'
           '    # BOTH SIDES: ARITHMETIC CONTINUATION from the W71 row tail,\n'
           '    # no skip, no fork face: A 187_004..189_003 (= W71 A end\n'
           '    # 187_003 + 1) / B 51_401..51_600 (= W71 B end 51_400 + 1)\n'
           '    # -- both CLEAN per the W71 row W72+ WARNING projection\n'
           '    # (bm-c r361 gate projection leg + this freeze\'s machine\n'
           '    # re-derive, r302/r535 law).\n'
           '    # Machine-verified at prereg time\n'
           '    # (results/_r570bmb_w72_band_gate.py ADMIT receipt vs the\n'
           '    # 69-row pre-W72 table + live SEED_REGISTRY values + probe\n'
           '    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin\n'
           '    # slot vacancy machine-checked). NOT a re-pick (R250: W72\n'
           '    # bands were never assigned).\n'
           '    72: {"a": (187_004, 189_003), "b_exit": (51_401, 51_600),\n'
           '         "engine_owner": "bm-b"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[72] landed (anchor=W71 row, insert)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[72] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '72: {"batch": "PERPETUAL-N1-W72"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('"shard_subdir": "n1_w71", "out_name": "n1_w71_results.json",\n'
          '                            "engine_owner": "bm-c"},\n'
          '                       }')
    NEW2 = ('"shard_subdir": "n1_w71", "out_name": "n1_w71_results.json",\n'
            '                            "engine_owner": "bm-c"},\n'
            '                       72: {"batch": "PERPETUAL-N1-W72",\n'
            '                            "prereg": ("research/PERPETUAL_N1_W72_PREREG.md (wave-level frozen "\n'
            '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
            '                                       "new seed bands only; SIXTY-FIRST ENGINE-OWNED WAVE, "\n'
            '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
            '                                       "(first-free-number law over the registered W71 row; "\n'
            '                                       "seat declared published=reserved MSG-20261002-1028-bmb), "\n'
            '                                       "engine_owner=bm-b, wave 72 BOTH SIDES ARITHMETIC "\n'
            '                                       "CONTINUATION no skip no fork (A 187_004..189_003 / "\n'
            '                                       "B 51_401..51_600 both CLEAN == the W71 row W72+ "\n'
            '                                       "WARNING projection verbatim, machine re-derived "\n'
            '                                       "per r302/r535 law); W1..W68 finalizes ALL LANDED at "\n'
            '                                       "this freeze (net chain head 514,148, K=147,520, "\n'
            '                                       "bm-a r569), W69 bm-c + W70 bm-b + W71 bm-c = THREE "\n'
            '                                       "in-flight upstream seats "\n'
            '                                       "(finalize chain-pending FAIL-CLOSED r307)"),\n'
            '                            "a_seed_base": 187_004,        # law sec.4 W72 A: 187_004..189_003 (arithmetic continuation)\n'
            '                            "b_exit_seed_base": 51_401,   # law sec.4 W72 B: 51_401..51_600 (arithmetic continuation)\n'
            '                            "shard_subdir": "n1_w72", "out_name": "n1_w72_results.json",\n'
            '                            "engine_owner": "bm-b"},\n'
            '                       }')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[72] landed (anchor=W71 entry tail, insert)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W72 leg --------------
LEG72 = '''
    # --- W72 materializer face (r570 bm-b freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2):
    #     bm-b's TWENTY-THIRD owned per machine-derive (engine_owner==bm-b
    #     rows 22 + candidate); wave 72 = first free number after the
    #     registered W71 row (seat declared published=reserved
    #     MSG-20261002-1028-bmb; never-dry standing step).
    #     W1..W68 finalizes ALL LANDED (net chain head 514,148, K=147,520,
    #     bm-a r569); W69 bm-c (12/12 burned, finalize pending) + W70 bm-b
    #     (12/12 burned, finalize pending) + W71 bm-c (burn in flight)
    #     = THREE in-flight upstream seats at this freeze (FAIL-CLOSED
    #     r307). BOTH SIDES ARITHMETIC CONTINUATION from the W71 tail
    #     no skip no fork (A 187_004..189_003 / B 51_401..51_600 both
    #     CLEAN; == the W71 row W72+ WARNING projection verbatim,
    #     machine re-derived per r302/r535; ADMIT receipt
    #     results/_r570bmb_w72_band_gate.py; not a re-pick -- R250) --
    _set_wave(72)
    try:
        assert WAVE_CONFIGS[72]["a_seed_base"] == pf.N1_BANDS[72]["a"][0], \\
            "W72 A band drift vs law mirror"
        assert WAVE_CONFIGS[72]["b_exit_seed_base"] == \\
            pf.N1_BANDS[72]["b_exit"][0], "W72 B band drift vs law mirror"
        assert WAVE_CONFIGS[72].get("engine_owner") == \\
            pf.N1_BANDS[72].get("engine_owner") == "bm-b", \\
            "W72 engine_owner drift (law mirror parity)"
        w72_a = {A_SEED_BASE + j for j in range(A_N)}
        w72_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w72_a & w72_b), "W72 A/B band overlap"
        assert not (w72_a & reg_ints) and not (w72_b & reg_ints), \\
            "W72 hits SEED_REGISTRY"
        for nm, band in (("A", w72_a), ("B", w72_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W72 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W72 {nm} hits W1"
            assert not (band & probes), f"W72 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W64..W71
        # are REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly.
        assert pf.N1_BANDS[64] == {"a": (171_004, 173_003),
                                   "b_exit": (49_401, 49_600),
                                   "engine_owner": "bm-a"}, \\
            "registered W64 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[65] == {"a": (173_004, 175_003),
                                   "b_exit": (49_601, 49_800),
                                   "engine_owner": "bm-b"}, \\
            "registered W65 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[66] == {"a": (175_004, 177_003),
                                   "b_exit": (50_001, 50_200),
                                   "engine_owner": "bm-c"}, \\
            "registered W66 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[67] == {"a": (177_004, 179_003),
                                   "b_exit": (50_201, 50_400),
                                   "engine_owner": "bm-b"}, \\
            "registered W67 row parity drift (r307 two-state)"
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
        # prior-wave disjointness incl. W48..W71 (all registered; W69/W70/
        # W71 in flight -- coexist by band disjointness per r531).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                      70, 71):
            assert not (w72_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W72 A hits W{wprev}"
            assert not (w72_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W72 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W72 clears it.
        n3r1_used72 = set(range(70_000, 70_006))
        assert not (w72_a & n3r1_used72) and not (w72_b & n3r1_used72), \\
            "W72 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w72_a & lfc_actual12) and not (w72_b & lfc_actual12), \\
            "W72 bands must clear the lfc actual draw range"
        assert not (w72_a & options_actual12) and \\
            not (w72_b & options_actual12), \\
            "W72 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W72 row, r570): BOTH SIDES ARITHMETIC
        # CONTINUATION from the registered W71 tail -- no skip family
        # this wave (both windows CLEAN per the ADMIT receipt).
        assert WAVE_CONFIGS[72]["a_seed_base"] == 187_004 == 187_003 + 1, \\
            "W72 A must start at the registered W71 A end + 1 " \\
            "(arithmetic continuation window 187_004..189_003 CLEAN)"
        assert WAVE_CONFIGS[72]["b_exit_seed_base"] == 51_401 == 51_400 + 1, \\
            "W72 B must start at the registered W71 B end + 1 " \\
            "(arithmetic continuation window 51_401..51_600 CLEAN)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W72-SHARD-0",
                                          "n1w72-0of12"), "W72 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W72-SHARD-11",
                                          "n1w72-11of12")
        assert SHARD_DIR.endswith("n1_w72") and OUT.endswith(
            "n1_w72_results.json"), "W72 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                      70, 71):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W72 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W72_PREREG.md")), \\
            "W72 per-wave prereg missing (materializer requirement)"
        # W72 finalize cumulative deps: W17..W68 outputs ALL PRESENT
        # (static landed seats; chain head 514,148 = W68 bm-a r569
        # K=147,520; W69 bm-c + W70 bm-b + W71 bm-c = THREE in-flight
        # upstream seats -- the finalize merge loop derives the wave set
        # from registry keys at run time and stays FAIL-CLOSED on the
        # not-yet-finalized seats, r307 two-state law).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                      43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
                      56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W72 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 72 (no 15; incl.
        # 48..71 -- all registered, W69/W70/W71 finalize in flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 72) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
             65, 66, 67, 68, 69, 70, 71], \\
            "W72 prior-wave set must derive from registry keys (no 15, " \\
            "incl. 48..71)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W72 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG72.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W72 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 5th face) ------
t2c, eol2c = load(FP2)
if '+ W72 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('law sec.4 W71 row, r361 bm-c] "\n'
          '          "+ T-141 s2 ')
    SEG72 = ('law sec.4 W71 row, r361 bm-c] "\n'
             '          "+ W72 materializer face [same guard set, dep=W17..W68 "\n'
             '          "outputs ALL PRESENT (landed chain head 514,148, K=147,520, "\n'
             '          "bm-a r569), W69 bm-c + W70 bm-b + W71 bm-c = THREE in-flight "\n'
             '          "upstream seats (FAIL-CLOSED r307 at run time), SIXTY-FIRST "\n'
             '          "ENGINE-OWNED WAVE bm-b\'s TWENTY-THIRD owned claim per "\n'
             '          "machine-derive (engine_owner==bm-b rows 22 + candidate), "\n'
             '          "engine_owner=bm-b per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series (wave 72 = "\n'
             '          "first FREE number after the registered W71 row; seat "\n'
             '          "declared published=reserved MSG-20261002-1028-bmb), BOTH "\n'
             '          "SIDES ARITHMETIC CONTINUATION from the W71 tail no skip no "\n'
             '          "fork (A 187_004..189_003 / B 51_401..51_600 both CLEAN == "\n'
             '          "the W71 row W72+ WARNING projection verbatim, machine "\n'
             '          "re-derived per r302/r535; ADMIT receipt "\n'
             '          "results/_r570bmb_w72_band_gate.py; not a "\n'
             '          "free pick -- R250), N3-R1 used-seed leg, probe-seed "\n'
             '          "cluster leg, law sec.4 W72 row, r570 bm-b] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG72, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W72 segment landed (insert after W71 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W72 row -------------------
ROW72 = """
- N1 波72（r570 bm-b 冻·prereg 时展行）：**第六十一枚引擎波·bm-b 第二十三枚自有波〔机面 derive：engine_owner==bm-b 行 22+本候选〕**·engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W71 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-b 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启免做·W55/W56/W59/W61/W65/W67/W70 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 72=注册表 W71 行后首个自由号**·席位公示=MSG-20261002-1028-bmb（published=reserved r518-① 律·W48/W49/W55/W62/W65/W67/W68/W69/W70/W71 先例·**bm-a r569 之 W71 席位公示已被 bm-c r361 同窗占位消费=席位公示为错峰机制非裁决机制 r566 律实证第 2 例如实注记**）·r511 表尾锁例冻结前 fetch 实核表尾时 W72 号位净空·origin 侧 vacancy 机验】·**带位=双面算术续带零跳位（零分叉面）**：W71 行携带 W72+ 警示投影 **A 187_004..189_003 CLEAN／B 51_401..51_600 CLEAN**（bm-c r361 gate 投影腿机证）→本波 **r570 bm-b gate 机闸独立 derive 双面 CLEAN 复核逐字同**（r302 陈旧指针证伪律下非 prose 转抄——机闸 derive 为唯一 derive 面·prose 交叉核对）→本波 **A-ext seed=187_004..189_003**（**A 面算术续带**==W71 A 尾 187_003+1·步长逐字·零跳位）；**B-ext exit seed=51_401..51_600**（**B 面算术续带**==W71 B 尾 51_400+1·步长逐字·零跳位·双侧零跳位·R250：W72 带从未指派·测量面零结果可钓）。【机证净空——leg0 七十键（69 注册行+候选）+leg0b W71 行 W72+ 警示 prose 在场校验+leg1-A/leg1-B 算术位双 CLEAN 机证+leg2 双侧首净窗==候选逐位+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验·**MSG-0640 三修工具**（FIX-A 编辑前 origin-blob 等值断言+FIX-B 锚=最后注册行+行存活核查+FIX-C 推送前纯增量 diff 断言）〕·ADMIT 回执=results/_r570bmb_w72_band_gate.py·r570 bm-b 起草窗实跑·非重挑 R250。扫描面=pre-W72 六十九行 N1 带表【含 **W65 行 173_004..175_003/49_601..49_800〔bm-b r566·finalize 已落账 K=140,920·链头 507,548〕**·**W66 行 175_004..177_003/50_001..50_200〔bm-c r359·finalize 已落账 K=143,120·链头 509,748〕**·**W67 行 177_004..179_003/50_201..50_400〔bm-b r567 冻/r568 收口·finalize 已落账 K=145,320·链头 511,948〕**·**W68 行 179_004..181_003/50_501..50_700〔bm-a r568 冻·r569 presence 重烧·finalize 已落账 K=147,520·净账本链头 514,148·bm-a r569 本窗〕**·**W69 行 181_004..183_003/50_701..50_900〔bm-c r360 冻·12/12 烧毕·finalize 未落账〕**·**W70 行 183_004..185_003/51_001..51_200〔bm-b r568 冻·12/12 烧毕·finalize 未落账（链序等 W69 先行）〕**·**W71 行 185_004..187_003/51_201..51_400〔bm-c r361 冻·注册烧录在飞·finalize 未落账〕**】·**三在飞上游席披露：本波 finalize 链序前置=W69+W70+W71 三落账·FAIL-CLOSED r307 两态律**·带域不相交·W1 ext·v1 在用带·SEED_REGISTRY 全键（int 值全清·LOWAMP-P1/P2/P3 键 20.33M 域零交集）·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·lfc 实际流 30_000..30_099·options_wave2 实际流 63_000..63_049（leg-3e 实际流避让腿）·**W73+ 投影（带闸投影腿机证·W73 prereg 照例带闸复核 r335 律）：A 189_004..191_003／B 51_601..51_800 双 CLEAN**（命中面=W73 冻结窗机闸 derive 定谳·本波 gate 投影腿机证零命中）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce272\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW72.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W72 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    72: {"a": (187_004') == 1, 'FIX-B FAIL: W72 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W72"') == 1, 'FIX-B FAIL: W72 config not exactly once'
for w in (59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71):
    assert n11.count(f'W{w} materializer face') == 2, f'FIX-B FAIL: W{w} leg lost'
assert n11.count('W72 materializer face') == 2, \
    'FIX-B FAIL: W72 leg+summary must be exactly 2'
for w in (48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
          65, 66, 67, 68, 69, 70, 71):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce272\uff08') == 1, 'FIX-B FAIL: canon W72 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W72 added per face')

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
