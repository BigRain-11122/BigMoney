"""T-71 probe r3 (final budget request 3/3): num ceiling + data freshness verdict.

lscjfb = per-stock face (daima mandatory, r1 Input-error proof). Viability gate for
the collector-lane candidate: does the endpoint carry rows through the latest
completed bar day? num=100 tests history depth per request + date coverage.
"""
import sys, time, json, ast, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Referer": "https://finance.sina.com.cn/"}
url = ("https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/"
       "MoneyFlow.ssl_qsfx_lscjfb?page=1&num=100&sort=netamount&asc=0&fenlei=1&daima=sh600519")

t0 = time.time()
try:
    resp = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=15)
    body = resp.read(200000).decode("utf-8", errors="replace")
    ms = int((time.time() - t0) * 1000)
    rows = ast.literal_eval(body) if body.lstrip().startswith("[") else None
    if not rows:
        raise ValueError(f"unparsed: {body[:120]}")
    dates = sorted(str(r.get("opendate", "")) for r in rows)
    # tier-sum self-consistency law across all rows (dimension hardening)
    worst = 0.0
    for r in rows:
        try:
            s = sum(float(r.get(f"r{k}_net", 0) or 0) for k in range(4))
            worst = max(worst, abs(s - float(r.get("netamount", 0))))
        except (TypeError, ValueError):
            worst = float("inf")
    out = {
        "status": resp.status, "ms": ms, "rows": len(rows),
        "date_min": dates[0], "date_max": dates[-1],
        "tier_sum_vs_netamount_worst_abs_diff": worst,
        "fresh_through_latest_bar_day": dates[-1] >= "2026-09-24",
        "sample_fields": sorted(rows[0].keys()),
    }
    print(json.dumps(out, ensure_ascii=False, indent=1))
except Exception as e:
    out = {"error": type(e).__name__, "detail": str(e)[:160], "ms": int((time.time() - t0) * 1000)}
    print(json.dumps(out, ensure_ascii=False))

d = json.load(open("results/_r215_sina_mf_probe.json", encoding="utf-8"))
d["probes"]["num_ceiling_freshness"] = out
d["requests_consumed"] = 3
json.dump(d, open("results/_r215_sina_mf_probe.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("merged -> results/_r215_sina_mf_probe.json")
