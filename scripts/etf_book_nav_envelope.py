"""The book has one history. How much of its headline is that history happening to line up?

Every published ETF-book number is a point estimate over exactly one ordering of 1,6xx trading
days. r1325 showed how far a *phase* can move the answer (0.53pp IQR of the same book), and
r1291/r1282 kept discovering that two arms differ by less than that. The missing object is not
another arm -- it is the DISTRIBUTION the single path was drawn from.

This face publishes that distribution, and a second object the operator has never had: the
book's own daily NAV series, so any downstream study can bootstrap/replay it without loading
the 1,503-symbol panel.

  derive_series()  panel -> production book (N12 / R20 / 8% vol target / 10bp per side)
                   -> results/etf_book_series/NAV-<cutoff>.json  (dates + nav, 6 decimals)
  run()            circular block bootstrap of that return path (block=20 bars, one
                   rebalance cycle) x N_BOOT resamples, ProcessPoolExecutor across
                   --procs workers, optionally split into --shard k/N slices
                   -> results/etf_book_bootstrap/ENVELOPE-<cutoff>.json

READING THE OUTPUT: percentiles of CAGR / Sharpe / maxDD over resamples, the share of
resamples that lose money or break a -20% drawdown, and where the published point estimate
sits in its own distribution (point_pctile). A headline that sits below p50 is a path that
happened to be kind to the book; that is a property of THIS sample, not a forecast.

Honest limits stated up front:
  * block bootstrap preserves short-range autocorrelation inside a block and destroys the
    dependence BETWEEN blocks -- it is a ruler for sampling noise, not a market simulator.
  * resampling returns keeps the book's turnover/cost drag as an average, so a resample is
    not a re-run of the strategy on a new price path; it answers "how much does the ordering
    of the same days matter", which is exactly the question the phase tests kept raising.
  * one panel (survivor pool), one window, one cost assumption, all inherited from the card.

What is reused, never rewritten:
  * panel/class filter/repair/score = scripts.etf_book_production.prep_panel
  * book engine + window split      = scripts.etf_book_production.backtest / IS_END
  * the production cell's constants  = imported from P, echoed into the face

Usage:
    python scripts/etf_book_nav_envelope.py derive
    python scripts/etf_book_nav_envelope.py run [--boot=2000] [--block=20] [--procs=4]
                                                [--shard=0/2]
    python scripts/etf_book_nav_envelope.py --check
    python scripts/etf_book_nav_envelope.py --selftest
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np

from scripts import etf_book_production as P

SCRIPT = "scripts/etf_book_nav_envelope.py"
SERIES_DIR = ROOT / "results" / "etf_book_series"
ENV_DIR = ROOT / "results" / "etf_book_bootstrap"

# ---------------------------------------------------------------- frozen criteria
# Written before the first run. The gate refuses a face whose echo differs from these.
BOOK = {"n_hold": 12, "rebal": 20, "vol_target": 0.08, "cost": P.COST}
N_BOOT = 2000
BLOCK = 20                    # one rebalance cycle: keeps the decision-cycle structure intact
SEED = 20261029
PCTS = (1, 5, 25, 50, 75, 95, 99)
# r1156/E251: p5 answered "the deepest 5% of resamples", which is not the
# question an operator asks ("how bad can it get"). p1/p99 now ride on the
# same arms so the blocks face can say whether the ultra tail is bounded or
# runs away, instead of publishing a p5 that was chosen by habit as the worst.
LOSS_LINE = 0.0               # share of resamples with CAGR <= 0
DD_LINE = -0.20               # share of resamples with maxDD <= -20%

CRITERIA = {
    "book": {"n_hold": BOOK["n_hold"], "rebal": BOOK["rebal"],
             "vol_target": BOOK["vol_target"], "cost_bp_per_side": BOOK["cost"] * 1e4,
             "source": "scripts/etf_book_production.py (the published production cell)"},
    "bootstrap": {
        "method": "circular block bootstrap of the book's daily return path",
        "n_boot": N_BOOT, "block": BLOCK, "seed": SEED,
        "seed_rule": "seed_i = SEED + 7919*i, owned by the resample index: independent of "
                     "--procs and --shard (r1349; the first version seeded per job, so the "
                     "percentiles moved with the worker count)",
        "percentiles": list(PCTS),
        "loss_line_cagr": LOSS_LINE, "drawdown_line": DD_LINE,
        "formula_cagr": "(1+prod(r))**（bars_per_year/n) - 1, bars_per_year derived from the series",
        "frozen": "constants written before the first run; the gate refuses a face that echoes others",
    },
}


# ---------------------------------------------------------------- arithmetic
def bars_per_year(dates):
    """Trading bars per calendar year, derived from the series itself (never hardcoded)."""
    if len(dates) < 2:
        return None
    import datetime as _dt
    d0 = _dt.date.fromisoformat(str(dates[0])[:10])
    d1 = _dt.date.fromisoformat(str(dates[-1])[:10])
    years = (d1 - d0).days / 365.25
    if years <= 0:
        return None
    return (len(dates) - 1) / years


def path_stats(r, bpy):
    """CAGR / Sharpe / maxDD of one return path. Zero dispersion -> Sharpe None, never inf."""
    r = np.asarray(r, dtype=float)
    n = r.size
    if n == 0 or bpy is None:
        return {"cagr": None, "sharpe": None, "maxdd": None}
    nav = np.cumprod(1.0 + r)
    if nav[-1] > 0:
        cagr = float(nav[-1] ** (bpy / n) - 1.0)
    else:
        cagr = -1.0
    sd = float(np.std(r, ddof=1)) if n > 1 else 0.0
    mu = float(np.mean(r))
    sharpe = float(mu / sd * math.sqrt(bpy)) if sd > 0 else None
    peak = np.maximum.accumulate(np.concatenate(([1.0], nav)))[:-1]
    dd = nav / peak - 1.0
    maxdd = float(np.min(dd)) if dd.size else 0.0
    return {"cagr": cagr, "sharpe": sharpe, "maxdd": maxdd}


def resample(r, block, n, rng):
    """Circular block bootstrap: n draws in blocks of `block`, wrapping the ends."""
    r = np.asarray(r, dtype=float)
    L = r.size
    if L == 0:
        return np.zeros(n)
    b = max(1, min(int(block), L))
    out = np.empty(n, dtype=float)
    filled = 0
    while filled < n:
        start = int(rng.integers(0, L))
        take = min(b, n - filled)
        idx = (start + np.arange(take)) % L
        out[filled:filled + take] = r[idx]
        filled += take
    return out


def resample_seed(i):
    """The seed belongs to the resample INDEX, never to the worker or the shard.

    r1349: the first version seeded each job with `SEED + 7919 * k`, so the set of draws --
    and therefore every published percentile -- depended on how many processes the host
    happened to split the work into. The same face re-run with the default `--procs` moved
    p5 from 3.79% to 3.66% and the point percentile from 51.0 to 49.8, which is a wider
    band than most arms in this repo are judged on. A ruler that changes with the machine
    measuring it is not a ruler, so resample i now draws from SEED + 7919 * i and a job only
    says which indices it owns.
    """
    return SEED + 7919 * int(i)


def shard_spans(boot, shards):
    """[(first_index, count)] for shard k: contiguous, disjoint, covering [0, boot)."""
    per = [boot // shards + (1 if i < boot % shards else 0) for i in range(shards)]
    spans, at = [], 0
    for c in per:
        spans.append((at, c))
        at += c
    return spans


def boot_one(args):
    """One worker's slice: (returns, bpy, block, first_index, n) -> rows tagged with index."""
    r, bpy, block, first, n = args
    r = np.asarray(r, dtype=float)
    rows = []
    for j in range(int(n)):
        i = int(first) + j
        s = resample(r, block, r.size, np.random.default_rng(resample_seed(i)))
        row = path_stats(s, bpy)
        row["i"] = i
        rows.append(row)
    return rows


