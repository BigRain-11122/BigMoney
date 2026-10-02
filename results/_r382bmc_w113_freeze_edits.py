# -*- coding: utf-8 -*-
"""r382 bm-c W113 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening.

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED rows (W108 bm-c +
  W109 bm-b + W110 bm-a + W111 bm-b + W112 bm-a); every registered row
  signature survives exactly; exactly one new W113 signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.
AST gate (r580/r581 lesson): post-edit ast.parse on both py faces.

W113 = ONE HUNDRED-AND-THIRD engine wave BY MACHINE-DERIVE (engine_owner
rows 102 + candidate; gate leg0 machine output governs per r359 law),
bm-c's THIRTY-THIRD owned (engine_owner==bm-c rows 32 + candidate).
First free number after the REGISTERED W112 row (bm-a r590 freeze
0c4d67910) -- SINGLE STATE zero seat gap (W2..W112 all registered).
Seat published=reserved MSG-20261002-1949-bmc pushed to origin baa0c3888
BEFORE this freeze (r565 early-visibility law; clean single-file push,
deletion-set EMPTY, rev.A = only published face).
Bands:
  A 269_004..271_003 (W112 A tail 269_003 + 1, stride 2_000) hops=0 CLEAN.
  B 62_001..62_200   (arithmetic 61_801..62_000 refused at SEED_REGISTRY
      cta_wave1=62_000 window-tail endpoint -> jump-past-hit window per
      D-20261002-05 pinned skip law, W74/W81 endpoint family) hops=1.
  ADMIT receipt results/_r382bmc_w113_band_gate.py rc0; banned gate ADMIT 0.
W111 finalize LANDED (chain head 608,748, K=242,120 = bm-b r590 one-pass).
ONE in-flight upstream seat (W112 bm-a registered, finalize NOT landed) --
finalize merge loop stays FAIL-CLOSED r307 at run time.
W114+ projection: A 271_004..273_003 CLEAN / B 62_201..62_400 CLEAN
(gate machine-derived; next freezer re-derives, never transcribes).
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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 113))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 113)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 113)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[113] ---------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '113: {"a": (269_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    112: {"a": (267_004, 269_003), "b_exit": (61_601, 61_800),\n'
          '         "engine_owner": "bm-a"},\n'
          '}\n')
    NEW = ('    112: {"a": (267_004, 269_003), "b_exit": (61_601, 61_800),\n'
           '         "engine_owner": "bm-a"},\n'
           '    # ONE HUNDRED-AND-THIRD ENGINE-OWNED WAVE BY MACHINE-DERIVE (r382 bm-c\n'
           '    # freeze): engine_owner rows 102 + candidate; bm-c\'s thirty-\n'
           '    # third owned per machine-derive (engine_owner==bm-c rows 32 +\n'
           '    # candidate). Wave 113 = first free number after the REGISTERED\n'
           '    # W112 row (bm-a r590 freeze 0c4d67910) -- SINGLE STATE zero seat\n'
           '    # gap (W2..W112 all registered). Seat published=reserved\n'
           '    # MSG-20261002-1949-bmc pushed to origin baa0c3888 BEFORE this\n'
           '    # freeze per r565 early-visibility law (clean single-file push,\n'
           '    # payload=1 seat MSG, deletion-set EMPTY; rev.A = only published\n'
           '    # face). W111 finalize LANDED (chain head 608,748, K=242,120 =\n'
           '    # bm-b r590 one-pass). ONE in-flight upstream seat (W112 bm-a\n'
           '    # registered, finalize NOT landed) -- finalize merge loop stays\n'
           '    # FAIL-CLOSED r307 at run time.\n'
           '    # A = arithmetic continuation from the registered W112 A tail:\n'
           '    # 269_004..271_003 CLEAN hops=0. B = jump-past-hit window: the\n'
           '    # arithmetic window 61_801..62_000 is refused at SEED_REGISTRY\n'
           '    # cta_wave1=62_000 (window-tail endpoint, W74/W81 family) ->\n'
           '    # pinned sec.4 skip semantics (D-20261002-05) land 62_001..62_200\n'
           '    # hops=1. ADMIT receipt results/_r382bmc_w113_band_gate.py rc0;\n'
           '    # live SEED_REGISTRY + probe cluster 95_000..95_003 r335 leg +\n'
           '    # N3-R1 used-seed band 70_000..70_005 MSG-183x r529 leg.\n'
           '    # W114+ projection: A 271_004..273_003 CLEAN; B 62_201..62_400\n'
           '    # CLEAN (next freezer must re-derive, never transcribe).\n'
           '    # NOT a re-pick (R250: W113 bands were never assigned).\n'
           '    113: {"a": (269_004, 271_003), "b_exit": (62_001, 62_200),\n'
           '         "engine_owner": "bm-c"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[113] landed (anchor=W112 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[113] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '113: {"batch": "PERPETUAL-N1-W113"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w112", "out_name": "n1_w112_results.json",\n'
          '                            "engine_owner": "bm-a"},\n')
    NEW2 = A2 + (
        '                       113: {"batch": "PERPETUAL-N1-W113",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W113_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; ONE HUNDRED-AND-THIRD ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 102 + candidate), own-series "\n'
        '                                       "continuation per O-20261001-2355 sec.2 (first-free-number "\n'
        '                                       "law after the REGISTERED W112 row bm-a r590 freeze 0c4d67910, "\n'
        '                                       "SINGLE STATE zero seat gap W2..W112 all registered; seat "\n'
        '                                       "published=reserved MSG-20261002-1949-bmc PUSHED to origin "\n'
        '                                       "baa0c3888 BEFORE this freeze per r565 early-visibility law; "\n'
        '                                       "pre-seat probe and freeze-window band-gate runs derive "\n'
        '                                       "identical, no fork face; seat landed via clean single-file "\n'
        '                                       "push, payload=1 seat MSG deletion-set EMPTY, rev.A = only "\n'
        '                                       "published face), engine_owner=bm-c, wave 113: A = arithmetic "\n'
        '                                       "continuation from the registered W112 A tail (269_004..271_003 "\n'
        '                                       "CLEAN hops=0) + B = jump-past-hit window (arithmetic "\n'
        '                                       "61_801..62_000 refused at SEED_REGISTRY cta_wave1=62_000 "\n'
        '                                       "window-tail endpoint, landed 62_001..62_200 hops=1 per "\n'
        '                                       "D-20261002-05 pinned skip law W74/W81 endpoint family; ADMIT "\n'
        '                                       "receipt results/_r382bmc_w113_band_gate.py; W114+ projection: "\n'
        '                                       "A 271_004..273_003 CLEAN / B 62_201..62_400 CLEAN for the next "\n'
        '                                       "freezer); W111 finalize LANDED (chain head 608,748, K=242,120, "\n'
        '                                       "bm-b r590 one-pass) + ONE in-flight upstream seat W112 bm-a "\n'
        '                                       "registered-unfinalized -- finalize merge loop stays "\n'
        '                                       "FAIL-CLOSED r307 at run time)"),\n'
        '                            "a_seed_base": 269_004,        # law sec.4 W113 A: 269_004..271_003 (arithmetic continuation from the registered W112 A tail)\n'
        '                            "b_exit_seed_base": 62_001,   # law sec.4 W113 B: 62_001..62_200 (jump-past-hit window over SEED_REGISTRY cta_wave1=62_000, D-20261002-05)\n'
        '                            "shard_subdir": "n1_w113", "out_name": "n1_w113_results.json",\n'
        '                            "engine_owner": "bm-c"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[113] landed (anchor=W112 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W113 leg --------------
LEG113 = '''
    # --- W113 materializer face (r382 bm-c freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-c's
    #     thirty-third owned per machine-derive (engine_owner==bm-c
    #     rows 32 + candidate); wave 113 = first free number after
    #     the REGISTERED W112 row (bm-a r590 freeze 0c4d67910) --
    #     SINGLE STATE zero seat gap (W2..W112 all registered).
    #     Seat published=reserved MSG-20261002-1949-bmc pushed to
    #     origin baa0c3888 BEFORE this freeze, r565 law (clean
    #     single-file push; payload=1 seat MSG; deletion-set EMPTY;
    #     rev.A = only published face). ONE HUNDRED-AND-THIRD engine
    #     wave BY MACHINE-DERIVE (engine_owner rows 102 + candidate;
    #     gate leg0 machine output governs per r359 law). W111
    #     finalize LANDED (chain head 608,748, K=242,120, bm-b r590
    #     one-pass) + ONE in-flight upstream seat W112 bm-a
    #     registered, finalize NOT landed -- FAIL-CLOSED r307 at
    #     run time. ADMIT receipt results/_r382bmc_w113_band_gate.py;
    #     not a re-pick (R250: W113 bands were never assigned).
    _set_wave(113)
    try:
        assert WAVE_CONFIGS[113]["a_seed_base"] == pf.N1_BANDS[113]["a"][0], \\
            "W113 A band drift vs law mirror"
        assert WAVE_CONFIGS[113]["b_exit_seed_base"] == \\
            pf.N1_BANDS[113]["b_exit"][0], "W113 B band drift vs law mirror"
        assert WAVE_CONFIGS[113].get("engine_owner") == \\
            pf.N1_BANDS[113].get("engine_owner") == "bm-c", \\
            "W113 engine_owner drift (law mirror parity)"
        w113_a = {A_SEED_BASE + j for j in range(A_N)}
        w113_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w113_a & w113_b), "W113 A/B band overlap"
        assert not (w113_a & reg_ints) and not (w113_b & reg_ints), \\
            "W113 hits SEED_REGISTRY"
        for nm, band in (("A", w113_a), ("B", w113_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W113 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W113 {nm} hits W1"
            assert not (band & probes), f"W113 {nm} hits probe seeds"
        # registered row parity (r307 pinned constants, recent estate)
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
        assert pf.N1_BANDS[110] == {"a": (263_004, 265_003),
                                    "b_exit": (61_201, 61_400),
                                    "engine_owner": "bm-a"}, \\
            "registered W110 row parity drift (r307; bm-a r589)"
        assert pf.N1_BANDS[111] == {"a": (265_004, 267_003),
                                    "b_exit": (61_401, 61_600),
                                    "engine_owner": "bm-b"}, \\
            "registered W111 row parity drift (r307; bm-b r589)"
        assert pf.N1_BANDS[112] == {"a": (267_004, 269_003),
                                    "b_exit": (61_601, 61_800),
                                    "engine_owner": "bm-a"}, \\
            "registered W112 row parity drift (r307; bm-a r590)"
        # prior-wave disjointness W2..W112 (single state: all
        # registered, dynamic registry derive, r511 law)
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 113):
            assert not (w113_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W113 A hits W{wprev}"
            assert not (w113_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W113 B hits W{wprev}"
        n3r1_used113 = set(range(70_000, 70_006))
        assert not (w113_a & n3r1_used113) and not (w113_b & n3r1_used113), \\
            "W113 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        assert not (w113_a & lfc_actual12) and not (w113_b & lfc_actual12), \\
            "W113 bands must clear the lfc actual draw range"
        assert not (w113_a & options_actual12) and \\
            not (w113_b & options_actual12), \\
            "W113 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W113 row, r382): A side = arithmetic
        # continuation from the registered W112 A tail, zero skips.
        assert WAVE_CONFIGS[113]["a_seed_base"] == 269_004 == 269_003 + 1, (
            "W113 A must be the arithmetic continuation past the W112 "
            "registered A band tail")
        arith_a113 = set(range(269_004, 271_004))
        assert not (arith_a113 & reg_ints), \\
            "W113 A window must be CLEAN (arithmetic ADMIT face)"
        # B side = jump-past-hit window (D-20261002-05 pinned sec.4
        # skip semantics): the arithmetic window 61_801..62_000 is
        # refused at SEED_REGISTRY cta_wave1=62_000 (window-tail
        # endpoint, W74/W81 family); the landed window starts at
        # hit+1 and is clean.
        _hit113 = 62_000
        assert _hit113 in reg_ints, \\
            "W113 B jump provenance: 62_000 must be a live SEED_REGISTRY point"
        arith_b113 = set(range(61_801, 62_001))
        assert (arith_b113 & reg_ints) == {_hit113}, \\
            "W113 B arithmetic window must be refused exactly at 62_000"
        assert WAVE_CONFIGS[113]["b_exit_seed_base"] == 62_001 == _hit113 + 1, (
            "W113 B must be the jump-past-hit window (D-20261002-05)")
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W113-SHARD-0",
                                          "n1w113-0of12"), "W113 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W113-SHARD-11",
                                           "n1w113-11of12")
        assert SHARD_DIR.endswith("n1_w113") and OUT.endswith(
            "n1_w113_results.json"), "W113 path drift"
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 113):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W113 shard dir collides with W{wprev}"
        # W113 finalize cumulative deps: W17..W111 outputs ALL PRESENT
        # (landed chain head 608,748 = W111 bm-b r590 one-pass; W112
        # bm-a registered with finalize NOT landed -- in-flight
        # upstream seat, honest note; the finalize merge loop derives
        # the wave set from registry keys at run time and stays
        # FAIL-CLOSED, r307 law).
        for _depw in range(17, 112):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W113 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): every
        # registered wave below 113 composes; wave 15 excluded by
        # design; SINGLE STATE (W2..W112 all registered -- no
        # two-state seat disclosure needed at this freeze).
        assert sorted(w for w in WAVE_CONFIGS if w < 113) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 113)], \\
            "W113 prior-wave set must derive from registry keys (no 15; " \\
            "W2..W112 registered single state)"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W113_PREREG.md")), \\
            "W113 per-wave prereg missing (materializer requirement)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W113 materializer face' in t2b:
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
            + LEG113
            + '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n')
    t2b = rep(t2b, A3, NEW3, eol2b, 'n1-leg113')
    save(FP2, t2b)
    print('edit3 selftest W113 leg landed (insert before T-141 selftest lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment ----------------------
t2c, eol2c = load(FP2)
if '+ W113 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('"free pick -- R250), law sec.4 W112 row, r590 bm-a] "\n'
          '          "+ T-141 s2 ')
    SEG113 = ('"free pick -- R250), law sec.4 W112 row, r590 bm-a] "\n'
              '          "+ W113 materializer face [same guard set, dep=W17..W111 "\n'
              '"outputs ALL PRESENT (landed chain head 608,748 = W111 "\n'
              '"bm-b r590 one-pass, K=242,120; ONE in-flight upstream seat W112 "\n'
              '"bm-a registered, finalize NOT landed -- FAIL-CLOSED r307 at run "\n'
              '"time), ONE HUNDRED-AND-THIRD ENGINE-OWNED WAVE BY MACHINE-DERIVE "\n'
              '"(engine_owner rows 102 + candidate) bm-c\'s thirty-third owned "\n'
              '"claim per machine-derive (engine_owner==bm-c rows 32 + "\n'
              '"candidate), engine_owner=bm-c per engine de-throttle law "\n'
              '"O-20261001-2355 sec.2 own-continuous-series (wave 113 = first "\n'
              '"FREE number after the REGISTERED W112 row bm-a r590 freeze "\n'
              '"0c4d67910, SINGLE STATE zero seat gap W2..W112 all registered; "\n'
              '"seat published=reserved MSG-20261002-1949-bmc pushed to "\n'
              '"origin baa0c3888 BEFORE this freeze, r565 law; seat landed via "\n'
              '"clean single-file push, payload=1 seat MSG deletion-set EMPTY, "\n'
              '"rev.A = only published face), A=arithmetic continuation from the "\n'
              '"registered W112 A tail (269_004..271_003 CLEAN hops=0) + "\n'
              '"B=jump-past-hit window (arithmetic 61_801..62_000 refused at "\n'
              '"SEED_REGISTRY cta_wave1=62_000 window-tail endpoint, landed "\n'
              '"62_001..62_200 hops=1 per D-20261002-05 pinned skip law W74/W81 "\n'
              '"family; ADMIT receipt results/_r382bmc_w113_band_gate.py; W114+ "\n'
              '"projection A 271_004..273_003 CLEAN / B 62_201..62_400 CLEAN "\n'
              '"disclosed for the next freezer; not a free pick -- R250), "\n'
              '"law sec.4 W113 row, r382 bm-c] "\n'
              '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG113, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W113 segment landed (insert after W112 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W113 row ---------------------
ROW113 = """
- N1 波113（r382 bm-c 冻·prereg 时展行）：**第一百零三枚引擎波·bm-c 第三十三枚自有波〔机面 derive：engine_owner 行 102+本候选／engine_owner==bm-c 行 32+本候选·r359 律计数面以 gate 机输出为准〕**·engine_owner=bm-c·SATURATION_ENGINE_LAW §1/§2 同 W10-W112 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-c 实例=**常驻架构 v0.4 mtime-reload**——冻结编辑落工作树后 LIVE 引擎下一 tick 重读活树自见新行自燃〔D-20261002-03 修法·W59/W60/W61/W66/W69/W71/W78/W80/W88 同窗实证·r325/r330 kill-restart 序免做〕·点火验证唯一证据=产物增长面 r325 律·2 tick 窗〕·【never-dry 供给律常设步·**波号 113=注册表 W112 行后首个自由号·单态零席位空档**（W106=bm-b r585 freeze d6b2952e3+W107=bm-a r587 freeze a554dedd3+W108=bm-c r378 freeze 3a3c51b73+W109=bm-b r587 freeze f077ae11b+W110=bm-a r589 freeze ff0b1869b+W111=bm-b r589 freeze e0a103ec1+W112=bm-a r590 freeze 0c4d67910 均已注册·表尾=W112 行）·**席位公示=MSG-20261002-1949-bmc**〔published=reserved r518-① 律·先于冻结 commit 推 origin baa0c3888=r565 早可见性律·净空窗单件直推一发即达·payload=席位 MSG 单件 deletion-set 空·rev.A=唯一发布面〕】·本窗实况=**W111 finalize 已落账（净链头 608,748·K=242,120 合并池·bm-b r590 W111 one-pass）+一在飞上游席（W112 bm-a registered 烧录在飞 finalize 未落账）=本波 finalize 链序前置在飞（跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**·**带位（r535 机闸 derive 律·活注册表机证·单态收敛门·ADMIT 回执=results/_r382bmc_w113_band_gate.py rc0 实跑·pre-seat probe _r382bmc_w113_probe.py 先跑·双窗 derive 恒等·hops A=0/B=1）**：**A-ext seed=269_004..271_003**（==W112 行 A 尾 269_003+1 起算术续带·步长 2_000·**CLEAN 零拒绝点**）；**B-ext exit seed=62_001..62_200**（算术窗 61_801..62_000 撞 SEED_REGISTRY `cta_wave1`=62_000〔窗尾端点命中=W74/W81 判例族·两读法恒同解〕→ **法典 §4 D-20261002-05 钉死行：越 hit 起窗** 62_001..62_200·hops=1·撞值跳位先例族=W5/W26/W63/W68/W109）。R250：W113 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W113 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W113_PREREG.md（冻结件·锚=W111 finalize 实测值〔merged mu −0.09276358334710065·K=242,120·K-lift 0.0000·A-p95 0.3191·se_mu 0.000498〕）·**W114+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 271_004..273_003 **CLEAN**（hops=0）；B 62_201..62_400 **CLEAN**（hops=0）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce2113\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW113.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W113 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    113: {"a": (269_004') == 1, 'FIX-B FAIL: W113 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W113"') == 1, 'FIX-B FAIL: W113 config not exactly once'
for w in range(58, 113):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W113 materializer face') == 2, \
    'FIX-B FAIL: W113 leg+summary must be exactly 2'
for w in range(48, 113):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce2113\uff08') == 1, 'FIX-B FAIL: canon W113 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W113 added per face')

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
print('FREEZE_EDITS_OK 113')
