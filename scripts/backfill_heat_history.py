"""L2 per-stock popularity rank-history backfill - P-C follow-up leg.

O-20260923-1850 engineering lane (循环轮·数据+工程部), PC_COLLECTOR §4 L2,
claim MSG-20260923-2105. bm-b r39 audit probed this source at 366 bars;
one-shot BACKFILL of the *current* top-100 popularity members, NOT a daily
S6 chain job (the rolling list itself is forward-collected by update_heat).

Source (same emappdata domain as update_heat, direct-route verified from
bm-a 2026-09-23, probe SH600418):
  POST /stockrank/getHisList        -> [{calcTime: YYYY-MM-DD, rank}, ...]
  POST /stockrank/getHisProfileList-> [{calcTime: ... 23:00:00, newUidRate:
                                        '18.07%', oldUidRate: '81.93%'}, ...]
  payload = appId01 + globalId + srcSecurityCode (SH600418) + yearType '5'
Dataset era starts 2025-09-23 (366 rows = ~1 year window cap, probed).

HONESTY CAVEAT (PC_COLLECTOR §3): the full-market daily cross-section does
NOT exist - we backfill only members of today's top-100 snapshot = strong
selection bias (stocks popular *now*). Any factor batch consuming this
must declare the forward window start + survivorship clause. Files are
frozen at fetch time; the daily snapshot leg (L1) keeps accumulating the
universe going forward.

Safety (update_heat / update_lhb paradigm):
  - direct route only: urllib + ProxyHandler({}) (Clash hijacks EM domains)
  - resumable: per-stock checkpoint files, valid ones skipped on re-run
  - throttle: >=2.5s between requests (EM datacenter citizenship),
    1 retry + 8s backoff per request, 5 consecutive stock-level failures
    -> fuse abort exit 2 (checkpoint preserved, next round resumes)
  - atomic write: staged .tmp then os.replace, one file per stock
  - honest failure: validation gate fails -> no write, exit 2 verbatim
  - `selftest` subcommand: offline guard tests, zero network, tempdir only
"""
import datetime as dt
import json
import os
import re
import sys
import tempfile
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POP_DIR = os.path.join(ROOT, "data", "heat", "popularity")
HIST_DIR = os.path.join(ROOT, "data", "heat", "rank_history")
STATUS = os.path.join(ROOT, "results", "heat_backfill_status.json")

ENDPOINT = "https://emappdata.eastmoney.com/stockrank"
THROTTLE_S = 2.5                      # min interval between ANY requests
RETRY_BACKOFF_S = 8                    # per-request retry backoff
FUSE_CONSEC_FAILS = 5                  # consecutive stock fails -> abort
MIN_ROWS = 30                          # sanity floor (new IPOs shorter ok)
SC_RE = re.compile(r"^(SH|SZ)(\d{6})$")
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
REQ_TIMEOUT = 15


def post_direct(url, payload):
    """One direct-route POST -> parsed json. Raises on any failure."""
    body = json.dumps(payload).encode()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    with opener.open(req, timeout=REQ_TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))


def base_payload(sec):
    return {"appId": "appId01", "globalId": "786e4c21-70dc-435a-93bb-38",
            "marketType": "", "srcSecurityCode": sec, "yearType": "5"}


def find_latest_snapshot():
    """Newest data/heat/popularity/YYYYMMDD.json -> (path, doc). None if
    the L1 forward-collect leg has produced nothing yet (honest gate)."""
    if not os.path.isdir(POP_DIR):
        return None, None
    cands = sorted(f for f in os.listdir(POP_DIR)
                   if re.match(r"^\d{8}\.json$", f))
    if not cands:
        return None, None
    path = os.path.join(POP_DIR, cands[-1])
    with open(path, encoding="utf-8") as f:
        return path, json.load(f)


