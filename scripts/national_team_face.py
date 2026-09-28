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
  python scripts/national_team_face.py collect_pdf_holder
                                               # s2 leg: periodic-report
                                               # PDF top-10 holders +
                                               # national-team matching
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


# ------------------------------------------------- s2 PDF holder chapter
# (r185 bm-c, T-106 s2 physical-dep leg per progress_r184 exact
# continuation. Channel probes this round, receipts
# .codely-cli/scratch/r185bmc_probe_*.json: JJGG type=3 periodic-report
# list API live 200 (announcement ids + titles + dates); PDF direct
# link pdf.dfcfw.com/pdf/H2_<ID>_1.pdf live 200 (%PDF-1.7, 510300
# interim 2.3MB/67pp, annual 83pp); pypdf 6.19 text extraction
# clean-CJK live-verified. Annual reports carry the top-10 holder NAME
# face (sec 9.2, feeder-fund-excluded note) + anonymous >=20% table
# (sec 12.1); interim reports carry structure (sec 8.1) + >=20% note
# (sec 11.1) and NO top-10 table -- the honest face map, disclosed.)
JJGG_API = "https://api.fund.eastmoney.com/f10/JJGG"
PDF_URL_TMPL = "http://pdf.dfcfw.com/pdf/H2_{ann_id}_1.pdf"
PDF_HEADERS = {"Referer": "https://fund.eastmoney.com/", "User-Agent": UA}
REPORT_KINDS = (("interim", "中期报告"), ("annual", "年度报告"))
# NATIONAL-TEAM frozen definition (ticket spec): 中央汇金(incl. 汇金资管) /
# 中证金融(证金) / 社保基金 / 外管局旗下投资平台 / 国家级大基金.
# Conservative keyword matching -- zero-false-positive posture; the
# NationalBigFund class only auto-matches explicit fund names.
NT_PATTERNS = [
    ("HuiJin", ("汇金",)),
    ("Zhengjin", ("中证金融", "证金公司", "证券金融")),
    ("SocialSecurity", ("社保",)),
    ("SAFE_platform", ("外管局", "梧桐树")),
    ("NationalBigFund", ("国家集成电路", "国家制造业", "国家大基金")),
]
PDF_FACE_JSON = os.path.join(OUT_DIR, "pdf_holder_face.json")
PDF_CKPT_JSON = os.path.join(OUT_DIR, "pdf_holder_checkpoint.json")
PDF_RECEIPT_JSON = os.path.join(OUT_DIR, "pdf_holder_receipt.json")

_TOP10_TAIL_ONLY = re.compile(
    r"^((?:\d{1,3}(?:,\d{3})+|\d+)\.\d{2})\s+(\d{1,3}(?:\.\d{1,2})?)%?$")
_TOP10_FRAG_TAIL = re.compile(
    r"^(.+?)\s+((?:\d{1,3}(?:,\d{3})+|\d+)\.\d{2})\s+"
    r"(\d{1,3}(?:\.\d{1,2})?)%?$")
_TOP10_RANK_LINE = re.compile(r"^(\d{1,2})\s+(\S.*)$")
# rank domain guard 1-12: wrapped-digit tails ("...41.0\n0", "...202512\n31")
# must never be mistaken for a rank-alone row head (r187 live find)
_TOP10_RANK_ALONE = re.compile(r"^([1-9]|1[0-2])$")
_GE20_ROW_HEAD = re.compile(r"^([1-9]|1[0-2])\s*20\d{6}-?\s*$")
_GE20_CLASS_RANK = re.compile(r"^[\u4e00-\u9fff]{0,4}\s*([1-9]|1[0-2])\s*$")
_GE20_RANK_ALONE = re.compile(r"^([1-9]|1[0-2])$")
_GE20_CLASS_YEAR = re.compile(
    r"^[\u4e00-\u9fff]{0,4}\s*([1-9]|1[0-2])\s*20\d{2}年")
_GE20_STRIP_HEAD = re.compile(
    r"^(?:[\u4e00-\u9fff]{0,4})?(\d{1,2})(20\d{6}-20\d{6};?)")
_GE20_STRIP_TAIL = re.compile(
    r"((?:\d{1,3}(?:,\d{3})+|\d+)\.\d{2})(\d{1,3}\.\d{1,2})$")


def _jjgg_headers(code):
    return {"Referer": "https://fundf10.eastmoney.com/jjgg_%s_2.html" % code,
            "User-Agent": UA}


