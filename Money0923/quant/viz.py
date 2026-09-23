"""可视化看盘室：把系统真实状态渲染成自包含 HTML（无外部依赖，离线可开）。

自动化机制：auto 守护每轮进化后自动重生成 dashboard.html，
浏览器打开后 meta-refresh 每 30 秒自动重载 = 常驻"看盘"画面。
所有数字均取自 state/state.json 与 logs/ 真实运行留痕，无任何虚构数据。
覆盖全生态：账户/冠军团队/进化曲线/联赛/WF链式验证/锦标赛/风格/机制/审计/风控。
"""
from __future__ import annotations

import datetime as dt
import glob as _glob
import html
import json
import os
import re

from . import clock
from .config import LOGS_DIR, ROOT, AppConfig
from .state import load_state

PALETTE = ["#38bdf8", "#f472b6", "#fbbf24", "#34d399", "#a78bfa", "#fb7185",
           "#60a5fa", "#f97316", "#4ade80", "#e879f9", "#facc15", "#22d3ee"]

_GREEN, _RED, _AMBER, _DIM = "#4ade80", "#fb7185", "#fbbf24", "#8296b8"


def _pct(x, digits: int = 2) -> str:
    try:
        return f"{float(x) * 100:+.{digits}f}%"
    except Exception:  # noqa: BLE001
        return "—"


def _num(x, digits: int = 2) -> str:
    try:
        return f"{float(x):.{digits}f}"
    except Exception:  # noqa: BLE001
        return "—"


def _esc(x) -> str:
    return html.escape(str(x)) if x is not None else "—"


def _color_ret(x: float) -> str:
    return _GREEN if (x or 0) >= 0 else _RED


def _line_chart(points: list[tuple[str, float]], w: int = 640, h: int = 200,
                color: str = "#38bdf8") -> str:
    """权益折线图：面积填充 + 网格 + 首末/最高最低标注。"""
    pts = [(d, v) for d, v in points if v is not None]
    if len(pts) < 2:
        return ('<div class="empty">数据不足（≥2个点后绘制）——模拟盘轨道自首个交易日收盘后累积</div>')
    vals = [v for _, v in pts]
    vmin, vmax = min(vals), max(vals)
    if vmax <= vmin:  # 平线时留出可视区间
        vmax = vmin * 1.001 or 1.0
        vmin = vmin * 0.999
    rng = vmax - vmin
    pad = 30
    n = len(pts)
    coords = []
    for i, v in enumerate(vals):
        x = pad + i * (w - 2 * pad) / max(1, n - 1)
        y = h - pad - (v - vmin) / rng * (h - 2 * pad)
        coords.append((x, y))
    line = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    area = line + f" L{coords[-1][0]:.1f},{h - pad:.1f} L{coords[0][0]:.1f},{h - pad:.1f} Z"
    last_x, last_y = coords[-1]
    imax = vals.index(max(vals))
    grid = "".join(
        f'<line x1="{pad}" y1="{y:.1f}" x2="{w - pad}" y2="{y:.1f}" class="grid"/>'
        f'<text x="{w - pad + 4:.1f}" y="{y + 4:.1f}" class="tick">{v:,.0f}</text>'
        for v, y in [(vmax, pad), (vmin, h - pad)])
    return f'''<svg viewBox="0 0 {w} {h}" class="chart">
      {grid}
      <path d="{area}" fill="{color}" opacity="0.12"/>
      <path d="{line}" fill="none" stroke="{color}" stroke-width="2"/>
      <circle cx="{coords[imax][0]:.1f}" cy="{coords[imax][1]:.1f}" r="3.5" fill="{color}" opacity="0.7"/>
      <circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="4" fill="{color}"/>
      <text x="{pad}" y="{h - 6}" class="tick">{pts[0][0]}</text>
      <text x="{w - pad}" y="{h - 6}" class="tick" text-anchor="end">{pts[-1][0]}</text>
      <text x="{max(pad, last_x - 8):.1f}" y="{max(16, last_y - 10):.1f}" class="tick" text-anchor="end">{pts[-1][1]:,.0f}</text>
    </svg>'''


def _dual_chart(points: list[tuple[str, float, float]], w: int = 640, h: int = 220) -> str:
    """进化曲线：best（青）+ mean（琥珀）双线。"""
    pts = [(d, b, m) for d, b, m in points]
    if len(pts) < 2:
        return '<div class="empty">进化刚启动，曲线生成中…</div>'
    allv = [v for _, b, m in pts for v in (b, m)]
    vmin, vmax = min(allv), max(allv)
    if vmax <= vmin:
        vmax, vmin = vmin + 1e-9, vmin - 1e-9
    rng = vmax - vmin
    pad = 28
    n = len(pts)

    def path_of(idx: int) -> tuple[str, tuple[float, float]]:
        coords = []
        for i, row in enumerate(pts):
            x = pad + i * (w - 2 * pad) / max(1, n - 1)
            y = h - pad - (row[idx] - vmin) / rng * (h - 2 * pad)
            coords.append((x, y))
        return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in coords), coords[-1]

    p_best, e_best = path_of(1)
    p_mean, _ = path_of(2)
    return f'''<svg viewBox="0 0 {w} {h}" class="chart">
      <path d="{p_mean}" fill="none" stroke="#fbbf24" stroke-width="1.6" opacity="0.85"/>
      <path d="{p_best}" fill="none" stroke="#38bdf8" stroke-width="2"/>
      <circle cx="{e_best[0]:.1f}" cy="{e_best[1]:.1f}" r="4" fill="#38bdf8"/>
      <text x="{pad}" y="{h - 8}" class="tick">{pts[0][0]}</text>
      <text x="{w - pad}" y="{h - 8}" class="tick" text-anchor="end">{pts[-1][0]}</text>
      <text x="{w - pad}" y="16" class="tick" text-anchor="end">best {pts[-1][1]:.4f} / mean {pts[-1][2]:.4f}</text>
    </svg>
    <div class="legend"><span class="dot" style="background:#38bdf8"></span>最优适应度
    <span class="dot" style="background:#fbbf24"></span>种群均值</div>'''


