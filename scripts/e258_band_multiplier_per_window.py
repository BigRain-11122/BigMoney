#!/usr/bin/env python3
"""E258 -- does every published window have its OWN draw multiplier?

E256 measured the shuffled band's draw ladder inside ONE cell (era_2025_now) in two families
(head = first n sessions, tail = last n). E257 then had to widen every published band by a
multiplier read off that ladder, and because a fixed published window is neither the head nor the
tail of era_2025_now, it published the multiplier as a RANGE (2 families x 7 rungs, 1.098..1.664)
and re-judged every row at all fourteen values.

That is an honest compromise, not a measurement. The question this face asks is the one E257 could
not answer from published faces:

    for the window that actually produced each published band, how much does the band's 5%
    endpoint rise between the draws that band was measured at and the top draw budget?

This is not arithmetic on published faces: it rebuilds the shuffle band inside each published
window. Four things are pinned so the measurement is the SAME object as the band it widens:

  1. THE WINDOW comes from the published cell's own first/last dates, so the sessions are the
     sessions the band was built on.
  2. THE STAR is the star that cell published (`cell.star`), not a re-named one; a re-named star
     would price a different sleeve's null and the multiplier would not belong to this band.
  3. THE BASE DRAW COUNT is the row's own published band draw count (60 for the era cells, 200 for
     all_five), read off the row, never assumed.
  4. PREFIX NESTING as in E256/E255: one draw stream per seed at max(d_grid) is read back at every
     smaller count, so the columns are one experiment read several ways, not several experiments.

What is published per window: the multiplier (median over seeds) plus its seed scatter, and per row
the local re-judgement (`outside` recomputed on a band whose two edges are both scaled by the
window's own multiplier), beside E257's borrowed-range verdict for the same row. A row whose local
verdict disagrees with E257's is named, not averaged away.

NO BILL, NO ADOPTION, NO RE-PRICING, NO PANEL TRADE: this face measures how fast one band moves with
its own draw count. It prices nothing and moves no coefficient.
"""

from __future__ import annotations

import argparse
import io
import json
import math
import os
import statistics
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e239_own_vs_cross as e239  # noqa: E402
import e252_star_prices_itself as e252  # noqa: E402
import e255_band_draw_starvation as e255  # noqa: E402
import e257_band_at_top_flips as e257  # noqa: E402

ROOT = e252.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

STUDY = "E258_band_multiplier_per_window"
CUTOFF = "2026-10-29"

FACE_STARSELF = "STARSELF-2026-10-29.json"
FACE_STAROWN = "STAROWN-2026-10-29.json"
FACE_E257 = "BANDTOPFLIP-2026-10-29.json"

SEEDS = 3                      # E256's budget: 3 independent streams, median read
D_GRID = (60, 120, 200, 480, 960, 1920)   # 60/200 = both published base counts in the family
TOP_DRAWS = max(D_GRID)
N_MIN = e255.e254.N_MIN
BASE_SEED = e255.BASE_SEED

VERDICT_VOCAB = (
    "local_multiplier_flips_published_verdicts",
    "local_verdicts_depend_on_seed_scatter",
    "every_published_verdict_survives_its_own_windows_multiplier",
    "no_windows_measured",
)

NO_BILL = ("measurement only: each band is rebuilt inside its own published window; no coefficient "
           "is re-priced, no member is billed, nothing is adopted")


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


# ------------------------------------------------------------------ windows from published cells
def cells_of(face):
    """{label: {first, last, sessions, star, star_source}} from a published star face."""
    out = {}
    for c in (face.get("cells") or []):
        label = c.get("label")
        if not label or not c.get("first") or not c.get("last"):
            continue
        out[label] = {"label": label, "first": c.get("first"), "last": c.get("last"),
                      "sessions": c.get("sessions"), "star": c.get("star"),
                      "star_source": c.get("star_source"),
                      "members": list(c.get("members") or [])}
    return out


def measure_windows(per, syms, cells, seeds=SEEDS, d_grid=D_GRID):
    """One measurement per published window, pinned to that window's own star AND members.

    The members matter as much as the star: early_three is a three-member window whose star is
    sh510050. Measuring it on the five-member basket intersects five level series over 2013-2016
    and returns ZERO sessions, which reads as "this window cannot be measured" when the real cause
    is that the window was measured on the wrong universe.
    """
    out, skipped = [], []
    for label, c in sorted(cells.items()):
        if not c.get("star"):
            skipped.append({"cell": label, "window": [c.get("first"), c.get("last")],
                            "reason": "the published cell names no star, so there is no sleeve "
                                      "whose null this band is"})
            continue
        members = [m for m in (c.get("members") or syms) if per.get(m)]
        if not members:
            skipped.append({"cell": label, "window": [c.get("first"), c.get("last")],
                            "reason": "none of the cell's members are in the panel"})
            continue
        rec, why = e255.measure_window(per, members, c["first"], c["last"], c["star"],
                                       seeds=seeds, d_grid=d_grid)
        if rec is None:
            skipped.append({"cell": label, "window": [c.get("first"), c["last"]],
                            "reason": why})
            continue
        rec["cell"] = label
        rec["members"] = members
        rec["published_star"] = c.get("star")
        rec["published_star_source"] = c.get("star_source")
        rec["star_repinned"] = (rec.get("star") != c.get("star"))
        out.append(rec)
    return out, skipped


