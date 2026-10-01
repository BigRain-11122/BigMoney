# -*- coding: utf-8 -*-
"""r547 bm-a: build scripts/lowamp_p3.py from lowamp_p2.py (surgical
copy-adapt, every replacement asserted to hit exactly once).

P3 deltas (T-140 remaining face, O-20261001-2355 sec.1(e) / LOWAMP-P2
sec.9): the two NON-BRIDGED default-exit keys (loss_time_days +
global_hard_limit) move from the params channel (dead letters, r522 E1
root cause) to the live.paper ExitPatch channel; new seed band
20335500/20336000/20336500; law-A post-burn exit-reason census carried
in finalize (default-stack share > 20% -> consumption auto-block) with
selftest legs.
"""
import io
import sys

SRC = "scripts/lowamp_p2.py"
DST = "scripts/lowamp_p3.py"

src = io.open(SRC, encoding="utf-8").read()


def rep(old, new, n=1):
    global src
    c = src.count(old)
    assert c == n, f"pattern count {c} != {n}: {old[:80]!r}"
    src = src.replace(old, new)


# ---- 1. docstring head -------------------------------------------------
rep(
    '"""LOWAMP-P2 -- low-amplitude cross-sectional daily-rebalance family judged\n'
    'batch RE-ENTRY (T-2026-10-01-140 action-4 runner). The as-designed family\n'
    'face re-enters supply via the exit-axis explicit gate FIRST application.\n'
    '\n'
    'Prereg (FROZEN): research/LOWAMP-P2.md -- frozen at c3c825c2a9 (bm-a r514\n'
    'adoption commit; banned_direction_gate ADMIT rc0 re-verified same round).\n'
    'Judgments live there; this file implements them, never re-states a\n'
    'threshold. LOWAMP-P1 verdict VOID-with-face-note (O-20261001-1108 sec.3);\n'
    'this batch is a NEW batch, not a re-run (T-136 audit "Either way" line).\n',
    '"""LOWAMP-P3 -- low-amplitude cross-sectional daily-rebalance family judged\n'
    'batch (T-2026-10-01-140 remaining face; O-20261001-2355 sec.1(e) re-open\n'
    'channel). The family re-enters supply with the r522 root cause FIXED: the\n'
    'two NON-BRIDGED default-exit keys ride the live.paper ExitPatch channel.\n'
    '\n'
    'Prereg (FROZEN): research/LOWAMP-P3.md (freeze = the commit carrying this\n'
    'file; banned_direction_gate ADMIT re-verified pre-burn). Judgments live\n'
    'there; this file implements them, never re-states a threshold.\n'
    'LOWAMP-P1 + LOWAMP-P2 verdicts VOID-with-face-note (O-20261001-1108\n'
    'sec.3 / O-20261001-2355 sec.1); this batch is a NEW batch, not a re-run\n'
    '(T-136 audit "Either way" line; frozen-batch zero-re-run iron law).\n')

# ---- 2. execution-semantics docstring block ---------------------------
rep(
    '  EXPLICITLY DISABLED key-by-key in run_cell_portfolio params (prereg\n'
    '  sec.0.6 verbatim: take_profit_levels=(), trailing_stop_activate=1e12,\n'
    '  initial_stop=-1.0, time_decay_period=1e9, loss_time_days=1e9,\n'
    '  global_hard_limit=1e9) -- the same params channel the T-136 audit\n'
    '  as-burned leg proved, used in reverse (r301 hybrid finding closed).\n'
    '  x2 face = CostPatch(2.0) multiplier (r82 fix face).\n',
    '  DISABLED via TWO channels, split by the engine\'s own bridge surface\n'
    '  (r522 E1 root cause: backtester.py ExitConfig reads only SIX params\n'
    '  kwargs -- loss_time_days + global_hard_limit are NON-BRIDGED, dead\n'
    '  letters in the params channel):\n'
    '    params channel (bridge-reachable, 4 neutralized keys):\n'
    '      take_profit_levels=(), trailing_stop_activate=1e12,\n'
    '      initial_stop=-1.0, time_decay_period=1e9;\n'
    '    ExitPatch channel (live.paper ExitConfig factory patch, 2 keys):\n'
    '      loss_time_days=1e9, global_hard_limit=1e9 -- the same channel the\n'
    '      T-136 fixture Leg B and the r522 E1 corrected-face leg proved.\n'
    '  x2 face = CostPatch(2.0) multiplier (r82 fix face).\n'
    '\n'
    'Law-A post-burn exit-reason census (LOWAMP-P2 sec.9 / O-20261001-2355\n'
    'sec.1, carried by THIS batch): finalize re-runs the headline cell\n'
    'through the same frozen machinery capturing per-trade exit reasons; on\n'
    'the declared hold-through face the ONLY lawful reason is\n'
    'signal_reversal (selection rotation). Default-stack share > 20% =\n'
    'verdict consumption AUTO-BLOCKED (verdict = consumption-blocked).\n')

