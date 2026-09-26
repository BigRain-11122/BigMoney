# -*- coding: utf-8 -*-
"""scripts/strategy_scorecard.py — 三对象多维评价体系 v2 全量实装
(T-2026-09-25-63 · CEO 令 O-20260925-1755 · 正典 firm/STRATEGY_EVALUATION.md v2.0)

对象三类：策略卡（§2 八维 v1.0 冻结权重）/ 交易员卡（§6）/ 组合卡（§7）。
统一评价律五条（§8）：≥2 维呈报、硬否决面通用、评价≠门禁、数据驱动、校准律。

反重复律（anti-dup）：
- 策略卡 = REUSE scripts/scorecard.py（T-07 实装、公式 v1 冻结、命名差异已在册披露）
  —— 本件 import 复用零重建；results/scorecard_v1.json 随刷。
- P-6 月度运营记分卡 = firm 端不同件；本件纸盘数据=只读复用其数据源（results/paper/*）。
- CORR_WATCH / g25 / t22 / t27 / t28 结果件 = 只读消费。

校准律（§8.5，硬边界）：交易员卡/组合卡**无总分**——首届对象分布校准预注册
（research/STRATEGY_SCORECARD_CALIB.md）冻结前，本件只产维度读数卡（readout-only），
硬否决面（§1.4/§8.2）即刻生效。策略卡总分/分级 = v1.0 冻结口径不变。

用法：
  python scripts/strategy_scorecard.py            # 刷策略卡 + 三卡 -> results/strategy_scorecard.json
  python scripts/strategy_scorecard.py calibrate  # 首届分布校准批 (SCORECARD_CALIB_P1)
                                                 #   -> results/strategy_scorecard_calib.json
  python scripts/strategy_scorecard.py selftest   # 离线合成夹具自检（零网络零真实写）
"""
import datetime as _dt
import hashlib
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import scorecard as sc  # noqa: E402  (策略卡 v1.0 引擎 — T-07 认领权威命名, 复用零重建)

RESULTS = os.path.join(ROOT, "results")
OUT_DEFAULT = os.path.join(RESULTS, "strategy_scorecard.json")
UNTESTED = "⬜ 未测"


def _load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


# ———————————————— 交易员卡（§6 · readout-only）————————————————

def trader_card(tid, strategy_card, corps_entry, paper, g25):
    """纯函数：单交易员读数卡。strategy_card=None → 继承面 ⬜（PROSPECT 无在册策略卡）。"""
    inherited = UNTESTED
    if strategy_card:
        inherited = {"total": strategy_card.get("total"),
                     "grade": strategy_card.get("grade"),
                     "veto_clean": strategy_card.get("veto_clean"),
                     "dims": {k: (v.get("score") if isinstance(v, dict) else v)
                              for k, v in (strategy_card.get("dims") or {}).items()},
                     "source": "results/scorecard_v1.json (scripts/scorecard.py v1.0)"}
    # 实战面：纸盘生涯（无纸盘文件=未接入, PROSPECT 构造性）
    if paper is None:
        live = {"state": UNTESTED, "note": "no paper account (PROSPECT constructive)"}
        discipline = {"state": UNTESTED, "violations": [], "note": "paper discipline untracked pre-registration"}
    else:
        x2w = paper.get("x2_watch") or {}
        live = {"state": "tested",
                "months_tracked": paper.get("months_tracked"),
                "n_monthly_returns": len(paper.get("monthly_returns") or []),
                "current_dd": paper.get("current_dd"),
                "capital": paper.get("capital"),
                "paper_start": paper.get("paper_start"),
                "x2_watch": {"state": (x2w.get("state") if isinstance(x2w, dict)
                                       else (x2w if isinstance(x2w, str) else None))},
                "cost_x2_check": paper.get("cost_x2_check")}
        violations = []
        if paper.get("anchor_ok") is False:
            violations.append("paper_anchor_drift")
        if paper.get("no_future_data") is False:
            violations.append("future_data_violation")
        rg = paper.get("regime_guard") or {}
        if isinstance(rg, dict) and rg.get("breach"):
            violations.append("regime_guard_breach")
        fg = paper.get("forward_guard") or {}
        if isinstance(fg, dict) and fg.get("breach"):
            violations.append("forward_guard_breach")
        discipline = {"state": "tested", "violations": violations,
                      "veto": bool(violations),   # §8.2 硬否决面即刻生效
                      "note": "clean" if not violations else "DISCIPLINE VETO (sec 8.2)"}
    # 进度面：G2.5 三检 + 纸盘月（hr.py 唯一晋升权威, 本面只读）
    if g25 is None:
        progress = {"state": UNTESTED, "note": "no g25 evidence file"}
    else:
        legs = g25.get("legs") or {}
        progress = {"state": "tested", "g25_verdict": g25.get("verdict"),
                    "dsr": (legs.get("dsr") or {}).get("value"),
                    "dsr_gate": (legs.get("dsr") or {}).get("gate"),
                    "ci_pass": (legs.get("ci") or {}).get("pass"),
                    "pbo_status": (legs.get("pbo") or {}).get("status"),
                    "paper_months_hr_threshold": "hr.py authority (read-only)"}
    # 画像面：政体段角色（corps_roster 数据判定面, 军种编制参考）
    profile = {"state": UNTESTED}
    if corps_entry:
        segs = corps_entry.get("segments") or {}
        profile = {"state": "tested" if segs else UNTESTED,
                   "corps": corps_entry.get("corps") or corps_entry.get("candidate_corps"),
                   "passing_segments": corps_entry.get("passing_segments"),
                   "segment_beat_rate_12m": {k: (v or {}).get("beat_rate_12m")
                                            for k, v in segs.items()} or None,
                   "segment_evidence": corps_entry.get("segment_evidence"),
                   "no_blowup": corps_entry.get("no_blowup"),
                   "source": "results/corps_roster.json (T-33 data-determined corps face)"}
    return {"trader": tid, "readout_only": True, "no_composite_total": "pre-calibration (sec 8.5)",
            "inherited_strategy": inherited, "live_paper": live,
            "discipline": discipline, "progress": progress, "profile": profile}


# ———————————————— 组合卡（§7 · readout-only）————————————————

def _max_offdiag(row_dict, self_key):
    """row_dict = 相关系数矩阵的一行 {other: corr}; 排除自身后取 max|corr|。"""
    vals = [abs(v) for k, v in (row_dict or {}).items() if k != self_key]
    return round(max(vals), 4) if vals else None


def portfolio_card_tournament(method, cand, verdict_face, corr_row, weights, ledger):
    """锦标赛方法卡（A_IV/B_MAXDIV/C_IVMOM/D_REGIME/E_EW）——T-27 v2 冻结口径只读。"""
    x1 = (cand or {}).get("x1") or {}
    x2 = (cand or {}).get("x2") or {}
    full1 = x1.get("full") or {}
    full2 = x2.get("full") or {}
    return {"portfolio": method, "readout_only": True,
            "no_composite_total": "pre-calibration (sec 8.5)",
            "source": "results/portfolio_blend_tournament.json (T-27 v2 frozen roster)",
            "quality": {"state": "tested" if full1 else UNTESTED,
                        "x1_full_sharpe": full1.get("sharpe"),
                        "x1_annual": full1.get("annual_return"),
                        "x1_max_dd": full1.get("max_drawdown"),
                        "benefit": (verdict_face or {}).get("benefit"),
                        "drawdown": (verdict_face or {}).get("drawdown"),
                        "eligible": (verdict_face or {}).get("eligible", None),
                        "yearly": x1.get("yearly"), "worst_year": x1.get("worst_year")},
            "cost": {"state": "tested" if full2 else UNTESTED,
                     "x2_full_sharpe": full2.get("sharpe"),
                     "x2_margin": (verdict_face or {}).get("x2_margin"),
                     "note": "x2 survival gate (SCIENCE cost v2); margin vs frozen vi_bar"},
            "segment_coverage": {"state": "tested" if x1.get("yearly") else UNTESTED,
                                 "yearly_face": x1.get("yearly"),
                                 "note": "O-2012 no-universal-blend: per-year + regime-segment "
                                         "disclosure mandatory; 2025+ face = IS2 forward-lockbox "
                                         "(d2_note in source file)"},
            "cross_period_j4": {"state": "pointer",
                                "source": "results/spm_j4_attribution.json + "
                                          "results/current_market_stable_profit.json (T-28 J1-J4)",
                                "note": "portfolio-level J4 honest negative on record "
                                        "(stable-profit verdict NOT-DEMONSTRATED)"},
            "marginal": {"state": "tested" if corr_row else UNTESTED,
                         "max_abs_corr_vs_other_methods": _max_offdiag(corr_row, method)
                         if isinstance(corr_row, dict) else None,
                         "n_members_weighted": len((weights or {}).get("weights") or {})
                         if isinstance(weights, dict) else None},
            "statistical": {"state": "tested" if ledger else UNTESTED,
                            "trials_ledger_total": (ledger or {}).get("total"),
                            "batch_trials": (ledger or {}).get("batch_trials")}}


def portfolio_card_iv6(kind, src, head_to_head, ledger):
    """IV6/EW6 在册组合卡——各自结果件只读（EW6=validated carrier; IV6=report-only pass 2）。"""
    ports = src.get("portfolios_iv" if kind == "IV6" else "portfolios") or {}
    x1, x2 = ports.get("x1") or {}, ports.get("x2") or {}
    full1, full2 = x1.get("full") or {}, x2.get("full") or {}
    corr_matrix = ((src.get("correlation") or {}).get("full") or {}).get("matrix") or {}
    weights = (src.get("iv_weights") if kind == "IV6" else None) or {}
    return {"portfolio": kind, "readout_only": True,
            "no_composite_total": "pre-calibration (sec 8.5)",
            "source": ("results/portfolio_iv6.json" if kind == "IV6"
                       else "results/portfolio_ew6.json"),
            "quality": {"state": "tested" if full1 else UNTESTED,
                        "x1_full_sharpe": full1.get("sharpe"),
                        "x1_annual": full1.get("annual_return"),
                        "x1_max_dd": full1.get("max_drawdown"),
                        "head_to_head_vs_ew": head_to_head,
                        "void": src.get("void")},
            "cost": {"state": "tested" if full2 else UNTESTED,
                     "x2_full_sharpe": full2.get("sharpe"),
                     "note": "x2 margin disclosure via corr_watch W5 (recorded config)"},
            "segment_coverage": {"state": "pointer",
                                 "note": "per-member yearly in source members face; "
                                         "2025+ = IS2 forward-lockbox (d2_note)"},
            "cross_period_j4": {"state": "pointer",
                                "source": "results/spm_j4_attribution.json (T-28 J4 口径)",
                                "note": "member-level 12m beat rates in spm file; portfolio-level "
                                         "stable-profit J4 = NOT-DEMONSTRATED (honest negative)"},
            "marginal": {"state": "tested" if corr_matrix else UNTESTED,
                         "max_abs_offdiag_member_corr": _max_offdiag(
                             corr_matrix.get(next(iter(corr_matrix))), next(iter(corr_matrix)))
                         if corr_matrix else None,
                         "weights": weights.get("weights") if kind == "IV6" else
                                   (x1.get("weights") if x1 else None)},
            "statistical": {"state": "tested" if ledger else UNTESTED,
                            "trials_ledger_total": (ledger or {}).get("total"),
                            "batch_trials": (ledger or {}).get("batch_trials"),
                            "prereg_sha256_at_run": src.get("prereg_sha256_at_run")}}


# ———————————————— 校准批（SCORECARD_CALIB_P1 · §8.5）————————————————
# 预注册冻结件 = research/STRATEGY_SCORECARD_CALIB.md（程序冻结后一次性跑批；
# 跑后禁改程序禁调带，带数值随本批 commit 冻结，修订=v2 校准批·§6）。
# 纯读数统计批：零新回测、零引擎、ledger+0、不选对象只定标尺。

CALIB_PREREG = "research/STRATEGY_SCORECARD_CALIB.md"
CALIB_OUT_DEFAULT = os.path.join(RESULTS, "strategy_scorecard_calib.json")
W_DOMINANT = 0.40   # 主导维权重 = 冻结带 35-45% 中点（§1.3③）
W_CAP = 0.50        # 单一维度权重帽（§1.3② ≥2 维呈报律的带面化）
ANCHORS_DOC = {      # 面分公式锚点（跑前冻结；None/缺 → 0 = §1.1 未测零分惯例）
    "traders": {
        "inherited": "registered: v1.0 total (0-100 direct); PROSPECT: "
                     "100*(0.50*mean(g2 neighborhood/cost_x3/per_year legs) "
                     "+ 0.25*lin(recorded_oos_sharpe,0,2) + 0.25*lin(recorded_x2_full_sharpe,0,2))",
        "live_paper": "100*(0.50*min(1,months_tracked/6) + 0.30*clamp(1+2*current_dd,0,1) "
                      "+ 0.10*(x2_watch state=='ok') + 0.10*(cost_x2_check pass))",
        "progress": "100*(0.60*(g25_verdict=='pass') + 0.20*(dsr>=dsr_gate) + 0.20*(ci_pass is True))",
        "profile": "100*(0.30*(corps confirmed, non-pending) + 0.30*min(1,n_passing_segments/3) "
                   "+ 0.40*clamp(mean(segment_beat_rate_12m),0,1))",
        "discipline": "GATE ONLY (sec 1.3-1 / 8.2): veto face carries no weight",
    },
    "portfolios": {
        "quality": "100*(0.80*lin(x1_full_sharpe,0,2) + 0.20*lin(benefit or "
                   "head_to_head.delta_full_sharpe,0,1))",
        "cost": "100*(0.60*lin(x2_full_sharpe,0,2) + 0.40*lin(x2_margin,0,0.2); "
                "margin missing -> 0 credit (untested-zero sub-face)",
        "segment_coverage": "100*min(1,n_yearly_years/6); pointer face -> 0",
        "cross_period_j4": "0 for all (T-28 J4 NOT-DEMONSTRATED honest negative inherited, sec 2)",
        "marginal": "100*clamp((0.6-max_abs_corr)/0.6,0,1)",
        "statistical": "100*clamp(log10(max(trials_ledger_total,1))/4,0,1)",
    },
}
TRADER_FACES = ("inherited", "live_paper", "progress", "profile")
PORTFOLIO_FACES = ("quality", "cost", "segment_coverage", "cross_period_j4",
                   "marginal", "statistical")


