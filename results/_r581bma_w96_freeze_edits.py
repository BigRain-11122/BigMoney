# -*- coding: utf-8 -*-
"""r581 bm-a W96 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening.

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED rows (W95 bm-b r580);
  every registered row signature survives exactly; exactly one new W96
  signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.

W96 = EIGHTY-SIXTH engine wave by MACHINE-DERIVE (engine_owner rows 85 +
candidate), bm-a's TWENTY-SIXTH owned (engine_owner==bm-a rows 25 +
candidate). First free number after the registered W95 row (SINGLE STATE,
zero seat gap -- W95 registered by bm-b r580, landed origin 70b32c101).
Seat published=reserved MSG-20261002-1531-bma pushed to origin 2819d0393
BEFORE this freeze (r565 early-visibility law).
Bands (single-state arithmetic continuation from the registered W95 tails):
  A 235_004..237_003 (W95 A tail 235_003 + 1, stride 2_000) CLEAN hops=0.
  B 57_701..57_900   (W95 B tail 57_700 + 1, stride 200)    CLEAN hops=0.
  ADMIT receipt results/_r581bma_w96_band_gate.py rc0.
W91 finalize LANDED at this freeze (chain head 564,748 = W91 bm-b r579
one-pass; K=198,120). THREE in-flight upstream seats (W92 bm-c + W93 bm-b
+ W94 bm-a -- all registered, finalize pending) -- finalize merge loop
stays FAIL-CLOSED r307 at run time. W97+ projection: A 237_004..239_003
CLEAN / B 57_901..58_100 REFUSED at SEED_REGISTRY 58_000 (in-band -> next
freezer pins per D-20261002-05; next freezer must re-derive).
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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 96))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 96)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 96)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[96] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '96: {"a": (235_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    95: {"a": (233_004, 235_003), "b_exit": (57_501, 57_700),\n'
          '         "engine_owner": "bm-b"},\n'
          '}\n')
    NEW = ('    95: {"a": (233_004, 235_003), "b_exit": (57_501, 57_700),\n'
           '         "engine_owner": "bm-b"},\n'
           '    # EIGHTY-SIXTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r581 bm-a\n'
           '    # freeze): engine_owner rows 85 + candidate; bm-a\'s\n'
           '    # twenty-sixth owned per machine-derive (engine_owner==bm-a\n'
           '    # rows 25 + candidate). Wave 96 = first free number after the\n'
           '    # registered W95 row (SINGLE STATE, zero seat gap; no\n'
           '    # published seat to skip). Seat published=reserved\n'
           '    # MSG-20261002-1531-bma pushed to origin 2819d0393 BEFORE\n'
           '    # this freeze per r565 early-visibility law.\n'
           '    # W91 finalize LANDED at this freeze (landed chain head\n'
           '    # 564,748 = W91 bm-b r579 one-pass; K=198,120). THREE\n'
           '    # in-flight upstream seats (W92 bm-c + W93 bm-b + W94 bm-a\n'
           '    # -- all registered, finalize pending) -- finalize merge\n'
           '    # loop stays FAIL-CLOSED r307 at run time.\n'
           '    # BOTH SIDES ARITHMETIC CONTINUATION from the registered W95\n'
           '    # tails, single state: A 235_004..237_003 CLEAN + B\n'
           '    # 57_701..57_900 CLEAN zero refusal points\n'
           '    # (machine-verified at prereg time, ADMIT receipt\n'
           '    # results/_r581bma_w96_band_gate.py rc0 hops 0/0; live\n'
           '    # SEED_REGISTRY + probe cluster 95_000..95_003 r335 leg +\n'
           '    # N3-R1 used-seed band 70_000..70_005 MSG-183x r529 leg).\n'
           '    # W97+ projection: A 237_004..239_003 CLEAN; B 57_901..58_100\n'
           '    # REFUSED at SEED_REGISTRY 58_000 (in-band -> next freezer\n'
           '    # pins per D-20261002-05; next freezer must re-derive,\n'
           '    # never transcribe).\n'
           '    # NOT a re-pick (R250: W96 bands were never assigned).\n'
           '    96: {"a": (235_004, 237_003), "b_exit": (57_701, 57_900),\n'
           '         "engine_owner": "bm-a"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[96] landed (anchor=W95 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[96] ---------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '96: {"batch": "PERPETUAL-N1-W96"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w95", "out_name": "n1_w95_results.json",\n'
          '                            "engine_owner": "bm-b"},\n')
    NEW2 = A2 + (
        '                       96: {"batch": "PERPETUAL-N1-W96",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W96_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; EIGHTY-SIXTH ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 85 + candidate; prose "\n'
        '                                       "ordinal drift disclosed per r359 law), own-series "\n'
        '                                       "continuation per O-20261001-2355 sec.2 (first-free-number "\n'
        '                                       "law over the registered W95 row, SINGLE STATE zero seat "\n'
        '                                       "gap; seat published=reserved MSG-20261002-1531-bma "\n'
        '                                       "PUSHED to origin BEFORE this freeze per r565 early-"\n'
        '                                       "visibility law), engine_owner=bm-a, wave 96: BOTH SIDES "\n'
        '                                       "ARITHMETIC CONTINUATION from the registered W95 tails, "\n'
        '                                       "single state CLEAN zero refusal points (A 235_004..237_003 "\n'
        '                                       "+ B 57_701..57_900; ADMIT receipt results/_r581bma_w96_band_"\n'
        '                                       "gate.py hops 0/0; W97+ projection: A 237_004..239_003 CLEAN "\n'
        '                                       "/ B 57_901..58_100 REFUSED at SEED_REGISTRY point 58_000 "\n'
        '                                       "in-band -> D-20261002-05 pin for the next freezer); "\n'
        '                                       "W91 finalize LANDED at this freeze (chain head 564,748, "\n'
        '                                       "K=198,120) + THREE in-flight upstream seats W92 bm-c + "\n'
        '                                       "W93 bm-b + W94 bm-a all registered finalize-pending -- "\n'
        '                                       "finalize merge loop stays FAIL-CLOSED r307 at run "\n'
        '                                       "time)"),\n'
        '                            "a_seed_base": 235_004,        # law sec.4 W96 A: 235_004..237_003 (arithmetic continuation from the registered W95 tail)\n'
        '                            "b_exit_seed_base": 57_701,   # law sec.4 W96 B: 57_701..57_900 (arithmetic continuation from the registered W95 tail)\n'
        '                            "shard_subdir": "n1_w96", "out_name": "n1_w96_results.json",\n'
        '                            "engine_owner": "bm-a"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[96] landed (anchor=W95 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W96 leg --------------
LEG96 = '''
    # --- W96 materializer face (r581 bm-a freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-a's
    #     twenty-sixth owned per machine-derive (engine_owner==bm-a
    #     rows 25 + candidate); wave 96 = first free number after the
    #     registered W95 row (SINGLE STATE, zero seat gap). Seat
    #     published=reserved MSG-20261002-1531-bma pushed to origin
    #     2819d0393 BEFORE this freeze, r565 law. EIGHTY-SIXTH engine
    #     wave BY MACHINE-DERIVE (engine_owner rows 85 + candidate;
    #     prose ordinal drift disclosed per r359 law). W91 finalize
    #     LANDED (chain head 564,748, K=198,120) + THREE in-flight
    #     upstream seats W92 bm-c + W93 bm-b + W94 bm-a (all
    #     registered, finalize pending) -- FAIL-CLOSED r307 at run
    #     time. ADMIT receipt results/_r581bma_w96_band_gate.py;
    #     not a re-pick (R250: W96 bands were never assigned).
    _set_wave(96)
    try:
        assert WAVE_CONFIGS[96]["a_seed_base"] == pf.N1_BANDS[96]["a"][0], \\
            "W96 A band drift vs law mirror"
        assert WAVE_CONFIGS[96]["b_exit_seed_base"] == \\
            pf.N1_BANDS[96]["b_exit"][0], "W96 B band drift vs law mirror"
        assert WAVE_CONFIGS[96].get("engine_owner") == \\
            pf.N1_BANDS[96].get("engine_owner") == "bm-a", \\
            "W96 engine_owner drift (law mirror parity)"
        w96_a = {A_SEED_BASE + j for j in range(A_N)}
        w96_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w96_a & w96_b), "W96 A/B band overlap"
        assert not (w96_a & reg_ints) and not (w96_b & reg_ints), \\
            "W96 hits SEED_REGISTRY"
        for nm, band in (("A", w96_a), ("B", w96_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W96 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W96 {nm} hits W1"
            assert not (band & probes), f"W96 {nm} hits probe seeds"
        # registered row parity (r307 pinned constants, recent estate)
        assert pf.N1_BANDS[93] == {"a": (229_004, 231_003),
                                   "b_exit": (57_101, 57_300),
                                   "engine_owner": "bm-b"}, \\
            "registered W93 row parity drift (r307; bm-b r579)"
        assert pf.N1_BANDS[94] == {"a": (231_004, 233_003),
                                  "b_exit": (57_301, 57_500),
                                  "engine_owner": "bm-a"}, \\
            "registered W94 row parity drift (r307; bm-a r580, heal 4e6a5e7d0)"
        assert pf.N1_BANDS[95] == {"a": (233_004, 235_003),
                                  "b_exit": (57_501, 57_700),
                                  "engine_owner": "bm-b"}, \\
            "registered W95 row parity drift (r307; bm-b r580)"
        # prior-wave disjointness W2..W95 (ALL registered at this
        # freeze; single state, no in-flight registration gap below 96)
        for wprev in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
                [w for w in range(16, 96)]:
            assert not (w96_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W96 A hits W{wprev}"
            assert not (w96_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W96 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W96 clears it.
        n3r1_used96 = set(range(70_000, 70_006))
        assert not (w96_a & n3r1_used96) and not (w96_b & n3r1_used96), \\
            "W96 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w96_a & lfc_actual12) and not (w96_b & lfc_actual12), \\
            "W96 bands must clear the lfc actual draw range"
        assert not (w96_a & options_actual12) and \\
            not (w96_b & options_actual12), \\
            "W96 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W96 row, r581): single-state arithmetic
        # continuation from the registered W95 tails, zero refusal points.
        assert WAVE_CONFIGS[96]["a_seed_base"] == 235_004 == 235_003 + 1, \\
            "W96 A must start at the registered W95 A end + 1"
        assert WAVE_CONFIGS[96]["b_exit_seed_base"] == 57_701 == 57_700 + 1, \\
            "W96 B must start at the registered W95 B end + 1"
        arith_a96 = set(range(235_004, 237_004))
        assert not (arith_a96 & reg_ints), \\
            "W96 A window must be CLEAN (zero-skip ADMIT face)"
        arith_b96 = set(range(57_701, 57_901))
        assert not (arith_b96 & reg_ints), \\
            "W96 B window must be CLEAN (zero-skip ADMIT face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W96-SHARD-0",
                                          "n1w96-0of12"), "W96 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W96-SHARD-11",
                                           "n1w96-11of12")
        assert SHARD_DIR.endswith("n1_w96") and OUT.endswith(
            "n1_w96_results.json"), "W96 path drift"
        for wprev in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
                [w for w in range(16, 96)]:
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W96 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W96_PREREG.md")), \\
            "W96 per-wave prereg missing (materializer requirement)"
        # W96 finalize cumulative deps: W17..W91 outputs ALL PRESENT
        # (landed chain head 564,748 = W91; W92/W93/W94 registered with
        # finalizes NOT landed -- in-flight upstream seats, honest note;
        # the finalize merge loop derives the wave set from registry
        # keys at run time and stays FAIL-CLOSED, r307 two-state law).
        for _depw in range(17, 92):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W96 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): all
        # waves below 96 registered at this freeze (single state, zero
        # seat gap; wave 15 excluded by design).
        assert sorted(w for w in WAVE_CONFIGS if w < 96) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 96)], \\
            "W96 prior-wave set must derive from registry keys (no 15; " \\
            "W2..W95 ALL registered at this freeze)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W96 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    A3 = ('_set_wave(2)\n'
          '\n'
          '\n'
          '\n'
          '\n'
          '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim')
    A3X = A3.replace('\n', eol2b)
    assert t2b.count(A3X) == 1, f'selftest anchor not unique: {t2b.count(A3X)}'
    t2b = t2b.replace(A3X, '_set_wave(2)' + eol2b * 4 + LEG96.replace('\n', eol2b) + A3X)
    save(FP2, t2b)
    print('edit3 selftest W96 leg landed (insert before T-141 selftest lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment ----------------------
t2c, eol2c = load(FP2)
if '+ W96 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('          "law sec.4 W95 row, r580 bm-b] "\n'
          '          "+ T-141 s2 ')
    SEG96 = ('          "law sec.4 W95 row, r580 bm-b] "\n'
             '          "+ W96 materializer face [same guard set, dep=W17..W91 "\n'
             '          "outputs ALL PRESENT (landed chain head 564,748 = W91 "\n'
             '          "bm-b r579 one-pass, K=198,120; THREE in-flight upstream "\n'
             '          "seats W92 bm-c + W93 bm-b + W94 bm-a all registered "\n'
             '          "finalize-pending -- FAIL-CLOSED r307 at run time), "\n'
             '          "EIGHTY-SIXTH ENGINE-OWNED WAVE BY MACHINE-DERIVE "\n'
             '          "(engine_owner rows 85 + candidate; prose ordinal drift "\n'
             '          "disclosed per r359 law) bm-a\'s twenty-sixth owned "\n'
             '          "claim per machine-derive (engine_owner==bm-a rows 25 "\n'
             '          "+ candidate), engine_owner=bm-a per engine de-throttle "\n'
             '          "law O-20261001-2355 sec.2 own-continuous-series (wave 96 "\n'
             '          "= first FREE number after the registered W95 row, SINGLE "\n'
             '          "STATE zero seat gap; seat published=reserved "\n'
             '          "MSG-20261002-1531-bma pushed to origin BEFORE this "\n'
             '          "freeze, r565 law), BOTH SIDES ARITHMETIC CONTINUATION "\n'
             '          "from the registered W95 tails single-state (A "\n'
             '          "235_004..237_003 CLEAN + B 57_701..57_900 CLEAN zero "\n'
             '          "refusal points; ADMIT receipt results/_r581bma_w96_band_"\n'
             '          "gate.py hops 0/0; W97+ projection A 237_004..239_003 "\n'
             '          "CLEAN / B 57_901..58_100 REFUSED at 58_000 disclosed for "\n'
             '          "the next freezer; not a free pick -- R250), N3-R1 "\n'
             '          "used-seed leg, probe-seed cluster leg, law sec.4 W96 "\n'
             '          "row, r581 bm-a] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG96, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W96 segment landed (insert after W95 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W96 row ---------------------
ROW96 = """
- N1 波96（r581 bm-a 冻·prereg 时展行）：**第八十六枚引擎波·bm-a 第二十六枚自有波〔机面 derive：engine_owner 行 85+本候选／engine_owner==bm-a 行 25+本候选〕**·engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 同 W10-W95 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-a 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启免做·W44/W45/W48/W54/W57/W62/W64/W68/W73/W75/W77/W81/W84/W86/W87/W90/W94 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 96=注册表 W95 行后首个自由号·单态零席位空档**（W95 bm-b r580 已注册=表尾实况·无 skip-past-published 链面）·**席位公示=MSG-20261002-1531-bma**〔published=reserved r518-① 律·先于冻结 commit 推 origin 2819d0393=r565 早可见性律〕】·本窗实况=**W91 finalize 已落账（净链头 564,748·K=198,120 合并池）+三在飞上游席（W92 bm-c 12/12 烧毕 finalize 待+W93 bm-b 烧录中+W94 bm-a 12/12 烧毕本窗 finalize 待）=本波 finalize 链序前置在飞（跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**·**带位（r581 机闸 derive 律·活注册表机证·单态收敛门·ADMIT 回执=results/_r581bma_w96_band_gate.py rc0 实跑·hops 0/0）**：**A-ext seed=235_004..237_003**（==W95 行 A 尾 235_003+1 起·步长 2_000·**CLEAN 零拒绝点**·纯算术续带）；**B-ext exit seed=57_701..57_900**（==W95 行 B 尾 57_700+1 起·步长 200·**CLEAN 零拒绝点**·纯算术续带）。R250：W96 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W96 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W96_PREREG.md（冻结件·锚=W91 finalize 实测值〔锚滚动律·单波跨锚自 W76 滚动至 W91〕）·**W97+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 237_004..239_003 **CLEAN**；B 57_901..58_100 **REFUSED [58_000]**（算术位撞 SEED_REGISTRY 值·带内命中——下波按法典 §4 钉死行/pin 链 derive 首净窗）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce296\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW96.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W96 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    96: {"a": (235_004') == 1, 'FIX-B FAIL: W96 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W96"') == 1, 'FIX-B FAIL: W96 config not exactly once'
for w in range(58, 96):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W96 materializer face') == 2, \
    'FIX-B FAIL: W96 leg+summary must be exactly 2'
for w in range(48, 96):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce296\uff08') == 1, 'FIX-B FAIL: canon W96 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W96 added per face')

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
print('FREEZE_EDITS_OK 96')
