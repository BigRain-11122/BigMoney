"""r831 bm-b: T20 fix evidence probe -- digest key-position lines + live raw shape re-verify.

Read-only: prints matching digest lines, then (network) re-checks the raw sina
endpoint key semantics for OI (position volume) vs open price. ASCII source law.
"""
import io
import json
import re
import sys

t = io.open(r"research\digests\DIGEST-20261010-e8-futures-calendar-spread.md",
            encoding="utf-8").read()
for ln in t.splitlines():
    if ('"p"' in ln) or ("持仓" in ln) or ("键位" in ln):
        print(json.dumps(ln, ensure_ascii=True)[:420])

# live re-verify: one commodity + one index contract raw shape
RAW_URL = ("https://stock2.finance.sina.com.cn/futures/api/jsonp.php/"
           "var%20_F={sym}/InnerFuturesNewService.getDailyKLine?symbol={sym}")
import urllib.request
import time
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
for sym in ("RB2701", "IF2612"):
    try:
        with opener.open(RAW_URL.format(sym=sym), timeout=45) as resp:
            txt = resp.read().decode("utf-8", errors="replace")
        m = re.search(r"\(\s*(\[.*\])\s*\)", txt, re.S)
        arr = json.loads(m.group(1))
        last = arr[-1]
        print(json.dumps({"sym": sym, "keys": sorted(last.keys()), "last": last},
                         ensure_ascii=True)[:520])
    except Exception as e:
        print(json.dumps({"sym": sym, "err": f"{type(e).__name__}: {e}"[:160]},
                         ensure_ascii=True))
    time.sleep(2.5)
sys.exit(0)
