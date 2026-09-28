"""T-105: CEO live-usage daily one-pager generator (v1.1, aggregation-only).

Deliverable per O-20260928-1533 sec.4 / T-105 spec: an AUTO-GENERATED daily
one-pager the CEO can follow manually.  PURE PROJECTION of existing
calibrated faces -- ZERO new judgments, zero new indicators (fail-closed
law: sleeves not activated stay disclosed NOT_ACTIVATED).

v1.1 (r391 bm-b, O-20260928-1555 + O-20260928-1605):
  - five-member universe tier annotations (first-layer huijin high-control
    510050/510300, second-layer 510500/512100/588000; ChiNext excluded)
  - national-team status row in section 1 (current support/sell/neutral +
    one-line basis).  Face source = T-106 control-degree quantification
    (bm-c, in build) -- until that face lands the row honestly reads
    "quantification in flight"; face wiring = v1.2 on T-106 artifact.

Faces consumed (all existing, read-only):
  - results/regime_state.json            (REGIME_GUARD v3 state machine)
  - results/paper_export/latest.json     (T-35 d3: 6 traders positions/capital)
  - results/portfolio_blend_tournament.json (T-27: B_MAXDIV champion weights)
  - research/DECISION_CHAIN_LEDGER.md    (version banner rows, auto-derived)

Output: docs/live_usage/LIVE-YYYYMMDD.md + .json twin.  Same-day reruns
regenerate in place (idempotent); other days are never touched
(daily_report precedent).

Usage:
    python scripts/ceo_live_usage.py             # generate for today
    python scripts/ceo_live_usage.py selftest   # hermetic, no network
Exit codes: 0 = ok, 2 = mechanism fault (missing face / shape drift).
"""
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REGIME_JSON = os.path.join(ROOT, "results", "regime_state.json")
PAPER_LATEST = os.path.join(ROOT, "results", "paper_export", "latest.json")
BLEND_JSON = os.path.join(ROOT, "results",
                          "portfolio_blend_tournament.json")
LEDGER_MD = os.path.join(ROOT, "research", "DECISION_CHAIN_LEDGER.md")
OUT_DIR = os.path.join(ROOT, "docs", "live_usage")

# Position ladder, v2 frozen canonical (DECISION_CHAIN v2 prereg, adopted
# bm-c 2026-09-28; owner-canon rows in market_clock POSITION_LADDER):
LADDER = [
    ("RED", 0.20, "红色急跌/熔断态：股票敞口上限 20%"),
    ("YELLOW", 0.65, "黄色过渡态：上限 65%"),
    ("ORANGE", 0.50, "橙色高危态：上限 50%"),
    ("GREEN", 0.80, "绿色常态：上限 80%"),
    ("GREEN×HOT", 0.95, "绿色且市场热度 HOT：上限 95%"),
]
SIX = ("COMPOSITE-CE-01", "COMPOSITE-CE-02", "DROUGHT-CE-01",
       "ENGULF-CE-01", "NEEDLE-DE-01", "VOLATILITY-CE-01")
# Five-member universe final verdict (O-20260928-1555, CEO direct order):
# tier-1 huijin high-control {510050 SSE50, 510300 HS300}; tier-2
# {510500 CSI500, 512100 CSI1000, 588000 STAR50}.  ChiNext excluded.
UNIVERSE_T1 = {"510300", "510050"}
UNIVERSE_T2 = {"510500", "512100", "588000"}
CHINEXT_EXCL = {"159915", "159949"}   # 创业板指出列 (O-1555)
SECTOR_HINT = {          # honest category hints, no full spectrum re-derive
    "511880": "货币ETF", "511990": "货币ETF",
    "513100": "跨境ETF", "518880": "黄金ETF",
}
BOND_PREFIX = "511"


def _read_json(path):
    with open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)


def _classify(code: str) -> str:
    """Honest constituent annotation (O-1555 five-member verdict /
    O-1533 sec.1.3 / T-105 spec)."""
    code = str(code)
    if code in UNIVERSE_T1:
        return "宽基·第一层（汇金高度控盘·O-1555）"
    if code in UNIVERSE_T2:
        return "宽基·第二层（O-1555）"
    if code in CHINEXT_EXCL:
        return "创业板指出列（O-1555 禁新增·存量持仓月界动作）"
    if code in SECTOR_HINT:
        return SECTOR_HINT[code]
    if code.startswith(BOND_PREFIX):
        return "债券ETF（非宽基研究宇宙）"
    return "行业/主题或非五员宽基（O-1533/O-1555 收窄注记：非研究宇宙）"


