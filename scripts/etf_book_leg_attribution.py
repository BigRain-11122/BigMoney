"""Where in the day does the book's money accrue -- overnight, intraday, or toll?

Every published number for this book is one CAGR. Nothing on any of the faces says whether
that CAGR is earned between one close and the next open (the leg the OLD book keeps while
the order in the queue is not filled yet), between the open and the close of the fill bar
(the leg the NEW book earns), on the quiet bars in between, or whether it was simply paid
away in toll. That matters to the person who has to press the button: a book that earns in
the session is implementable with a market-on-open fill, a book that earns overnight is
implementable with a close-auction fill, and a book that earns neither is a toll machine
with a nice backtest.

This script does not re-derive a book: it walks the SAME state machine that
etf_book_forward.Forward walks (subclass, one function copied) and, at each of the four
places that machine multiplies the nav, books that factor's LOG into one of four buckets:

    overnight : close(prev) -> open(d)   earned by the OLD book (fill is still pending)
    toll      : (1 - rate*turn)          charged at the open of the fill bar
    intraday  : open(d) -> close(d)      earned by the NEW book
    plain     : close(prev) -> close(d)  a bar with no fill at all

so the four buckets sum to log(nav_final) EXACTLY (not approximately), and dividing by the
sample length turns them into pp/yr that add up to the log CAGR. The identity is a selftest
leg against Forward itself: if this walker ever drifts from the engine, the suite says so
instead of publishing a plausible attribution of a different book.

Three arms, because a split with no control is not readable (E214/E238 family -- a number
in a denominator needs a yardstick that shares the denominator):

    production  the card's config (12 names, 8% vol target, 10bp/side)
    base_book   the same selection, unlevered book, no overlay -- isolates selection
    control_ew  every name the panel printed, equal weight, same grid and toll

`base_book - control_ew` per bucket is the selection's timing contribution; `production`
is what the headline number is actually made of.

Scope discipline: zero prereg, zero judged face, zero network, zero engine edit. L1
deterministic -- rerun byte-identical (only the artifact's own timestamp moves).

  python scripts/etf_book_leg_attribution.py run
  python scripts/etf_book_leg_attribution.py --selftest
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_equity_alpha as A
import etf_robust_pf as R
import etf_book_production as P
import etf_book_forward as F
from config import PATHS

OUT_DIR = os.path.join(PATHS.results_dir, "etf_book_legs")
BARS_PER_YEAR = 244.0
BUCKETS = ("overnight", "toll", "intraday", "plain")
TOL = 1e-12


class LegWalker(F.Forward):
    """Forward's nav machine with four log buckets -- nothing else changes.

    `control=True` replaces the ranked selection with equal weight over every name the
    panel printed on the decision bar. That is the only behavioural difference, and it is
    pinned by a selftest leg asserting the control book's weights sum to 1.
    """

    def __init__(self, *args, **kwargs):
        self.control = bool(kwargs.pop("control", False))
        F.Forward.__init__(self, *args, **kwargs)
        self.buckets = dict((k, 0.0) for k in BUCKETS)
        self.n_bars = 0
        self.n_fill_bars = 0
        self.n_plain_bars = 0
        self.n_decision = 0
        self.last_book = {}

    def _decide(self, d):
        if not self.control:
            F.Forward._decide(self, d)
            if self.pending is not None:
                self.n_decision += 1
                self.last_book = self.pending[0]
            return
        row = self.px.loc[d]
        names = [p for p in row.index if np.isfinite(row[p]) and row[p] > 0]
        if not names:
            return
        new = dict((p, 1.0 / len(names)) for p in names)
        turn = sum(abs(new.get(k, 0.0) - self.held.get(k, 0.0))
                   for k in set(new) | set(self.held))
        self.pending = (new, turn)
        self.n_decision += 1
        self.last_book = new
        self.last_decision = {"bar": str(d.date()), "n_names": len(names),
                              "turnover": round(float(turn), 6)}
        self.books[str(d.date())] = self.last_decision

    def _book(self, bucket, factor):
        """Book one multiplicative factor's log into a bucket (no-op for factor 1)."""
        if factor is None or not np.isfinite(factor) or factor <= 0:
            return
        self.buckets[bucket] += float(np.log(factor))

    def run(self, dates, rebal_days):
        """Copy of etf_book_forward.Forward.run with the four buckets booked.

        The multiplication order and every guard are the engine's; the only additions are
        the `_book` calls on the four factors that move the nav. Identity to the engine is
        a selftest leg, so a divergence here cannot survive the suite.
        """
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
                    if self.held:
                        r = self._ret(self.held, self.px.loc[prev], open_d)
                        if r is not None:
                            self._book("overnight", 1.0 + r + carry)
                            self.nav *= (1.0 + r + carry)
                    elif carry:
                        self._book("overnight", 1.0 + carry)
                        self.nav *= (1.0 + carry)
                    new, turn = self.pending
                    rate = (self.cost(self.held, new, d) if callable(self.cost)
                            else self.cost)
                    self._book("toll", 1.0 - rate * turn)
                    self.nav *= (1.0 - rate * turn)
                    self.turnover_sum += turn
                    self.n_fill += 1
                    self.held, self.pending = new, None
                    filled = True
                    self.n_fill_bars += 1
                    r = self._ret(self.held, open_d, self.px.loc[d])
                    if r is not None:
                        self._book("intraday", 1.0 + r)
                        self.nav *= (1.0 + r)
                elif self.held:
                    r = self._ret(self.held, self.px.loc[prev], self.px.loc[d])
                    if r is not None:
                        self._book("plain", 1.0 + r + carry)
                        self.nav *= (1.0 + r + carry)
                        self.n_plain_bars += 1
                elif carry:
                    self._book("plain", 1.0 + carry)
                    self.nav *= (1.0 + carry)
            invested = float(sum(self.held.values()))
            self.n_bars += 1
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


