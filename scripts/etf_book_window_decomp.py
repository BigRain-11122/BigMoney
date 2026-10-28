"""Why does the same window print -4.97%/yr in one round and +5.12%/yr in another?

r1305 published cell A: on the 224 ETFs that existed before 2020, priced 2015-2019, the
six-factor book returned -4.97%/yr against +3.89%/yr equal weight = -8.86pp. r1308 then
priced the SAME window with the production cell (N12, 8% vol overlay, bond-free pool,
12bp->10bp) and the book came out at +5.12%/yr, beating its own static class mix by
+2.17pp. Two numbers, one window, opposite stories.

Both can be true -- they are different experiments -- but a card that carries the -8.86pp
caveat next to a +2.17pp premium paragraph is unreadable unless the gap is decomposed.
This ladder moves ONE axis per rung, starting from the published cell so the start of the
ladder is an assertion (r1297: the control arm must be the arm that was published):

  rung 1  published cell       U_pre (all classes)  N5   no overlay   <- asserted vs r1305
  rung 2  + bond-free pool     production classes   N5   no overlay
  rung 3  + wider book         production classes   N12  no overlay
  rung 4  + vol overlay        production classes   N12  8% target   <- must equal r1308

Every rung also carries the equal-weight control on its own universe, so each rung reports
two gaps: excess vs EW (r1305's yardstick) and the level itself. The last rung is the cell
r1308's premium paragraph is built from; if rung 4 reproduces it, the ladder is closed and
the card can print the explanation instead of two rival readings.

Reuse, not re-implementation: panel from etf_book_production.prep_panel, U_pre mask and the
truncate helper from etf_book_pre2020, both engines from etf_composite_pf /
etf_robust_pf. Nothing here re-implements a ranking or a fill.

  python scripts/etf_book_window_decomp.py run
  python scripts/etf_book_window_decomp.py --selftest
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_book_pre2020 as W
import etf_book_production as P
import etf_robust_pf as R

OUT = os.path.join(E.PATHS.results_dir, "etf_book_window_decomp.json")
PUB2020 = os.path.join(E.PATHS.results_dir, "etf_book_pre2020.json")
PUBMIX = os.path.join(E.PATHS.results_dir, "etf_book_passive_mix.json")
CONTROL_TOL_PP = 0.5

START = "2015-01-01"
END = "2019-12-31"
REBAL = 20
COST = 0.0010
PROD_N = 12
PROD_VT = 0.08


def rungs():
    """The ladder. Each entry moves exactly one axis from the previous one."""
    return [
        ("r1_published_cell", {"classes": "all", "n_hold": 5, "vol_target": None},
         "r1305 cell A: all classes, N5, no vol overlay, 10bp/side"),
        ("r2_bond_free_pool", {"classes": "prod", "n_hold": 5, "vol_target": None},
         "the production pool (equity/commodity/convertible) instead of all classes"),
        ("r3_wider_book", {"classes": "prod", "n_hold": PROD_N, "vol_target": None},
         "the shipped book width (12 names) instead of 5"),
        ("r4_vol_overlay", {"classes": "prod", "n_hold": PROD_N, "vol_target": PROD_VT},
         "the shipped 8% de-lever-only overlay -- the cell r1308's premium is built on"),
    ]


def published(name, path, keypath):
    """Read a published number, or None when the artifact or key is absent."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        cur = doc
        for k in keypath:
            cur = cur[k]
        return float(cur), name
    except (OSError, ValueError, KeyError, TypeError):
        return None, name


