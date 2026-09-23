"""系统状态持久化：账户/冠军策略/进化进度/风控停机，全部落在 state/state.json（原子写）。"""
from __future__ import annotations

import copy
import datetime as dt
import json
import os
import threading

from .config import STATE_FILE, ensure_dirs, load_config

_LOCK = threading.Lock()
_STATE: dict | None = None

# 跨线程状态写锁（2026-09-22 盘中伴生联赛上线：会话线程与联赛线程共享 state dict，
# 任何"变更 state 子树 + save_state"的临界区必须持有本锁，防 json.dumps 撞上并发
# 增删键（RuntimeError/dict changed size）与撕裂快照——16:35 state 污染事故的线程版防线）。
# RLock：临界区内可能嵌套调用 save_state（如 _respawn_from_top），同线程可重入。
STATE_LOCK = threading.RLock()

DEFAULT_STATE: dict = {
    "version": 1,
    "created_at": "",
    # 模拟账户（真实账户权益由 QMT 查询，此处仅 paper 用）
    "account": {
        "cash": 100_000.0,
        # positions[code] = {shares, available, locked:{date:qty}, cost, last_buy_date}
        "positions": {},
        "equity_high": 100_000.0,
        "day_key": "",             # 当日 YYYYMMDD，用于日熔断重置
        "day_start_equity": 100_000.0,
        "daily_pnl": 0.0,
    },
    # 现任冠军 {"strategy","params","holdout":{score,metrics...},"promoted_at","gen"}
    "champion": None,
    "champion_retired": [],
    "evolution": {
        "generation": 0,
        "last_run": None,
        "population": [],          # 精英池快照，跨次续跑
        "history": [],             # 每代最优记录
        "top10": [],               # 本轮前10名选手快照（策略+参数+得分），供观察与复盘
        "promote_date": None,      # 样本外晋升尝试计数（按日重置，防磨刷）
        "promote_count": 0,
    },
    "risk": {
        "halt": False,
        "halt_reason": None,
        "halted_at": None,
        "daily_breaker_date": None,  # 当日熔断触发日 YYYYMMDD（次日自动恢复）
    },
    # 模拟实盘轨道：[{date, cash, market_value, equity, n_positions}]
    "paper_track": [],
    # 模拟/实盘成交流水（追加式）
    "trade_log": [],
    "orders_today": [],
    "daily_breakdowns": [],       # [{date, equity, ret, reason}]
    # auto 调度去重标记（每类任务每天只跑一次）
    "auto": {
        "last_data_date": None,
        "last_evolve_date": None,
        "last_prep_date": None,
    },
    # 冠军团队（资产组合：不同策略族各出一人，资金均分；champion=队长兼容展示）
    "team": [],
    # 机制复盘（总结报告 + 触发的机制调整，审计留痕）
    "reviews": [],
    "meta": {
        "champion_decay": False,   # 冠军衰退信号（周度复盘置位，进化引擎消费后清零）
        "stress_defense": False,   # 随机取点体检防御态（体检未过置位：曝光≤0.5，新团队上位/体检通过解除）
        "last_review_week": None,
        "last_wf_week": None,      # walk-forward 链式验证（每周末一次）
        # 机制事件计数（统计中心：挣扎过程也可见）
        "promotions_total": 0,     # 冠军/团队 晋升总次数
        "stagnations_total": 0,    # 进化停滞触发总次数
        "immigrants_total": 0,     # 累计注入移民个体数
    },
    # 市场风格引擎（每晚更新：风格快照/族适配度/曝光系数/进化提示）
    "regime": {
        "snapshot": None,
        "history": [],
        "exposure_scale": 1.0,
        "hint_family": None,
    },
    # 随机取点体检留痕（每日：团队在历史随机窗口的压力验证结果）
    "stress_history": [],
    # 风控事件审计（熔断/停机，统计中心可见）
    "risk_events": [],
}


def _merge_defaults(state: dict) -> dict:
    for k, v in DEFAULT_STATE.items():
        if k not in state:
            state[k] = copy.deepcopy(v)
        elif isinstance(v, dict):
            for k2, v2 in v.items():
                if k2 not in state[k]:
                    state[k][k2] = copy.deepcopy(v2)
    return state


def load_state() -> dict:
    global _STATE
    with _LOCK:
        if _STATE is not None:
            return _STATE
        ensure_dirs()
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, encoding="utf-8") as f:
                _STATE = _merge_defaults(json.load(f))
        else:
            _STATE = copy.deepcopy(DEFAULT_STATE)
            _STATE["created_at"] = dt.datetime.now().isoformat(timespec="seconds")
            # 新建账户初始资金对齐当前配置（曾发生默认值与 config 口径漂移：100万≠10万）
            cap = float(load_config().risk.initial_capital)
            for k in ("cash", "equity_high", "day_start_equity"):
                _STATE["account"][k] = cap
    return _STATE


def save_state(state: dict | None = None) -> None:
    global _STATE
    with _LOCK:
        s = state if state is not None else _STATE
        if s is None:
            return
        ensure_dirs()
        # 状态写锁持有者之外的调用方（单线程路径）也过同一把锁：与其他线程的
        # 变更临界区互斥，保证 dumps 期间无并发增删键
        with STATE_LOCK:
            tmp = STATE_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(s, f, ensure_ascii=False, indent=1, default=str)
            os.replace(tmp, STATE_FILE)
        _STATE = s


def reset_account(state: dict, cash: float) -> None:
    """清空模拟账户（模拟盘用），保留进化进度。"""
    state["account"] = {
        "cash": float(cash),
        "positions": {},
        "equity_high": float(cash),
        "day_key": "",
        "day_start_equity": float(cash),
        "daily_pnl": 0.0,
    }
    state["paper_track"] = []
    state["trade_log"] = []


def halt_now(state: dict, reason: str) -> None:
    state["risk"]["halt"] = True
    state["risk"]["halt_reason"] = reason
    state["risk"]["halted_at"] = dt.datetime.now().isoformat(timespec="seconds")
    # 风控事件审计（统计中心可见）
    state.setdefault("risk_events", []).append({
        "date": dt.date.today().isoformat(), "type": "halt", "detail": reason})
    state["risk_events"] = state["risk_events"][-100:]
    save_state(state)


def resume(state: dict) -> None:
    """人工复盘后恢复（run.py resume）。

    同时重置回撤高水位与日熔断基线为当前账户估值——否则停机时的旧高水位
    会让恢复后首个 tick 再次触发 -10% 停机（恢复功能自锁，风控专家审查 P0#1）。
    语义：人工点击 resume = 人工确认"以当前权益为新基线重新开始"。
    """
    acc = state["account"]
    from .futures import position_value
    mv = sum(position_value(c, p) for c, p in acc.get("positions", {}).items())
    equity = float(acc.get("cash", 0.0) or 0.0) + mv
    acc["equity_high"] = equity
    acc["day_start_equity"] = equity
    state["risk"]["halt"] = False
    state["risk"]["halt_reason"] = None
    state["risk"]["halted_at"] = None
    state["risk"]["daily_breaker_date"] = None
    save_state(state)
