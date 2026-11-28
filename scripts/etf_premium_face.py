#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""etf_premium_face -- what the book pays over NAV to get filled (execution face).

WHY THIS FILE EXISTS
--------------------
The live ETF book holds cross-border legs (513100, 513690, 159501, 159577) whose
price is not pinned to NAV the way a domestic ETF's is: QDII quotas, trading-hour
mismatch and a capped subscription channel let the same basket trade several
percent above or below its own IOPV.  Every one of those percent is paid by the
buyer on entry -- the research record says which basket to hold, and this face
says whether *today* is a day you can actually get into it without handing the
market a slice of the edge.

    for each leg the ticket wants to buy, how far is the price from its IOPV,
    and how much CNY does that premium/discount mean on this ticket's size?

WHAT IT IS NOT
--------------
It is a snapshot face, not a backtest: one print of the ETF spot board, read at
whatever moment the command runs.  IOPV itself is a real-time *estimate* of the
basket (it is not the fund's published NAV), the spot board is intraday until
the close, and no price here is used to change a holding.  The book's rule is
price-based; this face only prices the *entry friction* that rule cannot see.

MODES
-----
  fetch     pull the ETF spot board once, write the snapshot to
            data/etf_premium/snap/<session>.csv, and render the face.
  render    render the face from the newest local snapshot (no network).
  selftest  offline legs over synthetic boards (the gate's own contract).

Bands (frozen): |premium| <= 0.30% is "at par"; <= 1.00% is "watch"; above that
is "stretched" -- a stretched cross-border leg is the case this face exists for.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP_DIR = os.path.join(ROOT, "data", "etf_premium", "snap")
OUT_DIR = os.path.join(ROOT, "results", "etf_premium")
TICKET_DIR = os.path.join(ROOT, "results", "etf_book_order")


def ticket_path():
    """The newest ORDER ticket (the book's own sheet), never the -card twin.

    r1398: the path used to be pinned to one session. On a daily chain that is a
    silent staleness bug -- the face would keep pricing the entry into a book the
    ticket no longer describes, and nothing would say so.
    """
    try:
        names = os.listdir(TICKET_DIR)
    except OSError:
        return None
    cands = [n for n in names
             if n.startswith("TICKET-") and n.endswith(".json") and not n.endswith("-card.json")]
    if not cands:
        return None
    return os.path.join(TICKET_DIR, sorted(cands)[-1])


TICKET_PATH = ticket_path() or os.path.join(TICKET_DIR, "TICKET-2026-11-06.json")

# Frozen bands, percent of IOPV.
PAR_BP = 0.30
WATCH_BP = 1.00
# Cross-section liquidity floor (CNY of session turnover) for the dispersion read.
MIN_AMOUNT = 20_000_000.0
# Execution hurdle: above this many CNY of over-NAV on one ticket the face says so
# out loud. Below it the cost is inside the book's own 8bp/side assumption and a
# warning line would be noise on every quiet day.
OVER_HURDLE_CNY = 500.0

# ---------------------------------------------------------- daily-chain gate
# The face is a SESSION snapshot, so it belongs on the daily chain (S6), not on a
# hand-run. A chain leg that runs every cycle needs three things the hand-run did
# not: it must not photograph an INTRADAY board and call it the close, it must not
# re-pull a session it already captured, and it must not hammer the source after a
# failure. `gate()` is that contract, and it is injectable so the selftest can
# exercise every branch without touching the real calendar or the real snapshots.
GATE_PATH = os.path.join(OUT_DIR, "_fetch_gate.json")
CLOSE_CUTOFF = (15, 30)
RETRY_BACKOFF_MIN = 30
# r1883: the chain is armed AT the close, but it has to actually run before today's
# board exists. Counting 15:31 as a hole made `board_gap` report a hole every day for
# the minutes between the close and the capture -- and a reader holding the page would
# read "缺了 2 个交易日" with one of them being this afternoon, which is not a missed
# session, it is a session nobody has reached yet. Inside this window today is
# `pending`, not `missing`.
CAPTURE_GRACE_MIN = 30

REQUIRED = ["代码", "名称", "最新价", "IOPV实时估值", "成交额", "数据日期"]
# The board publishes a DISCOUNT rate, not a premium: 159981 at price 1.801 over
# IOPV 1.806 prints 基金折价率 = 0.28 -- the number is POSITIVE for a *discount*.
# Reading that column as a premium would invert every band this face prints, so
# it is only a cross-check: the premium is always recomputed from price/IOPV and
# a disagreement between the two is counted and disclosed.
DISCOUNT_COLS = ["基金折价率", "基金折溢价率"]
CROSS_CHECK_TOL_PP = 0.10


DATING_PATH = os.path.join(ROOT, "results", "etf_nav", "source_dating.json")


def load_dating(path=None) -> dict:
    """Per-instrument NAV dates proven by the instrument's own price path (r2213 face).

    r2215: everything below decides "is this leg's denominator from this session?" from
    `nav_session`, and that field is ONE stamp for the whole batch -- the day the snapshot
    was fetched.  r2213 proved those are two different questions: of 1,439 datable rows
    under a single `2026-11-27` label, 1,371 sat on that day's price path, 8 sat on
    yesterday's close and 59 sat beyond the day's move.  A face that reads the label
    cannot see those 8, and one of them decided a ticket.

    So the dating face is loaded here as EVIDENCE about the day, never as an authority
    over the number: it answers per instrument, it names the day by the move that
    instrument actually made, and where it cannot tell (|move| under its own threshold)
    it says so -- a third answer the label does not have.
    """
    p = path or DATING_PATH
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return {"available": False,
                "why": "no dating face at %s" % os.path.relpath(p, ROOT).replace("\\", "/")}
    by = {}
    for r in d.get("rows") or []:
        c = str(r.get("code") or "").zfill(6)
        if not c:
            continue
        by[c] = {
            "position": r.get("board_position"),
            "sina_position": r.get("sina_position"),
            "move_pct": r.get("move_pct"),
            "sina_nav": r.get("sina_nav"),
            "sina_nav_date": r.get("sina_nav_date"),
            "board_missing": bool(r.get("board_missing")),
        }
    return {"available": True,
            "board_session": d.get("board_session"),
            "min_move_pct": d.get("min_move_pct"),
            "generated": d.get("generated"),
            "by_code": by}


def _num(s):
    return pd.to_numeric(s, errors="coerce")


SOURCE_COL_NAMES = ("_source", "source")
# r1600: the two spellings are the same fact -- one is how the board arrives in memory,
# the other is how it is written to the session CSV. A reader that knows only one of them
# loses the provenance on save or invents it on reload.
READER_IOPV = "em_iopv"
READER_NAV = "sina_nav_not_iopv"


def _src_one(v) -> str:
    """One cell -> a reader name. A missing cell means 'the board we read by default'.

    Deliberately not pandas string ops: a missing value in a string column arrives as NaN
    in one version and as the string 'nan' in another, and both spellings of 'absent' have
    to end up as the default reader rather than as a third, unknown one.
    """
    if v is None:
        return READER_IOPV
    try:
        if v != v:  # NaN, of either flavour
            return READER_IOPV
    except (TypeError, ValueError):
        pass
    s = str(v).strip()
    if not s or s.lower() in ("nan", "none", "<na>"):
        return READER_IOPV
    return s


def _cell_str(v):
    """A cell -> its text, or None when no date was ever recorded there."""
    if v is None:
        return None
    try:
        if v != v:  # NaN of either flavour
            return None
    except (TypeError, ValueError):
        pass
    s = str(v).strip()
    if not s or s.lower() in ("nan", "none", "<na>", "nat"):
        return None
    return s


def _src_series(df: pd.DataFrame) -> pd.Series:
    for c in SOURCE_COL_NAMES:
        if c in df.columns:
            return pd.Series([_src_one(v) for v in df[c].tolist()],
                             index=df.index, dtype=object)
    return pd.Series([READER_IOPV] * len(df), index=df.index, dtype=object)


def normalize_spot(df: pd.DataFrame) -> pd.DataFrame:
    """Spot board -> one row per ETF with a numeric premium, NaN kept as NaN.

    A row with no IOPV has NO premium (that is a fact about the row, not a
    zero); the same for a row with no price.  Never fill either with 0.
    """
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError("shape drift: missing columns %s" % ", ".join(missing))
    out = pd.DataFrame({
        "code": df["代码"].astype(str).str.zfill(6),
        "name": df["名称"].astype(str),
        "price": _num(df["最新价"]),
        "iopv": _num(df["IOPV实时估值"]),
        "amount": _num(df["成交额"]),
        "session": df["数据日期"].astype(str),
        # r1599: which reader produced the "iopv" column. Eastmoney prints an intraday
        # IOPV; the sina fallback carries the fund's published unit NAV. Without this
        # column the snapshot would claim one provenance while holding the other.
        # r1600: read BOTH spellings -- the shipped CSV calls it `source`, the in-memory
        # board calls it `_source`; knowing only the private one relabelled every
        # re-render of a sina snapshot as eastmoney.
        "source": _src_series(df),
    })
    # r1604: the denominator's own session. A published unit NAV arrives one session
    # behind the close for most domestic funds (and T+n for cross-border), so a premium
    # built on it is a CROSS-DATE gap unless the two dates agree. Carried, never inferred:
    # an older snapshot has no such column and must read as "undated", not as "same day".
    out["nav_session"] = (df["净值日期"].astype(str) if "净值日期" in df.columns
                          else np.nan)
    both = out["price"].gt(0) & out["iopv"].gt(0)
    out["premium_pct"] = np.nan
    out.loc[both, "premium_pct"] = (out.loc[both, "price"] / out.loc[both, "iopv"] - 1.0) * 100.0

    pub_col = next((c for c in DISCOUNT_COLS if c in df.columns), None)
    if pub_col is not None:
        published = _num(df[pub_col])          # discount: + means below IOPV
        implied = -published                    # what it would mean as a premium
        gap = (out["premium_pct"] - implied).abs()
        out["cross_check_pp"] = gap.round(4)
        out["cross_check_bad"] = gap.gt(CROSS_CHECK_TOL_PP) & out["premium_pct"].notna()
    else:
        out["cross_check_pp"] = np.nan
        out["cross_check_bad"] = False
    return out.reset_index(drop=True)


class NavBoard:
    """The second source: which funds published a unit NAV on `session` -- and the values.

    Membership answers one question ('can this session's NAV check the IOPV').  The VALUES
    answer a different one: a row whose own denominator belongs to an older session can be
    re-priced onto the session's published NAV instead of being printed as a cross-date gap
    (r2211: 159519 priced 11-27 against NAV(11-26) and labelled `iopv+same-day-nav` while
    the board had already published 11-27 = 1.7010).
    """

    def __init__(self, session: str, codes, nav=None):
        self.session = session
        self.codes = frozenset(codes)
        self.nav = dict(nav or {})

    def __contains__(self, code) -> bool:
        return str(code).zfill(6) in self.codes

    def __iter__(self):
        return iter(self.codes)

    def __len__(self) -> int:
        return len(self.codes)

    def value(self, code):
        """The session's published unit NAV for `code`, or None when the board has none."""
        v = self.nav.get(str(code).zfill(6))
        try:
            return float(v) if v and float(v) > 0 else None
        except (TypeError, ValueError):
            return None


def _nav_value(nav_ok, code):
    """A same-day published NAV from the second source, or None.

    A plain code set (the shape older callers pass, and the shape the selftest L16 uses)
    carries no values -- there is nothing to rebase onto and the caller must fall back to
    naming the leg instead of pricing it.
    """
    getter = getattr(nav_ok, "value", None)
    return getter(code) if callable(getter) else None


def normalize_nav_board(df: pd.DataFrame, session: str) -> NavBoard:
    """Fund NAV board -> the codes (and values) that published a unit NAV ON `session`.

    The board's columns are dated ('2026-11-06-单位净值'); a QDII fund prints
    '---' because its NAV arrives at T+n.  Membership is exactly 'the IOPV can be
    checked against a published NAV for this session'.
    """
    code_col = df.columns[0]
    date_cols = [c for c in df.columns if str(c).startswith(session) and "单位净值" in str(c)]
    if not date_cols:
        return NavBoard(session, set())
    col = date_cols[0]
    ok = set()
    nav = {}
    for _, r in df.iterrows():
        v = str(r.get(col, "")).strip()
        if v in ("", "---", "nan", "None", "--"):
            continue
        try:
            f = float(v)
        except ValueError:
            continue
        code = str(r[code_col]).strip().zfill(6)
        ok.add(code)
        if f > 0:
            nav[code] = f
    return NavBoard(session, ok, nav)


def band(premium_pct: float) -> str:
    if premium_pct is None or not np.isfinite(premium_pct):
        return "unknown"
    a = abs(premium_pct)
    if a <= PAR_BP:
        return "at-par"
    if a <= WATCH_BP:
        return "watch"
    return "stretched"


def leg_face(ticket: dict, spot: pd.DataFrame, nav_ok=None, session=None,
             dating=None) -> list[dict]:
    """One row per ordered leg.  A leg the board does not carry is MISSING:
    its premium is None, and the face prints it as unknown rather than free.

    nav_ok = the second source (a NavBoard, or a bare set of codes).  A QDII /
    cross-border fund publishes its NAV at T+n, so its IOPV is the only number
    on the board and that number is built from a basket whose home market has
    not printed yet -- such a leg is 'unverified', never priced.  Passing None
    disables the distinction (there is then no second source to appeal to).

    r2211: membership alone was not enough.  A leg can be ON the board's same-day
    list (so `unverified` was False) while the DENOMINATOR this row actually carries
    is an older session's NAV -- the row then printed a cross-date gap as a
    same-day premium AND a CNY figure ("trust: iopv+same-day-nav" next to
    "nav_session: 2026-11-26").  Two shapes, and the leg has to say which it is:
      * the board published this session's NAV -> re-price on it (`nav-rebased-same-day`,
        the board's own reading kept in `board_reading` so nothing is hidden);
      * the board published nothing -> `nav-cross-date`: keep the percentage as the
        board printed it, but it is not this session's premium and it carries no CNY.

    r2215: `nav_session` is a LABEL a whole batch shares, so "the label says this
    session" is not the same claim as "this row's denominator is this session".  The
    dating face (r2213) answers the second question per instrument from the move that
    instrument made; where it contradicts the label it wins, and where it cannot tell
    the leg says `label-only` with the size of the ambiguity printed.  A leg the board
    does not carry at all also carries whatever a second source dated, so "no row here"
    stops looking like "nothing known".
    """
    if session is None and "session" in spot.columns:
        seen = sorted(set(spot["session"].dropna()))
        session = seen[-1] if seen else None
    by_code = spot.set_index("code")
    ev_by = (dating or {}).get("by_code") or {}
    # r2215: an evidence face that describes a DIFFERENT session cannot overrule this
    # one's label -- that would be yesterday's proof deciding today's date.
    ev_bs = (dating or {}).get("board_session")
    ev_avail = bool((dating or {}).get("available")) and (
        ev_bs in (None, "") or session in (None, "") or str(ev_bs) == str(session))
    amb_pp = (dating or {}).get("min_move_pct")
    rows = []
    for leg in ticket.get("order", []):
        code = str(leg.get("symbol", "")).zfill(6)
        amount = float(leg.get("amount") or 0.0)
        ev = ev_by.get(code)
        proven = (ev or {}).get("position")
        if code in by_code.index:
            r = by_code.loc[code]
            if isinstance(r, pd.DataFrame):
                r = r.iloc[0]
            prem = float(r["premium_pct"]) if np.isfinite(r["premium_pct"]) else None
            den_date = _cell_str(r.get("nav_session")) if "nav_session" in by_code.columns else None
            in_board = nav_ok is not None and code in nav_ok
            unverified = nav_ok is not None and not in_board
            # Is the DENOMINATOR this row is priced on from the face's own session?
            label_same = den_date is None or session is None or den_date == session
            # r2215: the label is a batch stamp; the price path is per instrument. Only a
            # contradiction is overruled -- a path that says "same day" while the label
            # says otherwise is recorded, not acted on, because the label is still the
            # only statement about WHICH day the value belongs to.
            same_day = label_same
            if ev_avail and proven == "PREV_SESSION" and label_same:
                same_day = False
            if not ev_avail:
                date_proof = ("no-evidence-face" if not (dating or {}).get("available")
                              else "evidence-face-other-session")
            elif proven == "SAME_SESSION":
                date_proof = "path-proven"
            elif proven == "PREV_SESSION":
                date_proof = ("path-overrules-label" if label_same else "path-proven-prev")
            else:
                date_proof = "label-only"
            price = float(r["price"]) if np.isfinite(r["price"]) else None
            rebased_nav = None if same_day else _nav_value(nav_ok, code)
            board_reading = None
            if same_day or unverified:
                prem_used, trust = prem, ("iopv+same-day-nav" if not unverified else "iopv-only")
                band_used = "unverified" if unverified else band(prem)
            elif rebased_nav is not None and price and price > 0:
                prem_used = (price / rebased_nav - 1.0) * 100.0
                trust = "nav-rebased-same-day"
                band_used = band(prem_used)
                board_reading = {"raw_premium_pct": None if prem is None else round(prem, 4),
                                 "raw_nav": round(float(r["iopv"]), 4) if np.isfinite(r["iopv"]) else None,
                                 "raw_nav_session": den_date}
            else:
                prem_used, trust, band_used = prem, "nav-cross-date", "unverified"
            priced = prem_used is not None and band_used != "unverified"
            rows.append({
                "symbol": code,
                "name": str(r["name"]),
                "class": leg.get("class", ""),
                "amount_cny": round(amount, 2),
                "premium_pct": None if prem_used is None else round(prem_used, 4),
                "band": band_used,
                "trust": trust,
                # r2215: HOW the date above is known -- a printed label, this instrument's
                # own price path, or a path that contradicted the label.
                "date_proof": date_proof,
                "date_move_pct": None if not ev else ev.get("move_pct"),
                "date_ambiguous_pp": (amb_pp if date_proof == "label-only" else None),
                "over_nav_cny": round(amount * prem_used / 100.0, 2) if priced else None,
                "iopv": None if not np.isfinite(r["iopv"]) else round(float(r["iopv"]), 4),
                "price": price,
                # r1600: which reader priced THIS leg -- a mixed file has to be resolvable
                # leg by leg, not only as a file-level average.
                "source": (_src_one(r.get("source")) if "source" in by_code.columns else READER_IOPV),
                # r1604: the date the DENOMINATOR belongs to. Not the same question as
                # `trust` (a published NAV can be yesterday's and still be published).
                # r2211: it is the date of the denominator this row is PRICED on, so a
                # rebased leg carries the session (the board's own date lives in
                # `board_reading`).
                "nav_session": (session if trust == "nav-rebased-same-day" else den_date),
                "denominator_nav": (round(rebased_nav, 4) if trust == "nav-rebased-same-day"
                                    else (round(float(r["iopv"]), 4) if np.isfinite(r["iopv"]) else None)),
                "board_reading": board_reading,
            })
        else:
            # r2215: the board has no row for this leg. That is a coverage hole in one
            # source, not proof that nothing is known -- if the dated source carries a
            # NAV for it, name it here rather than printing an empty cell.
            alt = None
            if ev and ev.get("sina_nav") is not None:
                alt = {"nav": ev.get("sina_nav"), "date": ev.get("sina_nav_date"),
                       "reader": "sina published NAV",
                       "why_unused": "另一源的口径与板面不同源（公布净值≠IOPV），本面不拿它定价"}
            rows.append({
                "symbol": code,
                "name": "",
                "class": leg.get("class", ""),
                "amount_cny": round(amount, 2),
                "premium_pct": None,
                "band": "missing",
                "trust": "no-quote",
                "date_proof": ("no-evidence-face" if not (dating or {}).get("available")
                               else "evidence-face-other-session" if not ev_avail
                               else "board-has-no-row"),
                "date_move_pct": None if not ev else ev.get("move_pct"),
                "date_ambiguous_pp": None,
                "over_nav_cny": None,
                "iopv": None,
                "price": None,
                "source": "no-quote",
                "nav_session": None,
                "denominator_nav": None,
                "board_reading": None,
                "alt_source": alt,
            })
    return rows


def dispersion(spot: pd.DataFrame, min_amount: float = MIN_AMOUNT, nav_ok=None,
               session=None) -> dict:
    """The cross-section, measured on ONE date -- and the other date counted, not pooled.

    r1604: 41 QDII rows in the 2026-11-12 snapshot carried a denominator dated 11-13 (the
    US session that ends on the Beijing morning), and their "premium" averaged +7.0% with
    a +37.6% tail. Pooling them with the domestic rows makes one distribution out of two
    quantities, so they are reported in their own line instead.
    """
    lag = None
    if session and "nav_session" in spot.columns:
        dated = spot["nav_session"].apply(_cell_str)
        cross = spot[dated.notna() & (dated != session) & spot["premium_pct"].notna()]
        if len(cross):
            lag = {
                "n": int(len(cross)),
                "n_liquid": int((cross["amount"] >= min_amount).sum()),
                "mean_pct": round(float(cross["premium_pct"].mean()), 4),
                "max_pct": round(float(cross["premium_pct"].max()), 4),
                "dates": sorted(set(dated.loc[cross.index].tolist())),
                "amount_cny": round(float(cross["amount"].sum()), 0),
            }
        keep = dated.isna() | (dated == session)
        spot = spot[keep]
    liq = spot[(spot["amount"] >= min_amount) & spot["premium_pct"].notna()]
    if nav_ok is not None:
        # explicit membership map: the second source is a NavBoard, not a plain set, and
        # pandas' isin() would take an arbitrary iterable for a scalar.
        liq = liq[liq["code"].map(lambda c: c in nav_ok)]
    if liq.empty:
        return {"n": 0, "note": "no liquid ETF carries a premium reading today"}
    p = liq["premium_pct"]
    top = liq.sort_values("premium_pct", ascending=False).head(5)
    bot = liq.sort_values("premium_pct").head(5)
    return {
        "n": int(len(liq)),
        "amount_floor_cny": min_amount,
        "median_pct": round(float(p.median()), 4),
        "p10_pct": round(float(p.quantile(0.10)), 4),
        "p90_pct": round(float(p.quantile(0.90)), 4),
        "share_at_par": round(float((p.abs() <= PAR_BP).mean()), 4),
        "share_stretched": round(float((p.abs() > WATCH_BP).mean()), 4),
        "top_premium": [{"symbol": r.code, "name": r["name"], "pct": round(float(r.premium_pct), 4)}
                        for _, r in top.iterrows()],
        "top_discount": [{"symbol": r.code, "name": r["name"], "pct": round(float(r.premium_pct), 4)}
                         for _, r in bot.iterrows()],
        "cross_date": lag,
    }


def _reader_short(s: str) -> str:
    """The two readers in a reader's words: an IOPV estimate vs the published unit NAV."""
    if s == READER_NAV:
        return "单位净值"
    if s == READER_IOPV:
        return "IOPV"
    return "—"


def render_md(face: dict) -> str:
    L = []
    L.append("# 执行溢价面 · %s" % face["session"])
    L.append("")
    src = face["source"]
    readers = src.get("readers") or []
    rows_by = src.get("reader_rows") or {}
    census = "、".join("%s %d 行" % (k, rows_by[k]) for k in sorted(rows_by))
    if readers and all(r == READER_NAV for r in readers):
        L.append("快照口径：**本场主源（IOPV 牌价板）没有应答，本面由 sina 兜底采集**——分子＝当日成交价"
                 "（收盘口径），**分母＝当日公布单位净值，不是盘中 IOPV**（%s）。读数源：%s。"
                 "与历史 IOPV 口径的溢价只可粗比，不可当同一序列。" % (src.get("fetched_at", ""), census))
    elif src.get("mixed"):
        L.append("快照口径：**本文件混用了两种读数（%s）**——分子同源、分母不同源，"
                 "溢价只在同一读数源内可比，跨源不可比（%s）。" % (census, src.get("fetched_at", "")))
    else:
        L.append("快照口径：ETF 现货板一次读取（%s），IOPV=实时估值不是公布净值；"
                 "读数随盘中变动，收盘后才等于当日最终值。" % src.get("fetched_at", ""))
    L.append("")
    legs = face["legs"]
    if legs:
        L.append("## 本单入场摩擦（书要买的每一腿）")
        L.append("")
        L.append("| 代码 | 名称 | 类别 | 计划金额 | 溢价% | 档位 | 相对净值多付(CNY) | 分母读数源 |")
        L.append("|---|---|---|---|---|---|---|---|")
        for r in legs:
            prem = "—" if r["premium_pct"] is None else "%+.3f" % r["premium_pct"]
            over = "—" if r["over_nav_cny"] is None else format(r["over_nav_cny"], "+,.0f")
            # r1604: the reader cell carries the denominator's date, so a leg priced off
            # an older NAV says which day it is priced off -- the percentage cannot.
            # r2211: a re-priced leg says so in the same cell, with both NAVs.
            reader_cell = _reader_short(r.get("source") or "")
            if r.get("trust") == "nav-rebased-same-day":
                br = r.get("board_reading") or {}
                reader_cell += " %s（换基：板面 %s %s → 同日 %s）" % (
                    r.get("nav_session"), br.get("raw_nav_session"),
                    br.get("raw_nav"), r.get("denominator_nav"))
            elif r.get("nav_session"):
                reader_cell += " " + r["nav_session"]
            # r2215: a printed date is a label; say whether anything proved it. A re-priced
            # leg already says "换基 → 同日" above, which IS the proof, so it is not relabelled.
            _dp = r.get("date_proof")
            if r.get("trust") == "nav-rebased-same-day":
                pass
            elif _dp == "label-only":
                reader_cell += "·日期未证（价动 %s%%，两日同量级）" % (
                    "—" if r.get("date_move_pct") is None else "%.2f" % r["date_move_pct"])
            elif _dp == "path-overrules-label":
                reader_cell += "·价格路径说这是昨日净值"
            elif _dp == "path-proven-prev":
                reader_cell += "·路径证明在昨日"
            elif _dp == "path-proven":
                reader_cell += "·路径证明在当日"
            alt = r.get("alt_source")
            if alt:
                reader_cell += "（板面无行；%s 有 %s %s，未采用）" % (
                    alt.get("reader"), alt.get("date"), alt.get("nav"))
            L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
                r["symbol"], r["name"] or "(板面未列)", r["class"],
                format(r["amount_cny"], ",.0f"),
                prem, r["band"], over, reader_cell))
        L.append("")
        tot = sum(r["over_nav_cny"] for r in legs if r["over_nav_cny"] is not None)
        known = sum(r["amount_cny"] for r in legs if r["over_nav_cny"] is not None)
        unk = [r["symbol"] for r in legs if r["over_nav_cny"] is None]
        L.append("**合计：在已知 %s 的计划金额上，相对净值 %s 元**（正数=买入即在溢价上多付）。"
                 % (format(known, ",.0f"), format(tot, "+,.0f")))
        if unk:
            L.append("")
            L.append("未定价腿：%s（板面没有它的读数，或它没有当日公布净值可对——按「不知道」记，不按 0 记）。"
                     % "、".join(unk))
        cd = [r["symbol"] for r in legs if r.get("trust") == "nav-cross-date"]
        if cd:
            L.append("")
            L.append("分母不在本场：%s（板面分母属于另一场的净值，而本场没有已公布净值可换基——"
                     "它们的百分比是跨日缺口，不是本场溢价，也不进上面的 CNY 合计）。"
                     % "、".join(cd))
        de = face.get("date_evidence") or {}
        if de:
            L.append("")
            if not de.get("available"):
                L.append("分母日期证据：**没有可用的定日面**（%s）——上表的日期只能算标签，"
                         "不能算证明。" % (de.get("why") or "缺件"))
            else:
                bp = de.get("by_proof") or {}
                L.append("分母日期证据：本单 %d 腿里，价格路径证明在当日 %d 腿、路径证明在昨日 %d 腿、"
                         "标签与路径不一致 %d 腿（已改按跨日处理）、按本场公布净值换基 %d 腿、"
                         "路径判不了日 %d 腿（价动低于 %s%% 判据，两个日子的读数都自洽——数照印，"
                         "日期只算标签）。（定日面 %s，板面 session %s）"
                         % (de.get("n_legs") or 0, bp.get("path-proven") or 0,
                            bp.get("path-proven-prev") or 0, bp.get("path-overrules-label") or 0,
                            bp.get("rebased-onto-session") or 0,
                            bp.get("label-only") or 0, de.get("min_move_pct"),
                            de.get("generated") or "—", de.get("board_session") or "—"))
                if de.get("label_only"):
                    L.append("日期只算标签的腿：%s。" % "、".join(de["label_only"]))
        L.append("")
        oh = face.get("over_hurdle") or {}
        if oh:
            if oh.get("breached"):
                L.append("**执行闸：本单可核对腿合计多付 %s 元 > 阈值 %s 元"
                         "（占可核对计划金额的 %.4f%%）——买进即先把这笔交给溢价；"
                         "可等溢价回落、或换贴水腿。**"
                         % (format(oh["total_over_nav_cny"], ",.0f"),
                            format(oh["hurdle_cny"], ",.0f"),
                            oh.get("share_of_plan_pct") or 0.0))
            else:
                L.append("执行闸：可核对腿合计多付 %s 元，未超阈值 %s 元，不提示。"
                         % (format(oh.get("total_over_nav_cny") or 0.0, ",.0f"),
                            format(oh.get("hurdle_cny") or 0.0, ",.0f")))
            L.append("")
    disp = face["dispersion"]
    den = face.get("denominator") or {}
    if den.get("verdict") == "cross-date":
        L.append("分母净值日：**%d/%d 行的分母不是本场**（本单 %d 腿里 %d 腿在列）——"
                 "这不是同一场的溢价，读数＝价格对另一场净值的**跨日缺口**；"
                 "同日净值公布后本面会换分母重算。"
                 % (den["rows_dated"] - den["rows_same_session"], den["rows_dated"],
                    den.get("legs_dated") or 0, len(den.get("legs_lagging") or [])))
        L.append("")
    elif den.get("verdict") == "mixed":
        L.append("分母净值日：**%d/%d 行同场（本场净值已公布），%d 行的分母不是本场**"
                 "（跨时区品种，其净值日与国内收盘日不同）——两类不可混在一起读，"
                 "分布面只统计同场行，另一类单独列数。"
                 % (den["rows_same_session"], den["rows_dated"],
                    den["rows_dated"] - den["rows_same_session"]))
        L.append("")
    elif den.get("verdict") == "same-session":
        L.append("分母净值日：**本场净值已公布**（%d 行同日），这一列是同一场的溢价。"
                 % den["rows_same_session"])
        L.append("")
    elif den.get("verdict") == "undated":
        L.append("分母净值日：**这份快照没有记下分母属于哪一天**（旧版快照无该列）——"
                 "溢价是否同场不可核验，读者只能当口径未知。")
        L.append("")
    L.append("## 全市场溢价分布（只用当日有公布净值的 %d 只，成交额 ≥ %s）"
             % (disp.get("n", 0), format(MIN_AMOUNT, ",.0f")))
    L.append("")
    if disp.get("n"):
        L.append("- 中位 %+.3f%%，p10 %+.3f%%，p90 %+.3f%%" % (
            disp["median_pct"], disp["p10_pct"], disp["p90_pct"]))
        L.append("- 贴水/溢价在 ±%.2f%% 以内的占 %.1f%%，偏离超过 %.2f%% 的占 %.1f%%" % (
            PAR_BP, disp["share_at_par"] * 100, WATCH_BP, disp["share_stretched"] * 100))
        L.append("- 溢价最高：" + "、".join("%s %s %+.2f%%" % (t["symbol"], t["name"], t["pct"])
                                           for t in disp["top_premium"]))
        L.append("- 折价最深：" + "、".join("%s %s %+.2f%%" % (t["symbol"], t["name"], t["pct"])
                                           for t in disp["top_discount"]))
    else:
        L.append("- %s" % disp.get("note", ""))
    lag = disp.get("cross_date")
    if lag:
        L.append("")
        L.append("- **另有 %d 只（其中成交额 ≥ 20,000,000 的 %d 只，合计成交 %s 亿）分母净值日不在本场"
                 "（%s，晚于本场）——它们的溢价平均 %+.2f%%、最高 %+.2f%%，是把国内收盘价与另一场"
                 "海外交易的净值对出来的跨日缺口，已从上面的分布里剔除，不参与比较。**"
                 % (lag["n"], lag["n_liquid"], format(lag["amount_cny"] / 1e8, ",.0f"),
                    "、".join(lag["dates"]), lag["mean_pct"], lag["max_pct"]))
    L.append("")
    cc = face.get("cross_check") or {}
    if cc:
        L.append("## 口径核对：板面「折价率」列 vs 用 价格/IOPV 重算")
        L.append("")
        L.append("- 可比 %d 行，分歧 %d 行（阈值 %.2f 个百分点）——**板面那一列是折价率，符号与溢价相反**，"
                 "本面一律用价格/IOPV 重算，分歧只数不平均。" % (
                     cc.get("compared_rows", 0), cc.get("disagreeing_rows", 0), cc.get("tolerance_pp", 0)))
        L.append("")
    L.append("## 诚实边界")
    L.append("")
    for c in face["caveats"]:
        L.append("- %s" % c)
    L.append("")
    return "\n".join(L)


