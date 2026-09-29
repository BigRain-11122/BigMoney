# -*- coding: utf-8 -*-
"""r438 bm-b step C+D: W10 module docstring + overlay-layer transplant
(replace the W9-inherited amp function defs with tl9 import aliases +
NEW mom overlay functions; single script, idempotent by refusal)."""
import sys

T = "scripts/trial_labor_w10.py"
txt = open(T, encoding="utf-8").read()

DOC = '''"""TRIAL_LABOR_W10 runner -- T-122 mass-candidate trial wave-10
(5000-ceiling, momentum-confirmation MOM-gate THIRTEEN-gate wave).

Prereg FROZEN (bm-b r437 adopting-machine same-round freeze per the
candidate's own 10-item adopter checklist; freeze trigger MET live =
W9 full chain landed 2026-09-29 17:47:46 {w9_judge.json 243/243
judged zero G1 zero G2 + w9_intake lawful-zero + CEO-REPORT-WAVE9 +
attrition two rows + TRIAL_GRAMMAR_LEDGER wave-9 row + W9 prereg sec.7/
sec.8 backfilled} + ledger head 344,031 linear live-read {head file=
w9_judge.json} + zero in-flight judge faces [pool entries 120/120
done]):
research/TRIAL_LABOR_W10_PREREG.md -- generate grammar + funnel rules +
judgment lines all frozen; post-run only sec.7/8 backfill.  Seeds held
at the freeze commit per R250 one-step law: trial_labor_w10_gen=
20311000 / trial_labor_w10_scrnull=20311500 / trial_labor_w10_unc=
20312000 (berth-open adoption of the bm-c r228 MOM candidate whole
package per AMP->W9 precedent; freeze-time three-step re-verify ALL
GREEN, no re-pick).

Import-face law (prereg sec.6): the FULL trial_labor_w1-w9 chain is
imported (tl1 enumeration/loading/anchor/envelope primitives + tl2
initial-stop overlay + tl3 regime-gate overlay + tl4 vol overlay +
tl5 yang overlay + tl6 vconf overlay + tl7 streak overlay + tl8
tstate overlay & eleven-tuple machinery + tl9 amp overlay & twelve-
tuple machinery); Sobol sample_draws pattern follows mass_trial_w1
(paradigm import); strategies/ factory + engine/backtester imported,
never rewritten; engine/exit_rules.py ZERO touch (mom overlay is a
GRAMMAR layer).

Engineering mapping disclosures (pre-run, zero cells burned):

  MOM overlay (prereg sec.2/sec.3 NEW W10 frozen layer; r228 probe
  verbatim, zero-invention law; census family O-1855(4) ROC20_q10 =
  structural transplant of the in-repo census-verbatim MAD60_q10
  decile mechanics frozen in W8 prereg sec.2 / r431): member 510300
  signal-day-d close info set.  roc20(d) = close(d)/close(d-20) - 1;
  q10_ref = roc20.rolling(252, min_periods=120).quantile(0.10);
  mom_oversold = roc20 < q10_ref (20-day descent-speed entering its
  own bottom decile = oversold momentum state).  139-bar warmup
  window gate-closed honest (roc20 first valid bar-idx == 20; q10_ref
  min_periods 120 -> first decidable bar-idx == 139; spectrum vs YANG
  0 / STREAK 2 / VCONF 19 / AMP 19 / RSV 59 / MAD60 178 / VOL 519).
  Gate acts on ENTRY PERMITTANCE only (effective signal zeroed,
  MSG-0440 E1-mapping primitive; exit logic zero change).  MOM face
  = speed confirmation != TSTATE position face != STREAK direction
  face != AMP amplitude face (r228 probe: mad60-open days 66.06%
  co-open / rsv60-open 35.16%; 253 both-open / 121 mom-unique days =
  non-isomorphic increment space -- the wave's true question; bear
  15.49% vs bull 7.58% / wild 19.43% vs calm 3.74% / down_streak
  17.82% vs up_streak 7.38% deep-refinement loading honest, NOT an
  independent-dimension claim).  NaN comparison artifact law (pit-95
  batch-95 / r421 probe / r431 erratum face): NaN < x comparisons
  yield False NOT decidable -- the decidable face derives from the
  underlying values notna (q10_ref.notna() & roc20.notna()); the
  naive (roc20 < q10_ref) bool face masquerades warmup bars as
  mom_closed -- BANNED at the mask level.  Composition order frozen
  everywhere (dedup face + engine face): signal -> filter -> timing
  -> GATE -> VOL -> YANG -> VCONF -> STREAK -> TSTATE -> AMP -> MOM
  -> initial-stop (a mom-blocked signal never arms a stop; W9 order
  extended, prereg sec.3 thirteen-tuple order R/X/S/T/STOP/GATE/VOL/
  YANG/VCONF/STREAK/TSTATE/AMP/MOM).

  G-MOM anchor law (prereg sec.2 probe facts, fail-closed): on the
  raw full-history member face (data/daily/sh510300.csv, 3,483 bars
  2012-05-28 -> 2026-09-22 cutoff): roc20-nan rows before bar 20 ==
  20; first-decidable == 139 / decidable == 3,344 / open == 374 /
  closed == 2,969 (open rate 10.74% -- decile-constructively
  balanced; core48 member spread min 7.23% / median 10.12% / max
  12.15% all non-degenerate); cross LOWER BOUNDS on the r228 probe
  basis {mom^mad60 253, mom^rsv60 212, mom^down_streak 139, mom^wide
  222}; eight-gate (gate x vol x yang x vconf x streak x tstate x amp
  x mom) 256 open-window cells: 111 non-empty / 145 empty with the
  exact frozen 145-empty name list (probe range min-nonzero 1 / max
  37; all-decidable 3,305 days; empty corner cells naturally
  filtered by the G1' entries>=30 gate, honest elimination not
  pre-screen invention); extreme-day gate states frozen (SEVEN
  extreme days 2/7 mom-open: 2015-07-27 crash open roc20 -0.0906 +
  2025-04-07 exogenous gap open -0.0852; 2016-01-04 circuit-breaker
  -0.052 near-miss closed honest; mom-face crisis-day exposure
  nonzero vs AMP 7/7-wide = whole-window reading + dd line, not
  single-point max); STREAK/TSTATE/AMP reproduction counts asserted
  exact (up 844 / down 817 / neither 1820 / mad60 383 / rsv60 632 /
  wide 1718 / narrow 1746 / zero-range 0 -- W7/W8/W9 cross-probe
  determinism law); exact per-cell cross-check vs
  results/_r228bmc_momgate_w10_probe_facts.json when present (r228
  determinism cross-check law).

  Exclusion law (prereg sec.1, THIRTEEN-tuple cell key=(template,
  params, axis_config, initial_stop, gate, vol, yang, vconf, streak,
  tstate, amp, mom), TWENTY real-read source faces, exact
  already-judged key, mom=none face only): prior-wave keys lacking
  the mom axis are mom=none completed (semantic-identity match);
  mom=mom_oversold (any gate/vol/yang/vconf/streak/tstate/amp combo)
  = new-syntax legal cells (never excluded).  Sources: frozen grammar
  bands (stop-gate-vol-yang-vconf-streak-tstate-amp-mom-none pad) +
  w1_screen 149 + w2_screen 404 + MASS screen 166 (declared tl3
  translation) + w3_screen 513 + w4_screen 461 + w5_screen 372 +
  w6_screen 293 + w7_screen 284 + w8_screen 408 + w9_screen 243
  (landed 2026-09-29 17:10:14; generate-time real-read; absent at
  build = zero rows honest) + judged products re-declare window
  (w1_judge / MASS judged / w2_judge / w3_judge / w4_judge / w5_judge
  / w6_judge / w7_judge / w8_judge / w9_judge -- TEN sources,
  generate-time real-read, absent = declared-unavailable zero rows;
  W9-JUDGE landed 2026-09-29 17:47:46 -- freeze-time ten-source
  full-declare window = third in history, disclosed; live re-read at
  generate time is the law).

Slice plan (W3-W9 single-writer precedent; wave ticket T-2026-09-29-122
opened+claimed at the freeze commit per O-1730 immediate-law; runner
build slice self-claimed by bm-b r438 per prereg sec.9 open slice +
product-priority law + r437 next-pointer):
  - slice-1 (this file, bm-b r438): thirteen-tuple grammar
    build_grammar_w10 (tl9 grammar extended with the NEW mom axis ->
    10,450,944 axis combos, new grammar sha16 constructively distinct
    from W1/MASS/W2-W9) + mom overlay layer (mom_state_series /
    mom_zero_mask / structure gate / G-MOM fail-closed full-face gate)
    + hermetic selftest (mom causality / 139-bar warmup / NaN-artifact
    leg [r417 map-NaN-bucket erratum face] / mom=none identity /
    eight-gate intersection / G-MOM probe anchors incl. 256-cell
    111/145 + extreme days / grammar structure / draw determinism /
    20-source exclusion loader / engine double-run byte-identity legs
    / funnel dispatch + CSV contract + pit-95 guards) + grammar
    serialization subcommand + GENERATE pool entry (consumer_plan per
    O-1820(3), pre-positioned products same commit per pit-90,
    lane_owner=bm-b per pit-103 terminal gate);
  - LATER slices (physical deps, separate commits with MSG
    declarations per W3-W9 precedent): SCREEN pool entry AFTER
    generate lands (lane_owner=bm-b); JUDGE pool entry AFTER
    screen-finalize (RAM r354 three-sample gate + sequencing behind
    in-flight judge faces per prereg sec.0 + host_gates MSG-1305);
    intake (judge products required); grammar ledger wave-10 row
    append at consumption (generate burn writes the row).
"""'''

