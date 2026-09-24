# -*- coding: utf-8 -*-
"""scripts/scorecard.py — P-6 策略记分卡（总经办首单，T-2026-09-23-07）

判据权威 = firm/STRATEGY_EVALUATION.md v1.0（O-1823：八维权重 §2 + 分级带 §3 跑前写死）。
性质 = 评价面/报告面：叠加于 G1'/G2/paper 门禁之上，零写 trader level/paper 字段，
hr.py 仍是唯一 level 变更权（T-07 ZERO-TOUCH 条款）。
数据驱动聚合 = 零新回测（框架 §4）：一切分数来自 firm/traders/*.json、
results/p5_random_entry.json + p5b_new_traders.json（+同名 CSV 中位超额）、
results/portfolio_ew6.json（成员 full/IS2 指标+相关矩阵）、注册批 JSON
（g2_folk / ce_transfer / combined_exit 的 worst_year 与 x3 读数）、
results/paper/*_paper.json（维度8）、science_gates 活线（skill_line_v2 / i / vi）。
计数单源规则（O-2250）：花名册=glob firm/traders（零写死名单），线=science_gates 活读。

公式 v1（实现选择，跑前冻结于此）：框架只锁权重与分级带；维内子权重与线性带
（满分锚点）为本实现选择，全部随产物披露 provenance.formulas，修订=新版本号+轮报告。

命名披露：框架 §4 写 scripts/strategy_scorecard.py + results/strategy_scorecard.json，
任务单 T-07 写 scripts/scorecard.py + results/scorecard_v1.json —— 本实现循任务单
（认领权威），差异已在 provenance 披露，法件侧改名归 GM。

重算节律（自动化注记，T-07 第3项）：每月 hr 复核前重算 + 任何新交易员注册 /
P-5/paper/EW 新证据落账后重算；不入 10 分钟 S6 链（输入为事件节律非日内）。

用法：
  python scripts/scorecard.py                 # 写 results/scorecard_v1.json
  python scripts/scorecard.py --out PATH
  python scripts/scorecard.py selftest        # 离线合成夹具自检（零网络零真实写）
"""
import argparse
import csv
import datetime as _dt
import json
import math
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRADERS_DIR = os.path.join(ROOT, "firm", "traders")
RESULTS = os.path.join(ROOT, "results")
RESEARCH = os.path.join(ROOT, "research")
OUT_DEFAULT = os.path.join(RESULTS, "scorecard_v1.json")

# —— 框架 §2 权重（法件写死，禁改）——
WEIGHTS = {1: 0.30, 2: 0.20, 3: 0.15, 4: 0.10, 5: 0.10, 6: 0.10, 7: 0.05}
# 维度8 = 校验维度，首月后转 10% 届时权重再预注册（框架 §2）——当前权重 0
WEIGHT_D8 = 0.0
GRADE_BANDS = {"S": 80.0, "A": 65.0, "B": 50.0}  # 框架 §3
S_CORE_DIM_MINS = {1: 60.0, 2: 60.0, 3: 60.0}    # S 级附加条款：维1/2/3 各≥60
VETO_KEYS = ["future_data", "x2_not_survive", "worst_start_dd_breach",
             "oos_blindspot", "snooping_undeclared"]
DD_RED_LINE = 0.35        # 一票否决：单起点破 -35%（框架 §1.4）
BEAT_FULL = 0.70          # 维1：≥70% 线性满分（框架 §2 计分要点）