def _source_block(spot: pd.DataFrame, fetched_at: str, nav_ok=None) -> dict:
    """Which reader filled the denominator -- derived from the rows, never from the code.

    r1600: this face has two possible denominators (an intraday IOPV, or the fund's
    published unit NAV when the IOPV board refuses the host). A hard-coded `view` string
    is a claim about the code, not about the file that was read, so a sina snapshot
    printed "eastmoney via akshare fund_etf_spot_em" as its provenance -- the one place a
    reader could have caught the switch said the opposite of the truth.
    """
    series = _src_series(spot)
    counts = {str(k): int(v) for k, v in series.value_counts().items()}
    readers = sorted(counts)
    mixed = len(readers) > 1
    if readers and all(r == READER_NAV for r in readers):
        view = "sina quoted tape + the session's published unit NAV (fallback: the IOPV board did not answer)"
        denominator = "the session's published unit NAV, NOT an intraday IOPV"
    elif mixed:
        view = "mixed readers: %s" % ", ".join(readers)
        denominator = ("two denominators in one file -- premiums are comparable within a reader, "
                       "not across them")
    else:
        view = "ETF spot board (eastmoney via akshare fund_etf_spot_em)"
        denominator = "an intraday IOPV estimate"
    return {"view": view,
            "readers": readers,
            "reader_rows": counts,
            "mixed": mixed,
            "denominator": denominator,
            "fetched_at": fetched_at,
            "rows": int(len(spot)),
            "nav_board": "same-day unit NAV board (fund_etf_fund_daily_em) used as the second source" if nav_ok is not None else "not read -- every premium is IOPV-only"}


