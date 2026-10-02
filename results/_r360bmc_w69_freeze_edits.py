# -*- coding: utf-8 -*-
"""r360 bm-c W69 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r561 lineage).

FIX-A/B/C as per the W66/W67/W68 lineage. W69 = FIFTY-EIGHTH engine wave,
bm-c's TWENTY-SECOND owned (engine_owner==bm-c rows 21 + candidate). Seat =
published=reserved MSG-20261002-1015-bmc (W48/W49/W55/W62/W65/W67/W68
precedents; same-window re-occupation after the W68 yield per r565 law).
BOTH SIDES ARITHMETIC CONTINUATION from the registered W68 tail (bm-a
r568), no skip: A 181_004..183_003 / B 50_701..50_900 (both CLEAN, ==
the W68 row W69+ published projection + this gate's independent derive).
W67 bm-b + W68 bm-a = TWO in-flight upstream seats (finalize FAIL-CLOSED
r307).
"""
import subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NO_WIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)

def git(*a):
    r = subprocess.run(['git', '-C', REPO] + list(a), capture_output=True,
                       creationflags=NO_WIN)
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
                       capture_output=True, creationflags=NO_WIN)
    out = r.stdout.decode('utf-8', 'replace').strip()
    if r.returncode != 0:
        sys.exit(f'FIX-A git fail on {p}')
    for line in out.splitlines():
        add, dele, path = line.split('\t')
        if int(dele) > 0:
            sys.exit(f'STALE BASE (FIX-A abort): {p} shows {dele} deleted lines vs '
                     f'origin/main -- checkout origin version first '
                     f'(r559 clobber cure / same-window seat collision)')
print('FIX-A: all 3 tracked edit targets show zero deletions vs origin/main (fresh base)')

