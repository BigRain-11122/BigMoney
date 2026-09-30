"""D-20260930-41 deliverable #1 -- cross-start + rolling-window robustness
adjudication (CROSS-START-ROBUSTNESS-P1, bm-c berth r284).

Adjudicates the ORDER's two standing retail conclusions across start points
and rolling windows ("majority of starts hold -> keep, else withdraw"):

  Face A (burned this batch): four-asset allocation conclusion
      (claim anchor 5.87%/-14.4%/71%, regime-adaptive external config).
      In-repo face = equal-weight 25x4 monthly rebalance (near-kin, no
      replication obligation per EXCLUSION_MARGINAL precedent) + 3 seeded
      random static-weight null cells. Engine = 100% imported from
      scripts/allocation_policy_scan (load_faces/simulate/_path_metrics),
      zero rewrite per anti-dup law.
  Face B (STAGED, zero burns): low-volume stock-selection conclusion
      (14.80%/8-10y single-start defect named by the ORDER). Canonical
      baseline definition frozen in prereg sec.3-B, shared with bm-b #3
      EXCLUSION-MARGINAL; burn waits for that engine to land (import reuse,
      no second engine).

Prereg (frozen pre-burn) = research/CROSS_START_ROBUSTNESS.md.
Laws carried: G-ANCHOR-FACE four-tuples (inherited via load_faces fail-closed),
R99 freeze-before-burn, CN-C7 cost import (no hand-copy), M1 informational t,
M3 closed-family gate, trial gate <=500/30d (RETAIL_QUANT_TRACK sec.4),
evidence_cutoff=2026-09-22 (same lockbox as ALLOC-POLICY-SCAN-P1).

Usage (module mode, cwd = repo root):
    python -m scripts.cross_start_robustness probe      # anchors + gates
    python -m scripts.cross_start_robustness run        # face A burn
    python -m scripts.cross_start_robustness selftest   # hermetic
Direct run also works (repo-root sys.path fix mirrors allocation_policy_scan).
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

try:
    from scripts import science_gates as sg
    from scripts import allocation_policy_scan as aps
except ImportError:
    import science_gates as sg
    import allocation_policy_scan as aps

BATCH = "CROSS-START-ROBUSTNESS-P1"
EVIDENCE_CUTOFF = "2026-09-22"        # same lockbox as ALLOC-POLICY-SCAN-P1
OUT_DIR = os.path.join(_REPO_ROOT, "results", "cross_start_robustness")
FAMILY_KEY = "cross-start-robustness"
SEED_KEY = "cross_start_robustness_p1"
N_RAND_CELLS = 3
N_TRIALS = 1 + N_RAND_CELLS          # A-EQW + A-RAND x3 (face B staged +2 later)
KIN_FILE = os.path.join(_REPO_ROOT, "results", "allocation_policy_scan",
                        "scan.json")
KIN_CELL_IDS = ["0.30|0.50|0.20|monthly", "0.20|0.50|0.20|monthly"]
WIN_1Y_WINDOW = 252

# ORDER conclusion A claim anchors (external regime-adaptive config) --
# reference-only comparison anchors, never gates (prereg sec.4).
CLAIM_A = {"cagr": 0.0587, "maxdd": -0.144, "win_rate": 0.71,
           "source": "ORDER conclusion A: regime-adaptive four-asset, "
                     "external config not in repo"}


def _rand_targets():
    """Seeded random static weights (prereg sec.3-A): default_rng(base+k)
    .dirichlet(ones(4)), k=0..N_RAND_CELLS-1. Deterministic, sum=1."""
    base = int(sg.SEED_REGISTRY[SEED_KEY])
    rows = []
    for k in range(N_RAND_CELLS):
        rng = np.random.default_rng(base + k)
        w = rng.dirichlet(np.ones(4))
        assert abs(float(w.sum()) - 1.0) < 1e-12 and (w > 0).all()
        rows.append(w)
    return np.array(rows)


def _targets():
    eqw = np.array([[0.25, 0.25, 0.25, 0.25]])
    rand = _rand_targets()
    return np.vstack([eqw, rand]), ["A-EQW"] + \
        [f"A-RAND-{k+1}" for k in range(N_RAND_CELLS)]


def _win_metrics(path, starts):
    """Frozen win-rate readouts (prereg sec.3-A):
    win_1y_pos_share = share of rolling 252td windows with positive total
    return (daily step, log-diff); win_month_pos_share = share of positive
    complete month slices between consecutive month-first boundaries (tail
    partial month excluded; first slice starts at window head, disclosed)."""
    v = np.asarray(path, dtype=float)
    out = {"win_1y_pos_share": None, "win_month_pos_share": None,
           "n_1y_windows": 0, "n_month_slices": 0}
    if len(v) > WIN_1Y_WINDOW:
        logv = np.log(v)
        d = logv[WIN_1Y_WINDOW:] - logv[:-WIN_1Y_WINDOW]
        out["win_1y_pos_share"] = float((d > 0).mean())
        out["n_1y_windows"] = int(len(d))
    starts = np.asarray(starts)
    if len(starts) >= 2:
        seg = v[starts[1:]] / v[starts[:-1]] - 1.0
        out["win_month_pos_share"] = float((seg > 0).mean())
        out["n_month_slices"] = int(len(seg))
    return out


def _allstart_stats(dates, rets, targets, rule="monthly"):
    """Fresh-entry all-start grid (prereg sec.3-A). Start grid = monthly
    first trading days (same grid/horizon gate as #2); ENTRY SEMANTICS =
    clean sliced entry: each start enters at slice t=0 (engine sliced state
    is twin-verified vs the aps naive reference at 1e-12), because the
    engine's in-window fresh-entry leg drifts weights on the entry day
    without crediting V (measured perturbation = entry-day portfolio
    return, ~1e-3 relative; disclosed in prereg changelog + summary).
    Headline stats over starts with horizon >= aps.MIN_START_HORIZON."""
    starts = aps._monthly_start_idx(dates)
    n = rets.shape[0]
    horizon_days = (n - 1) - starts
    valid = horizon_days >= aps.MIN_START_HORIZON
    n_valid, n_short = int(valid.sum()), int((~valid).sum())
    R = targets.shape[0]
    zero = np.zeros(R, dtype=int)
    finals = np.empty((len(starts), R), dtype=float)
    for j, s in enumerate(starts):
        if horizon_days[j] <= 0:
            finals[j] = np.nan
            continue
        sim = aps.simulate_with_dates(dates[s:], rets[s:], targets, zero,
                                      rule, store_path=False)
        finals[j] = sim["V"]
    per_row = []
    for i in range(R):
        with np.errstate(divide="ignore", invalid="ignore"):
            cagrs = finals[:, i] ** (252.0 / horizon_days) - 1.0
        head = cagrs[valid & (horizon_days > 0)]
        per_row.append({
            "allstart_n_valid": n_valid, "allstart_short": n_short,
            "allstart_best": float(head.max()),
            "allstart_worst": float(head.min()),
            "allstart_p25": float(np.percentile(head, 25)),
            "allstart_median": float(np.percentile(head, 50)),
            "allstart_p75": float(np.percentile(head, 75)),
            "allstart_pos_share": float((head > 0).mean()),
        })
    return per_row, n_valid, n_short, int(len(starts))


def _adjudicate(cell):
    """Frozen PASS criteria (prereg sec.4, three-way conjunction):
    allstart_pos_share >= 0.50 AND allstart_median_cagr > 0 AND worst5y > 0."""
    ok_pos = cell["allstart_pos_share"] is not None \
        and cell["allstart_pos_share"] >= 0.50
    ok_med = cell["allstart_median"] is not None and cell["allstart_median"] > 0
    ok_w5 = cell["worst5y"] is not None and cell["worst5y"] > 0
    return {"pos_share_ok": bool(ok_pos), "median_ok": bool(ok_med),
            "worst5y_ok": bool(ok_w5), "pass": bool(ok_pos and ok_med and ok_w5)}


def _kin_context():
    """Read-only context from the burned #2 scan (zero new trials):
    pure-stock/pure-cash baselines + nearest-kin monthly cells."""
    with open(KIN_FILE, encoding="utf-8") as fh:
        scan = json.load(fh)
    kin = {"baselines": {}, "nearest_kin_cells": {}}
    for c in scan["cells"]:
        if c.get("baseline"):
            kin["baselines"][c["baseline"]] = {
                k: c.get(k) for k in ("cagr", "maxdd", "worst5y")}
        elif c["cell_id"] in KIN_CELL_IDS:
            kin["nearest_kin_cells"][c["cell_id"]] = {
                k: c.get(k) for k in ("w", "cagr", "maxdd", "worst5y",
                                      "allstart_median", "allstart_pos_share",
                                      "allstart_best", "allstart_worst")}
    kin["source"] = "results/allocation_policy_scan/scan.json (bm-b r474, +0 trials)"
    kin["nearest_kin_note"] = ("0.30|0.50|0.20|monthly = closest grid cell to "
                               "equal-weight in weight space (L1 dist 0.12)")
    return kin


def run(write=True):
    aps._cost_check()
    if aps.EVIDENCE_CUTOFF != EVIDENCE_CUTOFF:
        raise RuntimeError("cutoff drift vs #2 face (same-lockbox law)")
    fam = sg.closed_family_check(FAMILY_KEY)
    if fam.get("status") != "open":
        raise RuntimeError(f"closed-family gate: {fam}")
    dates, rets, facts = aps.load_faces()
    if SEED_KEY not in sg.SEED_REGISTRY:
        raise RuntimeError("seed base not registered (prereg sec.3-A law)")
    targets, cell_ids = _targets()
    R = targets.shape[0]

    # pass A: headline rows with full paths
    simA = aps.simulate_with_dates(dates, rets, targets,
                                  np.zeros(R, dtype=int), "monthly",
                                  store_path=True)
    # pass B: all-start fresh-entry grid
    allstart_rows, n_valid, n_short, n_starts = _allstart_stats(
        dates, rets, targets, "monthly")
    starts = aps._monthly_start_idx(dates)
    n = rets.shape[0]

    cells = []
    for i, cid in enumerate(cell_ids):
        m = aps._path_metrics(simA["path"][i])
        c = {"cell_id": cid, "rule": "monthly",
             "w": [round(float(x), 6) for x in targets[i]],
             "n_rebalances": int(simA["n_reb"][i]),
             "cost_drag_annual": float(simA["tot_cost"][i] * 252.0 / (n - 1)),
             "t_face": "informational t_from_sharpe (M1 declared non-gating)",
             }
        if cid == "A-EQW":
            c["seed"] = None
        else:
            c["seed"] = int(sg.SEED_REGISTRY[SEED_KEY]) + int(cid[-1]) - 1
        c.update(m)
        c.update(_win_metrics(simA["path"][i], starts))
        c.update(allstart_rows[i])
        c.update(_adjudicate(c))
        cells.append(c)

    eqw = cells[0]
    verdict_a = {
        "claim_anchor": dict(CLAIM_A),
        "inrepo_face": "equal-weight 25x4 monthly four-asset (near-kin; "
                       "no replication obligation per prereg sec.1.2)",
        "verdict_cell": "A-EQW",
        "criteria": "allstart_pos_share>=0.50 AND allstart_median_cagr>0 "
                    "AND worst5y_cagr>0 (prereg sec.4, frozen pre-burn)",
        "criteria_reads": eqw,
        "verdict": "retained" if eqw["pass"] else "withdrawn",
        "note": "ORDER wording: majority of starts hold -> keep, else "
                "withdraw. Claimed numbers are external-config reads, "
                "compared not gated.",
    }
    rand_pass = sum(1 for c in cells if c["cell_id"] != "A-EQW" and c["pass"])

    result = {
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "science_gates": {"cutoff_meta": sg.cutoff_meta(EVIDENCE_CUTOFF)},
        "batch": BATCH,
        "prereg": "research/CROSS_START_ROBUSTNESS.md",
        "n_trials": N_TRIALS,
        "family": {"key": FAMILY_KEY, "status": fam["status"]},
        "faces": facts,
        "cost": {"face": "A", "per_side_bp": 13.041, "rt_bp": 26.082,
                 "source": "knowledge/cost_spec.py X1_RATE (imported)"},
        "grid": {"cells": cell_ids, "rule": "monthly",
                 "n_starts": n_starts, "n_valid_starts": n_valid,
                 "n_short_starts": n_short,
                 "min_start_horizon_td": aps.MIN_START_HORIZON,
                 "rand_seed_base": int(sg.SEED_REGISTRY[SEED_KEY]),
                 "rand_procedure": "default_rng(base+k).dirichlet(ones(4))"},
        "face_B_staged": {
            "status": "STAGED zero burns this batch",
            "baseline": "amt20_mean asc top-10 monthly equal-weight T+1, "
                        "16 Jan-firsts 2007..2022, V2 stock costs",
            "engine_plan": "import bm-b EXCLUSION-MARGINAL engine when it "
                           "lands (anti-dup; MSG-1947 sec.2)",
            "planned_trials": 2,
        },
        "conclusion_A": verdict_a,
        "rand_null_pass_count": rand_pass,
        "kin_context": _kin_context(),
        "cells": cells,
    }
    if not write:
        return result

    os.makedirs(OUT_DIR, exist_ok=True)
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
        led["reexec_note"] = ("deterministic-engine legal re-execution; "
                              "ledger +0 per r259 single-count law")
    else:
        led = sg.append_ledger(
            batch_name=BATCH, batch_trials=N_TRIALS,
            file_name="results/cross_start_robustness/scan.json",
            evidence_cutoff=EVIDENCE_CUTOFF,
            note="D-41 deliverable #1 cross-start robustness adjudication "
                 "face A: equal-weight 25x4 monthly + 3 seeded random "
                 "static-weight nulls; conclusion adjudication not a "
                 "selection search")
    result["trials_ledger"] = led
    with open(scan_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    cols = ["cell_id", "rule", "w", "seed", "n_rebalances", "cost_drag_annual",
            "cagr", "vol", "sharpe", "t_info", "maxdd", "worst3y", "worst5y",
            "worst10y", "p_dd20_1y", "win_1y_pos_share", "win_month_pos_share",
            "n_1y_windows", "n_month_slices", "allstart_n_valid",
            "allstart_best", "allstart_worst", "allstart_p25",
            "allstart_median", "allstart_p75", "allstart_pos_share",
            "allstart_short", "pos_share_ok", "median_ok", "worst5y_ok",
            "pass"]
    import pandas as pd
    pd.DataFrame([{k: c.get(k) for k in cols} for c in cells]) \
        .to_csv(os.path.join(OUT_DIR, "cells.csv"), index=False)
    _write_summary(result)
    print(json.dumps({
        "batch": BATCH, "cutoff": EVIDENCE_CUTOFF,
        "conclusion_A_verdict": verdict_a["verdict"],
        "eqw": {k: eqw[k] for k in ("cagr", "maxdd", "win_1y_pos_share",
                                    "allstart_pos_share",
                                    "allstart_median", "worst5y", "pass")},
        "rand_null_pass": f"{rand_pass}/{N_RAND_CELLS}",
        "ledger_total_after": led.get("total"),
    }, ensure_ascii=False))
    return result


def _write_summary(result):
    va, f, kin = result["conclusion_A"], result["faces"], result["kin_context"]
    eqw = next(c for c in result["cells"] if c["cell_id"] == "A-EQW")
    bl = kin["baselines"]
    lines = [
        f"# CROSS-START-ROBUSTNESS-P1 裁定摘要（D-41 交付件#1·Face A）",
        "",
        f"- **结论A裁定：{('保留' if va['verdict'] == 'retained' else '撤回')}"
        f"**（判据：多数起点正份额≥50% ∩ 起点中位>0 ∩ 滚动5年最差>0——跑前冻结）",
        f"- evidence_cutoff = **{result['evidence_cutoff']}**（与 #2 同锁盒；"
        f"债/金孪生末行=cutoff 日，6td 尾差披露）·联合窗 {f['joint_start']}"
        f" → {f['joint_end']}（{f['n_days']} 交易日）",
        f"- 本仓面=等权 25×4 月频（政体自适应版=外部配置不在仓，无复现义务——"
        f"近亲面裁定，读数对照不裁断）",
        "",
        "## A-EQW vs 令文锚（对照不裁断）",
        "",
        "| 面 | 年化 | 最大回撤 | 胜率类读数 |",
        "|---|---|---|---|",
        f"| 令文结论A（外部政体自适应） | 5.87% | −14.4% | 71%（原口径未注） |",
        f"| 本仓面 A-EQW 等权月频 | {eqw['cagr']:+.2%} | {eqw['maxdd']:.1%} "
        f"| 1年滚动窗正占比 {eqw['win_1y_pos_share']:.1%} / 月切片正占比 "
        f"{eqw['win_month_pos_share']:.1%} |",
        "",
        "## 全起点分布（§1.3 必填面·新鲜入场独立模拟）",
        "",
        f"- 月度起点 {result['grid']['n_starts']} 个（≥3 年 horizon 入 "
        f"headline {result['grid']['n_valid_starts']} 个，短 horizon "
        f"{result['grid']['n_short_starts']} 个如实披露）",
        f"- A-EQW：最好 {eqw['allstart_best']:+.2%} / p75 "
        f"{eqw['allstart_p75']:+.2%} / 中位 {eqw['allstart_median']:+.2%} / "
        f"p25 {eqw['allstart_p25']:+.2%} / 最坏 {eqw['allstart_worst']:+.2%}"
        f" / 正份额 {eqw['allstart_pos_share']:.1%}",
        f"- 滚动窗最差：3年 {eqw['worst3y']:+.2%} / 5年 {eqw['worst5y']:+.2%}"
        f" / 10年 {eqw['worst10y']:+.2%}（10y 窗起点跨度薄样本如实注记）",
        f"- 一年内见 −20% 概率：{eqw['p_dd20_1y']:.1%}"
        f"（#2 纯股基线 38.5% 对照）",
        "",
        "## 随机静态权重 null 族（seeded·公布不设线）",
        "",
        "| 格 | 权重 | 年化 | 起点中位 | 正份额 | PASS |",
        "|---|---|---|---|---|---|",
    ]
    for c in result["cells"]:
        if c["cell_id"] == "A-EQW":
            continue
        lines.append(f"| {c['cell_id']} | {c['w']} | {c['cagr']:+.2%} "
                      f"| {c['allstart_median']:+.2%} "
                      f"| {c['allstart_pos_share']:.1%} "
                      f"| {'PASS' if c['pass'] else 'FAIL'} |")
    lines += [
        f"| （A-EQW 等权） | [0.25, 0.25, 0.25, 0.25] | {eqw['cagr']:+.2%} "
        f"| {eqw['allstart_median']:+.2%} | {eqw['allstart_pos_share']:.1%} "
        f"| {'PASS' if eqw['pass'] else 'FAIL'} |",
        "",
        f"随机 null 通过 {result['rand_null_pass_count']}/{N_RAND_CELLS}"
        f"——若随机混合亦多数通过=配置稳健性主体由分散承载的证据面"
        f"（等权无特权主张，如实对照）。",
        "",
        "## kin-context（#2 已烧面只读引用·+0 试验）",
        "",
        f"- 纯股 B&H：CAGR {bl['stock_bh']['cagr']:+.2%} / maxdd "
        f"{bl['stock_bh']['maxdd']:.1%}；纯现金：{bl['cash_only']['cagr']:+.2%}",
        f"- 最近邻格 {KIN_CELL_IDS[0]}：起点中位 "
        f"{kin['nearest_kin_cells'][KIN_CELL_IDS[0]]['allstart_median']:+.2%}"
        f" / 正份额 "
        f"{kin['nearest_kin_cells'][KIN_CELL_IDS[0]]['allstart_pos_share']:.1%}",
        "",
        "## Face B（低量选股结论）分级暂缓",
        "",
        "- 基线定义已冻结共享（20 日均额升序 10 只月频等权 T+1·2007..2022 "
        "16 起点·V2 成本）——烧批待 bm-b #3 排除引擎落地后 import 复用"
        "（防双引擎）；届时 +2 试验另行归因。",
        "",
        "## 诚实免责",
        "",
        "- as-traded 价格基（非全收益：股/债腿分红未计→实际回报被低估；"
        "金腿无分红）；再平衡=同日收盘理想化执行近似（日历规则历法先验）；",
        "- GC001 现金腿=前收年化利率/365 单利近似；首月切片自窗首 2013-07-29 "
        "起为残月（计入并披露）；",
        "- 本裁定=研究产出非投资建议；令文数字为外部配置读数（窗巧合与口径差"
        "异如实披露）；任何格晋升注册须另开预注册过全门（D6/M1/DSR/PBO）。",
        "",
        f"产物：results/cross_start_robustness/scan.json + cells.csv"
        f"（{len(result['cells'])} 行全指标）· 预注册："
        f"research/CROSS_START_ROBUSTNESS.md",
    ]
    with open(os.path.join(OUT_DIR, "SUMMARY_20260930.md"), "w",
              encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def probe():
    aps._cost_check()
    if SEED_KEY not in sg.SEED_REGISTRY:
        raise RuntimeError("seed base not registered")
    dates, rets, facts = aps.load_faces()
    fam = sg.closed_family_check(FAMILY_KEY)
    led = sg.ledger_head()
    kin_ok = os.path.exists(KIN_FILE)
    targets, cell_ids = _targets()
    print(json.dumps({
        "batch": BATCH, "evidence_cutoff": EVIDENCE_CUTOFF,
        "faces": {k: {"path": aps.FACES[k]["path"],
                      "first": facts[k]["first"], "last": facts[k]["last"],
                      "rows": facts[k]["rows"]} for k in aps.LEG_ORDER},
        "joint": {"start": facts["joint_start"], "end": facts["joint_end"],
                  "n_days": facts["n_days"],
                  "ffill_counts": facts["ffill_counts"]},
        "cost_per_side": aps.COST_PER_SIDE,
        "closed_family": fam["status"],
        "seed_base": int(sg.SEED_REGISTRY[SEED_KEY]),
        "rand_cells": [f"{cid}: w={[round(float(x), 6) for x in targets[i]]}"
                       for i, cid in enumerate(cell_ids)],
        "kin_file_present": kin_ok,
        "ledger_head_total": led["total"],
        "n_trials_planned": N_TRIALS,
        "face_B_staged": True,
    }, ensure_ascii=False, indent=1))
    return 0


# ---------------------------------------------------------------- selftest --
def selftest():
    ok = 0

    def chk(name, cond):
        nonlocal ok
        if not cond:
            raise AssertionError(f"selftest FAIL: {name}")
        ok += 1
        print(f"  [ok] {name}")

    # S1: cost anchor import (CN-C7, no hand-copy)
    aps._cost_check()
    chk("S1 cost anchor X1_RATE==0.0013041 (import chain)",
        abs(aps.COST_PER_SIDE - 0.0013041) < 1e-12)
    # S2: EQW target exact + RAND determinism/sum/positivity/distinctness
    targets, cell_ids = _targets()
    chk("S2a EQW target == [0.25]*4",
        np.allclose(targets[0], [0.25] * 4) and cell_ids[0] == "A-EQW")
    t2 = _rand_targets()
    chk("S2b RAND determinism (double-derive identical)",
        np.array_equal(targets[1:], t2))
    chk("S2c RAND rows sum=1, positive, pairwise distinct",
        np.allclose(t2.sum(axis=1), 1.0) and (t2 > 0).all()
        and not np.allclose(t2[0], t2[1]) and not np.allclose(t2[0], t2[2]))
    # S3: win_1y_pos_share on constructed paths (monotone up -> 1.0, down -> 0.0)
    starts_3 = np.array([0, 21, 42, 63])
    up = 1.0 + 0.001 * np.arange(600)
    down = 1.0 - 0.0004 * np.arange(600)
    m_up = _win_metrics(up, starts_3)
    m_dn = _win_metrics(down, starts_3)
    chk("S3 win_1y_pos_share monotone up==1.0 / down==0.0 "
        f"(windows {m_up['n_1y_windows']})",
        m_up["win_1y_pos_share"] == 1.0 and m_dn["win_1y_pos_share"] == 0.0
        and m_up["n_1y_windows"] == 600 - WIN_1Y_WINDOW)
    # S4: win_month_pos_share hand-check (rise/rise/fall -> 2/3)
    p = np.ones(64)
    p[21:42] = np.linspace(1.0, 1.10, 21)      # month 2 up
    p[42:63] = np.linspace(1.10, 1.05, 21)    # month 3 down
    m4 = _win_metrics(p, starts_3)
    # slices: [0,21) flat=0 -> not positive; [21,42) up -> positive;
    # [42,63) down -> negative => 1/3 positive
    chk("S4 win_month_pos_share hand-check == 1/3",
        abs(m4["win_month_pos_share"] - 1.0 / 3.0) < 1e-12
        and m4["n_month_slices"] == 3)
    # S5: fresh-entry engine math at a mid-window start (twin-check vs the
    # validated aps naive reference on the sliced window, rule="none")
    import pandas as pd
    rng = np.random.default_rng(7)
    dts = [d.strftime("%Y-%m-%d") for d in
           pd.bdate_range("2020-01-01", periods=700)]
    rets5 = rng.normal(0.0005, 0.01, size=(700, 4))
    tg = np.array([[0.25] * 4])
    s = 250
    sim5s = aps.simulate_with_dates(dts[s:], rets5[s:], tg,
                                    np.zeros(1, dtype=int), "none",
                                    store_path=True)
    entry = 0.75 * aps.COST_PER_SIDE
    chk("S5a fresh-entry V[0]==1-entry_cost(ETF legs)",
        abs(sim5s["path"][0, 0] - (1.0 - entry)) < 1e-12)
    v_naive, n_reb = aps._naive_sim(rets5[s:], dts[s:], tg[0], "none")
    chk("S5b sliced clean entry == aps naive reference (rule none)",
        abs(sim5s["V"][0] - v_naive) < 1e-10 and sim5s["n_reb"][0] == 0)
    sim5f = aps.simulate_with_dates(dts, rets5, tg, np.array([s]), "none",
                                    store_path=False)
    chk("S5c engine in-window fresh-entry perturbation documented "
        "(entry-day weight drift; clean sliced entry adopted for all-starts)",
        abs(sim5f["V"][0] - sim5s["V"][0]) > 1e-9)
    # S6: adjudication truth table
    base = {"allstart_pos_share": None, "allstart_median": None,
            "worst5y": None}
    c1 = dict(base, allstart_pos_share=0.60, allstart_median=0.03,
              worst5y=0.01)
    c2 = dict(base, allstart_pos_share=0.49, allstart_median=0.03,
              worst5y=0.01)
    c3 = dict(base, allstart_pos_share=0.60, allstart_median=-0.01,
              worst5y=0.01)
    c4 = dict(base, allstart_pos_share=0.60, allstart_median=0.03,
              worst5y=-0.005)
    c5 = dict(base, allstart_pos_share=0.60, allstart_median=0.03,
              worst5y=None)
    chk("S6 adjudication truth table (3-way conjunction, None fails)",
        _adjudicate(c1)["pass"] and not _adjudicate(c2)["pass"]
        and not _adjudicate(c3)["pass"] and not _adjudicate(c4)["pass"]
        and not _adjudicate(c5)["pass"])
    # S7: t_from_sharpe consistency with _path_metrics informational t
    v = np.cumprod(1.0 + rng.normal(0.0004, 0.008, size=1000))
    m7 = aps._path_metrics(v)
    chk("S7 t_info == t_from_sharpe (M1 informational face)",
        abs(m7["t_info"] - sg.t_from_sharpe(m7["sharpe"], 999)) < 1e-9)
    # S8: kin-context extraction from committed #2 fixture
    kin = _kin_context()
    chk("S8 kin-context baselines + nearest-kin cells extracted",
        "stock_bh" in kin["baselines"] and "cash_only" in kin["baselines"]
        and KIN_CELL_IDS[0] in kin["nearest_kin_cells"])
    # S9: determinism double-run (write=False) on real faces, byte-identical
    r1 = run(write=False)
    r2 = run(write=False)
    chk("S9 determinism double-run identical",
        json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True))
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