def denominator_block(spot: pd.DataFrame, session: str, legs: list) -> dict:
    """Is the DENOMINATOR from this session?  A dated question, not a trust question.

    A published unit NAV can be yesterday's and still be published: on 2026-11-12 every
    row of the evening snapshot carried NAV(11-11), so the whole table read a price
    against a NAV one session older and the word "premium" named a cross-date gap. The
    reader cannot see that from a percentage, so the face has to count it out loud.
    """
    if "nav_session" in spot.columns:
        dated = spot["nav_session"].apply(_cell_str)
    else:
        dated = pd.Series([None] * len(spot), index=spot.index)
    n_dated = int(dated.notna().sum())
    n_same = int((dated == session).sum())
    leg_dates = [r.get("nav_session") for r in legs if r.get("nav_session")]
    lagging = [r["symbol"] for r in legs
               if r.get("nav_session") and r["nav_session"] != session]
    if not n_dated:
        verdict = "undated"
    elif n_same == n_dated:
        verdict = "same-session"
    elif n_same == 0:
        verdict = "cross-date"
    else:
        # A table can hold both dates at once (2026-11-12: 1,483 domestic rows on the
        # session's own NAV, 41 QDII rows on the US session that ends that morning).
        # Calling that "cross-date" would mislabel the majority; calling it "same" would
        # hide the tail, so it gets its own word and its own counts.
        verdict = "mixed"
    return {
        "basis": "each row carries the date its own denominator belongs to; never inferred",
        "session": session,
        "rows_total": int(len(spot)),
        "rows_dated": n_dated,
        "rows_same_session": n_same,
        "legs_dated": len(leg_dates),
        "legs_lagging": lagging,
        "verdict": verdict,
    }