# ---- 3. G-CENSUS docstring lineage ------------------------------------
rep(
    'G-CENSUS zero-burn amendment (2026-10-01, pre-burn, zero cells burned,\n'
    'r251/r280 lineage, result-blind): the frozen text pinned legacy starts to\n'
    'the t22 finalize reading 1,255 -- measured on t22\'s 2026-09-23-END panel.\n'
    'Under THIS batch\'s binding evidence_cutoff 2026-09-22 truncation the\n'
    'deterministic enumeration yields 1,254 on BOTH the raw and adjusted\n'
    'faces (anchor rows 1,631; 1631-252-126+1). The binding cutoff discipline\n'
    'wins; the gate is re-anchored to the measured reading {legacy: 1254,\n'
    'deep: 1506}. Deep reading matches the frozen 1,506 bit-for-bit.\n',
    'G-CENSUS anchor (inherited from the P2 zero-burn amendment, r251/r280\n'
    'lineage): {legacy: 1254, deep: 1506} measured under the binding\n'
    '2026-09-22 cutoff truncation (raw + adjusted faces both read 1,254;\n'
    'anchor rows 1,631). Identical truncation here -- same deterministic\n'
    'enumeration, same anchor readings, bit-for-bit.\n')

# ---- 4. seed-registry docstring disclosure ----------------------------
rep(
    'Seed registry disclosure (P2 band, prereg sec.3 verbatim): nulls bound to\n'
    'rng([20334500, k]); sensitivity param draws bound to rng([20333500, k]);\n'
    'the lowamp_p2_starts=20334000 registry row is NOT consumed by this batch\n'
    '(judged starts = T-22 deterministic full enumeration; sensitivity legs =\n'
    'full-panel continuous runs) -- disclosed here and in the results audit\n'
    'block.\n',
    'Seed registry disclosure (P3 band, prereg sec.3 verbatim; new band per\n'
    'LOWAMP-P2 sec.9 no-recycle law): nulls bound to rng([20336500, k]);\n'
    'sensitivity param draws bound to rng([20335500, k]); the\n'
    'lowamp_p3_starts=20336000 registry row is NOT consumed by this batch\n'
    '(judged starts = T-22 deterministic full enumeration; sensitivity legs =\n'
    'full-panel continuous runs) -- disclosed here and in the results audit\n'
    'block.\n')

# ---- 5. usage examples --------------------------------------------------
for ln in ("probe                  # ignition gate face",
           "run --cell LA-REP --axis legacy --face base",
           "run --nulls",
           "run --sensitivity",
           "status",
           "finalize                # round-owned, post-shards",
           "selftest                # hermetic, offline"):
    rep(f"python scripts/lowamp_p2.py {ln}\n",
        f"python scripts/lowamp_p3.py {ln}\n")

# ---- 6. imports ---------------------------------------------------------
rep("from live.paper import build_panels, load_core\n",
    "from live.paper import build_panels, load_core, ExitPatch\n")

# ---- 7. constants --------------------------------------------------------
rep('PREREG = os.path.join(ROOT, "research", "LOWAMP-P2.md")\n'
    'OUT_DIR = os.path.join(ROOT, "results", "lowamp_p2")\n',
    'PREREG = os.path.join(ROOT, "research", "LOWAMP-P3.md")\n'
    'OUT_DIR = os.path.join(ROOT, "results", "lowamp_p3")\n')
rep('OUT_JSON = os.path.join(OUT_DIR, "lowamp_p2_results.json")\n',
    'OUT_JSON = os.path.join(OUT_DIR, "lowamp_p3_results.json")\n')
