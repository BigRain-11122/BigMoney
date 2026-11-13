#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""page_repeat_guard.py -- a published measurement may be printed once.

WHY THIS EXISTS (r1639 bm-c)
    r1638 found the same sentence ("4 个 REJECT 里有 3 个站得住", built in
    `_render_fc`) copied twice onto the live book page: the two copies read as
    two independent pieces of evidence, and the leg that guarded that block was
    `"..." in _md` -- immune to repetition by construction (284/284 green while
    the page was wrong).  The instance was fixed (one copy deleted, L56e now
    asserts `count(...) == 1`), but L56e is a BLOCK-scoped judgement inside one
    renderer: any other block, any other renderer, and any re-introduced copy
    leaves the same reading on a CEO-facing page with nothing able to see it.

WHAT THE RULE IS
    Within one published face, a *sentence* is
      * cut on 。！？!? (and on line breaks),
      * kept only if it carries a digit AND is at least MIN_LEN characters,
      * read from prose only -- table rows (`|`), headings (`#`), quotes (`>`)
        and fenced code are excluded, because a table legitimately repeats its
        column shape row after row and a heading legitimately repeats a date.
        List bullets (`-`/`*`/`+`/`1.`) ARE prose: the Chinese CEO faces are
        almost entirely bullets, and excluding them read those pages as
        "too little prose to judge" (r1639 measured 0 kept sentences on the
        live-usage page and 73 of 203 on the live book -- a guard that cannot
        see the page is not a guard).
    A kept sentence appearing twice is a HIT: the same measurement is offered
    twice as if it were two.  Identical SHORT phrases (< MIN_LEN) are not hits --
    "2026-11-13" belongs in every section that names the bar.

    The check is deliberately about the PUBLISHED bytes, not about one
    renderer's variables: it answers "what a reader can see", so it holds for
    pages this repo does not generate, and it cannot be satisfied by a renderer
    that prints the copy somewhere the renderer's own selftest does not look.

USAGE
  python Tools/page_repeat_guard.py scan            # default face set, exit 1 on hit
  python Tools/page_repeat_guard.py scan a.md b.md  # explicit faces
  python Tools/page_repeat_guard.py scan --verbose  # print every kept sentence count
  python Tools/page_repeat_guard.py selftest
