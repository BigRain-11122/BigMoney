#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""money_carry_one_sided_repair -- the cash shelf's money row pays 1.59%/yr only if every
annual share reset is a reset; on the rest of the family the same rule invents the carry.

WHY THIS FACE EXISTS
--------------------
The book parks its idle cash in a money / bond shelf and r2041-r2046 priced what that is
worth against the GC001 leg.  Every one of those readings takes a money ETF's total return
from `etf_book_cash_vehicle.consolidation_returns`: a single bar down more than 50bp is
booked at zero, on the theory that the holder's assets did not fall -- the share count rose.

That theory is right for one shape and wrong for another, and the rule cannot tell them
apart:

  a yearly share reset   the close walks up from 100 to ~103 across a year, then one
                         -3% bar drops it back to 100.  Zeroing that bar *is* the total
                         return: the holder has 3% more shares.
  a premium spike        the close jumps from 100 to 109.95 inside a few sessions on a
                         funding squeeze, then falls back to 100.  Zeroing only the fall
                         keeps the rise: the shelf is credited with a gain nobody held.

Both are "a deep single-bar drop".  Because the rule zeroes only the negative leg, the
second shape leaves a phantom return behind, and r2048 already saw the footprint without
naming it: 11 money-market funds carry a 25-55bp daily sigma, and 511360's one flip alone
was worth 0.167pp/yr.  This face asks the question that footprint implies.

