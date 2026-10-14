"""r997 probe: does the sina daily source actually carry the 2026-10-14 bar?
Honest check - direct raw endpoint pull for 510300 + one equity, print tail dates.
"""
import urllib.request, re, json, datetime

def probe(code):
    url = "https://quotes.sina.cn/cn/api/jsonp_v2.php/var%%20_=/CN_MarketDataService.getKLineData?symbol=%s&scale=240&ma=no&datalen=12" % code
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"})
    raw = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
    m = re.search(r"\((\[.*\])\)", raw, re.S)
    if not m:
        return {"code": code, "ok": False, "raw_head": raw[:120]}
    data = json.loads(m.group(1))
    return {"code": code, "ok": True, "n": len(data),
            "tail": [(d.get("day"), d.get("close")) for d in data[-4:]]}

out = {"ts": datetime.datetime.now().isoformat(timespec="seconds"), "probes": []}
for c in ("sh510300", "sh510050"):
    try:
        out["probes"].append(probe(c))
    except Exception as e:
        out["probes"].append({"code": c, "ok": False, "err": str(e)[:200]})
open(r"results\_r997bma_daily_source_probe.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps(out, ensure_ascii=False)[:800])
