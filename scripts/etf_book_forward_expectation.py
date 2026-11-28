"""Was the first five weeks of the live book a normal five weeks?

r2229. `results/etf_book_forward/LEDGER.json` is the production candidate's own
forward record: 26 bars from the 2026-10-23 seed, nav 0.988622, drawdown
-2.70%. Its `drift` block proves the marks re-derive and its `caveats` block
says what the backtest cannot see. Nothing on disk answers the question a
reader actually asks when a live number is red:

    is this what the book does all the time, or is something broken?

A power statement is *not* that answer. `etf_book_forward.power_table` answers
"how many bars before this ledger could resolve the edge" (7,758 bars at the
8.46%/yr excess dispersion). That is the right answer to a different question,
and it reads like a shrug to someone staring at a loss. This face answers the
narrow question the reader has today: given a 26-bar window already spent, how
often does this book's own history produce a window this bad?

Method (no new engine, no new data):
  * re-derive the same production book over its full history with the same
    state machine the ledger uses (`etf_book_forward.Forward`), so the
    distribution and the live record come from one implementation;
  * take every historical window of the same length (26 bars = 25 returns) and
    measure two things: the window's total return, and the deepest drawdown
    reached inside it;
  * report where the live window sits in each distribution, at four lengths so
    the reader can see whether the answer depends on the window he picked;
  * report the same for the benchmark spread (the book minus its four-exposure
    basket), because a book can lose money and still be doing its job;
  * report how long the book usually stays under water after reaching this
    depth, which is the number that decides whether to wait or to act.

Honest limits, printed in the face rather than left to the reader:
  * 26 bars is a short sample; the overlapping count (~1,648) is not 1,648
    independent trials. The disjoint count (~63) is, and both are printed.
  * the book pools today's listed ETFs, so the equity sleeve still carries
    survivorship (inherited caveat, not introduced here).
  * a window that is inside the historical range is *not* evidence the book is
    fine; it is evidence that nothing today distinguishes the two.

Output: results/etf_book_forward/expectation.json
        research/ETF_FORWARD_EXPECTATION.md

Usage:
    python scripts/etf_book_forward_expectation.py run
    python scripts/etf_book_forward_expectation.py check
    python scripts/etf_book_forward_expectation.py selftest

Exploratory measurement; no verdict on the book, no ledger booking.
"""
import argparse
import hashlib
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np                                                  # noqa: E402
import pandas as pd                                                 # noqa: E402

import etf_book_forward as F                                        # noqa: E402
import etf_robust_pf as R                                           # noqa: E402

OUT_DIR = os.path.join(ROOT, "results", "etf_book_forward")
OUT_JSON = os.path.join(OUT_DIR, "expectation.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_FORWARD_EXPECTATION.md")

HORIZONS = ((21, "4 weeks"), (26, "5 weeks (the live window)"), (42, "8 weeks"),
            (63, "3 months"))
RECOVERY_DEPTHS = (0.0114, 0.0270)      # the live loss, the live drawdown
RANGE_LINE_LO = 0.05                    # worse than the worst 5% of windows
RANGE_LINE_HI = 0.95                    # better than the best 95%
ART = "<!-- expectation-rows -->"       # marker pair (text, never a NUL: r1022 坑)


# ---------------------------------------------------------------- pure helpers
def window_returns(nav, h):
    """Total returns of every overlapping h-bar window (h-1 returns each)."""
    out = []
    n = len(nav)
    if h < 2:
        return out
    for i in range(0, n - h + 1):
        a, b = nav[i], nav[i + h - 1]
        if a > 0 and b > 0:
            out.append(b / a - 1.0)
    return out


def window_drawdown(nav, h):
    """Deepest drawdown inside every overlapping h-bar window (<= 0)."""
    out = []
    n = len(nav)
    if h < 2:
        return out
    for i in range(0, n - h + 1):
        peak = nav[i]
        worst = 0.0
        for j in range(i, i + h):
            if nav[j] > peak:
                peak = nav[j]
            if peak > 0:
                dd = nav[j] / peak - 1.0
                if dd < worst:
                    worst = dd
        out.append(worst)
    return out


def disjoint_stride(n, h):
    """Window starts for the independent (non-overlapping) sample."""
    return list(range(0, max(0, n - h + 1), h))


def share_at_or_below(values, x):
    """Empirical CDF: fraction of windows at or below x.  None when empty."""
    vals = [v for v in values if v is not None and np.isfinite(v)]
    if not vals:
        return None
    return sum(1 for v in vals if v <= x) / float(len(vals))


