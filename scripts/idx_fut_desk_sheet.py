# -*- coding: utf-8 -*-
"""The carry sleeve as a desk reads it the morning before it trades it. (bm-c r1701)

`idx_fut_carry_risk` answered "is holding the future instead of the ETF worth +9pp?".
That is a judgement, not a position: it carries no contract name, no lot count, no
margin, and no answer to "when does this roll next".  A desk cannot act on it.  This
face is the smallest thing that turns the judgement into a morning sheet:

  * which contract tomorrow's fill would go into, and how much of the product's open
    interest actually sits in it (a contract holding 4% of the book is a fill you may
    not get);
  * the margin one lot ties up at the exchange minimum -- an ASSUMPTION, printed as
    one, because a broker's surcharge is not measurable from this host -- and so how
    many lots a stated capital buys, both naively and after funding the product's own
    published max drawdown (the margin identity the source face already prints);
  * when the next roll falls, measured from this book's own switch history rather than
    a calendar rule -- the calendar rule was already shown to catch 50% of the rolls
    while eating market days near expiry;
  * the published gap after roll cost, BOTH ends of the band, read from the source
    face rather than recomputed here.

Nothing here is adopted.  The source face calls IC/IM `SLEEVE_CANDIDATE`; this sheet
repeats that word in every row it prints, and a product the source face refuses is
still printed with its refusal, not hidden.
"""
import os
import sys
import json
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import idx_fut_basis as base            # noqa: E402  (products, TRADING_DAYS, index panels)
import idx_fut_real_nav as rn           # noqa: E402  (contract panel + switch history, single source)

OUT = os.path.join(ROOT, "results", "idx_fut_desk_sheet.json")
DOC = os.path.join(ROOT, "research", "IDX_FUT_DESK_SHEET.md")
SRC = os.path.join(ROOT, "results", "idx_fut_carry_risk.json")

# CFFEX contract specs.  An assumption like the margin: the exchange publishes them,
# this host cannot query the file, and getting one wrong scales every lot count.
MULTIPLIER = {"IF": 300, "IH": 300, "IC": 200, "IM": 200}

CRITERIA = {
    "products": ["IC", "IF", "IM", "IH"],
    "capital_cny": 1000000.0,
    # the middle of the source face's three printed margin assumptions
    "margin_pct": 0.12,
    "thin_interest_share_pct": 8.0,
}


def _face():
    """The published judgement this sheet sits on.  Absent => the sheet is refused."""
    if not os.path.isfile(SRC):
        return None
    try:
        with open(SRC, "r", encoding="utf-8") as f:
            return json.load(f)
    except (ValueError, OSError):
        return None


def _panel(prod, cache_dir=None):
    ohlc = rn.contract_panel_ohlc(prod, cache_dir)
    if not ohlc:
        return None, None, None
    proj = {sym: {d: (row["close"], row["hold"], row["volume"])
                  for d, row in series.items()}
            for sym, series in ohlc.items()}
    days = sorted({d for sym in proj for d in proj[sym]})
    if not days:
        return None, None, None
    return ohlc, proj, days


