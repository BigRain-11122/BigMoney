"""LHB seat-level full-history pull, two-stage (LHB_SEAT_PULL.md pre-reg +
SS3.1 evidence-based amendment, claim MSG-20260923-1958).

Pure data engineering: zero IC, zero engine runs, strategy engine ledger N
untouched. Write-domain (claim-scoped): Money02/data/lhb_seat/ (new dir)
+ results/seat_pull_status.json mirror.

Stage 1 (bulk windows): datacenter-web EM API, reportName
RPT_BILLBOARD_DAILYDETAILSBUY (one row per seat, carries BOTH sides:
BUY/SELL/NET per probe v2 schema), browser UA. 10-day windows
2007-01-01 -> 2026-09-22, pageSize 500 (cap 2000 pages/window).
Measured bulk coverage: 88.9% of in-house event codes on the first
window (gate miss diagnosed: the gap is bulk-report coverage, NOT
missing source data).

Stage 2 (per-stock fallback): in-house dedup events NOT covered by
Stage 1 are fetched via the per-stock seat detail endpoint (proven to
cover 100% of tested bulk-missing codes, 5 buy + 5 sell rows each).
One call per event (BUY report carries both sides).

Politeness: 2.0s between requests (bm-b r39 same-network empirical
finding: EM datacenter family burst rate-limits; >=3-5s recommended for
sustained pulls, 2.0s chosen with exponential backoff + checkpoint stop),
backoff 5/15/45s x3, persistent window failure -> checkpoint stop exit 3
(resumable). Monthly parquet chunks with exact-duplicate dedup on
resume. Console ASCII-only.

Gates (SS3.1 amendment): first-window gate = rows>0 + required fields +
dates in window + code overlap >= 0.50 (hard floor = pull broken);
actual overlap RECORDED (not gated) - the 11% bulk gap is remedied by
Stage 2 by design.
"""
import glob
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
REPORT_BULK = "RPT_BILLBOARD_DAILYDETAILSBUY"
REPORT_STOCK = "RPT_BILLBOARD_DAILYDETAILSBUY"   # per-stock, both sides
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
START = pd.Timestamp("2007-01-01")
END = pd.Timestamp("2026-09-22")        # exclusive
WINDOW_DAYS = 10
PAGE_SIZE = 500
PAGE_CAP = 2000
SLEEP_S = 2.0                          # bm-b r39 finding (SS3.1 amendment)
BACKOFF_S = (5, 15, 45, 120, 300)      # extended after live 2009-12-26 stop:
# EM burst-throttle cooldown can exceed 45s (bm-b r39 + live evidence);
# ladder now rides out ~8min outages per request before checkpoint stop
REQ_FIELDS = ["TRADE_DATE", "SECURITY_CODE", "OPERATEDEPT_NAME", "BUY", "SELL"]
FIRST_WINDOW = (pd.Timestamp("2026-09-11"), pd.Timestamp("2026-09-21"))
OVERLAP_HARD_FLOOR = 0.50              # below = pull broken (SS3.1)
STAGE2_FLUSH_EVERY = 500               # events between month-chunk flushes
STAGE2_STATE_EVERY = 100               # events between state checkpoints


def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"windows_done": [], "rows_total": 0, "errors": [],
            "first_window_gated": False, "stage": 1,
            "first_window_overlap": None,
            "stage2_cursor": 0, "stage2_total": None,
            "stage2_done": 0, "stage2_errors": []}


def save_state(state):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, default=str)


def save_status(state, current, done, last_error=None):
    total_windows = int((END - START) / pd.Timedelta(days=WINDOW_DAYS)) + 1
    os.makedirs(os.path.dirname(STATUS_PATH), exist_ok=True)
    out = {"updated": time.strftime("%Y-%m-%d %H:%M:%S"),
           "stage": state.get("stage", 1),
           "windows_done": len(state["windows_done"]),
           "total_windows": total_windows,
           "done_pct": round(100.0 * len(state["windows_done"]) / total_windows, 1),
           "rows_total": state["rows_total"],
           "first_window_overlap": state.get("first_window_overlap"),
           "stage2_done": state.get("stage2_done", 0),
           "stage2_total": state.get("stage2_total"),
           "stage2_errors": len(state.get("stage2_errors", [])),
           "current_window": str(current) if current is not None else "",
           "done": bool(done), "last_error": last_error or ""}
    with open(STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, default=str)


def fetch_page(params):
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
        data = fetch_page({
            "reportName": REPORT_BULK, "columns": "ALL",
            "filter": (f"(TRADE_DATE>='{ws.date()}')"
                       f"(TRADE_DATE<'{we.date()}')"),
            "pageNumber": str(page), "pageSize": str(PAGE_SIZE),
            "sortTypes": "1", "sortColumns": "TRADE_DATE",
            "source": "WEB", "client": "WEB"})
        if not data:
            break
        rows.extend(data)
        if len(data) < PAGE_SIZE:
            break
        page += 1
        time.sleep(SLEEP_S)
    return [r for r in rows if "_page_cap_hit" not in r]


def first_window_gate(rows, ws, we, lhb):
    if not rows:
        return False, 0.0, "empty first window"
    for fld in REQ_FIELDS:
        if fld not in rows[0]:
            return False, 0.0, f"missing field {fld}"
    bad = sum(1 for r in rows
              if not (ws <= pd.Timestamp(r["TRADE_DATE"]) < we))
    if bad:
        return False, 0.0, f"{bad} rows outside window"
    codes = {str(r["SECURITY_CODE"]) for r in rows}
    d = pd.to_datetime(lhb["上榜日"])
    m = (d >= ws) & (d < we)
    ref = set(lhb.loc[m, "代码"].astype(str))
    overlap = (len(codes & ref) / len(ref)) if ref else 1.0
    return (overlap >= OVERLAP_HARD_FLOOR), overlap, \
        f"rows={len(rows)} codes={len(codes)} overlap={overlap:.4f}"


def month_chunk_path(month_key):
    return os.path.join(OUT_DIR, f"lhb_seat_{month_key}.parquet")


def flush_month(month_key, buf):
    df = pd.DataFrame(buf)
    path = month_chunk_path(month_key)
    if os.path.exists(path):
        old = pd.read_parquet(path)
        df = pd.concat([old, df], ignore_index=True)
    df.drop_duplicates().to_parquet(path, index=False)


def inhouse_events(lhb):
    """Dedup rule (PA SS1 verbatim): per (code, date) keep max LHB
    turnover row. Returns sorted [(code, date8), ...] within [START, END).
    """
    lhb = lhb.sort_values(["龙虎榜成交额", "序号"], ascending=[True, False])
    ev = lhb.drop_duplicates(subset=["代码", "上榜日"], keep="last")
    d = pd.to_datetime(ev["上榜日"])
    m = (d >= START) & (d < END)
    pairs = sorted({(str(c), str(t.date()).replace("-", ""))
                    for c, t in zip(ev.loc[m, "代码"], d[m])})
    return pairs


def covered_pairs():
    covered = set()
    for path in sorted(glob.glob(os.path.join(OUT_DIR, "lhb_seat_*.parquet"))):
        df = pd.read_parquet(path, columns=["TRADE_DATE", "SECURITY_CODE"])
        for t, c in zip(df["TRADE_DATE"], df["SECURITY_CODE"]):
            covered.add((str(c), str(pd.Timestamp(t).date()).replace("-", "")))
    return covered


def stage2_fetch_one(code, date8):
    return fetch_page({
        "reportName": REPORT_STOCK, "columns": "ALL",
        "filter": (f"(TRADE_DATE='{date8[:4]}-{date8[4:6]}-{date8[6:]}')"
                   f'(SECURITY_CODE="{code}")'),
        "pageNumber": "1", "pageSize": "500", "sortTypes": "-1",
        "sortColumns": "BUY", "source": "WEB", "client": "WEB"})


