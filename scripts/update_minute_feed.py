"""T-104 s1: sina 1-minute-K forward-accumulation archive collector.

Job: on each gated run, fetch the sina 1m rolling window (~2000 bars) for
the pinned grid-candidate universe (T-103 category map seed) and merge it
into the forward-accumulation archive data/minute_feed/<code>.csv --
append-only by bar timestamp; overlapping rows must match the local copy
byte-for-byte or the run aborts exit 3 (source-history-rewrite) with the
local file untouched.  Deep intraday history does not exist; the archive
is BUILT from now (forward-accumulation law, same design as the sentiment
collectors).  Spec = research/etf_ops/MINUTE_FEED.md v1.0 (frozen).

Source (GM probe 2026-09-28 15:30, O-20260928-1531 -- cite, no re-probe):
ak.stock_zh_a_minute(symbol='sh510300', period='1') = 1970 real bars.
Rolling window ~8+ trading days -> throttled runs merge losslessly via
overlap; a machine offline longer than the window LOSES the bars before
it (gap disclosed honestly in status, never fabricated).

Gates (spec sec.5):
  - lane host = bm-b only (R31 precedent); other machines = stdout-only
    honest no-op exit 0
  - non-workday OR before 09:15 -> legal no-op exit 0
  - <20min since last success -> no-op (throttle; overlap makes it
    lossless)
  - --force bypasses clock/throttle for pipeline validation, stamped
    kind="forced" (data still real source bars)

Atomicity: fetch ALL symbols first (any failure -> exit 2, zero writes),
verify ALL overlaps (any mismatch -> exit 3, zero writes), then write.

Usage:
    python scripts/update_minute_feed.py             # gated run
    python scripts/update_minute_feed.py --force     # validation run
    python scripts/update_minute_feed.py selftest    # hermetic offline
Exit codes: 0 = ok/no-op, 2 = source/mechanism failure (honest),
            3 = overlap mismatch (source rewrote history; local intact).
"""
import datetime as dt
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MACHINE_JSON = os.path.join(ROOT, "fleet", "machine.json")
FEED_DIR = os.path.join(ROOT, "data", "minute_feed")
STATUS_JSON = os.path.join(ROOT, "results", "minute_feed_status.json")

LANE_OWNER = "bm-b"          # T-104 s1 lane host (R31 precedent)
THROTTLE_MIN = 20            # spec sec.5
OPEN_GATE_T = dt.time(9, 15)
ATTEMPTS = 3
BACKOFF_S = (5, 10)
PERIOD = "1"

# T-103 category map seed -- spec sec.3 FROZEN
UNIVERSE = [
    ("510300", "broad-base", "T+1"),
    ("511010", "bond", "T+0"),
    ("511880", "money", "T+0"),
    ("511990", "money", "T+0"),
    ("513100", "crossborder", "T+0"),
    ("518880", "gold", "T+0"),
]
COLS = ("day", "open", "high", "low", "close", "volume", "amount")
NUM_COLS = ("open", "high", "low", "close", "volume", "amount")


# ------------------------------ helpers -------------------------------------

def _norm_day(raw) -> str:
    """Validate + normalize bar timestamp to 'YYYY-MM-DD HH:MM:SS'."""
    s = str(raw).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return dt.datetime.strptime(s, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    raise RuntimeError(f"bar timestamp not parseable: {s!r}")


def _norm_rows(records) -> list:
    """Normalize raw source dicts -> sorted, deduped tuple rows
    (day, open, high, low, close, volume), all values verbatim strings."""
    rows = {}
    for rec in records:
        day = _norm_day(rec["day"])
        vals = []
        for c in NUM_COLS:
            v = str(rec[c]).strip()
            float(v)                       # numeric sanity, verbatim store
            vals.append(v)
        row = (day, *vals)
        prev = rows.get(day)
        if prev is not None and prev != row:
            raise RuntimeError(f"conflicting duplicate bar {day}")
        rows[day] = row
    return [rows[k] for k in sorted(rows)]


def _merge_rows(local_rows, fetch_rows):
    """Pure merge (spec sec.4): append-only by day, overlap must match
    byte-for-byte.  Returns (new_rows, ok, mismatch_ts)."""
    if not local_rows:
        return list(fetch_rows), True, None
    local_max = local_rows[-1][0]
    local_map = {r[0]: r for r in local_rows}
    new_rows = []
    for row in fetch_rows:
        ts = row[0]
        if ts in local_map:
            if local_map[ts] != row:
                return None, False, ts
        elif ts > local_max:
            new_rows.append(row)
    return new_rows, True, None


def _read_local(path) -> list:
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, encoding="utf-8-sig") as fh:
        header = fh.readline().strip()
        if header != ",".join(COLS):
            raise RuntimeError(f"schema drift in {path}: {header!r}")
        for line in fh:
            line = line.strip()
            if line:
                parts = tuple(line.split(","))
                if len(parts) != len(COLS):
                    raise RuntimeError(
                        f"malformed row in {path}: {line[:60]!r}")
                rows.append(parts)
    return rows


