# -*- coding: utf-8 -*-
"""r568 bm-b W70 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r566 lineage).

FIX-A (origin-blob freshness): every tracked edit target must be content-equal
  to origin/main BEFORE any edit runs. Kills the r559 stale-base clobber.
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W69, bm-c's),
  and after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W70 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W70 = FIFTY-NINTH engine wave, bm-b's TWENTY-SECOND owned per machine-derive
(engine_owner==bm-b rows 21 + candidate). Seat declared published=reserved
(MSG-20261002-1040-bmb, r518-1 law; never-dry standing step under CEO
de-throttle order O-20261001-2355 sec.2 own-continuous-series; wave 70 =
first free number after the registered W69 row, r511 tail-lock, origin
vacancy machine-checked).
B-side = FORK FACE #3 (W69 row mandate: before the F-20261002-03 pin lands,
the freezer MUST machine-derive + disclose the fork). Arithmetic
50_901..51_100 REFUSED mid-band by SEED_REGISTRY xstock_synth_null_a=51_000
-> PAST-HIT RESTART 51_001..51_200 TAKEN (single-mid-hit precedent family
majority: W26-A 95_004 + W68-B 50_501 restart; family gate _first_clean law
lo=max(hits)+1); window-step chain alternative 51_101..51_300 DISCLOSED NOT
TAKEN (W63-B chained precedent was a DOUBLE-hit case). Canon currently
holds BOTH readings in-register (W63 chained + W68 restart) -- contradictory;
pin pending HQ-FEEDBACK F-20261002-03.
W67 finalize LANDED this window (bm-b r568 77fd35e87, net chain head
511,948, K=145,320); W68 bm-a (burn in flight) + W69 bm-c (burn in flight)
= TWO in-flight upstream seats at this freeze (FAIL-CLOSED r307).
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
             69]
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face')
       for w in (59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in (48, 49, 50, 51, 52, 53, 54, 55, 56,
                                                    57, 58, 59, 60, 61, 62, 63, 64, 65, 66,
                                                    67, 68, 69)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[70] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '70: {"a": (183_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    69: {"a": (181_004, 183_003), "b_exit": (50_701, 50_900),\n'
          '         "engine_owner": "bm-c"},\n'
          '}\n')
    NEW = ('    69: {"a": (181_004, 183_003), "b_exit": (50_701, 50_900),\n'
           '         "engine_owner": "bm-c"},\n'
           '    # FIFTY-NINTH ENGINE-OWNED WAVE (r568 bm-b freeze): bm-b\'s\n'
           '    # TWENTY-SECOND owned per machine-derive (engine_owner==bm-b\n'
           '    # rows 21 + candidate). Wave 70 = next free number after the\n'
           '    # registered W69 row (seat declared published=reserved\n'
           '    # MSG-20261002-1040-bmb, r518-1 law; never-dry standing step\n'
           '    # under CEO de-throttle order O-20261001-2355 sec.2).\n'
           '    # W1..W67 finalizes ALL LANDED (net head 511,948, K=145,320,\n'
           '    # bm-b r568 same window); W68 bm-a (burn in flight) + W69 bm-c\n'
           '    # (burn in flight) = TWO in-flight upstream seats at this\n'
           '    # freeze (FAIL-CLOSED r307).\n'
           '    # A-side: ARITHMETIC CONTINUATION from the W69 row tail, no\n'
           '    # skip: 183_004..185_003 (= W69 A end 183_003 + 1) -- CLEAN\n'
           '    # per the W69 row W70+ WARNING projection (bm-c r360 probe +\n'
           '    # this freeze\'s machine re-derive, r535 law).\n'
           '    # B-side: FORK FACE #3 (disclosed per the W69 row mandate;\n'
           '    # pin pending HQ-FEEDBACK F-20261002-03). Arithmetic window\n'
           '    # 50_901..51_100 REFUSED mid-band by SEED_REGISTRY\n'
           '    # xstock_synth_null_a=51_000 -> PAST-HIT RESTART\n'
           '    # 51_001..51_200 TAKEN (single-mid-hit precedent family:\n'
           '    # W26-A 95_004 + W68-B 50_501 restart; family gate\n'
           '    # _first_clean law lo=max(hits)+1); window-step chain\n'
           '    # alternative 51_101..51_300 DISCLOSED NOT TAKEN (the W63-B\n'
           '    # chained precedent was a DOUBLE-hit case).\n'
           '    # Machine-verified at prereg time\n'
           '    # (results/_r568bmb_w70_band_gate.py ADMIT receipt vs the\n'
           '    # 67-row pre-W70 table + live SEED_REGISTRY values + probe\n'
           '    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin\n'
           '    # slot vacancy machine-checked). NOT a re-pick (R250: W70\n'
           '    # bands were never assigned).\n'
           '    70: {"a": (183_004, 185_003), "b_exit": (51_001, 51_200),\n'
           '         "engine_owner": "bm-b"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[70] landed (anchor=W69 row, insert)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[70] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '70: {"batch": "PERPETUAL-N1-W70"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('"shard_subdir": "n1_w69", "out_name": "n1_w69_results.json",\n'
          '                            "engine_owner": "bm-c"},\n'
          '                       }')
    NEW2 = ('"shard_subdir": "n1_w69", "out_name": "n1_w69_results.json",\n'
            '                            "engine_owner": "bm-c"},\n'
            '                       70: {"batch": "PERPETUAL-N1-W70",\n'
            '                            "prereg": ("research/PERPETUAL_N1_W70_PREREG.md (wave-level frozen "\n'
            '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
            '                                       "new seed bands only; FIFTY-NINTH ENGINE-OWNED WAVE, "\n'
            '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
            '                                       "(first-free-number law over the registered W69 row; "\n'
            '                                       "seat declared published=reserved MSG-20261002-1040-bmb), "\n'
            '                                       "engine_owner=bm-b, wave 70 A-side ARITHMETIC "\n'
            '                                       "CONTINUATION no skip (183_004..185_003) + B-side "\n'
            '                                       "PAST-HIT RESTART fork face #3 (arithmetic "\n'
            '                                       "50_901..51_100 REFUSED mid-band by SEED_REGISTRY "\n'
            '                                       "xstock_synth_null_a=51_000 -> 51_001..51_200 taken "\n'
            '                                       "per single-mid-hit precedent family W26-A/W68-B, "\n'
            '                                       "window-step chain 51_101..51_300 disclosed NOT "\n'
            '                                       "taken; pin pending HQ-FEEDBACK F-20261002-03); "\n'
            '                                       "W1..W67 finalizes ALL LANDED at this freeze (net "\n'
            '                                       "chain head 511,948, K=145,320, bm-b r568), W68 bm-a "\n'
            '                                       "+ W69 bm-c = TWO in-flight upstream seats "\n'
            '                                       "(finalize chain-pending FAIL-CLOSED r307)"),\n'
            '                            "a_seed_base": 183_004,        # law sec.4 W70 A: 183_004..185_003 (arithmetic continuation)\n'
            '                            "b_exit_seed_base": 51_001,   # law sec.4 W70 B: 51_001..51_200 (past-hit restart, fork face #3)\n'
            '                            "shard_subdir": "n1_w70", "out_name": "n1_w70_results.json",\n'
            '                            "engine_owner": "bm-b"},\n'
            '                       }')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[70] landed (anchor=W69 entry tail, insert)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W70 leg --------------
LEG70 = '''
    # --- W70 materializer face (r568 bm-b freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2):
    #     bm-b's TWENTY-SECOND owned per machine-derive (engine_owner==bm-b
    #     rows 21 + candidate); wave 70 = next free number after the
    #     registered W69 row (seat declared published=reserved
    #     MSG-20261002-1040-bmb; never-dry standing step).
    #     W67 bm-b finalize LANDED r568 same window (net chain head
    #     511,948, K=145,320); W68 bm-a + W69 bm-c (finalize
    #     chain-pending) = TWO in-flight upstream seats at this
    #     freeze (FAIL-CLOSED r307). A-side ARITHMETIC CONTINUATION
    #     from the W69 tail no skip (183_004..185_003 CLEAN); B-side
    #     PAST-HIT RESTART fork face #3 (arithmetic 50_901..51_100
    #     REFUSED mid-band by SEED_REGISTRY xstock_synth_null_a=51_000
    #     -> 51_001..51_200 taken per single-mid-hit precedent family
    #     W26-A/W68-B; window-step chain 51_101..51_300 disclosed NOT
    #     taken; pin pending HQ-FEEDBACK F-20261002-03; ADMIT receipt
    #     results/_r568bmb_w70_band_gate.py; not a re-pick -- R250) --
    _set_wave(70)
    try:
        assert WAVE_CONFIGS[70]["a_seed_base"] == pf.N1_BANDS[70]["a"][0], \\
            "W70 A band drift vs law mirror"
        assert WAVE_CONFIGS[70]["b_exit_seed_base"] == \\
            pf.N1_BANDS[70]["b_exit"][0], "W70 B band drift vs law mirror"
        assert WAVE_CONFIGS[70].get("engine_owner") == \\
            pf.N1_BANDS[70].get("engine_owner") == "bm-b", \\
            "W70 engine_owner drift (law mirror parity)"
        w70_a = {A_SEED_BASE + j for j in range(A_N)}
        w70_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w70_a & w70_b), "W70 A/B band overlap"
        assert not (w70_a & reg_ints) and not (w70_b & reg_ints), \\
            "W70 hits SEED_REGISTRY"
        for nm, band in (("A", w70_a), ("B", w70_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W70 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W70 {nm} hits W1"
            assert not (band & probes), f"W70 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W63..W69
        # are REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly.
        assert pf.N1_BANDS[63] == {"a": (169_004, 171_003),
                                   "b_exit": (49_201, 49_400),
                                   "engine_owner": "bm-c"}, \\
            "registered W63 row parity drift (r307 two-state)"
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
        # prior-wave disjointness incl. W48..W69 (all registered; W68/W69
        # in flight -- coexist by band disjointness per r531).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69):
            assert not (w70_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W70 A hits W{wprev}"
            assert not (w70_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W70 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W70 clears it.
        n3r1_used70 = set(range(70_000, 70_006))
        assert not (w70_a & n3r1_used70) and not (w70_b & n3r1_used70), \\
            "W70 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w70_a & lfc_actual12) and not (w70_b & lfc_actual12), \\
            "W70 bands must clear the lfc actual draw range"
        assert not (w70_a & options_actual12) and \\
            not (w70_b & options_actual12), \\
            "W70 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W70 row, r568): A ARITHMETIC
        # CONTINUATION; B PAST-HIT RESTART (fork face #3, reading 1
        # taken; window-step chain 51_101..51_300 disclosed NOT
        # taken; pin pending HQ-FEEDBACK F-20261002-03).
        assert WAVE_CONFIGS[70]["a_seed_base"] == 183_004 == 183_003 + 1, \\
            "W70 A must start at the registered W69 A end + 1 " \\
            "(arithmetic continuation window 183_004..185_003 CLEAN -- " \\
            "no skip family)"
        assert WAVE_CONFIGS[70]["b_exit_seed_base"] == 51_001 == 51_000 + 1, \\
            "W70 B must start at the refused point 51_000 + 1 " \\
            "(past-hit restart window 51_001..51_200, fork face #3 " \\
            "reading 1 TAKEN per single-mid-hit precedent family " \\
            "W26-A/W68-B; reading 2 window-step chain 51_101..51_300 " \\
            "disclosed NOT taken; pin pending HQ-FEEDBACK " \\
            "F-20261002-03 -- W70 freezer acted per the W69 row " \\
            "mandate: derive + disclose before the pin)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W70-SHARD-0",
                                          "n1w70-0of12"), "W70 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W70-SHARD-11",
                                          "n1w70-11of12")
        assert SHARD_DIR.endswith("n1_w70") and OUT.endswith(
            "n1_w70_results.json"), "W70 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W70 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W70_PREREG.md")), \\
            "W70 per-wave prereg missing (materializer requirement)"
        # W70 finalize cumulative deps: W17..W67 outputs ALL PRESENT
        # (static landed seats; chain head 511,948 = W67 bm-b r568
        # K=145,320; W68 bm-a + W69 bm-c = TWO in-flight upstream
        # seats -- the finalize merge loop derives the wave set from
        # registry keys at run time and stays FAIL-CLOSED on the
        # not-yet-finalized W68/W69 seats, r307 two-state law).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                      43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
                      56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W70 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 70 (no 15; incl.
        # 48..69 -- all registered, W68/W69 finalize in flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 70) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
             65, 66, 67, 68, 69], \\
            "W70 prior-wave set must derive from registry keys (no 15, " \\
            "incl. 48..69)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W70 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG70.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W70 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 5th face) ------
t2c, eol2c = load(FP2)
if '+ W70 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('law sec.4 W69 row, r360 bm-c] "\n'
          '          "+ T-141 s2 ')
    SEG70 = ('law sec.4 W69 row, r360 bm-c] "\n'
             '          "+ W70 materializer face [same guard set, dep=W17..W67 "\n'
             '          "outputs ALL PRESENT (landed chain head 511,948, K=145,320, "\n'
             '          "bm-b r568 same window), W68 bm-a + W69 bm-c = TWO in-flight "\n'
             '          "upstream seats (FAIL-CLOSED r307 at run time), FIFTY-NINTH "\n'
             '          "ENGINE-OWNED WAVE bm-b\'s TWENTY-SECOND owned claim per "\n'
             '          "machine-derive (engine_owner==bm-b rows 21 + candidate), "\n'
             '          "engine_owner=bm-b per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series (wave 70 = "\n'
             '          "first FREE number after the registered W69 row; seat "\n'
             '          "declared published=reserved MSG-20261002-1040-bmb), A-side "\n'
             '          "ARITHMETIC CONTINUATION from the W69 tail no skip (A "\n'
             '          "183_004..185_003 CLEAN machine-derived) + B-side PAST-HIT "\n'
             '          "RESTART fork face #3 (arithmetic 50_901..51_100 REFUSED "\n'
             '          "mid-band by SEED_REGISTRY xstock_synth_null_a=51_000 -> "\n'
             '          "51_001..51_200 taken per single-mid-hit precedent family "\n'
             '          "W26-A/W68-B, window-step chain 51_101..51_300 disclosed "\n'
             '          "NOT taken, pin pending HQ-FEEDBACK F-20261002-03; ADMIT "\n'
             '          "receipt results/_r568bmb_w70_band_gate.py; not a "\n'
             '          "free pick -- R250), N3-R1 used-seed leg, probe-seed "\n'
             '          "cluster leg, law sec.4 W70 row, r568 bm-b] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG70, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W70 segment landed (insert after W69 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W70 row -------------------
ROW70 = """
- N1 波70（r568 bm-b 冻·prereg 时展行）：**第五十九枚引擎波·bm-b 第二十二枚自有波〔机面 derive：engine_owner==bm-b 行 21+本候选〕**·engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W69 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-b 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启免做·W55/W56/W59/W61/W65/W67 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 70=注册表 W69 行后首个自由号**·席位公示=MSG-20261002-1040-bmb（published=reserved r518-① 律·W48/W49/W55/W62/W65/W67/W68/W69 先例）·r511 表尾锁例冻结前 fetch 实核表尾时 W70 号位净空·origin 侧 vacancy 机验】·**带位=A 面算术续带零跳位＋B 面越 hit 起窗重启（分叉面第三例·强制披露）**：W69 行 W70+ 警示投影 **A 183_004..185_003 CLEAN／B 50_901..51_100 REFUSED**〔SEED_REGISTRY xstock_synth_null_a=**51_000**·窗口中位命中〕（bm-c r360 冻结窗 _r360bmc_w69_probe.py 投影腿机证+本波 r568 bm-b gate 复核逐字同〔r302 陈旧指针证伪律下本波机闸独立 derive 非 prose 转抄〕）→本波 **A-ext seed=183_004..185_003**（**A 面算术续带**==W69 A 尾 183_003+1·步长逐字·零跳位·CLEAN==W69 行公示投影逐位）；**B-ext exit seed=51_001..51_200**（**B 面越 hit 起窗重启**＝拒点 51_000+1 起·**分叉面第三例**：两读法分叉——**读法一〔越 hit 起窗 51_001..51_200·本波采此〕**（单点中位命中期例族多数：W26-A 95_004 起窗+W68-B 50_501 起窗先例·家族 gate 工具 _first_clean 内生律 lo=max(hits)+1）vs **读法二〔连锁整窗步进 51_101..51_300·披露不采〕**（W63-B 连锁先例=双点命中期非单点期）；法典现持 W63 连锁〔在册〕+W68 越hit〔在册〕双读法相反·**§4 钉死行待 HQ-FEEDBACK F-20261002-03 裁定·W70 冻结方按裁定行执行（裁定前=冻结方机闸 derive+分叉披露强制·W69 行明令·本行+gate 回执双面满足）**；两读法窗均机证净空·带域不相交）·【机证净空——leg0 六十八键（67 注册行+候选）+leg0b W69 行 W70+ 警示 prose 在场校验+leg1-A 算术位 CLEAN 机证+leg1-B 算术位 REFUSED 拒点集==[51_000] 机证+leg2 双读法双窗机证净空+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验·**MSG-0640 三修工具**（FIX-A 编辑前 origin-blob 等值断言+FIX-B 锚=最后注册行+行存活核查+FIX-C 推送前纯增量 diff 断言）〕·ADMIT 回执=results/_r568bmb_w70_band_gate.py·r568 bm-b 起草窗实跑·非重挑 R250·W70 带从未指派·测量面零结果可钓】·扫描面=pre-W70 六十七行 N1 带表【含 **W64 行 171_004..173_003/49_401..49_600〔bm-a r566·finalize 已落账 K=138,720·链头 505,348〕**·**W65 行 173_004..175_003/49_601..49_800〔bm-b r566·finalize 已落账 K=140,920·链头 507,548〕**·**W66 行 175_004..177_003/50_001..50_200〔bm-c r359·finalize 已落账 K=143,120·链头 509,748〕**·**W67 行 177_004..179_003/50_201..50_400〔bm-b r567·finalize 已落账 K=145,320·净账本链头 511,948·bm-b r568 本窗〕**·**W68 行 179_004..181_003/50_501..50_700〔bm-a r568·注册烧录在飞·finalize 未落账〕**·**W69 行 181_004..183_003/50_701..50_900〔bm-c r360·注册烧录在飞·finalize 未落账〕**】·**两在飞上游席披露：本波 finalize 链序前置=W68+W69 落账·FAIL-CLOSED r307 两态律**·带域不相交·W1 ext·v1 在用带·SEED_REGISTRY 全键（int 值全清·LOWAMP-P1/P2/P3 键 20.33M 域零交集）·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·N2/N4 探针点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·lfc 实际流 30_000..30_099·options_wave2 实际流 63_000..63_049（leg-3e 实际流避让腿）·**W71+ 投影（带闸投影腿机证=results/_r568bmb_w70_band_gate.py 尾投影·W71 prereg 照例带闸复核 r335 律）**·prereg=PERPETUAL_N1_W70_PREREG.md 冻结〔S5 锚=W67 实测（锚滚动律自 W63 滚至 W67）：merged mu −0.092429/W67-only mu −0.089229/sigma 0.243181/A-p95 0.3213/K-lift −0.0001·累计池投影 151,920（含 W68+W69 在飞 4,400）〕·burn 由本机 tick 引擎自燃·finalize=活链头 derive one-pass（r538 一过律）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce270\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW70.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W70 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    70: {"a": (183_004') == 1, 'FIX-B FAIL: W70 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W70"') == 1, 'FIX-B FAIL: W70 config not exactly once'
for w in (59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69):
    assert n11.count(f'W{w} materializer face') == 2, f'FIX-B FAIL: W{w} leg lost'
assert n11.count('W70 materializer face') == 2, \
    'FIX-B FAIL: W70 leg+summary must be exactly 2'
for w in (48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
          65, 66, 67, 68, 69):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce270\uff08') == 1, 'FIX-B FAIL: canon W70 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W70 added per face')

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
