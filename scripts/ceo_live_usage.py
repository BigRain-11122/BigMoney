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

v1.5 (r642 bm-b, in-flight judgment-batch visibility slice -- CEO anchor
  "process must be visible"): section 5 = live burn counters for the FUND
  trio NULLS judgment batches (fund_{quality,value,divlowvol}_p1), read
  as pure append-only line counts of results/fund_*_p1/nulls.jsonl
  (have-of-2000 + dup_k integrity + last-append age in the JSON twin).
  ZERO new judgments, zero gates, zero verdicts -- counters only; the
  finalize hard gate (have == 2000) is the frozen prereg face, not a new
  line.  Disclaimers renumbered to section 6.

v1.6 (r1065 bm-b, recommendation-face surfacing -- CEO anchor "product
  first / the one-pager should carry the answer"): section 3 gains a
  "配置参考" subsection that consumes the landed PORTFOLIO-RECOMMENDATION
  face (docs/portfolio_recommendation/REC-latest.json, r1064).  Readout
  only: recommendation sentence + basis + current stage + live sleeve
  holdings (count / EW weight / entry date / turnover) + full-page pointer
  and sha16.  ZERO new judgment, zero new hypothesis, zero ledger; the
  source face is itself a zero-judged-claims aggregation, and its
  insufficient-sample verdicts travel verbatim.  Missing face = honest
  absent disclosure (page still renders, exit 0 unchanged).

v1.7 (r1152 bm-a, "how much money" roll-up -- CEO anchor "我要的是结果
  能赚钱的结果"): section 3 opens with ONE line of money for the whole book:
  total equity / starting capital / cumulative return in percent and CNY /
  positions vs cash split / today's change against the previous export.
  Every figure is derived from the paper face (each trader's own
  capital_cny.initial, equity, cash, positions_value) and the previous
  export's own summary -- no constant is assumed, and an absent prior
  export reads None with a "no comparison face" sentence rather than a
  fabricated flat day.  Cross-face assertion: the roll-up must agree with
  the export summary's total_equity_cny (tolerance = rounding of the member
  rows).  ZERO new judgment (no benchmark, no win/loss claim).

v1.8 (r1154 bm-a): section 1 gains the market risk tape -- limit-up /
  limit-down / broken-seal / strong member counts, the seal rate, the streak
  ladder and the mechanical kill-day reading, on the same forward zt-pool
  panels.  SINGLE IMPLEMENTATION: it calls scripts/daily_report._zt_risk_face,
  the exact function that renders section 9 of the daily report, so the two
  pages cannot drift into two different sets of reading rules (r1290
  two-production-faces law).  A trading day that was never captured reads as
  absent, never as 0 members (r1149 marks-coverage law).  ZERO new judgment.

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
import re
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REGIME_JSON = os.path.join(ROOT, "results", "regime_state.json")
CLOCK_JSON = os.path.join(ROOT, "results", "market_clock", "call_latest.json")
PAPER_LATEST = os.path.join(ROOT, "results", "paper_export", "latest.json")
PAPER_EXPORT_DIR = os.path.join(ROOT, "results", "paper_export")
BLEND_JSON = os.path.join(ROOT, "results",
                          "portfolio_blend_tournament.json")
LEDGER_MD = os.path.join(ROOT, "research", "DECISION_CHAIN_LEDGER.md")
NT_S2_VERDICT = os.path.join(ROOT, "results", "national_team",
                             "s2_selection_verdict.json")
NT_S3_REVIEW = os.path.join(ROOT, "results", "national_team",
                            "s3_event_review.json")
OUT_DIR = os.path.join(ROOT, "docs", "live_usage")
REPORT_DIR = os.path.join(ROOT, "docs", "daily_report")        # v1.8 parity
MINUTE_FEED_DIR = os.path.join(ROOT, "data", "minute_feed")   # T-104 (v1.4)
# In-flight NULLS judgment batches (v1.5) -- pure counter faces:
FUND_NULLS_TARGET = 2000
FUND_NULLS_FACES = (
    ("FUND-QUALITY-P1", os.path.join(ROOT, "results", "fund_quality_p1",
                                     "nulls.jsonl")),
    ("FUND-VALUE-P1", os.path.join(ROOT, "results", "fund_value_p1",
                                   "nulls.jsonl")),
    ("FUND-DIVLOWVOL-P1", os.path.join(ROOT, "results",
                                       "fund_divlowvol_p1", "nulls.jsonl")),
)
# v1.6: landed portfolio-recommendation face (pure readout, zero judgment)
REC_JSON = os.path.join(ROOT, "docs", "portfolio_recommendation",
                        "REC-latest.json")
REC_REL = "docs/portfolio_recommendation/REC-latest.json"

# v1.9: sec.2 prints the cap and sec.3 prints the money, and until r1170 nothing
# subtracted them. The verdict now exists (scripts/regime_cap_vs_book.py); this
# page QUOTES it through the producer's own reader so the two faces cannot drift
# into two different sentences (r1290 law).
CAP_VS_BOOK_JSON = os.path.join(ROOT, "results", "regime_cap_vs_book.json")

# v2.0: the six members above are the legacy paper traders; the production
# candidate is a different book (the ETF composite, vol-targeted).  Until now
# its live record had no line on this page at all -- the only place the CEO
# could read "how is the money candidate doing" was a research file.
ETF_BOOK_FWD = os.path.join(ROOT, "results", "etf_book_forward", "LEDGER.json")
# r1846: every headline number for this book lives in 2020+, and the face that
# prices the SAME engine on the SAME panel BEFORE the ETF boom already exists
# (three cells: pre-2020 universe pre-period / same universe post / full post).
# It was never on this page, so the reader could only ever read the flattering
# cell.  Read-only quote, the producer's own generated/cutoff carried.
ETF_BOOK_PRE2020 = os.path.join(ROOT, "results", "etf_book_pre2020.json")
# r1580: ⑥ reports the forward ledger, but the sheet the desk holds is a
# DIFFERENT book (5 names on the beta target, k~0.43, vs 12 names on the 8%
# vol target, k~0.91).  Both are real and both run on the same 1,000,000 CNY.
ETF_TICKET_LATEST = os.path.join(ROOT, "results", "etf_book_order",
                                 "latest.json")
# r1820: the sheet says what to buy and at what price, but not what part of that
# price is a premium over the fund's own NAV.  The producer exists and publishes a
# verdict (ENTRY_PREMIUM_WARN); the reader's page never carried it.  Read-only.
ETF_PREMIUM_JSON = os.path.join(ROOT, "results", "etf_book_premium_leak.json")
ETF_PREMIUM_REL = "results/etf_book_premium_leak.json"
ETF_PREMIUM_CHOICE_JSON = os.path.join(ROOT, "results", "etf_book_premium_choice.json")
ETF_PREMIUM_CHOICE_REL = "results/etf_book_premium_choice.json"
# r1824: the page prices the sleeve at the 1-day repo rate, which answers "how much does
# the cash earn" and leaves "which tenor do I roll this morning" unanswered -- the ladder
# face's own ticket is stamped with ITS cutoff (2026-10-27), so it reads as history. The
# new face answers today's tenor under the constraint that the cash must be back by the
# decision bar. Read-only, with a same-generation guard (r1780/r1781 class).
ETF_CASH_ROLL_JSON = os.path.join(ROOT, "results", "etf_book_cash_roll_today.json")
ETF_CASH_ROLL_REL = "results/etf_book_cash_roll_today.json"
# r1826: ⑥ tells the reader which five codes to buy and how many lots, but never how
# much of the market's own turnover that order is.  The capacity face has measured it
# for weeks (1.0087% of ADV against a 1.00% line, 0 of 60 sessions passing, the largest
# capital that fits on the best of those days = 991,421 CNY) and the reader's page never
# carried a word of it -- the r1782 shape again.  Read-only: the page quotes the face.
ETF_CAPACITY_JSON = os.path.join(ROOT, "results", "etf_book_capacity_edge.json")
ETF_CAPACITY_REL = "results/etf_book_capacity_edge.json"
# r1827: the same question asked of THIS ticket's own five names and its own amounts
ETF_CAPACITY_SIZE_JSON = os.path.join(ROOT, "results", "etf_book_capacity_at_size.json")
ETF_CAPACITY_SIZE_REL = "results/etf_book_capacity_at_size.json"
# r1828: the sheet says what to do today but never whether today is the cheap day.
# results/etf_book_do_or_wait.json has priced that question on the panel (k-bar
# ladder vs the ticket's own permission); the page quotes it, never recomputes it.
ETF_DO_OR_WAIT_JSON = os.path.join(ROOT, "results", "etf_book_do_or_wait.json")
ETF_DO_OR_WAIT_REL = "results/etf_book_do_or_wait.json"
# r1829: every line on the sheet is priced at the decision bar's close and filled at the
# next open, and the page's own caveat said only "开盘成交价会不同" -- a promise nobody
# measured.  results/etf_book_open_gap.json measures that gap on the ticket's own five
# names.  Read-only; the page quotes the face and never re-derives the series.
ETF_OPEN_GAP_JSON = os.path.join(ROOT, "results", "etf_book_open_gap.json")
ETF_OPEN_GAP_REL = "results/etf_book_open_gap.json"

# v2.2 (r1782): the index-futures carry book is the second money candidate, and
# until now its only sentence on this page was nothing at all -- "this book buys
# zero lots" lived in a research file.  The reader needs the funding line that
# prices that zero.  Read-only: the page quotes the producer's numbers and
# prints the producer's own generation stamp (r1781: a section fed by another
# script must self-stamp, or it silently shows the previous trip's face).
CARRY_OPEN_JSON = os.path.join(ROOT, "results",
                               "idx_fut_carry_open_capital.json")
CARRY_OPEN_REL = "results/idx_fut_carry_open_capital.json"
# r1787: the capital line says how much money the first lot needs; the timing face says
# whether today is a day the rule wants that lot at all.  A reader who only sees the
# first will fund the book on a day the second says to wait.
CARRY_TIMING_JSON = os.path.join(ROOT, "results", "idx_fut_basis_timing.json")
CARRY_TIMING_REL = "results/idx_fut_basis_timing.json"
# r1819: the funding line and the timing rule were both on the page, but neither said
# whether a *broker's margin* -- a floor that has nothing to do with the 8% risk dial --
# could be the thing that actually decides the lot size.  Until now the page implied the
# vol ruler was the only constraint.  The margin face answers which one bites first and
# how far the index must fall before an account is called.
CARRY_MARGIN_JSON = os.path.join(ROOT, "results", "idx_fut_carry_margin.json")
CARRY_MARGIN_REL = "results/idx_fut_carry_margin.json"
# r1820: every number above is priced at the exchange document floor (fee + one tick
# each leg = 1.5bp per roll).  The repo now measures that roll from each contract's
# own high/low, and the measured median is 20-31bp -- 13-20x the floor, worth
# 1.5-2.4pp/yr of carry.  A page that sizes a lot on the floor and never shows the
# measured drag lets the reader believe the sleeve keeps money it pays away.
CARRY_RISK_JSON = os.path.join(ROOT, "results", "idx_fut_carry_risk.json")
CARRY_RISK_REL = "results/idx_fut_carry_risk.json"
# r1845: every number in the carry section above is a mark the book has *published*.
# The book is append-only, so a mark stays published even when the panel behind it no
# longer holds that row (live 11-19: IC2612/IM2612 carry a 11-17 bar whose close is the
# main-continuous close, while the contract CSVs were last written 11-16 22:30).  A page
# that prints the P&L and never says whether the bars under it are still on disk asks the
# reader to trust a number whose evidence may be gone.
CARRY_MARKS_JSON = os.path.join(ROOT, "results", "futures_book_marks.json")
CARRY_MARKS_REL = "results/futures_book_marks.json"

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


def _judgment_burn_face() -> dict:
    """v1.5: live burn counters for the in-flight NULLS judgment batches.

    Pure readout of append-only nulls.jsonl faces (zero new judgment,
    zero gates): have = parsed line count (a half-written daemon tail line
    is skipped, never double-counted), dup_k = duplicate-k integrity,
    last_append_age_min = wall-clock freshness (JSON twin only -- kept
    out of the md render so the double-run determinism check stays
    meaningful)."""
    families = []
    for fam, path in FUND_NULLS_FACES:
        have = dup = 0
        age_min = None
        if os.path.exists(path):
            ks = []
            with open(path, "rb") as fh:
                for raw in fh:
                    raw = raw.strip()
                    if not raw:
                        continue
                    try:
                        ks.append(json.loads(raw).get("k"))
                    except ValueError:          # daemon mid-append tail
                        continue
            have = len(ks)
            dup = have - len({k for k in ks if k is not None})
            age_min = round((time.time() - os.path.getmtime(path)) / 60, 1)
        families.append({
            "family": fam,
            "present": os.path.exists(path),
            "have": have,
            "target": FUND_NULLS_TARGET,
            "dup_k": dup,
            "last_append_age_min": age_min,
        })
    return {
        "feed": "results/fund_*_p1/nulls.jsonl append-only counters",
        "target": FUND_NULLS_TARGET,
        "finalize_gate": "have == 2000（预注册冻结硬门）",
        "families": families,
    }


def _recommendation_face() -> dict:
    """v1.6: pure projection of the landed portfolio-recommendation face.
    Read-only; a missing/unreadable face degrades to an honest absent row
    (the one-pager must never fail because a research face is absent)."""
    try:
        rec = _read_json(REC_JSON)
    except (OSError, ValueError) as exc:
        return {"present": False, "path": REC_REL,
                "note": f"研究面未生成（{type(exc).__name__}）= 诚实缺省，"
                        "本页其余各节不受影响"}
    dec = rec.get("decision") or {}
    live = rec.get("live_holdings") or {}
    stage = rec.get("stage_view") or {}
    best_combo = dec.get("best_combo") or {}
    best_unc = dec.get("best_unconditional") or {}
    try:
        picks = _read_json(os.path.join(
            ROOT, "results", "divlowvol_live", "latest.json"))
    except (OSError, ValueError):
        picks = {}
    picks_panel_rel = ((picks.get("panel") or {}).get("path")
                       or os.path.join("data", "cache", "p1c_local"))
    picks_panel_present = os.path.isdir(os.path.join(ROOT, picks_panel_rel))
    return {
        "present": True,
        "path": REC_REL,
        "as_of": rec.get("as_of"),
        "status": rec.get("status"),
        "recommendation": dec.get("recommendation"),
        "basis": dec.get("basis"),
        "current_stage": stage.get("current_stage"),
        "best_combo": best_combo.get("cell"),
        "best_combo_sharpe": best_combo.get("sharpe_x1"),
        "best_unconditional": best_unc.get("face"),
        "best_unconditional_sharpe": best_unc.get("sharpe_x1"),
        "margin_sharpe": dec.get("margin_sharpe"),
        "p4_pass": dec.get("p4_pass"),
        "n_holdings": live.get("n_holdings"),
        "entry_date": live.get("entry_date"),
        "weight": live.get("weight"),
        "turnover": live.get("one_way_turnover"),
        "codes": live.get("codes") or [],
        "sha16": rec.get("sha16"),
        # The recommendation is the one block on this page that hands the
        # reader actual stock codes, and it is a MONTHLY sleeve built from a
        # 5,225-name panel that lives on bm-b.  Both facts have to travel with
        # the list: the page must be able to say when it next changes, and
        # whether this machine could rebuild it at all.
        "picks_asof": (picks or {}).get("as_of"),
        "picks_panel": picks_panel_rel,
        "picks_panel_present": picks_panel_present,
        # r1864: the list's own forward record travels with the list.  A reader who
        # is told "don't open new positions on this list" still deserves to know what
        # holding it has been worth; a face with no producer would age, so the number
        # is read from the track face only when that face is about THIS list
        # (same list_as_of) -- a newer list with an older track would be a lie.
        "track": _divlowvol_track((picks or {}).get("as_of")),
    }


def _divlowvol_track(list_as_of):
    """Published-list forward record, only when it is about that very list.

    Returns a small dict or None.  None means "we cannot say" (face missing, or the
    face tracks a different list) -- the page prints that absence rather than
    borrowing numbers from another list.
    """
    if not list_as_of:
        return None
    try:
        track = _read_json(os.path.join(ROOT, "results", "divlowvol_live",
                                        "track_latest.json"))
    except (OSError, ValueError):
        return None
    if not track or track.get("list_as_of") != list_as_of:
        return None
    bench = track.get("benchmark") or {}
    return {
        "entry_bar": track.get("entry_bar"),
        "cutoff": track.get("cutoff"),
        "sessions": track.get("window_sessions"),
        "n_measured": track.get("n_measured"),
        "ret_pct": track.get("portfolio_ret_pct"),
        "bench_n": bench.get("n"),
        "bench_ret_pct": bench.get("ret_pct"),
        "excess_pp": track.get("excess_pp"),
    }


def _prior_export_equity(day: str):
    """Total equity (CNY) of the newest paper_export dated strictly before *day*.

    Returns (date, total).  The date is the export file's own day; the total is
    read from that file's own summary face.  A missing file or a summary
    without the key reads (None, None) -- never 0, which would invent a loss.
    """
    if not os.path.isdir(PAPER_EXPORT_DIR):
        return (None, None)
    best = None
    for name in os.listdir(PAPER_EXPORT_DIR):
        if not (name.startswith("export-") and name.endswith(".json")):
            continue
        d = name[len("export-"):-len(".json")]
        if len(d) != 10 or d >= day:
            continue
        if best is None or d > best:
            best = d
    if best is None:
        return (None, None)
    ex = _read_json(os.path.join(PAPER_EXPORT_DIR, "export-%s.json" % best))
    tot = (ex.get("summary") or {}).get("total_equity_cny")
    return (best, float(tot) if isinstance(tot, (int, float)) else None)


def _rollup_face(paper: dict, day: str) -> dict:
    """v1.7 six-member money roll-up: the page must answer "how much money".

    Every number is derived from the paper face itself: initial capital from
    each trader's own capital_cny.initial, equity/cash/positions from the same
    block, and the day change from the *previous* export's summary.  No
    constant is assumed; an absent prior file reads None (never 0) so a hole
    cannot be mistaken for a flat day.
    """
    traders = {t.get("trader"): t for t in paper.get("traders", [])}
    initial = equity = cash = pos = 0.0
    n = 0
    for tid in SIX:
        c = (traders.get(tid) or {}).get("capital_cny") or {}
        if not isinstance(c.get("equity"), (int, float)):
            continue
        n += 1
        initial += float(c.get("initial") or 0.0)
        equity += float(c["equity"])
        cash += float(c.get("cash") or 0.0)
        pos += float(c.get("positions_value") or 0.0)
    prior_day, prior_eq = _prior_export_equity(day)
    face_total = (paper.get("summary") or {}).get("total_equity_cny")
    face_total = (float(face_total) if isinstance(face_total, (int, float))
                  else None)
    return {
        "n_traders": n,
        "initial_cny": round(initial, 2),
        "equity_cny": round(equity, 2),
        "cash_cny": round(cash, 2),
        "positions_cny": round(pos, 2),
        "pnl_cny": round(equity - initial, 2),
        "return_pct": (round((equity / initial - 1.0) * 100.0, 4)
                       if initial > 0 else None),
        "day_prior": prior_day,
        "day_prior_equity_cny": (round(prior_eq, 2)
                                 if prior_eq is not None else None),
        "day_pnl_cny": (round(equity - prior_eq, 2)
                        if prior_eq is not None else None),
        "day_pct": (round((equity / prior_eq - 1.0) * 100.0, 4)
                    if prior_eq else None),
        "face_total_equity_cny": face_total,
        "face_agrees": (face_total is not None
                        and abs(face_total - equity) <= 0.5 * max(n, 1)),
        "source": ("results/paper_export/export-%s.json" % day
                   if os.path.exists(os.path.join(PAPER_EXPORT_DIR,
                                                  "export-%s.json" % day))
                   else "results/paper_export/latest.json"),
    }


def _cap_vs_book_face(regime_asof=None):
    """v1.9: put the published cap-vs-book verdict next to the cap it is about.

    Single implementation: the reader is `regime_cap_vs_book.read_published`, so
    the CEO page and the daily report quote one sentence (r1290).  A missing
    artifact reads as absent -- never as "everyone is inside the cap".  The
    `stale` flag is honest bookkeeping: the artifact prices the regime state it
    saw, and a page rendered on a later state says so instead of implying it
    compared today's cap with today's book."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import regime_cap_vs_book as _rcvb
    except Exception as exc:                                   # noqa: BLE001
        return {"status": "unavailable", "detail": str(exc)[:160]}
    try:
        face = dict(_rcvb.read_published(CAP_VS_BOOK_JSON))
    except Exception as exc:                                   # noqa: BLE001
        return {"status": "unreadable", "detail": str(exc)[:160]}
    if face.get("status") != "ok":
        return face
    face["stale"] = (regime_asof is not None
                     and face.get("priced_on") not in (None, regime_asof))
    return face


def _etf_book_face():
    """v2.0: what the production candidate has actually done since it went live.

    Pure readout of results/etf_book_forward/LEDGER.json -- the book's own bars
    and the four-ETF benchmark written by the same run, so no number here is
    re-derived and no second engine is implied.  Two rules that make it honest:

    * the track record travels WITH its noise band.  `published_bars` is 11,
      and the same file says a 1-year window can only separate a 16.9pp/yr
      edge, so a +100bp excess must never be printed as if it were a verdict
      (E162: a forward ledger cannot adjudicate its own alpha).
    * a bar that is still provisional is named, not averaged in silently --
      `drift.gate == settled_bars_only` is why the last bar can still move.

    Zero new judgment: no win/loss claim, no threshold, no recommendation."""
    d = _read_json(ETF_BOOK_FWD)
    rel = "results/etf_book_forward/LEDGER.json"
    if not d:
        return {"present": False, "path": rel,
                "note": "前向账本未产出（缺面不读 0）"}
    bars = d.get("bars") or []
    bmk = (d.get("benchmark") or {}).get("bars") or []
    if not bars:
        return {"present": False, "path": rel,
                "note": "账本在册但零 bar（播种未完成）"}
    last = bars[-1]
    nav = float(last.get("nav") or 0.0)
    bench_nav = float((bmk[-1] or {}).get("nav") or 0.0) if bmk else None
    dd = [float(b.get("dd") or 0.0) for b in bars]
    # the benchmark rows carry no dd of their own -- derive it from the same
    # nav series rather than printing a 0.000% that was never measured
    bpeak, bdd = None, []
    for b in bmk:
        v = float(b.get("nav") or 0.0)
        bpeak = v if bpeak is None else max(bpeak, v)
        bdd.append(v / bpeak - 1.0 if bpeak else 0.0)
    cfg = d.get("config") or {}
    sig = (d.get("benchmark") or {}).get("significance") or {}
    pwr = sig.get("power") or {}
    drift = d.get("drift") or {}
    ret = nav - 1.0
    bret = (bench_nav - 1.0) if bench_nav is not None else None
    return {
        "present": True,
        "path": rel,
        "status": d.get("status"),
        "first_bar": (bars[0] or {}).get("bar"),
        "last_bar": last.get("bar"),
        "n_bars": len(bars),
        "book_nav": round(nav, 6),
        "book_ret_pct": round(ret * 100.0, 3),
        "bench_nav": None if bench_nav is None else round(bench_nav, 6),
        "bench_ret_pct": None if bret is None else round(bret * 100.0, 3),
        "excess_bp": None if bret is None else round((ret - bret) * 1e4, 1),
        "book_max_dd_pct": round(min(dd) * 100.0, 3) if dd else None,
        "bench_max_dd_pct": round(min(bdd) * 100.0, 3) if bdd else None,
        "n_refills": sum(1 for b in bars if b.get("filled")),
        "rebal": cfg.get("rebal"),
        "n_hold": cfg.get("n_hold"),
        "vol_target_pct": (round(float(cfg["vol_target"]) * 100.0, 1)
                           if cfg.get("vol_target") is not None else None),
        "cost_bp_per_side": (round(float(cfg["cost_per_side"]) * 1e4, 1)
                             if cfg.get("cost_per_side") is not None else None),
        "published_bars": sig.get("published_bars"),
        "noise_band_pp": sig.get("noise_band_pp") or {},
        "min_detectable_edge_pp": pwr.get("min_detectable_edge_pp") or {},
        "years_for_80pct_power": (pwr.get("years_for_80pct_power") or {}).get(
            "in-window measured alpha (single arm)"),
        "provisional_bars": drift.get("provisional_bars") or [],
        "drift_gate": drift.get("gate"),
        "panel_last_bar": (d.get("panel") or {}).get("last_bar"),
        "cash_leg_note": (cfg.get("cash")
                          if isinstance(cfg.get("cash"), str) else None),
    }


def _etf_book_period_face():
    """r1846: the book's edge has a birth date, and the page must print it.

    results/etf_book_pre2020.json prices the same engine on the same file panel
    over three cells: the pre-2020 universe before the boom (A), the same
    universe after it (B), and the published full universe (C).  A-only and
    C-only readers each get one half of the truth; this face carries all three.

    Zero new judgment: no win/loss claim, no threshold.  Numbers are quoted
    from that face and its own `generated` / `evidence_cutoff` are carried --
    this page runs AFTER it on the chain, so a later rewrite would otherwise
    leave a silent stale stamp here (r1781 family).
    """
    d = _read_json(ETF_BOOK_PRE2020)
    rel = "results/etf_book_pre2020.json"
    if not d:
        return {"present": False, "path": rel,
                "note": "分期间面未产出（缺面不读 0）"}
    cells = d.get("cells") or {}

    def _span(key):
        c = cells.get(key) or {}
        rows = c.get("cells") or {}
        vals = [float(r["excess_cagr_pp"]) for r in rows.values()
                if isinstance(r, dict) and r.get("excess_cagr_pp") is not None]
        if not vals:
            return None
        return {"cell": key,
                "universe_size": c.get("universe_size"),
                "start": c.get("start"), "end": c.get("end"),
                "n_cells": len(vals),
                "worst_pp": round(min(vals), 2),
                "best_pp": round(max(vals), 2),
                "all_negative": all(v < 0 for v in vals),
                "all_positive": all(v > 0 for v in vals)}

    a = _span("A_pre_universe_pre_period")
    b = _span("B_pre_universe_post_period")
    c = _span("C_full_universe_post_period")
    if not (a or b or c):
        return {"present": False, "path": rel,
                "note": "分期间面在册但无超额读数（不印 0）"}
    return {"present": True, "path": rel,
            "generated": d.get("generated"),
            "cutoff": d.get("evidence_cutoff"),
            "pre": a, "same_universe_post": b, "full_post": c}


def _carry_book_face():
    """v2.2: what it costs to open the index-futures carry book (pure readout).

    Every number is quoted from results/idx_fut_carry_open_capital.json, which
    itself only quotes the sizing ruler -- no second engine, no re-derivation.
    Three rules that keep this honest:

    * a missing face prints nothing numeric.  "0 lots" must never be how a page
      says "I could not read the book" (r98: unknown is not zero);
    * the section carries the source's own `generated` / `evidence_cutoff`.
      This page runs AFTER that face on the chain, so a face rewritten later
      leaves an older stamp here -- printed rather than silently averaged in
      (r1781);
    * the withdrawal touched the executable ticket only.  The forward paper
      series is printed as kept and re-labelled, never as erased, and the desk
      ticket keeps its lots as a counterfactual.
    """
    d = _read_json(CARRY_OPEN_JSON)
    if not d:
        return {"present": False, "path": CARRY_OPEN_REL,
                "note": "资金线面未产出（缺面不读 0）"}
    accts = d.get("accounts") or {}
    if not accts:
        return {"present": False, "path": CARRY_OPEN_REL,
                "note": "资金线面在册但零账户（不完整面不冒充）"}
    rows = {}
    for code, a in sorted(accts.items()):
        ruler = a.get("ruler") or {}
        fund = a.get("funding") or {}
        ticket = a.get("desk_ticket") or {}
        ex = a.get("executable_ticket") or {}
        fwd = a.get("forward_paper") or {}
        rows[code] = {
            "capital_cny": a.get("capital_cny"),
            "target_pct": a.get("target_pct"),
            "lots": ruler.get("admissible_lots"),
            "ruler_state": ruler.get("state"),
            "executable_lots": ex.get("lots"),
            "executable_state": ex.get("state"),
            "withdrawn_lots": ex.get("withdrawn_lots"),
            "first_rung_cny": fund.get("first_rung_cny"),
            "gap_cny": fund.get("gap_cny"),
            "gap_pct": fund.get("gap_pct_of_capital"),
            "desk_lots": ticket.get("lots"),
            "desk_multiple": ticket.get("multiple_of_budget"),
            "paper_lots": fwd.get("lots_in_ledger"),
            "paper_label": fwd.get("label"),
        }
    book = d.get("book") or {}
    wd = d.get("withdrawal") or {}
    labels = {r.get("paper_label") for r in rows.values()} - {None}
    return {
        "present": True,
        "path": CARRY_OPEN_REL,
        "arm": d.get("arm_used_for_decision"),
        "accounts": rows,
        "paper_label": sorted(labels)[0] if len(labels) == 1 else None,
        "executable_lots_total": book.get("executable_lots_total"),
        "withdrawn_lots_total": book.get("withdrawn_lots_total"),
        "paper_lots_total": book.get("forward_paper_lots_total"),
        "funding_all_cny": book.get("funding_for_all_legs_cny"),
        "cheapest_product": (book.get("cheapest_to_open") or {}).get("product"),
        "cheapest_cny": (book.get("cheapest_to_open") or {}).get("funding_cny"),
        "decision": wd.get("decision"),
        "decided": wd.get("decided"),
        "decided_in": wd.get("decided_in"),
        "scope": wd.get("scope"),
        "reversal": wd.get("reversal"),
        "sentence": d.get("sentence"),
        "source_generated": d.get("generated"),
        "evidence_cutoff": d.get("evidence_cutoff"),
        "source_face": d.get("source_face"),
        "ladder_face": d.get("ladder_source_face"),
    }


def _carry_timing_face():
    """v2.3 r1787: is today a day the entry rule wants the lot at all?

    The capital line (⑦) answers "how much money does the first lot need".  The
    timing face answers the other half of the same decision: the rule that survived
    its own test (`verdict.verdict == "RULE"`) says *enter only when the discount
    sits in the widest fifth of its trailing year*.  A page that prints only the
    money invites the reader to fund the book on a day the rule says to wait.

    Three rules, same as the section above:
      * a missing face prints no number at all -- "not in the band" must never be
        how the page says "I could not read the rule" (r98);
      * the band edge is derived from the face's own quintile ladder, never typed
        from memory;
      * the direction is spelled out.  A WIDER discount is a LOWER percentile --
        the name says "percentile" and the number goes the other way, which is
        exactly the kind of label that gets read backwards (r1234).
    """
    d = _read_json(CARRY_TIMING_JSON)
    if not d:
        return {"present": False, "path": CARRY_TIMING_REL,
                "note": "择时面未产出（缺面不读 0）"}
    v = d.get("verdict") or {}
    pairs = d.get("pairs") or {}
    if not pairs or not v.get("verdict"):
        return {"present": False, "path": CARRY_TIMING_REL,
                "note": "择时面在册但无判决（不完整面不冒充）"}
    # the band edge comes off the quintile ladder the producer published
    edge = None
    for code, e in pairs.items():
        qs = e.get("quintiles") or []
        if len(qs) >= 2 and qs[0].get("quintile") is not None:
            edge = qs[1].get("quintile")
            break
    rows = {}
    for code, e in sorted(pairs.items()):
        lt = e.get("latest") or {}
        rows[code] = {
            "basis_pct": lt.get("basis_pct"),
            "percentile": lt.get("percentile"),
            "in_band": lt.get("in_widest_quintile"),
            "passes_rule": (e.get("verdict") == "RULE"),
        }
    cut = None
    for e in pairs.values():
        cut = (e.get("window") or {}).get("to")
        if cut:
            break
    return {
        "present": True,
        "path": CARRY_TIMING_REL,
        "verdict": v.get("verdict"),
        "kind": v.get("kind"),
        "rule": v.get("rule"),
        "passing_pairs": v.get("passing_pairs") or [],
        "percentile_adds_over_level_pairs": v.get("percentile_adds_over_level_pairs") or [],
        "ratio": v.get("median_fwd_to_basis_change_ratio"),
        "band_edge_pct": edge,
        "accounts": rows,
        "evidence_cutoff": cut,
        "source_generated": d.get("generated"),
    }


def _carry_margin_face():
    """v2.4 r1819: which constraint actually sets the lot -- the risk dial or the broker.

    Section ⑦ prints two halves of one decision (how much cash the first lot needs, and
    whether today's discount is inside the entry band) and both of them assume the 8% vol
    ruler is the only constraint.  It is not the only one: a 200-CNY-per-point contract
    carries ~1.24M of notional, so a broker's 12-15% initial margin is 149k-186k of the
    same account's cash.  If margin were binding, every number above it would be the wrong
    rung -- this block is the check, on the same page, next to the number it could overturn.

    Three rules, same family as the two blocks above:
      * a missing face prints no number at all (r98: unknown is not zero);
      * the sweep is labelled as a RULE PARAMETER, because the margin rate is an exchange
        rule plus a broker add-on -- never a measurement of this book;
      * the reader is told which arm wins and by how much, because "margin does not bind"
        is only useful when the size of the gap is printed beside it.
    """
    d = _read_json(CARRY_MARGIN_JSON)
    if not d:
        return {"present": False, "path": CARRY_MARGIN_REL,
                "note": "保证金面未产出（缺面不读 0）"}
    v = d.get("verdict") or {}
    products = d.get("products") or {}
    if not products or not v.get("verdict"):
        return {"present": False, "path": CARRY_MARGIN_REL,
                "note": "保证金面在册但无判词（不完整面不冒充）"}
    rows = {}
    for code, p in sorted(products.items()):
        if p.get("status") != "ok":
            continue
        at14 = (p.get("margin_sweep") or {}).get("14") or {}
        rows[code] = {
            "notional_cny": p.get("notional_per_lot_cny"),
            "vol_rung_cny": p.get("vol_ruler_first_rung_cny"),
            "margin_rung_cny": at14.get("capital_the_margin_arm_needs_cny"),
            "initial_margin_cny": at14.get("initial_margin_cny"),
            "call_trigger_pct": at14.get("call_trigger_pct"),
            "breakeven_rate_pct": p.get("breakeven_margin_rate_pct"),
            "worst_intraday_pct": (p.get("adverse") or {}).get("worst_intraday_pct"),
            "worst_intraday_date": (p.get("adverse") or {}).get("worst_intraday_date"),
            "gate": p.get("gate"),
        }
    return {
        "present": True,
        "path": CARRY_MARGIN_REL,
        "verdict": v.get("verdict"),
        "sentence": v.get("sentence"),
        "gates": v.get("gates") or {},
        "breakeven_rate_pct": v.get("breakeven_margin_rate_pct") or {},
        "ruler_gap": v.get("ruler_gap_vol_over_margin_at_14pct") or {},
        "accounts": rows,
        "rates_swept_pct": d.get("margin_rates_swept_pct") or [],
        "evidence_cutoff": d.get("evidence_cutoff"),
        "source_generated": d.get("generated"),
    }


def _carry_roll_cost_face():
    """r1820: the roll is the third thing that eats this sleeve, and it was unpriced.

    Sections ⑦ and ⑧ answer "how much money to open" and "is today's discount wide
    enough"; both, and the desk sheet behind them, charge a roll at the exchange
    document floor of 1.5bp.  `idx_fut_roll_cost` now measures that seam from each
    contract's own daily high/low (Corwin-Schultz, one-bar lag) and the median is
    19.8-30.8bp -- an order of magnitude above the floor.  At 5-11 rolls a year that
    is 1.5-2.4pp/yr of carry, which is the same order as the whole gap between this
    sleeve and the book.

    Rules, same family as the blocks above:
      * two calibers side by side (floor and measured), never one blended number --
        neither end is a quote, and the measured end saturates on the day's range;
      * the drag is quoted from the producer, with its generation stamp;
      * a missing face prints no number (r98: unknown is not zero).
    """
    d = _read_json(CARRY_RISK_JSON)
    if not d:
        return {"present": False, "path": CARRY_RISK_REL,
                "note": "换月成本面未产出（缺面不读 0）"}
    products = d.get("products") or {}
    if not products:
        return {"present": False, "path": CARRY_RISK_REL,
                "note": "换月成本面在册但无产品行（不完整面不冒充）"}
    rows = {}
    for code, p in sorted(products.items()):
        ex = p.get("execution") or {}
        band = ex.get("roll_cost_bp") or {}
        drag = ex.get("roll_cost_drag_pp_per_year") or {}
        gap = ex.get("gap_after_roll_cost_pp") or {}
        if band.get("median_bp") is None:
            continue
        rows[code] = {
            "median_bp": band.get("median_bp"),
            "floor_bp": band.get("floor_bp"),
            "rolls": p.get("rolls"),
            "drag_floor_pp": drag.get("file_floor"),
            "drag_measured_pp": drag.get("measured_median"),
            "gap_floor_pp": gap.get("file_floor"),
            "gap_measured_pp": gap.get("measured_median"),
        }
    if not rows:
        return {"present": False, "path": CARRY_RISK_REL,
                "note": "换月成本面无可读行（不完整面不冒充）"}
    return {
        "present": True,
        "path": CARRY_RISK_REL,
        "rows": rows,
        "evidence_cutoff": d.get("evidence_cutoff"),
        "source_generated": d.get("generated"),
    }


def _carry_marks_face():
    """r1845: are the bars under the carry P&L still on the contract panel?

    The book is append-only and the page prints its NAV, so the one thing the page
    cannot currently tell the reader is whether the last bar still has a quote behind
    it.  `futures_book_marks` answers that and is quoted here verbatim: the verdict,
    the unbacked bars (date / contract / close), what each one is (a close equal to
    the main-continuous close of that day, or a number no panel produces), and the
    CNY sitting on them.  A missing face prints a reason and NO number (r98).
    """
    d = _read_json(CARRY_MARKS_JSON)
    if not d:
        return {"present": False, "path": CARRY_MARKS_REL,
                "note": "账面报价支撑面未产出（缺面不读 0）"}
    products = d.get("products") or {}
    if not products:
        return {"present": False, "path": CARRY_MARKS_REL,
                "note": "支撑面在册但无产品行（不完整面不冒充）"}
    rows = {}
    for code, p in sorted(products.items()):
        rows[code] = {
            "state": p.get("state"),
            "contract": p.get("account_contract"),
            "last": p.get("last"),
            "panel_last": p.get("panel_last_quote"),
            "unbacked": p.get("unbacked") or [],
            "unbacked_n": p.get("unbacked_n") or 0,
        }
    return {
        "present": True,
        "path": CARRY_MARKS_REL,
        "verdict": d.get("verdict"),
        "rows": rows,
        "totals": d.get("totals") or {},
        "evidence_cutoff": d.get("evidence_cutoff"),
        "source_generated": d.get("generated"),
    }


# r1785: the sheet below is a full build; the reader who already followed the
# page needs the DIFFERENCE.  The producer (etf_book_exec_delta) has printed
# that difference since r1563 and nothing on the page ever showed it, so
# "follow the page" meant buying the whole book again at every hand-off.  Two
# rules:
#
#   * ALREADY_ON_TARGET is a real zero (nothing to do today) while a missing or
#     unpriced face is NOT -- the two must never print the same sentence (r98);
#   * the account row and the sheet are priced on different bars, so the
#     carry-leg mark is printed beside the cash chain instead of folded into it
#     (r1563: the producer keeps them apart, this page keeps them apart).
_ETF_DELTA_VERDICTS = {
    "ALREADY_ON_TARGET": "已到目标：今天没有动作",
    "SHEET_IMPLIES_A_SWAP": "换仓：一部分卖出、一部分买入",
    "BUY_ONLY": "只买不卖",
    "SELL_DOWN_ONLY": "只减不加",
    "CASH_SHORT": "卖出回笼不够买：现金会变成负数，这张差量单不能执行",
    "UNPRICED": "有票读不到价：差量算不出",
}


def _etf_delta_face(t):
    """The published sell/buy rows, read straight from the ticket's face."""
    d = (t or {}).get("exec_delta") or {}
    if not d:
        return {"present": False, "note": "换仓差量面未产出（缺面不读 0 手）"}
    rows = []
    for r in d.get("rows") or []:
        rows.append({
            "symbol": str(r.get("symbol") or ""),
            "price": r.get("price"),
            "current_lots": r.get("current_lots"),
            "target_lots": r.get("target_lots"),
            "delta_lots": r.get("delta_lots"),
            "side": str(r.get("side") or ""),
            "amount_cny": r.get("amount_cny"),
        })
    verdict = str(d.get("verdict") or "")
    mark = d.get("mark") or {}
    decl = d.get("declaration") or {}
    return {
        "present": True,
        "verdict": verdict,
        "verdict_cn": _ETF_DELTA_VERDICTS.get(
            verdict, "判定面出现未登记状态：按不可读处理"),
        "no_action": verdict == "ALREADY_ON_TARGET",
        "executable": verdict in {"SHEET_IMPLIES_A_SWAP", "BUY_ONLY",
                                  "SELL_DOWN_ONLY"},
        "rows": rows,
        "sells": [r for r in rows if r["side"] == "SELL"],
        "buys": [r for r in rows if r["side"] == "BUY"],
        "gross_sell_cny": d.get("gross_sell_cny"),
        "gross_buy_cny": d.get("gross_buy_cny"),
        "turnover_cny": d.get("turnover_cny"),
        "net_cash_cny": d.get("net_cash_cny"),
        "cash_before_cny": d.get("cash_before_cny"),
        "cash_after_cny": d.get("cash_after_cny"),
        "turnover_share_pct": d.get("turnover_share_of_book_pct"),
        "current_bar": d.get("current_bar"),
        "current_rows": d.get("current_rows"),
        "target_rows": d.get("target_rows"),
        "mark_cny": mark.get("drift_cny"),
        "mark_account_bar": mark.get("account_bar"),
        "declaration_status": str(decl.get("status") or ""),
        "declaration_bar": decl.get("bar"),
        "declaration_actions": decl.get("actions"),
        "positions_source": d.get("positions_source"),
    }


# r1786: the sheet spends 43.2% of the 1,000,000 and the page prints "留现金
# ¥568,272" -- but nothing said what that cash DOES.  The ticket face has priced
# it against the repo market since it landed (spot / 250-day mean / full-window
# mean, each already net of a fall haircut) and no reader page ever quoted it, so
# "half the book is cash" read as either dead money or as a return the book was
# already banking.
#
# The trap in one sentence: the forward ledger's own config says the cash leg
# earns 0.  So this is a RATE ON CASH, not money already made, and it must never
# be folded into the +0.681% printed above it.  Both sentences print or neither
# does.
_ETF_CASH_BANDS = (("spot", "最近一笔"), ("mean_tail", "250 日均"),
                   ("window", "有记录以来"))


def _etf_cash_leg_face(cl):
    """What the cash left on the sheet earns, quoted from the ticket face."""
    cl = cl or {}
    money = cl.get("money") or {}
    if not money:
        return None
    bands = {}
    for key, label in _ETF_CASH_BANDS:
        b = money.get(key) or {}
        if b.get("pct") is None:
            continue
        bands[key] = {
            "label": label,
            "pct": b.get("pct"),
            "net_pct": b.get("net_pct"),
            "net_annual_cny": b.get("net_annual_cny"),
            "as_of": b.get("date"),
            "quotes": b.get("quotes"),
        }
    if not bands:
        return None
    return {
        "source": cl.get("source"),
        "cash_cny": money.get("cash_amount_cny"),
        "fall_bp": money.get("fall_bp"),
        "bands": bands,
        "headline": "spot" if "spot" in bands else sorted(bands)[0],
        "tail": money.get("tail"),
        "verdict": money.get("verdict"),
        "window_years": (cl.get("accrual_window") or {}).get("years"),
        "missing_bar_steps": cl.get("missing_bar_steps"),
    }


def _etf_order_with_cash_roll():
    """The order face plus today's repo-roll instruction, guarded on the ticket's own bar."""
    eo = _etf_order_face() or {}
    eo["cash_roll"] = _etf_cash_roll_face(eo.get("bar"))
    return eo


def _etf_cash_roll_face(ticket_bar=None, decision_date=None):
    """v2.5 (r1824): which repo tenor the sleeve rolls into TODAY.

    The cash row prices the sleeve at the 1-day rate and stops there. The reader's next
    question is a tenor, and the ladder face cannot answer it: its ticket says "roll GC001
    on the first bar at/after 2026-10-27". `etf_book_cash_roll_today` answers it and adds
    the constraint the ladder face never carried -- the cash has to be raisable on the
    decision bar, so a high coupon that matures past it is excluded, not ranked.

    Three rules, each with a selftest leg:

    * a missing face, or one that names no tenor, prints a reason and NO number (r98);
    * the block prints the face's own as_of and decision date, and refuses to speak when
      they disagree with the ticket it sits under (r1780/r1781: two files agreeing by luck
      is not a guard);
    * the worth line is "versus rolling 1-day every session", never a forecast.
    """
    d = _read_json(ETF_CASH_ROLL_JSON)
    if not d:
        return {"present": False, "note": "闲钱滚仓面未产出（缺面不读 0）"}
    verdict = d.get("verdict")
    if not verdict:
        return {"present": False, "note": "闲钱滚仓面无判词（空面不冒充有读数）"}
    if verdict == "NO_INSTRUCTION":
        return {"present": True, "verdict": verdict,
                "reason": d.get("reason") or "面上没写原因",
                "as_of": d.get("as_of"), "decision_date": d.get("decision_date")}
    if ticket_bar and d.get("as_of") and d["as_of"] != ticket_bar:
        return {"present": False, "verdict": verdict, "as_of": d.get("as_of"),
                "ticket_bar": ticket_bar,
                "note": "滚仓面读的是 {}，这张票面读的是 {}——不是同一趟，今天不印这个数"
                        .format(d.get("as_of"), ticket_bar)}
    if decision_date and d.get("decision_date") and d["decision_date"] != decision_date:
        return {"present": False, "verdict": verdict,
                "as_of": d.get("as_of"), "decision_date": d.get("decision_date"),
                "ticket_decision_date": decision_date,
                "note": "滚仓面说下一次决策是 {}，票面说 {}——两个日期不一致，今天不印这个数"
                        .format(d.get("decision_date"), decision_date)}
    best = d.get("best_sh") or d.get("best_sz") or {}
    excl = d.get("excluded_locked") or []
    return {
        "present": True,
        "verdict": verdict,
        "as_of": d.get("as_of"),
        "decision_date": d.get("decision_date"),
        "window_days": d.get("window_days"),
        "cash_cny": d.get("cash_cny"),
        "contract": best.get("contract"),
        "tenor_days": best.get("tenor_days"),
        "net_ann_pct": best.get("net_ann_pct"),
        "quoted_pct": best.get("quoted_pct"),
        "matures": best.get("matures"),
        "placeable": d.get("placeable") or {},
        "worth_year_cny": d.get("worth_vs_daily_roll_cny_year"),
        "worth_window_cny": d.get("worth_vs_daily_roll_cny_window"),
        "locked_out": [{"contract": r.get("contract"), "quoted_pct": r.get("quoted_pct"),
                        "matures": r.get("matures"),
                        "late_days": r.get("locked_past_decision_days")} for r in excl[:3]],
        "sentence": d.get("sentence"),
        "source_rel": ETF_CASH_ROLL_REL,
    }


def _etf_premium_face():
    """v2.4 (r1820): what part of the build order is paid ABOVE NAV.

    ⑥ tells the reader which five codes to buy and at what price; nothing on the
    page said that one of those prices carries a premium.  The producer has published
    the number for weeks (etf_book_premium_leak: the ticket pays 1.21% over IOPV, and
    159655 alone carries 7.5% at the 98.8th percentile of its own year) -- it simply
    never reached the reader's page.  That is the r1782 shape: research-readable is
    not reader-readable.

    Read-only, three rules:

    * a missing face prints a reason and NO number (r98: an unread premium is not 0);
    * the block names the ticket it priced and its own two sessions, because this
      face is written by another script on its own trip (r1781);
    * the percentile is each fund's OWN year -- "7.5% premium" means something
      different at the 20th and the 99th percentile of the same fund, so both are
      printed, and the stress rows say reversion, not forecast.
    """
    d = _read_json(ETF_PREMIUM_JSON)
    if not d:
        return {"present": False, "note": "溢价面未产出（缺面不读 0）"}
    totals = d.get("totals") or {}
    names = d.get("names") or []
    if not names:
        return {"present": False, "note": "溢价面零行（空面不冒充有读数）"}
    rows = []
    for n in names:
        rows.append({
            "symbol": str(n.get("symbol") or ""),
            "premium_pct": n.get("premium_pct"),
            "premium_paid_cny": n.get("premium_paid_cny"),
            "market_pctile": n.get("market_pctile"),
            "status": n.get("status"),
        })
    own = d.get("own_ruler_summary") or {}
    return {
        "present": True,
        "verdict": d.get("verdict"),
        "verdict_reason": d.get("verdict_reason"),
        "ticket": d.get("ticket"),
        "ticket_session": d.get("ticket_session"),
        "iopv_session": d.get("iopv_session"),
        "session_match": d.get("session_match"),
        "premium_paid_cny": totals.get("premium_paid_cny"),
        "premium_share_of_order_pct": totals.get("premium_share_of_order_pct"),
        "premium_share_of_nav_pct": totals.get("premium_share_of_nav_pct"),
        "verified_amount_cny": totals.get("verified_amount_cny"),
        "n_verified": totals.get("n_verified"),
        "n_unverifiable": totals.get("n_unverifiable"),
        "book_cagr_pct": totals.get("book_cagr_pct"),
        "years_of_backtest_return_paid": totals.get("years_of_backtest_return_paid"),
        "rows": rows,
        "stress": d.get("stress") or {},
        "own_top_decile_pctile": own.get("top_decile_pctile"),
        "own_in_top_decile": own.get("in_own_top_decile") or [],
        "own_verdict": own.get("verdict"),
        "own_revert_cny": own.get("revert_to_own_median_cny"),
        "own_revert_note": own.get("revert_note"),
    }


def _etf_premium_choice_face():
    """r1835: the premium block names the expensive leg and stops there.

    It prints "159655 多付 ¥6,039｜98.8 分位｜在它自己历史的前 10% 高位" and then
    says nothing about the one thing a reader would ask next: buy a different,
    cheaper fund instead?  The answer exists (etf_book_premium_choice, r1775) and
    is priced two ways -- a one-off CNY saving at the order versus a give-up in
    expected return per window -- and the two rulers disagree.  A page that only
    prints the premium invites the reader to invent the swap himself.

    Read-only.  The block keeps the currencies apart (one-off CNY / CNY per window
    / pp per year are never summed) and prints the convergence threshold as a
    THRESHOLD, not as a probability: a single session snapshot cannot measure
    whether the premium gap closes before exit.
    """
    d = _read_json(ETF_PREMIUM_CHOICE_JSON)
    if not d:
        return {"present": False, "note": "换腿面未产出（缺面不读 0）"}
    legs = d.get("legs") or []
    if not legs:
        return {"present": False, "note": "换腿面零行（空面不冒充有读数）"}
    stretched = []
    for leg in legs:
        if not leg.get("stretched"):
            continue
        roads = {r.get("road"): r for r in (leg.get("roads") or [])}
        b = roads.get("B_same_market_twin") or {}
        twin = b.get("twin") or {}
        stretched.append({
            "symbol": leg.get("symbol"),
            "premium_pct": leg.get("premium_pct"),
            "premium_cny": leg.get("premium_cny"),
            "leg_score": leg.get("leg_score"),
            "verdict": leg.get("verdict"),
            "twin": twin.get("symbol"),
            "twin_premium_pct": twin.get("premium_pct"),
            "twin_score_gap": twin.get("score_gap"),
            "saving_cny_once": b.get("saving_cny_once"),
            "giveup_cny_per_window": b.get("giveup_cny_per_window"),
            "giveup_pp_per_year": b.get("giveup_pp_per_year"),
            "breakeven_convergence_p": b.get("breakeven_convergence_p"),
            "breakeven_tenure_windows": b.get("breakeven_tenure_windows"),
            "breakeven_tenure_years": b.get("breakeven_tenure_years"),
            "drop_to_cash_saving_cny": (roads.get("C_drop_to_cash") or {}).get(
                "saving_cny_once"),
        })
    crit = d.get("criteria") or {}
    tenure = d.get("seat_tenure") or {}
    totals = d.get("totals") or {}
    return {
        "present": True,
        "verdict": d.get("verdict"),
        "ticket": d.get("ticket"),
        "as_of": d.get("as_of"),
        "threshold_pp": crit.get("premium_swap_pp"),
        "annual_giveup_cap_pp": crit.get("max_giveup_pp_per_year_annual_ruler"),
        "stretched": stretched,
        "n_stretched": len(stretched),
        "mean_tenure_windows": tenure.get("mean_tenure_decisions"),
        "median_tenure_windows": tenure.get("median_tenure_decisions"),
        "share_one_window": tenure.get("share_held_one_window"),
        "best_saving_cny": totals.get("best_saving_cny"),
        "best_giveup_cny_per_window": totals.get("best_giveup_cny_per_window"),
    }


def _next_decision_face(t):
    """r1825: "16 bars away" is not a date.

    The sheet has carried `next_decision_bars` since r1786 and this page prints
    it, while the cash-roll block one line below hard-excludes any tenor that
    matures after **2026-12-09** -- the same day, on the same page, in two
    different currencies of language.  The sheet already answers in dates: its
    own `next_decision` face signs the bar three independent ways (production
    sheet, cut permission, swap units) against the official calendar.

    Read that face instead of converting bars here (a second implementation of
    the grid is exactly what r1822/r1823 spent two rounds removing).  Three
    rules:

    * missing face -> print the reason, never a computed guess (r98);
    * its own signatures disagreeing (`wrong_claims`/`off_grid_claims`) -> print
      the disagreeing names and NO date, rather than electing one (r1745 family);
    * a date that contradicts the ticket's own bar count -> print neither.
    """
    nd = t.get("next_decision") or {}
    if not nd:
        return {"present": False, "note": "票面未带下次决策面（缺面不读 0）"}
    grid = nd.get("grid") or {}
    return {
        "present": True,
        "date": grid.get("next_bar"),
        "bars_away": grid.get("bars_away"),
        "rebal": grid.get("rebal"),
        "anchor_bar": grid.get("anchor_bar"),
        "anchor_source": grid.get("anchor_source"),
        "calendar_source": nd.get("calendar_source"),
        "calendar_last": nd.get("calendar_last"),
        "verdict": nd.get("verdict"),
        "sentence": nd.get("sentence"),
        "n_claims": len(nd.get("claims") or []),
        "wrong_claims": [c.get("name") for c in (nd.get("wrong_claims") or [])],
        "off_grid_claims": [c.get("name") for c in
                            (nd.get("off_grid_claims") or [])],
        "agrees": nd.get("verdict") == "AGREE",
    }


def _etf_capacity_face():
    """r1826: how much of the market's turnover this order is.

    ⑥ names five codes, their lots and their cash, and says nothing about whether that
    size fits through the market.  results/etf_book_capacity_edge.json has measured it
    for weeks against the 1% ADV line -- and the reader's page never carried a word.

    Read-only, and the one thing this block must NOT do is scale the reading by hand.
    The face measured the 1,000,000 lens (five names, 200,000 each), not the 43%-sized
    ticket the desk is holding today, so quoting "0 of 60 sessions pass" beside today's
    order would read as "today's order breaches" -- a number nobody measured (r98
    family: an unread reading is not a reading).  The block therefore prints the lens
    it was measured at, the reader's own book weight beside it, and says the face was
    not re-measured at this size.

    * missing / reading-less face -> a reason, never 0 ("there is room" must be earned);
    * a face whose own session is not the ticket's bar -> say so, print no number
      (r1781 family: a section fed by another trip self-stamps or it lies);
    * the 1% line is the gate's own choice, quoted as such (caveat carried verbatim).
    """
    d = _read_json(ETF_CAPACITY_JSON)
    if not d:
        return {"present": False, "note": "容量面未产出（缺面不读 0）"}
    s = d.get("summary") or {}
    if s.get("reading_today_pct") is None:
        return {"present": False, "note": "容量面上没有读数（空面不冒充有空间）"}
    pub = d.get("published") or {}
    crit = d.get("criteria") or {}
    return {
        "present": True,
        "session": d.get("session"),
        "evidence_cutoff": d.get("evidence_cutoff"),
        "verdict": s.get("verdict"),
        "line_pct": s.get("line_pct", crit.get("line_pct")),
        "lens_cny": s.get("lens_cny", crit.get("lens_cny")),
        "lens_tag": crit.get("lens_tag"),
        "per_name_cny": pub.get("per_name_cny"),
        "reading_today_pct": s.get("reading_today_pct"),
        "binding_today": s.get("binding_today"),
        "n_sessions": s.get("n_sessions"),
        "n_passes": s.get("n_passes"),
        "n_unmeasurable": s.get("n_unmeasurable"),
        "capital_at_line_cny": s.get("capital_where_at_line_today_cny"),
        "capital_median_cny": s.get("capital_median_cny"),
        "capital_min_cny": s.get("capital_min_cny"),
        "gap_to_lens_cny": s.get("gap_to_lens_cny"),
        "sentence": d.get("sentence"),
        "caveats": d.get("caveats") or [],
    }


def _etf_capacity_at_size_face():
    """r1827: the same capacity question, asked of THIS ticket's names and amounts.

    r1826 printed the reading the capacity face had measured and said, correctly, that
    today's order was never measured at its own size -- the face's five names are not the
    ticket's five (only 1 of 5 overlapped on 2026-11-17).  A page that answers "may I size
    this order" with a number about another five names is the r1782 shape: the face is
    readable, the reader's question is not answered.

    `results/etf_book_capacity_at_size.json` measures exactly that (the ADV ruler is
    imported from the capacity face, never re-derived).  Read-only here, and the block
    keeps the one distinction that matters:

    * the measured verdict is quoted, never recomputed on this page (r1826 rule);
    * when the two faces are about different name sets the page prints BOTH and says they
      are different books -- it does not put them side by side as if one confirmed the
      other (E685 family: a number and its ruler travel together);
    * no face / no reading / an order priced on another bar -> a reason, never 0 and never
      "there is room" (r98).
    """
    d = _read_json(ETF_CAPACITY_SIZE_JSON)
    if not d:
        return {"present": False, "note": "同规模容量面未产出（缺面不读 0）"}
    s = d.get("summary") or {}
    if s.get("reading_pct") is None:
        return {"present": False,
                "note": d.get("sentence") or "同规模容量面没有读数（不冒充有空间）"}
    return {
        "present": True,
        "verdict": d.get("verdict"),
        "reading_pct": s.get("reading_pct"),
        "binding": s.get("binding"),
        "line_pct": s.get("line_pct"),
        "spent_cny": s.get("spent_cny"),
        "headroom_cny": s.get("headroom_cny_at_line"),
        "headroom_multiple": s.get("headroom_multiple"),
        "n_names": s.get("n_names"),
        "n_measurable": s.get("n_measurable"),
        "unmeasurable": s.get("unmeasurable") or [],
        "bar": d.get("bar"),
        "panel_bar": d.get("panel_bar"),
        "ticket_file": d.get("ticket_file"),
        "name_set": d.get("name_set") or {},
        "sentence": d.get("sentence"),
        "caveats": d.get("caveats") or [],
    }


def _etf_open_gap_face():
    """r1829: how far the next open sits from the close this sheet is priced at.

    ⑥ prices every line at the decision bar's close and the sheet is filled at the next
    open; the page's caveat admitted that ("开盘成交价会不同") and never put a number on
    it.  `results/etf_book_open_gap.py` measures the overnight gap on the ticket's own
    five names and converts the band to CNY on the ticket's own amount.

    Read-only, and the block keeps the three distinctions that make the number honest:

    * a gap is a price level, not a cost -- it moves `k` by the same percentage and is
      paid to nobody, so it may never be added to the commission line;
    * the median and the band are two readings (a typical session vs the middle 60%),
      both printed, never averaged into one "expected slippage" number;
    * the face's cutoff must be the ticket's bar -- another bar's distribution is
      another book (r1781/E685 family), and a missing face is a reason, never 0 (r98).
    """
    d = _read_json(ETF_OPEN_GAP_JSON)
    if not d:
        return {"present": False, "note": "开盘间隔面未产出（缺面不读 0）"}
    recent = (d.get("pooled") or {}).get("recent") or {}
    if recent.get("median_bp") is None:
        return {"present": False,
                "note": d.get("sentence") or "开盘间隔面上没有读数（不冒充量过）"}
    return {
        "present": True,
        "verdict": d.get("verdict"),
        "evidence_cutoff": d.get("evidence_cutoff"),
        "ticket": d.get("ticket"),
        "n_names": d.get("n_names"),
        "traded_amount_cny": d.get("traded_amount_cny"),
        "recent_sessions": d.get("recent_sessions"),
        "recent": recent,
        "all_history": (d.get("pooled") or {}).get("all_history") or {},
        "money": d.get("money") or {},
        "band_ratio_vs_fee": d.get("band_ratio_vs_fee"),
        "fee_double_sided_cny": d.get("fee_double_sided_cny"),
        "names": d.get("names") or [],
        "missing": d.get("missing") or [],
        "sentence": d.get("sentence"),
        "caveats": d.get("caveats") or [],
    }


def _etf_punctuality_face():
    """r1828: "do it today, or is waiting cheaper" -- printed for the sheet, not a book.

    ⑥ already tells the reader what to do today (the delta) and when the next scheduled
    decision is.  What it never answered is the question a reader asks while looking at
    the action lines: *is today the cheap day, or does waiting a few sessions cost less?*
    `results/etf_book_do_or_wait.json` has priced exactly that on the panel (a k-bar
    ladder against the ticket's own permission + carry), and r1481 already refused to
    call a single sheet's coin flip a decision.  Read-only here.

    Three rules, all of them shapes this repo has already been burned by:

    * the face's own verdict is quoted, never upgraded -- and NOTHING_OWED_TODAY is a
      first-class answer ("nothing is due"), not a missing number (r98 family);
    * the face's evidence_cutoff must be the ticket's bar, or the block prints the
      mismatch instead of the cost (E685/r1311: a number and its ruler travel together);
    * the mean and the single-sheet coin flip are printed side by side and never
      averaged into one sentence (r1481/E682: the mean is a many-times number).
    """
    d = _read_json(ETF_DO_OR_WAIT_JSON)
    if not d:
        return {"present": False, "note": "时点面未产出（缺面不读 0）"}
    dec = d.get("decision") or {}
    table = dec.get("table") or []
    if not table:
        return {"present": False,
                "note": dec.get("sentence") or "时点面没有阶梯（不冒充测过）"}
    rows = []
    for r in table:
        if r.get("k") in (None, 0):
            continue
        rows.append({"k": r.get("k"),
                     "cost_cny": r.get("cost_cny_vs_today"),
                     "t": r.get("t"),
                     "share_late_helps": r.get("share_late_helps"),
                     "separable": r.get("separable_from_zero")})
    one = dec.get("one_open_late") or {}
    return {
        "present": True,
        "verdict": dec.get("verdict"),
        "best_k": dec.get("best_k"),
        "today_cost_cny": dec.get("today_cost_cny"),
        "trim_owed": dec.get("trim_owed"),
        "rows": rows,
        "one_open_late": {
            "median_cny": one.get("median_cny"),
            "mean_cny": one.get("mean_cny"),
            "t": one.get("t"),
            "share_late_helps": one.get("share_late_helps"),
        },
        "evidence_cutoff": d.get("evidence_cutoff"),
        "capital_cny": d.get("capital_cny"),
        "sentence": dec.get("sentence"),
        "file": ETF_DO_OR_WAIT_REL,
    }


def _etf_order_face():
    """v2.3 (r1784): the executable sheet's own rows, in lots and cash.

    ⑥ has printed the ledger's return since r1580 and the identity line since
    the same round explains that the desk's 5-name sheet is a different book --
    but the sheet itself was still nowhere on the page.  A reader could see the
    book made +0.68% in 17 bars and still not know what "follow this" means on
    his own account (which five codes, how many lots, how much cash stays).

    Read-only.  Three rules:

    * a missing / empty ticket prints a reason, never 0 lots (r98);
    * the page names the decision bar and the producing trip, because the fill
      is the NEXT session's open while the ticket is priced on this bar's close
      (r1771/r1781 day-word family);
    * the list is the target build, not the rebalance delta -- r1785 prints the
      delta as its own block, one line below, labelled for the reader who has
      already followed an earlier sheet; mixing them would print a buy list for
      someone who is already holding the book.
    """
    latest = _read_json(ETF_TICKET_LATEST)
    if not latest:
        return {"present": False, "note": "执行单未产出（缺面不读 0）"}
    fname = latest.get("file")
    t = _read_json(os.path.join(os.path.dirname(ETF_TICKET_LATEST), fname)) \
        if fname else None
    if not t:
        return {"present": False,
                "note": "执行单指针指不到票面（不读 0）"}
    tk = t.get("ticket") or {}
    order = tk.get("order") or []
    if not order:
        return {"present": False,
                "note": "票面零行（空单不冒充有单）"}
    rows = []
    for o in order:
        rows.append({
            "symbol": str(o.get("symbol") or ""),
            "lots": o.get("lots"),
            "shares": o.get("shares"),
            "amount_cny": o.get("amount"),
            "price": o.get("price"),
            "note": o.get("note") or "",
        })
    spent = sum(r["amount_cny"] for r in rows
                if r.get("amount_cny") is not None)
    nav = tk.get("nav")
    return {
        "present": True,
        "file": fname,
        "bar": t.get("as_of") or latest.get("as_of"),
        "decision_bar": t.get("base_bar") or t.get("as_of"),
        "generated": latest.get("generated") or t.get("generated"),
        "rows": rows,
        "n": len(rows),
        "nav_cny": nav,
        "spent_cny": spent,
        "cash_left_cny": None if nav is None else nav - spent,
        "book_weight": tk.get("book_weight"),
        "cash_weight": tk.get("cash_weight"),
        "k_now": latest.get("k_now"),
        "next_decision_bars": t.get("next_decision_bars"),
        # r1825: the same sheet answers "when" in dates, not only in bars.
        "next_decision_face": _next_decision_face(t),
        "book_decided_bar": t.get("book_decided_at"),
        "rebal": t.get("rebal"),
        "cost_bp_per_side": t.get("cost_bp_per_side"),
        # r1786: what the cash row earns, quoted from the same sheet.
        "cash_leg": _etf_cash_leg_face(t.get("cash_leg")),
        # r1785: the same trip also published the rebalance difference; the
        # page prints it as a second, separately labelled reader.
        "delta": _etf_delta_face(t),
    }


# r1580: the two-books face lives in scripts/etf_book_identity.py so this
# page and the daily report read ONE implementation instead of two that drift.
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)
from etf_book_identity import face as _book_identity_face      # noqa: E402
from etf_book_identity import lines as _book_identity_lines    # noqa: E402


# ---------------------------------------------------------------- v2.1 ----
# Freshness (r1281).  Every section already prints its own asof, but nothing on
# the page said HOW OLD those numbers are relative to the market the reader is
# standing in: a NAV for 11-06 sat on a page rendered after 11-09 had closed,
# and the reader had to do the date arithmetic himself.  Three rules:
#
#   * the yardstick is the OFFICIAL exchange calendar, never a panel's own
#     dates (E136: a face must not grade itself);
#   * a face whose cutoff could not be read prints 无法核实, NOT 0 owed
#     (r98: unknown is not "up to date");
#   * the calendar's own last session is printed beside the yardstick, so a
#     calendar that is itself a session behind cannot make the book look
#     fresher than it is.
FRESHNESS_FACES = (
    ("etf_book", "⑥ ETF 复合书"),
    ("risk_tape", "③ 风险带（zt 四面板）"),
    ("market", "① 市场政体态"),
)


def _calendar_yardstick(now=None):
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import exchange_calendar_audit as C
    days = C.load_calendar()
    # the shared reader returns (last_day, past_days); the yardstick is the
    # first element -- unwrap here so callers never juggle the pair locally.
    last, _past = C.expected_last_day(days, now or dt.datetime.now())
    return days, last


def owed_sessions(cutoff, expected, days):
    """Official sessions strictly after `cutoff`, up to and including `expected`.

    None when either side is unknown -- a face we could not read must never be
    printed as "current"."""
    if not cutoff or not expected:
        return None
    if cutoff >= expected:            # on or ahead of the yardstick: no lag
        return 0
    return sum(1 for d in days if cutoff < d <= expected)


def owed_firings(entry, expected, days):
    """Month-start sessions strictly after *entry*, up to *expected*.

    A monthly face is not measured with the daily yardstick: thirty calendar
    days of lag is what this rule looks like when it is perfectly on time.
    What it is owed is one firing per month-start session that has already
    happened since the one it last fired on.  Empty list = on schedule;
    None = one side unknown (never printed as "current")."""
    if not entry or not expected:
        return None
    first_by_month = {}
    for d in days:
        first_by_month.setdefault(d[:7], d)   # days are ascending sessions
    return [d for _k, d in sorted(first_by_month.items())
            if entry < d <= expected]


def _freshness_face(book, tape, market_asof, rec=None, now=None):
    try:
        days, expected = _calendar_yardstick(now)
    except Exception as exc:                                     # noqa: BLE001
        return {"status": "unavailable", "detail": str(exc)[:160],
                "rows": [], "expected_bar": None}
    cutoffs = {"etf_book": (book or {}).get("last_bar"),
               "risk_tape": (tape or {}).get("cutoff"),
               "market": market_asof}
    rows = []
    for key, label in FRESHNESS_FACES:
        c = cutoffs.get(key)
        owed = owed_sessions(c, expected, days)
        rows.append({"face": key, "label": label, "cutoff": c,
                     "owed_sessions": owed,
                     "state": ("unreadable" if owed is None else
                               "current" if owed == 0 else "behind")})
    behind = [r for r in rows if r["state"] == "behind"]
    worst = max(behind, key=lambda r: r["owed_sessions"]) if behind else None
    monthly = []
    if rec and rec.get("present"):
        dues = owed_firings(rec.get("entry_date"), expected, days)
        monthly.append({
            "face": "recommendation",
            "label": "配置参考名单（DIVLOWVOL·月度）",
            "cutoff": rec.get("entry_date"),
            "dues": dues or [],
            "owed_firings": (None if dues is None else len(dues)),
            "state": ("unreadable" if dues is None else
                      "behind" if dues else "current"),
        })
    return {
        "status": "ok",
        "source": "exchange_calendar_audit.load_calendar/expected_last_day",
        "calendar_last": days[-1] if days else None,
        "expected_bar": expected,
        "rows": rows,
        "monthly": monthly,
        "worst_face": worst["label"] if worst else None,
        "worst_owed_sessions": worst["owed_sessions"] if worst else 0,
        "unreadable": [r["label"] for r in rows if r["state"] == "unreadable"],
        "book_panel_last_bar": (book or {}).get("panel_last_bar"),
    }


def _freshness_lines(fr):
    """Rendered banner.  Pure formatting -- every number comes from one place."""
    L = ["## ⓪ 本页新鲜度（先读这个）", ""]
    if fr.get("status") != "ok":
        L.append("- 官方日历读不出（{}）——**本页数字的新旧无法核实**，"
                 "不要当成今日读数。".format(fr.get("detail") or "原因未载"))
        L.append("")
        return L
    L.append("- 参照尺=**官方交易日历**（不是面板自己的日期）：按本页生成时刻算，"
             f"最后必须已有 bar 的会话是 **{fr['expected_bar']}**"
             f"（日历在册最后一日 {fr['calendar_last']}）")
    for r in fr["rows"]:
        if r["state"] == "unreadable":
            tail = "**无法核实**（读不到 cutoff，不按 0 记）"
        elif r["state"] == "current":
            tail = "**同步**"
        else:
            tail = f"**欠 {r['owed_sessions']} 个会话**"
        L.append(f"  - {r['label']}：截至 **{r['cutoff']}** · {tail}")
    if fr.get("book_panel_last_bar"):
        L.append(f"  - 书的定价面板尾 bar：**{fr['book_panel_last_bar']}**"
                 "（书的 bar 不可能比它定价的面板新）")
    for r in fr.get("monthly") or []:
        if r["state"] == "current":
            tail = "**在它的月度节律内**"
        elif r["state"] == "unreadable":
            tail = "**无法核实**（读不到换仓日，不按同步记）"
        else:
            tail = (f"**欠 {r['owed_firings']} 次调仓**"
                    f"（最近该换的是 {r['dues'][0]}·月度网格每根月首交易日一次）")
        L.append(f"  - {r['label']}：上次换仓 {r['cutoff']} · {tail}")
    if fr.get("worst_face"):
        L.append(f"- 结论：本页**不是** {fr['expected_bar']} 收盘后的读数——"
                 f"最旧的一面（{fr['worst_face']}）欠 {fr['worst_owed_sessions']} 个会话。"
                 "书与基准同 cutoff 故超额仍可横比，但任何一格都不能读成 "
                 f"{fr['expected_bar']} 的当日实绩。")
    elif fr.get("unreadable"):
        L.append("- 结论：有面读不到（" + "、".join(fr["unreadable"])
                 + f"），所以**不能说本页已追到 {fr['expected_bar']}**——"
                 "读不到的按「不知道」记，不按「同步」记。")
    else:
        L.append(f"- 结论：全部面都追到 {fr['expected_bar']}，"
                 "本页即该会话收盘后的读数。")
    if fr.get("unreadable"):
        L.append("- 读不到的：" + "、".join(fr["unreadable"]) + "（缺面不读 0）。")
    L.append("")
    return L


DATA_LANE_FACE = os.path.join(ROOT, "results", "data_lane_freshness.json")
# The feed side of ⓪.  The banner above measures the faces this page prints; it
# says nothing about the lanes that feed them, so a collector can be silent for a
# day and a half while the page still reads "全部面都追到 X".  Read-only: every
# field below comes off the lane board, nothing here re-measures a tail.
_LANE_BAD = ("stalled", "behind_1d", "unverifiable")


def _data_lane_face(path=None):
    try:
        d = _read_json(path or DATA_LANE_FACE)
    except Exception as exc:                                     # noqa: BLE001
        return {"status": "unavailable",
                "detail": "results/data_lane_freshness.json 读不到（{}）".format(
                    str(exc)[:80])}
    rows = []
    for r in d.get("lanes") or []:
        if r.get("verdict") == "retired":
            continue
        state = r.get("copy_verdict") or r.get("verdict")
        if state not in _LANE_BAD:
            continue
        rows.append({
            "lane": r.get("lane"),
            "host": r.get("lane_host") or r.get("owner"),
            "host_alive": r.get("host_alive"),
            "host_age_h": r.get("host_age_h"),
            "state": state,
            "tail": r.get("tail"),
            "expected": r.get("expected"),
            "missing_days": r.get("missing_days") or [],
            "loss_mode": r.get("loss_mode"),
            "takeover_capable": bool(r.get("takeover_capable")),
        })
    hosts = {}
    for h, v in (d.get("hosts") or {}).items():
        v = v or {}
        if not v.get("silent"):
            continue
        hosts[h] = {"age_h": v.get("age_h"), "alive": v.get("alive"),
                    "silent_waiting": v.get("silent_waiting") or [],
                    "silent_taken_over": v.get("silent_taken_over") or {}}
    return {"status": "ok", "as_of": d.get("as_of"),
            "verdict": d.get("verdict"), "counts": d.get("counts") or {},
            "n_lanes": d.get("n_lanes"), "machine": d.get("machine"),
            "expected": d.get("expected_last_official_day"),
            "rows": rows, "hosts": hosts}


def _data_lane_lines(dl):
    """Pure formatting over the lane board -- no new judgment, no re-measure."""
    L = ["### ⓪b 数据供给面（上面那些数字是这些采集器喂出来的）", ""]
    if dl.get("status") != "ok":
        L.append("- 车道板读不到（{}）——**不能说数据是新的，"
                 "也不能说它旧**。".format(dl.get("detail") or "原因未载"))
        L.append("")
        return L
    c = dl.get("counts") or {}
    L.append("- 车道板读数（{} 读自 {} 的盘）：**{} 条追平 / {} 条落后 1 天 / "
             "{} 条停滞 / {} 条已退役**，参照日 {}".format(
                 (dl.get("as_of") or "")[:16].replace("T", " "),
                 dl.get("machine") or "本机",
                 c.get("in_sync", 0), c.get("behind_1d", 0),
                 c.get("stalled", 0), c.get("retired", 0),
                 dl.get("expected") or "--"))
    for h, v in sorted(dl.get("hosts", {}).items()):
        wait = "、".join(v.get("silent_waiting") or []) or "--"
        line = "  - 属主 **{}** 静默 {}h，等它的车道：{}".format(
            h, v.get("age_h"), wait)
        taken = v.get("silent_taken_over") or {}
        if taken:
            line += "（已由他机接手：" + "、".join(
                "{}←{}".format(k, w) for k, w in sorted(taken.items())) + "）"
        L.append(line)
    for r in dl.get("rows") or []:
        miss = "、".join((r.get("missing_days") or [])[:4])
        L.append("  - `{}`（属主 {}·尾 {}·欠 {} 个会话{}）".format(
            r.get("lane"), r.get("host") or "--", r.get("tail") or "--",
            len(r.get("missing_days") or []), ("：" + miss) if miss else ""))
        if r.get("loss_mode"):
            L.append("    - 该车道自陈的缺失后果：{}".format(r["loss_mode"]))
    if not dl.get("rows"):
        L.append("- 全部 {} 条数据车道都追平参照日。".format(dl.get("n_lanes") or 0))
    else:
        L.append("- 这一节量的是**采集器**，不是书：书可以是当日收盘价、而喂它的"
                 "一条车道停在两天前——两种「旧」不要互相顶替。")
    L.append("")
    return L


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
    weight_face = None
    if weights:
        others = {k: float(v) for k, v in weights.items() if k not in SIX}
        top_other = (max(others.items(), key=lambda kv: kv[1])
                     if others else None)
        weight_face = {
            "members_total": len(weights),
            "face_sum": round(sum(float(v) for v in weights.values()), 6),
            "six_sum": round(sum(float(weights.get(t, 0.0)) for t in SIX), 6),
            "others_sum": round(sum(others.values()), 6),
            "others_count": sum(1 for v in others.values() if v),
            "top_other": ([top_other[0], round(top_other[1], 6)]
                          if top_other else None),
        }
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
    book = _etf_book_face()
    tape = _risk_tape_face()
    rec_face = _recommendation_face()
    return {
        "schema": "ceo_live_usage_v1_9",
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
        "risk_tape": tape,
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
        "weight_face": weight_face,
        "cap_vs_book": _cap_vs_book_face(regime.get("asof")),
        "rollup": _rollup_face(paper, day),
        "intraday": _intraday_face(held, day),
        "recommendation": rec_face,
        "judgment_burns": _judgment_burn_face(),
        "etf_book": book,
        "etf_book_periods": _etf_book_period_face(),
        "etf_order": _etf_order_with_cash_roll(),
        "etf_premium": _etf_premium_face(),
        "etf_premium_choice": _etf_premium_choice_face(),
        "etf_capacity": _etf_capacity_face(),
        "etf_capacity_at_size": _etf_capacity_at_size_face(),
        "etf_punctuality": _etf_punctuality_face(),
        "etf_open_gap": _etf_open_gap_face(),
        "book_identity": _book_identity_face(),
        "carry_book": _carry_book_face(),
        "carry_timing": _carry_timing_face(),
        "carry_margin": _carry_margin_face(),
        "carry_roll_cost": _carry_roll_cost_face(),
        "carry_marks": _carry_marks_face(),
        "freshness": _freshness_face(book, tape, regime.get("asof"),
                                     rec=rec_face),
        "data_lanes": _data_lane_face(),
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


def _risk_tape_face(root=None):
    """v1.8: today's market risk tape from the four forward zt-pool panels.

    SINGLE IMPLEMENTATION -- this is scripts/daily_report._zt_risk_face, the
    very function that renders section 9 of the daily report.  The one-pager
    must not grow a second copy of the reading rules (r1290 law), and a day
    that was never captured must read as absent rather than as 0 members
    (r1149 law).  Pure aggregation: zero new thresholds, zero new judgment."""
    root = root or ROOT
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import daily_report as _dr
    except Exception as exc:                                     # noqa: BLE001
        return {"status": "unavailable", "detail": str(exc)[:160], "panels": {}}
    try:
        raw = _dr._zt_risk_face(root=root)
    except Exception as exc:                                     # noqa: BLE001
        return {"status": "unreadable", "detail": str(exc)[:160], "panels": {}}
    panels = {}
    for k, v in (raw.get("panels") or {}).items():
        v = v or {}
        cnt = v.get("count")
        prev = v.get("prev_count")
        panels[k] = {
            "label": v.get("label") or k,
            "status": v.get("status"),
            "count": cnt,
            # r1520: the panel's OWN bar. The projection kept only `prev_cutoff`, so the
            # mismatch line below printed `zt=None、zbgc=None…` -- a number the face owns
            # arriving on the CEO page as "None". Absent stays absent: the renderer says
            # 未标注 rather than borrowing the block's date.
            "cutoff": v.get("cutoff"),
            "prev_count": prev,
            "prev_cutoff": v.get("prev_cutoff"),
            # r1579: carry the asked-vs-holds evidence, so a lagging panel can
            # say WHY it lags instead of leaving the reader to guess.
            "asked_through": v.get("asked_through"),
            "empty_days": v.get("empty_days"),
            "empty_days_count": v.get("empty_days_count"),
            "delta": (cnt - prev) if (cnt is not None
                                      and prev is not None) else None,
        }
    out = {"source": ("scripts/daily_report._zt_risk_face "
                      "(same implementation as daily report §九)"),
           "panels": panels}
    if not raw.get("present"):
        out["status"] = "absent"
        out["note"] = raw.get("note") or "风险面未产出（缺面不读 0）"
        return out
    out.update({"status": "ok", "cutoff": raw.get("cutoff"),
                "cutoffs": raw.get("cutoffs"),
                "aligned": raw.get("aligned"),
                "seal_rate": raw.get("seal_rate"),
                "ladder": raw.get("ladder") or {},
                "top_streak": raw.get("top_streak"),
                "down_over_up": raw.get("down_over_up"),
                "kill_day": raw.get("kill_day"),
                "kill_day_unavailable": raw.get("kill_day_unavailable"),
                # r1279: the age of the copy travels with the numbers -- a
                # reader on another machine must be able to see that this is a
                # replica (E256), not this morning's tape.
                "freshness": raw.get("freshness") or {}})
    return out


def _zt_lag_cause(panel: dict) -> str:
    """Why one panel's rows stop short of the others (r1579).

    Two very different facts used to print the same way: "nobody collected that
    day" and "the exchange had nothing to report that day". The collector's day
    ledger answers it -- a ledgered day with no rows is a day it asked and got
    an empty page. Everything else stays unstated rather than guessed."""
    if not isinstance(panel, dict):
        return ""
    asked = panel.get("asked_through")
    cut = panel.get("cutoff")
    if not asked or not cut or asked <= cut:
        return ""
    empty = panel.get("empty_days") or []
    after = [d for d in empty if d > cut]
    if not after:
        return "（日账已问到 {}，未记明原因）".format(asked)
    shown = "、".join(d[5:] if len(d) == 10 else d for d in after[-3:])
    return "（{} 已问·当日零行）".format(shown)


def day_word(page_day, as_of):
    """「今日」only when the page's own day is the day those numbers were priced on.

    On a Saturday this page printed 「今日 +¥0（对比 2026-11-13）」: the reader's day has had
    no session, and the number belongs to Friday. Borrowing the reader's day for another bar
    is the r1664 family; naming the bar costs one word and never lies. `as_of` is the bar the
    sentence is about -- pass the one the sentence quotes, not a page-wide default.
    """
    pd, ao = str(page_day or "")[:10], str(as_of or "")[:10]
    if pd and ao and pd != ao:
        return ao
    return "今日"


def render_md(p: dict) -> str:
    m = p["market"]
    L = []
    L.append(f"# CEO 实盘使用一页纸 · {p['day']}")
    L.append("")
    L.append(f"> 自动生成 {p['generated']} · T-105 v2.1 · "
             "纯聚合面（零新判据）· [版本台账]"
             "(../../research/DECISION_CHAIN_LEDGER.md)")
    L.append("")
    L.extend(_freshness_lines(p.get("freshness") or {}))
    L.extend(_data_lane_lines(p.get("data_lanes") or {}))
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
    rt = p.get("risk_tape") or {}
    if rt.get("status") == "ok":
        parts = []
        for k in ("zt", "dtgc", "zbgc", "strong"):
            pv = (rt.get("panels") or {}).get(k) or {}
            if pv.get("count") is None:
                parts.append("{}={}".format(pv.get("label") or k, "缺面"))
                continue
            seg = "{} {}".format(pv.get("label") or k, pv["count"])
            if pv.get("delta") is not None:
                seg += "（{:+.0f}）".format(pv["delta"])
            parts.append(seg)
        line = ("- **市场风险面（前向池四面板·与每日战报§九同一实现）**："
                "截止 {} · {}".format(rt.get("cutoff"), " · ".join(parts)))
        if rt.get("seal_rate") is not None:
            line += " · 封板率 {:.1%}".format(rt["seal_rate"])
        lad = rt.get("ladder") or {}
        if lad:
            lad_seg = " / ".join("{}板{}".format(k, v) for k, v in lad.items())
            line += " · 连板 " + lad_seg
        if rt.get("kill_day") is not None:
            dw = day_word(p.get("day"), rt.get("cutoff"))
            line += (" · 读法（机械口径）：跌停≥涨停 → 杀跌日"
                     + (f"，{dw} " if dw == "今日" else f"（bar {dw}）")
                     + ("是" if rt["kill_day"] else "否"))
        elif (rt.get("kill_day_unavailable") or {}).get("note"):
            # r1579: the rule needs both pools on one session. Printing "否"
            # from 11-11 涨停s vs 11-09 跌停s was a verdict across days.
            dw = day_word(p.get("day"), rt.get("cutoff"))
            line += (" · 读法（机械口径）："
                     + (f"{dw} " if dw == "今日" else f"bar {dw} ")
                     + "**未判** —— " + rt["kill_day_unavailable"]["note"])
        L.append(line)
        fr = rt.get("freshness") or {}
        if fr.get("status") == "stale":
            L.append("  - **⚠ 读数陈旧**：{}——上面的数不是今天的盘面".format(
                fr.get("note") or "副本落后于应有 bar 日"))
        elif fr.get("status") == "unknown":
            L.append("  - 新旧未验：{}".format(
                fr.get("note") or "日历不可用"))
        if rt.get("aligned") is False:
            # r1520: this line used to print `zt=None` for every panel -- the projection
            # carried only `prev_cutoff`, so the one place that says WHICH panel is on
            # another day named nothing. Each panel now carries its own bar; when a panel
            # truly does not publish one, say 未标注 instead of borrowing the block's date.
            mism = "、".join(
                "{}={}{}".format(
                    k, (v or {}).get("cutoff") or "未标注",
                    _zt_lag_cause(v or {}))
                for k, v in (rt.get("panels") or {}).items()
                if (v or {}).get("status") == "ok")
            L.append("  - 四面板截止日不一致：{}（如实标注）".format(mism))
    else:
        L.append("- 市场风险面：{}（缺面不读 0）".format(
            rt.get("note") or rt.get("detail") or "未产出"))
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
    cvb = p.get("cap_vs_book") or {}
    if cvb.get("status") == "ok":
        L.append(f"- **这个帽子和下面的钱对过账**：{cvb['sentence']}")
        wa = cvb.get("widest_above") or {}
        if wa.get("name"):
            # r1580: "β 目标×波动目标" named two different rules as if they
            # were one.  Name the books from the faces instead of a sentence.
            _bi = p.get("book_identity") or {}
            _l, _t = _bi.get("ledger") or {}, _bi.get("ticket") or {}
            if _l.get("present") and _t.get("present") and _bi.get("comparable"):
                _book_name = ("本页账本（%s 名·%s）与执行单（%s 名·%s）两本"
                              % (_l.get("n_hold"), _l.get("rule"),
                                 _t.get("n_hold"), _t.get("rule")))
            else:
                _book_name = "ETF 复合书"
            L.append(f"  - 超帽最多的是 {wa['name']}：仓位 "
                     f"{wa['deployed_weight']:.1%}（超 {wa['gap_pp']:.1f}pp·"
                     f"{wa['multiple_of_cap']:.2f} 倍帽）；{_book_name}"
                     "列在同一张表但不进裁决")
        if cvb.get("stale"):
            L.append(f"  - 注：该对账面按政体态 asof {cvb.get('priced_on')} 计价，"
                     "与本页当前态不同（如实标注，未外推）")
    else:
        L.append("- 上限 vs 实际仓位：{}".format(
            cvb.get("detail") or '对账面未产出（缺面不读合规）'))
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
    wf = p.get("weight_face")
    if not wf:
        L.append("  - 权重面读不到（B_MAXDIV 配件缺失）——本节的百分数**不印**，"
                 "不按 0 记（r98 未知≠空）")
    else:
        L.append(f"  - **这六个百分数不是一块饼**：它们取自同一张 **{wf['members_total']} "
                 f"名**的 B_MAXDIV 面（面自身合计 {wf['face_sum']:.2%}），六员只占 "
                 f"**{wf['six_sum']:.2%}**，其余 **{wf['others_sum']:.2%}** 分给 "
                 f"{wf['others_count']} 个不在本页纸盘在册的观察户"
                 + (f"（最大 {wf['top_other'][0]} {wf['top_other'][1]:.2%}）"
                    if wf.get("top_other") else "")
                 + "——六个百分数相加不等于 100%，也不是「余额 60% 不知道去哪了」。")
        L.append("  - 权重是组合面给这一员的配比，**不是纸盘账户的持股比例**：纸盘每户"
                 "独立起始资本核算，权益与权重之间没有倍数关系。")
    ru = p.get("rollup") or {}
    if ru.get("return_pct") is None:
        L.append("- **六员合计：口径缺件**（起始资本不可得=诚实空档，不填 0）")
    else:
        sgn_p = "+" if ru["pnl_cny"] >= 0 else "-"
        dw = day_word(p.get("day"), (p.get("freshness") or {}).get("expected_bar"))
        if ru.get("day_pnl_cny") is None:
            day_txt = "{} —（无对照件，不填 0）".format("今日" if dw == "今日" else dw + " 之后")
        else:
            sgn_d = "+" if ru["day_pnl_cny"] >= 0 else "-"
            amt = f"{sgn_d}¥{_fmt_cny(abs(ru['day_pnl_cny']))}"
            if dw == "今日":
                day_txt = f"今日 {amt}（对比 {ru['day_prior']}）"
            else:
                # the reader's own day has had no session; borrowing its name for Friday's
                # move is the r1664 family. Name the bar and say there is nothing newer.
                day_txt = f"较 {dw} 收盘 {amt}（本页无新 bar）"
        L.append(f"- **六员合计：权益 ¥{_fmt_cny(ru['equity_cny'])}"
                 f"（起始 ¥{_fmt_cny(ru['initial_cny'])}·累计 "
                 f"{ru['return_pct']:+.2f}%·{sgn_p}¥"
                 f"{_fmt_cny(abs(ru['pnl_cny']))}）**；其中持仓 ¥"
                 f"{_fmt_cny(ru['positions_cny'])} / 现金 ¥"
                 f"{_fmt_cny(ru['cash_cny'])}；{day_txt}")
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
    rec = p["recommendation"]
    L.append("### 配置参考（研究面·v1.6 接线·零新判据）")
    if not rec["present"]:
        L.append(f"- {rec['note']}（指针 {rec['path']}）")
    else:
        L.append(f"- **结论**（as_of {rec['as_of']}·"
                 f"{rec['status']}）：{rec['recommendation']}")
        L.append(f"  - 依据：{rec['basis']}")
        if rec.get("best_combo_sharpe") is not None:
            L.append(f"  - 读数：最优阶段组合 {rec['best_combo']} Sharpe "
                     f"{rec['best_combo_sharpe']:.4f} vs 无条件 "
                     f"{rec['best_unconditional']} "
                     f"{rec['best_unconditional_sharpe']:.4f}"
                     f"（差 {rec['margin_sharpe']:+.4f}·P4 过线="
                     f"{'是' if rec['p4_pass'] else '否（诚实判负）'}）")
        L.append(f"  - 当前阶段：{rec['current_stage']}（阶段表=描述性读数，"
                 "不含判决线）")
        L.append(f"  - 在册持仓：{rec['n_holdings']} 员等权 "
                 f"{rec['weight']:.0%}·入场 {rec['entry_date']}·单边换手 "
                 f"{rec['turnover']:.2f}")
        if rec["codes"]:
            L.append(f"  - 名单：{' '.join(rec['codes'])}")
        _mrec = next((m for m in ((p.get("freshness") or {})
                                  .get("monthly") or [])
                      if m.get("face") == "recommendation"), None)
        if _mrec is not None:
            if _mrec["state"] == "behind":
                L.append(f"  - **这份名单已经过期**：它是月度网格，它的下一个月首"
                         f"交易日（{_mrec['dues'][0]}）已经过去，共欠 "
                         f"{_mrec['owed_firings']} 次换仓——**不要照这份名单新开仓**，"
                         "它记的是上一次 fired 的那一组名字。")
            elif _mrec["state"] == "current":
                L.append(f"  - 名单在它的节律内：月度网格，下一次换仓在 "
                         f"{(p.get('freshness') or {}).get('expected_bar')} 之后"
                         "的下一个月首交易日。")
        _trk = rec.get("track")
        if _trk and _trk.get("ret_pct") is not None:
            L.append("  - **这份名单这段到底赚了多少**：{} 进、{} 出（{} 个交易日），"
                     "{} 只按发布权重等权 **{:+.2f}%**；同一窗口全市场等权"
                     "（{} 只有价）**{:+.2f}%** → 超额 **{:+.2f}pp**"
                     "（机械读数·未扣成本·不构成新判据）".format(
                         _trk.get("entry_bar"), _trk.get("cutoff"),
                         _trk.get("sessions"), _trk.get("n_measured"),
                         _trk["ret_pct"], _trk.get("bench_n"),
                         _trk.get("bench_ret_pct") or 0.0,
                         _trk.get("excess_pp") or 0.0))
            L.append("    - 出处：`results/divlowvol_live/track_latest.json`"
                     "（名单面自己不产结果，这一行是它的前向实绩面）")
        else:
            L.append("  - 这份名单这段赚了多少：**读不到**"
                     "（前向实绩面缺，或它追的是另一份名单）——不借用别份名单的数")
        L.append("  - 本机可再生性：面板 "
                 f"`{rec['picks_panel']}` "
                 + ("**在位**" if rec["picks_panel_present"] else
                    "**不在本机**（该面由 bm-b 生成，本机只读；改不了名单也"
                    "重算不了它）")
                 + f"｜picks 面 as_of {rec['picks_asof'] or '未载'}")
        L.append(f"  - 全页指针：`{rec['path']}`（sha16 "
                 f"{rec['sha16']}）——三族 P1 判决 verdict 均 "
                 "insufficient-sample，如实随源携带")
    L.append("")
    L.append("## ④ 决策链版本横幅")
    L.append("")
    for v in p["chain_versions"]:
        L.append(f"- {v['version']}：{v['status']}")
    L.append("- v1 诚实锚：链输（J-TARGET 0/12 未过）；v2 简化链=池序首位"
             "在烧；v3 锦标赛=预注册冻结排队；赢家=只入册候选，上线走月界。")
    L.append("")
    L.append("## ⑤ 在飞判决批（NULLS 烧录进度·纯计数）")
    L.append("")
    jb = p["judgment_burns"]
    L.append(f"- 判定批 = {jb['target']} nulls/族（预注册冻结面）·finalize "
             f"硬门 {jb['finalize_gate']}；下表为追加面纯计数读出"
             "（零新判据·裁定与窗口实况见轮报告/台账）：")
    for r in jb["families"]:
        L.append(f"  - {r['family']}：{r['have']}/{r['target']}"
                 f"（dup_k={r['dup_k']}）"
                 + ("" if r["present"] else "（nulls 面未落=0 诚实）"))
    L.append("")
    L.append("## ⑥ ETF 复合书 · 前向实绩（生产候选·纯读出）")
    L.append("")
    L.extend(_book_identity_lines(p.get("book_identity") or {}))
    eb = p.get("etf_book") or {}
    if not eb.get("present"):
        L.append(f"- {eb.get('note') or '前向账本未产出'}（指针 `{eb.get('path')}`）")
    else:
        L.append(f"- **账本**：{eb['first_bar']} 播种 → {eb['last_bar']}，"
                 f"{eb['n_bars']} 个 bar，净值 **{eb['book_nav']:.6f}**"
                 f"（{eb['book_ret_pct']:+.3f}%）；同窗四 ETF 等权基准 "
                 f"{eb['bench_nav']:.6f}（{eb['bench_ret_pct']:+.3f}%）→ "
                 f"**超额 {eb['excess_bp']:+.1f}bp**")
        L.append(f"  - 回撤：书 {eb['book_max_dd_pct']:+.3f}%｜基准 "
                 f"{eb['bench_max_dd_pct']:+.3f}%｜本段换仓 "
                 f"{eb['n_refills']} 次（网格 {eb['rebal']} bar·持仓 "
                 f"{eb['n_hold']} 员·波动目标 {eb['vol_target_pct']}%·成本 "
                 f"{eb['cost_bp_per_side']}bp/边）")
        if eb.get("cash_leg_note"):
            L.append(f"  - 口径：{eb['cash_leg_note']}")
        if eb.get("provisional_bars"):
            L.append(f"  - 未定稿 bar：{' '.join(eb['provisional_bars'])}"
                     f"（闸 `{eb.get('drift_gate')}`：定稿盘面重生成后会改述，"
                     "按改述披露读）")
        mde = eb.get("min_detectable_edge_pp") or {}
        nb = eb.get("noise_band_pp") or {}
        if mde or nb:
            bits = []
            if nb.get("1y"):
                bits.append(f"超额 1 年噪声带 ±{nb['1y']}pp/年")
            if mde.get("1y"):
                bits.append(f"80% 功效下 1 年窗只能分辨 "
                            f"{mde['1y']}pp/年")
            L.append("  - **还不能下结论**：账本只发了 "
                     f"{eb.get('published_bars')} 个 bar，"
                     + ("；".join(bits) if bits else "功效表在册")
                     + f"；要分辨它自己的在窗 alpha 需约 "
                     f"{eb.get('years_for_80pct_power')} 年。"
                     "这一行是实绩读数，不是判决。")
        L.append(f"  - 全页指针：`{eb['path']}`")
    # ---- r1846: the same engine, priced before the universe that carries it
    _bp = p.get("etf_book_periods") or {}
    if not _bp.get("present"):
        L.append(f"- 分期间读数：{_bp.get('note') or '缺件（缺面不读 0）'}")
    else:
        _a = _bp.get("pre") or {}
        _b = _bp.get("same_universe_post") or {}
        _c = _bp.get("full_post") or {}
        if _a and _b:
            L.append(
                f"- **这本书有出生日期**：同一引擎、同一批老标的"
                f"（{_a.get('universe_size')} 只），"
                f"{str(_a.get('start'))[:4]}–{str(_a.get('end'))[:4]} 的 "
                f"{_a.get('n_cells')} 格超额在 **{_a['worst_pp']:+.2f} ~ "
                f"{_a['best_pp']:+.2f}pp/年**"
                f"（{'全部为负' if _a.get('all_negative') else '不全为负'}）；"
                f"换成 {str(_b.get('start'))[:4]} 之后同宇宙读 "
                f"**{_b['worst_pp']:+.2f} ~ {_b['best_pp']:+.2f}pp/年**"
                f"（{'全部为正' if _b.get('all_positive') else '不全为正'}）")
        if _c:
            L.append(
                f"  - 全宇宙（{_c.get('universe_size')} 只）"
                f"{str(_c.get('start'))[:4]} 之后读 "
                f"**{_c['worst_pp']:+.2f} ~ {_c['best_pp']:+.2f}pp/年**——"
                "**这两段差不是因子的证据，是期间与截面的证据**：正的超额只在 "
                "2020 年之后出现，且截面越宽读数越好看，所以上面那段实绩不能"
                "外推成「一直都有效」")
        L.append(f"  - 出处：`{_bp['path']}`（generated {_bp.get('generated')}"
                 f"·cutoff {_bp.get('cutoff')}·零判决零记账）")
    eo = p.get("etf_order") or {}
    if not eo.get("present"):
        L.append(f"- 照做版执行单：{eo.get('note') or '缺件（缺面不读 0）'}")
    else:
        _bw = eo.get("book_weight")
        _cw = eo.get("cash_weight")
        _w = ("｜敞口 {:.1%}｜现金 {:.1%}".format(_bw, _cw)
              if _bw is not None and _cw is not None else "")
        L.append(f"- **照做版执行单**（决策 bar {eo.get('decision_bar')}·"
                 f"成交在下一交易日开盘·最小买入 100 份=1 手）："
                 f"{eo.get('n')} 只，合计 ¥{_fmt_cny(eo.get('spent_cny') or 0)}"
                 f"，留现金 ¥{_fmt_cny(eo.get('cash_left_cny') or 0)}{_w}")
        for r in eo.get("rows") or []:
            L.append(f"  - {r['symbol']}｜{r['lots']} 手（{r['shares']} 份）"
                     f"｜约 ¥{_fmt_cny(r['amount_cny'] or 0)}｜价 {r['price']}")
        L.append("  - 口径：这是 100 万账面按目标铺满的整手清单，**不是换仓差量**"
                 "（差量见紧接的下一段）；"
                 "价=决策 bar 收盘，开盘成交价会不同。")
        if eo.get("generated"):
            L.append(f"  - 出处：`results/etf_book_order/{eo.get('file')}`"
                     f"（generated {eo.get('generated')}·cutoff {eo.get('bar')}）")
        # ---- r1786: the cash row is not dead weight, and the page says so with
        # the rate the ticket already priced -- never as money already earned.
        _cl = eo.get("cash_leg")
        if _cl and _cl.get("bands"):
            _hd = _cl["bands"].get(_cl["headline"]) or {}
            _bits = []
            for _key, _lab in _ETF_CASH_BANDS:
                _b = _cl["bands"].get(_key)
                if not _b:
                    continue
                if _key == "window" and _cl.get("window_years") is not None:
                    _lab = "有记录以来 {} 年".format(_cl["window_years"])
                _s = "{} {}%".format(_lab, _b["pct"])
                if _b.get("as_of"):
                    _s += "（{}）".format(_b["as_of"])
                _bits.append(_s)
            _cash = _cl.get("cash_cny")
            _ann = _hd.get("net_annual_cny")
            _share = (None if (_ann is None or not eo.get("nav_cny"))
                      else _ann / float(eo["nav_cny"]) * 100.0)
            L.append(
                "  - 那 ¥{} 现金不是趴着：按国债逆回购（GC001）计息——{}；"
                "按{}并扣 {:g}bp 保守折扣约 **¥{}/年**{}。".format(
                    _fmt_cny(_cash or eo.get("cash_left_cny") or 0),
                    "、".join(_bits), _hd.get("label", ""),
                    _cl.get("fall_bp"),
                    _fmt_cny(_ann or 0),
                    "" if _share is None else "（占账面 {:.2f}%）".format(_share)))
            L.append("    - 这一笔**不并进上面的净值**：前向账本自己写着"
                     "「现金腿按 0 计息」（如实披露、不建模），所以它是"
                     "「这段现金按今天的利率值多少」的读数，不是已经赚到的钱。")
            if _cl.get("source"):
                L.append("    - 出处：同一张票面的现金腿面"
                         "（利率源 `{}`·{} 个报价点）".format(
                             _cl["source"], _cl.get("tail") or "?"))
        else:
            L.append("  - 那笔现金赚什么：票面未印（缺面不读 0）")
        # ---- r1824: the cash row prices the sleeve at the 1-day rate and stops. The
        # reader's next question is a tenor, and the ladder face answers it only as of
        # its own cutoff. This block prints TODAY's tenor under the constraint that the
        # cash must be raisable on the decision bar.
        _cr = eo.get("cash_roll") or {}
        if not _cr.get("present"):
            L.append("  - **今天这笔闲钱滚哪一档**：{}".format(
                _cr.get("note") or "缺面不读 0 档"))
        elif _cr.get("verdict") == "NO_INSTRUCTION":
            L.append("  - **今天这笔闲钱滚哪一档**：读不到指令（{}）".format(
                _cr.get("reason") or "面上没写原因"))
        else:
            L.append("  - **今天这笔闲钱滚哪一档**：**{}**（{} 天）——报价 {}% · "
                     "扣手续费后净 {}%/年，{} 到期，{} 的决策 bar 用得上钱。".format(
                         _cr.get("contract"), _cr.get("tenor_days"),
                         _cr.get("quoted_pct"), _cr.get("net_ann_pct"),
                         _cr.get("matures"), _cr.get("decision_date")))
            _wy = _cr.get("worth_year_cny")
            _ww = _cr.get("worth_window_cny")
            if _wy is not None:
                L.append("    - 比天天滚 GC001 多赚：**一年 ¥{}**（到下一次决策的 {} 天里 "
                         "¥{}）——这是「选哪一档」的价值，不是已经赚到的钱。".format(
                             _fmt_cny(_wy), _cr.get("window_days") or "?",
                             _fmt_cny(_ww or 0)))
            _lk = _cr.get("locked_out") or []
            if _lk:
                L.append("    - 看着更高但**今天不能碰**的档：{}。".format(
                    "；".join("{} {}% 到 {} 才到期（晚 {} 天）".format(
                        r.get("contract"), r.get("quoted_pct"), r.get("matures"),
                        r.get("late_days")) for r in _lk)))
            _pl = _cr.get("placeable") or {}
            if _pl.get("placed_cny") is not None:
                L.append("    - 钱怎么放：¥{} = 沪市 ¥{}（10 万起）+ 深市 ¥{}（1 千起），"
                         "剩 ¥{} 放不进去。".format(
                             _fmt_cny(_cr.get("cash_cny") or 0),
                             _fmt_cny(_pl.get("sh_cny") or 0),
                             _fmt_cny(_pl.get("sz_cny") or 0),
                             _fmt_cny(_pl.get("leftover_cny") or 0)))
            L.append("    - 出处：`{}`（本位 bar {}·决策日 {}）".format(
                _cr.get("source_rel") or "?", _cr.get("as_of") or "?",
                _cr.get("decision_date") or "?"))
        # ---- r1785: the difference a returning reader actually has to trade.
        eod = eo.get("delta") or {}
        if not eod.get("present"):
            L.append("  - **今天要做的动作**（同一张票面里的换仓差量）："
                     f"{eod.get('note') or '缺件（缺面不读 0 手）'}")
        elif eod.get("no_action"):
            L.append("  - **今天要做的动作**（同一张票面里的换仓差量）："
                     f"{eod.get('verdict_cn')}——这一段不需要下单。")
        elif not eod.get("executable"):
            L.append("  - **今天要做的动作**（同一张票面里的换仓差量）："
                     f"{eod.get('verdict_cn')}——所以这一段不给买卖手数。")
        else:
            _bp = eo.get("cost_bp_per_side")
            _bs = eod.get("gross_sell_cny") or 0.0
            _bb = eod.get("gross_buy_cny") or 0.0
            L.append("  - **今天要做的动作**（同一张票面里的换仓差量·账面持仓 bar "
                     f"{eod.get('current_bar')} → 票面 bar {eo.get('bar')}）："
                     f"{eod.get('verdict_cn')}")
            if eod.get("sells"):
                L.append("    - 先卖 {} 只｜合计回笼 ¥{}".format(
                    len(eod["sells"]), _fmt_cny(_bs)))
                for r in eod["sells"]:
                    L.append("      - {}｜卖 {} 手｜{}→{} 手｜约 ¥{}｜价 {}".format(
                        r["symbol"], abs(r["delta_lots"] or 0),
                        r["current_lots"], r["target_lots"],
                        _fmt_cny(r["amount_cny"] or 0), r["price"]))
            if eod.get("buys"):
                L.append("    - 再买 {} 只｜合计支出 ¥{}".format(
                    len(eod["buys"]), _fmt_cny(_bb)))
                for r in eod["buys"]:
                    L.append("      - {}｜买 {} 手｜{}→{} 手｜约 ¥{}｜价 {}".format(
                        r["symbol"], abs(r["delta_lots"] or 0),
                        r["current_lots"], r["target_lots"],
                        _fmt_cny(r["amount_cny"] or 0), r["price"]))
            _cb = eod.get("cash_before_cny")
            _ca = eod.get("cash_after_cny")
            if _cb is not None and _ca is not None:
                # r1785: direction is read off the two cash numbers, not off
                # net_cash_cny -- the producer's net cash is "money needed to
                # buy", positive when cash FALLS, so reusing its sign here
                # printed a 40,000 outflow as "+40,000".
                _d = _ca - _cb
                L.append("    - 现金：动手前 ¥{} → 动完 ¥{}（{}¥{}）".format(
                    _fmt_cny(_cb), _fmt_cny(_ca),
                    "净增" if _d >= 0 else "净减", _fmt_cny(abs(_d))))
            if _bp:
                L.append("    - 成本：按票面 {:.1f}bp/边估，卖出 ¥{}＋买入 ¥{}＝约 ¥{}"
                         .format(_bp, _fmt_cny(_bs * _bp / 10000.0),
                                 _fmt_cny(_bb * _bp / 10000.0),
                                 _fmt_cny((_bs + _bb) * _bp / 10000.0)))
            _ts = eod.get("turnover_share_pct")
            if _ts is not None:
                L.append("    - 换手是账面总额的 {:.1f}%：这是近乎全换仓，"
                         "不是小修小补。".format(_ts))
            L.append("    - 两种读者别混用：**手上没有这只书**的照上面那张铺满单建仓；"
                     "**已经照过前一张单**的只做这一段。混着看会把同一批票买两遍。")
            _mk = eod.get("mark_cny")
            if _mk is not None:
                L.append("    - 和这一段一起读：账上那本按 {} 的价、票面按 {} 的价，"
                         "保留腿重估差 {}¥{}，单列、不并进上面的现金数。".format(
                             eod.get("mark_account_bar") or "上一交易日",
                             eo.get("bar"), "-" if _mk < 0 else "",
                             _fmt_cny(abs(_mk))))
            if eod.get("declaration_status", "").startswith("UNEXPLAINED"):
                L.append("    - 也和这一句一起读：票面自标「目标动过、但没有成交记录"
                         "解释这次移动」（{} → {}，账面零成交）——所以这一段是"
                         "「把账面拉到今天这张单」，不是「策略今天叫你换仓」。".format(
                             eod.get("mark_account_bar") or "上一交易日",
                             eo.get("bar")))
            L.append("    - 出处：同一张票面里的换仓差量面（`{}`·bar {}）".format(
                "results/etf_book_order/" + str(eo.get("file")),
                eod.get("current_bar")))
        # ---- r1828: the sheet says what to do today and when the next decision is, but
        # not whether today is the cheap day.  The desk has priced that on the panel
        # (a k-bar ladder against the ticket's own permission); a reader about to place
        # five orders should not have to open a research file to learn it.  Quoted, never
        # recomputed; a face on another bar is refused rather than quoted (E685/r1311).
        _pw = p.get("etf_punctuality") or {}
        if not _pw.get("present"):
            L.append("  - **今天做还是分开几天做**：{}——今天不印数".format(
                _pw.get("note") or "时点面未产出（缺面不读 0）"))
        elif (_pw.get("evidence_cutoff") and eo.get("bar")
              and str(_pw.get("evidence_cutoff"))[:10] != str(eo.get("bar"))[:10]):
            L.append("  - **今天做还是分开几天做**：时点面量的是 {} 的面板，与这一页"
                     "票面的 {} 不是同一天——今天不印这个数".format(
                         str(_pw.get("evidence_cutoff"))[:10],
                         str(eo.get("bar"))[:10]))
        else:
            _prow = {(r.get("k")): r for r in (_pw.get("rows") or [])}
            _picks = [k for k in (1, 3, 5) if _prow.get(k)]
            _pbits = []
            for _k in _picks:
                _r = _prow[_k]
                if _r.get("cost_cny") is None:
                    continue
                _pbits.append("等 {} 根 bar 贵 ￥{}".format(
                    _k, _fmt_cny(abs(_r.get("cost_cny")))))
            _pt = [(_prow[k].get("t")) for k in _picks if _prow[k].get("t") is not None]
            _psep = all(_prow[k].get("separable") for k in _picks
                        if _prow[k].get("separable") is not None)
            if _pbits:
                # r1849: this block said 「今天做」 about a ladder measured on the ticket's own
                # bar. The day-word audit can only report a bare today-word as a day nobody can
                # read, so the sentence now names the bar it prices (the branch above already
                # proved the punctuality face and the ticket share that bar).
                _pbar = str(eo.get("bar"))[:10]
                L.append("  - **在 {} 这一档做，还是分开几天做**（同一张单自己的时点价·"
                         "把延迟拆成 k 根 bar 的价差）：{}；这一档做的成本记 0。".format(
                             _pbar, "、".join(_pbits)))
                if _pt:
                    L.append("    - 这三档都以均值读，而且都能与 0 分开（t {}）"
                             "——「等一等再买」在这本书上有价，不是免费的选择{}。".format(
                                 " / ".join("{:+.2f}".format(v) for v in _pt),
                                 "" if _psep else "（但有一档不能与 0 分开，别当三份证据）"))
            else:
                L.append("    - 这几档没有读数（不印半个阶梯）。")
            _verdict = _pw.get("verdict")
            if _verdict == "NOTHING_OWED_TODAY":
                L.append("    - 这不是催单：时点面自己的判词是 **NOTHING_OWED_TODAY**"
                         "（票面按它自己的许可下单·命令欠 0）——这张单是把账面拉到 "
                         "{} 的票面，不是一次到期的调度决策；所以在 {} 这一档做"
                         "不欠你什么，贵的是「拖几天做」。".format(
                             str(eo.get("bar"))[:10], str(eo.get("bar"))[:10]))
            elif _verdict:
                L.append("    - 时点面自己的判词：**{}**（照抄，不改写）。".format(_verdict))
            _one = _pw.get("one_open_late") or {}
            if _one.get("median_cny") is not None:
                L.append("    - 单张纸仍然是抛硬币：晚一天更好的情况占 {}，中位 {}¥{}"
                         "（均值 {}¥{}）——均值要很多次才兑现，只做一次不一定。".format(
                             "{:.1f}%".format(float(_one.get("share_late_helps")) * 100.0)
                             if _one.get("share_late_helps") is not None else "?",
                             "-" if _one.get("median_cny") < 0 else "",
                             _fmt_cny(abs(_one.get("median_cny"))),
                             "-" if (_one.get("mean_cny") or 0) < 0 else "",
                             _fmt_cny(abs(_one.get("mean_cny") or 0))))
            L.append("    - 出处：`{}`（计价截止 {}·与票面 bar 同日）".format(
                _pw.get("file") or "results/etf_book_do_or_wait.json",
                str(_pw.get("evidence_cutoff"))[:10]))
        # ---- r1786: the sheet also says when it will change again; a reader who
        # has followed it should not have to guess how long the position stands.
        _nd = eo.get("next_decision_bars")
        if _nd is None:
            L.append("  - **下次什么时候再看**：票面未印（缺面不读 0）")
        elif _nd == 0:
            L.append("  - **下次什么时候再看**：这张 bar 本身就是决策 bar，"
                     "下一次决策随下一个 bar 到来。")
        else:
            L.append("  - **下次什么时候再看**：下一次决策还有 **{} 个 bar**"
                     "（网格 {} bar·上一次决策 bar {}）；在那之前这本书不换仓。"
                     .format(_nd, eo.get("rebal") or "?",
                             eo.get("book_decided_bar") or "?"))
        # ---- r1825: a bar count is not a date, and this page already speaks dates
        # four lines below (the cash tenor that matures on the permission date).
        # Read the sheet's own next-decision face -- it signs the bar three ways.
        _nfd = eo.get("next_decision_face") or {}
        if _nfd.get("present") is False:
            L.append("    - 换成日历日期：{}".format(
                _nfd.get("note") or "缺面不读 0"))
        elif _nfd.get("present"):
            _bad = (_nfd.get("wrong_claims") or []) + \
                   (_nfd.get("off_grid_claims") or [])
            if not _nfd.get("agrees") or _bad:
                L.append("    - 换成日历日期：**今天不印**——票面自己的下次决策面"
                         "签名对不上（判定 {}·对不上的面：{}）；三个面说不到一天，"
                         "就不挑一个印。".format(
                             _nfd.get("verdict") or "?",
                             "、".join(_bad) if _bad else "未点名"))
            elif (_nd is not None and _nfd.get("bars_away") is not None
                  and _nfd.get("bars_away") != _nd):
                L.append("    - 换成日历日期：**今天不印**——面说 {} 根后是 {}，"
                         "而这张票面说 {} 根后；两个数总有一个是陈的。".format(
                             _nfd.get("bars_away"), _nfd.get("date"), _nd))
            elif _nfd.get("date"):
                L.append("    - 换成日历日期就是 **{}**（同一条票面的下次决策面，"
                         "{} 个面签名一致·日历源 `{}`）——20 根网格落在这一天，"
                         "不是月末也不是月初。".format(
                             _nfd.get("date"), _nfd.get("n_claims") or 0,
                             _nfd.get("calendar_source") or "?"))
    # ---- r1826: the sheet names the lots and the cash; nothing said how much of the
    # market's own turnover that order is.  Everything below is quoted from the
    # capacity face at the lens IT measured -- this block never scales it to today's
    # smaller book, because that number was never measured.
    _cap = p.get("etf_capacity") or {}
    if not _cap.get("present"):
        L.append("  - **这单装得进市场吗**（1% ADV 闸线）：{}——今天不印数".format(
            _cap.get("note") or "容量面未产出（缺面不读 0）"))
    elif (_cap.get("session") and eo.get("bar")
          and str(_cap.get("session"))[:10] != str(eo.get("bar"))[:10]):
        L.append("  - **这单装得进市场吗**（1% ADV 闸线）：容量面量的是 {} 的盘口，"
                 "与这一页票面的 {} 不是同一天——今天不印这个数".format(
                     str(_cap.get("session"))[:10], str(eo.get("bar"))[:10]))
    else:
        _cl = _cap.get("line_pct")
        _cr = _cap.get("reading_today_pct")
        _lens = _cap.get("lens_cny")
        _capok = (_cl is not None and _cr is not None and _lens)
        L.append(
            "  - **这单装得进市场吗**（{:.2f}% ADV 闸线）：{}".format(
                float(_cl or 0.0) if _capok else 0.0,
                ("按 ¥{} 全仓、5 个名字各 ¥{} 量，最近 {} 个交易日里 **{} 天**过线，"
                 "今天读数 **{:.4f}%**（最紧的一席 {}）。".format(
                     _fmt_cny(_lens), _fmt_cny(_cap.get("per_name_cny") or 0),
                     _cap.get("n_sessions"), _cap.get("n_passes"),
                     _cr, _cap.get("binding_today") or "?"))
                if _capok else "容量面读数不全（不印半张尺子）"))
        if _capok:
            _un = _cap.get("n_unmeasurable") or 0
            L.append("    - 倒过来读：今天这个成交额下能过的资本上限 **¥{}**"
                     "（比 ¥{} 少 ¥{}）；窗内中位 ¥{}、最差一天 ¥{}——"
                     "「装不下 100 万」要换成「平常装得下多少」{}。".format(
                         _fmt_cny(_cap.get("capital_at_line_cny")),
                         _fmt_cny(_lens), _fmt_cny(_cap.get("gap_to_lens_cny")),
                         _fmt_cny(_cap.get("capital_median_cny")),
                         _fmt_cny(_cap.get("capital_min_cny")),
                         "" if not _un else "（另有 {} 天不可量，既不算过也不算不过）"
                         .format(_un)))
            # ---- r1827: the paragraph above measures the full lens on ITS five names.
            # The reader's question is about THIS sheet's five names at THIS size, which
            # r1826 could only refuse.  Now it is measured; quote it and keep the
            # distinction between the two books explicit.
            _cs = p.get("etf_capacity_at_size") or {}
            _cs_bar_ok = (not _cs.get("bar") or not eo.get("bar")
                          or str(_cs.get("bar"))[:10] == str(eo.get("bar"))[:10])
            # r1830: the bar test above catches a face priced on another session, but not
            # the commoner shape -- a new ticket lands, the face still answers the old one,
            # and both are stamped with the same bar. The reading is about a different
            # order, so it is another book (E685: a number travels with its ruler).
            _cs_tk = os.path.basename(str(_cs.get("ticket_file") or "").replace("\\", "/"))
            _cs_tk_ok = (not _cs_tk or not eo.get("file") or _cs_tk == eo.get("file"))
            if _cs.get("present") and _cs_bar_ok and _cs_tk_ok:
                _csr = _cs.get("reading_pct")
                _csv = _cs.get("verdict")
                _csword = {"ADMIT_AT_THIS_SIZE": "**过线**",
                           "DENY_AT_THIS_SIZE": "**没过线**",
                           "UNMEASURABLE_AT_THIS_SIZE": "不给判词"}.get(
                               _csv, "不给判词")
                L.append("    - 换成本单**自己的名字与金额**重量：最紧一席 {} 占它自己"
                         "成交额的 **{:.4f}%**，闸线 {:.2f}% → {}。".format(
                             _cs.get("binding") or "?", _csr,
                             float(_cs.get("line_pct") or 0.0), _csword))
                _csh = _cs.get("headroom_cny")
                _csm = _cs.get("headroom_multiple")
                if _csv in ("ADMIT_AT_THIS_SIZE", "DENY_AT_THIS_SIZE") and _csh and _csm:
                    L.append("      - 同样这五个名字、同样的比例，还能放大约 **{:.2f}×**"
                             "（到 ¥{}）才碰到闸线。".format(float(_csm), _fmt_cny(_csh)))
                _csun = _cs.get("unmeasurable") or []
                if _csun:
                    L.append("      - 但 {} 读不到成交额，所以「这单装得下」这句话"
                             "缺一块（缺的读数不当成过线）。".format("、".join(_csun)))
                _csns = _cs.get("name_set") or {}
                if _csns and _csns.get("same_book") is False:
                    L.append("      - 上面那个 {:.4f}% 是**另一组名字**量的（只有 {} 个重合，"
                             "它量的是 {}）——两个数不是同一把尺子，本行用的是本单自己的名字。"
                             .format(float(_cr or 0.0), _csns.get("n_overlap") or 0,
                                     "、".join(_csns.get("only_in_published") or []) or "不同名单"))
            else:
                _cs_why = (_cs.get("note") or "同规模容量面未产出（缺面不读 0）")
                if _cs.get("present") and not _cs_bar_ok:
                    _cs_why = ("同规模容量面量的是 {} 的盘口，与这一页票面的 {} 不是同一天"
                               "——今天不印这个数".format(str(_cs.get("bar"))[:10],
                                                    str(eo.get("bar"))[:10]))
                elif _cs.get("present") and not _cs_tk_ok:
                    _cs_why = ("同规模容量面回答的是 {}，而这一页印的票面是 {}"
                               "——不是同一张单，今天不印这个数".format(_cs_tk, eo.get("file")))
                L.append("    - 和上面这张单一起读：这把尺子是**按全仓量的**，"
                         "而今天这单只用了账面 {:.1f}%（¥{}）——{}，"
                         "所以本页不印「今天这单过线/没过线」，只印它量过的那个规模。".format(
                             float((eo.get("book_weight") or 0.0)) * 100.0,
                             _fmt_cny(eo.get("spent_cny")), _cs_why))
            L.append("    - 1% 是闸自己选的线，不是量出来的线：换一条线，"
                     "这里的每个数按同一比例移动。")
        L.append("    - 出处：`{}`（盘口 {}·计价截止 {}）".format(
            ETF_CAPACITY_REL, str(_cap.get("session") or "未标")[:10],
            str(_cap.get("evidence_cutoff") or "未标")[:10]))
    # ---- r1829: the sheet is priced at a close and filled at the next open.  The
    # caveat "开盘成交价会不同" was the only word on it; measure it on the ticket's own
    # five names and give it in CNY on the ticket's own amount.  Never added to the
    # commission line -- one is a price level, the other is a transfer.
    _og = p.get("etf_open_gap") or {}
    _og_ok = (not _og.get("evidence_cutoff") or not eo.get("bar")
              or str(_og.get("evidence_cutoff"))[:10] == str(eo.get("bar"))[:10])
    _ogr = _og.get("recent") or {}
    if _og.get("present") and _og_ok and _ogr.get("median_bp") is not None:
        _ogm = _fmt_cny(abs(_og.get("money", {}).get("band_cny") or 0.0))
        _ogf = _og.get("fee_double_sided_cny")
        _ogr_ratio = _og.get("band_ratio_vs_fee")
        _ogword = {"OVERNIGHT_BAND_DWARFS_THE_FEE": "跳空这条带比成本大得多",
                   "THE_FEE_IS_THE_BIGGER_UNKNOWN": "成本比跳空这条带更大",
                   "COMPARABLE_BANDS": "两者量级相当"}.get(
                       _og.get("verdict"), "不给判词")
        L.append("    - **开盘价和票面价隔多远**（上面那句「开盘成交价会不同」的量化）："
                 "这 {} 只票近 {} 个交易日的隔夜跳空中位 **{:+.1f}bp**、"
                 "中间六成落 **{:+.1f}..{:+.1f}bp**；按本单 ¥{} 建仓，"
                 "这条带值 **¥{}**，而整张单的双边成本是 ¥{} → {}。".format(
                     _og.get("n_names") or "?", _og.get("recent_sessions") or "?",
                     float(_ogr["median_bp"]), float(_ogr.get("p20_bp") or 0.0),
                     float(_ogr.get("p80_bp") or 0.0),
                     _fmt_cny(_og.get("traded_amount_cny")), _ogm,
                     _fmt_cny(_ogf) if _ogf is not None else "（票面没写成本口径）",
                     _ogword))
        if _og.get("verdict") == "OVERNIGHT_BAND_DWARFS_THE_FEE" and _ogr_ratio:
            L.append("      - 换句话读：**成交价会飘多少，是手续费那个数的 {:.1f} 倍**"
                     "——这张单真正的不确定不在佣金上。".format(float(_ogr_ratio)))
        L.append("      - **跳空不是成本**：它是价格水平的变化，同一次跳空也把敞口 k（{:.2f}%）"
                 "按同一比例搬家，没有付给任何人——所以这一行**不能**与上面的手续费相加。".format(
                     float((eo.get("book_weight") or 0.0)) * 100.0))
        L.append("      - 中位与带是两把尺子，不平均：中位说的是「平常那一天」，"
                 "带说的是「中间六成的日子」。")
        _oga = _og.get("all_history") or {}
        if _oga.get("median_bp") is not None:
            L.append("      - 全史口径（第二把尺子·{:d} 段）：中位 {:+.1f}bp、"
                     "中间六成 {:+.1f}..{:+.1f}bp——换成全史看，答案没有变。".format(
                         int(_oga.get("n") or 0), float(_oga["median_bp"]),
                         float(_oga.get("p20_bp") or 0.0),
                         float(_oga.get("p80_bp") or 0.0)))
        if _og.get("missing"):
            L.append("      - 读不出的名字：{}（缺读数不当成 0）".format(
                "、".join(_og["missing"])))
        L.append("      - 出处：`{}`（计价截止 {}·票面 {}）".format(
            ETF_OPEN_GAP_REL, str(_og.get("evidence_cutoff") or "未标")[:10],
            _og.get("ticket") or "未标"))
    else:
        _og_why = _og.get("note") or "开盘间隔面未产出（缺面不读 0）"
        if _og.get("present") and not _og_ok:
            _og_why = ("开盘间隔面量的是 {} 的数据，与这一页票面的 {} 不是同一天"
                       "——今天不印这个数".format(
                           str(_og.get("evidence_cutoff"))[:10],
                           str(eo.get("bar"))[:10]))
        L.append("    - 上面那句「开盘成交价会不同」今天没有量过：{}。".format(_og_why))
    # ---- r1820: the sheet names five codes and their prices; nothing on this page
    # said what part of that money is paid above the funds' own NAV.  One number per
    # reader decision: how much of the ticket is premium, and what reversion would cost.
    _pm = p.get("etf_premium") or {}
    # r1820: this block is fed by another script on another trip.  Today the two
    # agree, but nothing enforced it -- the premium face was written at 02:00 and
    # the ticket re-issued at 02:36 under the same file name.  If that trip priced
    # a DIFFERENT ticket, the numbers describe a different order: say so and print
    # nothing, rather than quoting a premium against prices the reader is not
    # being asked to pay (r1781 family).
    _pm_tk = _pm.get("ticket")
    _eo_tk = eo.get("file")
    if _pm_tk and _eo_tk and _pm_tk != _eo_tk:
        L.append("  - **这笔钱里有多少是溢价**：溢价面价的票面是 `{}`，"
                 "与这一页的执行单 `{}` 不是同一张——今天不印这个数".format(
                     _pm_tk, _eo_tk))
    elif not _pm.get("present"):
        L.append("  - **这笔钱里有多少是溢价**：{}——今天不印数".format(
            _pm.get("note") or "溢价面未产出（缺面不读 0）"))
    else:
        _paid = _pm.get("premium_paid_cny")
        _osh = _pm.get("premium_share_of_order_pct")
        _nsh = _pm.get("premium_share_of_nav_pct")
        _amt = _pm.get("verified_amount_cny")
        _verb = "多付" if (_paid or 0) >= 0 else "少付（净折价）"
        L.append(
            "  - **这笔钱里有多少是溢价**（买价高于基金自己净值的那部分，"
            "不是手续费、不是佣金）：票面 {} 只合计 ¥{}，{} **¥{}**"
            "（＝票面的 {}%·账面的 {}%）".format(
                _pm.get("n_verified"),
                _fmt_cny(_amt) if _amt is not None else "?",
                _verb,
                _fmt_cny(abs(_paid)) if _paid is not None else "?",
                "{:.2f}".format(_osh) if _osh is not None else "?",
                "{:.2f}".format(_nsh) if _nsh is not None else "?"))
        _own = set(_pm.get("own_in_top_decile") or [])
        for _r in _pm.get("rows") or []:
            _pp = _r.get("premium_pct")
            _pc = _r.get("premium_paid_cny")
            _pl = _r.get("market_pctile")
            if _pp is None:
                continue
            _dir = "多付" if (_pc or 0) > 0 else "省"
            _bits = ["{}｜{:+.2f}%｜{} ¥{}".format(
                _r.get("symbol"), _pp, _dir, _fmt_cny(abs(_pc or 0)))]
            if _pl is not None:
                _bits.append("该基金近一年 {:.1f} 分位".format(_pl))
            if _r.get("symbol") in _own:
                _bits.append("**在它自己历史的前 10% 高位**")
            L.append("    - " + "｜".join(_bits))
        _st = _pm.get("stress") or {}
        _z = _st.get("if_premium_reverts_to_zero_cny")
        _zp = _st.get("if_premium_reverts_to_zero_pct_of_nav")
        _rm = _pm.get("own_revert_cny")
        _rmp = _st.get("if_premium_reverts_to_own_median_pct_of_nav")
        if _z is not None:
            L.append(
                "    - 压力读数（是压力不是预测）：溢价若回到 0 → **-¥{}"
                "（账面 -{}%）**；回到各基金自己的中位 → -¥{}（账面 -{}%）".format(
                    _fmt_cny(abs(_z)),
                    "{:.2f}".format(abs(_zp)) if _zp is not None else "?",
                    _fmt_cny(abs(_rm)) if _rm is not None else "?",
                    "{:.2f}".format(abs(_rmp)) if _rmp is not None else "?"))
        _yrs = _pm.get("years_of_backtest_return_paid")
        _cagr = _pm.get("book_cagr_pct")
        if _yrs is not None and _cagr is not None:
            # r1849: this line used to say 「今天」 about the premium face's own session, so the
            # day-word audit could only report PRINTED_BUT_UNANCHORED -- one line on the page
            # named a day nobody could read. The date is the session the premium numbers were
            # priced on; a sentence quoting a number names the bar that number came from. When
            # the face carries no session the sentence drops the day word instead of assuming
            # today (a missing date is a debt the audit can name, not a fact to invent).
            _sess = str(_pm.get("ticket_session") or p.get("day") or "")[:10]
            _tail = ("；而且在 {} 这一档，{} 正站在它自己一年里最贵的那一头".format(
                _sess, "、".join(sorted(_own))) if (_own and _sess) else
                ("；而且 {} 正站在它自己一年里最贵的那一头".format(
                    "、".join(sorted(_own))) if _own else ""))
            L.append(
                "    - 白话：¥{} 约等于这本书 {}% 年化产出的 **{} 年**。"
                "溢价不是手续费——赎回/套利恢复正常时它会吐回去，所以它是"
                "「先垫出去的钱」；但它也确实不是净值{}".format(
                    _fmt_cny(abs(_paid)) if _paid is not None else "?",
                    "{:.2f}".format(_cagr), "{:.1f}".format(_yrs), _tail))
        L.append(
            "    - 出处：`{}`（它自己价的票面 {}·票面会话 {}·IOPV 会话 {}·"
            "同会话={}）".format(
                ETF_PREMIUM_REL, _pm.get("ticket"),
                _pm.get("ticket_session"), _pm.get("iopv_session"),
                "是" if _pm.get("session_match") else "否"))
    # ---- r1835: the block above tells the reader one leg stands at the top decile
    # of its own year and stops there.  The next question ("buy a cheaper twin then?")
    # is already priced (etf_book_premium_choice) and the two rulers that answer it
    # DISAGREE -- so both are printed, and neither is applied silently.
    _pc = p.get("etf_premium_choice") or {}
    _pc_tk = os.path.basename(str(_pc.get("ticket") or ""))
    # the swap is priced off the same snapshot the premium block reads; when that
    # block could not be read (missing, or priced on another ticket) this one has no
    # business quoting a saving -- the reader would be told "we cannot read the
    # premium" and "you could save ¥X" in the same breath.
    _pm_readable = bool(_pm.get("present")) and (
        not _pm_tk or not _eo_tk
        or os.path.basename(str(_pm_tk)) == os.path.basename(str(_eo_tk)))
    if not _pm_readable:
        L.append("  - **这一腿要不要换成更便宜的**：溢价面今天读不到"
                 "（或价的不是这张票），换腿判断跟着缓一次——今天不印数")
    elif _pc_tk and _eo_tk and _pc_tk != os.path.basename(str(_eo_tk)):
        L.append("  - **这一腿要不要换成更便宜的**：换腿面价的票面是 `{}`，"
                 "与这一页的执行单 `{}` 不是同一张——今天不印这个数".format(
                     _pc_tk, _eo_tk))
    elif not _pc.get("present"):
        L.append("  - **这一腿要不要换成更便宜的**：{}——今天不印数".format(
            _pc.get("note") or "换腿面未产出（缺面不读 0）"))
    else:
        _cap = _pc.get("annual_giveup_cap_pp")
        _med = _pc.get("median_tenure_windows")
        _mean = _pc.get("mean_tenure_windows")
        _sh1 = _pc.get("share_one_window")
        for _lg in _pc.get("stretched") or []:
            _sym = _lg.get("symbol")
            _ppc = _lg.get("premium_pct")
            _cny = _lg.get("premium_cny")
            if _ppc is None:
                continue
            L.append(
                "    - **{} 这一腿换不换**：它自己溢价 {:+.2f}%（多付 ¥{}）"
                "超过换腿门槛 {}pp".format(
                    _sym, _ppc,
                    _fmt_cny(abs(_cny)) if _cny is not None else "?",
                    "{:.1f}".format(_pc.get("threshold_pp"))
                    if _pc.get("threshold_pp") is not None else "?"))
            if _lg.get("twin"):
                _twpp = _lg.get("twin_premium_pct")
                L.append(
                    "      - 同一市场的孪生 **{}** 溢价 {} → 一次省 **¥{}**；"
                    "但它在这本书自己的打分里落后 {:.3f}".format(
                        _lg.get("twin"),
                        "{:+.2f}%".format(_twpp) if _twpp is not None else "?",
                        _fmt_cny(_lg.get("saving_cny_once"))
                        if _lg.get("saving_cny_once") is not None else "?",
                        _lg.get("twin_score_gap") or 0.0))
                _gpp = _lg.get("giveup_pp_per_year")
                _gcn = _lg.get("giveup_cny_per_window")
                _bp = _lg.get("breakeven_convergence_p")
                _bw = _lg.get("breakeven_tenure_windows")
                if _gpp is not None and _cap is not None:
                    L.append(
                        "      - 尺子一（年化）：换过去每年放弃 **{:.2f}pp**，"
                        "门槛 {:.1f}pp → **不换**".format(_gpp, _cap))
                if _gcn is not None and _bw is not None:
                    _by = _lg.get("breakeven_tenure_years")
                    L.append(
                        "      - 尺子二（这本实测只持 {} 窗：中位 {} 窗、均值 {} 窗、"
                        "{}% 的座位只坐一窗）：每窗放弃 ¥{}，要 **{} 窗**{}"
                        "才吃掉省下的钱".format(
                            "{:.2f}".format(_mean) if _mean is not None else "?",
                            "{:.0f}".format(_med) if _med is not None else "?",
                            "{:.2f}".format(_mean) if _mean is not None else "?",
                            "{:.0f}".format((_sh1 or 0) * 100)
                            if _sh1 is not None else "?",
                            _fmt_cny(_gcn),
                            "{:.1f}".format(_bw),
                            "（{} 年）".format("{:.1f}".format(_by))
                            if _by is not None else ""))
                if _bp is not None:
                    L.append(
                        "      - 够本的门槛（不是预测）：离场前这段溢价差收敛超过 "
                        "**{:.1f}%** 换就划算；单日快照量不出它会不会收敛，"
                        "所以这里只印门槛".format(_bp * 100))
            if _lg.get("drop_to_cash_saving_cny") is not None:
                L.append(
                    "      - 第三条路（先不买、拿现金）：省 ¥{}，但放弃整段敞口"
                    "——它比孪生那条省得多，也把这本书的仓位改小了".format(
                        _fmt_cny(_lg.get("drop_to_cash_saving_cny"))))
        L.append(
            "    - 换腿面的判词是 **{}**：两把尺子在这张单上给相反答案，"
            "页面按预注册把两个都印、不合并、不替你选".format(
                _pc.get("verdict") or "未印"))
        L.append(
            "    - 出处：`{}`（票面 {}·as_of {}·换腿门槛与年化上限都是冻结常量）".format(
                ETF_PREMIUM_CHOICE_REL, _pc.get("ticket"), _pc.get("as_of")))
    L.append("")
    L.append("## ⑦ 指数期货 carry 书 · 开仓资金线（纯读出）")
    L.append("")
    cb = p.get("carry_book") or {}
    if not cb.get("present"):
        L.append(f"- {cb.get('note') or '资金线面未产出'}（指针 "
                 f"`{cb.get('path')}`）")
    else:
        acc = cb.get("accounts") or {}
        lots0 = cb.get("executable_lots_total")

        def _n(x, pct=0):
            return "?" if x is None else (
                _fmt_cny(x) if pct == 0 else f"{x:.{pct}f}")

        head = ("- **这本书当前不开仓**：按采纳的硬上限尺子"
                f"（arm={cb.get('arm')}），现金下可执行 "
                f"**{lots0} 手**；"
                if lots0 == 0 else
                f"- 可执行 **{lots0} 手**（尺子 arm={cb.get('arm')}）；")
        L.append(head + "桌上仓单已撤出可执行票面（撤下合计 "
                 f"{cb.get('withdrawn_lots_total')} 手）")
        for code in ("IC", "IM"):
            a = acc.get(code)
            if not a:
                continue
            L.append(f"  - {code}：目标 {_n(a.get('target_pct'), 1)}% · "
                     f"可执行 **{a.get('executable_lots')} 手**"
                     f"（{a.get('executable_state')}·撤 "
                     f"{a.get('withdrawn_lots')} 手）· 首档 "
                     f"**{_n(a.get('first_rung_cny'))} 元** · 差 "
                     f"{_n(a.get('gap_cny'))} 元"
                     f"（{_n(a.get('gap_pct'), 2)}% 资本）· 桌上 "
                     f"{a.get('desk_lots')} 手 = "
                     f"{_n(a.get('desk_multiple'), 2)} 倍波动预算")
        L.append(f"- 最便宜入门：**{cb.get('cheapest_product')} 账户 "
                 f"{_n(cb.get('cheapest_cny'))} 元**；两条腿同时开 "
                 f"{_n(cb.get('funding_all_cny'))} 元")
        L.append(f"- 撤单范围：`{cb.get('decision')}`"
                 f"（{cb.get('decided')}·{cb.get('decided_in')}）＝"
                 "只撤可执行票面；前向纸面序列是 append-only 证据行，"
                 "改标签不重写、不截断、不删除")
        L.append(f"  - 纸面账本 {cb.get('paper_lots_total')} 手**不删不改**，"
                 f"标签 `{cb.get('paper_label')}`"
                 "（它记的是那份更大资本账户的行为，不是这本书的）")
        L.append("  - 撤单是**条件的**不是判词：资金补到首档后同一规则自动"
                 "还回 1 手（撤单对资本，不对袖面）")
        L.append(f"- 出处：`{cb.get('path')}`｜generated "
                 f"{cb.get('source_generated')}｜cutoff "
                 f"{cb.get('evidence_cutoff')}｜尺子 "
                 f"`{cb.get('source_face')}`／`{cb.get('ladder_face')}`")
    ct = p.get("carry_timing") or {}
    if not ct.get("present"):
        L.append(f"- 贴水择时：{ct.get('note') or '择时面未产出'}"
                 f"（指针 `{ct.get('path')}`）——**时机这一半今天读不到，"
                 "资金到首档也先别下单**")
    else:
        rowst = ct.get("accounts") or {}
        edge = ct.get("band_edge_pct")
        inband = [c for c, r in rowst.items() if r.get("in_band")]
        verdict = ct.get("verdict")
        if verdict == "RULE":
            L.append(f"- **贴水择时（{verdict}）**：规则＝{ct.get('rule')}"
                     f"；进场带是分位 **≤ {edge}%**（贴水越宽＝分位越低，"
                     "数字方向与「宽」相反）")
        else:
            L.append(f"- **贴水择时（{verdict}）**：规则未通过检验，"
                     "这条线**不按时机进出**，一直拿着（口径见出处）")
        parts = []
        for c in ("IC", "IM", "IF", "IH"):
            r = rowst.get(c)
            if not r:
                continue
            mark = "**在带内**" if r.get("in_band") else "不在带内"
            pct = r.get("percentile")
            parts.append(f"{c} 分位 {('?' if pct is None else round(pct, 1))}"
                         f"（basis {('?' if r.get('basis_pct') is None else round(r.get('basis_pct'), 2))}%）{mark}")
        L.append("  - " + "；".join(parts) if parts else "  - 分位读数缺")
        # r1299: this sentence said 「今天」 over the carry face's own bar, which is one session
        # behind the page whenever the basis panel has not been pulled yet (11-16 against a
        # 11-17 page). Same one-word rule as the rest of this file: name the bar you read.
        _dw_t = day_word(p.get("day"), ct.get("evidence_cutoff"))
        _at_t = "今天" if _dw_t == "今天" else f"在 {_dw_t} 那根 bar 上"
        if inband:
            acct_codes = set((cb.get("accounts") or {}).keys()) if cb.get("present") else set()
            openable = [c for c in inband if c in acct_codes]
            L.append(f"  - {_at_t}在带内：**{'、'.join(inband)}** —— "
                     "时机这一半是开的"
                     + ("" if openable else
                        "；但其中没有一只有资金线（IF/IH 只作读数披露，"
                        "这本书只对 IC/IM 建仓）"))
        else:
            L.append(f"  - {_at_t}**四个品种都不在带内**：时机这一半是关的，"
                     "等贴水回到最宽的五分之一")
        L.append("  - **两个条件同时满足才下单**：资金到首档 ∧ 时机在带内。"
                 "钱够了但不在带内＝继续等（省下的是更贵的预付款）；"
                 "在带内但钱不够＝仍是 0 手")
        if ct.get("percentile_adds_over_level_pairs") == []:
            L.append("  - 诚实一条：这张面前后测过「分位是否比贴水水平多带信息」，"
                     "答案是**没有**（`percentile_adds_over_level_pairs` 为空）——"
                     "分位只是贴水水平的单调重排，所以这条规则也可以直接写在水平上")
        L.append(f"  - 出处：`{ct.get('path')}`｜cutoff {ct.get('evidence_cutoff')}"
                 f"｜generated {ct.get('source_generated') or '面未自带（读 window.to）'}"
                 f"｜收敛比 {ct.get('ratio')}")
    # r1819: the two halves above both assume the 8% vol ruler is the only constraint.
    # A broker's margin is a second floor, and the page owes the reader the check.
    cm = p.get("carry_margin") or {}
    if not cm.get("present"):
        L.append(f"- 保证金这一路：{cm.get('note') or '保证金面未产出'}"
                 f"（指针 `{cm.get('path')}`）——**今天读不到保证金读数，"
                 "上面那条首档资金线只按波动尺算，未与券商的保证金核对**")
    else:
        rows_m = cm.get("accounts") or {}
        gap = cm.get("ruler_gap") or {}
        gates = cm.get("gates") or {}
        if cm.get("verdict") == "VOL_RULER_IS_THE_GATE":
            L.append("- **保证金不是门槛**（`%s`）：两把尺子里先咬住的是 8%% 波动尺。"
                     "让保证金臂追平波动臂首档，初始保证金率要涨到 "
                     % cm.get("verdict")
                     + "、".join(f"{k} {v:.2f}%"
                                 for k, v in (cm.get("breakeven_rate_pct") or {}).items())
                     + "（本面扫了 " + "、".join("%.0f%%" % float(x) for x in
                                               (cm.get("rates_swept_pct") or []))
                     + " 四档，所有现实费率都远低于这个临界值）")
        elif cm.get("verdict") == "MARGIN_IS_THE_GATE":
            L.append("- **保证金才是门槛**（`%s`）：按扫描到的保证金率，保证金臂已经高于波动臂首档 —— "
                     "上面那条首档资金线是低估的，应按保证金口径重算"
                     % cm.get("verdict")
                     + f"（超出的品种：{'、'.join(k for k, g in gates.items() if g == 'MARGIN')}）")
        else:
            L.append(f"- 保证金读数无法判断：{cm.get('verdict')}")
        parts_m = []
        for code in ("IC", "IM"):
            r = rows_m.get(code)
            if not r:
                continue
            parts_m.append(
                f"{code} 每手名义 {_fmt_cny(r.get('notional_cny'))}"
                f"·14% 初始保证金 {_fmt_cny(r.get('initial_margin_cny'))}"
                f"·保证金臂首档 {_fmt_cny(r.get('margin_rung_cny'))}")
        if parts_m:
            L.append("  - " + "；".join(parts_m))
        if gap:
            L.append("  - **两把尺子差 "
                     + "、".join(f"{k} {v:.2f}×" for k, v in gap.items())
                     + "**：按保证金口径能开的杠杆是波动预算的这么多倍 —— "
                     "多出来的部分就是这本书故意不用的风险空间")
        worst = [f"{k} {r.get('worst_intraday_pct'):.2f}%"
                 for k, r in rows_m.items() if r.get("worst_intraday_pct") is not None]
        if worst:
            L.append("  - 追缴不是这条线的风险：四个品种历史最差盘中（"
                     + "、".join(worst) + "）离追缴线还差一个数量级")
        L.append(f"  - 出处：`{cm.get('path')}`｜generated {cm.get('source_generated')}"
                 f"｜cutoff {cm.get('evidence_cutoff')}"
                 "｜保证金率=规则参数扫描（非本书测度）")
    # r1820: every number above is priced at the exchange document floor (1.5bp per
    # roll).  The repo measures that seam now and the median is 20-31bp, so the gap
    # this sleeve leaves behind is 1.5-2.4pp/yr smaller than the page implied.
    cr = p.get("carry_roll_cost") or {}
    if not cr.get("present"):
        L.append(f"- 换月成本：{cr.get('note') or '换月成本面未产出'}"
                 f"（指针 `{cr.get('path')}`）——**今天读不到换月成本，"
                 "上面那些差距只按交易所文件底 1.5bp/次计**")
    else:
        rows_r = cr.get("rows") or {}

        def _bp(code):
            v = (rows_r.get(code) or {}).get("median_bp")
            return None if v is None else float(v)

        meds = [f"{c} {_bp(c):.1f}bp" for c in ("IC", "IM", "IF", "IH")
                if _bp(c) is not None]
        drags = [f"{c} {rows_r[c]['drag_measured_pp']:.2f}pp/年"
                 for c in ("IC", "IM", "IF", "IH")
                 if (rows_r.get(c) or {}).get("drag_measured_pp") is not None]
        L.append("- **换月不是免费的**（`%s`）：桌面上一直按交易所文件底 **1.5bp/次** 计"
                 "（手续费＋一个最小变动价），而本仓从各合约自己的日高/日低量出来的中位数是 "
                 "**%s** —— 差一个数量级；按各自换月次数折成每年：**%s**"
                 % (cr.get("path"), "、".join(meds), "、".join(drags)))
        gaps_r = []
        for c in ("IC", "IM", "IF"):
            r = rows_r.get(c) or {}
            f0, m0 = r.get("gap_floor_pp"), r.get("gap_measured_pp")
            if f0 is None or m0 is None:
                continue
            gaps_r.append(f"{c} {f0:.2f} → {m0:.2f}pp")
        if gaps_r:
            L.append("  - 这条袖面与这本书的差距（前面是文件底、后面是实测中位）："
                     + "、".join(gaps_r)
                     + " —— 判决不改（IC/IM 仍进、IF/IH 仍不进），"
                     "改的是「差距有多大」这件事本身")
        L.append("  - 诚实一条：实测中位来自**日高/日低估计量**（Corwin-Schultz），"
                 "它读的是当日振幅而不是报价带，所以高的一头会饱和；"
                 "文件底与实测中位是两种口径，**不相加、不平均**，"
                 "要一个确定数必须有一条报价带")
        L.append(f"  - 出处：`{cr.get('path')}`｜generated {cr.get('source_generated')}"
                 f"｜cutoff {cr.get('evidence_cutoff')}")
    # r1845: everything above reads marks the carry book has published.  The book is
    # append-only, so a bar stays published even when the panel behind it no longer
    # holds the row -- printed here, not discovered later.
    ck = p.get("carry_marks") or {}
    if not ck.get("present"):
        L.append(f"- 账面最后一根 bar 有没有报价撑着：{ck.get('note') or '支撑面未产出'}"
                 f"（指针 `{ck.get('path')}`）——**今天读不到，上面账面的 P&L 无法核对是否还有行情在后面**")
    else:
        rows_k = ck.get("rows") or {}
        tot = ck.get("totals") or {}
        n_un = int(tot.get("unbacked_bars") or 0)
        if n_un == 0:
            L.append("- 账面每一根 bar 都在合约盘上找得到（`%s`）：前向 P&L 的每个收盘价"
                     "都能被盘上的报价重算——这是少见的干净状态，不是沉默"
                     % ck.get("path"))
        else:
            bits_k = []
            for c in sorted(rows_k):
                r = rows_k[c] or {}
                for u in (r.get("unbacked") or []):
                    bits_k.append("%s %s 的 %s 收盘 %s（%s）"
                                  % (c, u.get("contract"), u.get("date"),
                                     u.get("close"),
                                     "等于当日主力连续收盘" if u.get("cause") == "matches_continuous"
                                     else "盘上没有任何面能给出这个数"))
            L.append("- **账面有 %d 根 bar 在合约盘上找不到报价**（`%s`）：%s。"
                     "这些价格不是错数，是「证据不在盘上」——账本只追加不回收，所以它们会一直在，"
                     "而它撑着 **¥%s** 的绝对盈亏"
                     % (n_un, ck.get("path"), "；".join(bits_k),
                        _fmt_cny(abs(float(tot.get("unbacked_abs_pnl_cny") or 0.0)))))
            L.append("  - 两种读法都成立、这张盘分不出来：要么那天合约真报了这个价而盘上后来丢了行，"
                     "要么这根 bar 是从主力连续盘抄来的、挂在了合约的名字下。"
                     "各自要的证据不同（前者要一次补采，后者要一次记账订正），**不猜**")
            L.append("  - 盘上文件落盘时间：" + "、".join(
                "%s 最新 %s（%s）" % (c, (rows_k[c] or {}).get("contract"),
                                     (rows_k[c] or {}).get("panel_last"))
                for c in sorted(rows_k)))
        L.append(f"  - 出处：`{ck.get('path')}`｜generated {ck.get('source_generated')}"
                 f"｜cutoff {ck.get('evidence_cutoff')}")
    L.append("")
    L.append("## ⑧ 诚实免责")
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
    check("schema v1.9", p1["schema"] == "ceo_live_usage_v1_9")
    # --- r1579: a lagging panel must name WHY it lags (asked and empty), and
    # the kill-day rule must not run across two sessions.
    check("zt lag cause names the asked-and-empty days",
          _zt_lag_cause({"cutoff": "2026-11-09",
                         "asked_through": "2026-11-11",
                         "empty_days": ["2026-11-10", "2026-11-11"]})
          == "（11-10、11-11 已问·当日零行）")
    check("zt lag cause silent when rows reach the ledger",
          _zt_lag_cause({"cutoff": "2026-11-11",
                         "asked_through": "2026-11-11"}) == "")
    check("zt lag cause does not invent a reason",
          "未记明原因" in _zt_lag_cause({"cutoff": "2026-11-09",
                                        "asked_through": "2026-11-11",
                                        "empty_days": []}))
    _p = json.loads(json.dumps(p1))
    _p["risk_tape"] = {
        "status": "ok", "cutoff": "2026-11-11", "aligned": False,
        "kill_day": None,
        "kill_day_unavailable": {"zt_cutoff": "2026-11-11",
                                 "dtgc_cutoff": "2026-11-09",
                                 "note": "两池不在同一交易日（涨停池 "
                                         "2026-11-11、跌停池 2026-11-09）"},
        "panels": {
            "zt": {"label": "涨停池", "status": "ok", "count": 85,
                   "cutoff": "2026-11-11", "delta": None,
                   "asked_through": "2026-11-11", "empty_days": []},
            "dtgc": {"label": "跌停池", "status": "ok", "count": 1,
                     "cutoff": "2026-11-09", "delta": None,
                     "asked_through": "2026-11-11",
                     "empty_days": ["2026-11-10", "2026-11-11"]}}}
    _md = render_md(_p)
    check("kill-day rule refuses across two sessions (r1579)",
          "未判" in _md and "11-10、11-11 已问·当日零行" in _md)

    # --- r1580: one page, two books.  The ⑥ track record is the 12-name vol
    # book; the desk is handed a 5-name beta sheet at half the exposure.  A
    # page that never names either lets "follow the page" mean two portfolios.
    bi = p1.get("book_identity") or {}
    check("book-identity face on the real faces (r1580)",
          bi.get("verdict") in {"SAME_BOOK", "DIFFERENT_BOOKS",
                                "NOT_COMPARABLE", "UNKNOWN"}
          and "这一页写的是哪本书（r1580）" in _md)
    # --- r1784: the executable sheet itself is on the page. The ledger line
    # answers "how has the book done"; until now nothing answered "what would
    # following it cost me tomorrow morning".  Assert the rows are the face's
    # own rows (lots x 100 == shares, one line per code) and that a missing
    # ticket prints a reason instead of a zero.
    _md_o = render_md(p1)
    _eo = p1.get("etf_order") or {}
    if _eo.get("present"):
        _rows_o = _eo.get("rows") or []
        check("order sheet: one line per code, lots x 100 == shares (r1784)",
              len(_rows_o) == _eo.get("n")
              and all(r.get("lots") is not None
                      and r.get("shares") == r["lots"] * 100
                      for r in _rows_o)
              and all(r["symbol"] in _md_o for r in _rows_o))
        check("order sheet: cash left == NAV - sum(amounts) (r1784)",
              _eo.get("nav_cny") is None
              or abs((_eo["spent_cny"] + _eo["cash_left_cny"])
                     - _eo["nav_cny"]) < 1.0)
        check("order sheet: the page names the decision bar and the trip",
              str(_eo.get("decision_bar")) in _md_o)
        # --- r1785: the delta a returning reader has to trade.  The sheet
        # above is a full build; a reader who already followed an earlier
        # sheet must not be told to buy the whole book again.  Three legs:
        # the rows are the face's own, the cash chain closes, and a real
        # "nothing to do" never shares wording with "could not read".
        _eod = _eo.get("delta") or {}
        if _eod.get("present"):
            check("delta: page carries every face row, one per code (r1785)",
                  all(r["symbol"] in _md_o for r in _eod.get("rows") or [])
                  and len(_eod.get("rows") or [])
                  == len(_eod.get("sells") or []) + len(_eod.get("buys") or []))
            _cb0 = _eod.get("cash_before_cny")
            _ca0 = _eod.get("cash_after_cny")
            _gs0 = _eod.get("gross_sell_cny") or 0.0
            _gb0 = _eod.get("gross_buy_cny") or 0.0
            check("delta: cash chain closes (before - buys + sells == after)",
                  _cb0 is None or _ca0 is None
                  or abs((_cb0 - _gb0 + _gs0) - _ca0) < 1.0)
            # r1785: the printed direction must follow the two cash numbers.
            # The producer's net_cash_cny is positive when cash FALLS, so a
            # page that reads it as a signed change prints an outflow as "+".
            if _cb0 is not None and _ca0 is not None:
                _want = "净减" if _ca0 < _cb0 else "净增"
                check("delta: money direction follows the cash numbers (r1785)",
                      _want in _md_o
                      and ("净增" if _want == "净减" else "净减") not in _md_o)
            _rows_sum = sum(abs(r.get("delta_lots") or 0)
                            for r in _eod.get("rows") or [])
            check("delta: lots moved is the face's own sum, not a recount",
                  _rows_sum == 0 or _eod.get("rows"))
            if _eod.get("declaration_status", "").startswith("UNEXPLAINED"):
                check("delta: an unexplained target move reaches the page (r1785)",
                      "目标动过" in _md_o)
        else:
            check("delta: absent face never reads as 'nothing to do' (r1785)",
                  "缺面不读 0" in _md_o and "不需要下单" not in _md_o)
        _pz = json.loads(json.dumps(p1))
        _pz["etf_order"]["delta"].update({
            "present": True, "verdict": "ALREADY_ON_TARGET",
            "verdict_cn": _ETF_DELTA_VERDICTS["ALREADY_ON_TARGET"],
            "no_action": True, "executable": False})
        _mdz = render_md(_pz)
        check("delta: ALREADY_ON_TARGET prints a real zero, not a blank (r1785)",
              "不需要下单" in _mdz and "不给买卖手数" not in _mdz)
        _pz2 = json.loads(json.dumps(p1))
        _pz2["etf_order"]["delta"].update({
            "present": True, "verdict": "UNPRICED",
            "verdict_cn": _ETF_DELTA_VERDICTS["UNPRICED"],
            "no_action": False, "executable": False})
        _mdz2 = render_md(_pz2)
        check("delta: an unreadable sheet refuses lots instead of printing 0 (r1785)",
              "不给买卖手数" in _mdz2 and "不需要下单" not in _mdz2)
        _pz3 = json.loads(json.dumps(p1))
        _pz3["etf_order"]["delta"] = {"present": False,
                                      "note": "换仓差量面未产出（缺面不读 0 手）"}
        _mdz3 = render_md(_pz3)
        check("delta: missing face and real zero never share a sentence (r1785)",
              "缺面不读 0" in _mdz3 and "不需要下单" not in _mdz3)
    else:
        check("order sheet: absent face never renders as a zero (r1784)",
              "缺面不读 0" in _md_o or "不读 0" in _md_o)
    _led = {"config": {"n_hold": 12, "vol_target": 0.08},
            "book_in_force": {"bar": "2026-11-11", "scale": 0.909384,
                              "names": ["a", "b", "c"]},
            "pending_fill": {"capital_cny": 1000000.0}}
    _tmp = tempfile.mkdtemp(prefix="bi1580_")
    _sheet = {"as_of": "2026-11-11", "n_hold": 4, "beta_target": 0.2,
              "ticket": {"book_weight": 0.432195,
                         "order": [{"symbol": s}
                                   for s in ("a", "b", "c", "d")],
                         "book_amount": 431696.8, "cash_amount": 568303.2}}
    with open(os.path.join(_tmp, "TICKET-2026-11-11.json"), "w",
              encoding="utf-8") as fh:
        json.dump(_sheet, fh)
    _latest = os.path.join(_tmp, "latest.json")
    with open(_latest, "w", encoding="utf-8") as fh:
        json.dump({"as_of": "2026-11-11", "file": "TICKET-2026-11-11.json",
                   "k_now": 0.432195}, fh)
    two = _book_identity_face(ledger=_led, latest_path=_latest)
    check("two different books are named, not merged (r1580)",
          two["verdict"] == "DIFFERENT_BOOKS" and two["same_book"] is False
          and two["names_overlap"] == 3
          and abs(two["scale_gap_pp"] - 47.72) < 0.01
          and abs(two["scale_gap_cny"] - 477189.0) < 1.0)
    _md2 = "\n".join(_book_identity_lines(two))
    check("the page prints both books with their own ks (r1580)",
          "0.909384" in _md2 and "0.432195" in _md2
          and "不是同一本" in _md2 and "47.72" in _md2)
    miss = _book_identity_face(ledger=_led,
                               latest_path=os.path.join(_tmp, "nope.json"))
    _md4 = "\n".join(_book_identity_lines(miss))
    check("a missing ticket is UNKNOWN, never 'same book' (r1580)",
          miss["verdict"] == "UNKNOWN" and miss["same_book"] is None
          and "同一本——" not in _md4 and "不可读" in _md4)
    _led2 = json.loads(json.dumps(_led))
    _led2["book_in_force"]["bar"] = "2026-11-10"
    nc = _book_identity_face(ledger=_led2, latest_path=_latest)
    _md3 = "\n".join(_book_identity_lines(nc))
    check("different decision bars are not compared (r1580)",
          nc["verdict"] == "NOT_COMPARABLE" and nc["comparable"] is False
          and "2026-11-10" in _md3 and "2026-11-11" in _md3)
    _sheet2 = json.loads(json.dumps(_sheet))
    _sheet2["n_hold"] = 2
    _sheet2["ticket"]["order"] = [{"symbol": s} for s in ("a", "b")]
    _sheet2["ticket"]["book_weight"] = 0.432195
    with open(os.path.join(_tmp, "TICKET-2026-11-11.json"), "w",
              encoding="utf-8") as fh:
        json.dump(_sheet2, fh)
    same = _book_identity_face(
        ledger={"config": {"n_hold": 2, "vol_target": None},
                "book_in_force": {"bar": "2026-11-11", "scale": 0.432195,
                                  "names": ["a", "b"]}},
        latest_path=_latest)
    check("one book on both sides says so (r1580)",
          same["verdict"] == "SAME_BOOK" and same["same_book"] is True
          and same["names_overlap"] == 2)
    rc = p1["recommendation"]
    check("recommendation face wired (v1.6)",
          rc["path"].endswith("REC-latest.json")
          and (not rc["present"]
               or (bool(rc["recommendation"]) and bool(rc["basis"])
                   and isinstance(rc["n_holdings"], int)
                   and rc["n_holdings"] == len(rc["codes"])
                   and isinstance(rc["sha16"], str)
                   and len(rc["sha16"]) == 16)))
    deg = json.loads(json.dumps(p1))
    deg["recommendation"] = {"present": False, "path": REC_REL,
                             "note": "研究面未生成=诚实缺省"}
    try:
        deg_md = render_md(deg)
        check("recommendation absent-face degrades honestly (no raise)",
              "诚实缺省" in deg_md and "④ 决策链版本横幅" in deg_md)
    except Exception as exc:                                 # noqa: BLE001
        print(f"  degrade render raised: {exc}")
        check("recommendation absent-face degrades honestly (no raise)",
              False)
    jb = p1["judgment_burns"]
    check("judgment-burn face present (v1.5)",
          jb["feed"].startswith("results/fund_*_p1/nulls.jsonl")
          and jb["finalize_gate"].endswith("（预注册冻结硬门）")
          and jb["target"] == 2000
          and [r["family"] for r in jb["families"]]
          == [f for f, _ in FUND_NULLS_FACES])
    check("judgment-burn counters honest-shaped (v1.5)",
          all(0 <= r["have"] <= r["target"] and r["dup_k"] == 0
              and r["dup_k"] <= r["have"]
              for r in jb["families"]))
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
    wf1 = p1.get("weight_face")
    md1_pre = render_md(p1)
    check("member weight sum names its own base (six of a wider face)",
          (wf1 is not None
           and abs(wf1["six_sum"] - round(sum(m["b_maxdiv_weight"]
                                              for m in p1["members"]), 6)) < 5e-7
           and (abs(wf1["six_sum"] - 1.0) < 0.005
                or ("不是一块饼" in md1_pre
                    and "相加不等于 100%" in md1_pre)))
          or (wf1 is None and "权重面读不到" in md1_pre))
    check("weight face sums to its own published total (not assumed 1.0)",
          wf1 is not None
          and abs(wf1["face_sum"] - wf1["six_sum"] - wf1["others_sum"]) < 1e-5
          and abs(wf1["face_sum"] - 1.0) < 0.005)
    _p_nw = dict(p1)
    _p_nw["weight_face"] = None
    _md_nw = render_md(_p_nw)
    check("missing weight face prints no percentage and no zero",
          "权重面读不到" in _md_nw
          and "六员只占 0.00%" not in _md_nw
          and "不是一块饼" not in _md_nw)
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
    check("all blocks in md",
          all(k in md1 for k in ("① 市场判定", "② 仓位指令",
                                 "③ 六员分配", "④ 决策链版本横幅",
                                 "⑤ 在飞判决批", "⑥ ETF 复合书",
                                 "⑦ 指数期货 carry 书",
                                 "⑧ 诚实免责")))
    fr = p1.get("freshness") or {}
    check("freshness banner rendered in md (v2.1)",
          "本页新鲜度" in md1 and fr.get("status") == "ok"
          and bool(fr.get("rows")))
    days_fr, exp_fr = _calendar_yardstick()
    check("freshness yardstick is the official calendar, not a panel",
          exp_fr == fr.get("expected_bar")
          and fr.get("calendar_last") == days_fr[-1])
    _ok_owed = True
    for r in fr.get("rows") or []:
        c, o = r.get("cutoff"), r.get("owed_sessions")
        if c and fr.get("expected_bar") and o is not None:
            _ok_owed &= (o == len({d for d in days_fr
                                   if c < d <= fr["expected_bar"]}))
        elif not c:
            _ok_owed &= (o is None)
    check("owed sessions equals a second count (set arithmetic)", _ok_owed)
    check("a face sitting on the yardstick owes zero, not one",
          owed_sessions(exp_fr, exp_fr, days_fr) == 0)
    _unread_md = "\n".join(_freshness_lines(
        {"status": "ok", "expected_bar": exp_fr, "calendar_last": days_fr[-1],
         "rows": [{"face": "x", "label": "X", "cutoff": None,
                   "owed_sessions": None, "state": "unreadable"}],
         "worst_face": None, "worst_owed_sessions": 0, "unreadable": ["X"]}))
    check("a face with no cutoff reads unreadable, never 0",
          owed_sessions(None, exp_fr, days_fr) is None
          and "无法核实" in _unread_md and "全部面都追到" not in _unread_md)
    check("the banner names the oldest face and its debt",
          ("全部面都追到" in md1) if not fr.get("worst_face")
          else (fr["worst_face"] in md1
                and str(fr["worst_owed_sessions"]) in md1))
    check("judgment-burn block rendered in md (v1.5)",
          "在飞判决批（NULLS 烧录进度·纯计数）" in md1
          and "FUND-QUALITY-P1" in md1 and "dup_k=0" in md1)
    eb = p1.get("etf_book") or {}
    check("etf-book forward record rendered in md (v2.0)",
          "ETF 复合书 · 前向实绩" in md1
          and (not eb.get("present")
               or (f"{eb['book_nav']:.6f}" in md1
                   and "还不能下结论" in md1)))
    if eb.get("present"):
        check("etf-book excess is the excess of its own two curves",
              abs(eb["excess_bp"]
                  - (eb["book_ret_pct"] - eb["bench_ret_pct"]) * 100.0)
              <= 0.3)
        check("etf-book bar count equals the ledger it read",
              eb["n_bars"]
              == len((_read_json(ETF_BOOK_FWD) or {}).get("bars") or []))
        # the benchmark rows carry no dd field; a drawdown of 0.000% printed
        # for a series that actually fell is a fabricated measurement, not a
        # missing one (r1261 family)
        check("etf-book benchmark drawdown is measured, not printed as zero",
              eb["bench_ret_pct"] is None or eb["bench_ret_pct"] >= 0
              or (eb["bench_max_dd_pct"] is not None
                  and eb["bench_max_dd_pct"] < 0))
    # --- v2.2 (r1782): the second money candidate's funding line.
    cb = p1.get("carry_book") or {}
    check("carry funding line rendered in md (v2.2)",
          "指数期货 carry 书 · 开仓资金线" in md1
          and (not cb.get("present")
               or (bool(cb.get("decision")) and cb["decision"] in md1
                   and _fmt_cny(cb["cheapest_cny"]) in md1)))
    if cb.get("present"):
        # r1781: this section is fed by another script, so it must print that
        # script's own stamp -- a face rewritten on the next trip must show up
        # as an older timestamp here, never as a silently fresher sentence.
        check("the carry section self-stamps its source",
              cb["source_generated"] in md1
              and cb["evidence_cutoff"] in md1)
        _cba = (cb.get("accounts") or {})
        check("executable lots are the ruler's lots, per account",
              bool(_cba) and all(a.get("executable_lots") == a.get("lots")
                                 for a in _cba.values()))
        check("the funding line is the shortfall to the first rung",
              all(abs(a["gap_cny"] - (a["first_rung_cny"] - a["capital_cny"]))
                  < 0.01 for a in _cba.values()))
        check("the withdrawn desk lots are printed as kept, not erased",
              cb.get("paper_lots_total") is not None
              and (cb.get("paper_label") or "") in md1
              and "不删不改" in md1)
    _cb_miss = dict(p1)
    _cb_miss["carry_book"] = {"present": False, "path": CARRY_OPEN_REL,
                              "note": "资金线面未产出（缺面不读 0）"}
    _mmd = render_md(_cb_miss)
    check("a missing carry face never reads as zero lots",
          "资金线面未产出" in _mmd and "可执行 **0 手**" not in _mmd)
    check("national-team row rendered in md",
          "国家队状态" in md1 and "T-106" in md1
          and "宇宙面注记" in md1 and "跟队信号面" in md1)
    check("clock + full-heat-tier rows rendered in md",
          "市场时钟" in md1 and "满热档判定" in md1
          and ("GREEN×HOT 满热档生效" in md1
               or "满热档未触发" in md1))
    check("intraday block rendered in md (v1.4)",
          "盘中档（T-104 分钟源·v1.4）" in md1)
    check("recommendation block rendered in md (v1.6)",
          "配置参考（研究面·v1.6 接线·零新判据）" in md1
          and (not rc["present"]
               or (rc["recommendation"][:12] in md1
                   and "全页指针" in md1)))
    ru = p1["rollup"]
    check("roll-up present and complete (v1.7)",
          ru["n_traders"] == len(SIX) and ru["initial_cny"] > 0
          and ru["equity_cny"] > 0)
    check("roll-up arithmetic is self-consistent (v1.7)",
          abs(ru["pnl_cny"] - (ru["equity_cny"] - ru["initial_cny"])) <= 0.05
          and abs(ru["return_pct"]
                  - (ru["equity_cny"] / ru["initial_cny"] - 1.0) * 100.0)
          <= 1e-3
          and abs(ru["positions_cny"] + ru["cash_cny"]
                  - ru["equity_cny"]) <= 0.05 * ru["n_traders"])
    _mem_sum = sum(m["equity_cny"] for m in p1["members"])
    _mem_cash = sum(m["cash_cny"] for m in p1["members"])
    check("roll-up equals the sum of its own member rows",
          abs(ru["equity_cny"] - _mem_sum) <= 0.5 * ru["n_traders"]
          and abs(ru["cash_cny"] - _mem_cash) <= 0.5 * ru["n_traders"])
    check("roll-up agrees with the export summary face (cross-face)",
          ru["face_agrees"] is True)
    _pd, _pe = _prior_export_equity(day)
    check("prior-export selector is strictly older than the day",
          (_pd is None or _pd < day) and _pd == ru["day_prior"])
    check("day change is derived or honestly absent, never 0",
          (ru["day_pnl_cny"] is None
           and ru["day_prior"] is None
           and "无对照件" in md1)
          or (ru["day_pnl_cny"] is not None
              and abs(ru["day_pnl_cny"]
                      - (ru["equity_cny"] - ru["day_prior_equity_cny"]))
              <= 0.05
              and ru["day_prior"] in md1))
    check("no prior export -> None, never an invented zero",
          _prior_export_equity("1990-01-01") == (None, None))
    _deg_ru = {"return_pct": None}
    _deg_p = dict(p1)
    _deg_p["rollup"] = _deg_ru
    try:
        _deg_md = render_md(_deg_p)
        check("absent starting capital degrades honestly (no raise)",
              "口径缺件" in _deg_md and "④ 决策链版本横幅" in _deg_md)
    except Exception as exc:                                     # noqa: BLE001
        print(f"  roll-up degrade render raised: {exc}")
        check("absent starting capital degrades honestly (no raise)", False)
    check("roll-up rendered in md with its own money (v1.7)",
          "六员合计" in md1 and _fmt_cny(ru["equity_cny"]) in md1
          and f"{ru['return_pct']:+.2f}%" in md1)
    # ---- v1.8: market risk tape (single implementation, honest absence) ----
    rt = p1["risk_tape"]
    tape_ok = rt.get("status") == "ok"
    shape_ok = True
    for _k, _v in (rt.get("panels") or {}).items():
        if _v.get("count") is not None and not isinstance(_v["count"], int):
            shape_ok = False
        if _v.get("status") == "ok" and _v.get("count") is None:
            shape_ok = False
    check("risk tape present and honestly shaped (v1.8)",
          rt.get("status") in ("ok", "absent", "unavailable", "unreadable")
          and shape_ok
          and (not tape_ok
               or (isinstance(rt.get("cutoff"), str)
                   and len(rt["cutoff"]) == 10
                   and (rt.get("seal_rate") is None
                        or 0.0 <= rt["seal_rate"] <= 1.0))))
    _tmp_rt = tempfile.mkdtemp(prefix="ceo_rt_empty_")
    _absent = _risk_tape_face(root=_tmp_rt)
    check("risk tape: absent panels read absent, never 0 members (v1.8)",
          _absent.get("status") == "absent"
          and all((v or {}).get("count") is None
                  for v in (_absent.get("panels") or {}).values()))
    _rep = os.path.join(REPORT_DIR, f"REPORT-{day}.md")
    if os.path.exists(_rep):
        with open(_rep, encoding="utf-8") as _fh:
            _txt = _fh.read()
        _got = {m.group(1): int(m.group(2)) for m in
                re.finditer(r"\*\*(涨停池|跌停池|炸板池|强势池) (\d+)\*\*", _txt)}
        _want = {}
        for _k, _lab in (("zt", "涨停池"), ("dtgc", "跌停池"),
                         ("zbgc", "炸板池"), ("strong", "强势池")):
            _v = (rt.get("panels") or {}).get(_k) or {}
            if _v.get("count") is not None:
                _want[_lab] = _v["count"]
        _cut = re.search(r"四面同为 \*\*(\d{4}-\d{2}-\d{2})\*\*", _txt)
        _par_ok = (_got == _want)
        if _cut and tape_ok:
            _par_ok = _par_ok and (_cut.group(1) == rt.get("cutoff"))
        check("risk tape agrees with daily report §九 (cross-face parity)",
              _par_ok)
    else:
        print(f"  [SKIP] cross-face parity: {os.path.basename(_rep)} "
              "not generated for today (absent, not 0)")
    check("risk tape rendered in md (v1.8)",
          "市场风险面" in md1
          and (not tape_ok or str(rt.get("cutoff")) in md1))
    # ---- r1786: the sheet leaves 56.8% in cash and the page now says what that
    # cash earns.  Three things it must never do: fold the rate into the track
    # record above (the ledger's own cash leg earns 0), print ¥0 when the rate
    # face is absent, or read an unknown next-decision as 0 bars.
    _eo1 = p1.get("etf_order") or {}
    _cl1 = _eo1.get("cash_leg") or {}
    if not _eo1.get("present") or not _cl1.get("bands"):
        print("  [SKIP] cash leg: the sheet or its rate face is absent")
    else:
        _hd1 = (_cl1.get("bands") or {}).get(_cl1.get("headline")) or {}
        check("the page prices the cash it leaves behind, as a rate not a return",
              _hd1.get("net_annual_cny") is not None
              and _fmt_cny(_hd1.get("net_annual_cny")) in md1
              and "不并进上面的净值" in md1
              and "现金腿按 0 计息" in md1)
        _deg2 = json.loads(json.dumps(p1))
        _deg2["etf_order"] = dict(_deg2.get("etf_order") or {})
        _deg2["etf_order"]["cash_leg"] = None
        _md2 = render_md(_deg2)
        check("a missing rate face prints a reason, never ¥0 (r1786)",
              "票面未印（缺面不读 0）" in _md2
              and _fmt_cny(_hd1.get("net_annual_cny") or 0) not in _md2)
        _nd1 = _eo1.get("next_decision_bars")
        check("the page says when the sheet changes again (r1786)",
              (_nd1 is None and "票面未印（缺面不读 0）" in md1)
              or (isinstance(_nd1, int)
                  and "下一次决策还有 **{} 个 bar**".format(_nd1) in md1))
        # r1825: "16 bars" is not a date -- the sheet's own next-decision face
        # signs it three ways, and the page must read that instead of converting.
        _nfd1 = _eo1.get("next_decision_face") or {}
        if not _nfd1.get("present") or not _nfd1.get("date"):
            print("  [SKIP] next-decision date: the face is absent")
        else:
            check("the bar count reaches the page as the calendar date it is (r1825)",
                  _nfd1.get("agrees") is True
                  and "换成日历日期就是 **{}**".format(_nfd1["date"]) in md1)
            _deg5 = json.loads(json.dumps(p1))
            _f5 = dict(_deg5["etf_order"]["next_decision_face"])
            _f5.update({"agrees": False, "verdict": "SPLIT",
                        "wrong_claims": ["cut_permission"],
                        "off_grid_claims": []})
            _deg5["etf_order"]["next_decision_face"] = _f5
            _md5 = render_md(_deg5)
            check("a face whose own signatures split prints no date (r1825)",
                  "今天不印" in _md5 and "cut_permission" in _md5
                  and "换成日历日期就是" not in _md5)
            _deg6 = json.loads(json.dumps(p1))
            _deg6["etf_order"]["next_decision_face"] = {
                "present": False, "note": "票面未带下次决策面（缺面不读 0）"}
            _md6 = render_md(_deg6)
            check("a missing next-decision face prints a reason, not a guess (r1825)",
                  "换成日历日期：票面未带下次决策面" in _md6
                  and "换成日历日期就是" not in _md6)
            _deg7 = json.loads(json.dumps(p1))
            _f7 = dict(_deg7["etf_order"]["next_decision_face"])
            _f7["bars_away"] = (0 if _nfd1.get("bars_away") is None
                                else int(_nfd1["bars_away"]) + 3)
            _deg7["etf_order"]["next_decision_face"] = _f7
            _md7 = render_md(_deg7)
            check("a date contradicting the ticket's own bar count prints neither (r1825)",
                  "今天不印" in _md7 and "两个数总有一个是陈的" in _md7)
        # ---- r1826: the order's own size against the market's turnover.  Three legs:
        # the measured reading and the capital ceiling reach the page; the block states
        # that the face was measured at the full lens, not at today's smaller order;
        # and a missing / other-session face prints a reason and NO number.
        _cp1 = p1.get("etf_capacity") or {}
        if not _cp1.get("present") or _cp1.get("reading_today_pct") is None:
            print("  [SKIP] capacity block: the face is absent")
        else:
            _crd1 = _cp1.get("reading_today_pct")
            check("the order's own share of market turnover reaches the page (r1826)",
                  "这单装得进市场吗" in md1
                  and "{:.4f}%".format(_crd1) in md1
                  and str(_cp1.get("binding_today") or "?") in md1)
            _ccap1 = _cp1.get("capital_at_line_cny")
            check("the capital ceiling at the line is quoted, never recomputed (r1826)",
                  _ccap1 is not None and _fmt_cny(_ccap1) in md1
                  and _fmt_cny(_cp1.get("capital_median_cny")) in md1)
            _csz1 = p1.get("etf_capacity_at_size") or {}
            _csc1 = "同规模容量面未产出"
            if _csz1.get("present") and _csz1.get("reading_pct") is not None:
                # r1827: the block now measures the ticket's own names at its own size,
                # so the r1826 "never measured at this size" sentence must be gone.
                check("the order is measured on its own names at its own size (r1827)",
                      "本单**自己的名字与金额**" in md1
                      and "{:.4f}%".format(_csz1.get("reading_pct")) in md1
                      and str(_csz1.get("binding") or "?") in md1)
                check("the r1826 'never measured at this size' refusal is retired (r1827)",
                      "没有在 {:.1f}% 这个规模上重量".format(
                          float((_eo1.get("book_weight") or 0.0)) * 100.0) not in md1)
                _csns1 = _csz1.get("name_set") or {}
                if _csns1.get("same_book") is False:
                    check("a reading on another five names is named as another book (r1827)",
                          "另一组名字" in md1
                          and str(_csns1.get("n_overlap")) not in ("", "None"))
                _degs = json.loads(json.dumps(p1))
                _degs["etf_capacity_at_size"] = {"present": False,
                                                 "note": "同规模容量面未产出（缺面不读 0）"}
                _mds = render_md(_degs)
                check("a missing at-size face falls back to the refusal, not a number (r1827)",
                      "只印它量过的那个规模" in _mds
                      and "{:.4f}%".format(_csz1.get("reading_pct")) not in _mds)
                _degq = json.loads(json.dumps(p1))
                _cq = dict(_degq.get("etf_capacity_at_size") or {})
                _cq["bar"] = "1999-01-01"
                _degq["etf_capacity_at_size"] = _cq
                _mdq = render_md(_degq)
                check("an at-size face on another bar is refused, not quoted (r1827)",
                      "不是同一天" in _mdq
                      and "{:.4f}%".format(_csz1.get("reading_pct")) not in _mdq)
                # r1830: same day, same bar, DIFFERENT ticket -- the shape a new sheet
                # landing under an unwritten face makes.  Both directions pinned: the
                # foreign ticket must be refused by name, and the same ticket still reads.
                _degt = json.loads(json.dumps(p1))
                _ct = dict(_degt.get("etf_capacity_at_size") or {})
                _ct["ticket_file"] = "results/etf_book_order/TICKET-1999-01-01.json"
                _degt["etf_capacity_at_size"] = _ct
                _mdt = render_md(_degt)
                check("an at-size face answering another ticket is refused (r1830)",
                      "不是同一张单" in _mdt
                      and "TICKET-1999-01-01" in _mdt
                      and "{:.4f}%".format(_csz1.get("reading_pct")) not in _mdt)
                check("the same ticket still prints its reading (r1830)",
                      "{:.4f}%".format(_csz1.get("reading_pct")) in md1)
            # ---- r1828: the timing half.  A reader holding the action lines must be
            # able to read "today or tomorrow" on the same page, and must not be able to
            # read a cost that was measured on another bar.
            _pw1 = p1.get("etf_punctuality") or {}
            if _pw1.get("present") and _pw1.get("rows"):
                _k1 = next((r for r in _pw1["rows"] if r.get("k") == 1), {})
                check("the page prices doing it today vs waiting a bar (r1828)",
                      "这一档做，还是分开几天做" in md1
                      and "今天做，还是分开几天做" not in md1
                      and "在 {} 这一档做".format(
                          str((p1.get("etf_punctuality") or {}).get("evidence_cutoff")
                              or "")[:10]) in md1
                      and _k1.get("cost_cny") is not None
                      and _fmt_cny(abs(_k1["cost_cny"])) in md1
                      and str(_pw1.get("verdict") or "?") in md1)
                _one1 = _pw1.get("one_open_late") or {}
                check("the single-sheet coin flip is printed beside the mean (r1828)",
                      _one1.get("share_late_helps") is not None
                      and "{:.1f}%".format(float(_one1["share_late_helps"]) * 100.0) in md1
                      and _fmt_cny(abs(_one1.get("median_cny"))) in md1)
                _degp = json.loads(json.dumps(p1))
                _degp["etf_punctuality"] = {"present": False,
                                            "note": "时点面未产出（缺面不读 0）"}
                _mdp = render_md(_degp)
                check("a missing timing face prints a reason, never a cost (r1828)",
                      "今天不印数" in _mdp
                      and _fmt_cny(abs(_k1["cost_cny"])) not in _mdp)
                _degpb = json.loads(json.dumps(p1))
                _pb = dict(_degpb.get("etf_punctuality") or {})
                _pb["evidence_cutoff"] = "1999-01-01"
                _degpb["etf_punctuality"] = _pb
                _mdpb = render_md(_degpb)
                check("a timing face on another bar is refused, not quoted (r1828)",
                      "不是同一天" in _mdpb
                      and _fmt_cny(abs(_k1["cost_cny"])) not in _mdpb)
            # ---- r1829: the gap between the printed close and the open the reader
            # actually pays.  Three legs: the measured band reaches the page in CNY on
            # the ticket's own amount; the block says it is not a cost; another bar's
            # distribution and a missing face both print a reason and no number.
            _og1 = p1.get("etf_open_gap") or {}
            _ogr1 = _og1.get("recent") or {}
            if _og1.get("present") and _ogr1.get("median_bp") is not None:
                _ogband = _fmt_cny(abs((_og1.get("money") or {}).get("band_cny") or 0.0))
                check("the gap between the paid open and the printed close reaches the page (r1829)",
                      "开盘价和票面价隔多远" in md1
                      and "{:+.1f}bp".format(float(_ogr1["median_bp"])) in md1
                      and _ogband in md1)
                check("the block says a gap is not a cost and cannot be added (r1829)",
                      "跳空不是成本" in md1 and "不能" in md1
                      and "按同一比例搬家" in md1)
                _degog = json.loads(json.dumps(p1))
                _ogb = dict(_degog.get("etf_open_gap") or {})
                _ogb["evidence_cutoff"] = "1999-01-01"
                _degog["etf_open_gap"] = _ogb
                _mdog = render_md(_degog)
                check("a gap face on another bar is refused, not quoted (r1829)",
                      "不是同一天" in _mdog and _ogband not in _mdog)
                _degog2 = json.loads(json.dumps(p1))
                _degog2["etf_open_gap"] = {"present": False,
                                           "note": "开盘间隔面未产出（缺面不读 0）"}
                _mdog2 = render_md(_degog2)
                check("a missing gap face prints the caveat's reason, never a number (r1829)",
                      "今天没有量过" in _mdog2 and _ogband not in _mdog2)
            _deg8 = json.loads(json.dumps(p1))
            _deg8["etf_capacity"] = {"present": False,
                                     "note": "容量面未产出（缺面不读 0）"}
            _md8 = render_md(_deg8)
            check("a missing capacity face prints a reason, never a reading (r1826)",
                  "今天不印数" in _md8
                  and "{:.4f}%".format(_crd1) not in _md8
                  and "能过的资本上限" not in _md8)
            _deg9 = json.loads(json.dumps(p1))
            _c9 = dict(_deg9.get("etf_capacity") or {})
            _c9["session"] = "1999-01-01"
            _deg9["etf_capacity"] = _c9
            _md9 = render_md(_deg9)
            check("a capacity face on another session is refused, not quoted (r1826)",
                  "不是同一天" in _md9
                  and "{:.4f}%".format(_crd1) not in _md9
                  and "能过的资本上限" not in _md9)
        # r1787: the money line and the timing line must both be on the page, and
        # the page must say that BOTH are needed -- funding on a day the rule says
        # wait is the mistake this section exists to prevent.
        _ct1 = p1.get("carry_timing") or {}
        check("the carry section carries the entry-timing half (r1787)",
              _ct1.get("present") is True
              and "贴水择时" in md1
              and "分位" in md1
              and "两个条件同时满足才下单" in md1)
        check("the timing band edge is derived from the face, not typed (r1787)",
              _ct1.get("band_edge_pct") is not None
              and "分位 **≤ {}%**".format(_ct1.get("band_edge_pct")) in md1)
        # a missing timing face must NOT read as "not in the band": it must say
        # "I could not read the half, do not fund" (r98: unknown is not zero)
        _deg4 = json.loads(json.dumps(p1))
        _deg4["carry_timing"] = {"present": False, "path": CARRY_TIMING_REL,
                                 "note": "择时面未产出（缺面不读 0）"}
        _md4 = render_md(_deg4)
        check("a missing timing face blocks funding instead of reading as out-of-band (r1787)",
              "时机这一半今天读不到" in _md4 and "不在带内" not in _md4)
        # r1819: the margin arm is the second floor under the same number. Three legs:
        # the verdict reaches the page, the breakeven rate comes off the face (not typed),
        # and a missing margin face says "I could not check the broker's floor" rather
        # than letting the vol ruler stand unexamined.
        _cm1 = p1.get("carry_margin") or {}
        if not _cm1.get("present"):
            print("  [SKIP] carry margin: the face is absent")
        else:
            check("the page says which floor sets the lot (r1819)",
                  _cm1.get("verdict") in md1
                  and ("保证金不是门槛" in md1 or "保证金才是门槛" in md1))
            _beh1 = _cm1.get("breakeven_rate_pct") or {}
            check("the breakeven margin rate is read off the face, never typed (r1819)",
                  bool(_beh1) and all(("%.2f%%" % float(v)) in md1
                                      for v in _beh1.values()))
            _gap1 = _cm1.get("ruler_gap") or {}
            check("the size of the gap between the two rulers reaches the page (r1819)",
                  bool(_gap1) and all("%.2f×" % v in md1 for v in _gap1.values()))
            _deg5 = json.loads(json.dumps(p1))
            _deg5["carry_margin"] = {"present": False, "path": CARRY_MARGIN_REL,
                                     "note": "保证金面未产出（缺面不读 0）"}
            _md5 = render_md(_deg5)
            check("a missing margin face says the funding line was never checked (r1819)",
                  "今天读不到保证金读数" in _md5 and "保证金不是门槛" not in _md5)
        # r1820: the roll charge is the third thing that eats this sleeve, and the page
        # sized the lot on the document floor while the repo had measured the seam.
        _cr1 = p1.get("carry_roll_cost") or {}
        if not _cr1.get("present"):
            print("  [SKIP] carry roll cost: the face is absent")
        else:
            check("the measured roll cost reaches the page beside the document floor (r1820)",
                  "换月不是免费的" in md1 and "1.5bp/次" in md1)
            _rr1 = _cr1.get("rows") or {}
            check("the measured roll median is quoted from the face, never typed (r1820)",
                  bool(_rr1) and all(("%.1fbp" % float(r["median_bp"])) in md1
                                     for r in _rr1.values()
                                     if r.get("median_bp") is not None))
            _deg6 = json.loads(json.dumps(p1))
            _deg6["carry_roll_cost"] = {"present": False, "path": CARRY_RISK_REL,
                                        "note": "换月成本面未产出（缺面不读 0）"}
            _md6 = render_md(_deg6)
            check("a missing roll-cost face says the gap was priced on the floor (r1820)",
                  "今天读不到换月成本" in _md6 and "换月不是免费的" not in _md6)
        # r1845: the carry P&L is printed from an append-only book; the page must say
        # whether the bars under it are still on the contract panel, and must not turn
        # a missing face into either "clean" or a number (r98).
        _ck1 = p1.get("carry_marks") or {}
        if not _ck1.get("present"):
            print("  [SKIP] carry marks: the face is absent")
        else:
            _kt = _ck1.get("totals") or {}
            _nun = int(_kt.get("unbacked_bars") or 0)
            if _nun:
                _uhit = all((u.get("date") or "") in md1 and str(u.get("close")) in md1
                            for r in (_ck1.get("rows") or {}).values()
                            for u in (r.get("unbacked") or []))
                check("unbacked book bars reach the page with their date and close (r1845)",
                      ("账面有 %d 根 bar 在合约盘上找不到报价" % _nun) in md1 and _uhit)
                check("the page refuses to pick between lost-row and spliced-mark (r1845)",
                      "两种读法都成立" in md1 and "不猜" in md1)
            else:
                check("a fully backed book says so instead of staying silent (r1845)",
                      "每一根 bar 都在合约盘上找得到" in md1)
            _deg7 = json.loads(json.dumps(p1))
            _deg7["carry_marks"] = {"present": False, "path": CARRY_MARKS_REL,
                                    "note": "账面报价支撑面未产出（缺面不读 0）"}
            _md7 = render_md(_deg7)
            check("a missing marks face says the P&L cannot be checked, never 0 (r1845)",
                  "今天读不到" in _md7 and "找不到报价" not in _md7)
        # r1820 bm-c: the build order now says what part of it is paid above NAV.  Three
        # legs: the headline money reaches the page; each row's own premium and its own
        # percentile come off the face (never typed); a missing face prints a reason
        # and NO number (r98) -- and the block self-stamps the ticket it priced,
        # because the producer is another script on another trip (r1781).
        _pm1 = p1.get("etf_premium") or {}
        if not _pm1.get("present"):
            print("  [SKIP] premium block: the face is absent")
        else:
            _paid1 = _pm1.get("premium_paid_cny")
            check("the page says what part of the build order is premium (r1820)",
                  "这笔钱里有多少是溢价" in md1
                  and _paid1 is not None
                  and _fmt_cny(abs(_paid1)) in md1
                  and "不是手续费" in md1)
            _row_ok = True
            for _r1 in _pm1.get("rows") or []:
                _p1 = _r1.get("premium_pct")
                if _p1 is None:
                    continue
                if "{:+.2f}%".format(_p1) not in md1:
                    _row_ok = False
            check("every name's own premium reaches the page, in percent not x100 (r1820)",
                  _row_ok)
            _ownset = set(_pm1.get("own_in_top_decile") or [])
            check("the name that sits at its own top decile is labelled so (r1820)",
                  all(("{}｜".format(s) in md1 and "前 10% 高位" in md1)
                      for s in _ownset) if _ownset else True)
            check("the premium block names the ticket and both sessions it read (r1781)",
                  str(_pm1.get("ticket")) in md1
                  and str(_pm1.get("ticket_session")) in md1
                  and str(_pm1.get("iopv_session")) in md1)
            _deg6 = json.loads(json.dumps(p1))
            _deg6["etf_premium"] = {"present": False,
                                    "note": "溢价面未产出（缺面不读 0）"}
            _md6 = render_md(_deg6)
            check("a missing premium face prints a reason, never ¥0 (r1820)",
                  "今天不印数" in _md6
                  and (_paid1 is None or _fmt_cny(abs(_paid1)) not in _md6)
                  and "多付" not in _md6)
            # the same block must refuse to quote a premium priced against a
            # DIFFERENT ticket than the one this page is asking the reader to buy
            _deg7 = json.loads(json.dumps(p1))
            _deg7["etf_premium"] = dict(_deg7.get("etf_premium") or {})
            _deg7["etf_premium"]["ticket"] = "TICKET-1999-01-01.json"
            _md7 = render_md(_deg7)
            check("a premium priced off another ticket is refused, not quoted (r1820)",
                  "不是同一张" in _md7
                  and (_paid1 is None or _fmt_cny(abs(_paid1)) not in _md7)
                  and "多付" not in _md7)
        # ---- r1824: today's repo tenor for the uninvested sleeve
        _cr1 = ((p1.get("etf_order") or {}).get("cash_roll")) or {}
        if _cr1.get("present") and _cr1.get("verdict") != "NO_INSTRUCTION":
            check("the page prints today's repo tenor with its own maturity (r1824)",
                  str(_cr1.get("contract")) in md1
                  and str(_cr1.get("matures")) in md1
                  and str(_cr1.get("decision_date")) in md1)
            check("the worth line is measured against rolling 1-day, not a forecast (r1824)",
                  "比天天滚 GC001" in md1)
            _lk1 = _cr1.get("locked_out") or []
            check("tenors that lock past the decision bar are named, not dropped (r1824)",
                  all(str(r.get("contract")) in md1 and str(r.get("matures")) in md1
                      for r in _lk1) if _lk1 else True)
            _deg8 = json.loads(json.dumps(p1))
            _deg8["etf_order"] = dict(_deg8.get("etf_order") or {})
            _deg8["etf_order"]["cash_roll"] = {
                "present": False, "note": "闲钱滚仓面未产出（缺面不读 0）"}
            _md8 = render_md(_deg8)
            check("a missing roll face prints a reason, never a tenor (r1824)",
                  "缺面不读 0" in _md8 and str(_cr1.get("contract")) not in _md8
                  and "比天天滚 GC001" not in _md8)
            _deg9 = json.loads(json.dumps(p1))
            _deg9["etf_order"] = dict(_deg9.get("etf_order") or {})
            _deg9["etf_order"]["cash_roll"] = {
                "present": True, "verdict": "NO_INSTRUCTION",
                "reason": "repo panel has no GC001 bar"}
            _md9 = render_md(_deg9)
            check("a roll face with no instruction prints its reason, not a tenor (r1824)",
                  "读不到指令" in _md9 and "repo panel has no GC001 bar" in _md9
                  and str(_cr1.get("contract")) not in _md9)
            _mismatch = _etf_cash_roll_face(ticket_bar="TICKET-1999-01-01")
            check("a roll instruction priced off another bar is refused, not quoted (r1824)",
                  not _mismatch.get("present") and "不是同一趟" in str(_mismatch.get("note")))
        _deg3 = json.loads(json.dumps(p1))
        _deg3["etf_order"] = dict(_deg3.get("etf_order") or {})
        _deg3["etf_order"]["next_decision_bars"] = None
        _md3 = render_md(_deg3)
        check("an unknown next decision is not printed as 0 bars (r1786)",
              "下一个 bar 到来" not in _md3
              and "票面未印（缺面不读 0）" in _md3)
        # ---- r1833: the recommendation block hands the reader actual stock codes,
        # and it is a MONTHLY sleeve.  Measured with the daily yardstick an on-time
        # list reads 30 days stale; measured with no yardstick at all, a list that
        # missed its month-start goes on being offered for new positions.  What it
        # is owed is one firing per month-start session.
        _cal33 = ["2026-10-08", "2026-10-09", "2026-10-30",
                  "2026-11-02", "2026-11-03", "2026-12-01"]
        check("a monthly face owes firings, not sessions (r1833)",
              owed_firings("2026-10-08", "2026-11-03", _cal33) == ["2026-11-02"])
        check("a monthly face short of its own month-start is on time (r1833)",
              owed_firings("2026-10-08", "2026-10-30", _cal33) == [])
        check("an unreadable monthly face is never read as on time (r1833)",
              owed_firings(None, "2026-11-03", _cal33) is None)
        _degm = json.loads(json.dumps(p1))
        _fm = dict(_degm.get("freshness") or {})
        _fm["monthly"] = [{"face": "recommendation",
                           "label": "配置参考名单（DIVLOWVOL·月度）",
                           "cutoff": "2026-10-08", "dues": ["2026-11-02"],
                           "owed_firings": 1, "state": "behind"}]
        _degm["freshness"] = _fm
        _mdm = render_md(_degm)
        check("the page says how many firings a monthly list owes (r1833)",
              "欠 1 次调仓" in _mdm and "2026-11-02" in _mdm)
        check("an overdue list is not offered for new positions (r1833)",
              "不要照这份名单新开仓" in _mdm)
        _fm2 = dict(_fm)
        _fm2["monthly"] = [dict(_fm["monthly"][0], dues=[], owed_firings=0,
                                state="current")]
        _degm["freshness"] = _fm2
        _degm["recommendation"] = dict(_degm.get("recommendation") or {},
                                       picks_panel_present=False,
                                       picks_panel="data/cache/p1c_local")
        _mdm2 = render_md(_degm)
        check("a list inside its own monthly rhythm is not called overdue (r1833)",
              "不要照这份名单新开仓" not in _mdm2
              and "在它的月度节律内" in _mdm2)
        check("a list this machine cannot rebuild says so, in words (r1833)",
              "data/cache/p1c_local" in _mdm2 and "不在本机" in _mdm2)
        # ---- r1864: "don't open new positions on this list" and "what holding it was
        # worth" are two different sentences, and a reader who is told only the first
        # has no money on the page.  The track face travels with the list only when it
        # tracks THAT list; a newer list with an older track must print "read it nowhere"
        # instead of borrowing numbers.
        _degm["recommendation"]["track"] = {
            "entry_bar": "2026-10-20", "cutoff": "2026-11-19", "sessions": 23,
            "n_measured": 20, "ret_pct": -1.9533, "bench_n": 4479,
            "bench_ret_pct": -11.2365, "excess_pp": 9.2832}
        _mdm3 = render_md(_degm)
        check("the page prints what the published list earned (r1864)",
              "-1.95%" in _mdm3 and "-11.24%" in _mdm3 and "+9.28pp" in _mdm3)
        check("the record is sourced to the face that produces it (r1864)",
              "results/divlowvol_live/track_latest.json" in _mdm3)
        _degm["recommendation"]["track"] = None
        _mdm4 = render_md(_degm)
        check("a missing record reads as unreadable, not as no money (r1864)",
              "读不到" in _mdm4 and "不借用别份名单的数" in _mdm4)
        check("a track about another list is refused (r1864)",
              _divlowvol_track.__doc__ is not None
              and _divlowvol_track("1999-01-01") is None)
        # ---- r1835: ⑥ names the leg standing at the top decile of its own year and
        # stopped there.  The swap question is priced on another face; the page must
        # print BOTH rulers that answer it (they disagree) and must not print a number
        # when that face priced a different ticket.
        _pc1 = p1.get("etf_premium_choice") or {}
        check("the swap answer reaches the page (r1835)",
              _pc1.get("present") is True
              and _pc1.get("n_stretched", 0) >= 1
              and bool((_pc1.get("stretched") or [{}])[0].get("twin")))
        _mdpc = render_md(p1)
        _leg0 = (_pc1.get("stretched") or [{}])[0]
        check("both rulers are printed, side by side (r1835)",
              "尺子一（年化）" in _mdpc and "尺子二（这本实测只持" in _mdpc
              and "不合并、不替你选" in _mdpc)
        check("the premium is printed as a percent, never rescaled (r1835)",
              "{} 这一腿换不换".format(_leg0.get("symbol")) in _mdpc
              and "{:+.2f}%".format(_leg0.get("premium_pct")) in _mdpc
              and "{:+.2f}%".format((_leg0.get("premium_pct") or 0) * 100)
              not in _mdpc)
        _pcx = json.loads(json.dumps(p1))
        _pcx["etf_premium_choice"] = {"present": False, "note": "换腿面未产出"}
        _mdx = render_md(_pcx)
        check("an unread swap face prints a reason, not a zero (r1835)",
              "换腿面未产出" in _mdx and "今天不印数" in _mdx)
        _pcy = json.loads(json.dumps(p1))
        _pcy["etf_premium_choice"] = dict(_pc1, ticket="TICKET-1999-01-01.json")
        _mdy = render_md(_pcy)
        check("a swap face priced on another ticket is refused (r1835)",
              "不是同一张" in _mdy and "不换**" not in _mdy)
    # ---- r1846: the birth date of the edge must reach the reader ----
    _pp = _read_json(ETF_BOOK_PRE2020) or {}
    _pra = ((_pp.get("cells") or {}).get("A_pre_universe_pre_period") or {})
    _prrows = _pra.get("cells") or {}
    _prvals = [float(r["excess_cagr_pp"]) for r in _prrows.values()
               if isinstance(r, dict) and r.get("excess_cagr_pp") is not None]
    check("the page prints the book's pre-2020 reading beside the headline (r1846)",
          (not _prvals) or ("这本书有出生日期" in md1
                            and "不是因子的证据" in md1
                            and f"{min(_prvals):+.2f}" in md1
                            and f"{max(_prvals):+.2f}" in md1))
    _pmm = json.loads(json.dumps(p1))
    _pmm["etf_book_periods"] = {"present": False,
                                "note": "分期间面未产出（缺面不读 0）"}
    _mdmm = render_md(_pmm)
    check("an unread period face prints a reason, not a zero (r1846)",
          "分期间面未产出" in _mdmm and "这本书有出生日期" not in _mdmm)
    _pnn = json.loads(json.dumps(p1))
    _pnn["etf_book_periods"] = dict(_pnn.get("etf_book_periods") or {})
    _pnn["etf_book_periods"]["pre"] = dict(
        (_pnn["etf_book_periods"].get("pre") or {}),
        all_negative=False, worst_pp=1.0, best_pp=2.0)
    _mdnn = render_md(_pnn)
    check("a pre-period that is not all negative is not printed as such (r1846)",
          "不全为负" in _mdnn and "全部为负" not in _mdnn)
    # ---- r1855: ⓪ measures the faces the page prints; the lanes that feed them
    # were never on the page, so a collector could go silent for a day and a half
    # while ⓪ still read "全部面都追到 X".  The block must name the lane, its
    # owner and the owner's silence -- and must not print a clean sheet when the
    # lane board itself cannot be read.
    _dl_ok = {"status": "ok", "as_of": "2026-11-20T01:40:00", "machine": "bm-c",
              "verdict": "attention", "n_lanes": 15, "expected": "2026-11-19",
              "counts": {"in_sync": 11, "stalled": 1, "behind_1d": 2,
                         "retired": 1},
              "rows": [{"lane": "heat", "host": "bm-a", "host_alive": False,
                        "host_age_h": 29.8, "state": "behind_1d",
                        "tail": "2026-11-18", "expected": "2026-11-19",
                        "missing_days": ["2026-11-19"],
                        "loss_mode": "a missed day is permanent: the guba rank "
                                     "is a live rolling list",
                        "takeover_capable": True}],
              "hosts": {"bm-a": {"age_h": 29.8, "alive": False,
                                 "silent_waiting": ["heat"],
                                 "silent_taken_over": {"futures": "bm-c"}}}}
    _md_dl = "\n".join(_data_lane_lines(_dl_ok))
    check("the page names the lane that is behind and who owns it (r1855)",
          "`heat`" in _md_dl and "bm-a" in _md_dl
          and "2026-11-19" in _md_dl and "11 条追平" in _md_dl)
    check("the carrier's own sentence about the missed day is carried verbatim "
          "(r1855)", "a missed day is permanent" in _md_dl)
    check("a silent owner is named with its age and what it owes (r1855)",
          "静默 29.8h" in _md_dl and "futures←bm-c" in _md_dl)
    _md_dl2 = "\n".join(_data_lane_lines(
        dict(_dl_ok, verdict="all_fresh", rows=[], hosts={},
             counts={"in_sync": 14, "retired": 1})))
    check("an all-clear lane board says so instead of an empty list (r1855)",
          "全部 15 条数据车道都追平" in _md_dl2 and "`heat`" not in _md_dl2)
    _dl_missing = _data_lane_face(
        path=os.path.join(ROOT, "results", "_no_such_lane_face.json"))
    _md_dl3 = "\n".join(_data_lane_lines(_dl_missing))
    check("a missing lane board prints a reason, not a clean sheet (r1855)",
          "读不到" in _md_dl3 and "追平" not in _md_dl3
          and "不能说数据是新的" in _md_dl3)
    print(f"selftest: {'ALL PASS' if not fails else f'FAIL {fails}'}")
    return 0 if not fails else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        print("=== ceo_live_usage selftest (read-only, no network) ===")
        return selftest()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