def _version_banner() -> list:
    """Derive version rows from the ledger table (append-only canon)."""
    out = []
    with open(LEDGER_MD, encoding="utf-8") as fh:
        for line in fh:
            s = line.strip()
            if not s.startswith("| v"):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) < 6:
                continue
            verdict = cells[-1]
            if verdict.startswith("PENDING"):
                status = "PENDING（烧批/队列中）"
            elif verdict.startswith("LANDED"):
                status = "LANDED（已判）"
            else:
                status = verdict[:12]
            out.append((cells[0][:24], status))
    return out


def _fmt_cny(x) -> str:
    return f"{x:,.0f}"


def build_payload(day: str) -> dict:
    regime = _read_json(REGIME_JSON)
    paper = _read_json(PAPER_LATEST)
    blend = _read_json(BLEND_JSON)

    state = regime.get("state", "?")
    caps = {name: cap for name, cap, _ in LADDER}
    cur_cap = caps.get(state.split("×")[0] if state == "GREEN×HOT" else state,
                      None)
    if state == "GREEN" and regime.get("hot"):
        cur_cap = caps["GREEN×HOT"]          # reserved for v1.1 clock face
    cap_row = next((r for r in LADDER if r[0] == state), None)
    if cap_row is None:                      # unknown state -> honest fault
        raise RuntimeError(f"regime state {state!r} not in frozen ladder")

    weights = (blend.get("weights", {}).get("B_MAXDIV", {})
               .get("weights", {}))
    traders = {t["trader"]: t for t in paper.get("traders", [])}

    members = []
    for tid in SIX:
        tr = traders.get(tid)
        if tr is None:
            raise RuntimeError(f"registered trader {tid} missing from "
                                "paper_export/latest.json")
        cap_c = tr.get("capital_cny", {})
        pos_rows = []
        for p in tr.get("open_positions", []):
            pos_rows.append({
                "symbol": str(p["symbol"]),
                "category": _classify(p["symbol"]),
                "market_value_cny": round(p["market_value_cny"], 0),
                "hold_days": p.get("hold_days"),
                "unrealized_pnl_cny": round(p["unrealized_pnl_cny"], 0),
            })
        members.append({
            "trader": tid,
            "b_maxdiv_weight": round(weights.get(tid, 0.0), 6),
            "equity_cny": round(cap_c.get("equity", 0.0), 0),
            "cash_cny": round(cap_c.get("cash", 0.0), 0),
            "positions": pos_rows,
        })

    return {
        "schema": "ceo_live_usage_v1_1",
        "ticket": "T-202609-28-105",
        "day": day,
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "market": {
            "state": state,
            "asof": regime.get("asof"),
            "mode": regime.get("mode"),
            "days_in_state": regime.get("days_in_state"),
            "triggers": regime.get("triggers", []),
            "bench_close": regime.get("dims", {}).get("bench", {})
                           .get("close"),
            "bench_ma200": regime.get("dims", {}).get("bench", {})
                            .get("ma200"),
        },
        "national_team": {
            "status": "中性（量化采集进行中）",
            "basis": "T-106 控盘度量化面在建（O-20260928-1540 令 + "
                     "O-20260928-1605 升格：份额异动+持仓披露差分+事件台账"
                     "+舆论新闻面四面）；本行=T-105 状态行占位诚实律——"
                     "face 落地前禁编造当值判读，v1.2 接线实测读数",
            "face_source": "T-106 s1 control-degree quantification "
                           "(owner bm-c, in build)",
        },
        "ladder": {
            "rungs": [{"state": n, "cap": c, "note": d}
                      for n, c, d in LADDER],
            "current_state": state,
            "current_cap": cap_row[1],
        },
        "corps_note": ("ORANGE 态当值军种=震荡+防御（MARKET_STAGE_TABLE）；"
                       "B_MAXDIV=防守型混合过渡正典（MSG-1958·军内分散法）"
                       if state == "ORANGE" else
                       "军种当值表按 MARKET_STAGE_TABLE 随政体态切换"),
        "members": members,
        "chain_versions": [
            {"version": v, "status": s} for v, s in _version_banner()],
        "disclaimers": [
            "本页=决策链条研究产出的聚合展示，非投资建议；",
            "CEO 手动跟随=CEO 直接权限；公司自动实盘开闸=月界（2026-10-01）"
            "+CEO 唯一门，本页不改变该门；",
            "未激活袖面如实披露 NOT_ACTIVATED；既有六员持仓含行业 ETF 成分"
            "按 O-1533 如实标注，改仓=月界统一动作不追溯；",
            "研究宇宙=五员宽基定谳（O-20260928-1555）：第一层 上证50/沪深300"
            "（汇金高度控盘）·第二层 中证500/中证1000/科创50；创业板指出列，"
            "行业/主题/跨境/债券/黄金维持排除；",
            "数据口径=最近收盘 bar（asof 见上），日内刷新=v1.1（T-104 实时源"
            "落地后）。",
        ],
    }


