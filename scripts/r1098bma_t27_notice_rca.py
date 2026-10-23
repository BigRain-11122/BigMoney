"""r1098 bm-a T27 RCA: does the stored income avail_date equal the source
NOTICE_DATE (first-announce) or UPDATE_DATE (latest revision)?

One EM datacenter period (default 2025-03-31) is paginated read-only and
joined to the local staging panel on code. Output = receipts JSON; no panel
writes. Exit 0 ok / 2 machinery.
"""
import datetime as dt
import json
import sys
import time
import urllib.parse
import urllib.request

import pandas as pd

API = "https://datacenter-web.eastmoney.com/api/data/v1/get"
SLEEP_S = 2.0


def _get(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0",
                 "Referer": "https://data.eastmoney.com/"},
    )
    with urllib.request.urlopen(req, timeout=40) as fh:
        return json.load(fh)


def pull_period(period, sleep_s=SLEEP_S, max_pages=40):
    date = period.replace("-", "")[:4] + "-" + period.replace("-", "")[4:6] + \
        "-" + period.replace("-", "")[6:]
    rows, page = [], 1
    while page <= max_pages:
        params = {
            "reportName": "RPT_LICO_FN_CPD",
            "columns": "SECURITY_CODE,REPORTDATE,NOTICE_DATE,UPDATE_DATE",
            "quoteColumns": "",
            "filter": f"(REPORTDATE='{date}')",
            "pageNumber": str(page),
            "pageSize": "500",
            "source": "WEB",
            "client": "WEB",
        }
        payload = _get(params)
        result = payload.get("result") or {}
        data = result.get("data") or []
        if not data:
            break
        rows.extend(data)
        pages = result.get("pages") or 1
        if page >= pages:
            break
        page += 1
        time.sleep(sleep_s)
    return rows


def classify(period):
    rows = pull_period(period)
    if not rows:
        raise RuntimeError(f"empty source response for {period}")
    src = pd.DataFrame(rows)
    src = src.rename(columns={"SECURITY_CODE": "code"})
    src["code"] = src["code"].astype(str).str.zfill(6)
    src["notice"] = pd.to_datetime(src["NOTICE_DATE"], errors="coerce")
    src["update"] = pd.to_datetime(src["UPDATE_DATE"], errors="coerce")
    local = pd.read_parquet(
        f"data/fund_statement_export/_staging/income_{period.replace('-', '')}.parquet")
    local = local[["code", "period_end", "avail_date"]].copy()
    local["stored"] = pd.to_datetime(local["avail_date"], errors="coerce")
    merged = local.merge(src[["code", "notice", "update"]], on="code", how="left")
    known = merged["stored"].notna()
    m = merged[known]
    eq_notice = (m["stored"] == m["notice"])
    eq_update = (m["stored"] == m["update"])
    gap = (m["stored"] - m["notice"]).dt.days
    period_end = pd.Timestamp(period)
    out = {
        "period": period,
        "source_rows": len(src),
        "panel_rows": len(local),
        "joined": int(m["notice"].notna().sum()),
        "panel_eq_notice_pct": round(100 * float(eq_notice.mean()), 2),
        "panel_eq_update_pct": round(100 * float(eq_update.mean()), 2),
        "median_notice_lag_from_period_days": float(
            (m["notice"] - period_end).dt.days.median()),
        "median_stored_lag_from_period_days": float(
            (m["stored"] - period_end).dt.days.median()),
        "median_stored_minus_notice_days": float(gap.median()),
        "stored_after_notice_pct": round(100 * float((gap > 0).mean()), 2),
        "stored_after_deadline_pct": round(
            100 * float((m["stored"] > pd.Timestamp(
                "2025-04-30")).mean()), 2),
    }
    return out, m


def main():
    period = sys.argv[1] if len(sys.argv) > 1 else "2025-03-31"
    receipt = {"tool": "r1098bma_t27_notice_rca",
               "ts": dt.datetime.now().astimezone().strftime(
                   "%Y-%m-%dT%H:%M:%S%z"),
               "period": period}
    out, m = classify(period)
    receipt.update(out)
    print(json.dumps(receipt, ensure_ascii=False, indent=1))
    path = "results/fund_avail_notice_rca.json"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print("wrote", path)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                  # noqa: BLE001
        print(f"machinery failure: {type(exc).__name__}: {exc}")
        sys.exit(2)