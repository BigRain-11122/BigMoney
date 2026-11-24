"""Does the money shelf's price accrue what the shelf says it carries?

r2050 zeroed every bar more than 1% from its own trailing median and priced the carry that
survived; r2051 measured what the band leaves behind and wrote its own blind spot into the
file.  Both read a **sum of returns**, and a sum cannot tell a fund whose price is accruing
from a fund whose price is standing above par -- worse, the 1% repair books a premium's
giveback but forgives its climb, and the money reader's share-reset rule zeroes the deepest
givebacks outright.  That is a mechanism for turning a premium into a rising line.

This face reads the LEVEL.  Per instrument, on the shelf face's own window:

  PAR FLOOR      cut the raw close into non-overlapping 250-bar blocks, take each block's 5th
                 percentile, fit a line through log(floor) against block index, annualise.
                 A premium is a minority of any 250-bar block and cannot lift its floor; a
                 price that accrues lifts every block's floor.  (The floor of a rising block
                 sits at the block's early part, biasing it LOW by about half a block of
                 accrual -- a constant, so the slope is unaffected.)  Deliberately the RAW
                 close, not the reset-corrected chain: zeroing a giveback is the illusion.

  QUIET DRIFT    median return of bars within 0.20% of their own 20-bar median (r2051's own
                 "near level" cut, reused rather than re-tuned).

  CLASS          two states, from the price alone:
                   PRICE_ACCRUES        |floor| >= 0.30 pp/yr -- the level moved, so this
                                        ruler and the shelf's carried number can be compared
                   LEVEL_DID_NOT_MOVE   everything else: the price cannot answer.  That is a
                                        limitation of a price panel, NOT a finding against the
                                        fund -- a distribution or a share count leaves it.
                 Descriptors (printed per row, never turned into a verdict): how much of the
                 window the price sits within 0.50% of its minimum, and how many single-bar
                 drops of 0.50% or more it has (distribution-sized events).

Verdicts, frozen before the first run:

  THE_CARRIED_RETURN_IS_ACCRUAL          on PRICE_ACCRUES names: median(carried - floor) < 0.30pp
  THE_CARRIED_RETURN_STILL_HOLDS_LEVEL   median gap >= 0.30pp -- the repair left a level in
  THE_FLOOR_EXCEEDS_THE_CARRIED_RETURN   median gap <= -0.30pp -- the repair charged givebacks
                                         it never forgave going up
  THE_FLOOR_CANNOT_BE_MEASURED           fewer than 5 PRICE_ACCRUES names

Tags (three-state; nothing gets a clean label it has not earned):

  THE_SHELF_PRINTS_CARRY_THE_PRICE_DID_NOT_EARN / THE_FLAT_NAMES_PRINT_NOTHING
  SOME_FLAT_NAMES_HAVE_A_DISTRIBUTION_SHAPE / NO_FLAT_NAME_SHOWS_DISTRIBUTIONS  (the shape is
      named as a question for r2047, never answered here)
  THE_TWO_RULERS_AGREE_EVERYWHERE / THE_TWO_RULERS_SPLIT (counted, never a median of a
      bimodal set -- r1313: when two pre-registered rulers disagree, print both)
  BOOK_LEGS_PRICE_CARRIES_ITS_RETURN / A_BOOK_LEG_PRINTS_CARRY_ITS_PRICE_CANNOT_SHOW

What this face does NOT claim (printed with the result, not discovered later):

  * dividends are not in the price -- r2047 owns the distribution question for the shelf legs;
  * a SHARE COUNT and a CASH DISTRIBUTION are both invisible here: when the price level did
    not move, this face has proved nothing about the fund's income, only about its price;
  * a PERMANENT relabelled par leaks into the floor (half the blocks stand higher forever);
  * 250 bars is a choice: a premium that lasts longer than a year is, to this ruler, a level;
  * an unmeasured row is "cannot answer", never zero.
"""
import hashlib
import io
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import etf_book_cash_vehicle as CV  # noqa: E402  (the published money reader)
import money_premium_carry_audit as MP  # noqa: E402  (the carry ruler and its level, r2050)

SHELF_FACE = "results/money_shelf_placement.json"
CARRY_FACE = "results/money_premium_carry_audit.json"
FACE = "results/money_accrual_rate.json"
DOC = "research/MONEY_ACCRUAL_RATE.md"

