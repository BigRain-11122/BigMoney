# -*- coding: utf-8 -*-
"""r584 bm-b W103 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening.

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED rows (W102 bm-c
  r375); every registered row signature survives exactly; exactly one new
  W103 signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.
AST gate (r580/r581 lesson): post-edit ast.parse on both py faces.

W103 = NINETY-THIRD engine wave by MACHINE-DERIVE (engine_owner rows 92 +
candidate; gate leg0 machine output governs per r359 law), bm-b's
THIRTY-FIFTH owned (engine_owner==bm-b rows 34 + candidate).
First free number after the REGISTERED W102 row (bm-c r375, surgical
delivery fd031f6ed) -- SINGLE STATE zero seat gap (no skip-past-published
chain). Seat published=reserved MSG-20261002-1658-bmb pushed to origin
badb5dcc2 BEFORE this freeze (r565 early-visibility law).
Bands (both sides arithmetic continuation from the registered W102 tails):
  A 249_004..251_003 (W102 A tail 249_003 + 1, stride 2_000) hops=0.
  B 59_401..59_600   (W102 B tail 59_400 + 1, stride 200) hops=0.
  ADMIT receipt results/_r584bmb_w103_band_gate.py rc0; banned gate ADMIT 0.
W98 finalize LANDED at this freeze (chain head 580,148, K=213,520 = W98
bm-a r584). FOUR in-flight upstream seats (W99 bm-c burned-unfinalized +
W100 bm-b burned-unfinalized + W101 bm-a burned-unfinalized + W102 bm-c
burned-unfinalized) -- finalize merge loop stays FAIL-CLOSED r307 at run
time. W104+ projection: A 251_004..253_003 CLEAN / B 59_601..59_800 CLEAN
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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 103))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 103)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 103)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[103] ---------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '103: {"a": (249_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    102: {"a": (247_004, 249_003), "b_exit": (59_201, 59_400),\n'
          '         "engine_owner": "bm-c"},\n'
          '}\n')
    NEW = ('    102: {"a": (247_004, 249_003), "b_exit": (59_201, 59_400),\n'
           '         "engine_owner": "bm-c"},\n'
           '    # NINETY-THIRD ENGINE-OWNED WAVE BY MACHINE-DERIVE (r584 bm-b\n'
           '    # freeze): engine_owner rows 92 + candidate; bm-b\'s thirty-\n'
           '    # fifth owned per machine-derive (engine_owner==bm-b rows 34 +\n'
           '    # candidate). Wave 103 = first free number after the REGISTERED\n'
           '    # W102 row (bm-c r375, surgical delivery fd031f6ed) -- SINGLE\n'
           '    # STATE zero seat gap (no skip-past-published chain). Seat\n'
           '    # published=reserved MSG-20261002-1658-bmb pushed to origin\n'
           '    # badb5dcc2 BEFORE this freeze per r565 early-visibility law.\n'
           '    # W98 finalize LANDED at this freeze (landed chain head\n'
           '    # 580,148 = W98 bm-a r584; K=213,520). FOUR in-flight upstream\n'
           '    # seats (W99 bm-c burned-unfinalized + W100 bm-b burned-\n'
           '    # unfinalized + W101 bm-a burned-unfinalized + W102 bm-c\n'
           '    # burned-unfinalized) -- finalize merge loop stays FAIL-CLOSED\n'
           '    # r307 at run time.\n'
           '    # A = arithmetic continuation from the registered W102 A tail:\n'
           '    # 249_004..251_003 CLEAN hops=0. B = arithmetic continuation\n'
           '    # from the registered W102 B tail: 59_401..59_600 CLEAN hops=0\n'
           '    # (both sides arithmetic continuation, W92 r370 / W100 r583\n'
           '    # precedent family). ADMIT receipt\n'
           '    # results/_r584bmb_w103_band_gate.py rc0; live SEED_REGISTRY\n'
           '    # + probe cluster 95_000..95_003 r335 leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 leg.\n'
           '    # W104+ projection: A 251_004..253_003 CLEAN; B 59_601..59_800\n'
           '    # CLEAN (next freezer must re-derive, never transcribe).\n'
           '    # NOT a re-pick (R250: W103 bands were never assigned).\n'
           '    103: {"a": (249_004, 251_003), "b_exit": (59_401, 59_600),\n'
           '         "engine_owner": "bm-b"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[103] landed (anchor=W102 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[103] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '103: {"batch": "PERPETUAL-N1-W103"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w102", "out_name": "n1_w102_results.json",\n'
          '                            "engine_owner": "bm-c"},\n')
    NEW2 = A2 + (
        '                       103: {"batch": "PERPETUAL-N1-W103",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W103_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; NINETY-THIRD ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 92 + candidate), own-series "\n'
        '                                       "continuation per O-20261001-2355 sec.2 (first-free-number "\n'
        '                                       "law after the REGISTERED W102 row, SINGLE STATE zero seat "\n'
        '                                       "gap; seat published=reserved MSG-20261002-1658-bmb "\n'
        '                                       "PUSHED to origin badb5dcc2 BEFORE this freeze per r565 "\n'
        '                                       "early-visibility law), engine_owner=bm-b, wave 103: A = "\n'
        '                                       "arithmetic continuation from the registered W102 A tail "\n'
        '                                       "(249_004..251_003 CLEAN hops=0) + B = arithmetic "\n'
        '                                       "continuation from the registered W102 B tail "\n'
        '                                       "(59_401..59_600 CLEAN hops=0; ADMIT receipt "\n'
        '                                       "results/_r584bmb_w103_band_gate.py; W104+ projection: "\n'
        '                                       "A 251_004..253_003 CLEAN / B 59_601..59_800 CLEAN for "\n'
        '                                       "the next freezer); W98 finalize LANDED at this freeze "\n'
        '                                       "(chain head 580,148, K=213,520) + FOUR in-flight "\n'
        '                                       "upstream seats W99 bm-c burned-unfinalized + W100 bm-b "\n'
        '                                       "burned-unfinalized + W101 bm-a burned-unfinalized + "\n'
        '                                       "W102 bm-c burned-unfinalized -- finalize merge loop stays "\n'
        '                                       "FAIL-CLOSED r307 at run time)"),\n'
        '                            "a_seed_base": 249_004,        # law sec.4 W103 A: 249_004..251_003 (arithmetic continuation from the registered W102 A tail)\n'
        '                            "b_exit_seed_base": 59_401,   # law sec.4 W103 B: 59_401..59_600 (arithmetic continuation from the registered W102 B tail)\n'
        '                            "shard_subdir": "n1_w103", "out_name": "n1_w103_results.json",\n'
        '                            "engine_owner": "bm-b"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[103] landed (anchor=W102 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W103 leg --------------
LEG103 = '''
    # --- W103 materializer face (r584 bm-b freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-b's
    #     thirty-fifth owned per machine-derive (engine_owner==bm-b
    #     rows 34 + candidate); wave 103 = first free number after
    #     the REGISTERED W102 row (bm-c r375, surgical delivery
    #     fd031f6ed) -- SINGLE STATE zero seat gap (no
    #     skip-past-published chain). Seat published=reserved
    #     MSG-20261002-1658-bmb pushed to origin badb5dcc2 BEFORE
    #     this freeze, r565 law. NINETY-THIRD engine wave BY
    #     MACHINE-DERIVE (engine_owner rows 92 + candidate; gate
    #     leg0 machine output governs per r359 law). W98 finalize
    #     LANDED (chain head 580,148, K=213,520) + FOUR in-flight
    #     upstream seats W99 bm-c + W100 bm-b + W101 bm-a + W102 bm-c
    #     burned-unfinalized -- FAIL-CLOSED r307 at run time. ADMIT
    #     receipt results/_r584bmb_w103_band_gate.py; not a re-pick
    #     (R250: W103 bands were never assigned).
    _set_wave(103)
    try:
        assert WAVE_CONFIGS[103]["a_seed_base"] == pf.N1_BANDS[103]["a"][0], \\
            "W103 A band drift vs law mirror"
        assert WAVE_CONFIGS[103]["b_exit_seed_base"] == \\
            pf.N1_BANDS[103]["b_exit"][0], "W103 B band drift vs law mirror"
        assert WAVE_CONFIGS[103].get("engine_owner") == \\
            pf.N1_BANDS[103].get("engine_owner") == "bm-b", \\
            "W103 engine_owner drift (law mirror parity)"
        w103_a = {A_SEED_BASE + j for j in range(A_N)}
        w103_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w103_a & w103_b), "W103 A/B band overlap"
        assert not (w103_a & reg_ints) and not (w103_b & reg_ints), \\
            "W103 hits SEED_REGISTRY"
        for nm, band in (("A", w103_a), ("B", w103_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W103 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W103 {nm} hits W1"
            assert not (band & probes), f"W103 {nm} hits probe seeds"
        # registered row parity (r307 pinned constants, recent estate)
        assert pf.N1_BANDS[97] == {"a": (237_004, 239_003),
                                   "b_exit": (58_001, 58_200),
                                   "engine_owner": "bm-b"}, \\
            "registered W97 row parity drift (r307; bm-b r581)"
        assert pf.N1_BANDS[98] == {"a": (239_004, 241_003),
                                   "b_exit": (58_201, 58_400),
                                   "engine_owner": "bm-a"}, \\
            "registered W98 row parity drift (r307; bm-a r582)"
        assert pf.N1_BANDS[99] == {"a": (241_004, 243_003),
                                   "b_exit": (58_551, 58_750),
                                   "engine_owner": "bm-c"}, \\
            "registered W99 row parity drift (r307; bm-c r374)"
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
        # prior-wave disjointness W2..W102 (single state: all
        # registered, dynamic registry derive, r511 law)
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 103):
            assert not (w103_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W103 A hits W{wprev}"
            assert not (w103_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W103 B hits W{wprev}"
        n3r1_used103 = set(range(70_000, 70_006))
        assert not (w103_a & n3r1_used103) and not (w103_b & n3r1_used103), \\
            "W103 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        assert not (w103_a & lfc_actual12) and not (w103_b & lfc_actual12), \\
            "W103 bands must clear the lfc actual draw range"
        assert not (w103_a & options_actual12) and \\
            not (w103_b & options_actual12), \\
            "W103 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W103 row, r584): both sides arithmetic
        # continuation from the registered W102 tails, zero skips.
        assert WAVE_CONFIGS[103]["a_seed_base"] == 249_004 == 249_003 + 1, (
            "W103 A must be the arithmetic continuation past the W102 "
            "registered A band tail")
        arith_a103 = set(range(249_004, 251_004))
        assert not (arith_a103 & reg_ints), \\
            "W103 A window must be CLEAN (arithmetic ADMIT face)"
        assert WAVE_CONFIGS[103]["b_exit_seed_base"] == 59_401 == 59_400 + 1, (
            "W103 B must be the arithmetic continuation past the W102 "
            "registered B band tail")
        arith_b103 = set(range(59_401, 59_601))
        assert not (arith_b103 & reg_ints), \\
            "W103 B window must be CLEAN (arithmetic ADMIT face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W103-SHARD-0",
                                          "n1w103-0of12"), "W103 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W103-SHARD-11",
                                           "n1w103-11of12")
        assert SHARD_DIR.endswith("n1_w103") and OUT.endswith(
            "n1_w103_results.json"), "W103 path drift"
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 103):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W103 shard dir collides with W{wprev}"
        # W103 finalize cumulative deps: W17..W98 outputs ALL PRESENT
        # (landed chain head 580,148 = W98 bm-a r584; W99/W100/W101/
        # W102 registered with finalizes NOT landed -- in-flight
        # upstream seats, honest note; the finalize merge loop derives
        # the wave set from registry keys at run time and stays
        # FAIL-CLOSED, r307 law).
        for _depw in range(17, 99):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W103 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): every
        # registered wave below 103 composes; wave 15 excluded by
        # design; SINGLE STATE (W2..W102 all registered -- no
        # two-state seat disclosure needed at this freeze).
        assert sorted(w for w in WAVE_CONFIGS if w < 103) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 103)], \\
            "W103 prior-wave set must derive from registry keys (no 15; " \\
            "W2..W102 registered single state)"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W103_PREREG.md")), \\
            "W103 per-wave prereg missing (materializer requirement)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W103 materializer face' in t2b:
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
            + LEG103
            + '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n')
    t2b = rep(t2b, A3, NEW3, eol2b, 'n1-leg103')
    save(FP2, t2b)
    print('edit3 selftest W103 leg landed (insert before T-141 selftest lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment ----------------------
t2c, eol2c = load(FP2)
if '+ W103 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('          "R250), law sec.4 W102 row, r375 bm-c] "\n'
          '          "+ T-141 s2 ')
    SEG103 = ('          "R250), law sec.4 W102 row, r375 bm-c] "\n'
              '          "+ W103 materializer face [same guard set, dep=W17..W98 "\n'
              '          "outputs ALL PRESENT (landed chain head 580,148 = W98 "\n'
              '          "bm-a r584, K=213,520; FOUR in-flight upstream "\n'
              '          "seats W99 bm-c burned-unfinalized + W100 bm-b burned-"\n'
              '          "unfinalized + W101 bm-a burned-unfinalized + W102 bm-c "\n'
              '          "burned-unfinalized -- FAIL-CLOSED r307 at run time), "\n'
              '          "NINETY-THIRD ENGINE-OWNED WAVE BY MACHINE-DERIVE "\n'
              '          "(engine_owner rows 92 + candidate) bm-b\'s thirty-fifth "\n'
              '          "owned claim per machine-derive (engine_owner==bm-b "\n'
              '          "rows 34 + candidate), engine_owner=bm-b per engine "\n'
              '          "de-throttle law O-20261001-2355 sec.2 own-"\n'
              '          "continuous-series (wave 103 = first FREE number after "\n'
              '          "the REGISTERED W102 row, SINGLE STATE zero seat gap; "\n'
              '          "seat published=reserved MSG-20261002-1658-bmb pushed to "\n'
              '          "origin badb5dcc2 BEFORE this freeze, r565 law), "\n'
              '          "A=arithmetic continuation from the registered W102 A "\n'
              '          "tail (249_004..251_003 CLEAN hops=0) + B=arithmetic "\n'
              '          "continuation from the registered W102 B tail "\n'
              '          "(59_401..59_600 CLEAN hops=0; ADMIT receipt "\n'
              '          "results/_r584bmb_w103_band_gate.py; W104+ projection A "\n'
              '          "251_004..253_003 CLEAN / B 59_601..59_800 CLEAN "\n'
              '          "disclosed for the next freezer; not a free pick -- "\n'
              '          "R250), law sec.4 W103 row, r584 bm-b] "\n'
              '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG103, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W103 segment landed (insert after W102 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W103 row ---------------------
ROW103 = """
- N1 波103（r584 bm-b 冻·prereg 时展行）：**第九十三枚引擎波·bm-b 第三十五枚自有波〔机面 derive：engine_owner 行 92+本候选／engine_owner==bm-b 行 34+本候选·r359 律计数面以 gate 机输出为准〕**·engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W102 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-b 实例=tick 架构——冻结 commit 后下一 tick 新进程读活工作树自见新行=免杀重启免做·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 103=注册表 W102 行〔bm-c r375〕后首个自由号·单态零席位空档**（无 skip-past-published 链面）·**席位公示=MSG-20261002-1658-bmb**〔published=reserved r518-① 律·先于冻结 commit 推 origin badb5dcc2=r565 早可见性律〕】·本窗实况=**W98 finalize 已落账（净链头 580,148·K=213,520 合并池）+四在飞上游席（W99 bm-c 12/12 烧毕 finalize 待+W100 bm-b 12/12 烧毕 finalize 待+W101 bm-a 12/12 烧毕 finalize 待+W102 bm-c 12/12 烧毕 finalize 待）=本波 finalize 链序前置在飞（跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**·**带位（r584 机闸 derive 律·活注册表机证·单态收敛门·ADMIT 回执=results/_r584bmb_w103_band_gate.py rc0 实跑·hops A=0/B=0）**：**A-ext seed=249_004..251_003**（==W102 行 A 尾 249_003+1 起算术续带·步长 2_000·**CLEAN 零拒绝点**）；**B-ext exit seed=59_401..59_600**（==W102 行 B 尾 59_400+1 起算术续带·步长 200·**CLEAN 零拒绝点**；双侧算术续带 W92 r370/W100 r583 先例族）。R250：W103 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W103 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W103_PREREG.md（冻结件·锚=W98 finalize 实测值〔锚滚动律·单波跨锚自 W94 滚动至 W98·r576 锚滚律〕）·**W104+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 251_004..253_003 **CLEAN**；B 59_601..59_800 **CLEAN**（下波按法典 §4 表尾+全 registry 重 derive）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce2103\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW103.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W103 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    103: {"a": (249_004') == 1, 'FIX-B FAIL: W103 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W103"') == 1, 'FIX-B FAIL: W103 config not exactly once'
for w in range(58, 103):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W103 materializer face') == 2, \
    'FIX-B FAIL: W103 leg+summary must be exactly 2'
for w in range(48, 103):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce2103\uff08') == 1, 'FIX-B FAIL: canon W103 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W103 added per face')

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
print('FREEZE_EDITS_OK 103')
