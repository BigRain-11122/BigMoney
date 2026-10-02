# -*- coding: utf-8 -*-
"""r361 bm-c W71 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r566 lineage).

FIX-A (origin-blob freshness): every tracked edit target must be content-equal
  to origin/main BEFORE any edit runs. Kills the r559 stale-base clobber.
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W70, bm-b's),
  and after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W71 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W71 = SIXTIETH engine wave, bm-c's TWENTY-THIRD owned per machine-derive
(engine_owner==bm-c rows 22 + candidate). Seat published=reserved
(MSG-20261002-1017-bmc, r518-1 law; never-dry standing step under CEO
de-throttle order O-20261001-2355 sec.2 own-continuous-series; wave 71 =
first free number after the registered W70 row, r511 tail-lock, origin
vacancy machine-checked).
BOTH SIDES ARITHMETIC CONTINUATION from the registered W70 tail, no skip:
A 185_004..187_003 (= W70 A end 185_003 + 1) / B 51_201..51_400 (= W70 B
end 51_200 + 1) -- both windows CLEAN per THIS gate's machine derive
(r535 law; the W70 canon row carries no W71+ WARNING prose -- bm-b r568
omitted the tail; their commit message + gate receipt carried the
projection, cross-checked here).
W1..W67 finalizes ALL LANDED (net chain head 511,948, K=145,320, bm-b
r568); W68 bm-a (12/12 burned, finalize pending) + W69 bm-c (12/12
burned, finalize pending) + W70 bm-b (burn in flight) = THREE in-flight
upstream seats at this freeze (FAIL-CLOSED r307).
"""
import subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NO_WIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)

def git(*a):
    r = subprocess.run(['git', '-C', REPO] + list(a), capture_output=True,
                       creationflags=NO_WIN)
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
                       capture_output=True, creationflags=NO_WIN)
    out = r.stdout.decode('utf-8', 'replace').strip()
    if r.returncode != 0:
        sys.exit(f'FIX-A git fail on {p}')
    for line in out.splitlines():
        add, dele, path = line.split('\t')
        if int(dele) > 0:
            sys.exit(f'STALE BASE (FIX-A abort): {p} shows {dele} deleted lines vs '
                     f'origin/main -- checkout origin version first '
                     f'(r559 clobber cure / same-window seat collision)')
print('FIX-A: all 3 tracked edit targets show zero deletions vs origin/main (fresh base)')

