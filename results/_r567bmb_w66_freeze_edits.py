# -*- coding: utf-8 -*-
"""r567 bm-b W66 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r566 lineage).

FIX-A (origin-blob freshness): every tracked edit target must be content-equal
  to origin/main BEFORE any edit runs. Kills the r559 stale-base clobber.
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W65, bm-b's),
  and after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W66 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W66 = FIFTY-FIFTH engine wave, bm-b's TWENTY-FIRST owned per machine-derive
(engine_owner==bm-b rows 20 + candidate). Seat declared published=reserved
(MSG-20261002-0940-bmb, r518-1 law; never-dry standing step -- W65 burned
12/12 local this same session chain, engine queue DRY -> zero-gap own-series
relay). W64 bm-a (burn in flight) + W65 bm-b (burned 12/12, finalize
chain-pending) = TWO in-flight upstream seats at this freeze; W1..W63
finalizes ALL LANDED (net head 503,148, K=136,520, bm-c r358).
A-side ARITHMETIC CONTINUATION no skip (175_004..177_003 CLEAN);
B-side FORCED SKIP past SEED_REGISTRY cta_p1=50_000 (arithmetic
49_801..50_000 REFUSED; first clean window 50_001..50_200; single
end-point hit so past-hit == window-stride -- no r566-bm-a W63-B
double-point semantics divergence).
"""
import subprocess, sys, os

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
TARGETS = [
    'scripts/perpetual_faces.py',
    'scripts/perpetual_faces_n1.py',
    'research/PERPETUAL_FACES.md',
]
for p in TARGETS:
    r = subprocess.run(['git', '-C', REPO, 'diff', 'origin/main', '--numstat', '--', p],
                       capture_output=True)
    out = r.stdout.decode('utf-8', 'replace').strip()
    if r.returncode != 0:
        sys.exit(f'FIX-A git fail on {p}')
    for line in out.splitlines():
        add, dele, path = line.split('\t')
        if int(dele) > 0:
            sys.exit(f'STALE BASE (FIX-A abort): {p} shows {dele} deleted lines vs '
                     f'origin/main -- checkout origin version first '
                     f'(r559 clobber cure)')
print('FIX-A: all 3 tracked edit targets show zero deletions vs origin/main (fresh base)')

