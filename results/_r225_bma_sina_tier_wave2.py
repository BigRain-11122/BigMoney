# -*- coding: utf-8 -*-
"""T-72 open-item 4 tier-doc wave-2 (bm-a R225) — different surface batch (R224 §3 candidate list).

Pre-registered decision matrix (frozen before any request; R109 budget discipline, cap 12):
  P1 re-fetch stock20180116.js (known 200 face, R224 r4) -> extract FULL `var moneyFlow` block
     (_drawMR/_drawFL bodies were truncated in R224 1200-char context window).
     Decision: if _drawMR/_drawFL map r0..r3 to labeled pie/bar categories -> r1/r2 semantics
     = official-JS evidence (same evidence class as R224 r0/r3 finding); record verbatim code.
  P2 direct call MoneyFlow.ssi_ssfx_flzjtj?daima=sh600519&gettime=1 (call format saved R224).
     Decision: field inventory only; labels only if response itself carries them.
  P3 mobile wap face gu.sina.cn quote page sh600519 (cap 2 URL variants).
     Decision: 200 + tier-legend hit -> evidence; 404/dead -> honest dead-surface log, no retry.
  P4 sina internal site-search face (search.sina.com.cn), legend/api terms (cap 2 queries).
     Decision: sina-owned help/blog hit -> follow at most 1; SERP-noise law (R224 r5) applies
     to external engines only — this is sina's own search = different surface.
Budget ledger: P1=1, P2=1, P3<=2, P4<=2, optional followup<=2 => total <= 8 requests.
Law refs: no-mapping law R118 (labels only, zero EM/THS mapping); PARTIAL ceiling — same-family
recognition is reasonable induction, never promoted to DOCUMENTED without API-level proof.
Zero criteria/schema/guard touches (first-pull in flight; freeze law intact).
"""
import io, json, re, ssl, time, urllib.request

OUT = "results/_r225_bma_sina_tier_wave2.json"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Referer": "https://finance.sina.com.cn/"}
CTX = ssl.create_default_context()
budget = {"spent": 0, "cap": 12}
res = {"ts_start": time.strftime("%Y-%m-%d %H:%M:%S"), "probes": [], "ledger": budget}

def fetch(url, timeout=20):
    budget["spent"] += 1
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers=UA)
        raw = urllib.request.urlopen(req, timeout=timeout, context=CTX).read()
        txt = raw.decode("utf-8", "replace")
        return {"url": url, "status": 200, "ms": int((time.time() - t0) * 1000), "bytes": len(raw), "text": txt}
    except Exception as e:
        return {"url": url, "status": "ERR", "err": repr(e)[:200], "ms": int((time.time() - t0) * 1000), "bytes": 0, "text": ""}

def strip_js_comments(s):
    return s

# ---------- P1: full moneyFlow block from stock20180116.js ----------
p1 = fetch("https://n.sinaimg.cn/finance/hq2018/js/stock20180116.js")
block = ""
if p1["status"] == 200:
    i = p1["text"].find("var moneyFlow = new function()")
    if i >= 0:
        block = p1["text"][i:i + 14000]
p1_art = {"probe": "P1", "purpose": "full moneyFlow block extraction (R224 truncation remediation)",
          "status": p1["status"], "ms": p1["ms"], "bytes": p1["bytes"], "block_found": bool(block)}
if block:
    # extraction: sentences that reference r0..r3 or tier-ish labels
    lines = [l.strip() for l in re.split(r"[;\n]", block) if re.search(r"\br[0-3]\b|主力|散户|大户|中户|机构|pie|dTitle", l)]
    p1_art["tier_sentences"] = lines[:60]
    p1_art["block_chars"] = len(block)
    io.open("results/_r225_bma_sina_tier_wave2_p1_block.txt", "w", encoding="utf-8").write(block)
res["probes"].append(p1_art)

# ---------- P2: flzjtj API direct call ----------
p2 = fetch("https://vip.stock.finance.sina.com.cn/quotes_service/api/jsonp.php/var%20moneyFlowData=/MoneyFlow.ssi_ssfx_flzjtj?daima=sh600519&gettime=1")
p2_art = {"probe": "P2", "purpose": "flzjtj (pie source API) response field inventory",
          "status": p2["status"], "ms": p2["ms"], "bytes": p2["bytes"], "body_head": p2["text"][:800]}
res["probes"].append(p2_art)

# ---------- P3: mobile wap face ----------
p3_urls = ["https://gu.sina.cn/stock/quotes/sh600519", "https://gu.sina.cn/hq/sh600519"]
p3_art = {"probe": "P3", "purpose": "mobile wap quote face tier legend", "tries": []}
for u in p3_urls:
    r = fetch(u)
    hit = ""
    if r["status"] == 200:
        for kw in ["主力", "大户", "中户", "散户", "r1", "r2", "资金流向", "净流入"]:
            if kw in r["text"]:
                hit += kw + "|"
                i = r["text"].find(kw)
                hit_ctx = r["text"][max(0, i - 80):i + 120].replace("\n", " ")
                p3_art.setdefault("hit_ctx", []).append({kw: hit_ctx})
    p3_art["tries"].append({"url": u, "status": r["status"], "bytes": r["bytes"], "kw_hits": hit.strip("|")})
    if r["status"] == 200:
        break
res["probes"].append(p3_art)

# ---------- P4: sina internal site search ----------
p4_art = {"probe": "P4", "purpose": "sina site-search face (legend terms; external SERP law does not apply to sina-own search)", "tries": []}
import urllib.parse
for q in ["lscjfb", "资金流向 大户 中户 散户"]:
    u = "https://search.sina.com.cn/?q=" + urllib.parse.quote(q) + "&c=stock"
    r = fetch(u)
    links = []
    if r["status"] == 200:
        links = re.findall(r'href="(https?://[^"]*(?:sina)[^"]*)"[^>]*>([^<]{4,60})<', r["text"])[:12]
    p4_art["tries"].append({"query": q, "status": r["status"], "bytes": r["bytes"], "candidate_links": links[:8]})
res["probes"].append(p4_art)

res["ts_end"] = time.strftime("%Y-%m-%d %H:%M:%S")
io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=1))
print("done. requests spent:", budget["spent"])
for p in res["probes"]:
    print(p["probe"], p.get("status", ""), str(p)[:200])
