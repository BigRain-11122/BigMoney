#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""money_band_blind_spot -- what the 1% band cannot see.

WHY THIS FACE EXISTS
--------------------
r2050 (`money_premium_carry_audit`) booked every bar more than 1% away from its own
trailing 20-bar median at zero return and concluded `PREMIUM_IS_NOT_CARRY`: eleven money
ETFs printed 1.8-7.8pp/yr of premium, while the book's own legs stayed under 0.25pp.

That repair has a shape it cannot see.  A premium that leaves in one bar crosses 1% and
gets caught.  A premium that bleeds back over three weeks never leaves 1% on any single
bar, so every bar keeps its return and the annualised carry keeps the premium.  r2050
left exactly this debt in its own report: 511930 and 511920 still print 26-31bp of daily
sigma after the repair, and it said the residual shape -- slow回复 / one-way drift -- was
outside its ruler.

So the question is not "is there a premium" (r2050 answered that).  It is: **below the
band, does an elevated price still pay itself back?**  If it does, the published carry is
still partly a premium on the legs the band called clean.

THE QUESTION (frozen before the first run)
------------------------------------------
For every instrument r2050 named, and for the book's own legs as control:

1. On the bars that sit in the band's blind spot -- between 0.20% and 1.00% away from the
   instrument's own trailing 20-bar median -- is the forward 20-bar return lower than on
   the bars that sit near the level?
2. How much of the elevation is given back (share), and what is that worth per year?
3. Does the book's own leg keep its clean tag under a ruler five times tighter?

RULER (nothing re-decided here)
-------------------------------
* window, panel, reader -- r2050's own: `etf_book_cash_vehicle.load_etf` +
  `consolidation_returns`; the window is the census window, 2020-07-16 .. 2026-11-20.
* fast breaches       -- `money_premium_carry_audit.find_breaches` at its own 1% band,
  booked at zero by its own `repaired_rets`.  This face measures what is *left* after
  that repair, not a different repair.
* local level         -- `money_premium_carry_audit.local_level` (trailing 20-bar median,
  minimum 10 bars), exactly.
* **LOW_PCT = 0.20** (added here) -- 0.20% is ~25 sessions of a money fund's accrual; the
  zone (0.20%, 1.00%] is the band's blind spot.
* **HORIZON = 20** (added here) -- one local-level window; long enough for a bleed to
  show, short enough that the level has not been re-estimated under the reader.
* give-back           -- mean forward 20-bar return on blind-spot bars MINUS the same on
  near-level bars (|dev| <= 0.20%), in bp.  Positive means the elevated price pays back.
* annualisation       -- (1+giveback)^(252/HORIZON)-1, so a reader can compare it to the
  printed carry.  It assumes the elevation is on the book every day, which is the
  conservative reading and is printed as an assumption.
* gates               -- r2050's own published rows must reproduce (carry reduction within
  0.01pp, printed sigma within 0.1bp) or this face refuses to publish.

WHAT THIS RULER CANNOT SEPARATE (printed, not folded)
-----------------------------------------------------
An instrument that genuinely yields more than it did a month ago sits above its own
20-bar median for weeks and does not come back -- that is a level shift, not a premium.
The give-back test is exactly what separates them: a permanent step-up shows no give-back,
a premium shows give-back.  This is why the verdict is on the give-back and not on the
elevation itself.  The mirror zone (below the level) is printed as a symmetry check: under
reversion it should show catch-up of roughly the same size.

VERDICTS (mechanical, frozen on the median across the named set)
---------------------------------------------------------------
* THE_BAND_LEAVES_A_TAIL       -- median give-back >= 5.00bp per 20 bars (>= ~0.63pp/yr).
* A_TAIL_TOO_SMALL_TO_MATTER   -- 1.50 <= median < 5.00bp.
* NOTHING_BELOW_THE_BAND       -- median < 1.50bp.

TAGS (printed beside the verdict, never folded into it)
-------------------------------------------------------
* BOOK_LEGS_SURVIVE_THE_LOWER_BAND     -- every money/bond book leg gives back < 5.00bp:
                                          r2050's clean tag survives a 5x tighter band.
* BOOK_LEGS_NEED_THE_LOWER_BAND        -- at least one book leg gives back >= 5.00bp: the
                                          published shelf numbers do not stand under this
                                          ruler.
* THE_ELEVATION_IS_MOSTLY_PAID_BACK    -- median share given back >= 50% of the elevation.
* THE_ELEVATION_IS_MOSTLY_REAL         -- median share given back < 50%: the price is
                                          high and stays high.
* THE_RESIDUAL_SIGMA_IS_A_TAIL         -- the instruments r2050 flagged for residual sigma
                                          give back at least the named-set median.

