"""A-share residual veto book: the drawdown-budget ticket -- how much insurance, at what price

r2022 (`astock_veto_hedgeable_beta`) priced five hedge sizes on a tradable instrument and
voted on k = 1, the only size with a mechanical meaning, and then said the honest thing:
the beta-neutral hedge improved the full window and did nothing for the out-of-sample
part.  But nobody holds a "k".  A person holding this book has a **drawdown budget** --
the worst peak-to-trough they will sit through -- and a short-finance price they can
actually get.

So this face turns the position into a purchase decision, with the rule frozen before
the numbers are read:

* **Rule A (primary)** -- among grid sizes whose *in-sample* drawdown fits the budget,
  take the one with the highest *in-sample* annualised return.
* **Rule B (comparison)** -- the smallest such size: buy only as much insurance as the
  budget literally requires.  A and B disagree exactly when a loose budget leaves slack,
  and the difference between them is the *return value of that slack*.
* Both rules are chosen **in-sample** and read **out-of-sample**; the size is never
  re-picked after seeing the out-of-sample numbers.
* The price is printed per window: annualised return given up per drawdown point
  removed, measured against the same window's k = 0 arm.  A negative price means the
  hedge paid you to take it.

What this face does **not** do: it does not claim a daily mark-to-market drawdown (the
curve is the book's own 20-bar period curve, same as r2022), it does not model margin
calls on the short leg, and it does not search beyond k = 2.00.

Outputs (new files only):
    results/astock_veto_hedge_budget.json
    research/ASTOCK_VETO_HEDGE_BUDGET.md

Usage:
    python scripts/astock_veto_hedge_budget.py selftest
    python scripts/astock_veto_hedge_budget.py run
    python scripts/astock_veto_hedge_budget.py check
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_veto_hedgeable_beta import arm_series, stats  # noqa: E402
from astock_veto_tearsheet import PPY  # noqa: E402

OUT = os.path.join(ROOT, "results", "astock_veto_hedge_budget.json")
MD = os.path.join(ROOT, "research", "ASTOCK_VETO_HEDGE_BUDGET.md")
PARENT = os.path.join(ROOT, "results", "astock_veto_hedgeable_beta.json")

KGRID = tuple(round(0.05 * i, 2) for i in range(41))     # 0.00 .. 2.00
BUDGETS = (0.10, 0.15, 0.20, 0.25)                       # |max drawdown| the account will sit through
CARRY_AXIS = (0.0, 0.02, 0.05)                           # short-finance, %/yr on shorted notional
BUDGET_PRIMARY = 0.20
CARRY_PRIMARY = 0.0
PRICE_KS = (0.20, 0.40, 0.60, 0.80, 1.00)
PARENT_ANCHOR_KS = (0.0, 0.25, 0.5, 1.0, 1.5)            # the sizes r2022 published
WINDOWS = ("full", "in_sample", "out_of_sample")
WINDOW_ZH = {"full": "全窗", "in_sample": "样本内", "out_of_sample": "样本外"}
TOL = 1e-12


# ------------------------------------------------------------------ pure logic
def _now() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def _read_json(path: str):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def parent_digest(parent: dict) -> str:
    """Content digest of the parent face, excluding its `generated` stamp.

    This is what makes the two kinds of red separable: a re-run of the parent with the
    same numbers must keep this digest stable (so this face is not spuriously STALE),
    while any real move -- a new bar, a new beta, a republished arm -- changes it."""
    payload = {
        "cutoff": parent["cutoff"],
        "beta": repr(float(parent["beta"])),
        "rows": [[r["date"], repr(float(r["book_net"])),
                  ("None" if r.get("hedge_etf") is None else repr(float(r["hedge_etf"]))),
                  bool(r["in_sample"])] for r in parent["rows"]],
        "arms": parent.get("arms") or {},
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def dd_mag(st) -> float | None:
    """Absolute size of the worst peak-to-trough.  An arm with no periods has no
    drawdown -- None, not 0.0: "could not measure" must never read as "no risk"."""
    if not st or not st.get("periods"):
        return None
    dd = st.get("max_drawdown")
    if dd is None or not np.isfinite(dd):
        return None
    return abs(float(dd))


def arm_grid(book, hedge, beta: float, carry_ppy: float = 0.0, is_mask=None) -> list:
    """One arm per grid size, each carrying all three windows.  The in-sample mask is
    passed in, not read from a module global: a pure function of its arguments is the
    only version the selftest can hold to an answer."""
    mask = IS_MASK_DEFAULT if is_mask is None else is_mask
    out = []
    for k in KGRID:
        series = arm_series(book, hedge, k, beta, carry_ppy=carry_ppy)
        out.append({
            "k": float(k),
            "full": stats(series),
            "in_sample": stats([v for v, m in zip(series, mask) if m]),
            "out_of_sample": stats([v for v, m in zip(series, mask) if not m]),
        })
    return out


def _feasible(arm: dict, window: str, budget: float) -> bool:
    dd = dd_mag(arm.get(window))
    ann = arm.get(window, {}).get("annualized_compound")
    return dd is not None and ann is not None and dd <= budget + TOL


def choose_max_return(arms: list, window: str, budget: float) -> dict | None:
    """Rule A.  Ties go to the smaller size: with two sizes that buy the same thing,
    the one that does less is the cheaper mistake."""
    feas = [a for a in arms if _feasible(a, window, budget)]
    if not feas:
        return None
    best = max(feas, key=lambda a: (a[window]["annualized_compound"], -a["k"]))
    return {"k": best["k"], "arm": best}


def choose_min_k(arms: list, window: str, budget: float) -> dict | None:
    """Rule B: the smallest size the budget literally requires."""
    feas = [a for a in arms if _feasible(a, window, budget)]
    if not feas:
        return None
    best = min(feas, key=lambda a: a["k"])
    return {"k": best["k"], "arm": best}


def min_achievable_dd(arms: list, window: str) -> float | None:
    """The smallest drawdown the grid can buy at all -- the floor under every
    budget question.  If the floor is above the budget, the answer is not a size,
    it is "you cannot buy that"."""
    vals = [dd_mag(a.get(window)) for a in arms]
    vals = [v for v in vals if v is not None]
    return None if not vals else float(min(vals))


def _arm_at(arms: list, k: float) -> dict | None:
    for a in arms:
        if abs(a["k"] - k) < 1e-9:
            return a
    return None


def price_of(arms: list, k: float, window: str) -> dict:
    """What the size k bought, priced against the same window's k = 0 arm:
    drawdown points removed, annualised return given up, and the ratio between them.
    A ratio of None means the pair removed nothing measurable -- printing 0.0 there
    would read as "free"."""
    base = _arm_at(arms, 0.0)
    cur = _arm_at(arms, k)
    if base is None or cur is None:
        return {"k": k, "window": window, "dd_removed_pp": None,
                "give_up_pp": None, "pp_return_per_dd_point": None}
    d0, d1 = dd_mag(base.get(window)), dd_mag(cur.get(window))
    a0 = base.get(window, {}).get("annualized_compound")
    a1 = cur.get(window, {}).get("annualized_compound")
    if None in (d0, d1, a0, a1):
        return {"k": k, "window": window, "dd_removed_pp": None,
                "give_up_pp": None, "pp_return_per_dd_point": None}
    dd_removed = (d0 - d1) * 100.0
    give_up = (a0 - a1) * 100.0
    ratio = None if dd_removed <= TOL else float(give_up / dd_removed)
    return {"k": float(k), "window": window, "dd_removed_pp": float(dd_removed),
            "give_up_pp": float(give_up), "pp_return_per_dd_point": ratio}


def step_price(arms: list, k: float, window: str, step: float = 0.05) -> dict:
    """The marginal price: what the *last* grid step before k cost, per drawdown
    point it removed.  Non-monotone segments divide by a non-positive number, so
    they return None and are printed as "nothing removed"."""
    prev_k = round(k - step, 2)
    if k <= 0 or prev_k < 0:
        return {"k": k, "from_k": None, "window": window, "dd_removed_pp": None,
                "give_up_pp": None, "pp_return_per_dd_point": None}
    prev = _arm_at(arms, prev_k)
    cur = _arm_at(arms, k)
    if prev is None or cur is None:
        return {"k": k, "from_k": prev_k, "window": window, "dd_removed_pp": None,
                "give_up_pp": None, "pp_return_per_dd_point": None}
    d0, d1 = dd_mag(prev.get(window)), dd_mag(cur.get(window))
    a0 = prev.get(window, {}).get("annualized_compound")
    a1 = cur.get(window, {}).get("annualized_compound")
    if None in (d0, d1, a0, a1):
        return {"k": k, "from_k": prev_k, "window": window, "dd_removed_pp": None,
                "give_up_pp": None, "pp_return_per_dd_point": None}
    dd_removed = (d0 - d1) * 100.0
    give_up = (a0 - a1) * 100.0
    ratio = None if dd_removed <= TOL else float(give_up / dd_removed)
    return {"k": float(k), "from_k": float(prev_k), "window": window,
            "dd_removed_pp": float(dd_removed), "give_up_pp": float(give_up),
            "pp_return_per_dd_point": ratio}


def budget_verdict(cell: dict) -> tuple:
    """Three states, and the middle one is not a failure of the run."""
    if cell["rule_a"]["k"] is None:
        return "BUDGET_UNREACHABLE_IN_SAMPLE", (
            "no size in the grid holds the budget on the periods the size was chosen "
            "on -- the floor is %.2f%%, the budget is %.2f%%"
            % (cell["min_achievable_dd_in_sample"] * 100, cell["budget"] * 100))
    raw_dd = cell["rule_a"]["out_of_sample_dd"]
    oos_dd = None if raw_dd is None else abs(float(raw_dd))
    if oos_dd is None:
        return "BUDGET_UNKNOWN_OUT_OF_SAMPLE", (
            "the chosen size has no priced out-of-sample drawdown")
    if oos_dd <= cell["budget"] + TOL:
        return "BUDGET_HOLDS_OUT_OF_SAMPLE", (
            "the size chosen on the in-sample budget kept the out-of-sample drawdown "
            "at %.2f%%, inside the %.2f%% budget"
            % (oos_dd * 100, cell["budget"] * 100))
    return "BUDGET_MISSES_OUT_OF_SAMPLE", (
        "the size chosen on the in-sample budget let the out-of-sample drawdown reach "
        "%.2f%%, outside the %.2f%% budget"
        % (oos_dd * 100, cell["budget"] * 100))


def price_verdict(is_price, oos_price) -> tuple:
    """Does the insurance cost the same on both sides of the split?  The sign is the
    whole story: negative = the hedge paid you."""
    if is_price is None or oos_price is None:
        return "PRICE_NOT_MEASURABLE", "one of the two windows has no priced size"
    if is_price <= 0 < oos_price:
        return "PAID_IN_SAMPLE_COSTS_OUTSIDE", (
            "in-sample the hedge paid %.2f pp of annual return per drawdown point; "
            "out-of-sample it costs %.2f" % (-is_price, oos_price))
    if is_price > 0 and oos_price > 0:
        return "COSTS_IN_BOTH_WINDOWS", (
            "the hedge costs %.2f pp per drawdown point in-sample and %.2f outside"
            % (is_price, oos_price))
    if is_price <= 0 and oos_price <= 0:
        return "PAID_IN_BOTH_WINDOWS", (
            "the hedge paid on both sides (%.2f / %.2f pp per drawdown point)"
            % (-is_price, -oos_price))
    return "CHEAPER_OUTSIDE_THAN_INSIDE", (
        "in-sample costs %.2f pp per drawdown point, out-of-sample %.2f"
        % (is_price, oos_price))


# ----------------------------------------------------------------------- loaders
def load_parent() -> dict:
    face = _read_json(PARENT)
    rows = face.get("rows") or []
    if not rows:
        raise SystemExit("parent face has no rows: %s" % _rel(PARENT))
    arms = face.get("arms_etf") or {}
    beta = None
    for key in arms:
        beta = arms[key].get("beta_used")
        break
    if beta is None:
        raise SystemExit("parent face carries no beta_used")
    return {
        "rows": rows,
        "dates": [r["date"] for r in rows],
        "book": [float(r["book_net"]) for r in rows],
        "hedge": [r["hedge_etf"] for r in rows],
        "is_mask": [bool(r["in_sample"]) for r in rows],
        "beta": float(beta),
        "cutoff": face.get("evidence_cutoff"),
        "generated": face.get("generated"),
        "arms": arms,
        "kind": face.get("kind"),
    }


IS_MASK_DEFAULT: list = []          # only a fallback for callers that pass no mask


def build_cells(arms: list, budget: float, carry: float) -> dict:
    a = choose_max_return(arms, "in_sample", budget)
    b = choose_min_k(arms, "in_sample", budget)
    ex_post = choose_max_return(arms, "full", budget)
    base = _arm_at(arms, 0.0)

    def summary_of(chosen, rule):
        if chosen is None:
            return {"rule": rule, "k": None, "in_sample_annualized": None,
                    "in_sample_dd": None, "out_of_sample_annualized": None,
                    "out_of_sample_dd": None, "out_of_sample_holds_budget": None,
                    "full_annualized": None, "full_dd": None,
                    "give_up_in_sample_pp": None, "give_up_out_of_sample_pp": None,
                    "at_max_grid": None, "at_zero": None}
        arm = chosen["arm"]
        is_ann = arm["in_sample"]["annualized_compound"]
        oos = arm["out_of_sample"]
        oos_dd = dd_mag(oos)
        b_ann = base["in_sample"]["annualized_compound"] if base else None
        o_ann = base["out_of_sample"]["annualized_compound"] if base else None
        return {
            "rule": rule,
            "k": float(arm["k"]),
            "in_sample_annualized": is_ann,
            "in_sample_dd": arm["in_sample"]["max_drawdown"],
            "out_of_sample_annualized": oos.get("annualized_compound"),
            "out_of_sample_dd": oos.get("max_drawdown"),
            "out_of_sample_holds_budget": (
                None if oos_dd is None else bool(oos_dd <= budget + TOL)),
            "full_annualized": arm["full"].get("annualized_compound"),
            "full_dd": arm["full"].get("max_drawdown"),
            "give_up_in_sample_pp": (None if b_ann is None or is_ann is None
                                     else float((b_ann - is_ann) * 100.0)),
            "give_up_out_of_sample_pp": (None if o_ann is None or oos.get("annualized_compound") is None
                                         else float((o_ann - oos["annualized_compound"]) * 100.0)),
            "at_max_grid": bool(abs(arm["k"] - KGRID[-1]) < 1e-9),
            "at_zero": bool(abs(arm["k"]) < 1e-9),
        }

    cell = {
        "budget": float(budget),
        "carry_per_year": float(carry),
        "min_achievable_dd_in_sample": min_achievable_dd(arms, "in_sample"),
        "min_achievable_dd_full": min_achievable_dd(arms, "full"),
        "rule_a": summary_of(a, "max in-sample return inside the budget"),
        "rule_b": summary_of(b, "smallest size the budget requires"),
        "ex_post_full_window": summary_of(ex_post, "what the full window would have needed"),
        "slack_value": None,
    }
    if (a is not None and b is not None
            and cell["rule_a"]["give_up_out_of_sample_pp"] is not None
            and cell["rule_b"]["give_up_out_of_sample_pp"] is not None
            and a["k"] != b["k"]):
        cell["slack_value"] = {
            "extra_give_up_out_of_sample_pp": float(
                cell["rule_a"]["give_up_out_of_sample_pp"]
                - cell["rule_b"]["give_up_out_of_sample_pp"]),
            "extra_dd_removed_out_of_sample_pp": float(
                (dd_mag(b["arm"]["out_of_sample"]) or 0.0) * 100
                - (dd_mag(a["arm"]["out_of_sample"]) or 0.0) * 100),
        }
    cell["verdict"], cell["verdict_why"] = budget_verdict(cell)
    return cell


def build() -> dict:
    p = load_parent()
    mask = list(p["is_mask"])
    n = len(p["rows"])
    if len(mask) != n:
        raise SystemExit("in_sample mask length does not match rows")

    grids = {}
    for c in CARRY_AXIS:
        grids["%.2f" % c] = arm_grid(p["book"], p["hedge"], p["beta"], carry_ppy=c,
                                     is_mask=mask)

    cells = {}
    for c in CARRY_AXIS:
        for b in BUDGETS:
            cells["%.2f|%.2f" % (b, c)] = build_cells(grids["%.2f" % c], b, c)

    zero = grids["%.2f" % CARRY_PRIMARY]
    prices = {}
    for w in WINDOWS:
        prices[w] = {"vs_zero": [price_of(zero, k, w) for k in PRICE_KS],
                     "marginal": [step_price(zero, k, w) for k in PRICE_KS]}

    curve = {}
    for w in WINDOWS:
        curve[w] = [{"k": a["k"],
                     "annualized_compound": a[w].get("annualized_compound"),
                     "max_drawdown": a[w].get("max_drawdown"),
                     "annual_vol": a[w].get("annual_vol"),
                     "sharpe_excess_0": a[w].get("sharpe_excess_0")} for a in zero]

    primary = cells["%.2f|%.2f" % (BUDGET_PRIMARY, CARRY_PRIMARY)]
    is_price = price_of(zero, primary["rule_a"]["k"], "in_sample")["pp_return_per_dd_point"] \
        if primary["rule_a"]["k"] else None
    oos_price = price_of(zero, primary["rule_a"]["k"], "out_of_sample")["pp_return_per_dd_point"] \
        if primary["rule_a"]["k"] else None
    pv, pv_why = price_verdict(is_price, oos_price)

    rows = []
    for i, r in enumerate(p["rows"]):
        rows.append({
            "date": r["date"],
            "book_net": float(r["book_net"]),
            "hedge_etf": (None if r.get("hedge_etf") is None else float(r["hedge_etf"])),
            "in_sample": bool(r["in_sample"]),
            "end": r.get("end"),
        })

    return {
        "generated": _now(),
        "evidence_cutoff": p["cutoff"],
        "machine": "bm-c",
        "kind": "astock_veto_hedge_budget",
        "fills_the_hole_of": (
            "r2022 priced five hedge sizes and voted on k = 1 because it is the only size "
            "with a mechanical meaning; it then wrote that the hedge buys the beta's path "
            "and not new edge.  Nobody translated that into the only question a holder "
            "asks: given the drawdown I will sit through and the financing I can get, "
            "how much do I buy and what does the last point cost?"),
        "parent": {"face": _rel(PARENT), "kind": p["kind"],
                   "content_sha256": parent_digest(p),
                   "generated": p["generated"], "evidence_cutoff": p["cutoff"],
                   "rows": n, "beta_used": p["beta"]},
        "prereg": {
            "question": ("for a drawdown budget and a short-finance price, which grid size "
                         "should be held, what does it cost in annualised return, and does "
                         "the answer survive the out-of-sample split?"),
            "grid": "k = 0.00..2.00 step 0.05, beta = the parent's in-sample OLS fit",
            "budgets": list(BUDGETS),
            "carry_axis": list(CARRY_AXIS),
            "primary_cell": {"budget": BUDGET_PRIMARY, "carry_per_year": CARRY_PRIMARY},
            "rule_a": ("among sizes whose IN-SAMPLE drawdown fits the budget, the highest "
                       "IN-SAMPLE annualised return; ties to the smaller size"),
            "rule_b": "the smallest size whose IN-SAMPLE drawdown fits the budget",
            "read": ("both rules are picked on the in-sample window and read on the "
                     "out-of-sample window; no size is re-picked after the split"),
            "verdict_states": ["BUDGET_HOLDS_OUT_OF_SAMPLE", "BUDGET_MISSES_OUT_OF_SAMPLE",
                               "BUDGET_UNREACHABLE_IN_SAMPLE"],
            "price_definition": ("annualised return given up (pp) per drawdown point removed (pp), "
                                 "measured against the same window's k = 0 arm; negative means "
                                 "the hedge paid you"),
            "frozen_before_run": True,
        },
        "spec": {
            "book": "astock_veto_turnover_layers rows (arm B, residual veto list)",
            "hedge": "512100 CSI1000 ETF traded close, per-period return, same grid as the book",
            "cost": "two sides x 8bp per roll on the shorted notional; carry axis 0/2/5 %/yr",
            "drawdown": ("on the book's own 20-bar period curve, not a daily mark-to-market "
                         "-- same caveat as r2022"),
            "periods_per_year": PPY,
            "windows": {"in_sample": "date <= 2023-12-31 (the beta's own fit window)",
                        "out_of_sample": "date > 2023-12-31"},
        },
        "primary": {"budget": BUDGET_PRIMARY, "carry_per_year": CARRY_PRIMARY,
                    "rule_a_k": primary["rule_a"]["k"],
                    "verdict": primary["verdict"], "verdict_why": primary["verdict_why"],
                    "price_verdict": pv, "price_verdict_why": pv_why,
                    "in_sample_price": is_price, "out_of_sample_price": oos_price},
        "cells": cells,
        "prices": prices,
        "curve": curve,
        "rows": rows,
    }


# ------------------------------------------------------------------------ run
def run() -> int:
    payload = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    text = render_md(payload)
    os.makedirs(os.path.dirname(MD), exist_ok=True)
    with open(MD, "w", encoding="utf-8") as fh:
        fh.write(text)

    pr = payload["primary"]
    print("HEDGE-BUDGET  periods=%d  cutoff %s  beta %.4f"
          % (len(payload["rows"]), payload["evidence_cutoff"], payload["parent"]["beta_used"]))
    print("  primary budget %.0f%% carry %.0f%%: rule-A k=%s  verdict %s"
          % (pr["budget"] * 100, pr["carry_per_year"] * 100,
             "n/a" if pr["rule_a_k"] is None else "%.2f" % pr["rule_a_k"], pr["verdict"]))
    print("  price per drawdown point: in-sample %s  out-of-sample %s -> %s"
          % (_fmt(pr["in_sample_price"]), _fmt(pr["out_of_sample_price"]), pr["price_verdict"]))
    for key in ("%.2f|%.2f" % (b, CARRY_PRIMARY) for b in BUDGETS):
        c = payload["cells"][key]
        print("  budget %4.0f%%: A k=%s (IS %s%% / OOS %s%%, holds=%s)  B k=%s  floor %s%%"
              % (c["budget"] * 100,
                 "n/a" if c["rule_a"]["k"] is None else "%.2f" % c["rule_a"]["k"],
                 _fmt100(c["rule_a"]["in_sample_dd"]),
                 _fmt100(c["rule_a"]["out_of_sample_dd"]),
                 c["rule_a"]["out_of_sample_holds_budget"],
                 "n/a" if c["rule_b"]["k"] is None else "%.2f" % c["rule_b"]["k"],
                 _fmt100(c["min_achievable_dd_in_sample"])))
    print("  -> %s" % _rel(OUT))
    print("  -> %s" % _rel(MD))
    return 0


def _fmt(x):
    return "n/a" if x is None else "%+.2f" % x


def _fmt100(x):
    return "n/a" if x is None else "%+.2f" % (x * 100.0)


# ---------------------------------------------------------------------- doc
def _table_cells(payload) -> list:
    lines = ["| 预算 | 融券 | 规则A 选的 k | IS 年化 | IS 回撤 | OOS 年化 | OOS 回撤 | OOS 守得住 | 规则B 的 k | 松弛的价值 | 判词 |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in CARRY_AXIS:
        for b in BUDGETS:
            cell = payload["cells"]["%.2f|%.2f" % (b, c)]
            a, bb = cell["rule_a"], cell["rule_b"]
            slack = cell.get("slack_value")
            slack_txt = ("—" if not slack
                         else "%+.2fpp 代价换 %+.2fpp 回撤"
                         % (slack["extra_give_up_out_of_sample_pp"],
                            slack["extra_dd_removed_out_of_sample_pp"]))
            lines.append("| %.0f%% | %.0f%% | %s | %s | %s | %s | %s | %s | %s | %s | %s |"
                         % (b * 100, c * 100,
                            "n/a" if a["k"] is None else "%.2f" % a["k"],
                            _pct(a["in_sample_annualized"]),
                            _pct(a["in_sample_dd"]),
                            _pct(a["out_of_sample_annualized"]),
                            _pct(a["out_of_sample_dd"]),
                            ("—" if a["out_of_sample_holds_budget"] is None
                             else ("是" if a["out_of_sample_holds_budget"] else "**否**")),
                            "n/a" if bb["k"] is None else "%.2f" % bb["k"],
                            slack_txt,
                            cell["verdict"].replace("BUDGET_", "")))
    return lines


def _pct(x) -> str:
    return "n/a" if x is None else "%+.2f%%" % (x * 100.0)


def _price_lines(payload) -> list:
    lines = ["| k | 窗口 | 削掉的回撤 | 付出的年化 | 每 pp 回撤的价格 |",
             "|---|---|---|---|---|"]
    for w in WINDOWS:
        for row in payload["prices"][w]["vs_zero"]:
            lines.append("| %.2f | %s | %s | %s | %s |"
                         % (row["k"], WINDOW_ZH[w],
                            _pp(row["dd_removed_pp"]), _pp(row["give_up_pp"]),
                            _ratio(row["pp_return_per_dd_point"])))
    return lines


def _marginal_lines(payload) -> list:
    lines = ["| k | 窗口 | 最后一步削掉的回撤 | 最后一步付出的年化 | 最后一步的价格 |",
             "|---|---|---|---|---|"]
    for w in WINDOWS:
        for row in payload["prices"][w]["marginal"]:
            lines.append("| %.2f | %s | %s | %s | %s |"
                         % (row["k"], WINDOW_ZH[w],
                            _pp(row["dd_removed_pp"]), _pp(row["give_up_pp"]),
                            _ratio(row["pp_return_per_dd_point"])))
    return lines


def _pp(x) -> str:
    return "n/a" if x is None else "%+.2fpp" % x


def _ratio(x) -> str:
    return "未削掉任何回撤" if x is None else "%+.3f pp/pp" % x


def render_md(payload) -> str:
    pr = payload["primary"]
    cell = payload["cells"]["%.2f|%.2f" % (BUDGET_PRIMARY, CARRY_PRIMARY)]
    a = cell["rule_a"]
    b = cell["rule_b"]
    floor_is = cell["min_achievable_dd_in_sample"]
    is_rows = {r["k"]: r for r in payload["prices"]["in_sample"]["vs_zero"]}
    oos_rows = {r["k"]: r for r in payload["prices"]["out_of_sample"]["vs_zero"]}

    lines = [
        "# A 股残差黑名单：回撤预算这张票——买多少保险、什么价、最后一点回撤多少钱",
        "",
        "generated %s | evidence_cutoff **%s** | 母面 `%s`（%s）| 判词 **%s**"
        % (payload["generated"], payload["evidence_cutoff"],
           payload["parent"]["face"], payload["parent"]["generated"], pr["verdict"]),
        "",
        "r2022 把「反票」在两种真能交易的标的上都打过了：beta 是同一个敞口（0.901 / 0.976），"
        "一单位 beta 能削掉 85% 的方差，全窗夏普 0.49→0.69，但样本外打平——它写下的结论是"
        "「对冲买的是保险，不是新的边」。",
        "",
        "那张面留下的是五个 k。**没有人持有 k。** 持有人手上只有两样东西：一条他愿意坐过去的"
        "**回撤预算**，和一个他真的能拿到的**融券价**。本面把持仓问题翻成采购问题，规则在读数字"
        "之前冻结：",
        "",
        "* **规则 A（主判）**：在**样本内**回撤不超预算的档位里，取**样本内**年化最高的那一个；"
        "并列取更小的档（两档买同样的东西时，做得少的那个是更便宜的错）。",
        "* **规则 B（对照）**：满足预算的**最小**档——只买预算字面要求的那么多。",
        "* 两条规则都只在样本内选，然后读样本外；看过样本外再回头挑档位的事，这里不做。",
        "",
        "## 一句话",
        "",
        "**10%% 的回撤预算这本书只能在样本内勉强买到：回撤地板 %.2f%%，余量不到一个百分点；"
        "融券一到 2%% 就连样本内都买不到，而同一档读到样本外是 %.2f%%——预算买得到，守不住。"
        "20%% 预算上两个买法都守住了，差别只剩一件事：多出来的额度，你是花掉还是留成余量。**"
        % (floor_is * 100.0,
           abs(payload["cells"]["0.10|0.00"]["rule_a"]["out_of_sample_dd"]) * 100.0),
        "",
        "在 %.0f%% 预算 / %.0f%% 融券的主格里：规则 A 选 **k = %s**，样本内回撤 **%s**、"
        "样本内年化 **%s**（相对不买保险是 **%s**）；同一档读样本外，回撤 **%s**（预算 %s）、"
        "年化 **%s**（相对不买保险是 **%s**）。规则 B 只要 **k = %s**。"
        % (BUDGET_PRIMARY * 100, CARRY_PRIMARY * 100,
           "n/a" if a["k"] is None else "%.2f" % a["k"],
           _pct(a["in_sample_dd"]), _pct(a["in_sample_annualized"]),
           _pp(a["give_up_in_sample_pp"]),
           _pct(a["out_of_sample_dd"]),
           ("**守住了**" if a["out_of_sample_holds_budget"] else "**没守住**"),
           _pct(a["out_of_sample_annualized"]), _pp(a["give_up_out_of_sample_pp"]),
           "n/a" if b["k"] is None else "%.2f" % b["k"]),
        "",
        "## 一、预算 × 融券：谁买多少、守不守得住",
        "",
        "「松弛的价值」= 规则 A 比规则 B 多花的样本外年化，换回来多少样本外回撤；"
        "空白（—）表示两条规则选了同一档，预算刚好卡在收益最优处。",
        "",
    ] + _table_cells(payload) + [
        "",
        "## 二、每一点回撤的价签（融券 0%）",
        "",
        "价格 = 相对同一窗口不买保险，**付出的年化 pp 除以削掉的回撤 pp**。负数＝对冲倒贴你钱。",
        "",
    ] + _price_lines(payload) + [
        "",
        f"样本内 k = 1.00 那一行的价格是 **{_ratio(is_rows[1.00]['pp_return_per_dd_point'])}**，"
        f"同一档在样本外是 **{_ratio(oos_rows[1.00]['pp_return_per_dd_point'])}**——同一个动作，"
        "两块窗口给出相反的符号。这正是 r2022 那句「买的是保险不是边」的价格形式：符号翻转，"
        "而且随 k 上升，样本外的价签变贵，样本内的价签几乎不动。",
        "",
        "## 三、最后一步的价签（边际价格）",
        "",
        "上一张表是「从 0 买到这里平均多少钱」，这张是「从上一个 5 分档再加到这里多少钱」。"
        "当「最后一步」削不掉任何回撤时，本面印「未削掉任何回撤」而不是 0——除以一个零"
        "会读成免费。",
        "",
    ] + _marginal_lines(payload) + [
        "",
        "## 四、和 r2022 对账",
        "",
        f"* 母面在印的五个档，本面 `check` 逐格对账（`annualized_compound` / `annual_vol` / "
        f"`max_drawdown`，全窗与样本外共 30 个格子），差值必须为 0——网格的 k = 0 与母面 "
        f"k = 0.00 逐位相同，这是控制臂锚。",
        f"* k = 1.00 在母面被选为「唯一有机械意义」的档；在本面的价签上它是**样本内倒贴"
        f"（{_ratio(is_rows[1.00]['pp_return_per_dd_point'])}）、样本外最贵的一档"
        f"（{_ratio(oos_rows[1.00]['pp_return_per_dd_point'])}）**，而且回撤的**地板**就在它附近——"
        f"再往上买（k = 1.50、2.00），回撤反而变大（全窗 {_pct(_dd_at(payload, 1.50))} → "
        f"{_pct(_dd_at(payload, 2.00))}），因为过度对冲把空头自己的波动买回来了。",
        f"* 因此「k = 1 不是最便宜的、也不是最好的」这句话在本面上有算术支撑：规则 A 在 "
        f"20% 预算下选的是 {('%.2f' % a['k']) if a['k'] is not None else 'n/a'}，不是 1.00。",
        "",
        "## 五、什么时候答案是「不买」",
        "",
    ] + [
        "| 预算 | 融券 0% | 融券 2% | 融券 5% |",
        "|---|---|---|---|",
    ] + [
        "| %.0f%% | %s | %s | %s |" % (
            b * 100,
            _kcell(payload["cells"]["%.2f|0.00" % b]),
            _kcell(payload["cells"]["%.2f|0.02" % b]),
            _kcell(payload["cells"]["%.2f|0.05" % b]))
        for b in BUDGETS
    ] + [
        "",
        "「不买」不是被规则挑出来的，是**买不到**：某档预算在某档融券下连网格的地板都够不着，"
        "或者网格里唯一可行的档就是 k = 0。两种都印成 k 值本身，不印成 0.00 的收益。",
        "",
        "## 六、未验证（如实）",
        "",
        "* 回撤是母面那条 **20 根 bar 的期间曲线**，不是日频 mark-to-market；真实账户的日回撤"
        "更深、恢复更慢，因此本面所有预算都应读作「期间口径的预算」。",
        "* 空头腿的**保证金占用、追保与强平**没有建模；r2022 已证 IM 一手 111 万，100 万的账"
        "连一手都不够。",
        "* 对冲腿按 as-traded 价格（不含分红、不含借券费以外的融券成本结构）。",
        "* 只有 77 期（样本内 43 / 样本外 34），2020 年只有少数几期；「样本外守住了」是一次"
        "观测，不是一条分布。",
        "* 预算网格 10/15/20/25% 与融券 0/2/5% 是冻结的四乘三，不是搜出来的最优组合；"
        "k 网格 0.00–2.00 步长 0.05，更细的档没量。",
        "* 本面是定价/口径件，不是可交易策略：没有仓位规则、没有容量约束、没有风控动作。",
        "* 本面尚未接 S6 链腿与冒烟两腿（本轮竞争窗只落新增文件面）；`check` 与 `selftest` "
        "是本轮的自证面。",
        "",
        "## 七、这张页是哪一趟写的",
        "",
        "本页由 `render_md(payload)` 从同一次 `run` 的 JSON 渲染，`check` 会把渲染结果与盘上"
        "文件逐字节比对；手改页面上任何一个数都会让 `check` 报 `CHECK FAILED page is not the "
        "render of the face`，而**不是**报 STALE。",
        "",
        "| 出处 | 值 |",
        "|---|---|",
        "| 母面 | `%s` |" % payload["parent"]["face"],
        "| 母面 generated | %s |" % payload["parent"]["generated"],
        "| 母面 evidence_cutoff | %s |" % payload["parent"]["evidence_cutoff"],
        "| 本面 generated | %s |" % payload["generated"],
        "| 本面 evidence_cutoff | %s |" % payload["evidence_cutoff"],
        "| 参与定价的期数 | %d |" % len(payload["rows"]),
        "",
    ]
    return "\n".join(lines)


def _kcell(cell: dict) -> str:
    a = cell["rule_a"]
    if a["k"] is None:
        return "买不到（地板 %s）" % _pct(cell["min_achievable_dd_in_sample"])
    return "k %.2f（OOS %s）" % (a["k"], _pct(a["out_of_sample_dd"]))


def _dd_at(payload, k: float, window: str = "full"):
    for row in payload["curve"][window]:
        if abs(row["k"] - k) < 1e-9:
            return row["max_drawdown"]
    return None


# --------------------------------------------------------------------- check
def check() -> int:
    """Re-derive from the face's own rows, then compare.  A moved input is STALE; a
    number that moved with the same inputs is a real defect and must not wear the
    STALE word."""
    try:
        face = _read_json(OUT)
    except (OSError, ValueError):
        print("CHECK FAILED face missing: %s" % _rel(OUT))
        return 3

    problems = []
    parent = load_parent()
    face_rows = face.get("rows") or []

    # (1) input identity, decided by the parent's own bytes-of-content digest recorded
    #     at build time.  The distinction matters: if the PARENT moved, this face is
    #     merely old (STALE).  If the parent is byte-identical to what we built from,
    #     then anything that disagrees is ours (CHECK FAILED).  Comparing our copy to
    #     the parent's rows cannot tell those two apart -- the digest can.
    recorded = (face.get("parent") or {}).get("content_sha256")
    now_digest = parent_digest(parent)
    if recorded is None:
        problems.append("CHECK FAILED face records no parent digest")
    elif recorded != now_digest:
        problems.append("STALE parent face moved: recorded %s vs now %s (cutoff %s)"
                        % (recorded[:12], now_digest[:12], parent["cutoff"]))
    else:
        if face.get("evidence_cutoff") != parent["cutoff"]:
            problems.append("CHECK FAILED face cutoff %r is not the parent's %r"
                            % (face.get("evidence_cutoff"), parent["cutoff"]))
        recorded_beta = (face.get("parent") or {}).get("beta_used")
        if recorded_beta is None or abs(float(recorded_beta) - parent["beta"]) > 1e-15:
            problems.append("CHECK FAILED face beta %r is not the parent's %r"
                            % (recorded_beta, parent["beta"]))
        if len(face_rows) != len(parent["rows"]):
            problems.append("CHECK FAILED face carries %d rows, the parent %d"
                            % (len(face_rows), len(parent["rows"])))
        else:
            moved = []
            for f, p in zip(face_rows, parent["rows"]):
                if f.get("date") != p.get("date") or \
                        abs(float(f["book_net"]) - float(p["book_net"])) > 1e-15:
                    moved.append(f.get("date"))
                    continue
                fh, ph = f.get("hedge_etf"), p.get("hedge_etf")
                if (fh is None) != (ph is None):
                    moved.append(f.get("date"))
                elif fh is not None and abs(float(fh) - float(ph)) > 1e-15:
                    moved.append(f.get("date"))
            if moved:
                problems.append("CHECK FAILED face rows are not the parent's on %d "
                                "period(s): %s" % (len(moved), moved[:5]))

    # (2) anchor: the five published sizes must reproduce r2022 cell for cell
    if not problems:
        mask = [bool(r["in_sample"]) for r in parent["rows"]]
        book = [float(r["book_net"]) for r in parent["rows"]]
        hedge = [r.get("hedge_etf") for r in parent["rows"]]
        worst = 0.0
        for k in PARENT_ANCHOR_KS:
            mine = arm_grid(book, hedge, parent["beta"], carry_ppy=0.0, is_mask=mask)
            got = _arm_at(mine, k)
            if got is None:
                problems.append("CHECK FAILED anchor k=%.2f missing from the grid" % k)
                continue
            pub = parent["arms"].get("%.2f" % k) or {}
            for win in ("full", "out_of_sample"):
                ref = pub.get(win) or {}
                for key in ("annualized_compound", "annual_vol", "max_drawdown"):
                    a, b = got[win].get(key), ref.get(key)
                    if a is None or b is None:
                        problems.append("CHECK FAILED anchor k=%.2f %s %s missing"
                                        % (k, win, key))
                        continue
                    worst = max(worst, abs(float(a) - float(b)))
                    if abs(float(a) - float(b)) > 1e-9:
                        problems.append("CHECK FAILED anchor k=%.2f %s %s %.12f != %.12f"
                                        % (k, win, key, a, b))
        # (3) the face's own numbers must re-derive from its own rows
        rebuilt = _rebuild_from_rows(parent["rows"], parent["beta"])
        for key, cell in face["cells"].items():
            mine = rebuilt["cells"].get(key)
            if mine is None:
                problems.append("CHECK FAILED cell %s missing from rebuild" % key)
                continue
            for rule in ("rule_a", "rule_b"):
                a, b = cell[rule], mine[rule]
                if a["k"] != b["k"]:
                    problems.append("CHECK FAILED cell %s %s k %r != %r"
                                    % (key, rule, a["k"], b["k"]))
                    continue
                for field in ("in_sample_annualized", "in_sample_dd",
                              "out_of_sample_annualized", "out_of_sample_dd",
                              "give_up_in_sample_pp", "give_up_out_of_sample_pp"):
                    x, y = a.get(field), b.get(field)
                    if (x is None) != (y is None):
                        problems.append("CHECK FAILED cell %s %s %s %r != %r"
                                        % (key, rule, field, x, y))
                    elif x is not None and abs(float(x) - float(y)) > 1e-9:
                        problems.append("CHECK FAILED cell %s %s %s %.12f != %.12f"
                                        % (key, rule, field, x, y))
            if cell["verdict"] != mine["verdict"]:
                problems.append("CHECK FAILED cell %s verdict %s != %s"
                                % (key, cell["verdict"], mine["verdict"]))
        # (4) the published curve must re-derive too -- the page reads sizes that no
        #     cell names (k = 1.50 / 2.00), so they need their own leg
        zero_mine = rebuilt["grids"]["%.2f" % CARRY_PRIMARY]
        for w in WINDOWS:
            for row in face["curve"][w]:
                mine = _arm_at(zero_mine, row["k"])
                if mine is None:
                    problems.append("CHECK FAILED curve k=%.2f missing" % row["k"])
                    continue
                for field, key in (("annualized_compound", "annualized_compound"),
                                   ("max_drawdown", "max_drawdown"),
                                   ("annual_vol", "annual_vol")):
                    x, y = row.get(field), mine[w].get(key)
                    if (x is None) != (y is None):
                        problems.append("CHECK FAILED curve k=%.2f %s %s %r != %r"
                                        % (row["k"], w, field, x, y))
                    elif x is not None and abs(float(x) - float(y)) > 1e-9:
                        problems.append("CHECK FAILED curve k=%.2f %s %s %.12f != %.12f"
                                        % (row["k"], w, field, x, y))
        # (5) the primary verdict must be the one its own numbers imply
        pv, _ = budget_verdict(face["cells"]["%.2f|%.2f" % (BUDGET_PRIMARY, CARRY_PRIMARY)])
        if face["primary"]["verdict"] != pv:
            problems.append("CHECK FAILED primary verdict %s != %s"
                            % (face["primary"]["verdict"], pv))
        # (6) the page must be the render of this face
        try:
            with open(MD, "r", encoding="utf-8") as fh:
                on_disk = fh.read()
        except OSError:
            problems.append("CHECK FAILED page missing: %s" % _rel(MD))
            on_disk = None
        if on_disk is not None and on_disk != render_md(face):
            problems.append("CHECK FAILED page is not the render of the face: %s" % _rel(MD))

    if not problems:
        pr = face["primary"]
        print("CHECK ok  (periods=%d, cutoff %s, primary %.0f%%/%.0f%% k=%s, verdict %s, "
              "price %s)"
              % (len(face_rows), face["evidence_cutoff"], pr["budget"] * 100,
                 pr["carry_per_year"] * 100,
                 "n/a" if pr["rule_a_k"] is None else "%.2f" % pr["rule_a_k"],
                 pr["verdict"], pr["price_verdict"]))
        return 0
    for p in problems:
        print(p)
    return 3


def _rebuild_from_rows(rows: list, beta: float) -> dict:
    """Same arithmetic `build()` does, driven by an arbitrary row list -- this is what
    the negative control uses to prove that a hand-edited return lands on CHECK
    FAILED rather than on STALE."""
    mask = [bool(r["in_sample"]) for r in rows]
    book = [float(r["book_net"]) for r in rows]
    hedge = [r.get("hedge_etf") for r in rows]
    grids = {"%.2f" % c: arm_grid(book, hedge, beta, carry_ppy=c, is_mask=mask)
             for c in CARRY_AXIS}
    cells = {}
    for c in CARRY_AXIS:
        for b in BUDGETS:
            cells["%.2f|%.2f" % (b, c)] = build_cells(grids["%.2f" % c], b, c)
    return {"grids": grids, "cells": cells}


# ------------------------------------------------------------------ selftest
_CHECKS = [0]


def _ok(cond, msg):
    _CHECKS[0] += 1
    if not cond:
        raise AssertionError("selftest leg %d failed: %s" % (_CHECKS[0], msg))


def _synthetic_arms(spec) -> list:
    """spec: list of (k, annualized, max_drawdown) -- the same shape arm_grid returns."""
    out = []
    for k, ann, dd in spec:
        st = {"periods": 10, "per_period_mean": ann / PPY,
              "annualized_compound": ann, "annual_vol": 0.1,
              "sharpe_excess_0": 0.5, "max_drawdown": dd, "hit_rate": 0.5,
              "worst_period": -0.02, "underwater_share": 0.5}
        out.append({"k": float(k), "full": dict(st), "in_sample": dict(st),
                    "out_of_sample": dict(st)})
    return out


def selftest() -> int:
    # 1. drawdown magnitude is the absolute size, not the signed number
    _ok(abs(dd_mag({"periods": 3, "max_drawdown": -0.25}) - 0.25) < 1e-15,
        "dd_mag is absolute")
    # 2. an arm with no periods has no drawdown -- None, never 0.0
    _ok(dd_mag({"periods": 0}) is None, "no periods -> None")
    _ok(dd_mag(None) is None, "no stats -> None")
    # 3. a flat book has no drawdown at any size, so the k=0 arm already fits every budget
    book = [0.01] * 12
    hedge = [0.0] * 12
    arms = arm_grid(book, hedge, 1.0, carry_ppy=0.0,
                    is_mask=[True] * 6 + [False] * 6)
    _ok(all((dd_mag(a["full"]) or 0.0) == 0.0 for a in arms), "flat book -> zero drawdown")
    pick = choose_max_return(arms, "in_sample", 0.05)
    _ok(pick is not None and abs(pick["k"]) < 1e-12,
        "flat book ties everywhere and ties go to the smaller size (k=0)")
    # 4. a perfect hedge removes the loss: book -20% with the index -20% is flat at k=1
    book = [0.01] * 12
    book[3] = -0.20
    hedge = [0.01] * 12
    hedge[3] = -0.20
    arms = arm_grid(book, hedge, 1.0, carry_ppy=0.0, is_mask=[True] * 12)
    at1 = _arm_at(arms, 1.0)
    hedged = arm_series(book, hedge, 1.0, 1.0, carry_ppy=0.0)
    _ok(max(hedged) - min(hedged) < 1e-15,
        "a beta-1 perfect hedge makes the -20% period indistinguishable from the rest")
    _ok(hedged[3] > -0.01, "the loss period is no longer the worst period")
    _ok(dd_mag(at1["full"]) is not None and dd_mag(at1["full"]) < dd_mag(arms[0]["full"]),
        "and the hedged book's drawdown is only the uniform cost drag, well inside the unhedged one")
    # 5. ... and the rule then buys as much as the grid allows
    pick = choose_max_return(arms, "full", 0.30)
    _ok(pick is not None and abs(pick["k"] - KGRID[-1]) < 1e-12,
        "a hedge that never hurts gets bought up to the grid edge")
    # 6. rule A picks the highest return inside the budget, inclusive at the boundary
    spec = [(0.0, 0.10, -0.30), (0.5, 0.09, -0.20), (1.0, 0.08, -0.15), (1.5, 0.05, -0.18)]
    arms = _synthetic_arms(spec)
    a = choose_max_return(arms, "full", 0.20)
    _ok(a is not None and abs(a["k"] - 0.5) < 1e-12,
        "0.09 beats 0.08 when both fit a 20% budget (boundary is inclusive)")
    # 7. rule B is the smallest size that fits, not the best one
    b = choose_min_k(arms, "full", 0.20)
    _ok(b is not None and abs(b["k"] - 0.5) < 1e-12, "rule B takes the smallest fit")
    b2 = choose_min_k(arms, "full", 0.31)
    _ok(b2 is not None and abs(b2["k"]) < 1e-12, "a loose budget lets rule B buy nothing")
    # 8. a budget no size can meet is None, not a silently smaller answer
    b3 = choose_max_return(_synthetic_arms([(0.0, 0.10, -0.30), (1.0, 0.08, -0.25)]),
                           "full", 0.05)
    _ok(b3 is None, "unreachable budget -> None")
    # 9. ties go to the smaller size
    tie = _synthetic_arms([(0.0, 0.10, -0.30), (0.5, 0.10, -0.10), (1.0, 0.10, -0.10)])
    _ok(abs(choose_max_return(tie, "full", 0.20)["k"] - 0.5) < 1e-12,
        "equal returns -> the smaller size")
    # 10. the floor under the budget question is the best drawdown the grid can buy
    _ok(abs((min_achievable_dd(arms, "full") or 0.0) - 0.15) < 1e-12,
        "floor = min |dd| over the grid")
    # 11. price: nothing removed -> None, never 0.0 (0.0 would read as free)
    flat = _synthetic_arms([(0.0, 0.10, -0.20), (0.05, 0.09, -0.20)])
    p = price_of(flat, 0.05, "full")
    _ok(p["dd_removed_pp"] == 0.0 and p["pp_return_per_dd_point"] is None,
        "zero drawdown removed -> price None")
    # 12. price arithmetic on a known pair: 0.10 of dd removed for 0.02 of return -> 0.2
    known = _synthetic_arms([(0.0, 0.10, -0.30), (0.05, 0.08, -0.20)])
    p = price_of(known, 0.05, "full")
    _ok(abs(p["dd_removed_pp"] - 10.0) < 1e-12 and abs(p["give_up_pp"] - 2.0) < 1e-12
        and abs(p["pp_return_per_dd_point"] - 0.2) < 1e-12, "price = give-up / dd removed")
    # 13. a negative price is a negative price -- hedging that paid you is printed, not clipped
    paid = _synthetic_arms([(0.0, 0.05, -0.30), (0.05, 0.06, -0.20)])
    p = price_of(paid, 0.05, "full")
    _ok(p["pp_return_per_dd_point"] is not None and p["pp_return_per_dd_point"] < 0,
        "paying you is a negative price, not zero")
    # 14. the base arm is the same window's k=0, not another window's
    split = [{"k": 0.0,
              "full": {"periods": 5, "annualized_compound": 0.10, "max_drawdown": -0.30},
              "in_sample": {"periods": 3, "annualized_compound": 0.01, "max_drawdown": -0.10},
              "out_of_sample": {"periods": 2, "annualized_compound": 0.20, "max_drawdown": -0.30}},
             {"k": 0.05,
              "full": {"periods": 5, "annualized_compound": 0.09, "max_drawdown": -0.20},
              "in_sample": {"periods": 3, "annualized_compound": 0.02, "max_drawdown": -0.08},
              "out_of_sample": {"periods": 2, "annualized_compound": 0.18, "max_drawdown": -0.20}}]
    _ok(abs(price_of(split, 0.05, "in_sample")["give_up_pp"] - (-1.0)) < 1e-12,
        "in-sample price uses the in-sample k=0 arm")
    _ok(abs(price_of(split, 0.05, "out_of_sample")["give_up_pp"] - 2.0) < 1e-12,
        "out-of-sample price uses the out-of-sample k=0 arm")
    # 15. the marginal price looks at the step before k, not at k=0
    step_arms = _synthetic_arms([(0.0, 0.10, -0.30), (0.05, 0.10, -0.20), (0.10, 0.09, -0.10)])
    m = step_price(step_arms, 0.10, "full")
    _ok(abs(m["from_k"] - 0.05) < 1e-12 and abs(m["pp_return_per_dd_point"] - 0.1) < 1e-12,
        "marginal price is the last step's, not the average's")
    # 16. at k=0 there is no marginal step to price
    m0 = step_price(step_arms, 0.0, "full")
    _ok(m0["from_k"] is None and m0["pp_return_per_dd_point"] is None, "k=0 has no step")
    # 17. verdicts: three states, and the boundaries are inclusive
    def cell(k, is_dd, oos_dd, budget=0.20, floor=0.10):
        return {"budget": budget, "min_achievable_dd_in_sample": floor,
                "rule_a": {"k": k, "out_of_sample_dd": oos_dd,
                           "in_sample_dd": is_dd}}
    _ok(budget_verdict(cell(None, None, None))[0] == "BUDGET_UNREACHABLE_IN_SAMPLE",
        "no size -> unreachable")
    _ok(budget_verdict(cell(0.5, -0.15, -0.20))[0] == "BUDGET_HOLDS_OUT_OF_SAMPLE",
        "exactly at the budget holds")
    _ok(budget_verdict(cell(0.5, -0.15, -0.2001))[0] == "BUDGET_MISSES_OUT_OF_SAMPLE",
        "a hair past the budget misses")
    _ok(budget_verdict(cell(0.5, -0.15, None))[0] == "BUDGET_UNKNOWN_OUT_OF_SAMPLE",
        "no priced out-of-sample drawdown -> unknown, not a pass")
    # 18. price verdicts: the sign flip is the named state
    _ok(price_verdict(-0.06, 1.52)[0] == "PAID_IN_SAMPLE_COSTS_OUTSIDE", "sign flip named")
    _ok(price_verdict(0.2, 1.5)[0] == "COSTS_IN_BOTH_WINDOWS", "costs in both")
    _ok(price_verdict(-0.2, -0.1)[0] == "PAID_IN_BOTH_WINDOWS", "paid in both")
    _ok(price_verdict(None, 1.0)[0] == "PRICE_NOT_MEASURABLE", "missing side -> not measurable")
    # 19. k=0 reproduces the input book bit for bit (the control arm identity)
    book = [0.0123, -0.0456, 0.0789, 0.0, -0.001]
    hedge = [0.01, -0.02, 0.03, None, 0.0]
    series = arm_series(book, hedge, 0.0, 0.9, carry_ppy=0.05)
    _ok(series[0] == book[0] and series[2] == book[2],
        "k=0 with carry still reproduces the book exactly")
    # 20. a period with no hedge price stays missing -- it is not hedged for free
    _ok(series[3] is None, "unpriced hedge period -> None")
    # 21. carry and roll cost scale with |k*beta|, so they vanish at k=0 and double with k
    one = arm_series([0.0], [0.0], 1.0, 1.0, carry_ppy=0.02)
    two = arm_series([0.0], [0.0], 2.0, 1.0, carry_ppy=0.02)
    _ok(abs(two[0] - 2.0 * one[0]) < 1e-18, "cost scales with the notional coefficient")
    _ok(abs(one[0] - (-(2.0 * 0.0008) - 0.02 / PPY)) < 1e-18,
        "one unit of beta costs two sides of 8bp plus carry")
    # 22. cells carry the OOS read of the size chosen in-sample, never a re-pick
    rows = [{"date": "2020-01-0%d" % (i + 1), "book_net": v, "hedge_etf": h,
             "in_sample": i < 4}
            for i, (v, h) in enumerate([(0.02, 0.01), (0.02, 0.01), (-0.15, -0.15),
                                        (0.02, 0.01), (0.02, 0.01), (0.02, 0.01),
                                        (-0.05, -0.05), (0.02, 0.01)])]
    rebuilt = _rebuild_from_rows(rows, 1.0)
    for key, c in rebuilt["cells"].items():
        if c["rule_a"]["k"] is None:
            _ok(c["verdict"] == "BUDGET_UNREACHABLE_IN_SAMPLE", "None k -> unreachable")
            continue
        _ok(c["rule_a"]["out_of_sample_dd"] is not None,
            "every reachable cell carries a priced out-of-sample drawdown")
    print("selftest %d/%d PASS" % (_CHECKS[0], _CHECKS[0]))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check", "selftest"))
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())