def _lin01(x, lo, hi):
    """线性锚点映射 → [0,1]；None/缺 → 0（未测零分 §1.1）。"""
    if x is None:
        return 0.0
    if hi <= lo:
        return 1.0 if x >= hi else 0.0
    t = (x - lo) / (hi - lo)
    return 0.0 if t < 0 else (1.0 if t > 1 else t)


def _quantile(vals, p):
    """线性插值分位（numpy 默认口径）；空集 → None。"""
    s = sorted(vals)
    if not s:
        return None
    if len(s) == 1:
        return float(s[0])
    idx = (len(s) - 1) * p
    lo = int(idx)
    if lo + 1 >= len(s):
        return float(s[lo])
    return float(s[lo] + (idx - lo) * (s[lo + 1] - s[lo]))


def _clamp01(x):
    if x is None:
        return 0.0
    return 0.0 if x < 0 else (1.0 if x > 1 else float(x))


def trader_face_scores(card):
    """交易员卡 → 各面 0-100 分 + 状态标记 + 纪律否决旗（公式锚点见 ANCHORS_DOC）。"""
    inh = card.get("inherited_strategy")
    live = card.get("live_paper") or {}
    prog = card.get("progress") or {}
    prof = card.get("profile") or {}
    disc = card.get("discipline") or {}
    if isinstance(inh, dict) and inh.get("total") is not None:
        inherited = float(inh["total"])
        inh_state = "tested(v1.0 total)"
    elif isinstance(inh, dict) and inh.get("dims"):
        d = inh.get("dims") or {}
        legs = [1.0 if d.get(k) is True else 0.0
                for k in ("g2_neighborhood_pass", "g2_cost_x3_pass", "g2_per_year_pass")]
        inherited = 100.0 * (0.50 * sum(legs) / 3.0
                             + 0.25 * _lin01(d.get("recorded_oos_sharpe"), 0.0, 2.0)
                             + 0.25 * _lin01(d.get("recorded_x2_full_sharpe"), 0.0, 2.0))
        inh_state = "tested(recorded-evidence)"
    else:
        inherited, inh_state = 0.0, "untested"
    if live.get("state") == "tested":
        months = live.get("months_tracked") or 0
        dd = live.get("current_dd") or 0.0
        x2 = live.get("x2_watch") if isinstance(live.get("x2_watch"), dict) else {}
        cost = live.get("cost_x2_check")
        cost_ok = (cost is True) or (isinstance(cost, dict) and cost.get("status") == "pass")
        live_s = 100.0 * (0.50 * min(1.0, months / 6.0)
                          + 0.30 * _clamp01(1.0 + 2.0 * dd)
                          + 0.10 * (1.0 if x2.get("state") == "ok" else 0.0)
                          + 0.10 * (1.0 if cost_ok else 0.0))
        live_state = "tested"
    else:
        live_s, live_state = 0.0, "untested"
    if prog.get("state") == "tested":
        dsr, gate = prog.get("dsr"), prog.get("dsr_gate")
        prog_s = 100.0 * (0.60 * (1.0 if prog.get("g25_verdict") == "pass" else 0.0)
                          + 0.20 * (1.0 if (dsr is not None and gate is not None
                                            and dsr >= gate) else 0.0)
                          + 0.20 * (1.0 if prog.get("ci_pass") is True else 0.0))
        prog_state = "tested"
    else:
        prog_s, prog_state = 0.0, "untested"
    if prof.get("state") == "tested":
        corps = prof.get("corps")
        segs = prof.get("passing_segments") or []
        beats = [v for v in ((prof.get("segment_beat_rate_12m") or {}).values())
                 if isinstance(v, (int, float))]
        confirmed = 1.0 if (corps and corps != "pending-classification") else 0.0
        prof_s = 100.0 * (0.30 * confirmed
                          + 0.30 * min(1.0, len(segs) / 3.0)
                          + 0.40 * _clamp01(sum(beats) / len(beats) if beats else 0.0))
        prof_state = "tested"
    else:
        prof_s, prof_state = 0.0, "untested"
    veto = bool(disc.get("veto")) if disc.get("state") == "tested" else False
    return {"inherited": round(inherited, 1), "live_paper": round(live_s, 1),
            "progress": round(prog_s, 1), "profile": round(prof_s, 1),
            "_states": {"inherited": inh_state, "live_paper": live_state,
                        "progress": prog_state, "profile": prof_state},
            "_discipline_veto": veto}


def portfolio_face_scores(card):
    """组合卡 → 各面 0-100 分 + 状态标记（公式锚点见 ANCHORS_DOC）。"""
    q = card.get("quality") or {}
    cost = card.get("cost") or {}
    seg = card.get("segment_coverage") or {}
    j4 = card.get("cross_period_j4") or {}
    marg = card.get("marginal") or {}
    stat = card.get("statistical") or {}
    if q.get("state") == "tested":
        benefit = q.get("benefit")
        if benefit is None:
            h2h = q.get("head_to_head_vs_ew")
            benefit = h2h.get("delta_full_sharpe") if isinstance(h2h, dict) else None
        q_s = 100.0 * (0.80 * _lin01(q.get("x1_full_sharpe"), 0.0, 2.0)
                       + 0.20 * _lin01(benefit, 0.0, 1.0))
        q_st = "tested"
    else:
        q_s, q_st = 0.0, "untested"
    if cost.get("state") == "tested":
        c_s = 100.0 * (0.60 * _lin01(cost.get("x2_full_sharpe"), 0.0, 2.0)
                       + 0.40 * _lin01(cost.get("x2_margin"), 0.0, 0.2))
        c_st = "tested"
    else:
        c_s, c_st = 0.0, "untested"
    if seg.get("state") == "tested":
        seg_s = 100.0 * min(1.0, len(seg.get("yearly_face") or {}) / 6.0)
        seg_st = "tested"
    else:
        seg_s, seg_st = 0.0, "pointer-untested"
    j4_s = 0.0   # NOT-DEMONSTRATED 诚实负结论继承（§2 禁美化）
    j4_st = "recorded-negative" if j4.get("state") == "pointer" else "untested"
    if marg.get("state") == "tested":
        corr = marg.get("max_abs_corr_vs_other_methods")
        if corr is None:
            corr = marg.get("max_abs_offdiag_member_corr")
        m_s = 100.0 * _clamp01((0.6 - corr) / 0.6) if corr is not None else 0.0
        m_st = "tested"
    else:
        m_s, m_st = 0.0, "untested"
    if stat.get("state") == "tested":
        trials = stat.get("trials_ledger_total") or 0
        st_s = 100.0 * _clamp01(math.log10(max(trials, 1)) / 4.0)
        st_st = "tested"
    else:
        st_s, st_st = 0.0, "untested"
    return {"quality": round(q_s, 1), "cost": round(c_s, 1),
            "segment_coverage": round(seg_s, 1), "cross_period_j4": round(j4_s, 1),
            "marginal": round(m_s, 1), "statistical": round(st_s, 1),
            "_states": {"quality": q_st, "cost": c_st, "segment_coverage": seg_st,
                        "cross_period_j4": j4_st, "marginal": m_st, "statistical": st_st},
            "_discipline_veto": False}


def _dist_row(values, cohort_n):
    """§1.2 分布披露：⬜ 不进分位分母；availability = tested/n。"""
    row = {"n": cohort_n, "tested_n": len(values),
           "availability": round(len(values) / cohort_n, 3) if cohort_n else None}
    if values:
        row.update({"min": round(min(values), 2), "q25": round(_quantile(values, .25), 2),
                    "median": round(_quantile(values, .5), 2),
                    "q75": round(_quantile(values, .75), 2), "max": round(max(values), 2)})
    else:
        row.update({"min": None, "q25": None, "median": None, "q75": None, "max": None})
    return row


def _allocate_weights(dominant, others, spreads):
    """§1.3 冻结规则：主导维 0.40；余量按 tested (q75-q25) 跨度比例分配；
    总跨度=0 → 等分；单维帽 0.50，超额按未帽面跨度比例单程再分配（无处再分配
    且主导维越帽 → 断言红=冻结规则死锁，诚实失败）。"""
    if not others:
        raise AssertionError("allocation requires >=1 non-dominant face (>=2-dim law sec 8.1)")
    w = {dominant: W_DOMINANT}
    pool = 1.0 - W_DOMINANT
    total_spread = sum(spreads.get(f, 0.0) for f in others)
    if total_spread <= 0:
        for f in others:
            w[f] = pool / len(others)
    else:
        for f in others:
            w[f] = pool * spreads.get(f, 0.0) / total_spread
    excess, capped = 0.0, set()
    for f in others:
        if w[f] > W_CAP:
            excess += w[f] - W_CAP
            w[f] = W_CAP
            capped.add(f)
    if excess > 0:
        rest = [f for f in others if f not in capped]
        rest_spread = sum(spreads.get(f, 0.0) for f in rest)
        if rest_spread > 0:
            for f in rest:
                w[f] += excess * spreads.get(f, 0.0) / rest_spread
        elif rest:
            for f in rest:
                w[f] += excess / len(rest)
        elif w[dominant] + excess <= W_CAP:
            w[dominant] += excess
        else:
            raise AssertionError("weight-cap deadlock under frozen allocation rule")
    return {k: round(v, 4) for k, v in w.items()}


def _grade_of(total, bands, vetoed):
    if vetoed:
        return "VETO"
    if total >= bands["S"]:
        return "S"
    if total >= bands["A"]:
        return "A"
    if total >= bands["B"]:
        return "B"
    return "C"


def _collect_evidence_cutoff(payload):
    """§0 evidence_cutoff = 输入源最旧 cutoff（前向锁盒 D2）；缺 cutoff 的源如实登记。"""
    cuts, missing = {}, []
    srcs = list((payload.get("audit") or {}).get("sources") or [])
    for sub in ("results/paper", "results/g25"):
        pdir = os.path.join(ROOT, sub)
        if os.path.isdir(pdir):
            for fn in os.listdir(pdir):
                if fn.endswith(".json") and not fn.startswith("_"):
                    srcs.append(os.path.join(sub, fn))
    for s in srcs:
        path = s if os.path.isabs(s) else os.path.join(ROOT, s)
        d = _load(path)
        if d is None:
            missing.append(s)
            continue
        c = d.get("evidence_cutoff") or d.get("cutoff") or d.get("data_cutoff")
        if isinstance(c, str) and len(c) >= 10:
            cuts[s] = c[:10]
        else:
            missing.append(s)
    return (min(cuts.values()) if cuts else None), cuts, missing