def _arm(px, op, score, dates, rebal_days, n_hold, rebal, cost, vol_target, control=False):
    """Walk one arm and package its buckets as pp/yr contributions."""
    w = LegWalker(px, op, score, n_hold, rebal, cost, vol_target=vol_target,
                  control=control)
    marks = w.run(dates, rebal_days)
    ser = pd.Series(dict(marks)).sort_index()
    nav = pd.Series({d: m["nav"] for d, m in marks}).sort_index()
    years = len(dates) / BARS_PER_YEAR
    pp = dict((k, round(100.0 * w.buckets[k] / years, 3)) for k in BUCKETS)
    total = round(100.0 * float(np.log(nav.iloc[-1])) / years, 3)
    stats = A.stats2(nav, "full")
    # Per-bar reading: 95% of the bars are plain, so the bucket TOTAL alone would make the
    # plain leg look like the engine of the book for arithmetic reasons rather than measured
    # ones. Every bucket is therefore also published per bar of the type it books on.
    n_of = {"overnight": w.n_fill_bars, "intraday": w.n_fill_bars, "toll": w.n_fill_bars,
            "plain": w.n_plain_bars}
    per_bar = dict((k, round(10000.0 * w.buckets[k] / n_of[k], 3) if n_of[k] else None)
                   for k in BUCKETS)
    fill_net = round(sum(per_bar[k] or 0.0 for k in ("overnight", "intraday", "toll")), 3)
    out = {
        "buckets_pp_per_year": pp,
        "buckets_sum_pp": round(sum(pp.values()), 3),
        "total_log_pp": total,
        "cagr_pct": None if stats.get("cagr") is None else round(stats["cagr"] * 100, 3),
        "sharpe": None if stats.get("sharpe") is None else round(stats["sharpe"], 3),
        "maxdd_pct": None if stats.get("maxdd") is None else round(stats["maxdd"] * 100, 2),
        "bars": len(dates),
        "years": round(years, 3),
        "fill_bars": w.n_fill_bars,
        "plain_bars": w.n_plain_bars,
        # Bars that book no leg at all: the first bar has no previous close and, when the
        # book is still empty (no decision has filled yet), the bar before the first fill
        # earns nothing either. Published so bars == fill + plain + seed closes exactly.
        "seed_bars": len(dates) - w.n_fill_bars - w.n_plain_bars,
        "per_bar_bp": per_bar,
        # The question an operator actually asks: does the day I place an order pay?
        "fill_bar_net_bp": fill_net,
        "fill_bar_drag_pp_per_year": round(
            100.0 * (w.n_fill_bars * fill_net / 10000.0) / years, 3),
        "plain_carry_pp_per_year": round(
            100.0 * (w.n_plain_bars * (per_bar["plain"] or 0.0) / 10000.0) / years, 3),
        "decisions": w.n_decision,
        "turnover_per_decision": round(float(w.turnover_sum / w.n_fill), 6) if w.n_fill else 0.0,
        "nav_final": round(float(nav.iloc[-1]), 8),
        "_log_nav": float(np.log(nav.iloc[-1])),
        "_buckets_log": dict(w.buckets),
        "_walker": w,
        "_nav": nav,
    }
    return out


