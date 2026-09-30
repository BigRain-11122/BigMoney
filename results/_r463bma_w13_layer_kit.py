# -*- coding: utf-8 -*-
"""_r463bma_w13_layer_kit.py -- W13 SUMN layer kit (bm-a r463).

Slice product of the W13 runner-build chain (ticket
T-2026-09-30-125-P1, r462 surgical map next_round_moves step 1):
the COMPLETE new-layer parts of the W13 surgeon, generated from the
FROZEN faces only (research/TRIAL_LABOR_W13_PREREG.md frozen
r461 commit 8bc04fd63 + probe facts
results/_r456bma_sumnsump_w13_probe_facts.json), verbatim-import
law on the a158 frozen runner (SUMN20/SUMN10/BETA20 columns;
zero re-implementation):

  (1) SUMN_SPEC -- the sixteen-tuple identity spec dict (embedded
      in the W13 runner identity-constants block);
  (2) build_sumn_anchor() -- SUMN_ANCHOR generated PROGRAMMATICALLY
      from the probe facts (zero hand-copy; r445 declare-vs-disk
      law; W13 frozen numbers asserted fail-closed);
  (3) SUMN_LAYER_TEXT -- the full overlay-layer source text
      (_sumn_faces_raw / sumn_state_series / _sumn_face_full /
      _sumn_state_full / sumn_zero_mask / _sumn_structure_pass),
      the SUMN adaptation of the W12 RSQR layer (r445bmb surgeon
      RSQR_LAYER mirror; q10 low-side gate + direction-loaded
      split 387/0 + mirror-twin XOR=0 + nine-gate 103/409 cells);
  (4) verify() -- exec the layer text and run the G-SUMN
      real-data identity face on data/daily/sh510300.csv: every
      frozen anchor digit-checked (3483/120/3363/387/2976/3363/
      368, slope 387 up/0 down, mirror XOR 0, nine-gate 103
      nonzero/409 empty/min 1/max 41/all-decidable 3305, extreme
      7-day states, probe-facts per-cell cross-check).

Products: kit file + verify report
results/_r463bma_w13_layer_kit_report.json.  This kit is NOT the
runner and NOT the surgeon -- next round embeds these parts into
the surgeon skeleton (W12 surgeon sections 1-16 adapted) and runs
the r446 three-command identity face (prep/finalize/judge-prep).
Selftest leg runs verify() end-to-end; deterministic (pure
function of the git-tracked panel + facts).
"""
from __future__ import annotations
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.getcwd()
FACTS = os.path.join("results", "_r456bma_sumnsump_w13_probe_facts.json")
REPORT = os.path.join("results", "_r463bma_w13_layer_kit_report.json")
SUMN_MEMBER = "510300"          # core48 member (prereg sec.2 probe fact)
CUTOFF = "2026-09-22"           # P-5C binding (prereg sec.0/sec.2)
PROBE_SHA256_HEAD16 = "C2E5AAB0AC05906F"   # r461 freeze-window rerun bit-exact


def _load_facts():
    return json.load(open(FACTS, encoding="utf-8"))


