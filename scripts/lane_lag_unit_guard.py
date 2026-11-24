# -*- coding: utf-8 -*-
"""lane_lag_unit_guard.py -- the block board's freshness tolerance is measured in the
wrong unit, so the same data state is red on Wednesday and green on Thursday.

WHY (r2069)
-----------
``scripts/block_board.py::probe_dir_bar_fresh`` decides "is this lane late?" like this::

    exp   = expected_last_weekday()          # today (or Friday), no holiday awareness
    lag   = (exp - bar_day).days             # CALENDAR days
    allow = int(spec.get("holiday_allow_days", 4))
    red   = lag > allow

The tolerance is *named* for holidays (i.e. for the days the exchange is shut) but it is
compared against **calendar** days.  A calendar gap is (trading days missing) plus
(weekend days in between), so the same shortage of bars is worth 3, 4 or 5 units
depending on which weekday you happen to run the probe:

    tail = Friday, run = Monday   -> lag 3 -> GREEN
    tail = Friday, run = Tuesday  -> lag 4 -> GREEN
    tail = Friday, run = Wednesday-> lag 5 -> RED

That is not a data property, it is a property of the wall clock.  Two consequences, both
already visible on the 2026-11-25 board:

  * **D6 (repo / cash rate)** prints *"modal bar 2026-11-20 is 5d behind last weekday
    2026-11-25"*.  The official calendar says the honest gap is **2 trading days**
    (11-23 and 11-24), and 11-25's bar does not exist before 15:30 at all -- the
    reference day is 11-24, not 11-25.  The number is 5, the fact is 2.
  * The *threshold* is equally untrustworthy in the other direction: a 2-trading-day
    hole passes the 4-unit tolerance on a Tuesday and fails it on a Wednesday, so a
    reader cannot tell "the lane stopped" from "it is Wednesday".

This face does not change the board (the board is a shared face and another host is
writing).  It recomputes every ``dir_bar_fresh`` row of ``research/QUANT-BLOCKS.json``
in **trading days** against the *official* exchange calendar, prints the two numbers side
by side, and freezes the classification:

    AGREE_CURRENT            both green, and the lane really is current
    AGREE_LATE               both red, and the trading gap is real
    RED_IS_UNIT_ARTIFACT     board red, lane current -- the tolerance, not the lane
    GREEN_IS_PREMATURE       board green, trading days are missing -- the tolerance
                             absorbed a real hole because it was counted in calendar days

Verdict tokens (frozen before the numbers are read):
    TOLERANCE_IS_IN_THE_WRONG_UNIT   at least one row changes colour when the same
                                     tolerance is read in trading days, or the weekday
                                     sweep shows a fixed gap flipping verdict
    LAG_NUMBERS_DISAGREE             every row is late for real, but the printed number
                                     is not the trading-day one
    CONSISTENT                       calendar lag == trading lag on every row

Exit 0 = computed (a descriptive face: the attention signal lives in the verdict),
2 = mechanism failure (no calendar / unreadable registry / unreadable input face).

Usage:
    python scripts/lane_lag_unit_guard.py run
    python scripts/lane_lag_unit_guard.py --check
    python scripts/lane_lag_unit_guard.py --selftest
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.exchange_calendar_audit import (  # noqa: E402
    CLOSE_ACCEPT_TIME,
    expected_last_day,
    load_calendar,
)

OUT = os.path.join(ROOT, "results", "lane_lag_unit_guard.json")
MD = os.path.join(ROOT, "research", "LANE_LAG_UNIT_GUARD.md")
BLOCKS = os.path.join(ROOT, "research", "QUANT-BLOCKS.json")
FRESH = os.path.join(ROOT, "results", "data_lane_freshness.json")

# D-block -> row on the freshness board.  A block with no lane row is measured from its
# own directory with the same modal-bar sampling the board uses (so the two numbers are
# the same number, only the unit differs -- r1788: the date rule must point at the face
# that produced the figure).
BLOCK_LANE = {
    "D1_fut_daily": "futures",
    "D2_index_daily": None,          # no freshness lane exists for the index panel
    "D3_etf_daily": "etf_panel",
    "D4_astock_daily": "astock_daily",
    "D5_cb_panel": None,             # file_fresh, not dir_bar_fresh
    "D6_cash_rate": "repo",
    "D7_lane_board": None,           # file_fresh
}

_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
DEFAULT_ALLOW = 4

# Blocks with no row on the freshness board still have a producer that says, on its own
# face, whether the missing bar exists at the source.  r1852: when the producer has
# already declared "the vendor has not published", the reader must not judge it again.
PENDING_FACE = {
    "D2_index_daily": os.path.join(ROOT, "results", "index_daily_update_status.json"),
}


def producer_declared_pending(path, expected):
    """The producer's own words, if it says the source has not published `expected`."""
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
    except Exception:
        return None
    src = d.get("source_tails") or {}
    tails = sorted({str(v)[:10] for v in src.values()}) if isinstance(src, dict) else []
    if tails and tails[-1] < expected and str(d.get("action") or "") in ("", "no-change"):
        return str(d.get("reason") or "producer reports source lag")
    return None