def build_arms(px=None, op=None, score=None):
    """Price the three arms and the selection wedge. Returns {} when the panel is absent."""
    if px is None:
        close, openp, amt, feats, score, cls, n_flip = F.build_inputs()
        px = close.reindex(columns=close.columns).ffill()
        op = openp.reindex(columns=close.columns)
        digest = getattr(F, "PANEL_DIGEST", None)
    else:
        n_flip = None
        digest = None
    if px is None or len(px) == 0 or score is None or len(score) == 0:
        return {}
    dates, rebal_days = F.date_grid(px, F.CONFIG["rebal"])
    if len(dates) < 60:
        return {}
    kw = dict(dates=dates, rebal_days=rebal_days, rebal=F.CONFIG["rebal"],
              cost=F.CONFIG["cost_per_side"])
    prod = _arm(px, op, score, n_hold=F.CONFIG["n_hold"],
                vol_target=F.CONFIG["vol_target"], **kw)
    base = _arm(px, op, score, n_hold=F.CONFIG["n_hold"], vol_target=None, **kw)
    ctrl = _arm(px, op, score, n_hold=len(px.columns), vol_target=None, control=True, **kw)
    wedge = dict((k, round(base["buckets_pp_per_year"][k] - ctrl["buckets_pp_per_year"][k], 3))
                 for k in BUCKETS)
    wedge["total"] = round(base["total_log_pp"] - ctrl["total_log_pp"], 3)
    arms = {"production": prod, "base_book": base, "control_ew": ctrl}
    # Identity on THIS panel, not only on the selftest fixture: an attribution is only about
    # this book if the walker that produced it is this book's engine. Any divergence is
    # published (and the chain leg refuses the face) rather than rounded away.
    ref = F.Forward(px, op, score, F.CONFIG["n_hold"], F.CONFIG["rebal"],
                    F.CONFIG["cost_per_side"], vol_target=F.CONFIG["vol_target"])
    ref_nav = np.array([m[1]["nav"] for m in ref.run(dates, rebal_days)])
    my_nav = prod["_nav"].values
    ident = float(np.max(np.abs(my_nav - ref_nav))) if len(my_nav) == len(ref_nav) else None
    out = {
        "evidence_cutoff": str(dates[-1].date()),
        "generated_ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "config": {
            "n_hold": F.CONFIG["n_hold"], "rebal": F.CONFIG["rebal"],
            "cost_per_side": F.CONFIG["cost_per_side"], "vol_target": F.CONFIG["vol_target"],
            "execution": F.CONFIG["execution"],
            "bars_per_year": BARS_PER_YEAR,
            "buckets": list(BUCKETS),
            "attribution": "each factor the nav machine multiplies is booked as its log, so "
                           "the four buckets sum to log(nav_final) exactly and pp/yr add up",
            "carry": "off (cash earns nothing here) -- the card's carry split is a different "
                     "face and is not re-priced by this one",
            "note": "pp/yr is log-return attribution; cagr_pct is the geometric reading of the "
                    "same curve. They differ only by the compounding term.",
        },
        "panel": {"first_bar": str(dates[0].date()), "last_bar": str(dates[-1].date()),
                  "symbols": int(px.shape[1]), "digest": digest},
        "arms": arms,
        "engine_identity_max_abs_diff": ident,
        "selection_wedge_pp": wedge,
    }
    return out


