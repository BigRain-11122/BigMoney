"""One size decision out of three rulers: denominator, window length, class universe.

r1448 priced each ruler on its own and left the arithmetic to the 2026-11-11 rebalance.
This face puts the rulers in ONE table, prices the cell they never measured (graded
universe x the common window), and asks the only question a desk can act on:

    what is the smallest size that every ruler agrees is defensible?

Nothing here reprices the book: every cell is the same engine as the published arm, and
the published ticket is reproduced first (identity legs) so the table cannot drift away
from the money that is running.

k = min(1, beta_target / beta).  k is a scale choice, not an optimum (r1447).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TICKET_GLOB = "results/etf_book_order/TICKET-*.json"
SPLIT_RECEIPT = "results/etf_book_class_beta_split.json"
OUT = os.path.join(BASE, "results", "etf_book_size_rulers_decision.json")

GRADED = ("equity", "commodity", "convertible")
MIN_OBS = 60
SIZE_TOL = 0.005          # 0.5pp on k = the same tolerance the class split uses
DECISION_DATE = "2026-11-11"

RULERS = ("denominator", "window", "universe", "window_x_universe")


def k_from_beta(beta, target):
    """De-risking only, never leverage -- the engine's own clip (etf_book_order.k_schedule)."""
    if beta is None or beta <= 1e-6:
        return None
    return float(min(1.0, max(0.0, float(target) / float(beta))))