def calibrate(in_path=OUT_DEFAULT, out_path=CALIB_OUT_DEFAULT):
    """SCORECARD_CALIB_P1 校准批（§1 五步）：读数物化 → 分布披露 → 权重带 →
    分级带（p80/p60/p40 分位法）→ 一次写盘。跑后只许回填 prereg §7。"""
    t0 = time.time()
    payload = _load(in_path)
    if not payload or not payload.get("trader_cards"):
        print("calibrate: input missing/invalid (%s) — run `strategy_scorecard.py run` first"
              % in_path)
        return 2
    t_cards = payload.get("trader_cards") or {}
    p_cards = payload.get("portfolio_cards") or {}
    t_scores = {tid: trader_face_scores(c) for tid, c in t_cards.items()}
    p_scores = {pid: portfolio_face_scores(c) for pid, c in p_cards.items()}

    def face_tables(scores, faces):
        dist, spreads = {}, {}
        for f in faces:
            vals = [s[f] for s in scores.values()
                    if s["_states"][f].startswith("tested") or s["_states"][f] == "recorded-negative"]
            dist[f] = _dist_row(vals, len(scores))
            spreads[f] = (dist[f]["q75"] or 0.0) - (dist[f]["q25"] or 0.0) \
                if dist[f]["q75"] is not None else 0.0
        return dist, {k: round(v, 4) for k, v in spreads.items()}

    t_dist, t_spread = face_tables(t_scores, TRADER_FACES)
    p_dist, p_spread = face_tables(p_scores, PORTFOLIO_FACES)
    t_w = _allocate_weights("inherited", [f for f in TRADER_FACES if f != "inherited"], t_spread)
    p_w = _allocate_weights("quality", [f for f in PORTFOLIO_FACES if f != "quality"], p_spread)

    t_totals = {tid: round(sum(w * s[f] for f, w in t_w.items()), 1)
                for tid, s in t_scores.items()}
    p_totals = {pid: round(sum(w * s[f] for f, w in p_w.items()), 1)
                for pid, s in p_scores.items()}
    t_bands = {"S": round(_quantile(list(t_totals.values()), 0.80), 1),
               "A": round(_quantile(list(t_totals.values()), 0.60), 1),
               "B": round(_quantile(list(t_totals.values()), 0.40), 1)}
    p_bands = {"S": round(_quantile(list(p_totals.values()), 0.80), 1),
               "A": round(_quantile(list(p_totals.values()), 0.60), 1),
               "B": round(_quantile(list(p_totals.values()), 0.40), 1)}
    t_grades = {tid: _grade_of(t, t_bands, s["_discipline_veto"])
                for tid, t, s in ((k, v, t_scores[k]) for k, v in t_totals.items())}
    p_grades = {pid: _grade_of(p, p_bands, False) for pid, p in p_totals.items()}
    veto_hits = {tid for tid, s in t_scores.items() if s["_discipline_veto"]}

    # §3 跑前预测核验（如实报告、不翻案）
    s_band_t = sorted(tid for tid, g in t_grades.items() if g == "S")
    prospect_in_s = [t for t in s_band_t if t.startswith("PROS-")]
    top2_spread_p = sorted(p_spread.items(), key=lambda kv: -kv[1])[:2]
    predictions_check = {
        "p1_double_clump": {
            "median_trader_total": t_dist and round(_quantile(list(t_totals.values()), .5), 1),
            "note": "median falls inside PROSPECT cluster" if _quantile(list(t_totals.values()), .5) < 30
            else "median NOT in prospect cluster (report as-is)",
            "s_band": s_band_t, "n_prospect_in_s_band": len(prospect_in_s),
            "anomaly_flag": bool(prospect_in_s),
            "prediction_holds": not prospect_in_s,
        },
        "p2_portfolio_differentiation": {
            "top2_spread_faces": [k for k, _ in top2_spread_p],
            "prediction_holds": {k for k, _ in top2_spread_p} <= {"quality", "cost"}
                                 and len(top2_spread_p) >= 2,
        },
        "p3_s_band_registered_only": {"prediction_holds": not prospect_in_s},
    }

    cutoff, cuts_detail, cuts_missing = _collect_evidence_cutoff(payload)
    n_untested_faces = {"traders": sum(1 for s in t_scores.values()
                                       for f in TRADER_FACES
                                       if not s["_states"][f].startswith("tested")),
                        "portfolios": sum(1 for s in p_scores.values()
                                          for f in PORTFOLIO_FACES
                                          if not (s["_states"][f].startswith("tested")
                                                  or s["_states"][f] == "recorded-negative"))}
    result = {
        "ticket": "T-2026-09-25-63", "batch": "SCORECARD_CALIB_P1",
        "prereg": CALIB_PREREG + " (frozen; run-once law sec 0/6)",
        "charter": "firm/STRATEGY_EVALUATION.md v2.0 sec 8.5",
        "generated": _dt.datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": cutoff, "cutoff_sources": cuts_detail,
        "cutoff_missing_sources": cuts_missing,
        "cohorts": {"traders": {"n": len(t_scores)},
                    "portfolios": {"n": len(p_scores)}},
        "face_score_anchors": ANCHORS_DOC,
        "distributions": {"traders": t_dist, "portfolios": p_dist},
        "spreads_q75_minus_q25": {"traders": t_spread, "portfolios": p_spread},
        "weight_allocation_rule": "dominant=0.40 (35-45% band midpoint); remaining 0.60 by "
                                  "tested (q75-q25) spread share; zero-total-spread -> equal "
                                  "split; single-face cap 0.50 with one-pass proportional "
                                  "redistribution (frozen, sec 1.3)",
        "weights": {"traders": t_w, "portfolios": p_w},
        "grade_band_rule": "S>=p80, A>=p60, B>=p40, C rest; VETO overrides (sec 1.4/8.2)",
        "grade_bands": {"traders": t_bands, "portfolios": p_bands},
        "totals": {"traders": {tid: {"faces": {f: t_scores[tid][f] for f in TRADER_FACES},
                                     "total": t_totals[tid], "grade": t_grades[tid],
                                     "discipline_veto": t_scores[tid]["_discipline_veto"]}
                               for tid in sorted(t_totals)},
                   "portfolios": {pid: {"faces": {f: p_scores[pid][f] for f in PORTFOLIO_FACES},
                                         "total": p_totals[pid], "grade": p_grades[pid]}
                                  for pid in sorted(p_totals)}},
        "predictions_check": predictions_check,
        "audit": {"input_generated": payload.get("generated"),
                  "input_path": in_path, "cohort_counts": {"traders": len(t_scores),
                                                           "portfolios": len(p_scores)},
                  "expected_cohorts": {"traders": 28, "portfolios": 7},
                  "untested_face_counts": n_untested_faces,
                  "discipline_veto_hits": sorted(veto_hits),
                  "elapsed_sec": round(time.time() - t0, 1),
                  "zero_new_backtests": True, "zero_engine_runs": True, "ledger_delta": 0,
                  "run_once_law": "band/weight values frozen at this batch's commit; "
                                  "recalibration = v2 prereg only (sec 2/6)"},
    }
    if len(t_scores) != 28 or len(p_scores) != 7:
        print("calibrate: cohort count mismatch (traders=%d expected 28, portfolios=%d expected 7)"
              " — honest abort, no output written" % (len(t_scores), len(p_scores)))
        return 2
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    os.replace(tmp, out_path)
    print("calibrate: traders n=%d portfolios n=%d -> %s (%.1fs)" %
          (len(t_scores), len(p_scores), out_path, result["audit"]["elapsed_sec"]))
    print("  weights traders:", t_w)
    print("  weights portfolios:", p_w)
    print("  bands traders:", t_bands, "| portfolios:", p_bands)
    print("  evidence_cutoff:", cutoff, "| untested faces:", n_untested_faces)
    if veto_hits:
        print("  DISCIPLINE VETO in cohort:", sorted(veto_hits))
    return 0


def _attach_composites(cards, weights, bands, face_scores_fn, faces):
    """启用门（§1.5）：校准批冻结后，本函数把总分+分级接到每张卡上。
    权重/带值只读自冻结件（SCORECARD_CALIB_P1），本函数零新阈值零调带；
    新对象按冻结带绝对值落带（§2 带不重算）。纯函数卡面保持读数原样。"""
    for oid, card in cards.items():
        s = face_scores_fn(card)
        total = round(sum(w * s[f] for f, w in weights.items() if f in s), 1)
        card["composite"] = {
            "total": total,
            "grade": _grade_of(total, bands, s["_discipline_veto"]),
            "face_scores": {f: s[f] for f in faces if f in s},
            "weights": weights, "bands": bands,
            "source": "results/strategy_scorecard_calib.json (SCORECARD_CALIB_P1 frozen)",
            "veto": s["_discipline_veto"],
        }
        card["readout_only"] = False
        card.pop("no_composite_total", None)
        card["calibrated_total"] = "sec 8.5 gate passed: frozen bands consumed"


def _load_calib_for_emission():
    """读冻结校准件；缺件/结构不符 → None（维持校准前读数卡模式）。"""
    calib = _load(CALIB_OUT_DEFAULT)
    if not calib or calib.get("batch") != "SCORECARD_CALIB_P1":
        return None
    tw = ((calib.get("weights") or {}).get("traders") or {})
    pw = ((calib.get("weights") or {}).get("portfolios") or {})
    tb = ((calib.get("grade_bands") or {}).get("traders") or {})
    pb = ((calib.get("grade_bands") or {}).get("portfolios") or {})
    if not (tw and pw and tb and pb):
        return None
    return {"tw": tw, "pw": pw, "tb": tb, "pb": pb,
            "cutoff": calib.get("evidence_cutoff")}


# ———————————————— 适用域画像卡（T-81 · O-20260926-1342 · PROFILE_CARDS_P1）————————————————
# 预注册冻结: research/PROFILE_CARDS_P1.md（跑前冻结判线，跑后禁改）。
# 语义=readout 派生面：对 T-79 既有 17 台账做逐状态战绩分解+死区+激活+击杀申报；
# 哲学律（O-1342 §一）：画像卡无总分，逐状态通过/失败=主判决，总分=派生索引视图非依据。

PROFILE_PREREG = os.path.join(ROOT, "research", "PROFILE_CARDS_P1.md")
SAMPLE_SCIENCE_PREREG = os.path.join(ROOT, "research", "SAMPLE_SCIENCE_P1.md")
LANDING_HOOKS_PREREG = os.path.join(ROOT, "research", "LANDING_HOOKS_P1.md")
PROFILE_MIN_N_DAYS = 20     # §3 冻结线：州内证据日下限
PROFILE_MIN_EPISODES = 2    # §3 冻结线：独立政体窗下限（单连续段=零复制）
PROFILE_STATES = ("GREEN", "YELLOW", "ORANGE", "RED")
COST_RAZOR_MARGINS = {"COMPOSITE-CE-02": 0.031,   # firm/OPERATING_PLAN §2 冻结数
                      "ENGULF-CE-01": 0.002}


def _profile_returns(dates, equity, initial):
    """收益日序列（§2 冻结口径）：r0=eq[0]/initial−1（A 组 hire 日=0 收益日计入州面）；
    ri=eq[i]/eq[i−1]−1。全窗逐日积=台账 cum_ret（自洽门 §3.4 消费）。"""
    out = []
    if not dates or not equity or not initial or initial <= 0:
        return out
    prev = float(initial)
    for d, e in zip(dates, equity):
        e = float(e)
        if prev > 0:
            out.append((d, e / prev - 1.0))
        prev = e
    return out


def _profile_episodes(seq):
    """{键: 连续段数}——独立政体窗计数（§3）。"""
    counts, prev = {}, None
    for k in seq:
        if k != prev:
            counts[k] = counts.get(k, 0) + 1
            prev = k
    return counts


def _cum_of(rets):
    c = 1.0
    for _d, r in rets:
        c *= (1.0 + r)
    return c - 1.0


def _state_cums(rets, states_by_date):
    """{州: 累计}——缺州=0.0（该州无日=零收益）。"""
    acc = {s: 1.0 for s in PROFILE_STATES}
    for d, r in rets:
        s = states_by_date.get(d)
        if s in acc:
            acc[s] *= (1.0 + r)
    return {s: acc[s] - 1.0 for s in PROFILE_STATES}


def _profile_verdict(n_days, episodes, cum, excess):
    """§3 冻结判定：证据不足=NO_EVIDENCE（fail-closed）；充分且双线过=PASS；否则 DEAD_ZONE。"""
    if n_days < PROFILE_MIN_N_DAYS or episodes < PROFILE_MIN_EPISODES:
        return "NO_EVIDENCE"
    return "PASS" if (cum > 0.0 and excess >= 0.0) else "DEAD_ZONE"


def _four_must_cell(rs, n_trades_cell, episodes):
    """SAMPLE_SCIENCE_P1 §1 四必报单格（T-81 slice-3·披露面，零判定线触碰）。

    oos_trades=A 组逐笔计数（int）/B-C 与缺面=null 诚实；covered_years=日集日历跨度
    （p5c L675 / t22 L465 公式先例）；independent_regime_windows=slice-1 episodes 逐字；
    ci95=science_gates.bootstrap_ci_sharpe 逐字（种子 20260923 家族冻结），n<20=机制
    下限诚实拒算（None 三值，非编数）。
    """
    n = len(rs)
    cov = None
    if n:
        ds = sorted(_d for _d, _r in rs)
        try:
            first = _dt.date.fromisoformat(ds[0])
            last = _dt.date.fromisoformat(ds[-1])
            cov = round((last - first).days / 365.25, 2)
        except ValueError:
            cov = None
    ci = None
    if n >= PROFILE_MIN_N_DAYS:
        import science_gates as _sg
        ci = _sg.bootstrap_ci_sharpe([r for _d, r in rs])
    return {
        "oos_trades": (int(n_trades_cell) if isinstance(n_trades_cell, int) else None),
        "covered_years": cov,
        "independent_regime_windows": int(episodes),
        "ci95_lo": (ci["ci95_low"] if ci else None),
        "ci95_hi": (ci["ci95_high"] if ci else None),
        "ci95_width": (round(ci["ci95_high"] - ci["ci95_low"], 4) if ci else None),
        "ci_lower_bound_positive": (ci["ci_lower_bound_positive"] if ci else None),
    }


def _sample_science_block(rets, states_by_date, state_seq, trades_total, states_face):
    """SAMPLE_SCIENCE_P1 §2 卡级分样缩水披露块（CI 加宽照报·O-1342 §二）。

    window_four_must=全窗四必报；per_state=州级对照；widest_state_ci=最宽州 CI
    （O-1342 §一.3 最宽 CI 披露落法）；min_windows_gate=slice-1 冻结门逐字携带。
    """
    fm = _four_must_cell(rets, trades_total,
                         sum(_profile_episodes(state_seq).values()))
    per_state = {s: {"n_days": states_face[s]["n_days"],
                     "ci95_width": states_face[s]["ci95_width"],
                     "ci_lower_bound_positive": states_face[s]["ci_lower_bound_positive"]}
                 for s in PROFILE_STATES}
    widest = None
    for s in PROFILE_STATES:
        w = states_face[s]["ci95_width"]
        if w is not None and (widest is None or w > widest[1]):
            widest = (s, w)
    return {
        "window_four_must": fm,
        "per_state": per_state,
        "shrinkage_note": ("split-sample shrinkage disclosed: state n_days < window n_days; "
                           "state CI width > window CI width expected (CI widened per "
                           "O-1342 sec-2); NO_EVIDENCE states reported as-is, no waiver"),
        "widest_state_ci": {"state": widest[0], "ci95_width": widest[1]} if widest else None,
        "min_windows_gate": {"min_n_days": PROFILE_MIN_N_DAYS,
                             "min_independent_regime_windows": PROFILE_MIN_EPISODES,
                             "source": "PROFILE_CARDS_P1 sec-3.1 frozen verbatim "
                                       "-- carried, not changed"},
        "ci_face": ("sharpe_ci95 stationary bootstrap (science_gates.bootstrap_ci_sharpe "
                    "verbatim, seed 20260923, block 10, 1000 resamples)"),
        "decay_baseline_note": ("per-state four-must = decay-probe readout baseline for "
                                "per-new-bar re-derivation (CI lower bound crossing below 0 / "
                                "window-count shrinkage = OOS-decay evidence flag; disclosed, "
                                "not auto-kill -- slice-1 sec-4 cost_fragile precedent)"),
    }


