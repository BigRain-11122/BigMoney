# --- kit part B: resi/cnt full-face gates (probe anchors + 512-cell
# grid + extreme days + facts cross-check) + structure passes + the
# reform five-member EW ceiling baseline (spliced into the W14 runner) ---

def _resicnt_face_full():
    """Frozen sec.2 RESI/CNT-series face (r470/r471 probe basis): the
    git-tracked raw full-history member file data/daily/sh510300.csv
    (open + high + low + close + volume columns), truncated at the
    evidence cutoff.  (tl8._tstate_face_full loading caliber reused
    verbatim -- same member, same columns, same cutoff law;
    import-face law.)"""
    return tl8._tstate_face_full()


def _resicnt_nine_gate_cells(face_open, face_dec, close, o_, h_, l_, v_):
    """NINE-gate 512-cell cross on the r470/r471 probe basis VERBATIM
    (W13 G-SUMN grid caliber with the 9th gate swapped to the W14
    member face): gate x vol x yang x vconf x streak x tstate x amp x
    std20 x <face>; W13 basis faces exactly (calm/wild = the VOL-axis
    face: 20-bar return std vs its trailing 500-bar median; surge/dry
    = volume vs its 20-bar median; yang/red = close-vs-open; bull/bear
    = close-vs-MA200; up/down_streak = 2-day close-over-close with the
    shift(2) warmup judge; mad60/rsv60 = tstate faces; wide/narrow =
    amplitude vs its 20-bar median; std20 = the W11 STD20_q90 face);
    m9 = face-decidable & bull/calm notna & amp_known & judge &
    dec_mad & dec_rsv & dec_s20.  Returns (cells, m9_days)."""
    amp = (h_ - l_) / close
    med20amp = amp.rolling(20, min_periods=20).median()
    amp_known = med20amp.notna()
    wide_face = (amp > med20amp) & amp_known
    narrow_face = (amp <= med20amp) & amp_known
    up1 = close > close.shift(1)
    up2 = close.shift(1) > close.shift(2)
    dn1 = close < close.shift(1)
    dn2 = close.shift(1) < close.shift(2)
    judge = close.shift(2).notna()      # bars 0-1 warmup gate-closed
    up_st = judge & (up1 & up2).fillna(False)
    dn_st = judge & (dn1 & dn2).fillna(False)
    ma60 = close.rolling(60).mean()
    dist = close / ma60 - 1.0
    ts_q10 = dist.rolling(252, min_periods=120).quantile(0.10)
    mad_q10 = dist < ts_q10
    dec_mad = ts_q10.notna()
    hh60 = h_.rolling(60).max()
    ll60 = l_.rolling(60).min()
    rng60 = (hh60 - ll60).replace(0, np.nan)
    rsv60 = (close - ll60) / rng60
    rsv_low = rsv60 < 0.2
    dec_rsv = rsv60.notna()
    s20o, s20d, _s20meta, _s20, _s20q, _s10o, _s10d, _s10, _s10q = \
        _std_series_raw({RESI_MEMBER: pd.DataFrame(
            {"open": o_, "high": h_, "low": l_, "close": close,
             "volume": v_}, index=close.index)})
    dec_s20 = s20d
    std20_open = s20o
    ma200 = close.rolling(200).mean()
    bull = close > ma200
    bear = ~bull
    ret = close.pct_change()
    vol20 = ret.rolling(20, min_periods=20).std(ddof=1)
    med500 = vol20.rolling(500, min_periods=500).median()
    calm = vol20 <= med500
    wild = vol20 > med500
    med20v = v_.rolling(20, min_periods=20).median()
    surge = v_ > med20v
    yang = close > o_
    red = ~yang
    open_face = face_open & face_dec
    closed_face = (~face_open) & face_dec
    m9 = face_dec & bull.notna() & calm.notna() & amp_known & judge \
        & dec_mad & dec_rsv & dec_s20
    cells = {}
    for bname, b in (("bull", bull), ("bear", bear)):
        for vname, vv in (("calm", calm), ("wild", wild)):
            for yname, y in (("yang", yang), ("red", red)):
                for sname, s in (("surge", surge), ("dry", ~surge)):
                    for kname, k in (("up_streak", up_st),
                                     ("down_streak", dn_st)):
                        for tname, t in (("mad60", mad_q10),
                                         ("rsv60", rsv_low)):
                            for aname, aa in (("wide", wide_face),
                                              ("narrow", narrow_face)):
                                for sdname, sd in (
                                        ("std20_open", std20_open),
                                        ("std20_closed",
                                         (~std20_open) & dec_s20)):
                                    for fname, ff in (
                                            ("open", open_face),
                                            ("closed", closed_face)):
                                        cells[f"{bname}|{vname}|"
                                              f"{yname}|{sname}|"
                                              f"{kname}|{tname}|"
                                              f"{aname}|{sdname}|"
                                              f"{fname}"] = \
                                              int((m9 & b & vv & y
                                                 & s & k & t & aa
                                                 & sd & ff).sum())
    return cells, int(m9.sum())


