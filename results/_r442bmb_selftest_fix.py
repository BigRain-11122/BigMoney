"""r442 bm-b: convert the 4 stale selftest legs + header to the frozen
W11 face (fourteen-tuple 31,352,832; seeds 20317000/20317500/20318000;
STD-face per-cell law r237; W10->W11 thirteen/fourteen-tuple).  All
edits exact-literal, assert single occurrence each."""
import io

p = 'scripts/trial_labor_w11.py'
src = io.open(p, encoding='utf-8').read()
edits = [
    # E1 header wave id
    ('"""TRIAL_LABOR_W11 runner -- T-122 mass-candidate trial wave-10\n'
     '(5000-ceiling, momentum-confirmation MOM-gate FOURTEEN-gate wave).',
     '"""TRIAL_LABOR_W11 runner -- T-123 mass-candidate trial wave-11\n'
     '(5000-ceiling, MOM+STD confirmation FOURTEEN-gate wave).'),
    # E2+E3 freeze paragraph -> r441 / W10 trigger / STD candidate / re-take seeds
    ("Prereg FROZEN (bm-b r437 adopting-machine same-round freeze per the\n"
     "candidate's own 10-item adopter checklist; freeze trigger MET live =\n"
     "W9 full chain landed 2026-09-29 17:47:46 {w9_judge.json 243/243\n"
     "judged zero G1 zero G2 + w9_intake lawful-zero + CEO-REPORT-WAVE9 +\n"
     "attrition two rows + TRIAL_GRAMMAR_LEDGER wave-9 row + W9 prereg sec.7/\n"
     "sec.8 backfilled} + ledger head 344,031 linear live-read {head file=\n"
     "w9_judge.json} + zero in-flight judge faces [pool entries 120/120\n"
     "done]):\n"
     "research/TRIAL_LABOR_W11_PREREG.md -- generate grammar + funnel rules +\n"
     "judgment lines all frozen; post-run only sec.7/8 backfill.  Seeds held\n"
     "at the freeze commit per R250 one-step law: trial_labor_w11_gen=\n"
     "20311000 / trial_labor_w11_scrnull=20311500 / trial_labor_w11_unc=\n"
     "20312000 (berth-open adoption of the bm-c r228 MOM candidate whole\n"
     "package per AMP->W9 precedent; freeze-time three-step re-verify ALL\n"
     "GREEN, no re-pick).",
     "Prereg FROZEN (bm-b r441 adopting-machine same-round freeze per the\n"
     "candidate's own 10-item adopter checklist; freeze trigger MET live =\n"
     "W10 full chain landed 2026-09-29 20:31:29 {w10_judge.json 283/283\n"
     "judged zero G1 zero G2 + w10_intake lawful-zero + CEO-REPORT-WAVE10 +\n"
     "attrition two rows + TRIAL_GRAMMAR_LEDGER wave-10 row + W10 prereg\n"
     "sec.7/sec.8 backfilled} + ledger head 346,553 linear live-read {head\n"
     "file=w10_judge.json} + zero in-flight judge faces [pool entries\n"
     "123/123 done]:\n"
     "research/TRIAL_LABOR_W11_PREREG.md -- generate grammar + funnel rules +\n"
     "judgment lines all frozen; post-run only sec.7/8 backfill.  Seeds held\n"
     "at the freeze commit per R250 one-step law: trial_labor_w11_gen=\n"
     "20317000 / trial_labor_w11_scrnull=20317500 / trial_labor_w11_unc=\n"
     "20318000 (berth-open adoption of the bm-c r237 STD candidate whole\n"
     "package per AMP->W9->W10 lineage; draft berths 20316000/20316500\n"
     "collided with bm-a r445 A12 keys -> +500 re-take per the draft\n"
     "clause-5 collision clause, three-step law all-green, no re-pick\n"
     "after freeze)."),
    # E4 import-face law includes tl10
    ("tstate overlay & eleven-tuple machinery + tl9 amp overlay & twelve-\n"
     "tuple machinery); Sobol sample_draws pattern follows mass_trial_w1",
     "tstate overlay & eleven-tuple machinery + tl9 amp overlay & twelve-\n"
     "tuple machinery + tl10 mom overlay & thirteen-tuple machinery);\n"
     "Sobol sample_draws pattern follows mass_trial_w1"),
    # E5 L6a combos -> W11 frozen face
    ('    _ok("L6a axis_combos == 10,450,944 (5,225,472 x 2)",\n'
     '        g["axis_combos"] == 10450944 == tl9.AXIS_COMBOS * 2)',
     '    _ok("L6a axis_combos == 31,352,832 (10,450,944 x 3 std-axis "\n'
     '        "values; W10 mom-face combos x len(AXIS_STD))",\n'
     '        g["axis_combos"] == 31352832\n'
     '        == tl10.AXIS_COMBOS * len(AXIS_STD))'),
    # E6 L6c label -> r441 re-take seeds
    ('    _ok("L6c W10 seeds == SEED_REGISTRY berths (20311000/20311500/"\n'
     '        "20312000 held, no re-pick)",',
     '    _ok("L6c W11 seeds == SEED_REGISTRY berths (20317000/20317500/"\n'
     '        "20318000 berth re-take held, no re-pick)",'),
    # E7 L7g -> STD-face per-cell vs r237 probe facts
    ('        if os.path.exists(PROBE_FACTS_FILE):\n'
     '            pf = json.load(open(PROBE_FACTS_FILE, encoding="utf-8"))\n'
     '            _ok("L7g probe-facts exact per-cell 256-grid cross-check "\n'
     '                "(r228 determinism law: every computed cell == the "\n'
     '                "git-tracked frozen probe face)",\n'
     '                rmeta["eight_gate_256cells"]\n'
     '                == pf.get("eight_gate_cells"))',
     '        if os.path.exists(PROBE_FACTS_FILE):\n'
     '            pf = json.load(open(PROBE_FACTS_FILE, encoding="utf-8"))\n'
     '            sstate, serr = _std_state_full()\n'
     '            _ok("L7g probe-facts exact per-cell 256-grid cross-check "\n'
     '                "(r237 determinism law: every computed STD-face cell "\n'
     '                "== the git-tracked frozen probe face)",\n'
     '                serr is None\n'
     '                and sstate[2]["eight_gate_256cells"]\n'
     '                == pf.get("eight_gate_cells"),\n'
     '                serr or "std-face cells == probe facts")'),
    # E8 L8a -> fourteen-tuple
    ('    _ok("L8a Sobol draw determinism (same seed -> byte-identical "\n'
     '        "candidate incl. the mom axis)",\n'
     '        json.dumps(c1[1], sort_keys=True) == json.dumps(c2[1],\n'
     '                                                        sort_keys=True)\n'
     '        and len(c1[1]["axis"]) == 13)',
     '    _ok("L8a Sobol draw determinism (same seed -> byte-identical "\n'
     '        "candidate incl. the mom+std axes, fourteen-tuple)",\n'
     '        json.dumps(c1[1], sort_keys=True) == json.dumps(c2[1],\n'
     '                                                        sort_keys=True)\n'
     '        and len(c1[1]["axis"]) == 14)'),
    # E9 L8b NameError thirteen -> fourteen
    ('    _ok("L8b MOM appends AFTER AMP in the rng stream (first twelve "\n'
     '        "axis arrays == W9-order stream verbatim, zero disturbance)",\n'
     '        all(np.array_equal(a, b) for a, b in zip(thirteen, twelve)))',
     '    _ok("L8b MOM+STD append AFTER AMP in the rng stream (first twelve "\n'
     '        "axis arrays == W9-order stream verbatim, zero disturbance)",\n'
     '        all(np.array_equal(a, b) for a, b in zip(fourteen, twelve)))'),
]
for i, (old, new) in enumerate(edits, 1):
    n = src.count(old)
    assert n == 1, f"E{i}: found {n} occurrences (expected 1)"
    src = src.replace(old, new)
io.open(p, 'w', encoding='utf-8', newline='\n').write(src)
print(f"all {len(edits)} edits applied cleanly")