def _read_json(rel):
    p = os.path.join(BASE, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def latest_ticket():
    files = sorted(glob.glob(os.path.join(BASE, TICKET_GLOB)))
    if not files:
        return None, None
    with open(files[-1], encoding="utf-8") as f:
        return os.path.basename(files[-1]), json.load(f)


def decide(cells, ticket):
    """The desk sentence.  Pure function of published cells + the ticket (no panel)."""
    target = ticket.get("beta_target")
    nav = ticket.get("ticket", {}).get("nav")
    k_now = ticket.get("k_now")
    known = {n: c for n, c in cells.items() if c.get("k") is not None}
    unreadable = [n for n, c in cells.items() if c.get("k") is None]
    out = {
        "k_now": None if k_now is None else round(float(k_now), 6),
        "nav_cny": nav,
        "deployed_now_cny": None if (k_now is None or nav is None) else round(float(k_now) * nav, 2),
        "cells_readable": sorted(known),
        "cells_unreadable": unreadable,
        "rulers": {n: {"k": None if c.get("k") is None else round(float(c["k"]), 6),
                       "delta_vs_now_pp": None if (c.get("k") is None or k_now is None)
                       else round(100.0 * (float(c["k"]) - float(k_now)), 2)}
                   for n, c in cells.items()},
    }
    if unreadable or k_now is None or nav is None or not known:
        out.update({"verdict": "UNREADABLE",
                    "sentence": "a ruler could not be measured; an unread ruler is not "
                                "evidence that the sizes agree",
                    "k_floor": None, "k_ceiling": None})
        return out
    ks = {n: float(c["k"]) for n, c in known.items()}
    k_lo, k_hi = min(ks.values()), max(ks.values())
    # the widest mover, named -- a range nobody can attribute is a shrug, not a decision
    mover = max(ks, key=lambda n: abs(ks[n] - float(k_now)))
    agree = (k_hi - k_lo) <= SIZE_TOL + 1e-12
    at_now = all(abs(k - float(k_now)) <= SIZE_TOL + 1e-12 for k in ks.values())
    out.update({
        "k_floor": round(k_lo, 6),
        "k_ceiling": round(k_hi, 6),
        "deployed_floor_cny": round(k_lo * float(nav), 2),
        "deployed_ceiling_cny": round(k_hi * float(nav), 2),
        "range_pp": round(100.0 * (k_hi - k_lo), 2),
        "widest_mover": mover,
        "widest_mover_pp": round(100.0 * (ks[mover] - float(k_now)), 2),
        "n_below_money": sum(1 for k in ks.values() if k < float(k_now) - SIZE_TOL),
        "n_above_money": sum(1 for k in ks.values() if k > float(k_now) + SIZE_TOL),
        "the_size_in_force_is_the_floor": abs(k_lo - float(k_now)) <= 1e-9,
        "the_size_in_force_is_the_ceiling": abs(k_hi - float(k_now)) <= 1e-9,
        "verdict": ("RULERS_AGREE_AT_SIZE_IN_FORCE" if agree and at_now else
                    "RULERS_AGREE_OFF_SIZE_IN_FORCE" if agree else
                    "SIZE_IS_A_RULER_CHOICE"),
    })
    # prose is derived from the flags, never written alongside them (r1449: the first version
    # printed "the money is at the ceiling" on a table whose ceiling was above the money)
    if out["verdict"] == "RULERS_AGREE_AT_SIZE_IN_FORCE":
        out["sentence"] = ("every ruler lands within %.1fpp of k=%.6f; the size in force is "
                           "not a ruler artefact" % (100.0 * SIZE_TOL, float(k_now)))
    elif out["verdict"] == "RULERS_AGREE_OFF_SIZE_IN_FORCE":
        out["sentence"] = ("the rulers agree with each other but not with the money: k=%.6f in "
                           "force vs %.6f agreed" % (float(k_now), k_lo))
    else:
        where = ("at the floor" if out["the_size_in_force_is_the_floor"] else
                 "at the ceiling" if out["the_size_in_force_is_the_ceiling"] else "inside")
        out["sentence"] = (
            "the same rule priced on the same panel lands between k=%.6f and k=%.6f (%.2fpp of "
            "range, widest mover=%s %+.2fpp); the money sits %s that range at k=%.6f -- %d "
            "readings below it, %d above it, floor CNY %s against CNY %s deployed"
            % (k_lo, k_hi, 100.0 * (k_hi - k_lo), mover, 100.0 * (ks[mover] - float(k_now)),
               where, float(k_now), out["n_below_money"], out["n_above_money"],
               format(round(k_lo * float(nav), 0), ",.0f"),
               format(round(float(k_now) * float(nav), 0), ",.0f")))
    return out


def published_face():
    """Receipt-only face, used by --check and as the pre-panel skeleton."""
    name, tk = latest_ticket()
    if tk is None:
        return {"face": "etf_book_size_rulers_decision", "verdict": "NO_TICKET",
                "sentence": "no ticket on disk; nothing to size"}
    split = _read_json(SPLIT_RECEIPT) or {}
    return {"face": "etf_book_size_rulers_decision",
            "ticket_file": name,
            "evidence_cutoff": tk.get("evidence_cutoff"),
            "decision_date": DECISION_DATE,
            "beta_target": tk.get("beta_target"),
            "split_receipt": SPLIT_RECEIPT if split else None,
            "split_window": (split.get("split") or {}).get("window_span"),
            "panel_work": "not run (file-only face; use `run` for the table)"}


def _ols_beta(rp, rm):
    import numpy as np
    var = float(rm.var())
    if not np.isfinite(var) or var <= 0:
        return None
    b = float(rp.cov(rm)) / var
    return b if np.isfinite(b) else None


def run():
    import numpy as np
    import pandas as pd

    sys.path.insert(0, BASE)
    sys.path.insert(0, os.path.join(BASE, "scripts"))
    from scripts import etf_composite_pf as F
    from scripts import etf_phase_beta_target as BT
    from scripts import etf_book_order as BO
    from scripts import etf_equity_alpha as AE
    from scripts import etf_book_class_beta_split as CS
    from scripts.etf_asset_class import classify

    face = published_face()
    if face.get("verdict") == "NO_TICKET":
        return face
    name, tk = latest_ticket()
    target = tk.get("beta_target")
    nav = tk["ticket"]["nav"]
    k_now = tk.get("k_now")

    print("panel: loading", flush=True)
    close, openp, amt, feats = F.build_panel()
    if BO.REPAIR_PANEL:
        close, openp, n_flip = AE.repair_flips(close, openp)
        print("panel: repaired %d flip prints" % n_flip, flush=True)
    classes = pd.Series(classify(list(close.columns)))
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        return dict(face, verdict="MECHANISM_FAULT", sentence="no market proxy on the panel")
    mkt = close[mkt_col]

    order = tk["ticket"]["order"]
    names = [r["symbol"] for r in order]
    dec_bar = pd.Timestamp(tk.get("book_decided_at")) if tk.get("book_decided_at") else close.index[-1]

    # ---- arm as published (all classes) and arm on the graded universe, same engine
    arms = {}
    for tag, cols in (("published", [c for c in close.columns if classes[c] in CS._keep_classes()]),
                      ("graded", [c for c in close.columns if classes[c] in GRADED])):
        score = F.build_score(close[cols], amt[cols], feats)
        ser, _to, _gap = F.run_next_open(close[cols], openp[cols], amt[cols], feats,
                                        BO.REBAL, n_hold=F.N_HOLD, cost=F.COST, score=score)
        idx = ser.index.intersection(mkt.index)
        sched = BO.k_schedule(BT.rets(ser.reindex(idx)), BT.rets(mkt.reindex(idx)),
                              BO.DEFAULT_BETA)
        if not sched:
            return dict(face, verdict="MECHANISM_FAULT", sentence="%s beta schedule empty" % tag)
        arms[tag] = {"series": ser, "idx": idx, "sched": sched,
                     "k": float(sched[-1][1]), "beta": float(sched[-1][2]),
                     "symbols": len(cols)}
        print("arm %s: %d symbols, k=%.6f beta=%.6f" % (tag, len(cols), arms[tag]["k"],
                                                       arms[tag]["beta"]), flush=True)

    # ---- the common window, re-derived from the ticket names (not read from the receipt)
    px = close.loc[close.index <= dec_bar]
    firsts = {}
    for s in names:
        if s not in px.columns:
            continue
        v = px[s].pct_change().dropna()
        if len(v):
            firsts[s] = v.index[0]
    span = {}
    if firsts:
        limiter = max(firsts, key=lambda s: firsts[s])
        span = {"first": str(firsts[limiter].date()), "last": str(dec_bar.date()),
                "limited_by": limiter}

    def beta_on_window(arm, span):
        if not span:
            return None
        rp_all = BT.rets(arm["series"].reindex(arm["idx"]))
        rm_all = BT.rets(mkt.reindex(arm["idx"]))
        mask = ((rp_all.index >= pd.Timestamp(span["first"]))
                & (rp_all.index <= pd.Timestamp(span["last"])))
        rp_w, rm_w = rp_all[mask], rm_all[mask]
        if len(rp_w) < MIN_OBS:
            return None
        b = _ols_beta(rp_w, rm_w)
        return None if b is None else {"beta": b, "bars": int(len(rp_w))}

    # ---- the denominator ruler: today's mix held over the window, fully invested
    try:
        weights = [float(r["weight"]) for r in order]
        split = CS.name_stats(close, mkt_col, names, weights,
                              classes, end_bar=dec_bar)
        beta_static_norm = split.get("static_composition_beta_normalized")
    except Exception as exc:                      # the cell must not sink the face
        split, beta_static_norm = {}, None
        print("split: FAILED (%s) -- denominator cell unreadable" % exc, flush=True)

    cells, notes = {}, {}
    cells["baseline_published"] = {"beta": arms["published"]["beta"],
                                   "k": arms["published"]["k"],
                                   "bars": int(len(arms["published"]["idx"])),
                                   "universe": "all classes on the panel",
                                   "window": "full"}
    w_pub = beta_on_window(arms["published"], span)
    cells["window"] = {"beta": None if w_pub is None else w_pub["beta"],
                       "k": None if w_pub is None else k_from_beta(w_pub["beta"], target),
                       "bars": None if w_pub is None else w_pub["bars"],
                       "universe": "all classes on the panel",
                       "window": "common (%s..%s)" % (span.get("first"), span.get("last"))}
    cells["universe"] = {"beta": arms["graded"]["beta"], "k": arms["graded"]["k"],
                         "bars": int(len(arms["graded"]["idx"])),
                         "universe": "graded (%s)" % ",".join(GRADED), "window": "full"}
    w_gr = beta_on_window(arms["graded"], span)
    cells["window_x_universe"] = {"beta": None if w_gr is None else w_gr["beta"],
                                  "k": None if w_gr is None else k_from_beta(w_gr["beta"], target),
                                  "bars": None if w_gr is None else w_gr["bars"],
                                  "universe": "graded (%s)" % ",".join(GRADED),
                                  "window": "common (%s..%s)" % (span.get("first"), span.get("last"))}
    cells["denominator"] = {"beta": beta_static_norm,
                            "k": k_from_beta(beta_static_norm, target) if beta_static_norm else None,
                            "bars": split.get("book_bars_complete_case"),
                            "universe": "today's 5 names, 100% invested",
                            "window": "common",
                            "note": "static composition, not a path: only comparable with the "
                                    "path rows because it is divided by covered weight"}
    notes["denominator"] = ("the sized mix is %.1f%% invested; dividing by covered weight puts it "
                            "on the path's denominator (r1448 unit note)"
                            % (100.0 * (split.get("weight_covered") or 0.0)))

    def _b(x):
        return None if x is None else bool(x)

    pub_split = _read_json(SPLIT_RECEIPT) or {}
    pub_span = (pub_split.get("split") or {}).get("window_span") or {}
    # the engine's beta_hat is the EXPANDING slope at the last decision bar, and the schedule
    # steps every REBAL bars -- so the last decision bar is not necessarily the last panel bar.
    # Re-deriving it on its own bar is the leg; comparing it to a full-sample OLS would fail
    # for a reason that has nothing to do with a ruler (self-caught, r1449).
    bar_last = arms["published"]["sched"][-1][0]
    rp_full = BT.rets(arms["published"]["series"].reindex(arms["published"]["idx"]))
    rm_full = BT.rets(mkt.reindex(arms["published"]["idx"]))
    cov_e = rp_full.expanding(min_periods=2).cov(rm_full)
    var_e = rm_full.expanding(min_periods=2).var()
    beta_at_bar = None
    if bar_last in cov_e.index and var_e.get(bar_last) and var_e.get(bar_last) > 0:
        beta_at_bar = float(cov_e.get(bar_last) / var_e.get(bar_last))
    legs = {
        "k_from_beta_reproduces_engine": _b(
            abs(k_from_beta(arms["published"]["beta"], target) - arms["published"]["k"]) <= 1e-9),
        "expanding_beta_at_decision_bar_reproduced": _b(
            None if beta_at_bar is None else abs(beta_at_bar - arms["published"]["beta"]) <= 1e-9),
        "ticket_k_reproduced": _b(None if k_now is None
                                   else abs(arms["published"]["k"] - float(k_now)) <= 1e-6),
        "ticket_book_amount_is_k_times_nav_minus_lots": _b(
            None if tk["ticket"].get("underspend_pct") is None
            else abs(float(tk["ticket"]["book_amount"])
                     - (float(k_now) * float(nav)
                        - float(nav) * float(tk["ticket"]["underspend_pct"]) / 100.0)) <= 1.0),
        "window_recomputed_matches_receipt": _b(
            None if (not pub_span or not span) else
            (pub_span.get("first") == span.get("first")
             and pub_span.get("last") == span.get("last")
             and (pub_split.get("split") or {}).get("window_limited_by") == span.get("limited_by"))),
        "graded_k_reproduces_split_receipt": _b(
            None if not (pub_split.get("graded_arm") or {}).get("k")
            else abs(float(pub_split["graded_arm"]["k"]) - arms["graded"]["k"]) <= 1e-6),
    }
    broken = [k for k, v in legs.items() if v is False]

    d = decide(cells, tk)
    d.update({
        "face": "etf_book_size_rulers_decision",
        "evidence_cutoff": tk.get("evidence_cutoff"),
        "ticket_file": name,
        "decision_date": DECISION_DATE,
        "beta_target": target,
        "panel_work": "run",
        "market_proxy": mkt_col,
        "window": span,
        "cells": cells,
        "cell_notes": notes,
        "arms": {t: {"symbols": a["symbols"], "beta": round(a["beta"], 6), "k": round(a["k"], 6),
                     "decision_bar": str(a["sched"][-1][0].date()
                                         if hasattr(a["sched"][-1][0], "date")
                                         else a["sched"][-1][0])}
                 for t, a in arms.items()},
        "identity_legs": legs,
        "identity_broken": broken,
        "prereg_requirements": [
            "1. fix the ruler before looking: which window (common vs full) and which universe "
            "(all vs graded) is the declared measurement universe",
            "2. fix the denominator rule (path beta, or static mix divided by covered weight) "
            "and forbid mixing the two inside one table",
            "3. if the declared size is the floor rather than the ceiling, sign the risk budget "
            "it implies (target 0.20 is a budget, not an optimum -- r1447)",
            "4. carry the chosen size into the 2026-11-11 ticket and print the three unused "
            "readings next to it so the choice stays visible",
        ],
    })
    if broken:
        d["verdict"] = "IDENTITY_BROKEN"
        d["sentence"] = ("a ruler disagrees with a published number (%s); the table is not "
                         "evidence until that is resolved" % ", ".join(broken))
    return d


def md_lines(d):
    out = ["# One size, three rulers", "",
           "ticket `%s` | evidence cutoff %s | decision date %s | beta target %s"
           % (d.get("ticket_file"), d.get("evidence_cutoff"), d.get("decision_date"),
              d.get("beta_target")), ""]
    if d.get("verdict") == "NO_TICKET":
        out.append("no ticket on disk")
        return out
    out += ["**%s** — %s" % (d.get("verdict"), d.get("sentence") or ""), ""]
    rows = d.get("cells") or {}
    if rows:
        out += ["| cell | universe | window | beta | k | vs money (pp) |",
                "|---|---|---|---|---|---|"]
        k_now = d.get("k_now")
        for n, c in rows.items():
            b = c.get("beta")
            k = c.get("k")
            out.append("| %s | %s | %s | %s | %s | %s |" % (
                n, c.get("universe"), c.get("window"),
                "-" if b is None else "%.6f" % b,
                "-" if k is None else "%.6f" % k,
                "-" if (k is None or k_now is None) else "%+.2f" % (100.0 * (k - k_now))))
        out.append("")
    if d.get("k_floor") is not None:
        out += ["- range: k %.6f .. %.6f (%.2fpp) = CNY %s .. %s"
                % (d["k_floor"], d["k_ceiling"], d["range_pp"],
                   format(d["deployed_floor_cny"], ",.0f"),
                   format(d["deployed_ceiling_cny"], ",.0f")),
                "- money in force: CNY %s at k=%.6f" % (format(d["deployed_now_cny"], ",.0f"),
                                                        d["k_now"]),
                "- widest mover: %s %+.2fpp" % (d["widest_mover"], d["widest_mover_pp"]), ""]
    if d.get("cell_notes"):
        for n, s in d["cell_notes"].items():
            out.append("- %s: %s" % (n, s))
        out.append("")
    legs = d.get("identity_legs") or {}
    if legs:
        out += ["identity legs: %d pass / %d fail%s"
                % (sum(1 for v in legs.values() if v is True),
                   sum(1 for v in legs.values() if v is False),
                   "" if not d.get("identity_broken")
                   else " (" + ", ".join(d["identity_broken"]) + ")"), ""]
    if d.get("prereg_requirements"):
        out.append("prereg requirements for %s:" % d.get("decision_date"))
        for r in d["prereg_requirements"]:
            out.append("- " + r)
    return out


def check():
    """Re-derive the decision from the receipt's own cells.  No panel, no network."""
    d = _read_json("results/etf_book_size_rulers_decision.json")
    if not d:
        print("[check] no receipt at %s" % OUT)
        return 2
    name, tk = latest_ticket()
    if tk is None:
        print("[check] no ticket on disk")
        return 2
    redo = decide(d.get("cells") or {}, tk)
    fails = []
    for k in ("verdict", "k_floor", "k_ceiling", "deployed_floor_cny", "widest_mover",
              "widest_mover_pp", "range_pp"):
        if redo.get(k) != d.get(k):
            fails.append("%s: receipt=%r rederive=%r" % (k, d.get(k), redo.get(k)))
    if d.get("ticket_file") != name:
        fails.append("receipt priced %r, newest ticket is %r (a stale receipt)" % (
            d.get("ticket_file"), name))
    print("[check] %d field(s) re-derived, %d mismatch" % (7, len(fails)))
    for f in fails:
        print("  MISMATCH " + f)
    return 0 if not fails else 1


def selftest():
    """Legs that can fail: a fixture that only ever turns green is not evidence."""
    fails = []

    def leg(cond, msg):
        if not cond:
            fails.append(msg)

    tk = {"beta_target": 0.20, "k_now": 0.460253,
          "ticket": {"nav": 1000000.0, "book_amount": 459796.3}}
    base = {"beta": 0.434543, "k": 0.460253}

    # L1 the clip is the engine's clip: de-risking only
    leg(k_from_beta(0.10, 0.20) == 1.0, "L1 beta below target must clip to 1.0, got %r"
        % (k_from_beta(0.10, 0.20),))
    leg(abs(k_from_beta(0.40, 0.20) - 0.5) < 1e-12, "L1 target/beta arithmetic")
    leg(k_from_beta(0.0, 0.20) is None, "L1 a zero beta must read None, not 1.0")

    # L2 all rulers equal the money -> AGREE_AT
    same = {"baseline_published": dict(base), "window": dict(base), "universe": dict(base)}
    d = decide(same, tk)
    leg(d["verdict"] == "RULERS_AGREE_AT_SIZE_IN_FORCE", "L2 got %s" % d["verdict"])
    leg(d["range_pp"] == 0.0, "L2 range must be 0.0, got %r" % (d["range_pp"],))

    # L3 one ruler moves -> the widest mover is named, the floor is the minimum
    moved = dict(same)
    moved["window"] = {"beta": 0.48465, "k": 0.412669}
    d = decide(moved, tk)
    leg(d["verdict"] == "SIZE_IS_A_RULER_CHOICE", "L3 got %s" % d["verdict"])
    leg(d["widest_mover"] == "window", "L3 widest mover %r" % d["widest_mover"])
    leg(abs(d["k_floor"] - 0.412669) < 1e-9, "L3 floor must be the minimum, got %r" % d["k_floor"])
    leg(d["the_size_in_force_is_the_ceiling"] is True, "L3 the money is at the ceiling")
    leg(abs(d["deployed_floor_cny"] - 412669.0) < 1.0, "L3 floor CNY %r" % d["deployed_floor_cny"])

    # L4 a ruler above the money is NOT the floor (the money cannot be raised by this table)
    up = dict(same)
    up["denominator"] = {"beta": 0.367361, "k": 0.544421}
    d = decide(up, tk)
    leg(d["the_size_in_force_is_the_ceiling"] is False,
        "L4 a ceiling above the money must be reported as such")
    leg(d["k_ceiling"] > d["k_now"], "L4 ceiling %r" % (d["k_ceiling"],))

    # L5 an unread ruler is UNREADABLE, not agreement (r98: unknown is not empty)
    miss = dict(same)
    miss["window_x_universe"] = {"beta": None, "k": None}
    d = decide(miss, tk)
    leg(d["verdict"] == "UNREADABLE", "L5 got %s" % d["verdict"])
    leg(d["cells_unreadable"] == ["window_x_universe"], "L5 unreadable list %r"
        % (d["cells_unreadable"],))

    # L6 tolerance boundary is inclusive on both sides
    edge = dict(same)
    edge["window"] = {"beta": 0.434543, "k": 0.460253 - SIZE_TOL}
    d = decide(edge, tk)
    leg(d["verdict"] == "RULERS_AGREE_AT_SIZE_IN_FORCE",
        "L6 exactly at tolerance must agree, got %s" % d["verdict"])

    # L7 the range must contain every cell it was derived from
    d = decide(moved, tk)
    for n, c in moved.items():
        leg(d["k_floor"] - 1e-12 <= c["k"] <= d["k_ceiling"] + 1e-12,
            "L7 cell %s at %r outside the printed range" % (n, c["k"]))

    # L8 the markdown prints every cell (a table that drops a row hides the mover)
    d = decide(moved, tk)
    d.update({"face": "x", "ticket_file": "t", "cells": moved})
    txt = "\n".join(md_lines(d))
    for n in moved:
        leg(n in txt, "L8 markdown missing cell %s" % n)

    # L9 a missing nav cannot be turned into a CNY claim
    d = decide(same, {"beta_target": 0.2, "k_now": 0.46, "ticket": {}})
    leg(d["verdict"] == "UNREADABLE", "L9 got %s" % d["verdict"])
    leg("sentence" in d and d.get("deployed_now_cny") is None, "L9 no money without nav")

    # L10 the prose must agree with the flags it sits next to
    d = decide(up, tk)
    leg(d["the_size_in_force_is_the_ceiling"] is False and "at the ceiling" not in d["sentence"],
        "L10 prose claims a ceiling the table contradicts: %r" % d["sentence"])
    d = decide(moved, tk)
    leg(d["the_size_in_force_is_the_ceiling"] is True and "at the ceiling" in d["sentence"],
        "L10 prose must say ceiling when every other ruler reads lower: %r" % d["sentence"])
    leg(d["n_below_money"] == 1 and d["n_above_money"] == 0,
        "L10 counts %r/%r" % (d["n_below_money"], d["n_above_money"]))

    for f in fails:
        print("  FAIL " + f)
    print("[selftest] %d/%d PASS" % (10 - len(fails), 10))
    return 0 if not fails else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # the smoke harness and the chain legs both spell the read-only modes with dashes
    argv = ["check" if a == "--check" else "selftest" if a == "--selftest" else a for a in argv]
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run",
                    choices=["run", "check", "selftest"])
    a = ap.parse_args(argv)
    if a.mode == "selftest":
        return selftest()
    if a.mode == "check":
        return check()
    t0 = time.time()
    d = run()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    d["elapsed_sec"] = round(time.time() - t0, 1)
    d["generated"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    md = os.path.join(BASE, "research", "ETF_BOOK_SIZE_RULERS.md")
    with open(md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines(d)) + "\n")
    print(json.dumps({k: d.get(k) for k in ("verdict", "sentence", "k_floor", "k_ceiling",
                                            "range_pp", "widest_mover", "widest_mover_pp",
                                            "deployed_floor_cny", "deployed_now_cny",
                                            "identity_broken")},
                     ensure_ascii=False, indent=1))
    return 0 if d.get("verdict") != "IDENTITY_BROKEN" else 1


if __name__ == "__main__":
    sys.exit(main())