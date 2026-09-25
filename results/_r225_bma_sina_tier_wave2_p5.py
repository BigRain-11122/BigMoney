# -*- coding: utf-8 -*-
"""P5 follow-up (bm-a R225, T-72 tier-doc wave-2): DataDrawer/FLFlow label extraction.
Pre-registered decision: stock20180116.js (known-200 face) re-fetched ONCE to extract
`DataDrawer` class source + any FLFlow/MRFlow row-label maps + direct keyword scan for
tier-name candidates (主力/大户/中户/散户/超大/大单/中单/小单). If label map found -> official
JS evidence for r1/r2 names; if DataDrawer defined elsewhere -> record source ref honestly.
Budget: 1 request (total wave-2 = 7/12)."""
import io, json, re, ssl, time, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Referer": "https://finance.sina.com.cn/"}
url = "https://n.sinaimg.cn/finance/hq2018/js/stock20180116.js"
t0 = time.time()
raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20,
                             context=ssl.create_default_context()).read()
txt = raw.decode("utf-8", "replace")
out = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "url": url, "status": 200,
       "ms": int((time.time() - t0) * 1000), "bytes": len(raw)}

# 1) direct keyword scan (whole file)
kws = ["主力", "散户", "大户", "中户", "超大", "大单", "中单", "小单", "机构", "FLFlow", "MRFlow", "DataDrawer"]
out["keyword_counts"] = {k: txt.count(k) for k in kws}

# 2) DataDrawer class source
i = txt.find("DataDrawer")
cls = ""
m = re.search(r"(var DataDrawer\s*=|function DataDrawer\s*\()", txt)
if m:
    cls = txt[m.start():m.start() + 9000]
    out["datadrawer_found_at"] = m.start()
    io.open("results/_r225_bma_sina_tier_wave2_p5_datadrawer.txt", "w", encoding="utf-8").write(cls)

# 3) FLFlow/MRFlow label maps anywhere
flow_ctx = []
for m in re.finditer(r"FLFlow|MRFlow", txt):
    flow_ctx.append(txt[max(0, m.start() - 200):m.start() + 500].replace("\n", " "))
    if len(flow_ctx) >= 6:
        break
out["flow_ctx"] = flow_ctx

# 4) keyword contexts for tier-name candidates
tier_ctx = {}
for k in ["大户", "中户", "超大", "大单", "中单", "小单"]:
    if txt.count(k):
        j = txt.find(k)
        tier_ctx[k] = txt[max(0, j - 150):j + 200].replace("\n", " ")
out["tier_kw_ctx"] = tier_ctx

io.open("results/_r225_bma_sina_tier_wave2_p5.json", "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print("keyword_counts:", out["keyword_counts"])
print("datadrawer_found:", bool(cls), "| flow_ctx n:", len(flow_ctx))