def pct(sorted_vals, q):
    if not sorted_vals:
        return None
    k = (len(sorted_vals) - 1) * (q / 100.0)
    lo, hi = int(math.floor(k)), int(math.ceil(k))
    if lo == hi:
        return float(sorted_vals[lo])
    return float(sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo))


def summarize(rows, point=None):
    """Percentile envelope from per-resample rows; the single source of the arithmetic."""
    out = {}
    for key in ("cagr", "sharpe", "maxdd"):
        vals = sorted(float(r[key]) for r in rows if r.get(key) is not None)
        block = {"n": len(vals),
                 "pct": {str(q): pct(vals, q) for q in PCTS},
                 "mean": (sum(vals) / len(vals)) if vals else None,
                 "min": vals[0] if vals else None,
                 "max": vals[-1] if vals else None}
        if point is not None and point.get(key) is not None and vals:
            below = sum(1 for v in vals if v <= float(point[key]))
            block["point"] = float(point[key])
            block["point_pctile"] = round(100.0 * below / len(vals), 1)
        out[key] = block
    n = len(rows)
    if n:
        out["shares"] = {
            "cagr_le_zero": round(sum(1 for r in rows if (r.get("cagr") or 0.0) <= LOSS_LINE) / n, 3),
            "maxdd_le_line": round(sum(1 for r in rows
                                       if (r.get("maxdd") is not None
                                           and r["maxdd"] <= DD_LINE)) / n, 3),
            "n_resamples": n,
        }
    return out


# ---------------------------------------------------------------- series
def derive_series():
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    bt, ser = P.backtest(close, openp, amt, score, BOOK["n_hold"], BOOK["rebal"],
                         cost=BOOK["cost"], vol_target=BOOK["vol_target"])
    ser = ser.dropna()
    nav = ser / float(ser.iloc[0])
    dates = [str(getattr(d, "date", lambda: d)()) for d in ser.index]
    navs = [round(float(v), 6) for v in nav.tolist()]
    cutoff = dates[-1] if dates else None
    doc = {
        "evidence_cutoff": cutoff,
        "script": SCRIPT,
        "config": {"n_hold": BOOK["n_hold"], "rebal": BOOK["rebal"],
                   "vol_target": BOOK["vol_target"], "cost_bp_per_side": BOOK["cost"] * 1e4,
                   "universe_symbols": int(close.shape[1]), "flips_repaired": int(n_flip)},
        "backtest": bt,
        "bars": len(dates),
        "bars_per_year": None if bars_per_year(dates) is None else round(bars_per_year(dates), 3),
        "first_bar": dates[0] if dates else None,
        "last_bar": cutoff,
        "dates": dates,
        "nav": navs,
        "note": ("the production cell's own daily path, published so bootstrap/replay studies "
                 "do not have to reload the panel; NAV is normalised to 1.0 at the first bar"),
    }
    SERIES_DIR.mkdir(parents=True, exist_ok=True)
    out = SERIES_DIR / f"NAV-{cutoff}.json"
    out.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    latest = SERIES_DIR / "latest.json"
    latest.write_text(json.dumps({k: v for k, v in doc.items() if k not in ("dates", "nav")}
                                 | {"file": out.name}, indent=1), encoding="utf-8")
    return doc, out


def returns_from(doc):
    nav = np.asarray(doc["nav"], dtype=float)
    if nav.size < 2:
        raise SystemExit("series too short to bootstrap")
    return nav[1:] / nav[:-1] - 1.0


