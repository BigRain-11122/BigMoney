"""Spanning test: is the shipped ETF book a ranking skill, or a basket of liquid betas?

r1305 found the composite's edge is period-bound (pre-2020 it loses to equal weight) and
r1306 found the commodity sleeve's excess is mostly its own beta. This asks the question a
funder asks before wiring money: after the four liquid exposures the account could hold
instead of this book -- gold, US tech (QDII), broad A-share, government bond -- does the
book's daily return still have an intercept?

Method (all on the book's own execution basis, close t decision -> open t+1 fill, 10bp/side,
8% de-lever-only overlay, exactly the published configuration read off the card):

    r_book(t) = a + sum_k b_k * r_span_k(t) + e(t)

  * `a` is annualised (a*252) and reported with its t-stat; a t below 2 means the book's
    return is not distinguishable from a fixed loadings mix of the span assets.
  * R^2 says how much of the book's daily variance the span already explains.
  * The same regression is refit on the IS window and applied to OOS (walk-forward, no
    lookahead) so the alpha quoted for the forward window is not fitted on it.
  * The span assets are also priced as *portfolios* over the same window (each one alone,
    and an equal-weight basket rebalanced on the book's own 20-bar grid) so the headline
    has a comparison a reader can hold instead of a coefficient.

Every number is printed with the window it belongs to. A coefficient without its window is
not a result (E95/E98 class).
"""

import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import etf_book_production as P  # noqa: E402
import etf_equity_alpha as A  # noqa: E402

RESULT = os.path.join(P.E.PATHS.data_dir, "..", "results", "etf_book_spanning.json")

# The four exposures the account could hold instead of the book. Codes are the panel's
# bare 6-digit form; etf_composite_pf keys each instrument once across its two file names.
SPAN = [
    ("gold", "518880", "gold ETF"),
    ("us_tech", "513100", "Nasdaq-100 QDII ETF"),
    ("csi300", "510300", "CSI 300 ETF"),
    ("bond", "511010", "treasury bond ETF"),
]


def card_config(default=(12, 20, 0.08)):
    """Read the shipped configuration off the production card, never a hardcoded copy.

    r1288 class: a consumer that repeats the card's numbers as literals drifts silently the
    first time the card changes. Falls back to the documented default only when the card is
    unreadable, and says so in the output.
    """
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                     "etf_book_production", "latest.json")
    try:
        with open(p, encoding="utf-8") as f:
            cfg = json.load(f).get("config") or {}
        n = int(cfg.get("n_hold"))
        r = int(cfg.get("rebal"))
        vt = float(cfg.get("vol_target"))
        return n, r, vt, "results/etf_book_production/latest.json"
    except Exception:
        return default[0], default[1], default[2], "fallback default (card unreadable)"


def ols(y, X):
    """Plain OLS with intercept. Returns coefficients, t-stats, R^2 and n.

    No HAC correction: the regressand is a daily return, not an overlapping multi-day
    return, so the main overlap problem this repo has hit before does not apply. The caveat
    is printed on the face rather than fixed silently.
    """
    y = np.asarray(y, dtype=float)
    X = np.asarray(X, dtype=float)
    n, k = X.shape
    if n <= k + 1:
        return None
    if k and np.any(X.std(axis=0) <= 0.0):
        # a constant regressor makes the system singular; refuse rather than let
        # pinv hand back an arbitrary attribution (r1261: never read a degenerate run)
        return None
    D = np.column_stack([np.ones(n), X])
    beta, *_ = np.linalg.lstsq(D, y, rcond=None)
    resid = y - D @ beta
    dof = n - D.shape[1]
    if dof <= 0:
        return None
    s2 = float(resid @ resid) / dof
    XtX_inv = np.linalg.pinv(D.T @ D)
    se = np.sqrt(np.maximum(np.diag(XtX_inv) * s2, 0.0))
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - float(resid @ resid) / ss_tot if ss_tot > 0 else float("nan")
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.where(se > 0, beta / se, np.nan)
    return {"alpha": float(beta[0]), "betas": [float(b) for b in beta[1:]],
            "t": [float(v) for v in t], "r2": float(r2), "n_obs": int(n),
            "resid_sd_daily": float(np.sqrt(s2))}


