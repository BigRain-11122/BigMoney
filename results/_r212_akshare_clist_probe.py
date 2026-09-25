"""R212 probe-3: akshare-canonical clist recipe test (1 request).

Question: does akshare's stock_individual_fund_flow_rank (same clist endpoint,
akshare's own param/header recipe incl. ut token) also fail? If yes -> block is
recipe-independent (server-side path death), evidence closed. If no -> diff
akshare's recipe vs ours = candidate unblock (param/header fix within signed lane).
"""
import sys, json, time, inspect
sys.stdout.reconfigure(encoding="utf-8")
out = {"ts": time.strftime("%Y-%m-%d %H:%M:%S")}

try:
    import akshare as ak
    out["akshare_version"] = getattr(ak, "__version__", "?")
    # source introspection first (R118 discipline: introspect before network)
    try:
        src = inspect.getsource(ak.stock_individual_fund_flow_rank)
        out["rank_fn_found"] = True
        import re
        urls = re.findall(r"https?://[^\s\"']+", src)
        out["rank_fn_urls"] = sorted(set(urls))
        # extract ut/params lines
        keep = [l.strip() for l in src.splitlines() if "ut" in l or "params" in l.lower() or "fltt" in l][:10]
        out["rank_fn_param_lines"] = keep
    except Exception as e:
        out["rank_fn_introspect_error"] = str(e)[:120]
    # the live probe: one call
    t0 = time.time()
    try:
        df = ak.stock_individual_fund_flow_rank(indicator="今日")
        out["live_call"] = {"ok": True, "rows": len(df), "ms": int((time.time()-t0)*1000),
                            "cols": list(df.columns)[:12]}
    except Exception as e:
        out["live_call"] = {"ok": False, "err": f"{type(e).__name__}: {str(e)[:140]}",
                            "ms": int((time.time()-t0)*1000)}
except Exception as e:
    out["akshare_import_error"] = str(e)[:160]

print(json.dumps(out, ensure_ascii=False, indent=1))
with open("results/_r212_akshare_clist_probe.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("saved -> results/_r212_akshare_clist_probe.json")
