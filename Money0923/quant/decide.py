"""决策层：冠军信号 → 目标组合 → 风控过滤后的次日订单清单。

约定：订单在 T-1 日收盘数据上生成，T 日开盘执行（与回测撮合模型一致）。
无冠军或停机状态下生成空单（空仓等待 / 人工复盘）。
"""
from __future__ import annotations

import json
import logging

import pandas as pd

from . import data as qdata
from . import strategies as strat_lib
from .config import AppConfig
from .risk import RiskManager
from .sizing import get_sizing
from .state import save_state

log = logging.getLogger("quant.decide")


def account_equity(state: dict, prices: dict[str, float]) -> float:
    from .futures import futures_meta
    from . import repo as qrepo
    acc = state["account"]
    mv = 0.0
    for c, pos in acc["positions"].items():
        if str(c).startswith("F."):
            # 期货现金池模型：cash 已含名义现金流，市值=带符号手数×乘数×价
            p = prices.get(c, 0.0) or pos.get("avg_entry", 0.0)
            mv += pos.get("lots", 0) * futures_meta(str(c))["mult"] * p
            continue
        p = prices.get(c, 0.0) or pos.get("cost", 0.0)
        mv += pos.get("shares", 0) * p
    # 在途国债逆回购本金计入权益（借出≠亏损：资金T+1开市前带息归还）
    return acc["cash"] + mv + qrepo.open_principal(state)


def team_members(state: dict) -> list[dict]:
    """冠军团队（资产组合）；无团队时回退单冠军；都没有→空。"""
    team = state.get("team") or []
    if not team and state.get("champion"):
        team = [state["champion"]]
    return team


def team_fingerprint(state: dict) -> list:
    """团队指纹：[(策略, 仓位策略, 基因json)]，用于备单→执行之间检测团队是否变更。"""
    return [(m.get("strategy"), m.get("sizing") or "equal",
             json.dumps({"p": m.get("params"), "sp": m.get("sizing_params") or {}}, sort_keys=True))
            for m in team_members(state)]


def team_target_weights(cfg: AppConfig, state: dict, panel) -> "pd.DataFrame":
    """团队合成目标权重：每个成员（不同策略族）资金均分，权重相加后求平均。
    每个成员的仓位控制基因（sizing）在合成前先叠加到自己的信号上。"""
    members = team_members(state)
    if not members:
        raise ValueError("暂无冠军团队")
    wsum = None
    for m in members:
        w_m = strat_lib.get_strategy(m["strategy"])().target_weights(panel, m["params"]).astype(float)
        sizing = get_sizing(m.get("sizing") or "equal")()
        w_m = sizing.apply(w_m, panel, m.get("sizing_params") or {})
        # fill_value=0 并集合并：CTA 成员带 F.* 列、股票成员无 → 缺失按 0 而非 NaN
        # （CTA 自服务架构下成员权重列可以不同构，绝不让 NaN 漏进订单层）
        wsum = w_m if wsum is None else wsum.add(w_m, fill_value=0.0)
    return wsum / len(members)


def vol_target_scale(cfg: AppConfig, state: dict) -> float:
    """组合波动率目标缩放（理性仓位，与回测引擎同公式）。

    用真实轨道（paper_track，含实盘日）近20日收益估实现年化波动：
    ann_vol > target_vol → scale = max(vol_scale_floor, target/ann)。
    轨道不足20个收益点时返回 1.0（不缩放）——回测端用自身模拟权益序列，
    两端口径在轨道建立后一致。
    """
    import math
    import statistics
    risk = cfg.risk
    if risk.target_vol <= 0:
        return 1.0
    track = state.get("paper_track") or []
    if len(track) < 21:
        return 1.0
    vals = [float(t.get("equity", 0) or 0) for t in track[-21:]]
    rets = [vals[i + 1] / vals[i] - 1.0 for i in range(len(vals) - 1) if vals[i] > 0]
    if len(rets) < 20:
        return 1.0
    ann = statistics.pstdev(rets) * math.sqrt(252.0)
    if ann <= risk.target_vol:
        return 1.0
    floor = max(0.05, float(getattr(risk, "vol_scale_floor", 0.25)))
    return max(floor, risk.target_vol / ann)


def _negative_screen(target_w: dict, cfg: AppConfig) -> dict:
    """负面清单终检（亏损/暴雷/行业/黑名单）：防股票池缓存与最新披露脱节。
    F.* 期货无业绩/行业语义，天然不命中（名称关键词匹配空名）。"""
    try:
        from . import fundamental
        names: dict[str, str] = {}
        try:
            uni = qdata.load_universe()
            names = dict(zip(uni["code"].astype(str), uni["name"].astype(str)))
        except Exception:  # noqa: BLE001
            pass
        for c in target_w:
            names.setdefault(c, "")
        excl = fundamental.build_exclusions(cfg, list(target_w), names)
        for c in [x for x in target_w if x in excl]:
            log.warning("负面清单剔除目标 %s: %s", c, excl[c])
            target_w.pop(c)
    except Exception as e:  # noqa: BLE001
        log.warning("负面清单终检失败（沿用目标）: %s", e)
    return target_w


