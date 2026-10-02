# -*- coding: utf-8 -*-
"""r587 bm-b W109 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening.

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED rows (W104 bm-a union
  r586 + W105 bm-c r376 + W106 bm-b r585 + W107 bm-a r587 + W108 bm-c r378);
  every registered row signature survives exactly; exactly one new W109
  signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.
AST gate (r580/r581 lesson): post-edit ast.parse on both py faces.

W109 = NINETY-NINTH engine wave by MACHINE-DERIVE (engine_owner rows 98 +
candidate; gate leg0 machine output governs per r359 law), bm-b's
THIRTY-SEVENTH owned (engine_owner==bm-b rows 36 + candidate).
First free number after the REGISTERED W108 row (bm-c r378 freeze 3a3c51b73)
-- SINGLE STATE zero seat gap (W2..W108 all registered).
Seat published=reserved MSG-20261002-1817-bmb rev.B pushed to origin 99e29877c
BEFORE this freeze (r565 early-visibility law). Rev.B: first-draft B
projection 60_801..61_000 corrected PRE-PUSH (origin advance caught by the
pre-push claw, r374 fork artifact; bm-c W108 freeze landed mid-window with
gate-tail disclosure B REFUSED [61_000]; own probe confirmed refusal point =
SEED_REGISTRY wild_route_s1=61_000; zero prior visibility).
Bands:
  A 261_004..263_003 (W108 A tail 261_003 + 1, stride 2_000) hops=0 CLEAN.
  B 61_001..61_200   (arithmetic window 60_801..61_000 hits SEED_REGISTRY
     wild_route_s1=61_000 -> jump to first clean window per law sec.4 W5
     value-collision precedent, hops=1, refusal facts machine-disclosed).
  ADMIT receipt results/_r587bmb_w109_band_gate.py rc0; banned gate ADMIT 0.
W103 finalize LANDED before this freeze (chain head 591,148, K=224,520 =
bm-b r586 one-pass). FIVE in-flight upstream seats (W104 bm-a + W105 bm-c +
W106 bm-b + W107 bm-a + W108 bm-c registered-unfinalized) -- finalize merge
loop stays FAIL-CLOSED r307 at run time.
W110+ projection: A 263_004..265_003 CLEAN / B 61_201..61_400 CLEAN
(next freezer re-derives, never transcribes).
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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 109))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 109)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 109)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[109] ---------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '109: {"a": (261_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    108: {"a": (259_004, 261_003), "b_exit": (60_601, 60_800),\n'
          '         "engine_owner": "bm-c"},\n'
          '}\n')
    NEW = ('    108: {"a": (259_004, 261_003), "b_exit": (60_601, 60_800),\n'
           '         "engine_owner": "bm-c"},\n'
           '    # NINETY-NINTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r587 bm-b\n'
           '    # freeze): engine_owner rows 98 + candidate; bm-b\'s thirty-\n'
           '    # seventh owned per machine-derive (engine_owner==bm-b rows 36 +\n'
           '    # candidate). Wave 109 = first free number after the REGISTERED\n'
           '    # W108 row (bm-c r378 freeze 3a3c51b73) -- SINGLE STATE zero seat\n'
           '    # gap (W2..W108 all registered). Seat published=reserved\n'
           '    # MSG-20261002-1817-bmb rev.B pushed to origin 99e29877c BEFORE\n'
           '    # this freeze per r565 early-visibility law. Rev.B: first-draft\n'
           '    # B projection 60_801..61_000 corrected PRE-PUSH (origin advance\n'
           '    # caught by pre-push claw r374 fork artifact; bm-c W108 freeze\n'
           '    # landed mid-window; own probe confirmed refusal point =\n'
           '    # SEED_REGISTRY wild_route_s1=61_000; zero prior visibility).\n'
           '    # W103 finalize LANDED before this freeze (chain head 591,148,\n'
           '    # K=224,520 = bm-b r586 one-pass). FIVE in-flight upstream seats\n'
           '    # (W104 bm-a + W105 bm-c + W106 bm-b + W107 bm-a + W108 bm-c\n'
           '    # registered-unfinalized) -- finalize merge loop stays\n'
           '    # FAIL-CLOSED r307 at run time.\n'
           '    # A = arithmetic continuation from the registered W108 A tail:\n'
           '    # 261_004..263_003 CLEAN hops=0. B = VALUE-COLLISION JUMP:\n'
           '    # arithmetic window 60_801..61_000 hits SEED_REGISTRY\n'
           '    # wild_route_s1=61_000 -> first clean window 61_001..61_200 hops=1\n'
           '    # per law sec.4 W5 precedent family (machine gate disjoint law\n'
           '    # over stride convention). ADMIT receipt\n'
           '    # results/_r587bmb_w109_band_gate.py rc0; live SEED_REGISTRY\n'
           '    # + probe cluster 95_000..95_003 r335 leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 leg.\n'
           '    # W110+ projection: A 263_004..265_003 CLEAN; B 61_201..61_400\n'
           '    # CLEAN (next freezer must re-derive, never transcribe).\n'
           '    # NOT a re-pick (R250: W109 bands were never assigned).\n'
           '    109: {"a": (261_004, 263_003), "b_exit": (61_001, 61_200),\n'
           '         "engine_owner": "bm-b"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[109] landed (anchor=W108 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[109] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '109: {"batch": "PERPETUAL-N1-W109"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w108", "out_name": "n1_w108_results.json",\n'
          '                            "engine_owner": "bm-c"},\n')
    NEW2 = A2 + (
        '                       109: {"batch": "PERPETUAL-N1-W109",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W109_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; NINETY-NINTH ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 98 + candidate), own-series "\n'
        '                                       "continuation per O-20261001-2355 sec.2 (first-free-number "\n'
        '                                       "law after the REGISTERED W108 row bm-c r378 freeze 3a3c51b73, "\n'
        '                                       "SINGLE STATE zero seat gap W2..W108 all registered; seat "\n'
        '                                       "published=reserved MSG-20261002-1817-bmb rev.B PUSHED to "\n'
        '                                       "origin 99e29877c BEFORE this freeze per r565 "\n'
        '                                       "early-visibility law; rev.B = first-draft B projection "\n'
        '                                       "60_801..61_000 corrected pre-push after the mid-window "\n'
        '                                       "bm-c W108 advance, refusal point SEED_REGISTRY "\n'
        '                                       "wild_route_s1=61_000 own-probe confirmed, zero prior "\n'
        '                                       "visibility), engine_owner=bm-b, wave 109: A = "\n'
        '                                       "arithmetic continuation from the registered W108 A tail "\n'
        '                                       "(261_004..263_003 CLEAN hops=0) + B = VALUE-COLLISION JUMP "\n'
        '                                       "(arithmetic window 60_801..61_000 hits SEED_REGISTRY "\n'
        '                                       "wild_route_s1=61_000 -> first clean window 61_001..61_200 "\n'
        '                                       "hops=1 per law sec.4 W5 precedent family; ADMIT receipt "\n'
        '                                       "results/_r587bmb_w109_band_gate.py; W110+ projection: "\n'
        '                                       "A 263_004..265_003 CLEAN / B 61_201..61_400 CLEAN for "\n'
        '                                       "the next freezer); W103 finalize LANDED before this freeze "\n'
        '                                       "(chain head 591,148, K=224,520, bm-b r586 one-pass) + "\n'
        '                                       "FIVE in-flight upstream seats W104 bm-a + W105 bm-c + "\n'
        '                                       "W106 bm-b + W107 bm-a + W108 bm-c registered-unfinalized "\n'
        '                                       "-- finalize merge loop stays FAIL-CLOSED r307 at run "\n'
        '                                       "time)"),\n'
        '                            "a_seed_base": 261_004,        # law sec.4 W109 A: 261_004..263_003 (arithmetic continuation from the registered W108 A tail)\n'
        '                            "b_exit_seed_base": 61_001,   # law sec.4 W109 B: 61_001..61_200 (value-collision jump past SEED_REGISTRY wild_route_s1=61_000, W5 precedent)\n'
        '                            "shard_subdir": "n1_w109", "out_name": "n1_w109_results.json",\n'
        '                            "engine_owner": "bm-b"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[109] landed (anchor=W108 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W109 leg --------------
LEG109 = '''
    # --- W109 materializer face (r587 bm-b freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-b's
    #     thirty-seventh owned per machine-derive (engine_owner==bm-b
    #     rows 36 + candidate); wave 109 = first free number after
    #     the REGISTERED W108 row (bm-c r378 freeze 3a3c51b73) --
    #     SINGLE STATE zero seat gap (W2..W108 all registered).
    #     Seat published=reserved MSG-20261002-1817-bmb rev.B pushed
    #     to origin 99e29877c BEFORE this freeze, r565 law; rev.B =
    #     first-draft B projection corrected pre-push (bm-c W108
    #     mid-window advance, refusal point 61_000 own-probe
    #     confirmed, zero prior visibility). NINETY-NINTH engine
    #     wave BY MACHINE-DERIVE (engine_owner rows 98 + candidate;
    #     gate leg0 machine output governs per r359 law). W103
    #     finalize LANDED (chain head 591,148, K=224,520, bm-b r586
    #     one-pass) + FIVE in-flight upstream seats W104 bm-a + W105
    #     bm-c + W106 bm-b + W107 bm-a + W108 bm-c
    #     registered-unfinalized -- FAIL-CLOSED r307 at run time.
    #     ADMIT receipt results/_r587bmb_w109_band_gate.py; not a
    #     re-pick (R250: W109 bands were never assigned).
    _set_wave(109)
    try:
        assert WAVE_CONFIGS[109]["a_seed_base"] == pf.N1_BANDS[109]["a"][0], \\
            "W109 A band drift vs law mirror"
        assert WAVE_CONFIGS[109]["b_exit_seed_base"] == \\
            pf.N1_BANDS[109]["b_exit"][0], "W109 B band drift vs law mirror"
        assert WAVE_CONFIGS[109].get("engine_owner") == \\
            pf.N1_BANDS[109].get("engine_owner") == "bm-b", \\
            "W109 engine_owner drift (law mirror parity)"
        w109_a = {A_SEED_BASE + j for j in range(A_N)}
        w109_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w109_a & w109_b), "W109 A/B band overlap"
        assert not (w109_a & reg_ints) and not (w109_b & reg_ints), \\
            "W109 hits SEED_REGISTRY"
        for nm, band in (("A", w109_a), ("B", w109_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W109 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W109 {nm} hits W1"
            assert not (band & probes), f"W109 {nm} hits probe seeds"
        # registered row parity (r307 pinned constants, recent estate)
        assert pf.N1_BANDS[103] == {"a": (249_004, 251_003),
                                    "b_exit": (59_401, 59_600),
                                    "engine_owner": "bm-b"}, \\
            "registered W103 row parity drift (r307; bm-b r584)"
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
        # prior-wave disjointness W2..W108 (single state: all
        # registered, dynamic registry derive, r511 law)
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 109):
            assert not (w109_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W109 A hits W{wprev}"
            assert not (w109_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W109 B hits W{wprev}"
        n3r1_used109 = set(range(70_000, 70_006))
        assert not (w109_a & n3r1_used109) and not (w109_b & n3r1_used109), \\
            "W109 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        assert not (w109_a & lfc_actual12) and not (w109_b & lfc_actual12), \\
            "W109 bands must clear the lfc actual draw range"
        assert not (w109_a & options_actual12) and \\
            not (w109_b & options_actual12), \\
            "W109 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W109 row, r587): A arithmetic
        # continuation from the registered W108 tails, zero skips;
        # B value-collision jump (W5 precedent family).
        assert WAVE_CONFIGS[109]["a_seed_base"] == 261_004 == 261_003 + 1, (
            "W109 A must be the arithmetic continuation past the W108 "
            "registered A band tail")
        arith_a109 = set(range(261_004, 263_004))
        assert not (arith_a109 & reg_ints), \\
            "W109 A window must be CLEAN (arithmetic ADMIT face)"
        assert WAVE_CONFIGS[109]["b_exit_seed_base"] == 61_001, (
            "W109 B must be the first clean window past the refusal point")
        arith_b109_refused = set(range(60_801, 61_001))
        assert arith_b109_refused & reg_ints, \\
            "W109 B refusal fact missing: arithmetic window 60_801..61_000 "
            "must hit SEED_REGISTRY (wild_route_s1=61_000)"
        assert 61_000 in reg_ints, \\
            "W109 B refusal point 61_000 (wild_route_s1) missing from registry"
        arith_b109 = set(range(61_001, 61_201))
        assert not (arith_b109 & reg_ints), \\
            "W109 B window must be CLEAN (value-collision jump ADMIT face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W109-SHARD-0",
                                          "n1w109-0of12"), "W109 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W109-SHARD-11",
                                           "n1w109-11of12")
        assert SHARD_DIR.endswith("n1_w109") and OUT.endswith(
            "n1_w109_results.json"), "W109 path drift"
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 109):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W109 shard dir collides with W{wprev}"
        # W109 finalize cumulative deps: W17..W103 outputs ALL PRESENT
        # (landed chain head 591,148 = W103 bm-b r586; W104/W105/W106/
        # W107/W108 registered with finalizes NOT landed -- in-flight
        # upstream seats, honest note; the finalize merge loop derives
        # the wave set from registry keys at run time and stays
        # FAIL-CLOSED, r307 law).
        for _depw in range(17, 104):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W109 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): every
        # registered wave below 109 composes; wave 15 excluded by
        # design; SINGLE STATE (W2..W108 all registered -- no
        # two-state seat disclosure needed at this freeze).
        assert sorted(w for w in WAVE_CONFIGS if w < 109) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 109)], \\
            "W109 prior-wave set must derive from registry keys (no 15; " \\
            "W2..W108 registered single state)"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W109_PREREG.md")), \\
            "W109 per-wave prereg missing (materializer requirement)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W109 materializer face' in t2b:
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
            + LEG109
            + '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n')
    t2b = rep(t2b, A3, NEW3, eol2b, 'n1-leg109')
    save(FP2, t2b)
    print('edit3 selftest W109 leg landed (insert before T-141 selftest lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment ----------------------
t2c, eol2c = load(FP2)
if '+ W109 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('          "sec.4 W108 row, r378 bm-c] "\n'
          '          "+ T-141 s2 ')
    SEG109 = ('          "sec.4 W108 row, r378 bm-c] "\n'
              '          "+ W109 materializer face [same guard set, dep=W17..W103 "\n'
              '          "outputs ALL PRESENT (landed chain head 591,148 = W103 "\n'
              '          "bm-b r586 one-pass, K=224,520; FIVE in-flight upstream "\n'
              '          "seats W104 bm-a + W105 bm-c + W106 bm-b + W107 bm-a + "\n'
              '          "W108 bm-c registered-unfinalized -- FAIL-CLOSED r307 "\n'
              '          "at run time), NINETY-NINTH ENGINE-OWNED WAVE BY "\n'
              '          "MACHINE-DERIVE (engine_owner rows 98 + candidate) bm-b\'s "\n'
              '          "thirty-seventh owned claim per machine-derive "\n'
              '          "(engine_owner==bm-b rows 36 + candidate), engine_owner=bm-b "\n'
              '          "per engine de-throttle law O-20261001-2355 sec.2 own-"\n'
              '          "continuous-series (wave 109 = first FREE number after the "\n'
              '          "REGISTERED W108 row bm-c r378 freeze 3a3c51b73, SINGLE "\n'
              '          "STATE zero seat gap W2..W108 all registered; seat "\n'
              '          "published=reserved MSG-20261002-1817-bmb rev.B pushed to "\n'
              '          "origin 99e29877c BEFORE this freeze, r565 law; rev.B = "\n'
              '          "first-draft B projection 60_801..61_000 corrected pre-push "\n'
              '          "after the mid-window bm-c W108 advance, refusal point "\n'
              '          "SEED_REGISTRY wild_route_s1=61_000 own-probe confirmed, "\n'
              '          "zero prior visibility), A=arithmetic continuation from "\n'
              '          "the registered W108 A tail (261_004..263_003 CLEAN hops=0) "\n'
              '          "+ B=VALUE-COLLISION JUMP (arithmetic window 60_801..61_000 "\n'
              '          "hits SEED_REGISTRY wild_route_s1=61_000 -> first clean "\n'
              '          "window 61_001..61_200 hops=1 per law sec.4 W5 precedent "\n'
              '          "family; ADMIT receipt results/_r587bmb_w109_band_gate.py; "\n'
              '          "W110+ projection A 263_004..265_003 CLEAN / B 61_201..61_400 "\n'
              '          "CLEAN disclosed for the next freezer; not a free pick -- "\n'
              '          "R250), law sec.4 W109 row, r587 bm-b] "\n'
              '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG109, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W109 segment landed (insert after W108 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W109 row ---------------------
ROW109 = """
- N1 波109（r587 bm-b 冻·prereg 时展行）：**第九十九枚引擎波·bm-b 第三十七枚自有波〔机面 derive：engine_owner 行 98+本候选／engine_owner==bm-b 行 36+本候选·r359 律计数面以 gate 机输出为准〕**·engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W108 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-b 实例=tick 架构——冻结 commit 后下一 tick 新进程读活工作树自见新行=免杀重启免做·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 109=注册表 W108 行后首个自由号·单态零席位空档**（W104=bm-a r586 union 48f6f2ff1+W105=bm-c r376 freeze f2db133c5+W106=bm-b r585 freeze d6b2952e3+W107=bm-a r587 freeze a554dedd3+W108=bm-c r378 freeze 3a3c51b73 均已注册·无 skip-past-published 链面）·**席位公示=MSG-20261002-1817-bmb rev.B**〔published=reserved r518-① 律·先于冻结 commit 推 origin 99e29877c=r565 早可见性律·**rev.B 披露**：首稿 B 投影 60_801..61_000 推送前修正（pre-push 爪拦 origin 前进分叉伪影 r374·推送前窗内 bm-c W108 冻结落 origin·其 gate 尾投影披露 B REFUSED[61_000]·本机独立机验拒绝点=SEED_REGISTRY `wild_route_s1`=61_000 命中算术窗尾·首稿从未推送=零外见性·rev.B=唯一发布面）〕】·本窗实况=**W103 finalize 已落账（净链头 591,148·K=224,520 合并池·bm-b r586 one-pass）+五在飞上游席（W104 bm-a+W105 bm-c+W106 bm-b+W107 bm-a+W108 bm-c registered 烧毕/在飞 finalize 待）=本波 finalize 链序前置在飞（跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**·**带位（r535 机闸 derive 律·活注册表机证·单态收敛门·ADMIT 回执=results/_r587bmb_w109_band_gate.py rc0 实跑·hops A=0/B=1）**：**A-ext seed=261_004..263_003**（==W108 行 A 尾 261_003+1 起算术续带·步长 2_000·**CLEAN 零拒绝点**）；**B-ext exit seed=61_001..61_200**（**撞值跳位带**：算术窗 60_801..61_000 撞 **SEED_REGISTRY `wild_route_s1`=61_000** → 跳位至首个净窗 61_001..61_200·步长 200·**refusal hops=1·拒绝事实机证披露**〔bm-c W108 gate 尾投影交叉验证一致·法典 §4 W5 撞值跳位先例族·机闸 disjoint 律优先于步长惯例〕）。R250：W109 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W109 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W109_PREREG.md（冻结件·锚=W103 finalize 实测值〔merged mu −0.09289408382326719·K=224,520·K-lift +0.0005·A-p95 0.3342·锚滚动律自 W101 滚动至 W103 跨 W102/W103 双落账窗·r576 锚滚律〕）·**W110+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 263_004..265_003 **CLEAN**；B 61_201..61_400 **CLEAN**（下波按法典 §4 表尾+全 registry 重 derive）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce2109\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW109.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W109 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    109: {"a": (261_004') == 1, 'FIX-B FAIL: W109 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W109"') == 1, 'FIX-B FAIL: W109 config not exactly once'
for w in range(58, 109):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W109 materializer face') == 2, \
    'FIX-B FAIL: W109 leg+summary must be exactly 2'
for w in range(48, 109):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce2109\uff08') == 1, 'FIX-B FAIL: canon W109 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W109 added per face')

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
print('FREEZE_EDITS_OK 109')