# Frozen before the first run.  See the docstring for why each number is what it is.
BLOCK_BARS = 250        # one year of sessions: a premium shorter than this cannot lift a floor
FLOOR_Q = 0.05          # the block's floor is its 5th percentile, not its mean
MIN_BLOCKS = 3          # two blocks define a line through any noise; three can disagree
MIN_BARS = 250          # the shelf face's own admission floor (r2054), reused
QUIET_BAND_PCT = 0.20   # r2051's "near level" cut, reused rather than re-tuned
CARRIER_PP = 0.30       # |floor| at or above this: the level moved, so the two rulers can talk
NEAR_FLOOR_PCT = 0.50   # "sits on its floor" = within this % of the window minimum
DROP_PCT = 0.50         # a single-bar drop this deep is distribution-sized, not accrual
AGREE_PP = 0.30         # two rulers "agree" when their annual rates are within this
FLAT_MATERIAL_PP = 0.30 # a flat-at-par name carrying this much is printing premium
REPRO_TOL_PP = 0.02     # the r2054 gate: his carried number must reproduce to this
BOOK_LEGS = ("511010", "511880", "511360")
BARS_PER_YEAR = 250.0
TICKET_CASH_KEY = "ticket_cash_cny"

MARK_BEGIN = "<!-- ACCRUAL-TABLE:BEGIN -->"
MARK_END = "<!-- ACCRUAL-TABLE:END -->"


# ------------------------------------------------------------------------ plumbing

def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load(path):
    with io.open(os.path.join(ROOT, path), "r", encoding="utf-8") as f:
        return json.load(f)


def _content_sha(obj):
    blob = json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _ann(per_bar):
    if per_bar is None:
        return None
    return round((math.exp(per_bar * BARS_PER_YEAR) - 1.0) * 100.0, 4)


