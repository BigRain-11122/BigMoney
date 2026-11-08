"""Audit every published ETF-book ticket against the panel that would have had to price it.

Why this face exists (r1610): `etf_book_order.panel_breadth` was added at r1609 *going
forward* -- a ticket now carries a third freshness face beside `feed_status` and
`staleness`. Nothing asked the backward question: of the tickets already published, how
many were priced on a bar that the panel does not certify as dense? This reads the six
published tickets under results/etf_book_order/ and, for each, measures on the daily panel:

  * cross-sectional breadth on the ticket's own bar (share of panel symbols with a row
    exactly on that date, against the same 0.50 gate the forward ticket uses),
  * whether every held name has a row on that bar, and whether the panel close equals
    the price the ticket ordered at,
  * what the ticket itself claimed about freshness.

The honest caveat, published in the face: breadth is measured on the tree as it stands
today, and the panel only ever grew (r1609 appended 8,514 rows), so a historical reading
is an *upper bound* on the breadth that existed when the ticket was written. The held-name
and price checks do not have that weakness -- a name either printed on that bar or it did
not.

Usage:
  python scripts/etf_book_ticket_audit.py run      # build + publish the face
  python scripts/etf_book_ticket_audit.py selftest
"""
import glob
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

DAILY_DIR = os.path.join(ROOT, "data", "daily")
TICKET_DIR = os.path.join(ROOT, "results", "etf_book_order")
OUT_DIR = os.path.join(ROOT, "results", "etf_book_order")

# Same gate the forward ticket enforces (scripts/etf_book_order.py BREADTH_GATE). Kept as
# a named constant here so the audit re-states the line it is auditing rather than
# importing a value that could move without the audit noticing; the selftest pins them
# to each other so drift is a red leg, not a silent divergence.
BREADTH_GATE = 0.50
PRICE_REL_TOL = 1e-4


def panel_key(basename):
    """Normalise a daily-panel filename to the bare ticker the tickets quote.

    The tree stores both spellings (bare `159901.csv` and exchange-prefixed
    `sz159501.csv` / `sh513690.csv`); a ticket always writes the bare 6-digit code, so a
    reader that keys on the filename loses every prefixed member. First build of this
    face did exactly that and reported all six tickets' holdings as `not_in_panel`.
    """
    stem = os.path.splitext(basename)[0]
    if len(stem) == 8 and stem[:2] in ("sz", "sh") and stem[2:].isdigit():
        return stem[2:]
    return stem


def read_panel(daily_dir, dates, full_symbols=()):
    """One pass over the daily CSVs.

    `close` keeps the wanted dates for every symbol (that is what the breadth count
    needs); `series` keeps the whole history but only for `full_symbols` (that is what the
    price-matching needs). Keeping the full history for all 1,6xx members would be three
    million dict entries for no reason.
    """
    want = set(dates)
    full = set(full_symbols)
    out = {}
    conflicts = []
    for p in sorted(glob.glob(os.path.join(daily_dir, "*.csv"))):
        sym = panel_key(os.path.basename(p))
        keep_all = sym in full
        last = None
        hits = {}
        series = {}
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if len(line) < 12:
                    continue
                d = line.split(",", 1)[0]
                if len(d) == 10 and d[4] == "-" and d[7] == "-":
                    last = d
                    if d in want or keep_all:
                        parts = line.split(",")
                        try:
                            px = float(parts[4])
                        except (IndexError, ValueError):
                            px = None
                        if d in want:
                            hits[d] = px
                        if keep_all:
                            series[d] = px
        if sym in out:
            prev = out[sym]
            for d, v in hits.items():
                if d in prev["close"] and prev["close"][d] != v:
                    conflicts.append({"symbol": sym, "date": d,
                                      "kept": prev["close"][d], "from": v,
                                      "files": prev["files"] + [os.path.basename(p)]})
                else:
                    prev["close"].setdefault(d, v)
            for d, v in series.items():
                prev["series"].setdefault(d, v)
            prev["files"].append(os.path.basename(p))
            if last and (prev["last"] is None or last > prev["last"]):
                prev["last"] = last
        else:
            out[sym] = {"last": last, "close": hits, "series": series,
                        "files": [os.path.basename(p)]}
    return out, conflicts


