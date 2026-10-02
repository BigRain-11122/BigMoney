# -*- coding: utf-8 -*-
"""r384 bm-c W115 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening.

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED rows (W110 bm-a +
  W111 bm-b + W112 bm-a + W113 bm-c + W114 bm-a); every registered row
  signature survives exactly; exactly one new W115 signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.
AST gate (r580/r581 lesson): post-edit ast.parse on both py faces.

W115 = ONE HUNDRED-AND-FIFTH engine wave BY MACHINE-DERIVE (engine_owner
rows 104 + candidate; gate leg0 machine output governs per r359 law),
bm-c's THIRTY-FOURTH owned (engine_owner==bm-c rows 33 + candidate).
First free number after the REGISTERED W114 row (bm-a r594 freeze
ddacf2616) -- SINGLE STATE zero seat gap (W2..W114 all registered).
Seat published=reserved MSG-20261002-2130-bmc-w115-seat pushed to origin
ac241dd32 BEFORE this freeze (r565 early-visibility law; payload = seat
MSG + pre-seat probe, deletion-set EMPTY, rev.A = only published face).
Bands:
  A 273_004..275_003 (W114 A tail 273_003 + 1, stride 2_000) hops=0 CLEAN.
  B 62_501..62_700   (arithmetic 62_401..62_600 REFUSED in-band at
                      SEED_REGISTRY grid_sleeve_p1=62_500 mid-window ->
                      pinned D-20261002-05 past-hit restart) hops=1 CLEAN.
  ADMIT receipt results/_r384bmc_w115_band_gate.py rc0; banned gate ADMIT 0.
W114 finalize LANDED (chain head 615,348, K=248,720 = bm-a r594 one-pass).
ZERO in-flight upstream seats (W2..W114 all landed) -- finalize merge loop
still derives the wave set from registry keys at run time, FAIL-CLOSED
r307 two-state law always on.
W116+ projection (gate-derived this window): A 275_004..277_003 CLEAN
hops=0 / B 62_701..62_900 CLEAN hops=0 (next freezer must re-derive,
never transcribe; r587 law).
"""
import subprocess, sys, os, ast, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# machine-derived W114 anchor values for the canon row (read, never copied)
_d114 = json.load(open(os.path.join(REPO, "results/perpetual_faces/n1_w114_results.json"), encoding="utf-8"))
_npc = _d114["null_pool_cumulative"]
_sk = _d114["skill_line_v2_k_lift"]
_K = _npc["merged"]["n_values"]
assert _K == 248720, f"W114 K drift {_K}"
_se_key = f"se_mu_at_k{_K}"
_w114_se_mu = repr(_npc[_se_key])
_w114_klift_raw = _sk["line_delta_k_lift"]
_w114_klift = ("+" + repr(_w114_klift_raw) if _w114_klift_raw > 0
               else ("\u2212" + repr(abs(_w114_klift_raw)) if _w114_klift_raw < 0
                     else "0.0000"))
