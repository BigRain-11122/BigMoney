"""周期交接文档生成器（用户指令 2026-09-22："每个周期都要形成文档，让我随时可以用AI
新开对话接上开发和回测"）。

每个周期（收盘结算/盘前会话/闭市进化轮）自动重写项目根 HANDOFF.md：
任何平台的新 AI 会话（不依赖本 CLI 的记忆系统）读完即可无损接上开发与回测。

文档自含八节：接手指南 / 用户红线 / 实况快照 / 本周期事件 / 周期史 / 开发状态
（含"磁盘代码 vs 运行中代码"差异检测）/ 命令速查 / 多会话铁律。
事实以 state.json 与 logs 为准——本文档只是地图与快照，生成时间戳见文首。

开发叙事（进行中工作/待办/下一步）由 DEV_NOTES.md 承载（AI/人可随时编辑），
每周期被原样嵌入 §6——自动事实与人工叙事分离，互不踩踏。
"""
from __future__ import annotations

import datetime as dt
import glob
import hashlib
import logging
import os

from .config import LOGS_DIR, ROOT, AppConfig

log = logging.getLogger("quant.handoff")

HANDOFF_FILE = os.path.join(ROOT, "HANDOFF.md")
DEV_NOTES_FILE = os.path.join(ROOT, "DEV_NOTES.md")
AUDIT_DOC = os.path.join(ROOT, "SYSTEM_AUDIT.md")


# ---------------------------------------------------------------- 代码版本检测
def _code_files() -> list[str]:
    files = sorted(glob.glob(os.path.join(ROOT, "quant", "*.py")))
    run_py = os.path.join(ROOT, "run.py")
    if os.path.exists(run_py):
        files.append(run_py)
    return files


def code_fingerprint() -> dict[str, str]:
    """relpath -> md5。auto 守护启动时快照进 state.auto['code_files']，
    HANDOFF 每周期对比磁盘现值 → 新会话立刻知道"有没有磁盘代码待重启载入"。"""
    out: dict[str, str] = {}
    for f in _code_files():
        try:
            with open(f, "rb") as fh:
                out[os.path.relpath(f, ROOT)] = hashlib.md5(fh.read()).hexdigest()
        except OSError:
            continue
    return out


def _code_drift(state: dict) -> list[str] | None:
    """磁盘 vs 守护启动快照差异；守护旧版本无快照时返回 None=未知（勿误报已同步）。"""
    snap = (state.get("auto") or {}).get("code_files") or {}
    if not snap:
        return None
    drift = []
    cur = code_fingerprint()
    for rel, h in sorted(snap.items()):
        if cur.get(rel) != h:
            drift.append(rel)
    for rel in sorted(set(cur) - set(snap)):
        drift.append(rel + "（新增）")
    return drift


# ---------------------------------------------------------------- 静态段落
_RULES_FALLBACK = ("（解析失败——以 SYSTEM_AUDIT.md §1 原文为准）")


def _rules_text() -> str:
    """用户红线=唯一事实源 SYSTEM_AUDIT.md §1，逐字嵌入（避免两处漂移）；
    标题降一级（##→###）避免与本文档章节号冲突。"""
    try:
        with open(AUDIT_DOC, encoding="utf-8") as f:
            lines = f.read().splitlines()
        start = next(i for i, l in enumerate(lines) if l.startswith("## 1."))
        end = next(i for i, l in enumerate(lines[start + 1:], start + 1)
                   if l.startswith("## "))
        seg = lines[start:end]
        if seg and seg[0].startswith("## "):
            seg[0] = "### " + seg[0][3:]   # 去掉重复的"## 1."编号行，改为降级子标题
        for i, l in enumerate(seg[1:], 1):
            if l.startswith("## "):
                seg[i] = "#### " + l[3:]
            elif l.startswith("# "):
                seg[i] = "#### " + l[2:]
        return "\n".join(seg).strip()
    except Exception:  # noqa: BLE001
        return _RULES_FALLBACK


