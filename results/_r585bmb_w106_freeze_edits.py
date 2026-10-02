# -*- coding: utf-8 -*-
"""r585 bm-b W106 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening.

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED rows (W104 bm-a union
  r586 + W105 bm-c r376); every registered row signature survives exactly;
  exactly one new W106 signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.
AST gate (r580/r581 lesson): post-edit ast.parse on both py faces.

W106 = NINETY-SIXTH engine wave by MACHINE-DERIVE (engine_owner rows 95 +
candidate; gate leg0 machine output governs per r359 law), bm-b's
THIRTY-SIXTH owned (engine_owner==bm-b rows 35 + candidate).
First free number after the REGISTERED W105 row (bm-c r376 freeze f2db133c5
+ bm-a r586 W104-union 48f6f2ff1) -- SINGLE STATE zero seat gap.
Seat published=reserved MSG-20261002-1733-bmb pushed to origin fe191d370
BEFORE this freeze (r565 early-visibility law); seat prose ordinal drift
(written pre-W104/W105-registration) disclosed per r359 law; seat-time
skip-past-published framing hops 2/2 vs freeze-time single-state arithmetic
hops 0/0 converge on identical bands (no fork face).
Bands (both sides arithmetic continuation from the registered W105 tails):
  A 255_004..257_003 (W105 A tail 255_003 + 1, stride 2_000) hops=0.
  B 60_201..60_400   (W105 B tail 60_200 + 1, stride 200) hops=0.
  ADMIT receipt results/_r585bmb_w106_band_gate.py rc0; banned gate ADMIT 0.
W100 finalize LANDED at this freeze (chain head 584,548, K=217,920 = W100
bm-b r585 one-pass this window). FIVE in-flight upstream seats (W101 bm-a +
W102 bm-c + W103 bm-b + W104 bm-a + W105 bm-c burned-unfinalized) --
finalize merge loop stays FAIL-CLOSED r307 at run time.
W107+ projection: A 257_004..259_003 CLEAN / B 60_401..60_600 CLEAN
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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 106))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 106)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 106)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[106] ---------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '106: {"a": (255_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    105: {"a": (253_004, 255_003), "b_exit": (60_001, 60_200),\n'
          '         "engine_owner": "bm-c"},\n'
          '}\n')
    NEW = ('    105: {"a": (253_004, 255_003), "b_exit": (60_001, 60_200),\n'
           '         "engine_owner": "bm-c"},\n'
           '    # NINETY-SIXTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r585 bm-b\n'
           '    # freeze): engine_owner rows 95 + candidate; bm-b\'s thirty-\n'
           '    # sixth owned per machine-derive (engine_owner==bm-b rows 35 +\n'
           '    # candidate). Wave 106 = first free number after the REGISTERED\n'
           '    # W105 row (bm-c r376 freeze f2db133c5 + bm-a r586 W104-union\n'
           '    # 48f6f2ff1) -- SINGLE STATE zero seat gap. Seat\n'
           '    # published=reserved MSG-20261002-1733-bmb pushed to origin\n'
           '    # fe191d370 BEFORE this freeze per r565 early-visibility law;\n'
           '    # seat prose ordinal drift (pre-registration framing) disclosed\n'
           '    # per r359 law; seat-time skip-past-published hops 2/2 vs\n'
           '    # freeze-time single-state arithmetic hops 0/0 converge on\n'
           '    # identical bands (no fork face).\n'
           '    # W100 finalize LANDED at this freeze (landed chain head\n'
           '    # 584,148->584,548 = W100 bm-b r585 one-pass this window;\n'
           '    # K=217,920). FIVE in-flight upstream seats (W101 bm-a + W102\n'
           '    # bm-c + W103 bm-b + W104 bm-a + W105 bm-c burned-unfinalized)\n'
           '    # -- finalize merge loop stays FAIL-CLOSED r307 at run time.\n'
           '    # A = arithmetic continuation from the registered W105 A tail:\n'
           '    # 255_004..257_003 CLEAN hops=0. B = arithmetic continuation\n'
           '    # from the registered W105 B tail: 60_201..60_400 CLEAN hops=0\n'
           '    # (both sides arithmetic continuation, W92 r370 / W100 r583 /\n'
           '    # W103 r584 precedent family). ADMIT receipt\n'
           '    # results/_r585bmb_w106_band_gate.py rc0; live SEED_REGISTRY\n'
           '    # + probe cluster 95_000..95_003 r335 leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 leg.\n'
           '    # W107+ projection: A 257_004..259_003 CLEAN; B 60_401..60_600\n'
           '    # CLEAN (next freezer must re-derive, never transcribe).\n'
           '    # NOT a re-pick (R250: W106 bands were never assigned).\n'
           '    106: {"a": (255_004, 257_003), "b_exit": (60_201, 60_400),\n'
           '         "engine_owner": "bm-b"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[106] landed (anchor=W105 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[106] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '106: {"batch": "PERPETUAL-N1-W106"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w105", "out_name": "n1_w105_results.json",\n'
          '                            "engine_owner": "bm-c"},\n')
    NEW2 = A2 + (
        '                       106: {"batch": "PERPETUAL-N1-W106",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W106_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; NINETY-SIXTH ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 95 + candidate), own-series "\n'
        '                                       "continuation per O-20261001-2355 sec.2 (first-free-number "\n'
        '                                       "law after the REGISTERED W105 row, SINGLE STATE zero seat "\n'
        '                                       "gap; seat published=reserved MSG-20261002-1733-bmb PUSHED "\n'
        '                                       "to origin fe191d370 BEFORE this freeze per r565 "\n'
        '                                       "early-visibility law; seat prose ordinal drift disclosed "\n'
        '                                       "per r359 law; seat-time skip-past-published hops 2/2 vs "\n'
        '                                       "freeze-time single-state arithmetic hops 0/0 converge "\n'
        '                                       "identical bands), engine_owner=bm-b, wave 106: A = "\n'
        '                                       "arithmetic continuation from the registered W105 A tail "\n'
        '                                       "(255_004..257_003 CLEAN hops=0) + B = arithmetic "\n'
        '                                       "continuation from the registered W105 B tail "\n'
        '                                       "(60_201..60_400 CLEAN hops=0; ADMIT receipt "\n'
        '                                       "results/_r585bmb_w106_band_gate.py; W107+ projection: "\n'
        '                                       "A 257_004..259_003 CLEAN / B 60_401..60_600 CLEAN for "\n'
        '                                       "the next freezer); W100 finalize LANDED at this freeze "\n'
        '                                       "(chain head 584,548, K=217,920, bm-b r585 one-pass "\n'
        '                                       "this window) + FIVE in-flight upstream seats W101 bm-a "\n'
        '                                       "+ W102 bm-c + W103 bm-b + W104 bm-a + W105 bm-c "\n'
        '                                       "burned-unfinalized -- finalize merge loop stays "\n'
        '                                       "FAIL-CLOSED r307 at run time)"),\n'
        '                            "a_seed_base": 255_004,        # law sec.4 W106 A: 255_004..257_003 (arithmetic continuation from the registered W105 A tail)\n'
        '                            "b_exit_seed_base": 60_201,   # law sec.4 W106 B: 60_201..60_400 (arithmetic continuation from the registered W105 B tail)\n'
        '                            "shard_subdir": "n1_w106", "out_name": "n1_w106_results.json",\n'
        '                            "engine_owner": "bm-b"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[106] landed (anchor=W105 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W106 leg --------------
LEG106 = '''
    # --- W106 materializer face (r585 bm-b freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-b's
    #     thirty-sixth owned per machine-derive (engine_owner==bm-b
    #     rows 35 + candidate); wave 106 = first free number after
    #     the REGISTERED W105 row (bm-c r376 freeze f2db133c5 + bm-a
    #     r586 W104-union 48f6f2ff1) -- SINGLE STATE zero seat gap.
    #     Seat published=reserved MSG-20261002-1733-bmb pushed to
    #     origin fe191d370 BEFORE this freeze, r565 law; seat prose
    #     ordinal drift disclosed per r359 law. NINETY-SIXTH engine
    #     wave BY MACHINE-DERIVE (engine_owner rows 95 + candidate;
    #     gate leg0 machine output governs per r359 law). W100
    #     finalize LANDED (chain head 584,548, K=217,920, bm-b r585
    #     one-pass this window) + FIVE in-flight upstream seats W101
    #     bm-a + W102 bm-c + W103 bm-b + W104 bm-a + W105 bm-c
    #     burned-unfinalized -- FAIL-CLOSED r307 at run time. ADMIT
    #     receipt results/_r585bmb_w106_band_gate.py; not a re-pick
    #     (R250: W106 bands were never assigned).
    _set_wave(106)
    try:
        assert WAVE_CONFIGS[106]["a_seed_base"] == pf.N1_BANDS[106]["a"][0], \\
            "W106 A band drift vs law mirror"
        assert WAVE_CONFIGS[106]["b_exit_seed_base"] == \\
            pf.N1_BANDS[106]["b_exit"][0], "W106 B band drift vs law mirror"
        assert WAVE_CONFIGS[106].get("engine_owner") == \\
            pf.N1_BANDS[106].get("engine_owner") == "bm-b", \\
            "W106 engine_owner drift (law mirror parity)"
        w106_a = {A_SEED_BASE + j for j in range(A_N)}
        w106_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w106_a & w106_b), "W106 A/B band overlap"
        assert not (w106_a & reg_ints) and not (w106_b & reg_ints), \\
            "W106 hits SEED_REGISTRY"
        for nm, band in (("A", w106_a), ("B", w106_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W106 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W106 {nm} hits W1"
            assert not (band & probes), f"W106 {nm} hits probe seeds"
        # registered row parity (r307 pinned constants, recent estate)
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
        assert pf.N1_BANDS[103] == {"a": (249_004, 251_003),
                                    "b_exit": (59_401, 59_600),
                                    "engine_owner": "bm-b"}, \\
            "registered W103 row parity drift (r307; bm-b r584)"
        assert pf.N1_BANDS[104] == {"a": (251_004, 253_003),
                                    "b_exit": (59_601, 59_800),
                                    "engine_owner": "bm-a"}, \\
            "registered W104 row parity drift (r307; bm-a r586 union)"
        assert pf.N1_BANDS[105] == {"a": (253_004, 255_003),
                                    "b_exit": (60_001, 60_200),
                                    "engine_owner": "bm-c"}, \\
            "registered W105 row parity drift (r307; bm-c r376)"
        # prior-wave disjointness W2..W105 (single state: all
        # registered, dynamic registry derive, r511 law)
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 106):
            assert not (w106_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W106 A hits W{wprev}"
            assert not (w106_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W106 B hits W{wprev}"
        n3r1_used106 = set(range(70_000, 70_006))
        assert not (w106_a & n3r1_used106) and not (w106_b & n3r1_used106), \\
            "W106 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        assert not (w106_a & lfc_actual12) and not (w106_b & lfc_actual12), \\
            "W106 bands must clear the lfc actual draw range"
        assert not (w106_a & options_actual12) and \\
            not (w106_b & options_actual12), \\
            "W106 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W106 row, r585): both sides arithmetic
        # continuation from the registered W105 tails, zero skips.
        assert WAVE_CONFIGS[106]["a_seed_base"] == 255_004 == 255_003 + 1, (
            "W106 A must be the arithmetic continuation past the W105 "
            "registered A band tail")
        arith_a106 = set(range(255_004, 257_004))
        assert not (arith_a106 & reg_ints), \\
            "W106 A window must be CLEAN (arithmetic ADMIT face)"
        assert WAVE_CONFIGS[106]["b_exit_seed_base"] == 60_201 == 60_200 + 1, (
            "W106 B must be the arithmetic continuation past the W105 "
            "registered B band tail")
        arith_b106 = set(range(60_201, 60_401))
        assert not (arith_b106 & reg_ints), \\
            "W106 B window must be CLEAN (arithmetic ADMIT face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W106-SHARD-0",
                                          "n1w106-0of12"), "W106 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W106-SHARD-11",
                                           "n1w106-11of12")
        assert SHARD_DIR.endswith("n1_w106") and OUT.endswith(
            "n1_w106_results.json"), "W106 path drift"
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 106):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W106 shard dir collides with W{wprev}"
        # W106 finalize cumulative deps: W17..W100 outputs ALL PRESENT
        # (landed chain head 584,548 = W100 bm-b r585; W101/W102/W103/
        # W104/W105 registered with finalizes NOT landed -- in-flight
        # upstream seats, honest note; the finalize merge loop derives
        # the wave set from registry keys at run time and stays
        # FAIL-CLOSED, r307 law).
        for _depw in range(17, 101):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W106 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): every
        # registered wave below 106 composes; wave 15 excluded by
        # design; SINGLE STATE (W2..W105 all registered -- no
        # two-state seat disclosure needed at this freeze).
        assert sorted(w for w in WAVE_CONFIGS if w < 106) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 106)], \\
            "W106 prior-wave set must derive from registry keys (no 15; " \\
            "W2..W105 registered single state)"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W106_PREREG.md")), \\
            "W106 per-wave prereg missing (materializer requirement)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W106 materializer face' in t2b:
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
            + LEG106
            + '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n')
    t2b = rep(t2b, A3, NEW3, eol2b, 'n1-leg106')
    save(FP2, t2b)
    print('edit3 selftest W106 leg landed (insert before T-141 selftest lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment ----------------------
t2c, eol2c = load(FP2)
if '+ W106 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('          "sec.4 W105 row, r376 bm-c] "\n'
          '          "+ T-141 s2 ')
    SEG106 = ('          "sec.4 W105 row, r376 bm-c] "\n'
              '          "+ W106 materializer face [same guard set, dep=W17..W100 "\n'
              '          "outputs ALL PRESENT (landed chain head 584,548 = W100 "\n'
              '          "bm-b r585 one-pass this window, K=217,920; FIVE in-flight "\n'
              '          "upstream seats W101 bm-a + W102 bm-c + W103 bm-b + W104 "\n'
              '          "bm-a + W105 bm-c burned-unfinalized -- FAIL-CLOSED r307 "\n'
              '          "at run time), NINETY-SIXTH ENGINE-OWNED WAVE BY "\n'
              '          "MACHINE-DERIVE (engine_owner rows 95 + candidate) bm-b\'s "\n'
              '          "thirty-sixth owned claim per machine-derive "\n'
              '          "(engine_owner==bm-b rows 35 + candidate), engine_owner=bm-b "\n'
              '          "per engine de-throttle law O-20261001-2355 sec.2 own-"\n'
              '          "continuous-series (wave 106 = first FREE number after the "\n'
              '          "REGISTERED W105 row, SINGLE STATE zero seat gap; seat "\n'
              '          "published=reserved MSG-20261002-1733-bmb pushed to origin "\n'
              '          "fe191d370 BEFORE this freeze, r565 law; seat prose ordinal "\n'
              '          "drift disclosed per r359 law; seat-time skip-past-published "\n'
              '          "hops 2/2 vs freeze-time single-state arithmetic hops 0/0 "\n'
              '          "converge identical bands, no fork face), A=arithmetic "\n'
              '          "continuation from the registered W105 A tail "\n'
              '          "(255_004..257_003 CLEAN hops=0) + B=arithmetic continuation "\n'
              '          "from the registered W105 B tail (60_201..60_400 CLEAN "\n'
              '          "hops=0; ADMIT receipt results/_r585bmb_w106_band_gate.py; "\n'
              '          "W107+ projection A 257_004..259_003 CLEAN / B 60_401..60_600 "\n'
              '          "CLEAN disclosed for the next freezer; not a free pick -- "\n'
              '          "R250), law sec.4 W106 row, r585 bm-b] "\n'
              '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG106, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W106 segment landed (insert after W105 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W106 row ---------------------
ROW106 = """
- N1 波106（r585 bm-b 冻·prereg 时展行）：**第九十六枚引擎波·bm-b 第三十六枚自有波〔机面 derive：engine_owner 行 95+本候选／engine_owner==bm-b 行 35+本候选·r359 律计数面以 gate 机输出为准〕**·engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W105 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-b 实例=tick 架构——冻结 commit 后下一 tick 新进程读活工作树自见新行=免杀重启免做·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 106=注册表 W105 行后首个自由号·单态零席位空档**（W104=bm-a r586 union 48f6f2ff1+W105=bm-c r376 freeze f2db133c5 均已注册·无 skip-past-published 链面）·**席位公示=MSG-20261002-1733-bmb**〔published=reserved r518-① 律·先于冻结 commit 推 origin fe191d370=r565 早可见性律·r523 外科 payload（首推被 pre-push 爪拦=r374 分叉基座伪影·origin 轮中前进他机 W104/W105 冻结·外科重放禁绕爪）·席位 prose 序数漂移披露 r359 律·席位时态 skip-past-published hops 2/2→冻结态单态算术 hops 0/0 带位逐位恒同=确定性收敛无分叉面〕】·本窗实况=**W100 finalize 已落账（净链头 584,548·K=217,920 合并池·bm-b r585 one-pass 本窗）+五在飞上游席（W101 bm-a 12/12 烧毕 finalize 待+W102 bm-c 12/12 烧毕 finalize 待+W103 bm-b 12/12 烧毕 finalize 待+W104 bm-a 烧录他机车道+W105 bm-c 12/12 烧毕 finalize 待）=本波 finalize 链序前置在飞（跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**·**带位（r535 机闸 derive 律·活注册表机证·单态收敛门·ADMIT 回执=results/_r585bmb_w106_band_gate.py rc0 实跑·hops A=0/B=0）**：**A-ext seed=255_004..257_003**（==W105 行 A 尾 255_003+1 起算术续带·步长 2_000·**CLEAN 零拒绝点**）；**B-ext exit seed=60_201..60_400**（==W105 行 B 尾 60_200+1 起算术续带·步长 200·**CLEAN 零拒绝点**；双侧算术续带 W92 r370/W100 r583/W103 r584 先例族）。R250：W106 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W106 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W106_PREREG.md（冻结件·锚=W100 finalize 实测值〔锚滚动律·单波跨锚自 W98 滚动至 W100 跨 W99/W100 双落账窗·r576 锚滚律〕）·**W107+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 257_004..259_003 **CLEAN**；B 60_401..60_600 **CLEAN**（下波按法典 §4 表尾+全 registry 重 derive）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce2106\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW106.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W106 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    106: {"a": (255_004') == 1, 'FIX-B FAIL: W106 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W106"') == 1, 'FIX-B FAIL: W106 config not exactly once'
for w in range(58, 106):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W106 materializer face') == 2, \
    'FIX-B FAIL: W106 leg+summary must be exactly 2'
for w in range(48, 106):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce2106\uff08') == 1, 'FIX-B FAIL: canon W106 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W106 added per face')

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
print('FREEZE_EDITS_OK 106')