def _median(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return round(float(np.median(vals)), 4)


# --------------------------------------------------------------------- measurement

def series_of(code, start, end):
    """Raw close of one instrument on the shelf face's own window."""
    px = CV.load_etf(code)
    px = px[(px.index >= pd.Timestamp(start)) & (px.index <= pd.Timestamp(end))].dropna()
    if len(px) < MIN_BARS:
        return None, len(px)
    return px.astype(float), len(px)


def floor_accrual(px):
    """Annualised slope through the 5th-percentile floor of each non-overlapping block."""
    if px is None or len(px) < BLOCK_BARS * MIN_BLOCKS:
        return None, []
    vals = px.to_numpy(dtype=float)
    blocks = []
    i = 0
    while i + BLOCK_BARS <= len(vals):
        seg = vals[i:i + BLOCK_BARS]
        blocks.append({
            "start": str(pd.Timestamp(px.index[i]).date()),
            "end": str(pd.Timestamp(px.index[i + BLOCK_BARS - 1]).date()),
            "floor": float(np.quantile(seg, FLOOR_Q)),
        })
        i += BLOCK_BARS
    if len(blocks) < MIN_BLOCKS:
        return None, blocks
    x = np.arange(len(blocks), dtype=float)
    y = np.log(np.array([b["floor"] for b in blocks], dtype=float))
    return float(np.polyfit(x, y, 1)[0]) / BLOCK_BARS, blocks


def quiet_drift(px):
    """Median return of bars that sit inside 0.20% of their own 20-bar median."""
    if px is None or len(px) < MIN_BARS:
        return None, 0
    rets = px.pct_change().fillna(0.0)
    lvl = px.rolling(MP.LEVEL_LOOKBACK, min_periods=MP.LEVEL_MIN_BARS).median()
    dev = (px / lvl - 1.0).abs() * 100.0
    quiet = rets[(dev <= QUIET_BAND_PCT).fillna(False)]
    if len(quiet) < 100:
        return None, int(len(quiet))
    return float(np.median(quiet.to_numpy(dtype=float))), int(len(quiet))


def classify(floor_pct):
    """Two states from the price alone.

    PRICE_ACCRUES means the LEVEL moved.  Everything else means the price cannot show the
    income -- which is NOT the same as the fund not earning it: a distribution, or a share
    count, leaves this panel entirely.  That difference is printed as a descriptor (how much
    of the window the price sits on its floor, how many distribution-sized drops it has),
    never as a verdict about the fund.
    """
    if floor_pct is None:
        return None
    return "PRICE_ACCRUES" if abs(floor_pct) >= CARRIER_PP else "LEVEL_DID_NOT_MOVE"


def measure_one(code, name, start, end, shelf_row):
    """One shelf instrument: where its price floor went, what the shelf prints for it."""
    px, bars = series_of(code, start, end)
    base = {"code": code, "name": name, "bars": int(bars or 0),
            "admission": shelf_row.get("admission"),
            "cagr_repaired_pct": shelf_row.get("cagr_repaired_pct"),
            "cagr_printed_pct": shelf_row.get("cagr_printed_pct"),
            "carries_return": shelf_row.get("carries_return")}
    if px is None:
        base.update({"measurable": False, "klass": None,
                     "why": "fewer than %d bars in the face's window" % MIN_BARS})
        return base
    per_bar, blocks = floor_accrual(px)
    quiet, quiet_bars = quiet_drift(px)
    lo, med, hi = float(px.min()), float(px.median()), float(px.max())
    band = (med - lo) / lo * 100.0 if lo > 0 else None
    amp = (hi - lo) / lo * 100.0 if lo > 0 else None
    rets = px.pct_change().fillna(0.0)
    near = float((px <= lo * (1.0 + NEAR_FLOOR_PCT / 100.0)).mean()) if lo > 0 else None
    drops = int((rets <= -DROP_PCT / 100.0).sum())
    floor_pct = _ann(per_bar)
    row = dict(base)
    row.update({
        "measurable": per_bar is not None,
        "blocks": len(blocks),
        "block_floors": [round(b["floor"], 4) for b in blocks],
        "floor_accrual_pct": floor_pct,
        "quiet_drift_pct": _ann(quiet),
        "quiet_bars": quiet_bars,
        "par_band_pct": None if band is None else round(band, 3),
        "amp_pct": None if amp is None else round(amp, 3),
        "near_floor_share": None if near is None else round(near, 4),
        "distribution_sized_drops": drops,
        "min_close": round(lo, 4),
        "median_close": round(med, 4),
        "max_close": round(hi, 4),
        "klass": classify(floor_pct),
    })
    if per_bar is None:
        row["why"] = "fewer than %d blocks of %d bars" % (MIN_BLOCKS, BLOCK_BARS)
    rep = row.get("cagr_repaired_pct")
    if rep is not None and floor_pct is not None:
        row["repaired_minus_floor_pp"] = round(rep - floor_pct, 4)
    if row.get("quiet_drift_pct") is not None and floor_pct is not None:
        row["quiet_minus_floor_pp"] = round(row["quiet_drift_pct"] - floor_pct, 4)
    return row


def verdict_of(gaps):
    """Mechanical verdict on the median (carried - par floor), PRICE_ACCRUES names only."""
    vals = [v for v in gaps if v is not None]
    if len(vals) < 5:
        return "THE_FLOOR_CANNOT_BE_MEASURED", _median(vals)
    med = float(np.median(vals))
    if med >= AGREE_PP:
        return "THE_CARRIED_RETURN_STILL_HOLDS_LEVEL", round(med, 4)
    if med <= -AGREE_PP:
        return "THE_FLOOR_EXCEEDS_THE_CARRIED_RETURN", round(med, 4)
    return "THE_CARRIED_RETURN_IS_ACCRUAL", round(med, 4)


def tags_of(rows, flat):
    """Three-state tags.  Counts, not medians, wherever the classes are different objects."""
    tags = []
    flat_carry = [r.get("cagr_repaired_pct") for r in flat if r.get("cagr_repaired_pct") is not None]
    flat_med = _median(flat_carry)
    printing = [r for r in flat if (r.get("cagr_repaired_pct") or 0.0) >= FLAT_MATERIAL_PP]
    tags.append({
        "tag": ("THE_SHELF_PRINTS_CARRY_THE_PRICE_DID_NOT_EARN"
                if (flat_med or 0.0) >= FLAT_MATERIAL_PP else "THE_FLAT_NAMES_PRINT_NOTHING"),
        "flat_names": len(flat), "flat_printing": len(printing),
        "flat_carried_median_pct": flat_med,
        "worst": (None if not printing else
                  max(printing, key=lambda r: r["cagr_repaired_pct"])["code"]),
        "worst_carried_pct": (None if not printing else
                              max(printing, key=lambda r: r["cagr_repaired_pct"])["cagr_repaired_pct"]),
    })
    dist = [r for r in flat if (r.get("distribution_sized_drops") or 0) >= 3]
    tags.append({"tag": ("SOME_FLAT_NAMES_HAVE_A_DISTRIBUTION_SHAPE"
                         if dist else "NO_FLAT_NAME_SHOWS_DISTRIBUTIONS"),
                 "names_with_3plus_drops": len(dist),
                 "codes": [r["code"] for r in dist][:8],
                 "owner": "r2047 (cash_shelf_total_return_audit) owns the cash-income question; "
                          "this face only says the price cannot answer it"})
    both = [r for r in flat if r.get("quiet_minus_floor_pp") is not None]
    splits = [r for r in both if abs(r["quiet_minus_floor_pp"]) >= AGREE_PP]
    if both:
        tags.append({"tag": ("THE_TWO_RULERS_SPLIT" if splits else "THE_TWO_RULERS_AGREE_EVERYWHERE"),
                     "names_compared": len(both), "names_split": len(splits),
                     "split_codes": [r["code"] for r in splits][:8]})
    else:
        tags.append({"tag": "NO_NAME_FOR_TWO_RULERS", "names_compared": 0})
    legs = {r["code"]: r for r in rows if r["code"] in BOOK_LEGS and r.get("klass")}
    legs_out = {c: {"klass": legs[c].get("klass"),
                    "floor_accrual_pct": legs[c].get("floor_accrual_pct"),
                    "cagr_repaired_pct": legs[c].get("cagr_repaired_pct")}
                for c in BOOK_LEGS if c in legs}
    aching = [c for c, v in legs_out.items() if v["klass"] != "PRICE_ACCRUES"]
    if legs_out:
        tags.append({"tag": ("A_BOOK_LEG_PRINTS_CARRY_ITS_PRICE_CANNOT_SHOW" if aching
                             else "BOOK_LEGS_PRICE_CARRIES_ITS_RETURN"),
                     "legs": legs_out, "legs_that_do_not_price": aching})
    else:
        tags.append({"tag": "NO_BOOK_LEG_MEASURED", "legs": {}})
    return tags


def build():
    shelf = _load(SHELF_FACE)
    window = shelf.get("window") or {}
    start = window.get("start") or "2020-07-16"
    end = window.get("end") or "2026-11-20"
    rows = [measure_one(r.get("code"), r.get("name"), start, end, r)
            for r in (shelf.get("rows") or []) if r.get("code")]

    measured = [r for r in rows if r.get("measurable")]
    carriers = [r for r in measured if r["klass"] == "PRICE_ACCRUES"]
    flat = [r for r in measured if r["klass"] == "LEVEL_DID_NOT_MOVE"]
    verdict, gap_med = verdict_of([r.get("repaired_minus_floor_pp") for r in carriers])
    tags = tags_of(rows, flat)

    ticket_cash = shelf.get(TICKET_CASH_KEY)
    priced = [r for r in carriers if r.get("admission") == "ADMIT"]
    best = None
    if priced:
        b = max(priced, key=lambda r: r["floor_accrual_pct"])
        best = {"code": b["code"], "name": b["name"],
                "floor_accrual_pct": b["floor_accrual_pct"],
                "cagr_repaired_pct": b.get("cagr_repaired_pct"),
                "cny_per_year_on_ticket_cash": (None if ticket_cash is None else
                                                round(ticket_cash * b["floor_accrual_pct"] / 100.0, 2)),
                "ticket_cash_cny": ticket_cash,
                "note": "the only kind of name this ruler may price: its level carries the return"}
    top_printed = max((r for r in measured if r.get("cagr_repaired_pct") is not None),
                      key=lambda r: r["cagr_repaired_pct"], default=None)
    face = {
        "schema": "money-accrual-rate/v3",
        "artifact": "money_accrual_rate",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "evidence_cutoff": end,
        "window": {"start": start, "end": end},
        "question": ("of the carry the shelf publishes, which names have a price that actually "
                     "accrued it, which have a share count this panel cannot see, and which are "
                     "printing a premium?"),
        "ruler": {
            "par_floor": ("slope of log(block 5th-percentile of the RAW close) vs block index, "
                          "annualised -- deliberately not the reset-corrected chain"),
            "quiet_drift": "median return of bars within %.2f%% of their own %d-bar median" % (
                QUIET_BAND_PCT, MP.LEVEL_LOOKBACK),
            "classes": {"PRICE_ACCRUES": "|floor| >= %.2f pp/yr -- the level moved" % CARRIER_PP,
                        "LEVEL_DID_NOT_MOVE": "everything else measurable -- the price cannot "
                                              "answer, which is not the same as the fund earning nothing"},
            "descriptors": {"near_floor_share": "share of bars within %.1f%% of the window minimum" % NEAR_FLOOR_PCT,
                            "distribution_sized_drops": "bars with a single-bar drop of %.1f%% or more" % DROP_PCT},
            "block_bars": BLOCK_BARS, "floor_q": FLOOR_Q, "min_blocks": MIN_BLOCKS,
            "agree_pp": AGREE_PP, "flat_material_pp": FLAT_MATERIAL_PP,
            "repro_tol_pp": REPRO_TOL_PP, "verdict_scope": "PRICE_ACCRUES names only",
        },
        "upstream": {
            "shelf_face": SHELF_FACE, "shelf_sha256": _sha(os.path.join(ROOT, SHELF_FACE)),
            "carry_face": CARRY_FACE, "carry_sha256": _sha(os.path.join(ROOT, CARRY_FACE)),
        },
        "universe": {"rows": len(rows), "measurable": len(measured),
                     "price_accrues": len(carriers), "level_did_not_move": len(flat)},
        "verdict": verdict,
        "median_repaired_minus_floor_pp": gap_med,
        "tags": tags,
        "headline": {
            "best_price_accruing_admitted": best,
            "top_by_carried": (None if top_printed is None else
                               {"code": top_printed["code"], "name": top_printed["name"],
                                "klass": top_printed["klass"],
                                "cagr_repaired_pct": top_printed.get("cagr_repaired_pct"),
                                "floor_accrual_pct": top_printed.get("floor_accrual_pct")}),
            "ticket_cash_cny": ticket_cash,
        },
        "not_claimed": [
            "dividends are not in the price: every number here is price-only, as the shelf's are",
            "a share count and a cash distribution are both invisible to a price panel: when the "
            "level did not move this face has proved nothing about the fund's income",
            "a PERMANENT relabelled par leaks into the floor -- half the blocks stand higher forever",
            "250 bars is a choice: a premium lasting longer than a year is a level to this ruler",
            "an unmeasured row is 'cannot answer', never zero",
        ],
        "rows": rows,
    }
    face["content_sha256"] = _content_sha({k: v for k, v in face.items() if k != "content_sha256"})
    with io.open(os.path.join(ROOT, FACE), "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    print("saved", FACE, "|", verdict, "| median", gap_med,
          "| accrues", len(carriers), "level did not move", len(flat), "of", len(rows), flush=True)
    return face


# ------------------------------------------------------------------------- rendering

def _f(v, nd=2, dash="-"):
    if v is None:
        return dash
    if isinstance(v, str):
        return v
    return ("%." + str(nd) + "f") % v


def render_table(face):
    head = ("| code | name | admission | class | blocks | par floor %/yr | quiet drift %/yr "
            "| carried %/yr | printed %/yr | carried - floor (pp) |")
    sep = "|---|---|---|---|---|---|---|---|---|---|"
    lines = [head, sep]
    order = {"PRICE_ACCRUES": 0, "LEVEL_DID_NOT_MOVE": 1}
    rows = sorted(face["rows"], key=lambda r: (r.get("klass") is None,
                                               order.get(r.get("klass"), 9),
                                               -(r.get("cagr_repaired_pct") or -99.0)))
    for r in rows:
        name = (r.get("name") or "")[:14]
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["code"], name, r.get("admission") or "-", r.get("klass") or "-",
            _f(r.get("blocks"), 0) if r.get("measurable") else "-",
            _f(r.get("floor_accrual_pct")), _f(r.get("quiet_drift_pct")),
            _f(r.get("cagr_repaired_pct")), _f(r.get("cagr_printed_pct")),
            _f(r.get("repaired_minus_floor_pp"))))
    return "\n".join(lines)