def run(boot=N_BOOT, block=BLOCK, procs=4, shard=None, series_file=None):
    sf = Path(series_file) if series_file else SERIES_DIR / "latest.json"
    if not sf.exists():
        raise SystemExit(f"no series face at {sf}; run `derive` first")
    meta = json.loads(sf.read_text(encoding="utf-8"))
    path = SERIES_DIR / meta.get("file", sf.name)
    doc = json.loads(path.read_text(encoding="utf-8"))
    r = returns_from(doc)
    bpy = doc.get("bars_per_year") or bars_per_year([doc["dates"][0], doc["dates"][-1]])
    point = {"cagr": doc["backtest"]["full"]["cagr"], "sharpe": doc["backtest"]["full"]["sharpe"],
             "maxdd": doc["backtest"]["full"]["maxdd"]}

    shards, k = (1, 0)
    if shard:
        a, b = str(shard).split("/")
        k, shards = int(a), int(b)
        if shards < 1 or not (0 <= k < shards):
            raise SystemExit("bad --shard k/N")
    spans = shard_spans(boot, shards)
    first, my_n = spans[k]
    if procs <= 1 or my_n <= 1:
        rows = boot_one((r.tolist(), bpy, block, first, my_n))
    else:
        chunk = max(1, my_n // procs)
        jobs = []
        left = my_n
        at = first
        while left > 0:
            take = min(chunk, left)
            jobs.append((r.tolist(), bpy, block, at, take))
            at += take
            left -= take
        rows = []
        with ProcessPoolExecutor(max_workers=procs) as ex:
            for part in ex.map(boot_one, jobs):
                rows.extend(part)

    shard_file = ENV_DIR / f"SHARD-{doc['evidence_cutoff']}-{k}of{shards}.json"
    ENV_DIR.mkdir(parents=True, exist_ok=True)
    shard_file.write_text(json.dumps({"evidence_cutoff": doc["evidence_cutoff"],
                                      "shard": f"{k}/{shards}", "rows": rows},
                                     separators=(",", ":")), encoding="utf-8")

    if shards > 1:
        print(f"shard {k}/{shards}: {len(rows)} resamples -> {shard_file.name}")
        return {"shard": f"{k}/{shards}", "rows": len(rows), "file": str(shard_file.name)}

    env = summarize(rows, point)
    env.update({
        "evidence_cutoff": doc["evidence_cutoff"],
        "script": SCRIPT,
        "criteria": CRITERIA | {"bootstrap": CRITERIA["bootstrap"] | {"block": block, "n_boot": boot}},
        "series_file": path.name,
        "bars": doc["bars"],
        "bars_per_year": round(bpy, 3),
        "point_estimate": point,
        "rows": rows,
    })
    # r1349: the reading names its own block length, so it has to be built AFTER the criteria
    # land in env -- calling it inside the update() above made every arm (b5/b60/b250) label
    # itself "block=20 bars", i.e. each arm's own sentence misreported its parameter.
    env["reading"] = _reading(env, point)
    tag = "" if block == BLOCK else f"-b{block}"
    out = ENV_DIR / f"ENVELOPE-{doc['evidence_cutoff']}{tag}.json"
    out.write_text(json.dumps(env, indent=1), encoding="utf-8")
    if not tag:
        (ENV_DIR / "latest.json").write_text(
            json.dumps({k2: v for k2, v in env.items() if k2 != "rows"} | {"file": out.name},
                       indent=1), encoding="utf-8")
    return env


def _reading(env, point):
    c = env["cagr"]["pct"]
    sh = env["sharpe"]["pct"]
    dd = env["maxdd"]["pct"]
    return ("block bootstrap (%d resamples, block=%d bars): CAGR p5/p50/p95 = "
            "%.2f%%/%.2f%%/%.2f%% per year, Sharpe %.2f/%.2f/%.2f, maxDD %.2f%%/%.2f%%/%.2f%%; "
            "the published point estimate %.2f%% sits at the %.1f pctile; %.1f%% of resamples "
            "lose money and %.1f%% break a -20%% drawdown"
            % (env["shares"]["n_resamples"],
               (env.get("criteria") or {}).get("bootstrap", {}).get("block", BLOCK),
               c["5"] * 100, c["50"] * 100, c["95"] * 100,
               sh["5"], sh["50"], sh["95"],
               dd["5"] * 100, dd["50"] * 100, dd["95"] * 100,
               (point["cagr"] or 0.0) * 100, env["cagr"].get("point_pctile") or 0.0,
               env["shares"]["cagr_le_zero"] * 100, env["shares"]["maxdd_le_line"] * 100))


def _arm_summary(env):
    """The handful of numbers every arm is compared on, read off its own face."""
    return {
        "file": None,
        "block": (env.get("criteria") or {}).get("bootstrap", {}).get("block"),
        "n_resamples": (env.get("shares") or {}).get("n_resamples"),
        "cagr": {str(q): env["cagr"]["pct"].get(str(q)) for q in PCTS},
        "sharpe": {str(q): env["sharpe"]["pct"].get(str(q)) for q in PCTS},
        "maxdd": {str(q): env["maxdd"]["pct"].get(str(q)) for q in PCTS},
        "point_pctile": {k: env[k].get("point_pctile") for k in ("cagr", "sharpe", "maxdd")},
        "shares": (env.get("shares") or {}),
    }


def blocks_spread(arms):
    """How far each quoted number moves across the block arms, in the numbers' own units."""

    def spread(key, q):
        vals = [a[key][str(q)] for a in arms if a[key].get(str(q)) is not None]
        return {"min": min(vals), "max": max(vals), "range": max(vals) - min(vals)} if vals else None

    return {
        "cagr_p1": spread("cagr", "1"),
        "cagr_p5": spread("cagr", "5"),
        "cagr_p50": spread("cagr", "50"),
        "cagr_p95": spread("cagr", "95"),
        "cagr_p99": spread("cagr", "99"),
        "maxdd_p1": spread("maxdd", "1"),
        "maxdd_p5": spread("maxdd", "5"),
        "maxdd_p50": spread("maxdd", "50"),
        "point_pctile_cagr": {
            "min": min(a["point_pctile"]["cagr"] for a in arms if a["point_pctile"]["cagr"] is not None),
            "max": max(a["point_pctile"]["cagr"] for a in arms if a["point_pctile"]["cagr"] is not None),
        },
        "dd_break_share": {"min": min(a["shares"]["maxdd_le_line"] for a in arms),
                           "max": max(a["shares"]["maxdd_le_line"] for a in arms)},
    }


def blocks_readings(spread):
    """The three descriptive readings, each comparison stating its own unit.

    r1348 defect this replaces: `drawdown_tail_is_block_dependent` compared a FRACTION range
    (-0.2502 .. -0.1708 -> 0.0794) against the threshold 3.0, so the one boolean that carries
    this face's headline ("the tail is the ruler") shipped False while the face's own reading
    string, the digest and every downstream sentence said the opposite. Percentiles here are
    fractions (cagr/maxdd) or percentile units (point_pctile), so a pp threshold must be
    applied to span*100 -- the cut-offs are 5 pctile points / 3 pp / 1 pp per the note above.
    """
    return {
        # percentile points, threshold 5
        "headline_not_a_lucky_path": (spread["point_pctile_cagr"]["max"]
                                      - spread["point_pctile_cagr"]["min"]) < 5.0,
        # pp/yr, threshold 3
        "drawdown_tail_is_block_dependent": spread["maxdd_p5"]["range"] * 100.0 > 3.0,
        # E251: same unit rule applied to the worst 1% instead of the worst 5%.
        # If the ultra tail also moves >3pp with the block length, "how bad can
        # it get" is not a bound at all -- the operator must size against a
        # distribution, not against a number.
        "ultra_tail_is_block_dependent": (
            (spread.get("maxdd_p1") or {}).get("range", 0.0) * 100.0 > 3.0),
        # pp/yr, threshold 1
        "median_cagr_stable": spread["cagr_p50"]["range"] * 100.0 < 1.0,
    }


def blocks_face(cutoff=None, out_file=None):
    """Price the one free parameter the envelope left open: the block length itself.

    E246 published a distribution but had to admit that block=20 is a choice. Three arms
    (block 5 / 60 / 250 = week / quarter / year) were registered against the same resample
    count and the same seed rule; this face puts them side by side and reports how far each
    published sentence moves when that choice moves.
    """
    latest_p = ENV_DIR / "latest.json"
    if not latest_p.exists():
        raise SystemExit("no latest.json; run `derive` + `run` first")
    latest = json.loads(latest_p.read_text(encoding="utf-8"))
    cutoff = cutoff or latest["evidence_cutoff"]
    files = sorted(ENV_DIR.glob(f"ENVELOPE-{cutoff}*.json"))
    arms = []
    refreshed = []
    for f in files:
        doc = json.loads(f.read_text(encoding="utf-8"))
        # E251: an arm published before p1/p99 existed already carries its own
        # resample rows, so the missing percentiles are a pure function of data
        # on disk -- no 2000-draw re-run, and no number that the rows do not
        # already contain. Refresh in place so the ARM stays the single source.
        if doc.get("rows"):
            again = summarize(doc["rows"], doc.get("point_estimate"))
            changed = False
            for key in ("cagr", "sharpe", "maxdd"):
                pct_block = doc.setdefault(key, {}).setdefault("pct", {})
                for q in PCTS:
                    got = (again.get(key) or {}).get("pct", {}).get(str(q))
                    if got is not None and pct_block.get(str(q)) is None:
                        pct_block[str(q)] = got
                        changed = True
            if changed:
                f.write_text(json.dumps(doc, indent=1), encoding="utf-8")
                refreshed.append(f.name)
        s = _arm_summary(doc)
        s["file"] = f.name
        s["reading"] = doc.get("reading")
        arms.append(s)
    arms.sort(key=lambda x: (x["block"] is None, x["block"]))
    if len({a["block"] for a in arms}) < 2:
        raise SystemExit(f"only one block arm on disk for {cutoff}; run `run --block N` first")

    face = {
        "evidence_cutoff": cutoff,
        "script": SCRIPT,
        "question": "how much of the published envelope is the block length rather than the book?",
        "arms": arms,
        "arm_pcts_refreshed": refreshed,
        "spread": blocks_spread(arms),
        "thresholds_note": ("the three readings below were fixed AFTER the arms were run, and "
                            "are descriptive cut-offs (5 pctile pts / 3 pp / 1 pp), not gates: "
                            "they name which sentences survive the parameter and which do not"),
    }
    sp = face["spread"]
    face["reading"] = (
        "block length %s: the headline's LOCATION is stable (point pctile %.1f to %.1f, CAGR p50 "
        "%.2f to %.2f%%/yr) while the TAIL is not (CAGR p5 %.2f to %.2f%%, maxDD p5 %.2f to "
        "%.2f%%, share breaking -20%% %.1f%% to %.1f%%)"
        % ("/".join(str(a["block"]) for a in arms),
           sp["point_pctile_cagr"]["min"], sp["point_pctile_cagr"]["max"],
           sp["cagr_p50"]["min"] * 100, sp["cagr_p50"]["max"] * 100,
           sp["cagr_p5"]["min"] * 100, sp["cagr_p5"]["max"] * 100,
           sp["maxdd_p5"]["min"] * 100, sp["maxdd_p5"]["max"] * 100,
           sp["dd_break_share"]["min"] * 100, sp["dd_break_share"]["max"] * 100))
    # E251: the ultra tail only speaks when the arms actually carry p1/p99. An
    # arm run before this change publishes no p1, and printing a nan range would
    # answer "how bad can it get" with a number-shaped nothing.
    p1_dd, p1_cagr = sp.get("maxdd_p1"), sp.get("cagr_p1")
    if p1_dd and p1_cagr and p1_dd.get("min") is not None:
        face["reading"] += (
            "; the worst 1%% reads maxDD p1 %.2f to %.2f%% and CAGR p1 %.2f to %.2f%%/yr"
            % (p1_dd["min"] * 100, p1_dd["max"] * 100,
               p1_cagr["min"] * 100, p1_cagr["max"] * 100))
        face["ultra_tail_published"] = True
    else:
        face["reading"] += ("; the worst 1% is NOT published on these arms (they were run "
                            "before p1/p99 were added -- re-run `run --block N` per arm)")
        face["ultra_tail_published"] = False
    face["readings"] = blocks_readings(sp)
    out = Path(out_file) if out_file else ENV_DIR / f"BLOCKS-{cutoff}.json"
    out.write_text(json.dumps(face, indent=1), encoding="utf-8")
    return face, out


def check_blocks(face_file=None):
    """Every quoted arm number must be re-derivable from that arm's own published rows."""
    f = Path(face_file) if face_file else None
    if f is None:
        latest_p = ENV_DIR / "latest.json"
        if not latest_p.exists():
            print("FACE MISSING: latest.json")
            return 2
        cutoff = json.loads(latest_p.read_text(encoding="utf-8"))["evidence_cutoff"]
        f = ENV_DIR / f"BLOCKS-{cutoff}.json"
    if not f.exists():
        print(f"FACE MISSING: {f.name}")
        return 2
    face = json.loads(f.read_text(encoding="utf-8"))
    problems = []
    arms = face.get("arms") or []
    if len(arms) < 2:
        problems.append("fewer than two block arms -- the parameter is not priced")
    for a in arms:
        p = ENV_DIR / str(a.get("file"))
        if not p.exists():
            problems.append(f"arm file missing: {a.get('file')}")
            continue
        doc = json.loads(p.read_text(encoding="utf-8"))
        again = summarize(doc.get("rows") or [], doc.get("point_estimate"))
        for key in ("cagr", "sharpe", "maxdd"):
            for q in PCTS:
                # E251: arms run before p1/p99 existed simply have no such
                # percentile; "absent on both sides" is the honest match, and a
                # quoted p1 with no rows behind it is still a problem.
                quoted = a[key].get(str(q))
                rebuild = again[key]["pct"].get(str(q))
                if (quoted is None) != (rebuild is None) or (
                        quoted is not None and abs(quoted - rebuild) > 1e-9):
                    problems.append(f"block {a['block']} {key} p{q}: quoted {quoted} != rows {rebuild}")
            if a["point_pctile"][key] != again[key].get("point_pctile"):
                problems.append(f"block {a['block']} {key} point_pctile: quoted "
                                f"{a['point_pctile'][key]} != rows {again[key].get('point_pctile')}")
    # r1348: the arms being right does not make the SUMMARY right. Re-derive the spread and
    # the three readings from the re-judged arms, so a stored boolean that contradicts the
    # arms (the unit-mismatch bug this round fixed) is caught by the gate instead of read.
    if arms and all(a.get("cagr") for a in arms):
        want_sp, want_rd = blocks_spread(arms), blocks_readings(blocks_spread(arms))
        for key, val in (face.get("spread") or {}).items():
            got = want_sp.get(key)
            if got is None:
                problems.append(f"spread.{key}: published but not derivable from the arms")
                continue
            for edge in ("min", "max"):
                if edge in got and (val.get(edge) is None
                                    or abs(float(val[edge]) - float(got[edge])) > 1e-12):
                    problems.append(f"spread.{key}.{edge}: published {val.get(edge)} != arms {got[edge]}")
        for key, flag in (face.get("readings") or {}).items():
            if key not in want_rd:
                problems.append(f"readings.{key}: published but not in the frozen rule")
            elif bool(flag) != bool(want_rd[key]):
                problems.append(f"readings.{key}: published {flag} but the arms say {want_rd[key]}")
    if problems:
        for p in problems[:12]:
            print("FAIL:", p)
        return 1
    print(f"OK: {len(arms)} block arms re-judged against their own rows "
          f"({', '.join(str(a['block']) for a in arms)})")
    return 0


# ---------------------------------------------------------------- vol overlay tail (E253)
# The card says the 8% vol target is "a drawdown tool, not an edge", and every number
# behind that sentence is a median or a single path. E253 asks the question the operator
# actually has: does the overlay shorten the TAIL, or only the middle? Answering it needs
# the same ruler on both books, so both arms are bootstrapped with the SAME resample index
# (hence the same draw) and compared per resample -- a paired test, not two published bands
# read side by side.
VT_BLOCKS = (5, 20, 60, 120, 250)   # the same block arms the envelope already prices
VT_FILE = "etf_book_voltarget_tail.json"


def resample_indices(L, block, n, rng):
    """The block-bootstrap index sequence itself, so two arms can share ONE draw.

    r1350: `resample()` advances the rng every call, so calling it twice with the same
    generator hands the second arm a *different* draw even when both arms are the same
    series -- the "paired" test would then be two independent bands read side by side,
    which is exactly what the design says it is not (selftest L21 caught it: identical
    arms produced a -10pp median delta). Drawing the indices once and indexing both
    return vectors is the only way the delta is really per-resample.
    """
    L = int(L)
    if L == 0:
        return np.zeros(int(n), dtype=int)
    b = max(1, min(int(block), L))
    out = np.empty(int(n), dtype=int)
    filled = 0
    while filled < n:
        start = int(rng.integers(0, L))
        take = min(b, n - filled)
        out[filled:filled + take] = (start + np.arange(take)) % L
        filled += take
    return out


def pair_rows(r_on, r_off, bpy, block, first, n):
    """Paired resamples: index i draws ONE sequence and prices both arms on it."""
    r_on = np.asarray(r_on, dtype=float)
    r_off = np.asarray(r_off, dtype=float)
    rows = []
    for j in range(int(n)):
        i = int(first) + j
        rng = np.random.default_rng(resample_seed(i))
        idx = resample_indices(r_on.size, block, r_on.size, rng)
        s_on = r_on[idx]
        s_off = r_off[idx]
        rows.append({"i": i, "on": path_stats(s_on, bpy), "off": path_stats(s_off, bpy)})
    return rows


def _pct_map(vals):
    s = sorted(v for v in vals if v is not None)
    return {"n": len(s), "pct": {str(q): pct(s, q) for q in PCTS}}


def paired_face(rows, on_point=None, off_point=None):
    """Per-arm envelopes plus the per-resample DELTA (on minus off) and its own percentiles."""
    on = summarize([r["on"] for r in rows], on_point)
    off = summarize([r["off"] for r in rows], off_point)
    d_dd = [r["on"]["maxdd"] - r["off"]["maxdd"] for r in rows
            if r["on"].get("maxdd") is not None and r["off"].get("maxdd") is not None]
    d_cg = [r["on"]["cagr"] - r["off"]["cagr"] for r in rows
            if r["on"].get("cagr") is not None and r["off"].get("cagr") is not None]
    n = len(d_dd)
    delta = {
        "n": n,
        "maxdd": _pct_map(d_dd),
        "cagr": _pct_map(d_cg),
        # a shallower drawdown is a POSITIVE delta (on - off), so "better" is the >0 share
        "maxdd_better_share": (round(sum(1 for d in d_dd if d > 0) / n, 3) if n else None),
        "maxdd_worse_share": (round(sum(1 for d in d_dd if d < 0) / n, 3) if n else None),
        "cagr_better_share": (round(sum(1 for d in d_cg if d > 0) / n, 3) if len(d_cg) else None),
        "unit_note": "deltas are fractions of capital (maxdd) and per-year returns (cagr); "
                     "positive maxdd delta = the overlay made the drawdown SHALLOWER",
    }
    return {"on": {k: on[k] for k in ("cagr", "sharpe", "maxdd", "shares")},
            "off": {k: off[k] for k in ("cagr", "sharpe", "maxdd", "shares")},
            "delta": delta}


def _tail_verdict(face_arms, tol=0.005):
    """Does the overlay move the tail as much as it moves the middle?

    Frozen after the first run (see criteria) and reported as booleans, not prose: an
    overlay that buys 3pp of median drawdown and 0.2pp of p1 drawdown is a middle-moving
    tool, and the card's advice would be wrong in the direction that matters.
    """
    med, tail, cg = [], [], []
    for a in face_arms:
        d = a["delta"]
        med.append(d["maxdd"]["pct"]["50"])
        tail.append(d["maxdd"]["pct"]["1"])
        cg.append(d["cagr"]["pct"]["50"])
    if not med or any(v is None for v in med + tail + cg):
        return {"middle_moves": None, "tail_moves": None, "middle_only": None}
    middle_moves = abs(sum(med) / len(med)) >= tol
    tail_moves = abs(sum(tail) / len(tail)) >= tol
    out = {
        "middle_moves": bool(middle_moves),
        "tail_moves": bool(tail_moves),
        "middle_only": bool(middle_moves and not tail_moves),
        "median_maxdd_delta_median": sum(med) / len(med),
        "p1_maxdd_delta_median": sum(tail) / len(tail),
        "p50_cagr_delta_median": sum(cg) / len(cg),
        # r1350: "the tail moves too" at 1.3pp is true and nearly useless next to a 6pp
        # median. The ratio is what an operator can act on: how much of the middle's gain
        # survives at the worst 1% of histories.
        "tail_share_of_middle": (round((sum(tail) / len(tail)) / (sum(med) / len(med)), 3)
                                 if abs(sum(med) / len(med)) > 1e-12 else None),
        "tail_is_mostly_a_middle_effect": None,
        "tol_note": "a move counts at >= %.1fpp of capital on the per-resample delta" % (tol * 100),
    }
    r = out["tail_share_of_middle"]
    out["tail_is_mostly_a_middle_effect"] = (None if r is None else bool(r < 0.5))
    return out


def derive_arm_series():
    """Both arms off ONE panel/score build: only the sizing rule differs."""
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    out = {}
    for lbl, vt in (("on", BOOK["vol_target"]), ("off", None)):
        bt, ser = P.backtest(close, openp, amt, score, BOOK["n_hold"], BOOK["rebal"],
                             cost=BOOK["cost"], vol_target=vt)
        ser = ser.dropna()
        out[lbl] = {"bt": bt, "returns": ser.pct_change().dropna().to_numpy(dtype=float),
                    "dates": [str(getattr(d, "date", lambda: d)()) for d in ser.index]}
    return out, n_flip, int(close.shape[1])


def voltail_face(boot=N_BOOT, procs=4, out_file=None):
    """Price the 8% overlay on the tail: same draws, both arms, per block length."""
    arms_series, n_flip, n_sym = derive_arm_series()
    bpy = bars_per_year(arms_series["on"]["dates"])
    cutoff = arms_series["on"]["dates"][-1]
    r_on = arms_series["on"]["returns"]
    r_off = arms_series["off"]["returns"]
    if r_on.size != r_off.size:
        raise SystemExit("arms have different path lengths -- they are not the same book")
    face_arms = []
    for block in VT_BLOCKS:
        spans = shard_spans(boot, max(1, procs))
        jobs = [(r_on.tolist(), r_off.tolist(), bpy, block, first, cnt)
                for first, cnt in spans if cnt > 0]
        rows = []
        if len(jobs) == 1:
            rows = pair_rows(*jobs[0])
        else:
            with ProcessPoolExecutor(max_workers=procs) as ex:
                for part in ex.map(_pair_job, jobs):
                    rows.extend(part)
        rows.sort(key=lambda r: r["i"])
        on_pt = arms_series["on"]["bt"]["full"]
        off_pt = arms_series["off"]["bt"]["full"]
        pf = paired_face(rows, {"cagr": on_pt["cagr"], "sharpe": on_pt["sharpe"],
                                "maxdd": on_pt["maxdd"]},
                         {"cagr": off_pt["cagr"], "sharpe": off_pt["sharpe"],
                          "maxdd": off_pt["maxdd"]})
        # rows go to their own file so the gate can re-judge every quoted delta without a
        # 2,000-draw re-run (same rule the block arms use for their own rows)
        rf = ENV_DIR / f"PAIRROWS-{cutoff}-b{block}.json"
        ENV_DIR.mkdir(parents=True, exist_ok=True)
        rf.write_text(json.dumps({"evidence_cutoff": cutoff, "block": block, "rows": rows},
                                 separators=(",", ":")), encoding="utf-8")
        one = {"block": block, "rows_file": rf.name}
        one.update(pf)
        face_arms.append(one)

    face = {
        "evidence_cutoff": cutoff,
        "script": SCRIPT,
        "question": "does the 8% vol overlay shorten the drawdown TAIL, or only the middle?",
        "arms_definition": {
            "on": {"vol_target": BOOK["vol_target"], "n_hold": BOOK["n_hold"],
                   "rebal": BOOK["rebal"], "cost_bp_per_side": BOOK["cost"] * 1e4},
            "off": {"vol_target": None, "n_hold": BOOK["n_hold"],
                    "rebal": BOOK["rebal"], "cost_bp_per_side": BOOK["cost"] * 1e4},
        },
        "design": ("paired circular block bootstrap: resample index i draws ONE sequence of "
                   "daily returns and prices BOTH arms on it, so a row's delta is the overlay's "
                   "effect on the same bootstrapped history rather than the difference of two "
                   "independent bands (r1349 seed law: seed_i = SEED + 7919*i)"),
        "blocks": list(VT_BLOCKS), "n_resamples": boot, "seed": SEED,
        "bars": int(r_on.size), "bars_per_year": round(bpy, 3),
        "universe_symbols": n_sym, "flips_repaired": n_flip,
        "point_estimate": {"on": arms_series["on"]["bt"]["full"],
                           "off": arms_series["off"]["bt"]["full"]},
        "arms": [{k: v for k, v in a.items() if k != "rows"} for a in face_arms],
        "verdict": _tail_verdict(face_arms),
    }
    v = face["verdict"]
    # E251 law (refuse to print a nan range): a face whose percentiles are all nan is a
    # number-shaped nothing. This shipped once in-window -- the returns were ratios, not
    # pct-change, so every drawdown read nan and the reading still printed.
    nonfinite = [k for k in ("median_maxdd_delta_median", "p1_maxdd_delta_median")
                 if v.get(k) is None or not math.isfinite(v[k])]
    if nonfinite:
        raise SystemExit("refusing to publish: non-finite deltas %s (check the return series)"
                         % nonfinite)
    face["reading"] = (
        "paired bootstrap (%d resamples, blocks %s): the overlay's median drawdown delta is "
        "%+.2fpp while the p1 delta is %+.2fpp -- %s"
        % (boot, "/".join(str(b) for b in VT_BLOCKS),
           (v.get("median_maxdd_delta_median") or 0.0) * 100,
           (v.get("p1_maxdd_delta_median") or 0.0) * 100,
           "the overlay moves the MIDDLE but not the TAIL, so it is not the crash insurance "
           "the card's wording implies" if v.get("middle_only") else
           "the overlay moves the tail too" if v.get("tail_moves") else
           "neither middle nor tail is priced on these arms"))
    if v.get("tail_share_of_middle") is not None:
        face["reading"] += (
            "; only %.0f%% of the median gain survives at the worst 1%% of histories, so the "
            "overlay is mostly a middle-path tool%s, bought with %+.2fpp of median CAGR"
            % (v["tail_share_of_middle"] * 100,
               " (the worst 1%% still lands between %.0f%% and %.0f%% across blocks)"
               % (min((a["on"]["maxdd"]["pct"]["1"] or 0.0) for a in face_arms) * 100,
                  max((a["on"]["maxdd"]["pct"]["1"] or 0.0) for a in face_arms) * 100)
               if v.get("tail_is_mostly_a_middle_effect") else "",
               v.get("p50_cagr_delta_median", 0.0) * 100))
    out = Path(out_file) if out_file else ENV_DIR / VT_FILE
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(face, indent=1), encoding="utf-8")
    return face, out


