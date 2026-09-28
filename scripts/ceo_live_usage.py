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

v1.2 (r190 bm-c, T-106 s4 universe-face wiring -- the promised hook):
  - national-team row now DERIVED from landed T-106 artifacts (no more
    placeholder): s2 selection verdict (name-matched annual top-10 nominal
    pcts, per-ETF control band) + s3 event-window review (segment share
    fingerprints + honest zero-cell verdict).
  - s4 signal face = honest negative (s3 zero cells: point announcements
    unverifiable in dead external window, segment return_cells=0,
    N_eff=0) -> NO tournament v4+ arm; universe-face annotation only.

v1.3 (r411 bm-b, T-105 next slices per progress_r390):
  - GREENxHOT clock face wired: consumes results/market_clock/
    call_latest.json (T-74 MARKET_CLOCK_COMBO -- existing calibrated face,
    runs earlier in the same S6 chain).  Effective ladder rung = regime
    state, upgraded to GREENxHOT (cap 95%) only when regime=GREEN AND
    thermometer heat=HOT.  Pure projection of the frozen v2 ladder rule,
    zero new judgment.
  - LIVE-latest.md/.json stable rolling pointer twins (copy of today's
    page) for dashboard/daily_report direct links.

v1.4 (r412 bm-b, intraday refresh slice per T-105 spec "intraday refresh
  v1.1 (realtime feed per T-104 once landed)" -- T-104 feed landed r390):
  - intraday face consuming data/minute_feed/<code>.csv (T-104 rolling
    1m archive): per held symbol latest 1m close + day change vs the
    feed's own previous-session last close (zero cross-panel coupling),
    plus an honest per-bar freshness status (LIVE / LAGGED / PREV_SESSION /
    NO_FEED).  Pre-market runs read the previous session's close honestly;
    the face lights up as the feed accumulates from 09:15.  Pure
    projection of the feed, zero new judgment, zero portfolio re-marking
    (positions stay last-close-caliber; the intraday block is a parallel
    readout, not a re-valuation).

Faces consumed (all existing, read-only):
  - results/regime_state.json            (REGIME_GUARD v3 state machine)
  - results/paper_export/latest.json     (T-35 d3: 6 traders positions/capital)
  - results/portfolio_blend_tournament.json (T-27: B_MAXDIV champion weights)
  - research/DECISION_CHAIN_LEDGER.md    (version banner rows, auto-derived)
  - results/national_team/s2_selection_verdict.json  (T-106 s2, e_cut 08-31)
  - results/national_team/s3_event_review.json       (T-106 s3, e_cut 09-24)

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
CLOCK_JSON = os.path.join(ROOT, "results", "market_clock", "call_latest.json")
PAPER_LATEST = os.path.join(ROOT, "results", "paper_export", "latest.json")
BLEND_JSON = os.path.join(ROOT, "results",
                          "portfolio_blend_tournament.json")
LEDGER_MD = os.path.join(ROOT, "research", "DECISION_CHAIN_LEDGER.md")
NT_S2_VERDICT = os.path.join(ROOT, "results", "national_team",
                             "s2_selection_verdict.json")
NT_S3_REVIEW = os.path.join(ROOT, "results", "national_team",
                            "s3_event_review.json")
OUT_DIR = os.path.join(ROOT, "docs", "live_usage")
MINUTE_FEED_DIR = os.path.join(ROOT, "data", "minute_feed")   # T-104 (v1.4)

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


def _effective_rung(regime_state: str, heat: str) -> str:
    """Frozen v2 ladder rule (pure): GREEN regime + HOT thermometer ->
    GREENxHOT rung (cap 95%); anything else maps to its own rung.
    Aggregation-only projection, zero new judgment (v1.3 wiring of the
    placeholder reserved in v1.1)."""
    if regime_state == "GREEN" and heat == "HOT":
        return "GREEN×HOT"
    return regime_state


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


def _national_team_face() -> dict:
    """T-106 s4 universe face (v1.2): derive the CEO row from landed
    artifacts -- s2 name-matched annual disclosure pcts + s3 segment
    fingerprints + honest zero-cell signal verdict.  Plain-language
    law (O-20260927-2245): no jargon, numbers first."""
    v = _read_json(NT_S2_VERDICT)
    s3 = _read_json(NT_S3_REVIEW)
    subset = list(v["subset"])                      # frozen s2 verdict
    per = v["per_etf"]
    nom = {c: per[c]["nt_combined_pct"] for c in subset}
    # latest segment fingerprint = 2026H1 exodus (share-face direction)
    seg = s3.get("segment_share_fingerprints", {})
    exo = seg.get("NT-2026H1-EXODUS", {})
    exo_510300 = exo.get("510300") or {}
    exo_delta = exo_510300.get("delta")
    zero_cell = (s3.get("n_cells", -1) == 0 and s3.get("n_eff", -1) == 0)
    if subset and all(nom[c] >= 80 for c in subset) and zero_cell:
        status = "存量高控·近期无已验证增持动作"
    else:                                          # honest fallback, no invented verdict
        status = "读数异构·见依据行（禁编造当值判读）"
    basis = (
        f"最新年报 top-10 名义持仓（T-106 s2·证据截至 {v['evidence_cutoff']}）："
        f"汇金两司合计 沪深300={nom.get('510300', 0)}%、"
        f"上证50={nom.get('510050', 0)}%（extreme 控盘带·>=20% 披露表佐证）；"
        "2026 上半年份额段指纹=区间净撤离（T-106 s3 EXODUS 段：510300 "
        f"{exo_delta / 1e8:.0f} 亿份·证据截至 {s3.get('evidence_cutoff')}）；"
        "增持公告面=外网窗口全灭·零已验证新增动作。"
        "白话：国家队年报纸面还握大头，但上半年份额在退，也没有可信的新买公告"
    )
    return {
        "status": status,
        "basis": basis,
        "face_source": "T-106 s2+s3 landed artifacts (owner bm-c)",
        "s2_evidence_cutoff": v["evidence_cutoff"],
        "s3_evidence_cutoff": s3.get("evidence_cutoff"),
        "supported_subset": subset,
        "nominal_pct": nom,
        "per_etf_band": {c: per[c]["kongpan_band"] for c in v["universe"]},
        "understated_note": "510500=75.58% heavy、512100=86.43% extreme："
                            "第二层持仓实测高于 CEO 两层命名暗示（UNDERSTATED"
                            "如实注记）；588000=0 名义缺席；159915=54.03% 非 CEO "
                            "点名员",
        "signal_face": {
            "verdict": "not_supported（诚实判负）",
            "basis": "T-106 s3 事件窗复盘=零格（点事件公告面外网不可达→冻结条款"
                     "转段级；段级 return_cells=0·N_eff=0·账本 +0）——无『跟国家"
                     "队』可交易边缘证据 → 不开锦标赛 v4+ 臂，一页纸只挂宇宙面"
                     "标注（s4 spec 证据门控 IF-not 路径）",
            "universe_face_only": True,
        },
    }


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


def _intraday_face(held_symbols, today: str) -> dict:
    """v1.4 intraday readout (T-104 minute feed, pure projection).

    Per held symbol: latest 1m close + day change vs the feed's own
    previous-session last close.  Honest freshness status per bar; no
    portfolio re-marking, no new judgment.  Symbols outside the feed
    universe (v1.2 narrowing) get an honest NO_FEED row."""
    rows = []
    now = dt.datetime.now()
    asof = None
    for sym in sorted(held_symbols):
        path = os.path.join(MINUTE_FEED_DIR, f"{sym}.csv")
        if not os.path.exists(path):
            rows.append({"symbol": sym, "status": "NO_FEED",
                         "note": "T-104 分钟宇宙外（v1.2 收窄）·口径=最近收盘"})
            continue
        last_day = last_close = prev_close = None
        with open(path, encoding="utf-8-sig") as fh:
            for line in fh:
                parts = line.strip().split(",")
                if len(parts) < 5 or parts[0] in ("day", ""):
                    continue
                d, close = parts[0], parts[4]
                if d[:10] == today:
                    last_day, last_close = d, float(close)
                else:
                    prev_close = float(close)   # feed-internal prev session
        if last_close is None and prev_close is None:
            rows.append({"symbol": sym, "status": "NO_FEED",
                         "note": "feed 文件在位但零 bar"})
            continue
        if last_close is None:                 # no today bars yet
            rows.append({"symbol": sym, "status": "PREV_SESSION",
                         "latest_bar": None, "latest_close": prev_close,
                         "prev_session_close": prev_close,
                         "day_change_pct": None,
                         "note": "上一场收盘档（今日 09:15 起随源点亮）"})
            continue
        if asof is None or last_day > asof:
            asof = last_day
        age_min = (now - dt.datetime.strptime(
            last_day, "%Y-%m-%d %H:%M:%S")).total_seconds() / 60.0
        status = "LIVE" if age_min <= 10.0 else "LAGGED"
        chg = (last_close / prev_close - 1.0) \
            if prev_close else None
        rows.append({"symbol": sym, "status": status,
                     "latest_bar": last_day, "latest_close": last_close,
                     "prev_session_close": prev_close,
                     "day_change_pct": round(chg * 100, 2)
                     if chg is not None else None,
                     "age_min": round(age_min, 1)})
    n_live = sum(1 for r in rows if r["status"] == "LIVE")
    return {
        "feed": "T-104 minute_feed (rolling 1m archive, bm-b lane)",
        "today": today,
        "asof": asof,          # latest today-bar across feed (None=pre-market)
        "n_held_with_feed": sum(1 for r in rows
                                if r["status"] != "NO_FEED"),
        "n_live": n_live,
        "rows": rows,
    }


def build_payload(day: str) -> dict:
    regime = _read_json(REGIME_JSON)
    clock = _read_json(CLOCK_JSON)
    paper = _read_json(PAPER_LATEST)
    blend = _read_json(BLEND_JSON)

    state = regime.get("state", "?")
    heat = (clock.get("heat_composite") or {}).get("heat")
    if not heat:                       # clock face shape drift -> honest fault
        raise RuntimeError("market_clock call_latest.json: heat_composite"
                           ".heat missing (run market_clock_call.py first)")
    rung = _effective_rung(state, heat)
    cap_row = next((r for r in LADDER if r[0] == rung), None)
    if cap_row is None:                      # unknown state -> honest fault
        raise RuntimeError(f"effective rung {rung!r} not in frozen ladder")

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

    held = sorted({pos["symbol"] for m in members
                   for pos in m["positions"]})
    return {
        "schema": "ceo_live_usage_v1_4",
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
            "clock_cell": clock.get("clock_cell"),
            "clock_asof": clock.get("asof"),
            "heat": heat,
            "heat_basis": (
                f"LHB 当日 {hc.get('rows_last_day')} 行 · 净买 "
                f"{hc.get('net_buy_sum_yuan', 0) / 1e8:.2f} 亿 vs 250日"
                f" p80={hc.get('rolling250_p80_rows')} 行（温度计="
                f"{heat}）"
                if (hc := clock.get("heat_composite") or {}) else ""),
        },
        "national_team": _national_team_face(),
        "ladder": {
            "rungs": [{"state": n, "cap": c, "note": d}
                      for n, c, d in LADDER],
            "regime_state": state,
            "current_state": rung,
            "current_cap": cap_row[1],
        },
        "corps_note": ("ORANGE 态当值军种=震荡+防御（MARKET_STAGE_TABLE）；"
                       "B_MAXDIV=防守型混合过渡正典（MSG-1958·军内分散法）"
                       if state == "ORANGE" else
                       "军种当值表按 MARKET_STAGE_TABLE 随政体态切换"),
        "members": members,
        "intraday": _intraday_face(held, day),
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
            "国家队标注=T-106 s4 宇宙面（实测年报名义持仓+2026H1 撤离段指纹）；"
            "跟队信号面按 s3 诚实判负只挂标注，不产生交易指令；",
            "持仓口径=最近收盘 bar（asof 见上）；盘中档=T-104 分钟源实时读出"
            "（v1.4 已接线·③节），09:15 起随源点亮·平行读出非重估值；",
        ],
    }


