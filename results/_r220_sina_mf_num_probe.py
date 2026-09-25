"""T-72 s2 deliverable: sina lscjfb num ceiling probe (prereg S5 open-item-1).

Freeze path per SINA_MF_PREREG.md section-5: "num 精确上限（>=100 已证，ceiling
未测）-> 首拉实测冻结回看窗参数". Read-only probe, zero panel writes, zero state
mutation. Recipe mirror = collector frozen face (direct urllib, no-proxy opener,
UA+Referer, page=1, sort=opendate&asc=0 date-sorted read per R216 law -- masked
netamount sort forbidden for any depth/freshness conclusion).

Ladder design (<=3 requests, R109 abstinence):
  r1 num=600  on sh600519: rows==100 -> server caps at 100 EXACT (freeze done);
               rows==600 -> ceiling >=600, escalate.
  r2 num=2500: rows==2500 -> ceiling >=2500 (>=10.3y, beyond practical need);
               rows<2500 -> history-limited vs cap disambiguated by earliest
               opendate (data-start face) -- practical freeze = full available
               history reachable in a single request.
  r3 conditional refine only if r1 returns an ambiguous middle value.
Row count ambiguity law: returned rows = min(num_param, server_cap, history_len)
-- never attribute a history boundary to a server cap without the earliest-date
face (R215 masking-trap family discipline).
"""
import sys, time, json, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

BASE = ("https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/"
        "MoneyFlow.ssl_qsfx_lscjfb")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
      "Referer": "https://finance.sina.com.cn/"}
DAIMA = "sh600519"   # deep-history stock (R215 masked read saw data back to 2018-10-30)


def opener():
    # collector frozen face: registry proxies defeat env clearing (digest T4)
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def fetch_num(op, num_val):
    url = f"{BASE}?page=1&num={num_val}&sort=opendate&asc=0&fenlei=1&daima={DAIMA}"
    t0 = time.time()
    req = urllib.request.Request(url, headers=UA)
    resp = op.open(req, timeout=15)
    body = resp.read(2_000_000).decode("utf-8", errors="replace")
    ms = int((time.time() - t0) * 1000)
    rows = json.loads(body) if body.lstrip().startswith("[") else None
    out = {"num_param": num_val, "status": resp.status, "ms": ms,
           "bytes": len(body), "rows": len(rows) if isinstance(rows, list) else None}
    if isinstance(rows, list) and rows:
        dates = [r.get("opendate") for r in rows if isinstance(r, dict) and r.get("opendate")]
        out["date_max"] = max(dates)
        out["date_min"] = min(dates)
        # self-collapse law spot check (same body, zero extra requests)
        worst = 0.0
        for r in rows:
            try:
                diff = abs(float(r["netamount"]) - sum(float(r[f"r{i}_net"]) for i in range(4)))
                worst = max(worst, diff)
            except (KeyError, ValueError, TypeError):
                pass
        out["collapse_worst_abs_diff"] = worst
        out["collapse_law"] = "exact" if worst < 1e-3 else f"VIOLATION worst={worst}"
    return out


results = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "ticket": "T-2026-09-26-72",
           "probe": "num_ceiling_freeze", "daima": DAIMA,
           "sort_face": "opendate asc=0 (date-sorted, R216 law; masked sort forbidden)",
           "requests_consumed": 0, "ladder": {}, "verdict": {}}

op = opener()
# r1: num=600
r1 = fetch_num(op, 600)
results["requests_consumed"] += 1
results["ladder"]["r1_num600"] = r1
print("r1 num=600:", json.dumps(r1, ensure_ascii=False))

if r1["rows"] == 100:
    results["verdict"] = {
        "ceiling_exact": 100,
        "finding": "server caps rows at 100 regardless of num param (num=600 -> 100 rows)",
        "freeze": ("collector num=100 IS the ceiling; lookback window ~100td is the "
                   "single-request maximum; deeper history NOT reachable via num "
                   "(page-face exists but = separate request economics, out of prereg scope)"),
        "status": "FROZEN",
    }
elif r1["rows"] == 600:
    # r2: num=2500 escalation
    time.sleep(2.5)
    r2 = fetch_num(op, 2500)
    results["requests_consumed"] += 1
    results["ladder"]["r2_num2500"] = r2
    print("r2 num=2500:", json.dumps(r2, ensure_ascii=False))
    if r2["rows"] == 2500:
        results["verdict"] = {
            "ceiling_exact": None, "ceiling_lower_bound": 2500,
            "finding": "num=2500 returns 2500 rows -- ceiling >=2500td (~10.3y), beyond any practical lookback need",
            "freeze": "single-request lookback practically unbounded for design purposes; deep backfill re-pull = future prereg amendment option (5222 req budget note), current pull stays frozen num=100",
            "status": "FROZEN-at-lower-bound",
        }
    else:
        # history-limited vs cap: earliest-date face disambiguates
        results["verdict"] = {
            "ceiling_exact": None,
            "finding": f"num=2500 returned {r2['rows']} rows, earliest {r2.get('date_min')} -- history-limited face (data start ~{r2.get('date_min')}) or cap; r1 num=600 returned full 600 rows proves ceiling >=600",
            "freeze": "full available history (~{rows}td) reachable in a single request; ceiling strictly >=600 proven, >=2500 unproven (history exhausted first)".replace("{rows}", str(r2["rows"])),
            "status": "FROZEN-practical",
        }
else:
    # ambiguous middle value (101..599): history boundary or odd cap
    results["verdict"] = {
        "ceiling_exact": None,
        "finding": f"num=600 returned {r1['rows']} rows, earliest {r1.get('date_min')} -- r1 ladder returned mid-value, refine needed before freeze",
        "freeze": None,
        "status": "AMBIGUOUS-needs-refine",
    }

with open("results/_r220_sina_mf_num_probe.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("saved -> results/_r220_sina_mf_num_probe.json")
print("VERDICT:", json.dumps(results["verdict"], ensure_ascii=False))
