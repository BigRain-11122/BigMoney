"""LHB event history incremental refresh (P-A family pointer 4, claim
MSG-20260923-2045). Pure data engineering: zero IC, zero engine runs,
ledger N untouched.

Source-consistent with the original archive: ak.stock_lhb_detail_em
(EastMoney), same schema by construction. The original pipeline
(Money02/lhb_download.py) is quarterly-chunked and idempotent; this
refresh keeps that mechanism intact: re-fetch ONLY the quarter that
contains the current cutoff (superset overwrite of that one chunk),
then rebuild lhb_detail.parquet exactly the way the original script does
(concat all chunks). Appending to the parquet without the chunk would
desynchronize the two and a future re-run of the original downloader
would silently drop the appended rows.

Safety (update_daily paradigm):
  - overlap check: re-fetched rows with date <= cutoff must match the
    stored rows for the cutoff date (row count + net-buy sum, tol 1e-6);
    mismatch = source restated history -> write NOTHING, flag, exit 3
  - idempotent: no events beyond cutoff -> honest no-op exit 0
  - fetch failure -> no write, exit 2 (retry next run)
Write-domain (claim-scoped): the current-quarter chunk file,
lhb_detail.parquet, results/lhb_update_status.json. Nothing else.

S6 wiring guards (bm-a loop round 18, delegated by MSG-2045 item 4):
called from the iteration loop right after update_daily on a 10-minute
schedule, so the fetch gates must make polling safe for the throttled
EM datacenter (bm-b r39 finding + seat-pull 300s backoff evidence):
  - publish-window/cutoff gate: no network unless the stored cutoff is
    behind the latest POSSIBLE disclosure date (weekday evening window,
    weekends roll back to Friday)
  - min re-attempt interval: last_attempt recorded in the status mirror
    BEFORE the network call (crash mid-fetch still throttles next round)
  - `selftest` subcommand: offline guard tests, zero network zero writes
"""
import json
import os
import sys
import time

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LHB_DIR = os.path.join(ROOT, "Money02", "data", "lhb")
PARQUET = os.path.join(LHB_DIR, "lhb_detail.parquet")
CHUNKS = os.path.join(LHB_DIR, "chunks")
STATUS = os.path.join(ROOT, "results", "lhb_update_status.json")
TOL = 1e-6
PUBLISH_HOUR = 17                # LHB disclosures land ~17-19h local
MIN_ATTEMPT_INTERVAL = 30 * 60  # min seconds between network attempts


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


def expected_disclosure_date(now):
    """LHB trading-day events disclose in the evening (~17h+). Before the
    publish window - and on weekends - the freshest possible disclosure
    is the most recent weekday strictly before today."""
    today = now.normalize()
    if now.hour >= PUBLISH_HOUR and today.weekday() < 5:
        return today
    d = today - pd.Timedelta(days=1)
    while d.weekday() >= 5:
        d -= pd.Timedelta(days=1)
    return d


def fetch_gate(cutoff, now, last_attempt):
    """(should_fetch, reason). Publish-window/cutoff staleness first, then
    min re-attempt interval (EM datacenter throttle citizenship)."""
    expected = expected_disclosure_date(now)
    if cutoff >= expected:
        return False, (f"no-op: cutoff {cutoff.date()} covers latest "
                       f"disclosure window ({expected.date()})")
    if (last_attempt is not None
            and (now - last_attempt).total_seconds() < MIN_ATTEMPT_INTERVAL):
        return False, (f"no-op: <{MIN_ATTEMPT_INTERVAL // 60}min since last "
                       "fetch attempt (min-interval guard)")
    return True, (f"fetch: cutoff {cutoff.date()} behind expected "
                 f"disclosure {expected.date()}")


def rebuild_from_chunks():
    frames = []
    for name in sorted(os.listdir(CHUNKS)):
        if not name.endswith(".parquet"):
            continue
        p = os.path.join(CHUNKS, name)
        if os.path.getsize(p) == 0:
            continue
        frames.append(pd.read_parquet(p))
    full = pd.concat([f for f in frames if len(f)], ignore_index=True)
    full.to_parquet(PARQUET, index=False)
    return len(full)


