# -*- coding: utf-8 -*-
"""r576 bm-a W86 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening.

FIX-A (origin-blob freshness): zero deleted lines vs origin/main pre-edit.
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W85, bm-b's);
  every registered row signature survives exactly; exactly one new W86
  signature per face.
FIX-C (pure-insertion delta): zero deleted lines vs origin/main post-edit.

W86 = SEVENTY-SIXTH engine wave by MACHINE-DERIVE (engine_owner rows 75 +
candidate), bm-a's TWENTY-SECOND owned (engine_owner==bm-a rows 21 +
candidate). First free number after the registered W85 row (bm-b r576
five-face freeze, landed origin mid-window -- dual-state gate re-run
mode B converged on the same bands as the mode-A run). Seat
published=reserved MSG-20261002-1305-bma PUSHED before this freeze
(r565 early-visibility law; commit a2388eb5b).
Bands: A 215_004..217_003 / B 55_201..55_400 (both arithmetic continuation
from the registered W85 tails, zero skip, CLEAN; dual-state gate receipt
results/_r576bma_w86_band_gate.py mode A + mode B rc0).
W1..W84 finalizes ALL LANDED (net head 549,348, K=182,720; W83 restored to
bm-c canonical block per r518 fixup 3b3a7fe19). ONE in-flight upstream
seat: W85 bm-b (registered, burn in flight, finalize pending) -- FAIL-CLOSED
r307 at run time. W87+ projection: A 217_004..219_003 CLEAN; B
55_401..55_600 REFUSED in-band at SEED_REGISTRY grid_p1=55_500 (median-hit
family -> D-20261002-05 pin: hit+1 restart 55_501..55_700).
"""
import subprocess, sys, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREAT = 0x08000000

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
TARGETS = ['scripts/perpetual_faces.py', 'scripts/perpetual_faces_n1.py',
           'research/PERPETUAL_FACES.md']
for p in TARGETS:
    r = subprocess.run(['git', '-C', REPO, 'diff', 'origin/main', '--numstat', '--', p],
                       capture_output=True, creationflags=CREAT)
    for line in r.stdout.decode('utf-8', 'replace').strip().splitlines():
        add, dele, path = line.split('\t')
        if int(dele) > 0:
            sys.exit(f'STALE BASE (FIX-A abort): {p} shows {dele} deleted lines vs '
                     f'origin/main (another machine landed edits -- re-derive first)')
print('FIX-A: all 3 tracked edit targets fresh vs origin/main (zero deletions)')