def write_doc(face):
    tag_lines = []
    for t in face["tags"]:
        extra = {k: v for k, v in t.items() if k != "tag"}
        tag_lines.append("- **%s**%s" % (t["tag"],
                                         (" · " + json.dumps(extra, ensure_ascii=False)) if extra else ""))
    best = face["headline"]["best_price_accruing_admitted"]
    best_line = ("none: no admitted name whose price accrues was measurable" if not best else
                 "%s %s par floor %.2f%%/yr (%s CNY/yr on the ticket's %s CNY cash) -- carried %.2f%%/yr"
                 % (best["code"], best["name"], best["floor_accrual_pct"],
                    best["cny_per_year_on_ticket_cash"], _f(best.get("ticket_cash_cny"), 0),
                    best.get("cagr_repaired_pct")))
    top = face["headline"]["top_by_carried"]
    top_line = ("none measured" if not top else
                "the shelf's top name by carried is **%s %s at %.2f%%/yr -- class %s, price floor %.2f%%/yr**"
                % (top["code"], top["name"], top["cagr_repaired_pct"], top["klass"],
                   top["floor_accrual_pct"]))
    u = face["universe"]
    doc = """<!-- BEGIN:MONEY-ACCRUAL-RATE -->

# does the shelf's price accrue what the shelf says it carries

generated {gen} | evidence_cutoff **{cut}** | window {ws}..{we}

r2050 zeroed every bar more than 1% from its own trailing median and priced what survived;
r2051 measured what the band leaves behind and wrote its own blind spot into the file. Both
read a **sum of returns**. A sum cannot tell a price that accrues from a price standing above
par -- and the repair that forgives a premium's climb while zeroing its giveback (or the money
reader's reset rule, which zeroes the deepest givebacks outright) manufactures a rising line.

This face reads the **level**: each raw close is cut into 250-bar blocks, each block's 5th
percentile is taken, and a line is fitted through log(floor) against block index. A premium is
a minority of any block and cannot lift its floor; accrual lifts every block's floor.

- {n} rows, **{m} measurable**: **{c} price accrues**, **{f} whose level did not move** (their
  price cannot show the income -- a distribution or a share count leaves this panel)
- verdict **{verdict}** on the accruing names only (median carried - floor = {med} pp/yr)
{tags}

## the parking number

- best admitted price-accruing name: **{best}**
- {top}

## the table

{begin}
{table}
{end}

## what this does not claim

{notc}

<!-- END:MONEY-ACCRUAL-RATE -->
""".format(
        gen=face["generated"], cut=face["evidence_cutoff"], ws=face["window"]["start"],
        we=face["window"]["end"], verdict=face["verdict"],
        med=_f(face["median_repaired_minus_floor_pp"], 4),
        n=u["rows"], m=u["measurable"], c=u["price_accrues"], f=u["level_did_not_move"],
        tags="\n".join(tag_lines), best=best_line, top=top_line,
        begin=MARK_BEGIN, table=render_table(face), end=MARK_END,
        notc="\n".join("- " + x for x in face["not_claimed"]))
    p = os.path.join(ROOT, DOC)
    existed = os.path.exists(p)
    with io.open(p, "w", encoding="utf-8") as f:
        f.write(doc)
    print("saved", DOC, "(%s, %.1f KB)" % ("rewritten" if existed else "new", len(doc) / 1024.0), flush=True)


