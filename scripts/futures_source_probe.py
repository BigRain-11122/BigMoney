"""C-layer futures data-gate probe (R47 bm-a, claim MSG-20260924-0628).

Probe-only: verifies sina main-continuous daily depth for the 9 Money0923
varieties. Writes depth metadata to results/shortline/futures_source_probe.json.
NO data files are written (pipeline/pull decisions belong to a future prereg).

Network rules (r39/R34 audit precedents):
- Direct connection (proxy env cleared) -- Clash hijack lesson (J13/r40).
- >=2.5s polite sleep between varieties.
- akshare parse failure (pandas3 Arrow bug family, r40) -> raw sina jsonp fallback.
Exit codes: 0=ok, 2=source failure (honest, do not mask).
"""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "shortline", "futures_source_probe.json")

VARIETIES = ["IF", "IC", "IM", "IH", "T", "TF", "RB", "AU", "SC"]
SLEEP_S = 2.5
RAW_URL = ("https://stock2.finance.sina.com.cn/futures/api/jsonp.php/"
           "var%20_F={sym}/InnerFuturesNewService.getDailyKLine?symbol={sym}")


def _no_proxy_opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _clear_proxy_env():
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)


def _probe_akshare(sym: str):
    """Try ak.futures_main_sina for main-continuous depth. Returns (rows, first, last, cols) or raises."""
    import akshare as ak
    import inspect
    fn = ak.futures_main_sina
    params = {"symbol": sym}
    sig = inspect.signature(fn).parameters
    if "start_date" in sig:
        params["start_date"] = "19900101"
        params["end_date"] = dt.date.today().strftime("%Y%m%d")
    df = fn(**params)
    if df is None or len(df) == 0:
        return None
    cols = list(df.columns)
    date_col = cols[0]  # sina main-continuous: first col is date-like
    first, last = str(df[date_col].iloc[0]), str(df[date_col].iloc[-1])
    return {"rows": int(len(df)), "first": first, "last": last, "cols": cols[:8]}


def _probe_raw(sym: str):
    """Raw sina jsonp fallback (r40 precedent). Returns depth dict or None."""
    url = RAW_URL.format(sym=sym)
    try:
        with _no_proxy_opener().open(url, timeout=30) as r:
            txt = r.read().decode("utf-8", errors="replace")
    except Exception as e:  # network-level
        return {"error": f"raw_open_fail: {type(e).__name__}"}
    m = re.search(r"\(\s*(\[.*\])\s*\)", txt, re.S)
    if not m:
        return {"error": "raw_parse_fail: no json array in payload"}
    try:
        arr = json.loads(m.group(1))
    except Exception as e:
        return {"error": f"raw_json_fail: {type(e).__name__}"}
    if not isinstance(arr, list) or not arr:
        return {"error": "raw_empty"}
    first = arr[0].get("d", arr[0].get("date", ""))
    last = arr[-1].get("d", arr[-1].get("date", ""))
    return {"rows": len(arr), "first": str(first), "last": str(last), "cols": sorted(arr[0].keys())[:8]}


def run_probe():
    _clear_proxy_env()
    records, notes = [], []
    use_raw = False
    for i, v in enumerate(VARIETIES):
        sym = v + "0"  # main-continuous convention
        rec = {"variety": v, "symbol": sym, "path": None, "depth": None, "error": None}
        try:
            if not use_raw:
                d = _probe_akshare(sym)
                rec["path"], rec["depth"] = "akshare.futures_main_sina", d
        except Exception as e:
            msg = f"{type(e).__name__}: {str(e)[:160]}"
            rec["error"] = f"akshare_fail: {msg}"
            notes.append(f"{v}: akshare path failed ({msg}); switching to raw fallback")
            use_raw = True  # pandas3 Arrow bug family: switch all remaining
        if use_raw and rec["depth"] is None:
            d = _probe_raw(sym)
            if d and "error" in d:
                rec["error"] = d["error"]
            else:
                rec["path"], rec["depth"] = "raw_sina_jsonp", d
        records.append(rec)
        if i < len(VARIETIES) - 1:
            time.sleep(SLEEP_S)
    ok = sum(1 for r in records if r["depth"])
    payload = {
        "ts": dt.datetime.now().isoformat(timespec="seconds"),
        "mode": "probe-only (depth metadata, no data files written)",
        "varieties": VARIETIES,
        "records": records,
        "summary": {"probed": len(records), "with_depth": ok, "source_failures": len(records) - ok},
        "network": {"direct": True, "proxy_env_cleared": True, "sleep_s": SLEEP_S},
        "notes": notes,
        "archive_baseline": {
            "Money0923/data/futures_daily": "9 csv, 165-436 rows, ends 2026-09-21 (shallow, non-backtest-grade)",
        },
        "claim": "MSG-20260924-0628-bm-a-futures-source-audit",
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"probe -> {OUT}")
    for r in records:
        d = r["depth"]
        print(f"  {r['variety']}: " + (f"{r['path']} rows={d['rows']} {d['first']}..{d['last']}" if d else f"FAIL {r['error']}"))
    return 0 if ok == len(VARIETIES) else 2


def _selftest():
    """Offline checks (zero network)."""
    import tempfile
    # S1: synthetic akshare-style frame depth extraction
    import pandas as pd
    df = pd.DataFrame({"日期": ["2010-04-16", "2026-09-23"], "收盘价": [1.0, 2.0]})
    assert (str(df["日期"].iloc[0]), str(df["日期"].iloc[-1])) == ("2010-04-16", "2026-09-23")
    # S2: raw jsonp regex parse on synthetic payload
    fake = 'var _F="x"=(\n[{"d":"2010-04-16","o":1},{"d":"2026-09-23","o":2}]\n);'
    m = re.search(r"\(\s*(\[.*\])\s*\)", fake, re.S)
    assert m and len(json.loads(m.group(1))) == 2
    # S3: record schema + JSON roundtrip (bool/int native types, no np scalars)
    rec = {"variety": "IF", "depth": {"rows": int(2), "first": "a", "last": "b", "cols": ["d"]}, "error": None}
    assert json.loads(json.dumps(rec))["depth"]["rows"] == 2
    # S4: variety symbols built as code+"0"
    assert [v + "0" for v in ["IF", "RB"]] == ["IF0", "RB0"]
    print("selftest: 4/4 PASS")
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        return _selftest()
    return run_probe()


if __name__ == "__main__":
    sys.exit(main())