def pct_to_float(s):
    """'18.07%' -> 0.1807 ; None/'' -> None."""
    if s is None:
        return None
    s = str(s).strip().rstrip("%").strip()
    if not s or s in ("-", "--"):
        return None
    return round(float(s) / 100.0, 6)


def merge_rows(rank_rows, profile_rows):
    """Merge the two per-stock legs into the frozen schema, validating
    as we go. rank rows REQUIRED (inner), profile rates OPTIONAL by date.
    Raises ValueError on any schema/semantic drift."""
    by_date = {}
    for r in rank_rows:
        d = str(r.get("calcTime", ""))[:10]
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            raise ValueError(f"bad rank calcTime: {r.get('calcTime')!r}")
        if d in by_date:
            raise ValueError(f"duplicate rank date: {d}")
        rank = int(r["rank"])
        if not (1 <= rank <= 100000):
            raise ValueError(f"rank out of range: {rank}")
        by_date[d] = {"date": d, "rank": rank,
                     "new_uid_rate": None, "old_uid_rate": None}
    prof_n = 0
    for p in profile_rows or []:
        m = DATE_RE.match(str(p.get("calcTime", "")))
        if not m:
            raise ValueError(f"bad profile calcTime: {p.get('calcTime')!r}")
        d = m.group(1)
        row = by_date.get(d)
        if row is None:
            continue  # profile leg may lag the rank leg; skip silently
        new = pct_to_float(p.get("newUidRate"))
        old = pct_to_float(p.get("oldUidRate"))
        if new is not None and not (0.0 <= new <= 1.0):
            raise ValueError(f"newUidRate out of range: {new}")
        if old is not None and not (0.0 <= old <= 1.0):
            raise ValueError(f"oldUidRate out of range: {old}")
        if new is not None and old is not None and abs(new + old - 1.0) > 0.02:
            raise ValueError(f"rates don't sum to 1: {new}+{old}")
        row["new_uid_rate"] = new
        row["old_uid_rate"] = old
        prof_n += 1
    rows = [by_date[d] for d in sorted(by_date)]
    return rows, prof_n


def validate_rows(rows):
    """Per-stock gate. Raises ValueError; caller must not write on fail."""
    if len(rows) < MIN_ROWS:
        raise ValueError(f"only {len(rows)} rows < floor {MIN_ROWS}")
    prev = ""
    for row in rows:
        if row["date"] <= prev:
            raise ValueError(f"dates not strictly increasing at {row['date']}")
        prev = row["date"]


def stock_file(sec):
    return os.path.join(HIST_DIR, f"{sec}.json")


def file_is_valid(path):
    """Checkpoint validation for resume-skip: load + re-run gates."""
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        rows = doc["rows"]
        validate_rows(rows)
        return len(rows) == doc["n_rows"]
    except Exception:  # noqa: BLE001
        return False


