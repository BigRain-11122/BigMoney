"""D-20260930-41 deliverable #2 -- allocation policy scan (weights x rebalance rules).

ORDER = docs/audits/ORDER-retail-quant-research-track-20260930.md sec.2 item 2
(full-grid PUBLICATION scan, ORDER sec.5-2 exception; "可赢/容量无限/不拥挤" dim).
Prereg (frozen pre-burn) = research/ALLOCATION_POLICY_SCAN.md.

Four-asset face (G-ANCHOR-FACE four-tuples, raw pd.read_csv direct reads,
truncated to EVIDENCE_CUTOFF at assembly -- RW-2 spirit):
    data/daily/sh510300.csv   stock leg, from 2012-05-28, warmup 0
    data/daily/sh511010.csv   bond leg,  from 2013-04-09, warmup 0
    data/daily/sh518880.csv   gold leg,  from 2013-07-29, warmup 0
    data/repo_daily/GC001.csv  cash leg,  from 2011-05-13, warmup 0
                              (daily ret = PRIOR bar's annualized close
                               percent / 365, strictly causal, ffill gaps)
Joint window 2013-07-29 -> 2026-09-22 (bond/gold twins last bar == cutoff;
6td tail staleness disclosed in prereg sec.2 -- 13.1y depth over freshness).

NOT a registration batch (prereg sec.0): no G1'/G2/DSR/PBO gates, no single
winner; all 302 cells (75 weights x 4 rules + 2 baselines) are published.
Trial budget: append_ledger +302 into the D-41 500/30d gate.

Usage (module mode, cwd = repo root):
    python -m scripts.allocation_policy_scan probe      # face anchors + gates
    python -m scripts.allocation_policy_scan run        # full scan + products
    python -m scripts.allocation_policy_scan selftest   # hermetic (synthetic)
Direct run also works (repo-root sys.path fix mirrors account_cost_tax).
"""
import json
import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
_SCRIPTS_DIR = os.path.join(_REPO_ROOT, "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

# GBK console reconfigure entry law (r236 family)
if hasattr(sys.stdout, "encoding") and sys.stdout.encoding \
        and sys.stdout.encoding.lower().replace("-", "") not in ("utf8", "utf8mb4"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from knowledge import cost_spec  # noqa: E402

try:
    from scripts import science_gates as sg
except ImportError:
    import science_gates as sg

BATCH = "ALLOC-POLICY-SCAN-P1"
EVIDENCE_CUTOFF = "2026-09-22"
OUT_DIR = os.path.join(_REPO_ROOT, "results", "allocation_policy_scan")
FAMILY_KEY = "allocation-policy-scan"

# --- frozen face four-tuples (prereg sec.2; probe asserts these literally) ---
FACES = {
    "stock": {"path": "data/daily/sh510300.csv", "first_bar": "2012-05-28",
              "rows_freeze": 3487},
    "bond": {"path": "data/daily/sh511010.csv", "first_bar": "2013-04-09",
             "rows_freeze": 3273},
    "gold": {"path": "data/daily/sh518880.csv", "first_bar": "2013-07-29",
             "rows_freeze": 3200},
    "cash": {"path": "data/repo_daily/GC001.csv", "first_bar": "2011-05-13",
             "rows_freeze": 3739},
}
LEG_ORDER = ["stock", "bond", "gold", "cash"]
ETF_LEGS = ("stock", "bond", "gold")
JOINT_START = "2013-07-29"          # max of first bars == gold first bar

# --- frozen grid (prereg sec.3): 75 weights x 4 rules + 2 baselines = 302 ---
STOCK_W = [0.20, 0.30, 0.40, 0.50, 0.60]
BOND_SHARE = [1.00, 0.75, 0.50, 0.25, 0.00]   # bond share of non-stock sleeve
CASH_W = [0.00, 0.10, 0.20]
RULES = ["annual", "quarterly", "monthly", "threshold5"]
BASELINES = ["stock_bh", "cash_only"]
N_TRIALS = len(STOCK_W) * len(BOND_SHARE) * len(CASH_W) * len(RULES) \
    + len(BASELINES)

COST_PER_SIDE = None  # set by _cost_check(): cost_spec.X1_RATE (imported)
THRESHOLD_BAND = 0.05  # 5pp absolute deviation -> rebalance next close
ROLLS = {"worst3y": 756, "worst5y": 1250, "worst10y": 2520}
DD_WINDOW = 252        # 1y window for P(see -20%)
DD_HIT = -0.20
MIN_START_HORIZON = 756  # 3y minimum for all-start headline stats
CASH_RET_DIV = 100.0 * 365.0  # annualized percent -> daily fraction


def _cost_check():
    """Face A per-side cost, imported + anchor-asserted (CN-C7 13.041bp/side)."""
    global COST_PER_SIDE
    if not cost_spec.verify():
        raise RuntimeError("cost_spec.verify() failed")
    x1 = float(cost_spec.X1_RATE)
    if abs(x1 * 1e4 - 13.041) > 1e-3:
        raise RuntimeError(f"X1_RATE anchor drift: {x1}")
    COST_PER_SIDE = x1
    return x1


def _etf_cost_leg_mask():
    return np.array([1.0 if leg in ETF_LEGS else 0.0 for leg in LEG_ORDER])


def load_faces(faces_root=None, cutoff=None, joint_start=None, min_days=3000):
    """Load 4 faces, truncate to cutoff, join on the stock-leg calendar.

    G-ANCHOR-FACE: loads EXACTLY the prereg-declared relative paths; any anchor
    mismatch -> ValueError (fail-closed VOID, reported as face-mismatch).
    """
    cutoff = cutoff or EVIDENCE_CUTOFF
    joint_start = joint_start or JOINT_START
    root = faces_root or _REPO_ROOT
    closes, facts = {}, {}
    for leg in LEG_ORDER:
        p = os.path.join(root, FACES[leg]["path"])
        if not os.path.exists(p):
            raise ValueError(f"face-mismatch: missing face {leg} at {p}")
        df = pd.read_csv(p)
        if df["date"].duplicated().any():
            raise ValueError(f"face-mismatch: duplicate dates in {leg}")
        if str(df["date"].iloc[0]) != FACES[leg]["first_bar"]:
            raise ValueError(
                f"face-mismatch: {leg} first bar {df['date'].iloc[0]} != "
                f"anchor {FACES[leg]['first_bar']}")
        if str(df["date"].iloc[-1]) < cutoff:
            raise ValueError(
                f"face-mismatch: {leg} last bar {df['date'].iloc[-1]} < "
                f"evidence_cutoff {cutoff}")
        if len(df) < FACES[leg]["rows_freeze"] - 2:
            raise ValueError(
                f"face-mismatch: {leg} rows {len(df)} < freeze snapshot "
                f"{FACES[leg]['rows_freeze']} - 2")
        df = df[df["date"] <= cutoff].reset_index(drop=True)
        closes[leg] = df.set_index("date")["close"]
        facts[leg] = {"rows": int(len(df)), "first": str(df["date"].iloc[0]),
                      "last": str(df["date"].iloc[-1])}
    master = [d for d in closes["stock"].index if d >= joint_start]
    if len(master) < min_days:
        raise ValueError(f"completeness gate: joint window {len(master)} < {min_days}")
    rets = np.zeros((len(master), 4), dtype=float)
    ffills = {}
    for j, leg in enumerate(LEG_ORDER):
        s = closes[leg].reindex(master)
        n_na = int(s.isna().sum())
        ffills[leg] = n_na
        s = s.ffill()
        if leg == "cash":
            # prior bar's annualized rate accrues overnight (strictly causal)
            rate_prev = s.shift(1).bfill()
            rets[:, j] = rate_prev.values / CASH_RET_DIV
        else:
            rets[:, j] = (s.values[1:] / s.values[:-1] - 1.0).tolist() + [0.0]
    for leg in ETF_LEGS:
        cov = 1.0 - ffills[leg] / len(master)
        if cov < 0.99:
            raise ValueError(f"completeness gate: {leg} coverage {cov:.4f} < 0.99")
    if np.isnan(rets).any():
        raise ValueError("face-mismatch: NaN in assembled returns")
    facts["ffill_counts"] = ffills
    facts["n_days"] = len(master)
    facts["joint_start"] = master[0]
    facts["joint_end"] = master[-1]
    return master, rets, facts


def _calendar_mask(dates, rule):
    """Per-day bool: t (t>=1) is the first trading day of the rule's period."""
    dti = pd.to_datetime(pd.Index(dates))
    months, quarters, years = [], [], []
    prev_m = prev_q = prev_y = None
    for d in dti:
        m, q, y = d.month, (d.month - 1) // 3 + 1, d.year
        months.append(m != prev_m)
        quarters.append(q != prev_q)
        years.append(y != prev_y)
        prev_m, prev_q, prev_y = m, q, y
    if rule == "monthly":
        mask = np.array(months, dtype=bool)
    elif rule == "quarterly":
        mask = np.array(quarters, dtype=bool)
    elif rule == "annual":
        mask = np.array(years, dtype=bool)
    elif rule == "none":
        mask = np.zeros(len(dates), dtype=bool)
    else:
        raise ValueError(f"unknown calendar rule {rule}")
    mask[0] = False
    return mask


def simulate(rets, targets, start_idx, rule, store_path=False, cal_mask=None):
    """Vectorized multi-row portfolio sim (prereg sec.3 execution model):
    calendar rules execute at the close of the period's first trading day
    (calendar known in advance); threshold5 signals at close t -> executes at
    close t+1 (strictly causal, one-day lag). Weights drift with returns;
    rebalances reset to target and pay per-side Face A cost on ETF-leg deltas.
    """
    n = rets.shape[0]
    R = targets.shape[0]
    w = np.zeros((R, 4), dtype=float)
    V = np.ones(R, dtype=float)
    cost_leg = _etf_cost_leg_mask()
    entry_cost = (targets * cost_leg).sum(1) * COST_PER_SIDE
    n_reb = np.zeros(R, dtype=int)
    tot_cost = np.zeros(R, dtype=float)
    pending = np.zeros(R, dtype=bool)
    path = np.ones((R, n), dtype=float) if store_path else None
    start_idx = np.asarray(start_idx)
    for t in range(n):
        newly = (start_idx == t)
        if newly.any():
            V[newly] = 1.0 - entry_cost[newly]
            w[newly] = targets[newly]
            pending[newly] = False
        if t > 0:
            act = start_idx < t
            pr = (w * rets[t]).sum(1)
            pr = np.where(act, pr, 0.0)
            pr = np.maximum(pr, -0.999999)
            V *= (1.0 + pr)
            w = w * (1.0 + rets[t]) / (1.0 + pr)[:, None]
            if rule == "threshold5":
                exec_mask = act & pending
            else:
                exec_mask = act & cal_mask[t]
            if exec_mask.any():
                cost = (np.abs(targets - w) * cost_leg).sum(1) * COST_PER_SIDE
                V[exec_mask] *= (1.0 - cost[exec_mask])
                w[exec_mask] = targets[exec_mask]
                n_reb[exec_mask] += 1
                tot_cost[exec_mask] += cost[exec_mask]
            if rule == "threshold5":
                pending = act & (np.abs(w - targets).max(1) >= THRESHOLD_BAND)
        if store_path:
            path[:, t] = V
    return {"V": V, "path": path, "n_reb": n_reb, "tot_cost": tot_cost,
            "entry_cost": entry_cost}


def simulate_with_dates(dates, rets, targets, start_idx, rule, store_path=False):
    cal_mask = _calendar_mask(dates, rule) \
        if rule in ("annual", "quarterly", "monthly", "none") else None
    return simulate(rets, targets, start_idx, rule, store_path, cal_mask)


def _path_metrics(path):
    """Headline-path metrics on the value curve (entry cost included at t0)."""
    v = np.asarray(path, dtype=float)
    n = len(v)
    out = {}
    rets_d = v[1:] / v[:-1] - 1.0
    years = (n - 1) / 252.0
    out["cagr"] = float((v[-1] / 1.0) ** (1.0 / years) - 1.0) if n > 1 else 0.0
    sd = float(np.std(rets_d, ddof=1))
    mean = float(np.mean(rets_d))
    out["vol"] = float(sd * np.sqrt(252.0))
    out["sharpe"] = float(mean / sd * np.sqrt(252.0)) if sd > 0 else 0.0
    out["t_info"] = float(out["sharpe"] * np.sqrt(years))
    out["maxdd"] = float((v / np.maximum.accumulate(v) - 1.0).min())
    logv = np.log(v)
    for k, L in ROLLS.items():
        if n > L:
            d = logv[L:] - logv[:-L]
            out[k] = float(np.exp(np.min(d) * 252.0 / L) - 1.0)
        else:
            out[k] = None
    # P(see -20% within a 1y window): daily-stepped, peak reset at window start
    sw = np.lib.stride_tricks.sliding_window_view(v, DD_WINDOW)
    runmax = np.maximum.accumulate(sw, axis=1)
    dd = (sw / runmax - 1.0).min(axis=1)
    out["p_dd20_1y"] = float((dd <= DD_HIT).mean())
    out["n_dd_windows"] = int(len(dd))
    return out


def _grid_weights():
    """75 weight rows (prereg sec.3): s(1-c) / (1-s)b(1-c) / (1-s)(1-b)(1-c) / c."""
    rows, keys = [], []
    for s in STOCK_W:
        for b in BOND_SHARE:
            for c in CASH_W:
                rows.append([s * (1 - c), (1 - s) * b * (1 - c),
                             (1 - s) * (1 - b) * (1 - c), c])
                keys.append({"s": s, "bond_share": b, "cash": c})
    return np.array(rows), keys


def _monthly_start_idx(dates):
    """Positions of each month's first trading day; index 0 = joint start."""
    idx = [0]
    prev_m = None
    for i, d in enumerate(pd.to_datetime(pd.Index(dates))):
        if prev_m is not None and d.month != prev_m:
            idx.append(i)
        prev_m = d.month
    return np.array(idx)


def run(write=True):
    _cost_check()
    dates, rets, facts = load_faces()
    fam = sg.closed_family_check(FAMILY_KEY)
    if fam.get("status") != "open":
        raise RuntimeError(f"closed-family gate: {fam}")
    weights, keys = _grid_weights()
    nW = len(weights)
    starts = _monthly_start_idx(dates)
    n = rets.shape[0]
    horizon_days = (n - 1) - starts
    valid = horizon_days >= MIN_START_HORIZON
    n_valid = int(valid.sum())
    n_short = int((~valid).sum())

    cells = []
    for rule in RULES:
        # pass A: 75 headline rows, full paths stored
        simA = simulate_with_dates(dates, rets, weights,
                                   np.zeros(nW, dtype=int), rule,
                                   store_path=True)
        # pass B: 75 x n_starts fresh-entry rows, finals only
        s_rows = np.repeat(np.arange(nW), len(starts))
        s_start = np.tile(starts, nW)
        simB = simulate_with_dates(dates, rets, weights[s_rows], s_start, rule,
                                  store_path=False)
        for i in range(nW):
            m = _path_metrics(simA["path"][i])
            cagrs = np.array([
                simB["V"][i * len(starts) + j] ** (252.0 / int(horizon_days[j]))
                - 1.0
                for j in range(len(starts))])
            head = cagrs[valid]
            a = {
                "cell_id": f"{keys[i]['s']:.2f}|{keys[i]['bond_share']:.2f}|"
                           f"{keys[i]['cash']:.2f}|{rule}",
                "s": keys[i]["s"], "bond_share": keys[i]["bond_share"],
                "cash": keys[i]["cash"], "rule": rule,
                "w": [round(float(x), 6) for x in weights[i]],
                "n_rebalances": int(simA["n_reb"][i]),
                "cost_drag_annual": float(simA["tot_cost"][i] * 252.0 / (n - 1)),
                "allstart_n_valid": n_valid,
                "allstart_short": n_short,
                "allstart_best": float(head.max()),
                "allstart_worst": float(head.min()),
                "allstart_p25": float(np.percentile(head, 25)),
                "allstart_median": float(np.percentile(head, 50)),
                "allstart_p75": float(np.percentile(head, 75)),
                "allstart_pos_share": float((head > 0).mean()),
            }
            a.update(m)
            a["pass"] = bool(a["worst5y"] is not None and a["worst5y"] > 0
                             and a["allstart_pos_share"] >= 0.50)
            cells.append(a)

    # baselines (rule "none": never rebalances)
    simBH = simulate_with_dates(dates, rets, np.array([[1.0, 0.0, 0.0, 0.0]]),
                                np.zeros(1, dtype=int), "none", store_path=True)
    simCH = simulate_with_dates(dates, rets, np.array([[0.0, 0.0, 0.0, 1.0]]),
                                np.zeros(1, dtype=int), "none", store_path=True)
    for name, sim in (("stock_bh", simBH), ("cash_only", simCH)):
        m = _path_metrics(sim["path"][0])
        cells.append({"cell_id": f"baseline|{name}", "s": None,
                      "bond_share": None, "cash": None, "rule": "none",
                      "w": None, "n_rebalances": 0,
                      "cost_drag_annual": float(sim["tot_cost"][0] * 252.0 / (n - 1)),
                      "allstart_n_valid": 0, "allstart_short": 0,
                      "allstart_best": None, "allstart_worst": None,
                      "allstart_p25": None, "allstart_median": None,
                      "allstart_p75": None, "allstart_pos_share": None,
                      "baseline": name, **m, "pass": None})

    grid_cells = [c for c in cells if c.get("baseline") is None]
    n_pass = sum(1 for c in grid_cells if c["pass"])
    per_rule = len(STOCK_W) * len(BOND_SHARE) * len(CASH_W)
    by_rule = {r: sum(1 for c in grid_cells if c["rule"] == r and c["pass"])
               for r in RULES}
    by_s = {s: sum(1 for c in grid_cells if c["s"] == s and c["pass"])
            for s in STOCK_W}
    by_c = {cv: sum(1 for c in grid_cells if c["cash"] == cv and c["pass"])
            for cv in CASH_W}
    result = {
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "science_gates": {"cutoff_meta": sg.cutoff_meta(EVIDENCE_CUTOFF)},
        "batch": BATCH,
        "prereg": "research/ALLOCATION_POLICY_SCAN.md",
        "n_trials": N_TRIALS,
        "grid": {"stock_w": STOCK_W, "bond_share": BOND_SHARE, "cash": CASH_W,
                 "rules": RULES, "n_weight_rows": nW,
                 "n_starts": int(len(starts)), "n_valid_starts": n_valid,
                 "n_short_starts": n_short,
                 "min_start_horizon_td": MIN_START_HORIZON},
        "faces": facts,
        "cost": {"face": "A", "per_side_bp": 13.041, "rt_bp": 26.082,
                 "source": "knowledge/cost_spec.py X1_RATE (imported)"},
        "closed_family": fam,
        "summary": {"n_grid_cells": len(grid_cells), "n_pass": n_pass,
                    "per_rule_total": per_rule,
                    "per_s_total": len(BOND_SHARE) * len(CASH_W) * len(RULES),
                    "per_c_total": len(STOCK_W) * len(BOND_SHARE) * len(RULES),
                    "pass_by_rule": by_rule, "pass_by_stock_w": by_s,
                    "pass_by_cash_w": by_c},
        "cells": cells,
    }
    if not write:
        return result
    os.makedirs(OUT_DIR, exist_ok=True)
    # r259 single-count law: legal re-execution of a void burn re-CARRIES the
    # existing ledger entry instead of appending again; the trials-ledger block
    # MUST live inside the batch results JSON (ledger_head is data-driven from
    # results files -- an entry left outside the JSON = chain-silent +N).
    scan_path = os.path.join(OUT_DIR, "scan.json")
    existing_tl = None
    if os.path.exists(scan_path):
        try:
            with open(scan_path, encoding="utf-8") as fh:
                old = json.load(fh)
            tl = old.get("trials_ledger") or {}
            if tl.get("batch") == BATCH:
                existing_tl = tl
        except Exception:
            existing_tl = None
    if existing_tl is not None:
        led = dict(existing_tl)
        led["reexec_single_count"] = True
        led["reexec_note"] = ("void-burn legal re-execution (engine cost-"
                              "multiplier bug fixed post first burn); ledger "
                              "+0 per r259 single-count law")
    else:
        led = sg.append_ledger(batch_name=BATCH, batch_trials=N_TRIALS,
                               file_name="results/allocation_policy_scan/scan.json",
                               evidence_cutoff=EVIDENCE_CUTOFF,
                               note="D-41 deliverable #2 full-grid publication "
                                    "scan (ORDER sec.5-2): 75 weights x 4 rules "
                                    "+ 2 baselines; no selection freedom")
    result["trials_ledger"] = led
    with open(scan_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    cols = ["cell_id", "s", "bond_share", "cash", "rule", "n_rebalances",
            "cost_drag_annual", "cagr", "vol", "sharpe", "t_info", "maxdd",
            "worst3y", "worst5y", "worst10y", "p_dd20_1y",
            "allstart_n_valid", "allstart_best", "allstart_worst",
            "allstart_p25", "allstart_median", "allstart_p75",
            "allstart_pos_share", "allstart_short", "pass"]
    pd.DataFrame([{k: c.get(k) for k in cols} for c in cells]) \
        .to_csv(os.path.join(OUT_DIR, "scan_cells.csv"), index=False)
    _write_summary(result)
    print(json.dumps({"batch": BATCH, "cutoff": EVIDENCE_CUTOFF,
                      "n_cells": len(cells), "n_pass": n_pass,
                      "by_rule": by_rule, "by_s": by_s, "by_c": by_c,
                      "ledger_total_after": led.get("total")},
                     ensure_ascii=False))
    return result


def _write_summary(result):
    s, f = result["summary"], result["faces"]
    lines = [
        f"# ALLOC-POLICY-SCAN-P1 扫描摘要（D-41 交付件#2）",
        "",
        f"- evidence_cutoff = **{result['evidence_cutoff']}**（锁盒；债/金孪生"
        f"末行=cutoff 日，6td 尾差披露见 prereg §2）",
        f"- 联合窗：{f['joint_start']} → {f['joint_end']}"
        f"（{f['n_days']} 交易日）·四腿=510300/511010/518880/GC001 现金腿",
        f"- 成本：ETF Face A 26.082bp/往返（cost_spec import）·现金腿零成本",
        f"- 格数：{s['n_grid_cells']} 网格 + 2 基线 = {result['n_trials']} 试验"
        f"（计入 RETAIL_QUANT_TRACK §四闸·全量公布零挑选）",
        f"- PASS 判据（prereg §4）：滚动 5 年最差年化>0 **且** 多数起点（≥50%）"
        f"全期 CAGR>0",
        "",
        "## 通过域分布（格级明细=scan_cells.csv）",
        "",
        "| 维度 | 通过分布 |",
        "|---|---|",
        "| 按再平衡规则 | " + " · ".join(
            f"{r}={s['pass_by_rule'][r]}/{s['per_rule_total']}" for r in RULES)
        + " |",
        "| 按股票权重 s | " + " · ".join(
            f"{x:.0%}={s['pass_by_stock_w'][x]}/{s['per_s_total']}"
            for x in STOCK_W) + " |",
        "| 按现金权重 c | " + " · ".join(
            f"{x:.0%}={s['pass_by_cash_w'][x]}/{s['per_c_total']}"
            for x in CASH_W) + " |",
        "",
        f"**总通过 {s['n_pass']}/{s['n_grid_cells']} 格。**",
        "",
        "## 基线对照",
        "",
        "| 基线 | CAGR | 滚动5年最差 | 1年内见-20%概率 | 最大回撤 |",
        "|---|---|---|---|---|",
    ]
    for c in result["cells"]:
        if c.get("baseline"):
            w5 = f"{c['worst5y']:+.2%}" if c["worst5y"] is not None else "N/A"
            lines.append(f"| {c['baseline']} | {c['cagr']:+.2%} | {w5} "
                         f"| {c['p_dd20_1y']:.1%} | {c['maxdd']:.1%} |")
    lines += [
        "",
        "## 诚实免责",
        "",
        "- as-traded 价格基（非全收益：股/债腿分红未计→股票腿实际回报被低估；"
        "金腿无分红；511010/518880 qfq 因子未考·纯价格面如实申报）；",
        "- 再平衡=同日收盘理想化执行近似（日历规则·历法先验无同日信息）；"
        "阈值5%=信号收盘 t、执行收盘 t+1（严格因果）；",
        "- GC001 现金腿=前收年化利率/365 单利近似；缺历日 ffill 计数见 scan.json",
        "- 本扫描=研究产出非投资建议；任何格晋升注册须另开预注册过全门"
        "（D6/M1/DSR/PBO）。",
        "",
        f"产物：results/allocation_policy_scan/scan.json + scan_cells.csv"
        f"（{len(result['cells'])} 行全指标）· 预注册：research/ALLOCATION_POLICY_SCAN.md",
    ]
    with open(os.path.join(OUT_DIR, "SUMMARY_20260930.md"), "w",
              encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def probe():
    _cost_check()
    dates, rets, facts = load_faces()
    fam = sg.closed_family_check(FAMILY_KEY)
    led = sg.ledger_head()
    print(json.dumps({
        "batch": BATCH, "evidence_cutoff": EVIDENCE_CUTOFF,
        "faces": {k: {"path": FACES[k]["path"], "first": facts[k]["first"],
                      "last": facts[k]["last"], "rows": facts[k]["rows"]}
                  for k in LEG_ORDER},
        "joint": {"start": facts["joint_start"], "end": facts["joint_end"],
                  "n_days": facts["n_days"],
                  "ffill_counts": facts["ffill_counts"]},
        "cost_per_side": COST_PER_SIDE,
        "closed_family": fam["status"],
        "ledger_head_total": led["total"],
        "n_trials_planned": N_TRIALS,
    }, ensure_ascii=False, indent=1))
    return 0


# ---------------------------------------------------------------- selftest --
def _naive_sim(rets, dates, target, rule):
    """Independent scalar reference simulator (selftest cross-check leg)."""
    n = rets.shape[0]
    entry = float((target * _etf_cost_leg_mask()).sum() * COST_PER_SIDE)
    V = 1.0 - entry
    w = target.copy()
    pending = False
    n_reb = 0
    cal = None if rule == "threshold5" else _calendar_mask(dates, rule)
    for t in range(n):
        if t > 0:
            pr = float((w * rets[t]).sum())
            V *= (1.0 + pr)
            w = w * (1.0 + rets[t]) / (1.0 + pr)
            do_exec = pending if rule == "threshold5" else bool(cal[t])
            if do_exec:
                cost = float((np.abs(target - w) * _etf_cost_leg_mask()).sum()
                             * COST_PER_SIDE)
                V *= (1.0 - cost)
                w = target.copy()
                n_reb += 1
            if rule == "threshold5":
                pending = bool(np.abs(w - target).max() >= THRESHOLD_BAND)
    return V, n_reb


def selftest():
    ok = 0

    def chk(name, cond):
        nonlocal ok
        if not cond:
            raise AssertionError(f"selftest FAIL: {name}")
        ok += 1
        print(f"  [ok] {name}")

    _cost_check()
    chk("S1 cost anchor X1_RATE==0.0013041 (Face A import, no hand-copy)",
        abs(COST_PER_SIDE - 0.0013041) < 1e-12)
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="aps_selftest_")
    try:
        dts = [d.strftime("%Y-%m-%d") for d in
               pd.bdate_range("2013-01-01", periods=70)]
        post = ["2026-09-25", "2026-09-26"]  # poison bars: post-cutoff, dropped
        daily_dir = os.path.join(tmp, "data", "daily")
        repo_dir = os.path.join(tmp, "data", "repo_daily")
        os.makedirs(daily_dir, exist_ok=True)
        os.makedirs(repo_dir, exist_ok=True)
        fname = {"stock": "sh510300.csv", "bond": "sh511010.csv",
                 "gold": "sh518880.csv"}
        for leg, drift in (("stock", 1.01), ("bond", 1.001), ("gold", 0.999)):
            rows = ["date,open,high,low,close,volume"]
            px = 100.0
            for d in dts:
                px *= drift
                rows.append(f"{d},{px:.6f},{px:.6f},{px:.6f},{px:.6f},1000")
            for d in post:
                px *= 2.0
                rows.append(f"{d},{px:.6f},{px:.6f},{px:.6f},{px:.6f},1000")
            with open(os.path.join(daily_dir, fname[leg]), "w") as fh:
                fh.write("\n".join(rows) + "\n")
        rows = ["date,open,high,low,close,volume"]
        for d in dts:
            rows.append(f"{d},1.5,1.5,1.5,1.5,100")
        for d in post:
            rows.append(f"{d},99,99,99,99,100")
        with open(os.path.join(repo_dir, "GC001.csv"), "w") as fh:
            fh.write("\n".join(rows) + "\n")
        saved = {k: dict(FACES[k]) for k in FACES}
        saved_start = JOINT_START
        try:
            for k in ("stock", "bond", "gold", "cash"):
                FACES[k]["first_bar"] = dts[0]
                FACES[k]["rows_freeze"] = 70
            globals()["JOINT_START"] = dts[0]
            dd, rr, ff = load_faces(faces_root=tmp, cutoff=dts[-1], min_days=70)
            chk("S2 load_faces truncates post-cutoff poison bars",
                ff["n_days"] == 70 and ff["stock"]["last"] == dts[-1])
            chk("S3 cash leg prior-bar accrual (1.5%/365 daily)",
                abs(rr[1, 3] - 1.5 / 36500.0) < 1e-15)
            tg = np.array([[0.40, 0.30, 0.20, 0.10]])
            for rule in ("annual", "quarterly", "monthly", "threshold5"):
                simM = simulate_with_dates(dd, rr, tg, np.zeros(1, dtype=int),
                                           rule, store_path=True)
                Vn, nreb = _naive_sim(rr, dd, tg[0], rule)
                chk(f"S4 matrix==naive reference ({rule})",
                    abs(simM["V"][0] - Vn) < 1e-10 and simM["n_reb"][0] == nreb)
            tg2 = np.array([[0.50, 0.50, 0.0, 0.0]])
            simT = simulate_with_dates(dd, rr, tg2, np.zeros(1, dtype=int),
                                       "threshold5", store_path=True)
            Vn2, _ = _naive_sim(rr, dd, tg2[0], "threshold5")
            chk("S5 threshold5 lagged execution == naive",
                abs(simT["V"][0] - Vn2) < 1e-10)
            # S6 hand-check: 2-day drift math with entry cost
            r1 = np.zeros((2, 4))
            r1[1] = [0.01, 0.0, 0.0, 1.5 / 36500.0]
            tg3 = np.array([[0.50, 0.50, 0.0, 0.0]])
            simD = simulate_with_dates(dd[:2], r1, tg3, np.zeros(1, dtype=int),
                                       "none", store_path=True)
            pr = 0.5 * 0.01 + 0.5 * 0.0 + 0.0 * 0.0 + 0.0 * (1.5 / 36500.0)
            chk("S6 drift math hand-check (V==(1-X1)*(1+pr))",
                abs(simD["V"][0] - (1.0 - COST_PER_SIDE) * (1.0 + pr)) < 1e-12)
            # S7 fresh-start entry cost at a mid-window start
            tg4 = np.array([[0.40, 0.30, 0.20, 0.10],
                            [0.40, 0.30, 0.20, 0.10]])
            simS = simulate_with_dates(dd, rr, tg4, np.array([0, 5]),
                                       "monthly", store_path=True)
            ec = (0.4 + 0.3 + 0.2) * COST_PER_SIDE
            chk("S7 fresh-start entry cost (V[start]=1-ETFlegs*X1)",
                abs(simS["path"][1, 5] - (1.0 - ec)) < 1e-12)
            # S8 baseline B&H closed form
            simB = simulate_with_dates(dd, rr, np.array([[1.0, 0.0, 0.0, 0.0]]),
                                      np.zeros(1, dtype=int), "none",
                                      store_path=True)
            prod = 1.0
            for t in range(1, len(dd)):
                prod *= 1.0 + rr[t, 0]
            chk("S8 stock_bh == (1-X1)*prod(1+r)",
                abs(simB["V"][0] - (1.0 - COST_PER_SIDE) * prod) < 1e-10)
            # S9 rolling worst5y on constructed path
            v = np.ones(1260)
            v[630:] = 0.8
            m = _path_metrics(v)
            expect = 0.8 ** (252.0 / 1250.0) - 1.0
            chk("S9 worst5y on constructed path", abs(m["worst5y"] - expect) < 1e-9)
            v2 = np.ones(400)
            v2[100:140] = np.linspace(1.0, 0.72, 40)
            m2 = _path_metrics(v2)
            chk("S10 p_dd20 detects -20%-class crash", m2["p_dd20_1y"] > 0)
            # S11 determinism double-run
            w75, _ = _grid_weights()
            sA = simulate_with_dates(dd, rr, w75, np.zeros(len(w75), dtype=int),
                                     "monthly", store_path=True)
            sA2 = simulate_with_dates(dd, rr, w75, np.zeros(len(w75), dtype=int),
                                      "monthly", store_path=True)
            chk("S11 determinism double-run identical",
                np.array_equal(sA["V"], sA2["V"])
                and np.array_equal(sA["path"], sA2["path"]))
            # S12 face-mismatch anchor gate refuses
            FACES["gold"]["first_bar"] = "1999-01-01"
            try:
                load_faces(faces_root=tmp, cutoff=dts[-1], min_days=70)
                raised = False
            except ValueError:
                raised = True
            chk("S12 face-mismatch anchor gate refuses (fail-closed)", raised)
            # S13 hand-value rebalance cost leg (cost-multiplier bug guard:
            # twin-equality S4 cannot catch a shared-bug -- this leg asserts
            # the literal per-side rate multiplies the ETF-leg weight delta)
            d3 = ["2013-01-31", "2013-02-01", "2013-02-04"]
            r3 = np.zeros((3, 4))
            r3[1] = [0.02, 0.0, 0.0, 0.0]
            tg5 = np.array([[0.50, 0.50, 0.0, 0.0]])
            sim13 = simulate_with_dates(d3, r3, tg5, np.zeros(1, dtype=int),
                                        "monthly", store_path=True)
            pr13 = 0.5 * 0.02
            dw13 = 2 * (0.5 * 1.02 / (1 + pr13) - 0.5)
            cost13 = dw13 * COST_PER_SIDE
            v13 = (1.0 - COST_PER_SIDE) * (1 + pr13) * (1 - cost13)
            chk("S13 rebalance cost == hand value (X1 multiplies |dw|)",
                abs(sim13["V"][0] - v13) < 1e-14
                and abs(sim13["tot_cost"][0] - cost13) < 1e-16
                and sim13["n_reb"][0] == 1)
        finally:
            for k in FACES:
                FACES[k] = saved[k]
            globals()["JOINT_START"] = saved_start
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"selftest: {ok}/{ok} PASS")
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "probe":
        return probe()
    if cmd == "run":
        run()
        return 0
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
