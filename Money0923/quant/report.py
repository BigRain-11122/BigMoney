"""报告与状态输出：控制台总览、逐日结算报告、周度机制复盘（总结→反哺进化）。

复盘是闭环的：周度复盘用真实轨道做冠军衰退检测，衰退则置位
state.meta.champion_decay，进化引擎下轮自动注入50%移民重启搜索。
用户指定的风控红线（15%/2周/3%/10%）永不被复盘自动修改——只进化方法论，不进化底线。
"""
from __future__ import annotations

import datetime as dt
import logging
import os

from .config import LOGS_DIR, AppConfig


def _pct(x) -> str:
    try:
        return f"{float(x) * 100:+.2f}%"
    except Exception:  # noqa: BLE001
        return "-"


def alert(cfg: AppConfig, message: str) -> None:
    """风控事件告警：日志必出；配置 meta.alert_webhook 时额外 POST 推送。

    触发场景：停机/单日熔断/极端行情闸/实盘STOP。webhook 收 json={"text": message}。
    """
    logging.getLogger("quant.risk").warning("[告警] %s", message)
    url = ""
    try:
        url = str(getattr(cfg.meta, "alert_webhook", "") or "")
    except Exception:  # noqa: BLE001
        pass
    if url:
        try:
            import requests
            requests.post(url, json={"text": message}, timeout=5)
        except Exception as e:  # noqa: BLE001
            logging.getLogger("quant.risk").warning("webhook 告警发送失败: %s", e)


def metrics_line(m: dict) -> str:
    return (f"收益 {_pct(m.get('total_return'))} | 年化 {_pct(m.get('cagr'))} | "
            f"回撤 {_pct(m.get('max_dd'))} | 夏普 {m.get('sharpe', 0):.2f} | "
            f"Calmar {m.get('calmar', 0):.2f} | 胜率 {_pct(m.get('win_rate'))} | "
            f"笔数 {m.get('n_trades', 0)} | 暴露 {m.get('exposure', 0) * 100:.0f}%")


