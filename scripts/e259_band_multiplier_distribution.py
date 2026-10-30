#!/usr/bin/env python3
"""E259 -- the draw multiplier is a DISTRIBUTION, not a range over three seeds.

E258 measured each published window's own draw multiplier and published it as min..max over
THREE seeds. Three draws from a Monte-Carlo stream are not a distribution: the interval a reader
needs is the one the seeds themselves scatter into, and three numbers cannot say where its ends
are. That is the question this face asks:

    for the window that produced each published band, what is the DISTRIBUTION of the band's own
    draw multiplier across independent shuffle streams -- and does a published verdict change
    depending on where inside that distribution the reader stands?

Nothing new is estimated. The four pins are E258's, unchanged:

  1. THE WINDOW is the published cell's own first/last dates.
  2. THE STAR is the star that cell published, pinned (never re-named).
  3. THE BASE DRAW COUNT is the row's own published band draw count, read off the row.
  4. PREFIX NESTING: one draw stream per seed at max(d_grid), read back at every smaller count.

The one thing that changes is the sample: SEEDS independent streams instead of three. The first
three are E258's exact seeds (BASE_SEED + 101*k, k < 3), so E258's published three-seed range must
reappear bit-for-bit inside this sample. That is a reproducibility leg, not a claim: if the first
three streams do not reproduce E258, nothing else on the face is worth reading.

What is published per (window, base count, leg): the multiplier quantiles p5/p25/median/p75/p95,
the interval [p5, p95], the three-seed range beside it, and whether that range sits inside the
interval. Every published row is then re-judged three times -- at the TIGHT end of the interval,
at the median, and at the WIDE end -- so a verdict that only holds at one end of the seed
distribution is published as interval-dependent rather than as flipped.

NO BILL, NO ADOPTION, NO RE-PRICING, NO PANEL TRADE: this face measures the width of its own
measurement. It prices nothing and moves no coefficient.
"""

from __future__ import annotations

import argparse
import io
import json
import multiprocessing as mp
import os
import statistics
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e239_own_vs_cross as e239  # noqa: E402
import e250_book_turnover_echo as e250  # noqa: E402
import e252_star_prices_itself as e252  # noqa: E402
import e254_band_exponent_inside_cell as e254  # noqa: E402
import e255_band_draw_starvation as e255  # noqa: E402
import e257_band_at_top_flips as e257  # noqa: E402
import e258_band_multiplier_per_window as e258  # noqa: E402

ROOT = e252.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

STUDY = "E259_band_multiplier_distribution"
CUTOFF = "2026-10-29"
FACE = "BANDWINDIST-%s.json" % CUTOFF

FACE_STARSELF = e258.FACE_STARSELF
FACE_STAROWN = e258.FACE_STAROWN
FACE_E258 = "BANDWINMULT-%s.json" % CUTOFF

SEEDS = 40                       # independent streams; the first three must reproduce E258
E258_SEEDS = e258.SEEDS          # 3, inherited: the reproducibility pin
D_GRID = e258.D_GRID
TOP_DRAWS = e258.TOP_DRAWS
BASE_SEED = e258.BASE_SEED
BASE_COUNTS = (60, 200)          # both published base counts in the family
LEGS = ("self", "cross")
QUANTILES = (0.05, 0.25, 0.50, 0.75, 0.95)
WORKERS = 8

VERDICT_VOCAB = (
    "interval_is_wider_than_the_three_seed_range",
    "three_seed_range_covers_the_interval",
    "no_windows_measured",
)

NO_BILL = ("measurement only: the band is rebuilt inside each published window across 40 "
           "independent shuffle streams; no coefficient is re-priced, no member is billed, "
           "nothing is adopted")


# ------------------------------------------------------------------ io
def _p(name):
    return os.path.join(OUTDIR, name)


def load(name):
    with io.open(_p(name), encoding="utf-8") as fh:
        return json.load(fh)


def _try_load(name):
    try:
        return load(name)
    except FileNotFoundError:
        return None


# ------------------------------------------------------------------ quantiles (frozen rule)
def quantile(values, q, method="linear"):
    """Deterministic quantile; `linear` = the positions (n-1)*q, boundary-clamped.

    Frozen here and pinned by selftest: every p5/p95 on this face comes from this function, never
    from min/max, so a distribution with 40 draws and one with 3 are read on the same rule.
    """
    vals = sorted(float(v) for v in (values or []) if v is not None)
    n = len(vals)
    if n == 0:
        return None
    if n == 1:
        return vals[0]
    pos = (n - 1) * float(q)
    lo = int(pos)
    hi = min(lo + 1, n - 1)
    w = pos - lo
    return vals[lo] * (1.0 - w) + vals[hi] * w


def quantiles(values):
    return {"p%02d" % int(q * 100): quantile(values, q) for q in QUANTILES}


# ------------------------------------------------------------------ measurement (parallel)
_PREP = {}


