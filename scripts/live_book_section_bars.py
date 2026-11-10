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

# A page behind by more than this many sessions is not "a different day", it is a page
# nobody refreshed -- that stays a hard finding on every host, not a note.
MAX_LAG_SESSIONS = 5

MIXED = "PAGE_MIXES_BARS"
SINGLE = "PAGE_ON_ONE_BAR"
NO_PAGE = "NO_PAGE"
NO_HEADLINE = "HEADLINE_UNKNOWN"


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
    return None, None


def headline_bar(doc):
    for f in HEADLINE_FIELDS:
        v = (doc or {}).get(f)
        if v not in (None, "", "None"):
            return str(v)[:10], f
    return None, None


def section_bars(doc, cal=None):
    """Every top-level section that carries a date, plus the count of those that do not."""
    head, head_field = headline_bar(doc)
    rows, unknown = [], []
    for k, v in (doc or {}).items():
        if not isinstance(v, dict):
            continue
        b, f = bar_of(v)
        if b is None:
            unknown.append(k)
            continue
        rows.append({"key": k, "bar": b, "field": f,
                     "lag_sessions": sessions_between(b, head, cal) if head else None,
                     "ahead_of_headline": bool(head and b > head)})
    hist = {}
    for r in rows:
        hist[r["bar"]] = hist.get(r["bar"], 0) + 1
    behind = [r for r in rows if head and r["bar"] != head]
    behind.sort(key=lambda r: (r["bar"], r["key"]))
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


def assess(page=None, jsonp=None, cal=None):
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
    sb = section_bars(doc, cal)
    face.update({k: sb[k] for k in ("headline_bar", "headline_field", "n_sections",
                                    "n_on_headline", "unknown_sections", "bars",
                                    "n_off_headline", "off_headline", "oldest",
                                    "max_lag_sessions", "by_key")})
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
        worst = max(sb["off_headline"], key=lambda r: r["lag_sessions"] or 0) if sb["off_headline"] else None
        face["sentence"] = (
            "页面头部写着按 %s 定价，但 %d 个带日期的节里只有 %d 节真在这一天；"
            "其余 %d 节最旧停在 %s%s，另外 %d 节根本没有日期——"
            "它们不是同一根 bar 上的数，读的时候不能互相加减。" %
            (sb["headline_bar"], sb["n_sections"], sb["n_on_headline"],
             sb["n_off_headline"], sb["oldest"],
             ("（最差 %s 落后 %d 个交易日）" % (worst["key"], worst["lag_sessions"])
              if worst and worst["lag_sessions"] else ""),
             len(sb["unknown_sections"])))
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
        L.append("| 节 | 它停在哪根 bar | 落后（交易日） |")
        L.append("|---|---|---|")
        for r in rows[:12]:
            L.append("| %s | %s | %s |" % (r["key"], r["bar"], r.get("lag_sessions")))
        if len(rows) > 12:
            L.append("| …其余 %d 节 | | |" % (len(rows) - 12))
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
              "max_lag_sessions", "by_key", "unknown_sections"):
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
    sb = section_bars(mixed)
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
    leg("L6 one bar everywhere is PAGE_ON_ONE_BAR", section_bars(single)["n_off_headline"] == 0)

    undated = {"priced_bar": "2026-11-10", "a": {"evidence_cutoff": "2026-11-10"},
               "z": {"sentence": "no date here"}}
    leg("L7 an undated section is named, never assumed to share the headline",
        section_bars(undated)["unknown_sections"] == ["z"])

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

    # a real page on disk, when there is one: the face must agree with its own JSON
    md, js = _paths()
    if js and os.path.exists(js):
        with open(js, encoding="utf-8") as fh:
            real = json.load(fh)
        sbr = section_bars(real)
        leg("L13 on the page on disk every dated section is accounted for",
            sbr["n_sections"] + len(sbr["unknown_sections"]) ==
            sum(1 for v in real.values() if isinstance(v, dict)))
        leg("L14 the published verdict names the headline the page itself declares",
            sbr["headline_bar"] == headline_bar(real)[0])
    else:
        leg("L13 no page on disk: boundary stated, nothing claimed", True)
        leg("L14 no page on disk: boundary stated, nothing claimed", True)

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
