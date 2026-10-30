#!/usr/bin/env python3
"""E263 -- does a window need more draws because it is longer, or because its band is narrower?

E260 measured WHERE each seed's band endpoint stops moving on windows of 1328 down to a few hundred
sessions, and found the published base counts (60/200) far below the arrival (median 1440 draws).
That leaves the practical question E260 did not answer: is the draw requirement a property of the
WINDOW (longer windows carry more data, so more of them are needed to reach a stable endpoint) or a
property of the BAND (a narrower band is a tighter claim, so more draws are needed to resolve it)?

If the answer is the length, the fix is a per-window draw budget. If it is the band, the fix is a draw
budget keyed on the band width. If it is NEITHER, the draw requirement is roughly uniform and the
only honest fix is one flat floor applied everywhere -- and a per-window budget would be a knob that
buys nothing.

THIS FACE ANSWERS ONLY THAT, AND ADDS NO DRAWS. It reads the per-seed edge tables E260 already
published (E259's BANDWINDIST windows_raw: 4 windows x 2 legs x 40 seeds x 6 draw counts) and
publishes:

  per arm (window x leg):  sessions, the band width the row publishes, the settled-edge spread,
                           the RESOLUTION RATIO R = spread / (band width / 2), the settled-share
                           curve across the draw grid, the area under that curve, and E260's arrival
  per seed (320):          arrival against the magnitude of the seed's own settled edge
  two rival channels:      Spearman(settled area, sessions)          -- the LENGTH rival
                           Spearman(settled area, resolution ratio)  -- the BAND rival
  a power statement:       the smallest |rho| an 8-arm design can call at p<0.05, enumerated exactly

THE RESPONSE IS THE SETTLED SHARE, NOT THE ARRIVAL MEDIAN, and that choice is forced by the data:
E260's arrival is right-censored at the top of the grid (174 of 320 seeds reach their final endpoint
only AT 1920, so their true arrival is unknown and > 1920). A median over a censored column saturates
at the ceiling in 5 of 8 arms and carries almost no rank information. The settled share at a fixed
draw count is uncensored, monotone in arrival, and is published per draw count so a reader can see
the whole curve rather than one summary. The censored share is published beside it and never hidden.

The reference point is excluded from the area: settled share at the TOP draw count is 1.0 by
construction ("does the edge at 1920 equal the edge at 1920"), so including it would add a constant
to every arm and shrink every difference for no information.

NO BILL, NO ADOPTION, NO RE-PRICING, NO PANEL TRADE: measurement only, on an already-published face.
Nothing here re-prices a band, changes a draw count, or admits a row.
"""

from __future__ import annotations

import argparse
import csv
import io
import itertools
import json
import os
import random
import statistics
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e259_band_multiplier_distribution as e259  # noqa: E402

ROOT = e259.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

STUDY = "E263_arrival_vs_cell_size"
TITLE = "does a window need more draws because it is longer, or because its band is narrower?"
CUTOFF = "2026-10-29"
FACE = "BANDARRIVALATE-%s.json" % CUTOFF
SRC_ARRIVAL = "BANDARRIVAL-%s.json" % CUTOFF
SRC_WIDTH = "BANDWINDIST-%s.json" % CUTOFF
CAL_REL = os.path.join("data", "exchange_calendar.csv")

LEGS = ("self", "cross")
GRID = (60, 120, 200, 480, 960, 1920)
TOP = 1920
TOL = 1e-12            # E260's own equality rule for "the endpoint stopped moving"
PERM_N = 20000         # frozen permutation budget
PERM_SEED = 20261130   # frozen: the same 20k resamples on every run
MIN_SEEDS = 8          # below this a per-arm seeded rank correlation is not published
ALPHA = 0.05           # frozen two-sided line

VERDICT_VOCAB = (
    "arrival_is_a_length_effect",
    "arrival_is_a_band_effect",
    "arrival_is_both_channels",
    "arrival_is_neither_channel",
    "no_windows_measured",
)

NO_BILL = ("measurement only: E260's published per-seed edge tables are re-read to test whether the "
           "draw count a window needs tracks its length or its band width; no draw is added, no "
           "coefficient is re-priced, no band is re-drawn, nothing is adopted")


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


def source_arrival():
    return _try_load(SRC_ARRIVAL)


def source_width():
    return _try_load(SRC_WIDTH)