def _donut(counts: dict[str, int]) -> str:
    """策略家族分布环图（纯 SVG）。"""
    total = sum(counts.values()) or 1
    r, cx, cy, sw = 70, 90, 90, 26
    circ = 2 * 3.14159265 * r
    segs, offset = [], 0.0
    items = sorted(counts.items(), key=lambda kv: -kv[1])
    for i, (name, cnt) in enumerate(items):
        frac = cnt / total
        color = PALETTE[i % len(PALETTE)]
        segs.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{sw}" '
                    f'stroke-dasharray="{frac * circ:.1f} {circ - frac * circ:.1f}" '
                    f'stroke-dashoffset="{-offset:.1f}" transform="rotate(-90 {cx} {cy})"/>')
        offset += frac * circ
    center = (f'<text x="{cx}" y="{cy - 4}" class="donut-num">{total}</text>'
              f'<text x="{cx}" y="{cy + 14}" class="donut-sub">个体</text>')
    legend = "".join(
        f'<div class="lg-row"><span class="dot" style="background:{PALETTE[i % len(PALETTE)]}"></span>'
        f'{_esc(name)} <b>{cnt}</b></div>'
        for i, (name, cnt) in enumerate(items))
    return (f'<svg viewBox="0 0 180 180" class="donut">{"".join(segs)}{center}</svg>'
            f'<div class="legend-col">{legend}</div>')


def _fam_bars(counts: dict[str, int], max_rows: int = 8) -> str:
    """横向家族分布条形图（联赛Top10构成等）。"""
    if not counts:
        return '<div class="empty">暂无数据</div>'
    top = max(counts.values()) or 1
    rows = sorted(counts.items(), key=lambda kv: -kv[1])[:max_rows]
    parts = []
    for i, (name, c) in enumerate(rows):
        color = PALETTE[i % len(PALETTE)]
        parts.append(
            f'<div class="bar-row"><span class="bar-name">{_esc(name)}</span>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{c / top * 100:.0f}%;background:{color}"></div></div>'
            f'<b>{c}</b></div>')
    return f'<div class="fam-bars">{"".join(parts)}</div>'


def _risk_gauge(equity: float, high: float, halt_pct: float) -> str:
    """回撤预算仪表：距 -X% 停机线的缓冲。"""
    if high <= 0 or equity <= 0:
        return '<div class="empty">账户未启动</div>'
    dd = equity / high - 1.0
    used = max(0.0, min(1.0, -dd / halt_pct))
    remain = 1.0 - used
    color = _GREEN if used < 0.5 else (_AMBER if used < 0.8 else _RED)
    return f'''<div class="gauge">
      <div class="gauge-bar"><div class="gauge-fill" style="width:{used * 100:.0f}%;background:{color}"></div></div>
      <div class="gauge-label">距停机线（-{halt_pct:.0%}）剩余缓冲 <b style="color:{color}">{remain * 100:.0f}%</b>
      &nbsp;·&nbsp; 当前回撤 <b style="color:{color}">{_pct(dd)}</b></div>
    </div>'''

def _next_open() -> tuple[dt.datetime, bool]:
    """下一开市时刻 + 当前是否盘中（与 run._next_open_dt 同口径）。"""
    now = dt.datetime.now()
    day = now.date()
    if clock.is_trade_date(day) and now.time() < dt.time(9, 25):
        return dt.datetime.combine(day, dt.time(9, 25)), False
    d = day
    for _ in range(60):
        d += dt.timedelta(days=1)
        if clock.is_trade_date(d):
            return dt.datetime.combine(d, dt.time(9, 25)), \
                clock.is_trade_date(day) and dt.time(9, 25) <= now.time() <= dt.time(15, 6)
    return dt.datetime.combine(day + dt.timedelta(days=1), dt.time(9, 25)), False


