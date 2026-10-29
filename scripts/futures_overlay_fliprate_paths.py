"""Futures-overlay flip damper: PATH TEST before adoption (E188 law).

Why this exists
---------------
`futures_overlay_fliprate.py` measured a real win for one damper arm: strength-hold at
theta=2% cuts sign flips by 72% and moves the breakeven from 1bp to 10bp. But that number
came from ONE decision sequence on ONE panel. r1325 taught the hard way that a single
sequence can be a phase, not an effect: the buffer arm looked like +0.07pp and turned into
-0.24pp once the decision grid was started one week later.

A daily-rebalanced sleeve has no rebalance grid to shift, so the paths that can actually
differ are:

  full          the published measurement window
  is / oos      the era split (<= 2023-12-31 vs 2024-01-01+, the same split every other
                face in this repo reports)
  lag2 / lag3   the same signal executed one and two bars later (execution-timing path)
  loo_<variety> the panel with one variety removed (weights renormalise -> a different
                decision sequence, not just a shorter one)

The adoption rule is FROZEN in ADOPT_RULE below, echoed verbatim into the artifact, and
the verdict is recomputed from the cell rows -- never hand-written (E188 56 小而美).

Honest scope: still a measurement face. It selects nothing by itself; it only says whether
the damper is safe to hand to the production book. Roll cost / margin / carry are still
not modelled, and the ETF leg's universe is survivors.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import futures_tsmom_probe as P                      # noqa: E402
import futures_overlay_sweep as S                    # noqa: E402
import futures_overlay_fliprate as FR                # noqa: E402
from config import PATHS                             # noqa: E402

LOOKBACKS = {"tsmom60": 60, "tsmom120": 120}
# the two arms r1140 published as the only survivors worth arguing about
CANDIDATES = {
    "strength_hold_2pct": ({"mechanism": "strength_hold", "theta": 0.02, "k": None},
                           lambda mom: FR.strength_hold(mom, 0.02)),
    "confirm_3d": ({"mechanism": "confirm_kd", "theta": None, "k": 3},
                   lambda mom: FR.confirm_kd(mom, 3)),
}
F = S.BREAKEVEN_WEIGHT
COSTS = [5.0, 10.0]            # the levels the shipped sleeve cannot clear today

IS_END = "2023-12-31"
OOS_START = "2024-01-01"
LAGS = [2, 3]

# ---------------------------------------------------------------- frozen adoption rule
ADOPT_RULE = {
    "primary_cost_bp": 10.0,
    "secondary_cost_bp": 5.0,
    "min_positive_share": 0.75,      # >= 3/4 of the path cells must improve
    "worst_cell_floor_pp": -1.0,     # no single path may lose more than 1pp/yr
    "require_full_positive": True,
    "require_oos_positive": True,
}


# ---------------------------------------------------------------- engine (mirrors probe)
def run_weights_lag(close, w, cost, lag=1):
    """Net daily returns when a weight decided at t is executed `lag` bars later."""
    rets = close.pct_change().fillna(0.0)
    held = w.shift(int(lag)).fillna(0.0)
    gross = (held * rets).sum(axis=1)
    turn = (held - held.shift(1).fillna(0.0)).abs().sum(axis=1)
    return pd.Series(gross - turn * cost, index=close.index), float(turn.sum())


def equal_risk_face(book_r, book_vol, sleeve_r, window=None):
    idx = book_r.index.intersection(sleeve_r.index)
    if window is not None:
        lo, hi = window
        if lo is not None:
            idx = idx[idx >= lo]
        if hi is not None:
            idx = idx[idx <= hi]
    e = book_r.reindex(idx).fillna(0.0)
    s = sleeve_r.reindex(idx).fillna(0.0)
    eq = S.eq_from_returns(S.blend_returns(e, s, F))
    return P.vol_normalize(eq, book_vol)


def cell_specs(close):
    """Every path this face is willing to judge the arm on."""
    specs = [{"name": "full", "close": close, "lag": 1, "window": None},
             {"name": "is", "close": close, "lag": 1, "window": (None, IS_END)},
             {"name": "oos", "close": close, "lag": 1, "window": (OOS_START, None)}]
    for lag in LAGS:
        specs.append({"name": "lag%d" % lag, "close": close, "lag": lag, "window": None})
    for v in list(close.columns):
        specs.append({"name": "loo_%s" % v, "close": close.drop(columns=[v]),
                      "lag": 1, "window": None})
    return specs


def arm_cells(close, book_r, book_vol, lookback, cand_fn, specs=None):
    """delta (pp of CAGR, equal risk) of the candidate vs the base, per path cell."""
    specs = specs if specs is not None else cell_specs(close)
    rows = []
    for sp in specs:
        c = sp["close"]
        mom = c.pct_change(lookback)
        w_b = P.tsmom_weights(c, lookback=lookback, signs=FR.base_signs(mom))
        w_c = P.tsmom_weights(c, lookback=lookback, signs=cand_fn(mom))
        row = {"cell": sp["name"], "lag": sp["lag"], "varieties": int(c.shape[1])}
        for cost in COSTS:
            rb, tb = run_weights_lag(c, w_b, cost / 10000.0, sp["lag"])
            rc, tc = run_weights_lag(c, w_c, cost / 10000.0, sp["lag"])
            sb = P.stats(equal_risk_face(book_r, book_vol, rb, sp["window"]), "base")
            sc = P.stats(equal_risk_face(book_r, book_vol, rc, sp["window"]), "cand")
            key = "%gbp" % cost
            if sb.get("cagr") is None or sc.get("cagr") is None:
                row["delta_pp_" + key] = None
                row["base_cagr_" + key] = None
            else:
                row["delta_pp_" + key] = round((sc["cagr"] - sb["cagr"]) * 100, 2)
                row["base_cagr_" + key] = sb["cagr"]
            row["turnover_" + key] = round(tc, 1)
        rows.append(row)
    return rows


def gate(cells, rule=None):
    """The frozen rule applied to the measured cells. Returns the verdict AND why."""
    rule = dict(rule or ADOPT_RULE)
    key = "delta_pp_%gbp" % rule["primary_cost_bp"]
    vals = [(r["cell"], r[key]) for r in cells if r.get(key) is not None]
    if not vals:
        return {"verdict": "NOT-ASSESSED", "reasons": ["no cells measured"],
                "share_positive": None, "worst_cell_pp": None}
    deltas = [v for _c, v in vals]
    pos = [d for d in deltas if d > 0]
    share = round(len(pos) / len(deltas), 3)
    worst = min(deltas)
    by_name = dict(vals)
    reasons = []
    if share < rule["min_positive_share"]:
        reasons.append("positive share %.3f < %.2f" % (share, rule["min_positive_share"]))
    if worst < rule["worst_cell_floor_pp"]:
        reasons.append("worst cell %.2f pp < floor %.2f pp"
                       % (worst, rule["worst_cell_floor_pp"]))
    if rule["require_full_positive"] and (by_name.get("full") or 0.0) <= 0:
        reasons.append("full-window delta %s pp is not positive" % by_name.get("full"))
    if rule["require_oos_positive"] and (by_name.get("oos") or 0.0) <= 0:
        reasons.append("out-of-sample delta %s pp is not positive" % by_name.get("oos"))
    worst_cell = min(vals, key=lambda t: t[1])[0]
    return {"verdict": "ADOPT" if not reasons else "REJECT",
            "share_positive": share, "worst_cell_pp": worst, "worst_cell": worst_cell,
            "n_cells": len(deltas), "reasons": reasons or ["clears every leg of the rule"]}


def pick_adopted(arms):
    """If more than one arm passes, publish the one with the best worst case."""
    passed = [(lab, a) for lab, a in arms.items() if a["adoption"]["verdict"] == "ADOPT"]
    if not passed:
        return None, "no arm passes the frozen rule"
    passed.sort(key=lambda t: -(t[1]["adoption"]["worst_cell_pp"] or -9))
    return passed[0][0], ("best worst-case among %d passing arm(s)" % len(passed))


# ---------------------------------------------------------------- render
def render_md(out):
    L = ["# Futures overlay: flip damper path test", "",
         "Generated by `scripts/futures_overlay_fliprate_paths.py`. Measurement face - "
         "selects nothing, changes no book, places no order.", "",
         "evidence_cutoff: %s" % out["evidence_cutoff"], "",
         "Frozen adoption rule (echoed from `ADOPT_RULE` in the script):", "",
         "```json", json.dumps(out["adoption_rule"], indent=2), "```", "",
         "**Overall: %s** (%s)" % (out["overall_verdict"], out["overall_reason"]), ""]
    for lab, a in out["arms"].items():
        ad = a["adoption"]
        L += ["## %s" % lab, "",
              "- verdict: **%s** - share positive %s of %s cells, worst cell %s (%s pp)"
              % (ad["verdict"], ad["share_positive"], ad["n_cells"], ad.get("worst_cell"),
                 ad.get("worst_cell_pp")),
              "- why: %s" % "; ".join(ad["reasons"]), "",
              "| cell | lag | varieties | delta pp @5bp | delta pp @10bp | base CAGR @10bp |",
              "|---|---|---|---|---|---|"]
        for r in a["cells"]:
            L.append("| %s | %d | %d | %s | %s | %s |"
                     % (r["cell"], r["lag"], r["varieties"],
                        r.get("delta_pp_5bp"), r.get("delta_pp_10bp"),
                        r.get("base_cagr_10bp")))
        L.append("")
    L += ["## Not modelled", "", out["not_modelled"], ""]
    L += consumer_section()
    return "\n".join(L) + "\n"


def consumer_section(artifact=None):
    """Who reads this verdict, rendered from the consumer's own artifact.

    This block used to be hand-appended, so every regeneration silently deleted it and the
    ADOPT verdict went back to having no reader on paper (r1143 caught the same deletion and
    restored it by hand -- which is why it came back). Deriving it from the consumer's JSON
    makes the section survive a re-run, and makes it say "nothing is wired" when nothing is.
    """
    if artifact is None:
        artifact = os.path.join(PATHS.results_dir, "futures_tsmom_signal.json")
    try:
        with open(artifact, encoding="utf-8") as fh:
            a = json.load(fh)
    except (OSError, ValueError):
        return ["## Consumer", "",
                "No consumer artifact on disk (`results/futures_tsmom_signal.json`), so nothing "
                "downstream is applying this verdict yet.", ""]
    ao = a.get("adopted_overlay") or {}
    fl = ao.get("flips") or {}
    if not ao or not fl:
        return ["## Consumer", "",
                "`results/futures_tsmom_signal.json` carries no `adopted_overlay` block -- the "
                "shadow face is not applying this verdict.", ""]
    same = ao.get("differs_today") or []
    return ["## Consumer", "",
            "The shadow face `scripts/futures_tsmom_signal.py` reads this artifact's rule "
            "(arm `%s`) and executes the same mechanism module, printing both books side by side. "
            "On %s: flips %s -> %s (cut %s%%), today's legs %s, gross %s."
            % (ao.get("arm"), a.get("generated_for_bar"), fl.get("raw"), fl.get("damped"),
               fl.get("cut_pct"),
               "identical" if not same else "%d differ" % len(same), ao.get("gross")), "",
            "Page: `docs/futures_lane/TSMOM-%s.md`; machine face: `results/futures_tsmom_signal.json`"
            " -> `adopted_overlay`. Re-running the path test rewrites that page on its next run; it "
            "never applies a rule the verdict does not currently hold." % a.get("generated_for_bar"), ""]


# ---------------------------------------------------------------- run
def run():
    close = P.load_panel()
    book, book_meta = P.etf_book_series()
    book_r = P.daily_returns(book)
    book_vol = float(book_r.std() * np.sqrt(252))

    specs = cell_specs(close)
    arms = {}
    for tag, lb in LOOKBACKS.items():
        for cname, (spec, fn) in CANDIDATES.items():
            label = "%s_%s" % (tag, cname)
            cells = arm_cells(close, book_r, book_vol, lb, fn, specs)
            arms[label] = {
                "label": label,
                "spec": {"lookback": lb, "mechanism": spec["mechanism"],
                         "theta": spec["theta"], "k": spec["k"]},
                "cells": cells,
                "adoption": gate(cells),
            }

    adopted, why = pick_adopted(arms)
    out = {
        "evidence_cutoff": str(close.index[-1].date()),
        "face": "path test of the flip damper; selects nothing, changes no book, no order",
        "adoption_rule": ADOPT_RULE,
        "anchor": {"book_vol": round(book_vol, 4), "blend_weight": round(F, 4),
                   "book_meta": book_meta},
        "legs": {"futures_sleeve": {"bars": int(close.shape[0]),
                                    "varieties": int(close.shape[1]),
                                    "varieties_list": [str(c) for c in close.columns]}},
        "cells_tested": [s["name"] for s in specs],
        "arms": arms,
        "adopted_arm": adopted,
        "overall_verdict": "ADOPT" if adopted else "REJECT",
        "overall_reason": why,
        "not_modelled": ("roll cost, margin, financing/carry, contract multipliers; the ETF "
                         "leg's universe is survivors; the cells are chosen before the run "
                         "and are not tuned on the result"),
    }

    p = os.path.join(PATHS.results_dir, "futures_overlay_fliprate_paths.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    md_path = os.path.join(os.path.dirname(PATHS.results_dir),
                           "research", "FUTURES_OVERLAY_FLIPRATE_PATHS.md")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(render_md(out))

    print("\ncells: %s" % ", ".join(out["cells_tested"]), flush=True)
    for lab, a in arms.items():
        ad = a["adoption"]
        print("  %-28s %-6s share=%s worst=%.2f (%s)"
              % (lab, ad["verdict"], ad["share_positive"], ad["worst_cell_pp"],
                 ad.get("worst_cell")), flush=True)
        for r in a["cells"]:
            print("      %-22s lag%d d5=%6s d10=%6s"
                  % (r["cell"], r["lag"], r.get("delta_pp_5bp"), r.get("delta_pp_10bp")),
                  flush=True)
    print("\nOVERALL: %s (%s)" % (out["overall_verdict"], out["overall_reason"]), flush=True)
    print("saved %s\nsaved %s" % (p, md_path), flush=True)
    return 0


# ---------------------------------------------------------------- selftest
def _fixture(n=1500, seed=11):
    rng = np.random.RandomState(seed)
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    close = pd.DataFrame({c: 100.0 * np.exp(np.cumsum(rng.normal(0.0002, 0.012, n)))
                          for c in ["a", "b", "c"]}, index=idx)
    book_r = pd.Series(rng.normal(0.0003, 0.008, n), index=idx)
    return close, book_r


def selftest():
    ok = total = 0

    def chk(label, cond, detail=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print("[PASS] %s | %s" % (label, detail))
        else:
            print("[FAIL] %s | %s" % (label, detail))

    close, book_r = _fixture()
    book_vol = float(book_r.std() * np.sqrt(252))
    specs = cell_specs(close)

    # 1 identity: an arm identical to the base must move nothing on ANY path
    ident = arm_cells(close, book_r, book_vol, 20, FR.base_signs, specs)
    chk("L1 a no-op arm returns exactly 0.00 pp on every cell and cost",
        all(r.get("delta_pp_10bp") == 0.0 and r.get("delta_pp_5bp") == 0.0 for r in ident),
        "cells=%d" % len(ident))

    # 2 liveness: the cells really traded (a fixture too short for the 60d vol window
    #   would return None everywhere and let every leg pass on nothing -- the r1261 trap)
    live = arm_cells(close, book_r, book_vol, 20, lambda m: FR.strength_hold(m, 0.02), specs)
    chk("L2 the cells are live (turnover > 0 and a CAGR on every row)",
        all((r.get("turnover_10bp") or 0) > 0 and r.get("delta_pp_10bp") is not None
            for r in live) and len(live) == len(specs),
        "cells=%d min_turn=%.1f" % (len(live), min(r["turnover_10bp"] for r in live)))

    # 3 the execution-lag cells really execute later: a single one-day unit position must
    #   earn its return one bar later at lag=1 and two bars later at lag=2 (a relabelled
    #   copy would earn it on the same day)
    spike_idx = pd.date_range("2020-01-06", periods=6, freq="B")
    spike_close = pd.DataFrame({"a": [100.0, 101.0, 102.0, 103.0, 104.0, 105.0]},
                               index=spike_idx)
    spike_w = pd.DataFrame({"a": [0.0, 1.0, 0.0, 0.0, 0.0, 0.0]}, index=spike_idx)
    r1, _ = run_weights_lag(spike_close, spike_w, 0.0, 1)
    r2, _ = run_weights_lag(spike_close, spike_w, 0.0, 2)
    earn1 = int(np.argmax(np.abs(r1.to_numpy())))
    earn2 = int(np.argmax(np.abs(r2.to_numpy())))
    chk("L3 lag n executes the weight n bars later (one day per extra bar, not a copy)",
        earn1 == 2 and earn2 == 3 and not np.allclose(r1.to_numpy(), r2.to_numpy()),
        "earn day index lag1=%d lag2=%d" % (earn1, earn2))

    # 4 leave-one-out covers every variety and each cell really drops exactly one
    loo = [s for s in specs if s["name"].startswith("loo_")]
    chk("L4 leave-one-out covers every variety exactly once",
        len(loo) == close.shape[1]
        and {s["name"] for s in loo} == {"loo_%s" % c for c in close.columns}
        and all(s["close"].shape[1] == close.shape[1] - 1 for s in loo),
        "varieties=%s" % sorted(close.columns))

    # 5 the era split is a partition of the same window (and never overlaps)
    full = close.index
    isidx = full[full <= pd.Timestamp(IS_END)]
    oosidx = full[full >= pd.Timestamp(OOS_START)]
    chk("L5 is/oos partition the full window with no overlap",
        len(isidx) + len(oosidx) == len(full)
        and len(set(isidx) & set(oosidx)) == 0 and len(isidx) > 60 and len(oosidx) > 60,
        "is=%d oos=%d full=%d" % (len(isidx), len(oosidx), len(full)))

    # 6 the gate reads the cells -- four fixtures, four different verdicts
    def cells_of(deltas, names=None):
        names = names or ["full", "is", "oos", "lag2", "lag3", "loo_a", "loo_b", "loo_c"]
        return [{"cell": n, "delta_pp_10bp": d} for n, d in zip(names, deltas)]

    good = cells_of([0.9, 0.5, 0.6, 0.4, 0.3, 0.7, 0.2, 0.1])
    thin = cells_of([0.9, 0.5, 0.6, 0.4, 0.3, -0.2, -0.3, -0.4])   # 5/8 = 0.625
    floor = cells_of([0.9, 0.5, 0.6, 0.4, 0.3, 0.2, 0.1, -2.5])    # 7/8 but one blow-up
    badfull = cells_of([-0.1, 0.5, 0.6, 0.4, 0.3, 0.2, 0.1, 0.2])
    bad_oos = cells_of([0.9, 0.5, -0.6, 0.4, 0.3, 0.2, 0.1, 0.2])
    chk("L6 the gate passes a clean sweep and rejects on share / floor / full / oos",
        gate(good)["verdict"] == "ADOPT" and gate(thin)["verdict"] == "REJECT"
        and gate(floor)["verdict"] == "REJECT" and gate(badfull)["verdict"] == "REJECT"
        and gate(bad_oos)["verdict"] == "REJECT",
        "share=%.3f/%s worst=%.1f" % (gate(thin)["share_positive"],
                                      gate(floor)["share_positive"],
                                      gate(floor)["worst_cell_pp"]))

    # 7 the verdict is recomputed from the rows, and the reason names the actual cause
    g1, g2 = gate(thin), gate(thin)
    chk("L7 the verdict is deterministic and the reason names its own cause",
        g1 == g2 and any("positive share" in r for r in g1["reasons"])
        and any("worst cell" in r for r in gate(floor)["reasons"]),
        str(g1["reasons"]))

    # 8 an empty measurement is NOT a rejection dressed up as success
    chk("L8 no measurable cell yields NOT-ASSESSED, never ADOPT",
        gate([{"cell": "full", "delta_pp_10bp": None}])["verdict"] == "NOT-ASSESSED")

    # 9 the published rule is the one the gate used (echo == enforcement)
    chk("L9 the echoed rule is the rule the gate enforces",
        gate(good, ADOPT_RULE) == gate(good)
        and set(ADOPT_RULE) >= {"primary_cost_bp", "min_positive_share",
                                "worst_cell_floor_pp"}
        and ADOPT_RULE["primary_cost_bp"] in COSTS)

    # 10 pick_adopted cannot invent an arm: an all-reject book returns None
    fake = {"x": {"adoption": {"verdict": "REJECT", "worst_cell_pp": 1.0}}}
    chk("L10 no passing arm means no adopted arm",
        pick_adopted(fake)[0] is None and pick_adopted({"y": {"adoption":
                      {"verdict": "ADOPT", "worst_cell_pp": -0.1}}})[0] == "y")

    # 11 the window slice really shortens the measured face
    long_f = equal_risk_face(book_r, book_vol, book_r, None)
    short_f = equal_risk_face(book_r, book_vol, book_r, (OOS_START, None))
    chk("L11 a cell window really restricts the measured series",
        len(short_f) < len(long_f) and short_f.index.min() >= pd.Timestamp(OOS_START),
        "long=%d short=%d" % (len(long_f), len(short_f)))

    # 12 the rendered doc must keep a Consumer section, derived from the consumer artifact
    # (this section was hand-appended and every regeneration deleted it -- r1143/r1145)
    import tempfile as _tf
    _td = _tf.mkdtemp()
    _fake = os.path.join(_td, "sig.json")
    with open(_fake, "w", encoding="utf-8") as _fh:
        json.dump({"generated_for_bar": "2026-10-28",
                   "adopted_overlay": {"arm": "tsmom60_strength_hold_2pct", "gross": 3.0,
                                       "differs_today": [],
                                       "flips": {"raw": 1469, "damped": 412, "cut_pct": 72.0}}},
                  _fh)
    _sec = "\n".join(consumer_section(_fake))
    _none_sec = "\n".join(consumer_section(os.path.join(_td, "absent.json")))
    chk("L12 the doc keeps a Consumer block, and says so honestly when nothing consumes it",
        "## Consumer" in _sec and "1469 -> 412" in _sec and "identical" in _sec
        and "## Consumer" in _none_sec and "nothing downstream" in _none_sec
        and "## Consumer" in render_md({"evidence_cutoff": "x", "adoption_rule": {},
                                        "overall_verdict": "ADOPT",
                                        "overall_reason": "r", "arms": {},
                                        "not_modelled": "n"}),
        "live-derived and absent-artifact both render")

    print("selftest %d/%d PASS" % (ok, total))
    return 0 if ok == total else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    sys.exit(run())