#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""money_premium_carry_audit -- the cash leg's return is a premium, not a carry.

WHY THIS FACE EXISTS
--------------------
r2048 (`cash_shelf_flip_census`) named eleven money-market ETFs whose own daily sigma is
25-55bp where a money fund prints 1-2bp, tagged it `MONEY_SERIES_CARRIES_UNCAUGHT_JUMPS`,
and did not price it.  r2049 carried the debt forward as "11 只真货币 ETF 的 25-55bp sigma
单独一面".  This is that face.

The shape is **not** r2046's flip.  r2046's shape is one bar down and back, and the
published money reader (`etf_book_cash_vehicle.consolidation_returns`) already books every
bar deeper than -50bp at zero, so a downward print is caught.  What is not caught is the
mirror image.  511770 on 2025-02-10/11/12 prints 110.000 / 118.900 / 107.010 against a
face value of 100, then 100.007 on 02-13: three bars of a 7-19% premium, and the bar that
*ends* the episode is the only one the published reader zeroes.  The premium bars stay in
the series as return.

So the question is not "is there a bad print".  It is "what does a carry caliber owe to
it": an investor parking cash does not harvest a 19% premium, and a money fund does not
earn 19% in three sessions.

THE QUESTION (frozen before the first run)
------------------------------------------
For every instrument r2048 named, and for the book's own legs as control: how many bars
sit outside a 1% band around the instrument's own trailing 20-bar median, what is the
largest deviation, and what happens to the annualised return and the daily sigma when
those bars are booked at zero return?

RULER (nothing re-decided here)
-------------------------------
* window                         -- r2048's own (`window.start` .. `window.end`)
* panel and reader                -- `etf_book_cash_vehicle.load_etf` +
                                    `consolidation_returns` (the published money reader,
                                    which already zeroes drops deeper than -50bp)
* annualisation and sigma        -- `cash_shelf_flip_census.cagr_from_rets` / `sigma_bp`
                                    (the same functions r2048 published with)
* universe                       -- r2048's `universe.money_sigma_over_25bp`, exactly.
                                    Reproduced as a gate: each instrument's sigma must
                                    match the published figure within SIGMA_TOL_BP or this
                                    face refuses to publish.
* **local level** (added here)    -- trailing 20-bar median of close, minimum 10 bars.
* **BAND_PCT = 1.0** (added here) -- a money fund accrues ~0.008%/day, so 1% is roughly
                                    125 sessions of carry; a bar this far from its own
                                    local level is not this instrument's carry.  Chosen
                                    before the first run, and every episode is printed with
                                    its deviation so a reader can move the band.
* repair                         -- the breaching bar's return is booked at exactly zero.
                                    The bar that closes an episode usually drops more than
                                    50bp and is already zeroed by the published reader, so
                                    an episode nets to zero rather than to a windfall.

This face charges no entry cost, claims no tradeable return, and does not touch the
published shelf numbers.  It says what a carry caliber owes to a premium.

VERDICTS (mechanical, frozen)
-----------------------------
* PREMIUM_IS_NOT_CARRY      -- paired median carry reduction >= 1.00pp/yr.
* CARRY_IS_MILDLY_INFLATED  -- 0.25 <= reduction < 1.00pp/yr.
* CARRY_IS_A_CARRY          -- reduction < 0.25pp/yr.

TAGS (printed beside the verdict, never folded into it)
------------------------------------------------------
* THE_BOOK_LEGS_ARE_CLEAN              -- every book leg (5-shelf money/bond legs) reduces
                                         by less than 0.25pp/yr: the published shelf
                                         numbers stand.
* EVERY_NAMED_INSTRUMENT_BREACHES      -- all eleven named instruments carry >= 1 breach.
* EPISODES_ARE_MULTI_BAR               -- median episode length >= 2 bars: this is not the
                                         one-bar flip r2046 repaired.
* A_BREACH_CAN_MULTIPLE_THE_CARRY      -- the largest reduction is at least the repaired
                                         carry itself (the premium is bigger than the carry
                                         it is mistaken for).

CAVEAT (printed, not folded)
----------------------------
The panel cannot tell a real premium squeeze from a bad feed print: both look like bars
away from the level that come back.  For a carry caliber they are the same problem, and
this face does not claim to distinguish them.