def _write_local(path, rows) -> None:
    """Atomic full rewrite (tmp + os.replace); byte-identical on rerun."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(",".join(COLS) + "\n")
        for r in rows:
            fh.write(",".join(r) + "\n")
    os.replace(tmp, path)


def _fetch_symbol(code) -> list:
    """Fetch + normalize the sina 1m rolling window; 3 attempts, honest."""
    import akshare as ak
    last_err = None
    for i in range(ATTEMPTS):
        try:
            df = ak.stock_zh_a_minute(symbol=f"sh{code}", period=PERIOD)
            if df is None or len(df) == 0:
                raise RuntimeError("empty frame")
            if list(df.columns) != list(COLS):
                raise RuntimeError(
                    f"column drift {list(df.columns)} != {list(COLS)}")
            return _norm_rows(df.to_dict("records"))
        except Exception as exc:                               # noqa: BLE001
            last_err = exc
            time.sleep(BACKOFF_S[min(i, len(BACKOFF_S) - 1)])
    raise RuntimeError(
        f"source failed for {code} after {ATTEMPTS} attempts: {last_err}")


def _load_status():
    if os.path.exists(STATUS_JSON):
        try:
            with open(STATUS_JSON, encoding="utf-8-sig") as fh:
                return json.load(fh)
        except Exception:                                      # noqa: BLE001
            pass                        # torn status -> full recompute
    return {}


def _write_status(payload, mid):
    """Shared face + lane file (D-03(1) dual-face convention)."""
    for path in (STATUS_JSON,
                 os.path.join(ROOT, "results",
                              f"minute_feed_status.{mid}.json")):
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, path)


# ------------------------------ main faces ----------------------------------

def run(force: bool = False) -> int:
    with open(MACHINE_JSON, encoding="utf-8") as fh:
        mid = json.load(fh).get("machine_id", "")
    if mid != LANE_OWNER:
        print(f"update_minute_feed: lane guard (owner={LANE_OWNER}, "
              f"this={mid}) -- stdout-only honest no-op")
        return 0

    now = dt.datetime.now()
    status = _load_status()
    kind = "gated"
    if not force:
        if now.weekday() >= 5:
            print("update_minute_feed: non-workday -- no-op")
            return 0
        if now.time() < OPEN_GATE_T:
            print("update_minute_feed: before 09:15 -- no-op")
            return 0
        last = status.get("last_success_ts", "")
        if last:
            try:
                delta = (now - dt.datetime.fromisoformat(last)
                         ).total_seconds()
                if delta < THROTTLE_MIN * 60:
                    print(f"update_minute_feed: throttle ({int(delta/60)}min"
                          f" < {THROTTLE_MIN}min) -- no-op")
                    return 0
            except ValueError:
                pass                  # torn ts -> full recompute
    else:
        kind = "forced"

    os.makedirs(FEED_DIR, exist_ok=True)
    try:
        frames = {}
        for code, _cat, _t in UNIVERSE:
            frames[code] = _fetch_symbol(code)  # any failure -> exit 2

        plan = []
        for code, cat, tsettle in UNIVERSE:
            path = os.path.join(FEED_DIR, f"{code}.csv")
            local = _read_local(path)           # schema drift -> exit 2
            new_rows, ok, bad_ts = _merge_rows(local, frames[code])
            if not ok:
                print(f"update_minute_feed: OVERLAP MISMATCH {code} "
                      f"@ {bad_ts} -- source rewrote history; local "
                      "untouched (exit 3)")
                return 3
            gap = bool(local) and bool(
                frames[code]) and frames[code][0][0] > local[-1][0]
            plan.append((code, cat, tsettle, path, local, new_rows, gap))
    except Exception as exc:                                    # noqa: BLE001
        print(f"update_minute_feed: mechanism/source failure (exit 2) -- "
              f"{exc}")
        return 2

    symbols = {}
    total_new = 0
    for code, cat, tsettle, path, local, new_rows, gap in plan:
        _write_local(path, local + new_rows)
        total_new += len(new_rows)
        symbols[code] = {
            "category": cat, "t_settlement": tsettle,
            "rows_total": len(local) + len(new_rows),
            "rows_new": len(new_rows),
            "oldest_fetched": frames[code][0][0],
            "gap_vs_local": gap,
        }
        print(f"update_minute_feed: {code} +{len(new_rows)} rows"
              f" (total {len(local) + len(new_rows)})"
              + (" [GAP: bars before window lost]" if gap else ""))

    payload = {
        "face": "minute_feed_status",
        "lane_machine": mid,
        "kind": kind,
        "ts": now.isoformat(timespec="seconds"),
        "last_success_ts": now.isoformat(timespec="seconds"),
        "archive_dir": "data/minute_feed",
        "symbols": symbols,
        "rows_new_total": total_new,
        "spec": "research/etf_ops/MINUTE_FEED.md v1.1",
    }
    _write_status(payload, mid)
    print(f"update_minute_feed: done, +{total_new} rows across "
          f"{len(plan)} symbols (kind={kind})")
    return 0


# ------------------------------ selftest ------------------------------------

def selftest() -> int:
    import tempfile
    tmp = tempfile.mkdtemp(prefix="minute_feed_selftest_")
    fails = []

    def check(name, cond):
        print(f"  [{ 'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            fails.append(name)

    # [1] timestamp normalize: seconds form kept, minute form padded
    check("norm_day keeps seconds form",
          _norm_day("2026-09-28 14:55:00") == "2026-09-28 14:55:00")
    check("norm_day pads minute form",
          _norm_day("2026-09-28 14:55") == "2026-09-28 14:55:00")
    try:
        _norm_day("garbage")
        check("norm_day rejects garbage", False)
    except RuntimeError:
        check("norm_day rejects garbage", True)

    # [2] row normalize: verbatim strings, sorted, dup-conflict refused
    recs = [
        {"day": "2026-09-28 14:56", "open": "1.0", "high": "1.1",
         "low": "0.9", "close": "1.05", "volume": "100", "amount": "105"},
        {"day": "2026-09-28 14:55:00", "open": "1.0", "high": "1.1",
         "low": "0.9", "close": "1.04", "volume": "100", "amount": "104"},
    ]
    rows = _norm_rows(recs)
    check("norm_rows sorted + padded",
          rows == [("2026-09-28 14:55:00", "1.0", "1.1", "0.9", "1.04",
                    "100", "104"),
                   ("2026-09-28 14:56:00", "1.0", "1.1", "0.9", "1.05",
                    "100", "105")])
    try:
        _norm_rows(recs + [dict(recs[0], close="9.9")])
        check("norm_rows refuses conflicting dup", False)
    except RuntimeError:
        check("norm_rows refuses conflicting dup", True)

    # [3] merge: fresh / append / overlap-identical / mismatch
    local = [("2026-09-28 14:55:00", "1.0", "1.1", "0.9", "1.04", "100",
              "104")]
    fetch = [
        ("2026-09-28 14:55:00", "1.0", "1.1", "0.9", "1.04", "100",
         "104"),
        ("2026-09-28 14:56:00", "1.0", "1.1", "0.9", "1.05", "100",
         "105"),
    ]
    new, ok, bad = _merge_rows(local, fetch)
    check("merge appends only new", ok and new == fetch[1:] and bad is None)
    new, ok, bad = _merge_rows([], fetch)
    check("merge fresh file takes all", ok and new == fetch)
    bad_fetch = [fetch[0], fetch[1]]
    bad_fetch[0] = ("2026-09-28 14:55:00", "1.0", "1.1", "0.9", "1.05",
                    "100", "104")
    new, ok, bad = _merge_rows(local, bad_fetch)
    check("merge refuses overlap mismatch",
          (not ok) and bad == "2026-09-28 14:55:00")

    # [4] local I/O: write/read roundtrip, determinism, schema drift
    p = os.path.join(tmp, "t.csv")
    _write_local(p, fetch)
    _write_local(p, fetch)                    # rewrite = byte-identical
    check("write/read roundtrip", _read_local(p) == fetch)
    with open(p, "rb") as fh:
        b1 = fh.read()
    _write_local(p, fetch)
    with open(p, "rb") as fh:
        check("rewrite byte-identical", fh.read() == b1)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write("rogue\n")
    try:
        _read_local(p)
        check("read rejects malformed row", False)
    except Exception:
        check("read rejects malformed row", True)
    _write_local(p, fetch)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write("wrong,header\n")
    try:
        _read_local(p)
        check("read rejects schema drift", False)
    except RuntimeError:
        check("read rejects schema drift", True)

    # [5] gap disclosure logic (inline face of run(): gap = window start
    # after local max -- bars between are lost, disclosed never fabricated)
    stale_local = [("2026-09-28 14:00:00", "1.0", "1.1", "0.9", "1.04",
                    "100", "104")]
    check("gap true when window starts after local max",
          fetch[0][0] > stale_local[-1][0])
    check("gap false when window overlaps local max",
          not (fetch[0][0] > local[-1][0]))

    print(f"selftest: {'ALL PASS' if not fails else f'FAIL {fails}'}")
    return 0 if not fails else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        print("=== update_minute_feed selftest (hermetic, no network) ===")
        return selftest()
    force = "--force" in argv
    return run(force=force)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
