"""Config-driven bench cell: one rule, many products, frozen criteria, MDE printed.

Why a generic runner
--------------------
Hand-writing a script per question is why the queue went empty: every cell cost
an hour of authoring, so the machine idled between sessions. Here a cell is a
JSON config (products, rule, parameters, cost, thresholds); the runner is the
same for all of them and always produces the same three things -- a result face,
a readable page, and a minimum detectable edge (MDE) so a negative cannot be
sold as knowledge it is not.

Cell types
----------
  single   one rule on one or more pooled products (long-only or long-short)
  pair     cross-sectional: long the top-k names, short the bottom-k (60d rank)
  robust   the same rule re-run with different parameters, to test whether the
           SIGN survives -- a validity check, not a parameter search

Config keys (all required unless noted):
  id, question, type, rule, products[], params{}, cost_bp_side, split,
  crit{H1_full_pct, H2_oos_pct, H2_oos_sharpe, H4_drop_best_pct, H5_p},
  target_edge_pp, long_only (single only), k (pair only), variants (robust only)

Nothing here reads the network. Universe files are the ones the data lanes keep.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402

RESULTS = bc.RESULTS
RESEARCH = bc.RESEARCH

# --- size normalisation -----------------------------------------------------
# H1 asks "is the annualised net return >= 4%?" -- but that number is printed on
# whatever volatility the arm happened to realise. r2152 measured the gap: arm
# vol runs 4.45%..14.68% against one declared target, so the same 4% line means
# different things on different books ("H1_IS_PARTLY_A_LEVERAGE_TEST"). The
# re-pricing below answers the same question on the face's own declared size.
# It is arithmetic on published numbers: no panel is reloaded, and the frozen
# verdict is NOT changed -- `H1_normalized_ge` is reported beside `H1_full_ge`
# so a reader can see both rulers at once (scripts/bench_size_normalized_h1.py).
H1_NORM_PCT = 4.0
# |realised / declared| beyond this counts as "this book is not the size the
# face claims"; same constant as scripts/bench_size_normalized_h1.py:OFF_TARGET
SIZE_OFF_TARGET = 0.10


def rescale_ann(ann_pct, vol_pct, k):
    """Annualised net return after putting a book on k x its own size.

    Exact under continuous rebalancing (no financing modelled): geometric ann g
    and vol s give arithmetic mu = g + s^2/2, and leverage k gives
    g(k) = k*mu - (k*s)^2/2. Both terms matter -- dropping the vol-drag term is
    how a levelled-up book looks better than it is.
    """
    if ann_pct is None or not vol_pct or not k:
        return None
    g = ann_pct / 100.0
    s = vol_pct / 100.0
    mu = g + 0.5 * s * s
    s2 = s * k
    return round((mu * k - 0.5 * s2 * s2) * 100.0, 4)


def normalize_to_target(ann_pct, vol_pct, declared_pct):
    """Re-price to the face's declared target and say how far off it was."""
    if ann_pct is None or not vol_pct or not declared_pct:
        return {"k": None, "ann_at_target_pct": None,
                "realized_vol_pct": vol_pct, "declared_vol_pct": declared_pct,
                "off_target": None}
    k = round(declared_pct / vol_pct, 6)
    off = abs(vol_pct / declared_pct - 1.0)
    return {"k": k,
            "ann_at_target_pct": rescale_ann(ann_pct, vol_pct, k),
            "realized_vol_pct": round(vol_pct, 4),
            "declared_vol_pct": declared_pct,
            "off_target": bool(off > SIZE_OFF_TARGET)}


# --------------------------------------------------------------------------
# signals
# --------------------------------------------------------------------------
def sig_ma_cross(closes, fast, slow, long_only=False):
    out = {}
    for c, s in closes.items():
        f, sl = s.rolling(fast).mean(), s.rolling(slow).mean()
        sig = np.sign(f - sl)
        if long_only:
            sig = sig.clip(lower=0.0)
        out[c] = sig.where(sl.notna())
    return out


def sig_tsmom(closes, lookback, skip, long_only=False):
    out = {}
    for c, s in closes.items():
        past = s.shift(lookback + skip)
        sig = np.sign(s / past - 1.0)
        if long_only:
            sig = sig.clip(lower=0.0)
        out[c] = sig.where((s.notna()) & (past.notna()))
    return out


