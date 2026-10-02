# -*- coding: utf-8 -*-
"""r376 bm-c W105 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening.

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED rows (W103 bm-b
  r584); every registered row signature survives exactly; exactly one new
  W105 signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.
AST gate (r580/r581 lesson): post-edit ast.parse on both py faces.

W105 = NINETY-FOURTH engine wave by MACHINE-DERIVE (engine_owner rows 93 +
candidate; gate leg0 machine output governs per r359 law), bm-c's
THIRTY-FIRST owned (engine_owner==bm-c rows 30 + candidate).
First free number after the REGISTERED W103 row (bm-b r584 freeze
fbbde996f) SKIPPING the published W104 seat (bm-a MSG-20261002-1712,
published=reserved r518-1; W104 seat-published unregistered honest note).
Seat published=reserved MSG-20261002-1738-bmc pushed to origin 565a6b254
BEFORE this freeze (r565 early-visibility law).
Bands:
  A 253_004..255_003 (skip W104 pub 251_004..253_003, hops=1).
  B 60_001..60_200   (skip W104 pub 59_601..59_800 then pinned past-hit
      restart past SEED_REGISTRY div_lowvol_p1=60_000 upper-edge of the
      refused window 59_801..60_000; both readings converge, W74-B/W81
      edge family, hops=2).
  ADMIT receipt results/_r376bmc_w105_band_gate.py rc0; banned gate ADMIT 0.
W99 finalize LANDED at this freeze (chain head 582,348, K=215,720 = bm-c
r376 one-pass). FOUR in-flight upstream seats (W100 bm-b burned-unfinalized
+ W101 bm-a burned-unfinalized + W102 bm-c burned-unfinalized + W103 bm-b
registered in-flight r584 8/12) -- finalize merge loop stays FAIL-CLOSED
r307 at run time. W106+ projection: A 255_004..257_003 CLEAN / B 60_201..
60_400 CLEAN (next freezer re-derives, never transcribes).
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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 104))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 104)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 104)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[105] ---------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '105: {"a": (253_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    103: {"a": (249_004, 251_003), "b_exit": (59_401, 59_600),\n'
          '         "engine_owner": "bm-b"},\n'
          '}\n')
    NEW = ('    103: {"a": (249_004, 251_003), "b_exit": (59_401, 59_600),\n'
           '         "engine_owner": "bm-b"},\n'
           '    # NINETY-FOURTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r376 bm-c\n'
           '    # freeze): engine_owner rows 93 + candidate; bm-c\'s thirty-\n'
           '    # first owned per machine-derive (engine_owner==bm-c rows 30 +\n'
           '    # candidate). Wave 105 = first free number after the REGISTERED\n'
           '    # W103 row (bm-b r584 freeze fbbde996f) SKIPPING the published\n'
           '    # W104 seat (bm-a MSG-20261002-1712, published=reserved r518-1;\n'
           '    # W104 seat-published unregistered honest note). Seat\n'
           '    # published=reserved MSG-20261002-1738-bmc pushed to origin\n'
           '    # 565a6b254 BEFORE this freeze per r565 early-visibility law.\n'
           '    # W99 finalize LANDED at this freeze (landed chain head\n'
           '    # 582,348 = W99 bm-c r376; K=215,720). FOUR in-flight upstream\n'
           '    # seats (W100 bm-b burned-unfinalized + W101 bm-a burned-\n'
           '    # unfinalized + W102 bm-c burned-unfinalized + W103 bm-b\n'
           '    # registered in-flight) -- finalize merge loop stays FAIL-CLOSED\n'
           '    # r307 at run time.\n'
           '    # A = skip-past-published W104 then arithmetic continuation:\n'
           '    # 253_004..255_003 CLEAN hops=1. B = skip-past-published W104\n'
           '    # then pinned past-hit restart past SEED_REGISTRY\n'
           '    # div_lowvol_p1=60_000 upper-edge of the refused window\n'
           '    # 59_801..60_000: 60_001..60_200 CLEAN hops=2 (both readings\n'
           '    # converge, W74-B/W81 edge family, no fork face). ADMIT receipt\n'
           '    # results/_r376bmc_w105_band_gate.py rc0; live SEED_REGISTRY\n'
           '    # + probe cluster 95_000..95_003 r335 leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 leg.\n'
           '    # W106+ projection: A 255_004..257_003 CLEAN; B 60_201..60_400\n'
           '    # CLEAN (next freezer must re-derive, never transcribe).\n'
           '    # NOT a re-pick (R250: W105 bands were never assigned).\n'
           '    105: {"a": (253_004, 255_003), "b_exit": (60_001, 60_200),\n'
           '         "engine_owner": "bm-c"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[105] landed (anchor=W103 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[105] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '105: {"batch": "PERPETUAL-N1-W105"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w103", "out_name": "n1_w103_results.json",\n'
          '                            "engine_owner": "bm-b"},\n')
    NEW2 = A2 + (
        '                       105: {"batch": "PERPETUAL-N1-W105",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W105_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; NINETY-FOURTH ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 93 + candidate), own-series "\n'
        '                                       "continuation per O-20261001-2355 sec.2 (first-free-number "\n'
        '                                       "law after the REGISTERED W103 row SKIPPING the published "\n'
        '                                       "W104 seat bm-a MSG-20261002-1712, W104 seat-published "\n'
        '                                       "unregistered honest note; seat published=reserved "\n'
        '                                       "MSG-20261002-1738-bmc PUSHED to origin 565a6b254 BEFORE "\n'
        '                                       "this freeze per r565 early-visibility law), "\n'
        '                                       "engine_owner=bm-c, wave 105: A = skip-past-published "\n'
        '                                       "W104 then arithmetic continuation (253_004..255_003 "\n'
        '                                       "CLEAN hops=1) + B = skip-past-published W104 then "\n'
        '                                       "pinned past-hit restart past SEED_REGISTRY "\n'
        '                                       "div_lowvol_p1=60_000 upper-edge (59_801..60_000 refused "\n'
        '                                       "-> 60_001..60_200 CLEAN hops=2; both readings converge, "\n'
        '                                       "W74-B/W81 edge family; ADMIT receipt "\n'
        '                                       "results/_r376bmc_w105_band_gate.py; W106+ projection: "\n'
        '                                       "A 255_004..257_003 CLEAN / B 60_201..60_400 CLEAN for "\n'
        '                                       "the next freezer); W99 finalize LANDED at this freeze "\n'
        '                                       "(chain head 582,348, K=215,720) + FOUR in-flight "\n'
        '                                       "upstream seats W100 bm-b burned-unfinalized + W101 bm-a "\n'
        '                                       "burned-unfinalized + W102 bm-c burned-unfinalized + "\n'
        '                                       "W103 bm-b registered in-flight -- finalize merge loop stays "\n'
        '                                       "FAIL-CLOSED r307 at run time)"),\n'
        '                            "a_seed_base": 253_004,        # law sec.4 W105 A: 253_004..255_003 (skip-past-published W104 then arithmetic continuation)\n'
        '                            "b_exit_seed_base": 60_001,   # law sec.4 W105 B: 60_001..60_200 (skip-past-published W104 + pinned past-hit restart past 60_000)\n'
        '                            "shard_subdir": "n1_w105", "out_name": "n1_w105_results.json",\n'
        '                            "engine_owner": "bm-c"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[105] landed (anchor=W103 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W105 leg --------------
LEG105 = '''
    # --- W105 materializer face (r376 bm-c freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-c's
    #     thirty-first owned per machine-derive (engine_owner==bm-c
    #     rows 30 + candidate); wave 105 = first free number after
    #     the REGISTERED W103 row (bm-b r584 freeze fbbde996f)
    #     SKIPPING the published W104 seat (bm-a MSG-20261002-1712,
    #     published=reserved r518-1; W104 seat-published
    #     unregistered honest note). Seat published=reserved
    #     MSG-20261002-1738-bmc pushed to origin 565a6b254 BEFORE
    #     this freeze, r565 law. NINETY-FOURTH engine wave BY
    #     MACHINE-DERIVE (engine_owner rows 93 + candidate; gate
    #     leg0 machine output governs per r359 law). W99 finalize
    #     LANDED (chain head 582,348, K=215,720 = bm-c r376) + FOUR
    #     in-flight upstream seats W100 bm-b + W101 bm-a + W102 bm-c
    #     burned-unfinalized + W103 bm-b registered in-flight --
    #     FAIL-CLOSED r307 at run time. ADMIT receipt
    #     results/_r376bmc_w105_band_gate.py; not a re-pick (R250:
    #     W105 bands were never assigned).
    _set_wave(105)
    try:
        assert WAVE_CONFIGS[105]["a_seed_base"] == pf.N1_BANDS[105]["a"][0], \\
            "W105 A band drift vs law mirror"
        assert WAVE_CONFIGS[105]["b_exit_seed_base"] == \\
            pf.N1_BANDS[105]["b_exit"][0], "W105 B band drift vs law mirror"
        assert WAVE_CONFIGS[105].get("engine_owner") == \\
            pf.N1_BANDS[105].get("engine_owner") == "bm-c", \\
            "W105 engine_owner drift (law mirror parity)"
        w105_a = {A_SEED_BASE + j for j in range(A_N)}
        w105_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w105_a & w105_b), "W105 A/B band overlap"
        assert not (w105_a & reg_ints) and not (w105_b & reg_ints), \\
            "W105 hits SEED_REGISTRY"
        for nm, band in (("A", w105_a), ("B", w105_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W105 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W105 {nm} hits W1"
            assert not (band & probes), f"W105 {nm} hits probe seeds"
        # registered row parity (r307 pinned constants, recent estate)
        assert pf.N1_BANDS[99] == {"a": (241_004, 243_003),
                                  "b_exit": (58_551, 58_750),
                                  "engine_owner": "bm-c"}, \\
            "registered W99 row parity drift (r307; bm-c r374)"
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
        # prior-wave disjointness W2..W103 (single state: all
        # registered, dynamic registry derive, r511 law)
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 105):
            assert not (w105_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W105 A hits W{wprev}"
            assert not (w105_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W105 B hits W{wprev}"
        n3r1_used105 = set(range(70_000, 70_006))
        assert not (w105_a & n3r1_used105) and not (w105_b & n3r1_used105), \\
            "W105 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        assert not (w105_a & lfc_actual12) and not (w105_b & lfc_actual12), \\
            "W105 bands must clear the lfc actual draw range"
        assert not (w105_a & options_actual12) and \\
            not (w105_b & options_actual12), \\
            "W105 bands must clear the options_wave2 actual draw range"
        # W104 published-band disjointness (r518-1 reserved face)
        w104_pub_a = set(range(251_004, 253_004))
        w104_pub_b = set(range(59_601, 59_801))
        assert not (w105_a & w104_pub_a), \\
            "W105 A must clear the W104 published band (r518-1 reserved)"
        assert not (w105_b & w104_pub_b), \\
            "W105 B must clear the W104 published band (r518-1 reserved)"
        # band facts (law sec.4 W105 row, r376): A = skip-past-published
        # W104 then arithmetic continuation; B = skip-past-published W104
        # then pinned past-hit restart past div_lowvol_p1=60_000.
        assert WAVE_CONFIGS[105]["a_seed_base"] == 253_004 == 251_003 + 1 + 2_000, (
            "W105 A must be the skip-past-published restart past the W104 "
            "published band (arithmetic position 251_004..253_003 refused "
            "by the published face)")
        arith_pos_a105 = set(range(251_004, 253_004))
        assert arith_pos_a105 == w104_pub_a, (
            "W105 A arithmetic position == the W104 published band "
            "(skip-past-published refusal fact)")
        assert not (set(range(253_004, 255_004)) & reg_ints), \\
            "W105 A window must be CLEAN (ADMIT face)"
        assert WAVE_CONFIGS[105]["b_exit_seed_base"] == 60_001, (
            "W105 B must be the pinned past-hit restart past the "
            "SEED_REGISTRY edge point 60_000 (D-20261002-05)")
        arith_b105 = set(range(59_801, 60_001))
        assert 60_000 in reg_ints and (arith_b105 & reg_ints), \\
            "W105 B refused window 59_801..60_000 must contain the registry " \\
            "edge hit div_lowvol_p1=60_000 (refusal fact)"
        assert not (set(range(60_001, 60_201)) & reg_ints), \\
            "W105 B window must be CLEAN (ADMIT face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W105-SHARD-0",
                                          "n1w105-0of12"), "W105 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W105-SHARD-11",
                                           "n1w105-11of12")
        assert SHARD_DIR.endswith("n1_w105") and OUT.endswith(
            "n1_w105_results.json"), "W105 path drift"
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 105):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W105 shard dir collides with W{wprev}"
        # W105 finalize cumulative deps: W17..W99 outputs ALL PRESENT
        # (landed chain head 582,348 = W99 bm-c r376; W100/W101/W102
        # registered with finalizes NOT landed + W103 registered
        # in-flight -- honest note; the finalize merge loop derives
        # the wave set from registry keys at run time and stays
        # FAIL-CLOSED, r307 law).
        for _depw in range(17, 100):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W105 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): every
        # registered wave below 105 composes; wave 15 excluded by
        # design; W104 seat-published unregistered honest note (W2..W103
        # all registered -- W104 gap disclosed, r519/r578 precedent).
        assert sorted(w for w in WAVE_CONFIGS if w < 105) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 104)], \\
            "W105 prior-wave set must derive from registry keys (no 15; " \\
            "W2..W103 registered single state; W104 seat-gap honest note)"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W105_PREREG.md")), \\
            "W105 per-wave prereg missing (materializer requirement)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W105 materializer face' in t2b:
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
            + LEG105
            + '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n')
    t2b = rep(t2b, A3, NEW3, eol2b, 'n1-leg105')
    save(FP2, t2b)
    print('edit3 selftest W105 leg landed (insert before T-141 selftest lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment ----------------------
t2c, eol2c = load(FP2)
if '+ W105 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('          "R250), law sec.4 W103 row, r584 bm-b] "\n'
          '          "+ T-141 s2 ')
    SEG105 = ('          "R250), law sec.4 W103 row, r584 bm-b] "\n'
              '          "+ W105 materializer face [same guard set, dep=W17..W99 "\n'
              '          "outputs ALL PRESENT (landed chain head 582,348 = W99 "\n'
              '          "bm-c r376 one-pass, K=215,720; FOUR in-flight upstream "\n'
              '          "seats W100 bm-b burned-unfinalized + W101 bm-a burned-"\n'
              '          "unfinalized + W102 bm-c burned-unfinalized + W103 bm-b "\n'
              '          "registered in-flight -- FAIL-CLOSED r307 at run "\n'
              '          "time), NINETY-FOURTH ENGINE-OWNED WAVE BY MACHINE-DERIVE "\n'
              '          "(engine_owner rows 93 + candidate; prose ordinal drift "\n'
              '          "disclosed per r359 law) bm-c\'s thirty-first owned claim "\n'
              '          "per machine-derive (engine_owner==bm-c rows 30 + "\n'
              '          "candidate), engine_owner=bm-c per engine de-throttle law "\n'
              '          "O-20261001-2355 sec.2 own-continuous-series (wave 105 = "\n'
              '          "first FREE number after the REGISTERED W103 row SKIPPING "\n'
              '          "the published W104 seat bm-a MSG-20261002-1712, W104 seat-"\n'
              '          "published unregistered honest note; seat published= "\n'
              '          "reserved MSG-20261002-1738-bmc pushed to origin "\n'
              '          "565a6b254 BEFORE this freeze, r565 law), A=skip-past-"\n'
              '          "published W104 then arithmetic continuation "\n'
              '          "(253_004..255_003 CLEAN hops=1) + B=skip-past-published "\n'
              '          "W104 then pinned past-hit restart past SEED_REGISTRY "\n'
              '          "div_lowvol_p1=60_000 upper-edge (59_801..60_000 refused "\n'
              '          "-> 60_001..60_200 CLEAN hops=2; both readings converge, "\n'
              '          "W74-B/W81 edge family, no fork face; ADMIT receipt "\n'
              '          "results/_r376bmc_w105_band_gate.py; W106+ projection A "\n'
              '          "255_004..257_003 CLEAN / B 60_201..60_400 CLEAN "\n'
              '          "disclosed for the next freezer; not a free pick -- "\n'
              '          "R250), N3-R1 used-seed leg, probe-seed cluster leg, "\n'
              '          "W104 published-band disjointness leg (r518-1), law "\n'
              '          "sec.4 W105 row, r376 bm-c] "\n'
              '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG105, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W105 segment landed (insert after W103 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W105 row ---------------------
ROW105 = """
- N1 波105（r376 bm-c 冻·prereg 时展行）：**第九十四枚引擎波·bm-c 第三十一枚自有波〔机面 derive：engine_owner 行 93+本候选／engine_owner==bm-c 行 30+本候选·r359 律计数面以 gate 机输出为准〕**·engine_owner=bm-c·SATURATION_ENGINE_LAW §1/§2 同 W10-W103 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-c 实例=常驻架构 v0.4 mtime-reload——冻结 commit 后下一 tick 重读活树自见新行自燃·免杀重启免做·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 105=注册表 W103 行〔bm-b r584〕后首个自由号·skip-past-published bm-a W104 公示带**（W104 席位公示=MSG-20261002-1712-bma·published=reserved r518-①·未注册=席位空档诚实注记）·**席位公示=MSG-20261002-1738-bmc**〔published=reserved r518-① 律·先于冻结 commit 推 origin 565a6b254=r565 早可见性律〕】·本窗实况=**W99 finalize 已落账（净链头 582,348·K=215,720 合并池）+四在飞上游席（W100 bm-b 12/12 烧毕 finalize 待+W101 bm-a 12/12 烧毕 finalize 待+W102 bm-c 12/12 烧毕 finalize 待+W103 bm-b r584 窗 8/12 在途）=本波 finalize 链序前置在飞（跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**·**带位（r376 机闸 derive 律·活注册表机证·ADMIT 回执=results/_r376bmc_w105_band_gate.py rc0 实跑·hops A=1/B=2）**：**A-ext seed=253_004..255_003**（skip-past-published W104 公示带 251_004..253_003 后算术续带·步长 2_000·**CLEAN 零拒绝点**）；**B-ext exit seed=60_001..60_200**（skip-past-published W104 公示带 59_601..59_800→算术位 59_801..60_000 撞 SEED_REGISTRY **[60_000=div_lowvol_p1]**=上缘端点→**越 hit 起窗**〔D-20261002-05 钉死行·两读法同解=W74-B/W81 边缘族·无分叉面〕）。R250：W105 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W105 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W105_PREREG.md（冻结件·锚=W99 finalize 实测值〔锚滚动律·单波跨锚自 W94 滚动至 W99·r576 锚滚律〕）·**W106+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 255_004..257_003 **CLEAN**；B 60_201..60_400 **CLEAN**（下波按法典 §4 表尾+全 registry 重 derive）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce2105\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW105.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W105 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    105: {"a": (253_004') == 1, 'FIX-B FAIL: W105 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W105"') == 1, 'FIX-B FAIL: W105 config not exactly once'
for w in range(58, 104):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W105 materializer face') == 2, \
    'FIX-B FAIL: W105 leg+summary must be exactly 2'
for w in range(48, 104):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce2105\uff08') == 1, 'FIX-B FAIL: canon W105 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W105 added per face')

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
print('FREEZE_EDITS_OK 105')
