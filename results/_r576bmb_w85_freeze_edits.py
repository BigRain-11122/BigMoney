# -*- coding: utf-8 -*-
"""r576 bm-b W85 freeze edits -- MSG-0640 INSERT-NOT-REPLACE hardening
(r561/r566/r568/r570/r571/r574/r575 lineage), adopted r575 half-product.

FIX-A (origin-blob freshness): every tracked edit target must show zero
  deleted lines vs origin/main BEFORE any edit runs (r559 stale-base cure).
FIX-B (anchor survival): anchors = the LAST REGISTERED row (W84, bm-a's);
  after every edit each registered row signature must survive exactly
  (count unchanged) with exactly one new W85 signature added.
FIX-C (pure-insertion delta): post-edit, `git diff origin/main --numstat`
  must show ZERO deleted lines for each edited file.

W85 = SEVENTY-FIFTH engine wave by MACHINE-DERIVE (engine_owner rows
74 + candidate; prose ordinal -1 drift disclosed since W80 -- machine:
W80=70th/W81=71st/W82=72nd/W83=73rd/W84=74th, r359 counts-from-gate
law), bm-b's TWENTY-EIGHTH owned per machine-derive
(engine_owner==bm-b rows 27 + candidate). First free number after the
registered W84 row (bm-a r575 freeze, landed origin).
Seat published=reserved MSG-20261002-1258-bmb PUSHED to origin in the
r575 window BEFORE this freeze (r565 early-visibility law; seat commit
ce51adf70). CROSS-ROUND freeze: the r575 session died pre-freeze
(state round_no stall 573 + r575-labeled commits = r529 sudden-death
diagnosis); this r576 round adopts the half-product with anchors
rolled W82->W83 per anchor-roll law (W83 finalize landed in the bm-c
r366 window 12:59) -- disclosed deviation from the r565 same-window
law.

Bands: A 213_004..215_003 (== W84 A end 213_003 + 1, arithmetic
continuation zero skip, CLEAN) / B 55_001..55_200 (arithmetic
54_801..55_000 REFUSED at SEED_REGISTRY a158_truegap_ic=55_000
upper-edge endpoint -> hit+1 restart per D-20261002-05 pinned
past-hit-start-window semantics; both readings converge = no fork
face, F-20261002-03 not triggered; W74-B/W81 edge-endpoint family).
ONE in-flight upstream seat at this freeze: W84 bm-a (11/12 burned on
origin, finalize not landed) -- finalize chain-pending FAIL-CLOSED
r307. W1..W83 finalizes ALL LANDED (net head 547,148, K=180,520,
W83 bm-c r365/r366).
ADMIT receipt results/_r575bmb_w85_band_gate.py (dual-state: r575
mode A + r576 mode B re-run rc0 vs the live 82-row table); banned
gate ADMIT 0 matched. W86+ projection disclosed by the gate: A
215_004..217_003 CLEAN; B 55_201..55_400 CLEAN.
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
REG_WAVES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + list(range(16, 85))
pf0 = load(os.path.join(REPO, 'scripts/perpetual_faces.py'))[0]
n1_0 = load(os.path.join(REPO, 'scripts/perpetual_faces_n1.py'))[0]
canon0 = load(os.path.join(REPO, 'research/PERPETUAL_FACES.md'))[0]
BASE_SIGS = (
    {w: pf0.count(f'    {w}: {{"a":') for w in REG_WAVES}
    | {f'w{w}leg': n1_0.count(f'W{w} materializer face') for w in
       range(58, 85)}
    | {w: canon0.count(f'- N1 \u6ce2{w}\uff08') for w in range(48, 85)}
)
assert all(v == 1 for w, v in BASE_SIGS.items() if isinstance(w, int)), \
    f'BASELINE FAIL (pf/canon rows): {BASE_SIGS}'
assert all(v == 2 for k, v in BASE_SIGS.items() if isinstance(k, str)), \
    f'BASELINE FAIL (legs must be leg+summary == 2): {BASE_SIGS}'

# ---------------- edit 1: perpetual_faces.py N1_BANDS[85] --------------------
FP1 = os.path.join(REPO, 'scripts/perpetual_faces.py')
t1, eol1 = load(FP1)
if '85: {"a": (213_004' in t1:
    print('edit1 already landed (idempotent skip)')
else:
    A1 = ('    84: {"a": (211_004, 213_003), "b_exit": (54_601, 54_800),\n'
          '         "engine_owner": "bm-a"},\n')
    NEW = ('    84: {"a": (211_004, 213_003), "b_exit": (54_601, 54_800),\n'
           '         "engine_owner": "bm-a"},\n'
           '    # SEVENTY-FIFTH ENGINE-OWNED WAVE BY MACHINE-DERIVE (r576 bm-b\n'
           '    # freeze): engine_owner rows 74 + candidate; bm-b\'s\n'
           '    # twenty-eighth owned per machine-derive (engine_owner==bm-b\n'
           '    # rows 27 + candidate). Wave 85 = first free number after the\n'
           '    # registered W84 row (r511 tail-lock, fetch-checked vacancy;\n'
           '    # seat published=reserved MSG-20261002-1258-bmb PUSHED to\n'
           '    # origin in the r575 window BEFORE this freeze per r565\n'
           '    # early-visibility law, seat commit ce51adf70). CROSS-ROUND\n'
           '    # freeze: r575 session died pre-freeze (state round_no stall\n'
           '    # + r575-labeled commits = r529 sudden-death diagnosis law);\n'
           '    # r576 adopts the half-product with anchors rolled W82->W83\n'
           '    # per anchor-roll law (W83 finalize landed, bm-c r366 window).\n'
           '    # W1..W83 finalizes ALL LANDED (net head 547,148, K=180,520,\n'
           '    # W83 bm-c r365/r366); ONE in-flight upstream seat at this\n'
           '    # freeze: W84 bm-a (11/12 burned on origin, finalize not\n'
           '    # landed) -- finalize chain-pending FAIL-CLOSED r307.\n'
           '    # A-side ARITHMETIC CONTINUATION from the W84 row tail, zero\n'
           '    # skip: A 213_004..215_003 (= W84 A end 213_003 + 1) CLEAN.\n'
           '    # B-side FORCED SKIP past-hit restart: arithmetic 54_801..55_000\n'
           '    # REFUSED at SEED_REGISTRY a158_truegap_ic=55_000 upper-edge\n'
           '    # endpoint -> hit+1 restart 55_001..55_200 per D-20261002-05\n'
           '    # pinned semantics (past-hit start-window), both readings\n'
           '    # converge = no fork face, F-20261002-03 not triggered\n'
           '    # (W74-B/W81 edge-endpoint family).\n'
           '    # Machine-verified at prereg time\n'
           '    # (results/_r575bmb_w85_band_gate.py ADMIT receipt, dual-state:\n'
           '    # r575 mode A + r576 mode B re-run rc0 vs the 82-row pre-W85\n'
           '    # table + live SEED_REGISTRY values + probe cluster\n'
           '    # 95_000..95_003 r335 discovery leg + N3-R1 used-seed band\n'
           '    # 70_000..70_005 MSG-183x r529 mandatory leg; origin slot\n'
           '    # vacancy machine-checked). W86+ gate projection: A\n'
           '    # 215_004..217_003 CLEAN; B 55_201..55_400 CLEAN.\n'
           '    # NOT a re-pick (R250: W85 bands were never assigned).\n'
           '    85: {"a": (213_004, 215_003), "b_exit": (55_001, 55_200),\n'
           '         "engine_owner": "bm-b"},\n')
    t1 = rep(t1, A1, NEW, eol1, 'pf-bands')
    save(FP1, t1)
    print('edit1 perpetual_faces.py N1_BANDS[85] landed (anchor=W84 row, insert after)')

# ---------------- edit 2: perpetual_faces_n1.py WAVE_CONFIGS[85] --------------
FP2 = os.path.join(REPO, 'scripts/perpetual_faces_n1.py')
t2, eol2 = load(FP2)
if '85: {"batch": "PERPETUAL-N1-W85"' in t2:
    print('edit2 already landed (idempotent skip)')
else:
    A2 = ('                            "shard_subdir": "n1_w84", "out_name": "n1_w84_results.json",\n'
          '                            "engine_owner": "bm-a"},\n')
    NEW2 = A2 + (
        '                       85: {"batch": "PERPETUAL-N1-W85",\n'
        '                            "prereg": ("research/PERPETUAL_N1_W85_PREREG.md (wave-level frozen "\n'
        '                                       "pre-run; design = frozen v1 null calibration verbatim, "\n'
        '                                       "new seed bands only; SEVENTY-FIFTH ENGINE-OWNED WAVE BY "\n'
        '                                       "MACHINE-DERIVE (engine_owner rows 74 + candidate; prose "\n'
        '                                       "ordinal -1 drift disclosed since W80, r359 law), "\n'
        '                                       "bm-b\'s twenty-eighth owned per machine-derive "\n'
        '                                       "(engine_owner==bm-b rows 27 + candidate), own-series "\n'
        '                                       "continuation per O-20261001-2355 sec.2 (first-free-number "\n'
        '                                       "law over the registered W84 row; seat published=reserved "\n'
        '                                       "MSG-20261002-1258-bmb PUSHED to origin in the r575 "\n'
        '                                       "window BEFORE this freeze per r565 early-visibility "\n'
        '                                       "law, seat commit ce51adf70; CROSS-ROUND freeze in r576: "\n'
        '                                       "r575 session died pre-freeze [r529 law], anchors rolled "\n'
        '                                       "W82->W83 per anchor-roll law after W83 finalize landed "\n'
        '                                       "[bm-c r366 window]), engine_owner=bm-b, wave 85 "\n'
        '                                       "A-SIDE ARITHMETIC CONTINUATION zero skip (A "\n'
        '                                       "213_004..215_003 CLEAN) + B-SIDE forced skip past-hit "\n'
        '                                       "restart per D-20261002-05 pinned semantics (arithmetic "\n'
        '                                       "54_801..55_000 REFUSED at SEED_REGISTRY "\n'
        '                                       "a158_truegap_ic=55_000 upper-edge endpoint -> hit+1 "\n'
        '                                       "restart 55_001..55_200, both readings converge, no "\n'
        '                                       "fork face; W86+ projection: A 215_004..217_003 CLEAN / "\n'
        '                                       "B 55_201..55_400 CLEAN, disclosed for the next "\n'
        '                                       "freezer); W1..W83 finalizes ALL LANDED at this freeze "\n'
        '                                       "(net chain head 547,148, K=180,520, W83 bm-c "\n'
        '                                       "r365/r366); ONE in-flight upstream seat: W84 bm-a "\n'
        '                                       "(11/12 burned on origin, finalize pending) -- finalize "\n'
        '                                       "chain-pending FAIL-CLOSED r307"),\n'
        '                            "a_seed_base": 213_004,        # law sec.4 W85 A: 213_004..215_003 (arithmetic continuation)\n'
        '                            "b_exit_seed_base": 55_001,    # law sec.4 W85 B: 55_001..55_200 (hit+1 restart past a158_truegap_ic=55_000)\n'
        '                            "shard_subdir": "n1_w85", "out_name": "n1_w85_results.json",\n'
        '                            "engine_owner": "bm-b"},\n')
    t2 = rep(t2, A2, NEW2, eol2, 'n1-configs')
    save(FP2, t2)
    print('edit2 WAVE_CONFIGS[85] landed (anchor=W84 entry tail, insert after)')

# ---------------- edit 3: perpetual_faces_n1.py selftest W85 leg --------------
LEG85 = '''
    # --- W85 materializer face (r576 bm-b freeze, own-series law
    #     under CEO de-throttle order O-20261001-2355 sec.2): bm-b's
    #     twenty-eighth owned per machine-derive (engine_owner==bm-b
    #     rows 27 + candidate); wave 85 = first free number after the
    #     registered W84 row (bm-a r575). SEVENTY-FIFTH engine wave
    #     BY MACHINE-DERIVE (engine_owner rows 74 + candidate; prose
    #     ordinal -1 drift disclosed since W80, r359 law). Seat
    #     published=reserved MSG-20261002-1258-bmb pushed to origin in
    #     the r575 window BEFORE this freeze (seat commit ce51adf70,
    #     r565 early-visibility law). CROSS-ROUND freeze: r575 session
    #     died pre-freeze (r529 law), r576 adopts with anchors rolled
    #     W82->W83 per anchor-roll law. ONE in-flight upstream seat at
    #     this freeze: W84 bm-a (11/12 burned on origin, finalize not
    #     landed) -- finalize chain-pending FAIL-CLOSED r307 at run
    #     time. W1..W83 finalizes ALL LANDED (net head 547,148,
    #     K=180,520, W83 bm-c r365/r366). ADMIT receipt
    #     results/_r575bmb_w85_band_gate.py (dual-state r575 mode A +
    #     r576 mode B re-run rc0); not a re-pick -- R250: W85 bands
    #     were never assigned --
    _set_wave(85)
    try:
        assert WAVE_CONFIGS[85]["a_seed_base"] == pf.N1_BANDS[85]["a"][0], \\
            "W85 A band drift vs law mirror"
        assert WAVE_CONFIGS[85]["b_exit_seed_base"] == \\
            pf.N1_BANDS[85]["b_exit"][0], "W85 B band drift vs law mirror"
        assert WAVE_CONFIGS[85].get("engine_owner") == \\
            pf.N1_BANDS[85].get("engine_owner") == "bm-b", \\
            "W85 engine_owner drift (law mirror parity)"
        w85_a = {A_SEED_BASE + j for j in range(A_N)}
        w85_b = {B_EXIT_SEED_BASE + j for j in range(B_N)}
        assert not (w85_a & w85_b), "W85 A/B band overlap"
        assert not (w85_a & reg_ints) and not (w85_b & reg_ints), \\
            "W85 hits SEED_REGISTRY"
        for nm, band in (("A", w85_a), ("B", w85_b)):
            assert not (band & v1_a) and not (band & v1_b), f"W85 {nm} hits v1"
            assert not (band & w1_a) and not (band & w1_b), f"W85 {nm} hits W1"
            assert not (band & probes), f"W85 {nm} hits probe seeds"
        # registered declared-band parity (r307 two-state): W73..W84 are
        # REGISTERED rows now -- pinned constants must equal the
        # registered rows exactly (W80 bm-c r364; W81 bm-a r574;
        # W82 bm-b r574, in-file blocks byte-healed by bm-c r365;
        # W83 bm-c r365; W84 bm-a r575).
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
        # prior-wave disjointness incl. W48..W84 (all registered; the
        # W84 row is the direct arithmetic upstream of W85's A side).
        for wprev in REG_WAVES_ALL:
            assert not (w85_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j
                                 for j in range(A_N)}), f"W85 A hits W{wprev}"
            assert not (w85_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j
                                  for j in range(B_N)}), f"W85 B hits W{wprev}"
        # N3-R1 used-seed band leg (MSG-183x mandatory) -- W85 clears it.
        n3r1_used85 = set(range(70_000, 70_006))
        assert not (w85_a & n3r1_used85) and not (w85_b & n3r1_used85), \\
            "W85 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"
        # actual-draw-range avoidance (leg-3e family)
        assert not (w85_a & lfc_actual12) and not (w85_b & lfc_actual12), \\
            "W85 bands must clear the lfc actual draw range"
        assert not (w85_a & options_actual12) and \\
            not (w85_b & options_actual12), \\
            "W85 bands must clear the options_wave2 actual draw range"
        # band facts (law sec.4 W85 row, r576): A-side ARITHMETIC
        # CONTINUATION from the registered W84 tail, zero skip -- the
        # A arithmetic window must be CLEAN; B-side FORCED SKIP
        # past-hit restart per D-20261002-05 pinned semantics -- the
        # B arithmetic window must be refused by exactly one registry
        # point at its upper edge (forced skip, R250; not a free pick).
        assert WAVE_CONFIGS[85]["a_seed_base"] == 213_004 == \\
            pf.N1_BANDS[84]["a"][1] + 1, \\
            "W85 A must start at the registered W84 A end + 1 " \\
            "(arithmetic continuation window 213_004..215_003 CLEAN)"
        assert WAVE_CONFIGS[85]["b_exit_seed_base"] == 55_001 == 55_000 + 1, \\
            "W85 B must start at hit+1 (past-hit start-window, " \\
            "D-20261002-05 pinned semantics)"
        arith_a85 = set(range(213_004, 215_004))
        arith_b85 = set(range(54_801, 55_001))
        assert not (arith_a85 & reg_ints), \\
            "W85 A arithmetic window must be CLEAN (zero-skip ADMIT face)"
        assert arith_b85 & reg_ints == {55_000}, \\
            "W85 B arithmetic window must be refused by exactly the " \\
            "single registry point a158_truegap_ic=55_000 at the upper " \\
            "edge (forced skip machine-proven, R250; both readings " \\
            "converge = no fork face)"
        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W85-SHARD-0",
                                          "n1w85-0of12"), "W85 entry identity"
        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W85-SHARD-11",
                                          "n1w85-11of12")
        assert SHARD_DIR.endswith("n1_w85") and OUT.endswith(
            "n1_w85_results.json"), "W85 path drift"
        for wprev in REG_WAVES_ALL:
            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(
                PATHS.results_dir, "p2cal_ext",
                WAVE_CONFIGS[wprev]["shard_subdir"])), \\
                f"W85 shard dir collides with W{wprev}"
        assert os.path.exists(os.path.join(
            PATHS.root, "research", "PERPETUAL_N1_W85_PREREG.md")), \\
            "W85 per-wave prereg missing (materializer requirement)"
        # W85 finalize cumulative deps: W17..W83 outputs ALL PRESENT
        # (landed chain head 547,148, K=180,520, W83 bm-c r365/r366;
        # W84 bm-a = ONE in-flight upstream seat -- the finalize merge
        # loop derives the wave set from registry keys at run time and
        # stays FAIL-CLOSED on the not-yet-finalized seat, r307
        # two-state law).
        for _depw in range(17, 84):
            assert os.path.exists(os.path.join(
                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\
                f"W85 finalize cumulative dep (W{_depw} output) missing"
        # finalize wave-set derivation face (r511 derive law):
        # prior-wave set derives from registry keys below 85 (no 15,
        # incl. 48..84 -- all registered, W84 in-flight,
        # FAIL-CLOSED at run time).
        assert sorted(w for w in WAVE_CONFIGS if w < 85) == \\
            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\
            [w for w in range(16, 85)], \\
            "W85 prior-wave set must derive from registry keys (no 15; " \\
            "incl. 48..84 -- W84 registered, in-flight, FAIL-CLOSED)"
        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"
    finally:
        _set_wave(2)
'''
t2b, eol2b = load(FP2)
if 'W85 materializer face' in t2b:
    print('edit3 already landed (idempotent skip)')
else:
    REG_WAVES_ALL = '[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + [w for w in range(16, 85)]'
    LEG85 = LEG85.replace('REG_WAVES_ALL', REG_WAVES_ALL)
    A3 = '\n    # --- T-141 s2 lane face'
    rep_probe = A3.replace('\n', eol2b)
    assert t2b.count(rep_probe) == 1, f'selftest anchor not unique: {t2b.count(rep_probe)}'
    t2b = t2b.replace(rep_probe, LEG85.replace('\n', eol2b) + rep_probe)
    save(FP2, t2b)
    print('edit3 selftest W85 leg landed (insert before T-141 lane face)')

# ---------------- edit 5: n1.py selftest SUMMARY segment (the 5th face) ------
t2c, eol2c = load(FP2)
if '+ W85 materializer face' in t2c:
    print('edit5 already landed (idempotent skip)')
else:
    A5 = ('          "probe-seed cluster leg, law sec.4 W84 row, "\n'
          '          "r575 bm-a] "\n'
          '          "+ T-141 s2 ')
    SEG85 = ('          "probe-seed cluster leg, law sec.4 W84 row, "\n'
             '          "r575 bm-a] "\n'
             '          "+ W85 materializer face [same guard set, dep=W17..W83 "\n'
             '          "outputs ALL PRESENT (landed chain head 547,148, "\n'
             '          "K=180,520, W83 bm-c r365/r366), ONE in-flight upstream "\n'
             '          "seat W84 bm-a (11/12 burned on origin, FAIL-CLOSED r307 "\n'
             '          "at run time), SEVENTY-FIFTH ENGINE-OWNED WAVE BY "\n'
             '          "MACHINE-DERIVE (engine_owner rows 74 + candidate; prose "\n'
             '          "ordinal -1 drift disclosed since W80, r359 law) bm-b\'s "\n'
             '          "twenty-eighth owned claim per machine-derive "\n'
             '          "(engine_owner==bm-b rows 27 + candidate), "\n'
             '          "engine_owner=bm-b per engine de-throttle law "\n'
             '          "O-20261001-2355 sec.2 own-continuous-series (wave 85 = "\n'
             '          "first FREE number after the registered W84 row; seat "\n'
             '          "published=reserved MSG-20261002-1258-bmb pushed to "\n'
             '          "origin in the r575 window BEFORE this freeze, seat "\n'
             '          "commit ce51adf70; CROSS-ROUND freeze in r576 after the "\n'
             '          "r575 session died pre-freeze [r529 law], anchors rolled "\n'
             '          "W82->W83 per anchor-roll law), A-SIDE ARITHMETIC "\n'
             '          "CONTINUATION zero skip (A 213_004..215_003 CLEAN) + "\n'
             '          "B-SIDE forced skip past-hit restart per D-20261002-05 "\n'
             '          "pinned semantics (arithmetic 54_801..55_000 REFUSED at "\n'
             '          "SEED_REGISTRY a158_truegap_ic=55_000 upper-edge "\n'
             '          "endpoint -> hit+1 restart 55_001..55_200, both readings "\n'
             '          "converge, no fork face; W86+ projection A 215_004..217_003 "\n'
             '          "CLEAN / B 55_201..55_400 CLEAN, disclosed for the next "\n'
             '          "freezer; ADMIT receipt results/_r575bmb_w85_band_gate.py "\n'
             '          "dual-state r575 mode A + r576 mode B re-run rc0; not a "\n'
             '          "free pick -- R250), N3-R1 used-seed leg, "\n'
             '          "probe-seed cluster leg, law sec.4 W85 row, "\n'
             '          "r576 bm-b] "\n'
             '          "+ T-141 s2 ')
    t2c = rep(t2c, A5, SEG85, eol2c, 'n1-summary')
    save(FP2, t2c)
    print('edit5 selftest SUMMARY W85 segment landed (insert after W84 segment)')

# ---------------- edit 4: PERPETUAL_FACES.md canon W85 row -------------------
ROW85 = """
- N1 波85（r576 bm-b 冻·prereg 时展行）：**第七十五枚引擎波·bm-b 第二十八枚自有波〔机面 derive：engine_owner 行 74+本候选／engine_owner==bm-b 行 27+本候选〕**·engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W84 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·【本机 bm-b 实例=tick 架构 r535 律——冻结 commit 后下一 tick 新进程重读活树自见新行=免杀重启免做·W55/W56/W59/W61/W65/W67/W70/W72/W74/W76/W79/W82 同窗实证·点火验证唯一证据=产物增长面 r325 律】·【never-dry 供给律常设步·**波号 85=注册表 W84 行后首个自由号**（r511 表尾锁例冻结前 fetch 实核表尾时 W85 号位净空·pf 行+prereg 路径双查·origin 侧 vacancy 机验）·**席位公示=MSG-20261002-1258-bmb（published=reserved r518-① 律·先于冻结 commit 推 origin=r565 早可见性律·席位 commit ce51adf70〔r575 窗〕）**·**席位→冻结跨轮落地**（r575 会话猝死于冻结前夜〔state round_no 停滞+git 已有 r575 自标=r529 猝死诊断律实证〕→r576 首轮收编半成品·锚滚动律刷锚 W82→W83+起草窗实况刷新后落地·r565 同窗律猝死偏离如实披露）·本窗实况=W83 finalize one-pass 已落账（bm-c r366 窗·**547,148 净链头**·K=180,520 合并池）→W84 单席在飞（bm-a r575 冻·烧录 11/12 已交付 origin·finalize 未落账）——本波 finalize 链序前置=W84 单落账（FAIL-CLOSED r307 两态律·本波 §5 锚滚动至 W83 实测值）〕·**带位（r535 机闸 derive 律·活注册表机证·ADMIT 回执=results/_r575bmb_w85_band_gate.py 双态〔r575 mode A 实跑+r576 mode B 复跑 rc0〕）**：**A-ext seed=213_004..215_003**（**A 面算术续带零跳位**==W84 A 尾 213_003+1·步长逐字·CLEAN）；**B-ext exit seed=55_001..55_200**（**B 面越 hit 强制跳位**：算术位 54_801..55_000 于带上边缘撞 SEED_REGISTRY **a158_truegap_ic=55_000** 端点单点→**越 hit 起窗=hit+1 起窗 55_001..55_200**〔**D-20261002-05 集团钉死=越 hit 起窗**·两读法恒同解=单读法零分叉〔F-20261002-03 跳位语义分叉面不触发〕·W74-B 52_000/W81-B 54_000 边缘端点先例族〕）·【机证净空——leg0 八十二行注册表形（82 注册行·表尾=W84 bm-a r575）+leg1-A 算术位 CLEAN+leg1-B2 算术位单点拒绝=被迫跳位非自由挑+leg2 A/B 首净窗机证+leg3 origin 号位净空机验（pf 行+prereg 路径双查）+SEED_REGISTRY 全键 160 值+N3-R1 已用种子带腿（70_000..70_005·MSG-183x r529 强制）+探针种子簇腿（95_000..95_003·r335 强制）+N2/N4+N2-W15 探针点+lfc/options 实际流腿】·**W86+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 215_004..217_003 **CLEAN**；B 55_201..55_400 **CLEAN**（双侧算术预期零拒绝点）·R250：W85 带从未指派·测量面零结果可钓·banned gate ADMIT 0 matched（W85 prereg §0.5）·per-wave prereg=research/PERPETUAL_N1_W85_PREREG.md（冻结件）·本波 §5 锚=W83 finalize 实测值（锚滚动律）·finalize 链序前置=W84 bm-a 单在飞上游席（FAIL-CLOSED r307 两态律）。
"""
FP4 = os.path.join(REPO, 'research/PERPETUAL_FACES.md')
t4, eol4 = load(FP4)
if '- N1 \u6ce285\uff08' in t4:
    print('edit4 already landed (idempotent skip)')
else:
    A4 = '\n- \u6bcf\u6ce2 finalize \u540e\uff1a`science_gates.append_ledger` \u843d\u884c'
    A4X = A4.replace('\n', eol4)
    assert t4.count(A4X) == 1, f'canon anchor not unique: {t4.count(A4X)}'
    t4 = t4.replace(A4X, ROW85.replace('\n', eol4) + A4X)
    save(FP4, t4)
    print('edit4 canon W85 row landed (insert before sec.5 line)')

# ---------------- FIX-B: survival signature re-scan ---------------------------
pf1 = load(FP1)[0]
n11 = load(FP2)[0]
canon1 = load(FP4)[0]
for w in REG_WAVES:
    c = pf1.count(f'    {w}: {{"a":')
    assert c == 1, f'FIX-B FAIL: pf.py row W{w} count={c} (must survive exactly once)'
assert pf1.count('    85: {"a": (213_004') == 1, 'FIX-B FAIL: W85 row not landed exactly once'
for w in REG_WAVES:
    assert n11.count(f'"batch": "PERPETUAL-N1-W{w}"') == 1, f'FIX-B FAIL: n1.py config W{w} count drift'
assert n11.count('"batch": "PERPETUAL-N1-W85"') == 1, 'FIX-B FAIL: W85 config not exactly once'
for w in range(58, 85):
    leg = f'W{w} materializer face'
    assert n11.count(leg) == BASE_SIGS[f'w{w}leg'], f'FIX-B FAIL: {leg} lost'
assert n11.count('W85 materializer face') == 2, \
    'FIX-B FAIL: W85 leg+summary must be exactly 2'
for w in range(48, 85):
    assert canon1.count(f'- N1 \u6ce2{w}\uff08') == 1, f'FIX-B FAIL: canon row W{w} lost'
assert canon1.count('- N1 \u6ce285\uff08') == 1, 'FIX-B FAIL: canon W85 row not exactly once'
print('FIX-B: all registered row signatures survive; exactly one W85 added per face')

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
print('FREEZE_EDITS_OK 85')
