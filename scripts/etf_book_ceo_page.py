"""ETF production book -> CEO one-page (docs/live_book/LIVE-BOOK-YYYYMMDD.md + .json).

Why this exists: the ETF book is the only money-making structure this company has
shown to work, but every face it publishes (ticket JSON, card JSON, registry JSON,
forward ledger) is machine-shaped. Nothing in the repo answers, in plain language,
"what do I buy today, with how much money, how am I doing, and when does it change".

Pure aggregation, zero new judgement:
  - order list / money split   <- results/etf_book_order/latest.json -> ticket file
  - backtest expectation band  <- results/etf_book_production/latest.json (card)
  - forward track vs inception <- results/etf_book_forward/LEDGER.json
  - next rebalance date        <- data/exchange_calendar.csv (official calendar)

Idempotent: same day -> same content; other days' pages are never touched.

Usage:
  python scripts/etf_book_ceo_page.py run
  python scripts/etf_book_ceo_page.py selftest
"""
from __future__ import annotations

import contextlib
import datetime as dt
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "docs", "live_book")
TICKET_PTR = os.path.join(ROOT, "results", "etf_book_order", "latest.json")
CARD = os.path.join(ROOT, "results", "etf_book_production", "latest.json")
LEDGER = os.path.join(ROOT, "results", "etf_book_forward", "LEDGER.json")
CAL = os.path.join(ROOT, "data", "exchange_calendar.csv")
REGIME_PATH = os.path.join(ROOT, "results", "etf_book_return_regime.json")
BETS_JSON = os.path.join(ROOT, "results", "etf_book_bets_face.json")
LEGS_JSON = os.path.join(ROOT, "results", "etf_book_legs", "latest.json")
CONC_JSON = os.path.join(ROOT, "results", "etf_book_concentration.json")
SLEEVE_JSON = os.path.join(ROOT, "results", "etf_book_sleeve_gate.json")
PATHS_JSON = os.path.join(ROOT, "results", "etf_book_sleeve_paths.json")
EXPOSURE_JSON = os.path.join(ROOT, "results", "etf_book_exposure_timing.json")
COST_JSON = os.path.join(ROOT, "results", "etf_book_cost_tape.json")
VOLWIN_JSON = os.path.join(ROOT, "results", "etf_book_vol_window_phase.json")
VOLWIN_EDGE_JSON = os.path.join(ROOT, "results", "etf_book_vol_window_edge.json")
LOOKAHEAD_JSON = os.path.join(ROOT, "results", "etf_book_lookahead_audit.json")
# r1213: the expectation table's rows are priced on different windows / classes / orderings.
BAND_RULER_JSON = os.path.join(ROOT, "results", "etf_book_band_ruler.json")
# r1216: row 1 of that table prints the ticket's own 683-bar window under a 全窗 header.
WINDOW_LABEL_JSON = os.path.join(ROOT, "results", "etf_book_window_label.json")
ENVELOPE_JSON = os.path.join(ROOT, "results", "etf_book_bootstrap", "latest.json")
# r1231: every other number on this page answers "how much" or "how deep". Nobody answered
# "how long do I have to wait", which is the question the person holding the book asks.
UNDERWATER_JSON = os.path.join(ROOT, "results", "etf_book_underwater.json")
MACHINE = os.path.join(ROOT, "fleet", "machine.json")

# Single writer: the page is a plain-language mirror of shared artefacts, so two
# machines regenerating the same day would only produce a git race on docs/live_book.
# bm-a prints it; every other host says so and writes nothing (R31 lane-guard lineage).
HOST = "bm-a"


def machine_id():
    try:
        with open(MACHINE, encoding="utf-8-sig") as fh:
            return json.load(fh).get("machine_id")
    except Exception:
        return None


def writer_allowed(mid):
    return mid == HOST

CLASS_ZH = {
    "equity": "A股",
    "crossborder": "跨境",
    "commodity": "商品",
    "convertible": "转债",
    "bond": "债券",
    "money": "货币",
}


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def carry_regime(path=REGIME_PATH):
    """How much of the quoted headline is cash carry, and what is left without it.

    Read from the artifact, never recomputed here: one price source per number. The page
    used to print 11.33%/yr beside a cash leg paying 1.09% today, without saying that a
    tenth of that headline was the repo leg earning ~2% when the history happened.
    """
    out = {"available": False, "rows": [], "base": None, "cash_rates": None,
           "identity": None, "window": None, "flags": None,
           "source": _rel(path, ROOT).replace("\\", "/")}
    if not os.path.exists(path):
        return out
    obj = _load(path)
    gate = obj.get("gate") or {}
    cells = obj.get("cells") or []
    by_cell = {(round(float(c.get("beta", 0.0)), 4), c.get("regime")): c for c in cells
               if c.get("cagr_pct") is not None}
    rows = []
    for beta, r in (gate.get("betas") or {}).items():
        if not r:
            continue
        try:
            b = round(float(beta), 4)
        except (TypeError, ValueError):
            continue
        obs = by_cell.get((b, "observed")) or {}
        rows.append({"beta": b, "observed_pct": r.get("observed_pct"),
                     "flat_today_pct": r.get("flat_today_pct"),
                     "zero_pct": r.get("zero_pct"), "carry_pp": r.get("carry_pp"),
                     "cash_share": r.get("cash_share"),
                     "pp_per_100bp": r.get("pp_per_100bp"),
                     "maxdd_pct": obs.get("maxdd_pct"), "vol_pct": obs.get("vol_pct")})
    rows.sort(key=lambda x: x["beta"])
    if not rows:
        return out
    base_beta = gate.get("base_beta")
    out.update({
        "available": True, "rows": rows,
        "base": next((r for r in rows if r["beta"] == base_beta), None),
        "cash_rates": obj.get("cash_rates"), "identity": obj.get("identity"),
        "flags": gate.get("flags"),
        "window": ({"first": cells[0].get("first_bar"), "last": cells[0].get("last_bar")}
                   if cells else None),
        "evidence_cutoff": obj.get("evidence_cutoff"),
    })
    return out


def bets_face(path=BETS_JSON):
    """How many independent bets the holdings on this page actually are.

    Single implementation: the reader is `etf_book_bets_face.read_published`, so
    the page quotes the same sentence the executable ticket carries (r1290).  A
    missing or unreadable artifact reads as absent -- never as "five tickers means
    five bets", which is exactly the reading this face exists to correct."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_bets_face as _bf
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unavailable", "detail": str(exc)[:160]}
    try:
        return dict(_bf.read_published(path))
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "detail": str(exc)[:160]}


def priced_faces(page_bar):
    """Which closing bar each of the three papers was priced on (r1185).

    Single implementation: `etf_book_production.priced_faces()` owns the rule. This page is
    the last of the three in the chain (card -> ticket -> page), so it is the first place that
    can print all three days beside each other. The footer used to say only
    "same priced bar = True"; a reader who is told "different" has to be told which paper is
    the stale one."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_production as _P
        return _P.priced_faces(page_bar=page_bar)
    except Exception as exc:                                    # noqa: BLE001
        return {"faces": {"card": None, "ticket": None, "page": page_bar},
                "verdict": "UNKNOWN", "detail": "reader failed (%s)" % str(exc)[:120],
                "missing": ["card", "ticket"], "same_day": None}


def family_coherence():
    """Whether the width family behind this page's name count was one measurement (r1184).

    Single implementation: `etf_book_production.family_coherence()` owns the rule; this
    page quotes it, exactly as the card does, so the two faces cannot drift into two
    definitions. The page quotes a backtest band whose width was chosen out of a family of
    arm cells -- if that family never priced one panel, the band is a configuration, not a
    measurement, and the reader has to be told which of the two it is. Absent or
    unreadable reads "unproven here", never a pass."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_production as _P
        return _P.family_coherence()
    except Exception as exc:                                    # noqa: BLE001
        return {"artifact": "results/etf_book_phase_atlas_arms.json", "verdict": None,
                "detail": "arm family face unreadable (%s)" % str(exc)[:120],
                "panels": [], "arms": 0, "evidence_cutoff": None,
                "priced_same_panel": None}


def leg_split(path=LEGS_JSON):
    """Where in the day this book's money is earned (r1189).

    Single implementation: `etf_book_leg_attribution.money_split_face()` owns the reader
    and the arithmetic check; this page quotes it. The page already tells the reader how
    much of the headline is lending cash out (the carry face) and how big the book is --
    what it never said is that the headline is earned on the ~1,500 quiet bars and that
    the ~83 bars where the order actually fills lose money. Without that line, a book
    that is a toll machine and a book that is a slow accumulator print the same CAGR.
    Absent/unreadable/broken reads as "cannot verify here", never as agreement."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_leg_attribution as _L
        return _L.money_split_face(path=path)
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path,
                "detail": "reader failed (%s)" % str(exc)[:120], "arms": {}}


def concentration_face(path=CONC_JSON):
    """Whose CAGR is this? The page quotes the published reading (r1191).

    The ticket started printing this at r1190; the page -- the face the CEO actually
    opens -- still answered the headline with no hint that three gold ETFs carry a fifth
    of the gross and that the whole commodity sleeve is what pays for the drawdown.
    Single implementation, moved down a level at r1192: `etf_book_concentration.reading()`
    now owns both the identity gate and the structured block (the card needs the same
    numbers, and a second copy of this assembly is the defect E289 named), so all three
    faces only format what it published. Absent/unreadable/broken reads as
    "cannot verify here", never as "broad"."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_concentration as _C
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path, "sentence": None,
                "detail": "reader failed (%s)" % str(exc)[:120]}
    return _C.reading(path=path)


def sleeve_gate_face(path=SLEEVE_JSON):
    """Does the commodity sleeve need a risk gate of its own? (r1193)

    The concentration section tells the reader the whole commodity sleeve is what pays
    for the drawdown; the reader's next question is "so should we gate it?". r1192
    measured exactly that and answered NO_GATE on the card; this page -- the face the
    CEO actually opens -- still ended the sentence there. Single implementation: the
    rows and the closest arm come from `etf_book_sleeve_gate.read_published()`, and the
    page only formats what it published. Absent/unreadable/broken reads as
    "cannot verify here", never as "no gate needed"."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_sleeve_gate as _G
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path, "sentence": None,
                "detail": "reader failed (%s)" % str(exc)[:120]}
    try:
        return _G.read_published(path=path) if path else _G.read_published()
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path, "sentence": None,
                "detail": "reading failed (%s)" % str(exc)[:120]}


def sleeve_paths_face(path=PATHS_JSON):
    """Was the named re-test candidate actually re-tested? (r1195)

    r1193 ended the sleeve section with "the vol gate is the candidate to re-test on new
    data, not a bar to lower". This page is where that promise has to be paid or dropped:
    the path face re-prices the same gate on several decision grids, and this reader is the
    single implementation every consumer uses (`read_published`). Absent, unreadable and
    stale all read as "cannot verify here" -- the one answer this section must never
    invent is "not needed"."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_sleeve_paths as _SP
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path, "detail": "reader failed (%s)"
                % str(exc)[:120]}
    try:
        return _SP.read_published(path=path)
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path,
                "detail": "reading failed (%s)" % str(exc)[:120]}


def exposure_timing_face(path=EXPOSURE_JSON):
    """The book's own de-levering: is it timing, or just a smaller book? (r1197)

    The page tells the reader the book is not always fully invested, and the reader's
    question is whether shrinking before bad stretches is a skill the record is paid for.
    r1196 measured exactly that (production vs a constant book at the same average
    exposure, against 20 permutations of the rule's own scale series) but it only reached
    a research file -- E311's old wound. Single implementation: the arms, the band and the
    verdict come from `etf_book_exposure_timing.read_published()`. Absent, unreadable or a
    failed identity gate reads as "cannot verify here", never as "the timing works"."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_exposure_timing as _ET
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path, "sentence": None,
                "detail": "reader failed (%s)" % str(exc)[:120]}
    try:
        return _ET.read_published(path=path)
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path, "sentence": None,
                "detail": "reading failed (%s)" % str(exc)[:120]}


def vol_window_face(path=VOLWIN_JSON):
    """The 8% overlay's 60-day window: load-bearing, or a champion on one calendar? (r1203)

    The page tells the reader the book is sized on a 60-day realised vol and that the
    overlay is a drawdown tool. The number nobody had tested across calendars is the 60
    itself -- the sweep behind it priced every cell on one decision grid (E321). Single
    implementation: the rows, the frozen criteria and the verdict come from
    `etf_book_vol_window_phase.read_published()`. Absent, unreadable or a face whose
    verdict does not recompute from its own rows reads as "cannot verify here", never as
    "the window is fine"."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_vol_window_phase as _VW
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path, "verdict": None,
                "detail": "reader failed (%s)" % str(exc)[:120]}
    try:
        return _VW.read_published(path=path)
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path, "verdict": None,
                "detail": "reading failed (%s)" % str(exc)[:120]}


def vol_window_edge_face(path=VOLWIN_EDGE_JSON):
    """The grid that had to be pushed further down: did the ladder turn, or keep falling? (r1212)

    The window face above ends on a promise -- "the champion sits on the edge of the grid, so
    pushing further is the next frozen face's job". This reader serves that face: the same
    question carried one grid lower, with the engine's own minimum estimation history
    measured from its per-decision diag rather than assumed.

    Single implementation: rows, verdict and position come from
    `etf_book_vol_window_edge.read_published()`. Absent, unreadable or drifted reads as
    "cannot verify here", never as "the window is fine"."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_vol_window_edge as _VWE
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path, "verdict": None,
                "detail": "reader failed (%s)" % str(exc)[:120]}
    try:
        return _VWE.read_published(path=path)
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path, "verdict": None,
                "detail": "reading failed (%s)" % str(exc)[:120]}


def window_label_face(path=WINDOW_LABEL_JSON):
    """Is the first row's 全窗年化 actually a full-window number? (r1216)

    r1213 measured that the three rows are three rulers and said so in a bullet *under*
    the table. The table itself kept printing the ticket's own 683-bar return under a
    header that promises 6.3 years. This reader serves the face that puts the same book's
    two windows side by side; its identity arm must still reproduce the ticket's own
    published number, and a face that no longer recomputes reads as "cannot verify"."""
    try:
        import etf_book_window_label as _WL
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": _rel(path, ROOT),
                "detail": "reader failed (%s)" % str(exc)[:120]}
    try:
        return _WL.read_published(path=path)
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": _rel(path, ROOT),
                "detail": "reading failed (%s)" % str(exc)[:120]}


def window_label_block(wl):
    """The lines this page prints about the first row's two windows (r1216).

    Factored out like `band_ruler_block` so a selftest can feed a missing / drifted / ok
    face. It never prints a window it cannot attribute, and a missing face says so."""
    L = []
    add = L.append
    add("## 表里第一行的「全窗年化」是几年")
    add("")
    if (wl or {}).get("status") != "ok":
        add("这一页没有拿到「窗口标签」面的可用读数（`%s`，状态 `%s`）：%s。"
            "所以第一行的「全窗年化」印 **—**——不拿 2.8 年那段去填 6.3 年的格子。"
            % (_rel((wl or {}).get("artifact") or WINDOW_LABEL_JSON, ROOT).replace(os.sep, "/"),
               (wl or {}).get("status") or "unknown",
               (wl or {}).get("detail") or "判决不能从自己的行重算"))
        add("")
        return L
    v = wl.get("verdict") or {}
    rows = wl.get("rows") or {}
    short = rows.get("printed_under_full_header") or {}
    long_ = rows.get("same_book_full_window") or {}
    if v.get("state") == "ROW_LABELED_BY_WINDOW":
        add("- 你手上这一本（5 名·beta 0.20·8bp），同一台引擎量两个窗口："
            "**全窗（%s bars）%.2f%%** ｜ **2024 起（%s bars）%.2f%%**——差 **%+.2f 个点/年**。"
            % (long_.get("bars") or "—", long_.get("cagr_pp") or 0.0,
               short.get("bars") or "—", short.get("cagr_pp") or 0.0,
               v.get("gap_pp") or 0.0))
        add("- 所以上表第一行现在把这两个数各放在各的列里：**全窗年化那一格不再是 2024 起的数**。"
            "这两段不能互相比较，只能各自同列比。")
    _trw = wl.get("table_row") or {}
    if (_trw.get("is") or {}).get("cagr_pct") is not None:
        add("- \u4e2d\u95f4\u6bb5\uff082020-2023\uff0c\u540c\u4e00\u628a\u5c3a\u5b50\uff09\uff1a**%.2f%%**\uff08%s bars\uff09\uff0c\u4e09\u6bb5 bars %s+%s=%s \u6070\u597d\u62fc\u6ee1\u5168\u7a97\uff08\u5bb9\u5dee\u00b11 bar\uff09\u3002"
            % (_trw["is"]["cagr_pct"], _trw.get("middle_window_bars") or "?",
               _trw.get("middle_window_bars"), _trw.get("short_window_bars"),
               _trw.get("full_window_bars")))
    elif v.get("state") == "SAME_WINDOW":
        add("- 你手上这一本两个窗口读数是同一个数（差 %+.2f 个点/年，在容差内），"
            "所以第一行照原样印，不存在标签问题。" % (v.get("gap_pp") or 0.0))
    else:
        add("- 这一节没有数：窗口标签面判决 **%s**（%s）。第一行两个格子按「未发表」处理，"
            "不拿短窗口的数去填全窗。" % (v.get("state"), v.get("why") or "—"))
    add("")
    add("> 窗口面：`%s` ｜ 定价截止 %s"
        % (str(wl.get("artifact") or "").replace(os.sep, "/"), wl.get("evidence_cutoff") or "—"))
    add("")
    return L


def band_ruler_face(path=BAND_RULER_JSON):
    """Which ruler priced each row of the table above (r1213).

    The expectation table mixes rows priced from 2020-01-01 with a row priced from
    2024-01-02, over two different class universes, under one column headed 全窗. This
    reader serves the face that priced those dials one at a time; it refuses a stored
    verdict that no longer recomputes, and an absent face reads as "cannot verify"."""
    try:
        import etf_book_band_ruler as _BR
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": _rel(path, ROOT),
                "detail": "reader failed (%s)" % str(exc)[:120]}
    try:
        return _BR.read_published(path=path)
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": _rel(path, ROOT),
                "detail": "reading failed (%s)" % str(exc)[:120]}


def band_ruler_block(br):
    """The lines this page prints about who priced its own table.

    Factored out (like `lookahead_block`) so a selftest can feed a missing / drifted / ok
    face. It never prints a dial it cannot attribute, and a missing face says so."""
    L = []
    add = L.append
    add("## 上面那张表的三行，是谁按什么尺子量的")
    add("")
    if (br or {}).get("status") != "ok":
        add("这一页没有拿到「尺子」面的可用读数（`%s`，状态 `%s`）：%s。"
            "请按默认口径读——上表第一行是从 2024 起算的，另两行从 2020 起算，"
            "两者**不在同一段时期**，本页无法核验这个差有多大。"
            % (_rel((br or {}).get("artifact") or BAND_RULER_JSON, ROOT).replace(os.sep, "/"),
               (br or {}).get("status") or "unknown",
               (br or {}).get("detail") or "判决不能从自己的行重算"))
        add("")
        return L
    v = br.get("verdict") or {}
    pr = br.get("dial_prices") or {}
    zh = {"ROWS_NOT_COMPARABLE": "**三行不是一把尺子**",
          "SAME_RULER": "**三行是同一把尺子**",
          "IDENTITY_FAILED": "**对照臂没复现，这一节不许引用**"}.get(v.get("state"), "**%s**" % v.get("state"))
    add("- 判决：%s。把这三行摆在一张表里比较，比的不只是策略。" % zh)
    cells = br.get("cells") or {}
    held = cells.get("held/causal/card") or {}
    if (held.get("full") or {}).get("cagr_pp") is not None:
        add("- 同一本书（你手上这本，5 名·beta 0.20）按同一把手量：全窗 %.2f%% / 2024 起 %.2f%%——"
            "同一个策略，两段时期差 %+.2f 个点。"
            % (held["full"]["cagr_pp"],
               ((held.get("ticket_window") or {}).get("cagr_pp") or 0.0),
               ((held.get("ticket_window") or {}).get("cagr_pp") or 0.0)
               - (held["full"]["cagr_pp"] or 0.0)))
    dials = [("window", "起点"), ("universe", "股票池"), ("ordering", "信号时点"), ("cost", "成本")]
    bits = []
    for k, name in dials:
        val = (pr.get(k) or {}).get("price_pp")
        if val is not None:
            bits.append("%s %+.2f" % (name, val))
    if bits:
        add("- 四个旋钮各自值多少（pp/年，正＝后者读得更高）：%s。" % "、".join(bits))
    add("- 所以按列读表（12.78 对 9.60）与按同一段读表（12.78 对这张表自己印的 2024 起 18.35）"
        "会得出相反的排序。要比较，请只在同一列里比。")
    add("")
    add("> 尺子面：`%s` ｜ 定价截止 %s ｜ 身份门 %s"
        % (str(br.get("artifact") or "").replace(os.sep, "/"), br.get("evidence_cutoff") or "—",
           "全 PASS" if all((x or {}).get("pass") for x in (br.get("identity") or {}).values())
           else "有 FAIL"))
    add("")
    return L



CAUSAL_REBUILD_JSON = os.path.join(ROOT, "results", "etf_book_causal_rebuild.json")
GAP_JSON = os.path.join(ROOT, "results", "etf_book_overnight_gap.json")


def gap_face(path=GAP_JSON):
    """Is anything visible at the fill worth the one-bar price? (r1226 / E26)

    Single implementation: verdict and arms come from `etf_book_overnight_gap`, which refuses
    to serve a stored sentence whose rows no longer recompute. An absent or drifted face reads
    as "cannot verify here" -- never as a clean negative."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_overnight_gap as _GP
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path, "verdict": None,
                "detail": "reader failed (%s)" % str(exc)[:120]}
    try:
        doc = _GP.read_published(path) if os.path.exists(path) else None
        if doc is None:
            return {"status": "absent", "artifact": path, "verdict": None,
                    "detail": "no artifact"}
        if _GP.check(path) != 0:
            return {"status": "drifted", "artifact": path, "verdict": doc.get("verdict"),
                    "detail": "the verdict no longer recomputes from its own rows"}
        doc["status"] = "ok"
        doc["artifact"] = path
        return doc
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path, "verdict": None,
                "detail": "reading failed (%s)" % str(exc)[:120]}


def causal_rebuild_face(path=CAUSAL_REBUILD_JSON):
    """Can the one-bar price be earned back by a causal rule? (r1224 / E341)

    The table tells the reader to size off the declared arm. The next question a reader has
    is whether that 1.14pp can be rebuilt -- average the causal score, trade less, win part of
    it back. This face prices that question and prints the answer, including when the answer
    is no: a negative result the operator can see is worth more than a silence he has to
    interpret."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_causal_rebuild as _CR
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path, "verdict": None,
                "detail": "reader failed (%s)" % str(exc)[:120]}
    try:
        doc = _CR.read_published(path) if os.path.exists(path) else None
        if doc is None:
            return {"status": "absent", "artifact": path, "verdict": None,
                    "detail": "no artifact"}
        if _CR.check(path) != 0:
            return {"status": "drifted", "artifact": path, "verdict": doc.get("verdict"),
                    "detail": "the verdict no longer recomputes from its own rows"}
        doc["status"] = "ok"
        doc["artifact"] = path
        return doc
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path, "verdict": None,
                "detail": "reading failed (%s)" % str(exc)[:120]}


def research_arc_face():
    """这三个问题已经问过几遍、每遍花掉多少（r1228 / E25+E26+E27 合订）

    Single implementation: `etf_book_production.research_exhaustion()` owns the roll-up, so
    the card and this page cannot drift into two opinions about whether the book has been
    interrogated. The page printed E25 and E26 in their own sections but never E27, and never
    said the three add up to "no lever" -- which left the reader free to ask a fourth time.
    A face that does not read makes the whole answer CANNOT_VERIFY: an absence is not a no."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_production as _P
        return _P.research_exhaustion()
    except Exception as exc:                                    # noqa: BLE001
        return {"verdict": "CANNOT_VERIFY", "rows": [], "missing": ["reader"],
                "levers": [], "cutoffs": [],
                "detail": "reader failed (%s)" % str(exc)[:120]}


def research_arc_block(rx):
    """What each of the three asks cost, and what the three together authorize (r1228).

    Factored out so a selftest can feed it a closed / open / unreadable face. The case
    labels are presentation only; every number and every state is read from the payloads."""
    L = []
    add = L.append
    add("## 这三个数字已经被问过三遍，答案都是「不值」")
    add("")
    rx = rx or {}
    rows = [r for r in (rx.get("rows") or []) if r.get("readable")]
    _zh = {"E25": "收盘后多出来那一 bar 的信息，能不能用因果规则赚回来",
           "E26": "决策收盘到成交开盘之间的隔夜跳空，值不值那 1.14pp",
           "E27": "把同一笔调仓摊到 k 个连续开盘上买，能不能省钱或多赚"}
    _state = {"IRRECOVERABLE": "捡不回来", "NO_GAP_EDGE": "不够线",
              "MIXED_ACROSS_PHASES": "全窗有、四个相位只部分赢",
              "NO_SLICING_EDGE": "没有边际"}
    if not rows:
        add("这一页读不到那三份研究面，所以**无从判断**它们问过没有——读不出来不是「没问过」，"
            "也不是「问了没用」。缺：%s。"
            % ", ".join((rx.get("missing") or ["未知"]) if isinstance(rx.get("missing"), list)
                        else [str(rx.get("missing"))]))
        add("")
        return L
    add("| 案例 | 问的是什么 | 判词 | 最好的臂 | 最多赚回 | 可采纳臂 |")
    add("|---|---|---|---|---|---|")
    for r in rows:
        add("| %s | %s | %s（`%s`） | `%s` | %+.2f pp/年 | %d |"
            % (r.get("case"), _zh.get(r.get("case")) or r.get("question"),
               (_state.get(r.get("state")) or "未命名判词"), r.get("state"),
               r.get("best_arm"), r.get("best_pp") or 0.0,
               len(r.get("admissible") or [])))
    add("")
    if rx.get("verdict") == "CLOSED":
        add("- **三问皆负**：三个都跑过、三个都没出可采纳的臂。所以说清一件事——印出来的数"
            "和真能下单的数之间的那道缝，**不是**靠平滑打分、不靠隔夜跳空、也不靠把成交摊薄能补回来的。")
        add("- 这句话的边界也要说清：它**不是**「这本书没有别的招」，而是「这三条不赚钱」。"
            "下一条线索得从别处来，不能从这个规则自己的机械里再挖第四遍。")
    elif rx.get("verdict") == "OPEN_LEVER":
        add("- **有一条臂过了自己的预注册门槛**：%s。它**还没被采纳**——这一页的数字仍按声明口径印，"
            "要不要换由另一张决策件定。" % "、".join("`%s`" % a for a in (rx.get("levers") or [])))
    else:
        add("- **不能称为「问完了」**：有 %d 个案例这一次没读到，那几问在这里仍是悬的。"
            % len(rx.get("missing") or []))
    add("")
    if rx.get("cutoffs"):
        add("> 三份证据的截止日：%s；预注册件与判据都在各自的 `research/CASE_PREREG_*.md`。"
            % "、".join(str(c) for c in rx["cutoffs"]))
        add("")
    return L


def underwater_face(path=UNDERWATER_JSON):
    """How long does the money sit under water before it comes back? (r1231 / E346)

    Every face on this page answers "how much" (CAGR) or "how deep" (max drawdown).
    None answered "how long", and that is the question a person holding the book asks.
    The producer publishes it censored-aware: an entry that has not healed on the last
    bar is reported as *still under water*, never scored as 0 bars -- counting it as 0
    would make the record look faster than it is (r1261 lineage: an empty measurement
    written as a good reading).

    This face only reads. A payload whose verdict no longer recomputes is refused
    rather than printed."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    if not os.path.exists(path):
        return {"status": "absent", "artifact": _rel(path, ROOT), "verdict": None,
                "detail": "no artifact"}
    try:
        import etf_book_underwater as _UW
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        # the producer's check narrates to stdout; this face must not pollute the page's run
        with contextlib.redirect_stdout(io.StringIO()):
            _rc = _UW.check(path)
        if _rc != 0:
            return {"status": "drifted", "artifact": _rel(path, ROOT),
                    "verdict": doc.get("verdict"),
                    "detail": "the verdict no longer recomputes from its own rows"}
        doc["status"] = "ok"
        doc["artifact"] = _rel(path, ROOT).replace("\\", "/")
        return doc
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": _rel(path, ROOT), "verdict": None,
                "detail": "reading failed (%s)" % str(exc)[:120]}


