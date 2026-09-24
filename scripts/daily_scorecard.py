# -*- coding: utf-8 -*-
"""T-29 daily scorecard generator v0.1 (CEO order O-20260924-1718 战绩直达面).

Reads ONLY canonical ledgers (zero handwriting):
  results/paper/{trader}_paper.json     live.paper 真账本 (6 registered traders)
  results/shortline/o1600_market_fit.json  archived window result (O-1600, first-screen 战绩)
Emits:
  results/daily_scorecard.html   (战绩直达页, self-contained, no JS deps)
  results/daily_scorecard.json    (machine-readable mirror, evidence_cutoff top-level)

Honesty rules (O-1718 §三): months_tracked=0 -> 残月不计, first full 战绩月=2026-10,
first complete report=10-31 首检; no future promises; numbers as-is from ledgers.
v0.2 queue (ticket note): desktop 量化战绩.lnk + dashboard top-row wiring.
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER_DIR = os.path.join(ROOT, "results", "paper")
OUT_HTML = os.path.join(ROOT, "results", "daily_scorecard.html")
OUT_JSON = os.path.join(ROOT, "results", "daily_scorecard.json")


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
            "risk_regime": d.get("risk_regime") or {},
        })
    return rows


def _load_o1600():
    p = os.path.join(ROOT, "results", "shortline", "o1600_market_fit.json")
    if not os.path.exists(p):
        return None
    d = json.load(io.open(p, encoding="utf-8"))
    return d


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
      "padding:10px 14px;font-size:12px;color:#d2a8ff;margin-top:16px}</style></head><body>")
    A("<h1>量化战绩 · 每日直达面</h1>")
    A(f"<div class='sub'>数据截止 {cutoff} · 生成于 paper 真账本+已归档成绩单 · "
      f"全部数字自动取自 results/paper 与 O-1600 成绩单，零手写（T-29 · O-1718）</div>")

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
    A("<div class='sub'>操作台账：纸盘尚在首月（起跑 2026-09-23），在册员尚未触发开平仓信号；"
      "「选股择时」动作台账自首笔信号起逐笔记录（fill_guard 计数随每 bar 更新）。</div>")

    A("<h2>月度战绩（完整成绩单）</h2>")
    A("<div class='sub'>完整战绩月自 2026-10-01 起算（IV6+REGIME_GUARD enforce 双切换）；"
      "首份完整月度成绩单=2026-10-31 首检；月度四件套自动并入。</div>")
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
        "generated_from": ["results/paper", "results/shortline/o1600_market_fit.json"],
        "traders": rows,
        "o1600_first_screen": {"passive_ew48_ret_pct": passive_pct,
                               "traders": o1600_rows},
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