def print_status(cfg: AppConfig, state: dict) -> None:
    acc = state["account"]
    risk = state["risk"]
    print("=" * 62)
    print("Money 自进化交易系统 · 状态总览")
    print(f"时间: {dt.datetime.now():%Y-%m-%d %H:%M} | 模式: {cfg.mode} | "
          f"风控停机: {'是' if risk['halt'] else '否'}")
    print("-" * 62)
    from .futures import position_value
    mv = sum(position_value(c, p) for c, p in acc["positions"].items())
    print(f"账户: 现金 {acc['cash']:,.0f} | 持仓成本 {mv:,.0f} | 高水位 {acc['equity_high']:,.0f}")
    if acc["positions"]:
        print("持仓:")
        for c, p in acc["positions"].items():
            if str(c).startswith("F."):
                print(f"  {c}: {p.get('lots', 0)}手 均价 @{p.get('avg_entry', 0.0):.2f}"
                      f"（期货仓位，T+0 可平）")
            else:
                print(f"  {c}: {p.get('shares', 0)}股（可卖 {p.get('available', 0)}）"
                      f"成本 @{p.get('cost', 0.0):.2f}")
    else:
        print("持仓: 空仓")
    sleeves = state.get("sleeves") or []
    if sleeves:
        from . import sleeves as qsl
        print("分仓制（每仓独立10%停机线·队死换人资金保留）:")
        for sv in sleeves:
            r = sv.get("risk") or {}
            hist = sv.get("history") or []
            eq = hist[-1].get("equity") if hist else "—"
            print(f"  {qsl.sleeve_label(sv)}: 权益 {eq} | 现金 {sv.get('cash', 0):,.0f} | "
                  f"高水位 {r.get('equity_high', 0):,.0f} | 换人 {sv.get('rotations', 0)} 次")
    print("-" * 62)
    team = state.get("team") or []
    champ = state.get("champion")
    if team:
        print(f"冠军团队（资产组合，{len(team)} 成员资金均分）:")
        for i, m in enumerate(team, 1):
            h = m.get("holdout", {})
            sizing = m.get("sizing") or "equal"
            print(f"  [{i}] {m['strategy']} + 仓位[{sizing}] 样本外分 {h.get('score', 0):.4f} | "
                  f"{metrics_line(h.get('metrics', {}))}")
        if champ and champ.get("team_avg") is not None:
            print(f"  团队平均分 {champ['team_avg']:.4f} | 历届团队: {len(state.get('champion_retired', []))} 任")
    elif champ:
        print(f"冠军(单): {champ['strategy']} + 仓位[{champ.get('sizing') or 'equal'}]"
              f"（第{champ.get('gen')}代晋升于 {champ.get('promoted_at', '')}）")
        print(f"  参数: {champ['params']} | 仓位参数: {champ.get('sizing_params') or {}}")
        h = champ.get("holdout", {})
        print(f"  样本外分 {h.get('score', 0):.4f} | {metrics_line(h.get('metrics', {}))}")
        print(f"  退休冠军: {len(state.get('champion_retired', []))} 任")
    else:
        print("冠军团队: 尚无（进化出合格团队前保持空仓）")
    evo = state["evolution"]
    print(f"进化: 第 {evo['generation']} 代 | 上次运行 {evo.get('last_run')}")
    for rec in evo.get("history", [])[-5:]:
        b = rec.get("best", {})
        print(f"  第{rec['gen']}代 best={rec['best_score']:.4f} mean={rec['mean_score']:.4f} "
              f"[σ×{rec.get('sigma_boost', 1.0)}] [{b.get('strategy')}]")
    top10 = evo.get("top10") or []
    if top10:
        fams: dict[str, int] = {}
        for t in top10:
            fams[t["strategy"]] = fams.get(t["strategy"], 0) + 1
        print(f"本轮前10名选手: " + ", ".join(f"{k}×{v}" for k, v in
                                              sorted(fams.items(), key=lambda kv: -kv[1])))
        for i, t in enumerate(top10[:3], 1):
            print(f"  Top{i}: {t['strategy']} 分{t['score']:.4f} {t['params']}")
    snap = (state.get("regime") or {}).get("snapshot") or {}
    if snap:
        cr = snap.get("champion_recent") or {}
        bs = snap.get("best_family_now") or {}
        print("-" * 62)
        print(f"市场风格: {snap.get('trend')} | {snap.get('factor_style')} | "
              f"{snap.get('size_style') or '大小盘均衡'} | 波动分位 {snap.get('vol_pct')}")
        if cr or bs:
            print(f"  冠军近段 夏普 {cr.get('sharpe', '-')} | 当前最适族 {bs.get('family', '-')}"
                  f"（{bs.get('sharpe', '-')}） | 曝光 ×{snap.get('exposure_scale')}"
                  f"{' [警示]错配' if snap.get('mismatch') else ''}{' [警示]敌对' if snap.get('hostile') else ''}")
    print("-" * 62)
    if state.get("paper_track"):
        print("账户轨道（最近5日）:")
        for t in state["paper_track"][-5:]:
            print(f"  {t['date']} 权益 {t['equity']:,.0f}（现金 {t['cash']:,.0f} / "
                  f"市值 {t['market_value']:,.0f} / {t.get('n_positions', 0)}只"
                  f"{'/实盘' if t.get('mode') == 'live' else ''}）")
    if state.get("reviews"):
        print(f"复盘: 已累计 {len(state['reviews'])} 份（最近 {state['reviews'][-1].get('date','')}）")
    if risk["halt"]:
        print(f"!! 停机原因: {risk['halt_reason']}（复盘后 run.py resume）")
    if risk.get("daily_breaker_date"):
        print(f"日熔断: {risk['daily_breaker_date']}（当日停止新开仓，次日自动恢复）")
    print("=" * 62)


