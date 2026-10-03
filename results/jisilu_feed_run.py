r"""jisilu 套利 category feed standing-channel runner (O-1721 常态道).

Mirrors results/hibor_radar.py design: fetch verbatim URL (R132 law), parse
item ids, machine-diff vs rolling baseline (R141), write updated baseline.
Deep-capture triage is a human/AI step per digest -- this script only diffs.

Usage: python results\jisilu_feed_run.py [run-number]
"""
import io
import json
import re
import sys
import time
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

URL = "https://www.jisilu.cn/feed/category-5.rss"  # verbatim R132 law
BASE = "results/jisilu_feed_baseline.json"


def pull(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    r = op.open(req, timeout=30)
    return r.read().decode("utf-8", "ignore")


def parse(raw):
    # atom-style feed: <entry><id>https://www.jisilu.cn/question/516978.html</id><title>..
    # fall back to rss <item> if present; raw persisted by main() for shape-verification
    items = []
    for m in re.finditer(r"<entry>(.*?)</entry>", raw, re.S):
        seg = m.group(1)
        lm = re.search(r"<id>.*?/question/(\d+)\.html</id>", seg)
        tm = re.search(r"<title[^>]*>(.*?)</title>", seg, re.S)
        dm = re.search(r"<published>(.*?)</published>", seg, re.S) or re.search(
            r"<updated>(.*?)</updated>", seg, re.S
        )
        if not lm:
            continue
        title = re.sub(r"<!\[CDATA\[|\]\]>", "", tm.group(1)).strip() if tm else ""
        items.append(
            {
                "id": lm.group(1),
                "title": title,
                "pubDate": (dm.group(1).strip() if dm else ""),
            }
        )
    if items:
        return items
    for m in re.finditer(r"<item>(.*?)</item>", raw, re.S):
        seg = m.group(1)
        lm = re.search(r"<link>.*?/question/(\d+)(?:\.html)?</link>", seg)
        tm = re.search(r"<title>(.*?)</title>", seg, re.S)
        dm = re.search(r"<pubDate>(.*?)</pubDate>", seg, re.S)
        if not lm:
            continue
        title = re.sub(r"<!\[CDATA\[|\]\]>", "", tm.group(1)).strip() if tm else ""
        items.append(
            {
                "id": lm.group(1),
                "title": title,
                "pubDate": (dm.group(1).strip() if dm else ""),
            }
        )
    return items


def main():
    run_no = sys.argv[1] if len(sys.argv) > 1 else "run-N"
    raw = pull(URL)
    io.open("results/jisilu_feed_raw.xml", "w", encoding="utf-8").write(raw)
    print("raw bytes:", len(raw), "(persisted results/jisilu_feed_raw.xml)")
    if len(raw) < 500:
        print("RAW HEAD:", raw[:500])
    items = parse(raw)
    if not items:
        print("PARSE FAIL -- raw persisted, aborting baseline write")
        print("RAW HEAD:", raw[:800])
        sys.exit(1)
    print("items:", len(items))
    prev = None
    try:
        prev = json.load(open(BASE, encoding="utf-8"))
    except FileNotFoundError:
        print("no previous baseline (baseline-establishing run)")
    new_ids, rolled_out = [], []
    if prev:
        prev_ids = set(prev.get("ids", []))
        cur_ids = {e["id"] for e in items}
        new_ids = sorted(cur_ids - prev_ids)
        rolled_out = sorted(prev_ids - cur_ids)
        print(
            "machine-diff vs prev (ts=%s): %d new / %d rolled-out"
            % (prev.get("ts"), len(new_ids), len(rolled_out))
        )
    for e in items:
        print("%s | %s | %s" % (e["id"], (e["title"] or "")[:60], e["pubDate"][:25]))
    for qid in new_ids:
        e = next(x for x in items if x["id"] == qid)
        print("NEW %s | %s" % (qid, e["title"][:70]))
    out = {
        "ids": [e["id"] for e in items],
        "ts": time.strftime("%Y-%m-%dT%H:%M") + time.strftime("%z")[:3],
        "prev_ts": prev.get("ts") if prev else None,
        "new": new_ids,
        "rolled_out": rolled_out,
        "titles": {e["id"]: e["title"] for e in items},
        "note": "jisilu arb-category feed %s (rolling-baseline design R141; verbatim URL R132 law; runner results/jisilu_feed_run.py)" % run_no,
    }
    json.dump(out, open(BASE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("baseline written:", BASE, "ids:", len(out["ids"]))


if __name__ == "__main__":
    main()
