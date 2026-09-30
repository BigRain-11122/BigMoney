"""_r472bmb_w14_edits5.py -- selftest + funnel-contract W14 rewire
(Slice-B completion of the dead r472 session's Slice-A draft):
L6/L8/L9/L10 stale W13 assertions -> W14 faces; L12-L15 region splice
(16-tuple calls/unpacks -> 18-tuple + resi/cnt states + 19-tuple
returns); new L16 G-RESI/G-CNT anchor legs; CSV contract resi/cnt
columns (extrasaction='ignore' was silently dropping them); honest
docstrings/prints.  Count-verified."""
import sys

DRAFT = "results/_r472bmb_w14_runner_draft.py"
text = open(DRAFT, encoding="utf-8").read()
log = []


def rep(old, new, expect=1, name=""):
    global text
    n = text.count(old)
    if n != expect:
        print(f"EDIT5-FAIL [{name}]: found {n} != {expect}")
        sys.exit(1)
    text = text.replace(old, new)
    log.append((name, n))


# 1. screen CSV contract: rename to own-wave + carry resi/cnt columns
rep('''csv_cols_screen_w13 = ["cell_id", "candidate_id", "family", "module", "fn",
                      "no_entries", "beat6m_k", "beat6m_n", "beat6m_rate",
                      "binom_z", "binom_p", "sharpe_full", "dd_full",
                      "n_trades", "n_entries", "stop_face", "stop_fired",
                      "gate_face", "gate_zeroed", "vol_face", "vol_zeroed",
                      "yang_face", "yang_zeroed", "vconf_face",
                      "vconf_zeroed", "streak_face", "streak_zeroed",
                      "tstate_face", "tstate_zeroed", "amp_face",
                      "amp_zeroed", "mom_face", "mom_zeroed",
                      "std_face", "std_zeroed",
                      "rsqr_face", "rsqr_zeroed",
                      "sumn_face", "sumn_zeroed",
                      "survives_screen"]''',
    '''csv_cols_screen_w14 = ["cell_id", "candidate_id", "family", "module", "fn",
                      "no_entries", "beat6m_k", "beat6m_n", "beat6m_rate",
                      "binom_z", "binom_p", "sharpe_full", "dd_full",
                      "n_trades", "n_entries", "stop_face", "stop_fired",
                      "gate_face", "gate_zeroed", "vol_face", "vol_zeroed",
                      "yang_face", "yang_zeroed", "vconf_face",
                      "vconf_zeroed", "streak_face", "streak_zeroed",
                      "tstate_face", "tstate_zeroed", "amp_face",
                      "amp_zeroed", "mom_face", "mom_zeroed",
                      "std_face", "std_zeroed",
                      "rsqr_face", "rsqr_zeroed",
                      "sumn_face", "sumn_zeroed",
                      "resi_face", "resi_zeroed",
                      "cnt_face", "cnt_zeroed",
                      "survives_screen"]''',
    1, "csv cols rename+extend")

rep('''        w = csv.DictWriter(fh, fieldnames=csv_cols_screen_w13,
                           extrasaction="ignore")''',
    '''        w = csv.DictWriter(fh, fieldnames=csv_cols_screen_w14,
                           extrasaction="ignore")''',
    1, "csv DictWriter fieldnames")

# 2. run_candidate_curve_w14 docstring: honest 19-tuple returns face
rep('''    amp_zeroed, mom_zeroed, std_zeroed, rsqr_zeroed, sumn_zeroed)."""''',
    '''    amp_zeroed, mom_zeroed, std_zeroed, rsqr_zeroed, sumn_zeroed,
    resi_zeroed, cnt_zeroed)."""''',
    1, "curve docstring returns")

# 3. cmd_grammar docstring: W10 -> W14
rep('''    """Serialize the frozen W10 grammar to results/trial_labor_w14/
    w14_grammar.json (idempotent; sha16 printed for the slice-1 pin)."""''',
    '''    """Serialize the frozen W14 grammar to results/trial_labor_w14/
    w14_grammar.json (idempotent; sha16 printed for the Slice-B pin)."""''',
    1, "cmd_grammar docstring")

# 4. cmd_status print: stale W10/r438 banner -> W14/r472 honest face
rep('''    print("slice-1 mom overlay + G-MOM gate + eighteen-tuple grammar + "
          "funnel bodies + dispatch LANDED (bm-b r438); GENERATE pool "
          "entry submitted same-commit -- autofill burns, no inline "
          "burn (O-2100); SCREEN/JUDGE pool entries land on their "
          "physical deps per W3-W9 precedent")''',
    '''    print("W14 resi+cnt overlay + G-RESI/G-CNT gates + eighteen-tuple "
          "grammar + funnel bodies + dispatch LANDED (bm-b r472); "
          "GENERATE pool entry submitted same-commit -- autofill "
          "burns, no inline burn (O-2100); SCREEN/JUDGE pool entries "
          "land on their physical deps per W3-W13 precedent")''',
    1, "cmd_status banner")

