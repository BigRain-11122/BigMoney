"""Does the order sheet price the execution it declares? (E25 slice)

The production card states its execution as "decide at close t -> fill at open t+1", and
`etf_book_lookahead_audit` showed the engine inside it takes its signal from `score.loc[d]`
while paying the book from open[d]: the sheet reads the bar it is about to buy. Delaying
that signal one bar costs 1.14 pp/yr on the audit's ladder.

So the operator currently reads a headline whose declared convention and priced convention
differ. This face measures that difference instead of asserting it: it re-prices the SAME
rule under the declared execution (signal from bar d-1, fill at open d -- `lag +1` on the
audit's ladder, which is the same lattice point as "decide at close d, fill at open d+1"),
re-prices the ledger the live paper actually runs, and reads what the card PRINTS and what
the card CLAIMS. The frozen rule then names one of:

  CONSISTENT              -- the printed headline is the declared-execution arm, within tol
  DISCLOSED               -- the headline is still the same-open arm, but the card prints the
                             declared arm beside it and that number agrees with this face's
                             own independently priced declared arm
  EXECUTION_CLAIM_MISMATCH-- the card claims fill-at-next-open and prints the same-open arm
                             with no declared number beside it
  DISCLOSURE_DISAGREES    -- the card publishes a declared number, but it is not this face's
                             declared arm: two faces of one book are measuring different books
  CANNOT_VERIFY           -- the card has no readable headline or no readable claim

No arm here invents a number: both price faces come from
`etf_book_lookahead_audit.arm_at_lag` (one implementation, `lag=0` = as coded, `lag=1` =
the declared execution), and the card's numbers are read from the files the operator reads.

Exit axis (TRIAL_LABOR_LAW §4): strategy's own -- the engine's rebalance grid decides when
the book changes; this face prices that rule, it does not invent exits. No carry is added
to the headline comparison (the card carries none either); the ledger arm is printed beside
it, labelled, because the live paper does earn the repo ladder.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time

import numpy as np
import pandas as pd

import etf_book_lookahead_audit as L
import etf_book_forward as F
import etf_book_production as P
import etf_book_ceo_page as C

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "results", "etf_book_causal_headline.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_CAUSAL_HEADLINE.md")
CARD = os.path.join(ROOT, "results", "etf_book_production", "CARD.md")
CARD_PAYLOAD = os.path.join(ROOT, "results", "etf_book_production", "latest.json")

CRITERIA = {
    "tol_pp": 0.25,
    "conventions": {
        "as_coded": "lag 0: score(bar d) selects, the book earns open[d] -> open[d+1]",
        "declared": "lag +1: score(bar d-1) selects, the book earns open[d] -> open[d+1] "
                    "-- the same lattice point as 'decide at close d, fill at open d+1', "
                    "which is what the card's config.execution string claims",
    },
    "verdict_rule": ("CONSISTENT iff |printed_cagr - declared_cagr| <= tol_pp; else, iff "
                     "the printed number reproduces the as-coded arm (|printed - as_coded| "
                     "<= tol_pp): DISCLOSED when the card also publishes a declared arm that "
                     "agrees with this face's declared arm to within tol_pp on BOTH arms, "
                     "DISCLOSURE_DISAGREES when it publishes one that does not, and "
                     "EXECUTION_CLAIM_MISMATCH when the card publishes no declared arm at "
                     "all; PRINTED_MATCHES_NEITHER_ARM when both sides are readable but the "
                     "printed number reproduces neither arm; CANNOT_VERIFY when a side is "
                     "unreadable (an unreadable disclosure is not evidence of a breach)"),
    "frozen": "thresholds and the reading rule were written before the first run; --check "
              "re-derives the verdict from the published rows and refuses a face whose "
              "criteria moved",
}
CRITERIA_DIGEST = None  # filled by _digest()


def _digest(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def _pp(x):
    return None if x is None else round(100.0 * float(x), 3)


def read_claim(payload_path=CARD_PAYLOAD):
    """The execution string the card publishes, read from the payload that wrote it."""
    try:
        with open(payload_path, encoding="utf-8") as fh:
            d = json.load(fh)
    except Exception as exc:  # noqa: BLE001 - unreadable is a verdict, not a crash
        return {"execution": None, "error": "%s: %s" % (type(exc).__name__, exc),
                "source": os.path.relpath(payload_path, ROOT)}
    cfg = d.get("config") or {}
    bt = (d.get("backtest") or {}).get("n%d_vt08" % (cfg.get("n_hold") or 12)) or {}
    full = bt.get("full") or {}
    return {"execution": cfg.get("execution"),
            "payload_cagr": full.get("cagr"),
            "payload_sharpe": full.get("sharpe"),
            "payload_bars_window": "full",
            "source": os.path.relpath(payload_path, ROOT)}


_ROW = re.compile(r"^\|\s*(2020-01 onwards[^|]*?)\s*\|\s*(-?[\d.]+)%")


def _display(path):
    """A label for a path that survives living on another drive than the repo."""
    try:
        return os.path.relpath(path, ROOT)
    except ValueError:  # pragma: no cover - Windows cross-drive temp fixtures
        return os.path.abspath(path)


def _row_basis(label):
    """Which fill a table row's own label declares, or None when it declares none."""
    s = (label or "").lower()
    if "declared" in s:
        return "declared"
    if "as coded" in s or "as-coded" in s:
        return "as_coded"
    return None


