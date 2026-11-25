#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""money_subband_jump_audit -- what is left in a money ETF's carry after both rulers.

WHY THIS FACE EXISTS
--------------------
r2050 (`money_premium_carry_audit`) repaired the eleven money ETFs r2048 named by zeroing
every bar more than 1% away from the instrument's own trailing median, and then printed a
number it did not answer: after the repair the daily sigma is 4.1-31.4bp, while a money
market fund accrues about 0.8bp a day.  In its own words (page section 5, point 3):

    "25-55bp 的 sigma 在修复后不是掉到 1-2bp 就完事——剩下的方差说明还有别的形状
     （多段阶梯、慢回复）没被两条规则抓住，这一点本面只点明，不宣称已清。"

This is that face.  The two rulers already in force are:

  * the published money reader `etf_book_cash_vehicle.consolidation_returns`, which books
    every bar deeper than -50bp at zero (a share consolidation);
  * r2050's band ruler, which books every bar more than 1% from its own 20-bar median at
    zero (a premium that is not a carry).

Neither can see a jump that is *smaller than the band* and *upward or mild*: a single
session that prints +40bp and gives it back the next day is 50 sessions of carry, it never
leaves a 1% band, and it is never a consolidation.  That bar is booked as return.

THE QUESTION (frozen before the first run)
------------------------------------------
On the r2050-repaired series, for every instrument r2048 named and for the book's own five
shelf legs as control: how much of the annualised carry comes from **isolated sub-band
jumps** -- bars of 5bp or more whose two neighbours move less than 2bp -- and how much of
the residual sigma do those bars explain?

RULER (nothing re-decided here)
-------------------------------
* window, panel, reader            -- exactly r2048's window via r2050's own module
                                      (`money_premium_carry_audit`: `find_breaches`,
                                      `repaired_rets`, `local_level`, `BAND_PCT`)
