# -*- coding: utf-8 -*-
"""r574 bm-a W81 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r561/r566/r568/r570/r571/r574 lineage).

FIX-A (origin-blob freshness): every tracked edit target must show zero
  deleted lines vs origin/main BEFORE any edit runs (r559 stale-base cure).
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W80, bm-c's);
  after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W81 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W81 = SEVENTIETH engine wave (ordinal per the live comment sequence
W78=67th, W79=68th, W80=69th), bm-a's TWENTIETH owned per
machine-derive (engine_owner==bm-a rows 19 + candidate). First free
number after the registered W80 row (bm-c r364 freeze, landed origin).
Seat published=reserved MSG-20261002-1210-bma PUSHED to origin BEFORE
this freeze (r565 early-visibility law; commit b38c8e64a).

Bands: A 205_004..207_003 (== W80 A end 205_003 + 1, arithmetic
continuation zero skip, CLEAN) / B 54_001..54_200 (B arithmetic
53_801..54_000 REFUSED at SEED_REGISTRY t18_deep_axis=54_000 band
UPPER-EDGE endpoint -> hit+1 restart 54_001..54_200, BOTH READINGS
CONVERGE at the edge endpoint -- W74-B 52_000 family, no fork face,
unlike W63 mid-band dual hits). ONE in-flight upstream seat at this
freeze: W80 bm-c (burn in flight at freeze commit time) -- finalize
chain-pending FAIL-CLOSED r307. W1..W79 finalizes ALL LANDED (net head
538,348, K=171,720 -- W79 bm-b r574 this window; chain W1..W79 fully
landed, ZERO in-flight upstream seats below W80).
ADMIT receipt results/_r574bma_w81_band_gate.py; banned gate ADMIT
0 matched. W82+ projection disclosed by the gate: A 207_004..209_003
CLEAN; B 54_201..54_400 CLEAN (both sides arithmetic expectation).
"""
import subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREAT = 0x08000000  # CREATE_NO_WINDOW (session-host flash guard)