def _wf_card() -> str:
    """WF 链式验证卡：解析最新 logs/walkforward_*.md（历史当实盘的铁证）。"""
    files = sorted(_glob.glob(os.path.join(LOGS_DIR, "walkforward_*.md")))
    if not files:
        return '<div class="empty">尚未生成（auto 每周末自动跑链式验证，也可 run.py wf 手动）</div>'
    try:
        with open(files[-1], encoding="utf-8") as f:
            text = f.read()
        gen_m = re.search(r"生成:\s*([\d\-]+ [\d:]+)", text)
        tot_m = re.search(r"链式总收益\s*([+-][\d.]+)%.*?年化\s*([+-][\d.]+)%" r".*?等权基准同期\s*([+-][\d.]+)%",
                          text, re.S)
        rows = re.findall(
            r"\|\s*(\d{4}-\d{2}-\d{2}~\d{4}-\d{2}-\d{2})\s*\|\s*([^|]+?)\s*\|\s*([+-][\d.]+)%", text)
        if not (gen_m and tot_m and rows):
            return '<div class="empty">报告解析失败（格式变更？），请看原文件</div>'
        tr, ann, bench = float(tot_m.group(1)), float(tot_m.group(2)), float(tot_m.group(3))
        chips = (f'<span class="chip">链式 <b style="color:{_color_ret(tr)}">{tr:+.2f}%</b></span>'
                 f'<span class="chip">年化 <b style="color:{_color_ret(ann)}">{ann:+.2f}%</b></span>'
                 f'<span class="chip">等权基准 <b style="color:{_color_ret(bench)}">{bench:+.2f}%</b></span>'
                 f'<span class="chip">相对基准 <b style="color:{_color_ret(tr - bench)}">{tr - bench:+.2f}%</b></span>')
        trs = []
        for win, team, ret in rows[:6]:
            ret_f = float(ret)
            is_cash = "空仓" in team
            trs.append(f'<tr><td>{win}</td><td class="{"dim" if is_cash else ""}">{_esc(team)}</td>'
                       f'<td style="color:{_color_ret(ret_f)}">{ret_f:+.2f}%</td></tr>')
        return (f'<div class="chips">{chips}</div>'
                f'<table style="margin-top:10px"><tr><th>窗口（实盘段）</th><th>团队</th><th>段收益</th></tr>'
                f'{"".join(trs)}</table>'
                f'<div class="legend">报告 {os.path.basename(files[-1])} · 生成于 {_esc(gen_m.group(1))} · '
                f'每窗只用窗前数据进化，下一段当实盘全规则撮合 · '
                f'<a href="logs/{os.path.basename(files[-1])}">原文</a></div>')
    except Exception:  # noqa: BLE001
        return '<div class="empty">报告读取失败</div>'


def _audit_card() -> str:
    """防作弊审计卡：解析 logs/audit_ledger.jsonl 最新一次审计结果。"""
    path = os.path.join(LOGS_DIR, "audit_ledger.jsonl")
    last_result = None
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except Exception:  # noqa: BLE001
                        continue
                    if rec.get("type") == "audit_result":
                        last_result = rec
        except Exception:  # noqa: BLE001
            last_result = None
    if not last_result:
        return '<div class="empty">审计未运行（auto 闭市段每日自动，或 run.py audit 手动）</div>'
    nl = last_result.get("no_lookahead") or {}
    det = last_result.get("determinism") or {}
    checks = nl.get("checks") or []
    npass = sum(1 for c in checks if c.get("pass"))
    hash_ok = bool(det.get("equity_hash")) and det.get("equity_hash") == det.get("equity_hash_2")
    passed = bool(last_result.get("passed"))
    pill = (f'<span class="pill pill-ok">🟢 通过</span>' if passed
            else '<span class="pill pill-bad">🔴 未通过</span>')
    eq = det.get("final_equity")
    return (f'<div class="metrics" style="margin-top:0">'
            f'<div class="m"><b>{"✅" if passed else "❌"}</b><span>总体结论</span></div>'
            f'<div class="m"><b>{npass}/{len(checks)}</b><span>无未来函数抽查</span></div>'
            f'<div class="m"><b>{"✓" if hash_ok else "✗"}</b><span>复算哈希一致</span></div>'
            f'<div class="m"><b>{str(det.get("equity_hash") or "—")[:8]}</b><span>净值指纹</span></div></div>'
            f'<div class="legend" style="margin-top:8px">{pill} 完成于 {_esc(last_result.get("finished_at", "—"))}'
            f'{f" · 复核期末权益 {float(eq):,.0f} 元" if eq else ""} · '
            f'先声明后揭示（台账 logs/audit_ledger.jsonl），防"先看结果再下结论"</div>')


def _league_card(state: dict) -> str:
    """联赛循环赛卡：随机窗开局（窗长随赛季配置） · 多样性前10晋级 · 连胜认证 → 基因注入GA。"""
    a = state.get("arena") or {}
    rh = a.get("round_history") or []
    if not rh:
        return '<div class="empty">联赛尚未开局（auto 闭市段自动进行）</div>'
    last = rh[-1]
    best = last.get("best") or {}
    fam: dict[str, int] = {}
    for p in (last.get("top10") or []):
        fam[p.get("strategy", "?")] = fam.get(p.get("strategy", "?"), 0) + 1
    total = a.get("round") or len(rh)
    qids_all = {q.get("id") for q in (a.get("qualified") or [])}
    qn = len(qids_all)
    # round_history 的 qualified 是 ID 字符串列表（历史格式）；顶层 qualified 是 dict
    # 列表——统一归一化后渲染（此前最新一局含新认证时渲染必崩→仪表盘间歇陈旧）
    new_q = [{"id": q, "strategy": "?"} if isinstance(q, str) else q
             for q in (last.get("qualified") or [])]
    new_q_html = "".join(
        f'<span class="chip">★认证 {_esc(q.get("id"))}({_esc(q.get("strategy"))})</span>'
        for q in new_q[:3]) or '<span class="chip dim">本局无新认证</span>'
    wl = str(last.get("window", ""))
    yrs = wl.split("≈", 1)[1].split("）", 1)[0].strip() if "≈" in wl else ""
    return (f'<div class="metrics" style="margin-top:0">'
            f'<div class="m"><b>{total:,}</b><span>累计局数</span></div>'
            f'<div class="m"><b>{qn}</b><span>稳定前10认证</span></div>'
            f'<div class="m"><b>{_num(last.get("mean_score"), 3)}</b><span>本局均分</span></div>'
            f'<div class="m"><b>{_esc(best.get("id", "—"))}</b><span>本局最佳({_esc(best.get("strategy", "—"))} {_num(best.get("score"), 2)})</span></div>'
            f'</div>'
            f'<div class="legend" style="margin-top:8px">最新一局窗口 {_esc(last.get("window", "—"))} · '
            f'每局=随机{_esc(yrs)}窗100人独立回测，多样性前10晋级，连续3局晋级即认证</div>'
            f'<div style="margin-top:10px"><div class="legend" style="margin:0 0 4px">本局Top10 家族构成</div>'
            f'{_fam_bars(fam)}</div>'
            f'<div class="chips" style="margin-top:10px">{new_q_html}</div>')


