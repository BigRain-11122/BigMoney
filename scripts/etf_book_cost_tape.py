"""Does the tape agree with the 10 bp/side the book charges itself?

The production card prices every leg at a flat 10 bp per side. That number is an
assumption: no measurement has ever asked what these ETFs actually quote. This face
estimates each name's effective spread from its own high/low (Corwin & Schultz 2012,
`2*(exp(a)-1)/(1+exp(a))` where `a` comes from the two-day high-low variance identity),
takes the spreads of the names the book ACTUALLY traded at each decision, and re-prices
the same engine at the turnover-weighted measured cost.

Nothing is re-implemented: the panel/score come from `etf_book_production.prep_panel`
(the production universe, repaired prints included) and the equity path from
`etf_robust_pf.open_to_open_equity` (the engine the card is priced by). The measured cost
enters as the scalar the engine already takes -- the equivalent cost is defined as
`sum(|dw| * halfspread) / sum(|dw|)`, which is exactly the scalar the engine charges.

Two honest limits, printed on the face:

  * the estimator is a proxy, not a quote tape. It reads the *effective* spread implied by
    the day's range, which for a wide-range day includes volatility, so the upper arm
    (each name's own 75th percentile) is the pessimistic bound, not a forecast;
  * spreads are estimated from highs and lows, which survive a share-conversion print in
    the close, so the repair applied to the panel does not contaminate the tape.

  python scripts/etf_book_cost_tape.py run|--selftest|--check
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

import etf_book_production as P
import etf_composite_pf as E
import etf_robust_pf as R

OUT_JSON = os.path.join(ROOT, "results", "etf_book_cost_tape.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_COST_TAPE.md")

N_HOLD = 12
REBAL = 20
COST = 0.0010          # the published per-side charge
TARGET_VOL = 0.08
START = "2020-01-01"
CS_WINDOW = 20
MAX_SPREAD = 0.0100    # 100 bp: above this the high/low pair is an artefact, not a quote
MIN_COVER = 0.60       # a decision is priced only if >=60% of its traded weight has a tape

# Frozen before the first run; --check refuses a face whose criteria moved.
CRITERIA = {
    "cell": "N12_R20_10bp",
    "assumed_cost_bp": COST * 1e4,
    "cs_window": CS_WINDOW,
    "max_spread_bp": MAX_SPREAD * 1e4,
    "min_coverage": MIN_COVER,
    "control_tolerance_pp": 0.5,
    "agree_band": 0.25,          # measured within +/-25% of the assumption = AGREE
    "survive_min_cagr": 0.05,
    "survive_min_sharpe": 0.60,
    "frozen": "written before the first run",
}

SCHEMA = "etf_book_cost_tape/v1"


# --------------------------------------------------------------------------- estimator
def cs_spread(high, low, window=CS_WINDOW, cap=MAX_SPREAD, causal=True):
    """Relative effective spread per day (Corwin-Schultz), 20-day rolling median.

    `causal=True` lags the finished series by one bar, because the raw estimator uses
    day t and t+1's range. A decision on bar t must not see t+1.
    """
    hi = high.astype(float)
    lo = low.astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        hl = (np.log(hi) - np.log(lo)) ** 2
        beta = hl + hl.shift(-1)
        hi2 = pd.Series(np.maximum(hi.values, hi.shift(-1).values), index=hi.index)
        lo2 = pd.Series(np.minimum(lo.values, lo.shift(-1).values), index=lo.index)
        gamma = (np.log(hi2) - np.log(lo2)) ** 2
        k = 3.0 - 2.0 * np.sqrt(2.0)
        alpha = (np.sqrt(2.0 * beta) - np.sqrt(beta)) / k - np.sqrt(gamma / k)
        s = 2.0 * (np.exp(alpha) - 1.0) / (1.0 + np.exp(alpha))
    s = s.replace([np.inf, -np.inf], np.nan)
    s = s.clip(lower=0.0, upper=cap)
    s = s.rolling(window, min_periods=max(5, window // 2)).median()
    if causal:
        s = s.shift(1)
    return s


def tape_spreads(prices, columns):
    """date x symbol relative spread frame for the production columns."""
    out = {}
    for s in columns:
        df = prices.get(s)
        if df is None or "high" not in df or "low" not in df:
            continue
        if len(df) < CS_WINDOW * 2:
            continue
        sp = cs_spread(df["high"], df["low"])
        if sp.notna().sum() < 60:
            continue
        out[s] = sp
    if not out:
        return pd.DataFrame()
    return pd.DataFrame(out).sort_index()


# --------------------------------------------------------------------------- book cost
def equivalent_cost(rows):
    """scalar the engine would have to charge to bill the same money.

    rows: [{turn, money, covered}] -> dict. None when the book never traded: a scalar
    cannot be inferred from zero turnover, and printing 0.0 would read as "free".
    """
    turn = sum(r["turn"] for r in rows)
    money = sum(r["money"] for r in rows)
    if turn <= 1e-12:
        return {"equivalent_cost": None, "turnover": float(turn), "money": float(money)}
    return {"equivalent_cost": float(money) / float(turn), "turnover": float(turn),
            "money": float(money)}


def measure(close, openp, amt, score, spreads, cost=COST, target=TARGET_VOL,
            n_hold=N_HOLD, rebal=REBAL):
    diag = []
    R.open_to_open_equity(close, openp, amt, score, rebal, n_hold, cost,
                          vol_target=target, diag=diag)
    sp = spreads.reindex(index=close.index).ffill()
    held = {}
    rows = []
    for d in diag:
        date = pd.Timestamp(d["date"])
        book = list(d["book"])
        scale = float(d["scale"])
        w = {p: scale / len(book) for p in book}
        row = sp.loc[date] if date in sp.index else None
        turn = money = covered = 0.0
        missing = []
        dws = {}
        for k in set(w) | set(held):
            dw = abs(w.get(k, 0.0) - held.get(k, 0.0))
            turn += dw
            if dw <= 0:
                continue
            dws[k] = dw
            v = None if row is None else row.get(k)
            if v is None or not np.isfinite(v):
                missing.append(k)
                continue
            money += dw * (float(v) / 2.0)      # half spread = cost per side
            covered += dw
        rows.append({"date": str(date.date()), "turn": turn, "money": money,
                     "covered": covered, "coverage": (covered / turn) if turn > 0 else 0.0,
                     "dws": dws, "missing": missing[:6]})
        held = w
    return rows, sp


def name_percentiles(spreads, traded):
    """per-name percentile spread (bps of price, i.e. relative spread) over time."""
    out = {}
    for s in sorted(traded):
        if s not in spreads.columns:
            continue
        v = spreads[s].dropna()
        if len(v) < 100:
            continue
        out[s] = {"p50": float(v.quantile(0.50)), "p75": float(v.quantile(0.75)),
                  "p90": float(v.quantile(0.90)), "n": int(len(v))}
    return out


def price_at(close, openp, amt, score, cost):
    eq, _ = R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, cost,
                                  vol_target=TARGET_VOL)
    return R.stats(eq, "cell"), eq


# --------------------------------------------------------------------------- run
def run():
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    prices = E._dedupe(E._load_prices())
    spreads = tape_spreads(prices, list(close.columns))
    if spreads.empty:
        raise SystemExit("no tape: every production column is missing high/low")

    rows, sp = measure(close, openp, amt, score, spreads)
    usable = [r for r in rows if r["turn"] > 0 and r["coverage"] >= MIN_COVER]
    dropped = [r for r in rows if r["turn"] > 0 and r["coverage"] < MIN_COVER]
    eq_measured = equivalent_cost(usable)
    # the traded set = names the book ever held, read back from a diag run
    traded = set()
    diag = []
    R.open_to_open_equity(close, openp, amt, score, REBAL, N_HOLD, COST,
                          vol_target=TARGET_VOL, diag=diag)
    for d in diag:
        traded |= set(d["book"])
    per_name = name_percentiles(spreads, traded)

    # upper arm: every name priced at its own 75th percentile, weighted by the turnover
    # this book actually did in that name (not an unweighted mean over the tape).
    upper_scalar = None
    if per_name:
        num = den = 0.0
        for r in usable:
            for k, dw in r["dws"].items():
                if k not in per_name:
                    continue
                num += dw * per_name[k]["p75"] / 2.0
                den += dw
        upper_scalar = num / den if den else None

    base, _ = price_at(close, openp, amt, score, COST)
    measured, _ = price_at(close, openp, amt, score,
                           eq_measured["equivalent_cost"]) if eq_measured["equivalent_cost"] else (None, None)
    upper, _ = price_at(close, openp, amt, score, upper_scalar) if upper_scalar else (None, None)

    assumed = CRITERIA["assumed_cost_bp"]
    meas_bp = (eq_measured["equivalent_cost"] or 0.0) * 1e4
    ratio = meas_bp / assumed if assumed else None
    band = CRITERIA["agree_band"]
    if ratio is None or not np.isfinite(ratio):
        assumption = "UNMEASURED"
    elif ratio > 1 + band:
        assumption = "OPTIMISTIC"
    elif ratio < 1 - band:
        assumption = "CONSERVATIVE"
    else:
        assumption = "AGREE"
    survives = None
    if measured:
        survives = bool(measured["cagr"] >= CRITERIA["survive_min_cagr"]
                        and measured["sharpe"] >= CRITERIA["survive_min_sharpe"])
    published = CARD_CAGR
    try:
        published = float((json.load(open(os.path.join(
            ROOT, "results", "etf_book_production", "PRODUCTION-2026-10-30.json"),
            encoding="utf-8")).get("runs", {}).get("n%d_vt08" % N_HOLD, {}).get("full", {})
            or {}).get("cagr", CARD_CAGR))
    except Exception:
        published = CARD_CAGR
    control_ok = abs((base or {}).get("cagr", 0.0) - published) <= CRITERIA["control_tolerance_pp"] / 100.0

    widest = sorted(per_name.items(), key=lambda kv: -kv[1]["p50"])[:5]
    payload = {
        "schema": SCHEMA,
        "script": "scripts/etf_book_cost_tape.py",
        "face": "results/etf_book_cost_tape.json",
        "evidence_cutoff": str(close.index[-1].date()),
        "question": ("the card charges every leg a flat 10 bp/side -- what do these names"
                     " actually quote, and does the book survive the tape's answer?"),
        "engine": ("etf_book_production.prep_panel (production universe, repaired prints)"
                   " + etf_robust_pf.open_to_open_equity (the card's own engine)"),
        "estimator": ("Corwin-Schultz (2012) effective spread from daily high/low,"
                      " 20-day rolling median, lagged one bar so a decision cannot see t+1"),
        "criteria": CRITERIA,
        "panel": {"symbols": int(close.shape[1]), "bars": int(close.shape[0]),
                  "flip_prints_repaired": int(n_flip or 0),
                  "tape_symbols": int(spreads.shape[1])},
        "decisions": {"total": len(rows), "priced": len(usable), "dropped_low_coverage": len(dropped),
                      "dropped_examples": [r["date"] for r in dropped[:5]]},
        "book": {"equivalent_cost_bp": round(meas_bp, 2) if meas_bp else None,
                 "turnover_total": round(eq_measured["turnover"], 4),
                 "cost_money_total": round(eq_measured["money"], 6),
                 "ratio_vs_assumed": round(ratio, 3) if ratio else None,
                 "upper_scalar_bp": round(upper_scalar * 1e4, 2) if upper_scalar else None},
        "tape": {"n_traded_names": len(per_name),
                 "median_name_p50_bp": round(1e4 * float(np.median([v["p50"] for v in per_name.values()])), 1) if per_name else None,
                 "median_name_p75_bp": round(1e4 * float(np.median([v["p75"] for v in per_name.values()])), 1) if per_name else None,
                 "widest_traded": [{"symbol": k, "p50_bp": round(1e4 * v["p50"], 1),
                                    "p90_bp": round(1e4 * v["p90"], 1)} for k, v in widest]},
        "arms": {"assumed_10bp": base, "measured": measured, "upper_p75": upper},
        "control": {"engine_cagr_at_10bp": (base or {}).get("cagr"),
                    "published_cagr": published,
                    "tolerance_pp": CRITERIA["control_tolerance_pp"],
                    "passes": bool(control_ok)},
        "assumption_verdict": assumption,
        "survives_verdict": ("SURVIVES" if survives else "FRAGILE") if survives is not None else "UNPRICED",
        "verdict": "%s | %s" % (assumption, ("SURVIVES" if survives else "FRAGILE") if survives is not None else "UNPRICED"),
        "generated": pd.Timestamp.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }
    payload["sentence"] = sentence(payload)
    write_json(payload, OUT_JSON)
    write_md(payload, OUT_MD)
    return payload


CARD_CAGR = 0.096       # results/etf_book_production/CARD.md, 2020-01 onwards


def sentence(p):
    b = p["book"]
    if not b["equivalent_cost_bp"]:
        return "the book never traded, so no cost can be inferred"
    m = p["arms"]["measured"] or {}
    u = p["arms"]["upper_p75"] or {}
    assumed = p["criteria"]["assumed_cost_bp"]
    toward = {"CONSERVATIVE": "more than the tape says (the card over-charges)",
              "OPTIMISTIC": "less than the tape says (the card under-charges)",
              "AGREE": "about what the tape says"}.get(p["assumption_verdict"], "unmeasured")
    return ("the names this book actually traded quote a measured one-way cost of %.1f bp"
            " half-spread; the card charges %.0f bp, which is %s -- on the tape's cost the"
            " same engine earns %.1f%% CAGR / %.2f Sharpe (each name at its own 75th"
            " percentile: %.1f%% / %.2f), so the book %s the measured cost"
            % (b["equivalent_cost_bp"], assumed, toward,
               (m.get("cagr") or 0.0) * 100.0, (m.get("sharpe") or 0.0),
               (u.get("cagr") or 0.0) * 100.0, (u.get("sharpe") or 0.0),
               "survives" if p["survives_verdict"] == "SURVIVES" else "does not survive"))


def read_published(path=None):
    """Consumer entry point: the measured cost, or an honest gap (r1198).

    The card, the ticket and the CEO page all restate "every side costs 10 bp", and until
    r1195 nobody had measured it. They must not each re-open the artifact and re-decide
    what it says (E289 family), so the read travels through this one function.

    The control arm travels with the read: a face whose re-price at the assumed cost does
    not reproduce the published CAGR is not evidence about the cost assumption -- it is a
    different book -- so it reads as `no_control` and callers print no numbers at all.
    """
    p = path or OUT_JSON
    if not os.path.exists(p):
        return {"status": "absent", "artifact": str(p), "verdict": None,
                "sentence": None, "evidence_cutoff": None}
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
    except Exception as exc:                                        # noqa: BLE001
        return {"status": "unreadable: %s" % str(exc)[:120], "artifact": str(p),
                "verdict": None, "sentence": None, "evidence_cutoff": None}
    ctl = doc.get("control") or {}
    if not ctl.get("passes"):
        return {"status": "no_control", "artifact": str(p),
                "verdict": doc.get("verdict"), "sentence": None, "evidence_cutoff": None,
                "detail": "re-price at %.0f bp gave %r vs published %r (tolerance %r pp)"
                          % (float((doc.get("criteria") or {}).get("assumed_cost_bp") or 0.0),
                             ctl.get("engine_cagr_at_10bp"), ctl.get("published_cagr"),
                             ctl.get("tolerance_pp"))}
    arms = doc.get("arms") or {}
    bk = doc.get("book") or {}
    tape = doc.get("tape") or {}
    crit = doc.get("criteria") or {}

    def _arm(k):
        a = arms.get(k) or {}
        return {"cagr": a.get("cagr"), "sharpe": a.get("sharpe"), "maxdd": a.get("maxdd"),
                "vol": a.get("vol"), "worst_month": a.get("worst_month"),
                "worst_year": a.get("worst_year")}

    return {
        "status": "ok",
        "artifact": str(p),
        "evidence_cutoff": doc.get("evidence_cutoff"),
        "verdict": doc.get("verdict"),
        "assumption_verdict": doc.get("assumption_verdict"),
        "survives_verdict": doc.get("survives_verdict"),
        "sentence": doc.get("sentence"),
        "assumed_bp": crit.get("assumed_cost_bp"),
        "measured_bp": bk.get("equivalent_cost_bp"),
        "upper_p75_bp": bk.get("upper_scalar_bp"),
        "ratio_vs_assumed": bk.get("ratio_vs_assumed"),
        "turnover_total": bk.get("turnover_total"),
        "arms": {k: _arm(k) for k in ("assumed_10bp", "measured", "upper_p75")},
        "tape": {"n_traded_names": tape.get("n_traded_names"),
                 "median_name_p50_bp": tape.get("median_name_p50_bp"),
                 "median_name_p75_bp": tape.get("median_name_p75_bp"),
                 "widest_traded": (tape.get("widest_traded") or [])[:3]},
        "control": {"passes": ctl.get("passes"),
                    "engine_cagr": ctl.get("engine_cagr_at_10bp"),
                    "published_cagr": ctl.get("published_cagr"),
                    "tolerance_pp": ctl.get("tolerance_pp")},
        "decisions": {"priced": (doc.get("decisions") or {}).get("priced"),
                      "dropped_low_coverage":
                          (doc.get("decisions") or {}).get("dropped_low_coverage")},
    }


def write_json(payload, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def write_md(p, path):
    a = p["arms"]
    L = []
    L.append("# ETF book -- what the tape says a side costs (cutoff %s)\n" % p["evidence_cutoff"])
    L.append(p["question"] + "\n")
    L.append("**Verdict: %s**\n" % p["verdict"])
    L.append(p["sentence"] + "\n")
    L.append("| arm | cost / side | CAGR | Sharpe | max drawdown |")
    L.append("|---|---|---|---|---|")
    for key, label in (("assumed_10bp", "the card's assumption"), ("measured", "the tape (turnover weighted)"),
                       ("upper_p75", "tape, every name at its own p75")):
        s = a.get(key) or {}
        if not s:
            continue
        c = {"assumed_10bp": "10.0 bp", "measured": ("%.1f bp" % (p["book"]["equivalent_cost_bp"] or 0)),
             "upper_p75": ("%.1f bp" % (p["book"].get("upper_scalar_bp") or 0))}[key]
        L.append("| %s | %s | %.1f%% | %.2f | %.1f%% |" % (
            label, c, (s.get("cagr") or 0) * 100, s.get("sharpe") or 0, (s.get("maxdd") or 0) * 100))
    L.append("")
    L.append("Control: the identical engine at 10 bp reproduces the published %.1f%% within %.1fpp -> %s."
             % ((p["control"]["published_cagr"] or 0) * 100, p["control"]["tolerance_pp"],
                "PASS" if p["control"]["passes"] else "FAIL"))
    L.append("")
    t = p["tape"]
    L.append("Tape: %d traded names carry an estimate (median own-median %.1f bp, median p75 %.1f bp of price). "
             "Widest traded names: %s."
             % (t["n_traded_names"], t["median_name_p50_bp"] or 0, t["median_name_p75_bp"] or 0,
                ", ".join("%s %s bp" % (w["symbol"], w["p50_bp"]) for w in t["widest_traded"])))
    L.append("")
    L.append("Decisions priced %d of %d (%d dropped: fewer than %.0f%% of the traded weight had a tape on that bar)."
             % (p["decisions"]["priced"], p["decisions"]["total"],
                p["decisions"]["dropped_low_coverage"], 100 * CRITERIA["min_coverage"]))
    L.append("")
    L.append("How to read it: the estimator is a proxy, not a quote tape -- on a wide-range day the "
             "implied spread absorbs volatility, which is why the p75 arm is the pessimistic bound "
             "and not a forecast. The measured arm is the number to compare with the 10 bp the card "
             "charges; the p75 arm is what happens if the whole book trades at the wide end of its own "
             "history. Criteria were frozen before the first run (%s)."
             % CRITERIA["frozen"])
    L.append("")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L))


# --------------------------------------------------------------------------- selftest
def selftest():
    legs = []

    def leg(name, ok, note=""):
        legs.append({"leg": name, "pass": bool(ok), "note": note})

    idx = pd.date_range("2020-01-01", periods=200, freq="B")
    mid = pd.Series(1.0, index=idx)

    def band(bp):
        h = mid * (1 + bp / 1e4 / 2)
        l = mid * (1 - bp / 1e4 / 2)
        return h, l

    h20, l20 = band(20)
    h60, l60 = band(60)
    s20 = cs_spread(h20, l20, causal=False)
    s60 = cs_spread(h60, l60, causal=False)
    leg("a wider band yields a wider estimate",
        float(s60.median()) > float(s20.median()),
        "20bp->%.4f 60bp->%.4f" % (float(s20.median()), float(s60.median())))

    h_big, l_big = band(500)          # 5% band -> above the 100 bp cap
    s_big = cs_spread(h_big, l_big, causal=False)
    leg("the estimator is capped", float(s_big.max()) <= MAX_SPREAD + 1e-12,
        "max=%.5f cap=%.5f" % (float(s_big.max()), MAX_SPREAD))

    leg("short series stays NaN", bool(cs_spread(h20.iloc[:6], l20.iloc[:6]).isna().all()))

    # causality: changing days t+2.. must not move the value at t
    h2 = h20.copy()
    l2 = l20.copy()
    h2.iloc[120:] = h2.iloc[120:] * 1.2
    l2.iloc[120:] = l2.iloc[120:] * 0.8
    a1 = cs_spread(h20, l20)
    a2 = cs_spread(h2, l2)
    same = np.allclose(a1.iloc[:115].fillna(-1).values, a2.iloc[:115].fillna(-1).values)
    leg("a decision cannot see tomorrow (future edit leaves past values alone)", same)

    rows = [{"turn": 0.5, "money": 0.5 * 0.002, "covered": 0.5},
            {"turn": 1.5, "money": 1.5 * 0.002, "covered": 1.5}]
    ec = equivalent_cost(rows)
    leg("equal spreads give that spread back regardless of turnover",
        abs(ec["equivalent_cost"] - 0.002) < 1e-12, "%.6f" % ec["equivalent_cost"])

    leg("zero turnover is unmeasured, not free",
        equivalent_cost([{"turn": 0.0, "money": 0.0, "covered": 0.0}])["equivalent_cost"] is None)

    # half-spread convention: a 20 bp relative spread costs 10 bp per side
    rows = [{"turn": 1.0, "money": 0.001, "covered": 1.0}]
    leg("half spread is charged per side",
        abs(equivalent_cost(rows)["equivalent_cost"] - 0.001) < 1e-12)

    payload = {"arms": {"measured": {"cagr": 0.08, "sharpe": 0.9},
                        "upper_p75": {"cagr": 0.06, "sharpe": 0.6}},
               "book": {"equivalent_cost_bp": 12.0, "ratio_vs_assumed": 1.2},
               "criteria": {"assumed_cost_bp": 10.0},
               "assumption_verdict": "AGREE", "survives_verdict": "SURVIVES"}
    s = sentence(payload)
    leg("the sentence quotes the arms it came from",
        "12.0 bp" in s and "8.0% CAGR" in s and "percentile: 6.0%" in s, s[-60:])

    # r1198: the consumer read. Three faces restate the 10 bp assumption and they must all
    # get the same answer from one place; a control that does not reproduce the published
    # CAGR must read as "no evidence", never as "the card is conservative".
    import tempfile
    absent = read_published(os.path.join(tempfile.gettempdir(), "ct_absent_r1198.json"))
    leg("absent artifact reads absent, never 'free'",
        absent["status"] == "absent" and absent["verdict"] is None and absent["sentence"] is None)

    good = {"control": {"passes": True}, "evidence_cutoff": "2026-10-30",
            "criteria": {"assumed_cost_bp": 10.0}, "assumption_verdict": "CONSERVATIVE",
            "survives_verdict": "SURVIVES", "verdict": "CONSERVATIVE | SURVIVES",
            "sentence": "measured 5.9 bp", "arms": {"measured": {"cagr": 0.1}},
            "book": {"equivalent_cost_bp": 5.9}, "tape": {}, "decisions": {}}
    bad_ctl = dict(good, control={"passes": False, "engine_cagr_at_10bp": 0.12,
                                  "published_cagr": 0.096, "tolerance_pp": 0.5})
    tmpdir = tempfile.mkdtemp(prefix="ct_r1198_")
    p_good = os.path.join(tmpdir, "ok.json")
    p_bad = os.path.join(tmpdir, "bad.json")
    with open(p_good, "w", encoding="utf-8") as fh:
        json.dump(good, fh)
    with open(p_bad, "w", encoding="utf-8") as fh:
        json.dump(bad_ctl, fh)
    r_good = read_published(p_good)
    r_bad = read_published(p_bad)
    leg("a clean artifact hands back the published cost and verdict",
        r_good["status"] == "ok" and r_good["measured_bp"] == 5.9
        and r_good["verdict"] == "CONSERVATIVE | SURVIVES")
    leg("a face whose control re-price misses the published CAGR reads no_control and carries no sentence",
        r_bad["status"] == "no_control" and r_bad["sentence"] is None,
        "control would have claimed 12.0% vs published 9.6%")

    ok = all(l["pass"] for l in legs)
    print(json.dumps({"selftest": "PASS" if ok else "FAIL", "legs": legs}, ensure_ascii=False, indent=1))
    return 0 if ok else 1


# --------------------------------------------------------------------------- check
def check():
    if not os.path.exists(OUT_JSON):
        print("no face at %s" % OUT_JSON)
        return 2
    p = json.load(open(OUT_JSON, encoding="utf-8"))
    bad = []
    if p.get("criteria") != CRITERIA:
        bad.append("criteria moved")
    b = p.get("book") or {}
    assumed = CRITERIA["assumed_cost_bp"]
    ratio = b.get("ratio_vs_assumed")
    if b.get("equivalent_cost_bp") and ratio:
        band = CRITERIA["agree_band"]
        want = "AGREE" if 1 - band <= ratio <= 1 + band else ("OPTIMISTIC" if ratio > 1 + band else "CONSERVATIVE")
        if p.get("assumption_verdict") != want:
            bad.append("assumption verdict does not match its own ratio")
    m = (p.get("arms") or {}).get("measured") or {}
    if m:
        want = "SURVIVES" if (m.get("cagr", 0) >= CRITERIA["survive_min_cagr"]
                              and m.get("sharpe", 0) >= CRITERIA["survive_min_sharpe"]) else "FRAGILE"
        if p.get("survives_verdict") != want:
            bad.append("survival verdict does not match its own arms")
    if not (p.get("control") or {}).get("passes"):
        bad.append("control does not reproduce the published cell")
    print(json.dumps({"check": "OK" if not bad else "BAD", "problems": bad,
                      "verdict": p.get("verdict")}, ensure_ascii=False))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest or a.cmd == "selftest":
        return selftest()
    if a.check or a.cmd == "check":
        return check()
    p = run()
    print(json.dumps({"verdict": p["verdict"], "cost_bp": p["book"]["equivalent_cost_bp"],
                      "arms": {k: (v or {}).get("cagr") for k, v in p["arms"].items()}},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())