def _strip(d):
    """Drop the in-memory helpers so the artifact is JSON-clean."""
    if not d:
        return d
    out = json.loads(json.dumps(d, default=str))
    for k in ("arms",):
        for arm in out.get(k, {}).values():
            for junk in ("_log_nav", "_buckets_log", "_walker", "_nav"):
                arm.pop(junk, None)
    return out


def check_face(face):
    """Recount a published face's own arithmetic. Returns a list of complaints (empty = ok).

    Nothing here re-runs the walk: the point is that the four buckets a reader is given
    must add up to the total the same face publishes, that the per-bar reading must be the
    bucket divided by the number of bars OF THAT TYPE, and that the two headline sentences
    (plain carry, fill-bar drag) must reproduce the total. A face whose arithmetic does not
    close is a caption, not a measurement.
    """
    bad = []
    if not face:
        return ["no face on disk"]
    arms = face.get("arms") or {}
    if not arms:
        return ["face carries no arms"]
    ident = face.get("engine_identity_max_abs_diff")
    if ident is None or float(ident) > 1e-9:
        bad.append("walker is not this book's engine on this panel (max abs nav diff %r)"
                   % (ident,))
    for name, arm in arms.items():
        pp = arm.get("buckets_pp_per_year") or {}
        if set(pp) != set(BUCKETS):
            bad.append("%s: bucket keys %r" % (name, sorted(pp)))
            continue
        if abs(sum(pp.values()) - arm.get("buckets_sum_pp", 0.0)) > 0.02:
            bad.append("%s: buckets sum %.3f != published %.3f"
                       % (name, sum(pp.values()), arm.get("buckets_sum_pp")))
        if abs(arm.get("buckets_sum_pp", 0.0) - arm.get("total_log_pp", 0.0)) > 0.02:
            bad.append("%s: buckets %.3f != total %.3f"
                       % (name, arm.get("buckets_sum_pp"), arm.get("total_log_pp")))
        nb, nf, npl = arm.get("bars"), arm.get("fill_bars"), arm.get("plain_bars")
        nseed = arm.get("seed_bars")
        if nb is None or nf is None or npl is None or nseed is None:
            bad.append("%s: bar counts incomplete" % name)
            continue
        if nf + npl + nseed != nb:
            bad.append("%s: bars %r != fill %r + plain %r + seed %r"
                       % (name, nb, nf, npl, nseed))
            continue
        years = arm.get("years")
        pb = arm.get("per_bar_bp") or {}
        for k, n in (("overnight", nf), ("intraday", nf), ("toll", nf), ("plain", npl)):
            if not n:
                continue
            want = 100.0 * (n * pb.get(k, 0.0) / 10000.0) / years
            if abs(want - pp.get(k, 0.0)) > 0.02:
                bad.append("%s: %s per-bar %.3f bp x %d bars != %.3f pp"
                           % (name, k, pb.get(k, 0.0), n, pp.get(k, 0.0)))
        drag, carry = arm.get("fill_bar_drag_pp_per_year"), arm.get("plain_carry_pp_per_year")
        if drag is None or carry is None or abs(drag + carry - arm.get("total_log_pp", 0)) > 0.02:
            bad.append("%s: drag %.3f + carry %.3f != total %.3f"
                       % (name, drag or 0.0, carry or 0.0, arm.get("total_log_pp", 0.0)))
        # sign invariant: the drag is the fill-bar net spread over the period, so the two
        # must agree in sign -- a positive net on a negative drag is a mixed unit, not data
        net = arm.get("fill_bar_net_bp")
        if net is not None and drag is not None and nf and (net > 0) != (drag > 0):
            bad.append("%s: fill-bar net %.3f bp but drag %.3f pp disagree in sign"
                       % (name, net, drag))
    return bad


