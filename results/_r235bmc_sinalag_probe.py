"""_r235bmc_sinalag_probe.py -- bm-c r235: sina fund-endpoint publication
lag diagnosis (T-08 dual-leg follow-up). Q: does the klc2 (akshare wrapper)
feed lag the r398 hisdata feed for the same symbol?

Findings feed the round report; zero writes to any production face.
"""
import json
import sys
import urllib.request

from py_mini_racer import MiniRacer

import akshare as ak
from akshare.stock.cons import hk_js_decode

HIS = "https://finance.sina.com.cn/realstock/company/{sym}/hisdata/klc_kl.js"
KLC2 = "https://finance.sina.com.cn/realstock/company/{sym}/hisdata_klc2/klc_kl.js"
GENERIC = ("https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20hq=/"
           "CN_MarketDataService.getKLineData?symbol={sym}&scale=240&ma=no&datalen=10")


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://finance.sina.com.cn",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def decode_klc(raw):
    txt = raw.decode("gbk", "replace")
    js = MiniRacer()
    js.eval(hk_js_decode)
    rows = js.call("d", txt.split("=")[1].split(";")[0].replace('"', ""))
    return rows


def main():
    out = {"ts": "2026-09-29 r235 probe", "symbols": {}}
    for sym in ("sh510300", "sh510050", "sz159915"):
        rec = {}
        # klc2 (akshare wrapper feed)
        try:
            rows = decode_klc(fetch(KLC2.format(sym=sym)))
            rec["klc2_tail"] = [str(rows[-1]["date"]), float(rows[-1]["close"])]
        except Exception as e:  # noqa: BLE001
            rec["klc2_err"] = f"{type(e).__name__}: {e}"[:120]
        # hisdata (r398 direct recipe feed)
        try:
            rows = decode_klc(fetch(HIS.format(sym=sym)))
            rec["hisdata_tail"] = [str(rows[-1]["date"]), float(rows[-1]["close"])]
        except Exception as e:  # noqa: BLE001
            rec["hisdata_err"] = f"{type(e).__name__}: {e}"[:120]
        # generic kline endpoint (no decode)
        try:
            txt = fetch(GENERIC.format(sym=sym)).decode("utf-8", "replace")
            import re
            m = re.search(r"\[.*\]", txt, __import__("re").S)
            data = json.loads(m.group(0)) if m else []
            rec["generic_tail"] = [data[-1].get("day"), float(data[-1].get("close"))]
        except Exception as e:  # noqa: BLE001
            rec["generic_err"] = f"{type(e).__name__}: {e}"[:120]
        out["symbols"][sym] = rec
        print(sym, json.dumps(rec, ensure_ascii=False))
    with open("results/_r235bmc_sinalag_probe.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("-> results/_r235bmc_sinalag_probe.json")


if __name__ == "__main__":
    sys.exit(main())