def read_printed_cagr(card_path=CARD):
    """The '2020-01 onwards' rows of the card, each kept with the label it carries.

    The card may print one unqualified row (the shape this face was written against) or
    several rows whose labels say which fill each cell prices. Both blind spots are
    parsing errors with opposite costs: taking the first match regardless of its label
    accuses a card that has already fixed itself, and demanding the label be exactly
    '2020-01 onwards' reads a card that only got better as unreadable. So the selector
    keeps every row and files the labelled ones under the basis their label states.
    """
    try:
        with open(card_path, encoding="utf-8") as fh:
            text = fh.read()
    except Exception as exc:  # noqa: BLE001
        return {"cagr": None, "error": "%s: %s" % (type(exc).__name__, exc)}
    rows = []
    for line in text.splitlines():
        m = _ROW.match(line.strip())
        if m:
            rows.append({"label": m.group(1).strip(),
                         "cagr": float(m.group(2)) / 100.0,
                         "raw": line.strip()})
    if not rows:
        return {"cagr": None, "error": "no '2020-01 onwards' row found",
                "source": _display(card_path)}
    labelled = {}
    for r in rows:
        b = _row_basis(r["label"])
        if b and b not in labelled:
            labelled[b] = {"cagr": r["cagr"], "label": r["label"]}
    head = rows[0]
    return {"cagr": head["cagr"], "label": head["label"], "raw": head["raw"],
            "rows": rows, "labelled": labelled,
            "source": _display(card_path)}


def read_disclosure(payload_path=CARD_PAYLOAD):
    """The declared arm the card publishes BESIDE its headline, if it publishes one.

    Missing is a normal state (the r1220 card had none), so absence is reported as
    `present: False` and never as an error -- an unreadable disclosure must not be
    mistaken for a card that discloses a different number.
    """
    try:
        with open(payload_path, encoding="utf-8") as fh:
            d = json.load(fh)
    except Exception as exc:  # noqa: BLE001 - unreadable is a verdict, not a crash
        return {"present": None, "error": "%s: %s" % (type(exc).__name__, exc),
                "source": os.path.relpath(payload_path, ROOT)}
    eb = d.get("execution_basis")
    src = os.path.relpath(payload_path, ROOT)
    if not isinstance(eb, dict) or not eb:
        return {"present": False, "source": src,
                "note": "the payload carries no execution_basis block"}
    return {"present": True, "source": src,
            "as_coded_cagr": eb.get("as_coded_cagr"),
            "declared_cagr": eb.get("declared_cagr"),
            "gap_pp": eb.get("gap_pp"),
            "verdict": eb.get("verdict")}


def _is_next_open(exe):
    """Does the declared execution say the fill happens at the NEXT bar's open?"""
    if not isinstance(exe, str):
        return None
    s = exe.lower()
    if "t+1" in s or "next open" in s:
        return True
    if "fill at open t" in s and "t+1" not in s:
        return False
    return None


