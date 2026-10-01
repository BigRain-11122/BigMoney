# -*- coding: utf-8 -*-
"""r561 bm-a W57 freeze edits -- MSG-0640 cure: INSERT-NOT-REPLACE hardening.

FIX-A (origin-blob freshness): every tracked edit target must be content-equal
  to origin/main BEFORE any edit runs (git-native EOL-aware compare). Kills
  the r559 stale-base clobber (W54 freeze edited a pre-W55 base and 1:1
  replaced bm-b's registered W55 content on push -- r519-family content
  variant: fresh parent does NOT imply fresh payload).
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W56, bm-b's),
  and after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W57 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file (content-level
  deletion-set self-check -- file-level D-status staging is blind to
  whole-file content replacement).

W57 = FORTY-SIXTH engine wave, bm-a's FOURTEENTH owned (W56 slot taken
same-window by bm-b r560 -- this machine's W56 drafts yielded unpushed
and unburned, zero pollution, yield_record in the round report).
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
                     f'origin/main -- the working tree is missing origin content '
                     f'(another machine\'s rows?) -- checkout origin version first '
                     f'(r559 clobber cure; pure insertions from this tool\'s own '
                     f'idempotent edits are the only legal pre-state)')
print('FIX-A: all 3 tracked edit targets show zero deletions vs origin/main (fresh base)')

# ---------------- survival signature baseline (FIX-B) ------------------------
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20,
             21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
             37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52,
             53, 54, 55, 56]
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {'w54leg': n1_0.count('W54 materializer face'),
       'w55leg': n1_0.count('W55 materializer face'),
       'w56leg': n1_0.count('W56 materializer face')}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in (48, 49, 50, 51, 52, 53, 54, 55, 56)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[57] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '57: {"a": (157_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    56: {"a": (155_004, 157_003), "b_exit": (47_201, 47_400),\n'
          '         "engine_owner": "bm-b"},\n')
    NEW = ('    56: {"a": (155_004, 157_003), "b_exit": (47_201, 47_400),\n'
           '         "engine_owner": "bm-b"},\n'
           '    # FORTY-SIXTH ENGINE-OWNED WAVE (r561 bm-a freeze): bm-a\'s\n'
           '    # FOURTEENTH owned wave. Wave 57 = next free number after the\n'
           '    # registered W56 row (own-series continuation under the\n'
           '    # de-throttle law; bm-a\'s previous wave W54 burned 12/12 and\n'
           '    # delivered to origin at r561 S0 surgical, finalize\n'
           '    # chain-pending; W53/W54/W55/W56 = FOUR in-flight upstream\n'
           '    # seats -- coexist by band disjointness per r531 law).\n'
           '    # BOTH SIDES = ARITHMETIC CONTINUATION from the W56 row tail,\n'
           '    # no skip: A 157_004..159_003 (= W56 A end 157_003 + 1) and\n'
           '    # B 47_401..47_600 (= W56 B end 47_400 + 1) -- both windows\n'
           '    # CLEAN per the W56 row W57+ WARNING projections\n'
           '    # (bm-b r560 freeze gate projection leg + this freeze\'s\n'
           '    # machine re-derive, r535 law). Machine-verified at prereg\n'
           '    # time (results/_r561bma_w57_band_gate.py ADMIT receipt vs\n'
           '    # the 54-row pre-W57 table + live SEED_REGISTRY values +\n'
           '    # probe cluster 95_000..95_003 r335 discovery leg + N3-R1\n'
           '    # used-seed band 70_000..70_005 MSG-183x r529 mandatory leg;\n'
           '    # origin slot vacancy machine-checked). NOT a re-pick\n'
           '    # (R250: W57 bands were never assigned).\n'
           '    57: {"a": (157_004, 159_003), "b_exit": (47_401, 47_600),\n'
           '         "engine_owner": "bm-a"},\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[57] landed (anchor=W56 row, insert)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[57] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '57: {"batch": "PERPETUAL-N1-W57"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w56", "out_name": "n1_w56_results.json",\n'
          '                            "engine_owner": "bm-b"},\n'
          '                       }')
    NEW2 = ('                            "shard_subdir": "n1_w56", "out_name": "n1_w56_results.json",\n'
            '                            "engine_owner": "bm-b"},\n'
            '                       57: {"batch": "PERPETUAL-N1-W57",\n'
            '                            "prereg": ("research/PERPETUAL_N1_W57_PREREG.md (wave-level frozen "\n'
            '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
            '                                       "new seed bands only; FORTY-SIXTH ENGINE-OWNED WAVE, "\n'
            '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
            '                                       "(first-free-number law over the registered W56 row), "\n'
            '                                       "engine_owner=bm-a, wave 57 BOTH SIDES ARITHMETIC "\n'
            '                                       "CONTINUATION no skip (A 157_004..159_003, B "\n'
            '                                       "47_401..47_600); W1..W52 finalizes ALL LANDED at "\n'
            '                                       "this freeze (ledger head 478,948), W53/W54/W55/W56 "\n'
            '                                       "registered with finalizes NOT landed = FOUR "\n'
            '                                       "in-flight upstream seats, finalize merge loop "\n'
            '                                       "derives the wave set from registry keys at run "\n'
            '                                       "time and stays FAIL-CLOSED on any "\n'
            '                                       "not-yet-finalized upstream seat, r307 two-state "\n'
            '                                       "law)"),\n'
            '                            "a_seed_base": 157_004,        # law sec.4 W57 A: 157_004..159_003 (arithmetic continuation)\n'
            '                            "b_exit_seed_base": 47_401,    # law sec.4 W57 B: 47_401..47_600 (arithmetic continuation)\n'
            '                            "shard_subdir": "n1_w57", "out_name": "n1_w57_results.json",\n'
            '                            "engine_owner": "bm-a"},\n'
            '                       }')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[57] landed (anchor=W56 entry tail, insert)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W57 leg --------------
LEG57 = '''
    # --- W57 materializer face (r561 bm-a freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2):
    #     bm-a's FOURTEENTH owned wave; wave 57 = next free number
    #     after the registered W56 row (bm-a's previous wave W54
    #     burned 12/12, products delivered to origin at r561 S0,
    #     finalize chain-pending; W53/W54/W55/W56 = FOUR in-flight
    #     upstream seats at this freeze, finalize merge loop
    #     FAIL-CLOSED at run time per r307 two-state law). BOTH
    #     SIDES ARITHMETIC CONTINUATION from the W56 tail no skip
    #     (A 157_004..159_003 / B 47_401..47_600, both CLEAN == the
    #     W56 row W57+ published projection verbatim -- bm-b r560
    #     freeze gate projection leg + this gate machine re-derive;
    #     ADMIT receipt results/_r561bma_w57_band_gate.py; not a
    #     re-pick -- R250: W57 bands were never assigned) --
    _set_wave(57)
    try:
        assert WAVE_CONFIGS[57]["a_seed_base"] == pf.N1_BANDS[57]["a"][0], \\
            "W57 A band drift vs law mirror"
        assert WAVE_CONFIGS[57]["b_exit_seed_base"] == \\
            pf.N1_BANDS[57]["b_exit"][0], "W57 B band drift vs law mirror"
        assert WAVE_CONFIGS[57].get("engine_owner") == \\
            pf.N1_BANDS[57].get("engine_owner") == "bm-a", \\
            "W57 engine_owner drift (law mirror parity)"
        w57_a = {A_SEED_BASE + j for j in range(A_N)}
        w57_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w57_a & w57_b), "W57 A/B band overlap"
        assert not (w57_a & reg_ints) and not (w57_b & reg_ints), \\
            "W57 hits SEED_REGISTRY"
        for nm, band in (("A", w57_a), ("B", w57_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W57 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W57 {nm} hits W1"
            assert not (band & probes), f"W57 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W54/W55/W56
        # are REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly.
        assert pf.N1_BANDS[54] == {"a": (151_004, 153_003),
                                   "b_exit": (46_601, 46_800),
                                   "engine_owner": "bm-a"}, \\
            "registered W54 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[55] == {"a": (153_004, 155_003),
                                   "b_exit": (47_001, 47_200),
                                   "engine_owner": "bm-b"}, \\
            "registered W55 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[56] == {"a": (155_004, 157_003),
                                   "b_exit": (47_201, 47_400),
                                   "engine_owner": "bm-b"}, \\
            "registered W56 row parity drift (r307 two-state)"
        # prior-wave disjointness incl. W48..W56 (all registered;
        # W53/W54/W55/W56 finalizes in flight -- coexist by band
        # disjointness per r531).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56):
            assert not (w57_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W57 A hits W{wprev}"
            assert not (w57_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W57 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W57 clears it.
        n3r1_used57 = set(range(70_000, 70_006))
        assert not (w57_a & n3r1_used57) and not (w57_b & n3r1_used57), \\
            "W57 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w57_a & lfc_actual12) and not (w57_b & lfc_actual12), \\
            "W57 bands must clear the lfc actual draw range"
        assert not (w57_a & options_actual12) and \\
            not (w57_b & options_actual12), \\
            "W57 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W57 row, r561): BOTH SIDES
        # ARITHMETIC CONTINUATION (A 157_004 = W56 A end 157_003 + 1;
        # B 47_401 = W56 B end 47_400 + 1, both windows CLEAN -- no
        # skip family).
        assert WAVE_CONFIGS[57]["a_seed_base"] == 157_004 == 157_003 + 1, \\
            "W57 A must start at the registered W56 A end + 1 " \\
            "(arithmetic continuation window 157_004..159_003 CLEAN -- " \\
            "no skip family)"
        assert WAVE_CONFIGS[57]["b_exit_seed_base"] == 47_401 == 47_400 + 1, \\
            "W57 B must start at the registered W56 B end + 1 " \\
            "(arithmetic continuation window 47_401..47_600 CLEAN -- " \\
            "no skip family)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W57-SHARD-0",
                                          "n1w57-0of12"), "W57 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W57-SHARD-11",
                                          "n1w57-11of12")
        assert SHARD_DIR.endswith("n1_w57") and OUT.endswith(
            "n1_w57_results.json"), "W57 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W57 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W57_PREREG.md")), \\
            "W57 per-wave prereg missing (materializer requirement)"
        # W57 finalize cumulative deps: W17..W52 outputs ALL PRESENT
        # (static landed seats; chain head 478,948); W53/W54/W55/W56 =
        # REGISTERED with finalizes NOT landed (FOUR in-flight
        # upstream seats -- the finalize merge loop derives the wave
        # set from registry keys at run time and stays FAIL-CLOSED on
        # any not-yet-finalized upstream seat, r307 two-state law).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                      43, 44, 45, 46, 47, 48, 49, 50, 51, 52):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W57 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 57 (no 15; incl.
        # 48..56 -- all registered, W53/W54/W55/W56 finalizes in flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 57) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56], \\
            "W57 prior-wave set must derive from registry keys (no 15, " \\
            "incl. 48..56)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W57 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    A3 = '\n    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG57.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W57 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 5th face) ------
t2c, eol2c = load(FP2)
if '+ W57 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('law sec.4 W56 row, r560 bm-b] "\n'
          '          "+ T-141 s2 ')
    SEG57 = ('law sec.4 W56 row, r560 bm-b] "\n'
             '          "+ W57 materializer face [same guard set, dep=W17..W52 "\n'
             '          "outputs ALL PRESENT (chain head 478,948 post the bm-c "\n'
             '          "r351 triple finalize); W53/W54/W55/W56 registered with "\n'
             '          "finalizes NOT landed at this freeze = FOUR in-flight "\n'
             '          "chain seats, finalize merge loop stays FAIL-CLOSED at "\n'
             '          "run time per r307 two-state law), FORTY-SIXTH "\n'
             '          "ENGINE-OWNED WAVE bm-a\'s fourteenth owned claim "\n'
             '          "engine_owner=bm-a per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series (wave 57 = "\n'
             '          "first FREE number after the registered W56 row; the W56 "\n'
             '          "slot was taken same-window by bm-b r560 -- this machine\'s "\n'
             '          "W56 drafts yielded unpushed and unburned, zero pollution), "\n'
             '          "BOTH SIDES ARITHMETIC CONTINUATION from the W56 tail no "\n'
             '          "skip (A 157_004..159_003 / B 47_401..47_600 both CLEAN "\n'
             '          "machine-derived per the W56 row W57+ WARNING; ADMIT "\n'
             '          "receipt results/_r561bma_w57_band_gate.py; not a free "\n'
             '          "pick -- R250), N3-R1 used-seed leg, probe-seed cluster "\n'
             '          "leg, law sec.4 W57 row, r561 bm-a] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG57, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W57 segment landed (insert after W56 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W57 row -------------------
ROW57 = """
- N1 波57（r561 bm-a 冻·prereg 时展行）：**第四十六枚引擎波·bm-a 第十四枚自有波**·engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 同 W10-W56 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-a 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启·W44/W45/W48/W54 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**本机上波 W54 已烧毕 12/12 且产品件已交付 origin**（r559 冻结→tick 自燃 12/12→r561 S0 外科合并交付 39b6658c7·r310 完备性门；W54 finalize 链序候 W53 前置）→零隔接力·**波号 57=注册表 W56 行后首个自由号**（r511 表尾锁例冻结前 fetch 实核：W56 号位已被 bm-b r560 同窗注册=本机 W56 草稿零推零烧纯让路·yield_record 入轮报告）·冻结前 fetch 实核表尾时 W57 号位净空】·**双面算术续带零跳位（r535 机闸 derive 律）**：W56 行 W57+ 警示投影 **A 157_004..159_003 CLEAN／B 47_401..47_600 CLEAN**（bm-b r560 冻结窗 gate 投影腿机证+本波 bm-a gate 复核逐字同）→本波 **A-ext seed=157_004..159_003**（**A 面算术续带零跳位**==W56 A 尾 157_003+1·步长逐字）·**B-ext exit seed=47_401..47_600**（**B 面算术续带零跳位**==W56 B 尾 47_400+1·步长逐字·双侧零跳位=W56 行公示投影逐位）·【机证净空——leg0 五十五键（54 注册行+候选）+leg0b W56 行 W57+ 警示 prose 在场校验+leg1-A/leg1-B 双侧算术 CLEAN 机证+leg2 双侧首净窗==候选逐位+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验·测量面零结果可钓·**MSG-0640 三修工具**（编辑前 origin-blob 等值断言+锚=最后注册行+行存活核查+推送前纯增量 diff 断言）〕·ADMIT 回执=results/_r561bma_w57_band_gate.py·r561 bm-a 起草窗实跑】·扫描面=pre-W57 五十四行 N1 带表【含 W52 行 147_004..149_003/46_201..46_400〔r351 bm-c·finalize 已落账 K=112,320·**净账本链头 478,948**〕·W53 行 149_004..151_003/46_401..46_600〔r351 bm-c·注册在飞·finalize 未落账〕·W54 行 151_004..153_003/46_601..46_800〔r559 bm-a·本机·12/12 烧毕交付 origin·finalize 未落账〕·W55 行 153_004..155_003/47_001..47_200〔r559 bm-b·12/12 烧毕交付 origin·finalize 未落账〕·W56 行 155_004..157_003/47_201..47_400〔r560 bm-b·注册在飞·finalize 未落账〕】·**四在飞上游席披露：本波 finalize 链序前置=W53→W54→W55→W56 四连落账·FAIL-CLOSED r307 两态律**·带域不相交·W1 ext·v1 在用带·SEED_REGISTRY 全键（int 值全清·LOWAMP-P1/P2/P3 键 20.33M 域零交集）·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·lfc 实际抽带 30_000..30_099·options_wave2 实际抽带 63_000..63_049·leg-3e 实际流避让。**N2/N4 让位注记**：本波 A 带 157_004..159_003——N2/N4 波级 prereg 冻结时按本表防撞律回避该域。**W58+ 警示**：A +2_000 算术位（159_004..161_003）投影与 B +200 算术位（47_601..47_800）投影均以本波带闸回执 W58+ 投影腿机证为准（机闸 derive 非 prose 转抄·r535 律·去节流令下=首个自由号法·无座位指派——W58 prereg 仍照例带闸复核）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 波57（r561 bm-a' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- 每波 finalize 后：`science_gates.append_ledger` 落行'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW57.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W57 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    57: {"a": (157_004') == 1, 'FIX-B FAIL: W57 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W57"') == 1, 'FIX-B FAIL: W57 config not exactly once'
for leg, base in (('W54 materializer face', 'w54leg'),
                  ('W55 materializer face', 'w55leg'),
                  ('W56 materializer face', 'w56leg')):
    assert n11.count(leg) == BASE_SIGS[base], f'FIX-B FAIL: {leg} lost'
assert n11.count('W57 materializer face') == 2, \
    'FIX-B FAIL: W57 leg+summary must be exactly 2'
for w in (48, 49, 50, 51, 52, 53, 54, 55, 56):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce257\uff08') == 1, 'FIX-B FAIL: canon W57 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W57 added per face')

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
