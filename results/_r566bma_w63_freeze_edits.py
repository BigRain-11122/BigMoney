# -*- coding: utf-8 -*-
"""r566 bm-a W63 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r561 lineage).

FIX-A (origin-blob freshness): every tracked edit target must be content-equal
  to origin/main BEFORE any edit runs. Kills the r559 stale-base clobber.
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W62, bm-a's),
  and after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W63 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W63 = FIFTY-SECOND engine wave, bm-a's fifteenth owned per machine-derive
(engine_owner==bm-a rows 14 + candidate). Seat declared published=reserved
(MSG-20261002-0843-bma, r518-1 law). W1..W62 finalizes ALL LANDED at this
freeze (net chain head 500,948, K=134,320) -- ZERO in-flight upstream seats,
chain fully caught up. B-side = FORCED-SKIP JUMP (r335 W26 past-hit
semantics) past SEED_REGISTRY 49_000 -> 49_100, first clean 49_101..49_300.
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
                     f'(r559 clobber cure; pure insertions from this tool\'s own '
                     f'idempotent edits are the only legal pre-state)')
print('FIX-A: all 3 tracked edit targets show zero deletions vs origin/main (fresh base)')

# ---------------- survival signature baseline (FIX-B) ------------------------
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20,
             21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
             37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52,
             53, 54, 55, 56, 57, 58, 59, 60, 61, 62]
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {'w58leg': n1_0.count('W58 materializer face'),
       'w59leg': n1_0.count('W59 materializer face'),
       'w60leg': n1_0.count('W60 materializer face'),
       'w61leg': n1_0.count('W61 materializer face'),
       'w62leg': n1_0.count('W62 materializer face')}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in (48, 49, 50, 51, 52, 53, 54, 55, 56,
                                                    57, 58, 59, 60, 61, 62)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[63] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '63: {"a": (169_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    62: {"a": (167_004, 169_003), "b_exit": (48_601, 48_800),\n'
          '         "engine_owner": "bm-a"},\n'
          '}\n')
    NEW = ('    62: {"a": (167_004, 169_003), "b_exit": (48_601, 48_800),\n'
           '         "engine_owner": "bm-a"},\n'
           '    # FIFTY-SECOND ENGINE-OWNED WAVE (r566 bm-a freeze): bm-a\'s\n'
           '    # fifteenth owned per machine-derive (engine_owner==bm-a\n'
           '    # rows 14 + candidate). Wave 63 = next free number after the\n'
           '    # registered W62 row (seat declared published=reserved\n'
           '    # MSG-20261002-0843-bma, r518-1 law; W1..W62 finalizes ALL\n'
           '    # LANDED at this freeze -- zero in-flight upstream seats,\n'
           '    # chain fully caught up, net head 500,948 K=134,320).\n'
           '    # A = ARITHMETIC CONTINUATION from the W62 row tail, no skip\n'
           '    # (169_004..171_003 = W62 A end 169_003 + 1, CLEAN per the\n'
           '    # W62 row W63+ WARNING projections machine re-derive,\n'
           '    # r535 law). B = FORCED-SKIP JUMP past the two-step refusal\n'
           '    # (arithmetic 48_801..49_000 REFUSED [SEED_REGISTRY\n'
           '    # p4_ext_tilt_q=49_000] -> 49_001..49_200 REFUSED\n'
           '    # [p4_ext_tilt_d20=49_100] -> first clean 49_101..49_300\n'
           '    # past-the-hit-point window, r335 W26 semantics;\n'
           '    # W5/W6/W8/W12/W17/W26/W39-B/W43-B/W47-B/W51-B skip family).\n'
           '    # Machine-verified at prereg time\n'
           '    # (results/_r566bma_w63_band_gate.py ADMIT receipt vs the\n'
           '    # 61-row pre-W63 table + live SEED_REGISTRY values + probe\n'
           '    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin\n'
           '    # slot vacancy machine-checked). NOT a re-pick (R250: W63\n'
           '    # bands were never assigned).\n'
           '    63: {"a": (169_004, 171_003), "b_exit": (49_101, 49_300),\n'
           '         "engine_owner": "bm-a"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[63] landed (anchor=W62 row, insert)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[63] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '63: {"batch": "PERPETUAL-N1-W63"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w62", "out_name": "n1_w62_results.json",\n'
          '                            "engine_owner": "bm-a"},\n'
          '                       }')
    NEW2 = ('                            "shard_subdir": "n1_w62", "out_name": "n1_w62_results.json",\n'
            '                            "engine_owner": "bm-a"},\n'
            '                       63: {"batch": "PERPETUAL-N1-W63",\n'
            '                            "prereg": ("research/PERPETUAL_N1_W63_PREREG.md (wave-level frozen "\n'
            '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
            '                                       "new seed bands only; FIFTY-SECOND ENGINE-OWNED WAVE, "\n'
            '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
            '                                       "(first-free-number law over the registered W62 row; "\n'
            '                                       "seat declared published=reserved MSG-20261002-0843-bma), "\n'
            '                                       "engine_owner=bm-a, wave 63 A-side ARITHMETIC "\n'
            '                                       "CONTINUATION no skip (A 169_004..171_003 machine-derived "\n'
            '                                       "CLEAN == the W62 row W63+ published projection verbatim) "\n'
            '                                       "+ B-side FORCED-SKIP JUMP past the two-step refusal "\n'
            '                                       "(arithmetic 48_801..49_000 REFUSED [SEED_REGISTRY "\n'
            '                                       "p4_ext_tilt_q=49_000] -> 49_001..49_200 REFUSED "\n'
            '                                       "[p4_ext_tilt_d20=49_100] -> first clean 49_101..49_300 "\n'
            '                                       "past-the-hit-point window, r335 W26 semantics; ADMIT "\n'
            '                                       "receipt results/_r566bma_w63_band_gate.py); W1..W62 "\n'
            '                                       "finalizes ALL LANDED at this freeze (net chain head "\n'
            '                                       "500,948, K=134,320) -- ZERO in-flight upstream seats, "\n'
            '                                       "chain fully caught up (finalize merge loop derives the "\n'
            '                                       "wave set from registry keys at run time and stays "\n'
            '                                       "FAIL-CLOSED on any not-yet-finalized upstream seat, "\n'
            '                                       "r307 two-state law)"),\n'
            '                            "a_seed_base": 169_004,        # law sec.4 W63 A: 169_004..171_003 (arithmetic continuation)\n'
            '                            "b_exit_seed_base": 49_101,    # law sec.4 W63 B: 49_101..49_300 (forced-skip jump past 49_000/49_100)\n'
            '                            "shard_subdir": "n1_w63", "out_name": "n1_w63_results.json",\n'
            '                            "engine_owner": "bm-a"},\n'
            '                       }')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[63] landed (anchor=W62 entry tail, insert)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W63 leg --------------
LEG63 = '''
    # --- W63 materializer face (r566 bm-a freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2):
    #     bm-a's fifteenth owned per machine-derive (engine_owner==bm-a
    #     rows 14 + candidate); wave 63 = next free number after the
    #     registered W62 row (seat declared published=reserved
    #     MSG-20261002-0843-bma; W1..W62 finalizes ALL LANDED at this
    #     freeze -- zero in-flight upstream seats, chain fully caught
    #     up, net head 500,948 K=134,320). A-side ARITHMETIC
    #     CONTINUATION from the W62 tail no skip (169_004..171_003
    #     CLEAN machine-derived == the W62 row W63+ published
    #     projection verbatim); B-side FORCED-SKIP JUMP past the
    #     two-step refusal (arithmetic 48_801..49_000 REFUSED
    #     [SEED_REGISTRY p4_ext_tilt_q=49_000] -> 49_001..49_200
    #     REFUSED [p4_ext_tilt_d20=49_100] -> first clean
    #     49_101..49_300 past-the-hit-point window, r335 W26
    #     semantics; ADMIT receipt
    #     results/_r566bma_w63_band_gate.py; not a re-pick -- R250:
    #     W63 bands were never assigned) --
    _set_wave(63)
    try:
        assert WAVE_CONFIGS[63]["a_seed_base"] == pf.N1_BANDS[63]["a"][0], \\
            "W63 A band drift vs law mirror"
        assert WAVE_CONFIGS[63]["b_exit_seed_base"] == \\
            pf.N1_BANDS[63]["b_exit"][0], "W63 B band drift vs law mirror"
        assert WAVE_CONFIGS[63].get("engine_owner") == \\
            pf.N1_BANDS[63].get("engine_owner") == "bm-a", \\
            "W63 engine_owner drift (law mirror parity)"
        w63_a = {A_SEED_BASE + j for j in range(A_N)}
        w63_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w63_a & w63_b), "W63 A/B band overlap"
        assert not (w63_a & reg_ints) and not (w63_b & reg_ints), \\
            "W63 hits SEED_REGISTRY"
        for nm, band in (("A", w63_a), ("B", w63_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W63 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W63 {nm} hits W1"
            assert not (band & probes), f"W63 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W60/W61/W62
        # are REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly.
        assert pf.N1_BANDS[60] == {"a": (163_004, 165_003),
                                   "b_exit": (48_201, 48_400),
                                   "engine_owner": "bm-c"}, \\
            "registered W60 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[61] == {"a": (165_004, 167_003),
                                   "b_exit": (48_401, 48_600),
                                   "engine_owner": "bm-b"}, \\
            "registered W61 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[62] == {"a": (167_004, 169_003),
                                   "b_exit": (48_601, 48_800),
                                   "engine_owner": "bm-a"}, \\
            "registered W62 row parity drift (r307 two-state)"
        # prior-wave disjointness incl. W48..W62 (all registered, all
        # finalizes landed -- zero in-flight seats at this freeze).
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62):
            assert not (w63_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W63 A hits W{wprev}"
            assert not (w63_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W63 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W63 clears it.
        n3r1_used63 = set(range(70_000, 70_006))
        assert not (w63_a & n3r1_used63) and not (w63_b & n3r1_used63), \\
            "W63 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w63_a & lfc_actual12) and not (w63_b & lfc_actual12), \\
            "W63 bands must clear the lfc actual draw range"
        assert not (w63_a & options_actual12) and \\
            not (w63_b & options_actual12), \\
            "W63 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W63 row, r566): A ARITHMETIC
        # CONTINUATION (169_004 = W62 A end 169_003 + 1); B
        # FORCED-SKIP JUMP past the two-step refusal (49_101 =
        # 49_100 + 1, window 49_101..49_300; the arithmetic window
        # 48_801..49_000 was REFUSED at 49_000, the intermediate
        # 49_001..49_200 at 49_100 -- r335 W26 past-hit semantics).
        assert WAVE_CONFIGS[63]["a_seed_base"] == 169_004 == 169_003 + 1, \\
            "W63 A must start at the registered W62 A end + 1 " \\
            "(arithmetic continuation window 169_004..171_003 CLEAN -- " \\
            "no skip family)"
        assert WAVE_CONFIGS[63]["b_exit_seed_base"] == 49_101 == 49_100 + 1, \\
            "W63 B must start at the last refused hit point + 1 " \\
            "(forced-skip jump window 49_101..49_300 per r335 W26 " \\
            "past-hit semantics -- two-step refusal 49_000/49_100 " \\
            "machine-derived, W5/W6/W8/W12/W17/W26/W39-B/W43-B/W47-B/" \\
            "W51-B skip family)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W63-SHARD-0",
                                          "n1w63-0of12"), "W63 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W63-SHARD-11",
                                          "n1w63-11of12")
        assert SHARD_DIR.endswith("n1_w63") and OUT.endswith(
            "n1_w63_results.json"), "W63 path drift"
        for wprev in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                      18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                      31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
                      44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                      57, 58, 59, 60, 61, 62):
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W63 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W63_PREREG.md")), \\
            "W63 per-wave prereg missing (materializer requirement)"
        # W63 finalize cumulative deps: W17..W62 outputs ALL PRESENT
        # (static landed seats; chain head 500,948 = W62 bm-c r357
        # K=134,320; W1..W62 finalizes ALL LANDED -- zero in-flight
        # upstream seats, first fully-caught-up window since W60;
        # the finalize merge loop derives the wave set from registry
        # keys at run time and stays FAIL-CLOSED on any not-yet-
        # finalized upstream seat, r307 two-state law).
        for _depw in (17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                      30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
                      43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
                      56, 57, 58, 59, 60, 61, 62):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W63 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law): prior-wave
        # set derives from registry keys below 63 (no 15; incl.
        # 48..62 -- all registered, all finalizes landed).
        assert sorted(w for w in WAVE_CONFIGS if w < 63) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19,
             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34,
             35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
             50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62], \\
            "W63 prior-wave set must derive from registry keys (no 15, " \\
            "incl. 48..62)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W63 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG63.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W63 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 5th face) ------
t2c, eol2c = load(FP2)
if '+ W63 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('law sec.4 W62 row, r565 bm-a] "\n'
          '          "+ T-141 s2 ')
    SEG63 = ('law sec.4 W62 row, r565 bm-a] "\n'
             '          "+ W63 materializer face [same guard set, dep=W17..W62 "\n'
             '          "outputs ALL PRESENT (landed chain head 500,948, K=134,320 "\n'
             '          "-- ZERO in-flight upstream seats, chain fully caught up, "\n'
             '          "first fully-caught-up window since W60), FIFTY-SECOND "\n'
             '          "ENGINE-OWNED WAVE bm-a\'s fifteenth owned claim per "\n'
             '          "machine-derive (engine_owner==bm-a rows 14 + candidate), "\n'
             '          "engine_owner=bm-a per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series (wave 63 = "\n'
             '          "first FREE number after the registered W62 row; seat "\n'
             '          "declared published=reserved MSG-20261002-0843-bma), "\n'
             '          "A-side ARITHMETIC CONTINUATION from the W62 tail no "\n'
             '          "skip (A 169_004..171_003 CLEAN machine-derived per the "\n'
             '          "W62 row W63+ WARNING) + B-side FORCED-SKIP JUMP past "\n'
             '          "the two-step refusal (arithmetic 48_801..49_000 REFUSED "\n'
             '          "[SEED_REGISTRY p4_ext_tilt_q=49_000] -> 49_001..49_200 "\n'
             '          "REFUSED [p4_ext_tilt_d20=49_100] -> first clean "\n'
             '          "49_101..49_300 past-the-hit-point window, r335 W26 "\n'
             '          "semantics; ADMIT receipt results/_r566bma_w63_band_gate.py; "\n'
             '          "not a free pick -- R250), N3-R1 used-seed leg, probe-seed "\n'
             '          "cluster leg, law sec.4 W63 row, r566 bm-a] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG63, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W63 segment landed (insert after W62 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W63 row -------------------
ROW63 = """
- N1 波63（r566 bm-a 冻·prereg 时展行）：**第五十二枚引擎波·bm-a 第十五枚自有波〔机面 derive：engine_owner==bm-a 行 14+本候选〕**·engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 同 W10-W62 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-a 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启免做·W44/W45/W48/W54/W57/W62 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**零隔接力：W62 全生命周期收口**（r565 bm-a 冻结 381d85208→本机 tick 引擎烧录 12/12→产品送达 796cee730→finalize bm-c r357 跨机收口 c2d4fb7a9〔三机接力首例全生命周期：让路→席位→冻结 bm-a→烧录 bm-a→收口 bm-c〕→本机 r566 finalize 确定性孪生让路〔payload 恒等断言过·r498 律取 origin 侧零损失〕）→**波号 63=注册表 W62 行后首个自由号**·席位公示=MSG-20261002-0843-bma（published=reserved r518-① 律·W48/W49/W55/W62 先例）·r511 表尾锁例冻结前 fetch 实核表尾时 W63 号位净空·origin 侧 vacancy 机验】·**双面分裂（r535 机闸 derive 律·r335 跳位语义）**：W62 行 W63+ 警示投影 **A 169_004..171_003 CLEAN／B 算术位 48_801..49_000 REFUSED**〔SEED_REGISTRY p4_ext_tilt_q=49_000+p4_ext_tilt_d20=49_100〕→本波 **A-ext seed=169_004..171_003**（**A 面算术续带**==W62 A 尾 169_003+1·步长逐字·CLEAN 机证）·**B-ext exit seed=49_101..49_300**（**B 面强制跳位**：算术位 48_801..49_000 REFUSED〔p4_ext_tilt_q=49_000 命中〕→越 hit 起窗 49_001..49_200 仍 REFUSED〔p4_ext_tilt_d20=49_100 命中〕→**首净窗 49_101..49_300**〔=49_100+1 起·200 宽·r335 W26 越 hit 起窗语义·W5/W6/W8/W12/W17/W26/W39-B/W43-B/W47-B/W51-B 跳位族·R250 非重挑·W63 B 带从未指派〕·跳位两步 jump trace 机闸留档）·【机证净空——leg0 六十二键（61 注册行+候选）+leg0b W62 行 W63+ 警示 prose 在场校验+leg1-A 算术位 CLEAN+leg1-B 算术位 REFUSED refusal facts 恒等 {49_000}+leg2-A 首净窗==算术==候选+leg2-B 越 hit 两步跳位 trace 恒等〔(48_801,[49_000])→(49_001,[49_100])→49_101..49_300〕+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验·**MSG-0640 三修工具**（FIX-A 编辑前 origin-blob 等值断言+FIX-B 锚=最后注册行+行存活核查+FIX-C 推送前纯增量 diff 断言）〕·ADMIT 回执=results/_r566bma_w63_band_gate.py·r566 bm-a 起草窗实跑·非重挑 R250·W63 带从未指派·测量面零结果可钓】·扫描面=pre-W63 六十一行 N1 带表【含 W59 行 161_004..163_003/48_001..48_200〔bm-b r562/563·finalize 已落账 K=127,720〕·W60 行 163_004..165_003/48_201..48_400〔bm-c r355·finalize 已落账 K=129,920〕·W61 行 165_004..167_003/48_401..48_600〔bm-b r564·finalize 已落账 K=132,120·bm-c r357 收口〕·**W62 行 167_004..169_003/48_601..48_800〔bm-a r565·finalize 已落账 K=134,320·净账本链头 500,948〕**】·**零在飞上游席披露：W1..W62 finalize 全落账=链全追平（W34/W47/W53/W58/W60 后又一个 fully-caught-up 冻结窗）·FAIL-CLOSED r307 两态律运行时守卫照设**·带域不相交·W1 ext·v1 在用带·SEED_REGISTRY 全键（int 值全清·LOWAMP-P1/P2/P3 键 20.33M 域零交集）·**N3-R1 实际种子带 70_000..70_005**（r529 裁定行强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·lfc 实际流 30_000..30_099·options_wave2 实际流 63_000..63_049（leg-3e 实际流避让腿）·**W64+ 投影（带闸投影腿机证·W64 prereg 照例带闸复核 r335 律）：A 171_004..173_003 CLEAN／B 49_301..49_500 CLEAN（复核于 W64 prereg）**·prereg=PERPETUAL_N1_W63_PREREG.md 冻结〔S5 锚=W62 实测：merged mu −0.092547/W62-only mu −0.100936/sigma 0.239601/A-p95 0.3037/K-lift −0.0006·累计池投影 136,520〕·burn 由本机 tick 引擎按分片合同执行·finalize=活链头 derive one-pass（r538 一过律）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce263\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW63.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W63 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    63: {"a": (169_004') == 1, 'FIX-B FAIL: W63 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W63"') == 1, 'FIX-B FAIL: W63 config not exactly once'
for leg, base in (('W58 materializer face', 'w58leg'),
                  ('W59 materializer face', 'w59leg'),
                  ('W60 materializer face', 'w60leg'),
                  ('W61 materializer face', 'w61leg'),
                  ('W62 materializer face', 'w62leg')):
    assert n11.count(leg) == BASE_SIGS[base], f'FIX-B FAIL: {leg} lost'
assert n11.count('W63 materializer face') == 2, \
    'FIX-B FAIL: W63 leg+summary must be exactly 2'
for w in (48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce263\uff08') == 1, 'FIX-B FAIL: canon W63 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W63 added per face')

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
