"""The page names a day in words ("今天") while the section beside it was priced on another bar.

r1663..r1667 repaired this defect five times by hand (quote, do-or-wait, fill, premium,
sibling gap) and every one of those repairs was found by eye, after the CEO had already read
the sentence. r1667 built the first half of the answer: `etf_book_ceo_page.page_day_debt_guard`
reads the page module's SOURCE and asks which block still says 今天 without being handed a
day. That guard cannot see the other half -- a block that was handed a day still emits today's
words about the bar it priced, and the sentence only exists once the page is written.

So this face reads the page through its own pointer and asks the reader's question twice, because
the two answers come from different papers (r1668):

  * the STRUCTURED face (`docs/live_book/LIVE-BOOK-*.json`) supplies the per-section bar, so a
    today-word that lives in the structured strings can be anchored;
  * the PRINTED face (`docs/live_book/LIVE-BOOK-*.md`, the file a reader opens) is where most
    today-words actually appear: `render_md` composes those sentences from code literals, so the
    JSON holds none of them. Reading only the JSON reported "0 day words" over a page that
    printed 24 -- a clean verdict over the wrong paper (E240 family: measured a face the words
    never live on).

The printed face is counted, never silently skipped: if it cannot be read the verdict says so,
and if it carries today-words that the structured face cannot anchor, the verdict is
PRINTED_BUT_UNANCHORED -- not NO_DAY_WORDS, whose sentence would have said the page uses none.

Three answers, and they are not interchangeable:

  * ANCHORED           -- every today-word sits in a section the page priced on its own day;
  * DAY_WORD_ON_ANOTHER_DAY -- at least one does not (the r1664 family, still on the paper);
  * DAY_WORD_WITHOUT_A_BAR  -- the section carries no day of its own, so the word cannot be
                          checked at all. This is NOT clean: "I could not verify" never reads
                          as "it is fine" (r98/r1159).
  * NO_DAY_WORDS      -- neither paper uses such a word. Printed as its own verdict so an
                          empty bucket never borrows the sentence of a verified one.
  * PRINTED_BUT_UNANCHORED -- the structured face carries no today-word, but the printed page
                          does, so nothing here can say which day those sentences mean.
  * UNVERIFIED_PRINTED_FACE -- the printed page could not be read at all. "Could not check" is
                          never reported as clean (r98/r1159).

Scope, stated instead of implied (E76 family): only the today-words 今天/今日/今晚 are
guarded, because those are the words that lie about the reader's own day. 昨天/上周/本周 name a
day explicitly and are out of scope here -- a face that quietly claimed them would be a
different check, and this docstring is where that claim would have to be made.

Exit codes: 0 anchored or no today-words, 1 a today-word sits on another day, 2 the artifact
cannot be read (no page, no pointer, unreadable JSON).

Usage:
    python scripts/live_book_day_words.py run
    python scripts/live_book_day_words.py check
    python scripts/live_book_day_words.py --selftest
"""
from __future__ import annotations

import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

DAY_WORDS = ("今天", "今日", "今晚")
# A line that carries its own date tells the reader which day it means (r1669).
DATE_IN_TEXT = re.compile(r"20\d{2}-\d{2}-\d{2}")

_D = r"(20\d{2}-\d{2}-\d{2})"
# r1671: a printed date is a claim until it is read against the face that issued it. Each rule
# anchors one sentence pattern from the page to the page's own date field, so "the sentence
# says 2026-11-13" becomes "the sentence says 2026-11-13 AND the premium face is priced on
# 2026-11-13". A date that no rule claims is reported as unmapped, never counted as checked.
CLAIM_RULES = [
    (re.compile(r"^# 今日 ETF 实盘单 —— " + _D), ["generated_for_date"]),
    (re.compile(r"上一次定稿 \*\*" + _D + r"\*\*"), ["book_decided_at"]),
    (re.compile(r"按新的收盘价（\*\*" + _D + r"\*\*）"), ["priced_bar"]),
    (re.compile(r"下一个动手日是 \*\*" + _D + r"\*\*"), ["next_rebalance_date"]),
    (re.compile(r"按 \*\*" + _D + r"\*\* 的读数"), ["premium_forward.face_asof"]),
    (re.compile(r"账只记到 " + _D), ["positions.ledger_bar"]),
    (re.compile(r"（" + _D + r" 报价）"), ["cash_yield.rate_date"]),
    (re.compile(r"重放回 " + _D + "~" + _D), ["stress.first", "stress.last"]),
    (re.compile(r"已经吃到 \*\*" + _D + r"\*\* 的收盘"), ["priced_bar"]),
    (re.compile(r"（bar " + _D + r"）"), ["priced_bar"]),
    (re.compile(r"本页是 \*\*" + _D + r"\*\* 的页面"), ["generated_for_date"]),
    (re.compile(r"价格和数据都停在 \*\*" + _D + r"\*\*"), ["priced_bar"]),
]


