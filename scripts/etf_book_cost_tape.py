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

import etf_book_forward as F
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


def price_at_window(close, openp, amt, score, cost, cutoff=None):
    """The same engine and settings, but the panel cut at `cutoff` -- the card's own window.

    A control arm that prices the live panel against a card written eighteen sessions earlier
    is comparing two books, and the difference it reports is the panel's drift, not a defect
    in the engine.
    """
    if cutoff:
        idx = close.index[close.index <= pd.Timestamp(cutoff)]
        if len(idx) == 0:
            raise SystemExit("no bars at or before %s" % cutoff)
        last = idx[-1]
        close, openp = close.loc[:last], openp.loc[:last]
        amt, score = amt.loc[:last], score.loc[:last]
    st, _ = price_at(close, openp, amt, score, cost)
    return st, str(close.index[-1].date())


CARD_DIR = os.path.join(ROOT, "results", "etf_book_production")


def card_cell_name():
    return "n%d_%s" % (N_HOLD, "vt08" if TARGET_VOL else "base")


def read_card(cell_key=None):
    """The published cell this face is the control arm for -- read, never remembered.

    r2126: this used to open a path pinned to PRODUCTION-2026-10-30.json and walk a `runs`
    block the face stopped carrying, so the read raised, the handler substituted a hand
    constant copied from that card, and the control compared a live-panel run against a
    number eighteen sessions old -- the panel's own drift printed as an engine miss (r98
    family: a missing read shown as a number). The card is re-derived every session, so the
    control follows the newest one. Nothing readable => `readable=False` + a reason, and the
    caller must refuse rather than compare.
    """
    key = cell_key or card_cell_name()
    out = {"cell": key, "readable": False, "why": None, "path": None,
           "evidence_cutoff": None, "cagr": None, "settings_match": False, "config": None}
    try:
        names = sorted(n for n in os.listdir(CARD_DIR)
                       if n.startswith("PRODUCTION-") and n.endswith(".json"))
    except OSError as exc:                                           # noqa: BLE001
        out["why"] = "no card directory (%s)" % str(exc)[:80]
        return out
    if not names:
        out["why"] = "no PRODUCTION-*.json face in %s" % os.path.relpath(CARD_DIR, ROOT)
        return out
    picked = None
    ptr = os.path.join(CARD_DIR, "latest.json")
    if os.path.exists(ptr):
        try:
            cut = json.load(open(ptr, encoding="utf-8")).get("evidence_cutoff")
            cand = "PRODUCTION-%s.json" % cut
            if cut and cand in names:
                picked = cand
        except Exception as exc:                                     # noqa: BLE001
            out["why"] = "latest.json unreadable (%s)" % str(exc)[:80]
    picked = picked or names[-1]
    path = os.path.join(CARD_DIR, picked)
    try:
        out["path"] = os.path.relpath(path, ROOT).replace("\\", "/")
    except ValueError:                       # a fixture on another drive
        out["path"] = path.replace("\\", "/")
    try:
        doc = json.load(open(path, encoding="utf-8"))
    except Exception as exc:                                         # noqa: BLE001
        out["why"] = "card unreadable (%s)" % str(exc)[:80]
        return out
    out["evidence_cutoff"] = doc.get("evidence_cutoff")
    cfg = doc.get("config") or {}
    out["config"] = {k: cfg.get(k) for k in
                     ("n_hold", "rebal", "cost_bp_per_side", "vol_target")}
    out["settings_match"] = bool(
        cfg.get("n_hold") == N_HOLD
        and cfg.get("rebal") == REBAL
        and cfg.get("cost_bp_per_side") is not None
        and abs(float(cfg["cost_bp_per_side"]) - COST * 1e4) < 1e-9
        and (cfg.get("vol_target") or None) == (TARGET_VOL or None))
    full = ((doc.get("backtest") or {}).get(key) or {}).get("full") or {}
    out["cagr"] = full.get("cagr")
    out["readable"] = out["cagr"] is not None
    if not out["readable"] and not out["why"]:
        out["why"] = "card carries no backtest.%s.full.cagr" % key
    return out


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
    # r2126: the control re-prices the card's OWN window, and the distance between that and
    # the live panel is published as its own number (panel drift) instead of being charged
    # to the engine.
    card = read_card()
    same, same_bar = (None, None)
    if card.get("readable") and card.get("evidence_cutoff"):
        same, same_bar = price_at_window(close, openp, amt, score, COST,
                                        cutoff=card["evidence_cutoff"])
    engine_cagr = (same or {}).get("cagr")
    card_cagr = card.get("cagr")
    gap_pp = (None if card_cagr is None or engine_cagr is None
              else round(100.0 * (engine_cagr - float(card_cagr)), 4))
    drift_pp = (None if card_cagr is None or not base
                else round(100.0 * ((base or {}).get("cagr", 0.0) - float(card_cagr)), 4))
    control_ok = bool(card.get("readable") and card.get("settings_match")
                      and gap_pp is not None
                      and abs(gap_pp) <= CRITERIA["control_tolerance_pp"])

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
        # r1625: the width of the panel is not its identity. Two runs on 2026-10-30 and on
        # 2026-11-12 both print 1,504 symbols of 1,652 bars, so nothing could tell that this
        # face had been priced on a panel nine sessions behind the card. `prep_panel` already
        # fingerprints the full repaired panel (the same digest `etf_book_forward` publishes),
        # so the face carries it and `--check` compares it against the live panel.
        "panel": {"symbols": int(close.shape[1]), "bars": int(close.shape[0]),
                  "flip_prints_repaired": int(n_flip or 0),
                  "tape_symbols": int(spreads.shape[1]),
                  "digest": (P.PANEL_DIGEST or {}).get("digest"),
                  "last_bar": str(close.index[-1].date())},
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
        "control": {"engine_cagr_at_10bp": engine_cagr,
                    "published_cagr": card_cagr,
                    "tolerance_pp": CRITERIA["control_tolerance_pp"],
                    "passes": bool(control_ok),
                    "window_bar": same_bar,
                    "same_window_gap_pp": gap_pp,
                    "card": {"path": card.get("path"), "cell": card.get("cell"),
                             "evidence_cutoff": card.get("evidence_cutoff"),
                             "readable": bool(card.get("readable")),
                             "settings_match": bool(card.get("settings_match")),
                             "why_unreadable": card.get("why"),
                             "config": card.get("config")},
                    "live_panel": {"bar": str(close.index[-1].date()),
                                   "cagr": (base or {}).get("cagr")},
                    "panel_drift_pp": drift_pp},
        "assumption_verdict": assumption,
        "survives_verdict": ("SURVIVES" if survives else "FRAGILE") if survives is not None else "UNPRICED",
        "verdict": "%s | %s" % (assumption, ("SURVIVES" if survives else "FRAGILE") if survives is not None else "UNPRICED"),
        "generated": pd.Timestamp.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }
    payload["sentence"] = sentence(payload)
    write_json(payload, OUT_JSON)
    write_md(payload, OUT_MD)
    return payload


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
    ctl = p["control"]
    _card_cut = (ctl.get("card") or {}).get("evidence_cutoff") or "?"
    if ctl["passes"]:
        _ctl_word = "PASS"
    else:
        _ctl_word = "FAIL (%s)" % ((ctl.get("card") or {}).get("why_unreadable")
                                  or "this face was priced on another book")
    L.append("Control: the identical engine at %.0f bp, run on the card's own window"
             " (%s -> %s), reproduces the published %.1f%% within %.1fpp -> %s."
             % (CRITERIA["assumed_cost_bp"], _card_cut, ctl.get("window_bar") or "?",
                (ctl.get("published_cagr") or 0) * 100, ctl["tolerance_pp"], _ctl_word))
    if ctl.get("panel_drift_pp") is not None:
        L.append("Since that card the panel has grown to %s, where the same book reads "
                 "%.2f%% (%+.2fpp). That gap is the book moving, not the engine."
                 % ((ctl.get("live_panel") or {}).get("bar"),
                    100 * ((ctl.get("live_panel") or {}).get("cagr") or 0.0),
                    ctl["panel_drift_pp"]))
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

    # r1625: the gate has to bite, and the fixture has to be a face that passes everything
    # else -- otherwise "rc2" could be the criteria drift and the leg would prove nothing.
    clean = {"criteria": CRITERIA,
             "book": {"equivalent_cost_bp": 10.0, "ratio_vs_assumed": 1.0},
             "assumption_verdict": "AGREE",
             "arms": {"measured": {"cagr": 0.20, "sharpe": 1.50}},
             "survives_verdict": "SURVIVES",
             "control": {"passes": True}, "verdict": "AGREE | SURVIVES"}
    fx = os.path.join(tempfile.mkdtemp(prefix="ct_r1625_"), "face.json")

    def _face(panel_seed):
        d = dict(clean)
        d["panel"] = panel_seed
        with open(fx, "w", encoding="utf-8") as fh:
            json.dump(d, fh)
        return fx

    leg("a face priced on the live panel passes the stamp gate",
        check(path=_face({"digest": "aaaa"}), stamp={"digest": "aaaa"}) == 0)
    leg("a face left on an older panel fails with the word the chain rebuilds on",
        check(path=_face({"digest": "aaaa"}), stamp={"digest": "bbbb"}) == 2)
    leg("a face that carries no stamp cannot pass as fresh",
        check(path=_face({"symbols": 1504}), stamp={"digest": "aaaa"}) == 2)

    # r2126: the control's published number must be read from the card face, followed when
    # the card is re-derived, refused when the card prices a different book, and refused
    # again when there is no card -- the old code answered all four with one constant.
    cdir = tempfile.mkdtemp(prefix="ct_r2126_")
    cell = card_cell_name()

    def _card(cagr, cut="2026-10-30", cfg=None):
        d = {"evidence_cutoff": cut,
             "config": cfg or {"n_hold": N_HOLD, "rebal": REBAL,
                               "cost_bp_per_side": COST * 1e4, "vol_target": TARGET_VOL},
             "backtest": {cell: {"full": {"cagr": cagr}}}}
        with open(os.path.join(cdir, "PRODUCTION-%s.json" % cut), "w", encoding="utf-8") as fh:
            json.dump(d, fh)

    saved_dir = globals()["CARD_DIR"]
    try:
        globals()["CARD_DIR"] = cdir
        _card(0.111)
        c1 = read_card()
        leg("the published cell is read from the card face, not a remembered constant",
            c1["readable"] and abs(c1["cagr"] - 0.111) < 1e-12 and c1["settings_match"],
            "cagr=%r" % (c1.get("cagr"),))
        _card(0.222, cut="2026-11-02")
        c2 = read_card()
        leg("a re-derived card is followed to its own cutoff",
            abs(c2["cagr"] - 0.222) < 1e-12 and c2["evidence_cutoff"] == "2026-11-02")
        _card(0.05, cut="2026-11-03",
              cfg={"n_hold": 5, "rebal": REBAL, "cost_bp_per_side": COST * 1e4,
                   "vol_target": TARGET_VOL})
        c3 = read_card()
        leg("a card priced on another book is flagged instead of compared",
            c3["readable"] and not c3["settings_match"], "%r" % (c3.get("config"),))
        globals()["CARD_DIR"] = os.path.join(cdir, "absent")
        c4 = read_card()
        leg("an unreadable card is a refusal with a reason, never a substituted number",
            not c4["readable"] and c4["cagr"] is None and bool(c4["why"]), "%r" % (c4.get("why"),))
        globals()["CARD_DIR"] = cdir
        _card(0.333, cut="2026-11-04")
        stale = dict(clean, control={"passes": True,
                                     "card": {"path": "results/etf_book_production/PRODUCTION-2026-10-30.json",
                                              "cell": cell, "evidence_cutoff": "2026-10-30",
                                              "readable": True},
                                     "published_cagr": 0.333, "engine_cagr_at_10bp": 0.333,
                                     "same_window_gap_pp": 0.0,
                                     "live_panel": {"bar": "2026-11-04", "cagr": 0.333},
                                     "panel_drift_pp": 0.0})
        stale["panel"] = {"digest": "aaaa"}
        with open(fx, "w", encoding="utf-8") as fh:
            json.dump(stale, fh)
        leg("a face priced on a card that has since been rebuilt says STALE (the word the chain rebuilds on)",
            check(path=fx, stamp={"digest": "aaaa"}) == 2)
    finally:
        globals()["CARD_DIR"] = saved_dir


    ok = all(l["pass"] for l in legs)
    print(json.dumps({"selftest": "PASS" if ok else "FAIL", "legs": legs}, ensure_ascii=False, indent=1))
    return 0 if ok else 1