def daily_report(cfg: AppConfig, state: dict, title: str, extra_lines: list[str] | None = None) -> str:
    """逐日结算报告（追加式：同一天多段结算共存于一个文件）。"""
    os.makedirs(LOGS_DIR, exist_ok=True)
    acc = state["account"]
    risk = state["risk"]
    lines = [f"## {title}（{dt.datetime.now().strftime('%Y-%m-%d %H:%M')}）",
             f"- 模式: {cfg.mode}"]
    lines.append(f"- 现金: {acc['cash']:,.2f}")
    if acc["positions"]:
        lines += ["", "| 代码 | 股数/手数 | 可卖 | 成本/均价 | 仓 |", "|---|---|---|---|---|"]
        for c, p in acc["positions"].items():
            if str(c).startswith("F."):
                lines.append(f"| {c} | {p.get('lots', 0)}手 | T+0 双向 | "
                             f"均价 @{p.get('avg_entry', 0.0):.2f} | {p.get('sleeve', '—')} |")
            else:
                lines.append(f"| {c} | {p.get('shares', 0)} | {p.get('available', 0)} | "
                             f"{p.get('cost', 0.0):.2f} | {p.get('sleeve', '—')} |")
    else:
        lines.append("- 持仓: 空仓")
    sleeves = state.get("sleeves") or []
    if sleeves:
        from . import sleeves as qsl
        lines.append("- 分仓制（每仓独立10%停机线·队死换人资金保留）:")
        for sv in sleeves:
            hist = sv.get("history") or []
            last_h = hist[-1] if hist else {}
            lines.append(f"  - {qsl.sleeve_label(sv)}：权益 {last_h.get('equity', '—')} | "
                          f"现金 {sv.get('cash', 0):,.0f} | 持仓 {last_h.get('n_pos', '—')} | "
                          f"换人 {sv.get('rotations', 0)} 次")
    champ = state.get("champion")
    if champ:
        lines.append(f"- 现任冠军: {champ['strategy']} 样本外分 {champ.get('holdout', {}).get('score', '')}")
    # 市场风格快照（每晚风格引擎写入）
    snap = (state.get("regime") or {}).get("snapshot") or {}
    if snap:
        lines.append(f"- 市场风格: {snap.get('trend')} | {snap.get('factor_style')} | "
                     f"{snap.get('size_style') or '大小盘均衡'} | 波动分位 {snap.get('vol_pct')}")
        cr = snap.get("champion_recent") or {}
        bs = snap.get("best_family_now") or {}
        if cr:
            lines.append(f"- 冠军近段验证: 夏普 {cr.get('sharpe')} | 当前最适族: "
                         f"{bs.get('family')}（夏普 {bs.get('sharpe')}）")
        lines.append(f"- 曝光系数: ×{snap.get('exposure_scale')} | 错配={snap.get('mismatch')} "
                     f"| 敌对={snap.get('hostile')}")
    lines.append(f"- 风控: 停机={risk['halt']} 日熔断={risk.get('daily_breaker_date')}")
    if extra_lines:
        lines += [f"- {x}" for x in extra_lines]
    lines.append("")
    path = os.path.join(LOGS_DIR, f"report_{dt.date.today().strftime('%Y%m%d')}.md")
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


# -------------------------------------------------- 交易统计与周度复盘

def trade_summary(trade_log: list, since: str | None = None) -> dict:
    """成交统计（since=YYYYMMDD 起算）：按原因/方向计数与金额。"""
    tl = [t for t in trade_log if not since or str(t.get("date", "")) >= since]
    by_reason: dict[str, int] = {}
    buys = sells = 0
    amount = 0.0
    for t in tl:
        by_reason[t.get("reason", "?")] = by_reason.get(t.get("reason", "?"), 0) + 1
        if t.get("side") == "buy":
            buys += 1
        else:
            sells += 1
        try:
            amount += float(t.get("shares", 0)) * float(t.get("price", 0))
        except Exception:  # noqa: BLE001
            pass
    return {"n": len(tl), "buys": buys, "sells": sells, "amount": amount, "by_reason": by_reason}