def share_at_or_worse_dd(values, dd):
    """Fraction of windows whose deepest drawdown is at least as deep as dd."""
    vals = [v for v in values if v is not None and np.isfinite(v)]
    if not vals:
        return None
    return sum(1 for v in vals if v <= dd) / float(len(vals))


def describe(values):
    """Five-number summary plus the tails.  Empty -> None, never zeros (r98 族)."""
    vals = [float(v) for v in values if v is not None and np.isfinite(v)]
    if not vals:
        return None
    a = np.asarray(vals, dtype=float)
    return {
        "n": int(a.size),
        "mean": round(float(a.mean()), 6),
        "sd": round(float(a.std(ddof=1)), 6) if a.size > 1 else None,
        "p05": round(float(np.percentile(a, 5)), 6),
        "p10": round(float(np.percentile(a, 10)), 6),
        "p25": round(float(np.percentile(a, 25)), 6),
        "median": round(float(np.median(a)), 6),
        "p75": round(float(np.percentile(a, 75)), 6),
        "p90": round(float(np.percentile(a, 90)), 6),
        "p95": round(float(np.percentile(a, 95)), 6),
        "min": round(float(a.min()), 6),
        "max": round(float(a.max()), 6),
    }


def recovery_episodes(nav, depth):
    """Bars spent under water by each episode that reached `depth`.

    Returns (recovered_bars, censored).  A censored episode is one still under
    water when the series ends: its duration is unknown, not zero.
    """
    recovered = []
    censored = 0
    if not nav:
        return recovered, censored
    peak = nav[0]
    in_ep = False
    start = 0
    for i, v in enumerate(nav):
        if peak > 0:
            dd = v / peak - 1.0
            if not in_ep and dd <= -depth:
                in_ep, start = True, i
            elif in_ep and v >= peak:
                recovered.append(i - start)
                in_ep = False
        if v > peak:
            peak = v
    if in_ep:
        censored = 1
    return recovered, censored


def classify(share):
    """Where the live window sits, in words a reader can act on."""
    if share is None:
        return "UNMEASURED"
    if share <= RANGE_LINE_LO:
        return "WORSE_THAN_THE_WORST_5_PERCENT"
    if share >= RANGE_LINE_HI:
        return "BETTER_THAN_THE_BEST_95_PERCENT"
    return "INSIDE_THE_USUAL_RANGE"


def one_in(share):
    """`1 in N` framing; None when the share cannot carry one."""
    if share is None or share <= 0:
        return None
    return int(round(1.0 / share))


# ---------------------------------------------------------------- the live record
def read_ledger(path=None):
    path = path or F.LEDGER
    with open(path, "rb") as fh:
        raw = fh.read()
    doc = json.loads(raw.decode("utf-8"))
    bars = doc.get("bars") or []
    nav = [float(b["nav"]) for b in bars if isinstance(b.get("nav"), (int, float))]
    dds = [float(b["dd"]) for b in bars if isinstance(b.get("dd"), (int, float))]
    return {
        "path": os.path.relpath(path, ROOT).replace("\\", "/"),
        "sha256": hashlib.sha256(raw).hexdigest()[:16],
        "bars": len(bars),
        "first_bar": bars[0]["bar"] if bars else None,
        "last_bar": bars[-1]["bar"] if bars else None,
        "nav": nav,
        "nav_last": nav[-1] if nav else None,
        "total_return": (nav[-1] / nav[0] - 1.0) if len(nav) > 1 and nav[0] > 0 else None,
        "dd_last": dds[-1] if dds else None,
        "dd_series": dds,
        "cash_last": bars[-1].get("cash") if bars else None,
        "status": doc.get("status"),
        "config": doc.get("config") or {},
        "book_in_force": doc.get("book_in_force") or {},
        "caveats": doc.get("caveats") or [],
    }


def live_uniqueness(nav):
    """Two identical bars in a row would mean the ledger stopped pricing."""
    if len(nav) < 3:
        return None
    same = sum(1 for i in range(1, len(nav)) if nav[i] == nav[i - 1])
    return {"flat_bars": same, "share": round(same / float(len(nav) - 1), 4)}