# ----------------------------------------------------------------------------- check

def _doc_table():
    p = os.path.join(ROOT, DOC)
    if not os.path.exists(p):
        return None
    t = io.open(p, encoding="utf-8").read()
    a, b = t.find(MARK_BEGIN), t.find(MARK_END)
    if a < 0 or b < 0:
        return None
    return t[a + len(MARK_BEGIN):b].strip("\n").strip()


def check():
    """Re-derive every row from the panels; classify drift (STALE) apart from error."""
    p = os.path.join(ROOT, FACE)
    if not os.path.exists(p):
        print("check FAIL: no face at", FACE)
        return 1
    face = _load(FACE)
    shelf = _load(SHELF_FACE)
    probs, stale = [], []

    up = face.get("upstream") or {}
    for key, path in (("shelf_sha256", SHELF_FACE), ("carry_sha256", CARRY_FACE)):
        if up.get(key) != _sha(os.path.join(ROOT, path)):
            stale.append("%s moved since this face was written" % path)

    by_code = {r.get("code"): r for r in shelf.get("rows") or []}
    rows = face.get("rows") or []
    for r in rows:
        src = by_code.get(r.get("code"))
        if not src:
            stale.append("row %s is no longer on %s" % (r.get("code"), SHELF_FACE))
            continue
        gated, mine = src.get("cagr_repaired_pct"), r.get("cagr_repaired_pct")
        if gated is None or mine is None:
            if gated != mine:
                probs.append("%s: carried %r vs shelf %r" % (r.get("code"), mine, gated))
        elif abs(gated - mine) > REPRO_TOL_PP:
            probs.append("%s: carried %.4f does not reproduce the shelf's %.4f"
                         % (r.get("code"), mine, gated))

    window = face.get("window") or {}
    rebuilt = [measure_one(r["code"], r.get("name"), window.get("start"), window.get("end"),
                           by_code.get(r.get("code")) or {}) for r in rows]
    for old, new in zip(rows, rebuilt):
        for k in ("floor_accrual_pct", "quiet_drift_pct", "blocks", "measurable",
                  "klass", "par_band_pct", "amp_pct"):
            if old.get(k) != new.get(k):
                probs.append("%s: %s %r != re-derived %r" % (old.get("code"), k, old.get(k), new.get(k)))
        if old.get("block_floors") and new.get("block_floors"):
            if any(abs(a - b) > 1e-9 for a, b in zip(old["block_floors"], new["block_floors"])):
                probs.append("%s: block floors do not re-derive" % old.get("code"))

    carriers = [r for r in rebuilt if r.get("measurable") and r.get("klass") == "PRICE_ACCRUES"]
    verdict, med = verdict_of([r.get("repaired_minus_floor_pp") for r in carriers])
    if verdict != face.get("verdict"):
        probs.append("verdict %r does not re-derive (%r)" % (face.get("verdict"), verdict))
    if (med is None) != (face.get("median_repaired_minus_floor_pp") is None):
        probs.append("median presence disagrees")
    elif med is not None and abs(med - face["median_repaired_minus_floor_pp"]) > 1e-6:
        probs.append("median %.4f != re-derived %.4f" % (face["median_repaired_minus_floor_pp"], med))
    counts = {"price_accrues": len(carriers),
              "level_did_not_move": sum(1 for r in rebuilt if r.get("klass") == "LEVEL_DID_NOT_MOVE"),
              "measurable": sum(1 for r in rebuilt if r.get("measurable")),
              "rows": len(rebuilt)}
    for k, v in counts.items():
        if face["universe"].get(k) != v:
            probs.append("universe.%s %r != re-derived %r" % (k, face["universe"].get(k), v))

    doc = _doc_table()
    if doc is None:
        probs.append("doc has no %s block" % MARK_BEGIN)
    elif doc != render_table(face).strip("\n"):
        probs.append("doc table is not the face's table")

    if stale:
        print("check STALE: this face was written against inputs that have since moved:")
        for s in stale:
            print("  -", s)
        print("rerun: python scripts/money_accrual_rate.py run")
        return 3
    if probs:
        print("check FAILED:")
        for x in probs:
            print("  -", x)
        return 1
    print("check ok: %d rows (%d measurable: %d accrue / %d level did not move), verdict %s, "
          "median %s pp, doc verbatim"
          % (len(rows), counts["measurable"], counts["price_accrues"],
             counts["level_did_not_move"], verdict, med))
    return 0