def load_tickets(ticket_dir):
    rows = []
    for p in sorted(glob.glob(os.path.join(ticket_dir, "TICKET-*.json"))):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception as exc:  # an unreadable ticket is a row, not a crash
            rows.append({"file": os.path.basename(p), "error": str(exc)})
            continue
        order = []
        tk = d.get("ticket") if isinstance(d.get("ticket"), dict) else d
        for leg in tk.get("order") or []:
            order.append({"symbol": str(leg.get("symbol")),
                          "weight": leg.get("weight"),
                          "price": leg.get("price")})
        bar = (d.get("evidence_cutoff") or d.get("asof_bar")
               or (d.get("feed_status") or {}).get("ticket_bar"))
        claim = {}
        if isinstance(d.get("feed_status"), dict):
            claim["feed_status"] = d["feed_status"].get("status")
            claim["feed_lag_days"] = d["feed_status"].get("lag_days")
        if isinstance(d.get("staleness"), dict):
            claim["claim_symbols_with_value_on_last_bar"] = \
                d["staleness"].get("symbols_with_value_on_last_bar")
            claim["claim_symbols_total"] = d["staleness"].get("symbols_total")
        if "panel_breadth" in d:
            claim["claim_panel_breadth"] = d.get("panel_breadth")
            claim["claim_panel_degraded"] = d.get("panel_degraded")
        if "pricing_bar" in d:
            claim["claim_pricing_bar"] = d.get("pricing_bar")
            claim["claim_pricing_drift"] = d.get("pricing_drift_vs_priced_bar")
        rows.append({"file": os.path.basename(p), "bar": bar, "order": order,
                     "claim": claim})
    return rows