# --------------------------------------------------------------- (1) SUMN_SPEC
SUMN_SPEC = {
    "member": SUMN_MEMBER,
    "series": "r456 probe verbatim / A158-TSGATE-P1 frozen SUMN "
              "construction via the frozen in-repo runner import "
              "(zero-invention law; scripts/a158_tsgate_probe.py "
              "alpha158_factors): signal-day-d close info set on "
              "the member face",
    "sumn20": 'F["SUMN20"] = down-share of absolute movement '
              "sum(clip(-diff,0),d)/sum(|diff|,d) in [0,1] (qlib "
              "semantics, expanding warmup; UP-dominant window = "
              "low value)",
    "sumn10": 'F["SUMN10"] = same construction, 10-day window',
    "q10_ref": "q10_ref = f.rolling(GATE_WIN=252, "
               "min_periods=GATE_MINP=120).quantile(0.10) "
               "(own-trailing 252-observation bottom-decile "
               "reference; GATE_WIN/GATE_MINP constants same-source "
               "frozen-runner import)",
    "sumn_lo": "f < q10_ref (up-share of absolute amplitude "
               "entering its own bottom decile = up-PURITY window; "
               "direction-LOADED unlike W12 RSQR sign-blind; "
               "A158-TSGATE-P1 48-PASS pool third-order family "
               "SUMN20_q10 OOS med_t 1.000 / SUMN10_q10 1.063 + "
               "GATE-RECHECK five-member net median +0.00921/"
               "+0.01562 CONFIRM = LONG anchor)",
    "none": "no gate (W12 semantic baseline face)",
    "direction_loaded": "up-share is direction-LOADED -- sumn20 "
                        "open-day BETA20 slope split 387 up / 0 "
                        "down (probe face; down-slope zero count = "
                        "gate up-purity BY CONSTRUCTION); direction "
                        "conditioning interaction carried by the "
                        "burned axes GATE/YANG/STREAK/MOM (prereg "
                        "sec.2 honesty disclosure (e); mom/mad/rsv "
                        "zero co-open empirical)",
    "mirror_twin": "SUMN20_q10 == SUMP20_q90 same-day co-open XOR=0 "
                   "(probe empirical; cluster #20-#23 corr-1.000; "
                   "SUMN+SUMP==1 identity, eps 1e-12 denominator; "
                   "SUMD monotone transform same days) -- supply "
                   "face = ONE up-share axis, zero extra dedup "
                   "burden",
    "grind_face": "sumn-open-and-calm 205 days forward-20d +0.71% "
                  "vs sumn-open-and-wild 144 days +4.92% (Welch "
                  "t=-5.86) -- grind increment face is a drag face "
                  "(prereg sec.2 honesty disclosure (b)); the VOL "
                  "axis co-conditioning decomposes this inside the "
                  "cell grid (W11/W12 same-structure third case)",
    "info_set": "signal-day d close; entry fills d+1 open (T+1 "
                "causal, same info set as GATE/VOL/YANG/VCONF/"
                "STREAK/TSTATE/AMP/MOM/STD/RSQR, zero lookahead)",
    "warmup": "120-bar warmup window gate-closed honest (diff "
              "undefined at bar 0; q10_ref min_periods 120 -> "
              "first decidable bar-idx == 120, fail-closed "
              "assertion == RSQR/STD family warmup)",
    "engine_note": "entry-permittance only (effective signal "
                   "zeroed, MSG-0440 E1-mapping primitive; exit "
                   "logic zero change; engine/exit_rules.py zero "
                   "touch)",
    "nan_artifact_note": "NaN comparisons (f < q10_ref) yield "
                         "False NOT decidable (pit-95 batch-95 law; "
                         "the decidable face derives from the "
                         "underlying values notna; the naive "
                         "comparison bool face masquerades warmup "
                         "bars as sumn_closed -- BANNED at the "
                         "mask level)",
    "adjacency_note": "nearest burned neighbor = W12 RSQR (fit "
                      "quality, sign-blind): both-open 163 / "
                      "sumn-only 224 / rsqr-only 178 (direction "
                      "purity vs fit shape read DIFFERENT states, "
                      "47.8%/42.12% mutual-open); W10 MOM zero "
                      "co-open 385/0 near-complement; W8 TSTATE "
                      "mad60/rsv60 double zero co-open (full "
                      "increment 387/0, 359/0); W4 VOL 41.26% "
                      "wild-side + 205 calm non-empty (above the "
                      "VSTD20_q20 collapsed-negative precedent "
                      "98.5%+11-empty); collapsed-neighbor "
                      "precedent NOT this face (probe cross-check "
                      "law)",
    "composition_order": "signal -> filter -> timing -> GATE -> "
                        "VOL -> YANG -> VCONF -> STREAK -> TSTATE "
                        "-> AMP -> MOM -> STD -> RSQR -> SUM -> "
                        "initial-stop (a sumn-blocked signal "
                        "never arms a stop; W12 order extended, "
                        "prereg sec.3 sixteen-tuple order R/X/S/T/"
                        "STOP/GATE/VOL/YANG/VCONF/STREAK/TSTATE/"
                        "AMP/MOM/STD/RSQR/SUM)",
}