def _arena_board(cfg: AppConfig, state: dict) -> str:
    """百人锦标赛排行榜：前瞻轨道（参数冻结链式回放=模拟实盘）的真实竞赛数据。"""
    a = state.get("arena") or {}
    players = a.get("players") or []
    if not players:
        return '<div class="empty">锦标赛尚未开赛（auto 守护每周六自动开赛）</div>'
    qids = {q.get("id") for q in (a.get("qualified") or [])}

    def ret_of(p: dict) -> float:
        cap = float(p.get("capital") or 1)
        return float(p.get("equity") or 0) / cap - 1 if cap > 0 else 0.0

    ranked = sorted(players, key=lambda p: (ret_of(p), float(p.get("score_last") or 0)), reverse=True)[:10]
    rows = []
    for i, p in enumerate(ranked):
        ret = ret_of(p)
        medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i + 1}"
        streak = int(p.get("streak") or 0)
        rows.append(
            f'<tr><td>{medal}</td><td>{_esc(p.get("id", "?"))}{"★" if p.get("id") in qids else ""}</td>'
            f'<td><span class="fam">{_esc(p.get("strategy", "?"))}</span>'
            f'<span class="badge">{_esc(p.get("style", ""))}</span></td>'
            f'<td>{"🔥" * min(streak, 3) if streak >= 2 else ""}</td>'
            f'<td style="color:{_color_ret(ret)}">{_pct(ret)}</td></tr>')
    qualified = len(qids)
    all_zero = all(abs(ret_of(p)) < 1e-9 for p in players)
    note = (' · 前瞻轨道自下个交易日收盘后开始逐日结算' if all_zero else '')
    return (f'<table><tr><th>#</th><th>选手</th><th>策略/风格</th><th>连胜</th><th>前瞻收益</th></tr>'
            f'{"".join(rows)}</table>'
            f'<div class="legend">参赛 {len(players)} 人（每队100万 · 5档风格谱系）· 认证 {qualified} 人 · '
            f'已赛 {a.get("round", 0)} 局 · 前瞻起点 {_esc(a.get("forward_start", "—"))}{note} · '
            f'<a href="logs/arena_board.html">完整竞技场看板 ↗</a></div>')


def _regime_card(cfg: AppConfig, state: dict) -> str:
    """市场风格雷达：风格引擎识别结果 + 曝光系数 + 机制提示。"""
    rg = (state.get("regime") or {}).get("snapshot") or {}
    if not rg:
        return '<div class="empty">风格引擎待运行（auto 守护自动刷新）</div>'
    best = rg.get("best_family_now") or {}
    champ_r = rg.get("champion_recent") or {}
    scale = float(rg.get("exposure_scale", 1.0) or 1.0)
    scale_color = _GREEN if scale >= 1.0 else _AMBER
    chips = "".join(
        f'<span class="chip">{k}: <b>{_esc(v)}</b></span>'
        for k, v in [("趋势", rg.get("trend")), ("因子风格", rg.get("factor_style")),
                     ("波动率", f"{float(rg.get('vol_now', 0) or 0):.1%}"),
                     ("市场宽度", f"{float(rg.get('breadth', 0) or 0):.0%}"),
                     ("大小盘", rg.get("size_style"))])
    mismatch = bool(rg.get("mismatch"))
    return (f'<div class="chips">{chips}</div>'
            f'<div class="metrics" style="margin-top:10px">'
            f'<div class="m"><b style="color:{scale_color}">×{scale:.1f}</b><span>曝光系数</span></div>'
            f'<div class="m"><b>{_esc(champ_r.get("family", "—"))}</b><span>冠军近段(夏普{_num(champ_r.get("sharpe"), 2)})</span></div>'
            f'<div class="m"><b>{_esc(best.get("family", "—"))}</b><span>当期最佳(夏普{_num(best.get("sharpe"), 2)})</span></div>'
            f'<div class="m"><b>{"⚠失配" if mismatch else "✓匹配"}</b><span>冠军适配度</span></div></div>'
            f'<div class="legend" style="margin-top:8px">风格引擎提示进化方向：{_esc(rg.get("hint_family", "—"))}'
            f'（失配时曝光自动收缩，体检不过线时进入防御态）</div>')