def _dev_notes() -> str:
    try:
        with open(DEV_NOTES_FILE, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return "（DEV_NOTES.md 尚未创建——请在本文件记录进行中工作/待办/下一步）"


_COMMANDS = """```bash
# —— 系统状态与实战成绩 ——
python run.py status              # 冠军/团队/联赛/配额/风控一览
python run.py stats               # 全量统计（控制台+logs/dashboard_*.html）
python tools/_live_score.py       # 盘中实时浮盈/三仓/联赛计数（只读）
python run.py sleeves             # 分仓面板（成员/权益/停机线/换人史）
python run.py top10               # 多维实战Top10（盈利最多/概率最高/最稳定）
python run.py verdict             # 「什么策略适合我」大样本裁决报告
python run.py race                # 百名交易员实赛榜（盘中实时）

# —— 回测与验证（接上回测从这里开始）——
python run.py paper --replay      # 冠军策略历史回放（只读，不写state）
python run.py stress              # 随机取点体检（24随机窗全规则撮合）
python run.py audit               # 防作弊抽查（无未来函数/复算一致性/台账）
python run.py walk-forward        # 链式walk-forward样本外验证
python run.py evolve --rounds N    # 手动GA进化N代（先建watchdog_pause！）
python run.py league              # 手动联赛（先建watchdog_pause！）

# —— 测试与质量 ——
python -m pytest tests/ -q        # 全量回归（先建watchdog_pause并停守护再跑）

# —— 可视化 ——
dashboard.html                   # Web仪表盘（30秒自动刷新）
logs/arena_board.html            # 200人竞技场看板（30秒自动刷新）
MoneyViz/                        # 团结引擎像素竞技场（tuanjie open 后按Play）
```"""


_IRON_RULES = """1. **编辑前必 read_file**（多会话并发编辑，replace 工具有陈旧检测）
2. **杀守护前必查进程命令行**（`Get-CimInstance Win32_Process -Filter "Name='python.exe'"` 过滤 `*run.py*auto*`；豆包沙箱自带大量 python.exe，勿按数量判断）
3. **盘中会话运行时绝不重启守护**（09:25-15:06）；重启一律走看门狗单点：树杀后 `schtasks /run MoneyAutoGuardian`
4. **手动跑 tests/league/evolve 前先建 `state\\watchdog_pause`，跑完删除**（防看门狗把手动进程当守护、防资源竞争）
5. **改 state/写 state 前必查进程**（守护每轮写盘，防互踩）
6. **盘中大量抓新浪数据会殃及交易会话**——采集任务放盘后
7. 一票一仓；分仓现金双记账不变式：Σ仓内现金 == 总账现金
8. 治理总纲（2026-09-21）：一切基于科学——机制上线前自问"是不是用选择结果证明选择"；同源数据只作参考，结论必须走独立证据链"""


# ---------------------------------------------------------------- 极简上下文（token最省入口）
def context_blob(cfg: AppConfig, state: dict) -> str:
    """新AI会话最省token的入口（目标~300 tokens）：几行实况+关键状态。
    需要深度再读 HANDOFF.md；输出避免非GBK字符（控制台打印安全，勿用¥/★）。"""
    acc = state.get("account") or {}
    track = state.get("paper_track") or []
    eq = float(track[-1]["equity"]) if track else float(acc.get("cash", 0.0))
    ar = state.get("arena") or {}
    ch = state.get("champion") or {}
    sleeves = state.get("sleeves") or []
    today_iso = dt.date.today().isoformat()
    today_key = dt.date.today().strftime("%Y%m%d")
    n_trades = sum(1 for t in state.get("trade_log") or []
                   if str(t.get("date", "")) in (today_iso, today_key))
    drift = _code_drift(state)
    lines = [
        f"[MONEY快照 {dt.datetime.now():%Y-%m-%d %H:%M}] mode={cfg.mode}",
        f"权益 {eq:,.0f} / 本金 {cfg.risk.initial_capital:,.0f}"
        f" ({eq / cfg.risk.initial_capital - 1:+.2%}) | 持仓 {len(acc.get('positions') or {})}"
        f" | 今日成交 {n_trades} 笔 | 逆回购在途 "
        f"{sum(float(r.get('amount', 0)) for r in state.get('repo_open') or []):,.0f}",
        (f"冠军 {ch.get('strategy') or '空位'} "
         f"{float((ch.get('holdout') or {}).get('score', 0)):.3f}") if ch else "冠军 空位",
        f"联赛 {ar.get('round', 0):,} 局 | 认证池 {len(ar.get('qualified') or [])}"
        f" | 纪元 s{ar.get('data_epoch_stock', '?')}/f{ar.get('data_epoch_futures', '?')}",
    ]
    for sv in sleeves:
        hl = sv.get("halt_line")
        lines.append(
            f"{sv['id']} {sv.get('label', '')} "
            f"[{'/'.join(m.get('strategy', '?') for m in sv.get('members') or [])}]"
            f" 停机{'无' if hl is None else f'-{int(float(hl) * 100)}%'}"
            f"{' [已停机]' if (sv.get('risk') or {}).get('halt') else ''}"
            f"{' [退役]' if sv.get('retired') else ''}")
    lines.append((f"代码 待载入{len(drift)}文件" if drift else
                  ("代码 未知（守护旧版未记录快照，重启后生效）" if drift is None else "代码 已同步"))
                 + f" | 会话日 {(state.get('auto') or {}).get('session_date', '?')}")
    lines.append("深度接手读 HANDOFF.md；审查读 SYSTEM_AUDIT.md；开发叙事 DEV_NOTES.md")
    return "\n".join(lines)


# ---------------------------------------------------------------- 主生成器
def write_handoff(cfg: AppConfig, state: dict, reason: str = "周期刷新") -> str:
    ts = dt.datetime.now()
    acc = state.get("account") or {}
    ar = state.get("arena") or {}
    ch = state.get("champion") or {}
    sleeves = state.get("sleeves") or []
    repo_open = sum(float(r.get("amount", 0.0)) for r in state.get("repo_open") or [])
    repo_earned = 0.0
    try:
        repo_earned = sum(float(r.get("interest", 0.0)) - float(r.get("fee", 0.0))
                          for r in state.get("repo_log") or [])
    except Exception:  # noqa: BLE001
        pass

    # —— 实况快照 ——
    track = state.get("paper_track") or []
    last_eq = float(track[-1]["equity"]) if track else float(acc.get("cash", 0.0))
    game = ar.get("game") or {}
    reg = (state.get("regime") or {}).get("snapshot") or {}
    drift = _code_drift(state)
    auto = state.get("auto") or {}

    snap_lines = [
        f"- **账户**：收盘权益 ¥{last_eq:,.0f}（本金 ¥{cfg.risk.initial_capital:,.0f}，"
        f"累计 {last_eq / cfg.risk.initial_capital - 1:+.2%}）｜现金 ¥{float(acc.get('cash', 0)):,.0f}"
        f"｜持仓 {len(acc.get('positions') or {})} 只｜逆回购在途 ¥{repo_open:,.0f}（累计落袋利息 ¥{repo_earned:.2f}）",
        f"- **冠军**：{ch.get('strategy') or '空位'}"
        + (f"（样本外分 {ch.get('holdout', {}).get('score', 0):.4f}，"
           f"上任 {ch.get('promoted_at', '?')}）" if ch else ""),
        f"- **联赛**：累计 {ar.get('round', 0):,} 局｜阵容 {len(ar.get('players') or [])} 人｜"
        f"认证池 {len(ar.get('qualified') or [])}★｜玩法自校准：认证门槛 "
        f"{game.get('qualify_floor', 0):.2f} / 近窗偏置 {game.get('recent_bias', 0):.2f}",
        f"- **风格引擎**：{reg.get('trend', '?')}｜{reg.get('factor_style', '')}｜"
        f"曝光 ×{reg.get('exposure_scale', 1):.2f}｜当前最适族 "
        f"{(reg.get('best_family_now') or {}).get('family', '?')}",
        f"- **数据纪元**：stock s{ar.get('data_epoch_stock', '?')} / futures f{ar.get('data_epoch_futures', '?')}"
        f"（纪元变更=缓存与污染证据清除）",
    ]
    if sleeves:
        for sv in sleeves:
            r = sv.get("risk") or {}
            members_txt = "+".join(m.get("strategy", "?") for m in sv.get("members") or [])
            hl = sv.get("halt_line")
            hl_txt = "无（仅毁灭线）" if hl is None else f"-{int(float(hl) * 100)}%"
            flags = ""
            if r.get("halt"):
                flags += "｜⚠️已停机待换人"
            if sv.get("retired"):
                flags += "｜💀已退役"
            snap_lines.append(
                f"- **分仓 {sv['id']} {sv.get('label', '')}** [{members_txt}]"
                f" 起点 ¥{float(sv.get('capital_start', 0)):,.0f}"
                f"｜停机线 {hl_txt}｜换人 {sv.get('rotations', 0)} 次{flags}")

    # —— 本周期事件（今日） ——
    today_iso = ts.date().isoformat()
    today_key = ts.strftime("%Y%m%d")
    today_trades = [t for t in state.get("trade_log") or []
                    if str(t.get("date", "")) in (today_iso, today_key)]
    ev_lines: list[str] = []
    if today_trades:
        ev_lines.append(f"- 今日成交 {len(today_trades)} 笔：" + "；".join(
            f"[{t.get('sleeve', '账')}] {t.get('code')} {t.get('side')} {t.get('shares')}@{t.get('price')}"
            for t in today_trades[-8:]))
    stress = state.get("stress_history") or []
    if stress:
        s = stress[-1]
        ok = (float(s.get("mean", 0)) >= 0.25 and float(s.get("beat_cash_pct", 0)) >= 0.5)
        ev_lines.append(f"- 团队体检（{s.get('date', '?')}）：24随机窗均分 {float(s.get('mean', 0)):.3f}"
                        f"｜跑赢持币 {float(s.get('beat_cash_pct', 0)):.0%}"
                        f"｜跑赢基准 {float(s.get('beat_bench_pct', 0)):.0%}"
                        f"｜最差窗 {float(s.get('worst', 0)):+.2%}"
                        f"——{'✅ 通过' if ok else '❌ 未过（移民重启中）'}")
    r_events = [e for e in state.get("risk_events") or [] if e.get("date") == today_iso]
    if r_events:
        ev_lines.extend(f"- 风控事件：{e.get('type')}——{e.get('detail', '')[:80]}"
                        for e in r_events[-3:])
    if not ev_lines:
        ev_lines.append("- （今日无事件——联赛/进化在闭市段持续进行，见 logs/auto.log）")

    # —— 周期史（近10收盘） ——
    hist_lines = ["| 日期 | 收盘权益 | 当日盈亏 | 持仓 |", "|---|---|---|---|"]
    rows = track[-10:]
    for i, t in enumerate(rows):
        prev = float(rows[i - 1]["equity"]) if i > 0 else None
        pnl = f"{float(t['equity']) - prev:+,.0f}" if prev is not None else "—"
        hist_lines.append(f"| {t['date']} | ¥{float(t['equity']):,.0f} | {pnl} | {t.get('n_positions', '?')} |")
    if not rows:
        hist_lines.append("| （轨道累积中） | | | |")

    # —— 代码版本段 ——
    if drift is None:
        code_line = ("⚠️ 代码版本未知：运行中守护是旧版本（未记录启动快照）——"
                     "待下一次看门狗重启后，drift 检测才生效")
    elif drift:
        code_line = (f"**⚠️ 磁盘有未载入改动（守护 {auto.get('code_loaded_at', '?')} 启动后变更）**："
                     + "、".join(drift[:12])
                     + "——按铁律在**收盘后**走看门狗单点重启载入；盘中绝不重启")
    else:
        code_line = f"✅ 运行中代码 = 磁盘最新（守护载入于 {auto.get('code_loaded_at', '?')}）"

    text = f"""# HANDOFF · 周期交接文档（{reason} · 生成于 {ts:%Y-%m-%d %H:%M:%S}）

> **目的**：任何平台的新 AI 会话读完本文档即可无损接上开发与回测。
> 事实以 `state/state.json` 与 `logs/` 落盘为准，本文档只是地图与快照。

## 0. 新会话接手指南（Token 经济版，2026-09-22 用户指令"顶层设计加入节省token机制"）
**最省路径**：先跑 `python run.py ctx`（~300 token 实况）→ 按任务选读下表，**勿上来全读**。

| 任务 | 读什么 | 成本 |
|---|---|---|
| 看成绩/实况 | `python run.py ctx` 或 `python tools/_live_score.py` | ~0.3K tok |
| 接手开发 | 本文档（§6 含 DEV_NOTES 全文）+ 待改的单个代码文件 | ~5K tok |
| 审查系统 | `SYSTEM_AUDIT.md` 全文（14节） | ~11K tok |
| 跑回测验证 | §7 命令直接跑（输出即所得） | ~1K tok |
| 历史考古 | `.codely-cli/memory/archive_*.md` / `logs/*.md` | 按需 |

**⚠️ 禁止全量读（token 灾难级）**：`state/state.json`（~350K tok）· `logs/auto.log`（~11M tok，只能 grep 关键词+行号切片）· `quant/*.py` 全部加起来 246K tok（只读你要改的那个文件）。**取数一律用 §7 命令或 python 片段按键取，绝不 read_file 大文件**。

1. 验证系统活着：`python run.py status` + 查守护进程（命令行含 `run.py auto`）
2. **§2 用户红线绝不可违反**；新机制上线前先读 §8 铁律与治理总纲
3. 接上回测：§7 命令速查从 `paper --replay`/`stress`/`audit` 开始

## 1. 系统是什么（30秒）
自进化 A股+ETF（+期货CTA闸控）量化系统：35 策略族 × GA进化 + 200人联赛认证选拔 →
冠军/认证者进入 3 分仓（稳健/进取/激进，各仓独立停机线）→ 模拟盘全规则实战（T+1/涨跌停/
费用/滑点/负面清单/国债逆回购现金管理）→ 战绩反哺进化。目标=大量真实实战样本裁决"什么策略适合你"。
本金 10 万，日频（收盘决策→次日开盘执行），持股 3~15 日。当前 mode=paper（真金实盘无限期搁置）。

## 2. 用户红线（摘自 SYSTEM_AUDIT.md §1，违反=事故）
{_rules_text()}

## 3. 实况快照（自动）
{chr(10).join(snap_lines)}

## 4. 本周期事件（{today_iso}）
{chr(10).join(ev_lines)}

## 5. 周期史（近10个收盘结算）
{chr(10).join(hist_lines)}

## 6. 开发状态（AI接手必读）
- **代码版本**：{code_line}
- **测试基线**：`python -m pytest tests/ -q`（改代码后先建 `state\\watchdog_pause` 再跑）

**DEV_NOTES.md 全文**（进行中工作/待办/下一步——AI/人可编辑，每周期自动嵌入）：

---
{_dev_notes()}
---

## 7. 命令速查（接上开发与回测）
{_COMMANDS}

## 8. 多会话协作铁律（安全）
{_IRON_RULES}

---
*本文档由 quant/handoff.py 每周期自动重写（收盘结算/闭市进化轮/CLI）。文档会错，代码与日志不会——冲突时以 state.json 与 logs 为准。*
"""
    try:
        with open(HANDOFF_FILE, "w", encoding="utf-8") as f:
            f.write(text)
    except OSError:
        log.warning("HANDOFF.md 写入失败")
    return text
