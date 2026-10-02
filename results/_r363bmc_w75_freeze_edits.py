# -*- coding: utf-8 -*-
"""r363 bm-c W75 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r561/r566/r568/r570 lineage).

FIX-A (origin-blob freshness): every tracked edit target must show zero
  deleted lines vs origin/main BEFORE any edit runs (r559 stale-base cure).
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W74, bm-b's);
  after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W75 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W75 = SIXTY-FOURTH engine wave, bm-c's TWENTY-FOURTH owned per
machine-derive (engine_owner==bm-c rows 23 + candidate). Seat declared
published=reserved MSG-20261002-1105-bmc. W74 = REGISTERED by bm-b (r571,
burning) with bands A 191_004..193_003 / B 52_001..52_200 == this
machine's gate-derived projection BITWISE (dual-machine cross-validation,
r530 family; B side = forced skip past SEED_REGISTRY
xstock_synth_null_b=52_000, single reading). Bands = ARITHMETIC
CONTINUATION from the registered W74 tail, zero skip (r535 law):
A 193_004..195_003 (== W74 A end 193_003 + 1) / B 52_201..52_400
(== W74 B end 52_200 + 1); single reading, no divergence face.
ONE in-flight upstream seat at this freeze: W74 bm-b (registered +
burning, finalize FAIL-CLOSED r307). W1..W73 finalizes ALL LANDED
(net head 525,148, K=158,520 -- bm-a r571). ADMIT receipt
results/_r363bmc_w75_band_gate.py.
"""
import subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREAT = 0x08000000  # CREATE_NO_WINDOW (session-host flash guard)

