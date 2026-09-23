"""百团锦标赛（2026-09-20 赛制）：每支团队=一名选手，各携100万本金同台竞技，分段出战绩。

- 风格谱系：极稳/保守/均衡/进取/激进 5档各占1/5席位，各队独立风控参数+曝光缩放
- 派员：现任团队 + 退休团队 + GA种群精英 + 经典种子 + 强变异"微调选手"，补满100队
- 历史锦标赛：全窗口回测（100万起步），按 period_days 交易日切段，每段+总榜+风格榜
- 联赛：随机起点 3 年窗口循环赛（用户指定周期三年），多样性前10晋级+连胜认证
- 前瞻轨道：spawn 之后每个收盘日推进全部选手（参数冻结，只用新到数据=模拟实盘）
- 机制回馈：总榜前 feed_top 名的基因注入 GA 种群，参与冠军/团队竞争
- 全员本地运算，多进程并行（复用 evolve.workers）

诚实口径：历史锦标赛是"冻结参数在历史分段的表现"（模拟）；spawn 日之后的
前瞻轨道才是严格意义的模拟实盘积累。报告均明确标注。
"""
from __future__ import annotations

import copy
import datetime as dt
import json
import logging
import os
import random
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

from . import data as qdata
from . import strategies as strat_lib
from .backtest import run_backtest
from .config import LOGS_DIR, AppConfig, resolve_workers
from .evolve import GA_SEEDS, composite_score, mutate, sample_individual
from .sizing import get_sizing
from .state import save_state

log = logging.getLogger("quant.arena")

_ARENA_CTX: dict = {}


def _arena_init(panel, cfg):
    _ARENA_CTX["panel"] = panel
    _ARENA_CTX["cfg"] = cfg


def _genes(src: dict) -> dict:
    """提取完整基因（策略+参数+仓位控制基因）；缺失字段默认等权仓位。"""
    return {"strategy": src["strategy"], "params": src["params"],
            "sizing": src.get("sizing") or "equal",
            "sizing_params": dict(src.get("sizing_params") or {})}


# ---------------------------------------------------------------- 风格谱系（用户指定：极保守→极激进全覆盖）

ROSTER_VERSION = "v5-200t-1y-styles"  # 赛制版本：200队/100万/1年窗/5风格（2026-09-21 用户"队伍模式要多/样本要大"→不符即重组）

TEAM_STYLES: dict[str, dict] = {
    # scale=目标权重的曝光缩放；其余=该风格独立风控参数（均在全球用户交易风格包络内：持股3~15日）
    "极稳": {"scale": 0.30, "max_position_pct": 0.05, "max_etf_position_pct": 0.15,
             "max_positions": 16, "stop_loss_pct": 0.05, "max_hold_days": 7},
    "保守": {"scale": 0.50, "max_position_pct": 0.08, "max_etf_position_pct": 0.25,
             "max_positions": 12, "stop_loss_pct": 0.06, "max_hold_days": 8},
    "均衡": {"scale": 1.00, "max_position_pct": 0.15, "max_etf_position_pct": 0.50,
             "max_positions": 8, "stop_loss_pct": 0.08, "max_hold_days": 10},
    "进取": {"scale": 1.00, "max_position_pct": 0.25, "max_etf_position_pct": 0.70,
             "max_positions": 6, "stop_loss_pct": 0.10, "max_hold_days": 12},
    "激进": {"scale": 1.00, "max_position_pct": 0.40, "max_etf_position_pct": 0.90,
             "max_positions": 4, "stop_loss_pct": 0.12, "max_hold_days": 15},
}
STYLE_ORDER = list(TEAM_STYLES)


def style_cfg(cfg: AppConfig, style: str) -> AppConfig:
    """按风格克隆一份风控参数（锦标赛口径；部署管线仍用全局用户红线，互不干扰）。"""
    s = TEAM_STYLES.get(style) or TEAM_STYLES["均衡"]
    c = copy.deepcopy(cfg)
    c.risk.max_position_pct = s["max_position_pct"]
    c.risk.max_etf_position_pct = s["max_etf_position_pct"]
    c.risk.max_positions = s["max_positions"]
    c.risk.stop_loss_pct = s["stop_loss_pct"]
    c.risk.max_hold_days = s["max_hold_days"]
    return c


def _least_style(players: list[dict]) -> str:
    """补员时分配当前席位最少的风格（保持 5 风格各占 1/5）。"""
    counts = {s: 0 for s in STYLE_ORDER}
    for p in players:
        counts[p.get("style") or "均衡"] = counts.get(p.get("style") or "均衡", 0) + 1
    return min(STYLE_ORDER, key=lambda s: counts[s])


def _arena_run_player(player: dict, span: tuple | None = None) -> dict:
    """单选手回测（各队100万起步，含全部引擎规则：T+1/涨跌停/费用/止损/持股上限）。

    风格谱系：按 player['style'] 克隆独立风控参数并缩放曝光
    （极稳×0.3 … 激进×1.0），策略/仓位基因与适应度口径一致地叠加。
    span=(start,end)（日期索引位置）：常驻池模式下 worker 只收到两个整数，
    自行从全量面板切窗（2026-09-21 迭代加速：此前每局整面板 pickle 给 16
    进程=20-30% 开销白烧，用户指令"迭代频率疯狂加速"）。
    """
    panel, cfg0 = _ARENA_CTX["panel"], _ARENA_CTX["cfg"]
    full, evalp = panel, panel
    if span is not None:
        # 指标预热缓冲（2026-09-21 用户"历史数据下全"配套）：评估窗口前再带
        # 300日供指标计算，评估/计分仍只在窗口内——250日动量/52周高点等长
        # 回看策略不再结构性失能（此前窗口硬切=长回看只有最后几天有信号，
        # 进化被迫收敛到短回看参数，全历史数据喂不进长周期规律）。无未来
        # 函数不变：指标只用 ≤当日 数据，预热段不参与计分。
        w_start = max(0, span[0] - 300)
        full = panel.window(panel.dates[w_start], panel.dates[span[1]])
        evalp = panel.window(panel.dates[span[0]], panel.dates[span[1]])
    style = player.get("style") or "均衡"
    use_style = bool(getattr(cfg0.arena, "style_spectrum", True))
    cfg = style_cfg(cfg0, style) if use_style else cfg0
    scale = (TEAM_STYLES[style]["scale"] if style in TEAM_STYLES else 1.0) if use_style else 1.0
    try:
        strat = strat_lib.get_strategy(player["strategy"])()
        w = strat.target_weights(full, player["params"])
        sizing = get_sizing(player.get("sizing") or "equal")()
        w = sizing.apply(w, full, player.get("sizing_params") or {})
        if scale != 1.0:
            w = w * scale
        if span is not None:
            w = w.loc[w.index >= evalp.dates[0]]
        res = run_backtest(evalp, w, cfg, start_cash=float(player["capital"]))
        return {"id": player["id"], "ok": True, "equity": res.equity, "metrics": res.metrics}
    except Exception as e:  # noqa: BLE001
        return {"id": player["id"], "ok": False, "error": f"{type(e).__name__}: {e}"[:100]}


# ---------------------------------------------------------------- 派员

def _ind_key(ind: dict) -> str:
    """基因指纹：含仓位控制基因（同策略同参数不同仓位=不同个体）。"""
    return json.dumps(_genes(ind), sort_keys=True, default=str)


def _next_id(a: dict, prefix: str) -> str:
    """全局单调递增选手编号（跨批次唯一）。历史按池内位置/批次序号编号
    （V{i}/G{len(pool)}）导致跨届ID复用——而联赛结果集/连胜/认证/看板多处
    按ID键控，重复ID会串战绩（2026-09-21 实测阵容100人仅73唯一ID）。"""
    n = int(a.get("id_seq", 0) or 0)
    if n <= 0:
        nums = []
        for p in (a.get("players") or []):
            s = str(p.get("id", ""))[1:]
            if s.isdigit():
                nums.append(int(s))
        n = max(nums) if nums else 0
    n += 1
    a["id_seq"] = n
    return f"{prefix}{n:03d}"


def _current_players(cfg: AppConfig, state: dict, persist: bool = True) -> list[dict]:
    """现行阵容（赛制版本不符自动重组新赛季：资金/周期/风格等赛制变更时触发）。"""
    a = state.setdefault("arena", {})
    if a.get("players") and a.get("roster_version") == ROSTER_VERSION:
        return a["players"]
    log.info("【锦标赛】赛制版本变更（%s）→ 重组新赛季阵容", ROSTER_VERSION)
    return spawn_players(cfg, state, force=True, persist=persist)


def spawn_players(cfg: AppConfig, state: dict, force: bool = False,
                  persist: bool = True) -> list[dict]:
    """派出 size 支团队（默认100），每队 capital 元（100万）。混合来源保证多样性；
    风格按 5 档轮转分配，保持各风格 1/5 席位（极稳/保守/均衡/进取/激进）。"""
    a = state.setdefault("arena", {})
    ac = cfg.arena
    if a.get("players") and not force and len(a["players"]) >= ac.size \
            and a.get("roster_version") == ROSTER_VERSION:
        return a["players"]

    rng = random.Random()
    pool: list[dict] = []
    # 1) 现任冠军团队（在役最优变体；完整携带仓位基因）
    for m in (state.get("team") or []):
        pool.append(_genes(m))
    if state.get("champion"):
        pool.append(_genes(state["champion"]))
    # 2) GA 种群精英
    for ind in (state["evolution"].get("population") or []):
        pool.append(_genes(ind))
    # 3) 经典公开模型种子
    pool += [copy.deepcopy(s) for s in GA_SEEDS]
    # 4) 微调选手：对既有基因做强变异 + 全新随机，直到补满
    seen: set[str] = {_ind_key(p) for p in pool}
    attempts = 0
    while len(pool) < ac.size and attempts < ac.size * 30:
        attempts += 1
        if pool and rng.random() < 0.7:
            cand = mutate(copy.deepcopy(rng.choice(pool)), rng, ac.mutate_rate, ac.mutate_sigma)
        else:
            cand = sample_individual(rng)
        k = _ind_key(cand)
        if k in seen:
            continue
        seen.add(k)
        pool.append(cand)

    players = [{"id": f"P{i + 1:03d}", "strategy": p["strategy"], "params": p["params"],
                "sizing": p.get("sizing") or "equal",
                "sizing_params": dict(p.get("sizing_params") or {}),
                "style": STYLE_ORDER[i % len(STYLE_ORDER)],  # 5风格轮转：各档1/5席位
                "capital": float(ac.capital), "equity": float(ac.capital), "track": []}
               for i, p in enumerate(pool[: ac.size])]
    a["players"] = players
    a["roster_version"] = ROSTER_VERSION
    a["spawn_date"] = dt.date.today().isoformat()
    if force or not a.get("forward_start"):
        a["forward_start"] = None  # 首次 advance 时定为当日
    if persist:
        save_state(state)
    style_str = " ".join(f"{s}×{sum(1 for p in players if p['style'] == s)}"
                         for s in STYLE_ORDER)
    log.info("【锦标赛】新赛季开赛：已派出 %d 支团队，各携 %.0f 万本金 | 风格席位 %s",
             len(players), ac.capital / 10_000, style_str)
    return players