def check():
    path = os.path.join(OUT_DIR, "latest.json")
    if not os.path.exists(path):
        print("NO-FACE: %s absent" % path, flush=True)
        return 2
    with open(path, encoding="utf-8") as f:
        face = json.load(f)
    bad = check_face(face)
    if bad:
        print("FACE-BROKEN: " + "; ".join(bad)[:400], flush=True)
        return 1
    print("FACE-OK %s (%d arms, production %.2fpp/yr = plain %+.2f + fill drag %+.2f)"
          % (face.get("evidence_cutoff"), len(face.get("arms") or {}),
             (face["arms"]["production"]["total_log_pp"]),
             face["arms"]["production"]["plain_carry_pp_per_year"],
             face["arms"]["production"]["fill_bar_drag_pp_per_year"]), flush=True)
    return 0


def money_split_face(path=None):
    """The published split, read the way a face has to quote it (r1189).

    Single implementation of "where in the day does the money accrue". A face that
    re-derived the four buckets from the nav curve would publish a second answer that
    drifts silently the first time either copy is touched (E289 lineage), so the faces
    quote this artifact and this function, never a re-derivation.

    A face whose own arithmetic does not close is REFUSED here (`check_face`), not
    printed with a caveat: a split that does not add up to its own total reads exactly
    like data.
    """
    path = path or os.path.join(OUT_DIR, "latest.json")
    if not os.path.exists(path):
        return {"status": "absent", "artifact": path,
                "detail": "leg split not published yet (%s)" % path}
    try:
        with open(path, encoding="utf-8") as f:
            face = json.load(f)
    except Exception as exc:                                     # noqa: BLE001
        return {"status": "unreadable", "artifact": path,
                "detail": "artifact unreadable (%s)" % str(exc)[:120]}
    bad = check_face(face)
    if bad:
        return {"status": "broken", "artifact": path, "detail": "; ".join(bad)[:240]}
    arms = {}
    for name, arm in (face.get("arms") or {}).items():
        arms[name] = {
            "buckets_pp_per_year": dict(arm.get("buckets_pp_per_year") or {}),
            "total_log_pp": arm.get("total_log_pp"),
            "plain_carry_pp_per_year": arm.get("plain_carry_pp_per_year"),
            "fill_bar_drag_pp_per_year": arm.get("fill_bar_drag_pp_per_year"),
            "fill_bars": arm.get("fill_bars"),
            "plain_bars": arm.get("plain_bars"),
            "bars": arm.get("bars"),
            "cagr_pct": arm.get("cagr_pct"),
            "sharpe": arm.get("sharpe"),
        }
    return {"status": "ok", "artifact": path,
            "evidence_cutoff": face.get("evidence_cutoff"),
            "generated_ts": face.get("generated_ts"),
            "execution": (face.get("config") or {}).get("execution"),
            "priced_bar": (face.get("panel") or {}).get("last_bar"),
            "panel_first_bar": (face.get("panel") or {}).get("first_bar"),
            "arms": arms, "selection_wedge_pp": face.get("selection_wedge_pp")}


