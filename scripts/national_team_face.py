# -*- coding: utf-8 -*-
"""NATIONAL_TEAM_FACE -- T-2026-09-28-106 s1 info-collection batch
(O-20260928-1540 CEO order: national-team participation face -- universe
refine + info collection + event-window review for the six broad-index ETFs).

Faces (interface-audited live @2026-09-28 16:1x, receipts in
research/etf_ops/NATIONAL_TEAM_FACE.md):

  (a) share-count anomaly face -- SSE official per-date ETF share table
      (query.sse.com.cn sqlId COMMON_SSE_ZQPZ_ETFZL_XXPL_ETFGM_SEARCH_L,
      one request per STAT_DATE, TOT_VOL unit = 万份 -> *1e4). Verified
      depth: 2015-07-03 reachable (s3 rescue-window viable), latest
      available STAT_DATE = 2026-09-24 as of 2026-09-28 16:0x (2026-09-25
      Friday returns empty = pipeline lag, honest note, NOT an error).
      SZSE (159915) = current-list xlsx only, NO date param -> fine-grid
      history face for the SZSE member is an honest s1 GAP (semi-annual
      F10 total-shares covers it on the report grid).
      akshare fund_etf_scale_sse/szse wrappers: sse wrapper OK but
      hard-crashes (KeyError) on empty dates; szse wrapper is BROKEN on
      pandas 3.0.6 (read_excel(raw-bytes) API removed) -> this script
      calls the endpoints DIRECTLY (r187 law: requests + Referer +
      browser UA, in-repo collector precedent), no akshare dependency.
  (b) holder-disclosure face -- EM fund F10 holder structure per report
      period (fundf10.eastmoney.com FundArchivesDatas.aspx?type=cyrjg),
      per-period 机构/个人/内部持有比例 + 总份额(亿份), semi-annual+annual
      grid, full history back to fund inception. THE hard evidence face:
      national-team bulk buying manifests as 机构持有比例 jumps + total
      share explosions (510300 2024: 64.74% -> 79.40% -> 83.06% with
      374 -> 607 -> 894 亿份, live-verified in audit).
  (c) event ledger -- public announcement timeline, source-cited,
      R176 AI-pollution gate. NOT in this script (web-research batch,
      lands in research/etf_ops/NATIONAL_TEAM_FACE.md + ledger file).

Six-member universe (O-1533 frozen core + same-class extensions, T-106
ticket): 510300 / 510050 / 510500 (SSE core) + 159915 (创业板, SZSE) /
588000 (科创50) / 512100 (中证1000) (largest per-index ETFs, extension
three = candidates pending s2 verdict + prereg discipline).

Universe = research face ONLY: zero admission, zero engine, zero backtest,
zero paper touch. No lane in the S6 chain. Deterministic given source
responses (wall-clock appears only in fetched_at meta, not in data rows).

Exit contracts: 0 = collection landed & verified; 2 = source/mechanism
failure (partial data may still be on disk -- receipt carries the failure
face, honest report, never masked); selftest = offline hermetic, no
network, exit 0.

Usage:
  python scripts/national_team_face.py audit    # probe all faces, receipt
  python scripts/national_team_face.py collect  # land s1 dataset
  python scripts/national_team_face.py selftest # offline parse checks
"""

import argparse
import calendar
import io
import json
import os
import re
import sys
import time
import tempfile
from datetime import date as _date_cls, datetime, timedelta

import requests

SIX = [
    ("510300", "沪深300ETF", "SSE"),
    ("510050", "上证50ETF", "SSE"),
    ("510500", "中证500ETF", "SSE"),
    ("159915", "创业板ETF", "SZSE"),
    ("588000", "科创50ETF", "SSE"),
    ("512100", "中证1000ETF", "SSE"),
]
SIX_CODES = [c for c, _, _ in SIX]

OUT_DIR = os.path.join("results", "national_team")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

