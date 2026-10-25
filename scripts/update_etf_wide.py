"""Wide ETF daily panel refresh leg (the missing leg behind DIGEST-e35 / r1256).

Why this exists
---------------
`data/daily/*.csv` IS the price universe for every ETF study in this repo
(`tasks.backtest_task._load_prices` reads the whole directory).  Only five
members (510300/510050/510500/512100/588000) had a refresh leg, so the other
~1,720 files simply stopped printing at whatever day the 2026-09-22 bulk
bootstrap ended.  r1256 measured the damage on the trading face: on
2026-10-23 only 50 of 1,547 bond-removed ETFs carried a live close, and an
ungated ticket was 5/5 unbuyable.  This leg closes that hole.

Face / basis
------------
Same source and same basis as the five-member leg (`update_etf_daily`): the
sina klc_kl.js direct endpoint, which is AS-TRADED for ETFs (its qfq factor is
1.0 on every event).  The overlap check is therefore an identity check, not an
approximation: every local row present in the source must reproduce within
1e-6 on OHLC and +-1 on volume/amount, or that symbol is refused untouched.

Semantics
---------
- Append-only, per-symbol atomic write (.tmp + os.replace).
- Per-symbol isolation: one symbol's fetch failure or overlap mismatch never
  blocks the other ~1,720 (the five-member leg is all-or-nothing because five
  files are one frozen research face; this universe is not).
- Refuse to append anything that would break the file's monotonic date order,
  OHLC sanity, or positivity.
- Freshness gate: if every symbol already carries the latest COMPLETE bar
  (15:30 convention, data/daily/510300.csv as calendar master) -> honest no-op.
- Lane ownership: this leg belongs to whichever machine first declared it
  (bm-c, r1257).  Other machines print an honest stdout-only no-op, with the
  same stale-takeover door as the five-member leg (explicit --takeover AND
  owner heartbeat silent >= 120 min).

Usage
  python scripts/update_etf_wide.py run [--limit N] [--workers 6]
  python scripts/update_etf_wide.py --selftest        # offline invariants
  python scripts/update_etf_wide.py status

Exit contract: 0 ok/no-op | 2 fetch/mechanism failure | 3 overlap mismatch
(source rewrote history -> those symbols left untouched and disclosed).
"""
import datetime as dt
import io
import json
import multiprocessing as mp
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import scripts.update_etf_daily as U

DATA_DIR = os.path.join(ROOT, "data", "daily")
STATUS = os.path.join(ROOT, "results", "etf_wide_update_status.json")
LANE_OWNER = "bm-c"
TAKEOVER_STALE_MIN = 120
PREFIXED = re.compile(r"^(sh|sz)(\d{6})$")
BARE = re.compile(r"^\d{6}$")
DEFAULT_WORKERS = 6
PACE_S = 0.05                 # per-request sleep inside a worker
FAIL_ABORT_SHARE = 0.25       # >25% fetch failures = mechanism problem, exit 2
CONN_STOP = 40                # absolute stop: consecutive-ish failures ceiling


# ------------------------------------------------------------------- universe
def universe():
    """Every csv in data/daily that maps to a sina symbol.

    Returns list of (stem, sina_symbol).  Bare 6-digit stems (legacy dupes,
    e.g. `159901` next to `sz159901`) are refreshed too so the two faces of the
    same instrument cannot drift apart.  Non-standard stems (`510880_t73`)
    are skipped and reported.
    """
    out, skipped = [], []
    for fn in sorted(os.listdir(DATA_DIR)):
        if not fn.endswith(".csv"):
            continue
        stem = fn[:-4]
        m = PREFIXED.match(stem)
        if m:
            out.append((stem, stem))
            continue
        if BARE.match(stem):
            out.append((stem, ("sh" if stem[0] == "5" else "sz") + stem))
            continue
        skipped.append(stem)
    return out, skipped


