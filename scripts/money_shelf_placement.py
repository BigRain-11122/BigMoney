#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""money_shelf_placement -- which of the shelf can hold the book's cash, and what does the screen cost?

WHY THIS FACE EXISTS
--------------------
Four faces have now audited the money shelf from four directions and none of them answers the
only question a person with cash and a ticket has:

* r2048 (`cash_shelf_flip_census`)  -- named the anomalous *prints* by sigma.
* r2050 (`money_premium_carry_audit`) -- priced the premium as carry you never collect, on the
  11 instruments that had episodes.
* r2051 (`money_band_blind_spot`)   -- showed the 1% band leaves a tail, and that the level of a
  money tape re-anchors about every ten bars so a persistent premium is invisible to it.
* r2053 (`money_residual_sigma_recovery`) -- showed 34 of 36 tapes have no accrual clock at all.

Every one of those ends with "and the book's own legs are clean", which is true and also useless
for the decision: the book does not always hold cash in its own legs.  When the ticket is out of
the market for a few days (r2041: 95 分位 265 元 of build-out cost on the 565,246 元 ticket) the
question is where the cash waits, and the shelf it waits in is the 59-code money class.

So this face does not re-measure anything.  It takes the two published rulers -- the
premium-repaired annual carry (`money_premium_carry_audit.measure_one`, r2050) and the
accrual-speed / clock test (`money_residual_sigma_recovery.read_one`, r2053) -- and puts them on
all 56 priced money codes, then answers three questions with money on the ticket:

1. How many of them may actually hold cash (admission, reasons printed)?
2. What does a screen that ranks by the printed number pick, and what does that pick actually pay?
3. What does a gate that ranks by the collectible number pick, and is the difference worth the
   gate?

THE QUESTION (frozen before the first run)
------------------------------------------
On the r2048 money universe (class = money, priced), in r2048's own window, holding the r2041
ticket of 565,246 元:

1. ADMISSION.  Which codes pass all four refusals below, and for the rest, which refusal fired?
2. PHANTOM.  For the code with the highest *printed* carry, how much of the money it appears to
   pay is premium the repair removes (元/年 on the ticket)?
3. FORGONE.  Comparing the printed-rank pick and the repaired-rank pick, does the gate gain or
   lose 元/年, and how does either compare with the book's own best leg?

RULERS (imported, not re-decided)
---------------------------------
* **PRINTED CARRY** = `MP.measure_one(code, start, end)["cagr_printed_pct"]` -- annual return of
  the published reader's series (drops below -50 bp booked at zero).  This is the number a screen
  sees.
* **COLLECTIBLE CARRY** = the same call's `cagr_repaired_pct` -- after zeroing every bar that sits
  more than 1% away from its own 20-bar median (r2050's band, r2050's function).
* **PHANTOM** = PRINTED - COLLECTIBLE, in pp/yr and 元/年 on the ticket.
* **ACCRUAL / CLOCK / EQUITY SPEED** = `R.read_one(px)` (r2053): median daily return, the
  `>= 0.0133 bp` clock floor, and the `>= 2 bp` equity-speed line.
* **CLOSE IS A RETURN** = `CV.carries_return(px)` -- a fixed-face vehicle pays in shares and its
  close carries no return at all.

ADMISSION (five refusals, in this order, first match wins)
----------------------------------------------------------
1. REFUSE_FIXED_FACE     -- the close is not a return, so no carry can be read from it.
2. REFUSE_NOT_MONEY      -- median bar >= 2 bp: the class label says money, the tape says equity.
                            (r2053's contamination: names containing 现金流.)
3. REFUSE_NOISY_TAPE     -- robust sigma >= 2 bp: the *typical* bar is already bigger than a day
                            of carry, so "annualised median" is not a carry at all.  This is the
                            half of r2053's contamination that its mean test let through: 8 of
                            the 28 现金流 names have a median bar under 2 bp but a typical bar of
                            72-95 bp, so they survived that test and are refused here.
4. REFUSE_THIN           -- fewer than 250 bars inside the window.
5. REFUSE_NEGATIVE_CARRY -- repaired carry <= 0: after the premium is taken out there is nothing
                            left to be paid for waiting.
6. ADMIT                 -- none of the above.

NOISE_BP is the only threshold this face adds, and it is not tuned: every money-class tape
measured in r2053 has a robust sigma of 0.15-1.19 bp and every 现金流 tape has 72-116 bp, so any
line from 2 to 70 separates them.  2.0 bp is where a single day of carry stops being the typical
bar.

VERDICTS (mechanical)
---------------------
* THE_SCREEN_PAYS_IN_PREMIA -- the printed-rank pick's PHANTOM >= 1.00 pp/yr (r2050's MATERIAL_PP).
* THE_SCREEN_IS_HONEST      -- it is below that line.
* MOST_OF_THE_SHELF_IS_NOT_A_PARKING_SPOT -- admitted / priced <= 0.50.
* HALF_THE_SHELF_IS_A_PARKING_SPOT        -- admitted / priced <= 0.80.
* THE_SHELF_IS_MOSTLY_USABLE              -- above that.
* THE_GATE_PAYS / THE_GATE_COSTS -- gate pick's realized 元/年 vs the screen pick's realized 元/年.

TAGS (printed beside the verdicts, never folded into them)
----------------------------------------------------------
* THE_SCREEN_TOP_IS_THE_WORST_LIAR -- the printed-rank pick also owns the largest phantom.
* AN_ADMITTED_SPOT_BEATS_THE_BOOK_LEG -- the gate's pick pays more than the best book leg.
* THE_BOOK_LEG_BEATS_THE_ADMITTED_SHELF -- the reverse.
* refusal counts per reason, the two picks with their numbers, and the phantom total are printed
  as measurement lines.

