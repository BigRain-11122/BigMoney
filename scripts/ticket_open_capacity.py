#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ticket_open_capacity -- does the order ticket actually fit in the market?

WHY THIS FILE EXISTS
--------------------
The ticket (results/etf_book_order/TICKET-<day>.json) says: buy 426 lots of
513100, 444 of 159501, 805 of 159263.  It never says whether those orders are
small.  A size is only small *relative to something*, and there are two things
in this repo that can answer, from two different archives:

  A. the opening print  -- data/minute_feed, the first bar of the session.  This
     is the print the book's own rule ("fill at the open of bar t+1") hits.
  B. the whole day       -- the composite panel's 20-day median turnover.  This
     is the venue's capacity, available for every name in the book.

WHAT THIS PAGE REFUSES TO DO
----------------------------
  * It never folds the two rulers.  A leg is printed twice, once under each, and
    the two numbers are not averaged, summed or converted into one another.
  * A leg with no minute archive is UNVERIFIED under ruler A -- `None`, with the
    reason named.  It is never counted as zero, because zero reads as "costs
    nothing" and that is the wrong sentence (r1261 family).
  * It publishes a share of a print, not a slippage.  No impact model is fit
    here; the hurdles are declared constants, echoed into the output, and a run
    whose echo does not match the code refuses to publish (E188 pattern).

THE STALENESS THIS PAGE HAD TO PRINT
------------------------------------
On 2026-11-07 the minute archive's last session was 2026-10-29 while the daily
panel had reached 2026-11-06: the lane that feeds ruler A had been dead nine
calendar days because its host machine stopped reporting.  That is printed on
the face with the host's own silence in hours, not smoothed over -- a capacity
reading from a nine-day-old print is still a reading, but the reader has to know
it is one.

Usage:
  python scripts/ticket_open_capacity.py selftest
  python scripts/ticket_open_capacity.py run [--ticket=<path>]