def fetch_jjgg_periodic(code):
    """Periodic-report announcement list (JJGG type=3). Returns
    (items, None) or (None, error)."""
    r = _get(JJGG_API, {"fundcode": code, "pageIndex": 1, "pageSize": 20,
                        "type": 3}, _jjgg_headers(code))
    if r is None:
        return None, "http_fail"
    try:
        items = r.json().get("Data") or []
    except ValueError:
        return None, "json_fail"
    if not items:
        return None, "empty"
    return items, None


def pick_report(items, keyword, exclude=("摘要",)):
    """Latest announcement whose title contains keyword (report-摘要
    summaries excluded -- they lack the full holder chapters)."""
    best = None
    for it in items:
        t = it.get("TITLE") or ""
        if keyword in t and not any(x in t for x in exclude):
            d = it.get("PUBLISHDATE") or ""
            if best is None or d > best[0]:
                best = (d, it)
    return best[1] if best else None


def fetch_pdf_pages(ann_id):
    """Download the announcement PDF, extract per-page text.
    Returns (dict, None) or (None, error)."""
    url = PDF_URL_TMPL.format(ann_id=ann_id)
    r = _get(url, {}, PDF_HEADERS, timeout=60)
    if r is None:
        return None, "http_fail"
    if not r.content.startswith(b"%PDF"):
        return None, "not_pdf"
    import hashlib
    from pypdf import PdfReader
    try:
        rd = PdfReader(io.BytesIO(r.content))
    except Exception:
        return None, "pdf_parse_fail"
    texts = []
    for pg in rd.pages:
        try:
            texts.append(pg.extract_text() or "")
        except Exception:
            texts.append("")
    return {"pdf_url": url, "sha256": hashlib.sha256(r.content).hexdigest(),
            "bytes": len(r.content), "pages": len(texts), "texts": texts}, None


def _holder_block(full_text, marker_re, end_markers, max_chars=3600):
    """Window from marker to the first end marker (or max_chars).
    The LAST match wins -- fund-report TOC pages carry the same section
    titles with dot leaders, and the body section always follows the
    TOC (probe-verified r185)."""
    matches = list(marker_re.finditer(full_text))
    if not matches:
        return None
    m = matches[-1]
    seg = full_text[m.start():m.start() + max_chars]
    cut = len(seg)
    for em in end_markers:
        k = seg.find(em, len(m.group(0)))
        if 0 <= k < cut:
            cut = k
    return seg[:cut]


def parse_top10(block):
    """Top-10 holder table (annual sec 9.2). Chinese names wrap
    mid-word across pdf lines -- fragments glue WITHOUT separator;
    a record completes when a line carries the shares+pct tail.
    Single-line rows (name+shares+pct on one line -- the 易方达/
    南方/华夏 pdf layouts) complete in place at the rank line.
    Returns list of {rank, name, shares, pct}."""
    recs = []
    rank = None
    frags = []
    for raw in (block or "").splitlines():
        ln = raw.strip()
        if not ln:
            continue
        if rank is None:
            m = _TOP10_RANK_LINE.match(ln)
            if m:
                t = _TOP10_FRAG_TAIL.match(m.group(2))
                if t and not _TOP10_RANK_LINE.match(m.group(2)):
                    recs.append({"rank": int(m.group(1)),
                                 "name": t.group(1),
                                 "shares": float(t.group(2).replace(",", "")),
                                 "pct": float(t.group(3))})
                    continue
                rank = int(m.group(1))
                frags = [m.group(2)]
                continue
            m = _TOP10_RANK_ALONE.match(ln)
            if m:
                rank = int(m.group(1))
                frags = []
                continue
            continue  # header/note lines before the first rank row
        m = _TOP10_FRAG_TAIL.match(ln)
        if m and not _TOP10_RANK_LINE.match(ln):
            frags.append(m.group(1))
            recs.append({"rank": rank, "name": "".join(frags),
                         "shares": float(m.group(2).replace(",", "")),
                         "pct": float(m.group(3))})
            rank, frags = None, []
            continue
        m = _TOP10_TAIL_ONLY.match(ln)
        if m:
            recs.append({"rank": rank, "name": "".join(frags),
                         "shares": float(m.group(1).replace(",", "")),
                         "pct": float(m.group(2))})
            rank, frags = None, []
            continue
        frags.append(ln)
    return [r for r in recs if 1 <= r["rank"] <= 12]


