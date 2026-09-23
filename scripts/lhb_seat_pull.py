"""LHB seat-level full-history pull (LHB_SEAT_PULL.md pre-reg, claim
MSG-20260923-1958). Pure data engineering: zero IC, zero engine runs,
strategy engine ledger N untouched.

Source: datacenter-web EastMoney API, reportName RPT_BILLBOARD_DAILYDETAILSBUY
(one row per seat, contains BOTH sides: BUY/SELL/NET per probe v2 schema),
browser UA (probe-proven; vendor akshare sends no UA and gets rate-limited
on this network).

Design (frozen): 10-calendar-day windows 2007-01-01 -> 2026-09-22, paged
pageSize=500 (page cap 2000/window), 0.4s politeness, backoff 5/15/45s x3,
persistent window failure -> checkpoint stop exit 3 (resumable via state).
Monthly parquet chunks with exact-duplicate dedup on resume. Tracked status
mirror results/seat_pull_status.json updated per window (fleet visibility +
compute-audit output evidence). Console output ASCII-only (PS console pit).

Write-domain (claim-scoped): Money02/data/lhb_seat/ (new dir) +
results/seat_pull_status.json. Nothing existing is touched.
"""
import json
import os
import sys
import time

import pandas as pd
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LHB_PATH = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")
OUT_DIR = os.path.join(ROOT, "Money02", "data", "lhb_seat")
STATE_PATH = os.path.join(OUT_DIR, "state.json")
STATUS_PATH = os.path.join(ROOT, "results", "seat_pull_status.json")

URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
REPORT = "RPT_BILLBOARD_DAILYDETAILSBUY"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
START = pd.Timestamp("2007-01-01")
END = pd.Timestamp("2026-09-22")        # exclusive
WINDOW_DAYS = 10
PAGE_SIZE = 500
PAGE_CAP = 2000
SLEEP_S = 0.4
BACKOFF_S = (5, 15, 45)
REQ_FIELDS = ["TRADE_DATE", "SECURITY_CODE", "OPERATEDEPT_NAME", "BUY", "SELL"]
FIRST_WINDOW = (pd.Timestamp("2026-09-11"), pd.Timestamp("2026-09-21"))
CODE_OVERLAP_MIN = 0.90


def w_start_end(start):
    return start, min(start + pd.Timedelta(days=WINDOW_DAYS), END)


def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"windows_done": [], "rows_total": 0, "errors": [],
            "first_window_gated": False}


def save_state(state):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, default=str)


def save_status(state, current_window, done, last_error=None):
    total_windows = int((END - START) / pd.Timedelta(days=WINDOW_DAYS)) + 1
    os.makedirs(os.path.dirname(STATUS_PATH), exist_ok=True)
    out = {"updated": time.strftime("%Y-%m-%d %H:%M:%S"),
           "windows_done": len(state["windows_done"]),
           "total_windows": total_windows,
           "done_pct": round(100.0 * len(state["windows_done"]) / total_windows, 1),
           "rows_total": state["rows_total"],
           "current_window": str(current_window) if current_window is not None else "",
           "done": bool(done), "last_error": last_error or ""}
    with open(STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, default=str)


def fetch_page(ws, we, page):
    params = {
        "reportName": REPORT, "columns": "ALL",
        "filter": f"(TRADE_DATE>='{ws.date()}')(TRADE_DATE<'{we.date()}')",
        "pageNumber": str(page), "pageSize": str(PAGE_SIZE),
        "sortTypes": "1", "sortColumns": "TRADE_DATE",
        "source": "WEB", "client": "WEB",
    }
    last_err = None
    for delay in BACKOFF_S + (None,):
        try:
            r = requests.get(URL, params=params,
                             headers={"User-Agent": UA}, timeout=20)
            j = r.json()
            data = (j.get("result") or {}).get("data")
            if data is None:
                raise RuntimeError(f"result null (http={r.status_code})")
            return data
        except Exception as ex:
            last_err = f"{type(ex).__name__}: {str(ex)[:120]}"
            if delay is None:
                raise RuntimeError(last_err)
            time.sleep(delay)
    raise RuntimeError(last_err or "unreachable")


def fetch_window(ws, we):
    rows, page = [], 1
    while page <= PAGE_CAP:
        data = fetch_page(ws, we, page)
        if not data:
            break
        rows.extend(data)
        if len(data) < PAGE_SIZE:
            break
        page += 1
        time.sleep(SLEEP_S)
    if page > PAGE_CAP:
        rows.append({"_page_cap_hit": True})
    return rows


