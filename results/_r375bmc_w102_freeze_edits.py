# -*- coding: utf-8 -*-
"""r375 bm-c W102 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening.

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED rows (W101 bm-a
  r583); every registered row signature survives exactly; exactly one new
  W102 signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.
AST gate (r580/r581 lesson): post-edit ast.parse on both py faces.

W102 = NINETY-SECOND engine wave by MACHINE-DERIVE (engine_owner rows 91 +
candidate; gate leg0 machine output governs per r359 law -- the seat MSG
prose ordinal "91st/rows 90" hand-calc drift is disclosed, zero science
impact), bm-c's THIRTIETH owned (engine_owner==bm-c rows 29 + candidate).
First free number after the REGISTERED W101 row (bm-a r583, landed
ffd844431) -- SINGLE STATE zero seat gap (no skip-past-published chain;
W100 bm-b r583 + W101 bm-a r583 both landed before this freeze).
Seat published=reserved MSG-20261002-1642-bmc pushed to origin a369ae045
BEFORE this freeze (r565 early-visibility law).
Bands (both sides arithmetic continuation from the registered W101 tails):
  A 247_004..249_003 (W101 A tail 247_003 + 1, stride 2_000) hops=0.
  B 59_201..59_400   (W101 B tail 59_200 + 1, stride 200) hops=0.
  ADMIT receipt results/_r375bmc_w102_band_gate.py rc0; banned gate ADMIT 0.
W97 finalize LANDED at this freeze (chain head 577,948, K=211,320). FOUR
in-flight upstream seats (W98 bm-a burned-unfinalized + W99 bm-c burned-
unfinalized + W100 bm-b burning + W101 bm-a burning) -- finalize merge
loop stays FAIL-CLOSED r307 at run time. W103+ projection:
A 249_004..251_003 CLEAN / B 59_401..59_600 CLEAN (next freezer
re-derives, never transcribes).
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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 102))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 102)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 102)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[102] ---------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '102: {"a": (247_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    101: {"a": (245_004, 247_003), "b_exit": (59_001, 59_200),\n'
          '         "engine_owner": "bm-a"},\n'
          '}\n')
    NEW = ('    101: {"a": (245_004, 247_003), "b_exit": (59_001, 59_200),\n'
           '         "engine_owner": "bm-a"},\n'
           '    # NINETY-SECOND ENGINE-OWNED WAVE BY MACHINE-DERIVE (r375 bm-c\n'
           '    # freeze): engine_owner rows 91 + candidate; bm-c\'s thirtieth\n'
           '    # owned per machine-derive (engine_owner==bm-c rows 29 +\n'
           '    # candidate). Wave 102 = first free number after the REGISTERED\n'
           '    # W101 row (bm-a r583, landed ffd844431) -- SINGLE STATE zero\n'
           '    # seat gap (no skip-past-published chain; W100 bm-b r583 +\n'
           '    # W101 bm-a r583 both landed before this freeze). Seat\n'
           '    # published=reserved MSG-20261002-1642-bmc pushed to origin\n'
           '    # a369ae045 BEFORE this freeze per r565 early-visibility law\n'
           '    # (seat prose ordinal "91st/rows 90" hand-calc drift disclosed\n'
           '    # per r359 law; gate machine face governs; zero science impact).\n'
           '    # W97 finalize LANDED at this freeze (landed chain head\n'
           '    # 577,948 = W97 bm-b r583 one-pass; K=211,320). FOUR\n'
           '    # in-flight upstream seats (W98 bm-a burned-unfinalized +\n'
           '    # W99 bm-c burned-unfinalized + W100 bm-b burning + W101 bm-a\n'
           '    # burning) -- finalize merge loop stays FAIL-CLOSED r307\n'
           '    # at run time.\n'
           '    # A = arithmetic continuation from the registered W101 A tail:\n'
           '    # 247_004..249_003 CLEAN hops=0. B = arithmetic continuation\n'
           '    # from the registered W101 B tail: 59_201..59_400 CLEAN hops=0\n'
           '    # (both sides arithmetic continuation, W92 r370 / W100 r583\n'
           '    # precedent family). ADMIT receipt\n'
           '    # results/_r375bmc_w102_band_gate.py rc0; live SEED_REGISTRY\n'
           '    # + probe cluster 95_000..95_003 r335 leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 leg.\n'
           '    # W103+ projection: A 249_004..251_003 CLEAN; B 59_401..59_600\n'
           '    # CLEAN (next freezer must re-derive, never transcribe).\n'
           '    # NOT a re-pick (R250: W102 bands were never assigned).\n'
           '    102: {"a": (247_004, 249_003), "b_exit": (59_201, 59_400),\n'
           '         "engine_owner": "bm-c"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[102] landed (anchor=W101 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[102] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '102: {"batch": "PERPETUAL-N1-W102"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w101", "out_name": "n1_w101_results.json",\n'
          '                            "engine_owner": "bm-a"},\n')
    NEW2 = A2 + (
        '                       102: {"batch": "PERPETUAL-N1-W102",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W102_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; NINETY-SECOND ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 91 + candidate; seat "\n'
        '                                       "prose ordinal drift disclosed per r359 law), own-series "\n'
        '                                       "continuation per O-20261001-2355 sec.2 (first-free-number "\n'
        '                                       "law after the REGISTERED W101 row, SINGLE STATE zero seat "\n'
        '                                       "gap; seat published=reserved MSG-20261002-1642-bmc "\n'
        '                                       "PUSHED to origin a369ae045 BEFORE this freeze per r565 "\n'
        '                                       "early-visibility law), engine_owner=bm-c, wave 102: A = "\n'
        '                                       "arithmetic continuation from the registered W101 A tail "\n'
        '                                       "(247_004..249_003 CLEAN hops=0) + B = arithmetic "\n'
        '                                       "continuation from the registered W101 B tail "\n'
        '                                       "(59_201..59_400 CLEAN hops=0; ADMIT receipt "\n'
        '                                       "results/_r375bmc_w102_band_gate.py; W103+ projection: "\n'
        '                                       "A 249_004..251_003 CLEAN / B 59_401..59_600 CLEAN for "\n'
        '                                       "the next freezer); W97 finalize LANDED at this freeze "\n'
        '                                       "(chain head 577,948, K=211,320) + FOUR in-flight "\n'
        '                                       "upstream seats W98 bm-a burned-unfinalized + W99 bm-c "\n'
        '                                       "burned-unfinalized + W100 bm-b burning + W101 bm-a "\n'
        '                                       "burning -- finalize merge loop stays FAIL-CLOSED "\n'
        '                                       "r307 at run time)"),\n'
        '                            "a_seed_base": 247_004,        # law sec.4 W102 A: 247_004..249_003 (arithmetic continuation from the registered W101 A tail)\n'
        '                            "b_exit_seed_base": 59_201,   # law sec.4 W102 B: 59_201..59_400 (arithmetic continuation from the registered W101 B tail)\n'
        '                            "shard_subdir": "n1_w102", "out_name": "n1_w102_results.json",\n'
        '                            "engine_owner": "bm-c"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[102] landed (anchor=W101 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W102 leg --------------
LEG102 = '''
    # --- W102 materializer face (r375 bm-c freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-c's
    #     thirtieth owned per machine-derive (engine_owner==bm-c
    #     rows 29 + candidate); wave 102 = first free number after
    #     the REGISTERED W101 row (bm-a r583, landed ffd844431) --
    #     SINGLE STATE zero seat gap (no skip-past-published chain;
    #     W100 bm-b r583 + W101 bm-a r583 both landed before this
    #     freeze). Seat published=reserved MSG-20261002-1642-bmc
    #     pushed to origin a369ae045 BEFORE this freeze, r565 law.
    #     NINETY-SECOND engine wave BY MACHINE-DERIVE
    #     (engine_owner rows 91 + candidate; seat prose ordinal
    #     "91st/rows 90" hand-calc drift disclosed per r359 law,
    #     gate machine face governs). W97 finalize LANDED (chain
    #     head 577,948, K=211,320) + FOUR in-flight upstream seats
    #     W98 bm-a + W99 bm-c burned-unfinalized + W100 bm-b +
    #     W101 bm-a burning -- FAIL-CLOSED r307 at run time. ADMIT
    #     receipt results/_r375bmc_w102_band_gate.py; not a re-pick
    #     (R250: W102 bands were never assigned).
    _set_wave(102)
    try:
        assert WAVE_CONFIGS[102]["a_seed_base"] == pf.N1_BANDS[102]["a"][0], \\
            "W102 A band drift vs law mirror"
        assert WAVE_CONFIGS[102]["b_exit_seed_base"] == \\
            pf.N1_BANDS[102]["b_exit"][0], "W102 B band drift vs law mirror"
        assert WAVE_CONFIGS[102].get("engine_owner") == \\
            pf.N1_BANDS[102].get("engine_owner") == "bm-c", \\
            "W102 engine_owner drift (law mirror parity)"
        w102_a = {A_SEED_BASE + j for j in range(A_N)}
        w102_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w102_a & w102_b), "W102 A/B band overlap"
        assert not (w102_a & reg_ints) and not (w102_b & reg_ints), \\
            "W102 hits SEED_REGISTRY"
        for nm, band in (("A", w102_a), ("B", w102_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W102 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W102 {nm} hits W1"
            assert not (band & probes), f"W102 {nm} hits probe seeds"
        # registered row parity (r307 pinned constants, recent estate)
        assert pf.N1_BANDS[96] == {"a": (235_004, 237_003),
                                   "b_exit": (57_701, 57_900),
                                   "engine_owner": "bm-a"}, \\
            "registered W96 row parity drift (r307; bm-a r581)"
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
        # prior-wave disjointness W2..W101 (single state: all
        # registered, dynamic registry derive, r511 law)
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 102):
            assert not (w102_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W102 A hits W{wprev}"
            assert not (w102_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W102 B hits W{wprev}"
        n3r1_used102 = set(range(70_000, 70_006))
        assert not (w102_a & n3r1_used102) and not (w102_b & n3r1_used102), \\
            "W102 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        assert not (w102_a & lfc_actual12) and not (w102_b & lfc_actual12), \\
            "W102 bands must clear the lfc actual draw range"
        assert not (w102_a & options_actual12) and \\
            not (w102_b & options_actual12), \\
            "W102 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W102 row, r375): both sides arithmetic
        # continuation from the registered W101 tails, zero skips.
        assert WAVE_CONFIGS[102]["a_seed_base"] == 247_004 == 247_003 + 1, (
            "W102 A must be the arithmetic continuation past the W101 "
            "registered A band tail")
        arith_a102 = set(range(247_004, 249_004))
        assert not (arith_a102 & reg_ints), \\
            "W102 A window must be CLEAN (arithmetic ADMIT face)"
        assert WAVE_CONFIGS[102]["b_exit_seed_base"] == 59_201 == 59_200 + 1, (
            "W102 B must be the arithmetic continuation past the W101 "
            "registered B band tail")
        arith_b102 = set(range(59_201, 59_401))
        assert not (arith_b102 & reg_ints), \\
            "W102 B window must be CLEAN (arithmetic ADMIT face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W102-SHARD-0",
                                          "n1w102-0of12"), "W102 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W102-SHARD-11",
                                           "n1w102-11of12")
        assert SHARD_DIR.endswith("n1_w102") and OUT.endswith(
            "n1_w102_results.json"), "W102 path drift"
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 102):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W102 shard dir collides with W{wprev}"
        # W102 finalize cumulative deps: W17..W97 outputs ALL PRESENT
        # (landed chain head 577,948 = W97 bm-b r583 one-pass; W98/W99/
        # W100/W101 registered with finalizes NOT landed -- in-flight
        # upstream seats, honest note; the finalize merge loop derives
        # the wave set from registry keys at run time and stays
        # FAIL-CLOSED, r307 law).
        for _depw in range(17, 98):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W102 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): every
        # registered wave below 102 composes; wave 15 excluded by
        # design; SINGLE STATE (W2..W101 all registered -- no
        # two-state seat disclosure needed at this freeze).
        assert sorted(w for w in WAVE_CONFIGS if w < 102) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 102)], \\
            "W102 prior-wave set must derive from registry keys (no 15; " \\
            "W2..W101 registered single state)"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W102_PREREG.md")), \\
            "W102 per-wave prereg missing (materializer requirement)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W102 materializer face' in t2b:
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
            + LEG102
            + '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n')
    t2b = rep(t2b, A3, NEW3, eol2b, 'n1-leg102')
    save(FP2, t2b)
    print('edit3 selftest W102 leg landed (insert before T-141 selftest lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment ----------------------
t2c, eol2c = load(FP2)
if '+ W102 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('          "W101 row, r583 bm-a] "\n'
          '          "+ T-141 s2 ')
    SEG102 = ('          "W101 row, r583 bm-a] "\n'
              '          "+ W102 materializer face [same guard set, dep=W17..W97 "\n'
              '          "outputs ALL PRESENT (landed chain head 577,948 = W97 "\n'
              '          "bm-b r583 one-pass, K=211,320; FOUR in-flight upstream "\n'
              '          "seats W98 bm-a burned-unfinalized + W99 bm-c burned-"\n'
              '          "unfinalized + W100 bm-b burning + W101 bm-a burning -- "\n'
              '          "FAIL-CLOSED r307 at run time), NINETY-SECOND "\n'
              '          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows "\n'
              '          "91 + candidate; seat prose ordinal drift disclosed per "\n'
              '          "r359 law) bm-c\'s thirtieth owned claim per machine-derive "\n'
              '          "(engine_owner==bm-c rows 29 + candidate), engine_owner=bm-c "\n'
              '          "per engine de-throttle law O-20261001-2355 sec.2 own-"\n'
              '          "continuous-series (wave 102 = first FREE number after "\n'
              '          "the REGISTERED W101 row, SINGLE STATE zero seat gap; "\n'
              '          "seat published=reserved MSG-20261002-1642-bmc pushed to "\n'
              '          "origin a369ae045 BEFORE this freeze, r565 law), "\n'
              '          "A=arithmetic continuation from the registered W101 A "\n'
              '          "tail (247_004..249_003 CLEAN hops=0) + B=arithmetic "\n'
              '          "continuation from the registered W101 B tail "\n'
              '          "(59_201..59_400 CLEAN hops=0; ADMIT receipt "\n'
              '          "results/_r375bmc_w102_band_gate.py; W103+ projection A "\n'
              '          "249_004..251_003 CLEAN / B 59_401..59_600 CLEAN "\n'
              '          "disclosed for the next freezer; not a free pick -- "\n'
              '          "R250), law sec.4 W102 row, r375 bm-c] "\n'
              '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG102, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W102 segment landed (insert after W101 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W102 row ---------------------
ROW102 = """
- N1 波102（r375 bm-c 冻·prereg 时展行）：**第九十二枚引擎波·bm-c 第三十枚自有波〔机面 derive：engine_owner 行 91+本候选／engine_owner==bm-c 行 29+本候选·r359 律计数面以 gate 机输出为准（本机席位 MSG-20261002-1642-bmc prose 序数「第九十一枚/行 90」手算偏差如实披露）〕**·engine_owner=bm-c·SATURATION_ENGINE_LAW §1/§2 同 W10-W101 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-c 实例=常驻架构 v0.4-d20261002-03 mtime-reload——冻结 commit 后 LIVE 引擎下一 tick 自见新行=免杀重启免做·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 102=注册表 W101 行〔bm-a r583〕后首个自由号·单态零席位空档**（W100 bm-b+W101 bm-a 双行已落 origin·无 skip-past-published 链面）·**席位公示=MSG-20261002-1642-bmc**〔published=reserved r518-① 律·先于冻结 commit 推 origin a369ae045=r565 早可见性律〕】·本窗实况=**W97 finalize 已落账（净链头 577,948·K=211,320 合并池）+四在飞上游席（W98 bm-a 12/12 烧毕 finalize 待+W99 bm-c 12/12 烧毕 finalize 待+W100 bm-b 烧录在飞+W101 bm-a 烧录在飞）=本波 finalize 链序前置在飞（跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**·**带位（r375 机闸 derive 律·活注册表机证·单态收敛门·ADMIT 回执=results/_r375bmc_w102_band_gate.py rc0 实跑·hops A=0/B=0）**：**A-ext seed=247_004..249_003**（==W101 行 A 尾 247_003+1 起算术续带·步长 2_000·**CLEAN 零拒绝点**）；**B-ext exit seed=59_201..59_400**（==W101 行 B 尾 59_200+1 起算术续带·步长 200·**CLEAN 零拒绝点**；双侧算术续带 W92 r370/W100 r583 先例族）。R250：W102 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W102 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W102_PREREG.md（冻结件·锚=W97 finalize 实测值〔锚滚动律·单波跨锚自 W94 滚动至 W97·r576 锚滚律〕）·**W103+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 249_004..251_003 **CLEAN**；B 59_401..59_600 **CLEAN**（下波按法典 §4 表尾+全 registry 重 derive）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce2102\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW102.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W102 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    102: {"a": (247_004') == 1, 'FIX-B FAIL: W102 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W102"') == 1, 'FIX-B FAIL: W102 config not exactly once'
for w in range(58, 102):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W102 materializer face') == 2, \
    'FIX-B FAIL: W102 leg+summary must be exactly 2'
for w in range(48, 102):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce2102\uff08') == 1, 'FIX-B FAIL: canon W102 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W102 added per face')

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
print('FREEZE_EDITS_OK 102')