def _doc_value(doc, path):
    v = doc
    for k in str(path).split("."):
        idx = re.match(r"^(.*?)\[(\d+)\]$", k)
        if idx:
            k, i = idx.group(1), int(idx.group(2))
        else:
            i = None
        if k:
            if not isinstance(v, dict):
                return None
            v = v.get(k)
        if i is not None:
            if not isinstance(v, (list, tuple)) or i >= len(v):
                return None
            v = v[i]
    return v


def _date_claims(rows, doc, rules=None):
    """Read every printed date against the field its sentence quotes.

    Three readings, and only one of them is green: `ok` (the sentence's date is the one the
    field carries), `mismatch` (the sentence names a day the field does not -- named with both
    dates), `unverifiable` (the field is missing, so nothing here can say the date is right).
    A date no rule claims is `unmapped`: the face does not know which paper that sentence
    quotes, and it says so rather than counting it as checked (r1471 family: reading a face
    is not the same as having a writer for it).
    """
    rules = CLAIM_RULES if rules is None else rules
    claims, mismatches, unmapped = [], [], []
    n_ok = n_unverif = 0
    for row in rows or []:
        line = row.get("line") or ""
        covered = []
        for pat, paths in rules:
            for m in pat.finditer(line):
                for gi, path in enumerate(paths, start=1):
                    date = m.group(gi)
                    covered.append(m.span(gi))
                    val = _doc_value(doc, path)
                    exp = str(val)[:10] if isinstance(val, str) else None
                    rec = {"heading": row.get("heading"), "date": date, "field": path,
                           "expected": exp, "line": line[:140]}
                    if exp is None:
                        rec["reading"] = "unverifiable"
                        n_unverif += 1
                    elif exp == date:
                        rec["reading"] = "ok"
                        n_ok += 1
                    else:
                        rec["reading"] = "mismatch"
                        mismatches.append(rec)
                    claims.append(rec)
        for m in DATE_IN_TEXT.finditer(line):
            if not any(a <= m.start() < b for a, b in covered):
                unmapped.append({"heading": row.get("heading"), "date": m.group(0),
                                 "line": line[:140]})
    return {"n_claims": len(claims), "n_ok": n_ok, "n_mismatch": len(mismatches),
            "n_unverifiable": n_unverif, "n_unmapped": len(unmapped),
            "n_rules": len(rules), "claims": claims[:40],
            "mismatches": mismatches[:20], "unmapped": unmapped[:20]}
FACE = os.path.join(ROOT, "results", "live_book_day_words.json")
POINTER = os.path.join(ROOT, "docs", "live_book", "latest.json")


def _bars():
    try:
        from scripts import live_book_section_bars as SB
    except Exception:
        import live_book_section_bars as SB
    return SB


def _walk(v, path=""):
    """Every string inside a section, with the path it sits at."""
    if isinstance(v, str):
        yield path or "/", v
    elif isinstance(v, dict):
        for k, kv in v.items():
            yield from _walk(kv, path + "/" + str(k))
    elif isinstance(v, (list, tuple)):
        for i, kv in enumerate(v):
            yield from _walk(kv, path + "[%d]" % i)


def _hits(section):
    out = []
    for path, s in _walk(section):
        for w in DAY_WORDS:
            if w in s:
                out.append({"path": path, "word": w, "text": s})
                break
    return out


def _printed_census(text):
    """Day-word lines on the paper a reader opens, grouped by the heading they sit under.

    r1669: "there are 20 such lines and nobody can date them" was the whole finding, and it
    left the reader with nothing to act on. The paper itself already distinguishes two
    cases: a line that names a date beside its today-word ("今天的 1.26%（2026-11-13 报价）",
    "今天没有新 bar，账只记到 2026-11-13") tells the reader which day it means; a line that
    does not ("| 今日报价 |" on a morning when the quote column is Friday's close) does not.
    The first is still not *anchored* -- nothing here can check the date is the right one --
    but it is self-dating, and the second is the debt. Splitting the two is what makes the
    count actionable, so each row carries `self_dated` and the undated ones are named.
    """
    rows = []
    heading = "(页首)"
    for line in (text or "").split("\n"):
        if line.startswith("## "):
            heading = line[3:].strip()[:46]
        if any(w in line for w in DAY_WORDS):
            shown = line.strip()[:180]
            rows.append({"heading": heading, "line": shown,
                         "self_dated": bool(DATE_IN_TEXT.search(shown))})
    heads = []
    for r in rows:
        if r["heading"] not in heads:
            heads.append(r["heading"])
    undated = [r for r in rows if not r["self_dated"]]
    return {"state": "ok", "n_lines": len(rows), "n_headings": len(heads),
            "n_self_dated": len(rows) - len(undated), "n_undated": len(undated),
            "undated": undated[:40],
            "headings": heads[:12], "rows": rows[:40]}


_UNMEASURED = object()


