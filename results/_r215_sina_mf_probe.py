"""T-71 probe: sina per-stock moneyflow folklore endpoint family (vip.stock.finance).

Probe only -- no panel writes, no state mutation, no collector code. Verdict faces
per R212 registration discipline: (1) liveness (2) dimension (byte-honest field
capture, aggregate-only = NOT 主力 decomposition => candidate dead for rank-lane
replacement, no mapping fabrication per R118 measure-level honesty law) (3)
economics. Request budget: <=3 (R109 diagnostic abstinence).
"""
import sys, time, json, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://finance.sina.com.cn/",
}

BASE = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/MoneyFlow.ssl_qsfx_lscjfb"

probes = [
    # r1: list/rank face liveness + field structure + sort-by-netamount viability
    ("list_rank_face", BASE + "?page=1&num=5&sort=netamount&asc=0&fenlei=1"),
    # r2: per-stock filter falsification (folklore daima param)
    ("per_stock_filter", BASE + "?page=1&num=5&sort=netamount&asc=0&fenlei=1&daima=sh600519"),
]

results = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "requests_consumed": 0, "probes": {}}


def fetch(name, url):
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers=UA)
        resp = urllib.request.urlopen(req, timeout=12)
        body = resp.read(8000).decode("utf-8", errors="replace")
        ms = int((time.time() - t0) * 1000)
        results["requests_consumed"] += 1
        out = {"status": resp.status, "ms": ms, "bytes_head": len(body)}
        # sina json_v2 returns JS-ish array (possibly with null literal); attempt parse
        parsed, perr = None, None
        try:
            parsed = json.loads(body.replace("null", "None").replace("\\/", "/")) if body.lstrip().startswith("[") else None
            if parsed is None:
                import ast
                parsed = ast.literal_eval(body) if body.lstrip().startswith("[") else None
        except Exception as e:
            perr = f"{type(e).__name__}: {str(e)[:80]}"
        out["parse"] = "ok" if parsed is not None else f"fail({perr})"
        if parsed:
            out["rows"] = len(parsed)
            if len(parsed) and isinstance(parsed[0], dict):
                out["fields"] = sorted(parsed[0].keys())
                out["row0"] = {k: parsed[0][k] for k in list(parsed[0])[:14]}
                syms = [r.get("symbol") or r.get("code") for r in parsed]
                out["symbols"] = syms
        else:
            out["head"] = body[:220].replace("\n", " ")
        results["probes"][name] = out
        print(f"{name}: HTTP {out['status']} {ms}ms parse={out['parse']} rows={out.get('rows')}")
        if "fields" in out:
            print("  fields:", ",".join(out["fields"]))
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        results["requests_consumed"] += 1
        results["probes"][name] = {"error": type(e).__name__, "detail": str(e)[:160], "ms": ms}
        print(f"{name}: FAIL {type(e).__name__}: {str(e)[:120]} | {ms}ms")


for name, url in probes:
    fetch(name, url)

# dimension verdict (byte-honest from observed field names only)
fields = results["probes"].get("list_rank_face", {}).get("fields") or []
DECOMP_KEYS = [k for k in fields if any(w in str(k).lower() for w in ("superlarge", "超大", "大单", "large", "main", "主力", "zzc", "cje"))]
verdict = {
    "liveness": "alive" if any(p.get("status") == 200 for p in results["probes"].values()) else "dead",
    "decomposition_keys_observed": DECOMP_KEYS,
    "dimension": "decomposition_present" if DECOMP_KEYS else ("aggregate_or_quote_fields_only" if fields else "unparsed_or_dead"),
    "measure_level_law": "aggregate-only = NOT 主力 decomposition; mapping onto 主力 semantics forbidden (R118 law)",
    "economics_note": f"list face num=5/page; full-universe 5222 est ~{(-(-5222 // 5))} pages/day at num=5 (vs clist 60 req/day) if per-stock absent; per-stock face economics measured at r2",
}
results["verdict"] = verdict

with open("results/_r215_sina_mf_probe.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("saved -> results/_r215_sina_mf_probe.json")
print("VERDICT:", json.dumps(verdict, ensure_ascii=False))