def _pair_job(args):
    return pair_rows(*args)


def check_voltail(face_file=None):
    """Every published delta must be recomputable from the stored paired rows."""
    f = Path(face_file) if face_file else ENV_DIR / VT_FILE
    if not f.exists():
        print(f"FACE MISSING: {f.name}")
        return 2
    face = json.loads(f.read_text(encoding="utf-8"))
    problems = []
    if (face.get("arms_definition") or {}).get("on", {}).get("vol_target") is None:
        problems.append("the 'on' arm has no vol target -- the two arms are the same book")
    if (face.get("arms_definition") or {}).get("off", {}).get("vol_target") is not None:
        problems.append("the 'off' arm carries a vol target -- it is not the control")
    if len(face.get("arms") or []) < 2:
        problems.append("fewer than two block arms -- the block parameter is not priced")
    for a in face.get("arms") or []:
        p = ENV_DIR / f"PAIRROWS-{face.get('evidence_cutoff')}-b{a.get('block')}.json"
        rows = None
        if p.exists():
            rows = json.loads(p.read_text(encoding="utf-8")).get("rows")
        if not rows:
            problems.append(f"block {a.get('block')}: no paired rows on disk to re-judge")
            continue
        again = paired_face(rows)
        for arm in ("on", "off"):
            for key in ("cagr", "maxdd"):
                for q in PCTS:
                    quoted = (a[arm][key]["pct"] or {}).get(str(q))
                    rebuild = again[arm][key]["pct"].get(str(q))
                    if (quoted is None) != (rebuild is None) or (
                            quoted is not None and abs(quoted - rebuild) > 1e-9):
                        problems.append(f"block {a['block']} {arm} {key} p{q}: "
                                        f"{quoted} != rows {rebuild}")
        for key in ("maxdd_better_share", "maxdd_worse_share", "cagr_better_share"):
            if a["delta"].get(key) != again["delta"].get(key):
                problems.append(f"block {a['block']} delta.{key}: published "
                                f"{a['delta'].get(key)} != rows {again['delta'].get(key)}")
    if problems:
        for p in problems[:12]:
            print("FAIL:", p)
        return 1
    print(f"OK: {len(face.get('arms') or [])} paired block arms re-judged against their rows")
    return 0


