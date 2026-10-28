"""Futures-overlay flip-rate arms: does cutting SIGN FLIPS pay for itself?

Why this exists
---------------
`futures_overlay_sweep.py` closed two axes and both came back negative:

  * weight axis  -- the overlay's best weight is in-sample, and it only clears at 1-3bp/side;
  * band axis    -- a no-trade band is a two-sided loss, because 86-92% of the sleeve's
                    turnover is STRUCTURAL (entries, exits, sign flips), not re-sizing.

So the frequency question has to be answered where the turnover actually lives: the sign
flip. This face re-prices the same sleeve with three flip-damping mechanisms and reports
BOTH sides of the trade (flips removed vs gross given up), at the full cost ladder, on the
same panels, the same execution lag and the same risk anchor as the sweep.

Mechanisms (all causal, all read data <= t)
-------------------------------------------
  base          sign(momentum) -- the shipped sleeve, unchanged.
  strength_hold keep the prior sign while |momentum| < theta; a flip needs a momentum
                reading of at least theta in the new direction. Participation is preserved
                by seeding each instrument at its first valid momentum sign (this is a flip
                filter, not an exposure cut -- the mean |weight| it changes is published).
  confirm_kd    keep the prior sign until the opposite sign has held for k consecutive
                days. Same seeding.

Honest scope: this selects nothing and changes no book. The flips are counted on the
signal face, the sleeve is charged 1bp in the sweep and the whole ladder here, and roll
cost / margin / carry still are not modelled (main-continuous splice hides them).
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import futures_tsmom_probe as P                      # noqa: E402
import futures_overlay_sweep as S                    # noqa: E402
from config import PATHS                             # noqa: E402

LOOKBACKS = {"tsmom60": 60, "tsmom120": 120}
THETA_GRID = [0.02, 0.04]
CONFIRM_GRID = [3, 5]
F = S.BREAKEVEN_WEIGHT          # the weight the shipped card publishes (1/3)
COSTS = S.COST_GRID_BP          # 1 / 3 / 5 / 10 bp per side


# ---------------------------------------------------------------- mechanisms
def base_signs(mom):
    return np.sign(mom)


def strength_hold(mom, theta):
    """Hold the prior sign while |mom| < theta; seed at the first valid sign.

    A flip (not a resize) rule: once a sign exists it survives weak readings, and it only
    turns when the momentum itself is at least theta in the other direction.
    """
    arr = np.asarray(mom.to_numpy(), dtype=float)
    out = np.zeros_like(arr)
    prev = np.zeros(arr.shape[1])
    seen = np.zeros(arr.shape[1], dtype=bool)
    for i in range(arr.shape[0]):
        m = arr[i]
        live = np.isfinite(m)
        seed = live & ~seen
        prev = np.where(seed, np.sign(m), prev)
        seen = seen | seed
        strong = live & (np.abs(np.nan_to_num(m)) >= theta)
        new = np.where(strong, np.sign(m), 0.0)
        prev = np.where(new != 0.0, new, prev)
        out[i] = np.where(live, prev, np.nan)
    return pd.DataFrame(out, index=mom.index, columns=mom.columns)


def confirm_kd(mom, k):
    """Hold the prior sign until the opposite sign has held for k consecutive days."""
    arr = np.asarray(mom.to_numpy(), dtype=float)
    sg = np.sign(arr)
    out = np.zeros_like(arr)
    prev = np.zeros(arr.shape[1])
    seen = np.zeros(arr.shape[1], dtype=bool)
    k = max(1, int(k))
    for i in range(arr.shape[0]):
        live = np.isfinite(arr[i])
        seed = live & ~seen
        prev = np.where(seed, sg[i], prev)
        seen = seen | seed
        new = np.where(live, sg[i], 0.0)
        if k == 1:
            prev = np.where(new != 0.0, new, prev)
        else:
            agree = new != 0.0
            for j in range(k):
                back = i - j
                if back < 0:
                    agree = np.zeros(arr.shape[1], dtype=bool)
                    break
                agree &= np.isfinite(arr[back]) & (sg[back] == new) & (new != 0.0)
            prev = np.where(agree, new, prev)
        out[i] = np.where(live, prev, np.nan)
    return pd.DataFrame(out, index=mom.index, columns=mom.columns)


# ---------------------------------------------------------------- counting
def flip_counts(signs):
    """Sign changes, entries (0 -> +/-1) and exits (+/-1 -> 0) on the signal face."""
    s = np.asarray(signs.to_numpy(), dtype=float)
    s = np.where(np.isfinite(s), s, 0.0)
    if s.shape[0] < 2:
        return {"flips": 0, "entries": 0, "exits": 0, "days": int(s.shape[0])}
    prev, cur = s[:-1], s[1:]
    flips = int(((prev != cur) & (prev != 0.0) & (cur != 0.0)).sum())
    entries = int(((prev == 0.0) & (cur != 0.0)).sum())
    exits = int(((prev != 0.0) & (cur == 0.0)).sum())
    return {"flips": flips, "entries": entries, "exits": exits, "days": int(s.shape[0])}


def _pct_cut(new, base):
    if not base:
        return None
    return round((1.0 - float(new) / float(base)) * 100.0, 1)


# ---------------------------------------------------------------- arms
def arms_for(lookback):
    yield ("base", {"mechanism": "base", "lookback": lookback, "theta": None, "k": None},
           lambda mom: base_signs(mom))
    for th in THETA_GRID:
        yield ("strength_hold_%g" % th,
               {"mechanism": "strength_hold", "lookback": lookback, "theta": th, "k": None},
               (lambda th_: lambda mom: strength_hold(mom, th_))(th))
    for k in CONFIRM_GRID:
        yield ("confirm_%dd" % k,
               {"mechanism": "confirm_kd", "lookback": lookback, "theta": None, "k": k},
               (lambda k_: lambda mom: confirm_kd(mom, k_))(k))


def arm_face(close, book_r, book_vol, book_anchor, tag, lookback, spec, sign_fn):
    mom = close.pct_change(lookback)
    signs = sign_fn(mom)
    w = P.tsmom_weights(close, lookback=lookback, signs=signs)
    cnt = flip_counts(signs)

    eq0, turn0, _ = P.run_weights(close, w, cost=0.0)
    gross_cagr = P.stats(eq0, tag + "_gross").get("cagr")

    cost_rows = []
    for bp in COSTS:
        eq, turn, _ = P.run_weights(close, w, cost=bp / 10000.0)
        sleeve_r = P.daily_returns(eq)
        idx = book_r.index.intersection(sleeve_r.index)
        e = book_r.reindex(idx).fillna(0.0)
        s = sleeve_r.reindex(idx).fillna(0.0)
        eq_b = S.eq_from_returns(S.blend_returns(e, s, F))
        at = P.stats(P.vol_normalize(eq_b, book_vol), "%s_c%gbp_scaled" % (tag, bp))
        blend = S.stats_for(e, s, F, "%s_c%gbp" % (tag, bp))
        cost_rows.append({
            "cost_per_side_bp": bp,
            "turnover_total": round(turn, 1),
            "blend_cagr": blend.get("cagr"),
            "blend_sharpe": blend.get("sharpe"),
            "equal_risk_cagr": at.get("cagr"),
            "equal_risk_delta_cagr_pp": round(
                (at.get("cagr", 0.0) - book_anchor.get("cagr", 0.0)) * 100, 2),
            "equal_risk_delta_maxdd_pp": round(
                (at.get("maxdd", 0.0) - book_anchor.get("maxdd", 0.0)) * 100, 2),
        })

    be = S.breakeven_cost([{"cost_per_side_bp": r["cost_per_side_bp"],
                            "rows": [{"weight_in_sleeve": round(F, 4),
                                      "at_equal_vol_delta_cagr_pp": r["equal_risk_delta_cagr_pp"]}]}
                           for r in cost_rows], F)

    arr = np.abs(w.to_numpy(dtype=float))
    mean_abs_w = float(np.nanmean(arr)) if np.isfinite(arr).any() else 0.0
    sleeve_1bp = next((r for r in cost_rows if r["cost_per_side_bp"] == 1.0), {})

    return {
        "label": tag,
        "spec": spec,
        "flips_total": cnt["flips"],
        "flips_per_year": round(cnt["flips"] / (cnt["days"] / 252.0), 1) if cnt["days"] else None,
        "entries_total": cnt["entries"],
        "exits_total": cnt["exits"],
        "mean_abs_weight": round(mean_abs_w, 4),
        "sleeve_turnover_total": round(turn0, 1),
        "sleeve_gross_cagr": gross_cagr,
        "sleeve_cagr_1bp": sleeve_1bp.get("blend_cagr"),
        "sleeve_sharpe_1bp": sleeve_1bp.get("blend_sharpe"),
        "cost_rows": cost_rows,
        "breakeven_bp": be,
    }


def robustness(arms):
    """Is the win a plateau or a single grid point? Measured, not asserted.

    A threshold axis that helps at one theta and collapses at the next one up is a
    hypothesis, not a rule. `clears_both_theta_levels` reads the measured rows.
    """
    holds = [a for a in arms if a["spec"]["mechanism"] == "strength_hold"]
    clears = [a for a in holds if a.get("beats_base_at_3bp_or_worse")]
    expo = [a["mean_abs_weight"] for a in arms if a["mean_abs_weight"]]
    return {
        "theta_levels_tested": [a["spec"]["theta"] for a in holds],
        "theta_levels_that_clear_the_base": [a["spec"]["theta"] for a in clears],
        "clears_both_theta_levels": bool(len(holds) > 1 and len(clears) == len(holds)),
        "exposure_spread_pct": (round((max(expo) - min(expo)) / min(expo) * 100, 2)
                                if expo and min(expo) > 0 else None),
        "note": ("a win at LOW theta next to a collapse at HIGH theta is a single grid "
                 "point; it needs a neighbourhood sweep before it can be called a rule"),
    }


def attach_cuts(rows):
    """Every cut is measured against the base arm of the SAME lookback (its own control)."""
    for lb, arms in rows.items():
        base = arms[0]
        for a in arms:
            a["flip_cut_pct"] = _pct_cut(a["flips_total"], base["flips_total"])
            a["turnover_cut_pct"] = _pct_cut(a["sleeve_turnover_total"],
                                             base["sleeve_turnover_total"])
            a["gross_give_up_pp"] = (None if a["sleeve_gross_cagr"] is None
                                     or base["sleeve_gross_cagr"] is None
                                     else round((a["sleeve_gross_cagr"]
                                                 - base["sleeve_gross_cagr"]) * 100, 2))
            b1 = next((r for r in base["cost_rows"] if r["cost_per_side_bp"] == 1.0), {})
            a1 = next((r for r in a["cost_rows"] if r["cost_per_side_bp"] == 1.0), {})
            if a1.get("blend_sharpe") is not None and b1.get("blend_sharpe") is not None:
                a["sharpe_delta_vs_base_1bp"] = round(
                    a1["blend_sharpe"] - b1["blend_sharpe"], 3)
            else:
                a["sharpe_delta_vs_base_1bp"] = None
            # the honest headline: a flip filter is only useful if it wins at a cost
            # level the sleeve cannot clear today (3bp+) -- winning at 1bp is the status quo
            a["beats_base_at_3bp_or_worse"] = bool(
                a["spec"]["mechanism"] != "base" and all(
                    (next((r for r in a["cost_rows"] if r["cost_per_side_bp"] == bp), {})
                     .get("equal_risk_delta_cagr_pp") or 0.0)
                    > (next((r for r in base["cost_rows"] if r["cost_per_side_bp"] == bp), {})
                       .get("equal_risk_delta_cagr_pp") or 0.0)
                    for bp in [3.0, 5.0, 10.0])
            )


def verdict_for(arms):
    """One sentence per lookback, derived from the measured rows (never hand-written)."""
    base = arms[0]
    cands = [a for a in arms[1:] if a.get("beats_base_at_3bp_or_worse")]
    if not cands:
        best = max(arms[1:], key=lambda a: (a.get("flip_cut_pct") or 0.0))
        return ("no arm beats the shipped sleeve at 3bp/side or worse; the biggest flip cut "
                "(%s: %s%% fewer flips) buys that by giving up %s pp of gross"
                % (best["label"], best.get("flip_cut_pct"),
                   best.get("gross_give_up_pp")))
    cands.sort(key=lambda a: a["cost_rows"][-1].get("equal_risk_delta_cagr_pp") or -9)
    b = cands[-1]
    be = b.get("breakeven_bp")
    at_be = next((r.get("equal_risk_delta_cagr_pp") for r in b["cost_rows"]
                  if be is not None and r["cost_per_side_bp"] == be), None)
    return ("%s clears the base at 3/5/10bp: %s%% fewer flips, turnover cut %s%%, gross %s pp; "
            "breakeven moves to %s (%+.2f pp at that cost, %+.2f pp at 10bp)"
            % (b["label"], b.get("flip_cut_pct"), b.get("turnover_cut_pct"),
               b.get("gross_give_up_pp"),
               ("%gbp" % be) if be else "none of the levels tested", at_be or 0.0,
               b["cost_rows"][-1].get("equal_risk_delta_cagr_pp") or 0.0))


# ---------------------------------------------------------------- render
def render_md(out):
    L = ["# Futures overlay: flip-rate arms", "",
         "Generated by `scripts/futures_overlay_fliprate.py` from the same panels as "
         "`results/futures_overlay_sweep.json`. Measurement face -- selects nothing, "
         "changes no book, places no order.", "",
         "evidence_cutoff: %s" % out["evidence_cutoff"], ""]
    for lb, blk in out["lookbacks"].items():
        L += ["## %s (lookback %d)" % (lb, blk["lookback"]), "",
              "flips on the signal face, sleeve charged the full cost ladder, blend at "
              "f=%.2f, equal risk against the book." % F, "",
              "| arm | flips | flip cut | turnover | turnover cut | gross CAGR | give-up pp | "
              "sharpe d (1bp) | delta CAGR pp @1bp | @3bp | @5bp | @10bp | breakeven |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for a in blk["arms"]:
            by = {r["cost_per_side_bp"]: r.get("equal_risk_delta_cagr_pp")
                  for r in a["cost_rows"]}
            L.append("| %s | %d | %s%% | %.1f | %s%% | %s%% | %s | %s | %s | %s | %s | %s | %s |"
                     % (a["label"], a["flips_total"],
                        "—" if a.get("flip_cut_pct") is None else a["flip_cut_pct"],
                        a["sleeve_turnover_total"],
                        "—" if a.get("turnover_cut_pct") is None else a["turnover_cut_pct"],
                        "—" if a["sleeve_gross_cagr"] is None else round(a["sleeve_gross_cagr"] * 100, 2),
                        "—" if a.get("gross_give_up_pp") is None else a["gross_give_up_pp"],
                        "—" if a.get("sharpe_delta_vs_base_1bp") is None else a["sharpe_delta_vs_base_1bp"],
                        by.get(1.0), by.get(3.0), by.get(5.0), by.get(10.0),
                        ("%gbp" % a["breakeven_bp"]) if a.get("breakeven_bp") else "none"))
        L += ["", "**%s**" % blk["verdict"], ""]
        rb = blk.get("robustness") or {}
        L += ["robustness: %s of the tested theta levels clear the base (%s); exposure spread "
              "across all arms %s%% -- so this is a flip filter, not a deleveraging"
              % (len(rb.get("theta_levels_that_clear_the_base") or []),
                 rb.get("theta_levels_tested"), rb.get("exposure_spread_pct")), ""]
        if not rb.get("clears_both_theta_levels"):
            L += ["> **Fragile:** the win lives at one theta. " + (rb.get("note") or ""), ""]
    L += ["## Not modelled", "", out["not_modelled"], ""]
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- run
def run():
    close = P.load_panel()
    book, book_meta = P.etf_book_series()
    book_r = P.daily_returns(book)
    book_vol = float(book_r.std() * np.sqrt(252))
    book_anchor = P.stats(P.vol_normalize(book, book_vol), "book_anchor")

    out = {
        "evidence_cutoff": str(close.index[-1].date()),
        "face": ("descriptive flip-rate sweep; selects no arm, changes no book, "
                 "places no order"),
        "anchor": {"book_vol": round(book_vol, 4),
                   "book_cagr": book_anchor.get("cagr"),
                   "book_sharpe": book_anchor.get("sharpe"),
                   "book_maxdd": book_anchor.get("maxdd"),
                   "blend_weight": round(F, 4)},
        "legs": {"etf_book": book_meta,
                 "futures_sleeve": {"source": "data/futures_daily main-continuous",
                                    "bars": int(close.shape[0]),
                                    "varieties": int(close.shape[1])}},
        "grid": {"theta": THETA_GRID, "confirm_days": CONFIRM_GRID,
                 "costs_bp": COSTS, "weight": round(F, 4)},
        "not_modelled": ("roll cost, margin, financing/carry, contract multipliers; the ETF "
                         "leg's universe is survivors; the arm grid is small on purpose and "
                         "is not tuned on the result"),
    }

    rows = {}
    for tag, lb in LOOKBACKS.items():
        arms = []
        for label, spec, fn in arms_for(lb):
            arms.append(arm_face(close, book_r, book_vol, book_anchor,
                                 "%s_%s" % (tag, label), lb, spec, fn))
        rows[tag] = arms
    attach_cuts(rows)

    out["lookbacks"] = {}
    for tag, lb in LOOKBACKS.items():
        arms = rows[tag]
        out["lookbacks"][tag] = {
            "lookback": lb,
            "control_arm": arms[0]["label"],
            "verdict": verdict_for(arms),
            "robustness": robustness(arms),
            "arms": arms,
        }

    p = os.path.join(PATHS.results_dir, "futures_overlay_fliprate.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    md_path = os.path.join(os.path.dirname(PATHS.results_dir),
                           "research", "ETF_BOOK_FUTURES_FLIPRATE.md")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(render_md(out))

    for tag, blk in out["lookbacks"].items():
        print("\n%s lookback=%d" % (tag, blk["lookback"]), flush=True)
        print("  arm                        flips  cut     turn    cut     gross    give-up  "
              "dSR1bp  dCAGR@1  @3   @5   @10  be", flush=True)
        for a in blk["arms"]:
            by = {r["cost_per_side_bp"]: r.get("equal_risk_delta_cagr_pp")
                  for r in a["cost_rows"]}
            print("  %-24s %6d %6s %8.1f %6s %7s %8s %7s %8s %5s %5s %5s %5s"
                  % (a["spec"]["mechanism"] + ("" if a["spec"].get("theta") is None
                                               and a["spec"].get("k") is None
                                               else "_%s" % (a["spec"].get("theta")
                                                             or a["spec"].get("k"))),
                     a["flips_total"],
                     "—" if a.get("flip_cut_pct") is None else a["flip_cut_pct"],
                     a["sleeve_turnover_total"],
                     "—" if a.get("turnover_cut_pct") is None else a["turnover_cut_pct"],
                     "—" if a["sleeve_gross_cagr"] is None else "%.2f%%" % (a["sleeve_gross_cagr"] * 100),
                     "—" if a.get("gross_give_up_pp") is None else a["gross_give_up_pp"],
                     "—" if a.get("sharpe_delta_vs_base_1bp") is None else a["sharpe_delta_vs_base_1bp"],
                     by.get(1.0), by.get(3.0), by.get(5.0), by.get(10.0),
                     ("%gbp" % a["breakeven_bp"]) if a.get("breakeven_bp") else "none"),
                  flush=True)
        print("  verdict: %s" % blk["verdict"], flush=True)
    print("\nsaved %s\nsaved %s" % (p, md_path), flush=True)
    return 0


# ---------------------------------------------------------------- selftest
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

    idx = pd.date_range("2020-01-01", periods=12, freq="B")
    mom = pd.DataFrame({"a": [0.05, 0.06, -0.01, -0.08, 0.02, 0.09, -0.03, -0.10, 0.01,
                              0.07, 0.02, -0.05]}, index=idx)

    # 1 identity: theta=0 is the shipped sleeve (a filter with no threshold filters nothing)
    chk("L1 strength_hold(theta=0) reproduces the base signs",
        np.array_equal(np.nan_to_num(strength_hold(mom, 0.0).to_numpy()),
                       np.nan_to_num(base_signs(mom).to_numpy())))

    # 2 liveness + full damping: an impossible threshold never flips, and the base DOES
    held = np.nan_to_num(strength_hold(mom, 10.0).to_numpy())[:, 0]
    base = np.nan_to_num(base_signs(mom).to_numpy())[:, 0]
    chk("L2 an unreachable threshold never flips (and the base does)",
        flip_counts(strength_hold(mom, 10.0))["flips"] == 0 and
        flip_counts(base_signs(mom))["flips"] >= 2 and len(set(held)) == 1,
        "base flips=%d held unique=%s" % (flip_counts(base_signs(mom))["flips"],
                                          sorted(set(held))))

    # 3 identity: k=1 confirms instantly
    chk("L3 confirm_kd(k=1) reproduces the base signs",
        np.array_equal(np.nan_to_num(confirm_kd(mom, 1).to_numpy()),
                       np.nan_to_num(base_signs(mom).to_numpy())))

    # 4 the confirmation window is really k days: with k=3 a one-day poking sign is ignored
    poke = pd.DataFrame({"a": [0.05, 0.05, -0.06, 0.05, 0.05]}, index=idx[:5])
    got = np.nan_to_num(confirm_kd(poke, 3).to_numpy())[:, 0]
    chk("L4 a one-day opposite sign does not flip a 3d-confirmed arm",
        list(got) == [1.0, 1.0, 1.0, 1.0, 1.0] and
        flip_counts(base_signs(poke))["flips"] == 2,
        "got=%s base_flips=%d" % (list(got), flip_counts(base_signs(poke))["flips"]))

    # 5 causality: truncating the future cannot change a past sign
    full = np.nan_to_num(strength_hold(mom, 0.02).to_numpy())[:, 0]
    part = np.nan_to_num(strength_hold(mom.iloc[:7], 0.02).to_numpy())[:, 0]
    chk("L5 both mechanisms are causal (prefix of the full run == the truncated run)",
        np.array_equal(full[:7], part) and
        np.array_equal(np.nan_to_num(confirm_kd(mom, 3).to_numpy())[:7, 0],
                       np.nan_to_num(confirm_kd(mom.iloc[:7], 3).to_numpy())[:, 0]))

    # 6 flips are actually cut on a chattering series, and a genuine strong crossing still
    #   flips (a filter that zeroes the mechanism has cut participation, not noise)
    chat_idx = pd.date_range("2020-01-01", periods=16, freq="B")
    chat = pd.DataFrame({"a": [0.05, 0.005, -0.005, 0.005, -0.005, -0.05, -0.005, 0.005,
                               -0.005, 0.005, 0.05, 0.005, -0.005, 0.005, -0.005, -0.05]},
                        index=chat_idx)
    f_base = flip_counts(base_signs(chat))["flips"]
    f_hold = flip_counts(strength_hold(chat, 0.02))["flips"]
    f_conf = flip_counts(confirm_kd(chat, 3))["flips"]
    chk("L6 damping cuts flips on a chattering series without zeroing them out",
        f_base >= 8 and 0 < f_hold < f_base and 0 < f_conf < f_base,
        "base=%d hold=%d confirm=%d" % (f_base, f_hold, f_conf))

    # 7 counts are not self-referential: entries/exits are 0<->sign, not counted as flips
    step = pd.DataFrame({"a": [np.nan, 0.01, 0.01, -0.01, np.nan]}, index=idx[:5])
    c = flip_counts(base_signs(step))
    chk("L7 a NaN gap counts as an exit, not as a sign flip",
        c["flips"] == 1 and c["entries"] == 1 and c["exits"] == 1, str(c))

    # 8 one decision sequence: turnover must not move across cost levels (on a panel long
    #   enough for the 60d vol window -- a shorter fixture has no weights at all and would
    #   make this leg pass without anything happening, the r1261 trap)
    rng = np.random.RandomState(7)
    n = 90
    close = pd.DataFrame({
        "a": 100.0 * np.exp(np.cumsum(rng.normal(0.0, 0.010, n))),
        "b": 50.0 * np.exp(np.cumsum(rng.normal(0.0, 0.014, n))),
    }, index=pd.date_range("2020-01-01", periods=n, freq="B"))
    signs = base_signs(close.pct_change(2))
    w = P.tsmom_weights(close, lookback=2, signs=signs)
    turns = {round(P.run_weights(close, w, cost=bp / 10000.0)[1], 9) for bp in COSTS}
    chk("L8 the cost ladder re-prices ONE decision sequence (turnover invariant)",
        len(turns) == 1 and min(turns) > 0, str(turns))

    # 9 the published give-up is the measured difference of the two gross CAGRs
    m = {"mechanism": "strength_hold", "lookback": 2, "theta": 0.02, "k": None}
    flat = pd.Series(1.0, index=close.index)
    flat_r = flat.pct_change().dropna() + 1e-12
    face = arm_face(close, flat_r, float(flat_r.std() * np.sqrt(252)),
                    {"cagr": 0.0, "maxdd": 0.0}, "t_hold", 2, m,
                    lambda mm: strength_hold(mm, 0.02))
    face_base = arm_face(close, flat_r, float(flat_r.std() * np.sqrt(252)),
                         {"cagr": 0.0, "maxdd": 0.0}, "t_base", 2,
                         {"mechanism": "base", "lookback": 2, "theta": None, "k": None},
                         base_signs)
    rows = {"t": [face_base, face]}
    attach_cuts(rows)
    expect = round((face["sleeve_gross_cagr"] - face_base["sleeve_gross_cagr"]) * 100, 2)
    chk("L9 the give-up column is the measured gross difference",
        rows["t"][1]["gross_give_up_pp"] == expect and
        rows["t"][1]["flip_cut_pct"] is not None,
        "give_up=%s expect=%s flips %d->%d" % (rows["t"][1]["gross_give_up_pp"], expect,
                                               face_base["flips_total"], face["flips_total"]))

    # 10 the arm grid is whole, unique, and every mechanism is represented
    labels = ["%s_%s" % (tag, lab) for tag, lb in LOOKBACKS.items()
              for lab, _s, _f in arms_for(lb)]
    mechs = {spec["mechanism"] for lb in LOOKBACKS.values() for _l, spec, _f in arms_for(lb)}
    chk("L10 the arm grid is complete and unique",
        len(labels) == len(set(labels)) == len(LOOKBACKS) * (1 + len(THETA_GRID) + len(CONFIRM_GRID))
        and mechs == {"base", "strength_hold", "confirm_kd"},
        "arms=%d mechs=%s" % (len(labels), sorted(mechs)))

    # 11 f=0 is the book: the blend must not invent a return stream
    e = pd.Series([0.01, -0.02, 0.03], index=idx[:3])
    s = pd.Series([0.05, 0.05, 0.05], index=idx[:3])
    chk("L11 f=0 blend is the book itself",
        np.allclose(S.blend_returns(e, s, 0.0).to_numpy(), e.to_numpy()))

    print("selftest %d/%d PASS" % (ok, total))
    return 0 if ok == total else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    sys.exit(run())