"""The CEO one-pager says 今日 while its own numbers were priced on another bar.

r1669..r1671 taught this question to the etf book page (`scripts/live_book_day_words.py`):
count the today-words a reader can actually see, then read every printed date against the
field its sentence quotes. That page is not the only paper the CEO opens. `docs/live_usage/
LIVE-*.md` prints **今日 +¥0（对比 2026-11-13）** on a Saturday: the reader's day has had no
session, and the number belongs to 2026-11-13. The same audit, on the second paper, is this
module.

Two questions, and they are not the same question:

  * **the date claim** -- "the sentence names a day; is that day the one the field carries?"
    Reuses `live_book_day_words._date_claims` verbatim (r1375 family: one implementation,
    two readers -- a second copy of the matcher is the defect that never gets fixed twice);
  * **the day word** -- "this sentence uses 今天/今日 to assert today's number; is the page's
    own day the day that number was priced on?" Only *value-claiming* today-words are
    judged. "今日尚未有 bar" and "今日 09:15 起随源点亮" are the honest forms -- they say the
    reader's day has nothing yet -- and are counted as honest, never as offenders.

Verdicts, none of which is interchangeable:

  * PRINTED_DATES_AGREE      -- every printed date matches its field and no today-word borrows
                                a day it does not have;
  * PRINTED_DATE_MISMATCH    -- a printed date disagrees with the field its sentence quotes;
  * DAY_WORD_ON_STALE_PAGE   -- a today-word asserts a number that was priced on another bar
                                (named with both days);
  * PRINTED_SELF_DATED       -- dates are present but some are unmapped/unverifiable: not
                                green, the audit simply cannot say;
  * PRINTED_BUT_UNANCHORED   -- the paper carries day words the rules cannot read at all;
  * UNVERIFIED_PRINTED_FACE  -- the paper could not be read ("could not check" is never clean).

Exit codes: 0 green, 1 a named debt, 2 the artifact cannot be read.

Usage:
    python scripts/live_usage_day_words.py run
    python scripts/live_usage_day_words.py check
    python scripts/live_usage_day_words.py --selftest
"""
from __future__ import annotations

import json
import os
import re
import sys
import time

# r1812: this guard prints the page's own lines back as evidence, and the CEO paper carries
# the yen sign (U+00A5), which the ANSI code page on this host (GBK) cannot encode -- the audit
# then died with UnicodeEncodeError instead of naming the debt (the failure the chain runner
# hit at r1578). An unprintable character is never a reason to lose the verdict.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors="replace")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from scripts import live_book_day_words as LBW  # noqa: E402  (shared matcher, one copy)

JSON_FACE = os.path.join(ROOT, "docs", "live_usage", "LIVE-latest.json")
PAGE_FACE = os.path.join(ROOT, "docs", "live_usage", "LIVE-latest.md")
FACE = os.path.join(ROOT, "results", "live_usage_day_words.json")

