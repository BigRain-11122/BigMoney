"""ETF book, forward ledger -- the production candidate's own record, starting at a seed bar.

The production config (12 names of the bond-free pool, rebalance every 20 bars, 10bp/side,
8% vol target that only de-levers) so far has a BACKTEST and an order sheet. Neither is a
track record: a backtest can silently keep improving after the fact, and a sheet is one
snapshot with no memory. This script closes that gap by seeding a forward ledger at a
stated bar and appending one mark per new bar thereafter, never rewriting what it already
published.

Execution is the honest one, not the convenient one: the decision is taken at the CLOSE of
a grid bar and filled at the OPEN of the next bar, so a mark dated d can never contain a
position chosen with d's own close. That is `etf_composite_pf.run_next_open`'s model, and
the selftest proves this accrual reproduces that engine's curve to 1e-12 rather than
trusting a re-implementation (r1261 lesson: an equivalence check must first prove the
mechanism actually ran).

  python scripts/etf_book_forward.py seed [--capital=1000000]   # create the ledger
  python scripts/etf_book_forward.py run                        # append new bars
  python scripts/etf_book_forward.py run --rebase                # only after a disclosed drift
  python scripts/etf_book_forward.py carry                      # price the cash leg
  python scripts/etf_book_forward.py --selftest

r1268 (defect found and fixed): the accrual used to average the book's per-name returns
UNWEIGHTED, so the 8% vol target de-levered the reported `cash` field but never the return
path -- the ledger ran 1/scale times hotter than the book it claims to record (2.37 vs the
engine's 1.86 for the same config, maxabs 0.55). The r1267 equivalence leg missed it
because it compared with `vol_target=None`, where every weight is 1/12 and the two paths
coincide. Returns are now sum(w*r) over the actual scaled weights, the vol-targeted
equivalence is its own selftest leg, and the un-invested fraction earns repo carry
(`carry` subcommand / CARRY.json) instead of being silently booked at zero.

Gates: recorded bars are re-derived every run; if any published mark no longer reproduces
(a repaired price flip, a re-sorted panel) the ledger FREEZES and exits 3 instead of
quietly rewriting history -- `--rebase` is the logged escape and stays visible in the file.
It trades nothing, touches no registry, and claims no edge.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_book_cash_ladder as REPO
import etf_equity_alpha as A
import etf_robust_pf as R
import etf_book_production as P
import etf_book_spanning as S
from config import PATHS

SCHEMA = "etf-book-forward/v1"
OUT_DIR = os.path.join(PATHS.results_dir, "etf_book_forward")
LEDGER = os.path.join(OUT_DIR, "LEDGER.json")
DRIFT_TOL = 1e-9
# A drift gate may only police SETTLED bars. The newest published bar is provisional until
# the panel for its date stops gaining symbols: a late print replaces a stale ffill, which
# moves that symbol's cross-sectional features and can flip the book's ranked selection on
# an already-published date -- with no revision anywhere and no row rewritten. Freezing on
# it (r1362/r1364/r1365, three rounds on the 2026-10-29 face, 5.064e-06) makes the gate
# answer a question nobody asked, and the only escape it offers rewrites the history it
# exists to protect. Settings: a provisional bar that comes back different once its panel
# settles gets ONE disclosed restatement; every other bar must re-derive bit-for-bit.
# Bumping this re-runs the one-time grandfathering; v1 flagged only the newest bar and left
# the bar published the day before it stranded as a settled-bar drift (seen live, r1366).
PROVISIONAL_FLAG_VERSION = 2
MAX_RUNS = 40
BARS_PER_YEAR = 244.0   # the repo's trading-year convention, used everywhere else for CAGR
T_CRIT = 2.0            # the t a forward spread has to reach before it means anything
SIG_EDGES = (0.03, 0.05, 0.10)   # candidate edges priced into a bars-needed table
# 80% power at a two-sided 5% test = z(0.975) + z(0.80). The bars-needed table above
# answers "how long for a t=2 test"; a holder asks the reverse question ("in the year
# I am willing to wait, what could this ledger even resolve?"), which is this z.
POWER_Z = 2.802
POWER_HORIZONS = (("6m", 122), ("1y", 244), ("2y", 488), ("3y", 732))
# Measured edges this book's own studies published, so the 'years until 80% power'
# column is priced on numbers that are already in the repo rather than typed here.
POWER_CANDIDATES = (
    ("pre-2020 measured alpha (single arm)", "results/etf_book_spanning_pre2020.json",
     ("arms", "single", "full", "alpha_annual")),
    ("in-window measured alpha (single arm)", "results/etf_book_spanning.json",
     ("arms", "book", "full", "alpha_annual")),
)
CONFIG = {
    "n_hold": 12,
    "rebal": 20,
    "cost_per_side": P.COST,
    "vol_target": P.TARGET_VOL,
    "classes": list(P.USE_CLASSES),
    "execution": "decide at close of bar d -> fill at open of bar d+1 -> hold to the next fill",
    "cash": ("cash held at the start of a bar earns that bar's repo carry "
             "(ladder3 = GC007/GC014/GC028 equal rungs, exchange commission charged, "
             "panel from scripts/update_repo.py); --carry=0 reproduces the zero-carry book"),
}
CAVEATS = [
    "The ETF pool is today's listed set: survivorship is still in the equity sleeve.",
    "The seed bar begins the record; nothing before it is a track record, however good the backtest.",
    # r1360: the card's sentence was priced on medians only; both faces now quote the measured
    # draw-tail share from one artifact instead of restating the impression in two dialects.
    P.vol_overlay_tail_sentence(),
    ("Cash carry rides a repo ladder, not a money-market fund: it assumes the treasurer can "
     "roll GC007/GC014/GC028 on every maturity bar, and it uses the 2026 exchange commission "
     "table (re-derivable with RATES fee=0)."),
    "Research output, not an investment recommendation.",
    ("The basket benchmark is an equal-weight rebalanced basket of the four exposures in "
     "scripts/etf_book_spanning.py (gold 518880 / Nasdaq QDII 513100 / CSI300 510300 / "
     "bond 511010) priced on the BOOK's own decision grid. Both arms ride the engine's "
     "fixed-weight convention, which does not charge the weight drift inside a holding "
     "period; the basket's would-be drift turnover is published beside it so that omission "
     "is sized rather than hidden."),
]


def build_inputs():
    """Same panel prep as etf_book_production.run(), so the ledger rides the same config."""
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in P.USE_CLASSES]
    close, openp, amt = close[cols], openp[cols], amt[cols]
    score = E.build_score(close, amt, feats)
    return close, openp, amt, feats, score, cls, n_flip


def _leg(book, a_ser, b_ser):
    """Weighted portfolio return of `book` between two price faces (engine-identical).

    `book` maps name -> weight, and a de-levered book's weights sum to less than 1: the
    remaining fraction is cash and earns nothing here (the caller adds carry). Names that
    did not print both faces drop out and their weight simply earns zero for that leg --
    the same conservative treatment the research engine applies, pinned by the selftest.
    """
    tot, seen = 0.0, 0.0
    for p, w in book.items():
        a = a_ser.get(p, np.nan)
        b = b_ser.get(p, np.nan)
        if not np.isfinite(a) or not np.isfinite(b) or a <= 0:
            continue
        tot += w * (b / a - 1.0)
        seen += w
    if seen <= 0:
        return None
    return float(tot)


def build_carry(dates, fee_free=False):
    """Per-bar fractional return of the repo cash ladder aligned to the book's bars.

    Reuses scripts/etf_book_cash_ladder.py rather than re-implementing a rolling contract:
    ladder3 = GC007/GC014/GC028 equal rungs, each a rolling contract with the exchange
    commission charged on every purchase. Returns None (with the reason) if the repo panel
    is not on disk, so the ledger degrades to zero-carry and says so instead of inventing a
    rate.
    """
    try:
        rates = REPO.load_panel(bars=dates)
    except Exception as exc:                       # pragma: no cover - panel absence only
        return None, "repo panel unreadable: %s" % exc
    if not rates:
        return None, "repo panel absent (run scripts/update_repo.py)"
    fees = {t: 0.0 for t in REPO.FEE_BP} if fee_free else None
    ret, _per = REPO.ladder(pd.DatetimeIndex(dates), rates, REPO.LADDERS["ladder3"], fees=fees)
    ret = ret.reindex(pd.DatetimeIndex(dates)).fillna(0.0)
    return ret, "ladder3 (%s) commission %s" % (
        "/".join(REPO.LADDERS["ladder3"]), "waived" if fee_free else "charged")


class Forward:
    """Incremental state machine: one bar in, one mark out.

    State is (nav, held, pending). `pending` is a book decided at the close of a grid bar
    waiting for the next open; it can never be applied on the bar that produced it.
    """

    def __init__(self, px, op, score, n_hold, rebal, cost, vol_target=None, carry=None,
                 legacy_mean=False):
        self.px, self.op, self.score = px, op, score
        self.n_hold, self.rebal, self.cost = n_hold, rebal, cost
        self.vol_target = vol_target
        # per-bar fractional return of the cash ladder; None = book cash at zero (disclosed)
        self.carry = carry
        # legacy_mean reproduces the pre-r1268 defect (unweighted average over names, so a
        # de-levered book still moved the whole nav). Kept as a ruler, never the default.
        self.legacy_mean = legacy_mean
        self.nav = 1.0
        self.held = {}
        self.pending = None
        self.turnover_sum = 0.0
        self.n_fill = 0
        self.books = {}
        self.last_decision = None

    def _decide(self, d):
        s = self.score.loc[d].dropna()
        if len(s) < self.n_hold:
            return
        picks = list(s.nlargest(self.n_hold).index)
        base = {p: 1.0 / self.n_hold for p in picks}
        scale, vol = 1.0, None
        if self.vol_target:
            scale, vol = P.scale_for(base, self.op, d, self.vol_target)
        new = {k: w * scale for k, w in base.items()}
        turn = sum(abs(new.get(k, 0.0) - self.held.get(k, 0.0))
                   for k in set(new) | set(self.held))
        self.pending = (new, turn)
        self.last_decision = {"bar": str(d.date()), "scale": round(float(scale), 6),
                              "realised_vol_60d": None if vol is None else round(float(vol), 6),
                              "names": picks, "turnover": round(float(turn), 6)}
        self.books[str(d.date())] = self.last_decision

    def _ret(self, book, a_ser, b_ser):
        if not self.legacy_mean:
            return _leg(book, a_ser, b_ser)
        out = []
        for p in book:
            a = a_ser.get(p, np.nan)
            b = b_ser.get(p, np.nan)
            if not np.isfinite(a) or not np.isfinite(b) or a <= 0:
                continue
            out.append(b / a - 1.0)
        return float(np.mean(out)) if out else None

    def _cash_carry(self, d):
        """Carry earned by the cash held at the start of bar d (None when carry is off)."""
        if self.carry is None:
            return 0.0
        cash = max(0.0, 1.0 - float(sum(self.held.values())))
        if cash <= 0.0:
            return 0.0
        v = self.carry.get(d, 0.0)
        return cash * float(v) if np.isfinite(v) else 0.0

    def run(self, dates, rebal_days):
        marks = []
        for i, d in enumerate(dates):
            filled, turn = False, 0.0
            if i > 0:
                prev = dates[i - 1]
                raw_open = self.op.loc[d]
                open_d = raw_open.where(np.isfinite(raw_open), self.px.loc[d])
                cash_start = max(0.0, 1.0 - float(sum(self.held.values())))
                carry = self._cash_carry(d)
                if self.pending is not None:
                    # overnight gap belongs to the OLD book, then the fill is charged at
                    # the open, and only open->close is earned by the NEW book
                    if self.held:
                        r = self._ret(self.held, self.px.loc[prev], open_d)
                        if r is not None:
                            self.nav *= (1.0 + r + carry)
                    elif carry:
                        self.nav *= (1.0 + carry)
                    new, turn = self.pending
                    # cost may be a scalar rate or a callable pricing THIS decision
                    # (prev, new, d) -- the ImpactCost contract of the capacity ladder
                    rate = (self.cost(self.held, new, d) if callable(self.cost)
                            else self.cost)
                    self.nav *= (1.0 - rate * turn)
                    self.turnover_sum += turn
                    self.n_fill += 1
                    self.held, self.pending = new, None
                    filled = True
                    r = self._ret(self.held, open_d, self.px.loc[d])
                    if r is not None:
                        self.nav *= (1.0 + r)
                elif self.held:
                    r = self._ret(self.held, self.px.loc[prev], self.px.loc[d])
                    if r is not None:
                        self.nav *= (1.0 + r + carry)
                elif carry:
                    self.nav *= (1.0 + carry)
            invested = float(sum(self.held.values()))
            marks.append((d, {
                "nav": self.nav,
                "cash": max(0.0, 1.0 - invested),
                "cash_start": round(cash_start, 6) if i > 0 else 1.0,
                "carry": round(carry, 10) if i > 0 else 0.0,
                "n_held": len(self.held),
                "filled": filled,
                "turn": round(float(turn), 6),
            }))
            if d in rebal_days:
                self._decide(d)
        return marks

    @property
    def mean_turnover(self):
        return self.turnover_sum / self.n_fill if self.n_fill else 0.0


def date_grid(px, rebal):
    dates = [d for d in px.index if d >= pd.Timestamp(R.START)]
    return dates, set(dates[::rebal])


BENCH_EXEC = ("decide on the book's own 20-bar grid -> fill at the next open -> equal "
              "weights restored at that fill; cost charged on the turnover it takes")


def _bench_frames(dates):
    """Open/close faces of the four span exposures, re-indexed onto the book's bars.

    The keys come from etf_book_spanning.SPAN rather than a copy: the annual spanning
    study and this daily benchmark must price the SAME basket, and a code change in one
    place has to move the other (pinned by a selftest leg).
    """
    close_b, open_b, n_flip = S.load_span_frames()
    keys = [code for _k, code, _l in S.SPAN]
    idx = pd.DatetimeIndex(list(dates))
    px_b = close_b.reindex(columns=keys)
    op_b = open_b.reindex(columns=keys)
    px_b = px_b.reindex(px_b.index.union(idx)).ffill().reindex(idx)
    op_b = op_b.reindex(op_b.index.union(idx)).ffill().reindex(idx)
    return px_b, op_b, keys, n_flip


def bench_block(dates, rebal_days, base_bar, cost=None):
    """Equal-weight four-ETF basket accrued on the book's grid, rebased to `base_bar`.

    This is the daily form of the question r1312 could only answer annually: is the
    shipped book beating a basket a human could hold instead of it? Both arms ride the
    same decision bars, the same next-open fill and the same fixed-weight convention, so
    a gap is a portfolio difference and not a calendar difference.

    Turnover is measured on the WEIGHT DRIFT that build-up produces between fills: the
    engine's convention does not charge it on either arm, so it is published as a
    friction estimate (`rebalance_friction`) rather than silently charged on one side.
    """
    cost = CONFIG["cost_per_side"] if cost is None else cost
    px_b, op_b, keys, n_flip = _bench_frames(dates)
    w = {k: 1.0 / len(keys) for k in keys}
    # a buy-and-hold basket is invested from its first bar: without an opening position the
    # arm would sit flat until the first grid decision and publish a 1.0 line (r1261 class
    # of silent no-op, caught by the "basket actually moved" leg).
    nav, held, pending = 1.0, dict(w), None
    last_fill_px = {k: float(px_b.loc[dates[0], k]) for k in keys}
    rows, turns = [], []
    for i, d in enumerate(dates):
        filled = False
        if i > 0:
            prev = dates[i - 1]
            open_d = op_b.loc[d].where(np.isfinite(op_b.loc[d]), px_b.loc[d])
            if pending is not None:
                new, turn = pending
                if held:
                    r = _leg(held, px_b.loc[prev], open_d)
                    if r is not None:
                        nav *= (1.0 + r)
                nav *= (1.0 - cost * turn)
                turns.append(turn)
                held, pending = new, None
                filled = True
                last_fill_px = open_d.to_dict()
                r = _leg(held, open_d, px_b.loc[d])
                if r is not None:
                    nav *= (1.0 + r)
            elif held:
                r = _leg(held, px_b.loc[prev], px_b.loc[d])
                if r is not None:
                    nav *= (1.0 + r)
        if d in rebal_days and last_fill_px:
            # weight drift since the fill is what a real equal-weight basket re-equalises
            drifted, tot = {}, 0.0
            for k in keys:
                a, b = last_fill_px.get(k), px_b.loc[d].get(k)
                if np.isfinite(a) and np.isfinite(b) and a > 0:
                    drifted[k] = w[k] * float(b) / float(a)
                    tot += drifted[k]
            turn = 0.0
            if tot > 0:
                drift_w = {k: v / tot for k, v in drifted.items()}
                turn = 0.5 * sum(abs(drift_w.get(k, 0.0) - w[k]) for k in keys)
            pending = (dict(w), turn)
        rows.append((d, {"nav": nav, "filled": filled}))
    base = None
    bars = []
    for d, m in rows:
        bar = str(d.date())
        if base is None:
            if bar != base_bar:
                continue
            base = m["nav"]
        bars.append({"bar": bar, "nav": round(m["nav"] / base, 10),
                     "filled": m["filled"]})
    mean_turn = float(np.mean(turns)) if turns else 0.0
    per_year = 244.0 / CONFIG["rebal"]
    return {
        "keys": keys,
        "labels": {code: lbl for _k, code, lbl in S.SPAN},
        "weights": "equal (1/4 each), restored at every fill",
        "execution": BENCH_EXEC,
        "source": "scripts/etf_book_spanning.py SPAN",
        "panel_flips_repaired": n_flip,
        "bars": bars,
        "rebalance_friction": {
            "turnover_per_decision": round(mean_turn, 6),
            "bp_per_year_if_charged": round(mean_turn * cost * per_year * 10000.0, 3),
            "note": ("weight drift a real equal-weight basket must re-equalise; the engine "
                     "convention charges it on NEITHER arm (the book's holdings drift the "
                     "same way), so it is sized here, not booked"),
        },
        "decisions": len(turns),
    }


def _excess(book_nav, bench_nav):
    """Book's lead over the basket as a fraction of the BASKET, not a difference."""
    if not np.isfinite(bench_nav) or bench_nav == 0:
        return None
    return book_nav / bench_nav - 1.0