def _grid_gate(cells, m9_days, a, face_label):
    """Shared 512-cell anchor assert (counts + min/max + all-decidable;
    W13 G-SUMN caliber).  Returns None or a one-line refusal."""
    empty = sorted(k for k, n_ in cells.items() if n_ <= 0)
    nonzero = [x for x in cells.values() if x > 0]
    if (len(cells) != 512
            or len(nonzero) != a["nine_gate_512cells_nonzero_count"]
            or len(empty) != a["nine_gate_512cells_empty_count"]
            or min(nonzero) < a["nine_gate_512cells_min_nonzero"]
            or max(cells.values()) > a["nine_gate_512cells_max"]
            or m9_days != a["nine_gate_all_decidable_days"]):
        return (f"{face_label} nine-gate 512-cell cross drift "
                f"(nonzero {len(nonzero)}/"
                f"{a['nine_gate_512cells_nonzero_count']}, empty "
                f"{len(empty)}/{a['nine_gate_512cells_empty_count']}, "
                f"min {min(nonzero)}, max {max(cells.values())}, "
                f"all-decidable {m9_days}/"
                f"{a['nine_gate_all_decidable_days']})")
    return None


def _facts_grid_crosscheck(facts_path, cells_key, cells, face_label):
    """Exact per-cell cross-check vs the git-tracked probe facts file
    (r470/r471 determinism cross-check law; skip-face = file absent,
    frozen header counts above still binding).  Returns None or a
    one-line refusal."""
    if not os.path.exists(facts_path):
        return None
    pf_ = json.load(open(facts_path, encoding="utf-8"))
    pcells = pf_.get(cells_key, {})
    drift = [f"{k}: {cells.get(k)} != {v_}"
             for k, v_ in pcells.items() if cells.get(k) != v_]
    if pcells and drift:
        return (f"{face_label} probe-facts per-cell cross-check drift: "
                f"{drift[:3]}")
    return None


def _extreme_day_checks(want_days, facts, close, face_map):
    """Extreme-day gate states exact (probe 7-day face; values at
    6-decimal rounding, open flags, slope sign).  face_map maps
    face name -> (open_series, dec_series, value_series).  Returns
    None or a one-line refusal."""
    for dstr, want in want_days.items():
        ts = pd.Timestamp(dstr)
        if ts not in close.index:
            return f"extreme day {dstr} absent from face"
        for fname, (open_s, dec_s, val_s) in face_map.items():
            if f"{fname}_open" not in want:
                continue
            if pd.isna(val_s.loc[ts]):
                return f"extreme day {dstr} {fname} value NaN"
            got_open = (bool(open_s.loc[ts])
                        if bool(dec_s.loc[ts]) else None)
            got_val = round(float(val_s.loc[ts]), 6)
            if (got_open != want[f"{fname}_open"]
                    or abs(got_val - want[f"{fname}_value"]) > 5.01e-6):
                return (f"extreme day {dstr} {fname} drift: open "
                        f"{got_open}/{want[fname + '_open']}, "
                        f"value {got_val}/{want[fname + '_value']}")
    return None