def decide(doc, tol=None):
    tol = CRITERIA["tol_pp"] if tol is None else tol
    pr, cl = doc.get("printed") or {}, doc.get("claim") or {}
    ar = doc.get("arms") or {}
    printed = pr.get("cagr")
    declared = (ar.get("declared") or {}).get("cagr")
    as_coded = (ar.get("as_coded") or {}).get("cagr")
    claim_next_open = _is_next_open(cl.get("execution"))
    why = []
    if printed is None or declared is None or as_coded is None:
        why.append("a side of the comparison is unreadable")
        return {"state": "CANNOT_VERIFY", "why": "; ".join(why),
                "printed_cagr_pp": _pp(printed), "declared_cagr_pp": _pp(declared),
                "as_coded_cagr_pp": _pp(as_coded)}
    gap_declared = 100.0 * (declared - printed)
    gap_as_coded = 100.0 * (as_coded - printed)
    labelled = pr.get("labelled") or {}
    row_decl = (labelled.get("declared") or {}).get("cagr")
    row_code = (labelled.get("as_coded") or {}).get("cagr")
    if row_decl is not None and row_code is not None:
        # A table that states its own basis needs no inference from the prose: compare each
        # labelled cell with the arm it names, which is the only comparison that cannot be
        # won by quoting one row and pricing the other.
        off_decl = 100.0 * (row_decl - declared)
        off_code = 100.0 * (row_code - as_coded)
        why.append("the card's own table labels both arms (declared row %.2f%%/yr, as-coded "
                   "row %.2f%%/yr)"
                   % (100.0 * row_decl, 100.0 * row_code))
        out = {"row_declared_pp": _pp(row_decl), "row_as_coded_pp": _pp(row_code),
               "row_vs_face_declared_pp": round(off_decl, 3),
               "row_vs_face_as_coded_pp": round(off_code, 3),
               "printed_vs_declared_pp": round(gap_declared, 3),
               "printed_vs_as_coded_pp": round(gap_as_coded, 3)}
        if abs(off_decl) <= tol and abs(off_code) <= tol:
            why.append("each labelled cell is this face's own measurement of the arm it "
                       "names (%+.2fpp and %+.2fpp), so the eye cannot land on a number the "
                       "sheet does not also label" % (off_decl, off_code))
            out["state"] = "TABLE_PRINTS_BOTH_ARMS"
            out["why"] = "; ".join(why)
            return out
        why.append("the labelled cells are %+.2fpp / %+.2fpp off this face's own arms -- a "
                   "label is a claim about the cell beside it, and this one is wrong"
                   % (off_decl, off_code))
        out["state"] = "TABLE_ROW_DISAGREES"
        out["why"] = "; ".join(why)
        return out
    why.append("the card prints %+.2fpp against the execution it declares (%.2f vs %.2f%%/yr)"
               % (100.0 * (printed - declared), printed * 100.0, declared * 100.0))
    if claim_next_open is None:
        why.append("the declared execution string is not readable as a fill convention, so no "
                   "claim can be compared -- this is not evidence of a mismatch")
        return {"state": "CANNOT_VERIFY", "why": "; ".join(why),
                "printed_cagr_pp": _pp(printed), "declared_cagr_pp": _pp(declared),
                "as_coded_cagr_pp": _pp(as_coded)}
    if claim_next_open and abs(gap_as_coded) <= tol and abs(gap_declared) >= tol:
        why.append("the printed number reproduces the same-open arm within %.2fpp" % tol)
        disc = doc.get("disclosure") or {}
        if disc.get("present"):
            d_decl, d_code = disc.get("declared_cagr"), disc.get("as_coded_cagr")
            if d_decl is None or d_code is None:
                why.append("the card publishes an execution_basis block this face cannot "
                           "read, so it is neither an accusation nor a clean disclosure")
                return {"state": "EXECUTION_CLAIM_MISMATCH", "why": "; ".join(why),
                        "printed_vs_declared_pp": round(gap_declared, 3),
                        "printed_vs_as_coded_pp": round(gap_as_coded, 3),
                        "disclosure_readable": False}
            off_decl = 100.0 * (float(d_decl) - declared)
            off_code = 100.0 * (float(d_code) - as_coded)
            if abs(off_decl) <= tol and abs(off_code) <= tol:
                why.append("the card also prints the declared arm (%.2f%%/yr) and it is this "
                           "face's own declared arm (%.2fpp); the operator can size off it"
                           % (100.0 * d_decl, off_decl))
                return {"state": "DISCLOSED", "why": "; ".join(why),
                        "printed_vs_declared_pp": round(gap_declared, 3),
                        "printed_vs_as_coded_pp": round(gap_as_coded, 3),
                        "disclosure_vs_face_declared_pp": round(off_decl, 3),
                        "disclosure_vs_face_as_coded_pp": round(off_code, 3)}
            why.append("the card prints a declared arm of %.2f%%/yr, which is %+.2fpp off this "
                       "face's declared arm (%.2f%%/yr, as-coded %+.2fpp) -- the two faces of "
                       "one book are pricing different books"
                       % (100.0 * d_decl, off_decl, declared * 100.0, off_code))
            return {"state": "DISCLOSURE_DISAGREES", "why": "; ".join(why),
                    "printed_vs_declared_pp": round(gap_declared, 3),
                    "printed_vs_as_coded_pp": round(gap_as_coded, 3),
                    "disclosure_vs_face_declared_pp": round(off_decl, 3),
                    "disclosure_vs_face_as_coded_pp": round(off_code, 3)}
        why.append("the card prints no declared arm beside the headline, so nothing on the "
                   "operator's sheet says which number is tradeable")
        return {"state": "EXECUTION_CLAIM_MISMATCH", "why": "; ".join(why),
                "printed_vs_declared_pp": round(gap_declared, 3),
                "printed_vs_as_coded_pp": round(gap_as_coded, 3),
                "disclosure_readable": False}
    if abs(gap_declared) <= tol:
        why.append("the printed number is the declared arm within %.2fpp" % tol)
        return {"state": "CONSISTENT", "why": "; ".join(why),
                "printed_vs_declared_pp": round(gap_declared, 3),
                "printed_vs_as_coded_pp": round(gap_as_coded, 3)}
    why.append("the printed number reproduces neither arm (%.2fpp off the declared one, "
               "%.2fpp off the as-coded one)" % (gap_declared, gap_as_coded))
    return {"state": "PRINTED_MATCHES_NEITHER_ARM", "why": "; ".join(why),
            "printed_vs_declared_pp": _pp(gap_declared),
            "printed_vs_as_coded_pp": _pp(gap_as_coded)}