rep('BATCH_NAME = "LOWAMP-P2"\n', 'BATCH_NAME = "LOWAMP-P3"\n')
rep("SEED_NULLS = 20334500                       # prereg sec.3 verbatim\n",
    "SEED_NULLS = 20336500                       # prereg sec.3 verbatim\n")
rep("SEED_SENS = 20333500                        # prereg sec.3 verbatim\n",
    "SEED_SENS = 20335500                        # prereg sec.3 verbatim\n")

# new module constants after FACES
rep('FACES = ("base", "x2")\n',
    'FACES = ("base", "x2")\n'
    '# sec.0.6 P3 fix face: the two NON-BRIDGED default-exit keys ride the\n'
    '# live.paper ExitPatch channel (params channel = dead letters, r522 E1)\n'
    'EXIT_PATCH_OVERRIDES = {"loss_time_days": 10 ** 9,\n'
    '                        "global_hard_limit": 10 ** 9}\n'
    '# law-A census: the ONLY lawful exit reason on the hold-through face\n'
    'LAWFUL_EXIT_REASONS = ("signal_reversal",)\n'
    'CENSUS_BLOCK_SHARE = 0.20\n'
    '# sec.0.6 params-channel face: bridge-reachable keys ONLY (the engine\n'
    '# ExitConfig bridge reads exactly these 6 kwargs; single source for\n'
    '# run_cell_portfolio AND the law-A census re-run)\n'
    'NEUTRALIZED_PARAMS = {\n'
    '    "position_size_pct": 1.0, "max_positions": 1,\n'
    '    "sizing_mode": "fixed_initial", "report_num_entries": True,\n'
    '    "take_profit_levels": (),\n'
    '    "trailing_stop_activate": 1e12,\n'
    '    "initial_stop": -1.0,\n'
    '    "time_decay_period": 10 ** 9,\n'
    '}\n')

# ---- 8. FROZEN_ENVELOPE -------------------------------------------------
rep('FROZEN_ENVELOPE = ("2026-10-01 pre-burn amendment note: legacy G-CENSUS "\n'
    '                   "re-anchored 1255->1254 under the binding 2026-09-22 "\n'
    '                   "cutoff truncation (r251/r280 zero-burn lineage)")\n',
    'FROZEN_ENVELOPE = ("2026-10-02 P3 lineage note: G-CENSUS anchor "\n'
    '                   "{legacy: 1254, deep: 1506} inherited verbatim from "\n'
    '                   "the LOWAMP-P2 zero-burn amendment (r251/r280 "\n'
    '                   "lineage) -- same binding 2026-09-22 cutoff "\n'
    '                   "truncation, same deterministic enumeration")\n')

# ---- 9. run_cell_portfolio params + engine call ------------------------
rep(
    '    from engine import run_backtest\n'
    '    params = {"position_size_pct": 1.0, "max_positions": 1,\n'
    '              "sizing_mode": "fixed_initial", "report_num_entries": True,\n'
    '              # sec.0.6 exit-axis: HOLD-THROUGH -- engine default exit\n'
    '              # stack explicitly disabled key-by-key (prereg verbatim;\n'
    '              # r301 default-stack x low-amp hybrid finding reversed via\n'
    '              # the engine\'s own params channel -- engine/ untouched)\n'
    '              "take_profit_levels": (),\n'
    '              "trailing_stop_activate": 1e12,\n'
    '              "initial_stop": -1.0,\n'
    '              "time_decay_period": 10 ** 9,\n'
    '              "loss_time_days": 10 ** 9,\n'
    '              "global_hard_limit": 10 ** 9}\n',
    '    from engine import run_backtest\n'
    '    # sec.0.6 exit-axis: HOLD-THROUGH -- the params channel carries the\n'
    '    # BRIDGE-REACHABLE neutralized keys only (NEUTRALIZED_PARAMS single\n'
    '    # source); the two non-bridged keys ride ExitPatch (r522 E1 fix)\n'
    '    params = dict(NEUTRALIZED_PARAMS)\n')
rep(
    '        with (CostPatch(2.0) if face == "x2" else nullcontext()):\n'
    '            res = run_backtest(win, params, entry_signal=ent,\n'
    '                               exit_signal=ent <= 0, entry_size_scale=sc)\n',
    '        with ExitPatch(EXIT_PATCH_OVERRIDES), \\\n'
    '             (CostPatch(2.0) if face == "x2" else nullcontext()):\n'
    '            res = run_backtest(win, params, entry_signal=ent,\n'
    '                               exit_signal=ent <= 0, entry_size_scale=sc)\n')