_D = r"(20\d{2}-\d{2}-\d{2})"
# Each rule anchors one sentence of this page to the field that issued it. A printed date no
# rule claims stays `unmapped` and blocks the green (r1671: unmapped is a debt, not a pass).
CLAIM_RULES = [
    (re.compile(r"^# CEO 实盘使用一页纸 · " + _D), ["day"]),
    (re.compile(r"自动生成 " + _D), ["generated"]),
    (re.compile(r"最后必须已有 bar 的会话是 \*\*" + _D + r"\*\*"), ["freshness.expected_bar"]),
    (re.compile(r"⑥ ETF 复合书：截至 \*\*" + _D + r"\*\*"), ["etf_book.last_bar"]),
    (re.compile(r"③ 风险带（zt 四面板）：截至 \*\*" + _D + r"\*\*"), ["risk_tape.cutoff"]),
    (re.compile(r"① 市场政体态：截至 \*\*" + _D + r"\*\*"), ["market.asof"]),
    (re.compile(r"定价面板尾 bar：\*\*" + _D + r"\*\*"), ["freshness.book_panel_last_bar"]),
    (re.compile(r"当前政体态：RED\*\*.*· asof " + _D), ["market.asof"]),
    (re.compile(r"`RED_COOL`（asof " + _D + r"）"), ["market.clock_asof"]),
    (re.compile(r"截止 " + _D + " · 涨停池"), ["risk_tape.cutoff"]),
    (re.compile(r"杀跌日（bar " + _D + r"）"), ["risk_tape.cutoff"]),
    (re.compile(r"较 " + _D + " 收盘"), ["freshness.expected_bar"]),
    (re.compile(r"今日 [+\-−]?¥[\d,]+（对比 " + _D + r"）"), ["rollup.day_prior"]),
    (re.compile(r"\*\*账本\*\*：" + _D + " 播种"), ["etf_book.first_bar"]),
    (re.compile(r"\*\*账本\*\*：2026-10-23 播种 → " + _D), ["etf_book.last_bar"]),
    (re.compile(r"top-10 名义持仓.*?证据截至 " + _D), ["national_team.s2_evidence_cutoff"]),
    (re.compile(r"EXODUS 段：.*?证据截至 " + _D), ["national_team.s3_evidence_cutoff"]),
    (re.compile(r"日历在册最后一日 " + _D), ["freshness.calendar_last"]),
    (re.compile(r"结论：全部面都追到 " + _D), ["freshness.expected_bar"]),
    (re.compile(r"（as_of " + _D + "·RESEARCH_READOUT"), ["recommendation.as_of"]),
    (re.compile(r"入场 " + _D + "·单边换手"), ["recommendation.entry_date"]),
    (re.compile(r"账本 \d+ 名 · k [\d.]+ · vol_target [\d.]+% · 决策 bar " + _D),
     ["book_identity.ledger.bar"]),
    (re.compile(r"执行单 \d+ 名 · k [\d.]+ · beta_target [\d.]+ · 决策 bar " + _D),
     ["book_identity.ticket.bar"]),
    (re.compile(r"未定稿 bar：" + _D), ["etf_book.provisional_bars[0]"]),
    # r1812: section 6's "next look" sentence and section 7's withdrawal provenance were
    # printed without a rule, so the audit could only say "cannot read that day" (2 lines).
    # Both name the face that issued them, so they are claimable rather than exempt: the
    # decision bar is the ledger's own bar, and section 7 stamps the carry face's
    # decided/source_generated pair.
    (re.compile(r"上一次决策 bar " + _D), ["book_identity.ledger.bar"]),
    (re.compile(r"WITHDRAW_FROM_TICKET`?（" + _D), ["carry_book.decided"]),
    # Engine files and provenance lines print the ticket's own date (its file name) beside the
    # bar the sentence is about, so the rule has to claim BOTH dates in one match -- a rule
    # that maps only the prose date leaves the file-name date unmapped and the line still red.
    (re.compile(r"换仓差量面（`results/etf_book_order/TICKET-" + _D + r"\.json`·bar " + _D),
     ["etf_order.bar", "etf_order.delta.current_bar"]),
    (re.compile(r"idx_fut_carry_open_capital\.json`?｜generated " + _D +
                r"T[\d:+]*(?:[+\-]\d{2}:\d{2})?｜cutoff " + _D),
     ["carry_book.source_generated", "carry_book.evidence_cutoff"]),
    (re.compile(r"（" + _D + r" → " + _D + r"，账面零成交）"),
     ["etf_order.delta.current_bar", "etf_order.delta.declaration_bar"]),
    (re.compile(r"账上那本按 " + _D + r" 的价、票面按 " + _D + r" 的价"),
     ["etf_order.delta.mark_account_bar", "etf_order.bar"]),
    (re.compile(r"账面持仓 bar " + _D + r" → 票面 bar " + _D),
     ["etf_order.delta.current_bar", "etf_order.bar"]),
    (re.compile(r"idx_fut_basis_timing\.json`?｜cutoff " + _D),
     ["carry_timing.evidence_cutoff"]),
    # r1299: the timing sentence now names the bar it read (instead of a bare 「今天」), so the
    # date it prints must resolve to the field behind it -- otherwise naming the bar turns one
    # false red into one foreign date.
    (re.compile(r"在 " + _D + r" 那根 bar 上\*\*四个品种都不在带内\*\*"),
     ["carry_timing.evidence_cutoff"]),
    # r1310: r1779/r1787 put the ticket, the withdrawal decision and the "today's action"
    # block on the page but taught no rule to read their dates -- 19 printed dates stayed
    # unmapped and the face could never be green (the "permanent red" family, r1789: a report
    # that is always red teaches readers to treat real defects as background noise). Every
    # rule below names a field that already exists on the page's own JSON; the file-name
    # dates sitting in the same lines are identifiers, sorted by _unmapped_classifier.
    (re.compile(r"照做版执行单\*\*（决策 bar " + _D), ["etf_order.decision_bar"]),
    # r1870: this rule used to be a bare `（generated <D>T`, so it also claimed the PRE2020
    # provenance line ("etf_book_pre2020.json（generated 2026-11-19T16:16:49…）") and compared
    # that paper's stamp against the ticket's. It only ever passed because both were written
    # on the same day; the first day the ticket was regenerated later than that face
    # (2026-11-20 08:06 vs 11-19 16:16) the page went red for a line about a different face.
    # Anchor the rule to the ticket's own file name; the pre2020 twin has its own rule below.
    (re.compile(r"TICKET-\d{4}-\d{2}-\d{2}\.json`（generated " + _D + r"T"),
     ["etf_order.generated"]),
    (re.compile(r"etf_book_order[^·]*·cutoff " + _D), ["etf_order.bar"]),
    (re.compile(r"今天读数 \*\*[\d.]+%\*\*（最紧的一席 [^）]*·盘口 " + _D + r"）"),
     ["etf_capacity.session"]),
    (re.compile(r"倒过来读：" + _D + r" 这个成交额下"), ["etf_capacity.session"]),
    # r1870: the new admission paragraph prints four days, and each names the field that
    # issued it -- an extra "bare date" on the page is a debt, not a decoration (r1671).
    (re.compile(r"（算到 " + _D + r"）"),
     ["etf_order.admission.years.evidence_cutoff"]),
    (re.compile(r"（从 " + _D + r" 这条曲线逐年读出"),
     ["etf_order.admission.years.money_base"]),
    (re.compile(r"块内最差的拒绝 " + _D),
     ["etf_order.admission.block.A1.worst.start"]),
    (re.compile(r"样本外窗口固定在 " + _D),
     ["etf_order.admission.years.oos_start"]),
    (re.compile(r"最近一笔 [\d.]+%（" + _D + r"）"),
     ["etf_order.cash_leg.bands.spot.as_of"]),
    (re.compile(r"账面持仓 bar " + _D + r" → 票面 bar " + _D),
     ["etf_order.delta.current_bar", "etf_order.delta.declaration_bar"]),
    (re.compile(r"账上那本按 " + _D + r" 的价、票面按 " + _D + r" 的价"),
     ["etf_order.delta.mark_account_bar", "etf_order.delta.declaration_bar"]),
    (re.compile(r"（" + _D + r" → " + _D + r"，账面零成交）"),
     ["etf_order.delta.current_bar", "etf_order.delta.declaration_bar"]),
    (re.compile(r"换仓差量面[^）]*·bar " + _D), ["etf_order.delta.current_bar"]),
    (re.compile(r"上一次决策 bar " + _D), ["etf_order.book_decided_bar"]),
    (re.compile(r"WITHDRAW_FROM_TICKET`（" + _D), ["carry_book.decided"]),
    (re.compile(r"idx_fut_carry_open_capital\.json`｜generated " + _D + r"T"),
     ["carry_book.source_generated"]),
    (re.compile(r"｜cutoff " + _D + r"｜尺子"), ["carry_book.evidence_cutoff"]),
    (re.compile(r"在 " + _D + r" 那根 bar 上在带内"), ["carry_timing.evidence_cutoff"]),
    (re.compile(r"idx_fut_basis_timing\.json`｜cutoff " + _D),
     ["carry_timing.evidence_cutoff"]),
    # r1849: section 6's 「premium paid ... and TODAY 159655 sits at the dearest end of its own
    # year」 printed a bare today-word, so the audit could only say it could not read that day
    # (PRINTED_BUT_UNANCHORED, 1 line). The producer now stamps the premium face's own
    # ticket_session; the rule reads that field rather than the page day, because a premium
    # quoted on yesterday's IOPV snapshot is readable, not wrong (E685: match the date to the
    # face that issued the number).
    (re.compile(r"而且在 " + _D + r" 这一档"), ["etf_premium.ticket_session"]),
    # r1849: the punctuality ladder (「today or split it over a few days」) and the
    # NOTHING_OWED_TODAY sentence were both bare today-words on numbers measured on the
    # ticket's own bar. They now name that bar; the rule reads it back off the punctuality
    # face, because the sentence is a claim about the bar the ladder was priced on.
    (re.compile(r"在 " + _D + r" 这一档做"), ["etf_punctuality.evidence_cutoff"]),
    # r1849: with the last bare today-word gone the face named its real debt -- 20 printed
    # dates no rule claimed ("cannot check" is not "agrees", so the page could never be green:
    # the permanent-red family, r1789). Each rule below maps a sentence to the field the page
    # already carries for it; none of them widens a tolerance or skips a date.
    (re.compile(r"上次换仓 " + _D + r" · \*\*欠 \d+ 次调仓\*\*（最近该换的是 " + _D),
     ["recommendation.entry_date", "freshness.monthly[0].dues[0]"]),
    (re.compile(r"下一个月首交易日（" + _D + r"）已经过去"),
     ["freshness.monthly[0].dues[0]"]),
    (re.compile(r"最新 1m bar " + _D), ["intraday.asof"]),
    (re.compile(r"bar " + _D + r" 15:00:00·lag"), ["intraday.asof"]),
    (re.compile(r"picks 面 as_of " + _D), ["recommendation.picks_asof"]),
    (re.compile(r"etf_book_pre2020\.json`（generated " + _D + r"T[\d:]+·cutoff " + _D),
     ["etf_book_periods.generated", "etf_book_periods.cutoff"]),
    (re.compile(r"滚仓面读的是 " + _D + r"，这张票面读的是 " + _D),
     ["etf_order.cash_roll.as_of", "etf_order.cash_roll.ticket_bar"]),
    (re.compile(r"把账面拉到 " + _D + r" 的票面"), ["etf_order.bar"]),
    (re.compile(r"etf_book_do_or_wait\.json`（计价截止 " + _D),
     ["etf_punctuality.evidence_cutoff"]),
    (re.compile(r"换成日历日期就是 \*\*" + _D + r"\*\*"),
     ["etf_order.next_decision_face.date"]),
    (re.compile(r"容量面量的是 " + _D + r" 的盘口，与这一页票面的 " + _D),
     ["etf_capacity.session", "etf_capacity_at_size.bar"]),
    (re.compile(r"idx_fut_carry_margin\.json`｜generated " + _D + r"T[\d:+]+｜cutoff " + _D),
     ["carry_margin.source_generated", "carry_margin.evidence_cutoff"]),
    (re.compile(r"idx_fut_carry_risk\.json`｜generated " + _D + r"T[\d:+]+｜cutoff " + _D),
     ["carry_roll_cost.source_generated", "carry_roll_cost.evidence_cutoff"]),
    (re.compile(r"futures_book_marks\.json`｜generated " + _D + r"T[\d:+]+｜cutoff " + _D),
     ["carry_marks.source_generated", "carry_marks.evidence_cutoff"]),
    # r1871: the capacity-by-year line is the only place on the page where a bar date and a
    # year share a sentence, and the boundary line ends on the face's own cutoff. Both are
    # read off the ticket block the same page prints, so the rule maps to that block.
    (re.compile(_D + r" 这根 bar 装 [\d,]+ 元"), ["etf_order.admission.capacity.latest.bar"]),
    (re.compile(r"ADV 是那一年自己的 20 根中位；算到 " + _D),
     ["etf_order.admission.capacity.evidence_cutoff"]),
    # r1893: the "do not wait for a sharper ruler" block prints the face's cutoff and its
    # producing stamp. Both are fields on this page's own JSON, so the block is claimable
    # instead of adding two more unchecked dates (r1671: a new bare date is a debt).
    (re.compile(r"面到 " + _D + r"）：把尺子从"),
     ["precision_wait.evidence_cutoff"]),
    (re.compile(r"etf_book_target_price\.py`?·" + _D + r"T"),
     ["precision_wait.generated"]),
    # r1893: the supply board prints one row per lane plus its read clock.  Twelve of the
    # twenty dates the audit could not place were these rows -- the lane table is keyed by
    # name on this page's own JSON, so the rule asks for the lane, never for row 0 (an order
    # change would otherwise read a different lane's tail and nobody would notice).
    (re.compile(r"车道板读数（" + _D + r" \d{2}:\d{2} 读自"), ["data_lanes.as_of"]),
    (re.compile(r"参照日 " + _D), ["data_lanes.expected"]),
    (re.compile(r"- `(?P<lane>[a-z_0-9]+)`（属主 [^·]+·尾 " + _D +
                r"·欠 \d+ 个会话：" + _D + r"）"),
     ["data_lanes.rows[lane={lane}].tail",
      "data_lanes.rows[lane={lane}].missing_days[0]"]),
    # r1907: r1900 put the book's own seed capital into money on the page, which introduced one
    # more bare date ("1,000,000 元 · 2026-10-23 起"). It is the ledger's own seed bar, a field
    # this page's JSON carries (`etf_book.seed_bar`), so it is claimable like every other date
    # here rather than a debt the audit has to keep naming.
    (re.compile(r"账本自己的播种资本 [\d,]+ 元 · " + _D + r" 起"),
     ["etf_book.seed_bar"]),
    # r1893 (second batch): the rest of the unchecked dates on this page, each one naming a
    # field the page's own JSON already carries. Written after the first-ever drive of this
    # leg showed 20 dates no rule could place -- a face that is always red teaches readers to
    # treat real defects as noise (r1789), so the debt gets paid down, not annotated.
    (re.compile(r"这份名单这段到底赚了多少\*\*：" + _D + r" 进、" + _D + r" 出"),
     ["recommendation.track.entry_bar", "recommendation.track.cutoff"]),
    (re.compile(r"检查面 generated " + _D + r"T"),
     ["etf_order.input_order.generated"]),
    (re.compile(r"边界：算到 " + _D + r"，面生成于 " + _D + r"T"),
     ["etf_entry_price.cutoff", "etf_entry_price.generated"]),
    (re.compile(r"（盘口 " + _D + r"·计价截止 " + _D + r"）"),
     ["etf_capacity.session", "etf_capacity.evidence_cutoff"]),
    (re.compile(r"最老的那根停在 " + _D),
     ["futures_panel.oldest_dead.last_bar"]),
    (re.compile(r"面板日 " + _D + r"｜活跃窗自 " + _D + r" 起.*?·" + _D +
                r"T.*?｜generated " + _D + r"T.*?｜cutoff " + _D),
     ["futures_panel.panel_date", "futures_panel.window_cut",
      "futures_panel.writer_generated", "futures_panel.source_generated",
      "futures_panel.evidence_cutoff"]),
    (re.compile(r"盘面最早一根（" + _D + r"）"),
     ["futures_gaps.panel_first_bar"]),
    (re.compile(r"futures_panel_gaps\.json`｜generated " + _D +
                r"T[\d:+]+｜cutoff " + _D + r"｜探针沿自 " + _D + r"T"),
     ["futures_gaps.source_generated", "futures_gaps.evidence_cutoff",
      "futures_gaps.carried_from"]),
]

