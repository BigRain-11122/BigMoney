"""统计中心：好的坏的全量统计，全部可见。

数据源（含并行扩展的全部机制）：
- trade_log（模拟盘已实现成交，含逐笔盈亏/持有天数/离场原因）
- paper_track（账户逐日轨道）     - team/champion/champion_retired（冠军团队与更迭史）
- stress_history（每日随机取点体检，含未过记录）  - regime（市场风格快照与历史）
- arena（百人擂台：选手前瞻轨道与战绩）          - risk_events（熔断/停机审计）
- meta 计数器（晋升/停滞/移民——挣扎过程也可见）

输出：控制台文本（run.py stats）+ 可视化HTML面板（logs/dashboard_*.html，
内联SVG无外部依赖，浏览器直接打开）。
"""
from __future__ import annotations

import datetime as dt
import os

from .config import LOGS_DIR, AppConfig


def _pct(x) -> str:
    try:
        return f"{float(x) * 100:+.2f}%"
    except Exception:  # noqa: BLE001
        return "-"


def _yuan(x) -> str:
    try:
        return f"{float(x):+,.0f}"
    except Exception:  # noqa: BLE001
        return "-"


def _names() -> dict[str, str]:
    try:
        import pandas as pd
        uni = pd.read_csv(os.path.join(os.path.dirname(LOGS_DIR), "data", "universe.csv"),
                          dtype={"code": str})
        return dict(zip(uni["code"].astype(str), uni["name"].astype(str)))
    except Exception:  # noqa: BLE001
        return {}


def _team_members(state: dict) -> list:
    team = state.get("team") or []
    if not team and state.get("champion"):
        team = [state["champion"]]
    return team


# ---------------------------------------------------------------- 交易统计

def trade_stats(trade_log: list) -> dict:
    sells = [t for t in trade_log if t.get("side") == "sell" and "pnl" in t]
    buys = [t for t in trade_log if t.get("side") == "buy"]
    out = {
        "n_total": len(trade_log), "n_buys": len(buys), "n_sells": len(sells),
        "realized": sum(t["pnl"] for t in sells),
        "wins": sum(1 for t in sells if t["pnl"] > 0),
        "losses": sum(1 for t in sells if t["pnl"] <= 0),
        "gross_win": sum(t["pnl"] for t in sells if t["pnl"] > 0),
        "gross_loss": sum(t["pnl"] for t in sells if t["pnl"] < 0),
        "max_win": max([t["pnl"] for t in sells], default=0.0),
        "max_loss": min([t["pnl"] for t in sells], default=0.0),
        "avg_hold": (sum(t.get("held_days") or 0 for t in sells) / len(sells)) if sells else None,
        "by_reason": {}, "by_code": {}, "by_date": {},
    }
    out["win_rate"] = out["wins"] / len(sells) if sells else None
    out["profit_factor"] = (out["gross_win"] / abs(out["gross_loss"])) \
        if out["gross_loss"] < 0 else None
    out["avg_win"] = out["gross_win"] / out["wins"] if out["wins"] else None
    out["avg_loss"] = out["gross_loss"] / out["losses"] if out["losses"] else None
    for t in sells:
        r = out["by_reason"].setdefault(t.get("reason", "?"), {"n": 0, "wins": 0, "pnl": 0.0})
        r["n"] += 1
        r["wins"] += 1 if t["pnl"] > 0 else 0
        r["pnl"] += t["pnl"]
        c = out["by_code"].setdefault(t["code"], {"n": 0, "wins": 0, "pnl": 0.0})
        c["n"] += 1
        c["wins"] += 1 if t["pnl"] > 0 else 0
        c["pnl"] += t["pnl"]
        out["by_date"][t["date"]] = out["by_date"].get(t["date"], 0.0) + t["pnl"]
    return out