def parse_ge20(block):
    """>=20% single-investor table (interim sec 11.1 / annual sec 12.1).
    Rows are anonymous (no holder names -- disclosure privacy face);
    the 期初/申购/赎回 numerics wrap mid-digit and stay raw-archived;
    the tail (持有份额+占比) is comma-anchored and parsed exactly.
    Returns dict(n_rows, rows=[{rank, interval, shares, pct}],
    raw) or None when the block is absent."""
    if not block:
        return None
    if "无需要披露" in block or "无需要说明" in block:
        return {"n_rows": 0, "rows": [], "raw": block[:800]}
    lines = block.splitlines()
    rows = []
    blob = []
    in_row = False

    def _flush():
        if not blob:
            return
        stripped = re.sub(r"[\s%]+", "", "".join(blob))
        head = _GE20_STRIP_HEAD.match(stripped)
        tail = _GE20_STRIP_TAIL.search(stripped)
        row = {"raw": " ".join(blob)[:400]}
        if head:
            row["rank"] = int(head.group(1))
            row["interval"] = head.group(2)
        if tail:
            row["shares"] = float(tail.group(1).replace(",", ""))
            row["pct"] = float(tail.group(2))
        if len(row) > 1:
            rows.append(row)
        del blob[:]

    for raw in lines:
        ln = raw.strip()
        if not ln:
            continue
        if (_GE20_ROW_HEAD.match(ln) or _GE20_CLASS_RANK.match(ln)
                or _GE20_RANK_ALONE.match(ln) or _GE20_CLASS_YEAR.match(ln)):
            _flush()
            in_row = True
            blob.append(ln)
        elif "产品特有风险" in ln:
            _flush()
            in_row = False
        elif in_row and not re.match(r"^\d{1,2}\.\d{1,2}\s*[\u4e00-\u9fff]", ln):
            # section-heading guard: "12.2 影响投资者决策..." stops the
            # blob; all-numeric wrapped tails like "4.00 42.62" pass
            blob.append(ln)
    _flush()
    return {"n_rows": len(rows), "rows": rows, "raw": block[:800]}


def national_team_match(name):
    """Frozen-definition category tags for a holder name."""
    return [cat for cat, kws in NT_PATTERNS
            if any(k in (name or "") for k in kws)]


_TOP10_MARKER = re.compile(r"期末上市基金前十名持有人")
_GE20_MARKER = re.compile(r"单一投资者持有基金份额比例达到或超过\s*20%")
_STRUCT_MARKER = re.compile(r"期末基金份额持有人户数及持有人结构")


def _pdf_faces(texts, kind):
    full = "\n".join(texts)
    faces = {"structure_raw": None, "top10": None, "ge20": None}
    b = _holder_block(full, _STRUCT_MARKER,
                     ["§", "份额变动", "重大事件揭示"])
    if b:
        faces["structure_raw"] = b[:1600]
    if kind == "annual":
        b = _holder_block(full, _TOP10_MARKER,
                          ["注：前十名持有人", "期末基金管理人的从业人员",
                           "§", "份额变动"])
        if b:
            faces["top10"] = parse_top10(b)
    b = _holder_block(full, _GE20_MARKER,
                     ["影响投资者决策的其他重要信息", "备查文件目录", "§"])
    if b:
        faces["ge20"] = parse_ge20(b)
    return faces


def cmd_collect_pdf_holder():
    """T-106 s2 leg: per-ETF periodic-report PDF holder-chapter face
    (top-10 names + national-team matching + >=20% trajectory).
    Checkpoint-resumable; throttle 1.2s; conn-fuse 3 family law."""
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    ckpt = {}
    if os.path.exists(PDF_CKPT_JSON):
        try:
            ckpt = json.load(open(PDF_CKPT_JSON, encoding="utf-8"))
        except (OSError, ValueError):
            ckpt = {}
    requests_done = 0
    failures = []
    for code, nm, _ex in SIX:
        items, err = fetch_jjgg_periodic(code)
        requests_done += 1
        time.sleep(THROTTLE)
        if items is None:
            failures.append((code, "jjgg_list", err))
            continue
        for kind, kw in REPORT_KINDS:
            key = code + "_" + kind
            if key in ckpt:
                continue                      # checkpoint resume
            ann = pick_report(items, kw)
            if ann is None:
                failures.append((code, kind, "no_report"))
                continue
            pdf, err = fetch_pdf_pages(ann["ID"])
            requests_done += 1
            time.sleep(THROTTLE)
            if pdf is None:
                failures.append((code, kind, err))
                continue
            faces = _pdf_faces(pdf["texts"], kind)
            rec = {"code": code, "fund_name": nm, "kind": kind,
                   "ann_id": ann["ID"], "title": ann.get("TITLE"),
                   "publish_date": ann.get("PUBLISHDATEDesc"),
                   "pdf_url": pdf["pdf_url"], "pdf_sha256": pdf["sha256"],
                   "pdf_bytes": pdf["bytes"], "pdf_pages": pdf["pages"],
                   "faces": faces}
            ckpt[key] = rec
            _atomic_write_json(PDF_CKPT_JSON, ckpt)
            print("collected %s %s (%d pp, top10 rows %s)"
                  % (code, kind, pdf["pages"],
                     len(faces["top10"]) if faces["top10"] else 0),
                  flush=True)
    product = {"six": {}, "national_team": {}}
    for code, nm, _ex in SIX:
        per = {}
        for kind, _kw in REPORT_KINDS:
            r = ckpt.get(code + "_" + kind)
            if r:
                per[kind] = r
        product["six"][code] = per
    for code in SIX_CODES:
        hits = []
        annual = product["six"][code].get("annual")
        if annual and annual["faces"].get("top10"):
            for row in annual["faces"]["top10"]:
                tags = national_team_match(row["name"])
                if tags:
                    hits.append({"report": "annual", "rank": row["rank"],
                                 "name": row["name"], "categories": tags,
                                 "shares": row["shares"], "pct": row["pct"]})
        product["national_team"][code] = {
            "hit": bool(hits), "hits": hits,
            "combined_pct": round(sum(h["pct"] for h in hits), 2)}
    _atomic_write_json(PDF_FACE_JSON, product)
    receipt = {"elapsed_sec": round(time.time() - t0, 1),
               "requests": requests_done, "failures": failures,
               "ckpt_keys": sorted(ckpt.keys()),
               "verdict": "ok" if not failures else "partial"}
    _atomic_write_json(PDF_RECEIPT_JSON, receipt)
    print("pdf_holder collect %s: %d requests, %d keys, failures=%s"
          % (receipt["verdict"], requests_done, len(ckpt), failures))
    return 0 if not failures else 2


