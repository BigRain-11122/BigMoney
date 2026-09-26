"""r270 bm-b -- T-76 wave-10 face (a) standing channels weekly machine-diff run.

Legs (ticket spec, wave-9 slice-1 seed state):
  hibor run-5   : reuse fixed collector results/hibor_radar.py (hash-keyed diff, rolls baseline)
  jisilu run-9  : /feed/category-5.rss verbatim URL (R132 verbatim law; slash variant 404s),
                  id-diff vs results/jisilu_feed_baseline.json, roll baseline
  guorn run-3   : raw-HTML href extraction (R169 recipe), diff vs
                  results/guorn_anchor_baseline.json posts, roll baseline + raw
Traffic discipline: serial, direct connection (ProxyHandler({})), no login (R109).
Also records the jin-gong daily-report observation (260925 absence hypothesis
verify pointer stays open until 09-28 first post-holiday daily).
"""
import json
import re
import subprocess
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
JISILU_URL = "https://jisilu.cn/feed/category-5.rss"
GUORN_URL = "https://guorn.com/"
JISILU_BASE = "results/jisilu_feed_baseline.json"
GUORN_BASE = "results/guorn_anchor_baseline.json"
GUORN_RAW = "results/guorn_home_raw.html"


def pull(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    r = op.open(req, timeout=30)
    return r.read().decode("utf-8", "ignore")


def now_ts():
    return time.strftime("%Y-%m-%dT%H:%M") + time.strftime("%z")[:3]


def leg_hibor():
    out = subprocess.run([sys.executable, "results/hibor_radar.py"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(out.stdout)
    if out.returncode != 0:
        print("HIBOR LEG FAIL rc=%d: %s" % (out.returncode, out.stderr[:300]))
    return out.returncode


def leg_jisilu():
    raw = pull(JISILU_URL)
    print("jisilu feed bytes:", len(raw))
    ids = re.findall(r"jisilu\.cn/question/(\d+)", raw)
    ids = sorted(set(ids))
    print("jisilu items:", len(ids))
    titles = {}
    for m in re.finditer(r"<item>(.*?)</item>", raw, re.S):
        link = re.search(r"<link>(.*?)</link>", m.group(1), re.S)
        title = re.search(r"<title>(.*?)</title>", m.group(1), re.S)
        if link and title:
            qid = re.search(r"question/(\d+)", link.group(1))
            if qid:
                titles[qid.group(1)] = re.sub(r"\s+", " ", re.sub(r"<!\[CDATA\[|\]\]>", "", title.group(1))).strip()
    base = json.load(open(JISILU_BASE, encoding="utf-8-sig"))
    prev_ids = set(base.get("ids", []))
    new = sorted(set(ids) - prev_ids)
    rolled = sorted(prev_ids - set(ids))
    print("machine-diff vs prev (ts=%s): %d new / %d rolled-out" % (base.get("ts"), len(new), len(rolled)))
    for q in new:
        print("NEW %s | %s" % (q, titles.get(q, "")[:90]))
    json.dump({"ids": ids, "ts": now_ts(), "prev_ts": base.get("ts"),
               "new": new, "rolled_out": rolled,
               "note": "run-9 weekly sample (wave10 face-a): rolling-baseline design (R141); verbatim URL R132 law"},
              open(JISILU_BASE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("baseline written:", JISILU_BASE)


def leg_guorn():
    raw = pull(GUORN_URL)
    open(GUORN_RAW, "w", encoding="utf-8").write(raw)
    print("guorn raw bytes:", len(raw))
    posts = sorted(set(re.findall(r"https://guorn\.com/forum/post/(p\.\d+\.\d+)", raw)))
    print("guorn unique post hrefs:", len(posts))
    base = json.load(open(GUORN_BASE, encoding="utf-8-sig"))
    prev = set(base.get("posts", []))
    new = sorted(set(posts) - prev)
    rolled = sorted(prev - set(posts))
    print("machine-diff vs prev (ts=%s): %d new / %d rolled-out" % (base.get("ts"), len(new), len(rolled)))
    for p in new:
        print("NEW", p)
    json.dump({"ts": now_ts(), "url": GUORN_URL, "posts": posts,
               "new": new, "rolled_out": rolled,
               "note": "guorn run-3 weekly sample (wave10 face-a): full unique /forum/post/ href extraction "
                       "(R169 raw-HTML recipe); raw persisted " + GUORN_RAW},
              open(GUORN_BASE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("baseline written:", GUORN_BASE)


def main():
    print("=== leg 1/3 hibor run-5 (existing collector) ===")
    rc1 = leg_hibor()
    time.sleep(2)
    print("=== leg 2/3 jisilu run-9 ===")
    leg_jisilu()
    time.sleep(2)
    print("=== leg 3/3 guorn run-3 ===")
    leg_guorn()
    print("=== face-a weekly sweep done (serial fetches, hibor rc=%d) ===" % rc1)


if __name__ == "__main__":
    main()