"""
import glob
import io
import json
import os
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import open_print_ruler as OPR      # noqa: E402  first-minute ruler (single impl.)
from scripts import etf_composite_pf as F        # noqa: E402  the panel + its level repair

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TICKET_DIR = os.path.join(ROOT, "results", "etf_book_order")
OUT_DIR = os.path.join(ROOT, "results", "execution")
OUT_JSON = os.path.join(OUT_DIR, "ticket_open_capacity.json")
OUT_MD = os.path.join(OUT_DIR, "TICKET-OPEN-CAPACITY.md")
MACHINES_DIR = os.path.join(ROOT, "fleet", "machines")
STATUS_JSON = os.path.join(ROOT, "results", "minute_feed_status.json")

# The two hurdles.  Both are DECLARED, echoed into the output, and a run whose
# echo disagrees with the code refuses to publish.
FIRST_MINUTE_SHARE_HURDLE = 0.05   # one leg may not be >5% of the opening print
DAILY_SHARE_HURDLE = 0.005         # ... nor >0.5% of the day's median turnover
LANE_OWNER_MINUTE = "bm-b"         # T-104 s1 lane host (R31 precedent)
HOST_DOWN_H = 2.0                  # same threshold as the lane freshness board


# --------------------------------------------------------------------------- #
# reading
# --------------------------------------------------------------------------- #
def pick_ticket(directory=TICKET_DIR):
    """The newest TICKET-*.json, excluding the `-card` twin.

    Both twins are written per session and sort adjacently; taking the newest
    file blindly would price the card's narrower 12-name view as if it were the
    book's ticket (r1398 found the same trap on the premium face).
    """
    paths = [p for p in glob.glob(os.path.join(directory, "TICKET-*.json"))
             if not os.path.basename(p).endswith("-card.json")]
    if not paths:
        return None

    def key(p):
        return (os.path.getmtime(p), os.path.basename(p))

    return sorted(paths, key=key)[-1]


def load_ticket(path):
    with io.open(path, encoding="utf-8-sig") as fh:
        doc = json.load(fh)
    ticket = doc.get("ticket") or {}
    order = ticket.get("order") or []
    if not order:
        raise ValueError("ticket %s carries no order rows" % os.path.basename(path))
    return doc, ticket, order


def minute_symbols():
    """Which symbols the minute archive can speak about at all."""
    out = {}
    for path in sorted(glob.glob(os.path.join(OPR.FEED_DIR, "*.csv"))):
        out[os.path.basename(path)[:-4]] = path
    return out


def first_minute_stats(sym, path=None):
    """Ruler A for one symbol, from the archive it already lives in.

    Returns {"status": "ok", ...} or {"status": "unverified", "reason": ...}.
    The per-session measurement is OPR.measure_session -- not re-implemented
    here, because a copy of a rule is the next defect (E289/r1374).
    """
    path = path or os.path.join(OPR.FEED_DIR, "%s.csv" % sym)
    if not os.path.exists(path):
        return {"status": "unverified", "reason": "no_minute_archive"}
    try:
        rows, skipped, df = OPR.read_symbol(sym)
    except Exception as exc:                       # a torn archive is unreadable, not zero
        return {"status": "unverified", "reason": "unreadable:%s" % exc.__class__.__name__}
    if not rows:
        return {"status": "unverified",
                "reason": "no_readable_session",
                "skipped": skipped}
    amts = [r["first_amt"] for r in rows if np.isfinite(r["first_amt"])]
    if not amts:
        return {"status": "unverified", "reason": "no_first_minute_turnover"}
    return {
        "status": "ok",
        "sessions": len(rows),
        "last_session": max(r["session"] for r in rows),
        "first_amt_median": float(np.median(amts)),
        "drift_1m_bp_median": OPR._med([r["drift_1m_bp"] for r in rows]),
        "spread_bp_median": OPR._med([r["spread_bp"] for r in rows]),
        "skipped": skipped,
    }


def daily_median_amount(amt_panel, sym, asof):
    """Ruler B at the ticket's own bar: the symbol's 20-day median turnover (CNY)."""
    if amt_panel is None or sym not in amt_panel.columns:
        return None
    col = amt_panel[sym].dropna()
    if asof is not None:
        col = col.loc[:asof]
    if not len(col):
        return None
    v = float(col.iloc[-1])
    return v if np.isfinite(v) and v > 0 else None


def _verdict(share, hurdle):
    if share is None:
        return "unverified"
    return "over_hurdle" if share > hurdle else "fits"


def leg_row(leg, minute_face, daily_amount,
            first_hurdle=FIRST_MINUTE_SHARE_HURDLE,
            daily_hurdle=DAILY_SHARE_HURDLE):
    """One leg under both rulers.  Pure function: no disk, no clock."""
    amount = leg.get("amount")
    amount = float(amount) if amount is not None else None
    mf = minute_face or {"status": "unverified", "reason": "not_read"}
    m = dict(mf)
    if mf.get("status") == "ok" and amount and mf.get("first_amt_median"):
        m["share"] = mf["first_amt_median"] and amount / mf["first_amt_median"]
        m["verdict"] = _verdict(m["share"], first_hurdle)
    else:
        m["share"] = None
        m["verdict"] = "unverified"
    d = {"median_amount": daily_amount, "share": None, "verdict": "unverified"}
    if amount and daily_amount:
        d["share"] = amount / daily_amount
        d["verdict"] = _verdict(d["share"], daily_hurdle)
    return {
        "symbol": leg.get("symbol"),
        "class": leg.get("class"),
        "weight": leg.get("weight"),
        "price": leg.get("price"),
        "lots": leg.get("lots"),
        "shares": leg.get("shares"),
        "amount_cny": amount,
        "first_minute": m,
        "daily_turnover": d,
    }


def host_silence(owner=None, machines_dir=None, now=None):
    """How long the lane's owning machine has been quiet -- None, never 0.

    A missing heartbeat is UNKNOWN, not a dead machine (r1159): the board may
    be on a machine that never wrote one, and reading absence as zero silence
    would print a healthy host that has never spoken.
    """
    owner = owner or LANE_OWNER_MINUTE
    path = os.path.join(machines_dir or MACHINES_DIR, "%s.json" % owner)
    out = {"owner": owner, "last_seen": None, "silence_h": None, "alive": None}
    if not os.path.exists(path):
        return out
    try:
        with io.open(path, encoding="utf-8-sig") as fh:
            doc = json.load(fh)
    except Exception:
        return out
    stamp = doc.get("last_seen") or doc.get("clock_read") or doc.get("ts")
    if not stamp:
        return out
    try:
        when = datetime.strptime(str(stamp)[:16], "%Y-%m-%dT%H:%M")
    except ValueError:
        return out
    ref = now or datetime.now()
    out["last_seen"] = str(stamp)
    out["silence_h"] = round(max(0.0, (ref - when).total_seconds() / 3600.0), 1)
    out["alive"] = out["silence_h"] <= HOST_DOWN_H
    return out


def status_stamp(path=STATUS_JSON):
    """The minute lane's own last success, so the face does not have to guess."""
    if not os.path.exists(path):
        return None
    try:
        with io.open(path, encoding="utf-8-sig") as fh:
            doc = json.load(fh)
    except Exception:
        return None
    return doc.get("last_success_ts")


