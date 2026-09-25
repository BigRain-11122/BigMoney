"""T-72 refine probe: extract FULL tier title map from sina utils-hq.js.

r224 first probe found sina's own quote-page JS (n.sinaimg.cn/finance/hq2018/
utils-hq.js) defining r3_in as "散户净流入(元)" -- investor-class semantics, NOT
EM-style order-size tiers. This refine pulls the same JS once and extracts the
complete key->title map for all r0..r3* fields + any numeric threshold text,
to document the full official label face. 1 request, read-only, zero state.
"""
import sys, time, json, re, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

URL = "https://n.sinaimg.cn/finance/hq2018/utils-hq.js?ts=3.7"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
      "Referer": "https://finance.sina.com.cn/"}

op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
req = urllib.request.Request(URL, headers=UA)
t0 = time.time()
resp = op.open(req, timeout=15)
body = resp.read(3_000_000).decode("utf-8", errors="replace")
out = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "url": URL, "status": resp.status,
       "ms": int((time.time() - t0) * 1000), "bytes": len(body)}

# full key->title extraction: rX[_suffix]: { key: ..., title: "..." }
pairs = re.findall(r'(r[0-3](?:_[a-z0-9]+)?)\s*:\s*\{[^{}]*?title\s*:\s*"([^"]+)"', body)
out["title_map"] = sorted(set(pairs))

# threshold text near tier words (any 万元-style definition)
out["threshold_texts"] = []
for m in re.finditer(r"(超大单|大单|中单|小单|主力|散户|机构)", body):
    seg = body[max(0, m.start() - 150):m.end() + 200]
    if re.search(r"(\d+(\.\d+)?\s*(万|亿)?元?)", seg):
        out["threshold_texts"].append(seg.replace("\r", " ").replace("\n", " "))
        if len(out["threshold_texts"]) >= 10:
            break

# does this JS reference the lscjfb API family?
out["mentions_moneyflow_api"] = "MoneyFlow" in body or "lscjfb" in body

with open("results/_r224_bma_sina_tier_title_map.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "threshold_texts"},
                 ensure_ascii=False, indent=1))
print("threshold_texts n:", len(out["threshold_texts"]))
for t in out["threshold_texts"][:5]:
    print("THR:", t[:300])
