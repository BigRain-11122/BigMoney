"""One page, many bars -- which bar is each section of the CEO page actually priced on?

The operator page declares a single `priced_bar` at the top, and a reader naturally takes
every number below it as that day's. On 2026-11-11 the page on disk said 2026-11-10 while:

  * its `sibling`/`bets`/`concentration`/`sleeve_paths`/`exposure_timing`/`entry_gate`
    sections carried `evidence_cutoff = 2026-11-06`,
  * its capital table's last column read `止 2026-11-09` (a full bar behind),
  * its `cost_tape`/`vol_window`/`lookahead`/`sample_window` sections sat on 2026-10-30/26.

None of those is a bug in itself -- a section legitimately prices the bar its face was last
built on. What is missing is the word: the page never says so, so two sections quoting
different days look like two sections quoting one day that disagree (r1177 family: the two
figures are both true, but each one's universe is unstated).

This face answers that single question for every section it can find, and it is the ONE
implementation the smoke legs read when they have to decide whether a page-side difference is
a page defect or a different day (`_page_elsewhere_note`), so the answer cannot drift between
the face and the gates.

Two boundaries this face is careful about:

  * a section with no dated field is `unknown`, never assumed to share the headline -- the
    headline is exactly the claim under audit;
  * `lag_sessions` is counted on the official exchange calendar, not on our own panels
    (r1286: a panel cannot audit its own lateness).

Usage:
    python scripts/live_book_section_bars.py run
    python scripts/live_book_section_bars.py check
    python scripts/live_book_section_bars.py selftest
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import exchange_calendar_audit as CA  # noqa: E402  (the official calendar owner)

PAGE_DIR = os.path.join(ROOT, "docs", "live_book")
LATEST = os.path.join(PAGE_DIR, "latest.json")
OUT = os.path.join(ROOT, "results", "live_book_section_bars.json")
OUT_MD = os.path.join(ROOT, "results", "live_book_section_bars.md")

# the page writer spells the same idea three ways depending on the section's age
BAR_FIELDS = ("priced_bar", "evidence_cutoff", "panel_last_bar", "asof", "bar")
HEADLINE_FIELDS = ("priced_bar", "evidence_cutoff")

# r1617: BAR_FIELDS was written from the spellings the page *header* uses, and 11 of the 19
# sections the page then called "no date at all, unverifiable" were carrying one under a name
# this list never asked for -- `rate_date` on the cash yield, `spot_date` on the cash balance,
# `as_of` on the forward face, `panel_bar` on the live quote, `face_asof`, `session`. Telling
# a reader "this cannot be checked" about a section that states exactly which day it prices is
# the r1611 shape one floor up. Widening is FORM-checked, never name-trusted, because two
# neighbouring fields on this same page would be read wrong by a naive widening:
#   * `agreement.same_decision_bar` is the string "True" (a claim, not a day);
#   * `permission.decision_date` is "2026-12-09" -- the NEXT rebalance, i.e. the one date in
#     this file that must never be read as the bar a section is priced on.
BAR_FIELDS_LOOSE = ("as_of", "rate_date", "repo_rate_date", "spot_date", "panel_bar",
                    "quote_date", "face_asof", "session", "trade_date", "nav_date",
                    "data_date", "face_date")
_ISO_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}")


# A page behind by more than this many sessions is not "a different day", it is a page
# nobody refreshed -- that stays a hard finding on every host, not a note.
MAX_LAG_SESSIONS = 5

MIXED = "PAGE_MIXES_BARS"
SINGLE = "PAGE_ON_ONE_BAR"
NO_PAGE = "NO_PAGE"
NO_HEADLINE = "HEADLINE_UNKNOWN"

# A section sitting on an old bar has two very different causes, and printing them as one
# word leaves nobody able to act (r1199: a red that measures half the causes is not
# actionable): the section is a research face whose own check still passes (it stopped
# because that is the bar it was graded on), or nothing in the chain re-runs it at all.
# The only machine-readable half is the second one -- we can ask the shared leg list
# whether any leg names this section's artifact. That is a NAME match, stated as such;
# it does not claim the leg passed, only that a producer exists.
MIN_NAME_FOR_MATCH = 8

# r1623: `guarded_by == []` was printed as "nothing re-runs this section", and that is
# false for a section the page computes itself on every build -- which is exactly the four
# cash sections. They sit on the last bar of `data/repo_daily`, a lane that lives on
# another machine (update_repo.py / bm-a, this host only reads it), so a reader was told
# "nobody re-ran this" about numbers recomputed minutes ago whose only possible next move
# is upstream. The page now publishes where each self-computed section's number comes
# from; this face compares that panel's own last bar with the bar the section states, and
# calls it a writer debt only when the panel moved and the section did not.
CHAIN_LEG = "chain_leg"
COMPUTED_IN_PAGE = "computed_in_page"
NO_WRITER = "no_writer"

# r1628: a fifth state, and it is the same mistake one floor down from r1623. `sample_window`
# was the page's worst offender -- 13 sessions behind the headline -- and the audit printed it
# as if its numbers were priced on the bar 2026-10-26. They are not: that section measures two
# FIXED windows (2015-01-01..2019-12-31 on the pre-2020 universe, 2020-01-01..2026-10-26 on
# today's) and the date it carries is the END OF ITS OWN WINDOW, not a bar it failed to
# follow. "A window that ends here" and "a bar that stopped here" produce the same date and
# opposite actions: the first needs the whole window re-priced (minutes of engine), the second
# needs a leg re-run. So a section that publishes a window whose end equals the date it states
# is reported as window-bound -- and the reader is told what closing the gap would cost.
WINDOW_BOUND = "window_bound"
WINDOW_FIELDS = ("page_window", "window")


def window_of(d):
    """The [start, end] window a section publishes (page_window first), or None."""
    if not isinstance(d, dict):
        return None
    for f in WINDOW_FIELDS:
        w = d.get(f)
        if isinstance(w, (list, tuple)) and len(w) == 2 and all(w):
            return [str(w[0])[:10], str(w[1])[:10]]
    return None


def page_computed_of(page_computed, key):
    """The page's own declaration for a self-computed section, or None."""
    if not isinstance(page_computed, dict):
        return None
    v = page_computed.get(str(key))
    return v if isinstance(v, dict) else None