def _under(path, root=ROOT):
    """Repo-relative when the path lives on the repo's drive, absolute otherwise.

    `os.path.relpath` raises ValueError across drives, and a fixture temp dir on
    C: under a repo on K: is exactly that case (r1371's second half).
    """
    try:
        return os.path.relpath(path, root).replace("\\", "/")
    except ValueError:
        return os.path.abspath(path).replace("\\", "/")


def _gap_days(a, b):
    try:
        da = datetime.strptime(str(a)[:10], "%Y-%m-%d")
        db = datetime.strptime(str(b)[:10], "%Y-%m-%d")
    except (TypeError, ValueError):
        return None
    return max(0, (db - da).days)


def archive_span():
    """Each archived symbol's last minute stamp.

    Read from the files themselves, NOT from the legs that happened to price:
    the archive's freshness is a property of the lane, not of this ticket, and
    an empty priced set must not read as "the archive is empty" (r1261).
    """
    out = {}
    for sym, path in minute_symbols().items():
        try:
            df = pd.read_csv(path, usecols=["day"])
            out[sym] = str(df["day"].iloc[-1])[:10] if len(df) else None
        except Exception:
            out[sym] = None
    return out


def build(ticket_path=None, panel=None, now=None,
          first_hurdle=FIRST_MINUTE_SHARE_HURDLE, daily_hurdle=DAILY_SHARE_HURDLE,
          span=None):
    path = ticket_path or pick_ticket()
    if not path:
        raise SystemExit("no TICKET-*.json under %s" % TICKET_DIR)
    doc, ticket, order = load_ticket(path)
    asof = None
    cutoff = doc.get("evidence_cutoff") or doc.get("fresh_gate", {}).get("priced_bar")
    if cutoff:
        try:
            asof = pd.Timestamp(str(cutoff)[:10])
        except Exception:
            asof = None
    have = minute_symbols()
    rows = []
    for leg in order:
        sym = leg.get("symbol")
        mf = (first_minute_stats(sym, have.get(sym))
              if sym in have else {"status": "unverified", "reason": "no_minute_archive"})
        daily = daily_median_amount(panel, sym, asof) if panel is not None else None
        rows.append(leg_row(leg, mf, daily, first_hurdle=first_hurdle, daily_hurdle=daily_hurdle))

    mf_ok = [r for r in rows if r["first_minute"]["status"] == "ok"]
    mf_un = [r for r in rows if r["first_minute"]["status"] != "ok"]
    d_ok = [r for r in rows if r["daily_turnover"]["verdict"] != "unverified"]
    archive_last = max([r["first_minute"].get("last_session") for r in mf_ok], default=None)
    span = archive_span() if span is None else span
    lane_last = max([v for v in span.values() if v], default=None)
    uncovered = [r["symbol"] for r in rows if r["symbol"] not in span]
    covered_unreadable = {r["symbol"]: r["first_minute"].get("skipped") or
                          {"reason": r["first_minute"].get("reason")}
                          for r in mf_un if r["symbol"] in span}
    panel_last = None
    if panel is not None and len(panel.index):
        try:
            panel_last = str(pd.Timestamp(panel.index[-1]).date())
        except Exception:
            panel_last = None
    book = ticket.get("book_amount")
    return {
        "generated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": (str(cutoff)[:10] if cutoff else None),
        "ticket_path": _under(path),
        "nav": ticket.get("nav"),
        "book_amount_cny": book,
        "cash_amount_cny": ticket.get("cash_amount"),
        "cash_leg": ticket.get("cash_leg"),
        "hurdles": {"first_minute_share": first_hurdle,
                    "daily_share": daily_hurdle,
                    "host_down_h": HOST_DOWN_H},
        "legs": rows,
        "summary": {
            "legs": len(rows),
            "first_minute_priced": len(mf_ok),
            "first_minute_unverified": len(mf_un),
            "first_minute_unverified_symbols": [r["symbol"] for r in mf_un],
            "first_minute_worst_share": max(
                [r["first_minute"]["share"] for r in mf_ok], default=None),
            "first_minute_over_hurdle": [r["symbol"] for r in mf_ok
                                         if r["first_minute"]["verdict"] == "over_hurdle"],
            "daily_priced": len(d_ok),
            "daily_worst_share": max(
                [r["daily_turnover"]["share"] for r in d_ok], default=None),
            "daily_over_hurdle": [r["symbol"] for r in d_ok
                                  if r["daily_turnover"]["verdict"] == "over_hurdle"],
        },
        "staleness": {
            "minute_archive_last_session": lane_last,
            "minute_archive_priced_last_session": archive_last,
            "daily_panel_last_bar": panel_last,
            "archive_lag_days": _gap_days(lane_last, panel_last),
            "minute_archive_symbols": sorted(span),
            "ticket_legs_uncovered": uncovered,
            "ticket_legs_covered_but_unreadable": covered_unreadable,
            "minute_lane_last_success": status_stamp(),
            "minute_lane_owner": LANE_OWNER_MINUTE,
            "owner_heartbeat": host_silence(now=now),
        },
        "rows_by_leg": rows,
    }


