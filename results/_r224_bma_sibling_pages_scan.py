"""T-72 refine-5: probe realstock sibling pages for the lscjfb consumer (<=4 req).

nc.shtml exists at finance.sina.com.cn/realstock/company/sh600519/. The lscjfb
historical four-tier table ("历史成交分布") may live on a sibling page. Candidates
probed with HEAD-then-GET, keyword scan on any 200 body: zjlx (资金流向),
cjfb (成交分布), lscjfb, hiszjlx. Read-only.
"""
import sys, time, json, re, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
      "Referer": "https://finance.sina.com.cn/"}
BASE = "https://finance.sina.com.cn/realstock/company/sh600519/"
CANDS = ["zjlx.shtml", "cjfb.shtml", "lscjfb.shtml", "hiszjlx.shtml"]
KEYS = ["lscjfb", "MoneyFlow", "超大单", "大单", "中单", "小单", "主力", "散户", "大户", "中户"]

op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
out = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "probe": "realstock_sibling_scan",
       "pages": []}

for i, slug in enumerate(CANDS):
    url = BASE + slug
    try:
        req = urllib.request.Request(url, headers=UA)
        t0 = time.time()
        resp = op.open(req, timeout=12)
        body = resp.read(2_000_000).decode("utf-8", errors="replace")
        e = {"url": url, "status": resp.status, "ms": int((time.time() - t0) * 1000),
             "bytes": len(body),
             "keyword_hits": {k: (k in body) for k in KEYS}}
        if e["keyword_hits"]["lscjfb"] or any(e["keyword_hits"][k] for k in ("超大单", "大户", "中户")):
            # capture the tier legend text
            legs = []
            for m in re.finditer(r"(超大单|大单|中单|小单|大户|中户|主力|散户)", body):
                seg = body[max(0, m.start() - 200):m.end() + 260].replace("\r", " ").replace("\n", " ")
                legs.append(seg[:460])
                if len(legs) >= 10:
                    break
            e["legend_contexts"] = legs
        out["pages"].append(e)
        print(slug, resp.status, len(body), json.dumps(e["keyword_hits"], ensure_ascii=False))
    except Exception as ex:
        out["pages"].append({"url": url, "error": f"{type(ex).__name__}: {ex}"})
        print(slug, "ERR", type(ex).__name__)
    if i < len(CANDS) - 1:
        time.sleep(2.0)

with open("results/_r224_bma_sibling_pages_scan.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("saved -> results/_r224_bma_sibling_pages_scan.json")
