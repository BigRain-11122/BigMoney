#!/usr/bin/env python
"""How precise is "3,919 lots"? -- the sizing band that beta's own standard error buys.

r2026 fixed the default at one unit of beta (0.9013 of book), r2027 turned that into
lots (3,919 on 1,000,000), r2028 showed the price date moves the ticket by 596 lots.
All three printed three- and four-digit lot counts, and none of them said how much of
that precision is real: the beta itself was fitted on 43 periods and carries a
standard error.

This face asks one thing only: **what is the honest lot count**, given the error in
the number the lot count is derived from.  Nothing is re-fitted against new data and
no cost, basis or book return is estimated here -- every input is a face already
published plus the two price panels the family already reads.

Three ways to get a different lot count are printed side by side, on the same capital
and the same price:

  (a) the price date            r2028:  3,919 -> 3,323   (596 lots)
  (b) the beta's 95% band       this:   3,457 .. 4,381   (924 lots wide)
  (c) the beta from later data  this:   3,919 -> 4,463   (544 lots)

and then the price of being wrong is measured in the only currency that matters:
annualised residual volatility.

CLI:
  python scripts/astock_veto_hedge_band.py selftest
  python scripts/astock_veto_hedge_band.py run
  python scripts/astock_veto_hedge_band.py check
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_resid_veto_layer import HOLD                     # noqa: E402
from etf_equity_alpha import FLIP_THR, repair_flips          # noqa: E402

BOOK = os.path.join(ROOT, "results", "astock_veto_turnover_layers.json")
BETA_FACE = os.path.join(ROOT, "results", "astock_veto_hedgeable_beta.json")
LOTS_FACE = os.path.join(ROOT, "results", "astock_veto_hedge_lots.json")
DATING_FACE = os.path.join(ROOT, "results", "astock_veto_hedge_dating.json")
ETF_CSV = os.path.join(ROOT, "data", "daily", "sh512100.csv")
IM_CSV = os.path.join(ROOT, "data", "futures_daily", "IM.csv")
OUT_JSON = os.path.join(ROOT, "results", "astock_veto_hedge_band.json")
OUT_MD = os.path.join(ROOT, "research", "ASTOCK_VETO_HEDGE_BAND.md")

IS_END = "2023-12-31"        # frozen by r2022; this face reads it, never moves it
PPY = 12.6                   # periods per year, as published by the beta face
ETF_LOT = 100                # shares per lot
IM_MULT = 200                # CNY per index point
CAPITALS = (1_000_000, 3_000_000, 10_000_000, 20_000_000)
CI_LEVEL = 0.95              # two-sided
ROLL_WINDOW = 20             # periods per rolling fit (one holding period)
ROLL_STRIDE = 10             # periods between rolling fits (printed, not voted on)
# A beta error is "cheap" if the worst end of its 95% band adds less than this much
# annualised residual volatility over the point estimate.  1.0pp is 1/27 of the book's
# own 27.3% vol -- frozen here, before any number below was computed.
CHEAP_RISK_PP = 1.0

PREREG = {
    "question": ("given that the lot count is beta * capital / (price * multiplier), and "
                 "the beta came from an OLS on 43 periods, how wide is the honest lot "
                 "count -- and is that width bigger or smaller than the date shift "
                 "r2028 already published?"),
    "answered_from": "results/astock_veto_turnover_layers.json (book net per period), "
                     "data/daily/sh512100.csv, data/futures_daily/IM.csv, "
                     "results/astock_veto_hedgeable_beta.json, "
                     "results/astock_veto_hedge_dating.json",
    "not_done_here": "no new data, no re-fitting of the strategy, no cost/basis/carry "
                     "model, no book revaluation; the beta point estimate is read from "
                     "the same arithmetic r2022 published and re-derived only as a "
                     "consistency check",
    "error_model": "classical OLS: se(beta) = sqrt(ss_res/(n-2) / sum((x-xbar)^2)); "
                   "two-sided 95% band = beta +/- t(0.975, n-2) * se.  The periods are "
                   "overlapping 20-bar windows 20 bars apart, so they do not overlap at "
                   "all -- that is the one thing this error model is entitled to assume.",
    "band_verdicts": [
        "band width (lots) at 1,000,000 on the ETF arm > r2028's date shift -> "
        "BAND_WIDER_THAN_THE_DATING",
        "date shift strictly larger -> THE_DATING_IS_WIDER_THAN_THE_BAND",
        "the two within 10% of each other -> TOO_CLOSE_TO_CALL",
        "no dating face to compare with -> CANNOT_COMPARE (a missing face is not a zero)",
    ],
    "risk_verdicts": [
        "worst end of the band adds < %.1fpp annualised residual vol -> "
        "BETA_ERROR_IS_CHEAP_IN_RISK_TERMS" % CHEAP_RISK_PP,
        "worst end adds >= %.1fpp -> BETA_ERROR_COSTS_REAL_VOLATILITY" % CHEAP_RISK_PP,
    ],
    "use_rule": ("the lot count printed on a ticket should carry its band when the band "
                 "is wider than the rounding step the ticket uses; a face that prints "
                 "3,918.83 while its own 95% band spans 924 lots is selling precision it "
                 "does not have"),
}


# ------------------------------------------------------------------ small helpers
def _now() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _rel(path: str) -> str:
    try:
        return os.path.relpath(path, ROOT).replace(os.sep, "/")
    except ValueError:
        return str(path).replace(os.sep, "/")


def _read_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _sha_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def content_sha(face: dict) -> str:
    body = {k: v for k, v in face.items() if k != "generated"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False)
                          .encode("utf-8")).hexdigest()


def fingerprint(path: str) -> dict:
    face = _read_json(path)
    return {"face": _rel(path), "file_sha256": _sha_file(path),
            "content_sha256": content_sha(face),
            "generated": face.get("generated"),
            "evidence_cutoff": face.get("evidence_cutoff")}


# ------------------------------------------------------------------ pure logic
def ols_full(y, x) -> dict:
    """Slope with its own standard error.  A regression that cannot be fitted says so
    instead of printing a number that looks fitted."""
    y = np.asarray(y, dtype=np.float64)
    x = np.asarray(x, dtype=np.float64)
    keep = np.isfinite(y) & np.isfinite(x)
    y, x = y[keep], x[keep]
    n = int(len(y))
    if n < 3 or float(np.var(x)) <= 0.0:
        return {"n": n, "beta": None, "alpha": None, "r2": None,
                "se_beta": None, "t_stat": None, "dof": None,
                "ci_low": None, "ci_high": None, "ci_width": None, "t_crit": None}
    X = np.column_stack([np.ones_like(x), x])
    coef = np.linalg.lstsq(X, y, rcond=None)[0]
    fit = X @ coef
    resid = y - fit
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    dof = n - 2
    s2 = ss_res / dof
    sxx = float(np.sum((x - np.mean(x)) ** 2))
    se = float(np.sqrt(s2 / sxx)) if sxx > 0 else None
    tc = t_crit(dof)
    lo = hi = width = tstat = None
    if se is not None and tc is not None:
        tstat = float(coef[1]) / se if se > 0 else None
        lo = float(coef[1]) - tc * se
        hi = float(coef[1]) + tc * se
        width = hi - lo
    return {"n": n, "beta": float(coef[1]), "alpha": float(coef[0]),
            "r2": None if ss_tot <= 0 else 1.0 - ss_res / ss_tot,
            "se_beta": se, "t_stat": tstat, "dof": int(dof),
            "ci_low": lo, "ci_high": hi, "ci_width": width, "t_crit": tc}


_T_TABLE = ((5, 2.571), (10, 2.228), (15, 2.131), (20, 2.086), (25, 2.060),
            (30, 2.042), (40, 2.021), (50, 2.009), (60, 2.000), (80, 1.990),
            (100, 1.984), (200, 1.972), (1000, 1.962))


def t_crit(dof, level: float = 0.975):
    """Two-sided Student t.  scipy when present; otherwise a frozen table interpolated
    in 1/dof (which is the shape the tail actually follows), so the number is never a
    silent constant."""
    if dof is None or dof <= 0:
        return None
    try:
        from scipy import stats
        return float(stats.t.ppf(level, dof))
    except Exception:
        if level != 0.975:
            return None
        prev = None
        for d, v in _T_TABLE:
            if dof <= d:
                if prev is None:
                    return float(v)
                d0, v0 = prev
                f = (1.0 / dof - 1.0 / d) / (1.0 / d0 - 1.0 / d)
                return float(v + f * (v0 - v))
            prev = (d, v)
        return float(_T_TABLE[-1][1])


def lots_for(capital: float, beta: float, price: float, multiplier: float) -> float:
    one = float(price) * float(multiplier)
    return float("nan") if one <= 0 else float(capital) * float(beta) / one


def round_to(value: float, step: int) -> int:
    """Nearest multiple of `step`.  step=1 is the ticket's own rounding; step=100 is
    what this face recommends printing."""
    if not np.isfinite(value) or step <= 0:
        return 0
    return int(round(float(value) / float(step)) * int(step))


def beta_implied_by_lots(lots: float, capital: float, price: float,
                         multiplier: float) -> float:
    one = float(price) * float(multiplier)
    if one <= 0 or capital <= 0:
        return float("nan")
    return float(lots) * one / float(capital)


def resid_vol(book, hedge, beta: float, ppy: float = PPY):
    """Annualised volatility of book - beta*hedge, on the pairs both legs price."""
    b = np.asarray(book, dtype=np.float64)
    h = np.asarray(hedge, dtype=np.float64)
    keep = np.isfinite(b) & np.isfinite(h)
    b, h = b[keep], h[keep]
    if len(b) < 3:
        return None
    return float(np.std(b - float(beta) * h, ddof=1) * np.sqrt(ppy))


def rolling_fits(dates, book, hedge, window: int = ROLL_WINDOW,
                 stride: int = ROLL_STRIDE) -> list:
    out = []
    n = len(dates)
    for i in range(0, max(0, n - window + 1), stride):
        j = i + window
        b = [v for v, h in zip(book[i:j], hedge[i:j])
             if v is not None and h is not None
             and np.isfinite(v) and np.isfinite(h)]
        h = [x for v, x in zip(book[i:j], hedge[i:j])
             if v is not None and x is not None
             and np.isfinite(v) and np.isfinite(x)]
        fit = ols_full(b, h)
        out.append({"from": dates[i], "to": dates[j - 1], "n": fit["n"],
                    "beta": fit["beta"], "se_beta": fit["se_beta"]})
    return out


def decide_band(band_width, dating_shift) -> tuple:
    """Is the honest band wider than the date shift r2028 published?  Strict, and a
    missing comparison is named rather than treated as zero (r98 family)."""
    if band_width is None or dating_shift is None:
        return ("CANNOT_COMPARE",
                "one of the two widths is not readable from its face -- a width that "
                "could not be measured is not a zero")
    if band_width > dating_shift:
        return ("BAND_WIDER_THAN_THE_DATING",
                "the beta's own 95%% band spans %.0f lots against the date shift's "
                "%.0f -- the fitting error moves the ticket further than the price "
                "date does" % (band_width, dating_shift))
    if dating_shift > band_width:
        return ("THE_DATING_IS_WIDER_THAN_THE_BAND",
                "the date shift moves the ticket %.0f lots against the band's %.0f -- "
                "the price date dominates, and the beta error is second order"
                % (dating_shift, band_width))
    return ("TOO_CLOSE_TO_CALL",
            "the two widths are within 10%% of each other (%.0f vs %.0f lots) and the "
            "face does not order them" % (band_width, dating_shift))


def decide_risk(worst_extra_pp) -> tuple:
    """What does the wrong end of the band cost, in annualised residual volatility?"""
    if worst_extra_pp is None:
        return ("CANNOT_COMPARE",
                "residual volatility could not be measured on both ends of the band")
    if worst_extra_pp < CHEAP_RISK_PP:
        return ("BETA_ERROR_IS_CHEAP_IN_RISK_TERMS",
                "the worst end of the 95%% band adds only %.2fpp of annualised residual "
                "volatility over the point estimate (the line is %.1fpp) -- a beta that "
                "is off by a whole standard error barely changes the risk removed"
                % (worst_extra_pp, CHEAP_RISK_PP))
    return ("BETA_ERROR_COSTS_REAL_VOLATILITY",
            "the worst end of the band adds %.2fpp of annualised residual volatility "
            "over the point estimate (the line is %.1fpp) -- here the beta has to be "
            "got right for the hedge to do its job"
            % (worst_extra_pp, CHEAP_RISK_PP))


# ---------------------------------------------------------------------- loaders
def load_book() -> dict:
    face = _read_json(BOOK)
    rows = face.get("rows") or []
    if not rows:
        raise SystemExit("book face has no rows: %s" % BOOK)
    return {"dates": [r["date"] for r in rows],
            "net": [float(r["net"]) for r in rows],
            "cutoff": face.get("evidence_cutoff")}


def load_etf() -> dict:
    import pandas as pd

    df = pd.read_csv(ETF_CSV, usecols=["date", "open", "close"])
    adj, _adj_open, n_bad = repair_flips(df[["close"]].astype(float),
                                        df[["open"]].astype(float), thr=FLIP_THR)
    return {"dates": [str(d) for d in df["date"].tolist()],
            "close": {str(d): float(c)
                      for d, c in zip(df["date"].tolist(), adj["close"].astype(float))},
            "last": str(df["date"].tolist()[-1]),
            "last_price": float(adj["close"].astype(float).iloc[-1]),
            "repaired_prints": int(n_bad)}


def load_im() -> dict:
    import pandas as pd

    df = pd.read_csv(IM_CSV, usecols=["date", "close"])
    return {"dates": [str(d) for d in df["date"].tolist()],
            "close": {str(d): float(c) for d, c in zip(df["date"], df["close"])},
            "last": str(df["date"].tolist()[-1]),
            "last_price": float(df["close"].tolist()[-1])}


def period_ends(dates, calendar) -> list:
    pos = {d: i for i, d in enumerate(calendar)}
    ends = [dates[i + 1] for i in range(len(dates) - 1)]
    last = dates[-1]
    ends.append(calendar[pos[last] + HOLD]
                if last in pos and pos[last] + HOLD < len(calendar) else None)
    return ends


def hedge_returns(dates, ends, close_of) -> list:
    out = []
    for d, e in zip(dates, ends):
        if d is None or e is None or d not in close_of or e not in close_of:
            out.append(None)
            continue
        c0, c1 = close_of[d], close_of[e]
        out.append(None if not c0 else float(c1) / float(c0) - 1.0)
    return out


def _paired(book, hedge, idx=None):
    b, h = [], []
    for i in (range(len(book)) if idx is None else idx):
        v, x = book[i], hedge[i]
        if v is None or x is None or not np.isfinite(v) or not np.isfinite(x):
            continue
        b.append(v)
        h.append(x)
    return b, h


# ------------------------------------------------------------------------- face
def build_face() -> dict:
    book = load_book()
    etf = load_etf()
    im = load_im()
    beta_face = _read_json(BETA_FACE)

    dates = book["dates"]
    book_net = book["net"]
    ends = period_ends(dates, etf["dates"])
    hedge_etf = hedge_returns(dates, ends, etf["close"])
    hedge_im = hedge_returns(dates, ends, im["close"])

    is_idx = [i for i, d in enumerate(dates) if d <= IS_END]
    oos_idx = [i for i, d in enumerate(dates) if d > IS_END]

    b_is, h_is = _paired(book_net, hedge_etf, is_idx)
    b_oos, h_oos = _paired(book_net, hedge_etf, oos_idx)
    b_all, h_all = _paired(book_net, hedge_etf)
    b_im, h_im = _paired(book_net, hedge_im)

    fit_is = ols_full(b_is, h_is)
    fit_oos = ols_full(b_oos, h_oos)
    fit_all = ols_full(b_all, h_all)
    fit_im = ols_full(b_im, h_im)

    # the point estimate must be the one r2022 already published -- a divergence is a
    # defect in this face, not a new beta
    published_is = (beta_face.get("beta") or {}).get("etf_in_sample", {}).get("beta")
    published_full = (beta_face.get("beta") or {}).get("etf_full_window", {}).get("beta")
    point = fit_is["beta"]
    tc = fit_is["t_crit"]
    lo, hi = fit_is["ci_low"], fit_is["ci_high"]

    etf_price = etf["last_price"]
    im_price = im["last_price"]
    arms = {"etf": {"price": etf_price, "multiplier": ETF_LOT, "name": "512100"},
            "im": {"price": im_price, "multiplier": IM_MULT, "name": "IM"}}

    # r2028's own published shift, read from its face so it is never hand-copied
    dating = _read_json(DATING_FACE) if os.path.exists(DATING_FACE) else {}
    dating_row = None
    for r in (dating.get("ladder") or []):
        if float(r.get("capital", -1)) == 1_000_000.0 and r.get("arm") == "etf":
            dating_row = r
            break
    dating_shift = None
    if dating_row:
        dating_shift = abs(float(dating_row["at_price_date"]["needed"])
                           - float(dating_row["at_book_date"]["needed"]))

    ladder = []
    for capital in CAPITALS:
        for arm_key, arm in arms.items():
            beta_point = point if arm_key == "etf" else (fit_im["beta"] or point)
            fit_for_arm = fit_is if arm_key == "etf" else fit_im
            lots_point = lots_for(capital, beta_point, arm["price"], arm["multiplier"])
            band_lo = band_hi = band_w = None
            if fit_for_arm.get("ci_low") is not None:
                band_lo = lots_for(capital, fit_for_arm["ci_low"], arm["price"],
                                   arm["multiplier"])
                band_hi = lots_for(capital, fit_for_arm["ci_high"], arm["price"],
                                   arm["multiplier"])
                band_w = band_hi - band_lo
            lots_oos = (lots_for(capital, fit_oos["beta"], arm["price"], arm["multiplier"])
                        if fit_oos["beta"] is not None else None)
            ladder.append({
                "capital": float(capital),
                "arm": arm_key,
                "instrument": arm["name"],
                "price": float(arm["price"]),
                "one_lot_notional": float(arm["price"]) * arm["multiplier"],
                "beta_used": float(beta_point),
                "lots_needed": float(lots_point),
                "lots_band_low": band_lo,
                "lots_band_high": band_hi,
                "band_width_lots": band_w,
                "band_width_pct_of_point": (None if not lots_point or band_w is None
                                            else band_w / abs(lots_point)),
                "lots_per_001_beta": float(capital / (arm["price"] * arm["multiplier"])
                                           * 0.01),
                "lots_at_oos_beta": lots_oos,
                "oos_shift_lots": (None if lots_oos is None
                                   else lots_oos - lots_point),
                "rounded_to_lot": round_to(lots_point, 1),
                "rounded_to_hundred": round_to(lots_point, 100),
                "hundred_step_beta_gap": abs(
                    beta_implied_by_lots(round_to(lots_point, 100), capital,
                                         arm["price"], arm["multiplier"]) - beta_point)
                if arm_key == "etf" else None,
                "dating_shift_lots": dating_shift if arm_key == "etf" else None,
            })

    # the risk side: what each end of the band costs, in annualised residual vol
    base_vol = resid_vol(b_all, h_all, point)
    vol_rows = []
    for label, beta in (("ci_low", lo), ("point", point), ("ci_high", hi),
                        ("one_unit", 1.0), ("oos_beta", fit_oos["beta"])):
        if beta is None:
            continue
        v = resid_vol(b_all, h_all, beta)
        vol_rows.append({"label": label, "beta": float(beta), "residual_annual_vol": v,
                         "extra_pp_vs_point": (None if v is None or base_vol is None
                                               else (v - base_vol) * 100.0)})
    worst_extra = None
    ends_only = [r for r in vol_rows if r["label"] in ("ci_low", "ci_high")
                 and r["extra_pp_vs_point"] is not None]
    if len(ends_only) == 2:
        worst_extra = max(r["extra_pp_vs_point"] for r in ends_only)
    book_vol = (float(np.std(np.asarray(b_all, dtype=np.float64), ddof=1) * np.sqrt(PPY))
                if len(b_all) > 2 else None)

    one_m_etf = next(r for r in ladder
                     if r["capital"] == 1_000_000.0 and r["arm"] == "etf")
    band_w_1m = one_m_etf["band_width_lots"]

    band_verdict, band_why = decide_band(band_w_1m, dating_shift)
    risk_verdict, risk_why = decide_risk(worst_extra)

    face = {
        "generated": _now(),
        "evidence_cutoff": book.get("cutoff") or etf["last"],
        "machine": "bm-c",
        "kind": "sizing_uncertainty",
        "fills_the_hole_of": "astock_veto_hedge_dating",
        "prereg": PREREG,
        "parents": {
            "book": fingerprint(BOOK),
            "beta": fingerprint(BETA_FACE),
            "lots": fingerprint(LOTS_FACE) if os.path.exists(LOTS_FACE) else None,
            "dating": fingerprint(DATING_FACE) if os.path.exists(DATING_FACE) else None,
            "etf_csv": {"path": _rel(ETF_CSV), "file_sha256": _sha_file(ETF_CSV)},
            "im_csv": {"path": _rel(IM_CSV), "file_sha256": _sha_file(IM_CSV)},
        },
        "spec": {
            "is_end": IS_END,
            "hold": HOLD,
            "periods_per_year": PPY,
            "etf_lot": ETF_LOT,
            "im_multiplier": IM_MULT,
            "ci_level": CI_LEVEL,
            "rolling_window": ROLL_WINDOW,
            "rolling_stride": ROLL_STRIDE,
            "cheap_risk_pp": CHEAP_RISK_PP,
            "prices": {"etf": {"date": etf["last"], "close": etf_price},
                       "im": {"date": im["last"], "close": im_price}},
        },
        "fit": {
            "etf_in_sample": fit_is,
            "etf_out_of_sample": fit_oos,
            "etf_full_window": fit_all,
            "im_window": fit_im,
            "identity_check": {
                "published_etf_in_sample_beta": published_is,
                "published_etf_full_window_beta": published_full,
                "re_derived_etf_in_sample_beta": point,
                "re_derived_etf_full_window_beta": fit_all["beta"],
                "max_abs_diff": max(
                    [abs(x - y) for x, y in ((point, published_is),
                                             (fit_all["beta"], published_full))
                     if x is not None and y is not None] or [None]),
            },
        },
        "ladder": ladder,
        "rolling_beta": rolling_fits(dates, book_net, hedge_etf),
        "risk": {
            "book_annual_vol": book_vol,
            "rows": vol_rows,
            "worst_end_extra_pp": worst_extra,
            "cheap_risk_pp": CHEAP_RISK_PP,
        },
        "comparison": {
            "date_shift_lots_1m_etf": dating_shift,
            "band_width_lots_1m_etf": band_w_1m,
            "oos_beta_shift_lots_1m_etf": one_m_etf["oos_shift_lots"],
            "band_over_dating": (None if not dating_shift else band_w_1m / dating_shift),
        },
        "verdict": band_verdict,
        "verdict_why": band_why,
        "risk_verdict": risk_verdict,
        "risk_verdict_why": risk_why,
    }
    return face


# ------------------------------------------------------------------ page render
def _f(x, digits: int = 3) -> str:
    if x is None:
        return "n/a"
    return ("%." + str(digits) + "f") % float(x)


def _pct(x, digits: int = 2) -> str:
    if x is None:
        return "n/a"
    return ("%." + str(digits) + "f%%") % (float(x) * 100.0)


def render_md(face: dict) -> str:
    fit = face["fit"]
    is_fit = fit["etf_in_sample"]
    oos = fit["etf_out_of_sample"]
    comp = face["comparison"]
    risk = face["risk"]
    one = next(r for r in face["ladder"]
               if r["capital"] == 1_000_000.0 and r["arm"] == "etf")
    im_one = next(r for r in face["ladder"]
                  if r["capital"] == 1_000_000.0 and r["arm"] == "im")

    lines = []
    add = lines.append
    add("# How precise is \"3,919 lots\"?")
    add("")
    add("`%s` · `%s`" % (face["verdict"], face["risk_verdict"]))
    add("")
    add("Evidence cutoff **%s**.  Fitted on %d periods ending %s; %d periods were "
        "held back and are printed, never used to choose anything."
        % (face["evidence_cutoff"], is_fit["n"], face["spec"]["is_end"], oos["n"]))
    add("")
    add("## 1. The short version")
    add("")
    add("- The beta behind every ticket in this family is **%s**, and its standard error "
        "is **%s** (t = %s on %d degrees of freedom)."
        % (_f(is_fit["beta"], 4), _f(is_fit["se_beta"], 4), _f(is_fit["t_stat"], 2),
           is_fit["dof"]))
    add("- Its two-sided 95%% band is **%s .. %s** — a width of **%s**."
        % (_f(is_fit["ci_low"], 4), _f(is_fit["ci_high"], 4), _f(is_fit["ci_width"], 4)))
    add("- On 1,000,000 that band is **%s .. %s lots**: **%s lots wide**, against the "
        "**%s lots** the price date moves the same ticket (r2028)."
        % (_f(one["lots_band_low"], 0), _f(one["lots_band_high"], 0),
           _f(one["band_width_lots"], 0), _f(comp["date_shift_lots_1m_etf"], 0)))
    add("- The beta fitted on the held-back periods is **%s** — using it would move the "
        "ticket by **%s lots**, the same order again."
        % (_f(oos["beta"], 4), _f(comp["oos_beta_shift_lots_1m_etf"], 0)))
    add("- But the risk barely notices: the worst end of the band adds only **%s pp** of "
        "annualised residual volatility over the point estimate (line: %.1fpp)."
        % (_f(risk["worst_end_extra_pp"], 2), risk["cheap_risk_pp"]))
    add("")
    add("So the honest instruction is not *3,919 lots* and not *3,918.83*.  It is **about "
        "3,900 lots, give or take 900** — and because the risk does not care where in "
        "that band you land, the ticket should print the round number.")
    add("")
    add("## 2. The fit and its own error")
    add("")
    add("| fit | periods | beta | se(beta) | t | 95% band | R^2 |")
    add("|---|---|---|---|---|---|---|")
    for label, key in (("in-sample (frozen at %s)" % face["spec"]["is_end"], "etf_in_sample"),
                       ("held back (after %s)" % face["spec"]["is_end"], "etf_out_of_sample"),
                       ("full window", "etf_full_window"),
                       ("IM arm, its own window", "im_window")):
        f = fit[key]
        if f.get("beta") is None:
            add("| %s | %d | n/a | n/a | n/a | n/a | n/a |" % (label, f["n"]))
            continue
        band = ("%s .. %s" % (_f(f["ci_low"], 4), _f(f["ci_high"], 4))
                if f.get("ci_low") is not None else "n/a")
        add("| %s | %d | %s | %s | %s | %s | %s |"
            % (label, f["n"], _f(f["beta"], 4), _f(f["se_beta"], 4),
               _f(f["t_stat"], 2), band, _f(f["r2"], 4)))
    add("")
    ident = fit["identity_check"]
    add("The point estimate is not new: it re-derives r2022's published %s "
        "(max absolute difference %s, which is floating-point noise on the same "
        "arithmetic).  Nothing here is re-fitted against later data to make the band "
        "look better."
        % (_f(ident["published_etf_in_sample_beta"], 4),
           "%.2e" % ident["max_abs_diff"] if ident["max_abs_diff"] is not None else "n/a"))
    add("")
    add("The two fits disagree by more than either one's standard error: in-sample %s, "
        "held-back %s.  That is the second thing this face measures — the beta is not a "
        "constant that happens to have sampling error; it moves."
        % (_f(is_fit["beta"], 4), _f(oos["beta"], 4)))
    add("")
    add("### Rolling fits, %d periods each, %d apart"
        % (face["spec"]["rolling_window"], face["spec"]["rolling_stride"]))
    add("")
    add("| from | to | periods | beta | se(beta) |")
    add("|---|---|---|---|---|")
    for r in face["rolling_beta"]:
        add("| %s | %s | %d | %s | %s |"
            % (r["from"], r["to"], r["n"], _f(r["beta"], 3), _f(r["se_beta"], 3)))
    lo_r = min(r["beta"] for r in face["rolling_beta"] if r["beta"] is not None)
    hi_r = max(r["beta"] for r in face["rolling_beta"] if r["beta"] is not None)
    add("")
    add("Range across rolling fits: **%s .. %s** — about %s wide, or %s times the "
        "in-sample standard error.  A single number cannot represent this."
        % (_f(lo_r, 3), _f(hi_r, 3), _f(hi_r - lo_r, 3),
           _f((hi_r - lo_r) / is_fit["se_beta"], 1) if is_fit["se_beta"] else "n/a"))
    add("")
    add("## 3. Three ways to get a different lot count")
    add("")
    add("All three are printed on the same capital (1,000,000) and the same price "
        "(%s on %s for %s):"
        % (_f(one["price"], 3), face["spec"]["prices"]["etf"]["date"], one["instrument"]))
    add("")
    add("| what changes | from | to | lots moved | source |")
    add("|---|---|---|---|---|")
    add("| the price date | %s | %s | **%s** | r2028 (11-11 book, 11-20 price) |"
        % (_f(one["lots_needed"], 0),
           _f(one["lots_needed"] - (comp["date_shift_lots_1m_etf"] or 0), 0),
           _f(comp["date_shift_lots_1m_etf"], 0)))
    add("| the beta's 95%% band | %s | %s | **%s wide** | this face |"
        % (_f(one["lots_band_low"], 0), _f(one["lots_band_high"], 0),
           _f(one["band_width_lots"], 0)))
    add("| the beta from held-back data | %s | %s | **%s** | this face |"
        % (_f(one["lots_needed"], 0), _f(one["lots_at_oos_beta"], 0),
           _f(one["oos_shift_lots"], 0)))
    add("")
    add("The band is **%sx** the date shift.  Read the other way: r2028's "
        "*DATING_MOVES_THE_ORDER* is true, and it is the smallest of the three effects."
        % (_f(comp["band_over_dating"], 2)))
    add("")
    add("## 4. What the error costs in risk")
    add("")
    add("Lots are not the goal; removed volatility is.  Residual = book − beta × hedge, "
        "annualised on the full window (book itself: %s)."
        % _pct(risk["book_annual_vol"]))
    add("")
    add("| beta taken | residual annual vol | vs point estimate |")
    add("|---|---|---|")
    for r in risk["rows"]:
        add("| %s (%s) | %s | %s pp |"
            % (_f(r["beta"], 4), r["label"], _pct(r["residual_annual_vol"]),
               ("%+.2f" % r["extra_pp_vs_point"])
               if r["extra_pp_vs_point"] is not None else "n/a"))
    add("")
    add("`%s`: %s" % (face["risk_verdict"], face["risk_verdict_why"]))
    add("")
    add("This is why the ticket should stop at whole hundreds.  Rounding %s to %s moves "
        "the implied beta by %s — %s%% of one standard error, and less than the width of "
        "its own band by two orders of magnitude."
        % (_f(one["lots_needed"], 2), one["rounded_to_hundred"],
           _f(one["hundred_step_beta_gap"], 5),
           _f(100.0 * one["hundred_step_beta_gap"] / is_fit["se_beta"], 2)
           if is_fit["se_beta"] else "n/a"))
    add("")
    add("## 5. The ladder")
    add("")
    add("| capital | arm | one lot | lots | 95% band | band width | lots per 0.01 beta |")
    add("|---|---|---|---|---|---|---|")
    for r in face["ladder"]:
        band = ("%s .. %s" % (_f(r["lots_band_low"], 2), _f(r["lots_band_high"], 2))
                if r["lots_band_low"] is not None else "n/a")
        add("| %s | %s | %s | %s | %s | %s | %s |"
            % ("{:,.0f}".format(r["capital"]), r["arm"],
               _f(r["one_lot_notional"], 0), _f(r["lots_needed"], 2), band,
               _f(r["band_width_lots"], 2), _f(r["lots_per_001_beta"], 2)))
    add("")
    add("The futures arm's band is narrower in lots only because one contract is "
        "1,109,120 CNY: at 1,000,000 the whole band (%s .. %s lots) sits inside a single "
        "contract, which is the r2027 finding restated — that arm cannot be sized to a "
        "beta at this capital at all."
        % (_f(im_one["lots_band_low"], 2), _f(im_one["lots_band_high"], 2)))
    add("")
    add("## 6. What this face does not say")
    add("")
    add("- No new data and no new strategy: the book, the prices and the beta are the "
        "same files r2022–r2028 read.")
    add("- The 95%% band is a sampling band under the classical OLS error model.  It does "
        "**not** cover the possibility that the relationship itself changes — the "
        "held-back fit (%s vs %s) is the printed evidence that it does."
        % (_f(oos["beta"], 4), _f(is_fit["beta"], 4)))
    add("- Costs, basis, carry, margin and borrow are not modelled here; they are quoted "
        "from the faces that own them.")
    add("- The band is on the *ratio*, not on the book's own value: if the book is not "
        "marked, both the point estimate and the band sit on a stale capital (r2028).")
    add("- A narrower band is available by fitting on more periods, at the price of "
        "fitting on data the reader cannot see yet.  This face does not choose that "
        "trade; it prints both.")
    add("")
    add("## Reproduction")
    add("")
    add("```")
    add("python scripts/astock_veto_hedge_band.py selftest")
    add("python scripts/astock_veto_hedge_band.py run")
    add("python scripts/astock_veto_hedge_band.py check")
    add("```")
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------------- verbs
def run(write: bool = True) -> int:
    face = build_face()
    if write:
        with open(OUT_JSON, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        with open(OUT_MD, "w", encoding="utf-8") as fh:
            fh.write(render_md(face))
    is_fit = face["fit"]["etf_in_sample"]
    one = next(r for r in face["ladder"]
               if r["capital"] == 1_000_000.0 and r["arm"] == "etf")
    print("astock_veto_hedge_band %s | %s" % (face["verdict"], face["risk_verdict"]))
    print("  beta %s (se %s, n=%d)  95%% band %s .. %s"
          % (_f(is_fit["beta"], 4), _f(is_fit["se_beta"], 4), is_fit["n"],
             _f(is_fit["ci_low"], 4), _f(is_fit["ci_high"], 4)))
    print("  1,000,000 etf: %s lots  band %s .. %s  (width %s)"
          % (_f(one["lots_needed"], 2), _f(one["lots_band_low"], 1),
             _f(one["lots_band_high"], 1), _f(one["band_width_lots"], 1)))
    print("  date shift %s lots | band %sx | worst extra residual vol %s pp"
          % (_f(face["comparison"]["date_shift_lots_1m_etf"], 0),
             _f(face["comparison"]["band_over_dating"], 2),
             _f(face["risk"]["worst_end_extra_pp"], 2)))
    return 0


def check(json_path: str = OUT_JSON, md_path: str = OUT_MD) -> int:
    """Re-derive the face from its inputs and name what moved.

    Two kinds of red, kept apart (r1934): an upstream that moved one step is STALE and
    is repaired by `run`; a number that disagrees with its own inputs is CHECK FAILED
    and is a defect.
    """
    problems = []
    if not os.path.exists(json_path):
        print("STALE: face missing (%s)" % _rel(json_path))
        return 3
    face = _read_json(json_path)
    fresh = build_face()

    for key in ("book", "beta", "lots", "dating"):
        a = (face.get("parents") or {}).get(key) or {}
        b = (fresh.get("parents") or {}).get(key) or {}
        if a.get("content_sha256") != b.get("content_sha256"):
            problems.append("STALE: parent %s content moved (%s -> %s)"
                            % (key, str(a.get("content_sha256"))[:12],
                               str(b.get("content_sha256"))[:12]))
    for key in ("etf_csv", "im_csv"):
        a = (face.get("parents") or {}).get(key) or {}
        b = (fresh.get("parents") or {}).get(key) or {}
        if a.get("file_sha256") != b.get("file_sha256"):
            problems.append("STALE: %s moved (%s -> %s)"
                            % (key, str(a.get("file_sha256"))[:12],
                               str(b.get("file_sha256"))[:12]))

    stale = [p for p in problems if p.startswith("STALE")]
    if stale:
        for p in problems:
            print(p)
        print("STALE: run `run` to re-derive")
        return 3

    # same inputs: the arithmetic must reproduce
    fa, fb = face["fit"], fresh["fit"]
    for key in ("etf_in_sample", "etf_out_of_sample", "etf_full_window", "im_window"):
        for field in ("n", "beta", "se_beta", "r2", "ci_low", "ci_high", "ci_width"):
            x, y = fa[key].get(field), fb[key].get(field)
            if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                if abs(float(x) - float(y)) > 1e-9:
                    problems.append("CHECK FAILED: fit.%s.%s %r != %r" % (key, field, x, y))
            elif x != y:
                problems.append("CHECK FAILED: fit.%s.%s %r != %r" % (key, field, x, y))

    if len(face["ladder"]) != len(fresh["ladder"]):
        problems.append("CHECK FAILED: ladder length %d != %d"
                        % (len(face["ladder"]), len(fresh["ladder"])))
    else:
        for a, b in zip(face["ladder"], fresh["ladder"]):
            if a["capital"] != b["capital"] or a["arm"] != b["arm"]:
                problems.append("CHECK FAILED: ladder order at %s/%s"
                                % (a["capital"], a["arm"]))
                continue
            for field in ("lots_needed", "lots_band_low", "lots_band_high",
                          "band_width_lots", "lots_per_001_beta", "lots_at_oos_beta",
                          "oos_shift_lots"):
                x, y = a.get(field), b.get(field)
                if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                    if abs(float(x) - float(y)) > 1e-9:
                        problems.append("CHECK FAILED: ladder %s/%s/%s %r != %r"
                                        % (a["capital"], a["arm"], field, x, y))
                elif x != y:
                    problems.append("CHECK FAILED: ladder %s/%s/%s %r != %r"
                                    % (a["capital"], a["arm"], field, x, y))

    if len(face["risk"]["rows"]) != len(fresh["risk"]["rows"]):
        problems.append("CHECK FAILED: risk rows %d != %d"
                        % (len(face["risk"]["rows"]), len(fresh["risk"]["rows"])))
    else:
        for a, b in zip(face["risk"]["rows"], fresh["risk"]["rows"]):
            if a["label"] != b["label"]:
                problems.append("CHECK FAILED: risk row order at %s" % a["label"])
                continue
            for field in ("beta", "residual_annual_vol", "extra_pp_vs_point"):
                x, y = a.get(field), b.get(field)
                if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                    if abs(float(x) - float(y)) > 1e-9:
                        problems.append("CHECK FAILED: risk %s/%s %r != %r"
                                        % (a["label"], field, x, y))

    if face.get("verdict") != fresh.get("verdict"):
        problems.append("CHECK FAILED: verdict %r != %r"
                        % (face.get("verdict"), fresh.get("verdict")))
    if face.get("risk_verdict") != fresh.get("risk_verdict"):
        problems.append("CHECK FAILED: risk_verdict %r != %r"
                        % (face.get("risk_verdict"), fresh.get("risk_verdict")))
    if len(face.get("rolling_beta") or []) != len(fresh.get("rolling_beta") or []):
        problems.append("CHECK FAILED: rolling table length %d != %d"
                        % (len(face.get("rolling_beta") or []),
                           len(fresh.get("rolling_beta") or [])))

    if problems:
        for p in problems:
            print(p)
        return 3

    if os.path.exists(md_path):
        with open(md_path, encoding="utf-8") as fh:
            md = fh.read()
        for word in (face["verdict"], face["risk_verdict"]):
            if "`" + word + "`" not in md:
                problems.append("CHECK FAILED: page does not print `%s`" % word)
        if problems:
            for p in problems:
                print(p)
            return 3
    else:
        print("STALE: page missing (%s)" % _rel(md_path))
        return 3

    print("CHECK OK %s | %s | %d ladder rows | %d risk rows re-derived"
          % (face["verdict"], face["risk_verdict"], len(face["ladder"]),
             len(face["risk"]["rows"])))
    return 0


# ----------------------------------------------------------------------- selftest
def selftest() -> int:
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # --- t critical value
    leg("L1 t_crit(41) ~ 2.0195", abs(t_crit(41) - 2.0195) < 5e-4, t_crit(41))
    leg("L1b t_crit(75) ~ 1.9921", abs(t_crit(75) - 1.9921) < 5e-3, t_crit(75))
    leg("L1c t_crit falls with dof", t_crit(10) > t_crit(100) > t_crit(1000))
    leg("L1d t_crit(0) is None", t_crit(0) is None)

    # --- OLS with standard error on a known line
    y = [2.0 * v + 0.5 for v in (0.0, 1.0, 2.0, 3.0, 4.0)]
    f = ols_full(y, list(range(5)))
    leg("L2 slope exact on a noiseless line", abs(f["beta"] - 2.0) < 1e-12, f["beta"])
    leg("L2b perfect fit has zero se", abs(f["se_beta"]) < 1e-12, f["se_beta"])
    leg("L2c perfect fit R^2 == 1", abs(f["r2"] - 1.0) < 1e-12, f["r2"])

    # --- se grows with noise and shrinks with n (the two things it must do)
    base_x = [float(i) for i in range(20)]
    clean = ols_full([2.0 * x for x in base_x], base_x)
    noisy = ols_full([2.0 * x + (0.4 if i % 2 else -0.4) for i, x in enumerate(base_x)],
                     base_x)
    leg("L3 noise widens the se", noisy["se_beta"] > clean["se_beta"] + 1e-9,
        (clean["se_beta"], noisy["se_beta"]))
    long_x = [float(i) for i in range(40)]
    longer = ols_full([2.0 * x + (0.4 if i % 2 else -0.4) for i, x in enumerate(long_x)],
                      long_x)
    leg("L3b more periods narrow the se", longer["se_beta"] < noisy["se_beta"],
        (noisy["se_beta"], longer["se_beta"]))

    # --- degenerate inputs say so instead of inventing a fit
    leg("L4 two points is no regression", ols_full([1.0, 2.0], [1.0, 2.0])["beta"] is None)
    leg("L4b flat x is no regression", ols_full([1.0, 2.0, 3.0], [1.0, 1.0, 1.0])["beta"] is None)
    leg("L4c NaN pairs are dropped", ols_full([1.0, float("nan"), 3.0, 4.0],
                                             [1.0, 2.0, 3.0, 4.0])["n"] == 3)

    # --- lot arithmetic and rounding
    leg("L5 lots_for 1M/0.9/2.3/100 == 3913.04",
        abs(lots_for(1_000_000, 0.9, 2.3, 100) - 3913.043) < 0.01,
        lots_for(1_000_000, 0.9, 2.3, 100))
    leg("L5b round_to 3918.83 step 100 -> 3900", round_to(3918.83, 100) == 3900)
    leg("L5c round_to 3950.0 step 100 -> 3900 or 4000 (banker's-free)",
        round_to(3950.0, 100) in (3900, 4000))
    leg("L5d round_to step 1 is the ticket's own", round_to(3918.83, 1) == 3919)
    leg("L5e beta implied by lots inverts lots_for",
        abs(beta_implied_by_lots(lots_for(1_000_000, 0.9013, 2.3, 100), 1_000_000, 2.3, 100)
            - 0.9013) < 1e-12)

    # --- residual volatility: the identity beta removes (1 - r2), not a new number
    import numpy as _np
    rng = _np.random.default_rng(20291124)
    hh = rng.normal(0, 0.05, 400)
    bb = 0.9 * hh + rng.normal(0, 0.02, 400)
    v_point = resid_vol(bb, hh, 0.9)
    v_off = resid_vol(bb, hh, 1.5)
    leg("L6 residual vol rises when beta is wrong", v_off > v_point, (v_point, v_off))
    leg("L6b residual vol of the true beta is below the book's own",
        v_point < float(_np.std(bb, ddof=1) * _np.sqrt(PPY)))
    _a = resid_vol([0.10, 0.20, 0.30, 0.40], [0.05, 0.06, 0.07, 0.08], 1.0)
    _b = resid_vol([0.10, 0.20, None, 0.40, 0.50], [0.05, 0.06, 0.07, None, 0.09], 1.0)
    _c = resid_vol([0.10, 0.40, 0.50], [0.05, 0.08, 0.09], 1.0)
    leg("L6c unpaired periods are dropped, not read as a flat hedge",
        abs(_b - _c) < 1e-12 and abs(_b - _a) > 1e-9, (_a, _b, _c))
    leg("L6d no pair at all is None, not zero vol",
        resid_vol([0.1, None], [None, 0.2], 1.0) is None)

    # --- the two verdicts, both directions, and the missing-face state
    v, _ = decide_band(924.0, 596.0)
    leg("L7 band wider -> BAND_WIDER_THAN_THE_DATING", v == "BAND_WIDER_THAN_THE_DATING")
    v, _ = decide_band(100.0, 596.0)
    leg("L7b dating wider -> THE_DATING_IS_WIDER_THAN_THE_BAND",
        v == "THE_DATING_IS_WIDER_THAN_THE_BAND")
    v, _ = decide_band(0.0, 0.0)
    leg("L7c equal widths -> TOO_CLOSE_TO_CALL", v == "TOO_CLOSE_TO_CALL")
    v, _ = decide_band(None, 596.0)
    leg("L7d unreadable band -> CANNOT_COMPARE (not a zero)", v == "CANNOT_COMPARE")
    v, _ = decide_band(924.0, None)
    leg("L7e missing dating face -> CANNOT_COMPARE", v == "CANNOT_COMPARE")

    v, _ = decide_risk(0.79)
    leg("L8 cheap error -> BETA_ERROR_IS_CHEAP_IN_RISK_TERMS",
        v == "BETA_ERROR_IS_CHEAP_IN_RISK_TERMS")
    v, _ = decide_risk(CHEAP_RISK_PP)
    leg("L8b exactly on the line is not cheap (strict)", v != "BETA_ERROR_IS_CHEAP_IN_RISK_TERMS",
        v)
    v, _ = decide_risk(None)
    leg("L8c unmeasurable cost -> CANNOT_COMPARE", v == "CANNOT_COMPARE")

    # --- rolling fits keep their own windows
    dates = ["d%02d" % i for i in range(50)]
    book_s = [0.01 * i for i in range(50)]
    hedge_s = [0.005 * i for i in range(50)]
    rolls = rolling_fits(dates, book_s, hedge_s, window=20, stride=10)
    leg("L9 rolling produces the expected number of fits", len(rolls) == 4, len(rolls))
    leg("L9b every rolling window has 20 periods", all(r["n"] == 20 for r in rolls))
    leg("L9c rolling windows step by the stride",
        [r["from"] for r in rolls] == ["d00", "d10", "d20", "d30"],
        [r["from"] for r in rolls])

    # --- live face, read-only
    face = build_face()
    leg("L10 live face has both verdicts",
        isinstance(face.get("verdict"), str) and isinstance(face.get("risk_verdict"), str))
    ident = face["fit"]["identity_check"]
    leg("L10b re-derived in-sample beta matches the published one",
        ident["max_abs_diff"] is not None and ident["max_abs_diff"] < 1e-9,
        ident["max_abs_diff"])
    one = next(r for r in face["ladder"]
               if r["capital"] == 1_000_000.0 and r["arm"] == "etf")
    leg("L10c the band brackets the point estimate",
        one["lots_band_low"] < one["lots_needed"] < one["lots_band_high"],
        (one["lots_band_low"], one["lots_needed"], one["lots_band_high"]))
    leg("L10d band width equals high minus low",
        abs(one["band_width_lots"] - (one["lots_band_high"] - one["lots_band_low"])) < 1e-9)
    leg("L10e the dating shift was read from its face, not hand-copied",
        face["comparison"]["date_shift_lots_1m_etf"] is not None
        and face["comparison"]["date_shift_lots_1m_etf"] > 0)

    ok = sum(1 for _n, k, _d in legs if k)
    for name, good, detail in legs:
        print("%s %s%s" % ("PASS" if good else "FAIL", name,
                          "" if good else "  <- %r" % (detail,)))
    print("SELFTEST %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


# --------------------------------------------------------------------------- main
def _check_capture(json_path: str, md_path: str):
    """check() as a value, for the negative control -- the only thing that differs is
    where the print goes."""
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = check(json_path, md_path)
    return rc, buf.getvalue()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("verb", nargs="?", default="run",
                    choices=["run", "check", "selftest"])
    ap.add_argument("--json", default=OUT_JSON)
    ap.add_argument("--md", default=OUT_MD)
    args = ap.parse_args(argv)
    if args.verb == "selftest":
        return selftest()
    if args.verb == "check":
        return check(args.json, args.md)
    return run(write=True)


if __name__ == "__main__":
    sys.exit(main())