# 5. selftest docstring: honest W14 scope
rep('''    """Hermetic offline selftest (zero network, zero live engine burns,
    zero cell evaluation): MOM causality / 139-bar warmup / NaN
    comparison-artifact leg (pit-95 batch-95 + r431 erratum face) /
    mom=none identity / eight-gate intersection / G-MOM probe anchors
    (incl. eight-gate 256-cell 111/145 + extreme days 2/7 + core48
    spread) / G-SUMN probe anchors (nine-gate 512-cell 103/409 +
    slope split 387/0 + core48 spread) / grammar structure / draw
    determinism / 25-source exclusion loader / engine double-run
    determinism legs / funnel faces (dispatch / null-cell engine path /
    CSV contract) + pit-95 finalize guards."""''',
    '''    """Hermetic offline selftest (zero network, zero live engine burns,
    zero cell evaluation): W10-W13 regression legs (MOM causality /
    139-bar warmup / NaN comparison-artifact / mom=none identity /
    eight-gate intersection / G-MOM probe anchors / G-SUMN probe
    anchors) + W14 own faces (eighteen-tuple grammar 1,693,052,928
    combos / resi+cnt stream append / 28-source exclusion loader
    resi/cnt-none completion / resi+cnt new-syntax legality / G-RESI
    + G-CNT real-face fail-closed anchor loads / mask + engine parity
    vs W9 + W13 baselines / engine double-run determinism / funnel
    faces (dispatch / null-cell engine path / CSV contract) + pit-95
    finalize guards."""''',
    1, "selftest docstring")

# 6. L6 family
rep('''    # ---- L6 grammar structure (fourteen axes / combos / seeds / sha)
    g = build_grammar_w14()
    sha = g["grammar_sha256"]
    _ok("L6a axis_combos == 282,175,488 (94,058,496 x 3 sumn-axis "
        "values; W12 rsqr-face combos x len(AXIS_SUMN))",
        g["axis_combos"] == 282175488
        == tl12.AXIS_COMBOS * len(AXIS_SUMN))''',
    '''    # ---- L6 grammar structure (eighteen axes / combos / seeds / sha)
    g = build_grammar_w14()
    sha = g["grammar_sha256"]
    _ok("L6a axis_combos == 1,693,052,928 (282,175,488 x 2 resi-axis "
        "x 3 cnt-axis values; W13 sumn-face combos x len(AXIS_RESI) x "
        "len(AXIS_CNT) adjudicated member-set 6-mult)",
        g["axis_combos"] == 1693052928
        == tl13.AXIS_COMBOS * len(AXIS_RESI) * len(AXIS_CNT))''',
    1, "L6a")

rep('''    _ok("L6b sixteen axes present, sumn == frozen three-value",
        len(g["axes"]) == 16 and g["axes"]["sumn"] == AXIS_SUMN)''',
    '''    _ok("L6b eighteen axes present, resi == frozen two-value + cnt "
        "== frozen three-value adjudicated member set",
        len(g["axes"]) == 18 and g["axes"]["sumn"] == AXIS_SUMN
        and g["axes"]["resi"] == AXIS_RESI and len(AXIS_RESI) == 2
        and g["axes"]["cnt"] == AXIS_CNT and len(AXIS_CNT) == 3)''',
    1, "L6b")

rep('_ok("L6c W13 seeds == SEED_REGISTRY berths (20327500/20328000/"',
    '_ok("L6c W14 seeds == SEED_REGISTRY berths (20327500/20328000/"',
    1, "L6c text")

rep('''    _ok("L6d new sha16 constructively distinct from W1/MASS/W2-W12",
        sha not in set(PRIOR_WAVE_SHA16.values())
        and sha != tl12.FROZEN_SHA16,
        f"sha16={sha}")''',
    '''    _ok("L6d new sha16 constructively distinct from W1/MASS/W2-W13",
        sha not in set(PRIOR_WAVE_SHA16.values())
        and sha != tl13.FROZEN_SHA16,
        f"sha16={sha}")''',
    1, "L6d")

rep('''    _ok("L6e exclusion face rows sumn=none-padded to 16-long axis",
        all(len(r["axis"]) == 16 and r["axis"][-1] == "none"
            for r in g["exclusion"]
            ["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_rsqr_sumn_none_face"]))''',
    '''    _ok("L6e exclusion face rows resi/cnt=none-padded to 18-long "
        "axis",
        all(len(r["axis"]) == 18 and r["axis"][-1] == "none"
            and r["axis"][-2] == "none"
            for r in g["exclusion"]
            ["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_std_"
             "rsqr_sumn_resi_cnt_none_face"]))''',
    1, "L6e")

