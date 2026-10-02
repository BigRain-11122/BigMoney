# -*- coding: utf-8 -*-
"""r592 bm-a W114 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening.

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED rows (W109 bm-b +
  W110 bm-a + W111 bm-b + W112 bm-a + W113 bm-c); every registered row
  signature survives exactly; exactly one new W114 signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.
AST gate (r580/r581 lesson): post-edit ast.parse on both py faces.

W114 = ONE HUNDRED-AND-FOURTH engine wave BY MACHINE-DERIVE (engine_owner
rows 103 + candidate; gate leg0 machine output governs per r359 law),
bm-a's THIRTY-THIRD owned (engine_owner==bm-a rows 32 + candidate).
First free number after the REGISTERED W113 row (bm-c r382 freeze
eeb062290) -- SINGLE STATE zero seat gap (W2..W113 all registered).
Seat published=reserved MSG-20261002-2014-bma pushed to origin 2cd67216a
BEFORE this freeze (r565 early-visibility law; one r589 reset-FF-reland
loop over the bm-c appender 3-shard mid-window advance; payload=1 seat
MSG, deletion-set EMPTY, rev.A = only published face).
Bands:
  A 271_004..273_003 (W113 A tail 271_003 + 1, stride 2_000) hops=0 CLEAN.
  B 62_201..62_400   (W113 B tail 62_200 + 1, stride 200) hops=0 CLEAN.
  ADMIT receipt results/_r592bma_w114_band_gate.py rc0; banned gate ADMIT 0.
W113 finalize LANDED (chain head 613,148, K=246,520 = bm-c r382 one-pass).
ZERO in-flight upstream seats (W2..W113 all landed) -- finalize merge loop
still derives the wave set from registry keys at run time, FAIL-CLOSED
r307 two-state law always on.
W115+ projection (pinned D-20261002-05): A 273_004..275_003 CLEAN /
B 62_501..62_700 (arithmetic 62_401..62_600 refused at SEED_REGISTRY
grid_sleeve_p1=62_500 mid-window -> past-hit restart; the W114 seat MSG
advisory line 62_601..62_800 = window-step-chain reading, superseded for
mid-window hits by the pinned law, disclosed not rewritten; zero impact
on W114 candidate bands -- both readings converge at hops=0).
"""
import subprocess, sys, os, ast, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# machine-derived W113 anchor values for the canon row (read, never copied)
_d113 = json.load(open(os.path.join(REPO, "results/perpetual_faces/n1_w113_results.json"), encoding="utf-8"))
_npc = _d113["null_pool_cumulative"]
_sk = _d113["skill_line_v2_k_lift"]
_K = _npc["merged"]["n_values"]
assert _K == 246520, f"W113 K drift {_K}"
_se_key = f"se_mu_at_k{_K}"
_w113_se_mu = repr(_npc[_se_key])
_w113_klift_raw = _sk["line_delta_k_lift"]
_w113_klift = ("+" + repr(_w113_klift_raw) if _w113_klift_raw > 0
               else ("\u2212" + repr(abs(_w113_klift_raw)) if _w113_klift_raw < 0
                     else "0.0000"))