def _tail_date(path):
    """Last data date of a 7-col csv (cheap, last non-empty line)."""
    try:
        with io.open(path, "r", encoding="utf-8") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 4096))
            chunk = f.read()
        lines = [ln.strip() for ln in chunk.splitlines() if ln.strip()]
        if not lines:
            return None
        last = lines[-1].split(",")
        return last[0] if re.match(r"^\d{4}-\d{2}-\d{2}$", last[0]) else None
    except Exception:  # noqa: BLE001
        return None


def panel_cutoff(exclude=None):
    """Oldest last-bar date across the universe (None if any file unreadable).

    min(), not median: the gate must stay open while ANY symbol is behind --
    the whole point of this leg is that a handful of fresh files were hiding
    ~1,670 stale ones.  `exclude` drops symbols whose SOURCE has itself ended
    (delisted funds; their last bar is legitimately old and would otherwise
    keep the gate open forever).
    """
    exclude = exclude or set()
    dates = []
    for fn in sorted(os.listdir(DATA_DIR)):
        if not fn.endswith(".csv"):
            continue
        if fn[:-4] in exclude:
            continue
        d = _tail_date(os.path.join(DATA_DIR, fn))
        if d is None:
            return None
        dates.append(d)
    return min(dates) if dates else None


# ----------------------------------------------------------------- fetch (proc)
_JS = None
_HIST = None
_JS_DECODE = None


def _worker_init():
    global _JS, _HIST, _JS_DECODE
    U._clear_proxy_env()
    _HIST, _JS_DECODE, MiniRacer = U._endpoints()
    _JS = MiniRacer()
    _JS.eval(_JS_DECODE)


def _fetch(sina_sym):
    import requests
    r = requests.get(_HIST.format(sina_sym), timeout=20)
    r.raise_for_status()
    if "=" not in r.text or ";" not in r.text:
        raise ValueError("payload_face_drift:len=%d" % len(r.text))
    dl = _JS.call("d", r.text.split("=")[1].split(";")[0].replace('"', ""))
    return U.normalize_decoded(dl)


def merge_tail(local, source):
    """Append-only TAIL merge with overlap verification.

    Strictly `date > local_last` rows are appended.  Two reasons this is not a
    union-by-date fill:

    * `data/daily` holds two structural families -- bare stems (`510300.csv`)
      are recent-window copies (2020+) kept by the core48 lanes, prefixed stems
      (`sh510300.csv`) are the full-history ETF face.  A union fill would
      silently push ~8 years of history into the bare copies and change what
      every consumer of those files computes (r1257 first live pass did exactly
      that on 35 files and was reverted before commit).
    * a refresh leg's job is to keep the TAIL current.  Pre-existing interior
      holes are disclosed (`holes_before_last`) and left alone; filling them is
      a research decision, not a maintenance side effect.

    Every local row must still be reproduced by the source within tolerance --
    failing that, the symbol is refused untouched (source rewrote history).
    """
    src_by_date = {str(r["date"]): r for r in source}
    overlap = 0
    for lr in local:
        d = str(lr["date"])
        s = src_by_date.get(d)
        if s is None:
            return {"merged_rows": None, "appended": 0, "overlap": overlap,
                    "holes": 0, "mismatch": "%s:absent_in_source" % d}
        overlap += 1
        for key in ("open", "high", "low", "close"):
            if abs(float(lr[key]) - float(s[key])) > U.PRICE_TOL:
                return {"merged_rows": None, "appended": 0, "overlap": overlap,
                        "holes": 0, "mismatch": "%s:%s_drift" % (d, key)}
        for key in ("volume", "amount"):
            if abs(int(float(lr[key])) - int(round(float(s[key])))) \
                    > U.INT_TOL:
                return {"merged_rows": None, "appended": 0, "overlap": overlap,
                        "holes": 0, "mismatch": "%s:%s_drift" % (d, key)}
    last = str(local[-1]["date"]) if local else ""
    local_dates = {str(r["date"]) for r in local}
    holes = sum(1 for d in src_by_date if d < last and d not in local_dates)
    new_rows = [r for r in source if str(r["date"]) > last]
    return {"merged_rows": list(local) + new_rows, "appended": len(new_rows),
            "overlap": overlap, "holes": holes, "mismatch": None}