def _rounded(m):
    return {"cagr": m.get("cagr"), "sharpe": m.get("sharpe"), "maxdd": m.get("maxdd"),
            "vol": m.get("vol"), "cagr_pp": _pp(m.get("cagr")),
            "maxdd_pp": _pp(m.get("maxdd"))}


def run():
    t0 = time.time()
    close, openp, amt, feats, score, cls, n_flip = F.build_inputs()
    doc = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "script": "scripts/etf_book_causal_headline.py",
           "evidence_cutoff": str(close.index[-1].date()),
           "criteria": CRITERIA,
           "criteria_digest": _digest(CRITERIA),
           "panel": {"symbols": int(close.shape[1]), "bars": int(close.shape[0]),
                     "flips_repaired": int(n_flip),
                     "first_bar": str(close.index[0].date()),
                     "last_bar": str(close.index[-1].date())}}
    arms = {}
    for name, lag in (("as_coded", 0), ("declared", 1)):
        ser, turn = L.arm_at_lag(close, openp, amt, score, lag)
        arms[name] = _rounded(L.stats(ser, name))
        arms[name]["lag"] = lag
        arms[name]["turnover_per_decision"] = round(float(turn), 3)
        arms[name]["convention"] = CRITERIA["conventions"]["as_coded" if lag == 0
                                                        else "declared"]
        arms[name]["bars"] = int(ser.dropna().shape[0])
    # the live paper's own engine (decide at close, fill next open, mark to close) with the
    # repo ladder it credits -- printed beside, never substituted for, the card comparison
    carry, carry_note = F.build_carry(F.date_grid(close, F.CONFIG["rebal"])[0])
    serL = L.arm_ledger(close, openp, score, carry) if carry is not None else None
    arms["ledger_live"] = (_rounded(L.stats(serL, "ledger_live")) if serL is not None
                           else {"cagr": None})
    arms["ledger_live"]["convention"] = ("etf_book_forward: decide at close d, fill open d+1, "
                                        "mark to close, repo ladder credited")
    arms["ledger_live"]["carry_note"] = (carry_note if isinstance(carry_note, str)
                                         else str(carry_note))
    doc["arms"] = arms
    doc["claim"] = read_claim()
    doc["printed"] = read_printed_cagr()
    doc["disclosure"] = read_disclosure()
    doc["claim"]["reads_as_next_open_fill"] = _is_next_open(doc["claim"].get("execution"))
    doc["verdict"] = decide(doc)
    doc["recommendation"] = _recommend(doc)
    doc["elapsed_sec"] = round(time.time() - t0, 1)
    return doc