def _days(cal=None):
    try:
        return [str(d)[:10] for d in CA.load_calendar(cal or CA.CAL_PATH)]
    except Exception:
        return []


def sessions_between(a, b, cal=None):
    """Sessions in (a, b]; 0 when b <= a (a face ahead of the page is not a lag)."""
    a, b = str(a)[:10], str(b)[:10]
    if not a or not b or b <= a:
        return 0
    days = _days(cal)
    if not days:
        # no calendar: fall back to a weekday count and let the caller see the unit
        n, d = 0, dt.date.fromisoformat(a)
        end = dt.date.fromisoformat(b)
        while d < end:
            d += dt.timedelta(days=1)
            if d.weekday() < 5:
                n += 1
        return n
    return sum(1 for x in days if a < x <= b)


def bar_of(d):
    if not isinstance(d, dict):
        return None, None
    for f in BAR_FIELDS:
        v = d.get(f)
        if v not in (None, "", "None"):
            return str(v)[:10], f
    for f in BAR_FIELDS_LOOSE:
        v = d.get(f)
        if isinstance(v, str) and _ISO_DAY.match(v):
            return v[:10], f
    return None, None


def leg_names():
    """Names from the shared chain leg list, or [] when it cannot be imported.

    Imported, never copied: this list is already the single source (Tools/s6_chain_bma.py
    imports it the same way) and a second copy would drift exactly the way r1182 fixed.
    """
    try:
        p = os.path.join(ROOT, "Tools")
        if p not in sys.path:
            sys.path.insert(0, p)
        import s6_chain_bmc as canonical  # noqa: E402
        return [str(leg[0]) for leg in canonical.LEGS if leg]
    except Exception:
        return []


# A first cut matched leg NAMES only, and that printed `leg_split` as unproduced while
# `etf_book_leg_attribution` had been in the chain all along (r1135: the cheapest wrong
# answer is a confident false red). Source-text matching was tried next and was worse -- the
# page renderer and four consumer legs all mention `etf_book_lookahead_audit`, so a text
# match called a section produced by its own reader, and it still missed `leg_split`.
# What ships is a name match that says out loud it is only a name match, plus a hand-written
# alias table proven against the live leg list in the selftest -- a table can be checked, a
# heuristic cannot.
COMMON_STEMS = {"latest", "index", "status", "summary", "state", "today", "result"}
LEG_ALIASES = {"leg_split": ["etf_book_leg_attribution"],
               "sample_window": ["etf_book_spanning"]}


def probes_for(key, section):
    """Names a leg would have to carry to be this section's by name."""
    out = [str(key).lower()]
    art = section.get("artifact")
    if isinstance(art, str) and art:
        stem = os.path.splitext(os.path.basename(art.replace("\\", "/")))[0].lower()
        if stem not in COMMON_STEMS:
            out.append(stem)
    return [p for p in out if len(p) >= MIN_NAME_FOR_MATCH]


def guarded_by(key, section, legs):
    """Chain legs whose NAME matches this section (aliases included), or None if unaskable.

    None (leg list unavailable) is not [] (nothing matches) -- r98/r1159: a face we could
    not read must not print as a clean one.
    """
    if not legs:
        return None
    probes = probes_for(key, section)
    out = {str(l) for l in legs if any(p in str(l).lower() for p in probes)}
    out.update(LEG_ALIASES.get(str(key), []))
    return sorted(out)


def headline_bar(doc):
    for f in HEADLINE_FIELDS:
        v = (doc or {}).get(f)
        if v not in (None, "", "None"):
            return str(v)[:10], f
    return None, None


