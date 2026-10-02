# -*- coding: utf-8 -*-
"""r360 bm-c W68 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r561 lineage).

FIX-A (origin-blob freshness): every tracked edit target must be content-equal
  to origin/main BEFORE any edit runs (zero deleted lines). Kills the r559
  stale-base clobber and same-window seat collisions (bm-b W68 drafts).
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W67, bm-b's),
  and after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W68 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W68 = FIFTY-SEVENTH engine wave, bm-c's TWENTY-SECOND owned per
machine-derive (engine_owner==bm-c rows 21 + candidate). Seat = the freeze
commit itself (r511 table-tail lock; engine waves have no claim face -- the
table row IS the only lock) + same-window MSG cross-notice. Wave 68 = first
free number over the registered W67 row (bm-b r567, burn in flight). W64 bm-a
+ W65 bm-b + W66 bm-c + W67 bm-b = FOUR in-flight upstream seats at this
freeze (finalize chain-pending, FAIL-CLOSED r307). A-side ARITHMETIC
CONTINUATION zero skip (179_004..181_003); B-side FORCED-SKIP family,
CHAINED window-step reading = the W63 REGISTERED in-canon face (arithmetic
50_401..50_600 REFUSED by SEED_REGISTRY cta_p2_noau=50_500 MID-window hit ->
first clean window 50_601..50_800; the divergent restart reading 50_501..50_700
from bm-b's W67-row prose projection is DISCLOSED and NOT adopted -- its own
caveat "复核于 W68 prereg" + r335 law: projections are machine-re-derived,
never prose-transcribed; r566 ruling family: the registered face governs).
"""
import subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NO_WIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)   # U060 zero-flash law

def git(*a):
    r = subprocess.run(['git', '-C', REPO] + list(a), capture_output=True,
                       creationflags=NO_WIN)
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
                       capture_output=True, creationflags=NO_WIN)
    out = r.stdout.decode('utf-8', 'replace').strip()
    if r.returncode != 0:
        sys.exit(f'FIX-A git fail on {p}')
    for line in out.splitlines():
        add, dele, path = line.split('\t')
        if int(dele) > 0:
            sys.exit(f'STALE BASE (FIX-A abort): {p} shows {dele} deleted lines vs '
                     f'origin/main -- checkout origin version first '
                     f'(r559 clobber cure / same-window seat collision)')
print('FIX-A: all 3 tracked edit targets show zero deletions vs origin/main (fresh base)')

