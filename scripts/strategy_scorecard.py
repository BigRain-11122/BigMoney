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
  python scripts/strategy_scorecard.py selftest   # 离线合成夹具自检（零网络零真实写）
"""
import datetime as _dt
import json
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
    print("selftest: 6/6 PASS (registered/prospect/veto/tournament/untested-propagation/iv6 "
          "production-shape fixtures; readout-only law asserted on every card)")
    return 0


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(selftest())
    sys.exit(0 if run() else 1)


if __name__ == "__main__":
    main()