# A date that rides inside a file name (`TICKET-2026-11-17.json`) names a paper; it does not
# claim that a field carries that day. Sorted into its own bucket and printed, never counted
# as checked (r1674's contract for `_date_claims.unmapped_classifier`).
_FILE_DATE = re.compile(r"[\w\-.\\/]*-20\d{2}-\d{2}-\d{2}(?:T[\d:+\-]+)?\.[A-Za-z0-9]{2,5}")


def _unmapped_classifier(rec):
    line = rec.get("line") or ""
    date = rec.get("date") or ""
    if not date:
        return None
    for m in _FILE_DATE.finditer(line):
        if date in m.group(0):
            return "identifier"
    return None

# Dates that are rule constants, not data claims: 月界（2026-10-01）is when a gate opens, and
# no field can disagree with it. They are counted and printed separately -- a policy date that
# quietly joined the pass bucket would be the "unmapped becomes green" defect (r1671).
POLICY_RULES = [
    re.compile(r"月界（" + _D + "）"),
]

# Only sentences that assert a number about the reader's own day. `honest` marks the forms
# that say the day has nothing yet -- those are the cure, not the disease.
DAY_CLAIM_RULES = [
    (re.compile(r"今日 [+\-−]?¥[\d,]+"), "rollup.day_pnl_cny", "asserts today's P&L"),
    (re.compile(r"今日 \*\*未判\*\*"), "risk_tape.kill_day_unavailable", "asserts today's read"),
    (re.compile(r"杀跌日，今日 (是|否)"), "risk_tape.kill_day", "asserts today's session"),
    # r1299: the basis-timing sentence read 「今天」 over the carry face's own bar, and that bar
    # sits one session behind the page whenever the basis panel lags (11-16 against a 11-17
    # page). Both halves -- in band and not in band -- are one claim about one field.
    (re.compile(r"(今天|在 \d{4}-\d{2}-\d{2} 那根 bar 上)\*\*四个品种都不在带内\*\*"),
     "carry_timing.evidence_cutoff", "asserts the timing state on the carry face's own bar"),
    (re.compile(r"(今天|在 \d{4}-\d{2}-\d{2} 那根 bar 上)在带内：\*\*"),
     "carry_timing.evidence_cutoff", "asserts the timing state on the carry face's own bar"),
]
DAY_HONEST_RULES = [
    re.compile(r"今日尚未有 ?bar"),
    re.compile(r"今日 09:15 起随源点亮"),
    # r1299: a quoted description of what a number IS (「这段现金按今天的利率值多少」 in a
    # sentence that says it is not folded into NAV) states the reading's nature, not a number
    # about a day. Anchored on the quote itself, so the same words outside 「」 stay unanchored.
    re.compile(r"「这段现金按今天的利率值多少」"),
]