def load_span_frames(span=None, data_dir=None, repair=True):
    """Close/open price frames for the span assets, read off the panel's own files.

    `etf_book_production.prep_panel()` filters the universe to USE_CLASSES
    (equity/commodity/convertible), so the bond and gold legs a book is tested against are
    NOT in the frame it returns. Reading them from the same files the panel loader reads
    keeps one price source while not pretending the book's universe contains them.

    The prefixed file (sh|sz<code>.csv) is the full-history wide face; the bare
    <code>.csv is the core48 face and may start years later (511010: 2013-04 vs 2020-01),
    so the wide face wins when both exist.

    The SAME flip repair the book's panel gets is applied here. Without it a single split
    (513100 has one on 2022-01-14) prints as a -50% day inside the span leg and a
    buy-and-hold basket of a Nasdaq QDII comes out at -5.3%/yr instead of +6.5%/yr -- the
    r1262 data-pit at the benchmark end, now measured on the comparison arm itself.
    """
    span = span or SPAN
    data_dir = data_dir or os.path.join(P.E.PATHS.data_dir, "daily")
    close_d, open_d = {}, {}
    for _key, code, _label in span:
        for name in ("sh%s.csv" % code, "sz%s.csv" % code, "%s.csv" % code):
            p = os.path.join(data_dir, name)
            if not os.path.exists(p):
                continue
            try:
                df = pd.read_csv(p, parse_dates=["date"]).set_index("date")
            except Exception:
                continue
            if not {"open", "close"} <= set(df.columns) or df.empty:
                continue
            close_d[code], open_d[code] = df["close"], df["open"]
            break
    if not close_d:
        return pd.DataFrame(), pd.DataFrame(), 0
    close = pd.DataFrame(close_d).sort_index().replace(0.0, np.nan)
    openp = pd.DataFrame(open_d).sort_index().replace(0.0, np.nan)
    n_flip = 0
    if repair:
        close, openp, n_flip = A.repair_flips(close, openp)
    return close, openp, n_flip


def span_returns(openp, keys):
    """Open-to-open returns of the span assets, the same basis the book earns on."""
    op = openp.reindex(columns=keys)
    return op.pct_change()


def basket(openp, keys, rebal, cost):
    """Equal-weight span basket on the book's own decision grid, 10bp/side on turnover.

    A span portfolio a human could actually hold, so the book has a comparison rather than
    a coefficient. Rebalanced every `rebal` bars like the book, de-lever not applied (the
    span legs are the raw exposures the book is being tested against).
    """
    op = openp.reindex(columns=keys)
    dates = list(op.index)
    have = op.notna().all(axis=1)
    dates = [d for d in dates if have.loc[d]]
    if len(dates) < rebal + 2:
        return None
    eq, held, turns = 1.0, set(), 0.0
    ser = []
    for i in range(len(dates) - 1):
        d, nxt = dates[i], dates[i + 1]
        if i % rebal == 0:
            new = set(keys)
            turn = len(new - held) / len(keys) + len(held - new) / len(keys)
            eq *= (1.0 - cost * turn)
            turns += turn
            held = new
        r = float((op.loc[nxt, list(keys)] / op.loc[d, list(keys)] - 1.0).mean())
        eq *= (1.0 + r)
        ser.append((nxt, eq))
    s = pd.Series(dict(ser)).sort_index()
    return s, turns


def _pstats(ser, label):
    """cagr/sharpe/maxdd/vol for a span portfolio, or None when the leg did not run.

    A return without its risk is not a comparison (E95/E99 class): the book de-levers to an
    8% target, so a raw-CAGR contest against an unlevered buy-and-hold arm would credit the
    span for taking more risk. Both columns are printed; neither is corrected.
    """
    if ser is None:
        return None
    m = A.stats2(ser, label)
    return {k: m.get(k) for k in ("cagr", "sharpe", "maxdd", "vol", "years")}