TOP10_BLOCK_FIXTURE = (
    "9.2 期末上市基金前十名持有人 \n"
    "序号  持有人名称  持有份额（份）  占上市总份额比例（%）  \n"
    "1 中央汇金资产管理有\n"
    "限责任公司 37,858,474,974.00 42.62  \n"
    "2 中央汇金投资有限责\n"
    "任公司 35,654,598,859.00 40.14  \n"
    "3 太平人寿保险有限公\n"
    "司 272,999,551.00 0.31  \n"
    "7 \n"
    "北京诚旸投资有限公\n"
    "司－诚旸灵活配置私\n"
    "募证券投资基金 \n"
    "179,399,890.00 0.20  \n"
    "11 \n"
    "华泰柏瑞沪深300交\n"
    "易型开放式指数证券\n"
    "投资基金联接基金 \n"
    "665,052,468.00 0.75  \n"
    "注：前十名持有人为除本基金的联接基金之外的前十名持有人。"
)

GE20_BLOCK_FIXTURE = (
    "12.1 报告期内单一投资者持有基金份额比例达到或超过 20%的情况 \n"
    "机构 \n"
    "1  20250101-\n"
    "20251231;  \n"
    "26,621,32\n"
    "8,344.00  \n"
    "11,237,\n"
    "146,630\n"
    ".00  \n"
    "0.00  37,858,474,97\n"
    "4.00  42.62  \n"
    "2  20250101-\n"
    "20251231;  \n"
    "35,654,59\n"
    "8,859.00 0.00 0.00  35,654,598,85\n"
    "9.00 40.14  \n"
    "产品特有风险 \n"
    "本基金报告期内有单一持有人持有基金份额超过20%的情形。"
)

GE20_NONE_FIXTURE = (
    "11.1 报告期内单一投资者持有基金份额比例达到或超过 20%的情况 \n"
    "注：本基金本报告期内无需要披露的单一投资者持有基金份额比例"
    "达到或超过20%的情况。"
)

JJGG_ITEMS_FIXTURE = [
    {"TITLE": "华泰柏瑞沪深300ETF2026年中期报告", "ID": "AN1",
     "PUBLISHDATE": "2026-08-29T00:00:00", "PUBLISHDATEDesc": "2026-08-29"},
    {"TITLE": "华泰柏瑞沪深300ETF2026年中期报告摘要", "ID": "AN0",
     "PUBLISHDATE": "2026-08-29T00:00:00", "PUBLISHDATEDesc": "2026-08-29"},
    {"TITLE": "华泰柏瑞沪深300ETF2025年年度报告", "ID": "AN2",
     "PUBLISHDATE": "2026-03-31T00:00:00", "PUBLISHDATEDesc": "2026-03-31"},
    {"TITLE": "华泰柏瑞沪深300ETF2025年年度报告摘要", "ID": "AN3",
     "PUBLISHDATE": "2026-03-31T00:00:00", "PUBLISHDATEDesc": "2026-03-31"},
    {"TITLE": "华泰柏瑞沪深300ETF2026年第2季度报告", "ID": "AN4",
     "PUBLISHDATE": "2026-07-21T00:00:00", "PUBLISHDATEDesc": "2026-07-21"},
]