def section_bars(doc, cal=None, legs=None):
    """Every top-level section that carries a date, plus the count of those that do not."""
    head, head_field = headline_bar(doc)
    if legs is None:
        legs = leg_names()
    page_computed = (doc or {}).get("page_computed") or {}
    rows, unknown = [], []
    for k, v in (doc or {}).items():
        if k in ("page_computed",):      # r1623: provenance面, not a dated section
            continue
        if not isinstance(v, dict):
            continue
        b, f = bar_of(v)
        if b is None:
            unknown.append(k)
            continue
        g = guarded_by(k, v, legs)
        pc = page_computed_of(page_computed, k)
        win = window_of(v)
        if g:
            prov = CHAIN_LEG
        elif g == [] and pc is not None:
            prov = COMPUTED_IN_PAGE
        elif g == []:
            prov = NO_WRITER
        else:
            prov = None      # leg list unreadable: claim nothing (r98/r1159)
        # r1628: the date IS the end of the section's own window -- a fixed-window study, not
        # a bar that stopped following the page. Checked before the table is printed; the
        # guarded_by list stays as it is (the table still shows who mentions it).
        window_bound = bool(win and str(win[1])[:10] == str(b)[:10])
        rows.append({"key": k, "bar": b, "field": f,
                     "lag_sessions": sessions_between(b, head, cal) if head else None,
                     "ahead_of_headline": bool(head and b > head),
                     "guarded_by": g, "provenance": prov,
                     "window": win, "window_bound": window_bound,
                     "pricing_mode": ((v.get("pricing") or {}).get("mode")
                                      if isinstance(v.get("pricing"), dict) else None),
                     "refresh_reprices": ((v.get("pricing") or {}).get("reprices_bar")
                                          if isinstance(v.get("pricing"), dict) else None),
                     "panel": (pc or {}).get("panel"),
                     "panel_last_bar": (pc or {}).get("panel_last_bar"),
                     "panel_owner": (pc or {}).get("owner_lane")})
    hist = {}
    for r in rows:
        hist[r["bar"]] = hist.get(r["bar"], 0) + 1
    behind = [r for r in rows if head and r["bar"] != head]
    behind.sort(key=lambda r: (r["bar"], r["key"]))
    pc_rows = [r for r in behind if r.get("provenance") == COMPUTED_IN_PAGE]
    # Two very different states inside COMPUTED_IN_PAGE: the section sits exactly on its
    # panel's last bar (the panel is the thing that stopped), or the panel has a newer bar
    # and the section did not move (a real writer debt behind a page-computed face).
    pc_on_tail = [r for r in pc_rows
                  if r.get("panel_last_bar") and r["bar"] == str(r["panel_last_bar"])[:10]]
    nw_rows = [r for r in behind if r.get("provenance") == NO_WRITER]
    # r1628: window-bound sections are counted, but they are NOT the worst lag: their lag is
    # measured from the end of a window they state, so it can never shrink without re-pricing
    # the window (see WINDOW_BOUND above).
    wb_rows = [r for r in behind if r.get("window_bound")]
    # r1627: a leg whose NAME matches says "something mentions this", not "something can move
    # it". The width family is re-aggregated every chain cycle from eleven engine-priced arm
    # faces, so it sat four sessions behind the book while the audit counted it as guarded --
    # a section declared by its own face as engine-priced with a non-repricing leg is data
    # debt, and a reader has to be told that instead of "the page is not at fault".
    eg_rows = [r for r in behind
               if r.get("pricing_mode") == "engine" and r.get("refresh_reprices") is False]
    return {
        "headline_bar": head,
        "headline_field": head_field,
        "sections": rows,
        "by_key": {r["key"]: r["bar"] for r in rows},
        "unknown_sections": unknown,
        "n_sections": len(rows),
        "n_on_headline": len(rows) - len(behind),
        "bars": dict(sorted(hist.items(), reverse=True)),
        "n_off_headline": len(behind),
        "off_headline": behind,
        "oldest": min(hist) if hist else None,
        "max_lag_sessions": max([r["lag_sessions"] or 0 for r in rows] or [0]),
        "n_unguarded": (None if not legs else
                        sum(1 for r in behind if r.get("guarded_by") == [])),
        "unguarded": (None if not legs else
                      [r["key"] for r in behind if r.get("guarded_by") == []]),
        "n_page_computed": (None if not legs else len(pc_rows)),
        "page_computed": (None if not legs else [r["key"] for r in pc_rows]),
        "page_computed_on_panel_tail": (None if not legs else [r["key"] for r in pc_on_tail]),
        "page_computed_panels": (None if not legs else
                                 sorted({"%s（%s，末行 %s）" % (r.get("panel") or "?",
                                                              r.get("panel_owner") or "属主未声明",
                                                              r.get("panel_last_bar") or "?")
                                         for r in pc_rows})),
        "n_no_writer": (None if not legs else len(nw_rows)),
        "no_writer": (None if not legs else [r["key"] for r in nw_rows]),
        "n_engine_priced": (None if not legs else len(eg_rows)),
        "engine_priced": (None if not legs else [r["key"] for r in eg_rows]),
        "n_window_bound": len(wb_rows),
        "window_bound": [r["key"] for r in wb_rows],
    }