def _resi_state_full():
    """Canonical full-face resi_state with the frozen probe anchors
    asserted (prereg sec.2 G-RESI fail-closed): n_bars == 3,483;
    first-decidable == 120 / decidable == 3,363 / open == 390
    (11.20%); slope-sign split 352 up / 38 down (BETA20 same frozen
    runner); NINE-gate 512-cell grid 103 non-empty / 409 empty (max
    41; all-decidable 3,305) + exact per-cell cross-check vs the
    git-tracked r470 facts file when present; extreme-day gate
    states exact (probe 7-day face).  Returns (resi_state, err); err
    is a one-line honest refusal reason when not None."""
    face = _resicnt_face_full()
    if face is None:
        return None, (f"raw member face data/daily/sh{RESI_MEMBER}.csv "
                      f"absent/open-high-low-close-volume columns "
                      f"missing or truncated tail != cutoff {CUTOFF}")
    open_r, dec_r, meta, _od, _dd, _on, _dn, _cm, resi60, _c5, _n20, \
        beta20 = _resicnt_faces_raw(face)
    a = RESI_ANCHOR
    if (meta.get("n_bars") != a["n_bars"]
            or meta["first_decidable_bar_idx"]
            != a["first_decidable_bar_idx"]
            or meta["decidable_days"] != a["decidable_days"]
            or meta["open_days"] != a["open_days"]
            or meta["closed_days"] != a["closed_days"]
            or meta["open_rate_on_decidable"]
            != a["open_rate_on_decidable"]):
        return None, (f"G-RESI core anchors {meta} != probe "
                      f"{{n 3483, warmup 120, decidable 3363, open "
                      f"390 (11.20%)}}")
    # slope-sign split (disclosure face; direction conditioning lives
    # in burned axes; NOT a gate input -- asserted as frozen probe
    # fact)
    m_open = open_r & dec_r & beta20.notna()
    up_days = int((m_open & (beta20 > 0)).sum())
    dn_days = int((m_open & (beta20 <= 0)).sum())
    if (up_days != a["slope_sign_split"]["up_slope_days"]
            or dn_days != a["slope_sign_split"]["down_slope_days"]):
        return None, (f"G-RESI slope-sign split drift {up_days}/"
                      f"{dn_days} != probe "
                      f"{a['slope_sign_split']['up_slope_days']}/"
                      f"{a['slope_sign_split']['down_slope_days']}")
    # NINE-gate 512-cell grid + facts cross-check
    df = face[RESI_MEMBER]
    close = df["close"].astype(float).sort_index()
    o_ = df["open"].astype(float).reindex(close.index)
    h_ = df["high"].astype(float).reindex(close.index)
    l_ = df["low"].astype(float).reindex(close.index)
    v_ = df["volume"].astype(float).reindex(close.index)
    cells, m9_days = _resicnt_nine_gate_cells(open_r, dec_r, close,
                                              o_, h_, l_, v_)
    err = _grid_gate(cells, m9_days, a, "G-RESI")
    if err:
        return None, f"G-RESI {err}"
    err = _facts_grid_crosscheck(RESI_PROBE_FACTS,
                                 "resi60_nine_gate_cells", cells,
                                 "G-RESI")
    if err:
        return None, f"G-RESI {err}"
    # extreme-day gate states (frozen probe face)
    if os.path.exists(RESI_PROBE_FACTS):
        pf_ = json.load(open(RESI_PROBE_FACTS, encoding="utf-8"))
        want_days = pf_.get("extreme_day_states", {})
        beta_up = beta20 > 0
        err = _extreme_day_checks(want_days, pf_, close,
                                  {"resi60": (open_r, dec_r, resi60)})
        if err:
            return None, f"G-RESI {err}"
        # slope_sign + std20_open + rsqr20_open cross-reads
        s20o, s20d, _m20, _s20, _q20, _s10o, _s10d, _s10, _q10 = \
            _std_series_raw({RESI_MEMBER: pd.DataFrame(
                {"open": o_, "high": h_, "low": l_, "close": close,
                 "volume": v_}, index=close.index)})
        r20o, r20d, _r20meta = _rsqr_faces_raw(face)[0], \
            _rsqr_faces_raw(face)[1], _rsqr_faces_raw(face)[2]
        for dstr, want in want_days.items():
            ts = pd.Timestamp(dstr)
            if pd.isna(beta20.loc[ts]):
                continue
            got_slope = "up" if bool(beta_up.loc[ts]) else "down"
            if got_slope != want.get("slope_sign"):
                return None, (f"G-RESI extreme day {dstr} slope drift "
                              f"{got_slope}/{want.get('slope_sign')}")
            got_std = (bool(s20o.loc[ts])
                       if bool(s20d.loc[ts]) else None)
            if got_std != want.get("std20_open"):
                return None, (f"G-RESI extreme day {dstr} std20 drift "
                              f"{got_std}/{want.get('std20_open')}")
            got_rsqr = (bool(r20o.loc[ts])
                        if bool(r20d.loc[ts]) else None)
            if got_rsqr != want.get("rsqr20_open"):
                return None, (f"G-RESI extreme day {dstr} rsqr drift "
                              f"{got_rsqr}/{want.get('rsqr20_open')}")
    meta = dict(meta)
    meta["slope_sign_split"] = {"up_slope_days": up_days,
                                "down_slope_days": dn_days}
    meta["nine_gate_512cells"] = cells
    meta["nine_gate_all_decidable_days"] = m9_days
    return (open_r, dec_r, meta), None