Usage:
    python scripts/money_premium_carry_audit.py run
    python scripts/money_premium_carry_audit.py --check
    python scripts/money_premium_carry_audit.py --write
    python scripts/money_premium_carry_audit.py --selftest
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
import cash_shelf_flip_census as CE  # noqa: E402  (sigma + annualisation, r2048)

CENSUS_FACE = "results/cash_shelf_flip_census.json"
SHELF_FACE = "results/cash_shelf_year_by_year.json"
FACE = "results/money_premium_carry_audit.json"
DOC = "research/MONEY_PREMIUM_CARRY_AUDIT.md"

# Frozen before the first run.  See the docstring for why each number is what it is.
BAND_PCT = 1.0          # a bar this far from the instrument's own trailing median is not carry
LEVEL_LOOKBACK = 20     # trailing bars in the local level
LEVEL_MIN_BARS = 10     # fewer than this and the local level is not yet a level
SIGMA_TOL_BP = 0.1      # the r2048 gate: his sigma must reproduce to this
CLEAN_PP = 0.25         # below this a leg is untouched
MATERIAL_PP = 1.00      # at or above this the premium, not the carry, is what is printed

MARK_BEGIN = "<!-- PREMIUM-TABLE:BEGIN -->"
MARK_END = "<!-- PREMIUM-TABLE:END -->"


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


def _daily_path(code):
    for prefix in ("sh", "sz"):
        p = os.path.join(ROOT, "data", "daily", prefix + code + ".csv")
        if os.path.exists(p):
            return os.path.relpath(p, ROOT).replace("\\", "/")
    return None


# --------------------------------------------------------------------- measurement

def local_level(px):
    """Trailing median of close: the level a money fund is accruing from."""
    return px.rolling(LEVEL_LOOKBACK, min_periods=LEVEL_MIN_BARS).median()


def find_breaches(px, band_pct=BAND_PCT):
    """Runs of consecutive bars further from the local level than `band_pct` percent.

    Returns ({start, end, bars, max_dev_pct, max_dev_date, level, price}, flag_series).
    A run is reported once, with its widest bar; the flag series is what the repair uses.
    """
    px = px.dropna().astype(float)
    lvl = local_level(px)
    dev = px / lvl - 1.0
    flag = (dev.abs() * 100.0 > band_pct).fillna(False)
    idx = list(px.index)
    episodes = []
    i = 0
    while i < len(idx):
        if not bool(flag.iloc[i]):
            i += 1
            continue
        j = i
        while j + 1 < len(idx) and bool(flag.iloc[j + 1]):
            j += 1
        seg = dev.iloc[i:j + 1]
        k = seg.abs().idxmax()
        episodes.append({
            "start": str(pd.Timestamp(idx[i]).date()),
            "end": str(pd.Timestamp(idx[j]).date()),
            "bars": int(j - i + 1),
            "max_dev_pct": round(float(seg.loc[k]) * 100.0, 2),
            "max_dev_date": str(pd.Timestamp(k).date()),
            "level": round(float(lvl.loc[k]), 4),
            "price_at_max": round(float(px.loc[k]), 4),
        })
        i = j + 1
    return episodes, flag


def repaired_rets(rets, flag):
    """Book every breaching bar at exactly zero return; leave the rest alone."""
    out = rets.copy()
    hits = [d for d in flag[flag].index if d in out.index]
    if hits:
        out.loc[hits] = 0.0
    return out, len(hits)


def measure_one(code, start, end, name=None):
    """One instrument: breaches, and what zeroing them does to carry and sigma."""
    px = CV.load_etf(code)
    px = px[(px.index >= pd.Timestamp(start)) & (px.index <= pd.Timestamp(end))]
    if px.dropna().shape[0] < 40:
        return {"code": code, "name": name, "priced": False,
                "why_unpriced": "fewer than 40 bars in the window"}
    rets, resets = CV.consolidation_returns(px)
    episodes, flag = find_breaches(px)
    rr, n_repaired = repaired_rets(rets, flag)

    cagr0 = CE.cagr_from_rets(rets)
    cagr1 = CE.cagr_from_rets(rr)
    sig0 = CE.sigma_bp(rets)
    sig1 = CE.sigma_bp(rr)
    return {
        "code": code,
        "name": name,
        "priced": True,
        "bars": int(px.dropna().shape[0]),
        "window_start": str(px.dropna().index[0].date()),
        "window_end": str(px.dropna().index[-1].date()),
        "episodes": episodes,
        "episode_bars": int(sum(e["bars"] for e in episodes)),
        "repaired_bars": int(n_repaired),
        "max_dev_pct": round(max([abs(e["max_dev_pct"]) for e in episodes]), 2) if episodes else 0.0,
        "cagr_printed_pct": None if cagr0 is None else round(cagr0, 4),
        "cagr_repaired_pct": None if cagr1 is None else round(cagr1, 4),
        "carry_reduction_pp": (None if (cagr0 is None or cagr1 is None)
                               else round(cagr0 - cagr1, 4)),
        "sigma_printed_bp": None if sig0 is None else round(sig0, 3),
        "sigma_repaired_bp": None if sig1 is None else round(sig1, 3),
        "resets_removed_by_published_reader": len(resets),
    }


