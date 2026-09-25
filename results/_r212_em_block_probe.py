"""R212 diagnostic: characterize EM push2 block (mf rank lane blocked since 09-25 01:50).

Probe only — no panel writes, no state mutation. Purpose: evidence for whether
the block is (a) whole-domain EM, (b) push2-specific, (c) proxy/network-local.
"""
import sys, time, json, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

probes = [
    ("push2.clist.pn1", "https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=5&po=1&fid=f3&fs=m:0+t:6&fields=f12,f14", True),
    ("push2.host.root", "https://push2.eastmoney.com/", False),
    ("emappdata.heat", "https://emappdata.eastmoney.com/stockrank/getAllCurrentList", False),
    ("datacenter-web", "https://datacenter-web.eastmoney.com/api/data/v1/get", False),
    ("quote.eastmoney", "https://quote.eastmoney.com/", False),
]

results = {}
for name, url, is_rank in probes:
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers=UA)
        resp = urllib.request.urlopen(req, timeout=10)
        body = resp.read(300)
        ok = resp.status
        head = body[:80].decode("utf-8", errors="replace").replace("\n", " ")
        results[name] = {"status": ok, "ms": int((time.time() - t0) * 1000), "head": head}
        print(f"{name}: HTTP {ok} {results[name]['ms']}ms | {head}")
    except Exception as e:
        results[name] = {"error": type(e).__name__, "detail": str(e)[:120], "ms": int((time.time() - t0) * 1000)}
        print(f"{name}: FAIL {type(e).__name__}: {str(e)[:100]} | {results[name]['ms']}ms")

with open("results/_r212_em_block_probe.json", "w", encoding="utf-8") as f:
    json.dump({"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "probes": results}, f, ensure_ascii=False, indent=1)
print("saved -> results/_r212_em_block_probe.json")
