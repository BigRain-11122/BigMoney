"""Monthly ops briefing generator (GM office mandate; O-20260923-2205 item 9; org_chart v3 GM-office team).

One-page ledger auto-generated, zero-action reach. Aggregates existing on-disk
evidence ONLY -- no network, no engine runs, no LLM (LOCAL_FIRST L1 route).
Report-only: hr.py remains the sole level authority; this file never writes
registration/trader state.

Subcommands:
  run      : write results/briefings/BRIEF-<YYYYMM>.md (default month = month
             before run date, i.e. first rounds of month M+1 brief month M;
             --month YYYYMM override for drafts/mid-month refresh). Idempotent:
             rerun regenerates the same file (deterministic given inputs).
  selftest : offline synthetic-fixture checks (render/determinism/guards/month
             rollover). Zero network, zero writes outside temp dir.
"""

import json
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIEF_DIR_NAME = "briefings"

PROV_NOTE = (
    "本简报=只读聚合台账（报告制），不改变任何编制/等级/风控状态；"
    "交易员等级唯一权在 firm/hr.py，行情防线 shadow 态非干预。"
    "数字单源：全部读自命名产物件，零手抄。"
)


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, OSError):
        return None


def _f(x, nd=4):
    try:
        return f"{float(x):.{nd}f}"
    except (TypeError, ValueError):
        return "-"


def _pct(x, nd=2):
    """Fraction (0.0368) -> percentage string (3.68%)."""
    try:
        return f"{float(x) * 100:.{nd}f}%"
    except (TypeError, ValueError):
        return "-"


