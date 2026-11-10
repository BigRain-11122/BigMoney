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
# r1233: every number on this page is measured on the 2020-2026 ETF boom. The card tests
# the same rule on the ETFs that already existed before it and says the alpha does not
# survive; the page never carried that sentence, so a reader sizing off it would believe
# the numbers are a property of the rule rather than of the window.
SPANNING_PRE2020_JSON = os.path.join(ROOT, "results", "etf_book_spanning_pre2020.json")
PRE2020_JSON = os.path.join(ROOT, "results", "etf_book_pre2020.json")
UNIVERSE_LOCK_JSON = os.path.join(ROOT, "results", "etf_book_universe_lock.json")
EXIT_LIQ_JSON = os.path.join(ROOT, "results", "etf_book_exit_liquidity.json")
FORCED_HOLD_JSON = os.path.join(ROOT, "results", "etf_book_forced_hold.json")
MIN_CAPITAL_JSON = os.path.join(ROOT, "results", "etf_book_min_capital.json")
# r1247: the whole universe is picked by one number -- a 20M median-turnover cut. Nobody had
# swept that number inside this book, so a reader could not tell whether it is a result or an
# inheritance, nor that what sits on it is the book's CAPACITY (how many names it may hold),
# not its return.
ENTRY_GATE_JSON = os.path.join(ROOT, "results", "etf_book_entry_gate.json")
# r1251: for a few hours every evening the daily panel is still a bar behind, and this page
# answered "what is the book worth" with yesterday's close. The snapshot face fills exactly
# that gap; the page must carry it, and must refuse it the moment its own rows stop
# reproducing it (a quote the chain gate would reject is not something to print here).
LIVE_QUOTE_DIR = os.path.join(ROOT, "results", "etf_book_live_quote")
# r1458: r1451-r1457 built a permission (how big this book is allowed to be), proved the
# order sheet can be trimmed to it, and stored the floor in a ledger. None of it reached
# THIS page, so the one face a human reads still sizes at the ordered k -- the page said
# buy CNY 459,796 while the executable sheet said only 392,616 is allowed.
PERMISSION_JSON = os.path.join(ROOT, "results", "etf_book_rebalance_permission.json")
CUT_GAP_JSON = os.path.join(ROOT, "results", "etf_book_cut_order_gap.json")
PERMISSION_LEDGER_JSON = os.path.join(ROOT, "results", "etf_book_floor_ledger.json")
PREMIUM_LEAK_JSON = os.path.join(ROOT, "results", "etf_book_premium_leak.json")
SIBLING_GAP_JSON = os.path.join(ROOT, "results", "etf_book_sibling_gap.json")
# r1470: r1468 wrote the executed book down and r1469 started accruing repo on its cash leg,
# but that account lived only in results/etf_book_positions.json -- the page kept telling the
# reader to buy the full sheet as if no lots were already held.
POSITIONS_JSON = os.path.join(ROOT, "results", "etf_book_positions.json")
# r1473: the page tells the reader how big the order may be but never WHY that number is
# that number. results/etf_book_floor_provenance.json answers it (the floor is beta_target
# divided by the largest measured beta) and results/etf_book_vol_target_gate.json kills the
# obvious follow-up ("then dial the book until it clears the calendar").
FLOOR_PROVENANCE_JSON = os.path.join(ROOT, "results", "etf_book_floor_provenance.json")
VOL_TARGET_GATE_JSON = os.path.join(ROOT, "results", "etf_book_vol_target_gate.json")
MACHINE = os.path.join(ROOT, "fleet", "machine.json")

# Single writer: the page is a plain-language mirror of shared artefacts, so two
# machines regenerating the same day would only produce a git race on docs/live_book.
# bm-a prints it; every other host says so and writes nothing (R31 lane-guard lineage).
HOST = "bm-a"
# r1387: a single writer that is not running is not a style, it is a stopped CEO product.
# bm-a's last heartbeat was 2026-11-05 21:26 and its page sat three trading days behind the
# ticket while every consumer leg downstream of the page went red on this host. Another host
# may take the pen, but only on a DECLARED silence measured from the owner's own heartbeat
# file, and the page says who wrote it and why -- a take-over that cannot be told apart from
# the owner writing is worse than the staleness.
TAKEOVER_SILENCE_H = 6.0


def machine_id():
    try:
        with open(MACHINE, encoding="utf-8-sig") as fh:
            return json.load(fh).get("machine_id")
    except Exception:
        return None


def owner_silence_hours():
    """Hours since the writer machine's own heartbeat. None = unknown, not silence.

    An unreadable heartbeat is the one case that must NOT authorize a take-over: "I cannot
    see the owner" and "the owner is gone" produce different actions everywhere else in this
    repo, and reading the first as the second is how a second writer appears (E378 lineage).
    """
    p = os.path.join(ROOT, "fleet", "machines", "%s.json" % HOST)
    try:
        with open(p, encoding="utf-8-sig") as fh:
            d = json.load(fh)
    except Exception:
        return None
    ts = d.get("last_seen") or d.get("ts")
    if not ts:
        return None
    try:
        seen = dt.datetime.fromisoformat(str(ts))
    except Exception:
        return None
    now = dt.datetime.now(seen.tzinfo) if seen.tzinfo else dt.datetime.now()
    return max(0.0, (now - seen).total_seconds() / 3600.0)


def takeover_authority(mid, silence_h=None):
    """None when `mid` may not write; otherwise the block that names the take-over."""
    if not mid or mid == HOST:
        return None
    h = owner_silence_hours() if silence_h is None else silence_h
    if h is None or h < TAKEOVER_SILENCE_H:
        return None
    return {"writer": mid, "owner": HOST, "owner_silent_h": round(float(h), 1),
            "took_over": True,
            "why": "%s has not written its own heartbeat for %.1f h (> %.0f h): its page faces "
                   "are stopped, not merely old" % (HOST, float(h), TAKEOVER_SILENCE_H)}


def writer_allowed(mid):
    return mid == HOST or takeover_authority(mid) is not None

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


def permission_face(perm_path=PERMISSION_JSON, gap_path=CUT_GAP_JSON,
                    ledger_path=PERMISSION_LEDGER_JSON):
    """How big this book is ALLOWED to be, against how big the list above orders (r1458).

    Three published receipts already hold this: the permission prices a floor from the
    sizing rulers, the cut-gap receipt turns that floor into integer lots to sell, and the
    floor ledger remembers the floor across rounds. This reader only reads them, and it
    refuses to print an obedience claim when two receipts quote different floors (two
    copies of one number is an E289 defect, not freshness). A missing receipt is UNKNOWN
    -- never a zero that would read as "no cut needed"."""
    perm = _load(perm_path) if os.path.exists(perm_path) else None
    gap = _load(gap_path) if os.path.exists(gap_path) else None
    led = _load(ledger_path) if os.path.exists(ledger_path) else None
    if not perm or perm.get("permitted_k") is None or perm.get("k_now") is None:
        return {"status": "unreadable",
                "artifact": _rel(perm_path, ROOT).replace(os.sep, "/"),
                "detail": "permission receipt absent or carries no permitted_k"}
    k_allowed = float(perm["permitted_k"])
    k_order = float(perm["k_now"])
    out = {
        "status": "ok",
        "artifact": _rel(perm_path, ROOT).replace(os.sep, "/"),
        "decision_date": perm.get("decision_date"),
        "ticket_file": perm.get("ticket_file"),
        "k_order": round(k_order, 6),
        "k_allowed": round(k_allowed, 6),
        "ordered_cny": perm.get("book_amount_cny"),
        "allowed_cny": perm.get("permitted_book_cny"),
        "over_cny": perm.get("cut_cny"),
        "over_pp": perm.get("cut_pp"),
        "keep_allowed": perm.get("keep_allowed"),
        "readings": {k: {"k": v.get("k"), "delta_pp": v.get("delta_vs_now_pp"), "kind": v.get("kind")}
                     for k, v in (perm.get("readings") or {}).items()},
        "naive_permits_keep": (perm.get("naive_max_over_all_readings") or {}).get("keep_allowed"),
        "trim": None,
        "cost": None,
        "floor_verdict": None,
        "floor_sentence": None,
        "floor_k": None,
        "k_schedule_last": None,
        "consistency": {},
    }
    # the trim: integer lots off the published gap receipt, never re-derived here
    tr = (gap or {}).get("trim") or {}
    if tr.get("legs"):
        out["trim"] = {
            "legs": [{"symbol": l.get("symbol"), "price": l.get("price"),
                      "lots_now": l.get("lots_now"), "lots_target": l.get("lots_target"),
                      "lots_sell": l.get("lots_sell"), "sell_cny": l.get("sell_cny")}
                     for l in tr["legs"]],
            "lots_total": tr.get("lots_sell_total"),
            "sold_cny": tr.get("sold_cny"),
            "k_after": tr.get("k_after_integer_lots"),
            "within": tr.get("trim_within_permission"),
            "basis": tr.get("basis"),
        }
        out["cost"] = {k: (gap.get("cost") or {}).get(k)
                       for k in ("cost_bp_per_side", "tx_cny_one_side", "carry_cny_per_year",
                                 "repo_rate_pct", "repo_rate_date")}
        gu = (gap.get("cost") or {}).get("giveup_cny_per_year_ex_post") or {}
        out["cost"]["give_up_book_realized"] = gu.get("book_realized")
        out["cost"]["give_up_at_benchmark"] = gu.get("same_beta_benchmark")
    # the ledger: what the floor's own memory says about the NEXT decision bar
    asd = (led or {}).get("assessed") or {}
    if asd:
        out["floor_verdict"] = asd.get("verdict")
        out["floor_k"] = asd.get("floor")
        out["k_schedule_last"] = asd.get("k_schedule_last")
        out["schedule_last_date"] = asd.get("schedule_last_date")
        out["floor_action"] = asd.get("action")
        out["floor_sentence"] = (led or {}).get("sentence")
        out["floor_issued"] = asd.get("floor_issued")
        rows = (led or {}).get("rows") or []
        if rows:
            out["floor_ledger_issued_at"] = rows[-1].get("issued_at")
    # two receipts quoting the same floor must agree, or the page says so instead of obeying
    cons = out["consistency"]
    if gap and gap.get("permitted_k") is not None:
        cons["permission_vs_gap"] = abs(float(gap["permitted_k"]) - k_allowed) < 1e-6
    if out["floor_k"] is not None:
        cons["permission_vs_ledger"] = abs(float(out["floor_k"]) - k_allowed) < 1e-6
    cons["agree"] = all(cons.get(k) is not False for k in
                        ("permission_vs_gap", "permission_vs_ledger"))
    return out


def permission_block(pf):
    """The lines this page prints about the size limit behind the list above."""
    L = []
    add = L.append
    add("## 这张单能下多大（额度）")
    add("")
    pf = pf or {}
    if pf.get("status") != "ok":
        add("这一节读不到额度面（`%s`）：%s。**上面那张清单没有经过额度检查**——"
            "它可能是按规则算出来的仓位，也可能是超过额度的仓位，本页分不出来。"
            % ((pf.get("artifact") or "results/etf_book_rebalance_permission.json"),
               pf.get("detail") or "无读数"))
        add("")
        return L
    if pf.get("consistency", {}).get("agree") is False:
        add("**两张收据对同一个额度报了不同的数**（%s）——本页不宣称这张单守住了额度。"
            % json.dumps(pf.get("consistency"), ensure_ascii=False))
        add("")
        return L
    allowed = pf.get("allowed_cny")
    ordered = pf.get("ordered_cny")
    over = pf.get("over_cny")
    add("- 允许的仓位：**k=%.6f**（风险腿 ¥%s）；上面那张清单下的仓位：k=%.6f（¥%s）"
        % (pf["k_allowed"], format(allowed or 0, ",.0f"), pf["k_order"], format(ordered or 0, ",.0f")))
    if over and over > 0:
        add("- 所以上面那张表**超出额度 ¥%s（%.2f 个百分点）**，它不是可以照着下的单。"
            % (format(over, ",.0f"), pf.get("over_pp") or 0.0))
    else:
        add("- 这张单没有超过额度。")
    tr = pf.get("trim") or {}
    if over and over > 0 and tr.get("legs"):
        add("")
        add("按额度执行要这样卖（整数手，卖出后 k=%.6f）：" % (tr.get("k_after") or 0.0))
        add("")
        add("| 代码 | 价 | 现在手数 | 目标手数 | 卖出手数 | 卖出 ¥ |")
        add("|---|---|---|---|---|---|")
        for l in tr["legs"]:
            add("| %s | %s | %s | %s | %s | %s |"
                % (l["symbol"], l["price"], format(l["lots_now"] or 0, ","),
                   format(l["lots_target"] or 0, ","), format(l["lots_sell"] or 0, ","),
                   format(l["sell_cny"] or 0, ",.0f")))
        add("| — | **合计** | | | **%s 手** | **¥%s** |"
            % (format(tr.get("lots_total") or 0, ","), format(tr.get("sold_cny") or 0, ",.0f")))
        add("")
        if tr.get("basis"):
            add("- 读法：%s" % tr["basis"])
        _tgt_cny = sum((l.get("lots_target") or 0) * 100 * float(l.get("price") or 0)
                       for l in tr["legs"])
        add("- 今天才建仓的话：照「目标手数」那一列买（%s 手），实际投入 **¥%s**——"
            "与额度的差是整手取整（欠投留在现金腿，不重分配）。"
            % ("/".join(format(l.get("lots_target") or 0, ",") for l in tr["legs"]),
               format(_tgt_cny, ",.0f")))
        if tr.get("within") is False:
            add("- ⚠ 这张裁剪表本身没有落回额度内，不许照它下单。")
        cost = pf.get("cost") or {}
        if cost.get("tx_cny_one_side") is not None:
            bits = ["一次卖出成本 ¥%s（%s bp/边）" % (format(cost["tx_cny_one_side"], ",.2f"),
                                                   cost.get("cost_bp_per_side"))]
            if cost.get("carry_cny_per_year") is not None:
                bits.append("少拿一年逆回购利息 ¥%s（按 %s%% 报价）"
                            % (format(cost["carry_cny_per_year"], ",.0f"),
                               cost.get("repo_rate_pct")))
            if cost.get("give_up_book_realized") is not None:
                bits.append("如果这条袖继续按自己实现过的收益走，一年少赚 ¥%s（按同 β 基准算只有 ¥%s）"
                            % (format(cost["give_up_book_realized"], ",.0f"),
                               format(cost.get("give_up_at_benchmark") or 0, ",.0f")))
            add("- 守额度的代价：%s。" % "；".join(bits))
    elif over and over > 0:
        add("- 裁剪表读不到（`results/etf_book_cut_order_gap.json` 缺席）：知道超了 ¥%s，但不知道该卖多少手。"
            % format(over, ",.0f"))
    fv = pf.get("floor_verdict")
    if fv:
        zh = {"REAPPLY_REQUIRED": "**这张单守住了，但排程没有**：下一张单会重新超额度，除非在那根决策 bar 上重新裁一次",
              "HOLDING": "**仓位本身就在额度之下**，没有需要修剪的东西",
              "NOT_ENFORCED": "**这张单也没有守住额度**",
              "REISSUE_REQUIRED": "**额度是按一张已经被取代的票定的**，要重新签发"}.get(fv, "**%s**" % fv)
        add("")
        add("- 地板台账（`results/etf_book_floor_ledger.json`）：%s。" % zh)
        if pf.get("floor_sentence"):
            add("- 台账原话：%s" % pf["floor_sentence"])
        if pf.get("k_schedule_last") is not None:
            add("- 地板 k=%.6f（签给 %s 这一次换仓）；排程最后一根决策 bar k=%.6f（%s）。"
                % (pf.get("floor_k") or 0.0, pf.get("floor_issued") or "—",
                   pf.get("k_schedule_last") or 0.0, pf.get("schedule_last_date") or "—"))
    # the trap that a "keep it" reading falls into
    rd = pf.get("readings") or {}
    path_rows = [(k, v) for k, v in rd.items() if v.get("kind") == "path"]
    if path_rows:
        add("")
        add("- 额度没采用的读数（同一规则、同一面板，只换尺子）：%s。"
            % "；".join("%s k=%.6f (%+.2fpp)" % (k, v["k"], v.get("delta_pp") or 0.0)
                        for k, v in path_rows))
        if pf.get("naive_permits_keep"):
            add("- 如果拿「所有读数里最宽的那个」当许可，就会得出「可以不动」——这正是这一节要拦的那一步。")
    add("")
    return L


def premium_face(path=PREMIUM_LEAK_JSON):
    """What the order pays ABOVE the basket it buys (r1463).

    Reads the published face only. Two rules carried here: an absent face is "cannot
    verify" (never a clean zero), and a face priced on a different session than the page's
    own bar is a mismatch, not freshness."""
    if not os.path.exists(path):
        return {"status": "unreadable",
                "artifact": _rel(path, ROOT).replace(os.sep, "/"),
                "detail": "premium-leak face absent"}
    f = _load(path) or {}
    if f.get("status") != "ok":
        return {"status": "unreadable",
                "artifact": _rel(path, ROOT).replace(os.sep, "/"),
                "detail": "face status %r: %s" % (f.get("status"), f.get("note") or "")}
    tot = f.get("totals") or {}
    out = {
        "status": "ok",
        "artifact": _rel(path, ROOT).replace(os.sep, "/"),
        "session": f.get("iopv_session"),
        "ticket_session": f.get("ticket_session"),
        "session_match": f.get("session_match"),
        "verdict": f.get("verdict"),
        "verdict_reason": f.get("verdict_reason"),
        "names": f.get("names") or [],
        "totals": tot,
        "premium_names": f.get("premium_names") or [],
        "stress": f.get("stress") or {},
        "rulers": f.get("rulers") or {},
        "nav_ruler_history": f.get("nav_ruler_history") or {},
        "criteria": f.get("criteria") or {},
    }
    return out


def premium_board_gap(now=None):
    """(r1505) Which trading sessions the IOPV board behind this section never captured.

    Why the page needs it: the section above dates itself ("rate day 11-06, price day
    11-09") but a reader cannot tell WHY the rate is old, or whether it will catch up.
    The board is a realtime print taken after the close, so a missed session is not
    late -- it is gone. Single implementation lives in etf_premium_face.board_gap();
    this wrapper only carries the reading to the page (E289: no second copy)."""
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        import etf_premium_face as _epf
        return dict(_epf.board_gap(now=now))
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unavailable", "detail": str(exc)[:160]}


def premium_board_gap_lines(gap):
    """The two-to-three lines this page prints about the board's own holes."""
    L = []
    add = L.append
    gap = gap or {}
    st = gap.get("status")
    if st == "unavailable":
        add("- 这块板缺没缺日子，本页核验不了（%s）——不写成「没有缺口」。" % (gap.get("detail") or "无读数"))
        return L
    if st == "unreadable_calendar":
        add("- 这块板的完整性核验不了：官方交易日历读不出来，所以「缺了几天」是**未知**，"
            "不是零。下一次能抓：**%s**。" % (gap.get("next_capture_session") or "—"))
        return L
    miss = gap.get("missing")
    if miss is None:
        return L
    nxt = gap.get("next_capture_session") or "—"
    after = gap.get("next_capture_after")
    when = ("**%s %s 之后**" % (nxt, after)) if after else ("**%s**（现在就能抓）" % nxt)
    if miss:
        add("- **这块板缺了 %d 个交易日：%s。** 它是**收盘后抓一次的实时快照**，不是能回头补的"
            "历史序列——缺掉的那天重跑也拍不回来，所以上面这些数会一直停在 **%s**，"
            "等到下一次收盘后有人跑一次 `etf_premium_face.py fetch`。下一次能同日报价：%s。"
            % (len(miss), "、".join(miss), gap.get("last_board") or "—", when))
    else:
        add("- 这块板从 **%s** 起每个交易日都有，没有缺口（现在的读数就是最新收盘）；"
            "下一次抓取：%s。" % (gap.get("coverage_starts") or "—", when))
    return L


def premium_on_page_sheet(pb, page_sheet, tol_cny=100.0, tol_pct=0.5):
    """(r1503) What THIS page's sheet pays above IOPV, at the face's own premium rates.

    Why it exists: the published face is priced against the sheet that was executable when
    it ran. This page's sheet has since been trimmed by the permission floor (k 0.460 ->
    0.393), so the face's "share of the order" is 9.07% of a DIFFERENT order than the one
    the reader is looking at -- two yuan totals on one page, neither labelled, which is the
    defect the card ledger calls "one book, two sheets of paper".

    It is a recomputation, not a rescale: each name's premium rate is the face's, each
    name's weight is the page's, and both provenances are printed. A name on the page with
    no rate in the face is counted as unverifiable and stays OUT of the sum (never a zero).
    Returns None when there is nothing to say -- no page sheet, or the two sheets are the
    same sheet.
    """
    ps = page_sheet or {}
    legs = [l for l in (ps.get("legs") or []) if l and l.get("symbol")]
    amt = ps.get("amount_cny")
    tot = pb.get("totals") or {}
    face_amt = tot.get("book_amount_cny")
    if not legs or amt is None or face_amt is None:
        return None
    amt = float(amt)
    face_amt = float(face_amt)
    if abs(amt - face_amt) <= max(tol_cny, abs(face_amt) * tol_pct / 100.0):
        return None
    rate = {}
    for r in (pb.get("names") or []):
        if r.get("symbol") and r.get("status") == "OK" and r.get("premium_pct") is not None:
            rate[r["symbol"]] = float(r["premium_pct"])
    out = {"page_amount_cny": round(amt, 2), "face_amount_cny": round(face_amt, 2),
           "face_session": pb.get("session"), "rows": [], "unverifiable": [],
           "paid_cny": 0.0, "n_rows": 0}
    for l in legs:
        a = l.get("amount_cny")
        sym = l["symbol"]
        if a is None:
            out["unverifiable"].append(sym)
            continue
        p = rate.get(sym)
        if p is None:
            out["unverifiable"].append(sym)
            continue
        paid = float(a) * p / 100.0
        out["rows"].append({"symbol": sym, "amount_cny": round(float(a), 2),
                            "premium_pct": p, "premium_cny": round(paid, 2)})
        out["paid_cny"] += paid
        out["n_rows"] += 1
    out["paid_cny"] = round(out["paid_cny"], 2)
    if out["n_rows"] == 0:
        out["share_of_page_pct"] = None
    else:
        out["share_of_page_pct"] = round(100.0 * out["paid_cny"] / amt, 4) if amt else None
    nav = tot.get("nav_cny")
    out["share_of_nav_pct"] = (round(100.0 * out["paid_cny"] / float(nav), 4)
                               if nav else None)
    cagr = tot.get("book_cagr_pct")
    if cagr:
        out["years_of_backtest_return_paid"] = round(
            out["share_of_page_pct"] / float(cagr), 4) if out.get("share_of_page_pct") else None
    return out


