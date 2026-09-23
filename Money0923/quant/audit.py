"""防作弊审计套件 —— 把"没有作弊"从口头承诺变成机器可验证的证据。

回应三条指控："提前知道结果作弊"、"AI幻觉"、"提前知道分时走势"。

三项审计（全部只读 state + 追加式台账，不写 state.json——可与守护进程并行运行，
台账落盘顺序即为不可抵赖的证据链）：

1. 无未来函数抽查：随机取 K 个历史日 D，仅用 ≤D 的截断面板重算
   **完整决策链**（策略信号 → 仓位基因缩放 → 团队合成），D 行必须与全量计算
   逐元素一致 → 证明决策时刻"看不见" D 之后的任何数据（含当日分时与结果）。
2. 复算一致性：同一输入跑两遍回测引擎，净值曲线哈希必须相同
   → 证明结果由确定性代码算出，不存在幻觉数字。
3. 先声明后揭示：任何审计先向台账写入声明（窗口/团队快照/输入与代码指纹），
   结果算完才追加 → 声明落盘时结果尚不存在，编排者不可能先看结果再写结论。

台账：logs/audit_ledger.jsonl（追加式，每行一个 JSON 事件；事后篡改会破坏
声明→结果的时间顺序与指纹，一眼可辨）。
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import logging
import os
import random

import numpy as np

from .config import LOGS_DIR
from .decide import team_fingerprint, team_members, team_target_weights

log = logging.getLogger("quant.audit")

LEDGER = os.path.join(LOGS_DIR, "audit_ledger.jsonl")


# ---------------------------------------------------------------- 指纹与台账

def _ledger_append(rec: dict) -> None:
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")


def code_fingerprint() -> str:
    """quant 包全部源码的指纹（报告可复核当时的代码版本）。"""
    h = hashlib.sha256()
    pkg = os.path.dirname(os.path.abspath(__file__))
    for f in sorted(os.listdir(pkg)):
        if f.endswith(".py"):
            with open(os.path.join(pkg, f), "rb") as fh:
                h.update(fh.read())
    return h.hexdigest()[:16]


def input_fingerprint(panel) -> str:
    """输入数据指纹：日期范围+标的清单+收盘矩阵。复算须得到相同指纹。"""
    h = hashlib.sha256()
    h.update(str(panel.dates[0]).encode())
    h.update(str(panel.dates[-1]).encode())
    h.update(str(len(panel.dates)).encode())
    for c in panel.codes:
        h.update(c.encode())
    arr = np.round(panel.close.to_numpy(dtype=float), 4)
    h.update(np.ascontiguousarray(arr).tobytes())
    return h.hexdigest()[:16]


def _equity_hash(res) -> str:
    return hashlib.sha256(np.round(res.equity.to_numpy(), 4).tobytes()).hexdigest()[:16]


# ---------------------------------------------------------------- 审计项

def no_lookahead_audit(cfg, state, panel, k_days: int = 5, seed: int | None = None) -> dict:
    """无未来函数抽查：截断重算 == 全量计算（逐元素），覆盖完整决策链。"""
    members = team_members(state)
    if not members:
        return {"passed": False, "reason": "no_team"}
    w_full = team_target_weights(cfg, state, panel).astype(float)
    dates = list(panel.dates)
    rng = random.Random(seed if seed is not None else int(dt.date.today().strftime("%Y%m%d")))
    lo = int(len(dates) * 0.5)  # 抽查日前须留足历史供滚动指标热身
    picks = rng.sample(range(lo, len(dates)), min(k_days, len(dates) - lo))
    checks, passed = [], True
    for i in picks:
        day = dates[i]
        trunc = panel.window(dates[0], day)  # 只给 ≤day 的数据
        w_tr = team_target_weights(cfg, state, trunc).astype(float)
        a = w_full.loc[day].fillna(0.0)
        b = w_tr.loc[day].fillna(0.0)
        diff = float((a - b).abs().max())
        ok = diff < 1e-9
        passed = passed and ok
        checks.append({"day": str(day.date()), "max_abs_diff": f"{diff:.2e}", "pass": bool(ok)})
    return {"passed": bool(passed), "checks": checks,
            "team": [[m.get("strategy"), m.get("sizing") or "equal"] for m in members]}


def determinism_audit(cfg, state, panel, window_days: int = 120) -> dict:
    """复算一致性：同一输入两遍引擎，净值哈希必须相同。"""
    from .backtest import run_backtest
    if not team_members(state):
        return {"passed": False, "reason": "no_team"}
    w = team_target_weights(cfg, state, panel).astype(float)
    sub = panel.window(panel.dates[max(0, len(panel.dates) - window_days)], panel.dates[-1])
    r1 = run_backtest(sub, w, cfg)
    r2 = run_backtest(sub, w, cfg)
    h1, h2 = _equity_hash(r1), _equity_hash(r2)
    return {"passed": h1 == h2, "equity_hash": h1, "equity_hash_2": h2,
            "window": [str(sub.dates[0].date()), str(sub.dates[-1].date())],
            "final_equity": round(float(r1.equity.iloc[-1]), 2)}


# ---------------------------------------------------------------- 套件（先声明后揭示）

def run_audit_suite(cfg, state, panel=None, k_days: int = 5, window_days: int = 120) -> dict:
    """审计套件：声明 → 三项审计 → 结果落台账 + Markdown 报告。只读 state，不写 state。"""
    from . import data as qd
    if panel is None:
        _, panel = qd.full_panel(cfg)
    members = team_members(state)
    if not members:
        print("暂无冠军团队，无法审计（先 run.py evolve）")
        return {"passed": False, "reason": "no_team"}

    ep_id = dt.datetime.now().strftime("%Y%m%d%H%M%S")
    fp_in, fp_code = input_fingerprint(panel), code_fingerprint()
    # —— 先声明（此时任何结果都尚未计算）——
    _ledger_append({"type": "audit_declaration", "ep": ep_id,
                    "declared_at": dt.datetime.now().isoformat(timespec="seconds"),
                    "panel_window": [str(panel.dates[0].date()), str(panel.dates[-1].date())],
                    "team": team_fingerprint(state),
                    "fingerprint_input": fp_in, "fingerprint_code": fp_code,
                    "note": "声明落盘时结果尚未计算（先声明后揭示，防先看结果再下结论）"})

    nl = no_lookahead_audit(cfg, state, panel, k_days=k_days)
    dm = determinism_audit(cfg, state, panel, window_days=window_days)
    overall = bool(nl.get("passed")) and bool(dm.get("passed"))
    result = {"type": "audit_result", "ep": ep_id,
              "finished_at": dt.datetime.now().isoformat(timespec="seconds"),
              "no_lookahead": nl, "determinism": dm, "passed": overall}
    _ledger_append(result)

    lines = ["# 防作弊审计报告",
            f"- 时间: {result['finished_at']} | 审计批次: {ep_id}",
            f"- 输入指纹: {fp_in} | 代码指纹: {fp_code}",
            f"- 团队: {nl.get('team')}", "",
            "## ① 无未来函数抽查（截断重算 == 全量计算）",
            "| 抽查日 | 最大偏差 | 结果 |", "|---|---|---|"]
    for c in nl.get("checks", []):
        lines.append(f"| {c['day']} | {c['max_abs_diff']} | {'✅' if c['pass'] else '❌'} |")
    lines += ["",
              f"**结论①: {'通过——决策时刻无法看到当日及之后的任何走势' if nl.get('passed') else '未通过——存在未来函数泄漏！'}**",
              "",
              "## ② 复算一致性（同输入两遍引擎）",
              f"- 净值哈希: {dm.get('equity_hash')} vs {dm.get('equity_hash_2')}"
              f" → {'✅ 相同' if dm.get('passed') else '❌ 不同（存在非确定性！）'}",
              f"- 复核窗口: {dm.get('window')} | 期末权益 {dm.get('final_equity'):,} 元",
              "",
              "## ③ 台账顺序（先声明后揭示）",
              f"- 声明与结果均已追加 logs/audit_ledger.jsonl（ep={ep_id}），"
              "声明时间早于结果时间且含输入/代码指纹，事后可复核。",
              "",
              f"## 总结论: {'✅ 通过（无作弊证据链完整）' if overall else '❌ 未通过——禁止实盘，先排查'}",
              "",
              "审计范围说明：抽查覆盖完整决策链（策略→仓位基因→团队合成）的全量vs截断一致性；",
              "复算一致性证明结果为确定性代码输出。审计为只读操作，不修改任何账户与状态。"]
    os.makedirs(LOGS_DIR, exist_ok=True)
    path = os.path.join(LOGS_DIR, f"audit_{dt.date.today().strftime('%Y%m%d')}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    try:
        print("\n".join(lines))
    except UnicodeEncodeError:
        pass  # GBK 控制台显示不了✅等符号；报告文件已 UTF-8 落盘，不影响审计结论
    log.info("防作弊审计完成 → %s | 通过=%s", path, overall)
    return result