SSE_URL = "https://query.sse.com.cn/commonQuery.do"
SSE_PARAMS = {
    "isPagination": "true",
    "pageHelp.pageSize": "10000",
    "pageHelp.pageNo": "1",
    "pageHelp.beginPage": "1",
    "pageHelp.cacheSize": "1",
    "pageHelp.endPage": "1",
    "sqlId": "COMMON_SSE_ZQPZ_ETFZL_XXPL_ETFGM_SEARCH_L",
}
SSE_HEADERS = {"Referer": "https://www.sse.com.cn/", "User-Agent": UA}

F10_URL = "http://fundf10.eastmoney.com/FundArchivesDatas.aspx"
F10_HEADERS = {"Referer": "http://fundf10.eastmoney.com/", "User-Agent": UA}

SZSE_URL = "https://fund.szse.cn/api/report/ShowReport"
SZSE_PARAMS = {
    "SHOWTYPE": "xlsx",
    "CATALOGID": "1000_lf",
    "TABKEY": "tab1",
    "random": "0.07610353191740105",
}
SZSE_HEADERS = {
    "Referer": "https://fund.szse.cn/marketdata/fundslist/index.html",
    "User-Agent": UA,
}

F10_ROW_RE = re.compile(
    r"<tr><td>(\d{4}-\d{2}-\d{2})</td><td class='tor'>([^<]*)</td>"
    r"<td class='tor'>([^<]*)</td><td class='tor'>([^<]*)</td>"
    r"<td class='tor'>([^<]*)</td></tr>")

THROTTLE = 1.2          # seconds between face requests (exchange-polite)
RETRY = 2               # retries per request
CONN_FUSE = 3           # consecutive failures -> abort (honest exit 2)
MAX_REQUESTS = 90       # per-run safety valve


def _get(url, params, headers, timeout=20):
    for attempt in range(RETRY + 1):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=timeout)
            if r.status_code == 200:
                return r
        except requests.RequestException:
            pass
        if attempt < RETRY:
            time.sleep(1.5)
    return None


def _atomic_write_json(path, obj):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=True)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def _pct(s):
    return _num(s.rstrip("%"))


def _num(s):
    """Tolerant numeric parse: '---' and blanks = honest None (some report
    periods disclose no value for a cell)."""
    s = s.strip()
    if not s or s == "---":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def fetch_f10_holder(code):
    """(b) face: per-period holder structure. rows =
    [period_date, inst_pct, indiv_pct, internal_pct, total_shares_yi]."""
    r = _get(F10_URL, {"type": "cyrjg", "code": code, "rt": "0.123456"}, F10_HEADERS)
    if r is None:
        return None, "http_fail"
    rows = []
    for m in F10_ROW_RE.finditer(r.text):
        rows.append([m.group(1), _pct(m.group(2)), _pct(m.group(3)),
                     _pct(m.group(4)), _num(m.group(5))])
    if not rows:
        return None, "parse_empty"
    return rows, None


def fetch_sse_shares(stat_date):
    """(a) face: all-SSE ETF share table for one STAT_DATE.
    Returns (dict code->shares, error). Empty official response = (None, 'empty')."""
    r = _get(SSE_URL, dict(SSE_PARAMS, STAT_DATE=stat_date), SSE_HEADERS)
    if r is None:
        return None, "http_fail"
    try:
        result = r.json().get("result") or []
    except ValueError:
        return None, "json_fail"
    if not result:
        return None, "empty"
    out = {}
    for row in result:
        code = str(row.get("SEC_CODE", "")).strip()
        vol = row.get("TOT_VOL")
        if code and vol not in (None, ""):
            out[code] = float(vol) * 10000.0  # 万份 -> 份
    return out, None