def premium_block(pb, page_bar=None, page_sheet=None, board_gap=None):
    """The lines this page prints about what the order pays above the basket."""
    L = []
    add = L.append
    add("## 这张单买的东西本身值多少（溢价）")
    add("")
    gap = premium_board_gap() if board_gap is None else board_gap
    pb = pb or {}
    if pb.get("status") != "ok":
        add("这一节读不到溢价面（`%s`）：%s。**上面那张清单因此没有经过溢价检查**——"
            "按什么价格买到多少篮子价值，本页分不出来。" % (
                (pb.get("artifact") or "results/etf_book_premium_leak.json"),
                pb.get("detail") or "无读数"))
        add("")
        for line in premium_board_gap_lines(gap):
            add(line)
        add("")
        return L
    if page_bar and pb.get("session") and str(page_bar)[:10] != str(pb["session"])[:10]:
        add("溢价面是按 **%s** 的 IOPV 算的，本页的价是 **%s**——两个日子对不上，"
            "下面这些数不能直接搬到今天的单上。" % (pb["session"], page_bar))
        add("")
    for line in premium_board_gap_lines(gap):
        add(line)
        add("")
    tot = pb.get("totals") or {}
    paid = tot.get("premium_paid_cny") or 0.0
    share = tot.get("premium_share_of_order_pct")
    share_nav = tot.get("premium_share_of_nav_pct")
    # r1503: the face is priced on ITS sheet, this page prints ANOTHER one (the floor
    # trimmed it since). Say which sheet the sentence is about before a reader subtracts
    # two yuan totals that were never meant to match.
    onpage = premium_on_page_sheet(pb, page_sheet)
    top = [r for r in pb.get("names") or [] if r.get("status") == "OK"
           and (r.get("market_pctile") or 0.0) >= ((pb.get("criteria") or {}).get("top_pctile") or 95.0)]
    sentence = ("清单上 **¥%s** 的单里，有 **¥%s** 买的是**溢价**（价格高出这只 ETF 自己一篮子资产的部分），"
                "不是篮子的价值" % (format(tot.get("book_amount_cny") or 0, ",.0f"),
                                   format(paid, ",.0f")))
    if onpage:
        sentence = ("溢价面自己那张单 **¥%s** 里，有 **¥%s** 买的是**溢价**（价格高出这只 ETF "
                    "自己一篮子资产的部分），不是篮子的价值" %
                    (format(onpage["face_amount_cny"], ",.0f"), format(paid, ",.0f")))
    if share is not None:
        sentence += ("——占它那张单的 **%.2f%%**" if onpage else "——占这张单的 **%.2f%%**") % share
    if share_nav is not None:
        sentence += "、占总资金的 **%.2f%%**" % share_nav
    # r1504: the sentence already bolds its own amounts. Wrapping it in another ** made the
    # rendered page break the bold at the first inner marker ("那张单 **￥459,796** 里"), so the
    # one line a reader sees first read as a typo. Bold lives inside the sentence only.
    add("%s。" % sentence)
    add("")
    if top:
        add("其中 %d 只票站在全市场 **%d** 只 ETF 溢价的最高 5%% 里（%s）。"
            % (len(top), (top[0].get("market_n") or 0),
               "、".join("%s 第 %s" % (r["symbol"], r.get("market_rank")) for r in top)))
        add("")
    # r1504: the dates go INTO the table header. A sentence above the table can be skipped,
    # and the row a reader copies carries no date of its own -- so "which day is this rate
    # from" has to travel with each column, not sit in prose. Every column here (price,
    # IOPV, premium, rank) comes from the face's own session; the page's sheet prices are
    # a different day, and the header says which one this table is.
    _face_ds = str(pb.get("session"))[:10] if pb.get("session") else "—"
    _page_ds = str(page_bar)[:10] if page_bar else "—"
    if page_bar and pb.get("session") and _page_ds != _face_ds:
        add("本表每一列——价格、IOPV、溢价率、全市场排名——都是 **%s** 那一天的读数；"
            "本页这张单的价是 **%s** 的。一张表只装一个日子。" % (_face_ds, _page_ds))
        add("")
    add("| 代码 | 类别 | 参考价（%s） | 同一日的 IOPV（%s） | 溢价 | 买溢价 ¥ | 全市场排名 |"
        % (_face_ds, _face_ds))
    add("|---|---|---|---|---|---|---|")
    for r in pb.get("names") or []:
        if r.get("status") == "OK":
            add("| %s | %s | %s | %s | %+.2f%% | %s | %s/%s |"
                % (r["symbol"], r.get("class") or "", r.get("price"), r.get("iopv"),
                   r.get("premium_pct") or 0.0, format(r.get("premium_paid_cny") or 0, ",.2f"),
                   r.get("market_rank"), r.get("market_n")))
        else:
            add("| %s | %s | %s | — | — | 无法核验（%s） | — |"
                % (r.get("symbol"), r.get("class") or "", r.get("price"), r.get("status")))
    add("| — | **合计** | | | | **¥%s** | |"
        % format(paid, ",.2f"))
    add("")
    if tot.get("n_unverifiable"):
        add("- %d 只票这一天没有 IOPV 读数，上面的合计**不含**它们——是「查不到」，不是「没有溢价」。"
            % tot["n_unverifiable"])
    if onpage:
        add("")
        add("**按本页这张单重算**（份数×价取本页，溢价率取 %s 那次读数）：**¥%s**，"
            "占本页这张单 **%s%%**、总资金 **%s%%**——这才是你手上这张单要付的溢价。"
            % (onpage.get("face_session") or "溢价面那一次",
               format(onpage["paid_cny"], ",.0f"),
               "—" if onpage.get("share_of_page_pct") is None
               else "%.2f" % onpage["share_of_page_pct"],
               "—" if onpage.get("share_of_nav_pct") is None
               else "%.2f" % onpage["share_of_nav_pct"]))
        add("")
        add("- 两张单不是一回事：溢价面那张 **¥%s**、本页这张 **¥%s**。两个金额并列，不许相加，"
            "也不许拿上面那个百分之几套到本页的 ¥ 上。"
            % (format(onpage["face_amount_cny"], ",.0f"),
               format(onpage["page_amount_cny"], ",.0f")))
        add("")
        add("| 代码 | 本页金额（%s 价） | 溢价率（%s 读数） | 买溢价 ¥ |" % (_page_ds, _face_ds))
        add("|---|---|---|---|")
        for r in onpage["rows"]:
            add("| %s | ¥%s | %+.2f%% | %s |"
                % (r["symbol"], format(r["amount_cny"], ",.0f"), r["premium_pct"],
                   format(r["premium_cny"], ",.2f")))
        add("| — | **合计** | | **¥%s** |" % format(onpage["paid_cny"], ",.2f"))
        add("")
        if onpage.get("unverifiable"):
            add("- %s 在本页这张单上没有可配的溢价率（溢价面那天没读到它的 IOPV）——"
                "上面的合计**不含**它们，是「查不到」，不是「没有溢价」。"
                % "、".join(onpage["unverifiable"]))
            add("")
    st = pb.get("stress") or {}
    if st.get("if_premium_reverts_to_zero_cny") is not None:
        add("- 如果溢价回落到 0（限购放开、套利关门被打开），这一笔就是 **¥%s** 的损失，"
            "占总资金 %s%%——溢价不是手续费，它是一笔押在「别人继续愿意多付」上的钱。"
            % (format(st["if_premium_reverts_to_zero_cny"], ",.0f"),
               st.get("if_premium_reverts_to_zero_pct_of_nav")))
    if tot.get("years_of_backtest_return_paid") is not None:
        add("- 换个说法：按这本书自己回测的 %.2f%%/年，这一次入场先付出了 **%.2f 年**的收益。"
            % (tot.get("book_cagr_pct") or 0.0, tot["years_of_backtest_return_paid"]))
    add("- 但溢价可以长期存在——限购让一二级套利关不上门，这类 ETF 常年溢价。所以这不是卖出的理由，"
        "是「这张单今天不便宜」的读数。")
    hist = pb.get("nav_ruler_history") or {}
    if hist:
        rows = [v for v in hist.values() if (v or {}).get("status") == "OK"]
        thin = [v for v in hist.values() if (v or {}).get("status") != "OK"]
        if rows:
            add("- **另一把尺子（收盘价 ÷ 已披露单位净值 − 1）**：%s。它和上面不是同一个量"
                "（净值晚一天披露），并列放着不许相加。"
                % "；".join("%s 中位 %+.2f%%（%d 次观测）" % (r["symbol"], r["median_pct"], r["n_obs"])
                           for r in rows))
        if thin:
            add("- %s 在这把尺子上没有够用的历史观测（少于 %s 次），所以「今天这个溢价算不算高」"
                "本页答不了——只能答「今天买它要付多少」。" % (
                    "、".join(t.get("symbol") or "?" for t in thin),
                    (pb.get("criteria") or {}).get("min_history_obs")))
    add("")
    add("- 机器判词（`%s`）：**%s** — %s。" % (pb.get("artifact"), pb.get("verdict"),
                                              pb.get("verdict_reason")))
    add("")
    return L


# r1502: the section above says what the order PAYS above IOPV. The operator's next question
# is what the price did after paying it, and that answer already exists in
# results/etf_premium/PREMIUM-FORWARD.json -- cut to this sheet's own legs by
# etf_book_order.premium_read (r1501). Importing that function instead of parsing the face
# here is the point: two human faces may not disagree about a number neither of them
# computes (E509 family; the ORDER sheet and this page must print the same rows).
PREMIUM_FORWARD_JSON = os.path.join(ROOT, "results", "etf_premium", "PREMIUM-FORWARD.json")


def premium_forward_face(ticket=None, results_dir=None):
    """What these funds' own records did after a premium reading like today's.

    Single implementation: the rows, the verdict word and the money column come out of
    `etf_book_order.premium_read`, the same call the ORDER sheet renders from. This face
    only carries that block up to the page; it re-derives nothing and types no word.
    """
    art = _rel(PREMIUM_FORWARD_JSON, ROOT).replace(os.sep, "/")
    try:
        _sd = os.path.dirname(os.path.abspath(__file__))
        if _sd not in sys.path:
            sys.path.insert(0, _sd)
        import etf_book_order as _obo
        pr = _obo.premium_read(ticket or {}, None, results_dir=results_dir)
    except Exception as exc:  # an unreadable producer is a status, never a crashed page
        return {"status": "unreadable", "artifact": art,
                "detail": "premium_read failed: %s" % exc}
    if pr.get("fwd_status") != "produced":
        return {"status": "unreadable", "artifact": art,
                "detail": "forward face %s" % (pr.get("fwd_status") or "missing")}
    return {"status": "ok", "artifact": art,
            "face_asof": pr.get("fwd_face_asof"), "stale": pr.get("fwd_stale"),
            "verdict": pr.get("fwd_verdict"), "horizon": pr.get("fwd_horizon"),
            "sentence": pr.get("fwd_sentence"), "caveat": pr.get("fwd_caveat"),
            "rows": list(pr.get("fwd_rows") or []),
            "missing_legs": list(pr.get("fwd_missing_legs") or []),
            "cny_total": pr.get("fwd_cny_total")}


def premium_forward_block(pf, page_bar=None):
    """The lines this page prints about what the price did after such a reading."""
    L = []
    add = L.append
    add("## 付了溢价之后，这些基金自己的价格怎么走")
    add("")
    add("（上一节说的是**今天多付了多少**，这一节说的是**付过之后，这只基金自己在同样处境下的历史里怎么走**"
        "——两个问题、两个数，不许相加。）")
    add("")
    pf = pf or {}
    if pf.get("status") != "ok":
        add("这一条**还没被量过**（`%s` 读不到：%s）。没测不等于没问题——它只是说这条路还没有人量过。"
            % (pf.get("artifact") or "results/etf_premium/PREMIUM-FORWARD.json",
               pf.get("detail") or "无读数"))
        add("")
        return L
    if page_bar and pf.get("face_asof") and str(page_bar)[:10] != str(pf["face_asof"])[:10]:
        add("这张读数按 **%s** 的票面算，本页价的日期是 **%s**——两个日子对不上，下面这些数不能直接搬到今天的单上。"
            % (pf["face_asof"], page_bar))
        add("")
    h = pf.get("horizon") or "?"
    add("| 代码 | 今日档位 | 同档此后 %s 个交易日均涨 | 观测 | t | 本单金额 | 同档折成钱 |" % h)
    add("|---|---|---|---|---|---|---|")
    for r in pf.get("rows") or []:
        add("| %s | %s | %+.2f%% | %s | %+.1f | %s | %s |"
            % (r.get("symbol"), r.get("bucket") or "?",
               float(r.get("mean_pct") or 0.0), r.get("n") or 0, float(r.get("t") or 0.0),
               format(r.get("amount_cny") or 0, ",.0f"),
               ("%+.0f" % float(r["same_bucket_move_cny"]))
               if r.get("same_bucket_move_cny") is not None else "—"))
    tot = pf.get("cny_total")
    add("| — | | | | | **合计** | **%s** |"
        % (format(float(tot), "+,.0f") if tot is not None else "—"))
    add("")
    if pf.get("missing_legs"):
        add("- %s 在这张面上没有读数——是「没量过」，不是「没有漂移」。"
            % "、".join(pf["missing_legs"]))
    add("- 判词 **%s**：%s" % (pf.get("verdict") or "?", pf.get("sentence") or ""))
    if pf.get("caveat"):
        add("- %s" % pf["caveat"])
    add("- 出处：`%s`（scripts/etf_book_premium_forward.py 单一生产者；按本票的腿裁剪由 "
        "scripts/etf_book_order.py 的 premium_read 完成，票面与本页同源）。" % pf.get("artifact"))
    add("")
    return L


SIBLING_GAP_WORDS = {
    "PERSISTENT_GAP": "长期收的",
    "EPISODIC_GAP": "今天才有",
    "NO_GAP": "今天没有价差",
    "AMBIGUOUS_GAP": "读不出方向",
    "INSUFFICIENT_HISTORY": "历史太短，读不出",
    "CANNOT_VERIFY": "无法核验",
}


def sibling_gap_face(path=SIBLING_GAP_JSON):
    """Whether today's sibling premium gap is a rate or an episode (r1465).

    Read-only over the published face. An absent face is "cannot verify" -- never "the gap
    repeats" -- and a face anchored on another session is a mismatch, not freshness."""
    if not os.path.exists(path):
        return {"status": "unreadable", "artifact": _rel(path, ROOT).replace(os.sep, "/"),
                "detail": "sibling-gap face absent"}
    f = _load(path) or {}
    if not f.get("pairs"):
        return {"status": "unreadable", "artifact": _rel(path, ROOT).replace(os.sep, "/"),
                "detail": "face carries no priced pair"}
    return {
        "status": "ok",
        "artifact": _rel(path, ROOT).replace(os.sep, "/"),
        "session": f.get("session"),
        "pairs": f.get("pairs") or [],
        "skipped_legs": f.get("skipped_legs") or [],
        "sentence": f.get("sentence"),
        "today_gain_cny": f.get("today_gain_cny"),
        "repeatable_gain_cny": f.get("repeatable_gain_cny"),
        "one_off_gain_cny": f.get("one_off_gain_cny"),
        "immaterial_gain_cny": f.get("immaterial_gain_cny"),
        "criteria": f.get("criteria") or {},
        "caveats": f.get("caveats") or [],
    }


def sibling_gap_block(sg, page_bar=None):
    """The lines this page prints about whether the swap saving repeats."""
    L = []
    add = L.append
    add("## 这个价差是长期收的，还是今天才有的")
    add("")
    sg = sg or {}
    if sg.get("status") != "ok":
        add("这一节读不到价差历史面（`%s`）：%s。**因此本页只有今天的价差，说不出它会不会天天有**——"
            "把今天的一次价差当成长期成本，和把它当成可以永远重复的收益，都是本页现在不能支持的说法。"
            % (sg.get("artifact") or "results/etf_book_sibling_gap.json", sg.get("detail") or "无读数"))
        add("")
        return L
    if page_bar and sg.get("session") and str(page_bar)[:10] != str(sg["session"])[:10]:
        add("价差历史面是拿 **%s** 的盘口锚定的，本页的价是 **%s**——两个日子对不上，"
            "下面这些历史分位不能搬到今天的单上。" % (sg["session"], page_bar))
        add("")
    today = sg.get("today_gain_cny") or 0.0
    rep = sg.get("repeatable_gain_cny") or 0.0
    one = sg.get("one_off_gain_cny") or 0.0
    if today:
        add("**同一笔钱换只票能多买 ￥%s 的篮子，其中按历史平均价差只算得上 ￥%s 是「以后还能再拿到」的，"
            "剩下 ￥%s 是今天这一次。**" % (format(today, ",.0f"), format(rep, ",.0f"), format(one, ",.0f")))
        add("")
    add("| 这只票 | 换到 | 今天价差 | 历史平均 | 多少交易日 | 今天分位 | 读法 |")
    add("|---|---|---|---|---|---|---|")
    for pr in sg.get("pairs") or []:
        d = pr.get("stats") or {}
        word = SIBLING_GAP_WORDS.get(pr.get("verdict"), pr.get("verdict") or "")
        if pr.get("verdict") == "PERSISTENT_GAP" and (pr.get("flags") or {}).get("today_is_tail"):
            word += "（但今天是最高分位）"
        add("| %s | %s %s | %+.2fpp | %s | %s | %s | %s |" % (
            pr.get("leg_symbol"), pr.get("sibling_symbol") or "", pr.get("sibling_name") or "",
            pr.get("gap_today_pp") or 0.0,
            ("%+.2fpp" % d["mean_pp"]) if d.get("mean_pp") is not None else "—",
            d.get("days", "—"),
            ("%.0f%%" % d["today_percentile"]) if d.get("today_percentile") is not None else "—",
            word))
    add("")
    for pr in sg.get("pairs") or []:
        d = pr.get("stats") or {}
        if pr.get("verdict") in ("PERSISTENT_GAP", "EPISODIC_GAP") and d:
            tail = (pr.get("flags") or {}).get("today_is_tail")
            if pr["verdict"] == "PERSISTENT_GAP":
                say = ("这只票历史上多数日子都比换过去那只贵，平均 %+.2fpp（%d 个交易日，同向占 %.0f%%）——"
                       "长期换掉它是对的；但今天的 %+.2fpp 是这段历史里的第 %.0f 分位，"
                       "高出来的那部分是今天这一次，不是长期成本。"
                       % (d["mean_pp"], d["days"], 100 * d["share_days_positive"],
                          pr.get("gap_today_pp") or 0.0, d["today_percentile"]))
                if not tail:
                    say = ("这只票历史上多数日子都比换过去那只贵，平均 %+.2fpp（%d 个交易日，同向占 %.0f%%）"
                           "——今天的 %+.2fpp 与它一致，长期换掉它就是一次性的修正。"
                           % (d["mean_pp"], d["days"], 100 * d["share_days_positive"],
                              pr.get("gap_today_pp") or 0.0))
            else:
                say = ("%d 个交易日里两边平均只差 %+.2fpp，今天的 %+.2fpp 落在第 %.0f 分位"
                       "——这是今天的一次，别把它当成年年有的收益。"
                       % (d["days"], d["mean_pp"], pr.get("gap_today_pp") or 0.0, d["today_percentile"]))
            add("- %s→%s：%s" % (pr.get("leg_symbol"), pr.get("sibling_symbol"), say))
    if sg.get("skipped_legs"):
        add("- 这一节读不出价的腿：%s。**读不出不是「没有价差」**——这几只票的同类标签上今天没有"
            "第二只活着的票，所以页面只能给「无法核验」。"
            % "；".join("%s（%s）" % (x.get("leg_symbol"), x.get("label") or "无同类标签")
                       if x.get("label") else "%s（无同类标签）" % x.get("leg_symbol")
                       for x in sg["skipped_legs"]))
    add("")
    return L


def floor_provenance_face(path=FLOOR_PROVENANCE_JSON):
    """What ISSUED the size limit this page prints (r1473).

    Read-only over the published face. An absent face is "cannot say why", never "the
    limit is a rule" -- and a face anchored on another session is a mismatch, not
    freshness."""
    if not os.path.exists(path):
        return {"status": "unreadable", "artifact": _rel(path, ROOT).replace(os.sep, "/"),
                "detail": "floor-provenance face absent"}
    f = _load(path) or {}
    if not f.get("verdict"):
        return {"status": "unreadable", "artifact": _rel(path, ROOT).replace(os.sep, "/"),
                "detail": "face carries no verdict"}
    return {
        "status": "ok",
        "artifact": _rel(path, ROOT).replace(os.sep, "/"),
        "verdict": f.get("verdict"),
        "beta_target": f.get("beta_target"),
        "published_floor": f.get("published_floor"),
        "identity": f.get("identity") or [],
        "grid": f.get("grid") or {},
        "effects": f.get("effects") or {},
        "issuing_cell": f.get("issuing_cell") or {},
        "issuing_cell_is_the_floor": f.get("issuing_cell_is_the_floor"),
        "sentence": f.get("sentence"),
        "not_measured": f.get("not_measured") or [],
        "evidence_cutoff": f.get("evidence_cutoff"),
    }


def vol_target_face(path=VOL_TARGET_GATE_JSON):
    """Whether dialling the book clears its calendar (r1473).

    Same two rules: absent is "cannot verify", and only the arms the face actually
    priced are printed -- a sweep with no rows is not a refusal."""
    if not os.path.exists(path):
        return {"status": "unreadable", "artifact": _rel(path, ROOT).replace(os.sep, "/"),
                "detail": "vol-target-gate face absent"}
    f = _load(path) or {}
    if not f.get("arms"):
        return {"status": "unreadable", "artifact": _rel(path, ROOT).replace(os.sep, "/"),
                "detail": "face carries no priced arm"}
    arms = []
    for a in f.get("arms") or []:
        money = a.get("money") or {}
        yh = ((a.get("rulers") or {}).get("years_for_half") or {})
        arms.append({
            "arm": a.get("arm"),
            "vol_target": a.get("vol_target"),
            "word": a.get("word") or a.get("verdict"),
            "reason": a.get("reason"),
            "cagr_pct": money.get("cagr_pct"),
            "sharpe": money.get("sharpe"),
            "maxdd_pct": money.get("maxdd_pct"),
            "years_for_half_state": yh.get("state"),
            "years_for_half_median": yh.get("median"),
            "years_for_half_line": yh.get("line"),
            "phases": a.get("phases"),
        })
    return {
        "status": "ok",
        "artifact": _rel(path, ROOT).replace(os.sep, "/"),
        "verdict": f.get("verdict"),
        "reading": f.get("verdict_reading"),
        "asof": f.get("asof"),
        "capacity_cny": f.get("capacity_cny_1day_5pct"),
        "arms": arms,
        "shape": f.get("shape_invariance") or {},
    }


FLOOR_PROVENANCE_WORDS = {
    "FLOOR_IS_A_BETA_RECIPROCAL":
        "**额度不是一个版本的规则，是一把倒过来的尺子**：每一格都满足 k×β=目标波动，"
        "所以额度=目标波动÷实测最大的那个 β",
    "IDENTITY_BROKEN": "**面自己不自洽**：k×β 不等于目标波动，读到的额度不能当尺子用",
}

VOL_TARGET_VERDICT_WORDS = {
    "LAWFUL_SUPPLY_FOUND": "**至少有一档能过门**",
    "STILL_REFUSED": "**没有一档能过门**",
    "INDETERMINATE": "**测不出**（有档位在若干相位上读不到判据）",
    "NO_ARMS": "**没有可测的档**",
}


def floor_provenance_block(fp, vt=None, page_bar=None):
    """The lines this page prints about WHERE its own size limit comes from."""
    L = []
    add = L.append
    add("## 为什么这张单只能下这么大")
    add("")
    fp = fp or {}
    if fp.get("status") != "ok":
        add("这一节读不到额度来源面（`%s`）：%s。**所以本页只能给出额度是多少，说不出它是怎么定的**——"
            "读者若要问「能不能多买一点」，本页此刻没有能回答的东西。"
            % (fp.get("artifact") or "results/etf_book_floor_provenance.json",
               fp.get("detail") or "无读数"))
        add("")
    else:
        if page_bar and fp.get("evidence_cutoff") and \
                str(page_bar)[:10] != str(fp["evidence_cutoff"])[:10]:
            add("额度来源面锚在 **%s**，本页的价是 **%s**——两个日子对不上，下面的拆分不能直接当作今天的。"
                % (fp["evidence_cutoff"], page_bar))
            add("")
        add("- 判词：%s。" % FLOOR_PROVENANCE_WORDS.get(
            fp.get("verdict"), "**%s**" % fp.get("verdict")))
        ic = fp.get("issuing_cell") or {}
        if ic:
            add("- 签发它的那一格：**%s**（%s；%s 根 bar），β=%.4f、k=%.6f。"
                % (ic.get("cell"), ic.get("window") or "窗口未标注",
                   ic.get("bars") or "—", ic.get("beta") or 0.0, ic.get("k") or 0.0))
        grid = fp.get("grid") or {}
        if grid:
            add("")
            add("| 这一格 | 窗口 | 币种池 | bar 数 | 实测 β | 会给出的额度 k |")
            add("|---|---|---|---|---|---|")
            name_map = {"baseline_published": "全窗·全池（已发布基线）",
                        "window": "短窗·全池",
                        "universe": "全窗·分级池",
                        "window_x_universe": "短窗·分级池（签发了今天的额度）"}
            for key in ("full|all", "common|all", "full|graded", "common|graded"):
                cell = grid.get(key) or {}
                if not cell:
                    continue
                add("| %s | %s | %s | %s | %.4f | %.6f |" % (
                    name_map.get(cell.get("cell"), cell.get("cell")),
                    "全窗" if key.startswith("full") else "短窗",
                    "全" if key.endswith("all") else "分级",
                    cell.get("bars") or "—", cell.get("beta") or 0.0, cell.get("k") or 0.0))
            add("")
        eff = fp.get("effects") or {}
        if eff.get("total_gap_pp") is not None:
            add("**最宽的额度（k=%.6f）与今天的额度（k=%.6f）差 %.2fpp，按 ￥1,000,000 本钱折 ￥%s——"
                "其中 %.2fpp（%.0f%%，￥%s）只是把窗口从全史缩到 %s 根 bar 造成的，"
                "%.2fpp（%.0f%%，￥%s）是改币种池造成的，两者交互 %.2fpp。**"
                % (eff.get("floor_full_all") or 0.0, eff.get("floor_common_graded") or 0.0,
                   eff.get("total_gap_pp") or 0.0, format(eff.get("total_gap_cny") or 0, ",.0f"),
                   eff.get("window_effect_pp") or 0.0,
                   100 * (eff.get("window_share_of_gap") or 0.0),
                   format(eff.get("window_effect_cny") or 0, ",.0f"),
                   (grid.get("common|all") or {}).get("bars") or "—",
                   eff.get("universe_effect_pp") or 0.0,
                   100 * (eff.get("universe_share_of_gap") or 0.0),
                   format(eff.get("universe_effect_cny") or 0, ",.0f"),
                   eff.get("interaction_pp") or 0.0))
            add("")
        for nm in fp.get("not_measured") or []:
            add("- 这一面没有量的：%s" % nm)
        if fp.get("not_measured"):
            add("")
    vt = vt or {}
    add("### 那么把波动档调一调，能不能让这本账今天就能按年度门供上货")
    add("")
    if vt.get("status") != "ok":
        add("这一节读不到波动档扫描面（`%s`）：%s。**所以本页说不出「调档能不能过门」**——"
            "读不到不等于不能。"
            % (vt.get("artifact") or "results/etf_book_vol_target_gate.json",
               vt.get("detail") or "无读数"))
        add("")
        return L
    arms = vt.get("arms") or []
    add("- 判词：%s——%s。" % (
        VOL_TARGET_VERDICT_WORDS.get(vt.get("verdict"), "**%s**" % vt.get("verdict")),
        vt.get("reading") or "无读数"))
    add("")
    add("| 波动档 | 年化 | 夏普 | 最大回撤 | 判词 | 理由 |")
    add("|---|---|---|---|---|---|")
    for a in arms:
        vtw = {"ADMIT_AT_EVERY_PHASE": "过门", "REFUSED": "仍被拒",
               "INDETERMINATE": "测不出", "NO_ARMS": "没有臂"}.get(
                   a.get("word"), a.get("word") or "—")
        add("| %s | %s | %s | %s | %s | %s |" % (
            ("不调档（原书）" if a.get("vol_target") in (None, 0) else "%.0f%% 波动目标" % (100 * (a.get("vol_target") or 0))),
            ("%.2f%%" % a["cagr_pct"]) if a.get("cagr_pct") is not None else "—",
            ("%.2f" % a["sharpe"]) if a.get("sharpe") is not None else "—",
            ("%.2f%%" % a["maxdd_pct"]) if a.get("maxdd_pct") is not None else "—",
            vtw, (a.get("reason") or "—")))
    add("")
    yh = [(a.get("years_for_half_median"), a.get("years_for_half_state"), a.get("years_for_half_line"))
          for a in arms if a.get("years_for_half_median") is not None]
    if yh:
        meds = [x[0] for x in yh]
        line = yh[0][2]
        add("**调档能改年化，改不了那把尺子**：%d 档里「几年才凑够一半收益」的中位数是 %s（线是 %s 年），"
            "最好的一档也只到 %s——所以「再等几年」不是缩放没调对的假象，是这本账自身的形状。"
            % (len(yh), ("%.2f" % (sum(meds) / len(meds))), line if line is not None else "—",
               "%.0f" % max(meds)))
        add("")
    shp = vt.get("shape") or {}
    if shp.get("reason"):
        add("- 同一面还量了「换档会不会让尺子自己动」：%s" % shp["reason"])
        add("")
    return L


