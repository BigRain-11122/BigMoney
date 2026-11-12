#!/usr/bin/env python
"""English-prose census for the two Chinese pages a reader actually opens.

WHY
---
r1582 found `regime_cap_vs_book.sentence()` printed verbatim inside the CEO 一页纸
§② and the daily report §一: four lines of English prose in a Chinese page, and it
had been there since the face was wired. Fixing that one sentence does not stop the
class -- the pages quote other upstream faces in the same way (portfolio readouts,
paper-account notes, data-lane caveats).

WHY A CENSUS AND NOT A HARD GATE
--------------------------------
Those inherited lines belong to other faces' authors, and rewriting them blind would
falsify someone else's disclosure. So this is an allow-list census: what is already
published is recorded once with a stable fingerprint, and the gate fires only on a
line that appears for the first time. The count of inherited lines is printed on
every run so the debt stays visible instead of being absorbed into a green light.

FINGERPRINT
-----------
Numbers move every day (asof dates, equities) so a raw-line hash would fire daily.
The fingerprint is the ASCII word sequence only: `[A-Za-z]+` lowercased, joined.
A line that keeps its words keeps its fingerprint no matter what the numbers say.

Usage:
    python scripts/zh_page_prose_census.py run [--date YYYY-MM-DD]
    python scripts/zh_page_prose_census.py run --accept      # record today's hits
    python scripts/zh_page_prose_census.py check
    python scripts/zh_page_prose_census.py selftest

Exit: 0 = no new English prose, 1 = at least one new line, 2 = mechanism failure.
"""
import datetime
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "results", "zh_page_prose_census.json")
ALLOW = os.path.join(ROOT, "results", "zh_page_en_allow.json")

MIN_BODY = 60       # shorter lines are labels/tickers, not prose
MIN_WORDS = 8       # an English sentence carries at least this many words
MIN_SPACES = 8      # ... and this many gaps
ASCII_RATIO = 0.55  # ... and the letters are mostly ASCII


def face_paths(day=None):
    day = day or datetime.date.today().strftime("%Y-%m-%d")
    return [os.path.join(ROOT, "docs", "live_usage", "LIVE-%s.md" % day),
            os.path.join(ROOT, "docs", "daily_report", "REPORT-%s.md" % day)]


def fingerprint(line):
    """Stable across number changes: the ASCII word sequence, lowercased."""
    return hashlib.sha256(
        " ".join(w.lower() for w in re.findall(r"[A-Za-z]+", line)).encode()
    ).hexdigest()[:16]


def is_prose(line):
    body = "".join(ch for ch in line if ch not in "`*_|>#-\t")
    if len(body) < MIN_BODY:
        return False
    words = re.findall(r"[A-Za-z]{2,}", line)
    if len(words) < MIN_WORDS:
        return False
    letters = sum(1 for ch in body if ch.isascii() and ch.isalpha())
    return letters / len(body) > ASCII_RATIO and line.count(" ") >= MIN_SPACES


def scan(paths):
    hits = []
    for p in paths:
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as fh:
            for i, ln in enumerate(fh.read().splitlines(), 1):
                if is_prose(ln):
                    hits.append({"face": os.path.basename(p), "line": i,
                                 "sha16": fingerprint(ln),
                                 "text": ln.strip()[:180]})
    return hits


def load_allow():
    try:
        with open(ALLOW, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {"sha16": [], "note": "no allow list yet -- every hit counts as new"}


def run(day=None, accept=False):
    paths = face_paths(day)
    missing = [os.path.basename(p) for p in paths if not os.path.exists(p)]
    if missing:
        return 2, {"verdict": "FACES_MISSING", "missing": missing}
    hits = scan(paths)
    allow = load_allow()
    known = set(allow.get("sha16") or [])
    new = [h for h in hits if h["sha16"] not in known]
    face = {"generated": datetime.datetime.now().isoformat(timespec="seconds"),
            "cutoff": day or datetime.date.today().strftime("%Y-%m-%d"),
            "faces": [os.path.basename(p) for p in paths],
            "n_hits": len(hits), "n_inherited": len(hits) - len(new),
            "n_new": len(new), "new": new[:20], "hits": hits,
            "verdict": "NEW_PROSE" if new else "ONLY_INHERITED"}
    if accept:
        merged = sorted(known | {h["sha16"] for h in hits})
        with open(ALLOW, "w", encoding="utf-8") as fh:
            json.dump({"note": "inherited English prose on the Chinese CEO pages (r1582 census)",
                       "accepted_at": datetime.datetime.now().isoformat(timespec="seconds"),
                       "sha16": merged}, fh, ensure_ascii=False, indent=1)
        face["accepted"] = True
        face["allow_n"] = len(merged)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
    return (1 if new else 0), face


def detail(face):
    if face.get("verdict") == "FACES_MISSING":
        return "missing=%s" % face["missing"]
    return "hits=%d inherited=%d new=%d%s" % (
        face["n_hits"], face["n_inherited"], face["n_new"],
        (" first_new=%s:%d" % (face["new"][0]["face"], face["new"][0]["line"])) if face["new"] else "")


def check(day=None):
    rc, face = run(day)
    return rc, detail(face)


def _selftest():
    ok = tot = 0

    def chk(name, cond):
        nonlocal ok, tot
        tot += 1
        if cond:
            ok += 1
            print("[OK] " + name)
        else:
            print("[FAIL] " + name)
        return cond

    en = ("- **这个帽子和下面的钱对过账**：Market state RED caps new risk at 20% of "
          "equity. The cap sources disagree (paper_engine) -- read the gap as unresolved.")
    zh = "- **这个帽子和下面的钱对过账**：市场状态 RED 把新增风险的股票敞口压在上限 20%。"
    tick = "- 持仓：510300 4.15 · SHA16 04f8fce9856cb2e1"
    chk("an English sentence on a Chinese page is prose", is_prose(en))
    chk("a Chinese line with one latin ticker is not prose", not is_prose(zh))
    chk("a label/ticker line is not prose", not is_prose(tick))
    chk("numbers do not move the fingerprint",
        fingerprint("- tail 2026-10-26 official day behind window 20")
        == fingerprint("- tail 2026-11-02 official day behind window 09"))
    daily_a = "- `sina_mf`: tail 2026-10-26, **12** official day(s) behind, window **20** trading days"
    daily_b = "- `sina_mf`: tail 2026-11-02, **9** official day(s) behind, window **20** trading days"
    chk("a caveat that only changes its numbers keeps its fingerprint",
        fingerprint(daily_a) == fingerprint(daily_b))
    chk("a different sentence carries a different fingerprint",
        fingerprint(en) != fingerprint(daily_a))
    print("selftest %d/%d PASS" % (ok, tot))
    return 0 if ok == tot else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    day = None
    accept = False
    for i, a in enumerate(argv[2:], 2):
        if a == "--date" and i + 1 < len(argv):
            day = argv[i + 1]
        elif a.startswith("--date="):
            day = a.split("=", 1)[1]
        elif a == "--accept":
            accept = True
    if cmd == "selftest":
        return _selftest()
    if cmd == "check":
        rc, d = check(day)
        print("%s %s" % ("NEW-PROSE" if rc == 1 else ("FACES-MISSING" if rc == 2 else "CLEAN"), d))
        return rc
    rc, face = run(day, accept=accept)
    print(detail(face))
    if accept:
        print("accepted %d hit(s) -> %s" % (face["n_hits"], os.path.basename(ALLOW)))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