def fetch_szse_shares():
    """(a) face: SZSE current ETF share list (xlsx; pandas-3 safe BytesIO)."""
    r = _get(SZSE_URL, SZSE_PARAMS, SZSE_HEADERS, timeout=30)
    if r is None:
        return None, "http_fail"
    try:
        import pandas as pd
        df = pd.read_excel(io.BytesIO(r.content), engine="openpyxl",
                           dtype={"基金代码": str})
    except Exception:
        return None, "parse_fail"
    col_code = "基金代码" if "基金代码" in df.columns else None
    col_share = "当前规模(份)" if "当前规模(份)" in df.columns else None
    if col_code is None or col_share is None:
        return None, "shape_drift"
    out = {}
    for _, row in df.iterrows():
        code = str(row[col_code]).strip()
        raw = row[col_share]
        try:
            out[code] = float(str(raw).replace(",", ""))
        except (TypeError, ValueError):
            continue
    return out, None


def month_end_dates(start_year, start_month, end_year, end_month):
    """Last weekday of each month (share grid probe date; SSE empty
    response on holidays -> collect walks back up to 3 calendar days)."""
    out = []
    y, m = start_year, start_month
    while (y, m) <= (end_year, end_month):
        if m == 12:
            nxt = (y + 1, 1)
        else:
            nxt = (y, m + 1)
        # last day of month (y, m): day before first of nxt
        last = (_date_cls(nxt[0], nxt[1], 1) - timedelta(days=1)).day
        d = _date_cls(y, m, last)
        while d.weekday() >= 5:
            d -= timedelta(days=1)
        out.append(d.isoformat())
        y, m = nxt
    return out


def cmd_audit():
    receipts = {"six": [c for c, _, _ in SIX], "faces": {}}
    failures = 0
    n_req = 0

    # (b) face probe: one core member + depth rows count
    rows, err = fetch_f10_holder("510300")
    n_req += 1
    if err:
        receipts["faces"]["f10_holder"] = {"ok": False, "error": err}
        failures += 1
    else:
        receipts["faces"]["f10_holder"] = {
            "ok": True, "rows": len(rows), "first": rows[-1][0], "last": rows[0][0],
            "sample_latest": rows[0],
        }

    # (a) SSE probes: latest reachable + historical depth (2015 rescue)
    for probe in ("2015-07-03",):
        shares, err = fetch_sse_shares(probe)
        n_req += 1
        if err:
            receipts["faces"]["sse_" + probe] = {"ok": False, "error": err}
            failures += 1
        else:
            receipts["faces"]["sse_" + probe] = {
                "ok": True, "etf_rows": len(shares),
                "in_six": {c: shares.get(c) for c in SIX_CODES if c in shares},
            }

    # (a) SZSE probe
    sz, err = fetch_szse_shares()
    n_req += 1
    if err or not sz:
        receipts["faces"]["szse_list"] = {"ok": False, "error": err or "zero_rows"}
        failures += 1
    else:
        receipts["faces"]["szse_list"] = {
            "ok": True, "etf_rows": len(sz),
            "in_six": {c: sz.get(c) for c in SIX_CODES if c in sz},
        }

    receipts["requests"] = n_req
    receipts["verdict"] = "faces_ok" if failures == 0 else "faces_failed"
    _atomic_write_json(os.path.join(OUT_DIR, "audit_receipt.json"), receipts)
    print(json.dumps(receipts, ensure_ascii=False, indent=1))
    return 0 if failures == 0 else 2


