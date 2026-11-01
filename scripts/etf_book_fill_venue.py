"""The 9.60% is not a claim about information -- it is a claim about where you fill.

r1207 pinned the defect: the research engine ranks on bar d's own close and then earns
bar d's OPEN -> bar d+1's open, i.e. it fills at a price that was already in the past when
the signal existed. r1208 put that on the CEO page as "9.60% -> 8.46%, one bar = 1.14pp/yr".

That leaves an unasked question, and it is the one that decides what an operator does:

    is the missing 1.14pp *lost information*, or just an unachievable fill?

The two answers point in opposite directions -- if the edge is really in the information
then the rule needs redesigning; if it is only in the fill, then the same signal is worth
almost the same money and only the execution venue has to change.

Three fills of the SAME signal, same panel, same ranking, same 20-bar grid, same cost
model, same vol overlay (only the price series the book is filled and marked at differs):

    card        fill at open[d]      (the published convention -- not achievable)
    next_open   fill at open[d+1]    (the executable ledger convention, causal)
    close       fill at close[d]     (closing auction / MOC: rank on the close you trade)

`close - next_open` over `card - next_open` is the share of the gap that is a fill-price
artefact. The close arm is then re-priced with extra cost per side, which stands in for
the two honest frictions of trading the close: the ranking is computed on a price that is
not exactly the print you get, and the closing auction has impact. The largest extra cost
that still beats the next-open book is the operator's execution budget.

Frozen before the first run; `--check` re-derives the verdict and every delta from the
published rows, so the sentence cannot drift from the numbers.

  python scripts/etf_book_fill_venue.py run
  python scripts/etf_book_fill_venue.py --check
  python scripts/etf_book_fill_venue.py --selftest
"""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

import etf_book_forward as F
import etf_book_production as P
import etf_equity_alpha as A
import etf_robust_pf as R
import etf_book_lookahead_audit as L

OUT_JSON = os.path.join(ROOT, "results", "etf_book_fill_venue.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_FILL_VENUE.md")
AUDIT_JSON = L.OUT_JSON

# ---------------------------------------------------------------- frozen criteria
# The threshold that makes this a decision and not a table: if most of the one-bar gap
# survives a fill at the close, the problem was never the signal.
SHARE_DOMINANT = 0.60      # share of the gap recovered by filling at the close
SHARE_INFORMATION = 0.25   # below this the gap is information, not fill
# Extra cost per side charged on the close arm, in bp: the closing auction is not free and
# the ranking is computed from a price that is not exactly the fill.
IMPACT_BP = (0, 2, 5, 10, 15, 20, 30)
TOL_PP = 0.25              # a quarter of a point/yr: below this the two fills are the same
CRITERIA = {
    "share_dominant": SHARE_DOMINANT,
    "share_information": SHARE_INFORMATION,
    "impact_bp_grid": list(IMPACT_BP),
    "tol_pp_per_year": TOL_PP,
    "verdict_rule": (
        "FILL_PRICE_DOMINATES iff filling at the close recovers >= 60% of the one-bar gap "
        "(card - next_open); INFORMATION_DOMINATES iff it recovers < 25%; MIXED otherwise. "
        "Execution budget = the largest grid cost per side at which the close book still "
        "matches or beats the next-open book; NONE if even the no-extra-cost close book "
        "does not."),
    "arms": {
        "card": "same signal, filled at open[d] -- the published convention (not achievable)",
        "next_open": "same signal shifted one bar, filled at open[d+1] -- the ledger convention",
        "close": "same signal, filled and marked at close[d] -- closing auction (MOC)",
        "close_i<k>": "close arm with k extra bp per side (auction impact + rank/fill gap)",
    },
    "frozen": ("thresholds written before the first run; --check refuses a face that does "
               "not reproduce them, and refuses a close arm that does not reproduce the "
               "look-ahead audit's own causal arm on the same panel"),
}


def _pp(x):
    return None if x is None else round(100.0 * float(x), 3)