def census(doc, artifact=None, printed=_UNMEASURED):
    """The reader's-day audit over one page: its structured face, and the paper it prints.

    Unknown is a third verdict, not a zero: a section with a today-word and no bar of its
    own is reported, and a page that names no day at all can only be judged against the
    headline bar it does carry.

    `printed` defaults to the not-measured sentinel so the fixtures below keep testing the
    structured half alone; `run()` always passes the rendered page (text, or None when it
    could not be read). A caller that leaves it out is not claiming the page is clean.
    """
    ret = {"artifact": artifact, "page_day": None, "headline_bar": None,
           "n_sections": 0, "n_with_day_word": 0, "n_anchored": 0,
           "offenders": [], "n_unverifiable": 0, "unverifiable": [],
           "rows": [], "verdict": "UNREADABLE", "sentence": ""}
    if printed is _UNMEASURED:
        ret["printed"] = {"state": "not_measured"}
        ret["date_claims"] = {"state": "not_measured"}
    elif printed is None:
        ret["printed"] = {"state": "unreadable"}
        ret["date_claims"] = {"state": "not_measured"}
    else:
        ret["printed"] = _printed_census(printed)
        ret["date_claims"] = _date_claims(ret["printed"]["rows"],
                                          doc if isinstance(doc, dict) else {})
    if not isinstance(doc, dict) or not doc:
        ret["sentence"] = "页面件读不出来——这不是「没有日词」，是没法核验。"
        return ret
    SB = _bars()
    try:
        head, head_field = SB.headline_bar(doc)
    except Exception:
        head, head_field = None, None
    page_day = str(doc.get("generated_for_date") or "")[:10] or None
    if page_day is None:
        page_day = str(head or "")[:10] or None
        ret["day_source"] = "headline_bar"
    else:
        ret["day_source"] = "generated_for_date"
    ret["page_day"] = page_day
    ret["headline_bar"] = str(head)[:10] if head else None
    ret["headline_field"] = head_field
    for key, sec in doc.items():
        if key == "page_computed" or not isinstance(sec, dict):
            continue
        ret["n_sections"] += 1
        hits = _hits(sec)
        if not hits:
            continue
        try:
            bar, field = SB.bar_of(sec)
        except Exception:
            bar, field = None, None
        bar = str(bar)[:10] if bar else None
        row = {"key": key, "bar": bar, "field": field, "n": len(hits),
               "words": sorted({h["word"] for h in hits}),
               "paths": sorted({h["path"] for h in hits})[:6]}
        ret["n_with_day_word"] += 1
        if bar is None:
            row["reading"] = "no_bar"
            ret["n_unverifiable"] += 1
            ret["unverifiable"].append(dict(row, sample=[h["text"][:160] for h in hits[:2]]))
        elif page_day and bar != page_day:
            row["reading"] = "another_day"
            ret["offenders"].append(dict(row, sample=[h["text"][:160] for h in hits[:2]]))
        else:
            row["reading"] = "anchored"
            ret["n_anchored"] += 1
        ret["rows"].append(row)
    pr = ret["printed"]
    if ret["offenders"]:
        ret["verdict"] = "DAY_WORD_ON_ANOTHER_DAY"
    elif pr["state"] == "unreadable":
        ret["verdict"] = "UNVERIFIED_PRINTED_FACE"
    elif pr["state"] == "ok" and pr["n_lines"] and not ret["n_with_day_word"]:
        # r1670: "N printed lines say 今天 and the reader cannot date them" and "every printed
        # line carries its own date" are two different debts, and both stay red -- nothing in
        # this face checks that a printed date is the RIGHT date. Splitting the name is what
        # lets the reader tell "still owed" from "paid, not yet audited".
        # r1671: the audit is what this branch now also carries. A printed date that names a
        # day its own field does not is a mismatch and is named with both dates; a date no
        # rule claims, or one whose field is missing, keeps the page on the self-dated name --
        # "I could not check it" never graduates to green.
        dc = ret["date_claims"]
        if dc.get("n_mismatch"):
            ret["verdict"] = "PRINTED_DATE_MISMATCH"
        elif (dc.get("n_claims") and not dc.get("n_unmapped") and not pr.get("n_undated")
              and not dc.get("n_unverifiable") and dc.get("n_ok") == dc.get("n_claims")):
            ret["verdict"] = "PRINTED_DATES_AGREE"
        elif pr.get("n_undated") == 0 and pr.get("n_self_dated"):
            ret["verdict"] = "PRINTED_SELF_DATED"
        else:
            ret["verdict"] = "PRINTED_BUT_UNANCHORED"
    elif ret["n_unverifiable"]:
        ret["verdict"] = "DAY_WORD_WITHOUT_A_BAR"
    elif not ret["n_with_day_word"] and pr["state"] == "ok" and not pr["n_lines"]:
        ret["verdict"] = "NO_DAY_WORDS"
    elif not ret["n_with_day_word"]:
        ret["verdict"] = "NO_DAY_WORDS"
    else:
        ret["verdict"] = "ANCHORED"
    ret["sentence"] = sentence(ret)
    return ret