def render_md(p: dict) -> str:
    m = p["market"]
    L = []
    L.append(f"# CEO 实盘使用一页纸 · {p['day']}")
    L.append("")
    L.append(f"> 自动生成 {p['generated']} · T-105 v1.1 · "
             "纯聚合面（零新判据）· [版本台账]"
             "(../../research/DECISION_CHAIN_LEDGER.md)")
    L.append("")
    L.append("## ① 市场判定")
    L.append("")
    L.append(f"- **当前政体态：{m['state']}**（shadow 探测·已连续 "
             f"{m['days_in_state']} 日）· asof {m['asof']}")
    L.append(f"- 依据：{'; '.join(m['triggers']) or '（无触发面在案）'}")
    L.append(f"- 沪深300ETF 收盘 {m['bench_close']} vs MA200 "
             f"{m['bench_ma200']}"
             + ("（熔断线之下）" if (m['bench_close'] or 0)
                < (m['bench_ma200'] or 0) else "（熔断线之上）"))
    nt = p["national_team"]
    L.append(f"- **国家队状态：{nt['status']}** · 依据：{nt['basis']}")
    L.append("")
    L.append("## ② 仓位指令（阶梯总帽）")
    L.append("")
    L.append(f"- **当前态 {p['ladder']['current_state']} → 股票敞口总帽 "
             f"{p['ladder']['current_cap']:.0%}**")
    L.append("- 阶梯全表（冻结）：")
    for r in p["ladder"]["rungs"]:
        mark = " ←当前" if r["state"] == p["ladder"]["current_state"] else ""
        L.append(f"  - {r['state']}：{r['cap']:.0%} — {r['note']}{mark}")
    L.append("- 状态切换触发器（REGIME_GUARD v3 冻结面）："
             "十日累计≤−8% / 20日波动>3年滚动p95 / 广度崩塌"
             "（core48 价<MA20 占比≥80% 且 5 日斜率为负）/ 沪深300<MA200 "
             "熔断线；GREEN×HOT 满热档=温度计 HOT 复合（v1.1 接线）。")
    L.append("")
    L.append("## ③ 六员分配与当前持仓")
    L.append("")
    L.append(f"- {p['corps_note']}")
    L.append("- 六员权重=B_MAXDIV 冠军组合面（T-27 锦标赛 winner，10-01 起 "
             "SPM-v1 enforce 接线）；持仓=纸盘在册实况（T-35 导出面）：")
    for mem in p["members"]:
        L.append("")
        L.append(f"### {mem['trader']}（权重 "
                 f"{mem['b_maxdiv_weight']:.2%}｜权益 ¥"
                 f"{_fmt_cny(mem['equity_cny'])}｜现金 ¥"
                 f"{_fmt_cny(mem['cash_cny'])}）")
        if not mem["positions"]:
            L.append("  - （当前空仓）")
        for pos in mem["positions"]:
            L.append(f"  - {pos['symbol']}｜{pos['category']}｜市值 ¥"
                     f"{_fmt_cny(pos['market_value_cny'])}｜持有 "
                     f"{pos['hold_days']} 日｜浮盈亏 "
                     f"{_fmt_cny(pos['unrealized_pnl_cny'])}")
    L.append("")
    L.append("## ④ 决策链版本横幅")
    L.append("")
    for v in p["chain_versions"]:
        L.append(f"- {v['version']}：{v['status']}")
    L.append("- v1 诚实锚：链输（J-TARGET 0/12 未过）；v2 简化链=池序首位"
             "在烧；v3 锦标赛=预注册冻结排队；赢家=只入册候选，上线走月界。")
    L.append("")
    L.append("## ⑤ 诚实免责")
    L.append("")
    for d in p["disclaimers"]:
        L.append(f"- {d}")
    L.append("")
    return "\n".join(L)