_w114_mu = repr(_npc["merged"]["mu"]).replace("-", "\u2212")
_w114_p95 = repr(_d114["families"]["A_random_engine_exit"]["full_sharpe_p95"])

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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 115))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 115)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 115)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[115] ---------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '115: {"a": (273_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    114: {"a": (271_004, 273_003), "b_exit": (62_201, 62_400),\n'
          '         "engine_owner": "bm-a"},\n'
          '}\n')
    NEW = ('    114: {"a": (271_004, 273_003), "b_exit": (62_201, 62_400),\n'
           '         "engine_owner": "bm-a"},\n'
           '    # ONE HUNDRED-AND-FIFTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r384 bm-c\n'
           '    # freeze): engine_owner rows 104 + candidate; bm-c\'s thirty-\n'
           '    # fourth owned per machine-derive (engine_owner==bm-c rows 33 +\n'
           '    # candidate). Wave 115 = first free number after the REGISTERED\n'
           '    # W114 row (bm-a r594 freeze ddacf2616) -- SINGLE STATE zero seat\n'
           '    # gap (W2..W114 all registered). Seat published=reserved\n'
           '    # MSG-20261002-2130-bmc-w115-seat pushed to origin ac241dd32\n'
           '    # BEFORE this freeze per r565 early-visibility law (payload = seat\n'
           '    # MSG + pre-seat probe, deletion-set EMPTY; rev.A = only published\n'
           '    # face).\n'
           '    # W114 finalize LANDED (chain head 615,348, K=248,720 = bm-a r594\n'
           '    # one-pass). ZERO in-flight upstream seats (W2..W114 all landed) --\n'
           '    # finalize merge loop still derives the wave set from registry\n'
           '    # keys at run time, FAIL-CLOSED r307 two-state law always on.\n'
           '    # A = arithmetic continuation from the registered W114 A tail:\n'
           '    # 273_004..275_003 CLEAN hops=0. B = pinned D-20261002-05 past-hit\n'
           '    # restart: arithmetic 62_401..62_600 refused in-band at\n'
           '    # SEED_REGISTRY grid_sleeve_p1=62_500 (mid-window hit) ->\n'
           '    # restart 62_501..62_700 CLEAN hops=1 (window-step-chain reading\n'
           '    # 62_601..62_800 BANNED per W68-B negative anchor; ADMIT receipt\n'
           '    # results/_r384bmc_w115_band_gate.py rc0; live SEED_REGISTRY +\n'
           '    # probe cluster 95_000..95_003 r335 leg + N3-R1 used-seed band\n'
           '    # 70_000..70_005 MSG-183x r529 leg.\n'
           '    # W116+ projection (gate-derived r384): A 275_004..277_003 CLEAN\n'
           '    # hops=0; B 62_701..62_900 CLEAN hops=0 (next freezer must\n'
           '    # re-derive, never transcribe; r587 law).\n'
           '    # NOT a re-pick (R250: W115 bands were never assigned).\n'
           '    115: {"a": (273_004, 275_003), "b_exit": (62_501, 62_700),\n'
           '         "engine_owner": "bm-c"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[115] landed (anchor=W114 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[115] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '115: {"batch": "PERPETUAL-N1-W115"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w114", "out_name": "n1_w114_results.json",\n'
          '                            "engine_owner": "bm-a"},\n')
    NEW2 = A2 + (
        '                       115: {"batch": "PERPETUAL-N1-W115",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W115_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; ONE HUNDRED-AND-FIFTH ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 104 + candidate), own-series "\n'
        '                                       "continuation per O-20261001-2355 sec.2 (first-free-number "\n'
        '                                       "law after the REGISTERED W114 row bm-a r594 freeze ddacf2616, "\n'
        '                                       "SINGLE STATE zero seat gap W2..W114 all registered; seat "\n'
        '                                       "published=reserved MSG-20261002-2130-bmc-w115-seat PUSHED to "\n'
        '                                       "origin ac241dd32 BEFORE this freeze per r565 early-visibility "\n'
        '                                       "law; pre-seat probe and freeze-window band-gate runs derive "\n'
        '                                       "identical, no fork face; payload = seat MSG + pre-seat probe, "\n'
        '                                       "deletion-set EMPTY, rev.A = only published face), "\n'
        '                                       "engine_owner=bm-c, wave 115: "\n'
        '                                       "A = arithmetic continuation from the registered W114 A tail "\n'
        '                                       "(273_004..275_003 CLEAN hops=0) + B = pinned D-20261002-05 "\n'
        '                                       "past-hit restart (arithmetic 62_401..62_600 refused in-band at "\n'
        '                                       "SEED_REGISTRY grid_sleeve_p1=62_500 mid-window -> restart "\n'
        '                                       "62_501..62_700 CLEAN hops=1; ADMIT receipt "\n'
        '                                       "results/_r384bmc_w115_band_gate.py; W116+ projection per this "\n'
        '                                       "window gate: A 275_004..277_003 CLEAN / B 62_701..62_900 "\n'
        '                                       "CLEAN for the next freezer); W114 finalize LANDED (chain "\n'
        '                                       "head 615,348, K=248,720, bm-a r594 one-pass) + ZERO "\n'
        '                                       "in-flight upstream seats -- finalize merge loop still "\n'
        '                                       "derives the wave set from registry keys at run time, "\n'
        '                                       "FAIL-CLOSED r307 always on)"),\n'
        '                            "a_seed_base": 273_004,        # law sec.4 W115 A: 273_004..275_003 (arithmetic continuation from the registered W114 A tail)\n'
        '                            "b_exit_seed_base": 62_501,   # law sec.4 W115 B: 62_501..62_700 (pinned D-20261002-05 past-hit restart over SEED_REGISTRY grid_sleeve_p1=62_500)\n'
        '                            "shard_subdir": "n1_w115", "out_name": "n1_w115_results.json",\n'
        '                            "engine_owner": "bm-c"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[115] landed (anchor=W114 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W115 leg --------------
LEG115 = '''
    # --- W115 materializer face (r384 bm-c freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-c's
    #     thirty-fourth owned per machine-derive (engine_owner==bm-c
    #     rows 33 + candidate); wave 115 = first free number after
    #     the REGISTERED W114 row (bm-a r594 freeze ddacf2616) --
    #     SINGLE STATE zero seat gap (W2..W114 all registered).
    #     Seat published=reserved MSG-20261002-2130-bmc-w115-seat
    #     pushed to origin ac241dd32 BEFORE this freeze, r565 law
    #     (payload = seat MSG + pre-seat probe; deletion-set EMPTY;
    #     rev.A = only published face). ONE HUNDRED-AND-FIFTH
    #     engine wave BY MACHINE-DERIVE (engine_owner rows 104 +
    #     candidate; gate leg0 machine output governs per r359
    #     law). W114 finalize LANDED (chain head 615,348, K=248,720,
    #     bm-a r594 one-pass) + ZERO in-flight upstream seats --
    #     finalize merge loop still derives the wave set from
    #     registry keys at run time, FAIL-CLOSED r307 always on.
    #     ADMIT receipt results/_r384bmc_w115_band_gate.py; not a
    #     re-pick (R250: W115 bands were never assigned).
    _set_wave(115)
    try:
        assert WAVE_CONFIGS[115]["a_seed_base"] == pf.N1_BANDS[115]["a"][0], \\
            "W115 A band drift vs law mirror"
        assert WAVE_CONFIGS[115]["b_exit_seed_base"] == \\
            pf.N1_BANDS[115]["b_exit"][0], "W115 B band drift vs law mirror"
        assert WAVE_CONFIGS[115].get("engine_owner") == \\
            pf.N1_BANDS[115].get("engine_owner") == "bm-c", \\
            "W115 engine_owner drift (law mirror parity)"
        w115_a = {A_SEED_BASE + j for j in range(A_N)}
        w115_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w115_a & w115_b), "W115 A/B band overlap"
        assert not (w115_a & reg_ints) and not (w115_b & reg_ints), \\
            "W115 hits SEED_REGISTRY"
        for nm, band in (("A", w115_a), ("B", w115_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W115 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W115 {nm} hits W1"
            assert not (band & probes), f"W115 {nm} hits probe seeds"
        # registered row parity (r307 pinned constants, recent estate)
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
        assert pf.N1_BANDS[114] == {"a": (271_004, 273_003),
                                    "b_exit": (62_201, 62_400),
                                    "engine_owner": "bm-a"}, \\
            "registered W114 row parity drift (r307; bm-a r594)"
        # prior-wave disjointness W2..W114 (single state: all
        # registered, dynamic registry derive, r511 law)
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 115):
            assert not (w115_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W115 A hits W{wprev}"
            assert not (w115_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W115 B hits W{wprev}"
        n3r1_used115 = set(range(70_000, 70_006))
        assert not (w115_a & n3r1_used115) and not (w115_b & n3r1_used115), \\
            "W115 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        assert not (w115_a & lfc_actual12) and not (w115_b & lfc_actual12), \\
            "W115 bands must clear the lfc actual draw range"
        assert not (w115_a & options_actual12) and \\
            not (w115_b & options_actual12), \\
            "W115 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W115 row, r384): A = arithmetic
        # continuation from the registered W114 tails, zero skips;
        # B = pinned D-20261002-05 past-hit restart (jump window).
        assert WAVE_CONFIGS[115]["a_seed_base"] == 273_004 == 273_003 + 1, (
            "W115 A must be the arithmetic continuation past the W114 "
            "registered A band tail")
        arith_a115 = set(range(273_004, 275_004))
        assert not (arith_a115 & reg_ints), \\
            "W115 A window must be CLEAN (arithmetic ADMIT face)"
        assert WAVE_CONFIGS[115]["b_exit_seed_base"] == 62_501 == 62_500 + 1, (
            "W115 B must be the pinned past-hit restart at 62_500+1 "
            "(D-20261002-05 越hit起窗)")
        arith_b115 = set(range(62_401, 62_601))
        assert 62_500 in arith_b115, \\
            "W115 B arithmetic window must CONTAIN the SEED_REGISTRY "
            "grid_sleeve_p1=62_500 refusal point (forced jump, R250 face)"
        assert any(reg_ints & arith_b115), \\
            "W115 B arithmetic window must be REFUSED in-band (jump forced)"
        assert not (w115_b & reg_ints), \\
            "W115 B registered window must be CLEAN past the hit"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W115-SHARD-0",
                                          "n1w115-0of12"), "W115 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W115-SHARD-11",
                                           "n1w115-11of12")
        assert SHARD_DIR.endswith("n1_w115") and OUT.endswith(
            "n1_w115_results.json"), "W115 path drift"
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 115):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W115 shard dir collides with W{wprev}"
        # W115 finalize cumulative deps: W17..W114 outputs ALL PRESENT
        # (landed chain head 615,348 = W114 bm-a r594 one-pass; ZERO
        # in-flight upstream seats, single closed state; the finalize
        # merge loop derives the wave set from registry keys at run
        # time and stays FAIL-CLOSED, r307 law).
        for _depw in range(17, 115):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W115 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): every
        # registered wave below 115 composes; wave 15 excluded by
        # design; SINGLE STATE (W2..W114 all registered -- no
        # two-state seat disclosure needed at this freeze).
        assert sorted(w for w in WAVE_CONFIGS if w < 115) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 115)], \\
            "W115 prior-wave set must derive from registry keys (no 15; " \\
            "W2..W114 registered single state)"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W115_PREREG.md")), \\
            "W115 per-wave prereg missing (materializer requirement)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W115 materializer face' in t2b:
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
            + LEG115
            + '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n')
    t2b = rep(t2b, A3, NEW3, eol2b, 'n1-leg115')
    save(FP2, t2b)
    print('edit3 selftest W115 leg landed (insert before T-141 selftest lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment ----------------------
t2c, eol2c = load(FP2)
if '+ W115 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('"free pick -- R250), law sec.4 W114 row, r592 bm-a] "\n'
          '          "+ T-141 s2 ')
    SEG115 = ('"free pick -- R250), law sec.4 W114 row, r592 bm-a] "\n'
              '          "+ W115 materializer face [same guard set, dep=W17..W114 "\n'
              '"outputs ALL PRESENT (landed chain head 615,348 = W114 "\n'
              '"bm-a r594 one-pass, K=248,720; ZERO in-flight upstream seats "\n'
              '"-- W2..W114 all landed, finalize merge loop still derives the "\n'
              '"wave set from registry keys at run time, FAIL-CLOSED r307 "\n'
              '"always on), ONE HUNDRED-AND-FIFTH ENGINE-OWNED WAVE BY "\n'
              '"MACHINE-DERIVE (engine_owner rows 104 + candidate) bm-c\'s "\n'
              '"thirty-fourth owned claim per machine-derive (engine_owner==bm-c "\n'
              '"rows 33 + candidate), engine_owner=bm-c per engine de-throttle "\n'
              '"law O-20261001-2355 sec.2 own-continuous-series (wave 115 = "\n'
              '"first FREE number after the REGISTERED W114 row bm-a r594 "\n'
              '"freeze ddacf2616, SINGLE STATE zero seat gap W2..W114 all "\n'
              '"registered; seat published=reserved MSG-20261002-2130-bmc-w115-seat "\n'
              '"pushed to origin ac241dd32 BEFORE this freeze, r565 law; "\n'
              '"payload = seat MSG + pre-seat probe deletion-set EMPTY, rev.A = "\n'
              '"only published face), A=arithmetic continuation from the "\n'
              '"registered W114 A tail (273_004..275_003 CLEAN hops=0) + "\n'
              '"B=pinned D-20261002-05 past-hit restart (arithmetic "\n'
              '"62_401..62_600 refused in-band at SEED_REGISTRY grid_sleeve_p1 "\n'
              '"=62_500 mid-window -> restart 62_501..62_700 CLEAN hops=1; ADMIT "\n'
              '"receipt results/_r384bmc_w115_band_gate.py; W116+ projection per "\n'
              '"this window gate: A 275_004..277_003 CLEAN / B 62_701..62_900 "\n'
              '"CLEAN disclosed for the next freezer; not a free pick -- R250), "\n'
              '"law sec.4 W115 row, r384 bm-c] "\n'
              '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG115, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W115 segment landed (insert after W114 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W115 row ---------------------
ROW115 = f"""
- N1 波115（r384 bm-c 冻·prereg 时展行）：**第一百零五枚引擎波·bm-c 第三十四枚自有波〔机面 derive：engine_owner 行 104+本候选／engine_owner==bm-c 行 33+本候选·r359 律计数面以 gate 机输出为准〕**·engine_owner=bm-c·SATURATION_ENGINE_LAW §1/§2 同 W10-W114 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-c 实例=**常驻架构 v0.4 mtime-reload**——冻结编辑落工作树后 LIVE 引擎下一 tick 重读活树自见 W115 行并点火〔D-20261002-03 修法·r325/r330 kill-restart 序免做〕·点火验证唯一证据=产物增长面 r325 律·2 tick 窗】·【never-dry 供给律常设步·**波号 115=注册表 W114 行后首个自由号·单态零席位空档**（W110=bm-a r589 freeze ff0b1869b+W111=bm-b r589 freeze e0a103ec1+W112=bm-a r590 freeze 0c4d67910+W113=bm-c r382 freeze eeb062290+W114=bm-a r594 freeze ddacf2616 均已注册·表尾=W114 行）·**席位公示=MSG-20261002-2130-bmc-w115-seat**〔published=reserved r518-① 律·先于冻结 commit 推 origin ac241dd32=r565 早可见性律·payload=席位 MSG+pre-seat probe 双件 deletion-set 空·rev.A=唯一发布面〕】·本窗实况=**W114 finalize 已落账（净链头 615,348·K=248,720 合并池·bm-a r594 W114 one-pass）+零在飞上游席（W2..W114 全落账=本波 finalize 链序前置零空档·跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**·**带位（r535 机闸 derive 律·活注册表机证·单态收敛门·ADMIT 回执=results/_r384bmc_w115_band_gate.py rc0 实跑·pre-seat probe _r383bmc_w115_probe.py 先跑·双窗 derive 恒等·hops A=0/B=1）**：**A-ext seed=273_004..275_003**（==W114 行 A 尾 273_003+1 起算术续带·步长 2_000·**CLEAN 零拒绝点**）；**B-ext exit seed=62_501..62_700**（==W114 行 B 尾 62_400+1 起算术窗 62_401..62_600 撞 SEED_REGISTRY `grid_sleeve_p1`=62_500〔中位命中 100/200 非边缘〕→ 法典 §4 D-20261002-05 越 hit 起窗·**撞值跳位**·步长 200·先例族=W5/W26/W63/W68/W87/W109）。R250：W115 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W115 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W115_PREREG.md（冻结件·锚=W114 finalize 实测值〔merged mu {_w114_mu}·K=248,720·K-lift {_w114_klift}·A-p95 {_w114_p95}·se_mu {_w114_se_mu}〕）·**W116+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 275_004..277_003 **CLEAN**（hops=0）；B 62_701..62_900 **CLEAN**（hops=0）（r384 冻结窗 gate 回执尾行·与本席位 MSG 投影披露交叉验证一致）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce2115\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW115.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W115 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    115: {"a": (273_004') == 1, 'FIX-B FAIL: W115 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W115"') == 1, 'FIX-B FAIL: W115 config not exactly once'
for w in range(58, 115):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W115 materializer face') == 2, \
    'FIX-B FAIL: W115 leg+summary must be exactly 2'
for w in range(48, 115):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce2115\uff08') == 1, 'FIX-B FAIL: canon W115 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W115 added per face')

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
print('FREEZE_EDITS_OK 115')