def load_calendar(path=None):
    """The official trading calendar -- the window's own panel is never its own calendar (E136)."""
    path = path or os.path.join(ROOT, CAL_REL)
    try:
        with io.open(path, encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
    except FileNotFoundError:
        return None
    out = []
    for row in rows:
        if not row:
            continue
        cell = row[0].strip()
        if len(cell) == 10 and cell[4] == "-" and cell[7] == "-" and cell[:4].isdigit():
            out.append(cell)
    return sorted(set(out))


def sessions_between(cal, first, last):
    """Count the calendar's sessions that fall inside a closed window; None if the calendar is absent."""
    if not cal or not first or not last:
        return None
    return sum(1 for d in cal if first <= d <= last)


# ------------------------------------------------------------------ ranks and permutation
def ranks(values):
    """Average ranks, so a column full of ties cannot silently produce a correlation."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            out[order[k]] = avg
        i = j + 1
    return out


def spearman(x, y):
    if len(x) != len(y) or len(x) < 3:
        return None
    rx, ry = ranks(x), ranks(y)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    if den == 0:
        return None
    return num / den


def spearman_perm(x, y, n=None, seed=None):
    """Two-sided permutation p for |rho|, from a frozen resample budget."""
    rho = spearman(x, y)
    if rho is None:
        return None, None
    n = n or PERM_N
    rng = random.Random(PERM_SEED if seed is None else seed)
    yy = list(y)
    hit = 0
    limit = abs(rho) - 1e-12
    for _ in range(n):
        rng.shuffle(yy)
        r = spearman(x, yy)
        if r is not None and abs(r) >= limit:
            hit += 1
    return rho, (hit + 1.0) / (n + 1.0)


def critical_rho(n, alpha=None):
    """The smallest |rho| that a two-sided permutation test of n ranks can call at `alpha`.

    Enumerated exactly rather than tabled: n is 8 here, so all 40320 orderings are cheap, and a
    hand-copied table would be one more number nobody re-derives.
    """
    alpha = ALPHA if alpha is None else alpha
    if n < 3 or n > 8:
        return None
    base = list(range(n))
    obs = list(range(n))
    rhos = []
    for perm in itertools.permutations(base):
        rhos.append(abs(spearman(obs, list(perm))))
    rhos.sort()
    total = len(rhos)
    for r in rhos:
        # the share of orderings that reach |rho| >= r, two-sided
        k = sum(1 for v in rhos if v >= r - 1e-12)
        if k / float(total) <= alpha:
            return r
    return 1.0


# ------------------------------------------------------------------ the measurement
def settled_share(edge_at_d, top, tol=TOL):
    """Share of seeds whose edge at this draw count already equals their own top-draw edge."""
    pairs = [(a, b) for a, b in zip(edge_at_d, top) if a is not None and b is not None]
    if not pairs:
        return None, 0
    hit = sum(1 for a, b in pairs if abs(float(a) - float(b)) <= tol)
    return hit / float(len(pairs)), len(pairs)


def arrival_of(edges_by_draws, leg, grid=GRID, top=TOP, tol=TOL):
    """E260's rule, recomputed from the same table: the first grid count that equals the top edge."""
    top_vals = edges_by_draws[str(top)][leg]
    out = []
    for i, tv in enumerate(top_vals):
        if tv is None:
            out.append(None)
            continue
        found = None
        for d in grid:
            v = edges_by_draws[str(d)][leg][i]
            if v is not None and abs(float(v) - float(tv)) <= tol:
                found = int(d)
                break
        out.append(found)
    return out


def band_of(width_face):
    """(cell, leg) -> the published band, straight off the rows that carry one."""
    out = {}
    for row in (width_face or {}).get("rows") or []:
        lo, hi = row.get("band_lo"), row.get("band_hi")
        if lo is None or hi is None:
            continue
        cell, leg = row.get("cell"), row.get("row")
        if not cell or leg not in LEGS:
            continue
        out[(cell, leg)] = {"band_lo": float(lo), "band_hi": float(hi),
                            "band_width": float(hi) - float(lo),
                            "band_draws": row.get("band_draws"),
                            "b": row.get("b")}
    return out


def arm_record(cell, leg, raw, arrival_face, bands, cal):
    """One window x leg: everything the two rivals need, published side by side."""
    edges = raw.get("by_draws") or {}
    if str(TOP) not in edges or leg not in (edges.get(str(TOP)) or {}):
        return None
    top = edges[str(TOP)][leg]
    usable = [v for v in top if v is not None]
    n_seeds = len(usable)
    if n_seeds < MIN_SEEDS:
        return None
    curve = {}
    for d in GRID:
        share, n = settled_share(edges.get(str(d), {}).get(leg) or [], top)
        if share is not None:
            curve[str(d)] = {"share_settled": share, "n_pairs": n}
    # the reference draw count is 1.0 by construction, so it is published and NOT counted
    body = [curve[str(d)]["share_settled"] for d in GRID[:-1] if str(d) in curve]
    area = statistics.mean(body) if body else None
    published = arrival_face.get("arrivals_per_seed", {}).get(cell, {}).get(leg) or []
    recomputed = arrival_of(edges, leg)
    band = bands.get((cell, leg)) or {}
    spread = statistics.stdev(usable) if n_seeds > 1 else None
    width = band.get("band_width")
    half = (width / 2.0) if width else None
    ratio = (spread / half) if (spread is not None and half) else None
    return {
        "cell": cell,
        "leg": leg,
        "first": raw.get("first"),
        "last": raw.get("last"),
        "sessions": sessions_between(cal, raw.get("first"), raw.get("last")),
        "n_seeds": n_seeds,
        "band_width": width,
        "band_half_width": half,
        "band_draws": band.get("band_draws"),
        "b_published": band.get("b"),
        "settled_edge_spread": spread,
        "resolution_ratio": ratio,
        "curve": curve,
        "settled_area": area,
        "arrival_median_median": (statistics.median([a for a in published if a is not None])
                                  if published else None),
        "arrival_recomputed_matches_e260": (published == recomputed),
        "arrival_censored_share": (sum(1 for a in published if a is not None and int(a) >= TOP)
                                   / float(len(published)) if published else None),
        "settled_edges": usable,
        "arrival_per_seed": published,
    }


def arms_of(arrival_face, width_face, cal):
    raw_windows = (width_face or {}).get("windows_raw") or {}
    bands = band_of(width_face)
    out = []
    for cell in sorted(raw_windows):
        for leg in LEGS:
            rec = arm_record(cell, leg, raw_windows[cell] or {}, arrival_face, bands, cal)
            if rec is not None:
                out.append(rec)
    return out


def channel(arms, key):
    """Spearman between the settled area and one rival covariate, with its permutation p."""
    pairs = [(a["settled_area"], a[key]) for a in arms
             if a.get("settled_area") is not None and a.get(key) is not None]
    if len(pairs) < 3:
        return {"n": len(pairs), "rho": None, "p": None, "answered": False,
                "covariate": key, "reason": "fewer than three arms carry this covariate"}
    x = [p[1] for p in pairs]
    y = [p[0] for p in pairs]
    rho, p = spearman_perm(x, y)
    return {"n": len(pairs), "rho": rho, "p": p,
            "answered": bool(rho is not None and p is not None and p < ALPHA),
            "covariate": key,
            "direction": (None if rho is None else
                          ("slower_settling_as_the_covariate_rises" if rho < 0
                           else "faster_settling_as_the_covariate_rises"))}


def per_seed_channel(arms):
    """Inside each arm: does a seed settle later when its own settled edge is smaller?

    The band rival says a tighter (smaller) claim needs more draws, so it predicts a NEGATIVE rank
    correlation between arrival and |settled edge|. This channel is uncensored-blind (arrivals at the
    ceiling are ties) so the uncensored-only reading is published beside it.
    """
    rows = []
    for a in arms:
        arr = a.get("arrival_per_seed") or []
        edges = a.get("settled_edges") or []
        pairs = [(x, abs(y)) for x, y in zip(arr, edges) if x is not None and y is not None]
        if len(pairs) < MIN_SEEDS:
            rows.append({"cell": a["cell"], "leg": a["leg"], "n": len(pairs),
                         "rho": None, "published": False,
                         "reason": "fewer than %d seeded pairs" % MIN_SEEDS})
            continue
        rho = spearman([m for _, m in pairs], [x for x, _ in pairs])
        unc = [(x, abs(y)) for x, y in zip(arr, edges)
               if x is not None and y is not None and int(x) < TOP]
        rho_unc = (spearman([m for _, m in unc], [x for x, _ in unc])
                   if len(unc) >= MIN_SEEDS else None)
        rows.append({"cell": a["cell"], "leg": a["leg"], "n": len(pairs),
                     "rho": rho, "published": rho is not None,
                     "n_uncensored": len(unc), "rho_uncensored": rho_unc})
    live = [r["rho"] for r in rows if r.get("rho") is not None]
    neg = sum(1 for r in live if r < 0)
    pos = sum(1 for r in live if r > 0)
    # exact two-sided sign test, enumerated
    n = neg + pos
    p_sign = None
    if n:
        k = min(neg, pos)
        tail = sum(_binom(n, i) for i in range(0, k + 1)) / float(2 ** n)
        p_sign = min(1.0, 2 * tail)
    return {
        "arms": len(rows),
        "arms_published": len(live),
        "rho_median": statistics.median(live) if live else None,
        "arms_negative": neg,
        "arms_positive": pos,
        "sign_test_p_two_sided": p_sign,
        "prediction": ("the band rival predicts NEGATIVE: a smaller settled edge means a tighter "
                       "claim and therefore a later arrival"),
        "answered": bool(p_sign is not None and p_sign < ALPHA and neg > pos),
        "rows": rows,
    }


def _binom(n, k):
    from math import comb
    return comb(n, k)


def uniformity(arms):
    """How much the settling speed actually varies across the arms at all."""
    areas = [a["settled_area"] for a in arms if a.get("settled_area") is not None]
    sessions = [a["sessions"] for a in arms if a.get("sessions") is not None]
    ratios = [a["resolution_ratio"] for a in arms if a.get("resolution_ratio") is not None]
    def span(v):
        return (max(v) - min(v)) if v else None
    def fold(v):
        return (max(v) / min(v)) if (v and min(v)) else None
    return {
        "arms": len(areas),
        "settled_area_min": min(areas) if areas else None,
        "settled_area_max": max(areas) if areas else None,
        "settled_area_span": span(areas),
        "settled_area_stdev": statistics.stdev(areas) if len(areas) > 1 else None,
        "sessions_min": min(sessions) if sessions else None,
        "sessions_max": max(sessions) if sessions else None,
        "sessions_fold": fold(sessions),
        "resolution_ratio_min": min(ratios) if ratios else None,
        "resolution_ratio_max": max(ratios) if ratios else None,
        "resolution_ratio_fold": fold(ratios),
        "reading": ("a flat entry means the draw requirement does not vary with the window at all, "
                    "so a per-window budget cannot buy anything a global floor does not"),
    }


def verdict_of(arms, length, band, seeded, crit):
    if not arms:
        return "no_windows_measured", "E260's windows and E259's edge tables do not overlap"
    if length.get("rho") is None or band.get("rho") is None:
        return "no_windows_measured", "a rival channel could not be evaluated on fewer than three arms"
    both = length["answered"] and band["answered"]
    if both:
        return ("arrival_is_both_channels",
                "both the window length and the band ratio clear p<%.2f on %d arms"
                % (ALPHA, length["n"]))
    if length["answered"]:
        return ("arrival_is_a_length_effect",
                "sessions clear p<%.2f (rho %+.3f) while the resolution ratio does not (p=%.3f)"
                % (ALPHA, length["rho"], band["p"]))
    if band["answered"]:
        return ("arrival_is_a_band_effect",
                "the resolution ratio clears p<%.2f (rho %+.3f) while sessions do not (p=%.3f)"
                % (ALPHA, band["rho"], length["p"]))
    why = ("neither the window length (rho %+.3f, p=%.3f) nor the resolution ratio (rho %+.3f, "
           "p=%.3f) clears p<%.2f on %d arms, and the %d-seed channel inside the arms does not "
           "carry the band rival either (median rho %s, %d of %d arms positive where the rival "
           "predicts negative, sign test p=%s)"
           % (length["rho"], length["p"], band["rho"], band["p"], ALPHA, length["n"],
              seeded.get("arms_published", 0),
              _fmt(seeded.get("rho_median")), seeded.get("arms_positive", 0),
              seeded.get("arms_published", 0), _fmt(seeded.get("sign_test_p_two_sided"))))
    if crit is not None:
        why += ("; the smallest |rho| this design could have called is %.3f, so an effect smaller "
                "than that is not excluded -- only one larger than it is" % crit)
    return "arrival_is_neither_channel", why


def _fmt(v, nd=3):
    return "n/a" if v is None else ("%+.*f" % (nd, v))


# ------------------------------------------------------------------ run
def run(save=True, outdir=None, calendar_path=None):
    outdir = outdir or OUTDIR
    a_face = source_arrival()
    w_face = source_width()
    if a_face is None or w_face is None:
        out = {"study": STUDY, "title": TITLE, "evidence_cutoff": CUTOFF,
               "generated": datetime.now().isoformat(timespec="seconds"),
               "verdict": "no_windows_measured",
               "verdict_reason": "E260's %s or E259's %s is absent; no arrival can be attributed"
                                 % (SRC_ARRIVAL, SRC_WIDTH),
               "arms": [], "channels": {}, "no_bill": NO_BILL}
        out["summary"] = _summary(out)
        if save:
            _write(out, outdir)
        return out

    cal = load_calendar(calendar_path)
    arms = arms_of(a_face, w_face, cal)
    length = channel(arms, "sessions")
    band = channel(arms, "resolution_ratio")
    seeded = per_seed_channel(arms)
    crit = critical_rho(len(arms))
    v, why = verdict_of(arms, length, band, seeded, crit)
    out = {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": a_face.get("evidence_cutoff") or CUTOFF,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "frozen_spec": {
            "design": ("read the per-seed edge tables E260 already published and test two rivals for "
                       "the draw count a window needs: its LENGTH (sessions) and its BAND (the "
                       "published band width relative to the settled-edge spread)"),
            "response": ("the settled share at each draw count below the top, averaged -- uncensored "
                         "and monotone in E260's arrival, where the arrival median itself is "
                         "right-censored at %d" % TOP),
            "reference_excluded": ("the top draw count is 1.0 by construction and is excluded from "
                                   "the area; the censored share is published beside it"),
            "settled_rule": "the edge at draw count d equals the same seed's edge at %d within %g"
                            % (TOP, TOL),
            "resolution_ratio": ("settled-edge spread (sample stdev over the %d seeds) divided by "
                                 "half the published band width -- the noise a draw must beat "
                                 "measured against the tolerance the row must resolve" % 40),
            "calendar": ("data/exchange_calendar.csv -- the official calendar, never the window's "
                         "own panel (E136)"),
            "permutation": {"budget": PERM_N, "seed": PERM_SEED, "alpha": ALPHA,
                            "two_sided": True},
            "sign_test": "exact two-sided binomial over the arms' per-seed rank correlations",
        },
        "source_faces": ["results/state_tilt/%s" % SRC_ARRIVAL,
                         "results/state_tilt/%s" % SRC_WIDTH],
        "windows_measured": sorted({a["cell"] for a in arms}),
        "arms": [{k: v for k, v in a.items() if k not in ("settled_edges", "arrival_per_seed")}
                 for a in arms],
        "channels": {"length": length, "band": band, "per_seed": seeded},
        "uniformity": uniformity(arms),
        "power": {
            "arms": len(arms),
            "critical_abs_rho_at_alpha": crit,
            "alpha": ALPHA,
            "note": ("exactly enumerated over all orderings of %d ranks; an effect smaller than "
                     "this is not excluded by this design" % len(arms)),
        },
        "reproducibility": {
            "arms_recomputing_e260_arrival": sum(1 for a in arms
                                                 if a["arrival_recomputed_matches_e260"]),
            "arms": len(arms),
        },
        "verdict": v,
        "verdict_reason": why,
        "no_bill": NO_BILL,
    }
    out["summary"] = _summary(out)
    if save:
        _write(out, outdir)
    return out