# ------------------------------------------------------------------ multiplier arithmetic
def edge_series(win, leg="self"):
    """[(draws, edge)] sorted, from a window's by_draws table."""
    series = []
    for d, cell in ((win.get("by_draws") or {}).items()):
        e = (cell or {}).get("edge_" + leg)
        if e is not None:
            series.append((int(d), float(e)))
    return sorted(series)


def multiplier_at(win, base_draws, top=TOP_DRAWS, leg="self"):
    """m = edge(top)/edge(base) for this window, with the same ratio per seed.

    Both the pooled edge and every seed's own edge are read through E257's log-log interpolation,
    so a base or top count that falls between grid points is interpolated rather than snapped.
    """
    series = edge_series(win, leg)
    if not series:
        return None
    e_top = e257.edge_at(series, top)
    e_base = e257.edge_at(series, base_draws)
    if not e_top or not e_base:
        return None
    per_seed = []
    for k in range(int(win.get("seeds") or 0)):
        s = []
        for d, cell in ((win.get("by_draws") or {}).items()):
            vals = (cell or {}).get("edge_%s_per_seed" % leg) or []
            if k < len(vals) and vals[k] is not None:
                s.append((int(d), float(vals[k])))
        s = sorted(s)
        if not s:
            continue
        eb = e257.edge_at(s, base_draws)
        et = e257.edge_at(s, top)
        if eb and et:
            per_seed.append(et / eb)
    return {"base_draws": float(base_draws), "top_draws": top,
            "edge_base": e_base, "edge_top": e_top,
            "multiplier": e_top / e_base,
            "multiplier_per_seed": per_seed,
            "multiplier_min": min(per_seed) if per_seed else e_top / e_base,
            "multiplier_max": max(per_seed) if per_seed else e_top / e_base,
            "seed_scatter": (max(per_seed) - min(per_seed)) if len(per_seed) > 1 else None}


def published_verdicts(face):
    """{(source, cell, row): published row} from the E257 face.

    The whole row travels, not just its verdict: the borrowed multiplier range and the borrowed
    margin live in that row, and printing "n/a..n/a" beside a measured multiplier would hide the
    very comparison this face exists to make.
    """
    out = {}
    for r in ((face or {}).get("rows") or []):
        key = (r.get("source"), r.get("cell"), r.get("row"))
        if key[0] is not None and r.get("verdict"):
            out[key] = r
    return out


def window_multipliers(windows, base_counts=(60, 200), top=TOP_DRAWS):
    """{cell: {base: multiplier record}} for every window and every published base count."""
    out = {}
    for w in windows:
        table = {}
        for b in base_counts:
            m = multiplier_at(w, b, top=top)
            if m is not None:
                table[str(b)] = m
        out[w["cell"]] = {"cell": w["cell"], "sessions": w.get("sessions"),
                          "first": w.get("first"), "last": w.get("last"),
                          "star": w.get("star"), "by_base": table}
    return out


# ------------------------------------------------------------------ local re-judgement
def rejudge_local(rows, wm, published=None):
    """Re-judge each published row with the multiplier measured inside ITS OWN window.

    `published` maps (source, cell, row) -> E257's verdict for the same row, so the local reading
    is published BESIDE the borrowed-range reading instead of replacing it.
    """
    published = published or {}
    out = []
    for r in rows:
        rec = dict(r)
        prior = published.get((r.get("source"), r.get("cell"), r.get("row")))
        if prior is not None:
            rec["e257_verdict"] = prior.get("verdict")
            rec["e257_row_present"] = True
            for k in ("multiplier_min", "multiplier_max", "multiplier_median",
                      "margin_at_top_median"):
                if prior.get(k) is not None:
                    rec[k] = prior[k]
        w = wm.get(r.get("cell"))
        b, lo, hi = r.get("b"), r.get("band_lo"), r.get("band_hi")
        if b is None or lo is None or hi is None:
            rec.update({"local_verdict": "unjudgeable",
                        "local_reason": "row carries no coefficient or no band"})
            out.append(rec)
            continue
        base = float(r.get("band_draws") or 200)
        mrec = None
        if w:
            mrec = (w.get("by_base") or {}).get(str(int(base))) or None
            if mrec is None:
                mrec = multiplier_at({"by_draws": {}}, base) if False else None
        if not mrec:
            rec.update({"local_verdict": "unjudgeable",
                        "local_reason": "no local multiplier at the row's own published draw "
                                        "count %d (window not measured or count absent)" % int(base)})
            out.append(rec)
            continue
        pub = e257.outside(b, lo, hi)
        rec["outside_at_published"] = pub
        if r.get("published_outside") is not None and pub != bool(r["published_outside"]):
            rec.update({"local_verdict": "published_flag_not_reproduced",
                        "local_reason": "recomputed flag %r != published %r"
                                        % (pub, r["published_outside"])})
            out.append(rec)
            continue
        ms = mrec.get("multiplier_per_seed") or [mrec["multiplier"]]
        outs = [e257.outside(b, *e257.scale_band(lo, hi, m)) for m in ms]
        m_med = mrec["multiplier"]
        lo_m, hi_m = e257.scale_band(lo, hi, m_med)
        rec.update({
            "local_multiplier": m_med,
            "local_multiplier_min": mrec.get("multiplier_min"),
            "local_multiplier_max": mrec.get("multiplier_max"),
            "local_seed_scatter": mrec.get("seed_scatter"),
            "local_base_draws": mrec.get("base_draws"),
            "local_top_draws": mrec.get("top_draws"),
            "local_edge_base": mrec.get("edge_base"),
            "local_edge_top": mrec.get("edge_top"),
            "edge_at_published": max(abs(lo), abs(hi)),
            "band_at_local": [lo_m, hi_m],
            "edge_at_local": max(abs(lo_m), abs(hi_m)),
            "margin_at_published": abs(b) / max(abs(lo), abs(hi)),
            "margin_at_local": abs(b) / max(abs(lo_m), abs(hi_m)),
            "outside_at_local_seeds": outs,
            "outside_at_local_all_seeds": all(outs),
            "outside_at_local_any_seed": any(outs),
            "flips_at_local": bool(e257.outside(b, lo_m, hi_m) != pub),
            "flips_on_every_seed": all(o != pub for o in outs),
            "flips_on_any_seed": any(o != pub for o in outs),
            "e257_verdict": rec.get("e257_verdict"),
        })
        if rec["flips_on_every_seed"]:
            rec["local_verdict"] = "flips_at_local_multiplier"
        elif rec["flips_on_any_seed"]:
            rec["local_verdict"] = "flips_depends_on_seed_scatter"
        elif pub:
            rec["local_verdict"] = "survives_outside"
        else:
            rec["local_verdict"] = "stays_inside"
        out.append(rec)
    return out