# ---------------------------------------------------------------- the backtest
def prepare():
    """One panel load, one grid, one carry tape -- both arms ride it."""
    close, openp, amt, feats, score, cls, n_flip = F.build_inputs()
    px = close.ffill()
    op = openp.reindex(columns=close.columns)
    dates, rebal_days = F.date_grid(px, F.CONFIG["rebal"])
    try:
        carry_ser, carry_note = F.build_carry(dates)
    except Exception as exc:                                     # noqa: BLE001
        print("carry tape unavailable (%s) -- carry arm equals the parity arm" % exc,
              file=sys.stderr)
        carry_ser, carry_note = None, "unavailable"
    return {"px": px, "op": op, "score": score, "dates": dates,
            "rebal_days": rebal_days, "carry": carry_ser, "carry_note": carry_note,
            "n_flip": n_flip}


def run_arm(prep, carry_on):
    """The same production book over its full history; carry on or off."""
    state = F.Forward(prep["px"], prep["op"], prep["score"], F.CONFIG["n_hold"],
                      F.CONFIG["rebal"], F.CONFIG["cost_per_side"],
                      vol_target=F.CONFIG["vol_target"],
                      carry=(prep["carry"] if carry_on else None))
    marks = state.run(prep["dates"], prep["rebal_days"])
    ser = pd.Series({d: m["nav"] for d, m in marks}).sort_index()
    cash = pd.Series({d: m.get("cash", np.nan) for d, m in marks}).sort_index()
    return {"nav": ser, "cash": cash, "n_fill": state.n_fill,
            "mean_turnover": state.mean_turnover}


def series_faces(nav):
    """CAGR / vol / sharpe / max drawdown on a nav series (annualised, 244 bars)."""
    a = np.asarray(nav, dtype=float)
    if a.size < 3:
        return None
    rets = a[1:] / a[:-1] - 1.0
    yrs = (a.size - 1) / F.BARS_PER_YEAR
    cagr = (a[-1] / a[0]) ** (1.0 / yrs) - 1.0 if yrs > 0 and a[0] > 0 else None
    sd = float(np.std(rets, ddof=1)) * np.sqrt(F.BARS_PER_YEAR)
    sharpe = (float(np.mean(rets)) * F.BARS_PER_YEAR / (float(np.std(rets, ddof=1))
              * np.sqrt(F.BARS_PER_YEAR))) if np.std(rets, ddof=1) > 0 else None
    peak, mdd = a[0], 0.0
    for v in a:
        if v > peak:
            peak = v
        if peak > 0 and v / peak - 1.0 < mdd:
            mdd = v / peak - 1.0
    return {
        "bars": int(a.size),
        "cagr": round(float(cagr), 6) if cagr is not None else None,
        "vol_annual": round(sd, 6),
        "sharpe": round(float(sharpe), 4) if sharpe is not None else None,
        "max_drawdown": round(float(mdd), 6),
    }


def horizon_block(nav, live, h, label):
    """Everything the reader needs at one window length."""
    rets = window_returns(nav, h)
    dds = window_drawdown(nav, h)
    starts = disjoint_stride(len(nav), h)
    d_ret, d_dd = [], []
    for i in starts:
        seg = nav[i:i + h]
        d_ret.extend(window_returns(seg, h))
        d_dd.extend(window_drawdown(seg, h))
    live_ret = live.get("total_return")
    live_dd = live.get("dd_last")
    share_ret = share_at_or_below(rets, live_ret) if live_ret is not None else None
    share_dd = (share_at_or_worse_dd(dds, live_dd)
                if live_dd is not None else None)
    return {
        "bars": h,
        "label": label,
        "returns": describe(rets),
        "drawdowns": describe(dds),
        "disjoint": {"n": len(d_ret), "returns": describe(d_ret),
                     "drawdowns": describe(d_dd)},
        "live_return": None if live_ret is None else round(live_ret, 6),
        "live_dd": None if live_dd is None else round(live_dd, 6),
        "share_as_bad_or_worse": None if share_ret is None else round(share_ret, 5),
        "one_in_returns": one_in(share_ret),
        "share_dd_as_deep_or_deeper": None if share_dd is None else round(share_dd, 5),
        "one_in_drawdown": one_in(share_dd),
        "verdict_return": classify(share_ret),
        "verdict_drawdown": classify(share_dd),
    }