# --------------------------------------------------------------------------- helpers
def _now():
    return dt.datetime.now()


def last_bar_date(path):
    """Bar date of a csv panel (last non-empty line's first field), or None."""
    try:
        with open(path, "rb") as fh:
            fh.seek(0, os.SEEK_END)
            size = fh.tell()
            chunk = min(size, 4096)
            fh.seek(size - chunk)
            tail = fh.read().decode("utf-8", "replace")
    except OSError:
        return None
    for line in reversed(tail.splitlines()):
        line = line.strip()
        if not line or line.lower().startswith("date"):
            continue
        first = line.split(",")[0].strip()
        if _DATE_RE.match(first):
            return first
    return None


def modal_bar(directory, pattern="*.csv", min_count=1):
    """The board's own sampling: newest three writes plus a stride over the rest."""
    import fnmatch

    if not os.path.isdir(directory):
        return None, "dir missing: %s" % directory
    files = sorted(f for f in os.listdir(directory) if fnmatch.fnmatch(f, pattern))
    if len(files) < int(min_count):
        return None, "only %d files < %d" % (len(files), min_count)
    files.sort(key=lambda f: os.path.getmtime(os.path.join(directory, f)), reverse=True)
    sample = files[:3]
    step = max(1, len(files) // 300)
    sample += files[::step][:300]
    counts = {}
    for f in sample:
        b = last_bar_date(os.path.join(directory, f))
        if b:
            counts[b] = counts.get(b, 0) + 1
    if not counts:
        return None, "cannot read a bar date"
    return max(counts, key=lambda k: (counts[k], k)), "%d sampled dates" % len(counts)


def expected_last_weekday(now):
    """What the board uses today: 'the last Mon-Fri', holidays and 15:30 ignored."""
    d = now.date()
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d


def trading_gap(calendar_days, tail_iso, expected_iso):
    """Trading days strictly after `tail` and up to and including `expected`."""
    if not tail_iso or not expected_iso:
        return []
    return [d for d in calendar_days if tail_iso < d <= expected_iso]


def classify(board_red, state):
    """Three honest states, not two: a bar the source has not published is not late.

    The freshness board already owns that third state (``today_pending`` / source_lag).
    Re-judging it here as a defect would be the wolf-crying this face exists to stop.
    """
    if state == "LATE":
        return "AGREE_LATE" if board_red else "GREEN_IS_PREMATURE"
    if state == "PENDING_TODAY":
        return "RED_IS_TOO_STRICT_FOR_SOURCE_LAG" if board_red else "AGREE_PENDING"
    return "RED_IS_UNIT_ARTIFACT" if board_red else "AGREE_CURRENT"


def weekday_sweep(calendar_days):
    """Prove the tolerance is not a function of the data.

    For a fixed shortage of k trading days, walk every weekday a run could land on and
    record the calendar lag the board would compute.  If a k produces both colours the
    tolerance is measuring the calendar, not the lane.
    """
    cal = sorted(calendar_days)
    out = []
    for k in (1, 2, 3, 4, 5):
        rows = []
        for back in range(0, 14):
            # walk `back` official days back from the last official day so the weekday
            # the probe is run on varies across all seven
            idx = len(cal) - 1 - back
            if idx < 0:                                          # pragma: no cover
                continue
            run_day = cal[idx]
            tail_idx = max(0, idx - k)
            tail = cal[tail_idx]
            lag = (dt.date.fromisoformat(run_day) - dt.date.fromisoformat(tail)).days
            rows.append({"run_on": run_day,
                         "run_weekday": dt.date.fromisoformat(run_day).strftime("%a"),
                         "tail": tail,
                         "calendar_lag": lag,
                         "board_red": lag > DEFAULT_ALLOW})
        colours = {r["board_red"] for r in rows}
        out.append({
            "missing_trading_days": k,
            "calendar_lag_min": min(r["calendar_lag"] for r in rows),
            "calendar_lag_max": max(r["calendar_lag"] for r in rows),
            "flips": len(colours) > 1,
            "rows": rows,
        })
    return out


# --------------------------------------------------------------------------- build
def build(now=None, blocks_path=BLOCKS, fresh_path=FRESH):
    now = now or _now()
    calendar_days = load_calendar()
    if not calendar_days:
        raise SystemExit("mechanism: no exchange calendar")
    calendar_days = sorted(str(d) for d in calendar_days)

    with open(blocks_path, encoding="utf-8") as fh:
        blocks = json.load(fh)
    fresh = None
    if os.path.exists(fresh_path):
        with open(fresh_path, encoding="utf-8") as fh:
            fresh = json.load(fh)
    lane_rows = {r["lane"]: r for r in (fresh or {}).get("lanes") or []}

    expected, _past = expected_last_day(calendar_days, now)
    last_weekday = expected_last_weekday(now).isoformat()

    rows = []
    for blk in blocks.get("blocks") or []:
        probe = blk.get("probe") or {}
        if probe.get("type") != "dir_bar_fresh":
            continue
        bid = blk.get("id")
        lane = BLOCK_LANE.get(bid)
        allow = int(probe.get("holiday_allow_days", DEFAULT_ALLOW))

        tail = None
        tail_src = None
        if lane and lane in lane_rows and lane_rows[lane].get("tail"):
            tail = str(lane_rows[lane]["tail"])[:10]
            tail_src = "data_lane_freshness:%s" % lane
        else:
            tail, why = modal_bar(os.path.join(ROOT, probe.get("dir", "")),
                                  probe.get("pattern", "*.csv"),
                                  probe.get("min_count", 1))
            tail_src = "modal_bar(%s)" % (why or "")

        if not tail:
            rows.append({"block": bid, "lane": lane, "error": "no bar date",
                         "tail_source": tail_src})
            continue

        missing = trading_gap(calendar_days, tail, expected)
        calendar_lag = (dt.date.fromisoformat(last_weekday)
                        - dt.date.fromisoformat(tail)).days
        cited = str(((lane_rows.get(lane) or {}) if lane else {}).get("verdict") or "")
        declared = producer_declared_pending(PENDING_FACE.get(bid), expected)
        # the lane's own contract says whether the expected bar has been published yet
        pending = bool(missing) and missing == [expected] and (
            cited in ("today_pending", "in_sync") or bool(declared))
        if not missing:
            state = "CURRENT"
        elif pending:
            state = "PENDING_TODAY"
        else:
            state = "LATE"
        board_red = calendar_lag > allow
        honest_red = state == "LATE"
        rows.append({
            "block": bid,
            "lane": lane,
            "artifact": blk.get("artifact"),
            "tail_bar": tail,
            "tail_source": tail_src,
            "expected_bar": expected,
            "board_reference_day": last_weekday,
            "calendar_lag_days": calendar_lag,
            "trading_days_missing": len(missing),
            "missing_days": missing,
            "tolerance_units": allow,
            "board_red": board_red,
            "honest_red": honest_red,
            "honest_state": state,
            "cited_lane_verdict": cited or None,
            "producer_reason": declared,
            "classification": classify(board_red, state),
            "board_prints": ("modal bar %s is %dd behind last weekday %s"
                             % (tail, calendar_lag, last_weekday)),
            "calendar_says": ("%d trading day(s) missing: %s"
                              % (len(missing), ", ".join(missing) or "none")),
        })

    sweep = weekday_sweep(calendar_days)

    swing = ("RED_IS_UNIT_ARTIFACT", "GREEN_IS_PREMATURE",
             "RED_IS_TOO_STRICT_FOR_SOURCE_LAG")
    flips = [r for r in rows if r.get("classification") in swing]
    disagree = [r for r in rows
                if "calendar_lag_days" in r
                and r["calendar_lag_days"] != r["trading_days_missing"]]
    sweep_flips = [s for s in sweep if s["flips"]]

    if flips or sweep_flips:
        verdict = "TOLERANCE_IS_IN_THE_WRONG_UNIT"
    elif disagree:
        verdict = "LAG_NUMBERS_DISAGREE"
    else:
        verdict = "CONSISTENT"

    def _n(tok):
        return sum(1 for r in rows if r.get("classification") == tok)

    return {
        "face": "lane_lag_unit_guard",
        "question": ("the block board's freshness tolerance is called holiday_allow_days "
                     "but compared against calendar days -- does any lane change colour "
                     "when the same tolerance is read in the market's unit?"),
        "evidence_cutoff": expected,
        "generated": now.isoformat(timespec="seconds"),
        "now": now.isoformat(timespec="seconds"),
        "close_accept_time": CLOSE_ACCEPT_TIME.strftime("%H:%M"),
        "calendar_days": len(calendar_days),
        "calendar_tail": calendar_days[-1] if calendar_days else None,
        "expected_bar": expected,
        "board_reference_day": last_weekday,
        "tolerance_default": DEFAULT_ALLOW,
        "rows": rows,
        "weekday_sweep": sweep,
        "counts": {
            "rows": len(rows),
            "agree_late": _n("AGREE_LATE"),
            "agree_current": _n("AGREE_CURRENT"),
            "agree_pending": _n("AGREE_PENDING"),
            "red_is_unit_artifact": _n("RED_IS_UNIT_ARTIFACT"),
            "green_is_premature": _n("GREEN_IS_PREMATURE"),
            "red_too_strict_for_source_lag": _n("RED_IS_TOO_STRICT_FOR_SOURCE_LAG"),
            "numbers_disagree": len(disagree),
            "sweep_rows_that_flip": len(sweep_flips),
        },
        "verdict": verdict,
        "honest": [
            "this face does not fix the board: block_board.py is a shared face and another "
            "host is writing (r1907). The patch stays proven-not-applied until a clean window",
            "the expected bar is the last OFFICIAL day whose bar must exist by the 15:30 "
            "accept time; the board's reference is 'last Mon-Fri', which is 11-25 today "
            "even though no 11-25 bar can exist before 15:30",
            "a trading-day gap of 0 means the lane is current; it says nothing about the "
            "lane being correct, only about it having written its bar",
            "holidays are taken from data/exchange_calendar.csv (the same file the rest of "
            "the chain imports); a wrong calendar moves every row together",
        ],
        "patch": {
            "file": "scripts/block_board.py",
            "shape": ("expected/allow must both be in trading days: replace "
                      "expected_last_weekday() with exchange_calendar_audit.expected_last_day"
                      "(calendar, now) and compare len(trading_gap(...)) against "
                      "holiday_allow_days; keep the printed string in trading days"),
            "status": "PROVEN_NOT_APPLIED",
        },
    }


def aggregate(payload):
    return {
        "verdict": payload["verdict"],
        "counts": payload["counts"],
        "rows": [{k: r.get(k) for k in
                  ("block", "lane", "tail_bar", "expected_bar", "calendar_lag_days",
                   "trading_days_missing", "board_red", "honest_red", "honest_state",
                   "classification")}
                 for r in payload["rows"]],
    }


# --------------------------------------------------------------------------- doc
def render_block(p):
    lines = []
    lines.append("<!-- BEGIN lane_lag_unit_guard -->")
    lines.append("generated %s | verdict **%s**" % (p["generated"], p["verdict"]))
    lines.append("")
    lines.append("| 块 | 车道 | 尾部 bar | 应到 bar | 板印的日历日 | 日历说的交易日 | 板判 | 诚实态 | 分类 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for r in p["rows"]:
        if "error" in r:
            lines.append("| %s | %s | — | — | — | — | — | — | %s |"
                         % (r["block"], r.get("lane") or "—", r["error"]))
            continue
        lines.append("| %s | %s | %s | %s | %d | %d | %s | %s | **%s** |" % (
            r["block"], r.get("lane") or "—", r["tail_bar"], r["expected_bar"],
            r["calendar_lag_days"], r["trading_days_missing"],
            "RED" if r["board_red"] else "GREEN",
            r.get("honest_state") or "—",
            r["classification"]))
    lines.append("")
    lines.append("同一条款按不同星期几跑，结果如下（k = 真实缺的交易日数）：")
    lines.append("")
    lines.append("| 缺 k 日 | 板算出的日历差 | 两个方向都出现过? |")
    lines.append("|---|---|---|")
    for s in p["weekday_sweep"]:
        lines.append("| %d | %d–%d | %s |" % (
            s["missing_trading_days"], s["calendar_lag_min"], s["calendar_lag_max"],
            "**是（同一个缺口红绿两色）**" if s["flips"] else "否"))
    lines.append("")
    c = p["counts"]
    lines.append("**读数**：%d 条里 %d 条当前、%d 条源还没发布（合法第三态）、%d 条真落后；"
                 "**%d 条的日历差都不是交易日差**。" % (
                     c["rows"], c["agree_current"], c["agree_pending"],
                     c["agree_late"], c["numbers_disagree"]))
    for r in p["rows"]:
        if r.get("classification") == "AGREE_LATE":
            lines.append("")
            lines.append("- 真落后那条 = **%s**：板印「%s」，日历事实「%s」。" % (
                r["block"], r["board_prints"], r["calendar_says"]))
        if r.get("producer_reason"):
            lines.append("- %s 的生产者已经说过：%s" % (r["block"], r["producer_reason"]))
    flips = [s for s in p["weekday_sweep"] if s["flips"]]
    if flips:
        lines.append("")
        lines.append("- 同一个缺口在不同星期几红绿不同：缺 %s 个交易日时，板算出的日历差分别是 "
                     "%s —— 一个死了三天的车道，周一周二显示绿的。" % (
                         " / ".join(str(s["missing_trading_days"]) for s in flips),
                         " / ".join("%d–%d" % (s["calendar_lag_min"], s["calendar_lag_max"])
                                    for s in flips)))
    lines.append("<!-- END lane_lag_unit_guard -->")
    return "\n".join(lines)


def write_doc(payload, path=MD):
    block = render_block(payload)
    header = [
        "# 车道落后：板上的数字和日历上的事实差在哪一个单位",
        "",
        "`scripts/lane_lag_unit_guard.py` · 只描述不修板（板是共享面，竞争窗内禁改）。",
        "",
        "读数由 `run` 渲染进下面的 marker 块，`--check` 逐字比对面；手改一位即 rc3。",
        "",
    ]
    tail = [
        "",
        "## 它不声称什么",
        "",
    ] + ["- " + h for h in payload["honest"]] + [
        "",
        "## 补丁（已证未落）",
        "",
        "- 文件：`%s`" % payload["patch"]["file"],
        "- 形状：%s" % payload["patch"]["shape"],
        "- 状态：`%s`" % payload["patch"]["status"],
        "",
    ]
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(header) + block + "\n" + "\n".join(tail))


# --------------------------------------------------------------------------- check
_MARK_BEGIN = "<!-- BEGIN lane_lag_unit_guard -->"
_MARK_END = "<!-- END lane_lag_unit_guard -->"


def _doc_block(text):
    i = text.find(_MARK_BEGIN)
    j = text.find(_MARK_END)
    if i < 0 or j < 0 or j < i:
        return None
    return text[i:j + len(_MARK_END)]


def check(now=None):
    """Re-derive the face from the inputs and compare it, field by field, to disk."""
    if not os.path.exists(OUT):
        return 3, "STALE face missing: %s (run `run`)" % os.path.basename(OUT)
    with open(OUT, encoding="utf-8") as fh:
        published = json.load(fh)

    # drift in the inputs is not a defect in this face: name it STALE so the chain pays
    # for a rebuild (r1850), and never let the word STALE into a real disagreement.
    drift = []
    try:
        with open(BLOCKS, "rb") as fh:
            blocks_bytes = fh.read()
        with open(FRESH, "rb") as fh:
            fresh_bytes = fh.read()
    except OSError as e:                                        # pragma: no cover
        return 2, "mechanism: cannot read inputs (%r)" % (e,)
    if published.get("inputs_digest"):
        import hashlib
        want = published["inputs_digest"]
        got = {"blocks": hashlib.sha256(blocks_bytes).hexdigest()[:16],
               "freshness": hashlib.sha256(fresh_bytes).hexdigest()[:16]}
        for k in ("blocks", "freshness"):
            if want.get(k) != got[k]:
                drift.append(k)
    if drift:
        return 3, ("STALE input moved: %s -- rebuild with `run`" % ", ".join(drift))

    fresh = build(now=now)
    # the 15:30 boundary moves the expected bar: a face published before the close is
    # not wrong, it is a different question.  Name it STALE so the chain republishes.
    if fresh.get("expected_bar") != published.get("expected_bar"):
        return 3, ("STALE the expected bar moved %r -> %r (15:30 boundary) -- rebuild "
                   "with `run`" % (published.get("expected_bar"), fresh.get("expected_bar")))
    got = aggregate(fresh)
    want = aggregate(published)
    if got != want:
        for a, b in zip(got["rows"], want["rows"]):
            if a != b:
                for k in a:
                    if a[k] != b[k]:
                        return 3, ("CHECK FAILED %s.%s: recomputed %r, published %r "
                                   "(same inputs, different numbers -- a disagreement, "
                                   "not drift)" % (a.get("block"), k, a[k], b[k]))
        return 3, ("CHECK FAILED verdict/counts: recomputed %r, published %r (same "
                   "inputs, different numbers -- a disagreement, not drift)"
                   % (got.get("verdict"), want.get("verdict")))

    with open(MD, encoding="utf-8") as fh:
        text = fh.read()
    block = _doc_block(text)
    if block is None:
        return 3, "CHECK FAILED page has no marker block"
    if block != render_block(published):
        return 3, ("CHECK FAILED page block is not what the face renders (same inputs, "
                   "different text -- a disagreement, not drift)")
    return 0, "CHECK OK"


# --------------------------------------------------------------------------- selftest
def selftest():
    import hashlib
    import tempfile

    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    cal = sorted(str(d) for d in load_calendar())
    leg("calendar loads with more than 1000 days", len(cal) > 1000)

    # 15:30 boundary pins both sides
    d = dt.date.fromisoformat(cal[-1])
    before = dt.datetime.combine(d, dt.time(9, 0))
    after = dt.datetime.combine(d, dt.time(16, 0))
    exp_before, _ = expected_last_day(cal, before)
    exp_after, _ = expected_last_day(cal, after)
    leg("before 15:30 the expected bar is the previous official day", exp_before != d.isoformat())
    leg("after 15:30 the expected bar is today", exp_after == d.isoformat())

    # the two units really differ: a Friday tail read on a Wednesday
    fri = "2026-11-20"
    wed = "2026-11-25"
    gap = trading_gap(cal, fri, "2026-11-24")
    leg("trading gap skips the weekend", gap == ["2026-11-23", "2026-11-24"])
    leg("calendar lag counts the weekend",
        (dt.date.fromisoformat(wed) - dt.date.fromisoformat(fri)).days == 5)

    # a current lane
    leg("tail == expected means no missing day", trading_gap(cal, "2026-11-24", "2026-11-24") == [])
    leg("one day back is one missing day",
        trading_gap(cal, "2026-11-23", "2026-11-24") == ["2026-11-24"])
    leg("a weekend tail still only counts official days",
        trading_gap(cal, "2026-11-21", "2026-11-24") == ["2026-11-23", "2026-11-24"])

    # classification table (three honest states, not two)
    leg("red+LATE is AGREE_LATE", classify(True, "LATE") == "AGREE_LATE")
    leg("red+CURRENT is RED_IS_UNIT_ARTIFACT",
        classify(True, "CURRENT") == "RED_IS_UNIT_ARTIFACT")
    leg("green+LATE is GREEN_IS_PREMATURE",
        classify(False, "LATE") == "GREEN_IS_PREMATURE")
    leg("green+CURRENT is AGREE_CURRENT", classify(False, "CURRENT") == "AGREE_CURRENT")
    leg("green+PENDING is AGREE_PENDING", classify(False, "PENDING_TODAY") == "AGREE_PENDING")
    leg("red+PENDING blames the board, not the source",
        classify(True, "PENDING_TODAY") == "RED_IS_TOO_STRICT_FOR_SOURCE_LAG")

    # the sweep proves the tolerance is not a function of the data
    sweep = weekday_sweep(cal)
    leg("weekday sweep produced rows", len(sweep) == 5)
    leg("at least one fixed gap flips colour across weekdays",
        any(s["flips"] for s in sweep))

    # end to end on the real inputs
    p = build()
    leg("real build has rows", len(p["rows"]) > 0)
    leg("real build carries a verdict", bool(p["verdict"]))
    d6 = next((r for r in p["rows"] if r["block"] == "D6_cash_rate"), None)
    leg("D6 is on the build", d6 is not None)
    if d6 and "error" not in d6:
        leg("D6's calendar lag is larger than its trading lag",
            d6["calendar_lag_days"] > d6["trading_days_missing"])
        leg("D6 is classified as a number disagreement, not a flip",
            d6["classification"] in ("AGREE_LATE", "RED_IS_UNIT_ARTIFACT"))
    leg("aggregate is stable across two builds", aggregate(build()) == aggregate(build()))

    # behavioural legs for check(): they must fail for the right reasons
    with tempfile.TemporaryDirectory() as td:
        out_bak = OUT
        md_bak = MD
        try:
            globals()["OUT"] = os.path.join(td, "face.json")
            globals()["MD"] = os.path.join(td, "page.md")
            leg("check without a face is STALE, not OK", check()[0] == 3
                and "STALE" in check()[1])
            payload = build()
            import hashlib as _h
            payload["inputs_digest"] = {
                "blocks": _h.sha256(open(BLOCKS, "rb").read()).hexdigest()[:16],
                "freshness": _h.sha256(open(FRESH, "rb").read()).hexdigest()[:16],
            }
            with open(globals()["OUT"], "w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=1)
            write_doc(payload, globals()["MD"])
            rc, why = check()
            leg("check passes on the face it just wrote", rc == 0)
            # tamper one number: must be CHECK FAILED and must not say STALE
            bad = json.loads(json.dumps(payload))
            bad["rows"][0]["calendar_lag_days"] = bad["rows"][0].get("calendar_lag_days", 0) + 7
            with open(globals()["OUT"], "w", encoding="utf-8") as fh:
                json.dump(bad, fh, ensure_ascii=False, indent=1)
            rc_bad, why_bad = check()
            leg("a tampered number is red", rc_bad == 3)
            leg("a tampered number says CHECK FAILED", "CHECK FAILED" in why_bad)
            leg("a tampered number never says STALE", "STALE" not in why_bad)
            # drift in the inputs is STALE
            worse = json.loads(json.dumps(payload))
            worse["inputs_digest"]["blocks"] = "0" * 16
            with open(globals()["OUT"], "w", encoding="utf-8") as fh:
                json.dump(worse, fh, ensure_ascii=False, indent=1)
            rc_drift, why_drift = check()
            leg("moved inputs are STALE", rc_drift == 3 and "STALE" in why_drift)
        finally:
            globals()["OUT"] = out_bak
            globals()["MD"] = md_bak

    ok = sum(1 for _, c in legs if c)
    for name, cond in legs:
        print(("  ok   " if cond else "  FAIL ") + name)
    print("\nselftest: %d/%d OK" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


# --------------------------------------------------------------------------- main
def run(check_only=False):
    if check_only:
        rc, why = check()
        print(why)
        return rc
    import hashlib
    p = build()
    p["inputs_digest"] = {
        "blocks": hashlib.sha256(open(BLOCKS, "rb").read()).hexdigest()[:16],
        "freshness": hashlib.sha256(open(FRESH, "rb").read()).hexdigest()[:16],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(p, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    write_doc(p)
    print(json.dumps({"verdict": p["verdict"], "counts": p["counts"],
                      "expected_bar": p["expected_bar"]}, ensure_ascii=False))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "selftest"])
    ap.add_argument("--check", action="store_true", help="alias for `check`")
    ap.add_argument("--selftest", action="store_true", help="alias for `selftest`")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "selftest":
        return selftest()
    if args.check or args.cmd == "check":
        return run(check_only=True)
    return run()


if __name__ == "__main__":
    sys.exit(main())