# ---- r186/r187 real-layout variants (live PDF text shapes, six-fund
# census): single-line top-10 rows carry a trailing % on the pct; the
# >=20% tables wrap digits mid-group ("202512\n31", "62,941.0\n0").
TOP10_SINGLELINE_FIXTURE = (
    "9.2  期末上市基金前十名持有人 \n"
    "序号 持有人名称 持有份额（份） 占上市总份额比例 \n"
    "1 中央汇金投资有限责任公司 11,362,962,941.00 36.07% \n"
    "2 中央汇金资产管理有限责任公司 5,656,821,265.00 17.96% \n"
    "3 中国人寿保险股份有限公司 834,431,450.00 2.65% \n"
)

GE20_SOUTH_FIXTURE = (
    "单一投资者持有基金份额比例达到或超过20%的情况\n"
    "机构 1\n"
    "20250408-\n"
    "20251231\n"
    "2,615,889,75\n"
    "5.00\n"
    "3,366,087,76\n"
    "3.00 - 5,981,977,51\n"
    "8.00\n"
    "31.3\n"
    "8%\n"
    "产品特有风险\n"
)

GE20_RANK_ALONE_FIXTURE = (
    "单一投资者持有基金份额比例达到或超过 20%的情况 \n"
    "机构\n"
    "1\n"
    "2025-\n"
    "01-01\n"
    "至\n"
    "2025-\n"
    "12-31 28,791,513,899.00 - - 28,791,513,899.00 50.81%\n"
    "产品特有风险 \n"
)

GE20_CLASS_YEAR_FIXTURE = (
    "单一投资者持有基金份额比例达到或超过20%的情况 \n"
    "机构 1 2025年 01月 01日\n"
    "~2025年 12月 31日\n"
    "11,362,9\n"
    "62,941.0\n"
    "0 0.00 0.00\n"
    "11,362,9\n"
    "62,941.0\n"
    "0\n"
    "36.06\n"
    "%\n"
    "产品特有风险\n"
)

# synthetic mini-ckpt (parser output shape; values canned to exercise
# every claim-support branch -- NOT the live disclosure numbers)
VERDICT_CKPT_FIXTURE = {
    "510300_annual": {"code": "510300", "fund_name": "沪深300ETF",
                      "ann_id": "ANV1", "publish_date": "2026-03-31",
                      "pdf_sha256": "aa01",
                      "faces": {"top10": [
                          {"rank": 1, "name": "中央汇金资产管理有限责任公司",
                           "shares": 37858474974.0, "pct": 42.62},
                          {"rank": 2, "name": "中央汇金投资有限责任公司",
                           "shares": 35654598859.0, "pct": 40.14},
                          {"rank": 3, "name": "太平人寿保险有限公司",
                           "shares": 272999551.0, "pct": 0.31}],
                          "ge20": {"n_rows": 2, "rows": [
                              {"rank": 1, "interval": "20250101-20251231;",
                               "shares": 37858474974.0, "pct": 42.62},
                              {"rank": 2, "interval": "20250101-20251231;",
                               "shares": 35654598859.0, "pct": 40.14}]}}},
    "510500_annual": {"code": "510500", "fund_name": "中证500ETF",
                      "ann_id": "ANV2", "publish_date": "2026-03-31",
                      "pdf_sha256": "bb02",
                      "faces": {"top10": [
                          {"rank": 1, "name": "中央汇金投资有限责任公司",
                           "shares": 8235101633.0, "pct": 43.20},
                          {"rank": 2, "name": "华泰证券股份有限公司",
                           "shares": 244841519.0, "pct": 1.28}],
                          "ge20": {"n_rows": 1, "rows": [
                              {"rank": 1, "interval": "20250408-20251231",
                               "shares": 5981977518.0, "pct": 31.38}]}}},
    "510050_annual": {"code": "510050", "fund_name": "上证50ETF",
                      "ann_id": "ANV3", "publish_date": "2026-03-31",
                      "pdf_sha256": "cc03",
                      "faces": {"top10": [
                          {"rank": 1, "name": "中信建投证券股份有限公司",
                           "shares": 355124763.0, "pct": 0.63}],
                          "ge20": {"n_rows": 0, "rows": []}}},
    "159915_annual": {"code": "159915", "fund_name": "创业板ETF",
                      "ann_id": "ANV4", "publish_date": "2026-03-31",
                      "pdf_sha256": "dd04",
                      "faces": {"top10": [],
                                "ge20": {"n_rows": 0, "rows": []}}},
    "588000_annual": {"code": "588000", "fund_name": "科创50ETF",
                      "ann_id": "ANV5", "publish_date": "2026-03-31",
                      "pdf_sha256": "ee05",
                      "faces": {"top10": [
                          {"rank": 1, "name": "中国人寿保险股份有限公司",
                           "shares": 1673812745.0, "pct": 3.12}],
                          "ge20": {"n_rows": 0, "rows": []}}},
    "512100_annual": {"code": "512100", "fund_name": "中证1000ETF",
                      "ann_id": "ANV6", "publish_date": "2026-03-31",
                      "pdf_sha256": "ff06",
                      "faces": {"top10": [
                          {"rank": 1, "name": "中央汇金资产管理有限责任公司",
                           "shares": 13212186794.0, "pct": 51.51},
                          {"rank": 2, "name": "中央汇金投资有限责任公司",
                           "shares": 8956692256.0, "pct": 34.92}],
                          "ge20": {"n_rows": 0, "rows": []}}},
}


