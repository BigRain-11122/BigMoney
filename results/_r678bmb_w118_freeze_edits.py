# -*- coding: utf-8 -*-
"""r678 bm-b W118 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening.

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED rows (W113 bm-c +
  W114 bm-a + W115 bm-c + W116 bm-b + W117 bm-a); every registered row
  signature survives exactly; exactly one new W118 signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.
AST gate (r580/r581 lesson): post-edit ast.parse on both py faces.

W118 = ONE HUNDRED-AND-EIGHTH engine wave BY MACHINE-DERIVE (engine_owner
rows 107 + candidate; gate leg0 machine output governs per r359 law),
bm-b's FORTIETH owned (engine_owner==bm-b rows 39 + candidate).
First free number after the REGISTERED W117 row (bm-a r683 freeze
c36a087ea) -- SINGLE STATE zero seat gap (W2..W117 all registered).
Seat published=reserved MSG-2026-10-04-1532-bmb-w118-seat pushed to origin
24960f5e1 BEFORE this freeze (r565 early-visibility law; payload = seat
MSG + pre-seat probe + W117 yield record + D-19 receipts, deletion-set
EMPTY, rev.A = only published face).
Bands:
  A 279_004..281_003 (W117 A tail 279_003 + 1, stride 2_000) hops=0 CLEAN.
  B 65_250..65_449   (W117 B tail 65_249 + 1, stride 200) hops=0 CLEAN
                     (zero-jump two-reading-identical face; cross-machine
                     convergence with the bm-a r683 W117 seat W118+
                     projection re-derived here, not transcribed).
  ADMIT receipt results/_r678bmb_w118_band_gate.py rc0; banned gate ADMIT 0.
W115 finalize LANDED (net chain head 617,548, K=250,920 = bm-c r445
one-pass) + TWO in-flight upstream seats: W116 bm-b (registered bc1e82773,
queue 12/12 materialized, ignition held by engine RAM floor gate,
finalize pending) + W117 bm-a (registered c36a087ea, burn pending) --
finalize merge loop still derives the wave set from registry keys at run
time, FAIL-CLOSED r307 two-state law always on.
Same-window yield record: W117 pre-seat probe caught bm-a's published
W117 seat (origin-first) -> bm-b yielded W117 per r518-1 + fleet sec.4;
W118 = re-derived first-free-number after the landed W117 registration.
W119+ projection (gate-derived this window): A 281_004..283_003 CLEAN
hops=0 / B 65_450..65_649 CLEAN hops=0 (next freezer must re-derive,
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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 118))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 118)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 118)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[118] ---------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '118: {"a": (279_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    117: {"a": (277_004, 279_003), "b_exit": (65_050, 65_249),\n'
          '         "engine_owner": "bm-a"},\n'
          '}\n')
    NEW = ('    117: {"a": (277_004, 279_003), "b_exit": (65_050, 65_249),\n'
           '         "engine_owner": "bm-a"},\n'
           '    # W118 (r678 bm-b freeze, own-series law under CEO de-throttle\n'
           '    # order O-20261001-2355 sec.2): bm-b\'s fortieth owned per\n'
           '    # machine-derive (engine_owner==bm-b rows 39 + candidate); wave\n'
           '    # 118 = first free number after the REGISTERED W117 row (bm-a\n'
           '    # r683 freeze c36a087ea) -- SINGLE STATE zero seat gap\n'
           '    # (W2..W117 all registered). Seat published=reserved\n'
           '    # MSG-2026-10-04-1532-bmb-w118-seat pushed to origin 24960f5e1\n'
           '    # BEFORE this freeze, r565 law (payload = seat MSG + pre-seat\n'
           '    # probe + W117 yield record + D-19 receipts; deletion-set EMPTY;\n'
           '    # rev.A = only published face). ONE HUNDRED-AND-EIGHTH engine\n'
           '    # wave BY MACHINE-DERIVE (engine_owner rows 107 + candidate;\n'
           '    # gate leg0 machine output governs per r359 law). W1..W115\n'
           '    # finalize LANDED (net chain head 617,548, K=250,920, bm-c r445\n'
           '    # one-pass) + TWO in-flight upstream seats: W116 bm-b\n'
           '    # (registered bc1e82773, queue 12/12 materialized, ignition\n'
           '    # held by engine RAM floor gate, finalize pending) + W117 bm-a\n'
           '    # (registered c36a087ea, burn pending) -- finalize merge loop\n'
           '    # still derives the wave set from registry keys at run time,\n'
           '    # FAIL-CLOSED r307 two-state law always on.\n'
           '    # Same-window yield record: W117 pre-seat probe caught bm-a\'s\n'
           '    # published W117 seat (origin-first) -> bm-b yielded W117 per\n'
           '    # r518-1 published=reserved + fleet sec.4 commit-time ordering;\n'
           '    # cross-machine derive convergence (A 277_004..279_003 /\n'
           '    # B 65_050..65_249 identical) recorded\n'
           '    # results/_r678bmb_w117_probe_receipt.txt.\n'
           '    # A = arithmetic continuation from the registered W117 A tail:\n'
           '    # 279_004..281_003 CLEAN hops=0. B = arithmetic continuation\n'
           '    # from the registered W117 B tail: 65_250..65_449 CLEAN hops=0\n'
           '    # (zero-jump two-reading-identical face; cross-machine\n'
           '    # convergence with the bm-a r683 W117 seat W118+ projection\n'
           '    # re-derived here, not transcribed; ADMIT receipt\n'
           '    # results/_r678bmb_w118_band_gate.py; live SEED_REGISTRY +\n'
           '    # probe cluster 95_000..95_003 r335 leg + cross-face probe points\n'
           '    # 95_004/95_006 r602 leg + N3-R1 used-seed band 70_000..70_005\n'
           '    # MSG-183x r529 leg.\n'
           '    # W119+ projection (gate-derived r678): A 281_004..283_003\n'
           '    # CLEAN hops=0; B first-clean 65_450..65_649 CLEAN hops=0;\n'
           '    # next freezer must re-derive, never transcribe (r587 law).\n'
           '    # NOT a re-pick (R250: W118 bands were never assigned).\n'
           '    118: {"a": (279_004, 281_003), "b_exit": (65_250, 65_449),\n'
           '         "engine_owner": "bm-b"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[118] landed (anchor=W117 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[118] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '118: {"batch": "PERPETUAL-N1-W118"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w117", "out_name": "n1_w117_results.json",\n'
          '                            "engine_owner": "bm-a"},\n')
    NEW2 = A2 + (
        '                       118: {"batch": "PERPETUAL-N1-W118",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W118_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; ONE HUNDRED-AND-EIGHTH ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 107 + candidate), own-series "\n'
        '                                       "continuation per O-20261001-2355 sec.2 (first-free-number "\n'
        '                                       "law after the REGISTERED W117 row bm-a r683 freeze c36a087ea, "\n'
        '                                       "SINGLE STATE zero seat gap W2..W117 all registered; seat "\n'
        '                                       "published=reserved MSG-2026-10-04-1532-bmb-w118-seat PUSHED to "\n'
        '                                       "origin 24960f5e1 BEFORE this freeze per r565 early-visibility "\n'
        '                                       "law; pre-seat probe and freeze-window band-gate runs derive "\n'
        '                                       "identical, no fork face; payload = seat MSG + pre-seat probe + "\n'
        '                                       "W117 yield record + D-19 receipts, deletion-set EMPTY, rev.A = "\n'
        '                                       "only published face), "\n'
        '                                       "engine_owner=bm-b, wave 118: "\n'
        '                                       "A = arithmetic continuation from the registered W117 A tail "\n'
        '                                       "(279_004..281_003 CLEAN hops=0) + B = arithmetic continuation "\n'
        '                                       "from the registered W117 B tail (65_250..65_449 CLEAN hops=0, "\n'
        '                                       "zero-jump two-reading-identical face, cross-machine convergence "\n'
        '                                       "with the bm-a r683 W117 seat W118+ projection re-derived; ADMIT "\n'
        '                                       "receipt results/_r678bmb_w118_band_gate.py; W119+ projection per "\n'
        '                                       "this window gate: A 281_004..283_003 CLEAN / B first-clean "\n'
        '                                       "65_450..65_649 CLEAN (hops=0) for the next freezer); "\n'
        '                                       "W115 finalize LANDED (net chain head 617,548, K=250,920, bm-c "\n'
        '                                       "r445 one-pass) + TWO in-flight upstream seats W116 bm-b "\n'
        '                                       "(registered bc1e82773, queue 12/12 materialized, ignition "\n'
        '                                       "held by engine RAM floor gate, finalize pending) + W117 bm-a "\n'
        '                                       "(registered c36a087ea, burn pending) -- finalize merge loop still "\n'
        '                                       "derives the wave set from registry keys at run time, "\n'
        '                                       "FAIL-CLOSED r307 always on)"),\n'
        '                            "a_seed_base": 279_004,        # law sec.4 W118 A: 279_004..281_003 (arithmetic continuation from the registered W117 A tail)\n'
        '                            "b_exit_seed_base": 65_250,   # law sec.4 W118 B: 65_250..65_449 (arithmetic continuation from the registered W117 B tail)\n'
        '                            "shard_subdir": "n1_w118", "out_name": "n1_w118_results.json",\n'
        '                            "engine_owner": "bm-b"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[118] landed (anchor=W117 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W118 leg --------------
LEG118 = '''
    # --- W118 materializer face (r678 bm-b freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-b's
    #     fortieth owned per machine-derive (engine_owner==bm-b
    #     rows 39 + candidate); wave 118 = first free number after
    #     the REGISTERED W117 row (bm-a r683 freeze c36a087ea) --
    #     SINGLE STATE zero seat gap (W2..W117 all registered).
    #     Seat published=reserved MSG-2026-10-04-1532-bmb-w118-seat
    #     pushed to origin 24960f5e1 BEFORE this freeze, r565 law
    #     (payload = seat MSG + pre-seat probe + W117 yield record
    #     + D-19 receipts; deletion-set EMPTY; rev.A = only
    #     published face). ONE HUNDRED-AND-EIGHTH engine wave BY
    #     MACHINE-DERIVE (engine_owner rows 107 + candidate; gate
    #     leg0 machine output governs per r359 law). W1..W115
    #     finalize LANDED (net chain head 617,548, K=250,920, bm-c
    #     r445 one-pass) + TWO in-flight upstream seats W116 bm-b
    #     (registered bc1e82773, queue 12/12 materialized, ignition
    #     held by engine RAM floor gate, finalize pending) + W117
    #     bm-a (registered c36a087ea, burn pending) -- finalize
    #     merge loop still derives the wave set from registry keys
    #     at run time, FAIL-CLOSED r307 always on. ADMIT receipt
    #     results/_r678bmb_w118_band_gate.py; banned gate ADMIT 0;
    #     not a re-pick (R250: W118 bands were never assigned).
    _set_wave(118)
    try:
        assert WAVE_CONFIGS[118]["a_seed_base"] == pf.N1_BANDS[118]["a"][0], \\
            "W118 A band drift vs law mirror"
        assert WAVE_CONFIGS[118]["b_exit_seed_base"] == \\
            pf.N1_BANDS[118]["b_exit"][0], "W118 B band drift vs law mirror"
        assert WAVE_CONFIGS[118].get("engine_owner") == \\
            pf.N1_BANDS[118].get("engine_owner") == "bm-b", \\
            "W118 engine_owner drift (law mirror parity)"
        w118_a = {A_SEED_BASE + j for j in range(A_N)}
        w118_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w118_a & w118_b), "W118 A/B band overlap"
        assert not (w118_a & reg_ints) and not (w118_b & reg_ints), \\
            "W118 hits SEED_REGISTRY"
        for nm, band in (("A", w118_a), ("B", w118_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W118 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W118 {nm} hits W1"
            assert not (band & probes), f"W118 {nm} hits probe seeds"
        # registered row parity (r307 pinned constants, recent estate)
        assert pf.N1_BANDS[113] == {"a": (269_004, 271_003),
                                    "b_exit": (62_001, 62_200),
                                    "engine_owner": "bm-c"}, \\
            "registered W113 row parity drift (r307; bm-c r382)"
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
        # prior-wave disjointness W2..W117 (single state: all
        # registered, dynamic registry derive, r511 law)
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 118):
            assert not (w118_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W118 A hits W{wprev}"
            assert not (w118_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W118 B hits W{wprev}"
        n3r1_used118 = set(range(70_000, 70_006))
        assert not (w118_a & n3r1_used118) and not (w118_b & n3r1_used118), \\
            "W118 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        assert not (w118_a & lfc_actual12) and not (w118_b & lfc_actual12), \\
            "W118 bands must clear the lfc actual draw range"
        assert not (w118_a & options_actual12) and \\
            not (w118_b & options_actual12), \\
            "W118 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W118 row, r678): A and B are both
        # arithmetic continuations from the registered W117 tails,
        # zero skips on both faces (CLEAN windows, hops=0).
        assert WAVE_CONFIGS[118]["a_seed_base"] == 279_004 == 279_003 + 1, (
            "W118 A must be the arithmetic continuation past the W117 "
            "registered A band tail")
        arith_a118 = set(range(279_004, 281_004))
        assert not (arith_a118 & reg_ints), \\
            "W118 A window must be CLEAN (arithmetic ADMIT face)"
        assert WAVE_CONFIGS[118]["b_exit_seed_base"] == 65_250 == 65_249 + 1, (
            "W118 B must be the arithmetic continuation past the W117 "
            "registered B band tail")
        arith_b118 = set(range(65_250, 65_450))
        assert not (arith_b118 & reg_ints), \\
            "W118 B window must be CLEAN (arithmetic ADMIT face, hops=0)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W118-SHARD-0",
                                          "n1w118-0of12"), "W118 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W118-SHARD-11",
                                           "n1w118-11of12")
        assert SHARD_DIR.endswith("n1_w118") and OUT.endswith(
            "n1_w118_results.json"), "W118 path drift"
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 118):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W118 shard dir collides with W{wprev}"
        # W118 finalize cumulative deps: W17..W115 outputs ALL PRESENT
        # (landed net chain head 617,548 = W115 bm-c r445 one-pass;
        # W116 bm-b + W117 bm-a registered with finalize NOT landed =
        # TWO in-flight upstream seats, honest note; the finalize merge
        # loop derives the wave set from registry keys at run time and
        # stays FAIL-CLOSED, r307 two-state law).
        for _depw in range(17, 116):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W118 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): every
        # registered wave below 118 composes; wave 15 excluded by
        # design; SINGLE STATE (W2..W117 all registered -- no
        # two-state seat disclosure needed at this freeze).
        assert sorted(w for w in WAVE_CONFIGS if w < 118) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 118)], \\
            "W118 prior-wave set must derive from registry keys (no 15; " \\
            "W2..W117 registered single state)"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W118_PREREG.md")), \\
            "W118 per-wave prereg missing (materializer requirement)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W118 materializer face' in t2b:
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
            + LEG118
            + '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n')
    t2b = rep(t2b, A3, NEW3, eol2b, 'n1-leg118')
    save(FP2, t2b)
    print('edit3 selftest W118 leg landed (insert before T-141 selftest lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment ----------------------
t2c, eol2c = load(FP2)
if '+ W118 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('law sec.4 W117 row, r683 bm-a] "\n'
          '          "+ T-141 s2 ')
    SEG118 = ('law sec.4 W117 row, r683 bm-a] "\n'
              '          "+ W118 materializer face [same guard set, dep=W17..W115 "\n'
              '"outputs ALL PRESENT (landed net chain head 617,548 = W115 "\n'
              '"bm-c r445 one-pass, K=250,920; TWO in-flight upstream seats "\n'
              '"W116 bm-b registered bc1e82773 queue-materialized RAM-floor-"\n'
              '"gated + W117 bm-a registered c36a087ea burn-pending -- finalize "\n'
              '"merge loop still derives the wave set from registry keys at "\n'
              '"run time, FAIL-CLOSED r307 always on), ONE HUNDRED-AND-EIGHTH "\n'
              '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 107 + "\n'
              '"candidate) bm-b\'s fortieth owned claim per machine-derive "\n'
              '"(engine_owner==bm-b rows 39 + candidate), engine_owner=bm-b "\n'
              '"per engine de-throttle law O-20261001-2355 sec.2 own-continuous-"\n'
              '"series (wave 118 = first FREE number after the REGISTERED W117 "\n'
              '"row bm-a r683 freeze c36a087ea, SINGLE STATE zero seat gap "\n'
              '"W2..W117 all registered; same-window yield record: bm-b W117 "\n'
              '"pre-seat probe caught bm-a\'s published W117 seat -> yielded "\n'
              '"per r518-1 published=reserved + fleet sec.4 commit-time "\n'
              '"ordering, cross-machine derive convergence recorded; seat "\n'
              '"published=reserved MSG-2026-10-04-1532-bmb-w118-seat pushed to "\n'
              '"origin 24960f5e1 BEFORE this freeze, r565 law; payload = seat "\n'
              '"MSG + pre-seat probe + W117 yield record + D-19 receipts "\n'
              '"deletion-set EMPTY, rev.A = only published face), "\n'
              '"A=arithmetic continuation from the registered W117 A tail "\n'
              '"(279_004..281_003 CLEAN hops=0) + B=arithmetic continuation "\n'
              '"from the registered W117 B tail (65_250..65_449 CLEAN hops=0, "\n'
              '"zero-jump two-reading-identical face, cross-machine convergence "\n'
              '"with the bm-a r683 W117 seat W118+ projection re-derived; ADMIT "\n'
              '"receipt results/_r678bmb_w118_band_gate.py; W119+ projection "\n'
              '"per this window gate: A 281_004..283_003 CLEAN / B first-clean "\n'
              '"65_450..65_649 CLEAN (hops=0) disclosed for the next freezer; "\n'
              '"not a free pick -- R250), "\n'
              '"law sec.4 W118 row, r678 bm-b] "\n'
              '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG118, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W118 segment landed (insert after W117 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W118 row ---------------------
ROW118 = f"""
- N1 波118（r678 bm-b 冻·prereg 时展行）：**第一百零八枚引擎波·bm-b 第四十枚自有波〔机面 derive：engine_owner 行 107+本候选／engine_owner==bm-b 行 39+本候选·r359 律计数面以 gate 机输出为准〕**·engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W117 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-b 实例=**tick 架构**——冻结编辑落工作树后下一 tick 新进程读活树自见 W118 行并点火〔r535 律·r325/r330 kill-restart 序免做〕·点火验证唯一证据=产物增长面 r325 律·2 tick 窗·**RAM floor gate 3.4-4.0GB 机器纪律在位=自点火当 RAM 清**】·【never-dry 供给律常设步·**波号 118=注册表 W117 行后首个自由号·单态零席位空档**（W113=bm-c r382 freeze eeb062290+W114=bm-a r594 freeze ddacf2616+W115=bm-c r445 解停 freeze f6b521153+W116=bm-b r677 freeze bc1e82773+W117=bm-a r683 freeze c36a087ea 均已注册·表尾=W117 行）·**席位公示=MSG-2026-10-04-1532-bmb-w118-seat**〔published=reserved r518-① 律·先于冻结 commit 推 origin 24960f5e1=r565 早可见性律·payload=席位 MSG+pre-seat probe+W117 让路记录+D-19 回执件 deletion-set 空·rev.A=唯一发布面〕】·**同窗让路实录**：本机 W117 pre-seat probe 撞 bm-a 已发布 W117 席位（15:35 origin-first）→按 r518-①+fleet §4 commit 时序让路 W117·转 W118=表尾后新首个自由号；双机带位 derive 收敛实证（A 277_004..279_003/B 65_050..65_249 逐位恒等）留档 _r678bmb_w117_probe_receipt.txt。本窗实况=**W115 finalize 已落账（净链头 617,548·K=250,920 合并池·bm-c r445 W115 one-pass）+两席在飞上游（W116 bm-b 已注册 bc1e82773·queue 12/12 materialized·RAM floor gate 点火待 RAM·finalize 未落+W117 bm-a 已注册 c36a087ea·burn pending·finalize 未落=本波 finalize 链序前置两空档·跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**·**带位（r535 机闸 derive 律·活注册表机证·单态收敛门·ADMIT 回执=results/_r678bmb_w118_band_gate.py rc0 实跑·pre-seat probe _r678bmb_w118_probe.py 先跑·双窗 derive 恒等·hops A=0/B=0）**：**A-ext seed=279_004..281_003**（==W117 行 A 尾 279_003+1 起算术续带·步长 2_000·**CLEAN 零拒绝点**）；**B-ext exit seed=65_250..65_449**（==W117 行 B 尾 65_249+1 起算术续带·步长 200·**CLEAN 零拒绝点·两读法恒同解零跳位·与 bm-a r683 W117 席位 W118+ 投影逐位收敛=双机交叉验证**）。R250：W118 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W118 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W118_PREREG.md（冻结件·锚=W115 finalize 实测值〔merged mu {_w115_mu}·K=250,920·K-lift {_w115_klift}·A-p95 {_w115_p95}·se_mu {_w115_se_mu}〕）·**W119+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 281_004..283_003 **CLEAN**（hops=0）；B 首净窗 **65_450..65_649** **CLEAN**（hops=0）（r678 冻结窗 gate 回执尾行·与本席位 MSG W119+ 投影披露交叉验证一致）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce2118\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW118.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W118 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    118: {"a": (279_004') == 1, 'FIX-B FAIL: W118 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W118"') == 1, 'FIX-B FAIL: W118 config not exactly once'
for w in range(58, 118):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W118 materializer face') == 2, \
    'FIX-B FAIL: W118 leg+summary must be exactly 2'
for w in range(48, 118):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce2118\uff08') == 1, 'FIX-B FAIL: canon W118 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W118 added per face')

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
print('FREEZE_EDITS_OK 118')