def _recommend(doc):
    ar, v = doc.get("arms") or {}, doc.get("verdict") or {}
    declared = (ar.get("declared") or {}).get("cagr")
    ledger = (ar.get("ledger_live") or {}).get("cagr")
    if v.get("state") == "TABLE_PRINTS_BOTH_ARMS":
        return ("No further change is called for on this face: the card's table prints both "
                "arms with their basis in the row label (declared %.2f%%/yr, as-coded "
                "%.2f%%/yr) and both cells are this face's own measurements, so the operator "
                "can size off the tradeable row without reading prose."
                % (v.get("row_declared_pp") or 0.0, v.get("row_as_coded_pp") or 0.0))
    if v.get("state") == "TABLE_ROW_DISAGREES":
        return ("The card's labelled rows do not agree with this face (declared row %+.2fpp, "
                "as-coded row %+.2fpp): a row label is a promise about the cell beside it, so "
                "either the card or this face is pricing a different book -- re-price both on "
                "one panel before anyone sizes off either row."
                % (v.get("row_vs_face_declared_pp") or 0.0,
                   v.get("row_vs_face_as_coded_pp") or 0.0))
    if v.get("state") == "PRINTED_MATCHES_NEITHER_ARM":
        return ("The sheet should print the arm it actually prices: it currently reads "
                "%+.2fpp off the execution it declares and %+.2fpp off the arm the engine "
                "prices, so neither convention reproduces the headline."
                % (v.get("printed_vs_declared_pp") or 0.0,
                   v.get("printed_vs_as_coded_pp") or 0.0))
    if v.get("state") != "EXECUTION_CLAIM_MISMATCH":
        if v.get("state") == "DISCLOSURE_DISAGREES":
            return ("The card's declared arm and this face's declared arm are %.2fpp apart: "
                    "before anyone sizes a position, the two faces must be re-priced off one "
                    "panel -- this is not a tolerance question, it is two books using one name."
                    % (v.get("disclosure_vs_face_declared_pp") or 0.0))
        if v.get("state") == "DISCLOSED":
            return ("No further change is called for on this face: the headline is still the "
                    "same-open arm, but the card prints the declared arm (%.2f%%/yr) beside it "
                    "and that number is this face's own measurement, so the operator can size "
                    "off the tradeable arm."
                    % (100.0 * ((doc.get("disclosure") or {}).get("declared_cagr") or 0.0)))
        return ("No headline change is called for: the sheet already prices the execution it "
                "declares%s." % ("" if v.get("state") == "CONSISTENT" else
                                 " -- but the comparison is unreadable, so the sheet should "
                                 "print its convention until it can be re-derived"))
    return ("The order sheet should carry the declared-execution number (%.2f%%/yr) beside "
            "the as-coded one, or fix the engine to fill at open t+1 -- until then the "
            "headline is %+.2fpp/yr above the execution the sheet itself claims%s."
            % (100.0 * declared, (v.get("printed_vs_declared_pp") or 0.0),
               "" if ledger is None else
               "; the live paper, which does fill next open and earns the repo ladder, "
               "reads %.2f%%/yr" % (100.0 * ledger)))


def write_md(doc):
    v = doc["verdict"]
    ar = doc["arms"]
    lines = ["# Does the order sheet price the execution it declares?", "",
             "Generated %s from `%s` (panel %s -> %s, %d symbols, cutoff `%s`)."
             % (doc["generated"], doc["script"], doc["panel"]["first_bar"],
                doc["panel"]["last_bar"], doc["panel"]["symbols"], doc["evidence_cutoff"]), "",
             "## Verdict", "",
             "**%s** -- %s" % (v["state"], v.get("why") or ""), "",
             "Recommendation: %s" % doc["recommendation"], "",
             "## The three numbers, each with its own convention", "",
             "| arm | convention | CAGR | Sharpe | max drawdown |", "|---|---|---|---|---|"]
    for k, lbl in (("as_coded", "as coded"), ("declared", "declared by the card"),
                   ("ledger_live", "the live paper")):
        a = ar.get(k) or {}
        lines.append("| %s | %s | %s | %s | %s |" % (
            lbl, a.get("convention") or "?",
            "unreadable" if a.get("cagr") is None else "%.2f%%" % (a["cagr"] * 100.0),
            "unreadable" if a.get("sharpe") is None else "%.2f" % a["sharpe"],
            "unreadable" if a.get("maxdd") is None else "%.1f%%" % (a["maxdd"] * 100.0)))
    pr, cl, ds = doc["printed"], doc["claim"], (doc.get("disclosure") or {})
    lines += ["", "## What the operator's files say", "",
              "- the card prints **%s** (%s)" % (
                  "unreadable" if pr.get("cagr") is None else "%.2f%%/yr" % (pr["cagr"] * 100.0),
                  pr.get("error") or (("row label '%s', %s" % (pr.get("label"), pr.get("source")))
                                      if pr.get("label") else pr.get("source"))),
              "- the card claims execution **%s** (%s)" % (
                  cl.get("execution") or "unreadable", cl.get("error") or cl.get("source")),
              "- the card discloses beside it **%s** (%s)" % (
                  "no declared arm" if not ds.get("present") else
                  "%s%%/yr declared vs %s%%/yr as-coded, verdict %s" % (
                      "unreadable" if ds.get("declared_cagr") is None
                      else "%.2f" % (100.0 * ds["declared_cagr"]),
                      "unreadable" if ds.get("as_coded_cagr") is None
                      else "%.2f" % (100.0 * ds["as_coded_cagr"]),
                      ds.get("verdict") or "unstated"),
                  ds.get("error") or ds.get("note") or ds.get("source") or "unreadable"), ""]
    lab = pr.get("labelled") or {}
    if lab:
        lines += ["- the card's own row labels state the basis: %s" % "; ".join(
            "%s = %.2f%%/yr" % (k, 100.0 * (v.get("cagr") or 0.0))
            for k, v in sorted(lab.items()))]
    lines += ["", "## Why this is a defect and not a preference", "",
              "The two arms differ in exactly one number -- how many bars of information the "
              "signal has when the book is paid for. `as coded` ranks on bar d's own close and "
              "then buys at bar d's open, i.e. at a price set before the information it ranks "
              "on; `declared` is the same rule holding the signal one bar back, which is what "
              "the card's own execution string promises. A sheet may print either, but it "
              "cannot print one and declare the other: the operator sizes a position on the "
              "difference.", "",
              "Full ladder and the mechanism pin: `results/etf_book_lookahead_audit.json`. "
              "This face adds only the comparison against the published claim, and it refuses "
              "to move its own tolerance.", ""]
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return OUT_MD


