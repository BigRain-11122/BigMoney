# -*- coding: utf-8 -*-
"""r575 bm-a W84 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening (r561/r566/r568/r570/r571/r574 lineage).

FIX-A (origin-blob freshness): every tracked edit target must show zero
  deleted lines vs origin/main BEFORE any edit runs (r559 stale-base cure).
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W83, bm-c's);
  after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W84 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W84 = SEVENTY-FOURTH engine wave by MACHINE-DERIVE (engine_owner rows
73 + candidate; live prose comment ordinals carried a -1 drift at least
since W80 -- machine: W80=70th/W81=71st/W82=72nd/W83=73rd, r359
counts-from-gate law), bm-a's TWENTY-FIRST owned per machine-derive
(engine_owner==bm-a rows 20 + candidate). First free number after the
registered W83 row (bm-c r365 freeze, landed origin).
Seat published=reserved MSG-20261002-1245-bma PUSHED to origin BEFORE
this freeze (r565 early-visibility law; commit ad5df156c).

Bands: A 211_004..213_003 (== W83 A end 211_003 + 1, arithmetic
continuation zero skip, CLEAN) / B 54_601..54_800 (== W83 B end
54_600 + 1, arithmetic continuation zero skip, CLEAN). BOTH SIDES
arithmetic continuation, no refusal points, single reading -- no fork
face, F-20261002-03 not triggered. TWO in-flight upstream seats at
this freeze: W82 bm-b (12/12 burned, adopted by bm-b r575 S0
recovery, finalize not yet landed) + W83 bm-c (registered, burn in
flight) -- finalize chain-pending FAIL-CLOSED r307. W1..W81 finalizes
ALL LANDED (net head 542,748, K=176,120, W81 bm-a r574).
ADMIT receipt results/_r575bma_w84_band_gate.py; banned gate ADMIT
0 matched. W85+ projection disclosed by the gate: A 213_004..215_003
CLEAN; B 54_801..55_000 REFUSED at SEED_REGISTRY a158_truegap_ic=55_000
(upper-edge endpoint -> hit+1 55_001..55_200, W74-B/W81 edge family).
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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 84))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in
       range(58, 84)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 84)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[84] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '84: {"a": (211_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    83: {"a": (209_004, 211_003), "b_exit": (54_401, 54_600),\n'
          '         "engine_owner": "bm-c"},\n')
    NEW = ('    83: {"a": (209_004, 211_003), "b_exit": (54_401, 54_600),\n'
           '         "engine_owner": "bm-c"},\n'
           '    # SEVENTY-FOURTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r575 bm-a\n'
           '    # freeze): engine_owner rows 73 + candidate; bm-a\'s\n'
           '    # twenty-first owned per machine-derive (engine_owner==bm-a\n'
           '    # rows 20 + candidate). Wave 84 = first free number after the\n'
           '    # registered W83 row (r511 tail-lock, fetch-checked vacancy;\n'
           '    # seat published=reserved MSG-20261002-1245-bma PUSHED to\n'
           '    # origin before this freeze per r565 early-visibility law,\n'
           '    # commit ad5df156c).\n'
           '    # W1..W81 finalizes ALL LANDED (net head 542,748, K=176,120,\n'
           '    # W81 bm-a r574; chain W1..W81 fully landed); TWO in-flight\n'
           '    # upstream seats at this freeze: W82 bm-b (12/12 burned,\n'
           '    # adopted by bm-b r575 S0 recovery, finalize pending) + W83\n'
           '    # bm-c (registered, burn in flight) -- finalize chain-pending\n'
           '    # FAIL-CLOSED r307.\n'
           '    # BOTH SIDES ARITHMETIC CONTINUATION from the W83 row tails,\n'
           '    # zero skip: A 211_004..213_003 (= W83 A end 211_003 + 1)\n'
           '    # CLEAN. B 54_601..54_800 (= W83 B end 54_600 + 1) CLEAN.\n'
           '    # Single reading, no refusal points, no fork face,\n'
           '    # F-20261002-03 not triggered.\n'
           '    # Machine-verified at prereg time\n'
           '    # (results/_r575bma_w84_band_gate.py ADMIT receipt vs the\n'
           '    # 81-row pre-W84 table + live SEED_REGISTRY values + probe\n'
           '    # cluster 95_000..95_003 r335 discovery leg + N3-R1 used-seed\n'
           '    # band 70_000..70_005 MSG-183x r529 mandatory leg; origin\n'
           '    # slot vacancy machine-checked). W85+ gate projection: A\n'
           '    # 213_004..215_003 CLEAN; B 54_801..55_000 REFUSED at\n'
           '    # SEED_REGISTRY a158_truegap_ic=55_000 upper-edge endpoint\n'
           '    # -> hit+1 restart 55_001..55_200 (W74-B/W81 edge family).\n'
           '    # NOT a re-pick (R250: W84 bands were never assigned).\n'
           '    84: {"a": (211_004, 213_003), "b_exit": (54_601, 54_800),\n'
           '         "engine_owner": "bm-a"},\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[84] landed (anchor=W83 row, insert after)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[84] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '84: {"batch": "PERPETUAL-N1-W84"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w83", "out_name": "n1_w83_results.json",\n'
          '                            "engine_owner": "bm-c"},\n')
    NEW2 = A2 + (
        '                       84: {"batch": "PERPETUAL-N1-W84",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W84_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; SEVENTY-FOURTH ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 73 + candidate; prose "\n'
        '                                       "ordinal -1 drift disclosed since W80, r359 law), "\n'
        '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
        '                                       "(first-free-number law over the registered W83 row; "\n'
        '                                       "seat published=reserved MSG-20261002-1245-bma "\n'
        '                                       "PUSHED to origin BEFORE this freeze per r565 "\n'
        '                                       "early-visibility law, commit ad5df156c), "\n'
        '                                       "engine_owner=bm-a, wave 84 BOTH SIDES ARITHMETIC "\n'
        '                                       "CONTINUATION zero skip (A 211_004..213_003 CLEAN + "\n'
        '                                       "B 54_601..54_800 CLEAN, single reading, no fork face, "\n'
        '                                       "F-20261002-03 not triggered; W85+ projection: A "\n'
        '                                       "213_004..215_003 CLEAN / B 54_801..55_000 REFUSED at "\n'
        '                                       "SEED_REGISTRY a158_truegap_ic=55_000 upper-edge "\n'
        '                                       "endpoint -> hit+1 restart 55_001..55_200, W74-B/W81 "\n'
        '                                       "edge family, disclosed for the next freezer); "\n'
        '                                       "W1..W81 finalizes ALL LANDED at this freeze (net "\n'
        '                                       "chain head 542,748, K=176,120, W81 bm-a r574); TWO "\n'
        '                                       "in-flight upstream seats: W82 bm-b (12/12 burned, "\n'
        '                                       "adopted by bm-b r575 S0 recovery, finalize pending) "\n'
        '                                       "+ W83 bm-c (burn in flight) -- finalize chain-pending "\n'
        '                                       "FAIL-CLOSED r307"),\n'
        '                            "a_seed_base": 211_004,        # law sec.4 W84 A: 211_004..213_003 (arithmetic continuation)\n'
        '                            "b_exit_seed_base": 54_601,   # law sec.4 W84 B: 54_601..54_800 (arithmetic continuation)\n'
        '                            "shard_subdir": "n1_w84", "out_name": "n1_w84_results.json",\n'
        '                            "engine_owner": "bm-a"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[84] landed (anchor=W83 entry tail, insert after)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W84 leg --------------
LEG84 = '''
    # --- W84 materializer face (r575 bm-a freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-a's
    #     twenty-first owned per machine-derive (engine_owner==bm-a
    #     rows 20 + candidate); wave 84 = first free number after the
    #     registered W83 row (bm-c r365). SEVENTY-FOURTH engine wave
    #     BY MACHINE-DERIVE (engine_owner rows 73 + candidate; prose
    #     ordinal -1 drift disclosed since W80, r359 law). Seat
    #     published=reserved MSG-20261002-1245-bma pushed to origin
    #     BEFORE this freeze (commit ad5df156c, r565 early-visibility
    #     law). TWO in-flight upstream seats at this freeze: W82 bm-b
    #     (12/12 burned, adopted by bm-b r575 S0 recovery, finalize
    #     pending) + W83 bm-c (burn in flight) -- finalize
    #     chain-pending FAIL-CLOSED r307 at run time. W1..W81
    #     finalizes ALL LANDED (net head 542,748, K=176,120, W81 bm-a
    #     r574). ADMIT receipt results/_r575bma_w84_band_gate.py;
    #     not a re-pick -- R250: W84 bands were never assigned --
    _set_wave(84)
    try:
        assert WAVE_CONFIGS[84]["a_seed_base"] == pf.N1_BANDS[84]["a"][0], \\
            "W84 A band drift vs law mirror"
        assert WAVE_CONFIGS[84]["b_exit_seed_base"] == \\
            pf.N1_BANDS[84]["b_exit"][0], "W84 B band drift vs law mirror"
        assert WAVE_CONFIGS[84].get("engine_owner") == \\
            pf.N1_BANDS[84].get("engine_owner") == "bm-a", \\
            "W84 engine_owner drift (law mirror parity)"
        w84_a = {A_SEED_BASE + j for j in range(A_N)}
        w84_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w84_a & w84_b), "W84 A/B band overlap"
        assert not (w84_a & reg_ints) and not (w84_b & reg_ints), \\
            "W84 hits SEED_REGISTRY"
        for nm, band in (("A", w84_a), ("B", w84_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W84 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W84 {nm} hits W1"
            assert not (band & probes), f"W84 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W73..W83 are
        # REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly (W80 bm-c r364; W81 bm-a r574;
        # W82 bm-b r574, in-file blocks byte-healed by bm-c r365;
        # W83 bm-c r365).
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
        assert pf.N1_BANDS[81] == {"a": (205_004, 207_003),
                                   "b_exit": (54_001, 54_200),
                                   "engine_owner": "bm-a"}, \\
            "registered W81 row parity drift (r307 two-state; bm-a r574)"
        assert pf.N1_BANDS[82] == {"a": (207_004, 209_003),
                                   "b_exit": (54_201, 54_400),
                                   "engine_owner": "bm-b"}, \\
            "registered W82 row parity drift (r307 two-state; bm-b r574)"
        assert pf.N1_BANDS[83] == {"a": (209_004, 211_003),
                                   "b_exit": (54_401, 54_600),
                                   "engine_owner": "bm-c"}, \\
            "registered W83 row parity drift (r307 two-state; bm-c r365)"
        # prior-wave disjointness incl. W48..W83 (all registered; the
        # W83 row is the direct arithmetic upstream of W84's bands).
        for wprev in REG_WAVES_ALL:
            assert not (w84_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W84 A hits W{wprev}"
            assert not (w84_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W84 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W84 clears it.
        n3r1_used84 = set(range(70_000, 70_006))
        assert not (w84_a & n3r1_used84) and not (w84_b & n3r1_used84), \\
            "W84 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w84_a & lfc_actual12) and not (w84_b & lfc_actual12), \\
            "W84 bands must clear the lfc actual draw range"
        assert not (w84_a & options_actual12) and \\
            not (w84_b & options_actual12), \\
            "W84 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W84 row, r575): BOTH SIDES ARITHMETIC
        # CONTINUATION from the registered W83 tails, zero skip -- the
        # arithmetic windows must be CLEAN (no registry points inside;
        # the skip-free face is forced by the ADMIT receipt, refusal
        # facts empty).
        assert WAVE_CONFIGS[84]["a_seed_base"] == 211_004 == \\
            pf.N1_BANDS[83]["a"][1] + 1, \\
            "W84 A must start at the registered W83 A end + 1 " \\
            "(arithmetic continuation window 211_004..213_003 CLEAN)"
        assert WAVE_CONFIGS[84]["b_exit_seed_base"] == 54_601 == \\
            pf.N1_BANDS[83]["b_exit"][1] + 1, \\
            "W84 B must start at the registered W83 B end + 1 " \\
            "(arithmetic continuation window 54_601..54_800 CLEAN)"
        arith_a84 = set(range(211_004, 213_004))
        arith_b84 = set(range(54_601, 54_801))
        assert not (arith_a84 & reg_ints) and not (arith_b84 & reg_ints), \\
            "W84 arithmetic windows must be CLEAN (zero-skip ADMIT face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W84-SHARD-0",
                                          "n1w84-0of12"), "W84 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W84-SHARD-11",
                                          "n1w84-11of12")
        assert SHARD_DIR.endswith("n1_w84") and OUT.endswith(
            "n1_w84_results.json"), "W84 path drift"
        for wprev in REG_WAVES_ALL:
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W84 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W84_PREREG.md")), \\
            "W84 per-wave prereg missing (materializer requirement)"
        # W84 finalize cumulative deps: W17..W81 outputs ALL PRESENT
        # (landed chain head 542,748, K=176,120, W81 bm-a r574; W82
        # bm-b + W83 bm-c = TWO in-flight upstream seats -- the
        # finalize merge loop derives the wave set from registry keys
        # at run time and stays FAIL-CLOSED on the not-yet-finalized
        # seats, r307 two-state law).
        for _depw in range(17, 82):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W84 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law):
        # prior-wave set derives from registry keys below 84 (no 15,
        # incl. 48..83 -- all registered, W82/W83 in-flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 84) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 84)], \\
            "W84 prior-wave set must derive from registry keys (no 15; " \\
            "incl. 48..83 -- W82/W83 registered, in-flight, FAIL-CLOSED)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W84 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    REG_WAVES_ALL = '[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 84)]'
    LEG84 = LEG84.replace('REG_WAVES_ALL', REG_WAVES_ALL)
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG84.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W84 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 5th face) ------
t2c, eol2c = load(FP2)
if '+ W84 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('          "probe-seed cluster leg, law sec.4 W83 row, "\n'
          '          "r365 bm-c] "\n'
          '          "+ T-141 s2 ')
    SEG84 = ('          "probe-seed cluster leg, law sec.4 W83 row, "\n'
             '          "r365 bm-c] "\n'
             '          "+ W84 materializer face [same guard set, dep=W17..W81 "\n'
             '          "outputs ALL PRESENT (landed chain head 542,748, "\n'
             '          "K=176,120, W81 bm-a r574), TWO in-flight upstream "\n'
             '          "seats W82 bm-b (12/12 burned, adopted by bm-b r575 "\n'
             '          "S0 recovery, finalize pending) + W83 bm-c (burn in "\n'
             '          "flight, FAIL-CLOSED r307 at run time), "\n'
             '          "SEVENTY-FOURTH ENGINE-OWNED WAVE BY MACHINE-DERIVE "\n'
             '          "(engine_owner rows 73 + candidate; prose ordinal -1 "\n'
             '          "drift disclosed since W80, r359 law) bm-a\'s "\n'
             '          "twenty-first owned claim per machine-derive "\n'
             '          "(engine_owner==bm-a rows 20 + candidate), "\n'
             '          "engine_owner=bm-a per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series "\n'
             '          "(wave 84 = first FREE number after the registered "\n'
             '          "W83 row; seat published=reserved "\n'
             '          "MSG-20261002-1245-bma pushed to origin BEFORE "\n'
             '          "this freeze, commit ad5df156c, r565 law), BOTH "\n'
             '          "SIDES ARITHMETIC CONTINUATION zero skip (A "\n'
             '          "211_004..213_003 CLEAN + B 54_601..54_800 CLEAN, "\n'
             '          "single reading, no fork face; W85+ projection "\n'
             '          "A 213_004..215_003 CLEAN / B 54_801..55_000 REFUSED "\n'
             '          "at SEED_REGISTRY a158_truegap_ic=55_000 upper-edge "\n'
             '          "endpoint -> hit+1 restart 55_001..55_200, W74-B/W81 "\n'
             '          "edge family, disclosed for the next freezer; ADMIT "\n'
             '          "receipt results/_r575bma_w84_band_gate.py; not a "\n'
             '          "free pick -- R250), N3-R1 used-seed leg, "\n'
             '          "probe-seed cluster leg, law sec.4 W84 row, "\n'
             '          "r575 bm-a] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG84, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W84 segment landed (insert after W83 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W84 row -------------------
ROW84 = """
- N1 波84（r575 bm-a 冻·prereg 时展行）：**第七十四枚引擎波·bm-a 第二十一枚自有波〔机面 derive：engine_owner 行 73+本候选／engine_owner==bm-a 行 20+本候选〕**·engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 同 W10-W83 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-a 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启免做·W44/W45/W48/W54/W57/W62/W64/W68/W73/W75/W77/W81 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 84=注册表 W83 行后首个自由号**（r511 表尾锁例冻结前 fetch 实核表尾时 W84 号位净空·pf 行+prereg 路径双查·origin 侧 vacancy 机验）·**席位公示=MSG-20261002-1245-bma（published=reserved r518-① 律·先于冻结 commit 推 origin=r565 早可见性律·commit ad5df156c）**·本窗实况=W81 finalize one-pass 已落账（bm-a r574·**542,748 净链头**·K=176,120 合并池）→W82+W83 两席在飞（W82 bm-b r575 S0 recovery 收养 12/12 烧毕待 finalize·W83 bm-c r365 冻·烧录中）——本波 finalize 链序前置=W82+W83 双落账（FAIL-CLOSED r307 两态律·本波 §5 锚滚动至 W81 实测值）〕·**带位（r535 机闸 derive 律·活注册表机证·ADMIT 回执=results/_r575bma_w84_band_gate.py）**：**A-ext seed=211_004..213_003**（**A 面算术续带零跳位**==W83 A 尾 211_003+1·步长逐字·CLEAN）；**B-ext exit seed=54_601..54_800**（**B 面算术续带零跳位**==W83 B 尾 54_600+1·步长逐字·CLEAN·双侧算术窗零拒绝点=单读法零分叉〔F-20261002-03 跳位语义分叉面不触发〕）·【机证净空——leg0 八十一行注册表形（81 注册行·表尾=W83 bm-c r365）+leg1-A/B 双侧算术位 CLEAN 零拒绝点+leg2 A/B 首净窗==算术位恒等+leg3 origin 号位净空机验（pf 行+prereg 路径双查）+SEED_REGISTRY 全键 160 值+N3-R1 已用种子带腿（70_000..70_005·MSG-183x r529 强制）+探针种子簇腿（95_000..95_003·r335 强制）+N2/N4+N2-W15 探针点+lfc/options 实际流腿】·**W85+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 213_004..215_003 **CLEAN**；B 54_801..55_000 于带上边缘撞 SEED_REGISTRY **a158_truegap_ic=55_000** 端点单点→越 hit 起窗 55_001..55_200（边缘端点族 W74-B/W81 先例·两读法恒同解零分叉）·R250：W84 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W84 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W84_PREREG.md（冻结件）·本波 §5 锚=W81 finalize 实测值（锚滚动律）·finalize 链序前置=W82 bm-b+W83 bm-c 两在飞上游席（FAIL-CLOSED r307 两态律）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce284\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW84.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W84 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    84: {"a": (211_004') == 1, 'FIX-B FAIL: W84 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W84"') == 1, 'FIX-B FAIL: W84 config not exactly once'
for w in range(58, 84):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W84 materializer face') == 2, \
    'FIX-B FAIL: W84 leg+summary must be exactly 2'
for w in range(48, 84):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce284\uff08') == 1, 'FIX-B FAIL: canon W84 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W84 added per face')

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
print('FREEZE_EDITS_OK 84')