# 7. L8 family
rep('''    # ---- L8 draw contract (deterministic re-draw byte-identity +
    # sixteen-tuple + order-frozen stream)
    ga = build_grammar_w14()
    c1 = next(draw_candidate_sobol_w14(ga, "A", 0, 1))
    c2 = next(draw_candidate_sobol_w14(build_grammar_w14(), "A", 0, 1))
    _ok("L8a Sobol draw determinism (same seed -> byte-identical "
        "candidate incl. the rsqr+sumn axes, sixteen-tuple)",
        json.dumps(c1[1], sort_keys=True) == json.dumps(c2[1],
                                                        sort_keys=True)
        and len(c1[1]["axis"]) == 16)''',
    '''    # ---- L8 draw contract (deterministic re-draw byte-identity +
    # eighteen-tuple + order-frozen stream)
    ga = build_grammar_w14()
    c1 = next(draw_candidate_sobol_w14(ga, "A", 0, 1))
    c2 = next(draw_candidate_sobol_w14(build_grammar_w14(), "A", 0, 1))
    _ok("L8a Sobol draw determinism (same seed -> byte-identical "
        "candidate incl. the resi+cnt axes, eighteen-tuple)",
        json.dumps(c1[1], sort_keys=True) == json.dumps(c2[1],
                                                        sort_keys=True)
        and len(c1[1]["axis"]) == 18)''',
    1, "L8a")

rep('''    rng_a = np.random.default_rng([SEED_GEN + 0, 7919])
    n = 16
    sixteen = [rng_a.integers(0, 4, n) for _ in range(16)]
    rng_b = np.random.default_rng([SEED_GEN + 0, 7919])
    fourteen = [rng_b.integers(0, 4, n) for _ in range(14)]
    _ok("L8b RSQR+SUM append AFTER AMP in the rng stream (first fourteen "
        "axis arrays == W11-order stream verbatim, zero disturbance)",
        all(np.array_equal(a, b) for a, b in zip(sixteen, fourteen)))''',
    '''    rng_a = np.random.default_rng([SEED_GEN + 0, 7919])
    n = 16
    eighteen = [rng_a.integers(0, 4, n) for _ in range(18)]
    rng_b = np.random.default_rng([SEED_GEN + 0, 7919])
    sixteen = [rng_b.integers(0, 4, n) for _ in range(16)]
    _ok("L8b RESI+CNT append AFTER SUMN in the rng stream (first "
        "sixteen axis arrays == W13-order stream verbatim, zero "
        "disturbance)",
        all(np.array_equal(a, b) for a, b in zip(eighteen, sixteen)))''',
    1, "L8b")

# 8. L9a: 18-tuple rows + w13 disc keys (loader tags by source wave)
rep('''    _ok("L9a exclusion loader: every row a 16-tuple axis, sumn=none "
        "at 15 for ALL rows + rsqr at 14 inside the frozen three-value "
        "domain + W12 real-rsqr rows present (25 sources; W1-W11 "
        "sources rsqr=none, W12 survivors/judged carry real values)",
        all(len(r["axis"]) == 16 and r["axis"][15] == "none"
            and r["axis"][14] in AXIS_RSQR for r in rows10)
        and any(r["axis"][14] in ("rsqr20_hi", "rsqr10_hi")
                for r in rows10)
        and {"w1_screen_survivors", "mass_screen_survivors",
             "w9_screen_survivors", "w9_judge_products",
             "w10_screen_survivors", "w10_judge_products",
             "w12_screen_survivors", "w12_judge_products",
             "w14_screen_survivors", "w14_judge_products",
             "judged_supply_weighting"} <= set(disc10))''',
    '''    _ok("L9a exclusion loader: every row an 18-tuple axis, resi/cnt "
        "= none at 16/17 for ALL rows + sumn at 15 inside the frozen "
        "three-value domain + W13 real-sumn rows present (28 "
        "real-read sources; W1-W12 sources sumn=none, W13 survivors/"
        "judged carry real values)",
        all(len(r["axis"]) == 18 and r["axis"][16] == "none"
            and r["axis"][17] == "none"
            and r["axis"][15] in AXIS_SUMN for r in rows10)
        and any(r["axis"][15] in ("sumn20_lo", "sumn10_lo")
                for r in rows10)
        and {"w1_screen_survivors", "mass_screen_survivors",
             "w9_screen_survivors", "w9_judge_products",
             "w10_screen_survivors", "w10_judge_products",
             "w12_screen_survivors", "w12_judge_products",
             "w13_screen_survivors", "w13_judge_products",
             "judged_supply_weighting"} <= set(disc10))''',
    1, "L9a")