def _mech_stats(state: dict) -> str:
    """机制生命周期统计（机制自我更新的累计留痕）。"""
    m = state.get("meta") or {}
    evo = state.get("evolution") or {}
    stress = state.get("stress_history") or []
    last_stress = stress[-1] if stress else None
    items = [
        (evo.get("generation", 0), "🧬 进化世代"),
        (m.get("immigrants_total", 0), "🛬 累计移民注入"),
        (m.get("stagnations_total", 0), "🔁 停滞重启次数"),
        (m.get("promotions_total", 0), "👑 冠军晋升次数"),
    ]
    if last_stress:
        passed = bool(last_stress.get("pass", last_stress.get("passed")))
        items.append((f"{'✅' if passed else '❌'} {_num(last_stress.get('mean'), 3)}", "🩺 最近体检均分"))
        items.append((f"{float(last_stress.get('beat_cash_pct', 0) or 0) * 100:.0f}%", "🏃 跑赢持币占比"))
    defense = bool(m.get("stress_defense"))
    cards = "".join(f'<div class="m"><b>{_esc(v)}</b><span>{k}</span></div>' for k, v in items)
    note = ('<div class="legend" style="margin-top:8px">🩺 防御态生效中：体检未全过，曝光系数减半直至通过或新冠军上位</div>'
            if defense else "")
    return f'<div class="metrics">{cards}</div>{note}'

def _champ_team_html(cfg: AppConfig, state: dict) -> str:
    """冠军王座 + 策略团队 + 下一交易日执行预案（含晋升通道状态）。"""
    champ = state.get("champion")
    team = state.get("team") or []
    evo = state.get("evolution") or {}
    quota = int(getattr(cfg.evolve, "max_promote_attempts_per_day", 12))
    used = int(evo.get("promote_count", 0) or 0)
    dd_gate = float(getattr(cfg.meta, "team_member_max_dd", 0.05))

    parts: list[str] = []
    if champ:
        hm = (champ.get("holdout") or {}).get("metrics") or {}
        parts.append(f'''<div class="card-title">👑 冠军王座 · <span class="champ-name">{_esc(champ.get('strategy'))}</span>
        <span class="pill pill-ok">第{champ.get('gen', '?')}代上位 · {_esc(str(champ.get('promoted_at', ''))[:16])}</span></div>
        <div class="params"><code>{_esc(json.dumps(champ.get('params'), ensure_ascii=False))}</code></div>
        <div class="metrics">
          <div class="m"><b>{_pct(hm.get("cagr"))}</b><span>样本外年化</span></div>
          <div class="m"><b>{_pct(hm.get("max_dd"))}</b><span>最大回撤</span></div>
          <div class="m"><b>{_num(hm.get("sharpe"), 2)}</b><span>夏普</span></div>
          <div class="m"><b>{_pct(hm.get("win_rate"))}</b><span>胜率</span></div>
          <div class="m"><b>{_num((champ.get("holdout") or {}).get("score"), 4)}</b><span>样本外分</span></div>
        </div>''')
    elif team:
        parts.append('<div class="card-title">👑 团队执政（冠军王座空悬 · 团队制决策）</div>')
    else:
        parts.append('<div class="card-title">👑 冠军/团队</div>')

    if team:
        rows = "".join(
            f'<tr><td>{_esc(m.get("name", m.get("strategy", "?")))}</td>'
            f'<td><span class="fam">{_esc(m.get("strategy", "?"))}</span></td>'
            f'<td><span class="badge">{_esc(m.get("sizing", "equal"))}</span></td>'
            f'<td>{"✅在岗" if m.get("active", True) else "⏸休整"}</td></tr>'
            for m in team[:8])
        parts.append(f'''<table style="margin-top:8px"><tr><th>成员</th><th>策略族</th><th>仓位基因</th><th>状态</th></tr>{rows}</table>''')
        parts.append('<div class="legend" style="margin-top:6px">开市后按团队合成权重执行（各成员资金均分，'
                     f'成员样本外回撤≤{dd_gate:.0%}硬约束在岗）</div>')
    else:
        parts.append(f'''<div class="empty">王座空悬 · 团队未组建——进化出合格团队前保持空仓（防垃圾策略上场的保护）。
        晋升通道：候选须同时通过 样本外回撤≤{dd_gate:.0%} 硬闸 + 16个随机历史窗口取点体检；
        今日晋升尝试 {used}/{quota} 次（每日上限防样本外磨刷）。</div>''')

    retired = state.get("champion_retired") or []
    if retired:
        names = " · ".join(f"{_esc(r.get('strategy', '?'))}({_esc(str(r.get('retired_at', ''))[:10])})"
                           for r in retired[-4:])
        parts.append(f'<div class="legend" style="margin-top:6px">褪任者留名：{names}</div>')
    return "".join(parts)

