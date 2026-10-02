# -*- coding: utf-8 -*-
"""r374 bm-c W99 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening.

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED rows (W98 bm-a r582);
  every registered row signature survives exactly; exactly one new W99
  signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.
AST gate (r580/r581 lesson): post-edit ast.parse on both py faces.

W99 = EIGHTY-NINTH engine wave by MACHINE-DERIVE (engine_owner rows 88 +
candidate), bm-c's TWENTY-NINTH owned (engine_owner==bm-c rows 28 +
candidate). First free number after the registered W98 row (SINGLE STATE,
zero seat gap -- W98 registered by bm-a r582, landed origin 8be174832).
Seat published=reserved MSG-20261002-1625-bmc pushed to origin fed0b4054
BEFORE this freeze (r565 early-visibility law).
Bands:
  A 241_004..243_003 (W98 A tail 241_003 + 1, stride 2_000) CLEAN hops=0.
  B 58_551..58_750   D-20261002-05 pinned-skip derive: arithmetic window
     58_401..58_600 refused at SEED_REGISTRY in-band values 58_500
     (mf_ic_p1) + 58_550 (sina_construct_p1) -> past-hit restart (hops=2),
     first clean window 58_551..58_750.
  ADMIT receipt results/_r374bmc_w99_band_gate.py rc0; banned gate ADMIT 0.
W94 finalize LANDED at this freeze (chain head 571,348 = W94 bm-a r582
one-pass; K=204,720). FOUR in-flight upstream seats (W95 bm-b + W96 bm-a +
W97 bm-b + W98 bm-a -- all registered, finalize pending) -- finalize merge
loop stays FAIL-CLOSED r307 at run time. W100+ projection: A
243_004..245_003 CLEAN / B 58_751..58_950 CLEAN (next freezer must
re-derive, never transcribe).
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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 99))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 99)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 99)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[99] ---------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '99: {"a": (241_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    98: {"a": (239_004, 241_003), "b_exit": (58_201, 58_400),\n'
          '         "engine_owner": "bm-a"},\n'
          '}\n')
    NEW = ('    98: {"a": (239_004, 241_003), "b_exit": (58_201, 58_400),\n'
           '         "engine_owner": "bm-a"},\n'
           '    # EIGHTY-NINTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r374 bm-c\n'
           '    # freeze): engine_owner rows 88 + candidate; bm-c\'s\n'
           '    # twenty-ninth owned per machine-derive (engine_owner==bm-c\n'
           '    # rows 28 + candidate). Wave 99 = first free number after the\n'
           '    # registered W98 row (SINGLE STATE, zero seat gap; no\n'
           '    # published seat to skip). Seat published=reserved\n'
           '    # MSG-20261002-1625-bmc pushed to origin fed0b4054 BEFORE\n'
           '    # this freeze per r565 early-visibility law.\n'
           '    # W94 finalize LANDED at this freeze (landed chain head\n'
           '    # 571,348 = W94 bm-a r582 one-pass; K=204,720). FOUR\n'
           '    # in-flight upstream seats (W95 bm-b + W96 bm-a + W97 bm-b\n'
           '    # + W98 bm-a -- all registered, finalize pending) --\n'
           '    # finalize merge loop stays FAIL-CLOSED r307 at run time.\n'
           '    # A side ARITHMETIC CONTINUATION from the registered W98\n'
           '    # A tail: A 241_004..243_003 CLEAN zero refusal points\n'
           '    # (machine-verified at prereg time, ADMIT receipt\n'
           '    # results/_r374bmc_w99_band_gate.py rc0 hops 0; live\n'
           '    # SEED_REGISTRY + probe cluster 95_000..95_003 r335 leg +\n'
           '    # N3-R1 used-seed band 70_000..70_005 MSG-183x r529 leg).\n'
           '    # B side D-20261002-05 PINNED-SKIP DERIVE: arithmetic window\n'
           '    # 58_401..58_600 refused at SEED_REGISTRY in-band values\n'
           '    # 58_500 (mf_ic_p1) + 58_550 (sina_construct_p1) -> past-hit\n'
           '    # restart per the D-20261002-05 pinned line; first clean\n'
           '    # window B 58_551..58_750 (hops=2; ADMIT receipt same).\n'
           '    # W100+ projection: A 243_004..245_003 CLEAN; B 58_751..58_950\n'
           '    # CLEAN (next freezer must re-derive, never transcribe).\n'
           '    # NOT a re-pick (R250: W99 bands were never assigned).\n'
           '    99: {"a": (241_004, 243_003), "b_exit": (58_551, 58_750),\n'
           '         "engine_owner": "bm-c"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[99] landed (anchor=W98 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[99] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '99: {"batch": "PERPETUAL-N1-W99"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w98", "out_name": "n1_w98_results.json",\n'
          '                            "engine_owner": "bm-a"},\n')
    NEW2 = A2 + (
        '                       99: {"batch": "PERPETUAL-N1-W99",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W99_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; EIGHTY-NINTH ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 88 + candidate; prose "\n'
        '                                       "ordinal drift disclosed per r359 law), own-series "\n'
        '                                       "continuation per O-20261001-2355 sec.2 (first-free-number "\n'
        '                                       "law over the registered W98 row, SINGLE STATE zero seat "\n'
        '                                       "gap; seat published=reserved MSG-20261002-1625-bmc "\n'
        '                                       "PUSHED to origin BEFORE this freeze per r565 early-"\n'
        '                                       "visibility law), engine_owner=bm-c, wave 99: A side "\n'
        '                                       "ARITHMETIC CONTINUATION from the registered W98 A tail "\n'
        '                                       "(241_004..243_003 CLEAN hops 0) + B side D-20261002-05 "\n'
        '                                       "PINNED-SKIP DERIVE (arithmetic window 58_401..58_600 "\n'
        '                                       "refused at SEED_REGISTRY in-band values 58_500 "\n'
        '                                       "(mf_ic_p1) + 58_550 (sina_construct_p1) -> past-hit "\n'
        '                                       "restart; first clean window 58_551..58_750 hops 2; ADMIT "\n'
        '                                       "receipt results/_r374bmc_w99_band_gate.py; W100+ "\n'
        '                                       "projection: A 243_004..245_003 CLEAN / B 58_751..58_950 "\n'
        '                                       "CLEAN); W94 finalize LANDED at this freeze (chain head "\n'
        '                                       "571,348, K=204,720) + FOUR in-flight upstream seats "\n'
        '                                       "W95 bm-b + W96 bm-a + W97 bm-b + W98 bm-a all registered "\n'
        '                                       "finalize-pending -- finalize merge loop stays FAIL-CLOSED "\n'
        '                                       "r307 at run time)"),\n'
        '                            "a_seed_base": 241_004,        # law sec.4 W99 A: 241_004..243_003 (arithmetic continuation from the registered W98 tail)\n'
        '                            "b_exit_seed_base": 58_551,   # law sec.4 W99 B: 58_551..58_750 (D-20261002-05 pinned-skip derive past SEED_REGISTRY 58_500/58_550)\n'
        '                            "shard_subdir": "n1_w99", "out_name": "n1_w99_results.json",\n'
        '                            "engine_owner": "bm-c"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[99] landed (anchor=W98 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W99 leg --------------
LEG99 = '''
    # --- W99 materializer face (r374 bm-c freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-c's
    #     twenty-ninth owned per machine-derive (engine_owner==bm-c
    #     rows 28 + candidate); wave 99 = first free number after the
    #     registered W98 row (SINGLE STATE, zero seat gap). Seat
    #     published=reserved MSG-20261002-1625-bmc pushed to origin
    #     fed0b4054 BEFORE this freeze, r565 law. EIGHTY-NINTH engine
    #     wave BY MACHINE-DERIVE (engine_owner rows 88 + candidate;
    #     prose ordinal drift disclosed per r359 law). W94 finalize
    #     LANDED (chain head 571,348, K=204,720) + FOUR in-flight
    #     upstream seats W95 bm-b + W96 bm-a + W97 bm-b + W98 bm-a
    #     (all registered, finalize pending) -- FAIL-CLOSED r307 at
    #     run time. ADMIT receipt results/_r374bmc_w99_band_gate.py;
    #     not a re-pick (R250: W99 bands were never assigned).
    _set_wave(99)
    try:
        assert WAVE_CONFIGS[99]["a_seed_base"] == pf.N1_BANDS[99]["a"][0], (
            "W99 A band drift vs law mirror")
        assert WAVE_CONFIGS[99]["b_exit_seed_base"] == \\
            pf.N1_BANDS[99]["b_exit"][0], ("W99 B band drift vs law mirror")
        assert WAVE_CONFIGS[99].get("engine_owner") == \\
            pf.N1_BANDS[99].get("engine_owner") == "bm-c", \\
            "W99 engine_owner drift (law mirror parity)"
        w99_a = {A_SEED_BASE + j for j in range(A_N)}
        w99_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w99_a & w99_b), "W99 A/B band overlap"
        assert not (w99_a & reg_ints) and not (w99_b & reg_ints), \\
            "W99 hits SEED_REGISTRY"
        for nm, band in (("A", w99_a), ("B", w99_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W99 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W99 {nm} hits W1"
            assert not (band & probes), f"W99 {nm} hits probe seeds"
        # registered row parity (r307 pinned constants, recent estate)
        assert pf.N1_BANDS[95] == {"a": (233_004, 235_003),
                                   "b_exit": (57_501, 57_700),
                                   "engine_owner": "bm-b"}, \\
            "registered W95 row parity drift (r307; bm-b r580)"
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
        # prior-wave disjointness W2..W98 (ALL registered at this
        # freeze; single state, no in-flight registration gap below 99)
        for wprev in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
                [w for w in range(16, 99)]:
            assert not (w99_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W99 A hits W{wprev}"
            assert not (w99_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W99 B hits W{wprev}"
        assert not (w99_a & set(range(239_004, 241_004))) and \\
            not (w99_b & set(range(58_201, 58_401))), (
            "W99 bands must clear the W98 registered bands (prior-wave "
            "loop belt-and-braces)")
        n3r1_used99 = set(range(70_000, 70_006))
        assert not (w99_a & n3r1_used99) and not (w99_b & n3r1_used99), \\
            "W99 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        assert not (w99_a & lfc_actual12) and not (w99_b & lfc_actual12), \\
            "W99 bands must clear the lfc actual draw range"
        assert not (w99_a & options_actual12) and \\
            not (w99_b & options_actual12), \\
            "W99 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W99 row, r374): A = arithmetic
        # continuation from the registered W98 A tail, zero refusals.
        assert WAVE_CONFIGS[99]["a_seed_base"] == 241_004 == 241_003 + 1, (
            "W99 A must be the arithmetic continuation from the "
            "registered W98 A tail")
        arith_a99 = set(range(241_004, 243_004))
        assert not (arith_a99 & reg_ints), \\
            "W99 A window must be CLEAN (arithmetic continuation ADMIT face)"
        # B = D-20261002-05 pinned-skip derive: the arithmetic window
        # 58_401..58_600 is REFUSED (in-band SEED_REGISTRY hits --
        # honest refusal face, refusal facts derive not transcribe) and
        # the landed window 58_551..58_750 is the first CLEAN window
        # past the last hit (past-hit restart per D-20261002-05).
        arith_b99_refused = set(range(58_401, 58_601))
        assert arith_b99_refused & reg_ints, (
            "W99 B arithmetic window must carry the SEED_REGISTRY "
            "in-band refusal hits (D-20261002-05 pin forcing face)")
        assert 58_500 in (arith_b99_refused & reg_ints) and \\
            58_550 in (arith_b99_refused & reg_ints), (
            "W99 B refusal facts must include 58_500 and 58_550 "
            "(mf_ic_p1 / sina_construct_p1, gate refusal receipt)")
        assert WAVE_CONFIGS[99]["b_exit_seed_base"] == 58_551 == 58_550 + 1, (
            "W99 B must start past the LAST in-band hit per the "
            "D-20261002-05 pinned past-hit restart (hit+1)")
        arith_b99 = set(range(58_551, 58_751))
        assert not (arith_b99 & reg_ints), \\
            "W99 B window must be CLEAN (pinned-skip ADMIT face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W99-SHARD-0",
                                          "n1w99-0of12"), "W99 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W99-SHARD-11",
                                           "n1w99-11of12")
        assert SHARD_DIR.endswith("n1_w99") and OUT.endswith(
            "n1_w99_results.json"), "W99 path drift"
        for wprev in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
                [w for w in range(16, 99)]:
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W99 shard dir collides with W{wprev}"
        # W99 finalize cumulative deps: W17..W94 outputs ALL PRESENT
        # (landed chain head 571,348 = W94; W95/W96/W97/W98 registered
        # with finalizes NOT landed -- in-flight upstream seats, honest
        # note; the finalize merge loop derives the wave set from
        # registry keys at run time and stays FAIL-CLOSED, r307 law).
        for _depw in range(17, 95):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W99 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): all
        # waves below 99 registered at this freeze (single state, zero
        # seat gap; wave 15 excluded by design).
        assert sorted(w for w in WAVE_CONFIGS if w < 99) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 99)], \\
            "W99 prior-wave set must derive from registry keys (no 15; " \\
            "W2..W98 ALL registered at this freeze)"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W99_PREREG.md")), \\
            "W99 per-wave prereg missing (materializer requirement)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W99 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    # r580/r581 anchor law: FULL-LINE anchor, replacement = anchor head
    # + blank + new leg + anchor tail-head line (no full-anchor backfill
    # duplication of the body between; anchor bytes probed repr-exact).
    A3 = ('        _set_wave(2)\n'
          '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n')
    A3X = A3.replace('\n', eol2b)
    assert t2b.count(A3X) == 1, f'selftest anchor not unique: {t2b.count(A3X)}'
    NEW3 = ('        _set_wave(2)\n'
            '\n'
            + LEG99
            + '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n')
    t2b = rep(t2b, A3, NEW3, eol2b, 'n1-leg99')
    save(FP2, t2b)
    print('edit3 selftest W99 leg landed (insert before T-141 selftest lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment ----------------------
t2c, eol2c = load(FP2)
if '+ W99 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('          "W98 row, r582 bm-a] "\n'
          '          "+ T-141 s2 ')
    SEG99 = ('          "W98 row, r582 bm-a] "\n'
             '          "+ W99 materializer face [same guard set, dep=W17..W94 "\n'
             '          "outputs ALL PRESENT (landed chain head 571,348 = W94 "\n'
             '          "bm-a r582 one-pass, K=204,720; FOUR in-flight upstream "\n'
             '          "seats W95 bm-b + W96 bm-a + W97 bm-b + W98 bm-a all "\n'
             '          "registered finalize-pending -- FAIL-CLOSED r307 at run "\n'
             '          "time), EIGHTY-NINTH ENGINE-OWNED WAVE BY MACHINE-DERIVE "\n'
             '          "(engine_owner rows 88 + candidate; prose ordinal drift "\n'
             '          "disclosed per r359 law) bm-c\'s twenty-ninth owned "\n'
             '          "claim per machine-derive (engine_owner==bm-c rows 28 "\n'
             '          "+ candidate), engine_owner=bm-c per engine de-throttle "\n'
             '          "law O-20261001-2355 sec.2 own-continuous-series (wave 99 "\n'
             '          "= first FREE number after the registered W98 row, SINGLE "\n'
             '          "STATE zero seat gap; seat published=reserved "\n'
             '          "MSG-20261002-1625-bmc pushed to origin BEFORE this "\n'
             '          "freeze, r565 law), A side ARITHMETIC CONTINUATION from "\n'
             '          "the registered W98 A tail (241_004..243_003 CLEAN hops "\n'
             '          "0) + B side D-20261002-05 PINNED-SKIP DERIVE (arithmetic "\n'
             '          "window 58_401..58_600 refused at SEED_REGISTRY in-band "\n'
             '          "values 58_500 mf_ic_p1 + 58_550 sina_construct_p1 -> "\n'
             '          "past-hit restart; first clean window 58_551..58_750 hops "\n'
             '          "2; ADMIT receipt results/_r374bmc_w99_band_gate.py; "\n'
             '          "W100+ projection A 243_004..245_003 CLEAN / B "\n'
             '          "58_751..58_950 CLEAN disclosed for the next freezer; "\n'
             '          "not a free pick -- R250), "\n'
             '          "N3-R1 used-seed leg, probe-seed cluster leg, law sec.4 "\n'
             '          "W99 row, r374 bm-c] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG99, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W99 segment landed (insert after W98 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W99 row ---------------------
ROW99 = """
- N1 波99（r374 bm-c 冻·prereg 时展行）：**第八十九枚引擎波·bm-c 第二十九枚自有波〔机面 derive：engine_owner 行 88+本候选／engine_owner==bm-c 行 28+本候选〕**·engine_owner=bm-c·SATURATION_ENGINE_LAW §1/§2 同 W10-W98 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-c 实例=**常驻架构 v0.4-d20261002-03**——n1_bands mtime-watch 模块重载修复已载（D-20261002-03）·冻结编辑落工作树后 LIVE 引擎下一 tick 自见新行=**免杀重启免做**（r325/r330 kill-restart 序在 mtime-reload 修复后免做）·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 99=注册表 W98 行后首个自由号·单态零席位空档**（W98 bm-a r582 已注册=表尾实况·无 skip-past-published 链面）·**席位公示=MSG-20261002-1625-bmc**〔published=reserved r518-① 律·先于冻结 commit 推 origin fed0b4054=r565 早可见性律〕】·本窗实况=**W94 finalize 已落账（净链头 571,348·K=204,720 合并池）+四在飞上游席（W95 bm-b finalize 待+W96 bm-a finalize 待+W97 bm-b finalize 待+W98 bm-a finalize 待）=本波 finalize 链序前置在飞（跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**·**带位（r374 机闸 derive 律·活注册表机证·单态收敛门·ADMIT 回执=results/_r374bmc_w99_band_gate.py rc0 实跑·A hops 0/B hops 2）**：**A-ext seed=241_004..243_003**（==W98 行 A 尾 241_003+1 起·步长 2_000·**CLEAN 零拒绝点**·纯算术续带）；**B-ext exit seed=58_551..58_750**（**D-20261002-05 钉死跳位 derive**：W98 行 B 尾 58_400+1 算术位 58_401..58_600 撞 SEED_REGISTRY 带内值〔58_500=mf_ic_p1·58_550=sina_construct_p1〕=带内中位命中→**越 hit 起窗**〔窗自 hit+1 起扫首个净窗·D-20261002-05 钉死行·r566 W63 双读法分叉后集团裁定面〕·两跳 58_501→58_551·末窗 58_551..58_750 **CLEAN**）。R250：W99 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W99 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W99_PREREG.md（冻结件·锚=W94 finalize 实测值〔锚滚动律·单波跨锚自 W76 滚动至 W94〕）·**W100+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 243_004..245_003 **CLEAN**；B 58_751..58_950 **CLEAN**。
"""
FP4 = os.path.join(REPO, 'research', 'PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce299\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW99.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W99 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    99: {"a": (241_004') == 1, 'FIX-B FAIL: W99 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W99"') == 1, 'FIX-B FAIL: W99 config not exactly once'
for w in range(58, 99):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W99 materializer face') == 2, \
    'FIX-B FAIL: W99 leg+summary must be exactly 2'
for w in range(48, 99):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce299\uff08') == 1, 'FIX-B FAIL: canon W99 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W99 added per face')

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
print('FREEZE_EDITS_OK 99')
