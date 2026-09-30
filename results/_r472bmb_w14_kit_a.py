# --- kit part A: sumn import-face + resi/cnt axes + specs + anchors +
# faces computation + zero masks (spliced into the W14 runner) ---

# up-share-purity SUMN axis (W13 frozen face, imported verbatim from
# tl13 -- import-face law; the W14 runner re-derives ZERO sumn machinery)
AXIS_SUMN = tl13.AXIS_SUMN               # ["none","sumn20_lo","sumn10_lo"]
SUMN_MEMBER = tl13.SUMN_MEMBER          # "510300"
sumn_state_series = tl13.sumn_state_series
sumn_zero_mask = tl13.sumn_zero_mask
_sumn_state_full = tl13._sumn_state_full
_sumn_structure_pass = tl13._sumn_structure_pass
_sumn_faces_raw = tl13._sumn_faces_raw
# SUMN_SPEC/SUMN_ANCHOR carried from tl13.build_grammar_w13() inside
# build_grammar_w14 (import-time grammar-chain build is heavy; lazy
# face = build-time read)

# trend-extension-position RESI axis (prereg sec.3 NEW W14 frozen
# layer, TWO-value adjudicated member axis; resi30 GATE-RECHECK FAIL
# demoted -- member-set adjudication banner; W4-VOL/W11-STD/W12-RSQR/
# W13-SUMN axis-family precedent)
AXIS_RESI = ["none", "resi60_hi"]
RESI_MEMBER = "510300"          # core48 member (prereg sec.2 probe fact)
RESI_PROBE_FACTS = os.path.join(
    "results", "_r470bmb_vsumd_resi_w14_probe_facts.json")
RESI_SPEC = {
 "member": "510300",
 "series": "r470 probe verbatim / A158-TSGATE-P1 frozen RESI construction via the frozen in-repo runner import (zero-invention law; scripts/a158_tsgate_probe.py alpha158_factors): signal-day-d close info set on the member face",
 "resi60": "F[\"RESI60\"] = rolling-OLS(close, 60) end-point residual / close (closed-form cumsum, O(n); qlib expanding min_periods=1 warmup; RESI[0] NaN -- expanding k=1 Stt=0 guard)",
 "q90_ref": "q90_ref = resi60.rolling(GATE_WIN=252, min_periods=GATE_MINP=120).quantile(QHIGH=0.90) (own-trailing 252-observation top-decile reference; GATE_WIN/GATE_MINP/QHIGH constants same-source frozen-runner import)",
 "resi60_hi": "resi60 > q90_ref (price stretched ABOVE its own 60-bar trend into the trailing top decile = trend-extension position state; direction-agnostic POSITION face -- high residual = above-trend stretch, readout sign carried by BETA20 slope split 352 up / 38 down; A158-TSGATE-P1 RESI60_q90 OOS med_t 1.178 + GATE-RECHECK CONFIRM +0.005699 = LONG anchor)",
 "none": "no gate (W13 semantic baseline face)",
 "position_not_fit": "RESI high-extension days 96% above the fit-difference trend axis (W12 RSQR judg-negative axis does NOT swallow the RESI face: extension POSITION != regression fit QUALITY; prereg sec.1 D6 (a))",
 "demoted": "resi30_hi GATE-RECHECK FAIL (face_a med_net -0.006028 SIGN FLIP vs P1 OOS 0.433; c1 downgrade list) -- demoted from the member set; increment face 219 days (61% open-day) disclosed non-collapsed but increment existence != recheck pass (two judgments do not conflict)",
 "info_set": "signal-day d close; entry fills d+1 open (T+1 causal, same info set as GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR/SUMN, zero lookahead)",
 "warmup": "120-bar warmup window gate-closed honest (q90_ref min_periods 120 -> first decidable bar-idx == 120, fail-closed assertion == RSQR/STD/SUMN family warmup)",
 "engine_note": "entry-permittance only (effective signal zeroed, MSG-0440 E1-mapping primitive; exit logic zero change; engine/exit_rules.py zero touch)",
 "nan_artifact_note": "NaN comparisons (f > q90_ref) yield False NOT decidable (pit-95 batch-95 law; the decidable face derives from the underlying values notna; the naive comparison bool face masquerades warmup bars as resi-closed -- BANNED at the mask level)",
 "adjacency_note": "nearest burned neighbor: W12 RSQR (fit quality, sign-blind) -- resi60^rsqr20_closed dominant (RESI high-extension days 96% fall above the fit-difference trend = two gates read DIFFERENT states); W10 MOM zero co-open (390/0) + cntn20^mom_closed 265 days (position != oversold rebound); W8 RSV60 zero co-open (trend extension != range oversold); prereg sec.1 D6 (a)/(d)/(e)",
 "composition_order": "signal -> filter -> timing -> GATE -> VOL -> YANG -> VCONF -> STREAK -> TSTATE -> AMP -> MOM -> STD -> RSQR -> SUMN -> RESI -> initial-stop (W13 order extended; prereg sec.3 eighteen-tuple)"
}