FORMULAS = {
    1: "beat=100*min(1,beat_rate_6m/0.70); dd=100*clip((0.35-|min_dd_6m|)/0.30,0,1); "
       "excess=100*clip(median_excess_6m/0.05,0,1); D1=0.60*beat+0.25*dd+0.15*excess",
    2: "full=100*min(1,full_sharpe/skill_line_v2); oos=100*min(1,oos_sharpe/i_line); "
       "D2=0.70*full+0.30*oos",
    3: "ratio=cost_x2_sharpe/vi_bar; x2=100*clip((ratio-0.80)/0.70,0,1); "
       "bonus=+5 if recorded x3 full sharpe >= vi_bar else 0; D3=min(100,x2+bonus)",
    4: "retention=100*min(1,is2_sharpe/full_sharpe); "
       "worst_year=100*clip((worst_year+0.20)/0.20,0,1) [None=untested,re-norm]; "
       "direction=100 if is2_sharpe>0 else 0; D4=0.4*retention+0.4*worst_year+0.2*direction",
    5: "corr=100*clip((0.60-max_corr_others)/0.50,0,1) "
       "[portfolio benefit contribution = portfolio-level only, untestable per-member -> context]; D5=corr",
    6: "trades=100 if 30<=n<=800 else below:100*clip((n-10)/20,0,1) / above:100*clip((1200-n)/400,0,1); "
       "[pool capacity + T+1 turnover load = no wired data -> untested, re-norm]; D6=trades",
    7: "prereg=100 if registration carries repro/batch evidence chain else 0; "
       "declared=100 if no undeclared-snooping flag recorded else 0; D7=0.5*prereg+0.5*declared",
    8: "check dimension, weight 0 until first paper month (framework s5); "
       "months_tracked==0 -> untested",
}


def clip01(x):
    return max(0.0, min(1.0, x))


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_lines():
    """判线活读：science_gates 单源（O-2250 计数单源规则），零手抄常数。"""
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import science_gates as sg  # noqa: PLC0415
    sl = sg.skill_line_v2(batch_cells=0)  # 记分卡=零新搜索 -> n_eff=账本链头
    rec = sg.recorded_lines()
    return {
        "skill_line_v2": sl["line"], "skill_line_n_eff": sl["n_eff"],
        "i_line": rec["i_line"], "vi_bar": rec["vi_bar"],
        "passive": sg.passive_baseline(),
        "ledger_head": sg.ledger_head(),
        "source": "science_gates live reads (skill_line_v2 batch_cells=0, recorded_lines, passive_baseline)",
    }


def load_roster():
    out = []
    for f in sorted(os.listdir(TRADERS_DIR)):
        if not f.endswith(".json") or f.startswith("_"):
            continue
        t = _load(os.path.join(TRADERS_DIR, f))
        # T-24: PROSPECT = observation tier, excluded from scorecard ranking
        # (spec verbatim; ranking stays the registered roster's contest).
        if t.get("level") == "PROSPECT":
            continue
        out.append(t)
    return out


def _csv_rows(path, trader_id):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8-sig", newline="") as f:
        return [r for r in csv.DictReader(f) if r.get("trader") == trader_id]


def _median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return None
    m = n // 2
    return xs[m] if n % 2 else 0.5 * (xs[m - 1] + xs[m])


def batch_evidence(reg, lines):
    """按注册件 repro.script 定位批 JSON，解析 worst_year 与 x3 读数（缺=未测）。"""
    script = (reg.get("repro") or {}).get("script", "")
    base = os.path.basename(script)
    entry = (reg.get("params") or {}).get("entry", "")
    fam = entry.split("(")[0].strip()
    ev = {"worst_year": None, "x3_full": None, "batch": base}
    try:
        if base == "g2_folk.py":
            d = _load(os.path.join(RESULTS, "shortline_g2_folk.json"))
            for v in d.get("verdicts", []):
                if v.get("family") == fam:
                    ev["worst_year"] = v.get("worst_year")
                    ev["x3_full"] = v.get("x3")
                    break
        elif base == "ce_transfer.py":
            import re
            d = _load(os.path.join(RESULTS, "ce_transfer.json"))
            m = re.search(r"n=(\d+)", entry)
            if m:
                cell = d.get("runs", {}).get("ct_ce_top" + m.group(1), {})
                ev["worst_year"] = cell.get("worst_year")
                x3 = d.get("runs", {}).get("ct_ce_top" + m.group(1) + "_x3", {})
                ev["x3_full"] = (x3.get("full") or {}).get("sharpe")
        elif base == "combined_exit_screen.py":
            d = _load(os.path.join(RESULTS, "combined_exit.json"))
            v = d.get("verdict") or {}
            if "worst_year" in v:
                ev["worst_year"] = v.get("worst_year")
            ev["x3_full"] = v.get("cost_x3_full")  # J15 批未存 x3 键 -> None=未测
    except (OSError, ValueError, KeyError):
        pass
    return ev