_CSS = """
  :root { --bg:#0b1220; --card:#121b30; --line:#1f2b47; --tx:#dbe6ff; --dim:#8296b8; }
  * { box-sizing:border-box; }
  body { margin:0; padding:20px 24px 32px; background:radial-gradient(1200px 600px at 80% -10%, #16223f 0%, var(--bg) 60%);
        color:var(--tx); font-family:"Microsoft YaHei",system-ui,sans-serif; }
  h1 { font-size:22px; margin:0 0 4px; }
  .sub { color:var(--dim); font-size:12px; margin-bottom:14px; display:flex; gap:14px; flex-wrap:wrap; align-items:center; }
  .sub b { color:#7dd3fc; }
  a { color:#7dd3fc; text-decoration:none; } a:hover { text-decoration:underline; }
  .grid { display:grid; gap:14px; grid-template-columns:repeat(12,1fr); }
  .card { background:linear-gradient(180deg,var(--card),#0e1729); border:1px solid var(--line);
          border-radius:14px; padding:16px; box-shadow:0 8px 24px #0006; }
  .c3 { grid-column:span 3; } .c4 { grid-column:span 4; } .c6 { grid-column:span 6; }
  .c8 { grid-column:span 8; } .c12 { grid-column:span 12; }
  .card-title { font-size:13px; color:var(--dim); margin-bottom:10px; letter-spacing:1px; }
  .kpi b { font-size:26px; display:block; }
  .kpi span { color:var(--dim); font-size:12px; }
  .chart { width:100%; height:auto; }
  .tick { fill:#8296b8; font-size:11px; font-family:Consolas,monospace; }
  line.grid { stroke:#1a2540; stroke-width:1; }
  .empty { color:var(--dim); font-size:12px; padding:14px 4px; line-height:1.7; }
  table { width:100%; border-collapse:collapse; font-size:12px; }
  th { color:var(--dim); text-align:left; font-weight:normal; padding:4px 6px; border-bottom:1px solid var(--line); }
  td { padding:5px 6px; border-bottom:1px solid #18233c; }
  td.dim, .dim { color:var(--dim); }
  .pill { font-size:11px; padding:2px 10px; border-radius:999px; border:1px solid; margin-left:8px; }
  .pill-ok { color:#4ade80; border-color:#2f5d43; background:#12291c; }
  .pill-bad { color:#fb7185; border-color:#5d2f36; background:#291318; }
  .side { padding:1px 8px; border-radius:6px; font-size:11px; }
  .side.b { background:#12321f; color:#4ade80; } .side.s { background:#321212; color:#fb7185; }
  .gauge-bar { height:10px; background:#18233c; border-radius:999px; overflow:hidden; }
  .gauge-fill { height:100%; border-radius:999px; transition:width .6s; }
  .gauge-label { font-size:12px; color:var(--dim); margin-top:8px; }
  .donut { width:170px; flex:none; } .donut-num { fill:#dbe6ff; font-size:26px; text-anchor:middle; }
  .donut-sub { fill:#8296b8; font-size:11px; text-anchor:middle; }
  .legend-col { display:flex; flex-direction:column; gap:4px; font-size:12px; }
  .lg-row { display:flex; gap:6px; align-items:center; color:var(--dim); }
  .lg-row b { color:var(--tx); }
  .dot { width:8px; height:8px; border-radius:50%; display:inline-block; margin-right:4px; }
  .legend { font-size:11px; color:var(--dim); margin-top:6px; line-height:1.6; }
  .metrics { display:flex; gap:10px; flex-wrap:wrap; margin-top:10px; }
  .m { background:#0e1729; border:1px solid var(--line); border-radius:10px; padding:8px 12px; min-width:86px; }
  .m b { display:block; font-size:16px; } .m span { color:var(--dim); font-size:11px; }
  .params code { font-size:11px; color:#7dd3fc; word-break:break-all; }
  .champ-name { color:#fbbf24; font-size:15px; }
  .ticker { font-family:Consolas,monospace; font-size:12px; color:#7dd3fc; overflow:hidden;
            white-space:nowrap; text-overflow:ellipsis; }
  .rev { font-size:12px; color:var(--dim); padding:6px 0; border-bottom:1px dashed #1c2946; }
  .chips { display:flex; gap:8px; flex-wrap:wrap; }
  .chip { font-size:12px; background:#0e1729; border:1px solid var(--line); border-radius:8px;
          padding:4px 10px; color:var(--dim); }
  .chip b { color:var(--tx); }
  .fam { color:#7dd3fc; }
  .badge { display:inline-block; font-size:10px; padding:0 6px; margin-left:5px; border-radius:7px;
           background:#1b2a4a; color:#cddffb; border:1px solid #26375f; }
  .fam-bars { display:flex; flex-direction:column; gap:5px; }
  .bar-row { display:flex; align-items:center; gap:8px; font-size:12px; }
  .bar-name { width:110px; color:var(--dim); overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }
  .bar-track { flex:1; height:12px; background:#152036; border-radius:999px; overflow:hidden; }
  .bar-fill { height:100%; border-radius:999px; }
  .bar-row b { color:var(--tx); min-width:18px; }
  #cd { font-family:Consolas,monospace; color:#7dd3fc; font-weight:bold; }
  @media (max-width:960px) { .c3,.c4,.c6,.c8 { grid-column:span 12; } }
"""

def _sleeves_card(state: dict) -> str:
    """多队并行分仓制卡：逐仓成员/权益/回撤/停机/换人（null-safe）。"""
    svs = state.get("sleeves") or []
    if not svs:
        return ('<div class="empty">分仓制未初始化——今夜备单时自动迁移：S1=现任冠军团队 | '
                'S2/S3=认证池多样性选队（每仓独立10%停机线 · 队死换人资金保留）</div>')
    rows = []
    for sv in svs:
        hist = sv.get("history") or []
        eq = float(hist[-1].get("equity", 0) or 0) if hist else float(sv.get("cash", 0) or 0)
        start = float(sv.get("capital_start") or 0) or 1.0
        ret = eq / start - 1.0
        r = sv.get("risk") or {}
        hw = float(r.get("equity_high") or eq)
        dd = (eq / hw - 1.0) if hw > 0 else 0.0
        m = (sv.get("members") or [{}])[0]
        badge = ""
        if sv.get("retired"):
            badge = " <b>退役</b>"
        elif r.get("halt"):
            badge = " <b>停机</b>"
        rows.append(
            f"<tr><td>{_esc(sv['id'])}{badge}</td>"
            f"<td>{_esc(m.get('strategy', '空'))}/{_esc(m.get('sizing') or 'equal')}</td>"
            f"<td>{eq:,.0f}</td><td>{_pct(ret)}</td><td>{_pct(dd)}</td>"
            f"<td>{_esc(sv.get('rotations', 0))}</td></tr>")
    return (f'<table><tr><th>仓</th><th>成员</th><th>权益</th><th>自起点</th>'
            f'<th>距高水位</th><th>换人</th></tr>{"".join(rows)}</table>'
            f'<div class="legend" style="margin-top:6px">每仓独立10%停机线（收盘判定）'
            f'· 队死换人资金保留 · 账户毁灭线80%兜底 · S1跟随冠军换血</div>')