def _summary(face):
    arms = face.get("arms") or []
    ch = face.get("channels") or {}
    lg, bd, sd = ch.get("length") or {}, ch.get("band") or {}, ch.get("per_seed") or {}
    uni = face.get("uniformity") or {}
    return {
        "arms": len(arms),
        "windows": len(face.get("windows_measured") or []),
        "seeds": sum(a.get("n_seeds") or 0 for a in arms),
        "sessions_min": uni.get("sessions_min"),
        "sessions_max": uni.get("sessions_max"),
        "sessions_fold": uni.get("sessions_fold"),
        "resolution_ratio_fold": uni.get("resolution_ratio_fold"),
        "settled_area_min": uni.get("settled_area_min"),
        "settled_area_max": uni.get("settled_area_max"),
        "length_rho": lg.get("rho"),
        "length_p": lg.get("p"),
        "length_answered": lg.get("answered"),
        "band_rho": bd.get("rho"),
        "band_p": bd.get("p"),
        "band_answered": bd.get("answered"),
        "per_seed_rho_median": sd.get("rho_median"),
        "per_seed_arms_positive": sd.get("arms_positive"),
        "per_seed_arms_published": sd.get("arms_published"),
        "per_seed_sign_test_p": sd.get("sign_test_p_two_sided"),
        "per_seed_answered": sd.get("answered"),
        "critical_abs_rho": (face.get("power") or {}).get("critical_abs_rho_at_alpha"),
        "arms_recomputing_e260_arrival": ((face.get("reproducibility") or {})
                                          .get("arms_recomputing_e260_arrival")),
        "arrival_censored_share_median": (statistics.median(
            [a["arrival_censored_share"] for a in arms
             if a.get("arrival_censored_share") is not None]) if arms else None),
        "verdict": face.get("verdict"),
    }