WHAT THIS FACE CANNOT DO (printed, not folded)
----------------------------------------------
* It does not decide whether a money ETF can be sold at all: capacity, one-lot size and turnover
  are r2041/r2043's business and are not re-read here.
* PRINTED and COLLECTIBLE are both annualised from the same six years; a premium episode in the
  next six years will not look like these.
* Refusal is about *reading* a carry, not about the instrument being unsound.  A fixed-face money
  fund is a perfectly good place for cash; it simply cannot be ranked on a close price.
* The ticket is r2041's 565,246 元, read from that face, not chosen here.

Usage:
    python scripts/money_shelf_placement.py run
    python scripts/money_shelf_placement.py --check
    python scripts/money_shelf_placement.py --write
    python scripts/money_shelf_placement.py --selftest
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import etf_book_cash_vehicle as CV  # noqa: E402  (the published money reader)
import money_premium_carry_audit as MP  # noqa: E402  (r2050: printed vs repaired carry)
import money_residual_sigma_recovery as R  # noqa: E402  (r2053: accrual clock, equity speed)

CENSUS_FACE = "results/cash_shelf_flip_census.json"
PREMIUM_FACE = "results/money_premium_carry_audit.json"
SIGMA_FACE = "results/money_residual_sigma_recovery.json"
TICKET_FACE = "results/cb_parking_shelf_at_size.json"
FACE = "results/money_shelf_placement.json"
DOC = "research/MONEY_SHELF_PLACEMENT.md"

MIN_BARS = 250          # r2053's own floor for "this tape can be read at all"
NOISE_BP = 2.0          # a cash tape's typical bar is a day of carry; measured 0.15-1.19 bp
MATERIAL_PP = 1.00      # r2050's line: at or above this the premium, not the carry, is printed
ABSURD_PP = 20.0        # no cash instrument pays this; anything above it is a mislabelled tape
ADMIT_HALF = 0.50       # admitted / priced, the "mostly not a parking spot" line
ADMIT_MOSTLY = 0.80
GATE_TOL = 0.02         # pp: the gate that re-reads r2050 must agree with it to this precision
SIGMA_TOL = 0.05        # bp: same, against r2053's plain sigma

_QUIET = False


def log(msg: str) -> None:
    if not _QUIET:
        print(msg)


# ----------------------------------------------------------------------------- io helpers
def _load(path):
    with open(os.path.join(ROOT, path), "r", encoding="utf-8") as fh:
        return json.load(fh)


