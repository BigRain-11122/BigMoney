# -*- coding: utf-8 -*-
"""r572 bm-b W76 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r566 lineage).

FIX-A (origin-blob freshness): every tracked edit target must be content-equal
  to origin/main BEFORE any edit runs. Kills the r559 stale-base clobber.
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W75, bm-a's),
  and after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W76 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W76 = SIXTY-FIFTH engine wave, bm-b's TWENTY-FIFTH owned per machine-derive
(engine_owner==bm-b rows 24 + candidate). Seat declared published=reserved
(MSG-20261002-1130-bmb, r518-1 law; never-dry standing step under CEO
de-throttle order O-20261001-2355 sec.2 own-continuous-series; wave 76 =
first free number after the registered W75 row, r511 tail-lock, origin
vacancy machine-checked).
BANDS: BOTH SIDES plain ARITHMETIC CONTINUATION from the registered W75
tail -- A 195_004..197_003 (= W75 A end 195_003 + 1), B 52_401..52_600
(= W75 B end 52_400 + 1); zero skip both sides, single reading, no fork
face (F-20261002-03 skip-semantics divergence not triggered).
W1..W74 finalizes ALL LANDED (net chain head 527,348, K=160,720, bm-b r572
same window); W75 bm-a (burn in flight) = ONE in-flight upstream seat at
this freeze (FAIL-CLOSED r307).
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
             69, 70, 71, 72, 73, 74, 75]
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face')
       for w in (59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in (48, 49, 50, 51, 52, 53, 54, 55, 56,
                                                    57, 58, 59, 60, 61, 62, 63, 64, 65, 66,
                                                    67, 68, 69, 70, 71, 72, 73, 74, 75)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[76] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '76: {"a": (195_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    75: {"a": (193_004, 195_003), "b_exit": (52_201, 52_400),\n'
          '         "engine_owner": "bm-a"},\n'
          '}\n')
    NEW = ('    75: {"a": (193_004, 195_003), "b_exit": (52_201, 52_400),\n'
           '         "engine_owner": "bm-a"},\n'
           '    # SIXTY-FIFTH ENGINE-OWNED WAVE (r572 bm-b freeze): bm-b\'s\n'
           '    # TWENTY-FIFTH owned per machine-derive (engine_owner==bm-b\n'
           '    # rows 24 + candidate). Wave 76 = next free number after the\n'
           '    # registered W75 row (seat declared published=reserved\n'
           '    # MSG-20261002-1130-bmb, r518-1 law; never-dry standing step\n'
           '    # under CEO de-throttle order O-20261001-2355 sec.2).\n'
           '    # W1..W74 finalizes ALL LANDED (net head 527,348, K=160,720,\n'
           '    # bm-b r572); W75 bm-a (burn in flight, finalize pending) =\n'
           '    # ONE in-flight upstream seat at this freeze (FAIL-CLOSED\n'
           '    # r307).\n'
           '    # BOTH SIDES ARITHMETIC CONTINUATION from the W75 row tail,\n'
           '    # zero skip: A 195_004..197_003 (= W75 A end 195_003 + 1),\n'
           '    # B 52_401..52_600 (= W75 B end 52_400 + 1); single reading,\n'
           '    # no fork face (F-20261002-03 not triggered).\n'
           '    # Machine-verified at prereg time\n'
           '    # (results/_r572bmb_w76_band_gate.py ADMIT receipt vs the\n'
           '    # 73-row pre-W76 table + live SEED_REGISTRY values + probe\n'
           '    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin\n'
           '    # slot vacancy machine-checked). NOT a re-pick (R250: W76\n'
           '    # bands were never assigned).\n'
           '    76: {"a": (195_004, 197_003), "b_exit": (52_401, 52_600),\n'
           '         "engine_owner": "bm-b"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[76] landed (anchor=W75 row, insert)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[76] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '76: {"batch": "PERPETUAL-N1-W76"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('"shard_subdir": "n1_w75", "out_name": "n1_w75_results.json",\n'
          '                            "engine_owner": "bm-a"},\n'
          '                       }')
    NEW2 = ('"shard_subdir": "n1_w75", "out_name": "n1_w75_results.json",\n'
            '                            "engine_owner": "bm-a"},\n'
            '                       76: {"batch": "PERPETUAL-N1-W76",\n'
            '                            "prereg": ("research/PERPETUAL_N1_W76_PREREG.md (wave-level frozen "\n'
            '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
            '                                       "new seed bands only; SIXTY-FIFTH ENGINE-OWNED WAVE, "\n'
            '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
            '                                       "(first-free-number law over the registered W75 row; "\n'
            '                                       "seat declared published=reserved MSG-20261002-1130-bmb), "\n'
            '                                       "engine_owner=bm-b, wave 76 BOTH SIDES ARITHMETIC "\n'
            '                                       "CONTINUATION zero skip (A 195_004..197_003 CLEAN + "\n'
            '                                       "B 52_401..52_600 CLEAN; single reading, no fork "\n'
            '                                       "face, F-20261002-03 not triggered); "\n'
            '                                       "W1..W74 finalizes ALL LANDED at this freeze (net "\n'
            '                                       "chain head 527,348, K=160,720, bm-b r572), W75 bm-a = "\n'
            '                                       "ONE in-flight upstream seat "\n'
            '                                       "(finalize chain-pending FAIL-CLOSED r307)"),\n'
            '                            "a_seed_base": 195_004,        # law sec.4 W76 A: 195_004..197_003 (arithmetic continuation)\n'
            '                            "b_exit_seed_base": 52_401,   # law sec.4 W76 B: 52_401..52_600 (arithmetic continuation)\n'
            '                            "shard_subdir": "n1_w76", "out_name": "n1_w76_results.json",\n'
            '                            "engine_owner": "bm-b"},\n'
            '                       }')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[76] landed (anchor=W75 entry tail, insert)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W76 leg --------------
LEG76 = '''
    # --- W76 materializer face (r572 bm-b freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2):
    #     bm-b's TWENTY-FIFTH owned per machine-derive (engine_owner==bm-b
    #     rows 24 + candidate); wave 76 = first free number after the
    #     registered W75 row (seat declared published=reserved
    #     MSG-20261002-1130-bmb; never-dry standing step).
    #     W1..W74 finalizes ALL LANDED (net chain head 527,348, K=160,720,
    #     bm-b r572); W75 bm-a (burn in flight, finalize pending) = ONE
    #     in-flight upstream seat at this freeze (FAIL-CLOSED r307).
    #     BOTH SIDES ARITHMETIC CONTINUATION from the W75 tail no skip
    #     (A 195_004..197_003 CLEAN + B 52_401..52_600 CLEAN; single
    #     reading, no fork face; ADMIT receipt
    #     results/_r572bmb_w76_band_gate.py; not a re-pick -- R250) --
    _set_wave(76)
    try:
        assert WAVE_CONFIGS[76]["a_seed_base"] == pf.N1_BANDS[76]["a"][0], \\
            "W76 A band drift vs law mirror"
        assert WAVE_CONFIGS[76]["b_exit_seed_base"] == \\
            pf.N1_BANDS[76]["b_exit"][0], "W76 B band drift vs law mirror"
        assert WAVE_CONFIGS[76].get("engine_owner") == \\
            pf.N1_BANDS[76].get("engine_owner") == "bm-b", \\
            "W76 engine_owner drift (law mirror parity)"
        w76_a = {A_SEED_BASE + j for j in range(A_N)}
        w76_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w76_a & w76_b), "W76 A/B band overlap"
        assert not (w76_a & reg_ints) and not (w76_b & reg_ints), \\
            "W76 hits SEED_REGISTRY"
        for nm, band in (("A", w76_a), ("B", w76_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W76 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W76 {nm} hits W1"
            assert not (band & probes), f"W76 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W65..W75
        # are REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly.
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
        # prior-wave disjointness incl. W48..W75 (all registered; W75
        # in flight -- coexist by band disjointness per r531).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                      70, 71, 72, 73, 74, 75):
            assert not (w76_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W76 A hits W{wprev}"
            assert not (w76_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W76 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W76 clears it.
        n3r1_used76 = set(range(70_000, 70_006))
        assert not (w76_a & n3r1_used76) and not (w76_b & n3r1_used76), \\
            "W76 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w76_a & lfc_actual12) and not (w76_b & lfc_actual12), \\
            "W76 bands must clear the lfc actual draw range"
        assert not (w76_a & options_actual12) and \\
            not (w76_b & options_actual12), \\
            "W76 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W76 row, r572): BOTH SIDES ARITHMETIC
        # CONTINUATION from the registered W75 tail (zero skip) --
        # the arithmetic windows are CLEAN vs the full reserved
        # universe (no refusal point inside either window; single
        # reading, no fork face, F-20261002-03 not triggered).
        assert WAVE_CONFIGS[76]["a_seed_base"] == 195_004 == 195_003 + 1, \\
            "W76 A must start at the registered W75 A end + 1 " \\
            "(arithmetic continuation window 195_004..197_003 CLEAN)"
        assert WAVE_CONFIGS[76]["b_exit_seed_base"] == 52_401 == 52_400 + 1, \\
            "W76 B must start at the registered W75 B end + 1 " \\
            "(arithmetic continuation window 52_401..52_600 CLEAN)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W76-SHARD-0",
                                          "n1w76-0of12"), "W76 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W76-SHARD-11",
                                          "n1w76-11of12")
        assert SHARD_DIR.endswith("n1_w76") and OUT.endswith(
            "n1_w76_results.json"), "W76 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                      70, 71, 72, 73, 74, 75):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W76 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W76_PREREG.md")), \\
            "W76 per-wave prereg missing (materializer requirement)"
        # W76 finalize cumulative deps: W17..W74 outputs ALL PRESENT
        # (static landed seats; chain head 527,348 = W74 bm-b r572
        # K=160,720; W75 bm-a = ONE in-flight upstream seat -- the
        # finalize merge loop derives the wave set from registry keys
        # at run time and stays FAIL-CLOSED on the not-yet-finalized
        # seat, r307 two-state law).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                      43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
                      56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68,
                      69, 70, 71, 72, 73, 74):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W76 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 76 (no 15; incl.
        # 48..75 -- all registered, W75 finalize in flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 76) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
             65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75], \\
            "W76 prior-wave set must derive from registry keys (no 15, " \\
            "incl. 48..75)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W76 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG76.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W76 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 5th face) ------
t2c, eol2c = load(FP2)
if '+ W76 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('r571 bm-a] "\n'
          '          "+ T-141 s2 ')
    SEG76 = ('r571 bm-a] "\n'
             '          "+ W76 materializer face [same guard set, dep=W17..W74 "\n'
             '          "outputs ALL PRESENT (landed chain head 527,348, "\n'
             '          "K=160,720, bm-b r572 same window), W75 bm-a = ONE in-flight "\n'
             '          "upstream seat (FAIL-CLOSED r307 at run time), SIXTY-FIFTH "\n'
             '          "ENGINE-OWNED WAVE bm-b\'s TWENTY-FIFTH owned claim per "\n'
             '          "machine-derive (engine_owner==bm-b rows 24 + candidate), "\n'
             '          "engine_owner=bm-b per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series (wave 76 = "\n'
             '          "first FREE number after the registered W75 row; seat "\n'
             '          "declared published=reserved MSG-20261002-1130-bmb), BOTH "\n'
             '          "SIDES ARITHMETIC CONTINUATION from the W75 tail no skip "\n'
             '          "(A 195_004..197_003 CLEAN + B 52_401..52_600 CLEAN; "\n'
             '          "single reading, no fork face, F-20261002-03 not "\n'
             '          "triggered; ADMIT receipt "\n'
             '          "results/_r572bmb_w76_band_gate.py; not a "\n'
             '          "free pick -- R250), N3-R1 used-seed leg, probe-seed "\n'
             '          "cluster leg, law sec.4 W76 row, r572 bm-b] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG76, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W76 segment landed (insert after W75 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W76 row -------------------
ROW76 = """
- N1 波76（r572 bm-b 冻·prereg 时展行）：**第六十五枚引擎波·bm-b 第二十五枚自有波〔机面 derive：engine_owner==bm-b 行 24+本候选〕**·engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W75 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-b 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启免做·W55/W56/W59/W61/W65/W67/W70/W72/W74 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 76=注册表 W75 行后首个自由号**·席位公示=MSG-20261002-1130-bmb（published=reserved r518-① 律·W48/W49/W55/W62/W65/W67/W68/W69/W70/W71/W72/W73/W74/W75 先例）·r511 表尾锁例冻结前 fetch 实核表尾时 W76 号位净空·origin 侧 vacancy 机验】·**带位=双侧算术续带零跳位（单读法零分叉面）**：W75 行携带 W76+ 警示投影 **A 195_004..197_003 CLEAN／B 52_401..52_600 CLEAN**（bm-a r571 gate 投影腿机证）→本波 **r572 bm-b gate 机闸独立 derive 复核逐字同**（r302 陈旧指针证伪律下非 prose 转抄——机闸 derive 为唯一 derive 面·prose 交叉核对）→本波 **A-ext seed=195_004..197_003**（**A 面算术续带**==W75 A 尾 195_003+1·步长逐字·零跳位）；**B-ext exit seed=52_401..52_600**（**B 面算术续带**==W75 B 尾 52_400+1·步长逐字·零跳位·双侧算术窗零拒绝点=单读法零分叉〔F-20261002-03 跳位语义分叉面不触发〕·R250：W76 带从未指派·测量面零结果可钓）。【机证净空——leg0 七十四键（73 注册行+候选）+leg0b W75 行 W76+ 警示 prose 在场校验+leg1-A 算术位 CLEAN 机证+leg1-B 算术位 CLEAN 机证+leg2 双侧首净窗==候选逐位+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验·**MSG-0640 三修工具**（FIX-A 编辑前 origin-blob 等值断言+FIX-B 锚=最后注册行+行存活核查+FIX-C 推送前纯增量 diff 断言）〕·ADMIT 回执=results/_r572bmb_w76_band_gate.py·r572 bm-b 起草窗实跑·非重挑 R250。扫描面=pre-W76 七十三行 N1 带表【含 **W72 行 187_004..189_003/51_401..51_600〔bm-b r570 冻·finalize 已落账 K=156,320·链头 522,948〕**·**W73 行 189_004..191_003/51_601..51_800〔bm-a r570 冻·finalize 已落账 K=158,520·链头 525,148〕**·**W74 行 191_004..193_003/52_001..52_200〔bm-b r571 冻·finalize 已落账 K=160,720·净账本链头 527,348·bm-b r572 本窗〕**·**W75 行 193_004..195_003/52_201..52_400〔bm-a r571 冻·烧录在飞·finalize 未落账〕**】·**一在飞上游席披露：本波 finalize 链序前置=W75 bm-a（烧录在飞）——FAIL-CLOSED r307 两态律·该席落账后 one-pass**。W76 行 **W77+ 投影（gate 投影腿机证·W77 prereg 窗机闸复核 r335 律）**：**A 197_004..199_003 CLEAN／B 52_601..52_800 CLEAN**（A 算术续带==W76 A 尾 197_003+1·B 算术续带==W76 B 尾 52_600+1）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce276\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW76.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W76 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    76: {"a": (195_004') == 1, 'FIX-B FAIL: W76 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W76"') == 1, 'FIX-B FAIL: W76 config not exactly once'
for w in (59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75):
    assert n11.count(f'W{w} materializer face') == 2, f'FIX-B FAIL: W{w} leg lost'
assert n11.count('W76 materializer face') == 2, \
    'FIX-B FAIL: W76 leg+summary must be exactly 2'
for w in (48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
          65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce276\uff08') == 1, 'FIX-B FAIL: canon W76 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W76 added per face')

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