_w113_mu = repr(_npc["merged"]["mu"]).replace("-", "\u2212")
_w113_p95 = repr(_d113["families"]["A_random_engine_exit"]["full_sharpe_p95"])

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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 114))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 114)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 114)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[114] ---------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '114: {"a": (271_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    113: {"a": (269_004, 271_003), "b_exit": (62_001, 62_200),\n'
          '         "engine_owner": "bm-c"},\n'
          '}\n')
    NEW = ('    113: {"a": (269_004, 271_003), "b_exit": (62_001, 62_200),\n'
           '         "engine_owner": "bm-c"},\n'
           '    # ONE HUNDRED-AND-FOURTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r592 bm-a\n'
           '    # freeze): engine_owner rows 103 + candidate; bm-a\'s thirty-\n'
           '    # third owned per machine-derive (engine_owner==bm-a rows 32 +\n'
           '    # candidate). Wave 114 = first free number after the REGISTERED\n'
           '    # W113 row (bm-c r382 freeze eeb062290) -- SINGLE STATE zero seat\n'
           '    # gap (W2..W113 all registered). Seat published=reserved\n'
           '    # MSG-20261002-2014-bma pushed to origin 2cd67216a BEFORE this\n'
           '    # freeze per r565 early-visibility law (one r589 reset-FF-reland\n'
           '    # loop over the bm-c appender 3-shard mid-window advance; payload=1\n'
           '    # seat MSG, deletion-set EMPTY; rev.A = only published face).\n'
           '    # W113 finalize LANDED (chain head 613,148, K=246,520 = bm-c r382\n'
           '    # one-pass). ZERO in-flight upstream seats (W2..W113 all landed) --\n'
           '    # finalize merge loop still derives the wave set from registry\n'
           '    # keys at run time, FAIL-CLOSED r307 two-state law always on.\n'
           '    # A = arithmetic continuation from the registered W113 A tail:\n'
           '    # 271_004..273_003 CLEAN hops=0. B = arithmetic continuation from\n'
           '    # the registered W113 B tail: 62_201..62_400 CLEAN hops=0 (both\n'
           '    # clean windows per ADMIT receipt results/_r592bma_w114_band_gate.py\n'
           '    # rc0; live SEED_REGISTRY + probe cluster 95_000..95_003 r335 leg +\n'
           '    # N3-R1 used-seed band 70_000..70_005 MSG-183x r529 leg.\n'
           '    # W115+ projection (pinned D-20261002-05): A 273_004..275_003\n'
           '    # CLEAN; B arithmetic 62_401..62_600 refused at SEED_REGISTRY\n'
           '    # grid_sleeve_p1=62_500 (mid-window hit) -> past-hit restart\n'
           '    # 62_501..62_700 CLEAN (next freezer must re-derive, never\n'
           '    # transcribe; the W114 seat MSG advisory line 62_601..62_800 =\n'
           '    # window-step-chain reading, superseded for mid-window hits).\n'
           '    # NOT a re-pick (R250: W114 bands were never assigned).\n'
           '    114: {"a": (271_004, 273_003), "b_exit": (62_201, 62_400),\n'
           '         "engine_owner": "bm-a"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[114] landed (anchor=W113 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[114] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '114: {"batch": "PERPETUAL-N1-W114"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w113", "out_name": "n1_w113_results.json",\n'
          '                            "engine_owner": "bm-c"},\n')
    NEW2 = A2 + (
        '                       114: {"batch": "PERPETUAL-N1-W114",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W114_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; ONE HUNDRED-AND-FOURTH ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 103 + candidate), own-series "\n'
        '                                       "continuation per O-20261001-2355 sec.2 (first-free-number "\n'
        '                                       "law after the REGISTERED W113 row bm-c r382 freeze eeb062290, "\n'
        '                                       "SINGLE STATE zero seat gap W2..W113 all registered; seat "\n'
        '                                       "published=reserved MSG-20261002-2014-bma PUSHED to origin "\n'
        '                                       "2cd67216a BEFORE this freeze per r565 early-visibility law; "\n'
        '                                       "pre-seat probe and freeze-window band-gate runs derive "\n'
        '                                       "identical, no fork face; seat landed via one r589 "\n'
        '                                       "reset-FF-reland loop over the bm-c appender 3-shard "\n'
        '                                       "mid-window advance, payload=1 seat MSG deletion-set EMPTY, "\n'
        '                                       "rev.A = only published face), engine_owner=bm-a, wave 114: "\n'
        '                                       "A = arithmetic continuation from the registered W113 A tail "\n'
        '                                       "(271_004..273_003 CLEAN hops=0) + B = arithmetic continuation "\n'
        '                                       "from the registered W113 B tail (62_201..62_400 CLEAN hops=0; "\n'
        '                                       "ADMIT receipt results/_r592bma_w114_band_gate.py; W115+ "\n'
        '                                       "projection per pinned D-20261002-05: A 273_004..275_003 CLEAN / "\n'
        '                                       "B 62_501..62_700 past-hit restart over SEED_REGISTRY "\n'
        '                                       "grid_sleeve_p1=62_500 for the next freezer); W113 finalize "\n'
        '                                       "LANDED (chain head 613,148, K=246,520, bm-c r382 one-pass) + "\n'
        '                                       "ZERO in-flight upstream seats -- finalize merge loop still "\n'
        '                                       "derives the wave set from registry keys at run time, "\n'
        '                                       "FAIL-CLOSED r307 always on)"),\n'
        '                            "a_seed_base": 271_004,        # law sec.4 W114 A: 271_004..273_003 (arithmetic continuation from the registered W113 A tail)\n'
        '                            "b_exit_seed_base": 62_201,   # law sec.4 W114 B: 62_201..62_400 (arithmetic continuation from the registered W113 B tail)\n'
        '                            "shard_subdir": "n1_w114", "out_name": "n1_w114_results.json",\n'
        '                            "engine_owner": "bm-a"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[114] landed (anchor=W113 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W114 leg --------------
LEG114 = '''
    # --- W114 materializer face (r592 bm-a freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-a's
    #     thirty-third owned per machine-derive (engine_owner==bm-a
    #     rows 32 + candidate); wave 114 = first free number after
    #     the REGISTERED W113 row (bm-c r382 freeze eeb062290) --
    #     SINGLE STATE zero seat gap (W2..W113 all registered).
    #     Seat published=reserved MSG-20261002-2014-bma pushed to
    #     origin 2cd67216a BEFORE this freeze, r565 law (one r589
    #     reset-FF-reland loop over the bm-c appender 3-shard
    #     mid-window advance; payload=1 seat MSG; deletion-set
    #     EMPTY; rev.A = only published face). ONE HUNDRED-AND-
    #     FOURTH engine wave BY MACHINE-DERIVE (engine_owner rows
    #     103 + candidate; gate leg0 machine output governs per
    #     r359 law). W113 finalize LANDED (chain head 613,148,
    #     K=246,520, bm-c r382 one-pass) + ZERO in-flight upstream
    #     seats -- finalize merge loop still derives the wave set
    #     from registry keys at run time, FAIL-CLOSED r307 always
    #     on. ADMIT receipt results/_r592bma_w114_band_gate.py;
    #     not a re-pick (R250: W114 bands were never assigned).
    _set_wave(114)
    try:
        assert WAVE_CONFIGS[114]["a_seed_base"] == pf.N1_BANDS[114]["a"][0], \\
            "W114 A band drift vs law mirror"
        assert WAVE_CONFIGS[114]["b_exit_seed_base"] == \\
            pf.N1_BANDS[114]["b_exit"][0], "W114 B band drift vs law mirror"
        assert WAVE_CONFIGS[114].get("engine_owner") == \\
            pf.N1_BANDS[114].get("engine_owner") == "bm-a", \\
            "W114 engine_owner drift (law mirror parity)"
        w114_a = {A_SEED_BASE + j for j in range(A_N)}
        w114_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w114_a & w114_b), "W114 A/B band overlap"
        assert not (w114_a & reg_ints) and not (w114_b & reg_ints), \\
            "W114 hits SEED_REGISTRY"
        for nm, band in (("A", w114_a), ("B", w114_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W114 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W114 {nm} hits W1"
            assert not (band & probes), f"W114 {nm} hits probe seeds"
        # registered row parity (r307 pinned constants, recent estate)
        assert pf.N1_BANDS[108] == {"a": (259_004, 261_003),
                                    "b_exit": (60_601, 60_800),
                                    "engine_owner": "bm-c"}, \\
            "registered W108 row parity drift (r307; bm-c r378)"
        assert pf.N1_BANDS[109] == {"a": (261_004, 263_003),
                                    "b_exit": (61_001, 61_200),
                                    "engine_owner": "bm-b"}, \\
            "registered W109 row parity drift (r307; bm-b r587)"
        assert pf.N1_BANDS[110] == {"a": (263_004, 265_003),
                                    "b_exit": (61_201, 61_400),
                                    "engine_owner": "bm-a"}, \\
            "registered W110 row parity drift (r307; bm-a r589)"
        assert pf.N1_BANDS[111] == {"a": (265_004, 267_003),
                                    "b_exit": (61_401, 61_600),
                                    "engine_owner": "bm-b"}, \\
            "registered W111 row parity drift (r307; bm-b r589)"
        assert pf.N1_BANDS[112] == {"a": (267_004, 269_003),
                                    "b_exit": (61_601, 61_800),
                                    "engine_owner": "bm-a"}, \\
            "registered W112 row parity drift (r307; bm-a r590)"
        assert pf.N1_BANDS[113] == {"a": (269_004, 271_003),
                                    "b_exit": (62_001, 62_200),
                                    "engine_owner": "bm-c"}, \\
            "registered W113 row parity drift (r307; bm-c r382)"
        # prior-wave disjointness W2..W113 (single state: all
        # registered, dynamic registry derive, r511 law)
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 114):
            assert not (w114_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W114 A hits W{wprev}"
            assert not (w114_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W114 B hits W{wprev}"
        n3r1_used114 = set(range(70_000, 70_006))
        assert not (w114_a & n3r1_used114) and not (w114_b & n3r1_used114), \\
            "W114 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        assert not (w114_a & lfc_actual12) and not (w114_b & lfc_actual12), \\
            "W114 bands must clear the lfc actual draw range"
        assert not (w114_a & options_actual12) and \\
            not (w114_b & options_actual12), \\
            "W114 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W114 row, r592): BOTH sides =
        # arithmetic continuation from the registered W113 tails,
        # zero skips (double-arithmetic family, W112 precedent).
        assert WAVE_CONFIGS[114]["a_seed_base"] == 271_004 == 271_003 + 1, (
            "W114 A must be the arithmetic continuation past the W113 "
            "registered A band tail")
        arith_a114 = set(range(271_004, 273_004))
        assert not (arith_a114 & reg_ints), \\
            "W114 A window must be CLEAN (arithmetic ADMIT face)"
        assert WAVE_CONFIGS[114]["b_exit_seed_base"] == 62_201 == 62_200 + 1, (
            "W114 B must be the arithmetic continuation past the W113 "
            "registered B band tail")
        arith_b114 = set(range(62_201, 62_401))
        assert not (arith_b114 & reg_ints), \\
            "W114 B window must be CLEAN (arithmetic ADMIT face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W114-SHARD-0",
                                          "n1w114-0of12"), "W114 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W114-SHARD-11",
                                           "n1w114-11of12")
        assert SHARD_DIR.endswith("n1_w114") and OUT.endswith(
            "n1_w114_results.json"), "W114 path drift"
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 114):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W114 shard dir collides with W{wprev}"
        # W114 finalize cumulative deps: W17..W113 outputs ALL PRESENT
        # (landed chain head 613,148 = W113 bm-c r382 one-pass; ZERO
        # in-flight upstream seats, single closed state; the finalize
        # merge loop derives the wave set from registry keys at run
        # time and stays FAIL-CLOSED, r307 law).
        for _depw in range(17, 114):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W114 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): every
        # registered wave below 114 composes; wave 15 excluded by
        # design; SINGLE STATE (W2..W113 all registered -- no
        # two-state seat disclosure needed at this freeze).
        assert sorted(w for w in WAVE_CONFIGS if w < 114) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 114)], \\
            "W114 prior-wave set must derive from registry keys (no 15; " \\
            "W2..W113 registered single state)"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W114_PREREG.md")), \\
            "W114 per-wave prereg missing (materializer requirement)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W114 materializer face' in t2b:
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
            + LEG114
            + '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n')
    t2b = rep(t2b, A3, NEW3, eol2b, 'n1-leg114')
    save(FP2, t2b)
    print('edit3 selftest W114 leg landed (insert before T-141 selftest lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment ----------------------
t2c, eol2c = load(FP2)
if '+ W114 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    # r594 patch: A5 anchor corrected to the actual r382 bm-c SUMMARY face
    # (the "free pick -- R250)," and "law sec.4 W113 row..." tail literals sit
    # on TWO separate lines in the landed file; the r592 dead-session draft
    # glued them into one -- never executed, caught live at edit5).
    A5 = ('"law sec.4 W113 row, r382 bm-c] "\n'
          '          "+ T-141 s2 ')
    SEG114 = ('"law sec.4 W113 row, r382 bm-c] "\n'
              '          "+ W114 materializer face [same guard set, dep=W17..W113 "\n'
              '"outputs ALL PRESENT (landed chain head 613,148 = W113 "\n'
              '"bm-c r382 one-pass, K=246,520; ZERO in-flight upstream seats "\n'
              '"-- W2..W113 all landed, finalize merge loop still derives the "\n'
              '"wave set from registry keys at run time, FAIL-CLOSED r307 "\n'
              '"always on), ONE HUNDRED-AND-FOURTH ENGINE-OWNED WAVE BY "\n'
              '"MACHINE-DERIVE (engine_owner rows 103 + candidate) bm-a\'s "\n'
              '"thirty-third owned claim per machine-derive (engine_owner==bm-a "\n'
              '"rows 32 + candidate), engine_owner=bm-a per engine de-throttle "\n'
              '"law O-20261001-2355 sec.2 own-continuous-series (wave 114 = "\n'
              '"first FREE number after the REGISTERED W113 row bm-c r382 "\n'
              '"freeze eeb062290, SINGLE STATE zero seat gap W2..W113 all "\n'
              '"registered; seat published=reserved MSG-20261002-2014-bma "\n'
              '"pushed to origin 2cd67216a BEFORE this freeze, r565 law; "\n'
              '"seat landed via one r589 reset-FF-reland loop over the bm-c "\n'
              '"appender 3-shard mid-window advance, payload=1 seat MSG "\n'
              '"deletion-set EMPTY, rev.A = only published face), "\n'
              '"A=arithmetic continuation from the registered W113 A tail "\n'
              '"(271_004..273_003 CLEAN hops=0) + B=arithmetic continuation "\n'
              '"from the registered W113 B tail (62_201..62_400 CLEAN hops=0; "\n'
              '"ADMIT receipt results/_r592bma_w114_band_gate.py; W115+ "\n'
              '"projection per pinned D-20261002-05: A 273_004..275_003 CLEAN / "\n'
              '"B 62_501..62_700 past-hit restart over SEED_REGISTRY "\n'
              '"grid_sleeve_p1=62_500 disclosed for the next freezer; not a "\n'
              '"free pick -- R250), law sec.4 W114 row, r592 bm-a] "\n'
              '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG114, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W114 segment landed (insert after W113 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W114 row ---------------------
ROW114 = f"""
- N1 波114（r592 bm-a 冻·prereg 时展行）：**第一百零四枚引擎波·bm-a 第三十三枚自有波〔机面 derive：engine_owner 行 103+本候选／engine_owner==bm-a 行 32+本候选·r359 律计数面以 gate 机输出为准〕**·engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 同 W10-W113 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-a 实例=**tick 架构**——每 tick 新进程读活工作树·冻结编辑落工作树后下一 tick 自见 W114 行并点火〔r535 律 tick 面免杀重启免做〕·点火验证唯一证据=产物增长面 r325 律·2 tick 窗】·【never-dry 供给律常设步·**波号 114=注册表 W113 行后首个自由号·单态零席位空档**（W109=bm-b r587 freeze f077ae11b+W110=bm-a r589 freeze ff0b1869b+W111=bm-b r589 freeze e0a103ec1+W112=bm-a r590 freeze 0c4d67910+W113=bm-c r382 freeze eeb062290 均已注册·表尾=W113 行）·**席位公示=MSG-20261002-2014-bma**〔published=reserved r518-① 律·先于冻结 commit 推 origin 2cd67216a=r565 早可见性律·一次 r589 撤-FF-重落环（bm-c 引擎 appender 三分片中窗落账首推拒）·payload=席位 MSG 单件 deletion-set 空·rev.A=唯一发布面〕】·本窗实况=**W113 finalize 已落账（净链头 613,148·K=246,520 合并池·bm-c r382 W113 one-pass）+零在飞上游席（W2..W113 全落账=本波 finalize 链序前置零空档·跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**·**带位（r535 机闸 derive 律·活注册表机证·单态收敛门·ADMIT 回执=results/_r592bma_w114_band_gate.py rc0 实跑·pre-seat probe _r592bma_w114_probe.py 先跑·双窗 derive 恒等·hops A=0/B=0）**：**A-ext seed=271_004..273_003**（==W113 行 A 尾 271_003+1 起算术续带·步长 2_000·**CLEAN 零拒绝点**）；**B-ext exit seed=62_201..62_400**（==W113 行 B 尾 62_200+1 起算术续带·步长 200·**CLEAN 零拒绝点**·双侧算术续带=W92/W100/W103/W106/W107/W110/W111/W112 先例族）。R250：W114 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W114 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W114_PREREG.md（冻结件·锚=W113 finalize 实测值〔merged mu {_w113_mu}·K=246,520·K-lift {_w113_klift}·A-p95 {_w113_p95}·se_mu {_w113_se_mu}〕）·**W115+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 273_004..275_003 **CLEAN**（hops=0）；B **62_501..62_700（hops=1·撞值跳位）**——算术窗 62_401..62_600 撞 SEED_REGISTRY `grid_sleeve_p1`=62_500（中位命中）→ 法典 §4 D-20261002-05 越 hit 起窗（席位尾投影「62_601..62_800」=窗步链读法面 advisory 勘注·gate 回执为准）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce2114\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW114.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W114 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    114: {"a": (271_004') == 1, 'FIX-B FAIL: W114 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W114"') == 1, 'FIX-B FAIL: W114 config not exactly once'
for w in range(58, 114):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W114 materializer face') == 2, \
    'FIX-B FAIL: W114 leg+summary must be exactly 2'
for w in range(48, 114):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce2114\uff08') == 1, 'FIX-B FAIL: canon W114 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W114 added per face')

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
print('FREEZE_EDITS_OK 114')