def sig_donchian(closes, highs, lows, entry, exit_, long_only=False):
    out = {}
    for c, s in closes.items():
        hi = highs[c].reindex(s.index).rolling(entry).max().shift(1)
        lo = lows[c].reindex(s.index).rolling(exit_).min().shift(1)
        state, arr = 0, []
        for price, h, l in zip(s.values, hi.values, lo.values):
            if not np.isfinite(price) or not np.isfinite(h) or not np.isfinite(l):
                arr.append(np.nan)
                continue
            if state == 0:
                state = 1 if price > h else (-1 if price < l else 0)
            elif state == 1 and price < l:
                state = -1 if not long_only else 0
            elif state == -1 and price > h:
                state = 1
            elif state == 0 and long_only and price > h:
                state = 1
            arr.append(float(state))
        out[c] = pd.Series(arr, index=s.index).replace(0.0, np.nan)
    return out


def sig_reversal(closes, window, long_only=False):
    out = {}
    for c, s in closes.items():
        past = s.shift(window)
        sig = -np.sign(s / past - 1.0)
        if long_only:
            sig = sig.clip(lower=0.0)
        out[c] = sig.where((s.notna()) & (past.notna()))
    return out


def sig_xs_rank(closes, window, k):
    frame = pd.DataFrame(closes)
    ret = frame / frame.shift(window) - 1.0
    ranks = ret.rank(axis=1, pct=True)
    kk = k / max(len(frame.columns), 1)
    sig = pd.DataFrame(np.nan, index=frame.index, columns=frame.columns)
    sig[ranks >= 1.0 - kk] = 1.0
    sig[ranks <= kk] = -1.0
    return {c: sig[c] for c in frame.columns}


def build_signals(cfg, closes, highs, lows):
    rule = cfg["rule"]
    p = cfg.get("params") or {}
    lo = bool(cfg.get("long_only", False))
    if rule == "ma_cross":
        return sig_ma_cross(closes, p.get("fast", 50), p.get("slow", 200), lo)
    if rule == "tsmom":
        return sig_tsmom(closes, p.get("lookback", 252), p.get("skip", 21), lo)
    if rule == "donchian":
        return sig_donchian(closes, highs, lows, p.get("entry", 55), p.get("exit", 20), lo)
    if rule == "reversal":
        return sig_reversal(closes, p.get("window", 5), lo)
    if rule == "xs_rank":
        return sig_xs_rank(closes, p.get("window", 60), p.get("k", 1))
    raise ValueError(f"unknown rule {rule}")