RESI_ANCHOR = {
 "n_bars": 3483,
 "first_date": "2012-05-28",
 "cutoff": "2026-09-22",
 "warmup_gate_closed_bars": 120,
 "first_decidable_bar_idx": 120,
 "decidable_days": 3363,
 "open_days": 390,
 "closed_days": 2973,
 "open_rate_on_decidable": 0.112,
 "slope_sign_split": {
  "up_slope_days": 352,
  "down_slope_days": 38,
  "note": "BETA20 sign from the same frozen runner; resi60 is sign-aware by construction (high residual = above-trend stretch); direction conditioning lives in burned axes (GATE/YANG/STREAK/MOM), redundancy measured in adjacency cells"
 },
 "nine_gate_all_decidable_days": 3305,
 "nine_gate_512cells_nonzero_count": 103,
 "nine_gate_512cells_empty_count": 409,
 "nine_gate_512cells_min_nonzero": 1,
 "nine_gate_512cells_max": 41,
 "core48_note": "48/48 members non-degenerate (prereg sec.2 core48 face; probe r470)"
}

# yang-day-density CNT axis (prereg sec.3 NEW W14 frozen layer,
# THREE-value adjudicated member axis = density + frequency dual
# carrier; cntd10 GATE-RECHECK FAIL demoted, CNTD20 ABSENT below
# threshold/cluster-disambiguation -- member-set adjudication banner)
AXIS_CNT = ["none", "cntd5_hi", "cntn20_lo"]
CNT_MEMBER = "510300"          # core48 member (prereg sec.2 probe fact)
CNT_PROBE_FACTS_R470 = os.path.join(
    "results", "_r470bmb_vsumd_resi_w14_probe_facts.json")
CNT_PROBE_FACTS_R471 = os.path.join(
    "results", "_r471bmb_cntn20_w14_supplement_facts.json")