# ---- 10. probe seed note -----------------------------------------------
rep(
    '        "note": "registry row lowamp_p2_starts=20334000 NOT consumed by "\n'
    '                "this batch (T-22 full enumeration judged starts; "\n'
    '                "full-panel continuous sensitivity); prereg sec.3 binds "\n'
    '                "nulls to 20334500 and sens draws to 20333500 "\n'
    '                "(verbatim)."}\n',
    '        "note": "registry row lowamp_p3_starts=20336000 NOT consumed by "\n'
    '                "this batch (T-22 full enumeration judged starts; "\n'
    '                "full-panel continuous sensitivity); prereg sec.3 binds "\n'
    '                "nulls to 20336500 and sens draws to 20335500 "\n'
    '                "(verbatim; P3 new band per LOWAMP-P2 sec.9)."}\n')

# ---- 11. _entry_of ids ---------------------------------------------------
rep('    return ("LOWAMP-P2-NULLS", "lowamp-p2-nulls-0of1")\n',
    '    return ("LOWAMP-P3-NULLS", "lowamp-p3-nulls-0of1")\n')
rep('    return ("LOWAMP-P2-SENS", "lowamp-p2-sens-0of1")\n',
    '    return ("LOWAMP-P3-SENS", "lowamp-p3-sens-0of1")\n')
rep('    entry = ("LOWAMP-P2-CELL-" + args.cell.replace("-", "").upper()\n',
    '    entry = ("LOWAMP-P3-CELL-" + args.cell.replace("-", "").upper()\n')

# ---- 12. cmd_status path msg --------------------------------------------
rep('    print("no results/lowamp_p2 yet")\n',
    '    print("no results/lowamp_p3 yet")\n')

# ---- 13. finalize: probe_ref + ledger file_name --------------------------
rep('        "probe_ref": "results/lowamp_p2/probe.json",\n',
    '        "probe_ref": "results/lowamp_p3/probe.json",\n')
rep('                        file_name="results/lowamp_p2/lowamp_p2_results.json",\n',
    '                        file_name="results/lowamp_p3/lowamp_p3_results.json",\n')

# ---- 14. main description ------------------------------------------------
rep('ap = argparse.ArgumentParser(description="LOWAMP-P2 judged batch runner (exit-axis hold-through)")',
    'ap = argparse.ArgumentParser(description="LOWAMP-P3 judged batch runner (exit-axis hold-through, ExitPatch channel)")')

