"""Today or tomorrow?  Adding the trim's price to the price of being late.

Why this face exists
--------------------
The desk now has three separate prices on one page and still cannot act:

* r1478 prints the distance between this ticket's k and the permission that issued it;
* r1479/r1480 print what obeying the permission costs (one-side toll + carry) and what
  the delay *policy* costs;
* r1481 prints what one sheet costs when it is filled one open late -- and refuses to
  call that a decision because 41% of the sheets went the other way.

A desk does not hand three prices to a trader.  It asks one question: *should I do this
today, or is it cheaper to wait?*  That answer is the sum of the two prices it already
has, and it needs a third leg nobody had measured: waiting is usually "a few days", not
"one day", so the per-sheet price has to exist for k bars, not only for k=1.

What it measures
----------------
1. **The k-bar ladder.**  A sheet filled k opens late keeps the old book for k bars and
   then joins the new one; holding the two books otherwise identical, one sheet's price
   for a k-bar delay is the sum of the k bar-differences:

       delta_log_k = sum_{j<k} [log(1+r_old_j) - log(1+r_new_j)]

   Each decision's window is read off the same punctual walk (`tape_windows`), so the
   ladder costs one pass, not one replay per k.  The ledger form is
   `delta_cny_k = NAV * (prod(1+r_old) - prod(1+r_new))`.

2. **Whether the locals still add up at k>1.**  The aggregate is
   `etf_book_punctuality.replay(lag=k)`; the residual against the sum of the locals is
   printed, never assumed.  Only k < rebal is admissible: at k >= rebal a pending sheet
   is overwritten by the next decision, which is a different question.

3. **The decision.**  Today's cost is the baseline (0).  Waiting k opens costs
   `-mean(delta_cny_k) + carry_cny_per_year * k / 244` -- the price of the delay plus the
   carry the cut would have stopped collecting.  The row picks the cheapest k and says
   whether that choice is separable from zero *on the mean*; the single-sheet coin flip
   is disclosed next to it, never averaged away (r1481 verdict).

Nothing here is typed in: every number is read from the published receipts
(`etf_book_cut_order_gap.json`, `etf_book_late_sheet_price.json`) or re-derived on the
panel.

Usage: python scripts/etf_book_do_or_wait.py [run|selftest|--check]
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_equity_alpha as A
import etf_robust_pf as R
import etf_book_punctuality as P
import etf_book_late_sheet_price as L

CAPITAL_CNY = 1_000_000.0
REBAL, N_HOLD, COST = 20, 5, 0.0010
KS = (1, 2, 3, 5, 10)
MAX_K = max(KS)
PHASES = 5
BARS_PER_YEAR = 244.0
ARMS = (("nobond_vt08", 0.08), ("nobond_base", None))
ADD_TOL = 0.15  # same order as the k=1 face; above this the locals do not reconstruct the arm
T_SEPARABLE = 2.0

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUT = os.path.join(ROOT, "results", "etf_book_cut_order_gap.json")
LATE = os.path.join(ROOT, "results", "etf_book_late_sheet_price.json")
OUT = os.path.join(ROOT, "results", "etf_book_do_or_wait.json")


# --------------------------------------------------------------------- the ladder
def _windows_for(events, k):
    """Per-event k-bar price, skipping decisions whose window runs off the panel."""
    out = []
    for e in events:
        w = e["windows"]
        if len(w) < k:
            continue
        dl = sum(math.log1p(x["r_old"]) - math.log1p(x["r_new"]) for x in w[:k])
        prod_old = 1.0
        prod_new = 1.0
        for x in w[:k]:
            prod_old *= (1.0 + x["r_old"])
            prod_new *= (1.0 + x["r_new"])
        out.append({
            "date": e["date"], "nav_cny": e.get("nav_exact", e["nav_cny"]),
            "delta_log": dl, "delta_bps": (prod_old - prod_new) * 1e4,
            "delta_cny": e.get("nav_exact", e["nav_cny"]) * CAPITAL_CNY * (prod_old - prod_new),
        })
    return out


def _dist(values):
    v = np.asarray(values, dtype=float)
    n = int(v.size)
    if n == 0:
        return {"n": 0}
    sd = float(np.std(v, ddof=1)) if n > 1 else 0.0
    sem = sd / math.sqrt(n) if n > 1 else float("inf")
    mean = float(np.mean(v))
    return {"n": n, "mean": mean, "sd": sd, "sem": sem,
            "t": (mean / sem) if sem > 0 else None,
            "median": float(np.median(v)),
            "p10": float(np.percentile(v, 10)), "p90": float(np.percentile(v, 90)),
            "worst": float(np.min(v)), "best": float(np.max(v)),
            "share_late_helps": float(np.mean(v > 0))}


def measure_arm(close, openp, amt, sc, arm, vt):
    ref, _ = R.open_to_open_equity(close, openp, amt, sc, REBAL, N_HOLD, COST, vol_target=vt)
    per_phase, control, phase0 = [], None, None
    for ph in range(PHASES):
        ser, ev = L.tape_windows(close, openp, amt, sc, max_k=MAX_K, vol_target=vt, phase=ph)
        if ph == 0:
            joined = pd.concat([ref.rename("ref"), ser.rename("mine")], axis=1).dropna()
            gap = float((joined["ref"] - joined["mine"]).abs().max()) if len(joined) else float("inf")
            control = {"arm": arm, "bars": int(len(joined)), "max_abs_level_gap": gap,
                       "reproduces_engine": gap <= 1e-12}
            if not control["reproduces_engine"]:
                raise SystemExit("CONTROL_FAIL: window tape does not reproduce the engine for %s "
                                 "(gap=%r) -- refusing to price a wait" % (arm, gap))
            phase0, phase0_ser = ev, ser
        per_phase.append(ev)

    ladder = []
    for k in KS:
        evs = [x for ev in per_phase for x in _windows_for(ev, k)]
        db = _dist([e["delta_bps"] for e in evs])
        dc = _dist([e["delta_cny"] for e in evs])
        # aggregate on the same phase grid, phase 0 for the residual (one pass per k)
        late_ser, _t, _l = P.replay(close, openp, amt, sc, REBAL, N_HOLD, COST,
                                    vol_target=vt, lag=k, phase=0)
        loc0 = _windows_for(phase0, k)
        predicted = sum(e["delta_log"] for e in loc0)
        actual = math.log(float(late_ser.iloc[-1]) / float(phase0_ser.iloc[-1]))
        residual = actual - predicted
        share = (residual / abs(actual)) if actual else None
        ladder.append({
            "arm": arm, "vol_target": vt, "k": k,
            "events": db.get("n", 0),
            "mean_bps": db.get("mean"), "t": db.get("t"),
            "share_late_helps": db.get("share_late_helps"),
            "median_cny": dc.get("median"), "mean_cny": dc.get("mean"),
            "p10_cny": dc.get("p10"), "p90_cny": dc.get("p90"),
            "sd_cny": dc.get("sd"),
            "aggregate_dcagr_pp": (A.stats2(late_ser, "late")["cagr"] -
                                   A.stats2(phase0_ser, "ctl")["cagr"]) * 100.0,
            "predicted_log_delta": predicted, "actual_log_delta": actual,
            "residual": residual, "residual_share": share,
            "additivity_ok": share is not None and abs(share) <= ADD_TOL,
            "overlaps_next_decision": k >= REBAL,
        })
    worst = max((abs(x["residual_share"]) for x in ladder if x["residual_share"] is not None),
                default=None)
    return {"arm": arm, "vol_target": vt, "control": control, "ladder": ladder,
            "worst_residual_share": worst,
            "locals_add_up_at_every_k": all(x["additivity_ok"] for x in ladder)}


# ------------------------------------------------------------------ the decision
def _load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def decide(arm_block, gap, late):
    """Fold the cut's price and the wait's price into one action. Pure function."""
    if not arm_block or not arm_block.get("ladder"):
        return {"verdict": "UNKNOWN_MISSING_LADDER", "sentence": None, "table": []}
    ladder = arm_block["ladder"]
    if gap is None:
        trim_owed, tx, carry = None, None, None
    else:
        trim = gap.get("trim")
        cost = gap.get("cost") or {}
        trim_owed = bool(trim)
        tx = cost.get("tx_cny_one_side")
        carry = cost.get("carry_cny_per_year")

    table = [{"k": 0, "mean_cny": 0.0, "carry_cny": 0.0, "cost_cny_vs_today": 0.0,
              "t": None, "share_late_helps": None, "separable_from_zero": False,
              "baseline": True}]
    for row in ladder:
        k = row["k"]
        price = row.get("mean_cny")
        carry_k = (carry or 0.0) * k / BARS_PER_YEAR
        total = -price + carry_k if price is not None else None
        table.append({
            "k": k, "mean_cny": price, "carry_cny": round(float(carry_k), 2),
            "cost_cny_vs_today": round(float(total), 2) if total is not None else None,
            "t": row.get("t"), "share_late_helps": row.get("share_late_helps"),
            "separable_from_zero": bool(row.get("t") is not None and abs(row["t"]) >= T_SEPARABLE),
        })
    cand = [r for r in table if r["cost_cny_vs_today"] is not None]
    best = min(cand, key=lambda r: r["cost_cny_vs_today"]) if cand else None

    if not (tx is not None and carry is not None) or trim_owed is None:
        return {"verdict": "UNKNOWN_MISSING_RECEIPT", "sentence": None, "table": table,
                "best_k": None}

    one = next((r for r in ladder if r["k"] == 1), None)
    if trim_owed:
        today_cost = float(tx) + float(carry) / BARS_PER_YEAR
    else:
        # nothing is owed today; the baseline is "do nothing", so a wait costs only the
        # price of the fill it postpones
        today_cost = 0.0

    if best is None:
        verdict = "UNKNOWN_MISSING_LADDER"
    elif not trim_owed:
        # nothing is owed today: the action is "do nothing" whatever the ladder says, and
        # a cheapest-wait number would be advice to postpone something that is not owed
        verdict = "NOTHING_OWED_TODAY"
    elif best["k"] == 0 or best["cost_cny_vs_today"] >= 0:
        verdict = "DO_TODAY"
    elif best["separable_from_zero"] and best["cost_cny_vs_today"] < 0:
        verdict = "WAIT_%d_BARS_IS_CHEAPER" % best["k"]
    else:
        verdict = "WAIT_LOOKS_CHEAPER_BUT_NOT_SEPARABLE"

    if not trim_owed:
        head = ("nothing is owed today (the ticket orders k under its own permission), so "
                "the baseline is 'do nothing'")
    else:
        head = ("obeying the permission today costs %.2f CNY one side plus %.2f CNY/yr of "
                "carry (%.2f CNY for one open)"
                % (float(tx), float(carry), today_cost))

    if best is None:
        sentence = head + "; the ladder is missing, so the wait cannot be priced"
    else:
        waits = [x for x in table if not x.get("baseline")]
        lo = min(waits, key=lambda r: r["cost_cny_vs_today"]) if waits else best
        hi = max(waits, key=lambda r: r["cost_cny_vs_today"]) if waits else best
        if best.get("baseline"):
            pick = ("doing it today is the cheapest rung of the ladder (every wait is "
                    "more expensive)")
        else:
            pick = ("waiting is cheapest at k=%d (%+.0f CNY vs today, %s)"
                    % (best["k"], best["cost_cny_vs_today"],
                       ("separable from zero" if best["separable_from_zero"]
                        else "NOT separable from zero")))
        sentence = (
            head + ". " + pick + "; across k=1..%d the waits span %+.0f .. %+.0f CNY vs today. "
            "One open late is worth %s CNY of NAV on the median sheet with waiting helping on "
            "%.0f%% of them (t=%s), so the mean is priced but a single sheet is still a coin flip."
            % (MAX_K, lo["cost_cny_vs_today"], hi["cost_cny_vs_today"],
               ("{:,.0f}".format(one["median_cny"]) if one and one.get("median_cny") is not None else "?"),
               100.0 * (one.get("share_late_helps") or 0.0) if one else 0.0,
               ("%.2f" % one["t"]) if one and one.get("t") is not None else "n/a"))
    return {"verdict": verdict, "sentence": sentence, "table": table,
            "best_k": (best or {}).get("k"), "today_cost_cny": round(today_cost, 2),
            "trim_owed": trim_owed,
            "one_open_late": ({
                "median_cny": one["median_cny"], "mean_cny": one["mean_cny"],
                "t": one["t"], "share_late_helps": one["share_late_helps"],
            } if one else None)}


def run(out_path=None):
    close, openp, amt, sc, n_flip, _cls = P.build()
    arms = [measure_arm(close, openp, amt, sc, arm, vt) for arm, vt in ARMS]
    gap = _load(CUT)
    late = _load(LATE)
    main = next((a for a in arms if a["arm"] == "nobond_vt08"), arms[0] if arms else None)
    dec = decide(main, gap, late)
    payload = {
        "face": "etf_book_do_or_wait",
        "question": "Should this sheet be done today, or is waiting cheaper -- and does the "
                    "per-sheet price still add up when the wait is several bars?",
        "evidence_cutoff": str(close.index[-1].date()),
        "capital_cny": CAPITAL_CNY,
        "config": {"rebal": REBAL, "n_hold": N_HOLD, "cost_per_edge": COST,
                   "vol_window": 60, "universe": "bond-free", "phases": PHASES,
                   "ks": list(KS), "bars_per_year": BARS_PER_YEAR,
                   "additivity_tol": ADD_TOL, "separable_t": T_SEPARABLE},
        "panel": {"symbols": int(close.shape[1]), "first_bar": str(close.index[0].date()),
                  "last_bar": str(close.index[-1].date()), "flips_repaired": int(n_flip)},
        "model": {
            "local_price_k": "sum of k bar differences between the old and the new book",
            "aggregate": "etf_book_punctuality.replay(lag=k) on the same phase grid",
            "not_assumed": "that the locals add up -- residual printed per k",
            "decision": "cost(k) = -mean(delta_cny_k) + carry_per_year * k / bars_per_year",
            "single_sheet": "the mean is priced; the single sheet's dispersion is printed "
                            "beside it and never averaged away",
        },
        "arms": arms,
        "decision": dec,
        "headline": [dec["sentence"]] if dec.get("sentence") else [],
    }
    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        print("wrote", out_path)
    return payload


# --------------------------------------------------------------------- fixtures
def _fixture(kind, n=620, rebal=20):
    """Same three fixtures as the k=1 face: the ladder must degrade to it at k=1."""
    return L._fixture(kind, n=n, rebal=rebal)


def _two_bar_loser(n=620, rebal=20):
    """Alternating switch where the freshly bought book loses the first two bars after
    every switch.  A k-bar wait must then be worth exactly k times the one-bar wait --
    the ladder may not copy the first rung into the rest."""
    idx = pd.bdate_range("2020-01-01", periods=n)
    close = pd.DataFrame({"A": np.ones(n), "B": np.ones(n)}, index=idx)
    score = pd.DataFrame({"A": 2.0, "B": 1.0}, index=idx)

    def pick(s):
        return "A" if (s // rebal) % 2 == 0 else "B"

    for i in range(1, n):
        s = (i // rebal) * rebal
        losing = pick(s)
        winner = "B" if losing == "A" else "A"
        g = {losing: 0.999, winner: 1.001} if (s > 0 and i - s <= 2) else {"A": 1.0, "B": 1.0}
        close.iloc[i] = close.iloc[i - 1] * np.array([g["A"], g["B"]])
        score.iloc[i] = {pick(i): 2.0, ("B" if pick(i) == "A" else "A"): 1.0}
    openp = close.shift(1).bfill()
    amt = pd.DataFrame(1e9, index=idx, columns=close.columns)
    return close, openp, amt, score


def selftest():
    legs = []

    def leg(name, ok, note=""):
        legs.append((name, bool(ok), note))

    close, openp, amt, score = _fixture("monotone")
    ser_w, events = L.tape_windows(close, openp, amt, score, max_k=MAX_K, n_hold=1, cost=0.0)
    ser_t, events_t = L.tape(close, openp, amt, score, n_hold=1, cost=0.0)
    joined = pd.concat([ser_w.rename("w"), ser_t.rename("t")], axis=1).dropna()
    leg("window tape walks the same equity as the k=1 tape",
        float((joined.w - joined.t).abs().max()) <= 1e-12)
    leg("window tape keeps the same event dates",
        [e["date"] for e in events] == [e["date"] for e in events_t])
    leg("k=1 window price equals the published one-bar price",
        all(abs(_windows_for([e], 1)[0]["delta_log"] - e["delta_log"]) <= 1e-15
            for e in events if e["windows"]))
    leg("k-window price is the sum of its own bars",
        all(abs(_windows_for([e], 3)[0]["delta_log"] -
                sum(math.log1p(x["r_old"]) - math.log1p(x["r_new"]) for x in e["windows"][:3])) <= 1e-15
            for e in events if len(e["windows"]) >= 3))
    legs.append  # noqa: B018  (documented no-op guard against accidental rebinding)

    # "flip": the incoming book loses the switch bar. Every later bar is flat, so a
    # k-bar wait must be exactly as expensive as a one-bar wait -- the ladder may not
    # invent a cost for bars where the two books are identical.
    fc, fo, fa, fs = _fixture("flip")
    _s, fev = L.tape_windows(fc, fo, fa, fs, max_k=MAX_K, n_hold=1, cost=0.0)
    w1 = _windows_for(fev, 1)
    w3 = _windows_for(fev, 3)
    leg("flat continuation does not add to the price",
        len(w1) == len(w3) and all(abs(a["delta_log"] - b["delta_log"]) <= 1e-15
                                   for a, b in zip(w1, w3)))

    # a panel where the fresh book loses the first TWO bars after every switch: a two-bar
    # wait must be worth about twice a one-bar wait, not the same number copied over.
    close2, openp2, amt2, score2 = _two_bar_loser()
    _s2, ev2 = L.tape_windows(close2, openp2, amt2, score2, max_k=MAX_K, n_hold=1, cost=0.0)
    rows = [(e, _windows_for([e], 1)[0]["delta_log"], _windows_for([e], 2)[0]["delta_log"])
            for e in ev2 if e["legs_changed"] > 0 and len(e["windows"]) >= 2]
    leg("a longer wait is priced, not copied",
        bool(rows) and all(one > 0 and abs(two - 2.0 * one) <= 1e-9 for _e, one, two in rows),
        "%d switches" % len(rows))

    # dispersion helper: no sample, no t
    leg("empty ladder slice is not a zero", _dist([]) == {"n": 0})
    leg("constant sample has no t", _dist([5.0, 5.0, 5.0])["t"] is None)

    # the decision, on fixtures where the answer is known
    mk = lambda mean_bps, t, share, median=0.0: [  # noqa: E731
        {"k": k, "mean_bps": mean_bps, "t": t, "share_late_helps": share,
         "median_cny": median, "mean_cny": mean_bps * 100.0, "p10_cny": 0.0,
         "p90_cny": 0.0, "sd_cny": 1.0, "events": 400,
         "aggregate_dcagr_pp": 0.0, "predicted_log_delta": 0.0,
         "actual_log_delta": 0.0, "residual": 0.0, "residual_share": 0.0,
         "additivity_ok": True, "overlaps_next_decision": k >= 20}
        for k in (1, 2, 3, 5, 10)]
    gap = {"trim": {"legs": [{"symbol": "X"}]},
           "cost": {"tx_cny_one_side": 50.0, "carry_cny_per_year": 800.0}}
    d1 = decide({"ladder": mk(-12.0, -4.6, 0.41)}, gap, None)
    leg("a late sheet that costs money means do it today", d1["verdict"] == "DO_TODAY")
    leg("a cutting desk's cost table starts from its own one-side toll",
        abs(d1["today_cost_cny"] - (50.0 + 800.0 / 244.0)) <= 0.011)
    d2 = decide({"ladder": mk(+30.0, 4.0, 0.70)}, gap, None)
    leg("a late sheet that pays means wait", d2["verdict"].startswith("WAIT_") and d2["best_k"] == 1)
    d3 = decide({"ladder": mk(+30.0, 1.1, 0.60)}, gap, None)
    leg("a wait that is not separable is not recommended",
        d3["verdict"] == "WAIT_LOOKS_CHEAPER_BUT_NOT_SEPARABLE")
    d4 = decide({"ladder": mk(-12.0, -4.6, 0.41)}, {"trim": None,
                                                    "cost": {"tx_cny_one_side": 0.0,
                                                             "carry_cny_per_year": 0.0}}, None)
    leg("nothing owed today is stated as such, not as a zero-cost cut",
        d4["verdict"] == "NOTHING_OWED_TODAY" and d4["trim_owed"] is False
        and d4["today_cost_cny"] == 0.0
        and "nothing is owed today" in d4["sentence"])
    d5 = decide(None, gap, None)
    leg("missing ladder is UNKNOWN", d5["verdict"] == "UNKNOWN_MISSING_LADDER")
    d6 = decide({"ladder": mk(-12.0, -4.6, 0.41)}, None, None)
    leg("missing receipt is UNKNOWN, never a zero toll", d6["verdict"] == "UNKNOWN_MISSING_RECEIPT")

    failed = [x[0] for x in legs if not x[1]]
    for name, ok, note in legs:
        print(("PASS " if ok else "FAIL ") + name + (("  [" + note + "]") if note else ""))
    print("selftest %d/%d legs" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


def check(out_path=None):
    path = out_path or OUT
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    legs, bad = [], []

    for a in d["arms"]:
        legs.append(("%s: control replays the engine" % a["arm"],
                     a["control"]["reproduces_engine"], ""))
        if not a["control"]["reproduces_engine"]:
            bad.append(a["arm"] + ":control")
        legs.append(("%s: ladder has every k" % a["arm"],
                     [x["k"] for x in a["ladder"]] == list(d["config"]["ks"]), ""))
        if [x["k"] for x in a["ladder"]] != list(d["config"]["ks"]):
            bad.append(a["arm"] + ":ks")
        add_ok = all(x["additivity_ok"] ==
                     (x["residual_share"] is not None and
                      abs(x["residual_share"]) <= d["config"]["additivity_tol"])
                     for x in a["ladder"])
        legs.append(("%s: additivity verdict follows its own residual" % a["arm"], add_ok, ""))
        if not add_ok:
            bad.append(a["arm"] + ":additivity")
        legs.append(("%s: published sum equals the flag" % a["arm"],
                     a["locals_add_up_at_every_k"] == all(x["additivity_ok"] for x in a["ladder"]), ""))
        if a["locals_add_up_at_every_k"] != all(x["additivity_ok"] for x in a["ladder"]):
            bad.append(a["arm"] + ":flag")

    # the decision must be re-derivable from the table it published
    dec = d["decision"]
    main = next((a for a in d["arms"] if a["arm"] == "nobond_vt08"), d["arms"][0])
    redo = decide(main, _load(CUT), _load(LATE))
    for k in ("verdict", "best_k", "trim_owed"):
        legs.append(("decision re-derives (%s)" % k, dec.get(k) == redo.get(k),
                     "%r vs %r" % (dec.get(k), redo.get(k))))
        if dec.get(k) != redo.get(k):
            bad.append("decision:" + k)
    tbl_ok = all(abs(x["cost_cny_vs_today"] -
                     round(-(x["mean_cny"] or 0.0) + x["carry_cny"], 2)) <= 0.011
                 for x in dec["table"] if x["cost_cny_vs_today"] is not None)
    legs.append(("every cost row is its own two prices added", tbl_ok, ""))
    if not tbl_ok:
        bad.append("decision:table")

    # cross-face: the k=1 rung must be the published one-sheet price (E289 family)
    late = _load(LATE)
    if late:
        pub = next((a for a in late.get("arms", []) if a.get("arm") == "nobond_vt08"), None)
        one = next((x for x in main["ladder"] if x["k"] == 1), None)
        ok = (pub is not None and one is not None and
              abs(one["mean_bps"] - pub["dist_bps"]["mean"]) <= 1e-9 and
              abs(one["median_cny"] - pub["dist_cny"]["median"]) <= 0.51)
        legs.append(("k=1 rung equals the published one-sheet face", ok,
                     "" if ok else "ladder %r vs face %r" % (one and one.get("mean_bps"),
                                                             pub and pub["dist_bps"]["mean"])))
        if not ok:
            bad.append("cross:late_sheet_price")

    for n, ok, detail in legs:
        print(("PASS " if ok else "FAIL ") + n + (("  [" + detail + "]") if detail and not ok else ""))
    print("check %d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd in ("--check", "check"):
        return check()
    payload = run(OUT)
    dec = payload["decision"]
    print(dec["verdict"])
    if dec.get("sentence"):
        print("  " + dec["sentence"])
    for a in payload["arms"]:
        print("  %-12s locals add up at every k: %s (worst residual share %s)"
              % (a["arm"], a["locals_add_up_at_every_k"],
                 ("%.3f" % a["worst_residual_share"])
                 if a["worst_residual_share"] is not None else "n/a"))
        for x in a["ladder"]:
            print("    k=%-2d n=%-4d mean %+7.2f bps (t=%s) median %+8.0f CNY  agg %+6.2fpp  "
                  "residual %+.0e"
                  % (x["k"], x["events"], x["mean_bps"] or 0.0,
                     ("%.2f" % x["t"]) if x["t"] is not None else "n/a",
                     x["median_cny"] or 0.0, x["aggregate_dcagr_pp"], x["residual"]))
    print("  -> " + OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))