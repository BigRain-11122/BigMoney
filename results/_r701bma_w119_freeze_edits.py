# -*- coding: utf-8 -*-
"""r701 bm-a W119 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening
(adapted verbatim from the r678 bm-b W118 freeze-edits pattern).

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED rows; every
  registered row signature survives exactly; exactly one new W119
  signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.
AST gate (r580/r581 lesson): post-edit ast.parse on both py faces.

W119 = ONE HUNDRED-AND-NINTH engine wave BY MACHINE-DERIVE (engine_owner
rows 108 + candidate; gate leg0 machine output governs per r359 law),
bm-a's THIRTY-FIFTH owned (engine_owner==bm-a rows 34 + candidate).
First free number after the REGISTERED W118 row (bm-b r678 freeze
565e5b0b4) -- SINGLE STATE zero seat gap (W2..W118 all registered).
Seat published=reserved MSG-2026-10-04-2323-bma-w119-seat pushed to origin
432a1eaca BEFORE this freeze (r565 early-visibility law; payload = seat
MSG only, deletion-set EMPTY, rev.A = only published face).
Bands:
  A 281_004..283_003 (W118 A tail 281_003 + 1, stride 2_000) hops=0 CLEAN.
  B 65_450..65_649   (W118 B tail 65_449 + 1, stride 200) hops=0 CLEAN
                     (both arithmetic continuation, zero-jump
                     two-reading-identical face; cross-machine convergence
                     with the bm-b r678 W118 gate-tail W119+ projection
                     re-derived here, not transcribed).
  ADMIT receipt results/_r701bma_w119_band_gate.py rc0; banned gate ADMIT 0.
W115 finalize LANDED (net chain head 617,548, K=250,920) + THREE in-flight
upstream seats: W116 bm-b (registered bc1e82773, 6/12 shards burned,
engine RAM floor gate self-paced, finalize pending) + W117 bm-a (registered
c36a087ea, 12/12 shards burned, finalize rehearsal PASS r684 and ARMED on
W116 landing) + W118 bm-b (registered 565e5b0b4, 0/12 burned, queued behind
W116 on the bm-b engine) -- finalize merge loop still derives the wave set
from registry keys at run time, FAIL-CLOSED r307 two-state law always on.
W120+ projection (gate-derived this window): A 283_004..285_003 CLEAN
hops=0 / B 65_650..65_849 CLEAN hops=0 (next freezer must re-derive,
never transcribe; r587 law).
"""
import subprocess, sys, os, ast, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# machine-derived W115 anchor values for the canon row (read, never copied)
_d115 = json.load(open(os.path.join(REPO, "results/perpetual_faces/n1_w115_results.json"), encoding="utf-8"))
_npc = _d115["null_pool_cumulative"]
_sk = _d115["skill_line_v2_k_lift"]
_K = _npc["merged"]["n_values"]
assert _K == 250920, f"W115 K drift {_K}"
_se_key = f"se_mu_at_k{_K}"
_w115_se_mu = repr(_npc[_se_key])
_w115_klift_raw = _sk["line_delta_k_lift"]
_w115_klift = ("+" + repr(_w115_klift_raw) if _w115_klift_raw > 0
               else ("\u2212" + repr(abs(_w115_klift_raw)) if _w115_klift_raw < 0
                     else "0.0000"))