CLEAN = ("PRINTED_DATES_AGREE",)


def _printed_rows(text):
    """Every printed line under its heading -- the date audit reads all of them.

    `live_book_day_words._printed_census` keeps only today-word lines because there the two
    questions sit on the same sentences. Here they do not: the one-pager prints 23 dates and
    only 5 of them are near a today-word, so reusing that row filter would audit 5 of 23 and
    call the rest unmapped -- a face that measures the wrong paper (E240 family).
    """
    rows, heading = [], "(页首)"
    for line in (text or "").split("\n"):
        if line.startswith("## "):
            heading = line[3:].strip()[:46]
        if not line.strip():
            continue
        rows.append({"heading": heading, "line": line.strip()[:400],
                     "self_dated": bool(LBW.DATE_IN_TEXT.search(line))})
    return rows


def _day_word_rows(rows):
    return [r for r in rows if any(w in (r.get("line") or "") for w in LBW.DAY_WORDS)]


def _day_claims(rows, page_day, bar_day, rules=None, bar_for=None, honest_forms=None):
    """Value-claiming today-words, each read against the day the page's own bar falls on.

    `bar_for(field) -> day` lets a paper whose sections are priced on different bars answer
    per sentence instead of borrowing one page-wide bar (r1674: the daily report puts today's
    floor-compliance count beside the ETF book's Friday price). `honest_forms` replaces the
    page's own list of forms that say the day has nothing yet.
    """
    rules = DAY_CLAIM_RULES if rules is None else rules
    honest_pats = DAY_HONEST_RULES if honest_forms is None else honest_forms
    claims, offenders, honest = [], [], []
    for row in rows or []:
        line = row.get("line") or ""
        if any(p.search(line) for p in honest_pats):
            honest.append({"heading": row.get("heading"), "line": line[:140]})
            continue
        for pat, field, why in rules:
            if not pat.search(line):
                continue
            bar = bar_for(field) if bar_for is not None else bar_day
            stale = bool(page_day and bar and page_day != bar)
            rec = {"heading": row.get("heading"), "field": field, "why": why,
                   "page_day": page_day, "bar_day": str(bar)[:10] if bar else None,
                   "reading": "stale_day" if stale else "same_day",
                   "line": line[:160]}
            claims.append(rec)
            if stale:
                offenders.append(rec)
            break
    return {"n_claims": len(claims), "n_stale": len(offenders),
            "n_honest_forms": len(honest), "claims": claims[:20],
            "offenders": offenders[:20], "honest": honest[:10]}