# ---------------------------------------------------------------- gate
def check(env_file=None):
    """Re-derive every published percentile from the stored resample rows.

    r1349: the criteria-echo branch is a STALE branch and says so in that word -- the S6
    runner pays a leg's declared refresh only when the probe output contains "stale"
    (r1345/E237), so a face written under older CRITERIA stayed red through a whole chain
    record this morning with its refresh declared and never spent. A published number that
    disagrees with its own rows is still worded as a disagreement, never as staleness, so a
    tampered digit can never trigger a silent regeneration.
    """
    f = Path(env_file) if env_file else ENV_DIR / "latest.json"
    if not f.exists():
        print(f"FACE MISSING: {f}")
        return 2
    meta = json.loads(f.read_text(encoding="utf-8"))
    path = ENV_DIR / meta.get("file", f.name)
    env = json.loads(path.read_text(encoding="utf-8"))
    problems = []
    crit = env.get("criteria") or {}
    frozen = {k: v for k, v in crit.items() if k != "bootstrap"}
    if frozen != {k: v for k, v in CRITERIA.items() if k != "bootstrap"}:
        problems.append("criteria echo is stale against the frozen constants "
                        "(the face was written under older rules and needs a re-derive)")
    bootd = {k: v for k, v in (crit.get("bootstrap") or {}).items()
             if k not in ("block", "n_boot")}
    if bootd != {k: v for k, v in CRITERIA["bootstrap"].items() if k not in ("block", "n_boot")}:
        problems.append("bootstrap criteria echo is stale against the frozen constants "
                        "(block/n_boot are per-run knobs; every other field is fixed)")
    if not env.get("rows"):
        problems.append("no per-resample rows published -- the envelope cannot be re-judged")
        rows = []
    else:
        rows = env["rows"]
    if rows:
        again = summarize(rows, env.get("point_estimate"))
        for key in ("cagr", "sharpe", "maxdd"):
            for q in PCTS:
                a = env[key]["pct"][str(q)]
                b = again[key]["pct"][str(q)]
                if a is None or b is None or abs(a - b) > 1e-9:
                    problems.append(f"{key} p{q}: published {a} != rebuild {b}")
            if env[key].get("point_pctile") != again[key].get("point_pctile"):
                problems.append(f"{key} point_pctile: published "
                                f"{env[key].get('point_pctile')} != rebuild "
                                f"{again[key].get('point_pctile')}")
        if env.get("shares") != again.get("shares"):
            problems.append(f"shares: published {env.get('shares')} != rebuild {again.get('shares')}")
        # r1349: the percentile rebuild above only proves the face agrees with ITSELF. A face
        # produced by the old procs-dependent seeding agrees with itself and is still not
        # reproducible on another host, so re-draw a deterministic sample from the index rule.
        idx = [r0.get("i") for r0 in rows]
        if any(v is None for v in idx):
            problems.append("rows carry no resample index -- the draw rule cannot be re-judged")
        elif sorted(idx) != list(range(len(rows))):
            problems.append("resample indices are not exactly 0..n-1")
        else:
            sf = SERIES_DIR / str(env.get("series_file") or "")
            if not sf.exists():
                problems.append(f"series face missing ({sf.name}) -- draws cannot be re-judged")
            else:
                doc = json.loads(sf.read_text(encoding="utf-8"))
                rr = returns_from(doc)
                bpy = env.get("bars_per_year") or doc.get("bars_per_year")
                block = int((crit.get("bootstrap") or {}).get("block", BLOCK))
                by_i = {r0["i"]: r0 for r0 in rows}
                probe = [i for i in range(len(rows)) if i % 97 == 0]
                bad = 0
                for i in probe:
                    s = resample(rr, block, rr.size, np.random.default_rng(resample_seed(i)))
                    redraw = path_stats(s, bpy)
                    for key in ("cagr", "sharpe", "maxdd"):
                        a, b = by_i[i].get(key), redraw[key]
                        if (a is None) != (b is None) or (a is not None and abs(a - b) > 1e-12):
                            bad += 1
                            break
                if bad:
                    problems.append(f"{bad}/{len(probe)} sampled rows cannot be re-drawn from "
                                    f"seed_i = SEED + 7919*i (procs/shard-dependent seeding)")
                else:
                    print(f"seed rule: {len(probe)} of {len(rows)} rows re-drawn from their index")
    if problems:
        for p in problems[:12]:
            print("FAIL:", p)
        return 1
    print(f"OK: {len(rows)} resample rows re-judged, every percentile and share matches")
    return 0