def stage2(state):
    """Per-stock fallback for in-house events not covered by Stage 1."""
    t0 = time.time()
    if state["stage2_total"] is None:
        lhb = pd.read_parquet(LHB_PATH)
        events = inhouse_events(lhb)
        cov = covered_pairs()
        missing = [e for e in events if e not in cov]
        state["stage2_total"] = len(missing)
        state["stage2_missing"] = missing
        state["stage2_cursor"] = 0
        state["stage2_done"] = 0
        save_state(state)
        print(f"stage2: {len(missing)}/{len(events)} in-house events "
              f"uncovered by bulk ({time.time()-t0:.0f}s)", flush=True)
    missing = state["stage2_missing"]
    buf, cur_month = [], None
    since_flush, since_state = 0, 0
    while state["stage2_cursor"] < len(missing):
        code, date8 = missing[state["stage2_cursor"]]
        try:
            rows = stage2_fetch_one(code, date8)
        except RuntimeError as ex:
            state["stage2_errors"].append(f"{code}@{date8}: {str(ex)[:100]}")
            rows = []
        month_key = date8[:6]
        if cur_month is None or month_key != cur_month:
            if cur_month is not None:
                flush_month(cur_month, buf)
            cur_month = month_key
            buf = []
            mpath = month_chunk_path(cur_month)
            if os.path.exists(mpath):
                buf = pd.read_parquet(mpath).to_dict("records")
        buf.extend(rows)
        state["rows_total"] += len(rows)
        state["stage2_cursor"] += 1
        state["stage2_done"] += 1
        since_flush += 1
        since_state += 1
        if since_flush >= STAGE2_FLUSH_EVERY:
            flush_month(cur_month, buf)
            buf = pd.read_parquet(month_chunk_path(cur_month)).to_dict("records")
            since_flush = 0
        if since_state >= STAGE2_STATE_EVERY:
            save_state(state)
            save_status(state, f"{code}@{date8}", False)
            since_state = 0
            print(f"  stage2 {state['stage2_done']}/{len(missing)} "
                  f"({time.time()-t0:.0f}s)", flush=True)
        time.sleep(SLEEP_S)
    if cur_month is not None:
        flush_month(cur_month, buf)
    save_state(state)
    save_status(state, None, True)
    print(f"=== seat pull COMPLETE: stage1+2 rows={state['rows_total']}, "
          f"stage2 events={state['stage2_done']} "
          f"errors={len(state['stage2_errors'])} ===", flush=True)


def main():
    t0 = time.time()
    state = load_state()
    done_set = set(state["windows_done"])
    print(f"resume: stage={state['stage']}, {len(done_set)} windows, "
          f"{state['rows_total']} rows", flush=True)
    if state["stage"] >= 2:
        return stage2(state)

    lhb = pd.read_parquet(LHB_PATH)

    # ---- first-window gate (SS3.1: record coverage, hard floor 0.50)
    if not state["first_window_gated"]:
        ws, we = FIRST_WINDOW
        rows = fetch_window(ws, we)
        ok, overlap, msg = first_window_gate(rows, ws, we, lhb)
        print(f"first-window gate: ok={ok} {msg}", flush=True)
        state["first_window_overlap"] = round(float(overlap), 4)
        if not ok:
            save_state(state)
            save_status(state, ws, False, f"gate fail: {msg}")
            return 1
        state["first_window_gated"] = True
        state["windows_done"].append(str(ws.date()))
        state["rows_total"] += len(rows)
        save_state(state)
        save_status(state, ws, False)
        done_set.add(str(ws.date()))
        flush_month("202609", rows)

    # ---- Stage 1: chronological window walk
    total_windows = int((END - START) / pd.Timedelta(days=WINDOW_DAYS)) + 1
    n_done = len(done_set)
    cur = START
    buf, cur_month = [], None
    while cur < END:
        key = str(cur.date())
        ws, we = cur, min(cur + pd.Timedelta(days=WINDOW_DAYS), END)
        if key not in done_set:
            try:
                rows = fetch_window(ws, we)
            except RuntimeError as ex:
                state["errors"].append(f"{key}: {ex}")
                save_state(state)
                save_status(state, key, False, str(ex))
                print(f"window {key} persistent failure -> checkpoint "
                      f"stop (resumable)", flush=True)
                return 3
            month_key = str(ws)[:7].replace("-", "")
            if cur_month is None or month_key != cur_month:
                if cur_month is not None:
                    flush_month(cur_month, buf)
                cur_month = month_key
                buf = []
                mpath = month_chunk_path(cur_month)
                if os.path.exists(mpath):
                    buf = pd.read_parquet(mpath).to_dict("records")
            buf.extend(rows)
            state["windows_done"].append(key)
            state["rows_total"] += len(rows)
            done_set.add(key)
            n_done += 1
            if n_done % 10 == 0:
                save_state(state)
                save_status(state, key, False)
                print(f"  stage1 {n_done}/{total_windows} windows, "
                      f"{state['rows_total']} rows ({time.time()-t0:.0f}s)",
                      flush=True)
        cur = we
    if cur_month is not None:
        flush_month(cur_month, buf)
    state["stage"] = 2
    save_state(state)
    save_status(state, None, False)
    print(f"stage1 COMPLETE: {state['rows_total']} rows -> stage2 fallback",
          flush=True)
    return stage2(state)


if __name__ == "__main__":
    sys.exit(main())