def _paths(page=None, jsonp=None):
    """(page md, page json) for the page the pointer names, else the newest pair on disk.

    An explicitly named json is used as given -- a caller probing a page that does not exist
    must get NO_PAGE, not this repository's newest page (the same trap as a leg that opens
    `today.md` and reads yesterday's absence as a defect).
    """
    if jsonp:
        return page or (jsonp[:-5] + ".md"), jsonp
    if page:
        return page, page[:-3] + ".json"
    try:
        with open(LATEST, encoding="utf-8") as fh:
            ptr = json.load(fh) or {}
        md = os.path.join(ROOT, ptr.get("page") or "")
        js = os.path.join(ROOT, ptr.get("json") or "")
        if os.path.exists(md) and os.path.exists(js):
            return md, js
    except Exception:
        pass
    cands = sorted(__import__("glob").glob(os.path.join(PAGE_DIR, "LIVE-BOOK-*.json")))
    if not cands:
        return None, None
    js = cands[-1]
    return js[:-5] + ".md", js


def assess(page=None, jsonp=None, cal=None, legs=None):
    md, js = _paths(page, jsonp)
    face = {"script": "scripts/live_book_section_bars.py",
            "ts": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "page": {"path": None if md is None else os.path.relpath(md, ROOT).replace(os.sep, "/"),
                     "json": None if js is None else os.path.relpath(js, ROOT).replace(os.sep, "/")},
            "verdict": NO_PAGE, "sentence": "", "evidence_cutoff": None}
    if js is None or not os.path.exists(js):
        face["sentence"] = "磁盘上没有 CEO 页面，" + NO_PAGE
        return face
    try:
        with open(js, encoding="utf-8") as fh:
            doc = json.load(fh) or {}
    except Exception as e:
        face["sentence"] = "页面 JSON 打不开（%r），不能替它说话" % (e,)
        return face
    sb = section_bars(doc, cal, legs)
    face.update({k: sb[k] for k in ("headline_bar", "headline_field", "n_sections",
                                    "n_on_headline", "unknown_sections", "bars",
                                    "n_off_headline", "off_headline", "oldest",
                                    "max_lag_sessions", "by_key", "n_unguarded",
                                    "unguarded", "n_page_computed", "page_computed",
                                    "page_computed_on_panel_tail", "page_computed_panels",
                                    "n_no_writer", "no_writer",
                                    "n_engine_priced", "engine_priced",
                                    "n_window_bound", "window_bound")})
    face["evidence_cutoff"] = sb["headline_bar"]
    if sb["headline_bar"] is None:
        face["verdict"] = NO_HEADLINE
        face["sentence"] = ("页面没有声明任何一根 bar（%d 节里 %d 节带日期），"
                            "所以「这一页是哪一天的」无法确认。" %
                            (sb["n_sections"], sb["n_sections"] - len(sb["unknown_sections"])))
    elif sb["n_off_headline"] == 0 and not sb["unknown_sections"]:
        face["verdict"] = SINGLE
        face["sentence"] = ("页面声明的 %s 就是它全部 %d 节的 bar——"
                            "下面每个数都是这一天的。" % (sb["headline_bar"], sb["n_sections"]))
    else:
        face["verdict"] = MIXED
        # r1628: the worst lag must not be a section whose date is the end of its own window
        # (it would name the one row that cannot shrink by re-running a leg).
        _lagged = [r for r in (sb["off_headline"] or []) if not r.get("window_bound")]
        worst = max(_lagged, key=lambda r: r["lag_sessions"] or 0) if _lagged else None
        oldest_lagged = min([r["bar"] for r in _lagged]) if _lagged else sb["oldest"]
        face["sentence"] = (
            "页面头部写着按 %s 定价，但 %d 个带日期的节里只有 %d 节真在这一天；"
            "其余 %d 节不在这一天（最旧停在 %s%s），另外 %d 节根本没有日期——"
            "它们不是同一根 bar 上的数，读的时候不能互相加减。" %
            (sb["headline_bar"], sb["n_sections"], sb["n_on_headline"],
             sb["n_off_headline"], oldest_lagged,
             ("（最差 %s 落后 %d 个交易日）" % (worst["key"], worst["lag_sessions"])
              if worst and worst["lag_sessions"] else ""),
             len(sb["unknown_sections"])))
        if sb.get("n_unguarded") is not None:
            n_leg = sb["n_off_headline"] - sb["n_unguarded"]
            parts = ["这 %d 节里，%d 节的产物有同名链腿在守" % (sb["n_off_headline"], n_leg)]
            if sb.get("n_page_computed"):
                pc = sb["page_computed"]
                tail = sb.get("page_computed_on_panel_tail") or []
                if len(tail) == len(pc):
                    parts.append(
                        "%d 节（%s）是这一页每次生成时自己重算的，停的正是它读的那块面板的最后一天：%s"
                        "——落后的是那块面板，不是没人重跑这节"
                        % (len(pc), ", ".join(pc[:6]),
                           "、".join((sb.get("page_computed_panels") or [])[:2])))
                else:
                    parts.append(
                        "%d 节（%s）是这一页自己重算的，其中 %d 节坐在面板末行上、"
                        "%d 节面板已经有了新 bar 它还停在原处"
                        % (len(pc), ", ".join(pc[:6]), len(tail), len(pc) - len(tail)))
            if sb.get("n_no_writer"):
                parts.append("%d 节（%s）没有任何一条链腿重跑过它们——那是这一页真正的缺口"
                             % (sb["n_no_writer"], ", ".join((sb["no_writer"] or [])[:6])))
            if sb.get("n_engine_priced"):
                parts.append("%d 节（%s）的日期是引擎跑出来的，守它的腿只把旧面重新汇总、不会"
                             "重新定价——它们的落后是数据债，链上再跑多少轮也不会自己追上来"
                             % (sb["n_engine_priced"], ", ".join((sb["engine_priced"] or [])[:6])))
            if sb.get("n_window_bound"):
                _wb = [r for r in (sb["off_headline"] or []) if r.get("window_bound")]
                _txt = "、".join("%s（%s 至 %s）" % (r["key"], (r.get("window") or ["?", "?"])[0],
                                                  (r.get("window") or ["?", "?"])[1])
                                for r in _wb[:3])
                parts.append("另外 %d 节 %s 讲的是一整段固定窗口，它印的日期就是那段窗口自己的终点，"
                             "不是某一根 bar 没跟上——要它站到页头那根 bar 上，等于把整段窗口"
                             "重新定价一遍" % (len(_wb), _txt))
            if len(parts) > 1:
                face["sentence"] += "；".join(parts) + "。"
            elif not sb["n_unguarded"]:
                face["sentence"] += ("这 %d 节的产物各自都有同名链腿在守，"
                                     "停在原来的 bar 是它们各自被评分的那一天，不是页面的错。" %
                                     sb["n_off_headline"])
    return face