"""
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_LEN = 40

# CEO-facing faces. A path pattern with no match is SKIPPED and named, never a
# failure: the faces are produced by different legs and a round that runs before
# the order is published must not read "missing" as "clean" -- see the `absent`
# list in the receipt.
DEFAULT_FACES = [
    ("live_book", "docs/live_book/LIVE-BOOK-*.md"),
    ("order", "results/etf_book_order/ORDER-*.md"),
    ("daily_report", "docs/daily_report/REPORT-*.md"),
    ("live_usage", "docs/live_usage/LIVE-*.md"),
]

_TABLE = re.compile(r"^\s*(\||#{1,6}\s|>\s)")
_BULLET = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
_SENT = re.compile(r"(?<=[。！？!?])")
_FENCE = re.compile(r"^\s*```")


def sentences(text):
    """Prose sentences that carry a number and are long enough to be a claim.

    Returns [(sentence, line_no)].  A sentence is the join of consecutive prose
    lines inside one paragraph (a wrapped sentence is ONE sentence), which is why
    the paragraph buffer is flushed on a blank line, a table row, a heading, or
    a fence instead of being cut per line.
    """
    out = []
    buf = []
    start = None

    def join(lines):
        """Glue wrapped lines. A space is inserted only between two ASCII word
        characters: Chinese text must not gain spurious spaces (they would make
        the same sentence compare unequal when it happens to wrap elsewhere),
        while `card` + `says` must not become `cardsays`."""
        out = lines[0]
        for nxt in lines[1:]:
            if out and nxt and out[-1].isascii() and out[-1].isalnum() \
                    and nxt[0].isascii() and nxt[0].isalnum():
                out += " " + nxt
            else:
                out += nxt
        return out

    def flush():
        nonlocal buf, start
        if not buf:
            return
        para = join(buf)
        for s in _SENT.split(para):
            s = s.strip()
            if len(s) >= MIN_LEN and re.search(r"\d", s):
                out.append((s, start))
        buf = []
        start = None

    in_fence = False
    for i, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        if _FENCE.match(line):
            flush()
            in_fence = not in_fence
            continue
        if in_fence or not line.strip() or _TABLE.match(line):
            flush()
            continue
        # A bullet is its own paragraph: its marker is not prose, but the text
        # after it is (the Chinese faces are bullet pages; see the module doc).
        m = _BULLET.match(line)
        if m:
            flush()
            buf = [line[m.end():].strip()]
            start = i
            continue
        if not buf:
            start = i
        buf.append(line.strip())
    flush()
    return out


def scan_text(text):
    """[(sentence, count, lines)] for every sentence printed more than once."""
    seen = {}
    for s, ln in sentences(text):
        e = seen.setdefault(s, {"count": 0, "lines": []})
        e["count"] += 1
        e["lines"].append(ln)
    return [(s, e["count"], e["lines"]) for s, e in seen.items() if e["count"] > 1]


def _latest(pattern):
    hits = sorted(glob.glob(os.path.join(ROOT, pattern)))
    return hits[-1] if hits else None


def faces(argv):
    if argv:
        return [("arg", a if os.path.isabs(a) else os.path.join(ROOT, a)) for a in argv]
    out = []
    for name, pat in DEFAULT_FACES:
        p = _latest(pat)
        if p:
            out.append((name, p))
    return out


def scan(argv, verbose=False):
    hits = []
    thin = []
    absent = [n for n, p in DEFAULT_FACES if not argv and not _latest(p)] if not argv else []
    read = []
    for name, path in faces(argv):
        try:
            with io.open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError as exc:
            print("[repeat] cannot read %s: %s" % (path, exc))
            return 2
        read.append({"face": name, "path": os.path.relpath(path, ROOT)})
        kept = sentences(text)
        found = scan_text(text)
        if verbose:
            print("[repeat] %s: %d kept sentence(s), %d repeated"
                  % (name, len(kept), len(found)))
        # A face with (almost) no kept sentence cannot be broken twice by this
        # guard, and silence there must not read as "verified clean".
        if len(kept) < 3:
            thin.append({"face": name, "kept": len(kept)})
        for s, n, lines in found:
            hits.append({"face": name, "path": os.path.relpath(path, ROOT),
                         "count": n, "lines": lines, "sentence": s})
            print("[repeat] %s:%s printed %dx  %s"
                  % (name, ",".join(str(x) for x in lines), n, s[:160]))
    rec = {"faces": read, "absent": absent, "thin": thin, "hits": len(hits),
           "details": hits, "min_len": MIN_LEN}
    if not hits:
        print("[repeat] %d face(s) scanned, 0 repeated sentence(s)%s%s"
              % (len(read),
                 ("; absent: " + ",".join(absent)) if absent else "",
                 ("; too little prose to judge: "
                  + ",".join("%s(%d kept)" % (t["face"], t["kept"]) for t in thin))
                 if thin else ""))
    return 1 if hits else 0


# ----------------------------------------------------------------- selftest
def _run_selftest():
    ok = True

    def leg(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond)
        print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                             ("  (%s)" % detail) if detail else ""))

    dup = ("The book earned 8.41% a year on this panel and the card says 8.52%.\n"
           "\n"
           "The book earned 8.41% a year on this panel and the card says 8.52%.\n")
    leg("a sentence printed twice is a hit", len(scan_text(dup)) == 1,
        str(scan_text(dup)))

    once = "The book earned 8.41% a year on this panel and the card says 8.52%.\n"
    leg("a sentence printed once is clean", scan_text(once) == [])

    tbl = ("| arm | ann | sharpe |\n|---|---|---|\n"
           "| cost0 | 8.41% | 0.92 |\n| cost05 | 8.41% | 0.92 |\n")
    leg("table rows that share a shape are not hits", scan_text(tbl) == [])

    short = "2026-11-13\n\n2026-11-13\n"
    leg("a short repeated token (a date) is not a hit", scan_text(short) == [])

    wrapped = ("The book earned 8.41% a year on this panel and the card\n"
               "says 8.52% on the same bar.\n\n"
               "The book earned 8.41% a year on this panel and the card says 8.52% on the "
               "same bar.\n")
    leg("a wrapped sentence is compared as one sentence (not as two lines)",
        len(scan_text(wrapped)) == 1, str(len(scan_text(wrapped))))

    hed = ("# 2026-11-13\n\n## 2026-11-13\n\n> 2026-11-13 position 8.41% a year on the panel OK\n")
    leg("headings and quotes are excluded from the prose pool", scan_text(hed) == [])

    cjk = "跌停池 33（+28）· 炸板池 21（-14）· 封板率 63.8% · 读法：跌停≥涨停 → 杀跌日，今日 否"
    bullets = "- " + cjk + "\n\n- " + cjk + "\n"
    leg("a bullet carries prose: the same claim in two bullets is a hit",
        len(scan_text(bullets)) == 1, str(len(scan_text(bullets))))
    leg("a bullet page yields sentences to judge, not 'too little prose'",
        len(sentences(bullets)) == 2, str(len(sentences(bullets))))
    # the marker itself is not part of the claim: `- X` and `* X` are the same
    # sentence, which is what a re-render with another marker would produce
    mixed = "- " + cjk + "\n\n* " + cjk + "\n"
    leg("the bullet marker is stripped before comparing", len(scan_text(mixed)) == 1)
    short_cjk = "- 政体态 RED · asof 2026-11-13\n\n- 政体态 RED · asof 2026-11-13\n"
    leg("a short repeated bullet line is not a claim", scan_text(short_cjk) == [])

    fence = ("```\nThe book earned 8.41% a year on this panel and the card says 8.52%.\n"
             "The book earned 8.41% a year on this panel and the card says 8.52%.\n```\n")
    leg("fenced code is not prose", scan_text(fence) == [])

    # a sentence with no digit is not a claim this guard can price
    nodigit = "The book beat the card on the same bar and the reader must decide.\n"
    leg("a repeated sentence with no number is outside this guard", scan_text(nodigit * 2) == [])

    # real faces on disk, if present, must be clean
    for name, path in faces([]):
        with io.open(path, encoding="utf-8") as f:
            got = scan_text(f.read())
        leg("real face %s is clean" % name, got == [],
            "; ".join("%dx %s" % (n, s[:60]) for s, n, _ in got))

    print("[page_repeat_guard] selftest %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    if not argv:
        print(__doc__.strip().splitlines()[-4].strip())
        print("usage: page_repeat_guard.py [scan <faces...>] [--verbose] [--json] | selftest")
        return 2
    cmd, rest = argv[0], argv[1:]
    verbose = "--verbose" in rest
    rest = [a for a in rest if not a.startswith("--")]
    if cmd == "selftest":
        return _run_selftest()
    if cmd == "scan":
        rc = scan(rest, verbose=verbose)
        if "--json" in argv:
            print(json.dumps({"rc": rc}, ensure_ascii=False))
        return rc
    print("unknown command %r" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
