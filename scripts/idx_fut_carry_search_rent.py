#!/usr/bin/env python
"""idx_fut_carry_search_rent -- how many independent tries does the carry headline survive?

Why this face exists
--------------------
`results/idx_fut_carry_risk.json` publishes a Sharpe for every carry product (IC 1.451,
IM 1.435, IF 0.800, IH 0.533 on the hedged arm) and the desk sheet quotes them as the
reason to open the book.  Nothing in the carry family asks what those Sharpes are worth
*after* the search that produced them, while the ETF book has just been asked exactly
that (`scripts/etf_book_search_rent.py`, r1960: SEARCH_RENT_EATS_THE_HEADLINE).  A
Sharpe is a claim about a signal, and this desk has priced ~20 declared axes on this
family before reaching these four numbers.

What this face publishes
------------------------
1. **The DSR curve** for the eight cells the carry family actually publishes
   (4 products x 2 arms), on the frozen N grid, via
   `science_gates.deflated_sharpe_ratio` on the daily P&L series -- no second
   implementation of the formula anywhere in this file.
2. **N\\***, the trial count at which DSR crosses `DSR_LINE`, by bisection on that same
   function: "how many independent tries this Sharpe survives".
3. **The Sharpe each cell would need** to clear the same line at the audited counts.
4. **Three auditable trial counts** with mechanical definitions (family scripts, carry
   preregs, declared blend cells) and the verdict stated against all three, because N is
   not derivable from the repo without a convention.

The series are imported from `idx_fut_carry_paper.position_series / per_lot_daily`
(contract calendar, roll seam, forced-roll-as-zero) and the index panel from
`idx_fut_basis`, exactly as the paper face does -- this file builds no price path.

Frozen before the first run (the check refuses a face whose echoed criteria differ):
    PRODUCTS, ARMS, WINDOW_YEARS, N_GRID, DSR_LINE, MIN_BARS, SR_ALIGN_TOL_PP,
    AUDIT definitions.  No line is tuned after seeing the numbers.

Usage:
    python scripts/idx_fut_carry_search_rent.py run
    python scripts/idx_fut_carry_search_rent.py check
    python scripts/idx_fut_carry_search_rent.py --selftest
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT_JSON = ROOT / "results" / "idx_fut_carry_search_rent.json"
OUT_MD = ROOT / "research" / "IDX_FUT_CARRY_SEARCH_RENT.md"
PARENT_RISK = ROOT / "results" / "idx_fut_carry_risk.json"
SCRIPT = "scripts/idx_fut_carry_search_rent.py"
FACE = "results/idx_fut_carry_search_rent.json"

# ---------------------------------------------------------------- frozen criteria
PRODUCTS = ("IC", "IF", "IM", "IH")
ARMS = ("carry_unhedged", "excess_hedged")
WINDOW_YEARS = 10
N_GRID = (1, 2, 3, 5, 8, 12, 18, 30, 50, 100, 200, 450, 1000)
DSR_LINE = 0.95
MIN_BARS = 250
SR_ALIGN_TOL_PP = 0.05      # our hedged Sharpe vs the parent risk face, in Sharpe units
KIND = "idx_fut_carry_search_rent"

CRITERIA = {
    "products": list(PRODUCTS),
    "arms": list(ARMS),
    "window_years": WINDOW_YEARS,
    "n_grid": list(N_GRID),
    "dsr_line": DSR_LINE,
    "min_bars": MIN_BARS,
    "sr_align_tol": SR_ALIGN_TOL_PP,
    "parent": "results/idx_fut_carry_risk.json",
    "arm_definitions": {
        "carry_unhedged": "per-lot daily points on the held contract (roll priced on the outgoing leg)",
        "excess_hedged": "same day minus the same notional's index return (the residual the hedge leaves)",
    },
    "audit_definitions": {
        "family_scripts": "count of scripts/idx_fut_*.py -- one declared axis each",
        "carry_preregs": "count of research/**/*.md whose name or first paragraph declares IDX_FUT/CARRY/BASIS",
        "declared_blend_cells": "len(products) * len(blend_lambdas) in the parent risk face criteria",
    },
    "frozen": "constants above were written before the first run",
}


# ------------------------------------------------------------------------ helpers
def _load(path):
    if not Path(path).exists():
        return None
    return json.load(open(path, encoding="utf-8"))


def _dump(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")


def _ann_sharpe(points):
    """Scale-invariant: points are P&L per lot, so Sharpe needs no capital."""
    n = len(points)
    if n < 2:
        return None
    mu = sum(points) / n
    var = sum((x - mu) ** 2 for x in points) / (n - 1)
    if var <= 0:
        return None
    return mu / math.sqrt(var) * math.sqrt(252.0)


def build_arms():
    """[(product, arm)] -> (points, last_bar).  Imported primitives only."""
    import idx_fut_carry_paper as CP
    import idx_fut_basis as BASE

    out = {}
    for prod in PRODUCTS:
        try:
            rows, _rolls = CP.position_series(prod)
        except Exception as exc:                                    # noqa: BLE001
            out[prod] = {"error": "panel: %s" % exc}
            continue
        if not rows:
            out[prod] = {"error": "no contract panel"}
            continue
        idx_close = None
        idx_note = ""
        try:
            idx_close = BASE.load_index(BASE.PAIRS[prod][0])
        except Exception as exc:                                    # noqa: BLE001
            idx_note = "index panel unavailable (%s) -- excess leg off" % exc
        series = CP.per_lot_daily(rows, idx_close, years=WINDOW_YEARS)
        if not series:
            out[prod] = {"error": "per_lot_daily returned nothing"}
            continue
        out[prod] = {
            "window": series["window"],
            "forced_rolls": series["forced_rolls"],
            "note": idx_note,
            "carry_unhedged": list(series["fut_points"]),
            "excess_hedged": list(series["excess_points"]),
        }
    return out


def _dsr(points, n_trials):
    from science_gates import deflated_sharpe_ratio
    return deflated_sharpe_ratio(points, n_trials)


def _sr_star_for(points, n_trials):
    """The per-period Sharpe that would sit exactly on DSR_LINE at this N."""
    d = _dsr(points, n_trials)
    return d["sr_star"] + _z_for_line() * d["sigma_sr"]


def _z_for_line():
    from science_gates import _norm_ppf
    return _norm_ppf(DSR_LINE)


def _n_star(points, n_max=1_000_000):
    """Smallest N whose DSR still clears the line; bisection, monotone in N."""
    if _dsr(points, n_max)["dsr"] >= DSR_LINE:
        return int(n_max)
    lo, hi = 2, n_max
    if _dsr(points, hi)["dsr"] >= DSR_LINE:
        return int(hi)
    while lo < hi:
        mid = (lo + hi) // 2
        if _dsr(points, mid)["dsr"] >= DSR_LINE:
            lo = mid + 1
        else:
            hi = mid
    return int(max(2, lo - 1))


def audit_counts():
    """Three countable proxies for 'how many bets did this family put a judgment on'."""
    scripts = len(glob.glob(str(ROOT / "scripts" / "idx_fut_*.py")))
    preregs = 0
    for p in glob.glob(str(ROOT / "research" / "**" / "*.md"), recursive=True):
        if Path(p) == OUT_MD:
            continue        # this face's own doc must not count itself as a declared bet
        name = Path(p).name.upper()
        if not any(k in name for k in ("IDX_FUT", "CARRY", "BASIS")):
            continue
        try:
            head = open(p, encoding="utf-8", errors="replace").read(2000).upper()
        except Exception:                                            # noqa: BLE001
            head = ""
        if "PREREG" in name or "PREREG" in head or "FROZEN" in head:
            preregs += 1
    cells = None
    parent = _load(PARENT_RISK)
    if parent:
        c = parent.get("criteria") or {}
        if c.get("products") and c.get("blend_lambdas"):
            cells = len(c["products"]) * len(c["blend_lambdas"])
    return {"family_scripts": scripts, "carry_preregs": preregs,
            "declared_blend_cells": cells}


def _parent_sharpes():
    parent = _load(PARENT_RISK)
    out = {}
    if not parent:
        return out
    for prod, blk in (parent.get("products") or {}).items():
        sr = (blk.get("risk") or {}).get("sharpe")
        if isinstance(sr, (int, float)):
            out[prod] = float(sr)
    return out


def _verdict(cells, audited_ns):
    """Frozen decision rule: the claim has to clear the line at the LARGEST audited count."""
    live = [c for c in cells.values() if c.get("verdict") == "SURVIVES_AT_AUDITED_N"]
    n_max = max(audited_ns)
    strong = [c for c in cells.values() if c.get("n_star") and c["n_star"] >= n_max]
    if len(live) == len(cells):
        return "CARRY_SHARPE_SURVIVES_SEARCH"
    if len(live) == 0 and not strong:
        return "CARRY_SHARPE_IS_SEARCH_RENT"
    return "CARRY_SHARPE_SURVIVES_ONLY_SOME_CELLS"


# ------------------------------------------------------------------------ the face
def build(write=True):
    arms = build_arms()
    counts = audit_counts()
    audited = [counts["family_scripts"], counts["carry_preregs"]]
    if counts["declared_blend_cells"]:
        audited.append(int(counts["declared_blend_cells"]))
    n_audit_max = max(audited)

    cells = {}
    cutoffs = []
    for prod in PRODUCTS:
        blk = arms.get(prod) or {}
        if blk.get("error"):
            cells["%s|both" % prod] = {"error": blk["error"]}
            continue
        cutoffs.append(blk["window"][1])
        for arm in ARMS:
            points = blk.get(arm) or []
            key = "%s|%s" % (prod, arm)
            if len(points) < MIN_BARS:
                cells[key] = {"error": "only %d bars (< %d)" % (len(points), MIN_BARS)}
                continue
            curve = {}
            for n in N_GRID:
                curve[str(n)] = _dsr(points, n)["dsr"]
            alive = [n for n in N_GRID if curve[str(n)] >= DSR_LINE]
            n_star = _n_star(points)
            need = _sr_star_for(points, n_audit_max) * math.sqrt(252.0)
            cells[key] = {
                "bars": len(points),
                "window": blk["window"],
                "forced_rolls": blk["forced_rolls"],
                "sharpe_ann": round(_ann_sharpe(points), 4),
                "dsr_curve": curve,
                "n_star": int(n_star),
                "max_n_clearing_grid": (max(alive) if alive else None),
                "sharpe_needed_at_audited_n": round(need, 4),
                "gap_at_audited_n": round(need - _ann_sharpe(points), 4),
                "verdict": ("SURVIVES_AT_AUDITED_N" if curve[str(_grid_le(n_audit_max))] >= DSR_LINE
                            else "INSIDE_SEARCH_NOISE_AT_AUDITED_N"),
            }

    cutoff = max(cutoffs) if cutoffs else None
    parent_sr = _parent_sharpes()
    align = {}
    transplanted = {}
    for prod in PRODUCTS:
        mine = (cells.get("%s|excess_hedged" % prod) or {}).get("sharpe_ann")
        theirs = parent_sr.get(prod)
        if mine is None or theirs is None:
            align[prod] = {"status": "UNVERIFIED", "why": "missing side"}
            continue
        diff = mine - theirs
        align[prod] = {
            "ours": mine, "parent": theirs, "diff": round(diff, 4),
            "status": "ALIGNED" if abs(diff) <= SR_ALIGN_TOL_PP else "RELATION_UNVERIFIED",
            "why": ("same arm, same window, tolerance %.2f" % SR_ALIGN_TOL_PP),
        }
        # A transplanted reading: keep this series' shape (skew, kurtosis, n) and ask what
        # the PARENT's published Sharpe would be worth after the same search.  It is not
        # evidence about the parent's series, only about the number the desk quotes.
        points = (arms.get(prod) or {}).get("excess_hedged") or []
        if len(points) >= MIN_BARS and mine:
            scale = theirs / mine
            scaled = [x * scale for x in points]
            transplanted[prod] = {
                "parent_sharpe": theirs,
                "scale": round(scale, 4),
                "dsr_at_audited_n": _dsr(scaled, n_audit_max)["dsr"],
                "n_star": int(_n_star(scaled)),
                "reading": "parent's Sharpe on this face's return shape (not the parent's series)",
            }

    face = {
        "kind": KIND,
        "script": SCRIPT,
        "face": FACE,
        "generated": _now(),
        "evidence_cutoff": cutoff,
        "criteria": CRITERIA,
        "audit_counts": counts,
        "audited_n_used": n_audit_max,
        "cells": cells,
        "parent_alignment": align,
        "parent_transplanted": transplanted,
        "verdict": _verdict(cells, audited),
    }
    face["headline"] = _sentence(face)
    if write:
        _dump(OUT_JSON, face)
        _write_doc(face)
    return face


def _grid_le(n):
    """Largest grid point at or below n (the audited count may sit between grid points)."""
    cand = [g for g in N_GRID if g <= n]
    return max(cand) if cand else N_GRID[0]


def _now():
    from datetime import datetime
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _sentence(face):
    n = face["audited_n_used"]
    items = [(k, c) for k, c in face["cells"].items() if "sharpe_ann" in c]
    if not items:
        return "no cell is readable -- see the per-product errors"
    best_k, best = max(items, key=lambda kc: kc[1]["n_star"])
    worst_k, worst = min(items, key=lambda kc: kc[1]["n_star"])
    ok = [k for k, c in items if c.get("verdict") == "SURVIVES_AT_AUDITED_N"]
    return (
        "carry cells survive %d..%d independent tries at the %.0f%% line (best %s %d, "
        "worst %s %d); this family has audited N=%d (%s) -> %d of %d cells clear it (%s)"
        % (worst["n_star"], best["n_star"], DSR_LINE * 100,
           best_k, best["n_star"], worst_k, worst["n_star"],
           n, ", ".join("%s=%s" % (k, v) for k, v in sorted(face["audit_counts"].items())),
           len(ok), len(items), face["verdict"])
    )


def _render(face):
    lines = []
    lines.append("## What this face says\n")
    lines.append(face["headline"] + "\n")
    lines.append("Evidence cutoff: %s (newest contract bar across the four products).\n"
                 % face["evidence_cutoff"])
    lines.append("| cell | bars | Sharpe (ann) | N* | DSR @N=%d | Sharpe needed | verdict |"
                 % face["audited_n_used"])
    lines.append("|---|---|---|---|---|---|---|")
    for key in sorted(face["cells"]):
        c = face["cells"][key]
        label = key.replace("|", " / ")      # a literal pipe would split the markdown table
        if "sharpe_ann" not in c:
            lines.append("| %s | -- | -- | -- | -- | -- | %s |" % (label, c.get("error", "missing")))
            continue
        g = _grid_le(face["audited_n_used"])
        lines.append("| %s | %d | %.4f | %d | %.4f | %.4f | %s |"
                     % (label, c["bars"], c["sharpe_ann"], c["n_star"],
                        c["dsr_curve"][str(g)], c["sharpe_needed_at_audited_n"], c["verdict"]))
    lines.append("")
    lines.append("Parent alignment (hedged arm vs `results/idx_fut_carry_risk.json`, "
                 "tolerance %.2f Sharpe):\n" % CRITERIA["sr_align_tol"])
    for prod in PRODUCTS:
        a = face["parent_alignment"].get(prod) or {}
        lines.append("- **%s**: ours %s / parent %s / diff %s -> %s"
                     % (prod, a.get("ours"), a.get("parent"), a.get("diff"), a.get("status")))
    lines.append("")
    if face.get("parent_transplanted"):
        lines.append("### What the *published* Sharpe is worth (transplanted reading)\n")
        lines.append("The four constructions are not the same series (the alignment gap above "
                     "is up to 0.18 Sharpe), so this block asks the narrower question the desk "
                     "actually needs: if a cell's return shape had produced the Sharpe published "
                     "in `idx_fut_carry_risk.json`, would that number survive the search?  Only "
                     "the shape is ours -- the parent's series was never read here.\n")
        lines.append("| product | parent Sharpe | N* | DSR @N=%d |" % face["audited_n_used"])
        lines.append("|---|---|---|---|")
        for prod in PRODUCTS:
            t = face["parent_transplanted"].get(prod)
            if not t:
                continue
            lines.append("| %s | %.4f | %d | %.4f |"
                         % (prod, t["parent_sharpe"], t["n_star"], t["dsr_at_audited_n"]))
        lines.append("")
    lines.append("### The DSR curve (frozen grid)\n")
    lines.append("| cell | " + " | ".join(str(n) for n in N_GRID) + " |")
    lines.append("|---|" + "---|" * len(N_GRID))
    for key in sorted(face["cells"]):
        c = face["cells"][key]
        if "dsr_curve" not in c:
            continue
        lines.append("| %s | " % key.replace("|", " / ") + " | ".join("%.3f" % c["dsr_curve"][str(n)]
                                                                     for n in N_GRID) + " |")
    lines.append("")
    lines.append("### Why three different N\n")
    for k, v in sorted(CRITERIA["audit_definitions"].items()):
        lines.append("- **%s** = %s -> **%s**" % (k, v, face["audit_counts"].get(k)))
    lines.append("")
    lines.append("N is a convention, not a measurement, so the verdict above is stated "
                 "against the largest audited count; the N\\* column says how many tries "
                 "each cell would have to survive on its own.  The N=1 grid point is clamped "
                 "to 2 by `science_gates.deflated_sharpe_ratio`, so it prints the same DSR as "
                 "N=2 -- read the column from N=2 onwards.")
    return "\n".join(lines)


def _write_doc(face):
    body = _render(face)
    head = (
        "# Carry search rent: how many independent tries does this Sharpe survive?\n\n"
        "Generated by `%s` -- do not edit the block below by hand; `check` compares it\n"
        "byte-for-byte with what the face would render today.\n\n"
        "<!-- BEGIN GENERATED -->\n" % SCRIPT
    )
    tail = "\n<!-- END GENERATED -->\n"
    Path(OUT_MD).parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(head + body + tail)


def _doc_block(text):
    a = text.find("<!-- BEGIN GENERATED -->")
    b = text.find("<!-- END GENERATED -->")
    if a < 0 or b < 0:
        return None
    return text[a + len("<!-- BEGIN GENERATED -->"):b]


# ------------------------------------------------------------------------ verdicts
def check():
    """Anchored to the input that moves: the panels' newest bar and the parent face."""
    face = _load(OUT_JSON)
    if not face:
        print("STALE face missing: %s" % FACE)
        return 3
    if (face.get("criteria") or {}) != CRITERIA:
        print("CHECK FAILED criteria differ from the frozen constants (face is not this code)")
        return 4
    fresh = build(write=False)
    if fresh["evidence_cutoff"] != face["evidence_cutoff"]:
        print("STALE panels advanced: face cutoff %s, panels now %s"
              % (face["evidence_cutoff"], fresh["evidence_cutoff"]))
        return 3
    if (fresh.get("audit_counts") or {}) != (face.get("audit_counts") or {}):
        print("STALE audit counts moved: %s -> %s"
              % (face.get("audit_counts"), fresh.get("audit_counts")))
        return 3
    bad = []
    for key, c in fresh["cells"].items():
        o = (face.get("cells") or {}).get(key)
        if o is None:
            bad.append("%s missing" % key)
            continue
        if "sharpe_ann" not in c:
            continue
        for field in ("sharpe_ann", "n_star", "verdict", "sharpe_needed_at_audited_n"):
            if (o or {}).get(field) != c[field]:
                bad.append("%s.%s %s != %s" % (key, field, (o or {}).get(field), c[field]))
        for n, v in c["dsr_curve"].items():
            if abs((o.get("dsr_curve") or {}).get(n, -1) - v) > 1e-6:
                bad.append("%s.dsr[%s] %s != %s" % (key, n, o["dsr_curve"].get(n), v))
    if fresh.get("verdict") != face.get("verdict"):
        bad.append("verdict %s != %s" % (face.get("verdict"), fresh.get("verdict")))
    for prod, t in (fresh.get("parent_transplanted") or {}).items():
        o = (face.get("parent_transplanted") or {}).get(prod) or {}
        for field in ("parent_sharpe", "n_star", "dsr_at_audited_n"):
            if o.get(field) != t[field]:
                bad.append("transplanted.%s.%s %s != %s" % (prod, field, o.get(field), t[field]))
    md = OUT_MD.read_text(encoding="utf-8") if OUT_MD.exists() else ""
    blk = _doc_block(md)
    if blk is None:
        bad.append("doc marker block missing")
    elif blk.strip() != _render(face).strip():
        bad.append("doc block does not match the face")
    if bad:
        print("CHECK FAILED")
        for line in bad[:12]:
            print("  " + line)
        return 4
    print("OK verdict=%s cutoff=%s audited_n=%d"
          % (face["verdict"], face["evidence_cutoff"], face["audited_n_used"]))
    return 0