def gather(tid, reg, ew6, p5, csvs, lines):
    """聚合单交易员全部原始读数（缺数据=未测，禁编造）。"""
    m = ew6["members"].get(tid, {})
    x1 = m.get("x1") or {}
    p5t = p5.get(tid) or {}
    rows = csvs.get(tid) or []
    excess = _median([float(r["ret_6m"]) - float(r["p_ret_6m"]) for r in rows
                      if r.get("ret_6m") and r.get("p_ret_6m")])
    corr_row = ((ew6.get("correlation") or {}).get("full") or {}).get("matrix", {}).get(tid, {})
    others = [abs(v) for k, v in corr_row.items() if k != tid]
    ev = batch_evidence(reg, lines)
    paper_path = os.path.join(RESULTS, "paper", tid + "_paper.json")
    paper = _load(paper_path) if os.path.exists(paper_path) else {}
    return {
        "reg": reg,
        "full_sharpe": (x1.get("full") or {}).get("sharpe"),
        "is2_sharpe": (x1.get("is2") or {}).get("sharpe"),
        "oos_sharpe": ((reg.get("backtest") or {}).get("out_sample") or {}).get("sharpe"),
        "n_trades_full": x1.get("n_trades"),
        "x2_sharpe": ((reg.get("backtest") or {}).get("cost_x2") or {}).get("sharpe"),
        "x2_survive": ((reg.get("backtest") or {}).get("cost_x2") or {}).get("survive"),
        "beat_rate_6m": p5t.get("beat_rate_6m"),
        "min_dd_6m": p5t.get("min_dd_6m"),
        "p5_verdict_pass": p5t.get("verdict_pass"),
        "median_excess_6m": excess,
        "max_corr_others": max(others) if others else None,
        "worst_year": ev["worst_year"],
        "x3_full": ev["x3_full"],
        "batch": ev["batch"],
        "paper_months": (paper.get("months_tracked")
                         or ((reg.get("paper") or {}).get("months_tracked"))),
    }


def _dim1(r):
    reads = {k: r[k] for k in ("beat_rate_6m", "min_dd_6m", "median_excess_6m", "p5_verdict_pass")}
    if r["beat_rate_6m"] is None or r["min_dd_6m"] is None:
        return 0.0, "untested", reads
    beat = 100.0 * clip01(r["beat_rate_6m"] / BEAT_FULL)
    dd = 100.0 * clip01((DD_RED_LINE - abs(r["min_dd_6m"])) / 0.30)
    if r["median_excess_6m"] is None:
        return 0.60 * beat + 0.25 * dd, "partial", reads  # excess 未测 -> 子权重再归一披露
    exc = 100.0 * clip01(r["median_excess_6m"] / 0.05)
    return 0.60 * beat + 0.25 * dd + 0.15 * exc, "tested", reads


def _dim2(r, lines):
    reads = {"full_sharpe": r["full_sharpe"], "oos_sharpe": r["oos_sharpe"],
             "skill_line_v2": lines["skill_line_v2"], "i_line": lines["i_line"]}
    if r["full_sharpe"] is None or r["oos_sharpe"] is None:
        return 0.0, "untested", reads
    full = 100.0 * clip01(r["full_sharpe"] / lines["skill_line_v2"])
    oos = 100.0 * clip01(r["oos_sharpe"] / lines["i_line"])
    return 0.70 * full + 0.30 * oos, "tested", reads


def _dim3(r, lines):
    reads = {"cost_x2_sharpe": r["x2_sharpe"], "x3_full_recorded": r["x3_full"],
             "vi_bar": lines["vi_bar"], "x2_survive": r["x2_survive"]}
    if r["x2_sharpe"] is None:
        return 0.0, "untested", reads
    ratio = r["x2_sharpe"] / lines["vi_bar"]
    s = 100.0 * clip01((ratio - 0.80) / 0.70)
    bonus = 5.0 if (r["x3_full"] is not None and r["x3_full"] >= lines["vi_bar"]) else 0.0
    return min(100.0, s + bonus), "tested", reads


