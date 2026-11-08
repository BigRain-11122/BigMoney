"""Which rule sizes the money that is about to be traded?

r1446 closed with an open question: the executed book's weight (0.460253) is published
by the ticket, and the ticket sizes it as `k = beta_target / beta_hat` with
beta_target 0.20 (r1256, DEFAULT_BETA). But the book the year gate adjudicates
(`nobond_vt08_adopted`) sizes itself with an 8% volatility target -- a different rule
producing, by construction, a different weight. Two numbers that happen to agree today
are not the same number, and a size nobody graded is not a graded size.

This face asks one question and only one: at the ticket's own decision bar, on the
ticket's own panel, does the beta rule and the vol-target rule put the same fraction of
capital at risk, and do they hold the same names? It does not re-price returns, does not
change any rule, does not touch the ledger, and publishes no verdict on the gate.

Two identity legs keep it honest:
  * the beta-rule weight computed here must reproduce the published ticket's k
    (results/etf_book_order/TICKET-*.json), else this face is measuring another book;
  * the names it reads off the ticket's own score row must be the ticket's names.

Provenance is printed as a citation plus a liveness check: the cited commit is history,
but the constant it introduced is re-read from the imported module at run time. If
someone changes the constant, the citation stops matching and the leg fails loudly.

Run:
  python scripts/etf_book_live_size_provenance.py run      # ~2 min (two panel sims)
  python scripts/etf_book_live_size_provenance.py --check   # 0.2s, published face only
  python scripts/etf_book_live_size_provenance.py selftest   # offline
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TICKET_GLOB = "results/etf_book_order/TICKET-*.json"
DECISION_PATH = "results/etf_book_supply_gate_decision/DECISION.json"
NOBOND_PATH = "results/etf_nobond_vt.json"
OUT_PATH = "results/etf_book_live_size_provenance/SIZE-PROVENANCE.json"

# cited provenance: the beta target and the vol target were introduced by different
# rounds and mean different things. The commit is history; the value is re-read live.
CITED = {
    "beta_target": {"value": 0.20, "commit": "a8fc76102c", "round": 1256,
                    "sentence": "the ETF book now ships an executable ticket (k=0.61 at beta 0.20)"},
    "vol_target": {"value": 0.08, "commit": None, "round": None,
                   "sentence": "drop the bond sleeve, then apply the 8%/12% vol target"},
}
# how far apart two sizings may be and still count as "the same money at risk".
# 0.5pp of NAV: half a percentage point of capital is not a rounding difference.
SIZE_TOL = 0.005


def pp(x):
    return None if x is None else round(100.0 * float(x), 2)


def compare(k_beta, k_vol, names_a, names_b, tol=SIZE_TOL):
    """The whole verdict, in one place, offline-testable.

    k_vol None is UNREADABLE (r98: unknown is not empty, and not "the same").
    """
    if k_vol is None or k_beta is None:
        return {"verdict": "UNREADABLE",
                "sentence": "one of the two sizings could not be derived from the panel; "
                            "an unread rule is not evidence that the rules agree",
                "k_beta": k_beta, "k_vol": k_vol, "gap_pp": None,
                "same_names": None, "names_only_in_ticket": None,
                "names_only_in_adjudicated": None}
    gap = float(k_beta) - float(k_vol)
    a, b = list(names_a), list(names_b)
    only_a = [n for n in a if n not in set(b)]
    only_b = [n for n in b if n not in set(a)]
    same_names = not only_a and not only_b
    size_same = abs(gap) <= tol
    if size_same and same_names:
        verdict = "SAME_BOOK_SAME_SIZE"
    elif size_same and not same_names:
        verdict = "SAME_SIZE_DIFFERENT_NAMES"
    elif same_names and not size_same:
        verdict = "SAME_NAMES_DIFFERENT_SIZE"
    else:
        verdict = "DIFFERENT_BOOK_AND_SIZE"
    return {"verdict": verdict,
            "sentence": None, "k_beta": round(float(k_beta), 6),
            "k_vol": round(float(k_vol), 6), "gap_pp": round(100.0 * gap, 2),
            "size_same": size_same, "same_names": same_names,
            "names_only_in_ticket": only_a, "names_only_in_adjudicated": only_b,
            "tol_pp": round(100.0 * tol, 2)}


def money_reading(k_beta, k_vol, nav=1_000_000.0):
    """Same capital, two rules: how many yuan and how much book vol each puts on."""
    if k_beta is None or k_vol is None:
        return None
    return {"nav_cny": nav,
            "book_cny_beta_rule": round(nav * float(k_beta), 2),
            "book_cny_vol_rule": round(nav * float(k_vol), 2),
            "delta_cny": round(nav * (float(k_beta) - float(k_vol)), 2)}


def ticket_grid_bar(index, rebal=20, start="2020-01-01"):
    """The bar the published ticket decides on -- mirrored from etf_book_order.run().

    The ticket is NOT ranked on the last panel bar (r1229) and NOT on the engine's own
    re-decision date (a different phase); it is the last point of the fixed 2020-01-01
    20-bar grid. Kept as one function so the selftest can pin it.
    """
    import pandas as pd

    grid = [d for d in index if d >= pd.Timestamp(start)]
    if not grid:
        return None
    return grid[(len(grid) - 1) // rebal * rebal]


def _read_json(rel):
    p = os.path.join(BASE, rel)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def latest_ticket():
    files = sorted(glob.glob(os.path.join(BASE, TICKET_GLOB)))
    if not files:
        return None, None
    path = files[-1]
    with open(path, encoding="utf-8") as f:
        return os.path.basename(path), json.load(f)


def published_face():
    """Everything derivable without loading the panel (--check path)."""
    name, tk = latest_ticket()
    if tk is None:
        return {"face": "live_size_provenance", "verdict": "NO_TICKET",
                "sentence": "no ticket face on disk; nothing to audit"}
    dec = _read_json(DECISION_PATH) if os.path.exists(os.path.join(BASE, DECISION_PATH)) else None
    desk = (dec or {}).get("desk") or {}
    executed = desk.get("executed_book") or {}
    tk_names = [r["symbol"] for r in tk["ticket"]["order"]]
    out = {
        "face": "live_size_provenance",
        "evidence_cutoff": tk.get("evidence_cutoff"),
        "ticket_file": name,
        "ticket_rel": os.path.join("results", "etf_book_order", name),
        "ticket": {
            "beta_target": tk.get("beta_target"),
            "k_now": tk.get("k_now"),
            "book_weight": tk["ticket"].get("book_weight"),
            "cash_weight": tk["ticket"].get("cash_weight"),
            "book_amount_cny": tk["ticket"].get("book_amount"),
            "names": tk_names,
        },
        "decision_desk": {
            "executed_book": executed.get("candidate"),
            "book_weight_in_desk": executed.get("book_weight"),
            "book_amount_cny_in_desk": executed.get("book_amount_cny"),
            "names_in_ticket_in_desk": executed.get("names_in_ticket"),
            "class": executed.get("class"),
        },
        "provenance": {
            "beta_target": dict(CITED["beta_target"]),
            "vol_target": dict(CITED["vol_target"]),
        },
    }
    # the desk already equates the live ticket's weight with the adjudicated book's.
    # make that identity explicit instead of leaving it to the reader.
    desk_w = executed.get("book_weight")
    live_w = tk["ticket"].get("book_weight")
    out["desk_reads_the_ticket_weight"] = (
        None if desk_w is None or live_w is None
        else abs(float(desk_w) - float(live_w)) < 1e-9)
    return out


def run():
    import numpy as np
    import pandas as pd

    sys.path.insert(0, os.path.join(BASE, "scripts"))
    from scripts import etf_composite_pf as F
    from scripts import etf_phase_beta_target as BT
    from scripts import etf_variants_null_rolling as V
    from scripts import etf_equity_alpha as AE
    from scripts import etf_robust_pf as R
    from scripts import etf_book_order as BO
    from scripts.etf_asset_class import classify

    face = published_face()
    if face.get("verdict") == "NO_TICKET":
        return face

    print("panel: loading", flush=True)
    close, openp, amt, feats = F.build_panel()
    if BO.REPAIR_PANEL:
        close, openp, n_flip = AE.repair_flips(close, openp)
        print("panel: repaired %d flip prints" % n_flip, flush=True)
    classes = pd.Series(classify(list(close.columns)))

    # ---- arm A: the ticket's own construction (V.KEEP classes, beta target)
    cols_a = [c for c in close.columns if classes[c] in V.KEEP]
    score_a = F.build_score(close[cols_a], amt[cols_a], feats)
    print("arm A: %d symbols, simulating next-open engine" % len(cols_a), flush=True)
    ser_a, _to_a, _gap_a = F.run_next_open(close[cols_a], openp[cols_a], amt[cols_a], feats,
                                           BO.REBAL, n_hold=F.N_HOLD, cost=F.COST,
                                           score=score_a)
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        return dict(face, verdict="MECHANISM_FAULT", sentence="no 510300 on the panel")
    mkt = close[mkt_col]
    idx = ser_a.index.intersection(mkt.index)
    rp, rm = BT.rets(ser_a.reindex(idx)), BT.rets(mkt.reindex(idx))
    sched = BO.k_schedule(rp, rm, BO.DEFAULT_BETA)
    if not sched:
        return dict(face, verdict="MECHANISM_FAULT", sentence="beta schedule empty")
    _k_engine, k_beta, beta_hat = sched[-1]
    # `k_schedule` returns the ENGINE's own re-decision dates (run_next_open restarts the
    # 20-bar grid at its own first bar), and that phase is NOT the ticket's: r1229 fixed the
    # ticket to the panel's 2020-01-01 grid, so the two disagree by a fraction of a period.
    # Ranking on the engine's date is what made the first run of this face read the 10-23
    # top-5 against a sheet built on 10-14 -- a construction difference wearing the costume
    # of a ticket defect. Read the ticket's own grid formula instead of any second clock.
    grid = [d for d in close.index if d >= pd.Timestamp("2020-01-01")]
    if not grid:
        return dict(face, verdict="MECHANISM_FAULT", sentence="panel starts after 2020-01-01")
    dec_bar = ticket_grid_bar(close.index, BO.REBAL)
    last_bar = score_a.index[-1]
    row_a = score_a.loc[dec_bar].dropna()
    names_a = list(row_a.nlargest(F.N_HOLD).index)

    # ---- arm B: the book the year gate adjudicates (nobond, 8% vol target)
    want = ("equity", "commodity", "convertible")
    cols_b = [c for c in close.columns if classes[c] in want]
    score_b = F.build_score(close[cols_b], amt[cols_b], feats)
    diag = []
    print("arm B: %d symbols, vol-target sim" % len(cols_b), flush=True)
    R.open_to_open_equity(close[cols_b], openp[cols_b], amt[cols_b], score_b, 20, 5, 0.0010,
                          vol_target=0.08, diag=diag)
    # the vol rule's own decision grid may sit on a different offset, so read the scale in
    # force at the SAME decision date the beta rule decided on (causal: rows <= dec_bar).
    at_or_before = [r for r in diag
                    if r.get("date") is not None
                    and pd.Timestamp(r["date"]).toordinal()
                    <= pd.Timestamp(dec_bar).toordinal()]
    last = at_or_before[-1] if at_or_before else None
    k_vol = float(last["scale"]) if last and last.get("scale") is not None else None
    est_vol = float(last["est_vol"]) if last and last.get("est_vol") is not None else None
    vol_bar = last["date"] if last else None
    # both arms are ranked on the SAME decision bar: comparing today's picks with today's
    # picks would answer "do the two rules buy the same names", which is not the question --
    # the question is whether the book that is being sized is the book that was graded.
    row_b = score_b.loc[dec_bar].dropna()
    names_b = list(row_b.nlargest(5).index)

    verdict = compare(k_beta, k_vol, names_a, names_b)
    # r1438 recorded that the ticket's 'crossborder' class has no counterpart in the graded
    # card's equity/commodity/convertible vocabulary. Count it here: a book that is smaller
    # than the graded one but holds names the graded one never prices is not "the same
    # exposure, sized down" -- it is a different bet, and the sizes are not comparable.
    cens = {}
    for sym in face["ticket"]["names"]:
        c = str(classes.get(sym, "unknown"))
        cens[c] = cens.get(c, 0) + 1
    graded_universe = sorted(want)
    ungraded = {c: v for c, v in cens.items() if c not in graded_universe}
    face.update({
        "verdict": verdict["verdict"],
        "comparison": verdict,
        "ticket_class_census": cens,
        "ticket_classes_outside_graded_universe": ungraded,
        "graded_universe": graded_universe,
        "ticket_names_outside_graded_universe":
            sum(ungraded.values()),
        "decision_bar": str(dec_bar.date()) if hasattr(dec_bar, "date") else str(dec_bar),
        "names_bar": str(last_bar.date()) if hasattr(last_bar, "date") else str(last_bar),
        "vol_rule_bar": str(vol_bar.date()) if hasattr(vol_bar, "date") else str(vol_bar),
        "beta_hat": round(float(beta_hat), 6),
        "names_beta_rule": names_a,
        "names_vol_rule": names_b,
        "vol_rule_estimated_vol": None if est_vol is None else round(float(est_vol), 6),
        "money": money_reading(k_beta, k_vol, nav=float(face["ticket"]["book_amount_cny"] or 1e6)
                               / float(face["ticket"]["book_weight"] or 1.0)),
    })

    # identity legs -- if these fail this face is measuring some other book
    tk = _read_json(face["ticket_rel"])
    legs = {
        "L_beta": {"published": tk.get("k_now"), "derived": round(float(k_beta), 6),
                   "ok": abs(float(tk.get("k_now") or -1) - float(k_beta)) <= 1e-3},
        "L_names": {"published": face["ticket"]["names"], "derived": names_a,
                    "ok": list(face["ticket"]["names"]) == names_a},
        "L_constant": {"cited": CITED["beta_target"]["value"],
                       "module": float(BO.DEFAULT_BETA),
                       "ok": abs(float(BO.DEFAULT_BETA) - CITED["beta_target"]["value"]) < 1e-12},
        "L_bar": {"published": tk.get("evidence_cutoff"),
                  "derived": face["names_bar"],
                  "ok": str(tk.get("evidence_cutoff")) == face["names_bar"]},
        "L_decision": {"published": tk.get("book_decided_at"),
                       "derived": face["decision_bar"],
                       "ok": str(tk.get("book_decided_at")) == face["decision_bar"]},
    }
    face["identity_legs"] = legs
    face["identity_ok"] = all(v["ok"] for v in legs.values())
    if not face["identity_ok"]:
        face["verdict"] = "IDENTITY_FAIL"
        face["sentence"] = ("this face did not reproduce the published ticket; its reading "
                            "is about another book and must not be used")

    os.makedirs(os.path.dirname(os.path.join(BASE, OUT_PATH)), exist_ok=True)
    with open(os.path.join(BASE, OUT_PATH), "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=2)
    print("wrote %s | verdict=%s | k_beta=%s k_vol=%s gap_pp=%s"
          % (OUT_PATH, face["verdict"], face["comparison"]["k_beta"],
             face["comparison"]["k_vol"], face["comparison"]["gap_pp"]), flush=True)
    return 0


# ------------------------------------------------------------------------ selftest
def selftest():
    import tempfile
    ok = 0
    n = 0

    def leg(name, cond):
        nonlocal ok, n
        n += 1
        if cond:
            ok += 1
            print("  ok   %s" % name)
        else:
            print("  FAIL %s" % name)

    print("selftest: compare()")
    a = ["X1", "X2", "X3"]
    r = compare(0.46, 0.46, a, list(a))
    leg("L1 identical size+names -> SAME_BOOK_SAME_SIZE",
        r["verdict"] == "SAME_BOOK_SAME_SIZE")
    r = compare(0.46, 0.30, a, list(a))
    leg("L2 same names, 16pp gap -> SAME_NAMES_DIFFERENT_SIZE",
        r["verdict"] == "SAME_NAMES_DIFFERENT_SIZE")
    leg("L3 gap reported in pp with sign", r["gap_pp"] == 16.0)
    r = compare(0.46, 0.46, a, ["X1", "X2", "Y9"])
    leg("L4 same size, one name swapped -> SAME_SIZE_DIFFERENT_NAMES",
        r["verdict"] == "SAME_SIZE_DIFFERENT_NAMES")
    leg("L5 swapped name named on both sides",
        r["names_only_in_ticket"] == ["X3"] and r["names_only_in_adjudicated"] == ["Y9"])
    r = compare(0.46, 0.30, a, ["Y9"])
    leg("L6 both differ -> DIFFERENT_BOOK_AND_SIZE", r["verdict"] == "DIFFERENT_BOOK_AND_SIZE")
    r = compare(0.46, None, a, a)
    leg("L7 unreadable sizing -> UNREADABLE, not 'same' (r98)",
        r["verdict"] == "UNREADABLE" and r["gap_pp"] is None)
    r = compare(0.46, 0.4555, a, a)
    leg("L8 inside 0.5pp tolerance counts as the same size", r["size_same"] is True)
    r = compare(0.46, 0.4545, a, a)
    leg("L9 outside 0.5pp tolerance counts as different", r["size_same"] is False)
    leg("L10 tolerance readout in pp", compare(0.46, 0.46, a, a)["tol_pp"] == 0.5)

    print("selftest: money_reading()")
    m = money_reading(0.46, 0.30, nav=1_000_000.0)
    leg("L11 book CNY per rule", m["book_cny_beta_rule"] == 460000.0
        and m["book_cny_vol_rule"] == 300000.0)
    leg("L12 delta is signed", m["delta_cny"] == 160000.0)
    leg("L13 unreadable sizing yields no money line", money_reading(None, 0.3) is None)

    print("selftest: ticket_grid_bar()")
    import pandas as pd
    # a 55-bar panel: the ticket's grid point is index 40, not the last bar (54).
    idx55 = pd.bdate_range("2020-01-01", periods=55)
    leg("L17 grid bar is the LAST point of the fixed 20-bar grid, not the last bar",
        ticket_grid_bar(idx55, 20) == idx55[40])
    leg("L18 grid bar moves by one period when the panel grows past the next multiple",
        ticket_grid_bar(idx55, 20) == idx55[40]
        and ticket_grid_bar(pd.bdate_range("2020-01-01", periods=61), 20) ==
        pd.bdate_range("2020-01-01", periods=61)[60])
    leg("L19 a panel shorter than the start has no grid bar (UNKNOWN, not today)",
        ticket_grid_bar(pd.bdate_range("2019-01-01", periods=30), 20) is None)
    leg("L20 a 1-bar panel still yields its own bar (no off-by-one crash)",
        ticket_grid_bar(pd.bdate_range("2020-01-01", periods=1), 20)
        == pd.bdate_range("2020-01-01", periods=1)[0])

    print("selftest: published_face() on a fixture tree")
    with tempfile.TemporaryDirectory() as td:
        d1 = os.path.join(td, "results", "etf_book_order")
        d2 = os.path.join(td, "results", "etf_book_supply_gate_decision")
        os.makedirs(d1)
        os.makedirs(d2)
        tk = {"evidence_cutoff": "2026-11-06", "beta_target": 0.2, "k_now": 0.460253,
              "ticket": {"book_weight": 0.460253, "cash_weight": 0.539747,
                         "book_amount": 459796.3,
                         "order": [{"symbol": "159501"}]}}
        json.dump(tk, open(os.path.join(d1, "TICKET-2026-11-06.json"), "w", encoding="utf-8"))
        dec = {"desk": {"executed_book": {"candidate": "nobond_vt08_adopted",
                                          "book_weight": 0.460253,
                                          "book_amount_cny": 459796.3,
                                          "names_in_ticket": 5, "class": "INVARIANT"}}}
        json.dump(dec, open(os.path.join(d2, "DECISION.json"), "w", encoding="utf-8"))
        globals()["BASE"] = td
        f = published_face()
        leg("L14 face reads the ticket's own weight", f["ticket"]["book_weight"] == 0.460253)
        leg("L15 desk-vs-ticket weight equality is stated, not implied",
            f["desk_reads_the_ticket_weight"] is True)
        dec["desk"]["executed_book"]["book_weight"] = 0.30
        json.dump(dec, open(os.path.join(d2, "DECISION.json"), "w", encoding="utf-8"))
        f = published_face()
        leg("L16 a desk quoting a different weight is reported as False, not hidden",
            f["desk_reads_the_ticket_weight"] is False)
        globals()["BASE"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print("selftest: %d/%d" % (ok, n))
    return 0 if ok == n else 1


def check():
    """Re-derive every desk field from the receipt's own sources (r1438 --check pattern).

    Returns (ok, n, lines). A published number that cannot be rebuilt from the ticket and
    the panel-independent inputs is a stale receipt, not a reading.
    """
    path = os.path.join(BASE, OUT_PATH)
    if not os.path.exists(path):
        print("check: no published face at %s" % OUT_PATH)
        return 1, 1, ["MISSING receipt"]
    pub = _read_json(OUT_PATH)
    live = published_face()
    legs = []
    legs.append(("ticket file matches the newest on disk",
                 pub.get("ticket_file") == live.get("ticket_file")))
    legs.append(("ticket weight re-read from the ticket",
                 abs(float(pub["ticket"]["book_weight"]) - float(live["ticket"]["book_weight"])) < 1e-9))
    legs.append(("ticket names re-read from the ticket",
                 list(pub["ticket"]["names"]) == list(live["ticket"]["names"])))
    legs.append(("desk-vs-ticket equality re-derived",
                 pub.get("desk_reads_the_ticket_weight") == live.get("desk_reads_the_ticket_weight")))
    legs.append(("evidence cutoff re-read",
                 str(pub.get("evidence_cutoff")) == str(live.get("evidence_cutoff"))))
    tk = _read_json(pub["ticket_rel"])
    legs.append(("decision bar is the ticket's own book_decided_at",
                 str(pub.get("decision_bar")) == str(tk.get("book_decided_at"))))
    c = pub.get("comparison") or {}
    redo = compare(c.get("k_beta"), c.get("k_vol"),
                   pub.get("names_beta_rule") or [], pub.get("names_vol_rule") or [])
    legs.append(("verdict re-derived by compare() from the published inputs",
                 redo["verdict"] == c.get("verdict") and redo["gap_pp"] == c.get("gap_pp")))
    m = pub.get("money") or {}
    if m:
        # nav*k is the counterfactual target; the ticket's own book_amount is what whole
        # lots can actually buy, so the two differ by lot rounding -- printed, not hidden,
        # and bounded at 0.1% of NAV rather than compared as if they were the same figure.
        _d_beta = float(m["book_cny_beta_rule"]) - float(m["nav_cny"]) * float(c["k_beta"])
        _d_vol = float(m["book_cny_vol_rule"]) - float(m["nav_cny"]) * float(c["k_vol"])
        legs.append(("money line re-derived from nav x k (lot rounding %.4f/%.4f CNY printed)"
                     % (_d_beta, _d_vol),
                     abs(_d_beta) <= 0.001 * float(m["nav_cny"])
                     and abs(_d_vol) <= 0.001 * float(m["nav_cny"])))
    ok = sum(1 for _, v in legs if v)
    for name, v in legs:
        print("  %s %s" % ("ok  " if v else "FAIL", name))
    print("check: %d/%d" % (ok, len(legs)))
    return (0 if ok == len(legs) else 1), len(legs), [n for n, v in legs if not v]


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "--check":
        rc, _n, _bad = check()
        return rc
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv) or 0)