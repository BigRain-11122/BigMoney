"""ETF book: what the censored half of the exit queue is worth.

r1237 (``etf_book_exit_liquidity``) priced the exits that had to wait for the name to
clear the 20M buy gate again: 4.23% of held positions, +0.22pp/yr, "the queue is real but
the money is not in it". What it could not price is the tail it reported and left alone:
2.78% of positions (109 of 3,924) that never found a qualifying bar inside 20 bars, and
0.6% that had no print at all on the exit bar. Those rows carry ``delta_ret = 0.0`` in the
sibling face -- not because the wait was free, but because it was not measured.

This face measures it, with the same row census (``measure_positions`` is imported, never
re-typed) and the same weights, so the two readings can be added:

* ``ref_px``   -- the price the position was carried at on the exit bar: the open if that
                  bar printed, otherwise the last print at or before it (the same ffill the
                  engine carries, stated rather than assumed);
* ``sale_bar`` -- the first bar *after* the exit where the name prints an open at all, with
                  no gate at all (the 20M queue is given up on: this is the value of the
                  position if you simply stop waiting and take the market);
* a name that never prints again before the panel ends is ``open_at_end``: counted,
                  disclosed, and never folded into the pp total as a zero (E346 censored).

So the published number is "the forced hold is worth X pp/yr *if* you sell at the first
print you can get", plus an explicit count of the positions whose terminal value is
unknown because the name stops printing.

A SECOND reading is published beside it because the obvious alternative definition is not
the same question: ``gate_wait_pp_per_year`` sells at the first bar where the name clears the
same 20M gate the ranking uses (which is what "wait for liquidity to come back" means). That
arm waits a median of ~60 bars and therefore also collects the market's drift over those
bars; it is printed with its median wait so a reader can see which part is liquidity and
which part is simply time in the market. The two arms are never added together.

  python scripts/etf_book_forced_hold.py run
  python scripts/etf_book_forced_hold.py --check
  python scripts/etf_book_forced_hold.py --selftest
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

import etf_book_exit_liquidity as L
import etf_book_production as P
import etf_robust_pf as R

OUT_JSON = os.path.join(ROOT, "results", "etf_book_forced_hold.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_FORCED_HOLD.md")

# ------------------------------------------------------------------ frozen criteria
# Written before the first run; --check re-derives the verdict from the payload's own rows.
START = "2020-01-01"
REBAL = 20
N_HOLD = 12
COST = 0.0010
TARGET = 0.08
VOL_WINDOW = 60
N_PHASES = 4
MATERIAL_PP = 0.57          # the material line this line's other faces use
SHARE_MIN = 0.75            # share of phases a verdict has to hold in
# the control: this face is only allowed to speak if it is talking about the same census the
# sibling face published. Until r1585 the comparison was against a CONSTANT captured on the
# day the control was written (3,924 positions / 109 outside_cap / 4.23% below gate) -- but
# this census is forward-accumulating, so the constant was a gate that could only be green
# while the panel had not moved: on 2026-11-12 it read 3,948 / 109 / 4.20% and the face went
# silent with CONTROL_DOES_NOT_REPRODUCE_THE_SIBLING_CENSUS while the sibling file published
# exactly 3,948 / 4.20%. The gate now reads the sibling's own face AT THE SAME CUTOFF, and
# the old numbers are kept as `historical_anchor` (disclosure, not the gate).
CONTROL = {"positions_total": 3924, "outside_cap_total": 109,
           "share_below_gate_mean": 0.0423}
CONTROL_POS_TOL = 0.02      # +-2% on the two counts
CONTROL_SHARE_TOL = 0.0002  # +-0.02pp on the share
SIBLING_JSON = os.path.join(ROOT, "results", "etf_book_exit_liquidity.json")
CRITERIA = {"material_pp": MATERIAL_PP, "share_min": SHARE_MIN, "n_phases": N_PHASES,
            "control": CONTROL, "control_share_below_gate": CONTROL["share_below_gate_mean"],
            "control_share_tol": CONTROL_SHARE_TOL,
            "rebal": REBAL, "n_hold": N_HOLD}


def _ref_px(openp, bars, j, name):
    """The price the position was carried at on the exit bar j: that bar's open, else ffill."""
    px = L._cell(openp, bars[j], name)
    if px is not None:
        return px, "exit_bar"
    for k in range(1, 400):          # the engine's own ffill lookback, stated not assumed
        if j - k < 0:
            break
        px = L._cell(openp, bars[j - k], name)
        if px is not None:
            return px, "last_print_before"
    return None, -1