# ---------------- survival signature baseline (FIX-B) ------------------------
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20,
             21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
             37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52,
             53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68]
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {('w%dleg' % w): n1_0.count('W%d materializer face' % w)
       for w in (60, 61, 62, 63, 64, 65, 66, 67, 68)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(49, 69)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[69] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '69: {"a": (181_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    68: {"a": (179_004, 181_003), "b_exit": (50_501, 50_700),\n'
          '         "engine_owner": "bm-a"},\n'
          '}\n')
    NEW = ('    68: {"a": (179_004, 181_003), "b_exit": (50_501, 50_700),\n'
           '         "engine_owner": "bm-a"},\n'
           '    # FIFTY-EIGHTH ENGINE-OWNED WAVE (r360 bm-c freeze): bm-c\'s\n'
           '    # TWENTY-SECOND owned per machine-derive (engine_owner==bm-c\n'
           '    # rows 21 + candidate). Wave 69 = first free number after the\n'
           '    # registered W68 row (seat published=reserved\n'
           '    # MSG-20261002-1015-bmc, r518-1 law; same-window re-occupation\n'
           '    # after the W68 yield to bm-a r568 938d8bb54 first-land per\n'
           '    # r511 commit-order law -- my unpushed freeze 6e8a454b2 fully\n'
           '    # discarded, alien-seed B-band replicas (9 shards,\n'
           '    # audit.machine=bm-c verified) all discarded, finalize never\n'
           '    # ran = zero ledger pollution, r565 re-occupation law).\n'
           '    # W1..W66 finalizes ALL LANDED (net head 509,748, K=143,120,\n'
           '    # bm-c r360 same window); W67 bm-b (burn in flight) + W68 bm-a\n'
           '    # (burn in flight) = TWO in-flight upstream seats at this\n'
           '    # freeze (finalize chain-pending FAIL-CLOSED r307). BOTH\n'
           '    # SIDES ARITHMETIC CONTINUATION from the W68 row tail, no\n'
           '    # skip: A 181_004..183_003 (= W68 A end 181_003 + 1) and B\n'
           '    # 50_701..50_900 (= W68 B end 50_700 + 1) -- both windows\n'
           '    # CLEAN per the W68 row W69+ WARNING projections (bm-a r568\n'
           '    # probe + this freeze\'s machine re-derive, r535 law).\n'
           '    # Machine-verified at prereg time\n'
           '    # (results/_r360bmc_w69_probe.py draft derive +\n'
           '    # results/_r360bmc_w69_band_gate.py ADMIT receipt vs the\n'
           '    # 67-row pre-W69 table + live SEED_REGISTRY values + probe\n'
           '    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin\n'
           '    # slot vacancy machine-checked). NOT a re-pick (R250: W69\n'
           '    # bands were never assigned).\n'
           '    69: {"a": (181_004, 183_003), "b_exit": (50_701, 50_900),\n'
           '         "engine_owner": "bm-c"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[69] landed (anchor=W68 row, insert)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[69] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '69: {"batch": "PERPETUAL-N1-W69"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('"shard_subdir": "n1_w68", "out_name": "n1_w68_results.json",\n'
          '                            "engine_owner": "bm-a"},\n'
          '                       }')
    NEW2 = ('"shard_subdir": "n1_w68", "out_name": "n1_w68_results.json",\n'
            '                            "engine_owner": "bm-a"},\n'
            '                       69: {"batch": "PERPETUAL-N1-W69",\n'
            '                            "prereg": ("research/PERPETUAL_N1_W69_PREREG.md (wave-level frozen "\n'
            '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
            '                                       "new seed bands only; FIFTY-EIGHTH ENGINE-OWNED WAVE, "\n'
            '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
            '                                       "(first-free-number law over the registered W68 row; "\n'
            '                                       "seat published=reserved MSG-20261002-1015-bmc after "\n'
            '                                       "the W68 same-window yield to bm-a r568 first-land "\n'
            '                                       "per r511 commit-order law, same-window re-occupation "\n'
            '                                       "per r565 law), engine_owner=bm-c, wave 69 BOTH SIDES "\n'
            '                                       "ARITHMETIC CONTINUATION no skip (A 181_004..183_003 / "\n'
            '                                       "B 50_701..50_900 machine-derived CLEAN == the W68 row "\n'
            '                                       "W69+ published projection verbatim); W1..W66 finalizes "\n'
            '                                       "ALL LANDED at this freeze (net chain head 509,748, "\n'
            '                                       "K=143,120, bm-c r360 same window), W67 bm-b + W68 bm-a "\n'
            '                                       "= TWO in-flight upstream seats (finalize chain-pending "\n'
            '                                       "FAIL-CLOSED r307)"),\n'
            '                            "a_seed_base": 181_004,        # law sec.4 W69 A: 181_004..183_003 (arithmetic continuation)\n'
            '                            "b_exit_seed_base": 50_701,   # law sec.4 W69 B: 50_701..50_900 (arithmetic continuation)\n'
            '                            "shard_subdir": "n1_w69", "out_name": "n1_w69_results.json",\n'
            '                            "engine_owner": "bm-c"},\n'
            '                       }')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[69] landed (anchor=W68 entry tail, insert)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W69 leg --------------
LEG69 = '''
    # --- W69 materializer face (r360 bm-c freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2):
    #     bm-c's TWENTY-SECOND owned per machine-derive (engine_owner==bm-c
    #     rows 21 + candidate); wave 69 = first free number after the
    #     registered W68 row (seat published=reserved MSG-20261002-1015-bmc;
    #     same-window re-occupation after the W68 yield to bm-a r568 per
    #     r511 commit-order + r565 law). W67 bm-b + W68 bm-a = TWO in-flight
    #     upstream seats at this freeze (registered, finalize chain-pending
    #     FAIL-CLOSED r307). BOTH SIDES ARITHMETIC CONTINUATION from the
    #     W68 tail no skip (A 181_004..183_003 / B 50_701..50_900 both
    #     CLEAN machine-derived per the W68 row W69+ WARNING; ADMIT
    #     receipt results/_r360bmc_w69_band_gate.py; not a re-pick --
    #     R250) --
    _set_wave(69)
    try:
        assert WAVE_CONFIGS[69]["a_seed_base"] == pf.N1_BANDS[69]["a"][0], \\
            "W69 A band drift vs law mirror"
        assert WAVE_CONFIGS[69]["b_exit_seed_base"] == \\
            pf.N1_BANDS[69]["b_exit"][0], "W69 B band drift vs law mirror"
        assert WAVE_CONFIGS[69].get("engine_owner") == \\
            pf.N1_BANDS[69].get("engine_owner") == "bm-c", \\
            "W69 engine_owner drift (law mirror parity)"
        w69_a = {A_SEED_BASE + j for j in range(A_N)}
        w69_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w69_a & w69_b), "W69 A/B band overlap"
        assert not (w69_a & reg_ints) and not (w69_b & reg_ints), \\
            "W69 hits SEED_REGISTRY"
        for nm, band in (("A", w69_a), ("B", w69_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W69 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W69 {nm} hits W1"
            assert not (band & probes), f"W69 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W66/W67/W68
        # are REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly.
        assert pf.N1_BANDS[66] == {"a": (175_004, 177_003),
                                   "b_exit": (50_001, 50_200),
                                   "engine_owner": "bm-c"}, \\
            "registered W66 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[67] == {"a": (177_004, 179_003),
                                   "b_exit": (50_201, 50_400),
                                   "engine_owner": "bm-b"}, \\
            "registered W67 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[68] == {"a": (179_004, 181_003),
                                   "b_exit": (50_501, 50_700),
                                   "engine_owner": "bm-a"}, \\
            "registered W68 row parity drift (r307 two-state)"
        # prior-wave disjointness incl. W48..W68 (all registered; W67/W68
        # in flight -- coexist by band disjointness per r531).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68):
            assert not (w69_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W69 A hits W{wprev}"
            assert not (w69_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W69 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W69 clears it.
        n3r1_used69 = set(range(70_000, 70_006))
        assert not (w69_a & n3r1_used69) and not (w69_b & n3r1_used69), \\
            "W69 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w69_a & lfc_actual12) and not (w69_b & lfc_actual12), \\
            "W69 bands must clear the lfc actual draw range"
        assert not (w69_a & options_actual12) and \\
            not (w69_b & options_actual12), \\
            "W69 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W69 row, r360): BOTH SIDES ARITHMETIC
        # CONTINUATION from the registered W68 tail -- no skip family
        # this wave (both windows CLEAN per the ADMIT receipt).
        assert WAVE_CONFIGS[69]["a_seed_base"] == 181_004 == 181_003 + 1, \\
            "W69 A must start at the registered W68 A end + 1 " \\
            "(arithmetic continuation window 181_004..183_003 CLEAN)"
        assert WAVE_CONFIGS[69]["b_exit_seed_base"] == 50_701 == 50_700 + 1, \\
            "W69 B must start at the registered W68 B end + 1 " \\
            "(arithmetic continuation window 50_701..50_900 CLEAN)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W69-SHARD-0",
                                          "n1w69-0of12"), "W69 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W69-SHARD-11",
                                          "n1w69-11of12")
        assert SHARD_DIR.endswith("n1_w69") and OUT.endswith(
            "n1_w69_results.json"), "W69 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W69 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W69_PREREG.md")), \\
            "W69 per-wave prereg missing (materializer requirement)"
        # W69 finalize cumulative deps: W17..W66 outputs ALL PRESENT
        # (static landed seats; chain head 509,748 = W66 bm-c r360
        # K=143,120; W67 bm-b + W68 bm-a = TWO in-flight upstream
        # seats -- the finalize merge loop derives the wave set from
        # registry keys at run time and stays FAIL-CLOSED on the
        # not-yet-finalized seats, r307 two-state law).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                      43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
                      56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W69 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 69 (no 15; incl.
        # 48..68 -- all registered, W67/W68 finalize in flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 69) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
             65, 66, 67, 68], \\
            "W69 prior-wave set must derive from registry keys (no 15, " \\
            "incl. 48..68)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W69 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG69.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W69 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 6th face) ------
t2c, eol2c = load(FP2)
if '+ W69 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('law sec.4 W68 row, r568 bm-a] "\n'
          '          "+ T-141 s2 ')
    SEG69 = ('law sec.4 W68 row, r568 bm-a] "\n'
             '          "+ W69 materializer face [same guard set, dep=W17..W66 "\n'
             '          "outputs ALL PRESENT (landed chain head 509,748, K=143,120, "\n'
             '          "bm-c r360 same window), W67 bm-b + W68 bm-a = TWO in-flight "\n'
             '          "upstream seats (FAIL-CLOSED r307 at run time), FIFTY-EIGHTH "\n'
             '          "ENGINE-OWNED WAVE bm-c\'s TWENTY-SECOND owned claim per "\n'
             '          "machine-derive (engine_owner==bm-c rows 21 + candidate), "\n'
             '          "engine_owner=bm-c per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series (wave 69 = "\n'
             '          "first FREE number after the registered W68 row; seat "\n'
             '          "published=reserved MSG-20261002-1015-bmc after the W68 "\n'
             '          "same-window yield to bm-a r568 first-land per r511 "\n'
             '          "commit-order law, same-window re-occupation per r565 "\n'
             '          "law), BOTH SIDES ARITHMETIC CONTINUATION from the W68 "\n'
             '          "tail no skip (A 181_004..183_003 / B 50_701..50_900 both "\n'
             '          "CLEAN machine-derived per the W68 row W69+ WARNING; "\n'
             '          "ADMIT receipt results/_r360bmc_w69_band_gate.py; not a "\n'
             '          "free pick -- R250), N3-R1 used-seed leg, probe-seed "\n'
             '          "cluster leg, law sec.4 W69 row, r360 bm-c] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG69, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W69 segment landed (insert after W68 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W69 row -------------------
ROW69 = """
- N1 波69（r360 bm-c 冻·prereg 时展行）：**第五十八枚引擎波·bm-c 第二十二枚自有波〔机面 derive：engine_owner==bm-c 行 21+本候选〕**·engine_owner=bm-c·SATURATION_ENGINE_LAW §1/§2 同 W10-W68 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-c 实例=**常驻架构 v0.4 per-tick 重读**——D-20261002-03 修法同窗实证（W59/W60/W61/W66 四波注册后常驻实例自见自燃=免杀重启）·点火验证唯一证据=产物增长面 r325 律·state queue 面不信】·【never-dry 供给律常设步·**同窗让路后同窗再占位（r565 bm-a 律）：本机 W68 冻结窗与 bm-a r568 撞面（B 侧跳位读法分叉=首个异带面·r530 族第 13 例）→bm-a 938d8bb54 先落 origin=正主→本机全弃（未推 commit 6e8a454b2·异种子复制品 9 片验属全弃·零账本污染·MSG-20261002-1015-bmc 回执）→波号 69=注册表 W68 行后首个自由号·**席位公示=MSG-20261002-1015-bmc（published=reserved r518-① 律）**·r511 表尾锁例冻结前 fetch 实核表尾时 W69 号位净空·origin 侧 vacancy 机验】·**带位=双面算术续带零跳位（r535 机闸 derive 律）**：W68 行 W69+ 警示投影 **A 181_004..183_003 CLEAN／B 50_701..50_900 CLEAN**（bm-a r568 冻结窗投影腿机证+本波 r360 bm-c gate 复核〔双机互证·r302 陈旧指针证伪律下本波机闸独立 derive 非 prose 转抄〕）→本波 **A-ext seed=181_004..183_003**（**A 面算术续带**==W68 A 尾 181_003+1·步长逐字·零跳位）·**B-ext exit seed=50_701..50_900**（**B 面算术续带**==W68 B 尾 50_700+1·步长逐字·零跳位·双侧零跳位=W68 行公示投影逐位·R250：W69 带从未指派·测量面零结果可钓）·【机证净空——leg0 六十八键（67 注册行+候选）+leg0b W68 行 W69+ 警示 prose 在场校验+leg1-A/leg1-B 算术位 CLEAN 双机证+leg2 双侧首净窗==候选逐位+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验·**MSG-0640 三修工具**（FIX-A 编辑前 origin-blob 等值断言+FIX-B 锚=最后注册行+行存活核查+FIX-C 推送前纯增量 diff 断言）〕·ADMIT 回执=results/_r360bmc_w69_band_gate.py·起草窗投影探针=results/_r360bmc_w69_probe.py·r360 bm-c 起草窗实跑】·扫描面=pre-W69 六十七行 N1 带表【含 W64 行 171_004..173_003/49_401..49_600〔bm-a r566·finalize 已落账 K=138,720·链头 505,348〕·W65 行 173_004..175_003/49_601..49_800〔bm-b r566·finalize 已落账 K=140,920·链头 507,548〕·**W66 行 175_004..177_003/50_001..50_200〔bm-c r359·finalize 已落账 K=143,120·净账本链头 509,748·bm-c r360 本窗〕**·W67 行 177_004..179_003/50_201..50_400〔bm-b r567·注册烧录在飞·finalize 未落账〕·W68 行 179_004..181_003/50_501..50_700〔bm-a r568·注册烧录在飞·finalize 未落账〕】·**两在飞上游席披露：本波 finalize 链序前置=W67+W68 双落账·FAIL-CLOSED r307 两态律**·带域不相交·W1 ext·v1 在用带·SEED_REGISTRY 全键（int 值全清·LOWAMP-P1/P2/P3 键 20.33M 域零交集）·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·lfc 实际流 30_000..30_099·options_wave2 实际流 63_000..63_049（leg-3e 实际流避让腿）·**W70+ 投影（带闸投影腿机证=results/_r360bmc_w69_probe.py·W70 prereg 照例带闸复核 r335 律）：A 183_004..185_003 CLEAN／B 50_901..51_100 REFUSED〔SEED_REGISTRY xstock_synth_null_a=51_000·窗口中位命中〕→B 侧跳位族·**分叉面第三例预警**：越 hit 起窗 51_001..51_200 vs 连锁整窗步进 51_101..51_300 两读法分叉——法典现持 W63 连锁〔在册〕+W68 越hit〔在册〕双读法相反·§4 钉死行待 HQ-FEEDBACK F-20261002-03 裁定·W70 冻结方按裁定行执行（裁定前=冻结方机闸 derive+分叉披露强制）**·prereg=PERPETUAL_N1_W69_PREREG.md 冻结〔S5 锚=W66 实测（锚滚动律自 W63 滚至 W66）：merged mu −0.092478/W66-only mu −0.091431/sigma 0.245840/A-p95 0.3235/K-lift +0.0001·累计池投影 149,720（含 W67+W68 在飞 4,400）〕·burn 由本机常驻引擎 v0.4 per-tick 自燃·finalize=活链头 derive one-pass（r538 一过律）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce269\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW69.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W69 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    69: {"a": (181_004') == 1, 'FIX-B FAIL: W69 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W69"') == 1, 'FIX-B FAIL: W69 config not exactly once'
for w in (60, 61, 62, 63, 64, 65, 66, 67, 68):
    leg = 'W%d materializer face' % w
    assert n11.count(leg) == BASE_SIGS['w%dleg' % w], f'FIX-B FAIL: {leg} lost'
assert n11.count('W69 materializer face') == 2, \
    'FIX-B FAIL: W69 leg+summary must be exactly 2'
for w in range(49, 69):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce269\uff08') == 1, 'FIX-B FAIL: canon W69 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W69 added per face')

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