def agreement(row):
    """Does the locally measured multiplier reach E257's borrowed-range verdict on this row?"""
    local = row.get("local_verdict")
    borrowed = row.get("e257_verdict")
    if local is None or borrowed is None:
        return "not_comparable"
    if local in ("unjudgeable", "published_flag_not_reproduced"):
        return "not_comparable"
    if local == borrowed:
        return "same"
    if local == "flips_depends_on_seed_scatter" and borrowed == "flips_depends_on_measurement":
        return "same_shape_different_axis"
    return "differs"


# ------------------------------------------------------------------ verdict
def spread_readout(wm):
    """Is the multiplier one object across windows, or does each window have its own?"""
    vals = []
    for cell, rec in (wm or {}).items():
        for base, m in ((rec or {}).get("by_base") or {}).items():
            vals.append((cell, int(base), m.get("multiplier")))
    vals = [v for v in vals if v[2] is not None]
    if not vals:
        return {"n": 0, "spread_note": "no multiplier measured"}
    ms = [v[2] for v in vals]
    lo = min(vals, key=lambda v: v[2])
    hi = max(vals, key=lambda v: v[2])
    return {"n": len(vals), "min": min(ms), "max": max(ms),
            "median": statistics.median(ms), "ratio_max_over_min": max(ms) / min(ms),
            "min_at": {"cell": lo[0], "base_draws": lo[1], "multiplier": lo[2]},
            "max_at": {"cell": hi[0], "base_draws": hi[1], "multiplier": hi[2]},
            "differs_by_more_than_15pct": (max(ms) / min(ms)) > 1.15,
            "spread_note": ("the spread is the measured statement: one multiplier per window "
                            "replaces E257's borrowed range")}


def compare_borrowed(wm, e257face):
    """Does any window's OWN multiplier fall outside the range E257 borrowed from era_2025_now?

    E257 published its multiplier as a range precisely because it could not measure a fixed
    window; if a measured window lands outside that range, the range under- or over-widened that
    window's band, and the size of the gap is a measured number rather than a caveat.
    """
    tab = (e257face or {}).get("multiplier_table") or {}
    lo, hi = tab.get("multiplier_min"), tab.get("multiplier_max")
    if lo is None or hi is None:
        return {"borrowed_range": None, "windows": [], "n_outside": None,
                "note": "the E257 face is absent, so there is no borrowed range to compare"}
    rows = []
    for cell, rec in sorted((wm or {}).items()):
        for base, m in sorted((rec.get("by_base") or {}).items(), key=lambda kv: int(kv[0])):
            v = m.get("multiplier")
            if v is None:
                continue
            rows.append({"cell": cell, "base_draws": int(base), "multiplier": v,
                         "inside_borrowed_range": bool(lo <= v <= hi),
                         "gap_vs_nearest_edge": (0.0 if lo <= v <= hi
                                                 else (v - hi if v > hi else v - lo)),
                         "ratio_to_borrowed_max": v / hi})
    outside = [r for r in rows if not r["inside_borrowed_range"]]
    return {"borrowed_range": [lo, hi], "windows": rows, "n": len(rows),
            "n_outside": len(outside),
            "outside": [{"cell": r["cell"], "base_draws": r["base_draws"],
                         "multiplier": r["multiplier"]} for r in outside],
            "max_ratio_to_borrowed_max": max([r["ratio_to_borrowed_max"] for r in rows] or [None])
            if rows else None,
            "BASIS_WARNING": ("E257's table range was read at ITS OWN default base draw count "
                              "(200). A cell measured at 60 draws is not comparable to it, so this "
                              "block is published for completeness only -- the same-base comparison "
                              "is rows_vs_borrowed_range, which uses each row's own published draw "
                              "count on both sides."),
            "note": ("the borrowed range was measured on era_2025_now's head/tail ladder and "
                     "applied to every window; a measured window outside it was widened by the "
                     "wrong amount -- but only if the two numbers were read at the same base")}