def excess_block(nav, bench, live_ex, h, label):
    """Book minus basket, same windows: losing money and still doing the job."""
    if bench is None or len(bench) != len(nav):
        return None
    ex = np.asarray(nav, dtype=float) / np.asarray(bench, dtype=float) - 1.0
    if not np.all(np.isfinite(ex)):
        return None
    tape = 1.0 + ex
    wins = window_returns(list(tape), h)
    share = share_at_or_below(wins, live_ex) if live_ex is not None else None
    return {
        "bars": h,
        "label": label,
        "windows": describe(wins),
        "live_excess": None if live_ex is None else round(live_ex, 6),
        "share_as_bad_or_worse": None if share is None else round(share, 5),
        "verdict": classify(share),
    }


def build():
    live = read_ledger()
    prep = prepare()
    arm_on = run_arm(prep, True)          # the ruler: the ledger books cash carry
    arm_off = run_arm(prep, False)        # counterfactual: same book, cash earns nothing
    book = arm_on
    nav = [float(v) for v in book["nav"].tolist()]
    bench = None
    try:
        base = str(book["nav"].index[0].date())      # bench_block rebases on a BAR STRING
        blk = F.bench_block(prep["dates"], prep["rebal_days"], base)
        bench = [b["nav"] for b in blk["bars"]]
    except Exception as exc:                                     # noqa: BLE001
        print("benchmark unavailable (%s) -- excess arm unmeasured, not zero"
              % exc, file=sys.stderr)
        bench = None
    live_bench = None
    live_ex = None
    if bench and len(bench) == len(nav):
        # the ledger's window, not the whole grid: both arms rebased at the live seed bar
        try:
            i0 = [str(d.date()) for d in prep["dates"]].index(live["first_bar"])
        except (ValueError, TypeError):
            i0 = None
        if i0 is not None and nav[i0] > 0 and bench[i0] > 0:
            live_bench = bench[-1] / bench[i0]
            # the live arm is the ledger's own nav path (seeded at 1.0), not the backtest's
            lived = live["nav_last"] if live["nav_last"] else nav[-1]
            live_ex = lived / live_bench - 1.0
    elif bench:
        print("benchmark has %d bars against the book's %d -- excess arm unmeasured"
              % (len(bench), len(nav)), file=sys.stderr)
        bench = None

    hz = {}
    for h, label in HORIZONS:
        hz[str(h)] = horizon_block(nav, live, h, label)

    ex = {}
    for h, label in HORIZONS:
        blk = excess_block(nav, bench, live_ex, h, label)
        if blk:
            ex[str(h)] = blk

    live_rets = [live["nav"][i] / live["nav"][i - 1] - 1.0
                 for i in range(1, len(live["nav"])) if live["nav"][i - 1] > 0]
    live_vol = (round(float(np.std(live_rets, ddof=1)) * np.sqrt(F.BARS_PER_YEAR), 6)
                if len(live_rets) > 2 else None)
    rec = {}
    for depth in RECOVERY_DEPTHS:
        got, censored = recovery_episodes(nav, depth)
        rec["%0.4f" % depth] = {
            "depth": depth,
            "episodes": len(got) + censored,
            "recovered": len(got),
            "censored_still_under_water": censored,
            "median_bars": int(np.median(got)) if got else None,
            "p90_bars": int(np.percentile(got, 90)) if got else None,
            "max_bars": int(max(got)) if got else None,
            "share_within_63": (round(sum(1 for g in got if g <= 63) / float(len(got)), 4)
                                if got else None),
        }

    block = hz.get("26") or {}
    block_ex = ex.get("26") or {}
    depth1 = rec.get("%0.4f" % RECOVERY_DEPTHS[0]) or {}
    verdict = {
        "return_reading": block.get("verdict_return"),
        "drawdown_reading": block.get("verdict_drawdown"),
        "one_in_returns": block.get("one_in_returns"),
        "one_in_drawdown": block.get("one_in_drawdown"),
        "sentence": None,
    }
    if block.get("share_as_bad_or_worse") is not None:
        parts = [
            "The live book is %.2f%% after %d bars (%s to %s). In this book's own "
            "history, %.1f%% of %d-bar windows ended at or below that, i.e. roughly "
            "one window in %s; the drawdown of %.2f%% was matched or exceeded by "
            "%.1f%% of windows (one in %s)."
            % (100.0 * (live["total_return"] or 0.0), live["bars"],
               live["first_bar"], live["last_bar"],
               100.0 * block["share_as_bad_or_worse"], block["bars"],
               block.get("one_in_returns") or "never",
               100.0 * abs(live["dd_last"] or 0.0),
               100.0 * (block.get("share_dd_as_deep_or_deeper") or 0.0),
               block.get("one_in_drawdown") or "never")]
        if block_ex.get("live_excess") is not None:
            parts.append(
                "Against a plain four-ETF basket the same window is %s, which sits at "
                "the %.1f%% mark of the book's own excess windows."
                % ("%+.2fpp" % (100.0 * block_ex["live_excess"]),
                   100.0 * (block_ex.get("share_as_bad_or_worse") or 0.0)))
        if depth1.get("median_bars"):
            parts.append(
                "Reaching this depth has happened %d times since %s; the book came back "
                "in a median of %d bars (%s%% within a quarter), so the honest expectation "
                "is weeks under water, not days."
                % (depth1.get("episodes", 0), str(book["nav"].index[0].date()),
                   depth1["median_bars"],
                   "%.0f" % (100.0 * (depth1.get("share_within_63") or 0.0))))
        verdict["sentence"] = " ".join(parts)

    # the ruler: which arm the live path is on, decided by the ledger's own bars
    carry_bars = 0
    try:
        with open(os.path.join(ROOT, live["path"]), encoding="utf-8") as fh:
            raw = json.load(fh)
        carry_bars = sum(1 for b in (raw.get("bars") or [])
                         if (b.get("carry") or 0) > 0)
        cfg_says = (raw.get("config") or {}).get("cash")
    except (OSError, ValueError):
        carry_bars, cfg_says = 0, None
    off_faces = series_faces([float(v) for v in arm_off["nav"].tolist()])
    on_faces = series_faces(nav)
    ruler = {
        "live_books_cash_carry": carry_bars > 0,
        "live_bars_with_carry": carry_bars,
        "live_bars": live["bars"],
        "ledger_config_cash_field": cfg_says,
        "carry_on_face": on_faces,
        "carry_off_face": off_faces,
        "gap_cagr_pp": (None if not (on_faces and off_faces) else
                        round(100.0 * (on_faces["cagr"] - off_faces["cagr"]), 3)),
        "note": (None if cfg_says is None else
                 "the ledger's `config.cash` field (%r) contradicts its own bars: %d of %d "
                 "book a positive carry, and its `engine.cash_leg` says the repo ladder is "
                 "charged. This face reads the bars, and says so rather than picking the "
                 "string." % (cfg_says, carry_bars, live["bars"])),
    }

    return {
        "schema": "etf-book-forward-expectation/v1",
        "evidence_cutoff": live["last_bar"],
        "generated_ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "live": {
            "ledger": live["path"],
            "ledger_sha256_16": live["sha256"],
            "bars": live["bars"],
            "first_bar": live["first_bar"],
            "last_bar": live["last_bar"],
            "nav_last": round(float(live["nav_last"]), 8),
            "total_return": None if live["total_return"] is None
            else round(live["total_return"], 6),
            "drawdown_last": None if live["dd_last"] is None
            else round(live["dd_last"], 6),
            "cash_last": live["cash_last"],
            "open_names": len((live["book_in_force"] or {}).get("names") or []),
            "scale_in_force": (live["book_in_force"] or {}).get("scale"),
            "realised_vol_annual": live_vol,
            "flat_bars": live_uniqueness(live["nav"]),
        },
        "ruler": ruler,
        "backtest": {
            "engine": "etf_book_forward.Forward (the same state machine the ledger runs)",
            "config": dict(F.CONFIG),
            "carry": "on (the arm the live path is on; see `ruler`)",
            "carry_note": prep["carry_note"],
            "first_bar": str(book["nav"].index[0].date()),
            "last_bar": str(book["nav"].index[-1].date()),
            "faces": on_faces,
            "mean_cash_share": round(float(np.nanmean(book["cash"].values)), 4),
            "n_fills": book["n_fill"],
            "mean_turnover": round(float(book["mean_turnover"]), 4),
            "panel_flips_repaired": prep["n_flip"],
        },
        "horizons": hz,
        "excess_vs_basket": ex,
        "recovery": rec,
        "verdict": verdict,
        "caveats": [
            "26 bars is five weeks. The overlapping window count is not a sample size; "
            "the disjoint count is, and both are printed.",
            "The pool is today's listed ETFs, so the equity sleeve still carries "
            "survivorship (inherited from the backtest, not introduced here).",
            "A window inside the historical range is not evidence the book is fine -- it "
            "is evidence that nothing in these five weeks separates it from the backtest.",
            "The live book is running at %s annualised vol against an 8.00%% target on a "
            "26-bar estimate: the vol window is the one number this face cannot separate "
            "from noise at this length."
            % ("-" if live_vol is None else "%.2f%%" % (100.0 * live_vol)),
            "Research output, not an investment recommendation.",
        ],
    }


