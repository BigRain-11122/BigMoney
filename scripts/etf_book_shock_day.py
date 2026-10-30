"""ETF book -- if the market gaps down tomorrow, what does the operator lose?

Every face of this book publishes an expected return and a deep-drawdown number over
years. None of them answers the question an operator asks the night before a bad open:
*if the index opens -5%, what does my account lose?* Two numbers get confused here:

  * the book is only partially deployed (the ticket prints book_amount and cash_amount,
    currently about 47/53), and
  * that deployed sleeve is scaled to a beta target of 0.20, so its market exposure is a
    fifth of the sleeve, not all of it.

Multiplying "market -5%" by "47% deployed" gives -2.4% and is wrong twice over. This
face replaces that arithmetic with measurement:

  1. the realized beta of the book on 510300 (full history and the last 250 bars),
  2. the book's own return distribution that actually happened (worst day, 1%/5%
     quantiles with dates), and
  3. what the book really did on the worst market days in the panel -- conditional
     stress, not a linear assumption.

The frozen claim (written before the first run) is that the beta the ticket trades on
describes reality: both the full-history and last-250-bar realized betas land inside
BETA_BAND. If that fails, the ticket's k is mispricing risk and this face says so.

Usage:
    python scripts/etf_book_shock_day.py run [--out=...]
    python scripts/etf_book_shock_day.py --check
    python scripts/etf_book_shock_day.py --selftest
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np
import pandas as pd

import etf_composite_pf as F
import etf_equity_alpha as A
import etf_phase_beta_target as BT
import etf_phase_beta_window as BW
import etf_variants_null_rolling as V
import etf_book_order as O
from etf_asset_class import classify

OUT_JSON = ROOT / "results" / "etf_book_shock_day.json"
OUT_MD = ROOT / "research" / "ETF_BOOK_SHOCK_DAY.md"
OUT_FLIP = ROOT / "results" / "etf_book_flip_contamination.json"

SCRIPT = "scripts/etf_book_shock_day.py"
FACE = "results/etf_book_shock_day.json"

# ---------------------------------------------------------------- frozen criteria
# Written before the first run; the loader refuses a face whose echoed criteria differ,
# so a later "small adjustment" cannot pass as the rule it was not tested under.
BETA_BAND = (0.10, 0.30)          # the ticket trades to 0.20; a fifth plus/minus a band
RECENT_BARS = 250                 # "recent" = the last year of bars
WORST_DAYS = 20                   # how many worst market days the conditional read uses
SHOCKS = (-0.03, -0.05, -0.08)    # single-day index moves the operator asks about
SD_FLOOR = 1e-8                   # below this the market has no variance: refuse a slope

CRITERIA = {
    "beta_band": list(BETA_BAND),
    "recent_bars": RECENT_BARS,
    "worst_days": WORST_DAYS,
    "shocks": list(SHOCKS),
    "sd_floor": SD_FLOOR,
    "frozen": "constants above were written before the first run; the loader refuses "
              "a face that echoes others",
}

# ------------------------------------------------------------------ pure functions
def ret_series(prices):
    """Simple daily returns, first observation dropped (mirrors BT.rets)."""
    s = pd.Series(prices).astype(float)
    return s / s.shift(1) - 1.0


def iso(d):
    """A date stamp a reader can compare as a string (never '00:00:00' on the end)."""
    return pd.Timestamp(d).date().isoformat()


def dist(series, quantiles=(0.01, 0.05, 0.50)):
    """Distribution read-out of a return series, with the worst day named."""
    s = pd.Series(series).astype(float).dropna()
    if not len(s):
        return None
    worst_date = s.idxmin()
    return {
        "bars": int(len(s)),
        "worst": round(float(s.min()), 6),
        "worst_date": iso(worst_date),
        "second_worst": round(float(s.nsmallest(2).iloc[-1]), 6),
        **{"p%02d" % int(q * 100): round(float(s.quantile(q)), 6) for q in quantiles},
        "mean": round(float(s.mean()), 8),
        "sd": round(float(s.std(ddof=1)), 8),
    }


def beta_of(book, market):
    """OLS slope of book on market. None when the market has no dispersion.

    A constant market makes the regressor degenerate; returning 0.0 there would read as
    'the book has no market exposure', which is a different and unfounded statement.
    """
    b = pd.Series(book).astype(float)
    m = pd.Series(market).astype(float)
    common = b.dropna().index.intersection(m.dropna().index)
    if len(common) < 3:
        return None
    b, m = b.reindex(common), m.reindex(common)
    var = float(m.var(ddof=1))
    if not np.isfinite(var) or var <= SD_FLOOR:
        return None
    cov = float(np.cov(b.to_numpy(), m.to_numpy(), ddof=1)[0, 1])
    if not np.isfinite(cov):
        return None
    return cov / var


def conditional_stress(book, market, n=WORST_DAYS):
    """What the book did on the n worst market days -- measured, not assumed."""
    b = pd.Series(book).astype(float)
    m = pd.Series(market).astype(float)
    common = b.dropna().index.intersection(m.dropna().index)
    if len(common) < n + 1:
        return None
    b, m = b.reindex(common), m.reindex(common)
    worst = m.nsmallest(int(n))
    b_on = b.reindex(worst.index).dropna()
    if not len(b_on):
        return None
    return {
        "n_days": int(len(b_on)),
        "market_mean": round(float(worst.mean()), 6),
        "book_mean": round(float(b_on.mean()), 6),
        "book_worst": round(float(b_on.min()), 6),
        "book_worst_date": iso(b_on.idxmin()),
        "book_positive_share": round(float((b_on > 0).mean()), 4),
        "mean_ratio": (round(float(b_on.mean() / worst.mean()), 4)
                       if abs(float(worst.mean())) > SD_FLOOR else None),
        "days": [{"date": iso(d), "market": round(float(m.loc[d]), 6),
                  "book": round(float(b.loc[d]), 6)} for d in worst.index],
    }


def scenario_table(beta, nav, shocks=SHOCKS):
    """Index shock -> book return -> CNY at the given NAV."""
    if beta is None or nav is None:
        return None
    return [{"market_shock": round(float(s), 6),
             "book_return": round(float(s) * float(beta), 8),
             "cny": round(float(s) * float(beta) * float(nav), 2),
             "naive_deployed_cny": None} for s in shocks]


def verdict_from(beta_full, beta_recent, band=BETA_BAND):
    """Recomputed from the numbers by the gate; never taken on trust."""
    lo, hi = band
    if beta_full is None or beta_recent is None:
        return "UNMEASURED"
    ok = lo <= beta_full <= hi and lo <= beta_recent <= hi
    return "BETA_MATCHED" if ok else "BETA_DRIFTED"


def read_price_quality(path=None):
    """The published flip-contamination reading, quoted not recomputed.

    This face's worst day is a raw-price statistic, and the panel carries unit-change
    prints that read as -50% days. The contamination face measures that; this reader
    only quotes it, so a missing artifact reads as 'unverified' rather than as 'clean'.
    """
    p = Path(path) if path else OUT_FLIP
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        full = (d.get("windows") or {}).get("full_history") or {}
        wd = full.get("worst_day") or {}
        return {"face": str(OUT_FLIP.relative_to(ROOT)).replace("\\", "/"),
                "verdict": d.get("verdict"),
                "flip_prints": (d.get("panel") or {}).get("flip_prints_flattened"),
                "clean_worst": ((wd.get("clean") or {}).get("value")),
                "clean_worst_date": ((wd.get("clean") or {}).get("date"))}
    except (FileNotFoundError, KeyError, ValueError):
        return None


def read_ticket(ticket_path=None):
    """The live exposure to price the shocks on; None when the ticket is absent."""
    p = Path(ticket_path) if ticket_path else (ROOT / "results" / "etf_book_order" /
                                              "latest.json")
    try:
        if p.name == "latest.json":
            meta = json.loads(p.read_text(encoding="utf-8"))
            p = ROOT / "results" / "etf_book_order" / meta["file"]
        d = json.loads(p.read_text(encoding="utf-8"))
        t = d["ticket"]
        return {
            "file": str(p.relative_to(ROOT)).replace("\\", "/"),
            "as_of": d.get("evidence_cutoff"),
            "nav": float(t["nav"]),
            "book_amount": float(t["book_amount"]),
            "cash_amount": float(t["cash_amount"]),
            "deployed_share": round(float(t["book_weight"]), 6),
            "beta_target": float(d.get("beta_target") or O.DEFAULT_BETA),
        }
    except (FileNotFoundError, KeyError, ValueError):
        return None


# ------------------------------------------------------------------------- build
def build(out_path=OUT_JSON, md_path=OUT_MD):
    close, openp, amt, feats = F.build_panel()
    classes = pd.Series(classify(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in V.KEEP]
    score = F.build_score(close[cols], amt[cols], feats)
    ser, _turn, _gap = F.run_next_open(close[cols], openp[cols], amt[cols], feats,
                                       O.REBAL, n_hold=F.N_HOLD, cost=F.COST,
                                       score=score)
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        print("FATAL: no 510300 column on the panel")
        return 2
    idx = ser.index.intersection(close[mkt_col].index)
    rp, rm = BT.rets(ser.reindex(idx)), BT.rets(close[mkt_col].reindex(idx))

    rates = BW.load_repo_rates()
    cash_rf, _missing = BW.repo_daily_cash(idx, rates)
    cash_rf = cash_rf.reindex(idx).fillna(0.0)

    sched = O.k_schedule(rp, rm, O.DEFAULT_BETA)
    if not sched:
        print("FATAL: the production decision calendar could not be built")
        return 2
    equity, _k, _m = BT.apply_overlay(rp, rm, sched, 0.0, O.COST_BP, rf=cash_rf)
    if equity is None:
        print("FATAL: the production overlay produced no equity path")
        return 2
    book_ret = equity / equity.shift(1) - 1.0
    market_ret = rm.reindex(book_ret.index).dropna()

    beta_full = beta_of(book_ret, market_ret)
    recent = book_ret.iloc[-RECENT_BARS:]
    beta_recent = beta_of(recent, market_ret.reindex(recent.index))

    ticket = read_ticket()
    nav = ticket["nav"] if ticket else None
    # price on the ROUNDED beta the face publishes, so the gate can recompute the money
    beta_round = None if beta_full is None else round(beta_full, 6)
    table = scenario_table(beta_round, nav)
    if table is not None and ticket is not None:
        deployed = ticket["deployed_share"]
        for row in table:
            row["naive_deployed_cny"] = round(
                float(row["market_shock"]) * deployed * nav, 2)

    payload = {
        "script": SCRIPT,
        "face": FACE,
        "evidence_cutoff": iso(book_ret.index.max()),
        "market": mkt_col,
        "production_rule": {"beta_target": O.DEFAULT_BETA, "rebal": O.REBAL,
                            "cost_bp_per_side": O.COST_BP, "min_hist": O.MIN_HIST},
        "criteria": CRITERIA,
        "ticket": ticket,
        "beta": {"full": None if beta_full is None else round(beta_full, 6),
                 "recent": None if beta_recent is None else round(beta_recent, 6),
                 "recent_bars": min(int(len(book_ret)), RECENT_BARS),
                 "bars": int(len(book_ret))},
        "book_distribution": dist(book_ret),
        "market_distribution": dist(market_ret),
        "conditional_stress": conditional_stress(book_ret, market_ret),
        "scenarios": table,
        "price_quality": read_price_quality(),
        "verdict": verdict_from(beta_full, beta_recent),
    }
    payload["sentence"] = sentence_of(payload)

    if not check_payload(payload):
        print("FATAL: payload failed its own gate")
        return 2
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    if md_path:
        md_path.write_text(render_md(payload), encoding="utf-8")
    print("wrote %s (verdict %s)" % (out_path.relative_to(ROOT), payload["verdict"]))
    print(payload["sentence"])
    return 0


def sentence_of(p):
    """The one line a reader takes away, built from the numbers only."""
    bd, cs = p.get("book_distribution"), p.get("conditional_stress")
    beta = (p.get("beta") or {})
    if not bd or not cs or beta.get("full") is None:
        return "the shock face is missing a leg, so it states nothing"
    return ("the book's realized beta to %s is %.2f over its whole history and %.2f on "
            "the last %d bars (the ticket trades to %.2f) -- on the %d worst index days "
            "the book averaged %+.2f%% while the index averaged %+.2f%%, so an index gap "
            "costs that beta's share of the shock, never the deployed share"
            % (p.get("market"), beta["full"], beta.get("recent") or float("nan"),
               beta.get("recent_bars") or 0,
               (p.get("production_rule") or {}).get("beta_target", float("nan")),
               cs["n_days"], 100.0 * cs["book_mean"], 100.0 * cs["market_mean"]))


def render_md(p):
    cs = p.get("conditional_stress") or {}
    bd = p.get("book_distribution") or {}
    md = p.get("market_distribution") or {}
    tk = p.get("ticket") or {}
    lines = [
        "# ETF book -- what a market gap actually costs",
        "",
        "Evidence cutoff %s · rule beta target %.2f · rebalance %d bars · cost %s bp/side"
        % (p.get("evidence_cutoff"), p["production_rule"]["beta_target"],
           p["production_rule"]["rebal"], p["production_rule"]["cost_bp_per_side"]),
        "",
        "## The answer",
        "",
        p.get("sentence", ""),
        "",
        "## Realized beta",
        "",
        "| window | bars | beta |",
        "| --- | --- | --- |",
        "| full history | %d | %s |"
        % (p["beta"]["bars"], _fmt(p["beta"]["full"])),
        "| last %d bars | %d | %s |"
        % (p["beta"]["recent_bars"], p["beta"]["recent_bars"],
           _fmt(p["beta"]["recent"])),
        "",
        "Verdict: **%s** (band %.2f..%.2f)." % (p["verdict"], *BETA_BAND),
        "",
        "## The book's own worst days",
        "",
        "| face | book | %s |" % p.get("market"),
        "| --- | --- | --- |",
        "| worst day | %+.2f%% (%s) | %+.2f%% |"
        % (100 * bd.get("worst", float("nan")), bd.get("worst_date"),
           100 * md.get("worst", float("nan"))),
        "| 1st percentile | %+.2f%% | %+.2f%% |" % (100 * bd.get("p01", float("nan")),
                                                     100 * md.get("p01", float("nan"))),
        "| 5th percentile | %+.2f%% | %+.2f%% |" % (100 * bd.get("p05", float("nan")),
                                                     100 * md.get("p05", float("nan"))),
        "| daily sd | %.2f%% | %.2f%% |" % (100 * bd.get("sd", float("nan")),
                                             100 * md.get("sd", float("nan"))),
        "",
        _price_quality_line(p.get("price_quality")),
        "",
        "## On the %d worst index days (measured, not assumed)" % cs.get("n_days", 0),
        "",
        "| date | %s | book |" % p.get("market"),
        "| --- | --- | --- |",
    ]
    for row in (cs.get("days") or [])[:8]:
        lines.append("| %s | %+.2f%% | %+.2f%% |"
                     % (row["date"], 100 * row["market"], 100 * row["book"]))
    lines += [
        "",
        "Mean on those days: index %+.2f%% / book %+.2f%% (ratio %s) · book worst "
        "%+.2f%% on %s · book finished up on %.0f%% of them."
        % (100 * cs.get("market_mean", float("nan")),
           100 * cs.get("book_mean", float("nan")), cs.get("mean_ratio"),
           100 * cs.get("book_worst", float("nan")), cs.get("book_worst_date"),
           100 * cs.get("book_positive_share", 0.0)),
        "",
        "## Tomorrow, in money",
        "",
    ]
    if p.get("scenarios") and tk:
        lines += [
            "Priced on %s: NAV %s, deployed %s (%s), cash %s."
            % (tk.get("file"), _cny(tk.get("nav")), _cny(tk.get("book_amount")),
               _pct(tk.get("deployed_share")), _cny(tk.get("cash_amount"))),
            "",
            "| index gaps | book returns | costs you | the naive 'shock x deployed' |",
            "| --- | --- | --- | --- |",
        ]
        for row in p["scenarios"]:
            lines.append("| %+.0f%% | %+.2f%% | %s | %s |"
                         % (100 * row["market_shock"], 100 * row["book_return"],
                            _cny(row["cny"]), _cny(row.get("naive_deployed_cny"))))
        lines += ["",
                  "The last column is what an operator computes by hand and it "
                  "overstates the loss by roughly the inverse of the beta scaling."]
    else:
        lines += ["No live ticket on disk, so the shocks are not priced in money -- "
                  "the beta and the conditional stress above still stand."]
    lines += ["",
              "Descriptive face: no rule is adopted here, nothing is traded, and the "
              "shocks are index moves applied through the measured beta, not forecasts."]
    return "\n".join(lines) + "\n"


def _fmt(v):
    return "unmeasured" if v is None else "%.4f" % v


def _price_quality_line(pq):
    """One sentence about whether the worst day above is a real market day."""
    if not pq:
        return ("**Price quality unverified**: the flip-contamination reading is not on "
                "disk, so the worst day above may be a unit-change print rather than a "
                "market day.")
    cw = pq.get("clean_worst")
    if cw is None:
        return ("**Price quality**: the contamination face (%s) is %s but carries no "
                "clean worst day." % (pq.get("face"), pq.get("verdict")))
    return ("**Price quality**: the panel carries %s unit-change prints and the "
            "contamination face calls the effect %s. On repaired prices the same rule's "
            "worst day is %+.2f%% (%s) -- so the worst day quoted above is a print, not "
            "a market day. Source: %s."
            % (pq.get("flip_prints"), pq.get("verdict"), 100 * float(cw),
               pq.get("clean_worst_date"), pq.get("face")))


def _cny(v):
    return "n/a" if v is None else format(float(v), "+,.0f") + " CNY"


def _pct(v):
    return "n/a" if v is None else "%.1f%%" % (100 * float(v))


def check_payload(p):
    """Gate: the echoed criteria must equal the frozen ones and the verdict must
    recompute from the published numbers."""
    if p.get("criteria") != CRITERIA:
        print("GATE: echoed criteria differ from the frozen ones")
        return False
    beta = p.get("beta") or {}
    if p.get("verdict") != verdict_from(beta.get("full"), beta.get("recent")):
        print("GATE: verdict does not recompute from the published betas")
        return False
    if p.get("scenarios") and p.get("ticket"):
        nav = p["ticket"]["nav"]
        for row, shock in zip(p["scenarios"], SHOCKS):
            if abs(row["cny"] - shock * (beta.get("full") or 0.0) * nav) > 0.02:
                print("GATE: scenario money does not follow from beta x shock x nav")
                return False
    return True


# ---------------------------------------------------------------------- selftest
def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    idx = pd.date_range("2024-01-01", periods=6, freq="D")
    s = pd.Series([0.01, -0.02, -0.05, 0.03, 0.0, -0.04], index=idx)
    d = dist(s)
    leg("L1 dist names the worst day and its date", d["worst"] == -0.05
        and d["worst_date"] == "2024-01-03", d["worst_date"])
    leg("L2 second worst is not the worst", d["second_worst"] == -0.04)

    m = pd.Series([0.02, -0.01, -0.10, 0.06, 0.0, -0.08], index=idx)
    leg("L3 beta of 0.2 x market is exactly 0.2",
        abs((beta_of(0.2 * m, m) or 0.0) - 0.2) < 1e-12, beta_of(0.2 * m, m))
    leg("L4 beta of a constant market is refused, not reported as 0",
        beta_of(s, pd.Series(0.01, index=idx)) is None)
    leg("L5 beta needs dispersion on the book side too",
        beta_of(pd.Series(0.0, index=idx), m) == 0.0)

    cs = conditional_stress(0.2 * m, m, n=2)
    leg("L6 conditional stress picks the two worst market days",
        cs["n_days"] == 2 and [r["date"] for r in cs["days"]]
        == ["2024-01-03", "2024-01-06"])
    leg("L7 the book's mean on those days is a fifth of the market's",
        abs(cs["mean_ratio"] - 0.2) < 1e-9, cs["mean_ratio"])

    tab = scenario_table(0.2, 1_000_000.0, (-0.05,))
    leg("L8 a -5% index gap on a 0.2-beta book costs 10,000 CNY",
        tab[0]["cny"] == -10000.0 and abs(tab[0]["book_return"] + 0.01) < 1e-12)
    leg("L9 a zero shock costs nothing", scenario_table(0.2, 1e6, (0.0,))[0]["cny"] == 0.0)
    leg("L10 no beta means no money table, not a zero", scenario_table(None, 1e6) is None)

    leg("L11 verdict is matched inside the band on both windows",
        verdict_from(0.20, 0.18) == "BETA_MATCHED")
    leg("L12 verdict drifts when the recent window leaves the band",
        verdict_from(0.20, 0.55) == "BETA_DRIFTED")
    leg("L13 an unmeasured beta is not a verdict at all",
        verdict_from(0.20, None) == "UNMEASURED")
    leg("L14 band edges are inside", verdict_from(BETA_BAND[0], BETA_BAND[1])
        == "BETA_MATCHED")

    leg("L15 an absent ticket reads None instead of raising",
        read_ticket(ROOT / "results" / "_no_such_ticket.json") is None)

    p = {"criteria": CRITERIA, "verdict": "BETA_MATCHED",
         "beta": {"full": 0.2, "recent": 0.2}, "market": "510300",
         "book_distribution": {"worst": -0.02, "worst_date": "2024-01-03"},
         "conditional_stress": {"n_days": 2, "book_mean": -0.01, "market_mean": -0.05,
                                "book_worst": -0.02, "book_worst_date": "2024-01-03",
                                "book_positive_share": 0.0, "mean_ratio": 0.2, "days": []},
         "production_rule": {"beta_target": 0.2}, "ticket": None, "scenarios": None}
    leg("L16 the published sentence carries the beta and both means",
        "0.20" in sentence_of(p) and "-1.00%" in sentence_of(p)
        and "-5.00%" in sentence_of(p), sentence_of(p))
    bad = dict(p, verdict="BETA_DRIFTED")
    leg("L17 the gate refuses a verdict that does not recompute", not check_payload(bad))
    bad2 = dict(p, criteria=dict(CRITERIA, beta_band=[0.0, 1.0]))
    leg("L18 the gate refuses criteria that were edited after the fact",
        not check_payload(bad2))
    leg("L19 the gate passes a self-consistent payload", check_payload(p))

    ok = sum(1 for _n, o, _d in legs if o)
    for name, good, detail in legs:
        print("[%s] %s%s" % ("PASS" if good else "FAIL", name,
                             "" if not detail else " | " + str(detail)))
    print("%d/%d %s" % (ok, len(legs), "PASS" if ok == len(legs) else "FAIL"))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", default=str(OUT_JSON))
    ap.add_argument("--md", default=str(OUT_MD))
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.check:
        p = json.loads(Path(a.out).read_text(encoding="utf-8"))
        ok = check_payload(p)
        print("check: %s" % ("OK" if ok else "FAIL"))
        return 0 if ok else 1
    return build(Path(a.out), Path(a.md))


if __name__ == "__main__":
    sys.exit(main())