def gather(root=ROOT, month=None, asof=None):
    """Collect all briefing inputs from disk. Missing pieces -> honest None/'缺件'."""
    root = Path(root)
    g = {"month": month, "asof": asof or datetime.now().strftime("%Y-%m-%d %H:%M")}

    # Roster (single source of headcount: glob, template excluded).
    roster = []
    traders_dir = root / "firm" / "traders"
    if traders_dir.is_dir():
        for p in sorted(traders_dir.glob("*.json")):
            if p.stem == "_template":
                continue
            t = _read_json(p)
            if not isinstance(t, dict) or "id" not in t:
                continue
            bt = t.get("backtest") or {}
            x2 = bt.get("cost_x2") or {}
            pp = t.get("paper") or {}
            xw = pp.get("x2_watch") or {}
            roster.append({
                "id": t["id"],
                "name": t.get("name", "-"),
                "school": t.get("school", "-"),
                "level": t.get("level", "-"),
                "created": t.get("created", "-"),
                "is_sharpe": (bt.get("in_sample") or {}).get("sharpe"),
                "oos_sharpe": (bt.get("out_sample") or {}).get("sharpe"),
                "x2_survive": x2.get("survive"),
                "x2_margin": xw.get("margin"),
                "probation": bool(xw.get("probation")),
                "paper_months": pp.get("months_tracked"),
            })
    g["roster"] = roster

    # Scorecard grades (event-cadence rerun owned by scorecard.py; we only read).
    sc = _read_json(root / "results" / "scorecard_v1.json")
    g["grades"] = {k: v for k, v in (sc or {}).get("per_trader", {}).items()} if isinstance(sc, dict) else {}
    g["scorecard_generated"] = (sc or {}).get("generated") if isinstance(sc, dict) else None
    g["skill_line"] = ((sc or {}).get("lines") or {}).get("skill_line_v2") if isinstance(sc, dict) else None

    # Paper progress per trader.
    paper = {}
    paper_dir = root / "results" / "paper"
    if paper_dir.is_dir():
        for p in sorted(paper_dir.glob("*_paper.json")):
            d = _read_json(p)
            if isinstance(d, dict) and "trader" in d:
                paper[d["trader"]] = {
                    "bars": d.get("bars"),
                    "months_tracked": d.get("months_tracked"),
                    "anchor_ok": d.get("anchor_ok"),
                    "current_dd": d.get("current_dd"),
                    "updated": d.get("updated"),
                }
    g["paper"] = paper

    # Ledger N (single source: science_gates scanner).
    n_total = None
    try:
        sys.path.insert(0, str(root / "scripts"))
        from science_gates import ledger_head
        lh = ledger_head(str(root / "results"))
        n_total = lh.get("total")
    except Exception:
        try:
            from science_gates import ledger_head  # already on sys.path (selftest)
            lh = ledger_head(str(root / "results"))
            n_total = lh.get("total")
        except Exception:
            n_total = None
    g["ledger_total"] = n_total

    # Risk flags: regime (shadow) + corr-watch + x2 probation rollup.
    reg = _read_json(root / "results" / "regime_state.json") or {}
    g["regime"] = {
        "state": reg.get("state"), "mode": reg.get("mode"),
        "days": reg.get("days_in_state"), "asof": reg.get("asof"),
    }
    cw = _read_json(root / "results" / "corr_watch.json") or {}
    w = cw.get("watch") or {}
    g["corr_watch"] = {
        "verdict": cw.get("verdict"),
        "max_is2_pair": w.get("max_is2_pair"),
        "w2_hits": list((w.get("W2_is2_convergence") or {}).get("hits", {}).keys()),
        "w2_flag": (w.get("W2_is2_convergence") or {}).get("flag"),
        "generated": cw.get("generated"),
    }
    g["probation"] = sorted(r["id"] for r in roster if r["probation"])

    # Portfolios (report-only carriers; EW6 schema=portfolios, IV6 schema=portfolios_iv).
    def _pf(d):
        if not isinstance(d, dict) or d.get("void"):
            return {}
        p = d.get("portfolios") or d.get("portfolios_iv") or {}
        x1 = ((p.get("x1") or {}).get("full") or {})
        x2 = ((p.get("x2") or {}).get("full") or {})
        v = d.get("verdict") or {}
        return {
            "sharpe": x1.get("sharpe"),
            "annual": x1.get("annual_return"),
            "dd": x1.get("max_drawdown"),
            "benefit": v.get("ew_benefit", v.get("iv_benefit")),
            "x2": x2.get("sharpe"),
            "v2_pass": v.get("v2_pass"),
        }
    for key, fname in (("ew6", "portfolio_ew6.json"), ("iv6", "portfolio_iv6.json")):
        g[key] = _pf(_read_json(root / "results" / fname))

    # Gate attrition ledger (C4): month-window batch entries.
    att = _read_json(root / "results" / "gate_attrition.json") or {}
    entries = att.get("entries", []) if isinstance(att, dict) else []
    if month:
        in_month = [e for e in entries if str(e.get("ts", "")).startswith(str(month)[:4] + "-" + str(month)[4:6])]
    else:
        in_month = []
    g["attrition_month_n"] = len(in_month)
    g["attrition_batches_month"] = sorted({e.get("batch", "-") for e in in_month})

    # New registrations in the briefing month (roster created field).
    if month:
        mstr = str(month)
        y, m = mstr[:4], mstr[4:6]
        g["roster_new_month"] = [r["id"] for r in roster if str(r["created"]).startswith(f"{y}-{m}")]
    else:
        g["roster_new_month"] = []

    # Open fleet tickets (queue, data-driven).
    open_tickets = []
    tasks_dir = root / "fleet" / "tasks"
    if tasks_dir.is_dir():
        for p in sorted(tasks_dir.glob("*.json")):
            d = _read_json(p)
            if isinstance(d, dict) and d.get("status") == "open":
                open_tickets.append(p.stem)
    g["open_tickets"] = open_tickets
    return g


def _fmt_sharpe(x, nd=4):
    return "-" if x is None else _f(x, nd)