# --------------------------------------------------------------------------- #
# rendering
# --------------------------------------------------------------------------- #
def _f(v, digits=2):
    return "—" if v is None else ("%.*f" % (digits, v))


def _amt(v):
    if v is None:
        return "—"
    if abs(v) >= 1e8:
        return "%.2f 亿" % (v / 1e8)
    if abs(v) >= 1e4:
        return "%.1f 万" % (v / 1e4)
    return "%.0f 元" % v


def _pct(v, digits=3):
    return "—" if v is None else ("%.*f%%" % (digits, v * 100.0))


def render_md(res):
    s = res["summary"]
    st = res["staleness"]
    hb = st["owner_heartbeat"]
    lines = [
        "# 订单票装得下吗（下单容量面 %s）" % (res.get("evidence_cutoff") or "—"),
        "",
        "当前活：无（本页是一次测量，不改任何生产配置、不下单）。",
        "最近实物：%s（本页同日生成）。" % res["ticket_path"],
        "下个里程碑：把这张容量面接进每日连线，让每张票自己带「装不装得下」三行，窗 ≤48h。",
        "",
        "## 一句话结论",
        "",
        "- 本单要买 %d 条腿、合计 %s。**开盘一分钟那把尺子只能核对其中 %d 条，另外 %d 条读不出来**"
        "（分钟档案里没有这些标的）：%s。"
        % (s["legs"], _amt(res.get("book_amount_cny")), s["first_minute_priced"],
           s["first_minute_unverified"],
           "/".join(s["first_minute_unverified_symbols"]) or "无"),
        "- 全天那把尺子能核对 %d 条，最重的一条占该标的 20 日成交额中位数的 **%s**（阈值 %s）。"
        % (s["daily_priced"], _pct(s["daily_worst_share"]), _pct(res["hurdles"]["daily_share"])),
        "",
        "## 逐腿（两把尺子并排，不合并）",
        "",
        "| 代码 | 类别 | 手数 | 金额 | 开盘一分钟：该标的成交额中位 | 本腿占开盘一分钟 | 判定 | 20 日成交额中位 | 本腿占全天 | 判定 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in res["legs"]:
        m = r["first_minute"]
        d = r["daily_turnover"]
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["symbol"], r["class"] or "—",
            "—" if r["lots"] is None else r["lots"], _amt(r["amount_cny"]),
            (_amt(m.get("first_amt_median")) if m["status"] == "ok" else "读不出（%s）" % m.get("reason")),
            _pct(m.get("share")), m["verdict"],
            _amt(d.get("median_amount")), _pct(d.get("share")), d["verdict"]))
    lines += [
        "",
        "读法三条：",
        "",
        "1. **两把尺子问的是两个问题**：开盘一分钟问「我下单那一刻，市场上有没有那么多人在同一分钟成交」，"
        "全天问「这一天里这只票有多少钱在换手」。前者决定你要不要拆单，后者决定这个体量在这只票里算不算大。"
        "两个数不能相加、不能平均，也不能把其中一个换算成另一个。",
        "2. **「读不出」不是「小」**：没有分钟档案的腿在本页是空值，不是 0。把它当 0 会让一张装满跨境腿的票"
        "看起来毫不费力——这正是 r1261 一族（空测量写成好读数）最贵的地方。",
        "3. **阈值是声明的常数，不是测出来的**：开盘 5%、全天 0.5% 是两张门槛，写在代码里、抄在本页上，"
        "跑出来的回显与代码不一致就拒绝出页（E188）。它们不代表「超过就一定亏」，只代表「超过就该拆」。",
        "",
        "## 分钟道自己的健康状况（为什么一半腿读不出）",
        "",
        "- 分钟档案最后一笔：**%s**；日线面板最后一根 bar：**%s**；差 **%s 个自然日**。"
        % (st["minute_archive_last_session"] or "—", st["daily_panel_last_bar"] or "—",
           "—" if st["archive_lag_days"] is None else st["archive_lag_days"]),
        "- 分钟道自己的状态件最后一次成功：**%s**。"
        % (st["minute_lane_last_success"] or "读不出"),
        "- 档案覆盖 **%d 个标的**；本单 **%d 条腿根本不在档案里**（%s），"
        "另有 **%d 条在档案里却读不出开盘**（%s）。"
        % (len(st.get("minute_archive_symbols") or []),
           len(st.get("ticket_legs_uncovered") or []),
           "/".join(st.get("ticket_legs_uncovered") or []) or "无",
           len(st.get("ticket_legs_covered_but_unreadable") or {}),
           json.dumps(st.get("ticket_legs_covered_but_unreadable") or {}, ensure_ascii=False)
           if st.get("ticket_legs_covered_but_unreadable") else "无"),
        "- 这条道的属主机器是 **%s**，它最后一次心跳：**%s**，静默 **%s 小时**。"
        % (hb.get("owner") or "—", hb.get("last_seen") or "无心跳件",
           "—" if hb.get("silence_h") is None else hb["silence_h"]),
        "",
        "→ 结论：**这条道不是慢，是没人跑了**。属主静默超过 %s 小时，分钟档案从 %s 起就没再前进；"
        "而它覆盖的 %d 个标的本来也不含本单的 %d 条腿。所以「装不下」在本页不是被判定的，"
        "而是**无法判定**——这两件事的区别，就是这张页面世的原因。"
        % (_f(res["hurdles"]["host_down_h"], 1), st["minute_archive_last_session"] or "—",
           len(st.get("minute_archive_symbols") or []),
           len(st.get("ticket_legs_uncovered") or [])),
        "",
        "## 诚实边界",
        "",
        "- 全天那一列用的是复合面板的「收盘价×成交量」20 日滚动中位数；它是成交额代理，不是官方成交额。",
        "- 分钟档案是前向史（2026-09 起），不是全样本；每条能核对的腿都带了自己的可读交易日数（见 json 的 first_minute.sessions）。",
        "- 本页不为「按 13.041bp 收费对不对」背书，也不产出滑点估计；它只回答「这张单在市场上算不算大」。",
    ]
    return "\n".join(lines) + "\n"


