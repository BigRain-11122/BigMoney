"""Weekly arXiv q-fin standing-channel sweep - O-1721 wave-10 face (e), R153 recipe.

RESEARCH_MECHANISM.md §二 academic-source lane: arXiv API =
export.arxiv.org/api/query = open channel, zero login, zero wall
(R153 wave-8 slice-1 proof: category+phrase queries precise-hit, http->https
301 followed). /list/q-fin/recent single page is inefficient -> category
queries (q-fin.PM portfolio management / q-fin.STR statistical finance)
with a submittedDate window, past 7 days.

Weekly cadence (T-76 face (e) "one weekly query sweep"):
  - machine face ONLY: results/harvest/arxiv_sweep_<YYYYMMDD>.json
    (entries: id / published / updated / title / authors / categories /
    abstract). Triage/anti-dup/funnel is the round digest step, never here.
Safety (update_heat paradigm):
  - direct urllib + ProxyHandler({}) (Clash hijack law, bm-b r39)
  - serial fetch, >=3s pacing between the two category queries (R109)
  - idempotent by sweep date: today's file exists -> no-op exit 0
  - fetch fail -> exit 2 verbatim, no partial write (honest)
  - atomic write: staged .tmp then os.replace
  - `selftest` subcommand: offline Atom-XML fixture, zero network, tempdir
"""
import datetime as dt
import json
import os
import sys
import tempfile
import time
import urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "harvest")
API = "https://export.arxiv.org/api/query"
try:                              # bm-b: python default ctx lacks issuer for
    import ssl
    import certifi               # arxiv chain; certifi bundle is the fix (repo
    _CA = ssl.create_default_context(cafile=certifi.where())   # deps present)
except Exception:
    _CA = None
CATEGORIES = ("q-fin.PM", "q-fin.STR")   # channel spec: PM/STR category face
MAX_RESULTS = 60                          # >= one week of either category
PACING_S = 3                              # serial-step law (R109)
TIMEOUT_S = 60                            # arXiv sorted+filtered queries run
RETRY_SLEEP = 3                           # cold >30s (r260 probe 6.5s warm)
ATOM = "{http://www.w3.org/2005/Atom}"
OPENSEARCH = "{http://a9.com/-/spec/opensearch/1.1/}"


def _query_url(cat, start, end):
    # arXiv API date syntax: submittedDate:[YYYYMMDDHHMM TO YYYYMMDDHHMM]
    qr = "cat:%s AND submittedDate:[%s TO %s]" % (cat, start, end)
    from urllib.parse import urlencode
    return API + "?" + urlencode({
        "search_query": qr,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": str(MAX_RESULTS),
    })


def _fetch(url):
    handlers = [urllib.request.ProxyHandler({})]
    if _CA is not None:
        handlers.append(urllib.request.HTTPSHandler(context=_CA))
    opener = urllib.request.build_opener(*handlers)
    req = urllib.request.Request(url, headers={"User-Agent": "bigmoney-research/0.1"})
    try:
        with opener.open(req, timeout=TIMEOUT_S) as r:
            return r.read()
    except Exception:
        time.sleep(RETRY_SLEEP)          # one retry, cold-query latency face
        with opener.open(req, timeout=TIMEOUT_S) as r:
            return r.read()


def parse_atom(xml_bytes):
    """Atom XML -> (total_results, [entry dicts]). Raises on malformed."""
    root = ET.fromstring(xml_bytes)
    total = int(root.findtext(OPENSEARCH + "totalResults", "0"))
    entries = []
    for e in root.findall(ATOM + "entry"):
        g = lambda tag: (e.findtext(ATOM + tag) or "").strip()
        entries.append({
            "id": g("id"),
            "published": g("published"),
            "updated": g("updated"),
            "title": " ".join(g("title").split()),
            "authors": [a.findtext(ATOM + "name", "").strip()
                        for a in e.findall(ATOM + "author")],
            "categories": [c.get("term") for c in e.findall(ATOM + "category")],
            "abstract": " ".join(g("summary").split()),
        })
    return total, entries