CNT_SPEC = {
 "member": "510300",
 "series": "r470/r471 probe verbatim / A158-TSGATE-P1 frozen CNT construction via the frozen in-repo runner import (zero-invention law; scripts/a158_tsgate_probe.py alpha158_factors): signal-day-d close info set on the member face",
 "cntd5": "F[\"CNTD5\"] = F[\"CNTP5\"] - F[\"CNTN5\"] = mean(up-day, 5) - mean(down-day, 5) (yang-day NET-DOMINANCE density in [-1,1])",
 "cntn20": "F[\"CNTN20\"] = mean(down-day, 20) (down-day FREQUENCY share in [0,1] -- non-purity face: low value = FEW down days without any price-magnitude claim; r471 supplement distinct-space face)",
 "cntd5_hi": "cntd5 > rolling(GATE_WIN=252, min_periods=GATE_MINP=120).quantile(QHIGH=0.90) (net up-day dominance entering its own top decile; A158-TSGATE-P1 CNTD5_q90 OOS 0.815 + GATE-RECHECK CONFIRM +0.009845 = LONG anchor)",
 "cntn20_lo": "cntn20 < rolling(GATE_WIN=252, min_periods=GATE_MINP=120).quantile(QLOW=0.10) (down-day frequency entering its own bottom decile; A158-TSGATE-P1 CNTN20_q10 OOS 0.617 + GATE-RECHECK CONFIRM +0.007839 [+0.016584 r471 recheck supplement same direction] = LONG anchor)",
 "none": "no gate (W13 semantic baseline face)",
 "density_vs_frequency": "cntd5 (density) and cntn20 (frequency) are TWO orthogonal readings of the same up/down-day stream: cntd5^cntn20 both-open 44 / cntn20-only 221 days (r471 distinct_space_increment face; frequency-without-purity = few-down-day grind increment face vs prereg sec.1 D6 (b) SUMN purity axis: cntn20^sumn20_closed 69 + cntd5^sumn20_closed 44 days)",
 "demoted": "cntd10_hi GATE-RECHECK FAIL (c1 downgrade list) -- demoted from the member set; increment face 161 days (70% open-day) disclosed non-collapsed; CNTD20_q90 ABSENT below threshold/cluster-disambiguation (twin-window construction with cntn20 disclosed NOT taken)",
 "mirror_twin": "CNTD_q90 vs CNTN_q10 construction mirrors (r277 XOR measured: cntd10/cntn10 19 days, cntd5/cntn5 20 days; quantile reference-window contamination dominant 18/19-18/20 current-window zero-change) -- mirror NEAR-SAME not identity; dedup gate T-84s3 cell-key face carries the distinction",
 "info_set": "signal-day d close; entry fills d+1 open (T+1 causal, same info set as GATE/VOL/YANG/VCONF/STREAK/TSTATE/AMP/MOM/STD/RSQR/SUMN/RESI, zero lookahead)",
 "warmup": "119-bar first-decidable HONEST one-bar construction-family difference (idx-0 up/down-day indicator = comparison-vs-NaN -> False -> 0.0 NOT NaN -> qref valid one bar early; NOT the RSQR/STD/SUMN 120 face; probe assert anchors per-face; prereg sec.2 warmup fail-closed measured note)",
 "engine_note": "entry-permittance only (effective signal zeroed, MSG-0440 E1-mapping primitive; exit logic zero change; engine/exit_rules.py zero touch)",
 "nan_artifact_note": "NaN comparisons yield False NOT decidable (pit-95 batch-95 law; the decidable face derives from the underlying values notna; the naive comparison bool face masquerades warmup bars as cnt-closed -- BANNED at the mask level)",
 "adjacency_note": "W7 STREAK: cntd5^upstreak_closed 147 days (density has NO 2-day streak requirement); W13 SUMN: cntn20^sumn20_closed 69 + cntd5^sumn20_closed 44 (frequency without magnitude purity); W10 MOM: cntn20^mom_closed 265; prereg sec.1 D6 (b)/(c)/(d)",
 "composition_order": "signal -> filter -> timing -> GATE -> VOL -> YANG -> VCONF -> STREAK -> TSTATE -> AMP -> MOM -> STD -> RSQR -> SUMN -> RESI -> CNT -> initial-stop (W13 order extended; prereg sec.3 eighteen-tuple)"
}

CNT_ANCHOR = {
 "n_bars": 3483,
 "first_date": "2012-05-28",
 "cutoff": "2026-09-22",
 "cntd5": {
  "first_decidable_bar_idx": 119,
  "decidable_days": 3364,
  "open_days": 137,
  "closed_days": 3227,
  "open_rate_on_decidable": 0.0393,
  "thin_tail_note": "3.93% thin-tail axis honest note (prereg sec.2; insufficient-sample clause likely on thin-tail grids = honest expectation, NOT a defect)",
  "slope_sign_split": {"up_slope_days": 97, "down_slope_days": 40},
  "nine_gate_512cells_nonzero_count": 109,
  "nine_gate_512cells_empty_count": 403,
  "nine_gate_512cells_min_nonzero": 1,
  "nine_gate_512cells_max": 41,
  "nine_gate_all_decidable_days": 3305,
  "core48_open_rate": {"min": 0.0196, "median": 0.0411, "max": 0.065}
 },
 "cntn20": {
  "first_decidable_bar_idx": 119,
  "decidable_days": 3364,
  "open_days": 265,
  "closed_days": 3099,
  "open_rate_on_decidable": 0.0761,
  "nine_gate_512cells_nonzero_count": 103,
  "nine_gate_512cells_empty_count": 409,
  "nine_gate_512cells_min_nonzero": 1,
  "nine_gate_512cells_max": 41,
  "nine_gate_all_decidable_days": 3305,
  "core48_open_rate": {"min": 0.0276, "median": 0.065, "max": 0.0865}
 }
}