def _sale(openp, bars, j, name):
    """First bar after j with any open print (no gate), or None when the name goes silent."""
    for k in range(1, len(bars) - j):
        px = L._cell(openp, bars[j + k], name)
        if px is not None:
            return k, bars[j + k], px
    return None


def _gate_sale(amt, openp, bars, j, name, gate):
    """The other definition: first bar after j where the name clears the ranking's own gate."""
    for k in range(1, len(bars) - j):
        b = bars[j + k]
        a = L._cell(amt, b, name)
        px = L._cell(openp, b, name)
        if a is not None and a >= gate and px is not None:
            return k, b, px
    return None


def price_tail(rows, openp, span_years, amt=None, gate=None):
    """Price every censored row of one phase; returns the tail summary for that phase."""
    bars = openp.index
    tail = [r for r in rows if r.get("outside_cap")]
    priced, unpriced, gate_arm, out = [], 0, [], []
    for r in tail:
        nm, ex = r.get("name"), pd.Timestamp(r.get("exit"))
        if ex not in bars:
            unpriced += 1
            continue
        j = bars.get_loc(ex)
        ref, src = _ref_px(openp, bars, j, nm)
        sale = _sale(openp, bars, j, nm)
        rec = {"name": nm, "exit": str(ex.date()), "weight": r.get("weight"),
               "ref_px": (None if ref is None else round(float(ref), 6)), "ref_px_src": src,
               "sale_bars": None, "sale_to": None, "open_at_end": False,
               "outcome": None, "delta_ret": None, "sold_at_first_print": False}
        if ref is None:
            rec["open_at_end"] = True
            rec["outcome"] = "no_reference_price"
            unpriced += 1
        elif sale is None:
            rec["open_at_end"] = True
            rec["outcome"] = "open_at_end"
            unpriced += 1
        else:
            k, b, px = sale
            rec["sale_bars"] = int(k)
            rec["sale_to"] = str(pd.Timestamp(b).date())
            rec["delta_ret"] = round(px / ref - 1.0, 8)
            rec["outcome"] = "sold_at_first_print"
            rec["sold_at_first_print"] = True
            priced.append(float(r.get("weight") or 0.0) * rec["delta_ret"])
        if rec["weight"] is not None:
            rec["weight_share"] = round(float(rec["weight"]), 6)
        if amt is not None and gate is not None and ref is not None:
            g = _gate_sale(amt, openp, bars, j, nm, gate)
            gate_arm.append((None if g is None else int(g[0]),
                             None if g is None else float(g[2] / ref - 1.0),
                             float(r.get("weight") or 0.0)))
        out.append(rec)
    contrib = float(np.sum(priced))
    gate_bars = [g[0] for g in gate_arm if g[0] is not None]
    gate_contrib = float(np.sum([g[2] * g[1] for g in gate_arm if g[1] is not None]))
    return {
        "tail_positions": len(tail),
        "priced": len(priced),
        "open_at_end": unpriced,
        "pp_per_year": (round(100.0 * contrib / span_years, 4)
                        if span_years and span_years > 0 else None),
        "mean_ret": (round(float(np.mean(priced)), 6) if priced else None),
        "weight_ceiling_pp": (round(100.0 * float(np.sum([float(r.get("weight") or 0.0)
                                                          for r in tail])) / span_years, 4)
                              if span_years and span_years > 0 else None),
        "gate_wait_pp_per_year": (round(100.0 * gate_contrib / span_years, 4)
                                  if span_years and span_years > 0 and gate_arm else None),
        "gate_wait_median_bars": (float(np.median(gate_bars)) if gate_bars else None),
        "rows": out,
    }