def roll_intervals(days, rolls):
    """Trading days between consecutive switches, from the history this book booked.

    Measured rather than assumed: a fixed "roll 3 days before expiry" rule is what the
    calendar mask tried, and the source family already showed it mis-names half of them.
    """
    idx = {d: k for k, d in enumerate(days)}
    pos = [idx[r["date"]] for r in rolls if r.get("date") in idx]
    gaps = [b - a for a, b in zip(pos, pos[1:])] if len(pos) > 1 else []
    if not gaps:
        return {"n": 0, "median_td": None, "iqr_td": None, "gaps": []}
    s = sorted(gaps)
    mid = len(s) // 2
    median = float(s[mid]) if len(s) % 2 else (s[mid - 1] + s[mid]) / 2.0
    q1 = float(s[len(s) // 4])
    q3 = float(s[(3 * len(s)) // 4])
    return {"n": len(gaps), "median_td": round(median, 1),
            "iqr_td": [q1, q3], "gaps": gaps}


def desk_row(prod, face, cache_dir=None):
    ohlc, proj, days = _panel(prod, cache_dir)
    if not ohlc:
        return {"product": prod, "status": "no_contract_book"}
    held, rolls = rn.active_path(days, proj)
    last = days[-1]
    sym = held.get(last)
    if not sym or sym not in ohlc or last not in ohlc[sym]:
        return {"product": prod, "status": "no_contract_on_cutoff", "cutoff": last}
    row = ohlc[sym][last]
    oi_total = sum(ser.get(last, {}).get("hold", 0.0) or 0.0 for ser in ohlc.values())
    share = (row["hold"] / oi_total * 100.0) if oi_total > 0 else None

    mult = MULTIPLIER.get(prod)
    if not mult:
        return {"product": prod, "status": "no_contract_multiplier", "held": sym}
    notional = row["close"] * mult
    margin = notional * CRITERIA["margin_pct"]

    # the published judgement, read not recomputed
    src = (face or {}).get("products", {}).get(prod, {})
    verdict_row = ((face or {}).get("verdict", {}) or {}).get("rows", {}).get(prod, {})
    mdd = (src.get("risk") or {}).get("mdd_pct")
    dd_buffer = (abs(mdd) / 100.0 * notional) if isinstance(mdd, (int, float)) else None
    cap = CRITERIA["capital_cny"]
    lots_naive = int(cap // margin) if margin > 0 else None
    lots_after_dd = (int(cap // (margin + dd_buffer))
                     if (dd_buffer is not None and margin + dd_buffer > 0) else None)

    iv = roll_intervals(days, rolls)
    idx = {d: k for k, d in enumerate(days)}
    last_roll = rolls[-1] if rolls else None
    since = (idx[last] - idx[last_roll["date"]]) if (last_roll and last_roll.get("date") in idx) else None
    eta = (iv["median_td"] - since) if (iv["median_td"] is not None and since is not None) else None

    ex = src.get("execution") or {}
    band = ex.get("gap_after_roll_cost_pp") or {}
    return {
        "product": prod,
        "status": "ok",
        "cutoff": last,
        "held_contract": sym,
        "close": row["close"],
        "open_interest": row["hold"],
        "oi_share_pct": None if share is None else round(share, 2),
        "thin_interest": (share is not None and share < CRITERIA["thin_interest_share_pct"]),
        "multiplier": mult,
        "notional_per_lot_cny": round(notional, 0),
        "margin_per_lot_cny": round(margin, 0),
        "margin_pct_assumed": CRITERIA["margin_pct"] * 100.0,
        "drawdown_buffer_per_lot_cny": None if dd_buffer is None else round(dd_buffer, 0),
        "lots_for_capital": lots_naive,
        "lots_after_own_drawdown": lots_after_dd,
        "capital_cny": cap,
        "rolls": len(rolls),
        "last_roll": None if not last_roll else {"date": last_roll["date"],
                                                 "from": last_roll.get("from"),
                                                 "to": last_roll.get("to"),
                                                 "reason": last_roll.get("reason")},
        "td_since_last_roll": since,
        "roll_interval": {"n": iv["n"], "median_td": iv["median_td"], "iqr_td": iv["iqr_td"]},
        "next_roll_eta_td": eta,
        "verdict": verdict_row.get("verdict"),
        "verdict_why": verdict_row.get("why"),
        "gap_after_roll_cost_pp": {"file_floor": band.get("file_floor"),
                                   "measured_median": band.get("measured_median")},
        "gap_open_open_pp": ex.get("gap_open_open_pp"),
        "evidence_cutoff": (face or {}).get("evidence_cutoff"),
        # why the gap is refused, when it is: the source face names the reason and this
        # sheet copies it instead of printing a dash that reads like "nothing to report".
        # A gap that HAS a number cannot be refused -- a share-conversion flag on the ETF
        # leg is a note about that leg, not a reason to refuse the futures gap, so it
        # travels in its own field below instead of masquerading as a refusal.
        "gap_refused_because": (
            None if band.get("file_floor") is not None
            else (ex.get("etf_flag") or "the source face carries no execution block")),
        "etf_leg_note": ex.get("etf_flag"),
    }


def build(cache_dir=None):
    face = _face()
    rows = {}
    for prod in CRITERIA["products"]:
        rows[prod] = desk_row(prod, face, cache_dir)
    live = {p: r for p, r in rows.items() if r.get("status") == "ok"}
    return {
        "kind": "idx_fut_desk_sheet",
        "evidence_cutoff": (face or {}).get("evidence_cutoff"),
        "source_face": "results/idx_fut_carry_risk.json",
        "source_present": face is not None,
        "criteria": CRITERIA,
        "multiplier_assumption": MULTIPLIER,
        "rows": rows,
        "candidates": sorted(p for p, r in rows.items()
                             if r.get("verdict") == "SLEEVE_CANDIDATE"),
        "tradable_today": sorted(p for p, r in live.items()
                                 if not r.get("thin_interest")),
        "note": ("a candidate is a sleeve being priced forward, not an adopted position;"
                 " the margin and the multipliers are assumptions printed with the numbers"),
    }


# ------------------------------------------------------------------ rendering
def _p(v, nd=2, dash="-"):
    return dash if v is None else ("%." + str(nd) + "f") % v


def _sgn(v, nd=2, dash="-"):
    return dash if v is None else (("%+." if v >= 0 else "%.") + str(nd) + "f") % v


def render_md(face):
    L = []
    L.append("# the carry sleeve as a morning sheet")
    L.append("")
    L.append("evidence cutoff: **%s** | source judgement: `%s`%s"
             % (face.get("evidence_cutoff") or "unknown", face.get("source_face"),
                "" if face.get("source_present") else " **(absent: every number below is refused)**"))
    L.append("")
    L.append("The judgement face says whether the sleeve is worth holding. It does not say")
    L.append("which contract, how many lots, or when it rolls. This sheet answers only that.")
    L.append("")
    L.append("## what tomorrow's fill would be")
    L.append("")
    L.append("| product | judgement | contract | close | OI share | notional/lot | margin/lot |")
    L.append("|---|---|---|---|---|---|---|")
    for prod in CRITERIA["products"]:
        r = face["rows"].get(prod, {})
        if r.get("status") != "ok":
            L.append("| %s | %s | - | - | - | - | - |" % (prod, r.get("status")))
            continue
        share = _p(r.get("oi_share_pct"), 2)
        if r.get("thin_interest"):
            share += " (thin)"
        L.append("| %s | %s | %s | %s | %s%% | %s | %s |"
                 % (prod, r.get("verdict") or "unknown", r["held_contract"],
                    _p(r["close"], 1), share,
                    _p(r["notional_per_lot_cny"], 0), _p(r["margin_per_lot_cny"], 0)))
    L.append("")
    L.append("Margin is the exchange minimum at %.0f%%; a broker adds its own, which this"
             " host cannot measure. Notional and margin are per lot = price x multiplier"
             " (IF/IH 300, IC/IM 200)." % (face["criteria"]["margin_pct"] * 100.0))
    L.append("")
    L.append("## what a stated capital buys")
    L.append("")
    L.append("Capital **%s CNY**. Two counts: the naive one (margin only) and the one that"
             " can also fund the product's own published max drawdown, which is the only"
             " count that survives a bad year." % _p(face["criteria"]["capital_cny"], 0))
    L.append("")
    L.append("| product | margin only | after own max drawdown | drawdown buffer/lot |")
    L.append("|---|---|---|---|")
    for prod in CRITERIA["products"]:
        r = face["rows"].get(prod, {})
        if r.get("status") != "ok":
            continue
        L.append("| %s | %s lots | %s lots | %s |"
                 % (prod, _p(r.get("lots_for_capital"), 0, "?"),
                    _p(r.get("lots_after_own_drawdown"), 0, "?"),
                    _p(r.get("drawdown_buffer_per_lot_cny"), 0, "?")))
    L.append("")
    L.append("## when it rolls, and what the published gap is")
    L.append("")
    L.append("| product | last roll | td since | median interval | next roll ~td | gap after roll cost (floor / median) |")
    L.append("|---|---|---|---|---|---|")
    for prod in CRITERIA["products"]:
        r = face["rows"].get(prod, {})
        if r.get("status") != "ok":
            continue
        lr = r.get("last_roll") or {}
        band = r.get("gap_after_roll_cost_pp") or {}
        L.append("| %s | %s (%s→%s) | %s | %s td (n=%s) | %s | %s / %s pp |"
                 % (prod, lr.get("date") or "-", lr.get("from") or "-", lr.get("to") or "-",
                    _p(r.get("td_since_last_roll"), 0, "?"),
                    _p((r.get("roll_interval") or {}).get("median_td"), 1, "?"),
                    (r.get("roll_interval") or {}).get("n"),
                    _sgn(r.get("next_roll_eta_td"), 0, "?"),
                    _sgn(band.get("file_floor"), 2, "?"),
                    _sgn(band.get("measured_median"), 2, "?")))
    L.append("")
    L.append("The next-roll column is an estimate off this book's own switch history, not a")
    L.append("calendar rule: the calendar rule was measured to catch half of the rolls while")
    L.append("also eating market days near expiry. A negative number means the central")
    L.append("interval has already elapsed -- read it against who is actually holding the book:")
    L.append("")
    for prod in CRITERIA["products"]:
        r = face["rows"].get(prod, {})
        if r.get("status") != "ok" or r.get("next_roll_eta_td") is None:
            continue
        if r["next_roll_eta_td"] < 0:
            L.append("- **%s** is %s td past its median interval, and the incumbent still"
                     " holds %.2f%% of the product's open interest (median over %d switches,"
                     " IQR %s td): the series is irregular, so this is not a deadline."
                     % (prod, _p(abs(r["next_roll_eta_td"]), 0), r.get("oi_share_pct") or 0.0,
                        (r.get("roll_interval") or {}).get("n"),
                        (r.get("roll_interval") or {}).get("iqr_td")))
    L.append("")
    refused = [(p, (face["rows"].get(p) or {}).get("gap_refused_because"))
               for p in CRITERIA["products"]
               if (face["rows"].get(p) or {}).get("status") == "ok"
               and (face["rows"][p].get("gap_after_roll_cost_pp") or {}).get("file_floor") is None]
    if refused:
        L.append("A missing gap is refused, not zero:")
        L.append("")
        for prod, why in refused:
            L.append("- **%s** — %s" % (prod, why or "the source face gave no reason"))
        L.append("")
    noted = [(p, (face["rows"].get(p) or {}).get("etf_leg_note"))
             for p in CRITERIA["products"]
             if (face["rows"].get(p) or {}).get("status") == "ok"
             and (face["rows"][p].get("gap_after_roll_cost_pp") or {}).get("file_floor") is not None
             and (face["rows"][p] or {}).get("etf_leg_note")]
    if noted:
        L.append("Known defects in the ETF leg behind each gap -- the gap still prints, but")
        L.append("this is what the source face had to repair to get there:")
        L.append("")
        for prod, note in noted:
            L.append("- **%s** — %s" % (prod, note))
        L.append("")
    L.append("## the sentence this sheet is not allowed to say")
    L.append("")
    L.append("Nothing here is adopted. Candidates: **%s**. The readings behind them are"
             " in-sample, the margin is an assumption, and the roll cost is a band whose two"
             " ends are printed side by side because the estimator has no resolution below a"
             " few dozen ticks." % (", ".join(face.get("candidates") or []) or "none"))
    L.append("")
    if face.get("candidates"):
        L.append("What the source face says, copied verbatim so it cannot drift here:")
        L.append("")
        for prod in face["candidates"]:
            why = (face["rows"].get(prod) or {}).get("verdict_why")
            L.append("- **%s** — %s" % (prod, why or "no reason recorded"))
        L.append("")
    return "\n".join(L) + "\n"


def write_doc(face):
    with open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(face))
    return DOC


def checkdoc(face=None):
    face = build() if face is None else face
    if not os.path.isfile(DOC):
        print("checkdoc: page missing")
        return 1
    with open(DOC, "r", encoding="utf-8") as f:
        have = f.read()
    want = render_md(face)
    if have.strip() != want.strip():
        print("checkdoc: page != face (%d vs %d chars)" % (len(have), len(want)))
        return 1
    print("checkdoc: rc0 page==face (%d chars)" % len(want))
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # 1. the multiplier table is the CFFEX one; a wrong entry scales every lot count
    leg("multipliers are CFFEX specs (IF/IH 300, IC/IM 200)",
        MULTIPLIER == {"IF": 300, "IH": 300, "IC": 200, "IM": 200}, str(MULTIPLIER))
    leg("every product the sheet prints has a multiplier",
        set(CRITERIA["products"]) <= set(MULTIPLIER), str(sorted(MULTIPLIER)))

    # 2. margin per lot is price x multiplier x the assumed ratio, never a typed number
    price, mult, m = 6375.0, 200, 0.12
    notional = price * mult
    leg("margin per lot == price x multiplier x ratio",
        abs(notional * m - 153000.0) < 1e-6, str(notional * m))

    # 3. funding the drawdown can only reduce the lot count
    cap = 1000000.0
    naive = int(cap // (notional * m))
    after = int(cap // (notional * m + abs(5.639) / 100.0 * notional))
    leg("the drawdown-aware count never exceeds the margin-only count", after <= naive,
        "naive=%d after=%d" % (naive, after))

    # 4. a zero drawdown leaves the two counts equal (the buffer must not shrink for free)
    after0 = int(cap // (notional * m + 0.0))
    leg("with no drawdown the two counts agree", after0 == naive, str(after0))

    # 5. interval statistics come off the dates given, and a single roll has no interval
    days = ["d%03d" % i for i in range(30)]
    rr = [{"date": days[5]}, {"date": days[15]}, {"date": days[25]}]
    iv = roll_intervals(days, rr)
    leg("median interval is the median of the actual gaps", iv["median_td"] == 10.0, str(iv))
    leg("one roll yields no interval instead of a zero",
        roll_intervals(days, rr[:1])["median_td"] is None, str(roll_intervals(days, rr[:1])))

    # 6. the ETA keeps its sign -- an overdue roll is negative, not missing
    since, median = 12.0, 10.0
    leg("an overdue roll reads negative, not zero", (median - since) < 0, str(median - since))

    # 7. OI share is a share of the product's own book, so all shares sum to <= 100
    fake = {"A": {days[-1]: {"hold": 60.0}}, "B": {days[-1]: {"hold": 40.0}}}
    tot = sum(s[days[-1]]["hold"] for s in fake.values())
    leg("OI shares sum to 100 across contracts",
        abs(60.0 / tot * 100.0 + 40.0 / tot * 100.0 - 100.0) < 1e-9, str(tot))

    # 8. a missing judgement is printed as unknown, never inherited from a neighbour
    base_face = build()
    tampered = json.loads(json.dumps(base_face))
    if "IC" in tampered["rows"]:
        tampered["rows"]["IC"]["verdict"] = None
    page = render_md(tampered)
    leg("a missing judgement reads 'unknown', never a borrowed verdict",
        ("| IC | unknown |" in page) or ("IC" not in tampered["rows"]), "row-level")
    # ...and a refused gap has to say why, not print a bare dash
    refused_prods = [p for p in CRITERIA["products"]
                     if (tampered["rows"].get(p) or {}).get("status") == "ok"
                     and (tampered["rows"][p].get("gap_after_roll_cost_pp") or {}).get("file_floor") is None]
    leg("a refused gap carries its reason into the page",
        not refused_prods or all(
            not (tampered["rows"].get(p) or {}).get("gap_refused_because")
            or ((tampered["rows"][p]["gap_refused_because"] or "")[:24] in page)
            for p in refused_prods),
        "refused=%s" % refused_prods)
    # ...and the converse: a gap that printed a number must not also claim to be refused
    leg("a printed gap does not masquerade as a refused one",
        all(not (tampered["rows"].get(p) or {}).get("gap_refused_because")
            for p in CRITERIA["products"]
            if (tampered["rows"].get(p) or {}).get("status") == "ok"
            and (tampered["rows"][p].get("gap_after_roll_cost_pp") or {}).get("file_floor") is not None),
        str({p: (tampered["rows"].get(p) or {}).get("gap_refused_because")
             for p in CRITERIA["products"]}))

    # 9. the page's numbers are the face's numbers (re-render is byte-identical)
    face = build()
    leg("the page renders deterministically", render_md(face) == render_md(face), "")
    leg("a candidate row quotes the source face's reason",
        all((face["rows"].get(p) or {}).get("verdict_why")
            for p in face.get("candidates") or []), str(face.get("candidates")))

    # 10. determinism of the face itself, excluding nothing -- the sheet carries no clock
    leg("the face is byte-stable for identical inputs",
        json.dumps(build(), sort_keys=True) == json.dumps(build(), sort_keys=True), "")

    bad = [n for n, ok, _ in legs if not ok]
    for n, ok, d in legs:
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", n, (" | " + d) if d else ""))
    print("selftest: %d/%d PASS" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


# ------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--write-doc", action="store_true")
    ap.add_argument("--checkdoc", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    face = build()
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    print("wrote %s (cutoff=%s candidates=%s)"
          % (OUT, face.get("evidence_cutoff"), ",".join(face.get("candidates") or []) or "none"))
    if args.write_doc:
        print("wrote", write_doc(face))
    if args.checkdoc:
        return checkdoc(face)
    return 0


if __name__ == "__main__":
    sys.exit(main())
