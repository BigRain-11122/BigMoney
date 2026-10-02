# -*- coding: utf-8 -*-
"""r583 bm-a W101 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening.

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED rows (W99 bm-c r374);
  every registered row signature survives exactly; exactly one new W101
  signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.
AST gate (r580/r581 lesson): post-edit ast.parse on both py faces.

W101 = NINETIETH engine wave by MACHINE-DERIVE (engine_owner rows 89 +
candidate), bm-a's TWENTY-EIGHTH owned (engine_owner==bm-a rows 27 +
candidate). First free number after bm-b's PUBLISHED W100 seat
(MSG-20261002-1615-bmb, published=reserved r518-1; W100 NOT yet
registered at this freeze -- single state, skip-past-published chain).
Seat published=reserved MSG-20261002-1625-bma pushed to origin 4e351f312
BEFORE this freeze (r565 early-visibility law).
Bands (skip-past-published W100 from the registered W99 tails + pin):
  A 245_004..247_003 (W100 pub A tail 245_003 + 1, stride 2_000) hops=1.
  B 59_001..59_200   (skip W100 pub B -> 58_951..59_150 refused at 59_000
                      in-window -> past-hit restart per D-20261002-05) hops=2.
  ADMIT receipt results/_r583bma_w101_band_gate.py rc0; banned gate ADMIT 0.
W96 finalize LANDED at this freeze (chain head 575,748, K=209,120). FOUR
in-flight upstream seats (W97 bm-b burned-unfinalized + W98 bm-a
burned-blocked-by-W97 + W99 bm-c burning + W100 bm-b seat-unfrozen) --
finalize merge loop stays FAIL-CLOSED r307 at run time. W102+ projection:
A 247_004..249_003 CLEAN / B 59_201..59_400 CLEAN (next freezer
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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 100))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 100)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 100)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[101] ---------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '101: {"a": (245_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    99: {"a": (241_004, 243_003), "b_exit": (58_551, 58_750),\n'
          '         "engine_owner": "bm-c"},\n'
          '}\n')
    NEW = ('    99: {"a": (241_004, 243_003), "b_exit": (58_551, 58_750),\n'
           '         "engine_owner": "bm-c"},\n'
           '    # NINETIETH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r583 bm-a\n'
           '    # freeze): engine_owner rows 89 + candidate; bm-a\'s\n'
           '    # twenty-eighth owned per machine-derive (engine_owner==bm-a\n'
           '    # rows 27 + candidate). Wave 101 = first free number after\n'
           '    # bm-b\'s PUBLISHED W100 seat (MSG-20261002-1615-bmb,\n'
           '    # published=reserved r518-1; W100 NOT yet registered at this\n'
           '    # freeze -- single state skip-past-published chain from the\n'
           '    # registered W99 tails). Seat published=reserved\n'
           '    # MSG-20261002-1625-bma pushed to origin 4e351f312 BEFORE\n'
           '    # this freeze per r565 early-visibility law.\n'
           '    # W96 finalize LANDED at this freeze (landed chain head\n'
           '    # 575,748 = W96 bm-a r583 one-pass; K=209,120). FOUR\n'
           '    # in-flight upstream seats (W97 bm-b burned-unfinalized +\n'
           '    # W98 bm-a burned-blocked-by-W97 + W99 bm-c burning +\n'
           '    # W100 bm-b seat-unfrozen) -- finalize merge loop stays\n'
           '    # FAIL-CLOSED r307 at run time.\n'
           '    # A = SKIP-PAST-PUBLISHED W100 then arithmetic continuation:\n'
           '    # 245_004..247_003 CLEAN hops=1. B = skip-past-published W100\n'
           '    # -> arithmetic 58_951..59_150 refused at SEED_REGISTRY 59_000\n'
           '    # in-window -> D-20261002-05 pinned past-hit restart\n'
           '    # 59_001..59_200 hops=2 (window-step chain reading BANNED,\n'
           '    # W68-B positive anchor). ADMIT receipt\n'
           '    # results/_r583bma_w101_band_gate.py rc0; live SEED_REGISTRY\n'
           '    # + probe cluster 95_000..95_003 r335 leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 leg.\n'
           '    # W102+ projection: A 247_004..249_003 CLEAN; B 59_201..59_400\n'
           '    # CLEAN (next freezer must re-derive, never transcribe).\n'
           '    # NOT a re-pick (R250: W101 bands were never assigned).\n'
           '    101: {"a": (245_004, 247_003), "b_exit": (59_001, 59_200),\n'
           '         "engine_owner": "bm-a"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[101] landed (anchor=W99 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[101] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '101: {"batch": "PERPETUAL-N1-W101"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w99", "out_name": "n1_w99_results.json",\n'
          '                            "engine_owner": "bm-c"},\n')
    NEW2 = A2 + (
        '                       101: {"batch": "PERPETUAL-N1-W101",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W101_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; NINETIETH ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 89 + candidate; prose "\n'
        '                                       "ordinal drift disclosed per r359 law), own-series "\n'
        '                                       "continuation per O-20261001-2355 sec.2 (first-free-number "\n'
        '                                       "law over bm-b\'s PUBLISHED W100 seat, single state "\n'
        '                                       "skip-past-published chain; seat published=reserved "\n'
        '                                       "MSG-20261002-1625-bma PUSHED to origin BEFORE this "\n'
        '                                       "freeze per r565 early-visibility law), engine_owner=bm-a, "\n'
        '                                       "wave 101: A = skip-past-published W100 then arithmetic "\n'
        '                                       "continuation (245_004..247_003 CLEAN hops=1) + B = "\n'
        '                                       "skip-past-published W100 then pinned past-hit restart "\n'
        '                                       "(arithmetic 58_951..59_150 refused at SEED_REGISTRY 59_000 "\n'
        '                                       "in-window -> D-20261002-05 pin 59_001..59_200 hops=2; "\n'
        '                                       "window-step chain reading BANNED, W68-B positive anchor; "\n'
        '                                       "ADMIT receipt results/_r583bma_w101_band_gate.py; W102+ "\n'
        '                                       "projection: A 247_004..249_003 CLEAN / B 59_201..59_400 "\n'
        '                                       "CLEAN for the next freezer); W96 finalize LANDED at this "\n'
        '                                       "freeze (chain head 575,748, K=209,120) + FOUR in-flight "\n'
        '                                       "upstream seats W97 bm-b burned-unfinalized + W98 bm-a "\n'
        '                                       "burned-blocked-by-W97 + W99 bm-c burning + W100 bm-b "\n'
        '                                       "seat-unfrozen -- finalize merge loop stays FAIL-CLOSED "\n'
        '                                       "r307 at run time)"),\n'
        '                            "a_seed_base": 245_004,        # law sec.4 W101 A: 245_004..247_003 (skip-past-published W100 seat band then arithmetic continuation)\n'
        '                            "b_exit_seed_base": 59_001,   # law sec.4 W101 B: 59_001..59_200 (skip-past-published W100 seat band -> arithmetic refused at 59_000 -> D-20261002-05 pinned past-hit restart)\n'
        '                            "shard_subdir": "n1_w101", "out_name": "n1_w101_results.json",\n'
        '                            "engine_owner": "bm-a"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[101] landed (anchor=W99 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W101 leg --------------
LEG101 = '''
    # --- W101 materializer face (r583 bm-a freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-a's
    #     twenty-eighth owned per machine-derive (engine_owner==bm-a
    #     rows 27 + candidate); wave 101 = first free number after
    #     bm-b's PUBLISHED W100 seat (MSG-20261002-1615-bmb,
    #     published=reserved r518-1; W100 NOT yet registered at this
    #     freeze -- single state skip-past-published chain). Seat
    #     published=reserved MSG-20261002-1625-bma pushed to origin
    #     4e351f312 BEFORE this freeze, r565 law. NINETIETH engine
    #     wave BY MACHINE-DERIVE (engine_owner rows 89 + candidate;
    #     prose ordinal drift disclosed per r359 law). W96 finalize
    #     LANDED (chain head 575,748, K=209,120) + FOUR in-flight
    #     upstream seats W97 bm-b + W98 bm-a + W99 bm-c + W100 bm-b
    #     seat -- FAIL-CLOSED r307 at run time. ADMIT receipt
    #     results/_r583bma_w101_band_gate.py; not a re-pick (R250:
    #     W101 bands were never assigned).
    _set_wave(101)
    try:
        assert WAVE_CONFIGS[101]["a_seed_base"] == pf.N1_BANDS[101]["a"][0], \\
            "W101 A band drift vs law mirror"
        assert WAVE_CONFIGS[101]["b_exit_seed_base"] == \\
            pf.N1_BANDS[101]["b_exit"][0], "W101 B band drift vs law mirror"
        assert WAVE_CONFIGS[101].get("engine_owner") == \\
            pf.N1_BANDS[101].get("engine_owner") == "bm-a", \\
            "W101 engine_owner drift (law mirror parity)"
        w101_a = {A_SEED_BASE + j for j in range(A_N)}
        w101_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w101_a & w101_b), "W101 A/B band overlap"
        assert not (w101_a & reg_ints) and not (w101_b & reg_ints), \\
            "W101 hits SEED_REGISTRY"
        for nm, band in (("A", w101_a), ("B", w101_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W101 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W101 {nm} hits W1"
            assert not (band & probes), f"W101 {nm} hits probe seeds"
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
        assert pf.N1_BANDS[99] == {"a": (241_004, 243_003),
                                   "b_exit": (58_551, 58_750),
                                   "engine_owner": "bm-c"}, \\
            "registered W99 row parity drift (r307; bm-c r374)"
        # prior-wave disjointness W2..W99 (+ W100 if registered by the
        # time this leg runs -- dynamic registry derive, r511 law)
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 101):
            assert not (w101_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W101 A hits W{wprev}"
            assert not (w101_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W101 B hits W{wprev}"
        # W100 PUBLISHED seat bands are reserved (r518-1): W101 must
        # clear them belt-and-braces whether or not W100 registered yet
        assert not (w101_a & set(range(243_004, 245_004))), (
            "W101 A must clear the W100 published seat band (r518-1 "
            "published=reserved)")
        assert not (w101_b & set(range(58_751, 58_951))), (
            "W101 B must clear the W100 published seat band (r518-1 "
            "published=reserved)")
        n3r1_used101 = set(range(70_000, 70_006))
        assert not (w101_a & n3r1_used101) and not (w101_b & n3r1_used101), \\
            "W101 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        assert not (w101_a & lfc_actual12) and not (w101_b & lfc_actual12), \\
            "W101 bands must clear the lfc actual draw range"
        assert not (w101_a & options_actual12) and \\
            not (w101_b & options_actual12), \\
            "W101 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W101 row, r583): skip-past-published
        # W100 from the registered W99 tails; A arithmetic continuation
        # after the published-band skip; B pinned past-hit restart.
        assert WAVE_CONFIGS[101]["a_seed_base"] == 245_004 == 245_003 + 1, (
            "W101 A must be the arithmetic continuation past the W100 "
            "published A band tail (skip-past-published r518-1)")
        arith_a101 = set(range(245_004, 247_004))
        assert not (arith_a101 & reg_ints), \\
            "W101 A window must be CLEAN (skip-past-published ADMIT face)"
        assert WAVE_CONFIGS[101]["b_exit_seed_base"] == 59_001 == 59_000 + 1, (
            "W101 B must be the D-20261002-05 pinned past-hit restart "
            "past SEED_REGISTRY 59_000 (arithmetic 58_951..59_150 refused "
            "in-window; window-step chain reading BANNED, W68-B anchor)")
        arith_b101 = set(range(59_001, 59_201))
        assert not (arith_b101 & reg_ints), \\
            "W101 B window must be CLEAN (pin-restart ADMIT face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W101-SHARD-0",
                                          "n1w101-0of12"), "W101 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W101-SHARD-11",
                                           "n1w101-11of12")
        assert SHARD_DIR.endswith("n1_w101") and OUT.endswith(
            "n1_w101_results.json"), "W101 path drift"
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 101):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W101 shard dir collides with W{wprev}"
        # W101 finalize cumulative deps: W17..W96 outputs ALL PRESENT
        # (landed chain head 575,748 = W96 bm-a r583 one-pass; W97/W98/
        # W99/W100 registered-or-seat with finalizes NOT landed --
        # in-flight upstream seats, honest note; the finalize merge loop
        # derives the wave set from registry keys at run time and stays
        # FAIL-CLOSED, r307 law).
        for _depw in range(17, 97):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W101 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): every
        # registered wave below 101 composes; wave 15 excluded by
        # design; W100 seat-published but unregistered at this freeze
        # -- if bm-b lands the W100 freeze before a W101 finalize run,
        # the run-time set grows by 100 automatically (two-state honest
        # disclosure per r307 law).
        assert sorted(w for w in WAVE_CONFIGS if w < 101) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 100)] + \\
            ([100] if 100 in WAVE_CONFIGS else []), \\
            "W101 prior-wave set must derive from registry keys (no 15; " \\
            "W2..W99 registered + W100 two-state at run time)"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W101_PREREG.md")), \\
            "W101 per-wave prereg missing (materializer requirement)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W101 materializer face' in t2b:
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
            + LEG101
            + '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n')
    t2b = rep(t2b, A3, NEW3, eol2b, 'n1-leg101')
    save(FP2, t2b)
    print('edit3 selftest W101 leg landed (insert before T-141 selftest lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment ----------------------
t2c, eol2c = load(FP2)
if '+ W101 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('          "W99 row, r374 bm-c] "\n'
          '          "+ T-141 s2 ')
    SEG101 = ('          "W99 row, r374 bm-c] "\n'
              '          "+ W101 materializer face [same guard set, dep=W17..W96 "\n'
              '          "outputs ALL PRESENT (landed chain head 575,748 = W96 "\n'
              '          "bm-a r583 one-pass, K=209,120; FOUR in-flight upstream "\n'
              '          "seats W97 bm-b burned-unfinalized + W98 bm-a burned-"\n'
              '          "blocked-by-W97 + W99 bm-c burning + W100 bm-b seat-"\n'
              '          "unfrozen -- FAIL-CLOSED r307 at run time), NINETIETH "\n'
              '          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows "\n'
              '          "89 + candidate; prose ordinal drift disclosed per "\n'
              '          "r359 law) bm-a\'s twenty-eighth owned claim per "\n'
              '          "machine-derive (engine_owner==bm-a rows 27 + "\n'
              '          "candidate), engine_owner=bm-a per engine de-throttle "\n'
              '          "law O-20261001-2355 sec.2 own-continuous-series (wave "\n'
              '          "101 = first FREE number after bm-b\'s PUBLISHED W100 "\n'
              '          "seat, single state skip-past-published chain; seat "\n'
              '          "published=reserved MSG-20261002-1625-bma pushed to "\n'
              '          "origin BEFORE this freeze, r565 law), A=skip-past-"\n'
              '          "published W100 then arithmetic continuation (245_004.."\n'
              '          "247_003 CLEAN hops=1) + B=skip-past-published W100 "\n'
              '          "then D-20261002-05 pinned past-hit restart (arithmetic "\n'
              '          "58_951..59_150 refused at SEED_REGISTRY 59_000 in-window "\n'
              '          "-> 59_001..59_200 hops=2; window-step chain reading "\n'
              '          "BANNED, W68-B positive anchor; ADMIT receipt "\n'
              '          "results/_r583bma_w101_band_gate.py; W102+ projection A "\n'
              '          "247_004..249_003 CLEAN / B 59_201..59_400 CLEAN "\n'
              '          "disclosed for the next freezer; not a free pick -- "\n'
              '          "R250), W100 published-band clearance leg (r518-1), "\n'
              '          "N3-R1 used-seed leg, probe-seed cluster leg, law sec.4 "\n'
              '          "W101 row, r583 bm-a] "\n'
              '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG101, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W101 segment landed (insert after W99 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W101 row ---------------------
ROW101 = """
- N1 波101（r583 bm-a 冻·prereg 时展行）：**第九十枚引擎波·bm-a 第二十八枚自有波〔机面 derive：engine_owner 行 89+本候选／engine_owner==bm-a 行 27+本候选〕**·engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 同 W10-W99 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-a 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启免做·W44/W45/W48/W54/W57/W62/W64/W68/W73/W75/W77/W81/W84/W86/W87/W90/W94/W96/W98 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 101=bm-b W100 席位公示后首个自由号·skip-past-published 链**（注册表尾=W99 行〔bm-c r374〕→W100 已公示带 reserved 面〔MSG-20261002-1615-bmb·published=reserved r518-①〕→W101 首净窗·单态两读收敛）·**席位公示=MSG-20261002-1625-bma**〔published=reserved r518-① 律·先于冻结 commit 推 origin 4e351f312=r565 早可见性律〕】·本窗实况=**W96 finalize 已落账（净链头 575,748·K=209,120 合并池）+四在飞上游席（W97 bm-b 12/12 烧毕 finalize 待+W98 bm-a 12/12 烧毕被 W97 占位阻塞 finalize 待+W99 bm-c 烧录在飞+W100 bm-b 席公示未冻结）=本波 finalize 链序前置在飞（跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**·**带位（r583 机闸 derive 律·活注册表机证·单态收敛门·ADMIT 回执=results/_r583bma_w101_band_gate.py rc0 实跑·hops A=1/B=2）**：**A-ext seed=245_004..247_003**（skip-past-published W100 已公示 A 带 243_004..245_003 后首净窗·步长 2_000·**CLEAN 零拒绝点**）；**B-ext exit seed=59_001..59_200**（skip-past-published W100 已公示 B 带 58_751..58_950 后算术窗 58_951..59_150 **在窗内撞 SEED_REGISTRY 点 59_000**→**D-20261002-05 钉死行 past-hit restart 59_001**·禁窗步链读法 59_101..59_300〔W68-B 正锚〕·拒绝非自由挑）。R250：W101 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W101 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W101_PREREG.md（冻结件·锚=W96 finalize 实测值〔锚滚动律·单波跨锚自 W92 滚动至 W96〕）·**W102+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 247_004..249_003 **CLEAN**；B 59_201..59_400 **CLEAN**（下波按法典 §4 表尾+全 registry 重 derive）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce2101\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW101.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W101 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    101: {"a": (245_004') == 1, 'FIX-B FAIL: W101 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W101"') == 1, 'FIX-B FAIL: W101 config not exactly once'
for w in range(58, 100):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W101 materializer face') == 2, \
    'FIX-B FAIL: W101 leg+summary must be exactly 2'
for w in range(48, 100):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce2101\uff08') == 1, 'FIX-B FAIL: canon W101 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W101 added per face')

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
print('FREEZE_EDITS_OK 101')