def executed_face(ticket=None):
    """What today's ticket did to the account, from the stack it was netted through.

    The order sheet is the pre-trade target; the account is what came out the other side.
    Without this face the two tables contradict each other by a leg and nothing on the page
    says which one is stale (r1506: five rows on the sheet, four legs in the account)."""
    ticket = ticket or {}
    ss = ticket.get("swap_stack") or {}
    pos = ticket.get("positions") or {}
    actions = []
    src = None
    for a in (ss.get("actions") or []):
        actions.append({"side": a.get("side"), "symbol": a.get("symbol"),
                        "lots": a.get("lots"), "price": a.get("price"),
                        "amount_cny": a.get("amount_cny"), "why": a.get("why"),
                        "priced": a.get("price") is not None})
        src = src or "swap_stack"
    if not actions:
        # the ledger row carries sides and lot counts only -- no prices, so it can name the
        # trades but never their money. Carry that honestly instead of dropping the face.
        for a in ((pos.get("ledger_row") or {}).get("actions") or []):
            actions.append({"side": a.get("side"), "symbol": a.get("symbol"),
                            "lots": a.get("lots"), "price": None,
                            "amount_cny": None, "why": None, "priced": False})
            src = src or "ledger_row"
    if not actions:
        return {"status": "none",
                "detail": "这张票没有留下成交行（空票或本 bar 未换仓）"}
    sold = sum(a["amount_cny"] or 0.0 for a in actions
               if (a["side"] or "").upper() == "SELL")
    bought = sum(a["amount_cny"] or 0.0 for a in actions
                 if (a["side"] or "").upper() == "BUY")
    return {
        "status": "ok",
        "source": src,
        "asof": ss.get("asof") or ticket.get("as_of"),
        "verdict": ss.get("verdict"),
        "actions": actions,
        "priced": all(a["priced"] for a in actions),
        "sold_cny": sold,
        "bought_cny": bought,
        "lot_residue_cny": ss.get("lot_residue_cny"),
        "risk_book_before_cny": ss.get("risk_book_before_cny"),
        "risk_book_after_cny": ss.get("risk_book_after_cny"),
        "holdings_after": ss.get("holdings_after") or [],
    }


def executed_block(ex, sheet_symbols=None):
    """The lines that reconcile the sheet above with the legs the account actually holds."""
    L = []
    add = L.append
    add("## 这张票在账本里实际成交了什么")
    add("")
    ex = ex or {}
    if ex.get("status") != "ok":
        add("这张票读不到成交行（%s）——**所以上面那张清单和账上的持仓差在哪，本页说不出**；"
            "别把「没印出来」读成「没有成交」。" % (ex.get("detail") or "无读数"))
        add("")
        return L
    acts = ex.get("actions") or []
    sheet = [q for q in (sheet_symbols or []) if q]
    after = [h.get("symbol") for h in (ex.get("holdings_after") or []) if h.get("symbol")]
    if sheet and after:
        gone = [q for q in sheet if q not in after]
        new = [q for q in after if q not in sheet]
        if gone or new:
            add("**上面那张 %d 行清单是换仓前的票面；账本在 %s 这根 bar 上把它换成了 %d 只。**"
                % (len(sheet), ex.get("asof") or "—", len(after)))
            add("")
            add("- 清单里有、账上没有：%s。" % ("、".join(gone) if gone else "无"))
            add("- 账上有、清单里没有：%s。" % ("、".join(new) if new else "无"))
        else:
            add("**上面那张清单和账本的持仓是同一批票（%d 只）**，今天这一根 bar 只改了份数，没换票。"
                % len(after))
        add("")
    if ex.get("priced"):
        add("| 方向 | 代码 | 份 | 参考价 | 金额 |")
        add("|---|---|---|---|---|")
        for a in acts:
            side = (a.get("side") or "").upper()
            side_zh = "卖出" if side == "SELL" else ("买入" if side == "BUY" else (a.get("side") or "—"))
            add("| %s | %s | %s | %s | ￥%s |"
                % (side_zh, a.get("symbol"), format(a.get("lots") or 0, ","), a.get("price"),
                   format(a.get("amount_cny") or 0.0, ",.0f")))
        add("")
        net = (ex.get("bought_cny") or 0.0) - (ex.get("sold_cny") or 0.0)
        add("- 买入 ￥%s、卖出 ￥%s，净现金%s ￥%s。"
            % (format(ex.get("bought_cny") or 0.0, ",.0f"),
               format(ex.get("sold_cny") or 0.0, ",.0f"),
               "流出" if net >= 0 else "流入", format(abs(net), ",.0f")))
        if ex.get("lot_residue_cny"):
            add("- 手数取整留下 ￥%s 没投出去——不是成本，是没有整份可买。"
                % format(ex.get("lot_residue_cny") or 0.0, ",.2f"))
        whys = [a.get("why") for a in acts if a.get("why")]
        if whys:
            add("- 换的理由（票内原文）：%s。" % "；".join(whys))
        b0, b1 = ex.get("risk_book_before_cny"), ex.get("risk_book_after_cny")
        if b0 is not None and b1 is not None:
            add("- 风险腿 ￥%s → ￥%s（差 ￥%s 就是上面那笔取整残留）。"
                % (format(b0, ",.0f"), format(b1, ",.0f"), format(b0 - b1, ",.2f")))
    else:
        add("- 只有手数，没有价：这张票的成交行（`%s`）不带价格，**所以这一节说不出花了多少钱**——"
            "手数不是金额。" % (ex.get("source") or "ledger"))
        add("")
        add("| 方向 | 代码 | 份 |")
        add("|---|---|---|")
        for a in acts:
            side = (a.get("side") or "").upper()
            side_zh = "卖出" if side == "SELL" else ("买入" if side == "BUY" else (a.get("side") or "—"))
            add("| %s | %s | %s |" % (side_zh, a.get("symbol"), format(a.get("lots") or 0, ",")))
    add("")
    add("- 这不是第二条建议：它是同一张单的执行结果，所以「账上持有 %s 只」和上面那张清单不是矛盾，是先后。"
        % (len(after) if after else "—"))
    add("")
    return L


def positions_face(path=POSITIONS_JSON):
    """What the account itself holds, from the book's own sheet (r1470).

    Read-only over the published face. An absent face is "cannot verify" -- never "the
    printed rows are the whole order" -- and a face anchored on another session is a
    mismatch, not freshness."""
    if not os.path.exists(path):
        return {"status": "unreadable", "artifact": _rel(path, ROOT).replace(os.sep, "/"),
                "detail": "positions face absent"}
    f = _load(path) or {}
    if not f.get("next_order_base"):
        return {"status": "unreadable", "artifact": _rel(path, ROOT).replace(os.sep, "/"),
                "detail": "face carries no account base"}
    return {
        "status": "ok",
        "artifact": _rel(path, ROOT).replace(os.sep, "/"),
        "asof": f.get("asof"),
        "verdict": f.get("verdict"),
        "printed_rows": f.get("printed_rows"),
        "book_rows": f.get("book_rows"),
        "unexplained": f.get("unexplained") or [],
        "unexplained_total_cny": f.get("unexplained_total_cny"),
        "unexplained_unpriced_rows": f.get("unexplained_unpriced_rows"),
        "ledger_action": f.get("ledger_action"),
        "ledger_row": f.get("ledger_row") or {},
        "next_order_base": f.get("next_order_base") or {},
        "base_divergence": f.get("base_divergence") or [],
        "base_divergence_total_cny": f.get("base_divergence_total_cny"),
        "accrual": f.get("accrual") or {},
        "replay": f.get("replay") or {},
        "engine_book": f.get("engine_book") or {},
        "caveats": f.get("caveats") or [],
    }


def positions_block(ps, page_bar=None):
    """The lines this page prints about what the account actually holds."""
    L = []
    add = L.append
    add("## 账上现在拿的是什么（本仓库自己算的账）")
    add("")
    ps = ps or {}
    if ps.get("status") != "ok":
        add("这一节读不到账本面（`%s`）：%s。**因此本页只能给「如果你今天才建仓」的清单，"
            "说不出已经持有多少、现金还剩多少**——把这张清单当成账上现状是错的。"
            % (ps.get("artifact") or "results/etf_book_positions.json",
               ps.get("detail") or "无读数"))
        add("")
        return L
    if page_bar and ps.get("asof") and str(page_bar)[:10] != str(ps["asof"])[:10]:
        add("账本面锚在 **%s**，本页的价是 **%s**——两个日子对不上，下面的持仓与现金不能当成今天的账。"
            % (ps["asof"], page_bar))
        add("")
    row = ps.get("ledger_row") or {}
    base = ps.get("next_order_base") or {}
    if base.get("risk_book_cny") is not None:
        add("**账上自己的账（%s 收盘）：风险腿 ￥%s、现金 ￥%s、持有 %s 只。**"
            % (base.get("bar") or ps.get("asof") or "—",
               format(base.get("risk_book_cny") or 0.0, ",.0f"),
               format(base.get("cash_cny") or 0.0, ",.0f"),
               base.get("holdings") if base.get("holdings") is not None else "—"))
        add("")
    holds = row.get("holdings") or []
    if holds:
        add("| 代码 | 手数 | 参考价 | 金额 |")
        add("|---|---|---|---|")
        for h in holds:
            add("| %s | %s | %s | ￥%s |" % (
                h.get("symbol"), format(h.get("lots") or 0, ","), h.get("price"),
                format(h.get("amount_cny") or 0.0, ",.0f")))
        add("")
    unexp = ps.get("unexplained_total_cny") or 0.0
    unpriced = ps.get("unexplained_unpriced_rows") or 0
    if unexp or unpriced:
        add("- **这张票的换仓行只印 %s 行、账本有 %s 行**（不是上面那张 5 行建仓表）："
            "差出来的 **￥%s** 是「该卖却没印出来」的份额，照票上的卖出行动作会把这些仓留在账上。"
            % (ps.get("printed_rows"), ps.get("book_rows"), format(unexp, ",.0f")))
        if unpriced:
            add("- 其中 %d 行没有价格，算不进上面这个数——**未定价不是零**。" % unpriced)
    div = ps.get("base_divergence_total_cny") or 0.0
    if div:
        add("- 下一张单从这里起算和从清单起算差 **￥%s**：`%s` 那一步是从账本读的，不是从上一张纸读的。"
            % (format(div, ",.0f"), ps.get("ledger_action") or "kept"))
    rp = ps.get("replay") or {}
    if rp.get("bars"):
        add("- 从 %s 起 %d 根 bar 自己走了一遍：持仓端 %+.2f%%、现金腿利息 ￥%s，"
            "两段加起来与净值恒等（%s）。"
            % (rp.get("start_bar"), rp.get("bars"), 100.0 * (rp.get("legs_ret") or 0.0),
               format(rp.get("cash_interest_cny") or 0.0, ",.2f"),
               "成立" if rp.get("identity_holds") else "**不成立**"))
        if not rp.get("identity_holds"):
            add("- **恒等不成立**：这张账本自己的两半加不回净值，下面的读数不能当账。")
    ac = ps.get("accrual") or {}
    if ac:
        if ac.get("status") == "NO_NEW_BAR":
            add("- 现金腿利息：**今天没有新 bar，还没有新的利息入账**——这不是「利息为零」，"
                "是账只记到 %s。" % (ac.get("from_bar") or "—"))
        elif ac.get("rows"):
            last = ac.get("last") or {}
            add("- 现金腿利息：本 bar 入账 %s 行，最新 ￥%s（利率面板停在 %s，最新 %s%%）。"
                % (ac.get("rows"), format((last or {}).get("interest_cny") or 0.0, ",.2f"),
                   ac.get("rate_latest_bar") or "—", ac.get("rate_latest")))
        if ac.get("rf_missing_bars"):
            add("- 有 %d 根 bar 的利率缺失，那几段现金腿按 0 记——**不是真的没利息**。"
                % ac["rf_missing_bars"])
    eb = ps.get("engine_book") or {}
    dv = eb.get("divergence") or {}
    if dv.get("notional_gap_cny"):
        add("- 与引擎账（`%s`）差 %s 个 k 点 = ￥%s 名义额：这本账按额度裁过，引擎账没裁。"
            % ((eb.get("tail") or {}).get("source") or "engine",
               "%.6f" % (dv.get("k_gap") or 0.0), format(dv["notional_gap_cny"], ",.0f")))
    add("")
    return L


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


def sample_window_face(path=SPANNING_PRE2020_JSON, grid_path=PRE2020_JSON):
    """Where do the numbers on this page come from -- which window, which universe? (r1233)

    Everything printed above is measured on 2020-01 onwards, i.e. on the ETF boom. The card
    already ran the same shipment rule on the 193 ETFs that existed before that window and
    reports that no intercept survives; this page never said so, which let a reader size a
    position believing the numbers are the rule's level rather than the window's property.

    Reads only. The payload's own verdict is cross-checked against the numbers it publishes:
    "no intercept survives" must mean every published t is below 2, and a payload whose words
    disagree with its own rows is refused (drifted) instead of printed."""
    if not os.path.exists(path):
        return {"status": "absent", "artifact": _rel(path, ROOT), "detail": "no artifact"}
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        arms = doc.get("arms") or {}
        rows = []
        for key in ("single", "staggered"):
            arm = arms.get(key) or {}
            full = arm.get("full") or {}
            oos = arm.get("oos") or {}
            st = arm.get("stats") or {}
            if full.get("alpha_t") is None:
                continue
            rows.append({"arm": key,
                         "window": arm.get("window"),
                         "cagr": st.get("cagr"), "sharpe": st.get("sharpe"),
                         "maxdd": st.get("maxdd"), "vol": st.get("vol"),
                         "alpha_annual": full.get("alpha_annual"),
                         "alpha_t": full.get("alpha_t"),
                         "oos_alpha_annual": oos.get("alpha_annual"),
                         "oos_alpha_t": oos.get("alpha_t"),
                         "n_obs": full.get("n_obs")})
        if not rows:
            return {"status": "unreadable", "artifact": _rel(path, ROOT),
                    "detail": "no arm publishes an intercept test"}
        ts = [abs(float(r["alpha_t"])) for r in rows]
        survives = any(t >= 2.0 for t in ts)
        claimed_none = "no intercept survives" in (doc.get("verdict") or "").lower()
        # the words and the rows must agree; when they do not, the page has no basis to pick one
        if survives == claimed_none:
            return {"status": "drifted", "artifact": _rel(path, ROOT),
                    "detail": "the published verdict disagrees with its own t statistics",
                    "t_abs": ts, "verdict": doc.get("verdict")}
        grid = None
        page_window = None
        if os.path.exists(grid_path):
            try:
                with open(grid_path, encoding="utf-8") as fh:
                    gd = json.load(fh)
                prim = ((gd.get("grid") or {}).get("primary")) or "N5_R20"
                cell = None
                blocks = gd.get("cells") or {}
                # the post-period block IS the window every number on this page lives in;
                # read it in its own pass so the 2015 cell lookup cannot short-circuit it
                for key, block in blocks.items():
                    if key.startswith("C_") and block.get("start") and block.get("end"):
                        page_window = [block.get("start"), block.get("end")]
                        break
                for block in blocks.values():
                    if (block.get("start"), block.get("end")) == ("2015-01-01", "2019-12-31"):
                        cell = (block.get("cells") or {}).get(prim)
                        if cell:
                            grid = {"primary": prim, "start": block.get("start"),
                                    "end": block.get("end"),
                                    "book_cagr": (cell.get("book") or {}).get("cagr"),
                                    "ew_cagr": (cell.get("ew") or {}).get("cagr"),
                                    "excess_pp": cell.get("excess_cagr_pp"),
                                    "p_value": (cell.get("null") or {}).get("p_value"),
                                    "n_iter": (cell.get("null") or {}).get("n_iter"),
                                    "universe": block.get("universe_size"),
                                    "cost_bp": gd.get("cost_bp_per_side"),
                                    "cutoff": gd.get("evidence_cutoff")}
                            break
            except Exception:                                   # noqa: BLE001
                grid = None
        return {"status": "ok", "artifact": _rel(path, ROOT).replace("\\", "/"),
                "window": doc.get("window"), "universe": doc.get("universe") or {},
                "config": doc.get("config") or {}, "rows": rows,
                "verdict": doc.get("verdict"), "survives": survives,
                "t_abs_max": max(ts), "grid": grid, "page_window": page_window,
                "caveats": doc.get("caveats") or [],
                "evidence_cutoff": (grid or {}).get("cutoff")}
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": _rel(path, ROOT),
                "detail": "reading failed (%s)" % str(exc)[:120]}


def sample_window_block(sw):
    """The page's numbers belong to a window -- say which one, and what happens outside it.

    Factored out so a selftest can feed an absent / drifted / ok face. The label ("clears /
    does not clear") is derived from the published t statistics, never from the prose."""
    L = []
    add = L.append
    add("## 这些号码是从哪一段行情里长出来的")
    add("")
    sw = sw or {}
    if sw.get("status") != "ok":
        add("这一页没拿到跨窗口检验（`%s`，状态 `%s`）：%s。所以**这里无法回答**「换个时段还成不成」"
            "——读不出来不等于「跨时段也成立」。"
            % (str(sw.get("artifact") or "results/etf_book_spanning_pre2020.json").replace(os.sep, "/"),
               sw.get("status") or "unknown",
               sw.get("detail") or "判决不能从自己的行重算"))
        add("")
        return L
    uni = sw.get("universe") or {}
    cfg = sw.get("config") or {}
    win = sw.get("window") or ["?", "?"]
    pw = sw.get("page_window") or [None, None]
    _page_win = ("%s 至 %s" % (pw[0], pw[1])) if (pw[0] and pw[1]) else "2020 年以后"
    add("上面每一格都是 **%s** 这段行情里量出来的。同一套要发货的规则（%s 名 / %s 日 / %s%% 波动目标 / 单边 %s bp）"
        "跑到那之前就已经上市的 **%s 只** ETF 上、%s 至 %s："
        % (_page_win, cfg.get("n_hold"), cfg.get("rebal"),
           (round((cfg.get("vol_target") or 0.0) * 100, 2)), cfg.get("cost_bp_per_side"),
           uni.get("U_pre"), win[0], win[1]))
    add("")
    add("| 这条规则的跑法 | 年化 | 夏普 | 最大回撤 | 摊到「黄金/纳指/沪深300/债券」之后还剩 |")
    add("|---|---|---|---|---|")
    names = {"single": "一条序列（本页这种）", "staggered": "分成 %s 段错开建仓" % (cfg.get("stagger") or {}).get("n_total")}
    for r in sw.get("rows") or []:
        add("| %s | %+.2f%% | %.2f | %+.2f%% | %+.2f%%/年（t=%.2f） |"
            % (names.get(r.get("arm"), r.get("arm")),
               100.0 * (r.get("cagr") or 0.0), r.get("sharpe") or 0.0,
               100.0 * (r.get("maxdd") or 0.0),
               100.0 * (r.get("alpha_annual") or 0.0), r.get("alpha_t") or 0.0))
    add("")
    add("同一批数据，切成「前三年拟合、后两年检验」：%s。"
        % "；".join("%s %+.2f%%/年（t=%.2f）"
                   % (names.get(r.get("arm"), r.get("arm")),
                      100.0 * (r.get("oos_alpha_annual") or 0.0), r.get("oos_alpha_t") or 0.0)
                   for r in (sw.get("rows") or [])))
    add("")
    g = sw.get("grid") or {}
    if g.get("book_cagr") is not None:
        _cost = ("、单边 %s bp" % g["cost_bp"]) if g.get("cost_bp") is not None else ""
        _niter = ("随机置换 %s 次的 " % g["n_iter"]) if g.get("n_iter") is not None else ""
        add("换一种跑法（%s 名、不加波动覆盖%s）在同一时段：**%+.2f%%/年**，"
            "同期同样的票池等权是 **%+.2f%%/年**（相差 %+.2fpp/年，%sp=%.2f）。"
            % (str(g.get("primary") or "").split("_")[0].lstrip("N"), _cost,
               100.0 * g["book_cagr"],
               100.0 * (g.get("ew_cagr") or 0.0), g.get("excess_pp") or 0.0,
               _niter, g.get("p_value") if g.get("p_value") is not None else float("nan")))
        add("")
    if sw.get("survives"):
        add("- 上面那条 t 的读数**过线了**：换个时段这套规则仍与一个固定配比有所区别。"
            "但样本只有 %s 至 %s 这 %d 根 bar，仍不是「未来的承诺」。"
            % (win[0], win[1], max((r.get("n_obs") or 0) for r in (sw.get("rows") or [])) or 0))
    else:
        add("- 两条跑法的 t 都在 **%.2f 以下**：换个时段，这套规则**跟一个固定的四资产配比分不开**。"
            "所以上面那些数字是 **2020 之后这段行情** 的性质，不是这套规则的水平——"
            "买它等于押「这段行情还会再来」，不是买一个跨时段验证过的超额。" % sw.get("t_abs_max", 0.0))
    add("")
    for c in (sw.get("caveats") or [])[:2]:
        add("- 证据件原话（未改写，避免第二套措辞）：%s" % c)
    add("")
    add("> 跨窗口面：`%s` ｜ 窗口 %s ~ %s ｜ 票池 %s 只（2020 前已上市）"
        % (sw.get("artifact"), win[0], win[1], uni.get("U_pre")))
    add("")
    return L


def universe_lock_face(path=UNIVERSE_LOCK_JSON):
    """Was this book runnable in 2020, or does its return depend on funds listed since? (r1235)

    Every headline on this page is earned on today's universe. A third of those funds did not
    exist when the window opened, and 11 of the 12 names in the book in force were listed
    after it. This face answers the reader's question ("could I have bought this?") with the
    locked-universe run: same cell, same fill, universe frozen on the window's first day.

    Reads only, and re-derives the verdict from the payload's own rows through the face's
    single implementation (import, never a second copy). A payload whose control arms no
    longer reproduce the published headline is REFUSED rather than printed -- the lock numbers
    are meaningless if they were priced on a different book.
    """
    if not os.path.exists(path):
        return {"status": "absent", "artifact": _rel(path, ROOT), "detail": "no artifact"}
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        rows = doc.get("phase_rows") or []
        summary = doc.get("summary") or {}
        control = doc.get("control") or {}
        if not rows or not summary:
            return {"status": "unreadable", "artifact": _rel(path, ROOT),
                    "detail": "no phase rows"}
        if not (control.get("ok") and all(v.get("ok")
                                         for v in (control.get("arms") or {}).values())):
            return {"status": "drifted", "artifact": _rel(path, ROOT),
                    "detail": "the control arms no longer reproduce the published headline",
                    "control": control}
        import etf_book_universe_lock as UL
        recomputed = UL.verdict_from_summary(UL._summarise(rows))
        if summary.get("verdict") != recomputed:
            return {"status": "drifted", "artifact": _rel(path, ROOT),
                    "detail": "the published verdict disagrees with its own rows",
                    "verdict": summary.get("verdict"), "recomputed": recomputed}
        lock_key = "lock_%s" % (doc.get("criteria") or {}).get("headline_lock", "")
        phases = []
        for r in rows:
            lk = r.get(lock_key) or {}
            phases.append({"phase": r.get("phase"), "start": r.get("phase_start"),
                           "unlocked": (r.get("unlocked") or {}).get("cagr"),
                           "locked": lk.get("cagr"), "delta_pp": r.get("delta_pp")})
        return {"status": "ok", "artifact": _rel(path, ROOT),
                "evidence_cutoff": doc.get("evidence_cutoff"),
                "verdict": summary.get("verdict"),
                "delta_mean_pp": summary.get("delta_mean_pp"),
                "delta_min_pp": summary.get("delta_min_pp"),
                "delta_max_pp": summary.get("delta_max_pp"),
                "phases_lock_costs": summary.get("phases_lock_costs"),
                "phases": phases,
                "lock_date": (doc.get("criteria") or {}).get("headline_lock"),
                "full_n": ((doc.get("panel") or {}).get("columns")),
                "locked_n": (rows[0].get("locked_n") if rows else None),
                "ladder": doc.get("ladder") or [],
                "picks": doc.get("picks") or {},
                "control": control,
                "tol_pp": (doc.get("criteria") or {}).get("tol_pp")}
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": _rel(path, ROOT), "detail": repr(exc)}


def universe_lock_block(ul):
    L = []
    if ul.get("status") != "ok":
        L.append("## 2020 年能不能真的跑这本书？")
        L.append("")
        L.append("**这一问现在答不了。** 证据件缺席或已经对不上自己的行（%s）。"
                 % (ul.get("detail") or ul.get("status")))
        L.append("")
        return L
    pk = ul.get("picks") or {}
    L.append("## 2020 年能不能真的跑这本书？")
    L.append("")
    L.append("上面每个数都是在**今天**的 %s 只基金上算出来的；这些基金里有一部分在窗口开始时"
             "还不存在——今天在手的 %d 个名字里 **%d 个**是 2020 年以后才上市的。"
             % (ul.get("full_n"), len(pk.get("book_in_force") or []),
                pk.get("book_in_force_listed_after_lock") or 0))
    L.append("")
    L.append("同一格规则、同一种成交，把票池冻结在窗口第一天（%s，%s 只）重跑："
             % (ul.get("lock_date"), ul.get("locked_n")))
    L.append("")
    L.append("| 决策相位起点 | 全票池 | 冻结票池 | 差 |")
    L.append("|---|---|---|---|")
    for p in ul.get("phases") or []:
        L.append("| %s | %.2f%% | %.2f%% | %+.2f pp |"
                 % (p.get("start"), 100.0 * (p.get("unlocked") or 0.0),
                    100.0 * (p.get("locked") or 0.0), p.get("delta_pp") or 0.0))
    L.append("")
    v = ul.get("verdict")
    mean = ul.get("delta_mean_pp") or 0.0
    if v == "LOCK_COSTS_MONEY":
        L.append("**要动手的钱：** 冻结票池平均少赚 %+.2f pp/年（%d/%d 个相位达到 %.2f pp 线）——"
                 "上面那些数字有一部分是「买到了后来才上市的基金」给的。"
                 % (mean, ul.get("phases_lock_costs") or 0, len(ul.get("phases") or []),
                    ul.get("tol_pp") or 0.0))
    elif v == "UNIVERSE_ROBUST":
        L.append("**跟票池新旧无关：** 冻结票池后平均只差 %+.2f pp/年（四个相位都在 %.2f pp 内）——"
                 "这套规则在今天这份名单上能做的事，2020 年那份名单上也能做。"
                 % (mean, ul.get("tol_pp") or 0.0))
    else:
        L.append("**平均为零，但相位之间摆动很大：** 冻结票池平均 %+.2f pp/年，"
                 "单个相位从 %+.2f 到 %+.2f pp——摆幅比这条线测过的任何一个效应都大。"
                 "所以既不能说「靠新基金」，也不能说「完全无关」；"
                 "能确定的是选券需要**票池够宽**，而不是**票池够新**（见下表）。"
                 % (mean, ul.get("delta_min_pp") or 0.0, ul.get("delta_max_pp") or 0.0))
    L.append("")
    lad = ul.get("ladder") or []
    if lad:
        L.append("| 票池冻结在 | 基金数 | 年化 | 夏普 | 最大回撤 |")
        L.append("|---|---|---|---|---|")
        labels = {"unlocked": "不冻结（今天）"}
        for r in lad:
            L.append("| %s | %s | %.2f%% | %.2f | %.2f%% |"
                     % (labels.get(r.get("universe"), r.get("universe")), r.get("n_funds"),
                        100.0 * (r.get("cagr") or 0.0), r.get("sharpe") or 0.0,
                        100.0 * (r.get("maxdd") or 0.0)))
        L.append("")
    if pk.get("pick_slots"):
        L.append("整个窗口 %d 个决策持仓位里，有 %d 个（%.1f%%）落在「窗口内才上市」的名字上；"
                 "在手的这一本（决策日 %s）里 %d/%d 属于这一类。"
                 % (pk.get("pick_slots"), pk.get("slots_listed_after_lock") or 0,
                    100.0 * (pk.get("share_listed_after_lock") or 0.0),
                    pk.get("book_in_force_date"),
                    pk.get("book_in_force_listed_after_lock") or 0,
                    len(pk.get("book_in_force") or [])))
        L.append("")
    L.append("> 跨窗口面：`%s` ｜ 证据截止 %s ｜ 控制闸：本面先在卡片自己的两条臂上复现"
             "（as coded 与 declared fill 各差 0.00 pp）才引用任何冻结数。"
             % (str(ul.get("artifact") or "results/etf_book_universe_lock.json").replace(os.sep, "/"),
                ul.get("evidence_cutoff")))
    L.append("")
    return L