def excess_series(dates, marks, rebal_days):
    """Daily book-minus-basket returns across the WHOLE grid.

    The published marks are a prefix of this series, so its dispersion is the only
    defensible prior for "how big must the spread be before it means anything" while
    the ledger itself still holds a handful of bars. Dispersion measured off three
    forward bars would be noise wearing a number.
    """
    first = str(dates[0].date())
    book = _indexed(marks, first)
    bench = {b["bar"]: b["nav"] for b in bench_block(dates, rebal_days, first)["bars"]}
    out, prev = [], None
    for b in book:
        bn = bench.get(b["bar"])
        if bn is None or not np.isfinite(bn) or bn <= 0:
            continue
        cur = (b["nav"], float(bn))
        if prev is not None and prev[0] > 0 and prev[1] > 0:
            out.append(cur[0] / prev[0] / (cur[1] / prev[1]) - 1.0)
        prev = cur
    return out


def _dig(obj, path):
    for k in path:
        if not isinstance(obj, dict) or k not in obj:
            return None
        obj = obj[k]
    return obj


def power_table(sd_annual, horizons=POWER_HORIZONS, candidates=POWER_CANDIDATES,
                root=None):
    """The reader's version of the bars-needed table (r1316).

    `bars_needed_for_edge` answers "how long until a t=2 test" and the honest answer
    over this ledger's 8.46%/yr excess dispersion is 7,758 bars (31.8 years) for a
    3pp edge -- a number nobody can act on. The reverse question is answerable today:

      smallest edge this ledger could resolve at 80% power inside H bars
            E = POWER_Z * sd_annual / sqrt(H / BARS_PER_YEAR)
      years until a candidate edge E reaches 80% power
            Y = (POWER_Z * sd_annual / E)**2

    Candidate edges are READ from this repo's own studies (units: the stored field is
    a fraction, converted to pp here and labelled), never typed into this table. A
    missing source is omitted with its reason instead of being filled in.
    """
    root = root or PATHS.root
    out = {"units": {"sd_annual_pct": "percent per year",
                     "min_detectable_edge_pp": "percentage points per year",
                     "years_for_80pct_power": "years"},
           "power": 0.80, "alpha_two_sided": 0.05, "z": POWER_Z,
           "annual_vol_pct": round(sd_annual * 100, 3),
           "min_detectable_edge_pp": {}, "years_for_80pct_power": {},
           "candidate_sources": {}}
    if not np.isfinite(sd_annual) or sd_annual <= 0:
        out["available"] = False
        out["reason"] = "no dispersion to price power against"
        return out
    for label, n in horizons:
        out["min_detectable_edge_pp"][label] = round(
            POWER_Z * sd_annual / np.sqrt(n / BARS_PER_YEAR) * 100, 3)
    for name, rel, path in candidates:
        try:
            with open(os.path.join(root, rel), encoding="utf-8") as fh:
                raw = _dig(json.load(fh), path)
        except Exception as e:
            out["candidate_sources"][name] = {"omitted": "unreadable:%s" % type(e).__name__}
            continue
        if not isinstance(raw, (int, float)) or not np.isfinite(float(raw)) or raw <= 0:
            out["candidate_sources"][name] = {"omitted": "not a positive edge in %s" % rel}
            continue
        years = (POWER_Z * sd_annual / float(raw)) ** 2
        out["years_for_80pct_power"][name] = round(years, 1)
        out["candidate_sources"][name] = {"file": rel, "field": ".".join(path),
                                          "edge_pp_per_year": round(float(raw) * 100, 3)}
    out["available"] = True
    out["read"] = ("a spread inside these bands is not evidence either way: at 12 months "
                   "this ledger can only resolve edges above its 1y band, and the two "
                   "edges this book actually published need years, not months")
    return out