OVERLAY = '''# --------------------------------------------- amp overlay (tl9 import face)
# The FULL amp machinery is imported verbatim from tl9 (W9 frozen
# face; import-face law; zero re-implementation) -- the W10 runner only
# adds the NEW mom overlay layer on top of it.
amp_state_series = tl9.amp_state_series
amp_zero_mask = tl9.amp_zero_mask
_amp_state_full = tl9._amp_state_full
_amp_structure_pass = tl9._amp_structure_pass
_amp_series_raw = tl9._amp_series_raw


# ------------------------------------------------------------- mom overlay layer
def _mom_series_raw(prices: dict):
    """r228-probe-verbatim MOM series computation (single computation
    site for series + decidable + raw values; census family O-1855(4)
    ROC20_q10 -- structural transplant of the in-repo census-verbatim
    MAD60_q10 decile mechanics): roc20 = close/close.shift(20)-1;
    q10_ref = roc20.rolling(252, min_periods=120).quantile(0.10);
    open_perm = roc20 < q10_ref (comparison NaN->False); decidable
    derives from the underlying values notna (pit-95 batch-95 law +
    r431 erratum face).  Returns (open_perm, dec, meta, roc20,
    q10_ref); deterministic pure function of the (cutoff-truncated)
    panel."""
    df = prices[MOM_MEMBER]
    close = df["close"].astype(float).sort_index()
    roc20 = close / close.shift(20) - 1.0
    q10_ref = roc20.rolling(252, min_periods=120).quantile(0.10)
    dec = q10_ref.notna() & roc20.notna()  # underlying notna (pit-95)
    open_perm = (roc20 < q10_ref)           # comparison face: NaN->False
    n = len(close)

    def _first_true(s):
        arr = s.fillna(False).astype(bool).values
        nz = np.flatnonzero(arr)
        return int(nz[0]) if len(nz) else None

    dec_n = int(dec.sum())
    open_n = int((open_perm & dec).sum())
    closed_n = int(((~open_perm) & dec).sum())
    meta = {"n_bars": int(n),
            "warmup_gate_closed_bars": _first_true(dec),
            "first_decidable_bar_idx": _first_true(dec),
            "decidable_days": dec_n,
            "open_days": open_n, "closed_days": closed_n,
            "open_rate_on_decidable":
            (round(float(open_n / dec_n), 4) if dec_n else None),
            "na_window_bars": 139,   # the gate family's warmup
            }
    return open_perm, dec, meta, roc20, q10_ref


def mom_state_series(prices: dict):
    """Frozen MOM spec (prereg sec.2/3): member 510300 signal-day info
    set -- open perm + decidable face.  Returns (open_perm, dec, meta):
    boolean Series on the member's own date index + structural meta.
    Deterministic pure function of the (cutoff-truncated) panel."""
    open_perm, dec, meta, *_ = _mom_series_raw(prices)
    return open_perm, dec, meta


def _mom_face_full():
    """Frozen sec.2 MOM-series face (r228 probe basis): the git-tracked
    raw full-history member file data/daily/sh510300.csv (open + high +
    low + close + volume columns), truncated at the evidence cutoff.
    (tl8._tstate_face_full loading caliber reused verbatim -- same
    member, same columns, same cutoff law; import-face law.)"""
    return tl8._tstate_face_full()


def _mom_state_full():
    """Canonical full-face mom_state with the frozen probe anchors
    asserted (prereg sec.2 G-MOM fail-closed): n_bars == 3,483;
    roc20-nan rows before bar 20 == 20; q10_ref first-decidable == 139
    / decidable == 3,344 / open == 374 / closed == 2,969 exact; cross
    LOWER bounds {mom^mad60 253, mom^rsv60 212, mom^down_streak 139,
    mom^wide 222}; eight-gate (gate x vol x yang x vconf x streak x
    tstate x amp x mom) 256 open-window cells 111-non-empty with the
    exact frozen 145-empty name list (probe range 1-37; all-decidable
    3,305) + exact per-cell cross-check vs the git-tracked probe
    facts file when present; extreme-day gate states exact (2/7
    mom-open incl. 2015-07-27 -0.0906 + 2025-04-07 -0.0852; roc20
    values at probe 4-decimal rounding, ratios at 3-decimal, rsv at
    4-decimal); STREAK/TSTATE/AMP reproduction counts exact (W7/W8/W9
    cross-probe determinism law).  Returns (mom_state, err); err is a
    one-line honest refusal reason when not None."""
    face = _mom_face_full()
    if face is None:
        return None, (f"raw member face data/daily/sh{MOM_MEMBER}.csv "
                      f"absent/open-high-low-close-volume columns "
                      f"missing or truncated tail != cutoff {CUTOFF}")
    open_perm, dec, meta, roc20, q10_ref = _mom_series_raw(face)
    a = MOM_ANCHOR
    if (meta.get("n_bars") != a["n_bars"]
            or meta["first_decidable_bar_idx"]
            != a["first_decidable_bar_idx"]
            or meta["decidable_days"] != a["decidable_days"]
            or meta["open_days"] != a["open_days"]
            or meta["closed_days"] != a["closed_days"]):
        return None, (f"G-MOM core anchors {meta} != probe "
                      f"{{n 3483, warmup 139, decidable 3344, open 374, "
                      f"closed 2969}}")
    if int(roc20.isna().sum()) != a["roc20_nan_rows_before_bar20"]:
        return None, (f"G-MOM roc20 nan-row anchor broken "
                      f"({int(roc20.isna().sum())} != "
                      f"{a['roc20_nan_rows_before_bar20']})")
    # ---- r228 probe basis faces VERBATIM (cross + eight-gate grid)
    df = face[MOM_MEMBER]
    close = df["close"].astype(float).sort_index()
    o_ = df["open"].astype(float).reindex(close.index)
    h_ = df["high"].astype(float).reindex(close.index)
    l_ = df["low"].astype(float).reindex(close.index)
    v_ = df["volume"].astype(float).reindex(close.index)
    amp = (h_ - l_) / close
    med20amp = amp.rolling(20, min_periods=20).median()
    amp_known = med20amp.notna()
    wide_face = (amp > med20amp) & amp_known
    up1 = close > close.shift(1)
    up2 = close.shift(1) > close.shift(2)
    dn1 = close < close.shift(1)
    dn2 = close.shift(1) < close.shift(2)
    judge = close.shift(2).notna()      # bars 0-1 warmup gate-closed
    up_st = judge & (up1 & up2).fillna(False)
    dn_st = judge & (dn1 & dn2).fillna(False)
    neither_st = judge & ~((up1 & up2).fillna(False)
                           | (dn1 & dn2).fillna(False))
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
    # reproduction counts (W7/W8/W9 cross-probe determinism law)
    sar = a["streak_anchor_reproduction"]
    if (int(up_st.sum()) != sar["up_streak_days"]
            or int(dn_st.sum()) != sar["down_streak_days"]
            or int(neither_st.sum()) != sar["neither_days"]):
        return None, (f"G-MOM streak-anchor reproduction broken "
                      f"up {int(up_st.sum())}/down {int(dn_st.sum())}/"
                      f"neither {int(neither_st.sum())} != {sar}")
    tar = a["tstate_anchor_reproduction"]
    if (int((mad_q10 & dec_mad).sum()) != tar["mad60_gate_true_days"]
            or int((rsv_low & dec_rsv).sum())
            != tar["rsv60_gate_true_days"]):
        return None, (f"G-MOM tstate-anchor reproduction broken "
                      f"mad60 {int((mad_q10 & dec_mad).sum())}/"
                      f"rsv60 {int((rsv_low & dec_rsv).sum())} != "
                      f"{tar}")
    aar = a["amp_anchor_reproduction"]
    if (int(wide_face.sum()) != aar["wide_days"]
            or int((amp_known & ~wide_face).sum()) != aar["narrow_days"]
            or int((h_ == l_).sum()) != aar["zero_range_rows"]):
        return None, (f"G-MOM amp-anchor reproduction broken "
                      f"wide {int(wide_face.sum())}/narrow "
                      f"{int((amp_known & ~wide_face).sum())}/"
                      f"zero-range {int((h_ == l_).sum())} != {aar}")
    # cross lower bounds on the r228 probe basis VERBATIM (joint
    # decidable windows per the probe cell() caliber)
    cross = {
        "mad60_and_mom":
            int((mad_q10 & open_perm & (dec & dec_mad)).sum()),
        "rsv60_and_mom":
            int((rsv_low & open_perm & (dec & dec_rsv)).sum()),
        "down_streak_and_mom":
            int((dn_st & open_perm & (dec & judge)).sum()),
        "wide_and_mom":
            int((wide_face & open_perm & (dec & amp_known)).sum()),
    }
    for group, lb in (("cross_tstate", a["cross_tstate_lower_bounds"]),
                      ("cross_streak", a["cross_streak_lower_bounds"]),
                      ("cross_amp", a["cross_amp_lower_bounds"])):
        for k, v_ in lb.items():
            if cross[k] < v_:
                return None, (f"G-MOM {group} lower bound broken "
                              f"{k}={cross[k]} < {v_}")
    # eight-gate 256-cell cross on the r228 probe basis VERBATIM
    # (all-decidable window m8 = dec_mom & amp_known & streak-decidable
    # & dec_mad & dec_rsv == 3,305 days; gate/vol/yang/vconf faces are
    # NaN->False comparison faces, notna() always True)
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
    narrow_face = (amp <= med20amp) & amp_known
    mom_open_face = open_perm & dec
    mom_closed_face = (~open_perm) & dec
    m8 = dec & amp_known & judge & dec_mad & dec_rsv
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
                                for mname, mm in (
                                        ("mom_open", mom_open_face),
                                        ("mom_closed", mom_closed_face)):
                                    cells[f"{bname}|{vname}|{yname}|"
                                          f"{sname}|{kname}|{tname}|"
                                          f"{aname}|{mname}"] = \
                                        int((m8 & b & vv & y & s & k & t
                                             & aa & mm).sum())
    empty = sorted(k for k, n_ in cells.items() if n_ <= 0)
    nonzero = [x for x in cells.values() if x > 0]
    if (len(cells) != 256
            or len(nonzero)
            != a["eight_gate_256cells_nonzero_count"]
            or len(empty) != a["eight_gate_256cells_empty_count"]
            or empty != sorted(a["eight_gate_256cells_empty"])
            or min(nonzero) < a["eight_gate_256cells_min_nonzero"]
            or max(cells.values()) > a["eight_gate_256cells_max"]
            or int(m8.sum()) != a["eight_gate_all_decidable_days"]):
        return None, (f"G-MOM eight-gate 256-cell cross drift "
                      f"(nonzero {len(nonzero)}/111, empty "
                      f"{len(empty)}/145, min {min(nonzero)}, max "
                      f"{max(cells.values())}, all-decidable "
                      f"{int(m8.sum())}/3305)")
    # exact per-cell cross-check vs the git-tracked probe facts file
    # (r228 determinism cross-check law; skip-face = file absent,
    # header counts above still binding)
    if os.path.exists(PROBE_FACTS_FILE):
        pf = json.load(open(PROBE_FACTS_FILE, encoding="utf-8"))
        pcells = pf.get("eight_gate_cells", {})
        drift = [f"{k}: {cells.get(k)} != {v_}"
                 for k, v_ in pcells.items() if cells.get(k) != v_]
        if pcells and drift:
            return None, (f"G-MOM probe-facts per-cell cross-check "
                          f"drift: {drift[:3]}")
    # extreme-day gate states (frozen face; roc20 values at probe
    # 4-decimal rounding + ratios at 3-decimal + rsv at 4-decimal,
    # tolerance 5.001e-5 on values)
    for dstr, want in a["extreme_days"].items():
        ts = pd.Timestamp(dstr)
        if ts not in close.index:
            return None, f"G-MOM extreme day {dstr} absent from face"
        rv20 = roc20.loc[ts]
        if pd.isna(rv20):
            return None, f"G-MOM extreme day {dstr} roc20 NaN"
        got_open = bool(open_perm.loc[ts]) if bool(dec.loc[ts]) else None
        got_val = round(float(rv20), 4)
        qr = q10_ref.loc[ts]
        got_ratio = (None if pd.isna(qr) or qr == 0
                     else round(float(rv20 / qr), 3))
        got_streak = ("up_streak2" if bool(up_st.loc[ts])
                      else "down_streak2" if bool(dn_st.loc[ts])
                      else "neither")
        rsv_v = rsv60.loc[ts]
        rsv_v = (None if pd.isna(rsv_v) else round(float(rsv_v), 4))
        got_amp = ("wide" if bool(wide_face.loc[ts]) else "narrow")
        if (got_open != want["mom_open"]
                or abs(got_val - want["roc20_value"]) > 5.01e-5
                or got_streak != want["streak"]
                or bool(mad_q10.loc[ts]) != want["tstate_mad60_q10"]
                or bool(rsv_low.loc[ts]) != want["tstate_rsv60_low"]
                or rsv_v is None
                or abs(rsv_v - want["rsv60_value"]) > 5.001e-5
                or got_amp != want["amp_state"]
                or got_ratio is None
                or abs(got_ratio - want["roc20_over_q10ref"]) > 5.01e-4):
            return None, (f"G-MOM extreme day {dstr} drift: open "
                          f"{got_open}/{want['mom_open']}, roc20 "
                          f"{got_val}/{want['roc20_value']}, ratio "
                          f"{got_ratio}/"
                          f"{want['roc20_over_q10ref']}, streak "
                          f"{got_streak}/{want['streak']}, mad "
                          f"{bool(mad_q10.loc[ts])}/"
                          f"{want['tstate_mad60_q10']}, rsv "
                          f"{bool(rsv_low.loc[ts])}/"
                          f"{want['tstate_rsv60_low']}, amp "
                          f"{got_amp}/{want['amp_state']}")
    meta = dict(meta)
    meta["cross_lower_bounds"] = cross
    meta["eight_gate_256cells"] = cells
    meta["eight_gate_256cells_empty"] = empty
    meta["eight_gate_all_decidable_days"] = int(m8.sum())
    meta["streak_anchor"] = {k: sar[k] for k in
                             ("up_streak_days", "down_streak_days",
                              "neither_days")}
    meta["tstate_anchor"] = dict(tar)
    meta["amp_anchor"] = dict(aar)
    return (open_perm, dec, meta), None


def mom_zero_mask(mask: pd.DataFrame, mom_key: str, mom_state):
    """Grammar-layer mom entry gate (prereg sec.3 momentum-confirmation
    face; E1-mapping primitive): off-face signal days -> effective
    signal zeroed (entry blocked; engine-native signal-off exit
    semantics -- the same primitive every cell uses when its own
    signal turns off; zero engine touch).  mom=none = W9 semantic
    baseline (identity).  The keep face derives from the DECIDABLE
    face (pit-95 / r431 erratum law): mom_oversold keeps open AND
    decidable -- the naive comparison bool face alone would masquerade
    warmup bars as mom_closed (BANNED).  Member dates missing from
    the mask index -> mom-closed (conservative reindex law,
    tl3/tl4/tl5/tl6/tl7/tl8/tl9 gate caliber)."""
    if mom_key == "none":
        return mask
    open_perm, dec, _ = mom_state
    open_keep = open_perm.reindex(mask.index).fillna(False).astype(int)
    dec_keep = dec.reindex(mask.index).fillna(False).astype(int)
    if mom_key == "mom_oversold":
        keep = (open_keep & dec_keep)
    else:
        raise ValueError(f"unknown mom_key {mom_key}")
    return mask.mul(keep, axis=0)


def _mom_structure_pass(mom_meta) -> bool:
    """Series-structure invariants on every panel face (fail-closed):
    139-bar warmup -- first-decidable + decidable partitions n_bars;
    open <= decidable and closed <= decidable.  A face shorter than
    the warmup (first-decidable None) honestly refuses."""
    if not isinstance(mom_meta, dict):
        return False
    n = mom_meta.get("n_bars", -1)
    fv = mom_meta.get("first_decidable_bar_idx")
    return (fv is not None
            and fv + mom_meta.get("decidable_days", -10**9) == n
            and mom_meta.get("open_days", -1)
            <= mom_meta.get("decidable_days", -1)
            and mom_meta.get("closed_days", -1)
            <= mom_meta.get("decidable_days", -1))'''

if "tl9.amp_state_series" in txt:
    print("refuse: already transplanted"); sys.exit(2)
i0 = txt.index('"""')
i1 = txt.index('"""', 3) + 3
txt = DOC + txt[i1:]
i0 = txt.index("# " + "-" * 56 + " amp overlay layer")
i1 = txt.index("# " + "-" * 60 + " grammar build")
txt = txt[:i0] + OVERLAY + "\n\n\n" + txt[i1:]
open(T, "w", encoding="utf-8", newline="\n").write(txt)
print("step C+D done:", len(txt), "bytes")
