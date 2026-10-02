# -*- coding: utf-8 -*-
"""r359 bm-c W66 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r561 lineage).

FIX-A (origin-blob freshness): every tracked edit target must be content-equal
  to origin/main BEFORE any edit runs. Kills the r559 stale-base clobber.
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W65, bm-b's),
  and after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W66 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W66 = FIFTY-FIFTH engine wave, bm-c's TWENTY-FIRST owned per machine-derive
(engine_owner==bm-c rows 20 + candidate). Seat = the freeze commit itself
(r511 table-tail lock; engine waves have no claim face -- the table row IS
the only lock) + same-window MSG cross-notice. Wave 66 = first free number
over the registered W65 row (bm-b r566, burn in flight 4/12). W64 bm-a +
W65 bm-b = TWO in-flight upstream seats at this freeze (finalize
chain-pending, FAIL-CLOSED r307). A-side ARITHMETIC CONTINUATION zero skip
(175_004..177_003); B-side FORCED-SKIP family (arithmetic 49_801..50_000
REFUSED by SEED_REGISTRY cta_p1=50_000 tail hit -> first clean window
50_001..50_200; hit+1 restart == window-step chain, both readings coincide).
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
           '    # FIFTY-FIFTH ENGINE-OWNED WAVE (r359 bm-c freeze): bm-c\'s\n'
           '    # TWENTY-FIRST owned per machine-derive (engine_owner==bm-c\n'
           '    # rows 20 + candidate). Wave 66 = first free number after the\n'
           '    # registered W65 row (seat = the freeze commit itself per\n'
           '    # r511 table-tail lock -- engine waves have no claim face;\n'
           '    # same-window MSG cross-notice). W1..W63 finalizes ALL\n'
           '    # LANDED (net head 503,148, K=136,520, bm-c r358); W64 bm-a\n'
           '    # + W65 bm-b = TWO in-flight upstream seats at this freeze\n'
           '    # (registered, burn in flight, finalize chain-pending\n'
           '    # FAIL-CLOSED r307). A-side ARITHMETIC CONTINUATION\n'
           '    # from the W65 row tail, no skip: A 175_004..177_003\n'
           '    # (== W65 A end 175_003 + 1). B-side FORCED-SKIP family:\n'
           '    # the arithmetic window 49_801..50_000 is REFUSED by\n'
           '    # SEED_REGISTRY cta_p1=50_000 (window-TAIL hit; refusal\n'
           '    # machine-proved at leg1-B -- the skip is forced, not a\n'
           '    # free pick, r307 W26 precedent) -> first clean window\n'
           '    # 50_001..50_200 (hit+1 restart == window-step chain at a\n'
           '    # tail hit; r566 W63 fork semantics do not diverge).\n'
           '    # Machine-verified at prereg time\n'
           '    # (results/_r359bmc_w66_band_gate.py ADMIT receipt vs the\n'
           '    # 63-row pre-W66 table + live SEED_REGISTRY values + probe\n'
           '    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin\n'
           '    # slot vacancy machine-checked). NOT a re-pick (R250: W66\n'
           '    # bands were never assigned).\n'
           '    66: {"a": (175_004, 177_003), "b_exit": (50_001, 50_200),\n'
           '         "engine_owner": "bm-c"},\n'
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
            '                                       "seat = freeze-commit lock per r511 tail-lock + same-window "\n'
            '                                       "MSG cross-notice), engine_owner=bm-c, wave 66 A-side "\n'
            '                                       "ARITHMETIC CONTINUATION no skip (175_004..177_003) + "\n'
            '                                       "B-side FORCED-SKIP family (arithmetic 49_801..50_000 "\n'
            '                                       "REFUSED by SEED_REGISTRY cta_p1=50_000 tail hit -> first "\n'
            '                                       "clean window 50_001..50_200, hit+1 restart == window-step "\n'
            '                                       "chain, both readings coincide); W1..W63 finalizes ALL "\n'
            '                                       "LANDED at this freeze (net chain head 503,148, K=136,520, "\n'
            '                                       "bm-c r358), W64 bm-a + W65 bm-b = TWO in-flight upstream "\n'
            '                                       "seats (registered, finalize chain-pending FAIL-CLOSED "\n'
            '                                       "r307)"),\n'
            '                            "a_seed_base": 175_004,        # law sec.4 W66 A: 175_004..177_003 (arithmetic continuation)\n'
            '                            "b_exit_seed_base": 50_001,   # law sec.4 W66 B: 50_001..50_200 (forced-skip family, cta_p1 tail hit)\n'
            '                            "shard_subdir": "n1_w66", "out_name": "n1_w66_results.json",\n'
            '                            "engine_owner": "bm-c"},\n'
            '                       }')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[66] landed (anchor=W65 entry tail, insert)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W66 leg --------------
LEG66 = '''
    # --- W66 materializer face (r359 bm-c freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2):
    #     bm-c's TWENTY-FIRST owned per machine-derive (engine_owner==bm-c
    #     rows 20 + candidate); wave 66 = first free number after the
    #     registered W65 row (seat = the freeze commit itself per r511
    #     table-tail lock + same-window MSG cross-notice). W64 bm-a +
    #     W65 bm-b = TWO in-flight upstream seats at this freeze
    #     (registered, finalize chain-pending FAIL-CLOSED r307).
    #     A-side ARITHMETIC CONTINUATION no skip (175_004..177_003) +
    #     B-side FORCED-SKIP family (arithmetic 49_801..50_000 REFUSED
    #     by SEED_REGISTRY cta_p1=50_000 tail hit -> first clean window
    #     50_001..50_200; hit+1 restart == window-step chain, both
    #     readings coincide; ADMIT receipt
    #     results/_r359bmc_w66_band_gate.py; not a re-pick -- R250) --
    _set_wave(66)
    try:
        assert WAVE_CONFIGS[66]["a_seed_base"] == pf.N1_BANDS[66]["a"][0], \\
            "W66 A band drift vs law mirror"
        assert WAVE_CONFIGS[66]["b_exit_seed_base"] == \\
            pf.N1_BANDS[66]["b_exit"][0], "W66 B band drift vs law mirror"
        assert WAVE_CONFIGS[66].get("engine_owner") == \\
            pf.N1_BANDS[66].get("engine_owner") == "bm-c", \\
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
        # registered declared-band parity (r307 two-state): W62/W63/W64/W65
        # are REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly.
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
        # band facts (law sec.4 W66 row, r359): A-side ARITHMETIC
        # CONTINUATION (175_004 = W65 A end 175_003 + 1); B-side
        # FORCED-SKIP family -- the arithmetic window 49_801..50_000 is
        # REFUSED by cta_p1=50_000 (tail hit), first clean = 50_001..50_200.
        assert WAVE_CONFIGS[66]["a_seed_base"] == 175_004 == 175_003 + 1, \\
            "W66 A must start at the registered W65 A end + 1 " \\
            "(arithmetic continuation window 175_004..177_003 CLEAN -- " \\
            "no skip family)"
        assert 50_000 in reg_ints, \\
            "W66 B forced-skip basis: cta_p1=50_000 must be in " \\
            "SEED_REGISTRY (the arithmetic window 49_801..50_000 refusal)"
        assert WAVE_CONFIGS[66]["b_exit_seed_base"] == 50_001 == 50_000 + 1, \\
            "W66 B must start at hit+1 (forced-skip family: arithmetic " \\
            "49_801..50_000 refused, first clean window 50_001..50_200; " \\
            "hit+1 restart == window-step chain at the tail hit)"
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
        # seats, r307 two-state law).
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

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 6th face) ------
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
             '          "WAVE bm-c\'s TWENTY-FIRST owned claim per machine-derive "\n'
             '          "(engine_owner==bm-c rows 20 + candidate), "\n'
             '          "engine_owner=bm-c per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series (wave 66 = "\n'
             '          "first FREE number after the registered W65 row; seat = "\n'
             '          "freeze-commit lock r511 tail-lock + same-window MSG), "\n'
             '          "A-side ARITHMETIC CONTINUATION no skip (175_004..177_003) "\n'
             '          "+ B-side FORCED-SKIP family (arithmetic 49_801..50_000 "\n'
             '          "REFUSED by SEED_REGISTRY cta_p1=50_000 tail hit -> first "\n'
             '          "clean window 50_001..50_200, hit+1 restart == window-step "\n'
             '          "chain, both readings coincide; ADMIT receipt "\n'
             '          "results/_r359bmc_w66_band_gate.py; not a free pick -- "\n'
             '          "R250), N3-R1 used-seed leg, probe-seed cluster leg, "\n'
             '          "law sec.4 W66 row, r359 bm-c] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG66, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W66 segment landed (insert after W65 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W66 row -------------------
ROW66 = """
- N1 波66（r359 bm-c 冻·prereg 时展行）：**第五十五枚引擎波·bm-c 第二十一枚自有波〔机面 derive：engine_owner==bm-c 行 20+本候选〕**·engine_owner=bm-c·SATURATION_ENGINE_LAW §1/§2 同 W10-W65 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-c 实例=**常驻架构 v0.4 per-tick 重读**——D-20261002-03 修法同窗实证（W59/W60/W61 三波注册后常驻实例自见自燃=免杀重启）·点火验证唯一证据=产物增长面 r325 律·state queue 面不信】·【never-dry 供给律常设步·**零隔接力：本机 r358 规划 W65 席位、bm-b r566 同窗占 W65（MSG-20261002-0919-bmb 席位公示 published=reserved）→本机顺延**波号 66=注册表 W65 行后首个自由号**·席位=**冻结 commit 本身即锁**（r511 表尾锁·引擎波无 claim 面=表格行就是唯一锁）+同窗 MSG 交叉通知·r511 表尾锁例冻结前 fetch 实核表尾时 W66 号位净空·origin 侧 vacancy 机验】·**带位=A 面算术续带零跳位+B 面被迫跳位族（r535 机闸 derive 律·r307 W26 跳位被迫性先例）**：W65 行 W66+ 警示投影 **A 175_004..177_003 CLEAN／B 49_801..50_000 REFUSED〔SEED_REGISTRY cta_p1=50_000·窗口尾点命中〕**（bm-b r566 冻结窗 gate 投影腿机证+本波 r359 bm-c gate 复核逐字同〔双机互证·r302 陈旧指针证伪律下本波机闸独立 derive 非 prose 转抄〕）→本波 **A-ext seed=175_004..177_003**（**A 面算术续带**==W65 A 尾 175_003+1·步长逐字·零跳位）·**B-ext exit seed=50_001..50_200**（**B 面被迫跳位族**：算术窗 49_801..50_000 因 cta_p1=50_000 拒收→首净窗 **50_001..50_200**〔越 hit 起窗=hit+1 重启·r335 W26 先例族；hit 在窗尾=hit+1 重启与窗步链跳两读法逐位同解·r566 W63 分叉面不适用〕·跳位被迫性=leg1-B 机证算术位必红·非自由挑·R250：W66 带从未指派·测量面零结果可钓）·【机证净空——leg0 六十五键（64 注册行+候选）+leg0b W65 行 W66+ 警示 prose 在场校验+leg1-A 算术位 CLEAN／leg1-B 算术位 REFUSED〔cta_p1 尾点〕机证+leg2 A 侧首净窗==算术位／B 侧首净窗==hit+1 重启两读法同解+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验·**MSG-0640 三修工具**（FIX-A 编辑前 origin-blob 等值断言+FIX-B 锚=最后注册行+行存活核查+FIX-C 推送前纯增量 diff 断言）〕·ADMIT 回执=results/_r359bmc_w66_band_gate.py·r359 bm-c 起草窗实跑】·扫描面=pre-W66 六十四行 N1 带表【含 W62 行 167_004..169_003/48_601..48_800〔bm-a r565·finalize 已落账 K=134,320〕·**W63 行 169_004..171_003/49_201..49_400〔bm-c r357·finalize 已落账 K=136,520·净账本链头 503,148·bm-c r358〕**·**W64 行 171_004..173_003/49_401..49_600〔bm-a r566·注册在飞·finalize 未落账〕**·**W65 行 173_004..175_003/49_601..49_800〔bm-b r566·注册在飞·finalize 未落账〕**】·**两在飞上游席披露：本波 finalize 链序前置=W64+W65 双落账·FAIL-CLOSED r307 两态律**·带域不相交·W1 ext·v1 在用带·SEED_REGISTRY 全键（int 值全清·LOWAMP-P1/P2/P3 键 20.33M 域零交集）·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·lfc 实际流 30_000..30_099·options_wave2 实际流 63_000..63_049（leg-3e 实际流避让腿）·**W67+ 投影警示（r359 bm-c 探针机证=results/_r359bmc_w67_probe.py）：A 算术位 177_004..179_003 CLEAN／B 算术位 50_201..50_400 CLEAN（W66 尾后 +2_000/+200 顺延）——冻结前必跑带闸 derive 复核（净空宣称须机闸 derive 非 prose 转抄·r335 律）**。
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