# ---------------------------------------------------------------- 联赛制：随机1年窗口循环赛

def _wcorr(a: pd.DataFrame, b: pd.DataFrame) -> float:
    """两个持仓权重矩阵的"选股相似度"：公共列展平相关系数。"""
    common = [c for c in a.columns if c in b.columns]
    if not common:
        return 0.0
    x = np.nan_to_num(a[common].to_numpy(dtype=float)).ravel()
    y = np.nan_to_num(b[common].to_numpy(dtype=float)).ravel()
    if x.std() < 1e-12 or y.std() < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def _diverse_top(cfg: AppConfig, ranked: list[dict], sub_panel) -> list[dict]:
    """多样性前10（用户指定"选股等策略都要不一样"）：

    - 同策略族人数 ≤ max_family_top
    - 与已入选者的持仓权重相关性 < max_sel_corr（候选权重按需现算，控制成本）
    - 分数须 ≥ qualify_floor（全体垃圾局宁可少收）
    """
    ac = cfg.arena
    selected: list[dict] = []
    fam_count: dict[str, int] = {}
    sel_weights: list[pd.DataFrame] = []
    for cand in ranked[: max(30, ac.feed_top * 3)]:
        if len(selected) >= 10:  # 前10晋级（用户指定）
            break
        if cand["score"] < ac.qualify_floor:
            continue
        fam = cand["strategy"]
        if fam_count.get(fam, 0) >= ac.max_family_top:
            continue
        try:
            strat = strat_lib.get_strategy(fam)()
            w = strat.target_weights(sub_panel, cand["params"])
            sizing = get_sizing(cand.get("sizing") or "equal")()
            w = sizing.apply(w, sub_panel, cand.get("sizing_params") or {})
        except Exception:  # noqa: BLE001 权重计算失败的候选弃用
            continue
        if any(_wcorr(w, sw) >= ac.max_sel_corr for sw in sel_weights):
            continue
        selected.append(cand)
        fam_count[fam] = fam_count.get(fam, 0) + 1
        sel_weights.append(w)
        if len(selected) >= 10:
            break
    return selected


def _run_player_span(t: tuple) -> dict:
    """常驻池任务壳：t=(player, (start,end))，worker 端从全量面板切窗。"""
    return _arena_run_player(t[0], t[1])


def _evaluate_window(players: list[dict], sub_panel, cfg,
                     pool: "ProcessPoolExecutor | None" = None,
                     span: tuple | None = None) -> dict[str, dict]:
    """全员在一个窗口上并行回测。

    pool+span 模式（迭代加速，用户指令"疯狂加速"）：_ARENA_CTX 存全量面板的
    常驻池，每局只 pickle (player, (start,end)) 整数对给 worker——省掉此前
    每局整子面板 ×16 进程的重复 pickle（实测 20-30% 开销白烧）。
    pool=None：旧临时池路径（手动调用兼容）。"""
    results: dict[str, dict] = {}
    workers = resolve_workers(cfg)
    if pool is not None and span is not None:
        try:
            for r in pool.map(_run_player_span, [(p, span) for p in players]):
                results[r["id"]] = r
            return results
        except Exception as e:  # noqa: BLE001
            log.warning("联赛常驻池失败，本局回退临时池: %s", e)
            results = {}
    if workers > 1 and len(players) >= workers * 2:
        try:
            with ProcessPoolExecutor(max_workers=workers, initializer=_arena_init,
                                     initargs=(sub_panel, cfg)) as ex:
                for r in ex.map(_arena_run_player, players):
                    results[r["id"]] = r
        except Exception as e:  # noqa: BLE001
            log.warning("联赛并行失败，回退串行: %s", e)
            results = {}
    if not results:
        _arena_init(sub_panel, cfg)
        for p in players:
            results[p["id"]] = _arena_run_player(p)
    return results


def _trim_qualified(a: dict, cap: int = 200) -> None:
    """认证池按证据淘汰（防证据失忆）：认证分低者先出，各族唯一代表保护。

    尾部截断（保留最近N）在高流速下=时间遗忘——凌晨的强证据被当晚
    后段的弱证据顶掉。改为按 (可淘汰性, 认证分, 认证时间) 升序淘汰，
    保留证据最强的 cap 人；同分时先淘汰更陈旧者。保留后恢复时间序
    （展示端 qualified[-5:] 依赖"最新在后"）。"""
    q = a.get("qualified") or []
    if len(q) <= cap:
        return
    fams: dict[str, int] = {}
    for x in q:
        f = str(x.get("strategy") or "?")
        fams[f] = fams.get(f, 0) + 1
    uniq_fams = {f for f, n in fams.items() if n <= 1}
    ranked = sorted(q, key=lambda x: (
        0 if str(x.get("strategy") or "?") not in uniq_fams else 1,
        float(x.get("score") or 0.0), x.get("qualified_at") or ""))
    keep = ranked[len(q) - cap:]
    keep.sort(key=lambda x: x.get("qualified_at") or "")
    a["qualified"] = keep


