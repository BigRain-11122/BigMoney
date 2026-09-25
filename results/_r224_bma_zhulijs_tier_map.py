"""T-72 refine-4: extract r0..r3 tier map from hqZhuli0612.js (quote-page zhu-li JS).

Candidate list from the quote page revealed n.sinaimg.cn/finance/hq2018/js/
hqZhuli0612.js -- the zhu-li (main-force) analysis JS. Most likely consumer of
the lscjfb four-tier data. Extract: rX title pairs, lscjfb call sites, tier
legend labels, any numeric thresholds. 1 request, read-only.
"""
import sys, time, json, re, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

URL = "https://n.sinaimg.cn/finance/hq2018/js/hqZhuli0612.js?ts=3.6"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
      "Referer": "https://finance.sina.com.cn/"}

op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
req = urllib.request.Request(URL, headers=UA)
t0 = time.time()
resp = op.open(req, timeout=15)
body = resp.read(3_000_000).decode("utf-8", errors="replace")
out = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "url": URL, "status": resp.status,
       "ms": int((time.time() - t0) * 1000), "bytes": len(body)}

out["mentions_lscjfb"] = "lscjfb" in body
out["mentions_MoneyFlow"] = "MoneyFlow" in body

# every rX..: { ... title: "..." } or dTitle pattern
pairs = re.findall(r'(r[0-3](?:_[a-z0-9]+)?)\s*:\s*\{[^{}]*?title\s*:\s*[\'"]([^\'"]+)', body)
pairs += re.findall(r'(r[0-3](?:_[a-z0-9]+)?)\s*:\s*\{[^{}]*?dTitle\s*:\s*[\'"]([^\'"]+)', body)
out["rX_title_pairs"] = sorted(set(pairs))

# lscjfb call site context
out["lscjfb_contexts"] = []
for m in re.finditer(r"lscjfb", body):
    seg = body[max(0, m.start() - 400):m.end() + 400].replace("\r", " ").replace("\n", " ")
    out["lscjfb_contexts"].append(seg[:800])
    if len(out["lscjfb_contexts"]) >= 4:
        break

# tier legend: labels near r0/r1/r2/r3 mentions
out["tier_label_contexts"] = []
seen = set()
for m in re.finditer(r"r[0-3]", body):
    seg = body[max(0, m.start() - 200):m.end() + 260].replace("\r", " ").replace("\n", " ")
    if re.search(r"(主力|散户|大户|中户|超大|大单|中单|小单|超大单)", seg):
        key = seg[:50]
        if key in seen:
            continue
        seen.add(key)
        out["tier_label_contexts"].append(seg[:460])
    if len(out["tier_label_contexts"]) >= 12:
        break

with open("results/_r224_bma_zhulijs_tier_map.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if not k.endswith("contexts")}, ensure_ascii=False, indent=1))
print("=== lscjfb call sites ===")
for c in out["lscjfb_contexts"][:3]:
    print("LSCJFB:", c[:500])
    print("---")
print("=== tier label contexts ===", len(out["tier_label_contexts"]))
for c in out["tier_label_contexts"][:8]:
    print("TIER:", c[:420])
    print("---")