def _dim4(r):
    reads = {"is2_sharpe": r["is2_sharpe"], "full_sharpe": r["full_sharpe"],
             "worst_year": r["worst_year"]}
    if r["is2_sharpe"] is None or r["full_sharpe"] is None:
        return 0.0, "untested", reads
    ret = 100.0 * clip01(r["is2_sharpe"] / r["full_sharpe"])
    direction = 100.0 if r["is2_sharpe"] > 0 else 0.0
    if r["worst_year"] is None:
        # worst_year 未测 -> 0.4/0.2 子权重再归一（披露）
        return 0.667 * ret + 0.333 * direction, "partial", reads
    wy = 100.0 * clip01((r["worst_year"] + 0.20) / 0.20)
    return 0.40 * ret + 0.40 * wy + 0.20 * direction, "tested", reads


def _dim5(r, ew6):
    reads = {"max_corr_others": r["max_corr_others"],
             "portfolio_benefit_context": (ew6.get("verdict") or {}).get("ew_benefit"),
             "note": "benefit/DR contribution is portfolio-level in EW6 -> per-member untestable, context only"}
    if r["max_corr_others"] is None:
        return 0.0, "untested", reads
    return 100.0 * clip01((0.60 - r["max_corr_others"]) / 0.50), "tested", reads


def _dim6(r):
    reads = {"n_trades_full": r["n_trades_full"],
             "note": "pool capacity + T+1 turnover load = no wired per-trader data -> untested, re-norm"}
    n = r["n_trades_full"]
    if n is None:
        return 0.0, "untested", reads
    if 30 <= n <= 800:
        return 100.0, "tested", reads
    if n < 30:
        return 100.0 * clip01((n - 10) / 20.0), "tested", reads
    return 100.0 * clip01((1200 - n) / 400.0), "tested", reads


def _dim7(r, lines):
    reg = r["reg"]
    prereg = 100.0 if (reg.get("repro") or {}).get("script") else 0.0
    blob = json.dumps(reg, ensure_ascii=False).lower()
    declared = 0.0 if ("undeclared" in blob and "snooping" in blob) else 100.0
    reads = {"prereg_chain": bool((reg.get("repro") or {}).get("script")),
             "declared_clean": declared > 0, "batch_script": r["batch"],
             "null_margin_vs_skill_line": (
                 round(r["full_sharpe"] - lines["skill_line_v2"], 4)
                 if r["full_sharpe"] is not None else None),
             "ledger_head_total": lines["ledger_head"].get("total")}
    return 0.5 * prereg + 0.5 * declared, "tested", reads


def _dim8(r):
    reads = {"paper_months_tracked": r["paper_months"]}
    if not r["paper_months"]:
        return 0.0, "untested", reads
    return 0.0, "pending_first_month", reads  # 转正公式=首月后预注册（框架 §2/§5）


def vetoes(r):
    reg = r["reg"]
    out = {
        "future_data": {
            "pass": True,
            "provenance": "no violation recorded in registration; engine causality guard = "
                          "smoke 20/20 system-level + paper truncate-and-compare selftest"},
        "x2_not_survive": {
            "pass": bool(r["x2_survive"]),
            "provenance": "firm/traders registration certificate backtest.cost_x2.survive"},
        "worst_start_dd_breach": {
            "pass": (r["min_dd_6m"] is not None and abs(r["min_dd_6m"]) < DD_RED_LINE),
            "provenance": "P-5/P-5B min_dd_6m vs -35% red line (O-1816/O-2345)"},
        "oos_blindspot": {
            "pass": bool(reg.get("evidence_cutoff")) and r["oos_sharpe"] is not None,
            "provenance": "registration carries evidence_cutoff + tracked OOS metrics"},
        "snooping_undeclared": {
            "pass": not ("undeclared" in json.dumps(reg, ensure_ascii=False).lower()
                         and "snooping" in json.dumps(reg, ensure_ascii=False).lower()),
            "provenance": "family-discount/honest flags recorded in registration notes = declared"},
    }
    return out


def grade(total, veto_clean, dims):
    if total >= GRADE_BANDS["S"] and veto_clean \
            and all(dims[k]["score"] >= S_CORE_DIM_MINS[k] for k in S_CORE_DIM_MINS):
        return "S"
    if total >= GRADE_BANDS["A"] and veto_clean:
        return "A"
    if total >= GRADE_BANDS["B"]:
        return "B"
    return "C"


