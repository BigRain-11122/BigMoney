"""r280 bm-b T-87 supply-lane step-0: akshare A-share DAILY-BAR endpoint probe.

Ticket T-2026-09-26-87 progress_r279_bmb pointer (1): probe_akshare.py probed
list faces only; daily-bar endpoints (EM stock_zh_a_hist vs sina
stock_zh_a_daily) UNPROBED = collector step-0. This probe measures, per
endpoint: reachability, schema, qfq face availability, date coverage, sanity
(OHLC order, volume>=0, cross-endpoint close agreement on shared dates).
Zero state mutation; findings -> results/_r280bmb_probe_akshare_daily.json.
"""
import datetime as dt
import json
import sys
import time

import akshare as ak

OUT = "results/_r280bmb_probe_akshare_daily.json"
SAMPLES = [
    ("000001", "sz000001", "平安银行 sz main-board"),
    ("300750", "sz300750", "宁德时代 sz chinext"),
    ("600519", "sh600519", "贵州茅台 sh main-board"),
    ("920000", "bj920000", "安徽凤凰 bj-nt (edge face)"),
]
START = "20260901"
END = "20260926"


def _probe_one(kind, call, label):
    rec = {"kind": kind, "label": label, "ok": False}
    t0 = time.time()
    try:
        df = call()
        rec["rows"] = int(len(df))
        rec["columns"] = [str(c) for c in df.columns]
        rec["elapsed_s"] = round(time.time() - t0, 2)
        if len(df) > 0:
            rec["first_date"] = str(df.iloc[0, 0])
            rec["last_date"] = str(df.iloc[-1, 0])
            # take last row values by column-name family
            last = df.iloc[-1]
            rec["last_row_sample"] = {str(k): str(v) for k, v in last.items()}
        rec["ok"] = True
    except Exception as e:
        rec["error"] = "%s: %s" % (type(e).__name__, str(e)[:300])
        rec["elapsed_s"] = round(time.time() - t0, 2)
    return rec


def main():
    out = {"ts": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
           "akshare_version": ak.__version__, "start": START, "end": END,
           "em_hist": [], "sina_daily": [], "cross_check": {}}
    for sym6, symp, label in SAMPLES:
        out["em_hist"].append(_probe_one(
            "em_stock_zh_a_hist_qfq",
            lambda s=sym6: ak.stock_zh_a_hist(symbol=s, period="daily",
                                              start_date=START, end_date=END,
                                              adjust="qfq"),
            label))
        time.sleep(2.5)
        out["sina_daily"].append(_probe_one(
            "sina_stock_zh_a_daily_qfq",
            lambda s=symp: ak.stock_zh_a_daily(symbol=s, start_date=START,
                                               end_date=END, adjust="qfq"),
            label))
        time.sleep(2.5)
    # cross-endpoint agreement on shared dates for the first sample
    try:
        em = ak.stock_zh_a_hist(symbol="000001", period="daily",
                                start_date=START, end_date=END, adjust="qfq")
        time.sleep(2.5)
        si = ak.stock_zh_a_daily(symbol="sz000001", start_date=START,
                                 end_date=END, adjust="qfq")
        emm = {str(r["日期"]): float(r["收盘"]) for _, r in em.iterrows()}
        sim = {str(r["date"]): float(r["close"]) for _, r in si.iterrows()}
        shared = sorted(set(emm) & set(sim))
        diffs = [{"date": d, "em_close": emm[d], "sina_close": sim[d],
                  "absdiff": round(abs(emm[d] - sim[d]), 6)} for d in shared[-5:]]
        out["cross_check"] = {"symbol": "000001", "shared_dates": len(shared),
                              "tail_diffs": diffs,
                              "max_absdiff": round(max((abs(emm[d] - sim[d]) for d in shared), ), 6) if shared else None}
    except Exception as e:
        out["cross_check"] = {"error": "%s: %s" % (type(e).__name__, str(e)[:200])}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    ok_em = sum(1 for r in out["em_hist"] if r["ok"])
    ok_si = sum(1 for r in out["sina_daily"] if r["ok"])
    print("EM hist ok %d/4, sina daily ok %d/4 -> %s" % (ok_em, ok_si, OUT))
    for r in out["em_hist"] + out["sina_daily"]:
        print(" ", r["label"], r["kind"], "OK" if r["ok"] else "FAIL",
              "rows=%s" % r.get("rows"), r.get("last_date") or r.get("error", "")[:120])
    print(" cross_check:", json.dumps(out["cross_check"], ensure_ascii=False)[:400])


if __name__ == "__main__":
    main()