Usage:
    python scripts/money_band_blind_spot.py run
    python scripts/money_band_blind_spot.py --check
    python scripts/money_band_blind_spot.py --write
    python scripts/money_band_blind_spot.py --selftest
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
import money_premium_carry_audit as MP  # noqa: E402  (r2050's band, level and repair)

CENSUS_FACE = "results/cash_shelf_flip_census.json"
SHELF_FACE = "results/cash_shelf_year_by_year.json"
PREMIUM_FACE = "results/money_premium_carry_audit.json"
FACE = "results/money_band_blind_spot.json"
DOC = "research/MONEY_BAND_BLIND_SPOT.md"

# Frozen before the first run.  See the docstring for why each number is what it is.
LOW_PCT = 0.20        # the blind spot's lower edge: ~25 sessions of accrual
BAND_PCT = MP.BAND_PCT  # r2050's own band, imported -- not re-decided here
HORIZON = 20          # forward bars = one local-level window
MATERIAL_BP = 5.00    # at or above this the tail is worth pricing (~0.63pp/yr)
MILD_BP = 1.50        # below this the tail is noise for a carry caliber
SHARE_PAID = 0.50     # half the elevation is paid back => it was not real
MIN_ZONE_BARS = 20    # fewer blind-spot bars than this and the zone is not measurable
MIN_BASE_BARS = 100   # fewer near-level bars than this and there is no baseline
MIN_MEASURABLE = 6    # fewer measurable instruments than this and the answer is a bound
T_POWER = 2.0         # a give-back has to clear this t-stat to be called a tail
GATE_PP_TOL = 0.01    # r2050's carry reduction must reproduce to this
GATE_SIGMA_TOL_BP = 0.1

MARK_BEGIN = "<!-- BLIND-SPOT-TABLE:BEGIN -->"
MARK_END = "<!-- BLIND-SPOT-TABLE:END -->"


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

def forward_returns(rets, horizon=HORIZON):
    """Forward `horizon`-bar compound return at every bar (NaN where the future is short).

    Built on the *repaired* series so a fast breach inside the window cannot leak into the
    number this face is trying to isolate.
    """
    clean = rets.fillna(0.0).astype(float)
    cum = (1.0 + clean).cumprod()
    return (cum.shift(-horizon) / cum) - 1.0


def zones(px, flag, horizon=HORIZON):
    """Split bars into blind-spot / near-level / mirror-zone, aligned to forward returns."""
    px = px.dropna().astype(float)
    lvl = MP.local_level(px)
    dev = (px / lvl - 1.0) * 100.0          # deviation in percent
    dev = dev.dropna()
    fwd_idx = px.index
    dev = dev.reindex(fwd_idx)
    f = pd.Series(flag.reindex(fwd_idx).fillna(False).astype(bool), index=fwd_idx)
    near = dev.abs() <= LOW_PCT
    elevated = (dev > LOW_PCT) & (dev <= BAND_PCT) & (~f)
    depressed = (dev < -LOW_PCT) & (dev >= -BAND_PCT) & (~f)
    return dev, near & (~f), elevated, depressed


