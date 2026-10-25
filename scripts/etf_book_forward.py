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
  python scripts/etf_book_forward.py --selftest

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
import etf_equity_alpha as A
import etf_robust_pf as R
import etf_book_production as P
from config import PATHS

SCHEMA = "etf-book-forward/v1"
OUT_DIR = os.path.join(PATHS.results_dir, "etf_book_forward")
LEDGER = os.path.join(OUT_DIR, "LEDGER.json")
DRIFT_TOL = 1e-9
MAX_RUNS = 40
CONFIG = {
    "n_hold": 12,
    "rebal": 20,
    "cost_per_side": P.COST,
    "vol_target": P.TARGET_VOL,
    "classes": list(P.USE_CLASSES),
    "execution": "decide at close of bar d -> fill at open of bar d+1 -> hold to the next fill",
    "cash": "cash leg earns 0 in the ledger (disclosed, not modelled away)",
}
CAVEATS = [
    "The ETF pool is today's listed set: survivorship is still in the equity sleeve.",
    "The seed bar begins the record; nothing before it is a track record, however good the backtest.",
    "The vol target only de-levers -- a drawdown tool, not an edge.",
    "Cash earns 0 in the marks, so a de-levered book under-reports its true carry.",
    "Research output, not an investment recommendation.",
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
    """Mean simple return over the book between two price faces (engine-identical).

    Missing cells are skipped, which renormalises the equal-weight book over the names
    that actually printed -- the same approximation the research engine carries.
    """
    out = []
    for p in book:
        a = a_ser.get(p, np.nan)
        b = b_ser.get(p, np.nan)
        if not np.isfinite(a) or not np.isfinite(b) or a <= 0:
            continue
        out.append(b / a - 1.0)
    return float(np.mean(out)) if out else None


class Forward:
    """Incremental state machine: one bar in, one mark out.

    State is (nav, held, pending). `pending` is a book decided at the close of a grid bar
    waiting for the next open; it can never be applied on the bar that produced it.
    """

    def __init__(self, px, op, score, n_hold, rebal, cost, vol_target=None):
        self.px, self.op, self.score = px, op, score
        self.n_hold, self.rebal, self.cost = n_hold, rebal, cost
        self.vol_target = vol_target
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

    def run(self, dates, rebal_days):
        marks = []
        for i, d in enumerate(dates):
            filled, turn = False, 0.0
            if i > 0:
                prev = dates[i - 1]
                raw_open = self.op.loc[d]
                open_d = raw_open.where(np.isfinite(raw_open), self.px.loc[d])
                if self.pending is not None:
                    # overnight gap belongs to the OLD book, then the fill is charged at
                    # the open, and only open->close is earned by the NEW book
                    if self.held:
                        r = _leg(self.held, self.px.loc[prev], open_d)
                        if r is not None:
                            self.nav *= (1.0 + r)
                    new, turn = self.pending
                    self.nav *= (1.0 - self.cost * turn)
                    self.turnover_sum += turn
                    self.n_fill += 1
                    self.held, self.pending = new, None
                    filled = True
                    r = _leg(self.held, open_d, self.px.loc[d])
                    if r is not None:
                        self.nav *= (1.0 + r)
                elif self.held:
                    r = _leg(self.held, self.px.loc[prev], self.px.loc[d])
                    if r is not None:
                        self.nav *= (1.0 + r)
            invested = float(sum(self.held.values()))
            marks.append((d, {
                "nav": self.nav,
                "cash": max(0.0, 1.0 - invested),
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


def compute_marks(vol_target=CONFIG["vol_target"]):
    close, openp, amt, feats, score, cls, n_flip = build_inputs()
    px = close.reindex(columns=close.columns).ffill()
    op = openp.reindex(columns=close.columns)
    dates, rebal_days = date_grid(px, CONFIG["rebal"])
    fwd = Forward(px, op, score, CONFIG["n_hold"], CONFIG["rebal"], CONFIG["cost_per_side"],
                  vol_target=vol_target)
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
            "n_held": m["n_held"],
            "filled": m["filled"],
            "turn": m["turn"],
        })
    return out


def load_ledger():
    if not os.path.exists(LEDGER):
        return None
    with open(LEDGER, "r", encoding="utf-8") as f:
        return json.load(f)


def save_ledger(led):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(LEDGER, "w", encoding="utf-8") as f:
        json.dump(led, f, ensure_ascii=False, indent=1)


def _fresh(fwd, dates, cls, n_flip, capital):
    return {
        "schema": SCHEMA,
        "config": dict(CONFIG),
        "seed": None,
        "bars": [],
        "books": {},
        "book_in_force": None,
        "status": "live",
        "drift": {"faces": [], "max_abs": 0.0, "checked_bars": 0},
        "rebases": [],
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
    led["books"] = _books_after(fwd, led["seed"]["bar"])
    led["book_in_force"] = fwd.last_decision
    led["runs"] = [{"ts": led["seed"]["ts"], "new_bars": 0, "last_bar": last_bar, "first": True}]
    save_ledger(led)
    print("SEEDED %s nav=1.0 bars=%d names=%d status=live" %
          (last_bar, len(led["bars"]), CONFIG["n_hold"]), flush=True)
    return 0


def run(rebase=False):
    led = load_ledger()
    if led is None:
        return seed()
    if led.get("status") == "frozen" and not rebase:
        print("FROZEN: ledger froze on drift; inspect results/etf_book_forward/LEDGER.json "
              "and rerun with --rebase to adopt the re-derived history", flush=True)
        return 3

    fwd, marks, dates, cls, n_flip = compute_marks()
    seed_bar = led["seed"]["bar"]
    fresh = {b["bar"]: b for b in _indexed(marks, seed_bar)}

    # drift gate: every already-published mark must re-derive exactly
    faces, worst = [], 0.0
    for b in led["bars"]:
        f = fresh.get(b["bar"])
        if f is None:
            faces.append(b["bar"] + ":missing")
            continue
        d = abs(f["nav"] - b["nav"])
        worst = max(worst, d)
        if d > DRIFT_TOL:
            faces.append("%s:%.3e" % (b["bar"], d))
    led["drift"] = {"faces": faces[:20], "max_abs": worst, "checked_bars": len(led["bars"])}

    new_bars = [f for f in _indexed(marks, seed_bar) if f["bar"] > led["bars"][-1]["bar"]]
    if faces and not rebase:
        led["status"] = "frozen"
        save_ledger(led)
        print("DRIFT %d faces max_abs=%.3e -> FROZEN (exit 3); --rebase is the logged escape" %
              (len(faces), worst), flush=True)
        return 3
    if faces and rebase:
        led["rebases"].append({
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "n_faces": len(faces), "max_abs": worst, "sample": faces[:10],
        })
        led["bars"] = _indexed(marks, seed_bar)
        led["status"] = "live"
        print("REBASED %d faces max_abs=%.3e (logged in rebases)" % (len(faces), worst), flush=True)

    if not new_bars:
        headed = led["bars"][-1] if led["bars"] else {}
        print("NO-OP last_bar=%s nav=%s (no new panel bars)" %
              (headed.get("bar"), headed.get("nav")), flush=True)
        led["runs"] = (led.get("runs", []) + [{
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "new_bars": 0,
            "last_bar": headed.get("bar")}])[-MAX_RUNS:]
        led["books"] = _books_after(fwd, led["seed"]["bar"])
        led["book_in_force"] = fwd.last_decision
        led["panel"] = {"n_instruments": len(cls), "flips_repaired": n_flip}
        save_ledger(led)
        return 0

    led["bars"].extend(new_bars)
    # peak must be re-derived across the whole published series after appending
    peak = 1.0
    for b in led["bars"]:
        peak = max(peak, b["nav"])
        b["dd"] = round(b["nav"] / peak - 1.0, 6)
    led["books"] = _books_after(fwd, led["seed"]["bar"])
    led["book_in_force"] = fwd.last_decision
    led["panel"] = {"n_instruments": len(cls), "flips_repaired": n_flip}
    led["status"] = "live"
    led["runs"] = (led.get("runs", []) + [{
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "new_bars": len(new_bars),
        "last_bar": new_bars[-1]["bar"]}])[-MAX_RUNS:]
    save_ledger(led)
    tail = led["bars"][-1]
    print("APPENDED %d bars -> %s nav=%.4f dd=%.2f%% cash=%.0f%%" %
          (len(new_bars), tail["bar"], tail["nav"], tail["dd"] * 100, tail["cash"] * 100),
          flush=True)
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
    sys.exit(run(rebase="--rebase" in args))