def run() -> int:
    day = dt.date.today().strftime("%Y-%m-%d")
    try:
        payload = build_payload(day)
    except Exception as exc:                                    # noqa: BLE001
        print(f"ceo_live_usage: mechanism fault (exit 2) -- {exc}")
        return 2
    os.makedirs(OUT_DIR, exist_ok=True)
    md_path = os.path.join(OUT_DIR, f"LIVE-{day}.md")
    js_path = os.path.join(OUT_DIR, f"LIVE-{day}.json")
    md = render_md(payload)
    for path, data in ((md_path, md), (js_path, None)):
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            if data is not None:
                fh.write(data)
            else:
                json.dump(payload, fh, indent=1, ensure_ascii=False)
                fh.write("\n")
        os.replace(tmp, path)
    print(f"ceo_live_usage: {md_path} (+ .json twin) written "
          f"(state={payload['market']['state']}, "
          f"cap={payload['ladder']['current_cap']:.0%}, "
          f"{len(payload['members'])} members, "
          f"{len(payload['chain_versions'])} version rows)")
    return 0


# ------------------------------ selftest ------------------------------------

def selftest() -> int:
    """Hermetic: build payload from the REAL faces (read-only, no network),
    verify structure + same-day idempotency + double-run determinism."""
    fails = []

    def check(name, cond):
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            fails.append(name)

    day = dt.date.today().strftime("%Y-%m-%d")
    try:
        p1 = build_payload(day)
        check("payload builds from real faces", True)
    except Exception as exc:                                     # noqa: BLE001
        print(f"  build_payload raised: {exc}")
        return 1
    check("market block has state+asof",
          p1["market"]["state"] in {r[0] for r in LADDER}
          and bool(p1["market"]["asof"]))
    check("national-team status row present (O-1605)",
          p1["national_team"]["status"]
          and p1["national_team"]["basis"])
    check("schema v1.1", p1["schema"] == "ceo_live_usage_v1_1")
    tier_faces = {"宽基·第一层（汇金高度控盘·O-1555）",
                  "宽基·第二层（O-1555）"}
    seen = {pos["category"] for m in p1["members"] for pos in m["positions"]}
    check("universe tiers annotated where held",
          seen <= tier_faces | {
              "货币ETF", "跨境ETF", "黄金ETF", "创业板指出列（O-1555 禁新增"
              "·存量持仓月界动作）", "债券ETF（非宽基研究宇宙）",
              "行业/主题或非五员宽基（O-1533/O-1555 收窄注记：非研究宇宙）"})
    check("ladder cap matches frozen rung",
          p1["ladder"]["current_cap"]
          == dict((n, c) for n, c, _ in LADDER)[
              p1["ladder"]["current_state"]])
    check("six members present",
          [m["trader"] for m in p1["members"]] == list(SIX))
    check("member weights loaded",
          all(isinstance(m["b_maxdiv_weight"], float)
              for m in p1["members"]))
    check("positions carry category annotation",
          all("category" in pos for m in p1["members"]
              for pos in m["positions"]))
    check("version banner derived",
          any(v["version"].startswith("v1") for v in p1["chain_versions"])
          and any(v["version"].startswith("v2")
                  for v in p1["chain_versions"]))
    check("disclaimers present", len(p1["disclaimers"]) >= 3)
    md1 = render_md(p1)
    p2 = build_payload(day)
    md2 = render_md(p2)
    static1 = md1.split("自动生成")[0] + md1[md1.index("## ①"):]
    static2 = md2.split("自动生成")[0] + md2[md2.index("## ①"):]
    check("render deterministic (wall-clock stripped)",
          static1 == static2)
    check("all five blocks in md",
          all(k in md1 for k in ("① 市场判定", "② 仓位指令",
                                 "③ 六员分配", "④ 决策链版本横幅",
                                 "⑤ 诚实免责")))
    check("national-team row rendered in md",
          "国家队状态" in md1 and "T-106" in md1)
    print(f"selftest: {'ALL PASS' if not fails else f'FAIL {fails}'}")
    return 0 if not fails else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        print("=== ceo_live_usage selftest (read-only, no network) ===")
        return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