# 9. L10b: resi/cnt member values = new-syntax legal cells
rep('''    miss = _excluded_w14({**hit_key,
                          "axis": [*hit_key["axis"][:15],
                                   "sumn20_lo"]},
                         rows10)
    _ok("L10b sumn in {sumn20_lo, sumn10_lo} = new-syntax legal cell, "
        "never excluded",
        miss is None)''',
    '''    miss_r = _excluded_w14({**hit_key,
                            "axis": [*hit_key["axis"][:16],
                                     "resi60_hi",
                                     hit_key["axis"][17]]},
                           rows10)
    miss_c = _excluded_w14({**hit_key,
                            "axis": [*hit_key["axis"][:17],
                                     "cntd5_hi"]},
                           rows10)
    _ok("L10b resi in {resi60_hi} / cnt in {cntd5_hi, cntn20_lo} = "
        "new-syntax legal cells, never excluded",
        miss_r is None and miss_c is None)''',
    1, "L10b")

# 10. parser description + grammar help
rep('''    ap = argparse.ArgumentParser(description="TRIAL_LABOR_W14 runner "
                                     "(MOM+STD+RSQR+SUM sixteen-gate wave)")''',
    '''    ap = argparse.ArgumentParser(description="TRIAL_LABOR_W14 runner "
                                     "(RESI+CNT eighteen-gate wave)")''',
    1, "parser description")
rep('sub.add_parser("grammar", help="serialize the frozen W11 grammar")',
    'sub.add_parser("grammar", help="serialize the frozen W14 grammar")',
    1, "grammar help")

# 11. REGION SPLICE: L12 -> selftest end (full W14 rewire)
START = "    # ---- L12 effective-mask legs (mask level, zero engine burn)"
END = "def _build_parser():"
i = text.find(START)
j = text.find(END)
if i < 0 or j < 0 or j <= i:
    print(f"SPLICE-FAIL: start {i} end {j}")
    sys.exit(1)
