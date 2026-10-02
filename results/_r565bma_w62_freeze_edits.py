# -*- coding: utf-8 -*-
"""r565 bm-a W62 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r561 lineage).

FIX-A (origin-blob freshness): every tracked edit target must be content-equal
  to origin/main BEFORE any edit runs. Kills the r559 stale-base clobber
  (live-fire catch this window at the W61 collision: aborted pre-edit,
  zero pollution, pure yield).
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W61, bm-b's),
  and after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W62 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W62 = FIFTY-FIRST engine wave, bm-a's fourteenth owned per machine-derive
(engine_owner==bm-a rows 13 + candidate). Seat declared published=reserved
(MSG-20261002-0818-bma, r518-1 law). W61 = ONE in-flight upstream seat
(bm-b r564, shards burning, finalize not landed -> FAIL-CLOSED r307).
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
                     f'(r559 clobber cure; pure insertions from this tool\'s own '
                     f'idempotent edits are the only legal pre-state)')
print('FIX-A: all 3 tracked edit targets show zero deletions vs origin/main (fresh base)')

# ---------------- survival signature baseline (FIX-B) ------------------------
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20,
             21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
             37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52,
             53, 54, 55, 56, 57, 58, 59, 60, 61]
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {'w58leg': n1_0.count('W58 materializer face'),
       'w59leg': n1_0.count('W59 materializer face'),
       'w60leg': n1_0.count('W60 materializer face'),
       'w61leg': n1_0.count('W61 materializer face')}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in (48, 49, 50, 51, 52, 53, 54, 55, 56,
                                                    57, 58, 59, 60, 61)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[62] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '62: {"a": (167_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    61: {"a": (165_004, 167_003), "b_exit": (48_401, 48_600),\n'
          '         "engine_owner": "bm-b"},\n'
          '}\n')
    NEW = ('    61: {"a": (165_004, 167_003), "b_exit": (48_401, 48_600),\n'
           '         "engine_owner": "bm-b"},\n'
           '    # FIFTY-FIRST ENGINE-OWNED WAVE (r565 bm-a freeze): bm-a\'s\n'
           '    # fourteenth owned per machine-derive (engine_owner==bm-a\n'
           '    # rows 13 + candidate). Wave 62 = next free number after the\n'
           '    # registered W61 row (seat declared published=reserved\n'
           '    # MSG-20261002-0818-bma, r518-1 law; W61 bm-b r564 = ONE\n'
           '    # in-flight upstream seat at this freeze, shards burning,\n'
           '    # finalize chain-pending FAIL-CLOSED r307). BOTH SIDES =\n'
           '    # ARITHMETIC CONTINUATION from the W61 row tail, no skip: A\n'
           '    # 167_004..169_003 (= W61 A end 167_003 + 1) and B\n'
           '    # 48_601..48_800 (= W61 B end 48_600 + 1) -- both windows\n'
           '    # CLEAN per the W61 row W62+ WARNING projections\n'
           '    # (bm-b r564 freeze gate projection leg + this freeze\'s\n'
           '    # machine re-derive, r535 law). Machine-verified at prereg\n'
           '    # time (results/_r565bma_w62_band_gate.py ADMIT receipt vs\n'
           '    # the 60-row pre-W62 table + live SEED_REGISTRY values +\n'
           '    # probe cluster 95_000..95_003 r335 discovery leg + N3-R1\n'
           '    # used-seed band 70_000..70_005 MSG-183x r529 mandatory leg;\n'
           '    # origin slot vacancy machine-checked). NOT a re-pick\n'
           '    # (R250: W62 bands were never assigned).\n'
           '    62: {"a": (167_004, 169_003), "b_exit": (48_601, 48_800),\n'
           '         "engine_owner": "bm-a"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[62] landed (anchor=W61 row, insert)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[62] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '62: {"batch": "PERPETUAL-N1-W62"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w61", "out_name": "n1_w61_results.json",\n'
          '                            "engine_owner": "bm-b"},\n'
          '                       }')
    NEW2 = ('                            "shard_subdir": "n1_w61", "out_name": "n1_w61_results.json",\n'
            '                            "engine_owner": "bm-b"},\n'
            '                       62: {"batch": "PERPETUAL-N1-W62",\n'
            '                            "prereg": ("research/PERPETUAL_N1_W62_PREREG.md (wave-level frozen "\n'
            '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
            '                                       "new seed bands only; FIFTY-FIRST ENGINE-OWNED WAVE, "\n'
            '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
            '                                       "(first-free-number law over the registered W61 row; "\n'
            '                                       "seat declared published=reserved MSG-20261002-0818-bma), "\n'
            '                                       "engine_owner=bm-a, wave 62 BOTH SIDES ARITHMETIC "\n'
            '                                       "CONTINUATION no skip (A 167_004..169_003 / B "\n'
            '                                       "48_601..48_800 machine-derived CLEAN == the W61 row "\n'
            '                                       "W62+ published projection verbatim); W1..W60 finalizes "\n'
            '                                       "ALL LANDED at this freeze (W60 bm-c r355 one-pass "\n'
            '                                       "K=129,920, ledger head 496,548), W61 bm-b r564 = ONE "\n'
            '                                       "in-flight upstream seat (shards burning, finalize "\n'
            '                                       "chain-pending FAIL-CLOSED r307)"),\n'
            '                            "a_seed_base": 167_004,        # law sec.4 W62 A: 167_004..169_003 (arithmetic continuation)\n'
            '                            "b_exit_seed_base": 48_601,    # law sec.4 W62 B: 48_601..48_800 (arithmetic continuation)\n'
            '                            "shard_subdir": "n1_w62", "out_name": "n1_w62_results.json",\n'
            '                            "engine_owner": "bm-a"},\n'
            '                       }')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[62] landed (anchor=W61 entry tail, insert)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W62 leg --------------
LEG62 = '''
    # --- W62 materializer face (r565 bm-a freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2):
    #     bm-a's fourteenth owned per machine-derive (engine_owner==bm-a
    #     rows 13 + candidate); wave 62 = next free number after the
    #     registered W61 row (seat declared published=reserved
    #     MSG-20261002-0818-bma; W61 bm-b r564 = ONE in-flight upstream
    #     seat at this freeze, shards burning, finalize chain-pending
    #     FAIL-CLOSED r307). BOTH SIDES ARITHMETIC CONTINUATION from
    #     the W61 tail no skip (A 167_004..169_003 / B 48_601..48_800
    #     both CLEAN machine-derived == the W61 row W62+ published
    #     projection verbatim; ADMIT receipt
    #     results/_r565bma_w62_band_gate.py; not a re-pick -- R250:
    #     W62 bands were never assigned) --
    _set_wave(62)
    try:
        assert WAVE_CONFIGS[62]["a_seed_base"] == pf.N1_BANDS[62]["a"][0], \\
            "W62 A band drift vs law mirror"
        assert WAVE_CONFIGS[62]["b_exit_seed_base"] == \\
            pf.N1_BANDS[62]["b_exit"][0], "W62 B band drift vs law mirror"
        assert WAVE_CONFIGS[62].get("engine_owner") == \\
            pf.N1_BANDS[62].get("engine_owner") == "bm-a", \\
            "W62 engine_owner drift (law mirror parity)"
        w62_a = {A_SEED_BASE + j for j in range(A_N)}
        w62_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w62_a & w62_b), "W62 A/B band overlap"
        assert not (w62_a & reg_ints) and not (w62_b & reg_ints), \\
            "W62 hits SEED_REGISTRY"
        for nm, band in (("A", w62_a), ("B", w62_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W62 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W62 {nm} hits W1"
            assert not (band & probes), f"W62 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W59/W60/W61
        # are REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly.
        assert pf.N1_BANDS[59] == {"a": (161_004, 163_003),
                                   "b_exit": (48_001, 48_200),
                                   "engine_owner": "bm-b"}, \\
            "registered W59 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[60] == {"a": (163_004, 165_003),
                                   "b_exit": (48_201, 48_400),
                                   "engine_owner": "bm-c"}, \\
            "registered W60 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[61] == {"a": (165_004, 167_003),
                                   "b_exit": (48_401, 48_600),
                                   "engine_owner": "bm-b"}, \\
            "registered W61 row parity drift (r307 two-state)"
        # prior-wave disjointness incl. W48..W61 (all registered; W61
        # in flight -- coexist by band disjointness per r531).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61):
            assert not (w62_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W62 A hits W{wprev}"
            assert not (w62_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W62 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W62 clears it.
        n3r1_used62 = set(range(70_000, 70_006))
        assert not (w62_a & n3r1_used62) and not (w62_b & n3r1_used62), \\
            "W62 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w62_a & lfc_actual12) and not (w62_b & lfc_actual12), \\
            "W62 bands must clear the lfc actual draw range"
        assert not (w62_a & options_actual12) and \\
            not (w62_b & options_actual12), \\
            "W62 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W62 row, r565): BOTH SIDES ARITHMETIC
        # CONTINUATION (A 167_004 = W61 A end 167_003 + 1; B 48_601 =
        # W61 B end 48_600 + 1; both windows CLEAN -- no skip family).
        assert WAVE_CONFIGS[62]["a_seed_base"] == 167_004 == 167_003 + 1, \\
            "W62 A must start at the registered W61 A end + 1 " \\
            "(arithmetic continuation window 167_004..169_003 CLEAN -- " \\
            "no skip family)"
        assert WAVE_CONFIGS[62]["b_exit_seed_base"] == 48_601 == 48_600 + 1, \\
            "W62 B must start at the registered W61 B end + 1 " \\
            "(arithmetic continuation window 48_601..48_800 CLEAN -- " \\
            "no skip family)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W62-SHARD-0",
                                          "n1w62-0of12"), "W62 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W62-SHARD-11",
                                          "n1w62-11of12")
        assert SHARD_DIR.endswith("n1_w62") and OUT.endswith(
            "n1_w62_results.json"), "W62 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W62 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W62_PREREG.md")), \\
            "W62 per-wave prereg missing (materializer requirement)"
        # W62 finalize cumulative deps: W17..W60 outputs ALL PRESENT
        # (static landed seats; chain head 496,548 = W60 bm-c r355
        # K=129,920; W61 bm-b = ONE in-flight upstream seat -- the
        # finalize merge loop derives the wave set from registry keys
        # at run time and stays FAIL-CLOSED on the not-yet-finalized
        # W61 seat, r307 two-state law).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                      43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
                      56, 57, 58, 59, 60):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W62 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 62 (no 15; incl.
        # 48..61 -- all registered, W61 finalize in flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 62) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61], \\
            "W62 prior-wave set must derive from registry keys (no 15, " \\
            "incl. 48..61)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W62 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    A3 = '\n    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG62.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W62 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 5th face) ------
t2c, eol2c = load(FP2)
if '+ W62 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('law sec.4 W61 row, r564 bm-b] "\n'
          '          "+ T-141 s2 ')
    SEG62 = ('law sec.4 W61 row, r564 bm-b] "\n'
             '          "+ W62 materializer face [same guard set, dep=W17..W60 "\n'
             '          "outputs ALL PRESENT (landed chain head 496,548), W61 "\n'
             '          "bm-b = ONE in-flight upstream seat (FAIL-CLOSED "\n'
             '          "r307 at run time), FIFTY-FIRST ENGINE-OWNED WAVE "\n'
             '          "bm-a\'s fourteenth owned claim per machine-derive "\n'
             '          "(engine_owner==bm-a rows 13 + candidate), "\n'
             '          "engine_owner=bm-a per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series (wave 62 = "\n'
             '          "first FREE number after the registered W61 row; seat "\n'
             '          "declared published=reserved MSG-20261002-0818-bma), "\n'
             '          "BOTH SIDES ARITHMETIC CONTINUATION from the W61 tail "\n'
             '          "no skip (A 167_004..169_003 / B 48_601..48_800 both "\n'
             '          "CLEAN machine-derived per the W61 row W62+ WARNING; "\n'
             '          "ADMIT receipt results/_r565bma_w62_band_gate.py; not a "\n'
             '          "free pick -- R250), N3-R1 used-seed leg, probe-seed "\n'
             '          "cluster leg, law sec.4 W62 row, r565 bm-a] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG62, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W62 segment landed (insert after W61 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W62 row -------------------
ROW62 = """
- N1 波62（r565 bm-a 冻·prereg 时展行）：**第五十一枚引擎波·bm-a 第十四枚自有波〔机面 derive：engine_owner==bm-a 行 13+本候选——口径注记：W57 行旧口径「第十四枚」含前引擎时代自有行计数，本行起从 bm-b W61 先例统一为机面 derive 口径如实注记〕**·engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 同 W10-W61 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-a 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启免做（无常驻引擎进程·schtasks 60s tick 新 python 进程天然见新行）·W44/W45/W48/W54/W57 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**零隔接力：本机 r565 W61 同带让路完成**（bm-b r564 冻结 08:11:27 先达 origin→纯让零烧零推·MSG-0640 FIX-A 工具编辑前拦截首例实弹·MSG-20261002-0818-bma 回执）→**波号 62=注册表 W61 行后首个自由号**·席位公示=MSG-20261002-0818-bma（published=reserved r518-① 律·W48/W49/W55 先例）·r511 表尾锁例冻结前 fetch 实核表尾时 W62 号位净空·origin 侧 vacancy 机验】·**双面算术续带零跳位（r535 机闸 derive 律）**：W61 行 W62+ 警示投影 **A 167_004..169_003 CLEAN／B 48_601..48_800 CLEAN**（bm-b r564 冻结窗 gate 投影腿机证+本波 r565 bm-a gate 复核逐字同〔双机互证·r302 陈旧指针证伪律下本波机闸独立 derive 非 prose 转抄〕）→本波 **A-ext seed=167_004..169_003**（**A 面算术续带**==W61 A 尾 167_003+1·步长逐字）·**B-ext exit seed=48_601..48_800**（**B 面算术续带**==W61 B 尾 48_600+1·步长逐字·双侧零跳位=W61 行公示投影逐位）·【机证净空——leg0 六十一键（60 注册行+候选）+leg0b W61 行 W62+ 警示 prose 在场校验+leg1-A/leg1-B 算术位 CLEAN 双机证+leg2 双侧首净窗==候选逐位+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验·**MSG-0640 三修工具**（FIX-A 编辑前 origin-blob 等值断言+FIX-B 锚=最后注册行+行存活核查+FIX-C 推送前纯增量 diff 断言）〕·ADMIT 回执=results/_r565bma_w62_band_gate.py·r565 bm-a 起草窗实跑·非重挑 R250·W62 带从未指派·测量面零结果可钓】·扫描面=pre-W62 六十行 N1 带表【含 W58 行 159_004..161_003/47_601..47_800〔bm-c r354·finalize 已落账 K=125,520〕·W59 行 161_004..163_003/48_001..48_200〔bm-b r562/563·finalize 已落账 K=127,720〕·W60 行 163_004..165_003/48_201..48_400〔bm-c r355·finalize 已落账 K=129,920·净账本链头 496,548〕·**W61 行 165_004..167_003/48_401..48_600〔bm-b r564·注册在飞·烧录 10/12@起草窗·finalize 未落账〕**】·**一在飞上游席披露：本波 finalize 链序前置=W61 落账·FAIL-CLOSED r307 两态律**·带域不相交·W1 ext·v1 在用带·SEED_REGISTRY 全键（int 值全清·LOWAMP-P1/P2/P3 键 20.33M 域零交集）·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·lfc 实际抽带 30_000..30_099·options_wave2 实际抽带 63_000..63_049·leg-3e 实际流避让。**N2/N4 让位注记**：本波 A 带 167_004..169_003——N2/N4 波级 prereg 冻结时按本表防撞律回避该域。**W63+ 警示**：A +2_000 算术位（169_004..171_003）与 B +200 算术位（48_801..49_000）均以本波带闸回执 W63+ 投影腿机证为准（机闸 derive 非 prose 转抄·r535 律）；冻结 hash=本行 commit（r565 bm-a）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 波62（r565 bm-a' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- 每波 finalize 后：`science_gates.append_ledger` 落行'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW62.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W62 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    62: {"a": (167_004') == 1, 'FIX-B FAIL: W62 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W62"') == 1, 'FIX-B FAIL: W62 config not exactly once'
for leg, base in (('W58 materializer face', 'w58leg'),
                  ('W59 materializer face', 'w59leg'),
                  ('W60 materializer face', 'w60leg'),
                  ('W61 materializer face', 'w61leg')):
    assert n11.count(leg) == BASE_SIGS[base], f'FIX-B FAIL: {leg} lost'
assert n11.count('W62 materializer face') == 2, \
    'FIX-B FAIL: W62 leg+summary must be exactly 2'
for w in (48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce262\uff08') == 1, 'FIX-B FAIL: canon W62 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W62 added per face')

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