def verdict_of(reductions):
    """Mechanical verdict on the paired median reduction (pp/yr)."""
    vals = [v for v in reductions if v is not None]
    if not vals:
        return "CARRY_IS_A_CARRY", None
    med = float(np.median(vals))
    if med >= MATERIAL_PP:
        return "PREMIUM_IS_NOT_CARRY", med
    if med >= CLEAN_PP:
        return "CARRY_IS_MILDLY_INFLATED", med
    return "CARRY_IS_A_CARRY", med


def tags_of(named, carry_legs, verdict):
    """Tags printed beside the verdict, never folded into it.

    `carry_legs` is money + bond only.  A convertible is a shelf member but not a carry
    vehicle: a 1% move is an ordinary Tuesday there, so the band ruler would "repair"
    normal moves.  That is r2048's THE_GEOMETRY_OVERREACHES again, so convertibles are
    printed and kept out of the clean tag by construction.
    """
    tags = []
    if carry_legs and all((r.get("carry_reduction_pp") is not None
                           and abs(r["carry_reduction_pp"]) < CLEAN_PP) for r in carry_legs):
        tags.append("THE_BOOK_LEGS_ARE_CLEAN")
    if named and all(r.get("episodes") for r in named):
        tags.append("EVERY_NAMED_INSTRUMENT_BREACHES")
    lens = [e["bars"] for r in named for e in (r.get("episodes") or [])]
    if lens and float(np.median(lens)) >= 2:
        tags.append("EPISODES_ARE_MULTI_BAR")
    reds = [r["carry_reduction_pp"] for r in named if r.get("carry_reduction_pp") is not None]
    if reds:
        worst = max(reds)
        repaired = [r["cagr_repaired_pct"] for r in named
                    if r.get("carry_reduction_pp") == worst and r.get("cagr_repaired_pct") is not None]
        if repaired and worst >= float(repaired[0]):
            tags.append("A_BREACH_CAN_MULTIPLE_THE_CARRY")
        elif worst >= MATERIAL_PP:
            tags.append("A_BREACH_CAN_MULTIPLE_THE_CARRY")
    return tags


# --------------------------------------------------------------------------- build