def render_dashboard(cfg: AppConfig, state: dict | None = None, out: str | None = None) -> str:
    """把当前真实状态渲染为 dashboard.html，返回文件路径。"""
    state = state or load_state()
    acc = state["account"]
    evo = state["evolution"]
    champ = state.get("champion")
    risk = state.get("risk") or {}
    track = state.get("paper_track", [])
    orders = state.get("orders_today", [])
    trades = state.get("trade_log", [])[-8:][::-1]
    reviews = state.get("reviews", [])[-3:][::-1]
    team = state.get("team") or []
    now_str = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    equity = track[-1]["equity"] if track else acc["cash"]
    from .futures import position_value
    mv = sum(position_value(c, p) for c, p in acc["positions"].items())
    day_ret = (equity / acc["day_start_equity"] - 1) if acc.get("day_start_equity") else 0.0
    total_ret = equity / cfg.risk.initial_capital - 1

    eq_points = [(t["date"], float(t["equity"])) for t in track]
    evo_points = [(rec.get("time", str(rec.get("gen", "")))[5:16],
                   float(rec.get("best_score") or 0), float(rec.get("mean_score") or 0))
                  for rec in evo.get("history", [])[-200:]]
    fam: dict[str, int] = {}
    for ind in (evo.get("population") or []):
        fam[ind.get("strategy", "?")] = fam.get(ind.get("strategy", "?"), 0) + 1

    stop_file = os.path.exists(os.path.join(ROOT, "STOP"))
    halt = bool(risk.get("halt"))
    breaker = risk.get("daily_breaker_date")

    def pill(ok: bool, ok_txt: str, bad_txt: str) -> str:
        cls = "pill-ok" if ok else "pill-bad"
        return f'<span class="pill {cls}">{"🟢 " + ok_txt if ok else "🔴 " + bad_txt}</span>'

    next_open, in_session = _next_open()

    rows_pos = "".join(
        f"<tr><td>{c}</td><td>{p['shares']}</td><td>{p.get('available', 0)}</td>"
        f"<td>{p['cost']:.2f}</td></tr>"
        for c, p in acc["positions"].items()) or \
        '<tr><td colspan="4" class="empty">空仓（无冠军/停机/待开市，按规则行动）</td></tr>'

    rows_ord = "".join(
        f'<tr><td><span class="side {"b" if o["side"] == "buy" else "s"}">{"买入" if o["side"] == "buy" else "卖出"}</span></td>'
        f"<td>{o['code']}</td><td>{o['shares']}</td><td>{_esc(o.get('reason', ''))}</td></tr>"
        for o in orders) or '<tr><td colspan="4" class="empty">暂无待执行订单</td></tr>'

    rows_tr = "".join(
        f'<tr><td>{t["date"]}</td><td><span class="side {"b" if t["side"] == "buy" else "s"}">'
        f'{"买" if t["side"] == "buy" else "卖"}</span></td>'
        f'<td>{t["code"]}</td><td>{t["shares"]}</td><td>{t["price"]}</td>'
        f'<td>{_esc(t.get("reason", ""))}</td></tr>'
        for t in trades) or \
        '<tr><td colspan="6" class="empty">尚无成交（首个交易日开盘后开始）</td></tr>'

    rows_rev = "".join(
        f'<div class="rev">📋 <b>{_esc(r.get("week"))}</b> · 世代 {_esc(r.get("gens"))} · '
        f'冠军 {_esc(r.get("champion") or "无")} · '
        f'轨道收益 {("—" if r.get("track_ret") is None else _pct(r["track_ret"]))}'
        f'{" · ⚠衰退信号" if r.get("champion_decay") else ""}</div>'
        for r in reviews) or '<div class="empty">周六自动生成首份周度复盘</div>'

    ticker = " · ".join(
        f"第{rec.get('gen', '?')}代 best={float(rec.get('best_score') or 0):.3f}"
        for rec in evo.get("history", [])[-5:][::-1]) or "进化启动中…"

    n_fam = len(fam)

    page = f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta http-equiv="refresh" content="30">