def ticket_lines(face):
    """What the sheet prints: the headline, the sentence, the sections that are not on it."""
    L = []
    if not face or face.get("verdict") == NO_PAGE:
        L.append("页面逐节 bar：**磁盘上没有页面**，无可核对。")
        return L
    if face.get("sentence"):
        L.append("%s" % face["sentence"].rstrip("。") + "。")
        L.append("")
    L.append("页面逐节 bar：头部声明 **%s**，%d 个带日期的节里 **%s** 节在这一天，"
             "其余 %s 节在别的 bar 上。" %
             (face.get("headline_bar"), face.get("n_sections"), face.get("n_on_headline"),
              face.get("n_off_headline")))
    if face.get("off_headline"):
        rows = face["off_headline"]
        L.append("")
        L.append("| 节 | 它停在哪根 bar | 落后（交易日） | 守它的链腿 |")
        L.append("|---|---|---|---|")
        for r in rows[:12]:
            g = r.get("guarded_by")
            if r.get("window_bound"):
                _w = r.get("window") or ["?", "?"]
                cell = "窗口段（%s 至 %s）" % (_w[0], _w[1])
            elif g is None:
                cell = "未核验"
            elif g:
                cell = "、".join(g[:2])
            elif r.get("provenance") == COMPUTED_IN_PAGE:
                cell = "页内重算（%s 末行 %s）" % (r.get("panel") or "?", r.get("panel_last_bar") or "?")
            else:
                cell = "**没有**"
            L.append("| %s | %s | %s | %s |" % (r["key"], r["bar"], r.get("lag_sessions"), cell))
        if len(rows) > 12:
            L.append("| …其余 %d 节 | | | |" % (len(rows) - 12))
        L.append("")
        L.append("「守它的链腿」是按名字匹配的链清单（腿名含该节的名字或产物名），"
                 "只回答「有没有一条腿会重跑它」，不回答那条腿上次过没过——"
                 "这两件事在页面上一向是两个错。"
                 "标着「页内重算」的节不是没腿跑：这一页每次生成都把它们算一遍，"
                 "它们停在那天是因为下面那块面板只到那天，动作在上游数据车道，不在本页。"
                 "标着「窗口段」的节也不是没更新：它本来就是按一整段固定窗口量的，"
                 "印的那个日期是窗口的终点，要它跟上页头只能把整段窗口重算一遍（那是引擎的活，不是链腿的活）。"
                 "印「没有」的那几节，才是这一页真正的缺口。")
    if face.get("unknown_sections"):
        L.append("")
        L.append("这 %d 节没有任何日期字段，本面**不替它们认领**任何一根 bar：%s。"
                 % (len(face["unknown_sections"]), ", ".join(face["unknown_sections"][:12])))
    return L