def git(*a):
    r = subprocess.run(['git', '-C', REPO] + list(a), capture_output=True,
                       creationflags=CREAT)
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
                       capture_output=True, creationflags=CREAT)
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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 81))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in
       range(58, 81)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 81)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[81] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '81: {"a": (205_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    80: {"a": (203_004, 205_003), "b_exit": (53_601, 53_800),\n'
          '         "engine_owner": "bm-c"},\n')
    NEW = ('    80: {"a": (203_004, 205_003), "b_exit": (53_601, 53_800),\n'
           '         "engine_owner": "bm-c"},\n'
           '    # SEVENTIETH ENGINE-OWNED WAVE (r574 bm-a freeze): bm-a\'s\n'
           '    # twentieth owned per machine-derive (engine_owner==bm-a\n'
           '    # rows 19 + candidate). Wave 81 = first free number after the\n'
           '    # registered W80 row (r511 tail-lock, fetch-checked vacancy;\n'
           '    # seat published=reserved MSG-20261002-1210-bma PUSHED to\n'
           '    # origin before this freeze per r565 early-visibility law,\n'
           '    # commit b38c8e64a).\n'
           '    # W1..W79 finalizes ALL LANDED (net head 538,348, K=171,720,\n'
           '    # W79 bm-b r574 this window; chain W1..W79 fully landed);\n'
           '    # W80 bm-c (burn in flight) = ONE in-flight upstream seat at\n'
           '    # this freeze (finalize chain-pending FAIL-CLOSED r307).\n'
           '    # A SIDE ARITHMETIC CONTINUATION from the W80 row tail, zero\n'
           '    # skip: A 205_004..205_003.. A 205_004..207_003 (= W80 A end\n'
           '    # 205_003 + 1) CLEAN. B SIDE FORCED SKIP at the arithmetic\n'
           '    # position 53_801..54_000 which is REFUSED at SEED_REGISTRY\n'
           '    # t18_deep_axis=54_000 (band UPPER-EDGE endpoint) -> hit+1\n'
           '    # restart B 54_001..54_200; BOTH READINGS CONVERGE at the\n'
           '    # edge endpoint (W74-B 52_000 family; no fork face,\n'
           '    # F-20261002-03 not triggered).\n'
           '    # Machine-verified at prereg time\n'
           '    # (results/_r574bma_w81_band_gate.py ADMIT receipt vs the\n'
           '    # 78-row pre-W81 table + live SEED_REGISTRY values + probe\n'
           '    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin\n'
           '    # slot vacancy machine-checked). W82+ gate projection: A\n'
           '    # 207_004..209_003 CLEAN; B 54_201..54_400 CLEAN.\n'
           '    # NOT a re-pick (R250: W81 bands were never assigned).\n'
           '    81: {"a": (205_004, 207_003), "b_exit": (54_001, 54_200),\n'
           '         "engine_owner": "bm-a"},\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[81] landed (anchor=W80 row, insert after)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[81] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '81: {"batch": "PERPETUAL-N1-W81"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w80", "out_name": "n1_w80_results.json",\n'
          '                            "engine_owner": "bm-c"},\n')
    NEW2 = A2 + (
        '                       81: {"batch": "PERPETUAL-N1-W81",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W81_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; SEVENTIETH ENGINE-OWNED WAVE, "\n'
        '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
        '                                       "(first-free-number law over the registered W80 row; "\n'
        '                                       "seat published=reserved MSG-20261002-1210-bma "\n'
        '                                       "PUSHED to origin BEFORE this freeze per r565 "\n'
        '                                       "early-visibility law, commit b38c8e64a), "\n'
        '                                       "engine_owner=bm-a, wave 81 A-SIDE ARITHMETIC "\n'
        '                                       "CONTINUATION zero skip (A 205_004..207_003 CLEAN) + "\n'
        '                                       "B-SIDE FORCED SKIP (arithmetic 53_801..54_000 "\n'
        '                                       "REFUSED at SEED_REGISTRY t18_deep_axis=54_000 band "\n'
        '                                       "UPPER-EDGE endpoint -> hit+1 restart B 54_001..54_200; "\n'
        '                                       "BOTH READINGS CONVERGE at the edge endpoint, W74-B "\n'
        '                                       "52_000 family, no fork face, F-20261002-03 not "\n'
        '                                       "triggered; W82+ projection: A 207_004..209_003 "\n'
        '                                       "CLEAN / B 54_201..54_400 CLEAN disclosed for the "\n'
        '                                       "next freezer); "\n'
        '                                       "W1..W79 finalizes ALL LANDED at this freeze (net "\n'
        '                                       "chain head 538,348, K=171,720, W79 bm-b r574 this "\n'
        '                                       "window; chain W1..W79 fully landed); W80 bm-c = ONE "\n'
        '                                       "in-flight upstream seat (finalize chain-pending "\n'
        '                                       "FAIL-CLOSED r307)"),\n'
        '                            "a_seed_base": 205_004,        # law sec.4 W81 A: 205_004..207_003 (arithmetic continuation)\n'
        '                            "b_exit_seed_base": 54_001,   # law sec.4 W81 B: 54_001..54_200 (hit+1 forced skip at t18_deep_axis=54_000)\n'
        '                            "shard_subdir": "n1_w81", "out_name": "n1_w81_results.json",\n'
        '                            "engine_owner": "bm-a"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[81] landed (anchor=W80 entry tail, insert after)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W81 leg --------------
LEG81 = '''
    # --- W81 materializer face (r574 bm-a freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-a's
    #     twentieth owned per machine-derive (engine_owner==bm-a
    #     rows 19 + candidate); wave 81 = first free number after the
    #     registered W80 row (bm-c r364). Seat published=reserved
    #     MSG-20261002-1210-bma pushed to origin BEFORE this freeze
    #     (commit b38c8e64a, r565 early-visibility law). ONE in-flight
    #     upstream seat at this freeze: W80 bm-c (burn in flight) --
    #     finalize chain-pending FAIL-CLOSED r307 at run time. W1..W79
    #     finalizes ALL LANDED (net head 538,348, K=171,720, W79 bm-b
    #     r574 this window; chain W1..W79 fully landed). ADMIT receipt
    #     results/_r574bma_w81_band_gate.py; not a re-pick -- R250:
    #     W81 bands were never assigned --
    _set_wave(81)
    try:
        assert WAVE_CONFIGS[81]["a_seed_base"] == pf.N1_BANDS[81]["a"][0], \\
            "W81 A band drift vs law mirror"
        assert WAVE_CONFIGS[81]["b_exit_seed_base"] == \\
            pf.N1_BANDS[81]["b_exit"][0], "W81 B band drift vs law mirror"
        assert WAVE_CONFIGS[81].get("engine_owner") == \\
            pf.N1_BANDS[81].get("engine_owner") == "bm-a", \\
            "W81 engine_owner drift (law mirror parity)"
        w81_a = {A_SEED_BASE + j for j in range(A_N)}
        w81_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w81_a & w81_b), "W81 A/B band overlap"
        assert not (w81_a & reg_ints) and not (w81_b & reg_ints), \\
            "W81 hits SEED_REGISTRY"
        for nm, band in (("A", w81_a), ("B", w81_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W81 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W81 {nm} hits W1"
            assert not (band & probes), f"W81 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W73..W80 are
        # REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly (W77 bm-a r572; W78 bm-c r363;
        # W79 bm-b r573; W80 bm-c r364).
        assert pf.N1_BANDS[73] == {"a": (189_004, 191_003),
                                   "b_exit": (51_601, 51_800),
                                   "engine_owner": "bm-a"}, \\
            "registered W73 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[74] == {"a": (191_004, 193_003),
                                   "b_exit": (52_001, 52_200),
                                   "engine_owner": "bm-b"}, \\
            "registered W74 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[75] == {"a": (193_004, 195_003),
                                   "b_exit": (52_201, 52_400),
                                   "engine_owner": "bm-a"}, \\
            "registered W75 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[76] == {"a": (195_004, 197_003),
                                   "b_exit": (52_401, 52_600),
                                   "engine_owner": "bm-b"}, \\
            "registered W76 row parity drift (r307 two-state)"
        assert pf.N1_BANDS[77] == {"a": (197_004, 199_003),
                                   "b_exit": (52_601, 52_800),
                                   "engine_owner": "bm-a"}, \\
            "registered W77 row parity drift (r307 two-state; bm-a r572)"
        assert pf.N1_BANDS[78] == {"a": (199_004, 201_003),
                                   "b_exit": (53_201, 53_400),
                                   "engine_owner": "bm-c"}, \\
            "registered W78 row parity drift (r307 two-state; bm-c r363)"
        assert pf.N1_BANDS[79] == {"a": (201_004, 203_003),
                                   "b_exit": (53_401, 53_600),
                                   "engine_owner": "bm-b"}, \\
            "registered W79 row parity drift (r307 two-state; bm-b r573)"
        assert pf.N1_BANDS[80] == {"a": (203_004, 205_003),
                                   "b_exit": (53_601, 53_800),
                                   "engine_owner": "bm-c"}, \\
            "registered W80 row parity drift (r307 two-state; bm-c r364)"
        # prior-wave disjointness incl. W48..W80 (all registered; the
        # W80 row is the direct arithmetic upstream of W81's A band).
        for wprev in REG_WAVES_ALL:
            assert not (w81_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W81 A hits W{wprev}"
            assert not (w81_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W81 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W81 clears it.
        n3r1_used81 = set(range(70_000, 70_006))
        assert not (w81_a & n3r1_used81) and not (w81_b & n3r1_used81), \\
            "W81 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w81_a & lfc_actual12) and not (w81_b & lfc_actual12), \\
            "W81 bands must clear the lfc actual draw range"
        assert not (w81_a & options_actual12) and \\
            not (w81_b & options_actual12), \\
            "W81 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W81 row, r574): A-SIDE ARITHMETIC
        # CONTINUATION from the registered W80 tail, zero skip -- the
        # A arithmetic window must be CLEAN; B-SIDE FORCED SKIP -- the
        # B arithmetic window must be REFUSED at 54_000 and the landed
        # band must start at hit+1 (W74-B edge-endpoint family).
        assert WAVE_CONFIGS[81]["a_seed_base"] == 205_004 == \\
            pf.N1_BANDS[80]["a"][1] + 1, \\
            "W81 A must start at the registered W80 A end + 1 " \\
            "(arithmetic continuation window 205_004..207_003 CLEAN)"
        assert WAVE_CONFIGS[81]["b_exit_seed_base"] == 54_001 == 54_000 + 1, \\
            "W81 B must start at hit+1 past t18_deep_axis=54_000 " \\
            "(forced skip, upper-edge endpoint family W74-B)"
        arith_a81 = set(range(205_004, 207_004))
        arith_b81 = set(range(53_801, 54_001))
        assert not (arith_a81 & reg_ints), \\
            "W81 A arithmetic window must be CLEAN (zero-skip ADMIT face)"
        assert 54_000 in (arith_b81 & reg_ints), \\
            "W81 B arithmetic window must be REFUSED at 54_000 " \\
            "(forced-skip face, refusal facts identity)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W81-SHARD-0",
                                          "n1w81-0of12"), "W81 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W81-SHARD-11",
                                          "n1w81-11of12")
        assert SHARD_DIR.endswith("n1_w81") and OUT.endswith(
            "n1_w81_results.json"), "W81 path drift"
        for wprev in REG_WAVES_ALL:
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W81 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W81_PREREG.md")), \\
            "W81 per-wave prereg missing (materializer requirement)"
        # W81 finalize cumulative deps: W17..W79 outputs ALL PRESENT
        # (landed chain head 538,348, K=171,720, W79 bm-b r574 this
        # window; W80 bm-c = ONE in-flight upstream seat -- the
        # finalize merge loop derives the wave set from registry keys
        # at run time and stays FAIL-CLOSED on the not-yet-finalized
        # seat, r307 two-state law).
        for _depw in range(17, 80):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W81 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law):
        # prior-wave set derives from registry keys below 81 (no 15,
        # incl. 48..80 -- all registered, W80 in-flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 81) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 81)], \\
            "W81 prior-wave set must derive from registry keys (no 15; " \\
            "incl. 48..80 -- W80 registered before this freeze landed)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W81 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    REG_WAVES_ALL = '[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 81)]'
    LEG81 = LEG81.replace('REG_WAVES_ALL', REG_WAVES_ALL)
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG81.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W81 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 5th face) ------
t2c, eol2c = load(FP2)
if '+ W81 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('          "probe-seed cluster leg, law sec.4 W80 row, "\n'
          '          "r364 bm-c] "\n'
          '          "+ T-141 s2 ')
    SEG81 = ('          "probe-seed cluster leg, law sec.4 W80 row, "\n'
             '          "r364 bm-c] "\n'
             '          "+ W81 materializer face [same guard set, dep=W17..W79 "\n'
             '          "outputs ALL PRESENT (landed chain head 538,348, "\n'
             '          "K=171,720, W79 bm-b r574 this window; chain W1..W79 "\n'
             '          "fully landed), W80 bm-c = ONE in-flight upstream "\n'
             '          "seat (FAIL-CLOSED r307 at run time), SEVENTIETH "\n'
             '          "ENGINE-OWNED WAVE bm-a\'s twentieth owned claim "\n'
             '          "per machine-derive (engine_owner==bm-a rows 19 + "\n'
             '          "candidate), engine_owner=bm-a per engine "\n'
             '          "de-throttle law O-20261001-2355 sec.2 "\n'
             '          "own-continuous-series (wave 81 = first FREE number "\n'
             '          "after the registered W80 row; seat "\n'
             '          "published=reserved MSG-20261002-1210-bma pushed to "\n'
             '          "origin BEFORE this freeze, commit b38c8e64a, r565 "\n'
             '          "law), A-SIDE ARITHMETIC CONTINUATION zero skip (A "\n'
             '          "205_004..207_003 CLEAN) + B-SIDE FORCED SKIP "\n'
             '          "(arithmetic 53_801..54_000 REFUSED at SEED_REGISTRY "\n'
             '          "t18_deep_axis=54_000 upper-edge endpoint -> hit+1 "\n'
             '          "restart B 54_001..54_200; BOTH READINGS CONVERGE at "\n'
             '          "the edge endpoint, W74-B 52_000 family, no fork "\n'
             '          "face; W82+ projection both CLEAN disclosed for the "\n'
             '          "next freezer; ADMIT receipt "\n'
             '          "results/_r574bma_w81_band_gate.py; not a "\n'
             '          "free pick -- R250), N3-R1 used-seed leg, "\n'
             '          "probe-seed cluster leg, law sec.4 W81 row, "\n'
             '          "r574 bm-a] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG81, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W81 segment landed (insert after W80 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W81 row -------------------
ROW81 = """
- N1 波81（r574 bm-a 冻·prereg 时展行）：**第七十枚引擎波·bm-a 第二十枚自有波〔机面 derive：engine_owner==bm-a 行 19+本候选〕**·engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 同 W10-W80 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-a 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启免做·W44/W45/W48/W54/W57/W62/W64/W68/W73/W75/W77 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 81=注册表 W80 行后首个自由号**（r511 表尾锁例冻结前 fetch 实核表尾时 W81 号位净空·origin 侧 vacancy 机验）·**席位公示=MSG-20261002-1210-bma（published=reserved r518-① 律·先于冻结 commit 推 origin=r565 早可见性律·commit b38c8e64a）**·本窗实况=W79 finalize one-pass 已落账（bm-b r574·**538,348 净链头**·K=171,720·链序 W1..W79 全落账零在飞上游席——本波 §5 锚滚动至 W79 实测值）〕·**带位（r535 机闸 derive 律·活注册表机证·ADMIT 回执=results/_r574bma_w81_band_gate.py）**：**A-ext seed=205_004..207_003**（**A 面算术续带零跳位**==W80 A 尾 205_003+1·步长逐字·CLEAN）；**B-ext exit seed=54_001..54_200**（**B 面越 hit 强制跳位**：算术位 53_801..54_000 于带上边缘撞 **SEED_REGISTRY t18_deep_axis=54_000** 端点单点〔r307 W5/W74-B 52_000 边缘端点先例族〕→**两读法恒同解**：越 hit 起窗 54_001..54_200==窗步链跳位 54_001..54_200——无分叉面〔不同于 W63 双点中位分叉·r566 判例反面·F-20261002-03 不触发〕·跳位被迫性 R250 非自由挑）·【机证净空——leg0 七十八键（78 注册行·表尾=W80 bm-c r364）+leg1-A 算术位 CLEAN 机证+leg1-B 算术位 REFUSED 恒等 refusal facts=[54_000] 机证+leg2 A 侧首净窗==算术位恒等／B 侧 hit+1 首净窗==候选（B 双读法收敛断言）+leg3 双带 ADMIT+origin 号位净空机验+SEED_REGISTRY 全键 160 值+N3-R1 已用种子带腿（70_000..70_005·MSG-183x r529 强制）+探针种子簇腿（95_000..95_003·r335 强制）+N2/N4+N2-W15 探针点+lfc/options 实际流腿】·**W82+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 207_004..209_003 **CLEAN**；B 54_201..54_400 **CLEAN**（双侧算术零跳位预期）·R250：W81 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W81 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W81_PREREG.md（冻结件）·本波 §5 锚=W79 finalize 实测值（锚滚动律）·finalize 链序前置=W80 bm-c 唯一在飞上游席（FAIL-CLOSED r307 两态律）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce281\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW81.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W81 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    81: {"a": (205_004') == 1, 'FIX-B FAIL: W81 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W81"') == 1, 'FIX-B FAIL: W81 config not exactly once'
for w in range(58, 81):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W81 materializer face') == 2, \
    'FIX-B FAIL: W81 leg+summary must be exactly 2'
for w in range(48, 81):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce281\uff08') == 1, 'FIX-B FAIL: canon W81 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W81 added per face')

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
print('FREEZE_EDITS_OK 81')