def audit(tickets, panel, gate=BREADTH_GATE, tol=PRICE_REL_TOL):
    universe = len(panel)
    dates = sorted({t.get("bar") for t in tickets if t.get("bar")})
    breadth = {}
    for d in dates:
        live = sum(1 for v in panel.values() if d in v["close"])
        breadth[d] = {"date": d, "live_on_bar": live, "universe": universe,
                      "share": round(live / float(universe), 4) if universe else None,
                      "gate": gate,
                      "breadth_ok": bool(universe and live / float(universe) >= gate)}
    out_rows = []
    for t in tickets:
        if t.get("error"):
            out_rows.append(dict(t, verdict="unreadable_ticket"))
            continue
        bar = t.get("bar")
        b = breadth.get(bar)
        missing, off_bar, not_found, on_bar, later = [], [], [], [], []
        price_bars = []
        for leg in t["order"]:
            rec = panel.get(leg["symbol"])
            if rec is None:
                missing.append({"symbol": leg["symbol"], "why": "not_in_panel"})
                continue
            close = rec["close"].get(bar)
            if close is None:
                missing.append({"symbol": leg["symbol"], "why": "no_row_on_bar",
                                "symbols_last_bar": rec["last"]})
                continue
            if leg.get("price") in (None, 0):
                on_bar.append({"symbol": leg["symbol"], "ticket_price": None})
                continue
            rel = abs(close - leg["price"]) / float(leg["price"])
            if rel <= tol:
                on_bar.append({"symbol": leg["symbol"], "ticket_price": leg["price"],
                               "panel_close": close})
                continue
            # the ticket printed a price the bar does not carry -- ask the panel which bar
            # *does* carry it. A price that matches an earlier bar is a stale price; a price
            # that matches no bar at all is a different, worse class.
            hits = sorted(d for d, v in rec["series"].items()
                          if v is not None
                          and abs(v - leg["price"]) / float(leg["price"]) <= tol)
            before = [d for d in hits if d <= str(bar)]
            after = [d for d in hits if d > str(bar)]
            if before:
                price_bars.append(before[-1])
                off_bar.append({"symbol": leg["symbol"], "ticket_price": leg["price"],
                                "panel_close_on_ticket_bar": close,
                                "rel_off": round(rel, 6),
                                "price_matches_bars_at_or_before": before,
                                "price_matches_bars_after": after,
                                "price_bar_last": before[-1]})
            elif after:
                price_bars.append(after[0])
                later.append({"symbol": leg["symbol"], "ticket_price": leg["price"],
                              "panel_close_on_ticket_bar": close,
                              "price_matches_bars_after": after})
            else:
                nearest = min(((abs(v - leg["price"]), d, v)
                               for d, v in rec["series"].items() if v is not None),
                              default=None)
                not_found.append({"symbol": leg["symbol"], "ticket_price": leg["price"],
                                  "panel_close_on_ticket_bar": close,
                                  "nearest_bar": nearest[1] if nearest else None,
                                  "nearest_close": nearest[2] if nearest else None,
                                  "ratio": round(leg["price"] / nearest[2], 4)
                                  if nearest and nearest[2] else None})
        distinct_price_bars = sorted(set(price_bars))
        # A per-name candidate set is weak evidence: a price recurs. The ticket-level
        # question is which bars ALL the off-bar names agree on, so intersect them.
        cands = [set(m["price_matches_bars_at_or_before"]) for m in off_bar]
        common = sorted(set.intersection(*cands)) if cands else []
        # trading bars between the bar the prices come from and the bar the ticket names,
        # counted on the held names' own calendar (the panel has no separate calendar here)
        calendar = sorted({d for leg in t["order"]
                           for d in (panel.get(leg["symbol"], {}).get("series") or {})})
        price_bar = common[-1] if common else None
        bars_between = None
        if price_bar and bar:
            bars_between = sum(1 for d in calendar if price_bar < d <= str(bar))
        # what the stale prices are worth: the weight-weighted price level the ticket printed vs
        # the level the bar it names actually carried
        w = [leg for leg in t["order"] if leg.get("weight")]
        if w and b is not None:
            printed = sum(float(leg["weight"]) * float(leg.get("price") or 0) for leg in w)
            on_bar_px = sum(float(leg["weight"]) *
                            float((panel.get(leg["symbol"], {}).get("close") or {}).get(bar) or 0)
                            for leg in w)
            drift = (printed / on_bar_px - 1.0) if on_bar_px else None
        else:
            printed, on_bar_px, drift = None, None, None
        if b is None:
            verdict = "no_bar_recorded"
        elif missing:
            verdict = "held_name_not_priced_on_bar"
        elif not_found:
            verdict = "ticket_price_matches_no_panel_bar"
        elif off_bar:
            verdict = "ticket_prices_come_from_an_earlier_bar"
        elif later:
            verdict = "ticket_prices_match_only_a_later_bar"
        elif not b["breadth_ok"]:
            verdict = "priced_on_a_bar_the_panel_does_not_certify"
        else:
            verdict = "certified"
        cbar = (t["claim"] or {}).get("claim_pricing_bar")
        cdrift = (t["claim"] or {}).get("claim_pricing_drift")
        agree = None
        if cbar is not None or cdrift is not None:
            agree = {"claim_pricing_bar": cbar,
                     "measured_price_bar": price_bar,
                     "pricing_bar_agrees": (cbar == price_bar if cbar else None),
                     "claim_pricing_drift": cdrift,
                     "measured_pricing_drift": (round(drift, 6)
                                                if drift is not None else None),
                     "drift_agrees": (None if cdrift is None or drift is None
                                      else abs(cdrift - drift) < 1e-6)}
        out_rows.append({"file": t["file"], "bar": bar,
                         "n_held": len(t["order"]),
                         "breadth_at_bar": b,
                         "held_missing": missing,
                         "held_priced_on_the_ticket_bar": len(on_bar),
                         "held_priced_on_an_earlier_bar": off_bar,
                         "held_price_matches_no_bar": not_found,
                         "price_bar_candidates": distinct_price_bars,
                         "price_bar_shared_by_all_off_bar_names": common,
                         "price_bar": price_bar,
                         "trading_bars_before_the_ticket_bar": bars_between,
                         "weighted_price_level_printed": (round(printed, 6)
                                                          if printed is not None else None),
                         "weighted_price_level_on_the_ticket_bar": (
                             round(on_bar_px, 6) if on_bar_px is not None else None),
                         "weighted_price_drift": (round(drift, 6)
                                                  if drift is not None else None),
                         "claim": t["claim"],
                         "claim_vs_measurement": agree,
                         "verdict": verdict})
    counts = {}
    for r in out_rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    return {"universe": universe, "breadth_by_bar": breadth, "tickets": out_rows,
            "by_verdict": counts,
            "summary": {"n_tickets": len(out_rows),
                        "n_certified": counts.get("certified", 0),
                        "n_not_certified": counts.get(
                            "priced_on_a_bar_the_panel_does_not_certify", 0),
                        "n_held_name_not_priced": counts.get(
                            "held_name_not_priced_on_bar", 0),
                        "n_priced_on_an_earlier_bar": counts.get(
                            "ticket_prices_come_from_an_earlier_bar", 0),
                        "n_price_matches_no_bar": counts.get(
                            "ticket_price_matches_no_panel_bar", 0),
                        "price_bar_by_ticket": {
                            r["file"]: r.get("price_bar") for r in out_rows
                            if r.get("price_bar")}}}