def build_face(spot: pd.DataFrame, ticket: dict, fetched_at: str, nav_ok=None,
               dating=None) -> dict:
    sessions = sorted(set(spot["session"].dropna()))
    session = sessions[-1] if sessions else "unknown"
    bad = int(spot["cross_check_bad"].sum()) if "cross_check_bad" in spot.columns else 0
    checked = int(spot["cross_check_pp"].notna().sum()) if "cross_check_pp" in spot.columns else 0
    # The book's ticket nests its legs under "ticket"; a bare order list is also
    # accepted so this face can be pointed at any ticket-shaped file.
    inner = ticket.get("ticket") if isinstance(ticket.get("ticket"), dict) else ticket
    legs = leg_face(inner, spot, nav_ok, session=session, dating=dating)
    # r2211: a leg whose own denominator belonged to another session is either re-priced
    # onto this session's published NAV (and the board's reading kept beside it) or named
    # as cross-date. Both are counted here so the face says what it did, and a reader can
    # see the difference between "no gap" and "a gap we could not re-price".
    rebased = [{"symbol": r["symbol"], "board_nav": (r.get("board_reading") or {}).get("raw_nav"),
                "board_nav_session": (r.get("board_reading") or {}).get("raw_nav_session"),
                "premium_board_pct": (r.get("board_reading") or {}).get("raw_premium_pct"),
                "same_day_nav": r.get("denominator_nav"), "premium_same_day_pct": r["premium_pct"]}
               for r in legs if r["trust"] == "nav-rebased-same-day"]
    cross = [r["symbol"] for r in legs if r["trust"] == "nav-cross-date"]
    # r2215: how each leg's date is known. A label is one answer for the whole batch; the
    # price path is one answer per instrument; a leg the board skips has no answer here.
    # A re-priced leg is its own case: its date is no longer a claim, it is the NAV this
    # face just replaced the denominator with.
    proof = {}
    for r in legs:
        key = ("rebased-onto-session" if r.get("trust") == "nav-rebased-same-day"
               else (r.get("date_proof") or "unknown"))
        proof.setdefault(key, []).append(r["symbol"])
    overruled = proof.get("path-overrules-label") or []
    label_only = proof.get("label-only") or []
    # The hurdle is summed over PRICED legs only: an unverified leg has no CNY figure
    # and is excluded rather than counted as zero, so a ticket made mostly of unverified
    # cross-border legs cannot look cheap.
    priced = [r for r in legs if r["over_nav_cny"] is not None]
    tot = sum(r["over_nav_cny"] for r in priced)
    known = sum(r["amount_cny"] for r in priced)
    over_hurdle = {
        "hurdle_cny": OVER_HURDLE_CNY,
        "total_over_nav_cny": round(tot, 2),
        "priced_amount_cny": round(known, 2),
        "share_of_plan_pct": round(100.0 * tot / known, 4) if known else None,
        "breached": bool(tot > OVER_HURDLE_CNY),
        "basis": "sum over priced legs only; unverified legs carry no CNY figure and are excluded, never counted as zero",
    }
    date_evidence = {
        "available": bool((dating or {}).get("available")),
        "face": "results/etf_nav/source_dating.json",
        "board_session": (dating or {}).get("board_session"),
        "generated": (dating or {}).get("generated"),
        "min_move_pct": (dating or {}).get("min_move_pct"),
        "n_legs": len(legs),
        "by_proof": {k: len(v) for k, v in sorted(proof.items())},
        "overrules_label": overruled,
        "label_only": label_only,
        "why": (None if (dating or {}).get("available") else
                (dating or {}).get("why") or "no dating face"),
        "basis": ("a batch stamp says which day the snapshot was fetched; the dating face "
                  "says which day each instrument's denominator belongs to, from the move that "
                  "instrument made. Where the two disagree the path wins and the leg is priced "
                  "as cross-date; where the path cannot tell (|move| under its threshold) the leg "
                  "keeps its number and is marked label-only with the ambiguity printed."),
    }
    return {
        "artifact": "etf_premium_face",
        "machine": "bm-c",
        "session": session,
        "source": _source_block(spot, fetched_at, nav_ok),
        "cross_check": {"basis": "premium recomputed from price/IOPV; the board's own 折价率 column is only compared",
                        "compared_rows": checked,
                        "disagreeing_rows": bad,
                        "tolerance_pp": CROSS_CHECK_TOL_PP},
        "ticket": {"path": os.path.relpath(TICKET_PATH, ROOT).replace("\\", "/"),
                   "bar": inner.get("book_decided_at") or ticket.get("book_decided_at") or ticket.get("evidence_cutoff")},
        "bands": {"par_pct": PAR_BP, "watch_pct": WATCH_BP},
        "legs": legs,
        "priced_legs": sum(1 for r in legs if r["over_nav_cny"] is not None),
        "unverified_legs": sum(1 for r in legs if r["band"] == "unverified"),
        "over_hurdle": over_hurdle,
        "denominator_rebasis": {
            "n": len(rebased),
            "legs": rebased,
            "cross_date_unpriced": cross,
            "basis": ("a leg whose own denominator date is not this session is re-priced on the "
                      "session's published unit NAV when the NAV board carries one; the board's "
                      "own reading stays in board_reading. With no same-day NAV the leg is "
                      "nav-cross-date: it keeps the percentage the board printed, carries no CNY, "
                      "and never claims to be this session's premium."),
        },
        "dispersion": dispersion(spot, nav_ok=nav_ok, session=session),
        "denominator": denominator_block(spot, session, legs),
        "date_evidence": date_evidence,
        "caveats": [
            "IOPV is a real-time estimate of the basket, not the fund's published NAV; a premium measured against it inherits that error.",
            "the spot board publishes 折价率 (discount), the opposite sign of a premium -- this face recomputes from price/IOPV and reports any disagreement instead of choosing a side.",
            "a cross-border leg publishes its NAV at T+n, so on the session itself its IOPV cannot be checked against anything. Those legs are marked unverified and carry NO CNY figure: an IOPV that has drifted from the basket looks exactly like a real premium from one snapshot.",
            "the board is read at one moment: before the close these numbers move, and cross-border legs are the ones that move most (their underlying trades in another timezone).",
            "a positive premium is a cost only to a buyer; it is income to a seller. This face says nothing about which side the book will be on tomorrow.",
            "no historical premium series is long enough to build a percentile gate from: this face runs once per session on the daily chain from 2026-11-06, so a 'is today's premium high for this leg' reading has to wait for the series to accumulate.",
        ] + ([
            "this session's denominator is the fund's published unit NAV, not an intraday IOPV: the premium is measured against the day's official net asset value, so it carries no intraday basket drift -- and it is only coarsely comparable with an IOPV-based premium from an earlier session.",
        ] if READER_NAV in (_source_block(spot, fetched_at, nav_ok).get("readers") or []) else []),
    }


def _snap_path(session: str) -> str:
    return os.path.join(SNAP_DIR, "%s.csv" % session)


def _read_gate():
    try:
        with open(GATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _write_gate(d):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = GATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, GATE_PATH)


def _trading_days():
    """The official calendar, or None. None means 'unreadable', never 'holiday'."""
    try:
        if ROOT not in sys.path:
            sys.path.insert(0, ROOT)
        from scripts import exchange_calendar_audit as CA
        return CA.load_calendar()
    except Exception:  # noqa: BLE001 -- see docstring: unreadable is not a verdict
        return None


_AUTO = object()   # sentinel: "read the calendar yourself"; an explicit None is 'unreadable'


def _prev_close_session(days, today):
    """The newest session strictly before `today`, or None.

    Before the 15:30 close the board has not rolled, so this is the only tape it can
    still be printing -- and the only session a pre-close run may honestly file.
    """
    older = [d for d in days if d < today]
    return max(older) if older else None


def _snap_present(session, today, snap_exists):
    """Is there a snapshot for `session`? `snap_exists` injects the answer.

    A bare bool keeps its old meaning (the value for `today`); a callable is asked
    about the exact session, which is what the pre-close backfill branch needs.
    """
    if callable(snap_exists):
        return bool(snap_exists(session))
    if snap_exists is not None:
        return bool(snap_exists) if session == today else False
    p = _snap_path(session)
    return os.path.exists(p) and os.path.getsize(p) > 0


def gate(now=None, force=False, days=_AUTO, snap_exists=None, gate_state=None):
    """May `fetch` hit the source right now? -> (run, session, reason).

    Every input is injectable so the selftest can drive the clock, the calendar and
    the on-disk state explicitly instead of depending on the day it runs. `days` is
    _AUTO by default (read the file), None passes through as 'calendar unreadable'.

    r1599: the second element is the SESSION TO CAPTURE, not "today". Before the close
    it is the previous close, because that is the tape the board is still carrying. The
    old shape refused every pre-close run outright, which made one missed capture a
    permanent hole (`board_gap`'s own docstring: these holes do not heal) while the
    price board for that very session was still sitting on the source untouched.
    """
    import datetime as _dt
    now = now or _dt.datetime.now()
    today = now.date().isoformat()
    if force:
        return True, today, "forced"
    if days is _AUTO:
        days = _trading_days()
    if days is None:
        return False, today, "official calendar unreadable -- refusing to guess a session"
    if today not in days:
        return False, today, "not a trading session (%s)" % today
    g = gate_state if gate_state is not None else _read_gate()

    def _backoff_left(session):
        ts = g.get("last_fail_ts")
        if g.get("last_fail_session") != session or not ts:
            return None
        try:
            age = (now - _dt.datetime.fromisoformat(ts)).total_seconds() / 60.0
        except (TypeError, ValueError):
            return None
        return age if age < RETRY_BACKOFF_MIN else None

    if (now.hour, now.minute) < CLOSE_CUTOFF:
        prev = _prev_close_session(days, today)
        if prev and not _snap_present(prev, today, snap_exists):
            left = _backoff_left(prev)
            if left is not None:
                return False, prev, "backoff %.0f/%.0f min after a failed attempt on %s" % (
                    left, RETRY_BACKOFF_MIN, prev)
            return True, prev, ("backfilling %s before the board rolls to %s -- the tape it "
                                "is printing is still that close" % (prev, today))
        return False, today, "before the 15:30 close -- an intraday board is not the session"
    if _snap_present(today, today, snap_exists):
        return False, today, "session %s already captured" % today
    left = _backoff_left(today)
    if left is not None:
        return False, today, "backoff %.0f/%.0f min after a failed attempt" % (left, RETRY_BACKOFF_MIN)
    return True, today, "armed"