def cmd_collect():
    t0 = time.time()
    n_req = 0
    fuse = 0
    failures = []

    def throttle():
        nonlocal n_req
        if n_req:
            time.sleep(THROTTLE)

    # ---- (b) holder structure: all six ----
    holders = {}
    for code, name, ex in SIX:
        throttle()
        rows, err = fetch_f10_holder(code)
        n_req += 1
        if err:
            holders[code] = {"error": err}
            failures.append(("f10", code, err))
            fuse += 1
        else:
            holders[code] = {"name": name, "exchange": ex, "rows": rows}
            fuse = 0
        if fuse >= CONN_FUSE:
            print("CONN-FUSE tripped at F10 face -- aborting collect honestly")
            break

    # ---- (a) share snapshots: SSE latest reachable (walk back <=5 days) ----
    sse_latest = None
    sse_empty_receipt = []
    d = datetime.now().date()
    for back in range(6):
        ds = (d - timedelta(days=back)).isoformat()
        throttle()
        shares, err = fetch_sse_shares(ds)
        n_req += 1
        if err == "empty":
            sse_empty_receipt.append(ds)
            continue
        if err:
            failures.append(("sse_snapshot", ds, err))
            break
        sse_latest = {"stat_date": ds, "shares": shares}
        break

    # ---- (a) share snapshots: SZSE current ----
    throttle()
    sz, err = fetch_szse_shares()
    n_req += 1
    szse_latest = None
    if err:
        failures.append(("szse_snapshot", "-", err))
    else:
        szse_latest = sz

    # ---- (a) month-end share grid 2023-06..latest month (SSE five only) ----
    # 2023-06 onward brackets the 2023Q4-2024Q2 national-team ETF wave on a
    # monthly grid; s3 event windows get DAILY pulls under their own prereg.
    sse_codes = [c for c, _, ex in SIX if ex == "SSE"]
    grid = {}
    for ds in month_end_dates(2023, 6, datetime.now().year, datetime.now().month):
        if n_req >= MAX_REQUESTS:
            failures.append(("grid", ds, "max_requests_valve"))
            break
        got = None
        for back in range(4):
            dtry = (datetime.strptime(ds, "%Y-%m-%d") - timedelta(days=back)).date().isoformat()
            throttle()
            shares, err = fetch_sse_shares(dtry)
            n_req += 1
            if err == "empty":
                continue
            if err:
                failures.append(("grid", dtry, err))
                fuse += 1
                break
            got = {c: shares.get(c) for c in sse_codes}
            fuse = 0
            break
        if got is not None:
            grid[dtry] = got
        if fuse >= CONN_FUSE:
            failures.append(("grid", ds, "conn_fuse"))
            break

    evidence_cutoff = ""
    if sse_latest:
        evidence_cutoff = sse_latest["stat_date"]
    if holders:
        for h in holders.values():
            if h.get("rows"):
                evidence_cutoff = max(evidence_cutoff, h["rows"][0][0])

    out_holder = {
        "evidence_cutoff": evidence_cutoff,
        "face": "holder_disclosure_em_f10_cyrjg",
        "six": {code: holders[code] for code in SIX_CODES if code in holders},
    }
    _atomic_write_json(os.path.join(OUT_DIR, "holder_structure.json"), out_holder)

    snap = {
        "evidence_cutoff": evidence_cutoff,
        "sse_stat_date": sse_latest["stat_date"] if sse_latest else None,
        "sse_walkback_empty_receipt": sse_empty_receipt,
        "sse": {c: sse_latest["shares"].get(c) for c in sse_codes} if sse_latest else None,
        "szse": {c: szse_latest.get(c) for c in SIX_CODES if c in szse_latest} if szse_latest else None,
        "note_szse_history_gap": "SZSE endpoint has no date param -- 159915 fine-grid share history is an honest s1 gap; semi-annual F10 total-shares covers the report grid",
    }
    _atomic_write_json(os.path.join(OUT_DIR, "share_snapshot.json"), snap)

    series = {
        "evidence_cutoff": evidence_cutoff,
        "face": "sse_official_month_end_share_grid",
        "grid_dates": sorted(grid.keys()),
        "shares_by_code": {
            c: [[ds, grid[ds].get(c)] for ds in sorted(grid.keys())] for c in sse_codes
        },
    }
    _atomic_write_json(os.path.join(OUT_DIR, "share_series_sse.json"), series)

    receipt = {
        "requests": n_req,
        "elapsed_sec": round(time.time() - t0, 1),
        "failures": failures,
        "holder_codes_ok": sorted([c for c, v in holders.items() if v.get("rows")]),
        "grid_points": len(grid),
        "verdict": "ok" if not failures else "partial_failures_honest",
    }
    _atomic_write_json(os.path.join(OUT_DIR, "collect_receipt.json"), receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=1))
    return 0 if not failures else 2