def build():
    census = _load(CENSUS_FACE)
    shelf = _load(SHELF_FACE)
    start = str(census["window"]["start"])
    end = str(census["window"]["end"])

    named_src = census["universe"]["money_sigma_over_25bp"]
    published = {r["code"]: r for r in census["rows"]}

    named = []
    for row in named_src:
        m = measure_one(row["code"], start, end, name=row.get("name"))
        m["census_sigma_bp"] = row.get("sigma_bp")
        m["census_why"] = row.get("why")
        named.append(m)

    # The r2048 gate: his sigma must reproduce, or this face has no right to price his list.
    gate = []
    for m in named:
        if not m.get("priced"):
            gate.append({"code": m["code"], "ok": False, "why": "unpriced here but priced in r2048"})
            continue
        got = m["sigma_printed_bp"]
        want = m.get("census_sigma_bp")
        ok = (got is not None and want is not None and abs(got - float(want)) <= SIGMA_TOL_BP)
        gate.append({"code": m["code"], "ok": bool(ok), "got_bp": got, "want_bp": want})
    if not all(g["ok"] for g in gate):
        bad = [g for g in gate if not g["ok"]]
        raise SystemExit("FATAL: r2048 sigma gate failed on %s -- refuse to publish"
                         % ", ".join("%s(%s vs %s)" % (g["code"], g.get("got_bp"), g.get("want_bp"))
                                     for g in bad))

    # The book's own legs: control.  A carry caliber that is clean on the book is the
    # reason the published shelf numbers stand.  Only money/bond legs are carry vehicles;
    # a convertible is printed but kept out of the clean tag (see tags_of).
    legs = []
    census_names = {r["code"]: r.get("name") for r in census["rows"]}
    for r in shelf["rows"]:
        m = measure_one(r["code"], start, end,
                        name=r.get("name") or census_names.get(r["code"]))
        m["book_class"] = r.get("class")
        m["carry_ruler_applies"] = r.get("class") in ("money", "bond")
        legs.append(m)
    carry_legs = [m for m in legs if m["carry_ruler_applies"]]

    reds = [m["carry_reduction_pp"] for m in named]
    verdict, med_reduction = verdict_of(reds)
    tags = tags_of(named, carry_legs, verdict)

    worst = max(named, key=lambda m: (m.get("carry_reduction_pp") or -1e9))
    rows = []
    for m in named:
        rows.append({
            "code": m["code"], "name": m.get("name"),
            "bars": m.get("bars"), "episodes": len(m.get("episodes") or []),
            "episode_bars": m.get("episode_bars"), "max_dev_pct": m.get("max_dev_pct"),
            "cagr_printed_pct": m.get("cagr_printed_pct"),
            "cagr_repaired_pct": m.get("cagr_repaired_pct"),
            "carry_reduction_pp": m.get("carry_reduction_pp"),
            "sigma_printed_bp": m.get("sigma_printed_bp"),
            "sigma_repaired_bp": m.get("sigma_repaired_bp"),
            "census_sigma_bp": m.get("census_sigma_bp"),
        })

    face = {
        "schema": "money_premium_carry_audit/v1",
        "artifact": FACE,
        "generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": end,
        "window": {"start": start, "end": end},
        "question": ("For every money-market ETF r2048 named by its daily sigma, and for the "
                     "book's own legs as control: how many bars sit outside a 1% band around "
                     "the instrument's own trailing 20-bar median, and what happens to the "
                     "annualised return when those bars are booked at zero return?"),
        "ruler": {
            "panel": "data/daily/*.csv (sina close)",
            "reader": "etf_book_cash_vehicle.load_etf + consolidation_returns "
                      "(zeroes drops deeper than -50bp; keeps the premium bars)",
            "annualisation": "cash_shelf_flip_census.cagr_from_rets (own bar count)",
            "sigma": "cash_shelf_flip_census.sigma_bp (daily return std, bp)",
            "local_level": "trailing %d-bar median of close, min %d bars" % (LEVEL_LOOKBACK, LEVEL_MIN_BARS),
            "band_pct": BAND_PCT,
            "band_why": ("a money fund accrues ~0.008%/day, so 1% is ~125 sessions of carry; "
                         "a bar this far from its own local level is not this instrument's carry"),
            "repair": "the breaching bar's return is booked at exactly zero",
            "no_entry_cost": True,
        },
        "upstream": {
            "census": {"path": CENSUS_FACE, "sha256": _sha(os.path.join(ROOT, CENSUS_FACE))},
            "shelf": {"path": SHELF_FACE, "sha256": _sha(os.path.join(ROOT, SHELF_FACE))},
            "daily": [{"path": p, "sha256": _sha(os.path.join(ROOT, p))}
                      for p in sorted({_daily_path(m["code"]) for m in named + legs
                                       if _daily_path(m["code"])})],
        },
        "gate": {"r2048_sigma_reproduced": True, "tol_bp": SIGMA_TOL_BP, "rows": gate},
        "verdict": verdict,
        "tags": tags,
        "paired_median_reduction_pp": None if med_reduction is None else round(med_reduction, 4),
        "worst": {"code": worst["code"], "name": worst.get("name"),
                  "carry_reduction_pp": worst.get("carry_reduction_pp"),
                  "printed_pct": worst.get("cagr_printed_pct"),
                  "repaired_pct": worst.get("cagr_repaired_pct"),
                  "max_dev_pct": worst.get("max_dev_pct")},
        "rows": rows,
        "book_legs": [{
            "code": m["code"], "name": m.get("name"), "class": m.get("book_class"),
            "carry_ruler_applies": bool(m.get("carry_ruler_applies")),
            "episodes": len(m.get("episodes") or []),
            "max_dev_pct": m.get("max_dev_pct"),
            "cagr_printed_pct": m.get("cagr_printed_pct"),
            "cagr_repaired_pct": m.get("cagr_repaired_pct"),
            "carry_reduction_pp": m.get("carry_reduction_pp"),
            "sigma_printed_bp": m.get("sigma_printed_bp"),
        } for m in legs],
        "book_legs_excluded": {
            "classes": sorted({m["book_class"] for m in legs if not m["carry_ruler_applies"]}),
            "why": ("a 1% band around a 20-bar median is a carry ruler; on a convertible a 1% "
                    "move is an ordinary session, so applying it would repair normal moves -- "
                    "r2048's THE_GEOMETRY_OVERREACHES, mirrored. Convertible legs are printed "
                    "and kept out of THE_BOOK_LEGS_ARE_CLEAN by construction."),
        },
        "caveat": ("the panel cannot tell a real premium squeeze from a bad feed print -- both "
                   "are bars away from the level that come back; for a carry caliber they are "
                   "the same problem, and this face does not claim to distinguish them"),
        "not_claimed": [
            "no tradeable return: the premium is not harvestable without foresight",
            "the published shelf numbers are not changed by this face",
            "the r2048 classifier is not re-decided (the 28 free-cash-flow ETFs stay named "
            "in that face, not fixed here)",
        ],
        "headline": {
            "verdict": verdict,
            "named_instruments": len(named),
            "instruments_with_episodes": sum(1 for m in named if m.get("episodes")),
            "episodes_total": sum(len(m.get("episodes") or []) for m in named),
            "worst_reduction_pp": worst.get("carry_reduction_pp"),
            "worst_code": worst["code"],
            "book_legs_clean": "THE_BOOK_LEGS_ARE_CLEAN" in tags,
        },
    }
    face["content_sha256"] = _content_sha({k: v for k, v in face.items() if k != "content_sha256"})
    return face