def underwater_block(u):
    """How long the worst start had to wait -- and what the sample can promise (r1231).

    Factored out like the other blocks so a selftest can feed an absent / drifted / ok
    face. Two rules are printed, not merely obeyed: a censored entry is named as still
    under water (never 0 bars), and a 3-year "almost never loses" over a sample that
    begins in 2020 is a property of that sample, not a promise about the future."""
    L = []
    add = L.append
    add("## 这笔钱真要等多久才能回本")
    add("")
    u = u or {}
    if u.get("status") != "ok":
        add("这一页没拿到时长读数（`%s`，状态 `%s`）：%s。所以**这里无法回答**「最坏要等多久」"
            "——读不出来不等于「很快就回本」。"
            % (str(u.get("artifact") or "results/etf_book_underwater.json").replace(os.sep, "/"),
               u.get("status") or "unknown",
               u.get("detail") or "判决不能从自己的行重算"))
        add("")
        return L
    rec = u.get("recovery") or {}
    uw = u.get("underwater") or {}
    fw = u.get("forward") or {}
    add("上面所有格子说的都是「赚多少」和「跌多深」，没说过**要等多久**。同一本账，按你入场的日子"
        "算回本要多少根 bar（%s 至 %s，共 %d 根）："
        % (u.get("first_bar"), u.get("last_bar"), int(u.get("bars") or 0)))
    add("")
    add("| 读法 | 数字 |")
    add("|---|---|")
    we = rec.get("worst_entry") or {}
    if we.get("recovered_bar"):
        add("| 最坏的一笔入场（买在峰值 %s） | **%d 个交易日**后才回本（%s） |"
            % (str(we.get("entry_bar") or "")[:10], int(we.get("bars") or 0),
               str(we.get("recovered_bar"))[:10]))
    elif we:
        add("| 最坏的一笔入场（买在峰值 %s） | **仍未回本**，已在水下 %d 个交易日 |"
            % (str(we.get("entry_bar") or "")[:10], int(we.get("bars") or 0)))
    if rec.get("median_bars") is not None:
        add("| 中位 | %.0f 个交易日 |" % rec["median_bars"])
    if rec.get("p90_bars") is not None:
        add("| 九成入场点 | %.0f 个交易日内回本 |" % rec["p90_bars"])
    if rec.get("censored"):
        add("| 到最后一根 bar 仍未回本 | %d 个入场点（%.2f%%）——按「仍未回本」记，**不记 0** |"
            % (int(rec["censored"]), 100.0 * (rec.get("censored_share") or 0.0)))
    add("")
    lg = uw.get("longest") or {}
    if lg.get("bars_underwater") is not None:
        add("- 最长的一段水下：%s 见顶 → %s 见谷（%+.2f%%）→ %s 回本，水下 **%d 个交易日**；"
            "全史 %d 段里 %d 段愈合、%d 段到末 bar 仍在水下。"
            % (str(lg.get("peak_bar") or "")[:10], str(lg.get("trough_bar") or "")[:10],
               100.0 * (lg.get("trough_dd") or 0.0), str(lg.get("recover_bar") or "")[:10],
               int(lg.get("bars_underwater") or 0), int(uw.get("episodes") or 0),
               int(uw.get("healed") or 0), int(uw.get("never_healed") or 0)))
    horizon_rows = []
    for h in ("1y", "2y", "3y"):
        b = fw.get(h) or {}
        if b.get("min") is None:
            continue
        horizon_rows.append("| 持有 %s | %+.2f%% | %+.2f%% | %.2f%% |"
                            % (h, 100.0 * b["min"], 100.0 * (b.get("p50") or 0.0),
                               100.0 * (b.get("share_negative") or 0.0)))
    if horizon_rows:
        add("")
        add("| 持有期 | 最差一笔年化 | 中位年化 | 亏钱的入场点占比 |")
        add("|---|---|---|---|")
        L.extend(horizon_rows)
        add("")
        add("边界要一起读：长持有期「几乎没有亏钱的入场点」是**这段样本的性质**——样本从 %s 才开始，"
            "此后几年以上升为主。它不是「拿满就不会亏」的承诺，也不能外推到更长的持有期。"
            % u.get("first_bar"))
    add("")
    add("> 时长面：`%s` ｜ 证据截止 %s ｜ 定义：水下=严格低于历史峰值，回本日不计入；"
        "末 bar 未愈合的入场点按「仍未回本」披露，不参与分布。"
        % (u.get("artifact"), u.get("evidence_cutoff")))
    add("")
    return L


def lookahead_face(path=LOOKAHEAD_JSON):
    """Is the headline achievable at the price the book is actually bought at? (r1207)

    The table on this page quotes the research engine. r1207 found that engine ranks on bar
    d's own close and then earns open[d]->open[d+1], i.e. it buys at a price set before the
    information it ranks on; the ledger that prints orders is causal. Until this section the
    page told the reader what the book *would have* made if a bar of the future were free.

    Single implementation: verdict, arms and ladder come from
    `etf_book_lookahead_audit.read_published()`, which refuses to serve a stored sentence
    whose rows no longer recompute. Absent or drifted reads as "cannot verify here"."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_lookahead_audit as _LA
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path, "verdict": None,
                "detail": "reader failed (%s)" % str(exc)[:120]}
    try:
        return _LA.read_published(path=path)
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path, "verdict": None,
                "detail": "reading failed (%s)" % str(exc)[:120]}


def vol_window_edge_block(ve):
    """The lines this page prints about pushing the window grid below its old floor.

    Factored out (like `lookahead_block`) so a selftest can feed it a missing / drifted / ok
    face instead of trusting the render path by eye. The block never prints a winner it
    cannot attribute: every number comes from the reader, and a face that cannot be verified
    says so and stops."""
    L = []
    add = L.append
    add("### 那根「还得往下推」的网格——推到底了吗")
    add("")
    if (ve or {}).get("status") != "ok":
        add("这一页没有拿到「网格往下推」那张面的可用读数（`%s`，状态 `%s`）：%s。"
            "所以上一节末尾那句「往下推是下一张面的活」，本页还没法回答。"
            % (_rel(ve.get("artifact") or VOLWIN_EDGE_JSON, ROOT).replace(os.sep, "/"),
               (ve or {}).get("status") or "unknown",
               (ve or {}).get("detail") or "判决不能从自己的行重算"))
        add("")
        return L
    e = ve.get("edge") or {}
    v = ve.get("verdict") or {}
    st = e.get("state")
    zh = {"EDGE_AT_FLOOR": "**还在最边上**（是方向，不是水平）",
          "INTERIOR": "**阶梯在网格内部拐弯了**（有候选值）",
          "SHIPPED_IS_HIGHEST": "**在册窗口就是最高点**",
          "EDGE_AT_CEILING": "**顶边上**（异常）"}.get(st, "**%s**" % st)
    add("上一节的冠军落在它自己网格的最小格（30 日）上，那句话只能当方向读。把网格再往下延"
        "（%s 日），这一节回答它到底会不会拐弯。"
        % "、".join("%s" % w for w in (ve.get("criteria") or {}).get("windows") or []))
    add("")
    add("- 判决：%s。最高平均夏普的窗口 = **%s 日**（%.4f），在册 60 日 = %.4f。"
        % (zh, e.get("best_window"), e.get("best_mean_sharpe") or 0.0,
           (e.get("shipped") or {}).get("mean_sharpe") or 0.0))
    if e.get("inactive_windows"):
        add("- 关键一条：**%s 这三个窗口一个估计都出不来**。发动机自己要求至少 %s 根 bar 才肯"
            "算协方差，低于这条线它就按满仓走——那不是在测「更短的估计」，而是在测"
            "**把覆盖关掉**。三格数字一模一样（同一个臂），所以它们被并成一个臂、踢出曲线，"
            "否则「最优点」会因为重复格被读低。"
            % ("、".join("%sd" % w for w in e["inactive_windows"]), e.get("floor_window")))
    add("- 也就是说：**真正能跑的窗口地板就是 %s 日**，冠军正压在这条地板上。"
        "要再往下测，得先改「估计器最少用多少根 bar」——那是另一个决定（样本够不够统计），"
        "不是把窗口数字调小。" % e.get("floor_window"))
    pv = ve.get("paired") or {}
    if (pv.get("rows") or []):
        add("- 配对裁决（最好窗口 vs 在册 60 日，同一相位内的收益差自己做块自助）：**%s**。"
            % ((pv.get("verdict") or {}).get("state") or "—"))
    add("- 在册窗口留不留：**%s**。" % ("留" if ve.get("published_window_stays") else "可换"))
    add("")
    add("| 窗口 | 平均夏普（跨 4 相位） | 跑得动吗 |")
    add("|---|---|---|")
    for c in e.get("curve") or []:
        add("| %sd | %.4f | 是 |" % (c["window"], c["mean_sharpe"]))
    for w in e.get("inactive_windows") or []:
        add("| %sd | —（覆盖被关掉） | **否** |" % w)
    add("")
    add("> 网格底面：`%s` ｜ 定价截止 %s ｜ 在册窗口复现生产卡 = **%s**"
        % (_rel(ve.get("artifact") or VOLWIN_EDGE_JSON, ROOT).replace(os.sep, "/"),
           ve.get("evidence_cutoff") or "—",
           "PASS" if ve.get("identity_all_pass") else "FAIL"))
    add("")
    return L



def causal_rebuild_block(cr):
    """The lines this page prints about the rebuild question (r1224 / E341).

    Factored out so a selftest can feed a missing / drifted / ok face instead of trusting the
    render path by eye."""
    L = []
    add = L.append
    add("## 那条缝能不能捡回来：把因果分数平滑之后只拿回 0.07pp")
    add("")
    if (cr or {}).get("status") != "ok":
        add("这一页没能读到重排面的产物（`%s`，状态 `%s`：%s），所以「能不能捡回」在本页"
            "**无法核验**——它不是零，也不是没有这回事。"
            % (_rel((cr or {}).get("artifact") or CAUSAL_REBUILD_JSON, ROOT).replace(os.sep, "/"),
               (cr or {}).get("status") or "unknown",
               (cr or {}).get("detail") or "原因未报"))
        add("")
        return L
    v = cr.get("verdict") or {}
    dec = cr.get("decomposition") or {}
    st = v.get("state")
    _zh = {"IRRECOVERABLE": "**捡不回来**——这条缝是桌子从来没拿到的信息",
           "RECOVERABLE": "**能捡回来一部分**",
           "MIXED_ACROSS_PHASES": "**四个决策相位里说法不一**——不是一条规则",
           "INCOMPLETE": "**没有算完**"}.get(st, "**%s**" % st)
    add("- 判决：%s。卡上那条可交易口径是 **%.2f%%/年**，因果平滑最好的一臂只把它推到 "
        "**%+.2f pp/年**；判据要求至少捡回 %.2f pp/年，所以卡继续印声明口径。"
        % (_zh, 100.0 * (v.get("declared_cagr") or 0.0),
           v.get("best_recovered_pp") or 0.0,
           (cr.get("criteria") or {}).get("recovery_min_pp") or 0.0))
    add("")
    if dec.get("total_pp") is not None:
        add("- 捡回的是哪一块：同一个规则零佣金再算一次，**信号 %+.2f pp / 佣金 %+.2f pp**"
            "（换手 %.3f → %.3f）。两个几乎一样，所以这不是「少交易省下来的钱」。"
            % (dec.get("signal_pp") or 0.0, dec.get("cost_pp") or 0.0,
               dec.get("turnover_declared") or 0.0, dec.get("turnover_arm") or 0.0))
        add("")
    arms = v.get("arms") or []
    if arms:
        add("- 逐臂：%s。" % "，".join("`%s` %+.2f pp（%d/4 相位跑赢）"
                                     % (a.get("arm"), a.get("recovered_pp") or 0.0,
                                        a.get("phase_wins") or 0) for a in arms))
        add("")
    au = cr.get("audits") or {}
    _ok = all((au.get(k) or {}).get("ok") for k in ("A3_rank_causality", "A4_factor_source", "A5_lags"))
    add("- 机制审计：%s（秩层因果 / 因子库无全样本统计 / 每条重建臂滞后 ≥1）。"
        "不过这三条，「8.46%% 可交易」这句话本身就没有证据。" % ("三条全过" if _ok else "**有不过项**"))
    add("")
    add("> 证据：`%s`"
        % _rel((cr or {}).get("artifact") or CAUSAL_REBUILD_JSON, ROOT).replace(os.sep, "/"))
    add("")
    return L


def gap_block(gp):
    """The lines this page prints about the overnight gap (r1226 / E26).

    The rebuild answer is "no". A reader's next question is whether anything else visible at
    the fill could be worth the 1.14pp -- the gap between the decision close and the fill open
    is the only channel there. This block prints what it was worth, including when the answer
    is "not enough, and not everywhere", because a tested negative is worth more than a
    silence. Factored out so a selftest feeds it a missing / drifted / ok face."""
    L = []
    add = L.append
    add("## 收盘到开盘之间只剩一个通道：隔夜跳空，量了也不够")
    add("")
    if (gp or {}).get("status") != "ok":
        add("这一页没能读到跳空面的产物（`%s`，状态 `%s`：%s），所以「跳空值不值钱」在本页"
            "**无法核验**——它不是零，也不是没有这回事。"
            % (_rel((gp or {}).get("artifact") or GAP_JSON, ROOT).replace(os.sep, "/"),
               (gp or {}).get("status") or "unknown",
               (gp or {}).get("detail") or "原因未报"))
        add("")
        return L
    v = gp.get("verdict") or {}
    g = gp.get("gap_stats") or {}
    st = v.get("state")
    _zh = {"NO_GAP_EDGE": "**跳空不值钱**——结算出来的钱不是信息",
           "ADOPT_GAP": "**有一条跳空规则够格**",
           "MIXED_ACROSS_PHASES": "**全窗够线、四个相位里只有一半跑赢**——不是一条规则",
           "INCOMPLETE": "**没有算完**"}.get(st, "**%s**" % st)
    add("- 判决：%s。卡上可交易口径 **%.2f%%/年**；最好的一臂是 `%s`，**%+.2f pp/年**，"
        "判据线 %.2f pp/年。"
        % (_zh, 100.0 * (v.get("declared_cagr") or 0.0), v.get("best_arm"),
           v.get("best_gained_pp") or 0.0, (gp.get("criteria") or {}).get("gap_min_pp") or 0.0))
    add("")
    arms = v.get("arms") or []
    if arms:
        add("- 逐臂：%s。" % "，".join("`%s` %+.2f pp（%d/4 相位跑赢%s）"
                                     % (a.get("arm"), a.get("gained_pp") or 0.0,
                                        a.get("phase_wins") or 0,
                                        "，全窗三关过" if a.get("full_span_tests_pass")
                                        else "，全窗三关未过") for a in arms))
        add("")
    if g.get("median_abs_gap_bp") is not None:
        add("- 这个通道有多大：入场那根 bar 的跳空中位数 **%s bp**（均值 %s bp，90 分位 %s bp），"
            "入场 %s 次；剔除臂每次决策会扔掉 %s 个名字。跳空本身不是小量，"
            "但它作为排序信号是**负**的——按「跳得高就买」做是 %+.2f pp。"
            % (g.get("median_abs_gap_bp"), g.get("mean_abs_gap_bp"), g.get("p90_abs_gap_bp"),
               g.get("entry_bars"),
               (g.get("excluded_names_per_decision") or {}).get("excl_upgap_q80"),
               next((a.get("gained_pp") or 0.0 for a in arms if a.get("arm") == "gap_rank_up"),
                    0.0)))
        add("")
    au = gp.get("audits") or {}
    _ok = all((au.get(k) or {}).get("ok") for k in
              ("A6_fill_time_causality", "A7_declared_lag", "A8_mask_not_rescale"))
    add("- 机制审计：%s（跳空只用开盘价与前一根收盘 / 控制臂是滞后一根 / "
        "剔除只改选股集合不改分数）。第一条不过，这整节就是未来函数。"
        % ("三条全过" if _ok else "**有不过项**"))
    add("")
    add("> 证据：`%s`"
        % _rel((gp or {}).get("artifact") or GAP_JSON, ROOT).replace(os.sep, "/"))
    add("")
    return L


def lookahead_block(lk):
    """The lines this page prints about the audit. Factored out so a selftest can feed it
    a missing / drifted / ok face instead of trusting the render path by eye."""
    L = []
    add = L.append
    add("## 上面那张表的口径，是在用今天的收盘价买今天的开盘")
    add("")
    if (lk or {}).get("status") != "ok":
        add("这一页没有拿到时点体检面的可用读数（`%s`，状态 `%s`）：%s。"
            "按默认口径读——上面那张表是**研究引擎**的读数，它的信号取自第 d 根 bar 自己的"
            "收盘与成交额，却在第 d 根开盘成交；这个差在本页**无法核验**，别把表里的年化当成可得。"
            % (_rel((lk or {}).get("artifact") or LOOKAHEAD_JSON, ROOT).replace(os.sep, "/"),
               (lk or {}).get("status") or "unknown",
               (lk or {}).get("detail") or "判决不能从自己的行重算"))
        add("")
        return L
    v = lk.get("verdict") or {}
    arms = lk.get("arms") or {}
    dec = lk.get("decomposition") or {}
    st = v.get("state")
    pub = (arms.get("published") or {})
    cau = (arms.get("causal") or {})
    led0 = (arms.get("ledger_no_carry") or {})
    led1 = (arms.get("ledger_carry") or {})
    _zh = {"LOOKAHEAD_PRESENT": "**这张表的年化含一根 bar 的未来**",
           "WITHIN_TOL": "**时点差在容差内**（这张表的口径站得住）",
           "MECHANISM_ABSENT": "**引擎已经不再读自己那根 bar**（结论须重导出）"}.get(st, "**%s**" % st)
    add("- 判据：%s。研究引擎用第 d 根收盘选出的权重，从第 d 根开盘就赚起；"
        "而**真正下单的那本账**是收盘决定、次日开盘成交、按收盘计价。" % _zh)
    add("")
    if pub.get("cagr_pp") is not None and cau.get("cagr_pp") is not None:
        add("- 同一个规则只把信号推迟一根 bar：全窗年化 **%.2f%% → %.2f%%**，"
            "差 **%.2f pp/年**；回撤 **%.2f%% → %.2f%%**。"
            % (pub["cagr_pp"], cau["cagr_pp"], dec.get("price_of_the_one_bar_pp") or 0.0,
               pub.get("maxdd_pp") or 0.0, cau.get("maxdd_pp") or 0.0))
        add("")
    lad = lk.get("lag_ladder") or []
    if lad:
        add("- 阶梯（负 lag = 给它几根 bar 的未来，正 lag = 让它用更旧的信息，其余全不动）：%s。"
            % " → ".join("%+d:%+.2f%%" % (r.get("lag"), r.get("cagr_pp") or 0.0) for r in lad))
        add("")
    if led0.get("cagr_pp") is not None:
        add("- 账本引擎（因果、不计回购）**%.2f%%**，与上面「+1 根」那一格对得上，"
            "等于独立验证了两者是同一本书；账本再计 ladder3 回购 **%.2f%%**"
            "（+%.2f pp，是钱的来源之一，不是技能）。"
            % (led0["cagr_pp"],
               (led1 or {}).get("cagr_pp") if (led1 or {}).get("cagr_pp") is not None else float("nan"),
               dec.get("carry_pp") or 0.0))
        add("")
    n = lk.get("affected_faces") or 0
    add("- 影响面：机械扫出 **%d** 个脚本走同一个排序（含本页引用的多数生产面）。"
        "研究结论与账本都没有造假，差别只在**时点**：报价时要说清是哪一本。" % n)
    add("")
    add("> 时点体检面：`%s` ｜ 定价截止 %s ｜ 一 bar 的价钱 **%.2f pp/年**"
        % (_rel(lk.get("artifact") or LOOKAHEAD_JSON, ROOT).replace(os.sep, "/"),
           lk.get("evidence_cutoff") or "—", dec.get("price_of_the_one_bar_pp") or 0.0))
    add("")
    return L


def envelope_face(path=ENVELOPE_JSON):
    """Is 9.6% a property of the book, or of which 1652 days we happened to live through?

    r1210 built the block-bootstrap envelope and made it name which book it describes.
    This round puts that distribution where the number is read: next to the backtest
    table, because a point estimate with no spread reads like a promise. Single
    implementation: every percentile comes from `etf_book_nav_envelope.read_published()`,
    which recomputes them from the stored resample rows and returns `drift`/`missing`/
    `unreadable` instead of numbers when it cannot. Absent reads as "cannot verify"."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_nav_envelope as _NE
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path,
                "detail": "reader failed (%s)" % str(exc)[:120]}
    try:
        return _NE.read_published(path=path)
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path,
                "detail": "reading failed (%s)" % str(exc)[:120]}


def envelope_block(env):
    """The lines this page prints about the envelope. Factored out so a selftest can feed
    it a missing / drifted / foreign face instead of trusting the render path by eye."""
    L = []
    add = L.append
    add("## 这一本账在它自己的日子里，能有多好、多差")
    add("")
    if (env or {}).get("status") != "ok":
        add("这一页没有拿到运气分布面（`%s`，状态 `%s`，%s）。所以上面的年化 **只是走过的一条路**，"
            "不是这个策略的好坏区间——在这里**无法核验**，也不印任何百分位数。"
            % (_rel((env or {}).get("artifact") or ENVELOPE_JSON, ROOT).replace(os.sep, "/"),
               (env or {}).get("status") or "unknown",
               (env or {}).get("detail") or "研究面还没建"))
        add("")
        return L
    if env.get("reconciliation") and env.get("reconciliation") != "same_object":
        add("- ⚠ 这张分布描述的**不是**这一页上面那张表里的书（对账判词 `%s`）——"
            "读之前先看包络面的对账节。" % env.get("reconciliation"))
        add("")
    cg = env.get("cagr") or {}
    dd = env.get("maxdd") or {}
    sh = env.get("sharpe") or {}
    pt = env.get("point") or {}
    pp = env.get("point_pctile") or {}
    shs = env.get("shares") or {}

    def f(v, unit="%"):
        return "—" if v is None else ("%.2f%s" % (v * 100, unit) if unit == "%" else "%.2f" % v)

    n = shs.get("n_resamples") or env.get("n_resamples")
    blk = env.get("block")
    add("- 做法：把这本账自己的日收益按 **%s 根 bar 一块**整块重抽（%s 次，重抽不改变决策规则），"
        "看同一本书在别的历史片段里会长什么样。样本 %s 根 bar，截至 %s。"
        % (blk if blk is not None else "?", n if n is not None else "?",
           env.get("bars") or "?", env.get("evidence_cutoff") or "—"))
    add("")
    add("| 在这 %s 条重抽历史里的位置 | 年化 | 最大回撤 |" % (n if n is not None else "?"))
    add("|---|---|---|")
    for lbl, q in (("**最差 5%**（运气很差）", "5"), ("中位（一半比它好）", "50"),
                   ("最好 5%（运气很好）", "95")):
        add("| %s | %s | %s |" % (lbl, f(cg.get(q)), f(dd.get(q))))
    add("")
    if pt.get("cagr") is not None:
        add("- 上面那张表的 **%.2f%%** 落在这条分布的第 **%s** 分位（夏普 %.2f 在第 %s 分位）。"
            "换句话说：它既不是好运气，也不是坏运气，是一个**典型**结果。"
            % (pt["cagr"] * 100, pp.get("cagr") if pp.get("cagr") is not None else "—",
               pt.get("sharpe") if pt.get("sharpe") is not None else float("nan"),
               pp.get("sharpe") if pp.get("sharpe") is not None else "—"))
        add("")
    loz, ddl = shs.get("cagr_le_zero"), shs.get("maxdd_le_line")
    if loz is not None and ddl is not None:
        add("- **会亏钱的份额 %.1f%%**（年化 ≤ 0）；**回撤跌破 -20%% 的份额 %.1f%%**。"
            "这两个数就是「最坏能坏到哪」——比任何单点回测都诚实，也是配仓位时该用的数。"
            % (loz * 100, ddl * 100))
        add("")
    add("> 运气分布面：`%s` ｜ 块长 %s（另有 1/5/10/20/40/60/120/250 臂的敏感度面）"
        % (_rel(env.get("artifact") or ENVELOPE_JSON, ROOT).replace(os.sep, "/"), blk))
    add("")
    return L


def cost_tape_face(path=COST_JSON):
    """Every published number charges 10 bp a side. Is that assumption true? (r1198)

    r1195 measured the tape and filed it in a research note; the page -- the face the CEO
    opens -- still silently carried the assumption. Same wound as E311, twice in a row.
    Single implementation: the measured cost, the three arms and the verdict come from
    `etf_book_cost_tape.read_published()`. Absent, unreadable or a control arm that does
    not reproduce the published CAGR reads as "cannot verify here", never as "the card is
    conservative"."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_book_cost_tape as _CT
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path, "sentence": None,
                "detail": "reader failed (%s)" % str(exc)[:120]}
    try:
        return _CT.read_published(path=path)
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": path, "sentence": None,
                "detail": "reading failed (%s)" % str(exc)[:120]}


def _load_ticket():
    """Pointer -> the dated ticket file it names."""
    ptr = _load(TICKET_PTR)
    rel = ptr.get("ticket_file") or ptr.get("file") or ptr.get("path")
    if isinstance(rel, str) and rel:
        cands = [rel] if os.path.isabs(rel) else [
            os.path.join(os.path.dirname(TICKET_PTR), rel),   # sibling of the pointer
            os.path.join(ROOT, rel),                          # repo-root relative
        ]
        for cand in cands:
            if os.path.exists(cand):
                return ptr, _load(cand), cand
    # fall back to the pointer itself when it already carries the ticket body
    if "ticket" in ptr:
        return ptr, ptr, TICKET_PTR
    raise FileNotFoundError("ticket body not resolvable from %s" % TICKET_PTR)


def trading_days_after(cal_dates, anchor, n):
    """The n-th trading day strictly after `anchor` (ISO strings, sorted asc)."""
    if anchor is None or n is None or int(n) <= 0:
        return None
    later = [d for d in cal_dates if d > anchor]
    if len(later) < int(n):
        return None
    return later[int(n) - 1]


def calendar_dates(path=CAL):
    out = []
    with open(path, encoding="utf-8") as fh:
        next(fh, None)
        for line in fh:
            s = line.strip()
            if s:
                out.append(s[:10])
    return out


def money_cny(tk, nav):
    """Backtest percentages -> yuan on this ticket's own capital.

    Pure unit change: every number is one already published on the ticket times `nav`.
    Anything unreadable stays None -- a 0 here would read as "this book earns nothing".
    """
    tk = tk or {}
    metrics = tk.get("metrics") or {}
    book = metrics.get("book") or {}
    bench = metrics.get("same_beta_benchmark") or {}
    out = {"capital_cny": round(float(nav or 0.0), 2), "expected_annual_cny": None,
           "benchmark_annual_cny": None, "excess_annual_cny": None,
           "worst_drawdown_cny": None, "basis": None}
    if not nav or not book:
        return out
    out["expected_annual_cny"] = round(float(book["cagr"]) * nav, 0)
    out["worst_drawdown_cny"] = round(float(book["maxdd"]) * nav, 0)
    out["basis"] = "backtest cagr/maxdd x this ticket's capital, no new assumption"
    if bench and metrics.get("excess_pp") is not None:
        out["benchmark_annual_cny"] = round(float(bench["cagr"]) * nav, 0)
        out["excess_annual_cny"] = round(float(metrics["excess_pp"]) / 100.0 * nav, 0)
    return out


TRADING_DAYS_PER_YEAR = 250

REPO_DIR = os.path.join(ROOT, "data", "repo_daily")
CASH_LEG_SYMBOL = "GC001"

# Where the cash ACTUALLY sits. The page can only advise; nothing in the repo could
# read the account, so the gap between "advice" and "placement" was invisible -- and
# invisible is exactly the 0% case the cash block warns about. This file is the
# handshake: whoever places the order records it once, the page reconciles every run.
PLACEMENT = os.path.join(ROOT, "state", "account", "cash_placement.json")
# A current account pays something, so "idle" is not a 100% loss. No panel exists for
# it, so the rate is a declared constant rather than a fabricated quote; a recorded
# placement may override it in the file.
DEMAND_RATE_PCT = 0.05
PLACEMENT_MAX_AGE_DAYS = 7
DEMAND_INSTRUMENTS = ("", "活期", "demand", "cash", "现金", "活期存款")


def _rel(path, base=ROOT):
    """Repository-relative when both live on one drive, the absolute path otherwise.

    os.path.relpath raises ValueError across drives, and the selftest pins its fixtures
    under %TEMP% (C:) while the repo sits on K: -- a display string must never be able
    to abort a run (same family as pool_deliverable_audit in r1371).
    """
    try:
        return os.path.relpath(path, base)
    except ValueError:
        return os.path.abspath(path)


def cash_yield(cash_amount, symbol=CASH_LEG_SYMBOL, panel_dir=REPO_DIR, window=20):
    """What the idle half earns: cash x the repo panel's own quoted close.

    The page told the reader to buy GC001 but never said what that is worth -- a
    number the CEO pays for by leaving the money in a current account instead.
    Again a pure unit change: the panel prints the rate, this multiplies it by the
    cash on the page. The 1-day repo spikes at quarter-end and before holidays, so
    the trailing mean is quoted beside it. Anything unreadable stays None -- 0 would
    read as "the cash earns nothing", which is exactly the case worth warning about.
    """
    out = {"leg": symbol, "quoted_as": "收盘年化利率 %", "rate_date": None,
           "rate_pct": None, "rate_20d_pct": None, "annual_cny": None,
           "daily_cny": None, "window": int(window), "basis": None,
           "panel": _rel(os.path.join(panel_dir, "%s.csv" % symbol), ROOT)
           .replace("\\", "/")}
    if cash_amount is None or float(cash_amount) <= 0:
        return out
    path = os.path.join(panel_dir, "%s.csv" % symbol)
    if not os.path.exists(path):
        return out
    rows = []
    with open(path, encoding="utf-8") as fh:
        next(fh, None)
        for line in fh:
            parts = line.strip().split(",")
            if len(parts) < 5:
                continue
            try:
                rows.append((parts[0], float(parts[4])))
            except ValueError:
                continue
    rows = [r for r in rows if 0.0 < r[1] < 200.0]   # same sanity band the collector enforces
    if not rows:
        return out
    out["rate_date"], out["rate_pct"] = rows[-1]
    tail = rows[-int(window):]
    out["rate_20d_pct"] = round(sum(v for _, v in tail) / len(tail), 4)
    out["annual_cny"] = round(float(cash_amount) * out["rate_pct"] / 100.0, 0)
    out["daily_cny"] = round(out["annual_cny"] / TRADING_DAYS_PER_YEAR, 0)
    out["basis"] = ("cash x panel close rate / 100; per session = annual / %d sessions"
                    % TRADING_DAYS_PER_YEAR)
    return out


LADDER_TENORS = ("GC001", "GC003", "GC007", "GC014", "GC028", "GC091")
LADDER_WINDOWS_YEARS = (1, 3, 5)
# Frozen adoption rule. A longer tenor is only worth the lock-up if it pays at
# least 20bp a year MORE than rolling the 1-day leg, in BOTH the 1-year and the
# 3-year window (a single year can be a rate-regime accident), while leaving
# <=1% of the calendar with the cash uninvested (maturity landing on a weekend),
# and while being ahead in a majority of the complete calendar years on record.
LADDER_MIN_EDGE_BP = 20.0
LADDER_MAX_IDLE_SHARE = 0.01
LADDER_MIN_POSITIVE_YEAR_SHARE = 0.60
LADDER_YEARS_CHECKED = 5


def repo_rows(symbol, panel_dir=REPO_DIR):
    """(date, close) pairs from one repo panel, holding the collector's sanity band."""
    path = os.path.join(panel_dir, "%s.csv" % symbol)
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, encoding="utf-8") as fh:
        next(fh, None)
        for line in fh:
            parts = line.strip().split(",")
            if len(parts) < 5:
                continue
            try:
                val = float(parts[4])
                if 0.0 < val < 200.0:
                    rows.append((dt.date.fromisoformat(parts[0]), val))
            except ValueError:
                continue
    return rows


