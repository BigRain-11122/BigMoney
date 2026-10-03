# -*- coding: utf-8 -*-
"""r663 bm-a: CFO/statement bulk-source probe (FUND piece-4 unlock prerequisite).

Scope (read-only, small): EM datacenter bulk-by-report-date interfaces reachability
+ shape + PIT-declare-date column + history depth + latency. NO collection leg
build (P1 signed-ticket gate per DIGEST-20261004-fund-domain-recheck sec.5).
Deterministic facts file for GM routing decision + ticket evidence.
"""
import json
import time
import traceback

import akshare as ak

FACTS_PATH = r"results/_r663bma_cfo_source_probe_facts.json"

# probe plan: (interface, date) pairs -- recent shape + old-date depth legs
PLAN = [
    ("stock_xjll_em", "20250630"),   # cash-flow statement, latest mid-year
    ("stock_xjll_em", "20101231"),   # history depth leg (accrual-rule era start)
    ("stock_xjll_em", "20051231"),   # deep history leg
    ("stock_lrb_em", "20250630"),   # income statement (gross_profitability/FFScore legs)
    ("stock_zcfz_em", "20250630"),   # balance sheet (dROA/leverage/liquidity legs)
    ("stock_yjbb_em", "20250630"),   # performance report (declare-date check)
]

INTEREST_KEYS = ["经营", "现金", "公告", "报告", "资产", "负债", "收入", "净利", "每股", "日期"]


def probe_one(func_name, date):
    fn = getattr(ak, func_name)
    t0 = time.time()
    rec = {"interface": func_name, "date": date}
    try:
        df = fn(date=date)
        elapsed = round(time.time() - t0, 2)
        rec["ok"] = True
        rec["elapsed_sec"] = elapsed
        rec["n_rows"] = int(len(df))
        rec["columns"] = [str(c) for c in df.columns]
        # code universe shape
        code_col = None
        for cand in ["股票代码", "代码", "股票代码"]:
            if cand in df.columns:
                code_col = cand
                break
        if code_col is not None:
            codes = df[code_col].astype(str)
            rec["n_codes"] = int(codes.nunique())
            rec["code_sample"] = [str(x) for x in codes.head(3).tolist()]
        # declare/announce date column (PIT availability face)
        decl = [c for c in df.columns if ("公告" in str(c)) or ("披露" in str(c))]
        rec["declare_date_columns"] = [str(c) for c in decl]
        # CFO column legs
        cfo = [c for c in df.columns if ("经营" in str(c)) and ("现金" in str(c))]
        rec["cfo_columns"] = [str(c) for c in cfo]
        if cfo:
            col = cfo[0]
            s = df[col]
            rec["cfo_nonnull"] = int(s.notna().sum())
            rec["cfo_sample"] = [float(x) for x in s.dropna().head(3).tolist()]
        # null density on first cfo col
        if cfo:
            rec["cfo_null_share"] = round(float(df[cfo[0]].isna().mean()), 4)
    except Exception as e:  # noqa: BLE001 -- probe must record failure honestly
        rec["ok"] = False
        rec["error"] = f"{type(e).__name__}: {e}"
        rec["elapsed_sec"] = round(time.time() - t0, 2)
    return rec


def main():
    out = {
        "probe": "cfo_statement_bulk_source_probe",
        "machine": "bm-a",
        "round": 663,
        "lane": "FUND piece-4 unlock prerequisite (DIGEST-20261004-fund-domain-recheck sec.5 pointer)",
        "akshare_version": ak.__version__,
        "law_note": "reachability/shape probe only; collection leg = P1 signed-ticket gate, NOT built here",
        "results": [],
    }
    for func_name, date in PLAN:
        rec = probe_one(func_name, date)
        out["results"].append(rec)
        print(func_name, date, "->", "OK" if rec.get("ok") else "FAIL",
              "rows=", rec.get("n_rows"), "sec=", rec.get("elapsed_sec"))
        time.sleep(2.5)  # politeness throttle between probe calls
    # summary legs
    ok_recs = [r for r in out["results"] if r.get("ok")]
    out["summary"] = {
        "n_probe_calls": len(PLAN),
        "n_ok": len(ok_recs),
        "bulk_all_stocks_per_call": all(r.get("n_codes", 0) > 4000 for r in ok_recs),
        "xjll_has_cfo_col": any(r["interface"] == "stock_xjll_em" and r.get("cfo_columns") for r in ok_recs),
        "has_declare_date_any": any(r.get("declare_date_columns") for r in ok_recs),
        "deep_2005_ok": any(r["interface"] == "stock_xjll_em" and r["date"] == "20051231" and r.get("ok") for r in out["results"]),
        "deep_2010_ok": any(r["interface"] == "stock_xjll_em" and r["date"] == "20101231" and r.get("ok") for r in out["results"]),
    }
    with open(FACTS_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("facts ->", FACTS_PATH)
    s = out["summary"]
    print("summary:", json.dumps(s, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise
