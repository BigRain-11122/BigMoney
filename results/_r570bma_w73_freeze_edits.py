# -*- coding: utf-8 -*-
"""r570 bm-a W73 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r561/r566/r568 lineage).

FIX-A (origin-blob freshness): every tracked edit target must show zero
  deleted lines vs origin/main BEFORE any edit runs (r559 stale-base cure
  -- this very abort saved the W72 clobber this window, 9th intercept).
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W72, bm-b's);
  after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W73 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W73 = SIXTY-SECOND engine wave, bm-a's SEVENTEENTH owned per machine-derive
(engine_owner==bm-a rows 16 + candidate). Seat declared published=reserved
MSG-20261002-1036-bma (yield-receipt MSG, r518-1 law; r565 yield-then-
reoccupy after the W72 same-window collision yielded to bm-b c7babddec
first-land). W71 bm-c + W72 bm-b = TWO in-flight upstream seats at this
freeze (finalize chain-pending -> FAIL-CLOSED r307). BOTH SIDES ARITHMETIC
CONTINUATION zero skip: A 189_004..191_003 (== W72 A tail 189_003 + 1);
B 51_601..51_800 (== W72 B tail 51_600 + 1); single reading, no divergence
face (zero refusal points in either arithmetic window). ADMIT receipt
results/_r570bma_w73_band_gate.py.
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
                     f'origin/main -- checkout origin version first (r559 clobber cure)')
print('FIX-A: all 3 tracked edit targets show zero deletions vs origin/main (fresh base)')

# ---------------- survival signature baseline (FIX-B) ------------------------
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20,
             21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
             37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52,
             53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68,
             69, 70, 71, 72]
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in
       (58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in (48, 49, 50, 51, 52, 53, 54, 55, 56,
                                                    57, 58, 59, 60, 61, 62, 63, 64, 65,
                                                    66, 67, 68, 69, 70, 71, 72)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[73] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '73: {"a": (189_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    72: {"a": (187_004, 189_003), "b_exit": (51_401, 51_600),\n'
          '         "engine_owner": "bm-b"},\n'
          '}\n')
    NEW = ('    72: {"a": (187_004, 189_003), "b_exit": (51_401, 51_600),\n'
           '         "engine_owner": "bm-b"},\n'
           '    # SIXTY-SECOND ENGINE-OWNED WAVE (r570 bm-a freeze): bm-a\'s\n'
           '    # seventeenth owned per machine-derive (engine_owner==bm-a\n'
           '    # rows 16 + candidate). Wave 73 = next free number after the\n'
           '    # registered W72 row (seat declared published=reserved\n'
           '    # MSG-20261002-1036-bma, r518-1 law; r565 yield-then-reoccupy\n'
           '    # after the W72 same-window collision yielded to bm-b\n'
           '    # c7babddec first-land per r511 commit-order). W1..W70\n'
           '    # finalizes ALL LANDED (net head 518,548, K=151,920 --\n'
           '    # W70 bm-b r570); W71 bm-c + W72 bm-b = TWO in-flight\n'
           '    # upstream seats at this freeze (finalize chain-pending\n'
           '    # FAIL-CLOSED r307). BOTH SIDES ARITHMETIC CONTINUATION,\n'
           '    # zero skip: A 189_004..191_003 == W72 A end 189_003 + 1\n'
           '    # (CLEAN per the W72 row W73+ WARNING projection, machine\n'
           '    # re-derive r535 law -- dual-machine cross-check).\n'
           '    # B 51_601..51_800 == W72 B end 51_600 + 1 (CLEAN, single\n'
           '    # reading -- zero refusal points in either arithmetic\n'
           '    # window, no divergence face). ADMIT receipt\n'
           '    # results/_r570bma_w73_band_gate.py; NOT a re-pick (R250:\n'
           '    # W73 bands were never assigned).\n'
           '    73: {"a": (189_004, 191_003), "b_exit": (51_601, 51_800),\n'
           '         "engine_owner": "bm-a"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[73] landed (anchor=W72 row, insert)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[73] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '73: {"batch": "PERPETUAL-N1-W73"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w72", "out_name": "n1_w72_results.json",\n'
          '                            "engine_owner": "bm-b"},\n'
          '                       }')
    NEW2 = ('                            "shard_subdir": "n1_w72", "out_name": "n1_w72_results.json",\n'
            '                            "engine_owner": "bm-b"},\n'
            '                       73: {"batch": "PERPETUAL-N1-W73",\n'
            '                            "prereg": ("research/PERPETUAL_N1_W73_PREREG.md (wave-level frozen "\n'
            '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
            '                                       "new seed bands only; SIXTY-SECOND ENGINE-OWNED WAVE, "\n'
            '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
            '                                       "(first-free-number law over the registered W72 row; "\n'
            '                                       "seat published=reserved MSG-20261002-1036-bma; "\n'
            '                                       "r565 yield-then-reoccupy after the W72 same-window "\n'
            '                                       "collision yielded to bm-b c7babddec first-land per "\n'
            '                                       "r511 commit-order -- zero ignition zero push, "\n'
            '                                       "bitwise-identical ADMIT receipt = r530 family 9th "\n'
            '                                       "deterministic cross-validation), "\n'
            '                                       "engine_owner=bm-a, wave 73 BOTH SIDES ARITHMETIC "\n'
            '                                       "CONTINUATION no skip (A 189_004..191_003 / B 51_601..51_800 "\n'
            '                                       "machine-derived CLEAN == the W72 row W73+ WARNING "\n'
            '                                       "projection verbatim, dual-machine cross-check per "\n'
            '                                       "r302/r535 law; single reading no divergence face); "\n'
            '                                       "W1..W70 finalizes ALL LANDED at this freeze (net "\n'
            '                                       "chain head 518,548, K=151,920, bm-b r570), W71 bm-c "\n'
            '                                       "+ W72 bm-b = TWO in-flight upstream seats "\n'
            '                                       "(finalize chain-pending FAIL-CLOSED r307)"),\n'
            '                            "a_seed_base": 189_004,        # law sec.4 W73 A: 189_004..191_003 (arithmetic continuation)\n'
            '                            "b_exit_seed_base": 51_601,   # law sec.4 W73 B: 51_601..51_800 (arithmetic continuation)\n'
            '                            "shard_subdir": "n1_w73", "out_name": "n1_w73_results.json",\n'
            '                            "engine_owner": "bm-a"},\n'
            '                       }')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[73] landed (anchor=W72 entry tail, insert)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W73 leg --------------
LEG73 = '''
    # --- W73 materializer face (r570 bm-a freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2; r565
    #     yield-then-reoccupy after the W72 same-window collision):
    #     bm-a's seventeenth owned per machine-derive (engine_owner==bm-a
    #     rows 16 + candidate); wave 73 = next free number after the
    #     registered W72 row (seat declared published=reserved
    #     MSG-20261002-1036-bma). W71 bm-c + W72 bm-b = TWO in-flight
    #     upstream seats at this freeze (finalize chain-pending
    #     FAIL-CLOSED r307). BOTH SIDES ARITHMETIC CONTINUATION no
    #     skip (A 189_004..191_003 = W72 A end 189_003 + 1 /
    #     B 51_601..51_800 = W72 B end 51_600 + 1; both CLEAN
    #     machine-derived == the W72 row W73+ WARNING projection
    #     verbatim, dual-machine cross-check; single reading no
    #     divergence face -- zero refusal points in either arithmetic
    #     window; ADMIT receipt results/_r570bma_w73_band_gate.py;
    #     not a re-pick -- R250: W73 bands were never assigned) --
    _set_wave(73)
    try:
        assert WAVE_CONFIGS[73]["a_seed_base"] == pf.N1_BANDS[73]["a"][0], \\
            "W73 A band drift vs law mirror"
        assert WAVE_CONFIGS[73]["b_exit_seed_base"] == \\
            pf.N1_BANDS[73]["b_exit"][0], "W73 B band drift vs law mirror"
        assert WAVE_CONFIGS[73].get("engine_owner") == \\
            pf.N1_BANDS[73].get("engine_owner") == "bm-a", \\
            "W73 engine_owner drift (law mirror parity)"
        w73_a = {A_SEED_BASE + j for j in range(A_N)}
        w73_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w73_a & w73_b), "W73 A/B band overlap"
        assert not (w73_a & reg_ints) and not (w73_b & reg_ints), \\
            "W73 hits SEED_REGISTRY"
        for nm, band in (("A", w73_a), ("B", w73_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W73 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W73 {nm} hits W1"
            assert not (band & probes), f"W73 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W68..W72
        # are REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly.
        assert pf.N1_BANDS[68] == {"a": (179_004, 181_003),
                                   "b_exit": (50_501, 50_700),
                                   "engine_owner": "bm-a"}, \\
            "registered W68 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[69] == {"a": (181_004, 183_003),
                                   "b_exit": (50_701, 50_900),
                                   "engine_owner": "bm-c"}, \\
            "registered W69 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[70] == {"a": (183_004, 185_003),
                                   "b_exit": (51_001, 51_200),
                                   "engine_owner": "bm-b"}, \\
            "registered W70 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[71] == {"a": (185_004, 187_003),
                                   "b_exit": (51_201, 51_400),
                                   "engine_owner": "bm-c"}, \\
            "registered W71 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[72] == {"a": (187_004, 189_003),
                                   "b_exit": (51_401, 51_600),
                                   "engine_owner": "bm-b"}, \\
            "registered W72 row parity drift (r307 two-state)"
        # prior-wave disjointness incl. W48..W72 (all registered; W71
        # + W72 in flight -- coexist by band disjointness per r531).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                      70, 71, 72):
            assert not (w73_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W73 A hits W{wprev}"
            assert not (w73_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W73 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W73 clears it.
        n3r1_used73 = set(range(70_000, 70_006))
        assert not (w73_a & n3r1_used73) and not (w73_b & n3r1_used73), \\
            "W73 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w73_a & lfc_actual12) and not (w73_b & lfc_actual12), \\
            "W73 bands must clear the lfc actual draw range"
        assert not (w73_a & options_actual12) and \\
            not (w73_b & options_actual12), \\
            "W73 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W73 row, r570): BOTH SIDES ARITHMETIC
        # CONTINUATION (zero skip, single reading -- the arithmetic
        # windows are CLEAN, no refusal-facts identity face).
        assert WAVE_CONFIGS[73]["a_seed_base"] == 189_004 == 189_003 + 1, \\
            "W73 A must start at the registered W72 A end + 1 " \\
            "(arithmetic continuation window 189_004..191_003 CLEAN -- " \\
            "no skip family)"
        assert WAVE_CONFIGS[73]["b_exit_seed_base"] == 51_601 == 51_600 + 1, \\
            "W73 B must start at the registered W72 B end + 1 " \\
            "(arithmetic continuation window 51_601..51_800 CLEAN)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W73-SHARD-0",
                                          "n1w73-0of12"), "W73 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W73-SHARD-11",
                                          "n1w73-11of12")
        assert SHARD_DIR.endswith("n1_w73") and OUT.endswith(
            "n1_w73_results.json"), "W73 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                      70, 71, 72):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W73 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W73_PREREG.md")), \\
            "W73 per-wave prereg missing (materializer requirement)"
        # W73 finalize cumulative deps: W17..W70 outputs ALL PRESENT
        # (static landed seats; chain head 518,548 = W70 bm-b r570
        # K=151,920; W71 bm-c + W72 bm-b = TWO in-flight upstream
        # seats -- the finalize merge loop derives the wave set from
        # registry keys at run time and stays FAIL-CLOSED on the
        # not-yet-finalized W71/W72 seats, r307 two-state law).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                      43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
                      56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68,
                      69, 70):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W73 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 73 (no 15; incl.
        # 48..72 -- all registered, W71/W72 finalize in flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 73) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
             65, 66, 67, 68, 69, 70, 71, 72], \\
            "W73 prior-wave set must derive from registry keys (no 15, " \\
            "incl. 48..72)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W73 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG73.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W73 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 5th face) ------
t2c, eol2c = load(FP2)
if '+ W73 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('cluster leg, law sec.4 W72 row, r570 bm-b] "\n'
          '          "+ T-141 s2 ')
    SEG73 = ('cluster leg, law sec.4 W72 row, r570 bm-b] "\n'
             '          "+ W73 materializer face [same guard set, dep=W17..W70 "\n'
             '          "outputs ALL PRESENT (landed chain head 518,548, "\n'
             '          "K=151,920, bm-b r570), W71 bm-c + W72 bm-b = TWO "\n'
             '          "in-flight upstream seats (FAIL-CLOSED r307 at run "\n'
             '          "time), SIXTY-SECOND ENGINE-OWNED WAVE bm-a\'s "\n'
             '          "seventeenth owned claim per machine-derive "\n'
             '          "(engine_owner==bm-a rows 16 + candidate), "\n'
             '          "engine_owner=bm-a per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series "\n'
             '          "(wave 73 = first FREE number after the registered "\n'
             '          "W72 row; seat declared published=reserved "\n'
             '          "MSG-20261002-1036-bma; r565 yield-then-reoccupy "\n'
             '          "after the W72 same-window collision yielded to bm-b "\n'
             '          "c7babddec first-land per r511 commit-order -- zero "\n'
             '          "ignition zero push, bitwise-identical ADMIT "\n'
             '          "receipt = r530 family 9th deterministic "\n'
             '          "cross-validation), BOTH SIDES ARITHMETIC "\n'
             '          "CONTINUATION from the W72 tail no skip (A "\n'
             '          "189_004..191_003 / B 51_601..51_800 both CLEAN "\n'
             '          "machine-derived == the W72 row W73+ WARNING "\n'
             '          "projection verbatim, dual-machine cross-check per "\n'
             '          "r302/r535 law; single reading no divergence face; "\n'
             '          "ADMIT receipt results/_r570bma_w73_band_gate.py; "\n'
             '          "not a free pick -- R250), N3-R1 used-seed leg, "\n'
             '          "probe-seed cluster leg, law sec.4 W73 row, "\n'
             '          "r570 bm-a] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG73, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W73 segment landed (insert after W72 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W73 row -------------------
ROW73 = """
- N1 波73（r570 bm-a 冻·prereg 时展行）：**第六十二枚引擎波·bm-a 第十七枚自有波〔机面 derive：engine_owner==bm-a 行 16+本候选〕**·engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 同 W10-W72 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-a 实例=tick 架构 r535 律——冻结编辑落工作树后下一 tick 新进程重读活树自见新行=免杀重启免做·W44/W45/W48/W54/W57/W62/W64/W68 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 73=注册表 W72 行后首个自由号**（W72 席位=MSG-20261002-1028-bmb published=reserved 本机让路不碰·**r565 让路-再占位律**——W72 同窗撞面 bm-b c7babddec 先落（r511 commit 时序硬裁定）·本机纯草稿零烧录零推送=零成本让路〔FIX-A 拦截防顶替 r560 律第 9 例成功拦截·n1_w72 本机零点火实证〕·带位逐位互证=r530 族第 9 例）·席位公示=MSG-20261002-1036-bma（published=reserved r518-① 律·W48/W49/W55/W62/W65/W67/W68/W69/W70/W71/W72 先例·让路回执 MSG 内同窗再占位）·r511 表尾锁例冻结前 fetch 实核表尾时 W73 号位净空·origin 侧 vacancy 机验】·**带位=双面算术续带零跳位（r535 机闸 derive 律）**：W72 行 W73+ 警示投影 **A 189_004..191_003／B 51_601..51_800 双 CLEAN**（bm-b r570 冻结窗 gate 投影腿机证+本波 r570 bm-a gate 复核逐字同〔双机互证·且与本机 W72 gate 回执 W73+ 投影腿逐位同=双投影交叉验证·r302 陈旧指针证伪律下本波机闸独立 derive 非 prose 转抄〕）→本波 **A-ext seed=189_004..191_003**（==W72 A 尾 189_003+1·步长逐字·A 面算术续带零跳位）·**B-ext exit seed=51_601..51_800**（==W72 B 尾 51_600+1·步长逐字·B 面算术续带零跳位·双侧零跳位·单读法零分叉〔双侧算术窗零拒绝点·跳位语义分叉面 F-20261002-03 不触发〕·R250：W73 带从未指派·测量面零结果可钓）·【机证净空——leg0 七十键（70 注册行+候选）+leg0b W72 行 W73+ 警示 prose 在场校验+leg1-A/leg1-B 算术位 CLEAN 机证+leg2 双侧首净窗==算术==候选+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验·**MSG-0640 三修工具**（FIX-A 编辑前 origin-blob 等值断言+FIX-B 锚=最后注册行+行存活核查+FIX-C 推送前纯增量 diff 断言）〕·ADMIT 回执=results/_r570bma_w73_band_gate.py·r570 bm-a 起草窗实跑】·扫描面=pre-W73 七十行 N1 带表【含 **W69 行 181_004..183_003/50_701..50_900〔bm-c r360·finalize 已落账 r361·K=149,720〕**·**W70 行 183_004..185_003/51_001..51_200〔bm-b r568·finalize 已落账 r570·K=151,720·净账本链头 518,548〕**·**W71 行 185_004..187_003/51_201..51_400〔bm-c r361·12/12 烧毕·finalize 未落账（已被 W70 落账解锁）〕**·**W72 行 187_004..189_003/51_401..51_600〔bm-b r570·烧录在飞 4/12+·finalize 未落账〕**】·**两在飞上游席披露：本波 finalize 链序前置=W71+W72 两落账·FAIL-CLOSED r307 两态律**·带域不相交·W1 ext·v1 在用带·SEED_REGISTRY 全键（160 int 值全清·LOWAMP-P1/P2/P3 键 20.33M 域零交集）·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·lfc 实际流 30_000..30_099·options_wave2 实际流 63_000..63_049（leg-3e 实际流避让腿）·**W74+ 投影（带闸投影腿机证·W74 prereg 照例带闸复核 r335 律）：A 191_004..193_003 CLEAN／B 51_801..52_000 REFUSED**〔SEED_REGISTRY **xstock_synth_null_b=52_000** 端点单点红（命中位=窗上边缘·r307 W5 跳位被迫性先例族）→W74 冻结窗**被迫跳位**·越 hit 起窗 52_001..52_200 与窗步链跳 52_001..52_200 两读法恒同=零分叉（r566 单点/尾点拒绝先例族·不同于 W63 双点中位分叉面）·本波 gate 投影腿机证〕"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce273\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW73.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W73 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    73: {"a": (189_004') == 1, 'FIX-B FAIL: W73 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W73"') == 1, 'FIX-B FAIL: W73 config not exactly once'
for w in (58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W73 materializer face') == 2, \
    'FIX-B FAIL: W73 leg+summary must be exactly 2'
for w in (48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
          64, 65, 66, 67, 68, 69, 70, 71, 72):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce273\uff08') == 1, 'FIX-B FAIL: canon W73 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W73 added per face')

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
