# -*- coding: utf-8 -*-
"""r364 bm-c W80 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r561/r566/r568/r570/r571 lineage).

FIX-A (origin-blob freshness): every tracked edit target must show zero
  deleted lines vs origin/main BEFORE any edit runs (r559 stale-base cure).
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W79, bm-b's);
  after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W80 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W80 = SIXTY-NINTH engine wave (ordinal per the live comment sequence
W77=66th, W78=67th, W79=68th), bm-c's TWENTY-FIFTH owned per
machine-derive (engine_owner==bm-c rows 24 + candidate). First free
number after the registered W79 row (bm-b r573 freeze, landed origin).
Seat published=reserved MSG-20261002-1204-bmc PUSHED to origin BEFORE
this freeze (r565 early-visibility law; commit 31db49798).

Bands: A 203_004..205_003 (== W79 A end 203_003 + 1, arithmetic
continuation zero skip, CLEAN) / B 53_601..53_800 (== W79 B end 53_600
+ 1, arithmetic continuation zero skip, CLEAN; j13v2_mill pair
53_000/53_100 BELOW the window). ONE in-flight upstream seat at this
freeze: W79 bm-b (burn in flight 9/12 at freeze commit time) -- finalize
chain-pending FAIL-CLOSED r307. W1..W78 finalizes ALL LANDED (net head
536,148, K=169,520 -- W78 bm-c r364 this window).
ADMIT receipt results/_r364bmc_w80_band_gate.py; banned gate ADMIT
0 matched. W81+ projection disclosed by the gate: A 205_004..207_003
CLEAN; B 53_801..54_000 REFUSED at SEED_REGISTRY point 54_000.
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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 80))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in
       range(58, 80)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 80)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[80] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '80: {"a": (203_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    79: {"a": (201_004, 203_003), "b_exit": (53_401, 53_600),\n'
          '         "engine_owner": "bm-b"},\n')
    NEW = ('    79: {"a": (201_004, 203_003), "b_exit": (53_401, 53_600),\n'
           '         "engine_owner": "bm-b"},\n'
           '    # SIXTY-NINTH ENGINE-OWNED WAVE (r364 bm-c freeze): bm-c\'s\n'
           '    # twenty-fifth owned per machine-derive (engine_owner==bm-c\n'
           '    # rows 24 + candidate). Wave 80 = first free number after the\n'
           '    # registered W79 row (r511 tail-lock, fetch-checked vacancy;\n'
           '    # seat published=reserved MSG-20261002-1204-bmc PUSHED to\n'
           '    # origin before this freeze per r565 early-visibility law,\n'
           '    # commit 31db49798).\n'
           '    # W1..W78 finalizes ALL LANDED (net head 536,148, K=169,520,\n'
           '    # W78 bm-c r364 this window -- dead-r363 heritage closed);\n'
           '    # W79 bm-b (burn in flight) = ONE in-flight upstream seat at\n'
           '    # this freeze (finalize chain-pending FAIL-CLOSED r307).\n'
           '    # BOTH SIDES ARITHMETIC CONTINUATION from the W79 row tail,\n'
           '    # zero skip: A 203_004..205_003 (= W79 A end 203_003 + 1)\n'
           '    # CLEAN + B 53_601..53_800 (= W79 B end 53_600 + 1) CLEAN\n'
           '    # (single reading, no fork face, F-20261002-03 not triggered;\n'
           '    # j13v2_mill pair 53_000/53_100 BELOW the B window).\n'
           '    # Machine-verified at prereg time\n'
           '    # (results/_r364bmc_w80_band_gate.py ADMIT receipt vs the\n'
           '    # 77-row pre-W80 table + live SEED_REGISTRY values + probe\n'
           '    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin\n'
           '    # slot vacancy machine-checked). W81+ gate projection: A\n'
           '    # 205_004..207_003 CLEAN; B 53_801..54_000 REFUSED at\n'
           '    # SEED_REGISTRY 54_000. NOT a re-pick (R250: W80 bands\n'
           '    # were never assigned).\n'
           '    80: {"a": (203_004, 205_003), "b_exit": (53_601, 53_800),\n'
           '         "engine_owner": "bm-c"},\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[80] landed (anchor=W79 row, insert after)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[80] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '80: {"batch": "PERPETUAL-N1-W80"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w79", "out_name": "n1_w79_results.json",\n'
          '                            "engine_owner": "bm-b"},\n')
    NEW2 = A2 + (
        '                       80: {"batch": "PERPETUAL-N1-W80",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W80_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; SIXTY-NINTH ENGINE-OWNED WAVE, "\n'
        '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
        '                                       "(first-free-number law over the registered W79 row; "\n'
        '                                       "seat published=reserved MSG-20261002-1204-bmc "\n'
        '                                       "PUSHED to origin BEFORE this freeze per r565 "\n'
        '                                       "early-visibility lesson, commit 31db49798), "\n'
        '                                       "engine_owner=bm-c, wave 80 BOTH SIDES ARITHMETIC "\n'
        '                                       "CONTINUATION zero skip (A 203_004..205_003 CLEAN + "\n'
        '                                       "B 53_601..53_800 CLEAN; single reading, no fork "\n'
        '                                       "face, F-20261002-03 not triggered; j13v2_mill pair "\n'
        '                                       "53_000/53_100 BELOW the B window; W81+ projection: "\n'
        '                                       "A CLEAN / B REFUSED at SEED_REGISTRY 54_000 "\n'
        '                                       "disclosed for the next freezer); "\n'
        '                                       "W1..W78 finalizes ALL LANDED at this freeze (net "\n'
        '                                       "chain head 536,148, K=169,520, W78 bm-c r364 this "\n'
        '                                       "window, dead-r363 heritage closed); W79 bm-b = ONE "\n'
        '                                       "in-flight upstream seat (finalize chain-pending "\n'
        '                                       "FAIL-CLOSED r307)"),\n'
        '                            "a_seed_base": 203_004,        # law sec.4 W80 A: 203_004..205_003 (arithmetic continuation)\n'
        '                            "b_exit_seed_base": 53_601,   # law sec.4 W80 B: 53_601..53_800 (arithmetic continuation)\n'
        '                            "shard_subdir": "n1_w80", "out_name": "n1_w80_results.json",\n'
        '                            "engine_owner": "bm-c"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[80] landed (anchor=W79 entry tail, insert after)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W80 leg --------------
LEG80 = '''
    # --- W80 materializer face (r364 bm-c freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-c's
    #     twenty-fifth owned per machine-derive (engine_owner==bm-c
    #     rows 24 + candidate); wave 80 = first free number after the
    #     registered W79 row (bm-b r573). Seat published=reserved
    #     MSG-20261002-1204-bmc pushed to origin BEFORE this freeze
    #     (commit 31db49798, r565 early-visibility law). ONE in-flight
    #     upstream seat at this freeze: W79 bm-b (burn in flight) --
    #     finalize chain-pending FAIL-CLOSED r307 at run time. W1..W78
    #     finalizes ALL LANDED (net head 536,148, K=169,520, W78 bm-c
    #     r364 this window; dead-r363 heritage closed by r364 per
    #     r529 law). ADMIT receipt
    #     results/_r364bmc_w80_band_gate.py; not a re-pick -- R250:
    #     W80 bands were never assigned --
    _set_wave(80)
    try:
        assert WAVE_CONFIGS[80]["a_seed_base"] == pf.N1_BANDS[80]["a"][0], \\
            "W80 A band drift vs law mirror"
        assert WAVE_CONFIGS[80]["b_exit_seed_base"] == \\
            pf.N1_BANDS[80]["b_exit"][0], "W80 B band drift vs law mirror"
        assert WAVE_CONFIGS[80].get("engine_owner") == \\
            pf.N1_BANDS[80].get("engine_owner") == "bm-c", \\
            "W80 engine_owner drift (law mirror parity)"
        w80_a = {A_SEED_BASE + j for j in range(A_N)}
        w80_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w80_a & w80_b), "W80 A/B band overlap"
        assert not (w80_a & reg_ints) and not (w80_b & reg_ints), \\
            "W80 hits SEED_REGISTRY"
        for nm, band in (("A", w80_a), ("B", w80_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W80 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W80 {nm} hits W1"
            assert not (band & probes), f"W80 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W73..W79 are
        # REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly (W77 bm-a r572; W78 bm-c r363;
        # W79 bm-b r573).
        assert pf.N1_BANDS[73] == {"a": (189_004, 191_003),
                                   "b_exit": (51_601, 51_800),
                                   "engine_owner": "bm-a"}, \\
            "registered W73 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[74] == {"a": (191_004, 193_003),
                                   "b_exit": (52_001, 52_200),
                                   "engine_owner": "bm-b"}, \\
            "registered W74 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[75] == {"a": (193_004, 195_003),
                                   "b_exit": (52_201, 52_400),
                                   "engine_owner": "bm-a"}, \\
            "registered W75 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[76] == {"a": (195_004, 197_003),
                                   "b_exit": (52_401, 52_600),
                                   "engine_owner": "bm-b"}, \\
            "registered W76 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[77] == {"a": (197_004, 199_003),
                                   "b_exit": (52_601, 52_800),
                                   "engine_owner": "bm-a"}, \\
            "registered W77 row parity drift (r307 two-state; bm-a r572)"
        assert pf.N1_BANDS[78] == {"a": (199_004, 201_003),
                                   "b_exit": (53_201, 53_400),
                                   "engine_owner": "bm-c"}, \\
            "registered W78 row parity drift (r307 two-state; bm-c r363)"
        assert pf.N1_BANDS[79] == {"a": (201_004, 203_003),
                                   "b_exit": (53_401, 53_600),
                                   "engine_owner": "bm-b"}, \\
            "registered W79 row parity drift (r307 two-state; bm-b r573)"
        # prior-wave disjointness incl. W48..W79 (all registered; the
        # W79 row is the direct arithmetic upstream of W80's bands).
        for wprev in REG_WAVES_ALL:
            assert not (w80_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W80 A hits W{wprev}"
            assert not (w80_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W80 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W80 clears it.
        n3r1_used80 = set(range(70_000, 70_006))
        assert not (w80_a & n3r1_used80) and not (w80_b & n3r1_used80), \\
            "W80 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w80_a & lfc_actual12) and not (w80_b & lfc_actual12), \\
            "W80 bands must clear the lfc actual draw range"
        assert not (w80_a & options_actual12) and \\
            not (w80_b & options_actual12), \\
            "W80 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W80 row, r364): BOTH SIDES ARITHMETIC
        # CONTINUATION from the registered W79 tail, zero skip -- the
        # arithmetic windows must be CLEAN (no registry points inside;
        # the skip-free face is forced by the ADMIT receipt, refusal
        # facts empty).
        assert WAVE_CONFIGS[80]["a_seed_base"] == 203_004 == \\
            pf.N1_BANDS[79]["a"][1] + 1, \\
            "W80 A must start at the registered W79 A end + 1 " \\
            "(arithmetic continuation window 203_004..205_003 CLEAN)"
        assert WAVE_CONFIGS[80]["b_exit_seed_base"] == 53_601 == \\
            pf.N1_BANDS[79]["b_exit"][1] + 1, \\
            "W80 B must start at the registered W79 B end + 1 " \\
            "(arithmetic continuation window 53_601..53_800 CLEAN)"
        arith_a80 = set(range(203_004, 205_004))
        arith_b80 = set(range(53_601, 53_801))
        assert not (arith_a80 & reg_ints) and not (arith_b80 & reg_ints), \\
            "W80 arithmetic windows must be CLEAN (zero-skip ADMIT face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W80-SHARD-0",
                                          "n1w80-0of12"), "W80 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W80-SHARD-11",
                                          "n1w80-11of12")
        assert SHARD_DIR.endswith("n1_w80") and OUT.endswith(
            "n1_w80_results.json"), "W80 path drift"
        for wprev in REG_WAVES_ALL:
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W80 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W80_PREREG.md")), \\
            "W80 per-wave prereg missing (materializer requirement)"
        # W80 finalize cumulative deps: W17..W78 outputs ALL PRESENT
        # (landed chain head 536,148, K=169,520, W78 bm-c r364 this
        # window; W79 bm-b = ONE in-flight upstream seat -- the
        # finalize merge loop derives the wave set from registry keys
        # at run time and stays FAIL-CLOSED on the not-yet-finalized
        # seat, r307 two-state law).
        for _depw in range(17, 79):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W80 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law):
        # prior-wave set derives from registry keys below 80 (no 15,
        # incl. 48..79 -- all registered, W79 in-flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 80) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 80)], \\
            "W80 prior-wave set must derive from registry keys (no 15; " \\
            "incl. 48..79 -- W79 registered before this freeze landed)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W80 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    REG_WAVES_ALL = '[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 80)]'
    LEG80 = LEG80.replace('REG_WAVES_ALL', REG_WAVES_ALL)
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG80.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W80 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 5th face) ------
t2c, eol2c = load(FP2)
if '+ W80 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('          "cluster leg, law sec.4 W79 row, r573 bm-b] "\n'
          '          "+ T-141 s2 ')
    SEG80 = ('          "cluster leg, law sec.4 W79 row, r573 bm-b] "\n'
             '          "+ W80 materializer face [same guard set, dep=W17..W78 "\n'
             '          "outputs ALL PRESENT (landed chain head 536,148, "\n'
             '          "K=169,520, W78 bm-c r364 this window, dead-r363 "\n'
             '          "heritage closed per r529 law), W79 bm-b = ONE "\n'
             '          "in-flight upstream seat (FAIL-CLOSED r307 at run "\n'
             '          "time), SIXTY-NINTH ENGINE-OWNED WAVE bm-c\'s "\n'
             '          "twenty-fifth owned claim per machine-derive "\n'
             '          "(engine_owner==bm-c rows 24 + candidate), "\n'
             '          "engine_owner=bm-c per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series "\n'
             '          "(wave 80 = first FREE number after the registered "\n'
             '          "W79 row; seat published=reserved "\n'
             '          "MSG-20261002-1204-bmc pushed to origin BEFORE "\n'
             '          "this freeze, commit 31db49798, r565 law), BOTH "\n'
             '          "SIDES ARITHMETIC CONTINUATION zero skip (A "\n'
             '          "203_004..205_003 CLEAN + B 53_601..53_800 CLEAN, "\n'
             '          "single reading, no fork face; W81+ projection B "\n'
             '          "REFUSED at SEED_REGISTRY 54_000 disclosed for the "\n'
             '          "next freezer; ADMIT receipt "\n'
             '          "results/_r364bmc_w80_band_gate.py; not a "\n'
             '          "free pick -- R250), N3-R1 used-seed leg, "\n'
             '          "probe-seed cluster leg, law sec.4 W80 row, "\n'
             '          "r364 bm-c] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG80, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W80 segment landed (insert after W79 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W80 row -------------------
ROW80 = """
- N1 波80（r364 bm-c 冻·prereg 时展行）：**第六十九枚引擎波·bm-c 第二十五枚自有波〔机面 derive：engine_owner==bm-c 行 24+本候选〕**·engine_owner=bm-c·SATURATION_ENGINE_LAW §1/§2 同 W10-W79 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-c 实例=常驻架构 v0.4 per-tick 重读（D-20261002-03 修法·W59/W60/W61/W66/W69/W71/W78 同窗实证——冻结编辑落工作树后下一 tick 重读活树自见新行自燃=免杀重启免做·点火验证唯一证据=2 tick 内产物增长面 r325 律·state queue 面不信）】·【never-dry 供给律常设步·**波号 80=注册表 W79 行后首个自由号**（r511 表尾锁例冻结前 fetch 实核表尾时 W80 号位净空·origin 侧 vacancy 机验）·**席位公示=MSG-20261002-1204-bmc（published=reserved r518-① 律·先于冻结 commit 推 origin=r565 早可见性律·commit 31db49798）**·本窗实况=W78 finalize one-pass 已落账（bm-c r364·**536,148 净链头**·K=169,520·r363 猝死会话遗产跨轮收口·号位 363 烧毁 r529 律）→bm-b W79 finalize 链序解锁〕·**带位（r535 机闸 derive 律·活注册表机证·ADMIT 回执=results/_r364bmc_w80_band_gate.py）**：**A-ext seed=203_004..205_003**（**A 面算术续带零跳位**==W79 A 尾 203_003+1·步长逐字·CLEAN）；**B-ext exit seed=53_601..53_800**（**B 面算术续带零跳位**==W79 B 尾 53_600+1·步长逐字·CLEAN·双侧算术窗零拒绝点=单读法零分叉〔F-20261002-03 跳位语义分叉面不触发〕·SEED_REGISTRY j13v2_mill_ic1=53_000/j13v2_mill_ic2=53_100 均在窗下方净空）·【机证净空——leg0 七十七键（77 注册行·表尾=W79 bm-b r573）+leg1-A/B 双侧算术位 CLEAN 零拒绝点+leg2 A/B 首净窗==算术位恒等+leg3 origin 号位净空机验+SEED_REGISTRY 全键 160 值+N3-R1 已用种子带腿（70_000..70_005·MSG-183x r529 强制）+探针种子簇腿（95_000..95_003·r335 强制）+N2/N4+N2-W15 探针点+lfc/options 实际流腿】·**W81+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 205_004..207_003 **CLEAN**；B 53_801..54_000 **REFUSED**〔SEED_REGISTRY 点 54_000 带上边缘端点→首净窗预期 54_001..54_200·W5 边缘端点先例族〕·R250：W80 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W80 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W80_PREREG.md（冻结件）·本波 §5 锚=W78 finalize 实测值（锚滚动律）·finalize 链序前置=W79 bm-b 唯一在飞上游席（FAIL-CLOSED r307 两态律）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce280\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW80.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W80 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    80: {"a": (203_004') == 1, 'FIX-B FAIL: W80 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W80"') == 1, 'FIX-B FAIL: W80 config not exactly once'
for w in range(58, 80):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W80 materializer face') == 2, \
    'FIX-B FAIL: W80 leg+summary must be exactly 2'
for w in range(48, 80):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce280\uff08') == 1, 'FIX-B FAIL: canon W80 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W80 added per face')

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
print('FREEZE_EDITS_OK 80')