# ---------------------------------------------------------------- rendering
def _pct(x, dp=2):
    return "-" if x is None else ("%+.*f%%" % (dp, 100.0 * x))


def _plain(x, dp=2):
    """Magnitudes (vol, cash share) have no sign to report."""
    return "-" if x is None else ("%.*f%%" % (dp, 100.0 * x))


def render_md(doc):
    liv = doc["live"]
    bt = doc["backtest"]["faces"] or {}
    lines = []
    lines.append("# Was the live book's first five weeks normal?")
    lines.append("")
    lines.append("generated %s · cutoff %s · ledger %s (sha16 %s)"
                 % (doc["generated_ts"], doc["evidence_cutoff"],
                    liv["ledger"], liv["ledger_sha256_16"]))
    lines.append("")
    lines.append(ART)
    lines.append("")
    lines.append("## The record")
    lines.append("")
    lines.append("| | live | backtest, whole history |")
    lines.append("|---|---|---|")
    lines.append("| bars | %d (%s to %s) | %d (%s to %s) |"
                 % (liv["bars"], liv["first_bar"], liv["last_bar"],
                    bt.get("bars"), doc["backtest"]["first_bar"],
                    doc["backtest"]["last_bar"]))
    lines.append("| total return | %s | CAGR %s |"
                 % (_pct(liv["total_return"]),
                    _pct(bt.get("cagr")) if bt.get("cagr") is not None else "-"))
    lines.append("| drawdown | %s | worst %s |"
                 % (_pct(liv["drawdown_last"]), _pct(bt.get("max_drawdown"))))
    lines.append("| annualised vol | %s | %s |"
                 % (_plain(liv["realised_vol_annual"]), _plain(bt.get("vol_annual"))))
    lines.append("| cash share | %s | mean %s |"
                 % (_plain(liv["cash_last"]), _plain(doc["backtest"]["mean_cash_share"])))
    lines.append("")
    r = doc.get("ruler") or {}
    lines.append("## Which ruler")
    lines.append("")
    lines.append("The ledger books cash carry on %d of its %d bars, so the distribution "
                 "below is the carry-on arm; the same book with cash earning nothing "
                 "earns %s a year against %s, i.e. the ladder is worth %s pp/yr and is "
                 "not a rounding error."
                 % (r.get("live_bars_with_carry", 0), r.get("live_bars", 0),
                    _pct((r.get("carry_off_face") or {}).get("cagr")),
                    _pct((r.get("carry_on_face") or {}).get("cagr")),
                    r.get("gap_cagr_pp")))
    if r.get("note"):
        lines.append("")
        lines.append("Self-contradiction found in the ledger, reported not patched: "
                     + r["note"])
    lines.append("")
    lines.append("## Where the live window sits")
    lines.append("")
    lines.append("| window | windows | live return | at or below | one in | "
                 "live drawdown | as deep or deeper | one in |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for key in sorted(doc["horizons"], key=int):
        h = doc["horizons"][key]
        r = h["returns"] or {}
        lines.append("| %s | %s (%s disjoint) | %s | %s | %s | %s | %s | %s |"
                     % (h["label"], r.get("n", "-"), h["disjoint"]["n"],
                        _pct(h["live_return"]),
                        _plain(h["share_as_bad_or_worse"], 1),
                        h["one_in_returns"] or "-",
                        _pct(h["live_dd"]),
                        _plain(h["share_dd_as_deep_or_deeper"], 1),
                        h["one_in_drawdown"] or "-"))
    lines.append("")
    lines.append("## Book minus its four-exposure basket")
    lines.append("")
    if doc["excess_vs_basket"]:
        lines.append("| window | windows | live excess | at or below | verdict |")
        lines.append("|---|---|---|---|---|")
        for key in sorted(doc["excess_vs_basket"], key=int):
            e = doc["excess_vs_basket"][key]
            lines.append("| %s | %s | %s | %s | %s |"
                         % (e["label"], (e["windows"] or {}).get("n", "-"),
                            _pct(e["live_excess"]),
                            _plain(e["share_as_bad_or_worse"], 1), e["verdict"]))
    else:
        lines.append("unmeasured this round (benchmark arm unavailable) -- not zero.")
    lines.append("")
    lines.append("## How long the book stays under water")
    lines.append("")
    lines.append("| depth reached | episodes | recovered | median bars | p90 bars | "
                 "share back within 63 bars |")
    lines.append("|---|---|---|---|---|---|")
    for key in sorted(doc["recovery"]):
        r = doc["recovery"][key]
        lines.append("| %s | %d | %d | %s | %s | %s |"
                     % ("%.2f%% deep" % (100.0 * r["depth"]), r["episodes"],
                        r["recovered"],
                        r["median_bars"] if r["median_bars"] is not None else "-",
                        r["p90_bars"] if r["p90_bars"] is not None else "-",
                        _plain(r["share_within_63"], 1)))
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    lines.append(doc["verdict"]["sentence"] or "unmeasured")
    lines.append("")
    lines.append("## What this does not say")
    lines.append("")
    for c in doc["caveats"]:
        lines.append("- " + c)
    lines.append("")
    lines.append(ART)
    return "\n".join(lines) + "\n"


def _rows_of(text):
    """The generated section, without the marker lines (for byte comparison)."""
    if text.count(ART) < 2:
        return None
    parts = text.split(ART)
    return parts[1]


# ---------------------------------------------------------------- commands
def cmd_run(args):
    doc = build()
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_md(doc))
    v = doc["verdict"]
    print("EXPECTATION %s  live %s over %d bars  cutoff %s"
          % (doc["evidence_cutoff"], _pct(doc["live"]["total_return"]),
             doc["live"]["bars"], doc["evidence_cutoff"]))
    print("  return reading   : %s (one in %s windows)"
          % (v["return_reading"], v["one_in_returns"] or "-"))
    print("  drawdown reading : %s (one in %s windows)"
          % (v["drawdown_reading"], v["one_in_drawdown"] or "-"))
    print("  -> %s" % (v["sentence"] or "unmeasured"))
    print("  face: %s" % os.path.relpath(OUT_JSON, ROOT))
    return 0