<title>💰 Money · 自进化交易看盘室</title>
<style>{_CSS}</style></head><body>
<h1>💰 Money · 自进化交易看盘室</h1>
<div class="sub">模式 <b>{cfg.mode}</b> · 更新于 {now_str} · 每30秒自动刷新 · 守护每轮进化后重生成
· {'<b>🟢 盘中会话运行中</b>' if in_session else '距下一开市 <span id="cd"></span>'}（{next_open:%Y-%m-%d %H:%M}）
· 所有数字来自真实运行状态与留痕，零虚构</div>
<div class="grid">

  <div class="card c3 kpi"><div class="card-title">账户权益（模拟本金 {cfg.risk.initial_capital:,.0f}）</div>
    <b>{equity:,.0f}</b><span>累计 {_pct(total_ret)} · 今日 {_pct(day_ret)}</span></div>
  <div class="card c3 kpi"><div class="card-title">现金 / 持仓市值</div>
    <b>{acc['cash']:,.0f}</b><span>市值 {mv:,.0f} · {len(acc['positions'])} 只持仓</span></div>
  <div class="card c3 kpi"><div class="card-title">进化世代（本轮GA）</div>
    <b>{evo['generation']:,}</b><span>晋升尝试 {_esc(evo.get('promote_count', 0))}/{_esc(getattr(cfg.evolve, 'max_promote_attempts_per_day', 12))}（今日）
    · 上次运行 {_esc((evo.get('last_run') or '—'))[:16]}</span></div>
  <div class="card c3 kpi"><div class="card-title">风控红绿灯</div>
    <b>{'🟢 正常' if (not halt and not stop_file) else '🔴 停机'}</b>
    <span>{pill(not halt, '停机未触发', '停机:' + _esc(risk.get("halt_reason"))[:24])}
    {pill(not stop_file, '无STOP', 'STOP文件!')}
    {pill(not breaker, '日熔断未触发', '日熔断' + _esc(breaker))}</span></div>

  <div class="card c6"><div class="card-title">📈 账户权益曲线（模拟实盘轨道 · 团队定型后）</div>
    {_line_chart(eq_points)}
    <div class="gauge" style="margin-top:8px">{_risk_gauge(equity, acc.get('equity_high', equity), cfg.risk.drawdown_halt_pct)}</div></div>

  <div class="card c6"><div class="card-title">🧬 进化曲线（训练适应度 · 最近200代）</div>
    {_dual_chart(evo_points)}
    <div class="ticker" style="margin-top:8px">⟳ {ticker}</div></div>

  <div class="card c8">{_champ_team_html(cfg, state)}</div>

  <div class="card c4"><div class="card-title">🌦 市场风格雷达（风格引擎实时识别）</div>
    {_regime_card(cfg, state)}</div>

  <div class="card c6"><div class="card-title">🎽 多队并行分仓制（策略风格差异化 · 每仓独立10%停机线）</div>
    {_sleeves_card(state)}</div>

  <div class="card c6"><div class="card-title">🏟 联赛循环赛（随机窗开局 · 多样性前10晋级 · 认证基因注入GA）</div>
    {_league_card(state)}</div>

  <div class="card c6"><div class="card-title">🔬 Walk-Forward 链式验证（历史当实盘 · 周末自动重跑）</div>
    {_wf_card()}</div>

  <div class="card c4"><div class="card-title">🏆 百人锦标赛（前瞻轨道 · 每队100万 · 5档风格谱系）</div>
    {_arena_board(cfg, state)}</div>

  <div class="card c4"><div class="card-title">🧪 GA种群家族分布（精英池快照 · {n_fam} 族）</div>
    <div style="display:flex;gap:14px;align-items:center">{_donut(fam)}</div></div>

  <div class="card c4"><div class="card-title">⚙️ 机制生命周期（自我更新的累计留痕）</div>
    {_mech_stats(state)}</div>

  <div class="card c4"><div class="card-title">📋 下一交易日订单（{len(orders)} 笔待执行）</div>
    <table><tr><th>方向</th><th>代码</th><th>股数</th><th>原因</th></tr>{rows_ord}</table></div>

  <div class="card c4"><div class="card-title">💼 当前持仓</div>
    <table><tr><th>代码</th><th>股数</th><th>可卖</th><th>成本</th></tr>{rows_pos}</table></div>

  <div class="card c4"><div class="card-title">🧾 最近成交（真实流水）</div>
    <table><tr><th>日期</th><th>方向</th><th>代码</th><th>股数</th><th>价格</th><th>原因</th></tr>{rows_tr}</table></div>

  <div class="card c8"><div class="card-title">🧠 机制复盘档案（自动总结）</div>
    {rows_rev}</div>

  <div class="card c4"><div class="card-title">🛡 防作弊审计（先声明后揭示 · 每日自动）</div>
    {_audit_card()}</div>

  <div class="card c12"><div class="card-title">红线与证据链</div>
    <div class="empty">红线（永不被进化自动修改）：单股≤{cfg.risk.max_position_pct:.0%} / ETF≤{cfg.risk.max_etf_position_pct:.0%}
    / 最高持股{cfg.risk.max_hold_days}个交易日 / 出局只看收盘结算：回撤{cfg.risk.drawdown_halt_pct:.0%}停机（人工复盘可恢复）+ 本金亏{cfg.risk.ruin_loss_pct:.0%}毁灭出局（唯一账户出局，盘中波动永不触发）
    　|　证据链：<a href="logs/arena_board.html">竞技场看板</a> · <a href="logs/audit_ledger.jsonl">审计台账</a>
     · MoneyViz 像素竞技场（MoneyViz/ 目录，Play 即看）
    　|　历史回测≠未来收益，模拟盘轨道是唯一的"实盘为证"</div></div>

</div>
<script>
(function() {{
  var t = Date.parse("{next_open.isoformat()}");
  var el = document.getElementById("cd");
  if (!el) return;
  function tick() {{
    var s = Math.floor((t - Date.now()) / 1000);
    if (s <= 0) {{ el.textContent = "即将开市"; return; }}
    var d = Math.floor(s / 86400), h = Math.floor(s % 86400 / 3600),
        m = Math.floor(s % 3600 / 60), ss = s % 60;
    el.textContent = (d > 0 ? d + "天 " : "") + ("0" + h).slice(-2) + ":" +
                     ("0" + m).slice(-2) + ":" + ("0" + ss).slice(-2);
  }}
  tick(); setInterval(tick, 1000);
}})();
</script>
</body></html>'''

    out = out or os.path.join(ROOT, "dashboard.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    return out