AXIS_COMBOS = tl13.AXIS_COMBOS * len(AXIS_RESI) * len(AXIS_CNT)
# 282,175,488 x 2 x 3 = 1,693,052,928 (prereg sec.3 eighteen-tuple)


def _resicnt_faces_raw(prices: dict):
    """r470/r471-probe-verbatim RESI/CNT face computation (single
    computation site for all three member faces + decidables + raw
    values + slope sign; A158-TSGATE-P1 frozen construction via the
    FROZEN in-repo runner import -- zero-invention law):
    F = a158.alpha158_factors(member frame); resi60 = F["RESI60"]
    (rolling-OLS(close,60) end-point residual/close, expanding
    warmup); cntd5 = F["CNTD5"] (up-day minus down-day 5-bar mean);
    cntn20 = F["CNTN20"] (down-day 20-bar mean share).
    resi60_hi: q90_ref rolling(252,min_periods=120).quantile(QHIGH);
    open = (f > q90_ref); cntd5_hi same high-side law; cntn20_lo:
    q10_ref ...quantile(QLOW); open = (f < q10_ref).  decidable
    derives from the underlying values notna (pit-95 batch-95 law).
    Returns (resi_open, resi_dec, resi_meta, cntd_open, cntd_dec,
    cntn_open, cntn_dec, cnt_meta, resi60, cntd5, cntn20, beta20);
    deterministic pure function of the (cutoff-truncated) panel."""
    df = prices[RESI_MEMBER].sort_index()
    # .to_numpy() first: dict-of-Series construction ALIGNs to a
    # given index -> all-NaN reindex artifact (r447 probe live pit)
    di = pd.DataFrame({"open": df["open"].astype(float).to_numpy(),
                       "high": df["high"].astype(float).to_numpy(),
                       "low": df["low"].astype(float).to_numpy(),
                       "close": df["close"].astype(float).to_numpy(),
                       "volume": df["volume"].astype(float)
                       .to_numpy()},
                      index=df.index)
    F = a158.alpha158_factors(di)
    resi60, cntd5, cntn20, beta20 = (F["RESI60"], F["CNTD5"],
                                     F["CNTN20"], F["BETA20"])
    q90_r = resi60.rolling(a158.GATE_WIN,
                           min_periods=a158.GATE_MINP).quantile(a158.QHIGH)
    dec_r = resi60.notna() & q90_r.notna()   # underlying notna (pit-95)
    open_r = (resi60 > q90_r)                # comparison face: NaN->False
    q90_d = cntd5.rolling(a158.GATE_WIN,
                          min_periods=a158.GATE_MINP).quantile(a158.QHIGH)
    dec_d = cntd5.notna() & q90_d.notna()
    open_d = (cntd5 > q90_d)
    q10_n = cntn20.rolling(a158.GATE_WIN,
                           min_periods=a158.GATE_MINP).quantile(a158.QLOW)
    dec_n = cntn20.notna() & q10_n.notna()
    open_n = (cntn20 < q10_n)
    n = len(resi60)

    def _first_true(s):
        arr = s.fillna(False).astype(bool).values
        nz = np.flatnonzero(arr)
        return int(nz[0]) if len(nz) else None

    resi_meta = {"n_bars": int(n),
                 "warmup_gate_closed_bars": 120,
                 "first_decidable_bar_idx": _first_true(dec_r),
                 "decidable_days": int(dec_r.sum()),
                 "open_days": int((open_r & dec_r).sum()),
                 "closed_days": int(((~open_r) & dec_r).sum()),
                 "open_rate_on_decidable":
                 (round(float((open_r & dec_r).sum() / dec_r.sum()), 4)
                  if int(dec_r.sum()) else None),
                 "na_window_bars": 120}
    cnt_meta = {"n_bars": int(n),
                "cntd5_first_decidable_bar_idx": _first_true(dec_d),
                "cntd5_decidable_days": int(dec_d.sum()),
                "cntd5_open_days": int((open_d & dec_d).sum()),
                "cntd5_open_rate_on_decidable":
                (round(float((open_d & dec_d).sum() / dec_d.sum()), 4)
                 if int(dec_d.sum()) else None),
                "cntn20_first_decidable_bar_idx": _first_true(dec_n),
                "cntn20_decidable_days": int(dec_n.sum()),
                "cntn20_open_days": int((open_n & dec_n).sum()),
                "cntn20_open_rate_on_decidable":
                (round(float((open_n & dec_n).sum() / dec_n.sum()), 4)
                 if int(dec_n.sum()) else None),
                "na_window_bars": 120,
                "warmup_family_note":
                "119 first-decidable one-bar construction-family "
                "difference (idx-0 comparison-vs-NaN -> False -> 0.0 "
                "non-NaN; honest, probe-anchored per-face)"}
    return (open_r, dec_r, resi_meta, open_d, dec_d, open_n, dec_n,
            cnt_meta, resi60, cntd5, cntn20, beta20)