# ---------------- survival signature baseline (FIX-B) ------------------------
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20,
             21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
             37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52,
             53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65]
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {'w59leg': n1_0.count('W59 materializer face'),
       'w60leg': n1_0.count('W60 materializer face'),
       'w61leg': n1_0.count('W61 materializer face'),
       'w62leg': n1_0.count('W62 materializer face'),
       'w63leg': n1_0.count('W63 materializer face'),
       'w64leg': n1_0.count('W64 materializer face'),
       'w65leg': n1_0.count('W65 materializer face')}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in (48, 49, 50, 51, 52, 53, 54, 55, 56,
                                                    57, 58, 59, 60, 61, 62, 63, 64, 65)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[66] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '66: {"a": (175_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    65: {"a": (173_004, 175_003), "b_exit": (49_601, 49_800),\n'
          '         "engine_owner": "bm-b"},\n'
          '}\n')
    NEW = ('    65: {"a": (173_004, 175_003), "b_exit": (49_601, 49_800),\n'
           '         "engine_owner": "bm-b"},\n'
           '    # FIFTY-FIFTH ENGINE-OWNED WAVE (r567 bm-b freeze): bm-b\'s\n'
           '    # TWENTY-FIRST owned per machine-derive (engine_owner==bm-b\n'
           '    # rows 20 + candidate). Wave 66 = next free number after the\n'
           '    # registered W65 row (seat declared published=reserved\n'
           '    # MSG-20261002-0940-bmb, r518-1 law; never-dry standing step:\n'
           '    # W65 burned 12/12 local this same session chain, engine\n'
           '    # queue DRY -> zero-gap own-series relay per\n'
           '    # O-20261001-2355 sec.2). W1..W63 finalizes ALL LANDED (net\n'
           '    # head 503,148, K=136,520, bm-c r358); W64 bm-a (burn in\n'
           '    # flight) + W65 bm-b (burned 12/12, finalize chain-pending)\n'
           '    # = TWO in-flight upstream seats at this freeze\n'
           '    # (FAIL-CLOSED r307). A-side ARITHMETIC CONTINUATION from\n'
           '    # the W65 row tail no skip: 175_004..177_003 (= W65 A end\n'
           '    # 175_003 + 1) CLEAN per the W65 row W66+ WARNING projection\n'
           '    # (r566 probe + this freeze\'s machine re-derive, r535 law).\n'
           '    # B-side FORCED SKIP past SEED_REGISTRY cta_p1=50_000:\n'
           '    # arithmetic 49_801..50_000 REFUSED at the single end-point\n'
           '    # hit 50_000 -> first clean window 50_001..50_200\n'
           '    # machine-derived (single end-point hit so past-hit ==\n'
           '    # window-stride, no r566-bm-a W63-B double-point semantics\n'
           '    # divergence; skip family W26-A/W39-B/W43-B/W47-B/W51-B/\n'
           '    # W59-B/W63-B lineage). Machine-verified at prereg time\n'
           '    # (results/_r567bmb_w66_band_gate.py ADMIT receipt vs the\n'
           '    # 64-row pre-W66 table + live SEED_REGISTRY values + probe\n'
           '    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin\n'
           '    # slot vacancy machine-checked). NOT a re-pick (R250: W66\n'
           '    # bands were never assigned).\n'
           '    66: {"a": (175_004, 177_003), "b_exit": (50_001, 50_200),\n'
           '         "engine_owner": "bm-b"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[66] landed (anchor=W65 row, insert)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[66] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '66: {"batch": "PERPETUAL-N1-W66"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('"shard_subdir": "n1_w65", "out_name": "n1_w65_results.json",\n'
          '                            "engine_owner": "bm-b"},\n'
          '                       }')
    NEW2 = ('"shard_subdir": "n1_w65", "out_name": "n1_w65_results.json",\n'
            '                            "engine_owner": "bm-b"},\n'
            '                       66: {"batch": "PERPETUAL-N1-W66",\n'
            '                            "prereg": ("research/PERPETUAL_N1_W66_PREREG.md (wave-level frozen "\n'
            '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
            '                                       "new seed bands only; FIFTY-FIFTH ENGINE-OWNED WAVE, "\n'
            '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
            '                                       "(first-free-number law over the registered W65 row; "\n'
            '                                       "seat declared published=reserved MSG-20261002-0940-bmb), "\n'
            '                                       "engine_owner=bm-b, wave 66 A-side ARITHMETIC "\n'
            '                                       "CONTINUATION no skip (175_004..177_003 CLEAN) + "\n'
            '                                       "B-side FORCED SKIP past SEED_REGISTRY cta_p1=50_000 "\n'
            '                                       "(arithmetic 49_801..50_000 REFUSED; first clean "\n'
            '                                       "window 50_001..50_200 machine-derived == the W65 row "\n'
            '                                       "W66+ published projection verbatim; single end-point "\n'
            '                                       "hit: past-hit == window-stride, no semantics "\n'
            '                                       "divergence); W1..W63 finalizes ALL LANDED at this "\n'
            '                                       "freeze (net chain head 503,148, K=136,520, bm-c "\n'
            '                                       "r358), W64 bm-a + W65 bm-b = TWO in-flight "\n'
            '                                       "upstream seats (finalize chain-pending "\n'
            '                                       "FAIL-CLOSED r307)"),\n'
            '                            "a_seed_base": 175_004,        # law sec.4 W66 A: 175_004..177_003 (arithmetic continuation)\n'
            '                            "b_exit_seed_base": 50_001,    # law sec.4 W66 B: 50_001..50_200 (forced skip past cta_p1=50_000)\n'
            '                            "shard_subdir": "n1_w66", "out_name": "n1_w66_results.json",\n'
            '                            "engine_owner": "bm-b"},\n'
            '                       }')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[66] landed (anchor=W65 entry tail, insert)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W66 leg --------------
LEG66 = '''
    # --- W66 materializer face (r567 bm-b freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2):
    #     bm-b's TWENTY-FIRST owned per machine-derive (engine_owner==bm-b
    #     rows 20 + candidate); wave 66 = next free number after the
    #     registered W65 row (seat declared published=reserved
    #     MSG-20261002-0940-bmb; never-dry standing step -- W65 burned
    #     12/12 local the same session chain, engine queue DRY,
    #     zero-gap own-series relay).
    #     W64 bm-a (burn in flight) + W65 bm-b (finalize chain-pending)
    #     = TWO in-flight upstream seats at this freeze (FAIL-CLOSED
    #     r307). A-side ARITHMETIC CONTINUATION from the W65 tail no
    #     skip (175_004..177_003 CLEAN); B-side FORCED SKIP past
    #     SEED_REGISTRY cta_p1=50_000 (arithmetic 49_801..50_000 REFUSED;
    #     first clean window 50_001..50_200 machine-derived == the W65
    #     row W66+ published projection verbatim; single end-point hit so
    #     past-hit == window-stride -- no r566-bm-a W63-B double-point
    #     semantics divergence; ADMIT receipt
    #     results/_r567bmb_w66_band_gate.py; not a re-pick -- R250:
    #     W66 bands were never assigned) --
    _set_wave(66)
    try:
        assert WAVE_CONFIGS[66]["a_seed_base"] == pf.N1_BANDS[66]["a"][0], \\
            "W66 A band drift vs law mirror"
        assert WAVE_CONFIGS[66]["b_exit_seed_base"] == \\
            pf.N1_BANDS[66]["b_exit"][0], "W66 B band drift vs law mirror"
        assert WAVE_CONFIGS[66].get("engine_owner") == \\
            pf.N1_BANDS[66].get("engine_owner") == "bm-b", \\
            "W66 engine_owner drift (law mirror parity)"
        w66_a = {A_SEED_BASE + j for j in range(A_N)}
        w66_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w66_a & w66_b), "W66 A/B band overlap"
        assert not (w66_a & reg_ints) and not (w66_b & reg_ints), \\
            "W66 hits SEED_REGISTRY"
        for nm, band in (("A", w66_a), ("B", w66_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W66 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W66 {nm} hits W1"
            assert not (band & probes), f"W66 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W61/W62/W63/
        # W64/W65 are REGISTERED rows now -- pinned constants must equal
        # the registered rows exactly.
        assert pf.N1_BANDS[61] == {"a": (165_004, 167_003),
                                   "b_exit": (48_401, 48_600),
                                   "engine_owner": "bm-b"}, \\
            "registered W61 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[62] == {"a": (167_004, 169_003),
                                   "b_exit": (48_601, 48_800),
                                   "engine_owner": "bm-a"}, \\
            "registered W62 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[63] == {"a": (169_004, 171_003),
                                   "b_exit": (49_201, 49_400),
                                   "engine_owner": "bm-c"}, \\
            "registered W63 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[64] == {"a": (171_004, 173_003),
                                   "b_exit": (49_401, 49_600),
                                   "engine_owner": "bm-a"}, \\
            "registered W64 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[65] == {"a": (173_004, 175_003),
                                   "b_exit": (49_601, 49_800),
                                   "engine_owner": "bm-b"}, \\
            "registered W65 row parity drift (r307 two-state)"
        # prior-wave disjointness incl. W48..W65 (all registered; W64/W65
        # in flight -- coexist by band disjointness per r531).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65):
            assert not (w66_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W66 A hits W{wprev}"
            assert not (w66_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W66 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W66 clears it.
        n3r1_used66 = set(range(70_000, 70_006))
        assert not (w66_a & n3r1_used66) and not (w66_b & n3r1_used66), \\
            "W66 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w66_a & lfc_actual12) and not (w66_b & lfc_actual12), \\
            "W66 bands must clear the lfc actual draw range"
        assert not (w66_a & options_actual12) and \\
            not (w66_b & options_actual12), \\
            "W66 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W66 row, r567): A ARITHMETIC CONTINUATION
        # (175_004 = W65 A end 175_003 + 1, window CLEAN -- no skip);
        # B FORCED SKIP (arithmetic 49_801..50_000 refused at the single
        # end-point SEED_REGISTRY cta_p1=50_000; first clean window
        # 50_001..50_200 machine-derived; past-hit == window-stride on a
        # single end-point hit -- W26-A/W39-B/W43-B/W47-B/W51-B/W59-B/
        # W63-B skip family, no r566-bm-a double-point divergence).
        assert WAVE_CONFIGS[66]["a_seed_base"] == 175_004 == 175_003 + 1, \\
            "W66 A must start at the registered W65 A end + 1 " \\
            "(arithmetic continuation window 175_004..177_003 CLEAN -- " \\
            "no skip family)"
        assert WAVE_CONFIGS[66]["b_exit_seed_base"] == 50_001, \\
            "W66 B must be the machine-derived first clean window " \\
            "50_001..50_200 (arithmetic 49_801..50_000 REFUSED at " \\
            "SEED_REGISTRY cta_p1=50_000 -- forced skip family)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W66-SHARD-0",
                                          "n1w66-0of12"), "W66 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W66-SHARD-11",
                                          "n1w66-11of12")
        assert SHARD_DIR.endswith("n1_w66") and OUT.endswith(
            "n1_w66_results.json"), "W66 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W66 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W66_PREREG.md")), \\
            "W66 per-wave prereg missing (materializer requirement)"
        # W66 finalize cumulative deps: W17..W63 outputs ALL PRESENT
        # (static landed seats; chain head 503,148 = W63 bm-c r358
        # K=136,520; W64 bm-a + W65 bm-b = TWO in-flight upstream seats
        # -- the finalize merge loop derives the wave set from registry
        # keys at run time and stays FAIL-CLOSED on the not-yet-finalized
        # W64/W65 seats, r307 two-state law).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                      43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
                      56, 57, 58, 59, 60, 61, 62, 63):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W66 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 66 (no 15; incl.
        # 48..65 -- all registered, W64/W65 finalize in flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 66) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
             65], \\
            "W66 prior-wave set must derive from registry keys (no 15, " \\
            "incl. 48..65)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W66 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG66.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W66 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 5th face) ------
t2c, eol2c = load(FP2)
if '+ W66 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('law sec.4 W65 row, r566 bm-b] "\n'
          '          "+ T-141 s2 ')
    SEG66 = ('law sec.4 W65 row, r566 bm-b] "\n'
             '          "+ W66 materializer face [same guard set, dep=W17..W63 "\n'
             '          "outputs ALL PRESENT (landed chain head 503,148, K=136,520), "\n'
             '          "W64 bm-a + W65 bm-b = TWO in-flight upstream seats "\n'
             '          "(FAIL-CLOSED r307 at run time), FIFTY-FIFTH ENGINE-OWNED "\n'
             '          "WAVE bm-b\'s TWENTY-FIRST owned claim per machine-derive "\n'
             '          "(engine_owner==bm-b rows 20 + candidate), "\n'
             '          "engine_owner=bm-b per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series (wave 66 = "\n'
             '          "first FREE number after the registered W65 row; seat "\n'
             '          "declared published=reserved MSG-20261002-0940-bmb; never-dry "\n'
             '          "standing step -- W65 burned 12/12 local, engine queue "\n'
             '          "DRY, zero-gap own-series relay), A-side ARITHMETIC "\n'
             '          "CONTINUATION from the W65 tail no skip (175_004..177_003 "\n'
             '          "CLEAN) + B-side FORCED SKIP past SEED_REGISTRY "\n'
             '          "cta_p1=50_000 (arithmetic 49_801..50_000 REFUSED; first "\n'
             '          "clean window 50_001..50_200 machine-derived per the W65 "\n'
             '          "row W66+ WARNING; single end-point hit: past-hit == "\n'
             '          "window-stride, no semantics divergence; ADMIT receipt "\n'
             '          "results/_r567bmb_w66_band_gate.py; not a free pick -- "\n'
             '          "R250), N3-R1 used-seed leg, probe-seed cluster leg, "\n'
             '          "law sec.4 W66 row, r567 bm-b] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG66, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W66 segment landed (insert after W65 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W66 row -------------------
ROW66 = """
- N1 波66（r567 bm-b 冻·prereg 时展行）：**第五十五枚引擎波·bm-b 第二十一枚自有波〔机面 derive：engine_owner==bm-b 行 20+本候选〕**·engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W65 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-b 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启免做·W55/W56/W59/W61/W65 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 66=注册表 W65 行后首个自由号**·席位公示=MSG-20261002-0940-bmb（published=reserved r518-① 律·W48/W49/W55/W62/W65 先例）·r511 表尾锁例冻结前 fetch 实核表尾时 W66 号位净空·origin 侧 vacancy 机验·**零隔接力：本机 W65 12/12 烧毕同窗（引擎队列已干=never-dry 触发面）**】·**A 面算术续带零跳位+B 面强制跳位（r535 机闸 derive 律）**：W65 行 W66+ 警示投影 **A 175_004..177_003 CLEAN／B 49_801..50_000 REFUSED〔SEED_REGISTRY cta_p1=50_000〕→首净窗 50_001..50_200**（r566 bm-b 冻结窗 _r566bmb_w66_probe.py 投影腿机证+本波 r567 bm-b gate 复核逐字同〔r302 陈旧指针证伪律下本波机闸独立 derive 非 prose 转抄〕）→本波 **A-ext seed=175_004..177_003**（**A 面算术续带**==W65 A 尾 175_003+1·步长逐字）·**B-ext exit seed=50_001..50_200**（**B 面强制跳位族**=算术位 49_801..50_000 撞 SEED_REGISTRY cta_p1=50_000 单点窗尾拒绝→首净窗 50_001..50_200〔**单点窗尾撞=越 hit 起窗与窗步链跳两读法同解·无 r566 bm-a W63-B 双点分叉面**·跳位族 W26-A/W39-B/W43-B/W47-B/W51-B/W59-B/W63-B 序〕）·【机证净空——leg0 六十五键（64 注册行+候选）+leg0b W65 行 W66+ 警示 prose 在场校验+leg1-A 算术位 CLEAN+leg1-B 拒绝点机证〔50_000=cta_p1〕+leg2-B 首净窗==候选逐位+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验·**MSG-0640 三修工具**（FIX-A 编辑前 origin-blob 等值断言+FIX-B 锚=最后注册行+行存活核查+FIX-C 推送前纯增量 diff 断言）〕·ADMIT 回执=results/_r567bmb_w66_band_gate.py·r567 bm-b 起草窗实跑·非重挑 R250·W66 带从未指派·测量面零结果可钓】·扫描面=pre-W66 六十四行 N1 带表【含 **W63 行 169_004..171_003/49_201..49_400〔bm-c r357·finalize 已落账 K=136,520·净账本链头 503,148·bm-c r358〕**·**W64 行 171_004..173_003/49_401..49_600〔bm-a r566·注册烧录在飞·finalize 未落账〕**·**W65 行 173_004..175_003/49_601..49_800〔bm-b r566·12/12 烧毕·finalize 未落账〕**】·**双在飞上游席披露：本波 finalize 链序前置=W64+W65 落账·FAIL-CLOSED r307 两态律**·带域不相交·W1 ext·v1 在用带·SEED_REGISTRY 全键（int 值全清·LOWAMP-P1/P2/P3 键 20.33M 域零交集）·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·lfc 实际流 30_000..30_099·options_wave2 实际流 63_000..63_049（leg-3e 实际流避让腿）·**W67+ 投影（带闸投影腿机证·W67 prereg 照例带闸复核 r335 律）：A 177_004..179_003 CLEAN／B 50_201..50_400 CLEAN（复核于 W67 prereg）**·prereg=PERPETUAL_N1_W66_PREREG.md 冻结〔S5 锚=W63 实测：merged mu −0.092648/W63-only mu −0.098792/sigma 0.239446/A-p95 0.3016/K-lift −0.0005·累计池投影 143,120（含 W64+W65 在飞 4,400）〕·burn 由本机 tick 引擎按分片合同执行·finalize=活链头 derive one-pass（r538 一过律）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce266\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW66.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W66 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    66: {"a": (175_004') == 1, 'FIX-B FAIL: W66 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W66"') == 1, 'FIX-B FAIL: W66 config not exactly once'
for leg, base in (('W59 materializer face', 'w59leg'),
                  ('W60 materializer face', 'w60leg'),
                  ('W61 materializer face', 'w61leg'),
                  ('W62 materializer face', 'w62leg'),
                  ('W63 materializer face', 'w63leg'),
                  ('W64 materializer face', 'w64leg'),
                  ('W65 materializer face', 'w65leg')):
    assert n11.count(leg) == BASE_SIGS[base], f'FIX-B FAIL: {leg} lost'
assert n11.count('W66 materializer face') == 2, \
    'FIX-B FAIL: W66 leg+summary must be exactly 2'
for w in (48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce266\uff08') == 1, 'FIX-B FAIL: canon W66 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W66 added per face')

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
print('FREEZE_EDITS_OK')