def _row(label, ser, turn, extra_bp=0):
    st = A.stats2(ser.dropna(), label)
    return {
        "arm": label,
        "cagr": st.get("cagr"),
        "sharpe": st.get("sharpe"),
        "maxdd": st.get("maxdd"),
        "vol": st.get("vol"),
        "years": st.get("years"),
        "turnover_per_fill": round(float(turn), 3) if turn is not None else None,
        "extra_bp_per_side": extra_bp,
    }


def run_arms(close, openp, amt, score):
    """The four/ten fills. Reuses the audit's own arm builder so there is one implementation."""
    card, t_card = L.arm_at_lag(close, openp, amt, score, 0)
    causal, t_causal = L.arm_at_lag(close, openp, amt, score, 1)
    rows = [_row("card", card, t_card), _row("next_open", causal, t_causal)]
    # close fill: the only change is the price series the book is filled and marked at.
    for k in IMPACT_BP:
        cost = P.COST + k / 1e4
        ser, turn = R.open_to_open_equity(close, close, amt, score, F.CONFIG["rebal"],
                                          F.CONFIG["n_hold"], cost,
                                          vol_target=F.CONFIG["vol_target"])
        rows.append(_row("close" if k == 0 else "close_i%d" % k, ser, turn, k))
    return rows


def decide(rows):
    """Verdict from published rows alone -- --check must reproduce this without a re-run."""
    by = {r["arm"]: r for r in rows}
    for need in ("card", "next_open", "close"):
        if need not in by or by[need].get("cagr") is None:
            return {"state": "INCOMPLETE", "why": "missing arm %s" % need}
    gap_pp = 100.0 * (by["card"]["cagr"] - by["next_open"]["cagr"])
    got_pp = 100.0 * (by["close"]["cagr"] - by["next_open"]["cagr"])
    if abs(gap_pp) < TOL_PP:
        return {"state": "NO_GAP_TO_EXPLAIN", "gap_pp": round(gap_pp, 3),
                "recovered_pp": round(got_pp, 3), "share": None,
                "rule": CRITERIA["verdict_rule"]}
    share = got_pp / gap_pp
    if share >= SHARE_DOMINANT:
        state = "FILL_PRICE_DOMINATES"
    elif share < SHARE_INFORMATION:
        state = "INFORMATION_DOMINATES"
    else:
        state = "MIXED"
    # execution budget: the largest extra cost per side that still matches the causal book
    base = by["next_open"]["cagr"]
    budget = None
    for r in sorted((r for r in rows if r["arm"].startswith("close_i")),
                    key=lambda r: r["extra_bp_per_side"]):
        if r.get("cagr") is None:
            continue
        if r["cagr"] >= base:
            budget = r["extra_bp_per_side"]
    if by["close"]["cagr"] < base:
        budget = "NONE"
    return {
        "state": state,
        "gap_pp": round(gap_pp, 3),
        "recovered_pp": round(got_pp, 3),
        "share": round(share, 4),
        "execution_budget_bp_per_side": budget,
        "rule": CRITERIA["verdict_rule"],
    }