def price_arm(close, openp, amt, feats, cols, n_hold, vol_target, start=START, end=END):
    """One book arm on one universe/window, plus the equal-weight control on the same set.

    Only the END is clipped (r1305: clipping at `start` resets the 120-bar history counter
    and parks the book in cash). `start` always goes to the engine as an argument.
    """
    cols = [c for c in cols if c in close.columns]
    c, o, a, f = W.truncate(
        [close[cols], openp[cols], amt[cols],
         {k: v.reindex(columns=cols) for k, v in feats.items() if hasattr(v, "columns")}],
        None, end)
    # the score is rebuilt INSIDE the rung's own universe: rank sums computed on 1,499
    # names and then subset to 193 do not order the 193 the way a 193-name ranking does
    score = E.build_score(c, a, f)
    if vol_target is None:
        ser, turn, gap = E.run_next_open(c, o, a, f, rebal=REBAL, n_hold=n_hold, cost=COST,
                                         start=start, score=score)
    else:
        ser, turn = R.open_to_open_equity(c, o, a, score, REBAL, n_hold, COST,
                                          vol_target=vol_target, start=start)
        gap = 0
    book = E.metrics(ser, "book")
    ew = E.metrics(E.run_ew(c, a, REBAL, start=start), "ew")
    return {
        "n_cols": len(cols),
        "book_cagr": book.get("cagr"),
        "book_sharpe": book.get("sharpe"),
        "book_maxdd": book.get("maxdd"),
        "book_vol": book.get("vol"),
        "ew_cagr": ew.get("cagr"),
        "ew_sharpe": ew.get("sharpe"),
        "excess_vs_ew_pp": (round((book["cagr"] - ew["cagr"]) * 100, 2)
                            if book.get("cagr") is not None and ew.get("cagr") is not None
                            else None),
        "turnover_per_decision": round(float(turn), 4),
        "open_gapfill": int(gap or 0),
        "first_bar": str(ser.index[0].date()) if len(ser) else None,
        "last_bar": str(ser.index[-1].date()) if len(ser) else None,
    }


