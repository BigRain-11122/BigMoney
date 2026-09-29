"""_r235bmc_sinalag_parity.py -- bm-c r235: klc2 vs hisdata full-history
parity check (fallback-leg safety evidence). Compares decoded rows on 3
symbols: row count, per-column exact equality on the overlap window,
amount-column presence. Writes results/_r235bmc_sinalag_parity.json.
"""
import json
import urllib.request

from py_mini_racer import MiniRacer

from akshare.stock.cons import hk_js_decode

HIS = "https://finance.sina.com.cn/realstock/company/{sym}/hisdata/klc_kl.js"
KLC2 = "https://finance.sina.com.cn/realstock/company/{sym}/hisdata_klc2/klc_kl.js"
COLS = ("date", "open", "high", "low", "close", "volume", "amount")


def fetch_rows(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"})
    with urllib.request.urlopen(req, timeout=25) as r:
        txt = r.read().decode("gbk", "replace")
    js = MiniRacer()
    js.eval(hk_js_decode)
    return js.call("d", txt.split("=")[1].split(";")[0].replace('"', ""))


def norm(row):
    out = {}
    for c in COLS:
        v = row.get(c)
        out[c] = str(v)[:10] if c == "date" else str(v)
    return out


def main():
    report = {}
    for sym in ("sh510300", "sh510050", "sz159915"):
        a = fetch_rows(KLC2.format(sym=sym))   # akshare/update_daily primary
        b = fetch_rows(HIS.format(sym=sym))    # r398 direct recipe
        nb, na = norm(b[-1]), norm(a[-1])
        rec = {
            "klc2_rows": len(a), "hisdata_rows": len(b),
            "klc2_tail_date": na["date"], "hisdata_tail_date": nb["date"],
            "hisdata_amount_col_present": "amount" in b[-1],
            "hisdata_amount_tail": nb.get("amount"),
        }
        # overlap window = dates present in both (keyed by date prefix)
        amap = {str(r["date"])[:10]: norm(r) for r in a}
        bmap = {str(r["date"])[:10]: norm(r) for r in b}
        common = sorted(set(amap) & set(bmap))
        diffs = []
        for d in common[-500:]:  # recent 500 overlap rows, exact per-column
            ra, rb = amap[d], bmap[d]
            for c in COLS:
                if ra[c] != rb[c]:
                    diffs.append([d, c, ra[c], rb[c]])
        rec["overlap_rows_checked"] = min(500, len(common))
        rec["overlap_col_diffs"] = len(diffs)
        rec["diff_samples"] = diffs[:5]
        report[sym] = rec
        print(sym, json.dumps(rec, ensure_ascii=False)[:260])
    with open("results/_r235bmc_sinalag_parity.json", "w", encoding="utf-8") as f:
        json.dump({"ts": "2026-09-29 r235", "report": report}, f, ensure_ascii=False, indent=1)
    print("-> results/_r235bmc_sinalag_parity.json")


if __name__ == "__main__":
    main()