def caveats():
    return [
        "breadth is measured on the tree as it stands today; the daily panel only grew "
        "(r1609 appended 8,514 rows), so a historical reading is an upper bound on the "
        "breadth that existed when the ticket was written -- it can excuse a ticket it "
        "cannot condemn",
        "the held-name and price checks carry no such weakness: a name either printed a "
        "row on that bar or it did not",
        "the gate (0.50) is restated in this file rather than imported; the selftest pins "
        "it to scripts/etf_book_order.py BREADTH_GATE so drift is a red leg",
        "no comparison is made to what the ticket would have earned -- this face answers "
        "only whether the ticket could have been executed at the price it printed",
    ]


def build():
    tickets = load_tickets(TICKET_DIR)
    dates = [t["bar"] for t in tickets if t.get("bar")]
    held = {leg["symbol"] for t in tickets for leg in t.get("order", [])}
    panel, conflicts = read_panel(DAILY_DIR, dates, full_symbols=held)
    newest = max((v["last"] or "" for v in panel.values()), default="")
    res = audit(tickets, panel)
    face = {
        "study": "E581 etf book ticket breadth audit",
        "evidence_cutoff": newest,
        "generated_by": "scripts/etf_book_ticket_audit.py run",
        "panel_measured_at": newest,
        "panel_files": sum(len(v["files"]) for v in panel.values()),
        "panel_symbols": len(panel),
        "duplicate_symbol_conflicts": conflicts,
        **res,
        "caveats": caveats(),
    }
    return face