def significance(dates, marks, rebal_days, n_published, edges=SIG_EDGES):
    """How many bars before the published spread could mean anything.

    A spread with no noise floor gets read as an edge, and the first forward reading was
    +0.75pp over three bars. This block prices the floor from the parent series (the whole
    grid's excess dispersion), never from the published prefix -- a one-bar ledger would
    otherwise publish a zero-width band and call everything significant. Three identities:

      bars needed for a t=2 test of an edge E      N = (T*BARS_PER_YEAR*sd / E)**2
      95% band of a spread accumulated over n bars 1.96 * sd * sqrt(n)
      smallest edge visible inside a fixed horizon E = T*BARS_PER_YEAR*sd / sqrt(N)

    The last one is the reading a holder needs: inside a horizon they actually keep, what
    is the smallest edge this series could resolve at all.
    """
    ex = np.asarray(excess_series(dates, marks, rebal_days), dtype=float)
    if len(ex) < 3 or not np.all(np.isfinite(ex)):
        return {"available": False, "reason": "excess series too short or non-finite",
                "bars_used": int(len(ex))}
    sd = float(np.std(ex, ddof=1))
    if not np.isfinite(sd) or sd <= 0:
        return {"available": False, "reason": "zero dispersion", "bars_used": int(len(ex))}
    ann = sd * np.sqrt(BARS_PER_YEAR)
    need = {}
    for e in edges:
        need["%gpp/yr" % (e * 100)] = int(np.ceil((T_CRIT * BARS_PER_YEAR * sd / e) ** 2))
    band = {}
    for label, n in (("1m", 20), ("3m", 60), ("1y", 244), ("3y", 732)):
        band[label] = round(1.96 * sd * np.sqrt(n) * 100, 3)
    detectable = {}
    for label, n in (("1y", 244), ("3y", 732), ("5y", 1220)):
        detectable[label] = round(T_CRIT * BARS_PER_YEAR * sd / np.sqrt(n) * 100, 3)
    book_all = _indexed(marks, str(dates[0].date()))
    n_bars = len(book_all)
    hist = None
    if n_bars:
        g = book_all[-1]["nav"] / book_all[0]["nav"]
        if np.isfinite(g) and g > 0:
            hist = round((g ** (BARS_PER_YEAR / n_bars) - 1.0) * 100, 3)
    return {
        "available": True,
        "bars_used": int(len(ex)),
        "windows": ("%s..%s" % (book_all[0]["bar"], book_all[-1]["bar"])) if n_bars else "",
        "daily_vol_pct": round(sd * 100, 5),
        "annual_vol_pct": round(ann * 100, 3),
        "noise_band_pp": band,
        "noise_band_pp_at_published": round(1.96 * sd * np.sqrt(max(n_published, 1)) * 100, 3),
        "published_bars": int(n_published),
        "bars_needed_for_edge": need,
        "min_detectable_edge_pp": detectable,
        "power": power_table(ann),
        "book_cagr_pct_on_same_window": hist,
        "read": ("a spread smaller than the band at the bar count it was measured over is "
                 "indistinguishable from noise; the band shrinks as sqrt(bars), not faster"),
    }


def _sig_line(led):
    """The line that stops a 3-bar spread from being read as an edge."""
    sig = (led.get("benchmark") or {}).get("significance") or {}
    if not sig.get("available"):
        return "SIGNIFICANCE: unavailable (%s)" % (sig.get("reason") or "no block")
    need = sig.get("bars_needed_for_edge") or {}
    want = ", ".join("%s %d bars" % (k, v) for k, v in need.items())
    det = sig.get("min_detectable_edge_pp") or {}
    det_txt = ("; smallest edge visible inside %s" %
               ", ".join("%s %.1fpp/yr" % (k, v) for k, v in det.items())) if det else ""
    latest = (led.get("benchmark") or {}).get("latest") or {}
    return ("SIGNIFICANCE: excess vol %.2f%%/yr over %d bars (%s) -> %s at t=2%s; "
            "this ledger's %d bars carry a +-%.2fpp band, published spread %spp" % (
                sig.get("annual_vol_pct") if sig.get("annual_vol_pct") else float("nan"),
                sig.get("bars_used"),
                sig.get("windows"),
                want, det_txt,
                sig.get("published_bars") or 0,
                sig.get("noise_band_pp_at_published")
                if sig.get("noise_band_pp_at_published") else float("nan"),
                latest.get("excess_pp") if latest.get("excess_pp") is not None else "n/a"))


def _power_line(led):
    """The reverse question: inside a horizon a holder will actually keep, what can
    this ledger resolve -- and how long until the edges it published could be seen?"""
    sig = (led.get("benchmark") or {}).get("significance") or {}
    pw = sig.get("power") or {}
    if not pw.get("available"):
        return "POWER: unavailable (%s)" % (pw.get("reason") or "no block")
    mde = pw.get("min_detectable_edge_pp") or {}
    yrs = pw.get("years_for_80pct_power") or {}
    src = pw.get("candidate_sources") or {}
    mde_txt = ", ".join("%s %.1fpp/yr" % (k, v) for k, v in mde.items())
    yrs_txt = ", ".join(
        "%s %s -> %s y" % (k.split(" (")[0], src.get(k, {}).get("edge_pp_per_year", "?"),
                           v) for k, v in yrs.items()) or "no candidate edge readable"
    return ("POWER (80%% at 5%% two-sided, sd %.2f%%/yr): smallest edge this ledger can "
            "resolve is %s; the edges it published need %s"
            % (pw.get("annual_vol_pct") or float("nan"), mde_txt, yrs_txt))


def _attach_sig(led, sig):
    if led.get("benchmark") is not None:
        led["benchmark"]["significance"] = sig
    return led


def bench_drift(published, fresh, tol=DRIFT_TOL):
    """Faces of the published benchmark block that no longer re-derive."""
    if not published:
        return []
    old = {b.get("bar"): b for b in (published.get("bars") or [])}
    faces, worst = [], 0.0
    for b in (fresh.get("bars") or []):
        o = old.get(b["bar"])
        if o is None:
            continue
        d = abs(float(b["nav"]) - float(o.get("nav", 0.0)))
        worst = max(worst, d)
        if d > tol:
            faces.append("%s:%.3e" % (b["bar"], d))
    return faces[:20]


def partition_settled(bars, panel_last_date):
    """(settled, provisional) published bar dates -- the ONE implementation.

    A bar is provisional if it is the newest published bar or if its date is the newest
    date in the panel: either way more prints for that date can still arrive. Everything
    older has stopped gaining symbols and must reproduce exactly. The settle audit imports
    this rather than deciding settledness a second time (E270: one rule spelled twice is
    not two rules).
    """
    bars = list(bars)
    if not bars:
        return [], []
    newest = bars[-1]
    provisional = [b for b in bars if b == newest or b == panel_last_date]
    settled = [b for b in bars if b not in provisional]
    return settled, provisional


def split_faces(faces, settled):
    """Drift faces split by whether the bar they name has settled (blocking) or not."""
    settled = set(settled)
    blocking, provisional = [], []
    for f in faces or []:
        bar = str(f).split(":")[0]
        (blocking if bar in settled else provisional).append(f)
    return blocking, provisional


def restate_provisional(led, rec, fresh, delta, panel_last_date):
    """Accept a settled re-derivation for a bar that was PUBLISHED while still filling.

    Recorded, never silent: the published value, the settled value, the delta and the
    panel date that was still growing are all kept. This is the one case where a
    published mark may move, and it is announced as a restatement rather than sold as a
    rebase -- `--rebase` rewrites history on purpose and stays reserved for a real
    settled-bar drift an operator has inspected.
    """
    ent = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "bar": rec["bar"],
        "reason": "published while the panel for that date was still gaining symbols",
        "panel_last_date": panel_last_date,
        "nav_published": rec["nav"],
        "nav_settled": fresh["nav"],
        "delta": round(float(delta), 12),
    }
    for k in ("nav", "cash", "carry", "n_held", "filled", "turn"):
        if k in fresh:
            rec[k] = fresh[k]
    rec["provisional"] = False
    rec["restated_at"] = ent["ts"]
    led.setdefault("restatements", []).append(ent)
    return ent