# --------------------------------------------------------------------------- selftest

def _synth(kind, bars=1400, seed=11):
    """Synthetic money-fund closes, each isolating one shape the shelf ruler cannot see.

    accrue      par 100 drifting at 0.6bp/day: PRICE_ACCRUES, both rulers ~1.51%/yr
    sawtooth    par 100 accruing then resetting to par every 60 bars: LEVEL_DID_NOT_MOVE,
                and its descriptor must show the distribution-sized drops
    premia      par 100, no accrual, with 12-bar +2% premiums that come back: LEVEL_DID_NOT_MOVE,
                with a high near-floor share and no deep drops
    relabelled  par steps 100 -> 105 halfway: the floor is allowed to be fooled
    """
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2021-01-04", periods=bars)
    px = np.full(bars, 100.0)
    if kind == "accrue":
        px = 100.0 * np.exp(np.arange(bars) * 0.00006)
    elif kind == "sawtooth":
        for i in range(bars):
            px[i] = 100.0 * (1.0 + 0.00006 * (i % 60))
    elif kind == "premia":
        for s in range(30, bars - 20, 70):
            px[s:s + 12] *= 1.02
    elif kind == "relabelled":
        px = 100.0 * np.exp(np.arange(bars) * 0.00006)
        px[bars // 2:] *= 1.05
    px = px * (1.0 + rng.normal(0.0, 0.00002, bars))
    return pd.Series(px, index=dates)


def _synth_class(kind, **kw):
    px = _synth(kind, **kw)
    per_bar, _b = floor_accrual(px)
    lo, med, hi = float(px.min()), float(px.median()), float(px.max())
    band = (med - lo) / lo * 100.0
    amp = (hi - lo) / lo * 100.0
    f = _ann(per_bar)
    return f, classify(f), _ann(quiet_drift(px)[0]), band, amp


def selftest():
    legs, fails = [], []

    def leg(name, ok, detail):
        legs.append((name, ok, detail))
        if not ok:
            fails.append(name)

    f, k, q, band, amp = _synth_class("accrue")
    leg("L1 a price that accrues is priced", f is not None and abs(f - 1.51) < 0.30,
        "floor %.2f%%/yr vs truth 1.51" % f)
    leg("L1b ... and is classed PRICE_ACCRUES", k == "PRICE_ACCRUES", "%s (band %.2f%%)" % (k, band))
    leg("L1c both rulers agree on it", q is not None and abs(q - f) < 0.30, "quiet %.2f vs floor %.2f" % (q, f))

    f2, k2, _q2, band2, amp2 = _synth_class("sawtooth")
    leg("L2 a sawtooth is not called accrual", k2 == "LEVEL_DID_NOT_MOVE",
        "%s (floor %.2f%%, band %.2f%%, amp %.2f%%)" % (k2, f2, band2, amp2))

    f3, k3, _q3, band3, amp3 = _synth_class("premia")
    leg("L3 premium spikes around par did not move the level", k3 == "LEVEL_DID_NOT_MOVE",
        "%s (floor %.2f%%, band %.2f%%, amp %.2f%%)" % (k3, f3, band3, amp3))
    leg("L3b the floor reads ~zero on it", f3 is not None and abs(f3) < 0.30, "floor %.2f%%/yr" % f3)

    # L4 the repair shape that manufactures the illusion: forgive the climb, zero the giveback
    bars = 1400
    rets = np.zeros(bars)
    for s in range(30, bars - 40, 70):
        rets[s:s + 3] += 0.004        # each bar INSIDE the 1% band
        rets[s + 3] -= 0.012          # the giveback, one bar beyond it
    honest = (math.exp(float(np.log1p(rets).sum()) * BARS_PER_YEAR / bars) - 1.0) * 100.0
    zeroed = np.where(np.abs(rets) > 0.01, 0.0, rets)
    illusory = (math.exp(float(np.log1p(zeroed).sum()) * BARS_PER_YEAR / bars) - 1.0) * 100.0
    leg("L4 forgiving the giveback prints an accrual that is not there",
        abs(honest) < 0.5 and illusory > honest + 1.0,
        "honest %.2f%%/yr vs repaired %.2f%%/yr on the same price" % (honest, illusory))

    # L5 a permanent relabelling leaks (printed limitation, asserted so it stays true)
    f5, _k5, _q5, _b5, _a5 = _synth_class("relabelled")
    leg("L5 a permanent relabelling leaks into the floor (documented)",
        f5 is not None and abs(f5) > 1.0, "floor %.2f%%/yr with one +5%% step" % f5)

    # L6 too few blocks is 'cannot answer', not zero
    short = _synth("accrue", bars=400)
    per_bar, blocks = floor_accrual(short)
    leg("L6 fewer than %d blocks is unmeasurable" % MIN_BLOCKS,
        per_bar is None and len(blocks) < MIN_BLOCKS, "bars 400 -> %d blocks" % len(blocks))

    # L7 verdict branches
    v1, _ = verdict_of([0.0, 0.05, 0.1, 0.2, 0.25])
    v2, _ = verdict_of([0.6, 0.8, 1.2, 0.9, 2.0])
    v3, _ = verdict_of([-0.6, -0.4, -1.2, -0.9, -2.0])
    v4, _ = verdict_of([0.1, 0.2])
    leg("L7 verdict branches", (v1, v2, v3, v4) == ("THE_CARRIED_RETURN_IS_ACCRUAL",
                                                    "THE_CARRIED_RETURN_STILL_HOLDS_LEVEL",
                                                    "THE_FLOOR_EXCEEDS_THE_CARRIED_RETURN",
                                                    "THE_FLOOR_CANNOT_BE_MEASURED"),
        "%s / %s / %s / %s" % (v1, v2, v3, v4))

    # L8 tags: a flat name printing carry is named; a non-accruing book leg blocks the clean tag
    rows = [
        {"code": "511010", "klass": "PRICE_ACCRUES", "floor_accrual_pct": 2.5,
         "cagr_repaired_pct": 2.4, "quiet_minus_floor_pp": 0.0},
        {"code": "511880", "klass": "LEVEL_DID_NOT_MOVE", "floor_accrual_pct": 0.0,
         "cagr_repaired_pct": 1.5, "quiet_minus_floor_pp": 1.5, "distribution_sized_drops": 6},
        {"code": "511360", "klass": "LEVEL_DID_NOT_MOVE", "floor_accrual_pct": 0.0,
         "cagr_repaired_pct": 2.3, "quiet_minus_floor_pp": 2.3, "distribution_sized_drops": 0},
    ]
    flat = [r for r in rows if r["klass"] == "LEVEL_DID_NOT_MOVE"]
    names = [t["tag"] for t in tags_of(rows, flat)]
    leg("L8 flat names printing carry are named",
        "THE_SHELF_PRINTS_CARRY_THE_PRICE_DID_NOT_EARN" in names, str(names))
    leg("L8b a non-accruing book leg blocks the clean tag",
        "A_BOOK_LEG_PRINTS_CARRY_ITS_PRICE_CANNOT_SHOW" in names
        and "BOOK_LEGS_PRICE_CARRIES_ITS_RETURN" not in names, str(names))
    leg("L8c the rulers are split, and it is counted not averaged",
        "THE_TWO_RULERS_SPLIT" in names, str(names))

    # L9 determinism
    a, b = _synth("accrue"), _synth("accrue")
    leg("L9 two runs agree", _ann(floor_accrual(a)[0]) == _ann(floor_accrual(b)[0]),
        "%r" % (_ann(floor_accrual(a)[0]),))

    # L10 the published face is self-consistent and its doc is its own table
    p = os.path.join(ROOT, FACE)
    if os.path.exists(p):
        face = _load(FACE)
        med = face.get("median_repaired_minus_floor_pp")
        v, m2 = verdict_of([r.get("repaired_minus_floor_pp") for r in face.get("rows") or []
                            if r.get("measurable") and r.get("klass") == "PRICE_ACCRUES"])
        leg("L10 published verdict is the arithmetic of its accruing names",
            v == face.get("verdict") and (m2 is None or med is None or abs(m2 - med) < 1e-9),
            "%s / %s vs %s" % (v, m2, med))
        leg("L10b every unmeasurable row says why and carries no class",
            all(r.get("why") and r.get("klass") is None for r in (face.get("rows") or [])
                if not r.get("measurable")), "ok")
        leg("L10c doc table is the face's table", _doc_table() == render_table(face).strip("\n"),
            "verbatim")
    else:
        leg("L10 face present", True, "skipped (no face yet)")

    print("selftest: %d/%d PASS" % (len(legs) - len(fails), len(legs)))
    for name, ok, detail in legs:
        print("  [%s] %s -- %s" % ("PASS" if ok else "FAIL", name, detail))
    return 0 if not fails else 1


def run():
    face = build()
    write_doc(face)
    return 0


def main(argv):
    cmd = (argv[1].lstrip("-") if len(argv) > 1 else "run")
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        return run()
    print("usage: money_accrual_rate.py run|check|selftest")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