# ------------------------------------------------- (2) build_sumn_anchor
def build_sumn_anchor():
    """SUMN_ANCHOR dict generated programmatically from the frozen
    probe facts (zero hand-copy; r445 declare-vs-disk law)."""
    pf = _load_facts()
    cells = pf["nine_gate_cells"]
    empty = sorted(k for k, v in cells.items() if v <= 0)
    adj = pf["adjacency"]
    slope = pf["sumn20_open_slope_sign_split"]
    mir = pf["mirror_identity"]
    gr = pf["grind_face_forward_20d"]
    f20 = pf["forward_20d"]
    anchor = {
        "n_bars": pf["rows"],
        "first_date": pf["first_date"],
        "cutoff": pf["last_date"],
        "sumn20_first_valid_bar_idx": 1,  # diff undefined at 0
        "warmup_gate_closed_bars": 120,
        "first_decidable_bar_idx": 120,
        "decidable_days": pf["sumn20_decidable_days"],
        "open_days": pf["sumn20_open_days"],
        "closed_days": pf["sumn20_decidable_days"]
                       - pf["sumn20_open_days"],
        "sumn20_open_rate_on_decidable":
            pf["sumn20_open_rate_on_decidable"],
        "sumn10_decidable_days": pf["sumn10_decidable_days"],
        "sumn10_open_days": pf["sumn10_open_days"],
        "sumn10_open_rate_on_decidable":
            pf["sumn10_open_rate_on_decidable"],
        "slope_sign_split": {
            "up_slope_days": slope["up_slope_days"],
            "down_slope_days": slope["down_slope_days"],
            "note": "BETA20 sign from the same frozen runner; "
                    "up-dominant windows are slope-up-heavy BY "
                    "CONSTRUCTION (direction-loaded axis) -- the "
                    "split quantifies how much; direction "
                    "conditioning still lives in burned axes "
                    "(GATE/YANG/STREAK/MOM), redundancy measured "
                    "in adjacency cells",
        },
        "mirror_twin": {
            "sumn20_q10_vs_sump20_q90_both_open_days":
                mir["sumn20_q10_vs_sump20_q90_both_open_days"],
            "sumn20_q10_vs_sump20_q90_xor_days":
                mir["sumn20_q10_vs_sump20_q90_xor_days"],
            "sumn_plus_sump_max_dev":
                mir["sumn_plus_sump_max_dev"],
            "note": "mirror-twin identity SUMN+SUMP==1 (eps 1e-12 "
                    "denominator); supply face = ONE up-share axis",
        },
        "cross_lower_bounds": {
            "mad60_and_sumn20": adj["sumn20_vs_mad60"]["both_open"],
            "rsv60_and_sumn20":
                adj["sumn20_vs_rsv60"]["both_open"],
            "mom_and_sumn20": adj["sumn20_vs_mom"]["both_open"],
            "down_streak_and_sumn20":
                adj["sumn20_vs_downstreak"]["both_open"],
            "up_streak_and_sumn20":
                adj["sumn20_vs_upstreak"]["both_open"],
            "wide_and_sumn20": adj["sumn20_vs_wide"]["both_open"],
            "narrow_and_sumn20":
                adj["sumn20_vs_narrow"]["both_open"],
            "std20_and_sumn20":
                adj["sumn20_vs_std20"]["both_open"],
            "rsqr20_and_sumn20":
                adj["sumn20_vs_rsqr20"]["both_open"],
            "sumn20_vs_sumn10_both_open":
                adj["sumn10_vs_sumn20"]["both_open"],
            "calm_and_sumn20": adj["sumn20_vs_calm"]["both_open"],
            "wild_and_sumn20": adj["sumn20_vs_wild"]["both_open"],
        },
        "zero_coopen_exact_assert": {
            "mad60": adj["sumn20_vs_mad60"]["both_open"] == 0,
            "rsv60": adj["sumn20_vs_rsv60"]["both_open"] == 0,
            "mom": adj["sumn20_vs_mom"]["both_open"] == 0,
        },
        "nine_gate_all_decidable_days":
            pf["nine_gate_all_decidable_days"],
        "nine_gate_512cells_nonzero_count":
            pf["nine_gate_512_cells_nonzero_count"],
        "nine_gate_512cells_empty_count":
            pf["nine_gate_512_cells_empty_count"],
        "nine_gate_512cells_min_nonzero":
            pf["nine_gate_512_cells_min_nonzero"],
        "nine_gate_512cells_max": pf["nine_gate_512_cells_max"],
        "nine_gate_512cells_empty": empty,
        "extreme_days": pf["extreme_day_states"],
        "streak_anchor_reproduction": {
            "up_streak_days": 844, "down_streak_days": 817,
            "neither_days": 1820},
        "tstate_anchor_reproduction": {
            "mad60_gate_true_days": 383, "rsv60_gate_true_days": 632},
        "amp_anchor_reproduction": {
            "wide_days": 1718, "narrow_days": 1746,
            "zero_range_rows": 0},
        "core48_sumn20_open_rate": pf["core48_sumn20_open_rate"],
        "forward_20d_descriptive": {
            "mean_fwd_open": f20["mean_fwd_open"],
            "n_open": f20["n_open"], "welch_t": f20["welch_t"],
            "note": "descriptive probe face on the member anchor "
                    "only; overlapping windows inflate |t|; NOT a "
                    "strategy claim"},
        "grind_face_forward_20d": {
            "n_open_calm": gr["n_open_calm"],
            "n_open_wild": gr["n_open_wild"],
            "mean_fwd_open_calm": gr["mean_fwd_open_calm"],
            "mean_fwd_open_wild": gr["mean_fwd_open_wild"],
            "welch_t_calm_vs_wild": gr["welch_t_calm_vs_wild"],
        },
        "probe_facts_note": "generated verbatim from "
                            "_r456bma_sumnsump_w13_probe_facts.json "
                            "(r456 probe = frozen authoritative SUMN "
                            "definition via the a158 frozen-runner "
                            "import; r461 freeze-window rerun "
                            "bit-exact SHA256 head16 "
                            + PROBE_SHA256_HEAD16
                            + "; nine-gate face = sumn20 open/closed "
                            "states on the r456 probe basis; "
                            "W4-VOL/W11-STD/W12-RSQR three-value "
                            "axis precedent)",
    }
    assert anchor["nine_gate_512cells_nonzero_count"] == 103
    assert anchor["nine_gate_512cells_empty_count"] == 409
    assert len(empty) == 409
    assert anchor["decidable_days"] == 3363
    assert anchor["open_days"] == 387
    assert anchor["closed_days"] == 2976
    assert anchor["sumn10_decidable_days"] == 3363
    assert anchor["sumn10_open_days"] == 368
    assert anchor["first_decidable_bar_idx"] == 120
    assert (anchor["slope_sign_split"]["up_slope_days"] == 387
            and anchor["slope_sign_split"]["down_slope_days"] == 0)
    assert (anchor["mirror_twin"]
            ["sumn20_q10_vs_sump20_q90_both_open_days"] == 387
            and anchor["mirror_twin"]
            ["sumn20_q10_vs_sump20_q90_xor_days"] == 0)
    assert anchor["zero_coopen_exact_assert"] == {
        "mad60": True, "rsv60": True, "mom": True}
    assert anchor["nine_gate_all_decidable_days"] == 3305
    assert anchor["streak_anchor_reproduction"] == {
        "up_streak_days": 844, "down_streak_days": 817,
        "neither_days": 1820}
    assert anchor["extreme_days"]["2024-02-28"]["sumn20_open"] \
        is True
    assert anchor["extreme_days"]["2026-01-19"]["sumn20_open"] \
        is False
    return anchor


