"""Daily popularity-ranking (人气榜) forward-collect snapshot - P-C v1.

O-20260923-1850 engineering lane (循环轮·工程部), HEAT_ATTENTION_SPEC §2C/§4.
Pure forward accumulation: the guba rank list is a LIVE rolling ranking with
no retrievable full history -> per spec §1 "前向采集" row, we snapshot it once
per day and never fabricate backtest history. Factor use joins by as_of date
with strict availability lag (no look-ahead) at the factor-build layer.

Source (bm-b r39 audit, DIGEST-20260923-heat-source-audit): EM emappdata
getAllCurrentList - the same endpoint akshare's stock_hot_rank_em wraps
(pageSize=100 = public 人气榜 top-100; pageSize>100 returns 0 rows, probed
2026-09-23). We take ONLY this one request: the akshare wrapper's second
call enriches with push2.eastmoney.com quotes, which (a) is the subdomain
bm-b observed IP-blocked and (b) duplicates prices we already have in bars.

Safety (update_daily / update_lhb paradigm):
  - direct route only: urllib + ProxyHandler({}) - Clash hijacks EM
    domains (J13 / bm-b r39 坑1); requests/env/registry proxies bypassed
  - window guard: weekday + >=15:30 local (post-close snapshot aligns with
    the daily bar; intraday snapshots would be a different dataset)
  - idempotent by date: one snapshot file per day, exists -> no-op exit 0
  - min re-attempt interval: last_attempt recorded in the status mirror
    BEFORE the network call (crash mid-fetch still throttles next round;
    EM datacenter citizenship - 1 request/day nominal)
  - atomic write: staged .tmp then os.replace
  - honest failure: fetch/validation fail -> no write, exit 2 verbatim
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

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEAT_DIR = os.path.join(ROOT, "data", "heat", "popularity")
STATUS = os.path.join(ROOT, "results", "heat_update_status.json")

CLOSE_ACCEPT_TIME = dt.time(15, 30)   # post-close snapshot convention
MIN_ATTEMPT_INTERVAL = 30 * 60        # min seconds between network attempts
ENDPOINT = "https://emappdata.eastmoney.com/stockrank/getAllCurrentList"
PAGE_SIZE = 100                      # public top-100 (endpoint cap, probed)
MIN_ROWS = 50                        # validation floor (expect exactly 100)
SC_RE = re.compile(r"^(SH|SZ)(\d{6})$")
RETRY_SLEEP = 3                      # one retry, emappdata flakiness (r39)


def save_status(payload):
    os.makedirs(os.path.dirname(STATUS), exist_ok=True)
    payload["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(STATUS, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)


def load_status():
    if os.path.exists(STATUS):
        try:
            with open(STATUS, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def snapshot_gate(now, today_file, last_attempt):
    """(should_fetch, reason). Window + idempotence first, then the
    min re-attempt interval (EM throttle citizenship)."""
    if now.weekday() >= 5:
        return False, "no-op: weekend (no trading-day snapshot)"
    if now.time() < CLOSE_ACCEPT_TIME:
        return False, (f"no-op: before {CLOSE_ACCEPT_TIME} "
                       "(post-close snapshot window)")
    if os.path.exists(today_file):
        return False, f"no-op: snapshot for {now.date()} already collected"
    if (last_attempt is not None
            and (now - last_attempt).total_seconds() < MIN_ATTEMPT_INTERVAL):
        return False, (f"no-op: <{MIN_ATTEMPT_INTERVAL // 60}min since last "
                       "fetch attempt (min-interval guard)")
    return True, f"fetch: {now.date()} snapshot missing, in window"


def fetch_rank_rows():
    """One direct-route POST -> list of raw {sc, rk, ...} dicts."""
    payload = json.dumps({"appId": "appId01",
                          "globalId": "786e4c21-70dc-435a-93bb-38",
                          "marketType": "", "pageNo": 1,
                          "pageSize": PAGE_SIZE}).encode()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    last_ex = None
    for _ in range(2):  # one retry; emappdata route observed flaky (r39)
        try:
            req = urllib.request.Request(
                ENDPOINT, data=payload,
                headers={"Content-Type": "application/json",
                         "User-Agent": "Mozilla/5.0"})
            with opener.open(req, timeout=12) as r:
                data = json.loads(r.read().decode("utf-8"))
            rows = data.get("data") or []
            if rows:
                return rows, None
            last_ex = RuntimeError("endpoint returned 0 rows "
                                   f"(payload keys={sorted(data.keys())})")
        except Exception as ex:  # noqa: BLE001
            last_ex = ex
        time.sleep(RETRY_SLEEP)
    return [], last_ex


def canonical_rows(raw_rows):
    """Validate + project to the frozen schema. Any schema drift raises."""
    out = []
    seen = set()
    for row in raw_rows:
        m = SC_RE.match(str(row.get("sc", "")))
        if not m:
            raise ValueError(f"bad sc field: {row.get('sc')!r}")
        rank = int(row["rk"])
        if not (1 <= rank <= 1000):
            raise ValueError(f"rank out of range: {rank}")
        code = m.group(2)
        if code in seen:
            raise ValueError(f"duplicate code in list: {code}")
        seen.add(code)
        out.append({"code": code, "market": m.group(1), "rank": rank,
                    "rc": row.get("rc"), "hisrc": row.get("hisRc"),
                    "raw_sc": row["sc"]})
    ranks = sorted(r["rank"] for r in out)
    if ranks != list(range(1, len(out) + 1)):
        raise ValueError(f"ranks not a 1..N permutation: {ranks[:5]}...")
    return out


def write_snapshot(path, rows, now):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    doc = {"as_of": str(now.date()),
           "fetched_at": now.strftime("%Y-%m-%d %H:%M:%S"),
           "source": "emappdata getAllCurrentList (direct)",
           "n_rows": len(rows), "rows": rows}
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def main():
    now = pd.Timestamp.now()
    today_file = os.path.join(
        HEAT_DIR, f"{now.strftime('%Y%m%d')}.json")
    prev = load_status()
    last_attempt = prev.get("last_attempt")
    if isinstance(last_attempt, str):
        try:
            last_attempt = pd.Timestamp(last_attempt)
        except Exception:
            last_attempt = None

    should, reason = snapshot_gate(now, today_file, last_attempt)
    print(reason, flush=True)
    if not should:
        save_status({"verdict": reason,
                     "snapshots": count_snapshots(),
                     "last_attempt": prev.get("last_attempt")})
        return 0

    # record the attempt BEFORE the network call: a crash mid-fetch must
    # still throttle the next round (EM datacenter citizenship)
    save_status({"verdict": "fetching", "snapshots": count_snapshots(),
                 "last_attempt": str(now)})

    raw, ex = fetch_rank_rows()
    if ex is not None:
        save_status({"verdict": f"fetch_fail: {type(ex).__name__}: "
                                f"{str(ex)[:160]}",
                     "snapshots": count_snapshots(),
                     "last_attempt": str(now)})
        print(f"FETCH FAIL {type(ex).__name__}: {str(ex)[:160]}", flush=True)
        return 2
    try:
        rows = canonical_rows(raw)
        if len(rows) < MIN_ROWS:
            raise ValueError(f"only {len(rows)} rows < floor {MIN_ROWS}")
    except Exception as ve:  # noqa: BLE001
        save_status({"verdict": f"validation_fail: {str(ve)[:160]}",
                     "snapshots": count_snapshots(),
                     "last_attempt": str(now)})
        print(f"VALIDATION FAIL: {str(ve)[:160]}", flush=True)
        return 2

    write_snapshot(today_file, rows, now.to_pydatetime())
    save_status({"verdict": f"snapshot {now.date()} landed",
                 "snapshots": count_snapshots(),
                 "n_rows": len(rows), "last_attempt": str(now)})
    print(f"snapshot landed: {now.date()} n_rows={len(rows)} "
          f"(total snapshots={count_snapshots()})", flush=True)
    return 0


def count_snapshots():
    if not os.path.isdir(HEAT_DIR):
        return 0
    return len([f for f in os.listdir(HEAT_DIR) if f.endswith(".json")])


def selftest():
    """Offline guard tests: window/idempotence/throttle gates, schema
    validation, atomic write. Zero network; file ops in a tempdir."""
    ts = pd.Timestamp

    gate_cases = [
        ("Sat 20:00 weekend", "2026-09-26 20:00", False, "weekend"),
        ("Wed 15:00 pre-close", "2026-09-23 15:00", False, "before"),
        ("Wed 15:31 in window", "2026-09-23 15:31", True, None),
        ("Wed 20:00 in window", "2026-09-23 20:00", True, None),
    ]
    for name, now_s, want_fetch, want_sub in gate_cases:
        with tempfile.TemporaryDirectory() as td:
            tf = os.path.join(td, "x.json")
            if "already" in name:
                open(tf, "w").close()
            should, reason = snapshot_gate(ts(now_s), tf, None)
            assert should == want_fetch, f"{name}: {reason}"
            if want_sub:
                assert want_sub in reason, f"{name}: {reason}"
            print(f"[PASS] snapshot_gate {name}", flush=True)

    with tempfile.TemporaryDirectory() as td:
        tf = os.path.join(td, "x.json")
        open(tf, "w").close()  # today's snapshot exists
        should, reason = snapshot_gate(ts("2026-09-23 20:00"), tf, None)
        assert not should and "already" in reason, f"idempotence: {reason}"
        print(f"[PASS] snapshot_gate already collected -> no-op", flush=True)

    la_cases = [
        ("fresh attempt -> throttled", "2026-09-23 19:50", False),
        ("stale attempt -> fetch", "2026-09-23 10:00", True),
    ]
    for name, la_s, want in la_cases:
        with tempfile.TemporaryDirectory() as td:
            should, reason = snapshot_gate(ts("2026-09-23 20:00"),
                                           os.path.join(td, "x.json"),
                                           ts(la_s))
            assert should == want, f"{name}: {reason}"
            print(f"[PASS] snapshot_gate {name}", flush=True)

    good = [{"sc": "SH600418", "rk": 1, "rc": 0, "hisRc": 7},
            {"sc": "SZ000001", "rk": 2, "rc": -1, "hisRc": 3}]
    rows = canonical_rows(good)
    assert rows[0]["code"] == "600418" and rows[0]["rank"] == 1
    assert rows[1]["market"] == "SZ" and rows[1]["hisrc"] == 3
    print("[PASS] canonical_rows projection", flush=True)

    bads = [
        ("bad sc", [{"sc": "XX12345", "rk": 1}]),
        ("rank out of range", [{"sc": "SH600418", "rk": 0}]),
        ("duplicate code", [{"sc": "SH600418", "rk": 1},
                            {"sc": "SH600418", "rk": 2}]),
        ("rank gap", [{"sc": "SH600418", "rk": 1},
                      {"sc": "SZ000001", "rk": 3}]),
    ]
    for name, raw in bads:
        try:
            canonical_rows(raw)
            raise AssertionError(f"{name}: not rejected")
        except (ValueError, KeyError):
            print(f"[PASS] canonical_rows rejects {name}", flush=True)

    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "snap.json")
        write_snapshot(p, canonical_rows(good), dt.datetime(2026, 9, 23, 20, 1))
        with open(p, encoding="utf-8") as f:
            doc = json.load(f)
        assert doc["as_of"] == "2026-09-23" and doc["n_rows"] == 2
        assert doc["rows"][1]["code"] == "000001"
        assert not os.path.exists(p + ".tmp")
        print("[PASS] write_snapshot atomic+schema", flush=True)

    print("selftest: all guard cases PASS", flush=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    sys.exit(main())