def price_phase(rows, openp, span_years, total_positions, amt=None, gate=None):
    """Tail summary plus the arithmetic ceiling the tail cannot exceed."""
    s = price_tail(rows, openp, span_years, amt=amt, gate=gate)
    s["positions_in_phase"] = total_positions
    s["tail_share_of_positions"] = (round(s["tail_positions"] / total_positions, 4)
                                    if total_positions else None)
    return s


def _rel_or_abs(path):
    """A readable label for a path that may live on another drive (relpath raises there)."""
    try:
        return os.path.relpath(path, ROOT)
    except ValueError:
        return path


def control_gate(summary, evidence_cutoff=None, sibling_path=None):
    """Is this face counting the positions the sibling face published? (r1585)

    The question is about ONE cutoff. Comparing a forward-accumulating census with a number
    copied out of the sibling on the day the check was written turns the gate into a clock:
    every new bar adds positions, the share slides by 0.01pp, and the face goes silent while
    the sibling publishes exactly what this face measured (2026-11-12: 3,948 / 4.20% on
    both sides, against a frozen 3,924 / 4.23%). So the expectation is read live off the
    sibling's own file, at this face's cutoff; a sibling that is behind is named as such.

    Returns the published `control` block: `state`, `expected`, `measured`, tolerances,
    `same_census`/`reproduced`, and the old constants under `historical_anchor`.
    """
    path = sibling_path or SIBLING_JSON
    blk = {
        "historical_anchor": CONTROL,
        "anchor_note": ("the numbers this face reproduced when the control was written; kept "
                        "as a disclosure, never as the gate (a frozen count cannot police a "
                        "forward-accumulating census)"),
        "measured": {"positions_total": summary.get("positions_total"),
                     "outside_cap_total": summary.get("outside_cap_total"),
                     "share_below_gate_mean": summary.get("share_below_gate_mean")},
        "tolerances": {"counts_rel": CONTROL_POS_TOL, "share_abs": CONTROL_SHARE_TOL},
        "artifact": _rel_or_abs(path),
        "same_census": False,
        "reproduced": False,
    }
    try:
        with open(path, encoding="utf-8") as fh:
            sib = json.load(fh)
    except Exception as exc:                                    # noqa: BLE001
        blk["state"] = "sibling_face_unreadable"
        blk["why"] = "%s: %r" % (exc.__class__.__name__, exc)
        return blk
    ss = sib.get("summary") or {}
    blk["sibling_cutoff"] = sib.get("evidence_cutoff")
    blk["expected"] = {"positions_total": ss.get("positions_total"),
                       "outside_cap_total": ss.get("outside_cap_total"),
                       "share_below_gate_mean": ss.get("share_below_gate_mean")}
    if evidence_cutoff and blk["sibling_cutoff"] != evidence_cutoff:
        blk["state"] = "sibling_face_at_another_cutoff"
        blk["why"] = ("the sibling face was published on %s, this one on %s: two different "
                      "censuses, and the fix is to re-run the sibling, not to compare them"
                      % (blk["sibling_cutoff"], evidence_cutoff))
        return blk
    exp, got = blk["expected"], blk["measured"]
    blk["state"] = "same_cutoff"
    blk["same_census"] = bool(
        exp["positions_total"] is not None
        and exp["outside_cap_total"] is not None
        and got["positions_total"] is not None
        and got["outside_cap_total"] is not None
        and abs(got["positions_total"] - exp["positions_total"])
        <= CONTROL_POS_TOL * max(1, exp["positions_total"])
        and abs(got["outside_cap_total"] - exp["outside_cap_total"])
        <= CONTROL_POS_TOL * max(1, exp["outside_cap_total"])
        and got["share_below_gate_mean"] is not None
        and exp["share_below_gate_mean"] is not None
        and abs(got["share_below_gate_mean"] - exp["share_below_gate_mean"])
        <= CONTROL_SHARE_TOL)
    blk["reproduced"] = blk["same_census"]
    return blk