def _sleeve_prices(codes: set, panel) -> dict[str, float]:
    """最近收盘价（含持仓）；F.* 期货用日线缓存收盘（面板不含期货列）。"""
    prices: dict[str, float] = {}
    for c in codes:
        if str(c).startswith("F."):
            from .futures import last_close
            prices[c] = last_close(str(c))
            continue
        s = panel.close[c].dropna()
        prices[c] = float(s.iloc[-1]) if len(s) else 0.0
    return prices


def _prepare_sleeve_orders(cfg: AppConfig, state: dict, panel,
                           today_key: str | None) -> tuple[list, dict]:
    """分仓制订单编排（用户指令"策略风格要非常差异化和多种多样"）：
    逐仓独立备单（仓内权益/现金/持仓/停机状态视图），同票冲突规则
    （他仓已持有→本仓跳过留痕），订单带 sleeve 标签贯穿执行端。"""
    from . import sleeves as qsl
    from .risk import RiskManager
    from .futures import is_futures as _is_fut
    today_key = today_key or pd.Timestamp(panel.dates[-1]).strftime("%Y%m%d")
    if state["risk"]["halt"]:
        state["orders_today"] = []
        log.info("账户级风控停机：全仓不生成订单（人工复盘后 run.py resume）")
        return [], {"reason": "halted"}
    orders_all: list[dict] = []
    for sv in state["sleeves"]:
        if not sv.get("members"):
            continue  # 空仓/退役仓不备单
        if qsl.halted(sv) or sv.get("retired"):
            log.info("【分仓】%s 停机/退役 → 本轮不备新单（离场纪律单盘中另走）",
                     sv["id"])
            continue
        held_elsewhere: set[str] = set()
        for other in state["sleeves"]:
            if other is not sv:
                held_elsewhere |= set(qsl.sleeve_positions(state, other))
        # 成员权重合成（与 team_target_weights 同构：成员均分，fill_value=0 并集）
        wsum = None
        for m in sv["members"]:
            w_m = strat_lib.get_strategy(m["strategy"])().target_weights(
                panel, m["params"]).astype(float)
            sizing = get_sizing(m.get("sizing") or "equal")()
            w_m = sizing.apply(w_m, panel, m.get("sizing_params") or {})
            wsum = w_m if wsum is None else wsum.add(w_m, fill_value=0.0)
        if wsum is None:
            continue
        last = wsum.iloc[-1] / len(sv["members"])
        target_w = {c: float(v) for c, v in last.items()
                    if float(v) > 0 or (_is_fut(c) and float(v) != 0)}
        # S1=冠军仓：保留风格引擎曝光缩放语义；S2/S3 全目标暴露——各仓风格
        # 本就互不相干，多样性不许被单一冠军的错配全局降档（风险归各仓停机线）
        if sv["id"] == "S1":
            scale = float(state.get("regime", {}).get("exposure_scale", 1.0) or 1.0)
            if scale < 1.0:
                target_w = {c: v * scale for c, v in target_w.items()}
                log.info("【分仓】S1 风格引擎曝光 ×%.1f 已应用", scale)
        target_w = _negative_screen(target_w, cfg)
        for c in [c for c in target_w if c in held_elsewhere]:
            log.info("【分仓】%s 目标 %s 已由他仓持有 → 跳过（同票冲突规则）",
                     sv["id"], c)
            target_w.pop(c)
        prices = _sleeve_prices(set(target_w) | set(qsl.sleeve_positions(state, sv)),
                                panel)
        seq = qsl.sleeve_equity(state, sv, prices)
        view = {"account": {"cash": sv["cash"],
                            "positions": qsl.sleeve_positions(state, sv)},
                "risk": sv["risk"]}
        rm = RiskManager(cfg, view)
        orders = rm.plan_orders(target_w, view["account"]["positions"],
                                {c: {"price": p} for c, p in prices.items()},
                                seq, sv["cash"], today_key)
        for o in orders:
            o["sleeve"] = sv["id"]
        orders_all.extend(orders)
        log.info("【分仓】%s 备单 %d 笔（目标 %d 只 / 仓内权益 %.0f）",
                 sv["id"], len(orders), len(target_w), seq)
    state["orders_today"] = orders_all
    state["orders_fingerprint"] = qsl.deployment_fingerprint(state)
    save_state(state)
    log.info("已生成次日订单 %d 笔（分仓制 %d 仓：各仓独立风控与停机线）",
             len(orders_all), len(state["sleeves"]))
    return orders_all, {"sleeves": [qsl.sleeve_label(sv) for sv in state["sleeves"]]}


