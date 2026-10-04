# -*- coding: utf-8 -*-
"""r677 bm-b W116 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening.

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED rows (W111 bm-b +
  W112 bm-a + W113 bm-c + W114 bm-a + W115 bm-c); every registered row
  signature survives exactly; exactly one new W116 signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.
AST gate (r580/r581 lesson): post-edit ast.parse on both py faces.

W116 = ONE HUNDRED-AND-SIXTH engine wave BY MACHINE-DERIVE (engine_owner
rows 105 + candidate; gate leg0 machine output governs per r359 law),
bm-b's THIRTY-NINTH owned (engine_owner==bm-b rows 38 + candidate).
First free number after the REGISTERED W115 row (bm-c r445 unpark-freeze
f6b521153) -- SINGLE STATE zero seat gap (W2..W115 all registered).
Seat published=reserved MSG-20261004-1515-bmb-w116-seat pushed to origin
4b0409196 BEFORE this freeze (r565 early-visibility law; payload = seat
MSG + pre-seat probe + D-19 receipts, deletion-set EMPTY, rev.A = only
published face).
Bands:
  A 275_004..277_003 (W115 A tail 275_003 + 1, stride 2_000) hops=0 CLEAN.
  B 62_701..62_900   (W115 B tail 62_700 + 1, stride 200) hops=0 CLEAN
                     (zero-jump two-reading-identical face).
  ADMIT receipt results/_r677bmb_w116_band_gate.py rc0; banned gate ADMIT 0.
W115 finalize LANDED (net chain head 617,548, K=250,920 = bm-c r445
one-pass). ZERO in-flight upstream seats (W2..W115 all landed) -- finalize
merge loop still derives the wave set from registry keys at run time,
FAIL-CLOSED r307 two-state law always on.
W117+ projection (gate-derived this window): A 277_004..279_003 CLEAN
hops=0 / B first-clean 65_050..65_249 hops=1 (arith window 62_901..63:100
REFUSED at options_wave2 actual 63_000..63_049 + registered A-band
overlap; next freezer must re-derive, never transcribe; r587 law).
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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 116))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 116)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 116)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[116] ---------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '116: {"a": (275_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    115: {"a": (273_004, 275_003), "b_exit": (62_501, 62_700),\n'
          '         "engine_owner": "bm-c"},\n'
          '}\n')
    NEW = ('    115: {"a": (273_004, 275_003), "b_exit": (62_501, 62_700),\n'
           '         "engine_owner": "bm-c"},\n'
           '    # ONE HUNDRED-AND-SIXTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r677 bm-b\n'
           '    # freeze): engine_owner rows 105 + candidate; bm-b\'s thirty-\n'
           '    # ninth owned per machine-derive (engine_owner==bm-b rows 38 +\n'
           '    # candidate). Wave 116 = first free number after the REGISTERED\n'
           '    # W115 row (bm-c r445 unpark-freeze f6b521153) -- SINGLE STATE\n'
           '    # zero seat gap (W2..W115 all registered). Seat published=reserved\n'
           '    # MSG-20261004-1515-bmb-w116-seat pushed to origin 4b0409196\n'
           '    # BEFORE this freeze per r565 early-visibility law (payload = seat\n'
           '    # MSG + pre-seat probe + D-19 receipts, deletion-set EMPTY; rev.A\n'
           '    # = only published face).\n'
           '    # W115 finalize LANDED (net chain head 617,548, K=250,920 = bm-c\n'
           '    # r445 one-pass). ZERO in-flight upstream seats (W2..W115 all\n'
           '    # landed) -- finalize merge loop still derives the wave set from\n'
           '    # registry keys at run time, FAIL-CLOSED r307 two-state law\n'
           '    # always on.\n'
           '    # A = arithmetic continuation from the registered W115 A tail:\n'
           '    # 275_004..277_003 CLEAN hops=0. B = arithmetic continuation\n'
           '    # from the registered W115 B tail: 62_701..62_900 CLEAN hops=0\n'
           '    # (zero-jump two-reading-identical face; ADMIT receipt\n'
           '    # results/_r677bmb_w116_band_gate.py; live SEED_REGISTRY +\n'
           '    # probe cluster 95_000..95_003 r335 leg + cross-face probe points\n'
           '    # 95_004/95_006 r602 leg + N3-R1 used-seed band 70_000..70_005\n'
           '    # MSG-183x r529 leg.\n'
           '    # W117+ projection (gate-derived r677): A 277_004..279_003 CLEAN\n'
           '    # hops=0; B first-clean 65_050..65_249 hops=1 (arith window\n'
           '    # 62_901..63:100 refused at options_wave2 actual 63_000..63_049 +\n'
           '    # registered A-band overlap; next freezer must re-derive, never\n'
           '    # transcribe; r587 law).\n'
           '    # NOT a re-pick (R250: W116 bands were never assigned).\n'
           '    116: {"a": (275_004, 277_003), "b_exit": (62_701, 62_900),\n'
           '         "engine_owner": "bm-b"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[116] landed (anchor=W115 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[116] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '116: {"batch": "PERPETUAL-N1-W116"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w115", "out_name": "n1_w115_results.json",\n'
          '                            "engine_owner": "bm-c"},\n')
    NEW2 = A2 + (
        '                       116: {"batch": "PERPETUAL-N1-W116",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W116_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; ONE HUNDRED-AND-SIXTH ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 105 + candidate), own-series "\n'
        '                                       "continuation per O-20261001-2355 sec.2 (first-free-number "\n'
        '                                       "law after the REGISTERED W115 row bm-c r445 unpark-freeze "\n'
        '                                       "f6b521153, SINGLE STATE zero seat gap W2..W115 all registered; seat "\n'
        '                                       "published=reserved MSG-20261004-1515-bmb-w116-seat PUSHED to "\n'
        '                                       "origin 4b0409196 BEFORE this freeze per r565 early-visibility "\n'
        '                                       "law; pre-seat probe and freeze-window band-gate runs derive "\n'
        '                                       "identical, no fork face; payload = seat MSG + pre-seat probe + "\n'
        '                                       "D-19 receipts, deletion-set EMPTY, rev.A = only published face), "\n'
        '                                       "engine_owner=bm-b, wave 116: "\n'
        '                                       "A = arithmetic continuation from the registered W115 A tail "\n'
        '                                       "(275_004..277_003 CLEAN hops=0) + B = arithmetic continuation "\n'
        '                                       "from the registered W115 B tail (62_701..62_900 CLEAN hops=0, "\n'
        '                                       "zero-jump two-reading-identical face; ADMIT receipt "\n'
        '                                       "results/_r677bmb_w116_band_gate.py; W117+ projection per this "\n'
        '                                       "window gate: A 277_004..279_003 CLEAN / B first-clean "\n'
        '                                       "65_050..65_249 (arith 62_901..63:100 refused at options actual + "\n'
        '                                       "registered A-band overlap, hops=1) for the next freezer); "\n'
        '                                       "W115 finalize LANDED (net chain head 617,548, K=250,920, bm-c "\n'
        '                                       "r445 one-pass) + ZERO in-flight upstream seats -- finalize "\n'
        '                                       "merge loop still derives the wave set from registry keys at "\n'
        '                                       "run time, FAIL-CLOSED r307 always on)"),\n'
        '                            "a_seed_base": 275_004,        # law sec.4 W116 A: 275_004..277_003 (arithmetic continuation from the registered W115 A tail)\n'
        '                            "b_exit_seed_base": 62_701,   # law sec.4 W116 B: 62_701..62_900 (arithmetic continuation from the registered W115 B tail)\n'
        '                            "shard_subdir": "n1_w116", "out_name": "n1_w116_results.json",\n'
        '                            "engine_owner": "bm-b"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[116] landed (anchor=W115 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W116 leg --------------
LEG116 = '''
    # --- W116 materializer face (r677 bm-b freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-b's
    #     thirty-ninth owned per machine-derive (engine_owner==bm-b
    #     rows 38 + candidate); wave 116 = first free number after
    #     the REGISTERED W115 row (bm-c r445 unpark-freeze f6b521153)
    #     -- SINGLE STATE zero seat gap (W2..W115 all registered).
    #     Seat published=reserved MSG-20261004-1515-bmb-w116-seat
    #     pushed to origin 4b0409196 BEFORE this freeze, r565 law
    #     (payload = seat MSG + pre-seat probe + D-19 receipts;
    #     deletion-set EMPTY; rev.A = only published face).
    #     ONE HUNDRED-AND-SIXTH engine wave BY MACHINE-DERIVE
    #     (engine_owner rows 105 + candidate; gate leg0 machine
    #     output governs per r359 law). W115 finalize LANDED (net
    #     chain head 617,548, K=250,920, bm-c r445 one-pass) + ZERO
    #     in-flight upstream seats -- finalize merge loop still
    #     derives the wave set from registry keys at run time,
    #     FAIL-CLOSED r307 always on. ADMIT receipt
    #     results/_r677bmb_w116_band_gate.py; banned gate ADMIT 0;
    #     not a re-pick (R250: W116 bands were never assigned).
    _set_wave(116)
    try:
        assert WAVE_CONFIGS[116]["a_seed_base"] == pf.N1_BANDS[116]["a"][0], \\
            "W116 A band drift vs law mirror"
        assert WAVE_CONFIGS[116]["b_exit_seed_base"] == \\
            pf.N1_BANDS[116]["b_exit"][0], "W116 B band drift vs law mirror"
        assert WAVE_CONFIGS[116].get("engine_owner") == \\
            pf.N1_BANDS[116].get("engine_owner") == "bm-b", \\
            "W116 engine_owner drift (law mirror parity)"
        w116_a = {A_SEED_BASE + j for j in range(A_N)}
        w116_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w116_a & w116_b), "W116 A/B band overlap"
        assert not (w116_a & reg_ints) and not (w116_b & reg_ints), \\
            "W116 hits SEED_REGISTRY"
        for nm, band in (("A", w116_a), ("B", w116_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W116 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W116 {nm} hits W1"
            assert not (band & probes), f"W116 {nm} hits probe seeds"
        # registered row parity (r307 pinned constants, recent estate)
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
        assert pf.N1_BANDS[115] == {"a": (273_004, 275_003),
                                    "b_exit": (62_501, 62_700),
                                    "engine_owner": "bm-c"}, \\
            "registered W115 row parity drift (r307; bm-c r445)"
        # prior-wave disjointness W2..W115 (single state: all
        # registered, dynamic registry derive, r511 law)
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 116):
            assert not (w116_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W116 A hits W{wprev}"
            assert not (w116_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W116 B hits W{wprev}"
        n3r1_used116 = set(range(70_000, 70_006))
        assert not (w116_a & n3r1_used116) and not (w116_b & n3r1_used116), \\
            "W116 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        assert not (w116_a & lfc_actual12) and not (w116_b & lfc_actual12), \\
            "W116 bands must clear the lfc actual draw range"
        assert not (w116_a & options_actual12) and \\
            not (w116_b & options_actual12), \\
            "W116 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W116 row, r677): A and B are both
        # arithmetic continuations from the registered W115 tails,
        # zero skips on both faces (CLEAN windows, hops=0).
        assert WAVE_CONFIGS[116]["a_seed_base"] == 275_004 == 275_003 + 1, (
            "W116 A must be the arithmetic continuation past the W115 "
            "registered A band tail")
        arith_a116 = set(range(275_004, 277_004))
        assert not (arith_a116 & reg_ints), \\
            "W116 A window must be CLEAN (arithmetic ADMIT face)"
        assert WAVE_CONFIGS[116]["b_exit_seed_base"] == 62_701 == 62_700 + 1, (
            "W116 B must be the arithmetic continuation past the W115 "
            "registered B band tail")
        arith_b116 = set(range(62_701, 62_901))
        assert not (arith_b116 & reg_ints), \\
            "W116 B window must be CLEAN (arithmetic ADMIT face, hops=0)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W116-SHARD-0",
                                          "n1w116-0of12"), "W116 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W116-SHARD-11",
                                           "n1w116-11of12")
        assert SHARD_DIR.endswith("n1_w116") and OUT.endswith(
            "n1_w116_results.json"), "W116 path drift"
        for wprev in sorted(w for w in WAVE_CONFIGS if w < 116):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W116 shard dir collides with W{wprev}"
        # W116 finalize cumulative deps: W17..W115 outputs ALL PRESENT
        # (landed net chain head 617,548 = W115 bm-c r445 one-pass;
        # ZERO in-flight upstream seats, single closed state; the
        # finalize merge loop derives the wave set from registry keys
        # at run time and stays FAIL-CLOSED, r307 law).
        for _depw in range(17, 116):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W116 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): every
        # registered wave below 116 composes; wave 15 excluded by
        # design; SINGLE STATE (W2..W115 all registered -- no
        # two-state seat disclosure needed at this freeze).
        assert sorted(w for w in WAVE_CONFIGS if w < 116) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 116)], \\
            "W116 prior-wave set must derive from registry keys (no 15; " \\
            "W2..W115 registered single state)"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W116_PREREG.md")), \\
            "W116 per-wave prereg missing (materializer requirement)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W116 materializer face' in t2b:
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
            + LEG116
            + '    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n')
    t2b = rep(t2b, A3, NEW3, eol2b, 'n1-leg116')
    save(FP2, t2b)
    print('edit3 selftest W116 leg landed (insert before T-141 selftest lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment ----------------------
t2c, eol2c = load(FP2)
if '+ W116 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('"law sec.4 W115 row, r384 bm-c] "\n'
          '          "+ T-141 s2 ')
    SEG116 = ('"law sec.4 W115 row, r384 bm-c] "\n'
              '          "+ W116 materializer face [same guard set, dep=W17..W115 "\n'
              '"outputs ALL PRESENT (landed net chain head 617,548 = W115 "\n'
              '"bm-c r445 one-pass, K=250,920; ZERO in-flight upstream seats "\n'
              '"-- W2..W115 all landed, finalize merge loop still derives the "\n'
              '"wave set from registry keys at run time, FAIL-CLOSED r307 "\n'
              '"always on), ONE HUNDRED-AND-SIXTH ENGINE-OWNED WAVE BY "\n'
              '"MACHINE-DERIVE (engine_owner rows 105 + candidate) bm-b\'s "\n'
              '"thirty-ninth owned claim per machine-derive (engine_owner==bm-b "\n'
              '"rows 38 + candidate), engine_owner=bm-b per engine de-throttle "\n'
              '"law O-20261001-2355 sec.2 own-continuous-series (wave 116 = "\n'
              '"first FREE number after the REGISTERED W115 row bm-c r445 "\n'
              '"unpark-freeze f6b521153, SINGLE STATE zero seat gap W2..W115 "\n'
              '"all registered; seat published=reserved MSG-20261004-1515-bmb-w116-seat "\n'
              '"pushed to origin 4b0409196 BEFORE this freeze, r565 law; "\n'
              '"payload = seat MSG + pre-seat probe + D-19 receipts deletion-set "\n'
              '"EMPTY, rev.A = only published face), A=arithmetic continuation "\n'
              '"from the registered W115 A tail (275_004..277_003 CLEAN hops=0) "\n'
              '"+ B=arithmetic continuation from the registered W115 B tail "\n'
              '"(62_701..62_900 CLEAN hops=0, zero-jump two-reading-identical "\n'
              '"face; ADMIT receipt results/_r677bmb_w116_band_gate.py; W117+ "\n'
              '"projection per this window gate: A 277_004..279_003 CLEAN / B "\n'
              '"first-clean 65_050..65_249 (arith 62_901..63:100 refused at "\n'
              '"options actual + registered A-band overlap, hops=1) disclosed "\n'
              '"for the next freezer; not a free pick -- R250), "\n'
              '"law sec.4 W116 row, r677 bm-b] "\n'
              '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG116, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W116 segment landed (insert after W115 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W116 row ---------------------
ROW116 = f"""
- N1 波116（r677 bm-b 冻·prereg 时展行）：**第一百零六枚引擎波·bm-b 第三十九枚自有波〔机面 derive：engine_owner 行 105+本候选／engine_owner==bm-b 行 38+本候选·r359 律计数面以 gate 机输出为准〕**·engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W115 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-b 实例=**tick 架构**——冻结编辑落工作树后下一 tick 新进程读活树自见 W116 行并点火〔r535 律·r325/r330 kill-restart 序免做〕·点火验证唯一证据=产物增长面 r325 律·2 tick 窗】·【never-dry 供给律常设步·**波号 116=注册表 W115 行后首个自由号·单态零席位空档**（W111=bm-b r589 freeze e0a103ec1+W112=bm-a r590 freeze 0c4d67910+W113=bm-c r382 freeze eeb062290+W114=bm-a r594 freeze ddacf2616+W115=bm-c r445 解停 freeze f6b521153 均已注册·表尾=W115 行）·**席位公示=MSG-20261004-1515-bmb-w116-seat**〔published=reserved r518-① 律·先于冻结 commit 推 origin 4b0409196=r565 早可见性律·payload=席位 MSG+pre-seat probe+D-19 回执件 deletion-set 空·rev.A=唯一发布面〕】·本窗实况=**W115 finalize 已落账（净链头 617,548·K=250,920 合并池·bm-c r445 W115 one-pass）+零在飞上游席（W2..W115 全落账=本波 finalize 链序前置零空档·跑时按 registry 键 derive 复核·FAIL-CLOSED r307 两态律恒在）**·**带位（r535 机闸 derive 律·活注册表机证·单态收敛门·ADMIT 回执=results/_r677bmb_w116_band_gate.py rc0 实跑·pre-seat probe _r677bmb_w116_probe.py 先跑·双窗 derive 恒等·hops A=0/B=0）**：**A-ext seed=275_004..277_003**（==W115 行 A 尾 275_003+1 起算术续带·步长 2_000·**CLEAN 零拒绝点**）；**B-ext exit seed=62_701..62_900**（==W115 行 B 尾 62_700+1 起算术续带·步长 200·**CLEAN 零拒绝点·两读法恒同解零跳位**）。R250：W116 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W116 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W116_PREREG.md（冻结件·锚=W115 finalize 实测值〔merged mu {_w115_mu}·K=250,920·K-lift {_w115_klift}·A-p95 {_w115_p95}·se_mu {_w115_se_mu}〕）·**W117+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 277_004..279_003 **CLEAN**（hops=0）；B 首净窗 **65_050..65_249**（算术窗 62_901..63:100 撞 options_wave2 实际流 63_000..63_049+注册 A 带重叠 → 越 hit 起窗·hops=1）（r677 冻结窗 gate 回执尾行·与本席位 MSG 投影披露交叉验证一致）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce2116\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW116.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W116 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    116: {"a": (275_004') == 1, 'FIX-B FAIL: W116 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W116"') == 1, 'FIX-B FAIL: W116 config not exactly once'
for w in range(58, 116):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W116 materializer face') == 2, \
    'FIX-B FAIL: W116 leg+summary must be exactly 2'
for w in range(48, 116):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce2116\uff08') == 1, 'FIX-B FAIL: canon W116 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W116 added per face')

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
print('FREEZE_EDITS_OK 116')