# --------------------------------------------------------------------------
# one arm
# --------------------------------------------------------------------------
def run_arm(cfg, panel, dates, closes, rets, vols, highs, lows, split, tags=None):
    sigs = build_signals(cfg, closes, highs, lows)
    pos, live = bc.vol_weighted_positions(sigs, vols, target_vol=cfg.get("target_vol", 0.10))
    if pos is None or not pos.notna().any().any():
        return None
    gross, net, turn = bc.apply_costs(pos, rets, cost_bp_side=cfg.get("cost_bp_side", 3.0))
    net = net.reindex(dates).fillna(0.0)
    gross = gross.reindex(dates).fillna(0.0)
    turn = turn.reindex(dates).fillna(0.0)

    reading = bc.split_perf(net.values, dates, split=split)
    ctrl = bc.random_sign_control(pos, rets, draws=cfg.get("control_draws", 100))
    mde = (1.96 * (reading["full"]["vol_pct"] or 0)
           / max((reading["full"]["n"] or 1) / bc.TRADING_DAYS, 1e-9) ** 0.5
           if reading["full"]["vol_pct"] else None)
    target = cfg.get("target_edge_pp", 5.0)
    powered = None if mde is None else bool(mde <= target)

    c = cfg.get("crit", {})
    checks = {
        "H1_full_ge": bool(reading["full"]["ann_pct"] is not None
                           and reading["full"]["ann_pct"] >= c.get("H1_full_pct", 4.0)),
        "H2_oos_ge": bool(reading["oos"]["ann_pct"] is not None
                          and reading["oos"]["ann_pct"] >= c.get("H2_oos_pct", 3.0)
                          and (reading["oos"]["sharpe"] or -9) >= c.get("H2_oos_sharpe", 0.4)),
        "H3_both_halves": bool((reading.get("first_half_ann_pct") or -9) > 0
                               and (reading.get("second_half_ann_pct") or -9) > 0),
        "H4_drop_best": bool(reading["full"]["drop_best_year_ann_pct"] is not None
                             and reading["full"]["drop_best_year_ann_pct"]
                             >= c.get("H4_drop_best_pct", 1.5)),
        "H5_control": bool(ctrl["p_value"] is not None
                           and ctrl["p_value"] < c.get("H5_p", 0.05)),
    }
    verdict = bc.verdict_of(checks)
    if verdict != "NO_EDGE" and powered is False:
        verdict = "UNINFORMATIVE_AT_TARGET"
    # the same H1 question asked on the face's own declared size
    size = normalize_to_target(reading["full"]["ann_pct"],
                               reading["full"].get("vol_pct"),
                               round(float(cfg.get("target_vol", 0.10)) * 100.0, 4))
    h1_line = c.get("H1_full_pct", 4.0)
    size["h1_line_pct"] = h1_line
    size["H1_normalized_ge"] = (None if size["ann_at_target_pct"] is None
                                else bool(size["ann_at_target_pct"] >= h1_line))
    size["H1_flips_under_normalisation"] = (
        None if (size["H1_normalized_ge"] is None or checks["H1_full_ge"] is None)
        else bool(size["H1_normalized_ge"] != checks["H1_full_ge"]))
    return {
        "tags": tags or {},
        "common_window": reading["full"],
        "oos_2024_after": reading["oos"],
        "first_half_ann_pct": reading.get("first_half_ann_pct"),
        "second_half_ann_pct": reading.get("second_half_ann_pct"),
        "turnover_per_year": round(float(turn.sum()) * bc.TRADING_DAYS / max(len(turn), 1), 2),
        "cost_drag_ann_pct": round((float(gross.mean()) - float(net.mean()))
                                   * bc.TRADING_DAYS * 100, 2),
        "avg_live": round(float(live.reindex(dates).mean()), 1),
        "mde_pp": None if mde is None else round(mde, 2),
        "powered_for_target": powered,
        "size_normalized": size,
        "control": ctrl,
        "checks": checks,
        "verdict": verdict,
        "series": net,
    }


def buy_and_hold(dates, closes, rets, vols, split, cost_bp_side, target_vol=0.10):
    """Equal-risk buy-and-hold on the same basket.

    target_vol must be the arm's own vol target: the benchmark and the arm have to
    be the same size of book before their annualised numbers can be subtracted.
    """
    sig = {c: pd.Series(1.0, index=s.index).where(s.notna()) for c, s in closes.items()}
    pos, _ = bc.vol_weighted_positions(sig, vols, target_vol=target_vol)
    if pos is None:
        return None
    gross, net, turn = bc.apply_costs(pos, rets, cost_bp_side=cost_bp_side)
    net = net.reindex(dates).fillna(0.0)
    reading = bc.split_perf(net.values, dates, split=split)
    return {"common_window": reading["full"], "oos_2024_after": reading["oos"]}


# --------------------------------------------------------------------------
# cell
# --------------------------------------------------------------------------
def _same_size_measured(arms, bh, bh_tv):
    """Was the arm and the benchmark actually the same size of book?

    The declared target is one thing; the realised vol is what got compared. A
    ratio far from 1.0 means the excess printed on this face was taken between
    books of different size, however carefully both were *aimed* at the target.
    """
    out = {"declared_vol_pct": round(float(bh_tv) * 100.0, 4),
           "arms_off_target": 0, "n_arms": len(arms),
           "n_arms_with_realized_vol": 0,
           "bench_realized_vol_pct": None, "bench_ratio": None,
           "bench_off_target": None, "not_measurable": None}
    bvol = ((bh or {}).get("common_window") or {}).get("vol_pct")
    if bvol:
        out["bench_realized_vol_pct"] = round(float(bvol), 4)
        out["bench_ratio"] = round(float(bvol) / (float(bh_tv) * 100.0), 4)
        out["bench_off_target"] = bool(abs(out["bench_ratio"] - 1.0) > SIZE_OFF_TARGET)
    for a in arms:
        s = a.get("size_normalized") or {}
        if s.get("realized_vol_pct"):
            out["n_arms_with_realized_vol"] += 1
        if s.get("off_target"):
            out["arms_off_target"] += 1
    # a census arm carries no vol (run_census does not keep the series), so silence
    # there is "not measured", never "on target" -- the difference between a green
    # and a blind spot (r1311 family)
    if not arms or out["bench_off_target"] is None:
        out["not_measurable"] = "benchmark realised vol or arms missing"
        out["same_size"] = None
    elif out["n_arms_with_realized_vol"] < len(arms):
        out["not_measurable"] = (f"{len(arms) - out['n_arms_with_realized_vol']} of "
                                 f"{len(arms)} arms publish no realised vol")
        out["same_size"] = None
    else:
        out["same_size"] = bool(not out["bench_off_target"]
                                and out["arms_off_target"] == 0)
    return out