def run():
    face = assess()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    md = ["# CEO 页面：这一页是哪一天的（r1533）", "",
          "*由 `scripts/live_book_section_bars.py` 生成；判据见文件头。*", ""] \
        + ticket_lines(face) + [""]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))
    print("[live_book_section_bars] %s | %s | %s" %
          (face["verdict"], face.get("headline_bar"), face.get("sentence")[:120]))
    print("[live_book_section_bars] wrote %s" % os.path.relpath(OUT, ROOT).replace(os.sep, "/"))
    return 0


def check():
    if not os.path.exists(OUT):
        print("[check] %s missing" % os.path.relpath(OUT, ROOT))
        return 2
    with open(OUT, encoding="utf-8") as fh:
        pub = json.load(fh) or {}
    fresh = assess()
    diffs = []
    for k in ("verdict", "headline_bar", "n_sections", "n_off_headline", "oldest",
              "max_lag_sessions", "by_key", "unknown_sections", "n_page_computed",
              "no_writer", "n_engine_priced", "engine_priced",
              "n_window_bound", "window_bound"):
        if pub.get(k) != fresh.get(k):
            diffs.append("%s published=%r fresh=%r" % (k, pub.get(k), fresh.get(k)))
    if diffs:
        print("[check] NONZERO " + "; ".join(diffs)[:400])
        return 1
    print("[check] CHECK_OK verdict=%s headline=%s off=%d unknown=%d"
          % (fresh["verdict"], fresh.get("headline_bar"), fresh.get("n_off_headline", 0),
             len(fresh.get("unknown_sections") or [])))
    return 0


