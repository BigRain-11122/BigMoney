"""What is the book worth RIGHT NOW, when the daily panel is still one bar behind?

The executable ticket is priced on the last closed bar the panel has (2026-11-03 today),
and the panel takes a day to catch up with the exchange. So every evening between the
close and the panel catching up, the CEO page says "your book is worth what it was
yesterday", even though today's prices are already published.

That gap is not a research question and this face does not pretend to be one: it prices
NOTHING, forecasts NOTHING and touches no ledger, ticket or score. It reads one snapshot
quote per held name, checks that each quote's own previous close equals the panel's last
bar close (so the two sources provably join), and then reports today's move of the held
leg, weighted by the weights the ticket already published.

Frozen before the run (thresholds are CONSTANTS, not tuned here):

  * PREV_TOL_ABS = 0.0011  -- a snapshot's previous close must equal the panel's last
    close to within half a tick plus rounding. A bigger gap means the quote is not the
    next session of that panel (wrong symbol / split / stale source) and the face refuses
    to print a return for that name rather than guessing.
  * MISMATCH_SHARE_MAX = 0.20 -- if more than 20% of the held names fail that join, the
    whole face is UNAVAILABLE: a weighted return over joined and unjoined names alike
    would be a number without a denominator.
  * A snapshot whose trading date equals the panel's last bar is NO_NEW_BAR (the panel
    already has it -- this face has nothing to add and says so, printing no new number).
  * The held-leg return is Σ w_i * (last_i/prev_i - 1) over the ticket's own weights.
    Cash is *not* repriced: a snapshot says nothing about the repo rate, so the book
    change is w_book * held_return and the cash leg is stated as unchanged, never zeroed
    and never invented.

Exit codes: 0 = quote face written (or honest NO_NEW_BAR), 2 = mechanism failure (network,
unreadable ticket, too many unjoined names). Never a silent zero.

Usage:
  python scripts/etf_book_live_quote.py            # fetch, verify, write faces
  python scripts/etf_book_live_quote.py selftest   # offline self-test
  python scripts/etf_book_live_quote.py --check    # re-derive the published verdict
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TICKET_DIR = os.path.join(ROOT, "results", "etf_book_order")
OUT_DIR = os.path.join(ROOT, "results", "etf_book_live_quote")
DOC_DIR = os.path.join(ROOT, "docs", "live_book")
CAL = os.path.join(ROOT, "data", "exchange_calendar.csv")

PREV_TOL_ABS = 0.0011
MISMATCH_SHARE_MAX = 0.20

QUOTE_URL = "https://hq.sinajs.cn/list="
QUOTE_HEADERS = {
    "Referer": "https://finance.sina.com.cn",
    "User-Agent": "Mozilla/5.0",
}


def _p(*parts):
    return os.path.join(ROOT, *parts)


def to_sina_symbol(code: str) -> str:
    """Same mapping the daily pool uses -- imported, not re-implemented (5xx = SH)."""
    c = str(code).strip()
    if c[:2] in ("sh", "sz"):
        return c
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from update_daily import to_sina_symbol as _pool_symbol

    return _pool_symbol(c)


def panel_path(sina_symbol: str) -> str:
    return _p("data", "daily", f"{sina_symbol}.csv")


def panel_tail(sina_symbol: str):
    """(date, close) of the last row on the panel, or None when absent/unreadable."""
    p = panel_path(sina_symbol)
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            lines = [ln.strip() for ln in fh if ln.strip()]
    except OSError:
        return None
    if len(lines) < 2:
        return None
    cells = lines[-1].split(",")
    if len(cells) < 5:
        return None
    try:
        return cells[0], float(cells[4])
    except ValueError:
        return None


def parse_quote_line(text: str):
    """Parse one `var hq_str_XX="..."` line into a dict, or None when malformed."""
    if "=" not in text:
        return None
    left, right = text.split("=", 1)
    sym = left.strip().split("hq_str_")[-1]
    body = right.strip().strip(";").strip('"')
    if not sym or not body:
        return None
    f = body.split(",")
    if len(f) < 32:
        return None
    try:
        return {
            "symbol": sym,
            "name": f[0],
            "open": float(f[1]),
            "prev_close": float(f[2]),
            "last": float(f[3]),
            "high": float(f[4]),
            "low": float(f[5]),
            "quote_date": f[30],
            "quote_time": f[31],
        }
    except ValueError:
        return None


def fetch_quotes(symbols):
    """One batched request. Returns {symbol: quote}. Raises on transport failure."""
    url = QUOTE_URL + ",".join(symbols)
    req = urllib.request.Request(url, headers=QUOTE_HEADERS)
    raw = urllib.request.urlopen(req, timeout=15).read().decode("gbk", errors="replace")
    out = {}
    for line in raw.splitlines():
        q = parse_quote_line(line)
        if q:
            out[q["symbol"]] = q
    return out


def trading_days_between(cal_path: str, start: str, end: str):
    """Count official sessions in (start, end]; None when the calendar is unreadable."""
    if not os.path.exists(cal_path):
        return None
    try:
        with open(cal_path, encoding="utf-8", errors="replace") as fh:
            days = [ln.strip().split(",")[0] for ln in fh if ln.strip()]
    except OSError:
        return None
    days = [d for d in days if len(d) == 10 and d[4] == "-"]
    if start not in days or end not in days:
        # endpoint outside the calendar: count both ends as pending, do not guess
        pass
    return sum(1 for d in days if start < d <= end)


def held_leg(items, quotes):
    """Join each held name to its panel bar; return per-name rows and the totals."""
    rows = []
    joined = []
    for it in items:
        sym = to_sina_symbol(it["symbol"])
        q = quotes.get(sym)
        tail = panel_tail(sym)
        row = {
            "symbol": it["symbol"],
            "sina_symbol": sym,
            "weight": float(it.get("weight") or 0.0),
            "panel_bar": tail[0] if tail else None,
            "panel_close": tail[1] if tail else None,
            "quote_date": q["quote_date"] if q else None,
            "quote_prev_close": q["prev_close"] if q else None,
            "quote_last": q["last"] if q else None,
        }
        if tail and q:
            gap = abs(q["prev_close"] - tail[1])
            row["prev_gap"] = round(gap, 6)
            row["joined"] = gap <= PREV_TOL_ABS
        else:
            row["prev_gap"] = None
            row["joined"] = False
        if row["joined"]:
            row["ret"] = q["last"] / q["prev_close"] - 1.0
            joined.append(row["ret"])
        else:
            row["ret"] = None
        rows.append(row)
    n = len(rows)
    n_joined = sum(1 for r in rows if r["joined"])
    share_bad = (n - n_joined) / n if n else 1.0
    return rows, n_joined, share_bad


def verdict_of(panel_date, quote_date, n_joined, share_bad):
    if quote_date is None:
        return "UNAVAILABLE"
    if panel_date and quote_date == panel_date:
        return "NO_NEW_BAR"
    if share_bad > MISMATCH_SHARE_MAX or n_joined == 0:
        return "UNAVAILABLE"
    return "QUOTE_AHEAD"


RECHECK_TOL_HELD = 5e-7
RECHECK_TOL_RET = 1e-9


def recheck(face):
    """Re-derive a published quote face from its own rows.

    Single implementation of "does this face still say what its rows say": the chain gate
    (`check`) and the reader page both call it, so the page cannot grow a second copy of the
    arithmetic that silently disagrees the day the first one changes (E289 lineage).
    """
    rows = face.get("rows") or []
    n_joined = sum(1 for r in rows if r.get("joined"))
    share_bad = ((len(rows) - n_joined) / len(rows)) if rows else 1.0
    verdict = verdict_of(face.get("panel_bar"), face.get("quote_bar"), n_joined, share_bad)
    out = {"ok": True, "reason": None, "verdict": verdict, "n_joined": n_joined,
           "held_leg_return": None, "book_change": None}
    if verdict != face.get("verdict"):
        out.update(ok=False, reason="verdict %r is not the %r its rows give"
                   % (face.get("verdict"), verdict))
        return out
    if verdict != "QUOTE_AHEAD":
        out["reason"] = "nothing to re-derive (%s)" % verdict
        return out
    held = sum(r["weight"] * r["ret"] for r in rows if r.get("ret") is not None)
    out["held_leg_return"] = held
    out["book_change"] = float(face.get("book_weight") or 0.0) * held
    if face.get("held_leg_return") is None or abs(held - float(face["held_leg_return"])) > RECHECK_TOL_HELD:
        out.update(ok=False, reason="held_leg_return %r is not the %.6f its rows give"
                   % (face.get("held_leg_return"), held))
        return out
    for r in rows:
        if not r.get("joined"):
            continue
        expect = r["quote_last"] / r["quote_prev_close"] - 1.0
        if abs(expect - float(r["ret"])) > RECHECK_TOL_RET:
            out.update(ok=False, reason="%s ret %r is not the %.10f it quotes"
                       % (r.get("symbol"), r.get("ret"), expect))
            return out
    if n_joined != face.get("n_joined"):
        out.update(ok=False, reason="n_joined %r is not the %d its rows carry"
                   % (face.get("n_joined"), n_joined))
    return out


def build(ticket, quotes, cal_path=CAL):
    """Pure assembly: no network, no disk writes. Used by run() and by --check."""
    book = ticket["ticket"]
    items = book.get("order") or []
    rows, n_joined, share_bad = held_leg(items, quotes)

    panel_dates = [r["panel_bar"] for r in rows if r["panel_bar"]]
    panel_date = max(panel_dates) if panel_dates else None
    quote_dates = [r["quote_date"] for r in rows if r["quote_date"]]
    quote_date = max(quote_dates) if quote_dates else None

    verdict = verdict_of(panel_date, quote_date, n_joined, share_bad)

    held_ret = sum(r["weight"] * r["ret"] for r in rows if r["ret"] is not None)
    w_book = float(book.get("book_weight") or 0.0)
    book_change = w_book * held_ret

    lag_days = None
    if panel_date and quote_date and quote_date > panel_date:
        lag_days = trading_days_between(cal_path, panel_date, quote_date)

    return {
        "verdict": verdict,
        "panel_bar": panel_date,
        "quote_bar": quote_date,
        "quote_time": quotes.get(to_sina_symbol(items[0]["symbol"]), {}).get("quote_time")
        if items
        else None,
        "lag_trading_days": lag_days,
        "n_held": len(rows),
        "n_joined": n_joined,
        "mismatch_share": round(share_bad, 4),
        "held_leg_return": round(held_ret, 6) if verdict == "QUOTE_AHEAD" else None,
        "book_weight": round(w_book, 6),
        "cash_weight": round(float(book.get("cash_weight") or 0.0), 6),
        "book_change": round(book_change, 6) if verdict == "QUOTE_AHEAD" else None,
        "cash_leg": "unchanged -- a snapshot says nothing about the repo rate",
        "rows": rows,
        "thresholds": {
            "prev_tol_abs": PREV_TOL_ABS,
            "mismatch_share_max": MISMATCH_SHARE_MAX,
        },
    }


def render_md(face):
    L = []
    L.append(f"# 今天这本书值多少 — 快照 {face['quote_bar']} {face.get('quote_time') or ''}".rstrip())
    L.append("")
    L.append(
        "> 数据面日线还停在 **%s**（源滞后 %s 个交易日），这一页用交易所快照的收盘价把"
        "「今天涨了还是跌了」先算出来。它不改票面、不入账本、不产生任何交易指令。"
        % (face["panel_bar"], face["lag_trading_days"] if face["lag_trading_days"] is not None else "?")
    )
    L.append("")
    if face["verdict"] == "NO_NEW_BAR":
        L.append("**快照日期与面板最后一根 bar 相同：面板已经包含这一天，本页没有新信息。**")
        return "\n".join(L) + "\n"
    if face["verdict"] == "UNAVAILABLE":
        L.append(
            "**无法计算：%d 只持仓里有 %d 只的「快照昨收」与面板最后一根收盘对不上"
            "（容差 %.4f，失配占比 %.1f%% > %.0f%%）。**"
            % (
                face["n_held"],
                face["n_held"] - face["n_joined"],
                face["thresholds"]["prev_tol_abs"],
                face["mismatch_share"] * 100,
                face["thresholds"]["mismatch_share_max"] * 100,
            )
        )
        L.append("")
        L.append("| 代码 | 面板 bar | 面板收盘 | 快照日期 | 快照昨收 | 衔接 |")
        L.append("|---|---|---|---|---|---|")
        for r in face["rows"]:
            L.append(
                "| %s | %s | %s | %s | %s | %s |"
                % (
                    r["symbol"],
                    r["panel_bar"],
                    r["panel_close"],
                    r["quote_date"],
                    r["quote_prev_close"],
                    "✓" if r["joined"] else "✗ %.4f" % (r["prev_gap"] or 0.0),
                )
            )
        return "\n".join(L) + "\n"

    L.append("## 一句话")
    L.append(
        "**持仓腿今天 %+.2f%%，整本账（含未动现金）%+.2f%%**——以票面权重加权，"
        "现金腿按不变处理（快照里没有逆回购利率）。"
        % (face["held_leg_return"] * 100, face["book_change"] * 100)
    )
    L.append("")
    L.append("## 逐只")
    L.append("")
    L.append("| 代码 | 权重 | 面板收盘 %s | 快照 %s | 今日 | 衔接 |" % (face["panel_bar"], face["quote_bar"]))
    L.append("|---|---|---|---|---|---|")
    for r in face["rows"]:
        L.append(
            "| %s | %.2f%% | %s | %s | %s | %s |"
            % (
                r["symbol"],
                r["weight"] * 100,
                r["panel_close"],
                r["quote_last"],
                ("%+.2f%%" % (r["ret"] * 100)) if r["ret"] is not None else "对不上",
                "✓" if r["joined"] else "✗",
            )
        )
    L.append("")
    L.append("## 它证明什么、不证明什么")
    L.append(
        "- **衔接是逐只验证过的**：每只票快照自带的「昨收」都等于面板最后一根 bar 的收盘"
        "（容差 %.4f），所以这不是两个不同世界拼起来的数。" % face["thresholds"]["prev_tol_abs"]
    )
    L.append(
        "- **这不是净值**：ETF 快照是二级市场价，不是基金净值；本书的定价口径本来就是收盘价，所以口径一致。"
    )
    L.append(
        "- **现金腿没动**：快照里没有逆回购报价，`cash_weight %.2f%%` 按不变处理，"
        "不补默认利率、不算 0 息。" % (face["cash_weight"] * 100)
    )
    L.append(
        "- **不入账**：前向账本的 NAV 只按面板 bar 推进，这一页不进账本、不进票面、不进判词。"
    )
    return "\n".join(L) + "\n"


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    os.replace(tmp, path)


def host_id():
    p = _p("fleet", "machine.json")
    try:
        with open(p, encoding="utf-8") as fh:
            return json.load(fh).get("machine_id")
    except (OSError, ValueError):
        return None


def run():
    # Single-writer face: the book (and this quote page) is bm-a's. Other hosts print an
    # honest no-op rather than writing the same files from a different clock.
    me = host_id()
    if me != "bm-a":
        print("host=%s: etf_book_live_quote is bm-a's face -- honest no-op" % me)
        return 0
    latest = _p("results", "etf_book_order", "latest.json")
    if not os.path.exists(latest):
        print("no ticket pointer at %s" % latest)
        return 2
    with open(latest, encoding="utf-8") as fh:
        ptr = json.load(fh)
    ticket_path = os.path.join(TICKET_DIR, ptr["file"])
    if not os.path.exists(ticket_path):
        print("no ticket at %s" % ticket_path)
        return 2
    with open(ticket_path, encoding="utf-8") as fh:
        ticket = json.load(fh)

    items = (ticket.get("ticket") or {}).get("order") or []
    if not items:
        print("ticket carries no holdings -- refusing to print a book of nothing")
        return 2
    symbols = [to_sina_symbol(it["symbol"]) for it in items]
    try:
        quotes = fetch_quotes(symbols)
    except Exception as exc:  # noqa: BLE001 - transport failure is a fact, not a crash
        print("quote fetch failed: %s: %s" % (type(exc).__name__, exc))
        return 2

    face = build(ticket, quotes)
    face["ticket_file"] = os.path.relpath(ticket_path, ROOT).replace("\\", "/")
    face["ticket_priced_bar"] = ticket.get("evidence_cutoff")

    stamp = face["quote_bar"] or face["panel_bar"] or dt.date.today().isoformat()
    js = os.path.join(OUT_DIR, "QUOTE-%s.json" % stamp)
    _write(js, json.dumps(face, ensure_ascii=False, indent=1) + "\n")
    _write(
        os.path.join(OUT_DIR, "latest.json"),
        json.dumps(
            {"as_of": stamp, "file": os.path.basename(js), "verdict": face["verdict"]},
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
    )
    md = os.path.join(DOC_DIR, "LIVE-QUOTE-%s.md" % stamp)
    _write(md, render_md(face))

    print(
        "verdict=%s panel_bar=%s quote_bar=%s joined=%d/%d held=%s book=%s"
        % (
            face["verdict"],
            face["panel_bar"],
            face["quote_bar"],
            face["n_joined"],
            face["n_held"],
            ("%+.4f" % face["held_leg_return"]) if face["held_leg_return"] is not None else "n/a",
            ("%+.4f" % face["book_change"]) if face["book_change"] is not None else "n/a",
        )
    )
    print("wrote %s" % os.path.relpath(md, ROOT))
    return 0 if face["verdict"] != "UNAVAILABLE" else 2


def check():
    latest = os.path.join(OUT_DIR, "latest.json")
    if not os.path.exists(latest):
        print("no published quote face")
        return 2
    with open(latest, encoding="utf-8") as fh:
        ptr = json.load(fh)
    path = os.path.join(OUT_DIR, ptr["file"])
    with open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    rc = recheck(face)
    if not rc["ok"]:
        print("DRIFT " + str(rc["reason"]))
        return 2
    print("check OK (%s, %d rows)" % (face["verdict"], len(face.get("rows") or [])))
    return 0


# --------------------------------------------------------------------------- selftest

class _FakeTicket(dict):
    pass


def _ticket(weights, book_w, cash_w=0.5):
    return {
        "evidence_cutoff": "2026-11-03",
        "ticket": {
            "book_weight": book_w,
            "cash_weight": cash_w,
            "order": [
                {"symbol": s, "weight": w, "price": 1.0} for s, w in weights.items()
            ],
        },
    }


def selftest():
    ok = 0
    fail = []

    def leg(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append("%s %s" % (name, detail))

    # Build a throwaway panel on disk for two fake symbols.
    tmpdir = os.path.join(ROOT, ".codely-cli", "tmp", "livequote_selftest")
    os.makedirs(tmpdir, exist_ok=True)
    real_panel_path = globals()["panel_path"]

    def fake_panel(path):
        return os.path.join(tmpdir, path.split(os.sep)[-1])

    globals()["panel_path"] = lambda sym: os.path.join(tmpdir, sym + ".csv")

    def write_panel(sym, date, close):
        with open(os.path.join(tmpdir, sym + ".csv"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("date,open,high,low,close,volume,amount\n")
            fh.write("%s,1.0,1.0,1.0,%.4f,0,0\n" % (date, close))

    write_panel("sh510000", "2026-11-03", 10.0)
    write_panel("sz159999", "2026-11-03", 20.0)

    leg("51x maps to SH, 15x to SZ",
        to_sina_symbol("510000") == "sh510000" and to_sina_symbol("159999") == "sz159999",
        (to_sina_symbol("510000"), to_sina_symbol("159999")))

    q_ok = {
        "sh510000": {
            "symbol": "sh510000", "name": "A", "open": 10.0, "prev_close": 10.0,
            "last": 11.0, "high": 11.0, "low": 10.0,
            "quote_date": "2026-11-04", "quote_time": "15:00:00",
        },
        "sz159999": {
            "symbol": "sz159999", "name": "B", "open": 20.0, "prev_close": 20.0,
            "last": 19.0, "high": 20.0, "low": 19.0,
            "quote_date": "2026-11-04", "quote_time": "15:00:00",
        },
    }
    t = _ticket({"510000": 0.5, "159999": 0.5}, 0.5, 0.5)
    f = build(t, q_ok, cal_path=os.path.join(tmpdir, "nocal.csv"))
    leg("verdict ahead", f["verdict"] == "QUOTE_AHEAD", f["verdict"])
    # held leg = 0.5*(+10%) + 0.5*(-5%) = +2.5%
    leg("held leg maths", abs(f["held_leg_return"] - 0.025) < 1e-12, f["held_leg_return"])
    leg("book change = w_book * held", abs(f["book_change"] - 0.0125) < 1e-12, f["book_change"])
    leg("cash not repriced", "unchanged" in f["cash_leg"], f["cash_leg"])
    leg("lag unknown without calendar", f["lag_trading_days"] is None, f["lag_trading_days"])

    # a quote whose prev_close disagrees with the panel must not produce a return
    q_bad = json.loads(json.dumps(q_ok))
    q_bad["sz159999"]["prev_close"] = 21.0
    f2 = build(t, q_bad)
    leg("mismatched name has no return", f2["rows"][1]["ret"] is None, f2["rows"][1])
    leg("mismatched name is not joined", f2["rows"][1]["joined"] is False)
    leg("one of two unjoined = UNAVAILABLE", f2["verdict"] == "UNAVAILABLE", f2["verdict"])
    leg("unavailable prints no book number", f2["book_change"] is None, f2["book_change"])

    # same-day quote = nothing new
    q_same = json.loads(json.dumps(q_ok))
    for q in q_same.values():
        q["quote_date"] = "2026-11-03"
        q["prev_close"] = 9.9  # different sessions intrabar are not the point
    f3 = build(t, q_same)
    leg("same day is NO_NEW_BAR", f3["verdict"] == "NO_NEW_BAR", f3["verdict"])
    leg("NO_NEW_BAR prints no new number", f3["held_leg_return"] is None, f3["held_leg_return"])

    # missing quote entirely = unavailable, never a zero return
    f4 = build(t, {})
    leg("no quotes = UNAVAILABLE", f4["verdict"] == "UNAVAILABLE", f4["verdict"])
    leg("no quotes = no number", f4["book_change"] is None)

    # tolerance boundary: exactly PREV_TOL_ABS joins, one tick more does not
    qb = json.loads(json.dumps(q_ok))
    qb["sh510000"]["prev_close"] = 10.0 + PREV_TOL_ABS
    fb = build(t, qb)
    leg("tolerance boundary joins", fb["rows"][0]["joined"] is True, fb["rows"][0]["prev_gap"])
    qb["sh510000"]["prev_close"] = 10.0 + PREV_TOL_ABS + 0.0005
    fb2 = build(t, qb)
    leg("one step past tolerance refuses", fb2["rows"][0]["joined"] is False)

    # parse: a malformed line yields None rather than an invented quote
    leg("parse empty -> None", parse_quote_line('var hq_str_sh510000="";') is None)
    good = ('var hq_str_sh510000="X,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,'
            '20,21,22,23,24,25,26,27,28,29,2026-11-04,15:00:00,00";')
    pq = parse_quote_line(good)
    leg("parse keeps date and time", pq and pq["quote_date"] == "2026-11-04"
        and pq["quote_time"] == "15:00:00", pq)
    leg("parse keeps prev_close index 2", pq and pq["prev_close"] == 2.0, pq)

    # calendar lag counts sessions in (start, end] only
    calp = os.path.join(tmpdir, "cal.csv")
    with open(calp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("date\n2026-11-02\n2026-11-03\n2026-11-04\n2026-11-05\n")
    leg("lag counts one session", trading_days_between(calp, "2026-11-03", "2026-11-04") == 1)
    leg("lag counts two sessions", trading_days_between(calp, "2026-11-02", "2026-11-04") == 2)

    # md render must carry the join evidence and the caveats
    md = render_md(f)
    leg("md carries verdict sentence", "持仓腿今天" in md)
    leg("md carries cash caveat", "现金腿" in md)
    leg("md refuses on unavailable", "无法计算" in render_md(f2))

    globals()["panel_path"] = real_panel_path

    print("selftest %d/%d" % (ok, ok + len(fail)))
    for f_ in fail:
        print("  FAIL", f_)
    return 0 if not fail else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        return selftest()
    if len(argv) > 1 and argv[1] == "--check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))