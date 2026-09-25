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
    payload = {
        "ticket": "T-2026-09-25-63", "order": "O-20260925-1755",
        "charter": "firm/STRATEGY_EVALUATION.md v2.0 (sec 2/6/7/8)",
        "generated": _dt.datetime.now().isoformat(timespec="seconds"),
        "naming_reconciliation": "charter sec.4 names strategy_scorecard.py/json; T-07 "
                                 "delivered the strategy face as scripts/scorecard.py -> "
                                 "results/scorecard_v1.json (disclosed in that file). This v2 "
                                 "file IS the charter-named three-card artifact: strategy face "
                                 "= reused engine (zero rebuild), trader/portfolio cards = new.",
        "calibration_state": "pre-calibration: trader/portfolio cards are READOUT-ONLY "
                              "(sec 8.5); composite totals for these two faces require the "
                              "first-cohort calibration prereg (research/STRATEGY_SCORECARD_"
                              "CALIB.md) frozen THEN run. Strategy-face totals = v1.0 frozen.",
        "unified_law": {"sec8": ">=2-dimension decision basis; hard-veto faces universal; "
                                "evaluation never overrides gates; data-driven; "
                                "calibration-before-totals"},
        "strategy_face": {"source": "results/scorecard_v1.json (scripts/scorecard.py)",
                          "summary": strategy_payload.get("summary"),
                          "per_trader": strategy_payload.get("per_trader")},
        "trader_cards": built["trader_cards"],
        "portfolio_cards": built["portfolio_cards"],
        "cross_period_shared": built["cross_period_shared"],
        "discipline_veto_hits": built["discipline_veto_hits"],
        "summary": {"n_strategy_cards": len(strategy_payload.get("per_trader") or {}),
                    "n_trader_cards": len(built["trader_cards"]),
                    "n_portfolio_cards": len(built["portfolio_cards"]),
                    "trader_cohort": "6 registered + 22 PROSPECT (first-cohort per sec 8.5)",
                    "portfolio_cohort": "IV6/EW6 + tournament 5 methods (first-cohort)"},
        "audit": {"elapsed_sec": round(time.time() - t0, 1), "zero_new_backtests": True,
                  "zero_engine_runs": True, "ledger_delta": 0,
                  "sources": ["firm/traders/*.json (via scorecard.py)", "results/corps_roster.json",
                              "results/paper/*_paper.json", "results/g25/*.json",
                              "results/portfolio_blend_tournament.json",
                              "results/portfolio_iv6.json", "results/portfolio_ew6.json",
                              "results/spm_j4_attribution.json",
                              "results/current_market_stable_profit.json",
                              "results/pbo_cscv_v1.json"],
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
    print("selftest: 6/6 core + 4/4 calibration PASS (registered/prospect/veto/tournament/"
          "untested-propagation/iv6 production-shape fixtures; face formulas/weight-allocation/"
          "band-quantiles/end-to-end-calibrate; readout-only law asserted on every card)")
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