def cmd_check(args):
    """Published rows vs the world; drift says STALE, self-contradiction says FAILED."""
    problems = []
    stale = []
    if not os.path.exists(OUT_JSON):
        print("STALE face missing: %s -- nothing published yet" %
              os.path.relpath(OUT_JSON, ROOT))
        return 3
    with open(OUT_JSON, encoding="utf-8") as fh:
        doc = json.load(fh)
    live = read_ledger()
    if doc["live"]["ledger_sha256_16"] != live["sha256"]:
        stale.append("ledger moved (face priced %s, disk is %s)"
                     % (doc["live"]["ledger_sha256_16"], live["sha256"]))
    if doc["live"]["bars"] != live["bars"]:
        stale.append("ledger bar count %s != %s"
                     % (doc["live"]["bars"], live["bars"]))
    if doc["live"]["last_bar"] != live["last_bar"]:
        stale.append("ledger last bar %s != %s"
                     % (doc["live"]["last_bar"], live["last_bar"]))
    if live["nav_last"] and abs(doc["live"]["nav_last"] - round(live["nav_last"], 8)) > 1e-8:
        stale.append("ledger nav moved %.8f -> %.8f"
                     % (doc["live"]["nav_last"], live["nav_last"]))
    # self-contradiction: the face's own arithmetic, re-derived from its own rows
    for key, h in doc["horizons"].items():
        if h["share_as_bad_or_worse"] is not None:
            want = classify(h["share_as_bad_or_worse"])
            if want != h["verdict_return"]:
                problems.append("horizon %s says %s but its own share %.5f reads %s"
                                % (key, h["verdict_return"],
                                   h["share_as_bad_or_worse"], want))
        if h["returns"] is None:
            problems.append("horizon %s has no window summary" % key)
    if os.path.exists(OUT_MD):
        with open(OUT_MD, encoding="utf-8") as fh:
            md = fh.read()
        want = render_md(doc)
        got_rows, want_rows = _rows_of(md), _rows_of(want)
        if got_rows is None:
            problems.append("markdown lost its generated-section markers")
        elif got_rows != want_rows:
            problems.append("markdown rows do not reproduce from the face "
                            "(hand-edited numbers)")
    else:
        stale.append("markdown face missing")
    if problems:
        print("CHECK FAILED\n  " + "\n  ".join(problems))
        return 4
    if stale:
        print("STALE " + "; ".join(stale))
        return 3
    print("OK evidence_cutoff=%s ledger=%s horizons=%d"
          % (doc["evidence_cutoff"], doc["live"]["ledger_sha256_16"],
             len(doc["horizons"])))
    return 0