def run_census(cfg, panel, dates, closes, rets, vols, highs, lows, split):
    """Run the whole grid once and report the surface, not a single point.

    A single parameter set cannot tell a real edge from a lucky one. The census
    runs every (rule x window) combination on the same panel and reports how many
    are powered, how many keep the same sign, and what the median powered result
    is. This is the honest way to burn minutes of CPU: one artifact that says
    "this space is noise" or "this space leans positive", instead of a hundred
    cells that each say nothing.
    """
    rows = []
    grid = cfg.get("grid") or []
    target = cfg.get("target_edge_pp", 5.0)
    for spec in grid:
        sub = dict(cfg)
        sub["rule"] = spec["rule"]
        sub["params"] = spec.get("params") or {}
        sub["long_only"] = bool(spec.get("long_only", cfg.get("long_only", False)))
        arm = run_arm(sub, panel, dates, closes, rets, vols, highs, lows, split,
                      tags={"combo": f"{spec['rule']}|{sub['params']}|"
                                       f"{'long' if sub['long_only'] else 'ls'}"})
        if not arm:
            continue
        rows.append({
            "combo": f"{spec['rule']}|{sub['params']}|"
                     f"{'long' if sub['long_only'] else 'ls'}",
            "ann_pct": arm["common_window"]["ann_pct"],
            "sharpe": arm["common_window"]["sharpe"],
            "mdd_pct": arm["common_window"]["mdd_pct"],
            "oos_ann_pct": arm["oos_2024_after"]["ann_pct"],
            "turnover": arm["turnover_per_year"],
            "mde_pp": arm["mde_pp"],
            "powered": arm["powered_for_target"],
            "verdict": arm["verdict"],
        })
    if not rows:
        return {"rows": [], "verdict": "DATA_BLOCKED"}
    powered = [r for r in rows if r["powered"]]
    pos = [r for r in powered if (r["ann_pct"] or 0) > 0]
    neg = [r for r in powered if (r["ann_pct"] or 0) < 0]
    anns = [r["ann_pct"] for r in rows if r["ann_pct"] is not None]
    med = float(np.median(anns)) if anns else None
    if not powered:
        verdict = "CENSUS_UNPOWERED"
    elif len(pos) and len(neg):
        verdict = "CENSUS_SIGN_MIXED"
    elif pos:
        verdict = "CENSUS_LEANS_POSITIVE"
    else:
        verdict = "CENSUS_LEANS_NEGATIVE"
    # `powered` is a resolution statement (can this sample see target_edge?), not a
    # merit one. A lean headline with zero GO arms tells a reader the space "leans
    # positive" while every rule inside it failed every gate -- so the count of arms
    # that actually passed travels beside the headline instead of behind it
    # (scripts/bench_census_arm_contradiction.py measures how often this bites).
    n_go = sum(1 for r in rows if r["verdict"] == "GO")
    h1_line = (cfg.get("crit") or {}).get("H1_full_pct", 4.0)
    n_clear_h1 = sum(1 for r in rows
                     if r["ann_pct"] is not None and r["ann_pct"] >= h1_line)
    caveat = None
    if verdict in ("CENSUS_LEANS_POSITIVE", "CENSUS_LEANS_NEGATIVE") and n_go == 0:
        caveat = (f"{verdict} describes the SPACE, not any rule in it: 0 of "
                  f"{len(rows)} arms passed all gates ({n_clear_h1} cleared only the "
                  f"{h1_line}% H1 line). Do not read this headline as 'ready to trade'.")
    return {
        "rows": rows,
        "n_combos": len(rows),
        "n_powered": len(powered),
        "n_positive_powered": len(pos),
        "n_negative_powered": len(neg),
        "n_arms_go": n_go,
        "n_arms_clear_h1": n_clear_h1,
        "headline_caveat": caveat,
        "median_ann_pct": None if med is None else round(med, 2),
        "best_powered": max(powered, key=lambda r: r["ann_pct"]) if powered else None,
        "worst_powered": min(powered, key=lambda r: r["ann_pct"]) if powered else None,
        "target_edge_pp": target,
        "verdict": verdict,
    }