def rows_vs_borrowed_range(rows):
    """The same-base comparison: each row's measured multiplier vs the range E257 applied to it.

    E257 gave every row its own range (the ladder read at that row's published draw count). That is
    the only range this face may be compared against, and it is far wider than the table headline
    because it spans rung lengths the row never had. Publishing both is the point: the per-window
    measurement replaces a 74%-wide borrowed range with this window's own seed scatter.
    """
    out = []
    for r in rows:
        m = r.get("local_multiplier")
        lo, hi = r.get("multiplier_min"), r.get("multiplier_max")
        if m is None or lo is None or hi is None:
            continue
        out.append({"cell": r.get("cell"), "row": r.get("row"), "source": r.get("source"),
                    "base_draws": r.get("local_base_draws"),
                    "local_multiplier": m,
                    "borrowed_range_at_same_base": [lo, hi],
                    "inside_borrowed_range": bool(lo <= m <= hi),
                    "borrowed_range_width": (hi - lo) if hi >= lo else None,
                    "local_seed_range_width": ((r.get("local_multiplier_max") or m)
                                               - (r.get("local_multiplier_min") or m))})
    return {"rows": out, "n": len(out),
            "n_outside": len([x for x in out if not x["inside_borrowed_range"]]),
            "median_borrowed_width": (sorted(x["borrowed_range_width"] for x in out
                                             if x["borrowed_range_width"] is not None)[
                len(out) // 2] if out else None),
            "note": ("same-base comparison: E257's per-row range was the ladder read at that row's "
                     "own published draw count, so unlike the table range it IS comparable")}


def verdict_from(rows, wm):
    judged = [r for r in rows if r.get("local_verdict") not in
              ("unjudgeable", "published_flag_not_reproduced")]
    if not judged:
        return ("no_windows_measured",
                "no published row could be re-judged with a multiplier from its own window")
    flips = [r for r in judged if r.get("local_verdict") == "flips_at_local_multiplier"]
    dep = [r for r in judged if r.get("local_verdict") == "flips_depends_on_seed_scatter"]
    surv = [r for r in judged if r.get("local_verdict").startswith("survives")]
    if flips:
        return ("local_multiplier_flips_published_verdicts",
                "%d row(s) flip on every seed when the band is widened by their own window's "
                "multiplier; %d depend on the seed, %d survive" % (len(flips), len(dep), len(surv)))
    if dep:
        return ("local_verdicts_depend_on_seed_scatter",
                "no row flips on every seed, but %d flip for some seeds" % len(dep))
    return ("every_published_verdict_survives_its_own_windows_multiplier",
            "%d judged row(s) stay outside a band widened by their own window's multiplier "
            "(%d survive as outside, the rest stay inside)"
            % (len(judged), len(surv)))


# ------------------------------------------------------------------ run
def run(per=None, save=True, outdir=None, seeds=SEEDS, d_grid=D_GRID):
    outdir = outdir or OUTDIR
    starself = _try_load(FACE_STARSELF)
    starown = _try_load(FACE_STAROWN)
    e257face = _try_load(FACE_E257)
    missing = [n for n, f in (("starself", starself), ("starown", starown), ("e257", e257face))
               if f is None]
    if starself is None:
        face = {"study": STUDY,
                "title": "does every published window have its own draw multiplier?",
                "evidence_cutoff": CUTOFF,
                "generated": datetime.now().isoformat(timespec="seconds"),
                "verdict": "no_windows_measured",
                "verdict_reason": "the published star face is absent, so there is no window to "
                                  "measure inside",
                "faces_missing": missing, "windows": [], "rows": [],
                "frozen_spec": frozen_spec(seeds, d_grid), "no_bill": NO_BILL}
        face["summary"] = _summary(face)
        if save:
            _write(face, outdir)
        return face

    per = per if per is not None else e239.panels()
    syms = [s for s in e252.BASKET if per.get(s)]
    cells = cells_of(starself)
    windows, skipped = measure_windows(per, syms, cells, seeds=seeds, d_grid=d_grid)
    wm = window_multipliers(windows)

    prior = published_verdicts(e257face)
    rows = []
    if e257face is not None:
        rows += rejudge_local(e257.starself_rows(starself), wm, prior)
        if starown is not None:
            rows += rejudge_local(e257.starown_rows(starown), wm, prior)
    else:
        rows += rejudge_local(e257.starself_rows(starself), wm, prior)

    v, why = verdict_from(rows, wm)
    face = {
        "study": STUDY,
        "title": "does every published window have its own draw multiplier?",
        "evidence_cutoff": (max([w.get("last") for w in windows if w.get("last")] or [CUTOFF])),
        "generated": datetime.now().isoformat(timespec="seconds"),
        "frozen_spec": frozen_spec(seeds, d_grid),
        "source_faces": {"starself": "results/state_tilt/" + FACE_STARSELF,
                         "starown": "results/state_tilt/" + FACE_STAROWN,
                         "e257": "results/state_tilt/" + FACE_E257},
        "faces_missing": missing,
        "windows": wm,
        "windows_skipped": skipped,
        "windows_measured": sorted(wm.keys()),
        "multiplier_spread": spread_readout(wm),
        "windows_vs_borrowed_range": compare_borrowed(wm, e257face),
        "rows_vs_borrowed_range": rows_vs_borrowed_range(rows),
        "e257_borrowed_range": (None if e257face is None else {
            "min": ((e257face.get("multiplier_table") or {}).get("multiplier_min")),
            "max": ((e257face.get("multiplier_table") or {}).get("multiplier_max")),
            "median": ((e257face.get("multiplier_table") or {}).get("multiplier_median")),
            "note": "E257 read this off era_2025_now's head/tail ladder and applied it to every "
                    "window as a range; this face measures each window instead"}),
        "rows": rows,
        "verdict": v,
        "verdict_reason": why,
        "no_bill": NO_BILL,
    }
    face["summary"] = _summary(face)
    if save:
        _write(face, outdir)
    return face


def frozen_spec(seeds=SEEDS, d_grid=D_GRID):
    return {
        "design": "rebuild the paired shuffled band INSIDE each published window and measure that "
                  "window's own draw multiplier; no panel trade, no re-pricing",
        "window": "the published cell's own first/last dates (the sessions the band was built on)",
        "star": "pinned to the star the cell published (cell.star); a re-named star would price a "
                "different sleeve's null and the multiplier would not belong to this band",
        "base_draws": "each row's own published band draw count (60 for the era cells, 200 for "
                      "all_five), read off the row",
        "top_draws": TOP_DRAWS,
        "draw_grid": list(d_grid),
        "prefix_nesting": "one draw stream per seed at max(draw_grid); every smaller count reads "
                          "its own PREFIX, so the columns are one experiment read several ways",
        "seeds": seeds,
        "base_seed": BASE_SEED,
        "n_min": N_MIN,
        "multiplier": "m = edge(top)/edge(published draws), both edges through E257's log-log "
                      "interpolation in the draw count; published with the per-seed scatter",
        "rejudge_rule": "the published rule, unchanged: outside = value < lo or value > hi, applied "
                        "to a band whose two edges are both scaled by the window's own multiplier",
        "what_is_not_done": ["no coefficient is re-priced", "no member is billed",
                             "no verdict in the source faces is rewritten",
                             "no adoption and no bill"],
    }


def _summary(face):
    rows = face.get("rows") or []
    buckets = {}
    for r in rows:
        buckets[r.get("local_verdict")] = buckets.get(r.get("local_verdict"), 0) + 1
    judged = [r for r in rows if r.get("local_verdict") not in
              ("unjudgeable", "published_flag_not_reproduced")]
    agr = {}
    for r in rows:
        a = agreement(r)
        agr[a] = agr.get(a, 0) + 1
    sp = face.get("multiplier_spread") or {}
    return {
        "windows_measured": len(face.get("windows_measured") or []),
        "windows_skipped": len(face.get("windows_skipped") or []),
        "rows": len(rows),
        "rows_judged": len(judged),
        "rows_by_local_verdict": buckets,
        "rows_flip_every_seed": len([r for r in judged
                                     if r.get("local_verdict") == "flips_at_local_multiplier"]),
        "rows_flip_some_seed": len([r for r in judged
                                     if r.get("local_verdict") == "flips_depends_on_seed_scatter"]),
        "rows_survive_outside": len([r for r in judged
                                      if r.get("local_verdict") == "survives_outside"]),
        "agreement_with_e257_range": agr,
        "multiplier_min": sp.get("min"),
        "multiplier_max": sp.get("max"),
        "multiplier_median": sp.get("median"),
        "multiplier_spread_ratio": sp.get("ratio_max_over_min"),
        "multiplier_differs_by_more_than_15pct": sp.get("differs_by_more_than_15pct"),
        "rows_counts_add_up": sum(buckets.values()) == len(rows),
        "tightest_survivor_margin_at_local": min(
            [r.get("margin_at_local") for r in judged
             if r.get("local_verdict") == "survives_outside"
             and r.get("margin_at_local") is not None] or [None])
        if any(r.get("local_verdict") == "survives_outside" for r in judged) else None,
    }


def _write(face, outdir, tag=""):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "BANDWINMULT-%s%s.json" % (CUTOFF, tag))
    with io.open(path, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    latest = os.path.join(outdir, "bandwinmult_latest.json")
    with io.open(latest, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    face["written"] = os.path.relpath(path, ROOT)
    return path


def _r(v, n=4):
    return "n/a" if v is None else ("%." + str(n) + "f") % v


def _fmt(face):
    s = face.get("summary") or {}
    sp = face.get("multiplier_spread") or {}
    lines = [
        "E258 window multiplier -- %s" % face.get("study"),
        "verdict: %s" % face.get("verdict"),
        "  %s" % face.get("verdict_reason"),
        "windows measured %s (skipped %s)" % (s.get("windows_measured"), s.get("windows_skipped")),
        "multiplier across windows %.4f .. %.4f median %.4f (ratio %.2f)"
        % (sp.get("min") or 0, sp.get("max") or 0, sp.get("median") or 0,
           sp.get("ratio_max_over_min") or 0),
        "rows %s (judged %s): flip-every-seed %s  flip-some-seed %s  survive %s"
        % (s.get("rows"), s.get("rows_judged"), s.get("rows_flip_every_seed"),
           s.get("rows_flip_some_seed"), s.get("rows_survive_outside")),
        "agreement with E257 range: %s" % (s.get("agreement_with_e257_range") or {}),
        "cross-base block (informational, bases differ): %s of %s cells outside the TABLE range %s"
        % ((face.get("windows_vs_borrowed_range") or {}).get("n_outside"),
           (face.get("windows_vs_borrowed_range") or {}).get("n"),
           (face.get("windows_vs_borrowed_range") or {}).get("borrowed_range")),
        "SAME-BASE block: %s of %s rows outside their own borrowed range; median borrowed width %s "
        "vs median local seed width %s"
        % ((face.get("rows_vs_borrowed_range") or {}).get("n_outside"),
           (face.get("rows_vs_borrowed_range") or {}).get("n"),
           _r((face.get("rows_vs_borrowed_range") or {}).get("median_borrowed_width"), 3),
           _r(statistics.median([x["local_seed_range_width"] for x in
                                 ((face.get("rows_vs_borrowed_range") or {}).get("rows") or [])
                                 if x.get("local_seed_range_width") is not None] or [None]), 3)
           if (face.get("rows_vs_borrowed_range") or {}).get("rows") else "n/a"),
    ]
    for cell, rec in sorted((face.get("windows") or {}).items()):
        bits = []
        for base, m in sorted((rec.get("by_base") or {}).items(), key=lambda kv: int(kv[0])):
            bits.append("%s->%.3f" % (base, m.get("multiplier") or 0))
        lines.append("  window %-14s sessions %-5s star %-9s m: %s"
                     % (cell, rec.get("sessions"), rec.get("star"), "  ".join(bits)))
    for r in (face.get("rows") or []):
        if r.get("local_verdict") in ("flips_at_local_multiplier",
                                      "flips_depends_on_seed_scatter"):
            lines.append("  %-9s %-14s %-20s b=%s m_local=%s m_borrowed=%s..%s -> %s (was %s)"
                         % (r.get("source"), r.get("cell"), r.get("row"), _r(r.get("b"), 4),
                            _r(r.get("local_multiplier"), 4),
                            _r(r.get("multiplier_min"), 3), _r(r.get("multiplier_max"), 3),
                            r.get("local_verdict"), r.get("e257_verdict")))
    return "\n".join(lines)


# ------------------------------------------------------------------ verify
def verify(outdir=None, tag=""):
    outdir = outdir or OUTDIR
    path = os.path.join(outdir, "BANDWINMULT-%s%s.json" % (CUTOFF, tag))
    if not os.path.exists(path):
        return {"ok": False, "problems": ["face missing: %s" % path]}
    with io.open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    problems = []
    wm = face.get("windows") or {}
    rows = face.get("rows") or []
    # every multiplier must reproduce from its own window's edge table
    for cell, rec in wm.items():
        for base, m in (rec.get("by_base") or {}).items():
            e_base, e_top = m.get("edge_base"), m.get("edge_top")
            if not e_base or not e_top:
                problems.append("%s/%s: multiplier has no edges" % (cell, base))
                continue
            if abs((e_top / e_base) - m["multiplier"]) > 1e-9:
                problems.append("%s/%s: multiplier != edge_top/edge_base" % (cell, base))
            if m.get("multiplier_min") is not None and \
                    m["multiplier_min"] > m["multiplier"] + 1e-9:
                problems.append("%s/%s: per-seed min above the pooled multiplier" % (cell, base))
            if m.get("multiplier_max") is not None and \
                    m["multiplier_max"] < m["multiplier"] - 1e-9:
                problems.append("%s/%s: per-seed max below the pooled multiplier" % (cell, base))
    # every judged row's local verdict must follow from its own numbers
    for r in rows:
        lv = r.get("local_verdict")
        if lv in (None, "unjudgeable", "published_flag_not_reproduced"):
            continue
        lo_m, hi_m = (r.get("band_at_local") or [None, None])
        if lo_m is None or hi_m is None:
            problems.append("%s/%s/%s: judged without a local band"
                            % (r.get("source"), r.get("cell"), r.get("row")))
            continue
        want = e257.outside(r.get("b"), lo_m, hi_m)
        if (lv == "flips_at_local_multiplier") and want == r.get("outside_at_published"):
            problems.append("%s/%s/%s: marked flip but the local band keeps it"
                            % (r.get("source"), r.get("cell"), r.get("row")))
        if (lv in ("survives_outside", "stays_inside")) and want != r.get("outside_at_published"):
            problems.append("%s/%s/%s: marked stable but the local band moves it"
                            % (r.get("source"), r.get("cell"), r.get("row")))
    # the verdict must follow from the rows
    v, _why = verdict_from(rows, wm)
    if v != face.get("verdict"):
        problems.append("verdict %r does not follow from the rows (%r)"
                        % (face.get("verdict"), v))
    # the summary must agree with the rows
    s = face.get("summary") or {}
    if s.get("rows") != len(rows):
        problems.append("summary.rows %r != len(rows) %d" % (s.get("rows"), len(rows)))
    if not s.get("rows_counts_add_up"):
        problems.append("row verdict buckets do not add up")
    if s.get("windows_measured") != len(wm):
        problems.append("summary.windows_measured %r != %d"
                        % (s.get("windows_measured"), len(wm)))
    # the same-base borrowed comparison must follow from the rows
    rb = rows_vs_borrowed_range(rows)
    for x in rb["rows"]:
        if x["inside_borrowed_range"] != (x["borrowed_range_at_same_base"][0] <= x["local_multiplier"]
                                          <= x["borrowed_range_at_same_base"][1]):
            problems.append("%s/%s: same-base inside flag does not follow"
                            % (x["cell"], x["row"]))
    # the spread readout must match the windows
    sp = spread_readout(wm)
    got_sp = face.get("multiplier_spread") or {}
    if sp.get("n") and got_sp.get("n") and abs((sp.get("median") or 0)
                                              - (got_sp.get("median") or 0)) > 1e-12:
        problems.append("multiplier_spread.median does not reproduce")
    return {"ok": not problems, "problems": problems, "rows": len(rows),
            "windows": len(wm)}


# ------------------------------------------------------------------ selftest
_LEGS = []


def leg(ok, name, detail=None):
    _LEGS.append({"ok": bool(ok), "name": name, "detail": detail})
    return ok


def _fake_window(edges, per_seed=None, seeds=3):
    bd = {}
    for d, e in edges.items():
        rec = {"draws": d, "edge_self": e}
        if per_seed and d in per_seed:
            rec["edge_self_per_seed"] = per_seed[d]
        bd[str(d)] = rec
    return {"by_draws": bd, "seeds": seeds, "sessions": 400, "first": "2025-01-02",
            "last": "2026-10-29", "star": "X"}


def selftest():
    del _LEGS[:]
    # 1 multiplier arithmetic on a rising ladder
    w = _fake_window({60: 0.40, 120: 0.50, 200: 0.55, 480: 0.62, 960: 0.70, 1920: 0.80})
    m60 = multiplier_at(w, 60)
    leg(abs(m60["multiplier"] - 2.0) < 1e-9, "m = edge(top)/edge(base) on a rising ladder",
        "m=%.4f" % (m60["multiplier"]))
    m_top = multiplier_at(w, 1920)
    leg(abs(m_top["multiplier"] - 1.0) < 1e-9,
        "the multiplier is exactly one when the base IS the top")
    m200 = multiplier_at(w, 200)
    leg(1.0 < m200["multiplier"] < 2.0, "a later base gives a smaller multiplier",
        "m200=%.4f" % m200["multiplier"])

    # 2 interpolation is used, not snapping (base between grid points)
    w2 = _fake_window({100: 0.5, 400: 1.0})
    m = multiplier_at(w2, 200, top=400)
    leg(m is not None and m["edge_base"] not in (0.5, 1.0),
        "a base between grid points is interpolated, not snapped",
        "edge_base=%.4f" % (m["edge_base"] if m else -1))

    # 3 seed scatter is published as a range around the pooled value
    w3 = _fake_window({60: 0.40, 480: 0.62, 1920: 0.80},
                      per_seed={60: [0.38, 0.40, 0.42], 480: [0.60, 0.62, 0.64],
                                1920: [0.76, 0.80, 0.84]})
    m3 = multiplier_at(w3, 60)
    leg(len(m3["multiplier_per_seed"]) == 3 and
        m3["multiplier_min"] <= m3["multiplier"] <= m3["multiplier_max"],
        "per-seed multipliers bracket the pooled multiplier",
        "%.3f <= %.3f <= %.3f" % (m3["multiplier_min"], m3["multiplier"], m3["multiplier_max"]))

    # 4 the three local verdicts
    wm = {"c": {"cell": "c", "sessions": 400, "by_base": {
        "60": {"base_draws": 60, "top_draws": 1920, "edge_base": 0.40, "edge_top": 0.80,
               "multiplier": 2.0, "multiplier_per_seed": [2.0], "multiplier_min": 2.0,
               "multiplier_max": 2.0, "seed_scatter": 0.0}}}}
    base = {"source": "T", "cell": "c", "row": "r", "sessions": 400, "b": 0.62,
            "band_lo": -0.55, "band_hi": 0.55, "band_draws": 60, "published_outside": True,
            "e257_verdict": "survives_outside"}
    got = rejudge_local([base], wm)[0]
    leg(got["local_verdict"] == "flips_at_local_multiplier",
        "a value just outside its band flips when the window's own multiplier widens it",
        got["local_verdict"])
    leg(got["margin_at_local"] < 1.0, "a flipped row reports a margin below one",
        "%.3f" % got["margin_at_local"])

    # a value 73% beyond the published edge: a 1.2x widening leaves it outside (0.55*1.2 = 0.66)
    wm_mild = {"c": {"cell": "c", "sessions": 400, "by_base": {
        "60": {"base_draws": 60, "top_draws": 1920, "edge_base": 0.40, "edge_top": 0.48,
               "multiplier": 1.2, "multiplier_per_seed": [1.2], "multiplier_min": 1.2,
               "multiplier_max": 1.2, "seed_scatter": 0.0}}}}
    far = dict(base, b=0.95)
    leg(rejudge_local([far], wm_mild)[0]["local_verdict"] == "survives_outside",
        "a far-outside value survives its own window's multiplier",
        rejudge_local([far], wm_mild)[0]["local_verdict"])
    inside = dict(base, b=0.10, published_outside=False)
    leg(rejudge_local([inside], wm)[0]["local_verdict"] == "stays_inside",
        "an inside value stays inside when the band widens")

    # 5 rows with no measured window are unjudgeable, never dropped
    orphan = dict(base, cell="not_measured")
    got = rejudge_local([orphan], wm)[0]
    leg(got["local_verdict"] == "unjudgeable" and "not_measured" not in
        (got.get("local_multiplier") or ""),
        "a row whose window was not measured is unjudgeable, not silently re-judged",
        got.get("local_reason"))
    lie = dict(base, b=0.10, published_outside=True)
    leg(rejudge_local([lie], wm)[0]["local_verdict"] == "published_flag_not_reproduced",
        "a published flag that does not reproduce is quarantined")

    # 6 verdict totality and agreement bookkeeping
    leg(verdict_from([], {})[0] == "no_windows_measured",
        "verdict_from is total on an empty row list")
    leg(agreement({"local_verdict": "survives_outside", "e257_verdict": "survives_outside"})
        == "same", "agreement reads 'same' for identical verdicts")
    leg(agreement({"local_verdict": "flips_at_local_multiplier",
                   "e257_verdict": "survives_outside"}) == "differs",
        "agreement names a disagreement instead of averaging it")

    # 7 spread readout: one number, and the flag fires only when windows really differ
    flat = {"a": {"by_base": {"60": {"multiplier": 1.20}}},
            "b": {"by_base": {"60": {"multiplier": 1.24}}}}
    sp = spread_readout(flat)
    leg(sp["n"] == 2 and not sp["differs_by_more_than_15pct"],
        "a tight spread does not raise the differs flag", "%.3f" % sp["ratio_max_over_min"])
    wide = {"a": {"by_base": {"60": {"multiplier": 1.10}}},
            "b": {"by_base": {"60": {"multiplier": 1.80}}}}
    leg(spread_readout(wide)["differs_by_more_than_15pct"],
        "a wide spread raises the differs flag")

    # 8 ACTIVITY: the real windows were measured and at least one multiplier is above one
    face = None
    try:
        face = load("BANDWINMULT-%s.json" % CUTOFF)
    except FileNotFoundError:
        face = None
    if face is not None:
        wm_r = face.get("windows") or {}
        leg(len(wm_r) >= 3, "ACTIVITY: at least three published windows were measured",
            "n=%d" % len(wm_r))
        moved = [m.get("multiplier") for rec in wm_r.values()
                 for m in (rec.get("by_base") or {}).values() if m.get("multiplier")]
        leg(bool(moved) and max(moved) > 1.02,
            "ACTIVITY: at least one window's band really rises with draws",
            "max m=%.4f" % (max(moved) if moved else 0))
        # consistency with E256: era_2025_now's local multiplier must be in a plausible band
        era = (wm_r.get("era_2025_now") or {}).get("by_base") or {}
        vals = [m.get("multiplier") for m in era.values() if m.get("multiplier")]
        leg(bool(vals) and all(1.0 <= v <= 2.5 for v in vals),
            "the era_2025_now local multiplier is above one and within 2.5x",
            repr([round(v, 4) for v in vals]))
        # every measured window must report its own sessions
        leg(all(rec.get("sessions") for rec in wm_r.values()),
            "every measured window carries its session count")
    else:
        leg(False, "ACTIVITY: the face is present", "missing")

    # 9 the face imports no panel or market-data library (import statements only)
    import re as _re
    src = io.open(os.path.abspath(__file__), encoding="utf-8").read()
    imports = [ln.strip() for ln in src.splitlines() if _re.match(r"^\s*(import|from)\s+\w", ln)]
    banned = ("pan" + "das", "num" + "py", "poly" + "gon", "ak" + "share")
    hits = [ln for ln in imports if any(b in ln for b in banned)]
    leg(not hits, "the face imports no panel or market-data library", repr(hits)[:100])

    ok = sum(1 for l in _LEGS if l["ok"])
    return {"ok": ok == len(_LEGS), "passed": ok, "total": len(_LEGS), "legs": _LEGS}


# ------------------------------------------------------------------ main
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(description=STUDY)
    sub = ap.add_subparsers(dest="cmd")
    p_run = sub.add_parser("run")
    p_run.add_argument("--no-save", action="store_true")
    p_run.add_argument("--seeds", type=int, default=SEEDS)
    sub.add_parser("selftest")
    p_v = sub.add_parser("verify")
    p_v.add_argument("--tag", default="")
    sub.add_parser("print")
    args = ap.parse_args(argv)
    if args.cmd == "run":
        face = run(save=not args.no_save, seeds=args.seeds)
        print(_fmt(face))
        return 0
    if args.cmd == "selftest":
        res = selftest()
        for l in res["legs"]:
            print(("PASS " if l["ok"] else "FAIL ") + l["name"] +
                  ("" if l["detail"] in (None, "") else "  [%s]" % (l["detail"],)))
        print("%d/%d legs" % (res["passed"], res["total"]))
        return 0 if res["ok"] else 1
    if args.cmd == "verify":
        res = verify(tag=args.tag)
        for p in res["problems"]:
            print("PROBLEM " + p)
        print("verify %s (%d rows, %d windows)"
              % ("OK" if res["ok"] else "FAILED", res.get("rows", 0), res.get("windows", 0)))
        return 0 if res["ok"] else 1
    if args.cmd == "print":
        print(_fmt(load("BANDWINMULT-%s.json" % CUTOFF)))
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())