def _profile_heat_attr(day_seq):
    """热档归属=前收市档（shift(1)，§1 镜像州惯例）；build_heat=market_clock_backtest
    s1 冻结法逐字复用（LHB H_act/H_net/p80 尾250），零重实现。窗首日无前收市=n/a。"""
    import pandas as pd
    import market_clock_backtest as _mcb
    ts = pd.DatetimeIndex(pd.to_datetime(list(day_seq)))
    heat = _mcb.build_heat(pd.DataFrame(index=ts))
    by_date = {d.strftime("%Y-%m-%d"): v[3] for d, v in heat.items()}
    attr, prev = {}, None
    for d in day_seq:
        attr[d] = by_date.get(prev)
        prev = d
    return attr


def _t22_long_face(corps_entry):
    """A 组长史面：t22 代理分类法（≠v3 如实标签），corps 冻结线逐字（零新线）。"""
    if not corps_entry:
        return {"state": "n/a",
                "note": "no corps_roster registered entry (blend/alloc lane)"}
    out = {}
    for seg, ev in (corps_entry.get("segments") or {}).items():
        br, n = ev.get("beat_rate_12m"), ev.get("n_startpoints") or 0
        dd = ev.get("worst_dd_all_windows")
        if br is None or n < 30:
            v = "NO_EVIDENCE"
        elif br < 0.5 or (dd is not None and dd <= -0.35):
            v = "DEAD_ZONE"
        else:
            v = "PASS"
        out[seg] = {"beat_rate_12m": br, "n_startpoints": n,
                    "beat_ci95_12m": ev.get("beat_ci95_12m"),
                    "worst_dd_all_windows": dd, "verdict": v}
    return {"state": "tested",
            "taxonomy": "t22 proxy (510300 x MA200) -- NOT v3, honest label",
            "rule": {"beat_rate_12m_line": 0.5, "min_n": 30, "blowup_line": -0.35,
                     "source": "results/corps_roster.json rule face (T-33 frozen lines verbatim)"},
            "passing_segments": corps_entry.get("passing_segments"),
            "segments": out}


def _profile_kill_conditions(family, account):
    """§4 击杀条件申报（预注册读数+衰减探针载体，全既有面零新监视器）。"""
    hr_fire = ["paper_dd>20%", "live_monthly_loss<-8% (single live/paper month)",
               "ic_decay>50%", "risk_violation"]
    rederive = "profile_cards re-derivation per new bar (this face, three-card run carrier)"
    if family == "A":
        declared = {"hr_fire_faces": hr_fire}   # firm/hr.py FIRE_REASONS 逐字
        if account in COST_RAZOR_MARGINS:
            declared["x2_margin_razor"] = {
                "frozen_margin": COST_RAZOR_MARGINS[account],
                "kill_reading": "x2 margin <= 0 (cost-razor; firm/OPERATING_PLAN sec-2)"}
        else:
            declared["cost_fragile_flag"] = ("x2 window cum <= 0 while x1 > 0 "
                                             "(disclosed, not auto-kill)")
        return {"declared": declared,
                "probe_carriers": ["firm/hr.py run_review (auto-fire, wired)",
                                   "live.paper x2_watch/cost_x2_check (monthly auto)",
                                   rederive]}
    declared = {
        "paper_month_loss": "single paper month < -8% (hr live_monthly_loss line mirrored at account level)",
        "activation_set_empty": "all states NO_EVIDENCE/DEAD_ZONE on re-derivation -> not running anywhere (fail-closed)",
        "state_mismatch_demotion": "slice-2 L3 activation-table wiring hook (declared here, wired in slice-2)"}
    return {"declared": declared,
            "probe_carriers": ["marks monthly re-derivation (aggressive_lab.py paper / alloc_paper.py lanes)",
                               rederive]}


def profile_card(account, ledger, states_by_date, state_seq, day_seq, heat_attr,
                 canon_cums, corps_entry):
    """单候选适用域画像卡（readout-only，无总分——O-1342 §一 万金油禁令）。"""
    x1 = ledger.get("x1") or {}
    family = ledger.get("family") or "?"
    rets = _profile_returns(x1.get("dates"), x1.get("equity_cny"),
                            ledger.get("initial_cash_cny"))
    x2 = ledger.get("x2") if isinstance(ledger.get("x2"), dict) else None
    rets_x2 = _profile_returns((x2 or {}).get("dates"), (x2 or {}).get("equity_cny"),
                               ledger.get("initial_cash_cny")) if x2 else []
    x2_label = None if x2 else "n/a (alloc v2 cost face carried in x1 by construction, retro prereg sec-3)"
    by_state = {s: [] for s in PROFILE_STATES}
    by_cell = {}
    for d, r in rets:
        s = states_by_date.get(d, "UNKNOWN")
        by_state.setdefault(s, []).append((d, r))
        h = heat_attr.get(d)
        if h:
            by_cell.setdefault((s, h), []).append((d, r))
    by_state_x2 = {s: [] for s in PROFILE_STATES}
    for d, r in rets_x2:
        s = states_by_date.get(d, "UNKNOWN")
        by_state_x2.setdefault(s, []).append((d, r))
    state_ep = _profile_episodes(state_seq)
    cell_ep = _profile_episodes([(states_by_date.get(d, "UNKNOWN"), heat_attr.get(d))
                                 for d in day_seq])
    trades = x1.get("trades")
    trades_by_state = {}
    if isinstance(trades, list):
        for t in trades:
            s = states_by_date.get(t.get("date"), "UNKNOWN")
            trades_by_state[s] = trades_by_state.get(s, 0) + 1
    trades_by_cell = {}   # T-81 slice-3：格面逐笔归属（州×前收市热档，同收益归属律）
    if isinstance(trades, list):
        for t in trades:
            d = t.get("date")
            key = (states_by_date.get(d, "UNKNOWN"), heat_attr.get(d))
            trades_by_cell[key] = trades_by_cell.get(key, 0) + 1
    states = {}
    for s in PROFILE_STATES:
        rs = by_state.get(s) or []
        cum = _cum_of(rs)
        excess = cum - (canon_cums.get(s) or 0.0)
        states[s] = {
            "n_days": len(rs), "episodes": state_ep.get(s, 0),
            "cum_ret_x1": round(cum, 6),
            "cum_ret_x2": (round(_cum_of(by_state_x2.get(s) or []), 6)
                           if x2 else None),
            "excess_vs_canon": round(excess, 6),
            "worst_day": (round(min(r for _d, r in rs), 6) if rs else None),
            "n_trades": (trades_by_state.get(s) if isinstance(trades, list)
                         else ("n/a (blend/alloc face: no dated trade list)" if s in states_by_date else None)),
            "verdict": _profile_verdict(len(rs), state_ep.get(s, 0), cum, excess)}
        states[s].update(_four_must_cell(   # SAMPLE_SCIENCE_P1 §1 四必报（slice-3 披露面）
            rs, trades_by_state.get(s) if isinstance(trades, list) else None,
            state_ep.get(s, 0)))
    heat_cells = {}
    for (s, h), rs in sorted(by_cell.items()):
        cum = _cum_of(rs)
        heat_cells[f"{s}x{h}"] = {
            "n_days": len(rs), "episodes": cell_ep.get((s, h), 0),
            "cum_ret_x1": round(cum, 6),
            "verdict": _profile_verdict(len(rs), cell_ep.get((s, h), 0), cum, cum)}
        heat_cells[f"{s}x{h}"].update(_four_must_cell(
            rs, trades_by_cell.get((s, h)) if isinstance(trades, list) else None,
            cell_ep.get((s, h), 0)))
    activation = [s for s in PROFILE_STATES if states[s]["verdict"] == "PASS"]
    dead = [s for s in PROFILE_STATES if states[s]["verdict"] == "DEAD_ZONE"]
    noev = [s for s in PROFILE_STATES if states[s]["verdict"] == "NO_EVIDENCE"]
    cost_fragile = any(states[s]["cum_ret_x1"] > 0 and states[s]["cum_ret_x2"] is not None
                       and states[s]["cum_ret_x2"] <= 0 for s in PROFILE_STATES)
    return {
        "account": account, "family": family, "readout_only": True,
        "no_composite_total": "O-1342 sec-1: overall = derived index view only (never deployment basis)",
        "window_note": "2026-01-05..2026-09-24 replay window overlaps OOS dev window (retro prereg sec-4 annotation verbatim)",
        "x2_face": x2_label or "V1 legacy x2 cost face",
        "states": states, "heat_cells": heat_cells,
        "activation_set": activation, "dead_zones": dead, "no_evidence_states": noev,
        "all_state_claim": ("ALL-STATE-PASS: default-suspect (O-1342 sec-1.3) + widest-CI disclosure required"
                            if len(activation) == 4 else
                            "not claimed (activation set < 4 states; in-window ORANGE/RED zero-day = structurally impossible)"),
        "long_face_t22": _t22_long_face(corps_entry),
        "kill_conditions": _profile_kill_conditions(family, account),
        "sample_science": _sample_science_block(
            rets, states_by_date, state_seq,
            len(trades) if isinstance(trades, list) else None, states),
        "cost_fragile_flag": bool(cost_fragile),
        "window_cum_x1": round(_cum_of(rets), 6),
        "window_cum_x2": (round(_cum_of(rets_x2), 6) if rets_x2 else None),
    }


def build_profile_cards():
    """T-81 slice-1：17 候选适用域画像卡（读数派生面，零新回测）。缺件/失配=诚实拒发。"""
    import glob as _glob
    retro_dir = os.path.join(RESULTS, "retro_paper_2026")
    paths = sorted(_glob.glob(os.path.join(retro_dir, "*_ledger.json")))
    if not paths:
        return {"state": "absent", "note": "retro ledgers not delivered (T-79 face)"}
    ledgers = {}
    for p in paths:
        acc = os.path.basename(p)[:-len("_ledger.json")]
        d = _load(p)
        if d and d.get("complete") and d.get("x1"):
            ledgers[acc] = d
    if "B_MAXDIV" not in ledgers:
        return {"state": "absent", "note": "canon B_MAXDIV ledger missing"}
    variants = {}
    for acc, d in ledgers.items():   # 市场级 v3 序列恒等门（§1）
        s = d.get("shadow_regime_states")
        if s:
            variants[acc] = json.dumps(s, sort_keys=True)
    if not variants:
        return {"state": "absent", "note": "no shadow_regime_states in any ledger"}
    if len(set(variants.values())) != 1:
        return {"state": "inconsistent",
                "note": "market-level v3 series differ across ledgers (invariant broken)"}
    carrier = sorted(variants)[0]
    shadow = ledgers[carrier]["shadow_regime_states"]
    day_seq = [row["date"] for row in shadow]
    states_by_date = {row["date"]: row["state"] for row in shadow}
    state_seq = [row["state"] for row in shadow]
    for acc, d in ledgers.items():   # 日期集恒等门
        if (d.get("x1") or {}).get("dates") != day_seq:
            return {"state": "inconsistent",
                    "note": "ledger date-set differs from shadow series: " + acc}
    heat_attr = _profile_heat_attr(day_seq)
    canon = ledgers["B_MAXDIV"]
    canon_cums = _state_cums(_profile_returns(canon["x1"].get("dates"),
                                              canon["x1"].get("equity_cny"),
                                              canon.get("initial_cash_cny")),
                             states_by_date)
    corps = _load(os.path.join(RESULTS, "corps_roster.json")) or {}
    registered = {m.get("member"): m for m in (corps.get("registered") or [])}
    cards = {acc: profile_card(acc, ledgers[acc], states_by_date, state_seq, day_seq,
                               heat_attr, canon_cums, registered.get(acc))
             for acc in sorted(ledgers)}
    # §3.4 自洽门（v1.0.1 判据感知式）：T-79 分段面对 day-1 收益存在家族异质惯例
    # （A=engine 零收益日/B=marks 含 day-1/C=alloc 剔首日）→ 双惯例择一恒等+披露。
    mixed = any(s in ("ORANGE", "RED") for s in state_seq)
    gate = {"mode": "skip (mixed-state window: ORANGE/RED bull/chop mapping unverified)"
            if mixed else "assert (GREEN==bull, YELLOW==chop, tol 1e-9, day1-convention aware)"}
    if not mixed:
        conventions = {}
        for acc in sorted(cards):
            segs = (ledgers[acc].get("x1") or {}).get("regime_segments") or {}
            rets_all = _profile_returns((ledgers[acc].get("x1") or {}).get("dates"),
                                        (ledgers[acc].get("x1") or {}).get("equity_cny"),
                                        ledgers[acc].get("initial_cash_cny"))
            bases = {"with_day1": _state_cums(rets_all, states_by_date),
                     "without_day1": _state_cums(rets_all[1:], states_by_date)}
            matched = None
            for name, base in bases.items():
                ok = True
                for st_key, seg_key in (("GREEN", "bull"), ("YELLOW", "chop")):
                    ref = (segs.get(seg_key) or {}).get("cum_ret")
                    mine = round(base[st_key], 6)   # 台账分段面=6dp 舍入发布值，同基准比
                    if ref is None or abs(ref - mine) > 2e-6:
                        ok = False   # 2e-6=跨算术路径容差（逐日积 vs 台账内部累算，实测噪声 ~5e-7；
                        break        # 真实错切差≥1e-4 量级=仍全被门捕获）
                if ok:
                    matched = name
                    break
            if matched is None:
                return {"state": "consistency_failed",
                        "note": "self-consistency gate: %s no day1-convention reproduces "
                                "ledger bull/chop (both mismatch)" % acc}
            conventions[acc] = matched
        gate["conventions"] = conventions
        gate["result"] = "PASS %d/%d" % (len(cards), len(cards))
    board = _load(os.path.join(retro_dir, "LEADERBOARD.json")) or {}
    absent = dict(board.get("absent_families") or {})
    for member in ("AGGR-MOM", "AGGR-NOCASH"):
        if member not in ledgers:
            absent[member] = ("no retro ledger (T-79 B-group = CEO-named top-3); "
                              "marks since 09-24 = no state face -> NO_EVIDENCE by construction")
    absent["CN (T-73)"] = ("first batch CN-REV-TILT-P1 harvested NEGATIVE 4/4 G1v2 "
                           "(bm-a r248); further CN models in flight -- landing-hook per O-1342 sec-4 item-4")
    verdict_counts = {s: {} for s in PROFILE_STATES}
    for c in cards.values():
        for s in PROFILE_STATES:
            v = c["states"][s]["verdict"]
            verdict_counts[s][v] = verdict_counts[s].get(v, 0) + 1
    try:
        with open(PROFILE_PREREG, "rb") as f:
            sha16 = hashlib.sha256(f.read()).hexdigest()[:16]
    except OSError:
        sha16 = None
    try:
        with open(SAMPLE_SCIENCE_PREREG, "rb") as f:
            ss_sha16 = hashlib.sha256(f.read()).hexdigest()[:16]
    except OSError:
        ss_sha16 = None
    return {
        "state": "ok", "batch": "PROFILE-CARDS-P1", "ticket": "T-2026-09-26-81",
        "order": "O-20260926-1342",
        "prereg": "research/PROFILE_CARDS_P1.md", "prereg_sha256_16": sha16,
        "sample_science_prereg": "research/SAMPLE_SCIENCE_P1.md",
        "sample_science_prereg_sha256_16": ss_sha16,
        "evidence_cutoff": board.get("evidence_cutoff") or "2026-09-24",
        "cutoff_source": "results/retro_paper_2026/LEADERBOARD.json (T-79 frozen batch face)",
        "state_carrier": carrier,
        "canon": "B_MAXDIV",
        "lines": {"min_n_days": PROFILE_MIN_N_DAYS, "min_episodes": PROFILE_MIN_EPISODES,
                  "pass_line": "cum_x1>0 AND excess_vs_canon>=0 (double line, frozen)",
                  "taxonomy": "v3 four-state (ledger shift(1) causal) x LHB heat v0 (shift(1) attribution)",
                  "ledger_policy": "append_ledger +0 (readout/derivation face, T-56 slice-2 paradigm)"},
        "absent_families": absent,
        "self_consistency_gate": gate,
        "cards": cards,
        "summary": {"n_cards": len(cards),
                    "n_with_activation": sum(1 for c in cards.values() if c["activation_set"]),
                    "activation_sets": {a: c["activation_set"] for a, c in cards.items()},
                    "state_verdict_counts": verdict_counts},
    }