def _cnt_state_full():
    """Canonical full-face cnt_state with the frozen probe anchors
    asserted (prereg sec.2 G-CNT fail-closed): n_bars == 3,483;
    cntd5 first-decidable == 119 / decidable == 3,364 / open == 137
    (3.93% thin-tail honest note); cntn20 first-decidable == 119 /
    decidable == 3,364 / open == 265 (7.61%); cntd5 slope split 97/40;
    NINE-gate 512-cell grids: cntd5 109/403, cntn20 103/409 (max 41;
    all-decidable 3,305 both) + exact per-cell cross-checks vs the
    git-tracked r470/r471 facts files when present; extreme-day gate
    states exact (probe 7-day face).  Returns (cnt_state, err)."""
    face = _resicnt_face_full()
    if face is None:
        return None, (f"raw member face data/daily/sh{CNT_MEMBER}.csv "
                      f"absent/open-high-low-close-volume columns "
                      f"missing or truncated tail != cutoff {CUTOFF}")
    open_d, dec_d, open_n, dec_n, meta = cnt_state_series(face)
    a = CNT_ANCHOR
    for sub, okey, dkey in (("cntd5", open_d, dec_d),
                            ("cntn20", open_n, dec_n)):
        s = a[sub]
        dec_n_ = int(dkey.sum())
        open_n_ = int((okey & dkey).sum())
        rate = meta[f"{sub}_open_rate_on_decidable"]
        if (meta[f"{sub}_first_decidable_bar_idx"]
                != s["first_decidable_bar_idx"]
                or dec_n_ != s["decidable_days"]
                or open_n_ != s["open_days"]
                or rate != s["open_rate_on_decidable"]):
            return None, (f"G-CNT {sub} core anchors drift "
                          f"(first-dec "
                          f"{meta[sub + '_first_decidable_bar_idx']}, "
                          f"decidable {dec_n_}, open {open_n_}, rate "
                          f"{rate}) != probe {{first-dec "
                          f"{s['first_decidable_bar_idx']}, decidable "
                          f"{s['decidable_days']}, open "
                          f"{s['open_days']}, rate "
                          f"{s['open_rate_on_decidable']}}}")
    # cntd5 slope-sign split (frozen probe fact)
    _o, _d, _m, _od, _dd, _on, _dn, _cm, _r60, c5, _n20, beta20 = \
        _resicnt_faces_raw(face)
    m_open = open_d & dec_d & beta20.notna()
    up_days = int((m_open & (beta20 > 0)).sum())
    dn_days = int((m_open & (beta20 <= 0)).sum())
    sa = a["cntd5"]["slope_sign_split"]
    if (up_days != sa["up_slope_days"] or dn_days != sa["down_slope_days"]):
        return None, (f"G-CNT cntd5 slope-sign split drift {up_days}/"
                      f"{dn_days} != probe {sa['up_slope_days']}/"
                      f"{sa['down_slope_days']}")
    df = face[CNT_MEMBER]
    close = df["close"].astype(float).sort_index()
    o_ = df["open"].astype(float).reindex(close.index)
    h_ = df["high"].astype(float).reindex(close.index)
    l_ = df["low"].astype(float).reindex(close.index)
    v_ = df["volume"].astype(float).reindex(close.index)
    for sub, okey, dkey in (("cntd5", open_d, dec_d),
                            ("cntn20", open_n, dec_n)):
        cells, m9_days = _resicnt_nine_gate_cells(okey, dkey, close,
                                                  o_, h_, l_, v_)
        err = _grid_gate(cells, m9_days, a[sub], f"G-CNT {sub}")
        if err:
            return None, f"G-CNT {err}"
        fpath = (CNT_PROBE_FACTS_R470 if sub == "cntd5"
                 else CNT_PROBE_FACTS_R471)
        ckey = f"{sub}_nine_gate_cells"
        err = _facts_grid_crosscheck(fpath, ckey, cells, f"G-CNT {sub}")
        if err:
            return None, f"G-CNT {err}"
    # extreme-day gate states (frozen probe face; r470 carries the
    # cntd5 values, r471 the cntn20 values)
    if os.path.exists(CNT_PROBE_FACTS_R470):
        pf_ = json.load(open(CNT_PROBE_FACTS_R470, encoding="utf-8"))
        want_days = pf_.get("extreme_day_states", {})
        err = _extreme_day_checks(want_days, pf_, close,
                                  {"cntd5": (open_d, dec_d, c5)})
        if err:
            return None, f"G-CNT {err}"
    if os.path.exists(CNT_PROBE_FACTS_R471):
        pf2 = json.load(open(CNT_PROBE_FACTS_R471, encoding="utf-8"))
        want_days = pf2.get("extreme_day_states", {})
        err = _extreme_day_checks(want_days, pf2, close,
                                  {"cntn20": (open_n, dec_n, _n20)})
        if err:
            return None, f"G-CNT {err}"
    meta = dict(meta)
    meta["cntd5_slope_sign_split"] = {"up_slope_days": up_days,
                                      "down_slope_days": dn_days}
    return (open_d, dec_d, open_n, dec_n, meta), None