# ------------------------------------------------- s2 selection verdict
# (r186 bm-c, T-106 s2 slice-3 per progress_r184 continuation item 2:
# six -> national-team subset, evidence-hard, feeding the T-105
# annotation row. O-1555 CEO two-tier words = the hypothesis UNDER
# VERIFICATION -- verification-not-question posture, numbers only.)
S2_VERDICT_JSON = os.path.join(OUT_DIR, "s2_selection_verdict.json")
CEO_TIER_CLAIM = {
    "510050": 1, "510300": 1,          # 被汇金高度控盘
    "510500": 2, "512100": 2, "588000": 2,   # 其次
    "159915": 0,                        # T-106 six, not CEO-named
}
KONGPAN_BANDS = ((80.0, "extreme"), (50.0, "heavy"), (20.0, "present"))


def _kongpan_band(pct):
    for edge, label in KONGPAN_BANDS:
        if pct >= edge:
            return label
    return "absent"


def _claim_support(tier, band):
    if tier == 0:
        return "n/a_per_data"
    if tier == 1:
        return "supported" if band in ("extreme", "heavy") else "not_supported"
    # tier-2 claim "其次": present-but-second. Equal-or-tier-1-level
    # control = claim UNDERSTATED; zero presence = not supported.
    if band in ("extreme", "heavy"):
        return "understated"
    return "supported" if band == "present" else "not_supported"


def _ge20_max(ge20):
    rows = (ge20 or {}).get("rows") or []
    return max((r["pct"] for r in rows if "pct" in r), default=None)


def _derive_verdict(ckpt):
    """Pure derivation: ckpt -> s2 verdict product (deterministic,
    zero network, no wall-clock fields -- byte-identical on rerun)."""
    per = {}
    for code, name, _ex in SIX:
        a = ckpt.get(code + "_annual") or {}
        i = ckpt.get(code + "_interim") or {}
        top10 = (a.get("faces") or {}).get("top10") or []
        nt_rows = [{"rank": r["rank"], "name": r["name"], "pct": r["pct"],
                    "classes": national_team_match(r["name"])}
                   for r in top10 if national_team_match(r.get("name"))]
        nt_combined = round(sum(r["pct"] for r in nt_rows), 2)
        band = _kongpan_band(nt_combined) if nt_rows else "absent"
        ge20_a = (a.get("faces") or {}).get("ge20") or {}
        ge20_i = (i.get("faces") or {}).get("ge20") or {}
        corrob = sorted({g["pct"] for g in (ge20_a.get("rows") or [])
                         if "pct" in g
                         and any(abs(g["pct"] - r["pct"]) <= 0.02
                                 for r in nt_rows)})
        per[code] = {
            "fund_name": a.get("fund_name") or i.get("fund_name") or name,
            "receipt": {
                "annual": {"ann_id": a.get("ann_id"),
                           "publish_date": a.get("publish_date"),
                           "pdf_sha256": a.get("pdf_sha256")},
                "interim": {"ann_id": i.get("ann_id"),
                            "publish_date": i.get("publish_date"),
                            "pdf_sha256": i.get("pdf_sha256")},
            },
            "nt_top10_rows": nt_rows,
            "nt_combined_pct": nt_combined,
            "kongpan_band": band,
            "ceo_tier_claim": CEO_TIER_CLAIM[code],
            "claim_support": _claim_support(CEO_TIER_CLAIM[code], band),
            "ge20": {
                "annual_n_rows": ge20_a.get("n_rows"),
                "annual_max_pct": _ge20_max(ge20_a),
                "interim_n_rows": ge20_i.get("n_rows"),
                "interim_max_pct": _ge20_max(ge20_i),
                "corroborated_nt_pcts": corrob,
            },
        }
    # subset = claim-SUPPORTED members (r186 selftest contract: a fund
    # may hold NT rows yet stay excluded when its CEO tier-claim reads
    # understated -- e.g. tier-2 "其次" claim vs extreme-band data)
    subset = [c for c in SIX_CODES
              if per[c]["claim_support"] == "supported"]
    excluded = [c for c in SIX_CODES
                if per[c]["claim_support"] != "supported"]
    dates = [per[c]["receipt"][k]["publish_date"]
             for c in SIX_CODES for k in ("annual", "interim")
             if per[c]["receipt"][k]["publish_date"]]
    return {
        "batch": "NATIONAL_TEAM_S2_VERDICT",
        "spec": "T-2026-09-28-106 s2 (O-20260928-1540) + O-20260928-1555 CEO two-tier hypothesis verification",
        "evidence_cutoff": max(dates) if dates else None,
        "universe": SIX_CODES,
        "subset": subset,
        "excluded": excluded,
        "per_etf": per,
        "honest_face_map": {
            "interim_top10": "interim reports disclose holder STRUCTURE + >=20% note only -- NO top-10 table (annual-only face, per-report-layout fact)",
            "ge20_anonymity": ">=20% rows are anonymous; NT attribution ONLY via name-matched annual top-10; pct-coincidence rows listed as corroboration, never as independent NT evidence",
            "verdict_basis": "nt_top10_rows presence in LATEST ANNUAL report disclosures (name-matched, frozen NT definition) + O-1555 CEO two-tier claim-support gate; subset = supported claims, full NT evidence stays in per_etf",
        },
        "divergence_note": "O-1555 CEO five-member grid universe {510050,510300,512100,510500,588000} stays FROZEN for T-104 grid (separate consumer); this NT subset is the T-103/T-105 annotation face -- spec 'list subject to data' honored",
    }