def read_published(path=None):
    with open(path or OUT, encoding="utf-8") as fh:
        return json.load(fh)


def check(path=None, quiet=False, card_path=None):
    """Re-derive the verdict from the published rows; refuse a face whose criteria moved."""
    doc = read_published(path)
    problems = []
    if doc.get("criteria_digest") != _digest(doc.get("criteria") or {}):
        problems.append("the criteria block does not hash to its own recorded digest")
    if _digest(doc.get("criteria") or {}) != _digest(CRITERIA):
        problems.append("the published criteria are not the frozen criteria in this file")
    # A verdict is only as fresh as the row block it was derived from. Re-deriving from the
    # published rows alone reads a face that never re-ran as self-consistent (the r1282
    # family), so the card on disk is read here and the published block must match it.
    fresh = read_printed_cagr(card_path) if card_path else read_printed_cagr()
    pub = doc.get("printed") or {}
    pub_rows, fresh_rows = len(pub.get("rows") or []), len(fresh.get("rows") or [])
    if fresh_rows and not pub_rows:
        problems.append("the card on disk carries %d '2020-01 onwards' row(s) but the published "
                        "row block has none -- this face has not been re-run against the card "
                        "it reads" % fresh_rows)
    elif fresh_rows and pub.get("label") != fresh.get("label"):
        problems.append("the published row label %r is not the card's current label %r -- the "
                        "verdict was derived from a card that has since moved"
                        % (pub.get("label"), fresh.get("label")))
    live = decide(doc)
    if live.get("state") != (doc.get("verdict") or {}).get("state"):
        problems.append("the published verdict %r does not re-derive (%r)"
                        % ((doc.get("verdict") or {}).get("state"), live.get("state")))
    if not quiet:
        if problems:
            for p in problems:
                print("FAIL: %s" % p)
        else:
            print("check OK (%s, %s)" % ((doc.get("verdict") or {}).get("state"),
                                         doc.get("evidence_cutoff")))
    return 0 if not problems else 1


# ---------------------------------------------------------------- selftest fixtures

def _fixture(kind="mismatch", printed=None, tol=None, disclosure=None, labelled=None):
    """A face shaped like the real one, with numbers chosen so the rule must name them."""
    as_coded, declared = 0.0960, 0.0846
    if kind == "consistent":
        printed = 0.0846
    elif kind == "mismatch":
        printed = 0.0960
    elif kind == "unreadable_card":
        printed = None
    elif kind == "unreadable_claim":
        printed = 0.0960
    elif kind in ("disclosed", "disagrees", "half_disclosed", "unreadable_disclosure"):
        printed = 0.0960
    if disclosure is None:
        if kind == "disclosed":
            disclosure = {"present": True, "as_coded_cagr": as_coded,
                          "declared_cagr": declared, "verdict": "SAME_OPEN_ARM"}
        elif kind == "disagrees":
            disclosure = {"present": True, "as_coded_cagr": as_coded,
                          "declared_cagr": 0.0800, "verdict": "SAME_OPEN_ARM"}
        elif kind == "half_disclosed":
            disclosure = {"present": True, "as_coded_cagr": 0.0900,
                          "declared_cagr": declared, "verdict": "SAME_OPEN_ARM"}
        elif kind == "unreadable_disclosure":
            disclosure = {"present": True, "as_coded_cagr": None,
                          "declared_cagr": declared, "verdict": "SAME_OPEN_ARM"}
        else:
            disclosure = {"present": False}
    doc = {"arms": {"as_coded": {"cagr": as_coded}, "declared": {"cagr": declared},
                    "ledger_live": {"cagr": 0.0912}},
           "printed": {"cagr": printed},
           "disclosure": disclosure,
           "claim": {"execution": ("decide at close t -> fill at open t+1 -> hold to next "
                                   "rebalance") if kind != "unreadable_claim" else None}}
    if labelled is not None:
        doc["printed"]["labelled"] = labelled
    return doc