def measure_one(code, start, end, name=None):
    """What one instrument's blind spot pays back, in bp per HORIZON bars."""
    px = CV.load_etf(code)
    px = px[(px.index >= pd.Timestamp(start)) & (px.index <= pd.Timestamp(end))]
    if px.dropna().shape[0] < 40:
        return {"code": code, "name": name, "priced": False,
                "why_unpriced": "fewer than 40 bars in the window"}

    rets, _resets = CV.consolidation_returns(px)
    _episodes, flag = MP.find_breaches(px)
    rr, n_repaired = MP.repaired_rets(rets, flag)
    fwd = forward_returns(rr)
    dev, near, elevated, depressed = zones(px, flag)

    ok = fwd.notna()
    n_elev = int((elevated & ok).sum())
    n_near = int((near & ok).sum())
    n_depr = int((depressed & ok).sum())
    if n_elev < MIN_ZONE_BARS or n_near < MIN_BASE_BARS:
        return {"code": code, "name": name, "priced": False,
                "why_unpriced": ("blind-spot zone has %d usable bars (need %d) and near-level "
                                 "has %d (need %d) -- not measurable, not zero"
                                 % (n_elev, MIN_ZONE_BARS, n_near, MIN_BASE_BARS)),
                "zone_bars": n_elev, "near_bars": n_near, "repaired_bars": int(n_repaired)}

    base_v = fwd[ok & near].values.astype(float)
    elev_v = fwd[ok & elevated].values.astype(float)
    base = float(base_v.mean())
    elev = float(elev_v.mean())
    giveback = (base - elev) * 1e4
    se = float(np.sqrt(base_v.var(ddof=1) / base_v.size + elev_v.var(ddof=1) / elev_v.size)) * 1e4
    elevation_bp = float(dev[elevated].mean()) * 100.0  # dev is percent; bp is 1/100 of that
    giveback_pp = None
    if giveback > -1.0:
        giveback_pp = round(((1.0 + giveback / 1e4) ** (252.0 / HORIZON) - 1.0) * 100.0, 4)
    depr = float(fwd[ok & depressed].mean()) if n_depr >= MIN_ZONE_BARS else None
    catch_up = None if depr is None else (depr - base) * 1e4

    return {
        "code": code, "name": name, "priced": True,
        "bars": int(px.dropna().shape[0]),
        "window_start": str(px.dropna().index[0].date()),
        "window_end": str(px.dropna().index[-1].date()),
        "repaired_bars": int(n_repaired),
        "zone_bars": n_elev,
        "near_bars": n_near,
        "mirror_bars": n_depr,
        "baseline_fwd_bp": round(base * 1e4, 3),
        "zone_fwd_bp": round(elev * 1e4, 3),
        "giveback_bp": round(giveback, 3),
        "giveback_se_bp": round(se, 3),
        "giveback_t": (round(giveback / se, 2) if se > 1e-9 else None),
        "elevation_bp": round(elevation_bp, 3),
        "share_paid_back": (round(giveback / elevation_bp, 4) if elevation_bp > 1e-9 else None),
        "giveback_pp_per_year": giveback_pp,
        "mirror_catch_up_bp": None if catch_up is None else round(catch_up, 3),
    }


def verdict_of(givebacks):
    """Mechanical verdict on the median give-back (bp per HORIZON bars) of the priced set."""
    vals = [v for v in givebacks if v is not None]
    if not vals:
        return "NOTHING_BELOW_THE_BAND", None
    med = float(np.median(vals))
    if med >= MATERIAL_BP:
        return "THE_BAND_LEAVES_A_TAIL", med
    if med >= MILD_BP:
        return "A_TAIL_TOO_SMALL_TO_MATTER", med
    return "NOTHING_BELOW_THE_BAND", med


def symmetry_of(catch_up, giveback):
    """1.0 = the zone and the mirror zone move by the same amount (noise); 0.0 = one-sided."""
    if catch_up is None or giveback is None:
        return None
    denom = abs(catch_up) + abs(giveback)
    if denom < 1e-9:
        return None
    return 1.0 - abs(giveback - catch_up) / denom


def tags_of(named, carry_legs, residual_codes):
    """Tags printed beside the verdict.  Book legs are money/bond only: a convertible's
    1% move is an ordinary session, so the band ruler is not a carry ruler there."""
    tags = []
    tail = [m.get("giveback_bp") for m in carry_legs if m.get("priced")]
    if tail and all(v is not None and v < MATERIAL_BP for v in tail):
        tags.append("BOOK_LEGS_SURVIVE_THE_LOWER_BAND")
    elif tail:
        tags.append("BOOK_LEGS_NEED_THE_LOWER_BAND")

    shares = [m.get("share_paid_back") for m in named if m.get("share_paid_back") is not None]
    if shares:
        med = float(np.median(shares))
        tags.append("THE_ELEVATION_IS_MOSTLY_PAID_BACK" if med >= SHARE_PAID
                    else "THE_ELEVATION_IS_MOSTLY_REAL")

    priced = [m for m in named if m.get("priced")]
    powered = [m for m in priced
               if m.get("giveback_t") is not None and abs(m["giveback_t"]) >= T_POWER
               and float(m["giveback_t"]) > 0.0]
    if priced and not powered:
        tags.append("NO_INSTRUMENT_IS_POWERED")
    if len(priced) < MIN_MEASURABLE:
        tags.append("TOO_FEW_INSTRUMENTS_TO_MEASURE")

    syms = [symmetry_of(m.get("mirror_catch_up_bp"), m.get("giveback_bp")) for m in priced]
    syms = [s for s in syms if s is not None]
    if syms:
        tags.append("THE_ZONE_IS_SYMMETRIC_NOISE" if float(np.median(syms)) >= 0.50
                    else "THE_ZONE_IS_ONE_SIDED")

    named_gb = [m["giveback_bp"] for m in powered]
    res = [m["giveback_bp"] for m in powered if m.get("code") in residual_codes]
    if named_gb and res and float(np.median(res)) >= float(np.median(named_gb)):
        tags.append("THE_RESIDUAL_SIGMA_IS_A_TAIL")
    return tags


# --------------------------------------------------------------------------- build