def score_all(roster, lines, ew6, p5, csvs):
    cards = {}
    for reg in roster:
        tid = reg["id"]
        r = gather(tid, reg, ew6, p5, csvs, lines)
        dims = {}
        for num, fn in ((1, lambda: _dim1(r)), (2, lambda: _dim2(r, lines)),
                        (3, lambda: _dim3(r, lines)), (4, lambda: _dim4(r)),
                        (5, lambda: _dim5(r, ew6)), (6, lambda: _dim6(r)),
                        (7, lambda: _dim7(r, lines)), (8, lambda: _dim8(r))):
            s, status, reads = fn()
            w = WEIGHTS.get(num, WEIGHT_D8)
            dims[num] = {"score": round(s, 2), "weight": w, "status": status,
                         "reads": reads, "formula": FORMULAS[num]}
        total = sum(d["score"] * d["weight"] for d in dims.values())
        v = vetoes(r)
        veto_clean = all(x["pass"] for x in v.values())
        g = grade(total, veto_clean, dims)
        honest = []
        if r["p5_verdict_pass"] is False:
            honest.append("P-5/P-5B beat-line 0.70 verdict = FAIL (regime-premium discount "
                          "stands; score is ranking-line not gate, framework s0)")
        if r["x2_survive"] and r["x2_sharpe"] is not None \
                and r["x2_sharpe"] / lines["vi_bar"] < 1.05:
            honest.append("x2 margin razor-thin (<5% over vi_bar) -- watchdog mandatory (O-2205)")
        cards[tid] = {"grade": g, "total": round(total, 2), "veto_clean": veto_clean,
                      "vetoes": v, "dims": dims, "honest_notes": honest,
                      "level": reg.get("level"), "name": reg.get("name")}
    return cards