def track_stats(paper_track: list) -> dict:
    if len(paper_track) < 1:
        return {"days": 0}
    eq = [t["equity"] for t in paper_track]
    peak, max_dd = eq[0], 0.0
    for v in eq:
        peak = max(peak, v)
        max_dd = min(max_dd, v / peak - 1.0)
    return {"days": len(eq), "start": eq[0], "end": eq[-1],
            "ret": eq[-1] / eq[0] - 1.0 if eq[0] else 0.0, "max_dd": max_dd,
            "first_date": paper_track[0]["date"], "last_date": paper_track[-1]["date"]}


def arena_stats(arena: dict | None) -> dict:
    """擂台前瞻轨道：谁在赚谁在亏（真实推进数据，模拟实盘性质）。"""
    players = (arena or {}).get("players") or []
    live = [p for p in players if p.get("equity") is not None]
    out = {"n": len(players), "forward_start": (arena or {}).get("forward_start")}
    if live:
        for p in live:
            p["_ret"] = p["equity"] / p.get("capital", 100000.0) - 1.0
        live.sort(key=lambda p: p["_ret"], reverse=True)
        out["top"] = live[:5]
        out["bottom"] = live[-5:]
        out["median_ret"] = live[len(live) // 2]["_ret"]
        out["positive"] = sum(1 for p in live if p["_ret"] > 0)
    return out


# ---------------------------------------------------------------- 控制台文本

def render_text(cfg: AppConfig, state: dict) -> str:
    names = _names()
    ts = trade_stats(state.get("trade_log", []))
    tk = track_stats(state.get("paper_track", []))
    evo = state["evolution"]
    meta = state.get("meta", {})
    regime = state.get("regime", {})
    snap = regime.get("snapshot") or {}
    members = _team_members(state)
    L: list[str] = []
    bar = "=" * 66
    L.append(bar)
    L.append("Money 统计中心 · 好坏全量可见 " + dt.datetime.now().strftime("%Y-%m-%d %H:%M"))
    L.append(bar)
    # —— 账户轨道 ——
    if tk.get("days", 0) >= 1:
        L.append(f"[账户轨道] {tk['first_date']} ~ {tk['last_date']}（{tk['days']}个交易日）")
        L.append(f"  权益 {tk['start']:,.0f} → {tk['end']:,.0f} 元 | 区间收益 {_pct(tk['ret'])} | 区间最大回撤 {_pct(tk['max_dd'])}")
    else:
        L.append(f"[账户轨道] 暂无推进数据（本金 {cfg.risk.initial_capital:,.0f} 元待命，首个交易日起逐日累积）")
    # —— 已实现交易 ——
    L.append(f"[已实现交易] 总{ts['n_total']}笔（买{ts['n_buys']}/卖{ts['n_sells']}）| 累计已实现盈亏 {_yuan(ts['realized'])} 元")
    if ts["n_sells"]:
        wr = f"{ts['win_rate']*100:.1f}%" if ts["win_rate"] is not None else "-"
        pf = f"{ts['profit_factor']:.2f}" if ts["profit_factor"] else "∞"
        aw = f"{ts['avg_win']:,.0f}" if ts["avg_win"] is not None else "-"
        al = f"{ts['avg_loss']:,.0f}" if ts["avg_loss"] is not None else "-"
        L.append(f"  胜{ts['wins']}笔 / 负{ts['losses']}笔（胜率{wr}）| 盈亏比{pf} | 平均盈利{aw}元 / 平均亏损{al}元")
        L.append(f"  最大单笔盈利 {_yuan(ts['max_win'])} | 最大单笔亏损 {_yuan(ts['max_loss'])}"
                 + (f" | 平均持有 {ts['avg_hold']:.1f} 个交易日" if ts["avg_hold"] is not None else ""))
        L.append("  [离场原因归因]（好的坏的分开看）")
        for r, v in sorted(ts["by_reason"].items(), key=lambda kv: kv[1]["pnl"]):
            L.append(f"    {r:12s} {v['n']:3d}笔 | 胜率{v['wins']/v['n']*100:5.1f}% | 累计 {_yuan(v['pnl'])} 元")
        L.append("  [标的归因·盈亏Top/Bottom]")
        codes = sorted(ts["by_code"].items(), key=lambda kv: kv[1]["pnl"], reverse=True)
        for c, v in (codes[:5] + [None] + codes[-5:] if len(codes) > 5 else codes):
            if c is None:
                L.append("    ……")
                continue
            L.append(f"    {c} {names.get(c, '')[:6]:6s} {v['n']:3d}笔 | 胜{v['wins']}/{v['n']} | 累计 {_yuan(v['pnl'])} 元")
        L.append("  [每日已实现盈亏·最近5日]")
        for d, v in sorted(ts["by_date"].items())[-5:]:
            L.append(f"    {d}: {_yuan(v)} 元")
    # —— 冠军团队 ——
    L.append(f"[冠军团队]（{'团队' if state.get('team') else '单人'}口径，资金均分）")
    if members:
        for m in members:
            h = m.get("holdout", {})
            stress = m.get("stress") or {}
            L.append(f"  {m['strategy']}: 样本外分{h.get('score','-')}"
                     + (f" | 体检均分{stress.get('mean','-')}/跑赢持币{stress.get('beat_cash_pct','-')}" if stress else ""))
        champ = state.get("champion") or {}
        if champ.get("team_avg"):
            L.append(f"  团队平均样本外分 {champ['team_avg']} | 组队于 {champ.get('promoted_at','')[:16]}")
    else:
        L.append("  无（合格团队出现前保持空仓——宁缺毋滥）")
    retired = state.get("champion_retired", [])
    if retired:
        L.append(f"  [更迭史·被顶替者也留名] 共{len(retired)}任")
        for r in retired[-5:]:
            if "members" in r:  # 团队时代格式
                L.append(f"    {r.get('retired_at','')[:16]} 退役团队 {r.get('members')} 均分{r.get('team_avg')}")
            else:  # 早期单冠军格式
                L.append(f"    {r.get('retired_at','')[:16]} 退役 {r.get('strategy')} "
                         f"分{r.get('holdout',{}).get('score','-')}")
    # —— 市场风格 ——
    if snap:
        cr = snap.get("champion_recent") or {}
        bf = snap.get("best_family_now") or {}
        L.append(f"[市场风格] {snap.get('trend')} / {snap.get('factor_style')} / {snap.get('size_style')} "
                 f"| 波动分位 {snap.get('vol_pct')}")
        L.append(f"  冠军近段夏普 {cr.get('sharpe','-')} | 当前最适族 {bf.get('family','-')}（夏普{bf.get('sharpe','-')}）"
                 f" | 曝光 ×{regime.get('exposure_scale', 1.0)}" + (" ⚠错配" if snap.get("mismatch") else ""))
    # —— 随机取点体检 ——
    stress = state.get("stress_history") or []
    if stress:
        L.append(f"[随机取点体检·最近8次]（不过=坏消息，照登）")
        for s in stress[-8:]:
            verdict = "✅" if (s["mean"] >= cfg.meta.stress_min_mean
                               and s["beat_cash_pct"] >= cfg.meta.stress_min_beat_pct) else "❌"
            L.append(f"    {s.get('date','')} {verdict} 均分{s['mean']:.3f} | 跑赢持币{s['beat_cash_pct']*100:.0f}% "
                    f"| 跑赢基准{s['beat_bench_pct']*100:.0f}% | 最差{s['worst']:.3f}")
    # —— 百人擂台 ——
    ar = arena_stats(state.get("arena"))
    if ar.get("n"):
        L.append(f"[百人擂台·前瞻轨道] {ar['n']}名选手" +
                 (f" | 前瞻起点 {ar.get('forward_start')}" if ar.get("forward_start") else ""))
        if ar.get("top") is not None:
            L.append(f"  中位收益 {_pct(ar.get('median_ret',0))} | 正收益 {ar['positive']}/{ar['n']}")
            for p in ar["top"][:3]:
                L.append(f"    最赚 {p['id']} {p['strategy']:14s} {_pct(p['_ret'])}")
            for p in ar["bottom"][-3:]:
                L.append(f"    最亏 {p['id']} {p['strategy']:14s} {_pct(p['_ret'])}")
    # —— 风控事件 ——
    ev = state.get("risk_events", [])
    if ev:
        L.append(f"[风控事件·审计] 共{len(ev)}条")
        for e in ev[-8:]:
            L.append(f"  {e.get('date','')} {e.get('type','')}: {e.get('detail','')}")
    else:
        L.append("[风控事件·审计] 无（未触发过熔断/停机）")
    # —— 进化事件 ——
    L.append(f"[进化事件] 累计{evo['generation']}代 | 晋升{meta.get('promotions_total',0)}次 "
             f"| 停滞{meta.get('stagnations_total',0)}次 | 移民注入{meta.get('immigrants_total',0)}个")
    L.append(bar)
    return "\n".join(L)


# ---------------------------------------------------------------- HTML 可视化

def _svg_line(vals: list[float], w: int = 900, h: int = 260, color: str = "#2c7be5") -> str:
    if len(vals) < 2:
        return '<p style="color:#888">暂无足够数据绘图（首个交易日起累积）</p>'
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    pad, iw, ih = 30.0, w - 2 * pad, h - 2 * pad
    step = iw / (len(vals) - 1)
    pts = [f"{pad + i * step:.1f},{pad + ih * (1 - (v - lo) / span):.1f}"
           for i, v in enumerate(vals)]
    grid = ""
    for gy in (0, 0.25, 0.5, 0.75, 1.0):
        y = pad + ih * gy
        v = hi - span * gy
        grid += (f'<line x1="{pad}" y1="{y:.0f}" x2="{w-pad}" y2="{y:.0f}" stroke="#eee"/>'
                 f'<text x="{pad-4}" y="{y+4:.0f}" text-anchor="end" font-size="10" fill="#888">{v:,.0f}</text>')
    return (f'<svg viewBox="0 0 {w} {h}" style="width:100%;background:#fff">{grid}'
            f'<polyline fill="none" stroke="{color}" stroke-width="2.2" points="{" ".join(pts)}"/></svg>')


def _svg_bars(items: list[tuple[str, float]], w: int = 900, h: int = 200) -> str:
    if not items:
        return '<p style="color:#888">暂无平仓记录（首个交易日起累积）</p>'
    lo = min(v for _, v in items + [("", 0.0)])
    hi = max(v for _, v in items + [("", 0.0)])
    span = (hi - lo) or 1.0
    pad, iw, ih = 30.0, w - 2 * pad, h - 2 * pad
    zero_y = pad + ih * (1 - (0 - lo) / span)
    bars = f'<line x1="{pad}" y1="{zero_y:.1f}" x2="{w-pad}" y2="{zero_y:.1f}" stroke="#999"/>'
    step = iw / max(1, len(items))
    bw = max(1.0, min(24.0, step * 0.7))
    for i, (lab, v) in enumerate(items):
        x = pad + i * step + step * 0.15
        y = pad + ih * (1 - (max(v, 0) - lo) / span) if v >= 0 else zero_y
        bh = abs(ih * v / span)
        col = "#27ae60" if v >= 0 else "#c0392b"
        bars += f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{col}"/>'
    return f'<svg viewBox="0 0 {w} {h}" style="width:100%;background:#fff">{bars}</svg>'


def _table(headers: list[str], rows: list) -> str:
    if not rows:
        return '<p class="muted">暂无数据</p>'
    th = "".join(f"<th>{h}</th>" for h in headers)
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>'


def refresh_dashboard(cfg: AppConfig, state: dict) -> str:
    """生成可视化HTML统计面板（无外部依赖，浏览器直接打开）。"""
    ts = trade_stats(state.get("trade_log", []))
    tk = track_stats(state.get("paper_track", []))
    sells = [t for t in state.get("trade_log", []) if t.get("side") == "sell" and "pnl" in t]
    members = _team_members(state)
    meta = state.get("meta", {})
    evo = state["evolution"]
    snap = (state.get("regime") or {}).get("snapshot") or {}
    ar = arena_stats(state.get("arena"))

    css = ("body{font-family:'Microsoft YaHei',sans-serif;background:#f5f6f8;margin:0;padding:24px;color:#222}"
           "h1{font-size:22px}h2{font-size:16px;margin:28px 0 8px;border-left:4px solid #2c7be5;padding-left:8px}"
           ".card{background:#fff;border-radius:8px;padding:16px;margin:10px 0;box-shadow:0 1px 3px rgba(0,0,0,.08)}"
           "table{width:100%;border-collapse:collapse;font-size:13px}"
           "th,td{padding:6px 8px;border-bottom:1px solid #eee;text-align:left}"
           "th{background:#f0f3f7}.pos{color:#27ae60;font-weight:600}.neg{color:#c0392b;font-weight:600}"
           ".muted{color:#888;font-size:12px}")

    def sign(v):
        return f'<span class="{"pos" if v >= 0 else "neg"}">{v:+,.0f}</span>'

    rows_reason = [[r, v["n"], f"{v['wins']/v['n']*100:.0f}%", sign(v["pnl"])]
                   for r, v in sorted(ts["by_reason"].items(), key=lambda kv: kv[1]["pnl"], reverse=True)]
    rows_code = [[c, v["n"], f"{v['wins']}/{v['n']}", sign(v["pnl"])]
                 for c, v in sorted(ts["by_code"].items(), key=lambda kv: kv[1]["pnl"], reverse=True)]
    rows_members = []
    for m in members:
        h = m.get("holdout", {})
        rows_members.append([m["strategy"], h.get("score", "-"), h.get("metrics", {}).get("cagr", "-"),
                             (m.get("stress") or {}).get("mean", "-")])
    rows_retired = []
    for r in state.get("champion_retired", []):
        if "members" in r:
            rows_retired.append(["退役团队", ", ".join(r.get("members", [])),
                                 r.get("team_avg", "-"), r.get("retired_at", "")[:16]])
        else:
            rows_retired.append(["退役冠军", r.get("strategy", "?"),
                                 r.get("holdout", {}).get("score", "-"), r.get("retired_at", "")[:16]])
    rows_stress = []
    for s in (state.get("stress_history") or [])[-14:]:
        ok = (s["mean"] >= cfg.meta.stress_min_mean
              and s["beat_cash_pct"] >= cfg.meta.stress_min_beat_pct)
        rows_stress.append([s.get("date", ""), "✅通过" if ok else "❌未过",
                            f"{s['mean']:.3f}", f"{s['beat_cash_pct']*100:.0f}%",
                            f"{s['beat_bench_pct']*100:.0f}%", f"{s['worst']:.3f}"])
    rows_risk = [[e.get("date", ""), e.get("type", ""), e.get("detail", "")]
                 for e in state.get("risk_events", [])[-20:]]
    rows_days = [[d, sign(v)] for d, v in sorted(ts["by_date"].items())]
    rows_arena = []
    if ar.get("top"):
        for p in ar["top"]:
            rows_arena.append([f"最赚 {p['id']}", p["strategy"], f"{p['_ret']*100:+.2f}%"])
        for p in ar["bottom"]:
            rows_arena.append([f"最亏 {p['id']}", p["strategy"], f"{p['_ret']*100:+.2f}%"])
    rows_evo = [[h["gen"], h["time"][:16], h["best_score"], h["mean_score"],
                 h.get("sigma_boost", 1.0), h.get("best", {}).get("strategy", "")]
                for h in evo.get("history", [])[-12:][::-1]]

    pnl_items = [(f"{t['date']}{t['code']}", t["pnl"]) for t in sells]
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Money 统计面板</title><style>{css}</style></head>
<body><h1>Money 自进化交易系统 · 统计面板（好的坏的全在这）</h1>
<p class="muted">生成于 {dt.datetime.now():%Y-%m-%d %H:%M} | 模式 {cfg.mode} |
本金 {cfg.risk.initial_capital:,.0f} 元 | 模拟盘与实盘共用决策风控；实盘成交以券商对账单为准</p>
<div class="card"><h2>账户轨道（逐日推进）</h2>
{_svg_line([t["equity"] for t in state.get("paper_track", [])])}
{f'<p>起点 {tk["start"]:,.0f} → 期末 {tk["end"]:,.0f} 元 | 区间收益 <b>{_pct(tk["ret"])}</b> | 最大回撤 <b class="neg">{_pct(tk["max_dd"])}</b> | {tk["days"]} 个交易日</p>' if tk.get("days") else '<p class="muted">轨道自首个交易日起累积</p>'}
</div>
<div class="card"><h2>逐笔已实现盈亏（绿=盈利 红=亏损）</h2>{_svg_bars(pnl_items)}
<p>平仓 {ts['n_sells']} 笔：胜 {ts['wins']} / 负 {ts['losses']} |
累计已实现 <b>{sign(ts['realized'])}</b> 元 |
盈亏比 {f"{ts['profit_factor']:.2f}" if ts['profit_factor'] else ('∞' if ts['gross_win'] > 0 else '-')} |
最大单笔盈利 {sign(ts['max_win'])} / 最大单笔亏损 {sign(ts['max_loss'])}</p></div>
<div class="card"><h2>离场原因归因（止损伤多少、超时赚不赚）</h2>{_table(["离场原因","笔数","胜率","累计盈亏(元)"], rows_reason)}</div>
<div class="card"><h2>标的归因（赚钱的与亏钱的并排）</h2>{_table(["标的","平仓笔数","胜/总","累计盈亏(元)"], rows_code)}</div>
<div class="card"><h2>每日已实现盈亏</h2>{_table(["日期","盈亏(元)"], rows_days)}</div>
<div class="card"><h2>冠军团队（各策略族出一人，资金均分）</h2>
{_table(["成员","样本外分","样本外年化","体检均分"], rows_members)}
{_table(["状态","策略","团队均分/分数","时间"], rows_retired)}</div>
<div class="card"><h2>市场风格与模型验证</h2>
<p>{snap.get('trend','-')} / {snap.get('factor_style','-')} / {snap.get('size_style','-')} |
波动分位 {snap.get('vol_pct','-')} |
当前最适族 {(snap.get('best_family_now') or {}).get('family','-')} |
曝光系数 ×{(state.get('regime') or {}).get('exposure_scale', 1.0)}{(' ⚠风格错配（防御态）' if snap.get('mismatch') else '')}</p></div>
<div class="card"><h2>随机取点体检史（❌也照登）</h2>
{_table(["日期","结论","均分","跑赢持币","跑赢基准","最差窗口"], rows_stress)}</div>
<div class="card"><h2>百人擂台·前瞻轨道（真实推进，非历史回测）</h2>
<p>{f"中位 {_pct(ar.get('median_ret',0))} | 正收益 {ar['positive']}/{ar['n']}" if ar.get('top') else '前瞻轨道自下一交易日起累积'}</p>
{_table(["选手","策略","前瞻收益"], rows_arena)}</div>
<div class="card"><h2>风控事件审计</h2>{_table(["日期","类型","详情"], rows_risk)}</div>
<div class="card"><h2>进化事件（挣扎过程也可见）</h2>
<p>累计 <b>{evo['generation']}</b> 代 | 晋升 <b>{meta.get('promotions_total',0)}</b> 次 |
停滞 <b>{meta.get('stagnations_total',0)}</b> 次 | 移民注入 <b>{meta.get('immigrants_total',0)}</b> 个 |
防御态 {'开（曝光×0.5）' if meta.get('stress_defense') else '关'}</p>
{_table(["代","时间","最优分","平均分","σ倍数","最优个体"], rows_evo)}</div>
<p class="muted">风险提示：全部统计含失败记录；历史/模拟/回测业绩均不预示未来收益。</p>
</body></html>"""
    os.makedirs(LOGS_DIR, exist_ok=True)
    path = os.path.join(LOGS_DIR, f"dashboard_{dt.date.today().strftime('%Y%m%d')}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path