def main():
    t0 = time.time()
    lhb = pd.read_parquet(PARQUET)
    dates = pd.to_datetime(lhb["上榜日"])
    cutoff = dates.max()
    q = pd.Period(cutoff, freq="Q")
    now = pd.Timestamp.now()
    prev = load_status()
    last_attempt = prev.get("last_attempt")
    if isinstance(last_attempt, str):
        try:
            last_attempt = pd.Timestamp(last_attempt)
        except Exception:
            last_attempt = None
    print(f"cutoff={cutoff.date()} quarter={q} today={now.date()}",
          flush=True)

    should, reason = fetch_gate(cutoff, now, last_attempt)
    print(reason, flush=True)
    if not should:
        save_status({"cutoff": str(cutoff.date()), "new_rows": 0,
                     "verdict": reason,
                     "last_attempt": prev.get("last_attempt")})
        return 0

    # record the attempt BEFORE the network call: a crash mid-fetch must
    # still throttle the next round (EM datacenter citizenship)
    save_status({"cutoff": str(cutoff.date()), "verdict": "fetching",
                 "last_attempt": str(now)})
    qs = q.start_time.strftime("%Y%m%d")
    qe = q.end_time.strftime("%Y%m%d")

    # ---- re-fetch the cutoff quarter (superset by construction)
    try:
        import akshare as ak
        df = ak.stock_lhb_detail_em(start_date=qs, end_date=qe)
    except Exception as ex:
        save_status({"cutoff": str(cutoff.date()), "verdict":
                     f"fetch_fail: {type(ex).__name__}: {str(ex)[:120]}",
                     "last_attempt": str(now)})
        print(f"FETCH FAIL {type(ex).__name__}: {str(ex)[:120]}", flush=True)
        return 2
    if df is None or df.empty:
        save_status({"cutoff": str(cutoff.date()), "new_rows": 0,
                     "verdict": "fetch returned empty (kept local)",
                     "last_attempt": str(now)})
        print("fetch empty - kept local", flush=True)
        return 0
    fd = pd.to_datetime(df["上榜日"])
    new = df[fd > cutoff]
    print(f"refetched quarter rows={len(df)} new_beyond_cutoff={len(new)}",
          flush=True)

    # ---- overlap check at the cutoff date
    old_day = lhb[pd.to_datetime(lhb["上榜日"]) == cutoff]
    new_day = df[fd == cutoff]
    ok_overlap = True
    detail = {"old_rows": int(len(old_day)), "new_rows": int(len(new_day))}
    if len(old_day) and len(new_day):
        old_sum = float(pd.to_numeric(old_day["龙虎榜净买额"],
                                      errors="coerce").sum())
        new_sum = float(pd.to_numeric(new_day["龙虎榜净买额"],
                                      errors="coerce").sum())
        detail["netbuy_sum_old"] = round(old_sum, 2)
        detail["netbuy_sum_new"] = round(new_sum, 2)
        ok_overlap = (len(old_day) == len(new_day)
                      and abs(old_sum - new_sum) <= max(TOL, abs(old_sum) * 1e-9))
    elif len(old_day) != len(new_day):
        ok_overlap = False
    if not ok_overlap:
        save_status({"cutoff": str(cutoff.date()),
                     "verdict": "overlap_mismatch: source restated history, "
                                "local kept untouched",
                     "overlap": detail})
        print(f"OVERLAP MISMATCH {detail} - kept local, no write", flush=True)
        return 3

    # ---- overwrite the cutoff quarter chunk, rebuild parquet
    if len(new) == 0:
        save_status({"cutoff": str(cutoff.date()), "new_rows": 0,
                     "verdict": "no-op (no events beyond cutoff yet)",
                     "overlap": detail, "last_attempt": str(now)})
        print("no events beyond cutoff yet - no-op", flush=True)
        return 0
    chunk_path = os.path.join(CHUNKS, f"{q}.parquet")
    df.to_parquet(chunk_path, index=False)
    total = rebuild_from_chunks()
    new_cutoff = str(pd.to_datetime(
        pd.read_parquet(PARQUET, columns=["上榜日"])["上榜日"]).max().date())
    save_status({"cutoff_before": str(cutoff.date()),
                 "cutoff_after": new_cutoff, "new_rows": int(len(new)),
                 "quarter_refetched": str(q), "total_rows": int(total),
                 "overlap": detail, "last_attempt": str(now),
                 "verdict": "updated"})
    print(f"updated: +{len(new)} rows, cutoff {cutoff.date()} -> "
          f"{new_cutoff}, total {total} ({time.time()-t0:.0f}s)", flush=True)
    return 0


def selftest():
    """Offline guard tests: disclosure-window/weekend dates, gate logic,
    min-interval. Zero network, zero writes."""
    ts = pd.Timestamp
    exp_cases = [
        ("Fri 16:00 pre-window", "2026-09-25 16:00", "2026-09-24"),
        ("Fri 17:30 in-window", "2026-09-25 17:30", "2026-09-25"),
        ("Sat 12:00 weekend", "2026-09-26 12:00", "2026-09-25"),
        ("Sat 18:00 weekend evening", "2026-09-26 18:00", "2026-09-25"),
        ("Sun 20:00 weekend evening", "2026-09-27 20:00", "2026-09-25"),
        ("Mon 09:00 pre-window", "2026-09-28 09:00", "2026-09-25"),
        ("Mon 18:30 in-window", "2026-09-28 18:30", "2026-09-28"),
    ]
    for name, now_s, want_s in exp_cases:
        got = expected_disclosure_date(ts(now_s))
        want = ts(want_s)
        assert got == want, f"{name}: got {got.date()} want {want.date()}"
        print(f"[PASS] expected_disclosure_date {name} -> {got.date()}",
              flush=True)

    gate_cases = [
        ("behind -> fetch", "2026-09-23", "2026-09-25 16:00", None, True),
        ("caught up -> no-op", "2026-09-25", "2026-09-26 18:00", None,
         False),
        ("fresh attempt -> throttled", "2026-09-23", "2026-09-25 16:00",
         "2026-09-25 15:50", False),
        ("stale attempt -> fetch", "2026-09-23", "2026-09-25 16:00",
         "2026-09-25 10:00", True),
    ]
    for name, cutoff_s, now_s, la_s, want_fetch in gate_cases:
        should, reason = fetch_gate(ts(cutoff_s), ts(now_s),
                                    ts(la_s) if la_s else None)
        assert should == want_fetch, f"{name}: got {should} ({reason})"
        print(f"[PASS] fetch_gate {name}", flush=True)
    print("selftest: all guard cases PASS", flush=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    sys.exit(main())
