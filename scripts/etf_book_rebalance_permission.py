"""Is the 2026-11-11 rebalance allowed to keep a size that only one reading supports?

r1449 priced five readings of the same sizing rule on the same panel and left the money
at k=0.460253 (CNY 460,253 of a 1,000,000 NAV):

    baseline_published   0.460253   = the money itself (identity, r1449)
    denominator          0.544424   +8.42pp  static composition, not a decision path
    universe             0.432195   -2.81pp  path
    window               0.412669   -4.76pp  path
    window_x_universe    0.393073   -6.72pp  path (the cell never measured before)

The table answers "how wide is the argument".  It does not answer the question the desk
has to answer before the next rebalance: may the weight in force stay where it is?

This face turns the table into a permission, derived from the published receipts only
(no panel, no repricing, no engine import):

  * a reading SUPPORTS the size in force when it lands at or above the money
    (k >= k_now - 0.5pp: a reading that would have sized larger certainly permits the
    size in force), and it is not circular;
  * a reading is CIRCULAR when it is the construction the ticket was priced from -- its
    k equals k_now by identity, so it can never testify against the money.  If that
    identity ever fails the face refuses to classify (an unproved identity is not a
    licence to call a reading independent);
  * a reading is a PATH only if it was measured on decision bars (bars >= 60) and its
    own note does not declare it static;
  * permitted_k = min over readable, non-circular PATH readings.  Keeping the weight in
    force is allowed iff k_now <= permitted_k + tolerance.

The whole point is one subtraction: take the baseline out of the "minimum" and a desk
that reads "keep" reads "cut".  Both answers are printed, so the trap is visible.

Read-only over published JSON.  Deterministic.  No network.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULERS_RECEIPT = "results/etf_book_size_rulers_decision.json"
TICKET_GLOB_DIR = os.path.join(BASE, "results", "etf_book_order")
YEAR_GATE_RECEIPT = "results/etf_book_year_gate/YEAR-GATE.json"
OUT = os.path.join(BASE, "results", "etf_book_rebalance_permission.json")
MD = os.path.join(BASE, "research", "ETF_BOOK_REBALANCE_PERMISSION.md")

SIZE_TOL = 0.005          # 0.5pp on k: the same "same size" tolerance the rulers table uses
MIN_BARS = 60             # a reading with fewer decision bars is not a path (r1261 family)
IDENT_TOL = 1e-6          # the ticket publishes k at 6dp, the rulers receipt keeps full float
BASELINE = "baseline_published"
STATIC_MARKERS = ("static composition", "not a path")

VERDICT_KEEP_PATH = "KEEP_SUPPORTED_BY_INDEPENDENT_PATH"
VERDICT_KEEP_STATIC_ONLY = "KEEP_STANDS_ON_NON_PATH_ARGUMENT"
VERDICT_REPRICE = "REPRICE_REQUIRED"
VERDICT_UNREADABLE = "UNREADABLE"


def _read_json(rel):
    p = rel if os.path.isabs(rel) else os.path.join(BASE, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def latest_ticket():
    import glob
    files = sorted(glob.glob(os.path.join(TICKET_GLOB_DIR, "TICKET-*.json")))
    if not files:
        return None, None
    with open(files[-1], encoding="utf-8") as f:
        return os.path.basename(files[-1]), json.load(f)


def classify(name, cell, k_now):
    """circular / static / path / unreadable -- the classification this face acts on.

    Nothing here defaults into "path": a cell must either be the priced construction, or
    say in its own note that it is static, or carry the decision bars a path was measured
    on.  A cell that answers none of the three questions is unreadable, not a path.
    """
    k = cell.get("k")
    if k is None:
        return "unreadable", "no k on the cell"
    k = float(k)
    if name == BASELINE:
        if abs(k - float(k_now)) > IDENT_TOL:
            return "unreadable", ("baseline k=%.9f does not equal the ticket's k=%.9f: the "
                                  "circularity identity is broken, so no reading can be "
                                  "called independent" % (k, float(k_now)))
        return "circular", "the construction the ticket was priced from (k == k_now by identity)"
    note = (cell.get("note") or "").lower()
    if any(m in note for m in STATIC_MARKERS):
        return "static", cell.get("note") or "declared static"
    bars = cell.get("bars")
    if bars is None or float(bars) < MIN_BARS:
        return "unreadable", ("%d bars: too short to be a decision path" % (bars or 0))
    return "path", (cell.get("note") or "measured on %s bars" % bars)


def decide(rulers, ticket, year_gate=None):
    """Pure function of the published receipts.  No panel, no repricing."""
    if rulers is None:
        return {"verdict": VERDICT_UNREADABLE,
                "sentence": "the rulers receipt is missing: an unpriced table cannot grant "
                            "a size",
                "reason": "missing_rulers_receipt"}
    if ticket is None:
        return {"verdict": VERDICT_UNREADABLE,
                "sentence": "no ticket on disk: the face will not price a size nobody issued",
                "reason": "missing_ticket"}
    k_now = ticket.get("k_now")
    nav = (ticket.get("ticket") or {}).get("nav")
    if k_now is None or nav is None:
        return {"verdict": VERDICT_UNREADABLE,
                "sentence": "the ticket carries no k_now/nav: nothing to permission",
                "reason": "incomplete_ticket"}
    k_now = float(k_now)
    # r1471: the sheet now sizes from the executed account, so `k_now` is the size ORDERED.
    # The readings below are alternative SIZING-RULE readings; their circular identity is
    # "reproduces what the rule charged", which the ticket records separately as `k_rule`.
    k_rule = ticket.get("k_rule")
    k_rule = k_now if k_rule is None else float(k_rule)
    nav = float(nav)
    und = float((ticket.get("ticket") or {}).get("underspend_pct") or 0.0)

    cells = rulers.get("cells") or {}
    readings = {}
    unreadable = {}
    for name, cell in cells.items():
        kind, why = classify(name, cell, k_rule)
        k = cell.get("k")
        readings[name] = {
            "k": None if k is None else round(float(k), 6),
            "delta_vs_now_pp": None if k is None else round(100.0 * (float(k) - k_now), 2),
            "kind": kind,
            "why": why,
            "bars": cell.get("bars"),
        }
        if kind == "unreadable":
            unreadable[name] = why

    paths = {n: r["k"] for n, r in readings.items() if r["kind"] == "path" and r["k"] is not None}
    statics = {n: r["k"] for n, r in readings.items() if r["kind"] == "static" and r["k"] is not None}
    circular = [n for n, r in readings.items() if r["kind"] == "circular"]

    out = {
        "face": "etf_book_rebalance_permission",
        "decision_date": rulers.get("decision_date"),
        "ticket_file": ticket.get("_file"),
        "evidence_cutoff": ticket.get("evidence_cutoff") or rulers.get("evidence_cutoff"),
        "beta_target": ticket.get("beta_target"),
        "size_tol": SIZE_TOL,
        "k_now": round(k_now, 6),
        "k_rule": round(k_rule, 6),
        "nav_cny": nav,
        "book_amount_cny": (ticket.get("ticket") or {}).get("book_amount"),
        "cash_amount_cny": (ticket.get("ticket") or {}).get("cash_amount"),
        "readings": readings,
        "readings_unreadable": unreadable,
        "circular_readings": circular,
        "path_readings": sorted(paths),
        "static_readings": sorted(statics),
    }
    if unreadable:
        out.update({"verdict": VERDICT_UNREADABLE,
                    "sentence": "a reading could not be classified (%s); an unclassified "
                                "reading is not a vote for the size in force"
                                % ", ".join(sorted(unreadable)),
                    "permitted_k": None,
                    "keep_allowed": None})
        return out
    if not paths:
        out.update({"verdict": VERDICT_UNREADABLE,
                    "sentence": "no reading was measured on a decision path; the only cells "
                                "on disk are the money and a static mix",
                    "permitted_k": None,
                    "keep_allowed": None})
        return out

    permitted_k = min(paths.values())
    # "supports" = lands at or above the money, not "lands on it": a reading that would
    # have sized larger permits this size; a reading below it forbids it.
    supporters = sorted(n for n, k in {**paths, **statics}.items()
                        if k >= k_now - SIZE_TOL - 1e-12)
    keep_allowed = any(k >= k_now - SIZE_TOL - 1e-12 for k in paths.values())

    # the trap, printed: the lazy reading takes "some ruler says we could hold MORE" as
    # permission for the size in force.  On the live table that reading is the static mix.
    naive_k = max(k_now, *[r["k"] for r in readings.values() if r["k"] is not None])
    out.update({
        "permitted_k": round(permitted_k, 6),
        "permitted_book_cny": round(permitted_k * nav - nav * und / 100.0, 2),
        "cut_k": round(k_now - permitted_k, 6),
        "cut_pp": round(100.0 * (k_now - permitted_k), 2),
        "cut_cny": round((k_now - permitted_k) * nav, 2),
        "supporters": supporters,
        "supporters_path": sorted(n for n in paths if n in supporters),
        "supporters_static": sorted(n for n in statics if n in supporters),
        "keep_allowed": bool(keep_allowed),
        "naive_max_over_all_readings": {
            "k": round(naive_k, 6),
            "keep_allowed": bool(naive_k >= k_now - SIZE_TOL - 1e-12),
            "why": "a ruler that permits a LARGER size is read as permission for this one; "
                   "the permitting reading need not be a decision path (E456: the rulers "
                   "are not additive and not interchangeable)",
        },
    })
    if keep_allowed:
        out["verdict"] = VERDICT_KEEP_PATH
        out["sentence"] = (
            "keeping k=%.6f is supported by %d independent path reading(s) (%s); the "
            "permitting floor over all path readings is k=%.6f"
            % (k_now, len(out["supporters_path"]), ", ".join(out["supporters_path"]),
               permitted_k))
    elif out["supporters_static"]:
        out["verdict"] = VERDICT_KEEP_STATIC_ONLY
        out["sentence"] = (
            "keeping k=%.6f stands only on %s, which is a static mix and not a decision "
            "path; all %d path reading(s) sit below the money (highest k=%.6f), so the %s "
            "rebalance must size at k=%.6f (CNY %s, a cut of CNY %s = %.2fpp) unless a "
            "caliber prereg lands first"
            % (k_now, ", ".join(out["supporters_static"]), len(paths), max(paths.values()),
               out["decision_date"], permitted_k,
               format(out["permitted_book_cny"], ",.0f"),
               format(out["cut_cny"], ",.0f"), out["cut_pp"]))
    else:
        out["verdict"] = VERDICT_REPRICE
        out["sentence"] = (
            "keeping k=%.6f is not permitted: no reading at all reaches the money (%d path "
            "readings, highest k=%.6f), so the %s rebalance must size at k=%.6f (CNY %s, a "
            "cut of CNY %s = %.2fpp)"
            % (k_now, len(paths), max(paths.values()), out["decision_date"], permitted_k,
               format(out["permitted_book_cny"], ",.0f"),
               format(out["cut_cny"], ",.0f"), out["cut_pp"]))

    # supply side: the book's own calendar word, carried not re-judged
    gate = None
    if year_gate:
        for b in year_gate.get("books") or []:
            if b.get("book") == "nobond_vt08_adopted":
                ym = b.get("year_metrics") or {}
                gate = {"book": b.get("book"), "verdict": b.get("verdict"),
                        "failed_check": sorted(k for k, v in (b.get("checks") or {}).items()
                                               if v is False),
                        "top2_share": ym.get("top2_share"),
                        "top2_line": (year_gate.get("gate_rules") or {}).get("top2_share_max"),
                        "asof": year_gate.get("asof")}
    out["supply_side"] = gate or {"verdict": None, "why": "year gate receipt missing"}

    out["not_measured"] = [
        "the wrapper's yearly shape: beta overlay + GC001 cash leg have never been through "
        "the year gate (r1438), so a smaller k is not automatically a passing book",
        "which reading is the RIGHT measurement: the four-cell spread is a ruler choice and "
        "no caliber prereg has landed (r1446 four requirements)",
        "the cost of the cut: the ticket's own reprice delta (CNY 91.7 at the 11-06 bar) is "
        "not carried into the gate, and a 6.72pp cut pays one more round of 8bp",
    ]
    return out


def published_face():
    d = _read_json(OUT)
    return d if d else {}


def run():
    rulers = _read_json(RULERS_RECEIPT)
    name, tk = latest_ticket()
    if tk is not None:
        tk = dict(tk, _file=name)
    gate = _read_json(YEAR_GATE_RECEIPT)
    return decide(rulers, tk, gate)


def md_lines(d):
    out = ["# May the 2026-11-11 rebalance keep this size?", "",
           "ticket `%s` | evidence cutoff %s | decision date %s | beta target %s"
           % (d.get("ticket_file"), d.get("evidence_cutoff"), d.get("decision_date"),
              d.get("beta_target")), ""]
    if d.get("verdict") == VERDICT_UNREADABLE:
        out += ["**%s** — %s" % (d.get("verdict"), d.get("sentence")), ""]
        return out
    out += ["**%s** — %s" % (d.get("verdict"), d.get("sentence")), ""]
    out += ["| reading | k | vs money (pp) | kind | why |", "|---|---|---|---|---|"]
    for n, r in (d.get("readings") or {}).items():
        out.append("| %s | %s | %s | %s | %s |" % (
            n,
            "-" if r.get("k") is None else "%.6f" % r["k"],
            "-" if r.get("delta_vs_now_pp") is None else "%+.2f" % r["delta_vs_now_pp"],
            r.get("kind"), r.get("why")))
    out.append("")
    out += ["- money in force: k=%.6f = CNY %s of a CNY %s NAV"
            % (d["k_now"], format(d["book_amount_cny"], ",.0f"),
               format(d["nav_cny"], ",.0f")),
            "- permitted floor over %d path reading(s): k=%.6f = CNY %s"
            % (len(d.get("path_readings") or []), d["permitted_k"],
               format(d["permitted_book_cny"], ",.0f")),
            "- cut if reprice is required: k -%.6f (%.2fpp) = CNY %s"
            % (d["cut_k"], d["cut_pp"], format(d["cut_cny"], ",.0f")),
            "- supporters at the money: %s (path: %s / non-path: %s)"
            % (", ".join(d.get("supporters") or []) or "none",
               ", ".join(d.get("supporters_path") or []) or "none",
               ", ".join(d.get("supporters_static") or []) or "none"),
            "- the trap: reading 'some ruler permits a larger size' as permission reads "
            "k=%.6f -> keep=%s" % (d["naive_max_over_all_readings"]["k"],
                                   d["naive_max_over_all_readings"]["keep_allowed"]), ""]
    g = d.get("supply_side") or {}
    out += ["## supply side (carried, not re-judged)", "",
            "- book `%s`: **%s**%s" % (g.get("book"), g.get("verdict"),
                                       "" if not g.get("failed_check") else
                                       " (failed: %s)" % ", ".join(g["failed_check"])),
            "- top-2 year share %s vs line %s" % (g.get("top2_share"), g.get("top2_line")),
            ""]
    out += ["## not measured by this face", ""]
    for s in d.get("not_measured") or []:
        out.append("- " + s)
    out.append("")
    return out


def check():
    """Re-derive the published receipt from its own sources; refuse a stale face."""
    d = published_face()
    if not d:
        print("MISSING %s" % OUT)
        return 1
    fresh = run()
    fails = []

    def leg(ok, msg):
        if not ok:
            fails.append(msg)

    for k in ("verdict", "k_now", "permitted_k", "keep_allowed"):
        leg(fresh.get(k) == d.get(k), "field %s: disk=%r fresh=%r"
            % (k, d.get(k), fresh.get(k)))
    leg(abs((fresh.get("cut_cny") or 0) - (d.get("cut_cny") or 0)) <= 1.0,
        "cut_cny drifted: disk=%r fresh=%r" % (d.get("cut_cny"), fresh.get("cut_cny")))
    leg(sorted(fresh.get("path_readings") or []) == sorted(d.get("path_readings") or []),
        "path reading set drifted: disk=%r fresh=%r"
        % (d.get("path_readings"), fresh.get("path_readings")))
    leg((fresh.get("ticket_file") == d.get("ticket_file")),
        "a newer ticket landed since this receipt was written (disk=%r fresh=%r): re-run "
        "the face" % (d.get("ticket_file"), fresh.get("ticket_file")))
    for f in fails:
        print("  FAIL " + f)
    print("[check] %d/%d OK" % (6 - len(fails), 6))
    return 0 if not fails else 1


def _tk(k_now, nav=1000000.0, book=None, und=0.0):
    return {"k_now": k_now, "ticket": {"nav": nav, "underspend_pct": und,
                                       "book_amount": round(k_now * nav - nav * und / 100.0, 2)},
            "evidence_cutoff": "2026-11-06", "beta_target": 0.2, "_file": "TICKET-fixture.json"}


def _cell(k, bars=1658, note=None):
    c = {"k": k, "bars": bars}
    if note:
        c["note"] = note
    return c


def selftest():
    fails = []

    def leg(ok, msg):
        if not ok:
            fails.append(msg)

    k_now = 0.460253
    base = _cell(k_now, note=None)
    live = {"cells": {
        BASELINE: base,
        "denominator": _cell(0.544424, note="the sized mix is 46.0% invested; static "
                                             "composition, not a path"),
        "universe": _cell(0.432195),
        "window": _cell(0.412669),
        "window_x_universe": _cell(0.393073),
    }, "decision_date": "2026-11-11", "evidence_cutoff": "2026-11-06"}

    # L1 the live table: every path reading below the money, the only reading above it is
    # the static mix -> keeping the size stands on a non-path argument
    d = decide(live, _tk(k_now))
    leg(d["verdict"] == VERDICT_KEEP_STATIC_ONLY, "L1 verdict=%r" % d["verdict"])
    leg(abs(d["permitted_k"] - 0.393073) <= 1e-9, "L1 permitted=%r" % d.get("permitted_k"))
    leg(d["supporters_static"] == ["denominator"] and d["supporters_path"] == [],
        "L1 supporters=%r/%r" % (d.get("supporters_path"), d.get("supporters_static")))
    leg(abs(d["cut_cny"] - 67180.0) <= 1.0, "L1 cut_cny=%r" % d.get("cut_cny"))
    leg(d["naive_max_over_all_readings"]["keep_allowed"] is True,
        "L1 the trap must read 'keep' when the permitting reading is the static mix")

    # L2 a path reading AT the money must flip the answer -- a leg that can only say
    # "reprice" is not evidence
    flipped = json.loads(json.dumps(live))
    flipped["cells"]["universe"] = _cell(k_now)
    d = decide(flipped, _tk(k_now))
    leg(d["verdict"] == VERDICT_KEEP_PATH, "L2 verdict=%r" % d["verdict"])
    leg(d["supporters_path"] == ["universe"], "L2 supporters_path=%r" % d.get("supporters_path"))

    # L3 nothing at all reaches the money (static included) -> the unqualified refusal
    stat = json.loads(json.dumps(live))
    stat["cells"]["universe"] = _cell(0.30)
    stat["cells"]["window"] = _cell(0.31)
    stat["cells"]["window_x_universe"] = _cell(0.32)
    stat["cells"]["denominator"] = _cell(0.33, note="static composition, not a path")
    d = decide(stat, _tk(k_now))
    leg(d["verdict"] == VERDICT_REPRICE, "L3 verdict=%r" % d["verdict"])
    leg(d["supporters_static"] == [], "L3 static=%r" % d.get("supporters_static"))

    # L4 money below every path reading is allowed (the rule is not "always cut")
    low = json.loads(json.dumps(live))
    low["cells"]["universe"] = _cell(0.60)
    low["cells"]["window"] = _cell(0.61)
    low["cells"]["window_x_universe"] = _cell(0.62)
    low["cells"]["denominator"] = _cell(0.63, note="static composition, not a path")
    d = decide(low, _tk(k_now))
    leg(d["verdict"] == VERDICT_KEEP_PATH and d["keep_allowed"] is True,
        "L4 verdict=%r keep=%r" % (d["verdict"], d.get("keep_allowed")))

    # L5 a broken circularity identity must refuse, not classify
    broken = json.loads(json.dumps(live))
    broken["cells"][BASELINE] = _cell(0.50)
    d = decide(broken, _tk(k_now))
    leg(d["verdict"] == VERDICT_UNREADABLE, "L5 verdict=%r" % d["verdict"])
    leg("baseline_published" in d.get("readings_unreadable", {}), "L5 unreadable=%r"
        % d.get("readings_unreadable"))

    # L6 a short cell must not default into 'path'
    short = json.loads(json.dumps(live))
    short["cells"]["window"] = _cell(0.40, bars=12)
    d = decide(short, _tk(k_now))
    leg(d["verdict"] == VERDICT_UNREADABLE and "window" in d.get("readings_unreadable", {}),
        "L6 verdict=%r unreadable=%r" % (d["verdict"], d.get("readings_unreadable")))

    # L7 missing receipts are unreadable, never a default size
    leg(decide(None, _tk(k_now))["verdict"] == VERDICT_UNREADABLE, "L7 missing rulers")
    leg(decide(live, None)["verdict"] == VERDICT_UNREADABLE, "L7 missing ticket")

    # L8 the budget arithmetic mirrors the ticket (27 r-notes: k*nav - nav*underspend%)
    t = _tk(k_now, und=0.0457)
    d = decide(live, t)
    leg(abs(d["permitted_book_cny"] - (0.393073 * 1000000.0 - 456.7)) <= 1.0,
        "L8 permitted_book=%r" % d.get("permitted_book_cny"))

    # L9 the sentence must carry the number the flags say (r1449 prose-vs-flags)
    leg(("%.6f" % d["k_now"]) in (d.get("sentence") or ""), "L9 sentence=%r" % d.get("sentence"))

    for f in fails:
        print("  FAIL " + f)
    print("[selftest] %d/%d PASS" % (9 - len(fails), 9))
    return 0 if not fails else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    argv = ["check" if a == "--check" else "selftest" if a == "--selftest" else a for a in argv]
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "check", "selftest"])
    a = ap.parse_args(argv)
    if a.mode == "selftest":
        return selftest()
    if a.mode == "check":
        return check()
    t0 = time.time()
    d = run()
    d["elapsed_sec"] = round(time.time() - t0, 2)
    d["generated"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    with open(MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines(d)) + "\n")
    print(json.dumps({k: d.get(k) for k in ("verdict", "sentence", "k_now", "permitted_k",
                                            "permitted_book_cny", "cut_pp", "cut_cny",
                                            "supporters", "supporters_path",
                                            "supporters_static")},
                     ensure_ascii=False, indent=1))
    return 0 if d.get("verdict") != VERDICT_UNREADABLE else 1


if __name__ == "__main__":
    sys.exit(main())