def census(doc, printed):
    """Two papers, two questions: the printed dates, and the day words that assert a number."""
    ret = {"artifact": None, "page_day": None, "bar_day": None, "verdict": "UNREADABLE",
           "sentence": "", "printed": {"state": "not_measured"},
           "date_claims": {"state": "not_measured"}, "day_claims": {"state": "not_measured"}}
    if not isinstance(doc, dict) or not doc:
        ret["sentence"] = "一页纸的 JSON 读不出来——这不是「没有日词」，是没法核验。"
        return ret
    ret["page_day"] = str(doc.get("day") or "")[:10] or None
    ret["bar_day"] = str((doc.get("freshness") or {}).get("expected_bar") or "")[:10] or None
    if printed is None:
        ret["printed"] = {"state": "unreadable"}
        ret["verdict"] = "UNVERIFIED_PRINTED_FACE"
        ret["sentence"] = ("一页纸的印刷面读不出来（只读到 JSON）——「没核到」不等于「没问题」，"
                           "所以这一面不给绿。")
        return ret
    rows = _printed_rows(printed)
    day_rows = _day_word_rows(rows)
    honest_rows = [r for r in day_rows
                   if any(p.search(r.get("line") or "") for p in DAY_HONEST_RULES)]
    debt_rows = [r for r in day_rows if r not in honest_rows]
    heads = []
    for r in rows:
        if r["heading"] not in heads:
            heads.append(r["heading"])
    undated = [r for r in debt_rows if not r["self_dated"]]
    pr = {"state": "ok", "n_lines": len(day_rows), "n_all_lines": len(rows),
          "n_headings": len(heads), "n_honest": len(honest_rows),
          "n_self_dated": len(debt_rows) - len(undated),
          "n_undated": len(undated), "undated": undated[:40],
          "headings": heads[:12], "rows": rows}
    ret["printed"] = pr
    ret["date_claims"] = LBW._date_claims(rows, doc, rules=CLAIM_RULES,
                                          unmapped_classifier=_unmapped_classifier)
    policy = []
    if ret["date_claims"].get("unmapped"):
        keep = []
        for r in ret["date_claims"]["unmapped"]:
            if any(p.search(r.get("line") or "") for p in POLICY_RULES):
                policy.append(r)
            else:
                keep.append(r)
        ret["date_claims"]["unmapped"] = keep
        ret["date_claims"]["n_unmapped"] = len(keep)
    ret["date_claims"]["n_policy"] = len(policy)
    ret["date_claims"]["policy"] = policy
    ret["day_claims"] = _day_claims(day_rows, ret["page_day"], ret["bar_day"])
    dc, dy = ret["date_claims"], ret["day_claims"]
    if dc.get("n_mismatch"):
        ret["verdict"] = "PRINTED_DATE_MISMATCH"
    elif dy.get("n_stale"):
        ret["verdict"] = "DAY_WORD_ON_STALE_PAGE"
    elif pr.get("n_undated"):
        # a today-word that names no day at all is the reader-facing debt, and it comes
        # before any date-rule gap: "有人读不出这一天" outranks "这一处我还没规则可核".
        ret["verdict"] = "PRINTED_BUT_UNANCHORED"
    elif (dc.get("n_claims") and not dc.get("n_unmapped") and not dc.get("n_unverifiable")
          and dc.get("n_ok") == dc.get("n_claims")):
        ret["verdict"] = "PRINTED_DATES_AGREE"
    else:
        ret["verdict"] = "PRINTED_SELF_DATED"
    ret["sentence"] = sentence(ret)
    return ret


def sentence(c):
    pr, dc, dy = c.get("printed") or {}, c.get("date_claims") or {}, c.get("day_claims") or {}
    if c["verdict"] == "PRINTED_DATE_MISMATCH":
        named = "；".join("「%s」里写 `%s`，而 %s 是 `%s`"
                         % (r["heading"], r["date"], r["field"], r["expected"])
                         for r in (dc.get("mismatches") or [])[:4])
        return ("**一页纸上 %d 处日期里，有 %d 处与它引用的那张面对不上**：%s。"
                % (dc.get("n_claims", 0), dc.get("n_mismatch", 0), named))
    if c["verdict"] == "DAY_WORD_ON_STALE_PAGE":
        named = "；".join("「%s」" % r["line"][:60] for r in (dy.get("offenders") or [])[:4])
        return ("**本页是 %s 的页面，可它拿「今天/今日」说的是 %s 那根 bar 的数**（%d 处）：%s。"
                "读者在 %s 打开这页，读到的是自己今天的数，而那张面停在 %s。"
                % (c.get("page_day") or "?", c.get("bar_day") or "?", dy.get("n_stale", 0),
                   named, c.get("page_day") or "?", c.get("bar_day") or "?"))
    if c["verdict"] == "PRINTED_DATES_AGREE":
        return ("**一页纸上 %d 处日期逐句对上了它引用的那张面**（%d 条规则，0 处判不了，"
                "0 处无规则可核）；日词 %d 行全部自带日期，其中 %d 处拿「今天」说数的地方"
                "落在本页自己的 bar（%s）上。这一面核的是「句子写的日子 == 那个字段写的日子」，"
                "不核那个字段本身对不对。"
                % (dc.get("n_claims", 0), dc.get("n_rules", 0), pr.get("n_lines", 0),
                   dy.get("n_claims", 0), c.get("bar_day") or "?"))
    if c["verdict"] == "PRINTED_SELF_DATED":
        return ("**一页纸上 %d 行日词都自带日期，但 %d 处日期没有规则可核 / %d 处字段缺失**——"
                "核不了的不算对上，这一面不给绿。"
                % (pr.get("n_lines", 0), dc.get("n_unmapped", 0), dc.get("n_unverifiable", 0)))
    if c["verdict"] == "PRINTED_BUT_UNANCHORED":
        return ("**一页纸上 %d 行日词、%d 行读不出是哪一天**——规则还没覆盖这些句子，"
                "所以这一面说不出它们对不对。"
                % (pr.get("n_lines", 0), pr.get("n_undated", 0)))
    return c["sentence"] or "**这一面没有结论**。"