def _resi_structure_pass(resi_meta) -> bool:
    """Series-structure invariants on every panel face (fail-closed):
    120-bar warmup -- first-decidable + decidable partitions n_bars;
    open <= decidable and closed <= decidable.  A face shorter than
    the warmup (first-decidable None) honestly refuses."""
    if not isinstance(resi_meta, dict):
        return False
    n = resi_meta.get("n_bars", -1)
    fv = resi_meta.get("first_decidable_bar_idx")
    return (fv is not None
            and fv + resi_meta.get("decidable_days", -10**9) == n
            and resi_meta.get("open_days", -1)
            <= resi_meta.get("decidable_days", -1)
            and resi_meta.get("closed_days", -1)
            <= resi_meta.get("decidable_days", -1))


def _cnt_structure_pass(cnt_meta) -> bool:
    """Series-structure invariants on BOTH cnt sub-faces (fail-closed;
    same law as _resi_structure_pass, applied per sub-face with the
    119 one-bar construction-family difference)."""
    if not isinstance(cnt_meta, dict):
        return False
    for sub in ("cntd5", "cntn20"):
        n = cnt_meta.get("n_bars", -1)
        fv = cnt_meta.get(f"{sub}_first_decidable_bar_idx")
        dec = cnt_meta.get(f"{sub}_decidable_days", -10**9)
        op = cnt_meta.get(f"{sub}_open_days", -1)
        if fv is None or fv + dec != n or op > dec:
            return False
    return True


# reform return-ceiling baseline (prereg sec.4; REFORM_CEILING_BASELINE
# = five_member_ew_O1555, reform canon r271 ratification)
O1555_UNIVERSE = ("510300", "510050", "510500", "512100", "588000")


def _five_member_ew_baseline_annualized(leg_idx):
    """Equal-weight daily returns of the O-1555 frozen five-member
    universe over the SAME evaluation window as the candidates' leg-L
    curves (members without data on a day are excluded that day --
    deterministic, batch-independent passive face); annualized with
    the descriptive-face _ann formula (compound, 252/n scaling).
    Returns None on any member file absent/short (honest refuse ->
    return_ceiling_O1126 material missing -> missing-dims refuse,
    never zero-filled)."""
    closes = {}
    for s in O1555_UNIVERSE:
        path = os.path.join("data", "daily", f"sh{s}.csv")
        if not os.path.exists(path):
            return None
        df = pd.read_csv(path)
        df["date"] = df["date"].astype(str)
        df = df[df["date"] <= CUTOFF]
        if len(df) < 2:
            return None
        closes[s] = pd.Series(df["close"].astype(float).to_numpy(),
                              index=pd.to_datetime(df["date"]))
    m = pd.DataFrame(closes)              # columns = members
    daily = m.pct_change()                # member daily returns
    ew = daily.mean(axis=1, skipna=True)   # equal weight across the
    # members with data that day
    ew_win = ew.reindex(leg_idx)
    if ew_win.notna().sum() < 2:
        return None
    total = float((1.0 + ew_win.fillna(0.0)).prod())
    n = int(len(ew_win))
    if total <= 0 or n < 2:
        return None
    return float(total ** (252.0 / n) - 1.0)
