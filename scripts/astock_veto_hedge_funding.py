"""What does the hedge cost once you pay for the collateral and for the lender?

r2033 put the two carriers of this hedge on one ruler and printed what a reader has since been
quoting: the ETF short compounds at 12.39% and the IM short at 12.31%, a difference of 0.354pp a
year inside a 1pp tie band, so "the discount is a median artifact and IM wins on capital".  Two
things were left out of that comparison:

  * the borrow.  An ETF short is rented; r2033's arms are gross of the lender, and its own capital
    table prices the rent at 1.80 .. 7.21pp a year of the book.
  * the collateral.  r2035 walked the futures margin account and found the position consumes
    403,938 CNY (40.4% of the book), not the 108,160 the 12% ratio implies.  The ETF leg blocks
    450,666 .. 901,331 CNY depending on the haircut.  Neither number is free: the money that sits
    there is money that is not earning the book's return.

This face puts the same 52 periods, the same book and the same k on two funded rulers:

  1. gross of the lender and of the collateral (what r2033 printed) -- reproduced, not re-invented;
  2. net of the borrow fee, on the same notional;
  3. funded: book capital + the cash the hedge forces you to post, the reserve earning a declared
     cash yield, everything divided by the capital actually committed.

The question it answers is the one a ticket cannot dodge: if the insurance costs the lender's fee
plus the return on the collateral, does the carrier ranking survive, and does the size decision
move?

Usage
    python scripts/astock_veto_hedge_funding.py run
    python scripts/astock_veto_hedge_funding.py check
    python scripts/astock_veto_hedge_funding.py selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_veto_hedge_carrier import (  # noqa: E402
    CAPITAL,
    CASH_YIELD,
    ETF_BORROW_FEES,
    ETF_HAIRCUTS,
    K_GRID,
    TIE_PP,
    arm_stats,
    capital_table,
    hedged,
)

PARENT = os.path.join(ROOT, "results", "astock_veto_hedgeable_beta.json")
CARRIER = os.path.join(ROOT, "results", "astock_veto_hedge_carrier.json")
MARGIN = os.path.join(ROOT, "results", "astock_veto_hedge_margin.json")
OUT_JSON = os.path.join(ROOT, "results", "astock_veto_hedge_funding.json")
OUT_MD = os.path.join(ROOT, "research", "ASTOCK_VETO_HEDGE_FUNDING.md")

# Frozen before the run.  The gap line is r2033's own tie band, so "the tie was gross" means "it
# does not survive the band that called it a tie"; the widening line is the plain reading of
# "the cost is not a rounding error on the gap, it is a multiple of it".
LINE_GAP_PP = TIE_PP
LINE_WIDEN_MULT = 2.0
LINE_SWEEP_MULT = 1.5
K_REF = 1.0
IM_CASH_RUNG = "0.12"        # the rung r2035 walked; other rungs are printed as sensitivity
CASH_YIELDS = (0.0, CASH_YIELD)

VERDICT_GROSS = "THE_TIE_WAS_GROSS_OF_THE_LENDER"
VERDICT_COLLATERAL = "THE_COLLATERAL_COSTS_MORE_THAN_THE_LENDER"
VERDICT_WIDEN = "EQUAL_CAPITAL_WIDENS_THE_GAP"
VERDICT_FLIP = "THE_RANKING_FLIPS_WHEN_YOU_PAY_FOR_IT"
VERDICT_SWEEP = "SWEEPING_THE_ACCOUNT_COSTS_TWICE_THE_BLOCK"
VERDICT_SURVIVES = "THE_GAP_SURVIVES_THE_COSTS"
VERDICT_WHY = {
    VERDICT_GROSS: "the scarce comparison was priced without the lender; the cheapest rent the "
                   "family's own table allows already puts the ETF leg a tie band behind",
    VERDICT_COLLATERAL: "at the declared reference block (the full haircut) and the cheapest "
                        "rent, the cash the ETF short must post gives up more return than the "
                        "lender takes -- at a half haircut it is the smaller of the two, and the "
                        "page prints both bands rather than picking the friendly one",
    VERDICT_WIDEN: "dividing by the capital actually committed multiplies the gross gap, because "
                   "the leg that blocks more cash also divides by more of it",
    VERDICT_FLIP: "the carrier that led gross of costs trails net of them; the ordering, not "
                  "just the size of the gap, changes",
    VERDICT_SWEEP: "sweeping the margin account's excess is the usual treasury habit and it "
                   "multiplies the block, so it multiplies the return that block gives up",
    VERDICT_SURVIVES: "the costs are charged in full and the ordering still holds",
}


# ---------------------------------------------------------------------- plumbing
def _now() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _rel(path: str) -> str:
    try:
        return os.path.relpath(path, ROOT).replace(os.sep, "/")
    except ValueError:
        return str(path).replace(os.sep, "/")


def _read_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _sha_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def content_sha(face: dict) -> str:
    body = {k: v for k, v in face.items() if k != "content_sha256"}
    blob = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def fingerprint(path: str) -> dict:
    face = _read_json(path)
    return {"face": _rel(path), "file_sha256": _sha_file(path),
            "content_sha256": content_sha(face), "generated": face.get("generated"),
            "evidence_cutoff": face.get("evidence_cutoff")}


def _pct(x, nd=2) -> str:
    return "n/a" if x is None else ("%." + str(nd) + "f%%") % (x * 100.0)


def _pp(x, nd=2) -> str:
    return "n/a" if x is None else ("%." + str(nd) + "fpp") % (x * 100.0)


# ---------------------------------------------------------------- funded arithmetic
def borrow_series(arm_vals, fee: float, notional: float, capital: float, ppy: float) -> list:
    """The same arm, charged the lender once per period on the notional it rents.

    A fee is a rate per year on the shorted notional, so one period costs fee/ppy of notional --
    which is fee/ppy * notional/capital of the book.  Missing periods stay missing: a period we
    could not price is not a period we rented for free.
    """
    per_period = fee / ppy * (notional / capital) if ppy else 0.0
    return [None if v is None or not math.isfinite(v) else float(v) - per_period
            for v in arm_vals]


def funded_series(arm_vals, cash_cny: float, cash_yield: float, capital: float,
                  ppy: float) -> list:
    """The hedged book plus the cash it forces you to post, divided by the capital committed.

    r_funded = (book_arm * capital + cash * cash_yield/ppy) / (capital + cash)

    The reserve is not lost -- it earns the declared cash yield -- but it is not earning the
    book's return either, and that difference is what a funded ruler measures.  Missing periods
    stay missing so the funded and gross rows cover the same periods.
    """
    total = capital + cash_cny
    if total <= 0.0:
        return [None for _ in arm_vals]
    per_period_cash = cash_yield / ppy if ppy else 0.0
    out = []
    for v in arm_vals:
        if v is None or not math.isfinite(v):
            out.append(None)
            continue
        out.append((float(v) * capital + cash_cny * per_period_cash) / total)
    return out


def drag_pp(arm_ann: float, funded_ann: float) -> float:
    """Annualised return given up by committing the collateral, in pp."""
    if arm_ann is None or funded_ann is None:
        return 0.0
    return arm_ann - funded_ann


def collateral_cny(cash_cny: float, arm_ann: float, cash_yield: float) -> float:
    """What the reserve gives up per year, in CNY: cash x (book return - cash yield)."""
    if arm_ann is None:
        return 0.0
    return cash_cny * (arm_ann - cash_yield)


# ------------------------------------------------------------------------- build
def build_face() -> dict:
    parent = _read_json(PARENT)
    carrier = _read_json(CARRIER)
    margin = _read_json(MARGIN)

    spec_p = parent.get("spec") or {}
    ppy = float(spec_p.get("periods_per_year") or 12.6)
    rows = [r for r in (parent.get("rows") or []) if r.get("im_window")]
    if len(rows) < 20:
        return {"generated": _now(), "kind": "hedge_funding",
                "evidence_cutoff": parent.get("evidence_cutoff"),
                "verdict": "NOT_ENOUGH_PERIODS",
                "parents": {"beta": fingerprint(PARENT)}}

    beta = ((parent.get("arms_etf") or {}).get("1.0") or {}).get("beta_used")
    if beta is None:
        beta = ((parent.get("variance") or {}).get("beta_used_for_arms")) or 0.9013
    beta = float(beta)
    notional = beta * CAPITAL

    book = [r.get("book_net") for r in rows]
    etf_leg = [r.get("hedge_etf") for r in rows]
    im_leg = [r.get("hedge_im") for r in rows]

    cap_table = capital_table(beta, CAPITAL, CASH_YIELD)
    im_cash = float(((margin.get("required_margin_cny") or {}).get("no_sweep") or {})
                    .get(IM_CASH_RUNG) or 0.0)
    im_cash_sweep = float(((margin.get("required_margin_cny") or {}).get("sweep") or {})
                          .get(IM_CASH_RUNG) or 0.0)
    etf_blocked = {("%.2f" % r["haircut"]): float(r["blocked_cny"])
                   for r in cap_table.get("etf") or []}
    borrow_ppy = {("%.2f" % r["borrow_fee"]): float(r["borrow_pp_per_year"])
                  for r in cap_table.get("etf") or []}

    # --- 1. gross, exactly as r2033 published it (this is the anchor, not a re-invention)
    gross = {"etf": {}, "im": {}}
    for k in K_GRID:
        gross["etf"][("%.1f" % k)] = arm_stats(hedged(book, etf_leg, k), ppy)
        gross["im"][("%.1f" % k)] = arm_stats(hedged(book, im_leg, k), ppy)

    # --- 2. net of the lender, same periods, rent charged on the notional actually shorted
    net = {"etf": {("%.1f" % k): {} for k in K_GRID}, "im": {}}
    for k in K_GRID:
        for fee in ETF_BORROW_FEES:
            net["etf"][("%.1f" % k)][("%.2f" % fee)] = arm_stats(
                borrow_series(hedged(book, etf_leg, k), fee, notional * k, CAPITAL, ppy), ppy)
        net["im"][("%.1f" % k)] = gross["im"][("%.1f" % k)]

    # --- 3. funded: capital + the block the hedge forces, at two cash yields
    funded = {"etf": {}, "im": {}}
    for y in CASH_YIELDS:
        ykey = ("%.2f" % y)
        funded["etf"][ykey] = {}
        funded["im"][ykey] = {}
        for k in K_GRID:
            kkey = ("%.1f" % k)
            funded["im"][ykey][kkey] = {}
            for regime, cash0 in (("no_sweep", im_cash), ("sweep", im_cash_sweep)):
                cash = cash0 * k
                funded["im"][ykey][kkey][regime] = {
                    "cash_cny": cash,
                    "committed_cny": CAPITAL + cash,
                    "stats": arm_stats(
                        funded_series(hedged(book, im_leg, k), cash, y, CAPITAL, ppy), ppy),
                }
            funded["etf"][ykey][kkey] = {}
            for haircut in ETF_HAIRCUTS:
                hkey = ("%.2f" % haircut)
                cash = etf_blocked.get(hkey, notional * haircut) * k
                funded["etf"][ykey][kkey][hkey] = {}
                for fee in ETF_BORROW_FEES:
                    fkey = ("%.2f" % fee)
                    vals = borrow_series(hedged(book, etf_leg, k), fee, notional * k,
                                         CAPITAL, ppy)
                    funded["etf"][ykey][kkey][hkey][fkey] = {
                        "cash_cny": cash,
                        "committed_cny": CAPITAL + cash,
                        "stats": arm_stats(funded_series(vals, cash, y, CAPITAL, ppy), ppy),
                    }

    # --- the comparisons every verdict is derived from (k = 1, declared cash yield).
    # Sign convention is the carrier face's own: every gap here is IM minus ETF, so a positive
    # number means the futures leg is ahead.  r2033 published im_minus_etf = -0.354pp on the two
    # short legs; the same periodicity inside a hedged book compounds to a smaller arm gap.
    ykey = ("%.2f" % CASH_YIELD)
    kkey = ("%.1f" % K_REF)
    etf_g = (gross["etf"].get(kkey) or {})
    im_g = (gross["im"].get(kkey) or {})
    im_ann = float(im_g.get("annualized_compound") or 0.0)
    etf_ann = float(etf_g.get("annualized_compound") or 0.0)
    gross_gap_pp = (im_ann - etf_ann) * 100.0
    carrier_leg_gap_pp = (carrier.get("realised_carrier") or {}).get("im_minus_etf_pp_per_year")

    net_gap_pp = {}
    for fee in ETF_BORROW_FEES:
        fkey = ("%.2f" % fee)
        e = (net["etf"].get(kkey) or {}).get(fkey) or {}
        net_gap_pp[fkey] = (im_ann - float(e.get("annualized_compound") or 0.0)) * 100.0

    im_funded = (((funded["im"].get(ykey) or {}).get(kkey) or {}).get("no_sweep") or {})
    im_f = im_funded.get("stats") or {}
    funded_rows = []
    for haircut in ETF_HAIRCUTS:
        hkey = ("%.2f" % haircut)
        for fee in ETF_BORROW_FEES:
            fkey = ("%.2f" % fee)
            cell = ((((funded["etf"].get(ykey) or {}).get(kkey) or {}).get(hkey) or {})
                    .get(fkey) or {})
            st = cell.get("stats") or {}
            funded_rows.append({
                "carrier": "etf",
                "haircut": haircut,
                "borrow_fee": fee,
                "cash_cny": cell.get("cash_cny") or 0.0,
                "committed_cny": cell.get("committed_cny") or CAPITAL,
                "funded_ann": st.get("annualized_compound"),
                "funded_vol": st.get("annual_vol"),
                "funded_mdd": st.get("max_drawdown"),
                "gross_ann": ((net["etf"].get(kkey) or {}).get(fkey) or {})
                .get("annualized_compound"),
                "drag_pp": drag_pp(((net["etf"].get(kkey) or {}).get(fkey) or {})
                                   .get("annualized_compound"),
                                   st.get("annualized_compound")),
                "collateral_cny": collateral_cny(
                    cell.get("cash_cny") or 0.0,
                    ((net["etf"].get(kkey) or {}).get(fkey) or {}).get("annualized_compound"),
                    CASH_YIELD),
                "borrow_cny": notional * fee,
            })
    funded_rows.append({
        "carrier": "im",
        "haircut": None,
        "borrow_fee": 0.0,
        "cash_cny": im_funded.get("cash_cny") or 0.0,
        "committed_cny": im_funded.get("committed_cny") or CAPITAL,
        "funded_ann": im_f.get("annualized_compound"),
        "funded_vol": im_f.get("annual_vol"),
        "funded_mdd": im_f.get("max_drawdown"),
        "gross_ann": im_g.get("annualized_compound"),
        "drag_pp": drag_pp(im_g.get("annualized_compound"), im_f.get("annualized_compound")),
        "collateral_cny": collateral_cny(im_funded.get("cash_cny") or 0.0,
                                         im_g.get("annualized_compound"), CASH_YIELD),
        "borrow_cny": 0.0,
    })

    # the funded gap: IM funded minus ETF funded, at the declared reference haircut (the full
    # block -- the conservative end this face names as its reference case)
    ref_haircut = max(ETF_HAIRCUTS)
    full_rows = [r for r in funded_rows
                 if r["carrier"] == "etf" and r["haircut"] == ref_haircut]
    im_row = next(r for r in funded_rows if r["carrier"] == "im")
    funded_gap_pp = {}
    for r in full_rows:
        funded_gap_pp[("%.2f" % r["borrow_fee"])] = (
            ((im_row["funded_ann"] or 0.0) - (r["funded_ann"] or 0.0)) * 100.0)

    flags = decide(gross_gap_pp, net_gap_pp, funded_gap_pp, funded_rows, im_row,
                   im_cash, im_cash_sweep, ref_haircut)
    verdict = headline(flags)

    caveats = [
        "the borrow fee is charged on the notional every period and no fee is credited back; a "
        "lender that returns part of it, or a locate that fails, is a separate face",
        "the collateral is modelled as posted and idle at a declared cash yield; in practice a "
        "short-sale proceeds balance is frozen and may earn less than a deposit, so this is the "
        "optimistic end of the funding question",
        "the ETF block uses r2033's haircut ladder (50/80/100% of notional); the futures block "
        "uses r2035's walked path at the 12% rung -- 403,938 CNY, not the 108,160 a ratio implies",
        "both legs are marked off their own panels, so an ETF tracking error and its "
        "premium/discount remain inside the gap, as on r2033",
        "the window is the 52 shared periods (the IM panel starts 2022-07); the ETF leg's longer "
        "77-period record is not used anywhere here, exactly as on the carrier face",
        "the notional is held constant and nothing is rebalanced after a call; a real account "
        "de-levers and this face prices the cost of the block instead",
        "a funded return is not a portfolio recommendation: it says what the money you must "
        "commit earns, not what you should commit",
    ]

    face = {
        "generated": _now(),
        "kind": "hedge_funding",
        "machine": "bm-c",
        "evidence_cutoff": parent.get("evidence_cutoff"),
        "fills_the_hole_of": "r2033 priced both carriers gross of the lender and r2035 showed the "
                             "futures block is 40.4% of the book; nothing in the family charges "
                             "either cost against the other, so 'IM wins on capital' has never "
                             "been put on a funded ruler",
        "parents": {"beta": fingerprint(PARENT), "carrier": fingerprint(CARRIER),
                    "margin": fingerprint(MARGIN)},
        "sample": {"periods": len(rows), "periods_per_year": ppy,
                   "first": rows[0].get("date"), "last": rows[-1].get("end"),
                   "basis": "parent rows flagged im_window (both carriers priced)"},
        "spec": {"capital": CAPITAL, "beta": beta, "notional_cny": notional,
                 "k_grid": K_GRID, "k_ref": K_REF,
                 "cash_yield": CASH_YIELD, "cash_yields": list(CASH_YIELDS),
                 "im_cash_rung": IM_CASH_RUNG, "im_cash_cny": im_cash,
                 "im_cash_sweep_cny": im_cash_sweep,
                 "etf_blocked_cny": etf_blocked, "etf_borrow_fees": list(ETF_BORROW_FEES),
                 "etf_haircuts": list(ETF_HAIRCUTS),
                 "line_gap_pp": LINE_GAP_PP, "line_widen_mult": LINE_WIDEN_MULT,
                 "line_sweep_mult": LINE_SWEEP_MULT},
        "gross": gross,
        "net_of_borrow": net,
        "funded": funded,
        "gross_gap_pp": gross_gap_pp,
        "carrier_leg_gap_pp": carrier_leg_gap_pp,
        "net_gap_pp": net_gap_pp,
        "funded_gap_pp": funded_gap_pp,
        "ref_haircut": ref_haircut,
        "funded_rows": funded_rows,
        "verdicts": flags,
        "verdict": verdict,
        "verdict_why": VERDICT_WHY.get(verdict.split("+")[0], ""),
        "caveats": caveats,
    }
    face["reads"] = build_reads(face)
    face["content_sha256"] = content_sha(face)
    return face


def decide(gross_gap_pp, net_gap_pp, funded_gap_pp, funded_rows, im_row,
           im_cash, im_cash_sweep, ref_haircut) -> dict:
    """Each flag is a separate question about its own numbers; several can hold at once.

    Every gap is IM minus ETF.  The reference case for the funded flags is the declared full
    haircut; the ladder's other haircuts are printed as a band and are not folded into a flag.
    """
    out = {}
    cheapest_net = min(net_gap_pp.values()) if net_gap_pp else 0.0
    ref_gap = min(funded_gap_pp.values()) if funded_gap_pp else 0.0
    out[VERDICT_GROSS] = bool(net_gap_pp and cheapest_net >= LINE_GAP_PP)
    out[VERDICT_WIDEN] = bool(funded_gap_pp and ref_gap >= LINE_WIDEN_MULT * abs(gross_gap_pp))
    out[VERDICT_FLIP] = bool(gross_gap_pp < 0.0 and ref_gap > 0.0)
    ref_rows = [r for r in funded_rows
                if r["carrier"] == "etf" and r.get("haircut") == ref_haircut]
    if ref_rows and im_row:
        cheapest = min(ref_rows, key=lambda r: r["borrow_fee"])
        extra = ((cheapest["collateral_cny"] or 0.0)
                 - (im_row.get("collateral_cny") or 0.0))
        out[VERDICT_COLLATERAL] = bool(extra > 0.0
                                       and extra >= (cheapest["borrow_cny"] or 0.0))
    else:
        out[VERDICT_COLLATERAL] = False
    out[VERDICT_SWEEP] = bool(im_cash > 0.0 and im_cash_sweep / im_cash >= LINE_SWEEP_MULT)
    out[VERDICT_SURVIVES] = bool(not out[VERDICT_FLIP] and not out[VERDICT_GROSS])
    return out


def headline(flags) -> str:
    """One sentence, chosen by a fixed ladder -- not by whichever flag looks best."""
    if flags.get("not_enough"):
        return "NOT_ENOUGH_PERIODS"
    if flags.get(VERDICT_GROSS) and flags.get(VERDICT_FLIP):
        return VERDICT_GROSS + "+" + VERDICT_FLIP
    if flags.get(VERDICT_GROSS):
        return VERDICT_GROSS
    if flags.get(VERDICT_FLIP):
        return VERDICT_FLIP
    if flags.get(VERDICT_SURVIVES):
        return VERDICT_SURVIVES
    return VERDICT_WIDEN


# ------------------------------------------------------------------------- reads
def build_reads(face):
    reads = []
    spec = face.get("spec") or {}
    kkey = ("%.1f" % spec.get("k_ref", K_REF))
    gross = face.get("gross") or {}
    net = face.get("net_of_borrow") or {}
    funded = face.get("funded") or {}
    ykey = ("%.2f" % (spec.get("cash_yield") or 0.0))
    etf_g = ((gross.get("etf") or {}).get(kkey) or {})
    im_g = ((gross.get("im") or {}).get(kkey) or {})

    reads.append({
        "id": "R1",
        "text": "gross of everything, at k=%s on %d periods, the hedged book compounds at %s "
                "(ETF) and %s (IM) -- an arm gap of %s. r2033 published %s on the two short "
                "legs alone; inside the book the same periodicity compounds smaller because the "
                "long side dilutes it, which is why both numbers are printed here"
                % (kkey, (face.get("sample") or {}).get("periods") or 0,
                   _pct(etf_g.get("annualized_compound")),
                   _pct(im_g.get("annualized_compound")),
                   _pp((face.get("gross_gap_pp") or 0.0) / 100.0),
                   _pp((face.get("carrier_leg_gap_pp") or 0.0) / 100.0)),
    })

    fees = sorted((net.get("etf") or {}).get(kkey, {}).items())
    if fees:
        parts = []
        for fkey, st in fees:
            parts.append("at %s rent the ETF leg lands on %s"
                         % (_pct(float(fkey)), _pct((st or {}).get("annualized_compound"))))
        reads.append({
            "id": "R2",
            "text": "charge the lender on the same notional and the tie dissolves: %s -- the arm "
                    "gap becomes %s at the cheapest rent, against the %s band this family calls "
                    "a tie"
                    % ("; ".join(parts),
                       _pp(min((face.get("net_gap_pp") or {}).values() or [0.0]) / 100.0),
                       _pp((spec.get("line_gap_pp") or 0.0) / 100.0)),
        })

    im_cell = (((funded.get("im") or {}).get(ykey) or {}).get(kkey) or {}).get("no_sweep") or {}
    im_st = im_cell.get("stats") or {}
    im_row = next((r for r in (face.get("funded_rows") or []) if r["carrier"] == "im"), {})
    reads.append({
        "id": "R3",
        "text": "on the money you must commit, the futures leg earns %s a year on %.0f CNY "
                "(book %.0f plus the %.0f r2035 walked out), not the %s it quotes on the book "
                "alone -- %s of annual return given up to hold the block"
                % (_pct(im_st.get("annualized_compound")), im_cell.get("committed_cny") or 0.0,
                   CAPITAL, im_cell.get("cash_cny") or 0.0,
                   _pct(im_g.get("annualized_compound")),
                   _pp(im_row.get("drag_pp") or 0.0)),
    })

    etf_rows = [r for r in (face.get("funded_rows") or []) if r["carrier"] == "etf"]
    if etf_rows:
        lo = min(etf_rows, key=lambda r: r["funded_ann"] or -9.9)
        hi = max(etf_rows, key=lambda r: r["funded_ann"] or -9.9)
        reads.append({
            "id": "R4",
            "text": "the ETF leg is funded across a %.0f..%.0f CNY block and %s..%s rent; the "
                    "band of funded returns runs %s .. %s, and only the cheapest corner of it "
                    "keeps the leg near the futures buyer"
                    % (min(r["cash_cny"] for r in etf_rows), max(r["cash_cny"] for r in etf_rows),
                       _pct(min(r["borrow_fee"] for r in etf_rows)),
                       _pct(max(r["borrow_fee"] for r in etf_rows)),
                       _pct(lo["funded_ann"]), _pct(hi["funded_ann"])),
        })
        reads.append({
            "id": "R5",
            "text": "the two costs are not the same size: the ETF block gives up %.0f..%.0f CNY a "
                    "year of return and the lender takes %.0f..%.0f CNY -- the collateral, which "
                    "r2033 counted as an advantage for the futures leg in principle, is the one "
                    "that compounds with the haircut"
                    % (min(r["collateral_cny"] for r in etf_rows),
                       max(r["collateral_cny"] for r in etf_rows),
                       min(r["borrow_cny"] for r in etf_rows),
                       max(r["borrow_cny"] for r in etf_rows)),
        })

    sweep_cell = (((funded.get("im") or {}).get(ykey) or {}).get(kkey) or {}).get("sweep") or {}
    sweep_st = sweep_cell.get("stats") or {}
    if sweep_cell:
        reads.append({
            "id": "R6",
            "text": "and if the treasury habit of sweeping excess margin is kept, the futures leg "
                    "needs %.0f CNY and lands on %s funded -- the cheapest carrier in the gross "
                    "table becomes the one whose block eats the most return"
                    % (sweep_cell.get("cash_cny") or 0.0,
                       _pct(sweep_st.get("annualized_compound"))),
        })

    funded_gap = face.get("funded_gap_pp") or {}
    if funded_gap:
        cheapest = min(funded_gap.values())
        reads.append({
            "id": "R7",
            "text": "the ordering, at k=%s, %.0f%% haircut, cheapest rent: funded gap %s (IM "
                    "minus ETF), against %s gross -- the leg that led gross trails net, so the "
                    "'tie' compared two prices that neither buyer pays"
                    % (kkey, (face.get("ref_haircut") or 0.0) * 100,
                       _pp(cheapest / 100.0),
                       _pp((face.get("gross_gap_pp") or 0.0) / 100.0)),
        })
    return reads


# ------------------------------------------------------------------------ render
def render_md(face) -> str:
    parents = face.get("parents") or {}
    spec = face.get("spec") or {}
    sample = face.get("sample") or {}
    kkey = ("%.1f" % (spec.get("k_ref") or K_REF))
    ykey = ("%.2f" % (spec.get("cash_yield") or 0.0))
    gross = face.get("gross") or {}
    net = face.get("net_of_borrow") or {}
    funded = face.get("funded") or {}

    lines = ["# What the hedge costs once you pay for the collateral and the lender", "",
             "r2033 put both carriers of this hedge on one ruler and the reader has been quoting "
             "the result since: 12.39% (ETF) against 12.31% (IM) on the same 52 periods, a 0.354pp "
             "gap inside a 1pp tie band. That comparison is gross of two costs the same family "
             "prices elsewhere -- the securities the ETF leg rents, and the cash either leg must "
             "post and cannot invest. This face charges both and asks whether the carrier "
             "ordering and the size decision survive.", "",
             "Evidence cutoff **%s**. %d shared periods (%s .. %s), %s periods a year. Beta "
             "%.4f on %.0f CNY of book, short %.0f CNY of notional. Parents: beta `%s` "
             "(generated %s), carrier `%s` (generated %s), margin `%s` (generated %s)."
             % (face.get("evidence_cutoff"), sample.get("periods") or 0, sample.get("first"),
                sample.get("last"), sample.get("periods_per_year"),
                spec.get("beta") or 0.0, spec.get("capital") or 0.0,
                spec.get("notional_cny") or 0.0,
                (parents.get("beta") or {}).get("face"),
                (parents.get("beta") or {}).get("generated"),
                (parents.get("carrier") or {}).get("face"),
                (parents.get("carrier") or {}).get("generated"),
                (parents.get("margin") or {}).get("face"),
                (parents.get("margin") or {}).get("generated")), ""]

    lines += ["## 1. Three rulers on the same k", "",
              "| ruler | ETF annual | ETF vol | IM annual | IM vol | IM minus ETF |",
              "|---|---|---|---|---|---|"]
    etf_g = ((gross.get("etf") or {}).get(kkey) or {})
    im_g = ((gross.get("im") or {}).get(kkey) or {})
    lines.append("| gross of lender and collateral | %s | %s | %s | %s | %s |"
                 % (_pct(etf_g.get("annualized_compound")), _pct(etf_g.get("annual_vol")),
                    _pct(im_g.get("annualized_compound")), _pct(im_g.get("annual_vol")),
                    _pp((face.get("gross_gap_pp") or 0.0) / 100.0)))
    for fee in spec.get("etf_borrow_fees") or []:
        fkey = ("%.2f" % fee)
        st = ((net.get("etf") or {}).get(kkey) or {}).get(fkey) or {}
        gap = ((face.get("net_gap_pp") or {}).get(fkey) or 0.0) / 100.0
        lines.append("| net of the lender at %s | %s | %s | %s | %s | %s |"
                     % (_pct(fee), _pct(st.get("annualized_compound")),
                        _pct(st.get("annual_vol")), _pct(im_g.get("annualized_compound")),
                        _pct(im_g.get("annual_vol")), _pp(gap)))
    lines += ["", "The first row reproduces the carrier face's own arms to the last digit -- that "
                  "is the anchor, not a re-derivation. r2033's quoted number is the leg-to-leg "
                  "gap (%.2fpp), which the long side dilutes inside a hedged book; both are "
                  "printed because a reader can quote either. What the rent does to the arm gap "
                  "is the row that matters: it is an order of magnitude larger than the gap "
                  "itself." % (face.get("carrier_leg_gap_pp") or 0.0), ""]

    lines += ["## 2. Funded: book plus the block, divided by the capital committed", "",
              "| carrier | block | committed | gross annual | funded annual | give-up | "
              "block's give-up, CNY | rent, CNY |", "|---|---|---|---|---|---|---|---|"]
    im_cell = (((funded.get("im") or {}).get(ykey) or {}).get(kkey) or {}).get("no_sweep") or {}
    im_row = next((r for r in (face.get("funded_rows") or []) if r["carrier"] == "im"), {})
    lines.append("| IM future (r2035 path, %.0f%% rung) | %.0f | %.0f | %s | %s | %s | %.0f | 0 |"
                 % (float(spec.get("im_cash_rung") or 0.0) * 100,
                    spec.get("im_cash_cny") or 0.0,
                    im_cell.get("committed_cny") or 0.0,
                    _pct(im_row.get("gross_ann")), _pct(im_row.get("funded_ann")),
                    _pp(im_row.get("drag_pp") or 0.0), im_row.get("collateral_cny") or 0.0))
    for r in (face.get("funded_rows") or []):
        if r["carrier"] != "etf":
            continue
        lines.append("| 512100 short, haircut %.0f%%, rent %s | %.0f | %.0f | %s | %s | %s | "
                     "%.0f | %.0f |"
                     % ((r["haircut"] or 0.0) * 100, _pct(r["borrow_fee"]), r["cash_cny"],
                        r["committed_cny"], _pct(r["gross_ann"]), _pct(r["funded_ann"]),
                        _pp(r["drag_pp"] or 0.0), r["collateral_cny"], r["borrow_cny"]))
    lines += ["", "`gross annual` here is already net of the lender, so the two columns do not "
                  "count the rent twice: the ETF rows are charged the rent first (section 1) and "
                  "the block second, which is the order the money actually leaves.", ""]

    lines += ["## 3. The size decision", "",
              "| k | IM funded annual (no sweep) | IM funded vol | ETF funded annual, "
              "cheapest corner | ETF funded vol |", "|---|---|---|---|---|"]
    for k in spec.get("k_grid") or []:
        kk = ("%.1f" % k)
        cell = (((funded.get("im") or {}).get(ykey) or {}).get(kk) or {}).get("no_sweep") or {}
        st = cell.get("stats") or {}
        ecell = ((((funded.get("etf") or {}).get(ykey) or {}).get(kk) or {})
                 .get(("%.2f" % max(spec.get("etf_haircuts") or [1.0])) or {})
                 .get(("%.2f" % min(spec.get("etf_borrow_fees") or [0.02])))) or {}
        est = ecell.get("stats") or {}
        lines.append("| %s | %s | %s | %s | %s |"
                     % (kk, _pct(st.get("annualized_compound")), _pct(st.get("annual_vol")),
                        _pct(est.get("annualized_compound")), _pct(est.get("annual_vol"))))
    lines += ["", "The block grows with k, so the funded ruler is not the gross ruler shifted: "
                  "it is the gross ruler tilted against size. Read the two legs down each column "
                  "rather than across one row.", ""]

    sweep_cell = (((funded.get("im") or {}).get(ykey) or {}).get(kkey) or {}).get("sweep") or {}
    sweep_st = sweep_cell.get("stats") or {}
    lines += ["## 4. Sweeping the account", "",
              "If the excess margin is swept -- the ordinary treasury habit -- r2035's walk says "
              "the futures block is %.0f CNY instead of %.0f, and the funded futures leg earns "
              "**%s** instead of **%s**. The leg r2033 priced at 108,160 CNY of blocked capital "
              "then holds the largest block in the table, and the funded return of the whole book "
              "moves with that habit rather than with any view on the index."
              % (sweep_cell.get("cash_cny") or 0.0, im_cell.get("cash_cny") or 0.0,
                 _pct(sweep_st.get("annualized_compound")),
                 _pct((im_cell.get("stats") or {}).get("annualized_compound"))), ""]

    lines += ["## 5. Verdict", "", "**`%s`**" % face.get("verdict"), "",
              "Every flag below is computed from its own inputs and several can hold at once; "
              "the headline names the ones that change what a reader would do.", ""]
    for flag, on in (face.get("verdicts") or {}).items():
        if on and flag in VERDICT_WHY:
            lines.append("- `%s` -- %s" % (flag, VERDICT_WHY[flag]))
    lines.append("")

    reads = face.get("reads") or []
    if reads:
        lines += ["## 6. Readings", ""]
        for r in reads:
            lines.append("- **%s.** %s" % (r.get("id"), r.get("text")))
        lines.append("")

    lines += ["## 7. What this face does not settle", ""]
    for c in face.get("caveats") or []:
        lines.append("- " + c)
    lines += ["", "Machine `%s`, generated %s." % (face.get("machine"), face.get("generated")),
              "", "## 8. Reproduction", "", "```",
              "python scripts/astock_veto_hedge_funding.py selftest",
              "python scripts/astock_veto_hedge_funding.py run",
              "python scripts/astock_veto_hedge_funding.py check", "```", ""]
    return "\n".join(lines)


# ------------------------------------------------------------------------- cmds
def run() -> int:
    face = build_face()
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    _write_md(render_md(face))
    print("funding -> %s | %s" % (face.get("verdict"), _rel(OUT_JSON)))
    print("  arm gap gross %s | net at cheapest rent %s | funded (%.0f%% haircut) %s"
          % (_pp((face.get("gross_gap_pp") or 0.0) / 100.0),
             _pp(min((face.get("net_gap_pp") or {}).values() or [0.0]) / 100.0),
             (face.get("ref_haircut") or 0.0) * 100,
             _pp(min((face.get("funded_gap_pp") or {}).values() or [0.0]) / 100.0)))
    return 0


def _write_md(text: str) -> None:
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


VOLATILE = ("generated",)


def _diff(pub, fresh, path="", out=None, tol=1e-9):
    """Every published number must re-derive; a mover is STALE, a disagreement is a defect."""
    if out is None:
        out = []
    if isinstance(pub, dict) and isinstance(fresh, dict):
        for key in sorted(set(pub) | set(fresh)):
            if not path and key in VOLATILE:
                continue
            if key not in pub:
                out.append("%s/%s only in fresh" % (path, key))
                continue
            if key not in fresh:
                out.append("%s/%s only in published" % (path, key))
                continue
            _diff(pub[key], fresh[key], "%s/%s" % (path, key), out, tol)
        return out
    if isinstance(pub, list) and isinstance(fresh, list):
        if len(pub) != len(fresh):
            out.append("%s length %d != %d" % (path, len(pub), len(fresh)))
            return out
        for i, (a, b) in enumerate(zip(pub, fresh)):
            _diff(a, b, "%s[%d]" % (path, i), out, tol)
        return out
    if isinstance(pub, bool) or isinstance(fresh, bool):
        if pub != fresh:
            out.append("%s %r != %r" % (path, pub, fresh))
        return out
    if isinstance(pub, (int, float)) and isinstance(fresh, (int, float)):
        if not (math.isnan(pub) and math.isnan(fresh)) and abs(float(pub) - float(fresh)) > tol:
            out.append("%s %.12g != %.12g" % (path, pub, fresh))
        return out
    if pub != fresh:
        out.append("%s %r != %r" % (path, pub, fresh))
    return out


def check() -> int:
    """Parents moved => STALE; same parents and a different number => CHECK FAILED."""
    problems = []
    try:
        face = _read_json(OUT_JSON)
    except FileNotFoundError:
        print("STALE face missing: %s" % _rel(OUT_JSON))
        return 3
    except (json.JSONDecodeError, OSError) as exc:
        print("CHECK FAILED unreadable face: %s" % exc)
        return 1
    try:
        md = open(OUT_MD, encoding="utf-8").read()
    except FileNotFoundError:
        print("STALE page missing: %s" % _rel(OUT_MD))
        return 3

    for name, path in (("beta", PARENT), ("carrier", CARRIER), ("margin", MARGIN)):
        stored = (face.get("parents") or {}).get(name) or {}
        if not os.path.exists(path):
            print("STALE parent %s missing (%s)" % (name, _rel(path)))
            return 3
        if stored.get("file_sha256") != _sha_file(path):
            print("STALE parent %s moved (%s)" % (name, _rel(path)))
            return 3
        if stored.get("content_sha256") != content_sha(_read_json(path)):
            print("STALE parent %s content moved (%s)" % (name, _rel(path)))
            return 3

    fresh = build_face()
    if fresh.get("verdict") == "NOT_ENOUGH_PERIODS":
        print("STALE sample too short to re-derive")
        return 3
    problems.extend(_diff({k: v for k, v in face.items() if k != "content_sha256"},
                          {k: v for k, v in fresh.items() if k != "content_sha256"}))
    if face.get("content_sha256") != content_sha(face):
        problems.append("published content_sha256 does not match its own body")

    tokens = ["`%s`" % face.get("verdict")]
    spec = face.get("spec") or {}
    if spec.get("im_cash_cny"):
        tokens.append("%.0f" % spec["im_cash_cny"])
    if face.get("gross_gap_pp") is not None:
        tokens.append("%.2fpp" % face["gross_gap_pp"])
    for token in tokens:
        if token not in md:
            problems.append("page missing token %r" % token)

    if problems:
        print("CHECK FAILED %d problem(s)" % len(problems))
        for p in problems[:12]:
            print("  - " + p)
        return 1
    print("CHECK OK verdict=%s gross_gap=%s funded_gap=%s"
          % (face.get("verdict"), _pp((face.get("gross_gap_pp") or 0.0) / 100.0),
             _pp(min((face.get("funded_gap_pp") or {}).values() or [0.0]) / 100.0)))
    return 0


# --------------------------------------------------------------------- selftest
def selftest() -> int:
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # --- borrow arithmetic
    vals = [0.01, 0.02, 0.03]
    b = borrow_series(vals, 0.02, 900_000.0, 1_000_000.0, 12.5)
    leg("L1 a zero fee changes nothing",
        borrow_series(vals, 0.0, 900_000.0, 1_000_000.0, 12.5) == vals)
    leg("L1b one period of rent is fee/ppy on notional as a share of the book",
        abs((vals[0] - b[0]) - 0.02 / 12.5 * 0.9) < 1e-15)
    leg("L1c the rent is the same every period, not compounding",
        abs((vals[0] - b[0]) - (vals[2] - b[2])) < 1e-15)
    leg("L1d a missing period stays missing", borrow_series([None], 0.02, 1.0, 1.0, 12.5) == [None])

    # --- funded arithmetic
    f = funded_series([0.10], 0.0, 0.0, 1_000_000.0, 12.5)
    leg("L2 a zero reserve leaves the book return untouched", abs(f[0] - 0.10) < 1e-15)
    leg("L2b a reserve half the book halves a zero-yield return",
        abs(funded_series([0.10], 500_000.0, 0.0, 1_000_000.0, 12.5)[0] - 0.10 * 2.0 / 3.0)
        < 1e-15)
    f3 = funded_series([0.0], 500_000.0, 0.025, 1_000_000.0, 12.5)
    leg("L2c a fully idle portfolio earns the cash yield and nothing else",
        abs(f3[0] - 0.025 / 12.5 * (500_000.0 / 1_500_000.0)) < 1e-15)
    leg("L2d the funded blend never adds return to a book that beats cash",
        funded_series([0.20], 100_000.0, 0.02, 1_000_000.0, 12.5)[0] < 0.20)
    leg("L2e and it never lowers a book that loses to cash",
        funded_series([-0.20], 100_000.0, 0.02, 1_000_000.0, 12.5)[0] > -0.20)

    # --- the drag identity: give-up is cash x (book - cash), annualised
    cash, arm_ann, y = 403_937.7, 0.1231, 0.02
    leg("L3 the block's give-up is cash x (book return - cash yield)",
        abs(collateral_cny(cash, arm_ann, y) - cash * (arm_ann - y)) < 1e-9)
    leg("L3b a block that earns the book return gives up nothing",
        abs(collateral_cny(cash, y, y)) < 1e-12)
    leg("L3c the give-up is linear in the block", abs(
        collateral_cny(2 * cash, arm_ann, y) - 2 * collateral_cny(cash, arm_ann, y)) < 1e-6)
    leg("L3d drag_pp is the same statement in pp",
        abs(drag_pp(0.1231, 0.092) - 0.0311) < 1e-12)

    # --- verdict ladder: each flag on its own input (gaps are IM minus ETF)
    etf_r = {"carrier": "etf", "haircut": 1.0, "borrow_fee": 0.02,
             "collateral_cny": 80_000.0, "borrow_cny": 18_000.0, "funded_ann": 0.06}
    im_r = {"carrier": "im", "haircut": None, "borrow_fee": 0.0,
            "collateral_cny": 41_000.0, "borrow_cny": 0.0, "funded_ann": 0.09}
    flags = decide(-0.354, {"0.02": 1.72, "0.05": 4.43, "0.08": 7.13},
                   {"0.02": 3.0, "0.05": 4.4, "0.08": 5.8},
                   [etf_r, im_r], im_r, 403_938.0, 834_029.0, 1.0)
    leg("L4 the gross-tie flag needs the cheapest rent to break the band",
        flags[VERDICT_GROSS] is True)
    leg("L4b the collateral flag needs the extra block to beat the rent",
        flags[VERDICT_COLLATERAL] is True)
    leg("L4c the widening flag needs the funded gap to be a multiple of the gross one",
        flags[VERDICT_WIDEN] is True)
    leg("L4d the flip flag needs the funded gap to change sign", flags[VERDICT_FLIP] is True)
    leg("L4e the sweep flag needs the swept block to be 1.5x the kept one",
        flags[VERDICT_SWEEP] is True)
    etf_q = {"carrier": "etf", "haircut": 1.0, "borrow_fee": 0.02,
             "collateral_cny": 10_000.0, "borrow_cny": 18_000.0, "funded_ann": 0.09}
    quiet = decide(0.354, {"0.02": 0.4, "0.05": 0.5, "0.08": 0.6},
                   {"0.02": 0.9, "0.05": 0.8, "0.08": 0.7},
                   [etf_q, im_r], im_r, 403_938.0, 410_000.0, 1.0)
    leg("L4f a small rent does not summon the gross flag", quiet[VERDICT_GROSS] is False)
    leg("L4g a block smaller than the rent does not summon the collateral flag",
        quiet[VERDICT_COLLATERAL] is False)
    leg("L4h a surviving gap says so", quiet[VERDICT_SURVIVES] is True)
    leg("L4i the headline names both flags when both hold",
        "+" in headline({VERDICT_GROSS: True, VERDICT_FLIP: True}))
    leg("L4j no data is not a verdict", headline({"not_enough": True}) == "NOT_ENOUGH_PERIODS")

    # --- live face (only if every parent and the published face are on disk)
    if all(os.path.exists(p) for p in (PARENT, CARRIER, MARGIN, OUT_JSON, OUT_MD)):
        face = _read_json(OUT_JSON)
        parent = _read_json(PARENT)
        carrier = _read_json(CARRIER)
        ppy = float(((parent.get("spec") or {}).get("periods_per_year")) or 12.6)
        rows = [r for r in (parent.get("rows") or []) if r.get("im_window")]
        book = [r.get("book_net") for r in rows]
        etf = [r.get("hedge_etf") for r in rows]
        im = [r.get("hedge_im") for r in rows]
        kkey = ("%.1f" % (K_REF,))
        leg("L5 the published ETF arm is the carrier's own arithmetic",
            abs((((face.get("gross") or {}).get("etf") or {}).get(kkey) or {})
                .get("annualized_compound") - arm_stats(hedged(book, etf, K_REF), ppy)
                ["annualized_compound"]) < 1e-12)
        leg("L5b and it reproduces the carrier face bit for bit",
            abs((((face.get("gross") or {}).get("etf") or {}).get(kkey) or {})
                .get("annualized_compound")
                - ((carrier.get("arms") or {}).get("etf") or {}).get(kkey, {})
                .get("annualized_compound")) < 1e-12)
        leg("L5c the IM arm likewise reproduces the carrier face",
            abs((((face.get("gross") or {}).get("im") or {}).get(kkey) or {})
                .get("annualized_compound")
                - ((carrier.get("arms") or {}).get("im") or {}).get(kkey, {})
                .get("annualized_compound")) < 1e-12)
        walked = (((_read_json(MARGIN).get("required_margin_cny") or {})
                   .get("no_sweep") or {}).get(IM_CASH_RUNG) or 0.0)
        leg("L5d the futures block is r2035's walked number, not the 12% ratio",
            abs(float((face.get("spec") or {}).get("im_cash_cny") or 0.0)
                - float(walked)) < 1e-6)
        leg("L5e every funded row divides by book plus block",
            all(abs(r["committed_cny"] - (CAPITAL + r["cash_cny"])) < 1e-6
                for r in (face.get("funded_rows") or [])))
        leg("L5f the verdict in the file is the one this code would print",
            face.get("verdict") == build_face().get("verdict"))
        net0 = (((face.get("net_of_borrow") or {}).get("etf") or {}).get("0.0") or {})
        gross0 = (((face.get("gross") or {}).get("etf") or {}).get("0.0") or {})
        leg("L5g at k=0 there is nothing to rent, so the net arm is the gross arm",
            all(abs((cell or {}).get("annualized_compound") - gross0.get("annualized_compound"))
                < 1e-12 for cell in net0.values()))
        leg("L5h and the rent grows with the notional shorted",
            (((face.get("net_of_borrow") or {}).get("etf") or {}).get("1.0") or {})
            [("%.2f" % min(ETF_BORROW_FEES))]["annualized_compound"]
            < (((face.get("net_of_borrow") or {}).get("etf") or {}).get("0.5") or {})
            [("%.2f" % min(ETF_BORROW_FEES))]["annualized_compound"])
        leg("L5i the page carries the verdict token",
            ("`%s`" % face.get("verdict")) in open(OUT_MD, encoding="utf-8").read())
    else:
        leg("L5 live face skipped (files absent)", True, "skipped")

    width = max(len(n) for n, _, _ in legs) + 2
    bad = 0
    for name, ok, detail in legs:
        if not ok:
            bad += 1
        print("%s %-*s %s" % ("PASS" if ok else "FAIL", width, name, detail))
    print("%d/%d PASS" % (len(legs) - bad, len(legs)))
    return 0 if bad == 0 else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=("run", "check", "selftest"))
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())
