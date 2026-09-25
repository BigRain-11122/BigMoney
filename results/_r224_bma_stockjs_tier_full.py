"""T-72 refine-3: full r0..r3 title extraction from stock20180116.js (MoneyFlow hit).

r3 hit MoneyFlow+主力+散户 but no r1/r2 labels extracted yet (context filter too
narrow). This probe re-fetches the one JS and extracts exhaustively:
  (a) every rX[...]: { ... title: "..." } pair (utils-hq.js config pattern)
  (b) every +-300char context around MoneyFlow (API call site -- may reveal
      query params + field semantics used by sina's own frontend)
  (c) every context around 主力/散户/中户/大户 carrying any digit+元/万 pattern
1 request, read-only, zero state.
"""
import sys, time, json, re, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

URL = "https://n.sinaimg.cn/finance/hq2018/js/stock20180116.js?ts=3.6"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
      "Referer": "https://finance.sina.com.cn/"}

op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
req = urllib.request.Request(URL, headers=UA)
t0 = time.time()
resp = op.open(req, timeout=15)
body = resp.read(3_000_000).decode("utf-8", errors="replace")
out = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "url": URL, "status": resp.status,
       "ms": int((time.time() - t0) * 1000), "bytes": len(body)}

pairs = re.findall(r'(r[0-3](?:_[a-z0-9]+)?)\s*:\s*\{[^{}]*?title\s*:\s*"([^"]+)"', body)
out["rX_title_pairs"] = sorted(set(pairs))

out["moneyflow_contexts"] = []
for m in re.finditer(r"MoneyFlow", body):
    seg = body[max(0, m.start() - 350):m.end() + 350].replace("\r", " ").replace("\n", " ")
    out["moneyflow_contexts"].append(seg[:700])
    if len(out["moneyflow_contexts"]) >= 6:
        break

out["investor_class_contexts"] = []
seen = set()
for m in re.finditer(r"(主力|散户|中户|大户)", body):
    seg = body[max(0, m.start() - 160):m.end() + 220].replace("\r", " ").replace("\n", " ")
    key = seg[:60]
    if key in seen:
        continue
    seen.add(key)
    if re.search(r"(\d+(\.\d+)?\s*(万|亿)?元?)", seg):
        out["investor_class_contexts"].append(seg[:380])
    if len(out["investor_class_contexts"]) >= 10:
        break

with open("results/_r224_bma_stockjs_tier_full.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("moneyflow_contexts", "investor_class_contexts")}, ensure_ascii=False, indent=1))
print("=== moneyflow contexts ===")
for c in out["moneyflow_contexts"][:4]:
    print("MF:", c[:400])
    print("---")
print("=== investor contexts ===", len(out["investor_class_contexts"]))
for c in out["investor_class_contexts"][:5]:
    print("INV:", c[:300])
    print("---")