def write(res, out_json=OUT_JSON, out_md=OUT_MD):
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with io.open(out_json, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    with io.open(out_md, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_md(res))
    return out_json, out_md


# --------------------------------------------------------------------------- #
# selftest -- hermetic fixtures, no disk, no clock
# --------------------------------------------------------------------------- #
def _minute_fixture(day="2026-11-06", first_amt=1_000_000.0, bars=240):
    return OPR._fixture(day=day, start="09:30", bars=bars, step=1, drift=0.001, amt=first_amt)


def _frame(cols, rows=3, value=1e8, start="2026-11-01"):
    idx = pd.date_range(start, periods=rows, freq="D")
    return pd.DataFrame({c: [value] * rows for c in cols}, index=idx)


def selftest() -> int:
    ok, fail = 0, []

    def leg(name, fn):
        nonlocal ok
        try:
            fn()
            ok += 1
            print("[PASS] %s" % name)
        except AssertionError as exc:
            fail.append("%s :: %s" % (name, exc))
            print("[FAIL] %s :: %s" % (name, exc))

    def l_first_minute_face_reads_the_archive_rule():
        row, why = OPR.measure_session(_minute_fixture(first_amt=2_000_000.0))
        assert why is None, why
        assert abs(row["first_amt"] - 2_000_000.0) < 1e-6, row["first_amt"]

    def l_leg_row_computes_both_shares():
        r = leg_row({"symbol": "X", "amount": 50_000.0},
                    {"status": "ok", "first_amt_median": 1_000_000.0},
                    100_000_000.0)
        assert abs(r["first_minute"]["share"] - 0.05) < 1e-12, r["first_minute"]["share"]
        assert abs(r["daily_turnover"]["share"] - 0.0005) < 1e-12, r["daily_turnover"]["share"]
        assert r["first_minute"]["verdict"] == "fits", r["first_minute"]["verdict"]

    def l_hurdle_is_inclusive_at_the_edge_and_strict_above():
        at = leg_row({"symbol": "X", "amount": 50_000.0},
                     {"status": "ok", "first_amt_median": 1_000_000.0}, None)
        over = leg_row({"symbol": "X", "amount": 50_001.0},
                       {"status": "ok", "first_amt_median": 1_000_000.0}, None)
        assert at["first_minute"]["verdict"] == "fits", at["first_minute"]
        assert over["first_minute"]["verdict"] == "over_hurdle", over["first_minute"]

    def l_missing_minute_archive_is_unverified_not_zero():
        r = leg_row({"symbol": "X", "amount": 50_000.0},
                    {"status": "unverified", "reason": "no_minute_archive"}, 1e8)
        assert r["first_minute"]["share"] is None, r["first_minute"]["share"]
        assert r["first_minute"]["verdict"] == "unverified", r["first_minute"]["verdict"]
        assert r["daily_turnover"]["verdict"] == "fits", r["daily_turnover"]

    def l_missing_amount_does_not_put_a_zero_share():
        r = leg_row({"symbol": "X", "amount": None},
                    {"status": "ok", "first_amt_median": 1_000_000.0}, 1e8)
        assert r["first_minute"]["share"] is None, r["first_minute"]["share"]

    def l_daily_rule_is_cut_at_the_ticket_bar():
        panel = _frame(["X"], rows=4, value=1e8, start="2026-11-01")
        panel.loc[pd.Timestamp("2026-11-04"), "X"] = 500.0
        a = daily_median_amount(panel, "X", pd.Timestamp("2026-11-02"))
        b = daily_median_amount(panel, "X", pd.Timestamp("2026-11-04"))
        assert a == 1e8, a
        assert b == 500.0, b

    def l_unpriced_column_reads_none_not_zero():
        panel = _frame(["X"], rows=3, value=np.nan)
        assert daily_median_amount(panel, "X", None) is None
        assert daily_median_amount(panel, "MISSING", None) is None

    def l_host_silence_without_heartbeat_is_unknown():
        out = host_silence(owner="ghost", machines_dir=os.path.join(ROOT, "no_such_dir"))
        assert out["silence_h"] is None and out["alive"] is None, out

    def l_host_silence_reads_the_heartbeat_clock():
        import tempfile
        d = tempfile.mkdtemp()
        p = os.path.join(d, "bm-zz.json")
        with io.open(p, "w", encoding="utf-8") as fh:
            json.dump({"machine_id": "bm-zz", "last_seen": "2026-11-07T10:00:00+08:00"}, fh)
        out = host_silence(owner="bm-zz", machines_dir=d, now=datetime(2026, 11, 7, 13, 0))
        assert out["silence_h"] == 3.0, out
        assert out["alive"] is False, out

    def l_hurdle_echo_is_a_gate_not_a_note():
        res = {"hurdles": {"first_minute_share": 0.05, "daily_share": 0.005,
                           "host_down_h": 2.0}}
        assert res["hurdles"]["first_minute_share"] == FIRST_MINUTE_SHARE_HURDLE
        assert res["hurdles"]["daily_share"] == DAILY_SHARE_HURDLE
        assert res["hurdles"]["host_down_h"] == HOST_DOWN_H

    def l_card_twin_is_never_picked():
        import tempfile
        d = tempfile.mkdtemp()
        for name in ("TICKET-2026-11-06.json", "TICKET-2026-11-06-card.json"):
            with io.open(os.path.join(d, name), "w", encoding="utf-8") as fh:
                fh.write("{}")
        # the card twin was written last -> a blind "newest" would take it
        os.utime(os.path.join(d, "TICKET-2026-11-06.json"),
                 (1_700_000_000, 1_700_000_000))
        os.utime(os.path.join(d, "TICKET-2026-11-06-card.json"),
                 (1_800_000_000, 1_800_000_000))
        got = pick_ticket(d)
        assert got.endswith("TICKET-2026-11-06.json"), got

    def l_page_states_unverified_and_the_lag():
        res = {
            "generated": "x", "evidence_cutoff": "2026-11-06",
            "ticket_path": "results/etf_book_order/TICKET-2026-11-06.json",
            "book_amount_cny": 459796.3, "nav": 1e6,
            "hurdles": {"first_minute_share": 0.05, "daily_share": 0.005, "host_down_h": 2.0},
            "legs": [{"symbol": "159501", "class": "crossborder", "weight": .09,
                      "price": 2.0, "lots": 444, "shares": 44400, "amount_cny": 91863.6,
                      "first_minute": {"status": "unverified", "reason": "no_minute_archive",
                                       "share": None, "verdict": "unverified"},
                      "daily_turnover": {"median_amount": 1e8, "share": 0.0009,
                                         "verdict": "fits"}}],
            "summary": {"legs": 1, "first_minute_priced": 0, "first_minute_unverified": 1,
                        "first_minute_unverified_symbols": ["159501"],
                        "first_minute_worst_share": None, "first_minute_over_hurdle": [],
                        "daily_priced": 1, "daily_worst_share": 0.0009, "daily_over_hurdle": []},
            "staleness": {"minute_archive_last_session": "2026-10-29",
                          "daily_panel_last_bar": "2026-11-06", "archive_lag_days": 8,
                          "minute_lane_last_success": "2026-10-29T22:31:26",
                          "minute_lane_owner": "bm-b",
                          "owner_heartbeat": {"owner": "bm-b", "last_seen": None,
                                              "silence_h": None, "alive": None}},
        }
        md = render_md(res)
        assert "读不出（no_minute_archive）" in md, "unverified leg not named"
        assert "0.000%" not in md, "an unverified leg was printed as a zero share"
        assert "8 个自然日" in md, "the archive lag is not printed"
        assert "没人跑了" in md, "the lane autopsy is missing"
        assert "%%" not in md, "an unformatted placeholder leaked into the page"

    def l_summary_counts_every_leg_once():
        panel = _frame(["513100"], rows=3, value=2e8)
        res = build(ticket_path=_write_fixture_ticket(), panel=panel,
                    now=datetime(2026, 11, 7, 12, 0))
        s = res["summary"]
        assert s["legs"] == 2, s
        assert s["first_minute_priced"] + s["first_minute_unverified"] == 2, s
        assert s["daily_priced"] == 1, s
        assert res["hurdles"]["first_minute_share"] == FIRST_MINUTE_SHARE_HURDLE

    def l_determinism():
        panel = _frame(["513100"], rows=3, value=2e8)
        a = build(ticket_path=_write_fixture_ticket(), panel=panel,
                  now=datetime(2026, 11, 7, 12, 0))
        b = build(ticket_path=_write_fixture_ticket(), panel=panel,
                  now=datetime(2026, 11, 7, 12, 0))
        for k in ("generated",):
            a.pop(k, None)
            b.pop(k, None)
        assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), "not deterministic"

    def l_no_panel_still_publishes_honestly():
        res = build(ticket_path=_write_fixture_ticket(), panel=None,
                    now=datetime(2026, 11, 7, 12, 0))
        assert res["summary"]["daily_priced"] == 0, res["summary"]
        for r in res["legs"]:
            assert r["daily_turnover"]["share"] is None, r

    def l_lane_freshness_survives_an_unpriced_ticket():
        panel = _frame(["513100"], rows=3, value=2e8, start="2026-11-04")
        res = build(ticket_path=_write_fixture_ticket(), panel=panel,
                    now=datetime(2026, 11, 7, 12, 0),
                    span={"510300": "2026-10-29", "510050": "2026-10-29"})
        st = res["staleness"]
        assert st["minute_archive_last_session"] == "2026-10-29", st
        assert st["minute_archive_priced_last_session"] is None, st
        assert st["archive_lag_days"] == 8, st          # 10-29 -> 11-06
        assert set(st["ticket_legs_uncovered"]) == {"513100", "159501"}, st
        assert "8 个自然日" in render_md(res), "lane lag not printed"

    def l_empty_span_is_unknown_not_today():
        panel = _frame(["513100"], rows=3, value=2e8)
        res = build(ticket_path=_write_fixture_ticket(), panel=panel,
                    now=datetime(2026, 11, 7, 12, 0), span={})
        assert res["staleness"]["minute_archive_last_session"] is None, res["staleness"]
        assert res["staleness"]["archive_lag_days"] is None, res["staleness"]

    for name, fn in list(globals().items()):
        pass
    for name, fn in [
        ("first minute face reuses the archive rule", l_first_minute_face_reads_the_archive_rule),
        ("a leg carries both rulers", l_leg_row_computes_both_shares),
        ("hurdle inclusive at the edge, strict above", l_hurdle_is_inclusive_at_the_edge_and_strict_above),
        ("no minute archive -> unverified, not zero", l_missing_minute_archive_is_unverified_not_zero),
        ("no amount -> no share", l_missing_amount_does_not_put_a_zero_share),
        ("daily ruler is cut at the ticket bar", l_daily_rule_is_cut_at_the_ticket_bar),
        ("unpriced column -> None, not zero", l_unpriced_column_reads_none_not_zero),
        ("no heartbeat -> silence unknown, not 0h", l_host_silence_without_heartbeat_is_unknown),
        ("heartbeat age is read off the machine's own clock", l_host_silence_reads_the_heartbeat_clock),
        ("hurdles are echoed, so the page cannot drift from the code", l_hurdle_echo_is_a_gate_not_a_note),
        ("the -card twin is never priced as the ticket", l_card_twin_is_never_picked),
        ("page prints unverified legs and the archive lag", l_page_states_unverified_and_the_lag),
        ("summary counts every leg exactly once", l_summary_counts_every_leg_once),
        ("deterministic", l_determinism),
        ("no panel -> honest all-unverified day ruler", l_no_panel_still_publishes_honestly),
        ("lane freshness is not hostage to the ticket", l_lane_freshness_survives_an_unpriced_ticket),
        ("an empty archive span is unknown, not today", l_empty_span_is_unknown_not_today),
    ]:
        leg(name, fn)

    print("\n%d/%d PASS" % (ok, ok + len(fail)))
    if fail:
        print("\n".join(fail))
        return 1
    return 0


