"""r828 bm-b: E8 pre-flight -- per-contract sina daily kline shape probe.

One-shot: fetch a handful of specific-contract symbols across the four
families (commodity RB/AU/SC, CFFEX index IF, treasury T) and dump the RAW
endpoint payload shape (keys of first item) to decide the parser contract.
ASCII-only source (pit-encoding law). Read-only: writes nothing but stdout.
"""
import io
import json
import re
import sys
import urllib.request

RAW_URL = ("https://stock2.finance.sina.com.cn/futures/api/jsonp.php/"
           "var%20_F={sym}/InnerFuturesNewService.getDailyKLine?symbol={sym}")
SYMS = ["RB2610", "IF2610", "T2612", "AU2612", "SC2611"]


def main() -> int:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    out = {}
    for i, sym in enumerate(SYMS):
        try:
            with opener.open(RAW_URL.format(sym=sym), timeout=45) as resp:
                txt = resp.read().decode("utf-8", errors="replace")
            m = re.search(r"\(\s*(\[.*\])\s*\)", txt, re.S)
            if not m:
                out[sym] = {"ok": False, "why": "no_json_array",
                            "head": txt[:120]}
                continue
            arr = json.loads(m.group(1))
            if not arr:
                out[sym] = {"ok": False, "why": "empty_array", "head": txt[:80]}
                continue
            out[sym] = {"ok": True, "n": len(arr), "keys": sorted(arr[0].keys()),
                        "first": arr[0], "last": arr[-1]}
        except Exception as e:
            out[sym] = {"ok": False, "why": f"{type(e).__name__}: {str(e)[:120]}"}
        if i < len(SYMS) - 1:
            import time
            time.sleep(3.0)
    buf = io.StringIO()
    json.dump(out, buf, ensure_ascii=True, indent=1)
    print(buf.getvalue())
    return 0


if __name__ == "__main__":
    sys.exit(main())