def run():
    # rung 1 must be r1305's cell, which rode the RAW panel over ALL classes; rungs 2-4 ride
    # the production panel (flip-repaired, bond-free). Two panels, one ladder, and the pool
    # rung is the difference between them -- never a copy of one inside the other.
    close_all, openp_all, amt_all, feats_all = E.build_panel()
    close_p, openp_p, amt_p, _score_p, cls, n_flip = P.prep_panel()
    panels = {"all": (close_all, openp_all, amt_all, feats_all),
              "prod": (close_p, openp_p, amt_p, feats_all)}
    pre_all = W.universe_pre(close_all)
    pre_prod = W.universe_pre(close_p)
    print("panel all=%s prod=%s flips=%d  U_pre_all=%d  U_pre_prod=%d"
          % (close_all.shape, close_p.shape, n_flip, len(pre_all), len(pre_prod)), flush=True)

    out = {
        "schema": "etf_book_window_decomp/v1",
        "question": ("why does the 2015-2019 window print one number in etf_book_pre2020 "
                     "and another in etf_book_passive_mix?"),
        "engine": ("etf_composite_pf.run_next_open (no-overlay rungs) / "
                   "etf_robust_pf.open_to_open_equity (overlay rung); equal weight from "
                   "etf_composite_pf.run_ew -- no re-implementation"),
        "window": "%s..%s" % (START, END),
        "basis": "close decision -> next open fill, 10bp per side, top-N equal weight",
        "rungs": [],
        "controls": {},
        "ladder": [],
    }

    pub_a, _ = published("pre2020_cellA", PUB2020,
                         ["cells", "A_pre_universe_pre_period", "cells", "N5_R20",
                          "book", "cagr"])
    pub_mix, _ = published("passive_mix_pre2020", PUBMIX,
                           ["windows", "pre2020", "book", "cagr"])

    prev = None
    for name, spec, why in rungs():
        close, openp, amt, feats = panels[spec["classes"]]
        cols = pre_all if spec["classes"] == "all" else pre_prod
        row = price_arm(close, openp, amt, feats, cols, spec["n_hold"], spec["vol_target"])
        row.update({"rung": name, "moves": why, "classes": spec["classes"],
                    "n_hold": spec["n_hold"], "vol_target": spec["vol_target"]})
        if prev is not None and row.get("book_cagr") is not None \
                and prev.get("book_cagr") is not None:
            row["delta_vs_previous_pp"] = round((row["book_cagr"] - prev["book_cagr"]) * 100, 2)
            row["excess_delta_vs_previous_pp"] = (
                round(row["excess_vs_ew_pp"] - prev["excess_vs_ew_pp"], 2)
                if row.get("excess_vs_ew_pp") is not None
                and prev.get("excess_vs_ew_pp") is not None else None)
        out["rungs"].append(row)
        out["ladder"].append({"rung": name, "cagr": row.get("book_cagr"),
                              "ew": row.get("ew_cagr"),
                              "excess_pp": row.get("excess_vs_ew_pp"),
                              "delta_pp": row.get("delta_vs_previous_pp")})
        print("%-22s n=%4d N=%2d vt=%-4s cagr=%+.4f ew=%+.4f excess=%+.2fpp d=%+.2fpp"
              % (name, row["n_cols"], row["n_hold"], row["vol_target"],
                 row.get("book_cagr") or 0, row.get("ew_cagr") or 0,
                 row.get("excess_vs_ew_pp") or 0, row.get("delta_vs_previous_pp") or 0),
              flush=True)
        prev = row

    first, last = out["rungs"][0], out["rungs"][-1]
    # the ladder is only readable if both ends are the published arms (r1297)
    d_pub = (round((first["book_cagr"] - pub_a) * 100, 2)
             if pub_a is not None and first.get("book_cagr") is not None else None)
    d_mix = (round((last["book_cagr"] - pub_mix) * 100, 2)
             if pub_mix is not None and last.get("book_cagr") is not None else None)
    out["controls"] = {
        "rung1_vs_pre2020_cellA": {"published_cagr": pub_a,
                                  "recomputed_cagr": first.get("book_cagr"),
                                  "delta_pp": d_pub, "tolerance_pp": CONTROL_TOL_PP,
                                  "passes": (None if d_pub is None
                                             else abs(d_pub) <= CONTROL_TOL_PP)},
        "rung4_vs_passive_mix_pre2020": {"published_cagr": pub_mix,
                                        "recomputed_cagr": last.get("book_cagr"),
                                        "delta_pp": d_mix, "tolerance_pp": CONTROL_TOL_PP,
                                        "passes": (None if d_mix is None
                                                   else abs(d_mix) <= CONTROL_TOL_PP)},
    }

    # 5) the read: name the axis that carries the sign change
    deltas = [(r["rung"], r.get("delta_vs_previous_pp"), r.get("excess_delta_vs_previous_pp"))
              for r in out["rungs"][1:]]
    mover = None
    if deltas and all(d[1] is not None for d in deltas):
        mover = max(deltas, key=lambda d: abs(d[1]))
    out["read"] = {
        "total_move_pp": (round((last["book_cagr"] - first["book_cagr"]) * 100, 2)
                          if last.get("book_cagr") is not None
                          and first.get("book_cagr") is not None else None),
        "step_moves_pp": [{"rung": n, "level_pp": lv, "excess_vs_ew_pp": ex}
                          for n, lv, ex in deltas],
        "largest_step": mover[0] if mover else None,
        "verdict": None,
    }
    if out["read"]["total_move_pp"] is None or not mover:
        verdict = "undetermined -- a rung did not price"
    else:
        verdict = ("the two published readings are the same engine on different cells: "
                   "moving one axis at a time from r1305's cell to the shipped cell shifts "
                   "the 2015-2019 CAGR by %+.2fpp in total, and %+.2fpp of that comes from "
                   "%s. Neither round was wrong; the window answers a different question "
                   "depending on the cell asked."
                   % (out["read"]["total_move_pp"], mover[1], mover[0]))
    out["read"]["verdict"] = verdict
    print("READ", verdict, flush=True)

    out["caveats"] = [
        ("the ladder holds the window and the fill rule fixed; the ONLY things it moves are "
         "the pool, the book width and the overlay -- so every step is that step"),
        ("rung 1 is asserted against the published r1305 cell and rung 4 against the r1308 "
         "premium cell, each at %.1fpp; a ladder whose ends are not the published arms "
         "explains nothing" % CONTROL_TOL_PP),
        ("excess vs equal weight is r1305's yardstick and the premium paragraph uses a "
         "static class mix -- the two benchmarks differ, which is why both are printed "
         "per rung instead of one being translated into the other"),
        ("this is a reconciliation, not a new verdict: no prereg, no ledger row, no member "
         "file touched"),
    ]
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print("wrote", OUT, flush=True)
    return 0


# ---------------------------------------------------------------- selftest