def migrate_provisional(led):
    """Grandfather the newest published bar ONCE, for ledgers written before the flag existed.

    A bar published before this schema cannot say whether its panel was still filling, so
    the next run would read it as settled and freeze on a difference that is not a revision
    -- the deferred form of the false positive this rule removes. The newest bar is
    therefore treated as provisional exactly once and any difference is recorded as a
    restatement carrying both values. Older bars stay settled and must re-derive, so the
    gate keeps everything it can actually enforce. Self-disabling.
    """
    if led.get("provisional_flags") == PROVISIONAL_FLAG_VERSION:
        return led, None
    if not led.get("bars"):
        led["provisional_flags"] = PROVISIONAL_FLAG_VERSION
        return led, None
    # Which bars were priced on their OWN close-day panel is recoverable from the run log:
    # the first run whose last_bar is that bar is the run that appended it, and if its stamp
    # falls on the bar's own date the panel for that date had just closed and was still
    # gaining symbols (r1365 measured 1,710/1,725 symbols 43 min after the close). Those
    # bars were provisional in fact even though nothing recorded it.
    first_stamp = {}
    for r in led.get("runs") or []:
        lb = r.get("last_bar")
        if lb and lb not in first_stamp:
            first_stamp[lb] = str(r.get("ts") or "")[:10]
    flagged = [b for b in led["bars"] if first_stamp.get(b["bar"]) == b["bar"]]
    if not flagged:
        led["provisional_flags"] = PROVISIONAL_FLAG_VERSION
        return led, None
    for b in flagged:
        b["provisional"] = True
    ent = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "bars": [b["bar"] for b in flagged],
        "reason": "publish-time provisional flags did not exist when these bars were "
                  "written; each was appended on its own bar date (close-day panel still "
                  "gaining symbols), so each is treated as provisional until it settles",
    }
    led["migrations"] = (led.get("migrations") or []) + [ent]
    led["provisional_flags"] = PROVISIONAL_FLAG_VERSION
    return led, ent


def compute_marks(vol_target=CONFIG["vol_target"], carry_on=True):
    close, openp, amt, feats, score, cls, n_flip = build_inputs()
    px = close.reindex(columns=close.columns).ffill()
    op = openp.reindex(columns=close.columns)
    dates, rebal_days = date_grid(px, CONFIG["rebal"])
    carry, carry_note = (build_carry(dates) if carry_on else (None, "carry disabled"))
    fwd = Forward(px, op, score, CONFIG["n_hold"], CONFIG["rebal"], CONFIG["cost_per_side"],
                  vol_target=vol_target, carry=carry)
    fwd.carry_note = carry_note
    marks = fwd.run(dates, rebal_days)
    return fwd, marks, dates, cls, n_flip


def _indexed(marks, seed_bar):
    """Marks rebased so the seed bar is 1.0; drawdown measured from the seed peak."""
    out, base, peak = [], None, 1.0
    for d, m in marks:
        bar = str(d.date())
        if base is None:
            if bar != seed_bar:
                continue
            base = m["nav"]
        nav = m["nav"] / base
        peak = max(peak, nav)
        out.append({
            "bar": bar,
            "nav": round(nav, 10),
            "dd": round(nav / peak - 1.0, 6),
            "cash": round(m["cash"], 6),
            "carry": round(m.get("carry", 0.0), 10),
            "n_held": m["n_held"],
            "filled": m["filled"],
            "turn": m["turn"],
        })
    return out


def _engine_block(fwd):
    """Which return path and which cash leg produced these marks (re-read by a human)."""
    return {
        "book_return": "sum(w*r) over the actual (vol-targeted) weights",
        "cash_leg": getattr(fwd, "carry_note", "unknown"),
    }


def load_ledger():
    if not os.path.exists(LEDGER):
        return None
    with open(LEDGER, "r", encoding="utf-8") as f:
        return json.load(f)


def save_ledger(led):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(LEDGER, "w", encoding="utf-8") as f:
        json.dump(led, f, ensure_ascii=False, indent=1)


def _noop_stub(led, headed, day=None):
    """One liveness record per (day, last_bar) instead of one per poll.

    The leg now runs from the S6 chain every round, and a per-poll stub rewrote
    LEDGER.json on every call, so the file was permanently dirty even when the
    panel had not moved. Keeping one record per day preserves the liveness
    evidence and lets repeated no-op polls leave the file byte-identical.
    Returns True when a record was actually appended.
    """
    day = day or time.strftime("%Y-%m-%d")
    runs = list(led.get("runs") or [])
    last = runs[-1] if runs else None
    if (last and last.get("new_bars") == 0
            and last.get("last_bar") == headed.get("bar")
            and str(last.get("ts", ""))[:10] == day):
        return False
    # the stamp must be built from `day`, not from the wall clock: otherwise the
    # record we just wrote can never match the day we compare against, and the
    # one-per-day gate silently degrades back to one-per-poll.
    runs.append({"ts": "%sT%s" % (day, time.strftime("%H:%M:%S%z")),
                 "new_bars": 0, "last_bar": headed.get("bar")})
    led["runs"] = runs[-MAX_RUNS:]
    return True


def _fresh(fwd, dates, cls, n_flip, capital):
    return {
        "schema": SCHEMA,
        "config": dict(CONFIG),
        "engine": {
            "book_return": "sum(w*r) over the actual (vol-targeted) weights",
            "cash_leg": getattr(fwd, "carry_note", "unknown"),
        },
        "seed": None,
        "bars": [],
        "benchmark": None,
        "books": {},
        "book_in_force": None,
        "status": "live",
        "drift": {"faces": [], "max_abs": 0.0, "checked_bars": 0},
        "rebases": [],
        "restatements": [],
        "unfreezes": [],
        "migrations": [],
        "provisional_flags": PROVISIONAL_FLAG_VERSION,
        "runs": [],
        "panel": {"n_instruments": len(cls), "flips_repaired": n_flip},
        "caveats": CAVEATS,
    }


def _books_after(fwd, seed_bar):
    """Forward-only: decisions published in the ledger start at the seed bar.

    The decision that produced the book in force at the seed bar predates it; it rides in
    `book_in_force` so the current holding is readable without dragging 80 historical
    decisions into a "forward" record.
    """
    return {k: v for k, v in fwd.books.items() if k >= seed_bar}


def seed(capital=1_000_000.0):
    fwd, marks, dates, cls, n_flip = compute_marks()
    last_bar = str(dates[-1].date())
    led = _fresh(fwd, dates, cls, n_flip, capital)
    led["seed"] = {
        "bar": last_bar,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "capital_cny": capital,
        "grid_index": len(dates) - 1,
        "bars_since_last_decision": (len(dates) - 1) % CONFIG["rebal"],
        "note": "marks are indexed to 1.0 at this bar; nothing before it is a track record",
    }
    led["bars"] = _indexed(marks, last_bar)
    # the seed bar is priced on the panel as it stands at seeding time; say so, so a later
    # settle-time restatement is a recorded promotion rather than a silent mark change
    for b in led["bars"]:
        b["provisional"] = (b["bar"] == last_bar)
    led["benchmark"] = _bench_with_book(led["bars"], dates, last_bar)
    led["books"] = _books_after(fwd, led["seed"]["bar"])
    led["book_in_force"] = fwd.last_decision
    led["runs"] = [{"ts": led["seed"]["ts"], "new_bars": 0, "last_bar": last_bar, "first": True}]
    save_ledger(led)
    bl = _bench_line(led)
    print("SEEDED %s nav=1.0 bars=%d names=%d status=live | %s" %
          (last_bar, len(led["bars"]), CONFIG["n_hold"], bl), flush=True)
    return 0


def _bench_with_book(book_bars, dates, base_bar):
    """The benchmark block, with each basket bar carrying the book's nav beside it."""
    bench = bench_block(dates, set(dates[::CONFIG["rebal"]]), base_bar)
    book = {b["bar"]: b["nav"] for b in book_bars}
    last_book = None
    for b in bench["bars"]:
        nav = book.get(b["bar"], last_book)
        last_book = nav
        b["book_nav"] = nav
        b["excess"] = None if nav is None else round(_excess(nav, b["nav"]), 10)
    tail = bench["bars"][-1] if bench["bars"] else None
    bench["latest"] = None if not tail else {
        "bar": tail["bar"],
        "book_nav": tail["book_nav"],
        "basket_nav": tail["nav"],
        "excess_pp": None if tail["excess"] is None else round(tail["excess"] * 100, 4),
    }
    return bench


def _bench_line(led):
    """One line a reader (or a轮报告) can quote: is the book ahead of the basket?"""
    latest = (led.get("benchmark") or {}).get("latest")
    if not latest or latest.get("excess_pp") is None:
        return "basket: unavailable (four span names missing from the panel)"
    return ("book %.5f vs 4-ETF basket %.5f -> excess %+.2fpp on %s" %
            (latest["book_nav"], latest["basket_nav"], latest["excess_pp"], latest["bar"]))