def rolled_yield(rows, tenor_days, start=None, end=None):
    """Annualised return of rolling a repo of this maturity, measured on the calendar.

    A repo quote is per annum, so what the money earns is rate x days held / 365 --
    and the days held are not the tenor. One-day money bought on a Friday is lent
    over the weekend (that is why Friday's quote dips); a 3-day leg bought on a
    Thursday matures on a Sunday and the cash sits idle until Monday. Both are read
    off the panel's own calendar here instead of being assumed, and the idle days
    are returned rather than hidden: they are the reason a longer tenor can pay
    less, not more.
    """
    if not rows:
        return None
    dates = [d for d, _ in rows]
    rate = dict(rows)
    idx = [i for i, d in enumerate(dates)
           if (start is None or d >= start) and (end is None or d <= end)]
    if len(idx) < 2:
        return None
    i, last = idx[0], idx[-1]
    tot = 0.0
    days = 0
    idle = 0
    rolls = 0
    while i < last:
        d = dates[i]
        tenor = int(tenor_days)
        mat = d + dt.timedelta(days=tenor)
        j = i + 1
        while j < len(dates) and dates[j] < mat:
            j += 1
        if j > last:
            break
        accrue = (dates[j] - d).days if tenor == 1 else (mat - d).days
        tot += rate[d] / 100.0 * accrue / 365.0
        rolls += 1
        idle += max(0, (dates[j] - max(mat, d + dt.timedelta(days=accrue))).days)
        days += (dates[j] - d).days
        i = j
    if days <= 0:
        return None
    return {"realized_pct": round(tot / (days / 365.0) * 100.0, 4), "rolls": rolls,
            "idle_days": idle, "days": days,
            "idle_share": round(float(idle) / days, 4)}


def cash_ladder(cash_amount, panel_dir=REPO_DIR, tenors=LADDER_TENORS,
                windows=LADDER_WINDOWS_YEARS, years_checked=LADDER_YEARS_CHECKED,
                min_edge_bp=LADDER_MIN_EDGE_BP, max_idle_share=LADDER_MAX_IDLE_SHARE,
                min_positive_year_share=LADDER_MIN_POSITIVE_YEAR_SHARE):
    """Should the idle half be laddered out to a longer repo, or left at one day?

    The page already says "buy GC001"; the question a reader actually has is whether
    a longer tenor pays for the lock-up. It does not follow from the quotes: they are
    per annum, so a 7-day leg can only win if it clears the 1-day leg's own
    quarter-end spikes plus its maturity friction. So every tenor is rolled on the
    panel's own calendar and priced against rolling the 1-day leg in the same window.
    The adoption rule is a frozen constant (see LADDER_MIN_EDGE_BP) and the verdict is
    recomputed from those cells, never written by hand. Unreadable panels stay None.
    """
    base = tenors[0]
    base_rows = repo_rows(base, panel_dir)
    out = {"base": base, "tenors": [], "pick": None, "verdict": "NOT-ASSESSED",
           "reason": None, "cash_amount_cny": None,
           "forgotten_day_cny": None, "rolls": {}, "windows_years": list(windows),
           "rule": {"min_edge_bp": min_edge_bp, "max_idle_share": max_idle_share,
                    "min_positive_year_share": min_positive_year_share,
                    "years_checked": years_checked,
                    "basis": ("edge must clear min_edge_bp in the 1y AND 3y windows, "
                              "idle <= max_idle_share, positive in "
                              "min_positive_year_share of complete years")}}
    if not base_rows:
        out["reason"] = "一天期面板缺席，无法做基线"
        return out
    end = base_rows[-1][0]
    cash = None if cash_amount is None else float(cash_amount)
    out["cash_amount_cny"] = None if (cash is None or cash <= 0) else round(cash, 2)
    base_by_window = {y: rolled_yield(base_rows, 1, end - dt.timedelta(days=365 * y))
                      for y in windows}
    base_spot = base_rows[-1][1]
    if out["cash_amount_cny"]:
        out["forgotten_day_cny"] = round(out["cash_amount_cny"] * base_spot / 100.0 / 365.0, 0)

    complete_years = sorted({d.year for d, _ in base_rows if d.year < end.year})[-years_checked:]

    for symbol in tenors:
        rows = repo_rows(symbol, panel_dir)
        tenor_days = {"GC001": 1, "GC003": 3, "GC004": 4, "GC007": 7,
                      "GC014": 14, "GC028": 28, "GC091": 91, "GC182": 182}.get(
            symbol, int(symbol[-3:]) if symbol[-3:].isdigit() else 1)
        row = {"symbol": symbol, "tenor_days": tenor_days, "spot_pct": None,
               "spot_date": None, "mean250_pct": None, "realized": {}, "edge_bp": {},
               "rolls_1y": None, "idle_days_1y": None, "idle_share_1y": None,
               "annual_cny_spot": None, "annual_cny_realized_1y": None,
               "positive_years": None, "years_checked": None, "verdict": None,
               "reason": None}
        out["tenors"].append(row)
        if not rows:
            row["verdict"] = "NO-PANEL"
            row["reason"] = "面板缺席"
            continue
        row["spot_date"], row["spot_pct"] = rows[-1][0].isoformat(), rows[-1][1]
        tail = [v for _, v in rows[-250:]]
        row["mean250_pct"] = round(sum(tail) / len(tail), 4)
        if row["spot_pct"] is not None and out["cash_amount_cny"]:
            row["annual_cny_spot"] = round(out["cash_amount_cny"] * row["spot_pct"] / 100.0, 0)
        if symbol == base:
            row["verdict"] = "BASELINE"
            row["reason"] = "基线：一天期，季末飙高全部吃进"
        for y in windows:
            r = rolled_yield(rows, tenor_days, end - dt.timedelta(days=365 * y))
            if r is None:
                continue
            row["realized"][str(y)] = r
            if y == 1:
                row["rolls_1y"] = r["rolls"]
                row["idle_days_1y"] = r["idle_days"]
                row["idle_share_1y"] = r["idle_share"]
                if out["cash_amount_cny"]:
                    row["annual_cny_realized_1y"] = round(
                        out["cash_amount_cny"] * r["realized_pct"] / 100.0, 0)
            b = base_by_window.get(y)
            if b is not None and symbol != base:
                row["edge_bp"][str(y)] = round((r["realized_pct"] - b["realized_pct"]) * 100.0, 1)
        out["rolls"][symbol] = row["rolls_1y"]
        if symbol != base:
            pos = tot = 0
            for yr in complete_years:
                a = dt.date(yr, 1, 1)
                b2 = dt.date(yr, 12, 31)
                rr = rolled_yield(rows, tenor_days, a, b2)
                bb = rolled_yield(base_rows, 1, a, b2)
                if rr is None or bb is None:
                    continue
                tot += 1
                if rr["realized_pct"] > bb["realized_pct"]:
                    pos += 1
            row["positive_years"] = pos
            row["years_checked"] = tot
            e1 = row["edge_bp"].get("1")
            e3 = row["edge_bp"].get("3")

            def _over(e):
                return ("多 %.1f bp" % e) if e >= 0 else ("少 %.1f bp" % -e)

            if e1 is None or e3 is None:
                row["verdict"] = "NOT-ASSESSED"
                row["reason"] = "窗口内历史不足"
            else:
                # every failing gate is named: reporting only the first one would tell the
                # reader "idle days" when the real miss is a 12bp gap to the door
                fails = []
                if e1 < min_edge_bp or e3 < min_edge_bp:
                    fails.append("%s（1年）/ %s（3年），门槛 %.0f bp"
                                 % (_over(e1), _over(e3), min_edge_bp))
                if row["idle_share_1y"] is not None and row["idle_share_1y"] > max_idle_share:
                    fails.append("到期撞上休市日，一年空转 %d 天（%.1f%% > %.0f%%）"
                                 % (row["idle_days_1y"], row["idle_share_1y"] * 100.0,
                                    max_idle_share * 100.0))
                if tot and (float(pos) / tot) < min_positive_year_share:
                    fails.append("%d 个完整年只赢了 %d 年" % (tot, pos))
                if fails:
                    row["verdict"] = "REJECT"
                    row["reason"] = "；".join(fails)
                else:
                    row["verdict"] = "ADOPT"
                    row["reason"] = ("1年 %s / 3年 %s，%d/%d 年为正，空转 %.1f%%"
                                     % (_over(e1), _over(e3), pos, tot,
                                        (row["idle_share_1y"] or 0.0) * 100.0))

    adopted = [r for r in out["tenors"] if r["verdict"] == "ADOPT"]
    if adopted:
        best = max(adopted, key=lambda r: min(float(r["edge_bp"]["1"]),
                                              float(r["edge_bp"]["3"])))
        out["pick"] = best["symbol"]
        out["verdict"] = "ADOPT"
        out["reason"] = "%s：%s" % (best["symbol"], best["reason"])
    else:
        out["pick"] = base
        out["verdict"] = "KEEP-1D"
        rejected = [r for r in out["tenors"] if r["verdict"] == "REJECT"]
        if rejected:
            out["reason"] = "；".join("%s %s" % (r["symbol"], r["reason"]) for r in rejected)
        else:
            out["reason"] = "没有可评估的长期限腿"
    return out


def cash_handshake(cash_amount, ladder, placement_path=PLACEMENT, today=None,
                   max_age_days=PLACEMENT_MAX_AGE_DAYS, demand_rate_pct=DEMAND_RATE_PCT):
    """Is the cash where the page says it should be? (advice vs account, priced)

    The page has been telling the reader to hold every idle yuan in the 1-day repo,
    while nothing anywhere could see whether that happened -- so a reader who left it
    in the current account read the same page as one who did not. This closes the loop
    on the only side the company can observe: what the account says was placed.

    Three honesty rules, learned from this file's own earlier faces:
      - no recording -> UNRECORDED and a None gap, never "0 missing" (unread is not zero)
      - the gap is priced from the repo panel's own close minus the declared demand
        rate, so it moves with the market instead of being a typed-in number
      - a revealed fact that contradicts the book (more placed than the book holds)
        is surfaced as OVER-PLACED rather than silently clamped to a comfortable 0
    """
    out = {"status": "UNRECORDED", "recorded": False, "asof": None, "age_days": None,
           "recorded_by": None, "placements": [], "placed_cny": None, "idle_cny": None,
           "idle_share": None, "repo_rate_pct": None, "repo_rate_date": None,
           "demand_rate_pct": float(demand_rate_pct),
           "gap_annual_cny": None, "gap_daily_cny": None,
           "worst_case_annual_cny": None, "stale": None, "reason": None,
           "placement_file": _rel(placement_path, ROOT).replace("\\", "/"),
           "basis": ("idle = book cash - recorded repo placements; gap = idle x "
                     "(repo panel close - declared demand rate) / 100")}
    cash = None if cash_amount is None else float(cash_amount)
    out["cash_amount_cny"] = None if (cash is None or cash <= 0) else round(cash, 2)

    # the rate the page already quotes -- one price source, never re-read here
    base = None
    for row in (ladder or {}).get("tenors") or []:
        if row.get("symbol") == (ladder or {}).get("base"):
            base = row
            break
    if base:
        out["repo_rate_pct"] = base.get("spot_pct")
        out["repo_rate_date"] = base.get("spot_date")
    if out["cash_amount_cny"] and out["repo_rate_pct"] is not None:
        out["worst_case_annual_cny"] = round(
            out["cash_amount_cny"] * (float(out["repo_rate_pct"]) - float(demand_rate_pct))
            / 100.0, 0)

    if not os.path.exists(placement_path):
        out["reason"] = "账户实况未登记，无法判断钱在不在逆回购里"
        return out
    try:
        with open(placement_path, encoding="utf-8-sig") as fh:
            rec = json.load(fh)
    except Exception as exc:
        out["reason"] = "登记件读不动（%s）" % exc
        return out

    out["recorded_by"] = rec.get("recorded_by")
    out["asof"] = rec.get("asof")
    rows = [r for r in (rec.get("placements") or []) if isinstance(r, dict)]
    out["placements"] = [{"instrument": r.get("instrument"),
                          "amount_cny": r.get("amount_cny"),
                          "rate_pct": r.get("rate_pct"),
                          "rate_date": r.get("rate_date")} for r in rows]
    if rec.get("demand_rate_pct") is not None:
        try:
            out["demand_rate_pct"] = float(rec["demand_rate_pct"])
            if out["cash_amount_cny"] and out["repo_rate_pct"] is not None:
                out["worst_case_annual_cny"] = round(
                    out["cash_amount_cny"]
                    * (float(out["repo_rate_pct"]) - out["demand_rate_pct"]) / 100.0, 0)
        except (TypeError, ValueError):
            pass
    if str(rec.get("recorded_by") or "").strip().lower() in ("", "unrecorded", "none", "null"):
        out["reason"] = "账户实况未登记（登记件在位但没人填）"
        return out

    out["recorded"] = True
    try:
        placed = 0.0
        for r in rows:
            amt = r.get("amount_cny")
            if amt is None:
                continue
            inst = str(r.get("instrument") or "").strip()
            if inst.lower() in DEMAND_INSTRUMENTS:
                continue
            placed += float(amt)
        out["placed_cny"] = round(placed, 2)
    except (TypeError, ValueError) as exc:
        out["recorded"] = False
        out["reason"] = "登记件金额不可读（%s）" % exc
        return out

    ref = today or dt.date.today()
    if isinstance(ref, str):
        ref = dt.date.fromisoformat(ref[:10])
    if out["asof"]:
        try:
            out["age_days"] = (ref - dt.date.fromisoformat(str(out["asof"])[:10])).days
        except ValueError:
            out["age_days"] = None
    out["stale"] = (out["age_days"] is not None and out["age_days"] > int(max_age_days))

    if out["cash_amount_cny"] is None:
        out["reason"] = "账面现金不可读，无法对账"
        out["recorded"] = False
        return out

    idle = out["cash_amount_cny"] - out["placed_cny"]
    tol = max(1.0, 0.001 * out["cash_amount_cny"])
    if idle < -tol:
        out["status"] = "OVER-PLACED"
        out["idle_cny"] = 0.0
        out["idle_share"] = 0.0
        out["reason"] = ("登记的在仓金额比账面现金还多 ¥%s：登记件与账本对不上，先核账再谈缺口"
                         % format(-idle, ",.0f"))
        return out
    idle = max(0.0, idle)
    out["idle_cny"] = round(idle, 2)
    out["idle_share"] = round(idle / out["cash_amount_cny"], 4) if out["cash_amount_cny"] else None
    if out["repo_rate_pct"] is not None:
        out["gap_annual_cny"] = round(idle * (float(out["repo_rate_pct"])
                                              - out["demand_rate_pct"]) / 100.0, 0)
        out["gap_daily_cny"] = round(out["gap_annual_cny"] / TRADING_DAYS_PER_YEAR, 0)
    if idle <= tol:
        out["status"] = "IN-PLACE"
        out["reason"] = "账面现金已全部登记在逆回购里"
    elif idle >= out["cash_amount_cny"] * 0.995:
        out["status"] = "IDLE"
        out["reason"] = "登记件显示现金全部不在逆回购里（等于活期）"
    else:
        out["status"] = "PARTIAL"
        out["reason"] = "只登记了一部分"
    if out["stale"]:
        out["reason"] = ("登记于 %s（%s 天前，已过期：超过 %s 天）：先重记一次再判断；%s"
                         % (out["asof"], out["age_days"], max_age_days, out["reason"]))
    return out


STRESS_DIR = os.path.join(ROOT, "results", "etf_book_stress")
STRESS_WINDOWS = (1, 5, 20)


def stress_stats(daily, windows=STRESS_WINDOWS, capital=None):
    """Worst run of `n` consecutive days for a fixed-weight book.

    `daily` is a pandas Series of (weight-applied) book returns; a name that printed no
    price on a leg simply earns nothing for that leg, which is how the research engine
    treats it too. Everything here is the same arithmetic in a different window -- no new
    assumption, no fitted model. Returns None when there is not enough history, so a
    missing panel can never be read as "this book never loses".
    """
    if daily is None or len(daily) == 0:
        return None
    s = daily.dropna()
    if len(s) == 0:
        return None
    out = {"n_days": int(len(s)), "first": str(s.index[0])[:10], "last": str(s.index[-1])[:10],
           "worst": {}, "capital_cny": capital}
    for n in windows:
        if len(s) < n:
            out["worst"]["%dd" % n] = None
            continue
        # compounded, not summed: the reader is being told what the money did over N days
        gross = (1.0 + s).cumprod() / (1.0 + s).cumprod().shift(n) - 1.0
        roll = gross.dropna()
        if len(roll) == 0:
            out["worst"]["%dd" % n] = None
            continue
        when = roll.idxmin()
        val = float(roll.min())
        row = {"pct": round(val * 100.0, 2), "end_date": str(when)[:10]}
        row["cny"] = None if capital is None else round(val * float(capital), 0)
        out["worst"]["%dd" % n] = row
    return out


def panel_fingerprint(close):
    """Content hash of the panel a replay was priced against -- not its date.

    A flip repair inside the panel rewrites today's worst window without moving today's
    date, so a cache keyed on the bar alone hands back numbers for a world that has
    since been corrected (r1374 hit exactly this on the per-tier replay; this is the
    one implementation, imported there as well).
    """
    h = hashlib.sha256()
    if close is not None and len(getattr(close, "index", [])):
        try:
            import pandas as _pd
            h.update(("shape|%d,%d" % close.shape).encode())
            h.update(_pd.util.hash_pandas_object(close.fillna(0.0), index=True)
                     .values.tobytes())
        except Exception:
            h.update(b"|unhashable")
    return h.hexdigest()


def book_returns(close, names, wts):
    """Fixed-weight book return series for a panel -- one arithmetic, both runs use it."""
    import pandas as _pd
    legs = {}
    for n, w in zip(names, wts):
        if n in close.columns:
            legs[n] = close[n].astype(float).pct_change().fillna(0.0) * w
        else:
            legs[n] = _pd.Series(0.0, index=close.index)
    return _pd.DataFrame(legs).sum(axis=1)


def flip_threshold():
    """The published repair threshold, read from its owner -- None when it cannot be read."""
    try:
        import sys as _sys
        _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import etf_equity_alpha as A
        return float(getattr(A, "FLIP_THR", 0.35))
    except Exception:
        return None


def clean_panel(close):
    """The same panel with repairable price flips flattened -- published rule, imported.

    `etf_equity_alpha.repair_flips` is the single implementation (E270). It wants the
    open face as well; this page is close-only, so the open argument is the close face
    and the repaired open result is discarded. Returns (clean_close, n_flattened, thr),
    or (None, 0, None) when the rule cannot be imported -- no clean claim rather than a
    fabricated one.
    """
    try:
        import sys as _sys
        _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import etf_equity_alpha as A
    except Exception:
        return None, 0, None
    thr = float(getattr(A, "FLIP_THR", 0.35))
    try:
        adj, _open_ignored, n = A.repair_flips(close, close, thr)
        return adj, int(n), thr
    except Exception:
        return None, 0, None


def contamination_block(raw_st, clean_st, n_flattened, thr):
    """Which part of the printed worst window is a data print rather than a market day.

    The stress table replays today's weights over the raw panel; the raw panel carries
    single-day quote flips (share-count changes read as -90% returns), and the book's own
    worst day sits on one of them. This block answers that question in the page's own
    construction -- same weights, same windows, the published repair applied -- instead of
    quoting a number from a different face. It decides nothing: switching production onto
    the repaired panel moves every number this book has published, which is a separate,
    deliberate decision.
    """
    out = {"flip_thr": thr, "flip_prints_flattened": int(n_flattened),
           "raw_worst": {}, "clean_worst": {}, "differs": False, "sentence": None}
    for n in STRESS_WINDOWS:
        r = ((raw_st or {}).get("worst") or {}).get("%dd" % n)
        c = ((clean_st or {}).get("worst") or {}).get("%dd" % n)
        out["raw_worst"]["%dd" % n] = None if not r else {
            "pct": r.get("pct"), "end_date": r.get("end_date"), "cny": r.get("cny")}
        out["clean_worst"]["%dd" % n] = None if not c else {
            "pct": c.get("pct"), "end_date": c.get("end_date"), "cny": c.get("cny")}
    r1 = out["raw_worst"].get("1d")
    c1 = out["clean_worst"].get("1d")
    if not r1:
        return out
    if not c1:
        out["sentence"] = ("这里没有可比对的修复版读数（修复规则没有返回本页需要的窗口，"
                           "或者它根本读不到），所以不主张这个最差日是干净还是脏。")
        return out
    out["differs"] = abs(float(r1["pct"]) - float(c1["pct"])) > 0.005
    if not out["differs"]:
        out["sentence"] = ("按同一条修复规则把面板里的单日翻转压平（共 %d 处，阈值 %.0f%%）之后，"
                           "这张表最差的一天没有变化（%+.2f%%），也就是说它是行情，不是报价。"
                           % (n_flattened, (thr or 0.0) * 100.0, float(r1["pct"])))
        return out
    out["sentence"] = ("面板里有 %d 处单日超过 %.0f%% 的报价翻转（份额变动被读成暴跌），这张表最差的一天 "
                       "%+.2f%%（%s）就是其中之一；按同一条规则（etf_equity_alpha.repair_flips，"
                       "导入未改写）把翻转压平后，最差的一天是 %+.2f%%（%s）。修与不修是一次单独的决定："
                       "它会把这本书已发布的每一个数字一起挪动，不在本页里悄悄生效。"
                       % (n_flattened, (thr or 0.0) * 100.0, float(r1["pct"]), r1.get("end_date"),
                          float(c1["pct"]), c1.get("end_date")))
    return out


def stress_cache_digest(close, priced_bar, capital, windows, order, flip_thr=None):
    """What the cached replay was computed FROM: bar, capital, weights, panel bytes.

    Every one of these can move while the priced bar stays put: a repaired print, a
    re-priced ticket (weights rescale), a different capital figure. Keying on the date
    alone would answer a question nobody asked.
    """
    h = hashlib.sha256()
    h.update(("bar|%s|cap|%.4f|win|%s" % (
        priced_bar, float(capital or 0.0),
        ",".join(str(int(w)) for w in windows or STRESS_WINDOWS))).encode())
    h.update(("|w|" + ",".join(
        "%s:%.10f" % (o.get("symbol"), float(o.get("weight") or 0.0))
        for o in order or [])).encode())
    h.update(("|panel|" + panel_fingerprint(close)).encode())
    h.update(("|flipthr|%.4f" % (flip_thr if flip_thr is not None else -1.0)).encode())
    return h.hexdigest()