F10_FIXTURE = (
    "var apidata={ content:\"<table class='w782 comm cyrjg'><thead><tr>"
    "<th class='first'>公告日期</th><th>机构持有比例</th><th>个人持有比例</th>"
    "<th>内部持有比例</th><th class='last'>总份额（亿份）</th></tr></thead><tbody>"
    "<tr><td>2024-06-30</td><td class='tor'>79.40%</td><td class='tor'>19.54%</td>"
    "<td class='tor'>1.06%</td><td class='tor'>607.40</td></tr>"
    "<tr><td>2023-12-31</td><td class='tor'>64.74%</td><td class='tor'>33.30%</td>"
    "<td class='tor'>1.96%</td><td class='tor'>374.44</td></tr>"
    "</tbody></table>\",arryear:2024};"
)

SSE_JSON_FIXTURE = (
    '{"result":[{"NUM":1,"SEC_CODE":"510300","SEC_NAME":"300ETF","ETF_TYPE":"\\u8de8\\u5e02",'
    '"STAT_DATE":"2026-09-24 00:00:00","TOT_VOL":9106249.5},'
    '{"NUM":2,"SEC_CODE":"510050","SEC_NAME":"50ETF","ETF_TYPE":"\\u5355\\u5e02",'
    '"STAT_DATE":"2026-09-24 00:00:00","TOT_VOL":5533717.0}]}'
)


class _Resp:
    def __init__(self, text, content=None):
        self.text = text
        self.content = content if content is not None else text.encode("utf-8")
        self.status_code = 200


def cmd_selftest():
    checks = []

    def check(name, cond):
        checks.append((name, bool(cond)))

    # F10 row parser on fixture
    rows = [[m.group(1), _pct(m.group(2)), _pct(m.group(3)), _pct(m.group(4)),
             float(m.group(5)) if m.group(5).strip() else None]
            for m in F10_ROW_RE.finditer(F10_FIXTURE)]
    check("f10_fixture_rows==2", len(rows) == 2)
    check("f10_latest_period", rows[0][0] == "2024-06-30")
    check("f10_inst_pct", rows[0][1] == 79.40)
    check("f10_shares_yi", rows[0][4] == 607.40)

    # SSE JSON shape parse on fixture
    import json as _json
    result = _json.loads(SSE_JSON_FIXTURE)["result"]
    out = {str(r["SEC_CODE"]).strip(): float(r["TOT_VOL"]) * 10000.0 for r in result}
    check("sse_fixture_two_codes", len(out) == 2)
    check("sse_unit_wanfen_to_fen", abs(out["510300"] - 91062495000.0) < 1.0)

    # month-end date grid sanity
    dates = month_end_dates(2023, 6, 2023, 9)
    check("month_end_count", len(dates) == 4)
    check("month_end_all_weekday", all(datetime.strptime(x, "%Y-%m-%d").weekday() < 5 for x in dates))

    # config integrity
    check("six_codes_unique", len(set(SIX_CODES)) == 6)
    check("sse_five_szse_one", sum(1 for _, _, ex in SIX if ex == "SSE") == 5)

    failed = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(("PASS " if ok else "FAIL ") + n)
    print("selftest: %d/%d PASS" % (len(checks) - len(failed), len(checks)))
    return 0 if not failed else 2


def main():
    p = argparse.ArgumentParser(description="T-106 national-team face s1 collector")
    p.add_argument("cmd", choices=["audit", "collect", "selftest"])
    args = p.parse_args()
    if args.cmd == "audit":
        return cmd_audit()
    if args.cmd == "collect":
        return cmd_collect()
    return cmd_selftest()


if __name__ == "__main__":
    sys.exit(main())