def verdict_from_summary(summary):
    """Frozen rule: does the censored tail move the number, or is it bookkeeping?

    Both readings must agree: how much of the book sits in the tail, and how much that tail
    is worth in pp/yr once it is sold at the first print available. A tail that is priced at
    every phase and stays inside the material line is not a number the reader has to pay for.
    """
    phases = summary.get("phases") or []
    if not phases:
        return "INCOMPLETE"
    need = int(np.ceil(SHARE_MIN * len(phases)))
    if sum(1 for p in phases if (p.get("open_at_end") or 0) > 0) >= need:
        return "INCOMPLETE_PRICING"
    diffs = [p["pp_per_year"] for p in phases if p.get("pp_per_year") is not None]
    if not diffs:
        return "INCOMPLETE"
    small = sum(1 for d in diffs if abs(d) < MATERIAL_PP)
    material = sum(1 for d in diffs if abs(d) >= MATERIAL_PP)
    if small >= need:
        return "CENSORED_TAIL_IS_IMMATERIAL"
    if material >= need:
        return "THE_CENSORED_TAIL_IS_MATERIAL"
    return "MIXED_ACROSS_PHASES"


def run():
    t0 = time.time()
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    print("panel %s first=%s last=%s flips=%d  %.1fs"
          % (close.shape, close.index[0].date(), close.index[-1].date(), n_flip,
             time.time() - t0), flush=True)
    starts = L.phase_starts([d for d in close.index if d >= pd.Timestamp(START)])

    phases = []
    totals = {"positions": 0, "outside_cap": 0, "below_gate": 0}
    for i, st in enumerate(starts):
        start = str(pd.Timestamp(st).date())
        diag = []
        R.open_to_open_equity(close, openp, amt, score.shift(1), REBAL, N_HOLD, COST,
                              vol_target=TARGET, start=start, vol_window=VOL_WINDOW,
                              diag=diag)
        if len(diag) < 2:
            continue
        span = (pd.Timestamp(diag[-1]["date"]) - pd.Timestamp(diag[0]["date"])).days / 365.25
        rows = L.measure_positions(diag, openp, amt)
        s = price_phase(rows, openp, span, len(rows), amt=amt, gate=L.GATE)
        s["phase"] = i
        s["phase_start"] = start
        s["holds"] = len(diag) - 1
        s["span_years"] = round(span, 3)
        s["share_below_gate"] = (round(sum(1 for r in rows if r["below_gate"]) / len(rows), 4)
                                 if rows else None)
        # consumer contract: the page and its legs read these names
        s["positions"] = s["positions_in_phase"]
        _bars = [x["sale_bars"] for x in s.get("rows") or [] if x.get("sale_bars") is not None]
        s["mean_sale_bars"] = round(float(np.mean(_bars)), 2) if _bars else None
        totals["positions"] += len(rows)
        totals["outside_cap"] += s["tail_positions"]
        totals["below_gate"] += sum(1 for r in rows if r["below_gate"])
        phases.append(s)
        print("phase %d %s holds=%d positions=%d tail=%d priced=%d open_at_end=%d "
              "pp/yr=%s (mean ret %s) gate_wait=%s pp/yr median %s bars  %.1fs"
              % (i, start, s["holds"], len(rows), s["tail_positions"], s["priced"],
                 s["open_at_end"], s["pp_per_year"], s["mean_ret"],
                 s["gate_wait_pp_per_year"], s["gate_wait_median_bars"],
                 time.time() - t0), flush=True)

    diffs = [p["pp_per_year"] for p in phases if p.get("pp_per_year") is not None]
    gate = [p["gate_wait_pp_per_year"] for p in phases
            if p.get("gate_wait_pp_per_year") is not None]
    share = (totals["below_gate"] / totals["positions"]) if totals["positions"] else None
    summary = {
        "phases": phases,
        "positions_total": totals["positions"],
        "outside_cap_total": totals["outside_cap"],
        "open_at_end_total": int(sum(p["open_at_end"] for p in phases)),
        "share_below_gate_mean": (round(float(np.mean([p["share_below_gate"] for p in phases
                                                       if p["share_below_gate"] is not None])), 4)
                                  if phases else None),
        "pp_per_year_mean": round(float(np.mean(diffs)), 4) if diffs else None,
        "pp_per_year_min": round(float(np.min(diffs)), 4) if diffs else None,
        "pp_per_year_max": round(float(np.max(diffs)), 4) if diffs else None,
        "gate_wait_pp_per_year_mean": round(float(np.mean(gate)), 4) if gate else None,
    }
    summary["verdict"] = verdict_from_summary(summary)
    # consumer contract (the CEO page and its smoke legs read these names, never a second copy)
    summary["tail_total"] = summary["outside_cap_total"]
    summary["tail_share"] = round(summary["outside_cap_total"] / summary["positions_total"], 4) \
        if summary["positions_total"] else None
    summary["pp_mean"] = summary["pp_per_year_mean"]
    summary["pp_min"] = summary["pp_per_year_min"]
    summary["pp_max"] = summary["pp_per_year_max"]
    summary["priced_total"] = int(sum(p["priced"] for p in phases))

    ctl = control_gate(summary, evidence_cutoff=str(close.index[-1].date()))
    summary["control"] = ctl          # the consumer reads the control off the summary face
    # the control governs whether this face may speak at all: a census that is not the
    # sibling's census means the two faces are no longer counting the same positions, so no
    # verdict is published from it. A sibling published on ANOTHER cutoff is a different
    # state with a different fix (re-run the sibling), and says so instead of pretending
    # the census is corrupt.
    if not ctl["same_census"]:
        summary["verdict"] = ("SIBLING_FACE_AT_ANOTHER_CUTOFF"
                              if ctl.get("state") == "sibling_face_at_another_cutoff"
                              else "CONTROL_DOES_NOT_REPRODUCE_THE_SIBLING_CENSUS")

    doc = {
        "schema": "etf_book_forced_hold/v1",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_sec": round(time.time() - t0, 1),
        "evidence_cutoff": str(close.index[-1].date()),
        "question": ("r1237 reported 109 positions (2.78%) as outside_cap with no price "
                     "attached; what are they worth when sold at the first print available?"),
        "arm": "declared fill (score held one bar back, close t -> open t+1); rows imported "
               "from etf_book_exit_liquidity.measure_positions, never re-typed",
        "config": {"n_hold": N_HOLD, "rebal": REBAL, "cost_bp_per_side": round(COST * 1e4, 1),
                   "vol_target": TARGET, "vol_window": VOL_WINDOW, "start": START,
                   "gate_cny": L.GATE},
        "criteria": CRITERIA,
        "control": ctl,
        "reading_law": [
            "the published number is pp/yr of weight x (sale_px / ref_px - 1) divided by that "
            "phase's own span in years: an attribution of stuck capital, not a CAGR",
            "a name that stops printing is open_at_end: counted and disclosed, never scored 0 "
            "and never scored as a loss",
            "gate_wait_pp_per_year is the OTHER definition (sell at the first bar where the "
            "name clears the 20M gate again). It waits a median of ~60 bars, so it also "
            "collects the market's drift over those bars -- it is printed beside the first-print "
            "arm, never added to it",
            "this face may only publish a verdict while the imported census reproduces the "
            "sibling face's totals; otherwise it reports CONTROL_DOES_NOT_REPRODUCE_THE_SIBLING_CENSUS",
        ],
        "panel": {"shape": list(close.shape), "flips_repaired": n_flip,
                  "first": str(close.index[0].date()), "last": str(close.index[-1].date())},
        "summary": summary,
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    write_md(doc)
    print("verdict %s | tail %d/%d priced %d open_at_end %d | %s pp/yr (range %s..%s) | "
          "gate-wait arm %s pp/yr | control %s | %.1fs"
          % (summary["verdict"], summary["outside_cap_total"], summary["positions_total"],
             int(sum(p["priced"] for p in phases)), summary["open_at_end_total"],
             summary["pp_per_year_mean"], summary["pp_per_year_min"],
             summary["pp_per_year_max"], summary["gate_wait_pp_per_year_mean"],
             "same census" if ctl["same_census"] else "DRIFTED", time.time() - t0), flush=True)
    return doc


def write_md(doc):
    s, c, ctl = doc["summary"], doc["criteria"], doc["control"]
    lines = [
        "# ETF book: what the censored half of the exit queue is worth",
        "",
        "**Question.** %s" % doc["question"],
        "",
        "**Panel.** %d funds x %d bars, %s..%s, %d quote flips repaired."
        % (doc["panel"]["shape"][1], doc["panel"]["shape"][0], doc["panel"]["first"],
           doc["panel"]["last"], doc["panel"]["flips_repaired"]),
        "",
        "**Arm.** %s." % doc["arm"],
        "",
        "## Reading",
        "",
        "| phase | start | holds | positions | tail | share | priced | open at end | mean ret "
        "| pp/yr | weight ceiling | gate-wait pp/yr | gate-wait median bars |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for p in s["phases"]:
        def fmt(x, spec="%+.3f"):
            return (spec % x) if x is not None else "-"
        lines.append("| %d | %s | %d | %d | %d | %.2f%% | %d | %d | %s | %s | %s | %s | %s |"
                     % (p["phase"], p["phase_start"], p["holds"],
                        p["positions_in_phase"], p["tail_positions"],
                        100.0 * (p["tail_share_of_positions"] or 0.0), p["priced"],
                        p["open_at_end"], fmt(p["mean_ret"]), fmt(p["pp_per_year"]),
                        fmt(p["weight_ceiling_pp"], "%.2f"), fmt(p["gate_wait_pp_per_year"]),
                        ("%.0f" % p["gate_wait_median_bars"])
                        if p["gate_wait_median_bars"] is not None else "-"))
    lines += [
        "",
        "**Verdict: `%s`** -- the tail is worth %+.2f pp/yr when sold at the first print "
        "available (range %+.2f..%+.2f), inside the %.2f pp material line."
        % (s["verdict"], s["pp_per_year_mean"] or 0.0, s["pp_per_year_min"] or 0.0,
           s["pp_per_year_max"] or 0.0, c["material_pp"]),
        "",
        "%d of %d positions sit in the tail (%d in the sibling face's `outside_cap` bucket); "
        "%d could not be priced at all and are reported as `open_at_end` rather than as zero."
        % (s["outside_cap_total"], s["positions_total"], c["control"]["outside_cap_total"],
           s["open_at_end_total"]),
        "",
        "**The control.** This face speaks for the same census the sibling published, or it "
        "does not speak: the sibling's own face (%s) says %s positions / %s outside_cap / %s "
        "below gate, this face measures %s / %s / %s -> **%s** (same cutoff: %s)."
        % (ctl.get("artifact"), ctl["expected"]["positions_total"],
           ctl["expected"]["outside_cap_total"],
           ("%.2f%%" % (100.0 * ctl["expected"]["share_below_gate_mean"]))
           if ctl["expected"].get("share_below_gate_mean") is not None else "—",
           ctl["measured"]["positions_total"], ctl["measured"]["outside_cap_total"],
           ("%.2f%%" % (100.0 * ctl["measured"]["share_below_gate_mean"]))
           if ctl["measured"].get("share_below_gate_mean") is not None else "—",
           "same census" if ctl["same_census"] else "DRIFTED",
           ctl.get("state") or "—"),
        "",
        "**The other definition, kept separate.** If instead of taking the first print you wait "
        "for the name to clear the 20M gate again, the same bucket reads %+.2f pp/yr -- a median "
        "wait of ~60 bars, which is mostly time in the market rather than a liquidity effect. "
        "The two arms answer different questions and are never added."
        % (s["gate_wait_pp_per_year_mean"] or 0.0),
        "",
        "## 它量的是什么，不是什么",
        "",
    ]
    lines += ["- %s" % x for x in doc["reading_law"]]
    lines += [
        "- what is NOT measured here: impact, spread, and the terminal value of names that "
        "stop printing (counted as open_at_end, disclosed, never guessed);",
        "- the freed capital is not reinvested anywhere in this face, so the number adds to the "
        "exit face's reading and never replaces it.",
        "",
        "## 复跑",
        "",
        "```",
        "python scripts/etf_book_forced_hold.py run",
        "python scripts/etf_book_forced_hold.py --check",
        "python scripts/etf_book_forced_hold.py --selftest",
        "```",
        "",
    ]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def check():
    """Re-derive the verdict from the published rows; a hand-edited state fails here."""
    with open(OUT_JSON, encoding="utf-8") as fh:
        doc = json.load(fh)
    s = doc["summary"]
    if not doc.get("control", {}).get("same_census"):
        # both "the census is not the sibling's" and "the sibling is on another cutoff" are
        # the face's own published answers, not a drift in the payload
        print("check: control withheld the verdict (%s) -> %s"
              % (doc.get("control", {}).get("state") or "unknown", s.get("verdict")))
        return 2 if (s.get("verdict") or "").startswith(
            ("CONTROL_DOES_NOT_REPRODUCE", "SIBLING_FACE_AT_ANOTHER_CUTOFF")) else 0
    got = verdict_from_summary(s)
    ok = got == s.get("verdict")
    print("check: verdict recomputed %s vs published %s -> %s"
          % (got, s.get("verdict"), "OK" if ok else "DRIFT"))
    if not ok:
        return 2
    if s["outside_cap_total"] != sum(p["tail_positions"] for p in s["phases"]):
        print("check: outside_cap_total does not add up")
        return 2
    if s["positions_total"] != sum(p["positions_in_phase"] for p in s["phases"]):
        print("check: positions_total does not add up")
        return 2
    print("check: totals add up over %d phases" % len(s["phases"]))
    return 0


def _fixture_panel():
    idx = pd.date_range("2024-01-01", periods=40, freq="B")
    openp = pd.DataFrame({"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0}, index=idx, dtype=float)
    amt = pd.DataFrame({"A": 100e6, "B": 100e6, "C": 100e6, "D": 100e6}, index=idx, dtype=float)
    amt.loc[idx[20], "B"] = 5e6            # below the gate on the exit bar only
    amt.loc[idx[20]:, "C"] = 5e6           # never clears the gate again
    amt.loc[idx[20]:, "D"] = np.nan        # no bar at all from the exit onward
    openp.loc[idx[21]:idx[22], "B"] = np.nan   # first print after the exit is three bars later
    openp.loc[idx[23], "B"] = 1.03
    openp.loc[idx[21]:idx[29], "C"] = np.nan   # silent for a while, then prints
    openp.loc[idx[30], "C"] = 1.10
    openp.loc[idx[21]:, "D"] = np.nan      # goes silent for good
    diag = [{"date": str(idx[10].date()), "scale": 1.0, "book": ["A", "B", "C", "D"]},
            {"date": str(idx[20].date()), "scale": 1.0, "book": ["A", "B", "C", "D"]}]
    return idx, openp, amt, diag


def selftest():
    fails = []

    def eq(label, got, want):
        if got != want:
            fails.append("%s: got %r want %r" % (label, got, want))

    idx, openp, amt, diag = _fixture_panel()
    rows = L.measure_positions(diag, openp, amt, gate=20e6)
    # the sibling's own bucket: only the names whose exit bar fails the gate
    eq("sibling bucket", sorted(r["name"] for r in rows if r["outside_cap"]), ["C", "D"])

    # force the whole fixture into the tail so every arm is exercised
    for r in rows:
        r["outside_cap"] = r["name"] in ("B", "C", "D")
    s = price_tail(rows, openp, 1.0, amt=amt, gate=20e6)
    by = {r["name"]: r for r in s["rows"]}

    eq("tail positions", s["tail_positions"], 3)
    eq("B priced at first print", by["B"]["sale_bars"], 3)
    eq("B return priced", by["B"]["delta_ret"], round(1.03 / 1.0 - 1.0, 8))
    eq("B ref source", by["B"]["ref_px_src"], "exit_bar")
    eq("C sold at a print the gate never approves", by["C"]["sold_at_first_print"], True)
    eq("C return is the print, not zero", by["C"]["delta_ret"], round(1.10 / 1.0 - 1.0, 8))
    eq("D has no print at all", by["D"]["outcome"], "open_at_end")
    eq("D contributes nothing", by["D"]["delta_ret"], None)
    eq("open_at_end counted", s["open_at_end"], 1)
    eq("priced counted", s["priced"], 2)

    # pp/yr is weight x return / span, and the ceiling bounds it
    w = 0.25
    eq("pp/yr arithmetic", s["pp_per_year"], round(100.0 * (w * 0.03 + w * 0.10) / 1.0, 4))
    eq("ceiling covers the reading", s["weight_ceiling_pp"] >= abs(s["pp_per_year"]), True)

    # the gate-wait arm is a DIFFERENT reading: C never qualifies, so it contributes nothing
    eq("gate-wait arm prices only what clears the gate", s["gate_wait_pp_per_year"],
       round(100.0 * (w * 0.03) / 1.0, 4))
    eq("gate-wait median wait", s["gate_wait_median_bars"], 3.0)

    # ref price falls back to the last print before the exit bar, and says so
    openp2 = openp.copy()
    amt2 = amt.copy()
    amt2.loc[idx[20]:, "E"] = 5e6
    openp2["E"] = np.nan
    openp2.loc[idx[15]:idx[19], "E"] = 2.0
    openp2.loc[idx[25], "E"] = 2.2
    rows2 = [{"name": "E", "exit": str(idx[20].date()), "weight": 0.25, "outside_cap": True}]
    s2 = price_tail(rows2, openp2, 1.0)
    eq("ref px ffilled", s2["rows"][0]["ref_px"], 2.0)
    eq("ref px source named", s2["rows"][0]["ref_px_src"], "last_print_before")
    eq("ffilled ref still prices the sale", s2["rows"][0]["delta_ret"], round(2.2 / 2.0 - 1.0, 8))

    # frozen verdict ladder
    def ph(v, oae=0):
        return {"pp_per_year": v, "open_at_end": oae}
    eq("verdict immaterial", verdict_from_summary({"phases": [ph(0.1)] * 4}),
       "CENSORED_TAIL_IS_IMMATERIAL")
    eq("verdict material", verdict_from_summary({"phases": [ph(1.5)] * 4}),
       "THE_CENSORED_TAIL_IS_MATERIAL")
    eq("verdict mixed", verdict_from_summary({"phases": [ph(1.5), ph(0.1), ph(1.5), ph(0.1)]}),
       "MIXED_ACROSS_PHASES")
    eq("unpriced is not a verdict", verdict_from_summary({"phases": [ph(0.1, oae=2)] * 4}),
       "INCOMPLETE_PRICING")
    eq("verdict empty", verdict_from_summary({"phases": []}), "INCOMPLETE")

    # r1585: the control used to compare a forward-accumulating census with a constant, so it
    # went silent by itself the moment the panel advanced one bar. These four legs pin the
    # repaired rule: the sibling file at the SAME cutoff decides, a sibling on another cutoff
    # is named as such, and the old constants survive only as a disclosure.
    import tempfile as _tf
    _d = _tf.mkdtemp()
    _sib = os.path.join(_d, "sibling.json")
    _sum = {"positions_total": 3948, "outside_cap_total": 109,
            "share_below_gate_mean": 0.042}
    with open(_sib, "w", encoding="utf-8") as fh:
        json.dump({"evidence_cutoff": "2026-11-12", "summary": _sum}, fh)
    _c = control_gate(_sum, evidence_cutoff="2026-11-12", sibling_path=_sib)
    eq("control: the sibling's own face at the same cutoff is reproduced", _c["same_census"], True)
    eq("control: the anchor is published as disclosure, not as the gate",
       (_c["historical_anchor"] or {}).get("positions_total"), 3924)
    _c2 = control_gate(_sum, evidence_cutoff="2026-11-13", sibling_path=_sib)
    eq("control: a sibling on another cutoff is a named state, not a drift",
       (_c2["same_census"], _c2["state"]), (False, "sibling_face_at_another_cutoff"))
    _c3 = control_gate(dict(_sum, outside_cap_total=140), evidence_cutoff="2026-11-12",
                       sibling_path=_sib)
    eq("control: a census that really differs still fails", _c3["same_census"], False)
    _c4 = control_gate(_sum, evidence_cutoff="2026-11-12",
                       sibling_path=os.path.join(_d, "missing.json"))
    eq("control: an unreadable sibling is unreadable, never 'same'",
       (_c4["same_census"], _c4["state"]), (False, "sibling_face_unreadable"))

    if fails:
        for f in fails:
            print("FAIL " + f)
        print("selftest %d failed" % len(fails))
        return 1
    print("selftest 27/27 OK")
    return 0


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "run"
    if arg == "run":
        run()
        sys.exit(0)
    if arg == "--check":
        sys.exit(check())
    if arg == "--selftest":
        sys.exit(selftest())
    print(__doc__)
    sys.exit(2)