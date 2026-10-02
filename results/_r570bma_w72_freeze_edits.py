# -*- coding: utf-8 -*-
"""r570 bm-a W72 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r561/r566/r568 lineage).

FIX-A (origin-blob freshness): every tracked edit target must show zero
  deleted lines vs origin/main BEFORE any edit runs (r559 stale-base cure).
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W71, bm-c's);
  after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W72 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W72 = SIXTY-FIRST engine wave, bm-a's SEVENTEENTH owned per machine-derive
(engine_owner==bm-a rows 16 + candidate). Seat declared published=reserved
MSG-20261002-1032-bma (this window's MSG, r518-1 law). W70 bm-b + W71 bm-c
= TWO in-flight upstream seats at this freeze (finalize chain-pending ->
FAIL-CLOSED r307). BOTH SIDES ARITHMETIC CONTINUATION zero skip:
A 187_004..189_003 (== W71 A tail 187_003 + 1); B 51_401..51_600
(== W71 B tail 51_400 + 1); single reading, no divergence face (zero
refusal points in either arithmetic window). ADMIT receipt
results/_r570bma_w72_band_gate.py.
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
                     f'origin/main -- checkout origin version first (r559 clobber cure)')
print('FIX-A: all 3 tracked edit targets show zero deletions vs origin/main (fresh base)')

# ---------------- survival signature baseline (FIX-B) ------------------------
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20,
             21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
             37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52,
             53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68,
             69, 70, 71]
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in
       (58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in (48, 49, 50, 51, 52, 53, 54, 55, 56,
                                                    57, 58, 59, 60, 61, 62, 63, 64, 65,
                                                    66, 67, 68, 69, 70, 71)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[72] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '72: {"a": (187_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    71: {"a": (185_004, 187_003), "b_exit": (51_201, 51_400),\n'
          '         "engine_owner": "bm-c"},\n'
          '}\n')
    NEW = ('    71: {"a": (185_004, 187_003), "b_exit": (51_201, 51_400),\n'
           '         "engine_owner": "bm-c"},\n'
           '    # SIXTY-FIRST ENGINE-OWNED WAVE (r570 bm-a freeze): bm-a\'s\n'
           '    # seventeenth owned per machine-derive (engine_owner==bm-a\n'
           '    # rows 16 + candidate). Wave 72 = next free number after the\n'
           '    # registered W71 row (seat declared published=reserved\n'
           '    # MSG-20261002-1032-bma, r518-1 law). W1..W69 finalizes ALL\n'
           '    # LANDED (net head 516,348, K=149,720 -- W69 bm-c r361);\n'
           '    # W70 bm-b + W71 bm-c = TWO in-flight upstream seats at this\n'
           '    # freeze (finalize chain-pending FAIL-CLOSED r307).\n'
           '    # BOTH SIDES ARITHMETIC CONTINUATION, zero skip:\n'
           '    # A 187_004..189_003 == W71 A end 187_003 + 1 (CLEAN per the\n'
           '    # W71 row W72+ WARNING projection, machine re-derive r535\n'
           '    # law -- dual-machine cross-check). B 51_401..51_600 ==\n'
           '    # W71 B end 51_400 + 1 (CLEAN, single reading -- zero\n'
           '    # refusal points in either arithmetic window, no divergence\n'
           '    # face). ADMIT receipt results/_r570bma_w72_band_gate.py;\n'
           '    # NOT a re-pick (R250: W72 bands were never assigned).\n'
           '    72: {"a": (187_004, 189_003), "b_exit": (51_401, 51_600),\n'
           '         "engine_owner": "bm-a"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[72] landed (anchor=W71 row, insert)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[72] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '72: {"batch": "PERPETUAL-N1-W72"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w71", "out_name": "n1_w71_results.json",\n'
          '                            "engine_owner": "bm-c"},\n'
          '                       }')
    NEW2 = ('                            "shard_subdir": "n1_w71", "out_name": "n1_w71_results.json",\n'
            '                            "engine_owner": "bm-c"},\n'
            '                       72: {"batch": "PERPETUAL-N1-W72",\n'
            '                            "prereg": ("research/PERPETUAL_N1_W72_PREREG.md (wave-level frozen "\n'
            '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
            '                                       "new seed bands only; SIXTY-FIRST ENGINE-OWNED WAVE, "\n'
            '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
            '                                       "(first-free-number law over the registered W71 row; "\n'
            '                                       "seat published=reserved MSG-20261002-1032-bma), "\n'
            '                                       "engine_owner=bm-a, wave 72 BOTH SIDES ARITHMETIC "\n'
            '                                       "CONTINUATION no skip (A 187_004..189_003 / B 51_401..51_600 "\n'
            '                                       "machine-derived CLEAN == the W71 row W72+ WARNING "\n'
            '                                       "projection verbatim, dual-machine cross-check per "\n'
            '                                       "r302/r535 law; single reading no divergence face); "\n'
            '                                       "W1..W69 finalizes ALL LANDED at this freeze (net "\n'
            '                                       "chain head 516,348, K=149,720, bm-c r361), W70 bm-b "\n'
            '                                       "+ W71 bm-c = TWO in-flight upstream seats "\n'
            '                                       "(finalize chain-pending FAIL-CLOSED r307)"),\n'
            '                            "a_seed_base": 187_004,        # law sec.4 W72 A: 187_004..189_003 (arithmetic continuation)\n'
            '                            "b_exit_seed_base": 51_401,   # law sec.4 W72 B: 51_401..51_600 (arithmetic continuation)\n'
            '                            "shard_subdir": "n1_w72", "out_name": "n1_w72_results.json",\n'
            '                            "engine_owner": "bm-a"},\n'
            '                       }')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[72] landed (anchor=W71 entry tail, insert)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W72 leg --------------
LEG72 = '''
    # --- W72 materializer face (r570 bm-a freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2):
    #     bm-a's seventeenth owned per machine-derive (engine_owner==bm-a
    #     rows 16 + candidate); wave 72 = next free number after the
    #     registered W71 row (seat declared published=reserved
    #     MSG-20261002-1032-bma). W70 bm-b + W71 bm-c = TWO in-flight
    #     upstream seats at this freeze (finalize chain-pending
    #     FAIL-CLOSED r307). BOTH SIDES ARITHMETIC CONTINUATION no
    #     skip (A 187_004..189_003 = W71 A end 187_003 + 1 /
    #     B 51_401..51_600 = W71 B end 51_400 + 1; both CLEAN
    #     machine-derived == the W71 row W72+ WARNING projection
    #     verbatim, dual-machine cross-check; single reading no
    #     divergence face -- zero refusal points in either arithmetic
    #     window; ADMIT receipt results/_r570bma_w72_band_gate.py;
    #     not a re-pick -- R250: W72 bands were never assigned) --
    _set_wave(72)
    try:
        assert WAVE_CONFIGS[72]["a_seed_base"] == pf.N1_BANDS[72]["a"][0], \\
            "W72 A band drift vs law mirror"
        assert WAVE_CONFIGS[72]["b_exit_seed_base"] == \\
            pf.N1_BANDS[72]["b_exit"][0], "W72 B band drift vs law mirror"
        assert WAVE_CONFIGS[72].get("engine_owner") == \\
            pf.N1_BANDS[72].get("engine_owner") == "bm-a", \\
            "W72 engine_owner drift (law mirror parity)"
        w72_a = {A_SEED_BASE + j for j in range(A_N)}
        w72_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w72_a & w72_b), "W72 A/B band overlap"
        assert not (w72_a & reg_ints) and not (w72_b & reg_ints), \\
            "W72 hits SEED_REGISTRY"
        for nm, band in (("A", w72_a), ("B", w72_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W72 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W72 {nm} hits W1"
            assert not (band & probes), f"W72 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W67..W71
        # are REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly.
        assert pf.N1_BANDS[67] == {"a": (177_004, 179_003),
                                   "b_exit": (50_201, 50_400),
                                   "engine_owner": "bm-b"}, \\
            "registered W67 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[68] == {"a": (179_004, 181_003),
                                   "b_exit": (50_501, 50_700),
                                   "engine_owner": "bm-a"}, \\
            "registered W68 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[69] == {"a": (181_004, 183_003),
                                   "b_exit": (50_701, 50_900),
                                   "engine_owner": "bm-c"}, \\
            "registered W69 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[70] == {"a": (183_004, 185_003),
                                   "b_exit": (51_001, 51_200),
                                   "engine_owner": "bm-b"}, \\
            "registered W70 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[71] == {"a": (185_004, 187_003),
                                   "b_exit": (51_201, 51_400),
                                   "engine_owner": "bm-c"}, \\
            "registered W71 row parity drift (r307 two-state)"
        # prior-wave disjointness incl. W48..W71 (all registered; W70
        # + W71 in flight -- coexist by band disjointness per r531).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                      70, 71):
            assert not (w72_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W72 A hits W{wprev}"
            assert not (w72_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W72 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W72 clears it.
        n3r1_used72 = set(range(70_000, 70_006))
        assert not (w72_a & n3r1_used72) and not (w72_b & n3r1_used72), \\
            "W72 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w72_a & lfc_actual12) and not (w72_b & lfc_actual12), \\
            "W72 bands must clear the lfc actual draw range"
        assert not (w72_a & options_actual12) and \\
            not (w72_b & options_actual12), \\
            "W72 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W72 row, r570): BOTH SIDES ARITHMETIC
        # CONTINUATION (zero skip, single reading -- the arithmetic
        # windows are CLEAN, no refusal-facts identity face).
        assert WAVE_CONFIGS[72]["a_seed_base"] == 187_004 == 187_003 + 1, \\
            "W72 A must start at the registered W71 A end + 1 " \\
            "(arithmetic continuation window 187_004..189_003 CLEAN -- " \\
            "no skip family)"
        assert WAVE_CONFIGS[72]["b_exit_seed_base"] == 51_401 == 51_400 + 1, \\
            "W72 B must start at the registered W71 B end + 1 " \\
            "(arithmetic continuation window 51_401..51_600 CLEAN)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W72-SHARD-0",
                                          "n1w72-0of12"), "W72 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W72-SHARD-11",
                                          "n1w72-11of12")
        assert SHARD_DIR.endswith("n1_w72") and OUT.endswith(
            "n1_w72_results.json"), "W72 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                      70, 71):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W72 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W72_PREREG.md")), \\
            "W72 per-wave prereg missing (materializer requirement)"
        # W72 finalize cumulative deps: W17..W69 outputs ALL PRESENT
        # (static landed seats; chain head 516,348 = W69 bm-c r361
        # K=149,720; W70 bm-b + W71 bm-c = TWO in-flight upstream
        # seats -- the finalize merge loop derives the wave set from
        # registry keys at run time and stays FAIL-CLOSED on the
        # not-yet-finalized W70/W71 seats, r307 two-state law).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                      43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
                      56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68,
                      69):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W72 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 72 (no 15; incl.
        # 48..71 -- all registered, W70/W71 finalize in flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 72) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
             65, 66, 67, 68, 69, 70, 71], \\
            "W72 prior-wave set must derive from registry keys (no 15, " \\
            "incl. 48..71)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W72 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG72.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W72 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 5th face) ------
t2c, eol2c = load(FP2)
if '+ W72 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('cluster leg, law sec.4 W71 row, r361 bm-c] "\n'
          '          "+ T-141 s2 ')
    SEG72 = ('cluster leg, law sec.4 W71 row, r361 bm-c] "\n'
             '          "+ W72 materializer face [same guard set, dep=W17..W69 "\n'
             '          "outputs ALL PRESENT (landed chain head 516,348, "\n'
             '          "K=149,720, bm-c r361), W70 bm-b + W71 bm-c = TWO "\n'
             '          "in-flight upstream seats (FAIL-CLOSED r307 at run "\n'
             '          "time), SIXTY-FIRST ENGINE-OWNED WAVE bm-a\'s "\n'
             '          "seventeenth owned claim per machine-derive "\n'
             '          "(engine_owner==bm-a rows 16 + candidate), "\n'
             '          "engine_owner=bm-a per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series "\n'
             '          "(wave 72 = first FREE number after the registered "\n'
             '          "W71 row; seat declared published=reserved "\n'
             '          "MSG-20261002-1032-bma), BOTH SIDES ARITHMETIC "\n'
             '          "CONTINUATION from the W71 tail no skip (A "\n'
             '          "187_004..189_003 / B 51_401..51_600 both CLEAN "\n'
             '          "machine-derived == the W71 row W72+ WARNING "\n'
             '          "projection verbatim, dual-machine cross-check per "\n'
             '          "r302/r535 law; single reading no divergence face; "\n'
             '          "ADMIT receipt results/_r570bma_w72_band_gate.py; "\n'
             '          "not a free pick -- R250), N3-R1 used-seed leg, "\n'
             '          "probe-seed cluster leg, law sec.4 W72 row, "\n'
             '          "r570 bm-a] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG72, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W72 segment landed (insert after W71 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W72 row -------------------
ROW72 = """
- N1 波72（r570 bm-a 冻·prereg 时展行）：**第六十一枚引擎波·bm-a 第十七枚自有波〔机面 derive：engine_owner==bm-a 行 16+本候选〕**·engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 同 W10-W71 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-a 实例=tick 架构 r535 律——冻结编辑落工作树后下一 tick 新进程重读活树自见新行=免杀重启免做·W44/W45/W48/W54/W57/W62/W64/W68 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 72=注册表 W71 行后首个自由号**（W71 席位=MSG-20261002-1017-bmc published=reserved 本机不碰）·席位公示=MSG-20261002-1032-bma（published=reserved r518-① 律·W48/W49/W55/W62/W65/W67/W68/W69/W70/W71 先例）·r511 表尾锁例冻结前 fetch 实核表尾时 W72 号位净空·origin 侧 vacancy 机验】·**带位=双面算术续带零跳位（r535 机闸 derive 律）**：W71 行 W72+ 警示投影 **A 187_004..189_003／B 51_401..51_600 双 CLEAN**（bm-c r361 冻结窗 gate 投影腿机证+本波 r570 bm-a gate 复核逐字同〔双机互证·r302 陈旧指针证伪律下本波机闸独立 derive 非 prose 转抄〕）→本波 **A-ext seed=187_004..189_003**（==W71 A 尾 187_003+1·步长逐字·A 面算术续带零跳位）·**B-ext exit seed=51_401..51_600**（==W71 B 尾 51_400+1·步长逐字·B 面算术续带零跳位·双侧零跳位·单读法零分叉〔双侧算术窗零拒绝点·跳位语义分叉面 F-20261002-03 不触发〕·R250：W72 带从未指派·测量面零结果可钓）·【机证净空——leg0 六十九键（69 注册行+候选）+leg0b W71 行 W72+ 警示 prose 在场校验+leg1-A/leg1-B 算术位 CLEAN 机证+leg2 双侧首净窗==算术==候选+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验·**MSG-0640 三修工具**（FIX-A 编辑前 origin-blob 等值断言+FIX-B 锚=最后注册行+行存活核查+FIX-C 推送前纯增量 diff 断言）〕·ADMIT 回执=results/_r570bma_w72_band_gate.py·r570 bm-a 起草窗实跑】·扫描面=pre-W72 六十九行 N1 带表【含 **W68 行 179_004..181_003/50_501..50_700〔bm-a r568·finalize 已落账 r569·K=147,520〕**·**W69 行 181_004..183_003/50_701..50_900〔bm-c r360·finalize 已落账 r361·K=149,720·净账本链头 516,348〕**·**W70 行 183_004..185_003/51_001..51_200〔bm-b r568·12/12 烧毕·finalize 未落账〕**·**W71 行 185_004..187_003/51_201..51_400〔bm-c r361·12/12 烧毕·finalize 未落账〕**】·**两在飞上游席披露：本波 finalize 链序前置=W70+W71 两落账·FAIL-CLOSED r307 两态律**·带域不相交·W1 ext·v1 在用带·SEED_REGISTRY 全键（160 int 值全清·LOWAMP-P1/P2/P3 键 20.33M 域零交集）·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·lfc 实际流 30_000..30_099·options_wave2 实际流 63_000..63_049（leg-3e 实际流避让腿）·**W73+ 投影（带闸投影腿机证·W73 prereg 照例带闸复核 r335 律）：A 189_004..191_003／B 51_601..51_800 双 CLEAN**（命中面=W73 冻结窗机闸 derive 定谳·本波 gate 投影腿机证零命中）"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce272\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW72.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W72 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    72: {"a": (187_004') == 1, 'FIX-B FAIL: W72 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W72"') == 1, 'FIX-B FAIL: W72 config not exactly once'
for w in (58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W72 materializer face') == 2, \
    'FIX-B FAIL: W72 leg+summary must be exactly 2'
for w in (48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
          64, 65, 66, 67, 68, 69, 70, 71):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce272\uff08') == 1, 'FIX-B FAIL: canon W72 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W72 added per face')

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