# ---------------- survival baseline (FIX-B) -----------------------------------
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 86))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in range(58, 86)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 86)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[86] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '86: {"a": (215_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    85: {"a": (213_004, 215_003), "b_exit": (55_001, 55_200),\n'
          '         "engine_owner": "bm-b"},\n'
          '}\n')
    NEW = ('    85: {"a": (213_004, 215_003), "b_exit": (55_001, 55_200),\n'
           '         "engine_owner": "bm-b"},\n'
           '    # SEVENTY-SIXTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r576 bm-a\n'
           '    # freeze): engine_owner rows 75 + candidate; bm-a\'s\n'
           '    # twenty-second owned per machine-derive (engine_owner==bm-a\n'
           '    # rows 21 + candidate). Wave 86 = first free number after the\n'
           '    # registered W85 row (bm-b r576 five-face freeze landed\n'
           '    # mid-window; dual-state gate re-run mode B converged on the\n'
           '    # same bands as mode A; r511 tail-lock fetch-checked vacancy;\n'
           '    # seat published=reserved MSG-20261002-1305-bma PUSHED to\n'
           '    # origin before this freeze per r565 early-visibility law,\n'
           '    # commit a2388eb5b).\n'
           '    # W1..W84 finalizes ALL LANDED (net head 549,348, K=182,720;\n'
           '    # W83+W84 both landed bm-a r576 window; W83 block restored to\n'
           '    # bm-c canonical bytes per r518 origin-first-landed\n'
           '    # adjudication, fixup 3b3a7fe19). ONE in-flight upstream\n'
           '    # seat at this freeze: W85 bm-b (registered, burn in flight,\n'
           '    # finalize pending) -- finalize chain-pending FAIL-CLOSED\n'
           '    # r307 at run time.\n'
           '    # BOTH SIDES ARITHMETIC CONTINUATION from the registered W85\n'
           '    # row tails, zero skip: A 215_004..217_003 (= W85 A end\n'
           '    # 215_003 + 1) CLEAN. B 55_201..55_400 (= W85 B end 55_200 +\n'
           '    # 1) CLEAN. Dual-state gate mode A chain machine-verified:\n'
           '    # arithmetic 54_801..55_000 REFUSED at SEED_REGISTRY\n'
           '    # a158_truegap_ic=55_000 upper-edge endpoint -> hit+1 restart\n'
           '    # 55_001..55_200 == W85 published band -> skip-past-published\n'
           '    # (D-20261002-05 pin: past-hit start-window; edge-endpoint\n'
           '    # family W74-B/W81, both readings converge, no fork face).\n'
           '    # Machine-verified at prereg time\n'
           '    # (results/_r576bma_w86_band_gate.py dual-state ADMIT receipt\n'
           '    # vs the 83-row pre-W86 table + live SEED_REGISTRY values +\n'
           '    # probe cluster 95_000..95_003 r335 discovery leg + N3-R1\n'
           '    # used-seed band 70_000..70_005 MSG-183x r529 mandatory leg;\n'
           '    # origin slot vacancy machine-checked). W87+ projection: A\n'
           '    # 217_004..219_003 CLEAN; B 55_401..55_600 REFUSED in-band at\n'
           '    # SEED_REGISTRY grid_p1=55_500 median hit -> D-20261002-05\n'
           '    # pin: hit+1 restart 55_501..55_700 (window-step-chain reading\n'
           '    # 55_601..55_800 is BANNED by the pin; next freezer must\n'
           '    # re-derive, never transcribe).\n'
           '    # NOT a re-pick (R250: W86 bands were never assigned).\n'
           '    86: {"a": (215_004, 217_003), "b_exit": (55_201, 55_400),\n'
           '         "engine_owner": "bm-a"},\n'
           '}\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[86] landed (anchor=W85 row + closing brace)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[86] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '86: {"batch": "PERPETUAL-N1-W86"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w85", "out_name": "n1_w85_results.json",\n'
          '                            "engine_owner": "bm-b"},\n')
    NEW2 = A2 + (
        '                       86: {"batch": "PERPETUAL-N1-W86",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W86_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; SEVENTY-SIXTH ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 75 + candidate; prose "\n'
        '                                       "ordinal -1 drift disclosed since W80, r359 law), "\n'
        '                                       "own-series continuation per O-20261001-2355 sec.2 "\n'
        '                                       "(first-free-number law over the registered W85 row; "\n'
        '                                       "seat published=reserved MSG-20261002-1305-bma "\n'
        '                                       "PUSHED to origin BEFORE this freeze per r565 "\n'
        '                                       "early-visibility law, commit a2388eb5b), "\n'
        '                                       "engine_owner=bm-a, wave 86 BOTH SIDES ARITHMETIC "\n'
        '                                       "CONTINUATION zero skip (A 215_004..217_003 CLEAN + "\n'
        '                                       "B 55_201..55_400 CLEAN, single reading, no fork "\n'
        '                                       "face; dual-state gate mode A chain: B arithmetic "\n'
        '                                       "54_801..55_000 REFUSED at SEED_REGISTRY "\n'
        '                                       "a158_truegap_ic=55_000 edge endpoint -> hit+1 "\n'
        '                                       "55_001..55_200 == W85 published band -> skip-past, "\n'
        '                                       "D-20261002-05 pin; W87+ projection: A "\n'
        '                                       "217_004..219_003 CLEAN / B 55_401..55_600 REFUSED "\n'
        '                                       "in-band at grid_p1=55_500 median hit -> hit+1 "\n'
        '                                       "restart 55_501..55_700, disclosed for the next "\n'
        '                                       "freezer); W1..W84 finalizes ALL LANDED at this "\n'
        '                                       "freeze (net chain head 549,348, K=182,720, W83+W84 "\n'
        '                                       "both landed bm-a r576; W83 block restored to bm-c "\n'
        '                                       "canonical bytes r518 fixup 3b3a7fe19); ONE "\n'
        '                                       "in-flight upstream seat: W85 bm-b (registered, "\n'
        '                                       "burn in flight, finalize pending) -- finalize "\n'
        '                                       "chain-pending FAIL-CLOSED r307"),\n'
        '                            "a_seed_base": 215_004,        # law sec.4 W86 A: 215_004..217_003 (arithmetic continuation)\n'
        '                            "b_exit_seed_base": 55_201,   # law sec.4 W86 B: 55_201..55_400 (arithmetic continuation)\n'
        '                            "shard_subdir": "n1_w86", "out_name": "n1_w86_results.json",\n'
        '                            "engine_owner": "bm-a"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[86] landed (anchor=W85 entry tail, insert after)')

print('EDITS_1_2_OK')

# ---------------- edit 3: perpetual_faces_n1.py selftest W86 leg --------------
REG_WAVES_ALL = '[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 86)]'
LEG86 = '''
    # --- W86 materializer face (r576 bm-a freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-a's
    #     twenty-second owned per machine-derive (engine_owner==bm-a
    #     rows 21 + candidate); wave 86 = first free number after the
    #     registered W85 row (bm-b r576 five-face freeze landed
    #     mid-window; dual-state gate converged). SEVENTY-SIXTH engine
    #     wave BY MACHINE-DERIVE (engine_owner rows 75 + candidate;
    #     prose ordinal -1 drift disclosed since W80, r359 law). Seat
    #     published=reserved MSG-20261002-1305-bma pushed to origin
    #     BEFORE this freeze (commit a2388eb5b, r565 early-visibility
    #     law). ONE in-flight upstream seat at this freeze: W85 bm-b
    #     (registered, burn in flight, finalize pending) -- finalize
    #     chain-pending FAIL-CLOSED r307 at run time. W1..W84
    #     finalizes ALL LANDED (net head 549,348, K=182,720, W83+W84
    #     both landed bm-a r576 window; W83 block restored to bm-c
    #     canonical bytes per r518 fixup 3b3a7fe19). ADMIT receipt
    #     results/_r576bma_w86_band_gate.py (dual-state: mode A
    #     skip-past-published + mode B arithmetic continuation, both
    #     rc0 on the same bands); not a re-pick -- R250: W86 bands
    #     were never assigned --
    _set_wave(86)
    try:
        assert WAVE_CONFIGS[86]["a_seed_base"] == pf.N1_BANDS[86]["a"][0], \\
            "W86 A band drift vs law mirror"
        assert WAVE_CONFIGS[86]["b_exit_seed_base"] == \\
            pf.N1_BANDS[86]["b_exit"][0], "W86 B band drift vs law mirror"
        assert WAVE_CONFIGS[86].get("engine_owner") == \\
            pf.N1_BANDS[86].get("engine_owner") == "bm-a", \\
            "W86 engine_owner drift (law mirror parity)"
        w86_a = {A_SEED_BASE + j for j in range(A_N)}
        w86_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w86_a & w86_b), "W86 A/B band overlap"
        assert not (w86_a & reg_ints) and not (w86_b & reg_ints), \\
            "W86 hits SEED_REGISTRY"
        for nm, band in (("A", w86_a), ("B", w86_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W86 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W86 {nm} hits W1"
            assert not (band & probes), f"W86 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W73..W85 are
        # REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly (W84 bm-a r575; W85 bm-b r576).
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
        assert pf.N1_BANDS[84] == {"a": (211_004, 213_003),
                                   "b_exit": (54_601, 54_800),
                                   "engine_owner": "bm-a"}, \\
            "registered W84 row parity drift (r307 two-state; bm-a r575)"
        assert pf.N1_BANDS[85] == {"a": (213_004, 215_003),
                                   "b_exit": (55_001, 55_200),
                                   "engine_owner": "bm-b"}, \\
            "registered W85 row parity drift (r307 two-state; bm-b r576)"
        # prior-wave disjointness incl. W48..W85 (all registered; the
        # W85 row is the direct arithmetic upstream of W86's bands).
        for wprev in REG_WAVES_ALL:
            assert not (w86_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W86 A hits W{wprev}"
            assert not (w86_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W86 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W86 clears it.
        n3r1_used86 = set(range(70_000, 70_006))
        assert not (w86_a & n3r1_used86) and not (w86_b & n3r1_used86), \\
            "W86 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w86_a & lfc_actual12) and not (w86_b & lfc_actual12), \\
            "W86 bands must clear the lfc actual draw range"
        assert not (w86_a & options_actual12) and \\
            not (w86_b & options_actual12), \\
            "W86 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W86 row, r576): BOTH SIDES ARITHMETIC
        # CONTINUATION from the registered W85 tails, zero skip -- the
        # arithmetic windows must be CLEAN (no registry points inside;
        # zero-skip ADMIT face forced by the dual-state gate receipt).
        assert WAVE_CONFIGS[86]["a_seed_base"] == 215_004 == \\
            pf.N1_BANDS[85]["a"][1] + 1, \\
            "W86 A must start at the registered W85 A end + 1 " \\
            "(arithmetic continuation window 215_004..217_003 CLEAN)"
        assert WAVE_CONFIGS[86]["b_exit_seed_base"] == 55_201 == \\
            pf.N1_BANDS[85]["b_exit"][1] + 1, \\
            "W86 B must start at the registered W85 B end + 1 " \\
            "(arithmetic continuation window 55_201..55_400 CLEAN; " \\
            "dual-state gate mode A chain: 54_801..55_000 point-refused " \\
            "at a158_truegap_ic=55_000 -> hit+1 55_001..55_200 == W85 " \\
            "published band -> skip-past, D-20261002-05 pin)"
        arith_a86 = set(range(215_004, 217_004))
        arith_b86 = set(range(55_201, 55_401))
        assert not (arith_a86 & reg_ints) and not (arith_b86 & reg_ints), \\
            "W86 arithmetic windows must be CLEAN (zero-skip ADMIT face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W86-SHARD-0",
                                          "n1w86-0of12"), "W86 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W86-SHARD-11",
                                          "n1w86-11of12")
        assert SHARD_DIR.endswith("n1_w86") and OUT.endswith(
            "n1_w86_results.json"), "W86 path drift"
        for wprev in REG_WAVES_ALL:
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W86 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W86_PREREG.md")), \\
            "W86 per-wave prereg missing (materializer requirement)"
        # W86 finalize cumulative deps: W17..W84 outputs ALL PRESENT
        # (landed chain head 549,348, K=182,720, W83+W84 both landed
        # bm-a r576 window; W85 bm-b = ONE in-flight upstream seat --
        # the finalize merge loop derives the wave set from registry
        # keys at run time and stays FAIL-CLOSED on the not-yet-
        # finalized seat, r307 two-state law).
        for _depw in range(17, 85):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W86 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law):
        # prior-wave set derives from registry keys below 86 (no 15,
        # incl. 48..85 -- all registered, W85 in-flight burn,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 86) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 86)], \\
            "W86 prior-wave set must derive from registry keys (no 15; " \\
            "incl. 48..85 -- W85 registered, burn in flight, FAIL-CLOSED)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W86 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    LEG86X = LEG86.replace('REG_WAVES_ALL', REG_WAVES_ALL)
    t2b = t2b.replace(rep_probe, LEG86X.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W86 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment ----------------------
t2c, eol2c = load(FP2)
if '+ W86 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('          "r576 bm-b] "\n'
          '          "+ T-141 s2 ')
    SEG86 = ('          "r576 bm-b] "\n'
             '          "+ W86 materializer face [same guard set, dep=W17..W84 "\n'
             '          "outputs ALL PRESENT (landed chain head 549,348, "\n'
             '          "K=182,720, W83+W84 both landed bm-a r576 window, W83 "\n'
             '          "block restored to bm-c canonical bytes per r518 fixup "\n'
             '          "3b3a7fe19), ONE in-flight upstream seat W85 bm-b "\n'
             '          "(registered five-face freeze, burn in flight, "\n'
             '          "FAIL-CLOSED r307 at run time), SEVENTY-SIXTH "\n'
             '          "ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner "\n'
             '          "rows 75 + candidate; prose ordinal -1 drift disclosed "\n'
             '          "since W80, r359 law) bm-a\'s twenty-second owned "\n'
             '          "claim per machine-derive (engine_owner==bm-a rows 21 "\n'
             '          "+ candidate), engine_owner=bm-a per engine de-throttle "\n'
             '          "law O-20261001-2355 sec.2 own-continuous-series "\n'
             '          "(wave 86 = first FREE number after the registered "\n'
             '          "W85 row; seat published=reserved "\n'
             '          "MSG-20261002-1305-bma pushed to origin BEFORE this "\n'
             '          "freeze, commit a2388eb5b, r565 law), BOTH SIDES "\n'
             '          "ARITHMETIC CONTINUATION zero skip (A 215_004..217_003 "\n'
             '          "CLEAN + B 55_201..55_400 CLEAN, single reading, no "\n'
             '          "fork face; dual-state gate mode A chain: B arithmetic "\n'
             '          "54_801..55_000 REFUSED at SEED_REGISTRY "\n'
             '          "a158_truegap_ic=55_000 upper-edge endpoint -> hit+1 "\n'
             '          "restart 55_001..55_200 == W85 published band -> "\n'
             '          "skip-past-published, D-20261002-05 pin; W87+ projection "\n'
             '          "A 217_004..219_003 CLEAN / B 55_401..55_600 REFUSED "\n'
             '          "in-band at SEED_REGISTRY grid_p1=55_500 median hit -> "\n'
             '          "D-20261002-05 pin: hit+1 restart 55_501..55_700, "\n'
             '          "disclosed for the next freezer; ADMIT receipt "\n'
             '          "results/_r576bma_w86_band_gate.py dual-state rc0; not "\n'
             '          "a free pick -- R250), N3-R1 used-seed leg, "\n'
             '          "probe-seed cluster leg, law sec.4 W86 row, "\n'
             '          "r576 bm-a] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG86, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W86 segment landed (insert after W85 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W86 row -------------------
ROW86 = """
- N1 波86（r576 bm-a 冻·prereg 时展行）：**第七十六枚引擎波·bm-a 第二十二枚自有波〔机面 derive：engine_owner 行 75+本候选／engine_owner==bm-a 行 21+本候选〕**·engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 同 W10-W85 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-a 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启免做·W44/W45/W48/W54/W57/W62/W64/W68/W73/W75/W77/W81/W84 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 86=注册表 W85 行后首个自由号**（r511 表尾锁例冻结前 fetch 实核表尾时 W86 号位净空·pf 行+prereg 路径双查·origin 侧 vacancy 机验；**W85=表尾行 bm-b r576 五面冻结已注册·烧录在飞·finalize 未落账**——席位=MSG-20261002-1258-bmb·published=reserved r518-① 律·本机不占 85 号位·**席位公示=MSG-20261002-1305-bma（published=reserved r518-① 律·先于冻结 commit 推 origin=r565 早可见性律·commit a2388eb5b）**）·本窗实况=W83+W84 finalize 双落账（bm-a r576 one-pass·**549,348 净链头**·K=182,720 合并池——W83 收口按 r518 origin-时序面裁=恢复 bm-c 首落正典块〔r481 AA 信封面裁定·fixup 3b3a7fe19〕）→W85 bm-b 席在飞——本波 finalize 链序前置=W85 单落账（FAIL-CLOSED r307 两态律·本波 §5 锚滚动至 W84 实测值）〕·**带位（r535 机闸 derive 律·活注册表机证·双态门·ADMIT 回执=results/_r576bma_w86_band_gate.py 双态 rc0）**：**A-ext seed=215_004..217_003**（**A 面算术续带零跳位**==W85 行 A 尾 215_003+1·步长 2_000·CLEAN）；**B-ext exit seed=55_201..55_400**（**B 面算术续带零跳位**==W85 行 B 尾 55_200+1·步长 200·CLEAN·双侧算术窗零拒绝点=单读法零分叉〔F-20261002-03 跳位语义分叉面不触发〕·**state A 链机证**：算术位 54_801..55_000 于带上边缘撞 SEED_REGISTRY **a158_truegap_ic=55_000** 端点单点→越 hit 起窗 55_001..55_200==W85 公示带 reserved face→skip-past-published〔边缘端点族 W74-B/W81 先例·两读法恒同解；D-20261002-05 集团钉死=越 hit 起窗〕）·【机证净空——leg0 八十三行注册表形（83 注册行·表尾=W85 bm-b r576）+leg0b bm-b W85 席 MSG origin 在场机验（双路径收 processed/ 归档位）+leg1 双侧算术位 CLEAN 零拒绝点（state B）／skip-past-published 链（state A）+leg2 A/B 首净窗==候选恒等+leg3 origin 号位净空机验（pf 行+prereg 路径双查）+SEED_REGISTRY 全键 160 值+N3-R1 已用种子带腿（70_000..70_005·MSG-183x r529 强制）+探针种子簇腿（95_000..95_003·r335 强制）+N2/N4+N2-W15 探针点+lfc/options 实际流腿】·**W87+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 217_004..219_003 **CLEAN**；B 55_401..55_600 于带内撞 **SEED_REGISTRY grid_p1=55_500** 中位点→**非边缘端点命中族·两读法分叉面**——D-20261002-05 集团钉死=**越 hit 起窗 55_501..55_700**（禁窗步链读法 55_601..55_800；W87 prereg 窗机闸复核 r335 律）。R250：W86 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W86 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W86_PREREG.md（冻结件）·本波 §5 锚=W84 finalize 实测值（锚滚动律）·finalize 链序前置=W85 bm-b 单在飞上游席（FAIL-CLOSED r307 两态律）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce286\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW86.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W86 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    86: {"a": (215_004') == 1, 'FIX-B FAIL: W86 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W86"') == 1, 'FIX-B FAIL: W86 config not exactly once'
for w in range(58, 86):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W86 materializer face') == 2, \
    'FIX-B FAIL: W86 leg+summary must be exactly 2'
for w in range(48, 86):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce286\uff08') == 1, 'FIX-B FAIL: canon W86 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W86 added per face')

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
print('FREEZE_EDITS_OK 86')