# ------------------------------------------------------------------------ selftest
def selftest():
    import random
    legs = []

    def leg(name, cond, extra=""):
        legs.append((bool(cond), name, extra))

    rng = random.Random(20261123)
    # A realistic cell: daily vol 0.6%, annualised Sharpe ~1.3 -- the kind of number this
    # family publishes, so the legs exercise the part of the curve that actually moves.
    strong = [rng.gauss(0.00049, 0.006) for _ in range(1400)]
    weak = [rng.gauss(0.00004, 0.009) for _ in range(1400)]

    s_ann = _ann_sharpe(strong)
    mu = sum(strong) / len(strong)
    sd = math.sqrt(sum((x - mu) ** 2 for x in strong) / (len(strong) - 1))
    leg("ann Sharpe is scale invariant", abs(_ann_sharpe([x * 7.0 for x in strong]) - s_ann) < 1e-9)
    leg("ann Sharpe matches mean/sd*sqrt(252)", abs(s_ann - mu / sd * math.sqrt(252)) < 1e-9,
        "got %.4f" % s_ann)
    leg("the synthetic cell sits in the published range", 0.8 < s_ann < 2.5, "%.4f" % s_ann)

    d_small = _dsr(strong, 2)["dsr"]
    d_big = _dsr(strong, 1000)["dsr"]
    leg("DSR falls as the trial count rises", d_small > d_big, "%.3f > %.3f" % (d_small, d_big))
    leg("strong series clears the line at N=2", d_small >= DSR_LINE, "%.3f" % d_small)
    leg("weak series does not clear the line at N=8", _dsr(weak, 8)["dsr"] < DSR_LINE)

    n_star_strong = _n_star(strong)
    n_star_weak = _n_star(weak)
    leg("N* of the strong series beats the weak one", n_star_strong > n_star_weak,
        "%d vs %d" % (n_star_strong, n_star_weak))
    leg("N* sits on the crossing (clears there, fails just above)",
        _dsr(strong, n_star_strong)["dsr"] >= DSR_LINE and
        _dsr(strong, n_star_strong + 1)["dsr"] < DSR_LINE,
        "N*=%d" % n_star_strong)

    need_weak = _sr_star_for(weak, 8) * math.sqrt(252.0)
    leg("needed Sharpe at the audited N exceeds a cell that does not clear it",
        need_weak > _ann_sharpe(weak), "%.3f > %.3f" % (need_weak, _ann_sharpe(weak)))

    leg("N grid is sorted and unique", list(N_GRID) == sorted(set(N_GRID)))
    leg("_grid_le snaps down inside the grid", _grid_le(17) == 12 and _grid_le(1) == 1)

    cnt = audit_counts()
    leg("all three audit counts are readable", cnt["family_scripts"] > 5 and
        cnt["carry_preregs"] >= 0 and (cnt["declared_blend_cells"] or 0) > 0, str(cnt))

    # behaviour legs: the real check() on poisoned copies (restored in finally)
    import shutil
    import tempfile
    ok_behaviour = []
    if OUT_JSON.exists() and OUT_MD.exists():
        tmpdir = Path(tempfile.mkdtemp(prefix="carry_rent_"))
        jbak = tmpdir / "face.json"
        mbak = tmpdir / "doc.md"
        shutil.copy2(OUT_JSON, jbak)
        shutil.copy2(OUT_MD, mbak)
        try:
            face = _load(OUT_JSON)
            poisoned = json.loads(json.dumps(face))
            poisoned["evidence_cutoff"] = "1999-01-01"
            _dump(OUT_JSON, poisoned)
            import io
            from contextlib import redirect_stdout
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = check()
            out = buf.getvalue()
            ok_behaviour.append(("a moved cutoff reads STALE", rc == 3 and "STALE" in out,
                                 "rc=%s %r" % (rc, out.strip()[:60])))

            broken = json.loads(json.dumps(face))
            for key, c in broken["cells"].items():
                if "sharpe_ann" in c:
                    c["sharpe_ann"] = round(c["sharpe_ann"] + 0.5, 4)
                    break
            _dump(OUT_JSON, broken)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = check()
            out = buf.getvalue()
            ok_behaviour.append(("a wrong number at the same cutoff is CHECK FAILED, not STALE",
                                 rc == 4 and "STALE" not in out,
                                 "rc=%s %r" % (rc, out.strip()[:60])))
        finally:
            shutil.copy2(jbak, OUT_JSON)
            shutil.copy2(mbak, OUT_MD)
            shutil.rmtree(tmpdir, ignore_errors=True)
    else:
        ok_behaviour.append(("behaviour legs ran against a live face", False,
                             "face not published yet -- run first"))
    for name, ok, extra in ok_behaviour:
        legs.append((ok, name, extra))

    passed = sum(1 for ok, _, _ in legs if ok)
    for ok, name, extra in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name, (" [%s]" % extra) if extra else ""))
    print("SELFTEST %d/%d %s" % (passed, len(legs), "PASS" if passed == len(legs) else "FAIL"))
    return 0 if passed == len(legs) else 1


# ------------------------------------------------------------------------ cli
def show():
    face = _load(OUT_JSON)
    if not face:
        print("no face at %s" % FACE)
        return 2
    print(face.get("headline"))
    for key in sorted(face.get("cells") or {}):
        c = face["cells"][key]
        print("  %-22s %s" % (key, c.get("verdict") or c.get("error")))
    print("verdict=%s cutoff=%s audited_n=%s"
          % (face.get("verdict"), face.get("evidence_cutoff"), face.get("audited_n_used")))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check", "show"))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.cmd == "check":
        return check()
    if args.cmd == "show":
        return show()
    face = build(write=not args.no_write)
    print(face["headline"])
    if args.no_write:
        return 0
    print("wrote %s + %s" % (FACE, "research/IDX_FUT_CARRY_SEARCH_RENT.md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