# ---- 15. census helpers (insert before finalize banner) -------------------
rep('# ------------------------------------------------------------------ finalize\n',
    '# ----------------------------------------------------- law-A exit census\n'
    '\n'
    'def _census_core(prices, close, entry, weights, active, face):\n'
    '    """Law-A census engine loop: per-symbol sub-account runs through\n'
    '    the SAME frozen machinery (NEUTRALIZED_PARAMS + ExitPatch +\n'
    '    run_backtest), capturing per-trade exit reasons. Single source\n'
    '    shared by cmd_finalize (headline re-run) and selftest (fixture\n'
    '    leg) -- no hand-copied params face (r303 single-source law)."""\n'
    '    from engine import run_backtest\n'
    '    from contextlib import nullcontext\n'
    '    per_reason, per_sym = {}, {}\n'
    '    n_trades = 0\n'
    '    for sym in active:\n'
    '        win = {sym: prices[sym]}\n'
    '        ent = entry[[sym]]\n'
    '        sc = exec_day_scale(weights, sym)\n'
    '        with ExitPatch(EXIT_PATCH_OVERRIDES), \\\n'
    '             (CostPatch(2.0) if face == "x2" else nullcontext()):\n'
    '            res = run_backtest(win, dict(NEUTRALIZED_PARAMS),\n'
    '                               entry_signal=ent,\n'
    '                               exit_signal=ent <= 0,\n'
    '                               entry_size_scale=sc)\n'
    '        reasons = {}\n'
    '        for tr in res["trades"]:\n'
    '            r = tr["reason"]\n'
    '            per_reason[r] = per_reason.get(r, 0) + 1\n'
    '            reasons[r] = reasons.get(r, 0) + 1\n'
    '            n_trades += 1\n'
    '        per_sym[sym] = {"n_trades": len(res["trades"]),\n'
    '                        "reasons": reasons}\n'
    '    default_n = sum(v for k, v in per_reason.items()\n'
    '                    if k not in LAWFUL_EXIT_REASONS)\n'
    '    share = (default_n / n_trades) if n_trades else 0.0\n'
    '    return {"total_exits": n_trades, "per_reason": per_reason,\n'
    '            "default_stack_exits": default_n,\n'
    '            "default_share": round(share, 6),\n'
    '            "block_share": CENSUS_BLOCK_SHARE,\n'
    '            "pass": bool(share <= CENSUS_BLOCK_SHARE),\n'
    '            "per_sym": per_sym}\n'
    '\n'
    '\n'
    'def _exit_reason_census(axis, cell, face):\n'
    '    """Law-A post-burn exit-reason census (LOWAMP-P2 sec.9, carried per\n'
    '    O-20261001-2355 sec.1): re-run one (cell, face) cell on `axis`\n'
    '    through the same frozen machinery, capturing per-trade exit\n'
    '    reasons. On the declared hold-through face the ONLY lawful exit is\n'
    '    signal_reversal (selection rotation); every other reason is an\n'
    '    engine default-stack exit. default_share > CENSUS_BLOCK_SHARE\n'
    '    (20%) -> verdict consumption AUTO-BLOCKED."""\n'
    '    prices = load_axis(axis)\n'
    '    P = build_panels(prices)\n'
    '    close = P["close"]\n'
    '    spec = CELLS[cell]\n'
    '    entry, weights, _ = build_signal(close, P["volume"], P["amount"],\n'
    '                                     spec["W"], spec["N"])\n'
    '    active = [c for c in entry.columns if entry[c].any()]\n'
    '    core = _census_core(prices, close, entry, weights, active, face)\n'
    '    core.update({"cell": cell, "axis": axis, "face": face})\n'
    '    return core\n'
    '\n'
    '\n'
    '# ------------------------------------------------------------------ finalize\n')

# ---- 16. finalize: census computation + verdict branch + gates/print ------
rep(
    '        seg_cov[axis] = cnt\n'
    '        for reg in ("bear", "bull", "chop"):\n'
    '            if cnt.get(reg, 0) < 50:\n'
    '                gseg_pass = False\n',
    '        seg_cov[axis] = cnt\n'
    '        for reg in ("bear", "bull", "chop"):\n'
    '            if cnt.get(reg, 0) < 50:\n'
    '                gseg_pass = False\n'
    '    # law-A post-burn exit-reason census (LOWAMP-P2 sec.9 /\n'
    '    # O-20261001-2355 sec.1, carried by this batch): headline LA-REP\n'
    '    # legacy base re-run through the same frozen machinery; only\n'
    '    # signal_reversal is lawful on the hold-through face.\n'
    '    census = _exit_reason_census("legacy", "LA-REP", "base")\n'
    '    census_pass = bool(census["pass"])\n')
rep(
    '    if not gseg_pass:\n'
    '        verdict = "insufficient-sample"\n'
    '    elif gates_pass:\n'
    '        verdict = "PASS"\n'
    '    else:\n'
    '        verdict = "judged-negative"\n',
    '    if not gseg_pass:\n'
    '        verdict = "insufficient-sample"\n'
    '    elif not census_pass:\n'
    '        verdict = "consumption-blocked"   # law-A auto-block (>20% default)\n'
    '    elif gates_pass:\n'
    '        verdict = "PASS"\n'
    '    else:\n'
    '        verdict = "judged-negative"\n')
rep(
    '            "g_seg": {"coverage": seg_cov, "pass": gseg_pass},\n'
    '        },\n',
    '            "g_seg": {"coverage": seg_cov, "pass": gseg_pass},\n'
    '            "exit_census": census,\n'
    '        },\n')
rep(
    '            "deep_axis_amount": "volume x close proxy (t22 precedent, disclosed)",\n',
    '            "deep_axis_amount": "volume x close proxy (t22 precedent, disclosed)",\n'
    '            "law_a_census": {"block_share": CENSUS_BLOCK_SHARE,\n'
    '                            "lawful_reasons": list(LAWFUL_EXIT_REASONS),\n'
    '                            "ref": "LOWAMP-P2 sec.9 / O-20261001-2355 sec.1"},\n')