def build():
    census = _load(CENSUS_FACE)
    shelf = _load(SHELF_FACE)
    premium = _load(PREMIUM_FACE)
    start = str(census["window"]["start"])
    end = str(census["window"]["end"])

    published = {r["code"]: r for r in premium["rows"]}
    residual_codes = {r["code"] for r in premium["rows"]
                      if (r.get("sigma_repaired_bp") or 0.0) > 25.0}

    named = []
    for row in census["universe"]["money_sigma_over_25bp"]:
        m = measure_one(row["code"], start, end, name=row.get("name"))
        m["census_sigma_bp"] = row.get("sigma_bp")
        named.append(m)

    # r2050's own numbers must reproduce, or this face has no right to price its list.
    # Being unmeasurable by *this* ruler is a finding about the ruler, not a failed gate.
    gate = []
    for m in named:
        pub = published.get(m["code"])
        if not pub:
            gate.append({"code": m["code"], "ok": False, "why": "not in the r2050 face"})
            continue
        same = MP.measure_one(m["code"], start, end, name=m.get("name"))
        got_red = same.get("carry_reduction_pp")
        got_sig = same.get("sigma_printed_bp")
        ok = (got_red is not None and pub.get("carry_reduction_pp") is not None
              and abs(got_red - float(pub["carry_reduction_pp"])) <= GATE_PP_TOL
              and got_sig is not None and pub.get("sigma_printed_bp") is not None
              and abs(got_sig - float(pub["sigma_printed_bp"])) <= GATE_SIGMA_TOL_BP)
        gate.append({"code": m["code"], "ok": bool(ok),
                     "carry_reduction_pp": got_red,
                     "published_carry_reduction_pp": pub.get("carry_reduction_pp"),
                     "sigma_printed_bp": got_sig,
                     "published_sigma_printed_bp": pub.get("sigma_printed_bp")})
    if not all(g["ok"] for g in gate):
        bad = [g for g in gate if not g["ok"]]
        raise SystemExit("FATAL: r2050 reproduction gate failed on %s -- refuse to publish"
                         % ", ".join("%s(%s)" % (g["code"], g.get("why") or "numbers moved")
                                     for g in bad))

    legs = []
    census_names = {r["code"]: r.get("name") for r in census["rows"]}
    for r in shelf["rows"]:
        m = measure_one(r["code"], start, end, name=r.get("name") or census_names.get(r["code"]))
        m["book_class"] = r.get("class")
        m["carry_ruler_applies"] = r.get("class") in ("money", "bond")
        legs.append(m)
    carry_legs = [m for m in legs if m["carry_ruler_applies"]]

    verdict, med = verdict_of([m.get("giveback_bp") for m in named])
    tags = tags_of(named, carry_legs, residual_codes)

    rows = [{
        "code": m["code"], "name": m.get("name"), "priced": bool(m.get("priced")),
        "why_unpriced": m.get("why_unpriced"),
        "bars": m.get("bars"), "zone_bars": m.get("zone_bars"),
        "near_bars": m.get("near_bars"), "mirror_bars": m.get("mirror_bars"),
        "baseline_fwd_bp": m.get("baseline_fwd_bp"), "zone_fwd_bp": m.get("zone_fwd_bp"),
        "giveback_bp": m.get("giveback_bp"), "giveback_se_bp": m.get("giveback_se_bp"),
        "giveback_t": m.get("giveback_t"),
        "elevation_bp": m.get("elevation_bp"),
        "share_paid_back": m.get("share_paid_back"),
        "giveback_pp_per_year": m.get("giveback_pp_per_year"),
        "mirror_catch_up_bp": m.get("mirror_catch_up_bp"),
        "carry_reduction_pp_r2050": published.get(m["code"], {}).get("carry_reduction_pp"),
        "sigma_repaired_bp_r2050": published.get(m["code"], {}).get("sigma_repaired_bp"),
    } for m in named]

    priced_named = [m for m in named if m.get("priced")]
    worst = max(priced_named, key=lambda m: m.get("giveback_bp") or -1e9) if priced_named else None

    face = {
        "schema": "money_band_blind_spot/v1",
        "artifact": FACE,
        "generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": end,
        "window": {"start": start, "end": end},
        "question": ("Below r2050's 1% band -- on bars 0.20%..1.00% away from their own "
                     "trailing 20-bar median -- does an elevated price still pay itself back? "
                     "If it does, the printed carry is still partly a premium on legs the "
                     "band called clean."),
        "ruler": {
            "panel": "data/daily/*.csv (sina close)",
            "reader": "etf_book_cash_vehicle.load_etf + consolidation_returns",
            "fast_breaches": "money_premium_carry_audit.find_breaches at its own 1.00% band, "
                             "booked at zero by repaired_rets before measuring",
            "local_level": "money_premium_carry_audit.local_level (trailing 20-bar median, min 10)",
            "band_pct": BAND_PCT,
            "low_pct": LOW_PCT,
            "horizon": HORIZON,
            "giveback": "mean forward %d-bar return on blind-spot bars minus the same on "
                        "near-level bars (|dev| <= %.2f%%), in bp; positive = the elevation "
                        "pays back" % (HORIZON, LOW_PCT),
            "annualisation": "(1+giveback)^(252/%d)-1, assuming the elevation is held every "
                             "day -- printed as an assumption, not a forecast" % HORIZON,
            "no_entry_cost": True,
        },
        "upstream": {
            "census": {"path": CENSUS_FACE, "sha256": _sha(os.path.join(ROOT, CENSUS_FACE))},
            "shelf": {"path": SHELF_FACE, "sha256": _sha(os.path.join(ROOT, SHELF_FACE))},
            "premium": {"path": PREMIUM_FACE, "sha256": _sha(os.path.join(ROOT, PREMIUM_FACE))},
            "daily": [{"path": p, "sha256": _sha(os.path.join(ROOT, p))}
                      for p in sorted({_daily_path(m["code"]) for m in named + legs
                                       if _daily_path(m["code"])})],
        },
        "gate": {"r2050_reproduced": True, "pp_tol": GATE_PP_TOL,
                 "sigma_tol_bp": GATE_SIGMA_TOL_BP, "rows": gate},
        "verdict": verdict,
        "tags": tags,
        "paired_median_giveback_bp": None if med is None else round(med, 3),
        "worst": None if worst is None else {
            "code": worst["code"], "name": worst.get("name"),
            "giveback_bp": worst.get("giveback_bp"),
            "giveback_pp_per_year": worst.get("giveback_pp_per_year"),
            "elevation_bp": worst.get("elevation_bp"),
            "share_paid_back": worst.get("share_paid_back"),
        },
        "rows": rows,
        "book_legs": [{
            "code": m["code"], "name": m.get("name"), "class": m.get("book_class"),
            "carry_ruler_applies": bool(m.get("carry_ruler_applies")),
            "priced": bool(m.get("priced")),
            "why_unpriced": m.get("why_unpriced"),
            "zone_bars": m.get("zone_bars"),
            "giveback_bp": m.get("giveback_bp"),
            "giveback_se_bp": m.get("giveback_se_bp"),
            "giveback_t": m.get("giveback_t"),
            "elevation_bp": m.get("elevation_bp"),
            "share_paid_back": m.get("share_paid_back"),
            "giveback_pp_per_year": m.get("giveback_pp_per_year"),
        } for m in legs],
        "residual_sigma_codes": sorted(residual_codes),
        "caveat": ("an instrument that genuinely yields more than a month ago sits above its "
                   "own median and does not come back -- that is a level shift, not a premium. "
                   "The give-back test is what separates them; the elevation alone does not."),
        "assumptions": [
            "the annualised figure assumes the elevation is held on every day of the year",
            "no entry or exit cost is charged; this is a caliber question, not a trade",
            "the local level is a trailing 20-bar median, so a plateau longer than 20 bars "
            "re-bases the level under the reader -- slow bleeds longer than that are still unseen",
        ],
        "not_claimed": [
            "the published shelf numbers are not changed by this face",
            "r2050's verdict is not re-opened: this measures what its ruler leaves behind",
            "no tradeable return: the elevation is not harvestable without foresight",
        ],
        "headline": {
            "verdict": verdict,
            "named_instruments": len(named),
            "named_priced": len(priced_named),
            "named_unmeasurable": len(named) - len(priced_named),
            "powered": sum(1 for m in priced_named
                           if m.get("giveback_t") is not None
                           and abs(float(m["giveback_t"])) >= T_POWER),
            "median_giveback_bp": None if med is None else round(med, 3),
            "worst_code": (worst or {}).get("code"),
            "worst_giveback_bp": (worst or {}).get("giveback_bp"),
            "book_legs_survive": "BOOK_LEGS_SURVIVE_THE_LOWER_BAND" in tags,
            "book_legs_measured": sum(1 for m in carry_legs if m.get("priced")),
            "book_legs_unmeasurable": sum(1 for m in carry_legs if not m.get("priced")),
            "residual_sigma_codes": sorted(residual_codes),
        },
    }
    face["content_sha256"] = _content_sha({k: v for k, v in face.items() if k != "content_sha256"})
    return face