# ---------------- survival signature baseline (FIX-B) ------------------------
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20,
             21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
             37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52,
             53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68,
             69, 70]
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face')
       for w in (59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in (48, 49, 50, 51, 52, 53, 54, 55, 56,
                                                    57, 58, 59, 60, 61, 62, 63, 64, 65, 66,
                                                    67, 68, 69, 70)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[71] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '71: {"a": (185_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    70: {"a": (183_004, 185_003), "b_exit": (51_001, 51_200),\n'
          '         "engine_owner": "bm-b"},\n'
          '}\n')
    NEW = ('    70: {"a": (183_004, 185_003), "b_exit": (51_001, 51_200),\n'
           '         "engine_owner": "bm-b"},\n'
           '    # SIXTIETH ENGINE-OWNED WAVE (r361 bm-c freeze): bm-c\'s\n'
           '    # TWENTY-THIRD owned per machine-derive (engine_owner==bm-c\n'
           '    # rows 22 + candidate). Wave 71 = first free number after the\n'
           '    # registered W70 row (seat published=reserved\n'
           '    # MSG-20261002-1017-bmc, r518-1 law; never-dry standing step\n'
           '    # under CEO de-throttle order O-20261001-2355 sec.2).\n'
           '    # W1..W67 finalizes ALL LANDED (net head 511,948, K=145,320,\n'
           '    # bm-b r568); W68 bm-a (12/12 burned, finalize pending) +\n'
           '    # W69 bm-c (12/12 burned, finalize pending) + W70 bm-b (burn\n'
           '    # in flight) = THREE in-flight upstream seats at this\n'
           '    # freeze (FAIL-CLOSED r307).\n'
           '    # BOTH SIDES ARITHMETIC CONTINUATION from the W70 row tail,\n'
           '    # no skip: A 185_004..187_003 (= W70 A end 185_003 + 1) and\n'
           '    # B 51_201..51_400 (= W70 B end 51_200 + 1) -- both windows\n'
           '    # CLEAN per THIS gate\'s machine derive (r535 law; the W70\n'
           '    # canon row carries no W71+ WARNING prose -- bm-b r568\n'
           '    # omitted the tail; their commit-message projection\n'
           '    # cross-checked).\n'
           '    # Machine-verified at prereg time\n'
           '    # (results/_r361bmc_w71_band_gate.py ADMIT receipt vs the\n'
           '    # 68-row pre-W71 table + live SEED_REGISTRY values + probe\n'
           '    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin\n'
           '    # slot vacancy machine-checked). NOT a re-pick (R250: W71\n'
           '    # bands were never assigned).\n'
           '    71: {"a": (185_004, 187_003), "b_exit": (51_201, 51_400),\n'
           '         "engine_owner": "bm-c"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[71] landed (anchor=W70 row, insert)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[71] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '71: {"batch": "PERPETUAL-N1-W71"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('"shard_subdir": "n1_w70", "out_name": "n1_w70_results.json",\n'
          '                            "engine_owner": "bm-b"},\n'
          '                       }')
    NEW2 = ('"shard_subdir": "n1_w70", "out_name": "n1_w70_results.json",\n'
            '                            "engine_owner": "bm-b"},\n'
            '                       71: {"batch": "PERPETUAL-N1-W71",\n'
            '                            "prereg": ("research/PERPETUAL_N1_W71_PREREG.md (wave-level frozen "\n'
            '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
            '                                       "new seed bands only; SIXTIETH ENGINE-OWNED WAVE, "\n'
            '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
            '                                       "(first-free-number law over the registered W70 row; "\n'
            '                                       "seat published=reserved MSG-20261002-1017-bmc), "\n'
            '                                       "engine_owner=bm-c, wave 71 BOTH SIDES ARITHMETIC "\n'
            '                                       "CONTINUATION no skip (A 185_004..187_003 / B 51_201..51_400 "\n'
            '                                       "machine-derived CLEAN; the W70 canon row carries no "\n'
            '                                       "W71+ WARNING prose -- derivation basis = registered W70 "\n'
            '                                       "bands + bm-b r568 commit-message projection cross-check "\n'
            '                                       "per r302/r535 law); W1..W67 finalizes ALL LANDED at this "\n'
            '                                       "freeze (net chain head 511,948, K=145,320, bm-b r568), "\n'
            '                                       "W68 bm-a + W69 bm-c + W70 bm-b = THREE in-flight upstream "\n'
            '                                       "seats (finalize chain-pending FAIL-CLOSED r307)"),\n'
            '                            "a_seed_base": 185_004,        # law sec.4 W71 A: 185_004..187_003 (arithmetic continuation)\n'
            '                            "b_exit_seed_base": 51_201,   # law sec.4 W71 B: 51_201..51_400 (arithmetic continuation)\n'
            '                            "shard_subdir": "n1_w71", "out_name": "n1_w71_results.json",\n'
            '                            "engine_owner": "bm-c"},\n'
            '                       }')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[71] landed (anchor=W70 entry tail, insert)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W71 leg --------------
LEG71 = '''
    # --- W71 materializer face (r361 bm-c freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2):
    #     bm-c's TWENTY-THIRD owned per machine-derive (engine_owner==bm-c
    #     rows 22 + candidate); wave 71 = first free number after the
    #     registered W70 row (seat published=reserved
    #     MSG-20261002-1017-bmc; never-dry standing step).
    #     W1..W67 finalizes ALL LANDED (net chain head 511,948, K=145,320,
    #     bm-b r568); W68 bm-a + W69 bm-c (both 12/12 burned, finalize
    #     pending) + W70 bm-b (burn in flight) = THREE in-flight upstream
    #     seats at this freeze (FAIL-CLOSED r307). BOTH SIDES ARITHMETIC
    #     CONTINUATION from the W70 tail no skip (A 185_004..187_003 / B
    #     51_201..51_400 both CLEAN machine-derived; the W70 canon row
    #     carries no W71+ WARNING prose -- derivation basis = registered
    #     W70 bands + bm-b r568 commit-message projection cross-check,
    #     r302/r535 law; ADMIT receipt results/_r361bmc_w71_band_gate.py;
    #     not a re-pick -- R250) --
    _set_wave(71)
    try:
        assert WAVE_CONFIGS[71]["a_seed_base"] == pf.N1_BANDS[71]["a"][0], \\
            "W71 A band drift vs law mirror"
        assert WAVE_CONFIGS[71]["b_exit_seed_base"] == \\
            pf.N1_BANDS[71]["b_exit"][0], "W71 B band drift vs law mirror"
        assert WAVE_CONFIGS[71].get("engine_owner") == \\
            pf.N1_BANDS[71].get("engine_owner") == "bm-c", \\
            "W71 engine_owner drift (law mirror parity)"
        w71_a = {A_SEED_BASE + j for j in range(A_N)}
        w71_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w71_a & w71_b), "W71 A/B band overlap"
        assert not (w71_a & reg_ints) and not (w71_b & reg_ints), \\
            "W71 hits SEED_REGISTRY"
        for nm, band in (("A", w71_a), ("B", w71_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W71 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W71 {nm} hits W1"
            assert not (band & probes), f"W71 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W64..W70
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
        # prior-wave disjointness incl. W48..W70 (all registered; W68/W69/
        # W70 in flight -- coexist by band disjointness per r531).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                      70):
            assert not (w71_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W71 A hits W{wprev}"
            assert not (w71_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W71 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W71 clears it.
        n3r1_used71 = set(range(70_000, 70_006))
        assert not (w71_a & n3r1_used71) and not (w71_b & n3r1_used71), \\
            "W71 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w71_a & lfc_actual12) and not (w71_b & lfc_actual12), \\
            "W71 bands must clear the lfc actual draw range"
        assert not (w71_a & options_actual12) and \\
            not (w71_b & options_actual12), \\
            "W71 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W71 row, r361): BOTH SIDES ARITHMETIC
        # CONTINUATION from the registered W70 tail -- no skip family
        # this wave (both windows CLEAN per the ADMIT receipt).
        assert WAVE_CONFIGS[71]["a_seed_base"] == 185_004 == 185_003 + 1, \\
            "W71 A must start at the registered W70 A end + 1 " \\
            "(arithmetic continuation window 185_004..187_003 CLEAN)"
        assert WAVE_CONFIGS[71]["b_exit_seed_base"] == 51_201 == 51_200 + 1, \\
            "W71 B must start at the registered W70 B end + 1 " \\
            "(arithmetic continuation window 51_201..51_400 CLEAN)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W71-SHARD-0",
                                          "n1w71-0of12"), "W71 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W71-SHARD-11",
                                          "n1w71-11of12")
        assert SHARD_DIR.endswith("n1_w71") and OUT.endswith(
            "n1_w71_results.json"), "W71 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                      70):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W71 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W71_PREREG.md")), \\
            "W71 per-wave prereg missing (materializer requirement)"
        # W71 finalize cumulative deps: W17..W67 outputs ALL PRESENT
        # (static landed seats; chain head 511,948 = W67 bm-b r568
        # K=145,320; W68 bm-a + W69 bm-c + W70 bm-b = THREE in-flight
        # upstream seats -- the finalize merge loop derives the wave set
        # from registry keys at run time and stays FAIL-CLOSED on the
        # not-yet-finalized seats, r307 two-state law).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                      43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
                      56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W71 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 71 (no 15; incl.
        # 48..70 -- all registered, W68/W69/W70 finalize in flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 71) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
             65, 66, 67, 68, 69, 70], \\
            "W71 prior-wave set must derive from registry keys (no 15, " \\
            "incl. 48..70)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W71 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG71.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W71 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 5th face) ------
t2c, eol2c = load(FP2)
if '+ W71 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('law sec.4 W70 row, r568 bm-b] "\n'
          '          "+ T-141 s2 ')
    SEG71 = ('law sec.4 W70 row, r568 bm-b] "\n'
             '          "+ W71 materializer face [same guard set, dep=W17..W67 "\n'
             '          "outputs ALL PRESENT (landed chain head 511,948, K=145,320, "\n'
             '          "bm-b r568), W68 bm-a + W69 bm-c + W70 bm-b = THREE in-flight "\n'
             '          "upstream seats (FAIL-CLOSED r307 at run time), SIXTIETH "\n'
             '          "ENGINE-OWNED WAVE bm-c\'s TWENTY-THIRD owned claim per "\n'
             '          "machine-derive (engine_owner==bm-c rows 22 + candidate), "\n'
             '          "engine_owner=bm-c per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series (wave 71 = "\n'
             '          "first FREE number after the registered W70 row; seat "\n'
             '          "published=reserved MSG-20261002-1017-bmc), BOTH SIDES "\n'
             '          "ARITHMETIC CONTINUATION from the W70 tail no skip (A "\n'
             '          "185_004..187_003 / B 51_201..51_400 both CLEAN "\n'
             '          "machine-derived; the W70 canon row carries no W71+ WARNING "\n'
             '          "prose -- derivation basis = registered W70 bands + bm-b "\n'
             '          "r568 commit-message projection cross-check per r302/r535 "\n'
             '          "law; ADMIT receipt results/_r361bmc_w71_band_gate.py; not a "\n'
             '          "free pick -- R250), N3-R1 used-seed leg, probe-seed "\n'
             '          "cluster leg, law sec.4 W71 row, r361 bm-c] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG71, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W71 segment landed (insert after W70 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W71 row -------------------
ROW71 = """
- N1 波71（r361 bm-c 冻·prereg 时展行）：**第六十枚引擎波·bm-c 第二十三枚自有波〔机面 derive：engine_owner==bm-c 行 22+本候选〕**·engine_owner=bm-c·SATURATION_ENGINE_LAW §1/§2 同 W10-W70 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-c 实例=**常驻架构 v0.4 per-tick 重读**——D-20261002-03 修法同窗实证（W59/W60/W61/W66/W69 五波注册后常驻实例自见自燃=免杀重启）·点火验证唯一证据=产物增长面 r325 律·state queue 面不信】·【never-dry 供给律常设步·**波号 71=注册表 W70 行后首个自由号**·席位公示=MSG-20261002-1017-bmc（published=reserved r518-① 律·W48/W49/W55/W62/W65/W67/W68/W69/W70 先例）·r511 表尾锁例冻结前 fetch 实核表尾时 W71 号位净空·origin 侧 vacancy 机验】·**带位=双面算术续带零跳位（r535 机闸 derive 律）**：W70 行未携带 W71+ 警示投影尾（bm-b r568 行文省略——其 commit 消息与 gate 回执载投影 **A 185_004..187_003 CLEAN／B 51_201..51_400 CLEAN**）→本波 r361 bm-c gate 机闸独立 derive 双面 CLEAN（r302 陈旧指针证伪律下非 prose 转抄——上波行无投影文=机闸 derive 为唯一 derive 面）→本波 **A-ext seed=185_004..187_003**（**A 面算术续带**==W70 A 尾 185_003+1·步长逐字·零跳位）·**B-ext exit seed=51_201..51_400**（**B 面算术续带**==W70 B 尾 51_200+1·步长逐字·零跳位·双侧零跳位·R250：W71 带从未指派·测量面零结果可钓）·【机证净空——leg0 六十九键（68 注册行+候选）+leg0b W70 注册行带面 prose 在场校验〔183_004..185_003/51_001..51_200〕+leg1-A/leg1-B 算术位 CLEAN 机证+leg2 双侧首净窗==候选逐位+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验·**MSG-0640 三修工具**（FIX-A 编辑前 origin-blob 等值断言+FIX-B 锚=最后注册行+行存活核查+FIX-C 推送前纯增量 diff 断言）〕·ADMIT 回执=results/_r361bmc_w71_band_gate.py·起草窗投影探针=results/_r361bmc_w71_probe.py·r361 bm-c 起草窗实跑】·扫描面=pre-W71 六十八行 N1 带表【含 W64 行 171_004..173_003/49_401..49_600〔bm-a r566·finalize 已落账 K=138,720·链头 505,348〕·W65 行 173_004..175_003/49_601..49_800〔bm-b r566·finalize 已落账 K=140,920·链头 507,548〕·W66 行 175_004..177_003/50_001..50_200〔bm-c r359·finalize 已落账 K=143,120·链头 509,748〕·**W67 行 177_004..179_003/50_201..50_400〔bm-b r567 冻/r568 收口·finalize 已落账 K=145,320·净账本链头 511,948·bm-b r568 本窗〕**·W68 行 179_004..181_003/50_501..50_700〔bm-a r568·12/12 烧毕〔r569 presence 重烧〕·finalize 未落账〕·W69 行 181_004..183_003/50_701..50_900〔bm-c r360·12/12 烧毕·finalize 未落账〕·W70 行 183_004..185_003/51_001..51_200〔bm-b r568·注册烧录在飞·finalize 未落账〕】·**三在飞上游席披露：本波 finalize 链序前置=W68+W69+W70 三落账·FAIL-CLOSED r307 两态律**·带域不相交·W1 ext·v1 在用带·SEED_REGISTRY 全键（int 值全清·LOWAMP-P1/P2/P3 键 20.33M 域零交集）·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·lfc 实际流 30_000..30_099·options_wave2 实际流 63_000..63_049（leg-3e 实际流避让腿）·**W72+ 投影（带闸投影腿机证·W72 prereg 照例带闸复核 r335 律）：A 187_004..189_003／B 51_401..51_600 双 CLEAN**（命中面=W72 冻结窗机闸 derive 定谳·本波 gate 投影腿机证零命中）
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce271\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW71.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W71 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    71: {"a": (185_004') == 1, 'FIX-B FAIL: W71 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W71"') == 1, 'FIX-B FAIL: W71 config not exactly once'
for w in (59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70):
    assert n11.count(f'W{w} materializer face') == 2, f'FIX-B FAIL: W{w} leg lost'
assert n11.count('W71 materializer face') == 2, \
    'FIX-B FAIL: W71 leg+summary must be exactly 2'
for w in (48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
          65, 66, 67, 68, 69, 70):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce271\uff08') == 1, 'FIX-B FAIL: canon W71 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W71 added per face')

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