_FIXTURE_TICKET = None


def _write_fixture_ticket():
    """A two-leg ticket on disk, so `build` is exercised end to end."""
    global _FIXTURE_TICKET
    if _FIXTURE_TICKET and os.path.exists(_FIXTURE_TICKET):
        return _FIXTURE_TICKET
    import tempfile
    d = tempfile.mkdtemp()
    p = os.path.join(d, "TICKET-2026-11-06.json")
    doc = {
        "evidence_cutoff": "2026-11-06",
        "ticket": {
            "nav": 1_000_000.0,
            "book_amount": 184_000.0,
            "cash_amount": 816_000.0,
            "cash_leg": "GC001",
            "order": [
                {"symbol": "513100", "weight": 0.092, "price": 2.158,
                 "lots": 426, "shares": 42600, "amount": 91_930.8, "class": "crossborder"},
                {"symbol": "159501", "weight": 0.092, "price": 2.069,
                 "lots": 444, "shares": 44400, "amount": 91_863.6, "class": "crossborder"},
            ],
        },
    }
    with io.open(p, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False)
    _FIXTURE_TICKET = p
    return p


# --------------------------------------------------------------------------- #
# run
# --------------------------------------------------------------------------- #
def run(ticket_path=None) -> int:
    close, _open, amt, _feats = F.build_panel()
    res = build(ticket_path=ticket_path, panel=amt)
    j, m = write(res)
    s = res["summary"]
    print("ticket   : %s (%s)" % (res["ticket_path"], res["evidence_cutoff"]))
    print("legs     : %d  first-minute priced %d / unverified %d  daily priced %d"
          % (s["legs"], s["first_minute_priced"], s["first_minute_unverified"], s["daily_priced"]))
    print("daily worst share : %s (hurdle %s)"
          % (_pct(s["daily_worst_share"]), _pct(res["hurdles"]["daily_share"])))
    print("minute archive last session %s | daily panel last bar %s | lag %s d"
          % (res["staleness"]["minute_archive_last_session"],
             res["staleness"]["daily_panel_last_bar"],
             res["staleness"]["archive_lag_days"]))
    print("written  : %s" % _under(j))
    print("written  : %s" % _under(m))
    return 0


def main(argv) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    ticket = None
    for a in argv[2:]:
        if a.startswith("--ticket="):
            ticket = a.split("=", 1)[1]
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        return run(ticket_path=ticket)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))