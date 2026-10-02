# -*- coding: utf-8 -*-
"""r378 bm-c W108 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening.

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED rows (W107 bm-a
  r587); every registered row signature survives exactly; exactly one new
  W108 signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.
AST gate (r580/r581 lesson): post-edit ast.parse on both py faces.

W108 = NINETY-EIGHTH engine wave by MACHINE-DERIVE (engine_owner rows 97 +
candidate; gate leg0 machine output governs per r359 law), bm-c's
THIRTY-SECOND owned (engine_owner==bm-c rows 31 + candidate).
First free number after the REGISTERED W107 row (bm-a r587 freeze
a554dedd3), SINGLE STATE zero seat gap. Seat-time vs freeze-time tenses
converge identical bands (W106 r585 precedent): seat published at
MSG-20261002-1804-bmc (pushed origin ed44e0857 BEFORE this freeze per
r565 law) when W107 was published-unregistered (skip-past-published hops
1/1 projection); at freeze W107 is REGISTERED -> single-state arithmetic
continuation from the W107 tails hops 0/0. Dual-state ADMIT receipt
results/_r378bmc_w108_band_gate.py rc0 (state A + state B both run).
Bands:
  A 259_004..261_003 (== W107 A tail 259_003+1, stride 2_000, hops=0).
  B 60_601..60_800   (== W107 B tail 60_600+1, stride 200, hops=0).
W102 finalize LANDED at this freeze (chain head 588,948, K=222,320 = bm-c
r378 one-pass, commit 5c5541157). FIVE in-flight upstream seats (W103
bm-b + W104 bm-a + W105 bm-c + W106 bm-b burned-unfinalized + W107 bm-a
fresh-freeze burn pending) -- finalize merge loop stays FAIL-CLOSED r307
at run time. W109+ projection: A 261_004..263_003 CLEAN / B 60_801..61_000
REFUSED [61_000] (next freezer re-derives, never transcribes).
"""
import subprocess, sys, os, ast

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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 108))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 108)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 108)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[108] ---------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '108: {"a": (259_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    107: {"a": (257_004, 259_003), "b_exit": (60_401, 60_600),\n'
          '         "engine_owner": "bm-a"},\n'
          '}\n')
    NEW = ('    107: {"a": (257_004, 259_003), "b_exit": (60_401, 60_600),\n'
           '         "engine_owner": "bm-a"},\n'
           '    # NINETY-EIGHTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r378 bm-c\n'
           '    # freeze): engine_owner rows 97 + candidate; bm-c\'s thirty-\n'
           '    # second owned per machine-derive (engine_owner==bm-c rows 31 +\n'
           '    # candidate). Wave 108 = first free number after the REGISTERED\n'
           '    # W107 row (bm-a r587 freeze a554dedd3), SINGLE STATE zero seat\n'
           '    # gap. Seat-time vs freeze-time tenses converge identical bands\n'
           '    # (W106 r585 precedent): seat published=reserved\n'
           '    # MSG-20261002-1804-bmc pushed to origin ed44e0857 BEFORE this\n'
           '    # freeze per r565 early-visibility law when W107 was published-\n'
           '    # unregistered (skip-past-published hops 1/1 projection); at\n'
           '    # freeze W107 is registered -> single-state arithmetic\n'
           '    # continuation from the W107 tails hops 0/0. W102 finalize\n'
           '    # LANDED at this freeze (landed chain head 588,948 = W102 bm-c\n'
           '    # r378, K=222,320). FIVE in-flight upstream seats (W103 bm-b +\n'
           '    # W104 bm-a + W105 bm-c + W106 bm-b burned-unfinalized + W107\n'
           '    # bm-a fresh-freeze burn pending) -- finalize merge loop stays\n'
           '    # FAIL-CLOSED r307 at run time.\n'
           '    # A = arithmetic continuation == W107 A tail 259_003+1:\n'
           '    # 259_004..261_003 CLEAN hops=0. B = arithmetic continuation\n'
           '    # == W107 B tail 60_600+1: 60_601..60_800 CLEAN hops=0.\n'
           '    # ADMIT receipt results/_r378bmc_w108_band_gate.py rc0\n'
           '    # (dual-state); live SEED_REGISTRY + probe cluster\n'
           '    # 95_000..95_003 r335 leg + N3-R1 used-seed band 70_000..70_005\n'
           '    # MSG-183x r529 leg.\n'
           '    # W109+ projection: A 261_004..263_003 CLEAN; B 60_801..61_000\n'
           '    # REFUSED [61_000] (next freezer must re-derive, never\n'
           '    # transcribe).\n'
           '    # NOT a re-pick (R250: W108 bands were never assigned).\n'
           '    108: {"a": (259_004, 261_003), "b_exit": (60_601, 60_800),\n'
           '         "engine_owner": "bm-c"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[108] landed (anchor=W107 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[108] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '108: {"batch": "PERPETUAL-N1-W108"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w107", "out_name": "n1_w107_results.json",\n'
          '                            "engine_owner": "bm-a"},\n')
    NEW2 = A2 + (
        '                       108: {"batch": "PERPETUAL-N1-W108",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W108_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; NINETY-EIGHTH ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 97 + candidate), own-series "\n'
        '                                       "continuation per O-20261001-2355 sec.2 (first-free-number "\n'
        '                                       "law after the REGISTERED W107 row bm-a r587 a554dedd3, "\n'
        '                                       "SINGLE STATE zero seat gap; seat-time vs freeze-time tenses "\n'
        '                                       "converge identical bands per the W106 r585 precedent: seat "\n'
        '                                       "published=reserved MSG-20261002-1804-bmc PUSHED to origin "\n'
        '                                       "ed44e0857 BEFORE this freeze per r565 early-visibility law "\n'
        '                                       "when W107 was published-unregistered, skip-past-published "\n'
        '                                       "hops 1/1 projection; at freeze W107 registered -> arithmetic "\n'
        '                                       "continuation hops 0/0; engine_owner=bm-c, wave 108: A = "\n'
        '                                       "arithmetic continuation from the REGISTERED W107 A tail "\n'
        '                                       "(259_004..261_003 CLEAN hops=0) + B = arithmetic "\n'
        '                                       "continuation from the REGISTERED W107 B tail (60_601..60_800 "\n'
        '                                       "CLEAN hops=0; dual-state ADMIT receipt "\n'
        '                                       "results/_r378bmc_w108_band_gate.py; W109+ projection: A "\n'
        '                                       "261_004..263_003 CLEAN / B 60_801..61_000 REFUSED [61_000] "\n'
        '                                       "for the next freezer); W102 finalize LANDED at this freeze "\n'
        '                                       "(chain head 588,948, K=222,320) + FIVE in-flight upstream "\n'
        '                                       "seats W103 bm-b + W104 bm-a + W105 bm-c + W106 bm-b burned-"\n'
        '                                       "unfinalized + W107 bm-a fresh-freeze burn pending -- "\n'
        '                                       "finalize merge loop stays FAIL-CLOSED r307 at run time)"),\n'
        '                            "a_seed_base": 259_004,        # law sec.4 W108 A: 259_004..261_003 (arithmetic continuation from the registered W107 A tail)\n'
        '                            "b_exit_seed_base": 60_601,   # law sec.4 W108 B: 60_601..60_800 (arithmetic continuation from the registered W107 B tail)\n'
        '                            "shard_subdir": "n1_w108", "out_name": "n1_w108_results.json",\n'
        '                            "engine_owner": "bm-c"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[108] landed (anchor=W107 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W108 leg --------------
LEG108 = '''
    # --- W108 materializer face (r378 bm-c freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-c's
    #     thirty-second owned per machine-derive (engine_owner==bm-c
    #     rows 31 + candidate); wave 108 = first free number after
    #     the REGISTERED W107 row (bm-a r587 freeze a554dedd3),
    #     SINGLE STATE zero seat gap. Seat-time vs freeze-time tenses
    #     converge identical bands (W106 r585 precedent): seat
    #     published=reserved MSG-20261002-1804-bmc pushed to origin
    #     ed44e0857 BEFORE this freeze per r565 law when W107 was
    #     published-unregistered (skip-past-published hops 1/1
    #     projection); at freeze W107 registered -> single-state
    #     arithmetic continuation hops 0/0. NINETY-EIGHTH engine
    #     wave BY MACHINE-DERIVE (engine_owner rows 97 + candidate;
    #     gate leg0 machine output governs per r359 law). W102
    #     finalize LANDED (chain head 588,948, K=222,320 = bm-c r378)
    #     + FIVE in-flight upstream seats W103 bm-b + W104 bm-a +
    #     W105 bm-c + W106 bm-b burned-unfinalized + W107 bm-a
    #     fresh-freeze burn pending -- FAIL-CLOSED r307 at run time.
    #     ADMIT receipt results/_r378bmc_w108_band_gate.py (dual
    #     state); not a re-pick (R250: W108 bands were never
    #     assigned).
    _set_wave(108)
    try:
        assert WAVE_CONFIGS[108]["a_seed_base"] == pf.N1_BANDS[108]["a"][0], \\
            "W108 A band drift vs law mirror"
        assert WAVE_CONFIGS[108]["b_exit_seed_base"] == \\
            pf.N1_BANDS[108]["b_exit"][0], "W108 B band drift vs law mirror"
        assert WAVE_CONFIGS[108].get("engine_owner") == \\
            pf.N1_BANDS[108].get("engine_owner") == "bm-c", \\
            "W108 engine_owner drift (law mirror parity)"
        w108_a = {A_SEED_BASE + j for j in range(A_N)}
        w108_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w108_a & w108_b), "W108 A/B band overlap"
        assert not (w108_a & reg_ints) and not (w108_b & reg_ints), \\
            "W108 hits SEED_REGISTRY"
        for nm, band in (("A", w108_a), ("B", w108_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W108 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W108 {nm} hits W1"
            assert not (band & probes), f"W108 {nm} hits probe seeds"
        # registered row parity (r307 pinned constants, recent estate)
        assert pf.N1_BANDS[100] == {"a": (243_004, 245_003),
                                   "b_exit": (58_751, 58_950),
                                   "engine_owner": "bm-b"}, \\
            "registered W100 row parity drift (r307; bm-b r583)"
        assert pf.N1_BANDS[101] == {"a": (245_004, 247_003),
                                   "b_exit": (59_001, 59_200),
                                   "engine_owner": "bm-a"}, \\
            "registered W101 row parity drift (r307; bm-a r583)"
        assert pf.N1_BANDS[102] == {"a": (247_004, 249_003),
                                   "b_exit": (59_201, 59_400),
                                   "engine_owner": "bm-c"}, \\
            "registered W102 row parity drift (r307; bm-c r375)"
        assert pf.N1_BANDS[103] == {"a": (249_004, 251_003),
                                   "b_exit": (59_401, 59_600),
                                   "engine_owner": "bm-b"}, \\
            "registered W103 row parity drift (r307; bm-b r584)"
        assert pf.N1_BANDS[104] == {"a": (251_004, 253_003),
                                   "b_exit": (59_601, 59_800),
                                   "engine_owner": "bm-a"}, \\
            "registered W104 row parity drift (r307; bm-a r586)"
        assert pf.N1_BANDS[105] == {"a": (253_004, 255_003),
                                   "b_exit": (60_001, 60_200),
                                   "engine_owner": "bm-c"}, \\
            "registered W105 row parity drift (r307; bm-c r376)"
        assert pf.N1_BANDS[106] == {"a": (255_004, 257_003),
                                   "b_exit": (60_201, 60_400),
                                   "engine_owner": "bm-b"}, \\
            "registered W106 row parity drift (r307; bm-b r585)"
        assert pf.N1_BANDS[107] == {"a": (257_004, 259_003),
                                   "b_exit": (60_401, 60_600),
                                   "engine_owner": "bm-a"}, \\
            "registered W107 row parity drift (r307; bm-a r587)"
        # prior-wave disjointness W2..W107 (single state: all
        # registered, dynamic registry derive, r511 law)
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 108):
            assert not (w108_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W108 A hits W{wprev}"
            assert not (w108_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W108 B hits W{wprev}"
        n3r1_used108 = set(range(70_000, 70_006))
        assert not (w108_a & n3r1_used108) and not (w108_b & n3r1_used108), \\
            "W108 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        assert not (w108_a & lfc_actual12) and not (w108_b & lfc_actual12), \\
            "W108 bands must clear the lfc actual draw range"
        assert not (w108_a & options_actual12) and \\
            not (w108_b & options_actual12), \\
            "W108 bands must clear the options_wave2 actual draw range"
        # W107 band disjointness (registered row, explicit leg; was the
        # skip-past-published reserved face at seat time)
        w107_band_a = set(range(257_004, 259_004))
        w107_band_b = set(range(60_401, 60_601))
        assert not (w108_a & w107_band_a), \\
            "W108 A must clear the W107 band (registered r518-1 lineage)"
        assert not (w108_b & w107_band_b), \\
            "W108 B must clear the W107 band (registered r518-1 lineage)"
        # band facts (law sec.4 W108 row, r378): A = arithmetic
        # continuation from the REGISTERED W107 A tail; B = arithmetic
        # continuation from the REGISTERED W107 B tail (dual-state
        # convergent: seat-time skip-past-published == freeze-time
        # registered arithmetic, identical bands).
        assert WAVE_CONFIGS[108]["a_seed_base"] == 259_004 == 259_003 + 1, (
            "W108 A must be the arithmetic continuation from the "
            "REGISTERED W107 A tail 259_003 (single state; seat-time "
            "skip-past-published reading converges identical)")
        assert WAVE_CONFIGS[108]["b_exit_seed_base"] == 60_601 == 60_600 + 1, (
            "W108 B must be the arithmetic continuation from the "
            "REGISTERED W107 B tail 60_600 (single state; seat-time "
            "skip-past-published reading converges identical)")
        assert not (set(range(259_004, 261_004)) & reg_ints), \\
            "W108 A window must be CLEAN (ADMIT face)"
        assert not (set(range(60_601, 60_801)) & reg_ints), \\
            "W108 B window must be CLEAN (ADMIT face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W108-SHARD-0",
                                          "n1w108-0of12"), "W108 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W108-SHARD-11",
                                           "n1w108-11of12")
        assert SHARD_DIR.endswith("n1_w108") and OUT.endswith(
            "n1_w108_results.json"), "W108 path drift"
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 108):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W108 shard dir collides with W{wprev}"
        # W108 finalize cumulative deps: W17..W102 outputs ALL PRESENT
        # (landed chain head 588,948 = W102 bm-c r378; W103/W104/W105/
        # W106/W107 registered with finalizes NOT landed -- honest
        # note; the finalize merge loop derives the wave set from
        # registry keys at run time and stays FAIL-CLOSED, r307 law).
        for _depw in range(17, 103):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W108 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): every
        # registered wave below 108 composes; wave 15 excluded by
        # design; W2..W107 all registered single state zero seat gap.
        assert sorted(w for w in WAVE_CONFIGS if w < 108) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 108)], \\
            "W108 prior-wave set must derive from registry keys (no 15; " \\
            "W2..W107 registered single state zero seat gap)"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W108_PREREG.md")), \\
            "W108 per-wave prereg missing (materializer requirement)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W108 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    # r580/r581 anchor law: FULL-LINE anchor, replacement = anchor head
    # + blank + new leg + anchor tail-head line (no full-anchor backfill).
    A3 = ('        _set_wave(2)\n'
          '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n')
    A3X = A3.replace('\n', eol2b)
    assert t2b.count(A3X) == 1, f'selftest anchor not unique: {t2b.count(A3X)}'
    NEW3 = ('        _set_wave(2)\n'
            '\n'
            + LEG108
            + '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n')
    t2b = rep(t2b, A3, NEW3, eol2b, 'n1-leg108')
    save(FP2, t2b)
    print('edit3 selftest W108 leg landed (insert before T-141 selftest lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment ----------------------
t2c, eol2c = load(FP2)
if '+ W108 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('          "R250), law sec.4 W107 row, r587 bm-a] "\n'
          '          "+ T-141 s2 ')
    SEG108 = ('          "R250), law sec.4 W107 row, r587 bm-a] "\n'
              '          "+ W108 materializer face [same guard set, dep=W17..W102 "\n'
              '          "outputs ALL PRESENT (landed chain head 588,948 = W102 "\n'
              '          "bm-c r378 one-pass, K=222,320; FIVE in-flight upstream "\n'
              '          "seats W103 bm-b + W104 bm-a + W105 bm-c + W106 bm-b burned-"\n'
              '          "unfinalized + W107 bm-a fresh-freeze burn pending -- "\n'
              '          "FAIL-CLOSED r307 at run time), NINETY-EIGHTH ENGINE-OWNED "\n'
              '          "WAVE BY MACHINE-DERIVE (engine_owner rows 97 + candidate) "\n'
              '          "bm-c\'s thirty-second owned claim per machine-derive "\n'
              '          "(engine_owner==bm-c rows 31 + candidate), engine_owner=bm-c "\n'
              '          "per engine de-throttle law O-20261001-2355 sec.2 own-"\n'
              '          "continuous-series (wave 108 = first FREE number after the "\n'
              '          "REGISTERED W107 row, SINGLE STATE zero seat gap; seat-time "\n'
              '          "vs freeze-time tenses converge identical bands per the W106 "\n'
              '          "r585 precedent: seat published=reserved MSG-20261002-1804-"\n'
              '          "bmc pushed to origin ed44e0857 BEFORE this freeze, r565 "\n'
              '          "law, when W107 was published-unregistered skip-past-"\n'
              '          "published hops 1/1 projection; at freeze W107 registered -> "\n'
              '          "arithmetic continuation hops 0/0), A=arithmetic continuation "\n'
              '          "from the registered W107 A tail (259_004..261_003 CLEAN "\n'
              '          "hops=0) + B=arithmetic continuation from the registered "\n'
              '          "W107 B tail (60_601..60_800 CLEAN hops=0; dual-state ADMIT "\n'
              '          "receipt results/_r378bmc_w108_band_gate.py; W109+ projection "\n'
              '          "A 261_004..263_003 CLEAN / B 60_801..61_000 REFUSED "\n'
              '          "[61_000] disclosed for the next freezer; not a free pick -- "\n'
              '          "R250), N3-R1 used-seed leg, probe-seed cluster leg, W107 "\n'
              '          "band disjointness leg (registered r518-1 lineage), law "\n'
              '          "sec.4 W108 row, r378 bm-c] "\n'
              '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG108, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W108 segment landed (insert after W107 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W108 row ---------------------
ROW108 = """
- N1 波108（r378 bm-c 冻·prereg 时展行）：**第九十八枚引擎波·bm-c 第三十二枚自有波〔机面 derive：engine_owner 行 97+本候选／engine_owner==bm-c 行 31+本候选·r359 律计数面以 gate 机输出为准〕**·engine_owner=bm-c·SATURATION_ENGINE_LAW §1/§2 同 W10-W107 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-c 实例=常驻架构 v0.4 mtime-reload——冻结 commit 后下一 tick 重读活树自见新行自燃·免杀重启免做·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 108=注册表 W107 行〔bm-a r587〕后首个自由号·单态零席位空档**·**席位公示=MSG-20261002-1804-bmc**〔published=reserved r518-① 律·先于冻结 commit 推 origin ed44e0857=r565 早可见性律〕·**席位时态注记（W106 r585 先例逐字族）**：席位公示窗（18:04 推送）W107 尚未注册→席位文案=skip-past-published 单席位链 hops 1/1 投影；冻结窗 W107 已由 bm-a r587 冻结注册→**冻结态=单态算术续带 hops 0/0·两读法带位逐位恒同（确定性收敛·无分叉面·F-20261002-03 不触发）**〕·本窗实况=**W102 finalize 已落账（净链头 588,948·K=222,320 合并池·bm-c r378 one-pass·commit 5c5541157）+五在飞上游席（W103 bm-b 12/12 烧毕 finalize 待+W104 bm-a 12/12 烧毕 finalize 待+W105 bm-c 12/12 烧毕 finalize 待+W106 bm-b 12/12 烧毕 finalize 待+W107 bm-a 新冻烧录待启）=本波 finalize 链序前置在飞（跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**·**带位（r378 机闸 derive 律·活注册表机证·ADMIT 回执=results/_r378bmc_w108_band_gate.py rc0 实跑·双态收敛门〔state A 席位窗 skip-past-published/state B 冻结窗单态算术——两态全跑〕·hops A=0/B=0〔冻结态〕）**：**A-ext seed=259_004..261_003**（**A 面算术续带**==W107 行 A 尾 259_003+1 起·步长 2_000·**CLEAN 零拒绝点**）；**B-ext exit seed=60_601..60_800**（**B 面算术续带**==W107 行 B 尾 60_600+1 起·步长 200·**CLEAN 零拒绝点**；双侧算术续带 W92 r370/W100 r583/W102 r375/W103 r584/W106 r585 先例族；与 bm-a W107 席 MSG W108+ 投影披露逐位恒同〔r565 双源交叉〕·本波 gate 机闸独立 derive 非 prose 转抄）。R250：W108 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W108 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W108_PREREG.md（冻结件·锚=W102 finalize 实测值〔锚滚动律自 W99 滚动至 W102·跨 W100/W101/W102 三落账窗·r576 锚滚律〕）·**W109+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 261_004..263_003 **CLEAN**；B 60_801..61_000 **REFUSED [61_000]**（SEED_REGISTRY 拒点→W109 B 侧 D-20261002-05 钉死律 past-hit restart 61_001 起投影·命中位形待 W109 gate 机导定谳）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce2108\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW108.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W108 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    108: {"a": (259_004') == 1, 'FIX-B FAIL: W108 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W108"') == 1, 'FIX-B FAIL: W108 config not exactly once'
for w in range(58, 108):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W108 materializer face') == 2, \
    'FIX-B FAIL: W108 leg+summary must be exactly 2'
for w in range(48, 108):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce2108\uff08') == 1, 'FIX-B FAIL: canon W108 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W108 added per face')

# ---------------- AST gate (r580/r581 lesson: mandatory post-edit) -------------
for fp in (FP1, FP2):
    ast.parse(open(fp, 'rb').read().decode('utf-8'))
print('AST gate: both py faces parse clean')

# ---------------- FIX-C: pure-insertion delta vs origin ------------------------
for p in TARGETS:
    out = git('diff', 'origin/main', '--numstat', '--', p).decode('utf-8').strip()
    if not out:
        sys.exit(f'FIX-C FAIL: no diff shown for {p} (edits missing?)')
    for line in out.splitlines():
        add, dele, path = line.split('\t')
        assert int(dele) == 0, f'FIX-C FAIL: {p} shows {dele} deleted lines ' \
                               f'(pure insertion violated -- r519 content-variant abort)'
        print(f'FIX-C: {p} +{add} -0 (pure insertion)')
print('FREEZE_EDITS_OK 108')