def board_gap(now=None, days=_AUTO, snap_dir=None):
    """Which trading sessions the IOPV board holds, and which are gone for good.

    The board is a REALTIME print: `fetch` reads the session's spot board after the
    close and files it under that session. A session with no file is therefore not
    "late" -- re-running the lane tomorrow photographs tomorrow, not yesterday. That
    makes this the one face in the chain whose holes do not heal, which is why a
    consumer has to be told the hole instead of assuming a merely old file (contrast
    the daily bar panels: any later run backfills them).

    Coverage starts at the first board on disk -- sessions before it are NOT counted
    as holes, because nothing ever claimed to cover them. An unreadable calendar
    returns `missing=None` (unknown), never an empty list.
    """
    import datetime as _dt
    now = now or _dt.datetime.now()
    today = now.date().isoformat()
    if days is _AUTO:
        days = _trading_days()
    snap_dir = snap_dir or SNAP_DIR
    present = []
    try:
        names = os.listdir(snap_dir)
    except OSError:
        names = []
    for fn in names:
        if not fn.endswith(".csv"):
            continue
        stem = fn[:-4]
        try:
            _dt.date.fromisoformat(stem)
        except ValueError:
            continue
        try:
            if os.path.getsize(os.path.join(snap_dir, fn)) <= 0:
                continue
        except OSError:
            continue
        present.append(stem)
    present = sorted(set(present))
    before_close = (now.hour, now.minute) < CLOSE_CUTOFF
    out = {"status": "ok", "boards_present": present, "n_boards": len(present),
           "first_board": present[0] if present else None,
           "last_board": present[-1] if present else None,
           "coverage_starts": present[0] if present else None,
           "sessions_expected": [], "missing": [], "n_missing": 0, "pending": [],
           "capture_grace_min": CAPTURE_GRACE_MIN,
           "recoverable": False,
           "why_unrecoverable": "the board is a realtime print taken after the close, so a "
                                "rerun photographs the session it runs in, not the one it missed",
           "next_capture_session": None, "next_capture_after": None,
           "clock": now.isoformat(timespec="minutes")}
    if days is None:
        out["status"] = "unreadable_calendar"
        out["sessions_expected"] = None
        out["missing"] = None
        out["n_missing"] = None
        out["pending"] = None
        out["next_capture_session"] = today
        out["next_capture_after"] = "15:30" if before_close else None
        return out
    days = set(days)
    # r1883: a session that closed minutes ago is DUE, not lost. Until the grace
    # window expires it is named under `pending` and kept out of `missing`, so a
    # consumer reading at 15:33 does not print "the board is missing a day" about
    # an afternoon nobody has reached.
    closed_at = now.replace(hour=CLOSE_CUTOFF[0], minute=CLOSE_CUTOFF[1],
                            second=0, microsecond=0)
    in_grace = (not before_close) and (now - closed_at).total_seconds() < CAPTURE_GRACE_MIN * 60
    closable = [d for d in days if d < today or (d == today and not before_close and not in_grace)]
    last_closable = max(closable) if closable else None
    if present and last_closable:
        expected = sorted(d for d in days if present[0] <= d <= last_closable)
        have = set(present)
        out["sessions_expected"] = expected
        out["missing"] = [d for d in expected if d not in have]
        out["n_missing"] = len(out["missing"])
    if in_grace and today in days and today not in set(present):
        out["pending"] = [today]
    if today in days and before_close:
        out["next_capture_session"] = today
        out["next_capture_after"] = "15:30"
    elif today in days and today not in set(present):
        out["next_capture_session"] = today
    else:
        later = sorted(d for d in days if d > today)
        out["next_capture_session"] = later[0] if later else None
        out["next_capture_after"] = "15:30"
    return out


# ------------------------------------------------------------------ spot board (host failover)
# One clist API, several EM hosts. 2026-11-12: the delay host answered 1660 ETFs at
# 16:25 and then refused every request for the rest of the day (RemoteDisconnected /
# ReadTimeout), while push2.eastmoney.com served the same board with the same fields
# in 8s. A dead host cost the lane a whole session -- and this face photographs a
# session, it does not backfill one, so that hole never heals. So the board is pulled
# through an ordered list of sources: the first that answers wins, and the gate
# records WHICH one answered.
SPOT_CLIST_PATH = "/api/qt/clist/get"
SPOT_HOSTS = ("https://push2delay.eastmoney.com",
              "https://push2.eastmoney.com",
              "https://7.push2.eastmoney.com",
              "https://45.push2.eastmoney.com")
SPOT_PARAMS = {
    "pn": "1", "pz": "100", "po": "1", "np": "1",
    "ut": "bd1d9ddb04089700cf9c27f6f7426281", "fltt": "2", "invt": "2",
    "wbp2u": "|0|0|0|web", "fid": "f12",
    "fs": "b:MK0021,b:MK0022,b:MK0023,b:MK0024,b:MK0827",
    "fields": "f2,f6,f12,f14,f297,f441",
}
# Board field -> the column names normalize_spot() reads (REQUIRED).
SPOT_FIELDS = {"f12": "代码", "f14": "名称", "f2": "最新价",
               "f6": "成交额", "f297": "数据日期", "f441": "IOPV实时估值"}


def _http_get_json(url, params, timeout=(8, 20)):
    import requests
    r = requests.get(url, params=params, timeout=timeout,
                     headers={"User-Agent": "Mozilla/5.0",
                              "Referer": "https://quote.eastmoney.com/"})
    r.raise_for_status()
    return r.json()


def _board_from_host(host, get=None, page_size=500, max_pages=20,
                     throttle_s=2.5, retries=2):
    """One host's clist board -> a frame carrying exactly the REQUIRED columns.

    `get(url, params)` is injectable so the selftest can drive paging and shape
    without a socket. Pages are throttled and retried in place: this host drops
    connections after a handful of rapid requests (2026-11-12: one page answered in
    8s, the next five were RemoteDisconnected), so a page that fails is retried
    before the host is declared dead. A short page set that stops early is not an
    error here -- normalize_spot() is what decides whether the board is usable.
    """
    import time as _time
    get = get or _http_get_json
    rows = []
    for pn in range(1, max_pages + 1):
        params = dict(SPOT_PARAMS)
        params["pn"] = str(pn)
        params["pz"] = str(page_size)
        payload, last_err = None, None
        for attempt in range(retries + 1):
            try:
                payload = get(host + SPOT_CLIST_PATH, params)
                break
            except Exception as e:  # noqa: BLE001 -- retried, then named
                last_err = e
                if attempt < retries:
                    _time.sleep(throttle_s * 2 * (attempt + 1))
        if payload is None:
            raise last_err
        data = (payload or {}).get("data") or {}
        diff = data.get("diff") or []
        if isinstance(diff, dict):      # EM answers as {index: row} on some hosts
            diff = list(diff.values())
        if not diff:
            break
        rows.extend(diff)
        if len(rows) >= int(data.get("total") or 0):
            break
        _time.sleep(throttle_s)
    if not rows:
        raise ValueError("%s returned no rows" % host)
    df = pd.DataFrame(rows)
    missing = [k for k in SPOT_FIELDS if k not in df.columns]
    if missing:
        raise ValueError("%s shape drift: missing %s" % (host, ", ".join(missing)))
    return df[list(SPOT_FIELDS)].rename(columns=SPOT_FIELDS)


def _board_from_akshare():
    import akshare as ak
    return ak.fund_etf_spot_em()


def _spot_board(sources=None):
    """Pull the board from the first source that answers -> (frame, source name).

    Every attempt is named in the failure text: reporting only the last host would
    hide that the lane still had options (r1199: a red that measures half the causes
    is not actionable).
    """
    if sources is None:
        sources = [("akshare.push2delay", _board_from_akshare)]
        for host in SPOT_HOSTS[1:]:
            sources.append((host.split("//", 1)[1],
                            lambda h=host: _board_from_host(h, page_size=200)))
    errors = []
    for name, fn in sources:
        try:
            return fn(), name
        except Exception as e:  # noqa: BLE001 -- each source is a reading
            errors.append("%s: %s: %s" % (name, type(e).__name__, str(e)[:160]))
    raise RuntimeError("; ".join(errors))


def do_fetch(force=False, session=None) -> int:
    import time as _t
    if session:
        # r1604: a DELIBERATE re-capture of a session already on disk. The gate is right
        # to refuse a second pull of a captured session, but when the first pull's
        # denominator was one session behind (a published NAV arrives late), the honest
        # repair is to re-photograph that same session with the number since published --
        # and to say so. Hand-run only: never the chain's path.
        run, target, why = True, str(session), "explicit session re-capture"
    else:
        run, target, why = gate(force=force)
    if not run:
        print("fetch: no-op -- %s" % why)
        return 0
    try:
        df, source = _spot_board()
        print("board source: %s (%d rows)" % (source, len(df)))
    except Exception as e:  # noqa: BLE001 -- source failure is a reading, not a crash
        print("source failure: %s" % e)
        # r1599: the eastmoney family can refuse this host for a whole evening, and this
        # lane's holes do not heal -- the board stops carrying that session the moment it
        # rolls. Sina answers with the same session's tape (proven reachable), so use it
        # and let the snapshot say which reader produced it.
        try:
            try:
                from scripts import etf_premium_sina as _S
            except ImportError:
                # r1604: run as `python scripts/etf_premium_face.py`, sys.path[0] is the
                # scripts directory itself -- `scripts` then resolves to something else
                # ("unknown location") and the whole fallback died on the import, which is
                # the one branch that exists for the evenings eastmoney refuses this host.
                import etf_premium_sina as _S
            df, source = _S.board_for_session(target)
            print("board source: %s (%d rows)" % (source, len(df)))
        except Exception as e2:  # noqa: BLE001
            print("fallback also failed: %s" % e2)
            g = _read_gate()
            g.update({"last_fail_session": target,
                      "last_fail_ts": _t.strftime("%Y-%m-%dT%H:%M:%S"),
                      "last_fail_reason": (str(e)[:200] + " | fallback: " + str(e2)[:180])})
            _write_gate(g)
            return 2
    try:
        spot = normalize_spot(df)
    except ValueError as e:
        print(str(e))
        return 3
    session = sorted(set(spot["session"].dropna()))[-1]
    if session != target:
        # r1599: the file is named for the session the board actually printed, never for
        # the session we hoped to capture. A board that has already rolled past the
        # target (or still sits behind it) must not be filed under another day's name.
        print("fetch: no-op -- board reports %s, target session is %s" % (session, target))
        return 0
    os.makedirs(SNAP_DIR, exist_ok=True)
    path = _snap_path(session)
    tmp = path + ".tmp"
    spot.to_csv(tmp, index=False, encoding="utf-8")
    os.replace(tmp, path)
    print("snapshot: %s (%d rows, session %s)" % (os.path.relpath(path, ROOT), len(spot), session))
    nav_ok = fetch_nav_ok(session)
    _save_nav_ok(session, nav_ok)
    g = _read_gate()
    g.pop("last_fail_session", None)
    g.pop("last_fail_ts", None)
    g.pop("last_fail_reason", None)
    g["last_ok_session"] = session
    g["last_ok_ts"] = _t.strftime("%Y-%m-%dT%H:%M:%S")
    g["last_ok_source"] = source
    _write_gate(g)
    return _render(spot, _t.strftime("%Y-%m-%dT%H:%M:%S%z"), nav_ok, dating=load_dating())


def fetch_nav_ok(session: str):
    """Second source: which funds published a unit NAV on `session`.

    Failure to read it is not a reason to invent a number -- it downgrades the
    whole face to IOPV-only (nav_ok=None), which the face then says out loud.
    """
    try:
        import akshare as ak
        df = ak.fund_etf_fund_daily_em()
    except Exception as e:  # noqa: BLE001
        print("nav board unavailable (%s: %s) -- every premium is IOPV-only" % (type(e).__name__, e))
        return None
    ok = normalize_nav_board(df, session)
    if not ok:
        print("nav board carries no %s unit NAV -- every premium is IOPV-only" % session)
        return None
    print("nav board: %d funds published a unit NAV for %s" % (len(ok), session))
    return ok


def _nav_ok_path(session: str) -> str:
    return os.path.join(SNAP_DIR, "%s.navok.json" % session)


def _save_nav_ok(session: str, ok) -> None:
    """Persist membership AND the values: `render` runs with no network, so a rebase that
    was possible at fetch time has to still be possible on a re-render."""
    payload = {"session": session, "codes": None, "nav": None}
    if ok is not None:
        payload["codes"] = sorted(ok)
        payload["nav"] = {k: ok.nav[k] for k in sorted(ok.nav)} if getattr(ok, "nav", None) else None
    with open(_nav_ok_path(session), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)


def _cached_nav_ok(session: str):
    p = _nav_ok_path(session)
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            blob = json.load(f)
    except (OSError, ValueError):
        return None
    codes = blob.get("codes")
    if not codes:
        return None
    # Caches written before r2211 carry codes only: membership still works, there is just
    # nothing to re-price onto, which is the honest state for an older snapshot.
    return NavBoard(session, set(codes), blob.get("nav"))


