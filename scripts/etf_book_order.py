"""ETF composite book -- the same book, sold at a stated beta, with a real cash leg.

Five rounds of stress tests (r1251-r1255) ended on three findings worth acting on:

  * the package's value is the removal of the phase choice, never alpha (p=0.62);
  * 66% of its 2024+ lead over its own equal weight was just extra beta (0.295 vs 0.066);
  * the cash remainder is worth reals: observed GC001 repo (2.09%/yr) beats a flat 0%
    by +1.53/+1.00/+0.46pp at beta 0.10/0.20/0.30.

This script turns those into the only artefact that can actually be executed: a daily
target-weight ticket plus a forward ledger that runs on the same accounting from now on.

Accounting (reused, never rewritten):
  * the book's own leg chain = `base.run_next_open` (close decision -> next-open fill,
    8bp/side on |weight change|, overnight to the old book, intraday to the new one);
  * the beta overlay = `BT.apply_overlay` (k = target/beta, clipped to [0,1], a decision
    taken on a close applies from the next bar, |delta k| * 8bp charged on the k leg);
  * the cash leg = `BW.load_repo_rates` + `BW.repo_daily_cash` (GC001 close is an
    annualised yield known at bar t, accrued over the calendar gap to the next bar).

Difference from the stress-test scripts: this one emits a ticket a human or a broker
adapter could follow -- instrument, weight, amount at a stated NAV, whole lots, cash
remainder -- and it accrues that book forward one bar at a time (idempotent by bar).

  python scripts/etf_book_order.py run [--beta=0.20] [--nav=1000000] [--inception=2024-01-01]
  python scripts/etf_book_order.py --selftest

Outputs:
  results/etf_book_order/state.json          book state (target, last bar, nav)
  results/etf_book_order/ledger.jsonl        one row per bar from inception
  results/etf_book_order/TICKET-<asof>.json  executable ticket + evidence
  results/etf_book_order/ORDER-<asof>.md     one-page face (regenerated per run)
  results/etf_book_order/latest.json         pointer to the newest ticket

Exploratory: not a verdict, not investment advice, no ledger booking.
"""
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import etf_composite_pf as F          # noqa: E402
from scripts import etf_phase_beta_target as BT    # noqa: E402
from scripts import etf_phase_beta_window as BW    # noqa: E402
from scripts import etf_variants_null_rolling as V  # noqa: E402
from scripts import etf_equity_alpha as AE          # noqa: E402
from scripts import exchange_calendar_audit as CA   # noqa: E402
from scripts.etf_asset_class import classify       # noqa: E402
from scripts.etf_book_bets_face import read_published as read_bets_face  # noqa: E402
from scripts.etf_book_concentration import read_published as read_concentration  # noqa: E402
from scripts.etf_book_cut_order_gap import trim_legs        # noqa: E402  (r1455: one trim rule)
from config import PATHS                           # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(PATHS.results_dir, "etf_book_order")

REBAL = 20
N_HOLD = F.N_HOLD
COST_BP = 8.0
DEFAULT_BETA = 0.20
DEFAULT_NAV = 1_000_000.0
DEFAULT_INCEPTION = "2024-01-01"
MIN_HIST = 126
LOT = 100
# r1177: this sheet repairs quote flips before it measures anything, like the card and the
# forward ledger already did. It was the last live face ranking on raw prices, so a
# share-count flip could enter a pick here and nowhere else, and the two faces of one book
# were quoting a CAGR computed on two different panels. The size of the correction is
# priced, not assumed: results/etf_book_flip_contamination.json (verdict MATERIAL).
REPAIR_PANEL = True
PRICE_BASIS_ARTIFACT = "results/etf_book_flip_contamination.json"


# ------------------------------------------------------------------ decision schedule
def k_schedule(rp, rm, target, step=REBAL, min_hist=MIN_HIST):
    """[(decision_date, k, beta_hat)] under r1254's expanding-beta rule.

    beta is the expanding OLS slope of the book on the market through the decision
    day only; k = target/beta clipped to [0,1] -- de-risking only, never leverage.
    """
    var = rm.expanding(min_periods=2).var()
    cov = rp.expanding(min_periods=2).cov(rm)
    beta = cov / var
    out = []
    i = int(min_hist)
    while i < len(rp):
        b = beta.iloc[i]
        if b is None or not np.isfinite(b) or b <= 1e-6:
            i += step
            continue
        out.append((rp.index[i], float(min(1.0, max(0.0, target / b))), float(b)))
        i += step
    return out


def in_force(sched, dates):
    """k applied to each bar's return: a decision made on a close applies next bar."""
    if not sched:
        return pd.Series(np.nan, index=dates, dtype=float)
    marks = pd.Series(np.nan, index=dates, dtype=float)
    for d, k, _ in sched:
        if d in marks.index:
            marks.loc[d] = k
    return marks.shift(1).ffill()