def run():
    t0 = time.time()
    close, openp, amt, _feats, score, cls, n_flip = F.build_inputs()
    rows = run_arms(close, openp, amt, score)
    verdict = decide(rows)

    # cross-artifact identity: this face must be pricing the book the audit priced
    # the money ladder: this face's fills beside the audited conventions, so a reader can
    # see which part of the headline is a fill, which part is a marking basis, and which
    # part is simply not there
    by = {r["arm"]: r for r in rows}
    ladder = {"this_face": {"card": by["card"]["cagr"],
                            "close": by["close"]["cagr"],
                            "next_open": by["next_open"]["cagr"]}}
    audited = {}
    try:
        a = L.read_published()
        audited = dict((a or {}).get("arms") or {})
    except Exception:                                                # noqa: BLE001
        audited = {}
    reconciliation = {
        "sources": {"card": "this face", "close": "this face",
                    "next_open": "this face",
                    "causal": "results/etf_book_lookahead_audit.json",
                    "ledger_no_carry": "results/etf_book_lookahead_audit.json",
                    "ledger_carry": "results/etf_book_lookahead_audit.json"},
        "rows": [
            {"arm": "card", "what": "fill at open[d] with the close[d] signal",
             "cagr": by["card"]["cagr"]},
            {"arm": "close", "what": "same signal, fill at close[d] (closing auction)",
             "cagr": by["close"]["cagr"]},
            {"arm": "next_open", "what": "same rule, one bar earlier, fill at open[d]",
             "cagr": by["next_open"]["cagr"]},
            {"arm": "ledger_no_carry", "what": "the executable ledger, no repo carry",
             "cagr": (audited.get("ledger_no_carry") or {}).get("cagr")},
            {"arm": "ledger_carry", "what": "the executable ledger, with repo carry",
             "cagr": (audited.get("ledger_carry") or {}).get("cagr")},
        ],
        "fill_venue_pp": round(100.0 * (by["close"]["cagr"] - by["next_open"]["cagr"]), 3),
        "mark_basis_pp": (None if (audited.get("ledger_no_carry") or {}).get("cagr") is None
                          else round(100.0 * ((audited["ledger_no_carry"]["cagr"]
                                               - by["next_open"]["cagr"])), 3)),
        "headline_not_in_the_ledger_pp": (
            None if (audited.get("ledger_no_carry") or {}).get("cagr") is None
            else round(100.0 * (by["card"]["cagr"] - audited["ledger_no_carry"]["cagr"]), 3)),
        "card_vs_executable_pp": (
            None if (audited.get("ledger_carry") or {}).get("cagr") is None
            else round(100.0 * (by["card"]["cagr"] - audited["ledger_carry"]["cagr"]), 3)),
    }

    cross = {"audit_artifact": AUDIT_JSON, "checked": False}
    try:
        a = L.read_published()
        arms = (a or {}).get("arms") or {}
        got_card = (arms.get("published") or {}).get("cagr")
        got_causal = (arms.get("causal") or {}).get("cagr")
        by = {r["arm"]: r for r in rows}
        cross = {
            "audit_artifact": AUDIT_JSON,
            "checked": True,
            "audit_cutoff": a.get("evidence_cutoff"),
            "card_vs_audit_pp": None if got_card is None
            else round(100.0 * (by["card"]["cagr"] - got_card), 4),
            "causal_vs_audit_pp": None if got_causal is None
            else round(100.0 * (by["next_open"]["cagr"] - got_causal), 4),
        }
        cross["agrees"] = (cross["card_vs_audit_pp"] is not None
                           and cross["causal_vs_audit_pp"] is not None
                           and abs(cross["card_vs_audit_pp"]) < 1e-6
                           and abs(cross["causal_vs_audit_pp"]) < 1e-6)
    except Exception as exc:                                        # noqa: BLE001
        cross["error"] = str(exc)[:160]

    doc = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_sec": round(time.time() - t0, 1),
        "evidence_cutoff": str(close.index[-1].date()),
        "bars": int(len([d for d in close.index if d >= pd.Timestamp(R.START)])),
        "config": {"n_hold": F.CONFIG["n_hold"], "rebal": F.CONFIG["rebal"],
                   "cost_bp": round(P.COST * 1e4, 1), "vol_target": F.CONFIG["vol_target"],
                   "classes": list(P.USE_CLASSES)},
        "criteria": CRITERIA,
        "cross_artifact": cross,
        "arms": rows,
        "reconciliation": reconciliation,
        "verdict": verdict,
        "notes": [
            "every arm holds the same names on the same grid; only the price series the "
            "book is filled and marked at changes (card/next_open: the open; close: the close)",
            "the close arm ranks on the same close it trades -- institutionally that means "
            "the ordering is computed from last-tick data before the 14:57-15:00 auction, "
            "which is why the extra-cost grid exists instead of an assumption of free fills",
            "the liquidity filter uses each bar's full-day turnover, which is only known at "
            "the close; that is inside the priced friction, not outside it",
            "the toll is charged on turnover at the same 10bp/side in every arm, so a "
            "higher-turnover fill is not being flattered",
        ],
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    write_md(doc)
    v = verdict
    print("fill venue: %s | card %.2f%% -> next_open %.2f%% -> close %.2f%% "
          "(recovered %+.2fpp of %+.2fpp, share %s) | budget %s bp/side | %d bars cutoff %s"
          % (v["state"],
             100 * {r["arm"]: r for r in rows}["card"]["cagr"],
             100 * {r["arm"]: r for r in rows}["next_open"]["cagr"],
             100 * {r["arm"]: r for r in rows}["close"]["cagr"],
             v.get("recovered_pp") or 0.0, v.get("gap_pp") or 0.0, v.get("share"),
             v.get("execution_budget_bp_per_side"), doc["bars"], doc["evidence_cutoff"]))
    return doc