def build(openp=None, close=None, amt=None, score=None, n_hold=None, rebal=None,
          vol_target=None, cost=P.COST, span=None, span_open=None):
    """Book return series + span returns + the two regressions. Pure function of inputs."""
    span = span or SPAN
    keys = [c for _, c, _ in span]
    span_flips = 0
    if span_open is None:
        _sc, span_open, span_flips = load_span_frames(span)
    bt, ser = P.backtest(close, openp, amt, score, n_hold, rebal, cost=cost,
                         vol_target=vol_target)
    book_r = ser.pct_change().dropna()
    sr = span_returns(span_open, keys)
    idx = book_r.index.intersection(sr.dropna().index)
    if len(idx) < 60:
        return {"status": "insufficient_overlap", "n_obs": int(len(idx)),
                "keys": keys,
                "missing": [c for c in keys if c not in span_open.columns]}
    y = book_r.loc[idx]
    X = sr.loc[idx, keys]
    full = ols(y, X)
    is_split = pd.Timestamp(P.IS_END)
    is_mask = idx <= is_split
    oos_mask = idx > is_split
    is_fit = ols(y[is_mask], X[is_mask]) if is_mask.sum() > len(keys) + 2 else None
    oos_fit = ols(y[oos_mask], X[oos_mask]) if oos_mask.sum() > len(keys) + 2 else None
    wf = None
    if is_fit:
        # walk-forward: IS coefficients, applied to OOS. The alpha is whatever the IS
        # intercept pays on the forward window -- no refit, so nothing is fitted on OOS.
        pred_is = is_fit["alpha"] + X[oos_mask] @ np.array(is_fit["betas"])
        wf = {
            "alpha_is_annual": round(is_fit["alpha"] * 252, 4),
            "oos_mean_resid_annual": round(float((y[oos_mask] - pred_is).mean()) * 252, 4),
            "oos_realised_annual": round(float(y[oos_mask].mean()) * 252, 4),
            "oos_predicted_annual": round(float(pred_is.mean()) * 252, 4),
            "n_oos": int(oos_mask.sum()),
        }
    bk = {}
    for key, code, label in span:
        s, turns = basket(span_open, [code], rebal, cost)
        row = {"code": code, "label": label,
               "cagr": None, "turnover_total": turns if s is not None else None}
        if s is not None:
            row.update(_pstats(s[s.index >= idx[0]], key) or {})
        bk[key] = row
    sb, basket_turns = basket(span_open, keys, rebal, cost)
    bk["equal_weight_basket"] = {
        "codes": keys,
        "cagr": None,
        "turnover_total": round(basket_turns, 3) if sb is not None else None,
    }
    if sb is not None:
        bk["equal_weight_basket"].update(_pstats(sb[sb.index >= idx[0]], "ew") or {})
    out = {
        "schema": "etf_book_spanning/v1",
        "evidence_cutoff": str(idx[-1].date()),
        "span": [{"key": k, "code": c, "label": lb} for k, c, lb in span],
        "config": {"n_hold": n_hold, "rebal": rebal, "vol_target": vol_target,
                   "cost_bp_per_side": round(cost * 1e4, 2)},
        "book": {"cagr": bt["full"]["cagr"], "sharpe": bt["full"]["sharpe"],
                 "maxdd": bt["full"]["maxdd"], "vol": bt["full"]["vol"],
                 "turnover_per_decision": bt["turnover_per_decision"],
                 "obs": {"full": int(len(idx)), "is": int(is_mask.sum()),
                         "oos": int(oos_mask.sum())}},
        "full": _fmt(full, keys),
        "is": _fmt(is_fit, keys),
        "oos": _fmt(oos_fit, keys),
        "walkforward": wf,
        "span_portfolios": bk,
        "caveats": [
            "daily OLS, no HAC correction (non-overlapping daily returns; autocorrelation in "
            "the residual would only widen the alpha interval, so a t below 2 is not rescued "
            "by it)",
            "the span set is four liquid ETFs a retail account can actually hold; a book that "
            "fails this test can still be a timing story, but not an alpha story",
            "loadings are not constant: the table is the average over the window, and the "
            "IS/OOS columns are the check on that",
            "span prices carry the same single-day flip repair as the book's panel; %d flip(s) "
            "flattened, otherwise a split prints as a -50%% day in the benchmark arm"
            % span_flips,
        ],
    }
    return out


def _fmt(fit, keys):
    if not fit:
        return None
    return {
        "alpha_annual": round(fit["alpha"] * 252, 4),
        "alpha_t": round(fit["t"][0], 3),
        "betas": {k: round(b, 4) for k, b in zip(keys, fit["betas"])},
        "beta_t": {k: round(v, 3) for k, v in zip(keys, fit["t"][1:])},
        "r2": round(fit["r2"], 4),
        "n_obs": fit["n_obs"],
        "resid_vol_annual": round(fit["resid_sd_daily"] * np.sqrt(252), 4),
    }