def cmd_verdict():
    """T-106 s2 slice-3: selection verdict product (deterministic
    derivation over the collected PDF faces; zero network)."""
    if not os.path.exists(PDF_CKPT_JSON):
        print("verdict: pdf_holder_checkpoint.json absent -- "
              "run collect_pdf_holder first (honest exit 2)")
        return 2
    with open(PDF_CKPT_JSON, encoding="utf-8") as fh:
        ckpt = json.load(fh)
    v = _derive_verdict(ckpt)
    _atomic_write_json(S2_VERDICT_JSON, v)
    for code in SIX_CODES:
        p = v["per_etf"][code]
        print("%s %-8s nt_combined=%6.2f%% band=%-7s tier_claim=%s "
              "support=%s" % (code, p["fund_name"], p["nt_combined_pct"],
                              p["kongpan_band"], p["ceo_tier_claim"],
                              p["claim_support"]))
    print("verdict: subset=%s excluded=%s evidence_cutoff=%s -> %s"
          % (v["subset"], v["excluded"], v["evidence_cutoff"],
             S2_VERDICT_JSON))
    return 0


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

    # ---- s2 PDF holder-chapter leg (r185): canned-block parsers
    top10 = parse_top10(TOP10_BLOCK_FIXTURE)
    check("top10 rows parsed", len(top10) == 5)
    r1 = top10[0]
    check("top10 wrapped-name glue",
          r1["name"] == "中央汇金资产管理有限责任公司"
          and r1["shares"] == 37858474974.00 and r1["pct"] == 42.62)
    r7 = [r for r in top10 if r["rank"] == 7][0]
    check("top10 multi-wrap + tail-only line",
          r7["name"] == "北京诚旸投资有限公司－诚旸灵活配置私募证券投资基金"
          and r7["shares"] == 179399890.00 and r7["pct"] == 0.20)
    r11 = [r for r in top10 if r["rank"] == 11][0]
    check("top10 feeder row 11",
          r11["name"] == "华泰柏瑞沪深300交易型开放式指数证券投资基金联接基金"
          and r11["pct"] == 0.75)

    ge20 = parse_ge20(GE20_BLOCK_FIXTURE)
    check("ge20 two rows", ge20["n_rows"] == 2)
    g1 = ge20["rows"][0]
    check("ge20 row1 interval+tail (comma-anchor vs wrapped digits)",
          g1["interval"] == "20250101-20251231;"
          and g1["shares"] == 37858474974.00 and g1["pct"] == 42.62)
    g2 = ge20["rows"][1]
    check("ge20 row2 tail", g2["shares"] == 35654598859.00
          and g2["pct"] == 40.14)
    ge20n = parse_ge20(GE20_NONE_FIXTURE)
    check("ge20 none-note zero rows", ge20n["n_rows"] == 0)

    check("nt match HuiJin",
          national_team_match("中央汇金投资有限责任公司") == ["HuiJin"])
    check("nt match Zhengjin",
          national_team_match("中国证券金融股份有限公司") == ["Zhengjin"])
    check("nt match SocialSecurity",
          national_team_match("全国社保基金一一二组合") == ["SocialSecurity"])
    check("nt match SAFE_platform",
          national_team_match("梧桐树投资平台有限责任公司")
          == ["SAFE_platform"])
    check("nt no-false-positive insurer",
          national_team_match("太平人寿保险有限公司") == [])

    ann_i = pick_report(JJGG_ITEMS_FIXTURE, "中期报告")
    ann_a = pick_report(JJGG_ITEMS_FIXTURE, "年度报告")
    check("pick_report interim (摘要 excluded)",
          ann_i["ID"] == "AN1" and ann_a["ID"] == "AN2")

    faces_interim = _pdf_faces(
        ["x\n" + GE20_NONE_FIXTURE + "\n§12 备查文件目录"], "interim")
    check("_pdf_faces interim (no top10 face, ge20 none)",
          faces_interim["top10"] is None
          and faces_interim["ge20"]["n_rows"] == 0)

    # ---- r186: single-line top10 rows (易方达/南方/华夏 layouts)
    top10s = parse_top10(TOP10_SINGLELINE_FIXTURE)
    check("top10 single-line 3 rows", len(top10s) == 3)
    s1 = top10s[0]
    check("top10 single-line row1 complete",
          s1["rank"] == 1 and s1["name"] == "中央汇金投资有限责任公司"
          and s1["shares"] == 11362962941.00 and s1["pct"] == 36.07)
    s3 = top10s[2]
    check("top10 single-line row3 no-NT insurer",
          s3["name"] == "中国人寿保险股份有限公司" and s3["pct"] == 2.65)

    ge20s = parse_ge20(GE20_SOUTH_FIXTURE)
    check("ge20 south-layout one row", ge20s["n_rows"] == 1)
    gs1 = ge20s["rows"][0]
    check("ge20 south interval+tail (% stripped, wrapped digits)",
          gs1["interval"] == "20250408-20251231"
          and gs1["shares"] == 5981977518.00 and gs1["pct"] == 31.38)

    ge20r = parse_ge20(GE20_RANK_ALONE_FIXTURE)
    check("ge20 rank-alone layout one row", ge20r["n_rows"] == 1)
    gr1 = ge20r["rows"][0]
    check("ge20 rank-alone tail (shares+pct, interval raw-retained)",
          gr1["shares"] == 28791513899.00 and gr1["pct"] == 50.81
          and "interval" not in gr1)

    ge20y = parse_ge20(GE20_CLASS_YEAR_FIXTURE)
    check("ge20 class+year layout one row", ge20y["n_rows"] == 1)
    gy1 = ge20y["rows"][0]
    check("ge20 class+year tail (易方达 wrapped shares)",
          gy1["shares"] == 11362962941.00 and gy1["pct"] == 36.06)

    # ---- r186: _derive_verdict on canned mini-ckpt
    v = _derive_verdict(VERDICT_CKPT_FIXTURE)
    check("verdict subset two-of-six",
          v["subset"] == ["510300", "510500"]
          and v["excluded"] == ["510050", "159915", "588000", "512100"])
    h = v["per_etf"]["510300"]
    check("verdict huijin combined + tier1 supported",
          h["nt_combined_pct"] == 82.76 and h["kongpan_band"] == "extreme"
          and h["claim_support"] == "supported"
          and h["ge20"]["corroborated_nt_pcts"] == [40.14, 42.62])
    n = v["per_etf"]["588000"]
    check("verdict absent band + tier2 not_supported",
          n["nt_combined_pct"] == 0 and n["kongpan_band"] == "absent"
          and n["claim_support"] == "not_supported")
    u = v["per_etf"]["512100"]
    check("verdict tier2 understated at extreme band",
          u["claim_support"] == "understated")
    check("verdict deterministic (pure derive rerun equal)",
          _derive_verdict(VERDICT_CKPT_FIXTURE) == v)

    failed = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(("PASS " if ok else "FAIL ") + n)
    print("selftest: %d/%d PASS" % (len(checks) - len(failed), len(checks)))
    return 0 if not failed else 2


def main():
    p = argparse.ArgumentParser(description="T-106 national-team face collector")
    p.add_argument("cmd", choices=["audit", "collect", "collect_pdf_holder",
                                   "verdict", "selftest"])
    args = p.parse_args()
    if args.cmd == "audit":
        return cmd_audit()
    if args.cmd == "collect":
        return cmd_collect()
    if args.cmd == "collect_pdf_holder":
        return cmd_collect_pdf_holder()
    if args.cmd == "verdict":
        return cmd_verdict()
    return cmd_selftest()


if __name__ == "__main__":
    sys.exit(main())