def run():
    res = build_arms()
    if not res:
        print("NO-PANEL: nothing priced, nothing published", flush=True)
        return 2
    os.makedirs(OUT_DIR, exist_ok=True)
    payload = _strip(res)
    path = os.path.join(OUT_DIR, "LEGS-%s.json" % payload["evidence_cutoff"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT_DIR, "latest.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    pr = payload["arms"]["production"]["buckets_pp_per_year"]
    print("LEGS %s | production %.2fpp/yr = overnight %+.2f + intraday %+.2f + plain %+.2f "
          "+ toll %+.2f | book-vs-EW wedge %+.2f | -> %s" % (
              payload["evidence_cutoff"], payload["arms"]["production"]["total_log_pp"],
              pr["overnight"], pr["intraday"], pr["plain"], pr["toll"],
              payload["selection_wedge_pp"]["total"], path), flush=True)
    return 0


def _fixture(n=120, seed=7, gap=0.0, cost=0.0, n_names=6):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    cols = ["S%d" % i for i in range(n_names)]
    steps = rng.normal(0.0, 0.01, size=(n, n_names))
    close = pd.DataFrame(100.0 * np.cumprod(1.0 + steps, axis=0), index=idx, columns=cols)
    openp = close.shift(1) * (1.0 + gap)
    openp.iloc[0] = close.iloc[0]
    score = pd.DataFrame(rng.normal(size=(n, n_names)), index=idx, columns=cols)
    return close, openp, score, cost


def selftest():
    fails = []

    def check(name, ok, detail=""):
        print(("PASS " if ok else "FAIL ") + name + ((" | " + detail) if detail else ""),
              flush=True)
        if not ok:
            fails.append(name)

    # L1 -- the walker IS the engine: same nav curve, production flags, on a fixture.
    close, openp, score, cost = _fixture()
    dates = list(close.index)
    rebal_days = set(dates[::5])
    ref = F.Forward(close, openp, score, 2, 5, cost, vol_target=None)
    ref_marks = ref.run(dates, rebal_days)
    ref_nav = np.array([m[1]["nav"] for m in ref_marks])
    w = LegWalker(close, openp, score, 2, 5, cost, vol_target=None)
    mine = w.run(dates, rebal_days)
    my_nav = np.array([m[1]["nav"] for m in mine])
    check("L1 the attribution walker reproduces Forward's nav curve exactly",
          np.max(np.abs(my_nav - ref_nav)) <= TOL,
          "max abs diff=%.3e" % float(np.max(np.abs(my_nav - ref_nav))))

    # L2 -- the four buckets are an exact decomposition, not an approximation.
    gap = float(np.log(my_nav[-1]) - sum(w.buckets.values()))
    check("L2 buckets sum to log(nav_final) exactly",
          abs(gap) <= TOL, "residual=%.3e" % gap)

    # L3 -- with no overnight gap the overnight bucket is exactly zero (and only it).
    close2, openp2, score2, cost2 = _fixture(gap=0.0)
    openp2 = close2.shift(1)
    openp2.iloc[0] = close2.iloc[0]
    w2 = LegWalker(close2, openp2, score2, 2, 5, 0.0, vol_target=None)
    w2.run(list(close2.index), set(list(close2.index)[::5]))
    check("L3 a panel with no open/close gap books exactly zero overnight",
          w2.buckets["overnight"] == 0.0, "overnight=%.3e" % w2.buckets["overnight"])

    # L4 -- with no fill on the grid there is no toll and no intraday leg.
    w3 = LegWalker(close, openp, score, 2, 5, cost, vol_target=None)
    w3.run(dates, set())
    check("L4 a grid with no fills books zero toll and zero intraday",
          w3.buckets["toll"] == 0.0 and w3.buckets["intraday"] == 0.0,
          "toll=%.3e intraday=%.3e" % (w3.buckets["toll"], w3.buckets["intraday"]))

    # L5 -- the toll bucket is the toll the engine charged, not a re-derivation of it.
    tolled = _fixture(cost=0.002)
    wt = LegWalker(tolled[0], tolled[1], tolled[2], 2, 5, tolled[3], vol_target=None)
    marks_t = wt.run(list(tolled[0].index), set(list(tolled[0].index)[::5]))
    toll_log = sum(np.log1p(-tolled[3] * m[1]["turn"]) for m in marks_t if m[1]["filled"])
    check("L5 the toll bucket equals the engine's own charge line",
          abs(toll_log - wt.buckets["toll"]) <= TOL and wt.buckets["toll"] < 0.0,
          "charge=%.6e bucket=%.6e" % (toll_log, wt.buckets["toll"]))

    # L6 -- a control book really is fully invested (weights sum to 1).
    w4 = LegWalker(close, openp, score, 2, 5, cost, vol_target=None, control=True)
    w4.run(dates, rebal_days)
    check("L6 the control arm's book weights sum to 1 on every decision",
          w4.n_decision > 0 and bool(w4.last_book)
          and abs(sum(w4.last_book.values()) - 1.0) <= 1e-12,
          "decisions=%d weight_sum=%.12f" % (w4.n_decision, sum(w4.last_book.values())))

    # L7 -- buckets are signed readings, not magnitudes: on a decaying panel they go negative.
    decay = _fixture()
    dclose = decay[0].mul(np.power(0.995, np.arange(len(decay[0]))), axis=0)
    dopen = dclose.shift(1) * 1.001
    dopen.iloc[0] = dclose.iloc[0]
    w5 = LegWalker(dclose, dopen, decay[2], 2, 5, decay[3], vol_target=None)
    w5.run(list(dclose.index), set(list(dclose.index)[::5]))
    check("L7 measured on a decaying panel the buckets are negative, not magnitudes",
          w5.buckets["plain"] < 0.0 and w5.buckets["intraday"] < 0.0,
          "plain=%.4f intraday=%.4f" % (w5.buckets["plain"], w5.buckets["intraday"]))

    # L8 -- absence reads as no face, never as zeros.
    empty = pd.DataFrame()
    out = build_arms(px=empty, op=empty, score=empty)
    check("L8 an absent panel yields no face at all (not a zero-filled one)", out == {},
          "got %r" % (type(out).__name__,))

    # L9 -- the artifact echoes the rule it used (r1297), and the wedge is book minus control.
    res = build_arms(px=close, op=openp, score=score)
    if res:
        echo = res["config"]["buckets"] == list(BUCKETS)
        wedge_ok = all(abs(res["selection_wedge_pp"][k] -
                           (res["arms"]["base_book"]["buckets_pp_per_year"][k] -
                            res["arms"]["control_ew"]["buckets_pp_per_year"][k])) <= 1e-9
                       for k in BUCKETS)
        check("L9 the face echoes its bucket list and the wedge is book minus control",
              echo and wedge_ok, "echo=%s wedge=%s" % (echo, wedge_ok))
    else:
        check("L9 the face echoes its bucket list and the wedge is book minus control", False,
              "no face built")

    # L10 -- the reader the faces quote. Three states, and a broken face must not leak
    # numbers: "absent" is not zero, "broken" is not a caveat, and the ok path must hand
    # back the artifact's own figures verbatim (a reader that recomputed them would be
    # the second copy this leg exists to prevent).
    import tempfile
    tmp = tempfile.mkdtemp()
    r_absent = money_split_face(path=os.path.join(tmp, "absent.json"))
    check("L10a an unpublished split reads absent, with no arms",
          r_absent.get("status") == "absent" and not r_absent.get("arms"),
          "status=%r" % (r_absent.get("status"),))
    if res:
        good = os.path.join(tmp, "good.json")
        with open(good, "w", encoding="utf-8") as f:
            json.dump(_strip(res), f, ensure_ascii=False)
        r_ok = money_split_face(path=good)
        want = res["arms"]["production"]["buckets_pp_per_year"]
        got = ((r_ok.get("arms") or {}).get("production") or {}).get("buckets_pp_per_year") or {}
        check("L10b a published split is quoted verbatim (no re-derivation)",
              r_ok.get("status") == "ok" and all(got.get(k) == want.get(k) for k in BUCKETS),
              "status=%r production_plain=%r vs %r"
              % (r_ok.get("status"), got.get("plain"), want.get("plain")))
        bad_face = json.loads(json.dumps(_strip(res)))
        bad_face["arms"]["production"]["buckets_pp_per_year"]["plain"] += 5.0
        broken = os.path.join(tmp, "broken.json")
        with open(broken, "w", encoding="utf-8") as f:
            json.dump(bad_face, f, ensure_ascii=False)
        r_bad = money_split_face(path=broken)
        check("L10c a split whose buckets miss its own total is refused, not published",
              r_bad.get("status") == "broken" and not r_bad.get("arms"),
              "status=%r detail=%r" % (r_bad.get("status"), (r_bad.get("detail") or "")[:80]))
    else:
        check("L10b a published split is quoted verbatim (no re-derivation)", False, "no face")
        check("L10c a split whose buckets miss its own total is refused, not published",
              False, "no face")

    print("SELFTEST %s (%d fails)" % ("OK" if not fails else "FAIL", len(fails)), flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "run"
    if arg == "--selftest":
        sys.exit(selftest())
    if arg == "--check":
        sys.exit(check())
    sys.exit(run())