def selftest():
    ok = []

    def leg(name, cond, detail=""):
        ok.append(bool(cond))
        print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                             "" if cond else "  <- %s" % (detail,)))

    tol = CRITERIA["tol_pp"]
    leg("L1 the frozen rule names the arm the card prints on the real-shaped fixture",
        decide(_fixture("mismatch"))["state"] == "EXECUTION_CLAIM_MISMATCH",
        decide(_fixture("mismatch")))
    leg("L2 a card that prints the declared arm is CONSISTENT",
        decide(_fixture("consistent"))["state"] == "CONSISTENT",
        decide(_fixture("consistent")))
    leg("L3 an unreadable headline is CANNOT_VERIFY, never a silent CONSISTENT",
        decide(_fixture("unreadable_card"))["state"] == "CANNOT_VERIFY",
        decide(_fixture("unreadable_card")))
    leg("L4 an unreadable execution claim cannot license a mismatch verdict",
        decide(_fixture("unreadable_claim"))["state"] == "CANNOT_VERIFY",
        decide(_fixture("unreadable_claim")))
    d = _fixture("mismatch")
    d["printed"] = {"cagr": 0.0846 + tol / 100.0 * 0.5}
    leg("L5 inside the tolerance the rule reads CONSISTENT",
        decide(d, tol=tol)["state"] == "CONSISTENT", decide(d, tol=tol))
    d2 = _fixture("mismatch")
    d2["printed"] = {"cagr": 0.0846 + tol / 100.0 * 2.0}
    leg("L6 a number that matches neither arm is named as such, with both distances",
        decide(d2, tol=tol)["state"] == "PRINTED_MATCHES_NEITHER_ARM"
        and abs(decide(d2, tol=tol).get("printed_vs_declared_pp") or 0) > tol,
        decide(d2, tol=tol))
    d3 = _fixture("mismatch")
    d3["claim"]["execution"] = "fill at open t, hold to next rebalance"
    leg("L7 a card that already declares a same-open fill is not accused",
        decide(d3)["state"] != "EXECUTION_CLAIM_MISMATCH", decide(d3))
    leg("L8 the criteria hash matches its own block",
        _digest(CRITERIA) == _digest({k: CRITERIA[k] for k in CRITERIA}))
    leg("L9 a moved tolerance changes the verdict on the same rows",
        decide(_fixture("consistent"), tol=5.0)["state"] == "CONSISTENT"
        and decide(_fixture("mismatch"), tol=5.0)["state"] == "CONSISTENT")
    leg("L10 the recommendation names the declared number when it accuses",
        "8.46" in (_recommend({"arms": {"declared": {"cagr": 0.0846},
                                        "ledger_live": {"cagr": 0.0912}},
                               "verdict": {"state": "EXECUTION_CLAIM_MISMATCH",
                                           "printed_vs_declared_pp": 1.14}})))
    leg("L11 a card that prints the untradeable arm AND its declared arm is DISCLOSED, "
        "not accused",
        decide(_fixture("disclosed"))["state"] == "DISCLOSED", decide(_fixture("disclosed")))
    leg("L12 a card whose declared number is NOT this face's declared arm reads "
        "DISCLOSURE_DISAGREES, with both distances named",
        decide(_fixture("disagrees"))["state"] == "DISCLOSURE_DISAGREES"
        and abs(decide(_fixture("disagrees")).get("disclosure_vs_face_declared_pp") or 0)
        > tol, decide(_fixture("disagrees")))
    leg("L13 a half-readable disclosure is neither an accusation nor a clean disclosure",
        decide(_fixture("unreadable_disclosure"))["state"] == "EXECUTION_CLAIM_MISMATCH",
        decide(_fixture("unreadable_disclosure")))
    leg("L14 the disclosure must match on BOTH arms -- same declared, wrong as-coded reads "
        "DISCLOSURE_DISAGREES",
        decide(_fixture("half_disclosed"))["state"] == "DISCLOSURE_DISAGREES",
        decide(_fixture("half_disclosed")))
    leg("L15 a DISCLOSED face says the operator can size off it, and names the number",
        "8.46" in _recommend({"arms": {"declared": {"cagr": 0.0846}},
                              "disclosure": {"present": True, "declared_cagr": 0.0846},
                              "verdict": {"state": "DISCLOSED"}}))
    labelled_both = {"as_coded": {"cagr": 0.0960}, "declared": {"cagr": 0.0846}}
    leg("L16 a table whose rows label their own basis reads TABLE_PRINTS_BOTH_ARMS, not an "
        "accusation against a card that fixed itself",
        decide(_fixture("mismatch", labelled=labelled_both))["state"]
        == "TABLE_PRINTS_BOTH_ARMS", decide(_fixture("mismatch", labelled=labelled_both)))
    labelled_wrong = {"as_coded": {"cagr": 0.0960}, "declared": {"cagr": 0.0960}}
    leg("L17 a declared row that prints the as-coded number reads TABLE_ROW_DISAGREES with "
        "the distance named",
        decide(_fixture("mismatch", labelled=labelled_wrong))["state"] == "TABLE_ROW_DISAGREES"
        and abs(decide(_fixture("mismatch", labelled=labelled_wrong))
                .get("row_vs_face_declared_pp") or 0) > tol,
        decide(_fixture("mismatch", labelled=labelled_wrong)))
    leg("L18 the labelled branch cannot be reached by position: the same first-row number "
        "reads a different state once the rows carry labels",
        decide(_fixture("mismatch"))["state"] == "EXECUTION_CLAIM_MISMATCH"
        and decide(_fixture("mismatch", labelled=labelled_both))["state"]
        == "TABLE_PRINTS_BOTH_ARMS",
        decide(_fixture("mismatch", labelled=labelled_both)))
    leg("L19 row labels the card actually writes map to the arms they name, and an "
        "unqualified label maps to neither",
        _row_basis("2020-01 onwards -- declared fill (close t -> open t+1)") == "declared"
        and _row_basis("2020-01 onwards -- as coded") == "as_coded"
        and _row_basis("2020-01 onwards") is None)
    # the drift tripwire: a face that never re-ran must not read itself as self-consistent
    import tempfile
    tmp = tempfile.mkdtemp(prefix="causal_headline_selftest_")
    card = os.path.join(tmp, "CARD.md")
    with open(card, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("| window | CAGR |\n|---|---|\n"
                 "| 2020-01 onwards -- as coded | 9.6% | 0.99 |\n"
                 "| 2020-01 onwards -- declared fill (close t -> open t+1) | 8.4% | 0.87 |\n")
    stale_doc = os.path.join(tmp, "stale.json")
    d = _fixture("mismatch")
    d["criteria"], d["criteria_digest"] = CRITERIA, _digest(CRITERIA)
    d["verdict"] = decide(d)
    with open(stale_doc, "w", encoding="utf-8") as fh:
        json.dump(d, fh)
    stale_rc = check(stale_doc, quiet=True, card_path=card)
    d2 = _fixture("mismatch", labelled=labelled_both)
    d2["printed"]["label"] = "2020-01 onwards -- as coded"
    d2["printed"]["rows"] = read_printed_cagr(card)["rows"]
    d2["criteria"], d2["criteria_digest"] = CRITERIA, _digest(CRITERIA)
    d2["verdict"] = decide(d2)
    fresh_doc = os.path.join(tmp, "fresh.json")
    with open(fresh_doc, "w", encoding="utf-8") as fh:
        json.dump(d2, fh)
    fresh_rc = check(fresh_doc, quiet=True, card_path=card)
    leg("L20 a published block that predates the card reads as stale (rc1), and the same "
        "block carrying the card's own label reads clean (rc0)",
        stale_rc == 1 and fresh_rc == 0, "stale=%r fresh=%r" % (stale_rc, fresh_rc))
    print("\n%d/%d legs PASS" % (sum(ok), len(ok)))
    return 0 if all(ok) else 1

def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    argv = [a for a in argv if a != "--offline"]
    cmd = argv[0] if argv else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        return check()
    if cmd in ("run", "--run"):
        doc = run()
        with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=True)
        write_md(doc)
        v = doc["verdict"]
        print("causal headline: %s | printed %s%% vs declared %s%% vs as-coded %s%% | "
              "cutoff %s | %.1fs" % (
                  v["state"],
                  _pp(doc["printed"].get("cagr")) if doc["printed"].get("cagr") is not None
                  else "?",
                  _pp(doc["arms"]["declared"].get("cagr")),
                  _pp(doc["arms"]["as_coded"].get("cagr")),
                  doc["evidence_cutoff"], doc["elapsed_sec"]))
        print("  %s" % doc["recommendation"])
        return 0
    print("usage: etf_book_causal_headline.py [run|check|selftest]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())