# --------------------------------------------------------------------- check + write

CHECK_FIELDS = ("verdict", "tags", "paired_median_giveback_bp", "worst", "rows",
                "book_legs", "headline", "gate")


def _f(v, nd=2, dash="-"):
    return dash if v is None else ("%.*f" % (nd, float(v)))


def render_table(face):
    lines = [MARK_BEGIN,
             "| code | name | blind-spot bars | near-level bars | baseline fwd (bp/20) | "
             "zone fwd (bp/20) | give-back (bp/20) | elevation (bp) | paid back | per year | "
             "r2050 carry cut (pp) |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in face["rows"]:
        if not r.get("priced"):
            lines.append("| %s | %s | %s | - | - | - | unpriced (needs %d zone bars) | - | - | - | %s |"
                         % (r["code"], r["name"] or "-",
                            "-" if r.get("zone_bars") is None else "%d" % r["zone_bars"],
                            MIN_ZONE_BARS, _f(r.get("carry_reduction_pp_r2050"))))
            continue
        lines.append("| %s | %s | %d | %d | %s | %s | %s | %s | %s | %s%%/yr | %s |" % (
            r["code"], r["name"] or "-", r["zone_bars"], r["near_bars"],
            _f(r["baseline_fwd_bp"], 1), _f(r["zone_fwd_bp"], 1), _f(r["giveback_bp"], 2),
            _f(r["elevation_bp"], 1),
            "-" if r["share_paid_back"] is None else "%.0f%%" % (r["share_paid_back"] * 100.0),
            _f(r["giveback_pp_per_year"]), _f(r["carry_reduction_pp_r2050"])))
    lines.append("")
    lines.append("Book legs (control) — `carry` says whether the band ruler applies to this leg:")
    lines.append("")
    lines.append("| code | class | carry | name | blind-spot bars | give-back (bp/20) | "
                 "elevation (bp) | paid back | per year |")
    lines.append("|---|---|---|---|---:|---:|---:|---:|---:|")
    for r in face["book_legs"]:
        if not r.get("priced"):
            lines.append("| %s | %s | %s | %s | %s | unpriced (needs %d zone bars) | - | - | - |" % (
                r["code"], r["class"], "yes" if r["carry_ruler_applies"] else "NO",
                r["name"] or "-",
                "-" if r.get("zone_bars") is None else "%d" % r["zone_bars"],
                MIN_ZONE_BARS))
            continue
        lines.append("| %s | %s | %s | %s | %d | %s | %s | %s | %s%%/yr |" % (
            r["code"], r["class"], "yes" if r["carry_ruler_applies"] else "NO",
            r["name"] or "-", r["zone_bars"], _f(r["giveback_bp"], 2),
            _f(r["elevation_bp"], 1),
            "-" if r["share_paid_back"] is None else "%.0f%%" % (r["share_paid_back"] * 100.0),
            _f(r["giveback_pp_per_year"])))
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


def check():
    """Re-derive the face and compare.  Upstream bytes moved => STALE (the chain pays to
    rebuild); a number that disagrees with the same inputs => CHECK FAILED, no STALE."""
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
        print("STALE (%d upstream byte(s) moved) -- run `run` to rebuild this face" % len(stale))
        return 3
    if hard:
        return 1
    print("CHECK OK (%d named / %d book legs / median give-back %s bp re-derived)"
          % (len(face["rows"]), len(face["book_legs"]),
             _f(face["paired_median_giveback_bp"], 2)))
    return 0


# ------------------------------------------------------------------------- selftest

def _synth(mode="clean", bars=620, seed=11, bumps=8, height=0.50, length=3):
    """A money fund at face 100 accruing ~0.008%/day, plus a deviation curve laid on the
    price directly (percent of price), so the shape is exact.

    The shape matters more than it looks: the ruler's own 20-bar median re-bases in about
    ten bars, so a *sustained* elevation is structurally invisible to it.  What the ruler
    can see is short deviations, which is why the synthetic injects short ones.

    mode='clean' : nothing but accrual
    mode='bumps' : short elevations `length` bars long, `height` percent high, spread out
    mode='dips'  : the same, mirrored below the level (the symmetry check)
    mode='step'  : one permanent level shift -- a higher yield, not a premium
    """
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2021-01-04", periods=bars)
    steps = 0.00008 + rng.normal(0.0, 0.00002, bars)
    path = np.cumprod(1.0 + steps) * 100.0
    d = np.zeros(bars)
    if mode in ("bumps", "dips", "mixed"):
        sign = {"bumps": 1.0, "dips": -1.0}.get(mode, 1.0)
        starts = np.linspace(150, bars - 40, bumps).astype(int)
        for k, s in enumerate(starts):
            sg = sign if mode != "mixed" else (1.0 if k % 2 == 0 else -1.0)
            d[int(s):int(s) + length] = sg * height
    elif mode == "step":
        d[200:] = height
    return pd.Series(path * (1.0 + d / 100.0), index=idx)


def _measure_series(px):
    rets, _ = CV.consolidation_returns(px)
    _ep, flag = MP.find_breaches(px)
    rr, n = MP.repaired_rets(rets, flag)
    fwd = forward_returns(rr)
    dev, near, elevated, depressed = zones(px, flag)
    ok = fwd.notna()
    n_e = int((elevated & ok).sum())
    n_n = int((near & ok).sum())
    n_d = int((depressed & ok).sum())
    if n_e < MIN_ZONE_BARS or n_n < MIN_BASE_BARS:
        return {"priced": False, "zone_bars": n_e, "near_bars": n_n, "repaired": n}
    base = float(fwd[ok & near].mean())
    elev = float(fwd[ok & elevated].mean())
    out = {"priced": True, "zone_bars": n_e, "near_bars": n_n, "repaired": n,
           "giveback_bp": (base - elev) * 1e4,
           "elevation_bp": float(dev[elevated].mean()) * 100.0}
    out["mirror_catch_up_bp"] = (float(fwd[ok & depressed].mean()) - base) * 1e4 \
        if n_d >= MIN_ZONE_BARS else None
    return out


def selftest():
    errs = []

    def chk(ok, msg):
        if not ok:
            errs.append(msg)

    # 1. A pure accrual has no blind-spot zone: nothing to measure is "unpriced", not zero.
    clean = _measure_series(_synth("clean"))
    chk(not clean.get("priced"),
        "a clean accrual produced a priced blind spot (%s bars)" % clean.get("zone_bars"))

    # 2. Short elevations (0.50%, 3 bars, eight of them) show a material give-back, and the
    #    share given back is the size of the deviation, not a rounding artefact.
    bumps = _measure_series(_synth("bumps"))
    chk(bumps.get("priced"), "the bump series has too few zone bars to measure")
    if bumps.get("priced"):
        chk(bumps["giveback_bp"] >= MATERIAL_BP,
            "bump give-back %.2fbp is below the %.2f material line"
            % (bumps["giveback_bp"], MATERIAL_BP))
        chk(bumps["elevation_bp"] > 20.0,
            "bump elevation %.1fbp is not ~50bp" % bumps["elevation_bp"])
        chk(0.3 <= bumps["giveback_bp"] / bumps["elevation_bp"] <= 1.5,
            "bump share paid back %.2f is not around the deviation"
            % (bumps["giveback_bp"] / bumps["elevation_bp"]))

    # 2b. The mirror zone catches up: the same ruler with the other sign.  0.30% keeps the
    #     dip above the published reader's -50bp consolidation line, so nothing is zeroed.
    mixed = _measure_series(_synth("mixed", height=0.40, bumps=16))
    chk(mixed.get("priced"), "the mixed series has too few zone bars to measure")
    if mixed.get("priced"):
        chk(mixed["giveback_bp"] > 0.0,
            "elevations in the mixed series gave nothing back (%.2f bp)" % mixed["giveback_bp"])
        chk(mixed.get("mirror_catch_up_bp") is not None and mixed["mirror_catch_up_bp"] > 0.0,
            "the mirror zone did not catch up (%.2f bp)" % (mixed.get("mirror_catch_up_bp") or 0.0))

    # 3. A *sustained* step-up is structurally invisible to this ruler: the 20-bar median
    #    re-bases under it.  Either it leaves too few zone bars to measure, or the
    #    give-back is far smaller than a real bleed.  Both are honest; a material
    #    give-back here would mean the ruler is inventing a premium.
    step = _measure_series(_synth("step"))
    chk((not step.get("priced"))
        or step["giveback_bp"] < bumps.get("giveback_bp", MATERIAL_BP) / 3.0,
        "step give-back %s is not clearly smaller than the bump's %.2fbp"
        % (step.get("giveback_bp"), bumps.get("giveback_bp") or 0.0))

    # 4. Verdict thresholds are mechanical.
    chk(verdict_of([9.0, 7.0, 6.0])[0] == "THE_BAND_LEAVES_A_TAIL", "verdict: material")
    chk(verdict_of([3.0, 2.5, 2.0])[0] == "A_TAIL_TOO_SMALL_TO_MATTER", "verdict: mild")
    chk(verdict_of([0.4, 0.2, 0.0])[0] == "NOTHING_BELOW_THE_BAND", "verdict: clean")
    chk(verdict_of([None, None])[0] == "NOTHING_BELOW_THE_BAND", "verdict: no data")
    chk(abs(verdict_of([9.0, 7.0, 6.0])[1] - 7.0) < 1e-9, "verdict median is not the median")

    # 5. Tag: clean carry legs survive; one dirty leg flips the tag.
    legs_ok = [{"priced": True, "giveback_bp": 0.4}, {"priced": True, "giveback_bp": 1.2}]
    named_ok = [{"priced": True, "giveback_bp": 6.0, "share_paid_back": 0.9,
                 "giveback_t": 3.0, "mirror_catch_up_bp": 5.0, "code": "511600"},
                {"priced": True, "giveback_bp": 8.0, "share_paid_back": 0.7,
                 "giveback_t": 3.5, "mirror_catch_up_bp": 7.0, "code": "511930"}]
    tg = tags_of(named_ok, legs_ok, {"511930"})
    chk("BOOK_LEGS_SURVIVE_THE_LOWER_BAND" in tg, "clean book legs not tagged as surviving")
    chk("THE_ELEVATION_IS_MOSTLY_PAID_BACK" in tg, "paid-back tag missing")
    chk("THE_RESIDUAL_SIGMA_IS_A_TAIL" in tg, "residual-sigma tag missing")
    legs_bad = [{"priced": True, "giveback_bp": 9.0}]
    chk("BOOK_LEGS_SURVIVE_THE_LOWER_BAND" not in tags_of(named_ok, legs_bad, set()),
        "surviving tag fired on a dirty book leg")
    named_real = [{"priced": True, "giveback_bp": 8.0, "share_paid_back": 0.2, "code": "511600"}]
    chk("THE_ELEVATION_IS_MOSTLY_REAL" in tags_of(named_real, legs_ok, set()),
        "mostly-real tag missing on a small share")

    # 6. Unpriced is not zero: the guard must return a reason, and the reason must say so.
    thin = _synth("clean", bars=120)
    m = _measure_series(thin)
    chk(not m.get("priced"), "a 120-bar series was priced")
    chk("zone_bars" in m, "unpriced result does not report its zone bar count")

    # 7. Determinism: the same synthetic gives the same number twice.
    a = _measure_series(_synth("wave"))
    b = _measure_series(_synth("wave"))
    chk(json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True),
        "blind-spot measurement is not deterministic")

    # 8. The forward window is built on the repaired series: a fast breach inside the
    #    window must not leak into the forward return.
    leaky = _synth("clean", bars=400)
    leaky.iloc[260] = float(leaky.iloc[259]) * 1.05   # a +5% fast breach inside the window
    leaky.iloc[261] = float(leaky.iloc[259]) * 1.0001
    rets, _ = CV.consolidation_returns(leaky)
    _ep, flag = MP.find_breaches(leaky)
    rr, n_rep = MP.repaired_rets(rets, flag)
    fwd_raw = forward_returns(rets)
    fwd_rep = forward_returns(rr)
    chk(n_rep >= 1, "the injected breach was not repaired")
    chk(float(fwd_raw.iloc[250]) > float(fwd_rep.iloc[250]) + 0.03,
        "the repair did not remove the injected breach from the forward return")
    chk(abs(float(fwd_rep.iloc[250]) - float(fwd_rep.iloc[251])) < 0.002,
        "the repaired forward return still jumps across the injected breach")

    # 9. Annualisation: 5bp per 20 bars is ~0.63pp/yr (252/20 compounding).
    ann = ((1.0 + 5.0 / 1e4) ** (252.0 / HORIZON) - 1.0) * 100.0
    chk(abs(ann - 0.63) < 0.05, "annualisation of 5bp/20 bars is %.3fpp, want ~0.63" % ann)

    # 10. The published face, when it exists: its verdict follows from its own rows.
    p = os.path.join(ROOT, FACE)
    if os.path.exists(p):
        face = _load(FACE)
        chk(verdict_of([r.get("giveback_bp") for r in face["rows"]])[0] == face["verdict"],
            "published verdict %s does not follow from its own rows" % face["verdict"])
        chk(face["headline"]["named_instruments"] == len(face["rows"]),
            "headline count disagrees with rows")
        chk(face["headline"]["named_priced"] == sum(1 for r in face["rows"] if r.get("priced")),
            "headline priced count disagrees with rows")
        chk(render_table(face).count("|") > 0, "table does not render")

    if errs:
        print("SELFTEST FAILED (%d)" % len(errs))
        for e in errs:
            print(" -", e)
        return 1
    print("SELFTEST OK (10 legs)")
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
    print("named=%d priced=%d median_giveback=%s bp/20 worst=%s %s bp (%s)"
          % (h["named_instruments"], h["named_priced"],
             _f(h["median_giveback_bp"], 2), h["worst_code"],
             _f(h["worst_giveback_bp"], 2), (face["worst"] or {}).get("name")))
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