def entry_gate_face(path=ENTRY_GATE_JSON):
    """The universe is chosen by one number. Is it a result, or an inheritance? (r1247)

    Every name this book may buy cleared a single cut -- median 20-day turnover >= 20M CNY --
    and that cut was never swept inside the book, so nobody could say whether it is measured
    or just copied. The face that swept it (scripts/etf_book_entry_gate.py, its own selftest)
    is consumed here, not re-run: the verdict is re-derived from the payload's own rows and
    its own control arm through the face's single implementation. A payload whose shipped arm
    no longer reproduces the card's published cell, or whose stored verdict disagrees with its
    own six rows, is REFUSED -- a plateau claim priced on a different book is worse than none.

    The two axes are kept apart on purpose: the same knob buys ±0.2pp of return and it also
    sets how many names the book may hold. Reporting only the first hides the second.
    """
    if not os.path.exists(path):
        return {"status": "absent", "artifact": _rel(path, ROOT), "detail": "no artifact"}
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        rows = doc.get("rows") or []
        control = doc.get("control") or {}
        cfg = doc.get("config") or {}
        stored = doc.get("verdict") or {}
        if len(rows) < 3:
            return {"status": "unreadable", "artifact": _rel(path, ROOT),
                    "detail": "fewer than three priced gates"}
        if control.get("delta_pp") is None:
            return {"status": "drifted", "artifact": _rel(path, ROOT), "control": control,
                    "detail": "no control arm, so a sweep of the cut is not a statement "
                              "about this book"}
        tol = float(control.get("tol_pp") or 0.0)
        if abs(float(control["delta_pp"])) > tol:
            return {"status": "drifted", "artifact": _rel(path, ROOT), "control": control,
                    "detail": "the shipped arm misses the published cell by %.3fpp "
                              "(tolerance %.2fpp)" % (float(control["delta_pp"]), tol)}
        import etf_book_entry_gate as _EG
        recomputed = _EG.classify(
            rows, control_delta_pp=control.get("delta_pp"),
            universe_delta=cfg.get("universe_delta_names"))
        if stored.get("verdict") != recomputed.get("verdict"):
            return {"status": "drifted", "artifact": _rel(path, ROOT),
                    "detail": "the published verdict disagrees with its own rows",
                    "verdict": stored.get("verdict"),
                    "recomputed": recomputed.get("verdict")}
        gates = []
        for r in rows:
            if r.get("cagr") is None or r.get("error"):
                continue
            gates.append({"gate_m": r.get("min_amt_m"),
                          "gate_cny": r.get("min_amt_cny"),
                          "cagr": float(r.get("cagr")),
                          "sharpe": r.get("sharpe"),
                          "maxdd": r.get("maxdd"),
                          "median_names": r.get("median"),
                          "turnover": r.get("turnover_per_decision"),
                          "delta_pp": (stored.get("deltas_pp") or {}).get(
                              str(int(r.get("min_amt_cny") or 0)))})
        if len(gates) < 3:
            return {"status": "unreadable", "artifact": _rel(path, ROOT),
                    "detail": "fewer than three gates could be priced"}
        widths = [g["median_names"] for g in gates if g["median_names"] is not None]
        widest, narrowest = (max(widths), min(widths)) if widths else (None, None)
        near = stored.get("near_deltas_pp") or []
        return {"status": "ok", "artifact": _rel(path, ROOT),
                "evidence_cutoff": doc.get("evidence_cutoff"),
                "panel_last_bar": doc.get("panel_last_bar"),
                "verdict": recomputed.get("verdict"),
                "sentence": recomputed.get("sentence"),
                "shipped_cny": (doc.get("rule") or {}).get("shipped_cny"),
                "tol_pp": (doc.get("rule") or {}).get("tol_pp"),
                "near_max_pp": (max(abs(float(d)) for d in near) if near else None),
                "best_delta_pp": stored.get("best_delta_pp"),
                "gates": gates,
                "widest_names": widest, "narrowest_names": narrowest,
                "width_ratio": (float(widest) / float(narrowest)
                                if widest and narrowest else None),
                "universe_measured": cfg.get("universe_measured"),
                "universe_published": cfg.get("universe_published"),
                "control": control}
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": _rel(path, ROOT), "detail": repr(exc)}


def entry_gate_block(eg):
    L = []
    if eg.get("status") != "ok":
        L.append("## 这本书的票池是被一个数选出来的，那个数是从哪来的？")
        L.append("")
        L.append("**这一问现在答不了。** 证据件缺席、或它自己的行已经对不上"
                 "（%s），所以下面这个门槛是不是量出来的，本页不冒充知道。"
                 % (eg.get("detail") or eg.get("status")))
        L.append("")
        return L
    shipped_m = (float(eg.get("shipped_cny") or 0.0)) / 1e6
    L.append("## 这本书的票池是被一个数选出来的，那个数是从哪来的？")
    L.append("")
    L.append("能买的每一个名字，都要先过同一道闸：20 日成交额中位数 ≥ **%gM**。这个数一直是被继承的，"
             "没人在本书内部挪过它。同一张面板、同一套排名、同一个网格，只动这一个数："
             % shipped_m)
    L.append("")
    L.append("| 门槛 | 年化 | 夏普 | 最大回撤 | 可选名数（中位） | 每次调仓换手 | 相对这一档 |")
    L.append("|---|---|---|---|---|---|---|")
    for g in eg.get("gates") or []:
        d = g.get("delta_pp")
        L.append("| %gM | %.2f%% | %s | %s | %s | %s | %s |"
                 % (g.get("gate_m") or 0.0, 100.0 * (g.get("cagr") or 0.0),
                    "—" if g.get("sharpe") is None else "%.2f" % g["sharpe"],
                    "—" if g.get("maxdd") is None else "%.2f%%" % (100.0 * g["maxdd"]),
                    "—" if g.get("median_names") is None else "%d" % g["median_names"],
                    "—" if g.get("turnover") is None else "%.2f" % g["turnover"],
                    "—" if d is None else "%+.2f pp" % float(d)))
    L.append("")
    near = eg.get("near_max_pp")
    ratio = eg.get("width_ratio")
    if eg.get("verdict") == "GATE_SITS_ON_PLATEAU":
        L.append("**把这道闸砍一半或翻一倍，年化只动 ±%.2f pp**（判据 %.1f pp 内），"
                 "最好的那一档也只多 %+.2f pp——所以这个 20M 不是一个结果，它站在一段平台上，"
                 "可以是任何人的默认值。"
                 % (float(near or 0.0), float(eg.get("tol_pp") or 0.0),
                    float(eg.get("best_delta_pp") or 0.0)))
    else:
        L.append("**判词：%s。** %s"
                 % (eg.get("verdict"), eg.get("sentence") or ""))
    L.append("")
    if ratio is not None and float(ratio) >= 2.0:
        L.append("但对**宽度**它不是平的：同一个门槛从最松到最紧，可选名数中位从 **%d 只** 掉到 "
                 "**%d 只**（%.1f 倍）。这道闸不是你的收益来源，**它是你的容量来源**——"
                 "它决定这本书最多能在多少个名字里挑，也决定同样的钱摊到每个名字上有多大。"
                 "想要更宽的书，代价不是收益，是单笔更小、其中一部分名字的成交额更薄。"
                 % (int(eg.get("widest_names") or 0), int(eg.get("narrowest_names") or 0),
                    float(ratio)))
        L.append("")
    L.append("> 跨窗口面：`%s` ｜ 证据截止 %s（面板末根 bar %s）｜ 控制闸：%gM 这一档先复现"
             "卡片已发表的「可交易臂」年化（差 %.3f pp，容差 %.2f pp）才引用任何一行；"
             "判词由本面从这六行重新导出，不读存盘结论。"
             % (str(eg.get("artifact") or "results/etf_book_entry_gate.json").replace(os.sep, "/"),
                eg.get("evidence_cutoff"), eg.get("panel_last_bar"), shipped_m,
                float((eg.get("control") or {}).get("delta_pp") or 0.0),
                float((eg.get("control") or {}).get("tol_pp") or 0.0)))
    L.append("")
    return L


def live_quote_face(dir_path=LIVE_QUOTE_DIR):
    """What is this book worth today, while the daily panel is still a bar behind? (r1251)

    The snapshot face already answers that question (scripts/etf_book_live_quote.py, with its
    own selftest). This reads the published payload and re-derives both the verdict and the
    arithmetic through that script's single `recheck()` -- a second copy of the join here
    would disagree with the chain gate the first time either one changed.

    Refused rather than softened:
      * no payload / unreadable          -> the page says it cannot answer
      * rows no longer reproduce         -> same, because a quote the chain gate would
                                            reject is not something to print at a reader
      * a snapshot OLDER than the panel  -> nothing here is new information
    """
    latest = os.path.join(dir_path, "latest.json")
    if not os.path.exists(latest):
        return {"status": "absent", "artifact": _rel(latest, ROOT),
                "detail": "no published quote face"}
    try:
        ptr = _load(latest)
        fname = ptr.get("file")
        path = os.path.join(dir_path, fname) if fname else None
        if not path or not os.path.exists(path):
            return {"status": "unreadable", "artifact": _rel(latest, ROOT),
                    "detail": "the pointer names no payload on disk"}
        face = _load(path)
        import etf_book_live_quote as _LQ
        rc = _LQ.recheck(face)
        if not rc.get("ok"):
            return {"status": "drifted", "artifact": _rel(path, ROOT),
                    "detail": rc.get("reason")}
        rows = []
        for r in face.get("rows") or []:
            rows.append({"symbol": r.get("symbol"), "weight": r.get("weight"),
                         "panel_bar": r.get("panel_bar"),
                         "panel_close": r.get("panel_close"),
                         "quote_date": r.get("quote_date"),
                         "quote_prev_close": r.get("quote_prev_close"),
                         "quote_last": r.get("quote_last"),
                         "joined": bool(r.get("joined")), "ret": r.get("ret")})
        out = {"status": "ok", "artifact": _rel(path, ROOT),
               "verdict": rc.get("verdict"),
               "panel_bar": face.get("panel_bar"), "quote_bar": face.get("quote_bar"),
               "quote_time": face.get("quote_time"),
               "lag_trading_days": face.get("lag_trading_days"),
               "n_held": face.get("n_held"), "n_joined": rc.get("n_joined"),
               "mismatch_share": face.get("mismatch_share"),
               "mismatch_share_max": (face.get("thresholds") or {}).get("mismatch_share_max"),
               "book_weight": face.get("book_weight"), "cash_weight": face.get("cash_weight"),
               "held_leg_return": rc.get("held_leg_return"),
               "book_change": rc.get("book_change"),
               "ticket_priced_bar": face.get("ticket_priced_bar"),
               "rows": rows}
        if out["quote_bar"] and out["panel_bar"] and out["quote_bar"] < out["panel_bar"]:
            return dict(out, status="behind",
                        detail="the snapshot %s is older than the panel %s"
                               % (out["quote_bar"], out["panel_bar"]))
        return out
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": _rel(latest, ROOT), "detail": repr(exc)}


def live_quote_block(lq):
    L = []
    L.append("## 面板还停在昨天的时候，这本书今天值多少？")
    L.append("")
    st = lq.get("status")
    if st != "ok":
        why = {"behind": "快照比数据面还旧，这里没有新信息",
               "drifted": "快照自己的行已经复现不出它发布的数字",
               "unreadable": "证据件读不出来",
               "absent": "还没有发布过快照面"}.get(st, str(lq.get("detail") or st))
        L.append("**这一问现在答不了。** %s（%s）——所以本页仍按面板最后一根已收 bar 讲故事，"
                 "不印今天的涨跌。" % (why, lq.get("detail") or st))
        L.append("")
        return L
    v = lq.get("verdict")
    if v == "NO_NEW_BAR":
        L.append("数据面已经吃到 **%s** 这一根 bar，快照里没有更新的东西可加——这一问今天没有新答案。"
                 % lq.get("panel_bar"))
        L.append("")
        return L
    if v != "QUOTE_AHEAD":
        L.append("**整面拒发。** 快照与面板衔接不上的名字占 **%.0f%%**（上限 %.0f%%），"
                 "用剩下几个名字加权出来的是一个没有分母的数。"
                 % (100.0 * float(lq.get("mismatch_share") or 0.0),
                    100.0 * float(lq.get("mismatch_share_max") or 0.0)))
        L.append("")
        return L
    lag = lq.get("lag_trading_days")
    L.append("日线面板还停在 **%s**（源端收盘后要几小时才补当天那根），而交易所快照已经有 **%s %s** "
             "的收盘价——领先 **%s** 个交易日。逐只证明快照接得上面板最后一根（快照昨收 = 面板收盘，"
             "容差半个最小变动价位），再按票面自己的权重报今天："
             % (lq.get("panel_bar"), lq.get("quote_bar"), lq.get("quote_time") or "",
                "?" if lag is None else str(lag)))
    L.append("")
    L.append("| 名字 | 权重 | 面板末根 | 快照昨收 | 今日收盘 | 当日变动 |")
    L.append("|---|---|---|---|---|---|")
    for r in lq.get("rows") or []:
        ret = r.get("ret")
        L.append("| %s | %.2f%% | %s | %s | %s | %s |"
                 % (r.get("symbol"), 100.0 * float(r.get("weight") or 0.0),
                    r.get("panel_bar") or "—",
                    "—" if r.get("quote_prev_close") is None else "%.3f" % r["quote_prev_close"],
                    "—" if r.get("quote_last") is None else "%.3f" % r["quote_last"],
                    ("—（未衔接）" if not r.get("joined") else
                     "—" if ret is None else "%+.2f%%" % (100.0 * float(ret)))))
    L.append("")
    L.append("**持仓腿今天 %+.2f%%**，按票面的持仓权重折算到整本账是 **%+.2f%%**。"
             "现金腿 **%.2f%%** 一动不动——快照里没有逆回购报价，"
             "写成 0 息或补一个历史均值都是给账面编钱。"
             % (100.0 * float(lq.get("held_leg_return") or 0.0),
                100.0 * float(lq.get("book_change") or 0.0),
                100.0 * float(lq.get("cash_weight") or 0.0)))
    L.append("")
    L.append("> 快照面：`%s` ｜ 明细头衔：%d/%d 只衔接 ｜ 定价票面 bar %s。"
             "这条数字**不进账本、不进票面、不产生交易指令**——它只回答「今天涨没涨」，"
             "第二个交易日的收盘 bar 一到，账本自己会给同一个答案。"
             % (str(lq.get("artifact") or "").replace(os.sep, "/"),
                int(lq.get("n_joined") or 0), int(lq.get("n_held") or 0),
                lq.get("ticket_priced_bar") or "—"))
    L.append("")
    return L


def sellability_face(exit_path=EXIT_LIQ_JSON, tail_path=FORCED_HOLD_JSON):
    """Can the desk actually get out of what it is holding? (r1238)

    Every name this book buys passed a 20-bar turnover gate on the bar it was ranked. Nobody
    checked that same number on the bar it is sold. Two faces measure that: one prices the
    exits that had to wait for the gate to clear again, the other prices the tail that never
    cleared it. Both are read here, and both verdicts are re-derived through their own single
    implementation (imported, never a second copy). A payload whose stored verdict disagrees
    with its own rows -- or a tail whose imported census no longer reproduces the totals the
    published 2.78% was counted on -- is REFUSED rather than printed.
    """
    for p in (exit_path, tail_path):
        if not os.path.exists(p):
            return {"status": "absent", "artifact": _rel(p, ROOT), "detail": "no artifact"}
    try:
        with open(exit_path, encoding="utf-8") as fh:
            ex = json.load(fh)
        with open(tail_path, encoding="utf-8") as fh:
            tl = json.load(fh)
        exs = ex.get("summary") or {}
        tls = tl.get("summary") or {}
        if not (exs.get("phases") and tls.get("phases")):
            return {"status": "unreadable", "artifact": _rel(tail_path, ROOT),
                    "detail": "no phase rows"}
        import etf_book_exit_liquidity as L
        import etf_book_forced_hold as FH
        ex_v = L.verdict_from_summary(exs)
        tl_v = FH.verdict_from_summary(tls)
        if exs.get("verdict") != ex_v or tls.get("verdict") != tl_v:
            return {"status": "drifted", "artifact": _rel(tail_path, ROOT),
                    "detail": "a published verdict disagrees with its own rows",
                    "verdicts": [exs.get("verdict"), tls.get("verdict")],
                    "recomputed": [ex_v, tl_v]}
        control = tls.get("control") or {}
        if not control.get("reproduced"):
            return {"status": "drifted", "artifact": _rel(tail_path, ROOT),
                    "detail": "the tail census no longer reproduces the published totals",
                    "control": control}
        ceiling = [p.get("weight_ceiling_pp") for p in (tls.get("phases") or [])
                   if p.get("weight_ceiling_pp") is not None]
        return {
            "status": "ok",
            "artifact": _rel(tail_path, ROOT),
            "sibling_artifact": _rel(exit_path, ROOT),
            "evidence_cutoff": tl.get("evidence_cutoff"),
            "sibling_cutoff": ex.get("evidence_cutoff"),
            "positions": exs.get("positions_total"),
            "below_gate": exs.get("below_gate_total"),
            "share_below_gate": exs.get("share_below_gate_mean"),
            "wait_pp": exs.get("drag_pp_mean"),
            "exit_verdict": exs.get("verdict"),
            "tail_total": tls.get("tail_total"),
            "tail_share": tls.get("tail_share"),
            "tail_pp": tls.get("pp_mean"),
            "tail_pp_min": tls.get("pp_min"),
            "tail_pp_max": tls.get("pp_max"),
            # the two halves are additive by construction (same census, same weights), so the
            # sentence that adds them is derived here rather than typed into prose.
            "combined_pp": ((round((exs["drag_pp_mean"] or 0.0) + (tls["pp_mean"] or 0.0), 4))
                            if exs.get("drag_pp_mean") is not None
                            and tls.get("pp_mean") is not None else None),
            "priced_total": tls.get("priced_total"),
            "open_at_end_total": tls.get("open_at_end_total"),
            "ceiling_min": min(ceiling) if ceiling else None,
            "ceiling_max": max(ceiling) if ceiling else None,
            "material_pp": (tl.get("criteria") or {}).get("material_pp"),
            "verdict": tl_v,
            "phases": [{"phase": p.get("phase"), "start": p.get("phase_start"),
                        "positions": p.get("positions"),
                        "tail": p.get("tail_positions"),
                        "share": p.get("tail_share_of_positions"),
                        "pp": p.get("pp_per_year"),
                        "wait_bars": p.get("mean_sale_bars")} for p in (tls.get("phases") or [])],
        }
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": _rel(tail_path, ROOT), "detail": repr(exc)}


def sellability_block(sf):
    L = []
    L.append("## 你手上这些东西，真卖得掉吗？")
    L.append("")
    if sf.get("status") != "ok":
        L.append("**这一问现在答不了。** 证据件缺席或已经对不上自己的行（%s）。"
                 % (sf.get("detail") or sf.get("status")))
        L.append("")
        return L
    share = sf.get("share_below_gate") or 0.0
    L.append("这本书选名字的时候，每一个名字都要过「最近 20 个交易日平均成交额 ≥ 2000 万」这道门；"
             "**卖的时候没人查过同一个数**。在 %d 个持仓里，有 **%d 个（%.2f%%）**的卖出落在"
             "「按自己的规则不允许买入」的名字上。"
             % (sf.get("positions") or 0, sf.get("below_gate") or 0, 100.0 * share))
    L.append("")
    L.append("分两半量：")
    L.append("")
    L.append("- **等到它重新达标再卖**：平均多等几根 bar，等待期价格 **%+.2f pp/年**（很小，"
             "而且方向是正的——跌出门槛的名字在等待期在涨）。"
             % (sf.get("wait_pp") or 0.0))
    L.append("- **不再等，见价就卖**：有 **%d 个（%.2f%%）**在 20 根内根本没等到重新达标。"
             "按「卖出后第一个有报价的 bar」成交，它们值 **%+.2f pp/年**（单个相位 %+.2f ~ %+.2f）"
             "——这是上一条把尾巴记成 0 时没有量的那一半。"
             % (sf.get("tail_total") or 0, 100.0 * (sf.get("tail_share") or 0.0),
                sf.get("tail_pp") or 0.0, sf.get("tail_pp_min") or 0.0,
                sf.get("tail_pp_max") or 0.0))
    L.append("")
    L.append("| 决策相位起点 | 持仓数 | 尾巴数 | 尾巴占比 | 尾巴值 (pp/年) | 平均要等几根 bar |")
    L.append("|---|---|---|---|---|---|")
    for p in sf.get("phases") or []:
        L.append("| %s | %d | %d | %.2f%% | %+.3f | %s |"
                 % (p.get("start"), p.get("positions") or 0, p.get("tail") or 0,
                    100.0 * (p.get("share") or 0.0), p.get("pp") or 0.0,
                    ("%.1f" % p["wait_bars"]) if p.get("wait_bars") is not None else "-"))
    L.append("")
    if sf.get("combined_pp") is not None:
        L.append("**两半加起来**（同一个持仓清点、同一套权重，所以可以相加）：卖单排队一共占 **%.2f%%** "
                 "的持仓、**%+.2f pp/年** = 等待 %+.2f + 尾巴 %+.2f。这个数是「卖出这条路一共值多少钱」，"
                 "不是净值曲线里的拖累。"
                 % (100.0 * (sf.get("share_below_gate") or 0.0), sf.get("combined_pp") or 0.0,
                    sf.get("wait_pp") or 0.0, sf.get("tail_pp") or 0.0))
        L.append("")
    _sale = ("**结论：卖得掉。** 尾巴就算按最坏的口径（占全部仓位 %.2f%% 的权重全按一年摊）"
             "天花板也只有 %.2f~%.2f pp/年，实测 %+.2f pp/年，远在 %.2f pp 这条材料线之下；"
             "而且它平均**下一根 bar 就有报价**——这些不是退市的死票，只是永远过不了自己的买入门槛。"
             % (100.0 * (sf.get("tail_share") or 0.0), sf.get("ceiling_min") or 0.0,
                sf.get("ceiling_max") or 0.0, sf.get("tail_pp") or 0.0,
                sf.get("material_pp") or 0.0))
    if sf.get("verdict") == "THE_CENSORED_TAIL_IS_MATERIAL":
        _sale = ("**结论：这一项是要付钱的。** 尾巴值 %+.2f pp/年，已经越过 %.2f pp 的材料线。"
                 % (sf.get("tail_pp") or 0.0, sf.get("material_pp") or 0.0))
    elif sf.get("verdict") != "CENSORED_TAIL_IS_IMMATERIAL":
        _sale = ("**结论：两半结论不一致**（%s）：有的相位小到可以忽略，有的越过了材料线，"
                 "不挑好看的那一半报。" % sf.get("verdict"))
    L.append(_sale)
    L.append("")
    _cens = ("%d 个尾巴持仓里 **%d 个**在面板结束前还有报价、被定价了；**%d 个**彻底不再报价，"
             "按「仍未定价」单独计数，**没有折成 0**。"
             % (sf.get("tail_total") or 0, sf.get("priced_total") or 0,
                sf.get("open_at_end_total") or 0))
    L.append(_cens)
    L.append("")
    L.append("> 口径：这是**卡住的资金的归因**，不是重算净值曲线——曲线上的年化/回撤仍按引擎自己的"
             "停牌处理。冲击成本与买卖价差不在射程；门槛本身（2000 万 / 20 个交易日）没有扫过。"
             "证据件：`%s` 与 `%s` ｜ 证据截止 %s。"
             % (str(sf.get("sibling_artifact") or "").replace(os.sep, "/"),
                str(sf.get("artifact") or "").replace(os.sep, "/"), sf.get("evidence_cutoff")))
    L.append("")
    return L


