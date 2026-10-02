# -*- coding: utf-8 -*-
"""r589 bm-a W110 freeze edits -- five-face registration (copy-adapt
r587bma W107 family; MSG INSERT-NOT-REPLACE hardening).

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED rows (W109 bm-b r587
  freeze f077ae11b); every registered row signature survives exactly;
  exactly one new W110 signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.
AST gate (r580/r581 lesson): post-edit ast.parse on both py faces.

W110 = ONE HUNDREDTH engine wave by MACHINE-DERIVE (engine_owner rows 99 +
candidate), bm-a's THIRTY-FIRST owned (engine_owner==bm-a rows 30 +
candidate). First free number after the REGISTERED W109 row (bm-b r587
freeze f077ae11b) -- SINGLE STATE zero seat gap (W2..W109 all registered).
Seat published=reserved MSG-20261002-1829-bma pushed to origin f457e1c4f
BEFORE this freeze (r565 early-visibility law); seat-window r588 and
freeze-window r589 gate runs bitwise identical (re-run this window), no
fork face.
Bands (both sides arithmetic continuation from the registered W109 tails):
  A 263_004..265_003 (W109 A tail 263_003 + 1, stride 2_000) hops=0.
  B 61_201..61_400   (W109 B tail 61_200 + 1, stride 200)   hops=0.
  ADMIT receipt results/_r588bma_w110_band_gate.py rc0 (re-run r589
  freeze window); banned gate ADMIT 0 matched (W110 prereg sec 0.5).
W105 finalize LANDED before this freeze (chain head 595,548, K=228,920 =
bm-c r379 one-pass). FOUR in-flight upstream seats (W106 bm-b + W107 bm-a
+ W108 bm-c burned-unfinalized + W109 bm-b frozen-burn-in-flight) --
finalize merge loop stays FAIL-CLOSED r307 at run time.
W111+ projection: A 265_004..267_003 CLEAN / B 61_401..61_600 CLEAN
(next freezer re-derives, never transcribes).
"""
import subprocess, sys, os, ast
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

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