_w115_mu = repr(_npc["merged"]["mu"]).replace("-", "\u2212")
_w115_p95 = repr(_d115["families"]["A_random_engine_exit"]["full_sharpe_p95"])

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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 119))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 119)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 119)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[119] ---------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '119: {"a": (281_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    118: {"a": (279_004, 281_003), "b_exit": (65_250, 65_449),\n'
          '         "engine_owner": "bm-b"},\n'
          '}\n')
    NEW = ('    118: {"a": (279_004, 281_003), "b_exit": (65_250, 65_449),\n'
           '         "engine_owner": "bm-b"},\n'
           '    # W119 (r701 bm-a freeze, own-series law under CEO de-throttle\n'
           '    # order O-20261001-2355 sec.2): bm-a\'s thirty-fifth owned per\n'
           '    # machine-derive (engine_owner==bm-a rows 34 + candidate); wave\n'
           '    # 119 = first free number after the REGISTERED W118 row (bm-b\n'
           '    # r678 freeze 565e5b0b4) -- SINGLE STATE zero seat gap\n'
           '    # (W2..W118 all registered). Seat published=reserved\n'
           '    # MSG-2026-10-04-2323-bma-w119-seat pushed to origin 432a1eaca\n'
           '    # BEFORE this freeze, r565 law (payload = seat MSG only,\n'
           '    # deletion-set EMPTY, rev.A = only published face). ONE\n'
           '    # HUNDRED-AND-NINTH engine wave BY MACHINE-DERIVE (engine_owner\n'
           '    # rows 108 + candidate; gate leg0 machine output governs per\n'
           '    # r359 law). W1..W115 finalize LANDED (net chain head 617,548,\n'
           '    # K=250,920, bm-c r445 one-pass) + THREE in-flight upstream\n'
           '    # seats: W116 bm-b (registered bc1e82773, 6/12 shards burned,\n'
           '    # engine RAM floor gate self-paced, finalize pending) +\n'
           '    # W117 bm-a (registered c36a087ea, 12/12 shards burned,\n'
           '    # finalize rehearsal PASS r684, ARMED on W116 landing) +\n'
           '    # W118 bm-b (registered 565e5b0b4, 0/12 burned, queued behind\n'
           '    # W116 on the bm-b engine) -- finalize merge loop still derives\n'
           '    # the wave set from registry keys at run time, FAIL-CLOSED r307\n'
           '    # two-state law always on. Zero seat conflict this window\n'
           '    # (first pre-seat probe of the window found the slot vacant;\n'
           '    # cross-machine derive convergence with the bm-b r678 W118\n'
           '    # gate-tail W119+ projection re-derived here, not transcribed).\n'
           '    # A = arithmetic continuation from the registered W118 A tail:\n'
           '    # 281_004..283_003 CLEAN hops=0. B = arithmetic continuation\n'
           '    # from the registered W118 B tail: 65_450..65_649 CLEAN hops=0\n'
           '    # (zero-jump two-reading-identical face; ADMIT receipt\n'
           '    # results/_r701bma_w119_band_gate.py; live SEED_REGISTRY +\n'
           '    # probe cluster 95_000..95_003 r335 leg + cross-face probe\n'
           '    # points 95_004/95_006 r602 leg + N3-R1 used-seed band\n'
           '    # 70_000..70_005 MSG-183x r529 leg.\n'
           '    # W120+ projection (gate-derived r701): A 283_004..285_003\n'
           '    # CLEAN hops=0; B first-clean 65_650..65_849 CLEAN hops=0;\n'
           '    # next freezer must re-derive, never transcribe (r587 law).\n'
           '    # NOT a re-pick (R250: W119 bands were never assigned).\n'
           '    119: {"a": (281_004, 283_003), "b_exit": (65_450, 65_649),\n'
           '         "engine_owner": "bm-a"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[119] landed (anchor=W118 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[119] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '119: {"batch": "PERPETUAL-N1-W119"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w118", "out_name": "n1_w118_results.json",\n'
          '                            "engine_owner": "bm-b"},\n')
    NEW2 = A2 + (
        '                       119: {"batch": "PERPETUAL-N1-W119",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W119_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; ONE HUNDRED-AND-NINTH ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 108 + candidate), own-series "\n'
        '                                       "continuation per O-20261001-2355 sec.2 (first-free-number "\n'
        '                                       "law after the REGISTERED W118 row bm-b r678 freeze 565e5b0b4, "\n'
        '                                       "SINGLE STATE zero seat gap W2..W118 all registered; seat "\n'
        '                                       "published=reserved MSG-2026-10-04-2323-bma-w119-seat PUSHED to "\n'
        '                                       "origin 432a1eaca BEFORE this freeze per r565 early-visibility "\n'
        '                                       "law; pre-seat probe and freeze-window band-gate runs derive "\n'
        '                                       "identical, no fork face; payload = seat MSG only, deletion-set "\n'
        '                                       "EMPTY, rev.A = only published face), "\n'
        '                                       "engine_owner=bm-a, wave 119: "\n'
        '                                       "A = arithmetic continuation from the registered W118 A tail "\n'
        '                                       "(281_004..283_003 CLEAN hops=0) + B = arithmetic continuation "\n'
        '                                       "from the registered W118 B tail (65_450..65_649 CLEAN hops=0, "\n'
        '                                       "zero-jump two-reading-identical face, cross-machine convergence "\n'
        '                                       "with the bm-b r678 W118 gate-tail W119+ projection re-derived; "\n'
        '                                       "ADMIT receipt results/_r701bma_w119_band_gate.py; W120+ "\n'
        '                                       "projection per this window gate: A 283_004..285_003 CLEAN / "\n'
        '                                       "B first-clean 65_650..65_849 CLEAN (hops=0) for the next "\n'
        '                                       "freezer); "\n'
        '                                       "W115 finalize LANDED (net chain head 617,548, K=250,920, bm-c "\n'
        '                                       "r445 one-pass) + THREE in-flight upstream seats W116 bm-b "\n'
        '                                       "(registered bc1e82773, 6/12 shards burned, engine RAM floor "\n'
        '                                       "gate self-paced, finalize pending) + W117 bm-a (registered "\n'
        '                                       "c36a087ea, 12/12 shards burned, finalize rehearsal PASS r684 "\n'
        '                                       "and ARMED on W116 landing) + W118 bm-b (registered 565e5b0b4, "\n'
        '                                       "0/12 burned, queued behind W116 on the bm-b engine) -- "\n'
        '                                       "finalize merge loop still derives the wave set from registry "\n'
        '                                       "keys at run time, FAIL-CLOSED r307 always on)"),\n'
        '                            "a_seed_base": 281_004,        # law sec.4 W119 A: 281_004..283_003 (arithmetic continuation from the registered W118 A tail)\n'
        '                            "b_exit_seed_base": 65_450,   # law sec.4 W119 B: 65_450..65_649 (arithmetic continuation from the registered W118 B tail)\n'
        '                            "shard_subdir": "n1_w119", "out_name": "n1_w119_results.json",\n'
        '                            "engine_owner": "bm-a"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[119] landed (anchor=W118 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W119 leg --------------
LEG119 = '''
    # --- W119 materializer face (r701 bm-a freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-a's
    #     thirty-fifth owned per machine-derive (engine_owner==bm-a
    #     rows 34 + candidate); wave 119 = first free number after
    #     the REGISTERED W118 row (bm-b r678 freeze 565e5b0b4) --
    #     SINGLE STATE zero seat gap (W2..W118 all registered).
    #     Seat published=reserved MSG-2026-10-04-2323-bma-w119-seat
    #     pushed to origin 432a1eaca BEFORE this freeze, r565 law
    #     (payload = seat MSG only; deletion-set EMPTY; rev.A = only
    #     published face). ONE HUNDRED-AND-NINTH engine wave BY
    #     MACHINE-DERIVE (engine_owner rows 108 + candidate; gate
    #     leg0 machine output governs per r359 law). W1..W115
    #     finalize LANDED (net chain head 617,548, K=250,920, bm-c
    #     r445 one-pass) + THREE in-flight upstream seats W116 bm-b
    #     (registered bc1e82773, 6/12 shards burned, engine RAM
    #     floor gate self-paced, finalize pending) + W117 bm-a
    #     (registered c36a087ea, 12/12 shards burned, finalize
    #     rehearsal PASS r684, ARMED on W116 landing) + W118 bm-b
    #     (registered 565e5b0b4, 0/12 burned, queued behind W116 on
    #     the bm-b engine) -- finalize merge loop still derives the
    #     wave set from registry keys at run time, FAIL-CLOSED r307
    #     always on. ADMIT receipt results/_r701bma_w119_band_gate.py;
    #     banned gate ADMIT 0; not a re-pick (R250: W119 bands were
    #     never assigned).
    _set_wave(119)
    try:
        assert WAVE_CONFIGS[119]["a_seed_base"] == pf.N1_BANDS[119]["a"][0], \\
            "W119 A band drift vs law mirror"
        assert WAVE_CONFIGS[119]["b_exit_seed_base"] == \\
            pf.N1_BANDS[119]["b_exit"][0], "W119 B band drift vs law mirror"
        assert WAVE_CONFIGS[119].get("engine_owner") == \\
            pf.N1_BANDS[119].get("engine_owner") == "bm-a", \\
            "W119 engine_owner drift (law mirror parity)"
        w119_a = {A_SEED_BASE + j for j in range(A_N)}
        w119_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w119_a & w119_b), "W119 A/B band overlap"
        assert not (w119_a & reg_ints) and not (w119_b & reg_ints), \\
            "W119 hits SEED_REGISTRY"
        for nm, band in (("A", w119_a), ("B", w119_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W119 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W119 {nm} hits W1"
            assert not (band & probes), f"W119 {nm} hits probe seeds"
        # registered row parity (r307 pinned constants, recent estate)
        assert pf.N1_BANDS[114] == {"a": (271_004, 273_003),
                                    "b_exit": (62_201, 62_400),
                                    "engine_owner": "bm-a"}, \\
            "registered W114 row parity drift (r307; bm-a r594)"
        assert pf.N1_BANDS[115] == {"a": (273_004, 275_003),
                                    "b_exit": (62_501, 62_700),
                                    "engine_owner": "bm-c"}, \\
            "registered W115 row parity drift (r307; bm-c r445)"
        assert pf.N1_BANDS[116] == {"a": (275_004, 277_003),
                                    "b_exit": (62_701, 62_900),
                                    "engine_owner": "bm-b"}, \\
            "registered W116 row parity drift (r307; bm-b r677)"
        assert pf.N1_BANDS[117] == {"a": (277_004, 279_003),
                                    "b_exit": (65_050, 65_249),
                                    "engine_owner": "bm-a"}, \\
            "registered W117 row parity drift (r307; bm-a r683)"
        assert pf.N1_BANDS[118] == {"a": (279_004, 281_003),
                                    "b_exit": (65_250, 65_449),
                                    "engine_owner": "bm-b"}, \\
            "registered W118 row parity drift (r307; bm-b r678)"
        # prior-wave disjointness W2..W118 (single state: all
        # registered, dynamic registry derive, r511 law)
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 119):
            assert not (w119_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W119 A hits W{wprev}"
            assert not (w119_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W119 B hits W{wprev}"
        n3r1_used119 = set(range(70_000, 70_006))
        assert not (w119_a & n3r1_used119) and not (w119_b & n3r1_used119), \\
            "W119 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        assert not (w119_a & lfc_actual12) and not (w119_b & lfc_actual12), \\
            "W119 bands must clear the lfc actual draw range"
        assert not (w119_a & options_actual12) and \\
            not (w119_b & options_actual12), \\
            "W119 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W119 row, r701): A and B are both
        # arithmetic continuations from the registered W118 tails,
        # zero skips on both faces (CLEAN windows, hops=0).
        assert WAVE_CONFIGS[119]["a_seed_base"] == 281_004 == 281_003 + 1, (
            "W119 A must be the arithmetic continuation past the W118 "
            "registered A band tail")
        arith_a119 = set(range(281_004, 283_004))
        assert not (arith_a119 & reg_ints), \\
            "W119 A window must be CLEAN (arithmetic ADMIT face)"
        assert WAVE_CONFIGS[119]["b_exit_seed_base"] == 65_450 == 65_449 + 1, (
            "W119 B must be the arithmetic continuation past the W118 "
            "registered B band tail")
        arith_b119 = set(range(65_450, 65_650))
        assert not (arith_b119 & reg_ints), \\
            "W119 B window must be CLEAN (arithmetic ADMIT face, hops=0)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W119-SHARD-0",
                                          "n1w119-0of12"), "W119 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W119-SHARD-11",
                                           "n1w119-11of12")
        assert SHARD_DIR.endswith("n1_w119") and OUT.endswith(
            "n1_w119_results.json"), "W119 path drift"
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 119):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W119 shard dir collides with W{wprev}"
        # W119 finalize cumulative deps: W17..W115 outputs ALL PRESENT
        # (landed net chain head 617,548 = W115 bm-c r445 one-pass;
        # W116 bm-b + W117 bm-a + W118 bm-b registered with finalize NOT
        # landed = THREE in-flight upstream seats, honest note; the
        # finalize merge loop derives the wave set from registry keys at
        # run time and stays FAIL-CLOSED, r307 two-state law).
        for _depw in range(17, 116):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W119 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): every
        # registered wave below 119 composes; wave 15 excluded by
        # design; SINGLE STATE (W2..W118 all registered -- no
        # two-state seat disclosure needed at this freeze).
        assert sorted(w for w in WAVE_CONFIGS if w < 119) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 119)], \\
            "W119 prior-wave set must derive from registry keys (no 15; " \\
            "W2..W118 registered single state)"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W119_PREREG.md")), \\
            "W119 per-wave prereg missing (materializer requirement)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W119 materializer face' in t2b:
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
            + LEG119
            + '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n')
    t2b = rep(t2b, A3, NEW3, eol2b, 'n1-leg119')
    save(FP2, t2b)
    print('edit3 selftest W119 leg landed (insert before T-141 selftest lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment ----------------------
t2c, eol2c = load(FP2)
if '+ W119 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('law sec.4 W118 row, r678 bm-b] "\n'
          '          "+ T-141 s2 ')
    SEG119 = ('law sec.4 W118 row, r678 bm-b] "\n'
              '          "+ W119 materializer face [same guard set, dep=W17..W115 "\n'
              '"outputs ALL PRESENT (landed net chain head 617,548 = W115 "\n'
              '"bm-c r445 one-pass, K=250,920; THREE in-flight upstream seats "\n'
              '"W116 bm-b registered bc1e82773 6-of-12 shards burned RAM-floor-"\n'
              '"gated + W117 bm-a registered c36a087ea 12/12 burned finalize-"\n'
              '"rehearsal-ARMED + W118 bm-b registered 565e5b0b4 0/12 queued "\n'
              '"-- finalize merge loop still derives the wave set from registry "\n'
              '"keys at run time, FAIL-CLOSED r307 always on), ONE HUNDRED-AND-"\n'
              '"NINTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 108 "\n'
              '"+ candidate) bm-a\'s thirty-fifth owned claim per machine-derive "\n'
              '"(engine_owner==bm-a rows 34 + candidate), engine_owner=bm-a "\n'
              '"per engine de-throttle law O-20261001-2355 sec.2 own-continuous-"\n'
              '"series (wave 119 = first FREE number after the REGISTERED W118 "\n'
              '"row bm-b r678 freeze 565e5b0b4, SINGLE STATE zero seat gap "\n'
              '"W2..W118 all registered; zero seat conflict this window, "\n'
              '"cross-machine derive convergence with the bm-b r678 W118 "\n'
              '"gate-tail W119+ projection re-derived; seat published=reserved "\n'
              '"MSG-2026-10-04-2323-bma-w119-seat pushed to origin 432a1eaca "\n'
              '"BEFORE this freeze, r565 law; payload = seat MSG only "\n'
              '"deletion-set EMPTY, rev.A = only published face), "\n'
              '"A=arithmetic continuation from the registered W118 A tail "\n'
              '"(281_004..283_003 CLEAN hops=0) + B=arithmetic continuation "\n'
              '"from the registered W118 B tail (65_450..65_649 CLEAN hops=0, "\n'
              '"zero-jump two-reading-identical face, cross-machine convergence "\n'
              '"with the bm-b r678 W118 gate-tail W119+ projection re-derived; "\n'
              '"ADMIT receipt results/_r701bma_w119_band_gate.py; W120+ projection "\n'
              '"per this window gate: A 283_004..285_003 CLEAN / B first-clean "\n'
              '"65_650..65_849 CLEAN (hops=0) disclosed for the next freezer; "\n'
              '"not a free pick -- R250), "\n'
              '"law sec.4 W119 row, r701 bm-a] "\n'
              '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG119, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W119 segment landed (insert after W118 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W119 row ---------------------
ROW119 = f"""
- N1 波119（r701 bm-a 冻·prereg 时展行）：**第一百零九枚引擎波·bm-a 第三十五枚自有波〔机面 derive：engine_owner 行 108+本候选／engine_owner==bm-a 行 34+本候选·r359 律计数面以 gate 机输出为准〕**·engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 同 W10-W118 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-a 实例=**tick 架构**——冻结编辑落工作树后下一 tick 新进程读活树自见 W119 行并点火〔r535 律·r325/r330 kill-restart 序免做〕·点火验证唯一证据=产物增长面 r325 律·2 tick 窗·**RAM floor gate 机器纪律在位（席位窗实况 avail 47.39GB load 52%）=自点火当 RAM 清**】·【never-dry 供给律常设步·**波号 119=注册表 W118 行后首个自由号·单态零席位空档**（W114=bm-a r594 freeze ddacf2616+W115=bm-c r445 解停 freeze f6b521153+W116=bm-b r677 freeze bc1e82773+W117=bm-a r683 freeze c36a087ea+W118=bm-b r678 freeze 565e5b0b4 均已注册·表尾=W118 行）·**席位公示=MSG-2026-10-04-2323-bma-w119-seat**〔published=reserved r518-① 律·先于冻结 commit 推 origin 432a1eaca=r565 早可见性律·payload=席位 MSG 单件 deletion-set 空·rev.A=唯一发布面·席位内容逐字节=本工作树原稿（构造性恒等）〕】·**本窗零席位冲突实录**：本机 pre-seat probe（_r701bma_w119_probe.py）首探即净空（r374 inbox+processed 双目录零外机 W119 席位）·双窗 derive 恒等（pre-seat probe+冻结窗 band gate 逐位 ADMIT）·与 bm-b r678 W118 闸尾 W119+ 投影逐位收敛=双机交叉验证（非转抄 r587 律）。本窗实况=**W115 finalize 已落账（净链头 617,548·K=250,920 合并池·bm-c r445 W115 one-pass）+三席在飞上游（W116 bm-b 已注册 bc1e82773·6/12 分片烧毕·RAM floor gate 自步进·finalize 未落+W117 bm-a 已注册 c36a087ea·12/12 烧毕·finalize rehearsal PASS r684 armed 等 W116 落账+W118 bm-b 已注册 565e5b0b4·0/12 排队 bm-b 引擎 W116 之后=本波 finalize 链序前置三空档·跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**·**带位（r535 机闸 derive 律·活注册表机证·单态收敛门·ADMIT 回执=results/_r701bma_w119_band_gate.py rc0 实跑·pre-seat probe _r701bma_w119_probe.py 先跑·双窗 derive 恒等·hops A=0/B=0）**：**A-ext seed=281_004..283_003**（==W118 行 A 尾 281_003+1 起算术续带·步长 2_000·**CLEAN 零拒绝点**）；**B-ext exit seed=65_450..65_649**（==W118 行 B 尾 65_449+1 起算术续带·步长 200·**CLEAN 零拒绝点·两读法恒同解零跳位·与 bm-b r678 W118 闸尾 W119+ 投影逐位收敛=双机交叉验证**）。R250：W119 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W119 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W119_PREREG.md（冻结件·锚=W115 finalize 实测值〔merged mu {_w115_mu}·K=250,920·K-lift {_w115_klift}·A-p95 {_w115_p95}·se_mu {_w115_se_mu}〕）·**W120+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 283_004..285_003 **CLEAN**（hops=0）；B 首净窗 **65_650..65_849** **CLEAN**（hops=0）（r701 冻结窗 gate 回执尾行·与本席位 MSG W120+ 投影披露交叉验证一致）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce2119\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW119.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W119 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    119: {"a": (281_004') == 1, 'FIX-B FAIL: W119 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W119"') == 1, 'FIX-B FAIL: W119 config not exactly once'
for w in range(58, 119):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W119 materializer face') == 2, \
    'FIX-B FAIL: W119 leg+summary must be exactly 2'
for w in range(48, 119):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce2119\uff08') == 1, 'FIX-B FAIL: canon W119 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W119 added per face')

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
print('FREEZE_EDITS_OK 119')