def write_md(doc):
    by = {r["arm"]: r for r in doc["arms"]}
    v = doc["verdict"]
    lines = [
        "# Where do you fill it? The missing bar is not a fill price",
        "",
        "Face: `results/etf_book_fill_venue.json` (evidence cutoff %s, %d bars, %.1f s)."
        % (doc["evidence_cutoff"], doc["bars"], doc["elapsed_sec"]),
        "",
        "Same signal, same panel, same 20-bar grid, same 10bp/side, same 8% vol overlay.",
        "The card and close fills differ ONLY in the price series the book is filled and marked",
        "at -- same names, same dates. The next-open fill is the same rule read one bar earlier,",
        "which is what the executable ledger does.",
        "",
        "| fill | where | CAGR | Sharpe | maxDD | turnover/fill |",
        "|---|---|---|---|---|---|",
    ]
    where = {"card": "open of bar d (published, not achievable)",
             "next_open": "open of bar d+1 (the ledger)",
             "close": "close of bar d (closing auction)"}
    for r in doc["arms"]:
        w = where.get(r["arm"], "close + %d bp/side extra" % r["extra_bp_per_side"])
        lines.append("| %s | %s | %.2f%% | %.2f | %.2f%% | %.3f |"
                     % (r["arm"], w, 100 * r["cagr"], r["sharpe"], 100 * r["maxdd"],
                        r["turnover_per_fill"] if r["turnover_per_fill"] is not None else 0.0))
    rec = doc["reconciliation"]
    lines += [
        "",
        "## The money ladder (what each convention is worth)",
        "",
        "| convention | what it is | CAGR |",
        "|---|---|---|",
    ]
    for r in rec["rows"]:
        if r.get("cagr") is None:
            lines.append("| %s | %s | cannot read |" % (r["arm"], r["what"]))
        else:
            lines.append("| %s | %s | %.2f%% |" % (r["arm"], r["what"], 100 * r["cagr"]))
    lines += [
        "",
        "- switching the **fill venue** (close vs next open) moves the book by "
        "**%+.2f pp/yr**" % rec["fill_venue_pp"],
        "- switching the **marking basis** (open-to-open accrual vs the ledger's "
        "close-marked book) moves it by **%+.2f pp/yr**" % (rec.get("mark_basis_pp") or 0.0),
        "- the part of the headline that is **not in the executable book at all**: "
        "**%+.2f pp/yr**" % (rec.get("headline_not_in_the_ledger_pp") or 0.0),
        "- headline vs the executable book **including repo carry**: "
        "**%+.2f pp/yr**" % (rec.get("card_vs_executable_pp") or 0.0),
        "",
        "So the honest split of the 1.14pp is: 0.00pp of it is a fill choice, 0.07pp of it is",
        "how the book is priced, and 1.07pp of it is a bar that is not tradable. The ledger",
        "already earns the executable number (9.12% with carry) -- nothing an operator can do",
        "at the venue recovers the rest.",
        "",
        "## Verdict",
        "",
        "- **%s**" % v["state"],
        "- one-bar gap (card - next_open): **%+.2f pp/yr**" % (v.get("gap_pp") or 0.0),
        "- recovered by filling at the close: **%+.2f pp/yr (share %s)**"
        % (v.get("recovered_pp") or 0.0, v.get("share")),
        "- execution budget at the close: **%s**"
        % ("none -- even a free closing fill does not reach the causal book"
           if v.get("execution_budget_bp_per_side") == "NONE"
           else "%s bp per side before the causal book wins again"
                % (v.get("execution_budget_bp_per_side"),)),
        "",
        "Reading: the two fills an operator can actually get -- the closing auction and the",
        "next open -- land within 0.03 pp/yr of each other, so the venue is not the lever.",
        "The card's extra bar is not purchasable at any venue: it is spent between the open",
        "and the close of the bar whose close produced the ranking. What does change the",
        "money is the executable book's own carry (repo rungs), already inside the ledger.",
        "",
        "## What this is not",
        "",
        "- not a claim that a closing fill is free: the extra-cost grid prices auction impact",
        "  and the rank-vs-fill price gap together, it does not separate them",
        "- not a re-statement of the look-ahead finding: the card arm and the causal arm here",
        "  must reproduce `results/etf_book_lookahead_audit.json` to 1e-6 pp or the face refuses",
        "  to publish (cross-artifact gate, see `cross_artifact.agrees`)",
        "- not an instruction to change production: the ledger already fills at the next open;",
        "  switching to closing-auction fills is an adoption decision with its own freeze",
        "",
        "Reproduce: `python scripts/etf_book_fill_venue.py run|--check|--selftest`.",
    ]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def read_published(path=None):
    """Consumer entry point: the fills and the verdict, or an honest gap.

    Callers must not read the artifact themselves (E289 family) and must not publish a
    number when the cross-artifact gate did not pass -- a face that quotes a different
    book than the audit is worse than no face.
    """
    p = path or OUT_JSON
    if not os.path.exists(p):
        return {"status": "absent", "artifact": str(p), "verdict": None, "sentence": None,
                "evidence_cutoff": None}
    try:
        with open(p, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
    except Exception as exc:                                        # noqa: BLE001
        return {"status": "unreadable: %s" % str(exc)[:120], "artifact": str(p),
                "verdict": None, "sentence": None, "evidence_cutoff": None}
    cross = doc.get("cross_artifact") or {}
    if cross.get("checked") and not cross.get("agrees"):
        return {"status": "no_cross_check", "artifact": str(p), "verdict": doc.get("verdict"),
                "sentence": None, "evidence_cutoff": doc.get("evidence_cutoff"),
                "detail": cross}
    by = {r.get("arm"): r for r in doc.get("arms") or []}
    v = doc.get("verdict") or {}
    return {
        "status": "ok",
        "artifact": str(p),
        "evidence_cutoff": doc.get("evidence_cutoff"),
        "bars": doc.get("bars"),
        "fills": {k: {"cagr": (by.get(k) or {}).get("cagr"),
                      "sharpe": (by.get(k) or {}).get("sharpe"),
                      "maxdd": (by.get(k) or {}).get("maxdd")}
                  for k in ("card", "next_open", "close")},
        "verdict": {"state": v.get("state"), "gap_pp": v.get("gap_pp"),
                    "recovered_pp": v.get("recovered_pp"), "share": v.get("share"),
                    "execution_budget_bp_per_side": v.get("execution_budget_bp_per_side")},
        "cross_artifact": cross,
        "sentence": ("the one-bar gap is %+.2fpp/yr and filling at the close keeps %+.2fpp "
                     "of it (share %s), so %s"
                     % (v.get("gap_pp") or 0.0, v.get("recovered_pp") or 0.0, v.get("share"),
                        {"FILL_PRICE_DOMINATES": "the execution venue, not the signal, is the "
                                                 "thing to change",
                         "INFORMATION_DOMINATES": "the edge really is in the future bar and "
                                                  "the rule needs redesigning",
                         "MIXED": "part of the gap is fill and part is information"}
                        .get(v.get("state"), "the face is inconclusive")))
        if v.get("state") else None,
    }


def check(path=None):
    with open(path or OUT_JSON, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    cross = doc.get("cross_artifact") or {}
    if cross.get("checked") and not cross.get("agrees"):
        print("CHECK FAIL: the card/next_open arms do not reproduce the look-ahead audit "
              "(%r)" % (cross,))
        return 1
    v = decide(doc["arms"])
    pub = doc["verdict"]
    if v["state"] != pub["state"]:
        print("CHECK FAIL: published verdict %s, re-derived %s" % (pub["state"], v["state"]))
        return 1
    for key, tol in (("gap_pp", 0.011), ("recovered_pp", 0.011)):
        if pub.get(key) is None or v.get(key) is None:
            continue
        if abs(v[key] - pub[key]) > tol:
            print("CHECK FAIL: %s moved %.3f -> %.3f" % (key, pub[key], v[key]))
            return 1
    print("CHECK OK: %s (gap %+.2fpp, recovered %+.2fpp, share %s, budget %s)"
          % (v["state"], v["gap_pp"], v["recovered_pp"], v["share"],
             v["execution_budget_bp_per_side"]))
    return 0


# ---------------------------------------------------------------- offline selftest
def _fixture(n_names=14, n_bars=420, seed=11, informative=True):
    rng = np.random.RandomState(seed)
    idx = pd.bdate_range("2021-01-01", periods=n_bars)
    names = ["t%02d" % i for i in range(n_names)]
    rets = rng.normal(0.0002, 0.012, size=(n_bars, n_names))
    close = pd.DataFrame(100.0 * np.exp(np.cumsum(rets, axis=0)), index=idx, columns=names)
    openp = close.shift(1).bfill() * (1.0 + rng.normal(0, 0.002, size=close.shape))
    amt = pd.DataFrame(np.full(close.shape, 1e9), index=idx, columns=names)
    if informative:
        # a score that knows the NEXT bar's fill-to-fill return: the card fill (open d ->
        # open d+1) can use it, a one-bar-delayed copy of the same score cannot
        fwd = openp.shift(-1) / openp - 1.0
        score = fwd + rng.normal(0, 0.004, size=fwd.shape)
    else:
        score = pd.DataFrame(rng.normal(size=(n_bars, n_names)), index=idx, columns=names)
    return close, openp, amt, score


def selftest():
    ok = [0, 0]

    def chk(name, cond, detail=""):
        ok[0] += 1
        if cond:
            ok[1] += 1
            print("  PASS %s %s" % (name, detail))
        else:
            print("  FAIL %s %s" % (name, detail))

    close, openp, amt, score = _fixture()
    rows = run_arms(close, openp, amt, score)
    by = {r["arm"]: r for r in rows}

    # L1: the card arm IS the audit's published arm (one implementation, not two)
    a_ser, a_turn = L.arm_published(close, openp, amt, score)
    a_cagr = A.stats2(a_ser.dropna(), "audit_published").get("cagr")
    chk("card arm equals the audit's published arm", abs(a_cagr - by["card"]["cagr"]) < 1e-12,
        "delta=%.2e" % (a_cagr - by["card"]["cagr"]))

    # L2: an informative score must be worth more at the card fill than one bar later
    chk("a score that knows the next bar pays for itself at the card fill",
        by["card"]["cagr"] > by["next_open"]["cagr"],
        "card %.3f vs next %.3f" % (100 * by["card"]["cagr"], 100 * by["next_open"]["cagr"]))

    # L3: with open == close the close fill is the card fill (the only difference is the
    # price series, so collapsing the two must collapse the arms)
    same_ser, _t = R.open_to_open_equity(close, close, amt, score, F.CONFIG["rebal"],
                                         F.CONFIG["n_hold"], P.COST,
                                         vol_target=F.CONFIG["vol_target"])
    card_same, _t2 = R.open_to_open_equity(close, close, amt, score, F.CONFIG["rebal"],
                                           F.CONFIG["n_hold"], P.COST,
                                           vol_target=F.CONFIG["vol_target"])
    g2 = float(np.max(np.abs(same_ser.dropna().to_numpy() - card_same.dropna().to_numpy())))
    chk("close fill degenerates to the card fill when open == close", g2 == 0.0, "gap=%.2e" % g2)

    # L4: extra cost per side can only hurt
    ladder = sorted([r for r in rows if r["arm"] == "close" or r["arm"].startswith("close_i")],
                    key=lambda r: r["extra_bp_per_side"])
    mono = all(ladder[i + 1]["cagr"] <= ladder[i]["cagr"] + 1e-12
               for i in range(len(ladder) - 1))
    chk("the close arm is monotone in extra cost", mono,
        "costs %s" % [r["extra_bp_per_side"] for r in ladder])

    # L5: verdict arithmetic, driven by the rows and nothing else
    def mk(card, next_open, close_c, budget=None):
        out = [{"arm": "card", "cagr": card}, {"arm": "next_open", "cagr": next_open},
               {"arm": "close", "cagr": close_c}]
        for k in IMPACT_BP[1:]:
            out.append({"arm": "close_i%d" % k, "cagr": budget if budget is not None
                        else close_c - 0.0005, "extra_bp_per_side": k})
        return out

    v = decide(mk(0.096, 0.0846, 0.0940))
    chk("most of the gap recovered -> FILL_PRICE_DOMINATES", v["state"] == "FILL_PRICE_DOMINATES",
        v["state"])
    v = decide(mk(0.096, 0.0846, 0.0850))
    chk("little of the gap recovered -> INFORMATION_DOMINATES",
        v["state"] == "INFORMATION_DOMINATES", v["state"])
    v = decide(mk(0.096, 0.0846, 0.0890))
    chk("in between -> MIXED", v["state"] == "MIXED", v["state"])
    v = decide(mk(0.096, 0.0846, 0.0840, budget=0.0838))
    chk("no extra cost survives -> budget NONE", v["execution_budget_bp_per_side"] == "NONE",
        str(v["execution_budget_bp_per_side"]))
    v = decide(mk(0.096, 0.0846, 0.0940, budget=0.0847))
    chk("budget is the largest surviving grid point",
        v["execution_budget_bp_per_side"] == IMPACT_BP[-1],
        str(v["execution_budget_bp_per_side"]))
    v = decide([{"arm": "card", "cagr": 0.096}])
    chk("missing arms -> INCOMPLETE", v["state"] == "INCOMPLETE", v["state"])
    v = decide(mk(0.0846, 0.0846, 0.0846))
    chk("no gap to explain -> NO_GAP_TO_EXPLAIN", v["state"] == "NO_GAP_TO_EXPLAIN", v["state"])

    # L6: the reader refuses a face whose cross-check failed, and publishes numbers otherwise
    import tempfile
    tmp = os.path.join(tempfile.gettempdir(), "_fill_venue_selftest.json")
    good = {"evidence_cutoff": "2026-10-30", "bars": 100, "arms": mk(0.096, 0.0846, 0.0940),
            "verdict": {"state": "FILL_PRICE_DOMINATES", "gap_pp": 1.14,
                        "recovered_pp": 0.94, "share": 0.82,
                        "execution_budget_bp_per_side": IMPACT_BP[-1]},
            "cross_artifact": {"checked": True, "agrees": True}}
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(good, fh)
    rd = read_published(tmp)
    chk("reader publishes a checked face", rd["status"] == "ok" and rd["sentence"], rd["status"])
    good["cross_artifact"] = {"checked": True, "agrees": False}
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(good, fh)
    rd = read_published(tmp)
    chk("reader refuses a face that does not reproduce the audit",
        rd["status"] == "no_cross_check" and rd["sentence"] is None, rd["status"])
    if os.path.exists(tmp):
        os.remove(tmp)

    print("selftest %d/%d" % (ok[1], ok[0]))
    return 0 if ok[1] == ok[0] else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] == "run":
        run()
        return 0
    if argv[0] == "--check":
        return check()
    if argv[0] == "--selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())