# ---------------------------------------------------------------------------- ticket
def build_ticket(score_last, close_last, k, nav, n_hold=N_HOLD, lot=LOT, classes=None,
                 k_rule=None):
    """Whole-lot order sheet: k of NAV spread equally over the picks, rest to GC001.

    Weights always sum to 1 (book + cash). Amounts are floor'ed to whole lots, so the
    ticket can only ever spend less than NAV -- the unspent remainder stays in cash and
    is reported, never silently redistributed.

    r1471: `k` is the size this sheet ORDERS (read off the executed account when one is
    published); `k_rule` is what the sizing rule alone would say. Both travel on the
    ticket, because "which book did you size from" is the question that costs 67,852 CNY
    when it goes unasked.
    """
    s = score_last.dropna()
    if len(s) < n_hold:
        return None
    picks = list(s.nlargest(n_hold).index)
    w_each = float(k) / len(picks)
    rows, spent = [], 0.0
    for p in picks:
        px = close_last.get(p, np.nan)
        if not np.isfinite(px) or px <= 0:
            rows.append({"symbol": p, "weight": round(w_each, 6), "price": None,
                         "lots": None, "shares": None, "amount": None,
                         "class": (classes or {}).get(p), "note": "no live price"})
            continue
        want = nav * w_each
        lots = int(want // (px * lot))
        shares = lots * lot
        amt = shares * px
        spent += amt
        rows.append({"symbol": p, "weight": round(w_each, 6), "price": round(float(px), 4),
                     "lots": lots, "shares": shares, "amount": round(amt, 2),
                     "class": (classes or {}).get(p),
                     "note": "" if lots else "budget below one lot"})
    cash_amt = float(nav) - spent
    return {"beta_k": round(float(k), 6),
            "beta_k_rule": None if k_rule is None else round(float(k_rule), 6),
            "book_weight": round(float(k), 6),
            "cash_weight": round(1.0 - float(k), 6),
            "nav": float(nav), "order": rows,
            "book_amount": round(spent, 2), "cash_amount": round(cash_amt, 2),
            "cash_leg": "GC001 (1-day repo, observed close)",
            "basket_drift": [n["symbol"] for n in rows if n["amount"] is None],
            "underspend_pct": round(100.0 * cash_amt / float(nav) - 100.0 * (1.0 - k), 4)}


def reprice_block(legacy, ticket, dec_bar, asof):
    """What this sheet used to say, and what it says now that it prices the bar you pay.

    The weights must come from the DECISION bar -- the book is not re-ranked between grid
    dates, and ranking the panel's last bar hands the operator a book the engine never
    held. The *prices* are a different question: an order placed on `asof` pays the
    `asof` print, so quoting the decision bar's close made every lot count and amount a
    twelve-day-old arithmetic while the header claimed "priced bar = asof / current".
    Measured on the 2026-10-30 sheet: 159501 was quoted 2.229 against a bar that closed
    2.158 (+3.3%), the four other names drifted 1.3%-5.3%, and the "unspent" line was an
    artefact of that stale price rather than of lot granularity.

    One measurement, two arms: `legacy` is the same ticket priced on the decision bar,
    `ticket` the same ticket priced on the priced bar. A name with no price on the priced
    bar is REPORTED (priced_price None) and never back-filled from the decision bar.
    """
    if not legacy or not ticket:
        return {"status": "unavailable",
                "sentence": "one of the two price bases could not be built, so this sheet "
                            "cannot say what changed since the decision bar"}
    a = {r["symbol"]: r for r in legacy["order"]}
    rows, n_rep = [], 0
    worst, amt_delta, lot_delta = 0.0, 0.0, 0
    missing = []
    for r in ticket["order"]:
        sym = r["symbol"]
        old = a.get(sym) or {}
        p_old, p_new = old.get("price"), r.get("price")
        if p_new is None or p_old is None:
            missing.append(sym)
            rows.append({"symbol": sym, "decision_price": p_old, "priced_price": p_new,
                         "drift_pct": None, "lots_at_decision": old.get("lots"),
                         "lots_at_priced": r.get("lots"),
                         "amount_at_decision": old.get("amount"),
                         "amount_at_priced": r.get("amount")})
            continue
        drift = 100.0 * (float(p_new) - float(p_old)) / float(p_old)
        if abs(float(p_new) - float(p_old)) > 1e-9:
            n_rep += 1
        worst = max(worst, abs(drift))
        amt_delta += float(r["amount"]) - float(old.get("amount") or 0.0)
        lot_delta += int(r["lots"]) - int(old.get("lots") or 0)
        rows.append({"symbol": sym, "decision_price": p_old, "priced_price": p_new,
                     "drift_pct": round(drift, 4),
                     "lots_at_decision": old.get("lots"), "lots_at_priced": r["lots"],
                     "amount_at_decision": old.get("amount"),
                     "amount_at_priced": r["amount"]})
    if missing:
        verdict = "PRICE_MISSING_ON_PRICED_BAR"
        sentence = ("%d of %d names have no print on the priced bar (%s); those rows are "
                    "left unfilled rather than priced off the decision bar"
                    % (len(missing), len(ticket["order"]), ", ".join(missing)))
    elif n_rep == 0:
        verdict = "SAME_PRICES_ON_BOTH_BARS"
        sentence = ("the decision bar and the priced bar carry the same close for all %d "
                    "names, so this sheet's amounts are the same under either reading"
                    % len(ticket["order"]))
    else:
        verdict = "REPRICED_TO_THE_BAR_YOU_PAY"
        sentence = ("%d of %d names moved between the decision bar (%s) and the priced bar "
                    "(%s); worst drift %.2f%%, whole book %+.0f CNY and %+d lots versus the "
                    "same weights priced on the decision bar"
                    % (n_rep, len(ticket["order"]), dec_bar, asof, worst, amt_delta, lot_delta))
    return {"status": "ok", "verdict": verdict, "decision_bar": str(dec_bar),
            "priced_bar": str(asof), "n_names": len(ticket["order"]),
            "n_repriced": n_rep, "worst_drift_pct": round(worst, 4),
            "amount_delta_cny": round(amt_delta, 2), "lots_delta": lot_delta,
            "missing": missing, "names": rows, "sentence": sentence}


# ----------------------------------------------------------------------------- ledger
def accrue(state, dates, rp, rm, fees_k, rf, sched_k, cost_bp=COST_BP):
    """Name it forward: one row per bar, the k changes charge |delta k| * cost.

    The book leg (rp) already carries its own next-open fill costs and the overlay's
    k leg is charged here -- two layers by design, each on its own notional.
    """
    state = json.loads(json.dumps(state))
    last = state.get("last_bar")
    rows = []
    equity = float(state.get("nav", 1.0))
    prev_k = None if state.get("last_k") is None else float(state["last_k"])
    prev_date = None
    for d in dates:
        if last is not None and d <= pd.Timestamp(last):
            continue
        cost = 0.0 if prev_k is None else abs(float(fees_k.loc[d]) - prev_k) * cost_bp / 10000.0
        rf_day = float(rf.get(d, 0.0) or 0.0) if isinstance(rf, pd.Series) else float(rf)
        r = float(fees_k.loc[d]) * float(rp.loc[d]) + (1.0 - float(fees_k.loc[d])) * rf_day
        equity *= (1.0 + r - cost)
        prev_k = float(fees_k.loc[d])
        prev_date = d
        rows.append({"date": str(d.date()), "nav": round(equity, 8),
                     "ret": round(r - cost, 8), "k": round(float(fees_k.loc[d]), 6),
                     "k_cost": round(cost, 8), "rf": round(rf_day, 8),
                     "decision": str(sched_k.get(d, "")) if isinstance(sched_k, dict) else ""})
    state["nav"] = equity
    state["last_bar"] = str(prev_date.date()) if prev_date is not None else last
    state["last_k"] = prev_k
    state["rows"] = int(state.get("rows", 0)) + len(rows)
    return state, rows


# ------------------------------------------------------------------------- run helpers
def _load_state(inception, beta):
    p = os.path.join(OUT_DIR, "state.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            st = json.load(f)
        if abs(float(st.get("beta_target", -1)) - float(beta)) < 1e-9:
            return st
        print("note: state carries beta_target=%s, requested %s -> fresh state (old ledger kept)"
              % (st.get("beta_target"), beta))
    return {"inception": str(inception), "beta_target": float(beta), "last_bar": None,
            "last_k": None, "nav": 1.0, "rows": 0}


def _write(name, obj):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def withdraw_unsupported_bars(state, idx, out_dir=None, now=None):
    """A ledger bar the price panel no longer carries is withdrawn, never carried.

    r1483 live defect: the 2026-11-09 row entered this ledger while a handful of symbols
    had printed that session and the wide panel had not; the panel then settled back on
    2026-11-06, so the state file stayed stuck on a bar no face could price. The ticket
    bar and the account bar diverged (11-06 vs 11-09) and every reconciliation downstream
    (cash leg, ladder, placement, operator page) read two different worlds.

    The repair may not rewrite history quietly: the withdrawn rows are recorded with the
    panel that refused them, and nav/last_k are rebuilt from the last surviving row.
    """
    out_dir = out_dir or OUT_DIR
    ledger_p = os.path.join(out_dir, "ledger.jsonl")
    last_bar = state.get("last_bar")
    if not last_bar or not len(idx):
        return state, [], {"bar": last_bar, "supported": True}
    supported = set(pd.Timestamp(d) for d in idx)
    rows = []
    if os.path.exists(ledger_p):
        with open(ledger_p, encoding="utf-8") as f:
            rows = [json.loads(l) for l in f if l.strip()]
    bad = [r for r in rows
           if pd.Timestamp(r["date"]) not in supported
           or pd.Timestamp(r["date"]) > pd.Timestamp(idx[-1])]
    if not bad:
        return state, [], {"bar": last_bar, "supported": True}
    bad_dates = {r["date"] for r in bad}
    keep = [r for r in rows if r["date"] not in bad_dates]
    with open(ledger_p, "w", encoding="utf-8") as f:
        for r in keep:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    if keep:
        tail = keep[-1]
        state.update({"nav": float(tail["nav"]), "last_k": float(tail["k"]),
                      "last_bar": str(tail["date"]), "rows": len(keep)})
    else:
        state.update({"nav": 1.0, "last_k": None, "last_bar": None, "rows": 0})
    record = {"withdrawn": [{"date": r.get("date"), "nav": r.get("nav"), "ret": r.get("ret"),
                             "k": r.get("k"), "rf": r.get("rf")} for r in bad],
              "reason": "the price panel no longer carries this bar (or carries later ones)",
              "panel_last": str(pd.Timestamp(idx[-1]).date()),
              "state_rewound_to": state.get("last_bar"),
              "at": now or str(pd.Timestamp.now().floor("s"))}
    wpath = os.path.join(out_dir, "withdrawals.json")
    hist = []
    if os.path.exists(wpath):
        try:
            with open(wpath, encoding="utf-8") as f:
                hist = json.load(f)
            if not isinstance(hist, list):
                hist = [hist]
        except Exception:
            hist = []
    hist.append(record)
    os.makedirs(out_dir, exist_ok=True)
    with open(wpath, "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=1)
    return state, bad, {"bar": last_bar, "supported": False,
                        "panel_last": record["panel_last"],
                        "rewound_to": state.get("last_bar")}


def ledger_dates(out_dir=None):
    """Every bar the ledger carries now -- the only evidence that a withdrawal still stands."""
    out_dir = out_dir or OUT_DIR
    p = os.path.join(out_dir, "ledger.jsonl")
    out = set()
    if not os.path.exists(p):
        return out
    try:
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.add(str(json.loads(line).get("date")))
                except Exception:
                    continue
    except Exception:
        return set()
    return out


def withdrawals_line(out_dir=None):
    """One sentence for the reader, or None when this ledger never had to withdraw.

    r1489: a withdrawal record is history, not a standing state. On 2026-11-09 a bar was
    cut at 23:54 off a panel that ended 11-06; the panel then carried that bar again and
    the ledger row came back, yet the sheet kept printing "state rewound to 2026-11-06 and
    this sheet is priced on the panel's own last bar" while being priced on 2026-11-09.
    The record may not describe the present: read the ledger and say which one it is.
    """
    out_dir = out_dir or OUT_DIR
    p = os.path.join(out_dir, "withdrawals.json")
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            hist = json.load(f)
        if isinstance(hist, dict):
            hist = [hist]
    except Exception:
        return None
    if not hist:
        return None
    last = hist[-1]
    withdrawn = last.get("withdrawn") or []
    dates = ", ".join(str(w.get("date")) for w in withdrawn)
    back = set(str(w.get("date")) for w in withdrawn) & ledger_dates(out_dir)
    if withdrawn and len(back) == len(set(str(w.get("date")) for w in withdrawn)):
        return ("ledger withdrew %d bar(s) at %s because the price panel then ended %s (%s); "
                "the panel has since carried %s again and that ledger row is live -- the "
                "withdrawal stays on record but it is not this sheet's pricing bar"
                % (len(withdrawn), last.get("at"), last.get("panel_last"), dates,
                   ", ".join(sorted(back))))
    return ("ledger withdrew %d bar(s) the price panel no longer carries (%s; panel ends %s); "
            "state rewound to %s and this sheet is priced on the panel's own last bar"
            % (len(withdrawn), dates, last.get("panel_last"),
               last.get("state_rewound_to")))


def _read_jsonl(path):
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except Exception:
                    continue
    return out


def reinstatement_check(rp, cash_rf, k_ser, out_dir=None, tol=1e-9, now=None, cost_bp=None):
    """A withdrawn bar that comes back is RE-DERIVED, never carried over.

    r1489: on 2026-11-09 a bar was cut at 23:54 off a panel that ended 11-06; the panel then
    carried 11-09 again and the ledger row reappeared. The row that reappears is only honest
    if it is the panel's own arithmetic: a withdrawn row was priced off a panel that has since
    changed, so re-using its stored nav/ret would publish a number nobody can re-derive.

    For every withdrawn date the ledger now carries, this recomputes that bar from the panel
    (same return rule as the accrual: r = rp*k + (1-k)*rf - |dk|*cost) off the ledgers own
    preceding row, and:
      * equal within tol -> RECOMPUTED_IDENTICAL (the panel reprinted the same closes),
      * different        -> REWRITTEN_FROM_PANEL: the row is replaced with the recomputed
                            values, marked `restated_at` so the restatement trail sees it,
                            and every later nav is scaled so the chain stays self-consistent
                            (the factor and the row count are published, never silent),
      * an input missing -> UNVERIFIABLE, naming what is missing; no rewrite.
    Also quotes what the withdrawal record stored, so "the row came back" and "the row came
    back with different closes" cannot read the same.
    """
    out_dir = out_dir or OUT_DIR
    cost_bp = COST_BP if cost_bp is None else float(cost_bp)
    wpath = os.path.join(out_dir, "withdrawals.json")
    lpath = os.path.join(out_dir, "ledger.jsonl")
    if not os.path.exists(wpath):
        return None
    try:
        with open(wpath, encoding="utf-8") as f:
            hist = json.load(f)
        if isinstance(hist, dict):
            hist = [hist]
    except Exception:
        return None
    if not hist:
        return None
    cut = {}
    for rec in hist:
        for w in (rec.get("withdrawn") or []):
            d = str(w.get("date"))
            cut.setdefault(d, w)          # first record wins: what was actually cut
    rows = _read_jsonl(lpath)
    if not cut or not rows:
        return None
    live = {str(r.get("date")): i for i, r in enumerate(rows)}
    back = sorted(d for d in cut if d in live)
    if not back:
        return None
    out = []
    rewritten = []
    for d in back:
        i = live[d]
        row = rows[i]
        prev = rows[i - 1] if i > 0 else None
        k = float(row.get("k")) if row.get("k") is not None else None
        rec = {"date": d, "withdrawn_nav": (cut[d] or {}).get("nav"),
               "withdrawn_ret": (cut[d] or {}).get("ret"),
               "withdrawn_k": (cut[d] or {}).get("k")}
        missing = []
        try:
            pd_ = pd.Timestamp(d)
            rp_d = float(rp.loc[pd_]) if pd_ in rp.index else None
            rf_d = float(cash_rf.loc[pd_]) if pd_ in cash_rf.index else None
            if k is None and pd_ in k_ser.index:
                k = float(k_ser.loc[pd_])
        except Exception:
            rp_d = rf_d = None
        if rp_d is None or not np.isfinite(rp_d):
            missing.append("book return on %s" % d)
        if rf_d is None or not np.isfinite(rf_d):
            missing.append("repo rate on %s" % d)
        if k is None or not np.isfinite(k):
            missing.append("overlay weight k on %s" % d)
        if prev is None:
            missing.append("a preceding ledger row to carry the nav from")
        if missing:
            rec.update({"status": "UNVERIFIABLE", "missing": missing})
            out.append(rec)
            continue
        prev_k = prev.get("k")
        cost = 0.0 if prev_k is None else abs(k - float(prev_k)) * cost_bp / 10000.0
        r_new = rp_d * k + (1.0 - k) * rf_d - cost
        nav_new = float(prev.get("nav")) * (1.0 + r_new)
        nav_new8, r_new8 = round(nav_new, 8), round(r_new, 8)
        nav_old = row.get("nav")
        ret_old = row.get("ret")
        dnav = None if nav_old is None else nav_new8 - float(nav_old)
        dret = None if ret_old is None else r_new8 - float(ret_old)
        rec.update({"recomputed_nav": nav_new8, "recomputed_ret": r_new8,
                    "ledger_nav": nav_old, "ledger_ret": ret_old, "k": round(k, 6),
                    "rf": round(rf_d, 8), "nav_delta": None if dnav is None else round(dnav, 10)})
        same = (dnav is not None and abs(dnav) <= tol
                and (dret is None or abs(dret) <= tol))
        if same:
            rec["status"] = "RECOMPUTED_IDENTICAL"
            wd_nav = (cut[d] or {}).get("nav")
            rec["same_as_withdrawn"] = (wd_nav is not None
                                        and abs(float(wd_nav) - nav_new8) <= tol)
            # r1490: a bar PUBLISHED at one number and restated to another is "identical"
            # only against today's panel -- the row itself still carries the history.
            # Plain RECOMPUTED_IDENTICAL on the second run would tell the operator "nothing
            # ever moved here" about a bar whose own later navs were rescaled. Quote the
            # row's own record back instead of trusting it to be absent.
            if row.get("nav_published") is not None or row.get("restated_at"):
                rec["settled_restated"] = {
                    "published_nav": row.get("nav_published"),
                    "published_ret": row.get("ret_published"),
                    "settled_nav": nav_new8,
                    "settled_ret": r_new8,
                    "restated_at": row.get("restated_at"),
                    "nav_factor_applied": row.get("nav_factor_applied"),
                    "later_rows_rescaled": row.get("later_rows_rescaled")}
        else:
            factor = 1.0 if not nav_old else nav_new8 / float(nav_old)
            ts = str(now or pd.Timestamp.now().floor("s"))
            n_shift = 0
            for j in range(i + 1, len(rows)):
                if rows[j].get("nav") is not None:
                    rows[j]["nav"] = round(float(rows[j]["nav"]) * factor, 8)
                    n_shift += 1
            # r1490: keep BOTH numbers on the row. reinstatements.json is rewritten on every
            # run, so a published value living only there is a record the producer reads and
            # the operator never can (E281). The rescale that moved later navs is stamped the
            # same way, so a reader can see how far the chain moved and by what factor.
            row.update({"nav": nav_new8, "ret": r_new8, "k": round(k, 6),
                        "k_cost": round(cost, 8), "rf": round(rf_d, 8),
                        "nav_published": nav_old, "ret_published": ret_old,
                        "restated_at": ts, "nav_factor_applied": round(factor, 12),
                        "later_rows_rescaled": n_shift,
                        "restate_reason": "reinstated bar re-derived from the panel (r1489)"})
            # r1490: the rescale is only honest if the chain still compounds. Measure it on
            # the rows this write produced instead of asserting it.
            # r1490: nav is stored at 8 decimals, so every rescale carries up to 1e-8 of
            # rounding per bar; a fixed 1e-9 gate would print a false red on a chain that is
            # arithmetically perfect (measured on the real 2026-11-06 row: expected
            # 1.46125781 vs ledger 1.46125782). The gate scales with the distance from the
            # rewritten bar, and the gate it used is published, not implied.
            chain_breaks = []
            for j in range(i + 1, len(rows)):
                a_nav, b_nav, b_ret = (rows[j - 1].get("nav"), rows[j].get("nav"),
                                       rows[j].get("ret"))
                if a_nav is None or b_nav is None or b_ret is None:
                    continue
                exp = round(float(a_nav) * (1.0 + float(b_ret)), 8)
                gate = tol + 1e-8 * (j - i) + 1e-12
                if abs(exp - float(b_nav)) > gate:
                    chain_breaks.append({"date": str(rows[j].get("date")),
                                         "expected": exp, "ledger": float(b_nav),
                                         "gate": gate})
            rec.update({"status": "REWRITTEN_FROM_PANEL", "restated_at": ts,
                        "nav_factor": round(factor, 12), "later_rows_rescaled": n_shift,
                        "nav_published": nav_old, "ret_published": ret_old,
                        "chain_intact": not chain_breaks,
                        "chain_breaks": chain_breaks})
            rewritten.append(d)
        out.append(rec)
    if rewritten:
        with open(lpath, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    payload = {"at": str(now or pd.Timestamp.now().floor("s")), "n_reinstated": len(out),
               "rewritten": rewritten,
               "verbatim_identical": [r["date"] for r in out
                                      if r.get("status") == "RECOMPUTED_IDENTICAL"
                                      and r.get("same_as_withdrawn")],
               # r1490: bars whose own history is on the row (published != settled). These
               # stay in the ledger, so they are listed every run -- not only the run that
               # rewrote them.
               "settled_restated": [r["date"] for r in out if r.get("settled_restated")],
               "chain_broken": [r["date"] for r in out
                                if r.get("chain_intact") is False],
               "records": out}
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "reinstatements.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    return payload


def _chain_break_line(breaks):
    """Name the rows where nav != previous nav x (1+ret) -- a broken chain is never a dash."""
    if not breaks:
        return "-"
    return "；".join("%s 应为 %.8f 实为 %.8f" % (b.get("date"), b.get("expected"),
                                                b.get("ledger")) for b in breaks[:5])


def reinstated_history(ledger_path=None):
    """Bars in the ORDER ledger whose own history moved, read from the ledger itself.

    r1490: reinstatement_check writes reinstatements.json fresh on every run, so a bar
    restated three runs ago is only visible to whoever re-reads the ledger rows. The
    operator holds the sheet, so the sheet carries this block -- three states kept apart
    (unreadable / none / N bars), the same way _ledger_restatements does it.
    """
    p = ledger_path or os.path.join(OUT_DIR, "ledger.jsonl")
    out = {"path": p, "readable": False, "bars": [], "records": [],
           "bars_total": None, "chain_broken": []}
    try:
        rows = _read_jsonl(p)
    except Exception:
        return out
    out["readable"] = True
    out["bars_total"] = len(rows)
    for i, r in enumerate(rows):
        if r.get("restated_at") is None and r.get("nav_published") is None:
            continue
        rec = {"date": str(r.get("date")), "restated_at": r.get("restated_at"),
               "nav_published": r.get("nav_published"),
               "ret_published": r.get("ret_published"),
               "nav": r.get("nav"), "ret": r.get("ret"),
               "nav_factor_applied": r.get("nav_factor_applied"),
               "later_rows_rescaled": r.get("later_rows_rescaled"),
               "reason": r.get("restate_reason")}
        nxt = rows[i + 1] if i + 1 < len(rows) else None
        if nxt is not None and nxt.get("nav") is not None and r.get("nav") is not None \
                and nxt.get("ret") is not None:
            exp = round(float(r["nav"]) * (1.0 + float(nxt["ret"])), 8)
            if abs(exp - float(nxt["nav"])) > 1e-8:
                out["chain_broken"].append({"date": str(nxt.get("date")),
                                            "expected": exp, "ledger": float(nxt["nav"])})
        out["records"].append(rec)
    out["bars"] = [x["date"] for x in out["records"]]
    return out


def reinstated_history_md(h):
    """The block an operator reads: did the ledger this sheet quotes ever move, and where."""
    if not h or not h.get("readable"):
        return ["", "## 账本历史变更：本单引用的账本有没有被改过", "",
                "- **无法核验**：读不到订单账本（%s），所以本单不能回答这个问题 —— "
                "这不是「没有被改述」。"
                % _relpath_safe((h or {}).get("path") or "-", BASE)]
    recs = h.get("records") or []
    if not recs:
        return ["", "## 账本历史变更：本单引用的账本有没有被改过", "",
                "- 已核验：订单账本共 %s 根 bar，其中**没有一根在发布后被改述**。"
                % (h.get("bars_total") if h.get("bars_total") is not None else "?")]
    L = ["", "## 账本历史变更：本单引用的账本有没有被改过", "",
         "**有 %d 根 bar 在发布后被改述**（两个值都留在账本行上）：" % len(recs), "",
         "| bar | 发布时 NAV | 定格后 NAV | 改述时刻 | 之后同乘 | 被缩放的后续行 |",
         "|---|---|---|---|---|---|"]
    for r in recs:
        L.append("| %s | %s | %s | %s | %s | %s |"
                 % (r.get("date") or "-",
                    "-" if r.get("nav_published") is None
                    else "%.8f" % float(r["nav_published"]),
                    "-" if r.get("nav") is None else "%.8f" % float(r["nav"]),
                    r.get("restated_at") or "-",
                    r.get("nav_factor_applied") if r.get("nav_factor_applied") is not None else "-",
                    r.get("later_rows_rescaled")
                    if r.get("later_rows_rescaled") is not None else "-"))
    if h.get("chain_broken"):
        L += ["", "- **改述之后链条没接上**（逐根 nav=前根×(1+ret) 校验失败，%d 处）：%s"
              % (len(h["chain_broken"]), _chain_break_line(h["chain_broken"]))]
    else:
        L += ["", "- 链条校验：改述行与其后一根 bar 的 nav=前根×(1+ret) 关系成立"
              "（容差按 8 位存储的舍入计，不是拿 1e-9 去判 8 位小数的乘积）。"]
    L += ["", "- 读法：本单引用的行以「定格后」那一列为准；发布值保留在同一行的 "
          "nav_published 上，不是只留在生成器的临时文件里。"]
    return L


def reinstatement_md(ri):
    """One paragraph for the sheet: what came back, and whether it is the panel's number."""
    if not ri or not ri.get("n_reinstated"):
        return []
    L = ["", "**账本 reinstatement（撤回过的 bar 又回来了）** 共 %d 根：" % ri["n_reinstated"]]
    for r in ri["records"]:
        if r.get("status") == "RECOMPUTED_IDENTICAL":
            L.append("- %s：按当日面板重算 nav=%.8f ret=%+.8f，与账本行差 %.0e（k=%.6f rf=%.8f）；"
                     "撤回记录当时存的是 nav=%s —— %s"
                     % (r["date"], r["recomputed_nav"], r["recomputed_ret"],
                        abs(r.get("nav_delta") or 0.0), r["k"], r["rf"],
                        r.get("withdrawn_nav"),
                        "面板重印的是同一批收盘价，回来的是重算值不是旧副本"
                        if r.get("same_as_withdrawn")
                        else "面板重印后收盘价变了：旧副本会差 %.2e" % abs(
                            float(r["recomputed_nav"]) - float(r["withdrawn_nav"]))))
        elif r.get("status") == "REWRITTEN_FROM_PANEL":
            L.append("- %s：账本行与面板重算不一致（nav %s → %.8f，差 %+.2e，ret %s → %+.8f）"
                     "——已按面板改写并标 restated_at=%s，之后 %d 根 nav 同乘 %.12f %s"
                     % (r["date"], r.get("ledger_nav"), r["recomputed_nav"],
                        r.get("nav_delta") or 0.0, r.get("ledger_ret"), r["recomputed_ret"],
                        r.get("restated_at"), r.get("later_rows_rescaled") or 0,
                        r.get("nav_factor") or 1.0,
                        "链条复利校验通过（逐根 nav=前根×(1+ret)，容差随 8 位存储舍入放大）"
                        if r.get("chain_intact") is not False else
                        "**改后链条断了**：%s" % _chain_break_line(r.get("chain_breaks"))))
        else:
            L.append("- %s：**无法核验**（缺 %s）——这一行没有被证明是面板算出来的"
                     % (r["date"], "、".join(r.get("missing") or [])))
        # r1490: on a later run the row agrees with the panel and would read plain
        # RECOMPUTED_IDENTICAL. Its own record says it was published at a different number,
        # so both values are printed -- history that moved must not read as history that
        # never moved.
        _sr = r.get("settled_restated") or {}
        if _sr:
            L.append("  - 这根 bar **定格后被改述过**（%s）：当时发布 nav=%s ret=%s → 定格后 "
                     "nav=%s ret=%s；之后 %s 根 nav 同乘 %s。"
                     % (_sr.get("restated_at") or "-",
                        "-" if _sr.get("published_nav") is None
                        else "%.8f" % float(_sr["published_nav"]),
                        "-" if _sr.get("published_ret") is None
                        else "%+.8f" % float(_sr["published_ret"]),
                        "%.8f" % float(_sr["settled_nav"]),
                        "%+.8f" % float(_sr["settled_ret"]),
                        _sr.get("later_rows_rescaled")
                        if _sr.get("later_rows_rescaled") is not None else "-",
                        _sr.get("nav_factor_applied")
                        if _sr.get("nav_factor_applied") is not None else "-"))
    return L


def metrics(nav_ser, bench_ser, lb=252):
    def block(s):
        if s is None or len(s.dropna()) < 30:
            return None
        s = s.dropna()
        yrs = (s.index[-1] - s.index[0]).days / 365.25
        ret = s.pct_change().dropna()
        cagr = (float(s.iloc[-1]) / float(s.iloc[0])) ** (1.0 / yrs) - 1.0 if yrs > 0 else float("nan")
        vol = float(ret.std() * np.sqrt(252))
        mdd = float((s / s.cummax() - 1.0).min())
        return {"cagr": round(cagr, 4), "sharpe": round((cagr / vol) if vol else float("nan"), 3),
                "maxdd": round(mdd, 4), "vol": round(vol, 4), "bars": int(len(s))}

    out = {"book": block(nav_ser), "same_beta_benchmark": block(bench_ser)}
    if out["book"] and out["same_beta_benchmark"]:
        out["excess_pp"] = round((out["book"]["cagr"] - out["same_beta_benchmark"]["cagr"]) * 100, 2)
    return out


# ------------------------------------------------------------------ feed freshness
# One implementation lives in exchange_calendar_audit (it owns the official calendar);
# these aliases keep the local call sites readable.
feed_status = CA.ticket_feed_status


def live_feed_status(ticket_bar, now=None):
    return CA.live_ticket_feed_status(ticket_bar, now=now)


def drawdown_band():
    """How bad can the drawdown be, per the bootstrap block arms (r1348).

    The order sheet prints one realised maxDD for a book that has one history. The same
    book, resampled, has a 5th-percentile drawdown several pp deeper -- so an operator
    sizing to the printed number is sizing to a median. Soft-fails to None.
    """
    try:
        files = sorted(glob.glob(os.path.join(BASE, "results", "etf_book_bootstrap",
                                              "BLOCKS-*.json")))
        if not files:
            return None
        with open(files[-1], "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        arms = doc.get("arms") or []
        if len(arms) < 2:
            return None
        return {"artifact": os.path.relpath(files[-1], BASE).replace("\\", "/"),
                "evidence_cutoff": doc.get("evidence_cutoff"),
                "block_set": [a.get("block") for a in arms],
                "maxdd_p5": doc["spread"]["maxdd_p5"],
                "maxdd_p50": doc["spread"]["maxdd_p50"],
                "dd_break": doc["spread"]["dd_break_share"]}
    except Exception:
        return None


def carry_split(beta=None, path=None):
    """How much of the quoted headline is the 1-day repo leg (r1367).

    The sheet quotes one CAGR for a book that parks roughly half its NAV in GC001, so a
    reader cannot tell whether the selection machinery pays or the parking does. The split
    is measured once by ``scripts/etf_book_return_regime.py``; this reads that artifact at
    the beta the ticket is actually running instead of re-running the engine (and instead
    of hand-copying a number that would rot).

    Soft-fails to None -- the caller must say so, because silence reads as "all alpha".
    """
    p = path or os.path.join(BASE, "results", "etf_book_return_regime.json")
    want = float(DEFAULT_BETA if beta is None else beta)
    try:
        with open(p, encoding="utf-8") as fh:
            doc = json.load(fh)
        gate = doc.get("gate") or {}
        cells = gate.get("betas") or {}
        if not cells:
            return None
        key = min(cells, key=lambda k: abs(float(k) - want))
        cell = cells[key] or {}
        obs, flat, zero = (cell.get("observed_pct"), cell.get("flat_today_pct"),
                           cell.get("zero_pct"))
        if None in (obs, flat, zero):
            return None
        rates = doc.get("cash_rates") or {}
        try:
            artifact = os.path.relpath(p, BASE).replace("\\", "/")
        except Exception:                       # fixture on another drive
            artifact = str(p)
        return {"artifact": artifact,
                "evidence_cutoff": doc.get("evidence_cutoff"),
                "beta": float(key),
                "beta_requested": want,
                "observed_pct": float(obs),
                "flat_today_pct": float(flat),
                "zero_pct": float(zero),
                "carry_pp": round(float(obs) - float(zero), 4),
                "flat_rate_cost_pp": round(float(obs) - float(flat), 4),
                "carry_share_pct": round(cell.get("carry_share_of_headline_pct")
                                         if cell.get("carry_share_of_headline_pct") is not None
                                         else 100.0 * (float(obs) - float(zero)) / float(obs), 3),
                "pp_per_100bp": cell.get("pp_per_100bp"),
                "cash_share": cell.get("cash_share"),
                "rate_today_pct": rates.get("today_pct"),
                "rate_today_date": rates.get("today_date"),
                "rate_observed_pct": rates.get("observed_mean_pct"),
                "identity_matched": (doc.get("identity") or {}).get("matched")}
    except Exception:
        return None


CASH_MONEY_BP = 25.0        # frozen before the run: spot must clear this far below its own
                            # trailing mean before this face calls it a fall rather than noise


def cash_money(cash_amount, rates, asof, accrual_pct=None, tail=250, fall_bp=CASH_MONEY_BP):
    """What the idle half of THIS ticket earns, in CNY, at the rates this book actually parks in.

    The sheet printed the cash weight and the cash amount and stopped there: the only yield it
    quoted was a multi-year mean (the accrual window), which is a history that includes the
    quarters when GC001 traded several times today's quote (r1167 caught the three windows
    disagreeing and nobody pricing them). A mean is not a forecast, so the same cash is priced
    here at three rates read off the one repo panel -- the last quote, its own trailing mean and
    the window mean the ledger accrued -- and the difference is printed in CNY instead of being
    left for the reader to pick the flattering one. Unreadable inputs stay None, never 0.
    """
    out = {"cash_amount_cny": None, "spot": None, "mean_tail": None, "window": None,
           "tail": int(tail), "fall_bp": float(fall_bp), "verdict": "CANNOT_PRICE",
           "sentence": None, "spread_vs_tail_cny": None, "spread_vs_window_cny": None}
    try:
        cash = None if cash_amount is None else float(cash_amount)
    except (TypeError, ValueError):
        cash = None
    if cash is None or cash <= 0:
        out["sentence"] = "现金腿金额不可读，这一半今天赚多少钱本单不报。"
        return out
    out["cash_amount_cny"] = round(cash, 2)
    if rates is None or len(rates) == 0:
        out["sentence"] = "repo 面板缺席，现金腿今天赚多少钱本单不报（不是 0）。"
        return out
    seen = rates[rates.index <= pd.Timestamp(asof)] if asof else rates
    if len(seen) == 0:
        out["sentence"] = "repo 面板没有 %s 当日或更早的报价，现金腿今天赚多少钱本单不报。" % asof
        return out
    spot_pct = float(seen.iloc[-1])
    spot_date = str(seen.index[-1].date())
    tail_pct = float(seen.tail(int(tail)).mean())
    out["spot"] = {"pct": round(spot_pct, 4), "date": spot_date,
                   "annual_cny": round(cash * spot_pct / 100.0, 0),
                   "quotes": int(min(len(seen), int(tail)))}
    out["mean_tail"] = {"pct": round(tail_pct, 4),
                        "annual_cny": round(cash * tail_pct / 100.0, 0)}
    if accrual_pct is not None and np.isfinite(float(accrual_pct)):
        out["window"] = {"pct": round(float(accrual_pct), 4),
                         "annual_cny": round(cash * float(accrual_pct) / 100.0, 0)}
    out["spread_vs_tail_cny"] = round(cash * (spot_pct - tail_pct) / 100.0, 0)
    if out["window"] is not None:
        out["spread_vs_window_cny"] = round(
            cash * (spot_pct - out["window"]["pct"]) / 100.0, 0)
    if spot_pct <= tail_pct - float(fall_bp) / 100.0:
        out["verdict"] = "RATES_FELL"
    elif spot_pct >= tail_pct + float(fall_bp) / 100.0:
        out["verdict"] = "RATES_ROSE"
    else:
        out["verdict"] = "RATES_STEADY"
    sent = ("现金 ¥%s 按 %s 报价 %.2f%% 一年赚 ¥%s；按自己近 %d 个报价的均值 %.2f%% 是 ¥%s"
            % (format(int(cash), ","), spot_date, spot_pct,
               format(int(out["spot"]["annual_cny"]), ","),
               out["spot"]["quotes"], tail_pct,
               format(int(out["mean_tail"]["annual_cny"]), ",")))
    if out["window"] is not None:
        sent += "；按账本自己走过的全窗均值 %.2f%% 是 ¥%s" % (
            out["window"]["pct"], format(int(out["window"]["annual_cny"]), ","))
    if out["verdict"] == "RATES_FELL":
        sent += ("。差出来的 ¥%s 是利率掉了，不是这个月选错了票。"
                 % format(int(abs(out["spread_vs_tail_cny"])), ","))
    elif out["verdict"] == "RATES_ROSE":
        sent += "。今天的报价高于它自己的均值 ¥%s，别把这个差当成常常有。" % format(
            int(out["spread_vs_tail_cny"]), ",")
    else:
        sent += "。今天的报价就在它自己的均值上，这一半该怎么算就怎么算。"
    out["sentence"] = sent
    return out


def entry_gate_support():
    """r1248: 这本书能买哪些票，是一只手的数定的。

    派生不重跑：唯一读器是 scripts/etf_book_ceo_page.entry_gate_face —— 它用申报格校验
    20M 档是否复现本书、并用 etf_book_entry_gate.classify 从载荷自己的行重算判词。
    第二份实现就是同一个缺陷的第二份拷贝（E289），所以这里 import 那条派生。
    """
    try:
        from scripts import etf_book_ceo_page as _PAGE
        return _PAGE.entry_gate_face()
    except Exception as exc:                                    # noqa: BLE001
        try:
            import etf_book_ceo_page as _PAGE2
            return _PAGE2.entry_gate_face()
        except Exception:                                       # noqa: BLE001
            return {"status": "unreadable", "detail": repr(exc)}


def entry_gate_md(eg):
    """两轴分开印：这道闸买到了多少收益，和它买到了多少容量。"""
    eg = eg or {}
    if eg.get("status") != "ok":
        return ["## 这本书能买哪些票（r1248）",
                "- **这一问答不了。** %s —— 选票的那道闸在本单上没有测过，不是验过了。"
                % (eg.get("detail") or eg.get("status")), ""]
    shipped_m = (float(eg.get("shipped_cny") or 0.0)) / 1e6
    L = ["## 这本书能买哪些票，是谁定的（r1248）",
         "- 全部可选名都过了**同一道闸**：20 日成交额中位数 ≥ **%gM**。这道闸从来没在本书内部"
         "被扫过，所以「这个门槛对不对」过去只能猜。" % shipped_m]
    if eg.get("verdict") == "GATE_SITS_ON_PLATEAU":
        L.append("- **收益这一轴是平的**：门槛砍一半或翻一倍，申报口径年化只动 ≤%.2f pp"
                 "（最好那档 %+.2f pp，容差 %.1f pp）——%gM 不承载收益。"
                 % (float(eg.get("near_max_pp") or 0.0),
                    float(eg.get("best_delta_pp") or 0.0),
                    float(eg.get("tol_pp") or 0.0), shipped_m))
    else:
        L.append("- **收益这一轴不平：%s。** %s"
                 % (eg.get("verdict"), eg.get("sentence") or ""))
    ratio = eg.get("width_ratio")
    if ratio is not None and float(ratio) >= 2.0:
        L.append("- **容量这一轴不平**：同一个旋钮把可选名数中位数从 **%d 只** 压到 **%d 只**"
                 "（%.1f 倍）——这道闸不是你的收益来源，是**你的容量来源**：同样的钱摊到几只票上，"
                 "改变的是单笔能有多大，不是期望收益。"
                 % (int(eg.get("widest_names") or 0), int(eg.get("narrowest_names") or 0),
                    float(ratio)))
    L.append("- 判定 **%s**｜出处 `%s`（证据截止 %s，面板末 bar %s；%gM 档复现本书申报格 "
             "%.3f pp，容差 %.2f pp）。"
             % (eg.get("verdict"),
                str(eg.get("artifact") or "results/etf_book_entry_gate.json").replace(os.sep, "/"),
                eg.get("evidence_cutoff"), eg.get("panel_last_bar"), shipped_m,
                float((eg.get("control") or {}).get("delta_pp") or 0.0),
                float((eg.get("control") or {}).get("tol_pp") or 0.0)))
    L.append("")
    return L


PERMISSION_FACE = "results/etf_book_rebalance_permission.json"
RULERS_FACE = "results/etf_book_size_rulers_decision.json"
FLOOR_FACE = "results/etf_book_floor_ledger.json"
SWAP_FACE = "results/etf_book_swap_trigger.json"
SWAP_STACK_FACE = "results/etf_book_swap_stack.json"
POSITIONS_FACE = "results/etf_book_positions.json"


def _json_face(rel):
    p = os.path.join(PATHS.results_dir, os.path.basename(rel))
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _permission_receipt():
    return _json_face(PERMISSION_FACE)


def _floor_face():
    return _json_face(FLOOR_FACE)


def swap_trigger_md(sw):
    """r1466: the ticket says what the swap is worth; it has to say when to look again too.
    Absent or unreadable prints one line -- an empty section would read as "nothing to watch"
    (r1108 有产无读)."""
    if sw is None:
        return ["", "## 换票之后什么时候再看一次（r1466）",
                "- **这一问答不了**：没有已发布的换票触发面（跑 "
                "scripts/etf_book_swap_trigger.py run）。缺面不等于没有要看的数。", ""]
    L = ["", "## 换票之后什么时候再看一次（r1466）",
         "- %s" % sw["recheck_rule"]]
    for r in sw.get("pairs") or []:
        exp = r.get("expiry") or {}
        med = exp.get("median_sessions")
        exp_s = ("未测（%d 例全部未愈合）" % (exp.get("n_censored") or 0) if med is None
                 else "中位 %.0f 个交易日（%d 例回均值，%d 例未愈合）"
                 % (med, exp.get("n_completed") or 0, exp.get("n_censored") or 0))
        # an immaterial pair never had its split computed: print "not counted", not ¥0 --
        # a zero reads as "measured, and it is zero" (E206 名即语义)
        if r.get("source_verdict") == "SWAP_SAVES" and r.get("one_off_gain_cny") is not None:
            split = "一次性 ¥%s / 可重复 ¥%s" % (format(r["one_off_gain_cny"], ",.0f"),
                                                format(r.get("repeatable_gain_cny") or 0, ",.0f"))
        else:
            split = "钱不单列（上游面判为 %s）" % (r.get("source_verdict") or "?")
        L.append("- `%s → %s`：今日 %s pp 对历史均值 %s pp｜%s｜"
                 "超过触发价占比 %s｜%s｜**%s**"
                 % (r["leg_symbol"], r["sibling_symbol"],
                    ("%+.2f" % r["today_gap_pp"]) if r.get("today_gap_pp") is not None else "?",
                    ("%+.2f" % r["mean_gap_pp"]) if r.get("mean_gap_pp") is not None else "?",
                    split,
                    ("%.0f%%" % (100.0 * r["window_share"]))
                    if r.get("window_share") is not None else "?", exp_s, r["verdict"]))
    L += ["- 读法：这条不是日历提醒。书每 %d 个交易日重排，那一天换票本来就会被重新决定；"
          "两次决策之间唯一能改主意的是价差——只有它越过来回成本（%.2f pp），再动一次才不亏。"
          % (REBAL, float((sw.get("criteria") or {}).get("toll_pp") or 0.0)), ""]
    return L


def swap_stack_md(ss):
    """r1467: the sheet carries two sections that both sell the same leg.

    The trim table sells the part the floor forbids; the swap line sells the whole leg and
    prices its benefit on the *untrimmed* size. Read together the page sells more of that
    ticker than the book holds, and quotes a swap gain the permission already refused. This
    block prints the netted order -- what to type -- and the two numbers the two sections
    disagree about. An absent face prints one line, never a silent pass (r1108).
    """
    if ss is None:
        return ["", "## 这张单真正要下的是一笔还是两笔（r1467）",
                "- **这一问答不了**：没有已发布的净额单面（跑 "
                "scripts/etf_book_swap_stack.py run）。缺面不等于没有要合并的动作。", ""]
    v = ss.get("verdict")
    head = {
        "TWO_SECTIONS_OVERSELL_THE_LEG":
            "**两段话卖同一只票**：额度表卖一部分、换票线卖整只腿，照两段一起下单会卖超；"
            "顺序只有一种——先按额度裁，再拿剩下的整只腿去换。",
        "NETTED_WITH_RESIDUE":
            "**两段合成一笔**：换票在裁剪后手数上重算，整手取整零头 ¥%s 留在现金腿。"
            % format(ss.get("lot_residue_cny") or 0.0, ",.0f"),
        "NETTED_CLEAN": "**两段合成一笔，整手正好对齐**。",
        "NOTHING_TO_NET": "**今天没有要合并的动作**：本单只有额度裁剪这一件事。",
        "CANNOT_VERIFY": "**这一问答不了**：票面或换票面读不出来，不给净额单。",
    }.get(v, v or "?")
    L = ["", "## 这张单真正要下的是一笔还是两笔（r1467）", "- %s" % head]
    acts = ss.get("actions") or []
    if acts:
        L += ["", "| 方向 | 代码 | 价 | 手数 | 金额 |", "|---|---|---|---|---|"]
        for r in acts:
            L.append("| **%s** | %s | %.3f | %d | ¥%s |"
                     % (r["side"], r["symbol"], r["price"], r["lots"],
                        format(r["amount_cny"], ",.0f")))
        L.append("")
    for o in ss.get("oversell") or []:
        if o.get("swapped") and o.get("as_printed_excess"):
            L.append("- `%s`：额度表卖 %d 手 + 换票线卖 %d 手 = %d 手，账面只有 %d 手 → "
                     "照两段念会多卖 **%d 手**（净额单里只卖 %d 手）。"
                     % (o["symbol"], o["trim_sells"], o["swap_sells"],
                        o["sections_add_up_to"], o["held"], o["as_printed_excess"],
                        o["held"] - o["trim_sells"]))
    rp = ss.get("swap_repricing") or []
    if rp:
        L.append("- 换票收益按**下单量**定价，额度裁掉的那部分不会发生：合计高估 **¥%s**"
                 "（%s）。" % (format(ss.get("overstated_total_cny") or 0.0, ",.0f"),
                              "；".join("%s %s→%s" % (r["leg"],
                                                     format(r["gain_published_cny"], ",.0f"),
                                                     format(r["gain_on_trimmed_book_cny"], ",.0f"))
                                       for r in rp)))
    w = ss.get("widest_name") or {}
    b = ss.get("baskets") or {}
    if w:
        L.append("- 执行后最宽的一只是 `%s`（风险腿 %.1f%%），独立篮子数 %s → %s（%s）："
                 "把两只同一篮子的票并成一只，票数变少、篮子没变。"
                 % (w.get("symbol"), 100.0 * (w.get("share_of_risk_book") or 0.0),
                    b.get("n_before"), b.get("n_after"),
                    "未变" if b.get("n_before") == b.get("n_after") else "变了"))
    L += ["- 出处：%s。" % SWAP_STACK_FACE, ""]
    return L


def positions_md(pos):
    """r1468: the netted rows are not the whole order, and the executed book is not the sheet.

    Two things only become visible once the post-execution book is written down: the printed
    rows leave lots the same face declares it sold (the trim table's own five sells never
    became rows), and after the swap executes the account holds a different set of tickers than
    the sheet names. This block puts both on the page the desk types from. An absent face
    prints one line, never a silent pass (r1108).
    """
    if pos is None:
        return ["", "## 打印的动作能不能凑成账上的书（r1468）",
                "- **这一问答不了**：没有已发布的持仓对账面（跑 "
                "scripts/etf_book_positions.py run）。缺面不等于动作齐全。", ""]
    v = pos.get("verdict")
    head = {
        "PRINTED_ROWS_UNDERSELL_THE_BOOK":
            "**照上面这几行打字，账上还剩 ¥%s 的票没卖**——不是估值差，是打印出来的动作行"
            "没覆盖这张单自己声明的账。"
            % format(pos.get("unexplained_total_cny") or 0.0, ",.0f"),
        "PRINTED_ROWS_OVERSELL_THE_BOOK":
            "**打印的动作比声明的账买得更多**（¥%s）：纸面与账面在买入方向分叉。"
            % format(abs(pos.get("unexplained_total_cny") or 0.0), ",.0f"),
        "PRINTED_ROWS_REBUILD_THE_BOOK":
            "**打印的动作能一笔一笔复原声明的账**：没有漏印的腿，也没有多印的手数。",
        "GAPS_NOT_PRICED": "**手数对不上，但没有一条腿有当日价**：只印手数，不编金额。",
        "CANNOT_VERIFY": "**这一问答不了**：票面、净额单面或声明账缺一件，不拿缺口当零。",
    }.get(v, v or "?")
    L = ["", "## 打印的动作能不能凑成账上的书（r1468）", "- %s" % head]
    if pos.get("unexplained"):
        L += ["", "| 代码 | 票面起点 | 打印后 | 声明的账 | 差 | 差多少钱 |",
              "|---|---|---|---|---|---|"]
        for r in pos["unexplained"]:
            L.append("| %s | %d | %d | %d | **%+d 手** | %s |"
                     % (r["symbol"], r.get("sheet_lots") or 0, r["printed_lots"],
                        r["book_lots"], r["delta_lots"],
                        ("**¥%s**" % format(r["delta_cny"], ",.0f"))
                        if r.get("delta_cny") is not None else "无价，不编"))
        L += ["", "- 少的那几笔是额度裁剪表自己五腿的卖出；净额单只把换票的两笔卖和一笔合并买"
              "变成了动作行。**先按顺序做没错，但打字要补上这 %d 笔**。"
              % len(pos["unexplained"])]
    base = pos.get("next_order_base") or {}
    if base:
        L.append("- 执行后的账已写下（bar `%s`：风险腿 ¥%s / 现金 ¥%s / %d 只）："
                 "**下一张单从这本账起算**，不从上一条票面起算。"
                 % (base.get("bar"), format(base.get("risk_book_cny") or 0.0, ",.0f"),
                    format(base.get("cash_cny") or 0.0, ",.0f"), base.get("holdings") or 0))
        if pos.get("base_divergence_total_cny"):
            L.append("- 按票面修回来要再打 ¥%s：换票执行后票面与账本已不是同一批票"
                     "（票面还写着换出的两只），这个数就是错误底座的名义代价。"
                     % format(pos["base_divergence_total_cny"], ",.0f"))
    elif v != "CANNOT_VERIFY":
        L.append("- **没有写下的执行后账**：下一张单只能退回上一张票面起算，那正是两本账分叉的入口。")
    L += ["- 出处：%s。" % POSITIONS_FACE, ""]
    return L


def executed_base(asof=None):
    """r1471: size the sheet from the account that exists, not from the engine's book.

    r1468 wrote the post-execution book down and r1469 accrued it bar by bar, but nothing
    that CUTS an order read it: the ticket still sized k off the engine's own ledger
    (k=0.460253) while the desk actually holds k=0.392401. That gap is not bookkeeping --
    it is the exact 6.79pp the permission table was already trimming away, i.e. CNY 67,852
    of notional exposure the account does not carry. Printing the fork (r1470) is not the
    same as closing it here.
    """
    pos = _json_face(POSITIONS_FACE)
    if pos is None:
        return {"status": "absent", "face": POSITIONS_FACE,
                "sentence": "没有执行后的账（%s 缺失）：本单只能退回引擎账起算" % POSITIONS_FACE}
    b = pos.get("next_order_base") or {}
    bar, risk, cash = b.get("bar"), b.get("risk_book_cny"), b.get("cash_cny")
    if risk is None or cash is None or (float(risk) + float(cash)) <= 0:
        return {"status": "unreadable", "face": POSITIONS_FACE,
                "sentence": "执行后的账读不出风险腿/现金（%s）：缺数不等于空仓" % POSITIONS_FACE}
    total = float(risk) + float(cash)
    k_exec = float(risk) / total
    div = ((pos.get("engine_book") or {}).get("divergence") or {})
    k_engine = div.get("engine_k")
    out = {"status": "ok", "face": POSITIONS_FACE, "bar": bar,
           "risk_book_cny": round(float(risk), 2), "cash_cny": round(float(cash), 2),
           "nav_cny": round(total, 2), "k_executed": round(k_exec, 6),
           "k_engine": None if k_engine is None else round(float(k_engine), 6),
           "holdings": b.get("holdings")}
    if k_engine is not None:
        out["k_gap"] = round(float(k_engine) - k_exec, 6)
        out["notional_gap_cny"] = round((float(k_engine) - k_exec) * total, 2)
    if asof is not None and bar != asof:
        out["status"] = "stale"
        out["sentence"] = ("执行后的账停在 %s，本单定价 bar 是 %s：两天的账不能拿来起算"
                           % (bar, asof))
    return out


def executed_base_md(base):
    """Print which book this sheet sized from. An unreadable base prints one line."""
    if base is None:
        return []
    st = base.get("status")
    sz = base.get("sizing") or {}
    L = ["", "## 这张单从哪一本账起算（r1471）"]
    _same_bar = sz.get("source") == "rule_same_bar_outcome"
    if st == "ok":
        L += ["- %sbar `%s` 风险腿 ¥%s / 现金 ¥%s → k=**%.6f**（账上 %d 只）。"
              % ("**这本账是本单自己的结果，不作起算**：" if _same_bar
                 else "**从执行账起算**：",
                 base["bar"], format(base["risk_book_cny"], ",.0f"),
                 format(base["cash_cny"], ",.0f"), base["k_executed"],
                 base.get("holdings") or 0)]
        if base.get("k_engine") is not None and abs(base.get("k_gap") or 0.0) > 1e-9:
            L += ["- 引擎账 k=%.6f 与账本差 **%+.6f**（¥%s 名义额）：引擎账是规则算出来的、"
                  "从没被额度裁过，照它下单等于把账上没有的仓位再买一遍。%s"
                  % (base["k_engine"], base["k_gap"],
                     format(base.get("notional_gap_cny") or 0.0, ",.0f"),
                     "" if _same_bar else "本单的手数按执行账裁。")]
    elif st == "stale":
        L += ["- **不能用这本账起算**：%s" % base.get("sentence"),
              "- 本单一律退回引擎账，并在票面注明——把旧账当今天的账，正是两本账分叉的入口。"]
    else:
        L += ["- **这一问答不了**：%s" % base.get("sentence"),
              "- 缺面读成「没有持仓」会把整本书从现金重建，所以只印这一行。"]
    if sz.get("source") == "rule_same_bar_outcome":
        L += ["- **本单的 k 不取这本账**：账本 `%s` 那一行是**本张单自己执行后的结果**——"
              "票面按 k 下单、整手只花得比 k 少、账本记下更小的 k，再拿它回来定 k 就是"
              "一条只降不升的循环（r1476 实测 0.389744→0.389298→0.388680）。所以这一轮"
              "沿用规则 k，执行后的 k=%.6f 只作披露、不作输入。"
              % (sz.get("account_bar"), float(sz.get("k_executed") or 0.0))]
    elif sz.get("source") == "executed":
        L += ["- 本单按执行账 `%s` 的 k 定规模（那是**已经存在的一本书**，不是本轮结果）。"
              % sz.get("account_bar")]
    L += ["- 出处：%s。" % (base.get("face") or POSITIONS_FACE), ""]
    return L


def sizing_level(base, asof, k_engine, floor=None):
    """r1476: which k this sheet ORDERS, and why -- and the one case that must not feed back.

    r1471 sized the sheet from the executed account so the ticket stops ordering a book the
    desk does not hold. That is right when the account row comes from an EARLIER bar. It is
    wrong when the row was written by this same bar's own sheet: the sheet asks for k, whole
    lots spend less than k, the ledger writes the smaller executed k, and the next run of the
    same bar orders from that smaller number -- a monotone fixed-point iteration with a floor
    in it. Measured on 2026-11-06 by re-walking the chain three times: 0.389744 -> 0.389298
    -> 0.388680, ~0.0006 per run and never converging. r1474's "ticket k = ledger k" was two
    numbers that happened to meet at one point, not a mechanism.

    So: a ledger row for the bar being priced is the OUTCOME of this ticket and may not be
    its input; the level then comes from the sizing rule alone (the permission face still
    trims it). A row from an earlier bar is still an input, because that book really exists.
    """
    k_rule = float(k_engine)
    fl = None if floor is None else float(floor)
    # The permission is a hard cap, so the authorized level is min(rule, floor): asking for
    # the rule's k and then printing a trim table would tell the desk to sell names it does
    # not hold (the account already sits below the floor).
    cap = (lambda k: k if fl is None else min(float(k), fl))
    st = (base or {}).get("status")
    if st != "ok":
        return {"k": cap(k_rule), "source": "rule", "account_bar": None,
                "k_executed": None, "capped_by_floor": fl is not None and k_rule > fl,
                "reason": "no executed account to size from (base %s)" % st}
    bar = (base or {}).get("bar")
    if asof is not None and bar == asof:
        return {"k": cap(k_rule), "source": "rule_same_bar_outcome",
                "account_bar": bar, "k_executed": base.get("k_executed"),
                "capped_by_floor": fl is not None and k_rule > fl,
                "reason": ("the executed account for %s was written by this bar's own sheet, "
                           "so it is this ticket's outcome and cannot size it" % bar)}
    return {"k": cap(base["k_executed"]), "source": "executed",
            "account_bar": bar, "k_executed": base.get("k_executed"),
            "capped_by_floor": fl is not None and float(base["k_executed"]) > fl,
            "reason": "sized from the executed account for %s, a book that exists" % bar}


SIZING_PREREG_FACE = "results/etf_book_sizing_prereg.json"


def floor_quoting_faces(results_dir=None, floor=None, tol=1e-6):
    """r1478: which published faces carry this floor, derived by reading them.

    A re-issue is not one number moving: every receipt that quotes the floor is written
    against the old one, and the list of those receipts is exactly what has to be rebuilt.
    Writing that list by hand is the r1108 mistake one level up (a list nobody maintains
    reads as "nothing depends on this"), so the list is produced by scanning the published
    results tree for the floor's own value under a key that names it (k / floor / permitted).
    Faces that ISSUE the floor are tagged `source`, everything else `consumer`.
    """
    root = results_dir or PATHS.results_dir
    if floor is None:
        return {"status": "unreadable", "faces": [],
                "sentence": "没有可比的 floor 值，引用面无从清点（缺数不等于没有下游）"}
    want = float(floor)
    faces = {}

    def walk(obj, path, rel):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    walk(v, path + "/" + k, rel)
                elif isinstance(v, (int, float)) and not isinstance(v, bool):
                    name = str(k).lower()
                    if ("k" in name or "floor" in name or "permitted" in name) \
                            and abs(float(v) - want) <= tol:
                        entry = faces.setdefault(rel, [])
                        if len(entry) < 6:
                            entry.append(path + "/" + k)
        elif isinstance(obj, list):
            for i, v in enumerate(obj[:200]):
                if isinstance(v, (dict, list)):
                    walk(v, path + "[%d]" % i, rel)

    for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            if not fn.lower().endswith(".json"):
                continue
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, root).replace(os.sep, "/")
            try:
                with open(p, encoding="utf-8") as f:
                    walk(json.load(f), "", rel)
            except (OSError, ValueError):
                continue
    src = {os.path.basename(PERMISSION_FACE), os.path.basename(RULERS_FACE)}
    out = [{"face": "results/" + rel, "role": "source" if rel.split("/")[-1] in src
            else "consumer", "keys": keys}
           for rel, keys in sorted(faces.items())]
    return {"status": "ok", "faces": out, "n": len(out),
            "n_consumers": sum(1 for f in out if f["role"] == "consumer"),
            "floor": round(want, 6),
            "sentence": "%d published faces carry k=%.6f (%d of them consume it)"
                        % (len(out), want, sum(1 for f in out if f["role"] == "consumer"))}


def band_block(ticket_k, asof=None, prereg=None, permission=None, rulers=None,
               results_dir=None):
    """r1478: the sheet says how far its k sits from the ruler that signed it.

    r1477 pinned the band to the ruler's own noise (10.43pp of k, warn at 2 sd) and left
    the wiring for this round: an operator opening ORDER-*.md could not tell whether the
    number on it was inside the resolution of the ruler that authorised it. Two distances
    are printed, because they answer different questions: the FRESH reading re-derived on
    today's panel against the SIGNED floor (does the ruler still say the same thing), and
    the ticket's own k against that same signed floor (does the sheet obey it). The zone is
    the worse of the two -- reporting the flattering one is how a drift hides (E206).
    v1 is advisory: the band never changes k, it only refuses to stay quiet about it.
    """
    pre = prereg if prereg is not None else _json_face(SIZING_PREREG_FACE)
    band = (pre or {}).get("band") or {}
    inside = band.get("inside_pp")
    warn = band.get("warn_pp")
    if pre is None or inside is None or warn is None:
        return {"status": "unreadable", "zone": None,
                "sentence": ("没有可用的带子（%s 缺失或缺 inside_pp/warn_pp）："
                             "本单离签发的尺子有多远，这一问答不了" % SIZING_PREREG_FACE)}
    issued = None if permission is None else permission.get("permitted_k")
    fresh = None if rulers is None else rulers.get("k_now")
    if fresh is None and rulers is not None:
        fresh = ((rulers.get("rulers") or {}).get("window_x_universe") or {}).get("k")
    drift_pp = (None if issued is None or fresh is None
                else (float(fresh) - float(issued)) * 100.0)
    ticket_pp = (None if issued is None or ticket_k is None
                 else (float(ticket_k) - float(issued)) * 100.0)
    known = [abs(x) for x in (drift_pp, ticket_pp) if x is not None]
    if not known:
        return {"status": "unreadable", "zone": None, "band": band,
                "sentence": "签发的 floor 或票面 k 读不出来，距离无从计算（缺件不是合规）"}
    worst = max(known)
    zone = "inside" if worst <= float(inside) else ("warn" if worst <= float(warn)
                                                    else "outside")
    out = {"status": "ok", "zone": zone, "band": {"inside_pp": float(inside),
                                                  "warn_pp": float(warn),
                                                 "noise_pp": band.get("noise_pp")},
           "issued_k": None if issued is None else round(float(issued), 6),
           "fresh_k": None if fresh is None else round(float(fresh), 6),
           "ticket_k": None if ticket_k is None else round(float(ticket_k), 6),
           "drift_pp": None if drift_pp is None else round(drift_pp, 3),
           "ticket_gap_pp": None if ticket_pp is None else round(ticket_pp, 3),
           "worst_pp": round(worst, 3),
           # r1478: a distance of 0.000 on the first live reading is NOT "measured and
           # perfectly aligned" -- when the sheet's k IS the signed floor, both distances
           # are zero because of how the sheet was built, not because the ruler was
           # re-read and agreed. Printing 0.000 with no qualifier is the E206 shape (an
           # empty measurement that reads as a good one), so the zero says which zero it is.
           "zero_is_structural": bool(
               issued is not None and ticket_k is not None
               and abs(float(ticket_k) - float(issued)) <= 1e-9
               and (fresh is None or abs(float(fresh) - float(issued)) <= 1e-9)),
           "production_effect": band.get("production_effect"),
           "receipt": None}
    if zone == "outside":
        out["receipt"] = floor_quoting_faces(results_dir, issued)
        out["verdict"] = "BAND_EXCEEDED"
        out["sentence"] = ("本轮 k 离签发的 floor %.3fpp，超出 %.2fpp 的带子：票面 k 不变（v1 只读），"
                           "但要让换发回执重跑引用这个数的面（%s）。"
                           % (worst, float(warn),
                              out["receipt"].get("sentence") or "清单读不出来"))
    else:
        out["verdict"] = "WITHIN_BAND" if zone == "inside" else "BAND_WARN"
        out["sentence"] = ("距签发的 floor %.3fpp，落在尺子自己 %.2fpp 的分辨率%s。"
                           % (worst, float(inside),
                              "之内" if zone == "inside" else "之外（warn 档，仍不改 k）"))
    return out


def band_md(bb):
    """Print the band next to the size. Silence would read as "measured and fine"."""
    if not bb:
        return []
    L = ["", "## 这张单的 k 离签发的尺子有多远（r1478）"]
    if bb.get("status") != "ok":
        L += ["- **无法核验**：%s" % bb.get("sentence"), ""]
        return L
    if bb["zone"] == "inside":
        L += ["- 判定 **%s**：%s" % (bb["verdict"], bb["sentence"])]
    else:
        L += ["- %s 判定 **%s**：%s" % ("⚠" if bb["zone"] == "warn" else "⛔",
                                        bb["verdict"], bb["sentence"])]
    L += ["- 带子：±%.2fpp 内为「在尺子分辨率之内」，±%.2fpp 之外要换发回执"
          "（带子=尺子自己的 k 噪声%s，来自 `%s`，不许给默认值）。"
          % (bb["band"]["inside_pp"], bb["band"]["warn_pp"],
             " %.2fpp" % bb["band"]["noise_pp"] if bb["band"].get("noise_pp") else "",
             SIZING_PREREG_FACE)]
    L += ["- 三个数分开印：签发 k=%s｜本轮重读 k=%s（差 %s pp）｜本单 k=%s（差 %s pp）"
          % ("-" if bb["issued_k"] is None else "%.6f" % bb["issued_k"],
             "-" if bb["fresh_k"] is None else "%.6f" % bb["fresh_k"],
             "-" if bb["drift_pp"] is None else "%+.3f" % bb["drift_pp"],
             "-" if bb["ticket_k"] is None else "%.6f" % bb["ticket_k"],
             "-" if bb["ticket_gap_pp"] is None else "%+.3f" % bb["ticket_gap_pp"])]
    if bb.get("zero_is_structural"):
        L += ["- **这个 0.000pp 是构造出来的，不是量出来的**：本单的 k 就是签发的 floor 本身"
              "（`min(规则 k, 额度)`），所以两个距离必然为零——它说的是「票面照抄了额度」，"
              "不是「尺子重读后与签发值一致」。带子要真开火，需要额度重算出低于本单 k 的读数。"]
    if bb.get("production_effect"):
        L += ["- 这一节**只读**：%s" % bb["production_effect"]]
    rc = bb.get("receipt")
    if rc:
        if rc.get("status") == "ok":
            L += ["- **换发回执要重跑的面（%d 个，%d 个消费者）**——清单由扫描 `results/` 里"
                  "引用 k=%.6f 的已发布面派生，不是手写：" % (rc["n"], rc["n_consumers"],
                                                              rc["floor"])]
            for f in rc["faces"]:
                L.append("  - `%s`（%s）" % (f["face"], f["role"]))
        else:
            L += ["- **要重跑哪些面：这一问答不了** —— %s" % rc.get("sentence")]
    L.append("")
    return L


def floor_ledger_md(fl):
    """r1457: a trim printed on one sheet is not obedience on the next decision bar.

    r1456 measured the schedule that erases it. This line makes the sheet itself carry
    the answer, so the desk does not have to remember a verdict from another file:
    a floor that is no longer satisfied by the path is printed as REAPPLY_REQUIRED here,
    on the sheet someone actually executes. A missing ledger reads as UNKNOWN (r1108).
    """
    if fl is None:
        return ["- **额度是否仍在生效：无法核验** —— %s 缺失；票面裁剪只对这一张单有效，"
                "下一决策 bar 要重新施加（r1456）。" % FLOOR_FACE]
    a = fl.get("assessed") or {}
    v = a.get("verdict")
    if not v:
        return ["- **额度是否仍在生效：无法核验** —— %s 里没有 assessed 块。" % FLOOR_FACE]
    floor = a.get("floor")
    floor_s = "无法核验" if floor is None else "%.6f" % floor
    L = ["- 地板台账（%s）：**%s** ← 当期 floor k=%s，签发于 %s；排程末决策 bar k=%s"
         % (FLOOR_FACE, v, floor_s, a.get("floor_issued") or "?",
            "无法核验" if a.get("k_schedule_last") is None else "%.6f" % a["k_schedule_last"])]
    if v == "REAPPLY_REQUIRED":
        L += ["- ⚠ **下一决策 bar 要重新裁剪**：这一张单守住了额度，但排程在那一个 bar 上 still "
              "sizes at the ordered size —— 不重新施加，下一张单就会重新超额度。"]
    elif v == "NOT_ENFORCED":
        L += ["- ⚠ **无人执行这条额度**：排程与票面都在 floor 之上。"]
    elif v == "REISSUE_REQUIRED":
        L += ["- ⚠ **额度要重签**：它由旧票面定价，最新票面已换代。"]
    elif v == "HOLDING":
        L += ["- 路径本身已在 floor 之下，下张单无需再裁剪。"]
    if a.get("action"):
        L += ["- 该做什么：%s" % a["action"]]
    return L


def permission_block(ticket, perm, rulers=None):
    """r1455: does this sheet size to what the desk's own permission allows?

    r1450 turned five readings of one sizing rule into a permission (floor k=0.393073,
    ceiling k=0.544424) and its prereg requirement 4 asked for the chosen size to be carried
    into the 2026-11-11 ticket with the unused readings printed beside it. Nothing carried
    it: r1451 measured the ticket in force at k=0.460253 and found no module reading the
    receipt, so the file an operator executes ordered 6.72pp more than the file that
    authorises it (r1108 有产无读 in its most expensive form -- a *smaller* order is not what
    a missing reader costs you).

    So this sheet now reads the permission itself and prints, next to the weights:
    the floor, the ceiling, the size it is about to order, and -- when the order is over --
    the integer-lot trim that lands at or below the floor (shared arithmetic with
    scripts/etf_book_cut_order_gap.py, floor-and-never-round). An absent or unreadable
    receipt reads as UNKNOWN, never as a pass.

    Two published faces quote this number (results/etf_book_rebalance_permission.json and
    results/etf_book_size_rulers_decision.json). They are allowed to disagree in the world;
    they are NOT allowed to disagree silently (E289): a mismatch is printed as CONFLICT and
    the sheet refuses to call itself executable.
    """
    if not ticket:
        return {"status": "unreadable", "reason": "no_ticket",
                "sentence": "本单没有可定价的仓位，额度无从对照"}
    k_now = ticket.get("beta_k")
    if k_now is None:
        return {"status": "unreadable", "reason": "ticket_missing_k",
                "sentence": "票据里没有 k，额度无从对照"}
    k_now = float(k_now)
    if not perm:
        return {"status": "unreadable", "reason": "missing_permission_receipt", "k_now": k_now,
                "sentence": ("缺 %s：本单是否超出批准额度**未知**（缺件不等于合规）"
                             % PERMISSION_FACE)}
    floor = perm.get("permitted_k")
    if floor is None:
        return {"status": "unreadable", "reason": "permission_missing_floor", "k_now": k_now,
                "sentence": "%s 里没有 permitted_k，额度无从对照" % PERMISSION_FACE}
    floor = float(floor)
    ceiling = ((perm.get("naive_max_over_all_readings") or {}).get("k"))
    if ceiling is None and rulers:
        ceiling = rulers.get("k_ceiling")
    ceiling = None if ceiling is None else float(ceiling)
    nav = ticket.get("nav")
    undeployed = float(ticket.get("underspend_pct") or 0.0)

    # E289: two copies of one number must agree, or the reader is told they do not.
    conflicts = []
    if rulers and rulers.get("k_floor") is not None:
        if abs(float(rulers["k_floor"]) - floor) > 1e-6:
            conflicts.append("%s 的 k_floor=%r 与权限面 permitted_k=%.6f 不一致"
                             % (RULERS_FACE, rulers.get("k_floor"), floor))

    over = k_now > floor + 1e-6
    trim = None
    if over and nav:
        trim = trim_legs(ticket.get("order") or [], floor, float(nav), undeployed)

    unused = []
    for name, cell in (perm.get("readings") or {}).items():
        k = (cell or {}).get("k")
        if k is None:
            continue
        k = float(k)
        if abs(k - floor) <= 1e-6 or abs(k - k_now) <= 1e-6:
            continue
        unused.append({"ruler": name, "k": k,
                       "delta_vs_now_pp": (cell or {}).get("delta_vs_now_pp"),
                       "kind": (cell or {}).get("kind")})

    if conflicts:
        status = "conflict"
    elif over:
        status = "trim_required"
    else:
        status = "within_permission"
    return {"status": status,
            "k_now": k_now, "permitted_k": floor, "ceiling_k": ceiling,
            "decision_date": perm.get("decision_date"),
            "nav_cny": None if nav is None else float(nav),
            "ordered_book_cny": None if nav is None else round(k_now * float(nav), 2),
            "permitted_book_cny": None if nav is None else round(floor * float(nav), 2),
            "over_by_cny": None if nav is None else round((k_now - floor) * float(nav), 2),
            "trim": trim,
            "trim_lands_within": (None if not trim or trim.get("k_after") is None
                                  else bool(trim["k_after"] <= floor + 1e-6)),
            "unused_readings": unused,
            "conflicts": conflicts,
            "artifact": PERMISSION_FACE,
            "verdict": ("PERMISSION_FACES_CONFLICT" if conflicts else
                        "TRIM_REQUIRED" if over else "WITHIN_PERMISSION")}


def permission_md(pb):
    """Print the permission next to the weights. Silence is not an option (r1108)."""
    if pb is None:
        return []
    L = ["", "## 这张单按谁的额度下单（r1455·批准额度）"]
    if pb.get("status") == "unreadable":
        L += ["- **无法核验**：%s。" % (pb.get("sentence") or "额度读不出来"),
              "- 读法：缺件读成「合规」是最贵的一种误读，所以这一节一旦读不出来就只印这一行。", ""]
        return L
    L += ["- 额度下限 k=%.6f（风险腿 ¥%s），上限 k=%s；本单 k=%.6f（¥%s）"
          % (pb["permitted_k"], format(pb.get("permitted_book_cny") or 0, ",.0f"),
             "-" if pb.get("ceiling_k") is None else "%.6f" % pb["ceiling_k"],
             pb["k_now"], format(pb.get("ordered_book_cny") or 0, ",.0f")),
          "- 判定：**%s**%s" % (pb["verdict"],
                              "" if pb["status"] == "within_permission"
                              else "｜超出 ¥%s" % format(pb.get("over_by_cny") or 0, ",.0f"))]
    if pb.get("conflicts"):
        L += ["- ⚠ **两张已发布的额度面互相矛盾**：%s。在它们一致之前，本单不宣称自己按额度执行。"
              % "；".join(pb["conflicts"])]
    t = pb.get("trim")
    if pb["status"] != "within_permission":
        L += ["", "上面那张表是**未裁剪的下单量（不可执行）**；按额度执行要这样卖：", "",
              "| 代码 | 价 | 现手数 | 目标手数 | 卖出手数 | 卖出 CNY |",
              "|---|---|---|---|---|---|"]
        for r in (t or {}).get("legs") or []:
            if not r.get("priced"):
                L += ["| %s | %s | %s | — | — | 未定价 |"
                      % (r.get("symbol"), r.get("price"), r.get("lots_now"))]
                continue
            L += ["| %s | %s | %d | %d | %d | %s |"
                  % (r.get("symbol"), r.get("price"), r.get("lots_now"), r.get("lots_target"),
                     r.get("lots_sell"), format(r.get("sell_cny") or 0, ",.0f"))]
        L += ["",
              "- 卖出合计 %s 手 / ¥%s，整手取整后 k=%.6f（%s）"
              % ((t or {}).get("lots_sell_total"),
                 format((t or {}).get("sold_cny") or 0, ",.0f"),
                 (t or {}).get("k_after") or 0.0,
                 "不超过额度" if pb.get("trim_lands_within") else "**仍超出额度**")]
        if not pb.get("trim_lands_within"):
            L += ["- ⚠ 取整后仍超额度：这正是「四舍五入会把仓位顶回去」的地方，本单拒绝把这一版当可执行单。"]
        if t and pb["status"] == "trim_required":
            L += ["- 读法：上面那张未裁剪表是「按规则算出来的仓位」，这张裁剪表是「按额度允许的仓位」；"
                  "两者差的就是批准额度这一步，缺了它，票面读起来完全一样。"]
    if pb.get("unused_readings"):
        L += ["", "- 额度没采用的读数（同一规则、同一面板，只换尺子）：%s"
              % "；".join("%s k=%.6f（%+.2fpp，%s）"
                          % (u["ruler"], u["k"], u.get("delta_vs_now_pp") or 0.0,
                             u.get("kind") or "?")
                          for u in pb["unused_readings"])]
    L += ["- 出处：%s（决策日 %s）；裁剪算术与 scripts/etf_book_cut_order_gap.py 共用一处实现。"
          % (pb.get("artifact"), pb.get("decision_date") or "?"), ""]
    L += floor_ledger_md(_floor_face())
    L.append("")
    return L


def card(ticket, mk, sched, asof, beta, extra):
    L = ["# ETF 复合书 · 可执行订单单（%s）" % asof, "",
         "当前活：β 目标 %.2f 的单本 R%d N%d + GC001 现金腿，每 %d 个交易日重算一次 k。"
         % (beta, REBAL, N_HOLD, REBAL),
         "最近实物：%s（本文件同日生成）。"
         % os.path.relpath(os.path.join(OUT_DIR, "TICKET-%s.json" % asof), BASE).replace("\\", "/"),
         "下个里程碑：下一决策日落单后前向账本追加一行（窗 ≤48h，随面板推进）。", ""]
    feed = extra.get("feed")
    if feed:
        lag = feed.get("lag_days")
        L += ["## 数据新鲜度（本单定价用的是哪一天的 bar）",
              "- 官方交易日历期望最新 bar：%s" % (feed.get("expected_bar") or "未知（无日历）"),
              "- 本单定价 bar：%s" % (feed.get("ticket_bar") or "未知"),
              "- 判定：**%s**｜落后 %s 个交易日" % (feed.get("status", "unknown"),
                                                  "?" if lag is None else lag),
              "- %s" % feed.get("detail", ""), ""]
        if feed.get("status") in ("stale_feed", "feed_broken"):
            L += ["> ⚠ 提醒：本单的定价 bar 落后市场 %s 个交易日 —— 这是数据面的滞后，"
                  "不是书换了判断。照此单下手前必须知道这一点。" % ("?" if lag is None else lag), ""]
    L += restatement_md(extra.get("restatements"))
    if extra.get("withdrawals"):
        L += ["", "> 账本撤回：%s" % extra["withdrawals"]]
    L += reinstatement_md(extra.get("reinstatements"))
    L += reinstated_history_md(extra.get("reinstated_history"))
    if ticket:
        L += ["## 今日目标（NAV ¥%s）" % format(int(ticket["nav"]), ","),
              "k=%.2f（书内 %.0f%%、现金 %.0f%%）｜ 现金腿=%s ｜ 现金 ¥%s"
              % (ticket["beta_k"], ticket["book_weight"] * 100,
                 ticket["cash_weight"] * 100, ticket["cash_leg"],
                 format(int(ticket["cash_amount"]), ",")),
              "", "| 代码 | 权重 | 类别 | 参考价 | 手数 | 股数 | 金额 |", "|---|---|---|---|---|---|---|"]
        for r in ticket["order"]:
            L.append("| %s | %.1f%% | %s | %s | %s | %s | %s |"
                     % (r["symbol"], r["weight"] * 100, r.get("class") or "?",
                        ("%.3f" % r["price"]) if r["price"] else "-",
                        r["lots"] if r["lots"] is not None else "-",
                        r["shares"] if r["shares"] is not None else "-",
                        format(int(r["amount"]), ",") if r["amount"] else "-"))
        L += ["", "整手取整后欠投 %.2f%% NAV（留在现金腿，不重分配）。" % ticket["underspend_pct"]]
        L += permission_md(extra.get("permission"))
        L += band_md(extra.get("size_band"))
        L += swap_trigger_md(extra.get("swap_trigger"))
        L += swap_stack_md(extra.get("swap_stack"))
        L += executed_base_md(extra.get("base"))
        L += positions_md(extra.get("positions"))
        cm = extra.get("cash_money")
        if cm:
            L += ["", "## 现金那一半今天赚多少钱（r1245）"]
            if cm.get("verdict") == "CANNOT_PRICE":
                L += ["- %s" % (cm.get("sentence") or "现金腿收益不可读。")]
            else:
                L += ["- %s。" % cm["sentence"],
                      "- 读法：现金占比 %.0f%% 不是「没仓位」，它是一笔按天计息的停车位；"
                      "上面三个数用同一块 repo 面板、同一笔 ¥%s 算出来，差别只来自取哪一段利率。"
                      % (ticket["cash_weight"] * 100,
                         format(int(cm["cash_amount_cny"]), ",")),
                      "- 出处：%s（同一块面板，%d 个报价的尾窗；判定 **%s**）。"
                      % ("data/repo_daily/GC001.csv", cm["spot"]["quotes"], cm["verdict"])]
        L += entry_gate_md(extra.get("entry_gate"))
        rp = extra.get("reprice")
        if rp and rp.get("status") == "ok":
            L += ["", "## 参考价用的是哪一天（这会改变手数）",
                  "- 权重来自决策 bar **%s**（网格日之间不重排），价格来自定价 bar **%s**"
                  % (rp["decision_bar"], rp["priced_bar"]),
                  "- 判定：**%s**｜%s" % (rp["verdict"], rp["sentence"]), ""]
            if rp["verdict"] == "REPRICED_TO_THE_BAR_YOU_PAY":
                L += ["| 代码 | 决策 bar 收 | 定价 bar 收 | 漂移 | 手数(旧→新) | 金额(旧→新) |",
                      "|---|---|---|---|---|---|"]
                for r in rp["names"]:
                    if r.get("drift_pct") is None:
                        L.append("| %s | %s | - | 无定价 bar 报价 | %s | %s |"
                                 % (r["symbol"], r.get("decision_price") or "-",
                                    r.get("lots_at_priced") if r.get("lots_at_priced") is not None else "-",
                                    r.get("amount_at_priced") if r.get("amount_at_priced") else "-"))
                        continue
                    L.append("| %s | %.3f | %.3f | %+.2f%% | %s→%s | %s→%s |"
                             % (r["symbol"], r["decision_price"], r["priced_price"],
                                r["drift_pct"],
                                r["lots_at_decision"], r["lots_at_priced"],
                                format(int(r["amount_at_decision"]), ","),
                                format(int(r["amount_at_priced"]), ",")))
                L += ["", "读法：手数是按「今天要付的价」算的；旧口径把 %s 的收盘当成今天的参考价，"
                      "所以那一版的手数/欠投是按十几天前的一张价目表算出来的。" % rp["decision_bar"]]
        elif rp:
            L += ["", "## 参考价用的是哪一天",
                  "- 两套价格基准里有一套没能建起来，本单**不能**说明自决策 bar 以来价格变了多少。"]
    else:
        L += ["## 今日目标", "当日无有效信号（可选池不足），不下单。"]
    if sched:
        ks = [k for _, k, _ in sched]
        L += ["", "## k 历程", "决策 %d 次｜均值 %.2f｜区间 %.2f~%.2f｜触顶(≥0.999)占比 %.0f%%"
              % (len(ks), float(np.mean(ks)), min(ks), max(ks),
                 100.0 * sum(1 for k in ks if k >= 0.999) / len(ks))]
    if mk and mk.get("book"):
        L += ["", "## 同期对照（%s 起）" % extra.get("inception"),
              "| 账簿 | 年化 | 夏普 | 最大回撤 |", "|---|---|---|---|"]
        for name, zh in (("book", "本账（β 目标 + GC001）"), ("same_beta_benchmark", "同 β 指数+现金")):
            b = mk.get(name)
            if b:
                L.append("| %s | %.1f%% | %.2f | %.1f%% |" % (zh, b["cagr"] * 100, b["sharpe"],
                                                             b["maxdd"] * 100))
        if "excess_pp" in mk:
            L += ["", "超额 %+.2fpp/年（同 β 基准对照，成本双层已计）。" % mk["excess_pp"]]
    cs = extra.get("carry")
    if cs:
        L += ["", "## 这条年化里有多少是现金利息",
              "同一本书换三种现金利率重算（β %.2f 档）：按全窗真实 repo 利率年化 **%.2f%%** → "
              "按今天利率持平年化 **%.2f%%** → 现金零收益年化 **%.2f%%**。"
              % (cs["beta"], cs["observed_pct"], cs["flat_today_pct"], cs["zero_pct"]),
              "- 现金利息贡献 **%.2fpp = 年化的 %.1f%%**；现金占比 %.0f%%，利率每降 100bp "
              "年化约少 %.2fpp。"
              % (cs["carry_pp"], cs["carry_share_pct"], (cs["cash_share"] or 0.0) * 100,
                 cs["pp_per_100bp"] or 0.0),
              "- 读法：把现金腿按零利率计这本书仍有 %.2f%% —— 选股机器本身不是靠停车费活着；"
              "但今天报价里的 %.1f%% 确实是 repo 利息，利率掉到今天的 %.2f%%（%s 报价）"
              "就是少赚 %.2fpp，不是这个月选错了票。"
              % (cs["zero_pct"], cs["carry_share_pct"], cs["rate_today_pct"] or 0.0,
                 cs["rate_today_date"] or "未知", cs["flat_rate_cost_pp"])]
        if cs["evidence_cutoff"] and asof and cs["evidence_cutoff"] != asof:
            L += ["- ⚠ 拆解定价 bar %s 落后本单 %s：这是拆解面没跟上，不是利率变了，"
                  "按旧 bar 的数字只当量级读。" % (cs["evidence_cutoff"], asof)]
        L += ["- 出处：%s（cutoff %s；探索件，无预注册、无判决、不入账本）。"
              % (cs["artifact"], cs["evidence_cutoff"] or "未知")]
    else:
        L += ["", "## 这条年化里有多少是现金利息",
              "- 拆解面在盘上没有可用读数（results/etf_book_return_regime.json 缺失或"
              "缺本 β 档）：上面那个年化含现金利息，具体多少本单不报 —— "
              "这正是 r1367 要修的那个空白。"]
    db = drawdown_band()
    if db:
        L += ["", "## 最大回撤：本单上面那个数是中位数，不是尾部（r1348）",
              "本账簿只有一个历史。对同一条收益路径做块自助（块长 %s 根 bar，块长本身是自由参数），"
              "%s 百分位最大回撤落在 **%.1f%% ~ %.1f%%**，中位落在 %.1f%% ~ %.1f%%，"
              "跌破 -20%% 的重采样占比 %.1f%% ~ %.1f%%。"
              % ("/".join(str(b) for b in db["block_set"]), "5",
                 db["maxdd_p5"]["min"] * 100, db["maxdd_p5"]["max"] * 100,
                 db["maxdd_p50"]["min"] * 100, db["maxdd_p50"]["max"] * 100,
                 db["dd_break"]["min"] * 100, db["dd_break"]["max"] * 100),
              "- 口径：band 定价于 %s bar（%s）。按 p5 一档定仓位，不按中位一档。"
              % (db["evidence_cutoff"] or "未知", db["artifact"])]
    else:
        L += ["", "## 最大回撤的尾部", "- 无自助带在盘：上面只有单路径回撤，尾部未发布。"]
    ag = extra.get("agreement")
    if ag:
        L += ["", "## 两张生产面是不是同一天",
              "- 决策 bar：卡片 %s ｜ 本单 %s ｜ 一致=%s"
              % (ag["card_decided_at"], ag["ticket_book_decided_at"], ag["same_decision_bar"]),
              "- 定价 bar：卡片 %s（%s）｜ 本单 %s（%s）｜ 一致=%s"
              % (ag["card_priced_bar"] or "未知", ag["card_feed_status"] or "未知",
                 ag["ticket_priced_bar"], (feed or {}).get("status", "未知"),
                 ag["same_priced_bar"])]
        if not ag["same_priced_bar"]:
            L += ["- ⚠ 两张面定价不在同一天：卡片是配置口径的对照面、本单是可执行面，"
                  "若两张之间跨过了一个网格决策日，它们描述的是两本不同的书 —— 照单下手前"
                  "只看本单的仓位，卡片的名数与波动目标行不可当今天的仓位用。"]
        pf = extra.get("priced_faces")
        if pf:
            day = "卡片 %s ｜ 本单 %s ｜ CEO 一页纸 %s" % (
                (pf.get("faces") or {}).get("card") or "未知", ag["ticket_priced_bar"],
                (pf.get("faces") or {}).get("page") or "未知")
            if pf.get("verdict") == "SAME_DAY":
                L += ["- **同一天**：%s —— 三张纸的数是同一本书。" % day]
            elif pf.get("verdict") == "DIFFERENT_DAYS":
                L += ["- **不是同一天**：%s —— %s。落后的那一张只能当历史读，不能与今天的仓位"
                      "并排比。" % (day, pf.get("detail") or "无细节")]
            else:
                L += ["- **无法判断**：%s —— %s。缺一天不是「一致」。" % (
                    day, pf.get("detail") or "无细节")]
    wd = extra.get("width")
    if wd:
        d = wd["delta_ticket_minus_card"]
        L += ["", "## 这张单是 %d 名，卡片是 %d 名" % (wd["ticket_names"], wd["card_names"]),
              "两张面不只名数不同，杠杆规则也不同（本单 %s 覆盖 / 卡片 %s 目标），"
              "所以下表的差值是一条对角线，不是「名数的代价」："
              % (wd["ticket_rule"], wd["card_rule"]),
              "| 账簿 | 名数 | 规则 | 年化 | 夏普 | 实现波动 | 最大回撤 |",
              "|---|---|---|---|---|---|---|",
              "| 本单（可执行） | %d | %s | %.1f%% | %.2f | %.1f%% | %.1f%% |"
              % (wd["ticket_names"], wd["ticket_rule"], wd["ticket"]["cagr"] * 100,
                 wd["ticket"]["sharpe"], (wd["ticket"].get("vol") or 0.0) * 100,
                 wd["ticket"]["maxdd"] * 100),
              "| 卡片（对照面） | %d | %s | %.1f%% | %.2f | %.1f%% | %.1f%% |"
              % (wd["card_names"], wd["card_rule"], wd["card"]["cagr"] * 100,
                 wd["card"]["sharpe"], (wd["card"].get("vol") or 0.0) * 100,
                 wd["card"]["maxdd"] * 100),
              "", "本单 − 卡片：年化 %+.2fpp、夏普 %+.3f、波动 %+.2fpp、回撤 %+.2fpp。"
              % (d["cagr_pp"], d["sharpe"], d.get("vol_pp") or 0.0, d["maxdd_pp"])]
        we = wd.get("width_effect") or {}
        if we:
            L += ["", "同一规则下只换名数（这才是名数的代价）："]
            for rule, v in sorted(we.items()):
                L += ["- %s 规则：%d 名 → %d 名 年化 %+.2fpp"
                      % (rule, wd["ticket_names"], wd["card_names"], v["pp"])]
        L += ["", "读法：名数的代价随规则变号（β 覆盖下宽账少担风险 → 少赚；8%% 波动目标下"
              "两宽度实现波动相当 → 名数几乎不花钱）。两张面的夏普差 %+.3f，即风险调整后"
              "基本等价——两者之间选，是选承担多少波动，不是选谁更会选股。"
              % d["sharpe"],
              "出处：%s（cutoff %s）。" % (wd["source"], wd["evidence_cutoff"])]
    ru = extra.get("ruler") or {}
    if ru.get("state") == "inside_disagreement":
        L += ["", "## 两张面之间的差，落在两台引擎自己打架的范围里",
              "把本单和卡片放到同一条尺子上、逐相位配对：中位差 **%+.2fpp**"
              "（%d 个相位，%s 个往上、%s 个往下，区间 %+.2f ~ %+.2f）；"
              "同一档 5→12 名在另一台引擎上是 **%+.2fpp** —— 两台引擎对这一档的分歧 "
              "**%+.2fpp**（方向还相反）。"
              % (float(ru["gap_pp"]), ru["pairs"], ru.get("positive_phases"),
                 (ru["pairs"] - (ru.get("positive_phases") or 0)) if ru.get("pairs") else "?",
                 float(ru.get("min_pp") if ru.get("min_pp") is not None
                       else -abs(float(ru.get("spread_pp") or 0)) / 2),
                 float(ru.get("max_pp") if ru.get("max_pp") is not None
                       else abs(float(ru.get("spread_pp") or 0)) / 2),
                 float(ru.get("capacity_rung_pp") or 0), float(ru["disagreement_pp"])),
              "- 读法：这个差只有引擎分歧的 **%.1f%%**，所以「本单比卡片差多少」这句话"
              "在本窗读不出来——能读出来的是：两张面之间的大部分差来自杠杆规则（β 覆盖 vs "
              "8%% 波动目标），不是名数。挑哪张面照旧看愿意承担多少波动。"
              % (100.0 * (ru.get("share_of_disagreement") or 0.0)),
              _resolution_md(ru),
              "- 出处：%s（cutoff %s，%s 个相位配对）。"
              % (ru["source"], ru["evidence_cutoff"], ru["pairs"])]
    elif ru.get("state") and ru["state"] != "unavailable":
        L += ["", "## 两张面之间的差（尺子没给出干净的读数）",
              "- 尺子状态：**%s** —— %s" % (ru["state"], ru.get("detail") or ""),
              "- 出处：%s（cutoff %s）。" % (ru.get("source"), ru.get("evidence_cutoff"))]
    L += ["", "## 诚实面", "",
          "- 探索件：无预注册、无判决、不入成绩账本。"]
    if not wd:
        L += ["- **名数差未定价**：本单 %d 名而生产卡片跑不同名数，本窗未取到宽度审计"
              "（scripts/etf_book_width_audit.py），差额未知。" % N_HOLD]
    st = extra.get("stale")
    if st:
        L += ["- **面板新鲜度**：最后 bar 全池 %d/%d 只有价；历史决策中 %.1f%% 的选票落在"
              "决策日之前已停更的标的上（最坏滞后 %d 天）——停更标的被 ffill 冻结成零收益持仓，"
              "读数会因此偏乐观。" % (st["symbols_with_value_on_last_bar"], st["symbols_total"],
                                     100.0 * (st.get("stale_share") or 0.0),
                                     st["worst_stale_gap_days"])]
    if ticket and ticket.get("basket_drift"):
        L += ["- **票面不可执行**：%d/%d 只在收盘日无价（停更），本单只能作为研究面参考。"
              % (len(ticket["basket_drift"]), len(ticket["order"]))]
    if extra.get("bets_line"):
        L += ["- **五只名字不是五个赌注**：%s" % extra["bets_line"]]
    if extra.get("conc_line"):
        L += ["- **这笔钱是从哪赚来的**：%s" % extra["conc_line"]]
    pb = extra.get("price_basis") or {}
    if pb.get("sentence"):
        L += ["- **价格面板**：%s" % pb["sentence"]]
    pdg = pb.get("panel_digest") or {}
    if pdg.get("digest"):
        L += ["- **面板指纹**：`%s`（%d 个交易日 × %d 只票，%s→%s，覆盖 %s）——卡片和账本印同一个"
              "指纹才叫同一本书；指纹不同不是算错，是两张纸在给不同的世界定价。"
              % (pdg["digest"], pdg["dates"], pdg["columns"], pdg["first"], pdg["last"],
                 "/".join(pdg.get("blocks") or []))]
    fcs = extra.get("family_coherence") or {}
    if fcs.get("verdict") == "ONE_WORLD":
        L += ["- **名数的来历**：%d 个宽度臂的判词全部算在同一张面板 `%s`（截至 %s）——本单这个名数是"
              "比出来的宽度，不是拍出来的配置。"
              % (fcs.get("arms") or 0, ((fcs.get("panels") or [""])[0] or "?"),
                 fcs.get("evidence_cutoff"))]
    elif fcs.get("verdict"):
        L += ["- **名数没被证过**：宽度臂家族已收回自己的判词（%s，%s），所以本单这个名数只是配置，"
              "不是测出来的最优。" % (fcs["verdict"], fcs.get("detail") or "无细节")]
    else:
        L += ["- **名数没被证过**：读不到宽度臂家族的面（%s）——这是「没验」，不是「没问题」。"
              % (fcs.get("detail") or "家族面缺席")]
    L += ["- 票池=现存 ETF，存在幸存者偏差；票面仅按收盘价折算，未计冲击成本与涨跌停。",
          "- GC001 单期限且滚动假设零费；真实现金台应做 1/7/14 天梯队。",
          "- k 每 %d 个交易日才重算，段内实际 β 仍会漂移。" % REBAL]
    return "\n".join(L) + "\n"


def staleness_stats(score, close, rebal=REBAL, n_hold=N_HOLD, start="2020-01-01"):
    """How much of the book is picked on stale prices?

    This panel is refreshed only for a core handful of instruments; the rest were frozen
    at a one-off batch pull (see DIGEST-20261021-e35). The engine ffill's prices, so a
    frozen symbol silently becomes a zero-return holding. Any book number is suspect
    until the share of stale picks is known.
    """
    dates = [d for d in close.index if d >= pd.Timestamp(start)]
    decs = dates[::rebal]
    picked = stale = impossible = 0
    worst_gap = 0
    last_valid = close.apply(lambda s: s.dropna().index[-1] if s.notna().any() else s.index[0])
    for d in decs:
        s = score.loc[d].dropna() if d in score.index else pd.Series(dtype=float)
        if len(s) < n_hold:
            impossible += 1
            continue
        bar = close.loc[d]
        for p in s.nlargest(n_hold).index:
            picked += 1
            px = bar.get(p, np.nan)
            if not np.isfinite(px):
                stale += 1
                lv = last_valid.get(p)
                worst_gap = max(worst_gap, int((d - lv).days) if lv is not None else 9999)
    live_last = int(close.iloc[-1].notna().sum())
    return {"decisions": len(decs), "picks": picked,
            "stale_picks": stale,
            "stale_share": round(stale / picked, 4) if picked else None,
            "worst_stale_gap_days": worst_gap,
            "symbols_with_value_on_last_bar": live_last,
            "symbols_total": int(close.shape[1]),
            "decisions_with_too_few_picks": impossible}


def price_basis(close, cols, repaired=None):
    """Which prices this sheet's numbers are computed on, and how many prints that costs.

    One arithmetic, one sentence: `etf_equity_alpha.flip_census` counts the raw panel and
    `etf_equity_alpha.price_basis_line` writes the line, so this sheet and the production
    card cannot drift into quoting two different definitions of "clean" (E289).

    Since r1177 this sheet repairs (`REPAIR_PANEL`), matching the card and the forward
    ledger. Before that it was the only live face ranking on raw prices: a share-count flip
    that reads as a -90% day could enter a pick here and nowhere else, and the ticket's
    CAGR was then compared against a card priced on the other panel.
    """
    try:
        import etf_equity_alpha as A
    except Exception:
        return {"panel": "unknown", "flip_thr": None, "flip_prints": None,
                "sentence": ("本单的数字算在哪张价格面板上读不到（etf_equity_alpha 不可用），"
                             "所以这里不替它下结论。")}
    cen = A.flip_census(close, cols)
    line = A.price_basis_line(bool(REPAIR_PANEL if repaired is None else repaired),
                              cen["prints"], cen["thr"], cen["symbols"],
                              PRICE_BASIS_ARTIFACT, columns=cen["columns"])
    line["columns"] = cen["columns"]
    return line


def family_coherence():
    """Whether the width family that licenses this sheet's name count was one measurement.

    One implementation: `etf_book_production.family_coherence()` owns the rule and this
    sheet only quotes it (E289). The card has carried the verdict since r1183, but the
    executable sheet -- the face an operator actually holds -- printed a width and its
    CAGR without ever saying whether the arms behind that width priced one panel. A
    missing or unreadable face reads "unproven here", never a pass.
    """
    try:
        import sys as _sys
        _d = os.path.dirname(os.path.abspath(__file__))
        if _d not in _sys.path:
            _sys.path.insert(0, _d)
        import etf_book_production as _P
        return _P.family_coherence()
    except Exception as e:
        return {"artifact": "results/etf_book_phase_atlas_arms.json", "verdict": None,
                "detail": "arm family face unreadable (%r)" % (e,), "panels": [],
                "arms": 0, "evidence_cutoff": None, "priced_same_panel": None}


def priced_face_check(card_bar, ticket_bar):
    """Which day each of the three papers a reader holds was priced on (r1186).

    One implementation: `etf_book_production.priced_faces()` owns the rule; this sheet only
    supplies its own bar and quotes the three-state answer. Until r1186 the sheet published
    the bare boolean `same_priced_bar`, which tells a reader "different" without saying
    WHICH paper is the stale one -- a claim nobody can re-derive. The page's day is read
    from the page's own artifact, so on a chain day where the page has not caught up yet
    this sheet will name it instead of agreeing with itself.
    """
    try:
        import sys as _sys
        _d = os.path.dirname(os.path.abspath(__file__))
        if _d not in _sys.path:
            _sys.path.insert(0, _d)
        import etf_book_production as _P
        return _P.priced_faces(card_bar=card_bar, ticket_bar=ticket_bar)
    except Exception as e:
        return {"faces": {"card": card_bar, "ticket": ticket_bar, "page": None},
                "verdict": "UNKNOWN", "detail": "reader failed (%s)" % str(e)[:120],
                "missing": ["page"], "same_day": None}


def run(beta=DEFAULT_BETA, nav=DEFAULT_NAV, inception=DEFAULT_INCEPTION, fresh_gate=False):
    global OUT_DIR
    if fresh_gate:
        OUT_DIR = os.path.join(PATHS.results_dir, "etf_book_order_fresh")
    close, openp, amt, feats = F.build_panel()
    classes = pd.Series(classify(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in V.KEEP]
    # census on the panel as the source prints it: after the repair the count is zero by
    # construction, and a disclosure that always reads "no flips" discloses nothing.
    basis = price_basis(close, cols)
    if REPAIR_PANEL:
        close, openp, _n_flip = AE.repair_flips(close, openp)
        print("price basis: repaired %d flip prints on %s symbols before any measurement"
              % (basis["flip_prints"], basis["symbols_with_a_flip"]), flush=True)
    # r1178: the world this sheet priced, not just the rule it applied. The card and the
    # ledger print the same digest when -- and only when -- all three priced one panel.
    basis["panel_digest"] = AE.panel_digest(close, openp, amt)
    score = F.build_score(close[cols], amt[cols], feats)
    stale = staleness_stats(score, close[cols])
    print("staleness: %d/%d picks (%.1f%%) priced before the decision bar | panel live on "
          "last bar %d/%d symbols | worst gap %dd"
          % (stale["stale_picks"], stale["picks"], 100.0 * (stale["stale_share"] or 0.0),
             stale["symbols_with_value_on_last_bar"], stale["symbols_total"],
             stale["worst_stale_gap_days"]), flush=True)
    # a second, independent staleness face: the one above is between symbols inside the
    # panel, this one is between the panel and the official calendar (r1287).
    feed = live_feed_status(close.index[-1])
    print("feed: %s | ticket bar %s vs official %s | lag %s day(s)"
          % (feed["status"], feed["ticket_bar"], feed["expected_bar"],
             "-" if feed["lag_days"] is None else feed["lag_days"]), flush=True)
    if fresh_gate:
        # only instruments that actually printed a close on the decision bar are eligible
        score = score.where(close[cols].notna())
        print("fresh gate ON: decisions restricted to symbols with a live bar", flush=True)
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        print("FATAL: no 510300 column on the panel")
        return 2
    mkt = close[mkt_col]

    ser, turnover, gapfill = F.run_next_open(close[cols], openp[cols], amt[cols], feats,
                                             REBAL, n_hold=N_HOLD, cost=F.COST, score=score)
    idx = ser.index.intersection(mkt.index)
    rp, rm = BT.rets(ser.reindex(idx)), BT.rets(mkt.reindex(idx))

    sched = k_schedule(rp, rm, beta)
    k_ser = in_force(sched, idx)
    rates = BW.load_repo_rates()
    cash_rf, cash_missing = BW.repo_daily_cash(idx, rates)
    cash_rf = cash_rf.reindex(idx).fillna(0.0)

    strat, bench, kk = BT.apply_overlay(rp, rm, sched, 0.0, COST_BP, rf=cash_rf)
    if strat is None:
        print("FATAL: overlay produced no live window (not enough history for beta)")
        return 2

    start = pd.Timestamp(inception)
    slip = strat[strat.index >= start]
    blip = bench[bench.index >= start]
    # the overlay only lives where a beta estimate existed, so the forward ledger must
    # start there too -- accruing the warm-up at k=1 would drift off the engine NAV.
    live_k = k_ser.dropna()
    if len(live_k):
        slip = slip[slip.index >= live_k.index[0]]
        blip = blip[blip.index >= live_k.index[0]]

    state = _load_state(inception, beta)
    state["beta_target"] = float(beta)
    # r1483: the account may not stand on a bar the panel stopped carrying (see
    # withdraw_unsupported_bars) -- a stale state bar silently parks the whole chain.
    state, _withdrawn, _wd_info = withdraw_unsupported_bars(state, idx)
    if _withdrawn:
        print("ledger withdrew %d bar(s) the panel no longer carries (%s); rewound to %s"
              % (len(_withdrawn), ", ".join(r["date"] for r in _withdrawn),
                 _wd_info.get("rewound_to")), flush=True)
    dec_dates = {d for d, _, _ in sched}
    rows_in = [d for d in slip.index if state.get("last_bar") is None or
               d > pd.Timestamp(state["last_bar"])]
    merged = []
    if rows_in:
        prev = 1.0 if state.get("last_bar") is None else float(state.get("nav", 1.0))
        last_k = None if state.get("last_k") is None else float(state["last_k"])
        for d in rows_in:
            k_d = float(k_ser.loc[d]) if np.isfinite(k_ser.loc[d]) else (last_k if last_k is not None else 1.0)
            cost = 0.0 if last_k is None else abs(k_d - last_k) * COST_BP / 10000.0
            r = float(rp.loc[d]) * k_d + (1.0 - k_d) * float(cash_rf.loc[d]) - cost
            prev *= (1.0 + r)
            last_k = k_d
            merged.append({"date": str(d.date()), "nav": round(prev, 8), "ret": round(r, 8),
                           "k": round(k_d, 6), "k_cost": round(cost, 8),
                           "rf": round(float(cash_rf.loc[d]), 8),
                           "decision": str(d.date()) if d in dec_dates else ""})
        state.update({"nav": prev, "last_k": last_k, "last_bar": str(rows_in[-1].date()),
                      "rows": int(state.get("rows", 0)) + len(merged)})
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(os.path.join(OUT_DIR, "ledger.jsonl"), "a", encoding="utf-8") as f:
            for r in merged:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # r1489: a bar that came back after being withdrawn must be the panel's arithmetic, not
    # the copy that was cut. Recomputed here, after the accrual, so the check sees the very
    # rows this run wrote (and catches a row restored by anything else, too).
    _ri = reinstatement_check(rp, cash_rf, k_ser)
    if _ri:
        print("reinstatement: %d withdrawn bar(s) back in the ledger | rewritten=%s | "
              "identical to a fresh re-derivation=%s"
              % (_ri["n_reinstated"], _ri["rewritten"] or "none",
                 _ri["verbatim_identical"] or "none"), flush=True)
        if _ri["rewritten"]:
            tail = _read_jsonl(os.path.join(OUT_DIR, "ledger.jsonl"))
            if tail:
                state.update({"nav": float(tail[-1]["nav"]),
                              "last_k": float(tail[-1]["k"]),
                              "last_bar": str(tail[-1]["date"]), "rows": len(tail)})

    # cross-check: the incremental ledger must reproduce the engine NAV at the same date.
    # The ledger's base 1.0 sits the bar *before* the first accrued bar, while the engine
    # slice's first point already carries that bar's return -- strip it before comparing.
    drift = None
    if len(rows_in) and len(slip) > 1:
        f0 = slip.index[0]
        r0 = (float(k_ser.loc[f0]) * float(rp.loc[f0])
              + (1.0 - float(k_ser.loc[f0])) * float(cash_rf.loc[f0]))
        my_norm = float(state["nav"]) / (1.0 + r0)
        eng = float(slip.loc[rows_in[-1]]) / float(slip.iloc[0])
        drift = round(my_norm - eng, 10)

    asof = str(slip.index[-1].date())
    # ---- rank on the engine's last DECISION bar, never on the panel's last bar.
    # `run_next_open` re-decides only every REBAL bars, so ranking `slip.index[-1]` hands an
    # operator a ticket for a book the engine does not hold. At cutoff 2026-10-23 this
    # ticket listed the 10-23 top-5 while the book in force (and the production card, and
    # the forward ledger) had been decided 2026-10-14 -- disjoint sets, so following the
    # ticket would have traded five names the book never owned.
    grid_dates = [d for d in close.index if d >= pd.Timestamp("2020-01-01")]
    dec_bar = grid_dates[(len(grid_dates) - 1) // REBAL * REBAL] if grid_dates else None
    k_engine = state.get("last_k")
    if k_engine is None:
        k_engine = 1.0
    # r1471: the size this sheet orders comes from the executed account, not from the
    # engine's own ledger. Falls back to the rule's k only when the account is absent,
    # unreadable or from another bar -- and says so on the page (never a silent fallback).
    # r1476: an account row written BY THIS BAR's own sheet is an outcome, not an input.
    base = executed_base(asof)
    _fl = _json_face(PERMISSION_FACE) or {}
    _sz = sizing_level(base, asof, k_engine, floor=_fl.get("permitted_k"))
    base["sizing"] = _sz
    k_now = float(_sz["k"])
    print("base: %s | account k=%s vs rule k=%.6f -> ordering k=%.6f (%s)"
          % (base.get("status"),
             "n/a" if base.get("k_executed") is None else "%.6f" % base["k_executed"],
             float(k_engine), float(k_now), _sz["source"]), flush=True)
    cls_map = dict(zip(close.columns, classes))
    # r1229: the weights come from the decision bar (above), the PRICES come from the bar
    # this sheet says it is priced on. Both arms are kept so the difference is measured
    # instead of asserted -- `legacy` is what this sheet printed before the fix.
    ticket = build_ticket(score.loc[dec_bar], close.loc[asof],
                          k_now, nav, classes=cls_map,
                          k_rule=k_engine) if dec_bar is not None else None
    legacy = build_ticket(score.loc[dec_bar], close.loc[dec_bar],
                          k_now, nav, classes=cls_map,
                          k_rule=k_engine) if dec_bar is not None else None
    if ticket is None:
        print("FATAL: no decision bar on the grid -- panel too short")
        return 2
    # r1241: a bar the panel barely covers is not a bar. On 2026-11-02 the shared panel
    # carried 5 closes out of 1613 (the five-member leg advanced, the wide panel's owner
    # had been silent for ~57h), so this ticket priced --  nothing -- and published
    # "book 0 / cash 1,000,000" with every order row unpriced while its weights still
    # summed to k. Publishing that is worse than publishing nothing: the desk would read
    # a fully-cashed book. Refuse the sheet, say why, and keep the last priced one.
    _unpriced = [r["symbol"] for r in ticket["order"] if r.get("price") is None]
    _cov = int(close.loc[asof].notna().sum())
    if _cov and len(_unpriced) == len(ticket["order"]):
        print("FATAL: bar %s covers only %d of %d names on the panel -- every pick is "
              "unpriced, so this sheet would read 'book 0 / all cash'. Refusing to write."
              % (asof, _cov, len(close.columns)))
        return 2
    rp_block = reprice_block(legacy, ticket, dec_bar, asof)
    print("reprice: %s -- %s" % (rp_block.get("verdict"), rp_block.get("sentence")), flush=True)
    ticket_picks = [r["symbol"] for r in ticket["order"]]
    cb = card_book()
    agreement = None
    if cb:
        agreement = {"card_decided_at": cb["decided_at"],
                     "ticket_book_decided_at": str(dec_bar.date()),
                     "same_decision_bar": cb["decided_at"] == str(dec_bar.date()),
                     "ticket_is_prefix_of_card": cb["symbols"][:len(ticket_picks)] == ticket_picks,
                     "card_names": len(cb["symbols"]),
                     # the priced bar is the second half of the agreement: two faces can
                     # share a decision bar and still be built off different panel endings,
                     # and a card refreshed before a grid decision keeps describing the
                     # PREVIOUS book (r1290: the card sat at 2026-10-23/stale_feed while
                     # this ticket was already 2026-10-26/current, both calling themselves
                     # the production book, neither saying a word about the other).
                     "card_priced_bar": cb.get("priced_bar"),
                     "ticket_priced_bar": asof,
                     "same_priced_bar": bool(cb.get("priced_bar")) and cb.get("priced_bar") == asof,
                     "card_feed_status": cb.get("feed_status")}
        print("card agreement: same decision bar=%s | ticket is %d-name prefix of the card's "
              "%d-name book=%s | same priced bar=%s (card %s vs ticket %s)"
              % (agreement["same_decision_bar"], len(ticket_picks),
                 agreement["card_names"], agreement["ticket_is_prefix_of_card"],
                 agreement["same_priced_bar"], cb.get("priced_bar"), asof), flush=True)
    mk = metrics(slip, blip)
    wd = width_disclosure()
    ruler = live_width_ruler(asof=asof, card_n=(wd or {}).get("card_names"))
    # r1184: a width without its license is a config, not a measurement. Quote the family
    # verdict here too (same reader as the card), so the sheet an operator holds says
    # whether the arm family that picked this name count priced one panel.
    fam = family_coherence()
    _priced_faces = priced_face_check((agreement or {}).get("card_priced_bar"), asof)
    carry = carry_split(beta)
    # r1172: five tickers are not five bets. The face that measures how many independent
    # directions the sleeve spans is quoted HERE, verbatim, so the operator reading this
    # order sees the concentration next to the weights instead of counting tickers (r1108
    # 有产无读). Absent or unreadable -> the ticket says so, never a silent pass.
    bets = read_bets_face()
    if bets.get("status") == "ok" and bets.get("sentence"):
        bets_line = bets["sentence"]
        if bets.get("evidence_cutoff") and bets["evidence_cutoff"] != asof:
            bets_line += " (measured on the %s bar)" % bets["evidence_cutoff"]
    else:
        bets_line = ("how many independent bets the sleeve holds is unpublished (%s); "
                     "run scripts/etf_book_bets_face.py run" % (bets.get("status") or "absent"))
    # r1190 / E298: five names are not five sources of RETURN either. The concentration face
    # splits the book's own P&L by symbol and re-prices it without the top names and without
    # their whole sleeve; quoting it here puts "whose CAGR is this" beside the weights instead
    # of one document away (r1108 有产无读). Unreadable -> the ticket says so, never a pass.
    conc = read_concentration()
    if conc.get("status") == "ok" and conc.get("sentence"):
        conc_line = conc["sentence"]
        if conc.get("evidence_cutoff") and conc["evidence_cutoff"] != asof:
            conc_line += " (measured on the %s bar)" % conc["evidence_cutoff"]
    else:
        conc_line = ("where this book's return actually comes from is unpublished (%s); "
                     "run scripts/etf_book_concentration.py run" % (conc.get("status") or "absent"))
    _perm = permission_block(ticket, _permission_receipt(), _json_face(RULERS_FACE))
    # r1478: the band r1477 pinned is now on the sheet an operator opens -- advisory only.
    _band = band_block(k_now, asof, _json_face(SIZING_PREREG_FACE), _perm,
                       _json_face(RULERS_FACE))
    payload = {"evidence_cutoff": asof, "beta_target": float(beta),
               "permission": _perm,
               "size_band": _band,
               "inception": str(slip.index[0].date()) if len(slip) else inception,
               "rebal": REBAL, "n_hold": N_HOLD, "cost_bp_per_side": COST_BP,
               "fresh_gate": bool(fresh_gate), "staleness": stale,
               "feed_status": feed,
               "k_now": round(float(k_now), 6),
               "k_rule": round(float(k_engine), 6),
               # r1478: the receipt a reader actually opens (this file) must name the book
               # its k came from, same as latest.json. Two faces, one writer: a downstream
               # face reading the ticket may not have to guess, and it may not re-derive.
               "k_rule_capped_by_floor": round(float(_sz["k"]), 6),
               "sizing_source": _sz.get("source"),
               "sizing_reason": _sz.get("reason"),
               "base_bar": _sz.get("account_bar"),
               "as_of": asof,
               "base_k_executed": _sz.get("k_executed"),
               "base": base,
               "book_decided_at": str(dec_bar.date()),
               "card_agreement": agreement,
               "next_decision_bars": _next_decision(close.index, slip.index[-1]),
               "ticket": ticket, "metrics": mk, "reprice": rp_block,
               "book_leg": {"turnover_per_rebal": round(float(turnover), 4),
                            "open_gapfill": int(gapfill)},
               "cash_leg": {"source": "data/repo_daily/GC001.csv",
                            "mean_accrual_ann_pct": round(float(cash_rf.mean() * 252.0) * 100, 3),
                            "accrual_window": accrual_window(idx),
                            "missing_bar_steps": int(cash_missing),
                            "money": cash_money(
                                (ticket or {}).get("cash_amount"), rates, asof,
                                accrual_pct=float(cash_rf.mean() * 252.0) * 100.0)},
               "ledger": {"bars": int(state.get("rows", 0)), "nav": round(float(state["nav"]), 8),
                          "rows_added": len(merged), "engine_naive_vs_ledger": drift,
                          "withdrawn_now": [r["date"] for r in _withdrawn],
                          "withdrawal_note": withdrawals_line(),
                          "reinstatements": _ri,
                          # r1490: read from the ledger rows, not from this run's
                          # reinstatements.json -- a restatement three runs old must still
                          # be on the sheet an operator opens today.
                          "reinstated_history": reinstated_history()},
               "entry_gate": entry_gate_support(),
               "swap_trigger": _json_face(SWAP_FACE),
               "swap_stack": _json_face(SWAP_STACK_FACE),
               "positions": _json_face(POSITIONS_FACE),
               "width_disclosure": wd,
               "live_width_ruler": ruler,
               "price_basis": basis,
               "family_coherence": fam,
               "priced_faces": _priced_faces,
               "carry_split": carry,
               "restatements": _ledger_restatements(),
               "bets": bets,
               "concentration": conc,
               "caveats": ["survivorship: on-disk panel holds ETFs that still exist",
                           "ticket prices are closes; no impact cost, no limit-move guard",
                           "GC001 single tenor, rolling assumed cost-free",
                           "k revised every %d bars so delivered beta still wanders" % REBAL,
                           bets_line,
                           conc_line,
                           "exploratory: no preregistration, no verdict, no ledger booking",
                           ("sizing base: executed account %s (k=%.6f) -- the rule alone "
                            "would order k=%.6f" % (base.get("bar"), k_now, float(k_engine)))
                           if _sz.get("source") == "executed" else
                           ("sizing base: the rule's k=%.6f -- the executed account for %s "
                            "is this sheet's own outcome (k=%.6f), so it cannot size it"
                            % (float(k_engine),
                               _sz.get("account_bar"),
                               float(_sz.get("k_executed") or 0.0)))
                           if _sz.get("source") == "rule_same_bar_outcome" else
                           ("sizing base: the executed account is %s, so this sheet sizes "
                            "off the rule's k=%.6f -- the account it describes is not the "
                            "account the desk holds" % (base.get("status"), float(k_engine)))]
                          + (["this ticket is the %d-name aggressive end of the book; the "
                              "production card runs %d names -- see width_disclosure"
                              % (N_HOLD, wd["card_names"])] if wd else
                             ["width disclosure unavailable: run "
                              "scripts/etf_book_width_audit.py run to price the %d-name ticket "
                              "against the production card" % N_HOLD])
                          + ([] if ruler["state"] == "inside_disagreement" else
                             ["live width ruler %s: %s" % (ruler["state"], ruler["detail"])])}

    _write("state.json", state)
    _write("TICKET-%s.json" % asof, payload)
    _write("latest.json", {"as_of": asof, "file": "TICKET-%s.json" % asof,
                           "beta_target": float(beta), "k_now": round(float(k_now), 6),
                           "k_rule": round(float(k_engine), 6),
                           "k_rule_capped_by_floor": round(float(_sz["k"]), 6),
                           "sizing_source": _sz.get("source"),
                           "sizing_reason": _sz.get("reason"),
                           "base_status": base.get("status"),
                           "base_bar": _sz.get("account_bar"),
                           "base_k_executed": _sz.get("k_executed")})
    with open(os.path.join(OUT_DIR, "ORDER-%s.md" % asof), "w", encoding="utf-8") as f:
        f.write(card(ticket, mk, sched, asof, beta,
                     {"inception": payload["inception"], "stale": stale, "width": wd,
                      "feed": feed, "agreement": agreement, "ruler": ruler,
                      "carry": carry, "restatements": payload["restatements"],
                      "withdrawals": payload["ledger"]["withdrawal_note"],
                      "reinstatements": payload["ledger"]["reinstatements"],
                      "reinstated_history": payload["ledger"]["reinstated_history"],
                      "cash_money": payload["cash_leg"]["money"],
                      "entry_gate": payload["entry_gate"],
                      "swap_trigger": payload["swap_trigger"],
                      "swap_stack": payload["swap_stack"],
                      "positions": payload["positions"],
                      "base": payload["base"],
                      "permission": payload["permission"],
                      "size_band": payload["size_band"],
                      "bets_line": bets_line,
                      "conc_line": conc_line,
                      "family_coherence": fam,
                      "priced_faces": _priced_faces,
                      "price_basis": payload["price_basis"],
                      "reprice": rp_block}))

    print("as_of=%s beta=%.2f k=%.6f (rule k=%.6f, base %s) nav=%.4f rows+=%d drift=%s"
          % (asof, beta, k_now, float(k_engine), base.get("status"), state["nav"],
             len(merged), drift))
    if ticket:
        print("ticket: book %.0f%% cash %.0f%% | %s"
              % (ticket["book_weight"] * 100, ticket["cash_weight"] * 100,
                 ", ".join("%s %.1f%%" % (r["symbol"], r["weight"] * 100) for r in ticket["order"])))
    if mk.get("book") and mk.get("same_beta_benchmark"):
        print("book CAGR %.2f%% vs same-beta %.2f%% | excess %+.2fpp"
              % (mk["book"]["cagr"] * 100, mk["same_beta_benchmark"]["cagr"] * 100,
                 mk.get("excess_pp", float("nan"))))
    if wd:
        print("width: %d names here vs %d on the card -> %+.2fpp/yr CAGR, %+.3f Sharpe, "
              "%+.2fpp maxDD (audit cutoff %s)"
              % (wd["ticket_names"], wd["card_names"], wd["delta_ticket_minus_card"]["cagr_pp"],
                 wd["delta_ticket_minus_card"]["sharpe"],
                 wd["delta_ticket_minus_card"]["maxdd_pp"], wd["evidence_cutoff"]))
    else:
        print("width: disclosure unavailable (width audit or card width missing)")
    if carry:
        print("carry split: headline %.2f%% = cash %.2fpp (%.1f%% of it) | zero-cash %.2f%% | "
              "flat-today %.2f%%"
              % (carry["observed_pct"], carry["carry_pp"], carry["carry_share_pct"],
                 carry["zero_pct"], carry["flat_today_pct"]))
    else:
        print("carry split: unavailable -- the sheet says the headline is not decomposed")
    _cm = (payload.get("cash_leg") or {}).get("money") or {}
    if _cm.get("verdict") and _cm["verdict"] != "CANNOT_PRICE":
        print("cash money: %s %.2f%% -> %s CNY/yr | mean %.2f%% -> %s CNY/yr | %s"
              % (_cm["spot"]["date"], _cm["spot"]["pct"],
                 format(int(_cm["spot"]["annual_cny"]), ","),
                 _cm["mean_tail"]["pct"], format(int(_cm["mean_tail"]["annual_cny"]), ","),
                 _cm["verdict"]))
    else:
        print("cash money: %s" % (_cm.get("sentence") or "unreadable"))
    if _band.get("status") == "ok":
        print("size band: %s | drift %s pp | ticket gap %s pp (inside %.2f, warn %.2f)%s"
              % (_band["verdict"],
                 "-" if _band["drift_pp"] is None else "%+.3f" % _band["drift_pp"],
                 "-" if _band["ticket_gap_pp"] is None else "%+.3f" % _band["ticket_gap_pp"],
                 _band["band"]["inside_pp"], _band["band"]["warn_pp"],
                 "" if not _band.get("receipt")
                 else " | re-issue touches %s faces" % (_band["receipt"].get("n")
                                                        if _band["receipt"].get("status") == "ok"
                                                        else "?")))
    else:
        print("size band: %s" % _band.get("sentence"))
    print("wrote", os.path.join(OUT_DIR, "TICKET-%s.json" % asof))
    return 0


CARD_DIR = os.path.join(PATHS.results_dir, "etf_book_production")
AUDIT_PATH = os.path.join(PATHS.results_dir, "etf_book_width_audit.json")
RULER_PATH = os.path.join(PATHS.results_dir, "etf_book_live_width_ruler.json")
RULER_STALE_DAYS = 10


def card_width(card_dir=None):
    """Name count the production card is actually running, read off its own artefact.

    Hardcoding 12 here would rot the moment the card's config changes; the pointer
    chain (latest.json -> PRODUCTION-<asof>.json) is the only place that knows.
    """
    d = card_dir or CARD_DIR
    try:
        with open(os.path.join(d, "latest.json"), encoding="utf-8") as f:
            doc = json.load(f)
        # latest.json is either a pointer to the dated card or the card itself
        if doc.get("file"):
            with open(os.path.join(d, doc["file"]), encoding="utf-8") as f:
                doc = json.load(f)
        n = (doc.get("config") or {}).get("n_hold")
        return int(n) if n else None
    except Exception:
        return None


def card_book(card_dir=None):
    """(decided_at, ordered symbols) of the book the production card is holding.

    Read off the card's own artefact -- the same pointer chain as card_width. Used to
    assert the ticket and the card describe one book: after r1277 both rank on the same
    decision bar, so the ticket's N names must be a prefix of the card's list.
    """
    d = card_dir or CARD_DIR
    try:
        with open(os.path.join(d, "latest.json"), encoding="utf-8") as f:
            doc = json.load(f)
        if doc.get("file"):
            with open(os.path.join(d, doc["file"]), encoding="utf-8") as f:
                doc = json.load(f)
        sh = doc.get("sheet") or {}
        return {"decided_at": sh.get("book_decided_at") or sh.get("last_decision_bar"),
                "symbols": [l.get("symbol") for l in (sh.get("legs") or [])],
                "scale": sh.get("risk_scale"),
                # the bar the card was PRICED on, not just the bar its book was decided
                # on: both faces slice the same panel, but only this field says WHICH day
                # the numbers under it belong to. Measured r1290: on a non-grid day the
                # book is identical (vol overlay sizes at the decision bar, not daily) and
                # only the feed line moves -- but a card refreshed before a grid decision
                # and a ticket refreshed after it describe two different books, and
                # nothing in either face would have said so.
                "priced_bar": sh.get("as_of_bar"),
                "feed_status": (doc.get("feed_status") or {}).get("status")}
    except Exception:
        return None


# The ticket sizes through the fixed beta overlay, the card through an 8% vol target.
# That is not a detail: the audit's width table now carries BOTH rules (r1291), and a
# lookup keyed on the name count alone silently returns whichever arm was written last
# (the vol arm) -- i.e. it would print vol-rule numbers under the "this ticket" label.
TICKET_RULE = "beta"


def card_rule(card_dir=None):
    """Leverage rule the card runs, read off its own config (vol target present -> vol)."""
    d = card_dir or CARD_DIR
    try:
        with open(os.path.join(d, "latest.json"), encoding="utf-8") as f:
            doc = json.load(f)
        if doc.get("file"):
            with open(os.path.join(d, doc["file"]), encoding="utf-8") as f:
                doc = json.load(f)
        cfg = doc.get("config") or {}
        return "vol" if cfg.get("vol_target") else "beta"
    except Exception:
        return None


# ------------------------------------------------------------------ card-config ticket
# The card, the forward ledger and this ticket are three faces of one book only if the
# ticket is issued FROM the card instead of re-ranking the panel at its own width. Until
# r1333 the executable ticket was a 5-name beta-overlay book while the card and the
# ledger both ran 12 names at an 8% vol target -- two published books, one operator.
def _read_card(card_dir=None):
    """The card document itself, pointer chain resolved. None when the face is absent."""
    d = card_dir or CARD_DIR
    try:
        with open(os.path.join(d, "latest.json"), encoding="utf-8") as f:
            doc = json.load(f)
        if doc.get("file"):
            with open(os.path.join(d, doc["file"]), encoding="utf-8") as f:
                doc = json.load(f)
        return doc
    except Exception:
        return None


LEDGER_PATH_DEFAULT = os.path.join(PATHS.results_dir, "etf_book_forward", "LEDGER.json")


def _ledger_book(ledger_path=None):
    """Third face: what the forward ledger is actually holding and on what bar."""
    p = ledger_path or LEDGER_PATH_DEFAULT
    try:
        with open(p, encoding="utf-8") as f:
            led = json.load(f)
    except Exception:
        return None
    bif = led.get("book_in_force") or {}
    bars = led.get("bars") or []
    last = bars[-1] if bars else {}
    return {"config": led.get("config") or {}, "names": list(bif.get("names") or []),
            "scale": bif.get("scale"), "book_bar": bif.get("bar"),
            "last_bar": last.get("bar"), "last_nav": last.get("nav"),
            "status": led.get("status"), "source": p}


def _ledger_restatements(ledger_path=None):
    """Bars the ledger restated AFTER they settled -- a history change nobody was told about.

    The forward ledger is allowed to move a mark once, for a bar that was published while
    its panel was still filling (see etf_book_forward.restate_provisional): it keeps both
    values, the delta and the run that did it. That record only helped whoever opened
    LEDGER.json. The operator holds the ticket, so the ticket has to carry the notice.

    Three states are kept apart on purpose: unreadable, readable-and-empty, readable with
    notices. Collapsing the first into the second would let a missing ledger read as
    "your history is clean".
    """
    p = ledger_path or LEDGER_PATH_DEFAULT
    out = {"path": p, "readable": False, "source": None, "notices": [],
           "bars": [], "bars_published": None}
    try:
        with open(p, encoding="utf-8") as f:
            led = json.load(f)
    except Exception:
        return out
    out["readable"] = True
    bars = led.get("bars") or []
    out["bars_published"] = len(bars)
    lst = led.get("restatements")
    if isinstance(lst, list):
        out["source"] = "restatements"
        for n in lst:
            if not isinstance(n, dict) or not n.get("bar"):
                continue
            out["notices"].append({"bar": n.get("bar"), "ts": n.get("ts"),
                                   "nav_published": n.get("nav_published"),
                                   "nav_settled": n.get("nav_settled"),
                                   "delta": n.get("delta"), "reason": n.get("reason")})
    else:
        # ledgers written before the top-level list existed carry the marks on the bars
        out["source"] = "bars"
        for b in bars:
            if not isinstance(b, dict) or not b.get("restated_at"):
                continue
            pub = b.get("nav_published")
            stl = b.get("nav_settled", b.get("nav"))
            out["notices"].append({
                "bar": b.get("bar"), "ts": b.get("restated_at"),
                "nav_published": pub, "nav_settled": stl,
                "delta": (None if pub is None or stl is None else float(stl) - float(pub)),
                "reason": b.get("restate_reason")})
    out["bars"] = [n["bar"] for n in out["notices"]]
    return out


def _relpath_safe(p, base=None):
    """Relative path for display; a fixture or ledger on another drive is printed absolute."""
    p = str(p or "")
    try:
        return os.path.relpath(p, base or BASE).replace("\\", "/")
    except Exception:
        return p.replace("\\", "/")


def restatement_md(rst, base=None):
    """The notice block: which published bars moved after they settled -- or that none did."""
    base = base or BASE
    if not rst or not rst.get("readable"):
        return ["", "## 历史变更通知：本单引用的历史有没有被改过", "",
                "- **无法核验**：读不到前向账本（%s），所以本单不能回答这个问题 —— "
                "这不是「没有被改述」。"
                % _relpath_safe((rst or {}).get("path") or LEDGER_PATH_DEFAULT, base)]
    notices = rst.get("notices") or []
    if not notices:
        return ["", "## 历史变更通知：本单引用的历史有没有被改过", "",
                "- 已核验：前向账本已发布 %s 根 bar，其中**没有一根在定格之后被改述**（%s）。"
                % (rst.get("bars_published") if rst.get("bars_published") is not None else "?",
                   "账本顶层 restatements 清单为空"
                   if rst.get("source") == "restatements"
                   else "账本无顶层清单，已按每根 bar 的 restated_at 标记逐根核对")]
    L = ["", "## 历史变更通知：本单引用的历史有没有被改过", "",
         "**有 %d 根 bar 在定格之后又被改述**（=历史变了，两个值都留着）：" % len(notices),
         "", "| bar | 当时发布(NAV) | 定格后(NAV) | 差 | 何时 |", "|---|---|---|---|---|"]
    for n in notices:
        pub, stl, dl = n.get("nav_published"), n.get("nav_settled"), n.get("delta")
        L.append("| %s | %s | %s | %s | %s |"
                 % (n.get("bar") or "-",
                    ("%.8f" % float(pub)) if pub is not None else "-",
                    ("%.8f" % float(stl)) if stl is not None else "-",
                    ("%+.2e" % float(dl)) if dl is not None else "-",
                    n.get("ts") or "-"))
    relist = "；".join(sorted({str(n.get("reason") or "未注明") for n in notices}))
    L += ["", "- 读法：被改述的是「当天面板还在补数就先定过的价」，不是有人事后改了历史；"
          "本单引用的行以「定格后」那一列为准。原因：%s。" % relist,
          "- 出处：%s。" % _relpath_safe(rst.get("path") or LEDGER_PATH_DEFAULT, base)]
    return L


def card_config_ticket(card_dir=None, nav=None, ledger_path=None):
    """Broker-followable ticket for the book the production card publishes.

    Weights, names and the risk scale come from the card's own sheet (one source of
    truth); ``nav`` only re-prices the lot counts, it never re-ranks anything. Recomputing
    the lots from price x weight is deliberate: on the card's own capital the result must
    equal the card's published lot counts, and any drift between the two faces shows up as
    ``reprice_mismatch`` instead of being copied silently.
    """
    doc = _read_card(card_dir)
    if not doc:
        return None
    cfg = doc.get("config") or {}
    sh = doc.get("sheet") or {}
    legs = sh.get("legs") or []
    cap = float(sh.get("capital_cny") or cfg.get("capital_cny") or 0.0)
    if not legs or cap <= 0:
        return None
    stated = float(nav) if nav else cap
    rows, spent, mismatch = [], 0.0, []
    for l in legs:
        px = l.get("ref_price")
        w = float(l.get("weight") or 0.0)
        want = stated * w
        lots = shares = amt = None
        if px and float(px) > 0:
            lots = int(want // (float(px) * LOT))
            shares = lots * LOT
            amt = shares * float(px)
            spent += amt
            if (abs(stated - cap) < 1e-6 and l.get("lots_100") is not None
                    and int(l["lots_100"]) != shares):
                # the card's ``lots_100`` field carries the SHARE count rounded to 100
                # (live card: 159501 26600 shares x 2.194 = 58360 actual amount), not a
                # lot count -- comparing against ``lots`` here reads as a 100x mismatch
                mismatch.append({"symbol": l.get("symbol"), "card_shares": l.get("lots_100"),
                                 "ticket_shares": shares})
        rows.append({"symbol": l.get("symbol"), "name": l.get("name"),
                     "class": l.get("class"), "weight": round(w, 6),
                     "price": round(float(px), 4) if px else None,
                     "lots": lots, "shares": shares,
                     "amount": round(amt, 2) if amt is not None else None,
                     "note": "" if lots else "budget below one lot"})
    cash = stated - spent
    names = [r["symbol"] for r in rows]
    led = _ledger_book(ledger_path) or {}
    rst = _ledger_restatements(ledger_path)
    led_cfg = led.get("config") or {}
    card_scale = sh.get("risk_scale")
    recon = {"card_priced_bar": sh.get("as_of_bar"),
             "card_decided_at": sh.get("book_decided_at") or sh.get("last_decision_bar"),
             "card_scale": card_scale, "card_names": names,
             "same_names_as_card": names == [l.get("symbol") for l in legs],
             "ledger_names": led.get("names"),
             "same_names_as_ledger": (names == led["names"]) if led.get("names") else None,
             "ledger_scale": led.get("scale"),
             "same_scale_as_ledger": None,
             "ledger_book_bar": led.get("book_bar"), "ledger_last_bar": led.get("last_bar"),
             "ledger_last_nav": led.get("last_nav"), "ledger_status": led.get("status"),
             "ledger_source": led.get("source"),
             "restatements_readable": rst["readable"],
             "restatements_source": rst["source"],
             "restated_bars": rst["bars"],
             "restatements": rst["notices"],
             "ledger_bars_published": rst["bars_published"],
             "card_cash_weight": sh.get("cash_weight"),
             # r1342 / E230: the card now prints the EXECUTABLE cash row, so the ticket
             # reconciles against that one. A card that predates the fix has no
             # cash_executable_cny and still gets the legacy target-row disclosure.
             "card_cash_amount": sh.get("cash_executable_cny", sh.get("cash_amount_cny")),
             "card_cash_is_executable": sh.get("cash_executable_cny") is not None,
             "card_cash_target_amount": sh.get("cash_amount_cny"),
             "card_config": {k: cfg.get(k) for k in ("n_hold", "vol_target", "rebal",
                                                     "cost_bp_per_side")},
             "ledger_config": {k: led_cfg.get(k) for k in ("n_hold", "vol_target", "rebal",
                                                           "cost_per_side")},
             "same_config_as_ledger": None}
    if card_scale is not None and led.get("scale") is not None:
        # the card publishes the scale at 4 dp while the ledger keeps full precision
        # (0.7008 vs 0.700775) -- compare at the published precision, not bitwise, or
        # two faces of the same book would read as different books every round.
        recon["same_scale_as_ledger"] = (round(float(card_scale), 4)
                                         == round(float(led["scale"]), 4))
        recon["scale_precision"] = "4 dp (the card's published precision)"
    try:
        recon["same_config_as_ledger"] = (
            str(cfg.get("n_hold")) == str(led_cfg.get("n_hold"))
            and abs(float(cfg.get("vol_target") or 0.0)
                    - float(led_cfg.get("vol_target") or 0.0)) < 1e-9)
    except Exception:
        recon["same_config_as_ledger"] = None
    return {"kind": "card_config", "nav": stated, "card_capital": cap,
            "scale": float(card_scale or 0.0), "config": cfg, "order": rows,
            "book_amount": round(spent, 2), "cash_amount": round(cash, 2),
            "book_weight": round(spent / stated, 6), "cash_weight": round(cash / stated, 6),
            "cash_leg": "GC001 (1-day repo, observed close)",
            "underspend_pct": round(100.0 * cash / stated - 100.0 * (1.0 - float(card_scale or 0.0)), 4),
            "reprice_mismatch": mismatch, "priced_bar": sh.get("as_of_bar"),
            "decision": sh.get("decision"),
            "bars_until_next_decision": sh.get("bars_until_next_decision"),
            "feed": doc.get("feed_status") or {}, "recon": recon}


def _verdict(b):
    return "unknown" if b is None else ("一致" if b else "不一致")


def card_config_card(tk, width=None, ruler=None):
    """Markdown for the card-config order, with the three-face reconciliation on it."""
    rc = tk["recon"]
    cfg = tk["config"]
    L = ["# ETF 复合书 · 可执行订单单（%s，卡片配置口径）" % tk["priced_bar"], "",
         "当前活：生产卡片的原样配置——%d 名、每 %d 个交易日网格、%.0f%% 波动目标（只降不升杠杆）、"
         "空仓进 GC001。" % (int(cfg.get("n_hold") or 0), int(cfg.get("rebal") or REBAL),
                           100.0 * float(cfg.get("vol_target") or 0.0)),
         "最近实物：%s（与本文件同刻生成）。"
         % os.path.relpath(os.path.join(OUT_DIR, "TICKET-%s-card.json" % tk["priced_bar"]),
                           BASE).replace("\\", "/"),
         "下个里程碑：该单一是一张可下手的单，卡片/账本/单据三面同书（本文件末节逐项对账）。", ""]
    feed = tk.get("feed") or {}
    L += ["## 数据新鲜度（本单定价用的是哪一天的 bar）",
          "- 官方交易日历期望最新 bar：%s" % (feed.get("expected_bar") or "未知（无日历）"),
          "- 本单定价 bar：%s ｜ 判定：**%s**｜落后 %s 个交易日"
          % (tk["priced_bar"], feed.get("status", "unknown"),
             "?" if feed.get("lag_days") is None else feed.get("lag_days")),
          "- 前向账本最后一行 bar：%s（NAV %.6f，status=%s）"
          % (rc.get("ledger_last_bar") or "未知",
             float(rc.get("ledger_last_nav") or 0.0), rc.get("ledger_status") or "未知"), ""]
    L += restatement_md({"readable": rc.get("restatements_readable"),
                         "path": rc.get("ledger_source"),
                         "source": rc.get("restatements_source"),
                         "notices": rc.get("restatements") or [],
                         "bars_published": rc.get("ledger_bars_published")})
    L += ["## 今日目标（NAV ¥%s）" % format(int(round(tk["nav"])), ","),
          "风险缩放 k=%.3f（书内 %.1f%%、现金 %.1f%%）｜现金腿=%s｜现金 ¥%s"
          % (tk["scale"], tk["book_weight"] * 100, tk["cash_weight"] * 100,
             tk["cash_leg"], format(int(round(tk["cash_amount"])), ",")),
          "",
          "| 代码 | 名称 | 类别 | 权重 | 参考价 | 手数(100股) | 金额 |",
          "|---|---|---|---|---|---|---|"]
    for r in tk["order"]:
        L.append("| %s | %s | %s | %.1f%% | %s | %s | %s |"
                 % (r["symbol"], r.get("name") or "-", r.get("class") or "?",
                    r["weight"] * 100, ("%.3f" % r["price"]) if r["price"] else "-",
                    r["lots"] if r["lots"] is not None else "-",
                    format(int(r["amount"]), ",") if r["amount"] else "-"))
    L += ["", "整手取整后欠投 %+.2f%% NAV（留在现金腿，不重分配）。" % tk["underspend_pct"]]
    if tk.get("bars_until_next_decision") is not None:
        L += ["", "下一个网格决策点：%s 个交易日后（当前决策 bar %s）。"
              % (tk["bars_until_next_decision"], rc.get("card_decided_at") or "-")]
    L += ["", "## 三面是不是同一本书", "",
          "| 面 | 名数 | 杠杆规则 | 风险缩放 | 定价/决策 bar |",
          "|---|---|---|---|---|",
          "| 生产卡片 | %d | %s | %.4f | %s |"
          % (len(rc["card_names"]), "vol %.0f%%" % (100.0 * float(cfg.get("vol_target") or 0.0)),
             float(rc["card_scale"] or 0.0), rc.get("card_priced_bar") or "-"),
          "| 前向账本 | %d | %s | %s | %s（最后行 %s） |"
          % (len(rc.get("ledger_names") or []),
             "vol %.0f%%" % (100.0 * float((rc.get("ledger_config") or {}).get("vol_target") or 0.0)),
             ("%.4f" % float(rc["ledger_scale"])) if rc.get("ledger_scale") is not None else "-",
             rc.get("ledger_book_bar") or "-", rc.get("ledger_last_bar") or "-"),
          "| 本单（可执行） | %d | vol %.0f%% | %.4f | %s |"
          % (len(tk["order"]), 100.0 * float(cfg.get("vol_target") or 0.0), tk["scale"],
             tk["priced_bar"]),
          "",
          "- 名称：本单 vs 卡片 %s｜本单 vs 账本 %s"
          % (_verdict(rc["same_names_as_card"]), _verdict(rc["same_names_as_ledger"])),
          "- 风险缩放：本单 vs 账本 %s（%.4f / %s，按卡片 4 位小数口径比对）"
          % (_verdict(rc["same_scale_as_ledger"]), tk["scale"],
             ("%.4f" % float(rc["ledger_scale"])) if rc.get("ledger_scale") is not None else "-"),
          "- 配置：本单 vs 账本 %s（card %s / ledger %s）"
          % (_verdict(rc["same_config_as_ledger"]),
             rc.get("card_config"), rc.get("ledger_config")),
          "- 卡片重算手数 vs 卡片已发布手数：%d 处不一致%s"
          % (len(tk["reprice_mismatch"]),
             ("（%s）" % tk["reprice_mismatch"][:3]) if tk["reprice_mismatch"] else "")]
    if width:
        d = width["delta_ticket_minus_card"]
        L += ["", "## 与「%d 名 β 覆盖」那张单的关系" % width["ticket_names"],
              "那张单是**另一本书**（%d 名 / %s 覆盖 / 固定 β 目标 %.2f），不是本卡片的宽度变体："
              "两者的差值 (%+.2fpp 年化, %+.3f 夏普) 是同时换了宽度和杠杆规则的对角线。"
              % (width["ticket_names"], width["ticket_rule"], DEFAULT_BETA,
                 -d["cagr_pp"], -d["sharpe"]),
              "同一规则下只换名数的代价：%s。"
              % ("；".join("%s 规则 %+.2fpp" % (r, v["pp"])
                          for r, v in sorted((width.get("width_effect") or {}).items()))
                 or "本窗未取到同规则两宽度格"),
              "出处：%s（cutoff %s）。" % (width["source"], width["evidence_cutoff"])]
    ru = (ruler or {})
    if ru.get("state") == "inside_disagreement" and ru.get("sheet_role") == "measured_card":
        L += ["", "## 另一张单和本单的差（两张面逐相位配对）",
              "本单**就是卡片那一本书**（%d 名 / vol %.0f%%），所以下面这个差不是「本单 vs 卡片」，"
              "而是「%d 名 %s 覆盖那张单 vs 本单」：中位 **%+.2fpp**"
              "（%d 个相位，%s 个往上、%s 个往下，区间 %+.2f ~ %+.2f）；同一档 5→12 名在另一台引擎上"
              "是 **%+.2fpp** —— 两台引擎对这一档的分歧 **%+.2fpp**（方向还相反）。"
              % (len(tk["order"]), 100.0 * float(cfg.get("vol_target") or 0.0),
                 ru["widths"]["ticket"]["live_n_hold"], ru["widths"]["ticket"]["live_rule"],
                 float(ru["gap_pp"]), ru["pairs"], ru.get("positive_phases"),
                 (ru["pairs"] - (ru.get("positive_phases") or 0)) if ru.get("pairs") else "?",
                 float(ru.get("min_pp") or 0.0), float(ru.get("max_pp") or 0.0),
                 float(ru.get("capacity_rung_pp") or 0), float(ru["disagreement_pp"])),
              "- 读法：这个差只有引擎分歧的 **%.1f%%**，所以两张单之间选哪张读不出收益差——"
              "读得出来的是要在哪一档波动预算上：β 覆盖固定杠杆，本单按 8%% 目标只降不升。"
              % (100.0 * (ru.get("share_of_disagreement") or 0.0)),
              _resolution_md(ru),
              "- 出处：%s（cutoff %s，%s 个相位配对）。"
              % (ru["source"], ru["evidence_cutoff"], ru["pairs"])]
    elif ru.get("state") and ru["state"] != "unavailable":
        L += ["", "## 另一张单和本单的差（尺子没给出干净读数）",
              "- 尺子状态：**%s** —— %s" % (ru["state"], ru.get("detail") or ""),
              "- 本单在这把尺子上的身份：%s。"
              % {"measured_card": "卡片面（可读）",
                 "unverified": "**未核实**——尺子量的是旧宽度，本单不能引用它的读数",
                 None: "未声明"}.get(ru.get("sheet_role"), ru.get("sheet_role")),
              "- 出处：%s（cutoff %s）。" % (ru.get("source"), ru.get("evidence_cutoff"))]
    L += ["", "## 诚实面", "",
          "- 探索件：无预注册、无判决、不入成绩账本；本单只是把卡片已经公布的那本书变成可下手的单。"]
    _fcc = (tk.get("family_coherence") if isinstance(tk, dict) else None) or family_coherence()
    if _fcc.get("verdict") == "ONE_WORLD":
        L += ["- **名数的来历**：%d 个宽度臂的判词全部算在同一张面板 `%s`（截至 %s）——本单这个名数是"
              "比出来的宽度，不是拍出来的配置。"
              % (_fcc.get("arms") or 0, ((_fcc.get("panels") or [""])[0] or "?"),
                 _fcc.get("evidence_cutoff"))]
    elif _fcc.get("verdict"):
        L += ["- **名数没被证过**：宽度臂家族已收回自己的判词（%s，%s），所以本单这个名数只是配置，"
              "不是测出来的最优。" % (_fcc["verdict"], _fcc.get("detail") or "无细节")]
    else:
        L += ["- **名数没被证过**：读不到宽度臂家族的面（%s）——这是「没验」，不是「没问题」。"
              % (_fcc.get("detail") or "家族面缺席")]
    gap = None
    if rc.get("card_cash_amount") is not None:
        gap = tk["cash_amount"] - float(rc["card_cash_amount"])
        if abs(gap) >= 1.0:
            L += ["- **卡片现金行是目标口径**：卡片按 权重×资本 印目标金额、现金=(1-缩放)×资本"
                  "（¥%s）；整手取整后真实能花出去的钱比目标少 ¥%s（%.2f%% NAV），"
                  "所以本单的现金腿是 ¥%s。照卡片那行下手，账上实际会多出这 %.2f%% 现金"
                  "——卡片把投入算高了，不是把现金算少了。"
                  % (format(int(round(float(rc["card_cash_amount"]))), ","),
                     format(int(round(gap)), ","), 100.0 * gap / tk["nav"],
                     format(int(round(tk["cash_amount"])), ","), 100.0 * gap / tk["nav"])]
    L += [
          "- 票池=现存 ETF，存在幸存者偏差；票面按卡片定盘 bar 的参考价折算，未计冲击成本与涨跌停。",
          "- GC001 单期限且滚动假设零费；真实现金台应做 1/7/14 天梯队。",
          "- 波动目标是历史估计，只降不升杠杆：标注 8% 的书实测跑到 10%+（见卡片风险列）。"]
    return "\n".join(L) + "\n"


# --------------------------------------------------------- lot granularity (r1334)
LOT_CURVE_GRID = (50_000, 100_000, 200_000, 300_000, 500_000, 750_000,
                  1_000_000, 2_000_000, 3_000_000, 5_000_000, 10_000_000,
                  20_000_000)


def lot_point(legs, capital, scale=None, lot=LOT):
    """What the card's own weights actually buy at one stated capital.

    Whole lots only, buys floor'ed, so the book can only spend LESS than target: a
    card's cash row is ``(1 - k) * capital`` while the cash that lands on the desk is
    ``capital - spent``. The difference is the price of lot granularity, and
    ``max_abs_weight_drift_pp`` is the same thing seen from the book's side -- a leg
    that misses its weight by half a lot is mis-sized, not merely cheap.

    r1342: the production card PRINTS the executable cash (``capital - spent``) now, so
    ``cash_vs_target_cny`` no longer measures a card defect -- it measures the money the
    desk holds beyond the risk scale's own cash slot, most of it the lot residue. Read it
    as "cash above the slot", not "the card is wrong".
    """
    cap = float(capital)
    rows, spent, zero, max_drift, tot_w = [], 0.0, 0, 0.0, 0.0
    for l in legs:
        w = float(l.get("weight") or 0.0)
        px = l.get("ref_price") or l.get("price")
        tot_w += w
        if not px or float(px) <= 0:
            rows.append({"symbol": l.get("symbol"), "weight": round(w, 6), "price": None,
                         "lots": None, "amount": None, "drift_pp": None})
            continue
        lots = int((cap * w) // (float(px) * lot))
        amt = lots * lot * float(px)
        spent += amt
        if lots == 0:
            zero += 1
        drift_pp = 100.0 * (amt / cap - w)
        max_drift = max(max_drift, abs(drift_pp))
        rows.append({"symbol": l.get("symbol"), "weight": round(w, 6),
                     "price": round(float(px), 4), "lots": lots,
                     "amount": round(amt, 2), "drift_pp": round(drift_pp, 4)})
    s = float(scale) if scale is not None else tot_w
    cash = cap - spent
    gap = cash - cap * (1.0 - s)
    return {"capital_cny": round(cap, 2), "scale": round(s, 6),
            "target_book_cny": round(cap * s, 2), "book_amount_cny": round(spent, 2),
            "cash_amount_cny": round(cash, 2), "cash_vs_target_cny": round(gap, 2),
            "underspend_pp_nav": round(100.0 * gap / cap, 4) if cap else None,
            "max_abs_weight_drift_pp": round(max_drift, 4),
            "legs_with_zero_lots": zero, "legs": rows}


def lot_curve(legs, scale=None, grid=LOT_CURVE_GRID, thresholds=(1.0, 0.5)):
    """Sweep the stated capital: the granularity cost is a curve, not one number.

    A single-capital disclosure answers "is today's ticket executable"; the operator's
    real question is "how small may this book be before the ticket stops being the
    book". Both readings are published (cash vs target, and weight drift), because a
    book can be cheap and mis-sized at the same time.
    """
    pts = [lot_point(legs, c, scale) for c in grid]
    drift = [p["max_abs_weight_drift_pp"] for p in pts]

    def _mincap(th):
        for c, d in zip(grid, drift):
            if d <= th:
                return float(c)
        return None

    px_lot, min_w = 0.0, None
    for l in legs:
        px = l.get("ref_price") or l.get("price")
        w = float(l.get("weight") or 0.0)
        if px and float(px) > 0 and w > 0:
            px_lot = max(px_lot, float(px) * LOT)
            min_w = w if min_w is None else min(min_w, w)
    floor = (px_lot / min_w) if min_w else None
    # Each leg can leave at most one lot unspent, so the shortfall is BOUNDED in yuan
    # and does not shrink as the book grows -- only its percentage does. That is why the
    # cash column of this curve is jagged while the weight-drift column is monotone.
    bound = 0.0
    for l in legs:
        px = l.get("ref_price") or l.get("price")
        if px and float(px) > 0:
            bound += float(px) * LOT
    return {"grid": list(grid), "points": pts,
            "monotone_non_increasing": all(b <= a + 1e-9 for a, b in zip(drift, drift[1:])),
            "thresholds": {("%.2fpp" % th): {"min_capital_cny": _mincap(th)}
                           for th in thresholds},
            "shortfall_bound_cny": round(bound, 2),
            "max_observed_shortfall_cny": max(p["cash_vs_target_cny"] for p in pts),
            "one_lot_floor_cny": round(floor, 2) if floor else None}


def lot_curve_md(curve, card_cap=None):
    """The operator's half of the curve: the row about to be traded, plus the edge."""
    L = ["## 资金规模下限（整手取整的实际代价）", ""]
    cur = None
    if card_cap:
        for p in curve["points"]:
            if abs(p["capital_cny"] - float(card_cap)) < 1.0:
                cur = p
                break
    if cur:
        L += ["本单资金 %s 元：目标持仓 %s / 实际买入 %s，现金比卡片行多 %s（%.2f%% NAV），"
              "单腿最大偏离 %.2f%%，买不到一手 %d 腿。"
              % (format(int(round(cur["capital_cny"])), ","),
                 format(int(round(cur["target_book_cny"])), ","),
                 format(int(round(cur["book_amount_cny"])), ","),
                 format(int(round(cur["cash_vs_target_cny"])), ","),
                 cur["underspend_pp_nav"], cur["max_abs_weight_drift_pp"],
                 cur["legs_with_zero_lots"]), ""]
    L += ["| 资金 | 单腿最大偏离 | 买不到一手 | 现金比目标多 |",
          "|---|---|---|---|"]
    for p in curve["points"]:
        L.append("| %s | %.2f%% | %d | %s |"
                 % (format(int(round(p["capital_cny"])), ","),
                    p["max_abs_weight_drift_pp"], p["legs_with_zero_lots"],
                    format(int(round(p["cash_vs_target_cny"])), ",")))
    th = curve["thresholds"]
    a1 = th["1.00pp"]["min_capital_cny"]
    a5 = th["0.50pp"]["min_capital_cny"]
    L += ["",
          "- 单腿偏离 ≤1.00pp 需要资金 ≥ %s；≤0.50pp 需要 ≥ %s。"
          % (format(int(a1), ",") if a1 else "本表内不可达",
             format(int(a5), ",") if a5 else "本表内不可达"),
          "- 至少一腿连一手都买不起的下限 = %s 元（最贵一手 ÷ 最小权重）；这条线以下"
          "「按卡片权重执行」不成立，只能降标的数或换更便宜的腿。"
          % (format(int(curve["one_lot_floor_cny"]), ",")
             if curve.get("one_lot_floor_cny") else "未知"),
          "- 偏离随资金单调不增：%s（取整代价是小资金的税，不是策略的缺陷）。"
          % ("是" if curve["monotone_non_increasing"] else "**否，见上表**"),
          "- 缺口的绝对额不随资金变小：每腿最多剩一手，合计上限 %s 元，本表实测最大 %s 元——"
          "所以这条曲线在现金列是锯齿的（谁离整手更远谁更亏），只有占 NAV 的百分比随资金下降；"
          "换句话说「多留几百块现金」是固定小额开销，与资金规模无关。"
          % (format(int(round(curve["shortfall_bound_cny"])), ",")
             if curve.get("shortfall_bound_cny") else "未知",
             format(int(round(curve.get("max_observed_shortfall_cny") or 0.0)), ","))]
    return L


def run_card(nav=None):
    tk = card_config_ticket(nav=nav)
    if not tk:
        print("card: no production card to issue from (%s)" % CARD_DIR)
        return 2
    asof = tk["priced_bar"] or "unknown"
    doc = {"kind": tk["kind"], "asof_bar": asof, "capital_cny": tk["nav"],
           "card_capital_cny": tk["card_capital"], "scale": tk["scale"],
           "config": tk["config"], "order": tk["order"],
           "book_amount": tk["book_amount"], "cash_amount": tk["cash_amount"],
           "book_weight": tk["book_weight"], "cash_weight": tk["cash_weight"],
           "cash_leg": tk["cash_leg"], "underspend_pct": tk["underspend_pct"],
           "reprice_mismatch": tk["reprice_mismatch"], "recon": tk["recon"],
           "decision": tk.get("decision"),
           "bars_until_next_decision": tk.get("bars_until_next_decision"),
           "feed": tk.get("feed"),
           "caveats": ["exploratory: no prereg, no verdict, not in the scorecard",
                       "survivorship in the ETF pool; reference prices only, no impact cost",
                       "cash leg is GC001 single tenor, rolls at zero fee"]}
    wd = width_disclosure()
    curve = lot_curve(tk["order"], scale=tk["scale"])
    curve["asof_bar"] = asof
    curve["scale_of_capital_cny"] = tk["nav"]
    _write("LOTCURVE-%s-card.json" % asof, curve)
    # r1357: the ruler reaches the card sheet too -- both documents a reader can hold must
    # answer "what did the other sheet measure", and the paired gap is between the faces,
    # so this sheet says which face it is on that ruler rather than borrowing the gap.
    ruler = live_width_ruler(asof=tk["priced_bar"], card_n=len(tk["order"]), sheet="card")
    doc["live_width_ruler"] = ruler
    # r1184: this sheet IS the card's width, so it is the face that most needs to say
    # whether the arm family licensing that width priced one panel.
    doc["family_coherence"] = family_coherence()
    _write("TICKET-%s-card.json" % asof, doc)
    md = "\n".join([card_config_card(tk, wd, ruler).rstrip(),
                    "\n".join(lot_curve_md(curve, tk["nav"])).rstrip(),
                    ""])
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "ORDER-%s-card.md" % asof), "w", encoding="utf-8") as f:
        f.write(md)
    rc = tk["recon"]
    print("card-config ticket: %s | NAV %s | %d names | k=%.3f | cash %.1f%%"
          % (asof, format(int(round(tk["nav"])), ","), len(tk["order"]), tk["scale"],
             tk["cash_weight"] * 100))
    print("three faces: names card=%s ledger=%s | scale vs ledger=%s | config vs ledger=%s"
          % (_verdict(rc["same_names_as_card"]), _verdict(rc["same_names_as_ledger"]),
             _verdict(rc["same_scale_as_ledger"]), _verdict(rc["same_config_as_ledger"])))
    print("card lot recount mismatches: %d" % len(tk["reprice_mismatch"]))
    own = [p for p in curve["points"] if abs(p["capital_cny"] - tk["nav"]) < 1.0]
    if own:
        print("lot curve at this capital: drift %.2f%% max | %d legs below one lot | "
              "cash vs risk-scale slot +%s" % (own[0]["max_abs_weight_drift_pp"],
                                        own[0]["legs_with_zero_lots"],
                                        format(int(round(own[0]["cash_vs_target_cny"])), ",")))
    print("wrote", os.path.join(OUT_DIR, "ORDER-%s-card.md" % asof))
    return 0


def width_disclosure(card_n=None, audit_path=None, card_dir=None):
    """What this ticket's width costs against the card's, from the audit face.

    Both faces are published as "the production book", so an operator following this
    ticket buys N names under the beta overlay while the card's row describes its own
    width under an 8% vol target. ``scripts/etf_book_width_audit.py`` measures the full
    width x rule grid; this reads it back rather than re-running it.

    Two numbers matter and they are not interchangeable (r1291):
      * ``width_effect`` -- same rule, two widths: how much the name count alone costs.
        Under the beta overlay it is -1.5pp, under the vol target +0.2pp.
      * ``delta_ticket_minus_card`` -- the two *published* faces: they differ in BOTH
        width and rule, so this is a diagonal of that grid, not a width effect.

    Missing audit (or a width/rule missing from it) returns None and the caller says so
    out loud -- silence would read as "no difference".
    """
    p = audit_path or AUDIT_PATH
    n_card = card_n if card_n is not None else card_width()
    c_rule = card_rule(card_dir)
    try:
        with open(p, encoding="utf-8") as f:
            audit = json.load(f)
    except Exception:
        return None
    # keyed by (names, rule): rows written before the rule column existed are the beta arm.
    cells = {}
    for r in (audit.get("rows") or []):
        cells[(int(r["n_hold"]), r.get("rule") or "beta")] = r
    if c_rule is None:
        # A card artefact we cannot read is not a licence to assume its rule: use the
        # only arm present at its width, and say which one we ended up comparing.
        cand = [rule for (_n, rule) in cells if n_card and _n == int(n_card)]
        if len(cand) != 1:
            return None
        c_rule = cand[0]
    a = cells.get((int(N_HOLD), TICKET_RULE))
    b = cells.get((int(n_card), c_rule)) if n_card else None
    if not a or not b:
        return None

    def face(r):
        bk = r.get("book") or {}
        return {"cagr": bk.get("cagr"), "sharpe": bk.get("sharpe"), "maxdd": bk.get("maxdd"),
                "vol": bk.get("vol")}

    ta, tb = face(a), face(b)
    sq = audit.get("square") or {}
    # same-rule width effect, per rule, straight off the audit's own grid.
    # sign = the WIDER book minus this ticket's width (audit's own width_effect_pp
    # convention), so beta reads -1.5pp and vol +0.2pp at 12 vs 5 names.
    width_effect = {}
    for rule in {TICKET_RULE, c_rule}:
        lo = cells.get((int(N_HOLD), rule))
        hi = cells.get((int(n_card), rule)) if n_card else None
        if lo and hi:
            width_effect[rule] = {
                "ticket_width_cagr": (lo.get("book") or {}).get("cagr"),
                "card_width_cagr": (hi.get("book") or {}).get("cagr"),
                "pp": round((((hi.get("book") or {}).get("cagr") or 0.0)
                             - ((lo.get("book") or {}).get("cagr") or 0.0)) * 100, 2)}
    try:
        src = os.path.relpath(p, BASE).replace("\\", "/")
    except ValueError:            # audit path off the repo volume (selftest fixtures)
        src = p.replace("\\", "/")
    return {"ticket_names": int(N_HOLD), "card_names": int(n_card),
            "ticket_rule": TICKET_RULE, "card_rule": c_rule,
            "ticket": ta, "card": tb,
            "width_effect": width_effect,
            "rules_differ": TICKET_RULE != c_rule,
            "delta_ticket_minus_card": {
                "cagr_pp": round((ta["cagr"] - tb["cagr"]) * 100, 2),
                "sharpe": round(ta["sharpe"] - tb["sharpe"], 3),
                "maxdd_pp": round((ta["maxdd"] - tb["maxdd"]) * 100, 2),
                "vol_pp": round(((ta.get("vol") or 0.0) - (tb.get("vol") or 0.0)) * 100, 2)},
            "square": sq or None,
            "same_accounting": "one ledger (GC001 cash leg, next-open fills, 8bp/side); "
                               "width and leverage rule each varied in turn",
            "source": src,
            "evidence_cutoff": audit.get("evidence_cutoff")}


def _resolution_md(ru):
    """One line: how big a difference this pairing could have seen (r1358).

    Kept as a helper because both sheets print it and a second copy would drift from the first
    (the E271 cross-document lesson). A face that publishes no per-phase dispersion cannot have
    its resolution computed, and that absence is printed rather than filled with a zero.
    """
    mde = ru.get("resolution_pp")
    if mde is None:
        return ("- 这一面没有公布逐相位离散度（sd），分辨下限算不出来——"
                "「两张单差不多」这句话在这张单上没有尺子支撑，按未核实读。")
    return ("- 这把尺子自己的分辨下限：%d 个相位、逐相位差 sd %.2fpp，在 %.0f%% 功效"
            "（双侧 5%%）下能分辨的最小差值 **%.2fpp**；本次差是它下限的 %.0f%% —— %s"
            % (ru.get("pairs") or 0, float(ru.get("paired_sd_pp") or 0.0),
               100.0 * float(ru.get("power_target") or 0.8), float(mde),
               100.0 * float(ru.get("gap_over_resolution") or 0.0),
               "在射程内，差值可读" if ru.get("below_own_resolution") is False
               else "低于下限：所以「两者没差别」也不是本窗的结论，结论是这把尺子分不开"))


def live_width_ruler(asof=None, card_n=None, card_dir=None, path=None,
                     sheet=None, stale_days=RULER_STALE_DAYS):
    """Is the gap between the two live faces bigger than the engines' own disagreement?

    ``scripts/etf_book_phase_atlas_arms.py --live-widths`` puts both live cells on one
    ruler, paired phase by phase. This reads that face back so the number reaches the
    person placing the order (r1275: a difference that only lives in research/ is a
    difference nobody was told about).

    The verdict is re-derived here from the face's own published numbers rather than
    copied off its label: a verdict that can drift away from the numbers that produced
    it is a receipt, not a gate (r1266).

    States, in precedence order:
      unavailable        -- no face on disk
      inconsistent       -- the face's own verdict contradicts the numbers it published
      widths_moved       -- the face priced widths the live faces no longer run
      stale              -- cutoff older than ``stale_days`` calendar days before asof
      inside_disagreement-- |paired median| < |5->12 rung disagreement| and signs split
      separated          -- the paired gap is at least the size of the disagreement
    """
    p = path or RULER_PATH
    try:
        with open(p, encoding="utf-8") as f:
            doc = json.load(f)
    except Exception:
        return {"state": "unavailable",
                "detail": "no live-width ruler on disk; run scripts/etf_book_phase_atlas_arms.py "
                          "--live-widths", "source": p.replace("\\", "/")}
    pr = doc.get("paired") or {}
    ed = doc.get("engine_disagreement") or {}
    lf = doc.get("live_faces") or {}
    rule = doc.get("rule") or {}
    gap = pr.get("median_pp")
    dis = ed.get("rung_disagreement_pp")
    sign = pr.get("sign_agreement")
    pairs = pr.get("pairs") or 0
    pairs_min = rule.get("pairs_min") or 20
    split_max = rule.get("sign_split_max") or 0.6
    cutoff = doc.get("evidence_cutoff")

    # re-derive rather than trust the label
    inside = (gap is not None and dis is not None and abs(float(gap)) < abs(float(dis)))
    split = (sign is not None and float(sign) <= float(split_max))
    if pairs < pairs_min:
        derived = "NOT_ENOUGH_PAIRS"
    elif inside and split:
        derived = "COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT"
    elif inside:
        derived = "INSIDE_DISAGREEMENT_NO_SIGN_SPLIT"
    else:
        derived = "SEPARATED"
    published = doc.get("verdict")
    published_inside = bool(published) and str(published).startswith("COIN_FLIP")
    relabel = bool(published) and published_inside != (derived ==
                                                       "COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT")

    # are the priced widths still the ones the faces run?
    n_card = card_n if card_n is not None else card_width(card_dir)
    c_rule = card_rule(card_dir)
    widths = {}
    moved = []
    # rule labels are not written identically by the two faces ("vol" off the card
    # artefact, "vol_target" off the atlas), so compare them on a normalised spelling --
    # otherwise every read of a healthy face would report widths_moved.
    def _rule_key(x):
        return (str(x or "").lower().replace("_target", "").strip()) or None
    for name, live_n, live_rule in (("ticket", int(N_HOLD), TICKET_RULE),
                                    ("card", n_card, c_rule)):
        cell = lf.get(name) or {}
        widths[name] = {"live_n_hold": live_n, "priced_n_hold": cell.get("n_hold"),
                        "live_rule": live_rule, "priced_rule": cell.get("rule")}
        if cell.get("n_hold") is not None and live_n is not None \
                and int(cell["n_hold"]) != int(live_n):
            moved.append(name)
        if _rule_key(cell.get("rule")) and _rule_key(live_rule) \
                and _rule_key(cell["rule"]) != _rule_key(live_rule):
            moved.append(name)

    age = None
    try:
        if cutoff and asof:
            age = (pd.Timestamp(asof) - pd.Timestamp(cutoff)).days
    except Exception:
        age = None
    stale = age is not None and age > stale_days

    if relabel:
        state, detail = "inconsistent", (
            "face says %s but its own numbers give %s" % (published, derived))
    elif moved:
        state, detail = "widths_moved", (
            "face priced %s width(s) the live faces no longer run (%s)"
            % ("/".join(sorted(set(moved))), ", ".join(
                "%s priced %s vs live %s" % (k, widths[k]["priced_n_hold"],
                                             widths[k]["live_n_hold"]) for k in widths)))
    elif stale:
        state, detail = "stale", ("cutoff %s is %d days behind asof %s (limit %d)"
                                  % (cutoff, age, asof, stale_days))
    elif derived == "COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT":
        state, detail = "inside_disagreement", (
            "paired median %+.3fpp inside a %0.3fpp engine disagreement"
            % (float(gap), float(dis)))
    elif derived == "NOT_ENOUGH_PAIRS":
        state, detail = "separated", ("only %d paired phases (need %d)" % (pairs, pairs_min))
    else:
        state, detail = "separated", (
            "paired median %+.3fpp vs %0.3fpp disagreement" % (float(gap), float(dis)))

    try:
        src = os.path.relpath(p, BASE).replace("\\", "/")
    except ValueError:
        src = p.replace("\\", "/")
    share = (abs(float(gap)) / abs(float(dis))) if (gap is not None and dis) else None
    # r1358: the pairing's own resolution, re-derived here from the sd and the phase count the
    # face publishes -- never copied off a stored field. "The gap is small" and "this pairing
    # could not have seen a gap this small" are different sentences, and a sheet that prints
    # only the first one invites a reader to conclude the widths are equivalent.
    res = doc.get("resolution") or {}
    sd_p = pr.get("sd_pp")
    z = res.get("power_z") or 2.802
    mde = None
    if sd_p and pairs:
        mde = (float(z) * float(sd_p)) / (float(pairs) ** 0.5)
    gap_over_mde = (abs(float(gap)) / mde) if (mde and gap is not None) else None
    # which of the two measured faces is the sheet asking for this reading? The paired gap
    # is between the faces, so a sheet that IS one of them is told what the OTHER one
    # measured -- printing the gap as if it were "this sheet vs the card" would be a
    # sentence about two different books. If the face no longer prices this sheet's width
    # the role goes unverified, so the page cannot keep printing a clean reading for a
    # book the face never measured (r1280 family: a label that outlives its numbers).
    sheet_role = None
    if sheet in ("card", "ticket"):
        sheet_role = ("unverified" if sheet in moved else
                      {"card": "measured_card", "ticket": "measured_ticket"}[sheet])
    return {"state": state, "detail": detail, "sheet": sheet, "sheet_role": sheet_role,
            "verdict": derived, "published_verdict": published,
            "gap_pp": gap, "disagreement_pp": dis,
            "share_of_disagreement": round(share, 4) if share is not None else None,
            "resolution_pp": round(mde, 3) if mde is not None else None,
            "gap_over_resolution": (round(gap_over_mde, 3)
                                    if gap_over_mde is not None else None),
            "below_own_resolution": (None if gap_over_mde is None
                                     else bool(gap_over_mde < 1.0)),
            "power_target": res.get("power_target"),
            "paired_sd_pp": sd_p,
            "atlas_rung_pp": ed.get("atlas_rung_pp"),
            "capacity_rung_pp": ed.get("capacity_rung_pp"),
            "sign_flips": ed.get("sign_flips"),
            "sign_agreement": sign, "pairs": pairs,
            "positive_phases": pr.get("positive"),
            "min_pp": pr.get("min_pp"), "max_pp": pr.get("max_pp"),
            "spread_pp": pr.get("spread_pp"),
            "widths": widths, "age_days": age,
            "evidence_cutoff": cutoff, "asof": asof, "source": src}


def _next_decision(score_dates, last_bar, rebal=REBAL, start="2020-01-01"):
    """Trading bars until the next decision on the engine's own grid (no future dates exist)."""
    dates = [d for d in score_dates if d >= pd.Timestamp(start)]
    if last_bar not in dates:
        return None
    pos = dates.index(last_bar)
    return int(((pos // rebal) + 1) * rebal - pos)


# --------------------------------------------------------------------------- selftest
def accrual_window(idx):
    """Which bars the cash carry was averaged over.

    Three faces quote a cash yield and none of them say over what: this ticket's backtest mean,
    the book page's last-12-months roll, and the last quote. All three are correct and they differ
    by a factor of two, so the window travels with the number (r1167).
    """
    idx = pd.DatetimeIndex(idx)
    if len(idx) == 0:
        return None
    return {"first": str(idx[0].date()), "last": str(idx[-1].date()),
            "years": round((idx[-1] - idx[0]).days / 365.25, 2)}


def selftest():
    ok = total = 0

    def chk(name, cond, extra=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print("[ok] %s %s" % (name, extra))
        else:
            print("[FAIL] %s %s" % (name, extra))

    rng = np.random.default_rng(20261025)
    idx = pd.bdate_range("2020-01-01", periods=400)
    rm = pd.Series(rng.normal(0.0002, 0.01, len(idx)), index=idx)
    rp = 0.5 * rm
    beta = (rp.expanding(min_periods=2).cov(rm)
            / rm.expanding(min_periods=2).var()).dropna()
    chk("leg1 expanding beta recovers 0.5", float(np.max(np.abs(beta - 0.5))) < 1e-9,
        "maxerr=%.2e" % float(np.max(np.abs(beta - 0.5))))

    sched = k_schedule(rp, rm, 0.20, step=20)
    chk("leg2 k = target/beta clipped to 1", bool(sched) and
        all(abs(k - 0.4) < 1e-12 for _, k, _ in sched),
        "k=%.3f n=%d" % (sched[0][1], len(sched)))
    sched_hi = k_schedule(rp, rm, 5.0, step=20)     # target >> beta -> must clip at 1
    chk("leg3 k never exceeds 1 (no leverage)", all(k <= 1.0 for _, k, _ in sched_hi),
        "max=%.3f" % max(k for _, k, _ in sched_hi))

    f_idx = pd.DatetimeIndex(["2021-01-08", "2021-01-11", "2021-01-12"])
    rates = pd.Series([3.65, 3.65, 3.65], index=f_idx)
    cash, miss = BW.repo_daily_cash(f_idx, rates)
    chk("leg4 Fri->Mon cash earns 3 calendar days",
        abs(float(cash.iloc[1]) - 3.65 / 100.0 * 3 / 365.0) < 1e-15 and miss == 0,
        "mon=%.8f" % float(cash.iloc[1]))

    # leg4b: the cash carry must say which bars it averaged. Three live faces quote a cash yield
    # (this ticket's backtest mean 2.087%, the book page's 1y roll 1.313%, the last quote 1.09%)
    # and without the window they read as a contradiction (r1167).
    chk("leg4b the cash carry states the window it averaged",
        accrual_window(d2 := pd.DatetimeIndex(["2021-01-04", "2021-01-07"]))
        == {"first": "2021-01-04", "last": "2021-01-07", "years": 0.01}
        and accrual_window(pd.DatetimeIndex([])) is None,
        str(accrual_window(d2)))

    # leg4c-e: the cash half is priced in CNY at the rates the book really parks in. Three
    # windows of the SAME panel, one amount -- a multi-year mean quoted alone is a history,
    # not a forecast, and at 1.09% today vs a 1.4%+ trailing mean the difference is real money
    # on the ticket. Unreadable inputs must stay None instead of printing 0 (the r1261 class).
    _cm_idx = pd.bdate_range("2024-01-01", periods=40)
    _cm_fell = pd.Series([2.10] * 30 + [1.05] * 10, index=_cm_idx)
    _cm_a = cash_money(500000.0, _cm_fell, "2024-02-23", accrual_pct=2.10)
    chk("leg4c the cash half is priced in CNY at three rates off one panel",
        _cm_a["verdict"] == "RATES_FELL"
        and abs(_cm_a["spot"]["annual_cny"] - 500000.0 * 1.05 / 100.0) < 0.5
        and abs(_cm_a["mean_tail"]["annual_cny"] - 500000.0
                * float(_cm_fell.mean()) / 100.0) <= 1.0
        and abs(_cm_a["window"]["annual_cny"] - 500000.0 * 2.10 / 100.0) < 0.5,
        "%s spot=%.2f%% -> %s CNY" % (_cm_a["verdict"], _cm_a["spot"]["pct"],
                                      format(int(_cm_a["spot"]["annual_cny"]), ",")))
    _cm_flat = cash_money(500000.0, pd.Series([1.50] * 40, index=_cm_idx), "2024-02-23",
                          accrual_pct=1.50)
    chk("leg4d a steady quote is called steady and prices no spread",
        _cm_flat["verdict"] == "RATES_STEADY"
        and _cm_flat["spread_vs_tail_cny"] == 0
        and "别把这个差当成常常有" not in (_cm_flat["sentence"] or ""),
        "%s spread=%s" % (_cm_flat["verdict"], _cm_flat["spread_vs_tail_cny"]))
    _cm_none = cash_money(None, _cm_fell, "2024-02-23")
    _cm_absent = cash_money(500000.0, pd.Series(dtype=float), "2024-02-23")
    _cm_late = cash_money(500000.0, _cm_fell, "2019-01-01")
    chk("leg4e unreadable cash is None, never 0",
        _cm_none["verdict"] == "CANNOT_PRICE" and _cm_none["cash_amount_cny"] is None
        and _cm_none["spot"] is None
        and _cm_absent["verdict"] == "CANNOT_PRICE" and _cm_absent["spot"] is None
        and _cm_absent["cash_amount_cny"] == 500000.0
        and _cm_late["verdict"] == "CANNOT_PRICE" and _cm_late["spot"] is None
        and all(_x["sentence"] for _x in (_cm_none, _cm_absent, _cm_late)),
        "none/absent/late all CANNOT_PRICE with a sentence")

    # leg5: the incremental ledger reproduces the engine on a hand-built path
    d2 = pd.DatetimeIndex(["2021-01-04", "2021-01-05", "2021-01-06", "2021-01-07"])
    rp2 = pd.Series([0.0, 0.01, -0.02, 0.0], index=d2)
    rf2 = pd.Series(0.0, index=d2)
    k2 = pd.Series([0.5, 0.5, 0.2, 0.2], index=d2)
    st, rows = accrue({"inception": "2021-01-04", "nav": 1.0, "last_k": None},
                      list(d2), rp2, rp2 * 2, k2, rf2, {})
    want = 1.0 * (1.0 + 0.5 * 0.01) * (1.0 + 0.2 * -0.02 - 0.3 * COST_BP / 10000.0)
    chk("leg5 ledger matches hand path (incl |dk| cost)",
        abs(st["nav"] - want) < 1e-12, "got %.10f want %.10f" % (st["nav"], want))

    # leg6: k idempotent -- re-running the same bars adds nothing
    st2, rows2 = accrue(st, list(d2), rp2, rp2 * 2, k2, rf2, {})
    chk("leg6 accrual is idempotent by bar", len(rows2) == 0, "added=%d" % len(rows2))

    # leg7: idle capital earns the repo rate
    kz = pd.Series(0.5, index=d2)
    rfz = pd.Series(0.01 / 252.0, index=d2)
    st3, _ = accrue({"inception": "2021-01-04", "nav": 1.0, "last_k": None},
                    list(d2), pd.Series(0.0, index=d2), pd.Series(0.0, index=d2),
                    kz, rfz, {})
    # four bars (not three): the fixture has four dates, and the un-invested half is 1-k
    want3 = (1.0 + (1.0 - 0.5) * 0.01 / 252.0) ** len(d2)
    chk("leg7 cash leg accrues on the un-invested half",
        abs(st3["nav"] - want3) < 1e-12, "got %.10f want %.10f" % (st3["nav"], want3))

    # leg8: ticket weights sum to 1 and never overspend NAV
    sc = pd.Series({"AAA": 3.0, "BBB": 2.0, "CCC": 1.0})
    px = pd.Series({"AAA": 3.31, "BBB": 12.7, "CCC": 0.777})
    tk = build_ticket(sc, px, 0.20, 1_000_000.0, n_hold=3)
    tot_w = sum(r["weight"] for r in tk["order"]) + tk["cash_weight"]
    spent = sum(r["amount"] for r in tk["order"])
    chk("leg8 ticket weights sum to 1, spend <= NAV",
        abs(tot_w - 1.0) < 1e-4 and spent <= 1_000_000.0 + 1e-6 and
        abs(tk["book_amount"] + tk["cash_amount"] - 1_000_000.0) < 1e-6,
        "w=%.6f spent=%.2f cash=%.2f" % (tot_w, spent, tk["cash_amount"]))

    # leg9: whole lots only
    chk("leg9 ticket quantities are whole lots",
        all(r["shares"] is None or r["shares"] % LOT == 0 for r in tk["order"]))

    # leg12/13: the width disclosure prices this ticket against the card's own width,
    # and stays silent-and-honest (None) rather than inventing a zero when the audit or
    # the card artefact is missing. Fixtures, not the live files.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        audit_p = os.path.join(td, "audit.json")
        with open(audit_p, "w", encoding="utf-8") as f:
            json.dump({"evidence_cutoff": "2026-10-23", "rows": [
                {"n_hold": 5, "book": {"cagr": 0.1105, "sharpe": 1.353, "maxdd": -0.0601}},
                {"n_hold": 12, "book": {"cagr": 0.0953, "sharpe": 1.560, "maxdd": -0.0417}}]}, f)
        # card_dir pointed at nothing: the live card's rule must not leak into a fixture
        # (the audit below carries one arm, which is then used and named).
        wd = width_disclosure(card_n=12, audit_path=audit_p,
                              card_dir=os.path.join(td, "no_card"))
        chk("leg12 width disclosure reads the two rows and their difference",
            bool(wd) and wd["ticket_names"] == 5 and wd["card_names"] == 12
            and abs(wd["delta_ticket_minus_card"]["cagr_pp"] - 1.52) < 1e-9
            and abs(wd["delta_ticket_minus_card"]["sharpe"] + 0.207) < 1e-9,
            "delta=%s" % (wd["delta_ticket_minus_card"] if wd else None))
        chk("leg13 missing width row -> None (no silent zero)",
            width_disclosure(card_n=99, audit_path=audit_p) is None
            and width_disclosure(card_n=12, audit_path=os.path.join(td, "nope.json")) is None)

        # leg14: the card width comes off the card's pointer chain, not a constant
        cd = os.path.join(td, "prod")
        os.makedirs(cd)
        with open(os.path.join(cd, "latest.json"), "w", encoding="utf-8") as f:
            json.dump({"file": "PRODUCTION-2026-10-23.json"}, f)
        with open(os.path.join(cd, "PRODUCTION-2026-10-23.json"), "w", encoding="utf-8") as f:
            json.dump({"config": {"n_hold": 12}}, f)
        chk("leg14 card width read from the card pointer chain",
            card_width(cd) == 12 and card_width(os.path.join(td, "absent")) is None,
            "read=%s" % card_width(cd))

        # leg15: latest.json may BE the card (live shape) or point at it -- the fixture
        # above only proved the pointer shape, and the live run then said "unavailable".
        cd2 = os.path.join(td, "prod2")
        os.makedirs(cd2)
        with open(os.path.join(cd2, "latest.json"), "w", encoding="utf-8") as f:
            json.dump({"config": {"n_hold": 12}, "sheet": {}}, f)
        chk("leg15 latest.json holding the card itself is read too",
            card_width(cd2) == 12, "read=%s" % card_width(cd2))
        chk("leg16 live wiring: real card x real audit produce a disclosure",
            (width_disclosure() is not None) if os.path.exists(AUDIT_PATH) else True,
            "card=%s audit=%s" % (card_width(), os.path.exists(AUDIT_PATH)))

        # leg17/18 -> numbered 27/28 (17/18 were taken by the decision-bar and card_book
        # legs below): the audit now carries BOTH leverage rules, so a lookup keyed on the
        # name count alone returns whichever arm was written last (r1280's "last arm
        # silently wins" class, one file over). The ticket's cell must be the BETA row
        # even though a vol row with the same n_hold exists further down the file, and
        # the two width effects must be reported as separate arms.
        audit2 = os.path.join(td, "audit2.json")
        with open(audit2, "w", encoding="utf-8") as f:
            json.dump({"evidence_cutoff": "2026-10-26", "rows": [
                {"n_hold": 5, "rule": "beta", "book": {"cagr": 0.1104, "sharpe": 1.352,
                                                       "maxdd": -0.0601, "vol": 0.0816}},
                {"n_hold": 12, "rule": "beta", "book": {"cagr": 0.0952, "sharpe": 1.561,
                                                        "maxdd": -0.0417, "vol": 0.061}},
                {"n_hold": 5, "rule": "vol", "book": {"cagr": 0.1169, "sharpe": 1.352,
                                                      "maxdd": -0.0756, "vol": 0.0865}},
                {"n_hold": 12, "rule": "vol", "book": {"cagr": 0.119, "sharpe": 1.357,
                                                       "maxdd": -0.0795, "vol": 0.0876}}]}, f)
        cd_arm = os.path.join(td, "prod_arm")
        os.makedirs(cd_arm, exist_ok=True)
        with open(os.path.join(cd_arm, "latest.json"), "w", encoding="utf-8") as f:
            json.dump({"config": {"n_hold": 12, "vol_target": 0.08}}, f)
        wd2 = width_disclosure(card_n=12, audit_path=audit2, card_dir=cd_arm)
        chk("leg27 width lookup keyed by (names, rule): ticket cell is the beta arm, "
            "not whichever arm was written last",
            bool(wd2) and abs(wd2["ticket"]["cagr"] - 0.1104) < 1e-12
            and abs(wd2["card"]["cagr"] - 0.119) < 1e-12
            and wd2["ticket_rule"] == "beta" and wd2["card_rule"] == "vol",
            "ticket=%s card=%s" % (wd2["ticket"]["cagr"] if wd2 else None,
                                   wd2["card"]["cagr"] if wd2 else None))
        chk("leg28 same-rule width effect reported per arm, and the published faces "
            "compared as a diagonal",
            bool(wd2) and abs(wd2["width_effect"]["beta"]["pp"] + 1.52) < 1e-9
            and abs(wd2["width_effect"]["vol"]["pp"] - 0.21) < 1e-9
            and abs(wd2["delta_ticket_minus_card"]["cagr_pp"] + 0.86) < 1e-9,
            "arms=%s diag=%.2f" % (wd2["width_effect"] if wd2 else None,
                                   (wd2["delta_ticket_minus_card"]["cagr_pp"] if wd2 else 0)))

        # leg17: the ticket ranks on the engine's last DECISION bar, not the panel's last
        # bar. Until r1277 it ranked slip.index[-1], so the ticket traded five names the
        # book never held (2026-10-23 ticket vs the 2026-10-14 book in force: disjoint).
        gd = list(pd.bdate_range("2021-01-04", periods=45))
        rebal_t = 20
        dec_bar = gd[(len(gd) - 1) // rebal_t * rebal_t]
        chk("leg17 ticket ranks on the last grid decision bar",
            dec_bar == gd[40] and dec_bar != gd[-1],
            "dec=%s last=%s" % (dec_bar.date(), gd[-1].date()))
        # leg18: card_book reads the sheet off the pointer chain and the ticket's N names
        # are a prefix of it when both rank on the same bar (cross-artefact agreement).
        cd3 = os.path.join(td, "prod3")
        os.makedirs(cd3)
        syms = ["A%03d" % i for i in range(6)]
        with open(os.path.join(cd3, "latest.json"), "w", encoding="utf-8") as f:
            json.dump({"config": {"n_hold": 6},
                       "feed_status": {"status": "stale_feed", "ticket_bar": "2026-10-23"},
                       "sheet": {"as_of_bar": "2026-10-23",
                                 "book_decided_at": "2026-10-14", "risk_scale": 0.7008,
                                 "legs": [{"symbol": s} for s in syms]}}, f)
        cb = card_book(cd3)
        chk("leg18 card_book reads the held book off the card",
            bool(cb) and cb["decided_at"] == "2026-10-14" and cb["symbols"] == syms
            and card_book(os.path.join(td, "absent")) is None,
            "decided_at=%s n=%s" % (cb and cb["decided_at"], cb and len(cb["symbols"])))
        chk("leg19 ticket names are a prefix of the card's book",
            cb["symbols"][:3] == syms[:3] and cb["symbols"][:3] != syms[3:6])

    # leg10: a short universe yields no ticket rather than a partial one
    chk("leg10 insufficient picks -> no ticket",
        build_ticket(pd.Series({"AAA": 1.0}), px, 0.2, 1e6, n_hold=3) is None)

    # leg11: k in force lags the decision by exactly one bar
    sched2 = [(idx[5], 0.7, 0.3)]
    kv = in_force(sched2, idx)
    chk("leg11 decision applies from the next bar", bool(np.isnan(kv.iloc[5]))
        and abs(float(kv.iloc[6]) - 0.7) < 1e-12, "k5=%s k6=%.3f" % (kv.iloc[5], kv.iloc[6]))

    # legs 20-24: the ticket must answer "is this priced off a current bar?" by itself,
    # because every other leg grades the panel by the panel (r1286/r1287).
    cal = ["2026-10-21", "2026-10-22", "2026-10-23", "2026-10-26"]
    cur = feed_status(cal, "2026-10-26", "2026-10-26", "in_sync")
    chk("leg20 ticket on the newest official bar reads current",
        cur["status"] == "current" and cur["lag_days"] == 0,
        "status=%s lag=%s" % (cur["status"], cur["lag_days"]))
    lag1 = feed_status(cal, "2026-10-23", "2026-10-26", "source_lag")
    chk("leg21 one unpublished day reads as a 1-day lag (Fri->Mon costs 1, not 3)",
        lag1["status"] == "stale_feed" and lag1["lag_days"] == 1,
        "status=%s lag=%s" % (lag1["status"], lag1["lag_days"]))
    gap = feed_status(cal, "2026-10-22", "2026-10-26", "panel_gap")
    chk("leg22 a stopped feed outranks the plain lag",
        gap["status"] == "feed_broken" and gap["lag_days"] == 2,
        "status=%s lag=%s" % (gap["status"], gap["lag_days"]))
    unk = feed_status(cal, "2026-10-23", None, "in_sync")
    chk("leg23 no calendar reads unknown, never current", unk["status"] == "unknown",
        "status=%s" % unk["status"])
    md = card(None, None, None, "2026-10-23", 0.2,
              {"inception": "2024-01-01", "feed": lag1})
    chk("leg24 the stale warning reaches the one-page face a human reads",
        "\u26a0" in md and "stale_feed" in md, "chars=%d" % len(md))

    # leg24b/c (r1348): the sheet prints one realised drawdown, but the bootstrap arms put
    # the p5 several pp deeper. A tail quoted without its block is a sentence without its
    # parameter, so the sheet must carry both -- and must say 'unpublished' when absent.
    _db_keep = glob.glob
    try:
        doc = {"evidence_cutoff": "2026-10-29", "arms": [{"block": 5}, {"block": 250}],
               "spread": {"maxdd_p5": {"min": -0.2502, "max": -0.1708},
                          "maxdd_p50": {"min": -0.1459, "max": -0.1214},
                          "dd_break_share": {"min": 0.011, "max": 0.161}}}
        glob.glob = lambda *a, **k: [os.path.join("X", "BLOCKS-2026-10-29.json")]
        _open = open

        class _F:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self, *a):
                return json.dumps(doc)

        import builtins
        builtins.open = lambda *a, **k: _F()
        try:
            band = drawdown_band()
            md_band = card(None, None, None, "2026-10-29", 0.2, {"inception": "2024-01-01"})
        finally:
            builtins.open = _open
        chk("leg24b sheet carries the drawdown band with its block set",
            band is not None and "-25.0%" in md_band and "5/250" in md_band,
            "band=%s" % (band or {}).get("block_set"))
        glob.glob = lambda *a, **k: []
        chk("leg24c no band on disk is disclosed, never invented",
            drawdown_band() is None
            and "无自助带在盘" in card(None, None, None, "2026-10-29", 0.2,
                                       {"inception": "2024-01-01"}))
    finally:
        glob.glob = _db_keep

    # legs 25-26: two faces can share a decision bar and still price a day apart -- on a
    # HOLD bar the vol overlay re-sizes weights and the cash slot every single day, so the
    # priced bar has to travel with the book (r1290: card at 10-23/stale_feed, ticket at
    # 10-26/current, and nothing in either face said so).
    import shutil
    import tempfile
    cdt = tempfile.mkdtemp()
    try:
        with open(os.path.join(cdt, "latest.json"), "w", encoding="utf-8") as f:
            json.dump({"feed_status": {"status": "stale_feed", "ticket_bar": "2026-10-23"},
                       "sheet": {"as_of_bar": "2026-10-23", "book_decided_at": "2026-10-14",
                                 "legs": [{"symbol": "AAA"}]}}, f)
        cbo = card_book(cdt)
        chk("leg25 card_book carries the priced bar and its feed status",
            cbo["priced_bar"] == "2026-10-23" and cbo["feed_status"] == "stale_feed",
            "bar=%s feed=%s" % (cbo.get("priced_bar"), cbo.get("feed_status")))
        md_split = card(None, None, None, "2026-10-26", 0.2,
                        {"inception": "2024-01-01", "feed": cur,
                         "agreement": {"card_decided_at": cbo["decided_at"],
                                       "ticket_book_decided_at": "2026-10-14",
                                       "same_decision_bar": True,
                                       "card_priced_bar": cbo["priced_bar"],
                                       "card_feed_status": cbo["feed_status"],
                                       "ticket_priced_bar": "2026-10-26",
                                       "same_priced_bar": False}})
        chk("leg26 a one-day-stale card is flagged despite a matching decision bar",
            "\u26a0" in md_split and "两张面定价不在同一天" in md_split
            and "一致=True" in md_split, "chars=%d" % len(md_split))
        _pf_split = {"faces": {"card": "2026-10-23", "ticket": "2026-10-26",
                               "page": "2026-10-26"},
                     "verdict": "DIFFERENT_DAYS",
                     "detail": "priced on different bars: card 2026-10-23 / ticket 2026-10-26 "
                               "/ page 2026-10-26",
                     "missing": [], "same_day": False}
        md_pf = card(None, None, None, "2026-10-26", 0.2,
                     {"inception": "2024-01-01", "feed": cur,
                      "agreement": {"card_decided_at": cbo["decided_at"],
                                    "ticket_book_decided_at": "2026-10-14",
                                    "same_decision_bar": True,
                                    "card_priced_bar": cbo["priced_bar"],
                                    "card_feed_status": cbo["feed_status"],
                                    "ticket_priced_bar": "2026-10-26",
                                    "same_priced_bar": False},
                      "priced_faces": _pf_split})
        chk("leg26b the sheet names WHICH of the three papers is the stale one",
            "不是同一天" in md_pf and "卡片 2026-10-23" in md_pf
            and "CEO 一页纸 2026-10-26" in md_pf, "chars=%d" % len(md_pf))
        _pf_missing = {"faces": {"card": "2026-10-26", "ticket": "2026-10-26", "page": None},
                       "verdict": "UNKNOWN", "detail": "no pricing day on: page",
                       "missing": ["page"], "same_day": None}
        md_pf_unk = card(None, None, None, "2026-10-26", 0.2,
                         {"inception": "2024-01-01", "feed": cur,
                          "agreement": {"card_decided_at": cbo["decided_at"],
                                        "ticket_book_decided_at": "2026-10-14",
                                        "same_decision_bar": True,
                                        "card_priced_bar": cbo["priced_bar"],
                                        "card_feed_status": cbo["feed_status"],
                                        "ticket_priced_bar": "2026-10-26",
                                        "same_priced_bar": True},
                          "priced_faces": _pf_missing})
        chk("leg26c a missing paper reads unknown, never same-day",
            "无法判断" in md_pf_unk and "同一天**：" not in md_pf_unk,
            "chars=%d" % len(md_pf_unk))
    finally:
        shutil.rmtree(cdt, ignore_errors=True)

    # ---- card-config ticket (r1333): the executable face must be the card's own book
    cdt = tempfile.mkdtemp()
    try:
        legs = [{"symbol": "AAA", "name": "a", "class": "equity", "weight": 0.2,
                 "ref_price": 2.0, "lots_100": 100000, "amount_cny": 200000.0,
                 "actual_amount_cny": 200000.0},
                {"symbol": "BBB", "name": "b", "class": "equity", "weight": 0.25,
                 "ref_price": 5.0, "lots_100": 50000, "amount_cny": 250000.0,
                 "actual_amount_cny": 250000.0},
                {"symbol": "CCC", "name": "c", "class": "equity", "weight": 0.25,
                 "ref_price": 1.0, "lots_100": 250000, "amount_cny": 250000.0,
                 "actual_amount_cny": 250000.0}]
        card_doc = {"config": {"n_hold": 3, "rebal": 20, "vol_target": 0.08,
                              "capital_cny": 1000000.0, "cost_bp_per_side": 10.0},
                    "feed_status": {"status": "current", "ticket_bar": "2026-10-28",
                                    "expected_bar": "2026-10-28", "lag_days": 0},
                    "sheet": {"as_of_bar": "2026-10-28", "book_decided_at": "2026-10-14",
                              "capital_cny": 1000000.0, "risk_scale": 0.7,
                              "target_vol": 0.08, "cash_weight": 0.3,
                              "cash_amount_cny": 300000.0, "legs": legs,
                              "bars_until_next_decision": 10}}
        with open(os.path.join(cdt, "latest.json"), "w", encoding="utf-8") as f:
            json.dump(card_doc, f, ensure_ascii=False)
        led_same = {"config": {"n_hold": 3, "vol_target": 0.08, "rebal": 20,
                               "cost_per_side": 0.001},
                    "book_in_force": {"bar": "2026-10-14", "scale": 0.7,
                                      "names": ["AAA", "BBB", "CCC"]},
                    "bars": [{"bar": "2026-10-28", "nav": 1.00053}], "status": "live"}
        lp = os.path.join(cdt, "LEDGER.json")
        with open(lp, "w", encoding="utf-8") as f:
            json.dump(led_same, f, ensure_ascii=False)

        tk = card_config_ticket(card_dir=cdt, ledger_path=lp)
        rc = tk["recon"] if tk else {}
        chk("leg27 card-config ticket reproduces the card's names, scale and config",
            bool(tk) and rc.get("same_names_as_card") is True
            and rc.get("same_names_as_ledger") is True
            and rc.get("same_scale_as_ledger") is True
            and rc.get("same_config_as_ledger") is True,
            "names=%s scale=%s cfg=%s" % (rc.get("same_names_as_card"),
                                          rc.get("same_scale_as_ledger"),
                                          rc.get("same_config_as_ledger")))
        chk("leg28 lots recomputed from price x weight match the card's published lot counts",
            bool(tk) and tk["reprice_mismatch"] == []
            and [r["lots"] for r in tk["order"]] == [1000, 500, 2500],
            "mismatch=%s" % (tk["reprice_mismatch"] if tk else None))

        tk2 = card_config_ticket(card_dir=cdt, ledger_path=lp, nav=2000000.0)
        chk("leg29 a doubled stated capital doubles the book and keeps the cash share",
            bool(tk2) and abs(tk2["cash_weight"] - 0.3) < 0.001
            and 0.98 * 1_400_000.0 <= tk2["book_amount"] <= 1_400_000.0,
            "book=%.0f cash_w=%.4f" % (tk2["book_amount"] if tk2 else -1,
                                       tk2["cash_weight"] if tk2 else -1))

        led_other = json.loads(json.dumps(led_same))
        led_other["book_in_force"]["names"] = ["AAA", "BBB", "ZZZ"]
        lp2 = os.path.join(cdt, "LEDGER-other.json")
        with open(lp2, "w", encoding="utf-8") as f:
            json.dump(led_other, f, ensure_ascii=False)
        tk3 = card_config_ticket(card_dir=cdt, ledger_path=lp2)
        chk("leg30 a ledger holding other names is reported as a different book",
            bool(tk3) and tk3["recon"]["same_names_as_ledger"] is False,
            "verdict=%s" % (tk3["recon"]["same_names_as_ledger"] if tk3 else None))

        md_card = card_config_card(tk, None) if tk else ""
        chk("leg31 the order sheet prints the three-face table and both verdicts",
            "三面是不是同一本书" in md_card and "本单 vs 卡片 一致" in md_card
            and "本单 vs 账本 一致" in md_card and "2.000" in md_card,
            "chars=%d" % len(md_card))

        # ---- restated-bar notice (r1371): a mark that moves after the bar settled is a
        # history change, and the operator holding the sheet was the last to hear about it.
        led_rst = json.loads(json.dumps(led_same))
        led_rst["restatements"] = [{"ts": "2026-10-30T19:18:29+0800", "bar": "2026-10-28",
                                    "reason": "published while the panel was still filling",
                                    "nav_published": 1.00053, "nav_settled": 1.00052,
                                    "delta": -1e-05}]
        lp3 = os.path.join(cdt, "LEDGER-rst.json")
        with open(lp3, "w", encoding="utf-8") as f:
            json.dump(led_rst, f, ensure_ascii=False)
        tk4 = card_config_ticket(card_dir=cdt, ledger_path=lp3)
        md4 = card_config_card(tk4, None) if tk4 else ""
        chk("leg31b a bar restated after settling reaches the ticket instead of being silent history",
            bool(tk4) and tk4["recon"]["restated_bars"] == ["2026-10-28"]
            and "定格之后又被改述" in md4 and "1.00053000" in md4 and "1.00052000" in md4,
            "bars=%s in_md=%s" % (tk4["recon"]["restated_bars"] if tk4 else None,
                                  "定格之后又被改述" in md4))

        # the record existed on the bars before it existed at the ledger's top level
        led_rst2 = json.loads(json.dumps(led_same))
        led_rst2["bars"] = [{"bar": "2026-10-28", "nav": 1.00052,
                             "restated_at": "2026-10-30T19:18:29+0800",
                             "nav_published": 1.00053, "nav_settled": 1.00052}]
        led_rst2.pop("restatements", None)
        lp4 = os.path.join(cdt, "LEDGER-rst-on-bars.json")
        with open(lp4, "w", encoding="utf-8") as f:
            json.dump(led_rst2, f, ensure_ascii=False)
        tk5 = card_config_ticket(card_dir=cdt, ledger_path=lp4)
        _r5 = (tk5 or {}).get("recon") or {}
        chk("leg31c an older ledger that records restatements only on its bars still reaches the sheet",
            bool(tk5) and _r5.get("restatements_source") == "bars"
            and _r5.get("restated_bars") == ["2026-10-28"]
            and abs((_r5.get("restatements") or [{}])[0].get("delta") + 1e-05) < 1e-9,
            "source=%s bars=%s" % (_r5.get("restatements_source"), _r5.get("restated_bars")))

        # "no restatement" must be something the sheet checked, never the default when the
        # ledger is missing -- otherwise a deleted artifact reads as a clean history.
        tk6 = card_config_ticket(card_dir=cdt, ledger_path=os.path.join(cdt, "NO-LEDGER.json"))
        md6 = card_config_card(tk6, None) if tk6 else ""
        chk("leg31d an unreadable ledger prints 'cannot verify', not 'no restatements'",
            bool(tk6) and tk6["recon"]["restatements_readable"] is False
            and "无法核验" in md6 and "没有一根在定格之后被改述" not in md6,
            "readable=%s" % (tk6["recon"]["restatements_readable"] if tk6 else None))

        led_clean = json.loads(json.dumps(led_same))
        led_clean["restatements"] = []
        lp5 = os.path.join(cdt, "LEDGER-clean.json")
        with open(lp5, "w", encoding="utf-8") as f:
            json.dump(led_clean, f, ensure_ascii=False)
        tk7 = card_config_ticket(card_dir=cdt, ledger_path=lp5)
        md7 = card_config_card(tk7, None) if tk7 else ""
        chk("leg31e a readable ledger with an empty restatement list says so as a checked fact",
            bool(tk7) and tk7["recon"]["restatements_readable"] is True
            and tk7["recon"]["restated_bars"] == []
            and "没有一根在定格之后被改述" in md7 and "1 根 bar" in md7,
            "readable=%s bars=%s" % (tk7["recon"].get("restatements_readable") if tk7 else None,
                                     tk7["recon"]["restated_bars"] if tk7 else None))
    finally:
        shutil.rmtree(cdt, ignore_errors=True)

    # ---- lot granularity (r1334): the card's cash row is a target, the desk gets
    # floor'ed lots, so the shortfall has to be published as a curve over capital.
    fx = [{"symbol": "AAA", "weight": 0.0584, "ref_price": 2.194},
          {"symbol": "BBB", "weight": 0.0584, "ref_price": 11.8419},
          {"symbol": "CCC", "weight": 0.0584, "ref_price": 1.095},
          {"symbol": "DDD", "weight": 0.0584, "ref_price": 3.407}]
    lp1 = lot_point(fx, 1_000_000.0, scale=0.2336)
    chk("leg32 the lot point reports cash vs the card's target and the worst mis-sized leg",
        lp1["cash_vs_target_cny"] > 0.0 and lp1["max_abs_weight_drift_pp"] > 0.0
        and lp1["target_book_cny"] == 233600.0,
        "cash_vs_target=%s drift=%.3f" % (lp1["cash_vs_target_cny"],
                                          lp1["max_abs_weight_drift_pp"]))
    lc = lot_curve(fx, scale=0.2336)
    chk("leg33 granularity cost falls monotonically as the book grows",
        lc["monotone_non_increasing"] is True
        and lc["points"][-1]["max_abs_weight_drift_pp"]
        < lc["points"][0]["max_abs_weight_drift_pp"],
        "first=%.3f last=%.3f" % (lc["points"][0]["max_abs_weight_drift_pp"],
                                  lc["points"][-1]["max_abs_weight_drift_pp"]))
    px_lot = max(l["ref_price"] * LOT for l in fx)
    chk("leg34 every leg is off by less than one lot (drift bound = px*lot / capital)",
        all(p["max_abs_weight_drift_pp"] <= 100.0 * px_lot / p["capital_cny"] + 1e-6
            for p in lc["points"]),
        "bound at 50k=%.2f" % (100.0 * px_lot / 50_000.0))
    cheap = [{"symbol": "E%02d" % i, "weight": 0.05, "ref_price": 1.0}
             for i in range(19)] + [{"symbol": "PRICEY", "weight": 0.05,
                                     "ref_price": 1000.0}]
    lc2 = lot_curve(cheap, scale=1.0)
    chk("leg35 below the one-lot floor the book cannot even be bought (legs_with_zero_lots)",
        lc2["one_lot_floor_cny"] == 100_000.0 / 0.05
        and lc2["points"][0]["legs_with_zero_lots"] >= 1
        and lc2["points"][-1]["legs_with_zero_lots"] == 0,
        "floor=%s zero@50k=%d zero@20M=%d" % (lc2["one_lot_floor_cny"],
                                              lc2["points"][0]["legs_with_zero_lots"],
                                              lc2["points"][-1]["legs_with_zero_lots"]))
    md_lc = "\n".join(lot_curve_md(lc, 1_000_000.0))
    chk("leg36 the operator's page carries the capital table and both thresholds",
        "| 资金 |" in md_lc and "≤1.00pp" in md_lc and "单调不增" in md_lc,
        "chars=%d" % len(md_lc))
    chk("leg37 the yuan shortfall is bounded by one lot per leg and does NOT shrink",
        lc["max_observed_shortfall_cny"] <= lc["shortfall_bound_cny"] + 1e-6
        and abs(lc["points"][0]["cash_vs_target_cny"]
                - lc["points"][-1]["cash_vs_target_cny"])
            < lc["shortfall_bound_cny"],
        "bound=%s max=%s" % (lc["shortfall_bound_cny"], lc["max_observed_shortfall_cny"]))

    # ---- r1342: the card's cash row is now the EXECUTABLE cash, so the ticket must agree
    # with it to the yuan and stop printing the "card row is only a target" disclosure.
    # Both directions are asserted on the same fixture: a card that prints
    # capital - spent closes the gap, a legacy card that prints (1 - k) * capital still
    # gets called out. One-sided, this leg would pass on the old renderer too.
    cdt3 = tempfile.mkdtemp()
    try:
        leg_fx = [{"symbol": s, "name": s, "class": "equity", "weight": 0.35,
                   "ref_price": 2.194, "lots_100": 159500, "amount_cny": 350000.0,
                   "actual_amount_cny": 349943.0} for s in ("AAA", "BBB")]
        sheet_fx = {"as_of_bar": "2026-10-29", "book_decided_at": "2026-10-14",
                    "capital_cny": 1000000.0, "risk_scale": 0.7, "target_vol": 0.08,
                    "cash_weight": 0.3, "legs": leg_fx,
                    "bars_until_next_decision": 9}
        cfg_fx = {"n_hold": 2, "rebal": 20, "vol_target": 0.08,
                  "capital_cny": 1000000.0, "cost_bp_per_side": 10.0}
        lp4 = os.path.join(cdt3, "LEDGER.json")
        with open(lp4, "w", encoding="utf-8") as f:
            json.dump({"config": {"n_hold": 2, "vol_target": 0.08, "rebal": 20,
                                  "cost_per_side": 0.001},
                       "book_in_force": {"bar": "2026-10-14", "scale": 0.7,
                                         "names": ["AAA", "BBB"]},
                       "bars": [{"bar": "2026-10-29", "nav": 1.0}], "status": "live"},
                      f, ensure_ascii=False)
        printed = {}
        for label, cash_row in (("executable", {"cash_executable_cny": 1000000.0 - 2 * 349943.0,
                                                "cash_amount_cny": 300000.0}),
                                ("target", {"cash_amount_cny": 300000.0})):
            doc = {"config": cfg_fx,
                   "feed_status": {"status": "current", "ticket_bar": "2026-10-29",
                                   "expected_bar": "2026-10-29", "lag_days": 0},
                   "sheet": dict(sheet_fx, **cash_row)}
            with open(os.path.join(cdt3, "latest.json"), "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False)
            tk_fx = card_config_ticket(card_dir=cdt3, ledger_path=lp4)
            md_fx = card_config_card(tk_fx, None) if tk_fx else ""
            printed[label] = (tk_fx, md_fx)
        tk_e, md_e = printed["executable"]
        tk_t, md_t = printed["target"]
        chk("leg38 an executable cash row closes the ticket gap to the yuan",
            bool(tk_e) and abs(tk_e["cash_amount"]
                               - (1000000.0 - 2 * 349943.0)) <= 1e-6
            and "卡片现金行是目标口径" not in md_e,
            "cash=%.2f gap_paragraph=%s" % (tk_e["cash_amount"] if tk_e else -1,
                                            "卡片现金行是目标口径" in md_e))
        chk("leg39 a legacy target cash row is still called out as a target",
            bool(tk_t) and "卡片现金行是目标口径" in md_t,
            "legacy_paragraph=%s" % ("卡片现金行是目标口径" in md_t))
    finally:
        shutil.rmtree(cdt3, ignore_errors=True)

    # ---- r1356b: the live-width ruler has to reach the ticket, and its verdict has to be
    # re-derived from the numbers it publishes (r1266: a label copied blind is a receipt).
    # Every state gets its own fixture, and the widths/staleness ones are the two ways a
    # stale face would otherwise keep printing a clean "coin flip" forever.
    cdt5 = tempfile.mkdtemp()
    try:
        def _ruler_doc(**over):
            d = {"script": "scripts/etf_book_phase_atlas_arms.py --live-widths",
                 "rule": {"pairs_min": 20, "sign_split_max": 0.6},
                 "evidence_cutoff": "2026-10-29",
                 "live_faces": {"card": {"n_hold": 12, "rule": "vol_target"},
                                "ticket": {"n_hold": 5, "rule": "beta"}},
                 "paired": {"pairs": 20, "median_pp": 0.09, "positive": 10,
                            "sign_agreement": 0.5, "spread_pp": 4.94},
                 "engine_disagreement": {"atlas_rung_pp": 0.515, "capacity_rung_pp": -1.53,
                                         "rung_disagreement_pp": 2.045, "sign_flips": True},
                 "verdict": "COIN_FLIP_INSIDE_ENGINE_DISAGREEMENT"}
            d.update(over)
            return d

        def _put(name, doc):
            fp = os.path.join(cdt5, name)
            with open(fp, "w", encoding="utf-8") as f:
                json.dump(doc, f)
            return fp

        cd5 = os.path.join(cdt5, "card")
        os.makedirs(cd5, exist_ok=True)
        with open(os.path.join(cd5, "latest.json"), "w", encoding="utf-8") as f:
            json.dump({"config": {"n_hold": 12, "vol_target": 0.08, "rebal": 20}}, f)

        r_in = live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5,
                                path=_put("in.json", _ruler_doc()))
        chk("leg40 a paired gap inside the engines' own disagreement reads as a coin flip",
            r_in["state"] == "inside_disagreement"
            and abs(r_in["share_of_disagreement"] - 0.044) < 5e-3,
            "state=%s share=%.4f" % (r_in["state"], r_in["share_of_disagreement"] or -1))
        chk("leg40b a gap larger than the disagreement stops being a coin flip",
            live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5,
                             path=_put("wide.json", _ruler_doc(
                                 paired={"pairs": 20, "median_pp": 3.0, "positive": 18,
                                         "sign_agreement": 0.9, "spread_pp": 4.94},
                                 verdict="SEPARATED")))["state"] == "separated",
            "")
        chk("leg40c a face whose label contradicts its own numbers is flagged, not trusted",
            live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5,
                             path=_put("lab.json", _ruler_doc(
                                 paired={"pairs": 20, "median_pp": 3.0, "positive": 18,
                                         "sign_agreement": 0.9, "spread_pp": 4.94})
                             ))["state"] == "inconsistent", "")
        chk("leg40d a face pricing widths the live faces no longer run says so",
            live_width_ruler(asof="2026-10-29", card_n=8, card_dir=cd5,
                             path=_put("mov.json", _ruler_doc()))["state"] == "widths_moved",
            "")
        chk("leg40e an old cutoff is stale rather than a standing verdict",
            live_width_ruler(asof="2026-11-20", card_n=12, card_dir=cd5,
                             path=_put("old.json", _ruler_doc(evidence_cutoff="2026-10-20"))
                             )["state"] == "stale", "")
        chk("leg40f no face on disk is unavailable, never silently clean",
            live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5,
                             path=os.path.join(cdt5, "nope.json"))["state"] == "unavailable",
            "")

        md_r = card(None, None, None, "2026-10-29", 0.2,
                    {"ruler": r_in, "width": None, "feed": None, "agreement": None})
        chk("leg41 the order page prints the ruler (a number in research/ reaches nobody)",
            "## 两张面之间的差" in md_r and "+0.09pp" in md_r and "2.0" in md_r
            and "%" in md_r,
            "chars=%d gap=%s" % (len(md_r), "+0.09pp" in md_r))
        bad_r = dict(r_in, state="stale", detail="cutoff 2026-10-01 is 28 days behind")
        md_st = card(None, None, None, "2026-10-29", 0.2,
                     {"ruler": bad_r, "width": None, "feed": None, "agreement": None})
        chk("leg41b a non-clean ruler changes what the page says",
            md_st != md_r and "尺子状态" in md_st, "")

        # ---- r1357: the SAME ruler has to reach the card sheet, and it has to say which
        # face on that ruler this sheet is. The paired gap is between the two live faces,
        # so a card sheet that printed "gap vs the card" would be quoting a difference
        # between two other books. Three legs: the reading is there and names the other
        # face, a moved-widths face leaves the sheet unverified instead of clean, and the
        # caller's sheet label alone cannot invent a role.
        chk("leg42 the ruler knows which face the asking sheet is (and never for free)",
            live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5, sheet="card",
                             path=_put("s_card.json", _ruler_doc()))["sheet_role"]
            == "measured_card"
            and live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5, sheet="ticket",
                                 path=_put("s_tk.json", _ruler_doc()))["sheet_role"]
            == "measured_ticket"
            and live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5, sheet="x",
                                 path=_put("s_x.json", _ruler_doc()))["sheet_role"] is None,
            "")
        r_moved = live_width_ruler(asof="2026-10-29", card_n=8, card_dir=cd5, sheet="card",
                                   path=_put("s_mv.json", _ruler_doc()))
        chk("leg42b a face pricing a width we no longer run leaves this sheet unverified",
            r_moved["state"] == "widths_moved" and r_moved["sheet_role"] == "unverified",
            "state=%s role=%s" % (r_moved["state"], r_moved["sheet_role"]))

        # a 12-leg card sheet, so the rendered page is the one a reader would hold
        cd6 = os.path.join(cdt5, "card12")
        os.makedirs(cd6, exist_ok=True)
        legs12 = [{"symbol": "S%02d" % i, "name": "S%02d" % i, "class": "equity",
                   "weight": 0.058, "ref_price": 2.0, "lots_100": 29000,
                   "amount_cny": 58000.0, "actual_amount_cny": 58000.0} for i in range(12)]
        with open(os.path.join(cd6, "latest.json"), "w", encoding="utf-8") as f:
            json.dump({"config": {"n_hold": 12, "rebal": 20, "vol_target": 0.08,
                                  "capital_cny": 1000000.0, "cost_bp_per_side": 10.0},
                       "feed_status": {"status": "current", "ticket_bar": "2026-10-29",
                                       "expected_bar": "2026-10-29", "lag_days": 0},
                       "sheet": {"as_of_bar": "2026-10-29", "book_decided_at": "2026-10-14",
                                 "capital_cny": 1000000.0, "risk_scale": 0.7,
                                 "target_vol": 0.08, "cash_weight": 0.3, "legs": legs12,
                                 "bars_until_next_decision": 9}}, f, ensure_ascii=False)
        lp6 = os.path.join(cdt5, "LEDGER6.json")
        with open(lp6, "w", encoding="utf-8") as f:
            json.dump({"config": {"n_hold": 12, "vol_target": 0.08, "rebal": 20,
                                  "cost_per_side": 0.001},
                       "book_in_force": {"bar": "2026-10-14", "scale": 0.7,
                                         "names": [r["symbol"] for r in legs12]},
                       "bars": [{"bar": "2026-10-29", "nav": 1.0}], "status": "live"},
                      f, ensure_ascii=False)
        tk12 = card_config_ticket(card_dir=cd6, ledger_path=lp6)
        r_card = live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5, sheet="card",
                                  path=_put("s_card2.json", _ruler_doc()))
        md_c = card_config_card(tk12, None, r_card) if tk12 else ""
        chk("leg42c the card sheet prints the other sheet's measured gap, not its own",
            bool(tk12) and "+0.09pp" in md_c and "5 名 beta 覆盖那张单 vs 本单" in md_c
            and "另一张单和本单的差" in md_c and "4.4%" in md_c,
            "chars=%d has_gap=%s" % (len(md_c), "+0.09pp" in md_c))
        md_cu = card_config_card(tk12, None, r_moved) if tk12 else ""
        chk("leg42d an unverified sheet cannot print the clean reading",
            bool(md_cu) and "未核实" in md_cu and "+0.09pp" not in md_cu
            and md_cu != md_c, "")
        # r1358: the resolution is re-derived from the face's own sd and phase count. A face that
        # publishes a stored mde has no say here -- a number that can be edited independently of
        # the numbers that produce it is a receipt (r1266), so feed a poisoned one and demand the
        # derived value.
        r_res = live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5,
                                 path=_put("res.json", _ruler_doc(
                                     paired={"pairs": 20, "median_pp": 0.09, "positive": 10,
                                             "sign_agreement": 0.5, "spread_pp": 4.94,
                                             "sd_pp": 1.255},
                                     resolution={"mde_pp": 9.99, "power_z": 2.802,
                                                 "power_target": 0.8})))
        chk("leg42e the resolution is re-derived from sd and pairs, never read off the face",
            r_res.get("resolution_pp") is not None
            and abs(r_res["resolution_pp"] - 0.786) < 2e-3
            and r_res["resolution_pp"] != 9.99,
            "mde=%r" % (r_res.get("resolution_pp"),))
        r_wide = live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5,
                                  path=_put("wide2.json", _ruler_doc(
                                      paired={"pairs": 20, "median_pp": 0.09, "positive": 10,
                                              "sign_agreement": 0.5, "spread_pp": 4.94,
                                              "sd_pp": 4.0})))
        r_big = live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5,
                                 path=_put("big.json", _ruler_doc(
                                     paired={"pairs": 20, "median_pp": 3.0, "positive": 18,
                                             "sign_agreement": 0.9, "spread_pp": 4.94,
                                             "sd_pp": 1.0},
                                     verdict="SEPARATED")))
        chk("leg42f a gap under the pairing's own resolution is flagged, a big one is not",
            r_wide.get("below_own_resolution") is True
            and r_big.get("below_own_resolution") is False,
            "wide=%r big=%r" % (r_wide.get("below_own_resolution"),
                                r_big.get("below_own_resolution")))
        chk("leg42g a face with no published dispersion says so instead of printing a zero",
            "没有公布逐相位离散度" in _resolution_md(
                live_width_ruler(asof="2026-10-29", card_n=12, card_dir=cd5,
                                 path=_put("nosd.json", _ruler_doc()))), "")
    finally:
        shutil.rmtree(cdt5, ignore_errors=True)

    # ---- r1367: the sheet quotes one CAGR for a book that parks half its NAV in repo.
    # The split lives in one artifact; the ticket must carry it at ITS OWN beta, must do
    # the arithmetic rather than trust a field name, and must say so when the artifact is
    # missing or priced on another bar -- silence reads as "the whole number is alpha".
    cdt7 = tempfile.mkdtemp()
    try:
        rg = {"evidence_cutoff": "2026-10-30",
              "cash_rates": {"today_pct": 1.09, "today_date": "2026-10-27",
                             "observed_mean_pct": 1.9819},
              "gate": {"base_beta": 0.2,
                       "betas": {"0.1": {"observed_pct": 6.4, "flat_today_pct": 5.95,
                                         "zero_pct": 5.05, "carry_share_of_headline_pct": 21.1,
                                         "pp_per_100bp": 0.505, "cash_share": 0.775},
                                 "0.2": {"observed_pct": 11.19, "flat_today_pct": 10.85,
                                         "zero_pct": 10.19, "carry_share_of_headline_pct": 8.9,
                                         "pp_per_100bp": 0.381, "cash_share": 0.5501}}},
              "identity": {"matched": True}}
        rp7 = os.path.join(cdt7, "regime.json")
        with open(rp7, "w", encoding="utf-8") as f:
            json.dump(rg, f)
        cs = carry_split(0.2, path=rp7)
        chk("leg43 the ticket reads the carry split at its own beta and re-derives the pp",
            bool(cs) and cs["beta"] == 0.2
            and abs(cs["carry_pp"] - 1.00) < 1e-6
            and abs(cs["flat_rate_cost_pp"] - 0.34) < 1e-6
            and abs(cs["carry_share_pct"] - 8.9) < 1e-6
            and cs["identity_matched"] is True,
            "carry=%s flat=%s" % (cs and cs["carry_pp"], cs and cs["flat_rate_cost_pp"]))
        chk("leg43b an off-grid beta snaps to the nearest published cell, never to the base",
            (carry_split(0.45, path=rp7) or {}).get("beta") == 0.2
            and (carry_split(0.12, path=rp7) or {}).get("beta") == 0.1, "")
        md7 = card(None, None, None, "2026-10-30", 0.2, {"inception": "2024-01-01", "carry": cs})
        chk("leg44 the sheet prints the split: headline / zero-cash / the pp it costs",
            "这条年化里有多少是现金利息" in md7 and "8.9%" in md7
            and "10.19%" in md7 and "1.00pp" in md7, "chars=%d" % len(md7))
        chk("leg44b a split priced on another bar is flagged, not quietly quoted",
            "\u26a0" in card(None, None, None, "2026-11-05", 0.2,
                             {"inception": "2024-01-01", "carry": cs})
            and "\u26a0" not in md7, "")
        chk("leg45 no artifact is disclosed on the sheet instead of leaving a bare headline",
            carry_split(0.2, path=os.path.join(cdt7, "absent.json")) is None
            and "拆解面在盘上没有可用读数" in card(None, None, None, "2026-10-30", 0.2,
                                          {"inception": "2024-01-01", "carry": None}), "")
        broken = dict(rg)
        broken["gate"] = {"base_beta": 0.2, "betas": {"0.2": {"observed_pct": 11.19}}}
        bp7 = os.path.join(cdt7, "broken.json")
        with open(bp7, "w", encoding="utf-8") as f:
            json.dump(broken, f)
        chk("leg45b a half-written cell returns None rather than an invented zero",
            carry_split(0.2, path=bp7) is None, "")
    finally:
        shutil.rmtree(cdt7, ignore_errors=True)

    # 46a-c. the sheet has to say which price panel its own numbers were computed on
    _pb_idx = pd.bdate_range("2026-01-01", periods=4)
    _pb_flip = pd.DataFrame({"A": [10.0, 10.0, 1.0, 1.05]}, index=_pb_idx)
    _pb_ok = price_basis(_pb_flip, ["A"])
    chk("leg46a price basis: a -90% print on the panel is counted and called out",
        _pb_ok["flip_prints"] == 1 and "1 处" in _pb_ok["sentence"]
        and _pb_ok["panel"].startswith("repaired"), _pb_ok["sentence"][:60])
    _pb_clean = pd.DataFrame({"B": [10.0, 10.1, 10.2, 10.3]}, index=_pb_idx)
    _pb_none = price_basis(_pb_clean, ["B"])
    chk("leg46b price basis: a panel with no flip says the repair would change nothing",
        _pb_none["flip_prints"] == 0 and "同一批数字" in _pb_none["sentence"], "")
    _pb_md = card(None, None, None, "2026-10-30", 0.2,
                  {"inception": "2024-01-01", "price_basis": _pb_ok})
    chk("leg46c price basis: the sheet prints the line (and nothing when it is absent)",
        "价格面板" in _pb_md and "1 处" in _pb_md
        and "价格面板" not in card(None, None, None, "2026-10-30", 0.2,
                                   {"inception": "2024-01-01"}), "")
    _pb_raw = price_basis(_pb_flip, ["A"], repaired=False)
    chk("leg46d price basis: the raw arm still exists and reads differently "
        "(the counterfactual the audit needs, not a second definition)",
        _pb_raw["panel"].startswith("raw") and _pb_raw["flip_prints"] == _pb_ok["flip_prints"]
        and _pb_raw["sentence"] != _pb_ok["sentence"], _pb_raw["sentence"][:60])
    chk("leg46e price basis: both faces quote ONE implementation "
        "(the sentence this sheet prints is the one etf_equity_alpha writes)",
        _pb_ok["sentence"] == AE.price_basis_line(
            True, _pb_ok["flip_prints"], _pb_ok["flip_thr"],
            _pb_ok["symbols_with_a_flip"], PRICE_BASIS_ARTIFACT,
            columns=_pb_ok.get("columns"))["sentence"], "")
    chk("leg46f this sheet repairs its panel (r1177): the module constant is on",
        REPAIR_PANEL is True, "")

    # 46g-h. a width without its license is a config, not a measurement (r1184). The sheet
    # quotes the family verdict; the three render states must be distinct on the page, or
    # "unproven" and "proven" look the same to the operator holding the sheet.
    _fc_one = {"verdict": "ONE_WORLD", "arms": 10, "panels": ["abc123"], "evidence_cutoff": "2026-10-30"}
    _fc_mixed = {"verdict": "MIXED_WORLDS", "arms": 10, "panels": ["a", "b"], "detail": "2 panels"}
    _md_one = card(None, None, None, "2026-10-30", 0.2,
                   {"inception": "2024-01-01", "family_coherence": _fc_one})
    _md_mixed = card(None, None, None, "2026-10-30", 0.2,
                     {"inception": "2024-01-01", "family_coherence": _fc_mixed})
    _md_absent = card(None, None, None, "2026-10-30", 0.2,
                      {"inception": "2024-01-01", "family_coherence": None})
    chk("leg46g family coherence: one world names the arm count and the panel",
        "名数的来历" in _md_one and "10 个宽度臂" in _md_one and "abc123" in _md_one
        and "2026-10-30" in _md_one, "")
    chk("leg46h family coherence: withheld and absent never read as a pass",
        "名数没被证过" in _md_mixed and "ONE_WORLD" not in _md_mixed
        and "名数没被证过" in _md_absent and "ONE_WORLD" not in _md_absent, "")

    # 46i. five names are not five sources of return either (r1190 / E298). The sheet must
    # quote the concentration face verbatim, and an absent/unreadable face must read as a
    # gap on the page -- "no line" would look identical to "not concentrated".
    _cq = {"status": "ok", "sentence": "前三名只占毛收益 22.1%（第一 a 7.5%）（判 BROAD）",
           "evidence_cutoff": "2026-10-30", "verdict": "BROAD|SURVIVES_WITHOUT_TOP3"}
    _md_cq = card(None, None, None, "2026-10-30", 0.2,
                  {"inception": "2024-01-01", "conc_line": _cq["sentence"]})
    _md_cq_miss = card(None, None, None, "2026-10-30", 0.2,
                       {"inception": "2024-01-01",
                        "conc_line": "where this book's return actually comes from is "
                                     "unpublished (absent); run scripts/etf_book_concentration.py run"})
    chk("leg46i concentration: the sheet quotes the face verbatim, and a missing face reads "
        "as a gap rather than silence",
        "这笔钱是从哪赚来的" in _md_cq and _cq["sentence"] in _md_cq
        and "这笔钱是从哪赚来的" in _md_cq_miss and "unpublished" in _md_cq_miss
        and "22.1%" not in _md_cq_miss, "")

    # 47a-e. the reference price must be the bar the operator pays (r1229). Same weights on
    # both arms, only the price row changes -- and a name with no print on the priced bar is
    # reported, never back-filled from the decision bar.
    _rp_score = pd.Series({"A": 2.0, "B": 1.0})
    _rp_dec = pd.Series({"A": 10.0, "B": 20.0})
    _rp_pay = pd.Series({"A": 11.0, "B": 20.0})
    _rp_tk = build_ticket(_rp_score, _rp_pay, 0.5, 100000.0, n_hold=2)
    _rp_lg = build_ticket(_rp_score, _rp_dec, 0.5, 100000.0, n_hold=2)
    _rp = reprice_block(_rp_lg, _rp_tk, pd.Timestamp("2026-10-14"), "2026-10-30")
    chk("leg47a reprice: the sheet prices the bar it is priced on (A at 11.0, not 10.0)",
        [r for r in _rp_tk["order"] if r["symbol"] == "A"][0]["price"] == 11.0
        and _rp["n_repriced"] == 1 and _rp["verdict"] == "REPRICED_TO_THE_BAR_YOU_PAY",
        _rp["sentence"][:70])
    chk("leg47b reprice: an unmoved name is not counted as a repricing, and the delta is "
        "the money difference under the same weights",
        abs(_rp["amount_delta_cny"]) > 0
        and [r for r in _rp["names"] if r["symbol"] == "B"][0]["drift_pct"] == 0.0, "")
    _rp_same = reprice_block(_rp_lg, _rp_lg, pd.Timestamp("2026-10-14"), "2026-10-14")
    chk("leg47c reprice: identical bars say so instead of inventing a drift",
        _rp_same["verdict"] == "SAME_PRICES_ON_BOTH_BARS" and _rp_same["n_repriced"] == 0
        and _rp_same["amount_delta_cny"] == 0.0, "")
    _rp_pay_missing = pd.Series({"A": 11.0})
    _rp_tk_miss = build_ticket(_rp_score, _rp_pay_missing, 0.5, 100000.0, n_hold=2)
    _rp_miss = reprice_block(_rp_lg, _rp_tk_miss, pd.Timestamp("2026-10-14"), "2026-10-30")
    chk("leg47d reprice: a missing print on the priced bar is reported and NOT filled from "
        "the decision bar (B stays unfilled)",
        _rp_miss["verdict"] == "PRICE_MISSING_ON_PRICED_BAR" and _rp_miss["missing"] == ["B"]
        and [r for r in _rp_tk_miss["order"] if r["symbol"] == "B"][0]["price"] is None, "")
    _rp_md = card(_rp_tk, None, None, "2026-10-30", 0.2,
                  {"inception": "2024-01-01", "reprice": _rp})
    chk("leg47e reprice: the sheet prints the two price bars, the verdict and the per-name "
        "drift (and says nothing when the block is absent)",
        "参考价用的是哪一天" in _rp_md and "2026-10-14" in _rp_md
        and "REPRICED_TO_THE_BAR_YOU_PAY" in _rp_md and "+10.00%" in _rp_md
        and "参考价用的是哪一天" not in card(_rp_tk, None, None, "2026-10-30", 0.2,
                                            {"inception": "2024-01-01"}), "")

    # r1248: 选票的那道闸必须在票面上说话。三条腿分开打：①渲染器两轴都印（夹具值来自载荷，
    # 不是写死的常数）；②容量那句在宽度不动时消失；③票面真的带上这一节，缺席时不印假话。
    _eg_ok = {"status": "ok", "shipped_cny": 20e6, "verdict": "GATE_SITS_ON_PLATEAU",
              "near_max_pp": 1.53, "best_delta_pp": 0.21, "tol_pp": 1.0,
              "width_ratio": 8.25, "widest_names": 462, "narrowest_names": 56,
              "artifact": "results/etf_book_entry_gate.json",
              "evidence_cutoff": "2026-10-30", "panel_last_bar": "2026-10-30",
              "control": {"delta_pp": 0.0, "tol_pp": 0.25}}
    _eg_md = "\n".join(entry_gate_md(_eg_ok))
    chk("leg48a entry gate: the sheet prints BOTH axes from the payload it was given",
        "<=1.53 pp" in _eg_md.replace("≤", "<=") and "462" in _eg_md
        and "56" in _eg_md and "容量来源" in _eg_md and "GATE_SITS_ON_PLATEAU" in _eg_md,
        _eg_md[:80])
    chk("leg48b entry gate: no capacity sentence when the knob does not move width",
        "容量来源" not in "\n".join(entry_gate_md(
            dict(_eg_ok, width_ratio=1.2, widest_names=70, narrowest_names=60))))
    chk("leg48c entry gate: a refused face refuses in words, never a plateau claim",
        "这一问答不了" in "\n".join(entry_gate_md({"status": "drifted",
                                                   "detail": "no control arm"}))
        and "平台" not in "\n".join(entry_gate_md({"status": "drifted",
                                                   "detail": "no control arm"})))
    _tk_min = {"nav": 1_000_000.0, "beta_k": 0.2, "book_weight": 0.2, "cash_weight": 0.8,
               "cash_leg": "GC001 (1-day repo, observed close)", "cash_amount": 800_000.0,
               "order": [], "underspend_pct": 0.0}
    _tk_md = card(_tk_min, None, None, "2026-10-30", 0.2,
                  {"inception": "2024-01-01", "entry_gate": _eg_ok})
    _tk_absent = card(_tk_min, None, None, "2026-10-30", 0.2, {"inception": "2024-01-01"})
    chk("leg48d entry gate: the sheet carries the section, and an absent face says it "
        "cannot be answered instead of vanishing",
        "这本书能买哪些票" in _tk_md and "容量来源" in _tk_md
        and "这一问答不了" in _tk_absent and "容量来源" not in _tk_absent)

    # 49a-e. r1455: the sheet sizes to the permission the desk itself published. r1450
    # printed a floor (k=0.393073) and its prereg requirement 4 asked for it to be carried
    # into the 11-11 ticket with the unused readings beside it; nobody read it, so the file
    # a desk executes ordered 6.72pp more than the file that authorises it. Legs: the trim
    # exists and lands under the floor / the unused readings are the ones NOT chosen /
    # inside the floor prints nothing to sell / a missing receipt is UNKNOWN not a pass /
    # the section actually reaches the page.
    _pb_tk = {"nav": 100000.0, "beta_k": 0.50, "book_weight": 0.50, "cash_weight": 0.50,
              "cash_leg": "GC001 (1-day repo, observed close)", "cash_amount": 50000.0,
              "underspend_pct": 0.0,
              "order": [{"symbol": "A", "price": 3.33, "lots": 75, "shares": 7500,
                         "amount": 24975.0, "weight": 0.25, "class": "equity"},
                        {"symbol": "B", "price": 3.33, "lots": 75, "shares": 7500,
                         "amount": 24975.0, "weight": 0.25, "class": "equity"}]}
    _pb_perm = {"decision_date": "2026-11-11", "permitted_k": 0.40, "k_now": 0.50,
                "naive_max_over_all_readings": {"k": 0.55},
                "readings": {"baseline_published": {"k": 0.50, "kind": "circular",
                                                    "delta_vs_now_pp": 0.0},
                             "window": {"k": 0.412, "kind": "path", "delta_vs_now_pp": -4.76},
                             "universe": {"k": 0.432, "kind": "path", "delta_vs_now_pp": -2.81},
                             "window_x_universe": {"k": 0.40, "kind": "path",
                                                   "delta_vs_now_pp": -6.72},
                             "denominator": {"k": 0.544, "kind": "static",
                                             "delta_vs_now_pp": 8.42}}}
    _pb = permission_block(_pb_tk, _pb_perm)
    chk("leg49a permission: an order over the floor carries the integer-lot trim, and the "
        "trim lands at or below the floor (never rounded back over it)",
        _pb["status"] == "trim_required" and _pb["verdict"] == "TRIM_REQUIRED"
        and _pb["trim"]["lots_sell_total"] == 30 and _pb["trim"]["k_after"] <= 0.40 + 1e-9
        and [r["lots_target"] for r in _pb["trim"]["legs"]] == [60, 60],
        "k_after=%.6f" % _pb["trim"]["k_after"])
    chk("leg49b permission: the unused readings are the ones the order did NOT choose "
        "(three of them here, and never the floor or the size in force)",
        len(_pb["unused_readings"]) == 3
        and {u["ruler"] for u in _pb["unused_readings"]} == {"window", "universe", "denominator"}, "")
    _pb_in = permission_block(dict(_pb_tk, beta_k=0.35), _pb_perm)
    _pb_in_md = "\n".join(permission_md(_pb_in))
    chk("leg49c permission: inside the floor there is nothing to sell and the page says so",
        _pb_in["verdict"] == "WITHIN_PERMISSION" and _pb_in["trim"] is None
        and "卖出合计" not in _pb_in_md and "WITHIN_PERMISSION" in _pb_in_md, "")
    _pb_unk = permission_block(_pb_tk, None)
    _pb_unk_md = "\n".join(permission_md(_pb_unk))
    chk("leg49d permission: a missing receipt reads as UNKNOWN, never as a pass",
        _pb_unk["status"] == "unreadable" and "无法核验" in _pb_unk_md
        and "WITHIN_PERMISSION" not in _pb_unk_md and "卖出合计" not in _pb_unk_md, "")
    _pb_md = "\n".join(permission_md(_pb))
    chk("leg49e permission: the sheet carries the section, and an absent block prints "
        "nothing rather than a blank claim",
        "按谁的额度下单" in _pb_md and "TRIM_REQUIRED" in _pb_md and "不可执行" in _pb_md
        and "按谁的额度下单" not in card(_pb_tk, None, None, "2026-11-30", 0.2,
                                         {"inception": "2024-01-01"})
        and "按谁的额度下单" in card(_pb_tk, None, None, "2026-11-30", 0.2,
                                    {"inception": "2024-01-01", "permission": _pb}), "")
    _pb_cf = permission_block(_pb_tk, _pb_perm, {"k_floor": 0.45})
    _pb_cf_md = "\n".join(permission_md(_pb_cf))
    chk("leg49f permission: two published faces quoting different floors are printed as a "
        "CONFLICT, and the sheet stops claiming it obeys the permission",
        _pb_cf["status"] == "conflict" and _pb_cf["verdict"] == "PERMISSION_FACES_CONFLICT"
        and "矛盾" in _pb_cf_md and "PERMISSION_FACES_CONFLICT" in _pb_cf_md, "")

    # 50a-c. r1457: the sheet carries whether the floor is still in force on the PATH,
    # not only whether this one sheet was trimmed. A trim printed here is not obedience
    # on the next decision bar (r1456: the schedule carries no memory of it).
    _fl_re = {"assessed": {"verdict": "REAPPLY_REQUIRED", "floor": 0.393073,
                           "floor_issued": "2026-11-11", "k_schedule_last": 0.460253,
                           "action": "apply the trim again on the next decision bar"}}
    _fl_re_md = "\n".join(floor_ledger_md(_fl_re))
    chk("leg50a floor ledger: a floor the path no longer satisfies is printed on the sheet "
        "as REAPPLY_REQUIRED, with the action",
        "REAPPLY_REQUIRED" in _fl_re_md and "重新裁剪" in _fl_re_md
        and "apply the trim again" in _fl_re_md, "")
    _fl_none_md = "\n".join(floor_ledger_md(None))
    chk("leg50b floor ledger: a missing ledger reads as UNVERIFIABLE, never as compliance",
        "无法核验" in _fl_none_md and "REAPPLY_REQUIRED" not in _fl_none_md, "")
    _fl_h = {"assessed": {"verdict": "HOLDING", "floor": 0.393073,
                          "floor_issued": "2026-11-11", "k_schedule_last": 0.38}}
    _fl_h_md = "\n".join(floor_ledger_md(_fl_h))
    chk("leg50c floor ledger: HOLDING says the path itself is under the floor and no re-trim "
        "is needed",
        "HOLDING" in _fl_h_md and "无需再裁剪" in _fl_h_md, "")

    # 51a-b. r1466: the sheet that carries the swap has to carry the trigger too, and an
    # absent trigger face prints one line instead of an empty section that reads as
    # "there is nothing to watch".
    _sw = {"criteria": {"toll_pp": 0.16}, "recheck_rule": "act on this bar: ...",
           "pairs": [{"leg_symbol": "159501", "sibling_symbol": "159513",
                      "today_gap_pp": 8.6708, "mean_gap_pp": 0.8316,
                      "one_off_gain_cny": 5038.7, "repeatable_gain_cny": 573.8,
                      "window_share": 0.6343, "source_verdict": "SWAP_SAVES",
                      "expiry": {"n_completed": 0, "n_censored": 1, "median_sessions": None},
                      "verdict": "ACT_ON_THIS_BAR"},
                     {"leg_symbol": "159577", "sibling_symbol": "513850",
                      "today_gap_pp": 0.19, "mean_gap_pp": -0.0758,
                      "one_off_gain_cny": None, "repeatable_gain_cny": None,
                      "window_share": 0.3948, "source_verdict": "GAP_IMMATERIAL",
                      "expiry": {"n_completed": 27, "n_censored": 1, "median_sessions": 3.0},
                      "verdict": "NOT_ACTIONABLE"}]}
    _sw_md = "\n".join(swap_trigger_md(_sw))
    chk("leg51a swap trigger: the sheet states when to look again, a censored episode is "
        "printed as unmeasured (not 0 sessions), and an immaterial pair is not priced at 0",
        "换票之后什么时候再看一次" in _sw_md and "未测" in _sw_md
        and "ACT_ON_THIS_BAR" in _sw_md and "钱不单列" in _sw_md
        and " volte" not in _sw_md, "")
    chk("leg51b swap trigger: an absent face prints one line, never a silent pass",
        "这一问答不了" in "\n".join(swap_trigger_md(None))
        and "换票之后什么时候再看一次" in "\n".join(swap_trigger_md(None)), "")

    _st = {"verdict": "TWO_SECTIONS_OVERSELL_THE_LEG", "lot_residue_cny": 106.3,
           "actions": [{"side": "SELL", "symbol": "159501", "price": 2.069, "lots": 379,
                        "amount_cny": 78415.1},
                       {"side": "BUY", "symbol": "159513", "price": 1.705, "lots": 920,
                        "amount_cny": 156860.0}],
           "oversell": [{"symbol": "159501", "held": 444, "trim_sells": 65, "swapped": True,
                         "swap_sells": 444, "sections_add_up_to": 509,
                         "as_printed_excess": 65}],
           "swap_repricing": [{"leg": "159501", "sibling": "159513", "gain_published_cny": 5612.5,
                               "gain_on_trimmed_book_cny": 4791.3}],
           "overstated_total_cny": 1425.9,
           "widest_name": {"symbol": "159513", "share_of_risk_book": 0.3998},
           "baskets": {"n_before": 4, "n_after": 4}}
    _st_md = "\n".join(swap_stack_md(_st))
    chk("leg51c swap stack: the sheet prints the netted order and the lot count both sections "
        "would sell, instead of leaving two sections that disagree",
        "这张单真正要下的是一笔还是两笔" in _st_md and "159513" in _st_md
        and "多卖 **65 手**" in _st_md and "高估" in _st_md, "")
    chk("leg51d swap stack: an absent face prints one line, never a silent pass",
        "这一问答不了" in "\n".join(swap_stack_md(None)), "")

    _pos = {"verdict": "PRINTED_ROWS_UNDERSELL_THE_BOOK", "unexplained_total_cny": 67289.1,
            "unexplained": [{"symbol": "159501", "sheet_lots": 444, "printed_lots": 65,
                             "book_lots": 0, "delta_lots": 65, "delta_cny": 13448.5}],
            "next_order_base": {"bar": "2026-11-06", "risk_book_cny": 392400.9,
                                "cash_cny": 607599.1, "holdings": 4},
            "base_divergence_total_cny": 381115.4}
    _pos_md = "\n".join(positions_md(_pos))
    chk("leg51e positions: the sheet says how many printed lots are missing and in what money, "
        "and that the next order starts from the written book",
        "打印的动作能不能凑成账上的书" in _pos_md and "¥67,289" in _pos_md
        and "**+65 手**" in _pos_md and "下一张单从这本账起算" in _pos_md, "")
    chk("leg51f positions: an absent face prints one line, never a silent pass",
        "这一问答不了" in "\n".join(positions_md(None)), "")

    _base = {"status": "ok", "face": POSITIONS_FACE, "bar": "2026-11-06",
             "risk_book_cny": 392400.9, "cash_cny": 607599.1, "nav_cny": 1000000.0,
             "k_executed": 0.392401, "k_engine": 0.460253, "holdings": 4,
             "k_gap": 0.067852, "notional_gap_cny": 67852.0}
    _base_md = "\n".join(executed_base_md(_base))
    chk("leg51g base: the sheet says which book it sized from and prices the rule-vs-account "
        "gap in CNY instead of leaving it one document away",
        "这张单从哪一本账起算" in _base_md and "0.392401" in _base_md
        and "¥67,852" in _base_md and "本单的手数按执行账裁" in _base_md, "")
    chk("leg51h base: a stale or missing account never silently becomes the base",
        "这一问答不了" in "\n".join(executed_base_md(
            {"status": "absent", "sentence": "x", "face": POSITIONS_FACE}))
        and "不能用这本账起算" in "\n".join(executed_base_md(
            {"status": "stale", "sentence": "x", "face": POSITIONS_FACE})), "")
    _bt = build_ticket(pd.Series({"A": 2.0, "B": 1.0}), pd.Series({"A": 10.0, "B": 20.0}),
                       0.5, 100000.0, n_hold=2, k_rule=0.6)
    chk("leg51i base: the ticket carries both the size it orders and the size the rule alone "
        "would pick, so a reader can tell them apart",
        _bt and abs(_bt["beta_k"] - 0.5) < 1e-9 and abs(_bt["beta_k_rule"] - 0.6) < 1e-9, "")

    # r1476: the fixed point. A ledger row written by the bar being priced is this ticket's
    # own outcome; feeding it back is a monotone descent (0.389744 -> 0.389298 -> 0.388680).
    _same = sizing_level({"status": "ok", "bar": "2026-11-06", "k_executed": 0.388680},
                         "2026-11-06", 0.393073)
    _prev = sizing_level({"status": "ok", "bar": "2026-10-14", "k_executed": 0.388680},
                         "2026-11-06", 0.393073)
    chk("leg51j sizing: a ledger row for the bar being priced cannot size that bar (it is "
        "the ticket's own outcome), while a row from an earlier bar still can",
        abs(_same["k"] - 0.393073) < 1e-9 and _same["source"] == "rule_same_bar_outcome"
        and abs(_prev["k"] - 0.388680) < 1e-9 and _prev["source"] == "executed", "")
    # two reruns of one bar must land on the SAME k -- the descent r1475 measured, pinned.
    _k = 0.393073
    _drift = []
    for _ in range(3):
        _sz = sizing_level({"status": "ok", "bar": "2026-11-06", "k_executed": _k},
                           "2026-11-06", 0.393073)
        _drift.append(round(_sz["k"], 6))
        _k = round(_sz["k"] - 0.0006, 6)      # what the floor does to the executed k
    chk("leg51k sizing: three reruns of one bar cannot ratchet the ordered size downwards",
        len(set(_drift)) == 1, str(_drift))
    chk("leg51l sizing: the sheet PRINTS which of the two rules it used, so an operator can "
        "see a same-bar refusal instead of a silently smaller order",
        "本单的 k 不取这本账" in "\n".join(executed_base_md(
            dict(_base, sizing=_same)))
        and "本单按执行账" in "\n".join(executed_base_md(
            dict(_base, sizing=sizing_level({"status": "ok", "bar": "2026-10-14",
                                             "k_executed": 0.392401},
                                            "2026-11-06", 0.460253)))), "")

    _cap = sizing_level({"status": "ok", "bar": "2026-11-06", "k_executed": 0.388680},
                        "2026-11-06", 0.460253, floor=0.393073)
    chk("leg51m sizing: the ordered level is the authorized one -- the rule's k capped by "
        "the permission floor, so the sheet does not print a sell table for names the "
        "account never held",
        abs(_cap["k"] - 0.393073) < 1e-9 and _cap.get("capped_by_floor") is True
        and abs(sizing_level({"status": "ok", "bar": "2026-10-14", "k_executed": 0.30},
                             "2026-11-06", 0.460253, floor=0.393073)["k"] - 0.30) < 1e-9, "")

    # r1478: the band on the sheet. A pinned band that nothing prints is a config file.
    _pre = {"band": {"inside_pp": 10.43, "warn_pp": 20.86, "noise_pp": 10.43,
                     "production_effect": "advisory in v1"}
            if True else {}}
    _bb_ok = band_block(0.393073, "2026-11-06", _pre,
                        {"permitted_k": 0.393073}, {"k_now": 0.393073})
    chk("leg51n band: a k that sits on the signed floor reads inside, and the sheet prints "
        "the three numbers it was decided from",
        _bb_ok["zone"] == "inside" and _bb_ok["verdict"] == "WITHIN_BAND"
        and abs(_bb_ok["drift_pp"]) < 1e-9, str(_bb_ok.get("zone")))
    _pre2 = dict(_pre)
    _bb_miss = band_block(0.393073, "2026-11-06", {"band": {}}, {"permitted_k": 0.393073},
                          {"k_now": 0.393073})
    chk("leg51o band: a prereg without a published noise value reads as 'cannot answer', "
        "never as a pass -- the band has no default",
        _bb_miss["status"] == "unreadable"
        and "这一问答不了" in _bb_miss["sentence"], str(_bb_miss.get("sentence")))
    _bb_warn = band_block(0.393073, "2026-11-06", _pre2, {"permitted_k": 0.393073},
                          {"k_now": 0.513073})          # +12.00pp
    _bb_out = band_block(0.393073, "2026-11-06", _pre2, {"permitted_k": 0.393073},
                         {"k_now": 0.623073})            # +23.00pp
    chk("leg51p band: warn and outside are separated by the ruler's own 2 sd, and only "
        "outside asks for a receipt",
        _bb_warn["zone"] == "warn" and _bb_warn["verdict"] == "BAND_WARN"
        and _bb_warn.get("receipt") is None
        and _bb_out["zone"] == "outside" and _bb_out["verdict"] == "BAND_EXCEEDED"
        and (_bb_out.get("receipt") or {}).get("status") in ("ok", "unreadable"), "")
    # the flattering number is not the one that decides: ticket k can be on the floor while
    # the ruler itself has moved away from it.
    _bb_two = band_block(0.393073, "2026-11-06", _pre2, {"permitted_k": 0.393073},
                         {"k_now": 0.619073})            # fresh +22.6pp, ticket 0.0pp
    chk("leg51q band: the zone comes from the WORSE of the two distances -- a ticket that "
        "obeys the old floor while the ruler has moved is not reported as inside",
        _bb_two["zone"] == "outside" and abs(_bb_two["ticket_gap_pp"]) < 1e-9
        and abs(_bb_two["drift_pp"] - 22.6) < 1e-6, str(_bb_two.get("worst_pp")))
    # the re-issue list is scanned off the published tree, so a face that carries the floor
    # appears and a face that does not stays out.
    import tempfile
    _tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(_tmp, "sub"))
    with open(os.path.join(_tmp, "carries.json"), "w", encoding="utf-8") as f:
        json.dump({"permitted_k": 0.393073, "note": "x"}, f)
    with open(os.path.join(_tmp, "sub", "does_not.json"), "w", encoding="utf-8") as f:
        json.dump({"cagr": 0.393073, "k_label": "not a k value here"},
                  f)
    _qf = floor_quoting_faces(_tmp, 0.393073)
    chk("leg51r band: the re-issue list is derived by reading the published faces -- a face "
        "carrying the floor is named, a face holding the same digits under a non-k key is "
        "not",
        _qf["n"] == 1 and _qf["faces"][0]["face"].endswith("carries.json")
        and all("does_not" not in f["face"] for f in _qf["faces"]), str(_qf.get("faces")))
    chk("leg51s band: the printed section carries the band, the distances and the read-only "
        "promise, so the sheet cannot look silent about a drift",
        "这张单的 k 离签发的尺子有多远" in "\n".join(band_md(_bb_out))
        and "只读" in "\n".join(band_md(_bb_out))
        and "无法核验" in "\n".join(band_md(_bb_miss)), "")
    chk("leg51t band: a 0.000pp distance is labelled as constructed (the sheet's k IS the "
        "signed floor) instead of being read as a ruler that was re-read and agreed",
        _bb_ok.get("zero_is_structural") is True
        and "构造出来的，不是量出来的" in "\n".join(band_md(_bb_ok))
        and _bb_two.get("zero_is_structural") is False
        and "构造出来的，不是量出来的" not in "\n".join(band_md(_bb_two)), "")

    # ---- r1483: a ledger bar the price panel no longer carries must be withdrawn ----
    import tempfile as _tf
    _wd_dir = _tf.mkdtemp()
    _wd_idx = pd.DatetimeIndex(["2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06"])
    with open(os.path.join(_wd_dir, "ledger.jsonl"), "w", encoding="utf-8") as f:
        for _d, _nav, _k in (("2026-11-04", 1.10, 0.5), ("2026-11-05", 1.11, 0.46),
                             ("2026-11-06", 1.12, 0.46), ("2026-11-09", 1.13, 0.46)):
            f.write(json.dumps({"date": _d, "nav": _nav, "ret": 0.001, "k": _k,
                                "k_cost": 0.0, "rf": 0.0, "decision": ""}) + "\n")
    _wd_state = {"inception": "2024-01-01", "beta_target": 0.2, "last_bar": "2026-11-09",
                 "last_k": 0.46, "nav": 1.13, "rows": 4}
    _st2, _bad2, _info2 = withdraw_unsupported_bars(_wd_state, _wd_idx, out_dir=_wd_dir,
                                                    now="2026-11-09T23:00:00")
    _rows2 = [json.loads(l) for l in open(os.path.join(_wd_dir, "ledger.jsonl"),
                                          encoding="utf-8") if l.strip()]
    _wrec = json.load(open(os.path.join(_wd_dir, "withdrawals.json"), encoding="utf-8"))
    chk("leg52a withdraw: a bar the panel stopped carrying is cut, not carried",
        [r["date"] for r in _bad2] == ["2026-11-09"]
        and [r["date"] for r in _rows2] == ["2026-11-04", "2026-11-05", "2026-11-06"]
        and _st2["last_bar"] == "2026-11-06" and abs(_st2["nav"] - 1.12) < 1e-12
        and _st2["rows"] == 3 and _info2["supported"] is False,
        "bars=%s state=%s nav=%.4f" % ([r["date"] for r in _rows2], _st2["last_bar"], _st2["nav"]))
    chk("leg52b withdraw: the cut is recorded with the values it removed, and a sentence "
        "carries it to the sheet",
        len(_wrec) == 1 and _wrec[0]["withdrawn"][0]["date"] == "2026-11-09"
        and _wrec[0]["panel_last"] == "2026-11-06"
        and "2026-11-09" in (withdrawals_line(out_dir=_wd_dir) or ""),
        str((_wrec[0].get("withdrawn") or [{}])[0].get("date")))
    _st3, _bad3, _info3 = withdraw_unsupported_bars(
        {"last_bar": "2026-11-06", "nav": 1.12, "last_k": 0.46, "rows": 3}, _wd_idx,
        out_dir=_wd_dir)
    chk("leg52c withdraw: a supported state is untouched (no rows cut, no second record)",
        not _bad3 and _info3["supported"] is True and len(_rows2) == 3
        and _st3["last_bar"] == "2026-11-06"
        and len(json.load(open(os.path.join(_wd_dir, "withdrawals.json"),
                               encoding="utf-8"))) == 1, str(_bad3))

    # 52d/52e: the record may not describe the present -- read the ledger, not the log
    _rec2 = _tf.mkdtemp()
    with open(os.path.join(_rec2, "withdrawals.json"), "w", encoding="utf-8") as f:
        json.dump([{"withdrawn": [{"date": "2026-11-09", "nav": 1.13}],
                    "reason": "panel ended", "panel_last": "2026-11-06",
                    "state_rewound_to": "2026-11-06", "at": "2026-11-09 23:54:02"}], f)
    with open(os.path.join(_rec2, "ledger.jsonl"), "w", encoding="utf-8") as f:
        for _d in ("2026-11-06", "2026-11-09"):
            f.write(json.dumps({"date": _d, "nav": 1.12, "ret": 0.0, "k": 0.46}) + "\n")
    _line_back = withdrawals_line(out_dir=_rec2) or ""
    with open(os.path.join(_rec2, "ledger.jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps({"date": "2026-11-06", "nav": 1.12, "ret": 0.0, "k": 0.46}) + "\n")
    _line_gone = withdrawals_line(out_dir=_rec2) or ""
    chk("leg52d withdraw: a bar that came back is reported as live, not as a state that is "
        "still rewound (the 11-09 sheet printed the rewind while priced on 11-09)",
        "is live" in _line_back and "priced on the panel's own last bar" not in _line_back
        and "2026-11-09" in _line_back, _line_back)
    chk("leg52e withdraw: a bar that is still gone keeps the rewind sentence, so the two "
        "cases cannot read the same",
        "priced on the panel's own last bar" in _line_gone and "is live" not in _line_gone,
        _line_gone)

    # ---- r1489: a bar that came back must be RE-DERIVED from the panel, not carried ----
    _nav_ok = round(1.12 * (1.0 + 0.46 * 0.001 + 0.54 * 0.0001), 8)

    def _ri_fixture(row_nav, row_ret, drop_rp=False):
        d = _tf.mkdtemp()
        with open(os.path.join(d, "withdrawals.json"), "w", encoding="utf-8") as f:
            json.dump([{"withdrawn": [{"date": "2026-11-09", "nav": _nav_ok,
                                       "ret": 0.000514, "k": 0.46}],
                        "reason": "panel ended", "panel_last": "2026-11-06",
                        "state_rewound_to": "2026-11-06", "at": "2026-11-09 23:54:02"}], f)
        with open(os.path.join(d, "ledger.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"date": "2026-11-06", "nav": 1.12, "ret": 0.0, "k": 0.46}) + "\n")
            f.write(json.dumps({"date": "2026-11-09", "nav": row_nav, "ret": row_ret,
                                "k": 0.46}) + "\n")
            f.write(json.dumps({"date": "2026-11-10", "nav": 1.13, "ret": 0.0, "k": 0.46}) + "\n")
        ix = pd.DatetimeIndex(["2026-11-06", "2026-11-09", "2026-11-10"])
        _rp = pd.Series([0.0, 0.001, 0.0], index=ix)
        if drop_rp:
            _rp = _rp.drop(pd.Timestamp("2026-11-09"))
        return d, _rp, pd.Series([0.0, 0.0001, 0.0], index=ix), \
            pd.Series([0.46, 0.46, 0.46], index=ix)

    _dA, _rpA, _rfA, _kA = _ri_fixture(_nav_ok, 0.000514)
    _riA = reinstatement_check(_rpA, _rfA, _kA, out_dir=_dA, now="2026-11-10T03:30:00")
    _rowsA = _read_jsonl(os.path.join(_dA, "ledger.jsonl"))
    chk("leg52f reinstated: a bar that came back re-derives to the same number and is "
        "recorded as identical to both the ledger row and the row that was cut",
        _riA and _riA["records"][0]["status"] == "RECOMPUTED_IDENTICAL"
        and abs(_riA["records"][0]["nav_delta"]) <= 1e-9
        and _riA["records"][0]["same_as_withdrawn"] is True
        and not _riA["rewritten"]
        and len(_rowsA) == 3 and abs(_rowsA[1]["nav"] - _nav_ok) < 1e-12
        and "重算值不是旧副本" in "\n".join(reinstatement_md(_riA)), str(_riA))

    _dB, _rpB, _rfB, _kB = _ri_fixture(1.13, 0.0)
    _riB = reinstatement_check(_rpB, _rfB, _kB, out_dir=_dB, now="2026-11-10T03:30:00")
    _rowsB = _read_jsonl(os.path.join(_dB, "ledger.jsonl"))
    _fac = _nav_ok / 1.13
    chk("leg52g reinstated: a carried row that disagrees with the panel is rewritten, "
        "marked restated_at, and the later nav is rescaled so the chain stays consistent",
        _riB and _riB["records"][0]["status"] == "REWRITTEN_FROM_PANEL"
        and _riB["rewritten"] == ["2026-11-09"]
        and abs(_rowsB[1]["nav"] - _nav_ok) < 1e-8
        and _rowsB[1].get("restate_reason", "").startswith("reinstated bar")
        and abs(_rowsB[2]["nav"] - round(1.13 * _fac, 8)) < 1e-8
        and _rowsB[2].get("restated_at") is None
        and "账本行与面板重算不一致" in "\n".join(reinstatement_md(_riB)), str(_rowsB))

    _dC, _rpC, _rfC, _kC = _ri_fixture(_nav_ok, 0.000514, drop_rp=True)
    _riC = reinstatement_check(_rpC, _rfC, _kC, out_dir=_dC, now="2026-11-10T03:30:00")
    chk("leg52h reinstated: a bar whose panel inputs are missing is named UNVERIFIABLE and "
        "left untouched (an unproven row is never silently blessed)",
        _riC and _riC["records"][0]["status"] == "UNVERIFIABLE"
        and _riC["records"][0]["missing"]
        and not _riC["rewritten"]
        and abs(_read_jsonl(os.path.join(_dC, "ledger.jsonl"))[1]["nav"] - _nav_ok) < 1e-12
        and "无法核验" in "\n".join(reinstatement_md(_riC)), str(_riC))

    # ---- r1490: the rewrite must keep BOTH numbers on the row, and a later run must say so ----
    _dD, _rpD, _rfD, _kD = _ri_fixture(1.13, 0.0)
    _riD = reinstatement_check(_rpD, _rfD, _kD, out_dir=_dD, now="2026-11-10T03:30:00")
    _rowsD = _read_jsonl(os.path.join(_dD, "ledger.jsonl"))
    chk("leg52i reinstated: a rewritten row keeps what was published (nav_published/"
        "ret_published) on the row itself, so the old number survives the next run",
        _riD and _riD["records"][0]["status"] == "REWRITTEN_FROM_PANEL"
        and abs(float(_rowsD[1]["nav_published"]) - 1.13) < 1e-12
        and _rowsD[1]["ret_published"] == 0.0
        and abs(float(_rowsD[1]["nav"]) - _nav_ok) < 1e-8
        and _rowsD[1].get("restated_at") == "2026-11-10T03:30:00"
        and _rowsD[1].get("later_rows_rescaled") == 1
        and _riD["records"][0].get("chain_intact") is True, str(_rowsD))

    # second run: the row now agrees with the panel, and the sheet must still print its history
    _riD2 = reinstatement_check(_rpD, _rfD, _kD, out_dir=_dD, now="2026-11-11T03:30:00")
    _mdD2 = "\n".join(reinstatement_md(_riD2))
    chk("leg52j reinstated: on a later run an already-restated bar reports its published and "
        "settled values instead of reading as 'never moved'",
        _riD2 and _riD2["records"][0]["status"] == "RECOMPUTED_IDENTICAL"
        and _riD2["settled_restated"] == ["2026-11-09"]
        and (_riD2["records"][0].get("settled_restated") or {}).get("published_nav") == 1.13
        and "定格后被改述过" in _mdD2 and "1.13000000" in _mdD2, str(_riD2))

    _hist = reinstated_history(os.path.join(_dD, "ledger.jsonl"))
    _mdH = "\n".join(reinstated_history_md(_hist))
    chk("leg52k reinstated: the sheet's ledger-history block reads the LEDGER ROWS (not the "
        "per-run reinstatements.json) and prints published vs settled plus the chain verdict",
        _hist.get("readable") is True and _hist["bars"] == ["2026-11-09"]
        and _hist["records"][0]["nav_published"] == 1.13
        and not _hist["chain_broken"]
        and "发布时 NAV" in _mdH and "1.13000000" in _mdH
        and "链条校验" in _mdH, str(_hist))

    # a chain that no longer compounds must be named, never printed as a dash
    _dE, _rpE, _rfE, _kE = _ri_fixture(1.13, 0.0)
    reinstatement_check(_rpE, _rfE, _kE, out_dir=_dE, now="2026-11-10T03:30:00")
    _rowsE = _read_jsonl(os.path.join(_dE, "ledger.jsonl"))
    _rowsE[2]["nav"] = round(float(_rowsE[2]["nav"]) * 1.01, 8)      # break the chain on purpose
    with open(os.path.join(_dE, "ledger.jsonl"), "w", encoding="utf-8") as f:
        for _r in _rowsE:
            f.write(json.dumps(_r, ensure_ascii=False) + "\n")
    _histE = reinstated_history(os.path.join(_dE, "ledger.jsonl"))
    _mdE = "\n".join(reinstated_history_md(_histE))
    chk("leg52l reinstated: a ledger whose restated bar no longer compounds says so "
        "(expected vs ledger printed), it does not print a clean chain",
        _histE and len(_histE["chain_broken"]) == 1
        and "链条没接上" in _mdE, (_mdE[-300:] if _mdE else str(_histE)))

    # the gate must not read 8-decimal rounding as a broken chain (measured on the real
    # 2026-11-06 row: expected 1.46125781 vs rescaled ledger 1.46125782 = 1e-8, after a
    # genuinely correct rescale)
    _dF = _tf.mkdtemp()
    with open(os.path.join(_dF, "withdrawals.json"), "w", encoding="utf-8") as f:
        json.dump([{"withdrawn": [{"date": "2026-11-06", "nav": 1.45936114, "ret": -0.00874174,
                                   "k": 0.460253}],
                    "reason": "panel ended", "panel_last": "2026-11-05",
                    "state_rewound_to": "2026-11-05", "at": "2026-11-06T23:54:02"}], f)
    with open(os.path.join(_dF, "ledger.jsonl"), "w", encoding="utf-8") as f:
        for _d, _n, _r, _k in (("2026-11-03", 1.472231, 0.0, 0.460253),
                               ("2026-11-04", 1.472231, 0.0, 0.460253),
                               ("2026-11-05", 1.472231, 0.0, 0.460253),
                               ("2026-11-06", 1.45936114, -0.00874174, 0.460253),
                               ("2026-11-09", 1.45787328, -0.00101953, 0.460253)):
            f.write(json.dumps({"date": _d, "nav": _n, "ret": _r, "k": _k}) + "\n")
    _rpF = pd.Series([0.0, 0.0, 0.0, (-0.00874174 / 0.460253) + 0.005, 0.0],
                     index=pd.DatetimeIndex(["2026-11-03", "2026-11-04", "2026-11-05",
                                             "2026-11-06", "2026-11-09"]))
    _rfF = pd.Series([0.0] * 5, index=_rpF.index)
    _kF = pd.Series([0.460253] * 5, index=_rpF.index)
    _riF = reinstatement_check(_rpF, _rfF, _kF, out_dir=_dF, now="2026-11-10T04:10:00")
    _rowsF = _read_jsonl(os.path.join(_dF, "ledger.jsonl"))
    _gapF = abs(round(float(_rowsF[3]["nav"]) * (1.0 + float(_rowsF[4]["ret"])), 8)
                - float(_rowsF[4]["nav"]))
    chk("leg52m reinstated: a correct rescale whose 8-decimal rounding leaves a 1e-8 gap is "
        "read as an intact chain (the gate scales with rounding, it does not print a false red)",
        _riF and _riF["records"][0]["status"] == "REWRITTEN_FROM_PANEL"
        and _riF["records"][0].get("chain_intact") is True
        and _gapF > 1e-9 and _gapF < 1e-7
        and not _riF["chain_broken"], "gap=%.3e rec=%s" % (_gapF, _riF["records"][0]))

    print("selftest:", "PASS %d/%d" % (ok, total) if ok == total else "FAIL %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()

    def arg(name, default, cast):
        for a in sys.argv:
            if a.startswith("--%s=" % name):
                return cast(a.split("=", 1)[1])
        return default

    beta = arg("beta", DEFAULT_BETA, float)
    nav = arg("nav", DEFAULT_NAV, float)
    inception = arg("inception", DEFAULT_INCEPTION, str)
    fresh = "--fresh-gate" in sys.argv
    if "--reset" in sys.argv:
        base_dir = (os.path.join(PATHS.results_dir, "etf_book_order_fresh") if fresh else OUT_DIR)
        for name in ("state.json", "ledger.jsonl"):
            p = os.path.join(base_dir, name)
            if os.path.exists(p):
                os.remove(p)
        print("reset: cleared state.json + ledger.jsonl in", base_dir)
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        return run(beta, nav, inception, fresh_gate=fresh)
    if len(sys.argv) > 1 and sys.argv[1] == "card":
        # default = the card's own stated capital; --nav= only re-prices the lots
        stated = nav if any(a.startswith("--nav=") for a in sys.argv) else None
        return run_card(stated)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())