def sentence(c):
    """One line for the page. An empty bucket never borrows the wording of a checked one."""
    if c["verdict"] == "UNREADABLE":
        return c["sentence"]
    pr = c.get("printed") or {"state": "not_measured"}
    dc = c.get("date_claims") or {}
    if c["verdict"] == "PRINTED_DATE_MISMATCH":
        named = "；".join("「%s」里写 `%s`，而 %s 是 `%s`"
                         % (r["heading"], r["date"], r["field"], r["expected"])
                         for r in dc.get("mismatches") or [])
        return ("**页面自己用的「今天/今日」有 %d 行；其中 %d 处日期与它引用的那张面对不上**：%s。"
                "（共核过 %d 处，%d 处对得上，%d 处判不了。）"
                % (pr["n_lines"], dc.get("n_mismatch", 0), named,
                   dc.get("n_claims", 0), dc.get("n_ok", 0), dc.get("n_unverifiable", 0)))
    if c["verdict"] == "PRINTED_DATES_AGREE":
        return ("**页面自己用的「今天/今日」有 %d 行，%d 处日期逐句对上了它引用的那张面**"
                "（%d 条规则，0 处无规则可核，0 处判不了；结构面里 %d 节，日词 0 节）。"
                "这一面核的是「句子写的日子 == 那个字段写的日子」，不核那个字段本身对不对。"
                % (pr["n_lines"], dc.get("n_claims", 0), dc.get("n_rules", 0), c["n_sections"]))
    if c["verdict"] == "PRINTED_SELF_DATED":
        return ("**页面自己用的「今天/今日」有 %d 行，坐在 %d 个小节里；每一行都自带日期**"
                "（结构面里 %d 节，日词 0 节）。这一面核了 %d 处日期：%d 处对上它所引用的字段，"
                "**%d 处判不了（字段缺）**，**%d 处没有规则可核**——判不了的不算对上。"
                % (pr["n_lines"], pr["n_headings"], c["n_sections"], dc.get("n_claims", 0),
                   dc.get("n_ok", 0), dc.get("n_unverifiable", 0), dc.get("n_unmapped", 0)))
    if c["verdict"] == "PRINTED_BUT_UNANCHORED":
        _u = pr.get("undated") or []
        _split = ("其中 **%d 行自己带了日期**（读者读得出它算哪一天），**%d 行没有**"
                  % (pr.get("n_self_dated", 0), pr.get("n_undated", 0)))
        if _u:
            _split += "——没有的那几行是：%s%s" % (
                "、".join("「%s」里的一句 `%s`" % (r["heading"], r["line"][:40])
                         for r in _u[:4]),
                "…" if len(_u) > 4 else "")
        return ("**页面自己用的「今天/今日」有 %d 行，坐在 %d 个小节里；这一面核不到它们算哪一天**"
                "（结构面里 %d 节，日词 0 节）。%s。自带日期只说明句子诚实，不说明那个日期是对的。"
                "所以这不是「没有日词」，是「有，且没人能给它定日」。"
                % (pr["n_lines"], pr["n_headings"], c["n_sections"], _split))
    if c["verdict"] == "UNVERIFIED_PRINTED_FACE":
        return ("页面件读得出来（%d 节），但**印出来的那张纸读不到**——"
                "「没核到」不是「没有」。"
                % c["n_sections"])
    if c["verdict"] == "NO_DAY_WORDS":
        return ("页面这一版没有用「今天/今日/今晚」这类词（结构面 %d 节、印出来的纸上 0 行），"
                "因此没有可核验的日词——这既不是「全部对上了」，也不欠什么。"
                % c["n_sections"])
    head = "页面自称 %s，%d 个节里 %d 节用了日词" % (c.get("page_day") or "?",
                                                   c["n_sections"], c["n_with_day_word"])
    if c["verdict"] == "ANCHORED":
        return ("%s：全部 %d 节的日词都落在页面自己那天上。"
                % (head, c["n_anchored"]))
    if c["verdict"] == "DAY_WORD_WITHOUT_A_BAR":
        keys = "、".join("%s" % r["key"] for r in c["unverifiable"])
        return ("%s：其中 %d 节（%s）拿不到自己的日子，日词无从核验——"
                "「核不了」不是「对上了」。" % (head, c["n_unverifiable"], keys))
    parts = ["%s 定价在 %s" % (r["key"], r["bar"]) for r in c["offenders"]]
    return ("%s：**%d 节的日词坐在别的日子上**（%s）——读者星期日打开这张纸，"
            "句子里说的「今天」是星期五。" % (head, len(c["offenders"]), "；".join(parts)))


def _read(pointer=POINTER):
    """(doc, artifact, printed_text, error). Reads the page through its own pointer, never a guess.

    The printed text is None (not "") when the markdown cannot be read: an absent paper is a
    reading of its own, and `census` reports it as unverifiable rather than as zero day-words.
    """
    try:
        with open(pointer, "r", encoding="utf-8") as fh:
            ptr = json.load(fh) or {}
    except (OSError, ValueError) as exc:
        return None, None, None, "%s: %s" % (type(exc).__name__, exc)
    rel = ptr.get("json") or ""
    if not rel:
        return None, None, None, "pointer names no json file"
    path = os.path.join(ROOT, rel)
    printed = None
    md_rel = ptr.get("page") or ""
    if md_rel:
        try:
            with open(os.path.join(ROOT, md_rel), "r", encoding="utf-8") as fh:
                printed = fh.read()
        except (OSError, ValueError):
            printed = None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return (json.load(fh) or {}), rel, printed, None
    except (OSError, ValueError) as exc:
        return None, rel, printed, "%s: %s" % (type(exc).__name__, exc)