removed = text[i:j]
new_region = '''    # ---- L12 effective-mask legs (mask level, zero engine burn)
    tl1.GRAMMAR = g          # engine legs need tl1's grammar global
    frames3 = tl1._synth_prices(n_days=640, n_syms=3, seed=23)
    # controlled crash member: flat 100 (0-299) -> 1%/bar crash
    # (300-330) -> flat to 639 (mom opens only inside the crash window
    # subset {301..349})
    alt_c = pd.Series(100.0, index=frames3["510300"].index)
    avals = alt_c.values.copy()
    for i_ in range(len(avals)):
        if 300 <= i_ <= 330:
            avals[i_] = 100.0 * (0.99 ** (i_ - 299))
        elif i_ > 330:
            avals[i_] = 100.0 * (0.99 ** 31)
    alt_o = pd.Series(100.0, index=alt_c.index)
    alt_v = pd.Series(1000.0, index=alt_c.index)
    alt_h = pd.Series(avals + 1.0, index=alt_c.index)
    alt_l = pd.Series(avals - 1.0, index=alt_c.index)
    frames3[MOM_MEMBER] = pd.DataFrame(
        {"open": alt_o, "high": alt_h, "low": alt_l,
         "close": pd.Series(avals, index=alt_c.index),
         "volume": alt_v, "amount": 1e5}, index=alt_c.index)
    P3 = tl1.build_panels(frames3)
    gs3 = tl3.gate_state_series(frames3)
    vs3 = tl4.vol_state_series(frames3)
    ys3 = tl5.yang_state_series(frames3)
    cs3 = tl6.vconf_state_series(frames3)
    sk3 = tl7.streak_state_series(frames3)
    ts3 = tl8.tstate_state_series(frames3)
    as3 = tl9.amp_state_series(frames3)
    ms3 = mom_state_series(frames3)
    ss3 = std_state_series(frames3)
    rq3 = rsqr_state_series(frames3)
    nq3 = sumn_state_series(frames3)
    rs3 = resi_state_series(frames3)
    cn3 = cnt_state_series(frames3)
    sig = pd.DataFrame(1.0, index=P3["close"].index,
                       columns=P3["close"].columns)
    m_none = _effective_signal_mask_w14(
        sig, frames3, "none", None,
        "none", "none", "none", "none",          # gate vol yang vconf
        "none", "none", "none", "none",          # streak tstate amp mom
        "none", "none", "none", "none",          # std rsqr sumn resi
        "none",                                    # cnt
        gs3, vs3, ys3, cs3, sk3, ts3, as3, ms3, ss3,
        rq3, nq3, rs3, cn3)
    m_w9 = tl9._effective_signal_mask_w9(
        sig, frames3, "none", None, "none", "none", "none", "none",
        "none", "none", "none", gs3, vs3, ys3, cs3, sk3, ts3, as3)
    _ok("L12a effective mask mom=none == W9 face byte-equal "
        "(semantic-baseline identity law)",
        m_none.equals(m_w9))
    m_w13 = tl13._effective_signal_mask_w13(
        sig, frames3, "none", None,
        gate_key="none", vol_key="none", yang_key="none",
        vconf_key="none", streak_key="none", tstate_key="none",
        amp_key="none", mom_key="none", std_key="none",
        rsqr_key="none", sumn_key="none",
        gate_state=gs3, vol_state=vs3, yang_state=ys3,
        vconf_state=cs3, streak_state=sk3, tstate_state=ts3,
        amp_state=as3, mom_state=ms3, std_state=ss3,
        rsqr_state=rq3, sumn_state=nq3)
    _ok("L12a2 effective mask resi/cnt=none == tl13 W13 face "
        "byte-equal (W14 semantic-baseline identity law)",
        m_none.equals(m_w13))
    m_ov = _effective_signal_mask_w14(
        sig, frames3, "none", None,
        "none", "none", "none", "none",          # gate vol yang vconf
        "none", "none", "none", "mom_oversold",  # streak tstate amp mom
        "none", "none", "none", "none",          # std rsqr sumn resi
        "none",                                    # cnt
        gs3, vs3, ys3, cs3, sk3, ts3, as3, ms3, ss3,
        rq3, nq3, rs3, cn3)
    mo_open3 = set(np.flatnonzero((ms3[0] & ms3[1]).values))
    got_ov_days = set(np.flatnonzero(
        (m_ov[m_ov.columns[0]] > 0).values))
    _ok("L12b mom_oversold on the crash face permits ONLY mom-open "
        "decidable days (bite positive leg: permitted day-set == the "
        "mom-open set; warmup bars NEVER permitted)",
        got_ov_days == mo_open3
        and not (got_ov_days & set(range(139))),
        f"open={len(mo_open3)} permitted={len(got_ov_days)}")
    # accelerating-GROWTH member: roc20 strictly increasing -> q10_ref
    # (trailing decile of LOWER roc20s) always below roc20 -> ZERO open
    # days -> mom_oversold mask all-zero (bite negative leg)
    frames5 = tl1._synth_prices(n_days=640, n_syms=3, seed=23)
    grow_c = pd.Series(
        [100.0 * math.exp(0.000008 * (i5 ** 2)) for i5 in range(640)],
        index=frames5["510300"].index)
    frames5[MOM_MEMBER] = pd.DataFrame(
        {"open": pd.Series(100.0, index=grow_c.index),
         "high": grow_c + 1.0, "low": grow_c - 1.0, "close": grow_c,
         "volume": pd.Series(1000.0, index=grow_c.index),
         "amount": 1e5}, index=grow_c.index)
    P5 = tl1.build_panels(frames5)
    gs5 = tl3.gate_state_series(frames5)
    vs5 = tl4.vol_state_series(frames5)
    ys5 = tl5.yang_state_series(frames5)
    cs5 = tl6.vconf_state_series(frames5)
    sk5 = tl7.streak_state_series(frames5)
    ts5 = tl8.tstate_state_series(frames5)
    as5 = tl9.amp_state_series(frames5)
    ms5 = mom_state_series(frames5)
    ss5 = std_state_series(frames5)
    rq5 = rsqr_state_series(frames5)
    nq5 = sumn_state_series(frames5)
    rs5 = resi_state_series(frames5)
    cn5 = cnt_state_series(frames5)
    sig5 = pd.DataFrame(1.0, index=P5["close"].index,
                        columns=P5["close"].columns)
    m5_none = _effective_signal_mask_w14(
        sig5, frames5, "none", None,
        "none", "none", "none", "none",          # gate vol yang vconf
        "none", "none", "none", "none",          # streak tstate amp mom
        "none", "none", "none", "none",          # std rsqr sumn resi
        "none",                                    # cnt
        gs5, vs5, ys5, cs5, sk5, ts5, as5, ms5, ss5,
        rq5, nq5, rs5, cn5)
    m5_ov = _effective_signal_mask_w14(
        sig5, frames5, "none", None,
        "none", "none", "none", "none",          # gate vol yang vconf
        "none", "none", "none", "mom_oversold",  # streak tstate amp mom
        "none", "none", "none", "none",          # std rsqr sumn resi
        "none",                                    # cnt
        gs5, vs5, ys5, cs5, sk5, ts5, as5, ms5, ss5,
        rq5, nq5, rs5, cn5)
    _ok("L12c mom_oversold on the accelerating-growth face (roc20 "
        "strictly increasing = zero oversold days) permits NOTHING "
        "(bite negative leg: all-zero mask while mom=none face is "
        "live)",
        int((m5_ov > 0).sum().sum()) == 0
        and int((m5_none > 0).sum().sum()) > 0
        and int(ms5[0].sum()) == 0)

    # ---- L13 engine-face legs: parity + determinism + mom bites
    base = {"module": "volatility", "fn": "low_vol_long",
            "sig_params": {"n": 60, "top_k": 3, "rebal_days": None},
            "family": "B", "candidate_id": "ST-B-0000",
            "axis": ["none", "time_stop_5d", "equal_weight",
                     "daily_signal"] + ["none"] * 14}
    st3 = pd.Series("GREEN", index=P3["close"].index)
    eq10, tr10, m10, _, _, _, _, _, _, _, sz10, tz10, az10, mz10, \\
        sdz10, rz10, nz10, rrez10, cntz10 = \\
        run_candidate_curve_w14(
            base, None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,
            yang_state=ys3, vconf_state=cs3, streak_state=sk3,
            tstate_state=ts3, amp_state=as3, mom_state=ms3,
            std_state=ss3, rsqr_state=rq3, sumn_state=nq3,
            resi_state=rs3, cnt_state=cn3)
    eq9 = tl9.run_candidate_curve_w9(
        dict(base, axis=base["axis"][:12]), None, frames3, P3, st3,
        gate_state=gs3, vol_state=vs3, yang_state=ys3,
        vconf_state=cs3, streak_state=sk3, tstate_state=ts3,
        amp_state=as3)[0]
    _ok("L13a engine face: mom=none identical to tl9 W9 face "
        "(byte-equal parity law)",
        list(eq10.values) == list(eq9.values))
    eq10b, _, _, _, _, _, _, _, _, _, sz10b, tz10b, az10b, mz10b, \\
        sdz10b, rz10b, nz10b, rrez10b, cntz10b = \\
        run_candidate_curve_w14(
            dict(base, candidate_id="ST-B-0001"), None, frames3, P3,
            st3, gate_state=gs3, vol_state=vs3, yang_state=ys3,
            vconf_state=cs3, streak_state=sk3, tstate_state=ts3,
            amp_state=as3, mom_state=ms3, std_state=ss3,
            rsqr_state=rq3, sumn_state=nq3, resi_state=rs3,
            cnt_state=cn3)
    _ok("L13b engine double-run byte-identity (determinism leg) + "
        "19-tuple return shape (resi_zeroed + cnt_zeroed carried; "
        "all-none face zeroed counters == 0)",
        list(eq10.values) == list(eq10b.values) and sz10 == sz10b
        and tz10 == tz10b and az10 == az10b and mz10 == mz10b == 0
        and rz10 == rz10b == 0 and nz10 == nz10b == 0
        and rrez10 == rrez10b == 0 and cntz10 == cntz10b == 0
        and sdz10 == sdz10b)
    st5 = pd.Series("GREEN", index=P5["close"].index)
    eq5n, tr5n, m5n, _, _, _, _, _, _, _, _, _, az5n, mz5n, \\
        _, _, _, _, _ = \\
        run_candidate_curve_w14(
            dict(base, axis=list(base["axis"])), None, frames5, P5,
            st5, gate_state=gs5, vol_state=vs5, yang_state=ys5,
            vconf_state=cs5, streak_state=sk5, tstate_state=ts5,
            amp_state=as5, mom_state=ms5, std_state=ss5,
            rsqr_state=rq5, sumn_state=nq5, resi_state=rs5,
            cnt_state=cn5)
    _ok("L13c engine face: mom=none on the accelerating-growth face "
        "runs with entries (num_entries > 0 baseline leg)",
        int(m5n.get("num_entries", -1)) > 0 and mz5n == 0)
    eq5o, tr5o, m5o, _, _, _, _, _, _, _, _, _, az5o, mz5o, \\
        _, _, _, rrez5o, cntz5o = \\
        run_candidate_curve_w14(
            dict(base, axis=[*base["axis"][:12], "mom_oversold",
                             "none", "none", "none", "none", "none"]),
            None, frames5, P5, st5, gate_state=gs5, vol_state=vs5,
            yang_state=ys5, vconf_state=cs5, streak_state=sk5,
            tstate_state=ts5, amp_state=as5, mom_state=ms5,
            std_state=ss5, rsqr_state=rq5, sumn_state=nq5,
            resi_state=rs5, cnt_state=cn5)
    _ok("L13d engine face: mom_oversold on the zero-oversold face "
        "zeroes every entry (mask all-zero + engine num_entries == 0 + "
        "mom_zeroed > 0; resi/cnt none-face zeroed == 0)",
        int((m5_ov > 0).sum().sum()) == 0
        and int(m5o.get("num_entries", -1)) == 0 and mz5o > 0
        and rrez5o == 0 and cntz5o == 0)
    eq3o, tr3o, m3o, _, _, _, _, _, _, _, _, _, az3o, mz3o, \\
        _, _, _, _, _ = \\
        run_candidate_curve_w14(
            dict(base, axis=[*base["axis"][:12], "mom_oversold",
                             "none", "none", "none", "none", "none"]),
            None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,
            yang_state=ys3, vconf_state=cs3, streak_state=sk3,
            tstate_state=ts3, amp_state=as3, mom_state=ms3,
            std_state=ss3, rsqr_state=rq3, sumn_state=nq3,
            resi_state=rs3, cnt_state=cn3)
    _ok("L13e engine face: mom_oversold on the crash face runs with "
        "entries on the permitted window (bite positive leg: "
        "num_entries >= 0 with off-window signals zeroed: mom_zeroed "
        "> 0 iff off-open-day signals existed)",
        az3o >= 0 and mz3o >= 0)

    # ---- L14 null-axis draw contract (eighteen-tuple + determinism)
    p1, ax1, rg1 = _null_axis_draw_w14(0)
    p2, ax2, rg2 = _null_axis_draw_w14(0)
    _ok("L14 null-axis draw determinism + EIGHTEEN-tuple with resi+cnt "
        "in the frozen domains (W14 null berth 20328000)",
        p1 == p2 and ax1 == ax2 and len(ax1) == 18
        and ax1[12] in AXIS_MOM and ax1[13] in AXIS_STD
        and ax1[15] in AXIS_SUMN
        and ax1[14] in AXIS_RSQR
        and ax1[16] in AXIS_RESI and ax1[17] in AXIS_CNT
        and ax1[11] in tl9.AXIS_AMP
        and ax1[10] in tl8.AXIS_TSTATE and ax1[9] in tl7.AXIS_STREAK
        and ax1[4] in tl2.AXIS_STOP)

    # ---- L15 funnel faces (dispatch + null path + contract)
    want_cmds = ["grammar", "generate", "screen-prep", "screen",
                 "screen-finalize", "judge-prep", "judge",
                 "judge-finalize", "intake", "status", "selftest"]
    got_cmds = []
    for probe in (["grammar"], ["generate"], ["screen-prep"],
                  ["screen"], ["screen-finalize"], ["judge-prep"],
                  ["judge"], ["judge-finalize"], ["intake"],
                  ["status"], ["selftest"]):
        a = _build_parser().parse_args(probe)
        got_cmds.append(a.cmd)
    a_sh = _build_parser().parse_args(
        ["screen", "--shard", "1", "--shards", "4", "--workers", "9"])
    _ok("L15a main dispatch registers all eleven funnel subcommands "
        "zero-burn (r141 crash-lane: every registered cmd has a body)",
        got_cmds == want_cmds
        and (a_sh.shard, a_sh.shards, a_sh.workers) == (1, 4, 9))
    p_on0, ax0, rng0 = _null_axis_draw_w14(0)
    p_on0b, ax0b, rng0b = _null_axis_draw_w14(0)
    dom0 = (ax0[12] in AXIS_MOM and ax0[13] in AXIS_STD
            and ax0[15] in AXIS_SUMN
            and ax0[14] in AXIS_RSQR
            and ax0[16] in AXIS_RESI and ax0[17] in AXIS_CNT
            and ax0[4] in tl2.AXIS_STOP and len(ax0) == 18)
    mat0 = rng0.random((len(P3["close"].index), len(P3["close"].columns)))
    eqn, trn, mtn, prn, pt, frn, gzn, vzn, yzn, czn, szn, tzn, azn, \\
        mzn, sdzn, rzn, nznn, rrezn, cntzn = \\
        run_candidate_curve_w14(
            {"module": "null", "fn": "random_signal",
             "sig_params": {"p_on": p_on0}, "axis": ax0,
             "candidate_id": "W14-NULL-0000", "family": "NULL"},
            None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,
            yang_state=ys3, vconf_state=cs3, streak_state=sk3,
            tstate_state=ts3, amp_state=as3, mom_state=ms3,
            std_state=ss3, rsqr_state=rq3, sumn_state=nq3,
            resi_state=rs3, cnt_state=cn3, rng_matrix=mat0,
            p_on=p_on0)
    mat0b = rng0b.random((len(P3["close"].index),
                          len(P3["close"].columns)))
    eqnb, _, _, _, _, _, _, _, _, _, _, _, _, mznb, _, rznb, nznb, \\
        rreznb, cntznb = \\
        run_candidate_curve_w14(
            {"module": "null", "fn": "random_signal",
             "sig_params": {"p_on": p_on0b}, "axis": ax0b,
             "candidate_id": "W14-NULL-0000", "family": "NULL"},
            None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,
            yang_state=ys3, vconf_state=cs3, streak_state=sk3,
            tstate_state=ts3, amp_state=as3, mom_state=ms3,
            std_state=ss3, rsqr_state=rq3, sumn_state=nq3,
            resi_state=rs3, cnt_state=cn3, rng_matrix=mat0b,
            p_on=p_on0b)
    _ok("L15b null-cell engine path: eighteen-tuple null draw "
        "deterministic + resi/cnt axis in-domain + engine 19-tuple "
        "return + double-run byte-identity (screen null-family path)",
        p_on0 == p_on0b and ax0 == ax0b and dom0
        and len(eqn) == len(P3["close"].index) and mzn >= 0
        and list(eqn.values) == list(eqnb.values) and mzn == mznb
        and rzn == rznb
        and nznn == nznb and rrezn == rreznb and cntzn == cntznb)
    _ok("L15c screen CSV contract carries the mom+std+rsqr+sumn+resi+"
        "cnt columns in the frozen order (cell_id/candidate_id head + "
        "resi/cnt pairs before survives_screen)",
        csv_cols_screen_w14[:2] == ["cell_id", "candidate_id"]
        and csv_cols_screen_w14[-7:] == ["sumn_face", "sumn_zeroed",
                                         "resi_face", "resi_zeroed",
                                         "cnt_face", "cnt_zeroed",
                                         "survives_screen"]
        and "mom_face" in csv_cols_screen_w14
        and {"gate_zeroed", "vol_zeroed", "yang_zeroed", "vconf_zeroed",
             "streak_zeroed", "tstate_zeroed", "amp_zeroed",
             "mom_zeroed", "std_zeroed", "rsqr_zeroed", "sumn_zeroed",
             "resi_zeroed", "cnt_zeroed"} <= set(csv_cols_screen_w14))

    g_scr = tl6.finalize_already_landed(SCREEN_BATCH, SCREEN_FILE)
    if os.path.exists(SCREEN_FILE):
        _ok("L15d pit-95 guard live-fire: w14_screen.json carries "
            "SCREEN_BATCH -> finalize re-run would be refused",
            isinstance(g_scr, dict)
            and g_scr.get("batch") == SCREEN_BATCH
            and isinstance(g_scr.get("total"), int))
    else:
        _ok("L15d pit-95 guard fresh-face: w14_screen.json absent -> "
            "guard None = lawful fresh batch, finalize proceeds",
            g_scr is None)
    g_jdg = tl6.finalize_already_landed(JUDGE_BATCH, JUDGE_FILE)
    if os.path.exists(JUDGE_FILE):
        _ok("L15e pit-95 guard live-fire: w14_judge.json carries "
            "JUDGE_BATCH -> finalize re-run would be refused",
            isinstance(g_jdg, dict)
            and g_jdg.get("batch") == JUDGE_BATCH
            and isinstance(g_jdg.get("total"), int))
    else:
        _ok("L15e pit-95 guard fresh-face: w14_judge.json absent -> "
            "guard None = lawful fresh batch, finalize proceeds",
            g_jdg is None)

    # ---- L16 G-RESI/G-CNT real-face anchor loads (W14 own faces;
    # internal gates assert every probe anchor fail-closed)
    re_st, re_err = _resi_state_full()
    _ok("L16a real-face state loads G-RESI clean (n 3483 / grids / "
        "extreme-day anchors fail-closed; r470/r471 probe basis)",
        re_st is not None and re_err is None, re_err or "anchors clean")
    if re_st is not None:
        _re_meta = re_st[2]
        _ok("L16b G-RESI exact anchors (n_bars 3483 + structure "
            "pass: 120-bar warmup partitions)",
            _re_meta.get("n_bars") == 3483
            and _resi_structure_pass(_re_meta))
    cn_st, cn_err = _cnt_state_full()
    _ok("L16c real-face state loads G-CNT clean (dual cntd5+cntn20 "
        "sub-faces / grids / extreme days fail-closed; r470/r471 + "
        "bm-c r277 twin probe basis)",
        cn_st is not None and cn_err is None, cn_err or "anchors clean")
    if cn_st is not None:
        _cn_meta = cn_st[4]
        _ok("L16d G-CNT exact anchors (n_bars 3483 + dual sub-face "
            "structure pass)",
            _cn_meta.get("n_bars") == 3483
            and _cnt_structure_pass(_cn_meta))

    print(f"\\nselftest: {n_pass}/{n_leg} PASS "
          f"(scope: W14 resi+cnt layer + G-RESI/G-CNT + "
          f"eighteen-tuple grammar + machinery: effective mask / "
          f"curve runner parity / null draw / 28-source exclusion "
          f"loader + funnel faces: dispatch / null-cell engine path / "
          f"CSV contract + pit-95 finalize idempotency guard "
          f"state-adaptive legs + W10-W13 regression legs; zero live "
          f"cells burned, zero numbers fabricated)")
    return 0 if n_pass == n_leg else 1


'''
text = text[:i] + new_region + text[j:]
log.append(("L12-region splice", removed.count("\n")))

open(DRAFT, "w", encoding="utf-8", newline="\n").write(text)
print(f"edits5 OK: {len(log)} operations")
for name, n in log:
    print(f"  [{name}] x{n}")
print(f"draft now {text.count(chr(10))} lines")