def refresh_one(task):
    """Fetch + verify + append one symbol. Pure w.r.t. other symbols."""
    stem, sina_sym = task
    path = os.path.join(DATA_DIR, stem + ".csv")
    res = {"stem": stem, "sina": sina_sym}
    try:
        t0 = time.time()
        src = _fetch(sina_sym)
        res["secs"] = round(time.time() - t0, 3)
    except Exception as e:  # noqa: BLE001
        time.sleep(PACE_S)
        res["status"] = "fetch_fail"
        res["detail"] = "%s:%s" % (type(e).__name__, e)
        return res
    time.sleep(PACE_S)
    if not src:
        res["status"] = "fetch_fail"
        res["detail"] = "empty_source"
        return res
    res["src_last"] = src[-1]["date"]
    try:
        local = U.read_local_csv(path)
    except Exception as e:  # noqa: BLE001
        res["status"] = "read_fail"
        res["detail"] = "%s:%s" % (type(e).__name__, e)
        return res
    res["local_last"] = local[-1]["date"] if local else None
    m = merge_tail(local, src)
    if m["mismatch"]:
        res["status"] = "mismatch"
        res["detail"] = m["mismatch"]
        res["overlap_checked"] = m["overlap"]
        return res
    if m["holes"]:
        res["holes_before_last"] = m["holes"]
    if m["appended"] == 0:
        res["status"] = "no_change"
        return res
    err = U.validate_rows(m["merged_rows"])
    if err:
        res["status"] = "invalid"
        res["detail"] = err
        return res
    U.atomic_write(path, U.rows_to_csv_text(m["merged_rows"]))
    res["status"] = "appended"
    res["appended"] = m["appended"]
    res["overlap_checked"] = m["overlap"]
    res["new_last"] = m["merged_rows"][-1]["date"]
    return res


# ----------------------------------------------------------------------- run
def _now():
    return dt.datetime.now()


def _run_impl(limit=None, workers=DEFAULT_WORKERS, takeover=False,
              force=False):
    me = U._lane_owner_id()
    owner_note = None
    if me != LANE_OWNER:
        stale = U._owner_stale_min(LANE_OWNER)
        ok = U.takeover_decision(me, LANE_OWNER, stale, takeover)
        if not ok:
            payload = {"ts": _now().isoformat(timespec="seconds"),
                       "machine": me, "lane_owner": LANE_OWNER,
                       "status": "noop_lane_guard",
                       "detail": ("lane owned by %s (heartbeat silent %s min); "
                                    "pass --takeover to declare a stale "
                                    "takeover" % (LANE_OWNER, stale))}
            U.write_status(payload)
            print(json.dumps(payload, ensure_ascii=False, indent=1))
            return 0
        owner_note = {"takeover_by": me, "owner": LANE_OWNER,
                      "owner_silent_min": stale}

    uni, skipped = universe()
    now = _now()
    dates = U._load_trading_dates()
    expected = U.expected_latest_bar_date(now, dates)
    prev = U.load_status() or {}
    ended = set(prev.get("source_ended_stems") or [])
    cut = panel_cutoff(exclude=set(ended) | set(skipped))
    needs, expected2, reason = U.cutoff_gate(cut, now, dates)
    if not needs and not force:
        payload = {"ts": now.isoformat(timespec="seconds"), "machine": me,
                   "status": "noop_fresh", "panel_cutoff": cut,
                   "expected": expected2, "detail": reason,
                   "universe": len(uni), "skipped": skipped,
                   "source_ended_stems": sorted(ended)}
        if owner_note:
            payload.update(owner_note)
        U.write_status(payload)
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return 0

    tasks = uni[:limit] if limit else uni
    counts = {}
    mismatches, fails, invalid = [], [], []
    holes_syms = 0
    holes_bars = 0
    t0 = time.time()
    ctx = mp.get_context("spawn")
    with ctx.Pool(processes=max(1, workers), initializer=_worker_init) as pool:
        for i, res in enumerate(pool.imap_unordered(refresh_one, tasks,
                                                   chunksize=4), 1):
            counts[res["status"]] = counts.get(res["status"], 0) + 1
            if res.get("holes_before_last"):
                holes_syms += 1
                holes_bars += int(res["holes_before_last"])
            if res.get("src_last") and res["src_last"] < expected:
                ended.add(res["stem"])
            if res["status"] == "mismatch":
                mismatches.append("%s:%s" % (res["stem"], res.get("detail")))
            elif res["status"] in ("fetch_fail", "read_fail"):
                fails.append("%s:%s" % (res["stem"], res.get("detail")))
            elif res["status"] == "invalid":
                invalid.append("%s:%s" % (res["stem"], res.get("detail")))
            if i % 250 == 0:
                sys.stderr.write("  ... %d/%d\n" % (i, len(tasks)))
                sys.stderr.flush()
    elapsed = round(time.time() - t0, 1)

    payload = {
        "ts": _now().isoformat(timespec="seconds"),
        "machine": me, "lane_owner": LANE_OWNER,
        "status": "ok", "expected": expected, "panel_cutoff_before": cut,
        "panel_cutoff_after": panel_cutoff(exclude=set(ended) | set(skipped)),
        "source_ended_stems": sorted(ended),
        "universe": len(uni), "attempted": len(tasks), "workers": workers,
        "elapsed_s": elapsed, "counts": counts,
        "mismatch_n": len(mismatches), "mismatch_sample": mismatches[:20],
        "fetch_fail_n": len(fails), "fetch_fail_sample": fails[:20],
        "invalid_n": len(invalid), "invalid_sample": invalid[:20],
        "holes_symbols": holes_syms, "holes_bars": holes_bars,
        "skipped_stems": skipped,
    }
    if owner_note:
        payload.update(owner_note)
    nfail = len(fails)
    if nfail > max(CONN_STOP, FAIL_ABORT_SHARE * len(tasks)):
        payload["status"] = "fail_fetch_mass"
        U.write_status(payload)
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return 2
    if mismatches or invalid:
        payload["status"] = "ok_with_refusals"
        U.write_status(payload)
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return 3
    U.write_status(payload)
    print(json.dumps(payload, ensure_ascii=False, indent=1))
    return 0