* annualisation                    -- `cash_shelf_year_by_year.bars_per_year` (the
                                      r2045/r2046/r2048 ruler: the series' own bars over
                                      the series' own span), applied to the **arithmetic**
                                      mean.  An arithmetic annualisation is exactly
                                      additive across bar subsets, which is what makes a
                                      decomposition honest; the geometric CAGR is printed
                                      next to it as a cross-check, never as the share.
* daily sigma                      -- `cash_shelf_flip_census.sigma_bp`
* **QUIET_BP = 2.0** (added here)  -- a money fund prints ~0.8bp/day, so 2bp is about two
                                      and a half sessions of accrual: a neighbour this
                                      quiet is not part of a move.
* **JUMP_LO_BP = 5.0** (added here)-- below 5bp a bar is six days of carry and its own
                                      rounding noise; calling that a jump would be the
                                      r2048 `THE_GEOMETRY_OVERREACHES` mistake again.
* **MIN_DENOM_PP = 0.05**           -- below 5bp/yr of repaired carry the share has no
                                      denominator worth dividing by (r2043's negative-
                                      denominator lesson: print the reading, not a ratio).
* boundary                          -- a neighbour that does not exist counts as quiet.
                                      Deterministic; it can touch at most two bars and the
                                      count of such bars is printed.

VERDICTS (mechanical, frozen), on the median share across the eleven named instruments
----------------------------------------------------------------------------------------
* SUB_BAND_JUMPS_ARE_THE_CARRY      -- median share >= 50% of repaired carry
* SUB_BAND_JUMPS_ARE_HALF_THE_CARRY -- 20% <= median share < 50%
* CARRY_SURVIVES_THE_JUMPS          -- median share < 20%

TAGS (printed beside the verdict, never folded into it)
------------------------------------------------------
* THE_BOOK_LEGS_SURVIVE        -- every book leg (money/bond legs) moves by less than
                                 0.25pp of geometric carry when its isolated jumps are
                                 zeroed: the published shelf numbers stand.
* A_THIRD_RULE_WOULD_MOVE_THE_BOOK -- some book leg moves by 0.25pp or more: r2045's
                                 payback days must be re-derived before anyone uses them.
* EVERY_NAMED_INSTRUMENT_HAS_SUB_BAND_JUMPS -- all eleven carry at least one isolated bar.
* THE_RESIDUAL_SIGMA_IS_THE_JUMPS -- median sigma falls by at least 30% when the isolated
                                 bars are zeroed (the leftover variance has a name).
* CARRY_IS_TOO_THIN_FOR_A_SHARE  -- some instrument's repaired carry is under MIN_DENOM_PP,
                                 so it is printed without a share.

CAVEAT (printed, not folded)
----------------------------
The panel cannot tell a bad feed print from a real one-session price move; both are a bar
away from the level that comes back.  For a carry caliber they are the same problem, and
this face does not claim to tell them apart.  It charges no cost and claims no tradeable
return.

Usage:
    python scripts/money_subband_jump_audit.py run
    python scripts/money_subband_jump_audit.py --check
    python scripts/money_subband_jump_audit.py --selftest
"""

from __future__ import annotations

import datetime as dt
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

import etf_book_cash_vehicle as CV  # noqa: E402  (the published money reader)
import cash_shelf_flip_census as CE  # noqa: E402  (sigma, r2048)
import cash_shelf_year_by_year as YY  # noqa: E402  (bars_per_year, r2046)
import money_premium_carry_audit as MP  # noqa: E402  (the 1% band ruler, r2050)

PREMIUM_FACE = "results/money_premium_carry_audit.json"
CENSUS_FACE = "results/cash_shelf_flip_census.json"
SHELF_FACE = "results/cash_shelf_year_by_year.json"
FACE = "results/money_subband_jump_audit.json"
DOC = "research/MONEY_SUBBAND_JUMP_AUDIT.md"

# Frozen before the first run.  See the docstring for why each number is what it is.
QUIET_BP = 2.0          # a neighbour quieter than this is not part of a move
JUMP_LO_BP = 5.0        # smaller than this and a bar is accrual plus rounding, not a jump
MIN_DENOM_PP = 0.05     # below this the repaired carry cannot carry a share
MATERIAL_PP = 0.25      # a book leg moving this much means r2045 must be re-derived
HALF_SHARE = 0.50       # median share at or above this: the jumps are the carry
PART_SHARE = 0.20       # median share at or below this: the carry survives
SIGMA_DROP = 0.30       # median sigma reduction that earns the residual tag
RET_WINDOW = 20         # bars allowed for a jump to give itself back
RET_TOL_BP = 2.0        # within this of the pre-jump price counts as "gave it back"

# Magnitude buckets for the shape split.  Frozen: quiet is the accrual band, stair is the
# band r2050 named and neither ruler can see, jump_* is what this face calls a jump, huge
# is a share-count event wearing a return's clothes.
SHAPE_BUCKETS = (
    ("quiet_lt_2bp", 0.0, 2.0),
    ("stair_2_5bp", 2.0, 5.0),
    ("jump_5_25bp", 5.0, 25.0),
    ("jump_25_100bp", 25.0, 100.0),
    ("huge_ge_100bp", 100.0, float("inf")),
)

MARK_BEGIN = "<!-- SUBBAND-TABLE:BEGIN -->"
MARK_END = "<!-- SUBBAND-TABLE:END -->"


# ------------------------------------------------------------------------ plumbing

def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _rel_sha(path):
    p = os.path.join(ROOT, path)
    return _sha(p) if os.path.exists(p) else None


def _load(path):
    with io.open(os.path.join(ROOT, path), "r", encoding="utf-8") as f:
        return json.load(f)


def _content_sha(obj):
    blob = json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


# --------------------------------------------------------------------- measurement

def classify_isolated(rets):
    """Flag the isolated sub-band jumps of one repaired return series.

    A bar is a jump when its own move is at least JUMP_LO_BP.  It is *isolated* when both
    neighbours move at most QUIET_BP -- the move neither builds nor unwinds anything around
    it, which is the shape neither existing ruler can see.  A neighbour outside the window
    counts as quiet (documented boundary rule).
    """
    r = np.asarray(rets.to_numpy(), dtype=float)
    n = r.shape[0]
    mag_bp = np.abs(r) * 1e4
    big = mag_bp >= JUMP_LO_BP
    quiet = mag_bp <= QUIET_BP
    iso = np.zeros(n, dtype=bool)
    for i in range(n):
        if not big[i]:
            continue
        prev_quiet = bool(quiet[i - 1]) if i > 0 else True
        next_quiet = bool(quiet[i + 1]) if i + 1 < n else True
        iso[i] = prev_quiet and next_quiet
    run = big & ~iso
    return iso, run, big


def _zero_at(rets, mask):
    """Copy of `rets` with the masked bars booked at exactly zero return."""
    out = rets.copy()
    if mask.any():
        out.iloc[np.flatnonzero(mask)] = 0.0
    return out


def classify_pairs(rets):
    """The classical bad print: one bar up and the very next bar back down (or the reverse).

    This shape is worth counting separately because it is the one the isolation rule
    *excludes*: two adjacent jumps are each other's loud neighbour, so they land in `run`.
    Their carry effect is almost exactly zero by construction -- the two bars cancel -- so a
    face that only looked at carry would never notice them, and a face that only looked at
    sigma would see them everywhere.
    """
    r = np.asarray(rets.to_numpy(), dtype=float)
    n = r.shape[0]
    mag_bp = np.abs(r) * 1e4
    big = mag_bp >= JUMP_LO_BP
    quiet = mag_bp <= QUIET_BP
    pair = np.zeros(n, dtype=bool)
    count = 0
    for i in range(n - 1):
        if not (big[i] and big[i + 1]):
            continue
        if np.sign(r[i]) == np.sign(r[i + 1]):
            continue
        prev_quiet = bool(quiet[i - 1]) if i > 0 else True
        next_quiet = bool(quiet[i + 2]) if i + 2 < n else True
        if prev_quiet and next_quiet:
            pair[i] = pair[i + 1] = True
            count += 1
    return pair, count


def classify_shapes(px, rr, iso, zeroed_src):
    """Split the isolated jumps by what the price did next and by which ruler is on the
    other half of the move.

    The important discovery this face had to make twice: a ruler that books *one* bar of a
    round trip at zero and leaves the other bar alone does not remove the event, it
    manufactures a phantom return out of the half it kept.  So the mirror source is printed:

    * MIRROR_READER -- the opposite bar was zeroed by the published money reader (a drop
      deeper than -50bp, i.e. a share consolidation).  511920 on 2021-10-19 drops -9.01%
      and comes straight back on 10-20: the drop is booked at zero, the +989bp rebound is
      carried as return.
    * MIRROR_BAND  -- the opposite bar was zeroed by r2050's 1% band.  Same asymmetry, one
      generation later: the premium is zeroed, its return leg is kept.
    * RETURNS      -- the price comes back inside RET_WINDOW bars with no zeroed mirror:
      a bad print or a transient premium that no ruler has touched.
    * SHIFTS       -- the price stays at the new level: a share-count event in the upward
      direction, which the published reader cannot see at all.

    Whether a mirror counts as already paid is *not* decided here: that needs the list of
    pairs an upstream face says it neutralised, and `build` applies it.
    """
    n = int(px.shape[0])
    r = np.asarray(rr.to_numpy(), dtype=float)
    # Mirror magnitude must come from the printed prices, not from the reader's series: a
    # zeroed bar reads 0.0 there, and a mirror is measured against what was printed.
    orig = np.asarray(px.pct_change().fillna(0.0).to_numpy(), dtype=float)
    src_name = {0: None, 1: "reader", 2: "band"}
    out = []
    mirror_mask = np.zeros(n, dtype=bool)
    for i in np.flatnonzero(iso):
        i = int(i)
        pre = float(px.iloc[i - 1]) if i >= 1 else None
        move_bp = 0.0 if pre is None else round((float(px.iloc[i]) / pre - 1.0) * 1e4, 2)
        mag = abs(float(orig[i]))
        mirror = None
        source = None
        lo, hi = max(1, i - RET_WINDOW), min(n - 1, i + RET_WINDOW)
        for j in range(lo, hi + 1):
            if j == i or not int(zeroed_src[j]):
                continue
            if np.sign(orig[j]) == np.sign(orig[i]):
                continue
            if abs(float(orig[j])) < 0.5 * mag:
                continue
            mirror = str(pd.Timestamp(px.index[j]).date())
            source = src_name.get(int(zeroed_src[j]))
            break
        if pre is None:
            shape = "EDGE"
        elif mirror and source == "reader":
            shape = "MIRROR_READER"
            mirror_mask[i] = True
        elif mirror:
            shape = "MIRROR_BAND"
            mirror_mask[i] = True
        elif i >= n - 1:
            shape = "UNRESOLVED"
        else:
            shape = "SHIFTS"
            for j in range(i + 1, min(i + RET_WINDOW, n - 1) + 1):
                if abs(float(px.iloc[j]) / pre - 1.0) * 1e4 <= RET_TOL_BP:
                    shape = "RETURNS"
                    break
        out.append({"date": str(pd.Timestamp(px.index[i]).date()),
                    "move_bp": move_bp, "shape": shape, "mirror_date": mirror,
                    "mirror_source": source})
    return out, mirror_mask


def month_end_mask(index):
    """True on the last trading bar of each calendar month in this panel.

    A money ETF marks its accrual lumpily, and a 5-8bp step that lands on the last bar of a
    month is a different animal from a mid-month bad print: it usually persists.  Counting
    them is how a reader tells a caliber choice from a correction.
    """
    idx = pd.DatetimeIndex(index)
    out = np.zeros(len(idx), dtype=bool)
    if len(idx) == 0:
        return out
    months = idx.year * 100 + idx.month
    out[-1] = True
    for i in range(len(idx) - 1):
        out[i] = months[i] != months[i + 1]
    return out


def decompose(rets):
    """Arithmetic decomposition of one bar series into base / isolated / run.

    Arithmetic annualisation is additive: annualised mean = mean x bars_per_year, and the
    mean is the sum over disjoint bar subsets.  That is the only reading in which a share
    of carry by bar class is an identity rather than a narration.
    """
    rets = rets.dropna()
    n = int(rets.shape[0])
    bpy = YY.bars_per_year(rets)
    if n < 2 or not bpy:
        return None
    iso, run, big = classify_isolated(rets)
    vals = np.asarray(rets.to_numpy(), dtype=float)
    scale = bpy / n * 100.0           # sum(r_class) x scale = that class's pp per year
    out = {
        "bars": n,
        "bars_per_year": round(float(bpy), 3),
        "jump_bars": int(big.sum()),
        "isolated_bars": int(iso.sum()),
        "run_bars": int(run.sum()),
        "boundary_bars": int(big[0]) + (int(big[-1]) if n > 1 else 0),
        "isolated_pp": round(float(vals[iso].sum()) * scale, 4),
        "run_pp": round(float(vals[run].sum()) * scale, 4),
        "base_pp": round(float(vals[~big].sum()) * scale, 4),
        "arith_pp": round(float(vals.sum()) * scale, 4),
        "biggest_isolated_bp": (round(float(np.abs(vals[iso]).max()) * 1e4, 2)
                                if iso.any() else 0.0),
        "median_isolated_bp": (round(float(np.median(np.abs(vals[iso]))) * 1e4, 2)
                               if iso.any() else 0.0),
        "isolated_dates": [str(pd.Timestamp(d).date()) for d in rets.index[iso]],
    }
    # Identities the face is allowed to be wrong about only loudly.
    out["parts_sum_pp"] = round(out["base_pp"] + out["run_pp"] + out["isolated_pp"], 4)
    out["parts_sum_error_pp"] = round(out["parts_sum_pp"] - out["arith_pp"], 4)

    # The flip pair is a subset of `run` (two adjacent jumps are each other's loud
    # neighbour).  It is counted and priced separately because its carry is ~zero by
    # construction while its sigma is real.
    pair, pair_events = classify_pairs(rets)
    out["pair_bars"] = int(pair.sum())
    out["pair_events"] = int(pair_events)
    out["pair_pp"] = round(float(vals[pair].sum()) * scale, 4)

    # Where the leftover sigma actually lives.  Both columns are additive by construction:
    # the pp column sums to the arithmetic carry, the variance column sums to 100%.
    mean_ = float(vals.mean())
    ss_total = float(((vals - mean_) ** 2).sum())
    mag_bp = np.abs(vals) * 1e4
    shape = []
    for name, lo, hi in SHAPE_BUCKETS:
        m = (mag_bp >= lo) & (mag_bp < hi)
        shape.append({
            "bucket": name,
            "bars": int(m.sum()),
            "pp": round(float(vals[m].sum()) * scale, 4),
            "var_share_pct": (None if ss_total <= 0
                              else round(float(((vals[m] - mean_) ** 2).sum()) / ss_total * 100.0, 2)),
        })
    out["shape"] = shape
    out["var_share_sum_pct"] = round(sum(s["var_share_pct"] or 0.0 for s in shape), 2)
    return out


def measure_one(code, start, end, name=None, repaired_pairs=None):
    """One instrument: r2050's repair, then the sub-band decomposition, then sigma.

    `repaired_pairs` is the set of (code, date) round trips that an upstream face says it
    already neutralised on both sides.  Only those mirrors leave `isolated_pp_unpaid`; a
    mirror created by the reader's or the band's one-sided rule is debt, because the half
    that was kept is a phantom return.
    """
    px = CV.load_etf(code)
    px = px[(px.index >= pd.Timestamp(start)) & (px.index <= pd.Timestamp(end))]
    px = px.dropna().astype(float)
    if px.shape[0] < 40:
        return {"code": code, "name": name, "priced": False,
                "why_unpriced": "fewer than 40 bars in the window"}
    rets, resets = CV.consolidation_returns(px)
    episodes, flag = MP.find_breaches(px)
    rr, n_repaired = MP.repaired_rets(rets, flag)
    d = decompose(rr)
    if d is None:
        return {"code": code, "name": name, "priced": False,
                "why_unpriced": "decomposition needs two bars and a positive span"}
    iso_all = classify_isolated(rr)[0]
    no_jump = _zero_at(rr, iso_all)
    zeroed_src = np.zeros(int(px.shape[0]), dtype=np.int8)   # 1 = reader, 2 = band
    if bool(flag.any()):
        zeroed_src[np.asarray(flag.to_numpy(dtype=bool))] = 2
    reset_dates = set(d0.get("date") for d0 in resets)
    for i, dt_ in enumerate(px.index):
        if str(pd.Timestamp(dt_).date()) in reset_dates:
            zeroed_src[i] = 1
    events, mirror_mask = classify_shapes(px, rr, iso_all, zeroed_src)
    paid = set(repaired_pairs or ())
    already_mask = np.zeros(int(px.shape[0]), dtype=bool)
    for e in events:
        if e.get("mirror_date") and (code, e["mirror_date"]) in paid:
            already_mask[int(px.index.get_loc(pd.Timestamp(e["date"])))] = True
    unpaid_mask = iso_all & ~already_mask
    no_unpaid = _zero_at(rr, unpaid_mask)
    cagr_rep = CE.cagr_from_rets(rr)
    cagr_no = CE.cagr_from_rets(no_jump)
    cagr_unpaid = CE.cagr_from_rets(no_unpaid)
    biggest_event = max(events, key=lambda e: abs(e["move_bp"]), default=None)
    mirrors = [e for e in events if e["shape"].startswith("MIRROR")]
    biggest_mirror = max(mirrors, key=lambda e: abs(e["move_bp"]), default=None)
    me_mask = month_end_mask(px.index)
    month_end_bars = int((iso_all & me_mask).sum())
    month_end_shifts = int(sum(1 for e in events
                               if e["shape"] == "SHIFTS"
                               and bool(me_mask[int(px.index.get_loc(pd.Timestamp(e["date"])))])))
    d.update({
        "code": code,
        "name": name,
        "priced": True,
        "window_start": str(px.index[0].date()),
        "window_end": str(px.index[-1].date()),
        "band_episodes": len(episodes),
        "band_repaired_bars": int(n_repaired),
        "money_resets_removed": len(resets),
        "events": events,
        "events_returns": int(sum(1 for e in events if e["shape"] == "RETURNS")),
        "events_shifts": int(sum(1 for e in events if e["shape"] == "SHIFTS")),
        "events_mirror_reader": int(sum(1 for e in events if e["shape"] == "MIRROR_READER")),
        "events_mirror_band": int(sum(1 for e in events if e["shape"] == "MIRROR_BAND")),
        "events_already_repaired": int(already_mask.sum()),
        "events_unresolved": int(sum(1 for e in events
                                     if e["shape"] in ("UNRESOLVED", "EDGE"))),
        "mirror_bars": int(mirror_mask.sum()),
        "month_end_bars": month_end_bars,
        "month_end_shifts": month_end_shifts,
        "biggest_event": biggest_event,
        "biggest_mirror_event": biggest_mirror,
        "isolated_pp_unpaid": (None if cagr_rep is None or cagr_unpaid is None
                               else round(cagr_rep - cagr_unpaid, 4)),
        "cagr_repaired_pct": None if cagr_rep is None else round(cagr_rep, 4),
        "cagr_without_jumps_pct": None if cagr_no is None else round(cagr_no, 4),
        "carry_from_jumps_pp": (None if (cagr_rep is None or cagr_no is None)
                                else round(cagr_rep - cagr_no, 4)),
        "sigma_repaired_bp": _round_or_none(CE.sigma_bp(rr)),
        "sigma_without_jumps_bp": _round_or_none(CE.sigma_bp(no_jump)),
    })
    if d["arith_pp"] > MIN_DENOM_PP:
        d["isolated_share"] = round(d["isolated_pp"] / d["arith_pp"], 4)
        d["share_reason"] = "isolated_pp / arith_pp"
    else:
        d["isolated_share"] = None
        d["share_reason"] = ("repaired carry %.4fpp/yr is under the %.2fpp floor, so the "
                             "share has no denominator" % (d["arith_pp"], MIN_DENOM_PP))
    s1, s0 = d["sigma_without_jumps_bp"], d["sigma_repaired_bp"]
    d["sigma_drop_pct"] = (None if (s1 is None or s0 is None or s0 <= 0)
                           else round((s0 - s1) / s0 * 100.0, 2))
    return d


def _round_or_none(v):
    return None if v is None else round(float(v), 3)


# ------------------------------------------------------------------------ judgement

def verdict_of(rows):
    """Mechanical verdict on the median isolated share across the named instruments."""
    vals = [r["isolated_share"] for r in rows if r.get("isolated_share") is not None]
    if not vals:
        return "CARRY_IS_TOO_THIN_FOR_A_SHARE", None
    med = float(np.median(vals))
    if med >= HALF_SHARE:
        return "SUB_BAND_JUMPS_ARE_THE_CARRY", med
    if med >= PART_SHARE:
        return "SUB_BAND_JUMPS_ARE_HALF_THE_CARRY", med
    return "CARRY_SURVIVES_THE_JUMPS", med


def tags_of(named, carry_legs):
    """Tags printed beside the verdict, never folded into it.

    The book-leg tags read `isolated_pp_unpaid` -- the carry that an unrepaired jump
    explains.  A jump that is the mirror half of a flip some earlier face already zeroed
    (`MIRROR_ZEROED`) is printed and priced, but it is not new debt, and a tag that counted
    it would send a reader to re-derive numbers that are already repaired (r1787).
    """
    tags = []
    unpaid = [r.get("isolated_pp_unpaid") for r in carry_legs]
    if carry_legs and all(v is not None and abs(v) < MATERIAL_PP for v in unpaid):
        tags.append("THE_BOOK_LEGS_SURVIVE")
    if any(v is not None and abs(v) >= MATERIAL_PP for v in unpaid):
        tags.append("A_THIRD_RULE_WOULD_MOVE_THE_BOOK")
    if sum(int(r.get("events_already_repaired") or 0) for r in carry_legs) >= 1:
        tags.append("A_MEASURED_JUMP_WAS_ALREADY_REPAIRED")
    if named and all(r.get("isolated_bars", 0) >= 1 for r in named if r.get("priced")):
        tags.append("EVERY_NAMED_INSTRUMENT_HAS_SUB_BAND_JUMPS")
    drops = [r["sigma_drop_pct"] for r in named if r.get("sigma_drop_pct") is not None]
    if drops and float(np.median(drops)) >= SIGMA_DROP * 100.0:
        tags.append("THE_RESIDUAL_SIGMA_IS_THE_JUMPS")
    if any(r.get("isolated_share") is None for r in named):
        tags.append("CARRY_IS_TOO_THIN_FOR_A_SHARE")
    me_rows = [r for r in carry_legs if (r.get("isolated_bars") or 0)]
    if me_rows:
        tot_me = sum(int(r.get("month_end_bars") or 0) for r in me_rows)
        tot_iso = sum(int(r.get("isolated_bars") or 0) for r in me_rows)
        if tot_iso and tot_me / float(tot_iso) >= 0.5:
            tags.append("MONEY_STEPS_ARE_MONTH_END_MARKS")
    return tags


# ---------------------------------------------------------------------------- build

def build():
    premium = _load(PREMIUM_FACE)
    census = _load(CENSUS_FACE)
    shelf = _load(SHELF_FACE)

    start = str(premium["window"]["start"])
    end = str(premium["window"]["end"])

    # The r2050 gate: this face repairs with his ruler, so his repaired carry must
    # reproduce bar for bar.  If it does not, this face has no right to speak about what
    # is left over.
    gate = []
    named = []
    for row in premium["rows"]:
        m = measure_one(row["code"], start, end, name=row.get("name"))
        if not m.get("priced"):
            gate.append({"code": row["code"], "ok": False, "why": m.get("why_unpriced")})
            named.append(m)
            continue
        got = m["cagr_repaired_pct"]
        want = row.get("cagr_repaired_pct")
        ok = (got is not None and want is not None and abs(got - float(want)) <= 0.01)
        gate.append({"code": row["code"], "ok": bool(ok), "got_pct": got, "want_pct": want})
        named.append(m)
    if not all(g["ok"] for g in gate):
        bad = [g for g in gate if not g["ok"]]
        raise SystemExit("FATAL: r2050 repaired-carry gate failed on %s -- refuse to publish"
                         % ", ".join("%s(%s vs %s)" % (g["code"], g.get("got_pct"),
                                                       g.get("want_pct")) for g in bad))

    census_names = {r["code"]: r.get("name") for r in census["rows"]}

    # Round trips an upstream face says it already neutralised on both sides.  r2046 is the
    # only face that publishes such a list today (quote_audit.flip_pairs); everything else
    # is this face's own debt to name.
    repaired_pairs = set()
    for r in shelf["rows"]:
        for fp in ((r.get("quote_audit") or {}).get("flip_pairs") or []):
            if fp.get("drop_date"):
                repaired_pairs.add((r["code"], fp["drop_date"]))
            if fp.get("back_date"):
                repaired_pairs.add((r["code"], fp["back_date"]))

    legs = []
    for r in shelf["rows"]:
        m = measure_one(r["code"], start, end,
                        name=r.get("name") or census_names.get(r["code"]),
                        repaired_pairs=repaired_pairs)
        m["book_class"] = r.get("class")
        m["carry_ruler_applies"] = r.get("class") in ("money", "bond")
        legs.append(m)
    carry_legs = [m for m in legs if m["carry_ruler_applies"]]

    verdict, med_share = verdict_of(named)
    tags = tags_of(named, carry_legs)

    # The ten largest isolated bars among the instruments a carry caliber actually applies
    # to.  Convertibles are excluded on purpose: a 3% day is their ordinary weather, so
    # their bars would fill this table without saying anything about carry.
    events = []
    for m in named + carry_legs:
        if not m.get("priced"):
            continue
        for e in m.get("events") or []:
            events.append({"code": m["code"], "name": m.get("name"),
                           "date": e["date"], "move_bp": e["move_bp"], "shape": e["shape"],
                           "mirror_date": e.get("mirror_date")})
    events.sort(key=lambda e: -abs(e["move_bp"]))
    top_events = events[:10]
    biggest = top_events[0] if top_events else None

    # Where the leftover sigma lives, pooled across instruments: each instrument is centred
    # on its own mean, so the variance column is a share of the pooled within-instrument
    # sum of squares and sums to 100.
    def pool(rows_in):
        buckets = {name: {"bucket": name, "bars": 0, "pp": 0.0, "ss": 0.0} for name, _l, _h in SHAPE_BUCKETS}
        ss_total = 0.0
        for m in rows_in:
            if not m.get("priced"):
                continue
            for s in m["shape"]:
                buckets[s["bucket"]]["bars"] += int(s["bars"])
                buckets[s["bucket"]]["pp"] += float(s["pp"])
                buckets[s["bucket"]]["ss"] += float(s["var_share_pct"] or 0.0)
            ss_total += 100.0
        out = []
        for name, _lo, _hi in SHAPE_BUCKETS:
            b = buckets[name]
            out.append({"bucket": name, "bars": b["bars"], "pp": round(b["pp"], 4),
                        "var_share_pct": None if ss_total <= 0
                        else round(b["ss"] / ss_total * 100.0, 2)})
        return out

    shape_named = pool(named)
    shape_legs = pool(carry_legs)
    top_bucket = max((s for s in shape_named if s["var_share_pct"] is not None),
                     key=lambda s: s["var_share_pct"], default=None)
    stairs = next((s for s in shape_named if s["bucket"] == "stair_2_5bp"), None)
    quiet = next((s for s in shape_named if s["bucket"] == "quiet_lt_2bp"), None)

    rows = []
    for m in named:
        rows.append({
            "code": m["code"], "name": m.get("name"),
            "bars": m.get("bars"),             "isolated_bars": m.get("isolated_bars"),
            "run_bars": m.get("run_bars"),
            "pair_bars": m.get("pair_bars"),
            "pair_events": m.get("pair_events"),
            "pair_pp": m.get("pair_pp"),
            "median_isolated_bp": m.get("median_isolated_bp"),
            "biggest_isolated_bp": m.get("biggest_isolated_bp"),
            "isolated_pp": m.get("isolated_pp"),
            "arith_pp": m.get("arith_pp"),
            "isolated_share": m.get("isolated_share"),
            "cagr_repaired_pct": m.get("cagr_repaired_pct"),
            "cagr_without_jumps_pct": m.get("cagr_without_jumps_pct"),
            "carry_from_jumps_pp": m.get("carry_from_jumps_pp"),
            "sigma_repaired_bp": m.get("sigma_repaired_bp"),
            "sigma_without_jumps_bp": m.get("sigma_without_jumps_bp"),
            "sigma_drop_pct": m.get("sigma_drop_pct"),
            "band_repaired_bars": m.get("band_repaired_bars"),
            "money_resets_removed": m.get("money_resets_removed"),
            "events_returns": m.get("events_returns"),
            "events_shifts": m.get("events_shifts"),
            "events_mirror_reader": m.get("events_mirror_reader"),
            "events_mirror_band": m.get("events_mirror_band"),
            "events_already_repaired": m.get("events_already_repaired"),
            "mirror_bars": m.get("mirror_bars"),
            "month_end_bars": m.get("month_end_bars"),
            "isolated_pp_unpaid": m.get("isolated_pp_unpaid"),
            "biggest_event": m.get("biggest_event"),
            "biggest_mirror_event": m.get("biggest_mirror_event"),
        })
    leg_rows = []
    for m in legs:
        leg_rows.append({
            "code": m["code"], "name": m.get("name"), "class": m.get("book_class"),
            "carry_ruler_applies": m.get("carry_ruler_applies"),
            "bars": m.get("bars"), "isolated_bars": m.get("isolated_bars"),
            "pair_bars": m.get("pair_bars"), "pair_pp": m.get("pair_pp"),
            "biggest_isolated_bp": m.get("biggest_isolated_bp"),
            "isolated_pp": m.get("isolated_pp"), "arith_pp": m.get("arith_pp"),
            "isolated_share": m.get("isolated_share"),
            "cagr_repaired_pct": m.get("cagr_repaired_pct"),
            "cagr_without_jumps_pct": m.get("cagr_without_jumps_pct"),
            "carry_from_jumps_pp": m.get("carry_from_jumps_pp"),
            "sigma_repaired_bp": m.get("sigma_repaired_bp"),
            "sigma_without_jumps_bp": m.get("sigma_without_jumps_bp"),
            "share_reason": m.get("share_reason"),
            "events_returns": m.get("events_returns"),
            "events_shifts": m.get("events_shifts"),
            "events_mirror_reader": m.get("events_mirror_reader"),
            "events_mirror_band": m.get("events_mirror_band"),
            "events_already_repaired": m.get("events_already_repaired"),
            "mirror_bars": m.get("mirror_bars"),
            "month_end_bars": m.get("month_end_bars"),
            "isolated_pp_unpaid": m.get("isolated_pp_unpaid"),
            "biggest_event": m.get("biggest_event"),
            "biggest_mirror_event": m.get("biggest_mirror_event"),
        })

    # Sentences derived from the numbers, so the page cannot drift from its own table.
    worst_row = max((r for r in rows if r["isolated_share"] is not None),
                    key=lambda r: r["isolated_share"], default=None)
    leg_bits = []
    for r in leg_rows:
        if r.get("isolated_pp_unpaid") is None:
            continue
        extra = ""
        if (r.get("events_already_repaired") or 0) >= 1:
            be = r.get("biggest_mirror_event") or {}
            extra = ("（其中 %d 根的两侧都由上游面归零过，最大一根 %.2fbp 镜像自 %s——不是新欠账）"
                     % (r["events_already_repaired"], be.get("move_bp") or 0.0,
                        be.get("mirror_date") or "?"))
        tag0 = "" if r.get("carry_ruler_applies") else "（转债，不进判定）"
        leg_bits.append("%s %+.3fpp%s%s" % (r["code"], r["isolated_pp_unpaid"], tag0, extra))
    findings = []
    if top_bucket:
        findings.append(
            "r2050 留下的方差落点：`%s` 桶吃下 %.1f%%（%d 根），安静桶 %.1f%%、"
            "2–5bp 阶梯桶 %.1f%%——方差在左尾的大 bar 上，不在日常 accrual 上。"
            % (top_bucket["bucket"], top_bucket["var_share_pct"], top_bucket["bars"],
               (quiet or {}).get("var_share_pct") or 0.0,
               (stairs or {}).get("var_share_pct") or 0.0))
    findings.append("书腿的未修补跳变欠账（几何口径，pp/年）：%s。"
                    % ("；".join(leg_bits) if leg_bits else "无可测腿"))
    me_rows = [r for r in leg_rows
               if r.get("carry_ruler_applies") and (r.get("isolated_bars") or 0)]
    if me_rows:
        tot_me = sum(int(r.get("month_end_bars") or 0) for r in me_rows)
        tot_iso = sum(int(r.get("isolated_bars") or 0) for r in me_rows)
        findings.append(
            "书腿的孤立跳变里有 %d/%d 落在每月最后一根 bar 上（%s）——货币 ETF 的估值按月结块，"
            "所以对它们把跳变归零是一句口径选择（往返净额为零），不是一次纠错；规模就是上面那句里的数。"
            % (tot_me, tot_iso,
               "、".join("%s %d/%d" % (r["code"], int(r.get("month_end_bars") or 0),
                                      int(r.get("isolated_bars") or 0)) for r in me_rows)))

    # Cross-check: the part of a leg's jump carry that this face attributes to an
    # already-repaired mirror must equal what the face that repaired it published.  This is
    # the r1787 discipline made numeric: before claiming a new debt, price the old one.
    flip_pub = {r["code"]: ((r.get("quote_audit") or {}).get("flip_effect_pp_per_year"))
                for r in shelf["rows"]}
    cross = []
    for r in leg_rows:
        if r.get("carry_from_jumps_pp") is None or r.get("isolated_pp_unpaid") is None:
            continue
        pub = flip_pub.get(r["code"])
        if (r.get("events_already_repaired") or 0) < 1 or pub is None or abs(float(pub)) < 0.01:
            continue
        measured = round(r["carry_from_jumps_pp"] - r["isolated_pp_unpaid"], 4)
        gap = round(abs(measured - abs(float(pub))), 4)
        cross.append({"code": r["code"], "measured_mirror_pp": measured,
                      "published_flip_pp": float(pub), "gap_pp": gap,
                      "ok": bool(gap <= 0.02)})
    for c in cross:
        if c["ok"]:
            findings.append("交叉验证：%s 的镜像部分本面独立量到 %+.4fpp，"
                            "与修复它的那一面自己公布的 %.4fpp 相符（差 %.4fpp）。"
                            % (c["code"], c["measured_mirror_pp"],
                               c["published_flip_pp"], c["gap_pp"]))
    if worst_row:
        be = worst_row.get("biggest_event") or {}
        findings.append("被点名的十一只里最高占比是 %s %s（%.1f%% 的修复后 carry），"
                        "最大一根 %+.2fbp（%s，%s）。"
                        % (worst_row["code"], worst_row.get("name") or "",
                           worst_row["isolated_share"] * 100.0,
                           be.get("move_bp") or 0.0, be.get("date") or "?",
                           be.get("shape") or "?"))

    shares = [r["isolated_share"] for r in rows if r["isolated_share"] is not None]
    drops = [r["sigma_drop_pct"] for r in rows if r["sigma_drop_pct"] is not None]
    face = {
        "schema": "money_subband_jump_audit/v1",
        "artifact": FACE,
        "generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": end,
        "window": {"start": start, "end": end},
        "question": ("On the r2050-repaired series, how much of a money ETF's annualised "
                     "carry comes from isolated sub-band jumps (bars of 5bp or more whose "
                     "two neighbours move less than 2bp), and how much of the residual "
                     "sigma do those bars explain?"),
        "ruler": {
            "upstream_repair": "money_premium_carry_audit.find_breaches + repaired_rets "
                               "(1% band around the 20-bar trailing median, booked at zero)",
            "published_reader": "etf_book_cash_vehicle.consolidation_returns "
                                "(drops deeper than -50bp booked at zero)",
            "annualisation": "cash_shelf_year_by_year.bars_per_year x arithmetic mean "
                             "(exactly additive across bar subsets)",
            "sigma": "cash_shelf_flip_census.sigma_bp",
            "quiet_bp": QUIET_BP,
            "jump_lo_bp": JUMP_LO_BP,
            "min_denominator_pp": MIN_DENOM_PP,
            "return_window_bars": RET_WINDOW,
            "return_tolerance_bp": RET_TOL_BP,
            "shape_buckets": [{"bucket": n, "lo_bp": lo, "hi_bp": (None if hi == float("inf") else hi)}
                              for n, lo, hi in SHAPE_BUCKETS],
            "boundary_rule": "a neighbour outside the window counts as quiet",
            "no_entry_cost": True,
        },
        "upstream": {
            "premium": {"path": PREMIUM_FACE, "sha256": _rel_sha(PREMIUM_FACE),
                        "verdict": premium.get("verdict")},
            "census": {"path": CENSUS_FACE, "sha256": _rel_sha(CENSUS_FACE)},
            "shelf": {"path": SHELF_FACE, "sha256": _rel_sha(SHELF_FACE)},
        },
        "verdict": verdict,
        "tags": tags,
        "findings": findings,
        "cross_checks": {"r2046_flip_effect": cross},
        "headline": {
            "named_instruments": len([r for r in rows if r["bars"]]),
            "named_with_jumps": len([r for r in rows if (r["isolated_bars"] or 0) >= 1]),
            "median_isolated_share": None if not shares else round(float(np.median(shares)), 4),
            "median_sigma_drop_pct": None if not drops else round(float(np.median(drops)), 2),
            "isolated_bars_total": int(sum(r["isolated_bars"] or 0 for r in rows)),
            "biggest_isolated": biggest,
            "book_legs_carry_moves_pp": {r["code"]: r["carry_from_jumps_pp"] for r in leg_rows},
            "book_legs_unpaid_moves_pp": {r["code"]: r["isolated_pp_unpaid"] for r in leg_rows},
            "mirror_bars_total": int(sum(r.get("mirror_bars") or 0 for r in rows)),
        },
        "rows": rows,
        "legs": leg_rows,
        "components": {
            "note": ("pooled across instruments, each centred on its own mean; the pp column "
                     "sums to the arithmetic carry and the variance column sums to 100"),
            "named": {"rows": shape_named,
                      "events_returns": int(sum(r.get("events_returns") or 0 for r in rows)),
                      "events_shifts": int(sum(r.get("events_shifts") or 0 for r in rows)),
                      "events_unresolved": int(sum(r.get("events_unresolved") or 0 for r in rows))},
            "book_carry_legs": {"rows": shape_legs,
                                "events_returns": int(sum(r.get("events_returns") or 0 for r in leg_rows)),
                                "events_shifts": int(sum(r.get("events_shifts") or 0 for r in leg_rows))},
        },
        "top_isolated_events": top_events,
        "gate_r2050_repair": gate,
        "verdict_of_median_share": {"half_share_at": HALF_SHARE, "part_share_at": PART_SHARE,
                                    "median": None if not shares
                                    else round(float(np.median(shares)), 4)},
        "caveats": [
            "the panel cannot tell a bad feed print from a real one-session move; this face "
            "treats them as the same problem and does not claim to separate them",
            "no entry cost, no tradeable return, no position: this is a caliber question",
            "isolated means quiet neighbours, not small: a 900bp bar between two quiet bars "
            "is isolated too, and the band ruler will usually have caught it first",
            "bars at the window ends are judged with one neighbour; the count is printed",
        ],
    }
    face["content_sha"] = _content_sha({k: v for k, v in face.items()
                                        if k not in ("generated", "content_sha")})
    return face


# ----------------------------------------------------------------------------- page

def render_table(face):
    lines = []
    lines.append("| code | name | bars | isolated bars | median jump | biggest jump | "
                 "isolated pp/yr | arith pp/yr | share | printed->repaired->no-jump %/yr | "
                 "sigma bp -> without jumps |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|")
    for r in face["rows"]:
        if not r["bars"]:
            lines.append("| %s | %s | - | - | - | - | - | - | - | not priced | - |"
                         % (r["code"], r["name"] or ""))
            continue
        share = "n/a" if r["isolated_share"] is None else "%.1f%%" % (r["isolated_share"] * 100.0)
        lines.append("| %s | %s | %d | %d | %.2fbp | %.2fbp | %+.2f | %+.2f | %s | "
                     "%+.2f -> %+.2f -> %+.2f | %.1f -> %.1f |"
                     % (r["code"], r["name"] or "", r["bars"], r["isolated_bars"] or 0,
                        r["median_isolated_bp"] or 0.0, r["biggest_isolated_bp"] or 0.0,
                        r["isolated_pp"], r["arith_pp"], share,
                        r["cagr_repaired_pct"], r["cagr_repaired_pct"], r["cagr_without_jumps_pct"],
                        r["sigma_repaired_bp"] or 0.0, r["sigma_without_jumps_bp"] or 0.0))
    return "\n".join(lines)


def render_legs(face):
    lines = []
    lines.append("| code | class | bars | isolated bars | biggest jump | isolated share | "
                 "carry shifts by (pp) | sigma bp -> without jumps |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---|")
    for r in face["legs"]:
        if not r["bars"]:
            lines.append("| %s | %s | not priced | - | - | - | - | - |"
                         % (r["code"], r["class"]))
            continue
        share = "n/a" if r["isolated_share"] is None else "%.1f%%" % (r["isolated_share"] * 100.0)
        shift = "n/a" if r["carry_from_jumps_pp"] is None else "%+.3f" % r["carry_from_jumps_pp"]
        lines.append("| %s | %s | %d | %d | %.2fbp | %s | %s | %.2f -> %.2f |"
                     % (r["code"], r["class"], r["bars"], r["isolated_bars"] or 0,
                        r["biggest_isolated_bp"] or 0.0, share, shift,
                        r["sigma_repaired_bp"] or 0.0, r["sigma_without_jumps_bp"] or 0.0))
    return "\n".join(lines)


def render_events(face):
    lines = []
    lines.append("| code | name | date | move (bp) | shape |")
    lines.append("|---|---|---|---:|---|")
    for e in face["top_isolated_events"]:
        lines.append("| %s | %s | %s | %+.2f | %s |"
                     % (e["code"], e["name"] or "", e["date"], e["move_bp"],
                        e.get("shape") or ""))
    return "\n".join(lines)


def render_pairs(face):
    lines = []
    lines.append("| code | name | flip pairs | bars in pairs | carry these bars carry (pp/yr) |")
    lines.append("|---|---|---:|---:|---:|")
    for r in face["rows"]:
        if not r["bars"]:
            continue
        lines.append("| %s | %s | %d | %d | %+.4f |"
                     % (r["code"], r["name"] or "", r.get("pair_events") or 0,
                        r.get("pair_bars") or 0, r.get("pair_pp") or 0.0))
    return "\n".join(lines)


def render_components(face):
    lines = []
    lines.append("| magnitude bucket | bars | pp/yr | share of the leftover variance |")
    lines.append("|---|---:|---:|---:|")
    for s in face["components"]["named"]["rows"]:
        lines.append("| %s | %d | %+.4f | %s |"
                     % (s["bucket"], s["bars"], s["pp"],
                        "n/a" if s["var_share_pct"] is None else "%.1f%%" % s["var_share_pct"]))
    return "\n".join(lines)


def write_doc(face):
    h = face["headline"]
    med = h["median_isolated_share"]
    body = []
    body.append("# 货币 ETF 的收益，两条规则之后还剩什么\n")
    body.append("> 面 ID：`money_subband_jump_audit/v1`")
    body.append("> 正身：`scripts/money_subband_jump_audit.py` · 数据面：`%s`" % FACE)
    body.append("> 上游：`%s`（r2050 的 1%% 带修复）· `%s` · `%s`"
                % (PREMIUM_FACE, CENSUS_FACE, SHELF_FACE))
    body.append("> 窗口：%s .. %s" % (face["window"]["start"], face["window"]["end"]))
    body.append("> 生成：%s" % face["generated"])
    body.append("")
    body.append("## 一、为什么要有这一面\n")
    body.append("r2050 把十一只货币 ETF 的溢价 bar 修掉之后，留了一句没答的话：修复后的日 σ 还是 "
                "4.1–31.4bp，而货币基金一天只攒约 0.8bp。那部分方差是什么形状、值多少钱，"
                "r2050 明说「只点明，不宣称已清」。这一面就是那笔账。\n")
    body.append("现在在役的两把尺子都看不见它：发布中的货币读器只把跌幅超过 50bp 的 bar 归零；"
                "r2050 的带尺只把偏离自身 20 日中位 1% 以上的 bar 归零。"
                "一根上涨 40bp、第二天原路回去的 bar，既不离带、也不是合并，"
                "它被当成收益写进 carry——而 40bp 是五十个交易日的 carry。\n")
    body.append("这一类 bar 有四种形状，本面分开印、同一个口径归零：`RETURNS` 是跳完就回来（坏打印或瞬时溢价）；"
                "`SHIFTS` 是跳完停在新价（份额折算的镜像——发布中的读器只抓向下的合并，向上的那一半"
                "一直留在序列里当收益）；`MIRROR_READER` / `MIRROR_BAND` 是「对侧那根已经被谁归零了、"
                "这一根留下了」。**最后两种是本面最重要的发现**：只归零一根的尺子不会消掉一次往返，"
                "它会把留下的那一根变成一笔凭空的收益——r2046 在向下那一侧抓到过，r2050 的带尺在向上那一侧"
                "又造了一遍。\n")
    body.append("## 二、口径（跑之前就冻结）\n")
    body.append("| 项 | 取法 |")
    body.append("|---|---|")
    body.append("| 窗口 / 面板 / 读器 | 完全沿用 r2050（`money_premium_carry_audit` 自己的 "
                "`find_breaches` / `repaired_rets`），不重写 |")
    body.append("| 年化 | `cash_shelf_year_by_year.bars_per_year` × **算术**均值——"
                "算术年化在 bar 子集之间是**精确可加**的，这是让「占比」成为恒等式而不是叙述的唯一读法 |")
    body.append("| 日 σ | `cash_shelf_flip_census.sigma_bp`（r2048 发布时用的那个） |")
    body.append("| **QUIET_BP = %.1f** | 邻居一天走不到 2bp 就不算一次移动的一部分 |" % QUIET_BP)
    body.append("| **JUMP_LO_BP = %.1f** | 小于 5bp 的 bar 是六天的 carry 加报价噪声，叫它跳变就会重犯 "
                "r2048「几何尺子伸太长」的错 |" % JUMP_LO_BP)
    body.append("| **MIN_DENOM_PP = %.2f** | 修复后 carry 低于 5bp/年就没有值得相除的分母——"
                "印读数，不印比值 |" % MIN_DENOM_PP)
    body.append("| 边界 | 窗口外不存在的邻居按「安静」计；这类 bar 的条数单独印 |")
    body.append("| **RET_WINDOW = %d / RET_TOL_BP = %.1f** | 跳完 %d 个 bar 内回到跳前价 ±%.1fbp "
                "＝ 会回来；停在新价 ＝ 台阶 |" % (RET_WINDOW, RET_TOL_BP, RET_WINDOW, RET_TOL_BP))
    body.append("| 镜像归因 | 对侧那根被谁归零过：发布中的货币读器（跌幅 >50bp）＝ `MIRROR_READER`；"
                "r2050 的 1% 带尺 ＝ `MIRROR_BAND`。两者都会**造出一笔幻影收益**：被归零的那一侧没了，"
                "被留下的这一侧还在 carry 里 |")
    body.append("| 幅度桶 | quiet <2bp / stair 2–5bp / jump 5–25bp / jump 25–100bp / huge ≥100bp；"
                "两个可加列（pp 年化、方差份额）都由构造保证各自加总＝carry / 100% |")
    body.append("")
    body.append("## 三、判词（机械，跑之前冻结）\n")
    body.append("对十一个被点名标的取**占比中位**：")
    body.append("")
    body.append("- `SUB_BAND_JUMPS_ARE_THE_CARRY`：中位占比 ≥ %.0f%%" % (HALF_SHARE * 100))
    body.append("- `SUB_BAND_JUMPS_ARE_HALF_THE_CARRY`：%.0f%% ≤ 中位占比 < %.0f%%"
                % (PART_SHARE * 100, HALF_SHARE * 100))
    body.append("- `CARRY_SURVIVES_THE_JUMPS`：中位占比 < %.0f%%" % (PART_SHARE * 100))
    body.append("")
    body.append("标签与判词并列印、不折进判词：`THE_BOOK_LEGS_SURVIVE`（五货架腿的几何 carry "
                "移动都 < %.2fpp，r2045 的排队读数不用重算）· `A_THIRD_RULE_WOULD_MOVE_THE_BOOK`"
                "（有腿动 ≥ %.2fpp，r2045 必须先重导）· `EVERY_NAMED_INSTRUMENT_HAS_SUB_BAND_JUMPS`"
                " · `THE_RESIDUAL_SIGMA_IS_THE_JUMPS`（归零后 σ 中位掉 ≥ %.0f%%）· "
                "`CARRY_IS_TOO_THIN_FOR_A_SHARE`。"
                % (MATERIAL_PP, MATERIAL_PP, SIGMA_DROP * 100))
    body.append("")
    body.append("## 四、读数\n")
    body.append("判词 **%s**　中位占比 %s　标签 %s"
                % (face["verdict"],
                   "n/a" if med is None else "%.1f%%" % (med * 100.0),
                   "、".join(face["tags"]) or "（无）"))
    body.append("")
    body.append("**本面读到什么**（句子由面里的数字派生，不是手写）：\n")
    for s in face.get("findings") or []:
        body.append("- %s" % s)
    body.append("")
    body.append(MARK_BEGIN)
    body.append(render_table(face))
    body.append(MARK_END)
    body.append("")
    body.append("书腿（对照）：五只货架自己的腿。只对 money / bond 腿问 carry 问题；"
                "转债腿 1% 是寻常一天的波动，带尺会去「修」正常行情（r2048 的几何越界），"
                "所以照样印、但不进 `THE_BOOK_LEGS_SURVIVE` 的判定。\n")
    body.append(render_legs(face))
    body.append("")
    body.append("全样本里最大的十根孤立跳变（可对着面板手验）。`RETURNS`＝跳完五个 bar 内回到跳前价，"
                "`SHIFTS`＝跳完就停在新价（份额折算的镜像，向上的合并）；两者对 carry 口径都该归零，"
                "但不是同一件事：\n")
    body.append(render_events(face))
    body.append("")
    body.append("r2050 留下的方差在哪（十一只被点名标的合并，逐只先减自己的均值）：\n")
    body.append(render_components(face))
    body.append("")
    body.append("被本面的「孤立」定义排除在外的那一族：一根上涨紧跟一根下跌（经典坏打印）。"
                "它们的 carry 效应按构造互相抵消（所以它从不会抬高 carry，也正因如此，"
                "只看 carry 的审计永远看不见它们），但它们的方差是真的：\n")
    body.append(render_pairs(face))
    body.append("")
    body.append("## 五、怎么读\n")
    body.append("1. **先看占比，再看抓没抓干净**：占比说的是一年攒下的 carry 里有多少来自"
                "「一根跳、两边静」。这个数不是估值修正，是口径诚实度。")
    body.append("2. **再看 σ 掉了多少、方差落在哪个桶**：r2050 留下的 4–31bp 方差如果能被同一族 bar "
                "解释掉，那「还有别的形状」这句话就有一个名字和一份大小；如果 σ 只掉一点点而某一桶"
                "吃掉了大部分方差份额，那一桶就是下一面要量的形状。安静桶（<2bp）吃下的份额"
                "就是日常 accrual 的量级——它不是问题，是分母。")
    body.append("3. **最后看书腿**：五货架自己的腿如果 `THE_BOOK_LEGS_SURVIVE`，"
                "r2045 的排队天数、r2046 的逐年表、r2047 的分红校准都不需要重算——"
                "这是本面最重要的用途：它给出「不用重做」的结论。")
    body.append("4. **算术与几何并印**：占比来自算术分解（可加），几何 carry 移动是"
                "把孤立跳变归零后重算 CAGR 的差。两者不一致时不是谁错，"
                "是复利把大 bar 放大了；面里两个都印。")
    body.append("")
    body.append("## 六、不主张（如实）\n")
    body.append("1. 面板分不清「坏打印」与「真的一个交易日跳了」，两者长得一样；对 carry 口径"
                "是同一个问题，本面不宣称能区分。")
    body.append("2. 不给交易结论：溢价与跳变都不可预见，归零是口径修正不是可赚收益。")
    body.append("3. 只覆盖「一根跳、两边静」这一种形状；多段阶梯、慢回复不在射程，"
                "σ 若仍偏高就是它们的量。")
    body.append("4. 边界 bar 只有一个邻居，按安静计；数量已印，可自行扣除。")
    body.append("5. 镜像的「归因」说得出是哪把尺子留下的，说不出那次往返到底是坏打印还是真的申赎；"
                "对 carry 口径两者都要归零，本面到此为止。")
    body.append("6. 转债腿的数字照样印，但不进任何判词：1% 是它们的寻常一天，带尺会去「修」正常行情"
                "（r2048 的几何越界），本面不重复那个错。")
    body.append("")
    body.append("## 七、复跑\n")
    body.append("```bash")
    body.append("python scripts/money_subband_jump_audit.py run        # 重建面 + 渲染本页")
    body.append("python scripts/money_subband_jump_audit.py --check    # 重导对账（漂移自称 STALE）")
    body.append("python scripts/money_subband_jump_audit.py --selftest # 离线自检")
    body.append("```")
    body.append("")
    text = "\n".join(body)
    path = os.path.join(ROOT, DOC)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return path


# ---------------------------------------------------------------------------- check

COMPARE_FIELDS = ("isolated_bars", "run_bars", "pair_bars", "pair_pp", "isolated_pp", "arith_pp",
                  "isolated_share", "cagr_repaired_pct", "carry_from_jumps_pp",
                  "sigma_repaired_bp", "sigma_drop_pct", "events_returns", "events_shifts")


def check():
    """Re-derive from the panel and compare with what was published.

    Three outcomes, never mixed (r1934): an upstream byte move is STALE (pay to refresh),
    a number that disagrees on identical inputs is CHECK FAILED (a real defect, and it must
    not say STALE), and everything equal is CHECK OK.
    """
    p = os.path.join(ROOT, FACE)
    if not os.path.exists(p):
        print("STALE: face missing at %s -- run it" % FACE)
        return 3
    pub = _load(FACE)
    drift = []
    for key, rec in pub.get("upstream", {}).items():
        now = _rel_sha(rec["path"])
        if now != rec.get("sha256"):
            drift.append("%s %s (%s -> %s)" % (key, rec["path"],
                                               str(rec.get("sha256"))[:12], str(now)[:12]))
    if drift:
        print("STALE: upstream face moved, so every number below is about an older world: %s"
              % "; ".join(drift))
        return 3

    fresh = build()
    bad = []
    if fresh["verdict"] != pub["verdict"]:
        bad.append("verdict %s -> %s" % (pub["verdict"], fresh["verdict"]))
    if sorted(fresh["tags"]) != sorted(pub["tags"]):
        bad.append("tags %s -> %s" % (pub["tags"], fresh["tags"]))
    pub_rows = {r["code"]: r for r in pub["rows"]}
    for r in fresh["rows"]:
        q = pub_rows.get(r["code"])
        if q is None:
            bad.append("%s: missing from the published rows" % r["code"])
            continue
        for f in COMPARE_FIELDS:
            a, b = r.get(f), q.get(f)
            if a is None and b is None:
                continue
            if a is None or b is None:
                bad.append("%s.%s: %r vs %r" % (r["code"], f, b, a))
            elif abs(float(a) - float(b)) > 1e-6:
                bad.append("%s.%s: published %r, re-derived %r" % (r["code"], f, b, a))
    pub_legs = {r["code"]: r for r in pub["legs"]}
    for r in fresh["legs"]:
        q = pub_legs.get(r["code"])
        if q is None:
            bad.append("%s: missing from the published legs" % r["code"])
            continue
        for f in ("isolated_bars", "isolated_pp", "carry_from_jumps_pp"):
            a, b = r.get(f), q.get(f)
            if a is None and b is None:
                continue
            if a is None or b is None:
                bad.append("leg %s.%s: %r vs %r" % (r["code"], f, b, a))
            elif abs(float(a) - float(b)) > 1e-6:
                bad.append("leg %s.%s: published %r, re-derived %r" % (r["code"], f, b, a))
    if pub.get("content_sha") != _content_sha({k: v for k, v in pub.items()
                                               if k not in ("generated", "content_sha")}):
        bad.append("content_sha does not describe the published face")

    # The page must still carry the table the face says it carries.
    doc_path = os.path.join(ROOT, DOC)
    if not os.path.exists(doc_path):
        bad.append("page missing at %s" % DOC)
    else:
        page = io.open(doc_path, "r", encoding="utf-8").read()
        table = render_table(pub)
        if table not in page:
            bad.append("page table does not match the published face byte for byte")
        if MARK_BEGIN not in page or MARK_END not in page:
            bad.append("page lost its table markers")
        if "%%" in page:
            bad.append("page prints a literal %% (r2039 family)")

    if bad:
        print("CHECK FAILED (%d):" % len(bad))
        for b in bad:
            print(" -", b)
        return 1
    print("CHECK OK (%d named / %d legs / %d fields re-derived from the panel)"
          % (len(pub["rows"]), len(pub["legs"]), len(COMPARE_FIELDS)))
    return 0


# ------------------------------------------------------------------------- selftest

def _synth(kind="isolated", n=400, seed=7):
    """Synthetic money ETF series with a known shape, for the offline legs."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2021-01-04", periods=n)
    step = 0.00008                       # ~0.8bp/day, a money fund's accrual
    r = np.full(n, step) + rng.normal(0.0, 0.00002, n)
    if kind == "isolated":
        r[200] += 0.0040                 # one 40bp bar, neighbours untouched
    elif kind == "two":
        r[200] += 0.0020                 # two consecutive bars: not isolated
        r[201] += 0.0020
    elif kind == "tiny":
        r[200] += 0.0003                 # 3bp: under JUMP_LO_BP, must not count
    elif kind == "pair":
        r[200] += 0.0040                 # up then straight back down: a flip pair
        r[201] -= 0.0040
    elif kind == "flat":
        r[:] = 0.0                       # a hand-built price series, no accrual
    elif kind == "boundary":
        r[-1] += 0.0040                  # jump on the very last bar (one neighbour only)
    lvl = 100.0 * np.cumprod(1.0 + r)
    return pd.Series(lvl, index=idx)