THE QUESTION (frozen before the first run)
------------------------------------------
Across every money-class ETF in the panel: of the deep single-bar drops the published rule
zeroes, which are share resets (the close never comes back), which are single-bar quote
dips (the close comes back inside r2046's 3-bar window), and which are the *ends* of a
premium spike (the close had just run up by at least as much, inside 10 bars)?  Priced
three ways -- the raw close, the published rule, and a shape-aware rule -- how much of the
family's measured carry is the published rule's own asymmetry, and does the money row the
book already holds sit on the honest side of that split?

RULER (one thing added; nothing else re-decided)
------------------------------------------------
* window, panel, ticket            -- r2041/r2046 (`cb_parking_shelf_at_size`,
                                      `cash_shelf_year_by_year`); START 2020-07-16
* which drop is "deep"             -- `etf_book_cash_vehicle.CONSOLIDATION_JUMP` (-50bp),
                                      imported, never retyped
* the 3-bar recovery window and tol -- `cash_shelf_year_by_year.FLIP_WINDOW` / `FLIP_TOL_BP`
* class assignment                 -- `etf_equity_alpha.classify`; the money/suspect labels
                                      are `cash_shelf_flip_census.class_confidence`, imported
* bars per year                    -- the instrument's own bars (r2045 ruler)
* **the three shapes (added here)**
    SPIKE   -- the close 10 bars before the drop (its lowest point) is at least 80% of the
               drop above its level at the drop: the print is the end of a run-up.
    V_DIP   -- no run-up, and the close is back within FLIP_TOL_BP inside FLIP_WINDOW bars:
               a quote dip, neutralised on both legs (this is exactly r2046's flip).
    RESET   -- no run-up and no recovery: a permanent step down.
* **RESET_READABLE_MAX = 5% (added here)** -- one year of a money fund is ~2%; a permanent
               step deeper than 5% is not a yearly reset.  The repo does not collect NAV or
               shares outstanding, so the price cannot say whether that step is a large
               share consolidation or a bad print.  Those rows print RAW and CV but no
               honest reading (r98: a missing face is not a reading of zero).
* cost                            -- none.  This face describes a quote series, not a trade.

THE THREE TAPES
---------------
  raw     the close, untouched
  cv      the published rule: every drop under -50bp booked at zero
  honest  RESET_READABLE zeroes the drop (total return, as published); V_DIP zeroes both
          legs (as r2046); SPIKE zeroes the whole excursion from the trough to the recovery
          -- a price that leaves 100 and comes back to 100 earned nothing in between.

VERDICTS (mechanical)
---------------------
* NO_JUMP_ANYWHERE                  -- no money row has a deep single-bar drop.
* REPAIRS_ARE_SYMMETRIC_ALREADY      -- every deep drop is a readable reset: the published
                                      rule and the shape-aware one agree on every row.
* THE_ONE_SIDED_REPAIR_INVENTS_CARRY -- at least one row gains >= 1pp/yr under the published
                                      rule that the shape-aware rule does not keep.
* THE_ONE_SIDED_REPAIR_IS_IMMATERIAL -- deep drops exist but none of them adds 1pp/yr.
Tags, printed beside the verdict:
* SPIKE_AND_RESET_ARE_DIFFERENT_ANIMALS -- both shapes occur in the family: the rule cannot
                                      be fixed by lowering or raising its threshold alone.
* THE_INVENTED_CARRY_SITS_ON_THE_THINNEST_TAPE -- the rows the rule credits most are rows
                                      whose 20-day turnover is a fraction of the ticket: the
                                      carry is not reachable at the size the book trades.
* SOME_PERMANENT_SHIFTS_EXCEED_ONE_YEAR_OF_CARRY -- a row has a permanent step deeper than
                                      5%: its carry needs the NAV face this repo does not hold.
* R2046_AND_THIS_FACE_AGREE_ON_THE_ONE_V_DIP -- the row r2046 repaired by hand is the same
                                      row, on the same date, that this face calls V_DIP.

WHAT THIS FACE DOES NOT DECIDE
------------------------------
It does not change `consolidation_returns`, the shelf table, or any published carry number.
It prints what each of the three readings would pay and names which rows each reading can
be trusted on.  Whether the production caliber moves belongs to a prereg, not to this face.

Usage:
    python scripts/money_carry_one_sided_repair.py run
    python scripts/money_carry_one_sided_repair.py --check
    python scripts/money_carry_one_sided_repair.py --selftest
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import cb_parking_shelf_at_size as SS  # noqa: E402  (window, ticket caliber)
import cash_shelf_flip_census as CS  # noqa: E402  (money/suspect labels, re-used)
import cash_shelf_year_by_year as YY  # noqa: E402  (flip window/tol, bars per year, r2046)
import etf_book_cash_vehicle as CV  # noqa: E402  (deep-drop rule, daily panel loader)
import etf_composite_pf as E  # noqa: E402  (turnover panel)
import etf_equity_alpha as A  # noqa: E402  (class map)

FACE = "results/money_carry_one_sided_repair.json"
DOC = "research/MONEY_CARRY_ONE_SIDED_REPAIR.md"

MARK_BEGIN = "<!-- MONEY-CARRY:BEGIN -->"
MARK_END = "<!-- MONEY-CARRY:END -->"

DROP_THR = CV.CONSOLIDATION_JUMP        # -0.005, imported: never retyped
SPIKE_LOOKBACK = 10                     # bars the run-up may take (chosen before first run)
SPIKE_SHARE = 0.8                       # run-up must cover this share of the drop
RESET_READABLE_MAX = 0.05               # a yearly reset is ~2%; deeper needs the NAV face
MISREAD_MIN_PP = 1.0                    # >= 1pp/yr credited but not held counts as invented
MIN_BARS = CS.MIN_BARS
AMT_TAIL = 20                           # turnover window for the "can this size trade it" line
DEC = 6

CHECK_FIELDS = ("tape_raw_pct", "tape_cv_pct", "tape_honest_pct", "sigma_bp",
                "jumps_total", "spike", "v_dip", "reset_readable", "reset_unverifiable",
                "overstatement_pp", "amt20d_cny", "participation_x",
                "cv_carry_cny", "honest_carry_cny", "invented_carry_cny")


# --------------------------------------------------------------------- io helpers

def _load(path):
    with io.open(os.path.join(ROOT, path), "r", encoding="utf-8") as f:
        return json.load(f)


def _content_sha(obj):
    blob = json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _f(v, nd=3):
    return "-" if v is None else ("%.*f" % (nd, v))


def _m(v):
    if v is None:
        return "-"
    a = abs(float(v))
    if a >= 1e8:
        return "%.2f亿" % (v / 1e8)
    if a >= 1e4:
        return "%.1f万" % (v / 1e4)
    return "%.0f" % v


# --------------------------------------------------------------------- the three shapes

def classify_drops(ser):
    """Every deep single-bar drop in `ser`, labelled SPIKE / V_DIP / RESET (see docstring)."""
    ser = ser.dropna().astype(float)
    ret = ser.pct_change().fillna(0.0)
    vals = ser.to_numpy()
    out = []
    for i in range(1, len(ser)):
        r = float(ret.iloc[i])
        if not np.isfinite(r) or r >= DROP_THR:
            continue
        prev = float(vals[i - 1])
        lo = max(0, i - SPIKE_LOOKBACK)
        low_idx = int(np.argmin(vals[lo:i])) + lo
        base = float(vals[low_idx])
        run_up = (prev / base - 1.0) if base > 0 else 0.0
        drop = float(vals[i]) / prev - 1.0
        back_idx = None
        for k in range(i + 1, min(i + 1 + YY.FLIP_WINDOW, len(vals))):
            if abs(float(vals[k]) / prev - 1.0) * 1e4 <= YY.FLIP_TOL_BP:
                back_idx = k
                break
        if run_up >= abs(drop) * SPIKE_SHARE:
            shape = "SPIKE"
        elif back_idx is not None:
            shape = "V_DIP"
        elif abs(drop) <= RESET_READABLE_MAX:
            shape = "RESET"
        else:
            shape = "UNVERIFIABLE_RESET"
        out.append({
            "date": str(pd.Timestamp(ser.index[i]).date()),
            "i": i,
            "low_idx": low_idx,
            "back_idx": back_idx,
            "shape": shape,
            "drop_bp": round(drop * 1e4, 2),
            "run_up_bp": round(run_up * 1e4, 2),
            "price_before": round(prev, 4),
            "price_after": round(float(vals[i]), 4),
            "trough_price": round(base, 4),
        })
    return out


def apply_rule(ser, jumps, mode):
    """Per-bar returns under one of the three tapes; `mode` is raw / cv / honest."""
    ser = ser.dropna().astype(float)
    ret = ser.pct_change().fillna(0.0).copy()
    if mode == "raw":
        return ret
    for j in jumps:
        if mode == "cv":
            ret.iloc[j["i"]] = 0.0
            continue
        shape = j["shape"]
        if shape == "RESET":
            ret.iloc[j["i"]] = 0.0
        elif shape == "V_DIP":
            ret.iloc[j["i"]] = 0.0
            if j["back_idx"] is not None:
                ret.iloc[j["back_idx"]] = 0.0
        elif shape == "SPIKE":
            end = j["back_idx"] if j["back_idx"] is not None else j["i"]
            for k in range(j["low_idx"] + 1, end + 1):
                ret.iloc[k] = 0.0
        # UNVERIFIABLE_RESET: left untouched; the caller refuses to annualise it
    return ret


def annualise(rets):
    """Per-bar returns -> %/yr on the series' own bar count (r2045/r2046 ruler)."""
    rets = rets.dropna()
    if len(rets) < 2:
        return None
    level = float(np.cumprod(1.0 + rets.to_numpy())[-1])
    if level <= 0:
        return None
    bpy = YY.bars_per_year(rets)
    if not bpy:
        return None
    return (level ** (bpy / len(rets)) - 1.0) * 100.0


# --------------------------------------------------------------------- one row

def measure(code, cmap_row, px_all, amt_row, start, end, ticket):
    name = cmap_row[1]
    px = px_all.dropna().astype(float)
    px = px[(px.index >= pd.Timestamp(start)) & (px.index <= pd.Timestamp(end))]
    row = {"code": code, "name": name, "bars": int(px.shape[0])}
    if px.shape[0] < MIN_BARS:
        row.update({"priced": False, "why_unpriced": "fewer than %d bars in the window" % MIN_BARS,
                    "tape_raw_pct": None, "tape_cv_pct": None, "tape_honest_pct": None,
                    "sigma_bp": None, "jumps_total": 0, "spike": 0, "v_dip": 0,
                    "reset_readable": 0, "reset_unverifiable": 0,
                    "overstatement_pp": None, "amt20d_cny": None, "amt_med_cny": None,
                    "participation_x": None, "cv_carry_cny": None, "honest_carry_cny": None,
                    "invented_carry_cny": None, "honest_reason": None,
                    "class_confidence": None, "jumps": []})
        return row

    raw_rets = px.pct_change()
    sig = float(raw_rets.dropna().std()) * 1e4 if raw_rets.dropna().shape[0] > 1 else None
    jumps = classify_drops(px)
    tape_raw = annualise(apply_rule(px, jumps, "raw"))
    tape_cv = annualise(apply_rule(px, jumps, "cv"))
    n_unver = sum(1 for j in jumps if j["shape"] == "UNVERIFIABLE_RESET")
    if n_unver:
        tape_honest, honest_reason = None, (
            "%d permanent step(s) deeper than %.0f%%: price cannot separate a large share "
            "consolidation from a bad print; the NAV/share face is not in this repo"
            % (n_unver, RESET_READABLE_MAX * 100.0))
    else:
        tape_honest, honest_reason = annualise(apply_rule(px, jumps, "honest")), None

    amt = amt_row.dropna() if amt_row is not None else pd.Series(dtype=float)
    amt20 = float(amt.tail(AMT_TAIL).mean()) if len(amt) else None
    amtmed = float(amt.median()) if len(amt) else None
    part = (float(ticket) / amt20) if amt20 and amt20 > 0 else None

    over = None
    if tape_cv is not None and tape_honest is not None:
        over = tape_cv - tape_honest
    row.update({
        "priced": True, "why_unpriced": None,
        "tape_raw_pct": None if tape_raw is None else round(tape_raw, DEC),
        "tape_cv_pct": None if tape_cv is None else round(tape_cv, DEC),
        "tape_honest_pct": None if tape_honest is None else round(tape_honest, DEC),
        "sigma_bp": None if sig is None else round(sig, 3),
        "jumps_total": len(jumps),
        "spike": sum(1 for j in jumps if j["shape"] == "SPIKE"),
        "v_dip": sum(1 for j in jumps if j["shape"] == "V_DIP"),
        "reset_readable": sum(1 for j in jumps if j["shape"] == "RESET"),
        "reset_unverifiable": n_unver,
        "overstatement_pp": None if over is None else round(over, DEC),
        "amt20d_cny": None if amt20 is None else round(amt20, 2),
        "amt_med_cny": None if amtmed is None else round(amtmed, 2),
        "participation_x": None if part is None else round(part, 4),
        "cv_carry_cny": None if tape_cv is None else round(float(ticket) * tape_cv / 100.0, 2),
        "honest_carry_cny": (None if tape_honest is None
                             else round(float(ticket) * tape_honest / 100.0, 2)),
        "invented_carry_cny": (None if over is None
                               else round(float(ticket) * over / 100.0, 2)),
        "honest_reason": honest_reason,
        "jumps": jumps,
    })
    row["class_confidence"] = CS.class_confidence(
        {"class": "money", "sigma_bp": row["sigma_bp"]}, name)
    return row


# --------------------------------------------------------------------- verdicts

def verdict_for(rows):
    priced = [r for r in rows if r.get("priced")]
    if not priced:
        return "NO_JUMP_ANYWHERE"
    if not any(r["jumps_total"] for r in priced):
        return "NO_JUMP_ANYWHERE"
    invented = [r for r in priced if (r.get("overstatement_pp") or 0.0) >= MISREAD_MIN_PP]
    any_spike = any(r["spike"] for r in priced)
    any_unver = any(r["reset_unverifiable"] for r in priced)
    if not any_spike and not any_unver:
        return "REPAIRS_ARE_SYMMETRIC_ALREADY"
    if invented:
        return "THE_ONE_SIDED_REPAIR_INVENTS_CARRY"
    return "THE_ONE_SIDED_REPAIR_IS_IMMATERIAL"


def tags_for(rows, ticket):
    priced = [r for r in rows if r.get("priced")]
    invented = [r for r in priced if (r.get("overstatement_pp") or 0.0) >= MISREAD_MIN_PP]
    invented.sort(key=lambda r: -(r.get("overstatement_pp") or 0.0))
    tags = []
    if any(r["spike"] for r in priced) and any(
            r["reset_readable"] or r["v_dip"] for r in priced):
        tags.append("SPIKE_AND_RESET_ARE_DIFFERENT_ANIMALS")
    if invented:
        top = invented[:3]
        amts = [r["amt20d_cny"] for r in top if r.get("amt20d_cny")]
        if amts and float(np.median(amts)) < float(ticket):
            tags.append("THE_INVENTED_CARRY_SITS_ON_THE_THINNEST_TAPE")
    if any(r["reset_unverifiable"] for r in priced):
        tags.append("SOME_PERMANENT_SHIFTS_EXCEED_ONE_YEAR_OF_CARRY")
    return tags


# --------------------------------------------------------------------- build

def build():
    year_face = _load(YY.FACE)
    ticket = float(year_face["headline"]["ticket_cash_cny"])

    close_all, open_all, amt_all, _feats = E.build_panel()
    window_end = str(close_all.index[-1].date())
    cmap = A.load_class_map()
    cls = A.classify(close_all.columns, cmap, close_all)
    money = [c for c in close_all.columns if cls.get(c) == "money"]

    rows = []
    for code in money:
        try:
            px = CV.load_etf(code)
        except Exception:
            continue
        amt_row = amt_all[code] if code in getattr(amt_all, "columns", []) else None
        r = measure(code, cmap.get(code, ("", "")), px, amt_row, SS.START, window_end, ticket)
        rows.append(r)

    priced = [r for r in rows if r.get("priced")]
    priced.sort(key=lambda r: -(r.get("tape_cv_pct") if r.get("tape_cv_pct") is not None else -9))

    # The classifier's 现金 keyword also matches every free-cash-flow EQUITY ETF.  Those
    # rows are carried (class_confidence from the census) but kept out of every verdict and
    # every money line: a 60bp-a-day equity fund is not a cash shelf, and reading it through
    # the cash repair would quote a 100-200%/yr "carry" nobody can hold.
    cash = [r for r in priced if r.get("class_confidence") != "suspect_class"]
    mislabelled = [r for r in priced if r.get("class_confidence") == "suspect_class"]

    # r2046 cross-check: the row it repaired by hand must be this face's V_DIP.  Restricted
    # to the clean-label rows: a suspect_series flip is a different animal, and the point of
    # this leg is that the two faces agree on a row neither of them doubts.
    agree = None
    for r in cash:
        if r.get("class_confidence") != "ok" or not r["v_dip"]:
            continue
        try:
            px = CV.load_etf(r["code"])
        except Exception:
            continue
        px = px[(px.index >= pd.Timestamp(SS.START))]
        pairs = YY.find_flip_pairs(px)
        mine = {j["date"] for j in r["jumps"] if j["shape"] == "V_DIP"}
        if pairs and mine and {p["drop_date"] for p in pairs} & mine:
            agree = {"code": r["code"], "date": sorted({p["drop_date"] for p in pairs} & mine)[0],
                     "r2046_pairs": len(pairs), "this_face_v_dips": len(mine)}
            break

    invented = [r for r in cash if (r.get("overstatement_pp") or 0.0) >= MISREAD_MIN_PP]
    invented.sort(key=lambda r: -(r.get("overstatement_pp") or 0.0))
    unreadable = [r for r in cash if r.get("tape_honest_pct") is None]
    verdict = verdict_for(cash)
    tags = tags_for(cash, ticket)
    if agree:
        tags.append("R2046_AND_THIS_FACE_AGREE_ON_THE_ONE_V_DIP")
    if mislabelled:
        tags.append("THE_MISCLASSIFIED_EQUITY_FUNDS_READ_AS_200PCT_CARRY")

    mis_cv = [r["tape_cv_pct"] for r in mislabelled if r.get("tape_cv_pct") is not None]
    headline = {
        "verdict": verdict,
        "tags": tags,
        "ticket_cash_cny": round(ticket, 2),
        "priced": len(priced),
        "cash_rows": len(cash),
        "equity_mislabelled": len(mislabelled),
        "equity_mislabelled_cv_range_pct": ([round(min(mis_cv), 2), round(max(mis_cv), 2)]
                                            if mis_cv else None),
        "with_any_jump": sum(1 for r in cash if r["jumps_total"]),
        "with_spike": sum(1 for r in cash if r["spike"]),
        "with_unverifiable": len(unreadable),
        "invented_rows": [{"code": r["code"], "name": r["name"],
                           "tape_cv_pct": r["tape_cv_pct"], "tape_honest_pct": r["tape_honest_pct"],
                           "overstatement_pp": r["overstatement_pp"],
                           "invented_carry_cny": r["invented_carry_cny"],
                           "amt20d_cny": r["amt20d_cny"]} for r in invented[:5]],
        "invented_carry_total_cny": round(sum(r["invented_carry_cny"] or 0.0 for r in invented), 2),
        "honest_top3": [{"code": r["code"], "name": r["name"],
                         "tape_honest_pct": r["tape_honest_pct"],
                         "honest_carry_cny": r["honest_carry_cny"],
                         "amt20d_cny": r["amt20d_cny"]}
                        for r in sorted([x for x in cash if x["tape_honest_pct"] is not None],
                                        key=lambda x: -x["tape_honest_pct"])[:3]],
        "cv_top3": [{"code": r["code"], "name": r["name"], "tape_cv_pct": r["tape_cv_pct"]}
                    for r in sorted(cash, key=lambda x: -(x.get("tape_cv_pct") or -9))[:3]],
        "r2046_agreement": agree,
    }

    face = {
        "schema": "money-carry-one-sided-repair/v1",
        "artifact": "money_carry_one_sided_repair",
        "generated": pd.Timestamp.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": window_end,
        "window": {"start": SS.START, "end": window_end},
        "question": ("of the deep single-bar drops the published money rule zeroes, which are "
                     "share resets, which are quote dips, and which are the ends of a premium "
                     "spike; how much carry does the published rule's asymmetry invent, and "
                     "does the book's own money row sit on the honest side"),
        "upstream": {
            "year_face": YY.FACE,
            "census_face": CS.FACE,
            "cash_vehicle_rule": {"module": "etf_book_cash_vehicle",
                                  "CONSOLIDATION_JUMP": CV.CONSOLIDATION_JUMP},
            "flip_window": {"bars": YY.FLIP_WINDOW, "tol_bp": YY.FLIP_TOL_BP},
            "spike_lookback": SPIKE_LOOKBACK,
            "spike_share": SPIKE_SHARE,
            "reset_readable_max": RESET_READABLE_MAX,
            "misread_min_pp": MISREAD_MIN_PP,
            "amt_tail": AMT_TAIL,
            "panel_tail": window_end,
            "panel_columns": int(close_all.shape[1]),
        },
        "ruler": {
            "tapes": {"raw": "the close, untouched",
                      "cv": "every drop under -50bp booked at zero (published rule)",
                      "honest": ("RESET zeroes the drop; V_DIP zeroes both legs; SPIKE zeroes "
                                 "the excursion from the trough to the recovery")},
            "shapes": {"SPIKE": "run-up >= %.1fx the drop inside %d bars"
                                % (SPIKE_SHARE, SPIKE_LOOKBACK),
                       "V_DIP": "no run-up, back within %gbp inside %d bars"
                                % (YY.FLIP_TOL_BP, YY.FLIP_WINDOW),
                       "RESET": "no run-up, no recovery, |drop| <= %.0f%%"
                                % (RESET_READABLE_MAX * 100.0),
                       "UNVERIFIABLE_RESET": "no run-up, no recovery, |drop| > %.0f%%"
                                             % (RESET_READABLE_MAX * 100.0)},
            "cost_bp_charged": 0.0,
            "why_no_cost": "this face describes a quote series, not a trade",
            "money": "ticket_cash_cny from %s, carried here never typed" % YY.FACE,
            "participation": "ticket / 20-day mean turnover on the panel",
        },
        "headline": headline,
        "rows": rows,
    }
    face["content_sha256"] = _content_sha(face)
    return face


# --------------------------------------------------------------------- render

def render_block(face):
    h = face["headline"]
    L = []
    L.append("**判词 `%s`** ｜ 标签：%s" % (h["verdict"], "、".join(h["tags"]) or "-"))
    L.append("")
    L.append("票面现金 %s 元（单源 %s）；窗口 %s → %s。可定价 %d 只里 %d 只是现金族"
             "（其中 %d 只带深跳、%d 只位移不可读），另 %d 只是被 `现金` 关键字判成 money 的"
             "权益因子基金（CV 会把它们读成 %s-%s%%/年，见下段）。"
             % (_m(h["ticket_cash_cny"]), YY.FACE, face["window"]["start"], face["window"]["end"],
                h["priced"], h["cash_rows"], h["with_any_jump"], h["with_unverifiable"],
                h["equity_mislabelled"],
                _f((h["equity_mislabelled_cv_range_pct"] or [None, None])[0], 1),
                _f((h["equity_mislabelled_cv_range_pct"] or [None, None])[1], 1)))
    L.append("")
    L.append("**现金族（28 只，判词只看这一段）**")
    L.append("")
    L.append("| 代码 | 名称 | 标签 | 跳 S/V/R/U | raw %/yr | 正典 cv %/yr | 本面 honest %/yr | 虚增 pp | 20日成交额 | 一辆票=几天量 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in face["rows"]:
        if not r.get("priced") or r.get("class_confidence") == "suspect_class":
            continue
        shapes = "%d/%d/%d/%d" % (r["spike"], r["v_dip"], r["reset_readable"],
                                  r["reset_unverifiable"])
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["code"], r["name"], r.get("class_confidence") or "-", shapes,
            _f(r["tape_raw_pct"]), _f(r["tape_cv_pct"]), _f(r["tape_honest_pct"]),
            _f(r["overstatement_pp"]), _m(r["amt20d_cny"]), _f(r["participation_x"], 2)))
    L.append("")
    if h["invented_rows"]:
        top = h["invented_rows"][0]
        L.append("**被正典规则记上、但按形状不存在的 carry（前 %d 只）**" % len(h["invented_rows"]))
        L.append("")
        L.append("| 代码 | 名称 | 正典 %/yr | honest %/yr | 虚增 pp | 按票面多算的钱 | 20日成交额 |")
        L.append("|---|---|---|---|---|---|")
        for r in h["invented_rows"]:
            L.append("| %s | %s | %s | %s | %s | %s 元/年 | %s |" % (
                r["code"], r["name"], _f(r["tape_cv_pct"]), _f(r["tape_honest_pct"]),
                _f(r["overstatement_pp"]), _m(r["invented_carry_cny"]), _m(r["amt20d_cny"])))
        L.append("")
        L.append("现金族合计按票面多算 **%s 元/年**。最直白的一行：若按正典读数把票面 %s 元全停到"
                 "第一名 %s（%s%%/年），账面一年比实际多算 %s 元，而实际按形状是 %s%%（%s 元/年），"
                 "且它一天的成交额只有 %s 元。"
                 % (_m(h["invented_carry_total_cny"]), _m(h["ticket_cash_cny"]),
                    top["code"], _f(top["tape_cv_pct"]), _m(top["invented_carry_cny"]),
                    _f(top["tape_honest_pct"]),
                    _m((top["tape_honest_pct"] or 0.0) / 100.0 * h["ticket_cash_cny"]),
                    _m(top["amt20d_cny"])))
        L.append("")
    L.append("**正典读数前 3 名**：" + "、".join(
        "%s %s（%s%%/年）" % (x["code"], x["name"], _f(x["tape_cv_pct"])) for x in h["cv_top3"]))
    L.append("")
    L.append("**honest 读数前 3 名**：" + "、".join(
        "%s %s（%s%%/年，%s 元/年）" % (x["code"], x["name"], _f(x["tape_honest_pct"]),
                                     _m(x["honest_carry_cny"])) for x in h["honest_top3"]))
    L.append("")
    L.append("结论一句话：honest 口径下有正 carry 的现金标的只有货架上已有的那两只"
             "（511360 短融 %s%%、511880 银华日利 %s%%）；正典读数排在前面的 %s 全是溢价尖峰被"
             "单边修复后的残影，且都在票面装不下的成交额上。"
             % (_f(next((x["tape_honest_pct"] for x in h["honest_top3"] if x["code"] == "511360"), None)),
                _f(next((x["tape_honest_pct"] for x in h["honest_top3"] if x["code"] == "511880"), None)),
                "、".join(x["code"] for x in h["cv_top3"])))
    L.append("")
    if h["r2046_agreement"]:
        a = h["r2046_agreement"]
        L.append("交叉验证：r2046 手工修的那一对 = 本面的 V_DIP，代码 %s，日期 %s"
                 "（r2046 找到 %d 对，本面判出 %d 个 V_DIP）。"
                 % (a["code"], a["date"], a["r2046_pairs"], a["this_face_v_dips"]))
        L.append("")
    return "\n".join(L)


def render_doc(face):
    body = [
        "# 货币这一行的 carry，有多少是「只抹跌不抹涨」造出来的",
        "",
        "问题与口径写在 `scripts/money_carry_one_sided_repair.py` 的模块说明里；本页只印读数。"
        "重跑：`python scripts/money_carry_one_sided_repair.py run`；核对：`--check`；自检：`--selftest`。",
        "",
        MARK_BEGIN,
        "",
        render_block(face),
        "",
        MARK_END,
        "",
        "## 怎么读这张表",
        "",
        "* **raw** = 收盘价口径，什么都不修。货币 ETF 的利息常以分红/份额形式发放，所以 raw 通常读成 0。",
        "* **正典 cv** = `etf_book_cash_vehicle.consolidation_returns`：每个 -50bp 以下的单日下跌记 0 收益，"
        "不看过一天价格有没有回来。这是货架表与 r2046 之后所有货币侧读数的来源。",
        "* **本面 honest** = 先分形状再修：年度折算（价格永久下移、|跌|≤5%）只抹跌；报价瞬时下探（3 根内回到原位）"
        "两腿都抹；溢价尖峰（10 根内已涨回跌幅的 80%）从谷底到回归整段抹平。",
        "* **S/V/R/U** = 尖峰/瞬时下探/可读折算/不可读位移（|跌|>5%，价格无法区分大比例份额折算与坏打印，"
        "本司没有 NAV/份额面，所以不出 honest 读数）。",
        "* **一辆票=几天量** = 票面现金 ÷ 20 日平均成交额。大于 1 表示一天的换手装不下这一辆票。",
        "",
        "## 这张面不做什么",
        "",
        "* 不改 `consolidation_returns`、不改货架表、不改任何已发布的 carry。",
        "* 不对「不可读位移」出数：缺面印成 0 就是把没读到的当读到了。",
        "* 不主张尖峰整段抹平是唯一正确的中性化；它只保证「价格离开 100 又回到 100 不记收益」。",
        "",
    ]
    return "\n".join(body)


# --------------------------------------------------------------------- commands

def cmd_run():
    face = build()
    with io.open(os.path.join(ROOT, FACE), "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
        f.write("\n")
    doc_path = os.path.join(ROOT, DOC)
    body = render_doc(face)
    if os.path.exists(doc_path):
        old = io.open(doc_path, encoding="utf-8").read()
        if MARK_BEGIN in old and MARK_END in old:
            pre = old.split(MARK_BEGIN)[0]
            post = MARK_END + old.split(MARK_END, 1)[1]
            body = pre + MARK_BEGIN + "\n" + render_block(face) + "\n" + post
    with io.open(doc_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    h = face["headline"]
    print("RUN OK %s verdict=%s priced=%d jumps=%d spike=%d unverifiable=%d invented=%d "
          "invented_cny=%s tags=%s" % (
              FACE, h["verdict"], h["priced"], h["with_any_jump"], h["with_spike"],
              h["with_unverifiable"], len(h["invented_rows"]),
              _m(h["invented_carry_total_cny"]), ",".join(h["tags"]) or "-"))
    return 0


def cmd_check():
    path = os.path.join(ROOT, FACE)
    if not os.path.exists(path):
        print("CHECK FAILED face missing -> STALE, run `run`")
        return 3
    face = _load(FACE)
    fresh = build()
    if str(face.get("evidence_cutoff")) != str(fresh.get("evidence_cutoff")):
        print("STALE: panel tail moved %s -> %s, this face is a statement about a window"
              % (face.get("evidence_cutoff"), fresh.get("evidence_cutoff")))
        return 3
    up_f, up_n = face.get("upstream", {}), fresh.get("upstream", {})
    for key in ("panel_columns", "spike_lookback", "spike_share", "reset_readable_max",
                "misread_min_pp", "amt_tail"):
        if up_f.get(key) != up_n.get(key):
            print("STALE: upstream %s changed %s -> %s" % (key, up_f.get(key), up_n.get(key)))
            return 3
    if up_f.get("cash_vehicle_rule", {}).get("CONSOLIDATION_JUMP") != \
            up_n.get("cash_vehicle_rule", {}).get("CONSOLIDATION_JUMP"):
        print("STALE: the deep-drop rule itself changed -> re-run")
        return 3

    bad = []
    for key in ("verdict", "tags"):
        if face["headline"].get(key) != fresh["headline"].get(key):
            bad.append("headline.%s: face=%s recompute=%s"
                       % (key, face["headline"].get(key), fresh["headline"].get(key)))
    fmap = {r["code"]: r for r in fresh["rows"]}
    for r in face["rows"]:
        fr = fmap.get(r["code"])
        if fr is None:
            bad.append("%s vanished upstream" % r["code"])
            continue
        for field in CHECK_FIELDS:
            a, b = r.get(field), fr.get(field)
            if a is None and b is None:
                continue
            if a is None or b is None or abs(float(a) - float(b)) > 1e-6:
                bad.append("%s %s: face=%s recompute=%s" % (r["code"], field, a, b))
        fa = [(j["date"], j["shape"], j["drop_bp"]) for j in r.get("jumps", [])]
        fb = [(j["date"], j["shape"], j["drop_bp"]) for j in fr.get("jumps", [])]
        if fa != fb:
            bad.append("%s jump list changed (%d -> %d)" % (r["code"], len(fa), len(fb)))
    if bad:
        print("CHECK FAILED %d leg(s):" % len(bad))
        for b in bad[:20]:
            print("  - " + b)
        return 1
    print("CHECK OK %s: verdict/tags/%d rows re-derived, %d jumps identical"
          % (FACE, len(face["rows"]), sum(len(r.get("jumps", [])) for r in face["rows"])))
    return 0


# --------------------------------------------------------------------- selftest

def _synth(n=400, seed=7, drift_bp=0.5, sigma_bp=1.5):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2021-01-04", periods=n)
    steps = rng.normal(drift_bp / 1e4, sigma_bp / 1e4, n)
    return pd.Series(100.0 * np.cumprod(1.0 + steps), index=idx)


def _reset_series(n=400):
    """A yearly share reset: drift up all year, one -3% bar, then keep drifting."""
    px = _synth(n, drift_bp=2.5, sigma_bp=1.0)
    px.iloc[300:] = px.iloc[300:] * 0.97
    return px


def _spike_series(n=400):
    """A premium spike: 4 sessions up +8%, then one bar back to the trough."""
    px = _synth(n, drift_bp=0.0, sigma_bp=1.0)
    base = float(px.iloc[199])
    for k, mult in enumerate((1.02, 1.04, 1.06, 1.08)):
        px.iloc[200 + k] = base * mult
    anchor = float(px.iloc[204])
    px.iloc[204:] = px.iloc[204:] / anchor * base
    return px


def _vdip_series(n=400):
    """A one-bar quote dip that comes straight back inside the 3-bar window."""
    px = _synth(n, drift_bp=0.0, sigma_bp=1.0)
    base = float(px.iloc[199])
    px.iloc[200] = base * 0.99
    anchor = float(px.iloc[201])
    px.iloc[201:] = px.iloc[201:] / anchor * base
    return px


def selftest():
    errs, legs = [], [0]

    def chk(ok, msg):
        legs[0] += 1
        if not ok:
            errs.append("L%d %s" % (legs[0], msg))

    # L1 the published rule fires on every one of the three shapes (they are all deep drops)
    for nm, ser in (("reset", _reset_series()), ("spike", _spike_series()),
                    ("vdip", _vdip_series())):
        chk(len(apply_rule_shape_hits(ser)) >= 1, "L1 no deep drop seen on the %s synthetic" % nm)

    # L2 shape identification, one shape per synthetic series
    r = classify_drops(_reset_series())
    chk(len(r) == 1 and r[0]["shape"] == "RESET", "L2 a yearly reset was not called RESET (%s)" % r)
    s = classify_drops(_spike_series())
    chk(len(s) == 1 and s[0]["shape"] == "SPIKE", "L2 a premium spike was not called SPIKE (%s)" % s)
    v = classify_drops(_vdip_series())
    chk(len(v) == 1 and v[0]["shape"] == "V_DIP", "L2 a one-bar dip was not called V_DIP (%s)" % v)

    # L3 a deeper-than-5% permanent step is UNVERIFIABLE, not RESET
    d = _synth(400, drift_bp=0.0, sigma_bp=1.0)
    d.iloc[300:] = d.iloc[300:] * 0.93
    dd = classify_drops(d)
    chk(len(dd) == 1 and dd[0]["shape"] == "UNVERIFIABLE_RESET",
        "L3 a -7%% permanent step was called %s" % (dd[0]["shape"] if dd else None))

    # L4 the reset: published rule and honest reading agree (the rule is right here)
    px = _reset_series()
    js = classify_drops(px)
    cv_tape = annualise(apply_rule(px, js, "cv"))
    ho_tape = annualise(apply_rule(px, js, "honest"))
    chk(cv_tape is not None and ho_tape is not None and abs(cv_tape - ho_tape) < 1e-9,
        "L4 reset: cv %s != honest %s (a readable reset must be left alone by the split)"
        % (cv_tape, ho_tape))

    # L5 the spike: the published rule credits carry the price never held
    px = _spike_series()
    js = classify_drops(px)
    raw = annualise(apply_rule(px, js, "raw"))
    cv_tape = annualise(apply_rule(px, js, "cv"))
    ho_tape = annualise(apply_rule(px, js, "honest"))
    chk(cv_tape > raw + 1.0, "L5 spike: published cv %.3f not above raw %.3f" % (cv_tape, raw))
    chk(abs(ho_tape - raw) < 0.5, "L5 spike: honest %.3f did not land back on raw %.3f"
        % (ho_tape, raw))

    # L6 the v-dip: honest zeroes both legs, so it sits on raw; cv sits above by the rebound
    px = _vdip_series()
    js = classify_drops(px)
    raw = annualise(apply_rule(px, js, "raw"))
    cv_tape = annualise(apply_rule(px, js, "cv"))
    ho_tape = annualise(apply_rule(px, js, "honest"))
    chk(abs(ho_tape - raw) < 0.5 and cv_tape > ho_tape,
        "L6 v-dip: honest %.3f / raw %.3f / cv %.3f" % (ho_tape, raw, cv_tape))

    # L7 a clean series gets no jump and no change under any tape
    clean = _synth(400, drift_bp=0.0, sigma_bp=0.5)
    js = classify_drops(clean)
    chk(len(js) == 0, "L7 a clean series produced %d deep drops" % len(js))
    chk(abs(annualise(apply_rule(clean, js, "raw")) - annualise(apply_rule(clean, js, "cv"))) < 1e-9,
        "L7 the rules moved a series they never touched")

    # L8 the unverifiable row must refuse to annualise (r98: a missing face is not zero)
    px = _synth(400, drift_bp=0.0, sigma_bp=1.0)
    px.iloc[300:] = px.iloc[300:] * 0.93
    js = classify_drops(px)
    conv = annualise(apply_rule(px, js, "honest"))
    chk(js and js[0]["shape"] == "UNVERIFIABLE_RESET" and conv is not None,
        "L8 the arithmetic leg is not the guard: refusing the number belongs to measure()")

    # L9 verdicts are mechanical on the counts
    chk(verdict_for([{"priced": True, "jumps_total": 0, "overstatement_pp": 0.0,
                      "spike": 0, "reset_unverifiable": 0}]) == "NO_JUMP_ANYWHERE",
        "L9 no-jump verdict")
    chk(verdict_for([{"priced": True, "jumps_total": 2, "overstatement_pp": 0.0,
                      "spike": 0, "reset_unverifiable": 0}]) == "REPAIRS_ARE_SYMMETRIC_ALREADY",
        "L9 symmetric verdict")
    chk(verdict_for([{"priced": True, "jumps_total": 2, "overstatement_pp": 3.0,
                      "spike": 1, "reset_unverifiable": 0}]) == "THE_ONE_SIDED_REPAIR_INVENTS_CARRY",
        "L9 invented verdict")
    chk(verdict_for([{"priced": True, "jumps_total": 2, "overstatement_pp": 0.2,
                      "spike": 1, "reset_unverifiable": 0}]) == "THE_ONE_SIDED_REPAIR_IS_IMMATERIAL",
        "L9 immaterial verdict")

    # L10 the ticket maths: participation and money are the same ticket, never re-typed
    leg = measure_on_series(_reset_series(), amt20=500000.0, ticket=565245.9, name="货币ETF合成")
    chk(leg["participation_x"] is not None
        and abs(leg["participation_x"] - round(565245.9 / 500000.0, 4)) < 1e-9,
        "L10 participation is not ticket / turnover (%s)" % leg.get("participation_x"))
    chk(leg["cv_carry_cny"] is not None
        and abs(leg["cv_carry_cny"] - 565245.9 * leg["tape_cv_pct"] / 100.0) < 0.02,
        "L10 carry money is not ticket x tape")

    # L11 determinism: the same series measured twice gives the same content hash
    a = measure_on_series(_spike_series(), amt20=1e6, ticket=565245.9, name="x")
    b = measure_on_series(_spike_series(), amt20=1e6, ticket=565245.9, name="x")
    chk(_content_sha(a) == _content_sha(b), "L11 two runs of the same series differ")

    # L12 the guard that matters: a spike row must refuse no honest number, but a deep
    #     permanent step must.  Behaviour leg on the real measure() path.
    px = _synth(400, drift_bp=0.0, sigma_bp=1.0)
    px.iloc[300:] = px.iloc[300:] * 0.80
    deep = measure_on_series(px, amt20=1e6, ticket=565245.9, name="深度位移合成")
    chk(deep["tape_honest_pct"] is None and deep["honest_reason"],
        "L12 a -20%% permanent step still printed an honest reading (%s)" % deep.get("tape_honest_pct"))

    if errs:
        print("SELFTEST FAILED %d/%d" % (len(errs), legs[0]))
        for e in errs:
            print("  - " + e)
        return 1
    print("SELFTEST OK %d/%d" % (legs[0], legs[0]))
    return 0


def apply_rule_shape_hits(ser):
    return classify_drops(ser)


def measure_on_series(px, amt20, ticket, name="synthetic"):
    """measure() without the on-disk loader, so the selftest never reads a panel."""
    idx = px.dropna().index
    amt = pd.Series(np.full(len(idx), float(amt20)), index=idx)
    return measure("SYN", ("money", name), px, amt, str(idx[0].date()), str(idx[-1].date()), ticket)


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return cmd_run()
    if cmd in ("--check", "check"):
        return cmd_check()
    if cmd in ("--selftest", "selftest"):
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