def capital_face(path=MIN_CAPITAL_JSON):
    """How much money does this book need before 8bp is even the right cost? (r1239)

    The page quoted 8bp per side everywhere and never said the assumption carries a cash
    floor: retail commission has a 5-CNY minimum, so on a small account the traded leg pays
    more than 8bp and the headline is unreachable. `etf_book_min_capital` priced that; this
    face only carries its numbers -- and its *window* block, because the neutral NAV is a
    closed form in the median traded leg, i.e. a property of the sample, not of the strategy.
    Both verdicts are re-derived through the single implementation (imported, never a copy);
    a payload whose stored token disagrees with its own rows is refused, not printed.
    """
    if not os.path.exists(path):
        return {"status": "absent", "artifact": _rel(path, ROOT), "detail": "no artifact"}
    try:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        cfg = d.get("config") or {}
        dw = cfg.get("dw_median_all_legs")
        ladder = d.get("ladder") or []
        sched = (cfg.get("schedules") or [{}])[0]
        if dw is None or not ladder or not sched:
            return {"status": "unreadable", "artifact": _rel(path, ROOT),
                    "detail": "no traded-leg median or no ladder"}
        import etf_book_min_capital as MC
        model = MC.neutral_nav(dw, cfg.get("base_bp_published"), sched.get("min_fee_cny"))
        real = MC.neutral_nav(dw, sched.get("prop_bp"), sched.get("min_fee_cny"))
        for got, want, tag in ((d.get("fee_neutral_vs_model_nav"), model, "model"),
                               (d.get("fee_neutral_vs_real_nav"), real, "real")):
            if got is None or abs(got - want) > 0.02:
                return {"status": "drifted", "artifact": _rel(path, ROOT),
                        "detail": "the %s neutral NAV disagrees with its own traded-leg median" % tag,
                        "published": got, "recomputed": round(want, 2)}
        # (r1506) the delivered-rate column is the SAME closed form read at the rate the
        # card configures. If it no longer recomputes from its own median leg, this page
        # would print a threshold belonging to no book -- refuse rather than print.
        dlv_bp = cfg.get("base_bp_delivered")
        dlv_nav = d.get("fee_neutral_vs_delivered_nav")
        if dlv_bp is not None and dlv_nav is not None:
            want_d = MC.neutral_nav(dw, dlv_bp, sched.get("min_fee_cny"))
            if abs(dlv_nav - want_d) > 0.02:
                return {"status": "drifted", "artifact": _rel(path, ROOT),
                        "detail": "the delivered-rate neutral NAV disagrees with its own "
                                  "traded-leg median",
                        "published": dlv_nav, "recomputed": round(want_d, 2)}
        # (r1507) the lot block is the second smallness threshold, same closed form on the
        # same published medians. If it no longer recomputes, this page would print a
        # "you need this much money" belonging to no basket -- refuse, do not print.
        lot = d.get("lot") or {}
        if lot.get("lot_nav_median") is not None:
            want_lot = MC.lot_nav(lot.get("price_median"), lot.get("weight_median"),
                                  lot.get("lot_units") or MC.LOT_UNITS)
            if want_lot is None or abs(float(want_lot) - float(lot["lot_nav_median"])) > \
                    max(0.05, 1e-4 * abs(float(want_lot))):
                return {"status": "drifted", "artifact": _rel(path, ROOT),
                        "detail": "the whole-lot threshold disagrees with its own median "
                                  "price and weight",
                        "published": lot.get("lot_nav_median"),
                        "recomputed": (None if want_lot is None else round(want_lot, 2))}
            want_lv = MC._lot_verdict(want_lot, lot.get("compared_value"))
            if want_lv != lot.get("verdict"):
                return {"status": "drifted", "artifact": _rel(path, ROOT),
                        "detail": "the whole-lot verdict disagrees with its own two "
                                  "thresholds",
                        "published": lot.get("verdict"), "recomputed": want_lv}
        primary = [r for r in ladder if r.get("schedule") == sched.get("name")]
        want_v = MC._verdict(primary, model, real,
                             (min(cfg.get("capital_grid") or [0]),
                              max(cfg.get("capital_grid") or [0])))
        if want_v != d.get("verdict"):
            return {"status": "drifted", "artifact": _rel(path, ROOT),
                    "detail": "the ladder verdict disagrees with its own rows",
                    "published": d.get("verdict"), "recomputed": want_v}
        win = d.get("window") or {}
        wrows = win.get("rows") or []
        want_wv, want_ws = (MC._window_verdict(wrows, model) if wrows
                            else ("WINDOW_UNMEASURED", None))
        if wrows and win.get("verdict") != want_wv:
            return {"status": "drifted", "artifact": _rel(path, ROOT),
                    "detail": "the window token disagrees with its own rows",
                    "published": win.get("verdict"), "recomputed": want_wv}
        small = min(primary, key=lambda r: r.get("capital") or 0) if primary else {}
        big = max(primary, key=lambda r: r.get("capital") or 0) if primary else {}
        _tk_w, _tk_bar = _ticket_width()
        wid = d.get("width") or {}
        xrows = wid.get("rows") or []
        if xrows:
            want_xv, _want_xs = MC._width_verdict(xrows, model)
            if wid.get("verdict") != want_xv:
                return {"status": "drifted", "artifact": _rel(path, ROOT),
                        "detail": "the width token disagrees with its own rows",
                        "published": wid.get("verdict"), "recomputed": want_xv}
            want_pw = MC._delivered_width(xrows, model)
            if want_pw != wid.get("published_path_width"):
                return {"status": "drifted", "artifact": _rel(path, ROOT),
                        "detail": "the width this ladder was priced on disagrees with its rows",
                        "published": wid.get("published_path_width"),
                        "recomputed": want_pw}
        # (r1241) the headline must be priced on the basket the reader is holding: the
        # ladder's own width, the width its rows point at, and the delivered card must be
        # the same number. Before this leg the page printed a 5-name threshold next to a
        # 12-name card and only warned in prose.
        _lad_w = cfg.get("ladder_n_hold")
        _del_w = _delivered_names()
        if _lad_w is not None and _del_w is not None and int(_lad_w) != int(_del_w):
            return {"status": "drifted", "artifact": _rel(path, ROOT),
                    "detail": "the ladder is priced on %s names but the delivered card holds %s"
                              % (_lad_w, _del_w),
                    "published": _lad_w, "recomputed": _del_w}
        return {
            "status": "ok",
            "artifact": _rel(path, ROOT),
            "evidence_cutoff": d.get("evidence_cutoff"),
            "dw_median": dw,
            "model_nav": d.get("fee_neutral_vs_model_nav"),
            "real_nav": d.get("fee_neutral_vs_real_nav"),
            "model_nav_mean_leg": d.get("fee_neutral_vs_model_nav_mean_leg"),
            "ladder_n_hold": cfg.get("ladder_n_hold"),
            "ladder_n_hold_source": cfg.get("ladder_n_hold_source"),
            "ladder_dw_median": cfg.get("dw_median_all_legs"),
            "ladder_dw_mean": cfg.get("dw_mean_all_legs"),
            "base_bp": cfg.get("base_bp_published"),
            "delivered_bp": dlv_bp,
            "delivered_rate_source": cfg.get("delivered_rate_source"),
            "delivered_rate_check": cfg.get("delivered_rate_check"),
            "delivered_nav": dlv_nav,
            "delivered_nav_mean_leg": d.get("fee_neutral_vs_delivered_nav_mean_leg"),
            "delivered_verdict": d.get("verdict_delivered"),
            "delivered_rate_note": d.get("delivered_rate_note"),
            "lot": ({"median": lot.get("lot_nav_median"),
                     "cellwise_median": lot.get("lot_nav_cellwise_median"),
                     "p90": lot.get("lot_nav_p90"),
                     "units": lot.get("lot_units"),
                     "price_median": lot.get("price_median"),
                     "weight_median": lot.get("weight_median"),
                     "verdict": lot.get("verdict"),
                     "compared_value": lot.get("compared_value"),
                     "compared_against": lot.get("compared_against"),
                     "holdable_at": [{"capital": r.get("capital"),
                                      "share": r.get("holdable_share")}
                                     for r in lot.get("rows") or []],
                     "names_short_at_smallest": lot.get("names_short_at_smallest")}
                    if lot.get("lot_nav_median") is not None else None),
            "prop_bp": sched.get("prop_bp"),
            "min_fee_cny": sched.get("min_fee_cny"),
            "schedule": sched.get("name"),
            "verdict": want_v,
            "small_capital": small.get("capital"),
            "small_cagr": small.get("cagr"),
            "small_ref_cagr": small.get("ref_cagr"),
            "small_delta_pp": small.get("delta_vs_8bp_pp"),
            "small_fee_cny": small.get("fee_cny_total"),
            "big_capital": big.get("capital"),
            "big_delta_pp": big.get("delta_vs_8bp_pp"),
            "window_verdict": want_wv,
            "window_spread_pct": win.get("spread_pct_of_published"),
            "window_tol_pct": win.get("stability_tol_pct"),
            "windows": [{"window": r.get("window"), "first_bar": r.get("first_bar"),
                         "last_bar": r.get("last_bar"),
                         "dw_median": r.get("dw_median"),
                         "dw_mean": r.get("dw_mean"),
                         "model_nav": r.get("fee_neutral_vs_model_nav"),
                         "model_nav_mean_leg": r.get("fee_neutral_vs_model_nav_mean_leg"),
                         "delivered_nav": r.get("fee_neutral_vs_delivered_nav"),
                         "real_nav": r.get("fee_neutral_vs_real_nav")}
                        for r in wrows],
            "width_verdict": want_xv if xrows else "WIDTH_UNMEASURED",
            "width_spread_pct": wid.get("spread_pct_of_published"),
            "width_tol_pct": wid.get("stability_tol_pct"),
            "published_path_width": wid.get("published_path_width"),
            "widths": [{"n_hold": r.get("n_hold"),
                        "names_median": r.get("names_median"),
                        "dw_median": r.get("dw_median"),
                        "model_nav": r.get("fee_neutral_vs_model_nav"),
                        "delivered_nav": r.get("fee_neutral_vs_delivered_nav"),
                        "cagr_8bp": r.get("cagr_8bp")}
                       for r in xrows],
            "delivered_n_hold": _delivered_names(),
            "ticket_n_hold": _tk_w,
            "ticket_bar": _tk_bar,
            "ticket_model_nav": (next((r.get("fee_neutral_vs_model_nav") for r in xrows
                                       if r.get("n_hold") == _tk_w), None)
                                 if _tk_w is not None else None),
            # (r1506) the sheet on the table must be priced in the rate the sheet pays
            "ticket_delivered_nav": (next((r.get("fee_neutral_vs_delivered_nav") for r in xrows
                                           if r.get("n_hold") == _tk_w), None)
                                     if _tk_w is not None else None),
            "ticket_narrower_than_path": (None if (_tk_w is None or not wid.get("published_path_width"))
                                          else (_tk_w != wid.get("published_path_width"))),
            "width_mismatch": (None if (_delivered_names() is None
                                        or not wid.get("published_path_width"))
                               else (_delivered_names() != wid.get("published_path_width"))),
        }
    except Exception as exc:                                    # noqa: BLE001
        return {"status": "unreadable", "artifact": _rel(path, ROOT), "detail": repr(exc)}


def _delivered_names(path=None):
    """How many names the delivered card actually holds (read from its own payload).

    The capital face prices a basket; the card ships a basket. If the two differ, the
    floor printed on this page belongs to a book the reader does not hold -- a mismatch
    this page must be able to SEE rather than infer from two documents.
    """
    path = path or os.path.join(ROOT, "results", "etf_book_production", "latest.json")
    try:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        n = (d.get("config") or {}).get("n_hold")
        return int(n) if n is not None else None
    except Exception:                                           # noqa: BLE001
        return None


def _ticket_width():
    """How many names TODAY's executable ticket holds (r1244).

    The card configures a basket and the ladder is priced on that basket; the ticket a
    reader can actually place this session is a third number (5 names today, ~53% cash).
    The closed form is the same, the denominator is not -- so the page must be able to
    name the basket that is on the table instead of quoting the card's width at a reader
    holding another book.
    """
    try:
        _ptr, tk, _path = _load_ticket()
    except Exception:                                           # noqa: BLE001
        return None, None
    t = tk.get("ticket") or {}
    n = tk.get("n_hold")
    if n is None:
        n = len(t.get("order") or []) or None
    try:
        n = int(n) if n is not None else None
    except (TypeError, ValueError):
        n = None
    return n, tk.get("evidence_cutoff")


def capital_block(cf):
    L = []
    L.append("## 要用多少钱，才谈得上「这本书自己的每边成本」？")
    L.append("")
    if cf.get("status") != "ok":
        L.append("**这一问现在答不了。** 证据件缺席，或者它已经对不上自己的行（%s）。"
                 % (cf.get("detail") or cf.get("status")))
        L.append("")
        return L
    model_nav = cf.get("model_nav") or 0.0
    real_nav = cf.get("real_nav") or 0.0
    _bp_shelf = cf.get("base_bp") or 0.0
    _bp_dlv = cf.get("delivered_bp")
    _two_rates = bool(_bp_dlv) and abs(float(_bp_dlv) - _bp_shelf) > 1e-9
    L.append("费率是一个比例，没有地板；真实券商的佣金有 **每笔最少 %g 元**。"
             "一次换手里每个名字只动账户的 **%.2f%%**，所以账户越小，那 5 元越像一张固定门票。"
             % (cf.get("min_fee_cny") or 0.0, 100.0 * (cf.get("dw_median") or 0.0)))
    L.append("")
    if _two_rates:
        _agree = (cf.get("delivered_rate_check") or {}).get("agree")
        L.append("**这一节有两把尺子，先说清楚哪把是你手上的。** 这张要下的单按 **%g bp 每边**算"
                 "（读自卡片自己的 `cost_bp_per_side`，与票据引擎%s）；本页别处的历史年化仍按 "
                 "**%g bp** 算——那是这张货架上已发表数字的口径，不改。下面两个门槛并列印，"
                 "**不许相加、不许互相替代**：你手上这本要过的是 **%g bp 那一行**。"
                 % (_bp_dlv, {True: "一致", False: "**不一致**（两处已如实标注，不替它们选边）",
                              None: "无法交叉核对"}[_agree], _bp_shelf, _bp_dlv))
        L.append("")
        if cf.get("delivered_nav"):
            L.append("> 你手上这本的门槛（**%g bp**）是 **%.0f 元**；货架口径（%g bp）是 %.0f 元。"
                     "两个数并列，下面是它们各自怎么来的。"
                     % (_bp_dlv, cf["delivered_nav"], _bp_shelf, model_nav))
            L.append("")
    else:
        L.append("这本书的每一处成本都按 **%g bp 每边**算（外加冲击项），与卡片配置是同一把尺子。"
                 % _bp_shelf)
        L.append("")
    _lad_w = cf.get("ladder_n_hold")
    if cf.get("ladder_n_hold_source") == "production_card":
        L.append("**下面的门槛是按 %s 名的篮子算的**（宽度取自卡片本身，"
                 "`results/etf_book_production/latest.json`）——这正是你手上这本。"
                 % (_lad_w if _lad_w is not None else "？"))
    else:
        L.append("**下面的门槛按 %s 名算，但这个宽度不是从卡片读到的**（卡片配置缺席或读不出），"
                 "退回引擎默认——换言之它未必是你在持的那本，先看宽度表再引用。"
                 % (_lad_w if _lad_w is not None else "？"))
    L.append("")
    if _two_rates and cf.get("delivered_nav"):
        L.append("- **（你手上这本，%g bp）低于约 %.0f 元**：5 元地板就压过 %g bp，模型比真实便宜。"
                 "费率越高、地板越早松手（闭式解 = 10000 × 5 元 ÷（费率 × 换手）），"
                 "所以它比货架口径的 %.0f 元低 **%.1f%%**——以前这一行印的是货架的数，"
                 "会把「要多大的账户」说得偏大。"
                 % (_bp_dlv, cf["delivered_nav"], _bp_dlv, model_nav,
                    (100.0 * (model_nav - cf["delivered_nav"]) / model_nav)
                    if model_nav else 0.0))
    L.append("- **（货架口径 %g bp）低于约 %.0f 元**：5 元地板压过 %g bp，模型比真实便宜——"
             "%.0f 元账户的年化只剩 **%.2f%%**（同一路径、同一冲击项，按 %g bp 算是 **%.2f%%**），"
             "全窗佣金 **%.0f 元**，相当于把起始本金吃掉一大块。"
             % (_bp_shelf, model_nav, _bp_shelf, cf.get("small_capital") or 0.0,
                100.0 * (cf.get("small_cagr") or 0.0), _bp_shelf,
                100.0 * (cf.get("small_ref_cagr") or 0.0), cf.get("small_fee_cny") or 0.0))
    L.append("- **高于约 %.0f 元**：地板不再咬人，而万 %g 只有 %g bp——"
             "这时是 **%g bp 假设自己在多收钱**，同一个算术反向成立（%.0f 元账户 **%+.2f pp/年** 之差）。"
             "这一行与上面的费率无关：两边比的是券商价与 %g bp，地板早就退场了。"
             % (real_nav, cf.get("prop_bp") or 0.0, cf.get("prop_bp") or 0.0,
                _bp_dlv if _two_rates else _bp_shelf,
                cf.get("big_capital") or 0.0, cf.get("big_delta_pp") or 0.0,
                _bp_dlv if _two_rates else _bp_shelf))
    L.append("")
    spread = cf.get("window_spread_pct")
    if cf.get("window_verdict") == "BREAKEVEN_WINDOW_STABLE":
        L.append("**这个门槛是稳的**：换样本只动了 %.1f%%（冻结容差 %g%%），可以当常数用。"
                 % (spread or 0.0, cf.get("window_tol_pct") or 0.0))
    elif spread is not None:
        L.append("**不过它不是一个常数。** 门槛是「平均每个仓位动多少」的闭式解，而那个数由样本决定："
                 "同一套规则在三个样本上分别是 %s，极差 **%.1f%%**（冻结容差 %g%%，按货架口径算）——"
                 "所以「至少要 %.0f 元」是**这段行情**的说法，不是这条策略的常数。"
                 % ("、".join("%.0f 元（%s）" % (w.get("model_nav") or 0.0,
                                                str(w.get("window") or "").replace("_", " "))
                              for w in cf.get("windows") or [] if w.get("model_nav") is not None),
                    spread, cf.get("window_tol_pct") or 0.0,
                    (cf.get("delivered_nav") if _two_rates else model_nav) or 0.0))
        # if the median reading is being carried by a degenerate leg, say what the
        # amount-weighted reading says about the SAME samples, through the same rule
        _mv = [{"window": w.get("window"),
                "fee_neutral_vs_model_nav": w.get("model_nav_mean_leg")}
               for w in cf.get("windows") or [] if w.get("model_nav_mean_leg")]
        if len(_mv) >= 2:
            import etf_book_min_capital as _MCmm
            _mtok, _msp = _MCmm._window_verdict(_mv, model_nav)
            if _msp is not None and spread and _msp < spread / 3.0:
                L.append("按「平均那一笔」（按金额加权，下表解释两种读法）读同一组样本，"
                         "平衡点是 %s，极差 **%.1f%%**——没有中位数读数那么极端，"
                         "但同样不是常数。"
                         % ("、".join("%.0f 元" % r["fee_neutral_vs_model_nav"] for r in _mv),
                            _msp))
    L.append("")
    L.append("| 样本 | 起 | 止 | 平均每仓位换手 | %gbp 与券商费率的平衡点 | %gbp 与万%g 的平衡点 |"
             % (_bp_shelf, _bp_shelf, cf.get("prop_bp") or 0.0)
             + (" %gbp 平衡点（你手上这本） |" % _bp_dlv if _two_rates else ""))
    L.append("|---|---|---|---|---|---|" + ("---|" if _two_rates else ""))
    for w in cf.get("windows") or []:
        L.append("| %s | %s | %s | %.2f%% | %s | %s |%s"
                 % (str(w.get("window") or "").replace("_", " "), w.get("first_bar"),
                    w.get("last_bar"), 100.0 * (w.get("dw_median") or 0.0),
                    ("%.0f 元" % w["model_nav"]) if w.get("model_nav") is not None else "-",
                    ("%.0f 元" % w["real_nav"]) if w.get("real_nav") is not None else "-",
                    (((" %.0f 元 |" % w["delivered_nav"]) if w.get("delivered_nav") is not None
                      else " - |") if _two_rates else "")))
    # (r1241) the window table has two honest readings: the median leg (what the typical
    # single trade is worth -- where a per-trade floor bites hardest) and the mean leg
    # (amount-weighted -- what the account actually pays). In a thin universe they can be
    # a factor of 30 apart, and a table that prints only one of them reads as a bug.
    _mm = [(str(w.get("window") or "").replace("_", " "), w.get("model_nav"),
            w.get("model_nav_mean_leg")) for w in cf.get("windows") or []]
    _mm = [t for t in _mm if t[1] and t[2]]
    if _mm:
        _worst = max(_mm, key=lambda t: max(t[1] / t[2], t[2] / t[1]))
        _ratio = max(_worst[1] / _worst[2], _worst[2] / _worst[1])
        if _ratio > 3.0:
            L.append("")
            L.append("**这张表有两种读法，最远差 %.0f 倍。** 表里印的是「中位数那一笔」——"
                     "盘里大多数换手只是把某个名字的量修一点点，按这一笔算，5 元门票在任何账户"
                     "规模上都压过 8bp（%s 读到 **%.0f 元**）；换成「平均那一笔」（按金额加权）"
                     "读同一个样本，是 **%.0f 元**。地板是**每笔**收的，所以两个数都真，"
                     "问的不是同一件事：前者答「最抠的那一笔要多少钱才不亏」，"
                     "后者答「这个账户日常要付多少佣金」。判词仍取自中位数（冻结口径）。"
                     % (_ratio, _worst[0], _worst[1], _worst[2]))
    L.append("")
    wid_rows = cf.get("widths") or []
    wspread = cf.get("width_spread_pct")
    if wid_rows and cf.get("width_verdict") not in (None, "WIDTH_UNMEASURED"):
        pw = cf.get("published_path_width")
        L.append("**同一个门槛也随篮子宽度移动。** 上面的每一档都是按 **%s 名**的篮子算的"
                 "（这一条是从行本身认出来的，不是写死的）；名字越多，每个仓位动得越小，5 元地板就"
                 "咬得更晚：%s。极差 **%.1f%%**（冻结容差 %g%%）。"
                 % (("这 %d" % pw) if pw else "某个未在扫描里的",
                    "、".join("%d 名 %.0f 元" % (w.get("n_hold"), w.get("model_nav"))
                              for w in wid_rows if w.get("model_nav") is not None),
                    wspread or 0.0, cf.get("width_tol_pct") or 0.0))
        L.append("")
        if cf.get("width_mismatch"):
            _pv = cf.get("published_path_width")
            _dv = cf.get("delivered_n_hold")
            _hit = next((w for w in wid_rows if w.get("n_hold") == _dv), {})
            L.append("**⚠ 这一节的门槛是拿 %s 名的篮子算的，而卡片配置写的是 %s 名。** "
                     "同一套规则在 %s 名上重算，平衡点是 **%s**——比印在上面的数高。"
                     "换宽度就是换分母，门槛不是这一层的常数，读之前先对齐篮子宽度。"
                     % (_pv, _dv, _dv,
                        ("%.0f 元" % _hit["model_nav"]) if _hit.get("model_nav") is not None
                        else "（未扫到该宽度）"))
            L.append("")
        L.append("| 篮子宽度 | 实际持名（中位） | 平均每仓位换手 | %gbp 平衡点 | %gbp 下年化 |"
                 % (_bp_shelf, _bp_shelf)
                 + (" %gbp 平衡点（你手上这本） |" % _bp_dlv if _two_rates else ""))
        L.append("|---|---|---|---|---|" + ("---|" if _two_rates else ""))
        for w in wid_rows:
            L.append("| %s 名 | %s | %.2f%% | %s | %s |%s"
                     % (w.get("n_hold"),
                        ("%.1f" % w["names_median"]) if w.get("names_median") is not None else "-",
                        100.0 * (w.get("dw_median") or 0.0),
                        ("%.0f 元" % w["model_nav"]) if w.get("model_nav") is not None else "-",
                        ("%.2f%%" % (100.0 * w["cagr_8bp"])) if w.get("cagr_8bp") is not None else "-",
                        (((" %.0f 元 |" % w["delivered_nav"]) if w.get("delivered_nav") is not None
                          else " - |") if _two_rates else "")))
        L.append("")
    # (r1244) a third basket: the card configures one, the ladder is priced on it, and the
    # ticket a reader can place this session holds a third width. Saying it in prose was the
    # r1240 gap; naming it with its own break-even is the same rule applied to the sheet the
    # reader actually has.
    _tw = cf.get("ticket_n_hold")
    _pw2 = cf.get("published_path_width")
    if _tw is not None and _tw != _pw2:
        _th = cf.get("ticket_delivered_nav") if _two_rates else cf.get("ticket_model_nav")
        L.append("**今天这张可执行单实际持 %d 名**（bar %s），而这一节的门槛是按 **%s 名**算的。"
                 "同一闭式在 %d 名上重算%s，平衡点是 **%s**——这才是你手上这张单的那一本。"
                 % (_tw, cf.get("ticket_bar") or "？", _pw2, _tw,
                    ("（按 %g bp）" % _bp_dlv) if _two_rates else "",
                    ("%.0f 元" % _th) if _th is not None else "（宽度扫描里没有这一档，未量）"))
    elif _tw is not None:
        L.append("**今天这张可执行单持有 %d 名**（bar %s），与这一节定价的篮子宽度一致。"
                 % (_tw, cf.get("ticket_bar") or "？"))
    elif wid_rows:
        L.append("**今天这张可执行单的持名数读不出来**（票据缺席或没有 `n_hold`）——"
                 "所以上面那个门槛是在量哪一本，本页答不了，别按它下单。")
    L.append("")
    # (r1507) the second smallness constraint. The section above answers "is the fee model
    # honest at this size"; this one answers "can the book be held at this size at all".
    # They are the same order of magnitude and they are not the same question, so both are
    # printed, each with the number it is actually about.
    _lot = cf.get("lot") or {}
    if _lot.get("median"):
        _lu = _lot.get("units") or 100
        _lpx = _lot.get("price_median") or 0.0
        _lw = _lot.get("weight_median") or 0.0
        _lm = _lot.get("median") or 0.0
        _lp = _lot.get("p90") or 0.0
        _cmp = _lot.get("compared_value") or 0.0
        _lot_bigger = _lot.get("verdict") == "LOT_IS_THE_LARGER_REQUIREMENT"
        L.append("**还有一条更硬的约束：一手 = %d 份，买不到半手。** 上面那句答的是「贵不贵」，"
                 "这一条答的是「摆不摆得下」——一个仓位中位占账户 **%.2f%%**、单价中位 "
                 "**%.2f 元**，一手就是 **%.0f 元**的仓位。按规则里的权重把这本书摆满，"
                 "至少要有 **%.0f 元**；要让九成名字都各持一手，得 **%.0f 元**"
                 "（这个上限由最贵的那几个名字决定，不是平均值）。"
                 % (_lu, 100.0 * _lw, _lpx, _lu * _lpx, _lm, _lp))
        L.append("")
        if _lot_bigger:
            L.append("这个数 **高于** 5 元地板的门槛（%.0f 元）——所以小账户先撞上的不是「贵」，"
                     "是「摆不下」：钱不够时你不是买贵了这本，你是**买成了另一本**"
                     "（少买几个名字、或者每个名字多买一手把权重撑歪）。" % _cmp)
        else:
            L.append("这个数 **低于** 5 元地板的门槛（%.0f 元）——先撞上的是「贵」。"
                     "但两者问的不是同一件事：地板说「这笔佣金占得太高」，"
                     "手数说「这个仓位根本摆不出来」；钱再少一点，买到的就不再是这本书。"
                     % _cmp)
        _ha = [h for h in _lot.get("holdable_at") or [] if h.get("share") is not None]
        if _ha:
            L.append("")
            L.append("| 账户 | 能按规则权重摆出的名字占比 |")
            L.append("|---|---|")
            for h in _ha:
                L.append("| %.0f 元 | %.1f%% |"
                         % (h.get("capital") or 0.0, 100.0 * (h.get("share") or 0.0)))
        L.append("")
    L.append("> 口径：只算佣金与既有的冲击项。买卖价差已经在上面那把费率里"
             + ("（货架 %g bp / 你手上这本 %g bp）" % (_bp_shelf, _bp_dlv) if _two_rates
                else "（%g bp）" % _bp_shelf)
             + "，**没有再叠加一次**。"
             "资本在每一档内保持恒定，所以「小账户差多少」只归因于费率、不掺第二个变量。"
             "没有 5 元地板的券商（`wan%g+0`）在 1 万元上也不会被咬。"
             "证据件：`%s` ｜ 证据截止 %s。"
             % (cf.get("prop_bp") or 0.0,
                str(cf.get("artifact") or "").replace(os.sep, "/"), cf.get("evidence_cutoff")))
    L.append("")
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