def _selfcheck():
    """Behaviour legs on hand-built series: every predicate gets a negative control."""
    fails = []

    def leg(name, cond):
        if not cond:
            fails.append(name)

    nav = [1.0, 1.0, 1.0, 1.0]
    leg("flat series -> zero window returns",
        all(abs(r) < 1e-12 for r in window_returns(nav, 3)))
    up = [1.0, 1.1, 1.2, 1.3]
    leg("rising series -> positive windows", window_returns(up, 3)[0] > 0.19)
    leg("falling window is caught",
        window_returns([1.0, 0.9, 0.8], 3)[0] < -0.19)
    leg("drawdown of a dip is negative only inside the dip",
        window_drawdown([1.0, 0.98, 0.99], 3)[0] < -0.019)
    leg("drawdown of a monotone climb is zero",
        window_drawdown([1.0, 1.01, 1.02], 3)[0] == 0.0)
    leg("disjoint stride picks non-overlapping starts",
        disjoint_stride(10, 3) == [0, 3, 6])
    leg("disjoint windows do not overlap by construction",
        len(window_returns([float(i) for i in range(1, 11)], 3)) == 8)
    leg("share_at_or_below is a CDF, not a rank from the top",
        abs(share_at_or_below([-0.1, 0.0, 0.1], 0.0) - 2 / 3.0) < 1e-12)
    leg("share at the minimum is not zero (it is 1/n)",
        abs(share_at_or_below([-0.1, 0.0, 0.1], -0.1) - 1 / 3.0) < 1e-12)
    leg("dd share counts deeper-or-equal, not only equal",
        abs(share_at_or_worse_dd([-0.05, -0.02, 0.0], -0.02) - 2 / 3.0) < 1e-12)
    leg("empty input -> None, never zeros (r98 family)",
        describe([]) is None and share_at_or_below([], 0.0) is None)
    leg("classification: outside the low tail is named",
        classify(0.01) == "WORSE_THAN_THE_WORST_5_PERCENT")
    leg("classification: inside is named", classify(0.5) == "INSIDE_THE_USUAL_RANGE")
    leg("classification: top tail is named",
        classify(0.99) == "BETTER_THAN_THE_BEST_95_PERCENT")
    leg("one_in of 0.5 is 2", one_in(0.5) == 2)
    leg("one_in of zero is None, not infinity",
        one_in(0.0) is None and one_in(None) is None)
    got, cens = recovery_episodes([1.0, 0.95, 0.96, 1.0, 1.01], 0.03)
    leg("recovery counts the bars spent under water", got == [2] and cens == 0)
    got, cens = recovery_episodes([1.0, 0.95, 0.96, 0.97], 0.03)
    leg("an episode still under water is censored, not counted as zero",
        got == [] and cens == 1)
    got, cens = recovery_episodes([1.0, 0.99, 1.0], 0.03)
    leg("a dip shallower than the depth opens no episode", got == [] and cens == 0)
    faces = series_faces([1.0, 1.0, 1.0, 1.0])
    leg("a flat series has zero vol and no sharpe",
        faces["vol_annual"] == 0.0 and faces["sharpe"] is None)
    leg("series_faces refuses a two-point series", series_faces([1.0, 1.1]) is None)
    # a face whose own rows contradict its verdict must be caught by cmd_check
    h = horizon_block([1.0 + 0.001 * i for i in range(60)],
                      {"total_return": -0.5, "dd_last": -0.5}, 26, "test")
    leg("a loss worse than every window reads as the low tail",
        h["verdict_return"] == "WORSE_THAN_THE_WORST_5_PERCENT")
    leg("its share is 0, not None",
        h["share_as_bad_or_worse"] == 0.0)
    leg("one_in of a zero share is None, so the sentence cannot say 'one in 0'",
        h["one_in_returns"] is None)
    return fails


def cmd_selftest(args):
    fails = _selfcheck()
    if fails:
        print("SELFTEST FAILED (%d)" % len(fails))
        for f in fails:
            print("  - " + f)
        return 4
    print("SELFTEST OK")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("run", help="derive the face")
    r.set_defaults(func=cmd_run)
    c = sub.add_parser("check", help="published rows vs the world")
    c.set_defaults(func=cmd_check)
    s = sub.add_parser("selftest", help="offline behaviour legs")
    s.set_defaults(func=cmd_selftest)
    args = ap.parse_args(argv)
    if not getattr(args, "func", None):
        ap.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