def run(capital=1_000_000.0):
    n, rebal, vt, src = card_config()
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    out = build(openp=openp, close=close, amt=amt, score=score, n_hold=n, rebal=rebal,
                vol_target=vt)
    out["config_source"] = src
    out["panel"] = {"universe": int(len(close.columns)), "flips_repaired": int(n_flip),
                    "last_bar": str(close.index[-1].date())}
    if "book" not in out:
        print(json.dumps({"status": out.get("status"), "n_obs": out.get("n_obs"),
                          "missing": out.get("missing")}, ensure_ascii=False))
        return 2
    out["verdict"] = verdict(out)
    os.makedirs(os.path.dirname(RESULT), exist_ok=True)
    with open(RESULT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(json.dumps({"verdict": out["verdict"], "alpha": (out.get("full") or {}).get("alpha_annual"),
                      "alpha_t": (out.get("full") or {}).get("alpha_t"),
                      "r2": (out.get("full") or {}).get("r2"),
                      "book_cagr": out["book"]["cagr"],
                      "ew_basket_cagr": out["span_portfolios"]["equal_weight_basket"]["cagr"],
                      "path": RESULT}, ensure_ascii=False, indent=1))
    return 0


def verdict(out):
    f = out.get("full")
    if not f:
        return "no regression: %s" % out.get("status")
    ew = out["span_portfolios"]["equal_weight_basket"]
    b = out["book"]
    words = []
    words.append("book %.2f%%/yr SR %.2f DD %.1f%% vs EW span basket %s SR %.2f DD %.1f%% over %s"
                 % (b["cagr"] * 100, b["sharpe"], b["maxdd"] * 100,
                    ("%.2f%%/yr" % (ew["cagr"] * 100)) if ew.get("cagr") is not None else "n/a",
                    ew.get("sharpe") or 0.0, (ew.get("maxdd") or 0.0) * 100,
                    out["evidence_cutoff"]))
    words.append("span explains R2=%.2f of daily variance; alpha %+.2f%%/yr (t=%.2f)"
                 % (f["r2"], f["alpha_annual"] * 100, f["alpha_t"]))
    if f["alpha_t"] < 2.0:
        words.append("alpha NOT distinguishable from a fixed loadings mix of the four span "
                     "assets at 2 sigma")
    else:
        words.append("alpha survives the span at the full-window level; see IS/OOS columns")
    better = [k for k, v in out["span_portfolios"].items()
              if isinstance(v, dict) and k != "equal_weight_basket" and v.get("sharpe")
              and v["sharpe"] > b["sharpe"]]
    if better:
        words.append("span arms with a higher Sharpe than the book: %s" % ", ".join(better))
    return "; ".join(words)


# ---------------------------------------------------------------------------- selftest


def selftest():
    """Fixture legs: the machinery must recover a planted alpha and must NOT invent one.

    Every leg is paired with an activity assertion (r1261): before believing 'the alpha is
    zero', prove the regression actually ran on real variance.
    """
    n_ok = 0
    n_all = 0

    def chk(name, cond, detail=""):
        nonlocal n_ok, n_all
        n_all += 1
        if cond:
            n_ok += 1
            print("PASS %s%s" % (name, (" :: " + str(detail)) if detail else ""))
        else:
            print("FAIL %s%s" % (name, (" :: " + str(detail)) if detail else ""))

    rng = np.random.default_rng(11)
    n = 500
    idx = pd.bdate_range("2020-01-01", periods=n)
    keys = ["518880", "513100", "510300", "511010"]
    X = pd.DataFrame(rng.normal(0, 0.01, size=(n, 4)), index=idx, columns=keys)
    X.iloc[:, 3] = rng.normal(0, 0.0005, n)  # bond: quiet but not degenerate

    # L1 planted alpha is recovered (asserted in standard errors, not in absolute bp:
    #     a tighter absolute band just re-tests the fixture's noise draw)
    y = 0.0004 + X @ np.array([0.2, 0.3, 0.5, 0.0]) + rng.normal(0, 0.002, n)
    fit = ols(y, X)
    se_a = abs(fit["alpha"] / fit["t"][0]) if fit["t"][0] else float("nan")
    chk("L1 planted alpha recovered", abs(fit["alpha"] - 0.0004) <= 3 * se_a and fit["alpha"] > 0,
        "alpha_daily=%.6f se=%.6f t=%.2f" % (fit["alpha"], se_a, fit["t"][0]))
    se_b = np.array([abs(b / t) if t else np.nan for b, t in zip(fit["betas"], fit["t"][1:])])
    gaps = [abs(a - b) for a, b in zip(fit["betas"], [0.2, 0.3, 0.5, 0.0])]
    chk("L2 planted betas recovered",
        all(g <= max(3 * s, 0.01) for g, s in zip(gaps, se_b)),
        [round(g, 4) for g in gaps])

    # L3 a pure-beta series has no intercept (the test can say "no alpha")
    y2 = 0.0004 + X @ np.array([0.2, 0.3, 0.5, 0.0]) + rng.normal(0, 0.002, n)
    fit0 = ols(X @ np.array([0.2, 0.3, 0.5, 0.0]) + rng.normal(0, 0.002, n), X)
    chk("L3 pure beta yields alpha near zero", abs(fit0["alpha"] * 252) < 0.02,
        "alpha_annual=%.4f" % (fit0["alpha"] * 252))
    chk("L3b activity: regression ran on real variance",
        fit0["n_obs"] == n and 0.0 < fit0["r2"] < 1.0, "n=%d r2=%.3f" % (fit0["n_obs"], fit0["r2"]))

    # L4 the published alpha is the DAILY intercept times 252, not the daily number
    #     itself (r1292 unit class: a field labelled "annual" that carries a daily value)
    ann = _fmt(fit, keys)["alpha_annual"]
    chk("L4 published alpha carries the 252 factor",
        abs(ann / fit["alpha"] - 252) < 0.5 and abs(ann) > 10 * abs(fit["alpha"]),
        "annual=%.4f daily=%.6f" % (ann, fit["alpha"]))

    # L5 degenerate span is refused rather than silently returning a number
    Xbad = pd.DataFrame(0.0, index=idx, columns=keys)
    ybad = rng.normal(0, 0.01, n)
    chk("L5 constant span is refused", ols(ybad, Xbad) is None, "rc=None")

    # L6 too few observations is refused (no win from a 3-point regression)
    chk("L6 short sample refused", ols(y[:4], X.iloc[:4]) is None, "n=4")

    # L7 the basket is rebalanced and pays turnover on cost, not free
    op = pd.DataFrame(100 * np.exp(np.cumsum(rng.normal(0, 0.01, size=(300, 4)), axis=0)),
                      index=pd.bdate_range("2021-01-01", periods=300), columns=keys)
    s_free, t_free = basket(op, keys, 20, 0.0)
    s_cost, t_cost = basket(op, keys, 20, 0.001)
    chk("L7 basket turnover is nonzero and cost is charged",
        t_free > 0 and s_cost.iloc[-1] < s_free.iloc[-1],
        "turns=%.2f free=%.4f cost=%.4f" % (t_free, s_free.iloc[-1], s_cost.iloc[-1]))

    # L8 span returns are open-to-open, matching what the book earns on
    op2 = pd.DataFrame({"A": [100.0, 110.0, 121.0]},
                       index=pd.bdate_range("2021-01-01", periods=3))
    sr = span_returns(op2, ["A"])
    chk("L8 span returns are open-to-open", abs(sr["A"].iloc[1] - 0.10) < 1e-12,
        "r1=%.4f" % sr["A"].iloc[1])

    # L9 verdict language follows the t-stat, so a null alpha cannot be printed as skill
    fake = {"book": {"cagr": 0.09, "sharpe": 0.9, "maxdd": -0.12},
            "evidence_cutoff": "2026-10-26",
            "span_portfolios": {"equal_weight_basket": {"cagr": 0.05, "sharpe": 0.7,
                                                        "maxdd": -0.2},
                                "gold": {"cagr": 0.13, "sharpe": 0.8, "maxdd": -0.3}},
            "full": {"alpha_annual": 0.002, "alpha_t": 0.4, "r2": 0.9}}
    v1 = verdict(fake)
    fake["full"]["alpha_t"] = 3.1
    v2 = verdict(fake)
    chk("L9 verdict follows the t-stat", "NOT distinguishable" in v1
        and "survives" in v2, v1[:70])
    chk("L9b a span arm below the book's Sharpe is not named",
        "higher Sharpe" not in v1)
    fake["span_portfolios"]["gold"]["sharpe"] = 1.4
    v3 = verdict(fake)
    chk("L9c a span arm above the book's Sharpe is named", "gold" in v3.split("higher Sharpe")[-1],
        v3[-50:])

    print("%d/%d PASS" % (n_ok, n_all))
    return 0 if n_ok == n_all else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    return run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))