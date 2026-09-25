"""T-71 slice (R216): freshness FALSIFICATION probe -- date-sorted query (R215 mask-trap remedy).

R215 could not falsify freshness within budget: netamount-desc top-N is a masked read
(date_max only a lower bound; near-window silent days never enter top-N). This slice
uses sort=opendate&asc=0 (date-desc) so row0.opendate IS the endpoint's freshest date
for that stock -- a direct falsifier.

Decision matrix (budget <=2, R109 abstinence; every request counted):
  r1: daima=sh600519 sort=opendate asc=0
    - rows strictly date-desc => sort honored (unmasked read)
    - r2 conditional:
        fresh  (row0 >= 2026-09-24) => second stock hardening (sh601398)
        stale  (row0 <  2026-09-24) => second stock to separate endpoint-frozen vs stock-specific
        parse-fail/Input error                  => alternative-param retry (drop fenlei / sort=trade)
Freshness gate: latest completed bar day = 2026-09-24 (2026-09-25 Mid-Autumn holiday,
panel cutoff 09-24 per R213/R214; next bar 09-28).
Probe only: no panel writes, no collector code, zero engine contact.
"""
import sys, time, json, ast, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Referer": "https://finance.sina.com.cn/"}
BASE = ("https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/"
        "MoneyFlow.ssl_qsfx_lscjfb")
LATEST_BAR_DAY = "2026-09-24"

out = {
    "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
    "probe": "T-71 freshness falsification (date-sorted query, R215 mask-trap remedy)",
    "budget": 2,
    "requests_consumed": 0,
    "gate": {"latest_bar_day": LATEST_BAR_DAY, "note": "2026-09-25 Mid-Autumn market holiday; panel cutoff 09-24 (R213/R214); next bar 09-28"},
    "probes": {},
}


def fetch(name, url):
    t0 = time.time()
    try:
        resp = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=15)
        body = resp.read(200000).decode("utf-8", errors="replace")
        ms = int((time.time() - t0) * 1000)
        rows = ast.literal_eval(body) if body.lstrip().startswith("[") else None
        rec = {"status": resp.status, "ms": ms, "url_query": url.split("MoneyFlow.ssl_qsfx_lscjfb")[-1]}
        if not rows:
            rec["parse"] = "fail"
            rec["head"] = body[:160]
        else:
            dates = [str(r.get("opendate", "")) for r in rows]
            desc = all(dates[i] >= dates[i + 1] for i in range(len(dates) - 1))
            rec.update({
                "parse": "ok", "rows": len(rows),
                "row0_opendate": dates[0], "date_min": min(dates), "date_max": max(dates),
                "date_desc_monotone": desc,
                "row0": {k: rows[0][k] for k in list(rows[0])[:14]},
            })
        return rec
    except Exception as e:
        return {"error": type(e).__name__, "detail": str(e)[:160], "ms": int((time.time() - t0) * 1000)}


# r1: 600519 date-sorted
r1 = fetch("r1_600519_date_desc", BASE + "?page=1&num=5&sort=opendate&asc=0&fenlei=1&daima=sh600519")
out["requests_consumed"] += 1
out["probes"]["r1_600519_date_desc"] = r1
print("r1:", json.dumps(r1, ensure_ascii=False)[:300])

# decision matrix -> r2 (single conditional request)
r2_name, r2_url, r2_why = None, None, None
if r1.get("parse") == "ok" and r1.get("date_desc_monotone"):
    if r1["row0_opendate"] >= LATEST_BAR_DAY:
        r2_name, r2_why = "r2_601398_fresh_hardening", "r1 fresh -> second-stock confirmation (endpoint-level freshness)"
        r2_url = BASE + "?page=1&num=5&sort=opendate&asc=0&fenlei=1&daima=sh601398"
    else:
        r2_name, r2_why = "r2_601398_stale_discriminator", "r1 stale -> second stock separates endpoint-frozen vs stock-specific"
        r2_url = BASE + "?page=1&num=5&sort=opendate&asc=0&fenlei=1&daima=sh601398"
else:
    r2_name, r2_why = "r2_alt_param_retry", "r1 parse-fail/not-date-sorted -> alternative param face (drop fenlei, sort=trade)"
    r2_url = BASE + "?page=1&num=5&sort=opendate&asc=0&daima=sh600519"
out["r2_rationale"] = r2_why

r2 = fetch(r2_name, r2_url)
out["requests_consumed"] += 1
out["probes"][r2_name] = r2
print("r2:", json.dumps(r2, ensure_ascii=False)[:300])

# verdict (byte-honest)
fresh_dates = {}
for k, p in out["probes"].items():
    if p.get("parse") == "ok" and p.get("date_desc_monotone"):
        fresh_dates[k] = p["row0_opendate"]
if len(fresh_dates) >= 2 and all(d >= LATEST_BAR_DAY for d in fresh_dates.values()):
    verdict = "FRESH: endpoint carries rows through latest bar day 2026-09-24 (two stocks, date-sorted unmasked reads) -> freshness gate PASSED, candidate remains QUALIFIED; next slice = prereg draft (MF_COLLECTOR section-8 family cross-source dual-face candidate)"
elif len(fresh_dates) >= 2 and all(d < LATEST_BAR_DAY for d in fresh_dates.values()):
    verdict = "STALE: freshest dates %s < latest bar day on both stocks (date-sorted unmasked reads) -> endpoint frozen; candidate CLOSED honest-negative" % json.dumps(fresh_dates)
elif fresh_dates:
    verdict = "MIXED/INCONCLUSIVE: unmasked reads %s -- record honestly, no admission" % json.dumps(fresh_dates)
else:
    verdict = "UNDETERMINED: no clean date-sorted read within budget (parse-fail or not date-monotone) -- honest close, next budget window may retry with alternative sort face"
out["verdict"] = verdict
print("VERDICT:", verdict)

json.dump(out, open("results/_r216_sina_mf_freshness.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved -> results/_r216_sina_mf_freshness.json")