# --------------------------------------------------------------------------- check
def check(path=OUT_JSON, stamp=None):
    if not os.path.exists(path):
        print("no face at %s" % path)
        return 2
    p = json.load(open(path, encoding="utf-8"))
    # r1625: every assertion below re-derives from the numbers this file already publishes,
    # so this leg was green on any panel. The chain pays a refresh only when a probe says
    # `stale`, so a face priced on 2026-10-30 read as current while the card priced
    # 2026-11-12 -- the r1249 shape, one face further down (r1624 fixed the vol-window pair).
    rc = F.check_panel_stamp(p, stamp=stamp, label="cost tape")
    if rc != 0:
        return rc
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
    # r2126: the card face is re-derived every session, so a face priced against an older
    # one is stale by construction -- and that has to be SAID with the word the chain pays
    # a rewrite on (r1850), not silently compared to a number nobody reads any more.
    ctl = p.get("control") or {}
    fc = ctl.get("card") or {}
    if fc.get("path") or fc.get("evidence_cutoff"):
        card = read_card(fc.get("cell"))
        if card.get("readable") and (card.get("path") != fc.get("path")
                                     or card.get("evidence_cutoff") != fc.get("evidence_cutoff")):
            print(json.dumps({"check": "STALE",
                              "why": "card face moved: priced on %s (%s), on disk now %s (%s)"
                                     % (fc.get("evidence_cutoff"), fc.get("path"),
                                        card.get("evidence_cutoff"), card.get("path"))},
                             ensure_ascii=False))
            return 2
        if card.get("readable") and not fc.get("readable"):
            print(json.dumps({"check": "STALE",
                              "why": "this face recorded the card as unreadable (%s) but %s reads"
                                     % (fc.get("why_unreadable"), card.get("path"))},
                             ensure_ascii=False))
            return 2
    lp = ctl.get("live_panel") or {}
    if ctl.get("published_cagr") is not None and lp.get("cagr") is not None:
        want = round(100.0 * (lp["cagr"] - float(ctl["published_cagr"])), 4)
        if ctl.get("panel_drift_pp") is None or abs(ctl["panel_drift_pp"] - want) > 1e-6:
            bad.append("published drift %r does not match its own live panel and card (%.4f)"
                       % (ctl.get("panel_drift_pp"), want))
    if ctl.get("engine_cagr_at_10bp") is not None and ctl.get("published_cagr") is not None:
        want = round(100.0 * (ctl["engine_cagr_at_10bp"] - float(ctl["published_cagr"])), 4)
        if ctl.get("same_window_gap_pp") is None or abs(ctl["same_window_gap_pp"] - want) > 1e-6:
            bad.append("same-window gap %r is not engine minus card (%.4f)"
                       % (ctl.get("same_window_gap_pp"), want))
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