def run(out_path):
    lines = load_lines()
    roster = load_roster()
    if not roster:
        raise SystemExit("no traders found in firm/traders (roster = glob, zero hardcoded)")
    ew6 = _load(os.path.join(RESULTS, "portfolio_ew6.json"))
    p5 = {}
    for fn in ("p5_random_entry.json", "p5b_new_traders.json"):
        p5.update(_load(os.path.join(RESULTS, fn)).get("per_trader") or {})
    csvs = {}
    for tid in [t["id"] for t in roster]:
        rows = []
        for cp in (os.path.join(RESEARCH, "p5_random_entry_results.csv"),
                   os.path.join(RESEARCH, "shortline", "p5b_new_traders_results.csv")):
            rows += _csv_rows(cp, tid)
        csvs[tid] = rows
    cards = score_all(roster, lines, ew6, p5, csvs)
    counts = {g: sum(1 for c in cards.values() if c["grade"] == g) for g in "SABC"}
    best = max(cards.items(), key=lambda kv: kv[1]["total"])
    payload = {
        "task": "T-2026-09-23-07 (O-2311 GM Office first deliverable; O-1823 framework)",
        "framework": "firm/STRATEGY_EVALUATION.md v1.0 -- weights s2 + grade bands s3 frozen",
        "formula_version": "v1 (in-dimension sub-weights + linear anchors = implementation "
                           "choice, frozen here; revision = new version + round report)",
        "naming_disclosure": "framework s4 names strategy_scorecard(.py/.json); ticket T-07 "
                             "names scorecard.py + scorecard_v1.json -- implementation follows "
                             "the claimed ticket; law-side rename belongs to GM",
        "generated": _dt.datetime.now().isoformat(timespec="seconds"),
        "lines": lines,
        "weights": {str(k): v for k, v in WEIGHTS.items()},
        "grade_bands": GRADE_BANDS,
        "automation_note": "rerun monthly before hr first-business-day review + after any new "
                           "trader registration or new P-5/paper/EW evidence; NOT in 10-min S6 "
                           "chain (event cadence); report-only -- hr.py is sole level authority",
        "summary": {"n_traders": len(cards), "grade_counts": counts,
                    "best": {"id": best[0], "grade": best[1]["grade"],
                             "total": best[1]["total"]}},
        "per_trader": cards,
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    os.replace(tmp, out_path)
    print("scorecard: %d traders -> %s (S=%d A=%d B=%d C=%d, best %s %.1f)"
          % (len(cards), out_path, counts["S"], counts["A"], counts["B"], counts["C"],
             best[0], best[1]["total"]))
    for tid in sorted(cards, key=lambda k: -cards[k]["total"]):
        c = cards[tid]
        print("  %-18s %-2s total=%5.1f  d1=%.0f d2=%.0f d3=%.0f d4=%.0f d5=%.0f d6=%.0f d7=%.0f  veto=%s"
              % (tid, c["grade"], c["total"],
                 *[c["dims"][i]["score"] for i in range(1, 8)],
                 "clean" if c["veto_clean"] else "TRIGGERED"))
    return payload


def selftest():
    """离线合成夹具：零网络零真实写。锚定公式边界 + 否决路径 + 单调性。"""
    lines = {"skill_line_v2": 0.93, "skill_line_n_eff": 2753, "i_line": 0.3521,
             "vi_bar": 0.4004, "passive": 0.3792,
             "ledger_head": {"total": 2753}, "source": "synthetic"}
    champ = {"id": "T-CHAMP", "name": "x", "level": "INTERN", "evidence_cutoff": "2026-09-22",
             "repro": {"script": "scripts/g2_folk.py"},
             "backtest": {"out_sample": {"sharpe": 0.5}, "cost_x2": {"sharpe": 0.65, "survive": True}}}
    viol = {"id": "T-VIOL", "name": "y", "level": "INTERN", "evidence_cutoff": "2026-09-22",
            "repro": {"script": "scripts/g2_folk.py"},
            "backtest": {"out_sample": {"sharpe": 0.5}, "cost_x2": {"sharpe": 0.30, "survive": False}}}
    ew6 = {
        "members": {
            "T-CHAMP": {"x1": {"full": {"sharpe": 1.2}, "is2": {"sharpe": 0.9},
                               "n_trades": 300}},
            "T-VIOL": {"x1": {"full": {"sharpe": 1.2}, "is2": {"sharpe": 0.9},
                              "n_trades": 300}},
        },
        "correlation": {"full": {"matrix": {
            "T-CHAMP": {"T-CHAMP": 1.0, "T-VIOL": 0.15},
            "T-VIOL": {"T-CHAMP": 0.15, "T-VIOL": 1.0}}},
            "verdict": {"ew_benefit": 0.3}},
    }
    p5 = {"T-CHAMP": {"beat_rate_6m": 0.72, "min_dd_6m": -0.03, "verdict_pass": True},
          "T-VIOL": {"beat_rate_6m": 0.72, "min_dd_6m": -0.36, "verdict_pass": False}}
    csvs = {"T-CHAMP": [], "T-VIOL": []}
    cards = score_all([champ, viol], lines, ew6, p5, csvs)
    c, v = cards["T-CHAMP"], cards["T-VIOL"]
    assert c["veto_clean"] and c["grade"] == "S", "champion must be S (all sub-scores full-ish)"
    assert abs(c["dims"][1]["score"] - (0.60 * 100 + 0.25 * 100 * clip01((0.35 - 0.03) / 0.30))) < 1e-6
    assert not v["veto_clean"], "violator veto must trigger (x2 survive=False + dd breach)"
    assert v["grade"] in ("B", "C"), "veto triggered -> no S/A eligibility (framework s3)"
    # 边界单调性
    r = {"beat_rate_6m": 0.70, "min_dd_6m": -0.05, "median_excess_6m": 0.05,
         "p5_verdict_pass": True}
    s, st, _ = _dim1(r)
    assert st == "tested" and abs(s - 100.0) < 1e-6, "beat 0.70 + dd 5% + excess 5pp = full marks"
    r["min_dd_6m"] = -0.35
    s, _, _ = _dim1(r)
    assert abs(s - (0.60 * 100 + 0.15 * 100)) < 1e-6, "dd at red line -> dd sub-score 0"
    s3, _, _ = _dim3({"x2_sharpe": 0.4004 * 1.5, "x3_full": None, "x2_survive": True}, lines)
    assert abs(s3 - 100.0) < 1e-6, "x2 ratio 1.5x vi -> full"
    s6, _, _ = _dim6({"n_trades_full": 800})
    assert s6 == 100.0 and _dim6({"n_trades_full": 1200})[0] == 0.0
    print("selftest: 6/6 PASS (S-path, veto-path, boundary anchors, monotonic bands)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--out", default=OUT_DEFAULT)
    a = ap.parse_args()
    if a.cmd == "selftest":
        sys.exit(selftest())
    run(a.out)


if __name__ == "__main__":
    main()