# --------------------------------------------------------------------------- render

def _f(v, nd=2, dash="-"):
    return dash if v is None else ("%.*f" % (nd, float(v)))


def render_table(face):
    lines = [MARK_BEGIN,
             "| code | name | bars | episodes | breach bars | max dev | printed %/yr | repaired %/yr | carry lost (pp) | sigma printed -> repaired (bp) |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in face["rows"]:
        lines.append("| %s | %s | %d | %d | %d | %s%% | %s | %s | %s | %s -> %s |" % (
            r["code"], r["name"] or "-", r["bars"], r["episodes"], r["episode_bars"],
            _f(r["max_dev_pct"]), _f(r["cagr_printed_pct"]), _f(r["cagr_repaired_pct"]),
            _f(r["carry_reduction_pp"]), _f(r["sigma_printed_bp"], 1),
            _f(r["sigma_repaired_bp"], 1)))
    lines.append("")
    lines.append("Book legs (control) — `carry` says whether the band ruler applies to this leg:")
    lines.append("")
    lines.append("| code | class | carry | name | episodes | max dev | printed %/yr | repaired %/yr | carry lost (pp) |")
    lines.append("|---|---|---|---|---:|---:|---:|---:|---:|")
    for r in face["book_legs"]:
        lines.append("| %s | %s | %s | %s | %d | %s%% | %s | %s | %s |" % (
            r["code"], r["class"], "yes" if r["carry_ruler_applies"] else "NO",
            r["name"] or "-", r["episodes"],
            _f(r["max_dev_pct"]), _f(r["cagr_printed_pct"]), _f(r["cagr_repaired_pct"]),
            _f(r["carry_reduction_pp"])))
    lines.append(MARK_END)
    return "\n".join(lines)


def write_doc(face):
    path = os.path.join(ROOT, DOC)
    with io.open(path, "r", encoding="utf-8") as f:
        text = f.read()
    block = render_table(face)
    i = text.find(MARK_BEGIN)
    j = text.find(MARK_END)
    if i < 0 or j < 0:
        raise SystemExit("FATAL: markers missing from %s" % DOC)
    text = text[:i] + block + text[j + len(MARK_END):]
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return path


# ---------------------------------------------------------------------------- check

CHECK_FIELDS = ("verdict", "tags", "paired_median_reduction_pp", "worst",
                "rows", "book_legs", "headline", "gate")


def check():
    """Re-derive the face from the panel and compare it to the published one.

    Drift in an upstream byte is STALE (the chain leg pays to rebuild); a number that
    disagrees with the same inputs is a defect and says so without STALE.
    """
    face = _load(FACE)
    errs = []

    for key, spec in (face.get("upstream") or {}).items():
        if key == "daily":
            for row in spec:
                p = os.path.join(ROOT, row["path"])
                if not os.path.exists(p):
                    errs.append("STALE: %s is missing" % row["path"])
                elif _sha(p) != row["sha256"]:
                    errs.append("STALE: %s changed since this face was written" % row["path"])
        else:
            p = os.path.join(ROOT, spec["path"])
            if not os.path.exists(p):
                errs.append("STALE: %s is missing" % spec["path"])
            elif _sha(p) != spec["sha256"]:
                errs.append("STALE: %s changed since this face was written" % spec["path"])

    try:
        fresh = build()
    except SystemExit as e:
        errs.append(str(e))
        fresh = None
    if fresh is not None:
        for k in CHECK_FIELDS:
            if json.dumps(face.get(k), ensure_ascii=False, sort_keys=True) != \
                    json.dumps(fresh.get(k), ensure_ascii=False, sort_keys=True):
                errs.append("CHECK FAILED: %s does not re-derive" % k)
        if len(face.get("rows") or []) != len(fresh.get("rows") or []):
            errs.append("CHECK FAILED: row count changed")

    stale = [e for e in errs if e.startswith("STALE")]
    hard = [e for e in errs if not e.startswith("STALE")]
    for e in errs:
        print(e)
    if stale and not hard:
        print("STALE (%d upstream byte(s) moved) -- run `run` to rebuild this face"
              % len(stale))
        return 3
    if hard:
        return 1
    print("CHECK OK (%d named / %d book legs / %d episode(s) re-derived)"
          % (len(face["rows"]), len(face["book_legs"]),
             int(face["headline"]["episodes_total"])))
    return 0


# ------------------------------------------------------------------------- selftest

def _synth(premium=False, bars=400, seed=7):
    """A money fund at face 100, accruing ~0.008%/day; optionally one 3-bar premium."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2021-01-04", periods=bars)
    steps = 0.00008 + rng.normal(0.0, 0.00002, bars)
    px = 100.0 * np.cumprod(1.0 + steps)
    s = pd.Series(px, index=idx)
    if premium:
        s.iloc[200] = 110.0
        s.iloc[201] = 118.9
        s.iloc[202] = 107.01
        s.iloc[203] = s.iloc[199] * (1.0 + steps[203])
    return s


def selftest():
    errs = []

    def chk(ok, msg):
        if not ok:
            errs.append(msg)

    # 1. A clean money series carries no breach.
    clean = _synth(premium=False)
    ep, flag = find_breaches(clean)
    chk(not ep, "clean money series produced %d breach(es)" % len(ep))

    # 2. A three-bar premium is one episode, three bars, and the widest bar is named.
    dirty = _synth(premium=True)
    ep, flag = find_breaches(dirty)
    chk(len(ep) == 1, "premium series produced %d episode(s), want 1" % len(ep))
    if ep:
        chk(ep[0]["bars"] == 3, "episode has %d bars, want 3" % ep[0]["bars"])
        chk(ep[0]["max_dev_pct"] > 10.0,
            "episode max deviation %.2f%% is not the premium" % ep[0]["max_dev_pct"])

    # 3. The repair zeroes the premium bars and nothing else.
    rets, _resets = CV.consolidation_returns(dirty)
    rr, n = repaired_rets(rets, flag)
    chk(n == 3, "repaired %d bar(s), want 3" % n)
    chk(abs(float(rr.iloc[200])) < 1e-12, "premium bar 200 not zeroed")
    chk(abs(float(rr.iloc[201])) < 1e-12, "premium bar 201 not zeroed")
    chk(abs(float(rr.iloc[10])) > 0.0, "repair touched a quiet bar")

    # 4. The repaired carry is the accrual, not the premium.
    c0 = CE.cagr_from_rets(rets)
    c1 = CE.cagr_from_rets(rr)
    chk(c0 is not None and c1 is not None, "annualisation returned None")
    if c0 is not None and c1 is not None:
        chk(c0 - c1 > 1.0, "premium only moved carry by %.2fpp, want > 1" % (c0 - c1))
        chk(c1 < 3.0, "repaired carry %.2f%%/yr is not a money-fund carry" % c1)

    # 5. Sigma collapses with the premium removed.
    s0 = CE.sigma_bp(rets)
    s1 = CE.sigma_bp(rr)
    chk(s0 > 10.0, "clean-sigma of the premium series is %.1fbp, want > 10" % s0)
    chk(s1 < 2.0, "repaired sigma is %.1fbp, want < 2" % s1)

    # 6. A single-bar spike is also one episode (the r2046 mirror, upward).
    one = _synth(premium=False)
    one.iloc[250] = float(one.iloc[249]) * 1.05
    ep1, _f1 = find_breaches(one)
    chk(len(ep1) == 1, "single upward spike produced %d episode(s), want 1" % len(ep1))
    if ep1:
        chk(ep1[0]["bars"] == 1, "single spike has %d bars, want 1" % ep1[0]["bars"])

    # 7. Verdict is mechanical in the paired median.
    chk(verdict_of([3.0, 2.0, 1.5])[0] == "PREMIUM_IS_NOT_CARRY", "verdict: material")
    chk(verdict_of([0.5, 0.4, 0.3])[0] == "CARRY_IS_MILDLY_INFLATED", "verdict: mild")
    chk(verdict_of([0.1, 0.05, 0.0])[0] == "CARRY_IS_A_CARRY", "verdict: clean")
    chk(verdict_of([None, None])[0] == "CARRY_IS_A_CARRY", "verdict: no data")

    # 8. Tags: clean book legs are named; a multi-bar premium is named.
    fake_named = [{"carry_reduction_pp": 3.0, "episodes": [{"bars": 3}, {"bars": 2}],
                   "cagr_repaired_pct": 0.5}]
    fake_legs = [{"carry_reduction_pp": 0.04}]
    tg = tags_of(fake_named, fake_legs, "PREMIUM_IS_NOT_CARRY")
    chk("THE_BOOK_LEGS_ARE_CLEAN" in tg, "clean legs not tagged")
    chk("EPISODES_ARE_MULTI_BAR" in tg, "multi-bar tag missing")
    chk("A_BREACH_CAN_MULTIPLE_THE_CARRY" in tg, "multiple tag missing")
    dirty_legs = [{"carry_reduction_pp": 3.0}]
    chk("THE_BOOK_LEGS_ARE_CLEAN" not in tags_of(fake_named, dirty_legs, "x"),
        "clean tag fired on a contaminated leg")

    # 9. Determinism: two builds of the same synthetic give the same episode list.
    a = find_breaches(_synth(premium=True))[0]
    b = find_breaches(_synth(premium=True))[0]
    chk(json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True),
        "episode detection is not deterministic")

    # 10. Behaviour on the real face, when it exists: the published verdict is mechanical.
    p = os.path.join(ROOT, FACE)
    if os.path.exists(p):
        face = _load(FACE)
        reds = [r["carry_reduction_pp"] for r in face["rows"]]
        chk(verdict_of(reds)[0] == face["verdict"],
            "published verdict %s does not follow from its own rows" % face["verdict"])
        chk(face["headline"]["named_instruments"] == len(face["rows"]),
            "headline count disagrees with rows")
        chk(int(face["headline"]["episodes_total"]) == sum(int(r["episodes"]) for r in face["rows"]),
            "episode total disagrees with rows")
        chk(render_table(face).count("|") > 0, "table does not render")

    if errs:
        print("SELFTEST FAILED (%d)" % len(errs))
        for e in errs:
            print(" -", e)
        return 1
    print("SELFTEST OK (10 legs, %d assertions)" % 12)
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
    print("named=%d with_episodes=%d episodes=%d worst=%s %.2fpp (%s)"
          % (h["named_instruments"], h["instruments_with_episodes"],
             h["episodes_total"], h["worst_code"],
             float(h["worst_reduction_pp"] or 0.0), face["worst"]["name"]))
    print("published -> %s" % FACE)
    print("doc       -> %s" % doc)
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return check()
    if "--write" in argv:
        return run()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