def render_md(p: dict) -> str:
    m = p["market"]
    L = []
    L.append(f"# CEO 实盘使用一页纸 · {p['day']}")
    L.append("")
    L.append(f"> 自动生成 {p['generated']} · T-105 v1.2 · "
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
    L.append(f"- **市场时钟**：`{m['clock_cell']}`（asof {m['clock_asof']}）· "
             f"温度计 {m['heat_basis'] or m['heat']}")
    L.append(f"- 满热档判定（v1.3 已接线）：政体态 {m['state']}"
             + (" + 温度计 HOT → **GREEN×HOT 满热档生效（95%）**"
                if p['ladder']['current_state'] == "GREEN×HOT"
                else f" + 温度计 {m['heat']} → 满热档未触发（需 GREEN+HOT）"))
    nt = p["national_team"]
    # 3.11-safe: precompute the nominal join (bm-c r190 v1.2 nested
    # same-quote f-string was PEP 701 3.12-only = syntax death on the
    # fleet's 3.11.9 interpreters; output bytes unchanged)
    _nominal = '、'.join(
        "{}={}%".format(c, nt['nominal_pct'][c])
        for c in nt['supported_subset'])
    L.append(f"- **国家队状态：{nt['status']}** · 依据：{nt['basis']}")
    L.append(f"  - 宇宙面注记（T-106 s4）：已验证高控两员="
             f"{'、'.join(nt['supported_subset'])}"
             f"（名义 {_nominal}）；"
             f"{nt['understated_note']}")
    L.append(f"  - 跟队信号面：{nt['signal_face']['verdict']}——"
             f"{nt['signal_face']['basis']}")
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
             "熔断线；GREEN×HOT 满热档=GREEN 政体态+温度计 HOT 复合"
             "（v1.3 已接线 results/market_clock/call_latest.json）。")
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
    intr = p["intraday"]
    L.append("### 盘中档（T-104 分钟源·v1.4）")
    if intr["asof"]:
        L.append(f"- 最新 1m bar {intr['asof']}（LIVE {intr['n_live']}/"
                 f"{intr['n_held_with_feed']} 员在流）")
    else:
        L.append(f"- 今日尚未有 bar（上一场收盘档·09:15 起随源点亮）"
                 f"——在场 {intr['n_held_with_feed']} 员照挂上一场收盘")
    for r in intr["rows"]:
        if r["status"] == "NO_FEED":
            L.append(f"  - {r['symbol']}：{r['note']}")
        elif r["status"] == "PREV_SESSION":
            L.append(f"  - {r['symbol']}：上一场收盘 {r['latest_close']}"
                     f"（{r['note']}）")
        else:
            chg = (f"{r['day_change_pct']:+.2f}%"
                   if r.get("day_change_pct") is not None else "n/a")
            L.append(f"  - {r['symbol']}：{r['latest_close']}（{chg}·"
                     f"{r['status']}·bar {r['latest_bar']}"
                     f"·lag {r['age_min']}min）")
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
    # v1.3: stable rolling pointer twins (copy of today's page) for
    # dashboard / daily_report direct links (dated pages stay append-only).
    ptr = [(md_path, md), (js_path, None),
           (os.path.join(OUT_DIR, "LIVE-latest.md"), md),
           (os.path.join(OUT_DIR, "LIVE-latest.json"), None)]
    for path, data in ptr:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            if data is not None:
                fh.write(data)
            else:
                json.dump(payload, fh, indent=1, ensure_ascii=False)
                fh.write("\n")
        os.replace(tmp, path)
    print(f"ceo_live_usage: {md_path} (+ .json twin + LIVE-latest pointers) "
          f"written (state={payload['market']['state']}, "
          f"rung={payload['ladder']['current_state']}, "
          f"cap={payload['ladder']['current_cap']:.0%}, "
          f"heat={payload['market']['heat']}, "
          f"{len(payload['members'])} members, "
          f"intraday={payload['intraday']['asof'] or 'PREV_SESSION'} "
          f"live={payload['intraday']['n_live']}, "
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
    check("national-team face DERIVED (v1.2, not placeholder)",
          p1["national_team"]["face_source"]
          .startswith("T-106 s2+s3 landed artifacts")
          and p1["national_team"]["supported_subset"]
          == ["510300", "510050"]
          and p1["national_team"]["nominal_pct"]["510300"] == 82.76
          and p1["national_team"]["nominal_pct"]["510050"] == 86.05
          and p1["national_team"]["signal_face"]["universe_face_only"]
          is True)
    check("schema v1.4", p1["schema"] == "ceo_live_usage_v1_4")
    intr = p1["intraday"]
    check("intraday face present (v1.4)",
          intr["feed"].startswith("T-104 minute_feed")
          and intr["n_held_with_feed"] >= 0)
    stat_ok = {r["status"] for r in intr["rows"]} <= {
        "LIVE", "LAGGED", "PREV_SESSION", "NO_FEED"}
    shape_ok = True
    for r in intr["rows"]:
        if r["status"] == "NO_FEED":
            continue
        if not isinstance(r.get("latest_close"), float):
            shape_ok = False
            break
        if r["status"] in ("LIVE", "LAGGED") and not str(
                r.get("latest_bar", "")).startswith("2026-"):
            shape_ok = False
            break
    check("intraday rows honest-status shaped", stat_ok and shape_ok)
    check("intraday asof consistent with row statuses",
          (intr["asof"] is None)
          == all(r["status"] in ("PREV_SESSION", "NO_FEED")
                 for r in intr["rows"]))
    check("intraday disclaimer updated (v1.4 landed)",
          any("盘中档=T-104 分钟源实时读出" in d
              for d in p1["disclaimers"]))
    check("clock face consumed (v1.3)",
          bool(p1["market"]["clock_cell"]) and bool(p1["market"]["clock_asof"])
          and p1["market"]["heat"] in ("HOT", "COOL", "WARM", "COLD"))
    check("effective-rung law: GREEN+HOT -> GREENxHOT 95%",
          _effective_rung("GREEN", "HOT") == "GREEN×HOT"
          and _effective_rung("GREEN", "COOL") == "GREEN"
          and _effective_rung("ORANGE", "HOT") == "ORANGE"
          and _effective_rung("RED", "COOL") == "RED")
    check("ladder rung = frozen-law projection of faces",
          p1["ladder"]["current_state"]
          == _effective_rung(p1["market"]["state"], p1["market"]["heat"])
          and p1["ladder"]["current_cap"]
          == dict((n, c) for n, c, _ in LADDER)[
              p1["ladder"]["current_state"]])
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
          "国家队状态" in md1 and "T-106" in md1
          and "宇宙面注记" in md1 and "跟队信号面" in md1)
    check("clock + full-heat-tier rows rendered in md",
          "市场时钟" in md1 and "满热档判定" in md1
          and ("GREEN×HOT 满热档生效" in md1
               or "满热档未触发" in md1))
    check("intraday block rendered in md (v1.4)",
          "盘中档（T-104 分钟源·v1.4）" in md1)
    print(f"selftest: {'ALL PASS' if not fails else f'FAIL {fails}'}")
    return 0 if not fails else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        print("=== ceo_live_usage selftest (read-only, no network) ===")
        return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