# ———————————————— 落地钩子（T-81 slice-4 · O-20260926-1342 §四④ · LANDING_HOOKS_P1）————————————————
# 预注册冻结: research/LANDING_HOOKS_P1.md（判线零改动=三族自家冻结判词面逐字消费）。
# 落地=晋升级正面判定（CN/GRID/WILD 各自冻结判词位）；观察 marks 车道≠落地；
# 落地≠激活（激活仍走 profile_cards 逐州证据门×L3 格证据门，O-1342 §一.4 fail-closed 镜像）。

def landing_hooks(results_dir=None):
    """T-81 slice-4：三族落地判定+落地后画像管线动作契约（读数派生面，零判定线）。
    缺件=ABSENT 诚实态（fail-closed，禁默认落地）；hermetic 夹具经 results_dir 注入。"""
    import glob as _glob
    rd = results_dir or RESULTS
    # — GRID 族（T-78）：grid_sleeve_p1.json 判词面（s5b verbatim：science survivor
    #   =G1'v2 AND GATE-A；paper candidacy 另需 D6<0.70 注册面）；观察账户≠落地 —
    grid = _load(os.path.join(rd, "grid_sleeve_p1.json"))
    if isinstance(grid, dict) and "survivors_science" in grid:
        surv = grid.get("survivors_science") or []
        cand = grid.get("paper_candidates") or []
        grid_rec = {
            "state": "ok",
            "judgment_face": "results/grid_sleeve_p1.json (T-78 s5b verdict verbatim)",
            "n_survivors_science": len(surv),
            "n_paper_candidates": len(cand),
            "observation_lane_note": ("GRID-* paper marks accounts = observation lane, NOT "
                                      "landing (O-20260926-0958 unlock-4 + PROFILE_CARDS_P1 sec.0)"),
            "landings": [c.get("code") if isinstance(c, dict) else str(c) for c in cand],
        }
        if surv and not cand:
            grid_rec["intermediate"] = "SURVIVORS_NO_CANDIDACY"
    else:
        grid_rec = {"state": "ABSENT",
                    "note": "results/grid_sleeve_p1.json missing/unreadable -> fail-closed",
                    "landings": []}
    # — CN 族（T-73 s3 五模型链）：cn_*/p1_results.json g1'v2 pass 位（≥1 pass=最佳 cell
    #   过线=该模型判正；CN-GRID-SLEEVE 与 GRID 族同件，经 grid 判词面共享读） —
    cn = {"judgment_face": "results/cn_*/p1_results.json (g1_prime_v2 pass bits) + grid face "
                           "for CN-GRID-SLEEVE",
          "models": {}, "landings": []}
    for p in sorted(_glob.glob(os.path.join(rd, "cn_*", "p1_results.json"))):
        model = "CN-" + os.path.basename(os.path.dirname(p))[3:].upper().replace("_", "-")
        g1 = (_load(p) or {}).get("g1_prime_v2")
        if not isinstance(g1, dict) or not g1:
            cn["models"][model] = {"state": "ABSENT",
                                   "note": "product unreadable / no g1 face (fail-closed)"}
            continue
        n_pass = sum(1 for v in g1.values() if isinstance(v, dict) and v.get("pass"))
        rec = {"state": "ok", "n_cells": len(g1), "n_pass": n_pass}
        if n_pass:
            rec["landing_cells"] = [k for k, v in g1.items()
                                    if isinstance(v, dict) and v.get("pass")]
            cn["landings"].append(model)
        cn["models"][model] = rec
    if grid_rec["state"] == "ok":
        cn["models"]["CN-GRID-SLEEVE"] = {
            "state": "ok",
            "judgment_face": "results/grid_sleeve_p1.json (shared with GRID family)",
            "n_survivors_science": grid_rec["n_survivors_science"],
            "n_paper_candidates": grid_rec["n_paper_candidates"],
        }
        if grid_rec["landings"]:
            cn["landings"].append("CN-GRID-SLEEVE")
    else:
        cn["models"]["CN-GRID-SLEEVE"] = {"state": "ABSENT",
                                          "note": "grid face absent (shared with GRID family)"}
    cn["state"] = "ok" if any(m.get("state") == "ok" for m in cn["models"].values()) else "ABSENT"
    # — WILD 族（T-57）：wild_route_s1.json g1'v2 pass 位（幸存者=未来 satellite 袖供给面） —
    w1 = (_load(os.path.join(rd, "wild_route", "wild_route_s1.json")) or {}).get("g1_prime_v2")
    if isinstance(w1, dict) and w1:
        n_pass = sum(1 for v in w1.values() if isinstance(v, dict) and v.get("pass"))
        wrec = {"state": "ok",
                "judgment_face": "results/wild_route/wild_route_s1.json",
                "n_cells": len(w1), "n_pass": n_pass, "landings": []}
        if n_pass:
            wrec["landing_cells"] = [k for k, v in w1.items()
                                     if isinstance(v, dict) and v.get("pass")]
            wrec["landings"] = list(wrec["landing_cells"])
    else:
        wrec = {"state": "ABSENT",
                "note": "results/wild_route/wild_route_s1.json missing/unreadable -> fail-closed",
                "landings": []}
    fam = {"CN (T-73 s3 five-model chain)": cn,
           "GRID (T-78 grid sleeve)": grid_rec,
           "WILD (T-57 wild-route)": wrec}
    landed = [{"family": fname, "member": m}
              for fname, rec in fam.items() for m in rec.get("landings", [])]
    action_required = [{"action": "profile on landing (O-1342 sec.4 item-4)",
                        "family": e["family"], "member": e["member"],
                        "pipeline": "marks/paper ledger -> results/retro_paper_2026/"
                                    "*_ledger.json -> build_profile_cards auto-inclusion "
                                    "(no ledger yet = LANDED_AWAITING_LEDGER honest "
                                    "intermediate, no fabricated card)",
                        "activation_note": "landing != activation; activation still requires "
                                           "per-state PASS evidence gate x L3 cell evidence "
                                           "gate x design nomination (fail-closed)"}
                       for e in landed]
    board = _load(os.path.join(rd, "retro_paper_2026", "LEADERBOARD.json")) or {}
    try:
        with open(LANDING_HOOKS_PREREG, "rb") as f:
            lh_sha16 = hashlib.sha256(f.read()).hexdigest()[:16]
    except OSError:
        lh_sha16 = None
    return {
        "batch": "LANDING-HOOKS-P1", "ticket": "T-2026-09-26-81", "order": "O-20260926-1342",
        "prereg": "research/LANDING_HOOKS_P1.md", "prereg_sha256_16": lh_sha16,
        "evidence_cutoff": board.get("evidence_cutoff") or "2026-09-24",
        "cutoff_source": "results/retro_paper_2026/LEADERBOARD.json (T-79 frozen batch face)",
        "philosophy": "landing = promotion-grade positive judgment per each family's own "
                      "frozen prereg (verbatim consumption, zero new criteria); observation "
                      "marks lane is NOT landing; landing != activation",
        "families": fam,
        "landed": landed,
        "action_required": action_required,
        "summary": {"n_landings": len(landed),
                    "hook_state": "armed" if not landed else "FIRED",
                    "cadence": "re-derived on every strategy_scorecard refresh (S6 chain "
                               "wiring); L3 no-member sleeve structural labels cite this face"},
    }


# ———————————————— 装配 ————————————————

def build(strategy_payload, corps, papers, g25s, pbt, iv6, ew6, spm_j4, stable, pbo):
    registered_face = {m["member"]: m for m in (corps or {}).get("registered", [])}
    prospect_face = (corps or {}).get("prospect", [])
    cards_t, cards_p = {}, {}

    for tid, sc_card in (strategy_payload.get("per_trader") or {}).items():
        papersrc = papers.get(tid)
        g25 = g25s.get(tid)
        corps_entry = registered_face.get(tid)
        if papersrc is None and corps_entry is None and g25 is None:
            continue
        cards_t[tid] = trader_card(tid, sc_card, corps_entry, papersrc, g25)
    for p in prospect_face:
        tid = p.get("member")
        ev = p.get("evidence") or {}
        pseudo = {  # PROSPECT 策略继承面：在册证据读数 (corps prospect face recorded_*)
            "total": None, "grade": None, "veto_clean": None,
            "dims": {"recorded_oos_sharpe": ev.get("recorded_oos_sharpe"),
                     "recorded_x2_full_sharpe": ev.get("recorded_x2_full_sharpe"),
                     "recorded_oos_trades": ev.get("recorded_oos_trades"),
                     "recorded_max_dd": ev.get("recorded_max_dd"),
                     "g2_neighborhood_pass": ev.get("g2_neighborhood_pass"),
                     "g2_cost_x3_pass": ev.get("g2_cost_x3_pass"),
                     "g2_per_year_pass": ev.get("g2_per_year_pass"),
                     "g2_worst_year": ev.get("g2_worst_year")},
            "source": "results/corps_roster.json prospect face (recorded evidence readout)"}
        cards_t[tid] = trader_card(tid, pseudo, p, None, None)

    verdict = (pbt or {}).get("verdict") or {}
    cands = (pbt or {}).get("candidates") or {}
    corr = (pbt or {}).get("candidate_return_corr") or {}
    weights = (pbt or {}).get("weights") or {}
    ledger = pbt.get("trials_ledger") if pbt else None
    for method in ("A_IV", "B_MAXDIV", "C_IVMOM", "D_REGIME", "E_EW"):
        cards_p[method] = portfolio_card_tournament(
            method, cands.get(method), (verdict.get("faces") or {}).get(method),
            corr.get(method), weights.get(method), ledger)
    if iv6:
        cards_p["IV6"] = portfolio_card_iv6("IV6", iv6, iv6.get("head_to_head"),
                                           iv6.get("trials_ledger"))
    if ew6:
        cards_p["EW6"] = portfolio_card_iv6("EW6", ew6, None, ew6.get("trials_ledger"))

    j4_note = None
    if spm_j4:
        j4_note = {"state": "pointer", "batch": spm_j4.get("batch"),
                   "evidence_cutoff": spm_j4.get("evidence_cutoff")}
    stable_note = None
    if stable:
        stable_note = {"verdict": stable.get("verdict"),
                       "judgments": stable.get("judgments")}
    pbo_note = None
    if pbo:
        pbo_note = {"module": pbo.get("module"),
                    "live_fire": pbo.get("live_fire")}

    veto_hits = {tid: c["discipline"].get("veto")
                 for tid, c in cards_t.items() if c["discipline"].get("veto")}
    return {"trader_cards": cards_t, "portfolio_cards": cards_p,
            "cross_period_shared": {"spm_j4": j4_note, "stable_profit": stable_note,
                                    "pbo_cscv": pbo_note},
            "discipline_veto_hits": veto_hits}