def render(g):
    L = []
    month = g.get("month")
    month_label = f"{str(month)[:4]}-{str(month)[4:6]}" if month else "（未指定月）"
    n = len(g["roster"])
    L.append(f"# BigMoney 月度经营简报 · {month_label}")
    L.append("")
    L.append(f"- 生成时间：{g['asof']}（幂等可再生；机制=scripts/monthly_briefing.py run）")
    L.append(f"- 在册交易员：{n} 员（单源=firm/traders/ 花名册 glob）")
    if g["ledger_total"] is not None:
        L.append(f"- 试验账本累计 N={g['ledger_total']}（单源=science_gates.ledger_head 扫描 results/）")
    else:
        L.append("- 试验账本累计 N=缺件（science_gates 不可用或 results/ 空，如实标注）")
    if g.get("skill_line") is not None:
        L.append(f"- v2 判线（数据驱动）：技能线={_f(g['skill_line'])}（对账本深度多重性校正后）")
    if g.get("roster_new_month"):
        L.append(f"- 本月新注册：{len(g['roster_new_month'])} 员（{', '.join(g['roster_new_month'])}）")
    L.append("")

    # 1) Roster table.
    L.append("## 一、编制与战绩（注册证据 + 纸盘进度）")
    L.append("")
    L.append("| 交易员 | 等级 | 评级 | IS Sharpe | OOS Sharpe | ×2 存活 | ×2 垫 | paper 月/bars | 锚定 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in g["roster"]:
        gr = (g["grades"].get(r["id"]) or {})
        pm = g["paper"].get(r["id"]) or {}
        x2s = "是" if r["x2_survive"] else ("否" if r["x2_survive"] is not None else "-")
        anchor = "OK" if pm.get("anchor_ok") else ("红" if pm.get("anchor_ok") is False else "-")
        L.append(
            f"| {r['id']} | {r['level']} | {gr.get('grade','-')}({_f(gr.get('total'),1)}) "
            f"| {_fmt_sharpe(r['is_sharpe'])} | {_fmt_sharpe(r['oos_sharpe'])} "
            f"| {x2s} | {_fmt_sharpe(r['x2_margin'])} "
            f"| {pm.get('months_tracked','-')}月/{pm.get('bars','-')}bars | {anchor} |"
        )
    L.append("")
    if g.get("probation"):
        L.append(f"- ×2 看护 probation（剃刀线员自动盯防）：{', '.join(g['probation'])}")
    L.append(f"- 评级单源=results/scorecard_v1.json（生成于 {g.get('scorecard_generated') or '缺件'}，月度重算先于 hr 月检）")
    L.append("")

    # 2) Portfolio layer.
    L.append("## 二、组合层（报告制载体）")
    L.append("")
    ew6, iv6 = g.get("ew6") or {}, g.get("iv6") or {}
    if ew6.get("sharpe") is not None:
        L.append(f"- EW6（先验等权载体）：全期 Sharpe {_fmt_sharpe(ew6['sharpe'])}（年化 {_pct(ew6.get('annual'))}·回撤 {_f(ew6.get('dd'),3)}），分散化 benefit {_fmt_sharpe(ew6.get('benefit'))}，×2 组合 {_fmt_sharpe(ew6.get('x2'))}")
    else:
        L.append("- EW6：缺件（results/portfolio_ew6.json 无或字段缺）")
    if iv6.get("sharpe") is not None:
        v2 = "过" if iv6.get("v2_pass") else "未过"
        L.append(f"- IV6（风险预算，采纳=T1 呈报待批，载体仍 EW）：全期 Sharpe {_fmt_sharpe(iv6['sharpe'])}（年化 {_pct(iv6.get('annual'))}·回撤 {_f(iv6.get('dd'),3)}），benefit {_fmt_sharpe(iv6.get('benefit'))}，×2 组合 {_fmt_sharpe(iv6.get('x2'))}，v2 主门 {v2}")
    else:
        L.append("- IV6：缺件（results/portfolio_iv6.json 无或字段缺）")
    L.append("")

    # 3) Risk flags.
    L.append("## 三、风险旗")
    L.append("")
    reg = g.get("regime") or {}
    L.append(f"- 行情防线（shadow 只记录不干预）：{reg.get('state') or '缺件'}，在态 {reg.get('days','-')} 日（asof {reg.get('asof') or '-'}；enforce 未启用，v2 校准诚实 FAIL 呈 GM/CEO 重审中）")
    cw = g.get("corr_watch") or {}
    w2 = "、".join(cw.get("w2_hits") or []) or "无"
    L.append(f"- 相关性监控：{cw.get('verdict') or '缺件'}（W2 IS2 越线对：{w2}；IS2 最高对 {_fmt_sharpe(cw.get('max_is2_pair'))}；月更）")
    if g.get("probation"):
        L.append(f"- ×2 薄垫 probation：{', '.join(g['probation'])}（随每根新 bar 自动滚动盯防）")
    else:
        L.append("- ×2 薄垫 probation：无")
    L.append("")

    # 4) Research & ledger.
    L.append("## 四、研究与账本")
    L.append("")
    if g["ledger_total"] is not None:
        L.append(f"- 试验账本 N={g['ledger_total']}（含引擎跑+批格，零假设纪律全程记账）")
    if month:
        if g["attrition_month_n"]:
            L.append(f"- 本月批件损耗账（C4 台账）：{g['attrition_month_n']} 条——{', '.join(g['attrition_batches_month'])}")
        else:
            L.append("- 本月批件损耗账：本月无新批条目（或 gate_attrition.json 缺件）")
    L.append("")

    # 5) Queue.
    L.append("## 五、候选队列与待决项")
    L.append("")
    if g.get("open_tickets"):
        L.append(f"- 开放任务单（数据驱动）：{', '.join(g['open_tickets'])}")
    else:
        L.append("- 开放任务单：无（fleet/tasks 全闭环）")
    L.append("- P1 级待署名（总经理/CEO 一句话即开工）：现金腿 Phase 1 预注册、日线源双腿门票、Optuna 骨架、负面事件库消费、REGIME_GUARD enforce（校准过门前永不启用）")
    L.append("- 长线里程碑：2026-10-31 六员首月晋升检查（G2.5 三检已判=全员 HOLD 预期，禁手工改数）")
    L.append("")
    L.append("---")
    L.append(f"诚实声明：{PROV_NOTE}")
    return "\n".join(L) + "\n"


def _prev_month(d):
    y, m = d.year, d.month - 1
    if m == 0:
        y, m = y - 1, 12
    return f"{y}{m:02d}"


def cmd_run(month=None):
    month = month or _prev_month(date.today())
    g = gather(ROOT, month=month)
    out_dir = ROOT / "results" / BRIEF_DIR_NAME
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"BRIEF-{month}.md"
    text = render(g)
    tmp = out.with_suffix(".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(out)
    meta = {
        "month": month, "file": str(out.relative_to(ROOT)),
        "n_traders": len(g["roster"]), "ledger_total": g["ledger_total"],
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "class": "report-only aggregation; zero engine/N/token; idempotent regenerate",
    }
    (out_dir / "briefing_status.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[monthly_briefing] BRIEF-{month}.md written ({len(g['roster'])} traders, N={g['ledger_total']})")
    return 0


def cmd_selftest():
    ok = [0, 0]

    def check(name, cond):
        ok[0] += 1
        ok[1] += bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "firm" / "traders").mkdir(parents=True)
        (td / "results" / "paper").mkdir(parents=True)
        (td / "fleet" / "tasks").mkdir(parents=True)
        t1 = {
            "id": "TEST-CE-01", "name": "测试一号", "school": "测试流派",
            "created": "2026-09-23", "level": "INTERN",
            "backtest": {"in_sample": {"sharpe": 1.0}, "out_sample": {"sharpe": 2.0},
                         "cost_x2": {"sharpe": 0.53, "survive": True}},
            "paper": {"months_tracked": 0, "x2_watch": {"margin": 0.031, "probation": True}},
        }
        (td / "firm" / "traders" / "TEST-CE-01.json").write_text(
            json.dumps(t1, ensure_ascii=False), encoding="utf-8")
        (td / "results" / "paper" / "TEST-CE-01_paper.json").write_text(json.dumps({
            "trader": "TEST-CE-01", "anchor_ok": True, "bars": 1, "months_tracked": 0,
        }), encoding="utf-8")
        (td / "results" / "scorecard_v1.json").write_text(json.dumps({
            "generated": "2026-09-24T00:00:00",
            "lines": {"skill_line_v2": 0.93},
            "per_trader": {"TEST-CE-01": {"grade": "A", "total": 79.7}},
        }), encoding="utf-8")
        (td / "results" / "gate_attrition.json").write_text(json.dumps({
            "entries": [{"batch": "test-batch", "ts": "2026-09-24 03:00:00"}],
        }), encoding="utf-8")
        (td / "results" / "regime_state.json").write_text(json.dumps({
            "state": "ORANGE", "mode": "shadow", "days_in_state": 7, "asof": "2026-09-23",
        }), encoding="utf-8")
        (td / "results" / "portfolio_ew6.json").write_text(json.dumps({
            "void": False, "portfolios": {"x1": {"full": {"sharpe": 1.14, "annual_return": 0.036,
                                                           "max_drawdown": -0.056}},
                                          "x2": {"full": {"sharpe": 0.75}}},
            "verdict": {"ew_benefit": 0.376},
        }), encoding="utf-8")

        g1 = gather(td, month="202609", asof="2026-10-01 04:00")
        txt1 = render(g1)
        check("roster glob picks up trader (template excluded, n=1)", len(g1["roster"]) == 1)
        check("probation rollup catches razor-thin member", g1["probation"] == ["TEST-CE-01"])
        check("attrition month-window filter hits ts", g1["attrition_month_n"] == 1)
        check("roster new-in-month from created field", g1["roster_new_month"] == ["TEST-CE-01"])
        check("render contains all five sections",
              all(f"## {'一二三四五'}、".split()[0] or True for _ in [0]) and
              all(s in txt1 for s in ["一、编制与战绩", "二、组合层", "三、风险旗", "四、研究与账本", "五、候选队列"]))
        check("render surfaces probation + regime ORANGE",
              "TEST-CE-01" in txt1 and "ORANGE" in txt1)
        check("portfolio EW6 schema extraction (portfolios.x1.full)",
              g1["ew6"]["sharpe"] == 1.14 and g1["ew6"]["benefit"] == 0.376 and "EW6" in txt1)
        check("determinism: two renders identical", txt1 == render(gather(td, month="202609", asof="2026-10-01 04:00")))
        check("month rollover: 2026-10-01 -> 202609", _prev_month(date(2026, 10, 1)) == "202609")
        check("month rollover: 2026-01-05 -> 202512", _prev_month(date(2026, 1, 5)) == "202512")
        # Missing-file honesty.
        (td / "results" / "regime_state.json").unlink()
        txt2 = render(gather(td, month="202609", asof="2026-10-01 04:00"))
        check("missing regime file -> honest 缺件, no crash", "缺件" in txt2)
    print(f"selftest: {ok[1]}/{ok[0]} PASS")
    return 0 if ok[1] == ok[0] else 1


def main():
    args = sys.argv[1:]
    if args and args[0] == "selftest":
        return cmd_selftest()
    if args and args[0] == "run":
        month = None
        if "--month" in args:
            try:
                month = args[args.index("--month") + 1]
            except IndexError:
                print("usage: python scripts/monthly_briefing.py run [--month YYYYMM] | selftest")
                return 2
            if not (len(month) == 6 and month.isdigit() and 1 <= int(month[4:6]) <= 12):
                print(f"[monthly_briefing] invalid --month '{month}': expected YYYYMM (e.g. 202609)")
                return 2
        return cmd_run(month)
    print("usage: python scripts/monthly_briefing.py run [--month YYYYMM] | selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())
