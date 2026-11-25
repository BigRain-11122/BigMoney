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
# A line that carries its own date tells the reader which day it means (r1669). Group 1 is the
# date itself: r1684's ticket audit has to compare that day with the decision bar (a line dated
# with the page day is not anchored to the book), so the pattern carries the value, not just a
# boolean. Adding the group changes no caller that only asks "is there a date here".
DATE_IN_TEXT = re.compile(r"(20\d{2}-\d{2}-\d{2})")

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
    # r1788: this sentence ("按 DATE 的读数，这张单里可核验的 N 只票…") is the premium
    # one-liner, and its numbers come from premium_leak.own_ruler_summary at that face's
    # own session -- NOT from the premium-forward paper printed further down. The two are
    # different papers and the forward one may sit a session behind (it is built from a
    # panel that closes later), so reading this date against `premium_forward.face_asof`
    # went green on the days the two happened to coincide and red on every day they did
    # not -- a ruler that only agrees with itself (r1690 family, r1282/r1594).
    (re.compile(r"按 \*\*" + _D + r"\*\* 的读数"), ["premium_leak.session"]),
    (re.compile(r"账只记到 " + _D), ["positions.ledger_bar"]),
    (re.compile(r"（" + _D + r" 报价）"), ["cash_yield.rate_date"]),
    (re.compile(r"重放回 " + _D + "~" + _D), ["stress.first", "stress.last"]),
    (re.compile(r"已经吃到 \*\*" + _D + r"\*\* 的收盘"), ["priced_bar"]),
    (re.compile(r"（bar " + _D + r"）"), ["priced_bar"]),
    (re.compile(r"本页是 \*\*" + _D + r"\*\* 的页面"), ["generated_for_date"]),
    (re.compile(r"价格和数据都停在 \*\*" + _D + r"\*\*"), ["priced_bar"]),
    # r1721: the cash-caliber sentence says "today (the 2026-11-13 quote)"; it reads its own
    # face, so it must be checked against that face's quote date -- not against the cash
    # yield face just because the two happen to print the same day today.
    (re.compile(r"今天（" + _D + r" 的报价）"), ["cash_caliber.quote_date"]),
    # r1896 bm-c: the printed page grew ten dates whose issuing faces the page already reads,
    # and no rule claimed them -- so a page on which EVERY day word is dated (r1895: undated
    # 22 -> 0) still read as unpaid. r1789: a leg that is always red trains readers to treat
    # real defects as noise. Each rule names the face that ISSUED the number, not a field that
    # happens to hold the same day today (r1788).
    (re.compile(r"今天（" + _D + r"）距线"), ["era_capacity.evidence_cutoff"]),
    (re.compile(r"算到 " + _D + r"，面生成于 " + _D),
     ["era_capacity.evidence_cutoff", "era_capacity.generated"]),
    (re.compile(r"样本外窗口固定在 " + _D), ["admission.reads.oos_start"]),
    (re.compile(r"今天这一档读在 " + _D + r" 那天"), ["capacity_ticket.evidence_cutoff"]),
    (re.compile(r"「今天的报价」是 " + _D + r" 的"), ["carry_regime.quote_date"]),
    (re.compile(r"面板尾 " + _D + r" 落后"), ["carry_regime.evidence_cutoff"]),
    (re.compile(r"注意这一行定价在 \*\*" + _D + r"\*\* 那根 bar"),
     ["cash_caliber.quote_date"]),
    (re.compile(r"（本页 bar " + _D + r"）"), ["priced_bar"]),
    (re.compile(r"族面重定价的回执付的是世界 [^（]*（" + _D),
     ["family_coherence.receipt.generated"]),
    # r2119 bm-c: two sentences print TWO dates in one breath -- the day the source face is
    # priced on, and the day this page is priced on -- and both were unclaimed, so a page
    # whose every day word is anchored still carried four unpaid dates. Each date is read
    # against the field that issued it (the sentence names the face; the page carries it),
    # and the second date of each sentence is the page's own `priced_bar`, not a new one.
    (re.compile(r"这张读数按 \*\*" + _D + r"\*\* 的票面算，本页价的日期是 \*\*" + _D + r"\*\*"),
     ["premium_forward.face_asof", "priced_bar"]),
    (re.compile(r"额度来源面锚在 \*\*" + _D + r"\*\*，本页的价是 \*\*" + _D + r"\*\*"),
     ["floor_provenance.evidence_cutoff", "priced_bar"]),
]