CLEAN = ("ANCHORED", "NO_DAY_WORDS", "PRINTED_DATES_AGREE")


def run():
    doc, rel, printed, err = _read()
    if err:
        print("LIVE_BOOK_DAY_WORDS_UNREADABLE %s" % err)
        return 2
    c = census(doc, artifact=rel, printed=printed)
    c["script"] = "live_book_day_words"
    c["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    os.makedirs(os.path.dirname(FACE), exist_ok=True)
    with open(FACE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(c, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("%s | %s" % (c["verdict"], c["sentence"]))
    return 0 if c["verdict"] in CLEAN else 1


def check():
    doc, rel, printed, err = _read()
    if err:
        print("CHECK_UNREADABLE %s" % err)
        return 2
    c = census(doc, artifact=rel, printed=printed)
    pr = c.get("printed") or {}
    print("verdict %s | page %s | sections %d | day-word sections %d | anchored %d | "
          "offenders %d | unverifiable %d | printed %s %s lines / %s headings "
          "(self-dated %s / undated %s)"
          % (c["verdict"], c.get("page_day") or "?", c["n_sections"],
             c["n_with_day_word"], c["n_anchored"], len(c["offenders"]),
             c["n_unverifiable"], pr.get("state"),
             pr.get("n_lines", "-"), pr.get("n_headings", "-"),
             pr.get("n_self_dated", "-"), pr.get("n_undated", "-")))
    print(c["sentence"])
    dc = c.get("date_claims") or {}
    print("  DATES claims %s | ok %s | mismatch %s | unverifiable %s | unmapped %s | rules %s"
          % (dc.get("n_claims", "-"), dc.get("n_ok", "-"), dc.get("n_mismatch", "-"),
             dc.get("n_unverifiable", "-"), dc.get("n_unmapped", "-"), dc.get("n_rules", "-")))
    for r in dc.get("mismatches") or []:
        print("  DATE-MISMATCH %s | printed %s | %s = %s"
              % (r["heading"], r["date"], r["field"], r["expected"]))
    for r in dc.get("unmapped") or []:
        print("  DATE-UNMAPPED %s | %s | %s" % (r["heading"], r["date"], r["line"][:80]))
    for h in (pr.get("headings") or []):
        print("  PRINTED-UNDER %s" % h)
    for r in (pr.get("undated") or []):
        print("  UNDATED %s | %s" % (r["heading"], r["line"]))
    for r in c["offenders"]:
        print("  OFFENDER %s bar=%s words=%s" % (r["key"], r["bar"], ",".join(r["words"])))
        for s in r.get("sample") or []:
            print("    %s" % s)
    return 0 if c["verdict"] in CLEAN else 1


def selftest():
    total = ok = 0

    def leg(name, cond, detail=""):
        nonlocal total, ok
        total += 1
        ok += 1 if cond else 0
        print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                            ("" if cond else " | " + str(detail)[:400])))

    same = {"generated_for_date": "2026-11-13",
            "quote": {"evidence_cutoff": "2026-11-13",
                      "line": "今天的报价就在它自己的均值上"}}
    c = census(same, artifact="fixture/same.json")
    leg("same-day today-word reads as anchored", c["verdict"] == "ANCHORED"
        and c["n_anchored"] == 1 and not c["offenders"], c)

    stale = {"generated_for_date": "2026-11-14",
             "quote": {"evidence_cutoff": "2026-11-13",
                       "line": "今天的报价就在它自己的均值上"}}
    c = census(stale, artifact="fixture/stale.json")
    leg("a Saturday page printing Friday's bar as 今天 is an offender",
        c["verdict"] == "DAY_WORD_ON_ANOTHER_DAY" and len(c["offenders"]) == 1
        and c["offenders"][0]["key"] == "quote" and c["offenders"][0]["bar"] == "2026-11-13"
        and "2026-11-13" in c["sentence"], c)

    deep = {"generated_for_date": "2026-11-14",
            "stress": {"priced_bar": "2026-11-12",
                       "rows": [{"note": "今天的权重原封不动"}]}}
    c = census(deep, artifact="fixture/deep.json")
    leg("a today-word nested in a list is still found",
        len(c["offenders"]) == 1 and c["offenders"][0]["bar"] == "2026-11-12"
        and "/rows[0]/note" in (c["offenders"][0].get("paths") or []), c["offenders"])

    nobar = {"generated_for_date": "2026-11-14", "misc": {"line": "今天没有新 bar"}}
    c = census(nobar, artifact="fixture/nobar.json")
    leg("a today-word in a section with no date is unverifiable, never clean",
        c["verdict"] == "DAY_WORD_WITHOUT_A_BAR" and c["n_unverifiable"] == 1
        and not c["offenders"] and "核不了" in c["sentence"], c)

    clean = {"generated_for_date": "2026-11-14",
             "quote": {"evidence_cutoff": "2026-11-14", "line": "报价 1.26%"}}
    c = census(clean, artifact="fixture/clean.json")
    leg("no day words is its own verdict and does not claim everything matched",
        c["verdict"] == "NO_DAY_WORDS" and "不是「全部对上了」" in c["sentence"], c)

    c = census(None, artifact="fixture/missing.json")
    leg("an unreadable artifact is rc2, not a clean page", c["verdict"] == "UNREADABLE"
        and c["n_sections"] == 0, c)

    nopage = {"headline_bar": "2026-11-13", "quote": {"asof": "2026-11-13",
                                                     "line": "今天的报价"}}
    c = census(nopage, artifact="fixture/nopage.json")
    leg("a page with no reader day falls back to its headline bar and says so",
        c["verdict"] == "ANCHORED" and c["day_source"] == "headline_bar", c)

    # Conflicting evidence: the same section shows two days -> bar_of picks one, so the
    # census must at least not report the section as clean by accident.
    two = {"generated_for_date": "2026-11-14",
           "quote": {"evidence_cutoff": "2026-11-13", "asof": "2026-11-14",
                     "line": "今天的报价"}}
    c = census(two, artifact="fixture/two.json")
    leg("a section carrying two days is reported, not silently anchored",
        c["n_with_day_word"] == 1 and c["rows"][0]["reading"] in ("anchored", "another_day")
        and bool(c["rows"][0]["bar"]), c["rows"])

    # r1668: the two papers. The structured face carries no today-word when the sentence is
    # composed by the renderer, so a census that only reads it reports a clean page over a
    # page that prints 今天. Each of these three legs pins one of the ways that can go wrong.
    printed = ("# 今日 ETF 实盘单 —— 2026-11-14\n\n## 一句话\n\n**今天不用动手。**\n\n"
               "## 现金腿\n\n| 代码 | 今日报价 |\n")
    c = census(clean, artifact="fixture/clean.json", printed=printed)
    leg("a clean structured face over a printed page that says 今天 is not NO_DAY_WORDS",
        c["verdict"] == "PRINTED_BUT_UNANCHORED" and c["printed"]["n_lines"] == 3
        and c["printed"]["n_headings"] == 3 and "核不到" in c["sentence"], c)

    c = census(clean, artifact="fixture/clean.json", printed="# ETF 实盘单\n\n## 报价\n\n1.26%\n")
    leg("only when the printed page also has none does NO_DAY_WORDS stand",
        c["verdict"] == "NO_DAY_WORDS" and c["printed"]["n_lines"] == 0
        and "结构面 1 节" in c["sentence"], c)

    c = census(clean, artifact="fixture/clean.json", printed=None)
    leg("a printed page that cannot be read is unverifiable, never clean",
        c["verdict"] == "UNVERIFIED_PRINTED_FACE" and "没核到" in c["sentence"], c)

    c = census(clean, artifact="fixture/clean.json")
    leg("a caller that never measured the printed page is not claiming it is clean",
        c["verdict"] == "NO_DAY_WORDS" and c["printed"]["state"] == "not_measured", c)

    # r1669: "20 lines, nobody can date them" was the whole finding and it left the reader
    # nothing to act on. The paper already splits those lines in two -- one kind names a date
    # beside its today-word, the other does not -- and only the second kind is the debt. Each
    # leg below pins one half of that split, so a future edit that turns it back into a
    # single total fails here instead of quietly losing the distinction.
    _p = ("# 今日 ETF 实盘单 —— 2026-11-14\n\n"
          "## 一句话\n\n**今天不用动手。**\n\n"
          "## 下单清单（要是你现在才建仓）\n\n"
          "| 代码 | 期限 | 今日报价 |\n\n"
          "- 现金腿利息：**今天没有新 bar，账只记到 2026-11-13**。\n")
    c = census(clean, artifact="fixture/clean.json", printed=_p)
    _pr = c["printed"]
    leg("a printed today-word with no date beside it is named, with the heading it sits under",
        _pr["n_undated"] == 2
        and {r["heading"] for r in _pr["undated"]} == {"一句话", "下单清单（要是你现在才建仓）"}
        and "今天不用动手" in c["sentence"], _pr)
    # r1670: the heading itself stopped borrowing 今天 for a hypothetical. The table row under
    # it still carries 今日报价 (that is a real quote column, and the cash-ladder header dates
    # it), so the split is judged per line, not per section.
    leg("a hypothetical heading does not borrow the day word (the row under it still may)",
        not any("如果你今天才建仓" in r["heading"] for r in _pr["rows"]), _pr)
    leg("a printed today-word that carries its own date is not counted as debt",
        _pr["n_self_dated"] == 2
        and not any(DATE_IN_TEXT.search(r["line"]) for r in _pr["undated"]), _pr)
    leg("the two buckets add up to the day-word lines (no line disappears in the split)",
        _pr["n_self_dated"] + _pr["n_undated"] == _pr["n_lines"] == 4, _pr)
    # r1670: "N lines nobody can date" and "every line dates itself" both stay red here --
    # nothing checks that a printed date is the right one -- so the name has to say which
    # debt the page owes, or the reader cannot see that 7 lines became 0.
    _p_all_dated = ("# 今日 ETF 实盘单 —— 2026-11-14\n\n"
                    "## 一句话\n\n**今天没有新 bar，账只记到 2026-11-13。**\n")
    _c_self = census(clean, artifact="fixture/clean.json", printed=_p_all_dated)
    _c_owed = census(clean, artifact="fixture/clean.json", printed=_p)
    leg("a paper whose every day word dates itself is a different debt from one that does not",
        _c_self["verdict"] == "PRINTED_SELF_DATED"
        and _c_owed["verdict"] == "PRINTED_BUT_UNANCHORED",
        (_c_self["verdict"], _c_owed["verdict"]))
    leg("the self-dated verdict still refuses to claim the dates were checked",
        "判不了的不算对上" in _c_self["sentence"], _c_self["sentence"][:80])
    leg("one undated line is enough to fall back to the owed name",
        census(clean, artifact="fixture/clean.json",
               printed=_p_all_dated + "\n**今天不用动手。**\n")["verdict"]
        == "PRINTED_BUT_UNANCHORED", "")
    leg("a date on the paper is read as a date and not as a day-word verdict",
        _pr["rows"][0]["self_dated"] is True
        and _pr["rows"][0]["heading"] == "(页首)", _pr["rows"][0])

    # r1671: "every line dates itself" was still an un-audited claim -- nothing read the date
    # against the face the sentence quotes. These legs pin each way that audit can go wrong,
    # plus a table leg that fails if a rule is ever added without a sample of its own language.
    _samples = [
        ("# 今日 ETF 实盘单 —— 2026-11-14", 1),
        ("上一次定稿 **2026-11-11**，今天只是重新算份额", 1),
        ("今天只是按新的收盘价（**2026-11-13**）算", 1),
        ("下一个动手日是 **2026-12-09**", 1),
        ("按 **2026-11-13** 的读数，这张单里可核验的 5 只票", 1),
        ("现金腿利息：今天没有新 bar，账只记到 2026-11-13。", 1),
        ("| 若一直只有今天的 1.26%（2026-11-13 报价） |", 1),
        ("把今天这 5 只票的权重重放回 2005-02-23~2026-11-13 的整段面板", 2),
        ("日线面板自己已经吃到 **2026-11-13** 的收盘", 1),
        ("**今天这张可执行单实际持 5 名**（bar 2026-11-13）", 1),
        ("本页是 **2026-11-14** 的页面", 1),
        ("价格和数据都停在 **2026-11-13**", 1),
    ]
    leg("every date rule has a sample of its own language, and every sample fires one rule",
        len(_samples) == len(CLAIM_RULES)
        and all(pat.search(s) and len(paths) == n
                for (pat, paths), (s, n) in zip(CLAIM_RULES, _samples)),
        [bool(pat.search(s)) for (pat, _), (s, _n) in zip(CLAIM_RULES, _samples)])

    _doc = {"generated_for_date": "2026-11-14", "book_decided_at": "2026-11-11",
            "priced_bar": "2026-11-13", "next_rebalance_date": "2026-12-09",
            "premium_forward": {"face_asof": "2026-11-13"},
            "positions": {"ledger_bar": "2026-11-13"},
            "cash_yield": {"rate_date": "2026-11-13"},
            "stress": {"first": "2005-02-23", "last": "2026-11-13"}}
    _txt_ok = ("# 今日 ETF 实盘单 —— 2026-11-14\n\n## 一句话\n\n**今天不用动手。** 上一次定稿 "
               "**2026-11-11**，今天只是按新的收盘价（**2026-11-13**）把同一批权重重新算成份额。"
               "下一个动手日是 **2026-12-09**。\n\n## 现金腿\n\n"
               "| 若一直只有今天的 1.26%（2026-11-13 报价） |\n")
    _c_ok = census(_doc, artifact="fixture/claims.json", printed=_txt_ok)
    leg("a printed date that equals the field its sentence quotes graduates the page",
        _c_ok["verdict"] == "PRINTED_DATES_AGREE" and _c_ok["date_claims"]["n_claims"] == 5
        and _c_ok["date_claims"]["n_ok"] == 5
        and _c_ok["date_claims"]["n_unmapped"] == 0, _c_ok["date_claims"])
    leg("the agreeing verdict says what it checked and what it did not",
        "逐句对上了" in _c_ok["sentence"] and "不核那个字段本身对不对" in _c_ok["sentence"],
        _c_ok["sentence"][:120])

    _doc_bad = dict(_doc, priced_bar="2026-11-12")
    _c_bad = census(_doc_bad, artifact="fixture/claims.json", printed=_txt_ok)
    leg("a printed date that lands on another bar is a mismatch, not a rounding note",
        _c_bad["verdict"] == "PRINTED_DATE_MISMATCH"
        and _c_bad["date_claims"]["n_mismatch"] == 1
        and _c_bad["date_claims"]["mismatches"][0]["field"] == "priced_bar"
        and "2026-11-13" in _c_bad["sentence"] and "2026-11-12" in _c_bad["sentence"], _c_bad)
    leg("one mismatch keeps the other four readings visible instead of collapsing them",
        _c_bad["date_claims"]["n_ok"] == 4 and _c_bad["date_claims"]["n_claims"] == 5,
        _c_bad["date_claims"])

    _c_missing = census({k: v for k, v in _doc.items() if k != "positions"},
                        artifact="fixture/claims.json",
                        printed="## 账上\n\n- 今天没有新 bar，账只记到 2026-11-13。\n")
    leg("a date whose field is absent is unverifiable and never counts as checked",
        _c_missing["verdict"] == "PRINTED_SELF_DATED"
        and _c_missing["date_claims"]["n_unverifiable"] == 1
        and _c_missing["date_claims"]["n_ok"] == 0, _c_missing["date_claims"])

    _c_unmapped = census(_doc, artifact="fixture/claims.json",
                         printed="## 杂项\n\n今天和 2026-01-01 没有关系。\n")
    leg("a printed date no rule claims is unmapped, never silently checked",
        _c_unmapped["verdict"] == "PRINTED_SELF_DATED"
        and _c_unmapped["date_claims"]["n_unmapped"] == 1
        and _c_unmapped["date_claims"]["n_claims"] == 0, _c_unmapped["date_claims"])

    _c_two = census(_doc, artifact="fixture/claims.json",
                    printed="## 最坏\n\n把今天这 5 只票重放回 2005-02-23~2026-11-13 的老面板。\n")
    leg("a line that names a range is read as two dated claims, one per field",
        _c_two["verdict"] == "PRINTED_DATES_AGREE"
        and {r["field"] for r in _c_two["date_claims"]["claims"]} == {"stress.first",
                                                                     "stress.last"},
        _c_two["date_claims"])

    _c_mixed = census(_doc, artifact="fixture/claims.json",
                      printed="# 今日 ETF 实盘单 —— 2026-11-14\n\n**今天不用动手。**\n")
    leg("one undated line blocks the agreeing verdict even when the dated one checks",
        _c_mixed["verdict"] == "PRINTED_BUT_UNANCHORED"
        and _c_mixed["date_claims"]["n_ok"] == 1
        and _c_mixed["printed"]["n_undated"] == 1, _c_mixed["date_claims"])

    # The published page must go through the same function the fixtures do, on both papers.
    doc, rel, printed_text, err = _read()
    if err:
        leg("the published page reads through its pointer", False, err)
    else:
        c = census(doc, artifact=rel, printed=printed_text)
        leg("the published page has a verdict this face can state",
            c["verdict"] in ("ANCHORED", "NO_DAY_WORDS", "DAY_WORD_ON_ANOTHER_DAY",
                             "DAY_WORD_WITHOUT_A_BAR", "PRINTED_BUT_UNANCHORED",
                             "PRINTED_SELF_DATED", "UNVERIFIED_PRINTED_FACE",
                             "PRINTED_DATE_MISMATCH", "PRINTED_DATES_AGREE"),
            c["verdict"])
        # r1671: CLEAN no longer means "the paper carries no day word". It means "no offender,
        # the paper was opened, and either it carries none, or every printed date was read
        # against the field its sentence quotes".
        _dc = c.get("date_claims") or {}
        leg("the published page's verdict agrees with its own head line",
            (c["verdict"] in CLEAN) == bool(not c["offenders"]
                                            and c["printed"]["state"] == "ok"
                                            and (not c["printed"]["n_lines"]
                                                 or (not _dc.get("n_mismatch")
                                                     and not _dc.get("n_undated")
                                                     and not _dc.get("n_unmapped")
                                                     and not _dc.get("n_unverifiable")
                                                     and _dc.get("n_claims")))),
            (c["verdict"], len(c["offenders"]), _dc.get("n_claims"), _dc.get("n_mismatch")))
        leg("the printed page really was opened (a census with no paper is not a census)",
            c["printed"]["state"] == "ok" and c["printed"].get("n_headings", 0) >= 0
            and printed_text is not None, c["printed"].get("state"))
        # r1669: a debt that is named must be quoted from the paper, not composed here.
        leg("every undated line this face names is a line the paper actually prints",
            all(r["line"] in printed_text for r in (c["printed"].get("undated") or []))
            if printed_text else True,
            [r["line"][:40] for r in (c["printed"].get("undated") or [])][:3])
    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "check"
    if cmd in ("--selftest", "selftest"):
        return selftest()
    if cmd == "run":
        return run()
    if cmd == "check":
        return check()
    print("usage: live_book_day_words.py [run|check|--selftest]")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