def _in_window(entry, start_iso, end_iso):
    p = entry["published"][:10]
    return start_iso <= p <= end_iso


def run():
    os.makedirs(OUT_DIR, exist_ok=True)
    today = dt.date.today()
    out_path = os.path.join(OUT_DIR, "arxiv_sweep_%s.json" % today.strftime("%Y%m%d"))
    if os.path.exists(out_path):
        print("sweep: today's file exists -> no-op: %s" % out_path)
        return 0
    start = today - dt.timedelta(days=7)
    api_start, api_end = start.strftime("%Y%m%d%H%M"), today.strftime("%Y%m%d%H%M")
    queries, seen = [], {}
    try:
        for i, cat in enumerate(CATEGORIES):
            if i:
                time.sleep(PACING_S)
            xml = _fetch(_query_url(cat, api_start, api_end))
            total, entries = parse_atom(xml)
            kept = [e for e in entries if _in_window(e, start.isoformat(), today.isoformat())]
            queries.append({"category": cat, "totalResults": total,
                            "returned": len(entries), "in_window": len(kept)})
            for e in kept:
                seen.setdefault(e["id"], e)
    except Exception as exc:
        print("sweep: FETCH FAIL (%s) - no write, exit 2" % exc)
        return 2
    payload = {
        "swept_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "window": [start.isoformat(), today.isoformat()],
        "queries": queries,
        "entries": sorted(seen.values(), key=lambda e: (e["published"], e["id"])),
    }
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, out_path)
    print("sweep: %d entries in window [%s..%s] -> %s" %
          (len(payload["entries"]), payload["window"][0], payload["window"][1], out_path))
    for q in queries:
        print("  %s: totalResults=%d returned=%d in_window=%d" %
              (q["category"], q["totalResults"], q["returned"], q["in_window"]))
    return 0


def selftest():
    fixture = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">
<opensearch:totalResults>2</opensearch:totalResults>
<entry><id>http://arxiv.org/abs/2609.00001v1</id>
<published>2026-09-22T10:00:00Z</published><updated>2026-09-22T10:00:00Z</updated>
<title>Alpha  Discovery\n  via  Deep Nets</title>
<author><name>Alice Chen</name></author><author><name>Bob Li</name></author>
<category term="q-fin.PM"/><category term="q-fin.ST"/>
<summary>Momentum  is  nice.</summary></entry>
<entry><id>http://arxiv.org/abs/2609.00002v1</id>
<published>2026-08-01T10:00:00Z</published><updated>2026-08-01T10:00:00Z</updated>
<title>Old Paper Outside Window</title>
<author><name>Carol Wu</name></author>
<category term="q-fin.STR"/>
<summary>Outside the window.</summary></entry>
</feed>"""
    total, entries = parse_atom(fixture)
    assert total == 2, total
    assert len(entries) == 2
    e0 = entries[0]
    assert e0["title"] == "Alpha Discovery via Deep Nets", e0["title"]  # ws collapsed
    assert e0["authors"] == ["Alice Chen", "Bob Li"]
    assert e0["categories"] == ["q-fin.PM", "q-fin.ST"]
    assert e0["abstract"] == "Momentum is nice."
    assert _in_window(e0, "2026-09-19", "2026-09-26")
    assert not _in_window(entries[1], "2026-09-19", "2026-09-26")
    with tempfile.TemporaryDirectory() as td:
        bad = os.path.join(td, "bad.xml")
        with open(bad, "wb") as f:
            f.write(b"<feed><entry>")
        try:
            parse_atom(open(bad, "rb").read())
            raise AssertionError("malformed XML must raise")
        except ET.ParseError:
            pass
    print("selftest: all cases PASS")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(selftest())
    sys.exit(run())
