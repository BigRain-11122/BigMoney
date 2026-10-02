# -*- coding: utf-8 -*-
"""r589 bm-b W111 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening.

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED rows (W107 bm-a +
  W108 bm-c + W109 bm-b + W110 bm-a); every registered row signature
  survives exactly; exactly one new W111 signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.
AST gate (r580/r581 lesson): post-edit ast.parse on both py faces.

W111 = HUNDRED-AND-FIRST engine wave by MACHINE-DERIVE (engine_owner rows
100 + candidate; gate leg0 machine output governs per r359 law), bm-b's
THIRTY-EIGHTH owned (engine_owner==bm-b rows 37 + candidate).
First free number after the REGISTERED W110 row (bm-a r589 freeze
ff0b1869b) -- SINGLE STATE zero seat gap (W2..W110 all registered).
Seat published=reserved MSG-20261002-1911-bmb pushed to origin 8088582ba
BEFORE this freeze (r565 early-visibility law; re-landed twice after
mid-window origin advances via the r585 pure-FF window, first draft never
visible, rev.A = only published face).
Bands:
  A 265_004..267_003 (W110 A tail 265_003 + 1, stride 2_000) hops=0 CLEAN.
  B 61_401..61_600   (W110 B tail 61_400 + 1, stride 200) hops=0 CLEAN.
  ADMIT receipt results/_r589bmb_w111_band_gate.py rc0; banned gate ADMIT 0.
W107 finalize LANDED mid-draft-window (chain head 599,948, K=233,320 =
bm-a r589 one-pass). THREE in-flight upstream seats (W108 bm-c + W109
bm-b + W110 bm-a registered, 12/12 delivered, finalizes NOT landed) --
finalize merge loop stays FAIL-CLOSED r307 at run time.
W112+ projection: A 267_004..269_003 CLEAN / B 61_601..61_800 CLEAN
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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 111))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 111)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 111)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[111] ---------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '111: {"a": (265_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    110: {"a": (263_004, 265_003), "b_exit": (61_201, 61_400),\n'
          '         "engine_owner": "bm-a"},\n'
          '}\n')
    NEW = ('    110: {"a": (263_004, 265_003), "b_exit": (61_201, 61_400),\n'
           '         "engine_owner": "bm-a"},\n'
           '    # HUNDRED-AND-FIRST ENGINE-OWNED WAVE BY MACHINE-DERIVE (r589 bm-b\n'
           '    # freeze): engine_owner rows 100 + candidate; bm-b\'s thirty-\n'
           '    # eighth owned per machine-derive (engine_owner==bm-b rows 37 +\n'
           '    # candidate). Wave 111 = first free number after the REGISTERED\n'
           '    # W110 row (bm-a r589 freeze ff0b1869b) -- SINGLE STATE zero seat\n'
           '    # gap (W2..W110 all registered). Seat published=reserved\n'
           '    # MSG-20261002-1911-bmb pushed to origin 8088582ba BEFORE this\n'
           '    # freeze per r565 early-visibility law (re-landed twice after\n'
           '    # mid-window origin advances via the r585 pure-FF window; first\n'
           '    # draft never visible; rev.A = only published face). W107\n'
           '    # finalize LANDED mid-draft-window (chain head 599,948, K=233,320\n'
           '    # = bm-a r589 one-pass). THREE in-flight upstream seats (W108\n'
           '    # bm-c + W109 bm-b + W110 bm-a registered, 12/12 delivered,\n'
           '    # finalizes NOT landed) -- finalize merge loop stays\n'
           '    # FAIL-CLOSED r307 at run time.\n'
           '    # A = arithmetic continuation from the registered W110 A tail:\n'
           '    # 265_004..267_003 CLEAN hops=0. B = arithmetic continuation from\n'
           '    # the registered W110 B tail: 61_401..61_600 CLEAN hops=0.\n'
           '    # ADMIT receipt results/_r589bmb_w111_band_gate.py rc0; live\n'
           '    # SEED_REGISTRY + probe cluster 95_000..95_003 r335 leg + N3-R1\n'
           '    # used-seed band 70_000..70_005 MSG-183x r529 leg.\n'
           '    # W112+ projection: A 267_004..269_003 CLEAN; B 61_601..61_800\n'
           '    # CLEAN (next freezer must re-derive, never transcribe).\n'
           '    # NOT a re-pick (R250: W111 bands were never assigned).\n'
           '    111: {"a": (265_004, 267_003), "b_exit": (61_401, 61_600),\n'
           '         "engine_owner": "bm-b"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[111] landed (anchor=W110 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[111] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '111: {"batch": "PERPETUAL-N1-W111"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w110", "out_name": "n1_w110_results.json",\n'
          '                            "engine_owner": "bm-a"},\n')
    NEW2 = A2 + (
        '                       111: {"batch": "PERPETUAL-N1-W111",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W111_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; HUNDRED-AND-FIRST ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 100 + candidate), own-series "\n'
        '                                       "continuation per O-20261001-2355 sec.2 (first-free-number "\n'
        '                                       "law after the REGISTERED W110 row bm-a r589 freeze ff0b1869b, "\n'
        '                                       "SINGLE STATE zero seat gap W2..W110 all registered; seat "\n'
        '                                       "published=reserved MSG-20261002-1911-bmb PUSHED to origin "\n'
        '                                       "8088582ba BEFORE this freeze per r565 early-visibility law; "\n'
        '                                       "pre-seat probe and freeze-window band-gate runs derive "\n'
        '                                       "identical, no fork face; seat re-landed twice after mid-window "\n'
        '                                       "origin advances via r585 pure-FF window, first draft never "\n'
        '                                       "visible), engine_owner=bm-b, wave 111: A = arithmetic "\n'
        '                                       "continuation from the registered W110 A tail (265_004..267_003 "\n'
        '                                       "CLEAN hops=0) + B = arithmetic continuation from the "\n'
        '                                       "registered W110 B tail (61_401..61_600 CLEAN hops=0; ADMIT "\n'
        '                                       "receipt results/_r589bmb_w111_band_gate.py; W112+ projection: "\n'
        '                                       "A 267_004..269_003 CLEAN / B 61_601..61_800 CLEAN for the "\n'
        '                                       "next freezer); W107 finalize LANDED mid-draft-window (chain "\n'
        '                                       "head 599,948, K=233,320, bm-a r589 one-pass) + THREE "\n'
        '                                       "in-flight upstream seats W108 bm-c + W109 bm-b + W110 bm-a "\n'
        '                                       "registered-unfinalized -- finalize merge loop stays "\n'
        '                                       "FAIL-CLOSED r307 at run time)"),\n'
        '                            "a_seed_base": 265_004,        # law sec.4 W111 A: 265_004..267_003 (arithmetic continuation from the registered W110 A tail)\n'
        '                            "b_exit_seed_base": 61_401,   # law sec.4 W111 B: 61_401..61_600 (arithmetic continuation from the registered W110 B tail)\n'
        '                            "shard_subdir": "n1_w111", "out_name": "n1_w111_results.json",\n'
        '                            "engine_owner": "bm-b"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[111] landed (anchor=W110 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W111 leg --------------
LEG111 = '''
    # --- W111 materializer face (r589 bm-b freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-b's
    #     thirty-eighth owned per machine-derive (engine_owner==bm-b
    #     rows 37 + candidate); wave 111 = first free number after
    #     the REGISTERED W110 row (bm-a r589 freeze ff0b1869b) --
    #     SINGLE STATE zero seat gap (W2..W110 all registered).
    #     Seat published=reserved MSG-20261002-1911-bmb pushed to
    #     origin 8088582ba BEFORE this freeze, r565 law (re-landed
    #     twice after mid-window origin advances via r585 pure-FF
    #     window; first draft never visible). HUNDRED-AND-FIRST
    #     engine wave BY MACHINE-DERIVE (engine_owner rows 100 +
    #     candidate; gate leg0 machine output governs per r359 law).
    #     W107 finalize LANDED mid-draft-window (chain head 599,948,
    #     K=233,320, bm-a r589 one-pass) + THREE in-flight upstream
    #     seats W108 bm-c + W109 bm-b + W110 bm-a registered, 12/12
    #     delivered, finalizes NOT landed -- FAIL-CLOSED r307 at
    #     run time. ADMIT receipt results/_r589bmb_w111_band_gate.py;
    #     not a re-pick (R250: W111 bands were never assigned).
    _set_wave(111)
    try:
        assert WAVE_CONFIGS[111]["a_seed_base"] == pf.N1_BANDS[111]["a"][0], \\
            "W111 A band drift vs law mirror"
        assert WAVE_CONFIGS[111]["b_exit_seed_base"] == \\
            pf.N1_BANDS[111]["b_exit"][0], "W111 B band drift vs law mirror"
        assert WAVE_CONFIGS[111].get("engine_owner") == \\
            pf.N1_BANDS[111].get("engine_owner") == "bm-b", \\
            "W111 engine_owner drift (law mirror parity)"
        w111_a = {A_SEED_BASE + j for j in range(A_N)}
        w111_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w111_a & w111_b), "W111 A/B band overlap"
        assert not (w111_a & reg_ints) and not (w111_b & reg_ints), \\
            "W111 hits SEED_REGISTRY"
        for nm, band in (("A", w111_a), ("B", w111_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W111 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W111 {nm} hits W1"
            assert not (band & probes), f"W111 {nm} hits probe seeds"
        # registered row parity (r307 pinned constants, recent estate)
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
        assert pf.N1_BANDS[110] == {"a": (263_004, 265_003),
                                    "b_exit": (61_201, 61_400),
                                    "engine_owner": "bm-a"}, \\
            "registered W110 row parity drift (r307; bm-a r589)"
        # prior-wave disjointness W2..W110 (single state: all
        # registered, dynamic registry derive, r511 law)
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 111):
            assert not (w111_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W111 A hits W{wprev}"
            assert not (w111_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W111 B hits W{wprev}"
        n3r1_used111 = set(range(70_000, 70_006))
        assert not (w111_a & n3r1_used111) and not (w111_b & n3r1_used111), \\
            "W111 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        assert not (w111_a & lfc_actual12) and not (w111_b & lfc_actual12), \\
            "W111 bands must clear the lfc actual draw range"
        assert not (w111_a & options_actual12) and \\
            not (w111_b & options_actual12), \\
            "W111 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W111 row, r589): BOTH sides arithmetic
        # continuation from the registered W110 tails, zero skips.
        assert WAVE_CONFIGS[111]["a_seed_base"] == 265_004 == 265_003 + 1, (
            "W111 A must be the arithmetic continuation past the W110 "
            "registered A band tail")
        arith_a111 = set(range(265_004, 267_004))
        assert not (arith_a111 & reg_ints), \\
            "W111 A window must be CLEAN (arithmetic ADMIT face)"
        assert WAVE_CONFIGS[111]["b_exit_seed_base"] == 61_401 == 61_400 + 1, (
            "W111 B must be the arithmetic continuation past the W110 "
            "registered B band tail")
        arith_b111 = set(range(61_401, 61_601))
        assert not (arith_b111 & reg_ints), \\
            "W111 B window must be CLEAN (arithmetic ADMIT face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W111-SHARD-0",
                                          "n1w111-0of12"), "W111 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W111-SHARD-11",
                                           "n1w111-11of12")
        assert SHARD_DIR.endswith("n1_w111") and OUT.endswith(
            "n1_w111_results.json"), "W111 path drift"
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 111):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W111 shard dir collides with W{wprev}"
        # W111 finalize cumulative deps: W17..W107 outputs ALL PRESENT
        # (landed chain head 599,948 = W107 bm-a r589 closing; W108/W109/
        # W110 registered with finalizes NOT landed -- in-flight
        # upstream seats, honest note; the finalize merge loop derives
        # the wave set from registry keys at run time and stays
        # FAIL-CLOSED, r307 law).
        for _depw in range(17, 108):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W111 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): every
        # registered wave below 111 composes; wave 15 excluded by
        # design; SINGLE STATE (W2..W110 all registered -- no
        # two-state seat disclosure needed at this freeze).
        assert sorted(w for w in WAVE_CONFIGS if w < 111) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 111)], \\
            "W111 prior-wave set must derive from registry keys (no 15; " \\
            "W2..W110 registered single state)"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W111_PREREG.md")), \\
            "W111 per-wave prereg missing (materializer requirement)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W111 materializer face' in t2b:
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
            + LEG111
            + '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n')
    t2b = rep(t2b, A3, NEW3, eol2b, 'n1-leg111')
    save(FP2, t2b)
    print('edit3 selftest W111 leg landed (insert before T-141 selftest lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment ----------------------
t2c, eol2c = load(FP2)
if '+ W111 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('          "R250), law sec.4 W110 row, r589 bm-a] "\n'
          '          "+ T-141 s2 ')
    SEG111 = ('          "R250), law sec.4 W110 row, r589 bm-a] "\n'
              '          "+ W111 materializer face [same guard set, dep=W17..W107 "\n'
              '          "outputs ALL PRESENT (landed chain head 599,948 = W107 "\n'
              '          "bm-a r589 one-pass, K=233,320; THREE in-flight upstream "\n'
              '          "seats W108 bm-c + W109 bm-b + W110 bm-a registered, "\n'
              '          "12/12 delivered, finalizes NOT landed -- FAIL-CLOSED "\n'
              '          "r307 at run time), HUNDRED-AND-FIRST ENGINE-OWNED WAVE "\n'
              '          "BY MACHINE-DERIVE (engine_owner rows 100 + candidate) "\n'
              '          "bm-b\'s thirty-eighth owned claim per machine-derive "\n'
              '          "(engine_owner==bm-b rows 37 + candidate), engine_owner=bm-b "\n'
              '          "per engine de-throttle law O-20261001-2355 sec.2 own-"\n'
              '          "continuous-series (wave 111 = first FREE number after the "\n'
              '          "REGISTERED W110 row bm-a r589 freeze ff0b1869b, SINGLE "\n'
              '          "STATE zero seat gap W2..W110 all registered; seat "\n'
              '          "published=reserved MSG-20261002-1911-bmb pushed to "\n'
              '          "origin 8088582ba BEFORE this freeze, r565 law; seat "\n'
              '          "re-landed twice after mid-window origin advances via "\n'
              '          "r585 pure-FF window, first draft never visible), "\n'
              '          "A=arithmetic continuation from the registered W110 A tail "\n'
              '          "(265_004..267_003 CLEAN hops=0) + B=arithmetic "\n'
              '          "continuation from the registered W110 B tail "\n'
              '          "(61_401..61_600 CLEAN hops=0; ADMIT receipt "\n'
              '          "results/_r589bmb_w111_band_gate.py; W112+ projection "\n'
              '          "A 267_004..269_003 CLEAN / B 61_601..61_800 CLEAN "\n'
              '          "disclosed for the next freezer; not a free pick -- "\n'
              '          "R250), law sec.4 W111 row, r589 bm-b] "\n'
              '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG111, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W111 segment landed (insert after W110 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W111 row ---------------------
ROW111 = """
- N1 波111（r589 bm-b 冻·prereg 时展行）：**第一百零一枚引擎波·bm-b 第三十八枚自有波〔机面 derive：engine_owner 行 100+本候选／engine_owner==bm-b 行 37+本候选·r359 律计数面以 gate 机输出为准〕**·engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W110 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-b 实例=tick 架构——冻结 commit 后下一 tick 新进程读活工作树自见新行=免杀重启免做·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 111=注册表 W110 行后首个自由号·单态零席位空档**（W104=bm-a r586 union 48f6f2ff1+W105=bm-c r376 freeze f2db133c5+W106=bm-b r585 freeze d6b2952e3+W107=bm-a r587 freeze a554dedd3+W108=bm-c r378 freeze 3a3c51b73+W109=bm-b r587 freeze f077ae11b+W110=bm-a r589 freeze ff0b1869b 均已注册·无 skip-past-published 链面）·**席位公示=MSG-20261002-1911-bmb**〔published=reserved r518-① 律·先于冻结 commit 推 origin 8088582ba=r565 早可见性律·**三次 origin 前进重落实录**：首推被拒（bm-c r380+bm-a r589 closing 中窗落账）→r585 纯 FF 窗重落（共享 append-only 面 pool_core_samples.jsonl 按 r570 律 origin-verbatim+本地行 union 1051 行全 dict）→二推被爪拦（bm-a r589 tail telemetry 再前进·r374 分叉伪影族）→三落 8088582ba 一发即达；首稿从未可见=零外见性·rev.A=唯一发布面·全程零 rebase 零 force=r532 活写面律〕】·本窗实况=**W107 finalize 已落账（净链头 599,948·K=233,320 合并池·bm-a r589 closing one-pass·起草窗中段落账=锚随锚滚动律自 W106 滚至 W107 如实披露）+三在飞上游席（W108 bm-c+W109 bm-b+W110 bm-a registered 烧毕交付 finalize 待）=本波 finalize 链序前置在飞（跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**·**带位（r535 机闸 derive 律·活注册表机证·单态收敛门·ADMIT 回执=results/_r589bmb_w111_band_gate.py rc0 实跑·pre-seat probe _r589bmb_w111_probe.py 先跑·双窗 derive 恒等·hops A=0/B=0）**：**A-ext seed=265_004..267_003**（==W110 行 A 尾 265_003+1 起算术续带·步长 2_000·**CLEAN 零拒绝点**）；**B-ext exit seed=61_401..61_600**（==W110 行 B 尾 61_400+1 起算术续带·步长 200·**CLEAN 零拒绝点**·双侧算术续带=W92 r370/W100 r583/W103 r584/W106 r585/W107 r587/W110 r589 先例族）。R250：W111 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W111 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W111_PREREG.md（冻结件·锚=W107 finalize 实测值〔merged mu −0.0927601842962455·K=233,320·K-lift −0.0002·A-p95 0.3109·锚滚动律自 W106 滚动至 W107 跨起草窗中段 bm-a r589 closing 落账窗·r576 锚滚律〕）·**W112+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 267_004..269_003 **CLEAN**；B 61_601..61_800 **CLEAN**（下波按法典 §4 表尾+全 registry 重 derive）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce2111\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW111.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W111 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    111: {"a": (265_004') == 1, 'FIX-B FAIL: W111 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W111"') == 1, 'FIX-B FAIL: W111 config not exactly once'
for w in range(58, 111):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W111 materializer face') == 2, \
    'FIX-B FAIL: W111 leg+summary must be exactly 2'
for w in range(48, 111):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce2111\uff08') == 1, 'FIX-B FAIL: canon W111 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W111 added per face')

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
print('FREEZE_EDITS_OK 111')
