# -*- coding: utf-8 -*-
"""r1027 bm-a: moneyflow source-block diagnosis (read-only network probe).

Context: results/moneyflow_update_status.json shows refresh source-blocked
(connection-level) since 2026-10-14T19:46 (fetch_one RemoteDisconnected x3
-> conn fuse) and rank face fetch_failed page 1 at 05:15:31 (RemoteDisconnected).
Panel cutoff frozen at 2026-10-13, complete=false -> MF-IC-P1 batch legally
waiting. This probe classifies the block: endpoint-specific / UA-specific /
param-specific / EM-wide. Read-only: zero writes to any data face.

Probe legs (throttled 2.5s, total ~9 requests):
  L1 rank-exact        : replicate fetch_rank_one_page request verbatim
  L2 fflow-exact       : replicate fetch_one request verbatim (secid 0.000001)
  L3 rank-no-referer    : rank without Referer header
  L4 rank-modern-ua    : rank with Chrome/131 UA
  L5 fflow-modern-ua   : fflow with Chrome/131 UA
  L6 fflow-no-ut       : fflow without ut token
  L7 ctrl-quote        : push2 quote snapshot (different path, same host family)
  L8 ctrl-https-root   : https://push2his.eastmoney.com/ root TLS+HTTP probe
"""
import json
import time
import ssl
import urllib.request
import urllib.error
import datetime

OUT = "results/_r1027bma_mf_source_diag.json"
THROTTLE = 2.5

UA_OLD = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36")
UA_MODERN = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
UT = "b2884a393a59ad64002292a3e90d46a5"


def opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def probe(name, url, headers, timeout=15):
    t0 = time.time()
    rec = {"leg": name, "url": url[:110], "ok": False, "status": None,
           "bytes": 0, "ms": None, "err": None, "sample": None}
    try:
        req = urllib.request.Request(url, headers=headers)
        with opener().open(req, timeout=timeout) as resp:
            body = resp.read()
            rec["ok"] = True
            rec["status"] = resp.status
            rec["bytes"] = len(body)
            try:
                txt = body[:200].decode("utf-8", errors="replace")
                rec["sample"] = txt[:120]
            except Exception:
                pass
    except Exception as e:
        rec["err"] = f"{type(e).__name__}: {str(e)[:140]}"
    rec["ms"] = int((time.time() - t0) * 1000)
    return rec


def main():
    now_ms = int(time.time() * 1000)
    legs = []

    # L1 rank-exact (verbatim from update_moneyflow.py fetch_rank_one_page)
    rank_qs = ("pn=1&pz=100&po=1&np=1&fltt=2&invt=2&fid=f62&fs=m:0+t:6,"
               "m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048&fields=f12,f14,f62")
    rank_url = "https://push2.eastmoney.com/api/qt/clist/get?" + rank_qs
    legs.append(("rank-exact", rank_url,
                 {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                  "Referer": "https://quote.eastmoney.com/"}))
    time.sleep(THROTTLE)

    # L2 fflow-exact (verbatim fetch_one for 000001)
    fflow_url = ("https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
                 "?lmt=0&klt=101&secid=0.000001&fields1=f1,f2,f3,f7"
                 "&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,"
                 "f64,f65&ut=" + UT + f"&_={now_ms}")
    legs.append(("fflow-exact", fflow_url, {"User-Agent": UA_OLD}))
    time.sleep(THROTTLE)

    # L3 rank-no-referer
    legs.append(("rank-no-referer", rank_url,
                 {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}))
    time.sleep(THROTTLE)

    # L4 rank-modern-ua (+referer)
    legs.append(("rank-modern-ua", rank_url,
                 {"User-Agent": UA_MODERN, "Referer": "https://quote.eastmoney.com/"}))
    time.sleep(THROTTLE)

    # L5 fflow-modern-ua
    legs.append(("fflow-modern-ua", fflow_url, {"User-Agent": UA_MODERN}))
    time.sleep(THROTTLE)

    # L6 fflow-no-ut
    fflow_nout = fflow_url.replace("&ut=" + UT, "")
    legs.append(("fflow-no-ut", fflow_nout, {"User-Agent": UA_OLD}))
    time.sleep(THROTTLE)

    # L7 ctrl-quote (same push2 host, different api path)
    ctrl_url = ("https://push2.eastmoney.com/api/qt/stock/get?secid=1.510300"
                "&fields=f43,f57,f58&ut=" + UT)
    legs.append(("ctrl-quote", ctrl_url,
                 {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                  "Referer": "https://quote.eastmoney.com/"}))
    time.sleep(THROTTLE)

    # L8 ctrl-root (TLS+HTTP on push2his root)
    legs.append(("ctrl-push2his-root", "https://push2his.eastmoney.com/",
                 {"User-Agent": UA_MODERN}))

    out = {"probe": "r1027bma_mf_source_diag", "ts": datetime.datetime.now().isoformat(timespec="seconds"),
           "context": "source-blocked since 2026-10-14T19:46; panel cutoff 2026-10-13 complete=false",
           "legs": [probe(n, u, h) for (n, u, h) in legs]}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    for r in out["legs"]:
        line = f"{r['leg']:<22} ok={r['ok']} bytes={r['bytes']} ms={r['ms']} err={r['err']}"
        print(line)


if __name__ == "__main__":
    main()