def run(out_path=OUT_DEFAULT):
    t0 = time.time()
    strategy_payload = sc.run(sc.OUT_DEFAULT)   # 策略卡随刷（v1.0 引擎复用）
    corps = _load(os.path.join(RESULTS, "corps_roster.json"))
    papers, g25s = {}, {}
    pdir = os.path.join(RESULTS, "paper")
    if os.path.isdir(pdir):
        for fn in os.listdir(pdir):
            if fn.endswith("_paper.json"):
                d = _load(os.path.join(pdir, fn))
                if d:
                    papers[d.get("trader")] = d
    gdir = os.path.join(RESULTS, "g25")
    if os.path.isdir(gdir):
        for fn in os.listdir(gdir):
            if fn.endswith(".json") and not fn.startswith("_"):
                d = _load(os.path.join(gdir, fn))
                if d and d.get("trader"):
                    g25s[d["trader"]] = d
    built = build(strategy_payload, corps, papers, g25s,
                  _load(os.path.join(RESULTS, "portfolio_blend_tournament.json")),
                  _load(os.path.join(RESULTS, "portfolio_iv6.json")),
                  _load(os.path.join(RESULTS, "portfolio_ew6.json")),
                  _load(os.path.join(RESULTS, "spm_j4_attribution.json")),
                  _load(os.path.join(RESULTS, "current_market_stable_profit.json")),
                  _load(os.path.join(RESULTS, "pbo_cscv_v1.json")))
    calib = _load_calib_for_emission()
    if calib:
        _attach_composites(built["trader_cards"], calib["tw"], calib["tb"],
                           trader_face_scores, TRADER_FACES)
        _attach_composites(built["portfolio_cards"], calib["pw"], calib["pb"],
                           portfolio_face_scores, PORTFOLIO_FACES)
    profile_face = build_profile_cards()
    hooks_face = landing_hooks()
    payload = {
        "ticket": "T-2026-09-25-63", "order": "O-20260925-1755",
        "charter": "firm/STRATEGY_EVALUATION.md v2.0 (sec 2/6/7/8)",
        "generated": _dt.datetime.now().isoformat(timespec="seconds"),
        "naming_reconciliation": "charter sec.4 names strategy_scorecard.py/json; T-07 "
                                 "delivered the strategy face as scripts/scorecard.py -> "
                                 "results/scorecard_v1.json (disclosed in that file). This v2 "
                                 "file IS the charter-named three-card artifact: strategy face "
                                 "= reused engine (zero rebuild), trader/portfolio cards = new.",
        "calibration_state": ("calibrated (SCORECARD_CALIB_P1 frozen; evidence_cutoff "
                              + str((calib or {}).get("cutoff"))
                              + "): trader/portfolio composite totals & grades emitted from "
                              "frozen weight/band values (results/strategy_scorecard_calib."
                              "json); strategy-face totals = v1.0 frozen; discipline veto "
                              "faces gate the grade (sec 8.2). Evaluation never overrides "
                              "gates (sec 8.3)."
                              ) if calib else (
                              "pre-calibration: trader/portfolio cards are READOUT-ONLY "
                              "(sec 8.5); composite totals for these two faces require the "
                              "first-cohort calibration prereg (research/STRATEGY_SCORECARD_"
                              "CALIB.md) frozen THEN run. Strategy-face totals = v1.0 frozen."),
        "unified_law": {"sec8": ">=2-dimension decision basis; hard-veto faces universal; "
                                "evaluation never overrides gates; data-driven; "
                                "calibration-before-totals"},
        "strategy_face": {"source": "results/scorecard_v1.json (scripts/scorecard.py)",
                          "summary": strategy_payload.get("summary"),
                          "per_trader": strategy_payload.get("per_trader")},
        "trader_cards": built["trader_cards"],
        "portfolio_cards": built["portfolio_cards"],
        "profile_cards": profile_face,
        "landing_hooks": hooks_face,
        "cross_period_shared": built["cross_period_shared"],
        "discipline_veto_hits": built["discipline_veto_hits"],
        "summary": {"n_strategy_cards": len(strategy_payload.get("per_trader") or {}),
                    "n_trader_cards": len(built["trader_cards"]),
                    "n_portfolio_cards": len(built["portfolio_cards"]),
                    "trader_cohort": "6 registered + 22 PROSPECT (first-cohort per sec 8.5)",
                    "portfolio_cohort": "IV6/EW6 + tournament 5 methods (first-cohort)"},
        "audit": {"elapsed_sec": round(time.time() - t0, 1), "zero_new_backtests": True,
                  "zero_engine_runs": True, "ledger_delta": 0,
                  "calibration_consumed": bool(calib),
                  "sources": ["firm/traders/*.json (via scorecard.py)", "results/corps_roster.json",
                              "results/paper/*_paper.json", "results/g25/*.json",
                              "results/portfolio_blend_tournament.json",
                              "results/portfolio_iv6.json", "results/portfolio_ew6.json",
                              "results/spm_j4_attribution.json",
                              "results/current_market_stable_profit.json",
                              "results/pbo_cscv_v1.json",
                              "results/retro_paper_2026/*_ledger.json (profile_cards face, T-81)",
                              "results/cn_*/p1_results.json + results/grid_sleeve_p1.json + "
                              "results/wild_route/wild_route_s1.json (landing_hooks face, T-81 slice-4)",
                              "Money02/data/lhb/lhb_detail.parquet (heat via market_clock_backtest.build_heat)"]
                  + (["results/strategy_scorecard_calib.json (frozen bands)"] if calib else []),
                  "read_only_reuse": "CORR_WATCH/g25/t22/t27/t28/t33 readers per ticket anti-dup"},
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    os.replace(tmp, out_path)
    print("strategy_scorecard: %d strategy / %d trader / %d portfolio cards -> %s (%.1fs)"
          % (payload["summary"]["n_strategy_cards"], payload["summary"]["n_trader_cards"],
             payload["summary"]["n_portfolio_cards"], out_path, payload["audit"]["elapsed_sec"]))
    if built["discipline_veto_hits"]:
        print("  DISCIPLINE VETO (sec 8.2):", built["discipline_veto_hits"])
    return payload


def selftest():
    """离线合成夹具自检：生产形态镜像（r157/r162 配对律）+ 未测态传播 + 否决路径 + 读数卡律。"""
    # S1: 注册交易员卡 — 纸盘在场、纪律干净、g25 在册、corps 在册
    paper = {"trader": "T-A", "anchor_ok": True, "no_future_data": True,
             "months_tracked": 2, "monthly_returns": [0.01, 0.02], "current_dd": -0.01,
             "x2_watch": {"state": "ok"}, "cost_x2_check": True, "capital": 1000000,
             "regime_guard": {"breach": False}, "forward_guard": {"breach": False}}
    g25 = {"trader": "T-A", "verdict": "pass",
           "legs": {"dsr": {"value": 0.96, "gate": 0.95}, "ci": {"pass": True},
                    "pbo": {"status": "observe"}}}
    corps_entry = {"corps": "chop", "passing_segments": ["bear", "bull", "chop"],
                   "segments": {"bull": {"beat_rate_12m": 0.6}, "bear": {"beat_rate_12m": 0.55},
                                "chop": {"beat_rate_12m": 0.62}}}
    card = trader_card("T-A", {"total": 72.0, "grade": "A", "veto_clean": True,
                               "dims": {"1": {"score": 80}}}, corps_entry, paper, g25)
    assert card["inherited_strategy"]["total"] == 72.0
    assert card["live_paper"]["state"] == "tested" and card["live_paper"]["months_tracked"] == 2
    assert card["discipline"]["state"] == "tested" and not card["discipline"]["veto"]
    assert card["progress"]["g25_verdict"] == "pass"
    assert card["profile"]["corps"] == "chop"
    # S2: 未测态传播 — PROSPECT 无纸盘/无 g25 → 两面 ⬜, 继承面=录得证据读数
    prosp = trader_card("PROS-X", {"total": None, "grade": None, "veto_clean": None,
                                   "dims": {"recorded_oos_sharpe": 0.63}},
                        {"candidate_corps": "pending-classification", "evidence": {}},
                        None, None)
    assert prosp["live_paper"]["state"].startswith("⬜")
    assert prosp["discipline"]["state"].startswith("⬜")
    assert prosp["progress"]["state"].startswith("⬜")
    assert prosp["inherited_strategy"]["dims"]["recorded_oos_sharpe"] == 0.63
    # S3: 纪律否决路径 — anchor 漂移 + 未来数据旗 = 一票否决（§8.2 即刻生效）
    viol = trader_card("T-V", None, None,
                      {"anchor_ok": False, "no_future_data": False, "months_tracked": 1,
                       "monthly_returns": [0.01], "x2_watch": {}, "regime_guard": {"breach": True}},
                      None)
    assert viol["discipline"]["veto"] and set(viol["discipline"]["violations"]) == \
        {"paper_anchor_drift", "future_data_violation", "regime_guard_breach"}
    # S4: 组合卡（锦标赛形态）+ 未测面传播
    cand = {"x1": {"full": {"sharpe": 0.7, "annual_return": 0.014, "max_drawdown": -0.04},
                   "yearly": {"2020": 0.03}, "worst_year": -0.01},
            "x2": {"full": {"sharpe": 0.45}}}
    pc = portfolio_card_tournament("B_MAXDIV", cand, {"benefit": 0.66, "x2_margin": 0.21},
                                   {"B_MAXDIV": 1.0, "E_EW": 0.79},   # 行字典=生产调用形态
                                   {"weights": {"M1": 0.5, "M2": 0.5}},
                                   {"total": 3205, "batch_trials": 86})
    assert pc["quality"]["benefit"] == 0.66 and pc["cost"]["x2_full_sharpe"] == 0.45
    assert pc["marginal"]["max_abs_corr_vs_other_methods"] == 0.79
    assert pc["statistical"]["trials_ledger_total"] == 3205
    empty = portfolio_card_tournament("X", {}, None, None, None, None)
    assert empty["quality"]["state"].startswith("⬜") and empty["marginal"]["state"].startswith("⬜")
    # S5: 读数卡律 — 三卡恒无 composite total 键（校准前 §8.5）
    for c in (card, prosp, viol, pc, empty):
        assert "composite_total" not in c and "total" not in c
        assert c.get("readout_only") is True or c.get("no_composite_total")
    # S6: IV6 形态组合卡 — head_to_head 与权重面（r157 族双约定坑：_max_offdiag 吃行字典）
    iv6src = {"portfolios_iv": {"x1": {"full": {"sharpe": 1.37, "annual_return": 0.028,
                                                "max_drawdown": -0.05}, "weights": {"M1": 0.5}},
                                "x2": {"full": {"sharpe": 0.9}}},
              "iv_weights": {"weights": {"M1": 0.5}},
              "correlation": {"full": {"matrix": {"M1": {"M1": 1.0, "M2": 0.35}}}},
              "trials_ledger": {"total": 2779, "batch_trials": 14},
              "prereg_sha256_at_run": "abc", "void": False}
    iv6c = portfolio_card_iv6("IV6", iv6src, {"delta_benefit": 0.19}, iv6src["trials_ledger"])
    assert iv6c["quality"]["x1_full_sharpe"] == 1.37
    assert iv6c["marginal"]["max_abs_offdiag_member_corr"] == 0.35
    assert iv6c["statistical"]["trials_ledger_total"] == 2779
    # S7: 面分公式（生产形态镜像：cost_x2_check=dict insufficient_data / x2_watch=null）
    reg_card = trader_card("T-A", {"total": 72.0, "grade": "A", "veto_clean": True,
                                   "dims": {"1": {"score": 80}}}, corps_entry,
                           {"trader": "T-A", "anchor_ok": True, "no_future_data": True,
                            "months_tracked": 3, "monthly_returns": [0.01, 0.02, 0.03],
                            "current_dd": -0.10, "x2_watch": {"state": "ok"},
                            "cost_x2_check": True, "capital": 1, "paper_start": "2026-06-01",
                            "regime_guard": {"breach": False}, "forward_guard": {"breach": False}},
                           g25)
    fs = trader_face_scores(reg_card)
    assert fs["inherited"] == 72.0 and fs["_states"]["inherited"].startswith("tested")
    # 0.50*3/6 + 0.30*clamp(1+2*-0.1)=0.8 + 0.10 + 0.10 = 1.0*... -> 25+24+10+10=69
    assert fs["live_paper"] == 69.0, fs["live_paper"]
    # progress: verdict pass 60 + dsr(0.96>=0.95) 20 + ci 20 = 100
    assert fs["progress"] == 100.0
    # profile: 30 confirmed + 30*(3/3) + 40*mean(0.6,0.55,0.62)=40*0.59=23.6 -> 83.6
    assert fs["profile"] == 83.6, fs["profile"]
    assert not fs["_discipline_veto"]
    # 生产子字段形态：insufficient_data cost + null x2 -> 无 x2/cost 分（30*clamp(1+2*dd) only）
    prod_live = trader_face_scores(trader_card(
        "T-P", None, None,
        {"anchor_ok": True, "no_future_data": True, "months_tracked": 0,
         "monthly_returns": [], "current_dd": 0.0, "x2_watch": {"state": None},
         "cost_x2_check": {"status": "insufficient_data", "bars": 2, "min_bars": 20},
         "capital": 1, "paper_start": "2026-09-23",
         "regime_guard": {"breach": False}, "forward_guard": {"breach": False}}, None))
    assert prod_live["live_paper"] == 30.0, prod_live["live_paper"]
    # PROSPECT 继承面公式（prosp 夹具 dims 仅 recorded_oos_sharpe=0.63：legs 全 None->0）
    prosp_fs = trader_face_scores(prosp)
    assert prosp_fs["inherited"] == round(100.0 * 0.25 * 0.63 / 2, 1), prosp_fs["inherited"]
    assert prosp_fs["live_paper"] == 0.0 and prosp_fs["progress"] == 0.0 \
        and prosp_fs["profile"] == 0.0
    # 组合面分（夹具 pc：sharpe 0.7 / benefit 0.66 / x2 0.45 / margin 0.21 / corr 0.79）
    pfs = portfolio_face_scores(pc)
    assert pfs["quality"] == round(100.0 * (0.80 * 0.7 / 2 + 0.20 * 0.66), 1), pfs["quality"]
    assert pfs["cost"] == round(100.0 * (0.60 * 0.45 / 2 + 0.40 * 1.0), 1), pfs["cost"]
    assert pfs["segment_coverage"] == round(100.0 * min(1.0, 1 / 6.0), 1)  # yearly 1 年
    assert pfs["marginal"] == 0.0   # corr 0.79 >= 0.6 锚点 -> 0
    assert pfs["cross_period_j4"] == 0.0
    # S8: 权重分配冻结规则 — 跨度比例 + 帽 + 再分配 + 零跨度等分
    w = _allocate_weights("a", ["b", "c", "d"], {"b": 0.0, "c": 2.0, "d": 0.0})
    # c 拿满 0.60 -> 帽 0.50，超额 0.10 按 b/d 跨度(0/0)等分再分配
    assert w == {"a": 0.40, "b": 0.05, "c": 0.50, "d": 0.05}, w
    w2 = _allocate_weights("a", ["b", "c"], {"b": 1.0, "c": 1.0})   # 总跨度>0 等价比例
    assert abs(w2["b"] - 0.30) < 1e-9 and abs(w2["c"] - 0.30) < 1e-9
    w3 = _allocate_weights("a", ["b", "c"], {"b": 0.0, "c": 0.0})   # 零跨度 -> 等分
    assert abs(w3["b"] - 0.30) < 1e-9 and abs(w3["c"] - 0.30) < 1e-9
    w4 = _allocate_weights("a", ["b", "c", "d"], {"b": 10.0, "c": 0.1, "d": 0.1})
    # b 超帽：0.6*10/10.2=0.588->帽 0.50，超额按 c/d 跨度比例(各半)再分配
    assert w4 == {"a": 0.4, "b": 0.5, "c": 0.05, "d": 0.05}, w4
    assert abs(sum(w4.values()) - 1.0) < 1e-6 and max(w4.values()) <= 0.5
    # S9: 分级带分位法 + 否决覆盖（合成 10 员小队列）
    bands = {"S": round(_quantile(list(range(10, 20)), 0.80), 1),
             "A": round(_quantile(list(range(10, 20)), 0.60), 1),
             "B": round(_quantile(list(range(10, 20)), 0.40), 1)}
    # 线性插值分位：(n-1)*p 索引 -> 9*0.8=7.2 -> 17.2 等
    assert bands == {"S": 17.2, "A": 15.4, "B": 13.6}, bands
    assert _grade_of(19, bands, False) == "S" and _grade_of(15, bands, False) == "B"
    assert _grade_of(99, bands, True) == "VETO" and _grade_of(10, bands, False) == "C"
    # S10: calibrate() 端到端（合成生产形态 payload -> tmp 件，零真实写）
    import tempfile
    synth = {"generated": "2026-09-25T00:00:00", "audit": {"sources": []},
             "trader_cards": {}, "portfolio_cards": {}}
    for i in range(28):   # 镜像生产冻结队列：22 PROSPECT（低分团）+ 6 在册（高分团）
        if i < 22:
            synth["trader_cards"]["PROS-%02d" % i] = trader_card(
                "PROS-%02d" % i,
                {"total": None, "grade": None, "veto_clean": None,
                 "dims": {"g2_neighborhood_pass": i % 2 == 0, "g2_cost_x3_pass": False,
                          "g2_per_year_pass": True, "recorded_oos_sharpe": 0.2 + i * 0.05,
                          "recorded_x2_full_sharpe": 0.0}},
                {"candidate_corps": "pending-classification", "evidence": {}}, None, None)
        else:
            synth["trader_cards"]["REG-%02d" % i] = trader_card(
                "REG-%02d" % i, {"total": 70.0 + i, "grade": "A", "veto_clean": True,
                                 "dims": {}}, corps_entry,
                {"anchor_ok": True, "no_future_data": True, "months_tracked": 1,
                 "monthly_returns": [0.01], "current_dd": -0.02, "x2_watch": {"state": "ok"},
                 "cost_x2_check": True, "capital": 1, "paper_start": "2026-09-01",
                 "regime_guard": {"breach": False}, "forward_guard": {"breach": False}},
                g25)
    for i in range(7):
        synth["portfolio_cards"]["P%d" % i] = portfolio_card_tournament(
            "P%d" % i,
            {"x1": {"full": {"sharpe": 0.5 + i * 0.2, "annual_return": 0.01,
                             "max_drawdown": -0.04},
                    "yearly": {"2020": 0.03, "2021": 0.01}, "worst_year": -0.01},
             "x2": {"full": {"sharpe": 0.3 + i * 0.1}}},
            {"benefit": 0.2 + i * 0.1, "x2_margin": -0.3 + i * 0.08},
            {"P%d" % i: 0.3, "P6": 0.9} if i != 6 else {"P6": 0.9, "P0": 0.3},
            {"weights": {"M1": 0.5}}, {"total": 1000, "batch_trials": 10})
    with tempfile.TemporaryDirectory() as td:
        pin = os.path.join(td, "in.json")
        pout = os.path.join(td, "out.json")
        with open(pin, "w", encoding="utf-8") as f:
            json.dump(synth, f, ensure_ascii=False)
        rc = calibrate(in_path=pin, out_path=pout)
        assert rc == 0, rc
        cal = _load(pout)
        assert cal["cohorts"]["traders"]["n"] == 28 and cal["cohorts"]["portfolios"]["n"] == 7
        tw = cal["weights"]["traders"]
        assert abs(sum(tw.values()) - 1.0) < 1e-6 and max(tw.values()) <= 0.5
        assert tw["inherited"] == 0.40
        assert cal["grade_bands"]["traders"]["S"] >= cal["grade_bands"]["traders"]["A"] \
            >= cal["grade_bands"]["traders"]["B"]
        reg_totals = [cal["totals"]["traders"][t]["total"] for t in cal["totals"]["traders"]
                      if t.startswith("REG-")]
        pro_totals = [cal["totals"]["traders"][t]["total"] for t in cal["totals"]["traders"]
                      if t.startswith("PROS-")]
        assert min(reg_totals) > max(pro_totals), "double-clump violated in synthetic fixture"
        assert cal["audit"]["zero_new_backtests"] is True
        assert cal["audit"]["ledger_delta"] == 0
        assert cal["predictions_check"]["p3_s_band_registered_only"]["prediction_holds"] is True
        # 队列数不符 = 诚实拒写
        synth["trader_cards"].pop(next(iter(synth["trader_cards"])))
        with open(pin, "w", encoding="utf-8") as f:
            json.dump(synth, f, ensure_ascii=False)
        rc2 = calibrate(in_path=pin, out_path=os.path.join(td, "out2.json"))
        assert rc2 == 2 and not os.path.exists(os.path.join(td, "out2.json"))
    # S11: 启用门面 — 冻结带消费输出总分/分级（r157 配对律：交易员+组合双腿都测）
    fresh_reg = trader_card("T-A", {"total": 72.0, "grade": "A", "veto_clean": True,
                                    "dims": {"1": {"score": 80}}}, corps_entry, paper, g25)
    veto_card = trader_card(
        "T-V", {"total": 90.0, "grade": "S", "veto_clean": False, "dims": {}}, None,
        {"anchor_ok": False, "no_future_data": True, "months_tracked": 2,
         "monthly_returns": [0.01, 0.02], "current_dd": -0.02, "x2_watch": {"state": "ok"},
         "cost_x2_check": True, "capital": 1, "paper_start": "2026-08-01",
         "regime_guard": {"breach": False}, "forward_guard": {"breach": False}}, None)
    tw_fake = {"inherited": 0.40, "live_paper": 0.10, "progress": 0.20, "profile": 0.30}
    tb_fake = {"S": 50.0, "A": 14.0, "B": 10.0}
    cards11 = {"T-A": fresh_reg, "T-V": veto_card}
    _attach_composites(cards11, tw_fake, tb_fake, trader_face_scores, TRADER_FACES)
    fs11 = trader_face_scores(fresh_reg)   # S1 paper 夹具实值钉住
    assert (fs11["inherited"], fs11["live_paper"], fs11["progress"],
            fs11["profile"]) == (72.0, 66.1, 100.0, 83.6), fs11
    assert not fs11["_discipline_veto"]
    exp_t = round(sum(w * fs11[f] for f, w in tw_fake.items()), 1)
    ca = cards11["T-A"]["composite"]
    assert ca["total"] == exp_t and ca["grade"] == "S", (ca["total"], exp_t)
    assert cards11["T-A"]["readout_only"] is False
    assert "no_composite_total" not in cards11["T-A"]
    assert cards11["T-V"]["composite"]["grade"] == "VETO"      # §8.2 否决覆盖分级
    assert cards11["T-V"]["composite"]["veto"] is True
    pc11 = portfolio_card_tournament("B_MAXDIV", cand, {"benefit": 0.66, "x2_margin": 0.21},
                                    {"B_MAXDIV": 1.0, "E_EW": 0.79},
                                    {"weights": {"M1": 0.5, "M2": 0.5}},
                                    {"total": 3205, "batch_trials": 86})
    pw_fake = {"quality": 0.40, "cost": 0.30, "segment_coverage": 0.10,
               "cross_period_j4": 0.0, "marginal": 0.10, "statistical": 0.10}
    pb_fake = {"S": 40.0, "A": 25.0, "B": 15.0}
    pcards11 = {"B_MAXDIV": pc11}
    _attach_composites(pcards11, pw_fake, pb_fake, portfolio_face_scores, PORTFOLIO_FACES)
    pf = portfolio_face_scores(pc11)
    exp_p = round(sum(w * pf[f] for f, w in pw_fake.items()), 1)
    assert pcards11["B_MAXDIV"]["composite"]["total"] == exp_p
    assert pcards11["B_MAXDIV"]["composite"]["grade"] == "S"
    # 纯函数新建卡 = 仍读数态（启用门不改变纯函数契约，S5 律恒真）
    pfx = trader_card("T-X", {"total": 50.0, "grade": "B", "veto_clean": True, "dims": {}},
                      None, None, None)
    assert pfx.get("readout_only") is True and "composite" not in pfx
    # —————— T-81 画像卡腿（PROFILE_CARDS_P1 §3 冻结线合成夹具 + 在位实腿）——————
    # P1: 收益日序列口径 — r0=eq[0]/initial−1（A 组 hire 日=0），逐日积=台账 cum
    rets_p = _profile_returns(["d0", "d1", "d2"], [100.0, 110.0, 99.0], 100.0)
    assert [round(r, 9) for _d, r in rets_p] == [0.0, 0.1, -0.1], rets_p
    assert abs(_cum_of(rets_p) - (99.0 / 100.0 - 1.0)) < 1e-12
    # P2: 独立政体窗计数 — [G,G,Y,G] -> G:2, Y:1
    assert _profile_episodes(["G", "G", "Y", "G"]) == {"G": 2, "Y": 1}
    # P3: 判定线 — 小样本/单段 fail-closed；双线过=PASS；亏钱或跑输正典=DEAD_ZONE
    assert _profile_verdict(15, 2, 0.05, 0.03) == "NO_EVIDENCE"      # n<20
    assert _profile_verdict(25, 1, 0.05, 0.03) == "NO_EVIDENCE"      # 单段=零复制
    assert _profile_verdict(25, 2, 0.05, 0.03) == "PASS"
    assert _profile_verdict(25, 2, -0.02, 0.03) == "DEAD_ZONE"       # 绝对线败
    assert _profile_verdict(25, 2, 0.01, -0.01) == "DEAD_ZONE"       # 正典线败
    # P4: 合成台账全链 — GREEN 24 日双段正收益+跑赢正典=PASS；YELLOW 5 日=NO_EVIDENCE
    #     （n<20 fail-closed）；ORANGE/RED 零日=NO_EVIDENCE；热档 shift(1) 归属；万金油主张不成立
    days_p = ["2026-01-%02d" % (i + 1) for i in range(29)]
    states_seq_p = ["GREEN"] * 12 + ["YELLOW"] * 5 + ["GREEN"] * 2 + ["GREEN"] * 10
    sbd_p = dict(zip(days_p, states_seq_p))
    rets_by_day = [0.01] * 12 + [-0.01] * 5 + [0.01] * 12
    eq_p, e = [], 100.0 * (1.0 + rets_by_day[0])
    eq_p.append(e)
    for r in rets_by_day[1:]:
        e *= (1.0 + r)
        eq_p.append(e)
    heat_day_p = {days_p[3]}                     # d4 收市 HOT -> d5 归属 GREENxHOT
    heat_attr_p = {days_p[i]: (("HOT" if days_p[i - 1] in heat_day_p else "COOL")
                               if i else None) for i in range(len(days_p))}
    ledger_p = {"family": "B", "initial_cash_cny": 100.0,
                "x1": {"dates": days_p, "equity_cny": eq_p, "trades": None},
                "x2": {"dates": days_p, "equity_cny": [v * 0.999 for v in eq_p]}}
    canon_p = {"GREEN": 0.001, "YELLOW": 0.001}  # 正典同州 +0.1%（被跑赢）
    card_p = profile_card("SYN-B", ledger_p, sbd_p, states_seq_p, days_p,
                          heat_attr_p, canon_p, None)
    assert card_p["states"]["GREEN"]["verdict"] == "PASS", card_p["states"]["GREEN"]
    assert card_p["states"]["GREEN"]["n_days"] == 24
    assert card_p["states"]["GREEN"]["episodes"] == 2
    assert card_p["states"]["YELLOW"]["verdict"] == "NO_EVIDENCE"   # n<20 fail-closed
    assert card_p["states"]["ORANGE"]["n_days"] == 0
    assert card_p["states"]["ORANGE"]["verdict"] == "NO_EVIDENCE"
    assert card_p["states"]["RED"]["verdict"] == "NO_EVIDENCE"
    assert card_p["activation_set"] == ["GREEN"] and card_p["dead_zones"] == []
    assert card_p["long_face_t22"]["state"] == "n/a"                # blend 车道无 corps 面
    assert "not claimed" in card_p["all_state_claim"]                # 万金油禁令
    assert card_p["window_cum_x2"] is not None and card_p["cost_fragile_flag"] is False
    # 热档格：窗首日 n/a 不入格；d4 收市 HOT -> d5 归属（GREENxHOT 单日）
    gh = card_p["heat_cells"].get("GREENxHOT")
    assert gh is not None and gh["n_days"] == 1 and gh["verdict"] == "NO_EVIDENCE"
    # P5: 正典自比 excess=0；击杀申报 — A 组 hr 开除面+剃刀余量冻结数；B/C 月亏线+fail-closed
    canon_card_p = profile_card("B_MAXDIV", ledger_p, sbd_p, states_seq_p, days_p,
                                heat_attr_p, {"GREEN": card_p["states"]["GREEN"]["cum_ret_x1"],
                                              "YELLOW": -0.01, "ORANGE": 0.0, "RED": 0.0}, None)
    assert abs(canon_card_p["states"]["GREEN"]["excess_vs_canon"]) < 1e-9
    kc_a = _profile_kill_conditions("A", "COMPOSITE-CE-02")
    assert kc_a["declared"]["x2_margin_razor"]["frozen_margin"] == 0.031
    assert "ic_decay>50%" in kc_a["declared"]["hr_fire_faces"]
    kc_b = _profile_kill_conditions("B", "AGGR-SYN")
    assert "single paper month < -8%" in kc_b["declared"]["paper_month_loss"]
    assert "slice-2" in kc_b["declared"]["state_mismatch_demotion"]
    # P6: t22 长史面 — corps 冻结线逐字（beat<0.5 且 n≥30=DEAD_ZONE；n<30=NO_EVIDENCE）
    corps_p = {"segments": {"bull": {"beat_rate_12m": 0.45, "n_startpoints": 100,
                                     "worst_dd_all_windows": -0.1},
                            "bear": {"beat_rate_12m": 0.6, "n_startpoints": 10},
                            "chop": {"beat_rate_12m": 0.62, "n_startpoints": 87,
                                     "worst_dd_all_windows": -0.169}}}
    t22 = _t22_long_face(corps_p)
    assert t22["segments"]["bull"]["verdict"] == "DEAD_ZONE"
    assert t22["segments"]["bear"]["verdict"] == "NO_EVIDENCE"
    assert t22["segments"]["chop"]["verdict"] == "PASS"
    assert "NOT v3" in t22["taxonomy"]
    # P8 (slice-3): 四必报单格 — covered_years 公式 / n<20 CI 诚实拒算 / 种子确定性
    iso_days = ["2026-01-%02d" % (i + 1) for i in range(25)]
    rs8 = [(d, (0.01 if i % 2 == 0 else -0.005)) for i, d in enumerate(iso_days)]
    fm8 = _four_must_cell(rs8, 7, 3)
    assert fm8["covered_years"] == round(24 / 365.25, 2), fm8["covered_years"]
    assert fm8["oos_trades"] == 7 and fm8["independent_regime_windows"] == 3
    assert fm8["ci95_lo"] is not None and fm8["ci95_width"] > 0
    assert fm8["ci_lower_bound_positive"] is (fm8["ci95_lo"] > 0)
    assert _four_must_cell(rs8, 7, 3) == fm8      # LCG 家族种子确定性（幂等律 §6）
    short8 = _four_must_cell(rs8[:15], None, 1)
    assert short8["ci95_lo"] is None and short8["ci95_width"] is None \
        and short8["ci_lower_bound_positive"] is None and short8["oos_trades"] is None
    assert short8["covered_years"] == round(14 / 365.25, 2)
    # P9 (slice-3): 合成卡接线 — 州/格四必报 + sample_science 块（P4 夹具续用）
    assert "sample_science" in card_p
    g9 = card_p["states"]["GREEN"]
    assert g9["oos_trades"] is None              # B 族合成台账无逐笔单=null 诚实
    assert g9["covered_years"] is not None and g9["ci95_width"] is not None
    assert g9["independent_regime_windows"] == 2
    assert card_p["states"]["YELLOW"]["ci95_lo"] is None      # n=5<20 拒算
    assert card_p["heat_cells"]["GREENxHOT"]["ci95_lo"] is None   # n=1<20 拒算
    ss9 = card_p["sample_science"]
    assert ss9["window_four_must"]["independent_regime_windows"] == 3
    assert ss9["window_four_must"]["ci95_width"] is not None   # 全窗 n=29>=20
    assert ss9["widest_state_ci"]["state"] == "GREEN"
    assert ss9["min_windows_gate"]["min_independent_regime_windows"] == 2
    # P10: 在位实腿（在位才跑）— 17 卡全出、自洽门 PASS、判据链恒等（缺件=诚实 SKIP）
    if os.path.isdir(os.path.join(RESULTS, "retro_paper_2026")):
        face_live = build_profile_cards()
        assert face_live.get("state") == "ok", face_live.get("state")
        assert face_live["summary"]["n_cards"] == 17
        assert face_live["self_consistency_gate"]["result"].startswith("PASS 17/17")
        assert "paper_month_loss" in face_live["cards"]["B_MAXDIV"]["kill_conditions"]["declared"]
        bmd = face_live["cards"]["B_MAXDIV"]["states"]
        assert abs(bmd["GREEN"]["excess_vs_canon"]) < 1e-9            # 正典自比=0
        # P10b (slice-3): 17 卡四必报在位面 — ORANGE/RED 构造性 None；A 组逐笔恒等门
        for acc10, c10 in face_live["cards"].items():
            for s10 in ("GREEN", "YELLOW"):
                cell10 = c10["states"][s10]
                assert cell10["ci95_lo"] is not None and cell10["ci95_width"] > 0, (acc10, s10)
                assert cell10["covered_years"] is not None and \
                    cell10["independent_regime_windows"] == cell10["episodes"], (acc10, s10)
            for s10 in ("ORANGE", "RED"):
                assert c10["states"][s10]["ci95_lo"] is None, (acc10, s10)
            assert c10["sample_science"]["widest_state_ci"] is not None, acc10
            assert c10["sample_science"]["window_four_must"]["ci95_width"] > 0, acc10
            if c10["family"] == "A":
                tot10 = c10["sample_science"]["window_four_must"]["oos_trades"]
                assert tot10 == sum(c10["states"][s10]["oos_trades"] or 0
                                    for s10 in c10["states"]), acc10   # §4.5 恒等门
        assert face_live.get("sample_science_prereg_sha256_16"), "slice-3 prereg sha missing"
    else:
        print("  [profile] live leg SKIP (retro ledgers absent) -- honest")
    # P11 (slice-4): 落地钩子 — 三族 hermetic 合成夹具（r157/r162 生产形态律：喂序列化件
    # 非内存对象）+缺件 fail-closed+GRID 中间态+CN-GRID-SLEEVE 共享读+在位零落地实腿
    import tempfile
    import shutil
    td = tempfile.mkdtemp(prefix="lh_p11_")
    try:
        # P11a: 缺件 = 三族全 ABSENT、CN-GRID-SLEEVE 联动 ABSENT、零落地 armed
        h0 = landing_hooks(td)
        assert h0["summary"]["n_landings"] == 0 and h0["summary"]["hook_state"] == "armed"
        assert all(v["state"] == "ABSENT" for v in h0["families"].values())
        assert h0["families"]["CN (T-73 s3 five-model chain)"]["models"]["CN-GRID-SLEEVE"]["state"] == "ABSENT"
        # P11b: CN 正例（1 pass cell=LANDED）+ GRID 中间态（survivor 无 candidacy）+ WILD 负例
        os.makedirs(os.path.join(td, "cn_test_model"), exist_ok=True)
        with open(os.path.join(td, "cn_test_model", "p1_results.json"), "w", encoding="utf-8") as f:
            json.dump({"g1_prime_v2": {"A_bare": {"pass": True}, "A_gate": {"pass": False},
                                        "B_bare": {"pass": False}, "B_gate": {"pass": False}}}, f)
        with open(os.path.join(td, "grid_sleeve_p1.json"), "w", encoding="utf-8") as f:
            json.dump({"survivors_science": [{"code": "510300"}], "paper_candidates": []}, f)
        os.makedirs(os.path.join(td, "wild_route"), exist_ok=True)
        with open(os.path.join(td, "wild_route", "wild_route_s1.json"), "w", encoding="utf-8") as f:
            json.dump({"g1_prime_v2": {"P01|x1": {"pass": False}}}, f)
        h1 = landing_hooks(td)
        cnm = h1["families"]["CN (T-73 s3 five-model chain)"]["models"]
        assert cnm["CN-TEST-MODEL"]["n_pass"] == 1 and cnm["CN-TEST-MODEL"]["landing_cells"] == ["A_bare"]
        assert cnm["CN-GRID-SLEEVE"]["n_survivors_science"] == 1   # 与 GRID 族同件共享读
        assert "CN-TEST-MODEL" in h1["families"]["CN (T-73 s3 five-model chain)"]["landings"]
        g1f = h1["families"]["GRID (T-78 grid sleeve)"]
        assert g1f["intermediate"] == "SURVIVORS_NO_CANDIDACY" and g1f["n_paper_candidates"] == 0
        assert h1["families"]["WILD (T-57 wild-route)"]["n_pass"] == 0
        assert h1["summary"]["n_landings"] == 1 and h1["summary"]["hook_state"] == "FIRED"
        assert h1["action_required"][0]["member"] == "CN-TEST-MODEL"
        assert "retro_paper_2026" in h1["action_required"][0]["pipeline"]  # 画像管线入口契约
        # P11c: GRID 落地正例 — paper candidacy -> GRID 落地 + CN-GRID-SLEEVE 联动落地
        with open(os.path.join(td, "grid_sleeve_p1.json"), "w", encoding="utf-8") as f:
            json.dump({"survivors_science": [{"code": "510300"}],
                       "paper_candidates": [{"code": "510300"}]}, f)
        h2 = landing_hooks(td)
        assert h2["families"]["GRID (T-78 grid sleeve)"]["landings"] == ["510300"]
        assert "CN-GRID-SLEEVE" in h2["families"]["CN (T-73 s3 five-model chain)"]["landings"]
        assert h2["summary"]["n_landings"] == 3   # CN-TEST-MODEL + CN-GRID-SLEEVE + GRID 510300
        # P11d: 在位实腿（在位才跑）— §3 预测=三族全 ok 零落地 armed（五模型链 ALL-NEGATIVE）
        #     超集断言非硬等集：glob 面天然吸收未来 cn_* 新批产物（slice-6+ 新 prereg
        #     模型落 results/cn_*/p1_results.json 即自动入观察名单=钩子本义；R259 零产物
        #     窗工程修正律——断言意图=五模型链齐读，非封死名单）
        if os.path.isdir(os.path.join(RESULTS, "cn_rev_tilt")):
            hl = landing_hooks()
            assert hl["summary"]["n_landings"] == 0, hl["summary"]
            assert hl["summary"]["hook_state"] == "armed"
            assert all(v["state"] == "ok" for v in hl["families"].values()), hl["families"]
            assert set(hl["families"]["CN (T-73 s3 five-model chain)"]["models"]) >= \
                {"CN-REV-TILT", "CN-DIV-LOWVOL-ROT", "CN-REGIME-POLICY",
                 "CN-CORE-SATELLITE", "CN-GRID-SLEEVE"}
            assert hl["families"]["WILD (T-57 wild-route)"]["n_pass"] == 0
            assert hl["families"]["GRID (T-78 grid sleeve)"]["n_paper_candidates"] == 0
        else:
            print("  [landing] live leg SKIP (cn products absent) -- honest")
    finally:
        shutil.rmtree(td, ignore_errors=True)
    print("selftest: 6/6 core + 5/5 calibration + 10/10 profile PASS (registered/prospect/"
          "veto/tournament/untested-propagation/iv6 production-shape fixtures; face formulas/"
          "weight-allocation/band-quantiles/end-to-end-calibrate/frozen-band-emission incl "
          "portfolio leg + veto override; readout-only law asserted on every pure card; "
          "T-81 profile: return-series caliber/episode-fail-closed/double-line verdicts/"
          "heat-shift attribution/canon self-face/kill-declarations/t22 corps lines verbatim"
          "; T-81 slice-3: four-must cell caliber/CI floor refusal/seed determinism/"
          "synthetic-card wiring/sample-science block"
          "; T-81 slice-4 landing hooks: absent-fail-closed/CN pass-bit landing/GRID "
          "survivors-no-candidacy intermediate/shared CN-GRID-SLEEVE read/paper-candidacy "
          "dual-family firing"
          + (" + live 17-card leg incl slice-3 four-must faces" if os.path.isdir(os.path.join(RESULTS, "retro_paper_2026")) else "") + ")")
    return 0


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(selftest())
    if cmd == "calibrate":
        sys.exit(calibrate())
    sys.exit(0 if run() else 1)


if __name__ == "__main__":
    main()
