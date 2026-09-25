# -*- coding: utf-8 -*-
"""T-29 daily scorecard generator v0.1 (CEO order O-20260924-1718 战绩直达面).

Reads ONLY canonical ledgers (zero handwriting):
  results/paper/{trader}_paper.json     live.paper 真账本 (6 registered traders)
  results/shortline/o1600_market_fit.json  archived window result (O-1600, first-screen 战绩)
Emits:
  results/daily_scorecard.html   (战绩直达页, self-contained, no JS deps)
  results/daily_scorecard.json   (machine-readable mirror, evidence_cutoff top-level)

v0.2 (bm-a R106 takeover slice, O-20260924-2045 s3 big-font amendment): BIG-FONT
in-house trader live face consuming results/paper_export/latest.json (T-35 d3
feed: 1M CNY capital + open positions + operations_today, deterministic zero-copy).

Honesty rules (O-1718 §三): months_tracked=0 -> 残月不计, first full 战绩月=2026-10,
first complete report=10-31 首检; no future promises; numbers as-is from ledgers.
v0.2 residual queue (ticket note): weekly one-liner -> monthly four-piece cadence.
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER_DIR = os.path.join(ROOT, "results", "paper")
OUT_HTML = os.path.join(ROOT, "results", "daily_scorecard.html")
OUT_JSON = os.path.join(ROOT, "results", "daily_scorecard.json")
POST_REVIEW_LEDGER = os.path.join(ROOT, "results", "post_review.jsonl")
PAPER_EXPORT = os.path.join(ROOT, "results", "paper_export", "latest.json")
THREE_CARD = os.path.join(ROOT, "results", "strategy_scorecard.json")


def _load_three_cards():
    """T-63 / O-20260925-1755 three-card face (strategy/trader/portfolio).
    Read-only consumption; composite totals/grades rendered ONLY when the
    payload carries calibration_consumed=True (SCORECARD_CALIB_P1 frozen
    bands per charter sec 8.5 -- pre-calibration payloads stay readout-only)."""
    if not os.path.exists(THREE_CARD):
        return None
    return json.load(io.open(THREE_CARD, encoding="utf-8"))


def _load_paper():
    rows = []
    for fn in sorted(os.listdir(PAPER_DIR)):
        if not fn.endswith("_paper.json"):
            continue
        d = json.load(io.open(os.path.join(PAPER_DIR, fn), encoding="utf-8"))
        wm = d.get("window_metrics") or {}
        md = d.get("months_detail") or []
        cur = [m for m in md if not m.get("month_ended")]
        rows.append({
            "trader": d.get("trader") or fn[:-11],
            "paper_start": d.get("paper_start"),
            "cutoff": d.get("cutoff"),
            "bars": d.get("bars"),
            "months_tracked": d.get("months_tracked"),
            "partial_month": cur[0] if cur else None,
            "current_dd": d.get("current_dd"),
            "num_trades": wm.get("num_trades"),
            "win_rate": wm.get("win_rate"),
            "fill_guard_buy_dropped": wm.get("fill_guard_buy_dropped"),
            "fill_guard_sell_deferred": wm.get("fill_guard_sell_deferred_events"),
            "forward_guard": d.get("forward_guard") or {},
            "risk_regime": d.get("risk_regime") or {},
        })
    return rows


def _load_o1600():
    p = os.path.join(ROOT, "results", "shortline", "o1600_market_fit.json")
    if not os.path.exists(p):
        return None
    d = json.load(io.open(p, encoding="utf-8"))
    return d


def _load_paper_export():
    """T-35 d3 daily export face (results/paper_export/latest.json,
    schema t35_paper_export_v1). Consumed read-only; missing file =
    face silently absent (pre-T-35 windows render v0.1 sections only)."""
    if not os.path.exists(PAPER_EXPORT):
        return None
    return json.load(io.open(PAPER_EXPORT, encoding="utf-8"))


def _cny(x):
    if x is None:
        return "—"
    return f"{x:,.0f}"


def _load_post_review():
    """T-37 d5 review column: latest sweep per claim id from the append-only
    post-review ledger (deterministic re-derivation, zero LLM, O-2115 s5).
    Filtered to the live criteria-registry id set so superseded rows (e.g.
    merged ids later split) drop off the CEO face naturally."""
    if not os.path.exists(POST_REVIEW_LEDGER):
        return None
    reg_ids = None
    reg_p = os.path.join(ROOT, "results", "post_review_criteria.json")
    if os.path.exists(reg_p):
        try:
            reg = json.load(io.open(reg_p, encoding="utf-8"))
            items = reg.get("items", reg) if isinstance(reg, dict) else reg
            reg_ids = {it.get("id") for it in items if it.get("id")}
        except ValueError:
            reg_ids = None
    latest = {}
    with io.open(POST_REVIEW_LEDGER, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            if r.get("id") and (reg_ids is None or r["id"] in reg_ids):
                latest[r["id"]] = r  # append-only -> last occurrence wins
    return list(latest.values())


def _pct(x):
    return "—" if x is None else f"{x * 100:+.2f}%"


def build():
    rows = _load_paper()
    o1600 = _load_o1600()
    cutoff = max((r["cutoff"] for r in rows if r["cutoff"]), default=None)
    o1600_rows = []
    passive_pct = None
    if o1600:
        passive_pct = o1600.get("passive_ew48_ret_pct")
        o1600_rows = list(o1600.get("traders", []))
    lines = []
    A = lines.append
    A("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>")
    A("<title>量化战绩 · BigMoney</title>")
    A("<style>body{font-family:'Microsoft YaHei',sans-serif;background:#0d1117;"
      "color:#e6edf3;margin:0;padding:24px;max-width:980px}"
      "h1{font-size:22px;margin:0 0 4px}h2{font-size:15px;color:#58a6ff;"
      "margin:22px 0 8px;border-bottom:1px solid #21262d;padding-bottom:6px}"
      ".sub{color:#8b949e;font-size:12px;margin-bottom:14px}"
      "table{border-collapse:collapse;width:100%;font-size:13px}"
      "th,td{padding:6px 10px;border-bottom:1px solid #21262d;text-align:left}"
      "th{color:#8b949e;font-weight:normal}"
      ".pos{color:#3fb950}.neg{color:#f85149}.dim{color:#8b949e}"
      ".card{background:#161b22;border:1px solid #21262d;border-radius:8px;"
      "padding:14px 16px;margin-bottom:10px}"
      ".warn{background:#1f1221;border:1px solid #3d1f4d;border-radius:8px;"
      "padding:10px 14px;font-size:12px;color:#d2a8ff;margin-top:16px}"
      "h2.bigface{font-size:26px;margin:22px 0 10px;color:#ffa657}"
      ".tcard{background:#161b22;border:1px solid #30363d;border-radius:10px;"
      "padding:18px 22px;margin-bottom:14px}"
      ".tname{font-size:24px;font-weight:bold;color:#e6edf3;margin-bottom:8px}"
      ".teq{font-size:38px;font-weight:bold;line-height:1.1}"
      ".tsub{font-size:15px;color:#8b949e;margin:2px 0 10px}"
      ".ttable{border-collapse:collapse;width:100%;font-size:16px}"
      ".ttable th,.ttable td{padding:8px 12px;border-bottom:1px solid #21262d;"
      "text-align:left}.ttable th{color:#8b949e;font-weight:normal}"
      ".facecap{font-size:13px;color:#8b949e;margin:0 0 10px}</style></head><body>")
    A("<h1>量化战绩 · 每日直达面</h1>")
    A(f"<div class='sub'>数据截止 {cutoff} · 生成于 paper 真账本+已归档成绩单 · "
      f"全部数字自动取自 results/paper 与 O-1600 成绩单，零手写（T-29 · O-1718）</div>")

    pe = _load_paper_export()
    if pe:
        pes = pe.get("summary") or {}
        first_snap = bool(pes.get("exits_not_derivable_first_snapshot"))
        A("<h2 class='bigface'>在册交易员实盘舱（大字版 · 100 万/人 纸盘本金）</h2>")
        A(f"<div class='facecap'>持仓+操作+资本自动取自 results/paper_export（T-35 d3 导出面 · "
          f"数据日 {pe.get('export_date')} · 确定性零网络）；"
          f"今日入场 {pes.get('entries_today')} 笔 / 出场 {pes.get('exits_today')} 笔"
          f"{' · 首日快照出场不可派生（诚实旗）' if first_snap else ''}（O-2045 s3）</div>")
        for t in pe.get("traders", []):
            cap = t.get("capital_cny") or {}
            eq, init = cap.get("equity"), cap.get("initial")
            pnl = None if (eq is None or init is None) else eq - init
            pnl_cls = "pos" if (pnl or 0) >= 0 else "neg"
            ops = t.get("operations_today") or []
            A("<div class='tcard'>")
            A(f"<div class='tname'>{t.get('trader')}</div>")
            A(f"<div class='teq'>{_cny(eq)} <span style='font-size:16px;"
              f"color:#8b949e'>CNY 总资产</span> "
              f"<span class='{pnl_cls}' style='font-size:18px'>"
              f"{'—' if pnl is None else f'{pnl:+,.0f}'}</span></div>")
            A(f"<div class='tsub'>本金 {_cny(init)} · 持仓市值 {_cny(cap.get('positions_value'))}"
              f" · 现金 {_cny(cap.get('cash'))} · 持仓 {t.get('positions_count')} 只</div>")
            pos = t.get("open_positions") or []
            if pos:
                A("<table class='ttable'><tr><th>持仓</th><th>数量</th>"
                  "<th>市值 CNY</th><th>浮动盈亏 CNY</th><th>持有天数</th></tr>")
                for p in pos:
                    up = p.get("unrealized_pnl_cny")
                    A(f"<tr><td>{p.get('symbol')}</td>"
                      f"<td>{p.get('quantity'):,.0f}</td>"
                      f"<td>{_cny(p.get('market_value_cny'))}</td>"
                      f"<td class='{'pos' if (up or 0) >= 0 else 'neg'}'>"
                      f"{'—' if up is None else f'{up:+,.0f}'}</td>"
                      f"<td>{p.get('hold_days')}</td></tr>")
                A("</table>")
            if ops:
                A("<table class='ttable'><tr><th>今日操作</th><th>动作</th>"
                  "<th>数量</th><th>价格</th></tr>")
                for op in ops:
                    act = op.get("action")
                    a_cls = "pos" if act == "entry" else "neg"
                    a_txt = "买入" if act == "entry" else ("卖出" if act == "exit" else act)
                    A(f"<tr><td>{op.get('symbol')}</td>"
                      f"<td class='{a_cls}'><b>{a_txt}</b></td>"
                      f"<td>{op.get('quantity'):,.0f}</td>"
                      f"<td>{op.get('cost_price')}</td></tr>")
                A("</table>")
            A("</div>")

    A("<h2>当前市场适配成绩单（已归档 · 2026-01-05 → 2026-09-23）</h2>")
    if passive_pct is not None:
        A(f"<div class='sub'>同期被动基准 EW-48：{passive_pct:+.2f}%——"
          f"2026 为下行市场，跑赢被动即适配；在册员 beat_passive 见表（O-1600）</div>")
    A("<table><tr><th>交易员</th><th>窗口收益%</th><th>回撤%</th><th>相对被动(pp)</th>"
      "<th>笔数</th><th>Sharpe</th><th>跑赢被动</th></tr>")
    for t in o1600_rows:
        ret = t.get("ret_pct")
        spread = None if (ret is None or passive_pct is None) else ret - passive_pct
        beat = t.get("beat_passive")
        A(f"<tr><td>{t.get('id')}</td>"
          f"<td>{ret:+.2f}%</td>"
          f"<td>{t.get('dd_pct', 0):+.2f}%</td>"
          f"<td class='{'pos' if (spread or 0) >= 0 else 'neg'}'>"
          f"{'—' if spread is None else f'{spread:+.2f}'}</td>"
          f"<td>{t.get('trades')}</td><td>{t.get('sharpe')}</td>"
          f"<td class='{'pos' if beat else 'neg'}'>{'✓' if beat else '✗'}</td></tr>")
    A("</table>")

    A("<h2>纸盘实盘级跟踪（live.paper 真账本）</h2>")
    A("<table><tr><th>交易员</th><th>起跑</th><th>bars</th><th>完整月数</th>"
      "<th>当月(残月·不计)</th><th>当前回撤</th><th>笔数</th><th>风控政体</th></tr>")
    for r in rows:
        pm = r["partial_month"]
        pm_s = "—" if not pm else f"{pm.get('month')} {_pct(pm.get('return'))} ({pm.get('bars')} bars)"
        A(f"<tr><td>{r['trader']}</td><td>{r['paper_start']}</td>"
          f"<td>{r['bars']}</td><td>{r['months_tracked']}</td>"
          f"<td class='dim'>{pm_s}</td>"
          f"<td class='{'neg' if (r['current_dd'] or 0) < 0 else ''}'>"
          f"{_pct(r['current_dd'])}</td>"
          f"<td>{r['num_trades']}</td>"
          f"<td class='dim'>{r['risk_regime'].get('state', '—')} "
          f"cap {r['risk_regime'].get('position_cap', '—')}</td></tr>")
    A("</table>")
    A("<div class='sub'>操作台账：实盘舱大字版（上节）逐日自 results/paper_export 差分链派生；"
      "纸盘尚在首月（起跑 2026-09-23），fill_guard 计数随每 bar 更新（禁买弃单/禁卖递延如实记）。</div>")

    # T-20 disclosure block: dual-rail fill_guard face (reporting-only wiring).
    fg_rows = [r for r in rows if r.get("forward_guard")]
    A("<h2>双轨护栏披露（T-20 · fill_guard 逐员披露面）</h2>")
    if fg_rows:
        fg_all_zero = all(
            (fg.get("buy_rejected_n") or 0) == 0
            and (fg.get("sell_deferred_events_n") or 0) == 0
            and (fg.get("deferred_days_total") or 0) == 0
            for fg in (r["forward_guard"] for r in fg_rows))
        A(f"<div class='sub'>护栏=A 轨规则保真（t14_rules_fidelity.build_guard 逐字复用）"
          f"+ B 轨纸盘执行面；{'窗口守卫事件全零（护栏在位·零拦截）' if fg_all_zero else '存在拦截/递延事件（见下表·诚实记录）'}"
          "（O-1820 · T-20）</div>")
        A("<table><tr><th>交易员</th><th>护栏</th><th>窗口语义</th>"
          "<th>买弃单</th><th>卖递延事件</th><th>递延天数</th><th>首递延日</th></tr>")
        for r in rows:
            fg = r.get("forward_guard") or {}
            if not fg:
                continue
            enabled = fg.get("enabled")
            any_hit = ((fg.get("buy_rejected_n") or 0) > 0
                       or (fg.get("sell_deferred_events_n") or 0) > 0)
            A(f"<tr><td>{r['trader']}</td>"
              f"<td class='{'pos' if enabled else 'neg'}'>"
              f"{'在位' if enabled else '缺失'}</td>"
              f"<td class='dim'>{fg.get('window_semantics') or '—'}</td>"
              f"<td class='{'neg' if (fg.get('buy_rejected_n') or 0) > 0 else ''}'>"
              f"{fg.get('buy_rejected_n', 0)}</td>"
              f"<td class='{'neg' if (fg.get('sell_deferred_events_n') or 0) > 0 else ''}'>"
              f"{fg.get('sell_deferred_events_n', 0)}</td>"
              f"<td>{fg.get('deferred_days_total', 0)}</td>"
              f"<td class='dim'>{fg.get('first_deferred_date') or '—'}</td></tr>")
        A("</table>")
    else:
        A("<div class='sub'>披露面缺件（forward_guard 未生成=护栏未随跑或字段缺失，如实标注）</div>")

    # T-63 three-card section (O-20260925-1755): strategy face full 8-dim +
    # trader/portfolio READOUT-only (sec 8.5 pre-calibration, no ranking).
    tc3 = _load_three_cards()
    A("<h2>三对象多维评价（v2 · 策略八维全卡 + 交易员/组合读数卡 · T-63）</h2>")
    if tc3:
        vet3 = tc3.get("discipline_veto_hits") or {}
        calibrated = bool((tc3.get("audit") or {}).get("calibration_consumed"))
        if calibrated:
            A(f"<div class='sub'>统一评价律：≥2 维呈报·评价≠门禁·数据驱动·硬否决即刻生效；"
              f"交易员/组合卡=校准后总分分级（SCORECARD_CALIB_P1 冻结权重带 research/"
              f"STRATEGY_SCORECARD_CALIB.md §7·评价≠门禁恒走 hr.py）·"
              f"纪律否决命中 {len(vet3)}{'：' + ', '.join(sorted(vet3)) if vet3 else ''}</div>")
        else:
            A(f"<div class='sub'>统一评价律：≥2 维呈报·评价≠门禁·数据驱动·"
              f"硬否决即刻生效；交易员/组合卡=校准前读数卡（无总分排名，"
              f"校准预注册 research/STRATEGY_SCORECARD_CALIB.md 冻结后启用）·"
              f"纪律否决命中 {len(vet3)}{'：' + ', '.join(sorted(vet3)) if vet3 else ''}</div>")
        sface = tc3.get("strategy_face") or {}
        A("<table><tr><th>策略（八维 v1.0 冻结）</th><th>级</th><th>总分</th>"
          "<th>实战</th><th>风险</th><th>成本</th><th>政体</th><th>分散</th>"
          "<th>交易</th><th>纯度</th><th>否决</th></tr>")
        for tid, c in sorted((sface.get("per_trader") or {}).items(),
                             key=lambda kv: -(kv[1].get("total") or 0)):
            dm = c.get("dims") or {}
            dv = [dm.get(str(i), {}).get("score") for i in range(1, 8)]
            A(f"<tr><td>{tid}</td><td class='pos'>{c.get('grade')}</td>"
              f"<td><b>{c.get('total'):.1f}</b></td>"
              + "".join(f"<td>{'—' if v is None else f'{v:.0f}'}</td>" for v in dv)
              + f"<td class='{'pos' if c.get('veto_clean') else 'neg'}'>"
              f"{'清' if c.get('veto_clean') else '触发'}</td></tr>")
        A("</table>")
        ptc = tc3.get("portfolio_cards") or {}
        A("<div class='sub'>组合卡：质量 Sharpe/成本 ×2/方法间 max|corr|/选择批 N（统计面）"
          + ("·总分分级=SCORECARD_CALIB_P1 冻结带" if calibrated else "（读数·无总分）")
          + "</div>")
        A("<table><tr><th>组合</th><th>级</th><th>总分</th><th>x1 Sharpe</th><th>年化</th>"
          "<th>回撤</th><th>×2 Sharpe</th><th>benefit</th><th>max|corr|</th><th>选择批 N</th></tr>")
        for name, p in sorted(ptc.items(),
                              key=lambda kv: -((kv[1].get("composite") or {}).get("total") or 0)):
            q, cost = p.get("quality") or {}, p.get("cost") or {}
            marg, stat = p.get("marginal") or {}, p.get("statistical") or {}
            comp = p.get("composite") or {}
            mc = marg.get("max_abs_corr_vs_other_methods") \
                or marg.get("max_abs_offdiag_member_corr")
            A(f"<tr><td>{name}</td>"
              + (f"<td class='pos'>{comp.get('grade')}</td>"
                 f"<td><b>{comp.get('total'):.1f}</b></td>" if comp
                 else "<td>—</td><td>—</td>")
              + f"<td>{q.get('x1_full_sharpe') or '—'}</td>"
              f"<td>{_pct(q.get('x1_annual'))}</td>"
              f"<td>{_pct(q.get('x1_max_dd'))}</td>"
              f"<td>{cost.get('x2_full_sharpe') or '—'}</td>"
              f"<td>{q.get('benefit') if q.get('benefit') is not None else '—'}</td>"
              f"<td>{mc if mc is not None else '—'}</td>"
              f"<td>{stat.get('trials_ledger_total') or '—'}</td></tr>")
        A("</table>")
        trc = tc3.get("trader_cards") or {}
        reg_n = sum(1 for c in trc.values()
                    if not str(c.get("trader", "")).startswith("PROS"))
        A(f"<div class='sub'>交易员卡 {len(trc)} 张（在册 {reg_n} + PROSPECT "
          f"{len(trc) - reg_n}）：继承策略分/纸盘实战/纪律/进度/军种画像"
          "——一切采纳晋升恒走 hr.py 冻结判据（评价≠门禁）</div>")
        if calibrated:
            A("<table><tr><th>交易员</th><th>级</th><th>总分</th><th>继承</th><th>实战</th>"
              "<th>纪律</th><th>进度</th><th>画像</th></tr>")
            for tid, c in sorted(trc.items(),
                                 key=lambda kv: -((kv[1].get("composite") or {})
                                                  .get("total") or 0)):
                comp = c.get("composite") or {}
                if not comp:
                    continue
                fsc = comp.get("face_scores") or {}
                disc = c.get("discipline") or {}
                veto = bool(comp.get("veto"))
                A(f"<tr><td>{tid}</td>"
                  f"<td class='{'neg' if veto else 'pos'}'>{comp.get('grade')}</td>"
                  f"<td><b>{comp.get('total'):.1f}</b></td>"
                  f"<td>{fsc.get('inherited', '—')}</td>"
                  f"<td>{fsc.get('live_paper', '—')}</td>"
                  f"<td class='{'neg' if veto else ('pos' if disc.get('state') == 'tested' else 'dim')}'>"
                  f"{'否决' if veto else ('清' if disc.get('state') == 'tested' else '未测')}</td>"
                  f"<td>{fsc.get('progress', '—')}</td>"
                  f"<td>{fsc.get('profile', '—')}</td></tr>")
            A("</table>")
    else:
        A("<div class='sub'>三卡面未产出（results/strategy_scorecard.json 缺件，如实标注）</div>")

    A("<h2>月度战绩（完整成绩单）</h2>")
    A("<div class='sub'>完整战绩月自 2026-10-01 起算（IV6+REGIME_GUARD enforce 双切换）；"
      "首份完整月度成绩单=2026-10-31 首检；月度四件套自动并入。</div>")

    pr_rows = _load_post_review()
    A("<h2>宣称→复验（post-review 复审列 · T-37 d5 / O-2115 §五）</h2>")
    if pr_rows:
        A("<div class='sub'>复审=确定性重derive（零 LLM·判据事前冻结·执行侧不自证）；"
          "✗=判据红=下一轮 P0 修复单；🟡=在制/未到期（pending 诚实标注，禁折算成成果）</div>")
        A("<table><tr><th>宣称</th><th>复验</th><th>宣称内容（一句话）</th>"
          "<th>证据 derive</th></tr>")
        for r in sorted(pr_rows, key=lambda x: x.get("ts", "")):
            v = r.get("verdict")
            glyph, cls = {"YES": ("✓", "pos"), "NO": ("✗", "neg"),
                          "WAIT": ("🟡", "dim"), "IDLE": ("⬜", "dim")}.get(
                v, ("?", "dim"))
            A(f"<tr><td>{r.get('id')}</td>"
              f"<td class='{cls}'>{glyph}</td>"
              f"<td>{(r.get('claim') or '')[:90]}</td>"
              f"<td class='dim'>{(r.get('evidence') or '—')[:70]}</td></tr>")
        A("</table>")
    else:
        A("<div class='sub'>复审台账未生成（post_review 首扫后本列自动出现）</div>")

    A("<div class='warn'><b>诚实边界</b>：残月不计入战绩（全员 months_tracked=0）；"
      "上表窗口成绩=研究计分口径（样本外 2026 窗·成本恒开）；"
      "不承诺未来收益；跑分幅度现阶段为稳健起步（年化 3% 级·回撤 −2.4%），"
      "「大幅」靠锦标赛与新因子线迭代爬坡，如实展示不夸大。</div>")
    A("</body></html>")
    html = "\n".join(lines)
    io.open(OUT_HTML, "w", encoding="utf-8").write(html)
    payload = {
        "ticket": "T-2026-09-24-29",
        "evidence_cutoff": cutoff,
        "generated_from": ["results/paper", "results/shortline/o1600_market_fit.json",
                           "results/paper_export/latest.json",
                           "results/strategy_scorecard.json (T-63 three-card face)"],
        "traders": rows,
        "paper_export_face": None if not pe else {
            "export_date": pe.get("export_date"),
            "schema": pe.get("schema"),
            "summary": pe.get("summary"),
            "traders": [
                {"trader": t.get("trader"),
                 "capital_cny": t.get("capital_cny"),
                 "positions_count": t.get("positions_count"),
                 "operations_today_count": len(t.get("operations_today") or [])}
                for t in pe.get("traders", [])],
        },
        "o1600_first_screen": {"passive_ew48_ret_pct": passive_pct,
                               "traders": o1600_rows},
        "post_review_latest": pr_rows,
        "post_review_source": "results/post_review.jsonl (append-only, per-id last sweep; T-37 d5)",
        "honesty": "months_tracked=0 partial-month not counted; first full month 2026-10; "
                   "first complete report 2026-10-31",
    }
    io.open(OUT_JSON, "w", encoding="utf-8").write(
        json.dumps(payload, ensure_ascii=False, indent=1))
    print("scorecard written:", OUT_HTML, "traders:", len(rows),
          "o1600 rows:", len(o1600_rows))
    return 0


if __name__ == "__main__":
    sys.exit(build())