# --------------------------------------------------- (3) SUMN_LAYER_TEXT
# The full overlay-layer source text.  Execution environment (the
# W13 runner identity-constants block / verify harness): pd, np,
# os, json, a158 (a158_tsgate_probe), tl8 (member face), and the
# burned-layer aliases _std_series_raw / _mom_series_raw /
# _rsqr_faces_raw (tl11/tl10/tl12 import faces -- W12 surgeon
# L328-L348 mirror), SUMN_MEMBER, SUMN_ANCHOR, CUTOFF,
# PROBE_FACTS_FILE.
SUMN_LAYER_TEXT = r'''# ------------------------------------------------------------ sumn overlay layer
def _sumn_faces_raw(prices: dict):
    """r456-probe-verbatim SUMN face computation (single
    computation site for both window faces + decidable + raw
    values + slope sign; A158-TSGATE-P1 frozen SUMN20_q10/
    SUMN10_q10 construction via the FROZEN in-repo runner import
    -- import a158_tsgate_probe; zero-invention law):
    F = a158.alpha158_factors(member frame); sumn20 = F["SUMN20"]
    (down-share of absolute movement sum(clip(-diff,0),d)/
    sum(|diff|,d) in [0,1], qlib semantics; UP-dominant window =
    low value); q10_ref = sumn20.rolling(a158.GATE_WIN,
    min_periods=a158.GATE_MINP).quantile(0.10); open_perm =
    sumn20 < q10_ref (comparison NaN->False); decidable derives
    from the underlying values notna (pit-95 batch-95 law).
    sumn10 same face on the 10-bar window.  Returns (open20,
    dec20, meta, sumn20, q10_ref, open10, dec10, sumn10,
    q10_ref10, beta20); deterministic pure function of the
    (cutoff-truncated) panel."""
    df = prices[SUMN_MEMBER].sort_index()
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
    sumn20, sumn10, beta20 = F["SUMN20"], F["SUMN10"], F["BETA20"]
    q10_ref = sumn20.rolling(a158.GATE_WIN,
                             min_periods=a158.GATE_MINP).quantile(0.10)
    dec = sumn20.notna() & q10_ref.notna()  # underlying notna (pit-95)
    open_perm = (sumn20 < q10_ref)           # comparison face: NaN->False
    q10_ref10 = sumn10.rolling(a158.GATE_WIN,
                               min_periods=a158.GATE_MINP).quantile(0.10)
    dec10 = sumn10.notna() & q10_ref10.notna()
    open10 = (sumn10 < q10_ref10)
    n = len(sumn20)

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
            "sumn10_decidable_days": int(dec10.sum()),
            "sumn10_open_days": int((open10 & dec10).sum()),
            "na_window_bars": 120,   # the gate family's warmup
            }
    return open_perm, dec, meta, sumn20, q10_ref, open10, dec10, \
        sumn10, q10_ref10, beta20


def sumn_state_series(prices: dict):
    """Frozen SUMN spec (prereg sec.2/3): member 510300 signal-day
    info set -- sumn20 open perm + decidable face + the sumn10
    faces.  Returns (open20, dec20, meta, open10, dec10): boolean
    Series on the member's own date index + structural meta + the
    10-bar faces.  Deterministic pure function of the (cutoff-
    truncated) panel."""
    o20, d20, meta, _s20, _q20, o10, d10, _s10, _q10, _b20 = \
        _sumn_faces_raw(prices)
    return o20, d20, meta, o10, d10


def _sumn_face_full():
    """Frozen sec.2 SUMN-series face (r456 probe basis): the
    git-tracked raw full-history member file data/daily/
    sh510300.csv (open + high + low + close + volume columns),
    truncated at the evidence cutoff.  (tl8._tstate_face_full
    loading caliber reused verbatim -- same member, same columns,
    same cutoff law; import-face law.)"""
    return tl8._tstate_face_full()


def _sumn_state_full():
    """Canonical full-face sumn_state with the frozen probe
    anchors asserted (prereg sec.2 G-SUMN fail-closed): n_bars ==
    3,483; first-decidable == 120 / decidable == 3,363 / open ==
    387 / closed == 2,976 / sumn10 decidable == 3,363 / sumn10
    open == 368 exact; slope-sign split 387 up / 0 down (BETA20
    same frozen runner; direction-loaded construction); mirror
    twin SUMN20_q10 vs SUMP20_q90 both-open 387 / XOR 0 (probe
    empirical); cross reproduction counts {streak up 844/down
    817/neither 1820, mad60 383, rsv60 632, wide 1718/narrow 1746/
    zero-range 0} + cross lower bounds {mad60 0-exact, rsv60
    0-exact, mom 0-exact, down_streak 33, up_streak 153, wide 228,
    narrow 159, std20 120, rsqr20 163, sumn10-both-open 193,
    calm 205, wild 144}; NINE-gate (gate x vol x yang x vconf x
    streak x tstate x amp x std20 x sumn20) 512 open-window cells
    103-non-empty with the exact frozen 409-empty name list (probe
    range 1-41; all-decidable 3,305) + exact per-cell cross-check
    vs the git-tracked probe facts file when present; extreme-day
    gate states exact (sumn20 open 2/7, sumn10 open 3/7; crisis
    crash days structurally closed, violent-rebound days open --
    sumn crisis behavior != none cells, readout note).  Returns
    (sumn_state, err); err is a one-line honest refusal reason
    when not None."""
    face = _sumn_face_full()
    if face is None:
        return None, (f"raw member face data/daily/sh{SUMN_MEMBER}.csv "
                      f"absent/open-high-low-close-volume columns "
                      f"missing or truncated tail != cutoff {CUTOFF}")
    open20, dec, meta, sumn20, q10_ref, open10, dec10, \
        sumn10, q10_ref10, beta20 = _sumn_faces_raw(face)
    a = SUMN_ANCHOR
    if (meta.get("n_bars") != a["n_bars"]
            or meta["first_decidable_bar_idx"]
            != a["first_decidable_bar_idx"]
            or meta["decidable_days"] != a["decidable_days"]
            or meta["open_days"] != a["open_days"]
            or meta["closed_days"] != a["closed_days"]
            or meta["sumn10_decidable_days"]
            != a["sumn10_decidable_days"]
            or meta["sumn10_open_days"] != a["sumn10_open_days"]):
        return None, (f"G-SUMN core anchors {meta} != probe "
                      f"{{n 3483, warmup 120, decidable 3363, open "
                      f"387, closed 2976, sumn10 dec 3363 open "
                      f"368}}")
    # slope-sign split (direction-loaded disclosure face; prereg
    # sec.2 (e): down-slope zero count = gate up-purity BY
    # CONSTRUCTION)
    m_open = open20 & dec & beta20.notna()
    up_days = int((m_open & (beta20 > 0)).sum())
    dn_days = int((m_open & (beta20 <= 0)).sum())
    if (up_days != a["slope_sign_split"]["up_slope_days"]
            or dn_days != a["slope_sign_split"]["down_slope_days"]):
        return None, (f"G-SUMN slope-sign split drift {up_days}/"
                      f"{dn_days} != probe "
                      f"{a['slope_sign_split']['up_slope_days']}/"
                      f"{a['slope_sign_split']['down_slope_days']}")
    # mirror-twin identity (prereg sec.2 frozen face): SUMN20_q10
    # and SUMP20_q90 fire identical days -- XOR must be 0 on the
    # decidable face (probe empirical; SUMN+SUMP==1, eps 1e-12
    # denominator; SUMP column face used directly, not 1-sumn)
    df = face[SUMN_MEMBER]
    close = df["close"].astype(float).sort_index()
    _di = pd.DataFrame({"open": df["open"].astype(float)
                        .reindex(close.index).to_numpy(),
                        "high": df["high"].astype(float)
                        .reindex(close.index).to_numpy(),
                        "low": df["low"].astype(float)
                        .reindex(close.index).to_numpy(),
                        "close": close.to_numpy(),
                        "volume": df["volume"].astype(float)
                        .reindex(close.index).to_numpy()},
                       index=close.index)
    Fm = a158.alpha158_factors(_di)
    sump20 = Fm["SUMP20"]
    q90r_sump = sump20.rolling(a158.GATE_WIN,
                                min_periods=a158.GATE_MINP).quantile(0.90)
    sump_open = (sump20 > q90r_sump)
    sump_dec = sump20.notna() & q90r_sump.notna()
    mir_both = int((sump_open & open20 & (dec & sump_dec)).sum())
    mir_xor = int(((sump_open ^ open20) & (dec & sump_dec)).sum())
    mt = a["mirror_twin"]
    if (mir_both != mt["sumn20_q10_vs_sump20_q90_both_open_days"]
            or mir_xor
            != mt["sumn20_q10_vs_sump20_q90_xor_days"]):
        return None, (f"G-SUMN mirror-twin drift both {mir_both}/"
                      f"{mir_both and 387}, xor {mir_xor} != probe "
                      f"{mt['sumn20_q10_vs_sump20_q90_both_open_days']}"
                      f"/{mt['sumn20_q10_vs_sump20_q90_xor_days']}")
    # ---- r456 probe basis faces VERBATIM (cross + nine-gate grid)
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
        return None, (f"G-SUMN streak-anchor reproduction broken "
                      f"up {int(up_st.sum())}/down {int(dn_st.sum())}/"
                      f"neither {int(neither_st.sum())} != {sar}")
    tar = a["tstate_anchor_reproduction"]
    if (int((mad_q10 & dec_mad).sum()) != tar["mad60_gate_true_days"]
            or int((rsv_low & dec_rsv).sum())
            != tar["rsv60_gate_true_days"]):
        return None, (f"G-SUMN tstate-anchor reproduction broken "
                      f"mad60 {int((mad_q10 & dec_mad).sum())}/"
                      f"rsv60 {int((rsv_low & dec_rsv).sum())} != "
                      f"{tar}")
    aar = a["amp_anchor_reproduction"]
    if (int(wide_face.sum()) != aar["wide_days"]
            or int((amp_known & ~wide_face).sum()) != aar["narrow_days"]
            or int((h_ == l_).sum()) != aar["zero_range_rows"]):
        return None, (f"G-SUMN amp-anchor reproduction broken "
                      f"wide {int(wide_face.sum())}/narrow "
                      f"{int((amp_known & ~wide_face).sum())}/"
                      f"zero-range {int((h_ == l_).sum())} != {aar}")
    # std faces VERBATIM from the W11 frozen machinery (tl11
    # import face; A158 STD20_q90/STD10_q90 construction)
    s20o, s20d, _s20meta, _s20, _s20q, s10o, s10d, _s10, _s10q = \
        _std_series_raw(face)
    dec_s20 = s20d
    std20_open = s20o
    # mom faces VERBATIM from the W10 frozen machinery (tl10
    # import face) for the mom cross bound
    m_open_face, m_dec, _mmeta = _mom_series_raw(face)[:3]
    # rsqr faces VERBATIM from the W12 frozen machinery (tl12
    # import face) for the rsqr cross bound
    r20o, r20d, _r20meta = _rsqr_faces_raw(face)[0], \
        _rsqr_faces_raw(face)[1], _rsqr_faces_raw(face)[2]
    # cross bounds on the r456 probe basis VERBATIM (zero-co-open
    # neighbors asserted EXACT per the frozen adjacency face)
    cross = {
        "mad60_and_sumn20":
            int((mad_q10 & open20 & (dec & dec_mad)).sum()),
        "rsv60_and_sumn20":
            int((rsv_low & open20 & (dec & dec_rsv)).sum()),
        "mom_and_sumn20":
            int((m_open_face & open20 & (dec & m_dec)).sum()),
        "down_streak_and_sumn20":
            int((dn_st & open20 & (dec & judge)).sum()),
        "up_streak_and_sumn20":
            int((up_st & open20 & (dec & judge)).sum()),
        "wide_and_sumn20":
            int((wide_face & open20 & (dec & amp_known)).sum()),
        "narrow_and_sumn20":
            int(((amp_known & ~wide_face) & open20
                 & (dec & amp_known)).sum()),
        "std20_and_sumn20":
            int((std20_open & open20 & (dec & dec_s20)).sum()),
        "rsqr20_and_sumn20":
            int((r20o & open20 & (dec & r20d)).sum()),
        "sumn20_vs_sumn10_both_open":
            int((open10 & open20 & (dec & dec10)).sum()),
        "calm_and_sumn20": None,   # filled below (vol face needed)
        "wild_and_sumn20": None,
    }
    # vol faces for the calm/wild grind decomposition bounds
    ret = close.pct_change()
    vol20 = ret.rolling(20, min_periods=20).std(ddof=1)
    med500 = vol20.rolling(500, min_periods=500).median()
    calm = vol20 <= med500
    wild = vol20 > med500
    cross["calm_and_sumn20"] = int((calm & open20
                                    & (dec & calm.notna())).sum())
    cross["wild_and_sumn20"] = int((wild & open20
                                    & (dec & calm.notna())).sum())
    zc = a["zero_coopen_exact_assert"]
    for k, exact in (("mad60_and_sumn20", zc["mad60"]),
                     ("rsv60_and_sumn20", zc["rsv60"]),
                     ("mom_and_sumn20", zc["mom"])):
        if exact and cross[k] != 0:
            return None, (f"G-SUMN zero-co-open exact bound broken "
                          f"{k}={cross[k]} != 0 (perfect "
                          f"disjointness face)")
    for k, lbv in a["cross_lower_bounds"].items():
        if k in cross and cross[k] < lbv:
            return None, (f"G-SUMN cross lower bound broken "
                          f"{k}={cross[k]} < {lbv}")
    # NINE-gate 512-cell cross on the r456 probe basis VERBATIM
    # (m9 = dec_sumn20 & bull/calm notna & amp_known & streak-
    # decidable & dec_mad & dec_rsv & dec_s20 == 3,305 days;
    # gate/vol/yang/vconf faces are NaN->False comparison faces)
    ma200 = close.rolling(200).mean()
    bull = close > ma200
    bear = ~bull
    med20v = v_.rolling(20, min_periods=20).median()
    surge = v_ > med20v
    yang = close > o_
    red = ~yang
    narrow_face = (amp <= med20amp) & amp_known
    sumn_open_face = open20 & dec
    sumn_closed_face = (~open20) & dec
    m9 = dec & bull.notna() & calm.notna() & amp_known & judge \
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
                                    for suname, su in (
                                            ("sumn20_open",
                                             sumn_open_face),
                                            ("sumn20_closed",
                                             sumn_closed_face)):
                                        cells[f"{bname}|{vname}|"
                                              f"{yname}|{sname}|"
                                              f"{kname}|{tname}|"
                                              f"{aname}|{sdname}|"
                                              f"{suname}"] = \
                                              int((m9 & b & vv & y
                                                 & s & k & t & aa
                                                 & sd & su).sum())
    empty = sorted(k for k, n_ in cells.items() if n_ <= 0)
    nonzero = [x for x in cells.values() if x > 0]
    if (len(cells) != 512
            or len(nonzero)
            != a["nine_gate_512cells_nonzero_count"]
            or len(empty) != a["nine_gate_512cells_empty_count"]
            or empty != sorted(a["nine_gate_512cells_empty"])
            or min(nonzero) < a["nine_gate_512cells_min_nonzero"]
            or max(cells.values()) > a["nine_gate_512cells_max"]
            or int(m9.sum())
            != a["nine_gate_all_decidable_days"]):
        return None, (f"G-SUMN nine-gate 512-cell cross drift "
                      f"(nonzero {len(nonzero)}/103, empty "
                      f"{len(empty)}/409, min {min(nonzero)}, max "
                      f"{max(cells.values())}, all-decidable "
                      f"{int(m9.sum())}/3305)")
    # exact per-cell cross-check vs the git-tracked probe facts file
    # (r456 determinism cross-check law; skip-face = file absent,
    # header counts above still binding)
    if os.path.exists(PROBE_FACTS_FILE):
        pf_ = json.load(open(PROBE_FACTS_FILE, encoding="utf-8"))
        pcells = pf_.get("nine_gate_cells", {})
        drift = [f"{k}: {cells.get(k)} != {v_}"
                 for k, v_ in pcells.items() if cells.get(k) != v_]
        if pcells and drift:
            return None, (f"G-SUMN probe-facts per-cell cross-check "
                          f"drift: {drift[:3]}")
    # extreme-day gate states (frozen face; sumn20 values at probe
    # 6-decimal rounding + ratios at 3-decimal; sumn20 open 2/7
    # violent-rebound days / closed on crash days; sumn10 open 3/7)
    for dstr, want in a["extreme_days"].items():
        ts = pd.Timestamp(dstr)
        if ts not in close.index:
            return None, f"G-SUMN extreme day {dstr} absent from face"
        sv20 = sumn20.loc[ts]
        if pd.isna(sv20):
            return None, f"G-SUMN extreme day {dstr} sumn20 NaN"
        got_open = bool(open20.loc[ts]) if bool(dec.loc[ts]) else None
        got_open10 = (bool(open10.loc[ts]) if bool(dec10.loc[ts])
                      else None)
        got_val = round(float(sv20), 6)
        qr = q10_ref.loc[ts]
        got_ratio = (None if pd.isna(qr) or qr == 0
                     else round(float(sv20 / qr), 3))
        got_std20 = (bool(std20_open.loc[ts])
                     if bool(dec_s20.loc[ts]) else None)
        got_rsqr20 = (bool(r20o.loc[ts])
                      if bool(r20d.loc[ts]) else None)
        got_slope = None
        if bool(dec.loc[ts]) and not pd.isna(beta20.loc[ts]):
            got_slope = "up" if beta20.loc[ts] > 0 else "down"
        if (got_open != want["sumn20_open"]
                or got_open10 != want["sumn10_open"]
                or abs(got_val - want["sumn20_value"]) > 5.01e-6
                or got_slope != want["slope_sign"]
                or got_std20 != want["std20_open"]
                or got_rsqr20 != want["rsqr20_open"]
                or got_ratio is None
                or abs(got_ratio - want["sumn20_over_q10ref"])
                > 5.01e-4):
            return None, (f"G-SUMN extreme day {dstr} drift: open "
                          f"{got_open}/{want['sumn20_open']}, "
                          f"open10 {got_open10}/"
                          f"{want['sumn10_open']}, sumn20 "
                          f"{got_val}/{want['sumn20_value']}, "
                          f"ratio {got_ratio}/"
                          f"{want['sumn20_over_q10ref']}, slope "
                          f"{got_slope}/{want['slope_sign']}, "
                          f"std20 {got_std20}/"
                          f"{want['std20_open']}, rsqr20 "
                          f"{got_rsqr20}/{want['rsqr20_open']}")
    meta = dict(meta)
    meta["slope_sign_split"] = {"up_slope_days": up_days,
                                "down_slope_days": dn_days}
    meta["mirror_twin"] = {"both_open_days": mir_both,
                           "xor_days": mir_xor}
    meta["cross_lower_bounds"] = cross
    meta["nine_gate_512cells"] = cells
    meta["nine_gate_512cells_empty"] = empty
    meta["nine_gate_all_decidable_days"] = int(m9.sum())
    meta["streak_anchor"] = {k: sar[k] for k in
                             ("up_streak_days", "down_streak_days",
                              "neither_days")}
    meta["tstate_anchor"] = dict(tar)
    meta["amp_anchor"] = dict(aar)
    return (open20, dec, meta, open10, dec10), None


def sumn_zero_mask(mask: pd.DataFrame, sumn_key: str, sumn_state):
    """Grammar-layer sumn entry gate (prereg sec.3 up-purity face;
    E1-mapping primitive): off-face signal days -> effective
    signal zeroed (entry blocked; engine-native signal-off exit
    semantics -- the same primitive every cell uses when its own
    signal turns off; zero engine touch).  sumn=none = W12
    semantic baseline (identity).  The keep face derives from the
    DECIDABLE face (pit-95 law): sumn20_lo keeps sumn20-open AND
    decidable; sumn10_lo keeps sumn10-open AND decidable -- the
    naive comparison bool face alone would masquerade warmup bars
    as sumn_closed (BANNED).  Member dates missing from the mask
    index -> sumn-closed (conservative reindex law,
    tl3/tl4/tl5/tl6/tl7/tl8/tl9/tl10/tl11/tl12 gate caliber)."""
    if sumn_key == "none":
        return mask
    open20, dec20, _meta, open10, dec10 = sumn_state
    if sumn_key == "sumn20_lo":
        keep = (open20.reindex(mask.index).fillna(False).astype(int)
                & dec20.reindex(mask.index).fillna(False).astype(int))
    elif sumn_key == "sumn10_lo":
        keep = (open10.reindex(mask.index).fillna(False).astype(int)
                & dec10.reindex(mask.index).fillna(False).astype(int))
    else:
        raise ValueError(f"unknown sumn_key {sumn_key}")
    return mask.mul(keep, axis=0)


def _sumn_structure_pass(sumn_meta) -> bool:
    """Series-structure invariants on every panel face (fail-closed):
    120-bar warmup -- first-decidable + decidable partitions n_bars;
    open <= decidable and closed <= decidable.  A face shorter than
    the warmup (first-decidable None) honestly refuses."""
    if not isinstance(sumn_meta, dict):
        return False
    n = sumn_meta.get("n_bars", -1)
    fv = sumn_meta.get("first_decidable_bar_idx")
    return (fv is not None
            and fv + sumn_meta.get("decidable_days", -10**9) == n
            and sumn_meta.get("open_days", -1)
            <= sumn_meta.get("decidable_days", -1)
            and sumn_meta.get("closed_days", -1)
            <= sumn_meta.get("decidable_days", -1))
'''


