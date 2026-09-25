"""T-72 refine-2 probe: locate the lscjfb consumer page/JS with full 4-tier legend.

Known so far (official sina surface, utils-hq.js): r0_in="主力净流入(元)",
r3_in="散户净流入(元)" -- investor-class semantics. Missing: r1/r2 labels and
numeric thresholds. The lscjfb API consumer JS is NOT utils-hq.js (no MoneyFlow
mention). This probe: quote page src scan with a sharper filter (hq2018 family,
money/zjlx/capital/flow names) + the vip quotes_service view fallback.
<=5 requests, read-only.
"""
import sys, time, json, re, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
      "Referer": "https://finance.sina.com.cn/"}
QUOTE_PAGE = "https://finance.sina.com.cn/realstock/company/sh600519/nc.shtml"
VIEW_CAND = "https://vip.stock.finance.sina.com.cn/quotes_service/view/xh1.php?symbol=sh600519"
KEYS = ["lscjfb", "MoneyFlow", "超大单", "大单", "中单", "小单", "主力", "散户", "中户", "大户"]
MAX_REQ = 5
budget = {"n": 0}


def opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def fetch(op, url, cap=3_000_000):
    if budget["n"] >= MAX_REQ:
        return {"url": url, "skipped": "budget"}
    budget["n"] += 1
    try:
        req = urllib.request.Request(url, headers=UA)
        t0 = time.time()
        resp = op.open(req, timeout=15)
        body = resp.read(cap).decode("utf-8", errors="replace")
        return {"url": url, "status": resp.status, "ms": int((time.time() - t0) * 1000),
                "bytes": len(body), "body": body}
    except Exception as e:
        return {"url": url, "error": f"{type(e).__name__}: {e}"}


out = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "machine": "bm-a",
       "probe": "lscjfb_consumer_locate", "requests": [], "tier_definitions": []}
op = opener()

page = fetch(op, QUOTE_PAGE)
srcs = []
if "body" in page:
    srcs = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', page["body"])
    out["quote_page_srcs_n"] = len(srcs)
    # inline mentions of the moneyflow tab / lscjfb
    for m in re.finditer(r"lscjfb|MoneyFlow|资金流向", page["body"]):
        seg = page["body"][max(0, m.start() - 100):m.end() + 150]
        out["requests"].append({"url": QUOTE_PAGE + "#inline", "snippet": seg.replace("\r", " ").replace("\n", " ")[:260]})
        break

# sharp filter: hq2018 family OR money/zjlx/capital/flow-named srcs
cands = []
for s in srcs:
    low = s.lower()
    if "hq2018" in low or any(t in low for t in ("money", "zjlx", "capital", "flow")):
        if s.startswith("//"):
            s = "https:" + s
        cands.append(s)
out["candidates"] = cands

for url in cands[: MAX_REQ - 2]:
    time.sleep(2.0)
    js = fetch(op, url)
    e = {k: v for k, v in js.items() if k != "body"}
    if "body" in js:
        e["keyword_hits"] = {k: (k in js["body"]) for k in KEYS}
        if "lscjfb" in js["body"] or any(e["keyword_hits"][k] for k in ("超大单", "中户", "大户")):
            # extract tier definition contexts
            for m in re.finditer(r"(超大单|大单|中单|小单|主力|散户|中户|大户|lscjfb)", js["body"]):
                seg = js["body"][max(0, m.start() - 260):m.end() + 260].replace("\r", " ").replace("\n", " ")
                out["tier_definitions"].append({"src": url, "ctx": seg[:520]})
                if len(out["tier_definitions"]) >= 12:
                    break
    out["requests"].append(e)
    print(f"r{budget['n']}:", url[:90], "->", json.dumps({k: v for k, v in e.items() if k in ("status", "bytes", "error", "keyword_hits")})[:260])

# view fallback
if budget["n"] < MAX_REQ:
    time.sleep(2.0)
    v = fetch(op, VIEW_CAND)
    ve = {k: v for k, v in v.items() if k != "body"}
    if "body" in v:
        ve["keyword_hits"] = {k: (k in v["body"]) for k in KEYS}
        for m in re.finditer(r"(超大单|大单|中单|小单|中户|大户|主力|散户)", v["body"]):
            seg = v["body"][max(0, m.start() - 260):m.end() + 260].replace("\r", " ").replace("\n", " ")
            out["tier_definitions"].append({"src": VIEW_CAND, "ctx": seg[:520]})
            if len(out["tier_definitions"]) >= 12:
                break
    out["requests"].append(ve)
    print(f"r{budget['n']} view:", json.dumps({k: v for k, v in ve.items() if k in ("status", "bytes", "error", "keyword_hits")})[:260])

with open("results/_r224_bma_lscjfb_consumer_probe.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("requests:", budget["n"], "| tier_definition contexts:", len(out["tier_definitions"]))
for t in out["tier_definitions"][:6]:
    print("DEF:", t["src"][:70], "|", t["ctx"][:200])