CASH_MONEY_TAIL = 250


def cash_money_face(cash_amount, ticket=None, panel_dir=REPO_DIR, tail=CASH_MONEY_TAIL):
    """The order sheet's three-rate cash pricing, applied to the money this page shows.

    (r1246) The ticket learned (r1245) to price its idle half in CNY at the quote it
    actually pays today, at its own trailing mean and at the ledger's window mean; this
    page kept quoting one of the three, so the CEO one-pager and the sheet described the
    same cash at different calibers. Both documents describe the same money, so the
    function is imported from scripts/etf_book_order instead of being copied here -- a
    second copy is exactly how two faces drift apart while each still looks right.
    Unreadable inputs stay None with a stated reason, never 0.
    """
    ticket = ticket or {}
    out = {"status": "absent", "source": None, "tail": int(tail), "block": None,
           "note": None}
    try:
        cash = float(cash_amount)
    except (TypeError, ValueError):
        cash = 0.0
    if cash <= 0:
        out["note"] = "现金腿金额读不出来（不是 0，是不知道）"
        return out
    # (r1246) the ticket already priced this exact money. Consume that block instead of
    # re-deriving it: round-tripping through `mean_accrual_ann_pct` (3 dp) printed 11,041
    # here against the sheet's 11,039 -- the same cash at two calibers, which is the very
    # defect this face exists to remove. Only when the two cash amounts differ (a page
    # built off a different snapshot) does this recompute, and then it refuses the window
    # row rather than borrowing the ticket's accrual for a different pile of money.
    money = ((ticket.get("cash_leg") or {}).get("money") or {})
    m_cash = money.get("cash_amount_cny")
    if m_cash is not None:
        try:
            same = abs(float(m_cash) - cash) <= 0.01
        except (TypeError, ValueError):
            same = False
        if same:
            out["block"] = money
            out["source"] = "票据 cash_leg.money（逐字消费）"
            out["status"] = ("ok" if money.get("verdict")
                             and money.get("verdict") != "CANNOT_PRICE" else "unpriced")
            if out["status"] != "ok":
                out["note"] = money.get("sentence") or "票据说这一半不可定价"
            return out
        out["note"] = ("票据那一份现金是 ¥%s，这一页是 ¥%s —— 不是同一笔钱，"
                       "所以窗口口径不往下借"
                       % (format(float(m_cash), ",.0f"), format(cash, ",.0f")))
    else:
        out["note"] = "票据没有为这一半定价（没有 cash_leg.money），窗口口径不印"
    rows = repo_rows(CASH_LEG_SYMBOL, panel_dir)
    if not rows:
        out["note"] = "%s 面板缺席" % CASH_LEG_SYMBOL
        return out
    try:
        import etf_book_order as _ORD
    except Exception as exc:                 # a broken sibling must not blank the page
        out["note"] = "定价模块取不到（%s）" % exc.__class__.__name__
        return out
    try:
        import pandas as _pd
    except Exception as exc:
        out["note"] = "pandas 不可用（%s）" % exc.__class__.__name__
        return out
    rates = _pd.Series([v for _, v in rows],
                       index=_pd.to_datetime([d.isoformat() for d, _ in rows]))
    asof = ticket.get("evidence_cutoff") or rows[-1][0].isoformat()
    blk = _ORD.cash_money(cash, rates, asof, tail=tail)
    blk["sentence"] = ((blk.get("sentence") or "") +
                       "（窗口口径缺席：这一页的现金不是票据定价的那一笔）").strip()
    out["block"] = blk
    out["source"] = "scripts/etf_book_order.cash_money（页自己重算，无窗口行）"
    out["status"] = "ok" if blk.get("verdict") and blk["verdict"] != "CANNOT_PRICE" else "unpriced"
    if out["status"] != "ok":
        out["note"] = blk.get("sentence") or "定价面返回不可定价"
    return out


def cash_money_block(cm):
    """Three rates on the same cash, and what picking the flattering one would cost (r1246)."""
    L = []
    L.append("## 同一笔现金，三种利率口径差多少钱")
    L.append("")
    if cm.get("status") != "ok":
        L.append("**这一问现在答不了。** %s —— 不印 0，也不拿别的口径顶上。"
                 % (cm.get("note") or cm.get("status")))
        L.append("")
        return L
    b = cm.get("block") or {}
    cash = float(b.get("cash_amount_cny") or 0.0)
    spot = b.get("spot") or {}
    tail_b = b.get("mean_tail") or {}
    win = b.get("window") or {}
    base = spot.get("pct")
    L.append("这 ¥%s 放在逆回购里，一年赚多少取决于拿哪个利率去乘它。三个都是这张面板自己的读数、"
             "不是预测；并排印出来，是因为「按历史均值去算」会让账面以为有另一笔钱。"
             % format(cash, ",.0f"))
    L.append("")
    L.append("| 口径 | 年化 | 一年约赚 | 比今天的报价 |")
    L.append("|---|---|---|---|")

    def _row(label, pct, annual, is_base=False):
        if pct is None:
            return "| %s | — | — | — |" % label
        if is_base or base is None:
            delta = "—"
        else:
            dpct = (float(pct) - float(base)) * 100.0
            dcny = float(annual or 0) - float(spot.get("annual_cny") or 0)
            delta = "%+.0f bp / %s¥%s" % (dpct, "+" if dcny >= 0 else "-",
                                          format(abs(dcny), ",.0f"))
        return "| %s | %.2f%% | %s | %s |" % (
            label, float(pct),
            ("**¥%s**" % format(annual, ",.0f")) if annual is not None else "—", delta)

    L.append(_row("**今天的报价**（%s）" % (spot.get("date") or "—"), base,
                  spot.get("annual_cny"), is_base=True))
    L.append(_row("自己近 %d 个报价的均值" % (spot.get("quotes") or cm.get("tail") or 0),
                  tail_b.get("pct"), tail_b.get("annual_cny")))
    if win.get("pct") is not None:
        L.append(_row("账本自己走过的全窗均值", win.get("pct"), win.get("annual_cny")))
    L.append("")
    verdict = b.get("verdict")
    if verdict == "RATES_FELL":
        L.append("**今天能拿到的是第一行。** 它比自己近一段的均值低 **%.2f pp**——"
                 "照均值算会以为一年多赚 **¥%s**，那是利率掉下来的差，不是这个月选错了票；"
                 "把历史平均收益率写进预期，等于给账面多记一笔钱。"
                 % (float(tail_b.get("pct") or 0.0) - float(base or 0.0),
                    format(abs(float(b.get("spread_vs_tail_cny") or 0.0)), ",.0f")))
    elif verdict == "RATES_ROSE":
        L.append("**今天能拿到的比自己的均值高**（%+.0f bp，一年多 **¥%s**）——季末/节前的飙高是常态，"
                 "别把这个差当成常常有，往后还是按均值算。"
                 % ((float(base or 0.0) - float(tail_b.get("pct") or 0.0)) * 100.0,
                    format(abs(float(b.get("spread_vs_tail_cny") or 0.0)), ",.0f")))
    else:
        L.append("**今天的报价就在它自己的均值上**（差 %.0f bp，在冻结的 %.0f bp 噪声带内）——"
                 "这三个口径挑哪个都不算撒谎，但利率一变，第一行就不在这了。"
                 % (abs(float(base or 0.0) - float(tail_b.get("pct") or 0.0)) * 100.0,
                    float(b.get("fall_bp") or 0.0)))
    if win.get("pct") is not None:
        L.append("")
        L.append("- 第三行是回测账本 accrued 用的利率（历史全窗均值 %.2f%%）：它说的是「过去这些年现金值多少」，"
                 "不是今天这 ¥%s 的收益率 —— 同一笔钱在首末两行之间能差 **¥%s**。"
                 % (float(win["pct"]), format(cash, ",.0f"),
                    format(abs(float(win.get("annual_cny") or 0)
                               - float(spot.get("annual_cny") or 0)), ",.0f")))
    L.append("- 这三个数都不是收益来源：现金的活是「不缩水」，要收益得靠上面那些票。")
    L.append("")
    return L


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