# --------------------------------------------------------------- (4) verify
def verify():
    """Exec the layer text and run the G-SUMN real-data identity
    face.  Returns (report, err)."""
    steps = []
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import pandas as pd
    import numpy as np
    import a158_tsgate_probe as a158          # frozen A158 runner
    import trial_labor_w8 as tl8              # member-face loader
    import trial_labor_w10 as tl10            # mom import face
    import trial_labor_w11 as tl11            # std import face
    import trial_labor_w12 as tl12            # rsqr import face
    import trial_labor_w1 as tl1

    anchor = build_sumn_anchor()
    steps.append(f"anchor: {anchor['decidable_days']}d dec / "
                 f"open {anchor['open_days']} / sumn10 "
                 f"{anchor['sumn10_open_days']} / nine-gate "
                 f"{anchor['nine_gate_512cells_nonzero_count']}"
                 f"/{anchor['nine_gate_512cells_empty_count']}")

    env = {
        "pd": pd, "np": np, "os": os, "json": json, "a158": a158,
        "tl8": tl8, "tl1": tl1,
        "_std_series_raw": tl11._std_series_raw,
        "_mom_series_raw": tl10._mom_series_raw,
        "_rsqr_faces_raw": tl12._rsqr_faces_raw,
        "SUMN_MEMBER": SUMN_MEMBER, "SUMN_ANCHOR": anchor,
        "CUTOFF": CUTOFF,
        "PROBE_FACTS_FILE": FACTS,
    }
    exec(compile(SUMN_LAYER_TEXT, "<sumn_layer>", "exec"), env)
    steps.append("layer: exec OK (6 functions defined)")

    # T+1 zero-lookahead anchor: five-tuple date partition at the
    # frozen cutoff is checked implicitly by _sumn_face_full tail;
    # explicit cutoff assertion on the loaded face:
    face = env["_sumn_face_full"]()
    if face is None:
        return None, "member face sh510300.csv absent/truncated"
    tail = str(face[SUMN_MEMBER].index[-1].date())
    if tail != CUTOFF:
        return None, f"face tail {tail} != cutoff {CUTOFF}"
    steps.append(f"face: tail {tail} == cutoff")

    state, err = env["_sumn_state_full"]()
    if err is not None:
        return None, f"G-SUMN refusal: {err}"
    o20, d20, meta, o10, d10 = state
    nz_cells = len([x for x in
                    meta["nine_gate_512cells"].values() if x > 0])
    em_cells = len(meta["nine_gate_512cells_empty"])
    steps.append(
        f"G-SUMN: dec {meta['decidable_days']} / open "
        f"{meta['open_days']} / sumn10 {meta['sumn10_open_days']} / "
        f"slope {meta['slope_sign_split']['up_slope_days']}/"
        f"{meta['slope_sign_split']['down_slope_days']} / mirror "
        f"{meta['mirror_twin']['both_open_days']}/"
        f"{meta['mirror_twin']['xor_days']} / nine-gate "
        f"{nz_cells} nonzero / {em_cells} empty / "
        f"all-dec {meta['nine_gate_all_decidable_days']}")

    # zero-mask E1-mapping smoke: none identity + sumn20_lo keeps
    # only sumn-open decidable days on a small synthetic mask
    import pandas as pd2
    sm = pd2.DataFrame({SUMN_MEMBER: [1, 1, 1]},
                       index=face[SUMN_MEMBER].index[-3:])
    assert env["sumn_zero_mask"](sm, "none", state).equals(sm)
    keep_n = int(env["sumn_zero_mask"](sm, "sumn20_lo", state)
                 .values.sum())
    exp = int((o20 & d20).reindex(sm.index).fillna(False).sum())
    if keep_n != exp:
        return None, f"zero-mask sumn20_lo keep {keep_n} != {exp}"
    steps.append(f"zero-mask: none identity + sumn20_lo keep {exp}")
    if not env["_sumn_structure_pass"](meta):
        return None, "structure-pass False on canonical meta"
    steps.append("structure-pass: OK")

    report = {
        "ts": None, "round": 463, "machine": "bm-a",
        "lane": "trial-labor W13 runner build / layer kit",
        "steps": steps,
        "anchor_head": {k: anchor[k] for k in (
            "n_bars", "decidable_days", "open_days", "closed_days",
            "sumn10_open_days", "first_decidable_bar_idx",
            "nine_gate_512cells_nonzero_count",
            "nine_gate_512cells_empty_count",
            "nine_gate_all_decidable_days")},
        "slope_sign_split": anchor["slope_sign_split"],
        "mirror_twin": anchor["mirror_twin"],
        "zero_coopen_exact_assert":
            anchor["zero_coopen_exact_assert"],
        "probe_sha256_head16": PROBE_SHA256_HEAD16,
        "next": "embed kit into W13 surgeon skeleton "
                "(W12 surgeon sections adapted; src="
                "scripts/trial_labor_w12.py) -> draft -> r446 "
                "three-command identity face -> selftest -> "
                "formal land scripts/trial_labor_w13.py -> "
                "catalog runner_exists flip + GENERATE pool entry",
    }
    return report, None


def main():
    import datetime
    rep, err = verify()
    if err is not None:
        print("KIT-FAIL: " + err)
        return 2
    rep["ts"] = datetime.datetime.now().astimezone().isoformat(
        timespec="seconds")
    json.dump(rep, open(REPORT, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("KIT-OK all steps green:")
    for s in rep["steps"]:
        print("  - " + s)
    print("report: " + REPORT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