# ---------------- survival signature baseline (FIX-B) ------------------------
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20,
             21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
             37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52,
             53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67]
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {('w%dleg' % w): n1_0.count('W%d materializer face' % w)
       for w in (59, 60, 61, 62, 63, 64, 65, 66, 67)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 68)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[68] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '68: {"a": (179_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    67: {"a": (177_004, 179_003), "b_exit": (50_201, 50_400),\n'
          '         "engine_owner": "bm-b"},\n'
          '}\n')
    NEW = ('    67: {"a": (177_004, 179_003), "b_exit": (50_201, 50_400),\n'
           '         "engine_owner": "bm-b"},\n'
           '    # FIFTY-SEVENTH ENGINE-OWNED WAVE (r360 bm-c freeze): bm-c\'s\n'
           '    # TWENTY-SECOND owned per machine-derive (engine_owner==bm-c\n'
           '    # rows 21 + candidate). Wave 68 = first free number after the\n'
           '    # registered W67 row (seat = the freeze commit itself per\n'
           '    # r511 table-tail lock -- engine waves have no claim face;\n'
           '    # same-window MSG cross-notice). W1..W63 finalizes ALL\n'
           '    # LANDED (net head 503,148, K=136,520, bm-c r358); W64 bm-a\n'
           '    # (burn in flight) + W65 bm-b (burned 12/12) + W66 bm-c\n'
           '    # (burned 12/12) + W67 bm-b (burn in flight) = FOUR in-flight\n'
           '    # upstream seats at this freeze (finalize chain-pending\n'
           '    # FAIL-CLOSED r307). A-side ARITHMETIC CONTINUATION from\n'
           '    # the W67 row tail, no skip: A 179_004..181_003\n'
           '    # (= W67 A end 179_003 + 1, CLEAN). B-side FORCED-SKIP\n'
           '    # family, CHAINED window-step reading = the W63 REGISTERED\n'
           '    # in-canon face (r566 ruling family: the registered face\n'
           '    # governs): arithmetic 50_401..50_600 REFUSED by\n'
           '    # SEED_REGISTRY cta_p2_noau=50_500 (MID-window hit;\n'
           '    # refusal machine-proved at leg1-B -- the skip is forced,\n'
           '    # not a free pick, r307 W26 precedent) -> first clean\n'
           '    # chained window 50_601..50_800. FORK DISCLOSURE: the\n'
           '    # W67 row W68+ prose projection said 50_501..50_700\n'
           '    # (restart-at-hit+1 reading, self-tagged "re-verify at\n'
           '    # W68 prereg"); r335 law: projections are machine-re-derived\n'
           '    # never prose-transcribed -- both candidate windows are\n'
           '    # clean vs everything, zero disjointness difference;\n'
           '    # escalated to HQ-FEEDBACK for a pinned sec.4 skip-semantics\n'
           '    # line. Machine-verified at prereg time\n'
           '    # (results/_r360bmc_w68_probe.py draft-window derive +\n'
           '    # results/_r360bmc_w68_band_gate.py ADMIT receipt vs the\n'
           '    # 66-row pre-W68 table + live SEED_REGISTRY values + probe\n'
           '    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin\n'
           '    # slot vacancy machine-checked). NOT a re-pick (R250: W68\n'
           '    # bands were never assigned).\n'
           '    68: {"a": (179_004, 181_003), "b_exit": (50_601, 50_800),\n'
           '         "engine_owner": "bm-c"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[68] landed (anchor=W67 row, insert)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[68] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '68: {"batch": "PERPETUAL-N1-W68"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('"shard_subdir": "n1_w67", "out_name": "n1_w67_results.json",\n'
          '                            "engine_owner": "bm-b"},\n'
          '                       }')
    NEW2 = ('"shard_subdir": "n1_w67", "out_name": "n1_w67_results.json",\n'
            '                            "engine_owner": "bm-b"},\n'
            '                       68: {"batch": "PERPETUAL-N1-W68",\n'
            '                            "prereg": ("research/PERPETUAL_N1_W68_PREREG.md (wave-level frozen "\n'
            '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
            '                                       "new seed bands only; FIFTY-SEVENTH ENGINE-OWNED WAVE, "\n'
            '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
            '                                       "(first-free-number law over the registered W67 row; "\n'
            '                                       "seat = freeze-commit lock per r511 tail-lock + same-window "\n'
            '                                       "MSG cross-notice), engine_owner=bm-c, wave 68 A-side "\n'
            '                                       "ARITHMETIC CONTINUATION no skip (179_004..181_003) + "\n'
            '                                       "B-side FORCED-SKIP family CHAINED window-step reading "\n'
            '                                       "= the W63 registered in-canon face (arithmetic "\n'
            '                                       "50_401..50_600 REFUSED by SEED_REGISTRY cta_p2_noau=50_500 "\n'
            '                                       "MID-window hit -> first clean chained window "\n'
            '                                       "50_601..50_800; the divergent restart reading "\n'
            '                                       "50_501..50_700 from the W67-row prose projection "\n'
            '                                       "disclosed and NOT adopted per r335 machine-derive law; "\n'
            '                                       "fork escalated to HQ-FEEDBACK for a pinned sec.4 "\n'
            '                                       "skip-semantics line); W1..W63 finalizes ALL "\n'
            '                                       "LANDED at this freeze (net chain head 503,148, K=136,520, "\n'
            '                                       "bm-c r358), W64 bm-a + W65 bm-b + W66 bm-c + W67 bm-b = "\n'
            '                                       "FOUR in-flight upstream seats (finalize chain-pending "\n'
            '                                       "FAIL-CLOSED r307)"),\n'
            '                            "a_seed_base": 179_004,        # law sec.4 W68 A: 179_004..181_003 (arithmetic continuation)\n'
            '                            "b_exit_seed_base": 50_601,   # law sec.4 W68 B: 50_601..50_800 (forced-skip, CHAINED reading per W63 registered face)\n'
            '                            "shard_subdir": "n1_w68", "out_name": "n1_w68_results.json",\n'
            '                            "engine_owner": "bm-c"},\n'
            '                       }')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[68] landed (anchor=W67 entry tail, insert)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W68 leg --------------
LEG68 = '''
    # --- W68 materializer face (r360 bm-c freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2):
    #     bm-c's TWENTY-SECOND owned per machine-derive (engine_owner==bm-c
    #     rows 21 + candidate); wave 68 = first free number after the
    #     registered W67 row (seat = the freeze commit itself per r511
    #     table-tail lock + same-window MSG cross-notice). W64 bm-a +
    #     W65 bm-b + W66 bm-c + W67 bm-b = FOUR in-flight upstream seats
    #     at this freeze (registered, finalize chain-pending
    #     FAIL-CLOSED r307).
    #     A-side ARITHMETIC CONTINUATION no skip (179_004..181_003) +
    #     B-side FORCED-SKIP family, CHAINED window-step reading = the
    #     W63 registered in-canon face (arithmetic 50_401..50_600
    #     REFUSED by SEED_REGISTRY cta_p2_noau=50_500 MID-window hit ->
    #     first clean chained window 50_601..50_800; the divergent
    #     restart reading 50_501..50_700 from the W67-row prose
    #     projection disclosed and NOT adopted per r335 law; ADMIT
    #     receipt results/_r360bmc_w68_band_gate.py; not a re-pick --
    #     R250) --
    _set_wave(68)
    try:
        assert WAVE_CONFIGS[68]["a_seed_base"] == pf.N1_BANDS[68]["a"][0], \\
            "W68 A band drift vs law mirror"
        assert WAVE_CONFIGS[68]["b_exit_seed_base"] == \\
            pf.N1_BANDS[68]["b_exit"][0], "W68 B band drift vs law mirror"
        assert WAVE_CONFIGS[68].get("engine_owner") == \\
            pf.N1_BANDS[68].get("engine_owner") == "bm-c", \\
            "W68 engine_owner drift (law mirror parity)"
        w68_a = {A_SEED_BASE + j for j in range(A_N)}
        w68_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w68_a & w68_b), "W68 A/B band overlap"
        assert not (w68_a & reg_ints) and not (w68_b & reg_ints), \\
            "W68 hits SEED_REGISTRY"
        for nm, band in (("A", w68_a), ("B", w68_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W68 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W68 {nm} hits W1"
            assert not (band & probes), f"W68 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W65/W66/W67
        # are REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly.
        assert pf.N1_BANDS[65] == {"a": (173_004, 175_003),
                                   "b_exit": (49_601, 49_800),
                                   "engine_owner": "bm-b"}, \\
            "registered W65 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[66] == {"a": (175_004, 177_003),
                                   "b_exit": (50_001, 50_200),
                                   "engine_owner": "bm-c"}, \\
            "registered W66 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[67] == {"a": (177_004, 179_003),
                                   "b_exit": (50_201, 50_400),
                                   "engine_owner": "bm-b"}, \\
            "registered W67 row parity drift (r307 two-state)"
        # prior-wave disjointness incl. W48..W67 (all registered; W64..W67
        # in flight -- coexist by band disjointness per r531).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67):
            assert not (w68_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W68 A hits W{wprev}"
            assert not (w68_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W68 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W68 clears it.
        n3r1_used68 = set(range(70_000, 70_006))
        assert not (w68_a & n3r1_used68) and not (w68_b & n3r1_used68), \\
            "W68 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w68_a & lfc_actual12) and not (w68_b & lfc_actual12), \\
            "W68 bands must clear the lfc actual draw range"
        assert not (w68_a & options_actual12) and \\
            not (w68_b & options_actual12), \\
            "W68 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W68 row, r360): A-side ARITHMETIC
        # CONTINUATION (179_004 = W67 A end 179_003 + 1); B-side
        # FORCED-SKIP family, CHAINED window-step reading = the W63
        # registered in-canon face -- the arithmetic window
        # 50_401..50_600 is REFUSED by cta_p2_noau=50_500 (MID hit),
        # first clean CHAINED window = 50_601..50_800.
        assert WAVE_CONFIGS[68]["a_seed_base"] == 179_004 == 179_003 + 1, \\
            "W68 A must start at the registered W67 A end + 1 " \\
            "(arithmetic continuation window 179_004..181_003 CLEAN -- " \\
            "no skip family)"
        assert 50_500 in reg_ints, \\
            "W68 B forced-skip basis: cta_p2_noau=50_500 must be in " \\
            "SEED_REGISTRY (the arithmetic window 50_401..50_600 refusal)"
        assert WAVE_CONFIGS[68]["b_exit_seed_base"] == 50_601 == 50_401 + 200, \\
            "W68 B must start one WHOLE window past the refused " \\
            "arithmetic window start (CHAINED window-step reading per " \\
            "the W63 registered in-canon face, r566 ruling family)"
        assert WAVE_CONFIGS[68]["b_exit_seed_base"] != 50_501, \\
            "W68 B must NOT be the restart-at-hit+1 reading (50_501) -- " \\
            "the W67-row prose projection diverged and was disclosed, " \\
            "NOT adopted (r335 machine-derive law)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W68-SHARD-0",
                                          "n1w68-0of12"), "W68 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W68-SHARD-11",
                                          "n1w68-11of12")
        assert SHARD_DIR.endswith("n1_w68") and OUT.endswith(
            "n1_w68_results.json"), "W68 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W68 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W68_PREREG.md")), \\
            "W68 per-wave prereg missing (materializer requirement)"
        # W68 finalize cumulative deps: W17..W63 outputs ALL PRESENT
        # (static landed seats; chain head 503,148 = W63 bm-c r358
        # K=136,520; W64 bm-a + W65 bm-b + W66 bm-c + W67 bm-b = FOUR
        # in-flight upstream seats -- the finalize merge loop derives
        # the wave set from registry keys at run time and stays
        # FAIL-CLOSED on the not-yet-finalized seats, r307 two-state
        # law).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                      43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
                      56, 57, 58, 59, 60, 61, 62, 63):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W68 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 68 (no 15; incl.
        # 48..67 -- all registered, W64..W67 finalize in flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 68) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
             65, 66, 67], \\
            "W68 prior-wave set must derive from registry keys (no 15, " \\
            "incl. 48..67)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W68 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG68.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W68 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 6th face) ------
t2c, eol2c = load(FP2)
if '+ W68 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('law sec.4 W67 row, r567 bm-b] "\n'
          '          "+ T-141 s2 ')
    SEG68 = ('law sec.4 W67 row, r567 bm-b] "\n'
             '          "+ W68 materializer face [same guard set, dep=W17..W63 "\n'
             '          "outputs ALL PRESENT (landed chain head 503,148, K=136,520), "\n'
             '          "W64 bm-a + W65 bm-b + W66 bm-c + W67 bm-b = FOUR in-flight "\n'
             '          "upstream seats (FAIL-CLOSED r307 at run time), FIFTY-SEVENTH "\n'
             '          "ENGINE-OWNED WAVE bm-c\'s TWENTY-SECOND owned claim per "\n'
             '          "machine-derive (engine_owner==bm-c rows 21 + candidate), "\n'
             '          "engine_owner=bm-c per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series (wave 68 = "\n'
             '          "first FREE number after the registered W67 row; seat = "\n'
             '          "freeze-commit lock r511 tail-lock + same-window MSG), "\n'
             '          "A-side ARITHMETIC CONTINUATION no skip (179_004..181_003) "\n'
             '          "+ B-side FORCED-SKIP family CHAINED window-step reading "\n'
             '          "= the W63 registered in-canon face (arithmetic "\n'
             '          "50_401..50_600 REFUSED by SEED_REGISTRY cta_p2_noau=50_500 "\n'
             '          "MID-window hit -> first clean chained window "\n'
             '          "50_601..50_800; divergent restart reading 50_501..50_700 "\n'
             '          "from the W67-row prose projection disclosed and NOT "\n'
             '          "adopted per r335 machine-derive law, fork escalated "\n'
             '          "to HQ-FEEDBACK for a pinned sec.4 skip-semantics line; "\n'
             '          "ADMIT receipt results/_r360bmc_w68_band_gate.py; not a "\n'
             '          "free pick -- R250), N3-R1 used-seed leg, probe-seed "\n'
             '          "cluster leg, law sec.4 W68 row, r360 bm-c] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG68, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W68 segment landed (insert after W67 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W68 row -------------------
ROW68 = """
- N1 波68（r360 bm-c 冻·prereg 时展行）：**第五十七枚引擎波·bm-c 第二十二枚自有波〔机面 derive：engine_owner==bm-c 行 21+本候选〕**·engine_owner=bm-c·SATURATION_ENGINE_LAW §1/§2 同 W10-W67 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-c 实例=**常驻架构 v0.4 per-tick 重读**——D-20261002-03 修法同窗实证（W59/W60/W61/W66 四波注册后常驻实例自见自燃=免杀重启）·点火验证唯一证据=产物增长面 r325 律·state queue 面不信】·【never-dry 供给律常设步·**零隔接力：本机上波 W66 已 12/12 烧毕交付 origin（finalize 链序候 W64/W65 落账）→波号 68=注册表 W67 行后首个自由号**（W67=bm-b r567 同窗注册·烧录在飞·席位公示 MSG-20261002-0945-bmb；W68 号位无人公示·本机冻结前 fetch 实核表尾时 W68 号位净空·origin 侧 vacancy 机验）·**席位=冻结 commit 本身即锁**（r511 表尾锁·引擎波无 claim 面=表格行就是唯一锁）+同窗 MSG 交叉通知】·**带位=A 面算术续带零跳位+B 面被迫跳位族（连锁跳位读法=W63 在册面正典先例·r535 机闸 derive 律·r307 W26 跳位被迫性先例）**：W67 行 W68+ 警示投影 **A 179_004..181_003 CLEAN／B 50_401..50_600 REFUSED〔SEED_REGISTRY cta_p2_noau=50_500·窗口中位命中〕**（bm-b r567 冻结窗投影腿机证+本波 r360 bm-c gate 复核〔双机互证·r302 陈旧指针证伪律下本波机闸独立 derive 非 prose 转抄〕）→本波 **A-ext seed=179_004..181_003**（**A 面算术续带**==W67 A 尾 179_003+1·步长逐字·零跳位）·**B-ext exit seed=50_601..50_800**（**B 面被迫跳位族·连锁跳位读法**：算术窗 50_401..50_600 因 cta_p2_noau=50_500 中位命中拒收→按 W63 在册面先例〔r357 bm-c·leg2-B 连锁跳位逐位 49_201..49_400·r566 分叉裁定族「正典在册面照准」〕整窗步进至下一 200 连续净窗 **50_601..50_800**·**跳位语义分叉披露**：W67 行 W68+ 投影 prose 曾载「首净窗 50_501..50_700」〔越 hit 起窗读法·该投影自带「复核于 W68 prereg」保留条款〕——r335 律投影 prose 非权威面（净空/首净宣称必须机闸 derive）·本波机闸独立 derive 按在册正典先例取连锁读法·两读法候选窗均对全部已预留面净空零 disjoint 差异·分叉提 HQ-FEEDBACK 待法典 §4 钉死行·跳位被迫性=leg1-B 机证算术位必红〔50_500〕·非自由挑·R250：W68 带从未指派·测量面零结果可钓）·【机证净空——leg0 六十七键（66 注册行+候选）+leg0b W67 行 W68+ 警示 prose 在场校验+leg1-A 算术位 CLEAN+leg1-B 算术位中位拒收机证〔cta_p2_noau=50_500〕+leg2-A 首净窗==算术位+leg2-B 连锁跳位逐位〔50_601..50_800〕+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验·**MSG-0640 三修工具**（FIX-A 编辑前 origin-blob 等值断言+FIX-B 锚=最后注册行+行存活核查+FIX-C 推送前纯增量 diff 断言）〕·ADMIT 回执=results/_r360bmc_w68_band_gate.py·起草窗投影探针=results/_r360bmc_w68_probe.py·r360 bm-c 起草窗实跑】·扫描面=pre-W68 六十六行 N1 带表【含 W63 行 169_004..171_003/49_201..49_400〔bm-c r357·finalize 已落账 K=136,520·净账本链头 503,148·bm-c r358〕·W64 行 171_004..173_003/49_401..49_600〔bm-a r566·注册烧录在飞·finalize 未落账〕·W65 行 173_004..175_003/49_601..49_800〔bm-b r566·12/12 烧毕·finalize 未落账〕·W66 行 175_004..177_003/50_001..50_200〔bm-c r359·12/12 烧毕·finalize 未落账〕·W67 行 177_004..179_003/50_201..50_400〔bm-b r567·注册烧录在飞·finalize 未落账〕】·**四在飞上游席披露：本波 finalize 链序前置=W64+W65+W66+W67 四落账·FAIL-CLOSED r307 两态律**·带域不相交·W1 ext·v1 在用带·SEED_REGISTRY 全键（int 值全清·LOWAMP-P1/P2/P3 键 20.33M 域零交集）·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·lfc 实际流 30_000..30_099·options_wave2 实际流 63_000..63_049（leg-3e 实际流避让腿）·**W69+ 投影（带闸投影腿机证=results/_r360bmc_w68_probe.py·W69 prereg 照例带闸复核 r335 律）：A 181_004..183_003 CLEAN／B 50_801..51_000 REFUSED〔SEED_REGISTRY xstock_synth_null_a=51_000·窗口尾点命中〕→B 侧跳位族·尾点族两读法同解·首净窗 51_001..51_200（复核于 W69 prereg）**·prereg=PERPETUAL_N1_W68_PREREG.md 冻结〔S5 锚=W63 实测：merged mu −0.092648/W63-only mu −0.098792/sigma 0.239446/A-p95 0.3016/K-lift −0.0005·累计池投影 147,520（含 W64+W65+W66+W67 在飞 8,800）〕·burn 由本机常驻引擎 v0.4 per-tick 自燃·finalize=活链头 derive one-pass（r538 一过律）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce268\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW68.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W68 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    68: {"a": (179_004') == 1, 'FIX-B FAIL: W68 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W68"') == 1, 'FIX-B FAIL: W68 config not exactly once'
for w in (59, 60, 61, 62, 63, 64, 65, 66, 67):
    leg = 'W%d materializer face' % w
    assert n11.count(leg) == BASE_SIGS['w%dleg' % w], f'FIX-B FAIL: {leg} lost'
assert n11.count('W68 materializer face') == 2, \
    'FIX-B FAIL: W68 leg+summary must be exactly 2'
for w in range(48, 68):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce268\uff08') == 1, 'FIX-B FAIL: canon W68 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W68 added per face')

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