rep(
    '    print(f"  g1={g1.get(\'pass\')} x2={x2_pass} m1={m1.get(\'pass\')} "\n'
    '          f"g2={g2.get(\'pass\')} dual_axis={dual_axis_pass} "\n'
    '          f"g_seg={gseg_pass}")\n',
    '    print(f"  g1={g1.get(\'pass\')} x2={x2_pass} m1={m1.get(\'pass\')} "\n'
    '          f"g2={g2.get(\'pass\')} dual_axis={dual_axis_pass} "\n'
    '          f"g_seg={gseg_pass} census={census_pass} "\n'
    '          f"(default_share={census[\'default_share\']})")\n')

# ---- 17. selftest new legs ------------------------------------------------
rep(
    '    # F10 cost single-source derivation\n'
    '    rate = cost_spec.x1_side_rate()\n'
    '    check("F10_cost_rt_26_082bp", abs(rate * 2.0 * 1e4 - 26.082) < 1e-6,\n'
    '          f"{rate*2e4:.3f}bp")\n',
    '    # F10 cost single-source derivation\n'
    '    rate = cost_spec.x1_side_rate()\n'
    '    check("F10_cost_rt_26_082bp", abs(rate * 2.0 * 1e4 - 26.082) < 1e-6,\n'
    '          f"{rate*2e4:.3f}bp")\n'
    '    # F11 P3 exit-channel split: ExitPatch overrides disjoint from the\n'
    '    # bridge-reachable params face (dead-letter regression guard, r522)\n'
    '    check("F11_exit_channels_disjoint",\n'
    '          not (set(EXIT_PATCH_OVERRIDES) & set(NEUTRALIZED_PARAMS)),\n'
    '          f"patch={sorted(EXIT_PATCH_OVERRIDES)}")\n'
    '    import engine.exit_rules as _er\n'
    '    with ExitPatch(EXIT_PATCH_OVERRIDES):\n'
    '        cfg = _er.ExitConfig(max_positions=1)\n'
    '        ok_bite = (cfg.loss_time_days == 10 ** 9\n'
    '                   and cfg.global_hard_limit == 10 ** 9)\n'
    '    cfg_out = _er.ExitConfig()\n'
    '    check("F12_exitpatch_bites_and_restores",\n'
    '          ok_bite and cfg_out.loss_time_days != 10 ** 9,\n'
    '          f"bite={ok_bite} restored={cfg_out.loss_time_days}")\n'
    '    # F13 census share math + block threshold (pure-function face)\n'
    '    fake = {"signal_reversal": 14, "loss_time_stop": 3,\n'
    '            "global_hard_limit": 1}\n'
    '    tot = sum(fake.values())\n'
    '    share = sum(v for k, v in fake.items()\n'
    '                if k not in LAWFUL_EXIT_REASONS) / tot\n'
    '    check("F13_census_share_math",\n'
    '          abs(share - 4 / 18) < 1e-12 and share <= CENSUS_BLOCK_SHARE,\n'
    '          f"share={share:.4f} vs block={CENSUS_BLOCK_SHARE}")\n'
    '    fake_bad = {"signal_reversal": 7, "loss_time_stop": 8,\n'
    '                "global_hard_limit": 6}\n'
    '    tot_b = sum(fake_bad.values())\n'
    '    share_b = sum(v for k, v in fake_bad.items()\n'
    '                  if k not in LAWFUL_EXIT_REASONS) / tot_b\n'
    '    check("F13b_census_block_face", share_b > CENSUS_BLOCK_SHARE,\n'
    '          f"share={share_b:.4f}")\n'
    '    # F14 hold-through census on the synthetic fixture: the P3 face\n'
    '    # produces ZERO default-stack exits through the real engine\n'
    '    cen = _census_core(prices, P["close"], entry, weights, active,\n'
    '                       "base")\n'
    '    check("F14_fixture_census_zero_default",\n'
    '          cen["total_exits"] > 0 and cen["default_stack_exits"] == 0,\n'
    '          f"total={cen[\'total_exits\']} reasons={cen[\'per_reason\']}")\n')

io.open(DST, "w", encoding="utf-8", newline="\n").write(src)
print(f"built {DST}: {len(src.splitlines())} lines")
