"""r281 bm-b: T-87 astock_daily full-universe pass mid-flight health probe.

Question (state r280 'next' pointer #1): is the detached first-pull pass
(5228 syms, spawned r280 23:47) on track to complete before the Mon
2026-09-28 09:15 first daily-continuation live fire?

Read-only w.r.t. the pass: only reads per/ files (atomic-write family,
no torn reads), lock, progress, status. Writes one dict-topped JSON
(r276 law: results/ root glob consumers require dict top level).

Anchors (r261 source-anchor law, no memory rebuild):
- frozen schema = ["date"] + BAR_COLS from scripts/update_astock_daily.py
  L85-86 (date,open,high,low,close,volume,amount,outstanding_share,
  turnover); probe cross-checks every sampled file header against the
  actual on-disk header AND this list (double face).
- rate face = per-file mtimes (collector writes one file per symbol).
- preexisting face = r280 6-symbol smoke files (status last_refresh
  fetched=6) are excluded from the rate numerator.
"""
import csv as _csv
import ctypes
import datetime as dt
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PER_DIR = os.path.join(ROOT, "data", "astock_daily", "per")
PROGRESS = os.path.join(ROOT, "data", "astock_daily", "_progress.json")
LOCK = os.path.join(ROOT, "data", "astock_daily", "_refresh.lock")
STATUS = os.path.join(ROOT, "results", "astock_daily_update_status.json")
OUT = os.path.join(ROOT, "results", "_r281bmb_astock_pass_probe.json")

FROZEN_FIELDS = ["date", "open", "high", "low", "close", "volume", "amount",
                 "outstanding_share", "turnover"]   # update_astock_daily.py L85-86
PREEXISTING_N = 6        # r280 smoke files (status last_refresh.fetched=6)
DEADLINE = dt.datetime(2026, 9, 28, 9, 15)   # Mon open: first live fire


def _pid_alive(pid):
    h = ctypes.windll.kernel32.OpenProcess(0x1000, False, int(pid))
    if not h:
        return False
    ctypes.windll.kernel32.CloseHandle(h)
    return True


def _last_line(path):
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - 4096))
        tail = f.read().decode("utf-8", "replace").rstrip("\n").splitlines()
    return tail[-1] if tail else ""


def main():
    now = dt.datetime.now()
    files = sorted(
        (os.path.join(PER_DIR, f) for f in os.listdir(PER_DIR)
         if f.endswith(".csv")),
        key=os.path.getmtime)
    n_done = len(files)

    status = json.load(io.open(STATUS, encoding="utf-8-sig"))
    universe_n = int((status.get("panel") or {}).get("universe_n") or 0)
    prog = json.load(io.open(PROGRESS, encoding="utf-8-sig"))
    attempts = prog.get("attempts") or {}
    quarantined = [c for c, n in attempts.items() if n >= 3]

    lock = json.load(io.open(LOCK, encoding="utf-8-sig")) if os.path.exists(LOCK) else None
    lock_alive = bool(lock) and _pid_alive(lock.get("pid", 0))

    # rate face: new files since pass start (spawn ts = lock ts)
    rate_face = {}
    eta_ts = None
    if lock and lock_alive:
        start = dt.datetime.fromisoformat(lock["ts"])
        n_new = max(0, n_done - PREEXISTING_N)
        elapsed_min = max(0.1, (now - start).total_seconds() / 60)
        rate_per_min = n_new / elapsed_min
        remaining = max(0, universe_n - n_done)
        eta_min = remaining / rate_per_min if rate_per_min > 0 else None
        eta_ts = (now + dt.timedelta(minutes=eta_min)).isoformat(timespec="seconds") \
            if eta_min is not None else None
        rate_face = {"n_new": n_new, "elapsed_min": round(elapsed_min, 1),
                     "rate_per_min": round(rate_per_min, 2),
                     "remaining": remaining,
                     "eta_ts": eta_ts}

    # shape face: every file header + tail-date census + 3-sample OHLC sanity
    header_mismatch = []
    tail_dates = {}
    ohlc_bad = []
    for idx, p in enumerate(files):
        with io.open(p, encoding="utf-8") as f:
            header = next(_csv.reader(f))
        if header != FROZEN_FIELDS:
            header_mismatch.append(os.path.basename(p))
        tdate = _last_line(p).split(",")[0]
        tail_dates[tdate] = tail_dates.get(tdate, 0) + 1
        if idx in (0, n_done // 2, n_done - 1):
            row = _last_line(p).split(",")
            try:
                d = dict(zip(header, row))
                o, h = float(d["open"]), float(d["high"])
                lo, c = float(d["low"]), float(d["close"])
                if not (h >= max(o, c) and lo <= min(o, c) and h >= lo
                        and float(d["volume"]) >= 0 and float(d["amount"]) >= 0):
                    ohlc_bad.append(os.path.basename(p))
            except Exception:
                ohlc_bad.append(os.path.basename(p))

    cutoff_expected = "2026-09-24"      # status panel.cutoff (Thu bar; Fri=mkt holiday)
    at_cutoff = tail_dates.get(cutoff_expected, 0)

    eta_ok = bool(eta_ts and dt.datetime.fromisoformat(eta_ts) < DEADLINE)
    verdict = "on_track" if (lock_alive and eta_ok and not header_mismatch
                             and not ohlc_bad) else "at_risk"
    out = {
        "ts": now.isoformat(timespec="seconds"),
        "round": "r281",
        "machine": "bm-b",
        "lane": "T-87 astock_daily supply (bm-b)",
        "pass_state": {
            "universe_n": universe_n,
            "per_files": n_done,
            "done_pct": round(100 * n_done / universe_n, 1) if universe_n else None,
            "lock": lock,
            "lock_alive": lock_alive,
            "attempts_n": len(attempts),
            "attempts": attempts,
            "quarantined": quarantined,
        },
        "rate_face": rate_face,
        "shape_face": {
            "frozen_fields": FROZEN_FIELDS,
            "header_mismatch": header_mismatch,
            "tail_date_census_top": sorted(tail_dates.items(),
                                           key=lambda kv: -kv[1])[:5],
            "files_at_expected_cutoff": at_cutoff,
            "ohlc_sanity_bad": ohlc_bad,
        },
        "monday_deadline": DEADLINE.isoformat(timespec="seconds"),
        "eta_ok_before_deadline": eta_ok,
        "verdict": verdict,
        "note": ("first-pull mid-flight; failed syms self-heal via file-derived "
                 "todo on next gate spawn (family law); probe read-only"),
    }
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in
                      ("ts", "verdict", "eta_ok_before_deadline")}, ensure_ascii=False))
    print(f"per_files={n_done}/{universe_n} rate={rate_face.get('rate_per_min')}/min "
          f"eta={eta_ts} at_cutoff={at_cutoff}/{n_done} "
          f"header_bad={len(header_mismatch)} ohlc_bad={len(ohlc_bad)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