def selftest():
    legs = []

    def leg(name, ok):
        legs.append((name, bool(ok)))

    mixed = {"priced_bar": "2026-11-10", "evidence_cutoff": "2026-11-10",
             "sleeve_gate": {"evidence_cutoff": "2026-11-10"},
             "entry_gate": {"evidence_cutoff": "2026-11-06", "panel_last_bar": "2026-11-06"},
             "cost_tape": {"evidence_cutoff": "2026-10-30"},
             "capital_cny": 100000, "n_hold": 5}
    sb = section_bars(mixed, legs=[])
    leg("L1 a page whose sections sit on three bars names both off-headline sections",
        sb["headline_bar"] == "2026-11-10" and sb["n_off_headline"] == 2)
    leg("L2 the histogram counts sections, not fields", sum(sb["bars"].values()) == sb["n_sections"] == 3)
    leg("L3 the oldest section is named", sb["oldest"] == "2026-10-30")
    leg("L4 lag is counted forward from the section to the headline",
        [r["lag_sessions"] for r in sb["off_headline"] if r["key"] == "entry_gate"][0] >= 1)
    leg("L5 a scalar section is not a section (headline fields are not audited against themselves)",
        all(r["key"] not in ("priced_bar", "evidence_cutoff", "capital_cny") for r in sb["sections"]))

    single = {"priced_bar": "2026-11-10", "a": {"evidence_cutoff": "2026-11-10"},
              "b": {"panel_last_bar": "2026-11-10"}}
    leg("L6 one bar everywhere is PAGE_ON_ONE_BAR",
        section_bars(single, legs=[])["n_off_headline"] == 0)

    undated = {"priced_bar": "2026-11-10", "a": {"evidence_cutoff": "2026-11-10"},
               "z": {"sentence": "no date here"}}
    leg("L7 an undated section is named, never assumed to share the headline",
        section_bars(undated, legs=[])["unknown_sections"] == ["z"])

    leg("L7b the sections on the headline plus the ones off it are all the dated sections",
        sb["n_on_headline"] + sb["n_off_headline"] == sb["n_sections"] == 3
        and sb["n_on_headline"] == 1)

    leg("L8 a section ahead of the headline is not a lag",
        sessions_between("2026-11-10", "2026-11-06") == 0)
    leg("L9 the calendar counts sessions, not days",
        sessions_between("2026-11-06", "2026-11-10") == 2)
    leg("L10 the same date is zero sessions", sessions_between("2026-11-10", "2026-11-10") == 0)

    face = assess(jsonp=os.path.join(ROOT, "results", "_no_such_page.json"))
    leg("L11 a missing page says NO_PAGE and claims no bar",
        face["verdict"] == NO_PAGE and face["evidence_cutoff"] is None)

    t = "\n".join(ticket_lines(assess(jsonp=os.path.join(ROOT, "results", "_no_such_page.json"))))
    leg("L12 the sheet does not invent a bar for a page it cannot read", "没有页面" in t)

    # r1189 family: a stale section has two causes, and the second one is the only
    # actionable half. The face must say which, from a name match it states as a name match.
    guarded = {"priced_bar": "2026-11-10",
               "cost_tape": {"evidence_cutoff": "2026-10-30",
                             "artifact": "results/etf_book_cost_tape.json"},
               "lookahead": {"evidence_cutoff": "2026-10-30",
                             "artifact": "results/etf_book_lookahead_audit.json"}}
    LEGS_FAKE = ["etf_book_cost_tape", "etf_book_ceo_page", "etf_book_leg_attribution"]
    gsb = section_bars(guarded, legs=LEGS_FAKE)
    leg("L15 a section whose artifact name appears in a leg name is attributed to that leg",
        [r["guarded_by"] for r in gsb["off_headline"] if r["key"] == "cost_tape"] == [["etf_book_cost_tape"]])
    leg("L16 a stale section nothing in the chain names is printed as unguarded, by name",
        gsb["unguarded"] == ["lookahead"] and gsb["n_unguarded"] == 1)
    leg("L17 an unavailable leg list is 'not checked', never 'nothing guards it'",
        section_bars(guarded, legs=[])["n_unguarded"] is None
        and section_bars(guarded, legs=[])["unguarded"] is None)

    fx = guarded
    tmp = os.path.join(ROOT, "results", "_tmp_section_bars_fixture.json")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(fx, fh)
    try:
        f2 = assess(jsonp=tmp, legs=LEGS_FAKE)
        leg("L19 the printed sentence carries the split, not just the count of stale sections",
            "没有任何一条链腿重跑过" in f2["sentence"] and "lookahead" in f2["sentence"])
        leg("L20 the sheet's table marks the unguarded section in bold rather than leaving it blank",
            "**没有**" in "\n".join(ticket_lines(f2)))
        real = leg_names()
        leg("L21 every alias points at a leg that is actually in the chain",
            (not real) or all(l in real for ls in LEG_ALIASES.values() for l in ls))
        leg("L22 an aliased section is attributed to its real producer, not to nothing",
            (not real) or ("etf_book_leg_attribution" in
                           (section_bars({"priced_bar": "2026-11-10",
                                          "leg_split": {"evidence_cutoff": "2026-10-30",
                                                        "artifact": "results/etf_book_legs/latest.json"}},
                                         legs=real)["off_headline"][0]["guarded_by"] or [])))
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass

    # a real page on disk, when there is one: the face must agree with its own JSON
    md, js = _paths()
    if js and os.path.exists(js):
        with open(js, encoding="utf-8") as fh:
            real = json.load(fh)
        sbr = section_bars(real)
        leg("L13 on the page on disk every dated section is accounted for",
            sbr["n_sections"] + len(sbr["unknown_sections"]) ==
            sum(1 for k, v in real.items()
                if isinstance(v, dict) and k not in ("page_computed",)))
        leg("L14 the published verdict names the headline the page itself declares",
            sbr["headline_bar"] == headline_bar(real)[0])
    else:
        leg("L13 no page on disk: boundary stated, nothing claimed", True)
        leg("L14 no page on disk: boundary stated, nothing claimed", True)

    # ---- r1623: a page-computed section is not an unproduced one -----------------------
    pc_fx = {"priced_bar": "2026-11-12",
             "cash_yield": {"rate_date": "2026-11-11"},
             "cash_money": {"spot_date": "2026-11-11"},
             "lookahead": {"evidence_cutoff": "2026-10-30"},
             "page_computed": {"cash_yield": {"panel": "data/repo_daily/GC001.csv",
                                              "panel_last_bar": "2026-11-11",
                                              "owner_lane": "update_repo.py / bm-a"},
                               "cash_money": {"panel": "data/repo_daily/GC001.csv",
                                              "panel_last_bar": "2026-11-11",
                                              "owner_lane": "update_repo.py / bm-a"}}}
    psb = section_bars(pc_fx, legs=LEGS_FAKE)
    leg("L25 a section the page recomputes itself is not counted as having no producer",
        psb["page_computed"] == ["cash_money", "cash_yield"]
        and psb["no_writer"] == ["lookahead"]
        and "data/repo_daily/GC001.csv" in (psb["page_computed_panels"] or [""])[0])
    leg("L26 the provenance face is not itself a dated section",
        "page_computed" not in psb["unknown_sections"]
        and psb["n_sections"] + len(psb["unknown_sections"]) ==
        sum(1 for v in pc_fx.values() if isinstance(v, dict)) - 1)
    stale_pc = {"priced_bar": "2026-11-12", "cash_yield": {"rate_date": "2026-11-11"},
                "page_computed": {"cash_yield": {"panel": "p",
                                                 "panel_last_bar": "2026-11-12"}}}
    s2 = section_bars(stale_pc, legs=LEGS_FAKE)
    leg("L27 a page-computed section whose panel moved past it is a real debt",
        s2["page_computed"] == ["cash_yield"] and s2["page_computed_on_panel_tail"] == [])
    tmp2 = os.path.join(ROOT, "results", "_tmp_section_bars_pc.json")
    with open(tmp2, "w", encoding="utf-8") as fh:
        json.dump(pc_fx, fh)
    try:
        f3 = assess(jsonp=tmp2, legs=LEGS_FAKE)
        leg("L28 the sentence blames the panel that stopped, not a re-run nobody did",
            "不是没人重跑这节" in f3["sentence"] and "lookahead" in f3["sentence"])
        leg("L29 the sheet names the panel and its last bar for such a section",
            "页内重算（data/repo_daily/GC001.csv 末行 2026-11-11）" in "\n".join(ticket_lines(f3)))
    finally:
        try:
            os.unlink(tmp2)
        except OSError:
            pass

    # ---- r1627: "a leg mentions it" is not "a leg can move it" ---------------------------
    eng_fx = {"priced_bar": "2026-11-12",
              "cost_tape": {"evidence_cutoff": "2026-11-06",
                            "pricing": {"mode": "engine", "reprices_bar": False}},
              "dual": {"evidence_cutoff": "2026-11-05",
                       "artifact": "results/etf_book_leg_attribution.json"}}
    engb = section_bars(eng_fx, legs=LEGS_FAKE)
    leg("L30 a section priced by an engine behind a non-repricing leg is its own bucket",
        engb["engine_priced"] == ["cost_tape"] and engb["n_engine_priced"] == 1
        and [r["guarded_by"] for r in engb["off_headline"] if r["key"] == "cost_tape"]
        == [["etf_book_cost_tape"]])
    leg("L31 a guarded section that declares nothing is not counted as engine-priced",
        "dual" not in (engb["engine_priced"] or []))
    tmp3 = os.path.join(ROOT, "results", "_tmp_section_bars_engine.json")
    with open(tmp3, "w", encoding="utf-8") as fh:
        json.dump(eng_fx, fh)
    try:
        f4 = assess(jsonp=tmp3, legs=LEGS_FAKE)
        leg("L32 the sentence calls it data debt and does not say the page is blameless",
            "数据债" in f4["sentence"] and "cost_tape" in f4["sentence"]
            and "不是页面的错" not in f4["sentence"])
    finally:
        try:
            os.unlink(tmp3)
        except OSError:
            pass

    # ---- r1628: a window that ends here is not a bar that stopped here -------------------
    wb_fx = {"priced_bar": "2026-11-12",
             "sample_window": {"evidence_cutoff": "2026-10-26",
                               "window": ["2015-01-01", "2019-12-31"],
                               "page_window": ["2020-01-01", "2026-10-26"],
                               "artifact": "results/etf_book_spanning_pre2020.json"},
             "cost_tape": {"evidence_cutoff": "2026-10-30",
                           "artifact": "results/etf_book_cost_tape.json"}}
    wbb = section_bars(wb_fx, legs=LEGS_FAKE)
    leg("L33 a section whose own window ends on the date it states is window-bound, by name",
        wbb["window_bound"] == ["sample_window"] and wbb["n_window_bound"] == 1)
    leg("L34 the named worst lag is not the window-bound section (its lag cannot shrink by re-running a leg)",
        [r["key"] for r in wbb["off_headline"] if r["window_bound"]] == ["sample_window"])
    tmp4 = os.path.join(ROOT, "results", "_tmp_section_bars_window.json")
    with open(tmp4, "w", encoding="utf-8") as fh:
        json.dump(wb_fx, fh)
    try:
        f5 = assess(jsonp=tmp4, legs=LEGS_FAKE)
        leg("L35 the sentence names the window and does not call it the worst lag",
            "最差 cost_tape" in f5["sentence"] and "最差 sample_window" not in f5["sentence"]
            and "sample_window（2020-01-01 至 2026-10-26）" in f5["sentence"])
        leg("L36 the sheet prints the window, not a leg name, for that row",
            "窗口段（2020-01-01 至 2026-10-26）" in "\n".join(ticket_lines(f5)))
    finally:
        try:
            os.unlink(tmp4)
        except OSError:
            pass
    # form check, not name trust: a published window that does NOT end on the stated bar is
    # an ordinary lag and must stay one (the field name alone buys nothing).
    near = {"priced_bar": "2026-11-12",
            "x": {"evidence_cutoff": "2026-11-01", "window": ["2020-01-01", "2026-10-30"]}}
    leg("L37 a window ending somewhere else does not make its section window-bound",
        section_bars(near, legs=LEGS_FAKE)["n_window_bound"] == 0)

    # ---- r1617: a section that says which day it prices is not "undatable" ---------------
    leg("L23 a date under another name is read, and a boolean that merely looks like one is not",
        bar_of({"rate_date": "2026-11-11"})[0] == "2026-11-11"
        and bar_of({"same_decision_bar": "True"})[0] is None
        and bar_of({"asof": "None", "repo_rate_date": "2026-11-11"})[0] == "2026-11-11")
    leg("L24 the next rebalance date is never read as the bar a section is priced on",
        bar_of({"decision_date": "2026-12-09", "k_order": 0.39})[0] is None)

    # r1533: `sum(1 for _, ok in legs)` counts every leg whatever its verdict -- a suite
    # that can print [FAIL] and still exit 0.
    passed = sum(1 for _, ok in legs if ok)
    for name, ok in legs:
        print(("[PASS] " if ok else "[FAIL] ") + name)
    print("%d/%d PASS" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv=None):
    # r1532's trap: a GBK console raising on a CJK glyph turns a green leg into a red one
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "selftest" or args.selftest:
        return selftest()
    if args.cmd == "check" or args.check:
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())