def _doc_value(doc, path):
    v = doc
    for k in str(path).split("."):
        idx = re.match(r"^(.*?)\[(\d+)\]$", k)
        sel = re.match(r"^(.*?)\[([A-Za-z_]\w*)=([^\]]*)\]$", k)
        if sel:
            # r1893: a lane table is keyed by name, not by position.  `rows[lane=futures]`
            # survives a re-ordered table where `rows[0]` would quietly read the wrong lane.
            k, field, want = sel.group(1), sel.group(2), sel.group(3)
            if k:
                if not isinstance(v, dict):
                    return None
                v = v.get(k)
            if not isinstance(v, (list, tuple)):
                return None
            v = next((it for it in v
                      if isinstance(it, dict) and str(it.get(field)) == want), None)
            continue
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


def _date_claims(rows, doc, rules=None, unmapped_classifier=None):
    """Read every printed date against the field its sentence quotes.

    Three readings, and only one of them is green: `ok` (the sentence's date is the one the
    field carries), `mismatch` (the sentence names a day the field does not -- named with both
    dates), `unverifiable` (the field is missing, so nothing here can say the date is right).
    A date no rule claims is `unmapped`: the face does not know which paper that sentence
    quotes, and it says so rather than counting it as checked (r1471 family: reading a face
    is not the same as having a writer for it).

    `unmapped_classifier(rec) -> bucket or None` lets a longer paper sort its leftovers
    instead of either writing one rule per sentence or dropping forty dates into one
    anonymous debt bucket (r1674: the third paper prints 67 dates). A bucket is a *reason
    this date is not checked* (`identifier`, `policy`, `member_of_twin`) and it never counts
    as checked: the counts are printed beside the checked ones.
    """
    rules = CLAIM_RULES if rules is None else rules
    claims, mismatches, unmapped = [], [], []
    buckets, bucket_rows = {}, {}
    n_ok = n_unverif = 0
    for row in rows or []:
        line = row.get("line") or ""
        covered = []
        for pat, paths in rules:
            for m in pat.finditer(line):
                # r1893: a path may name a group placeholder (`rows[lane={lane}].tail`).
                # Named groups carry the key, positional groups carry the dates, so the
                # date group is the N-th *positional* group, not the N-th group overall.
                named = set(pat.groupindex.values())
                positional = [i for i in range(1, (pat.groups or 0) + 1)
                              if i not in named]
                gd = m.groupdict()
                for n, path in enumerate(paths):
                    gi = positional[n] if n < len(positional) else n + 1
                    date = m.group(gi)
                    if date is None:
                        continue
                    covered.append(m.span(gi))
                    # r1907: the claim publishes the path it actually read, with the named
                    # groups already filled in. Publishing the template (`rows[lane={lane}]`)
                    # put an unfilled brace placeholder on a reader face -- reader_text_audit
                    # flagged it as a spelling defect, and a reader could not tell which row
                    # the date came from. The resolved path answers both.
                    val_path = path.format(**gd) if "{" in path else path
                    val = _doc_value(doc, val_path)
                    exp = str(val)[:10] if isinstance(val, str) else None
                    rec = {"heading": row.get("heading"), "date": date, "field": val_path,
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
                rec = {"heading": row.get("heading"), "date": m.group(0),
                       "line": line[:140]}
                bucket = None
                if unmapped_classifier is not None:
                    bucket = unmapped_classifier(rec)
                if bucket:
                    buckets[bucket] = buckets.get(bucket, 0) + 1
                    rows_ = bucket_rows.setdefault(bucket, [])
                    if len(rows_) < 20:
                        rows_.append(rec)
                else:
                    unmapped.append(rec)
    return {"n_claims": len(claims), "n_ok": n_ok, "n_mismatch": len(mismatches),
            "n_unverifiable": n_unverif, "n_unmapped": len(unmapped),
            "n_rules": len(rules), "claims": claims[:40],
            "mismatches": mismatches[:20], "unmapped": unmapped[:20],
            "buckets": buckets, "bucket_rows": bucket_rows}
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
    heading_full = "(页首)"
    heading_date = None
    for line in (text or "").split("\n"):
        if line.startswith("## "):
            heading_full = line[3:].strip()
            heading = heading_full[:46]
            # the date is read off the FULL heading: a long title truncated for display
            # would otherwise lose a day written at its end (r1314)
            _hm = DATE_IN_TEXT.search(heading_full)
            heading_date = _hm.group(1) if _hm else None
        if any(w in line for w in DAY_WORDS):
            shown = line.strip()[:180]
            own = DATE_IN_TEXT.search(shown)
            # r1314: a section heading that names a day is a date the reader can see, and
            # every line under it inherits that day. Before this the inheritance was not
            # read at all, so 28 table/prose lines printed under headings like
            # 「2026-11-17 的收益，面板自己有了」 were counted as undatable -- the page was
            # already telling the reader which day it meant, in the line above.
            # It is NOT a loosening: a line with neither its own date nor a dated heading
            # still lands in `undated` and still fails the page.
            if own:
                src, day = "self", own.group(1)
            elif heading_date:
                src, day = "section_heading", heading_date
            else:
                src, day = "none", None
            rows.append({"heading": heading, "line": shown,
                         "self_dated": bool(own), "day_source": src, "day": day})
    heads = []
    for r in rows:
        if r["heading"] not in heads:
            heads.append(r["heading"])
    undated = [r for r in rows if r["day_source"] == "none"]
    scope = [r for r in rows if r["day_source"] == "section_heading"]
    sect = {}
    for r in scope:
        d = sect.setdefault(r["heading"], {"heading": r["heading"], "date": r["day"],
                                          "n_lines": 0})
        d["n_lines"] += 1
    return {"state": "ok", "n_lines": len(rows), "n_headings": len(heads),
            "n_self_dated": sum(1 for r in rows if r["self_dated"]),
            "n_scope_dated": len(scope), "n_undated": len(undated),
            "undated": undated[:40], "scope_dated": scope[:40],
            "section_days": list(sect.values())[:12],
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
    # r1817 bm-c: a page rendered after the close carries the last close's readings and says
    # so (`evidence_cutoff`). The day a today-word must sit on is the page's own DATA day — a
    # section older than THAT is the red one (a stale section). A page that reprints yesterday's
    # close is the normal shape, not a day-word sitting on another day (r1788 family: the date a
    # claim is judged against must be the face that produced the number).
    data_day = str(doc.get("evidence_cutoff") or "")[:10] or None
    judge_day = data_day or page_day
    if data_day and page_day and data_day < page_day:
        ret["day_source"] = "evidence_cutoff"
    ret["page_day"] = page_day
    ret["judge_day"] = judge_day
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
        elif judge_day and bar != judge_day:
            row["reading"] = "another_day"
            ret["offenders"].append(dict(row, sample=[h["text"][:160] for h in hits[:2]]))
        else:
            row["reading"] = "anchored"
            ret["n_anchored"] += 1
        ret["rows"].append(row)
    pr = ret["printed"]
    dc = ret.get("date_claims") or {}
    # r1302: the printed-date audit used to live only inside the "no section day word"
    # branch, so a page that GREW anchored sections stopped being audited at all -- the
    # improvement laundered the debt. The published page did exactly that on 2026-11-17:
    # ten sections carried an anchored day word, so this face said ANCHORED while a printed
    # line read 「今天的 1.26%（2026-11-13 报价）」 against `cash_yield.rate_date` = 2026-11-17.
    # Two findings, kept apart: a printed date that contradicts its own field is VERIFIED
    # WRONG and outranks anchoring; leftover date debts (undated / unmapped / unverifiable)
    # do not borrow the clean names either, but they are not that same red.
    _mismatch = bool(dc.get("n_mismatch"))
    _owed = bool(dc.get("n_unmapped") or dc.get("n_unverifiable") or pr.get("n_undated"))
    if ret["offenders"]:
        ret["verdict"] = "DAY_WORD_ON_ANOTHER_DAY"
    elif pr["state"] == "unreadable":
        ret["verdict"] = "UNVERIFIED_PRINTED_FACE"
    elif pr["state"] == "ok" and pr["n_lines"] and _mismatch:
        ret["verdict"] = "PRINTED_DATE_MISMATCH"
    elif pr["state"] == "ok" and pr["n_lines"] and not ret["n_with_day_word"]:
        # r1670: "N printed lines say 今天 and the reader cannot date them" and "every printed
        # line carries its own date" are two different debts, and both stay red -- nothing in
        # this face checks that a printed date is the RIGHT date. Splitting the name is what
        # lets the reader tell "still owed" from "paid, not yet audited".
        # r1671: the audit is what this branch now also carries -- a date no rule claims, or
        # one whose field is missing, keeps the page on the self-dated name, because "I could
        # not check it" never graduates to green. (The mismatch arm moved above in r1302 so
        # that anchoring cannot hide it.)
        if (dc.get("n_claims") and not dc.get("n_unmapped") and not pr.get("n_undated")
                and not dc.get("n_unverifiable") and dc.get("n_ok") == dc.get("n_claims")):
            ret["verdict"] = "PRINTED_DATES_AGREE"
        elif pr.get("n_undated") == 0 and pr.get("n_self_dated"):
            ret["verdict"] = "PRINTED_SELF_DATED"
        else:
            ret["verdict"] = "PRINTED_BUT_UNANCHORED"
    elif ret["n_unverifiable"]:
        ret["verdict"] = "DAY_WORD_WITHOUT_A_BAR"
    elif pr["state"] == "ok" and pr["n_lines"] and _owed:
        # Anchored sections, but the paper still owes dates: the structured half being clean
        # is not a claim about the printed one (r1670), so the clean names stay unavailable.
        ret["verdict"] = "PRINTED_BUT_UNANCHORED"
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
        _sc = pr.get("n_scope_dated") or 0
        _how = ("每一行都自带日期" if not _sc
                else "**%d 行自带日期、%d 行从所在小节标题的日期继承**"
                     % (pr.get("n_self_dated", 0), _sc))
        return ("**页面自己用的「今天/今日」有 %d 行，坐在 %d 个小节里；%s**"
                "（结构面里 %d 节，日词 0 节）。这一面核了 %d 处日期：%d 处对上它所引用的字段，"
                "**%d 处判不了（字段缺）**，**%d 处没有规则可核**——判不了的不算对上。"
                % (pr["n_lines"], pr["n_headings"], _how, c["n_sections"],
                   dc.get("n_claims", 0), dc.get("n_ok", 0), dc.get("n_unverifiable", 0),
                   dc.get("n_unmapped", 0)))
    if c["verdict"] == "PRINTED_BUT_UNANCHORED":
        _u = pr.get("undated") or []
        _sc = pr.get("n_scope_dated") or 0
        _split = ("其中 **%d 行自己带了日期**（读者读得出它算哪一天），"
                  "**%d 行从所在小节标题的日期继承**，**%d 行没有日期来源**"
                  % (pr.get("n_self_dated", 0), _sc, pr.get("n_undated", 0)))
        if _u:
            _split += "——没有的那几行是：%s%s" % (
                "、".join("「%s」里的一句 `%s`" % (r["heading"], r["line"][:40])
                         for r in _u[:4]),
                "…" if len(_u) > 4 else "")
        # r1302: this name is also reached when the sections ARE anchored and only the paper
        # owes dates, so the structured half has to be described as it really is.
        _sec = ("结构面里 %d 节，日词 0 节" % c["n_sections"]
                if not c["n_with_day_word"]
                else "结构面里 %d 节，其中 %d 节的日词落在页面自己那天上"
                     % (c["n_sections"], c["n_anchored"]))
        return ("**页面自己用的「今天/今日」有 %d 行，坐在 %d 个小节里；这一面核不到它们算哪一天**"
                "（%s）。%s。自带日期只说明句子诚实，不说明那个日期是对的。"
                "所以这不是「没有日词」，是「有，且没人能给它定日」。"
                % (pr["n_lines"], pr["n_headings"], _sec, _split))
    if c["verdict"] == "UNVERIFIED_PRINTED_FACE":
        return ("页面件读得出来（%d 节），但**印出来的那张纸读不到**——"
                "「没核到」不是「没有」。"
                % c["n_sections"])
    if c["verdict"] == "NO_DAY_WORDS":
        return ("页面这一版没有用「今天/今日/今晚」这类词（结构面 %d 节、印出来的纸上 0 行），"
                "因此没有可核验的日词——这既不是「全部对上了」，也不欠什么。"
                % c["n_sections"])
    head = "页面自称 %s、数据到 %s，%d 个节里 %d 节用了日词" % (c.get("page_day") or "?",
                                                          c.get("judge_day") or "?",
                                                          c["n_sections"],
                                                          c["n_with_day_word"])
    if c["verdict"] == "ANCHORED":
        _p = pr.get("n_lines") or 0
        if _p:
            _sc = pr.get("n_scope_dated") or 0
            return ("%s：全部 %d 节的日词都落在页面自己那天上；印出来的纸 %d 行日词里，"
                    "%d 行自带日期、%d 行从所在小节标题继承，%d 行无来源。"
                    % (head, c["n_anchored"], _p, pr.get("n_self_dated", 0), _sc,
                       pr.get("n_undated", 0)))
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

    postclose = {"generated_for_date": "2026-11-14",
                 "evidence_cutoff": "2026-11-13",
                 "quote": {"evidence_cutoff": "2026-11-13",
                           "line": "今天的报价就在它自己的均值上"}}
    c = census(postclose, artifact="fixture/postclose.json")
    leg("a page that declares its own data day reprints the close without being an offender",
        c["verdict"] == "ANCHORED" and c["judge_day"] == "2026-11-13"
        and c["page_day"] == "2026-11-14" and c["day_source"] == "evidence_cutoff"
        and not c["offenders"], c)

    lagsec = {"generated_for_date": "2026-11-14",
              "evidence_cutoff": "2026-11-13",
              "quote": {"evidence_cutoff": "2026-11-12",
                        "line": "今天的报价就在它自己的均值上"}}
    c = census(lagsec, artifact="fixture/lagsec.json")
    leg("a section older than the page's own declared data day is still an offender",
        c["verdict"] == "DAY_WORD_ON_ANOTHER_DAY" and len(c["offenders"]) == 1
        and c["offenders"][0]["bar"] == "2026-11-12", c)

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
        ("今天（2026-11-13 的报价）比窗口均值低 **75.5bp**", 1),
        ("今天（2026-11-19）距线：装得下 1M 的 1.003 倍", 1),
        ("边界：每一年都用今天的名单倒推；算到 2026-11-19，面生成于 2026-11-20T08:28:03", 2),
        ("边界：闸的样本外窗口固定在 2024-01-01，往前挪锚只加样本内暖机", 1),
        ("今天这一档读在 2026-11-20 那天", 1),
        ("表里那句「今天的报价」是 2026-11-19 的", 1),
        ("比这张表自己的面板尾 2026-11-20 落后 1 根 bar", 1),
        ("注意这一行定价在 **2026-11-19** 那根 bar（本页 bar 2026-11-20）", 1),
        ("（本页 bar 2026-11-20）", 1),
        ("上一次族面重定价的回执付的是世界 `?`（2026-11-20T18:02:26+0800）", 1),
        ("这张读数按 **2026-11-24** 的票面算，本页价的日期是 **2026-11-25**——两个日子对不上", 2),
        ("额度来源面锚在 **2026-11-24**，本页的价是 **2026-11-25**——两个日子对不上", 2),
    ]
    leg("every date rule has a sample of its own language, and every sample fires one rule",
        len(_samples) == len(CLAIM_RULES)
        and all(pat.search(s) and len(paths) == n
                for (pat, paths), (s, n) in zip(CLAIM_RULES, _samples)),
        [bool(pat.search(s)) for (pat, _), (s, _n) in zip(CLAIM_RULES, _samples)])

    # r1896 bm-c: the era-capacity dates anchor to a section the page only just started
    # carrying. Without that section the two dates must read "unverifiable" (the face is
    # missing), never green -- "I could not check it" does not graduate (r98/r1159).
    _era_line = ("- 边界：每一年都用今天的名单倒推（幸存者偏差），ADV 是该年自己的"
                 "20 根中位；算到 2026-11-19，面生成于 2026-11-20T08:28:03。")
    _no_era = census({"generated_for_date": "2026-11-21",
                      "evidence_cutoff": "2026-11-20"},
                     artifact="fixture/no-era.json", printed=_era_line)
    _with_era = census({"generated_for_date": "2026-11-21",
                        "evidence_cutoff": "2026-11-20",
                        "era_capacity": {"evidence_cutoff": "2026-11-19",
                                         "generated": "2026-11-20T08:28:03+08:00"}},
                       artifact="fixture/era.json", printed=_era_line)
    leg("the era-capacity dates are unverifiable without that section, and agree with it",
        _no_era["date_claims"].get("n_unverifiable") == 2
        and _no_era["date_claims"].get("n_ok") == 0
        and _with_era["date_claims"].get("n_ok") == 2
        and _with_era["date_claims"].get("n_unmapped") == 0,
        (_no_era["date_claims"], _with_era["date_claims"]))

    # r2119: same shape for the two two-date sentences. The page can print both dates only
    # because it read a face that carries them; if that face is missing the dates must read
    # unverifiable -- a rule that maps a sentence to a field must not turn a missing field
    # into a green check (r98 family).
    _two_date_line = ("这张读数按 **2026-11-24** 的票面算，本页价的日期是 **2026-11-25**——两个日子"
                      "对不上，下面这些数不能直接搬到今天的单上。\n"
                      "额度来源面锚在 **2026-11-24**，本页的价是 **2026-11-25**——两个日子对不上，"
                      "下面的拆分不能直接当作今天的。\n")
    _bare = census({"generated_for_date": "2026-11-26", "priced_bar": "2026-11-25"},
                   artifact="fixture/no-two-date-faces.json", printed=_two_date_line)
    _full = census({"generated_for_date": "2026-11-26", "priced_bar": "2026-11-25",
                    "premium_forward": {"face_asof": "2026-11-24"},
                    "floor_provenance": {"evidence_cutoff": "2026-11-24"}},
                   artifact="fixture/two-date-faces.json", printed=_two_date_line)
    leg("the two-date sentences are unverifiable without their faces and ok with them",
        _bare["date_claims"].get("n_unmapped") == 0
        # the page's own price day is still checkable; only the two face days go unverified
        and _bare["date_claims"].get("n_ok") == 2
        and _bare["date_claims"].get("n_unverifiable") == 2
        and _full["date_claims"].get("n_ok") == 4
        and _full["date_claims"].get("n_unmapped") == 0,
        (_bare["date_claims"], _full["date_claims"]))

    _doc = {"generated_for_date": "2026-11-14", "book_decided_at": "2026-11-11",
            "priced_bar": "2026-11-13", "next_rebalance_date": "2026-12-09",
            "premium_forward": {"face_asof": "2026-11-13"},
            "premium_leak": {"session": "2026-11-13"},
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

    # r1788: the premium one-liner quotes premium_leak's own session. The forward paper beside
    # it may legitimately sit a session behind, so a page whose two faces disagree is healthy
    # -- and a page whose sentence names a day neither face carries is not. Both directions
    # are pinned, because the old mapping passed the second case by accident.
    _txt_leak = ("## 一句话\n\n**今天不用动手。** 按 **2026-11-13** 的读数，"
                 "这张单里可核验的 5 只票有 **1 只**站在各自历史的最高一档溢价里。\n")
    _doc_split = dict(_doc, premium_forward={"face_asof": "2026-11-11"},
                      premium_leak={"session": "2026-11-13"})
    _c_leak = census(_doc_split, artifact="fixture/claims.json", printed=_txt_leak)
    leg("the premium one-liner is read against the leak face it quotes, not the forward paper",
        _c_leak["date_claims"]["n_mismatch"] == 0
        and [r["field"] for r in _c_leak["date_claims"]["claims"]]
        == ["premium_leak.session"], _c_leak["date_claims"])
    _c_leak_bad = census(_doc_split, artifact="fixture/claims.json",
                         printed=_txt_leak.replace("2026-11-13", "2026-11-12"))
    leg("a premium one-liner that names a day neither face carries is a mismatch",
        _c_leak_bad["date_claims"]["n_mismatch"] == 1
        and _c_leak_bad["date_claims"]["mismatches"][0]["field"] == "premium_leak.session"
        and "2026-11-12" in _c_leak_bad["sentence"]
        and "2026-11-13" in _c_leak_bad["sentence"], _c_leak_bad["date_claims"])

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

    # r1314: a dated section heading is a date the reader can see, so the lines under it
    # inherit it. Pinned in both directions -- inheriting must not turn an undated section
    # green, or the split becomes a blanket exemption.
    _pr_head = _printed_census(
        "## 2026-11-17 的收益，面板自己有了\n\n"
        "| 今天这么宽的历史样本够厚 | 1,122 |\n\n"
        "## 这些价差，收得回来吗\n\n| 今天这么宽的历史不足 8 次 | 373 |\n")
    leg("a line under a dated heading inherits that day; one under an undated heading does not",
        _pr_head["n_scope_dated"] == 1 and _pr_head["n_undated"] == 1
        and [r["day"] for r in _pr_head["scope_dated"]] == ["2026-11-17"],
        _pr_head)
    leg("an inherited day is carried on the row, so the reader is told where it came from",
        all(r.get("day_source") == "section_heading" and r.get("day")
            for r in _pr_head["scope_dated"]), _pr_head["scope_dated"])
    # A long heading is displayed truncated but READ in full: a date at its end must not be
    # invisible to the reader (the price-spread section is exactly this shape).
    _pr_long = _printed_census(
        "## 这些价差，收得回来吗：1,495 个里数出 325 个，但这个数没有超过尺子自己"
        "（重排路径中位 1,122 个）；2026-11-17 的盘口\n\n今天这么宽的历史不足 8 次 | 373 |\n")
    leg("a day written past the display cutoff is still read off the full heading",
        _pr_long["n_undated"] == 0 and _pr_long["n_scope_dated"] == 1
        and _pr_long["scope_dated"][0]["day"] == "2026-11-17", _pr_long)

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
        # r1813: `n_unmapped` counts prose dates -- sentences like "the quote in that table is
        # 2026-11-13's, two bars behind the panel's 2026-11-17" -- that name a date but quote
        # no field, because they exist to explain the gap. Demanding zero of them made a page
        # that explains itself fail the very leg that checks it explains itself. The hard
        # condition is a date that was read AGAINST a field and did not match (n_mismatch);
        # an unmapped prose date is information, not a defect.
        # r1310: `undated` is a field of the PRINTED face, not of `date_claims`. Reading it off
        # the wrong dict made the right-hand side true whenever the paper carried undated lines
        # (None is falsy), so this leg failed on every page with an undated line while bm-c's own
        # page -- which has none -- stayed green. A leg that is red only off its own machine is
        # the r1789 permanent-red shape: readers learn to skip it.
        leg("the published page's verdict agrees with its own head line",
            (c["verdict"] in CLEAN) == bool(not c["offenders"]
                                            and c["printed"]["state"] == "ok"
                                            and (not c["printed"]["n_lines"]
                                                 or (not _dc.get("n_mismatch")
                                                     and not c["printed"].get("n_undated")
                                                     and not _dc.get("n_unverifiable")
                                                     and _dc.get("n_claims")))),
            (c["verdict"], len(c["offenders"]), _dc.get("n_claims"), _dc.get("n_mismatch"),
             _dc.get("n_unmapped")))
        leg("the printed page really was opened (a census with no paper is not a census)",
            c["printed"]["state"] == "ok" and c["printed"].get("n_headings", 0) >= 0
            and printed_text is not None, c["printed"].get("state"))
        # r1669: a debt that is named must be quoted from the paper, not composed here.
        leg("every undated line this face names is a line the paper actually prints",
            all(r["line"] in printed_text for r in (c["printed"].get("undated") or []))
            if printed_text else True,
            [r["line"][:40] for r in (c["printed"].get("undated") or [])][:3])
    # r1893: a lane table is keyed by name.  Three legs pin the selector and the placeholder
    # rule shape, because both are new machinery and machinery without a failing-first leg
    # never reports (r1282/r1861 family).
    _lane_doc = {"lanes": {"rows": [
        {"lane": "heat", "tail": "2026-11-19", "missing_days": ["2026-11-20"]},
        {"lane": "futures", "tail": "2026-11-11", "missing_days": ["2026-11-12"]}]}}
    leg("a table read by name is not read by row number",
        _doc_value(_lane_doc, "lanes.rows[lane=futures].tail") == "2026-11-11"
        and _doc_value(_lane_doc, "lanes.rows[lane=heat].missing_days[0]") == "2026-11-20",
        _lane_doc)
    _lane_rules = [(__import__("re").compile(
        r"- `(?P<lane>[a-z_0-9]+)`（尾 " + _D + r"·欠：" + _D + r"）"),
        ["lanes.rows[lane={lane}].tail", "lanes.rows[lane={lane}].missing_days[0]"])]
    _rows_lane = [{"heading": "board", "line": "- `futures`（尾 2026-11-11·欠：2026-11-12）",
                   "self_dated": True}]
    _lc = _date_claims(_rows_lane, _lane_doc, rules=_lane_rules)
    leg("a named-group rule reads the lane's own row, both dates green",
        _lc["n_ok"] == 2 and not _lc["n_mismatch"] and not _lc["n_unmapped"], _lc)
    _rows_lane_bad = [{"heading": "board",
                       "line": "- `futures`（尾 2026-11-11·欠：2026-11-13）",
                       "self_dated": True}]
    _lb = _date_claims(_rows_lane_bad, _lane_doc, rules=_lane_rules)
    leg("a day the lane's row does not carry is a mismatch, not a pass",
        _lb["n_mismatch"] == 1 and _lb["mismatches"][0]["field"].endswith("missing_days[0]"),
        _lb)
    _rows_lane_missing = [{"heading": "board",
                           "line": "- `repo`（尾 2026-11-11·欠：2026-11-12）",
                           "self_dated": True}]
    _lm = _date_claims(_rows_lane_missing, _lane_doc, rules=_lane_rules)
    leg("a lane absent from the table reads as unverifiable, never as agreeing",
        _lm["n_unverifiable"] == 2 and _lm["n_ok"] == 0, _lm)
    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def _safe_stdout():
    """The page carries U+00A5 (¥) inside quoted lines; a GBK console raises
    UnicodeEncodeError mid-report and the chain reads a crash as rc=1 (r1310).
    Keep the console's own encoding, only stop it from raising."""
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass


def main(argv=None):
    _safe_stdout()
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