def status():
    try:
        with io.open(STATUS, encoding="utf-8-sig") as f:
            print(json.dumps(json.load(f), ensure_ascii=False, indent=1))
    except FileNotFoundError:
        print(json.dumps({"status": "never_run"}, indent=1))
    return 0


# ------------------------------------------------------------------ selftest
def _selftest():
    """Offline invariants -- no network, no writes outside tmp."""
    fails = []
    _checks = []

    def chk(name, cond):
        _checks.append(1)
        if not cond:
            fails.append(name)

    # 1 symbol mapping: prefixed preserved, bare 6-digit gets the right prefix
    chk("map_prefixed", PREFIXED.match("sh510300").group(0) == "sh510300")
    chk("map_bare_etf", ("sh" if "510880"[0] == "5" else "sz") + "510880"
        == "sh510880")
    chk("map_bare_sz", ("sh" if "159915"[0] == "5" else "sz") + "159915"
        == "sz159915")
    chk("map_reject_slot", PREFIXED.match("510880_t73") is None
        and BARE.match("510880_t73") is None)

    # 2 merge is append-only + refuses drift
    local = [{"date": "2026-10-19", "open": 1.0, "high": 1.1, "low": 0.9,
              "close": 1.05, "volume": 100, "amount": 105}]
    src_ok = local + [{"date": "2026-10-20", "open": 1.05, "high": 1.2,
                       "low": 1.0, "close": 1.15, "volume": 120,
                       "amount": 138}]
    m = U.merge_incremental(local, src_ok)
    chk("merge_appends", m["merged"] and m["appended"] == 1
        and len(m["merged_rows"]) == 2)
    bad = [dict(local[0], close=1.06)] + src_ok[1:]
    chk("merge_refuses_drift", not U.merge_incremental(local, bad)["merged"])
    gone = src_ok[1:]
    chk("merge_refuses_absent_overlap",
        not U.merge_incremental(local, gone)["merged"])

    # 3 validate rejects OHLC order break / non-positive
    chk("validate_ok", U.validate_rows(src_ok) is None)
    chk("validate_bad_ohlc",
        U.validate_rows([dict(src_ok[0], low=1.2)]) is not None)
    chk("validate_nonpos",
        U.validate_rows([dict(src_ok[0], close=0.0)]) is not None)

    # 3b merge_tail: tail append only, interior holes disclosed NOT filled
    src_dense = [
        {"date": "2026-10-19", "open": 1.0, "high": 1.1, "low": 0.9,
         "close": 1.05, "volume": 100, "amount": 105},
        {"date": "2026-10-20", "open": 1.05, "high": 1.2, "low": 1.0,
         "close": 1.15, "volume": 120, "amount": 138},
        {"date": "2026-10-21", "open": 1.15, "high": 1.25, "low": 1.1,
         "close": 1.2, "volume": 130, "amount": 156},
    ]
    gap_local = [src_dense[0], src_dense[2]]        # 10-20 missing in the middle
    mt = merge_tail(gap_local, src_dense)
    chk("tail_does_not_fill_interior_hole",
        mt["mismatch"] is None and mt["appended"] == 0 and mt["holes"] == 1
        and len(mt["merged_rows"]) == 2)
    chk("tail_appends_new_last_bar",
        merge_tail(src_dense[:2], src_dense)["appended"] == 1)
    chk("tail_noop_when_current", merge_tail(src_dense, src_dense)["appended"]
        == 0)
    chk("tail_refuses_drift",
        merge_tail([dict(src_dense[0], close=9.9)], src_dense)["mismatch"]
        is not None)
    chk("tail_refuses_absent_row",
        merge_tail([{"date": "1999-01-04", "open": 1.0, "high": 1.0,
                     "low": 1.0, "close": 1.0, "volume": 1, "amount": 1}],
                   src_dense)["mismatch"] is not None)
    chk("tail_keeps_local_bytes",
        merge_tail(src_dense[:2], src_dense)["merged_rows"][:2] == src_dense[:2])

    # 4 tail reader + min-cutoff semantics (uses tmp files only)
    import tempfile
    tmpd = tempfile.mkdtemp(prefix="etfwide_")
    U_PATH = os.path.join(tmpd, "sh000001.csv")
    with io.open(U_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(U.rows_to_csv_text(src_ok))
    chk("tail_date", _tail_date(U_PATH) == "2026-10-20")
    global DATA_DIR
    keep = DATA_DIR
    try:
        DATA_DIR = tmpd
        chk("panel_cutoff_min", panel_cutoff() == "2026-10-20")
        with io.open(os.path.join(tmpd, "sh000002.csv"), "w",
                     encoding="utf-8", newline="\n") as f:
            f.write(U.rows_to_csv_text(local))
        chk("panel_cutoff_is_min_not_max",
            panel_cutoff() == "2026-10-19")
    finally:
        DATA_DIR = keep
        import shutil
        shutil.rmtree(tmpd, ignore_errors=True)

    # 5 fresh gate closes only when the min cutoff reaches the expected bar
    now = dt.datetime(2026, 10, 25, 19, 45)
    dates = U._load_trading_dates()
    if dates:
        needs, exp, _ = U.cutoff_gate("2026-10-23", now, dates)
        chk("gate_closed_when_fresh", not needs)
        needs2, _, _ = U.cutoff_gate("2026-10-20", now, dates)
        chk("gate_open_when_stale", needs2)

    if fails:
        print("etf_wide selftest FAIL: " + ", ".join(fails))
        return 1
    print("etf_wide selftest %d/%d PASS" % (len(_checks), len(_checks)))
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "--selftest" or cmd == "selftest":
        return _selftest()
    if cmd == "status":
        return status()
    limit = None
    workers = DEFAULT_WORKERS
    takeover = "--takeover" in argv
    force = "--force" in argv
    for a in argv:
        if a.startswith("--limit="):
            limit = int(a.split("=", 1)[1])
        elif a.startswith("--workers="):
            workers = int(a.split("=", 1)[1])
    return _run_impl(limit, workers, takeover, force)


if __name__ == "__main__":
    sys.exit(main(sys.argv))