def prepare_orders(cfg: AppConfig, state: dict, panel=None,
                   today_key: str | None = None) -> tuple[list, dict]:
    """生成次日订单，写入 state['orders_today']。

    分仓制（2026-09-21 用户"策略风格非常差异化和多种多样"指令落地）：
    多队并行分仓各自独立备单（S1=现任冠军团队；S2/S3=联赛认证池多样性
    选队），每仓独立 10% 停机线与现金；无分仓时回退冠军团队单路径。
    """
    from . import sleeves as qsl
    if not state.get("sleeves"):
        qsl.ensure_sleeves(state, cfg)
    if state.get("sleeves"):
        qsl.sync_champion_sleeve(state)
        if panel is None:
            _, panel = qdata.full_panel(cfg)
        return _prepare_sleeve_orders(cfg, state, panel, today_key)

    members = team_members(state)
    if not members:
        state["orders_today"] = []
        log.info("暂无冠军团队：保持空仓（进化出合格团队前不开仓，这是设计行为）")
        return [], {"reason": "no_team"}
    if state["risk"]["halt"]:
        state["orders_today"] = []
        log.info("风控停机中：不生成订单（人工复盘后 run.py resume）")
        return [], {"reason": "halted"}

    if panel is None:
        _, panel = qdata.full_panel(cfg)
    w = team_target_weights(cfg, state, panel)
    last = w.iloc[-1]
    # 期货双向（F.* 保留负权重=空头目标）；股票/ETF 纯多头资产只取正权重
    from .futures import is_futures as _is_fut
    target_w = {c: float(v) for c, v in last.items()
                if float(v) > 0 or (_is_fut(c) and float(v) != 0)}

    # 风格引擎曝光系数：错配/敌对风格自动降暴露（只降意愿，不越风控红线）
    scale = float(state.get("regime", {}).get("exposure_scale", 1.0) or 1.0)
    if scale < 1.0:
        target_w = {c: v * scale for c, v in target_w.items()}
        log.info("风格引擎曝光系数 ×%.1f 已应用（目标权重已缩放）", scale)

    # 波动率目标（与回测引擎同源公式）：组合近20日实现年化波动超 target_vol → 线性降杠杆。
    # 轨道数据不足时不缩放（回测端用模拟权益序列，两端在轨道建立后口径一致）。
    vol_scale = vol_target_scale(cfg, state)
    if vol_scale < 1.0:
        target_w = {c: v * vol_scale for c, v in target_w.items()}
        log.info("波动率目标降杠杆 ×%.2f（近20日实现波动超目标 %.0f%%）",
                 vol_scale, cfg.risk.target_vol * 100)

    # 负面清单终检（亏损/暴雷/行业/黑名单）：防股票池缓存与最新披露脱节
    try:
        from . import fundamental
        names: dict[str, str] = {}
        try:
            uni = qdata.load_universe()
            names = dict(zip(uni["code"].astype(str), uni["name"].astype(str)))
        except Exception:  # noqa: BLE001
            pass
        for c in target_w:
            names.setdefault(c, "")
        excl = fundamental.build_exclusions(cfg, list(target_w), names)
        for c in [x for x in target_w if x in excl]:
            log.warning("负面清单剔除目标 %s: %s", c, excl[c])
            target_w.pop(c)
    except Exception as e:  # noqa: BLE001
        log.warning("负面清单终检失败（沿用目标）: %s", e)

    # 最近收盘价（含持仓股，用于市值估算）；F.* 期货用日线缓存收盘（面板不含期货列）
    codes = set(target_w) | set(state["account"]["positions"])
    prices: dict[str, float] = {}
    for c in codes:
        if str(c).startswith("F."):
            from .futures import last_close
            prices[c] = last_close(str(c))
            continue
        s = panel.close[c].dropna()
        prices[c] = float(s.iloc[-1]) if len(s) else 0.0
    price_map = {c: {"price": p} for c, p in prices.items()}

    equity = account_equity(state, prices)
    today_key = today_key or pd.Timestamp(panel.dates[-1]).strftime("%Y%m%d")
    rm = RiskManager(cfg, state)
    orders = rm.plan_orders(target_w, state["account"]["positions"], price_map,
                            equity, state["account"]["cash"], today_key)
    state["orders_today"] = orders
    state["orders_fingerprint"] = team_fingerprint(state)  # 备单→执行之间团队变更检测用
    save_state(state)
    log.info("已生成次日订单 %d 笔（目标持仓 %d 只 / 账户约 %.0f 元）",
             len(orders), len(target_w), equity)
    return orders, {"target_w": target_w, "equity": equity}