def run_round(cfg: AppConfig, state: dict, panel=None, rng: random.Random | None = None,
              persist: bool = True, pool: "ProcessPoolExecutor | None" = None) -> dict | None:
    """联赛一局（用户指定机制，2026-09-20 赛制：每队100万/周期3年）：

    ① 随机起点抽 3 年（round_days 交易日）考核窗口 → ② 全员独立回测（100万/队，各自风格风控）
    → ③ 多样性前10晋级（同族≤3、持仓相关<0.85、分数过线）
    → ④ 晋级者 streak+1，其余清零 → ⑤ 连续 qualify_streak 局前10 = 稳定前10认证
    （基因注入 GA 种群参与冠军团队竞争，留痕可审计）→ ⑥ 换血：Top10保留+变异体+新基因补满。
    """
    ac = cfg.arena
    a = state.setdefault("arena", {})
    players = _current_players(cfg, state, persist=persist)
    if panel is None:
        _, panel = qdata.full_panel(cfg)
    rng = rng or random.Random()

    dates = list(panel.dates)
    n = len(dates)
    rd = min(ac.round_days, n - 2)
    if rd < 60:
        log.warning("联赛窗口数据不足（%d 日），跳过本局", n)
        return None
    # 玩法自进化（2026-09-21 用户指令"每半小时迭代玩法"）：近窗采样偏置——
    # 与时俱进：市场切换时加大"近1/4历史"窗口的抽样占比（同局全员同窗=公平）
    g = a.get("game") or {}
    if rng.random() < float(g.get("recent_bias", 0.20)):
        start = rng.randint(max(0, n - rd - 1 - max(60, n // 4)), n - rd - 1)
    else:
        start = rng.randint(0, n - rd - 1)
    sub = panel.window(dates[start], dates[start + rd - 1])

    results = _evaluate_window(players, sub, cfg, pool=pool,
                               span=(start, start + rd - 1) if pool is not None else None)
    rows = []
    for p in players:
        r = results.get(p["id"])
        if not r or not r.get("ok"):
            continue
        rows.append({"id": p["id"], "strategy": p["strategy"], "params": p["params"],
                     "sizing": p.get("sizing") or "equal",
                     "sizing_params": dict(p.get("sizing_params") or {}),
                     "style": p.get("style") or "均衡",
                     "score": composite_score(r["metrics"], cfg),
                     "ret": r["metrics"]["total_return"], "metrics": r["metrics"]})
    if not rows:
        log.error("联赛本局无有效选手")
        return None
    rows.sort(key=lambda x: x["score"], reverse=True)

    # —— 多样性前10（选股必须不一样）—— 相关性检查同样带预热缓冲：
    # 长回看策略在硬切窗内权重全NaN=变相绕过相关性闸（NaN不构成有效对比）
    top10 = _diverse_top(cfg, rows, panel.window(
        dates[max(0, start - 300)], dates[start + rd - 1]))
    top_ids = {r["id"] for r in top10}

    # —— 多维战绩累积（用户指令：实战多维度评价，2026-09-21）——
    # pstats 会为每个新基因加键（dict size 变化）——与并发 save_state 的 dumps
    # 互斥必须持锁（盘中伴生联赛线程安全，2026-09-22）
    from .state import STATE_LOCK
    with STATE_LOCK:
        _accum_pstats(a, rows, top_ids, halt_pct=float(cfg.risk.drawdown_halt_pct or 0.10))

    # —— 稳定性计数与认证 ——
    newly_qualified: list[dict] = []
    qualified_keys = {_ind_key(q) for q in (a.get("qualified") or [])}
    for p in players:
        p["rounds"] = int(p.get("rounds", 0)) + 1
        hist = (p.get("top10_hist") or [])[-9:] + [1 if p["id"] in top_ids else 0]
        p["top10_hist"] = hist
        row = next((x for x in rows if x["id"] == p["id"]), None)
        p["score_last"] = round(row["score"], 4) if row else None
        if p["id"] in top_ids:
            p["streak"] = int(p.get("streak", 0)) + 1
            if (p["streak"] >= ac.qualify_streak and row
                    and row["score"] >= float((a.get("game") or {}).get("qualify_floor")
                                              or ac.qualify_floor)
                    and _ind_key(p) not in qualified_keys):
                q = {"id": p["id"], "strategy": p["strategy"], "params": p["params"],
                     "sizing": p.get("sizing") or "equal",
                     "sizing_params": dict(p.get("sizing_params") or {}),
                     "streak": p["streak"], "score": p["score_last"],
                     "qualified_at": dt.datetime.now().isoformat(timespec="seconds"),
                     "round": int(a.get("round", 0)) + 1,
                     "window": f"{dates[start].date()}~{dates[start + rd - 1].date()}"}
                (a.setdefault("qualified", [])).append(q)
                # 认证池扩容 50→200（2026-09-21 用户"样本数量测试数量太少"指令）：
                # 高认证流速下 cap50 半小时即全池换血=证据失忆，选队/裁决失去纵深。
                # 科学审计（2026-09-21 用户红线"所有都要基于科学"）：尾部截断只
                # 放缓失忆未根治——0.75秒/局下流量带顶格≈300+认证/小时，200池
                # 40分钟仍全换血，选队只见"最后一小时"幸存者。淘汰改证据制
                # （_trim_qualified：分数最低先出，各族唯一代表保护）。
                _trim_qualified(a, 200)
                qualified_keys.add(_ind_key(p))
                newly_qualified.append(q)
                # 稳定前10 → 基因注入 GA 种群（参与冠军团队竞争，含仓位基因）
                pop = state["evolution"].setdefault("population", [])
                pop.append(_genes(p))
                state["evolution"]["population"] = pop[-96:]  # GA池随认证流速同步扩容96
        else:
            p["streak"] = 0

    a["round"] = int(a.get("round", 0)) + 1
    rec = {"round": a["round"],
           "window": f"{dates[start].date()}~{dates[start + rd - 1].date()}（{rd}日≈{rd/252:.1f}年）",
           "mean_score": round(float(np.mean([x["score"] for x in rows])), 4),
           "best": {"id": rows[0]["id"], "strategy": rows[0]["strategy"],
                    "style": rows[0].get("style", "均衡"), "score": round(rows[0]["score"], 4)},
           "top10": [{"id": r["id"], "strategy": r["strategy"], "style": r.get("style", "均衡"),
                      "score": round(r["score"], 4)} for r in top10],
           "qualified": [q["id"] for q in newly_qualified]}
    a["round_history"] = (a.get("round_history") or [])[-199:] + [rec]

    # —— 换血：Top10 保留（streak/轨道延续）+ 变异体 + 新基因 → 下一局阵容 ——
    # 持锁：respawn 整体换 a["players"] 引用 + persist 落盘，与会话线程互斥
    with STATE_LOCK:
        _respawn_from_top(cfg, state, top10, rows, persist=persist)
        if persist:
            save_state(state)
    log.info("【联赛】第%d局 %s | 均分%.3f 最佳 %s(%s,%.3f) | 新认证:%s",
             rec["round"], rec["window"], rec["mean_score"],
             rows[0]["id"], rows[0]["strategy"], rows[0]["score"],
             ",".join(q["id"] for q in newly_qualified) or "无")
    for q in newly_qualified:
        log.info("★【联赛】%s (%s) 连续%d局稳定前10 → 认证为正式选手，基因已注入GA种群",
                 q["id"], q["strategy"], q["streak"])
    if persist:
        maybe_write_board(cfg, state)
    return rec


def _purge_polluted_evidence(cfg: AppConfig, state: dict) -> None:
    """数据纪元变化 → 联赛实战证据按事件类型清除（用户红线 2026-09-21：
    "错误的训练数据及时清空，发现以后，不要污染我的模型"）。

    事件分两类（读纪元文件的域内原因）：
    - 校验发现类（原因含"校验"）：错误数据上挣的证据不可留——pstats 实战
      样本 + 认证池（选队依据）全部清除重练。认证池清空后 S2/S3 短暂空仓
      至新认证流入（当前流速≈1小时内重建），S1 冠军团队不受影响（晋升闸
      用当前数据独立复验后才允许部署，本就不是认证池出身）。
    - 例行重写类（周全量重拉/期货日更重拼接）：只清评估缓存分（进化自动
      用新数据重算），pstats/认证保留——同一批随机窗内的相对排名自洽，
      qfq 基准小漂移对所有选手同向，清证据=毁灭好证据，过度清除反而不科学。"""
    from .data import data_epoch
    ep = data_epoch()
    a = state.setdefault("arena", {})
    s_seen, f_seen = a.get("data_epoch_stock"), a.get("data_epoch_futures")
    if s_seen == ep["stock"] and f_seen == ep["futures"]:
        return
    a["data_epoch_stock"], a["data_epoch_futures"] = ep["stock"], ep["futures"]
    discovery = ((s_seen != ep["stock"] and "校验" in ep.get("reason_stock", ""))
                 or (f_seen != ep["futures"] and "校验" in ep.get("reason_futures", "")))
    if discovery:
        n_ps, n_q = len(a.get("pstats") or {}), len(a.get("qualified") or [])
        a["pstats"] = {}
        a["qualified"] = []
        log.warning("【污染清除】数据校验发现修正（%s）→ 联赛实战证据清除重练："
                    "pstats %d 条 + 认证池 %d 人（晋升闸用当前数据独立复验，S1 不受影响）",
                    ep.get("reason_stock") or ep.get("reason_futures"), n_ps, n_q)
    elif s_seen is not None or f_seen is not None:
        log.warning("【污染清除】数据纪元例行更新 s%d/f%d（%s）→ 评估缓存分已清除重算，联赛证据保留",
                    ep["stock"], ep["futures"],
                    ep.get("reason_stock") or ep.get("reason_futures") or "例行重写")


def run_rounds(cfg: AppConfig, state: dict, panel=None, time_budget_s: float = 600.0,
               persist: bool = True) -> int:
    """时间盒内连续开局（高频迭代：闭市时段由 auto 守护循环调用）。

    每批先走一拍玩法自进化（内部半小时时间闸）：真实实战信号→有界校准+公平审计。
    """
    try:
        from .state import STATE_LOCK
        with STATE_LOCK:
            _purge_polluted_evidence(cfg, state)
    except Exception:  # noqa: BLE001
        log.exception("污染清除检查异常（忽略，下批重查）")
    try:
        from . import game_evo
        from .state import STATE_LOCK
        # game_evo/purge 变更 arena.game 与证据池——持锁防并发 dumps 撕裂
        with STATE_LOCK:
            game_evo.maybe_evolve_game(cfg, state)
    except Exception:  # noqa: BLE001
        log.debug("玩法自进化节拍异常（忽略）")
    if panel is None:
        _, panel = qdata.full_panel(cfg)
    rng = random.Random()
    t0 = time.time()
    n = 0
    # 批级常驻池（迭代加速：全量面板只 pickle 一次，每局只传整数区间给 worker；
    # 用户指令"迭代频率疯狂加速"——此前每局重建池+重复pickle=20-30%开销白烧）
    batch_pool = None
    workers = resolve_workers(cfg)
    try:
        if workers > 1 and len(_current_players(cfg, state, persist=False)) >= workers * 2:
            batch_pool = ProcessPoolExecutor(max_workers=workers,
                                             initializer=_arena_init,
                                             initargs=(panel, cfg))
    except Exception:  # noqa: BLE001 常驻池失败→逐局临时池（旧行为）
        batch_pool = None
    try:
        while time.time() - t0 < time_budget_s:
            try:
                if run_round(cfg, state, panel=panel, rng=rng, persist=persist,
                             pool=batch_pool) is None:
                    break
                n += 1
            except Exception:  # noqa: BLE001
                log.exception("联赛开局异常，终止本批")
                break
    finally:
        if batch_pool is not None:
            try:
                batch_pool.shutdown(wait=False)
            except Exception:  # noqa: BLE001
                pass
    # 批次结束刷新多维Top10与"适合我"裁决报告（用户指令：实战多维度评价，2026-09-21）
    if persist and n:
        try:
            dimension_report(cfg, state, write_file=True)
            verdict_report(cfg, state, write_file=True)
        except Exception:  # noqa: BLE001
            log.debug("多维Top10/verdict报告刷新失败")
    return n


def _segment_returns(eq: pd.Series, days: int) -> list[dict]:
    """把净值曲线按 days 交易日切段，返回各段收益。"""
    idx = list(eq.index)
    out = []
    for s in range(0, len(idx), days):
        chunk = idx[s: s + days]
        out.append({"idx": s // days,
                    "start": chunk[0].strftime("%Y-%m-%d"),
                    "end": chunk[-1].strftime("%Y-%m-%d"),
                    "ret": float(eq[chunk[-1]] / eq[chunk[0]] - 1.0)})
    return out


def _respawn_from_top(cfg: AppConfig, state: dict, feed: list[dict], rows: list[dict],
                      persist: bool = True) -> None:
    """循环迭代阵容（每届锦标赛后调用）：Top10 原样保留 + 每人1个变异体 + 新基因补满。

    - 保留者延续个人前瞻轨道（p.track 不清），equity 保持——观察"迭代后的老选手"而非删号重练
    - 变异体以 arena.mutate_rate/sigma 对 Top10 微调，下届同台检验
    - 补满成员来自：GA种群、经典种子、上一届中游表现者（多样性）、全新随机
    """
    ac = cfg.arena
    a = state.setdefault("arena", {})
    old_players = a.get("players") or []
    by_id = {p["id"]: p for p in old_players}
    rng = random.Random()

    new_pool: list[dict] = []
    seen: set[str] = set()
    used_ids: set[str] = set()  # 新阵容内ID唯一（历史重复ID串战绩，2026-09-21修复）
    kept = 0
    # 1) 本轮 Top10（按适应分）原样保留——战绩留档，轨道延续，风格随队保留
    for r in feed:
        ind = _genes(r)
        k = _ind_key(ind)
        if k in seen:
            continue
        seen.add(k)
        old = by_id.get(r["id"]) or {}
        pid = r["id"] if r["id"] not in used_ids else _next_id(a, r["id"][:1] or "P")
        used_ids.add(pid)
        new_pool.append({**ind,
                         "id": pid, "capital": float(ac.capital),
                         "style": r.get("style") or old.get("style") or "均衡",
                         "equity": float(old.get("equity", ac.capital)),
                         "track": old.get("track") or [], "iter": int(old.get("iter", 1)) + 1,
                         # 联赛稳定性计数跨局延续（稳定前10认证依赖）
                         "streak": int(old.get("streak", 0)),
                         "rounds": int(old.get("rounds", 0)),
                         "score_last": old.get("score_last"),
                         "top10_hist": old.get("top10_hist") or []})
        kept += 1
    # 2) Top10 的变异体（微调下届参赛；风格按最少席位分配——冠军基因跨风格检验：
    #    同一策略基因在不同风险档下的表现差异，本身就是"哪种风格合适"的证据）
    n_var = max(kept, ac.feed_top)
    for i in range(n_var):
        base = feed[i % len(feed)] if feed else None
        if not base:
            break
        var = mutate(_genes(base), rng, ac.mutate_rate, ac.mutate_sigma)
        k = _ind_key(var)
        if k in seen:
            continue
        seen.add(k)
        pid = _next_id(a, "V")
        used_ids.add(pid)
        new_pool.append({**var, "id": pid, "capital": float(ac.capital),
                         "style": _least_style(new_pool),
                         "equity": float(ac.capital), "track": [], "iter": 1})
    # 3) 补满：GA种群 → 经典种子 → 上届中游（第11~40名） → 随机（风格补最少席位，保持1/5均衡）
    gap = ac.size - len(new_pool)
    if gap > 0:
        mids = rows[10:40]
        for r in mids[: gap // 4]:
            ind = _genes(r)
            k = _ind_key(ind)
            if k not in seen:
                seen.add(k)
                pid = r["id"] if r["id"] not in used_ids else _next_id(a, r["id"][:1] or "N")
                used_ids.add(pid)
                new_pool.append({**ind, "id": pid, "capital": float(ac.capital),
                                 "style": r.get("style") or _least_style(new_pool),
                                 "equity": float(by_id.get(r["id"], {}).get("equity", ac.capital)),
                                 "track": by_id.get(r["id"], {}).get("track") or [], "iter": 1})
        for ind in (state["evolution"].get("population") or []):
            if len(new_pool) >= ac.size:
                break
            k = _ind_key(ind)
            if k in seen:
                continue
            seen.add(k)
            pid = _next_id(a, "G")
            used_ids.add(pid)
            new_pool.append({**copy.deepcopy(ind), "id": pid,
                             "capital": float(ac.capital), "style": _least_style(new_pool),
                             "equity": float(ac.capital), "track": [], "iter": 1})
        for s in GA_SEEDS:
            if len(new_pool) >= ac.size:
                break
            k = _ind_key(s)
            if k not in seen:
                seen.add(k)
                pid = _next_id(a, "S")
                used_ids.add(pid)
                new_pool.append({**copy.deepcopy(s), "id": pid,
                                 "capital": float(ac.capital), "style": _least_style(new_pool),
                                 "equity": float(ac.capital), "track": [], "iter": 1})
        attempts = 0
        while len(new_pool) < ac.size and attempts < ac.size * 20:
            attempts += 1
            cand = mutate(copy.deepcopy(rng.choice(new_pool)), rng, ac.mutate_rate, ac.mutate_sigma) \
                if new_pool and rng.random() < 0.7 else sample_individual(rng)
            k = _ind_key(cand)
            if k in seen:
                continue
            seen.add(k)
            pid = _next_id(a, "N")
            used_ids.add(pid)
            new_pool.append({**cand, "id": pid,
                             "capital": float(ac.capital), "style": _least_style(new_pool),
                             "equity": float(ac.capital), "track": [], "iter": 1})

    a["players"] = new_pool[: ac.size]
    # 4) 全族保底席（2026-09-21 用户指令"策略风格要非常细分和差异化"）：每个策略族
    #    在阵容中至少 1 席——参与权保障（参考设计 30 种全谱上场），留任由战绩说话。
    #    新族即刻上场（等 GA 随机采样要数小时）。落位规则：只顶替 N/V/G/S 补员中
    #    "非任何族唯一代表"的席位（防保底自己打掉别族唯一席——实测随机命中时
    #    kdj_rev/dual_ma 间歇性消失），先收集后统一落位，绝不静默丢弃。
    try:
        from .strategies import STRATEGIES
        roster = a["players"]
        have = {p["strategy"] for p in roster}
        missing = [f for f in sorted(STRATEGIES) if f not in have]
        if missing:
            pop = state.get("evolution", {}).get("population") or []
            best_of_fam: dict[str, dict] = {}
            for ind in pop:
                f = ind.get("strategy")
                if f in missing and f not in best_of_fam:
                    best_of_fam[f] = copy.deepcopy(ind)
            entries: list[dict] = []
            for f in missing:
                cand = best_of_fam.get(f)
                if cand is None:
                    cand = sample_individual(rng, prefer_family=f, force_family=True)
                if _ind_key(cand) in seen:
                    cand = mutate(cand, rng, ac.mutate_rate, ac.mutate_sigma)
                entries.append(cand)
            fam_count: dict[str, int] = {}
            for p in roster:
                fam_count[p["strategy"]] = fam_count.get(p["strategy"], 0) + 1
            replaceable = [p for p in roster
                           if p["id"].startswith(("N", "V", "G", "S"))
                           and fam_count.get(p["strategy"], 0) >= 2]
            placed = 0
            for cand, victim in zip(entries, reversed(replaceable)):
                roster[roster.index(victim)] = {
                    **cand, "id": _next_id(a, "F"), "capital": float(ac.capital),
                    "style": _least_style(roster), "equity": float(ac.capital),
                    "track": [], "iter": 1}
                placed += 1
            for cand in entries[placed:]:
                if len(roster) < ac.size:
                    roster.append({**cand, "id": _next_id(a, "F"),
                                   "capital": float(ac.capital),
                                   "style": _least_style(roster),
                                   "equity": float(ac.capital), "track": [], "iter": 1})
                    placed += 1
            if placed < len(entries):
                log.warning("【锦标赛】全族保底：%d 个缺席族中 %d 个无法落位"
                            "（可替换席不足），下轮换血再补", len(entries), placed)
            else:
                log.info("【锦标赛】全族保底：新补 %d 个缺席族席位（%s）——"
                         "参与权保障，留任由战绩说话", placed,
                         ",".join(missing[:12]))
    except Exception:  # noqa: BLE001 保底失败不阻塞换血
        log.exception("全族保底席补位失败（忽略）")
    # 5) 风格在场保障（用户指定"从极稳到激进都要有"）：任何风格缺位时，
    #    把最后补员的席位改派到缺位风格（随机/变异体/种子优先让位，保留者与中游不动）
    roster = a["players"]
    for want in STYLE_ORDER:
        if not any((p.get("style") or "均衡") == want for p in roster):
            for p in reversed(roster):
                if p["id"].startswith(("N", "V", "G", "S")):
                    p["style"] = want
                    break
    a["iter_round"] = int(a.get("iter_round", 0)) + 1
    fams: dict[str, int] = {}
    for p in a["players"]:
        fams[p["strategy"]] = fams.get(p["strategy"], 0) + 1
    log.info("【锦标赛】循环迭代：保留Top10中%d名 + 变异体 → 第%d届阵容 %d 人（%s）",
             kept, a["iter_round"], len(a["players"]),
             " ".join(f"{k}×{v}" for k, v in sorted(fams.items(), key=lambda kv: -kv[1])[:6]))
    if persist:
        save_state(state)


def run_tournament(cfg: AppConfig, state: dict, period_days: int | None = None,
                   panel=None, label: str = "历史锦标赛", start=None,
                   persist: bool = True) -> dict | None:
    """全员全窗口锦标赛：分段战绩 + 总榜 + 报告 + 机制回馈 + Top10循环迭代换血。"""
    ac = cfg.arena
    a = state.setdefault("arena", {})
    players = _current_players(cfg, state)
    if panel is None:
        _, panel = qdata.full_panel(cfg)
    if start is not None:
        panel = panel.window(pd.Timestamp(start), panel.dates[-1])
    period_days = period_days or ac.period_days

    log.info("【锦标赛】%s开赛：%d 名选手 × 窗口 %s ~ %s（%d 交易日，段长%d）",
             label, len(players), panel.dates[0].date(), panel.dates[-1].date(),
             len(panel.dates), period_days)

    results: dict[str, dict] = {}
    workers = resolve_workers(cfg)
    if workers > 1 and len(players) >= workers * 2:
        try:
            with ProcessPoolExecutor(max_workers=workers, initializer=_arena_init,
                                     initargs=(panel, cfg)) as ex:
                for r in ex.map(_arena_run_player, players):
                    results[r["id"]] = r
            log.info("【锦标赛】并行评估完成（%d 进程）", workers)
        except Exception as e:  # noqa: BLE001
            log.warning("锦标赛并行失败，回退串行: %s", e)
            results = {}
    if not results:
        _arena_init(panel, cfg)
        for p in players:
            results[p["id"]] = _arena_run_player(p)

    # ---- 战绩统计
    rows = []
    n_failed = 0
    for p in players:
        r = results.get(p["id"])
        if not r or not r.get("ok"):
            n_failed += 1
            continue
        m = r["metrics"]
        segs = _segment_returns(r["equity"], period_days)
        rows.append({
            "id": p["id"], "strategy": p["strategy"], "params": p["params"],
            "sizing": p.get("sizing") or "equal",
            "sizing_params": dict(p.get("sizing_params") or {}),
            "style": p.get("style") or "均衡",
            "final_equity": float(r["equity"].iloc[-1]),
            "total_return": m["total_return"], "cagr": m["cagr"], "max_dd": m["max_dd"],
            "sharpe": m["sharpe"], "calmar": m["calmar"], "win_rate": m["win_rate"],
            "n_trades": m["n_trades"], "exposure": m["exposure"],
            "adapt": composite_score(m, cfg),
            # 用户口径「只认最终的盈利和稳定」：盈稳分 = 累计收益 − 1.5×|最大回撤|
            "ps": round(m["total_return"] - 1.5 * abs(m["max_dd"]), 4),
            # 实盘口径：历史回撤若超实盘停机线（-10%），实盘根本拿不住（早被强平停机）
            "halt_ok": bool(m["max_dd"] >= -cfg.risk.drawdown_halt_pct),
            "pos_periods": sum(1 for s in segs if s["ret"] > 0),
            "n_periods": len(segs),
            "segs": segs, "equity": r["equity"],
        })
    if not rows:
        log.error("锦标赛无有效选手结果")
        return None
    rows.sort(key=lambda x: x["ps"], reverse=True)  # 总榜首序=盈利+稳定（用户指定口径）

    # ---- 机制回馈：前 feed_top 名（按含回撤惩罚的适应分）注入 GA 种群
    feed = sorted(rows, key=lambda x: x["adapt"], reverse=True)[: ac.feed_top]
    pop = state["evolution"].setdefault("population", [])
    fed_keys = {_ind_key(p) for p in pop}
    n_fed = 0
    for r in feed:
        ind = _genes(r)
        k = _ind_key(ind)
        if k not in fed_keys:
            fed_keys.add(k)
            pop.append(ind)
            n_fed += 1
    state["evolution"]["population"] = pop[-48:]  # 种群快照上限，防止无限膨胀
    if persist and n_fed:
        log.info("【锦标赛】机制回馈：%d 名优胜者基因注入 GA 种群", n_fed)

    # ---- 循环迭代（用户指定机制）：下一轮阵容 = 本轮Top10原样保留 + 其变异体 + 新基因
    # 选手池不再永久冻结——每届锦标赛后围绕前10名重组，前瞻轨道由迭代阵容继续累积
    _respawn_from_top(cfg, state, feed, rows, persist=persist)

    rep = _write_report(cfg, state, rows, period_days, label, n_failed)
    a["last_tournament"] = {"date": dt.date.today().isoformat(), "label": label,
                            "n_players": len(rows), "n_failed": n_failed,
                            "best_id": rows[0]["id"], "best_ret": round(rows[0]["total_return"], 4),
                            "best_ps": rows[0]["ps"], "best_halt_ok": rows[0]["halt_ok"],
                            "n_halt_ok": sum(1 for r in rows if r["halt_ok"]),
                            "mean_ret": round(float(np.mean([r["total_return"] for r in rows])), 4),
                            "report": rep["report"]}
    a["results_cache"] = [{"id": r["id"], "final_equity": round(r["final_equity"], 2),
                           "total_return": round(r["total_return"], 4),
                           "max_dd": round(r["max_dd"], 4), "sharpe": round(r["sharpe"], 2),
                           "adapt": round(r["adapt"], 4)} for r in rows]
    if persist:
        save_state(state)
    maybe_write_board(cfg, state)
    return rep


def _write_report(cfg: AppConfig, state: dict, rows: list[dict], period_days: int,
                  label: str, n_failed: int) -> dict:
    """战绩报告：总榜 + 分段战绩 + 回馈名单（logs/arena_*.md + 两份CSV）。"""
    os.makedirs(LOGS_DIR, exist_ok=True)
    today_str = dt.date.today().strftime("%Y%m%d")
    n_periods = rows[0]["n_periods"]
    seg_table: dict[int, dict] = {}
    for r in rows:
        for s in r["segs"]:
            t = seg_table.setdefault(s["idx"], {"start": s["start"], "end": s["end"], "rets": []})
            t["rets"].append((r["id"], s["ret"]))

    lines = [f"# 百团锦标赛 · {label}",
             f"- 生成: {dt.datetime.now():%Y-%m-%d %H:%M} | 团队 {len(rows)} 支"
             f"（{n_failed} 支评估失败自动淘汰）| 本金 {cfg.arena.capital:,.0f}/队（各队独立风控风格）",
             f"- 口径: 冻结参数在历史分段的表现（模拟），非未来收益承诺；"
             f"spawn（{state['arena'].get('spawn_date')}）之后的前瞻轨道另计",
             f"- 分段: {n_periods} 段 × {period_days} 交易日", "",
             "## 总榜（按盈稳分 = 累计收益 − 1.5×|回撤|，用户口径「只认盈利和稳定」）", "",
             "| 排名 | 团队 | 风格 | 策略 | 期末权益 | 累计 | 年化 | 回撤 | 夏普 | 正收益段 | 盈稳分 | 实盘线 |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows[:20], 1):
        lines.append(f"| {i} | {r['id']} | {r.get('style', '均衡')} | {r['strategy']} | {r['final_equity']:,.0f} | "
                     f"{r['total_return']*100:+.1f}% | {r['cagr']*100:+.1f}% | {r['max_dd']*100:.1f}% | "
                     f"{r['sharpe']:.2f} | {r['pos_periods']}/{r['n_periods']} | "
                     f"{r['ps']:+.3f} | {'✓' if r['halt_ok'] else '✗'} |")
    if len(rows) > 20:
        lines.append(f"| … | （中位累计 {np.median([r['total_return'] for r in rows])*100:+.1f}% / "
                     f"实盘线存活 {sum(1 for r in rows if r['halt_ok'])}/{len(rows)} 支，共 {len(rows)} 支） | | | | | | | | | | |")
        for i, r in enumerate(rows[-3:], len(rows) - 2):
            lines.append(f"| {i} | {r['id']} | {r.get('style', '均衡')} | {r['strategy']} | {r['final_equity']:,.0f} | "
                         f"{r['total_return']*100:+.1f}% | {r['cagr']*100:+.1f}% | {r['max_dd']*100:.1f}% | "
                         f"{r['sharpe']:.2f} | {r['pos_periods']}/{r['n_periods']} | "
                         f"{r['ps']:+.3f} | {'✓' if r['halt_ok'] else '✗'} |")

    # ---- 风格榜（用户指定"从极稳到极激进都要有"→ 哪个风格最合适的直接证据）
    lines += ["", "## 风格榜（5档风格各自均值战绩——赛制的核心问题：哪种风格适合当下市场）", "",
              "| 风格 | 席位 | 平均累计 | 平均回撤 | 平均盈稳分 | 实盘线存活 | 最佳团队 |",
              "|---|---|---|---|---|---|---|"]
    for style in STYLE_ORDER:
        group = [r for r in rows if (r.get("style") or "均衡") == style]
        if not group:
            continue
        best = max(group, key=lambda x: x["ps"])
        lines.append(f"| {style} | {len(group)} | {np.mean([r['total_return'] for r in group])*100:+.1f}% | "
                     f"{np.mean([abs(r['max_dd']) for r in group])*100:.1f}% | "
                     f"{np.mean([r['ps'] for r in group]):+.3f} | "
                     f"{sum(1 for r in group if r['halt_ok'])}/{len(group)} | "
                     f"{best['id']}（{best['strategy']}，{best['total_return']*100:+.1f}%） |")
    lines += ["", "> 风格参数：极稳(单票5%/敞口×0.3/止损5%) → 保守(8%/×0.5/6%) → 均衡(15%/×1.0/8%) "
              "→ 进取(25%/×1.0/10%) → 激进(40%/×1.0/12%)；锦标赛口径，部署仍守全局用户红线。"]
    lines += ["", "## 分段战绩（每段全部选手的均值/最佳/最差）", "",
              "| 段 | 时间窗口 | 选手均值 | 最佳选手 | 最差选手 |",
              "|---|---|---|---|---|"]
    for idx in sorted(seg_table):
        t = seg_table[idx]
        rets = t["rets"]
        vals = [v for _, v in rets]
        best = max(rets, key=lambda x: x[1])
        worst = min(rets, key=lambda x: x[1])
        lines.append(f"| {idx + 1} | {t['start']}~{t['end']} | {np.mean(vals)*100:+.2f}% | "
                     f"{best[0]} {best[1]*100:+.1f}% | {worst[0]} {worst[1]*100:+.1f}% |")
    lines += ["", "## 机制回馈",
              f"- 总榜适应分前 {cfg.arena.feed_top} 名的基因已注入 GA 种群，"
              "下一轮进化参与冠军/团队竞争（战绩说话）", "",
              "## 读法提示",
              "- 单段冠军≠好策略：看正收益段占比与回撤；**盈稳分（收益−1.5×|回撤|）为总榜首序，即用户口径「只认盈利和稳定」**",
              "- **风格榜回答「哪种风格最合适」**：激进收益高但回撤大常过不了实盘线；极稳回撤小但牛市跑不赢——市场说了算，每届重排",
              "- 「实盘线✗」= 历史回撤超实盘停机线（-10%），实盘根本拿不住——历史收益再高也只配看，不配上场",
              "- 历史锦标赛用于选种；真实本事看 spawn 之后的前瞻轨道（每日 auto 自动推进）"]

    path = os.path.join(LOGS_DIR, f"arena_{today_str}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    # 完整 CSV
    lb = pd.DataFrame([{k: r.get(k) for k in ("id", "style", "strategy", "final_equity", "total_return",
                                              "cagr", "max_dd", "sharpe", "win_rate", "n_trades",
                                              "exposure", "adapt", "ps", "halt_ok",
                                              "pos_periods", "n_periods")}
                       for r in rows])
    lb.to_csv(os.path.join(LOGS_DIR, "arena_leaderboard.csv"), index=False, encoding="utf-8-sig")
    per = [{"id": r["id"], "period": s["idx"] + 1, "start": s["start"], "end": s["end"],
            "ret": round(s["ret"], 5)} for r in rows for s in r["segs"]]
    pd.DataFrame(per).to_csv(os.path.join(LOGS_DIR, "arena_periods.csv"), index=False, encoding="utf-8-sig")
    log.info("【锦标赛】战绩报告 → %s（总榜 %d 名 / %d 段）", path, len(rows), n_periods)
    return {"report": path, "rows": rows, "segments": seg_table}


# ---------------------------------------------------------------- 前瞻轨道

def advance_day(cfg: AppConfig, state: dict, panel=None, persist: bool = True) -> bool:
    """收盘数据就绪后推进全部选手一个交易日（参数冻结 → 模拟实盘锦标赛）。

    实现：自 forward_start 起对窗口重放链式回测（确定性、逐日推进），
    等价于每天用当日真实 OHLC 给所有选手结算一次。
    """
    a = state.setdefault("arena", {})
    players = _current_players(cfg, state, persist=persist)
    if not players:
        return False
    if panel is None:
        _, panel = qdata.full_panel(cfg)
    last = panel.dates[-1]
    last_key = str(last.date())
    if a.get("last_advance") == last_key:
        return False
    if not a.get("forward_start"):
        a["forward_start"] = last_key  # 轨道从下一交易日开始累积
        a["last_advance"] = last_key
        if persist:
            save_state(state)
        log.info("【锦标赛】前瞻轨道起点锚定 %s（明日起每日结算）", last_key)
        return True

    sub = panel.window(pd.Timestamp(a["forward_start"]), last)
    if len(sub.dates) < 2:
        a["last_advance"] = last_key
        return False
    workers = resolve_workers(cfg)
    results: dict[str, dict] = {}
    if workers > 1 and len(players) >= workers * 2:
        try:
            with ProcessPoolExecutor(max_workers=workers, initializer=_arena_init,
                                     initargs=(sub, cfg)) as ex:
                for r in ex.map(_arena_run_player, players):
                    results[r["id"]] = r
        except Exception:  # noqa: BLE001
            results = {}
    if not results:
        _arena_init(sub, cfg)
        for p in players:
            results[p["id"]] = _arena_run_player(p)

    rets = []
    for p in players:
        r = results.get(p["id"])
        if r and r.get("ok"):
            p["equity"] = round(float(r["equity"].iloc[-1]), 2)
            p["track"] = (p.get("track") or [])[-499:] + [
                {"date": last_key, "equity": p["equity"]}]
            rets.append(r["equity"].iloc[-1] / p["capital"] - 1.0)
    if rets:
        summary = {"date": last_key, "n": len(rets),
                   "mean_ret": round(float(np.mean(rets)), 4),
                   "best": max(zip(rets, [p["id"] for p in players]), key=lambda x: x[0]),
                   "worst": min(zip(rets, [p["id"] for p in players]), key=lambda x: x[0])}
        a["history"] = (a.get("history") or [])[-499:] + [summary]
        log.info("【锦标赛】前瞻结算 %s：选手均值 %+.2f%% | 最佳 %s %+.2f%% | 最差 %s %+.2f%%",
                 last_key, summary["mean_ret"] * 100, summary["best"][1],
                 summary["best"][0] * 100, summary["worst"][1], summary["worst"][0] * 100)
    a["last_advance"] = last_key
    if persist:
        save_state(state)
        maybe_write_board(cfg, state)
    return True


def arena_status(state: dict) -> list[str]:
    """给 status 总览用的锦标赛/联赛摘要行。"""
    a = state.get("arena") or {}
    out = []
    if a.get("players"):
        eqs = [p.get("equity", p["capital"]) / p["capital"] - 1 for p in a["players"]]
        styles = {}
        for p in a["players"]:
            styles[p.get("style") or "均衡"] = styles.get(p.get("style") or "均衡", 0) + 1
        style_str = "/".join(f"{s}{n}" for s, n in styles.items())
        out.append(f"锦标赛: {len(a['players'])} 支团队（风格席位 {style_str}）| 前瞻均值 {np.mean(eqs)*100:+.2f}% | "
                   f"最佳 {max(eqs)*100:+.2f}% | 最差 {min(eqs)*100:+.2f}%")
        if a.get("last_tournament"):
            t = a["last_tournament"]
            out.append(f"  上届{t['label']}: 最佳 {t['best_id']} {t['best_ret']*100:+.1f}% | "
                       f"全员均值 {t['mean_ret']*100:+.2f}%（{t['date']}）")
    if a.get("round"):
        streakers = sorted(a.get("players") or [], key=lambda p: -int(p.get("streak", 0)))[:3]
        streak_str = ", ".join(f"{p['id']}({p['strategy']}/{p.get('style', '均衡')})×{p.get('streak', 0)}"
                               for p in streakers if p.get("streak"))
        _rh = a.get("round_history") or []
        _w = str(_rh[-1].get("window", "")) if _rh else ""
        _yrs = _w.split("≈", 1)[1].split("）", 1)[0].strip() if "≈" in _w else ""
        if not _yrs.endswith("年"):
            _yrs = ""
        out.append(f"联赛: 第 {a['round']} 局（随机{_yrs}窗，每队100万，前10晋级+换血）"
                   f"{' | 连胜王: ' + streak_str if streak_str else ''}")
        qualified = a.get("qualified") or []
        if qualified:
            out.append(f"  ★ 稳定前10认证选手: "
                       + ", ".join(f"{q['id']}({q['strategy']})连{q['streak']}局"
                                   for q in qualified[-5:]))
        elif a.get("round_history"):
            last = a["round_history"][-1]
            out.append(f"  上局 {last['window']} 均分{last['mean_score']:.3f} | "
                       f"前10: {', '.join(t['strategy'] for t in last['top10'][:5])}...")
    return out


# ---------------------------------------------------------------- 可视化看板（"头顶上写着策略"）

_BOARD_CSS = """
body{font-family:'Microsoft YaHei',sans-serif;background:#0d1117;color:#e6edf3;margin:0;padding:20px}
h1{font-size:20px} .meta{color:#8b949e;font-size:12px;margin-bottom:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}
.card{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:10px;position:relative}
.card .head{font-weight:bold;font-size:15px;padding:4px 8px;border-radius:6px;background:#1f6feb22;
  color:#79c0ff;display:inline-block;margin-bottom:6px}          /* 头顶：策略名 */
.card.top{border-color:#d29922;background:#1c1a0f}
.card.top .head{background:#d2992233;color:#e3b341}
.card .id{color:#8b949e;font-size:12px}
.card .ret{font-size:20px;font-weight:bold;margin:4px 0}
.pos{color:#3fb950}.neg{color:#f85149}
.badge{display:inline-block;font-size:11px;padding:1px 6px;border-radius:8px;margin-right:4px;
  background:#21262d;color:#8b949e}
.badge.q{background:#1f6feb33;color:#79c0ff}
.badge.fire{background:#6e2c0011;color:#f0883e}
.hist{display:flex;gap:2px;margin-top:6px}
.hist i{width:14px;height:8px;border-radius:2px;background:#30363d;display:block}
.hist i.on{background:#3fb950}
.params{color:#8b949e;font-size:10.5px;margin-top:6px;word-break:break-all}
.sec{margin-top:24px} .sec h2{font-size:15px;border-bottom:1px solid #30363d;padding-bottom:4px}
"""


def write_board(cfg: AppConfig, state: dict) -> str:
    """交易员竞技场看板：每人一张卡片，头顶写策略名，卡片=战绩/连胜/认证。

    每届锦标赛/联赛/每日前瞻结算后自动重写 logs/arena_board.html（浏览器打开，
    页面30秒自刷新）。卡片按最近得分排序；金色边框=最近一局前10；红区=垫底待换血。
    """
    import html as _html

    a = state.get("arena") or {}
    players = a.get("players") or []
    if not players:
        return ""
    qualified_ids = {q["id"] for q in (a.get("qualified") or [])}
    last_round = (a.get("round_history") or [{}])[-1] or {}
    top_ids = {t["id"] for t in (last_round.get("top10") or [])}
    cache = {r["id"]: r for r in (a.get("results_cache") or [])}

    def ret_color(x: float) -> str:
        return "pos" if x >= 0 else "neg"

    cards = []
    ordered = sorted(players, key=lambda p: -(p.get("score_last") or -9))
    for rank, p in enumerate(ordered, 1):
        ret = p.get("equity", p["capital"]) / p["capital"] - 1.0
        hist = (p.get("top10_hist") or [])[-10:]
        hist_html = "".join(f'<i class="{"on" if h else ""}"></i>' for h in hist)
        badges = []
        if p["id"] in qualified_ids:
            badges.append('<span class="badge q">★认证</span>')
        if int(p.get("streak", 0)) >= 2:
            badges.append(f'<span class="badge fire">🔥连{p.get("streak")}</span>')
        badges.append(f'<span class="badge">{_html.escape(str(p.get("style") or "均衡"))}</span>')
        badges.append(f'<span class="badge">{p.get("sizing", "equal")}</span>')
        tc = cache.get(p["id"])
        params_txt = ", ".join(f"{k}={v}" for k, v in list(p.get("params", {}).items())[:4])
        cards.append(
            f'<div class="card{" top" if p["id"] in top_ids else ""}">'
            f'<div class="head">{_html.escape(str(p["strategy"]))}</div>'
            f'<div class="id">#{rank} · {p["id"]} · 第{p.get("iter", 1)}届</div>'
            f'<div class="ret {ret_color(ret)}">{ret * 100:+.1f}%</div>'
            f'<div class="id">最近得分 {p.get("score_last") if p.get("score_last") is not None else "—"}'
            f'{" | 前瞻" + str(round(p.get("equity", 0), 0)) + "元" if p.get("track") else ""}</div>'
            f'<div>{"".join(badges)}</div>'
            f'<div class="hist" title="近10局前10记录（绿=晋级）">{hist_html}</div>'
            f'<div class="params">{_html.escape(params_txt)}</div>'
            f'</div>')

    t = a.get("last_tournament") or {}
    sec_top = ""
    if top_ids:
        names = ", ".join(sorted(top_ids))
        sec_top = (f'<div class="sec"><h2>🥇 最近一局前10（金色卡框）</h2>'
                   f'<div class="meta">晋级者 streak+1，连续3局前10 → ★认证进 GA 种群；'
                   f'其余选手每局后换血淘汰。本局前10：{names}</div></div>')
    sec_elim = ""
    if a.get("round_history"):
        worst = sorted(cache.values(), key=lambda r: r.get("total_return", 0))[:5]
        if worst:
            rows = "".join(f'<div class="id">❌ {r["id"]}（{r["total_return"] * 100:+.1f}%，'
                           f'回撤{r["max_dd"] * 100:.0f}%）</div>' for r in worst)
            sec_elim = (f'<div class="sec"><h2>💀 上届垫底（已被换血淘汰出阵容）</h2>{rows}'
                        f'<div class="meta">联赛每局只留前10原班+变异体，其余全部出局重练</div></div>')

    # —— 多维实战Top10区块（用户指令2026-09-21：各维度评价实战出来的最好前10）——
    sec_dims = ""
    try:
        ps = a.get("pstats") or {}
        players_by_id = {p["id"]: p for p in players}
        dim_cards = []
        for name, fn, desc in DIMENSIONS:
            cands = [s for s in ps.values() if s["n"] >= 20]
            if not cands:
                continue
            rev = not name.startswith("🪂")
            ranked = sorted(cands, key=fn, reverse=rev)[:5]
            items = []
            for i, s in enumerate(ranked, 1):
                v = fn(s)
                p = players_by_id.get(s["id"]) or {}
                nm = f'{s["id"]}·{p.get("strategy") or s.get("strategy") or "?"}'
                vt = f"{int(v)}次" if name.startswith("🏅") else f"{v * 100:+.1f}%"
                items.append(f'<div class="id">{i}. {_html.escape(nm)} '
                             f'<b class="{"pos" if v >= 0 else "neg"}">{vt}</b></div>')
            dim_cards.append(f'<div class="card"><div class="head">{_html.escape(name)}</div>'
                             f'<div class="id" style="color:#8b949e">{_html.escape(desc)}</div>'
                             f'{"".join(items)}</div>')
        if dim_cards:
            sec_dims = (f'<div class="sec"><h2>📊 多维实战Top10（8维度·联赛累积口径）</h2>'
                        f'<div class="grid">{"".join(dim_cards)}</div>'
                        f'<div class="meta">完整榜单 CLI: run.py top10 | '
                        f'logs/top10_*.md 每批联赛后自动刷新</div></div>')
    except Exception:  # noqa: BLE001
        log.debug("多维榜区块渲染失败")

    doc = (f'<!DOCTYPE html><html><head><meta charset="utf-8">'
           f'<meta http-equiv="refresh" content="30">'
           f'<title>交易员竞技场</title><style>{_BOARD_CSS}</style></head><body>'
           f'<h1>🏟️ 百团竞技场 · {len(players)} 支团队 × {cfg.arena.capital:,.0f} 元/队（极稳/保守/均衡/进取/激进 各1/5）</h1>'
           f'<div class="meta">第 {a.get("round", 0)} 局 | 更新 {dt.datetime.now():%Y-%m-%d %H:%M:%S} | '
           f'上届锦标赛最佳: {t.get("best_id", "—")} {t.get("best_ret", 0) * 100 if t else 0:+.1f}% | '
           f'页面30秒自动刷新 · 历史战绩口径=冻结参数模拟，前瞻轨道=spawn后真实推进</div>'
           f'{sec_top}<div class="grid">{"".join(cards)}</div>{sec_elim}{sec_dims}'
           f'</body></html>')
    os.makedirs(LOGS_DIR, exist_ok=True)
    path = os.path.join(LOGS_DIR, "arena_board.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    return path


def live_race(cfg: AppConfig, state: dict, top_n: int = 15) -> str:
    """100名交易员盘中实赛榜（用户指令2026-09-21："不同策略的100名交易员
    同时开工比赛"）。

    口径（日频系统）：各选手冻结策略在上一交易日收盘数据上的目标持仓
    （昨日决策→今日持有），今日浮动=Σ w×(现价/昨收−1)（行情缺失部分按
    覆盖权重归一）。正式战绩仍以收盘结算（advance_day→前瞻轨道）为准，
    本榜为盘中实时视图，只读不写 state。
    """
    a = state.get("arena") or {}
    players = a.get("players") or []
    if not players:
        return "（阵容为空）"
    _, panel = qdata.full_panel(cfg)
    rows: list[dict] = []
    code_set: set[str] = set()
    for p in players:
        try:
            strat = strat_lib.get_strategy(p["strategy"])()
            w = strat.target_weights(panel, p["params"])
            sizing = get_sizing(p.get("sizing") or "equal")()
            w = sizing.apply(w, panel, p.get("sizing_params") or {})
            last = w.iloc[-1]
            holds = {c: float(v) for c, v in last.items() if float(v) > 0.001}
        except Exception:  # noqa: BLE001
            holds = {}
        code_set |= set(holds)
        rows.append({"p": p, "holds": holds})
    quotes: dict[str, dict] = {}
    codes = sorted(code_set)
    for i in range(0, len(codes), 50):
        quotes.update(qdata.spot_quotes_light(codes[i:i + 50]))
    ranked: list[tuple[float, dict, dict]] = []
    for r in rows:
        ret = cov = 0.0
        for c, wgt in r["holds"].items():
            q = quotes.get(c)
            if not q or q.get("prev_close", 0) <= 0 or q.get("price", 0) <= 0:
                continue
            cov += wgt
            ret += wgt * (q["price"] / q["prev_close"] - 1.0)
        ranked.append((ret / cov if cov > 0.01 else 0.0, r["p"], r["holds"]))
    ranked.sort(key=lambda x: -x[0])
    n_hold = sum(1 for _, _, h in ranked if h)
    lines = [f"🏃 百名交易员实赛榜（{dt.datetime.now():%Y-%m-%d %H:%M} 盘中实时）",
             f"- 100 队 × 100万虚拟本金 · 持仓生效 {n_hold} 队 | 口径：昨日收盘决策 × 今日实时浮动",
             "- 正式战绩以收盘结算入前瞻轨道为准；本榜为实时视图（只读）", "",
             "| 名次 | 交易员 | 策略 | 风格 | 今日浮动 | 头号持仓 |", "|---|---|---|---|---|---|"]
    for i, (ret, p, holds) in enumerate(ranked[:top_n], 1):
        top_hold = max(holds, key=holds.get) if holds else "—"
        lines.append(f"| {i} | {p['id']} | {p['strategy']} | {p.get('style') or '均衡'} "
                     f"| **{ret * 100:+.2f}%** | {top_hold} |")
    lines += ["", "…", "", "| 名次 | 交易员 | 策略 | 风格 | 今日浮动 |", "|---|---|---|---|---|"]
    for i, (ret, p, _) in enumerate(ranked[-5:], len(ranked) - 4):
        lines.append(f"| {i} | {p['id']} | {p['strategy']} | {p.get('style') or '均衡'} "
                     f"| {ret * 100:+.2f}% |")
    # 族/风格今日赛况
    fam: dict[str, list[float]] = {}
    sty: dict[str, list[float]] = {}
    for ret, p, h in ranked:
        if not h:
            continue
        fam.setdefault(p["strategy"], []).append(ret)
        sty.setdefault(p.get("style") or "均衡", []).append(ret)
    lines += ["", "## 今日赛况（按策略族 / 按风格）", ""]
    for label, d in (("族", fam), ("风格", sty)):
        agg = sorted(((k, sum(v) / len(v), len(v)) for k, v in d.items()),
                     key=lambda t: -t[1])
        txt = " | ".join(f"{k} {m * 100:+.1f}%×{n}" for k, m, n in agg[:6])
        lines.append(f"- 领先{label}：{txt}")
    champ = (state.get("champion") or {}).get("strategy")
    if champ:
        lines.append(f"\n👑 真金赛道（10万模拟盘账户）由冠军 {champ} 执行中"
                      "（晋升管道赢家，非本榜参赛口径）")
    return "\n".join(lines)


def maybe_write_board(cfg: AppConfig, state: dict) -> None:
    """看板重写（失败不影响主流程）。"""
    try:
        write_board(cfg, state)
    except Exception:  # noqa: BLE001
        log.debug("看板重写失败", exc_info=True)


# ------------------------------------------------ 多维实战评价（用户指令 2026-09-21：
# "实战出来最好的前10，各个维度评价：最稳定盈利/盈利概率最高/盈利最多等"）

def _accum_pstats(a: dict, rows: list[dict], top_ids: set,
                  halt_pct: float = 0.10) -> None:
    """联赛每局后累积全员战绩（按基因指纹键控，跨阵容换代延续个人记录）。

    每局=随机1年历史窗全规则撮合（含各队风格风控）——累积口径即"实战样本"。
    存均值而非巨量明细，state 体量恒定（~100键×10字段）。
    halt_ok=样本回撤未破用户停机线的局数（"适合我"的裁决指标，2026-09-21）。
    """
    ps = a.setdefault("pstats", {})
    for r in rows:
        k = _ind_key(r)
        m = r.get("metrics") or {}
        ret = float(r.get("ret") or 0.0)
        dd = float(m.get("max_dd") or 0.0)
        sh = float(m.get("sharpe") or 0.0)
        wr = float(m.get("win_rate") or 0.0)
        s = ps.get(k)
        if s is None:
            s = {"id": r["id"], "strategy": r["strategy"], "style": r.get("style") or "均衡",
                 "sizing": r.get("sizing") or "equal", "n": 0, "ret_sum": 0.0,
                 "win_rounds": 0, "dd_sum": 0.0, "sharpe_sum": 0.0, "wr_sum": 0.0,
                 "ps_sum": 0.0, "best": ret, "worst": ret, "top10": 0, "halt_ok": 0}
            ps[k] = s
        s["id"] = r["id"]  # 展示用最新编号
        s["n"] += 1
        s["ret_sum"] += ret
        s["win_rounds"] += 1 if ret > 0 else 0
        s["dd_sum"] += dd
        s["sharpe_sum"] += sh
        s["wr_sum"] += wr
        s["ps_sum"] += ret - 1.5 * abs(dd)
        s["best"] = max(s["best"], ret)
        s["worst"] = min(s["worst"], ret)
        if dd >= -halt_pct:
            s["halt_ok"] = int(s.get("halt_ok", 0)) + 1
        if r["id"] in top_ids:
            s["top10"] += 1
    ps_last = sorted(ps.items(), key=lambda kv: -kv[1]["n"])[:400]
    a["pstats"] = dict(ps_last)


DIMENSIONS: list[tuple[str, str, str]] = [
    # (维度名, 取数函数, 单位/说明)
    ("💰 盈利最多", lambda s: s["ret_sum"] / s["n"], "平均局收益（每局=1年窗实战）"),
    ("🛡️ 最稳定盈利", lambda s: s["ps_sum"] / s["n"], "平均盈稳分=收益−1.5×|回撤|（用户口径）"),
    ("🎯 盈利概率最高", lambda s: s["win_rounds"] / s["n"], "正收益局占比"),
    ("📐 风险调整最优", lambda s: s["sharpe_sum"] / s["n"], "平均夏普"),
    ("🪂 最抗跌", lambda s: s["dd_sum"] / s["n"], "平均最大回撤（越接近0越好）"),
    ("☄️ 极端行情存活", lambda s: s["worst"], "最差一局的收益（越大越抗炸）"),
    ("✅ 交易胜率最高", lambda s: s["wr_sum"] / s["n"], "局内逐笔交易胜率均值"),
    ("🏅 晋级最稳", lambda s: s["top10"], "历史前10晋级总次数"),
]


def dimension_report(cfg: AppConfig, state: dict, top_n: int = 10,
                     min_rounds: int = 20, write_file: bool = True) -> str:
    """多维实战 Top10：8 个维度各出前十 + 前瞻轨道实战榜，输出文本与 logs/top10_*.md。"""
    a = state.get("arena") or {}
    ps = a.get("pstats") or {}
    players = {p["id"]: p for p in (a.get("players") or [])}
    lines = [f"# 多维实战 Top10（生成 {dt.datetime.now():%Y-%m-%d %H:%M}）",
             f"- 样本：联赛 {a.get('round', 0)} 局累积，每局=随机1年历史窗全规则撮合（100万/队）",
             f"- 入榜门槛：≥{min_rounds} 局（统计显著性）| 维度独立排名，同一名将可横扫多榜", ""]

    def _fmt(sid, val, unit):
        p = players.get(sid) or {}
        return f"{sid}（{p.get('strategy') or '?'}·{p.get('style') or '?'}）"

    any_board = False
    for name, fn, desc in DIMENSIONS:
        cands = [s for s in ps.values() if s["n"] >= min_rounds]
        if not cands:
            continue
        any_board = True
        rev = not name.startswith("🪂")  # 回撤榜：越接近0越好（均值大=更浅）
        ranked = sorted(cands, key=fn, reverse=rev)[:top_n]
        lines += [f"## {name}（{desc}）", "", "| 名次 | 选手 | 数值 | 局数 | 晋级次数 |", "|---|---|---|---|---|"]
        for i, s in enumerate(ranked, 1):
            v = fn(s)
            p = players.get(s["id"]) or {}  # 已淘汰选手回退用 pstats 自存的族/风格
            nm = (f'{s["id"]}（{p.get("strategy") or s.get("strategy") or "?"}'
                  f'·{p.get("style") or s.get("style") or "?"}）')
            txt = f"{v * 100:+.1f}%" if abs(v) <= 10 else f"{v:.3f}"
            if name.startswith("🏅"):
                txt = f"{int(v)}次"
            lines.append(f"| {i} | {nm} | {txt} | {s['n']} | {s['top10']} |")
        lines.append("")

    # —— 前瞻轨道实战榜（spawn 后逐日真实推进=准实盘线）——
    fwd = [(p["id"], p.get("strategy"), p.get("style"),
            p.get("equity", p.get("capital", cfg.arena.capital)) / p.get("capital", cfg.arena.capital) - 1.0)
           for p in (a.get("players") or []) if p.get("track")]
    if fwd:
        any_board = True
        fwd.sort(key=lambda x: x[3], reverse=True)
        lines += ["## 🎬 前瞻轨道实战榜（参数冻结逐日推进＝准实盘）", "",
                  "| 名次 | 选手 | 累计收益 |", "|---|---|---|"]
        for i, (pid, strat, style, r) in enumerate(fwd[:top_n], 1):
            lines.append(f"| {i} | {pid}（{strat}·{style}） | {r * 100:+.2f}% |")
        lines.append("")

    # —— 冠军实盘线（真正的模拟盘账户，10万真金轨道）——
    acct = (state.get("account") or {})
    track = state.get("paper_track") or []
    # 账户字典无 equity 键：官方权益=收盘结算轨道末值；无轨道时才退化为现金（勿把现金当权益虚报浮亏）
    eq = float(track[-1]["equity"]) if track else float(acct.get("cash") or 0.0)
    cap = float(cfg.risk.initial_capital)
    if eq > 0:
        champ = state.get("champion") or {}
        lines += [f"## 👑 冠军实盘线（模拟盘账户：{champ.get('strategy') or '空仓'}）",
                  f"- 账户权益 {eq:,.0f} / 本金 {cap:,.0f} = **{(eq / cap - 1) * 100:+.2f}%**",
                  "- 以上所有榜单均为历史模拟战绩；此行才是真实轨道", ""]
    if not any_board:
        lines.append("（战绩累积中：联赛样本不足，稍后再看）")
    text = "\n".join(lines)
    if write_file:
        try:
            os.makedirs(LOGS_DIR, exist_ok=True)
            path = os.path.join(LOGS_DIR, f"top10_{dt.date.today().strftime('%Y%m%d')}.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(text + "\n")
        except Exception:  # noqa: BLE001
            log.debug("top10 报告落盘失败")
    return text


def verdict_report(cfg: AppConfig, state: dict, min_rounds: int = 50,
                   write_file: bool = True) -> str:
    """“什么策略适合我”大样本裁决报告（用户终极目标，2026-09-21）。

    证据层：联赛累积样本按 策略族×风格 聚合——样本量N/胜率/平均收益/平均回撤/
    停机线存活率（样本回撤未破用户-10%停机线的占比）/最差样本/平均盈稳分。
    自检层：选才有效性只认独立证据（前瞻轨道，2026-09-21 科学口径修正——
    同源对比是循环论证仅作参考，用户红线"不要自我幻觉"）。
    实锤层：前瞻轨道（逐日真实推进）+ 冠军实盘线（模拟盘真实轨道）。
    """
    a = state.get("arena") or {}
    ps = a.get("pstats") or {}
    agg: dict[tuple, dict] = {}
    for s in ps.values():
        key = (s["strategy"], s.get("style") or "均衡")
        c = agg.get(key)
        if c is None:
            c = {"strategy": s["strategy"], "style": s.get("style") or "均衡",
                 "n": 0, "ret_sum": 0.0, "win": 0, "dd_sum": 0.0,
                 "ps_sum": 0.0, "halt": 0, "worst": 1.0, "tops": 0, "genes": 0,
                 "n_halt_cov": 0}
            agg[key] = c
        c["n"] += s["n"]
        c["ret_sum"] += s["ret_sum"]
        c["win"] += s["win_rounds"]
        c["dd_sum"] += s["dd_sum"]
        c["ps_sum"] += s["ps_sum"]
        c["halt"] += int(s.get("halt_ok", 0))
        c["worst"] = min(c["worst"], s["worst"])
        c["tops"] += s["top10"]
        c["genes"] += 1
        if "halt_ok" in s:  # halt_ok 自2026-09-21起累积：覆盖度单独计
            c["n_halt_cov"] += s["n"]
    cells = [c for c in agg.values() if c["n"] >= min_rounds]
    cells.sort(key=lambda c: (c["ps_sum"] / c["n"]) * (c["halt"] / c["n"] if c["n"] else 0),
               reverse=True)

    # 游戏自检（科学口径，2026-09-21 02:40 用户红线"不要自我幻觉"）：
    # 同源对比（认证者从这批局选出再用同批局证明）= 循环论证，仅作参考；
    # 选才有效性只认 game_evo 维护的独立前瞻证据。
    cert_keys = {_ind_key(q) for q in (a.get("qualified") or [])}
    cert_ps = [s for k, s in ps.items() if k in cert_keys and s["n"] >= min_rounds]
    rest_ps = [s for k, s in ps.items() if k not in cert_keys and s["n"] >= min_rounds]
    avg = lambda lst, f: (sum(f(s) for s in lst) / len(lst)) if lst else 0.0  # noqa: E731
    cert_ps_mean = avg(cert_ps, lambda s: s["ps_sum"] / s["n"])
    rest_ps_mean = avg(rest_ps, lambda s: s["ps_sum"] / s["n"])
    gm = a.get("game") or {}
    eff = gm.get("cert_effective")
    eff_txt = ("数据未成熟（诚实口径，不宣称）" if eff is None
               else ("✅ 有效（独立前瞻证据支持）" if eff
                     else "⚠️ 无效——玩法需要进化"))

    regime = state.get("regime") or {}
    acct = state.get("account") or {}
    track = state.get("paper_track") or []
    # 同 top10 报告：官方权益=收盘结算轨道末值，现金只是兜底（曾把现金当权益报出-56%假浮亏）
    eq = float(track[-1]["equity"]) if track else float(acct.get("cash") or 0.0)
    champ = state.get("champion") or {}

    lines = [f"# 「什么策略适合我」大样本裁决（生成 {dt.datetime.now():%Y-%m-%d %H:%M}）",
             f"- 样本：联赛 {a.get('round', 0)} 局 × 100 队，每局=随机1年历史窗全规则实战",
             f"- 你的真实约束：本金10万 | 停机线-10%（实盘风控会强制平仓）| 日频 | 持股3~15日",
             f"- 入榜门槛：家族×风格 聚合样本 ≥{min_rounds} 局", "",
             "## ① 策略族×风格 实战矩阵（按 盈稳分×停机线存活率 排序）", "",
             "| 族×风格 | 样本局数 | 正收益占比 | 平均收益 | 平均回撤 | **停机线存活** | 最差样本 | 盈稳分 | 基因数 |",
             "|---|---|---|---|---|---|---|---|---|"]
    for c in cells[:15]:
        halt_r = c["halt"] / c["n_halt_cov"] if c["n_halt_cov"] else 0.0
        cov = f"（覆盖{c['n_halt_cov']}/{c['n']}）" if c["n_halt_cov"] < c["n"] * 0.9 else ""
        lines.append(
            f"| {c['strategy']}·{c['style']} | {c['n']} | {c['win'] / c['n'] * 100:.0f}% "
            f"| {c['ret_sum'] / c['n'] * 100:+.1f}% | {c['dd_sum'] / c['n'] * 100:.1f}% "
            f"| **{halt_r * 100:.0f}%**{cov} | {c['worst'] * 100:+.1f}% "
            f"| {c['ps_sum'] / c['n'] * 100:+.1f} | {c['genes']} |")
    lines += ["",
              "**读法**：停机线存活率=该类型在100万样本局中回撤没碰到你-10%红线且赚钱的能力；"
              "正收益占比=盈利概率；最差样本=历史最坏一局（你要能睡得着觉的数字）。", ""]
    if cells:
        top3 = cells[:3]
        lines += ["## ② 结论：当前证据下最适合你的类型", ""]
        for i, c in enumerate(top3, 1):
            halt_r = c["halt"] / c["n_halt_cov"] * 100 if c["n_halt_cov"] else None
            halt_txt = (f"{halt_r:.0f}% 的局不触发你的停机线"
                        if c["n_halt_cov"] >= 50 else
                        "停机线存活数据自20260921晨起累积中")
            lines.append(f"**第{i}名：{c['strategy']} · {c['style']}风格** —— "
                         f"{c['n']}局真实样本中 {c['win'] / c['n'] * 100:.0f}% 的局正收益、"
                         f"平均回撤仅 {c['dd_sum'] / c['n'] * 100:.1f}%、"
                         f"{halt_txt}"
                         f"（最坏一局 {c['worst'] * 100:+.1f}%）。")
        lines += ["",
                  f"- 当前市场风格：{regime.get('label') or regime.get('hint_family') or '—'}"
                  f"（风格引擎判定，冠军={champ.get('strategy') or '空仓'}）",
                  "- 注意：以上为历史实战口径；真正实锤=下方实盘轨道", ""]
    lines += ["## ③ 游戏自检：联赛选才有效性（科学口径：只认独立证据）", "",
              f"- 同源参考（有选择偏差，仅展示不作结论）：认证者盈稳分 {cert_ps_mean * 100:+.1f}"
              f" vs 非认证 {rest_ps_mean * 100:+.1f}（n={len(cert_ps)}/{len(rest_ps)}）"
              "——认证者本就是从这批局里选出的，此对比是循环论证",
              f"- 独立证据（前瞻轨道，认证后真实推进）：{gm.get('cert_evidence', '尚未成熟')}",
              f"- **选才有效性：{eff_txt}**", "",
              "## ④ 实锤线（真实时间推进的轨道，样本少但最真）", "",
              f"- 冠军实盘线（模拟盘账户）：权益 {eq:,.0f}（{(eq / float(cfg.risk.initial_capital) - 1) * 100:+.2f}%）",
              "- 前瞻轨道：见 logs/top10_*.md 前瞻榜（逐日推进）", ""]
    text = "\n".join(lines)
    if write_file:
        try:
            os.makedirs(LOGS_DIR, exist_ok=True)
            path = os.path.join(LOGS_DIR, f"verdict_{dt.date.today().strftime('%Y%m%d')}.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(text + "\n")
        except Exception:  # noqa: BLE001
            log.debug("verdict 报告落盘失败")
    return text