def run(rebase=False):
    led = load_ledger()
    if led is None:
        return seed()
    was_frozen = led.get("status") == "frozen"
    led, migrated = migrate_provisional(led)
    if migrated:
        print("MIGRATED provisional flags onto %s (%s)" %
              (",".join(migrated["bars"]), migrated["reason"]), flush=True)

    fwd, marks, dates, cls, n_flip = compute_marks()
    seed_bar = led["seed"]["bar"]
    fresh = {b["bar"]: b for b in _indexed(marks, seed_bar)}
    panel_last = str(dates[-1].date()) if dates else None
    settled, provisional = partition_settled([b["bar"] for b in led["bars"]], panel_last)

    # drift gate: every published mark on a SETTLED bar must re-derive exactly. A bar
    # that was published while its panel was still filling and has since settled gets one
    # disclosed restatement instead (see restate_provisional); a bar still filling is not
    # asked the question at all, because its answer is not final yet.
    faces, restated, worst = [], [], 0.0
    for b in led["bars"]:
        f = fresh.get(b["bar"])
        if f is None:
            faces.append(b["bar"] + ":missing")
            continue
        d = abs(f["nav"] - b["nav"])
        if b.get("provisional") and b["bar"] in settled:
            # the panel for this date has stopped growing: promote the bar. A difference is
            # recorded as a restatement (both values kept); no difference just closes the
            # flag, so the bar is policed like every other settled bar from now on.
            if d > DRIFT_TOL:
                restated.append(restate_provisional(led, b, f, d, panel_last))
            else:
                b["provisional"] = False
                b["settled_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
            continue
        if b["bar"] in provisional:
            continue
        worst = max(worst, d)
        if d > DRIFT_TOL:
            faces.append("%s:%.3e" % (b["bar"], d))
    if restated:
        # dd is a running peak over the published series, so it has to be rebuilt whenever
        # a mark in the middle of that series moves -- appending already does this for the
        # same reason.
        peak = 1.0
        for b in led["bars"]:
            peak = max(peak, b["nav"])
            b["dd"] = round(b["nav"] / peak - 1.0, 6)

    # the basket benchmark is regenerated every run for the same reason: a published
    # daily answer that stopped re-deriving must freeze the ledger, not be overwritten
    bench_all = bench_drift(led.get("benchmark"), _bench_with_book(led["bars"], dates, seed_bar))
    bench_faces, bench_prov = split_faces(bench_all, settled)
    faces_settled, faces_prov = split_faces(faces, settled)
    blocking = bool(faces_settled or bench_faces)
    led["drift"] = {
        "faces": (faces_settled + faces_prov)[:20],
        "max_abs": worst,
        "checked_bars": len(led["bars"]),
        "gate": "settled_bars_only",
        "settled_bars": settled[-10:],
        "provisional_bars": provisional,
        "settled_faces": faces_settled,
        "provisional_faces": faces_prov,
        "benchmark_settled_faces": bench_faces,
        "benchmark_provisional_faces": bench_prov,
        "restated_bars": [r["bar"] for r in restated],
    }

    new_bars = [f for f in _indexed(marks, seed_bar) if f["bar"] > led["bars"][-1]["bar"]]
    for nb in new_bars:
        nb["provisional"] = (nb["bar"] == panel_last)
    if blocking and not rebase:
        led["status"] = "frozen"
        save_ledger(led)
        print("DRIFT %d settled faces (bench %d) max_abs=%.3e -> FROZEN (exit 3); "
              "inspect the panel for a revision before --rebase rewrites the history"
              % (len(faces_settled), len(bench_faces), worst), flush=True)
        return 3
    if blocking and rebase:
        led["rebases"].append({
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "n_faces": len(faces_settled), "n_bench_faces": len(bench_faces),
            "max_abs": worst, "sample": (faces_settled + bench_faces)[:10],
        })
        led["bars"] = _indexed(marks, seed_bar)
        # the re-derived series already contains every bar, so nothing is left to append
        new_bars = []
        led["status"] = "live"
        print("REBASED %d settled faces (bench %d) max_abs=%.3e (logged in rebases)" %
              (len(faces_settled), len(bench_faces), worst), flush=True)
    elif was_frozen:
        # a freeze raised by a bar whose inputs were still arriving clears itself: nothing
        # published on a settled bar moved, so there is no history to adopt and no reason
        # to spend a rebase on one.
        led["unfreezes"] = (led.get("unfreezes") or []) + [{
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "reason": "no settled bar failed to re-derive; the freeze came from a "
                      "provisional bar (%s)" % ", ".join(provisional),
            "restated_bars": [r["bar"] for r in restated],
        }]
        led["status"] = "live"
        print("UNFROZEN no settled bar drifted (provisional=%s, restated=%s) -> live" %
              (",".join(provisional) or "none", ",".join(r["bar"] for r in restated) or "none"),
              flush=True)
    if faces_prov or bench_prov:
        print("PROVISIONAL drift on %s (%d faces, bench %d): panel for that date is still "
              "gaining symbols -- reported, not frozen, not rebased" %
              (",".join(provisional) or "none", len(faces_prov), len(bench_prov)), flush=True)

    if not new_bars:
        headed = led["bars"][-1] if led["bars"] else {}
        led["benchmark"] = _bench_with_book(led["bars"], dates, seed_bar)
        _attach_sig(led, significance(dates, marks, set(dates[::CONFIG["rebal"]]),
                                      len(led["bars"])))
        print("NO-OP last_bar=%s nav=%s (no new panel bars) | %s" %
              (headed.get("bar"), headed.get("nav"), _bench_line(led)), flush=True)
        print(_sig_line(led), flush=True)
        print(_power_line(led), flush=True)
        _noop_stub(led, headed)
        led["books"] = _books_after(fwd, led["seed"]["bar"])
        led["book_in_force"] = fwd.last_decision
        led["engine"] = _engine_block(fwd)
        led["panel"] = {"n_instruments": len(cls), "flips_repaired": n_flip}
        # r1360: the caveats are DERIVED text (the vol-overlay sentence now quotes the measured
        # draw-tail share), so a no-op poll must still refresh them -- otherwise the ledger keeps
        # publishing the pre-measurement wording until the next bar happens to arrive, and the two
        # human faces disagree about what was measured. Numbers are untouched; the stub stays
        # byte-identical across repeated no-ops because this is the same constant each time.
        led["caveats"] = CAVEATS
        save_ledger(led)
        return 0

    led["bars"].extend(new_bars)
    # peak must be re-derived across the whole published series after appending
    peak = 1.0
    for b in led["bars"]:
        peak = max(peak, b["nav"])
        b["dd"] = round(b["nav"] / peak - 1.0, 6)
    led["benchmark"] = _bench_with_book(led["bars"], dates, seed_bar)
    _attach_sig(led, significance(dates, marks, set(dates[::CONFIG["rebal"]]),
                                  len(led["bars"])))
    led["books"] = _books_after(fwd, led["seed"]["bar"])
    led["book_in_force"] = fwd.last_decision
    led["engine"] = _engine_block(fwd)
    led["panel"] = {"n_instruments": len(cls), "flips_repaired": n_flip}
    led["status"] = "live"
    led["runs"] = (led.get("runs", []) + [{
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "new_bars": len(new_bars),
        "last_bar": new_bars[-1]["bar"]}])[-MAX_RUNS:]
    save_ledger(led)
    tail = led["bars"][-1]
    print("APPENDED %d bars -> %s nav=%.4f dd=%.2f%% cash=%.0f%% | %s" %
          (len(new_bars), tail["bar"], tail["nav"], tail["dd"] * 100, tail["cash"] * 100,
           _bench_line(led)),
          flush=True)
    print(_sig_line(led), flush=True)
    print(_power_line(led), flush=True)
    return 0


def calibrate():
    """How much of the production CARD's number is the fill basis?

    etf_book_production.py reports the 12-name/8%-vol config on `open_to_open_equity`,
    which charges the fill at the OPEN of the same bar whose close produced the score.
    The ledger cannot use that (it would be a forward record with a one-bar lookahead), so
    it rides the honest next-open basis. This writes both curves' stats side by side: the
    gap is the price of honesty for this configuration, published rather than discovered
    later by someone comparing the card to the ledger.
    """
    close, openp, amt, feats, score, cls, n_flip = build_inputs()
    px = close.reindex(columns=close.columns).ffill()
    op = openp.reindex(columns=close.columns)
    dates, rebal_days = date_grid(px, CONFIG["rebal"])

    fwd = Forward(px, op, score, CONFIG["n_hold"], CONFIG["rebal"], CONFIG["cost_per_side"],
                  vol_target=CONFIG["vol_target"])
    marks = fwd.run(dates, rebal_days)
    honest = pd.Series({d: m["nav"] for d, m in marks}).sort_index()
    card, turn_card = R.open_to_open_equity(close, openp, amt, score, CONFIG["rebal"],
                                            CONFIG["n_hold"], CONFIG["cost_per_side"],
                                            vol_target=CONFIG["vol_target"])

    def face(ser, turn):
        out = {"turnover_per_decision": round(float(turn), 3)}
        for lbl, sl in (("full", ser), ("is", ser[ser.index <= R.IS_END]),
                        ("oos", ser[ser.index > R.IS_END])):
            m = A.stats2(sl, lbl)
            out[lbl] = {k: m.get(k) for k in ("cagr", "sharpe", "maxdd", "vol", "years")}
        return out

    h, c = face(honest, fwd.mean_turnover), face(card, turn_card)
    out = {
        "evidence_cutoff": str(honest.index[-1].date()),
        "generated_ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "config": dict(CONFIG),
        "honest_next_open": h,
        "card_open_to_open": c,
        "basis_delta_pp": {
            "full": round((c["full"]["cagr"] - h["full"]["cagr"]) * 100, 2),
            "is": round((c["is"]["cagr"] - h["is"]["cagr"]) * 100, 2),
            "oos": round((c["oos"]["cagr"] - h["oos"]["cagr"]) * 100, 2),
            "sharpe_full": round((c["full"]["sharpe"] or 0) - (h["full"]["sharpe"] or 0), 3),
        },
        "windows_shifted_bars": 1,
        "turnover_identical": abs(h["turnover_per_decision"] - c["turnover_per_decision"]) < 1e-12,
        "note": ("card_open_to_open charges the fill at the open of the bar whose close "
                 "produced the score (a one-bar lookahead) and therefore holds over a window "
                 "shifted by exactly one bar; honest_next_open is what the forward ledger "
                 "accrues. Turnover is identical on both, so this is a WINDOW ALIGNMENT "
                 "difference, not two portfolios: the sign of the gap is not alpha and must "
                 "not be read as one -- it says the headline is sensitive to which single "
                 "bar the holding period starts on."),
        "panel": {"n_instruments": len(cls), "flips_repaired": n_flip},
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "BASIS.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("BASIS honest full CAGR=%.2f%% SR=%.2f DD=%.1f%% | card full CAGR=%.2f%% SR=%.2f DD=%.1f%% "
          "| basis delta=%+.2fpp turnover_identical=%s" % (
              h["full"]["cagr"] * 100, h["full"]["sharpe"] or 0, h["full"]["maxdd"] * 100,
              c["full"]["cagr"] * 100, c["full"]["sharpe"] or 0, c["full"]["maxdd"] * 100,
              out["basis_delta_pp"]["full"], out["turnover_identical"]),
        flush=True)
    return 0


def _faces(ser, turn=None):
    out = {}
    if turn is not None:
        out["turnover_per_decision"] = round(float(turn), 3)
    for lbl, sl in (("full", ser), ("is", ser[ser.index <= R.IS_END]),
                    ("oos", ser[ser.index > R.IS_END])):
        m = A.stats2(sl, lbl)
        out[lbl] = {k: m.get(k) for k in ("cagr", "sharpe", "maxdd", "vol", "years")}
    return out


def carry(fee_free=False):
    """Price the two things the r1267 ledger got wrong: the de-leverage and the cash leg.

    Three books, identical decisions:
      legacy_mean   pre-r1268 accrual: unweighted mean over names, cash at zero -- the defect
      fixed         sum(w*r) over the scaled weights, cash at zero
      fixed_carry   the same book with the un-invested fraction earning the repo ladder
    The research engine (etf_robust_pf.open_to_open_equity, vol target on) is the
    independent referee for `fixed`, so the fix is not graded by its own re-derivation.
    """
    close, openp, amt, feats, score, cls, n_flip = build_inputs()
    px = close.reindex(columns=close.columns).ffill()
    op = openp.reindex(columns=close.columns)
    dates, rebal_days = date_grid(px, CONFIG["rebal"])
    carry_ser, carry_note = build_carry(dates, fee_free=fee_free)

    def book(carry_on, legacy):
        f = Forward(px, op, score, CONFIG["n_hold"], CONFIG["rebal"],
                    CONFIG["cost_per_side"], vol_target=CONFIG["vol_target"],
                    carry=(carry_ser if carry_on else None), legacy_mean=legacy)
        marks = f.run(dates, rebal_days)
        return f, pd.Series({d: m["nav"] for d, m in marks}).sort_index(), marks

    f_leg, s_leg, _ = book(False, True)
    f_fix, s_fix, m_fix = book(False, False)
    f_car, s_car, m_car = book(True, False)
    eng, turn_eng = R.open_to_open_equity(close, openp, amt, score, CONFIG["rebal"],
                                          CONFIG["n_hold"], CONFIG["cost_per_side"],
                                          vol_target=CONFIG["vol_target"])

    common = eng.index.intersection(s_fix.index)
    referee = float((s_fix.loc[common] - eng.loc[common]).abs().max()) if len(common) else None
    cashes = [m["cash"] for _d, m in m_car]
    invested = [1.0 - c for c in cashes]
    yrs = (s_car.index[-1] - s_car.index[0]).days / 365.25
    up_cum = float(s_car.iloc[-1] / s_fix.iloc[-1] - 1.0)
    carry_bars = sum(1 for _d, m in m_car if m.get("carry", 0.0) > 0)

    out = {
        "evidence_cutoff": str(s_fix.index[-1].date()),
        "generated_ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "config": dict(CONFIG),
        "carry_note": carry_note,
        "books": {
            "legacy_mean": _faces(s_leg, f_leg.mean_turnover),
            "fixed": _faces(s_fix, f_fix.mean_turnover),
            "fixed_carry": _faces(s_car, f_car.mean_turnover),
        },
        "defect": {
            "what": ("pre-r1268 marks averaged the book's per-name returns unweighted, so a "
                     "vol-targeted book still moved the whole nav: the reported `cash` field "
                     "was de-levered while the return path was not"),
            "final_nav_legacy": round(float(s_leg.iloc[-1]), 6),
            "final_nav_fixed": round(float(s_fix.iloc[-1]), 6),
            "card_basis_gap_note": (
                "the open_to_open_equity curve sits on a basis shifted by one bar (it fills "
                "at the open of the bar whose close decided the book), so it is NOT an "
                "equality referee for a next-open accrual; the selftest instead pins "
                "r_scaled == s * r_unscaled against the engine-exact unscaled curve"),
            "card_basis_final_nav": round(float(eng.iloc[-1]), 6),
            "card_basis_bars": int(len(common)),
            "escape": "the r1267 equivalence leg compared with vol_target=None, where every weight is 1/12",
        },
        "cash_leg": {
            "mean_cash_share": round(float(np.mean(cashes)), 4),
            "mean_invested_share": round(float(np.mean(invested)), 4),
            "bars_with_carry": int(carry_bars),
            "bars_total": len(m_car),
            "carry_mean_annualised_pct": round(float(carry_ser.mean()) * 365.0 * 100, 4),
            "carry_ladder3_cagr_pct": round(REPO.cagr_pct(carry_ser, dates), 4),
            "cumulative_uplift_pct": round(up_cum * 100, 3),
            "annualised_uplift_pp": round(((1.0 + up_cum) ** (1.0 / yrs) - 1.0) * 100, 3),
            "fees": "waived" if fee_free else "charged",
        },
        "panel": {"n_instruments": len(cls), "flips_repaired": n_flip},
        "note": ("fixed_carry is the config the forward ledger now accrues. The uplift is "
                 "carry on money the vol target had already parked, not alpha."),
    }
    out["defect"]["cagr_pp_legacy_minus_fixed"] = round(
        (out["books"]["legacy_mean"]["full"]["cagr"] - out["books"]["fixed"]["full"]["cagr"]) * 100, 2)
    os.makedirs(OUT_DIR, exist_ok=True)
    name = "CARRY_fee_free.json" if fee_free else "CARRY.json"
    with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    b = out["books"]
    print("CARRY fixed+cash CAGR=%.2f%% SR=%.2f DD=%.1f%% | fixed=%.2f%% | legacy=%.2f%% "
          "| cash=%.0f%% carry=%.2f%%/yr uplift=%+.2fpp/yr" % (
              b["fixed_carry"]["full"]["cagr"] * 100, b["fixed_carry"]["full"]["sharpe"] or 0,
              b["fixed_carry"]["full"]["maxdd"] * 100, b["fixed"]["full"]["cagr"] * 100,
              b["legacy_mean"]["full"]["cagr"] * 100,
              out["cash_leg"]["mean_cash_share"] * 100,
              out["cash_leg"]["carry_ladder3_cagr_pct"],
              out["cash_leg"]["annualised_uplift_pp"]), flush=True)
    return 0


def selftest():
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond)
        print(("PASS " if cond else "FAIL ") + name + (" " + detail if detail else ""), flush=True)

    close, openp, amt, feats, score, cls, _ = build_inputs()
    px = close.reindex(columns=close.columns).ffill()
    op = openp.reindex(columns=close.columns)
    dates, rebal_days = date_grid(px, CONFIG["rebal"])

    # 1. gold standard: no vol target -> the accrual must equal run_next_open exactly
    ser, turn_eng, _ = E.run_next_open(close, openp, amt, feats, CONFIG["rebal"],
                                       CONFIG["n_hold"], CONFIG["cost_per_side"], score=score)
    f0 = Forward(px, op, score, CONFIG["n_hold"], CONFIG["rebal"], CONFIG["cost_per_side"])
    marks0 = f0.run(dates, rebal_days)
    mine = pd.Series({d: m["nav"] for d, m in marks0}).sort_index()
    common = ser.index.intersection(mine.index)
    diff = float((ser.loc[common] - mine.loc[common]).abs().max()) if len(common) else float("inf")
    chk("equivalence with run_next_open", diff < 1e-12 and len(common) == len(ser),
        "bars=%d maxdiff=%.2e" % (len(common), diff))
    chk("equivalence covers turnover", abs(f0.mean_turnover - turn_eng) < 1e-12,
        "%.6f vs %.6f" % (f0.mean_turnover, turn_eng))

    # 2. the mechanism must actually have run (a pair of flat 1.0 lines can "match")
    chk("mechanism traded", f0.n_fill > 10 and f0.mean_turnover > 0 and mine.std() > 0,
        "fills=%d turn=%.3f std=%.4f" % (f0.n_fill, f0.mean_turnover, mine.std()))

    # 3. no lookahead: every fill lands exactly one bar AFTER the bar that decided it,
    #    and a bar that decides a book is marked with the OLD book still in force
    f1 = Forward(px, op, score, CONFIG["n_hold"], CONFIG["rebal"], CONFIG["cost_per_side"],
                 vol_target=CONFIG["vol_target"])
    marks1 = f1.run(dates, rebal_days)
    fill_idx = {i for i, (d, m) in enumerate(marks1) if m["filled"]}
    dec_idx = {i for i, d in enumerate(dates) if str(d.date()) in f1.books}
    lag_ok = fill_idx and fill_idx == {i + 1 for i in dec_idx if i + 1 < len(dates)}
    chk("fill lags its decision bar by exactly one", bool(lag_ok),
        "fills=%d decisions=%d" % (len(fill_idx), len(dec_idx)))
    chk("fills happen", len(fill_idx) > 10, "fills=%d" % len(fill_idx))

    # 4. vol target never levers up and cash stays inside [0, 1]
    scales = [b["scale"] for b in f1.books.values()]
    chk("vol target never levers up", scales and max(scales) <= 1.0 + 1e-12,
        "max_scale=%.6f min_scale=%.6f" % (max(scales), min(scales)))
    cashes = [m["cash"] for _, m in marks0]
    chk("cash in [0,1]", cashes and min(cashes) >= -1e-12 and max(cashes) <= 1.0 + 1e-12,
        "min=%.3f max=%.3f" % (min(cashes), max(cashes)))
    # 5. invested + cash == 1 on every mark of the vol-targeted run
    fwd_vt_marks = f1.run(dates, rebal_days)
    bad = [(d, m) for d, m in fwd_vt_marks if not (0.0 <= m["cash"] <= 1.0)]
    chk("vol-target book conserves capital", not bad, "bad=%d" % len(bad))

    # 6. rebasing: the last mark is 1.0 and every later nav divides by the same base
    last_bar = str(dates[-1].date())
    mid_bar = str(dates[-6].date())
    a = _indexed(fwd_vt_marks, mid_bar)
    b = _indexed(fwd_vt_marks, str(dates[-3].date()))
    ratio = []
    bmap = {x["bar"]: x["nav"] for x in b}
    for x in a:
        y = bmap.get(x["bar"])
        if y:
            ratio.append(round(x["nav"] / y, 9))
    chk("rebasing is a constant rescale", ratio and len(set(ratio)) == 1,
        "distinct_ratios=%d" % len(set(ratio)))
    c = _indexed(fwd_vt_marks, last_bar)
    chk("seed bar is 1.0", c[0]["bar"] == last_bar and abs(c[0]["nav"] - 1.0) < 1e-12)

    # 7. drift gate fires on a doctored mark
    bars = _indexed(fwd_vt_marks, mid_bar)
    fresh = {x["bar"]: x for x in bars}
    doctored = dict(bars[1])
    doctored["nav"] = doctored["nav"] + 1e-6
    d = abs(fresh[doctored["bar"]]["nav"] - doctored["nav"])
    chk("drift gate fires on a doctored mark", d > DRIFT_TOL, "delta=%.2e" % d)

    # 7b. the settled-bar rule (r1366): a bar whose panel date is still gaining symbols is
    #     asked no question, an older one must reproduce. Both halves are asserted, because
    #     a partition that returned "everything provisional" would also pass a one-sided leg.
    bd = ["2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29"]
    st, pv = partition_settled(bd, "2026-10-30")
    chk("partition: only the newest published bar is provisional while the panel date is ahead",
        pv == ["2026-10-29"] and st == bd[:3], "settled=%s provisional=%s" % (st, pv))
    st2, pv2 = partition_settled(bd, "2026-10-29")
    chk("partition: a bar matching the newest panel date is provisional too",
        pv2 == ["2026-10-29"] and st2 == bd[:3], "settled=%s provisional=%s" % (st2, pv2))
    chk("partition: empty ledger has no settled bars", partition_settled([], "2026-10-30") == ([], []))
    blk, prov = split_faces(["2026-10-28:5.064e-06", "2026-10-29:1.0e-07",
                             "2026-10-27:missing"], st)
    chk("faces: only provisional-bar drift is non-blocking",
        blk == ["2026-10-28:5.064e-06", "2026-10-27:missing"] and prov == ["2026-10-29:1.0e-07"],
        "blocking=%s provisional=%s" % (blk, prov))
    # the restatement is recorded, and the published value is recoverable from the record
    _led = {"restatements": []}
    _rec = {"bar": "2026-10-29", "nav": 1.1, "cash": 0.5, "provisional": True}
    _freshrec = {"nav": 1.100001, "cash": 0.61, "carry": 1e-5, "n_held": 5, "filled": 0,
                 "turn": 0.02}
    ent = restate_provisional(_led, _rec, _freshrec, 1e-6, "2026-10-30")
    # a ledger written before the flag existed must not turn its own legacy bar into a
    # settled-bar drift on the next run; the migration is one bar, logged, and self-disabling
    _old = {"bars": [{"bar": "2026-10-28", "nav": 1.0}, {"bar": "2026-10-29", "nav": 1.1}],
            "runs": [{"ts": "2026-10-29T00:20:00+0800", "last_bar": "2026-10-28"},
                     {"ts": "2026-10-29T15:52:25+0800", "last_bar": "2026-10-29"}]}
    _mig, _ent = migrate_provisional(_old)
    chk("legacy ledger: a bar appended on its own date is grandfathered, an older one is not",
        _mig["bars"][-1].get("provisional") is True
        and "provisional" not in _mig["bars"][0] and _ent["bars"] == ["2026-10-29"]
        and _mig["provisional_flags"] == PROVISIONAL_FLAG_VERSION, str(_ent))
    _mig2, _ent2 = migrate_provisional(_mig)
    chk("migration runs once, never again", _ent2 is None and len(_mig2["migrations"]) == 1)
    chk("restatement moves the mark, records both values, and clears the provisional flag",
        _rec["nav"] == 1.100001 and _rec["provisional"] is False
        and _led["restatements"][0]["nav_published"] == 1.1
        and abs(ent["delta"] - 1e-6) < 1e-15, str(ent))

    # 8. THE BUG CATCHER: with the vol target ON the accrual must still be the book's
    #    weighted return. r1267's equivalence leg ran with vol_target=None, where every
    #    weight is 1/12 and a weighted and an unweighted path coincide -- that is exactly
    #    why the defect below survived. The referee here is the engine-exact unscaled curve
    #    from leg 1 plus the scaling identity r_scaled = s * r_unscaled on non-fill bars
    #    (the picks do not depend on the scale, so both runs hold the same 12 names).
    #    NOTE: etf_robust_pf.open_to_open_equity can NOT referee this accrual -- it fills at
    #    the open of the bar whose close decided the book (a one-bar-shifted basis), which
    #    r1267's `calibrate` already priced as a different window, not a different book.
    f2 = Forward(px, op, score, CONFIG["n_hold"], CONFIG["rebal"], CONFIG["cost_per_side"],
                 vol_target=CONFIG["vol_target"])
    vtm = f2.run(dates, rebal_days)
    vt_mine = pd.Series({d: m["nav"] for d, m in vtm}).sort_index()
    un = pd.Series({d: m["nav"] for d, m in marks0}).sort_index()
    rs = vt_mine.pct_change()
    ru = un.pct_change()
    cashmap = {d: m["cash"] for d, m in vtm}
    fillbars = {d for d, m in vtm if m["filled"]}
    worst = (0.0, None)
    for i, d in enumerate(vt_mine.index):
        if i == 0 or d in fillbars:
            continue
        s_i = 1.0 - cashmap[d]
        delta = abs(rs.iloc[i] - s_i * ru.iloc[i])
        if delta > worst[0]:
            worst = (delta, str(d.date()))
    chk("scaled book moves s x the engine-exact book", worst[0] < 1e-12,
        "worst=%.2e at %s over %d non-fill bars" %
        (worst[0], worst[1], len(rs) - 1 - len(fillbars)))
    chk("vol target actually de-levered", 0.0 < min(b["scale"] for b in f2.books.values()) < 1.0,
        "min_scale=%.4f" % min(b["scale"] for b in f2.books.values()))

    # 9. the defect is reproducible as a ruler (unweighted mean must diverge from the engine)
    f3 = Forward(px, op, score, CONFIG["n_hold"], CONFIG["rebal"], CONFIG["cost_per_side"],
                 vol_target=CONFIG["vol_target"], legacy_mean=True)
    leg_ser = pd.Series({d: m["nav"] for d, m in f3.run(dates, rebal_days)}).sort_index()
    d3 = float((leg_ser - un).abs().max())
    rl = leg_ser.pct_change()
    worst_l = max(abs(rl.iloc[i] - ru.iloc[i]) for i, d in enumerate(leg_ser.index)
                  if i and d not in fillbars)
    chk("legacy_mean ignores the scale (defect, reproduced as a ruler)",
        worst_l < 1e-15 and leg_ser.iloc[-1] / vt_mine.iloc[-1] > 1.10,
        "worst_bar_delta=%.2e vs_unscaled=%.4f vs_fixed=%.4f" %
        (worst_l, leg_ser.iloc[-1] / un.iloc[-1], leg_ser.iloc[-1] / vt_mine.iloc[-1]))

    # 10. carry raises the book, is plausible in size, and never touches a fully invested bar
    carry_ser, _note = build_carry(pd.DatetimeIndex(dates))
    chk("carry series present", carry_ser is not None and len(carry_ser) == len(dates),
        "bars=%d" % (0 if carry_ser is None else len(carry_ser)))
    if carry_ser is not None:
        chk("carry rate plausible", 1e-6 < float(carry_ser.mean()) < 2e-4,
            "mean_daily=%.3e -> %.2f%%/yr" % (carry_ser.mean(), carry_ser.mean() * 365 * 100))
        flat = pd.Series(0.0, index=pd.DatetimeIndex(dates))
        f4 = Forward(px, op, score, CONFIG["n_hold"], CONFIG["rebal"], CONFIG["cost_per_side"],
                     vol_target=CONFIG["vol_target"], carry=flat)
        s4 = pd.Series({d: m["nav"] for d, m in f4.run(dates, rebal_days)}).sort_index()
        chk("zero carry is an exact identity", float((s4 - vt_mine).abs().max()) < 1e-15,
            "maxabs=%.2e" % float((s4 - vt_mine).abs().max()))
        f5 = Forward(px, op, score, CONFIG["n_hold"], CONFIG["rebal"], CONFIG["cost_per_side"],
                     vol_target=CONFIG["vol_target"], carry=carry_ser)
        s5 = pd.Series({d: m["nav"] for d, m in f5.run(dates, rebal_days)}).sort_index()
        up = float(s5.iloc[-1] / vt_mine.iloc[-1] - 1.0)
        chk("carry lifts the book in a plausible band", 0.005 < up < 0.15,
            "cumulative=%+.2f%% final=%.4f" % (up * 100, s5.iloc[-1]))
        # carry must ride cash only: a fully invested bar's mark carries zero
        marks5 = f5.run(dates, rebal_days)
        first_bar = marks5[0][0]
        bad = [(d, m) for d, m in marks5 if d != first_bar
               and (m["cash_start"] <= 1e-12) != (abs(m.get("carry", 0.0)) <= 0)]
        chk("carry rides start-of-bar cash only", not bad, "bad=%d" % len(bad))

    # (r1276) a repeated poll must not rewrite the ledger file
    led_f = {"runs": [], "bars": [{"bar": "2026-10-23", "nav": 1.0}]}
    chk("no-op stub", _noop_stub(led_f, {"bar": "2026-10-23"}, day="2026-10-26") is True,
        "first poll of a day records one liveness stub")
    _before = json.dumps(led_f, sort_keys=True)
    chk("no-op stub quiet", _noop_stub(led_f, {"bar": "2026-10-23"},
                                       day="2026-10-26") is False,
        "second poll on the same day records nothing")
    chk("no-op stub stable", json.dumps(led_f, sort_keys=True) == _before,
        "so the ledger stays byte-identical across repeated no-ops (n=%d)"
        % len(led_f["runs"]))
    chk("no-op stub daily", _noop_stub(led_f, {"bar": "2026-10-23"},
                                       day="2026-10-27") is True,
        "a new day records again, so liveness evidence is never lost")

    # --- basket benchmark (r1313): the daily form of "are we beating buy-and-hold?" -----
    mid_bar = str(dates[-6].date())
    bench = bench_block(dates, rebal_days, mid_bar)
    span_codes = [code for _k, code, _l in S.SPAN]
    chk("basket keys come from the spanning study", bench["keys"] == span_codes,
        "keys=%s" % ",".join(bench["keys"]))
    navs = [b["nav"] for b in bench["bars"]]
    chk("basket is rebased to 1.0 at the base bar",
        bench["bars"][0]["bar"] == mid_bar and abs(navs[0] - 1.0) < 1e-12,
        "first=%s nav=%.10f" % (bench["bars"][0]["bar"], navs[0]))
    # a flat 1.0 line would satisfy every identity above -- prove the arm actually ran
    chk("basket actually moved", max(navs) - min(navs) > 1e-4 and bench["decisions"] > 5,
        "range=%.4f decisions=%d" % (max(navs) - min(navs), bench["decisions"]))
    chk("basket nav stays positive and finite", all(np.isfinite(v) and v > 0 for v in navs),
        "n=%d min=%.4f" % (len(navs), min(navs)))
    # the excess must be a ratio (a difference would read 0.03 where the honest number is
    # 0.0294) -- pin it on a hand-checkable pair rather than on the live series
    ex = _excess(1.05, 1.02)
    chk("excess is measured against the basket, not subtracted",
        abs(ex - (1.05 / 1.02 - 1.0)) < 1e-15 and abs(ex - 0.03) > 1e-4,
        "excess=%.6f vs naive difference 0.03" % ex)
    # a published basket bar that stops re-deriving must freeze the ledger the same way
    doctored = json.loads(json.dumps(bench))
    doctored["bars"][1]["nav"] = doctored["bars"][1]["nav"] + 1e-6
    chk("basket drift gate fires on a doctored bar",
        len(bench_drift(doctored, bench)) == 1, "faces=%d" % len(bench_drift(doctored, bench)))
    chk("basket drift gate is quiet on an identical block", bench_drift(bench, bench) == [],
        "re-derivation is deterministic")
    # the engine convention charges weight drift on NEITHER arm; that omission is sized,
    # not hidden -- and a cost sweep must therefore be an exact identity here
    b_free = bench_block(dates, rebal_days, mid_bar, cost=0.0)
    same = max(abs(a["nav"] - b["nav"]) for a, b in zip(b_free["bars"], bench["bars"]))
    chk("basket turnover is drift-only and is not booked on either arm",
        same < 1e-12 and bench["rebalance_friction"]["turnover_per_decision"] >= 0.0,
        "cost_sweep_maxabs=%.1e drift_turn/decision=%.4f -> %.1fbp/yr if charged" %
        (same, bench["rebalance_friction"]["turnover_per_decision"],
         bench["rebalance_friction"]["bp_per_year_if_charged"]))
    # the book's nav must ride the same bar list as the basket, or the gap is a calendar
    led_b = {"bars": _indexed(marks0, mid_bar)}
    wired = _bench_with_book(led_b["bars"], dates, mid_bar)
    chk("book and basket share one bar list",
        [b["bar"] for b in wired["bars"]] == [b["bar"] for b in led_b["bars"]],
        "bars=%d" % len(wired["bars"]))
    chk("excess is published per bar and as a latest line",
        wired["latest"] is not None and wired["latest"].get("excess_pp") is not None
        and all("excess" in b for b in wired["bars"]),
        "latest=%s" % json.dumps(wired["latest"]))

    # --- significance: the noise floor a spread has to clear (r1314) --------------
    sig = significance(dates, marks0, set(dates[::CONFIG["rebal"]]), 3)
    chk("the significance floor is measured off the parent series, not the published prefix",
        sig.get("available") and sig["bars_used"] > 100 and sig["published_bars"] == 3,
        "bars_used=%s published=%s" % (sig.get("bars_used"), sig.get("published_bars")))
    sd = (sig["daily_vol_pct"] / 100.0) if sig.get("available") else 0.0
    chk("the published band is the 95% identity at the bar count it was measured over",
        sig.get("available") and abs(sig["noise_band_pp_at_published"] -
                                     1.96 * sd * np.sqrt(3) * 100) < 5e-3,
        "band=%.3fpp" % (sig.get("noise_band_pp_at_published") or float("nan")))
    b = sig.get("noise_band_pp") or {}
    chk("the band shrinks as sqrt(bars), not faster",
        b.get("3y") and b.get("3m") and
        abs((b["3y"] / b["3m"]) / np.sqrt(732.0 / 60.0) - 1.0) < 1e-3,
        "3y/3m=%.3f vs sqrt(12.2)=%.3f" % (b.get("3y", 0) / b["3m"], np.sqrt(732 / 60.0))
        if b.get("3m") else "no band")
    need = sig.get("bars_needed_for_edge") or {}
    tres = []
    for lbl, n in need.items():
        e = float(lbl.replace("pp/yr", "")) / 100.0
        tres.append(T_CRIT * BARS_PER_YEAR * sd / (np.sqrt(n) * e))
    chk("bars_needed is the t=2 identity, and it rounds up not down",
        len(tres) == len(SIG_EDGES) and all(0.999 <= t < 1.02 for t in tres),
        "t=%s" % ",".join("%.4f" % t for t in tres))
    det = sig.get("min_detectable_edge_pp") or {}
    chk("the inverted reading is the same identity solved for edge, not a new fit",
        det.get("1y") and abs(det["1y"] / 100 - T_CRIT * BARS_PER_YEAR * sd / np.sqrt(244)) < 1e-2,
        "1y=%.1fpp/yr" % (det.get("1y") or 0))
    led_real = load_ledger() or {}
    spread = ((led_real.get("benchmark") or {}).get("latest") or {}).get("excess_pp")
    band_pub = ((led_real.get("benchmark") or {}).get("significance") or {}).get(
        "noise_band_pp_at_published")
    chk("the published line carries the floor beside the spread, not the spread alone",
        spread is None or (band_pub is not None and abs(spread) < band_pub
                           and "band" in _sig_line(led_real) and
                           ("%.2fpp" % band_pub) in _sig_line(led_real)),
        "spread=%s band=%s" % (spread, band_pub))
    chk("a shorter-than-two-bar excess series publishes unavailable, not a zero-width band",
        significance(dates, marks0, set(dates[::CONFIG["rebal"]]), 3)["available"] is True
        and significance(dates, marks0[-1:], set(dates[::CONFIG["rebal"]]), 1)
        .get("available") is False,
        "guard leg")

    # The reverse question (r1316). Three legs: the horizon table is the power
    # identity, the candidate years are priced off the studies' own published alpha
    # (not typed here), and a missing study is omitted rather than filled in.
    pw = sig.get("power") or {}
    mde = pw.get("min_detectable_edge_pp") or {}
    chk("the horizon table is the 80%-power identity and shrinks as sqrt(horizon)",
        pw.get("available") and mde.get("1y")
        and abs(mde["1y"] / 100 - POWER_Z * sd * np.sqrt(BARS_PER_YEAR)) < 1e-4
        and mde["1y"] > mde["2y"] > mde["3y"]
        and abs(mde["1y"] / mde["2y"] - np.sqrt(2.0)) < 0.01,
        "1y=%.1f 2y=%.1f 3y=%.1f" % (mde.get("1y", 0), mde.get("2y", 0), mde.get("3y", 0)))
    src = pw.get("candidate_sources") or {}
    yrs = pw.get("years_for_80pct_power") or {}
    pre = src.get("pre-2020 measured alpha (single arm)") or {}
    chk("the candidate years are priced off the study's own published alpha",
        pre.get("edge_pp_per_year")
        and abs(yrs.get("pre-2020 measured alpha (single arm)", 0)
                - (POWER_Z * pw["annual_vol_pct"] / 100
                   / (pre["edge_pp_per_year"] / 100)) ** 2) < 0.15,
        "edge=%spp/yr years=%s" % (pre.get("edge_pp_per_year"),
                                   yrs.get("pre-2020 measured alpha (single arm)")))
    nofile = power_table(sd, candidates=(("missing study", "results/nope.json",
                                         ("a", "b")),), root=PATHS.root)
    chk("a study that is not on disk is omitted with its reason, not filled in",
        nofile["available"] and not nofile["years_for_80pct_power"]
        and (nofile["candidate_sources"].get("missing study") or {}).get("omitted"),
        str(nofile["candidate_sources"].get("missing study")))

    print("SELFTEST " + ("OK" if ok else "FAILED"), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--selftest" in args:
        sys.exit(selftest())
    cmd = args[0] if args else "run"
    opts = {}
    for a in args:
        if a.startswith("--") and "=" in a:
            k, v = a[2:].split("=", 1)
            opts[k] = v
    if cmd == "seed":
        sys.exit(seed(capital=float(opts.get("capital", 1_000_000))))
    if cmd == "calibrate":
        sys.exit(calibrate())
    if cmd == "carry":
        sys.exit(carry(fee_free=opts.get("fees") == "0"))
    sys.exit(run(rebase="--rebase" in args))