def resi_state_series(prices: dict):
    """Frozen RESI spec (prereg sec.2/3): member 510300 signal-day
    info set -- resi60_hi open perm + decidable face.  Returns
    (open, dec, meta): boolean Series on the member's own date
    index + structural meta.  Deterministic pure function of the
    (cutoff-truncated) panel."""
    o, d, m, _od, _dd, _on, _dn, _cm, _r, _c, _n, _b = \
        _resicnt_faces_raw(prices)
    return o, d, m


def cnt_state_series(prices: dict):
    """Frozen CNT spec (prereg sec.2/3): member 510300 signal-day
    info set -- cntd5_hi + cntn20_lo open perms + decidables.
    Returns (open_d5, dec_d5, open_n20, dec_n20, meta).
    Deterministic pure function of the (cutoff-truncated) panel."""
    _o, _d, _m, od, dd, on, dn, cm, _r, _c, _n, _b = \
        _resicnt_faces_raw(prices)
    return od, dd, on, dn, cm


def resi_zero_mask(mask: pd.DataFrame, resi_key: str, resi_state):
    """Grammar-layer resi entry gate (prereg sec.3 trend-extension
    position face; E1-mapping primitive): off-face signal days ->
    effective signal zeroed (entry blocked; engine-native signal-off
    exit semantics; zero engine touch).  resi=none = W13 semantic
    baseline (identity).  The keep face derives from the DECIDABLE
    face (pit-95 law): resi60_hi keeps resi60-open AND decidable --
    the naive comparison bool face alone would masquerade warmup bars
    as resi-closed (BANNED).  Member dates missing from the mask
    index -> resi-closed (conservative reindex law,
    tl3..tl13 gate caliber)."""
    if resi_key == "none":
        return mask
    open_r, dec_r, _meta = resi_state
    if resi_key == "resi60_hi":
        keep = (open_r.reindex(mask.index).fillna(False).astype(int)
                & dec_r.reindex(mask.index).fillna(False).astype(int))
    else:
        raise ValueError(f"unknown resi_key {resi_key}")
    return mask.mul(keep, axis=0)


def cnt_zero_mask(mask: pd.DataFrame, cnt_key: str, cnt_state):
    """Grammar-layer cnt entry gate (prereg sec.3 yang-day density +
    down-day frequency dual face; E1-mapping primitive): off-face
    signal days -> effective signal zeroed.  cnt=none = W13 semantic
    baseline (identity).  Keep faces derive from the DECIDABLE faces
    (pit-95 law): cntd5_hi keeps cntd5-open AND decidable; cntn20_lo
    keeps cntn20-open AND decidable.  Member dates missing from the
    mask index -> cnt-closed (conservative reindex law)."""
    if cnt_key == "none":
        return mask
    open_d, dec_d, open_n, dec_n, _meta = cnt_state
    if cnt_key == "cntd5_hi":
        keep = (open_d.reindex(mask.index).fillna(False).astype(int)
                & dec_d.reindex(mask.index).fillna(False).astype(int))
    elif cnt_key == "cntn20_lo":
        keep = (open_n.reindex(mask.index).fillna(False).astype(int)
                & dec_n.reindex(mask.index).fillna(False).astype(int))
    else:
        raise ValueError(f"unknown cnt_key {cnt_key}")
    return mask.mul(keep, axis=0)