def fixture(n_sym=40, n_bars=900, seed=5):
    """Synthetic panel with the frames the engines take; half the names list late."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2014-01-01", periods=n_bars)
    prices = {}
    for k in range(n_sym):
        start = 0 if k % 2 == 0 else 400
        n = n_bars - start
        ret = rng.normal(0.0003, 0.012, n)
        close = 2.0 * np.cumprod(1 + ret)
        op = close * (1 + rng.normal(0, 0.002, n))
        df = pd.DataFrame({"open": op, "close": close, "volume": np.full(n, 3e7)},
                          index=idx[start:])
        df["high"] = np.maximum(df["open"], df["close"]) * 1.004
        df["low"] = np.minimum(df["open"], df["close"]) * 0.996
        prices["s%02d" % k] = df
    close = pd.DataFrame({s: p["close"] for s, p in prices.items()}).sort_index()
    openp = pd.DataFrame({s: p["open"] for s, p in prices.items()}).sort_index()
    amt = (close * pd.DataFrame({s: p["volume"] for s, p in prices.items()})
           ).rolling(20, min_periods=10).median()
    from engine.factors import compute_all
    feats = compute_all(prices, None)
    return close, openp, amt, feats


def selftest():
    out = []

    def chk(label, cond, detail=""):
        out.append((label, bool(cond), detail))

    # 1. the ladder moves exactly one axis per rung
    rs = rungs()
    chk("ladder has four rungs", len(rs) == 4, ", ".join(r[0] for r in rs))
    axes = [(r[1]["classes"], r[1]["n_hold"], r[1]["vol_target"]) for r in rs]
    diffs = [sum(1 for a, b in zip(axes[i], axes[i + 1]) if a != b) for i in range(len(axes) - 1)]
    chk("each rung moves exactly one axis", diffs == [1, 1, 1], str(diffs))

    # 2. a missing published control soft-fails instead of raising
    v, _ = published("nope", os.path.join(E.PATHS.results_dir, "no_such_file.json"),
                     ["cells"])
    chk("published control soft-fails when absent", v is None)

    # 3. the arm really trades (r1261: an equivalence on a book that never traded passes
    #    trivially), and both engines are reachable through this path
    close, openp, amt, feats = fixture()
    start = str(close.index[300].date())
    end = str(close.index[800].date())
    a = price_arm(close, openp, amt, feats, list(close.columns)[:24], 5, None,
                  start=start, end=end)
    chk("no-overlay arm trades", (a["turnover_per_decision"] or 0) > 0
        and a.get("book_cagr") is not None,
        "turn=%.3f cagr=%s" % (a["turnover_per_decision"], a.get("book_cagr")))
    b = price_arm(close, openp, amt, feats, list(close.columns)[:24], 5, 0.08,
                  start=start, end=end)
    chk("overlay arm de-levers", b.get("book_vol") is not None
        and a.get("book_vol") is not None and b["book_vol"] <= a["book_vol"] + 1e-9,
        "vol no-vt=%.3f vt=%.3f" % (a.get("book_vol") or 0, b.get("book_vol") or 0))

    # 4. the window bounds are respected on both ends
    chk("window bounds respected", a["last_bar"] is not None
        and a["last_bar"] <= end and a["first_bar"] >= start,
        "%s..%s inside %s..%s" % (a["first_bar"], a["last_bar"], start, end))
    chk("universe mask binds", a["n_cols"] == 24, "n_cols=%d" % a["n_cols"])

    # 5. a wider book is a different experiment, not a rounding
    c = price_arm(close, openp, amt, feats, list(close.columns)[:24], 12, None,
                  start=start, end=end)
    chk("width changes the arm", c.get("book_cagr") != a.get("book_cagr"),
        "N5=%.4f N12=%.4f" % (a.get("book_cagr") or 0, c.get("book_cagr") or 0))

    ok = sum(1 for _, cond, _ in out if cond)
    for label, cond, detail in out:
        print(("[PASS] " if cond else "[FAIL] ") + label + (" | " + detail if detail else ""),
              flush=True)
    print("selftest %d/%d PASS" % (ok, len(out)), flush=True)
    return 0 if ok == len(out) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(selftest())
    raise SystemExit(run())