# ---------------- survival baseline (FIX-B) ------------------------------------
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 110))
pf0 = load(os.path.join(REPO, 'scripts', 'perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts', 'perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research', 'PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 110)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 110)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[110] ---------------------
FP1 = os.path.join(REPO, 'scripts', 'perpetual_faces.py')
t1, eol1 = load(FP1)
if '110: {"a": (263_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    109: {"a": (261_004, 263_003), "b_exit": (61_001, 61_200),\n'
          '         "engine_owner": "bm-b"},\n'
          '}\n')
    NEW = ('    109: {"a": (261_004, 263_003), "b_exit": (61_001, 61_200),\n'
           '         "engine_owner": "bm-b"},\n'
           '    # ONE HUNDREDTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r589 bm-a\n'
           '    # freeze): engine_owner rows 99 + candidate; bm-a\'s thirty-first\n'
           '    # owned per machine-derive (engine_owner==bm-a rows 30 +\n'
           '    # candidate). Wave 110 = first free number after the REGISTERED\n'
           '    # W109 row (bm-b r587 freeze f077ae11b) -- SINGLE STATE zero\n'
           '    # seat gap (W2..W109 all registered). Seat published=reserved\n'
           '    # MSG-20261002-1829-bma pushed to the origin f457e1c4f BEFORE\n'
           '    # this freeze per r565 early-visibility law; seat-window r588\n'
           '    # and freeze-window r589 band-gate runs bitwise identical, no\n'
           '    # fork face.\n'
           '    # W105 finalize LANDED before this freeze (landed chain head\n'
           '    # 595,548 = bm-c r379 one-pass; K=228,920). FOUR in-flight\n'
           '    # upstream seats (W106 bm-b + W107 bm-a + W108 bm-c\n'
           '    # burned-unfinalized + W109 bm-b frozen-burn-in-flight) -- the\n'
           '    # finalize merge loop stays FAIL-CLOSED r307 at run time.\n'
           '    # A = arithmetic continuation from the registered W109 A tail:\n'
           '    # 263_004..265_003 CLEAN hops=0. B = arithmetic continuation\n'
           '    # from the registered W109 B tail: 61_201..61_400 CLEAN hops=0\n'
           '    # (both sides arithmetic continuation, W92 r370 / W100 r583 /\n'
           '    # W103 r584 / W106 r585 / W107 r587 precedent family). ADMIT\n'
           '    # receipt results/_r588bma_w110_band_gate.py rc0 (re-run this\n'
           '    # freeze window, bitwise identical to the r588 seat-window\n'
           '    # run); live SEED_REGISTRY + probe cluster 95_000..95_003 r335\n'
           '    # leg + N3-R1 used-seed band 70_000..70_005 MSG-183x r529 leg.\n'
           '    # W111+ projection: A 265_004..267_003 CLEAN; B 61_401..61_600\n'
           '    # CLEAN (next freezer must re-derive, never transcribe).\n'
           '    # NOT a re-pick (R250: W110 bands were never assigned).\n'
           '    110: {"a": (263_004, 265_003), "b_exit": (61_201, 61_400),\n'
           '         "engine_owner": "bm-a"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[110] landed (anchor=W109 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[110] -------------
FP2 = os.path.join(REPO, 'scripts', 'perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '110: {"batch": "PERPETUAL-N1-W110"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w109", "out_name": "n1_w109_results.json",\n'
          '                            "engine_owner": "bm-b"},\n')
    NEW2 = A2 + (
        '                       110: {"batch": "PERPETUAL-N1-W110",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W110_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; ONE HUNDREDTH ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 99 + candidate), own-series "\n'
        '                                       "continuation per O-20261001-2355 sec.2 (first-free-number "\n'
        '                                       "law after the REGISTERED W109 row bm-b r587 freeze "\n'
        '                                       "f077ae11b, SINGLE STATE zero seat gap W2..W109 all "\n'
        '                                       "registered; seat published=reserved MSG-20261002-1829-bma "\n'
        '                                       "PUSHED to origin f457e1c4f BEFORE this freeze per r565 "\n'
        '                                       "early-visibility law; seat-window r588 and freeze-window "\n'
        '                                       "r589 band-gate runs bitwise identical, no fork face), "\n'
        '                                       "engine_owner=bm-a, wave 110: A = arithmetic continuation "\n'
        '                                       "from the registered W109 A tail (263_004..265_003 CLEAN "\n'
        '                                       "hops=0) + B = arithmetic continuation from the registered "\n'
        '                                       "W109 B tail (61_201..61_400 CLEAN hops=0; ADMIT receipt "\n'
        '                                       "results/_r588bma_w110_band_gate.py; W111+ projection: "\n'
        '                                       "A 265_004..267_003 CLEAN / B 61_401..61_600 CLEAN for "\n'
        '                                       "the next freezer); W105 finalize LANDED before this "\n'
        '                                       "freeze (chain head 595,548, K=228,920, bm-c r379 "\n'
        '                                       "one-pass) + FOUR in-flight upstream seats W106 bm-b + "\n'
        '                                       "W107 bm-a + W108 bm-c + W109 bm-b "\n'
        '                                       "registered-unfinalized -- finalize merge loop stays "\n'
        '                                       "FAIL-CLOSED r307 at run time)"),\n'
        '                            "a_seed_base": 263_004,        # law sec.4 W110 A: 263_004..265_003 (arithmetic continuation from the registered W109 A tail)\n'
        '                            "b_exit_seed_base": 61_201,   # law sec.4 W110 B: 61_201..61_400 (arithmetic continuation from the registered W109 B tail)\n'
        '                            "shard_subdir": "n1_w110", "out_name": "n1_w110_results.json",\n'
        '                            "engine_owner": "bm-a"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[110] landed (anchor=W109 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W110 leg -------------
LEG110 = '''
    # --- W110 materializer face (r589 bm-a freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-a's
    #     thirty-first owned per machine-derive (engine_owner==bm-a
    #     rows 30 + candidate); wave 110 = first free number after
    #     the REGISTERED W109 row (bm-b r587 freeze f077ae11b) --
    #     SINGLE STATE zero seat gap (W2..W109 all registered).
    #     Seat published=reserved MSG-20261002-1829-bma pushed to
    #     the origin f457e1c4f BEFORE this freeze, r565 law;
    #     seat-window r588 and freeze-window r589 band-gate runs
    #     bitwise identical, no fork face. ONE HUNDREDTH engine
    #     wave BY MACHINE-DERIVE (engine_owner rows 99 + candidate;
    #     gate leg0 machine output governs per r359 law). W105
    #     finalize LANDED (chain head 595,548, K=228,920, bm-c r379
    #     one-pass) + FOUR in-flight upstream seats W106 bm-b +
    #     W107 bm-a + W108 bm-c + W109 bm-b registered-unfinalized
    #     -- FAIL-CLOSED r307 at run time. ADMIT receipt
    #     results/_r588bma_w110_band_gate.py; not a re-pick
    #     (R250: W110 bands were never assigned).
    _set_wave(110)
    try:
        assert WAVE_CONFIGS[110]["a_seed_base"] == pf.N1_BANDS[110]["a"][0], \\
            "W110 A band drift vs law mirror"
        assert WAVE_CONFIGS[110]["b_exit_seed_base"] == \\
            pf.N1_BANDS[110]["b_exit"][0], "W110 B band drift vs law mirror"
        assert WAVE_CONFIGS[110].get("engine_owner") == \\
            pf.N1_BANDS[110].get("engine_owner") == "bm-a", \\
            "W110 engine_owner drift (law mirror parity)"
        w110_a = {A_SEED_BASE + j for j in range(A_N)}
        w110_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w110_a & w110_b), "W110 A/B band overlap"
        assert not (w110_a & reg_ints) and not (w110_b & reg_ints), \\
            "W110 hits SEED_REGISTRY"
        for nm, band in (("A", w110_a), ("B", w110_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W110 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W110 {nm} hits W1"
            assert not (band & probes), f"W110 {nm} hits probe seeds"
        # registered row parity (r307 pinned constants, recent estate)
        assert pf.N1_BANDS[104] == {"a": (251_004, 253_003),
                                    "b_exit": (59_601, 59_800),
                                    "engine_owner": "bm-a"}, \\
            "registered W104 row parity drift (r307; bm-a r586 union)"
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
        assert pf.N1_BANDS[108] == {"a": (259_004, 261_003),
                                    "b_exit": (60_601, 60_800),
                                    "engine_owner": "bm-c"}, \\
            "registered W108 row parity drift (r307; bm-c r378)"
        assert pf.N1_BANDS[109] == {"a": (261_004, 263_003),
                                    "b_exit": (61_001, 61_200),
                                    "engine_owner": "bm-b"}, \\
            "registered W109 row parity drift (r307; bm-b r587)"
        # prior-wave disjointness W2..W109 (single state: all
        # registered, dynamic registry derive, r511 law)
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 110):
            assert not (w110_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W110 A hits W{wprev}"
            assert not (w110_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W110 B hits W{wprev}"
        n3r1_used110 = set(range(70_000, 70_006))
        assert not (w110_a & n3r1_used110) and not (w110_b & n3r1_used110), \\
            "W110 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        assert not (w110_a & lfc_actual12) and not (w110_b & lfc_actual12), \\
            "W110 bands must clear the lfc actual draw range"
        assert not (w110_a & options_actual12) and \\
            not (w110_b & options_actual12), \\
            "W110 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W110 row, r589): both sides arithmetic
        # continuation from the registered W109 tails, zero skips.
        assert WAVE_CONFIGS[110]["a_seed_base"] == 263_004 == 263_003 + 1, (
            "W110 A must be the arithmetic continuation past the W109 "
            "registered A band tail")
        arith_a110 = set(range(263_004, 265_004))
        assert not (arith_a110 & reg_ints), \\
            "W110 A window must be CLEAN (arithmetic ADMIT face)"
        assert WAVE_CONFIGS[110]["b_exit_seed_base"] == 61_201 == 61_200 + 1, (
            "W110 B must be the arithmetic continuation past the W109 "
            "registered B band tail")
        arith_b110 = set(range(61_201, 61_401))
        assert not (arith_b110 & reg_ints), \\
            "W110 B window must be CLEAN (arithmetic ADMIT face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W110-SHARD-0",
                                          "n1w110-0of12"), "W110 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W110-SHARD-11",
                                           "n1w110-11of12")
        assert SHARD_DIR.endswith("n1_w110") and OUT.endswith(
            "n1_w110_results.json"), "W110 path drift"
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 110):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W110 shard dir collides with W{wprev}"
        # W110 finalize cumulative deps: W17..W105 outputs ALL PRESENT
        # (landed chain head 595,548 = W105 bm-c r379; W106/W107/W108/
        # W109 registered with finalizes NOT landed -- in-flight
        # upstream seats, honest note; the finalize merge loop derives
        # the wave set from registry keys at run time and stays
        # FAIL-CLOSED, r307 law).
        for _depw in range(17, 106):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W110 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): every
        # registered wave below 110 composes; wave 15 excluded by
        # design; SINGLE STATE (W2..W109 all registered -- no
        # two-state seat disclosure needed at this freeze).
        assert sorted(w for w in WAVE_CONFIGS if w < 110) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 110)], \\
            "W110 prior-wave set must derive from registry keys (no 15; " \\
            "W2..W109 registered single state)"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W110_PREREG.md")), \\
            "W110 per-wave prereg missing (materializer requirement)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W110 materializer face' in t2b:
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
            + LEG110
            + '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n')
    t2b = rep(t2b, A3, NEW3, eol2b, 'n1-leg110')
    save(FP2, t2b)
    print('edit3 selftest W110 leg landed (insert before T-141 selftest lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment -----------------------
t2c, eol2c = load(FP2)
if '+ W110 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('          "R250), law sec.4 W109 row, r587 bm-b] "\n'
          '          "+ T-141 s2 ')
    SEG110 = ('          "R250), law sec.4 W109 row, r587 bm-b] "\n'
              '          "+ W110 materializer face [same guard set, dep=W17..W105 "\n'
              '          "outputs ALL PRESENT (landed chain head 595,548 = W105 "\n'
              '          "bm-c r379 one-pass, K=228,920; FOUR in-flight upstream "\n'
              '          "seats W106 bm-b + W107 bm-a + W108 bm-c + W109 bm-b "\n'
              '          "registered-unfinalized -- FAIL-CLOSED r307 at run "\n'
              '          "time), ONE HUNDREDTH ENGINE-OWNED WAVE BY MACHINE-"\n'
              '          "DERIVE (engine_owner rows 99 + candidate) bm-a\'s "\n'
              '          "thirty-first owned claim per machine-derive "\n'
              '          "(engine_owner==bm-a rows 30 + candidate), engine_owner=bm-a "\n'
              '          "per engine de-throttle law O-20261001-2355 sec.2 own-"\n'
              '          "continuous-series (wave 110 = first FREE number after the "\n'
              '          "REGISTERED W109 row bm-b r587 freeze f077ae11b, SINGLE "\n'
              '          "STATE zero seat gap W2..W109 all registered; seat "\n'
              '          "published=reserved MSG-20261002-1829-bma pushed to "\n'
              '          "origin f457e1c4f BEFORE this freeze, r565 law; seat-"\n'
              '          "window r588 and freeze-window r589 band-gate runs "\n'
              '          "bitwise identical, no fork face), A=arithmetic "\n'
              '          "continuation from the registered W109 A tail "\n'
              '          "(263_004..265_003 CLEAN hops=0) + B=arithmetic "\n'
              '          "continuation from the registered W109 B tail "\n'
              '          "(61_201..61_400 CLEAN hops=0; ADMIT receipt "\n'
              '          "results/_r588bma_w110_band_gate.py; W111+ projection "\n'
              '          "A 265_004..267_003 CLEAN / B 61_401..61_600 CLEAN "\n'
              '          "disclosed for the next freezer; not a free pick -- "\n'
              '          "R250), law sec.4 W110 row, r589 bm-a] "\n'
              '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG110, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W110 segment landed (insert after W109 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W110 row --------------------
ROW110 = """
- N1 \u6ce2110\uff08r589 bm-a \u51bb\u00b7prereg \u65f6\u5c55\u884c\uff09\uff1a**\u7b2c\u4e00\u767e\u679a\u5f15\u64ce\u6ce2\u00b7bm-a \u7b2c\u4e09\u5341\u4e00\u679a\u81ea\u6709\u6ce2\u3014\u673a\u9762 derive\uff1aengine_owner \u884c 99+\u672c\u5019\u9009\uff0fengine_owner==bm-a \u884c 30+\u672c\u5019\u9009\u00b7r359 \u5f8b\u8ba1\u6570\u9762\u4ee5 gate \u673a\u8f93\u51fa\u4e3a\u51c6\u3015**\u00b7engine_owner=bm-a\u00b7SATURATION_ENGINE_LAW \u00a71/\u00a72 \u540c W10-W109 \u5408\u540c\u00b7\u4e0d\u5165\u6c60\u00b7\u514d\u9884\u6ce8\u518c\u7a0e\u00b7cmd_supply \u8df3\u8fc7\u95e8\u00b7**\u5f15\u64ce\u53bb\u8282\u6d41\u4ee4 O-20261001-2355 \u00a7\u4e8c\u81ea\u6709\u8fde\u7eed\u7cfb\u5217**\u00b7\u3010\u672c\u673a bm-a \u5b9e\u4f8b=tick \u67b6\u6784\u2014\u2014\u51bb\u7ed3 commit \u540e\u4e0b\u4e00 tick \u65b0\u8fdb\u7a0b\u8bfb\u6d3b\u5de5\u4f5c\u6811\u81ea\u89c1\u65b0\u884c=\u514d\u6740\u91cd\u542f\u514d\u505a\u00b7\u70b9\u706b\u9a8c\u8bc1\u552f\u4e00\u8bc1\u636e=\u4ea7\u7269\u589e\u957f\u9762 r325 \u5f8b\u3011\u00b7\u3010never-dry \u4f9b\u7ed9\u5f8b\u5e38\u8bbe\u6b65\u00b7**\u6ce2\u53f7 110=\u6ce8\u518c\u8868 W109 \u884c\u540e\u9996\u4e2a\u81ea\u7531\u53f7\u00b7\u5355\u6001\u96f6\u5e2d\u4f4d\u7a7a\u6863**\uff08W104=bm-a r586 union 48f6f2ff1+W105=bm-c r376 freeze f2db133c5+W106=bm-b r585 freeze d6b2952e3+W107=bm-a r587 freeze a554dedd3+W108=bm-c r378 freeze 3a3c51b73+W109=bm-b r587 freeze f077ae11b \u5747\u5df2\u6ce8\u518c\u00b7\u65e0 skip-past-published \u94fe\u9762\uff09\u00b7**\u5e2d\u4f4d\u516c\u793a=MSG-20261002-1829-bma**\u3014published=reserved r518-\u2460 \u5f8b\u00b7\u5148\u4e8e\u51bb\u7ed3 commit \u63a8 origin f457e1c4f=r565 \u65e9\u53ef\u89c1\u6027\u5f8b\u00b7\u5e2d\u4f4d\u7a97 r588 \u4e0e\u51bb\u7ed3\u7a97 r589 \u53cc\u8dd1 band gate derive \u9010\u4f4d\u6052\u7b49\u00b7\u96f6\u5206\u53c9\u9762\u3011\u3011\u00b7\u672c\u7a97\u5b9e\u51b5=**W105 finalize \u5df2\u843d\u8d26\uff08\u51c0\u94fe\u5934 595,548\u00b7K=228,920 \u5408\u5e76\u6c60\u00b7bm-c r379 one-pass\uff09+\u56db\u5728\u98de\u4e0a\u6e38\u5e2d\uff08W106 bm-b+W107 bm-a+W108 bm-c+W109 bm-b registered \u70e7\u6bd5\uff0f\u5728\u98de finalize \u5f85\uff09=\u672c\u6ce2 finalize \u94fe\u5e8f\u524d\u7f6e\u5728\u98de\uff08\u8dd1\u65f6\u6309 registry \u952e derive \u590d\u6838\u00b7FAIL-CLOSED r307 \u4e24\u6001\u5f8b\u6052\u5728\uff09**\u00b7**\u5e26\u4f4d\uff08r535 \u673a\u95f8 derive \u5f8b\u00b7\u6d3b\u6ce8\u518c\u8868\u673a\u8bc1\u00b7\u5355\u6001\u6536\u655b\u95e8\u00b7ADMIT \u56de\u6267=results/_r588bma_w110_band_gate.py rc0 \u5b9e\u8dd1\u00b7\u5e2d\u4f4d\u7a97 r588+\u51bb\u7ed3\u7a97 r589 \u53cc\u8dd1\u6052\u7b49\u00b7hops A=0/B=0\uff09**\uff1a**A-ext seed=263_004..265_003**\uff08==W109 \u884c A \u5c3e 263_003+1 \u8d77\u7b97\u672f\u7eed\u5e26\u00b7\u6b65\u957f 2_000\u00b7**CLEAN \u96f6\u62d2\u7edd\u70b9**\uff09\uff1b**B-ext exit seed=61_201..61_400**\uff08==W109 \u884c B \u5c3e 61_200+1 \u8d77\u7b97\u672f\u7eed\u5e26\u00b7\u6b65\u957f 200\u00b7**CLEAN \u96f6\u62d2\u7edd\u70b9**\u00b7\u53cc\u4fa7\u7b97\u672f\u7eed\u5e26=W92 r370/W100 r583/W103 r584/W106 r585/W107 r587 \u5148\u4f8b\u65cf\uff09\u3002R250\uff1aW110 \u5e26\u4ece\u672a\u6307\u6d3e\u00b7\u6d4b\u91cf\u9762\u96f6\u7ed3\u679c\u53ef\u9493\u00b7banned gate ADMIT 0 matched\uff08W110 prereg \u00a70.5\uff09\u00b7per-wave prereg=research/PERPETUAL_N1_W110_PREREG.md\uff08\u51bb\u7ed3\u4ef6\u00b7\u9528=W105 finalize \u5b9e\u6d4b\u503c\u3014merged mu \u22120.09270678970819501\u00b7K=228,920\u00b7K-lift \u22120.0002\u00b7A-p95 0.3038\u00b7\u9528\u6eda\u52a8\u5f8b\u81ea W103 \u6eda\u52a8\u81f3 W105 \u8de8 W104/W105 \u53cc\u843d\u8d26\u7a97\u00b7r576 \u9528\u6eda\u5f8b\u3015\uff09\u00b7**W111+ \u6295\u5f71\uff08gate \u673a\u8bc1\u00b7\u4e0b\u6ce2\u51bb\u7ed3\u65b9\u5fc5\u590d\u6838\u975e\u8f6c\u6284\uff09**\uff1aA 265_004..267_003 **CLEAN**\uff1bB 61_401..61_600 **CLEAN**\uff08\u4e0b\u6ce2\u6309\u6cd5\u5178 \u00a74 \u8868\u5c3e+\u5168 registry \u91cd derive\uff09\u3002
"""
FP4 = os.path.join(REPO, 'research', 'PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce2110\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW110.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W110 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    110: {"a": (263_004') == 1, 'FIX-B FAIL: W110 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W110"') == 1, 'FIX-B FAIL: W110 config not exactly once'
for w in range(58, 110):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W110 materializer face') == 2, \
    'FIX-B FAIL: W110 leg+summary must be exactly 2'
for w in range(48, 110):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce2110\uff08') == 1, 'FIX-B FAIL: canon W110 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W110 added per face')

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
print('FREEZE_EDITS_OK 110')