def git(*a):
    r = subprocess.run(['git', '-C', REPO] + list(a), capture_output=True,
                       creationflags=CREAT)
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
                       capture_output=True, creationflags=CREAT)
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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 75))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in
       range(58, 75)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 75)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[75] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '75: {"a": (193_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    74: {"a": (191_004, 193_003), "b_exit": (52_001, 52_200),\n'
          '         "engine_owner": "bm-b"},\n')
    NEW = ('    74: {"a": (191_004, 193_003), "b_exit": (52_001, 52_200),\n'
           '         "engine_owner": "bm-b"},\n'
           '    # SIXTY-FOURTH ENGINE-OWNED WAVE (r363 bm-c freeze): bm-c\'s\n'
           '    # twenty-fourth owned per machine-derive (engine_owner==bm-c\n'
           '    # rows 23 + candidate). Wave 75 = first free number after the\n'
           '    # registered W74 row (seat published=reserved\n'
           '    # MSG-20261002-1105-bmc; r511 tail-lock vacancy machine-\n'
           '    # checked). Bands = ARITHMETIC CONTINUATION from the\n'
           '    # registered W74 tail, zero skip (r535 law): W74 (bm-b r571)\n'
           '    # landed exactly at this machine\'s gate-derived projection\n'
           '    # (A 191_004..193_003 clean / B forced skip past\n'
           '    # SEED_REGISTRY xstock_synth_null_b=52_000 -> 52_001..52_200,\n'
           '    # single reading) -- dual-machine cross-validation, r530\n'
           '    # family; so A 193_004..195_003 == W74 A end 193_003 + 1 and\n'
           '    # B 52_201..52_400 == W74 B end 52_200 + 1, single reading,\n'
           '    # no divergence face. W1..W73 finalizes ALL LANDED (net\n'
           '    # head 525,148, K=158,520 -- W73 bm-a r571); W74 bm-b =\n'
           '    # ONE in-flight upstream seat at this freeze (registered +\n'
           '    # burning, finalize chain-pending FAIL-CLOSED r307).\n'
           '    # ADMIT receipt results/_r363bmc_w75_band_gate.py;\n'
           '    # NOT a re-pick (R250: W75 bands were never assigned).\n'
           '    75: {"a": (193_004, 195_003), "b_exit": (52_201, 52_400),\n'
           '         "engine_owner": "bm-c"},\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[75] landed (anchor=W74 row, insert after)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[75] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '75: {"batch": "PERPETUAL-N1-W75"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w74", "out_name": "n1_w74_results.json",\n'
          '                            "engine_owner": "bm-b"},\n')
    NEW2 = ('                            "shard_subdir": "n1_w74", "out_name": "n1_w74_results.json",\n'
            '                            "engine_owner": "bm-b"},\n'
            '                       75: {"batch": "PERPETUAL-N1-W75",\n'
            '                            "prereg": ("research/PERPETUAL_N1_W75_PREREG.md (wave-level frozen "\n'
            '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
            '                                       "new seed bands only; SIXTY-FOURTH ENGINE-OWNED WAVE, "\n'
            '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
            '                                       "(first-free-number law over the registered W74 row; "\n'
            '                                       "seat published=reserved MSG-20261002-1105-bmc; bands = "\n'
            '                                       "ARITHMETIC CONTINUATION from the registered W74 tail "\n'
            '                                       "zero skip per r535 law -- W74 bm-b r571 landed exactly "\n'
            '                                       "at this machine\'s gate-derived projection incl. the "\n'
            '                                       "xstock_synth_null_b=52_000 forced skip on the B side, "\n'
            '                                       "dual-machine cross-validation r530 family, single "\n'
            '                                       "reading; ONE in-flight upstream seat W74 bm-b "\n'
            '                                       "registered-burning -- FAIL-CLOSED r307), "\n'
            '                                       "engine_owner=bm-c; W1..W73 finalizes ALL LANDED at this "\n'
            '                                       "freeze (net chain head 525,148, K=158,520, bm-a r571)"),\n'
            '                            "a_seed_base": 193_004,        # law sec.4 W75 A: 193_004..195_003 (arithmetic continuation from registered W74 tail, r535)\n'
            '                            "b_exit_seed_base": 52_201,   # law sec.4 W75 B: 52_201..52_400 (arithmetic continuation from registered W74 tail, r535)\n'
            '                            "shard_subdir": "n1_w75", "out_name": "n1_w75_results.json",\n'
            '                            "engine_owner": "bm-c"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[75] landed (anchor=W74 entry tail, insert after)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W75 leg --------------
LEG75 = '''
    # --- W75 materializer face (r363 bm-c freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-c's
    #     twenty-fourth owned per machine-derive (engine_owner==bm-c
    #     rows 23 + candidate); wave 75 = first free number after the
    #     registered W74 row (seat MSG-20261002-1105-bmc). Bands =
    #     ARITHMETIC CONTINUATION from the registered W74 tail, zero
    #     skip (r535 law): W74 (bm-b r571) landed exactly at this
    #     machine's gate-derived projection (B side forced skip past
    #     xstock_synth_null_b=52_000, single reading) -- dual-machine
    #     cross-validation r530 family. ONE in-flight upstream seat
    #     at this freeze: W74 bm-b registered-burning (finalize
    #     chain-pending FAIL-CLOSED r307 at run time). ADMIT receipt
    #     results/_r363bmc_w75_band_gate.py; not a re-pick -- R250:
    #     W75 bands were never assigned --
    _set_wave(75)
    try:
        assert WAVE_CONFIGS[75]["a_seed_base"] == pf.N1_BANDS[75]["a"][0], \\
            "W75 A band drift vs law mirror"
        assert WAVE_CONFIGS[75]["b_exit_seed_base"] == \\
            pf.N1_BANDS[75]["b_exit"][0], "W75 B band drift vs law mirror"
        assert WAVE_CONFIGS[75].get("engine_owner") == \\
            pf.N1_BANDS[75].get("engine_owner") == "bm-c", \\
            "W75 engine_owner drift (law mirror parity)"
        w75_a = {A_SEED_BASE + j for j in range(A_N)}
        w75_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w75_a & w75_b), "W75 A/B band overlap"
        assert not (w75_a & reg_ints) and not (w75_b & reg_ints), \\
            "W75 hits SEED_REGISTRY"
        for nm, band in (("A", w75_a), ("B", w75_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W75 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W75 {nm} hits W1"
            assert not (band & probes), f"W75 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W69..W74
        # are REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly.
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
        assert pf.N1_BANDS[72] == {"a": (187_004, 189_003),
                                   "b_exit": (51_401, 51_600),
                                   "engine_owner": "bm-b"}, \\
            "registered W72 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[73] == {"a": (189_004, 191_003),
                                   "b_exit": (51_601, 51_800),
                                   "engine_owner": "bm-a"}, \\
            "registered W73 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[74] == {"a": (191_004, 193_003),
                                   "b_exit": (52_001, 52_200),
                                   "engine_owner": "bm-b"}, \\
            "registered W74 row parity drift (r307 two-state; bm-b r571 "\\
            "landed exactly at this machine's gate-derived projection)"
        # prior-wave disjointness incl. W48..W74 (all registered; the
        # W74 row is the direct arithmetic upstream of W75).
        for wprev in REG_WAVES_ALL:
            assert not (w75_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W75 A hits W{wprev}"
            assert not (w75_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W75 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W75 clears it.
        n3r1_used75 = set(range(70_000, 70_006))
        assert not (w75_a & n3r1_used75) and not (w75_b & n3r1_used75), \\
            "W75 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w75_a & lfc_actual12) and not (w75_b & lfc_actual12), \\
            "W75 bands must clear the lfc actual draw range"
        assert not (w75_a & options_actual12) and \\
            not (w75_b & options_actual12), \\
            "W75 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W75 row, r363): ARITHMETIC CONTINUATION
        # from the registered W74 tail (zero skip, single reading);
        # W74 landed == the gate-derived projection (cross-validated).
        if 74 in pf.N1_BANDS:
            assert pf.N1_BANDS[74]["a"] == (191_004, 193_003) and \\
                pf.N1_BANDS[74]["b_exit"] == (52_001, 52_200), \\
                "registered W74 divergent from the gate-derived projection " \\
                "(W75 static bands invalid -- re-derive, r566-3 law)"
            assert WAVE_CONFIGS[75]["a_seed_base"] == \\
                pf.N1_BANDS[74]["a"][1] + 1, \\
                "W75 A must start at the registered W74 A end + 1"
            assert WAVE_CONFIGS[75]["b_exit_seed_base"] == \\
                pf.N1_BANDS[74]["b_exit"][1] + 1, \\
                "W75 B must start at the registered W74 B end + 1"
        else:
            assert WAVE_CONFIGS[75]["a_seed_base"] == 193_004 == \\
                191_003 + 1 + 2_000, \\
                "W75 A = W74 published-projection tail + 1 " \\
                "(seat-reservation skip, r518-1 law; W73 A end 191_003 + 1 " \\
                "skips exactly the 2,000-wide reserved window)"
            assert WAVE_CONFIGS[75]["b_exit_seed_base"] == 52_201 == \\
                51_800 + 1 + 400, \\
                "W75 B = W74 DERIVED window tail + 1 (seat-reservation " \\
                "skip, r518-1 law; W73 B end 51_800 + 1 skips the REFUSED " \\
                "arithmetic window AND the 52_001..52_200 derived window)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W75-SHARD-0",
                                          "n1w75-0of12"), "W75 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W75-SHARD-11",
                                          "n1w75-11of12")
        assert SHARD_DIR.endswith("n1_w75") and OUT.endswith(
            "n1_w75_results.json"), "W75 path drift"
        for wprev in REG_WAVES_ALL:
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W75 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W75_PREREG.md")), \\
            "W75 per-wave prereg missing (materializer requirement)"
        # W75 finalize cumulative deps: W17..W73 outputs ALL PRESENT
        # (static landed seats; chain head 525,148 = W73 bm-a r571
        # K=158,520; W74 bm-b = ONE in-flight upstream seat -- the
        # finalize merge loop derives the wave set from registry keys
        # at run time and stays FAIL-CLOSED on the not-yet-finalized
        # seat, r307 two-state law).
        for _depw in range(17, 74):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W75 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law):
        # prior-wave set derives from registry keys below 75 (no 15,
        # incl. 48..74 -- all registered, W74 in-flight,
        # FAIL-CLOSED at run time).
        expect_below = sorted(w for w in WAVE_CONFIGS if w < 75)
        base_keys = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 74)] + [74]
        assert expect_below == base_keys, \\
            "W75 prior-wave set must derive from registry keys (no 15; " \\
            "incl. 48..74 -- W74 registered by bm-b r571 before this " \\
            "freeze landed)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W75 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    REG_WAVES_ALL = '[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 75)]'
    LEG75 = LEG75.replace('REG_WAVES_ALL', REG_WAVES_ALL)
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG75.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W75 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 5th face) ------
t2c, eol2c = load(FP2)
if '+ W75 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('cluster leg, law sec.4 W74 row, "\n'
          '          "r571 bm-b] "\n'
          '          "+ T-141 s2 ')
    SEG75 = ('cluster leg, law sec.4 W74 row, "\n'
             '          "r571 bm-b] "\n'
             '          "+ W75 materializer face [same guard set, dep=W17..W73 "\n'
             '          "outputs ALL PRESENT (landed chain head 525,148, "\n'
             '          "K=158,520, bm-a r571), W74 bm-b = registered-burning "\n'
             '          "upstream seat (FAIL-CLOSED r307 at run time), "\n'
             '          "SIXTY-FOURTH ENGINE-OWNED WAVE bm-c\'s twenty-"\n'
             '          "fourth owned claim per machine-derive "\n'
             '          "(engine_owner==bm-c rows 23 + candidate), "\n'
             '          "engine_owner=bm-c per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series "\n'
             '          "(wave 75 = first FREE number after the registered "\n'
             '          "W74 row; seat published=reserved MSG-20261002-1105-bmc; "\n'
             '          "bands = ARITHMETIC CONTINUATION from the registered "\n'
             '          "W74 tail zero skip per r535 law -- W74 bm-b r571 landed "\n'
             '          "exactly at this machine\'s gate-derived projection incl. "\n'
             '          "the xstock_synth_null_b=52_000 forced skip on the B side, "\n'
             '          "dual-machine cross-validation r530 family, single "\n'
             '          "reading), N3-R1 used-seed leg, probe-seed cluster leg, "\n'
             '          "law sec.4 W75 row, r363 bm-c] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG75, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W75 segment landed (insert after W74 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W75 row -------------------
ROW75 = """
- N1 波75（r363 bm-c 冻·prereg 时展行）：**第六十四枚引擎波·bm-c 第二十四枚自有波〔机面 derive：engine_owner==bm-c 行 23+本候选〕**·engine_owner=bm-c·SATURATION_ENGINE_LAW §1/§2 同 W10-W74 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-c 实例=常驻架构 v0.4 per-tick 重读（D-20261002-03 修法·mtime-watch+importlib.reload）——冻结 commit 后常驻实例下一 tick 重读活树自见新行自燃=免杀重启免做·W59/W60/W61/W66/W69/W71 同窗实证·点火验证唯一证据=2 tick 内产物增长面 r325 律】·【never-dry 供给律常设步·**波号 75=注册表 W74 行后首个自由号**（**W74=bm-b r571 已注册·引擎烧录在飞·带位 A 191_004..193_003／B 52_001..52_200==本机 gate 派生投影逐位同（双机互证·r530 族第 10 例）**·席位公示=MSG-20261002-1105-bmc published=reserved r518-① 律·W48/W49/W55/W62/W65/W67/W68/W69/W70/W71/W73/W74 先例）·r511 表尾锁例冻结前 fetch 实核表尾时 W75 号位净空·origin 侧 vacancy 机验】·**带位=注册 W74 尾双面算术续带零跳位（r535 机闸 derive 律）**：W74 行〔bm-b r571·B 面=越 SEED_REGISTRY **xstock_synth_null_b=52_000** 端点强制跳位·两读法同解无分叉（r566 面）〕==本波 r363 bm-c gate 派生投影复核**逐位同**（双机互证·r302 陈旧指针证伪律下机闸独立 derive 非 prose 转抄·r530 族第 10 例确定性交叉验证）→本波 **A-ext seed=193_004..195_003**（==W74 A 尾 193_003+1·步长逐字·A 面算术续带零跳位）；**B-ext exit seed=52_201..52_400**（==W74 B 尾 52_200+1·步长逐字·B 面算术续带零跳位·双侧零跳位·单读法零分叉·R250：W75 带从未指派·测量面零结果可钓）·【机证净空——leg0 七十二键（72 注册行·W74 两态 r307 已收敛为在册态）+leg0b W73 行 W74+ 警示投影 prose 在场校验（含 REFUSED+派生窗+refusal 身份三锚）+leg1 A 算术位 CLEAN+B 算术窗 REFUSED〔xstock_synth_null_b=52_000 端点恒等〕→W74 派生窗=52_001..52_200 单读法+leg2 双侧首净窗==注册 W74 尾续带候选+leg3 双带 ADMIT（W74 在册带全清）+N3-R1 腿+探针簇腿+origin 号位净空机验·**MSG-0640 三修工具**（FIX-A 编辑前 origin-blob 等值断言+FIX-B 锚=最后注册行 W74+行存活核查+FIX-C 推送前纯增量 diff 断言）〕·ADMIT 回执=results/_r363bmc_w75_band_gate.py·r363 bm-c 起草窗实跑】·扫描面=pre-W75 七十二行 N1 带表【含 **W70 行 183_004..185_003/51_001..51_200〔bm-b r568·finalize 已落账 r570·K=151,720〕**·**W71 行 185_004..187_003/51_201..51_400〔bm-c r361·finalize 已落账 r362·K=154,120〕**·**W72 行 187_004..189_003/51_401..51_600〔bm-b r570·finalize 已落账 r571·K=156,320〕**·**W73 行 189_004..191_003/51_601..51_800〔bm-a r570·finalize 已落账 r571·K=158,520·净链头 525,148〕**·**W74 行 191_004..193_003/52_001..52_200〔bm-b r571 注册·烧录在飞·finalize 未落账〕**】·**一在飞上游席披露：W74 bm-b（注册+烧录在飞）→本波 finalize 链序前置=W74 落账·FAIL-CLOSED r307 两态律**·带域不相交·W1 ext·v1 在用带·SEED_REGISTRY 全键（160 int 值全清·LOWAMP-P1/P2/P3 键 20.33M 域零交集机证）·N3-R1 已用带 70_000..70_005（MSG-183x r529 裁定行②）·探针簇 95_000..95_003（r335 发现腿·W26 起强制）·N2/N4 探针点 40_000/40_001·N2-W15 31_000/31_500/32_000·lfc 30_000..30_099·options 63_000..63_049·prereg=research/PERPETUAL_N1_W75_PREREG.md（r363 冻结 commit 入库·§7/§8 占位纪律）
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce275\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW75.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W75 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    75: {"a": (193_004') == 1, 'FIX-B FAIL: W75 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W75"') == 1, 'FIX-B FAIL: W75 config not exactly once'
for w in range(58, 75):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W75 materializer face') == 2, \
    'FIX-B FAIL: W75 leg+summary must be exactly 2'
for w in range(48, 75):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce275\uff08') == 1, 'FIX-B FAIL: canon W75 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W75 added per face')

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
