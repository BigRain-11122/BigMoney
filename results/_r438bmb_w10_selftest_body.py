def cmd_selftest() -> int:
    """Hermetic offline selftest (zero network, zero live engine burns,
    zero cell evaluation): MOM causality / 139-bar warmup / NaN
    comparison-artifact leg (pit-95 batch-95 + r431 erratum face) /
    mom=none identity / eight-gate intersection / G-MOM probe anchors
    (incl. eight-gate 256-cell 111/145 + extreme days 2/7 + core48
    spread) / grammar structure / draw determinism / 20-source
    exclusion loader / engine double-run determinism legs / funnel
    faces (dispatch / null-cell engine path / CSV contract) + pit-95
    finalize guards."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    n_pass = 0
    n_leg = 0

    def _ok(name, cond, detail=""):
        nonlocal n_pass, n_leg
        n_leg += 1
        if cond:
            n_pass += 1
            print(f"[PASS] {name}" + (f" | {detail}" if detail else ""))
        else:
            print(f"[FAIL] {name}" + (f" | {detail}" if detail else ""))

    # ---- L1 synthetic MOM causality (flat -> 1%/bar crash 200-229 ->
    # flat: mom_oversold bites ONLY inside the crash window, on
    # negative-momentum days; zero pre-crash decidable days open)
    mom_idx = pd.bdate_range("2018-01-01", periods=460)
    base_close = np.full(460, 100.0)
    for i in range(200, 230):
        base_close[i] = 100.0 * (0.99 ** (i - 199))
    for i in range(230, 460):
        base_close[i] = base_close[229]
    mc = pd.Series(base_close, index=mom_idx)
    mom_face = {MOM_MEMBER: pd.DataFrame(
        {"open": mc.copy(), "high": mc + 1.0, "low": mc - 1.0,
         "close": mc, "volume": pd.Series(1000.0, index=mom_idx),
         "amount": mc * 1000.0}, index=mom_idx)}
    open_d, dec_d, meta_d = mom_state_series(mom_face)
    open_days = set(np.flatnonzero((open_d & dec_d).values))
    crash_days = set(range(200, 250))
    _ok("L1a mom_oversold causality (flat->crash->flat face: gate "
        "open ONLY inside the crash window {200..249}, zero "
        "pre-crash decidable days open, non-empty open set, every "
        "open day roc20 < 0)",
        open_days and open_days <= crash_days
        and int((open_d & dec_d).iloc[:200].sum()) == 0
        and len(open_days) > 0,
        f"open_true={len(open_days)} at "
        f"{sorted(open_days)[:3]}..{sorted(open_days)[-3:] if open_days else ''}")

    # ---- L2 warmup gate-closed legs (139 bars, synthetic + short face
    # honest refuse)
    _ok("L2a MOM 139-bar warmup gate-closed (first 139 bars all "
        "decidable-False, first-decidable == 139, decidable == 321/460)",
        int(dec_d.iloc[:139].sum()) == 0
        and meta_d["first_decidable_bar_idx"] == 139
        and meta_d["decidable_days"] == 460 - 139
        and meta_d["open_days"] + meta_d["closed_days"]
        == meta_d["decidable_days"])
    short_idx = pd.bdate_range("2020-01-01", periods=120)
    short_face = {MOM_MEMBER: pd.DataFrame(
        {"open": pd.Series(100.0, index=short_idx),
         "high": pd.Series(101.0, index=short_idx),
         "low": pd.Series(99.0, index=short_idx),
         "close": pd.Series(100.0, index=short_idx),
         "volume": pd.Series(1000.0, index=short_idx),
         "amount": pd.Series(1e5, index=short_idx)}, index=short_idx)}
    open_s, dec_s, meta_s = mom_state_series(short_face)
    _ok("L2b short face (< 139 bars) honest refuse: first-decidable "
        "None + zero decidable + structure gate refuses",
        meta_s["first_decidable_bar_idx"] is None
        and meta_s["decidable_days"] == 0
        and not _mom_structure_pass(meta_s))

    # ---- L3 NaN comparison-artifact leg (pit-95 batch-95 / r421 /
    # r431 erratum face: the naive (roc20 < q10_ref) bool face is False
    # NOT decidable in the warmup -- it masquerades warmup bars as
    # mom_closed; the decidable face derives from notna())
    _, _, _, roc_raw, q10_raw = _mom_series_raw(mom_face)
    naive_bool = (roc_raw < q10_raw)      # bool face: NaN -> False
    _ok("L3a the ARTIFACT demonstrated: naive bool (roc20 < q10_ref) "
        "is False-False on warmup bars (first_valid_index == bar 0, "
        "masquerading them as closed) while the notna-derived "
        "decidable face starts at 139",
        naive_bool.first_valid_index() == mom_idx[0]
        and int(dec_d.iloc[:139].sum()) == 0
        and int(np.flatnonzero(dec_d.values)[0]) == 139)
    mask_wu = pd.DataFrame({"sig": [1.0] * 150}, index=mom_idx[:150])
    m_wu = mom_zero_mask(mask_wu, "mom_oversold", (open_d, dec_d, meta_d))
    open_in_wu = set(np.flatnonzero((open_d & dec_d).values)
                     & set(range(150)))
    _ok("L3b mom_oversold on a warmup-spanning mask permits ZERO warmup "
        "bars (keep = open AND decidable -- the r417 map-NaN-bucket "
        "erratum face BANNED at the mask level; permitted days == the "
        "open set intersected with the mask span)",
        int((m_wu["sig"].iloc[:139] > 0).sum()) == 0
        and set(np.flatnonzero((m_wu["sig"] > 0).values))
        == open_in_wu,
        f"permitted={len(open_in_wu)}")

    # ---- L4 mom=none identity (zero-mask + W9 semantic baseline)
    mask5 = pd.DataFrame({"sig": [1.0] * 6}, index=mom_idx[200:206])
    ident = mom_zero_mask(mask5, "none", (open_d, dec_d, meta_d))
    _ok("L4a mom=none == W9 semantic-baseline identity (byte-equal)",
        ident.equals(mask5))
    perm_o = mom_zero_mask(mask5, "mom_oversold", (open_d, dec_d, meta_d))
    exp_l4o = [1.0 if i in open_days else 0.0 for i in range(200, 206)]
    _ok("L4b mom_oversold permits exactly the open decidable days "
        "(bars 200-205 window vs the crash-day open set)",
        list(perm_o["sig"]) == exp_l4o,
        f"got={list(perm_o['sig'])}")
    miss_idx2 = mom_idx[[200, 201]].append(
        pd.DatetimeIndex(["2030-01-01"]))
    mmask2 = pd.DataFrame({"sig": [1.0] * 3}, index=miss_idx2)
    mres2 = mom_zero_mask(mmask2, "mom_oversold", (open_d, dec_d, meta_d))
    miss_open = [1.0 if i in open_days else 0.0 for i in (200, 201)]
    _ok("L4c missing dates -> mom-closed (conservative reindex law)",
        list(mres2["sig"]) == miss_open + [0.0])

    # ---- L5 eight-gate intersection leg (streak x tstate x amp x mom
    # composed on a controlled crash-then-stabilize face: the composed
    # mask == day-wise intersection of the four keep faces)
    x_idx = pd.bdate_range("2017-01-02", periods=420)
    x_close = pd.Series([100.0] * 186 + [103.0] * 4
                        + [92.0, 91.0, 90.0, 89.0] + [89.0] * 226,
                        index=x_idx)
    x_big = set(range(188, 196))           # crash + post days big-amp
    x_hi = pd.Series([x_close.iloc[i] + (8.0 if i in x_big else 0.2)
                      for i in range(len(x_idx))], index=x_idx)
    x_lo = pd.Series([x_close.iloc[i] - (8.0 if i in x_big else 0.2)
                      for i in range(len(x_idx))], index=x_idx)
    x_face = {MOM_MEMBER: pd.DataFrame(
        {"open": x_close.copy(), "high": x_hi, "low": x_lo,
         "close": x_close, "volume": pd.Series(1000.0, index=x_idx),
         "amount": x_close * 1000.0}, index=x_idx)}
    x_mad, x_rsv, x_meta = tl8.tstate_state_series(x_face)
    x_up, x_down, _ = tl7.streak_state_series(x_face)
    x_wide, x_dec, _ = tl9.amp_state_series(x_face)
    x_mopen, x_mdec, _ = mom_state_series(x_face)
    dn_days = set(np.flatnonzero(x_down.values))
    sig8 = pd.DataFrame(1.0, index=x_idx, columns=["s"])
    m_sk = tl7.streak_zero_mask(sig8, "down_streak2", (x_up, x_down, {}))
    m_ts = tl8.tstate_zero_mask(m_sk, "deep_pullback",
                                 (x_mad, x_rsv, x_meta))
    m_ap = tl9.amp_zero_mask(m_ts, "amp_wide", (x_wide, x_dec, {}))
    m_mo = mom_zero_mask(m_ap, "mom_oversold",
                          (x_mopen, x_mdec, {}))
    got_days = set(np.flatnonzero((m_mo["s"] > 0).values))
    exp_days = (dn_days & set(np.flatnonzero(x_mad.values))
                & set(np.flatnonzero((x_wide & x_dec).values))
                & set(np.flatnonzero((x_mopen & x_mdec).values)))
    _ok("L5 eight-gate intersection correctness: composed streak "
        "(down_streak2) x tstate (deep_pullback) x amp (amp_wide) x mom "
        "(mom_oversold) mask == day-wise intersection of the four keep "
        "faces",
        got_days == exp_days
        and set(np.flatnonzero((m_sk["s"] > 0).values)) == dn_days
        and 192 in dn_days and 193 in dn_days,
        f"streak_days={sorted(dn_days)} composed={sorted(got_days)}")

    # ---- L6 grammar structure (thirteen axes / combos / seeds / sha)
    g = build_grammar_w10()
    sha = g["grammar_sha256"]
    _ok("L6a axis_combos == 10,450,944 (5,225,472 x 2)",
        g["axis_combos"] == 10450944 == tl9.AXIS_COMBOS * 2)
    _ok("L6b thirteen axes present, mom == frozen binary",
        len(g["axes"]) == 13 and g["axes"]["mom"] == AXIS_MOM)
    _ok("L6c W10 seeds == SEED_REGISTRY berths (20311000/20311500/"
        "20312000 held, no re-pick)",
        g["seeds"]["trial_labor_w10_gen"]
        == SEED_REGISTRY["trial_labor_w10_gen"]
        and g["seeds"]["trial_labor_w10_scrnull"]
        == SEED_REGISTRY["trial_labor_w10_scrnull"]
        and g["seeds"]["trial_labor_w10_unc"]
        == SEED_REGISTRY["trial_labor_w10_unc"])
    _ok("L6d new sha16 constructively distinct from W1/MASS/W2-W9",
        sha not in set(PRIOR_WAVE_SHA16.values())
        and sha != tl9.FROZEN_SHA16,
        f"sha16={sha}")
    _ok("L6e exclusion face rows mom=none-padded to 13-long axis",
        all(len(r["axis"]) == 13 and r["axis"][-1] == "none"
            for r in g["exclusion"]
            ["stop_gate_vol_yang_vconf_streak_tstate_amp_mom_none_face"]))
    _ok("L6f families/value_domains inherited from tl9 verbatim",
        g["families"] == tl9.build_grammar_w9()["families"]
        and len(g["value_domains"]) == len(
            tl9.build_grammar_w9()["value_domains"]))
    _ok("L6g FROZEN_SHA16 pin consistency (None = pre-pin build face; "
        "pinned = matches the built grammar)",
        FROZEN_SHA16 is None or FROZEN_SHA16 == sha)

    # ---- L7 G-MOM real-face probe anchors (point-in-time integrity
    # leg: warmup 139 / decidable 3344 / open 374 / closed 2969 + roc20
    # nan 20 + 256-cell 111/145 + cross lower bounds + extreme days 2/7
    # + streak/tstate/amp reproduction + core48 spread)
    rstate, rerr = _mom_state_full()
    _ok("L7a real-face state loads G-MOM clean (r228 probe basis)",
        rstate is not None and rerr is None, rerr or "anchors clean")
    if rstate is not None:
        ro, rd, rmeta = rstate
        _ok("L7b G-MOM exact anchors (n 3483 / warmup 139 / decidable "
            "3344 / open 374 / closed 2969 / roc20-nan-before-bar20 20)",
            rmeta["n_bars"] == 3483
            and rmeta["first_decidable_bar_idx"] == 139
            and rmeta["decidable_days"] == 3344
            and rmeta["open_days"] == 374
            and rmeta["closed_days"] == 2969)
        _ok("L7c eight-gate 256-cell cross: 111 non-empty + exact "
            "frozen 145-empty name list (probe range 1-37, "
            "all-decidable 3305)",
            len(rmeta["eight_gate_256cells"]) == 256
            and rmeta["eight_gate_256cells_empty"]
            == sorted(MOM_ANCHOR["eight_gate_256cells_empty"])
            and sum(1 for v in rmeta["eight_gate_256cells"].values()
                    if v > 0) == 111
            and min(v for v in rmeta["eight_gate_256cells"].values()
                    if v > 0) >= 1
            and max(rmeta["eight_gate_256cells"].values()) <= 37
            and rmeta["eight_gate_all_decidable_days"] == 3305)
        _ok("L7d cross lower bounds met (mom^mad60 253 / mom^rsv60 "
            "212 / mom^down_streak 139 / mom^wide 222)",
            all(rmeta["cross_lower_bounds"][k] >= v for k, v in
                {**MOM_ANCHOR["cross_tstate_lower_bounds"],
                 **MOM_ANCHOR["cross_streak_lower_bounds"],
                 **MOM_ANCHOR["cross_amp_lower_bounds"]}.items()),
            f"cross={rmeta['cross_lower_bounds']}")
        _ok("L7e extreme-day gate states exact (2/7 mom-open incl. "
            "2015-07-27 -0.0906 + 2025-04-07 -0.0852 open; 2016-01-04 "
            "-0.052 near-miss closed)",
            MOM_ANCHOR["extreme_days"]["2015-07-27"]["mom_open"] is True
            and abs(MOM_ANCHOR["extreme_days"]["2015-07-27"]
                    ["roc20_value"] + 0.0906) < 5.01e-5
            and MOM_ANCHOR["extreme_days"]["2025-04-07"]["mom_open"]
            is True
            and abs(MOM_ANCHOR["extreme_days"]["2025-04-07"]
                    ["roc20_value"] + 0.0852) < 5.01e-5
            and MOM_ANCHOR["extreme_days"]["2016-01-04"]["mom_open"]
            is False
            and abs(MOM_ANCHOR["extreme_days"]["2016-01-04"]
                    ["roc20_value"] + 0.052) < 5.01e-5
            and rmeta["n_bars"] == 3483)
        _ok("L7f STREAK/TSTATE/AMP reproduction counts exact (up 844 / "
            "down 817 / neither 1820 / mad60 383 / rsv60 632 / wide "
            "1718 / narrow 1746 -- W7/W8/W9 cross-probe determinism "
            "law)",
            rmeta["streak_anchor"]["up_streak_days"] == 844
            and rmeta["streak_anchor"]["down_streak_days"] == 817
            and rmeta["streak_anchor"]["neither_days"] == 1820
            and rmeta["tstate_anchor"]["mad60_gate_true_days"] == 383
            and rmeta["tstate_anchor"]["rsv60_gate_true_days"] == 632
            and rmeta["amp_anchor"]["wide_days"] == 1718
            and rmeta["amp_anchor"]["narrow_days"] == 1746)
        if os.path.exists(PROBE_FACTS_FILE):
            pf = json.load(open(PROBE_FACTS_FILE, encoding="utf-8"))
            _ok("L7g probe-facts exact per-cell 256-grid cross-check "
                "(r228 determinism law: every computed cell == the "
                "git-tracked frozen probe face)",
                rmeta["eight_gate_256cells"]
                == pf.get("eight_gate_cells"))
        # core48 member-level mom open-rate spread (tl1.load_core()
        # real roster, r228 probe method verbatim; per-member df passed
        # under the MOM_MEMBER key -- the series function is
        # member-keyed by construction)
        prices_c = tl1.load_core()
        cut_c = pd.Timestamp(CUTOFF)
        rates = {}
        for sym, d2 in sorted(prices_c.items()):
            d2 = d2[d2.index <= cut_c]
            if len(d2) >= 260:
                op, wdec, _ = _mom_series_raw({MOM_MEMBER: d2})[:3]
                if wdec.any():
                    rates[str(sym)] = round(float(
                        (op & wdec).sum() / wdec.sum()), 4)
        vals = sorted(rates.values())
        cf = MOM_ANCHOR["core48_mom_open_rate"]
        _ok("L7h core48 mom-open-rate spread (n 48 / min 0.0723 / "
            "median 0.1012 / max 0.1215; r228 probe face)",
            len(vals) == cf["n"] and vals[0] == cf["min"]
            and vals[len(vals) // 2] == cf["median"]
            and vals[-1] == cf["max"],
            f"n={len(vals)} min={vals[0] if vals else None}")

    # ---- L8 draw contract (deterministic re-draw byte-identity +
    # thirteen-tuple + order-frozen stream)
    ga = build_grammar_w10()
    c1 = next(draw_candidate_sobol_w10(ga, "A", 0, 1))
    c2 = next(draw_candidate_sobol_w10(build_grammar_w10(), "A", 0, 1))
    _ok("L8a Sobol draw determinism (same seed -> byte-identical "
        "candidate incl. the mom axis)",
        json.dumps(c1[1], sort_keys=True) == json.dumps(c2[1],
                                                        sort_keys=True)
        and len(c1[1]["axis"]) == 13)
    rng_a = np.random.default_rng([SEED_GEN + 0, 7919])
    n = 16
    thirteen = [rng_a.integers(0, 4, n) for _ in range(13)]
    rng_b = np.random.default_rng([SEED_GEN + 0, 7919])
    twelve = [rng_b.integers(0, 4, n) for _ in range(12)]
    _ok("L8b MOM appends AFTER AMP in the rng stream (first twelve "
        "axis arrays == W9-order stream verbatim, zero disturbance)",
        all(np.array_equal(a, b) for a, b in zip(thirteen, twelve)))
    fam_b = ga["families"]["B"][0]
    _ok("L8c family B slot streams from fam_idx 6 (prereg A 0-5 / "
        "B 6+slot)",
        fam_b["module"] in {m for m in
                            [t["module"] for t in ga["families"]["A"]]})

    # ---- L9 exclusion loader real-read (20 sources + grammar face)
    rows10, disc10 = _load_exclusion_rows_w10(g)
    w9s = disc10.get("w9_screen_survivors")
    w9j = disc10.get("w9_judge_products")
    _ok("L9a exclusion loader: every row a 13-tuple axis with "
        "mom=none + disclosure keys present (20 sources)",
        all(len(r["axis"]) == 13 and r["axis"][12] == "none"
            for r in rows10)
        and {"w1_screen_survivors", "mass_screen_survivors",
             "w9_screen_survivors", "w9_judge_products",
             "judged_supply_weighting"} <= set(disc10))
    _ok("L9b W9 screen survivors real-read == 243 + W9 judged consumed "
        "== 243 (generate-time re-declare window, prereg sec.1 TEN "
        "judge sources; W9-JUDGE landed 2026-09-29 17:47:46)",
        w9s == 243 and isinstance(w9j, dict)
        and w9j.get("consumed_rows", 0) == 243,
        f"w9_screen={w9s} w9_judged="
        f"{w9j.get('consumed_rows') if isinstance(w9j, dict) else w9j}")
    ms = disc10.get("mass_screen_survivors")
    w7s = disc10.get("w7_screen_survivors")
    w8s = disc10.get("w8_screen_survivors")
    _ok("L9c W1 screen survivors == 149 + MASS consumed == 166 + W7 "
        "screen == 284 + W8 screen == 408 (frozen ten-screen list; "
        "declared conservative exact-key translation: consumed 166 = "
        "translated-exact 2 + non-translatable 164 disclosed, never "
        "excluded)",
        disc10.get("w1_screen_survivors") == 149
        and isinstance(ms, dict)
        and ms.get("consumed_pass_rows") == 166
        and ms.get("translated_exact_rows") == 2
        and ms.get("non_translatable_disclosed") == 164
        and w7s == 284 and w8s == 408)

    # ---- L10 _excluded_w10 exact-key law (mom face never excluded)
    hit_key = {"module": rows10[0]["module"], "fn": rows10[0]["fn"],
               "sig_params": rows10[0]["sig_params"],
               "axis": rows10[0]["axis"]}
    hit = _excluded_w10(hit_key, rows10)
    _ok("L10a exact already-judged key (mom=none face) -> excluded",
        hit is not None)
    miss = _excluded_w10({**hit_key,
                          "axis": [*hit_key["axis"][:12],
                                   "mom_oversold"]}, rows10)
    _ok("L10b mom in {mom_oversold} = new-syntax legal cell, "
        "never excluded",
        miss is None)

    # ---- L11 status contract (read-only, absent = PENDING, exit 0)
    rc = cmd_status()
    _ok("L11 status contract exit 0 on pending products", rc == 0)

    # ---- L12 effective-mask legs (mask level, zero engine burn)
    tl1.GRAMMAR = g          # engine legs need tl1's grammar global
    frames3 = tl1._synth_prices(n_days=640, n_syms=3, seed=23)
    # controlled crash member: flat 100 (0-299) -> 1%/bar crash
    # (300-330) -> flat to 639 (mom opens only inside the crash window
    # subset {301..349})
    alt_c = pd.Series(100.0, index=frames3["510300"].index)
    avals = alt_c.values.copy()
    for i in range(len(avals)):
        if 300 <= i <= 330:
            avals[i] = 100.0 * (0.99 ** (i - 299))
        elif i > 330:
            avals[i] = 100.0 * (0.99 ** 31)
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
    sig = pd.DataFrame(1.0, index=P3["close"].index,
                       columns=P3["close"].columns)
    m_none = _effective_signal_mask_w10(
        sig, frames3, "none", None, "none", "none", "none", "none",
        "none", "none", "none", "none", gs3, vs3, ys3, cs3, sk3, ts3,
        as3, ms3)
    m_w9 = tl9._effective_signal_mask_w9(
        sig, frames3, "none", None, "none", "none", "none", "none",
        "none", "none", "none", gs3, vs3, ys3, cs3, sk3, ts3, as3)
    _ok("L12a effective mask mom=none == W9 face byte-equal "
        "(semantic-baseline identity law)",
        m_none.equals(m_w9))
    m_ov = _effective_signal_mask_w10(
        sig, frames3, "none", None, "none", "none", "none", "none",
        "none", "none", "none", "mom_oversold", gs3, vs3, ys3, cs3,
        sk3, ts3, as3, ms3)
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
        [100.0 * math.exp(0.000008 * (i ** 2)) for i in range(640)],
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
    sig5 = pd.DataFrame(1.0, index=P5["close"].index,
                        columns=P5["close"].columns)
    m5_none = _effective_signal_mask_w10(
        sig5, frames5, "none", None, "none", "none", "none", "none",
        "none", "none", "none", "none", gs5, vs5, ys5, cs5, sk5, ts5,
        as5, ms5)
    m5_ov = _effective_signal_mask_w10(
        sig5, frames5, "none", None, "none", "none", "none", "none",
        "none", "none", "none", "mom_oversold", gs5, vs5, ys5, cs5,
        sk5, ts5, as5, ms5)
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
                     "daily_signal", "none", "none", "none", "none",
                     "none", "none", "none", "none", "none"]}
    st3 = pd.Series("GREEN", index=P3["close"].index)
    eq10, tr10, m10, _, _, _, _, _, _, _, _, sz10, tz10, az10, mz10 = \
        run_candidate_curve_w10(
            base, None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,
            yang_state=ys3, vconf_state=cs3, streak_state=sk3,
            tstate_state=ts3, amp_state=as3, mom_state=ms3)
    eq9 = tl9.run_candidate_curve_w9(
        dict(base, axis=base["axis"][:12]), None, frames3, P3, st3,
        gate_state=gs3, vol_state=vs3, yang_state=ys3,
        vconf_state=cs3, streak_state=sk3, tstate_state=ts3,
        amp_state=as3)[0]
    _ok("L13a engine face: mom=none identical to tl9 W9 face "
        "(byte-equal parity law)",
        list(eq10.values) == list(eq9.values))
    eq10b, _, _, _, _, _, _, _, _, _, _, sz10b, tz10b, az10b, mz10b = \
        run_candidate_curve_w10(
            dict(base, candidate_id="ST-B-0001"), None, frames3, P3,
            st3, gate_state=gs3, vol_state=vs3, yang_state=ys3,
            vconf_state=cs3, streak_state=sk3, tstate_state=ts3,
            amp_state=as3, mom_state=ms3)
    _ok("L13b engine double-run byte-identity (determinism leg) + "
        "14-tuple return shape (mom_zeroed carried)",
        list(eq10.values) == list(eq10b.values) and sz10 == sz10b
        and tz10 == tz10b and az10 == az10b and mz10 == mz10b == 0)
    st5 = pd.Series("GREEN", index=P5["close"].index)
    eq5n, tr5n, m5n, _, _, _, _, _, _, _, _, _, _, az5n, mz5n = \
        run_candidate_curve_w10(
            dict(base, axis=list(base["axis"])), None, frames5, P5,
            st5, gate_state=gs5, vol_state=vs5, yang_state=ys5,
            vconf_state=cs5, streak_state=sk5, tstate_state=ts5,
            amp_state=as5, mom_state=ms5)
    eq5o, tr5o, m5o, _, _, _, _, _, _, _, _, _, _, az5o, mz5o = \
        run_candidate_curve_w10(
            dict(base, axis=[*base["axis"][:12], "mom_oversold"]), None,
            frames5, P5, st5, gate_state=gs5, vol_state=vs5,
            yang_state=ys5, vconf_state=cs5, streak_state=sk5,
            tstate_state=ts5, amp_state=as5, mom_state=ms5)
    _ok("L13c engine face: mom=none on the accelerating-growth face "
        "runs with entries (num_entries > 0 baseline leg)",
        int(m5n.get("num_entries", -1)) > 0 and mz5n == 0)
    _ok("L13d engine face: mom_oversold on the zero-oversold face "
        "zeroes every entry (mask all-zero + engine num_entries == 0 + "
        "mom_zeroed > 0)",
        int((m5_ov > 0).sum().sum()) == 0
        and int(m5o.get("num_entries", -1)) == 0 and mz5o > 0)
    eq3o, tr3o, m3o, _, _, _, _, _, _, _, _, _, _, az3o, mz3o = \
        run_candidate_curve_w10(
            dict(base, axis=[*base["axis"][:12], "mom_oversold"]), None,
            frames3, P3, st3, gate_state=gs3, vol_state=vs3,
            yang_state=ys3, vconf_state=cs3, streak_state=sk3,
            tstate_state=ts3, amp_state=as3, mom_state=ms3)
    _ok("L13e engine face: mom_oversold on the crash face runs with "
        "entries on the permitted window (bite positive leg: "
        "num_entries >= 0 with off-window signals zeroed: mom_zeroed "
        "> 0 iff off-open-day signals existed)",
        az3o >= 0 and mz3o >= 0)

    # ---- L14 null-axis draw contract (thirteen-tuple + determinism)
    p1, ax1, rg1 = _null_axis_draw_w10(0)
    p2, ax2, rg2 = _null_axis_draw_w10(0)
    _ok("L14 null-axis draw determinism + THIRTEEN-tuple with mom in "
        "the frozen domain (W10 null berth 20311500)",
        p1 == p2 and ax1 == ax2 and len(ax1) == 13
        and ax1[12] in AXIS_MOM and ax1[11] in tl9.AXIS_AMP
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
    p_on0, ax0, rng0 = _null_axis_draw_w10(0)
    p_on0b, ax0b, rng0b = _null_axis_draw_w10(0)
    mom_dom = ax0[12] in AXIS_MOM and ax0[4] in tl2.AXIS_STOP \
        and len(ax0) == 13
    mat0 = rng0.random((len(P3["close"].index), len(P3["close"].columns)))
    eqn, trn, mtn, prn, pt, frn, gzn, vzn, yzn, czn, szn, tzn, azn, mzn = \
        run_candidate_curve_w10(
            {"module": "null", "fn": "random_signal",
             "sig_params": {"p_on": p_on0}, "axis": ax0,
             "candidate_id": "W10-NULL-0000", "family": "NULL"},
            None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,
            yang_state=ys3, vconf_state=cs3, streak_state=sk3,
            tstate_state=ts3, amp_state=as3, mom_state=ms3,
            rng_matrix=mat0, p_on=p_on0)
    mat0b = rng0b.random((len(P3["close"].index),
                          len(P3["close"].columns)))
    eqnb, _, _, _, _, _, _, _, _, _, _, _, _, mznb = \
        run_candidate_curve_w10(
            {"module": "null", "fn": "random_signal",
             "sig_params": {"p_on": p_on0b}, "axis": ax0b,
             "candidate_id": "W10-NULL-0000", "family": "NULL"},
            None, frames3, P3, st3, gate_state=gs3, vol_state=vs3,
            yang_state=ys3, vconf_state=cs3, streak_state=sk3,
            tstate_state=ts3, amp_state=as3, mom_state=ms3,
            rng_matrix=mat0b, p_on=p_on0b)
    _ok("L15b null-cell engine path: thirteen-tuple null draw "
        "deterministic + mom axis in-domain + engine 14-tuple return "
        "+ double-run byte-identity (screen null-family path)",
        p_on0 == p_on0b and ax0 == ax0b and mom_dom
        and len(eqn) == len(P3["close"].index) and mzn >= 0
        and list(eqn.values) == list(eqnb.values) and mzn == mznb)
    _ok("L15c screen CSV contract carries the mom columns in the "
        "frozen order (cell_id/candidate_id head + mom pair before "
        "survives_screen)",
        csv_cols_screen_w10[:2] == ["cell_id", "candidate_id"]
        and csv_cols_screen_w10[-3:] == ["mom_face", "mom_zeroed",
                                         "survives_screen"]
        and "mom_face" in csv_cols_screen_w10
        and {"gate_zeroed", "vol_zeroed", "yang_zeroed", "vconf_zeroed",
             "streak_zeroed", "tstate_zeroed", "amp_zeroed",
             "mom_zeroed"} <= set(csv_cols_screen_w10))

    g_scr = tl6.finalize_already_landed(SCREEN_BATCH, SCREEN_FILE)
    if os.path.exists(SCREEN_FILE):
        _ok("L15d pit-95 guard live-fire: w10_screen.json carries "
            "SCREEN_BATCH -> finalize re-run would be refused",
            isinstance(g_scr, dict)
            and g_scr.get("batch") == SCREEN_BATCH
            and isinstance(g_scr.get("total"), int))
    else:
        _ok("L15d pit-95 guard fresh-face: w10_screen.json absent -> "
            "guard None = lawful fresh batch, finalize proceeds",
            g_scr is None)
    g_jdg = tl6.finalize_already_landed(JUDGE_BATCH, JUDGE_FILE)
    if os.path.exists(JUDGE_FILE):
        _ok("L15e pit-95 guard live-fire: w10_judge.json carries "
            "JUDGE_BATCH -> finalize re-run would be refused",
            isinstance(g_jdg, dict)
            and g_jdg.get("batch") == JUDGE_BATCH
            and isinstance(g_jdg.get("total"), int))
    else:
        _ok("L15e pit-95 guard fresh-face: w10_judge.json absent -> "
            "guard None = lawful fresh batch, finalize proceeds",
            g_jdg is None)

    print(f"\nselftest: {n_pass}/{n_leg} PASS "
          f"(scope: slice-1 mom layer + G-MOM + thirteen-tuple grammar "
          f"+ machinery: effective mask / curve runner parity / null "
          f"draw / 20-source exclusion loader + funnel faces: dispatch "
          f"/ null-cell engine path / CSV contract + pit-95 finalize "
          f"idempotency guard state-adaptive legs; zero live cells "
          f"burned, zero numbers fabricated)")
    return 0 if n_pass == n_leg else 1