def inhouse_codes(ws, we, lhb):
    m = (pd.to_datetime(lhb["上榜日"]) >= ws) & (pd.to_datetime(lhb["上榜日"]) < we)
    return set(lhb.loc[m, "代码"].astype(str))


def first_window_gate(rows, ws, we, lhb):
    if not rows:
        return False, "empty first window"
    f0 = rows[0]
    for fld in REQ_FIELDS:
        if fld not in f0:
            return False, f"missing field {fld}"
    bad_dates = sum(1 for r in rows
                    if not (ws <= pd.Timestamp(r["TRADE_DATE"]) < we))
    if bad_dates:
        return False, f"{bad_dates} rows outside window"
    codes = {str(r["SECURITY_CODE"]) for r in rows}
    ref = inhouse_codes(ws, we, lhb)
    overlap = (len(codes & ref) / len(ref)) if ref else 1.0
    if overlap < CODE_OVERLAP_MIN:
        return False, f"code overlap {overlap:.3f} < {CODE_OVERLAP_MIN}"
    return True, f"rows={len(rows)} codes={len(codes)} overlap={overlap:.3f}"


def month_chunk_path(month_key):
    return os.path.join(OUT_DIR, f"lhb_seat_{month_key}.parquet")


def flush_month(month_key, buf):
    df = pd.DataFrame(buf)
    path = month_chunk_path(month_key)
    if os.path.exists(path):
        old = pd.read_parquet(path)
        df = pd.concat([old, df], ignore_index=True)
    df = df.drop_duplicates()
    df.to_parquet(path, index=False)
    return len(df)


def main():
    t0 = time.time()
    lhb = pd.read_parquet(LHB_PATH)
    state = load_state()
    done_set = set(state["windows_done"])
    print(f"resume: {len(done_set)} windows done, "
          f"{state['rows_total']} rows", flush=True)

    # ---- first-window hard gate (fresh runs only)
    if not state["first_window_gated"]:
        ws, we = FIRST_WINDOW
        rows = fetch_window(ws, we)
        ok, msg = first_window_gate(rows, ws, we, lhb)
        print(f"first-window gate: ok={ok} {msg}", flush=True)
        if not ok:
            save_status(state, ws, False, f"gate fail: {msg}")
            return 1
        state["first_window_gated"] = True
        state["windows_done"].append(str(ws.date()))
        state["rows_total"] += len(rows)
        save_state(state)
        save_status(state, ws, False)
        done_set.add(str(ws.date()))
        buf, cur_month = rows, "202609"
        flush_month(cur_month, buf)
    else:
        buf, cur_month = [], None

    # ---- chronological walk (resume-friendly, month buffers in memory)
    total_windows = int((END - START) / pd.Timedelta(days=WINDOW_DAYS)) + 1
    n_done = len(done_set)
    cur = START
    while cur < END:
        key = str(cur.date())
        ws, we = w_start_end(cur)
        if key not in done_set:
            try:
                rows = fetch_window(ws, we)
            except RuntimeError as ex:
                state["errors"].append(f"{key}: {ex}")
                save_state(state)
                save_status(state, key, False, str(ex))
                print(f"window {key} persistent failure -> checkpoint stop "
                      f"(resumable)", flush=True)
                return 3
            month_key = str(ws)[:7].replace("-", "")
            if cur_month is None or month_key != cur_month:
                if cur_month is not None:
                    flush_month(cur_month, buf)
                cur_month = month_key
                buf = []
                mpath = month_chunk_path(cur_month)
                if os.path.exists(mpath):
                    old = pd.read_parquet(mpath)
                    buf = old.to_dict("records")
            rows = [r for r in rows if "_page_cap_hit" not in r]
            buf.extend(rows)
            state["windows_done"].append(key)
            state["rows_total"] += len(rows)
            done_set.add(key)
            n_done += 1
            if n_done % 10 == 0:
                save_state(state)
                save_status(state, key, False)
                print(f"  {n_done}/{total_windows} windows, "
                      f"{state['rows_total']} rows "
                      f"({time.time()-t0:.0f}s)", flush=True)
        cur = we
    if cur_month is not None:
        flush_month(cur_month, buf)
    save_state(state)
    save_status(state, None, True)
    print(f"=== LHB seat pull COMPLETE: {state['rows_total']} rows, "
          f"{len(state['windows_done'])} windows "
          f"({time.time()-t0:.0f}s) ===", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