def _write(face, outdir, tag=""):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "BANDARRIVALATE-%s%s.json" % (face.get("evidence_cutoff"), tag))
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    latest = os.path.join(outdir, "bandarrivalate_latest.json")
    with io.open(latest, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    return path


def verify(outdir=None, tag=""):
    """Re-derive the published face and report every field that does not come back."""
    outdir = outdir or OUTDIR
    try:
        got = load("BANDARRIVALATE-%s%s.json" % (CUTOFF, tag))
    except FileNotFoundError:
        return ["no published face at %s"
                % os.path.join(outdir, "BANDARRIVALATE-%s%s.json" % (CUTOFF, tag))]
    fresh = run(save=False)
    problems = []
    for key in ("verdict", "verdict_reason", "summary", "frozen_spec", "uniformity",
                "reproducibility", "power"):
        if got.get(key) != fresh.get(key):
            problems.append("%s does not re-derive" % key)
    pa = {(a.get("cell"), a.get("leg")): a for a in (got.get("arms") or [])}
    fa = {(a.get("cell"), a.get("leg")): a for a in (fresh.get("arms") or [])}
    if set(pa) != set(fa):
        problems.append("arm set does not re-derive")
    else:
        for k in pa:
            if pa[k] != fa[k]:
                problems.append("arm %s/%s does not re-derive" % k)
    ch_got = (got.get("channels") or {})
    ch_new = (fresh.get("channels") or {})
    for name in ("length", "band", "per_seed"):
        if ch_got.get(name) != ch_new.get(name):
            problems.append("channel %s does not re-derive" % name)
    return problems


# ------------------------------------------------------------------ selftest
def _leg(ok, name, detail=None):
    return {"leg": name, "ok": bool(ok), "detail": detail}


def _fixture_series(n=40, start=1.0, step=0.01, seed=7):
    rng = random.Random(seed)
    return [start + step * i + rng.uniform(-1e-9, 1e-9) for i in range(n)]


def selftest():
    legs = []

    # --- median-of-ties cannot fabricate a correlation
    legs.append(_leg(spearman([1, 2, 3, 4], [1, 2, 3, 4]) == 1.0,
                     "a perfectly increasing pair reads rho = 1"))
    legs.append(_leg(spearman([1, 2, 3, 4], [4, 3, 2, 1]) == -1.0,
                     "a perfectly decreasing pair reads rho = -1"))
    legs.append(_leg(spearman([1, 1, 1, 1], [1, 2, 3, 4]) is None,
                     "a constant column has no rank correlation and is published as None, not zero"))
    legs.append(_leg(ranks([5, 5, 7]) == [1.5, 1.5, 3.0],
                     "tied values take their average rank", ranks([5, 5, 7])))

    # --- the settled rule is E260's, and the reference point is 1.0 by construction
    top = [1.0, 2.0, 3.0]
    legs.append(_leg(settled_share([1.0, 2.0, 3.0], top)[0] == 1.0,
                     "the top draw count settles every seed against itself"))
    legs.append(_leg(settled_share([1.0 + 1e-13, 2.0, 3.0], top)[0] == 1.0,
                     "a difference inside the frozen tolerance counts as settled"))
    legs.append(_leg(abs(settled_share([1.0 + 1e-6, 2.0, 3.0], top)[0] - 2 / 3.0) < 1e-12,
                     "a difference outside the frozen tolerance is not settled"))
    legs.append(_leg(settled_share([None, None], [1.0, 2.0])[0] is None,
                     "a draw count with no comparable pair publishes None, not zero"))

    # --- the area must exclude its own reference point (a constant added to every arm)
    ten = list(range(10))
    top_ten = [1.0 + 0.01 * i for i in ten]
    by_draws = {"60": {"self": [9.0] * 10}, "120": {"self": list(top_ten)},
                "200": {"self": list(top_ten)}, "480": {"self": list(top_ten)},
                "960": {"self": list(top_ten)}, "1920": {"self": list(top_ten)}}
    rec = arm_record("fx", "self", {"by_draws": by_draws, "first": "2020-01-01",
                                    "last": "2020-01-31"}, {}, {}, None)
    legs.append(_leg(rec["settled_area"] == 0.8,
                     "the area averages the five counts below the top, not the six including it",
                     rec["settled_area"]))
    legs.append(_leg(rec["curve"]["1920"]["share_settled"] == 1.0,
                     "the reference point is still published in the curve"))

    # --- arrival recomputed from the table is E260's rule, and a changed table is caught
    legs.append(_leg(arrival_of(by_draws, "self") == [120] * 10,
                     "the first count that matches the top edge is the arrival", None))
    moved = json.loads(json.dumps(by_draws))
    for d in ("60", "120", "200", "480", "960"):
        moved[d]["self"][-1] = top_ten[-1] + 0.5
    legs.append(_leg(arrival_of(moved, "self") == [120] * 9 + [1920],
                     "a seed that is still moving at 960 arrives at the top"))
    legs.append(_leg(arrival_of({"1920": {"self": [None]}}, "self") == [None],
                     "a seed with no edge at all publishes no arrival"))

    # --- the band rival's ratio is spread over HALF the width, and a missing band is None
    band = band_of({"rows": [{"cell": "c", "row": "self", "band_lo": -0.3, "band_hi": 0.1,
                              "band_draws": 200, "b": -0.2}]})
    legs.append(_leg(abs(band[("c", "self")]["band_width"] - 0.4) < 1e-12,
                     "the band width is hi minus lo", band[("c", "self")]["band_width"]))
    noband = band_of({"rows": [{"cell": "c", "row": "self", "band_lo": None, "band_hi": None}]})
    legs.append(_leg(noband == {}, "a row with no band publishes no width"))
    legs.append(_leg(band_of({"rows": [{"cell": "c", "row": "star_lag1_residual",
                                        "band_lo": -0.1, "band_hi": 0.1}]}) == {},
                     "a residual row is not a leg and is not given one"))

    # --- sessions come from the calendar, and an absent calendar is None (never zero)
    cal = ["2020-01-01", "2020-01-02", "2020-01-03"]
    legs.append(_leg(sessions_between(cal, "2020-01-01", "2020-01-02") == 2,
                     "a closed window counts both ends", None))
    legs.append(_leg(sessions_between(None, "2020-01-01", "2020-01-02") is None,
                     "an absent calendar publishes None rather than a zero session count"))

    # --- the calendar loader picks dates and ignores a header
    tmp = os.path.join(HERE, "_tmp_e263_cal.csv")
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("date\n2020-01-02\n2020-01-01\nnot-a-date\n")
    try:
        got = load_calendar(tmp)
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass
    legs.append(_leg(got == ["2020-01-01", "2020-01-02"],
                     "the loader keeps ISO dates, sorts them and drops the header", got))

    # --- permutation test: an exact permutation of a perfect rank order is never as extreme
    rho, p = spearman_perm([1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6], n=200, seed=1)
    legs.append(_leg(rho == 1.0 and p is not None and p < 0.05,
                     "a perfect monotone pair is significant on 6 points", [rho, p]))
    rho2, p2 = spearman_perm([1, 2, 3, 4, 5, 6], [6, 5, 4, 3, 2, 1], n=200, seed=1)
    legs.append(_leg(rho2 == -1.0 and p2 is not None and p2 < 0.05,
                     "a perfect reversed pair is significant too (two-sided)", [rho2, p2]))

    # --- the frozen resample seed makes the p reproducible run to run
    pa = spearman_perm([3, 1, 4, 1, 5, 9, 2, 6], [2, 7, 1, 8, 2, 8, 1, 8])
    pb = spearman_perm([3, 1, 4, 1, 5, 9, 2, 6], [2, 7, 1, 8, 2, 8, 1, 8])
    legs.append(_leg(pa == pb, "the permutation p is identical on a rerun", pa))

    # --- the power statement is a number, and it is stricter on fewer arms
    c8 = critical_rho(8)
    c6 = critical_rho(6)
    legs.append(_leg(c8 is not None and 0.5 < c8 <= 1.0,
                     "eight arms can call an effect well inside |rho| = 1", c8))
    legs.append(_leg(c6 is not None and c6 > c8,
                     "fewer arms need a larger |rho| to be called", [c6, c8]))
    legs.append(_leg(critical_rho(20) is None,
                     "the enumeration declines to table a design it did not enumerate"))

    # --- sign test: all-negative is significant, a split is not
    neg_arm = {"leg": "self",
               "arrival_per_seed": [60, 120, 200, 480, 960, 1920, 60, 120],
               "settled_edges": [-0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.35, -0.3]}
    pos_arm = {"leg": "self",
               "arrival_per_seed": [60, 120, 200, 480, 960, 1920, 60, 120],
               "settled_edges": [-0.3, -0.35, -0.4, -0.5, -0.6, -0.7, -0.8, -0.9]}
    six = per_seed_channel([dict(neg_arm, cell="c%d" % i) for i in range(6)])
    legs.append(_leg(six["arms_negative"] == 6 and six["answered"] is True,
                     "six arms that all run negative clear the sign test", six))
    two = per_seed_channel([dict(neg_arm, cell="c1"), dict(neg_arm, cell="c2")])
    legs.append(_leg(two["arms_negative"] == 2 and two["answered"] is False,
                     "two arms cannot clear the sign test however one-sided they look",
                     two["sign_test_p_two_sided"]))
    mixed = per_seed_channel([dict(neg_arm, cell="c1"), dict(pos_arm, cell="c2")])
    legs.append(_leg(mixed["arms_positive"] == 1 and mixed["arms_negative"] == 1
                     and mixed["answered"] is False,
                     "a split pair of arms answers nothing", mixed["sign_test_p_two_sided"]))

    # --- a mechanism-happened precondition: the verdict machinery must be fed real variation
    # (r1261: assuming the mechanism ran is how a whole face passes while nothing moves)
    flat = [{"settled_area": 0.5, "sessions": 100, "resolution_ratio": 0.2},
            {"settled_area": 0.5, "sessions": 200, "resolution_ratio": 0.3},
            {"settled_area": 0.5, "sessions": 300, "resolution_ratio": 0.4}]
    ch_len = channel(flat, "sessions")
    legs.append(_leg(ch_len["rho"] is None and ch_len["answered"] is False,
                     "a response column with no variation is not reported as an answered channel",
                     ch_len))
    uni = uniformity(flat)
    legs.append(_leg(uni["settled_area_span"] == 0.0,
                     "a flat response publishes a zero span rather than a small nonzero one", uni))
    legs.append(_leg(uni["sessions_fold"] == 3.0,
                     "the fold is max/min, so a 3x covariate reads 3", uni["sessions_fold"]))

    empty_v, empty_why = verdict_of([], {}, {}, {}, None)
    legs.append(_leg(empty_v == "no_windows_measured" and "do not overlap" in empty_why,
                     "no arms at all is named, not zeroed", empty_v))

    # --- verdict selection on fixtures
    yes = {"n": 8, "rho": -0.9, "p": 0.001, "answered": True}
    no = {"n": 8, "rho": -0.1, "p": 0.9, "answered": False}
    arms_fx = [{"settled_area": 0.3, "sessions": 400, "resolution_ratio": 0.15,
                "arrival_censored_share": 0.5}]
    v1, _ = verdict_of(arms_fx, yes, no, {}, 0.83)
    v2, _ = verdict_of(arms_fx, no, yes, {}, 0.83)
    v3, _ = verdict_of(arms_fx, yes, yes, {}, 0.83)
    v4, why4 = verdict_of(arms_fx, no, no, {"arms_positive": 6, "arms_published": 8,
                                            "rho_median": 0.11, "sign_test_p_two_sided": 0.29}, 0.83)
    legs.append(_leg(v1 == "arrival_is_a_length_effect", "a length-only fixture names the length", v1))
    legs.append(_leg(v2 == "arrival_is_a_band_effect", "a band-only fixture names the band", v2))
    legs.append(_leg(v3 == "arrival_is_both_channels", "both-clearing fixture names both", v3))
    legs.append(_leg(v4 == "arrival_is_neither_channel" and "smallest |rho|" in why4,
                     "a neither fixture names the power limit it was tested under", v4))

    # --- the summary carries the verdict and the arms it came from
    face_fx = {"arms": arms_fx, "channels": {"length": no, "band": no,
                                            "per_seed": {"rho_median": 0.1, "arms_positive": 1,
                                                         "arms_published": 1,
                                                         "sign_test_p_two_sided": 1.0}},
               "uniformity": {"sessions_min": 400, "sessions_max": 400, "sessions_fold": 1.0,
                              "resolution_ratio_fold": 1.0, "settled_area_min": 0.3,
                              "settled_area_max": 0.3},
               "power": {"critical_abs_rho_at_alpha": 0.83},
               "reproducibility": {"arms_recomputing_e260_arrival": 1},
               "windows_measured": ["fx"], "verdict": v4}
    sm = _summary(face_fx)
    legs.append(_leg(sm["verdict"] == v4 and sm["arms"] == 1 and sm["critical_abs_rho"] == 0.83,
                     "the summary carries the verdict, the arm count and the power line", sm))
    # a field that names a count must publish a count: `(A or {}).get(k)` silently returns the whole
    # dict when the left side is truthy, and the first draft of this face published exactly that
    legs.append(_leg(isinstance(sm["arms_recomputing_e260_arrival"], int)
                     and sm["arms_recomputing_e260_arrival"] == 1,
                     "the reproduction count is an int, not the block it was read from",
                     sm["arms_recomputing_e260_arrival"]))

    ok = all(r["ok"] for r in legs)
    return {"ok": ok, "legs": legs, "passed": sum(1 for r in legs if r["ok"]), "total": len(legs)}


# ------------------------------------------------------------------ cli
def main(argv=None):
    ap = argparse.ArgumentParser(description=TITLE)
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "selftest", "verify", "summarize"])
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--tag", default="")
    ap.add_argument("--calendar", default=None)
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        res = selftest()
        for r in res["legs"]:
            print("%-4s %s" % ("ok" if r["ok"] else "FAIL", r["leg"]))
        print("selftest %d/%d" % (res["passed"], res["total"]))
        return 0 if res["ok"] else 1
    if args.cmd == "verify":
        problems = verify(outdir=args.outdir, tag=args.tag)
        for p in problems:
            print("PROBLEM %s" % p)
        print("verify %s (%d problems)" % ("OK" if not problems else "FAILED", len(problems)))
        return 0 if not problems else 1
    if args.cmd == "summarize":
        face = run(save=False, calendar_path=args.calendar)
        print(json.dumps(face.get("summary"), ensure_ascii=False, indent=1, sort_keys=True))
        print(face.get("verdict_reason"))
        return 0
    face = run(outdir=args.outdir, calendar_path=args.calendar)
    print(json.dumps(face.get("summary"), ensure_ascii=False, indent=1, sort_keys=True))
    print(face.get("verdict"))
    print(face.get("verdict_reason"))
    return 0


if __name__ == "__main__":
    sys.exit(main())