def write_stock(path, sec, rows, prof_n, now):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    doc = {"sc": sec, "fetched_at": now, "source": "emappdata "
           "getHisList+getHisProfileList (direct)", "n_rows": len(rows),
           "profile_coverage": prof_n,
           "date_min": rows[0]["date"], "date_max": rows[-1]["date"],
           "rows": rows}
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def save_status(payload):
    os.makedirs(os.path.dirname(STATUS), exist_ok=True)
    payload["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(STATUS, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)


class Throttler:
    """Global request clock: >=THROTTLE_S between any two requests."""

    def __init__(self, interval=THROTTLE_S):
        self.interval = interval
        self.last = 0.0
        self.n_requests = 0

    def wait(self):
        delta = time.time() - self.last
        if delta < self.interval:
            time.sleep(self.interval - delta)
        self.last = time.time()
        self.n_requests += 1


def fetch_stock(sec, throttler):
    """Two throttled requests (retry x2 each) -> (rows, prof_n). Raises."""
    payload = base_payload(sec)
    rank_rows, profile_rows = None, None
    for url_suffix, key in (("getHisList", "rank"),
                            ("getHisProfileList", "profile")):
        data = None
        for attempt in range(2):
            throttler.wait()
            try:
                data = post_direct(f"{ENDPOINT}/{url_suffix}", payload)
                break
            except Exception:  # noqa: BLE001
                if attempt == 1:
                    raise
                time.sleep(RETRY_BACKOFF_S)
        rows = data.get("data") or []
        if not rows:
            raise ValueError(f"{key} leg returned 0 rows")
        if key == "rank":
            rank_rows = rows
        else:
            profile_rows = rows
    return merge_rows(rank_rows, profile_rows)


def main():
    snap_path, snap = find_latest_snapshot()
    if snap_path is None:
        print("no L1 popularity snapshot found - run update_heat.py first",
              flush=True)
        save_status({"verdict": "no snapshot: L1 leg empty"})
        return 2
    secs = []
    for row in snap["rows"]:
        sec = f"{row['market']}{row['code']}"
        if SC_RE.match(sec):
            secs.append(sec)
    if not secs:
        print(f"snapshot {snap_path} has no valid sc codes", flush=True)
        save_status({"verdict": "no valid codes in snapshot"})
        return 2

    now = time.strftime("%Y-%m-%d %H:%M:%S")
    throttler = Throttler()
    n_skip = n_done = 0
    failures = []
    consec = 0
    short_rows = []
    era_min, era_max = "9999-99-99", ""

    for sec in secs:
        path = stock_file(sec)
        if os.path.exists(path) and file_is_valid(path):
            n_skip += 1
            print(f"[skip] {sec} (checkpoint valid)", flush=True)
            continue
        try:
            rows, prof_n = fetch_stock(sec, throttler)
            validate_rows(rows)
            write_stock(path, sec, rows, prof_n, now)
            n_done += 1
            consec = 0
            if len(rows) < 366:
                short_rows.append({"sc": sec, "n_rows": len(rows)})
            era_min = min(era_min, rows[0]["date"])
            era_max = max(era_max, rows[-1]["date"])
            print(f"[done] {sec} n_rows={len(rows)} "
                  f"({rows[0]['date']}..{rows[-1]['date']})", flush=True)
        except Exception as ex:  # noqa: BLE001
            failures.append({"sc": sec, "error": f"{type(ex).__name__}: "
                                                 f"{str(ex)[:120]}"})
            consec += 1
            print(f"[FAIL] {sec} {type(ex).__name__}: {str(ex)[:120]}",
                  flush=True)
            if consec >= FUSE_CONSEC_FAILS:
                print(f"FUSE: {FUSE_CONSEC_FAILS} consecutive fails - "
                      "aborting (checkpoint preserved, resume next round)",
                      flush=True)
                break

    done_all = (n_skip + n_done + len(failures) >= len(secs)
                and not failures)
    status = {"verdict": "backfill complete" if done_all else
              f"incomplete: {len(failures)} fails (resume next round)",
              "target_snapshot": os.path.basename(snap_path),
              "n_target": len(secs), "n_skip_existing": n_skip,
              "n_done_run": n_done, "n_fail": len(failures),
              "failures": failures[:20],
              "short_history_stocks": short_rows[:20],
              "n_files_total": len([f for f in os.listdir(HIST_DIR)
                                    if f.endswith(".json")])
              if os.path.isdir(HIST_DIR) else 0,
              "dataset_era": {"date_min": era_min or None,
                              "date_max": era_max or None}}
    save_status(status)
    print(f"backfill: target={len(secs)} done_run={n_done} "
          f"skip={n_skip} fail={len(failures)}", flush=True)
    return 0 if done_all else 2


def selftest():
    """Offline guard tests: merge/validation/checkpoint-skip/fuse.
    Zero network; file ops in a tempdir."""
    rank_rows = [{"calcTime": "2026-09-21", "rank": 10},
                 {"calcTime": "2026-09-22", "rank": 5},
                 {"calcTime": "2026-09-23", "rank": 1}]
    prof_rows = [{"calcTime": "2026-09-21 23:00:00", "newUidRate": "20.00%",
                  "oldUidRate": "80.00%"},
                 {"calcTime": "2026-09-22 23:00:00", "newUidRate": "18.07%",
                  "oldUidRate": "81.93%"},
                 {"calcTime": "2026-09-24 23:00:00", "newUidRate": "1.00%",
                  "oldUidRate": "99.00%"}]  # future-orphan row -> skipped
    rows, prof_n = merge_rows(rank_rows, prof_rows)
    assert len(rows) == 3 and prof_n == 2
    assert rows[0]["rank"] == 10 and rows[0]["old_uid_rate"] == 0.8
    assert rows[1]["new_uid_rate"] == 0.1807
    assert rows[2]["new_uid_rate"] is None  # orphan profile not merged
    print("[PASS] merge_rows join+projection+orphan-skip", flush=True)

    bads = [
        ("duplicate rank date", [{"calcTime": "2026-09-21", "rank": 1},
                                 {"calcTime": "2026-09-21", "rank": 2}], []),
        ("rank out of range", [{"calcTime": "2026-09-21", "rank": 0}], []),
        ("bad calcTime", [{"calcTime": "x", "rank": 1}], []),
        ("rates don't sum", [{"calcTime": "2026-09-21", "rank": 1}],
         [{"calcTime": "2026-09-21 23:00:00", "newUidRate": "50.00%",
           "oldUidRate": "20.00%"}]),
        ("rate out of range", [{"calcTime": "2026-09-21", "rank": 1}],
         [{"calcTime": "2026-09-21 23:00:00", "newUidRate": "150.00%",
           "oldUidRate": "-50.00%"}]),
    ]
    for name, rr, pr in bads:
        try:
            merge_rows(rr, pr)
            raise AssertionError(f"{name}: not rejected")
        except (ValueError, KeyError):
            print(f"[PASS] merge_rows rejects {name}", flush=True)

    rows_ok = [{"date": f"2026-09-{d:02d}", "rank": d, "new_uid_rate": None,
                "old_uid_rate": None} for d in range(1, 31)]
    validate_rows(rows_ok)
    print("[PASS] validate_rows 30-row monotonic", flush=True)
    try:
        validate_rows(rows_ok[::-1])
        raise AssertionError("non-monotonic accepted")
    except ValueError:
        print("[PASS] validate_rows rejects non-monotonic", flush=True)
    try:
        validate_rows(rows_ok[:10])
        raise AssertionError("below floor accepted")
    except ValueError:
        print("[PASS] validate_rows rejects below floor", flush=True)

    assert pct_to_float("18.07%") == 0.1807
    assert pct_to_float(None) is None and pct_to_float("-") is None
    print("[PASS] pct_to_float", flush=True)

    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "SH600418.json")
        write_stock(path, "SH600418", rows_ok, 30, "2026-09-23 21:00:00")
        assert file_is_valid(path)
        assert not os.path.exists(path + ".tmp")
        print("[PASS] write_stock atomic + file_is_valid", flush=True)
        # corrupt checkpoint -> invalid -> would refetch
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        doc["rows"] = doc["rows"][:3]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f)
        assert not file_is_valid(path)
        print("[PASS] file_is_valid rejects corrupt checkpoint", flush=True)

    th = Throttler(interval=0.2)
    th.last = time.time()
    t0 = time.time()
    th.wait(); th.wait()
    assert th.n_requests == 2 and time.time() - t0 >= 0.2
    print("[PASS] throttler min interval", flush=True)

    snap_bad = {"rows": [{"market": "XX", "code": "123", "rank": 1}]}
    secs = [f"{r['market']}{r['code']}" for r in snap_bad["rows"]
            if SC_RE.match(f"{r['market']}{r['code']}")]
    assert secs == []
    print("[PASS] SC_RE filter rejects malformed codes", flush=True)

    print("selftest: all guard cases PASS", flush=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    sys.exit(main())