def _read(json_face=JSON_FACE, page_face=PAGE_FACE):
    """(doc, printed, error). The page is read through the published pair, never a guess."""
    try:
        with open(json_face, "r", encoding="utf-8") as fh:
            doc = json.load(fh) or {}
    except (OSError, ValueError) as exc:
        return None, None, "%s: %s" % (type(exc).__name__, exc)
    printed = None
    try:
        with open(page_face, "r", encoding="utf-8") as fh:
            printed = fh.read()
    except (OSError, ValueError):
        printed = None
    return doc, printed, None


def run(out=FACE):
    doc, printed, err = _read()
    if err:
        print("LIVE_USAGE_DAY_WORDS_UNREADABLE %s" % err)
        return 2
    c = census(doc, printed)
    c["script"] = "live_usage_day_words"
    c["artifact"] = "docs/live_usage/LIVE-latest.json"
    c["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(c, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("%s | %s" % (c["verdict"], c["sentence"]))
    return 0 if c["verdict"] in CLEAN else 1


def check():
    doc, printed, err = _read()
    if err:
        print("CHECK_UNREADABLE %s" % err)
        return 2
    c = census(doc, printed)
    pr, dc, dy = c["printed"], c["date_claims"], c["day_claims"]
    print("verdict %s | page %s | bar %s | printed %s lines (self-dated %s / undated %s)"
          % (c["verdict"], c.get("page_day") or "?", c.get("bar_day") or "?",
             pr.get("n_lines", "-"), pr.get("n_self_dated", "-"), pr.get("n_undated", "-")))
    print("  DATES claims %s | ok %s | mismatch %s | unverifiable %s | unmapped %s | rules %s"
          % (dc.get("n_claims", "-"), dc.get("n_ok", "-"), dc.get("n_mismatch", "-"),
             dc.get("n_unverifiable", "-"), dc.get("n_unmapped", "-"), dc.get("n_rules", "-")))
    print("  DAYS  claims %s | stale %s | honest-forms %s"
          % (dy.get("n_claims", "-"), dy.get("n_stale", "-"), dy.get("n_honest_forms", "-")))
    for r in dc.get("mismatches") or []:
        print("  DATE-MISMATCH %s | printed %s | %s = %s"
              % (r["heading"], r["date"], r["field"], r["expected"]))
    for r in dc.get("unmapped") or []:
        print("  DATE-UNMAPPED %s | %s | %s" % (r["heading"], r["date"], r["line"][:80]))
    if dc.get("buckets"):
        # a bucket is a reason a date is not checked; it is printed so the reader can see
        # what was set aside, and it never joins the ok count (r1674 contract).
        print("  DATE-BUCKETS %s" % ", ".join("%s=%s" % (k, v)
                                              for k, v in sorted(dc["buckets"].items())))
    for r in dy.get("offenders") or []:
        print("  STALE-DAY %s | page %s vs bar %s | %s"
              % (r["heading"], r["page_day"], r["bar_day"], r["line"][:100]))
    for r in dy.get("honest") or []:
        print("  HONEST-DAY %s | %s" % (r["heading"], r["line"][:90]))
    print(c["sentence"])
    return 0 if c["verdict"] in CLEAN else 1


def selftest():
    total = ok = 0

    def leg(name, cond, detail=""):
        nonlocal total, ok
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL %s %s" % (name, detail))

    def doc(day="2026-11-14", bar="2026-11-13", prior="2026-11-13"):
        return {"day": day, "generated": day + "T10:56:48",
                "freshness": {"expected_bar": bar, "book_panel_last_bar": bar},
                "market": {"asof": bar, "clock_asof": bar},
                "risk_tape": {"cutoff": bar},
                "etf_book": {"last_bar": bar, "first_bar": "2026-10-23"},
                "rollup": {"day_prior": prior},
                "national_team": {"s2_evidence_cutoff": "2026-08-31",
                                  "s3_evidence_cutoff": "2026-09-24"}}

    def page(day="2026-11-14", bar="2026-11-13", prior="2026-11-13", amount="0"):
        return "\n".join([
            "# CEO 实盘使用一页纸 · " + day,
            "> 自动生成 " + day + "T10:56:48",
            "## ⓪ 本页新鲜度",
            "- 最后必须已有 bar 的会话是 **" + bar + "**",
            "  - ⑥ ETF 复合书：截至 **" + bar + "**",
            "  - ③ 风险带（zt 四面板）：截至 **" + bar + "**",
            "  - ① 市场政体态：截至 **" + bar + "**",
            "- 书的定价面板尾 bar：**" + bar + "**",
            "## ① 市场判定",
            "- **当前政体态：RED**（shadow 探测）· asof " + bar,
            "- **市场时钟**：`RED_COOL`（asof " + bar + "）",
            "- **市场风险面**：截止 " + bar + " · 涨停池 37 · 读法：跌停≥涨停 → 杀跌日，今日 否",
            "## ③ 六员分配",
            "- **六员合计**：今日 +¥" + amount + "（对比 " + prior + "）",
            "### 盘中档",
            "- 今日尚未有 bar（上一场收盘档·09:15 起随源点亮）",
            "  - 510050：上一场收盘 2.889（上一场收盘档（今日 09:15 起随源点亮））",
            "## ⑥ ETF 复合书",
            "- **账本**：2026-10-23 播种 → " + bar,
        ])

    # L1 a Saturday page whose P&L is priced on Friday is named with both days
    c = census(doc(), page())
    leg("L1 stale day word is an offender", c["verdict"] == "DAY_WORD_ON_STALE_PAGE", c["verdict"])
    leg("L1b sentence names both days",
        "2026-11-14" in c["sentence"] and "2026-11-13" in c["sentence"], c["sentence"][:80])
    leg("L1c the kill-day sentence is named too", c["day_claims"]["n_stale"] >= 1)

    # L2 the same page on a session day is green
    c2 = census(doc(day="2026-11-13", bar="2026-11-13", prior="2026-11-12"),
                page(day="2026-11-13", bar="2026-11-13", prior="2026-11-12", amount="1,234"))
    leg("L2 same day is green", c2["verdict"] == "PRINTED_DATES_AGREE",
        "%s claims=%s ok=%s unmapped=%s unverif=%s undated=%s fields=%s"
        % (c2["verdict"], c2["date_claims"].get("n_claims"), c2["date_claims"].get("n_ok"),
           c2["date_claims"].get("n_unmapped"), c2["date_claims"].get("n_unverifiable"),
           c2["printed"].get("n_undated"),
           [r["field"] for r in c2["date_claims"].get("claims") or []
            if r.get("reading") == "unverifiable"]))

    # L3 the honest forms are never offenders
    c3 = census(doc(), page())
    leg("L3 honest no-bar form counted apart", c3["day_claims"]["n_honest_forms"] >= 2,
        str(c3["day_claims"]["n_honest_forms"]))

    # L4 a printed date that disagrees with its field is a mismatch (both dates printed)
    bad = page().replace("定价面板尾 bar：**2026-11-13**", "定价面板尾 bar：**2026-11-12**")
    c4 = census(doc(), bad)
    leg("L4 date mismatch", c4["verdict"] == "PRINTED_DATE_MISMATCH", c4["verdict"])
    leg("L4b both dates printed", "2026-11-12" in c4["sentence"] and "2026-11-13" in c4["sentence"])

    # L5 an unreadable paper is never clean
    c5 = census(doc(), None)
    leg("L5 unreadable paper", c5["verdict"] == "UNVERIFIED_PRINTED_FACE", c5["verdict"])
    leg("L5b not in CLEAN", c5["verdict"] not in CLEAN)

    # L6 a date no rule claims blocks the green rather than counting as checked
    same = page(day="2026-11-13", bar="2026-11-13", prior="2026-11-12", amount="1,234")
    c6 = census(doc(day="2026-11-13", bar="2026-11-13", prior="2026-11-12"),
                same.replace("## ③ 六员分配", "## ③ 六员分配\n- 上个季度 2026-06-30 的读数"))
    leg("L6 unmapped date blocks green", c6["verdict"] == "PRINTED_SELF_DATED", c6["verdict"])
    leg("L6b unmapped counted", c6["date_claims"]["n_unmapped"] >= 1)

    # L7 the JSON missing is unreadable, not zero day words
    c7 = census({}, page())
    leg("L7 missing doc", c7["verdict"] == "UNREADABLE", c7["verdict"])

    # L7c a rule constant (月界) is counted apart and never counts as checked
    c7c = census(doc(day="2026-11-13", bar="2026-11-13", prior="2026-11-12"),
                 same + "\n- 公司自动实盘开闸=月界（2026-10-01）+CEO 唯一门")
    leg("L7c policy date keeps the page green", c7c["verdict"] == "PRINTED_DATES_AGREE",
        c7c["verdict"])
    leg("L7d policy date is counted, not checked",
        c7c["date_claims"].get("n_policy") == 1
        and c7c["date_claims"].get("n_claims") == c2["date_claims"].get("n_claims"),
        "policy=%s claims=%s vs base=%s" % (c7c["date_claims"].get("n_policy"),
                                            c7c["date_claims"].get("n_claims"),
                                            c2["date_claims"].get("n_claims")))

    # L8 the real published pair (whatever it says today) must be self-consistent to parse
    try:
        rdoc, rprinted, rerr = _read()
    except Exception as exc:  # pragma: no cover
        rdoc, rprinted, rerr = None, None, str(exc)
    leg("L8 live pair readable", rerr is None and isinstance(rdoc, dict), str(rerr))
    if rerr is None and rprinted is not None:
        live = census(rdoc, rprinted)
        leg("L8b live pair yields a verdict", live["verdict"] in (
            "PRINTED_DATES_AGREE", "PRINTED_DATE_MISMATCH", "DAY_WORD_ON_STALE_PAGE",
            "PRINTED_SELF_DATED", "PRINTED_BUT_UNANCHORED"), live["verdict"])

    # L9 (r1310) the ticket-provenance sentences r1779/r1787 put on the page name fields
    # that exist; a file-name date in the same line is an identifier, not a claim. Both
    # halves are pinned, because the failure mode this round fixed was 19 dates with no rule
    # at all, and the failure mode of the fix would be a rule that matches the shape but
    # never reads the field (a rule-shaped pass, r1471 family).
    d9 = doc(day="2026-11-13", bar="2026-11-13", prior="2026-11-12")
    d9["etf_order"] = {"decision_bar": "2026-11-13", "bar": "2026-11-13",
                       "generated": "2026-11-13T10:00:00+08:00"}
    p9 = page(day="2026-11-13", bar="2026-11-13", prior="2026-11-12", amount="1,234") + "\n" + "\n".join([
        "- **照做版执行单**（决策 bar 2026-11-13·成交在下一交易日开盘）",
        "- 出处：`results/etf_book_order/TICKET-2026-11-13.json`"
        "（generated 2026-11-13T10:00:00·cutoff 2026-11-13）",
    ])
    c9 = census(d9, p9)
    dc9 = c9["date_claims"]
    leg("L9 ticket provenance dates are read, not left unmapped",
        dc9.get("n_unmapped") == 0 and dc9.get("n_mismatch") == 0
        and any(r.get("field") == "etf_order.decision_bar"
                for r in dc9.get("claims") or []),
        "unmapped=%s mismatch=%s fields=%s"
        % (dc9.get("n_unmapped"), dc9.get("n_mismatch"),
           sorted({r.get("field") for r in dc9.get("claims") or []})))
    leg("L9b the file-name date is bucketed as an identifier, never counted as checked",
        (dc9.get("buckets") or {}).get("identifier", 0) >= 1, dc9.get("buckets"))

    d10 = dict(d9)
    d10["etf_order"] = dict(d9["etf_order"], bar="2026-11-12")
    c10 = census(d10, p9)
    leg("L10 a provenance date the field does not carry is a mismatch",
        c10["verdict"] == "PRINTED_DATE_MISMATCH", c10["verdict"])

    # L11 (r1849) section 6's premium sentence: the producer now stamps the premium face's own
    # session, so the line is self-dated and the date is read against that field. All three
    # shapes are pinned -- stamped and read, stamped but the field carries another day, and the
    # old bare today-word -- because the failure this round removed was a line nobody could
    # read, and the failure a lazy fix would add is a rule that matches the shape but never
    # reads the field (r1471 family).
    d11 = doc(day="2026-11-13", bar="2026-11-13", prior="2026-11-12")
    d11["etf_premium"] = {"ticket_session": "2026-11-13"}
    _prem = ("- 白话：¥4,342 约等于这本书 12.29% 年化产出的 **0.1 年**。"
             "溢价不是手续费；而且")
    p11 = page(day="2026-11-13", bar="2026-11-13", prior="2026-11-12", amount="1,234") + "\n" + (
        _prem + "在 2026-11-13 这一档，159655 正站在它自己一年里最贵的那一头")
    c11 = census(d11, p11)
    dc11 = c11["date_claims"]
    leg("L11 the stamped premium sentence is self-dated and read, not left unmapped",
        dc11.get("n_unmapped") == 0 and dc11.get("n_mismatch") == 0
        and any(r.get("field") == "etf_premium.ticket_session"
                for r in dc11.get("claims") or []),
        "unmapped=%s fields=%s" % (dc11.get("n_unmapped"),
                                   sorted({r.get("field") for r in dc11.get("claims") or []})))
    d11b = dict(d11)
    d11b["etf_premium"] = {"ticket_session": "2026-11-12"}
    c11b = census(d11b, p11)
    leg("L11b a premium date the face does not carry is a mismatch",
        c11b["verdict"] == "PRINTED_DATE_MISMATCH", c11b["verdict"])
    c11c = census(d11, page(day="2026-11-13", bar="2026-11-13", prior="2026-11-12",
                            amount="1,234") + "\n" + _prem
                  + "今天 159655 正站在它自己一年里最贵的那一头")
    leg("L11c a bare today-word on the premium line is reported, not passed",
        c11c["verdict"] == "PRINTED_BUT_UNANCHORED",
        "%s undated=%s" % (c11c["verdict"], c11c["printed"].get("n_undated")))

    # L12 (r1849) the provenance lines the carry section prints. With the last bare today-word
    # gone this face exposed 20 dates no rule claimed; each now maps to a field the page already
    # carries. Pinned both ways: the line is read (not unmapped) AND a date the face does not
    # carry is a mismatch -- a rule that matches the shape but reads nothing would pass the
    # first half alone (r1471 family).
    d12 = doc(day="2026-11-18", bar="2026-11-18", prior="2026-11-17")
    d12["carry_margin"] = {"source_generated": "2026-11-18T16:10:55+0800",
                           "evidence_cutoff": "2026-11-18"}
    d12["carry_roll_cost"] = {"source_generated": "2026-11-18T16:08:50",
                              "evidence_cutoff": "2026-11-18"}
    d12["carry_marks"] = {"source_generated": "2026-11-18T16:56:04",
                          "evidence_cutoff": "2026-11-17"}
    p12 = page(day="2026-11-18", bar="2026-11-18", prior="2026-11-17", amount="1,234") + "\n" + "\n".join([
        "- 出处：`results/idx_fut_carry_margin.json`｜generated 2026-11-18T16:10:55+0800"
        "｜cutoff 2026-11-18｜保证金率=规则参数扫描（非本书测度）",
        "- 出处：`results/idx_fut_carry_risk.json`｜generated 2026-11-18T16:08:50｜cutoff 2026-11-18",
        "- 出处：`results/futures_book_marks.json`｜generated 2026-11-18T16:56:04｜cutoff 2026-11-17",
    ])
    c12 = census(d12, p12)
    dc12 = c12["date_claims"]
    _f12 = sorted({r.get("field") for r in dc12.get("claims") or []})
    leg("L12 the carry provenance dates are read, not left unmapped",
        dc12.get("n_unmapped") == 0 and dc12.get("n_mismatch") == 0
        and "carry_margin.source_generated" in _f12
        and "carry_margin.evidence_cutoff" in _f12
        and "carry_marks.evidence_cutoff" in _f12,
        "unmapped=%s mismatch=%s fields=%s"
        % (dc12.get("n_unmapped"), dc12.get("n_mismatch"), _f12))
    d12b = dict(d12)
    d12b["carry_margin"] = {"source_generated": "2026-11-18T16:10:55+0800",
                            "evidence_cutoff": "2026-11-17"}
    c12b = census(d12b, p12)
    leg("L12b a carry cutoff the face does not carry is a mismatch",
        c12b["verdict"] == "PRINTED_DATE_MISMATCH"
        and any(r.get("field") == "carry_margin.evidence_cutoff"
                for r in c12b["date_claims"].get("mismatches") or []),
        "%s mismatches=%s" % (c12b["verdict"],
                              [(r.get("field"), r.get("date"), r.get("expected"))
                               for r in c12b["date_claims"].get("mismatches") or []]))

    print("live_usage_day_words selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1

def _safe_stdout():
    """The page carries U+00A5 (¥) inside quoted lines; a GBK console raises
    UnicodeEncodeError mid-report and the chain reads a crash as rc=1 (r1310).
    Keep the console's own encoding, only stop it from raising."""
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass


def main(argv):
    _safe_stdout()
    arg = (argv[1] if len(argv) > 1 else "run").strip()
    if arg in ("--selftest", "selftest"):
        return selftest()
    if arg == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