# ---------------------------------------------------------------- selftest
def selftest():
    ok = []

    def leg(name, cond, detail=""):
        ok.append((name, bool(cond), detail))

    rng = np.random.default_rng(7)
    r = rng.normal(0.0004, 0.009, 1650)
    bpy = 243.0

    # L1 a resample has the length of the source
    s = resample(r, 20, 500, np.random.default_rng(1))
    leg("L1 resample length == n", s.size == 500, s.size)

    # L2 with block == n the resample is a rotation: same multiset of returns
    s2 = resample(r, r.size, r.size, np.random.default_rng(2))
    leg("L2 block==n is a rotation", np.allclose(np.sort(s2), np.sort(r)))

    # L3 determinism under a seed
    a = boot_one((r.tolist(), bpy, 20, 99, 5))
    b = boot_one((r.tolist(), bpy, 20, 99, 5))
    leg("L3 same seed -> identical stats", a == b)

    # L4 a different seed moves the numbers
    c = boot_one((r.tolist(), bpy, 20, 100, 5))
    leg("L4 different seed -> different stats", a != c)

    # L5 percentile ordering is monotone
    env = summarize(a)
    p = env["cagr"]["pct"]
    leg("L5 percentiles monotone", p["5"] <= p["25"] <= p["50"] <= p["75"] <= p["95"], p)

    # L6 zero dispersion gives None Sharpe, never inf/nan
    z = path_stats(np.zeros(50), bpy)
    leg("L6 zero vol -> Sharpe None", z["sharpe"] is None, z)

    # L7 point percentile: a point above every resample reads 100
    pt = {"cagr": max(x["cagr"] for x in a) + 1.0, "sharpe": None, "maxdd": None}
    env2 = summarize(a, pt)
    leg("L7 point above all -> 100th pctile", env2["cagr"]["point_pctile"] == 100.0,
        env2["cagr"]["point_pctile"])

    # L8 the mechanism actually ran: resampled paths are not the identity path
    ident = path_stats(r, bpy)
    leg("L8 bootstrap moves the answer", abs(env["cagr"]["pct"]["50"] - ident["cagr"]) > 1e-12,
        (env["cagr"]["pct"]["50"], ident["cagr"]))

    # L9 a hand-edited percentile is caught by the gate's recompute
    good = summarize(a, None)
    bad = json.loads(json.dumps(good))
    bad["cagr"]["pct"]["50"] = (bad["cagr"]["pct"]["50"] or 0.0) + 0.01
    caught = bad["cagr"]["pct"]["50"] != summarize(a, None)["cagr"]["pct"]["50"]
    leg("L9 edited percentile contradicted by rows", caught)

    # L10 shard arithmetic: the per-shard spans are contiguous, disjoint and cover [0, boot)
    spans = shard_spans(7, 3)
    leg("L10 shard spans cover 0..n exactly once",
        [c for _, c in spans] == [3, 2, 2] and [f for f, _ in spans] == [0, 3, 5]
        and sum(c for _, c in spans) == 7, spans)

    # L11 maxDD is <= 0 by construction
    leg("L11 maxDD not positive", all(x["maxdd"] <= 0 for x in a))

    # L12 r1349: the draw set is owned by the index, so splitting the same span across more
    # jobs must not change one number -- this is the leg that would have caught the
    # procs-dependent seeding before the face shipped.
    whole = boot_one((r.tolist(), bpy, 20, 0, 8))
    split = (boot_one((r.tolist(), bpy, 20, 0, 3))
             + boot_one((r.tolist(), bpy, 20, 3, 2))
             + boot_one((r.tolist(), bpy, 20, 5, 3)))
    leg("L12 job split does not move the draws", whole == split)

    # L13 and the index travels with the row, so the gate can re-draw any single resample
    leg("L13 rows carry their own index", [x["i"] for x in whole] == list(range(8)),
        [x["i"] for x in whole])

    # L14 a row re-drawn from its index reproduces the stored stats exactly
    redraw = path_stats(resample(r, 20, r.size, np.random.default_rng(resample_seed(5))), bpy)
    leg("L14 stored row == re-draw from its index",
        all(whole[5][k] == redraw[k] for k in ("cagr", "sharpe", "maxdd")), whole[5])

    # L15/L16 r1348: the readings compare FRACTIONS (cagr/maxdd) and percentile units
    # (point_pctile), so each threshold states its unit. The shipped bug compared a 7.94pp
    # drawdown span (-0.2502..-0.1708 -> 0.0794) against 3.0 and published False -- the one
    # boolean carrying "the tail is the ruler" contradicted the face's own reading string.
    wide = {"maxdd_p5": {"min": -0.2502, "max": -0.1708, "range": 0.0794},
            "cagr_p50": {"min": 0.0921, "max": 0.0974, "range": 0.0052},
            "point_pctile_cagr": {"min": 49.6, "max": 53.6}}
    leg("L15 a 7.94pp drawdown span reads block-dependent (pp units, not fractions)",
        blocks_readings(wide)["drawdown_tail_is_block_dependent"] is True,
        blocks_readings(wide))
    narrow = {"maxdd_p5": {"min": -0.1310, "max": -0.1260, "range": 0.0050},
              "cagr_p50": {"min": 0.0960, "max": 0.0970, "range": 0.0010},
              "point_pctile_cagr": {"min": 50.0, "max": 51.0}}
    leg("L16 a 0.50pp drawdown span does not (the flag is not hardwired true)",
        blocks_readings(narrow)["drawdown_tail_is_block_dependent"] is False,
        blocks_readings(narrow))

    # L17 a stored readings block that contradicts the arms is contradicted by the gate rule
    # (the same recompute check_blocks runs), not merely by a comment.
    stored = dict(blocks_readings(wide))
    stored["drawdown_tail_is_block_dependent"] = False
    leg("L17 an edited readings flag is contradicted by its own spread",
        any(bool(v) != bool(want) for k, v in stored.items()
            for want in [blocks_readings(wide)[k]]))
    leg("L18 spread is derived, not stored",
        abs(blocks_spread([{"cagr": {"5": 0.02}, "maxdd": {"5": -0.25},
                            "point_pctile": {"cagr": 49.0}, "shares": {"maxdd_le_line": 0.16}},
                           {"cagr": {"5": 0.04}, "maxdd": {"5": -0.17},
                            "point_pctile": {"cagr": 53.0}, "shares": {"maxdd_le_line": 0.01}}])
            ["maxdd_p5"]["range"] - 0.08) < 1e-12)

    # L19/L20 E251: the ultra tail is on the same arms, ordered, and priced --
    # a p1 that claims to be deeper than the p5 it sits beside is a lie the
    # page would publish. L20 proves the new flag can fire AND can stay quiet.
    leg("L19 p1 <= p5 <= p50 <= p95 <= p99 on the same rows",
        p["1"] <= p["5"] <= p["50"] <= p["95"] <= p["99"], p)
    ultra = {"maxdd_p1": {"min": -0.4210, "max": -0.2910, "range": 0.1300},
             "maxdd_p5": {"min": -0.2502, "max": -0.1708, "range": 0.0794},
             "cagr_p50": {"min": 0.0921, "max": 0.0974, "range": 0.0052},
             "point_pctile_cagr": {"min": 49.6, "max": 53.6}}
    tight = {"maxdd_p1": {"min": -0.3900, "max": -0.3850, "range": 0.0050},
             "maxdd_p5": {"min": -0.1310, "max": -0.1260, "range": 0.0050},
             "cagr_p50": {"min": 0.0960, "max": 0.0970, "range": 0.0010},
             "point_pctile_cagr": {"min": 50.0, "max": 51.0}}
    leg("L20 the ultra-tail flag fires on a 13pp span and stays quiet on 0.50pp",
        blocks_readings(ultra)["ultra_tail_is_block_dependent"] is True
        and blocks_readings(tight)["ultra_tail_is_block_dependent"] is False,
        (blocks_readings(ultra)["ultra_tail_is_block_dependent"],
         blocks_readings(tight)["ultra_tail_is_block_dependent"]))

    # L21-L25 E253: the paired tail test must be provably PAIRED (identical arms give
    # exactly zero deltas), ordered, and its verdict must be able to say both things.
    same = pair_rows(r.tolist(), r.tolist(), bpy, 20, 0, 6)
    pf_same = paired_face(same)
    leg("L21 identical arms give exactly zero delta on every resample",
        all(x["on"]["maxdd"] == x["off"]["maxdd"] and x["on"]["cagr"] == x["off"]["cagr"]
            for x in same)
        and pf_same["delta"]["maxdd"]["pct"]["50"] == 0.0
        and pf_same["delta"]["maxdd_better_share"] == 0.0,
        pf_same["delta"]["maxdd"]["pct"])

    # a real pair: the overlay de-levers, so the same draw on both arms is a fair test
    hires = r * 1.5
    pf_pair = paired_face(pair_rows(hires, r, bpy, 20, 0, 200))
    d = pf_pair["delta"]
    leg("L22 a scaled arm produces a non-degenerate delta and a complete split",
        d["maxdd"]["pct"]["50"] is not None
        and abs((d["maxdd_better_share"] or 0) + (d["maxdd_worse_share"] or 0) - 1.0) < 1e-9,
        (d["maxdd_better_share"], d["maxdd_worse_share"]))
    leg("L23 delta percentiles are ordered p1 <= p5 <= p50 <= p95 <= p99",
        d["maxdd"]["pct"]["1"] <= d["maxdd"]["pct"]["5"] <= d["maxdd"]["pct"]["50"]
        <= d["maxdd"]["pct"]["95"] <= d["maxdd"]["pct"]["99"], d["maxdd"]["pct"])

    # L24/L25 the verdict must be able to say "middle only" AND must not say it when the
    # tail moves by the same amount (a flag that is always true is not a reading).
    def _arm(med, p1, cg):
        return {"delta": {"maxdd": {"pct": {"50": med, "1": p1, "5": p1}},
                          "cagr": {"pct": {"50": cg}}}}
    middle_only = _tail_verdict([_arm(0.030, 0.001, -0.004), _arm(0.028, 0.002, -0.004)])
    tail_too = _tail_verdict([_arm(0.030, 0.026, -0.004), _arm(0.028, 0.027, -0.004)])
    leg("L24 verdict reads middle-only when the middle moves 3pp and the p1 does not",
        middle_only["middle_only"] is True and middle_only["tail_moves"] is False,
        middle_only)
    leg("L25 verdict clears the overlay when the p1 moves with the middle",
        tail_too["middle_only"] is False and tail_too["tail_moves"] is True, tail_too)

    # L26 the paired ruler IS the published ruler: the index sequence reproduces
    # resample() exactly on the same stream, so the delta is priced by the same bootstrap.
    rng1, rng2 = np.random.default_rng(SEED), np.random.default_rng(SEED)
    leg("L26 resample_indices == resample on the same stream",
        np.allclose(r[resample_indices(r.size, 20, 300, rng1)], resample(r, 20, 300, rng2)),
        None)
    leg("L27 the two arms share one draw even when the generator is advanced",
        all(x["on"]["maxdd"] == x["off"]["maxdd"]
            for x in pair_rows(r.tolist(), r.tolist(), bpy, 60, 0, 4)))

    # L28/L29 the ratio that makes "the tail moves too" actionable: a 1.3pp tail against a
    # 6pp middle is not crash insurance, and the flag must say both things.
    ratio = _tail_verdict([_arm(0.060, 0.013, -0.046)])["tail_share_of_middle"]
    leg("L28 a 1.3pp tail on a 6pp middle reads a tail share of ~0.22",
        ratio is not None and 0.15 < ratio < 0.30, ratio)
    leg("L29 a tail that keeps 80% of the middle does not",
        _tail_verdict([_arm(0.060, 0.048, -0.046)])["tail_is_mostly_a_middle_effect"] is False
        and _tail_verdict([_arm(0.060, 0.013, -0.046)])["tail_is_mostly_a_middle_effect"] is True)

    print(f"selftest {sum(1 for _, c, _ in ok if c)}/{len(ok)}")
    for name, cond, detail in ok:
        if not cond:
            print("FAIL", name, detail)
    return 0 if all(c for _, c, _ in ok) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--boot", type=int, default=N_BOOT)
    ap.add_argument("--block", type=int, default=BLOCK)
    ap.add_argument("--procs", type=int, default=max(1, min(8, (os.cpu_count() or 4) - 6)))
    ap.add_argument("--shard", default=None)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.cmd == "blocks":
        if a.check:
            return check_blocks()
        face, out = blocks_face()
        print(face["reading"])
        print(f"-> {out.relative_to(ROOT)}")
        return 0
    if a.cmd == "voltail":
        if a.check:
            return check_voltail()
        face, out = voltail_face(boot=a.boot, procs=a.procs)
        print(face["reading"])
        print(f"-> {out.relative_to(ROOT)}")
        return 0
    if a.check:
        return check()
    if a.cmd == "derive":
        doc, out = derive_series()
        print(f"series {doc['bars']} bars to {doc['evidence_cutoff']} -> "
              f"{out.relative_to(ROOT)} (cagr {doc['backtest']['full']['cagr']:.4f}, "
              f"sharpe {doc['backtest']['full']['sharpe']:.3f})")
        return 0
    env = run(boot=a.boot, block=a.block, procs=a.procs, shard=a.shard)
    if "reading" in env:
        print(env["reading"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())