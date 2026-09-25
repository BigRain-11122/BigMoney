"""T-72 prereg S5 open-item: sina four-tier (r0..r3) threshold documentation probe.

Path designated by SINA_MF_PREREG.md section-5: "档位阈值官方文档（sina 页面 JS/
帮助面）→ 外源扫描常态线下批收口（O-1721）；收口前消费面档位语义=UNDOCUMENTED
诚实标注". Zero panel writes, zero state mutation, read-only page/JS scan.

Ladder (<=6 requests, 2.5s throttle -- first pull in flight on sibling path family):
  r1  quote page finance.sina.com.cn/realstock/company/sh600519/nc.shtml --
      collect script srcs + inline JS mentions of lscjfb/MoneyFlow/超大单.
  r2-r5 fetch up to 4 candidate JS/pages found by r1 (priority: mention-bearing
      srcs), grep for lscjfb + tier keywords (超大单/大单/中单/小单/r0_net),
      capture +-240char context around each hit (label mapping + any numeric
      threshold definitions).
  r6  reserved: direct known-view candidate if r1 yields nothing.

Verdict faces (honest, no overreach):
  DOCUMENTED       -- tier labels AND numeric thresholds on sina-owned surface
  PARTIAL-LABELS   -- tier label mapping documented, thresholds absent
  UNDOCUMENTED     -- nothing found (open item stays open, evidence kept)
"""
import sys, time, json, re, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
      "Referer": "https://finance.sina.com.cn/"}
QUOTE_PAGE = "https://finance.sina.com.cn/realstock/company/sh600519/nc.shtml"
FALLBACK_VIEW = ("https://vip.stock.finance.sina.com.cn/quotes_service/view/"
                "xh1.php?symbol=sh600519")
KEYWORDS = ["lscjfb", "MoneyFlow", "超大单", "大单", "中单", "小单", "r0_net", "主力净"]
TIER_RE = re.compile(r"(超大单|大单|中单|小单|lscjfb|r0_net)")
MAX_REQ = 6
budget = {"n": 0}


def opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def fetch(op, url, cap=3_000_000):
    if budget["n"] >= MAX_REQ:
        return {"url": url, "skipped": "budget exhausted"}
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


def hits(body):
    found = {k: (k in body) for k in KEYWORDS}
    ctx = []
    for m in TIER_RE.finditer(body):
        s, e = max(0, m.start() - 240), min(len(body), m.end() + 240)
        ctx.append(body[s:e].replace("\r", " ").replace("\n", " "))
        if len(ctx) >= 8:
            break
    return found, ctx


results = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "ticket": "T-2026-09-26-72",
           "probe": "sina_tier_threshold_documentation", "machine": "bm-a",
           "requests": [], "verdict": None}

op = opener()

# r1: quote page
page = fetch(op, QUOTE_PAGE)
entry = {k: v for k, v in page.items() if k != "body"}
if "body" in page:
    found, ctx = hits(page["body"])
    entry["keyword_hits"] = found
    entry["contexts"] = ctx[:4]
    srcs = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', page["body"])
    entry["script_srcs_n"] = len(srcs)
    results["script_srcs"] = srcs
results["requests"].append(entry)
print("r1 quote page:", json.dumps({k: v for k, v in entry.items() if k != "contexts"},
                                   ensure_ascii=False))

# r2-r5: candidate JS/iframe srcs mentioning likely moneyflow/quote JS
cands = []
if "script_srcs" in results:
    for s in results["script_srcs"]:
        low = s.lower()
        if any(t in low for t in ("moneyflow", "lscjfb", "hqview", "stock",
                                  "realstock", "vline", "sina")):
            if s.startswith("//"):
                s = "https:" + s
            elif s.startswith("/"):
                s = "https://finance.sina.com.cn" + s
            cands.append(s)
# inline JS may reference the API domain directly; add fallback view as tail candidate
cands = cands[:5]
for url in cands:
    if budget["n"] >= MAX_REQ:
        break
    time.sleep(2.5)
    js = fetch(op, url)
    je = {k: v for k, v in js.items() if k != "body"}
    if "body" in js:
        found, ctx = hits(js["body"])
        je["keyword_hits"] = found
        if ctx:
            je["contexts"] = ctx[:6]
    results["requests"].append(je)
    print(f"r{budget['n']} js:", url[:90], "->",
          json.dumps({k: v for k, v in je.items() if k in ("status", "bytes", "error", "keyword_hits")})[:220])

# r6: fallback dedicated view if no tier hit anywhere yet
any_hit = any(any(r.get("keyword_hits", {}).values()) for r in results["requests"])
if not any_hit and budget["n"] < MAX_REQ:
    time.sleep(2.5)
    fb = fetch(op, FALLBACK_VIEW)
    fe = {k: v for k, v in fb.items() if k != "body"}
    if "body" in fb:
        found, ctx = hits(fb["body"])
        fe["keyword_hits"] = found
        if ctx:
            fe["contexts"] = ctx[:6]
    results["requests"].append(fe)
    print("r6 fallback view:", json.dumps({k: v for k, v in fe.items() if k != "contexts"}, ensure_ascii=False)[:220])

# verdict derivation (honest faces)
tier_label_hit = False
threshold_hit = False
for r in results["requests"]:
    ctxs = r.get("contexts") or []
    joined = " ".join(ctxs)
    if any(t in joined for t in ("超大单", "大单", "中单", "小单")) and ("r0" in joined or "lscjfb" in joined):
        tier_label_hit = True
    # numeric threshold pattern near tier words (e.g. 100万 / >=50万元 style)
    for t in ("超大单", "大单", "中单", "小单"):
        for m in re.finditer(t, joined):
            seg = joined[max(0, m.start() - 120):m.end() + 160]
            if re.search(r"(\d+(\.\d+)?\s*(万|亿)?元?)", seg) and any(op_ in seg for op_ in (">", "≥", "大于", "以上", "不超过", "<", "≤", "介于")):
                threshold_hit = True

if tier_label_hit and threshold_hit:
    results["verdict"] = {"status": "DOCUMENTED",
                         "finding": "sina surface documents tier labels AND numeric thresholds",
                         "open_item": "CLOSED"}
elif tier_label_hit:
    results["verdict"] = {"status": "PARTIAL-LABELS",
                          "finding": "tier label mapping documented on sina surface; numeric thresholds NOT found",
                          "open_item": "advanced: labels documented, thresholds stay UNDOCUMENTED"}
else:
    results["verdict"] = {"status": "UNDOCUMENTED",
                          "finding": "no tier label or threshold documentation found on probed sina surfaces",
                          "open_item": "stays OPEN (consumption-face semantics remain UNDOCUMENTED honest label)"}

with open("results/_r224_bma_sina_tier_doc_probe.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("requests consumed:", budget["n"], "/", MAX_REQ)
print("saved -> results/_r224_bma_sina_tier_doc_probe.json")
print("VERDICT:", json.dumps(results["verdict"], ensure_ascii=False))