def build_stress(order, capital, priced_bar, close=None):
    """Data path: replay today's weights over the whole panel, worst-window report.

    Cached per (priced bar, capital, weights, panel content) -- re-walking 20 years of a
    1,500-column panel every tick is cost without information, but the bar alone is not
    an identity: a repaired print rewrites the worst window without moving the date, and
    a re-priced ticket changes the weights on the very same bar. A cache written before
    this digest existed has no `inputs_sha256` and is a MISS, not a hit.
    """
    if not order:
        return None
    if close is None:
        try:
            import sys as _sys
            _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import etf_book_forward as F
            close, _o, _a, _f, _sc, _cls, _nf = F.build_inputs()
        except Exception as exc:
            return {"error": "%s: %s" % (type(exc).__name__, exc), "worst": {},
                    "capital_cny": capital}
    inputs_sha = stress_cache_digest(close, priced_bar, capital, STRESS_WINDOWS, order,
                                     flip_thr=flip_threshold())
    cache = os.path.join(STRESS_DIR, "STRESS-%s.json" % str(priced_bar).replace("-", ""))
    if os.path.exists(cache):
        try:
            with open(cache, encoding="utf-8") as fh:
                c = json.load(fh)
            if (c.get("inputs_sha256") == inputs_sha
                    and c.get("priced_bar") == str(priced_bar)):
                return c
        except (OSError, ValueError):
            pass
    try:
        names = [o.get("symbol") for o in order]
        wts = [float(o.get("weight") or 0.0) for o in order]
        book = book_returns(close, names, wts)
    except Exception as exc:               # honest: no panel -> no stress claim
        return {"error": "%s: %s" % (type(exc).__name__, exc), "worst": {}, "capital_cny": capital}
    st = stress_stats(book, capital=capital)
    if st is None:
        return None
    # the same replay on the repaired panel, so the page can say whether its own worst
    # day is a market day or a quote flip -- exactly one number (the raw one) is published
    clean, n_flat, thr = clean_panel(close)
    clean_st = None
    if clean is not None:
        try:
            import pandas as _pd
            clean_st = stress_stats(book_returns(clean, names, wts), capital=capital)
        except Exception:
            clean_st = None
    st["contamination"] = contamination_block(st, clean_st, n_flat, thr)
    st["capital_cny"] = round(float(capital or 0.0), 2)
    st["basis"] = ("今天的权重原封不动摆回整段面板（现金 0 息），取最坏的连续 N 个交易日；"
                   "不是策略实际路径，是同一批票的最坏窗口")
    try:
        os.makedirs(STRESS_DIR, exist_ok=True)
        with open(cache, "w", encoding="utf-8", newline="\n") as fh:
            st["priced_bar"] = str(priced_bar)
            st["inputs_sha256"] = inputs_sha
            json.dump(st, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    except OSError:
        pass
    return st


def today_action(p):
    """Does the reader have to touch the account today?

    The ticket is re-priced every session against a fixed set of weights, so the
    share counts in the order list change daily even though the DECISION has not
    moved since `book_decided_at`. Publishing that list as "buy this today" makes
    a holder re-buy a book they already own -- at 8bp a side that is more than the
    book's own expected annual return. So the page has to name the world the
    reader is in:

      rebalance -- this priced bar IS the decision bar: trade.
      open      -- the reader is not in the book yet: buy the list once.
      hold      -- already holding and the decision has not moved: do nothing.
      unknown   -- a date face is missing; refuse to guess.
    """
    decided = p.get("book_decided_at")
    priced = p.get("priced_bar")
    holding = bool((p.get("forward") or {}).get("bars"))
    out = {"mode": "unknown", "holding": holding, "book_decided_at": decided,
           "priced_bar": priced, "next_trade_date": None, "cost_if_retraded_pct_per_year": None,
           "cost_basis": None}
    if not decided or not priced:
        return out
    decided_bar_is_priced = (str(decided) == str(priced))
    if decided_bar_is_priced:
        out["mode"] = "rebalance" if holding else "open"
    else:
        out["mode"] = "hold" if holding else "open"
    out["next_trade_date"] = p.get("next_rebalance_date") if out["mode"] == "hold" else priced

    # What chasing this list every session would cost, in percent of CAPITAL per year.
    # 2 sides x cost_bp on the book slice x a 250-session year -- an assumption, published.
    cost_bp = p.get("cost_bp_per_side")
    k = p.get("k_now")
    if cost_bp and k:
        per_year = 2.0 * (float(cost_bp) / 10000.0) * TRADING_DAYS_PER_YEAR * float(k)
        out["cost_if_retraded_pct_per_year"] = round(per_year * 100.0, 2)
        out["cost_basis"] = ("2 sides x %s bp x %d sessions x book share %.4f, on capital"
                             % (cost_bp, TRADING_DAYS_PER_YEAR, float(k)))
    return out


def build(with_stress=False):
    ptr, tk, tk_path = _load_ticket()
    card = _load(CARD) if os.path.exists(CARD) else {}
    ledger = _load(LEDGER) if os.path.exists(LEDGER) else {}

    nav = float(tk.get("ticket", {}).get("nav") or 0.0)
    order = list(tk.get("ticket", {}).get("order") or [])
    cash_amt = float(tk.get("ticket", {}).get("cash_amount") or 0.0)
    book_amt = float(tk.get("ticket", {}).get("book_amount") or 0.0)
    cash_w = float(tk.get("ticket", {}).get("cash_weight") or 0.0)
    cash_leg = tk.get("ticket", {}).get("cash_leg") or "cash (no instrument named)"

    bars = list(ledger.get("bars") or [])
    fwd = {"bars": len(bars), "inception": None, "nav": None, "since_inception_pct": None,
           "as_of": None}
    if bars:
        fwd["inception"] = bars[0].get("bar")
        fwd["as_of"] = bars[-1].get("bar")
        fwd["nav"] = bars[-1].get("nav")
        fwd["since_inception_pct"] = round((float(bars[-1]["nav"]) - 1.0) * 100.0, 4)

    # the daily answer to "are we beating just buying the four exposures" -- read off the
    # forward ledger's own benchmark block, never re-priced here (one price source)
    bench = (ledger.get("benchmark") or {}).get("latest") or {}
    # r1316: a spread with no horizon is read as a verdict. Carry the ledger's own
    # power table (what edge this record can resolve inside 6m/1y/2y/3y, and how
    # many YEARS the published alphas would need) beside the number.
    _pw = ((ledger.get("benchmark") or {}).get("significance") or {}).get("power") or {}
    vs_basket = None
    if bench.get("excess_pp") is not None:
        vs_basket = {
            "bar": bench.get("bar"),
            "book_nav": bench.get("book_nav"),
            "basket_nav": bench.get("basket_nav"),
            "excess_pp": bench.get("excess_pp"),
            "basket": ((ledger.get("benchmark") or {}).get("labels") or {}),
            "basis": "等权 1/4、同一换仓日、次日开盘成交",
            "horizon": ({"min_detectable_edge_pp": _pw.get("min_detectable_edge_pp"),
                         "years_for_80pct_power": _pw.get("years_for_80pct_power"),
                         "candidate_sources": _pw.get("candidate_sources")}
                        if _pw.get("available") else None),
        }

    bt = (card.get("backtest") or {})
    page_window_label = window_label_face()
    band = {}
    # the executable ticket prices its own book; quote that口径 first, from the ticket itself
    tk_book = (tk.get("metrics") or {}).get("book") or {}
    wl = page_window_label
    if tk_book:
        label = "%d 名·可执行单口径（本单这份账）" % (tk.get("n_hold") or len(order))
        tr = (wl or {}).get("table_row") or {} if (wl or {}).get("status") == "ok" else {}
        if (tr.get("full") or {}).get("cagr_pct") is not None:
            # r1216: the full column carries the FULL window; the ticket's own 683-bar
            # return moves to the 2024+ column, where the card's 18.35% already sits.
            band[label] = {
                "full": {"cagr_pct": round(tr["full"]["cagr_pct"], 2),
                         "sharpe": round(tr["full"]["sharpe"] or 0.0, 2),
                         "maxdd_pct": round(tr["full"]["maxdd_pct"] or 0.0, 2)},
                "oos": {"cagr_pct": round(tr["oos"]["cagr_pct"], 2),
                        "sharpe": round(tr["oos"]["sharpe"] or 0.0, 2),
                        "maxdd_pct": round(tr["oos"]["maxdd_pct"] or 0.0, 2)}}
            # r1216b: the middle window rides along only when the face publishes it
            # (the three segments tile the full window). Without it the cell is a
            # dash, never a number borrowed from a neighbour.
            if (tr.get("is") or {}).get("cagr_pct") is not None:
                band[label]["is"] = {
                    "cagr_pct": round(tr["is"]["cagr_pct"], 2),
                    "sharpe": round(tr["is"].get("sharpe") or 0.0, 2),
                    "maxdd_pct": round(tr["is"].get("maxdd_pct") or 0.0, 2)}
        else:
            # no relabelled cell: print the ticket's own numbers in the 2024+ column only,
            # because that is the window they were measured on. "Unknown" never reads as a
            # full-window return (E192 / E256 lineage).
            band[label] = {
                "full": {"cagr_pct": None, "sharpe": None, "maxdd_pct": None},
                "oos": {"cagr_pct": round(tk_book["cagr"] * 100, 2),
                        "sharpe": round(tk_book["sharpe"], 2),
                        "maxdd_pct": round(tk_book["maxdd"] * 100, 2)}}
    for key, label in (("n5_base", "5 名·beta 覆盖"),
                       ("n12_vt08", "12 名·8% 波动目标（生产卡片口径）")):
        blk = bt.get(key) or {}
        if not blk:
            continue
        row = {}
        for seg in ("full", "is", "oos"):
            s = blk.get(seg) or {}
            if s:
                row[seg] = {"cagr_pct": round(s["cagr"] * 100, 2),
                            "sharpe": round(s["sharpe"], 2),
                            "maxdd_pct": round(s["maxdd"] * 100, 2)}
        band[label] = row

    # the same percentages expressed in yuan on THIS ticket's capital -- a unit change, not a new estimate
    money = money_cny(tk, nav)

    feed = tk.get("feed_status") or {}
    agree = tk.get("card_agreement") or {}
    cal = calendar_dates() if os.path.exists(CAL) else []
    next_reb = trading_days_after(cal, tk.get("evidence_cutoff"), tk.get("next_decision_bars"))
    today = dt.date.today().isoformat()

    page = {
        "schema": "etf-book-ceo-page/v1",
        "generated_for_date": today,
        "evidence_cutoff": tk.get("evidence_cutoff"),
        "priced_bar": feed.get("ticket_bar"),
        "feed_status": feed.get("status"),
        "feed_lag_days": feed.get("lag_days"),
        "capital_cny": nav,
        "book_amount_cny": round(book_amt, 2),
        "cash_amount_cny": round(cash_amt, 2),
        "cash_weight": round(cash_w, 4),
        "cash_leg": cash_leg,
        "cash_yield": cash_yield(cash_amt),
        "cash_ladder": cash_ladder(cash_amt),
        "k_now": tk.get("k_now"),
        "n_hold": tk.get("n_hold"),
        "cost_bp_per_side": tk.get("cost_bp_per_side"),
        "book_decided_at": tk.get("book_decided_at"),
        "next_decision_bars": tk.get("next_decision_bars"),
        "next_rebalance_date": next_reb,
        "order": [{"symbol": o.get("symbol"), "class": o.get("class"),
                   "class_zh": CLASS_ZH.get(o.get("class"), o.get("class")),
                   "weight": o.get("weight"), "price": o.get("price"),
                   "lots": o.get("lots"), "shares": o.get("shares"),
                   "amount_cny": o.get("amount")} for o in order],
        "forward": fwd,
        "vs_basket": vs_basket,
        "backtest_band": band,
        "excess_pp": (tk.get("metrics") or {}).get("excess_pp"),
        "money_cny": money,
        "ticket_book": tk_book or None,
        "same_beta_benchmark": (tk.get("metrics") or {}).get("same_beta_benchmark"),
        "agreement": {"same_decision_bar": agree.get("same_decision_bar"),
                      "same_priced_bar": agree.get("same_priced_bar"),
                      "card_names": agree.get("card_names")},
        "sources": {"ticket": _rel(tk_path, ROOT),
                    "card": "results/etf_book_production/latest.json",
                    "ledger": "results/etf_book_forward/LEDGER.json",
                    "calendar": "data/exchange_calendar.csv"},
        "caveats": [
            "回测票池是现存 ETF（有幸存者偏差）；2020-2023 段弱、收益主要集中在 2024 之后。",
            "前向账本只有 %d 个交易日，自起始净值 %.4f 不构成业绩记录。" % (fwd["bars"], fwd["nav"] or 0.0),
            "现金腿若不下单，账本按 %s 计息；不买逆回购则实际是 0 息。" % cash_leg,
            "这是研究产出，不是投资建议；实盘下单是 CEO 的直接权限，公司自动实盘仍是 CEO 唯一门。",
        ],
    }
    page["today_action"] = today_action(page)
    page["bets"] = bets_face()
    page["family_coherence"] = family_coherence()
    page["priced_faces"] = priced_faces(page["priced_bar"])
    page["cash_handshake"] = cash_handshake(cash_amt, page["cash_ladder"], today=today)
    page["carry_regime"] = carry_regime()
    page["leg_split"] = leg_split()
    page["concentration"] = concentration_face()
    page["sleeve_gate"] = sleeve_gate_face()
    page["sleeve_paths"] = sleeve_paths_face()
    page["exposure_timing"] = exposure_timing_face()
    page["cost_tape"] = cost_tape_face()
    page["vol_window"] = vol_window_face()
    page["vol_window_edge"] = vol_window_edge_face()
    page["lookahead"] = lookahead_face()
    page["causal_rebuild"] = causal_rebuild_face()
    page["research_arc"] = research_arc_face()
    page["underwater"] = underwater_face()
    page["gap"] = gap_face()
    page["band_ruler"] = band_ruler_face()
    page["window_label"] = page_window_label
    page["envelope"] = envelope_face()
    page["stress"] = build_stress(order, nav, feed.get("ticket_bar")) if with_stress else None
    return page, today


def render_md(p):
    L = []
    add = L.append
    add("# 今日 ETF 实盘单 —— %s" % p["generated_for_date"])
    add("")
    add("> 一页纸，全部数字从机器面直接抄来：单子来自可执行票、预期来自生产卡片、账面来自前向账本。没有新增判断。")
    add("")
    add("## 一句话")
    inv = p["book_amount_cny"]
    act = p.get("today_action") or {"mode": "unknown"}
    mode = act.get("mode")
    if mode == "hold":
        add("**今天不用动手。** 这套组合上一次定稿 **%s**，今天只是按新的收盘价（**%s**）把同一批权重重新算成份额——"
            "清单里份额和金额的变化是价格漂移，不是新指令。下一个动手日是 **%s**。"
            % (p["book_decided_at"], p["priced_bar"], p["next_rebalance_date"]))
        if act.get("cost_if_retraded_pct_per_year") is not None:
            # r1216: the rate this line is compared against is the book's FULL-window
            # number. It used to be the ticket's 683-bar return, i.e. the very number the
            # table above had just stopped calling a full-window figure.
            _wl_row = (p.get("window_label") or {})
            _wl_full = (((_wl_row.get("table_row") or {}).get("full") or {})
                        .get("cagr_pct") if _wl_row.get("status") == "ok" else None)
            _cmp = ("这本账全窗回测的 %.2f%%/年" % _wl_full) if _wl_full is not None \
                else "这本账回测的收益（全窗口径本期未发表）"
            add("")
            add("（照这份清单每天重下一遍的代价：单边 %s bp、进出两边、一年按 %d 个交易日、账内占比 %.1f%%，"
                "一年约 **%.1f%% 的资本**——比%s还高。所以「今天不动」不是懒惰，是这条纪律的一部分。）"
                % (p.get("cost_bp_per_side"), TRADING_DAYS_PER_YEAR, (p.get("k_now") or 0.0) * 100,
                   act["cost_if_retraded_pct_per_year"], _cmp))
    elif mode == "rebalance":
        add("**今天是换仓日。** 先卖掉不在清单里的，再按下面清单买：花 **¥%s**（占总资金 %.1f%%）买 %d 只 ETF，"
            "剩下的 **¥%s**（%.1f%%）放%s。"
            % (format(inv, ",.0f"), (p["k_now"] or 0) * 100, p["n_hold"] or len(p["order"]),
               format(p["cash_amount_cny"], ",.0f"), p["cash_weight"] * 100, p["cash_leg"]))
    elif mode == "open":
        add("**还没建仓的话，按这个下单：** 花 **¥%s**（占总资金 %.1f%%）买 %d 只 ETF，"
            "剩下的 **¥%s**（%.1f%%）放%s。已经在账上的不要照着重下一遍，下一次动手日是 **%s**。"
            % (format(inv, ",.0f"), (p["k_now"] or 0) * 100, p["n_hold"] or len(p["order"]),
               format(p["cash_amount_cny"], ",.0f"), p["cash_weight"] * 100, p["cash_leg"],
               p["next_rebalance_date"]))
    else:
        add("**今天是否要动手：无法判定**（缺 book_decided_at 或 priced_bar，不猜）。下面只有数值，不代表指令。")
    add("")
    add("## 下单清单%s" % ("（如果你今天才建仓）" if mode == "hold" else ""))
    add("")
    add("| 代码 | 类别 | 份（100 股/份） | 参考价 | 金额 |")
    add("|---|---|---|---|---|")
    for o in p["order"]:
        add("| %s | %s | %s | %s | ¥%s |"
            % (o["symbol"], o["class_zh"] or "", format(o["lots"] or 0, ","),
               o["price"], format(o["amount_cny"] or 0, ",.0f")))
    add("| — | **合计** | | | **¥%s** |" % format(p["book_amount_cny"], ",.0f"))
    add("")
    add("剩余现金 ¥%s 买 %s（或等价），不要留活期。" % (format(p["cash_amount_cny"], ",.0f"), p["cash_leg"]))
    add("")
    bf = p.get("bets") or {}
    if bf.get("status") == "ok" and bf.get("sentence"):
        add("## 这几只票到底有几个赌注")
        add("")
        add("**%s**" % bf["sentence"])
        add("")
        if bf.get("effective_bets") is not None and bf.get("nominal_bets") is not None:
            add("- 数票数 %d 只，数方向 **%.2f** 个（这两个数不一样的原因：相关性）。"
                % (round(float(bf["nominal_bets"])), float(bf["effective_bets"])))
        if bf.get("risk_split") is not None:
            add("- 风险不是按钱分的：按波动与相关拆到每只身上，等效 **%.2f** 个下注。"
                % float(bf["risk_split"]))
        if bf.get("evidence_cutoff"):
            add("- 计价截止 %s（读的是这张单自己的持仓权重，不是另抄一份书）。"
                % bf["evidence_cutoff"])
        add("")
    elif bf:
        add("- 这几只票到底有几个赌注：%s（缺面不读成一个赌注）"
            % (bf.get("note") or bf.get("detail") or "未产出"))
        add("")
    cy = p.get("cash_yield") or {}
    if cy.get("annual_cny") is not None:
        add("## 现金那一半在赚多少")
        add("")
        add("¥%s 放着不是 0 息：按 **%s** 最近收盘年化 **%.2f%%**（%s 的报价）算，一年约 **+¥%s**，"
            "每个交易日约 +¥%s。"
            % (format(p["cash_amount_cny"], ",.0f"), cy["leg"], cy["rate_pct"], cy["rate_date"],
               format(cy["annual_cny"], ",.0f"), format(cy["daily_cny"], ",.0f")))
        if cy.get("rate_20d_pct") is not None:
            add("")
            add("- 近 %d 个交易日这个利率平均 %.2f%%（一天期逆回购在季末/节前会飙高，平时就是个零钱利率），"
                "所以这笔钱是「现金不缩水」，不是收益来源。"
                % (cy["window"], cy["rate_20d_pct"]))
        add("- 不买逆回购、留在活期，这 ¥%s 就是没有的。" % format(cy["annual_cny"], ",.0f"))
        add("")
    cl = p.get("cash_ladder") or {}
    rows_l = cl.get("tenors") or []
    if rows_l and cl.get("cash_amount_cny"):
        add("## 现金腿要不要换长一点的期限")
        add("")
        add("逆回购报价是年化，所以「期限越长利率越高」不等于「赚得更多」——一天的腿季末会飙高，"
            "长的腿到期撞周末还会空转。按这些面板自己的日历逐条滚出来：")
        add("")
        add("| 代码 | 期限 | 今日报价 | 过去 1 年实盘年化 | 比一天期 | 一年滚几次 | 空转天/年 | 一年约赚 |")
        add("|---|---|---|---|---|---|---|---|")
        for r in rows_l:
            r1 = (r.get("realized") or {}).get("1") or {}
            edge = (r.get("edge_bp") or {}).get("1")
            add("| %s | %d 天 | %.2f%% | %s | %s | %s | %s | %s |"
                % (r["symbol"], r["tenor_days"], r["spot_pct"],
                   ("%.2f%%" % r1["realized_pct"]) if r1 else "—",
                   ("%+.1f bp" % edge) if edge is not None else "基线",
                   r.get("rolls_1y") if r.get("rolls_1y") is not None else "—",
                   r.get("idle_days_1y") if r.get("idle_days_1y") is not None else "—",
                   ("¥%s" % format(r["annual_cny_realized_1y"], ",.0f"))
                   if r.get("annual_cny_realized_1y") is not None else "—"))
        add("")
        rule = cl.get("rule") or {}
        if cl.get("verdict") == "KEEP-1D":
            add("**结论：不换，继续一天期。** 过门的条件是三条一起满足：比一天期一年多赚 %.0f bp 以上、"
                "1 年和 3 年都成立、空转不超过 %.0f%% 的日历日。没有一条腿过门——逐条见下表与下面三行。"
                % (rule.get("min_edge_bp") or 0.0,
                   (rule.get("max_idle_share") or 0.0) * 100.0))
            add("")
            for r in rows_l:
                if r["symbol"] == cl.get("base"):
                    continue
                e = r.get("edge_bp") or {}
                if not e:
                    continue
                add("- %s（%d 天）：1 年 %s -> 3 年 %s -> 5 年 %s，%d 个完整年里赢了 %s 年 —— %s。"
                    % (r["symbol"], r["tenor_days"],
                       "%+.1f bp" % float(e.get("1") or 0.0),
                       "%+.1f bp" % float(e.get("3") or 0.0),
                       "%+.1f bp" % float(e.get("5") or 0.0),
                       int(r.get("years_checked") or 0),
                       r.get("positive_years") if r.get("positive_years") is not None else "—",
                       {"REJECT": "不选", "ADOPT": "选它",
                        "NOT-ASSESSED": "历史不足"}.get(r.get("verdict"), r.get("verdict"))))
            add("- 一句话：差价随窗口拉长而缩水，锁久了换不来确定性，只换来「这笔钱这几天不能动」。")
            _horizon = [r for r in rows_l if int(r.get("tenor_days") or 0) >= 28]
            if _horizon:
                _h = _horizon[0]
                _he = (_h.get("edge_bp") or {}).get("1")
                add("- 这笔钱一个月才换一次仓，所以真正对得上闲置期的是 %s（%d 天，一年只滚 %s 次），"
                    "它实测 %s、空转 %s 天——同样没过门，不是「期限没选对」。"
                    % (_h["symbol"], _h["tenor_days"], _h.get("rolls_1y"),
                       ("%+.1f bp" % float(_he)) if _he is not None else "—",
                       _h.get("idle_days_1y")))
            add("")
            rolls_a = (cl.get("rolls") or {}).get(cl.get("base") or "GC001")
            rolls_b = (cl.get("rolls") or {}).get("GC007")
            if rolls_a and rolls_b:
                add("- 换 7 天期唯一真实的好处不是收益，是按键次数：一年 %d 次 -> %d 次。"
                    "代价是每忘记一天，那天的利息就没了，约 ¥%s。自己判断哪边更容易出错。"
                    % (rolls_a, rolls_b,
                       format(cl.get("forgotten_day_cny") or 0, ",.0f")))
        elif cl.get("verdict") == "ADOPT":
            add("**结论：换 %s。** %s。"
                % (cl.get("pick"), cl.get("reason")))
            add("")
            add("- 门槛 %.0f bp 是写死在代码里的（1 年和 3 年都要过），不是事后挑的。"
                % (rule.get("min_edge_bp") or 0.0))
        else:
            add("**结论：未判定。** %s" % (cl.get("reason") or "面板不足"))
        add("")
        add("- 这些都是「现金不缩水」的量级，不是收益来源；季末/节前的飙高是常态，别把它当稳定收益。")
        add("")
    hs = p.get("cash_handshake") or {}
    if hs:
        add("## 现金现在到底在哪（账实对账）")
        add("")
        st = hs.get("status")
        if st == "UNRECORDED":
            add("**这一页不知道钱在哪。** 上面的建议是「¥%s 全部放 %s」，但账户里实际下了多少，"
                "本仓库看不到——没人登记过。"
                % (format(p["cash_amount_cny"], ",.0f"), p.get("cash_leg")))
            add("")
            add("- 差多少不猜：如果这 ¥%s 还在活期，按 %s 报的 %.2f%%（%s）减去活期 %.2f%%，"
                "一年少赚约 **¥%s**（每个交易日约 ¥%s）。这是「全留活期」这个最坏情形的量级，不是实测。"
                % (format(p["cash_amount_cny"], ",.0f"), p.get("cash_leg"),
                   float(hs.get("repo_rate_pct") or 0.0), hs.get("repo_rate_date") or "—",
                   float(hs.get("demand_rate_pct") or 0.0),
                   format(hs.get("worst_case_annual_cny") or 0, ",.0f"),
                   format(round((hs.get("worst_case_annual_cny") or 0) / TRADING_DAYS_PER_YEAR), ",.0f")))
            add("- 怎么接上：把实际下单结果记一行到 `%s`（`recorded_by` 填你的名字、`asof` 填日期、"
                "`placements` 里每条 `instrument/amount_cny/rate_pct/rate_date`）——下一轮这页就会自动对账。"
                % hs.get("placement_file"))
            add("- %s。" % (hs.get("reason") or ""))
        elif st == "OVER-PLACED":
            add("**登记件与账本对不上。** %s" % (hs.get("reason") or ""))
            add("")
            add("- 已登记在仓 ¥%s vs 账面现金 ¥%s —— 先核哪个数是对的，别在这基础上加仓。"
                % (format(hs.get("placed_cny") or 0, ",.0f"),
                   format(p["cash_amount_cny"], ",.0f")))
        else:
            if st == "IN-PLACE":
                add("**对上了：** 登记的 ¥%s 全部在逆回购里，账面现金 ¥%s 没有缺口。"
                    % (format(hs.get("placed_cny") or 0, ",.0f"),
                       format(p["cash_amount_cny"], ",.0f")))
            elif st == "IDLE":
                add("**全在活期。** 登记件显示现金一分钱都没进逆回购——一年少赚约 **¥%s**。"
                    % format(hs.get("gap_annual_cny") or 0, ",.0f"))
            else:
                add("**只放了一部分：** 已登记在仓 ¥%s，还剩 ¥%s（%.1f%%）没进逆回购，"
                    "一年少赚约 **¥%s**（每个交易日约 ¥%s）。"
                    % (format(hs.get("placed_cny") or 0, ",.0f"),
                       format(hs.get("idle_cny") or 0, ",.0f"),
                       (hs.get("idle_share") or 0.0) * 100.0,
                       format(hs.get("gap_annual_cny") or 0, ",.0f"),
                       format(hs.get("gap_daily_cny") or 0, ",.0f")))
            add("")
            add("- 登记于 %s（%s 天前，登记人 %s）。"
                % (hs.get("asof") or "—",
                   hs.get("age_days") if hs.get("age_days") is not None else "—",
                   hs.get("recorded_by") or "—"))
            if hs.get("stale"):
                add("- **这条登记已经过期**（超过 %d 天），先重新记一次再看缺口。" % PLACEMENT_MAX_AGE_DAYS)
            add("- 缺口按 %s 收盘年化 %.2f%%（%s）减活期 %.2f%% 计；利率是市场价，缺口会随它漂。"
                % (p.get("cash_leg"), float(hs.get("repo_rate_pct") or 0.0),
                   hs.get("repo_rate_date") or "—", float(hs.get("demand_rate_pct") or 0.0)))
        add("")
    add("## 账面与节奏")
    add("")
    add("- 定价用的收盘日：**%s**（数据状态 %s，滞后 %s 个交易日）"
        % (p["priced_bar"], p["feed_status"], p["feed_lag_days"]))
    add("- 这套组合上一次定稿：**%s**" % p["book_decided_at"])
    add("- 下次换仓：**%s**（还有 %s 个交易日）" % (p["next_rebalance_date"], p["next_decision_bars"]))
    fwd = p["forward"]
    if fwd["nav"]:
        add("- 前向账本：起始 %s 净值 1.0000 -> %s 净值 **%.4f**（%+.2f%%），共 %d 个交易日"
            % (fwd["inception"], fwd["as_of"], fwd["nav"], fwd["since_inception_pct"], fwd["bars"]))
        add("  - 这只是起步，不能当业绩看。")
    else:
        add("- 前向账本：尚未起算")
    vsb = p.get("vs_basket")
    if vsb:
        add("- 同时期对照（**买入并持有 ETF 篮子**，%s）：到 **%s** 篮子净值 %.4f，本账 %.4f，"
            "领先 **%+.2f 个百分点**"
            % (vsb["basis"], vsb["bar"], vsb["basket_nav"], vsb["book_nav"], vsb["excess_pp"]))
        add("  - 篮子=黄金/纳指/沪深300/国债四只等权、与本账同一换仓日与成交口径；"
            "这个差只说明这几天谁更好，不是长期超额，日子还短。")
        _h = vsb.get("horizon") or {}
        _mde = _h.get("min_detectable_edge_pp") or {}
        _yrs = _h.get("years_for_80pct_power") or {}
        _cand = _h.get("candidate_sources") or {}
        if _mde:
            _pairs = []
            for _k, _v in _yrs.items():
                _e = (_cand.get(_k) or {}).get("edge_pp_per_year")
                _pairs.append("%s %.2fpp/年 -> %s 年" % (_k.split(" (")[0], _e or 0.0, _v))
            add("  - 这个差要多大才算数：以本账对篮子的日波动（年化 %s）计，"
                "**12 个月只能分辨 %.1f 个百分点/年以上的差**（6 个月 %.1f、3 年 %.1f）；"
                "本账发表过的超额要 %s 才能被证明——所以这行数字是健康检查，不是判词。"
                % ("8.46%", _mde.get("1y", 0), _mde.get("6m", 0), _mde.get("3y", 0),
                   "；".join(_pairs) or "（未读到研究文件）"))
    add("")
    add("## 该期待什么（回测口径，扣成本后）")
    add("")
    add("| 组合口径 | 全窗年化 | 夏普 | 最大回撤 | 2020-2023 | 2024 起 |")
    add("|---|---|---|---|---|---|")
    for label, row in p["backtest_band"].items():
        def g(seg, k):
            v = (row.get(seg) or {}).get(k)
            return "—" if v is None else ("%.2f%%" % v if k == "cagr_pct" else
                                          ("%.2f%%" % v if k == "maxdd_pct" else "%.2f" % v))
        add("| %s | %s | %s | %s | %s | %s |"
            % (label, g("full", "cagr_pct"), g("full", "sharpe"), g("full", "maxdd_pct"),
               g("is", "cagr_pct"), g("oos", "cagr_pct")))
    add("")
    add("三行是同一套选券信号，区别只在名数和杠杆规则：第一行是你要下的这份账（5 名 + beta 覆盖 + 8bp 成本）；另两行是生产卡片跑的对照口径。同一决策日，票是卡片的子集。")
    add("")
    _dash_n = sum(1 for _r in p["backtest_band"].values()
                  for _seg in ("full", "is", "oos")
                  if ((_r.get(_seg) or {}).get("cagr_pct")) is None)
    if _dash_n:
        add("\u2014\u2014 = \u8be5\u53e3\u5f84\u8fd9\u4e00\u683c\u6ca1\u6709\u53d1\u5e03\uff08%d \u683c\uff09\uff0c\u4e0d\u4f5c\u6570\uff1b\u6ca1\u6709\u53d1\u5e03\u4e0d\u7b49\u4e8e 0\uff0c\u4e5f\u4e0d\u7b49\u4e8e\u62ff\u522b\u7684\u7a97\u53e3\u9876\u4e0a\u3002"
            % _dash_n)
    # r1207/E324: the table just above is the research engine's reading. Put the timing
    # caveat where the number is read, not in a research file the reader never opens.
    for _lk_line in lookahead_block(p.get("lookahead") or {}):
        add(_lk_line)
    # r1224/E341: the reader is told to size off the declared arm; say whether that
    # gap was tested and what it cost to test it, where he reads the arm.
    for _cr_line in causal_rebuild_block(p.get("causal_rebuild") or {}):
        add(_cr_line)
    # r1226/E26: the rebuild answer is "no", so the reader's next question is whether anything
    # visible at the fill is worth the gap. Answer it where the rebuild answer is read.
    for _gp_line in gap_block(p.get("gap") or {}):
        add(_gp_line)
    # r1228: E25/E26/E27 each answered in their own section, and the three together were
    # never stated -- so the reader was invited to ask a fourth time. Say it where he reads
    # the answers, and say what the statement does NOT cover.
    for _ra_line in research_arc_block(p.get("research_arc") or {}):
        add(_ra_line)
    # r1213: the table's rows are not one ruler -- say which, where the table is read.
    for _br_line in band_ruler_block(p.get("band_ruler") or {}):
        add(_br_line)
    # r1216: the table's first row used to print the ticket's own 683-bar return under the
    # 全窗 header. Say, where the row is read, which window each of its two cells holds.
    for _wl_line in window_label_block(p.get("window_label") or {}):
        add(_wl_line)
    # r1211: a single CAGR is one path through one history. The envelope says how much of
    # it is the book and how much is which days you happened to live through -- and it
    # reads its numbers from the envelope's own reader, never from the JSON here.
    for _env_line in envelope_block(p.get("envelope") or {}):
        add(_env_line)
    if p.get("excess_pp") is not None and p.get("same_beta_benchmark") and p.get("ticket_book"):
        b = p["same_beta_benchmark"]
        bk = p["ticket_book"]
        add("")
        add("关键一句：**在同样的风险敞口下（beta 基准年化 %.2f%%、夏普 %.2f），这本账回测年化 %.2f%%、夏普 %.2f，多赚 %.2f 个百分点/年**——超额来自选券，不是来自加杠杆。"
            % (b["cagr"] * 100, b["sharpe"], bk["cagr"] * 100, bk["sharpe"], p["excess_pp"]))
    cr = p.get("carry_regime") or {}
    add("")
    add("## 这张表里的名数，是不是有实测撑腰")
    add("")
    fc = p.get("family_coherence") or {}
    if fc.get("verdict") == "ONE_WORLD":
        add("- **有。** %d 个宽度臂的判词全部算在同一张面板 `%s`（截至 %s）——卡片跑的那个名数是比出来的，"
            "不是配出来的。这张表之所以能对你说「该期待什么」，靠的就是这一句。"
            % (fc.get("arms") or 0, ((fc.get("panels") or [""])[0] or "?"),
               fc.get("evidence_cutoff")))
    elif fc.get("verdict"):
        add("- **没有。** 宽度臂家族已经收回了自己的判词（%s：%s）。所以上表里的名数只是配置，"
            "不是测出来的最优——读数照给，但别把它当「选过」的证据。"
            % (fc["verdict"], fc.get("detail") or "无细节"))
    else:
        add("- **不知道。** 读不到宽度臂家族的面（%s）。这是「没验」，不是「没问题」——"
            "上表的读数仍然有效，但它选的那个名数没有实测撑着。"
            % (fc.get("detail") or "家族面缺席"))
    add("")
    add("> 判词来源：`%s`。" % (fc.get("artifact") or "results/etf_book_phase_atlas_arms.json"))
    add("")
    add("## 这笔钱里有多少是「把现金借出去」挣的")
    add("")
    if not cr.get("available"):
        add("这一节没有数：`results/etf_book_return_regime.json` 不在盘上。跑 "
            "`python scripts/etf_book_return_regime.py run` 才会生成，不在这里现算。")
    else:
        rates = cr.get("cash_rates") or {}
        base = cr.get("base") or cr["rows"][-1]
        below = [r for r in cr["rows"] if r["beta"] < base["beta"]]
        above = [r for r in cr["rows"] if r["beta"] > base["beta"]]
        add("同一套引擎、同一批票、同样的 20 个交易日换仓和 8bp 成本，只把现金腿换成三种情形重算"
            "（历史真实报价 / 今天的报价固定不变 / 干脆 0 息）。风险和收益档位也一并列出，"
            "因为要不要多加风险是你可以自己选的事：")
        add("")
        add("| 风险档位 (beta) | 现金占比 | 回测年化（当时真实利率 %.2f%%） | 若一直只有今天的 %.2f%% | 若现金 0 息 | 最大回撤 |"
            % (rates.get("observed_mean_pct") or 0.0, rates.get("today_pct") or 0.0))
        add("|---|---|---|---|---|---|")
        for r in cr["rows"]:
            add("| %.2f%s | %.0f%% | %.2f%% | %.2f%% | %.2f%% | %s |"
                % (r["beta"], "（本单这一档）" if r is base else "",
                   (r["cash_share"] or 0.0) * 100, r["observed_pct"], r["flat_today_pct"],
                   r["zero_pct"],
                   "—" if r.get("maxdd_pct") is None else "%.2f%%" % r["maxdd_pct"]))
        add("")
        add("- **你现在这一档（beta %.2f）的 %.2f%% 里，%.2f 个百分点是把闲置现金借出去挣的**"
            "（占头条 %.0f%%）。就算逆回购掉到今天的 %.2f%% 不动，这本账还有 **%.2f%%**；"
            "就算现金一分利息都没有，也还有 **%.2f%%**——剩下来的钱来自选券，不是靠利息。"
            % (base["beta"], base["observed_pct"], base["carry_pp"],
               (100.0 * base["carry_pp"] / base["observed_pct"]) if base["observed_pct"] else 0.0,
               rates.get("today_pct") or 0.0, base["flat_today_pct"], base["zero_pct"]))
        if base.get("pp_per_100bp") is not None and cr.get("flags", {}).get("carry_positive"):
            add("- 利率每掉 100bp，这一档一年大约少 %.2f 个百分点（历史均值 %.2f%% -> 今天 %.2f%% 只差 %.0fbp，"
                "已经少赚约 %.2fpp）。这是个慢变量，不是每天看的东西。"
                % (base["pp_per_100bp"], rates.get("observed_mean_pct") or 0.0,
                   rates.get("today_pct") or 0.0,
                   100.0 * ((rates.get("observed_mean_pct") or 0.0) - (rates.get("today_pct") or 0.0)),
                   (base["observed_pct"] - base["flat_today_pct"])))
        if above:
            _hi = ("%.2f 档只剩 %.2fpp、%.2f 档只剩 %.2fpp"
                   % (above[0]["beta"], above[0]["carry_pp"],
                      above[-1]["beta"], above[-1]["carry_pp"])
                   if len(above) >= 2 else
                   "%.2f 档只剩 %.2fpp" % (above[0]["beta"], above[0]["carry_pp"]))
            add("- 档位越高、现金越少，这一项就越无关：%s。"
                "反过来，现金越多利息越要紧：%s 档有 %.0f%% 是现金，利息就撑起它头条的 %.0f%%。"
                "钱基本都投出去的时候，利不利率跟这本账没关系。"
                % (_hi,
                   "/".join("%.2f" % r["beta"] for r in below) or "更低",
                   100.0 * (below[-1].get("cash_share") or 0.0) if below else 0.0,
                   (100.0 * below[-1]["carry_pp"] / below[-1]["observed_pct"])
                   if below and below[-1]["observed_pct"] else 0.0))
        if above and above[0].get("maxdd_pct") is not None and base.get("maxdd_pct") is not None:
            add("- 想要更多钱就得扛更多波动，这个页不替你选：档位从 %.2f 提到 %.2f，"
                "回测年化 %.2f%% -> %.2f%%，代价是最大回撤 %.2f%% -> %.2f%%。"
                "今天这份单是按 %.2f 档开的。"
                % (base["beta"], above[0]["beta"], base["observed_pct"], above[0]["observed_pct"],
                   base["maxdd_pct"], above[0]["maxdd_pct"], base["beta"]))
        idy = cr.get("identity") or {}
        win = cr.get("window") or {}
        add("- 这段窗口是 **%s 起**（%s ~ %s），就是这张票自己在跑的那段，不是全史；"
            "全史口径看上一张表。%s"
            % (win.get("first") or "—", win.get("first") or "—", win.get("last") or "—",
               ("这一行是用你的票同一套引擎重算的（基准档 %.2f%% 与票面逐位对上）。"
                % (float(idy["published_cagr"]) * 100)) if idy.get("matched") else
               "重算结果与票面对不上，这张表不作为依据。"))
        add("")
        add("> 口径来源：`%s`（现金流按「前一根 bar 的报价 x 日历天数 / 365」计息，三种情形用同一约定；"
            "缺口日不计息并计数，不补默认值）。" % cr.get("source"))
    add("")
    ls = p.get("leg_split") or {}
    add("## 这笔钱是「一天里的哪一段」挣的")
    add("")
    if ls.get("status") != "ok":
        add("这一节没有数：拆解面%s（`%s`）。缺面就写「无法核验」，不拿零或「一致」顶上。"
            % ("未产出" if ls.get("status") == "absent" else "读不出",
               _rel(ls.get("artifact") or LEGS_JSON, ROOT).replace(os.sep, "/")))
        add("")
    else:
        pr_arm = ls["arms"].get("production") or {}
        bk = pr_arm.get("buckets_pp_per_year") or {}
        cw = (ls["arms"].get("control_ew") or {}).get("buckets_pp_per_year") or {}
        nf, npl = pr_arm.get("fill_bars") or 0, pr_arm.get("plain_bars") or 0
        drag = pr_arm.get("fill_bar_drag_pp_per_year") or 0.0
        carry = pr_arm.get("plain_carry_pp_per_year") or 0.0
        gross = (bk.get("overnight") or 0.0) + (bk.get("intraday") or 0.0)
        add("同一套引擎、同一批票、同样的换仓和成本，把上面那个回测年化按「钱是在哪一段挣的」拆成四桶——"
            "四桶按对数记账相加**精确等于**总额（不是大约等于），所以这一节不新增任何假设，"
            "只是把同一个数看仔细：")
        add("")
        add("| 桶 | 含义 | 一年几个百分点 |")
        add("|---|---|---|")
        add("| 安静 bar | %d 根「没有成交」的日子，持仓自己走 | %+.2f |" % (npl, bk.get("plain") or 0.0))
        add("| 隔夜 | 单子还没成交，旧持仓扛过收盘到开盘 | %+.2f |" % (bk.get("overnight") or 0.0))
        add("| 成交 bar 日内 | 新持仓在成交那天的开盘到收盘 | %+.2f |" % (bk.get("intraday") or 0.0))
        add("| 手续费 | 成交那一刻被收掉的 | %+.2f |" % (bk.get("toll") or 0.0))
        add("| **合计** | 与票面回测年化同一个词（对数口径） | **%+.2f** |" % (pr_arm.get("total_log_pp") or 0.0))
        add("")
        add("一句话：**%.2f 个百分点/年是在那 %d 根「什么都没发生」的 bar 上挣的；真正换手的那 %d 根 bar "
            "合计%s %.2f 个百分点**（手续费 + 开盘成交差）。"
            % (carry, npl, nf, "拖累" if drag < 0 else "贡献", abs(drag)))
        add("")
        add("- 这不是「少换手就多赚」的证据。把手续费当成 0，成交那一撮 bar 的毛腿**仍然是 %+.2f 个百分点**"
            "（隔夜 %+.2f + 日内 %+.2f）——问题不只在收费上，也在那一撮 bar 本身的方向上。"
            % (gross, bk.get("overnight") or 0.0, bk.get("intraday") or 0.0))
        if cw:
            add("- 同样这批票「平均买一遍」（等权、同样换仓同样成本）在安静 bar 上只有 **%+.2f**，"
                "这本账是 **%+.2f**——差的 %.2f 个百分点是选券给的，不是换手给的。"
                % (cw.get("plain") or 0.0, bk.get("plain") or 0.0,
                   (bk.get("plain") or 0.0) - (cw.get("plain") or 0.0)))
        add("")
        add("> 拆解面：`%s`（计价截止 %s；执行约定：%s；三臂=这本账 / 裸书 / 等权控制）。"
            % (_rel(ls.get("artifact") or LEGS_JSON, ROOT).replace(os.sep, "/"),
               ls.get("evidence_cutoff") or "—", ls.get("execution") or "—"))
        add("")
    cc = p.get("concentration") or {}
    add("## 这个年化是「谁」赚来的")
    add("")
    if cc.get("status") != "ok":
        add("这一节没有数：浓度面%s（`%s`）。缺面就写「无法核验」，不拿零或「分散」顶上。"
            % ("未产出" if cc.get("status") == "absent" else "读不出",
               _rel(cc.get("artifact") or CONC_JSON, ROOT).replace(os.sep, "/"))
            )
        add("")
    else:
        bl = cc.get("baseline") or {}
        top = cc.get("top") or []
        lk = cc.get("top_k_out") or {}
        veh = cc.get("sleeve") or {}
        add("上面那个回测年化（**%+.2f%%**）是把 %d 只票每天各自的贡献加起来的；"
            "把它拆开看，钱并不是均匀来自每一只："
            % (100 * (bl.get("cagr") or 0.0), cc.get("distinct_names") or 0))
        add("")
        add("| 读法 | 读数 |")
        add("|---|---|")
        add("| 第一名占毛收益 | **%.1f%%**（%s） |"
            % (100 * ((top[0].get("share") if top else 0) or 0),
               (top[0].get("name") if top else "—")))
        add("| 前三名合计 | **%.1f%%** |" % (100 * (cc.get("top3_share") or 0)))
        add("| 拥有正贡献的票 | %d 只（占 1%% 以上的 %d 只，负贡献 %d 只） |"
            % (cc.get("distinct_names") or 0, cc.get("names_above_1pct") or 0,
               cc.get("names_negative") or 0))
        _v = str(cc.get("verdict") or "—")
        # a verdict that carries a pipe would split its own table cell (markdown)
        add("| 集中度 HHI | %.4f（%s） |"
            % (cc.get("hhi") or 0.0, _v.replace("|", " · ")))
        add("")
        if lk.get("delta_cagr_pp") is not None:
            s = lk.get("stats") or {}
            f = s.get("full") or {}
            add("- 删掉前三名重跑：年化 **%+.2fpp**（→ %.2f%%，夏普 %.2f，回撤 %+.1f%%）——"
                "前面的数还是不是这套打法的数，取决于这一行。"
                % (lk["delta_cagr_pp"], 100 * (f.get("cagr") or 0.0),
                   f.get("sharpe") or 0.0, 100 * (f.get("maxdd") or 0.0)))
        if veh.get("delta_cagr_pp") is not None:
            s = veh.get("stats") or {}
            f = s.get("full") or {}
            base_dd = 100 * ((bl.get("maxdd") or 0.0))
            add("- 删掉整条 **%s** 袖（%d 只）重跑：年化 **%+.2fpp**（→ %.2f%%，夏普 %.2f），"
                "回撤从 %.1f%% 变成 **%+.1f%%**——赚钱的那条腿同时是抗回撤的那条腿。"
                % ({"commodity": "商品", "equity": "权益", "bond": "债",
                    "cash": "货币", "convertible": "转债"}.get(veh.get("class"),
                                                              veh.get("class") or "—"),
                   veh.get("symbols_removed") or 0,
                   veh["delta_cagr_pp"], 100 * (f.get("cagr") or 0.0),
                   f.get("sharpe") or 0.0, base_dd, 100 * (f.get("maxdd") or 0.0)))
        add("")
        add("> 浓度面：`%s`（计价截止 %s）。逐票贡献必须与引擎净值逐位相同才出件；"
            "删票是把整只票从票池里拿掉重跑，不是把权重调大调小。"
            % (_rel(cc.get("artifact") or CONC_JSON, ROOT).replace(os.sep, "/"),
               cc.get("evidence_cutoff") or "—"))
        add("")
    sg = p.get("sleeve_gate") or {}
    add("## 要不要给商品袖单独立个风险门")
    add("")
    if sg.get("status") != "ok":
        add("这一节没有数：袖门面%s（`%s`）。缺面就写「无法核验」，"
            "绝不默认读成「不需要门」。"
            % ("未产出" if sg.get("status") == "absent" else "读不出",
               _rel(sg.get("artifact") or SLEEVE_JSON, ROOT).replace(os.sep, "/")))
        add("")
    else:
        rows = sg.get("gates") or []
        crit = sg.get("criteria") or {}
        closest = sg.get("closest") or {}
        decisions = (sg.get("book") or {}).get("decisions") or 0
        add("上一节说了：赚钱的那条腿就是抗回撤的那条腿。那要不要给这条袖单独立个门"
            "（趋势破了就撤、波动太高就撤、回撤太深就撤）？同一套引擎、同一批票、同样的换手与成本，"
            "把三种门各跑一遍，并且每种门都配一个**同样关掉次数的安慰剂**——"
            "因为「固定比例地不持有」本身就会改变风险，只有赢过自己安慰剂的那种才算信号。")
        add("")
        add("| 门 | 关掉袖的决策数 | 占决策网格 | 年化变化 | 回撤变化 | 判词 |")
        add("|---|---|---|---|---|---|")
        for r in rows:
            add("| %s | %s/%d | %.1f%% | %+.2fpp | %+.2fpp | %s |"
                % ({"trend": "趋势（跌破 200 日线）", "vol": "波动（波动率过高）",
                    "drawdown": "回撤（从高点回落过深）"}.get(r.get("name"), r.get("name")),
                   r.get("off_decisions") or 0, decisions,
                   100 * (r.get("off_share") or 0),
                   r.get("delta_cagr_pp") or 0.0, r.get("delta_maxdd_pp") or 0.0,
                   str(r.get("verdict") or "—").replace("|", " · ")))
        add("")
        add("回撤一列是正数=比不加门时的回撤更浅。结论：**%s**"
            % str(sg.get("verdict") or "—").replace("|", " · "))
        add("")
        if closest.get("dd_gain_pp") is not None and (closest.get("dd_gain_pp") or 0) > 0:
            add("- 最接近的一条是 **%s门**：回撤只改善 **%+.2fpp**，没到事先冻结的 **%.1fpp** 门槛，"
                "但它赢了自己的安慰剂 **%+.2fpp**——所以它是「将来拿新数据再测」的候选，"
                "**不是**把门槛降下来让它过（那样就是跑到达标为止，本账不许）。"
                % ({"trend": "趋势", "vol": "波动", "drawdown": "回撤"}.get(closest.get("name")),
                   closest.get("dd_gain_pp") or 0.0, crit.get("min_dd_gain_pp") or 0.0,
                   closest.get("placebo_dd_edge_pp") or 0.0))
        # the rest of the verdict, read off each gate's own classification (never asserted
        # in prose): a gate can fail because it gains nothing, or because it loses to its
        # own untimed placebo -- and the same gate can be both at once
        no_gain = [r for r in rows if r.get("why") == "no_gain_vs_baseline"]
        lost = [r for r in rows if r.get("why") == "no_gain_vs_baseline"
                and not r.get("beats_placebo")]
        if no_gain:
            _zh = {"trend": "趋势", "vol": "波动", "drawdown": "回撤"}
            add("- 有 **%d 条**门（%s）连基线都没超过：按信号把这条袖关掉，回撤并不比一直拿着更浅。"
                % (len(no_gain), "、".join(_zh.get(r.get("name"), r.get("name"))
                                          for r in no_gain)))
        if lost:
            add("- 其中 **%s** 连自己的安慰剂也赢不了（换成同样次数的随机不持有更好）——"
                "它们看起来像「避险」，实际只是**少拿了这条袖**。"
                % "、".join({"trend": "趋势", "vol": "波动", "drawdown": "回撤"}.get(
                    r.get("name"), r.get("name")) for r in lost))
        add("- 也就是说：这条袖的风险已经在**书级**的波动目标里（整本账只降不升杠杆）管住了，"
            "再在袖上加一层门不会更安全，只会更常空仓。")
        add("")
        add("> 袖门面：`%s`（计价截止 %s）。每个臂都对照自己的同剂量安慰剂；"
            "判据（回撤门槛 %.1fpp、年化至少保留 %.0f%%）写在跑之前。"
            % (_rel(sg.get("artifact") or SLEEVE_JSON, ROOT).replace(os.sep, "/"),
               sg.get("evidence_cutoff") or "—",
               crit.get("min_dd_gain_pp") or 0.0, 100 * (crit.get("cagr_keep") or 0.0)))
        add("")
    sp = p.get("sleeve_paths") or {}
    gs = sp.get("gates_summary") or {}
    add("### 那个「拿新网格再测」的候选，测完了")
    add("")
    if sp.get("status") != "ok" or sp.get("stale_vs_sleeve_gate"):
        add("这一节没有数：网格重测面%s（`%s`）。"
            "缺面或落后于上面那张表就写「无法核验」，绝不默认读成「重测过了、没问题」。"
            % ("早于上面的袖门面" if sp.get("status") == "ok"
               else ("未产出" if sp.get("status") == "absent" else "读不出"),
               _rel(sp.get("artifact") or PATHS_JSON, ROOT).replace(os.sep, "/")))
        add("")
    else:
        rows_sp = [r for r in (sp.get("rows") or []) if r.get("placebo_offset") == 0]
        _zh = {"trend": "趋势", "vol": "波动", "drawdown": "回撤"}
        add("- 把决策网格整体往后挪 **0/5/10/15/20 根 bar**，得到 **%d 个网格**；"
            "每个网格再配 **%d 个不同起点的同剂量安慰剂**，共 **%d 条路径**。"
            "同一条门、同一道事先冻结的门槛、同一批票、同样的成本——变的只有「哪天做决定」。"
            % (gs.get("grids") or 0,
               (len(sp.get("rows") or []) // max(gs.get("grids") or 1, 1) or 0),
               gs.get("paths") or 0))
        add("")
        add("| 网格起点 | 关掉袖的决策数 | 回撤改善 | 年化保留 | 判词 |")
        add("|---|---|---|---|---|")
        for r in rows_sp:
            add("| %s | %s/%s | %+.2fpp | %.3f | %s |"
                % (r.get("start") or r.get("phase"),
                   r.get("off_decisions") if r.get("off_decisions") is not None else "无",
                   r.get("decisions") if r.get("decisions") is not None else "无",
                   r.get("dd_gain_pp") or 0.0, r.get("cagr_keep") or 0.0,
                   "过" if r.get("verdict") == "PASS" else "不过"))
        add("")
        add("- 回撤改善在 **%+.2f ~ %+.2fpp** 之间，**%d/%d** 条路径赢了自己的安慰剂，"
            "**%d/%d** 条够到 %.1fpp 的回撤门槛、**%d/%d** 条守住了 %.0f%% 的年化。"
            "三道条件要同时满足，全过的有 **%d 条**。"
            % (gs.get("dd_gain_min_pp") or 0.0, gs.get("dd_gain_max_pp") or 0.0,
               gs.get("beats_placebo") or 0, gs.get("paths") or 0,
               gs.get("clears_bar") or 0, gs.get("paths") or 0,
               (sp.get("criteria") or {}).get("min_dd_gain_pp") or 0.0,
               gs.get("keeps_cagr") or 0, gs.get("paths") or 0,
               100 * ((sp.get("criteria") or {}).get("cagr_keep") or 0.0),
               gs.get("passed") or 0))
        add("")
        add("- 结论：**%s**。这就是那句话的下文——候选真的拿去重测了，"
            "而不是把门槛降到它刚好能过（跑到达标为止是账上禁止的动作）。"
            % str(sp.get("verdict") or "无法核验").replace("|", " · "))
        add("")
        add("> 网格重测面：`%s`（计算截止 %s）。"
            % (_rel(sp.get("artifact") or PATHS_JSON, ROOT).replace(os.sep, "/"),
               sp.get("evidence_cutoff") or "无"))
        add("")
    et = p.get("exposure_timing") or {}
    add("## 仓位不是一直满的：这是本事，还是只是把书变小了")
    add("")
    if et.get("status") != "ok":
        add("这一节没有数：仓位面%s（`%s`）。"
            "缺面、读不出、或身份门没过（生产臂复现不出引擎自己的净值）就写「无法核验」，"
            "绝不默认读成「择时有效」。"
            % ({"absent": "未产出", "no_identity": "未通过身份门"}.get(et.get("status"), "读不出"),
               _rel(et.get("artifact") or EXPOSURE_JSON, ROOT).replace(os.sep, "/")))
        add("")
    else:
        arms_e = et.get("arms") or {}
        v_e = et.get("verdict") or {}
        pl_e = et.get("placebo") or {}
        ex_e = et.get("exposure") or {}
        prod_e = arms_e.get("production") or {}
        full_e = arms_e.get("full") or {}
        const_e = arms_e.get("constant") or {}
        _lab = {"production": "生产（8% 波动率目标，引擎自己的缩放）",
                "full": "满仓（暴露恒 1.0）",
                "constant": "对照（按本书自己的平均暴露 %.0f%%，天天持平）"
                % (100 * (const_e.get("mean_exposure") or 0.0))}
        add("这本书并不是一直满仓：**%.1f%%** 的决策日把仓位缩了下去，平均暴露 **%.1f%%**。"
            "问题不是「缩仓好不好」，而是「缩仓省下来的风险，是不是靠看准了时间换来的」——"
            "如果只是把书按比例变小，那么收益少、波动也小，这篇纸面上看起来一样漂亮，但一分本事都没有。"
            % (100 * (ex_e.get("delevered_decision_share") or 0.0),
               100 * (ex_e.get("mean_engine_scale") or 0.0)))
        add("")
        add("| 臂 | 年化 | 夏普 | 最大回撤 | 平均暴露 |")
        add("|---|---|---|---|---|")
        for k in ("production", "full", "constant"):
            a_e = arms_e.get(k) or {}
            add("| %s | %.2f%% | %.3f | %.2f%% | %.1f%% |"
                % (_lab[k], 100 * (a_e.get("cagr") or 0.0), a_e.get("sharpe") or 0.0,
                   100 * (a_e.get("maxdd") or 0.0),
                   100 * (a_e.get("mean_exposure") or 0.0)))
        add("")
        _st = str(v_e.get("state") or "—")
        _zh_st = {"AVERAGE_EXPOSURE_ONLY": "**AVERAGE_EXPOSURE_ONLY**——缩仓不是本事，是少承担风险",
                  "TIMING_ADDS": "**TIMING_ADDS**——同样的平均仓位下，这条缩仓路径确实跑赢了随机的",
                  "TIMING_SUBTRACTS": "**TIMING_SUBTRACTS**——同样的平均仓位下，这条缩仓路径还不如随机的",
                  "INCOMPLETE": "**INCOMPLETE**——臂不齐，判不了"}.get(_st, _st)
        add("- 生产 **%.2f%%** vs 对照 **%.2f%%**：在同样的平均仓位下，这条缩仓路径值 **%+.2fpp/年**，"
            "落在 %d 条安慰剂路径的 **%+.2f ~ %+.2fpp** 区间里 → 判词 %s。"
            "（安慰剂＝把引擎自己的缩放序列在它自己的决策日之间打乱：暴露分布一模一样，"
            "「哪天缩、哪天放」的信息被清零。）"
            % (100 * (prod_e.get("cagr") or 0.0), 100 * (const_e.get("cagr") or 0.0),
               v_e.get("timing_pp") or 0.0, pl_e.get("n") or 0,
               v_e.get("placebo_p05_pp") or 0.0, v_e.get("placebo_p95_pp") or 0.0, _zh_st))
        add("- 对照 vs 满仓：**%+.2fpp/年**——这才是这条覆盖律真正买到的东西："
            "一本更小的书、更浅的回撤（满仓 %.2f%% → 对照 %.2f%%），少赚的记在收益上。"
            % (v_e.get("de_risking_pp") or 0.0, 100 * (full_e.get("maxdd") or 0.0),
               100 * (const_e.get("maxdd") or 0.0)))
        add("- 读法：要判断「缩仓有没有本事」，唯一诚实的对照是**同一本书、同样的平均仓位**，"
            "而不是和满仓比——和满仓比，任何减仓都会「看起来减少了回撤」。")
        add("")
        add("> 仓位面：`%s`（计价截止 %s，%s bars / %s 决策；身份门与引擎净值误差 %s）。"
            % (_rel(et.get("artifact") or EXPOSURE_JSON, ROOT).replace(os.sep, "/"),
               et.get("evidence_cutoff") or "—", et.get("bars") or "—",
               et.get("decisions") or "—",
               "%.1e" % ((et.get("identity") or {}).get("gap") or 0.0)))
        add("")
    ct = p.get("cost_tape") or {}
    add("## 「每一分钱按 10bp 扣」——这个假设是该收紧，还是本来就更保守")
    add("")
    if ct.get("status") != "ok":
        add("这一节没有数：盘口面%s（`%s`）。"
            "缺面、读不出、或控制臂没能复现卡片自己的年化（那就不是同一本书）就写「无法核验」，"
            "绝不默认读成「卡片是保守的」。"
            % ({"absent": "未产出", "no_control": "未通过控制臂"}.get(ct.get("status"), "读不出"),
               _rel(ct.get("artifact") or COST_JSON, ROOT).replace(os.sep, "/")))
        add("")
    else:
        arms_c = ct.get("arms") or {}
        tp_c = ct.get("tape") or {}
        _lab_c = {"assumed_10bp": "卡片假设（每边 %.0f bp）" % (ct.get("assumed_bp") or 0.0),
                  "measured": "盘口实测（按本书自己的换手加权）",
                  "upper_p75": "悲观臂（每只票都按自己的 75 分位）"}
        add("这本书的每一次买卖都按每边 **%.0f bp** 扣钱——**所有已发布的年化都踩在这个数上**。"
            "如果真实价差是它的三倍，整面结论都该重写，所以这个假设本身就是个被测量的对象："
            "拿每只票自己的日高低价去估有效价差（滚动 20 日中位，**滞后一根 bar**，"
            "决策看不到次日），再按本书自己的换手加权，得到实测单边成本 **%.1f bp**——"
            "是假设的 **%.0f%%**。"
            % (ct.get("assumed_bp") or 0.0, ct.get("measured_bp") or 0.0,
               100 * (ct.get("ratio_vs_assumed") or 0.0)))
        add("")
        add("| 成本口径 | 年化 | 夏普 | 最大回撤 |")
        add("|---|---|---|---|")
        for _k in ("assumed_10bp", "measured", "upper_p75"):
            a_c = arms_c.get(_k) or {}
            add("| %s | %.2f%% | %.3f | %.2f%% |"
                % (_lab_c[_k], 100 * (a_c.get("cagr") or 0.0), a_c.get("sharpe") or 0.0,
                   100 * (a_c.get("maxdd") or 0.0)))
        add("")
        add("- 判词：**%s**——卡片收的比盘口贵，所以纸上那个年化是**偏保守**的；"
            "换成实测成本同一台引擎是 **%.2f%% / 夏普 %.2f**，"
            "就算每只票都按自己历史上最宽的 75 分位算也还有 **%.2f%% / %.2f**。"
            % (" ".join(str(ct.get("verdict") or "—").replace("|", "·").split()),
               100 * ((arms_c.get("measured") or {}).get("cagr") or 0.0),
               (arms_c.get("measured") or {}).get("sharpe") or 0.0,
               100 * ((arms_c.get("upper_p75") or {}).get("cagr") or 0.0),
               (arms_c.get("upper_p75") or {}).get("sharpe") or 0.0))
        add("- **控制臂**：同一台引擎按卡片的 10bp 重跑必须复现卡片自己的年化（%.2f%% vs %.2f%%，"
            "容差 %.1fpp，%s）——所以这是测量，不是断言；若复现不出，这一节整段写「无法核验」。"
            % (100 * ((ct.get("control") or {}).get("engine_cagr") or 0.0),
               100 * ((ct.get("control") or {}).get("published_cagr") or 0.0),
               (ct.get("control") or {}).get("tolerance_pp") or 0.0,
               "通过" if (ct.get("control") or {}).get("passes") else "未通过"))
        add("- 盘口：本书真正交易过的 **%s** 只票有估值，中位相对价差 **%.1f bp**，"
            "最宽的一只 %s 是 **%.1f bp**；%s/%s 个决策日全部可定价。"
            % (tp_c.get("n_traded_names") or "—", tp_c.get("median_name_p50_bp") or 0.0,
               ((tp_c.get("widest_traded") or [{}])[0]).get("symbol") or "—",
               ((tp_c.get("widest_traded") or [{}])[0]).get("p50_bp") or 0.0,
               (ct.get("decisions") or {}).get("priced") or "—",
               ((ct.get("decisions") or {}).get("priced") or 0)
               + ((ct.get("decisions") or {}).get("dropped_low_coverage") or 0)))
        add("- 诚实缺口：这里估的是**半边价差**，冲击成本没计；也就是说这张盘口是成本的地板不是天花板。")
        add("")
        add("> 盘口面：`%s`（计价截止 %s）。"
            % (_rel(ct.get("artifact") or COST_JSON, ROOT).replace(os.sep, "/"),
               ct.get("evidence_cutoff") or "—"))
        add("")
    vw = p.get("vol_window") or {}
    add("## 8% 那条闸用的 60 日窗口——是这本书的一部分，还是恰好量在一条决策日历上？")
    add("")
    if vw.get("status") != "ok":
        add("这一页没有拿到窗口面的可用读数（`%s`，状态 `%s`）：%s。"
            "按默认口径读——窗口被扫过，但扫在**一条**决策日历上，所以「60 日是稳的」在这里无法核验。"
            % (_rel(vw.get("artifact") or VOLWIN_JSON, ROOT).replace(os.sep, "/"),
               vw.get("status") or "unknown", vw.get("detail") or "判决不能从自己的行重算"))
        add("")
    else:
        v = vw.get("verdict") or {}
        rows = vw.get("phase_rows") or []
        st_v = v.get("state")
        best = v.get("best_window")
        picks = sorted({r.get("phase") for r in rows})
        _zh_v = {"ADOPT_WINDOW": "**有窗口赢过在册值**（不是靠一条日历）",
                 "PHASE_DEPENDENT": "**相位决定**（换一条日历结论会变）",
                 "WINDOW_INERT": "**这条轴不承重**（在册值安全）",
                 "REJECT_WINDOW_CHANGE": "**在册值站得住**（没有窗口赢）",
                 "INCOMPLETE": "**读数不完整**，不判"}.get(st_v, "**%s**" % st_v)
        add("这本书每次调仓都按最近 **60 个交易日**的实测波动决定敢用多少钱。这个 60 从没在"
            "**多条日历**上验过：此前那次窗口×目标的扫描，所有格子都跑在同一条 20 日调仓日"
            "网格上——就是「一个相位上的冠军」那个老毛病（E321）。这一节把它放到 %d 条相位上重跑。"
            % len(picks))
        add("")
        add("- 判决：%s。在册 60 日 vs 最好窗口 **%s 日**：后者在 **%d/%d** 条相位上把这 +%.2f 夏普"
            "的门槛真赢下来，样本外不差于在册的有 **%d/%d** 条。"
            % (_zh_v, best if best is not None else "—",
               v.get("best_phases_earned") or 0, v.get("phases_tested") or 0,
               (vw.get("criteria") or {}).get("sharpe_gain") or 0.0,
               v.get("best_phases_oos_not_worse") or 0, v.get("phases_tested") or 0))
        pv_v = vw.get("paired") or {}
        pr_v = pv_v.get("rows") or []
        pst_v = (pv_v.get("verdict") or {}).get("state")
        if pr_v:
            add("- 配对裁决（把两本书在同一相位上的收益差自己做块自助，1,000 次，块长=一个调仓周期）："
                "**%s**。逐相位：%s。"
                % (pst_v or "—",
                   "；".join("%s → %+.2fpp [%+.2f, %+.2f]" %
                            ((r.get("phase") if isinstance(r.get("phase"), str)
                              else "相位%s" % r.get("phase")),
                             r.get("mean_pp") or 0.0,
                             (r.get("ci_p05_p95_pp") or [0, 0])[0],
                             (r.get("ci_p05_p95_pp") or [0, 0])[1])
                            for r in pr_v if r.get("status") == "ok")))
            add("")
        _of_v = vw.get("older_face") or {}
        if _of_v.get("status") == "ok":
            add("- 同一根轴上还有一张早先的面（读它、不重算）：窗口 %s 日 vs %s 日对照，"
                "中位 **%+.2fpp**、中位夏普 %+.2f、%d/%d 相位向上，它自己的噪声底 **%.2fpp**"
                "（=对照自己在相位之间的跨度）→ 判它 **within noise**。两张面方向一致、"
                "只有「尺子」不同：那张把配对效应比给了跨组跨度，这张把配对效应比给了配对的带。"
                % (_of_v.get("w_test"), _of_v.get("control_window"),
                   _of_v.get("median_delta_pp") or 0.0, _of_v.get("median_delta_sharpe") or 0.0,
                   int(round(100 * (_of_v.get("share_up") or 0.0))), 4,
                   _of_v.get("noise_pp") or 0.0))
            add("")
        if st_v == "ADOPT_WINDOW":
            add("- 也就是说：**出货的 60 日不是任何一条日历上的最优**，而且梯度朝更短的窗口单调"
                "（越短越稳）。但最好的那一格正好落在网格边缘，所以本页**只把选择定价，不改出货配置**——"
                "往外推是下一张冻结面的活，不是这一格能替它答的。")
        elif st_v == "WINDOW_INERT":
            add("- 也就是说：窗口换一换，风险调整后的差别在噪声带里——这条轴不承重，在册的 60 日"
                "放心用，别把它当精心调过的参数。")
        elif st_v == "REJECT_WINDOW_CHANGE":
            add("- 也就是说：没有哪条窗口能真赢下在册的 60 日——这个数站得住，不用动。")
        elif st_v == "PHASE_DEPENDENT":
            add("- 也就是说：换个调仓起点，答案会变——所以在册值**既不该被夸成最优，也不该被换掉**，"
                "这属于相位噪声，不是可交易的改进。")
        add("")
        add("| 相位（调仓起点） | 在册 60 日夏普 | 最好窗口 %s 日夏普 | 差 |"
            % (best if best is not None else "—"))
        add("|---|---|---|---|")
        _by = {(r.get("phase"), r.get("window")): r for r in rows}
        for _i in picks:
            _a = _by.get((_i, 60)) or {}
            _b = _by.get((_i, best)) or {}
            _sa, _sb = _a.get("sharpe"), _b.get("sharpe")
            add("| %s | %s | %s | %s |"
                % ((_a.get("phase_start") or _i),
                   "—" if _sa is None else "%.3f" % _sa,
                   "—" if _sb is None else "%.3f" % _sb,
                   "—" if (_sa is None or _sb is None) else "%+.3f" % (_sb - _sa)))
        add("")
        add("- 别忘了这一面同时说明的代价：更短的估计反应更快，也**多拿**了这本书"
            "（平均仓位与交付波动都往上走）——所以夏普那一列才是「不只是多冒风险」的部分。")
        add("")
        add("> 窗口面：`%s` ｜ 定价截止 %s ｜ %s 条相位 × %s 个窗口 ｜ 在册窗口在出货跨度上"
            "复现生产卡 = **%s**"
            % (_rel(vw.get("artifact") or VOLWIN_JSON, ROOT).replace(os.sep, "/"),
               vw.get("evidence_cutoff") or "—",
               v.get("phases_tested") or "—",
               len({r.get("window") for r in rows}) or "—",
               "PASS" if vw.get("identity_all_pass") else "FAIL"))
        add("")
    L.extend(vol_window_edge_block(p.get("vol_window_edge") or {}))
    add("## 换成年内能赚多少钱（按本单资金 ¥%s）" % format(p["money_cny"]["capital_cny"], ",.0f"))
    add("")
    add("同一批数字再换一把尺子，只做单位换算，不叠加任何新假设：")
    add("")
    add("| 项目 | 一年多少钱 | 怎么来的 |")
    add("|---|---|---|")
    mc = p["money_cny"]

    def y(v):
        return "—" if v is None else ("%s¥%s" % ("+" if v > 0 else "-", format(abs(v), ",.0f")))

    add("| 这本账回测期望 | %s | 年化 %s%% × 资金 |"
        % (y(mc["expected_annual_cny"]), "%.2f" % (p["ticket_book"]["cagr"] * 100) if p.get("ticket_book") else "—"))
    add("| 同风险基准（beta 覆盖） | %s | 基准年化 %s%% × 资金 |"
        % (y(mc["benchmark_annual_cny"]),
           "%.2f" % (p["same_beta_benchmark"]["cagr"] * 100) if p.get("same_beta_benchmark") else "—"))
    add("| **超额部分** | **%s** | 多赚 %.2f 个百分点 × 资金 |"
        % (y(mc["excess_annual_cny"]), p["excess_pp"] or 0.0))
    add("| 一次最坏回撤要亏 | %s | 最大回撤 %s%% × 资金 |"
        % (y(mc["worst_drawdown_cny"]),
           "%.2f" % (p["ticket_book"]["maxdd"] * 100) if p.get("ticket_book") else "—"))
    add("")
    add("读法：一年赚多少是回测期望，不是承诺；最坏回撤那一行才是你要能扛住的数。")
    add("")
    st = p.get("stress") or {}
    worst = st.get("worst") or {}
    if worst.get("1d") or worst.get("5d") or worst.get("20d"):
        add("## 最坏的日子长什么样（同一批票，整段历史）")
        add("")
        add("把今天这 %d 只票的权重重放回 %s~%s 的整段面板（现金 0 息），看最坏的连续几个交易日："
            % (len(p["order"]), st.get("first"), st.get("last")))
        add("")
        add("| 窗口 | 最差涨跌 | 折成钱 | 结束于 |")
        add("|---|---|---|---|")
        for n in STRESS_WINDOWS:
            row = worst.get("%dd" % n)
            if not row:
                add("| %d 个交易日 | — | — | — |" % n)
                continue
            add("| %d 个交易日 | %+.2f%% | %s | %s |"
                % (n, row["pct"], "—" if row.get("cny") is None else
                   ("%s¥%s" % ("+" if row["cny"] > 0 else "-", format(abs(row["cny"]), ",.0f"))),
                   row.get("end_date") or "—"))
        add("")
        add("读法：这是「同一批票、同样权重、最倒霉的一段」值多少钱，不是预测，也不是这本账实际走过的路"
            "（实际路径的回撤见上一张表的最大回撤列）。")
        add("")
        cont = st.get("contamination") or {}
        if cont.get("sentence"):
            add("**这张表最差的一天，是行情还是报价？** " + cont["sentence"])
            add("")
            raw_c, clean_c = cont.get("raw_worst") or {}, cont.get("clean_worst") or {}
            if clean_c.get("1d"):
                add("| 同一批票、同一权重 | 最差 1 日 | 最差 5 日 | 最差 20 日 |")
                add("|---|---|---|---|")
                for label, block in (("现在的面板", raw_c), ("把翻转压平后", clean_c)):
                    cells = []
                    for n in STRESS_WINDOWS:
                        r = block.get("%dd" % n)
                        cells.append("—" if not r else "%+.2f%%（%s）" % (r["pct"], r.get("end_date")))
                    add("| %s | %s |" % (label, " | ".join(cells)))
                add("")
    # r1231: the reader now knows how much and how deep; it never knew how long. Print the
    # wait where he reads the worst case, and print the sample boundary with it -- a
    # 3-year "no losses" is this sample's property, not a promise.
    for _uw_line in underwater_block(p.get("underwater") or {}):
        add(_uw_line)
    add("## 必须记住的四条")
    add("")
    for c in p["caveats"]:
        add("- " + c)
    add("")
    add("## 这三张纸是不是同一天算出来的")
    add("")
    _pf = p.get("priced_faces") or {}
    _fm = _pf.get("faces") or {}
    _shown = "卡片 %s / 票据 %s / 本页 %s" % (
        _fm.get("card") or "没写", _fm.get("ticket") or "没写", _fm.get("page") or "没写")
    if _pf.get("verdict") == "SAME_DAY":
        add("**同一天。** %s —— 你手上的单子、卡片和这一页，用的是同一个收盘价。" % _shown)
    elif _pf.get("verdict") == "DIFFERENT_DAYS":
        add("**不是同一天。** %s —— 落后的那张纸，报的是上一个收盘的价；先别按它下单。"
            % _shown)
    else:
        add("**无法判断。** %s —— 有一张纸没写自己的定价日，所以这里既不能说「一致」，"
            "也不能说「不一致」。" % _shown)
    add("")
    add("---")
    add("*生成脚本 scripts/etf_book_ceo_page.py｜证据截止 %s｜卡片与单子同一决策日=%s，"
        "三张纸同一定价日=%s（%s）*"
        % (p["evidence_cutoff"], p["agreement"]["same_decision_bar"],
           _pf.get("verdict") or "UNKNOWN", _shown))
    return "\n".join(L) + "\n"


def run():
    mid = machine_id()
    if not writer_allowed(mid):
        print("etf_book_ceo_page: host=%s is not the writer (host=%s) -- honest no-op, nothing written"
              % (mid, HOST))
        return 0
    page, today = build(with_stress=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    md_path = os.path.join(OUT_DIR, "LIVE-BOOK-%s.md" % today.replace("-", ""))
    js_path = os.path.join(OUT_DIR, "LIVE-BOOK-%s.json" % today.replace("-", ""))
    with open(md_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_md(page))
    with open(js_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(page, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    # stable pointer for consumers that should not care about the date
    ptr = os.path.join(OUT_DIR, "latest.json")
    with open(ptr, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"generated_for_date": today,
                   "page": _rel(md_path, ROOT).replace("\\", "/"),
                   "json": _rel(js_path, ROOT).replace("\\", "/")},
                  fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("LIVE-BOOK written: %s (order %d names, book %.0f, cash %.0f, next rebalance %s)"
          % (_rel(md_path, ROOT), len(page["order"]), page["book_amount_cny"],
             page["cash_amount_cny"], page["next_rebalance_date"]))
    return 0


def selftest():
    ok = 0
    total = 0

    def chk(name, cond, detail=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print("[%d/%d] PASS %s%s" % (ok, total, name, (" | " + detail) if detail else ""))
        else:
            print("[%d/%d] FAIL %s%s" % (ok, total, name, (" | " + detail) if detail else ""))
        return cond

    # 1. next-rebalance arithmetic on a hand fixture: the 3rd trading day after Fri
    cal = ["2026-10-23", "2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29"]
    chk("L1 calendar: 3rd trading day after 2026-10-23", trading_days_after(cal, "2026-10-23", 3) == "2026-10-28",
        trading_days_after(cal, "2026-10-23", 3))
    chk("L2 calendar: anchor itself never counts", trading_days_after(cal, "2026-10-26", 1) == "2026-10-27")
    chk("L3 calendar: past the end -> None not a guess", trading_days_after(cal, "2026-10-26", 9) is None)
    chk("L4 calendar: degenerate n -> None", trading_days_after(cal, "2026-10-26", 0) is None)

    # 5. the live page's money must add up: order amounts + cash == capital
    page, _today = build()
    s = sum(float(o["amount_cny"] or 0) for o in page["order"])
    chk("L5 money: order sum + cash == capital",
        abs(s + page["cash_amount_cny"] - page["capital_cny"]) < 1.0,
        "sum %.2f + cash %.2f vs nav %.2f" % (s, page["cash_amount_cny"], page["capital_cny"]))
    chk("L6 money: book share == k_now", abs(page["book_amount_cny"] / page["capital_cny"] - page["k_now"]) < 0.002,
        "%.4f vs %.4f" % (page["book_amount_cny"] / page["capital_cny"], page["k_now"]))
    chk("L7 order non-empty and every row has a lot count",
        bool(page["order"]) and all((o["lots"] or 0) > 0 for o in page["order"]), "%d rows" % len(page["order"]))

    # 8. the page must actually say the things a human needs
    md = render_md(page)
    need = ["下单清单", "下次换仓", "该期待什么", "必须记住的四条"]
    missing = [k for k in need if k not in md]
    chk("L8 render: all required sections present", not missing, "missing=%s" % missing)
    chk("L9 render: no unformatted template leftovers", "{:" not in md and "%s" not in md and "%%" not in md)
    chk("L10 render: caveats carried onto the page",
        all(c.split("；")[0][:12] in md for c in page["caveats"]))
    chk("L11 page: next rebalance is a real calendar date",
        isinstance(page["next_rebalance_date"], str) and len(page["next_rebalance_date"]) == 10,
        str(page["next_rebalance_date"]))

    # 12. staleness is quoted, not hidden
    chk("L12 page: data freshness stated", page["feed_status"] is not None and page["priced_bar"] is not None,
        "%s lag=%s" % (page["feed_status"], page["feed_lag_days"]))

    # 13. the money block must be a pure unit change of numbers already on the page
    mc = page["money_cny"]
    tk_book = page.get("ticket_book") or {}
    exp_ok = (abs(mc["expected_annual_cny"] - tk_book["cagr"] * page["capital_cny"]) < 1.0
              if mc["expected_annual_cny"] is not None else mc["expected_annual_cny"] is None)
    chk("L13 money: annual yuan == backtest cagr x capital", exp_ok,
        "%s vs %.2f" % (mc["expected_annual_cny"], tk_book.get("cagr", 0) * page["capital_cny"]))
    chk("L14 money: excess yuan == excess_pp x capital",
        mc["excess_annual_cny"] is not None
        and abs(mc["excess_annual_cny"] - (page["excess_pp"] or 0.0) / 100.0 * page["capital_cny"]) < 1.0,
        "%s vs %s" % (mc["excess_annual_cny"], (page["excess_pp"] or 0.0) / 100.0 * page["capital_cny"]))
    chk("L15 money: absent inputs give None, never a zero that would read as 'earns nothing'",
        money_cny({}, 0.0)["expected_annual_cny"] is None
        and money_cny({}, 1000000.0)["excess_annual_cny"] is None
        and money_cny({"metrics": {"book": {"cagr": 0.1, "maxdd": -0.05}}}, 0.0)["expected_annual_cny"] is None,
        "empty ticket -> None; ticket without capital -> None")

    # 17. the page has to answer "do I trade today", and the answer must follow its own dates
    _base = {"book_decided_at": "2026-10-14", "priced_bar": "2026-10-26",
             "next_rebalance_date": "2026-11-11", "cost_bp_per_side": 8, "k_now": 0.5,
             "forward": {"bars": 3}}
    _hold = today_action(_base)
    chk("L17 action: holding + decision bar behind the priced bar -> hold, next date named",
        _hold["mode"] == "hold" and _hold["next_trade_date"] == "2026-11-11", _hold["mode"])
    _reb = today_action(dict(_base, book_decided_at="2026-10-26"))
    chk("L18 action: priced bar IS the decision bar -> rebalance (not hold)",
        _reb["mode"] == "rebalance", _reb["mode"])
    _open = today_action(dict(_base, forward={"bars": 0}))
    _none = today_action({"priced_bar": "2026-10-26", "forward": {"bars": 3}})
    chk("L19 action: no position -> open; missing date face -> unknown, never a guess",
        _open["mode"] == "open" and _none["mode"] == "unknown",
        "%s / %s" % (_open["mode"], _none["mode"]))
    chk("L20 action: re-trade cost is 2 sides x bp x 250 x book share on capital",
        _hold["cost_if_retraded_pct_per_year"] == 20.0,
        "%s vs 20.0 (%s)" % (_hold["cost_if_retraded_pct_per_year"], _hold["cost_basis"]))

    # 21. the LIVE page's own action line must agree with its own two dates and ledger
    _la = page["today_action"]
    _la_ok = (_la["mode"] in ("hold", "open", "rebalance")
              and (_la["mode"] == "rebalance") == (str(page["book_decided_at"]) == str(page["priced_bar"])
                                                   and bool(page["forward"]["bars"]))
              and (_la["mode"] != "hold" or _la["next_trade_date"] == page["next_rebalance_date"]))
    chk("L21 live page: action mode agrees with its own decision/priced bars and ledger",
        _la_ok, "%s decided=%s priced=%s bars=%s"
        % (_la["mode"], page["book_decided_at"], page["priced_bar"], page["forward"]["bars"]))
    # 22. single writer: only the host may write, and an unknown host must not write either
    chk("L22 guard: writer_allowed('bm-a') only",
        writer_allowed("bm-a") and not writer_allowed("bm-c") and not writer_allowed("bm-b")
        and not writer_allowed(None), "host=%s" % HOST)

    # 23-26. the stress block: hand fixture first, then the "absent panel is never zero" face
    import pandas as _pd
    _s = _pd.Series([0.01, -0.05, 0.02, -0.03, -0.04, 0.06, -0.08],
                    index=["2026-01-0%d" % i for i in range(1, 8)])
    _st = stress_stats(_s, windows=(1, 2, 5), capital=1000000.0)
    chk("L23 stress: worst 1-day is the single worst print, with its own end date",
        _st["worst"]["1d"]["pct"] == -8.0 and _st["worst"]["1d"]["end_date"] == "2026-01-07",
        str(_st["worst"]["1d"]))
    chk("L24 stress: the N-day window compounds its days and starts strictly after the anchor",
        -8.0 < _st["worst"]["5d"]["pct"] < -7.0 and _st["worst"]["5d"]["end_date"] == "2026-01-07",
        str(_st["worst"]["5d"]))
    chk("L25 stress: yuan is the percentage times this ticket's capital (a unit change only)",
        abs(_st["worst"]["1d"]["cny"] + 80000.0) < 1.0
        and abs(_st["worst"]["5d"]["cny"] / 1000000.0 * 100.0 - _st["worst"]["5d"]["pct"]) < 0.01,
        "%s / %s" % (_st["worst"]["1d"]["cny"], _st["worst"]["5d"]["cny"]))
    _no_cap = stress_stats(_s, windows=(1,), capital=None)["worst"]["1d"]
    chk("L26 stress: no panel / no capital gives None or a missing row, never a zero",
        stress_stats(None) is None and stress_stats(_pd.Series(dtype=float)) is None
        and _no_cap["cny"] is None and _no_cap["pct"] == -8.0,
        "empty panel -> None, capital-less yuan -> None")
    chk("L27 stress: a window longer than the history says 'no row', never a fabricated number",
        stress_stats(_s, windows=(50,))["worst"]["50d"] is None)
    # 27b-27e. the stress table's worst day has to be graded: a market day or a quote flip
    _cl = _pd.DataFrame({"A": [10.0, 10.0, 1.0, 1.05], "B": [10.0, 10.2, 10.3, 10.4]},
                        index=["2026-01-0%d" % i for i in range(1, 5)])
    _cleanA, _nflat, _thr = clean_panel(_cl)
    chk("L27b flip: the imported repair flattens a -90%% quote flip and keeps the level",
        _nflat == 1 and abs(float(_cleanA["A"].pct_change().iloc[2])) < 1e-12
        and abs(float(_cleanA["A"].iloc[3]) - 10.5) < 1e-9,
        "n=%s thr=%s last=%.4f" % (_nflat, _thr, float(_cleanA["A"].iloc[3])))
    _raws = stress_stats(book_returns(_cl, ["A"], [1.0]), capital=1000000.0)
    _cleans = stress_stats(book_returns(_cleanA, ["A"], [1.0]), capital=1000000.0)
    _cb = contamination_block(_raws, _cleans, _nflat, _thr)
    chk("L27c flip: the block names the raw worst day as a print and quotes both numbers",
        _cb["differs"] and _cb["raw_worst"]["1d"]["pct"] == -90.0
        and _cb["clean_worst"]["1d"]["pct"] == 0.0
        and ("-90.00%" in _cb["sentence"] and "repair_flips" in _cb["sentence"]),
        _cb["sentence"][:80])
    _cb_same = contamination_block(_raws, _raws, 0, _thr)
    chk("L27d flip: an unchanged worst day reads as a market move, not as clean-by-absence",
        (not _cb_same["differs"]) and ("行情" in _cb_same["sentence"])
        and ("-90.00%" in _cb_same["sentence"]), _cb_same["sentence"][:80])
    _cb_absent = contamination_block(_raws, None, 0, None)
    chk("L27e flip: no repaired panel -> no claim, never 'it is clean'",
        _cb_absent["clean_worst"]["1d"] is None and "不主张" in _cb_absent["sentence"],
        _cb_absent["sentence"][:80])

    # 28-29. the basket line must be the LEDGER's own number, and its absence must read as
    # absence -- re-pricing it here would be a second price source for the same claim
    _led = _load(LEDGER) if os.path.exists(LEDGER) else {}
    _bench = (_led.get("benchmark") or {}).get("latest") or {}
    if _bench.get("excess_pp") is not None:
        chk("L28 basket: page quotes the ledger's own benchmark, bar and navs to the digit",
            page["vs_basket"] is not None
            and page["vs_basket"]["bar"] == _bench.get("bar")
            and abs(page["vs_basket"]["excess_pp"] - _bench["excess_pp"]) < 1e-12
            and abs(page["vs_basket"]["book_nav"] - _bench["book_nav"]) < 1e-12,
            "ledger %s vs page %s" % (_bench.get("excess_pp"),
                                      (page["vs_basket"] or {}).get("excess_pp")))
    else:
        chk("L28 basket: page has no basket line when the ledger publishes none",
            page["vs_basket"] is None, "ledger benchmark latest absent -> page None")
    _md = render_md(dict(page, vs_basket={"bar": "2026-10-27", "book_nav": 1.004,
                                          "basket_nav": 0.9965, "excess_pp": 0.75,
                                          "basis": "等权 1/4、同一换仓日、次日开盘成交"}))
    chk("L29 basket: the rendered page carries the basket comparison and its caveat",
        "ETF 篮子" in _md and "+0.75" in _md and "不是长期超额" in _md,
        "rendered line present")

    # 30. the spread is not a verdict: the page must carry the horizon inside which the
    # number means anything (r1316). A power block that stays in the ledger is a decision
    # only a reader who opens the JSON gets.
    _pw = ((_led.get("benchmark") or {}).get("significance") or {}).get("power") or {}
    if _pw.get("available") and _bench.get("excess_pp") is not None:
        _md2 = render_md(dict(page, vs_basket=dict(page["vs_basket"])))
        _want = "%.1f 个百分点/年" % (_pw["min_detectable_edge_pp"]["1y"])
        chk("L30 basket: the page states the edge its 12-month view could resolve",
            _want in _md2 and "健康检查，不是判词" in _md2,
            "want=%s" % _want)
    else:
        chk("L30 basket: no horizon sentence when the ledger publishes no power block",
            page.get("vs_basket") is None
            or "健康检查，不是判词" not in render_md(dict(page)), "guard leg")

    # 31-34. the idle half is not 0% -- cash x the repo panel's own close, and an
    # unreadable panel stays None (a 0 would read as "the cash earns nothing", which is
    # the very case the reader needs to be warned about)
    import tempfile
    _td = tempfile.mkdtemp()
    with open(os.path.join(_td, "GC001.csv"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("date,open,high,low,close,volume\n")
        fh.write("2026-10-26,1.2,1.2,0.31,1.0,100\n")
        fh.write("2026-10-27,1.18,1.4,1,2.0,100\n")
    _cy = cash_yield(100000.0, panel_dir=_td)
    chk("L31 cash: annual yuan == cash x the panel's own close rate",
        _cy["rate_pct"] == 2.0 and _cy["rate_date"] == "2026-10-27"
        and _cy["annual_cny"] == 2000.0 and _cy["daily_cny"] == 8.0
        and _cy["rate_20d_pct"] == 1.5,
        "rate %.2f annual %s daily %s mean %s"
        % (_cy["rate_pct"], _cy["annual_cny"], _cy["daily_cny"], _cy["rate_20d_pct"]))
    _bad = tempfile.mkdtemp()
    with open(os.path.join(_bad, "GC001.csv"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("date,open,high,low,close,volume\n")
        fh.write("2026-10-27,900,900,900,900,100\n")
    chk("L32 cash: missing panel / zero cash / out-of-band print -> None, never 0",
        cash_yield(100000.0, panel_dir=os.path.join(_td, "nope"))["annual_cny"] is None
        and cash_yield(0.0, panel_dir=_td)["annual_cny"] is None
        and cash_yield(None, panel_dir=_td)["annual_cny"] is None
        and cash_yield(100000.0, panel_dir=_bad)["annual_cny"] is None,
        "absent / zero-cash / 900% print all None")
    _live = page["cash_yield"]
    _ok_live = (_live["annual_cny"] is None
                or (abs(_live["annual_cny"] - page["cash_amount_cny"] * _live["rate_pct"] / 100.0) < 1.0
                    and bool(_live["rate_date"])))
    chk("L33 live page: cash yuan == its own cash x its own rate, with the rate date",
        _ok_live, "cash %.0f rate %s @ %s -> %s"
        % (page["cash_amount_cny"], _live["rate_pct"], _live["rate_date"], _live["annual_cny"]))
    _md3 = render_md(dict(page, cash_yield={"leg": "GC001", "rate_pct": 1.09,
                                            "rate_date": "2026-10-27", "annual_cny": 5764.0,
                                            "daily_cny": 23.0, "rate_20d_pct": 1.1,
                                            "window": 20}))
    chk("L34 cash: the rendered page carries the rate, its date and the 'not a return source' line",
        "现金那一半在赚多少" in _md3 and "1.09%" in _md3 and "2026-10-27" in _md3
        and "+¥5,764" in _md3 and "不是收益来源" in _md3, "rendered cash block present")

    # 35-38. the ladder question ("should the cash sit in a longer repo?") is answered by
    # rolling each tenor on the panel's own calendar -- the adoption rule is a frozen
    # constant, and the verdict has to be recomputed from the cells, never typed in.
    import datetime as _dt

    def _panel(dirpath, symbol, pairs):
        with open(os.path.join(dirpath, "%s.csv" % symbol), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write("date,open,high,low,close,volume\n")
            for d, v in pairs:
                fh.write("%s,%.4f,%.4f,%.4f,%.4f,100\n" % (d, v, v, v, v))

    def _sessions(start, n, weekdays=(0, 1, 2, 3, 4)):
        out = []
        d = start
        while len(out) < n:
            if d.weekday() in weekdays:
                out.append(d)
            d += _dt.timedelta(days=1)
        return out

    _lad = tempfile.mkdtemp()
    _days = _sessions(_dt.date(2021, 1, 4), 700)
    # flat calendar: every tenor quoted at 2.0% -> identical realised yield, so no
    # longer tenor may be adopted (an adoption here would be a rule bug, not an edge)
    for _sym in ("GC001", "GC003", "GC007", "GC014"):
        _panel(_lad, _sym, [(d.isoformat(), 2.0) for d in _days])
    _cl_flat = cash_ladder(100000.0, panel_dir=_lad)
    chk("L35 ladder: identical quotes -> nothing adopts, the 1-day leg is kept",
        _cl_flat["verdict"] == "KEEP-1D" and _cl_flat["pick"] == "GC001"
        and abs(_cl_flat["tenors"][0]["realized"]["1"]["realized_pct"] - 2.0) < 1e-9,
        "verdict=%s pick=%s base1y=%s"
        % (_cl_flat["verdict"], _cl_flat["pick"],
           _cl_flat["tenors"][0]["realized"]["1"]["realized_pct"]))
    chk("L36 ladder: rolling the 1-day leg covers every calendar day, no idle cash",
        _cl_flat["tenors"][0]["idle_days_1y"] == 0
        and _cl_flat["tenors"][0]["idle_share_1y"] == 0.0,
        "idle=%s share=%s" % (_cl_flat["tenors"][0]["idle_days_1y"],
                              _cl_flat["tenors"][0]["idle_share_1y"]))

    _lad2 = tempfile.mkdtemp()
    _panel(_lad2, "GC001", [(d.isoformat(), 2.0) for d in _days])
    _panel(_lad2, "GC007", [(d.isoformat(), 2.60) for d in _days])   # +60bp: clears 20bp
    _cl_wide = cash_ladder(100000.0, panel_dir=_lad2, tenors=("GC001", "GC007"))
    chk("L37 ladder: a +60bp tenor that never sits idle adopts, and its yuan follows it",
        _cl_wide["verdict"] == "ADOPT" and _cl_wide["pick"] == "GC007"
        and abs(_cl_wide["tenors"][1]["annual_cny_realized_1y"] - 2600.0) < 20.0,
        "verdict=%s pick=%s edge=%s yuan=%s"
        % (_cl_wide["verdict"], _cl_wide["pick"],
           _cl_wide["tenors"][1]["edge_bp"].get("1"),
           _cl_wide["tenors"][1]["annual_cny_realized_1y"]))
    _lad3 = tempfile.mkdtemp()
    _panel(_lad3, "GC001", [(d.isoformat(), 2.0) for d in _days])
    _panel(_lad3, "GC007", [(d.isoformat(), 2.10) for d in _days])   # +10bp: below the door
    _cl_thin = cash_ladder(100000.0, panel_dir=_lad3, tenors=("GC001", "GC007"))
    chk("L38 ladder: a +10bp edge is rejected by the frozen 20bp rule, not adopted",
        _cl_thin["verdict"] == "KEEP-1D" and _cl_thin["tenors"][1]["verdict"] == "REJECT"
        and "门槛" in (_cl_thin["tenors"][1]["reason"] or "")
        and "20 bp" in (_cl_thin["tenors"][1]["reason"] or ""),
        "verdict=%s arm=%s reason=%s"
        % (_cl_thin["verdict"], _cl_thin["tenors"][1]["verdict"],
           _cl_thin["tenors"][1]["reason"]))
    _cl_live = page.get("cash_ladder") or {}
    _ok_l = bool(_cl_live.get("tenors")) and _cl_live.get("verdict") in ("KEEP-1D", "ADOPT")
    _ok_l = _ok_l and all(
        (r.get("spot_pct") is None or 0.0 < float(r["spot_pct"]) < 200.0)
        for r in _cl_live.get("tenors") or [])
    _md4 = render_md(page)
    _ok_l = _ok_l and ("现金腿要不要换长一点的期限" in _md4
                       and ("继续一天期" in _md4 or "换 " in _md4)
                       and "空转" in _md4)
    chk("L39 ladder: the live page answers the ladder question with each tenor's own quote",
        _ok_l, "verdict=%s pick=%s rows=%d"
        % (_cl_live.get("verdict"), _cl_live.get("pick"),
           len(_cl_live.get("tenors") or [])))

    # 40-44. the handshake: advice ("buy the repo") vs account ("what was placed").
    # The failure mode this guards is the one the cash block has been advertising all
    # along -- a reader who did nothing reads the same page as one who did.
    _lad_h = tempfile.mkdtemp()
    _panel(_lad_h, "GC001", [(d.isoformat(), 2.0) for d in _days])
    _lad_v = cash_ladder(100000.0, panel_dir=_lad_h, tenors=("GC001",))
    _rec = tempfile.mkdtemp()
    _pfile = os.path.join(_rec, "cash_placement.json")

    _h_absent = cash_handshake(100000.0, _lad_v, placement_path=_pfile,
                               today="2026-10-29")
    chk("L40 handshake: no record -> UNRECORDED with a None gap (unread is not zero), and the worst case is stated",
        _h_absent["status"] == "UNRECORDED" and _h_absent["gap_annual_cny"] is None
        and _h_absent["idle_cny"] is None
        and abs(_h_absent["worst_case_annual_cny"] - 1950.0) < 1.0,
        "status=%s gap=%s worst=%s" % (_h_absent["status"], _h_absent["gap_annual_cny"],
                                       _h_absent["worst_case_annual_cny"]))

    def _write_placements(rec, by, asof, rows, demand=0.05):
        with open(_pfile, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"schema": "cash-placement/v1", "asof": asof, "recorded_by": by,
                       "demand_rate_pct": demand, "placements": rows}, fh)
        return _pfile

    _write_placements(_rec, "unrecorded", "2026-10-29", [])
    _h_blank = cash_handshake(100000.0, _lad_v, placement_path=_pfile, today="2026-10-29")
    chk("L41 handshake: a file that exists but nobody filled is still UNRECORDED",
        _h_blank["status"] == "UNRECORDED" and _h_blank["gap_annual_cny"] is None,
        "status=%s" % _h_blank["status"])

    _write_placements(_rec, "jason", "2026-10-29",
                      [{"instrument": "GC001", "amount_cny": 40000.0,
                        "rate_pct": 1.9, "rate_date": "2026-10-28"}])
    _h_part = cash_handshake(100000.0, _lad_v, placement_path=_pfile, today="2026-10-29")
    chk("L42 handshake: half placed -> PARTIAL, idle and the gap are the panel's rate minus the declared demand rate",
        _h_part["status"] == "PARTIAL" and _h_part["idle_cny"] == 60000.0
        and abs(_h_part["gap_annual_cny"] - 1170.0) < 1.0
        and _h_part["gap_daily_cny"] == round(1170.0 / 250.0),
        "status=%s idle=%s gap=%s daily=%s" % (_h_part["status"], _h_part["idle_cny"],
                                               _h_part["gap_annual_cny"],
                                               _h_part["gap_daily_cny"]))

    _write_placements(_rec, "jason", "2026-10-29",
                      [{"instrument": "GC001", "amount_cny": 100000.0,
                        "rate_pct": 1.9, "rate_date": "2026-10-28"}])
    _h_full = cash_handshake(100000.0, _lad_v, placement_path=_pfile, today="2026-10-29")
    _write_placements(_rec, "jason", "2026-10-29",
                      [{"instrument": "GC001", "amount_cny": 100000.0, "rate_pct": 1.9},
                       {"instrument": "GC007", "amount_cny": 20000.0, "rate_pct": 2.0}])
    _h_over = cash_handshake(100000.0, _lad_v, placement_path=_pfile, today="2026-10-29")
    _write_placements(_rec, "jason", "2026-10-20",
                      [{"instrument": "GC001", "amount_cny": 100000.0, "rate_pct": 1.9}])
    _h_stale = cash_handshake(100000.0, _lad_v, placement_path=_pfile, today="2026-10-29")
    chk("L43 handshake: fully placed -> IN-PLACE at zero gap; more placed than the book holds -> OVER-PLACED, not silently clamped; an old record says so",
        _h_full["status"] == "IN-PLACE" and (_h_full["gap_annual_cny"] or 0) == 0.0
        and _h_over["status"] == "OVER-PLACED" and _h_over["idle_cny"] == 0.0
        and "对不上" in (_h_over["reason"] or "")
        and _h_stale["status"] == "IN-PLACE" and _h_stale["stale"] is True
        and "过期" in (_h_stale["reason"] or ""),
        "in-place=%s over=%s stale=%s" % (_h_full["status"], _h_over["status"],
                                          _h_stale["stale"]))

    _hs_live = page.get("cash_handshake") or {}
    _md5 = render_md(page)
    chk("L44 handshake: the live page renders the reconciliation and its status is one of the five honest states",
        "现金现在到底在哪" in _md5
        and _hs_live.get("status") in ("UNRECORDED", "IN-PLACE", "PARTIAL", "IDLE", "OVER-PLACED")
        and (("一年少赚约" in _md5) or ("没有缺口" in _md5) or ("对不上" in _md5)),
        "status=%s gap=%s" % (_hs_live.get("status"), _hs_live.get("gap_annual_cny")))

    # 45-47. the carry split: how much of the quoted headline is the repo leg. The failure
    # this guards is a page that quotes 11.33%/yr beside a 1.09% cash leg and leaves the
    # reader thinking selection earned all of it.
    _cr_live = page.get("carry_regime") or {}
    _md6 = render_md(page)
    if _cr_live.get("available"):
        _b = _cr_live.get("base") or {}
        _ok_c = ("这笔钱里有多少是" in _md6 and "%.2f%%" % (_b.get("zero_pct") or 0.0) in _md6
                 and "0 息" in _md6)
        chk("L45 carry split: the live page states what the book pays with a zero-rate cash leg",
            _ok_c, "base beta=%s observed=%s zero=%s" % (_b.get("beta"), _b.get("observed_pct"),
                                                         _b.get("zero_pct")))
        _rows = _cr_live.get("rows") or []
        _mono = all(r["observed_pct"] >= r["flat_today_pct"] >= r["zero_pct"] - 1e-9
                    for r in _rows)
        chk("L46 carry split: every published ladder row keeps observed >= today-flat >= zero",
            _mono and len(_rows) >= 2, "rows=%d" % len(_rows))
    else:
        _noart = carry_regime(path=os.path.join(tempfile.mkdtemp(), "absent.json"))
        chk("L45 carry split: absent artifact -> not available, and the section says so "
            "instead of inventing a number",
            _noart.get("available") is False and "这一节没有数" in _md6)
        chk("L46 carry split: absent artifact exposes no rows", _noart.get("rows") == [])

    _fake = os.path.join(tempfile.mkdtemp(), "regime.json")
    with open(_fake, "w", encoding="utf-8") as _fh:
        json.dump({"evidence_cutoff": "2026-10-29",
                   "cash_rates": {"observed_mean_pct": 2.0, "today_pct": 1.0},
                   "cells": [{"beta": 0.2, "regime": r, "cagr_pct": v, "maxdd_pct": -5.0,
                              "vol_pct": 8.0, "cash_share": 0.5, "first_bar": "2024-01-02",
                              "last_bar": "2026-10-29"}
                             for r, v in (("observed", 11.0), ("flat_today", 10.5), ("zero", 10.0))],
                   "gate": {"base_beta": 0.2, "flags": {"carry_positive": True},
                            "betas": {"0.2": {"observed_pct": 11.0, "flat_today_pct": 10.5,
                                             "zero_pct": 10.0, "carry_pp": 1.0,
                                             "cash_share": 0.5, "pp_per_100bp": 1.0}}}},
                  _fh)
    _fake_ok = carry_regime(path=_fake)
    chk("L47 carry split: a fixture artifact is read whole (base, ladder row, window, flags)",
        _fake_ok.get("available") is True and len(_fake_ok["rows"]) == 1
        and _fake_ok["base"]["beta"] == 0.2 and _fake_ok["base"]["pp_per_100bp"] == 1.0
        and _fake_ok["window"]["first"] == "2024-01-02",
        "rows=%d base=%s" % (len(_fake_ok.get("rows") or []), (_fake_ok.get("base") or {}).get("beta")))

    # 48-50. the bet count: five tickers are not five bets (r1172 face). The page must
    # quote the artifact's own sentence, and must never fall back to counting names.
    _sdir = os.path.dirname(os.path.abspath(__file__))
    if _sdir not in sys.path:
        sys.path.insert(0, _sdir)
    import etf_book_bets_face as _bfm
    _bf_live2 = bets_face()
    _bf_pub = _bfm.read_published()
    _md7 = render_md(page)
    chk("L48 bet count: the page goes through the one reader the ticket also quotes (no second copy)",
        _bf_live2.get("sentence") == _bf_pub.get("sentence")
        and _bf_live2.get("effective_bets") == _bf_pub.get("effective_bets"),
        "status=%s" % _bf_pub.get("status"))
    if _bf_pub.get("status") == "ok" and _bf_pub.get("sentence"):
        chk("L49 bet count: the live page prints the published sentence verbatim beside the order table",
            _bf_pub["sentence"] in _md7 and "这几只票到底有几个赌注" in _md7,
            "eff=%s nominal=%s" % (_bf_pub.get("effective_bets"), _bf_pub.get("nominal_bets")))
        chk("L50 bet count: the counts printed are the artifact's numbers, not a fresh computation",
            ("%.2f" % float(_bf_pub["effective_bets"])) in _md7
            and ("%.2f" % float(_bf_pub["risk_split"])) in _md7
            and ("数票数 %d 只" % round(float(_bf_pub["nominal_bets"]))) in _md7,
            "eff=%s nominal=%s split=%s" % (_bf_pub.get("effective_bets"),
                                            _bf_pub.get("nominal_bets"),
                                            _bf_pub.get("risk_split")))
    else:
        chk("L49 bet count: an absent artifact reads as absent, never as five bets",
            ("缺面不读成一个赌注" in _md7) and ("数方向" not in _md7),
            "status=%s" % _bf_pub.get("status"))

    # 51-53. the replay cache must key on what it was computed FROM, not on the date.
    # A repaired print (flip fix) rewrites today's worst window without moving today's
    # date, and a re-priced ticket changes the weights on the very same bar -- the cache
    # form of the staleness family closed in r1372-r1374.
    _pf = _pd.DataFrame({"AAA": [1.0, 1.01, 1.02, 1.0],
                         "BBB": [1.0, 0.99, 1.0, 1.01]},
                        index=_pd.to_datetime(["2020-01-02", "2020-01-03",
                                               "2020-01-06", "2020-01-07"]))
    _ord_a = [{"symbol": "AAA", "weight": 0.5}, {"symbol": "BBB", "weight": 0.5}]
    _d_a = stress_cache_digest(_pf, "2020-01-07", 1000000.0, STRESS_WINDOWS, _ord_a)
    chk("L51 stress cache: same bar, same weights, same panel -> same key (a hit is a hit)",
        _d_a == stress_cache_digest(_pf.copy(), "2020-01-07", 1000000.0,
                                    STRESS_WINDOWS, list(_ord_a)), "digest=%s" % _d_a[:12])
    _ord_b = [{"symbol": "AAA", "weight": 0.6}, {"symbol": "BBB", "weight": 0.4}]
    chk("L52 stress cache: re-pricing the ticket on the SAME bar changes the key",
        _d_a != stress_cache_digest(_pf, "2020-01-07", 1000000.0, STRESS_WINDOWS, _ord_b),
        "weights 50/50 vs 60/40")
    _pf2 = _pf.copy()
    _pf2.iloc[1, 0] = 1.03                  # a repaired print: same shape, same date
    chk("L53 stress cache: a repaired print on the SAME date changes the key",
        _d_a != stress_cache_digest(_pf2, "2020-01-07", 1000000.0, STRESS_WINDOWS, _ord_a),
        "identical bar and weights")

    # L54-L56 (r1184): the page quotes a band whose width was chosen out of a family of arm
    # cells. If that family never priced one panel, the band is a configuration -- and the
    # three states must read differently, or "unproven" and "proven" look identical.
    def _render_fc(fc):
        # the fixture is the LIVE page with one field swapped, so this leg fails only for
        # the reason it is about; a hand-built dict would rot the moment the page grows.
        _p, _ = build(with_stress=False)
        _p["family_coherence"] = fc
        return render_md(_p)

    _md_one = _render_fc({"verdict": "ONE_WORLD", "arms": 11, "panels": ["deadbeef"],
                          "evidence_cutoff": "2026-10-30",
                          "artifact": "results/etf_book_phase_atlas_arms.json"})
    _md_mixed = _render_fc({"verdict": "MIXED_WORLDS", "arms": 11, "panels": ["a", "b"],
                            "detail": "two panels", "evidence_cutoff": None,
                            "artifact": "results/etf_book_phase_atlas_arms.json"})
    _md_absent = _render_fc(None)
    chk("L54 family coherence: one world names the arm count, the panel and the cutoff",
        "有。" in _md_one and "11 个宽度臂" in _md_one and "deadbeef" in _md_one
        and "2026-10-30" in _md_one, "")
    chk("L55 family coherence: a withheld family reads 'no' and says the width is a config",
        "没有。" in _md_mixed and "MIXED_WORLDS" in _md_mixed
        and "ONE_WORLD" not in _md_mixed, "")
    chk("L56 family coherence: an absent face reads 'unknown', never a pass",
        "不知道。" in _md_absent and "ONE_WORLD" not in _md_absent
        and "没验" in _md_absent, "")

    # L57-L59 (r1185): the page used to answer "same priced bar = True" without ever printing
    # which day any of the three papers was priced on. A reader told "different" must be able
    # to see WHICH paper is stale, so all three days are printed and the three states read
    # differently -- an unknown must never borrow the wording of agreement.
    def _render_pf(pf):
        _p, _ = build(with_stress=False)
        _p["priced_faces"] = pf
        return render_md(_p)

    _md_same = _render_pf({"verdict": "SAME_DAY", "same_day": True, "missing": [],
                           "detail": "all three papers priced the 2026-10-30 bar",
                           "faces": {"card": "2026-10-30", "ticket": "2026-10-30",
                                     "page": "2026-10-30"}})
    _md_split = _render_pf({"verdict": "DIFFERENT_DAYS", "same_day": False, "missing": [],
                            "detail": "priced on different bars",
                            "faces": {"card": "2026-10-30", "ticket": "2026-10-30",
                                      "page": "2026-10-29"}})
    _md_unknown = _render_pf({"verdict": "UNKNOWN", "same_day": False, "missing": ["ticket"],
                              "detail": "no pricing day on: ticket",
                              "faces": {"card": "2026-10-30", "ticket": None,
                                        "page": "2026-10-30"}})
    # the section HEADING asks "are these three the same day" and therefore literally
    # contains the string 不是同一天, so every assertion anchors on the BOLDED verdict.
    chk("L57 priced days: all three papers print their own day and read 'same day'",
        "**同一天。**" in _md_same and _md_same.count("2026-10-30") >= 3
        and "**不是同一天。**" not in _md_same, "")
    chk("L58 priced days: a stale paper is named, not just denied",
        "**不是同一天。**" in _md_split and "本页 2026-10-29" in _md_split
        and "**同一天。**" not in _md_split, "")
    chk("L59 priced days: a paper with no day reads 'cannot tell', never agreement",
        "**无法判断。**" in _md_unknown and "**同一天。**" not in _md_unknown
        and "票据 没写" in _md_unknown, "")

    # L60-L62 (r1189): the page told the reader how much of the headline is cash lending
    # and how big the book is, but never where in the DAY the money accrues. The split
    # must be quoted verbatim from the artifact (not recomputed here), the three states
    # must read differently, and a broken face must print no numbers at all.
    def _render_legs(ls):
        _p, _ = build(with_stress=False)
        _p["leg_split"] = ls
        return render_md(_p)

    _legs_ok = {"status": "ok", "artifact": LEGS_JSON, "evidence_cutoff": "2026-10-30",
                "execution": "decide at close -> fill at next open",
                "arms": {"production": {"buckets_pp_per_year": {"plain": 9.83, "overnight": 0.16,
                                                                "intraday": -0.64, "toll": -1.15},
                                        "total_log_pp": 8.21,
                                        "plain_carry_pp_per_year": 9.83,
                                        "fill_bar_drag_pp_per_year": -1.62,
                                        "fill_bars": 83, "plain_bars": 1569},
                         "control_ew": {"buckets_pp_per_year": {"plain": 6.20}}}}
    _md_legs = _render_legs(_legs_ok)
    chk("L60 leg split: the four buckets and the fill-bar count reach the page verbatim",
        all(s in _md_legs for s in ("+9.83", "+0.16", "-0.64", "-1.15", "1569", "83")), "")
    chk("L61 leg split: a book that earns on quiet bars says so in one sentence",
        "什么都没发生" in _md_legs and "拖累 1.62" in _md_legs, "")
    _md_legs_gone = _render_legs({"status": "absent", "artifact": LEGS_JSON, "arms": {}})
    _md_legs_broken = _render_legs({"status": "broken", "artifact": LEGS_JSON,
                                    "detail": "production: buckets sum 5.000 != published 0.000",
                                    "arms": {}})
    chk("L62 leg split: absent or broken prints 'cannot verify' and no bucket numbers",
        "无法核验" in _md_legs_gone and "无法核验" in _md_legs_broken
        and "+9.83" not in _md_legs_gone and "+9.83" not in _md_legs_broken, "")

    # L63-L65 (r1191): the ticket started printing "whose CAGR is this" at r1190 while the
    # page -- the face the CEO opens -- answered with an unsourced headline. The page must
    # quote the published reading (never re-derive it here), the two deletion arms must
    # reach it with their own money, and a face that could not reproduce the engine equity
    # must print no numbers at all.
    def _render_conc(cc):
        _p, _ = build(with_stress=False)
        _p["concentration"] = cc
        return render_md(_p)

    _conc_ok = {"status": "ok", "artifact": CONC_JSON, "evidence_cutoff": "2026-10-30",
                "verdict": "BROAD|SURVIVES_WITHOUT_TOP3", "top3_share": 0.2205,
                "hhi": 0.0241, "names_negative": 69, "names_above_1pct": 41,
                "distinct_names": 189,
                "top": [{"symbol": "159934", "name": "黄金ETF", "share": 0.0752}],
                "baseline": {"cagr": 0.096, "sharpe": 0.99, "maxdd": -0.1177},
                "top_k_out": {"k": 3, "delta_cagr_pp": -1.99,
                              "stats": {"full": {"cagr": 0.0761, "sharpe": 0.809,
                                                 "maxdd": -0.1868}}},
                "sleeve": {"class": "商品", "symbols_removed": 41, "delta_cagr_pp": -3.71,
                           "stats": {"full": {"cagr": 0.0589, "sharpe": 0.64,
                                              "maxdd": -0.223}}}}
    _md_conc = _render_conc(_conc_ok)
    chk("L63 concentration: the reader's own numbers reach the page (top3 share, both deletions)",
        all(s in _md_conc for s in ("22.1%", "黄金ETF", "7.5%", "-1.99pp", "-3.71pp",
                                    "BROAD · SURVIVES_WITHOUT_TOP3")), "")
    chk("L64 concentration: the sleeve arm states that the paying leg is also the cushion",
        "抗回撤" in _md_conc and "-22.3%" in _md_conc and "+-22.3" not in _md_conc, "")
    _md_conc_absent = _render_conc({"status": "absent", "artifact": CONC_JSON,
                                    "sentence": None, "verdict": None})
    _md_conc_broken = _render_conc({"status": "no_identity", "artifact": CONC_JSON,
                                    "sentence": None, "verdict": None})
    chk("L65 concentration: absent or a broken identity prints 'cannot verify' and no numbers",
        "无法核验" in _md_conc_absent and "无法核验" in _md_conc_broken
        and "22.1%" not in _md_conc_absent and "22.1%" not in _md_conc_broken, "")

    # L66-L68 (r1193): the concentration section tells the reader the whole commodity
    # sleeve pays for the drawdown, and the reader's next question is "so should we gate
    # it?". r1192 measured that and answered on the card; the page has to answer too --
    # quoting the reader's rows, and reading each gate's failure mode off its own numbers
    # (a draft of this text said "both hard gates lose to their placebo" about an arm
    # that beat it by 2.43pp, which is why the sentence is generated, not written).
    def _render_sleeve(sg):
        _p, _ = build(with_stress=False)
        _p["sleeve_gate"] = sg
        return render_md(_p)

    _sg_ok = {"status": "ok", "artifact": SLEEVE_JSON, "evidence_cutoff": "2026-10-30",
              "verdict": "NO_GATE", "book": {"decisions": 83},
              "criteria": {"min_dd_gain_pp": 1.0, "cagr_keep": 0.95,
                           "placebo_dd_edge_pp": 0.5, "placebo_cagr_edge_pp": 0.5},
              "gates": [
                  {"name": "trend", "off_decisions": 20, "off_share": 0.241,
                   "delta_cagr_pp": -0.32, "delta_maxdd_pp": -2.77,
                   "dd_gain_pp": -2.77, "cagr_keep": 0.9667,
                   "placebo_dd_edge_pp": -1.03, "placebo_cagr_edge_pp": -1.41,
                   "beats_placebo": False, "verdict": "NO_GATE", "why": "no_gain_vs_baseline"},
                  {"name": "vol", "off_decisions": 25, "off_share": 0.3012,
                   "delta_cagr_pp": 0.02, "delta_maxdd_pp": 0.86,
                   "dd_gain_pp": 0.86, "cagr_keep": 1.0021,
                   "placebo_dd_edge_pp": 5.0, "placebo_cagr_edge_pp": 2.92,
                   "beats_placebo": True, "verdict": "NO_GATE", "why": "short_of_bar"},
                  {"name": "drawdown", "off_decisions": 13, "off_share": 0.1566,
                   "delta_cagr_pp": -0.18, "delta_maxdd_pp": -1.27,
                   "dd_gain_pp": -1.27, "cagr_keep": 0.9813,
                   "placebo_dd_edge_pp": 2.43, "placebo_cagr_edge_pp": 2.0,
                   "beats_placebo": True, "verdict": "NO_GATE", "why": "no_gain_vs_baseline"}],
              "closest": {"name": "vol", "dd_gain_pp": 0.86, "placebo_dd_edge_pp": 5.0}}
    _md_sg = _render_sleeve(_sg_ok)
    chk("L66 sleeve gate: every arm's dose and both deltas reach the page from the reader",
        all(s in _md_sg for s in ("20/83", "25/83", "13/83", "24.1%", "30.1%", "15.7%",
                                  "+0.86pp", "-2.77pp", "-1.27pp", "NO_GATE")), "")
    chk("L67 sleeve gate: the near miss is named as a re-test candidate, not a re-threshold",
        "波动门" in _md_sg and "1.0pp" in _md_sg and "+5.00pp" in _md_sg
        and "跑到达标为止" in _md_sg, "")
    chk("L68 sleeve gate: each failure mode comes from the row's own 'why', not from prose",
        "有 **2 条**门（趋势、回撤）" in _md_sg
        and "其中 **趋势** 连自己的安慰剂也赢不了" in _md_sg
        and "回撤 连自己的安慰剂" not in _md_sg, "")
    _md_sg_gone = _render_sleeve({"status": "absent", "artifact": SLEEVE_JSON,
                                  "sentence": None, "verdict": None})
    _md_sg_broken = _render_sleeve({"status": "no_identity", "artifact": SLEEVE_JSON,
                                    "sentence": None, "verdict": None})
    chk("L69 sleeve gate: absent or an identity failure reads 'cannot verify' and no gate table",
        "无法核验" in _md_sg_gone and "无法核验" in _md_sg_broken
        and "| 门 |" not in _md_sg_gone and "| 门 |" not in _md_sg_broken
        and "20/83" not in _md_sg_gone and "20/83" not in _md_sg_broken, "")

    # L70-L72 (r1197): r1196 proved the vol overlay is average exposure, not timing -- and
    # filed it in a research note. The page is what the CEO opens, and it was still telling
    # him the book shrinks with no hint that shrinking buys no skill. The page must quote
    # the reader (never re-derive), name the matched-average control instead of comparing
    # against a full book (any de-lever "reduces drawdown" against full), and print nothing
    # at all when the artifact is missing or its identity gate failed.
    def _render_et(et):
        _p, _ = build(with_stress=False)
        _p["exposure_timing"] = et
        return render_md(_p)

    _et_ok = {"status": "ok", "artifact": EXPOSURE_JSON, "evidence_cutoff": "2026-10-30",
              "bars": 1653, "decisions": 83,
              "identity": {"gap": 0.0, "tol": 1e-12},
              "exposure": {"mean_engine_scale": 0.7073, "delevered_decision_share": 0.879},
              "arms": {"production": {"cagr": 0.0912, "sharpe": 0.955, "maxdd": -0.1326,
                                      "mean_exposure": 0.7073},
                       "full": {"cagr": 0.1321, "sharpe": 0.921, "maxdd": -0.1629,
                                "mean_exposure": 1.0},
                       "constant": {"cagr": 0.1003, "sharpe": 0.974, "maxdd": -0.1154,
                                    "mean_exposure": 0.7073}},
              "placebo": {"n": 20, "cagr_mean": 0.098},
              "verdict": {"state": "AVERAGE_EXPOSURE_ONLY", "timing_pp": -0.91,
                          "placebo_p05_pp": -1.9, "placebo_p95_pp": 0.88,
                          "de_risking_pp": -3.18},
              "sentence": "production 9.12% vs a constant book 10.03%"}
    _md_et = _render_et(_et_ok)
    chk("L70 exposure timing: the reader's own numbers reach the page",
        all(s in _md_et for s in ("9.12%", "10.03%", "-0.91pp", "-1.90", "+0.88pp",
                                  "20 条安慰剂", "AVERAGE_EXPOSURE_ONLY", "87.9%", "70.7%")),
        "")
    chk("L71 exposure timing: the control is a matched-average book, and the cost of "
        "de-risking is printed",
        "同样的平均仓位" in _md_et and "-3.18pp" in _md_et
        and "和满仓比" in _md_et and "-0.1629" not in _md_et, "")
    _md_et_gone = _render_et({"status": "absent", "artifact": EXPOSURE_JSON, "sentence": None})
    _md_et_broken = _render_et({"status": "no_identity", "artifact": EXPOSURE_JSON,
                                "sentence": None})
    chk("L72 exposure timing: absent or a failed identity gate reads 'cannot verify' "
        "and prints no arithmetic",
        "无法核验" in _md_et_gone and "无法核验" in _md_et_broken
        and "-3.18pp" not in _md_et_gone and "-3.18pp" not in _md_et_broken
        and "AVERAGE_EXPOSURE_ONLY" not in _md_et_gone
        and "AVERAGE_EXPOSURE_ONLY" not in _md_et_broken, "")

    # r1198: the cost assumption under every published number -----------------------
    def _render_ct(ct):
        _p, _ = build(with_stress=False)
        _p["cost_tape"] = ct
        return render_md(_p)
    _ct_ok = {"status": "ok", "artifact": COST_JSON, "evidence_cutoff": "2026-10-30",
              "verdict": "CONSERVATIVE | SURVIVES", "assumed_bp": 10.0, "measured_bp": 5.9,
              "ratio_vs_assumed": 0.589,
              "arms": {"assumed_10bp": {"cagr": 0.096, "sharpe": 0.99, "maxdd": -0.1177},
                       "measured": {"cagr": 0.1011, "sharpe": 1.037, "maxdd": -0.1137},
                       "upper_p75": {"cagr": 0.0972, "sharpe": 1.001, "maxdd": -0.1168}},
              "tape": {"n_traded_names": 189, "median_name_p50_bp": 13.2,
                       "widest_traded": [{"symbol": "159967", "p50_bp": 31.5}]},
              "control": {"passes": True, "engine_cagr": 0.096, "published_cagr": 0.096,
                          "tolerance_pp": 0.5},
              "decisions": {"priced": 83, "dropped_low_coverage": 0}}
    _md_ct = _render_ct(_ct_ok)
    chk("L73 cost tape: the measured cost, all three arms and the verdict reach the page",
        all(s in _md_ct for s in ("5.9 bp", "59%", "10.11%", "9.72%", "9.60%",
                                  "CONSERVATIVE · SURVIVES", "189", "159967")), "")
    chk("L74 cost tape: the control arm is named, and the pipe in the verdict never "
        "reaches a table cell",
        "控制臂" in _md_ct and "CONSERVATIVE | SURVIVES" not in _md_ct,
        "a raw '|' in a cell silently splits the markdown row (r1193)")
    _md_ct_gone = _render_ct({"status": "absent", "artifact": COST_JSON, "sentence": None})
    _md_ct_bad = _render_ct({"status": "no_control", "artifact": COST_JSON,
                             "sentence": None})
    chk("L75 cost tape: absent or a failed control arm reads 'cannot verify' and prints "
        "no arithmetic",
        "无法核验" in _md_ct_gone and "无法核验" in _md_ct_bad
        and "5.9 bp" not in _md_ct_gone and "5.9 bp" not in _md_ct_bad
        and "CONSERVATIVE" not in _md_ct_gone and "CONSERVATIVE" not in _md_ct_bad, "")

    # r1203 / E321: the 60-day vol window was never tested across decision calendars ----
    def _render_vw(vw):
        _p, _ = build(with_stress=False)
        _p["vol_window"] = vw
        return render_md(_p)
    _crit = {"sharpe_gain": 0.02, "n_phases": 4, "windows": [30, 45, 60, 90, 120],
             "share_min": 0.75}
    _vw_ok = {"status": "ok", "artifact": VOLWIN_JSON, "evidence_cutoff": "2026-10-30",
              "identity_all_pass": True, "criteria": _crit,
              "verdict": {"state": "ADOPT_WINDOW", "best_window": 30,
                          "best_phases_earned": 4, "best_phases_oos_not_worse": 4,
                          "phases_tested": 4, "windows": []},
              "phase_rows": [{"phase": 0, "phase_start": "2020-01-02", "window": 60,
                              "sharpe": 0.990},
                             {"phase": 0, "phase_start": "2020-01-02", "window": 30,
                              "sharpe": 1.057},
                             {"phase": 1, "phase_start": "2020-01-09", "window": 60,
                              "sharpe": 0.939},
                             {"phase": 1, "phase_start": "2020-01-09", "window": 30,
                              "sharpe": 1.082}]}
    _md_vw = _render_vw(_vw_ok)
    _vw_pair = dict(_vw_ok)
    _vw_pair["paired"] = {"arm": 30, "control": 60,
                          "verdict": {"state": "MIXED_ACROSS_PHASES"},
                          "rows": [{"phase": 0, "status": "ok", "mean_pp": 0.83,
                                    "ci_p05_p95_pp": [-0.10, 1.92], "share_positive": 0.925},
                                   {"phase": 1, "status": "ok", "mean_pp": 1.82,
                                    "ci_p05_p95_pp": [0.75, 3.12], "share_positive": 0.999}]}
    _vw_pair["older_face"] = {"status": "ok", "w_test": 20, "control_window": 60,
                              "median_delta_pp": 1.5, "median_delta_sharpe": 0.12,
                              "share_up": 1.0, "noise_pp": 1.81, "within_noise": True}
    _md_vwp = _render_vw(_vw_pair)
    chk("L76 vol window: the reader's own numbers reach the page",
        all(_x in _md_vw for _x in ("30 日", "4/4", "0.990", "1.057", "+0.067",
                                    "有窗口赢过在册值")),
        "")
    chk("L80 vol window: the paired band and the older face's own ruler reach the page",
        all(_x in _md_vwp for _x in ("MIXED_ACROSS_PHASES", "+0.83pp", "[-0.10, +1.92]",
                                     "within noise", "1.81pp", "+1.50pp"))
        and "0.83pp" not in _md_vw, "")
    chk("L77 vol window: the adoption names the grid edge and the exposure cost, and it "
        "does not silently rewrite the shipped config",
        "网格边缘" in _md_vw and "多拿" in _md_vw and "不改出货配置" in _md_vw, "")
    _vw_inert = dict(_vw_ok)
    _vw_inert["verdict"] = {"state": "WINDOW_INERT", "best_window": 45,
                            "best_phases_earned": 0, "best_phases_oos_not_worse": 4,
                            "phases_tested": 4, "windows": []}
    chk("L78 vol window: a different verdict prints a different sentence",
        "这条轴不承重" in _render_vw(_vw_inert)
        and "有窗口赢过在册值" not in _render_vw(_vw_inert), "")
    _md_vw_gone = _render_vw({"status": "missing", "artifact": VOLWIN_JSON})
    _md_vw_drift = _render_vw({"status": "drift", "artifact": VOLWIN_JSON})
    chk("L79 vol window: absent or a verdict that will not recompute reads 'cannot "
        "verify' and prints no arithmetic",
        "无法核验" in _md_vw_gone and "无法核验" in _md_vw_drift
        and "1.057" not in _md_vw_gone and "1.057" not in _md_vw_drift
        and "有窗口赢过在册值" not in _md_vw_drift, "")

    # r1207 / E324: the headline table is priced one bar in the future ------------------
    def _render_lk(lk):
        _p, _ = build(with_stress=False)
        _p["lookahead"] = lk
        return render_md(_p)
    _lk_ok = {"status": "ok", "artifact": LOOKAHEAD_JSON, "evidence_cutoff": "2026-10-30",
              "verdict": {"state": "LOOKAHEAD_PRESENT", "gap_pp_per_year": 1.14},
              "arms": {"published": {"cagr_pp": 9.60, "maxdd_pp": -11.77},
                       "causal": {"cagr_pp": 8.46, "maxdd_pp": -16.56},
                       "ledger_no_carry": {"cagr_pp": 8.53},
                       "ledger_carry": {"cagr_pp": 9.12}},
              "decomposition": {"price_of_the_one_bar_pp": 1.14, "mark_basis_pp": -0.07,
                                "carry_pp": 0.59},
              "lag_ladder": [{"lag": -2, "cagr_pp": 15.98}, {"lag": -1, "cagr_pp": 12.46},
                             {"lag": 0, "cagr_pp": 9.60}, {"lag": 1, "cagr_pp": 8.46},
                             {"lag": 5, "cagr_pp": 7.39}, {"lag": 20, "cagr_pp": 5.09}],
              "affected_faces": 33}
    _md_lk = _render_lk(_lk_ok)
    chk("L81 look-ahead: both numbers, the one-bar price and the ladder reach the page",
        all(_x in _md_lk for _x in ("9.60%", "8.46%", "1.14 pp", "-16.56%",
                                    "-2:+15.98", "+20:+5.09", "8.53%", "9.12%")), "")
    _lk_lines = "\n".join(lookahead_block(_lk_ok))
    chk("L82 look-ahead: the page names the causal ledger as the cross-check and "
        "the affected face count, and its own lines print no table-breaking pipe",
        "同一本书" in _lk_lines and "33" in _lk_lines and "|" not in _lk_lines, "")
    _md_lk_gone = _render_lk({"status": "missing", "artifact": LOOKAHEAD_JSON})
    _md_lk_drift = _render_lk({"status": "drift", "artifact": LOOKAHEAD_JSON})
    chk("L83 look-ahead: absent or a face whose rows no longer recompute reads 'cannot "
        "verify' and prints no arithmetic",
        "无法核验" in _md_lk_gone and "无法核验" in _md_lk_drift
        and "1.14 pp" not in _md_lk_gone and "1.14 pp" not in _md_lk_drift
        and "含一根 bar 的未来" not in _md_lk_drift, "")
    _lk_within = dict(_lk_ok)
    _lk_within["verdict"] = {"state": "WITHIN_TOL", "gap_pp_per_year": 0.05}
    chk("L84 look-ahead: a different verdict prints a different sentence",
        "时点差在容差内" in _render_lk(_lk_within)
        and "含一根 bar 的未来" not in _render_lk(_lk_within), "")

    # r1211: a point CAGR is one path through one history ------------------------------
    def _render_env(env):
        _p, _ = build(with_stress=False)
        _p["envelope"] = env
        return render_md(_p)
    _env_ok = {"status": "ok", "artifact": ENVELOPE_JSON, "evidence_cutoff": "2026-10-30",
               "block": 20, "n_resamples": 2000, "bars": 1652,
               "cagr": {"5": 0.0315, "50": 0.0956, "95": 0.1633},
               "maxdd": {"5": -0.2095, "50": -0.1323, "95": -0.0890},
               "sharpe": {"5": 0.364, "50": 0.974, "95": 1.589},
               "point": {"cagr": 0.096, "sharpe": 0.99, "maxdd": -0.1177},
               "point_pctile": {"cagr": 50.3, "sharpe": 51.6, "maxdd": 66.1},
               "shares": {"cagr_le_zero": 0.004, "maxdd_le_line": 0.064, "n_resamples": 2000},
               "reconciliation": "same_object"}
    _md_env = _render_env(_env_ok)
    chk("L85 envelope: the spread, the losing share and the drawdown-break share reach "
        "the page beside the point estimate",
        all(_x in _md_env for _x in ("3.15%", "9.56%", "16.33%", "-20.95%",
                                     "0.4%", "6.4%", "50.3")), "")
    _env_lines = "\n".join(envelope_block(_env_ok))
    _tbl = [ln for ln in envelope_block(_env_ok) if ln.startswith("|")]
    chk("L86 envelope: the page says the point estimate is a TYPICAL path, and its table "
        "is a well-formed header + separator + three rows",
        "典型" in _env_lines and "块长 20" in _env_lines and len(_tbl) == 5
        and all(ln.count("|") == 4 for ln in _tbl), str(len(_tbl)))
    _md_env_gone = _render_env({"status": "missing", "artifact": ENVELOPE_JSON})
    _md_env_drift = _render_env({"status": "drift", "artifact": ENVELOPE_JSON})
    chk("L87 envelope: absent or a face whose rows no longer recompute reads 'cannot "
        "verify' and prints no percentiles",
        "无法核验" in _md_env_gone and "无法核验" in _md_env_drift
        and "3.15%" not in _md_env_gone and "3.15%" not in _md_env_drift
        and "16.33%" not in _md_env_drift, "")
    _env_foreign = dict(_env_ok)
    _env_foreign["reconciliation"] = "different_object"
    chk("L88 envelope: a face describing another book is flagged BEFORE its numbers",
        "不是" in "\n".join(envelope_block(_env_foreign))
        and "different_object" in "\n".join(envelope_block(_env_foreign)), "")

    # r1212 / E328: the grid pushed below its old floor ----------------------------------
    _ve_ok = {"status": "ok", "artifact": VOLWIN_EDGE_JSON, "evidence_cutoff": "2026-10-30",
              "identity_all_pass": True, "published_window_stays": True,
              "criteria": {"windows": [5, 10, 15, 20, 25, 30, 60]},
              "edge": {"state": "EDGE_AT_FLOOR", "best_window": 20,
                       "best_mean_sharpe": 1.1113, "floor_window": 20,
                       "inactive_windows": [5, 10, 15],
                       "shipped": {"window": 60, "mean_sharpe": 0.9908},
                       "curve": [{"window": 20, "mean_sharpe": 1.1113},
                                 {"window": 25, "mean_sharpe": 1.1082},
                                 {"window": 30, "mean_sharpe": 1.0815},
                                 {"window": 60, "mean_sharpe": 0.9908}]},
              "verdict": {"state": "ADOPT_WINDOW"}, "paired": {"rows": [
                  {"phase": 0, "status": "ok", "mean_pp": 1.56,
                   "ci_p05_p95_pp": [0.4, 3.06], "share_positive": 0.987}],
                  "verdict": {"state": "MIXED_ACROSS_PHASES"}}}
    _md_ve = "\n".join(vol_window_edge_block(_ve_ok))
    chk("L89 window grid floor: the winner, the floor and the switched-off windows reach "
        "the page", all(_x in _md_ve for _x in ("20 日", "1.1113", "0.9908",
                                               "5d", "15d",
                                               "覆盖被关掉", "还在最边上")), "")
    chk("L90 window grid floor: the page says how many bars the engine needs before it "
        "will estimate at all, rather than calling the floor a tuned value",
        "最少" in _md_ve or "至少" in _md_ve, "")
    _ve_gone = {"status": "missing", "artifact": VOLWIN_EDGE_JSON}
    _ve_drift = {"status": "drift", "artifact": VOLWIN_EDGE_JSON,
                 "edge": {"state": "INTERIOR", "best_window": 20,
                          "best_mean_sharpe": 1.1113}}
    _md_ve_gone = "\n".join(vol_window_edge_block(_ve_gone))
    _md_ve_drift = "\n".join(vol_window_edge_block(_ve_drift))
    chk("L91 window grid floor: absent or drifted reads 'cannot verify' and prints no "
        "winner", "没法回答" in _md_ve_gone and "没法回答" in _md_ve_drift
        and "1.1113" not in _md_ve_gone and "1.1113" not in _md_ve_drift, "")
    _ve_interior = dict(_ve_ok)
    _ve_interior["edge"] = dict(_ve_ok["edge"], state="INTERIOR", inactive_windows=[])
    _md_ve_int = "\n".join(vol_window_edge_block(_ve_interior))
    chk("L92 window grid floor: a different position prints a different sentence and stops "
        "blaming the estimator", "拐弯" in _md_ve_int and "覆盖被关掉" not in _md_ve_int, "")

    # L93-L95 (r1216): the table's first row printed the ticket's own 683-bar return under a
    # 全窗 header. The block must read the face (not the numbers), say which window each cell
    # holds, and print "no row" -- never the short-window number -- when the face is absent
    # or its identity arm failed.
    _wl_ok = {"status": "ok", "artifact": WINDOW_LABEL_JSON, "evidence_cutoff": "2026-10-30",
              "verdict": {"state": "ROW_LABELED_BY_WINDOW", "gap_pp": 5.07},
              "rows": {"printed_under_full_header": {"cagr_pp": 12.78, "bars": 683},
                       "same_book_full_window": {"cagr_pp": 7.71, "bars": 1525}},
              "table_row": {"full": {"cagr_pct": 7.71, "sharpe": 1.34, "maxdd_pct": -5.78},
                            "oos": {"cagr_pct": 12.78, "sharpe": 1.73, "maxdd_pct": -5.78},
                            "full_window_bars": 1525, "short_window_bars": 683}}
    _md_wl_ok = "\n".join(window_label_block(_wl_ok))
    chk("L93 window label: the block prints both windows and their bar counts",
        "7.71" in _md_wl_ok and "12.78" in _md_wl_ok and "1525" in _md_wl_ok
        and "683" in _md_wl_ok and "5.07" in _md_wl_ok, "")
    _md_wl_gone = "\n".join(window_label_block({"status": "missing", "artifact": WINDOW_LABEL_JSON}))
    _md_wl_bad = "\n".join(window_label_block(
        {"status": "ok", "artifact": WINDOW_LABEL_JSON,
         "verdict": {"state": "IDENTITY_FAILED", "why": "identity arm drifted"},
         "rows": _wl_ok["rows"], "table_row": None}))
    chk("L94 window label: absent or identity-failed prints no window number at all",
        "7.71" not in _md_wl_gone and "7.71" not in _md_wl_bad
        and "12.78" not in _md_wl_gone and "12.78" not in _md_wl_bad, "")
    _p_wl, _ = build(with_stress=False)
    _p_wl["window_label"] = _wl_ok
    _md_page_ok = render_md(_p_wl)
    _first_row = [ln for ln in _md_page_ok.splitlines()
                  if ln.startswith("| 5 名·可执行单口径")]
    chk("L95 window label: the table row itself carries the full window in the full column",
        bool(_first_row) and "7.71%" in _first_row[0] and "12.78%" in _first_row[0]
        and _first_row[0].index("7.71%") < _first_row[0].index("12.78%"), _first_row[0][:80])

    _wl_mid = {"status": "ok", "artifact": WINDOW_LABEL_JSON,
               "evidence_cutoff": "2026-10-30",
               "verdict": {"state": "ROW_LABELED_BY_WINDOW", "gap_pp": 5.07},
               "rows": _wl_ok["rows"],
               "table_row": dict(_wl_ok["table_row"],
                                 **{"is": {"cagr_pct": 3.71, "sharpe": 0.90,
                                          "maxdd_pct": -3.97},
                                    "middle_window_bars": 842})}
    _p_wl2, _ = build(with_stress=False)
    _p_wl2["window_label"] = _wl_mid
    _md_wl2 = render_md(_p_wl2)
    _row2 = [ln for ln in _md_wl2.splitlines()
             if ln.startswith("| 5 \u540d")]
    chk("L96 window label: the middle window reaches the middle column when the face "
        "publishes it", bool(_row2) and "3.71%" in _row2[0]
        and _row2[0].index("7.71%") < _row2[0].index("3.71%")
        and _row2[0].index("3.71%") < _row2[0].index("12.78%"), _row2[0][:80] if _row2 else "")
    # L97: the legend is a function of the table, not of the last round. Build one page
    # whose first row has no middle cell (a dash must appear AND be explained) and one
    # whose row is complete (no dash -> no legend).
    _LEGEND = "\u8be5\u53e3\u5f84\u8fd9\u4e00\u683c"
    _p_leg, _ = build(with_stress=False)
    _p_leg["window_label"] = _wl_mid
    _row0 = next(iter(_p_leg["backtest_band"]))
    _p_leg["backtest_band"][_row0].pop("is", None)
    _md_leg_dash = render_md(_p_leg)
    _p_leg2, _ = build(with_stress=False)
    _p_leg2["window_label"] = _wl_mid
    _md_leg_full = render_md(_p_leg2)
    chk("L97 window label: a dash on the table brings its legend, and a table with no "
        "dash carries no legend",
        _LEGEND in _md_leg_dash and _LEGEND not in _md_leg_full, "")
    chk("L98 window label: the block names the middle window and the bars that tile "
        "the full one", "842" in _md_wl2 and "1525" in _md_wl2
        and "3.71" in "\n".join(window_label_block(_wl_mid)), "")
    # r1224 / E341: the reader is told to size off the declared arm ------------------------
    def _render_cr(cr):
        _p, _ = build(with_stress=False)
        _p["causal_rebuild"] = cr
        return render_md(_p)
    _cr_ok = {"status": "ok", "artifact": CAUSAL_REBUILD_JSON, "evidence_cutoff": "2026-10-30",
              "criteria": {"recovery_min_pp": 0.57},
              "verdict": {"state": "IRRECOVERABLE", "declared_cagr": 0.0846,
                          "best_recovered_pp": 0.07,
                          "arms": [{"arm": "smooth_k2", "recovered_pp": 0.07, "phase_wins": 3},
                                   {"arm": "smooth_k4", "recovered_pp": -0.71, "phase_wins": 2}]},
              "decomposition": {"total_pp": 0.07, "signal_pp": 0.06, "cost_pp": 0.01,
                                "turnover_declared": 0.953, "turnover_arm": 0.942},
              "audits": {"A3_rank_causality": {"ok": True}, "A4_factor_source": {"ok": True},
                         "A5_lags": {"ok": True}}}
    _md_cr = _render_cr(_cr_ok)
    chk("L99 causal rebuild: the page names the tested gap, the recovery that failed the "
        "line and where it came from (signal vs commission)",
        all(_x in _md_cr for _x in ("8.46", "+0.07", "0.57", "0.06", "0.01", "3/4")), "")
    _cr_bad = dict(_cr_ok)
    _cr_bad["audits"] = {"A3_rank_causality": {"ok": True}, "A4_factor_source": {"ok": False},
                         "A5_lags": {"ok": True}}
    chk("L100 causal rebuild: a failed mechanism audit is printed as a failure, never as a "
        "clean negative result",
        "有不过项" in "\n".join(causal_rebuild_block(_cr_bad)), "")
    _cr_gone = "\n".join(causal_rebuild_block({"status": "absent",
                                               "artifact": CAUSAL_REBUILD_JSON}))
    _cr_drift = "\n".join(causal_rebuild_block({"status": "drifted",
                                                "artifact": CAUSAL_REBUILD_JSON}))
    chk("L101 causal rebuild: an absent or drifted face reads 'cannot verify' and prints no "
        "arithmetic",
        "无法核验" in _cr_gone and "无法核验" in _cr_drift
        and "+0.07" not in _cr_gone and "+0.07" not in _cr_drift and "|" not in _cr_gone, "")
    _cr_lines = "\n".join(causal_rebuild_block(_cr_ok))
    chk("L102 causal rebuild: the block itself prints no table-breaking pipe",
        "|" not in _cr_lines and "捡不回来" in _cr_lines, "")
    # r1226 / E26: the gap channel is priced and printed where the rebuild answer is read ----
    _gp_ok = {"status": "ok", "artifact": GAP_JSON, "evidence_cutoff": "2026-10-30",
              "criteria": {"gap_min_pp": 0.57},
              "verdict": {"state": "MIXED_ACROSS_PHASES", "declared_cagr": 0.0846,
                          "best_arm": "excl_upgap_q80", "best_gained_pp": 0.81,
                          "arms": [{"arm": "excl_upgap_q80", "gained_pp": 0.81,
                                    "phase_wins": 2, "full_span_tests_pass": True},
                                   {"arm": "gap_rank_up", "gained_pp": -10.86,
                                    "phase_wins": 0, "full_span_tests_pass": False}]},
              "gap_stats": {"median_abs_gap_bp": 23.98, "mean_abs_gap_bp": 41.48,
                            "p90_abs_gap_bp": 97.45, "entry_bars": 83,
                            "excluded_names_per_decision": {"excl_upgap_q80": 145.1}},
              "audits": {"A6_fill_time_causality": {"ok": True},
                         "A7_declared_lag": {"ok": True},
                         "A8_mask_not_rescale": {"ok": True}}}
    _gp_lines = "\n".join(gap_block(_gp_ok))
    chk("L103 gap: the block names the tested arm, its gain, the line, the phase share and "
        "how big the channel actually is",
        all(_x in _gp_lines for _x in ("8.46", "+0.81", "0.57", "2/4", "23.98", "83")), "")
    _gp_bad = dict(_gp_ok)
    _gp_bad["audits"] = {"A6_fill_time_causality": {"ok": False},
                         "A7_declared_lag": {"ok": True}, "A8_mask_not_rescale": {"ok": True}}
    chk("L104 gap: a failed fill-time audit is printed as a failure, never as a clean negative",
        "有不过项" in "\n".join(gap_block(_gp_bad)), "")
    _gp_gone = "\n".join(gap_block({"status": "absent", "artifact": GAP_JSON}))
    _gp_drift = "\n".join(gap_block({"status": "drifted", "artifact": GAP_JSON}))
    chk("L105 gap: an absent or drifted face reads 'cannot verify' and prints no arithmetic",
        "无法核验" in _gp_gone and "无法核验" in _gp_drift
        and "+0.81" not in _gp_gone and "+0.81" not in _gp_drift and "|" not in _gp_gone, "")
    # L106-L108 (r1228): E25 and E26 each had their own section; E27 never appeared and the
    # three were never added up, so the page kept inviting a fourth question. The block reads
    # the roll-up from production (one implementation) and the three states must read apart --
    # and an unreadable face must not print arithmetic at all.
    _rx_closed = research_arc_face()
    _md_closed = "\n".join(research_arc_block(_rx_closed))
    _md_open = "\n".join(research_arc_block(
        {"verdict": "OPEN_LEVER", "rows": _rx_closed.get("rows") or [],
         "levers": ["E27:k2"], "missing": [], "cutoffs": ["2026-10-30"]}))
    _md_gone = "\n".join(research_arc_block({"verdict": "CANNOT_VERIFY", "rows": [],
                                             "missing": ["E25", "E26", "E27"]}))
    chk("L106 research arc: the live faces read three-for-three and print E27",
        _rx_closed.get("verdict") in ("CLOSED", "OPEN_LEVER")
        and _rx_closed.get("faces_read") == 3
        and "NO_SLICING_EDGE" in _md_closed and "E27" in _md_closed,
        str(_rx_closed.get("verdict")))
    chk("L107 research arc: a lever is named and never printed as 'three noes'",
        "E27:k2" in _md_open and "三问皆负" not in _md_open
        and "还没被采纳" in _md_open, "")
    chk("L108 research arc: unreadable faces print no arithmetic, only the gap",
        "无从判断" in _md_gone and "|" not in _md_gone and "+0.07" not in _md_gone, "")
    # L109-L111 (r1231): the page answered "how much" and "how deep" but never "how long".
    # The wait must come from the payload (not a constant typed here), a censored entry must
    # read as still-under-water rather than 0 bars, and an unreadable face must print the gap
    # instead of a number.
    _uw = underwater_face()
    _uw_md = "\n".join(underwater_block(_uw))
    _uw_wait = (_uw.get("recovery") or {}).get("max_bars")
    chk("L109 underwater: the live face is read and the worst wait is the payload's own number",
        _uw.get("status") == "ok" and _uw_wait is not None
        and ("%d 个交易日" % int(_uw_wait)) in _uw_md
        and "这笔钱真要等多久才能回本" in _uw_md,
        "status=%s max_bars=%s" % (_uw.get("status"), _uw_wait))
    _uw_cens = {"status": "ok", "artifact": "fake", "evidence_cutoff": "2026-01-01",
                "first_bar": "2020-01-01", "last_bar": "2026-01-01", "bars": 10,
                "recovery": {"entries": 3, "max_bars": 5.0, "median_bars": 1.0,
                             "p90_bars": 2.0, "censored": 2, "censored_share": 0.6667,
                             "worst_entry": {"entry_bar": "2025-01-02 00:00:00", "bars": 5,
                                             "recovered_bar": None}},
                "underwater": {"episodes": 1, "healed": 0, "never_healed": 1, "longest": {}},
                "forward": {}}
    _uw_cens_md = "\n".join(underwater_block(_uw_cens))
    chk("L110 underwater: an entry that never healed prints 'still under water', never 0 bars",
        "仍未回本" in _uw_cens_md and "不记 0" in _uw_cens_md
        and "0 个交易日**后才回本" not in _uw_cens_md, "")
    _uw_gone = "\n".join(underwater_block({"status": "absent", "artifact": UNDERWATER_JSON}))
    _uw_drift = "\n".join(underwater_block({"status": "drifted", "artifact": UNDERWATER_JSON}))
    chk("L111 underwater: an absent or drifted face reads 'cannot answer' and prints no table",
        "无法回答" in _uw_gone and "无法回答" in _uw_drift
        and "|" not in _uw_gone and "|" not in _uw_drift, "")
    print("\nSummary: %d/%d PASS%s" % (ok, total, "" if ok == total else " -- %d FAIL" % (total - ok)))
    return 0 if ok == total else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run":
        raise SystemExit(run())
    if cmd == "selftest":
        raise SystemExit(selftest())
    print("usage: etf_book_ceo_page.py [run|selftest]")
    raise SystemExit(2)