def run_cell(cfg):
    bc.weight_priority()
    products = cfg.get("products") or bc.FUTURES
    panel = bc.load_futures_products(products)
    if len(panel) < 1:
        return {"ok": False, "error": "no product data"}
    dates, closes, rets, vols = bc.align_futures(panel)
    highs, lows = bc.align_highs_lows(panel, closes)
    split = cfg.get("split", "2024-01-01")

    arms = []
    census = None
    if cfg["type"] == "census":
        census = run_census(cfg, panel, dates, closes, rets, vols, highs, lows, split)
        for r in census.get("rows", []):
            r["tags"] = {}
        arms = [{"tags": {"variant": r["combo"]},
                 "common_window": {"ann_pct": r["ann_pct"], "sharpe": r["sharpe"],
                                   "mdd_pct": r["mdd_pct"], "drop_best_year_ann_pct": None},
                 "oos_2024_after": {"ann_pct": r["oos_ann_pct"]},
                 "first_half_ann_pct": None, "second_half_ann_pct": None,
                 "turnover_per_year": r["turnover"], "mde_pp": r["mde_pp"],
                 "powered_for_target": r["powered"], "verdict": r["verdict"],
                 "checks": {}} for r in census.get("rows", [])]
    elif cfg["type"] == "robust":
        for v in cfg.get("variants", []):
            sub = dict(cfg)
            sub["params"] = dict(cfg.get("params") or {}, **(v.get("params") or {}))
            if v.get("long_only") is not None:
                sub["long_only"] = v["long_only"]
            arm = run_arm(sub, panel, dates, closes, rets, vols, highs, lows, split,
                          tags=v.get("tags") or {"variant": v.get("name")})
            if arm:
                arms.append(arm)
    else:
        arm = run_arm(cfg, panel, dates, closes, rets, vols, highs, lows, split)
        if arm:
            arms.append(arm)

    bh_tv = cfg.get("target_vol", 0.10)
    bh = buy_and_hold(dates, closes, rets, vols, split, cfg.get("cost_bp_side", 3.0),
                      target_vol=bh_tv)
    bh_ann = ((bh or {}).get("common_window") or {}).get("ann_pct")
    for a in arms:
        a.pop("series", None)
        ann = a["common_window"]["ann_pct"]
        excess = None if (ann is None or bh_ann is None) else round(ann - bh_ann, 2)
        a["bench_target_vol"] = bh_tv
        a["excess_vs_bench_pp"] = excess
        # the arm can only claim an excess it could have seen: same yardstick as its own MDE
        a["excess_clears_mde"] = (None if (excess is None or not a.get("mde_pp"))
                                  else bool(excess >= a["mde_pp"]))

    if cfg["type"] == "census" and census:
        pooled = census["verdict"]
    elif cfg["type"] == "robust" and arms:
        anns = [a["common_window"]["ann_pct"] for a in arms]
        mdes = [a["mde_pp"] for a in arms if a["mde_pp"]]
        signs = {1 if x > 0 else -1 for x in anns}
        stable = len(signs) == 1 and mdes and min(abs(x) for x in anns) > max(mdes)
        pooled = ("STABLE_POSITIVE" if stable and 1 in signs
                  else ("STABLE_NEGATIVE" if stable else "UNSTABLE_ACROSS_PARAMS"))
    else:
        pooled = arms[0]["verdict"] if arms else "DATA_BLOCKED"

    payload = {
        "cell": cfg["id"],
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(pd.Timestamp(dates[-1]).date()),
        "question": cfg.get("question"),
        "config": {k: v for k, v in cfg.items() if k != "variants"} | {
            "variants": len(cfg.get("variants", []))} if cfg.get("variants") else cfg,
        "coverage": {"bars": int(len(dates)), "start": str(pd.Timestamp(dates[0]).date()),
                     "end": str(pd.Timestamp(dates[-1]).date()),
                     "products": sorted(panel)},
        "arms": arms,
        "benchmark_buy_and_hold": bh,
        "benchmark_sizing": {
            "target_vol": bh_tv,
            # `same_yardstick` stays True because the CODE now scales the benchmark
            # to the arm's target. That is a claim about the code, not a measurement
            # of the two books: r2152 measured 13/17 faces whose realised vol missed
            # its own declared target by >10%, so the realised ratio is reported
            # beside the claim and never inferred from it.
            "same_yardstick": True,
            "same_yardstick_is_a_claim_not_a_measurement": True,
            "same_yardstick_measured": _same_size_measured(arms, bh, bh_tv),
            "rule": ("the benchmark is scaled to the arm's own vol target; a hardwired "
                     "0.10 made 9 faces compare books of different size "
                     "(results/bench_go_ruler_audit.json, r2136)"),
            "arms_excess_clears_own_mde": sum(1 for a in arms if a.get("excess_clears_mde")),
        },
        "criteria": {"cost_bp_side": cfg.get("cost_bp_side", 3.0),
                     "target_edge_pp": cfg.get("target_edge_pp", 5.0),
                     "split": split, "crit": cfg.get("crit")},
        "verdict": pooled,
    }
    # the census headline's own numbers must reach the face, or a reader can only
    # see the word and never the count behind it
    if census:
        payload["census"] = {
            k: census.get(k) for k in
            ("n_combos", "n_powered", "n_positive_powered", "n_negative_powered",
             "n_arms_go", "n_arms_clear_h1", "headline_caveat", "median_ann_pct")
        }
    out = os.path.join(RESULTS, f"bench_{cfg['id']}.json")
    bc.write_json(out, payload)

    lines = [f"# {cfg.get('question') or cfg['id']}", "",
             f"cell `{cfg['id']}` · type `{cfg['type']}` · rule `{cfg.get('rule')}` · "
             f"cutoff {payload['evidence_cutoff']} · **{pooled}**", "",
             "| 臂 | 全期年化 | 夏普 | 回撤 | 样本外年化 | 前后半 | 剔除最好一年 | MDE | 可分辨? | 超额vs同口径基准 | 判决 |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for a in arms:
        f = a["common_window"]
        tag = a["tags"].get("variant") or a["tags"].get("name") or "arm"
        lines.append(f"| {tag} | {bc.fmt_pct(f['ann_pct'])} | {bc.fmt_num(f['sharpe'])} | "
                     f"{bc.fmt_pct(f['mdd_pct'])} | {bc.fmt_pct(a['oos_2024_after']['ann_pct'])} | "
                     f"{a['first_half_ann_pct']}/{a['second_half_ann_pct']} | "
                     f"{bc.fmt_pct(f['drop_best_year_ann_pct'])} | {a['mde_pp']} | "
                     f"{a['powered_for_target']} | "
                     f"{bc.fmt_pct(a.get('excess_vs_bench_pp'))}"
                     f"{'' if a.get('excess_clears_mde') else ('?' if a.get('excess_clears_mde') is None else ' (below MDE)')} | "
                     f"**{a['verdict']}** |")
    if bh:
        b = bh["common_window"]
        lines.append(f"| 同篮子买入持有 | {bc.fmt_pct(b['ann_pct'])} | {bc.fmt_num(b['sharpe'])} | "
                     f"{bc.fmt_pct(b['mdd_pct'])} | {bc.fmt_pct(bh['oos_2024_after']['ann_pct'])} | "
                     f"— | — | — | — | — | BENCHMARK |")
    lines += ["", f"判据：{json.dumps(cfg.get('crit'), ensure_ascii=False)}", "",
              "MDE = 1.96 × 年化波动 ÷ √年数；观测值落在这个范围内时，"
              "「没看见」不等于「不存在」。"]
    with open(os.path.join(RESEARCH, f"BENCH-{cfg['id'].upper()}.md"),
              "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")

    print(json.dumps({"ok": True, "cell": cfg["id"], "verdict": pooled,
                      "arms": len(arms)}, ensure_ascii=False, indent=1))
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    a = ap.parse_args()
    path = a.config if os.path.isabs(a.config) else os.path.join(bc.ROOT, a.config)
    cfg = json.load(open(path, encoding="utf-8"))
    res = run_cell(cfg)
    return 0 if isinstance(res, dict) and res.get("ok", True) else 1


if __name__ == "__main__":
    sys.exit(main())