def build(with_stress=False, window_label=None):
    """Assemble the page. `window_label` lets a caller pin the row-label face.

    r1251: without it, a selftest that checks "the full column carries the full window"
    could only be written against whatever the artifact happened to hold that morning -- the
    legs then pass on a coincidence and go red the day the panel re-prices the book.
    """
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
    page_window_label = window_label if window_label is not None else window_label_face()
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
        "cash_money": cash_money_face(cash_amt, tk),
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
    page["sample_window"] = sample_window_face()
    page["universe_lock"] = universe_lock_face()
    page["entry_gate"] = entry_gate_face()
    page["live_quote"] = live_quote_face()
    page["sellability"] = sellability_face()
    page["capital"] = capital_face()
    page["gap"] = gap_face()
    page["permission"] = permission_face()
    page["premium_leak"] = premium_face()
    page["premium_forward"] = premium_forward_face(tk.get("ticket") or {})
    page["sibling_gap"] = sibling_gap_face()
    page["floor_provenance"] = floor_provenance_face()
    page["vol_target_gate"] = vol_target_face()
    page["positions"] = positions_face()
    page["executed"] = executed_face(tk)
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
    for _ex_line in executed_block(p.get("executed") or {},
                                   sheet_symbols=[o.get("symbol") for o in (p.get("order") or [])]):
        add(_ex_line)
    for _pf_line in permission_block(p.get("permission") or {}):
        add(_pf_line)
    for _pl_line in premium_block(p.get("premium_leak") or {}, page_bar=p.get("priced_bar"),
                                  page_sheet={"amount_cny": p.get("book_amount_cny"),
                                              "legs": [{"symbol": o.get("symbol"),
                                                        "amount_cny": o.get("amount_cny")}
                                                       for o in (p.get("order") or [])]}):
        add(_pl_line)
    for _pfw_line in premium_forward_block(p.get("premium_forward") or {},
                                           page_bar=p.get("priced_bar")):
        add(_pfw_line)
    for _sg_line in sibling_gap_block(p.get("sibling_gap") or {}, page_bar=p.get("priced_bar")):
        add(_sg_line)
    for _fp_line in floor_provenance_block(p.get("floor_provenance") or {},
                                           vt=p.get("vol_target_gate") or {},
                                           page_bar=p.get("priced_bar")):
        add(_fp_line)
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
    for _cm_line in cash_money_block(p.get("cash_money") or {}):
        add(_cm_line)
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
    for _ps_line in positions_block(p.get("positions") or {}, page_bar=p.get("priced_bar")):
        add(_ps_line)
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
    # r1233: the reader must know the window those numbers were grown in before deciding
    # what "8%/yr" means for him.
    for _sw_line in sample_window_block(p.get("sample_window") or {}):
        add(_sw_line)
    # r1235: was this book runnable in 2020, or does its return depend on funds
    # that were listed after the window opened?
    for _ul_line in universe_lock_block(p.get("universe_lock") or {}):
        add(_ul_line)
    # r1247: the universe is picked by one number (a liquidity cut). Say where that number
    # came from, and say that what sits on it is the book's capacity, not its return.
    for _eg_line in entry_gate_block(p.get("entry_gate") or {}):
        add(_eg_line)
    # r1251: the panel is a bar behind for a few hours every evening. Say what the book is
    # worth today, and say it only when the quote's own rows still reproduce it.
    for _lq_line in live_quote_block(p.get("live_quote") or {}):
        add(_lq_line)
    # r1238: the gate is on the way in only -- can the desk get out of what it holds?
    for _sf_line in sellability_block(p.get("sellability") or {}):
        add(_sf_line)
    # r1239: 8bp per side is an assumption with a cash floor at the bottom end.
    for _cf_line in capital_block(p.get("capital") or {}):
        add(_cf_line)
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
    _auth = p.get("authority") or {}
    if _auth.get("took_over"):
        add("**这一页是 %s 代笔的。** %s 已经 %.1f 小时没有自己的心跳 —— 它的页面是"
            "停了，不是旧了；代笔只写这一页，不碰它盘上的任何面。"
            % (_auth.get("writer"), _auth.get("owner"),
               float(_auth.get("owner_silent_h") or 0)))
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
    auth = takeover_authority(mid) or {"writer": mid, "owner": HOST, "took_over": False}
    page["authority"] = auth
    if auth.get("took_over"):
        print("etf_book_ceo_page: WRITING AS %s -- %s" % (mid, auth["why"]))
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

    def _p(s):
        # The page quotes money as "¥..." and a GBK console cannot encode U+00A5;
        # a leg that prints a yuan figure must not fail the suite for that reason.
        try:
            print(s)
        except UnicodeEncodeError:
            print(s.encode("ascii", "backslashreplace").decode("ascii"))

    def chk(name, cond, detail=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            _p("[%d/%d] PASS %s%s" % (ok, total, name, (" | " + detail) if detail else ""))
        else:
            _p("[%d/%d] FAIL %s%s" % (ok, total, name, (" | " + detail) if detail else ""))
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
    need = ["下单清单", "下次换仓", "该期待什么", "必须记住的四条", "这张单买的东西本身值多少",
            "为什么这张单只能下这么大"]
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
    # 22. single writer: only the host may write while it is alive; an unknown heartbeat is
    # not a dead owner, and a declared silence is a take-over that says who took the pen.
    _orig_sil = globals()["owner_silence_hours"]
    try:
        globals()["owner_silence_hours"] = lambda: 0.5
        _fresh = (writer_allowed("bm-a") and not writer_allowed("bm-c")
                  and not writer_allowed("bm-b") and not writer_allowed(None))
        globals()["owner_silence_hours"] = lambda: 9.0
        _auth = takeover_authority("bm-c") or {}
        _silent = (writer_allowed("bm-a") and writer_allowed("bm-c")
                   and not writer_allowed(None)
                   and _auth.get("writer") == "bm-c" and _auth.get("owner") == HOST
                   and _auth.get("took_over") is True and _auth.get("why"))
        globals()["owner_silence_hours"] = lambda: None
        _unk = not writer_allowed("bm-c") and not writer_allowed("bm-b")
    finally:
        globals()["owner_silence_hours"] = _orig_sil
    chk("L22 guard: live owner = only bm-a; declared silence = takeover; unknown = nobody",
        _fresh and _silent and _unk,
        "fresh=%s silent=%s unknown=%s host=%s" % (_fresh, _silent, _unk, HOST))

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
    # r1458: this leg pinned the pre-r1400 convention (a repaired column walked forward from
    # the panel's first bar, ending at 10.5 on a 1:5 print). r1400 re-anchors each column to
    # its own last traded print, because a level is only a scale and the sheet was quoting a
    # pre-split price. The property that matters did not change: the flip bar is a 0% day and
    # every return the column feeds is untouched -- so the leg now asserts that, plus the
    # anchor, instead of a level the producer deliberately abandoned (E289 stale-leg family).
    chk("L27b flip: the imported repair flattens a -90%% quote flip, keeps the returns it feeds, "
        "and anchors the level to the column's own traded print",
        _nflat == 1 and abs(float(_cleanA["A"].pct_change().iloc[2])) < 1e-12
        and abs(float(_cleanA["A"].iloc[3]) - 1.05) < 1e-9
        and abs(float(_cleanA["A"].pct_change().iloc[3]) - 0.05) < 1e-9,
        "n=%s thr=%s last=%.4f ret_after=%.4f" % (_nflat, _thr, float(_cleanA["A"].iloc[3]),
                                                 float(_cleanA["A"].pct_change().iloc[3])))
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
        and "[-0.10, +1.92]" not in _md_vw, "")   # the CI is unique to the paired block;
    # the bare mean "+0.83pp" now also appears in the gap-history section (r1465), so it can
    # no longer serve as the evidence that the paired numbers stayed out of the plain page
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
    _p_wl, _ = build(with_stress=False, window_label=_wl_ok)
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
    _p_wl2, _ = build(with_stress=False, window_label=_wl_mid)
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
    # L112-L115 (r1233): every number on the page is measured on the 2020-2026 boom. The page
    # must name the window, quote the out-of-window test from its own payload, and refuse a
    # payload whose prose disagrees with its own t statistics.
    _sw = sample_window_face()
    _sw_md = "\n".join(sample_window_block(_sw))
    _sw_uni = (_sw.get("universe") or {}).get("U_pre")
    _sw_t = max([abs(float(r.get("alpha_t") or 0.0)) for r in (_sw.get("rows") or [])] or [0.0])
    _sw_pw = _sw.get("page_window") or [None, None]
    chk("L112 sample window: the live face is read and the page names the universe and window",
        _sw.get("status") == "ok" and _sw_uni and ("%s 只" % _sw_uni) in _sw_md
        and _sw_pw[0] and ("%s 至 %s" % (_sw_pw[0], _sw_pw[1])) in _sw_md
        # the sentence must name the window THIS page lives in, never the out-of-window test
        and "**2015" not in _sw_md
        and "这些号码是从哪一段行情里长出来的" in _sw_md,
        "status=%s universe=%s page_window=%s" % (_sw.get("status"), _sw_uni, _sw_pw))
    chk("L113 sample window: the out-of-window verdict is derived from the published t, not prose",
        (_sw.get("survives") is (_sw_t >= 2.0))
        and (("过线了" in _sw_md) if _sw.get("survives") else ("分不开" in _sw_md)), "t=%.3f" % _sw_t)
    _sw_fake = dict(_sw)
    _sw_fake["rows"] = [dict((_sw.get("rows") or [{}])[0])]
    _sw_fake["rows"][0]["alpha_t"] = 3.4
    _sw_fake["survives"] = True
    _sw_fake_md = "\n".join(sample_window_block(_sw_fake))
    chk("L114 sample window: a t above 2 prints 'clears the line', never the closed sentence",
        "过线了" in _sw_fake_md and "分不开" not in _sw_fake_md, "")
    _sw_gone = "\n".join(sample_window_block({"status": "absent",
                                              "artifact": SPANNING_PRE2020_JSON}))
    _sw_drift = "\n".join(sample_window_block({"status": "drifted",
                                               "artifact": SPANNING_PRE2020_JSON}))
    chk("L115 sample window: an absent or drifted face prints no window table at all",
        "无法回答" in _sw_gone and "无法回答" in _sw_drift
        and "|" not in _sw_gone and "|" not in _sw_drift, "")
    # L116-L119 (r1235): the reader must know whether he could have bought this book in 2020.
    # The page quotes the locked-universe run, its verdict sentence is chosen from the payload's
    # own rows (through the face's single implementation), a payload whose control arms drift is
    # refused rather than printed, and the book-composition sentence is the payload's number.
    _ul = universe_lock_face()
    _ul_md = "\n".join(universe_lock_block(_ul))
    _ul_ph = _ul.get("phases") or []
    _ul_decl = (((_ul.get("control") or {}).get("arms") or {}).get("declared") or {}).get(
        "published")
    chk("L116 universe lock: the live face is read and the window's own grid is quoted",
        _ul.get("status") == "ok" and _ul_ph
        and ("%.2f%%" % (100.0 * (_ul_ph[0].get("unlocked") or 0.0)) in _ul_md)
        and ("%.2f%%" % (100.0 * (_ul_ph[0].get("locked") or 0.0)) in _ul_md)
        # phase 0 is the card's own decision grid: it has to equal the declared headline
        and _ul_decl is not None
        and abs((_ul_ph[0].get("unlocked") or 0.0) - _ul_decl) <= 1e-9,
        "status=%s phases=%d declared=%s" % (_ul.get("status"), len(_ul_ph), _ul_decl))
    _ul_fake_cost = dict(_ul, verdict="LOCK_COSTS_MONEY")
    _ul_fake_rob = dict(_ul, verdict="UNIVERSE_ROBUST")
    chk("L117 universe lock: the verdict sentence follows the payload's own verdict",
        ("要动手的钱" in "\n".join(universe_lock_block(_ul_fake_cost)))
        and ("跟票池新旧无关" in "\n".join(universe_lock_block(_ul_fake_rob)))
        and any(s in _ul_md for s in ("要动手的钱", "跟票池新旧无关", "平均为零")),
        "verdict=%s" % _ul.get("verdict"))
    _ul_gone = "\n".join(universe_lock_block({"status": "absent",
                                              "artifact": UNIVERSE_LOCK_JSON}))
    _ul_drift = "\n".join(universe_lock_block({"status": "drifted",
                                               "artifact": UNIVERSE_LOCK_JSON}))
    chk("L118 universe lock: an absent or drifted face prints no lock table at all",
        "答不了" in _ul_gone and "答不了" in _ul_drift
        and "|" not in _ul_gone and "|" not in _ul_drift, "")
    _ul_pk = _ul.get("picks") or {}
    _ul_nb = len(_ul_pk.get("book_in_force") or [])
    chk("L119 universe lock: the book-composition sentence is the payload's own number",
        bool(_ul_pk.get("pick_slots"))
        and ("%d/%d" % (_ul_pk.get("book_in_force_listed_after_lock") or 0, _ul_nb)) in _ul_md
        and ("%.1f%%" % (100.0 * (_ul_pk.get("share_listed_after_lock") or 0.0))) in _ul_md,
        "slots=%s listed_after=%s" % (_ul_pk.get("pick_slots"),
                                      _ul_pk.get("book_in_force_listed_after_lock")))
    # L120 (r1235): L116-L119 read universe_lock_block()'s own return value, so they
    # stayed 122/122 GREEN while the shipped assembly loop appended `_sw_line` -- the
    # sample-window block's last line -- once per lock line, dropping every lock line
    # from the page. A leg that reads the producer cannot testify for the consumer, so
    # this one renders the page and looks for the block the reader is promised.
    _ul_lines = [l for l in universe_lock_block(page.get("universe_lock") or {})
                 if l.strip()]
    _ul_off = [l for l in _ul_lines if l not in md]
    chk("L120 universe lock: the block itself reaches the rendered page",
        bool(_ul_lines) and not _ul_off,
        "status=%s, %d/%d line(s) on the page"
        % ((page.get("universe_lock") or {}).get("status"),
           len(_ul_lines) - len(_ul_off), len(_ul_lines)))
    # L121-L123 (r1238): the sellability section reads two payloads. The legs pin the three
    # ways it can lie: printing a tail worth when its census no longer reproduces the totals
    # the published share was counted on (drift), printing a verdict its rows no longer say,
    # and -- the r1235 lesson repeated -- a block whose lines never reach the page.
    _sf_absent = "\n".join(sellability_block({"status": "absent",
                                              "artifact": FORCED_HOLD_JSON}))
    chk("L121 sellability: an absent or drifted face is not printed as a number",
        ("答不了" in _sf_absent)
        and ("答不了" in "\n".join(sellability_block(
            {"status": "drifted", "detail": "census"}))),
        "absent=%r" % _sf_absent[:40])
    _sf = sellability_face()
    _sf_rows_ok = (_sf.get("status") == "ok"
                   and (_sf.get("tail_total") or 0) == (_sf.get("priced_total") or 0)
                   + (_sf.get("open_at_end_total") or 0))
    chk("L122 sellability: priced + unpriced = the tail (no censored row folded into a zero)",
        _sf_rows_ok,
        "status=%s tail=%s priced=%s open_at_end=%s"
        % (_sf.get("status"), _sf.get("tail_total"), _sf.get("priced_total"),
           _sf.get("open_at_end_total")))
    _sf_lines = [l for l in sellability_block(_sf) if l.strip()]
    _sf_off = [l for l in _sf_lines if l not in md]
    chk("L123 sellability: the block itself reaches the rendered page",
        bool(_sf_lines) and not _sf_off,
        "status=%s, %d/%d line(s) on the page"
        % (_sf.get("status"), len(_sf_lines) - len(_sf_off), len(_sf_lines)))
    # L124 (r1238): the two halves are additive only because they come off the same census;
    # the combined sentence is therefore re-derived here from the two payloads (never from the
    # prose) and has to be on the page. A page that prints the halves but not their sum sends
    # the reader back to the methodology card for a number the operator page already has.
    _w_pp = ((_load(EXIT_LIQ_JSON) or {}).get("summary") or {}).get("drag_pp_mean")
    _t_pp = ((_load(FORCED_HOLD_JSON) or {}).get("summary") or {}).get("pp_mean")
    _sum_pp = (round((_w_pp or 0.0) + (_t_pp or 0.0), 4)
               if _w_pp is not None and _t_pp is not None else None)
    _sum_txt = "%+.2f pp/年" % (_sum_pp or 0.0)
    chk("L124 sellability: the combined reading is the arithmetic of the two published halves "
        "and it is printed",
        _sum_pp is not None and _sum_pp == _sf.get("combined_pp") and _sum_txt in md,
        "wait=%s tail=%s sum=%s printed=%s"
        % (_w_pp, _t_pp, _sum_pp, _sum_txt in md))
    # L125-L128 (r1239): the capital section. Same three ways to lie as the sections above --
    # an absent face printed as a number, a token that no longer follows from its own rows,
    # and lines that never reach the page -- plus the one this section exists for: a threshold
    # quoted as a constant of the strategy when its own window block says it moves.
    _cf_absent = "\n".join(capital_block({"status": "absent", "artifact": MIN_CAPITAL_JSON}))
    chk("L125 capital: an absent or drifted face is not printed as a number",
        ("答不了" in _cf_absent)
        and ("答不了" in "\n".join(capital_block({"status": "drifted", "detail": "ladder"}))),
        "absent=%r" % _cf_absent[:40])
    _cf = capital_face()
    chk("L126 capital: the two neutral points are re-derived from the published traded-leg "
        "median, not read back from the file",
        _cf.get("status") == "ok" and (_cf.get("model_nav") or 0) > 0
        and (_cf.get("real_nav") or 0) > (_cf.get("model_nav") or 0),
        "status=%s model=%s real=%s dw=%s"
        % (_cf.get("status"), _cf.get("model_nav"), _cf.get("real_nav"), _cf.get("dw_median")))
    _cf_lines = [l for l in capital_block(_cf) if l.strip()]
    _cf_off = [l for l in _cf_lines if l not in md]
    chk("L127 capital: the block itself reaches the rendered page",
        bool(_cf_lines) and not _cf_off,
        "status=%s, %d/%d line(s) on the page"
        % (_cf.get("status"), len(_cf_lines) - len(_cf_off), len(_cf_lines)))
    _cf_wv = _cf.get("window_verdict")
    _cf_published_txt = "**这个门槛是稳的**"
    _cf_moves_txt = "**不过它不是一个常数。**"
    chk("L128 capital: a break-even that moves across samples is not printed as a constant",
        (_cf_wv == "BREAKEVEN_WINDOW_STABLE" and _cf_published_txt in md)
        or (str(_cf_wv).startswith("BREAKEVEN_WINDOW_MOVES") and _cf_moves_txt in md
            and _cf_published_txt not in md),
        "window_verdict=%s printed_as_constant=%s" % (_cf_wv, _cf_published_txt in md))
    # r1240: the floor is a closed form in the traded leg, so it moves with the BASKET.
    # The page must print the width table, and it must SAY when the basket it priced is
    # not the basket the card ships -- a number from a 5-name book printed beside a
    # 12-name book is exactly the defect this pair of legs exists to catch.
    _cf_widths = _cf.get("widths") or []
    _cf_mm = _cf.get("width_mismatch")
    _cf_warn = [l for l in _cf_lines if "\u26a0" in l]
    chk("L129 capital: the block prints one row per width and warns only on a real mismatch",
        bool(_cf_widths)
        and all(("%d \u540d" % w.get("n_hold")) in md for w in _cf_widths)
        and ((_cf_mm is True and bool(_cf_warn)) or (_cf_mm is not True and not _cf_warn)),
        "width_verdict=%s widths=%d mismatch=%s warn_lines=%d"
        % (_cf.get("width_verdict"), len(_cf_widths), _cf_mm, len(_cf_warn)))
    _fake = {"status": "ok", "model_nav": 100000.0, "real_nav": 300000.0,
             "base_bp": 8.0, "min_fee_cny": 5.0, "dw_median": 0.09, "prop_bp": 2.5,
             "small_capital": 1e4, "small_cagr": 0.02, "small_ref_cagr": 0.08,
             "small_fee_cny": 4320.0, "big_capital": 1e6, "big_delta_pp": 0.6,
             "window_verdict": "WINDOW_UNMEASURED", "window_spread_pct": None,
             "window_tol_pct": 10.0, "windows": [],
             "width_verdict": "BREAKEVEN_WIDTH_STABLE", "width_spread_pct": 1.0,
             "width_tol_pct": 10.0, "published_path_width": 5, "delivered_n_hold": 12,
             "width_mismatch": True,
             "widths": [{"n_hold": 5, "names_median": 5.0, "dw_median": 0.09,
                         "model_nav": 100000.0, "cagr_8bp": 0.07},
                        {"n_hold": 12, "names_median": 12.0, "dw_median": 0.03,
                         "model_nav": 300000.0, "cagr_8bp": 0.06}]}
    _fake_on = [l for l in capital_block(_fake) if "\u26a0" in l]
    _fake_off_cf = dict(_fake)
    _fake_off_cf["width_mismatch"] = False
    _fake_off_cf["delivered_n_hold"] = 5
    _fake_off = [l for l in capital_block(_fake_off_cf) if "\u26a0" in l]
    chk("L130 capital: the width warning is derived from the two faces, not typed",
        len(_fake_on) == 1 and not _fake_off
        and "300000" in _fake_on[0].replace(",", ""),
        "on=%d off=%d" % (len(_fake_on), len(_fake_off)))
    # L131-L132 (r1244): the card configures 12 names, the ladder is priced on 12, and the
    # ticket a reader can place today holds 5. Prose that says "another book" is not enough:
    # the section must name the ticket's width and its OWN break-even, and when the ticket
    # cannot be read it must say so instead of quietly quoting the card's basket at a reader
    # holding another one.
    _tk_fake = dict(_fake_off_cf)
    _tk_fake.update({"ticket_n_hold": 5, "ticket_bar": "2026-10-30",
                     "ticket_model_nav": 100000.0, "published_path_width": 12})
    _tk_lines = [l for l in capital_block(_tk_fake) if "可执行单" in l]
    _tk_on = _tk_lines and ("5" in _tk_lines[0]) and ("100000" in _tk_lines[0].replace(",", ""))
    _tk_same = dict(_tk_fake)
    _tk_same.update({"ticket_n_hold": 12})
    _tk_same_lines = [l for l in capital_block(_tk_same) if "可执行单" in l]
    chk("L131 capital: the ticket's own width and its own break-even are printed, derived "
        "from the width rows (never re-typed)",
        bool(_tk_on) and bool(_tk_same_lines)
        and ("12" in _tk_same_lines[0]) and ("一致" in _tk_same_lines[0])
        and not any("\u26a0" in l for l in _tk_lines),
        "different=%r same=%r" % (_tk_lines[:1], _tk_same_lines[:1]))
    _tk_none = dict(_tk_fake)
    _tk_none.update({"ticket_n_hold": None, "ticket_model_nav": None})
    _tk_none_lines = [l for l in capital_block(_tk_none) if "可执行单" in l]
    chk("L132 capital: an unreadable ticket is printed as unmeasured, not as the card's basket",
        bool(_tk_none_lines) and "读不出来" in _tk_none_lines[0]
        and "203007" not in _tk_none_lines[0],
        "lines=%r" % (_tk_none_lines[:1],))
    # ---- r1507: the second smallness constraint (whole lots) ------------------------------
    # The section above prices "is the fee model honest at this size"; one lot = 100 units
    # means a position below that is not expensive, it is unrepresentable. The page must
    # print that threshold with the number it is actually about, derive which constraint
    # bites first, and refuse a lot block that no longer recomputes from its own medians.
    _lot_cf = dict(_fake_off_cf)
    _lot_cf.update({"lot": {"median": 141916.0, "cellwise_median": 147168.0,
                            "p90": 291701.0, "units": 100, "price_median": 102.968,
                            "weight_median": 0.072556, "verdict": "LOT_IS_THE_LARGER_REQUIREMENT",
                            "compared_value": 100000.0,
                            "holdable_at": [{"capital": 1e4, "share": 0.296},
                                            {"capital": 4e5, "share": 0.992}],
                            "names_short_at_smallest": 6}})
    _lot_lines = capital_block(_lot_cf)
    _lot_txt = "\n".join(_lot_lines)
    _lot_bigger = "高于" in _lot_txt and "摆不下" in _lot_txt
    _lot_smaller_cf = dict(_lot_cf)
    _lot_smaller_cf["lot"] = dict(_lot_cf["lot"],
                                  verdict="FEE_FLOOR_IS_THE_LARGER_REQUIREMENT",
                                  median=50000.0, compared_value=100000.0)
    _lot_smaller_txt = "\n".join(capital_block(_lot_smaller_cf))
    chk("L133 lot: the page prints the whole-lot threshold, the price it comes from, and "
        "which constraint bites first -- both ways, from the verdict word",
        ("141916" in _lot_txt.replace(",", "")) and ("102.97" in _lot_txt)
        and ("一手 = 100 份" in _lot_txt) and _lot_bigger
        and ("低于" in _lot_smaller_txt) and ("先撞上的是「贵」" in _lot_smaller_txt),
        "bigger_printed=%s smaller_printed=%s"
        % (_lot_bigger, "先撞上的是「贵」" in _lot_smaller_txt))
    chk("L134 lot: the holdable table is printed row by row from the face, not summarised",
        ("| 10000 元 | 29.6%" in _lot_txt.replace(",", ""))
        and ("| 400000 元 | 99.2%" in _lot_txt.replace(",", "")),
        str([l for l in _lot_lines if l.startswith("| 1") or l.startswith("| 4")][:2]))
    # the reader must refuse a lot block whose median no longer follows from its own price
    # and weight -- otherwise the page prints a "you need this much money" nobody can
    # re-derive (r1507: the closed form is 100*price/weight, both published above it).
    _lot_bad = tempfile.mkdtemp()
    _lot_bad_json = os.path.join(_lot_bad, "mincap.json")
    with open(_lot_bad_json, "w", encoding="utf-8") as _fh:
        json.dump({"config": {"dw_median_all_legs": 0.0152, "base_bp_published": 8.0,
                              "base_bp_delivered": 10.0,
                              "schedules": [{"name": "wan2.5+5", "prop_bp": 2.5,
                                             "min_fee_cny": 5.0}],
                              "capital_grid": [1e4, 1e7],
                              "dw_mean_all_legs": 0.0152,
                              "delivered_rate_check": {"agree": True, "card_bp": 10.0,
                                                       "engine_bp": 10.0}},
                   "fee_neutral_vs_model_nav": 411184.21,
                   "fee_neutral_vs_real_nav": 1315789.47,
                   "fee_neutral_vs_delivered_nav": 328947.37,
                   "ladder": [{"schedule": "wan2.5+5", "capital": 1e4, "cagr": 0.05,
                               "ref_cagr": 0.06}],
                   "verdict": "FLOOR_BINDS_BELOW_411184_AND_MODEL_GENEROUS_ABOVE_1315789",
                   "window": {"verdict": "WINDOW_UNMEASURED", "rows": []},
                   "width": {"verdict": "WIDTH_UNMEASURED", "rows": []},
                   "lot": {"lot_nav_median": 999999.0, "price_median": 102.968,
                           "weight_median": 0.072556, "lot_units": 100,
                           "verdict": "LOT_IS_THE_LARGER_REQUIREMENT",
                           "compared_value": 328947.37}}, _fh)
    _lot_bad_face = capital_face(_lot_bad_json)
    chk("L135 lot: a lot threshold that disagrees with its own price and weight is refused",
        _lot_bad_face.get("status") == "drifted"
        and "whole-lot" in (_lot_bad_face.get("detail") or "")
        and _lot_bad_face.get("recomputed") is not None,
        "status=%s recomputed=%s" % (_lot_bad_face.get("status"),
                                     _lot_bad_face.get("recomputed")))
    # ---- r1246: the page prices the same cash on the ticket's three rates ----------------
    # The ticket learned to print three calibers (today's quote / its own trailing mean /
    # the ledger's window mean) in r1245; the page kept quoting one. These legs drive a
    # fixture through both readers and demand one answer -- including the case where a
    # second implementation would have printed 11,041 against the sheet's 11,039.
    _cm_dir = tempfile.mkdtemp()
    _cm_days = _sessions(_dt.date(2023, 1, 2), 300)
    _cm_pairs = [(d.isoformat(), 2.0) for d in _cm_days]
    _cm_pairs[-1] = (_cm_days[-1].isoformat(), 1.0)     # today 100bp below its own mean
    _panel(_cm_dir, "GC001", _cm_pairs)
    _cm_date = _cm_days[-1].isoformat()
    _cm_nomoney = {"evidence_cutoff": _cm_date, "cash_leg": {"mean_accrual_ann_pct": 2.10}}
    _cm_money = {"cash_amount_cny": 100000.0,
                 "spot": {"pct": 1.0, "date": _cm_date, "annual_cny": 1000.0, "quotes": 250},
                 "mean_tail": {"pct": 1.996, "annual_cny": 1996.0},
                 "window": {"pct": 2.1, "annual_cny": 2100.0},
                 "spread_vs_tail_cny": -996, "spread_vs_window_cny": -1100,
                 "fall_bp": 25.0, "verdict": "RATES_FELL"}
    _cm_tk_money = {"evidence_cutoff": _cm_date, "cash_leg": {"money": _cm_money}}
    _cmf_v = cash_money_face(100000.0, _cm_tk_money, panel_dir=_cm_dir)
    _cmf_r = cash_money_face(100000.0, _cm_nomoney, panel_dir=_cm_dir)
    _cmb_r = _cmf_r.get("block") or {}
    chk("L133 cash money: the ticket's own block is consumed verbatim, not re-rounded",
        _cmf_v.get("status") == "ok"
        and (_cmf_v.get("block") or {}).get("window", {}).get("annual_cny") == 2100.0
        and (_cmf_v.get("block") or {}).get("spot", {}).get("annual_cny") == 1000.0
        and "逐字" in (_cmf_v.get("source") or ""),
        "status=%s source=%s window=%s"
        % (_cmf_v.get("status"), _cmf_v.get("source"),
           ((_cmf_v.get("block") or {}).get("window") or {}).get("annual_cny")))
    chk("L134 cash money: with no ticket block it re-prices spot and its own mean, no window",
        _cmf_r.get("status") == "ok" and _cmb_r.get("verdict") == "RATES_FELL"
        and abs(((_cmb_r.get("spot") or {}).get("annual_cny") or 0) - 1000.0) < 1.0
        and abs(((_cmb_r.get("mean_tail") or {}).get("annual_cny") or 0) - 1996.0) < 2.0
        and (_cmb_r.get("window") is None or _cmb_r["window"].get("pct") is None)
        and "重算" in (_cmf_r.get("source") or ""),
        "status=%s verdict=%s spot=%s tail=%s window=%r"
        % (_cmf_r.get("status"), _cmb_r.get("verdict"),
           ((_cmb_r.get("spot") or {}).get("annual_cny")),
           ((_cmb_r.get("mean_tail") or {}).get("annual_cny")),
           _cmb_r.get("window")))
    _cmf_empty = cash_money_face(100000.0, _cm_nomoney, panel_dir=tempfile.mkdtemp())
    chk("L135 cash money: a missing repo panel is unmeasured, never 0",
        _cmf_empty.get("status") != "ok" and _cmf_empty.get("block") is None
        and bool(_cmf_empty.get("note")),
        "status=%s note=%s" % (_cmf_empty.get("status"), _cmf_empty.get("note")))
    _cmf_mis = cash_money_face(50000.0, _cm_tk_money, panel_dir=_cm_dir)
    chk("L136 cash money: a different pile of money does not borrow the ticket's window row",
        (_cmf_mis.get("block") or {}).get("window") is None
        or ((_cmf_mis.get("block") or {}).get("window") or {}).get("pct") is None
        and "不是同一笔钱" in (_cmf_mis.get("note") or ""),
        "note=%s window=%r" % (_cmf_mis.get("note"),
                               ((_cmf_mis.get("block") or {}).get("window"))))
    _cm_lines = "\n".join(cash_money_block(_cmf_v))
    _cm_dir2 = tempfile.mkdtemp()
    _panel(_cm_dir2, "GC001", [(d.isoformat(), 2.0) for d in _cm_days])
    _cm_flat_txt = "\n".join(cash_money_block(
        cash_money_face(100000.0, _cm_nomoney, panel_dir=_cm_dir2)))
    chk("L137 cash money: the block prints all three rows and calls a fall a fall",
        ("今天的报价" in _cm_lines and "自己近" in _cm_lines and "全窗均值" in _cm_lines
         and "利率掉下来" in _cm_lines and "996" in _cm_lines)
        and ("利率掉下来" not in _cm_flat_txt),
        "rows=[spot=%s tail=%s window=%s] fall_says_fall=%s steady_says_fall=%s"
        % ("今天的报价" in _cm_lines, "自己近" in _cm_lines, "全窗均值" in _cm_lines,
           "利率掉下来" in _cm_lines, "利率掉下来" in _cm_flat_txt))
    # L138-L140 (r1247): the entry gate -- the one number that picks the whole universe.
    _eg_dir = tempfile.mkdtemp()
    _eg_gates = [5e6, 10e6, 20e6, 50e6, 100e6, 200e6]
    _eg_medians = [460, 370, 262, 150, 94, 56]
    _eg_cagrs = [8.50, 8.50, 8.40, 7.90, 8.50, 5.50]
    _eg_rows = [{"min_amt_cny": g, "min_amt_m": round(g / 1e6, 1), "cagr": c / 100.0,
                 "sharpe": 0.9, "maxdd": -0.16, "median": m,
                 "turnover_per_decision": 0.95}
                for g, c, m in zip(_eg_gates, _eg_cagrs, _eg_medians)]
    _eg_doc = {"evidence_cutoff": "2026-10-30", "panel_last_bar": "2026-10-30",
               "rule": {"shipped_cny": 20e6, "tol_pp": 1.0},
               "config": {"universe_delta_names": 0, "universe_measured": 1504,
                          "universe_published": 1504},
               "control": {"delta_pp": 0.0, "tol_pp": 0.25},
               "rows": _eg_rows,
               "verdict": {"verdict": "GATE_SITS_ON_PLATEAU", "sentence": "fixture",
                           "best_delta_pp": 0.1,
                           "near_deltas_pp": [0.1, 0.0, -0.5],
                           "deltas_pp": {"5000000": 0.1, "10000000": 0.1, "20000000": 0.0,
                                         "50000000": -0.5, "100000000": 0.1,
                                         "200000000": -2.9}}}
    _eg_path = os.path.join(_eg_dir, "gate.json")
    with open(_eg_path, "w", encoding="utf-8") as _fh:
        json.dump(_eg_doc, _fh, ensure_ascii=False)
    _eg_ok = entry_gate_face(_eg_path)
    _eg_bad = dict(_eg_doc)
    _eg_bad["verdict"] = dict(_eg_doc["verdict"], verdict="GATE_BINDS_LOW")
    _eg_bad_path = os.path.join(_eg_dir, "gate_lied.json")
    with open(_eg_bad_path, "w", encoding="utf-8") as _fh:
        json.dump(_eg_bad, _fh, ensure_ascii=False)
    _eg_lied = entry_gate_face(_eg_bad_path)
    chk("L138 entry gate: the verdict is re-derived from its own rows, and a payload that "
        "disagrees with them is refused",
        _eg_ok.get("status") == "ok" and _eg_ok.get("verdict") == "GATE_SITS_ON_PLATEAU"
        and _eg_lied.get("status") == "drifted"
        and "disagrees" in (_eg_lied.get("detail") or ""),
        "ok=%s/%s lied=%s" % (_eg_ok.get("status"), _eg_ok.get("verdict"),
                              _eg_lied.get("status")))
    _eg_nocontrol = dict(_eg_doc, control={"delta_pp": None, "tol_pp": 0.25})
    _eg_nc_path = os.path.join(_eg_dir, "gate_nocontrol.json")
    with open(_eg_nc_path, "w", encoding="utf-8") as _fh:
        json.dump(_eg_nocontrol, _fh, ensure_ascii=False)
    _eg_nc = entry_gate_face(_eg_nc_path)
    _eg_off = dict(_eg_doc, control={"delta_pp": 0.9, "tol_pp": 0.25})
    _eg_off_path = os.path.join(_eg_dir, "gate_offcontrol.json")
    with open(_eg_off_path, "w", encoding="utf-8") as _fh:
        json.dump(_eg_off, _fh, ensure_ascii=False)
    _eg_of = entry_gate_face(_eg_off_path)
    chk("L139 entry gate: a sweep without a reproducing control arm is not printed as a "
        "plateau (missing and off by more than tolerance both refuse)",
        _eg_nc.get("status") == "drifted" and _eg_of.get("status") == "drifted"
        and "misses the published cell" in (_eg_of.get("detail") or ""),
        "nocontrol=%s offcontrol=%s detail=%s"
        % (_eg_nc.get("status"), _eg_of.get("status"), _eg_of.get("detail")))
    _eg_lines = "\n".join(entry_gate_block(_eg_ok))
    _eg_absent = "\n".join(entry_gate_block({"status": "absent", "artifact": ENTRY_GATE_JSON}))
    chk("L140 entry gate: the block prints both axes -- the flat return and the width that "
        "is not flat -- and refuses to answer when the payload is missing",
        ("460" in _eg_lines and "56" in _eg_lines
         and "容量来源" in _eg_lines and "±0.50 pp" in _eg_lines
         and "答不了" in _eg_absent and "容量来源" not in _eg_absent),
        "width_sentence=%s return_sentence=%s absent_says_unmeasured=%s"
        % ("容量来源" in _eg_lines, "±0.50 pp" in _eg_lines, "答不了" in _eg_absent))
    # r1251: the evening quote face -- what the book is worth while the panel lags one bar.
    # The arithmetic here is downstream of etf_book_live_quote.recheck (never a second copy).
    _ql_dir = tempfile.mkdtemp()
    _ql_rows = [
        {"symbol": "510300", "weight": 0.5, "panel_bar": "2026-11-03", "panel_close": 4.0,
         "quote_date": "2026-11-04", "quote_prev_close": 4.0, "quote_last": 4.08,
         "joined": True, "ret": 0.02},
        {"symbol": "518880", "weight": 0.3, "panel_bar": "2026-11-03", "panel_close": 1.5,
         "quote_date": "2026-11-04", "quote_prev_close": 1.5, "quote_last": 1.485,
         "joined": True, "ret": -0.01},
    ]
    _ql_held = 0.5 * 0.02 + 0.3 * -0.01
    _ql_face = {"verdict": "QUOTE_AHEAD", "panel_bar": "2026-11-03", "quote_bar": "2026-11-04",
                "quote_time": "15:35:00", "lag_trading_days": 1, "n_held": 2, "n_joined": 2,
                "mismatch_share": 0.0, "book_weight": 0.8, "cash_weight": 0.2,
                "held_leg_return": round(_ql_held, 6),
                "book_change": round(0.8 * _ql_held, 6),
                "ticket_priced_bar": "2026-11-03", "rows": _ql_rows,
                "thresholds": {"prev_tol_abs": 0.0011, "mismatch_share_max": 0.2}}
    with open(os.path.join(_ql_dir, "QUOTE-fixture.json"), "w", encoding="utf-8") as _fh:
        json.dump(_ql_face, _fh, ensure_ascii=False)
    with open(os.path.join(_ql_dir, "latest.json"), "w", encoding="utf-8") as _fh:
        json.dump({"as_of": "2026-11-04", "file": "QUOTE-fixture.json",
                   "verdict": "QUOTE_AHEAD"}, _fh, ensure_ascii=False)
    _ql_ok = live_quote_face(_ql_dir)
    _ql_lied_dir = tempfile.mkdtemp()
    with open(os.path.join(_ql_lied_dir, "QUOTE-lied.json"), "w", encoding="utf-8") as _fh:
        json.dump(dict(_ql_face, held_leg_return=0.05), _fh, ensure_ascii=False)
    with open(os.path.join(_ql_lied_dir, "latest.json"), "w", encoding="utf-8") as _fh:
        json.dump({"file": "QUOTE-lied.json"}, _fh, ensure_ascii=False)
    _ql_lied = live_quote_face(_ql_lied_dir)
    chk("L141 live quote: today's move is re-derived from the payload's own rows through the "
        "single recheck, and a payload whose rows disagree with it is refused",
        _ql_ok.get("status") == "ok"
        and abs(float(_ql_ok.get("held_leg_return") or 0.0) - _ql_held) < 1e-9
        and _ql_lied.get("status") == "drifted"
        and "its rows give" in (_ql_lied.get("detail") or ""),
        "ok=%s held=%r lied=%s" % (_ql_ok.get("status"), _ql_ok.get("held_leg_return"),
                                   _ql_lied.get("status")))
    _behind_rows = [dict(r, quote_date="2026-11-01") for r in _ql_rows]
    _ql_behind_dir = tempfile.mkdtemp()
    with open(os.path.join(_ql_behind_dir, "QUOTE-behind.json"), "w", encoding="utf-8") as _fh:
        json.dump(dict(_ql_face, quote_bar="2026-11-01", rows=_behind_rows,
                       lag_trading_days=None), _fh, ensure_ascii=False)
    with open(os.path.join(_ql_behind_dir, "latest.json"), "w", encoding="utf-8") as _fh:
        json.dump({"file": "QUOTE-behind.json"}, _fh, ensure_ascii=False)
    _ql_behind = live_quote_face(_ql_behind_dir)
    _no_new_dir = tempfile.mkdtemp()
    with open(os.path.join(_no_new_dir, "QUOTE-same.json"), "w", encoding="utf-8") as _fh:
        json.dump(dict(_ql_face, verdict="NO_NEW_BAR", quote_bar="2026-11-03",
                       held_leg_return=None, book_change=None), _fh, ensure_ascii=False)
    with open(os.path.join(_no_new_dir, "latest.json"), "w", encoding="utf-8") as _fh:
        json.dump({"file": "QUOTE-same.json"}, _fh, ensure_ascii=False)
    _ql_same = live_quote_face(_no_new_dir)
    _behind_txt = "\n".join(live_quote_block(_ql_behind))
    _absent_txt = "\n".join(live_quote_block({"status": "absent"}))
    _same_txt = "\n".join(live_quote_block(_ql_same))
    _ok_txt = "\n".join(live_quote_block(_ql_ok))
    chk("L142 live quote block: a snapshot older than the panel, a missing payload, and a "
        "panel that already ate the day each say so instead of printing a move",
        _ql_behind.get("status") == "behind"
        and _ql_same.get("verdict") == "NO_NEW_BAR"
        and "答不了" in _behind_txt and "答不了" in _absent_txt
        and "没有新答案" in _same_txt
        and "持仓腿今天" not in _behind_txt and "持仓腿今天" not in _absent_txt
        and "持仓腿今天" not in _same_txt,
        "behind=%s same=%s" % (_ql_behind.get("status"), _ql_same.get("verdict")))
    chk("L143 live quote block: the reader sees both the held leg and what it is worth on the "
        "whole book, plus the cash leg declining to be re-priced",
        ("+0.70%" in _ok_txt and "+0.56%" in _ok_txt and "20.00%" in _ok_txt
         and "2/2" in _ok_txt),
        "txt=%s" % " | ".join(x for x in _ok_txt.splitlines() if "持仓腿" in x)[:120])
    # r1458: the permission reached the order sheet but not this page. The page is the only
    # face a human reads, so "how big am I allowed to be" has to be on it -- and it has to
    # stay honest when a receipt is missing or two receipts disagree.
    _pf = page.get("permission") or {}
    # r1471: the live sheet now sizes from the executed account, so "over the floor" is no
    # longer the expected state -- the invariant is "a trim exists iff the order is over,
    # and it lands under the floor", not "the page always prints lots to sell".
    _pf_over = (_pf.get("over_cny") or 0) > 0
    chk("L144 permission: the live page carries a floor, and any trim it prints lands under it",
        _pf.get("status") == "ok" and _pf.get("consistency", {}).get("agree") is True
        and _pf.get("k_allowed") is not None and _pf.get("k_order") is not None
        and (_pf.get("trim") is not None) == _pf_over
        and (_pf_over is False or
             ((_pf.get("trim") or {}).get("k_after") is not None
              and _pf["trim"]["k_after"] <= _pf["k_allowed"] + 1e-9)),
        "allowed=%s order=%s after=%s over=%s" % (_pf.get("k_allowed"), _pf.get("k_order"),
                                                  ((_pf.get("trim") or {}).get("k_after")),
                                                  _pf_over))
    _pf_txt = "\n".join(permission_block(_pf))
    chk("L145 permission block: the live face states its position against the floor and warns "
        "that the next decision bar re-sizes over it, printing lots only when it is over",
        ("超出额度" in _pf_txt and "卖出手数" in _pf_txt if _pf_over
         else "超出额度" not in _pf_txt and "卖出手数" not in _pf_txt)
        and "排程没有" in _pf_txt,
        "over=%s txt_has_trim=%s" % (_pf.get("over_cny"), "卖出手数" in _pf_txt))
    _pf_missing = permission_face(perm_path=os.path.join(tempfile.mkdtemp(), "absent.json"))
    _pf_missing_txt = "\n".join(permission_block(_pf_missing))
    chk("L146 permission block: a missing receipt reads 'cannot verify', never 'no cut needed'",
        _pf_missing.get("status") == "unreadable" and "没有经过额度检查" in _pf_missing_txt
        and "没有超过额度" not in _pf_missing_txt,
        "status=%s" % _pf_missing.get("status"))
    _pf_dir = tempfile.mkdtemp()
    _perm_fix = {"decision_date": "2026-11-11", "ticket_file": "T-fix.json",
                 "k_now": 0.46, "permitted_k": 0.40, "book_amount_cny": 460000.0,
                 "permitted_book_cny": 400000.0, "cut_cny": 60000.0, "cut_pp": 6.0,
                 "keep_allowed": False, "readings": {}}
    _gap_fix = {"permitted_k": 0.39, "trim": {"legs": [], "lots_sell_total": 0}}
    _led_fix = {"assessed": {"floor": 0.40, "verdict": "REAPPLY_REQUIRED"}, "rows": []}
    _p_fix, _g_fix, _l_fix = (os.path.join(_pf_dir, n) for n in ("p.json", "g.json", "l.json"))
    for _path, _obj in ((_p_fix, _perm_fix), (_g_fix, _gap_fix), (_l_fix, _led_fix)):
        with open(_path, "w", encoding="utf-8") as _fh:
            json.dump(_obj, _fh, ensure_ascii=False)
    _pf_conflict = permission_face(_p_fix, _g_fix, _l_fix)
    _pf_conflict_txt = "\n".join(permission_block(_pf_conflict))
    chk("L147 permission block: two receipts quoting different floors stop the page from "
        "claiming obedience (E289 two copies of one number)",
        _pf_conflict.get("consistency", {}).get("agree") is False
        and "两张收据对同一个额度报了不同的数" in _pf_conflict_txt
        and "没有超过额度" not in _pf_conflict_txt,
        "consistency=%s" % json.dumps(_pf_conflict.get("consistency"), ensure_ascii=False))
    _p_under = os.path.join(_pf_dir, "p_under.json")
    with open(_p_under, "w", encoding="utf-8") as _fh:
        json.dump(dict(_perm_fix, k_now=0.35, cut_cny=0.0, keep_allowed=True), _fh, ensure_ascii=False)
    _pf_under = permission_face(_p_under, os.path.join(_pf_dir, "absent_g.json"),
                                os.path.join(_pf_dir, "absent_l.json"))
    _pf_under_txt = "\n".join(permission_block(_pf_under))
    chk("L148 permission block: a sheet already under the floor says so and prints no sell table",
        "没有超过额度" in _pf_under_txt and "卖出手数" not in _pf_under_txt
        and "超出额度" not in _pf_under_txt,
        "over=%s" % _pf_under.get("over_cny"))

    # r1463: the premium section. Same three ways to lie as the size section above --
    # absent must not read as "nothing paid", a different session must not be pasted onto
    # today's prices, and the named top-premium rows must come off the face, not be written here.
    _pb_fix = {"status": "ok", "artifact": "results/etf_book_premium_leak.json",
               "session": "2026-11-06", "ticket_session": "2026-11-06", "session_match": True,
               "verdict": "ENTRY_PREMIUM_DOMINATES", "verdict_reason": "x",
               "criteria": {"top_pctile": 95.0, "min_history_obs": 2},
               "totals": {"book_amount_cny": 459796.3, "premium_paid_cny": 41696.54,
                          "premium_share_of_order_pct": 9.07, "premium_share_of_nav_pct": 4.17,
                          "n_unverifiable": 0, "book_cagr_pct": 11.46,
                          "years_of_backtest_return_paid": 0.73},
               "stress": {"if_premium_reverts_to_zero_cny": -41696.54,
                          "if_premium_reverts_to_zero_pct_of_nav": -4.17},
               "names": [{"symbol": "159501", "class": "crossborder", "price": 2.069,
                          "iopv": 1.6734, "premium_pct": 23.64,
                          "premium_paid_cny": 17564.64, "market_pctile": 99.9,
                          "market_rank": 2, "market_n": 1639, "status": "OK"}],
               "nav_ruler_history": {"159501": {"symbol": "159501", "n_obs": 1,
                                                "status": "NOT_ENOUGH_OBSERVATIONS"}}}
    _pb_txt = "\n".join(premium_block(_pb_fix, page_bar="2026-11-06"))
    chk("L149 premium block: the live face prints what the order pays above IOPV and names the top-premium row",
        "41,697" in _pb_txt and "159501 第 2" in _pb_txt and "9.07%" in _pb_txt,
        _pb_txt[:80])
    _pb_missing_txt = "\n".join(premium_block({"status": "unreadable",
                                               "artifact": "results/etf_book_premium_leak.json",
                                               "detail": "face absent"}))
    chk("L150 premium block: an absent face reads 'not checked', never 'nothing paid'",
        "没有经过溢价检查" in _pb_missing_txt and "合计" not in _pb_missing_txt)
    _pb_shift = premium_block(dict(_pb_fix, session="2026-11-05"), page_bar="2026-11-06")
    chk("L151 premium block: a face priced on another session says so instead of pasting it on today",
        "两个日子对不上" in "\n".join(_pb_shift))

    # r1503: the page prints TWO yuan totals when the floor has trimmed the sheet since the
    # premium face ran (459,796 published vs 392,727 on the sheet). Unlabelled, a reader
    # either subtracts them or applies "9.07%" to the wrong base.
    _pb_sheet = {"amount_cny": 392727.0,
                 "legs": [{"symbol": "159501", "amount_cny": 78501.0},
                          {"symbol": "888888", "amount_cny": 1000.0}]}
    _pb_own = premium_on_page_sheet(_pb_fix, _pb_sheet)
    chk("L152 premium on this page: recomputed at the face's rates, and both sheets are named",
        _pb_own and abs(_pb_own["paid_cny"] - round(78501.0 * 23.64 / 100.0, 2)) < 0.01
        and abs(_pb_own["share_of_page_pct"] - round(100.0 * _pb_own["paid_cny"] / 392727.0, 4)) < 1e-6
        and _pb_own["unverifiable"] == ["888888"],
        json.dumps(_pb_own, ensure_ascii=False)[:200])
    _pb_own_txt = "\n".join(premium_block(_pb_fix, page_bar="2026-11-09", page_sheet=_pb_sheet))
    chk("L153 premium on this page: the block prints the page's own money and refuses to add the two sheets",
        "按本页这张单重算" in _pb_own_txt and "459,796" in _pb_own_txt
        and "392,727" in _pb_own_txt and "不许相加" in _pb_own_txt
        and "占它那张单" in _pb_own_txt and "888888" in _pb_own_txt,
        "len=%d" % len(_pb_own_txt))
    _pb_same = premium_on_page_sheet(_pb_fix, {"amount_cny": 459796.3, "legs": _pb_sheet["legs"]})
    _pb_same_txt = "\n".join(premium_block(_pb_fix, page_bar="2026-11-06",
                                           page_sheet={"amount_cny": 459796.3,
                                                       "legs": _pb_sheet["legs"]}))
    chk("L154 premium on this page: one sheet, one sentence -- the block stays quiet when both are the same paper",
        _pb_same is None and "按本页这张单重算" not in _pb_same_txt
        and "清单上" in _pb_same_txt, "same=%r" % (_pb_same,))
    _pb_near = premium_on_page_sheet(_pb_fix, {"amount_cny": 459796.3 - 50.0,
                                               "legs": [{"symbol": "159501", "amount_cny": 1.0}]})
    chk("L155 premium on this page: a rounding-sized difference is the same paper, not a second one",
        _pb_near is None, "near=%r" % (_pb_near,))
    # r1504: the last round printed the date mismatch as a sentence above the table. A reader
    # who copies a row out of the table still holds an undated number, and the page's sheet
    # (2026-11-09 prices) and the face's rates (2026-11-06) sit in two different tables.
    _pb_hdr = "\n".join(premium_block(_pb_fix, page_bar="2026-11-09", page_sheet=_pb_sheet))
    chk("L156 premium block: each table's header carries its own date, not just a sentence above it",
        "参考价（2026-11-06）" in _pb_hdr and "同一日的 IOPV（2026-11-06）" in _pb_hdr
        and "买溢价 ¥" in _pb_hdr
        and "本页金额（2026-11-09 价）" in _pb_hdr and "溢价率（2026-11-06 读数）" in _pb_hdr
        and "本表每一列——价格、IOPV、溢价率、全市场排名——都是 **2026-11-06** 那一天的读数；"
            "本页这张单的价是 **2026-11-09** 的" in _pb_hdr,
        _pb_hdr[:200])
    _pb_hdr_same = "\n".join(premium_block(_pb_fix, page_bar="2026-11-06"))
    chk("L157 premium block: on the same session the header still dates itself and drops the mismatch line",
        "参考价（2026-11-06）" in _pb_hdr_same and "两个日子对不上" not in _pb_hdr_same
        and "本页这张单的价是" not in _pb_hdr_same, _pb_hdr_same[:160])
    _pb_unbal = [ln for ln in _pb_hdr.splitlines() if ln.count("**") % 2]
    chk("L158 premium block: no line breaks its own bold -- a sentence that bolds its amounts is not bolding twice",
        not _pb_unbal and "****" not in _pb_hdr, "unbalanced=%r" % (_pb_unbal[:1],))
    # r1465: the gap-history section. The ways it can lie are its own: an absent face would
    # otherwise read as "the gap repeats", a face anchored on another session cannot lend its
    # percentiles to today's sheet, and the repeatable money must come off the face.
    _sg_fix = {"status": "ok", "artifact": "results/etf_book_sibling_gap.json", "session": "2026-11-06",
               "today_gain_cny": 9761.9, "repeatable_gain_cny": 1540.1, "one_off_gain_cny": 8221.8,
               "criteria": {"min_days": 120},
               "pairs": [{"leg_symbol": "159501", "sibling_symbol": "159513",
                          "sibling_name": "纳斯达克100ETF大成", "gap_today_pp": 8.6708,
                          "verdict": "PERSISTENT_GAP", "flags": {"today_is_tail": True},
                          "advice": "x",
                          "stats": {"mean_pp": 0.832, "days": 793, "share_days_positive": 0.70,
                                    "today_percentile": 100.0}}]}
    _sg_txt = "\n".join(sibling_gap_block(_sg_fix, page_bar="2026-11-06"))
    chk("L152 sibling gap block: the saving is split into the part that repeats and the part that does not",
        "9,762" in _sg_txt and "1,540" in _sg_txt and "8,222" in _sg_txt and "793" in _sg_txt,
        _sg_txt[:80])
    _sg_missing = "\n".join(sibling_gap_block({"status": "unreadable",
                                               "artifact": "results/etf_book_sibling_gap.json",
                                               "detail": "face absent"}))
    chk("L153 sibling gap block: an absent face never reads as 'the gap repeats'",
        "说不出它会不会天天有" in _sg_missing and "长期收的（" not in _sg_missing
        and "| 这只票 |" not in _sg_missing)
    _sg_shift = "\n".join(sibling_gap_block(dict(_sg_fix, session="2026-11-05"), page_bar="2026-11-06"))
    chk("L154 sibling gap block: a face anchored on another session refuses to lend its percentiles",
        "两个日子对不上" in _sg_shift)
    _ps_fix = {"status": "ok", "artifact": "results/etf_book_positions.json", "asof": "2026-11-06",
               "verdict": "PRINTED_ROWS_UNDERSELL_THE_BOOK", "printed_rows": 3, "book_rows": 4,
               "unexplained_total_cny": 67289.1, "unexplained_unpriced_rows": 0,
               "ledger_action": "kept",
               "ledger_row": {"bar": "2026-11-06", "risk_book_cny": 392400.9, "cash_cny": 607599.1,
                              "holdings": [{"symbol": "159263", "lots": 687, "price": 1.143,
                                            "amount_cny": 78524.1}]},
               "next_order_base": {"bar": "2026-11-06", "risk_book_cny": 392400.9,
                                   "cash_cny": 607599.1, "holdings": 4},
               "base_divergence_total_cny": 381115.4,
               "replay": {"start_bar": "2026-10-09", "bars": 20, "legs_ret": -0.05999355,
                          "cash_interest_cny": 563.81, "identity_holds": True},
               "accrual": {"status": "NO_NEW_BAR", "from_bar": "2026-11-06", "rows": 0},
               "engine_book": {"tail": {"source": "x"},
                               "divergence": {"k_gap": 0.067852, "notional_gap_cny": 67852.0}}}
    _ps_txt = "\n".join(positions_block(_ps_fix, page_bar="2026-11-06"))
    chk("L158 positions block: the account itself (lots, cash) and the lots the sheet never sells reach the page",
        "392,401" in _ps_txt and "607,599" in _ps_txt and "687" in _ps_txt
        and "67,289" in _ps_txt and "381,115" in _ps_txt and "563.81" in _ps_txt,
        _ps_txt[:80])
    _ps_missing = "\n".join(positions_block({"status": "unreadable",
                                             "artifact": "results/etf_book_positions.json",
                                             "detail": "face absent"}))
    chk("L159 positions block: an absent account face is 'cannot say what is held', never an empty account",
        "说不出已经持有多少" in _ps_missing and "| 代码 |" not in _ps_missing)
    _ps_broken = "\n".join(positions_block(
        dict(_ps_fix, replay=dict(_ps_fix["replay"], identity_holds=False)), page_bar="2026-11-06"))
    chk("L160 positions block: an account whose halves do not add back to NAV is printed as a conflict",
        "恒等不成立" in _ps_broken)
    _ps_nobar = "\n".join(positions_block(_ps_fix, page_bar="2026-11-06"))
    chk("L161 positions block: a bar with no accrual is 'nothing booked yet', not a zero-interest day",
        "今天没有新 bar" in _ps_nobar and "入账 0 行" not in _ps_nobar)
    # r1473: the size-limit section. Its ways to lie: an absent face would read as "the limit
    # is a rule", a face anchored on another session cannot lend its split to today, and the
    # three money pieces must be the face's own numbers rather than a re-derivation here.
    _fp_fix = {"status": "ok", "artifact": "results/etf_book_floor_provenance.json",
               "verdict": "FLOOR_IS_A_BETA_RECIPROCAL", "beta_target": 0.2,
               "published_floor": 0.393073, "evidence_cutoff": "2026-11-06",
               "issuing_cell": {"cell": "window_x_universe", "beta": 0.50881115,
                                "k": 0.39307315, "bars": 306,
                                "window": "common (2025-07-09..2026-10-14)",
                                "universe": "graded (equity,commodity,convertible)"},
               "grid": {"full|all": {"cell": "baseline_published", "k": 0.46025345,
                                     "beta": 0.43454318, "bars": 1658},
                        "common|all": {"cell": "window", "k": 0.41266852,
                                       "beta": 0.48465048, "bars": 306},
                        "full|graded": {"cell": "universe", "k": 0.43219501,
                                        "beta": 0.46275407, "bars": 1658},
                        "common|graded": {"cell": "window_x_universe", "k": 0.39307315,
                                          "beta": 0.50881115, "bars": 306}},
               "effects": {"floor_full_all": 0.46025345, "floor_common_graded": 0.39307315,
                           "window_effect_pp": 3.91, "window_effect_cny": 39121.86,
                           "universe_effect_pp": 1.96, "universe_effect_cny": 19595.37,
                           "interaction_pp": 0.85, "total_gap_pp": 6.72,
                           "total_gap_cny": 67180.3, "window_share_of_gap": 0.582,
                           "universe_share_of_gap": 0.292},
               "not_measured": ["a rolling 306-bar beta path is not computed here"]}
    _vt_fix = {"status": "ok", "artifact": "results/etf_book_vol_target_gate.json",
               "verdict": "STILL_REFUSED",
               "reading": "no arm clears it; the wait in r1428 is not a scaling artifact",
               "arms": [{"arm": "unscaled", "vol_target": None, "word": "REFUSED",
                         "reason": "gate CONDITIONAL,REFUSE; ruler FAIL years_for_half",
                         "cagr_pct": 14.2, "sharpe": 0.945, "maxdd_pct": -18.07,
                         "years_for_half_state": "FAIL", "years_for_half_median": 2.0,
                         "years_for_half_line": 3},
                        {"arm": "vt04", "vol_target": 0.04, "word": "REFUSED",
                         "reason": "gate REFUSE; ruler FAIL years_for_half",
                         "cagr_pct": 9.1, "sharpe": 1.1, "maxdd_pct": -8.2,
                         "years_for_half_state": "FAIL", "years_for_half_median": 1.0,
                         "years_for_half_line": 3}],
               "shape": {"reason": "scaling does move this ruler"}}
    _fp_txt = "\n".join(floor_provenance_block(_fp_fix, vt=_vt_fix, page_bar="2026-11-06"))
    chk("L162 floor section: the size limit is printed as a beta reciprocal with the knob that issued it",
        "倒过来的尺子" in _fp_txt and "window_x_universe" in _fp_txt and "306" in _fp_txt
        and "39,122" in _fp_txt and "58%" in _fp_txt and "度" in _fp_txt,
        _fp_txt[:80])
    chk("L163 floor section: the vol-target sweep is printed arm by arm and never as a pass",
        "仍被拒" in _fp_txt and "不调档（原书）" in _fp_txt and "4% 波动目标" in _fp_txt
        and "STILL_REFUSED" not in _fp_txt and "| 过门 |" not in _fp_txt
        and "没有一档能过门" in _fp_txt)
    _fp_missing = "\n".join(floor_provenance_block(
        {"status": "unreadable", "artifact": "results/etf_book_floor_provenance.json",
         "detail": "face absent"},
        vt={"status": "unreadable", "artifact": "results/etf_book_vol_target_gate.json",
            "detail": "face absent"}))
    chk("L164 floor section: both absent faces read 'cannot say', never 'the limit is a rule'",
        "说不出它是怎么定的" in _fp_missing and "读不到不等于不能" in _fp_missing
        and "| 这一格 |" not in _fp_missing and "| 波动档 |" not in _fp_missing)
    _fp_shift = "\n".join(floor_provenance_block(
        dict(_fp_fix, evidence_cutoff="2026-11-05"), vt=_vt_fix, page_bar="2026-11-06"))
    chk("L165 floor section: a face anchored on another session refuses to lend its split to today",
        "两个日子对不上" in _fp_shift)
    # r1502: the premium-forward section. Same family of lies as the premium section above:
    # an absent face would read as "no drift", and the rows / verdict / money must come off
    # the producer (etf_book_order.premium_read), never be typed here.
    _pfw_fix = {"status": "ok", "artifact": "results/etf_premium/PREMIUM-FORWARD.json",
                "face_asof": "2026-11-09", "stale": False, "verdict": "MIXED",
                "horizon": 20, "sentence": "sign is not the same across the book",
                "caveat": "this is not a forecast and not a sell order",
                "rows": [{"symbol": "159501", "bucket": "TOP", "mean_pct": 0.4868, "n": 282,
                          "t": 1.6468, "amount_cny": 78501.0, "same_bucket_move_cny": 382.18},
                         {"symbol": "159577", "bucket": "TOP", "mean_pct": -0.954, "n": 124,
                          "t": -2.6, "amount_cny": 78504.0, "same_bucket_move_cny": -749.0}],
                "missing_legs": [], "cny_total": -366.82}
    _pfw_txt = "\n".join(premium_forward_block(_pfw_fix, page_bar="2026-11-09"))
    chk("L166 premium forward block: what the price did after such a reading reaches the page, priced on the ticket's own amounts",
        "159501" in _pfw_txt and "+0.49%" in _pfw_txt and "159577" in _pfw_txt
        and "-0.95%" in _pfw_txt and "+382" in _pfw_txt and "-749" in _pfw_txt
        and "-367" in _pfw_txt and "MIXED" in _pfw_txt and "not a forecast" in _pfw_txt,
        _pfw_txt[:80])
    _pfw_missing = "\n".join(premium_forward_block(
        {"status": "unreadable", "artifact": "results/etf_premium/PREMIUM-FORWARD.json",
         "detail": "face absent"}))
    chk("L167 premium forward block: an absent face is 'not measured yet', never 'no drift'",
        "还没被量过" in _pfw_missing and "| 代码 |" not in _pfw_missing
        and "没有漂移" not in _pfw_missing.replace("不是「没有漂移」", ""),
        _pfw_missing[:80])
    _pfw_shift = "\n".join(premium_forward_block(
        dict(_pfw_fix, face_asof="2026-11-06"), page_bar="2026-11-09"))
    chk("L168 premium forward block: a face anchored on another session refuses to lend its rows to today",
        "两个日子对不上" in _pfw_shift)
    _pfw_cut = "\n".join(premium_forward_block(dict(_pfw_fix, missing_legs=["513100"])))
    chk("L169 premium forward block: a leg with no reading is named as unmeasured, not as zero drift",
        "513100" in _pfw_cut and "没量过" in _pfw_cut)

    # r1505: the section dates itself ("rate day 11-06 / price day 11-09") but never said WHY
    # the rate is old or whether it catches up. The board is a realtime print, so a missed
    # session is gone -- the page has to name the day and the next moment a same-day read
    # exists, or the reader waits for a number that will never arrive.
    _gap_one = {"status": "ok", "boards_present": ["2026-11-06"], "n_boards": 1,
                "first_board": "2026-11-06", "last_board": "2026-11-06",
                "coverage_starts": "2026-11-06",
                "sessions_expected": ["2026-11-06", "2026-11-09"],
                "missing": ["2026-11-09"], "n_missing": 1, "recoverable": False,
                "why_unrecoverable": "the board is a realtime print taken after the close, so a "
                                     "rerun photographs the session it runs in, not the one it missed",
                "next_capture_session": "2026-11-10", "next_capture_after": "15:30"}
    _gap_txt = "\n".join(premium_block(_pb_fix, page_bar="2026-11-09", page_sheet=_pb_sheet,
                                       board_gap=_gap_one))
    chk("L170 premium block: a missed board session is named as unrecoverable and the next read is dated",
        "这块板缺了 1 个交易日：2026-11-09" in _gap_txt
        and "重跑也拍不回来" in _gap_txt and "一直停在 **2026-11-06**" in _gap_txt
        and "2026-11-10 15:30 之后" in _gap_txt, "len=%d" % len(_gap_txt))
    _gap_none = dict(_gap_one, sessions_expected=["2026-11-06"], missing=[], n_missing=0,
                     last_board="2026-11-06")
    _gap_none_txt = "\n".join(premium_block(_pb_fix, page_bar="2026-11-06",
                                            board_gap=_gap_none))
    chk("L171 premium block: a board with no holes says so and does not print a gap",
        "没有缺口" in _gap_none_txt and "缺了" not in _gap_none_txt
        and "2026-11-06" in _gap_none_txt, "len=%d" % len(_gap_none_txt))
    _gap_unk = {"status": "unreadable_calendar", "missing": None, "n_missing": None,
                "next_capture_session": "2026-11-10", "next_capture_after": None}
    _gap_unk_txt = "\n".join(premium_block(_pb_fix, page_bar="2026-11-09",
                                           board_gap=_gap_unk))
    chk("L172 premium block: an unreadable calendar reads as unknown, never as zero holes",
        "未知" in _gap_unk_txt and "不是零" in _gap_unk_txt
        and "没有缺口" not in _gap_unk_txt, "len=%d" % len(_gap_unk_txt))

    # r1506: the sheet above and the account below disagreed by a leg and the page printed
    # both without saying which came first. The executed face reconciles them from the stack
    # the ticket was netted through -- and when only lot counts exist it must not invent money.
    _tk_fix = {"as_of": "2026-11-09", "swap_stack": {
        "asof": "2026-11-09", "verdict": "NETTED_WITH_RESIDUE",
        "lot_residue_cny": 139.9, "risk_book_before_cny": 392727.2,
        "risk_book_after_cny": 392587.3,
        "actions": [{"side": "SELL", "symbol": "159501", "lots": 382, "price": 2.055,
                     "amount_cny": 78501.0, "why": "swap 159501 -> 159513"},
                    {"side": "SELL", "symbol": "513100", "lots": 367, "price": 2.142,
                     "amount_cny": 78611.4, "why": "swap 513100 -> 159513"},
                    {"side": "BUY", "symbol": "159513", "lots": 925, "price": 1.697,
                     "amount_cny": 156972.5, "why": "merged buy"}],
        "holdings_after": [{"symbol": "159263"}, {"symbol": "159513"},
                           {"symbol": "159577"}, {"symbol": "513690"}]}}
    _ex_fix = executed_face(_tk_fix)
    chk("L173 executed face: sides sum to their own money and the residue is carried",
        _ex_fix.get("status") == "ok" and _ex_fix.get("priced")
        and abs(_ex_fix["sold_cny"] - (78501.0 + 78611.4)) < 0.01
        and abs(_ex_fix["bought_cny"] - 156972.5) < 0.01
        and abs((_ex_fix.get("lot_residue_cny") or 0) - 139.9) < 0.01,
        "sold=%.2f bought=%.2f" % (_ex_fix.get("sold_cny") or 0, _ex_fix.get("bought_cny") or 0))
    _ex_txt = "\n".join(executed_block(
        _ex_fix, sheet_symbols=["159501", "513100", "513690", "159577", "159263"]))
    chk("L174 executed block: names the legs the sheet has and the account does not, and the net cash direction",
        "清单里有、账上没有：159501、513100" in _ex_txt
        and "账上有、清单里没有：159513" in _ex_txt
        and "净现金流入" in _ex_txt  # bought 156,972 < sold 157,112
        and "手数取整留下 ￥139.90" in _ex_txt, "len=%d" % len(_ex_txt))
    _tk_lots = {"as_of": "2026-11-09",
                "positions": {"ledger_row": {"actions": [
                    {"side": "SELL", "symbol": "159501", "lots": 382},
                    {"side": "BUY", "symbol": "159513", "lots": 925}]}}}
    _ex_lots = executed_face(_tk_lots)
    _ex_lots_txt = "\n".join(executed_block(_ex_lots, sheet_symbols=["159501"]))
    chk("L175 executed face: lots without prices read as lots, and the block refuses to print ￥0",
        _ex_lots.get("status") == "ok" and not _ex_lots.get("priced")
        and "手数不是金额" in _ex_lots_txt and "￥0" not in _ex_lots_txt
        and "| 参考价 |" not in _ex_lots_txt, "len=%d" % len(_ex_lots_txt))
    _ex_none_txt = "\n".join(executed_block(executed_face({"as_of": "2026-11-09"})))
    chk("L176 executed block: a ticket with no trade rows says so, never 'nothing was traded'",
        "没有留下成交行" in _ex_none_txt and "| 方向 |" not in _ex_none_txt
        and "没有成交" not in _ex_none_txt.replace("「没有成交」", ""),
        "len=%d" % len(_ex_none_txt))
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