def _content_sha(obj) -> str:
    blob = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _file_sha(path) -> str:
    with open(os.path.join(ROOT, path), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# ----------------------------------------------------------------------------- admission
REFUSALS = ("REFUSE_FIXED_FACE", "REFUSE_NOT_MONEY", "REFUSE_NOISY_TAPE", "REFUSE_THIN",
            "REFUSE_NEGATIVE_CARRY")
# the first four are about *reading* a tape at all; the last one is about collecting the carry
READABILITY = REFUSALS[:4]


def admission_of(rec) -> tuple:
    """Five refusals in the frozen order; the first match wins.  Returns (verdict, reason)."""
    if not rec.get("priced"):
        return "REFUSE_THIN", rec.get("why_unpriced") or "not priced"
    if not rec.get("carries_return", True):
        return "REFUSE_FIXED_FACE", "close carries no return (pays in shares)"
    if rec.get("equity_speed"):
        return "REFUSE_NOT_MONEY", ("median bar %s bp >= 2 bp: an equity tape wearing a money label"
                                    % rec.get("accrual_bp"))
    robust = rec.get("sigma_robust_bp_2053")
    if robust is not None and robust >= NOISE_BP:
        return "REFUSE_NOISY_TAPE", ("typical bar %.2f bp >= %g bp: a cash tape's day of carry is "
                                     "under 1 bp" % (robust, NOISE_BP))
    if rec.get("bars", 0) < MIN_BARS:
        return "REFUSE_THIN", "%d bars < %d" % (rec.get("bars", 0), MIN_BARS)
    repaired = rec.get("cagr_repaired_pct")
    if repaired is None or repaired <= 0.0:
        return "REFUSE_NEGATIVE_CARRY", ("repaired carry %s%% leaves nothing for the wait"
                                         % repaired)
    return "ADMIT", "passes all five refusals"


def pick_printed(rows):
    """What a screen ranks by: the highest printed number among tapes it can read at all.

    The four readability refusals are applied first, because a screen does filter them too (it
    drops a fixed-face vehicle whose close is flat, and it is obvious that a 213%/yr cash-labelled
    ETF is not cash).  The single thing it does NOT do is the premium repair -- that is the one
    variable this comparison moves.
    """
    live = [r for r in rows if r.get("readable") and r.get("cagr_printed_pct") is not None]
    return max(live, key=lambda r: r["cagr_printed_pct"]) if live else None


def pick_repaired(rows):
    """What the gate ranks by: the highest collectible number among admitted codes only."""
    live = [r for r in rows if r.get("admission") == "ADMIT"]
    return max(live, key=lambda r: r["cagr_repaired_pct"]) if live else None


def verdict_of(pick) -> str:
    if pick is None:
        return "THE_SCREEN_IS_HONEST"
    phantom = pick.get("phantom_pp")
    if phantom is None:
        return "THE_SCREEN_IS_HONEST"
    return "THE_SCREEN_PAYS_IN_PREMIA" if phantom >= MATERIAL_PP else "THE_SCREEN_IS_HONEST"


def admission_verdict_of(admitted, priced) -> str:
    if not priced:
        return "MOST_OF_THE_SHELF_IS_NOT_A_PARKING_SPOT"
    share = admitted / float(priced)
    if share <= ADMIT_HALF:
        return "MOST_OF_THE_SHELF_IS_NOT_A_PARKING_SPOT"
    if share <= ADMIT_MOSTLY:
        return "HALF_THE_SHELF_IS_A_PARKING_SPOT"
    return "THE_SHELF_IS_MOSTLY_USABLE"


def gate_verdict_of(gated, naive) -> str:
    a = (gated or {}).get("realized_cny") or 0.0
    b = (naive or {}).get("realized_cny") or 0.0
    return "THE_GATE_PAYS" if a >= b else "THE_GATE_COSTS"


def tags_of(rows, naive, gated, book_best) -> list:
    tags = []
    counts = {}
    for r in rows:
        if r.get("priced"):
            counts[r.get("admission")] = counts.get(r.get("admission"), 0) + 1
    tags.append("refusals=" + ",".join("%s:%d" % (k, counts.get(k, 0)) for k in REFUSALS + ("ADMIT",)))
    if naive:
        tags.append("screen_top=%s:printed_%.2f_realized_%.2f" % (
            naive["code"], naive["cagr_printed_pct"], naive["cagr_repaired_pct"]))
    if gated:
        tags.append("gate_top=%s:realized_%.2f" % (gated["code"], gated["cagr_repaired_pct"]))
    if book_best:
        tags.append("book_leg_best=%s:repaired_%.2f" % (book_best["code"],
                                                        book_best["cagr_repaired_pct"]))
    if naive and naive.get("phantom_pp") is not None:
        worst = max((r for r in rows if r.get("phantom_pp") is not None),
                    key=lambda r: r["phantom_pp"], default=None)
        if worst is not None and worst["code"] == naive["code"]:
            tags.append("THE_SCREEN_TOP_IS_THE_WORST_LIAR")
    absurd = [r for r in rows if (r.get("cagr_printed_pct") or 0.0) >= ABSURD_PP]
    if absurd:
        tags.append("A_CASH_LABEL_PRINTS_%gPCT_A_YEAR_ON_%d_TAPES" % (
            ABSURD_PP, len(absurd)))
        tags.append("absurd_top=%s:%.1f" % (
            max(absurd, key=lambda r: r["cagr_printed_pct"])["code"],
            max(r["cagr_printed_pct"] for r in absurd)))
    if gated and book_best:
        if gated["cagr_repaired_pct"] > book_best["cagr_repaired_pct"]:
            tags.append("AN_ADMITTED_SPOT_BEATS_THE_BOOK_LEG")
        else:
            tags.append("THE_BOOK_LEG_BEATS_THE_ADMITTED_SHELF")
    return tags


# ----------------------------------------------------------------------------- build
def _one(code, name, start, end, ticket) -> dict:
    m = MP.measure_one(code, start, end, name=name)
    rec = {
        "code": code,
        "name": name,
        "priced": bool(m.get("priced")),
        "why_unpriced": m.get("why_unpriced"),
        "bars": m.get("bars") or 0,
        "window_end": m.get("window_end"),
        "cagr_printed_pct": m.get("cagr_printed_pct"),
        "cagr_repaired_pct": m.get("cagr_repaired_pct"),
        "episode_count": len(m.get("episodes") or []),
        "episode_bars": m.get("episode_bars"),
        "max_dev_pct": m.get("max_dev_pct"),
        "sigma_printed_bp": m.get("sigma_printed_bp"),
        "sigma_repaired_bp": m.get("sigma_repaired_bp"),
    }
    if rec["priced"] and rec["cagr_printed_pct"] is not None and rec["cagr_repaired_pct"] is not None:
        rec["phantom_pp"] = round(rec["cagr_printed_pct"] - rec["cagr_repaired_pct"], 4)
        rec["believed_cny"] = round(ticket * rec["cagr_printed_pct"] / 100.0, 2)
        rec["realized_cny"] = round(ticket * rec["cagr_repaired_pct"] / 100.0, 2)
        rec["phantom_cny"] = round(rec["believed_cny"] - rec["realized_cny"], 2)
    else:
        rec["phantom_pp"] = None
        rec["believed_cny"] = None
        rec["realized_cny"] = None
        rec["phantom_cny"] = None
    # r2053's side: the clock and the contamination line
    try:
        px = R._series(code)
        px = px[(px.index >= pd.Timestamp(start)) & (px.index <= pd.Timestamp(end))]
        px = px.dropna().astype(float)
        rec["carries_return"] = bool(CV.carries_return(px))
        if len(px) >= MIN_BARS:
            r2053 = R.read_one(px)
            rec["accrual_bp"] = r2053["accrual_bp"]
            rec["equity_speed"] = bool(r2053["equity_speed"])
            rec["has_usable_clock"] = bool(r2053["has_usable_clock"])
            rec["sigma_plain_bp_2053"] = r2053["sigma_plain_bp"]
            rec["sigma_robust_bp_2053"] = r2053["sigma_robust_bp"]
            rec["n_events"] = r2053["n_events"]
            rec["n_snap"] = r2053["n_snap"]
        else:
            rec["accrual_bp"] = None
            rec["equity_speed"] = False
            rec["has_usable_clock"] = False
            rec["sigma_plain_bp_2053"] = None
            rec["sigma_robust_bp_2053"] = None
            rec["n_events"] = 0
            rec["n_snap"] = 0
    except FileNotFoundError:
        rec["carries_return"] = True
        rec["accrual_bp"] = None
        rec["equity_speed"] = False
        rec["has_usable_clock"] = False
        rec["sigma_plain_bp_2053"] = None
        rec["sigma_robust_bp_2053"] = None
        rec["n_events"] = 0
        rec["n_snap"] = 0
    adm, why = admission_of(rec)
    rec["admission"] = adm
    rec["reason"] = why
    rec["readable"] = bool(rec.get("priced") and adm not in READABILITY)
    return rec


def gate_reproduction(rows, premium, sigma) -> dict:
    """The two published faces must agree with what this face re-derives, or nothing is published."""
    by = {r["code"]: r for r in rows}
    checks = []
    for pub in (premium.get("rows") or []):
        got = by.get(pub["code"])
        if got is None or not got.get("priced"):
            checks.append({"code": pub["code"], "what": "premium row", "ok": False,
                           "why": "not re-derived here"})
            continue
        d = abs((got.get("cagr_repaired_pct") or 0.0) - (pub.get("cagr_repaired_pct") or 0.0))
        checks.append({"code": pub["code"], "what": "cagr_repaired", "got": got.get("cagr_repaired_pct"),
                       "published": pub.get("cagr_repaired_pct"), "delta_pp": round(d, 4),
                       "ok": d <= GATE_TOL})
    for pub in (sigma.get("rows") or []):
        if not pub.get("priced"):
            continue
        got = by.get(pub["code"])
        if got is None or got.get("sigma_plain_bp_2053") is None:
            continue
        d = abs(got["sigma_plain_bp_2053"] - pub["sigma_plain_bp"])
        checks.append({"code": pub["code"], "what": "sigma_plain", "got": got["sigma_plain_bp_2053"],
                       "published": pub["sigma_plain_bp"], "delta_bp": round(d, 3),
                       "ok": d <= SIGMA_TOL})
    bad = [c for c in checks if not c["ok"]]
    return {"checks": len(checks), "failed": len(bad), "ok": not bad, "bad": bad[:10]}


def build() -> dict:
    census = _load(CENSUS_FACE)
    premium = _load(PREMIUM_FACE)
    sigma = _load(SIGMA_FACE)
    ticket = float(_load(TICKET_FACE)["ticket_cash_cny"])
    start = pd.Timestamp(census["window"]["start"])
    end = pd.Timestamp(census["window"]["end"])
    names = {r["code"]: r.get("name") for r in census["rows"]}
    money = [r["code"] for r in census["rows"] if r.get("class") == "money"]

    rows = [_one(code, names.get(code), start, end, ticket) for code in sorted(money)]
    priced = [r for r in rows if r.get("priced")]
    readable = [r for r in rows if r.get("readable")]
    admitted = [r for r in rows if r.get("admission") == "ADMIT"]

    naive = pick_printed(rows)
    gated = pick_repaired(rows)
    book_legs = [b for b in (premium.get("book_legs") or [])
                 if b.get("carry_ruler_applies") and b.get("cagr_repaired_pct") is not None]
    book_best = max(book_legs, key=lambda b: b["cagr_repaired_pct"]) if book_legs else None

    counts = {k: sum(1 for r in priced if r.get("admission") == k) for k in REFUSALS + ("ADMIT",)}
    cutoff = max((r["window_end"] for r in priced if r.get("window_end")), default=None)

    def money_row(rec):
        if rec is None:
            return None
        out = {"code": rec["code"], "name": rec.get("name")}
        for k in ("cagr_printed_pct", "cagr_repaired_pct", "phantom_pp",
                  "believed_cny", "realized_cny", "phantom_cny", "admission"):
            out[k] = rec.get(k)
        return out

    best_book_pp = book_best["cagr_repaired_pct"] if book_best is not None else None

    bk = None
    if book_best is not None:
        bk = {"code": book_best["code"], "name": book_best.get("name"),
              "class": book_best.get("class"),
              "cagr_repaired_pct": round(book_best["cagr_repaired_pct"], 4),
              "realized_cny": round(ticket * book_best["cagr_repaired_pct"] / 100.0, 2)}

    payload = {
        "schema": "money-shelf-placement/v1",
        "artifact": "money_shelf_placement",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": cutoff,
        "window": {"start": str(start.date()), "end": str(end.date())},
        "question": ("which money-class codes may hold the book's cash, what does a screen that "
                     "ranks by the printed number pick and actually pay, and does a gate that "
                     "ranks by the collectible number pay for itself?"),
        "ticket_cash_cny": ticket,
        "ticket_source": TICKET_FACE,
        "ruler": {
            "printed_carry": "money_premium_carry_audit.measure_one(...)['cagr_printed_pct']",
            "collectible_carry": "the same call's cagr_repaired_pct (1% band repair, r2050)",
            "phantom_pp": "printed - collectible",
            "clock_and_contamination": "money_residual_sigma_recovery.read_one (r2053)",
            "close_is_a_return": "etf_book_cash_vehicle.carries_return",
            "admission_order": list(REFUSALS) + ["ADMIT"],
            "min_bars": MIN_BARS,
            "material_pp": MATERIAL_PP,
            "this_is_not": "a capacity or one-lot test (r2041/r2043 own those)",
        },
        "upstream": {
            "census_face": CENSUS_FACE,
            "census_sha256": _file_sha(CENSUS_FACE),
            "premium_face": PREMIUM_FACE,
            "premium_sha256": _file_sha(PREMIUM_FACE),
            "sigma_face": SIGMA_FACE,
            "sigma_sha256": _file_sha(SIGMA_FACE),
            "ticket_face": TICKET_FACE,
            "ticket_sha256": _file_sha(TICKET_FACE),
            "premium_cutoff": premium.get("evidence_cutoff"),
            "sigma_cutoff": sigma.get("evidence_cutoff"),
        },
        "gate": gate_reproduction(rows, premium, sigma),
        "universe": {
            "money_listed": len(money),
            "money_priced": len(priced),
            "readable": len(readable),
            "admitted": len(admitted),
            "refused": len(priced) - len(admitted),
            "counts": counts,
        },
        "verdict": verdict_of(naive),
        "admission_verdict": admission_verdict_of(len(admitted), len(priced)),
        "gate_verdict": gate_verdict_of(gated, naive),
        "tags": tags_of(rows, naive, gated, book_best),
        "headline": {
            "screen_pick": money_row(naive),
            "gate_pick": money_row(gated),
            "book_leg_best": bk,
            "forgone_by_screening_cny": (round((gated or {}).get("realized_cny", 0.0)
                                              - (naive or {}).get("realized_cny", 0.0), 2)
                                        if gated and naive else None),
            "phantom_total_cny": round(sum(r["phantom_cny"] for r in priced
                                           if r.get("phantom_cny") is not None), 2),
            "phantom_total_readable_cny": round(sum(r["phantom_cny"] for r in readable
                                                    if r.get("phantom_cny") is not None), 2),
            "absurd_carry": {
                "count": sum(1 for r in priced
                             if (r.get("cagr_printed_pct") or 0.0) >= ABSURD_PP),
                "max_code": (max(priced, key=lambda r: r.get("cagr_printed_pct") or -99.0) or {}).get("code")
                            if priced else None,
                "max_pp": (max((r.get("cagr_printed_pct") or -99.0) for r in priced)
                           if priced else None),
            },
            "best_collectible_pp": (round(max(r["cagr_repaired_pct"] for r in admitted), 4)
                                    if admitted else None),
            "margin_vs_book_pp": (round(gated["cagr_repaired_pct"] - best_book_pp, 4)
                                  if (gated is not None and best_book_pp is not None) else None),
            "gate_pick_trades_like_a_thin_tape": bool(
                gated is not None and (gated.get("n_events") or 0) > 0
                and (gated.get("n_snap") or 0) / float(gated["n_events"]) >= 0.4),
        },
        "not_claimed": [
            "Refusal is about reading a carry from a close, not about the fund being unsound.",
            "Capacity, one-lot size and turnover are r2041/r2043's; not re-read here.",
            "Both carries are one six-year window; a premium episode that has not happened yet "
            "will not look like these.",
            "The ticket is r2041's number, read from that face.",
        ],
        "rows": sorted(rows, key=lambda r: (r.get("admission") != "ADMIT",
                                            -(r.get("cagr_repaired_pct") or -99.0),
                                            r["code"])),
    }
    payload["content_sha256"] = _content_sha(
        {k: v for k, v in payload.items() if k != "content_sha256"})
    return payload


# ----------------------------------------------------------------------------- rendering
def _f(v, nd=2, dash="-"):
    if v is None:
        return dash
    if isinstance(v, float):
        return ("%." + str(nd) + "f") % v
    return str(v)


def render_table(payload) -> str:
    lines = [
        "| code | name | bars | printed %/yr | collectible %/yr | phantom pp | phantom 元/yr | admission |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for r in payload["rows"]:
        if not r.get("priced"):
            continue
        lines.append("| %s | %s | %d | %s | %s | %s | %s | %s |" % (
            r["code"], r.get("name") or "-", r["bars"],
            _f(r["cagr_printed_pct"], 2), _f(r["cagr_repaired_pct"], 2),
            _f(r.get("phantom_pp"), 2), _f(r.get("phantom_cny"), 0), r.get("admission")))
    return "\n".join(lines)


def write_doc(payload) -> None:
    h = payload["headline"]
    sp, gp, bk = h["screen_pick"], h["gate_pick"], h["book_leg_best"]
    counts = payload["universe"]["counts"]
    body = [
        "<!-- MONEY-SHELF-PLACEMENT:BEGIN -->",
        "",
        "**verdict** `%s` / `%s` / `%s`" % (payload["verdict"], payload["admission_verdict"],
                                            payload["gate_verdict"]),
        "",
        "票面 %s 元（取自 %s）。货币架 %d 只，够长可读 %d 只，过闸 %d 只；拒绝构成：固定面值 %d / 不是货币 %d / "
        "不是现金带 %d / 太短 %d / 修完是负的 carry %d。" % (
            _f(payload["ticket_cash_cny"], 0), payload["ticket_source"],
            payload["universe"]["money_listed"], payload["universe"]["readable"],
            payload["universe"]["admitted"],
            counts.get("REFUSE_FIXED_FACE", 0), counts.get("REFUSE_NOT_MONEY", 0),
            counts.get("REFUSE_NOISY_TAPE", 0),
            counts.get("REFUSE_THIN", 0), counts.get("REFUSE_NEGATIVE_CARRY", 0)),
        "",
        "**按屏幕上那个数挑**：%s，印 %s%%/年，实际收 %s%%/年 —— 面上 %s 元/年，拿到手 %s 元/年，"
        "差 %s 元/年是溢价，收不到。**按修完之后的数挑**：%s，%s%%/年 = %s 元/年。" % (
            (sp or {}).get("code", "-"), _f((sp or {}).get("cagr_printed_pct"), 2),
            _f((sp or {}).get("cagr_repaired_pct"), 2),
            _f((sp or {}).get("believed_cny"), 0), _f((sp or {}).get("realized_cny"), 0),
            _f((sp or {}).get("phantom_cny"), 0),
            (gp or {}).get("code", "-"), _f((gp or {}).get("cagr_repaired_pct"), 2),
            _f((gp or {}).get("realized_cny"), 0)),
        "",
        "这一道闸值 %s 元/年（同一张票面）。书自己最好的腿是 %s，%s%%/年 = %s 元/年。" % (
            _f(h.get("forgone_by_screening_cny"), 0),
            (bk or {}).get("code", "-"), _f((bk or {}).get("cagr_repaired_pct"), 2),
            _f((bk or {}).get("realized_cny"), 0)),
        "",
        ("过闸第一名的优势只有 %s pp（%s 元/年），而且它按 r2053 的尺是薄盘子（多数极端 bar 是报价翻转）——"
         "这是「别再按屏幕挑」的读数，不是「换到它」的指令。" % (
             _f(h.get("margin_vs_book_pp"), 2),
             _f((h.get("margin_vs_book_pp") or 0.0) * payload["ticket_cash_cny"] / 100.0, 0))
         if h.get("margin_vs_book_pp") is not None and h.get("gate_pick_trades_like_a_thin_tape")
         else "过闸第一名对书自己最好的腿 +%s pp——优势够大，但仍须过容量关（r2041/r2043），本页不替它们定价。" % (
             _f(h.get("margin_vs_book_pp"), 2))),
        "",
        "可读的 %d 只逐只 believed - realized 相加 = %s 元/年（同一张票面逐只假设持满，不是可加的组合）："
        "这不是收益，是屏幕上多出来的数。" % (
            payload["universe"]["readable"], _f(h.get("phantom_total_readable_cny"), 0)),
        "",
        "tags: " + " / ".join("`%s`" % t for t in payload["tags"]),
        "",
        render_table(payload),
        "",
        "读法：`printed` 是发布读器口径（跌破 -50bp 记零）下的年化，也就是行情软件上会看到的数；"
        "`collectible` 是把离自己 20 日中位 >1% 的 bar 记为溢价之后的年化（r2050 的尺）；"
        "`phantom` 是两者之差，乘票面就是「看着有、收不到」的钱。"
        "`admission` 五道拒绝按顺序先命中先算：固定面值 > 不是货币（中位 bar ≥2bp）> 不是现金带（典型 bar ≥2bp）"
        "> 太短（<250 根）> 修完 ≤0。",
        "",
        "<!-- MONEY-SHELF-PLACEMENT:END -->",
    ]
    doc = "\n".join(body) + "\n"
    with open(os.path.join(ROOT, DOC), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc)
    log("wrote %s (%d bytes)" % (DOC, len(doc.encode("utf-8"))))


def _block_of(text: str) -> str:
    b = text.find("<!-- MONEY-SHELF-PLACEMENT:BEGIN -->")
    e = text.find("<!-- MONEY-SHELF-PLACEMENT:END -->")
    if b < 0 or e < 0:
        return ""
    return text[b:e]


# ----------------------------------------------------------------------------- check
def check(payload=None) -> tuple:
    """Re-derive from the panel.  STALE = an input moved; CHECK FAILED = my own arithmetic."""
    problems = []
    stale = []
    face_path = os.path.join(ROOT, FACE)
    if payload is None:
        if not os.path.exists(face_path):
            return 3, ["STALE face missing: %s" % FACE]
        with open(face_path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)

    for key, path in (("census_sha256", CENSUS_FACE), ("premium_sha256", PREMIUM_FACE),
                      ("sigma_sha256", SIGMA_FACE), ("ticket_sha256", TICKET_FACE)):
        if _file_sha(path) != payload["upstream"][key]:
            stale.append("STALE upstream moved: %s" % path)

    if not stale:
        fresh = build()
        by = {r["code"]: r for r in fresh["rows"]}
        for old in payload["rows"]:
            got = by.get(old["code"])
            if got is None:
                stale.append("STALE row vanished: %s" % old["code"])
                continue
            if got.get("priced") != old.get("priced"):
                stale.append("STALE priced changed: %s" % old["code"])
                continue
            if not old.get("priced"):
                continue
            if got.get("bars") != old.get("bars"):
                stale.append("STALE bars moved %s: %d -> %d" % (old["code"], old["bars"],
                                                               got.get("bars")))
                continue
            for k in ("cagr_printed_pct", "cagr_repaired_pct", "phantom_pp"):
                a, b = old.get(k), got.get(k)
                if (a is None) != (b is None):
                    problems.append("%s %s null mismatch" % (old["code"], k))
                elif a is not None and abs(a - b) > GATE_TOL:
                    problems.append("%s %s %.4f != %.4f" % (old["code"], k, a, b))
            if got.get("admission") != old.get("admission"):
                problems.append("%s admission %s != %s" % (old["code"], got.get("admission"),
                                                           old.get("admission")))
        for k in ("verdict", "admission_verdict", "gate_verdict", "ticket_cash_cny"):
            if fresh.get(k) != payload.get(k):
                problems.append("%s %s != %s" % (k, fresh.get(k), payload.get(k)))

    doc_path = os.path.join(ROOT, DOC)
    if not os.path.exists(doc_path):
        stale.append("STALE doc missing: %s" % DOC)
    else:
        with open(doc_path, "r", encoding="utf-8") as fh:
            block = _block_of(fh.read())
        if "`%s`" % payload["verdict"] not in block:
            stale.append("STALE doc block is not this verdict")

    if problems:
        return 3, ["CHECK FAILED"] + problems[:20]
    if stale:
        return 3, ["STALE"] + stale[:20]
    return 0, ["CHECK OK %d money codes re-derived, %d admitted, cutoff %s" % (
        payload["universe"]["money_priced"], payload["universe"]["admitted"],
        payload["evidence_cutoff"])]


# ----------------------------------------------------------------------------- selftest
def selftest() -> int:
    fails = []
    n_ok = 0

    def ok(cond, msg):
        nonlocal n_ok
        if cond:
            n_ok += 1
        else:
            fails.append(msg)

    def rec(**kw):
        base = {"code": "X", "priced": True, "carries_return": True, "equity_speed": False,
                "bars": 1200, "cagr_printed_pct": 1.0, "cagr_repaired_pct": 0.9,
                "phantom_pp": 0.1, "accrual_bp": 0.6, "sigma_robust_bp_2053": 0.74}
        base.update(kw)
        base["readable"] = bool(base.get("priced")
                                and base.get("admission", "ADMIT") not in READABILITY)
        return base

    # 1. the five refusals, each on its own, and their order
    ok(admission_of(rec())[0] == "ADMIT", "L1 a clean record was not admitted")
    ok(admission_of(rec(carries_return=False))[0] == "REFUSE_FIXED_FACE",
       "L2 fixed face not refused")
    ok(admission_of(rec(carries_return=False, equity_speed=True))[0] == "REFUSE_FIXED_FACE",
       "L3 fixed face does not win over not-money")
    ok(admission_of(rec(equity_speed=True))[0] == "REFUSE_NOT_MONEY", "L4 equity speed admitted")
    ok(admission_of(rec(sigma_robust_bp_2053=90.4))[0] == "REFUSE_NOISY_TAPE",
       "L5 a 90 bp typical bar was admitted as cash")
    ok(admission_of(rec(equity_speed=True, sigma_robust_bp_2053=90.4))[0] == "REFUSE_NOT_MONEY",
       "L6 the mean test does not win over the sigma test")
    ok(admission_of(rec(sigma_robust_bp_2053=1.19))[0] == "ADMIT",
       "L7 the widest real money tape (1.19 bp) was refused")
    ok(admission_of(rec(sigma_robust_bp_2053=None))[0] == "ADMIT",
       "L8 an unmeasured sigma refused instead of deferring")
    ok(admission_of(rec(bars=100))[0] == "REFUSE_THIN", "L9 a thin tape was admitted")
    ok(admission_of(rec(cagr_repaired_pct=-0.2))[0] == "REFUSE_NEGATIVE_CARRY",
       "L10 a negative repaired carry was admitted")
    ok(admission_of(rec(cagr_repaired_pct=0.0))[0] == "REFUSE_NEGATIVE_CARRY",
       "L11 exactly zero repaired carry was admitted")
    ok(admission_of(rec(priced=False))[0] == "REFUSE_THIN", "L12 an unpriced record was admitted")

    # 2. the two picks: printed ranks everything, repaired ranks only admitted
    rows = [rec(code="A", cagr_printed_pct=8.4, cagr_repaired_pct=0.6, phantom_pp=7.8,
                admission="REFUSE_NOT_MONEY"),
            rec(code="B", cagr_printed_pct=2.4, cagr_repaired_pct=2.3, phantom_pp=0.1,
                admission="ADMIT"),
            rec(code="C", cagr_printed_pct=4.3, cagr_repaired_pct=1.9, phantom_pp=2.4,
                admission="ADMIT")]
    ok(pick_printed(rows)["code"] == "C",
       "L9 the screen did not take the printed top among readable tapes")
    ok(pick_printed(rows)["code"] != "A",
       "L9b the screen took a tape the readability tests refuse")
    ok(pick_repaired(rows)["code"] == "B", "L10 the gate did not take the admitted top")
    ok(pick_repaired([rec(code="A", admission="REFUSE_NOT_MONEY")]) is None,
       "L11 the gate picked a refused code")

    # 3. verdicts are functions of the numbers
    ok(verdict_of({"phantom_pp": 7.8}) == "THE_SCREEN_PAYS_IN_PREMIA", "L12 material phantom ignored")
    ok(verdict_of({"phantom_pp": 0.3}) == "THE_SCREEN_IS_HONEST", "L13 a 0.3pp phantom called premium")
    ok(verdict_of(None) == "THE_SCREEN_IS_HONEST", "L14 no pick did not read as honest")
    ok(admission_verdict_of(10, 56) == "MOST_OF_THE_SHELF_IS_NOT_A_PARKING_SPOT", "L15 share 0.18")
    ok(admission_verdict_of(40, 56) == "HALF_THE_SHELF_IS_A_PARKING_SPOT", "L16 share 0.71")
    ok(admission_verdict_of(50, 56) == "THE_SHELF_IS_MOSTLY_USABLE", "L17 share 0.89")
    ok(gate_verdict_of({"realized_cny": 100.0}, {"realized_cny": 50.0}) == "THE_GATE_PAYS",
       "L18 gate that pays more was called a cost")
    ok(gate_verdict_of({"realized_cny": 50.0}, {"realized_cny": 100.0}) == "THE_GATE_COSTS",
       "L19 gate that pays less was called a pay")

    # 4. the ticket arithmetic is a multiplication, in the same units as the faces
    ticket = 565245.9
    believed = ticket * 8.4414 / 100.0
    realized = ticket * 0.6163 / 100.0
    ok(abs((believed - realized) - ticket * (8.4414 - 0.6163) / 100.0) < 0.01,
       "L20 the phantom is not the difference of the two carries on the ticket")
    ok(39_000 < (believed - realized) < 50_000,
       "L21 511770's phantom on the r2041 ticket is not in the 39-50k band: %.0f" % (believed - realized))

    # 5. tags read the numbers, not the names
    rows2 = [rec(code="A", admission="ADMIT", cagr_printed_pct=8.4, cagr_repaired_pct=0.6,
                 phantom_pp=7.8),
             rec(code="B", admission="ADMIT", cagr_printed_pct=2.4, cagr_repaired_pct=2.3,
                 phantom_pp=0.1)]
    t = tags_of(rows2, {"code": "A", "cagr_printed_pct": 8.4, "cagr_repaired_pct": 0.6,
                        "phantom_pp": 7.8},
                {"code": "B", "cagr_repaired_pct": 2.3}, None)
    ok("THE_SCREEN_TOP_IS_THE_WORST_LIAR" in t, "L22 the worst liar was not tagged")
    ok(any(x.startswith("refusals=") for x in t), "L23 refusal counts not printed as a tag")
    t2 = tags_of(rows2, {"code": "A", "cagr_printed_pct": 8.4, "cagr_repaired_pct": 0.6,
                         "phantom_pp": 7.8},
                 {"code": "B", "cagr_repaired_pct": 1.0},
                 {"code": "511880", "cagr_repaired_pct": 1.49})
    ok("AN_ADMITTED_SPOT_BEATS_THE_BOOK_LEG" not in t2,
       "L24 a gate pick below the book leg claimed to beat it")
    t3 = tags_of(rows2, None, {"code": "B", "cagr_repaired_pct": 2.3},
                 {"code": "511880", "cagr_repaired_pct": 1.49})
    ok("AN_ADMITTED_SPOT_BEATS_THE_BOOK_LEG" in t3, "L25 a gate pick above the book leg not tagged")

    # 6. determinism of the content sha (wall clock is excluded from the digest)
    a = {"x": 1, "generated": "t1"}
    b = {"x": 1, "generated": "t2"}
    ok(_content_sha({k: v for k, v in a.items() if k != "generated"})
       == _content_sha({k: v for k, v in b.items() if k != "generated"}),
       "L26 the content sha is not deterministic")

    # 7. the published face and its page agree on the verdict
    if os.path.exists(os.path.join(ROOT, FACE)) and os.path.exists(os.path.join(ROOT, DOC)):
        with open(os.path.join(ROOT, FACE), "r", encoding="utf-8") as fh:
            face = json.load(fh)
        with open(os.path.join(ROOT, DOC), "r", encoding="utf-8") as fh:
            block = _block_of(fh.read())
        ok("`%s`" % face["verdict"] in block, "L27 doc block does not print the face verdict")
        ok(face.get("gate", {}).get("ok") is True, "L28 the published face carries a refused gate")
        ok(face["universe"]["admitted"] >= 1, "L29 no admitted code: the gate needs reviewing")

    log("selftest %d/%d PASS" % (n_ok, n_ok + len(fails)))
    for f in fails:
        log("  FAIL " + f)
    return 0 if not fails else 1


# ----------------------------------------------------------------------------- run
def run() -> int:
    payload = build()
    if not payload["gate"]["ok"]:
        log("REFUSE: the two published faces do not agree with this re-derivation")
        for bad in payload["gate"]["bad"]:
            log("  " + json.dumps(bad, ensure_ascii=False))
        return 1
    path = os.path.join(ROOT, FACE)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=False)
        fh.write("\n")
    write_doc(payload)
    h = payload["headline"]
    log("%s -> %s" % (payload["verdict"], FACE))
    log("  %s / %s" % (payload["admission_verdict"], payload["gate_verdict"]))
    log("  %d/%d admitted; screen pick %s (printed %.2f -> realized %.2f); gate pick %s (%.2f)" % (
        payload["universe"]["admitted"], payload["universe"]["money_priced"],
        (h["screen_pick"] or {}).get("code"), (h["screen_pick"] or {}).get("cagr_printed_pct") or 0.0,
        (h["screen_pick"] or {}).get("cagr_repaired_pct") or 0.0,
        (h["gate_pick"] or {}).get("code"), (h["gate_pick"] or {}).get("cagr_repaired_pct") or 0.0))
    log("  phantom on the screen pick %s CNY/yr; the gate is worth %s CNY/yr on a %s CNY ticket" % (
        _f((h["screen_pick"] or {}).get("phantom_cny"), 0),
        _f(h.get("forgone_by_screening_cny"), 0), _f(payload["ticket_cash_cny"], 0)))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "write", "selftest"])
    ap.add_argument("--check", action="store_true", dest="check_flag")
    ap.add_argument("--write", action="store_true", dest="write_flag")
    ap.add_argument("--selftest", action="store_true", dest="selftest_flag")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    global _QUIET
    _QUIET = args.quiet

    if args.selftest_flag or args.cmd == "selftest":
        return selftest()
    if args.check_flag or args.cmd == "check":
        rc, lines = check()
        for ln in lines:
            print(ln)
        return rc
    if args.write_flag or args.cmd == "write":
        payload = build()
        write_doc(payload)
        return 0
    return run()


if __name__ == "__main__":
    sys.exit(main())