def _load_snapshot() -> pd.DataFrame | None:
    if not os.path.isdir(SNAP_DIR):
        return None
    files = sorted(f for f in os.listdir(SNAP_DIR) if f.endswith(".csv"))
    if not files:
        return None
    return pd.read_csv(os.path.join(SNAP_DIR, files[-1]), dtype={"code": str, "session": str},
                       keep_default_na=True).assign(code=lambda d: d["code"].str.zfill(6))


def _render(spot: pd.DataFrame, fetched_at: str, nav_ok=None, dating=None) -> int:
    try:
        with open(TICKET_PATH, encoding="utf-8") as f:
            ticket = json.load(f)
    except (OSError, ValueError) as e:
        print("ticket unreadable: %s" % e)
        return 2
    face = build_face(spot, ticket, fetched_at, nav_ok, dating=dating)
    os.makedirs(OUT_DIR, exist_ok=True)
    js = os.path.join(OUT_DIR, "PREMIUM-%s.json" % face["session"])
    md = os.path.join(OUT_DIR, "PREMIUM-%s.md" % face["session"])
    with open(js, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    with open(md, "w", encoding="utf-8") as f:
        f.write(render_md(face))
    print("face: %s" % os.path.relpath(md, ROOT).replace("\\", "/"))
    for r in face["legs"]:
        prem = "unknown" if r["premium_pct"] is None else "%+.3f%%" % r["premium_pct"]
        print("  %s %-14s %10s %8s  %s" % (r["symbol"], r["name"][:12], format(r["amount_cny"], ",.0f"), prem, r["band"]))
    return 0


def _published_fetched_at(session: str):
    """Keep the original capture stamp when re-rendering a published session.

    A re-render after a code change (a new section, a new field) must not rewrite the
    provenance of a snapshot that was taken at a different moment -- 'local:<day>' is
    the fallback for a session that was never fetched by this tool.
    """
    p = os.path.join(OUT_DIR, "PREMIUM-%s.json" % session)
    try:
        with open(p, encoding="utf-8") as f:
            return (json.load(f).get("source") or {}).get("fetched_at")
    except (OSError, ValueError):
        return None


def do_render() -> int:
    spot = _load_snapshot()
    if spot is None:
        print("no local snapshot; run `fetch` first")
        return 2
    session = str(spot["session"].dropna().iloc[-1])
    print("rendering from local snapshot %s (no network)" % session)
    return _render(spot, _published_fetched_at(session) or "local:%s" % session,
                   _cached_nav_ok(session), dating=load_dating())


# ---------------------------------------------------------------- selftest

def selftest() -> int:
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    def board(rows, disc=None):
        df = pd.DataFrame(rows, columns=REQUIRED)
        if disc is not None:
            df["基金折价率"] = disc
        return df

    # L1 premium sign: price above IOPV is a positive premium.
    b = board([["510300", "沪深300ETF", 4.04, 4.00, 9e8, "2026-11-06"]])
    s = normalize_spot(b)
    leg("L1 price above IOPV reads as a positive premium", abs(s.loc[0, "premium_pct"] - 1.0) < 1e-9)

    # L2 a row with no IOPV has no premium -- NaN, never 0.
    b = board([["510300", "x", 4.04, np.nan, 9e8, "2026-11-06"]])
    s = normalize_spot(b)
    leg("L2 no IOPV -> NaN premium (not zero)", np.isnan(s.loc[0, "premium_pct"]))

    # L3 THE inversion leg: the board publishes a DISCOUNT rate, so a printed
    # +0.28 beside price 1.801 / IOPV 1.806 (a real 159981 row) is a DISCOUNT.
    # A reader that trusted the column would call it a premium and flip the band.
    b = board([["159981", "能源化工ETF建信", 1.801, 1.806, 1.4e9, "2026-11-06"]], disc=[0.28])
    s = normalize_spot(b)
    leg("L3 published 折价率 +0.28 reads as a -0.28% premium (never +0.28)",
        -0.35 < s.loc[0, "premium_pct"] < -0.20 and band(float(s.loc[0, "premium_pct"])) == "at-par")

    # L4 shape gate rejects a board missing a column.
    bad = pd.DataFrame([["510300", "x"]], columns=["代码", "名称"])
    try:
        normalize_spot(bad)
        ok = False
    except ValueError:
        ok = True
    leg("L4 shape drift (missing column) raises instead of guessing", ok)

    # L5 band edges.
    leg("L5 bands: 0.30 at-par / 1.00 watch / above stretched",
        band(0.30) == "at-par" and band(-0.99) == "watch" and band(1.01) == "stretched"
        and band(None) == "unknown")

    # L6 a leg the board does not carry is MISSING, not free.
    s = normalize_spot(board([["510300", "沪深300ETF", 4.04, 4.00, 9e8, "2026-11-06"]]))
    rows = leg_face({"order": [{"symbol": "513100", "amount": 100000.0, "class": "crossborder"}]}, s)
    leg("L6 unknown leg -> band=missing and no CNY figure", rows[0]["band"] == "missing"
        and rows[0]["over_nav_cny"] is None and rows[0]["premium_pct"] is None)

    # L7 CNY figure is signed against the ticket size.
    rows = leg_face({"order": [{"symbol": "510300", "amount": 100000.0, "class": "equity"}]}, s)
    leg("L7 over-NAV CNY scales with the ticket and keeps the sign",
        abs(rows[0]["over_nav_cny"] - 1000.0) < 1e-6)

    # L8 dispersion ignores names below the liquidity floor.
    b = board([["510300", "big", 4.04, 4.00, 9e8, "2026-11-06"],
               ["159999", "thin", 1.5, 1.4, 1e6, "2026-11-06"]])
    d = dispersion(normalize_spot(b))
    leg("L8 illiquid names stay out of the cross-section", d["n"] == 1 and d["median_pct"] == 1.0)

    # L9 top premium / top discount are opposite ends of the same set.
    b = board([["510300", "a", 4.04, 4.0, 9e8, "2026-11-06"],
               ["510050", "b", 2.0, 2.1, 9e8, "2026-11-06"],
               ["510500", "c", 6.0, 6.0, 9e8, "2026-11-06"]])
    d = dispersion(normalize_spot(b))
    leg("L9 extremes come from opposite sorts",
        d["top_premium"][0]["symbol"] == "510300" and d["top_discount"][0]["symbol"] == "510050")

    # L10 the renderer never crashes on an empty ticket and still prints its header.
    face = build_face(s, {"order": []}, "t:0")
    md = render_md(face)
    leg("L10 empty ticket still renders a one-pager", md.startswith("# 执行溢价面") and "诚实边界" in md)

    # L11 determinism: same board in -> same bytes out (no wall clock inside).
    f1 = build_face(s, {"order": []}, "t:0")
    f2 = build_face(s.copy(), {"order": []}, "t:0")
    leg("L11 face is deterministic for the same board", json.dumps(f1, sort_keys=True) == json.dumps(f2, sort_keys=True))

    # L12 a row whose IOPV is <= 0 must not produce a premium (guard division by zero).
    b = board([["510300", "x", 4.04, 0.0, 9e8, "2026-11-06"]])
    s2 = normalize_spot(b)
    leg("L12 IOPV<=0 -> NaN, no division", np.isnan(s2.loc[0, "premium_pct"]))

    # L13 cross-check counts a disagreement instead of silently preferring a side.
    b = board([["510300", "x", 4.04, 4.00, 9e8, "2026-11-06"]], disc=[1.0])
    s2 = normalize_spot(b)
    leg("L13 a board that disagrees with price/IOPV is counted, not averaged",
        bool(s2.loc[0, "cross_check_bad"]) and abs(s2.loc[0, "premium_pct"] - 1.0) < 1e-9)

    # L14 the table path itself renders (L10 only proves the empty case): a face
    # with one priced leg and one missing leg must print both rows.
    face = build_face(s, {"order": [{"symbol": "510300", "amount": 100000.0, "class": "equity"},
                                    {"symbol": "513100", "amount": 50000.0, "class": "crossborder"}]}, "t:0")
    md = render_md(face)
    leg("L14 ticket table renders priced and missing legs",
        "510300" in md and "513100" in md and "未定价腿" in md)

    # L15 the NAV board's dated column decides membership: '---' is NOT a NAV.
    nb = pd.DataFrame([["510300", "沪深300ETF", "4.1312", "4.12"],
                       ["513100", "纳指ETF国泰", "---", "---"]],
                      columns=["基金代码", "基金简称", "2026-11-06-单位净值", "2026-11-05-单位净值"])
    ok_set = normalize_nav_board(nb, "2026-11-06")
    leg("L15 NAV board: a fund that printed '---' is not 'has a NAV'",
        ok_set.codes == frozenset({"510300"}) and not len(normalize_nav_board(nb, "2026-11-07")))

    # L15b (r2211) the board keeps the VALUE, not just the name: membership alone let a
    # leg claim `iopv+same-day-nav` while its own denominator was a day older.
    leg("L15b NAV board carries the published value (the rebase source)",
        ok_set.value("510300") == 4.1312 and ok_set.value("513100") is None
        and ok_set.value("510300") and len(normalize_nav_board(nb, "2026-11-07").nav) == 0)

    # L15c (r2211) THE defect, re-created: price 1.685 against the board's 11-26 NAV
    # 1.6974 (-0.73%) while the session's own NAV 1.7010 was already published. Printed
    # as same-day it overstated the leg; re-priced it reads -0.94%, and the board's
    # reading stays visible instead of being overwritten.
    b_fgn = board([["159519", "港股国企", 1.685, 1.6974, 2e8, "2026-11-27"]])
    b_fgn["净值日期"] = ["2026-11-26"]   # the board's own denominator date column
    s_fgn = normalize_spot(b_fgn)
    nb_fgn = NavBoard("2026-11-27", {"159519"}, {"159519": 1.7010})
    r_rebased = leg_face({"order": [{"symbol": "159519", "amount": 86946.0, "class": "crossborder"}]},
                         s_fgn, nb_fgn, session="2026-11-27")[0]
    leg("L15c foreign denominator + a same-day NAV on the board -> re-priced, not claimed",
        r_rebased["trust"] == "nav-rebased-same-day"
        and r_rebased["nav_session"] == "2026-11-27"
        and abs(r_rebased["premium_pct"] + 0.9406) < 1e-3
        and abs(r_rebased["over_nav_cny"] + 817.8) < 0.1
        and r_rebased["board_reading"]["raw_nav"] == 1.6974
        and r_rebased["board_reading"]["raw_nav_session"] == "2026-11-26")

    # L15d the same leg with NO published same-day NAV (a T+n QDII) must not be priced
    # at all: it keeps the board's cross-date percentage and carries no CNY figure.
    r_cross = leg_face({"order": [{"symbol": "159519", "amount": 86946.0, "class": "crossborder"}]},
                       s_fgn, NavBoard("2026-11-27", {"159519"}), session="2026-11-27")[0]
    leg("L15d foreign denominator, no same-day NAV -> named cross-date, no money",
        r_cross["trust"] == "nav-cross-date" and r_cross["band"] == "unverified"
        and r_cross["over_nav_cny"] is None and abs(r_cross["premium_pct"] + 0.7305) < 1e-3)

    # L16 with the second source in hand, an uncheckable leg is UNVERIFIED:
    # it keeps its raw IOPV reading but must not be priced in CNY.
    s3 = normalize_spot(board([["513100", "纳指ETF国泰", 2.158, 1.7797, 4e8, "2026-11-06"],
                               ["510300", "沪深300ETF", 4.124, 4.1349, 9e8, "2026-11-06"]]))
    rows = leg_face({"order": [{"symbol": "513100", "amount": 90000.0, "class": "crossborder"},
                               {"symbol": "510300", "amount": 90000.0, "class": "equity"}]}, s3, {"510300"})
    leg("L16 unverifiable leg is unverified, not 'stretched' and not priced",
        rows[0]["band"] == "unverified" and rows[0]["over_nav_cny"] is None
        and abs(rows[0]["premium_pct"] - 21.2564) < 1e-3
        and rows[1]["band"] != "unverified" and rows[1]["over_nav_cny"] is not None)

    # ---- r2215: a printed date is a label; the price path is a proof.
    def _dating(items, min_move=1.0):
        return {"available": True, "board_session": "2026-11-27", "min_move_pct": min_move,
                "generated": "t:0",
                "by_code": {c: {"position": p, "sina_position": p, "move_pct": m,
                                "sina_nav": nv, "sina_nav_date": nd, "board_missing": bm}
                            for c, p, m, nv, nd, bm in items}}

    b_lab = board([["513630", "标普500ETF", 1.545, 1.5584, 3e8, "2026-11-27"],
                   ["513690", "恒生红利ETF", 1.103, 1.1161, 3e8, "2026-11-27"]])
    b_lab["净值日期"] = ["2026-11-27"] * len(b_lab)   # the batch stamp says this session
    s_lab = normalize_spot(b_lab)
    d_prev = _dating([("513630", "PREV_SESSION", -1.278, 1.5603, "2026-11-27", False)])

    # L41 THE label defect: the row carries the session's own date only because the whole
    # batch was stamped that day, while the instrument's own move says its denominator is
    # yesterday's. The path wins: no same-day claim and no CNY figure.
    r_lab = leg_face({"order": [{"symbol": "513630", "amount": 86916.0, "class": "crossborder"}]},
                     s_lab, None, session="2026-11-27", dating=d_prev)[0]
    leg("L41 a same-day label overruled by the price path is not priced as same-day",
        r_lab["trust"] == "nav-cross-date" and r_lab["over_nav_cny"] is None
        and r_lab["date_proof"] == "path-overrules-label")

    # L42 ... and when the session's own NAV is on the board it is re-priced, not refused.
    r_lab2 = leg_face({"order": [{"symbol": "513630", "amount": 100000.0, "class": "crossborder"}]},
                      s_lab, NavBoard("2026-11-27", {"513630"}, {"513630": 1.5300}),
                      session="2026-11-27", dating=d_prev)[0]
    leg("L42 the overruled leg is re-priced on the session NAV when one is published",
        r_lab2["trust"] == "nav-rebased-same-day"
        and abs(r_lab2["premium_pct"] - 0.9804) < 1e-3
        and r_lab2["date_proof"] == "path-overrules-label")

    # L43 a date the path cannot pin (|move| under 1%) keeps its number and says it is a label.
    d_und = _dating([("513690", "UNDECIDABLE", -0.7201, 1.1137, "2026-11-27", False)])
    r_und = leg_face({"order": [{"symbol": "513690", "amount": 86916.0, "class": "crossborder"}]},
                     s_lab, None, session="2026-11-27", dating=d_und)[0]
    leg("L43 an unpinnable date keeps the number but is marked label-only",
        r_und["date_proof"] == "label-only" and r_und["date_ambiguous_pp"] == 1.0
        and r_und["over_nav_cny"] is not None)

    # L44 no dating face at all: the older label behaviour stands, and the face says so
    # rather than quietly looking proven.
    r_noev = leg_face({"order": [{"symbol": "513690", "amount": 86916.0, "class": "crossborder"}]},
                      s_lab, None, session="2026-11-27",
                      dating={"available": False, "why": "x"})[0]
    leg("L44 no dating face -> label behaviour unchanged, and dated 'no-evidence-face'",
        r_noev["trust"] == "iopv+same-day-nav" and r_noev["date_proof"] == "no-evidence-face")

    # L45 a leg the board skips is not a leg nothing is known about: name the dated value
    # another source carries, and keep it out of the pricing (different reader).
    d_alt = _dating([("159655", "NO_DATA", 2.8297, 1.7413, "2026-11-28", True)])
    r_alt = leg_face({"order": [{"symbol": "159655", "amount": 86862.6, "class": "crossborder"}]},
                     s_lab, None, session="2026-11-27", dating=d_alt)[0]
    leg("L45 a board gap still names what another source dated (and does not price it)",
        r_alt["trust"] == "no-quote" and r_alt["premium_pct"] is None
        and r_alt["alt_source"]["nav"] == 1.7413 and r_alt["date_proof"] == "board-has-no-row")

    # L47 evidence about another session may not decide this one: a dating face from a
    # different board session is ignored (and named), not applied as yesterday's proof.
    d_stale = _dating([("513630", "PREV_SESSION", -1.278, 1.5603, "2026-11-27", False)])
    d_stale["board_session"] = "2026-11-26"
    r_stale = leg_face({"order": [{"symbol": "513630", "amount": 86916.0, "class": "crossborder"}]},
                       s_lab, None, session="2026-11-27", dating=d_stale)[0]
    leg("L47 dating evidence about another session is named, not applied",
        r_stale["date_proof"] == "evidence-face-other-session"
        and r_stale["trust"] == "iopv+same-day-nav"
        and r_stale["over_nav_cny"] is not None)

    # L46 the page itself has to carry the distinction, not only the JSON.
    f_ev = build_face(s_lab, {"order": [{"symbol": "513630", "amount": 86916.0, "class": "crossborder"}]},
                      "t:0", None, dating=d_prev)
    md_ev = render_md(f_ev)
    leg("L46 the page says how each date is known, and names the overruled leg",
        "分母日期证据" in md_ev and "标签与路径不一致 1 腿" in md_ev
        and f_ev["date_evidence"]["overrules_label"] == ["513630"])

    # ---- the daily-chain gate (r1398). This face moved from a hand-run to an S6
    # leg, so the gate is now load-bearing: a wrong branch either photographs an
    # intraday board as the close, or re-pulls a captured session every cycle.
    import datetime as _dt
    DAYS = {"2026-11-06", "2026-11-09"}
    after_open = _dt.datetime(2026, 11, 9, 15, 45)
    before_close = _dt.datetime(2026, 11, 9, 11, 0)

    # L17 a non-trading day never fires.
    r = gate(now=_dt.datetime(2026, 11, 7, 16, 0), days=DAYS, snap_exists=False, gate_state={})
    leg("L17 weekend is a no-op, not an empty snapshot",
        r[0] is False and "not a trading session" in r[2])

    # L18 the close is the boundary: 11:00 is refused, 15:45 runs, --force overrides.
    # `snap_exists` is a callable here (r1599): a bare False would now arm the pre-close
    # backfill branch, so the leg states which sessions already hold a file.
    _prev_has = lambda s: s == "2026-11-06"
    r_before = gate(now=before_close, days=DAYS, snap_exists=_prev_has, gate_state={})
    r_after = gate(now=after_open, days=DAYS, snap_exists=_prev_has, gate_state={})
    r_forced = gate(now=before_close, force=True, days=DAYS, snap_exists=_prev_has, gate_state={})
    leg("L18 before 15:30 refused, after it armed, --force overrides the clock",
        r_before[0] is False and "before the 15:30 close" in r_before[2]
        and r_after[0] is True and r_forced[0] is True)

    # L19 a captured session is not re-pulled (the chain runs many times a day).
    r = gate(now=after_open, days=DAYS, snap_exists=lambda s: True, gate_state={})
    leg("L19 an already captured session is a no-op",
        r[0] is False and "already captured" in r[2])

    # L20 a failed attempt backs the source off for 30 minutes, then re-arms.
    fail_state = {"last_fail_session": "2026-11-09", "last_fail_ts": "2026-11-09T15:40:00"}
    r_soon = gate(now=_dt.datetime(2026, 11, 9, 15, 50), days=DAYS, snap_exists=False,
                  gate_state=fail_state)
    r_late = gate(now=_dt.datetime(2026, 11, 9, 16, 20), days=DAYS, snap_exists=False,
                  gate_state=fail_state)
    leg("L20 30-minute backoff after a failure, and only for the same session",
        r_soon[0] is False and "backoff" in r_soon[2] and r_late[0] is True
        and gate(now=after_open, days=DAYS, snap_exists=False,
                 gate_state={"last_fail_session": "2026-11-06",
                             "last_fail_ts": "2026-11-06T15:40:00"})[0] is True)

    # L21 an unreadable calendar is NOT a holiday: refusing to run is the honest
    # branch, because guessing gives us a snapshot with a name we invented.
    r = gate(now=after_open, days=None, snap_exists=False, gate_state={})
    leg("L21 unreadable calendar refuses instead of guessing a session",
        r[0] is False and "unreadable" in r[2] and gate(now=after_open, force=True)[0] is True)

    # L22 a board still carrying an older session must not be filed under today.
    # (The branch lives in do_fetch, so this leg pins the comparison itself.)
    leg("L22 a stale board day sorts below today and is skipped",
        "2026-11-06" < "2026-11-09" and not ("2026-11-07" >= "2026-11-09"))

    # L22b-L22e (r1599) the pre-close window is the ONLY chance to heal a missed
    # capture: after the board rolls, that session's tape is gone for good. The gate
    # used to refuse every pre-close run, so a source outage at 15:31 became a
    # permanent hole -- and three faces downstream stayed one session behind for ever.
    r_back = gate(now=before_close, days=DAYS, snap_exists=lambda s: False, gate_state={})
    leg("L22b before the close, a missing previous close is backfilled under its own name",
        r_back[0] is True and r_back[1] == "2026-11-06" and "backfilling" in r_back[2])

    r_done = gate(now=before_close, days=DAYS, snap_exists=_prev_has, gate_state={})
    leg("L22c before the close, nothing to backfill means wait for the close",
        r_done[0] is False and "before the 15:30 close" in r_done[2])

    r_bo = gate(now=_dt.datetime(2026, 11, 9, 9, 0), days=DAYS, snap_exists=lambda s: False,
                gate_state={"last_fail_session": "2026-11-06",
                            "last_fail_ts": "2026-11-09T08:45:00"})
    leg("L22d a failed backfill backs off against the session it tried, not against today",
        r_bo[0] is False and "backoff" in r_bo[2] and "2026-11-06" in r_bo[2])

    # The previous close is the previous SESSION, not "yesterday": Monday 09:00 asks
    # for Friday. A wall-clock subtraction would invent a Saturday.
    _mon = gate(now=_dt.datetime(2026, 11, 9, 9, 0),
                days={"2026-11-06", "2026-11-09", "2026-11-10"},
                snap_exists=lambda s: False, gate_state={})
    leg("L22e before the close the target is the last session, so Monday asks for Friday",
        _mon[0] is True and _mon[1] == "2026-11-06")

    # L23 the hurdle sums PRICED legs only. One leg at +1% on 1,000,000 = +10,000 CNY
    # breaches; the same ticket with an unverified leg of equal size does NOT get to
    # count that leg as zero-and-therefore-cheap -- the priced basis is unchanged.
    s4 = normalize_spot(board([["510300", "沪深300ETF", 4.04, 4.00, 9e8, "2026-11-06"],
                               ["513100", "纳指ETF国泰", 2.158, 1.7797, 4e8, "2026-11-06"]]))
    f_hit = build_face(s4, {"order": [{"symbol": "510300", "amount": 1_000_000.0, "class": "equity"}]}, "t:0")
    f_mixed = build_face(s4, {"order": [{"symbol": "510300", "amount": 1_000_000.0, "class": "equity"},
                                        {"symbol": "513100", "amount": 1_000_000.0, "class": "crossborder"}]},
                         "t:0", {"510300"})
    leg("L23 hurdle sums priced legs only and never counts unverified as zero",
        f_hit["over_hurdle"]["breached"] is True
        and abs(f_hit["over_hurdle"]["total_over_nav_cny"] - 10_000.0) < 1e-6
        and f_mixed["over_hurdle"]["total_over_nav_cny"] == 10_000.0
        and f_mixed["over_hurdle"]["priced_amount_cny"] == 1_000_000.0
        and f_mixed["unverified_legs"] == 1)

    # L24 a small premium on a small ticket is under the hurdle and says so, in the
    # renderer, not only in the JSON (the operator reads the page, not the file).
    f_low = build_face(normalize_spot(board([["510300", "x", 4.005, 4.00, 9e8, "2026-11-06"]])),
                       {"order": [{"symbol": "510300", "amount": 10_000.0, "class": "equity"}]}, "t:0")
    md = render_md(f_low)
    leg("L24 under the hurdle the page prints the figure instead of a warning",
        f_low["over_hurdle"]["breached"] is False and abs(f_low["over_hurdle"]["total_over_nav_cny"] - 12.5) < 1e-6
        and "执行闸" in md and "不提示" in md)

    # ---- board gaps (r1505). This board is the one face in the chain whose holes
    # cannot be healed by running the lane again, so naming them is load-bearing.
    import tempfile
    tmp = tempfile.mkdtemp(prefix="epf_gap_")
    for d in ("2026-11-05", "2026-11-06"):
        with open(os.path.join(tmp, "%s.csv" % d), "w", encoding="utf-8") as f:
            f.write("代码,名称\n")
    CAL = {"2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06",
           "2026-11-09", "2026-11-10"}

    # L25 a missing session is named, not smoothed over -- and coverage starts at the
    # first board, so 11-03/11-04 (before it) are not counted as holes.
    g = board_gap(now=_dt.datetime(2026, 11, 9, 16, 0), days=CAL, snap_dir=tmp)
    leg("L25 a session with no board is named as a hole, and the gap says it cannot be healed",
        g["missing"] == ["2026-11-09"] and g["n_missing"] == 1
        and g["recoverable"] is False and "realtime print" in g["why_unrecoverable"]
        and "2026-11-03" not in g["sessions_expected"]
        and g["next_capture_session"] == "2026-11-09"
        and g["next_capture_after"] is None)

    # L26 before the close, today is not yet a hole: an intraday board is not the session.
    g = board_gap(now=_dt.datetime(2026, 11, 9, 11, 0), days=CAL, snap_dir=tmp)
    leg("L26 before 15:30 today is pending, not missing",
        g["missing"] == [] and g["n_missing"] == 0
        and g["next_capture_session"] == "2026-11-09" and g["next_capture_after"] == "15:30")

    # L26b (r1883) the hole is not born the instant the close passes: the chain is armed
    # AT 15:30 and has to run. Three minutes later the session is DUE, and a page read
    # then must not print "the board is missing a day" about this afternoon.
    g = board_gap(now=_dt.datetime(2026, 11, 9, 15, 33), days=CAL, snap_dir=tmp)
    leg("L26b 15:33 today is pending (armed, not yet captured), not a hole",
        g["missing"] == [] and g["n_missing"] == 0 and g["pending"] == ["2026-11-09"]
        and g["next_capture_session"] == "2026-11-09")

    # L26c the grace window is bounded: once it expires, an uncaptured session IS a hole
    # (L25 already pins the 30-minute mark; this pins the edge so the window cannot grow
    # silently into "today is never missing").
    g = board_gap(now=_dt.datetime(2026, 11, 9, 16, 30), days=CAL, snap_dir=tmp)
    leg("L26c past the grace window today becomes a hole again",
        g["missing"] == ["2026-11-09"] and g["pending"] == [])

    # L27 an unreadable calendar is UNKNOWN, never "no gap" -- the r98 unknown!=empty law.
    g = board_gap(now=_dt.datetime(2026, 11, 9, 16, 0), days=None, snap_dir=tmp)
    leg("L27 unreadable calendar -> missing=None, not an empty list",
        g["status"] == "unreadable_calendar" and g["missing"] is None
        and g["n_missing"] is None)

    # L28 a captured session disappears from the list, and the next capture moves on.
    with open(os.path.join(tmp, "2026-11-09.csv"), "w", encoding="utf-8") as f:
        f.write("代码,名称\n")
    g = board_gap(now=_dt.datetime(2026, 11, 9, 16, 0), days=CAL, snap_dir=tmp)
    leg("L28 a captured session stops being a hole and the next capture is tomorrow",
        g["missing"] == [] and g["last_board"] == "2026-11-09"
        and g["next_capture_session"] == "2026-11-10")
    # an empty file is not a capture -- a truncated write must not read as "done"
    with open(os.path.join(tmp, "2026-11-10.csv"), "w", encoding="utf-8") as f:
        f.write("")
    g = board_gap(now=_dt.datetime(2026, 11, 10, 16, 0), days=CAL, snap_dir=tmp)
    leg("L29 a zero-byte board file is not a capture",
        g["missing"] == ["2026-11-10"] and g["last_board"] == "2026-11-09")

    # L30 failover: a dead first source is a reading, not the end of the lane -- the
    # second source's board is used and its name comes back with it.
    calls = []

    def dead():
        calls.append("dead")
        raise RuntimeError("RemoteDisconnected")

    def live():
        calls.append("live")
        return pd.DataFrame([{"f12": "510300", "f14": "沪深300ETF", "f2": 4.04,
                              "f6": 9e8, "f297": "20261112", "f441": 4.00}])
    got, src = _spot_board(sources=[("dead-host", dead), ("push2", live)])
    leg("L30 first source down -> second source answers, and it is named",
        src == "push2" and calls == ["dead", "live"] and len(got) == 1)

    # L31 every source down -> the failure text names each one (no silent last-only).
    try:
        _spot_board(sources=[("a", dead), ("b", dead)])
        text = ""
    except RuntimeError as e:
        text = str(e)
    leg("L31 all sources down -> error names every source tried",
        "a: RuntimeError" in text and "b: RuntimeError" in text)

    # L32 the raw-host path renames the board into exactly what normalize_spot reads,
    # and it pages (a 150-row board over 100-row pages must arrive whole).
    def fake_get(url, params):
        pn = int(params["pn"])
        if pn > 2:
            return {"data": {"total": 150, "diff": []}}
        n = 100 if pn == 1 else 50
        base = 0 if pn == 1 else 100
        rows = {str(i): {"f12": "51%04d" % i, "f14": "e%d" % i, "f2": 4.0,
                         "f6": 1e8, "f297": "20261112", "f441": 4.0}
                for i in range(base, base + n)}
        return {"data": {"total": 150, "diff": rows}}
    raw = _board_from_host("https://push2.eastmoney.com", get=fake_get, throttle_s=0)
    leg("L32 raw-host board pages to the total and carries the REQUIRED columns",
        len(raw) == 150 and [c for c in REQUIRED if c not in raw.columns] == []
        and normalize_spot(raw).loc[0, "session"] == "20261112")

    # L34 a page that fails once is retried in place before the host is declared dead
    # (this host drops connections after a handful of rapid requests).
    tries = {"n": 0}
    def flaky_get(url, params):
        tries["n"] += 1
        if tries["n"] == 1:
            raise ConnectionError("RemoteDisconnected")
        return {"data": {"total": 1, "diff": {"0": {"f12": "510300", "f14": "x",
                                                    "f2": 4.0, "f6": 1e8,
                                                    "f297": "20261112", "f441": 4.0}}}}
    retried = _board_from_host("https://x", get=flaky_get, throttle_s=0, retries=1)
    leg("L33 one dropped connection is retried, not reported as a dead host",
        tries["n"] == 2 and len(retried) == 1)

    # L33 a host that answers nothing usable is a failure, not an empty face.
    try:
        _board_from_host("https://x", get=lambda u, p: {"data": {"total": 0, "diff": []}})
        empty_ok = False
    except ValueError:
        empty_ok = True
    leg("L34 an empty board raises instead of rendering an empty face", empty_ok)

    # L35 r1600: the shipped snapshot calls the provenance column `source`; a reader that
    # only knows the in-memory `_source` relabels a sina file as eastmoney on every
    # re-render -- the face then shows the wrong denominator with no hint it forgot.
    b_nav = board([["510300", "x", 4.04, 4.00, 9e8, "2026-11-06"]])
    b_nav["source"] = [READER_NAV]
    s_nav = normalize_spot(b_nav)
    leg("L35 the snapshot's own `source` column survives normalization",
        str(s_nav.loc[0, "source"]) == READER_NAV, str(s_nav.loc[0, "source"]))

    # L36 a sina-only file must say so on the face -- block, table and caveat -- and must
    # never print the eastmoney reader it did not use.
    tk = {"order": [{"symbol": "510300", "amount": 100000.0, "class": "宽基"}]}
    face_nav = build_face(s_nav, tk, "2026-11-06T16:00:00")
    md_nav = render_md(face_nav)
    leg("L36 a sina fallback face names its denominator and never claims eastmoney",
        face_nav["source"]["readers"] == [READER_NAV]
        and "published unit NAV" in (face_nav["source"]["denominator"] or "")
        and "sina" in md_nav and "单位净值" in md_nav and "eastmoney" not in md_nav
        and any("published unit NAV" in c for c in face_nav["caveats"]))

    # L37 the historical eastmoney file keeps its sentence (no regression on the old path).
    b_em = board([["510300", "x", 4.04, 4.00, 9e8, "2026-11-06"]])
    face_em = build_face(normalize_spot(b_em), tk, "2026-11-06T15:10:00")
    md_em = render_md(face_em)
    leg("L37 an IOPV file still reads as the spot board",
        face_em["source"]["readers"] == [READER_IOPV]
        and "eastmoney" in (face_em["source"]["view"] or "")
        and "sina" not in md_em and "兜底" not in md_em)

    # L38 a mixed file is labelled mixed and each leg carries its own reader.
    b_mix = pd.concat([b_nav, b_em], ignore_index=True)
    b_mix.loc[1, "代码"] = "510050"
    face_mix = build_face(normalize_spot(b_mix),
                          {"order": [{"symbol": "510300", "amount": 1.0, "class": "x"},
                                     {"symbol": "510050", "amount": 1.0, "class": "x"}]},
                          "2026-11-06T16:00:00")
    md_mix = render_md(face_mix)
    leg("L38 a mixed file is labelled mixed and each leg names its own reader",
        face_mix["source"]["mixed"] is True
        and {r["source"] for r in face_mix["legs"]} == {READER_NAV, READER_IOPV}
        and "混用了两种读数" in md_mix)

    # L39 r1604: a denominator dated the PREVIOUS session is a cross-date gap, and the
    # page has to say so -- 2026-11-12 shipped +8.0% on 159655 built exactly that way.
    b_lag = board([["510300", "x", 4.04, 4.00, 9e8, "2026-11-06"]])
    b_lag["净值日期"] = ["2026-11-05"]
    face_lag = build_face(normalize_spot(b_lag), tk, "2026-11-06T16:00:00")
    md_lag = render_md(face_lag)
    leg("L39 a NAV one session behind is printed as a cross-date gap, not a premium",
        face_lag["denominator"]["verdict"] == "cross-date"
        and face_lag["legs"][0]["nav_session"] == "2026-11-05"
        and "跨日缺口" in md_lag and "2026-11-05" in md_lag)

    # L40 the same board dated for its own session reads as a premium -- and a snapshot
    # that predates the column reads as UNDATED, never as "same day".
    b_same = board([["510300", "x", 4.04, 4.00, 9e8, "2026-11-06"]])
    b_same["净值日期"] = ["2026-11-06"]
    face_same = build_face(normalize_spot(b_same), tk, "2026-11-06T16:00:00")
    face_old = build_face(normalize_spot(board([["510300", "x", 4.04, 4.00, 9e8, "2026-11-06"]])),
                          tk, "2026-11-06T16:00:00")
    leg("L40 same-session denominator reads as a premium; an undated snapshot says undated",
        face_same["denominator"]["verdict"] == "same-session"
        and "本场净值已公布" in render_md(face_same)
        and face_old["denominator"]["verdict"] == "undated"
        and face_old["legs"][0]["nav_session"] is None)

    ok = sum(1 for _, p, _ in legs if p)
    for name, p, detail in legs:
        print("[%s] %s%s" % ("PASS" if p else "FAIL", name, (" | " + detail) if detail else ""))
    print("selftest: %d/%d PASS" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", nargs="?", default="render", choices=["fetch", "render", "selftest"])
    ap.add_argument("--force", action="store_true",
                    help="bypass the session/close/backoff gate (a hand-run, never the chain)")
    ap.add_argument("--session", default=None,
                    help="re-capture THIS session (an earlier capture whose denominator "
                         "was published late); hand-run only, never the chain")
    a = ap.parse_args(argv)
    if a.mode == "selftest":
        return selftest()
    if a.mode == "fetch":
        return do_fetch(force=a.force, session=a.session)
    return do_render()


if __name__ == "__main__":
    sys.exit(main())