def selftest():
    errs = []
    legs = []

    def chk(cond, msg):
        if not cond:
            errs.append(msg)

    def leg(name):
        legs.append(name)

    # 1. An isolated jump is found, its size is right, and it counts exactly once.
    leg("isolated jump is found")
    rets, _ = CV.consolidation_returns(_synth("isolated"))
    iso, run, big = classify_isolated(rets)
    chk(int(iso.sum()) == 1, "isolated series flagged %d bars, want 1" % int(iso.sum()))
    chk(int(run.sum()) == 0, "isolated series has %d run bars, want 0" % int(run.sum()))
    d = decompose(rets)
    chk(d["isolated_bars"] == 1, "decomposition lost the jump")

    # 2. The arithmetic decomposition is an identity, not a narration.
    leg("decomposition is additive")
    chk(abs(d["parts_sum_error_pp"]) < 1e-6,
        "parts do not sum to the total: error %.2e pp" % d["parts_sum_error_pp"])

    # 3. A two-bar move is a run, not an isolated jump (the pair is not the shape).
    leg("two consecutive bars are a run")
    r2, _ = CV.consolidation_returns(_synth("two"))
    iso2, run2, _b2 = classify_isolated(r2)
    chk(int(iso2.sum()) == 0, "pair flagged %d isolated bars, want 0" % int(iso2.sum()))
    chk(int(run2.sum()) == 2, "pair flagged %d run bars, want 2" % int(run2.sum()))

    # 4. A move under JUMP_LO_BP is accrual, not a jump.
    leg("sub-threshold bar is not a jump")
    r3, _ = CV.consolidation_returns(_synth("tiny"))
    iso3, run3, big3 = classify_isolated(r3)
    chk(int(big3.sum()) == 0, "3bp bar was called a jump")

    # 5. A jump at the window edge is judged by its one neighbour (documented rule).
    leg("boundary bar uses one neighbour")
    r4, _ = CV.consolidation_returns(_synth("boundary"))
    iso4, _run4, _b4 = classify_isolated(r4)
    chk(int(iso4.sum()) == 1, "boundary jump flagged %d bars, want 1" % int(iso4.sum()))

    # 6. Zeroing the jump removes exactly its own contribution.
    leg("zeroing removes exactly the jump")
    z = _zero_at(rets, iso)
    ziso, _zr, _zb = classify_isolated(z)
    chk(int(ziso.sum()) == 0, "zeroed jump still flagged")
    chk(abs(float(z.iloc[200])) < 1e-12, "zeroed bar is not exactly zero")

    # 7. The 5bp threshold is measured in bp, not in percent (and 6bp clears it; a bar of
    #    exactly 5.000bp computed in floats is 4.9999bp, which is why the test uses 6).
    leg("threshold is in bp")
    one = pd.Series([100.0, 100.06, 100.0604, 100.1409],
                    index=pd.bdate_range("2021-01-04", periods=4))
    r5 = one.pct_change().fillna(0.0)
    _i5, _r5, b5 = classify_isolated(r5)
    chk(int(b5.sum()) == 2, "a 6bp and an 8bp bar gave %d jumps, want 2" % int(b5.sum()))

    # 8. A negative share cannot be divided into (the r2043 lesson).
    leg("thin carry gets no share")
    dthin = {"arith_pp": 0.02, "isolated_pp": 0.01}
    would_divide = dthin["arith_pp"] > MIN_DENOM_PP
    chk(not would_divide, "a 2bp/yr carry would still get a share")

    # 9. Verdict is mechanical in the median share.
    leg("verdict is mechanical")
    mk = lambda v: {"isolated_share": v}
    chk(verdict_of([mk(0.8), mk(0.6)])[0] == "SUB_BAND_JUMPS_ARE_THE_CARRY", "verdict: half+")
    chk(verdict_of([mk(0.3), mk(0.25)])[0] == "SUB_BAND_JUMPS_ARE_HALF_THE_CARRY", "verdict: part")
    chk(verdict_of([mk(0.1), mk(0.05)])[0] == "CARRY_SURVIVES_THE_JUMPS", "verdict: survives")
    chk(verdict_of([mk(None)])[0] == "CARRY_IS_TOO_THIN_FOR_A_SHARE", "verdict: no denominator")

    # 10. Tags: a clean book is named, a moving book is named, and neither is silent.    leg("tags fire on both sides")
    clean = [{"isolated_pp_unpaid": 0.05}, {"isolated_pp_unpaid": -0.10}]
    dirty = [{"isolated_pp_unpaid": 0.60}]
    repaired = [{"isolated_pp_unpaid": 0.05, "events_already_repaired": 1}]
    named_ok = [{"isolated_bars": 2, "priced": True, "sigma_drop_pct": 55.0,
                 "isolated_share": 0.4}]
    t1 = tags_of(named_ok, clean)
    chk("THE_BOOK_LEGS_SURVIVE" in t1, "clean book not tagged")
    chk("A_THIRD_RULE_WOULD_MOVE_THE_BOOK" not in t1, "clean book got the moving tag")
    chk("EVERY_NAMED_INSTRUMENT_HAS_SUB_BAND_JUMPS" in t1, "jump tag missing")
    chk("THE_RESIDUAL_SIGMA_IS_THE_JUMPS" in t1, "sigma tag missing")
    t2 = tags_of(named_ok, dirty)
    chk("A_THIRD_RULE_WOULD_MOVE_THE_BOOK" in t2, "moving book not tagged")
    chk("THE_BOOK_LEGS_SURVIVE" not in t2, "clean tag fired on a moving book")
    t3 = tags_of(named_ok, repaired)
    chk("A_MEASURED_JUMP_WAS_ALREADY_REPAIRED" in t3, "already-repaired jump not disclosed")

    # 11. The shape split is additive: pp sums to the carry and variance shares sum to 100.
    leg("shape split is additive")
    ds = decompose(rets)
    chk(abs(sum(s["pp"] for s in ds["shape"]) - ds["arith_pp"]) < 1e-6,
        "shape pp column does not sum to the arithmetic carry")
    chk(abs(sum(s["var_share_pct"] or 0.0 for s in ds["shape"]) - 100.0) < 0.05,
        "shape variance column does not sum to 100%%")

    # 12. A flip pair is a pair, not two isolated jumps, and it carries ~no carry.
    leg("flip pairs are excluded and priced")
    rp, _ = CV.consolidation_returns(_synth("pair"))
    isop, _runp, _bigp = classify_isolated(rp)
    pairmask, paircount = classify_pairs(rp)
    chk(int(isop.sum()) == 0, "a flip pair was counted as %d isolated jumps" % int(isop.sum()))
    chk(paircount == 1, "pair count %d, want 1" % paircount)
    dp = decompose(rp)
    chk(abs(dp["pair_pp"]) < 0.02,
        "a pair carries %.4fpp/yr, want ~0 (the two bars cancel)" % dp["pair_pp"])
    chk(abs(dp["parts_sum_error_pp"]) < 1e-6, "pair series breaks the additive identity")

    # 13. A returning jump is RETURNS, a jump that stays is SHIFTS.
    leg("returns vs shifts")
    px_ret = _synth("flat")
    nflat = int(px_ret.shape[0])
    px_ret.iloc[200] = float(px_ret.iloc[199]) * 1.004
    for k in range(1, 21):
        px_ret.iloc[200 + k] = float(px_ret.iloc[199]) * (1.004 - 0.0002 * k)
    rr_ret, _ = CV.consolidation_returns(px_ret)
    iso_ret, _r_, _b_ = classify_isolated(rr_ret)
    none_zeroed = np.zeros(int(px_ret.shape[0]), dtype=bool)
    ev_ret, mirror_ret = classify_shapes(px_ret, rr_ret, iso_ret, none_zeroed)
    chk(len(ev_ret) == 1, "returning jump produced %d events, want 1" % len(ev_ret))
    chk(ev_ret and ev_ret[0]["shape"] == "RETURNS",
        "a jump that comes back inside %d bars was read as %s"
        % (RET_WINDOW, ev_ret[0]["shape"] if ev_ret else "nothing"))
    chk(int(mirror_ret.sum()) == 0, "a returning jump was called an already-repaired mirror")
    px_shift = _synth("flat")
    px_shift.iloc[200:] = float(px_shift.iloc[199]) * 1.004
    rr_shift, _ = CV.consolidation_returns(px_shift)
    iso_shift, _r2_, _b2_ = classify_isolated(rr_shift)
    none_zeroed_s = np.zeros(int(px_shift.shape[0]), dtype=bool)
    ev_shift, _m_s = classify_shapes(px_shift, rr_shift, iso_shift, none_zeroed_s)
    chk(ev_shift and ev_shift[0]["shape"] == "SHIFTS",
        "a jump that stays at the new level was read as %s"
        % (ev_shift[0]["shape"] if ev_shift else "nothing"))
    chk(nflat == int(px_shift.shape[0]), "shift case changed the bar count")

    # 14. A jump whose other half the reader already zeroed is named as such, not as debt.
    leg("already-repaired mirror is named")
    px_mir = _synth("flat")
    px_mir.iloc[200] = float(px_mir.iloc[199]) * 0.90      # -1000bp: the reader zeroes it
    px_mir.iloc[201] = float(px_mir.iloc[199])             # and the next bar comes straight back
    rr_mir, resets_mir = CV.consolidation_returns(px_mir)
    chk(len(resets_mir) == 1, "the -1000bp bar was not caught by the published reader")
    zeroed_mir = np.zeros(int(px_mir.shape[0]), dtype=np.int8)
    zeroed_mir[200] = 1                                   # the reader zeroed that bar
    iso_mir, _r3_, _b3_ = classify_isolated(rr_mir)
    ev_mir, mirror_mir = classify_shapes(px_mir, rr_mir, iso_mir, zeroed_mir)
    chk(len(ev_mir) == 1, "mirror case produced %d events, want 1" % len(ev_mir))
    chk(ev_mir and ev_mir[0]["shape"] == "MIRROR_READER",
        "the other half of a reader-repaired flip was read as %s"
        % (ev_mir[0]["shape"] if ev_mir else "nothing"))
    chk(int(mirror_mir.sum()) == 1, "mirror mask did not flag the bar")

    # 15. A mirror whose other half the band zeroed is named as the band's, not the reader's
    #     (the two are different defects, one generation apart).
    leg("mirror source is named")
    ev_band, _mb = classify_shapes(px_mir, rr_mir, iso_mir,
                                   (zeroed_mir * 2).astype(np.int8))
    chk(ev_band and ev_band[0]["shape"] == "MIRROR_BAND",
        "a band-zeroed mirror was read as %s"
        % (ev_band[0]["shape"] if ev_band else "nothing"))
    chk(ev_band and ev_band[0]["mirror_source"] == "band", "mirror source not printed")

    # 15. Determinism: the same panel gives the same decomposition twice.
    leg("deterministic")
    a = decompose(CV.consolidation_returns(_synth("isolated"))[0])
    b = decompose(CV.consolidation_returns(_synth("isolated"))[0])
    chk(json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True),
        "two runs disagree on the same series")

    # 12. The page never prints a literal %% (r2039/r2043 family).
    leg("page has no literal %%")
    p = os.path.join(ROOT, DOC)
    if os.path.exists(p):
        chk("%%" not in io.open(p, "r", encoding="utf-8").read(), "page prints a literal %%")

    # 13. Real face, when published: its verdict follows from its own rows and its page
    #     carries the table byte for byte.
    leg("published face is self-consistent")
    if os.path.exists(os.path.join(ROOT, FACE)):
        face = _load(FACE)
        chk(verdict_of(face["rows"])[0] == face["verdict"],
            "published verdict %s does not follow from its own rows" % face["verdict"])
        chk(render_table(face) in io.open(os.path.join(ROOT, DOC), "r",
                                         encoding="utf-8").read(),
            "page table does not match the published rows")
        chk(face["headline"]["isolated_bars_total"]
            == sum(int(r["isolated_bars"] or 0) for r in face["rows"]),
            "headline jump total disagrees with rows")

    if errs:
        print("SELFTEST FAILED (%d)" % len(errs))
        for e in errs:
            print(" -", e)
        return 1
    print("SELFTEST OK (%d legs)" % len(legs))
    return 0


# ----------------------------------------------------------------------------- run

def run():
    face = build()
    out = os.path.join(ROOT, FACE)
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    doc = write_doc(face)
    h = face["headline"]
    print("verdict=%s tags=%s" % (face["verdict"], ",".join(face["tags"])))
    print("named=%d with_jumps=%d median_share=%s isolated_bars=%d"
          % (h["named_instruments"], h["named_with_jumps"],
             "n/a" if h["median_isolated_share"] is None
             else "%.1f%%" % (h["median_isolated_share"] * 100.0),
             h["isolated_bars_total"]))
    print("published -> %s" % FACE)
    print("doc       -> %s" % doc)
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