def selftest():
    ok = []

    def chk(name, cond, extra=""):
        ok.append((name, bool(cond), extra))

    # fixtures: three symbols, two bars each; one ticket priced on the dense bar, one on
    # the sparse bar, one holding a name that never printed there.
    tmp = tempfile.mkdtemp(prefix="tickaudit_")
    daily = os.path.join(tmp, "daily")
    tkdir = os.path.join(tmp, "tickets")
    os.makedirs(daily, exist_ok=True)
    os.makedirs(tkdir, exist_ok=True)
    rows = {"510300": ["2026-01-02,4.0,4.1,3.9,4.05,10,100", "2026-01-05,4.05,4.2,4.0,4.15,10,100"],
            "510500": ["2026-01-02,5.0,5.1,4.9,5.05,10,100", "2026-01-05,5.05,5.2,5.0,5.15,10,100"],
            # exchange-prefixed spelling, exactly as data/daily stores sz159501.csv
            "sz159915": ["2026-01-02,2.0,2.1,1.9,2.05,10,100"]}
    for sym, lines in rows.items():
        with open(os.path.join(daily, sym + ".csv"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
    # a second file for a symbol already present, with one bar that disagrees
    with open(os.path.join(daily, "sh510300.csv"), "w", encoding="utf-8") as fh:
        fh.write("2026-01-05,4.05,4.2,4.0,4.99,10,100\n")
    t1 = {"evidence_cutoff": "2026-01-05",
          "ticket": {"order": [{"symbol": "510300", "price": 4.15, "weight": 0.5},
                               {"symbol": "510500", "price": 5.15, "weight": 0.5}]},
          "feed_status": {"status": "current", "ticket_bar": "2026-01-05", "lag_days": 0}}
    t2 = {"evidence_cutoff": "2026-01-05",
          "ticket": {"order": [{"symbol": "159915", "price": 2.05, "weight": 0.5},
                               {"symbol": "510300", "price": 4.15, "weight": 0.5}]}}
    t3 = {"evidence_cutoff": "2026-01-05",
          "ticket": {"order": [{"symbol": "510300", "price": 4.99, "weight": 1.0}]}}
    # ticket d prices at the PREVIOUS bar (2026-01-02 close 4.05) while claiming 01-05
    t4 = {"evidence_cutoff": "2026-01-05",
          "ticket": {"order": [{"symbol": "510300", "price": 4.05, "weight": 1.0},
                               {"symbol": "510500", "price": 5.05, "weight": 1.0}]}}
    for name, obj in (("TICKET-a.json", t1), ("TICKET-b.json", t2),
                      ("TICKET-c.json", t3), ("TICKET-d.json", t4)):
        with open(os.path.join(tkdir, name), "w", encoding="utf-8") as fh:
            json.dump(obj, fh)

    tickets = load_tickets(tkdir)
    held = {leg["symbol"] for t in tickets for leg in t["order"]}
    panel, conflicts = read_panel(daily, sorted({t["bar"] for t in tickets}),
                                  full_symbols=held)
    res = audit(tickets, panel)

    chk("panel read", len(panel) == 3, str(len(panel)))
    chk("exchange-prefixed file resolves to the bare ticker", "159915" in panel,
        str(sorted(panel)))
    chk("bare and prefixed spellings of one symbol merge", len(panel["510300"]["files"]) == 2,
        str(panel["510300"]["files"]))
    chk("disagreeing duplicate bar is published as a conflict",
        len(conflicts) == 1 and conflicts[0]["symbol"] == "510300", str(conflicts))
    chk("four tickets read", len(tickets) == 4, str(len(tickets)))
    # 2 of 3 symbols printed on 2026-01-05 -> 0.6667 >= 0.50 gate
    chk("breadth share", res["breadth_by_bar"]["2026-01-05"]["share"] == 0.6667,
        str(res["breadth_by_bar"]["2026-01-05"]))
    chk("breadth gate holds", res["breadth_by_bar"]["2026-01-05"]["breadth_ok"] is True)
    v = {r["file"]: r["verdict"] for r in res["tickets"]}
    chk("ticket a certified", v.get("TICKET-a.json") == "certified", str(v))
    chk("ticket b flags the missing name",
        v.get("TICKET-b.json") == "held_name_not_priced_on_bar", str(v))
    chk("ticket c: price matching no bar at all is its own class",
        v.get("TICKET-c.json") == "ticket_price_matches_no_panel_bar", str(v))
    chk("ticket d: prices from the previous bar are named, not just flagged",
        v.get("TICKET-d.json") == "ticket_prices_come_from_an_earlier_bar", str(v))
    drow = [r for r in res["tickets"] if r["file"] == "TICKET-d.json"][0]
    chk("ticket d publishes the bar its prices came from",
        drow["price_bar"] == "2026-01-02"
        and all(m["price_bar_last"] == "2026-01-02"
                for m in drow["held_priced_on_an_earlier_bar"]), str(drow["price_bar"]))
    chk("ticket d keeps its on-bar count honest",
        drow["held_priced_on_the_ticket_bar"] == 0, str(drow))
    chk("missing name records its own last bar",
        any(m.get("symbols_last_bar") == "2026-01-02"
            for r in res["tickets"] for m in r.get("held_missing", [])), "")
    chk("summary counts", res["summary"]["n_certified"] == 1
        and res["summary"]["n_held_name_not_priced"] == 1
        and res["summary"]["n_price_matches_no_bar"] == 1
        and res["summary"]["n_priced_on_an_earlier_bar"] == 1, str(res["summary"]))

    # the gate must be the forward ticket's gate, not a number that drifted apart
    try:
        import etf_book_order as EBO
        chk("gate pins to etf_book_order.BREADTH_GATE",
            abs(EBO.BREADTH_GATE - BREADTH_GATE) < 1e-12,
            "%s vs %s" % (EBO.BREADTH_GATE, BREADTH_GATE))
    except Exception as exc:
        chk("gate pins to etf_book_order.BREADTH_GATE", False, "import failed: %s" % exc)

    # a ticket with no bar at all is a row, not a crash
    res2 = audit([{"file": "TICKET-z.json", "bar": None, "order": [], "claim": {}}],
                 panel)
    chk("no-bar ticket is classified", res2["tickets"][0]["verdict"] == "no_bar_recorded")
    # an unreadable ticket is a row too
    res3 = audit([{"file": "TICKET-y.json", "error": "boom"}], panel)
    chk("unreadable ticket is classified",
        res3["tickets"][0]["verdict"] == "unreadable_ticket")
    # empty panel must not divide by zero
    res4 = audit([{"file": "TICKET-e.json", "bar": "2026-01-05", "order": [], "claim": {}}], {})
    chk("empty panel stays quiet", res4["universe"] == 0
        and res4["breadth_by_bar"]["2026-01-05"]["share"] is None
        and res4["breadth_by_bar"]["2026-01-05"]["breadth_ok"] is False,
        str(res4["breadth_by_bar"]))

    bad = [n for n, c, _ in ok if not c]
    for n, c, extra in ok:
        print(("PASS " if c else "FAIL ") + n + ((" | " + extra) if extra and not c else ""))
    print("selftest %d/%d" % (len(ok) - len(bad), len(ok)))
    return 0 if not bad else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd != "run":
        print(__doc__)
        return 2
    face = build()
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, "BREADTHAUDIT-%s.json" % face["evidence_cutoff"])
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    s = face["summary"]
    print("breadth audit: %d tickets | certified %d | not certified %d | "
          "held name not priced %d | priced on an earlier bar %d | "
          "price matches no bar %d"
          % (s["n_tickets"], s["n_certified"], s["n_not_certified"],
             s["n_held_name_not_priced"], s["n_priced_on_an_earlier_bar"],
             s["n_price_matches_no_bar"]))
    for r in face["tickets"]:
        b = r.get("breadth_at_bar") or {}
        print("  %-26s bar %s breadth %s/%s -> prices from %s (%d on bar, %d earlier, %d nowhere) -> %s"
              % (r["file"], r["bar"], b.get("live_on_bar"), b.get("universe"),
                 r.get("price_bar"), r.get("held_priced_on_the_ticket_bar", 0),
                 len(r.get("held_priced_on_an_earlier_bar") or []),
                 len(r.get("held_price_matches_no_bar") or []), r["verdict"]))
    print("wrote " + path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))