def _lower_priority():
    try:
        import ctypes
        BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
        ctypes.windll.kernel32.SetPriorityClass(
            ctypes.windll.kernel32.GetCurrentProcess(), BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass


def _prep_window(per, cell, seeds):
    """Everything that does not depend on the seed: the window panel, the star, the aggregate."""
    rec = dict(cell)
    members = [m for m in (cell.get("members") or []) if per.get(m)]
    if not members:
        return {"cell": cell.get("label"), "error": "none of the cell's members are in the panel"}
    win = e254.e243.subset_per(per, members, cell["first"], cell["last"])
    dates, panel = e254.e240.common_increments(win, members)
    if len(dates) < e254.N_MIN:
        return {"cell": cell.get("label"),
                "error": "window has %d sessions (floor %d)" % (len(dates), e254.N_MIN)}
    star = cell.get("star")
    if not star or star not in panel["dy"]:
        return {"cell": cell.get("label"),
                "error": "the published star is absent from this window"}
    lvl_dates = sorted(set.intersection(*[set(win[s]) for s in members]))
    loo = e250.aggregate_moves(win, members, lvl_dates, exclude=star)
    if len(loo) != len(panel["dy"][members[0]]):
        return {"cell": cell.get("label"),
                "error": "LOO aggregate has %d rows, panel has %d"
                         % (len(loo), len(panel["dy"][members[0]]))}
    return {"cell": cell.get("label"), "members": members, "star": star,
            "first": dates[0], "last": dates[-1], "sessions": len(dates),
            "panel": panel, "loo": loo, "seeds": seeds, "error": None}


def _init_worker(per, cells, seeds):
    _lower_priority()
    for c in cells:
        _PREP[c["label"]] = _prep_window(per, c, seeds)


def _seed_task(task):
    """One (window, seed) pair: the draw stream plus its edge at every grid count."""
    label, k = task
    prep = _PREP.get(label) or {}
    if prep.get("error"):
        return {"cell": label, "seed_index": k, "error": prep["error"]}
    panel, members, star, loo = prep["panel"], prep["members"], prep["star"], prep["loo"]
    self_vals, cross_vals = e255.per_draw_pair(panel, members, star, loo,
                                               TOP_DRAWS, BASE_SEED + 101 * k)
    by_draws = {}
    for d in D_GRID:
        by_draws[str(d)] = {
            "self": e255.prefix_edge(self_vals, d),
            "cross": e255.prefix_edge(cross_vals, d),
        }
    return {"cell": label, "seed_index": k, "by_draws": by_draws, "error": None}


def measure(per, cells, seeds=SEEDS, workers=WORKERS):
    """{cell: window record} with a per-seed edge table, plus the windows that were skipped."""
    tasks, skipped, live = [], [], []
    for c in cells:
        if not c.get("star"):
            skipped.append({"cell": c.get("label"), "window": [c.get("first"), c.get("last")],
                            "reason": "the published cell names no star, so there is no sleeve "
                                      "whose null this band is"})
            continue
        live.append(c)
        tasks += [(c["label"], k) for k in range(int(seeds))]
    results = []
    if tasks:
        n = max(1, min(int(workers or 1), len(tasks)))
        if n == 1:
            _init_worker(per, live, seeds)
            results = [_seed_task(t) for t in tasks]
        else:
            with mp.Pool(processes=n, initializer=_init_worker,
                         initargs=(per, live, seeds)) as pool:
                results = pool.map(_seed_task, tasks, chunksize=1)
    windows, by_cell = {}, {}
    for r in results:
        if r.get("error"):
            skipped.append({"cell": r["cell"], "reason": r["error"]})
            continue
        by_cell.setdefault(r["cell"], []).append(r)
    for c in live:
        rows = sorted(by_cell.get(c["label"], []), key=lambda r: r["seed_index"])
        if not rows:
            continue
        prep = _PREP.get(c["label"]) or {}
        win = {"cell": c["label"], "sessions": prep.get("sessions"), "first": c.get("first"),
               "last": c.get("last"), "star": prep.get("star"),
               "members": prep.get("members"), "seeds": len(rows), "by_draws": {}}
        for d in D_GRID:
            key = str(d)
            rec = {"draws": d}
            for leg in LEGS:
                vals = [((r["by_draws"].get(key) or {}).get(leg)) for r in rows]
                rec["edge_%s_per_seed" % leg] = vals
                rec["edge_%s" % leg] = statistics.median([v for v in vals if v is not None]) \
                    if any(v is not None for v in vals) else None
            win["by_draws"][key] = rec
        windows[c["label"]] = win
    return windows, skipped


# ------------------------------------------------------------------ multiplier per seed
def seed_multipliers(win, base_draws, top=TOP_DRAWS, leg="self"):
    """One multiplier per seed: m_k = edge_k(top) / edge_k(base), both interpolated on the grid."""
    out = []
    for k in range(int(win.get("seeds") or 0)):
        series = []
        for d, cell in (win.get("by_draws") or {}).items():
            vals = (cell or {}).get("edge_%s_per_seed" % leg) or []
            if k < len(vals) and vals[k] is not None:
                series.append((int(d), float(vals[k])))
        series.sort()
        e_base = e257.edge_at(series, base_draws)
        e_top = e257.edge_at(series, top)
        if e_base and e_top is not None:
            out.append(e_top / e_base)
    return out


def distribution_record(win, base_draws, leg="self", top=TOP_DRAWS, e258_face=None):
    """The published interval for one (window, base count, leg)."""
    ms = seed_multipliers(win, base_draws, top=top, leg=leg)
    if not ms:
        return None
    q = quantiles(ms)
    interval = (q["p05"], q["p95"])
    first = ms[:E258_SEEDS]
    rec = {
        "cell": win.get("cell"), "base_draws": float(base_draws), "top_draws": top,
        "leg": leg, "n_seeds": len(ms),
        "multiplier_median": q["p50"],
        "multiplier_quantiles": q,
        "interval": list(interval),
        "interval_width": interval[1] - interval[0],
        "iqr": (q["p75"] - q["p25"]),
        "min": min(ms), "max": max(ms),
        "e258_seed_range": [min(first), max(first)],
        "e258_seed_range_width": max(first) - min(first),
        "e258_seed_range_inside_interval": bool(interval[0] <= min(first)
                                                and max(first) <= interval[1]),
        "interval_over_e258_range": ((interval[1] - interval[0])
                                     / (max(first) - min(first))
                                     if max(first) > min(first) else None),
        "seeds_above_interval_top": sum(1 for m in ms if m > interval[1]),
        # the prefix nest admits a degenerate reading: if the draw that sets the band's lower
        # endpoint already arrived inside the base prefix, the endpoint does not move again and the
        # multiplier is EXACTLY one. That is a measurement, not a failure -- but it drags p05 to
        # 1.0, so the count is published beside the interval instead of being averaged away.
        "n_endpoint_already_attained": sum(1 for m in ms if abs(m - 1.0) <= 1e-12),
        "seed_multipliers": ms,
    }
    # reproducibility pin: the same three seeds E258 published must reappear here.
    # E258's window record is keyed by base count ALONE (no leg field), and its by_base table is
    # built with multiplier_at's default leg -- so it carries the SELF arm only. Comparing a cross
    # arm against it would report a false mismatch (this face's first run did exactly that, 8/16),
    # so the pin is applied to the arm E258 actually published and the other arm says so.
    if e258_face:
        prev = (((e258_face.get("windows") or {}).get(win.get("cell")) or {})
                .get("by_base") or {}).get(str(int(base_draws))) or {}
        pinned = prev.get("multiplier_per_seed") or []
        if leg != "self":
            rec["e258_reproduced"] = None
            rec["e258_pin_note"] = ("E258 publishes one arm per base count (its default leg, "
                                    "self); this %s arm was never published, so it is not "
                                    "compared" % leg)
        elif pinned:
            rec["e258_reproduced"] = (len(pinned) == len(first)
                                      and all(abs(a - b) <= 1e-12
                                              for a, b in zip(pinned, first)))
            rec["e258_published_per_seed"] = list(pinned)
    return rec


def distributions(windows, e258_face=None, base_counts=BASE_COUNTS, legs=LEGS):
    out = {}
    for label, win in sorted((windows or {}).items()):
        table = {}
        for leg in legs:
            for b in base_counts:
                rec = distribution_record(win, b, leg=leg, e258_face=e258_face)
                if rec:
                    table["%s:%d" % (leg, b)] = rec
        if table:
            out[label] = table
    return out


def edge_tables(windows):
    """The raw per-seed edge table each interval was read off, so a reader can re-derive it."""
    out = {}
    for label, win in (windows or {}).items():
        table = {}
        for d, cell in (win.get("by_draws") or {}).items():
            table[d] = {leg: (cell or {}).get("edge_%s_per_seed" % leg) for leg in LEGS}
        out[label] = {"cell": label, "sessions": win.get("sessions"),
                      "first": win.get("first"), "last": win.get("last"),
                      "star": win.get("star"), "members": win.get("members"),
                      "seeds": win.get("seeds"), "by_draws": table}
    return out


def interval_spread(dists):
    """How wide does the interval get, window by window, and is it wider than 3 seeds say?"""
    rows = []
    for cell, table in sorted((dists or {}).items()):
        for key, rec in sorted((table or {}).items()):
            rows.append({"cell": cell, "arm": key,
                         "median": rec.get("multiplier_median"),
                         "interval": rec.get("interval"),
                         "width": rec.get("interval_width"),
                         "e258_width": rec.get("e258_seed_range_width"),
                         "ratio": rec.get("interval_over_e258_range")})
    widths = [r["width"] for r in rows if r["width"] is not None]
    ratios = [r["ratio"] for r in rows if r["ratio"] is not None]
    return {
        "n": len(rows),
        "width_min": min(widths) if widths else None,
        "width_max": max(widths) if widths else None,
        "width_median": statistics.median(widths) if widths else None,
        "ratio_min": min(ratios) if ratios else None,
        "ratio_max": max(ratios) if ratios else None,
        "ratio_median": statistics.median(ratios) if ratios else None,
        "n_wider_than_three_seeds": sum(1 for r in ratios if r > 1.0),
        "n_narrower_than_three_seeds": sum(1 for r in ratios if r <= 1.0),
        "rows": rows,
    }


# ------------------------------------------------------------------ row re-judgement
def rejudge_rows(rows, dists):
    """Judge each published row at the tight end, the median, and the wide end of its interval."""
    out = []
    for r in rows:
        rec = dict(r)
        table = (dists or {}).get(r.get("cell")) or {}
        b, lo, hi = r.get("b"), r.get("band_lo"), r.get("band_hi")
        base = int(float(r.get("band_draws") or 200))
        drec = table.get("self:%d" % base) or table.get("self:%d" % 200) or None
        if b is None or lo is None or hi is None:
            rec.update({"verdict_tight": "unjudgeable", "verdict_median": "unjudgeable",
                        "verdict_wide": "unjudgeable",
                        "interval_reason": "row carries no coefficient or no band"})
            out.append(rec)
            continue
        if not drec:
            rec.update({"verdict_tight": "unjudgeable", "verdict_median": "unjudgeable",
                        "verdict_wide": "unjudgeable",
                        "interval_reason": "no distribution at the row's own published draw "
                                           "count %d" % base})
            out.append(rec)
            continue
        m_lo, m_hi = drec["interval"]
        m_med = drec["multiplier_median"]
        pub = e257.outside(b, lo, hi)
        rec.update({
            "outside_at_published": pub,
            "interval": [m_lo, m_hi],
            "e258_seed_range": drec.get("e258_seed_range"),
            "multiplier_median_dist": m_med,
            "n_seeds": drec.get("n_seeds"),
        })
        if r.get("published_outside") is not None and pub != bool(r["published_outside"]):
            rec.update({"verdict_tight": "published_flag_not_reproduced",
                        "verdict_median": "published_flag_not_reproduced",
                        "verdict_wide": "published_flag_not_reproduced",
                        "interval_reason": "recomputed flag %r != published %r"
                                           % (pub, r["published_outside"])})
            out.append(rec)
            continue
        ends = {}
        for name, m in (("tight", m_lo), ("median", m_med), ("wide", m_hi)):
            outs = e257.outside(b, *e257.scale_band(lo, hi, m))
            ends[name] = {"multiplier": m, "outside": outs,
                          "margin": abs(b) / max(abs(lo * m), abs(hi * m))}
        rec.update({
            "verdict_tight": "outside" if ends["tight"]["outside"] else "inside",
            "verdict_median": "outside" if ends["median"]["outside"] else "inside",
            "verdict_wide": "outside" if ends["wide"]["outside"] else "inside",
            "margin_tight": ends["tight"]["margin"],
            "margin_median": ends["median"]["margin"],
            "margin_wide": ends["wide"]["margin"],
        })
        three = set([rec["verdict_tight"], rec["verdict_median"], rec["verdict_wide"]])
        rec["same_at_every_end"] = len(three) == 1
        rec["interval_dependent"] = len(three) > 1
        rec["survives_outside_at_every_end"] = three == {"outside"}
        rec["inside_at_every_end"] = three == {"inside"}
        rec["flips_from_published_at_any_end"] = (
            rec["verdict_wide"] != ("outside" if pub else "inside")
            or rec["verdict_tight"] != ("outside" if pub else "inside"))
        out.append(rec)
    return out


def verdict_from(rows, dists):
    if not dists:
        return "no_windows_measured", "no published window could be measured"
    spread = interval_spread(dists)
    dependent = [r for r in rows if r.get("interval_dependent")]
    wider = spread.get("n_wider_than_three_seeds") or 0
    if wider or dependent:
        return ("interval_is_wider_than_the_three_seed_range",
                "%d of %d interval(s) are wider than the three-seed range E258 published "
                "(ratio median %.2f); %d published row(s) change verdict inside their own "
                "interval" % (wider, spread.get("n"), spread.get("ratio_median") or 0,
                              len(dependent)))
    return ("three_seed_range_covers_the_interval",
            "every interval is no wider than the three-seed range (ratio max %.2f) and no row "
            "changes verdict inside its interval"
            % (spread.get("ratio_max") or 0))


# ------------------------------------------------------------------ run
def run(per=None, save=True, outdir=None, seeds=SEEDS, workers=WORKERS):
    outdir = outdir or OUTDIR
    starself = _try_load(FACE_STARSELF)
    starown = _try_load(FACE_STAROWN)
    e258face = _try_load(FACE_E258)
    missing = [n for n, f in (("starself", starself), ("starown", starown), ("e258", e258face))
               if f is None]
    if starself is None:
        face = {"study": STUDY,
                "title": "is the draw multiplier a distribution, not a three-seed range?",
                "evidence_cutoff": CUTOFF,
                "generated": datetime.now().isoformat(timespec="seconds"),
                "verdict": "no_windows_measured",
                "verdict_reason": "the published star face is absent, so there is no window to "
                                  "measure inside",
                "faces_missing": missing, "windows": {}, "rows": [],
                "frozen_spec": frozen_spec(seeds), "no_bill": NO_BILL}
        face["summary"] = _summary(face)
        if save:
            _write(face, outdir)
        return face

    per = per if per is not None else e239.panels()
    syms = [s for s in e252.BASKET if per.get(s)]
    cells = [dict(c, members=(c.get("members") or syms))
             for c in e258.cells_of(starself).values()]
    windows, skipped = measure(per, cells, seeds=seeds, workers=workers)
    dists = distributions(windows, e258face)

    rows = []
    rows += rejudge_rows(e257.starself_rows(starself), dists)
    if starown is not None:
        rows += rejudge_rows(e257.starown_rows(starown), dists)

    v, why = verdict_from(rows, dists)
    face = {
        "study": STUDY,
        "title": "is the draw multiplier a distribution, not a three-seed range?",
        "evidence_cutoff": (max([w.get("last") for w in windows.values() if w.get("last")]
                                or [CUTOFF])),
        "generated": datetime.now().isoformat(timespec="seconds"),
        "frozen_spec": frozen_spec(seeds),
        "source_faces": {"starself": "results/state_tilt/" + FACE_STARSELF,
                         "starown": "results/state_tilt/" + FACE_STAROWN,
                         "e258": "results/state_tilt/" + FACE_E258},
        "faces_missing": missing,
        "windows": dists,
        "windows_raw": edge_tables(windows),
        "windows_skipped": skipped,
        "windows_measured": sorted(dists.keys()),
        "interval_spread": interval_spread(dists),
        "reproducibility": _reproducibility(dists, e258face),
        "rows": rows,
        "verdict": v,
        "verdict_reason": why,
        "no_bill": NO_BILL,
    }
    face["summary"] = _summary(face)
    if save:
        _write(face, outdir)
    return face


def _reproducibility(dists, e258face):
    """Does this sample's first three seeds reproduce E258's published per-seed multipliers?"""
    checked, same, diffs, unpublished = 0, 0, [], 0
    for cell, table in (dists or {}).items():
        for key, rec in (table or {}).items():
            if rec.get("e258_reproduced") is None:
                unpublished += 1
                continue
            if not rec.get("e258_published_per_seed"):
                continue
            checked += 1
            if rec.get("e258_reproduced"):
                same += 1
            else:
                diffs.append({"cell": cell, "arm": key,
                              "published": rec.get("e258_published_per_seed"),
                              "here": rec.get("seed_multipliers", [])[:E258_SEEDS]})
    return {"checked": checked, "reproduced": same, "n_differs": len(diffs),
            "n_not_published_by_e258": unpublished,
            "differs": diffs[:4],
            "pin": "the first %d streams are E258's (BASE_SEED + 101*k, k < %d); E258 published "
                   "one arm per base count, so only that arm (self) is pinned"
                   % (E258_SEEDS, E258_SEEDS),
            "e258_face_present": e258face is not None}


def frozen_spec(seeds=SEEDS):
    return {
        "design": "rebuild the paired shuffled band INSIDE each published window across SEEDS "
                  "independent streams and publish the multiplier's own distribution",
        "window": "the published cell's own first/last dates (the sessions the band was built on)",
        "star": "the star that cell published, pinned (never re-named)",
        "base_draws": "the row's own published band draw count, read off the row",
        "top_draws": TOP_DRAWS,
        "draw_grid": list(D_GRID),
        "prefix_nesting": "one stream per seed at max(draw_grid), read back at every smaller count",
        "seeds": int(seeds),
        "reproducibility_pin": "streams 0..%d are E258's exact seeds" % (E258_SEEDS - 1),
        "base_seed": BASE_SEED,
        "quantile_rule": "linear positions (n-1)*q, boundary-clamped",
        "interval": "[p05, p95] of the per-seed multipliers; never min..max",
        "rejudge_rule": "each published row is judged at the interval's tight end, at the median, "
                        "and at its wide end; a row that changes verdict between ends is "
                        "interval-dependent, not flipped",
        "no_bill": NO_BILL,
    }


def _summary(face):
    rows = face.get("rows") or []
    spread = face.get("interval_spread") or {}
    reps = face.get("reproducibility") or {}
    by = {}
    for r in rows:
        key = r.get("verdict_median") or "unjudgeable"
        by[key] = by.get(key, 0) + 1
    return {
        "windows_measured": len(face.get("windows") or {}),
        "windows_skipped": len(face.get("windows_skipped") or []),
        "seeds": (face.get("frozen_spec") or {}).get("seeds"),
        "intervals": spread.get("n"),
        "interval_width_min": spread.get("width_min"),
        "interval_width_max": spread.get("width_max"),
        "interval_width_median": spread.get("width_median"),
        "ratio_vs_three_seed_min": spread.get("ratio_min"),
        "ratio_vs_three_seed_max": spread.get("ratio_max"),
        "ratio_vs_three_seed_median": spread.get("ratio_median"),
        "intervals_wider_than_three_seeds": spread.get("n_wider_than_three_seeds"),
        "rows": len(rows),
        "rows_by_median_verdict": by,
        "rows_interval_dependent": sum(1 for r in rows if r.get("interval_dependent")),
        "rows_survive_outside_at_every_end": sum(
            1 for r in rows if r.get("survives_outside_at_every_end")),
        "rows_unjudgeable": sum(1 for r in rows
                                if r.get("verdict_median") == "unjudgeable"),
        "e258_reproduced": "%s/%s" % (reps.get("reproduced"), reps.get("checked")),
        "e258_arms_not_published": reps.get("n_not_published_by_e258"),
        "intervals_with_endpoint_already_attained": sum(
            1 for table in (face.get("windows") or {}).values() for rec in (table or {}).values()
            if (rec.get("n_endpoint_already_attained") or 0) > 0),
        "seeds_endpoint_already_attained": sum(
            (rec.get("n_endpoint_already_attained") or 0)
            for table in (face.get("windows") or {}).values() for rec in (table or {}).values()),
    }


# ------------------------------------------------------------------ write / verify
def _write(face, outdir, tag=""):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "BANDWINDIST-%s%s.json" % (face.get("evidence_cutoff"), tag))
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    latest = os.path.join(outdir, "bandwindist_latest.json")
    with io.open(latest, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    return path


def verify(outdir=None, tag=""):
    """Re-derive every published quantile, interval, and row verdict from the raw seed streams."""
    outdir = outdir or OUTDIR
    path = os.path.join(outdir, "BANDWINDIST-%s%s.json" % (CUTOFF, tag))
    problems = []
    with io.open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    n_int = 0
    raw = face.get("windows_raw") or {}
    for cell, table in (face.get("windows") or {}).items():
        win = raw.get(cell) or {}
        if not win:
            problems.append("%s: no raw edge table published" % cell)
        elif int(win.get("seeds") or 0) != len(
                [1 for _ in ((list((win.get("by_draws") or {}).values())[0] or {})
                              .get("self") or [])]):
            problems.append("%s: raw table seed count is not the window's seed count" % cell)
        for key, rec in (table or {}).items():
            ms = rec.get("seed_multipliers") or []
            q = quantiles(ms)
            for name, val in q.items():
                if rec.get("multiplier_quantiles", {}).get(name) is None or \
                        abs(val - rec["multiplier_quantiles"][name]) > 1e-12:
                    problems.append("%s/%s: %s does not re-derive" % (cell, key, name))
            if abs(q["p05"] - rec["interval"][0]) > 1e-12 or \
                    abs(q["p95"] - rec["interval"][1]) > 1e-12:
                problems.append("%s/%s: interval is not [p05, p95]" % (cell, key))
            if len(ms) != rec.get("n_seeds"):
                problems.append("%s/%s: n_seeds is not the stream length" % (cell, key))
            n_int += 1
    for r in (face.get("rows") or []):
        if r.get("verdict_median") in (None, "unjudgeable",
                                       "published_flag_not_reproduced"):
            continue
        b, lo, hi = r.get("b"), r.get("band_lo"), r.get("band_hi")
        scale = None
        cell, base = r.get("cell"), int(float(r.get("band_draws") or 200))
        rec = ((face.get("windows") or {}).get(cell) or {}).get("self:%d" % base) or {}
        if rec.get("multiplier_median") is not None:
            scale = rec["multiplier_median"]
        if scale is None:
            problems.append("row %s/%s says it was judged but has no distribution"
                            % (cell, r.get("row")))
            continue
        want = "outside" if e257.outside(b, *e257.scale_band(lo, hi, scale)) else "inside"
        if want != r.get("verdict_median"):
            problems.append("row %s/%s: median verdict %r != %r"
                            % (cell, r.get("row"), r.get("verdict_median"), want))
    return {"ok": not problems, "intervals": n_int, "problems": problems}


# ------------------------------------------------------------------ selftest
def _legs(ok, name, detail=None):
    return (bool(ok), name, detail)


def _fake_window(edges_by_seed, grid=D_GRID):
    """A window record fabricated from per-seed edge series: {seed: {draw: edge}}."""
    win = {"cell": "fixture", "seeds": len(edges_by_seed), "by_draws": {}}
    for d in grid:
        key = str(d)
        selfs = [edges_by_seed[k].get(d) for k in sorted(edges_by_seed)]
        win["by_draws"][key] = {"draws": d, "edge_self_per_seed": selfs,
                                "edge_cross_per_seed": list(selfs)}
    return win


def selftest():
    legs = []

    # --- quantile rule
    vals = [1.0, 2.0, 3.0, 4.0, 5.0]
    legs.append(_legs(abs(quantile(vals, 0.5) - 3.0) < 1e-12,
                      "the median of five is the middle value", quantile(vals, 0.5)))
    legs.append(_legs(abs(quantile(vals, 0.05) - 1.2) < 1e-12,
                      "p05 interpolates inside the sample, it does not snap to the min",
                      quantile(vals, 0.05)))
    legs.append(_legs(quantile([], 0.5) is None and quantile([7.0], 0.9) == 7.0,
                      "a one-point sample has a quantile and an empty one does not"))
    legs.append(_legs(abs(quantile([1.0, 5.0], 0.95) - 4.8) < 1e-12,
                      "p95 of two points is inside the pair, not the max", quantile([1.0, 5.0], 0.95)))

    # --- multiplier per seed: m = edge(top)/edge(base) on a rising ladder
    def series(scale, grid=D_GRID):
        return {d: scale * (d ** 0.5) for d in grid}
    want_m = (float(TOP_DRAWS) / 60.0) ** 0.5     # a sqrt ladder has a sqrt multiplier
    win = _fake_window({0: series(1.0), 1: series(1.1), 2: series(1.2)})
    ms = seed_multipliers(win, 60)
    legs.append(_legs(len(ms) == 3 and all(abs(m - want_m) < 1e-6 for m in ms),
                      "each seed gets its own multiplier (sqrt ladder -> sqrt(top/base))", ms))
    flat = _fake_window({0: series(1.0)})
    legs.append(_legs(abs(seed_multipliers(flat, 60)[0] - want_m) < 1e-6,
                      "a single-seed window still yields a multiplier"))

    # --- distribution record
    spread_seeds = {k: series(1.0 + 0.12 * k) for k in range(6)}
    rec = distribution_record(_fake_window(spread_seeds), 60)
    legs.append(_legs(rec["interval"][0] < rec["interval"][1],
                      "a scattered sample produces a positive-width interval",
                      rec["interval"]))
    legs.append(_legs(abs(rec["interval"][1] - rec["interval"][0]) > 0.0,
                      "the interval is [p05, p95], not a point"))
    legs.append(_legs(rec["multiplier_quantiles"]["p05"] <= rec["multiplier_quantiles"]["p50"]
                      <= rec["multiplier_quantiles"]["p95"],
                      "the quantiles are ordered"))
    legs.append(_legs(rec["e258_seed_range"] == [min(rec["seed_multipliers"][:3]),
                                                 max(rec["seed_multipliers"][:3])],
                      "the three-seed range is the first three streams, nothing else"))
    # a seed whose band endpoint never moves again after the base prefix reads exactly 1.0
    degenerate = {0: {d: 1.0 for d in D_GRID}, 1: {d: 1.0 for d in D_GRID}}
    for k in range(2, 20):
        degenerate[k] = series(1.0 + 0.05 * k)
    rec_deg = distribution_record(_fake_window(degenerate), 60)
    legs.append(_legs(rec_deg["n_endpoint_already_attained"] == 2,
                      "a seed whose endpoint never moves is counted, not dropped",
                      rec_deg["n_endpoint_already_attained"]))
    legs.append(_legs(rec_deg["interval"][0] == 1.0 and rec_deg["interval"][1] > 1.0,
                      "...and it is those seeds that put the interval's lower end at one",
                      rec_deg["interval"]))
    # same-window, same-seed reproduction of an E258-style face
    e258fake = {"windows": {"fixture": {"by_base": {"60": {
        "multiplier_per_seed": rec["seed_multipliers"][:3]}}}}}
    rec2 = distribution_record(_fake_window(spread_seeds), 60, e258_face=e258fake)
    legs.append(_legs(rec2.get("e258_reproduced") is True,
                      "the first three streams reproduce an E258 per-seed table bit-for-bit"))
    e258bad = {"windows": {"fixture": {"by_base": {"60": {
        "multiplier_per_seed": [9.9, 9.9, 9.9]}}}}}
    rec3 = distribution_record(_fake_window(spread_seeds), 60, e258_face=e258bad)
    legs.append(_legs(rec3.get("e258_reproduced") is False,
                      "a published table that does not reproduce is named, not absorbed"))
    rec4 = distribution_record(_fake_window(spread_seeds), 60, leg="cross", e258_face=e258fake)
    legs.append(_legs(rec4.get("e258_reproduced") is None and rec4.get("e258_pin_note"),
                      "an arm E258 never published is not compared against its self-only table",
                      rec4.get("e258_reproduced")))

    # --- row re-judgement at three ends
    def _dist(m_lo, m_med, m_hi):
        """A distribution record with the three multipliers rejudge_rows reads, nothing else."""
        return {"cell": "fixture", "base_draws": 60.0, "leg": "self", "n_seeds": 40,
                "multiplier_median": m_med, "interval": [m_lo, m_hi],
                "e258_seed_range": [m_lo, m_med]}

    tight_dep = {"cell": "fixture", "row": "self", "b": -0.40, "band_lo": -0.30, "band_hi": 0.20,
                 "band_draws": 60, "published_outside": True, "source": "fixture"}
    dists = {"fixture": {"self:60": _dist(1.0, 1.5, 3.0)}}
    r0 = rejudge_rows([tight_dep], dists)[0]
    legs.append(_legs(r0["verdict_tight"] == "outside",
                      "a value outside the tight end is outside there", r0["verdict_tight"]))
    legs.append(_legs(r0["verdict_wide"] == "inside",
                      "...and the same value is inside the wide end", r0["verdict_wide"]))
    legs.append(_legs(r0["interval_dependent"] is True and r0["same_at_every_end"] is False,
                      "a marginal row turns interval-dependent, not silently flipped",
                      (r0["verdict_tight"], r0["verdict_median"], r0["verdict_wide"])))
    legs.append(_legs(r0["margin_tight"] > r0["margin_wide"],
                      "the margin falls as the band widens (tight margin beats wide margin)",
                      (r0["margin_tight"], r0["margin_wide"])))
    far = rejudge_rows([dict(tight_dep, b=-9.0)], dists)[0]
    legs.append(_legs(far["survives_outside_at_every_end"] is True,
                      "a far-outside value survives every end of the interval"))
    inside_far = rejudge_rows([dict(tight_dep, b=-0.05, published_outside=False)], dists)[0]
    legs.append(_legs(inside_far["inside_at_every_end"] is True,
                      "a value inside the published band stays inside when it widens"))
    legs.append(_legs(rejudge_rows([dict(tight_dep, b=None)], dists)[0]["verdict_median"]
                      == "unjudgeable",
                      "a row without a coefficient is unjudgeable, not inside"))
    norow = rejudge_rows([dict(tight_dep, cell="elsewhere")], dists)[0]
    legs.append(_legs(norow["verdict_median"] == "unjudgeable",
                      "a row whose window was not measured is unjudgeable, not re-judged"))

    # --- verdict total on an empty face
    v, _ = verdict_from([], {})
    legs.append(_legs(v == "no_windows_measured",
                      "an empty measurement list returns the empty verdict, not a clean one", v))
    legs.append(_legs(verdict_from([r0], {})[0] == "no_windows_measured",
                      "rows without distributions cannot make a verdict"))

    # --- the module cannot have built the band itself
    src = io.open(os.path.abspath(__file__), encoding="utf-8").read()
    imports = [ln.strip() for ln in src.splitlines()
               if ln.strip().startswith(("import ", "from "))]
    legs.append(_legs(not any(("pandas" in s or "urllib" in s or "requests" in s)
                              for s in imports),
                      "the face imports no market-data library", imports[:3]))

    # --- ACTIVITY legs read the on-disk face when it exists
    face = _try_load(FACE)
    if face:
        s = face.get("summary") or {}
        legs.append(_legs((s.get("windows_measured") or 0) >= 3,
                          "ACTIVITY: at least three published windows were measured",
                          s.get("windows_measured")))
        legs.append(_legs((s.get("seeds") or 0) >= 20,
                          "ACTIVITY: the distribution has at least twenty streams",
                          s.get("seeds")))
        legs.append(_legs((s.get("interval_width_max") or 0) > 0,
                          "ACTIVITY: some interval has positive width",
                          s.get("interval_width_max")))
        legs.append(_legs((face.get("reproducibility") or {}).get("n_differs") == 0,
                          "every E258 per-seed table that could be checked reproduced",
                          (face.get("reproducibility") or {}).get("n_differs")))

    passed = sum(1 for ok, _, _ in legs if ok)
    for ok, name, detail in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name,
                           "" if detail is None else "  [%s]" % (detail,)))
    print("\n%d/%d legs" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


# ------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "selftest", "verify", "show"])
    ap.add_argument("--seeds", type=int, default=SEEDS)
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--tag", default="")
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "verify":
        r = verify(tag=args.tag)
        for p in r["problems"][:10]:
            print("PROBLEM", p)
        print("verify OK (%d intervals)" % r["intervals"] if r["ok"]
              else "verify FAILED (%d problems)" % len(r["problems"]))
        return 0 if r["ok"] else 1
    if args.cmd == "show":
        face = _try_load(FACE)
        if not face:
            print("no face at", FACE)
            return 1
        print(json.dumps(face.get("summary"), ensure_ascii=False, indent=1))
        return 0
    face = run(save=True, seeds=args.seeds, workers=args.workers)
    print(json.dumps(face.get("summary"), ensure_ascii=False, indent=1))
    print("verdict:", face.get("verdict"), "--", face.get("verdict_reason"))
    return 0


if __name__ == "__main__":
    sys.exit(main())