def weekly_review(cfg: AppConfig, state: dict, force: bool = False) -> str | None:
    """周度机制复盘：轨道绩效 → 交易行为画像 → 冠军衰退检测 → 机制调整（写审计）。

    返回报告路径；未到复盘日或本周已复盘则返回 None。
    衰退判定：轨道≥meta.decay_min_days 且实际年化 < 冠军样本外年化×decay_ratio
             → 置位 champion_decay，进化引擎下轮注入移民重启搜索。
    """
    mc = cfg.meta
    today = dt.date.today()
    week_key = f"{today.isocalendar().year}-W{today.isocalendar().week:02d}"
    if not force and state.get("meta", {}).get("last_review_week") == week_key:
        return None
    state.setdefault("meta", {})["last_review_week"] = week_key

    track = state.get("paper_track", [])
    evo = state["evolution"]
    champ = state.get("champion")
    lines = [f"# 周度机制复盘 · {week_key}",
             f"- 生成: {dt.datetime.now():%Y-%m-%d %H:%M}",
             f"- 进化: 累计第 {evo['generation']} 代，冠军 {champ['strategy'] if champ else '无'}，"
             f"退休 {len(state.get('champion_retired', []))} 任", ""]

    # —— 轨道绩效（冠军定型后的真实推进记录）——
    ret = dd = None
    if len(track) >= 2:
        eq = [t["equity"] for t in track]
        days = len(track)
        ret = eq[-1] / eq[0] - 1.0
        peak, max_dd = eq[0], 0.0
        for v in eq:
            peak = max(peak, v)
            max_dd = min(max_dd, v / peak - 1.0)
        lines += ["## 账户轨道（冠军定型后）",
                  f"- {track[0]['date']} ~ {track[-1]['date']}（{days} 个交易日）",
                  f"- 区间收益 {_pct(ret)} | 区间最大回撤 {_pct(max_dd)}",
                  f"- 期末权益 {eq[-1]:,.0f} 元", ""]

        # —— 冠军衰退检测（绩效反哺机制）——
        if champ and days >= mc.decay_min_days:
            exp_cagr = float(champ.get("holdout", {}).get("metrics", {}).get("cagr", 0) or 0)
            real_cagr = (eq[-1] / eq[0]) ** (252.0 / days) - 1.0
            lines += ["## 冠军衰退检测",
                      f"- 冠军样本外年化 {_pct(exp_cagr)} | 实际年化 {_pct(real_cagr)}（{days} 日轨道）"]
            if exp_cagr > 0 and real_cagr < exp_cagr * mc.decay_ratio:
                state["meta"]["champion_decay"] = True
                lines.append(f"- [警示] **判定衰退**：实际年化低于预期的 {mc.decay_ratio:.0%} → "
                             "已置位 champion_decay，进化引擎下轮注入 50% 移民重启搜索")
            else:
                lines.append("- 结论：冠军表现与样本外预期相符（或数据尚短）")
            lines.append("")
    else:
        lines += ["## 账户轨道", "- 尚无足够轨道数据（首个交易周），下期复盘补充", ""]

    # —— Top10 洞察（看策略：本轮谁在赢、参数长什么样 → 指导下轮精修方向）——
    top10 = evo.get("top10") or []
    if top10:
        fams: dict[str, int] = {}
        for t in top10:
            fams[t["strategy"]] = fams.get(t["strategy"], 0) + 1
        dom = max(fams.items(), key=lambda kv: kv[1])
        lines += ["## Top10 洞察（每轮前10名选手画像）",
                  "- 家族分布: " + ", ".join(f"{k}×{v}" for k, v in
                                             sorted(fams.items(), key=lambda kv: -kv[1])),
                  f"- 主导家族: {dom[0]}（占 Top10 的 {dom[1]}/10）"]
        dom_params = [t["params"] for t in top10 if t["strategy"] == dom[0]]
        if dom_params:
            means = {}
            for k in dom_params[0]:
                vals = [p[k] for p in dom_params if isinstance(p.get(k), (int, float))]
                if vals:
                    means[k] = round(sum(vals) / len(vals), 2)
            if means:
                lines.append(f"- 主导家族参数均值: {means}（下一轮 Top10 邻域精修围绕此重心）")
        arena_iter = (state.get("arena") or {}).get("iter_round")
        if arena_iter:
            lines.append(f"- 锦标赛迭代届数: 第 {arena_iter} 届（每届后 Top10 保留+变异进入下届）")
        lines.append("")

    # —— 市场风格演变（风格引擎每日快照的趋势总结）——
    rh = (state.get("regime") or {}).get("history") or []
    if rh:
        recent = rh[-7:]
        lines += ["## 本周市场风格演变（风格引擎）"]
        for h in recent:
            cr = h.get("champion_recent") or {}
            bs = h.get("best_family_now") or {}
            lines.append(f"- {h.get('date')}: {h.get('trend')} / {h.get('factor_style')} | "
                         f"冠军近段夏普 {cr.get('sharpe', '-')} | 最适族 {bs.get('family', '-')}"
                         f"（{bs.get('sharpe', '-')}） | 曝光×{h.get('scale')}"
                         f"{' [警示]错配' if h.get('mismatch') else ''}")
        mismatches = sum(1 for h in recent if h.get("mismatch"))
        if mismatches >= 3:
            lines.append(f"- 结论：本周 {mismatches}/7 天风格错配 → 冠军族与当下市场不合，"
                         "关注进化换血与新冠军晋升")
        lines.append("")

    # —— 交易行为画像 ——
    ts = trade_summary(state.get("trade_log", []))
    if ts["n"]:
        reason_str = ", ".join(f"{k}×{v}" for k, v in sorted(ts["by_reason"].items()))
        lines += ["## 交易行为画像",
                  f"- 成交 {ts['n']} 笔（买 {ts['buys']} / 卖 {ts['sells']}），金额 {ts['amount']:,.0f} 元",
                  f"- 离场原因分布: {reason_str}"]
        time_exits = ts["by_reason"].get("time_exit", 0)
        stops = ts["by_reason"].get("stop", 0) + ts["by_reason"].get("stop_open", 0) + ts["by_reason"].get("stop_intraday", 0)
        if ts["sells"]:
            if time_exits / ts["sells"] > 0.4:
                lines.append("- 结论：超时离场占比 >40% → 信号周期偏长，进化正被 2 周上限强制截短，"
                             "预计下任冠军转向更短调仓周期（这本身即机制约束在起作用）")
            if stops / ts["sells"] > 0.2:
                lines.append("- 结论：止损离场占比 >20% → 近期市场波动大或入场点偏弱，关注冠军换血")
        lines.append("")

    # —— 进化健康度 ——
    hist = evo.get("history", [])
    if hist:
        week_gens = [h for h in hist if h["time"][:10] >= (today - dt.timedelta(days=7)).isoformat()]
        scores = [h["best_score"] for h in week_gens] or [hist[-1]["best_score"]]
        lines += ["## 进化健康度",
                  f"- 本周新增 {len(week_gens)} 代 | 最优适应度 {min(scores):.4f} → {max(scores):.4f}",
                  f"- 变异步长当前 ×{hist[-1].get('sigma_boost', 1.0)}（停滞时自动放大，突破后回落）", ""]

    # —— 数据真实性核对（防自我幻觉：披露数据质量与口径）——
    from .validation import load_last_report as _load_vq
    vq = _load_vq()
    if vq:
        ex = vq.get("excluded") or []
        ex_str = ", ".join(f"{e['code']}({e['reason']})" for e in ex[:6]) or "无"
        lines += ["## 数据真实性核对",
                  f"- 最近校验 {vq.get('time', '')} | 输入 {vq.get('n_input', 0)} 只 → 通过 {vq.get('n_clean', 0)} 只",
                  f"- 校验剔除: {ex_str}" + ("…" if len(ex) > 6 else ""),
                  f"- 异常K线留痕: {len(vq.get('anomaly_bars', []))} 处（OHLC矛盾/涨跌停外跳变，保留但可审计）",
                  "- 复权口径: 股票=新浪前复权（每周全量重拉防拼接假跳空）；ETF=新浪不复权整段一致（分红日存在小缺口）",
                  "- 股票池口径: 沪深300当月权重表+中证1000小端（时点近似，成分漂移留待历史成分数据改善）",
                  "- 一切绩效数字仅来自上述校验后数据，无任何合成/估计序列参与决策", ""]

    lines += ["## 红线声明",
              "- 用户指定风控（单票15%/最高持股2周/日亏3%熔断/回撤10%停机）为硬规则，永不被复盘自动修改",
              "- 复盘只调整方法论机制：移民注入、变异步长、冠军换血"]

    os.makedirs(LOGS_DIR, exist_ok=True)
    path = os.path.join(LOGS_DIR, f"review_{today.strftime('%Y%m%d')}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    state.setdefault("reviews", []).append({
        "week": week_key, "date": today.isoformat(),
        "track_ret": None if ret is None else round(ret, 4),
        "gens": evo["generation"],
        "champion": champ["strategy"] if champ else None,
        "champion_decay": bool(state.get("meta", {}).get("champion_decay")),
        "report": path,
    })
    state["reviews"] = state["reviews"][-mc.review_keep:]
    return path
