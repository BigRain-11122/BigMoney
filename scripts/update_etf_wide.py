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
COVERAGE_FLOOR = 0.95         # gate: >=95% of the universe at the expected bar

# --- same-evening catch-up face ---------------------------------------------
# The klc_kl.js history face lags about one session: a 2026-10-26 close only
# appears in it the next morning, so the whole book prices off yesterday's bar
# all evening.  The same vendor's batch quote endpoint (hq.sinajs.cn) already
# carries the finished session at 19:xx (verified 2026-10-26: sh510300 open
# 4.155 / high 4.187 / low 4.130 / close 4.179 / volume 2,119,844,708 /
# amount 8,817,683,336 -- identical to the history face's own later print), and
# it is BATCHED (one request per QUOTE_CHUNK symbols) instead of one call per
# instrument.  It tops up only the missing tail session, never rewrites a row.
#
# The proof that a quote really is this instrument's bar is the quote's own
# 昨收 field: it has to reproduce the local last close, so a wrong symbol
# mapping or an unadjusted split shows up as a refusal instead of a bad bar.
QUOTE_URL = "https://hq.sinajs.cn/list={syms}"
QUOTE_CHUNK = 60
QUOTE_LINE = re.compile(r'hq_str_([a-z]{2}\d{6})="([^"]*)"')
ENDED_GRACE_TD = 5            # source silence (trading days) before "delisted"
QUIET_RECHECK_H = 24.0        # a "not printing" stem is re-checked daily


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


def panel_coverage(exclude=None, target=None):
    """Share of the universe that already carries ``target``.

    ``panel_cutoff`` answers "what is the oldest bar", which is the right
    disclosure but a wrong gate: one suspended symbol (no quote session, its
    source a session behind) holds a min() at yesterday forever, so the leg
    re-swept 1,724 symbols on every round -- 6 minutes and ~1,700 history
    requests each time, for zero new bars. E136 settled this shape already
    for the lag audit: staleness is a coverage question, not a min. The
    original protection survives because the floor is high -- a handful of
    fresh files hiding 1,670 stale ones still scores a few percent.
    """
    exclude = exclude or set()
    total = 0
    at_target = 0
    laggards = []
    for fn in sorted(os.listdir(DATA_DIR)):
        if not fn.endswith(".csv"):
            continue
        if fn[:-4] in exclude:
            continue
        d = _tail_date(os.path.join(DATA_DIR, fn))
        if d is None:
            continue
        total += 1
        if target is None or d >= target:
            at_target += 1
        else:
            laggards.append(fn[:-4])
    pct = (100.0 * at_target / total) if total else 0.0
    return {"total": total, "at_target": at_target, "pct": round(pct, 2),
            "laggard_n": len(laggards), "laggards": laggards}


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


HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
           "Referer": "https://finance.sina.com.cn",
           "Connection": "close"}
HTTP_TRIES = 3


def _get_text(url, timeout=20):
    """GET with a bounded retry: both faces abort single requests randomly."""
    import requests
    last = None
    for i in range(HTTP_TRIES):
        try:
            r = requests.get(url, timeout=timeout, headers=HEADERS)
            r.raise_for_status()
            return r.text
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(0.25 * (i + 1))
    raise last


def _fetch(sina_sym):
    text = _get_text(_HIST.format(sina_sym), timeout=20)
    if "=" not in text or ";" not in text:
        raise ValueError("payload_face_drift:len=%d" % len(text))
    dl = _JS.call("d", text.split("=")[1].split(";")[0].replace('"', ""))
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

    Every local row INSIDE the source's own window must be reproduced within
    tolerance -- failing that, the symbol is refused untouched (source rewrote
    history).  A local row dated AFTER the source's last print is not a
    disagreement: it is tonight's bar that the quote face already delivered
    while this history face still publishes yesterday (the same-evening gap
    this file exists to close), so it is counted and skipped.
    """
    src_by_date = {str(r["date"]): r for r in source}
    src_last = str(source[-1]["date"]) if source else ""
    overlap = 0
    beyond = 0
    for lr in local:
        d = str(lr["date"])
        s = src_by_date.get(d)
        if s is None:
            if src_last and d > src_last:
                beyond += 1
                continue
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
            "overlap": overlap, "holes": holes, "beyond_source": beyond,
            "mismatch": None}


def _quote_fields(sina_syms):
    """One batched quote request -> {sina_sym: [fields...]} (parent process)."""
    text = _get_text(QUOTE_URL.format(syms=",".join(sina_syms)), timeout=20)
    out = {}
    for sym, body in QUOTE_LINE.findall(text):
        if body:
            out[sym] = body.split(",")
    return out


def quote_tail(local, fields, target):
    """Pure: build the missing tail bar of one symbol from its quote fields.

    Accepted only when the quote's own session date equals `target` (so an
    intraday snapshot can never be written as a completed bar) and when the
    quote's previous close reproduces the local last close (so a wrong symbol
    mapping or an unadjusted split is refused, not written).
    """
    if len(fields) < 32:
        return {"row": None, "mismatch": "short_quote:%d" % len(fields)}
    try:
        q_date = fields[30].strip()
        q_open, q_prev = float(fields[1]), float(fields[2])
        q_close, q_high, q_low = float(fields[3]), float(fields[4]), float(fields[5])
        q_vol, q_amt = int(float(fields[8])), float(fields[9])
    except (TypeError, ValueError):
        return {"row": None, "mismatch": "unparsable_quote"}
    if not local:
        return {"row": None, "mismatch": "empty_local"}
    if q_date != str(target):
        return {"row": None, "mismatch": "quote_date_%s_not_%s"
                % (q_date or "blank", target)}
    if str(local[-1]["date"]) >= str(target):
        return {"row": None, "mismatch": None, "already_current": True}
    if abs(q_prev - float(local[-1]["close"])) > U.PRICE_TOL:
        return {"row": None, "mismatch": "prev_close_drift:%.6f_vs_%.6f"
                % (q_prev, float(local[-1]["close"]))}
    if min(q_open, q_close, q_high, q_low) <= 0 or q_vol <= 0:
        return {"row": None, "mismatch": "nonpositive_quote"}
    return {"row": {"date": q_date, "open": q_open, "high": q_high,
                    "low": q_low, "close": q_close, "volume": q_vol,
                    "amount": q_amt},
            "mismatch": None}
def _td_between(d0, d1, dates):
    """Trading days from d0 (exclusive) to d1 (inclusive); None if unknown.

    `dates` must be the OFFICIAL exchange calendar, not a panel-derived one:
    using the panel's own tail as the calendar is exactly how a one-session
    vendor lag reads as a delisting (r1286 / E136).
    """
    if not d0 or not d1:
        return None
    a, b = str(d0), str(d1)
    if b <= a:
        return 0
    inside = [d for d in (dates or []) if a < d <= b]
    if not inside:
        return None
    return len(inside)


def official_calendar():
    """Official exchange calendar days (falls back to the panel calendar)."""
    try:
        import scripts.exchange_calendar_audit as CA
        days = CA.load_calendar()
        if days:
            return sorted(days)
    except Exception:  # noqa: BLE001
        pass
    return U._load_trading_dates()


def _append_and_write(res, path, merged_rows, appended, overlap):
    """Shared tail write: validate, then atomic replace."""
    err = U.validate_rows(merged_rows)
    if err:
        res["status"] = "invalid"
        res["detail"] = err
        return res
    U.atomic_write(path, U.rows_to_csv_text(merged_rows))
    res["status"] = "appended"
    res["appended"] = appended
    res["overlap_checked"] = overlap
    res["new_last"] = merged_rows[-1]["date"]
    return res


def refresh_one(task):
    """Fetch + verify + append one symbol. Pure w.r.t. other symbols."""
    stem, sina_sym, target = task
    path = os.path.join(DATA_DIR, stem + ".csv")
    res = {"stem": stem, "sina": sina_sym}
    src = None
    try:
        t0 = time.time()
        src = _fetch(sina_sym)
        res["secs"] = round(time.time() - t0, 3)
    except Exception as e:  # noqa: BLE001
        res["sina_error"] = "%s:%s" % (type(e).__name__, e)
    time.sleep(PACE_S)
    if not src:
        res["status"] = "fetch_fail"
        res["detail"] = res.get("detail", "sina_unavailable")
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
    if m.get("beyond_source"):
        res["beyond_source_rows"] = m["beyond_source"]
    if m["appended"] == 0:
        # The history face has nothing newer: the panel is either current, or
        # it is one session behind because that face publishes the close only
        # next morning.  Those symbols go to the batched quote top-up.
        local_last = str(local[-1]["date"]) if local else None
        res["local_last"] = local_last
        if local_last and local_last < str(target):
            res["status"] = "tail_lag"
            res["sina_src_last"] = res.get("src_last")
            return res
        res["status"] = "no_change"
        return res
    return _append_and_write(res, path, m["merged_rows"], m["appended"],
                             m["overlap"])


# ----------------------------------------------------------------------- run
def _now():
    return dt.datetime.now()


def load_wide_status():
    """Wide-panel status face (local; NOT U's five-member status file)."""
    try:
        with io.open(STATUS, encoding="utf-8-sig") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def write_wide_status(payload):
    tmp = STATUS + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATUS)


def coverage_closes_gate(needs, coverage_pct, floor=COVERAGE_FLOOR):
    """Skip a sweep only when the calendar says work may exist AND the
    universe already carries the expected bar at the coverage floor."""
    return bool(needs) and coverage_pct >= floor * 100.0


def _run_impl(limit=None, workers=DEFAULT_WORKERS, takeover=False,
              force=False):
    me = U._lane_owner_id()
    owner_note = None
    if me != LANE_OWNER:
        stale = U._owner_stale_min(LANE_OWNER)
        # the shared guard is a 2-arg pure function (allow, stale_min); this
        # caller was left on the pre-refactor 4-arg form and died with TypeError
        # on EVERY non-owner machine -- a silent rc=1 in the S6 chain (r1208)
        ok, why = U.takeover_decision(takeover, stale)
        if not ok:
            payload = {"ts": _now().isoformat(timespec="seconds"),
                       "machine": me, "lane_owner": LANE_OWNER,
                       "status": "noop_lane_guard",
                       "detail": ("lane owned by %s (heartbeat silent %s min); "
                                    "%s" % (LANE_OWNER, stale, why))}
            write_wide_status(payload)
            print(json.dumps(payload, ensure_ascii=False, indent=1))
            return 0
        owner_note = {"takeover_by": me, "owner": LANE_OWNER,
                      "owner_silent_min": stale}

    uni, skipped = universe()
    now = _now()
    # official calendar: the panel's own tail cannot tell us today is a trading
    # day while the vendor is a session behind (E136 self-referential calendar)
    dates = official_calendar()
    expected = U.expected_latest_bar_date(now, dates)
    prev = load_wide_status()
    ended = set(prev.get("source_ended_stems") or [])
    quiet_prev = set()
    quiet_ts = prev.get("source_quiet_ts")
    if quiet_ts:
        try:
            age_h = (now - dt.datetime.fromisoformat(quiet_ts)).total_seconds() / 3600.0
        except ValueError:
            age_h = 99.0
        if age_h <= QUIET_RECHECK_H:
            quiet_prev = set(prev.get("source_quiet_stems") or [])
    cut = panel_cutoff(exclude=set(ended) | set(skipped) | quiet_prev)
    needs, expected2, reason = U.cutoff_gate(cut, now, dates)
    cov = panel_coverage(exclude=set(ended) | set(skipped) | quiet_prev,
                         target=expected2)
    if coverage_closes_gate(needs, cov["pct"]):
        # Coverage override (E136 rule on the gate): the floor is 95% of the
        # universe at the expected bar, so a couple of suspended symbols can
        # no longer buy a full 1,724-symbol sweep every round, while a truly
        # stale panel (the shape this leg was built for) still opens it.
        needs = False
        reason = ("coverage %s%% of %d symbols already at %s (floor %s%%); "
                  "laggards=%d %s"
                  % (cov["pct"], cov["total"], expected2,
                     int(COVERAGE_FLOOR * 100), cov["laggard_n"],
                     ",".join(cov["laggards"][:10])))
    if not needs and not force:
        payload = {"ts": now.isoformat(timespec="seconds"), "machine": me,
                   "status": "noop_fresh", "panel_cutoff": cut,
                   "expected": expected2, "detail": reason,
                   "coverage_pct": cov["pct"], "coverage_total": cov["total"],
                   "coverage_floor": COVERAGE_FLOOR,
                   "laggard_n": cov["laggard_n"],
                   "laggard_sample": cov["laggards"][:20],
                   "universe": len(uni), "skipped": skipped,
                   "source_ended_stems": sorted(ended),
                   "source_quiet_stems": sorted(quiet_prev),
                   "source_quiet_ts": quiet_ts}
        if owner_note:
            payload.update(owner_note)
        write_wide_status(payload)
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return 0

    tasks = [(s, sym, expected) for (s, sym) in (uni[:limit] if limit else uni)]
    counts = {}
    mismatches, fails, invalid = [], [], []
    holes_syms = 0
    holes_bars = 0
    lagging_syms = 0
    lag_tasks = []
    lag_src_last = {}
    quiet_stems = []
    quote_syms = 0
    quote_rows = 0
    quote_refusals = []
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
                # A vendor lag of one session must NOT delist the universe.
                # "Source ended" is a trading-day distance, not inequality.
                lag = _td_between(res["src_last"], expected, dates)
                if lag is not None and lag >= ENDED_GRACE_TD:
                    ended.add(res["stem"])
                else:
                    lagging_syms += 1
            if res["status"] == "tail_lag":
                lag_tasks.append((res["stem"], res["sina"]))
                lag_src_last[res["stem"]] = res.get("sina_src_last")
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

    # --- phase 2: same-evening tail top-up from the batched quote face ------
    for start in range(0, len(lag_tasks), QUOTE_CHUNK):
        chunk = lag_tasks[start:start + QUOTE_CHUNK]
        by_sym = {sym: stem for stem, sym in chunk}
        try:
            quotes = _quote_fields(sorted(by_sym))
        except Exception as e:  # noqa: BLE001
            quote_refusals.append("chunk%d:%s:%s"
                                  % (start, type(e).__name__, e))
            continue
        for sym, stem in by_sym.items():
            fields = quotes.get(sym)
            if not fields:
                # both faces silent for this stem -> the instrument is not
                # printing (suspended/delisted), not a stale panel
                quiet_stems.append(stem)
                quote_refusals.append("%s:absent" % stem)
                continue
            path = os.path.join(DATA_DIR, stem + ".csv")
            try:
                local = U.read_local_csv(path)
            except Exception as e:  # noqa: BLE001
                quote_refusals.append("%s:read:%s" % (stem, type(e).__name__))
                continue
            q = quote_tail(local, fields, expected)
            if q.get("already_current"):
                counts["no_change"] = counts.get("no_change", 0) + 1
                counts["tail_lag"] = max(0, counts.get("tail_lag", 0) - 1)
                continue
            if q["mismatch"]:
                quote_refusals.append("%s:%s" % (stem, q["mismatch"]))
                counts["tail_lag"] = max(0, counts.get("tail_lag", 0) - 1)
                counts["quote_refused"] = counts.get("quote_refused", 0) + 1
                if (str(q["mismatch"]).startswith("quote_date_")
                        and local and local[-1]["date"] == lag_src_last.get(stem)):
                    quiet_stems.append(stem)
                continue
            merged = list(local) + [q["row"]]
            res = {"stem": stem, "sina": sym}
            _append_and_write(res, path, merged, 1, len(local))
            if res["status"] == "appended":
                counts["tail_lag"] = max(0, counts.get("tail_lag", 0) - 1)
                counts["appended"] = counts.get("appended", 0) + 1
                quote_syms += 1
                quote_rows += int(res.get("appended") or 0)
            else:
                quote_refusals.append("%s:%s" % (stem, res.get("detail")))
    elapsed = round(time.time() - t0, 1)
    post_cov = panel_coverage(exclude=set(ended) | set(skipped)
                              | set(quiet_stems), target=expected)

    payload = {
        "ts": _now().isoformat(timespec="seconds"),
        "machine": me, "lane_owner": LANE_OWNER,
        "status": "ok", "expected": expected, "panel_cutoff_before": cut,
        "panel_cutoff_after": panel_cutoff(exclude=set(ended) | set(skipped)
                                            | set(quiet_stems)),
        "source_ended_stems": sorted(ended),
        "universe": len(uni), "attempted": len(tasks), "workers": workers,
        "elapsed_s": elapsed, "counts": counts,
        "ended_grace_td": ENDED_GRACE_TD,
        "source_quiet_stems": sorted(set(quiet_stems)),
        "source_quiet_ts": _now().isoformat(timespec="seconds"),
        "source_lagging_stems": lagging_syms,
        "coverage_pct_pre": cov["pct"], "coverage_floor": COVERAGE_FLOOR,
        "coverage_post": post_cov["pct"], "coverage_total": post_cov["total"],
        "laggard_n": post_cov["laggard_n"],
        "laggard_sample": post_cov["laggards"][:20],
        "quote_topup_stems": quote_syms, "quote_topup_rows": quote_rows,
        "quote_refusal_n": len(quote_refusals),
        "quote_refusal_sample": quote_refusals[:20],
        "quote_face": QUOTE_URL, "quote_chunk": QUOTE_CHUNK,
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
        write_wide_status(payload)
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return 2
    if mismatches or invalid:
        payload["status"] = "ok_with_refusals"
        write_wide_status(payload)
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return 3
    write_wide_status(payload)
    print(json.dumps(payload, ensure_ascii=False, indent=1))
    return 0


def status():
    d = load_wide_status()
    print(json.dumps(d or {"status": "never_run"}, ensure_ascii=False,
                     indent=1))
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

    # 0 shared-guard contract. The lane takeover guard lives in
    # update_etf_daily and was refactored to a 2-arg pure function while this
    # caller kept the 4-arg form: the leg then died with TypeError on every
    # non-owner machine inside the S6 chain, which reads as a silent rc=1 with
    # no output (r1208). Pin the arity here so the next refactor goes red in
    # selftest instead of going quiet in the chain.
    import inspect
    _params = list(inspect.signature(U.takeover_decision).parameters)
    chk("guard_arity", _params == ["allow", "stale_min"]
        and U.takeover_decision(False, 10_000)[0] is False
        and U.takeover_decision(True, None)[0] is False
        and U.takeover_decision(True, 10 * U.TAKEOVER_STALE_MIN)[0] is True)

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
    # a local bar NEWER than the source's own last print is tonight's quote-face
    # bar, not a source rewrite: tolerated and counted, never appended twice
    quote_bar = {"date": "2026-10-22", "open": 1.2, "high": 1.3, "low": 1.15,
                 "close": 1.25, "volume": 140, "amount": 175}
    mtb = merge_tail(src_dense + [quote_bar], src_dense)
    chk("tail_tolerates_bar_beyond_source",
        mtb["mismatch"] is None and mtb["appended"] == 0
        and mtb["beyond_source"] == 1)
    chk("tail_still_refuses_absent_inside_window",
        merge_tail([src_dense[1]], [src_dense[0], src_dense[2]])["mismatch"]
        is not None)

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
        # coverage is the gate that keeps a suspended symbol from buying a
        # 1,724-symbol sweep every round (1 of 2 files at target = 50%)
        cov = panel_coverage(target="2026-10-20")
        chk("coverage_counts", cov["total"] == 2 and cov["at_target"] == 1
            and cov["pct"] == 50.0 and cov["laggard_n"] == 1)
        chk("coverage_floor_not_met_opens_gate",
            not coverage_closes_gate(True, cov["pct"]))
        chk("coverage_floor_met_closes_gate",
            coverage_closes_gate(True, 99.9)
            and coverage_closes_gate(True, 95.0)
            and not coverage_closes_gate(True, 94.9))
        chk("coverage_never_closes_a_calendar_open_gate",
            not coverage_closes_gate(False, 100.0))
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

    # 6 same-evening quote top-up (pure; no network here).  The fixture is the
    #   real 2026-10-26 sh510300 session as the quote face printed it.
    def qfields(date, o, prev, c, h, low, vol, amt):
        f = [""] * 33
        f[0], f[1], f[2], f[3], f[4], f[5] = ("name", str(o), str(prev),
                                              str(c), str(h), str(low))
        f[8], f[9], f[30] = str(vol), str(amt), date
        return f

    local_q = [{"date": "2026-10-23", "open": 4.080, "high": 4.186,
                "low": 4.031, "close": 4.178, "volume": 3755608213,
                "amount": 15423238067}]
    ok_q = qfields("2026-10-26", 4.155, 4.178, 4.179, 4.187, 4.130,
                   2119844708, 8817683336.000)
    r = quote_tail(local_q, ok_q, "2026-10-26")
    chk("quote_tail_builds_bar", r["mismatch"] is None
        and r["row"]["date"] == "2026-10-26"
        and r["row"]["close"] == 4.179
        and r["row"]["volume"] == 2119844708
        and abs(r["row"]["amount"] - 8817683336.0) < 1.0)
    chk("quote_tail_refuses_wrong_session_date",
        quote_tail(local_q, qfields("2026-10-23", 4.155, 4.178, 4.179, 4.187,
                                    4.130, 2119844708, 8.8e9),
                   "2026-10-26")["mismatch"] is not None)
    chk("quote_tail_refuses_prev_close_drift",
        quote_tail(local_q, qfields("2026-10-26", 4.155, 4.100, 4.179, 4.187,
                                    4.130, 2119844708, 8.8e9),
                   "2026-10-26")["mismatch"] is not None)
    chk("quote_tail_refuses_nonpositive",
        quote_tail(local_q, qfields("2026-10-26", 4.155, 4.178, 4.179, 4.187,
                                    4.130, 0, 0.0),
                   "2026-10-26")["mismatch"] is not None)
    chk("quote_tail_refuses_short_quote",
        quote_tail(local_q, ok_q[:10], "2026-10-26")["mismatch"] is not None)
    chk("quote_tail_noop_when_current",
        quote_tail(local_q + [{"date": "2026-10-26", "open": 1, "high": 1,
                               "low": 1, "close": 1, "volume": 1,
                               "amount": 1}], ok_q, "2026-10-26")
        .get("already_current") is True)
    chk("quote_line_regex",
        QUOTE_LINE.findall('var hq_str_sh510300="a,b,c";')
        == [("sh510300", "a,b,c")])
    # the two ETF lanes must not share one status file (r1289: this lane wrote
    # its payload into the five-member lane's status for a week)
    chk("status_face_is_local_not_shared", os.path.abspath(STATUS)
        != os.path.abspath(U.STATUS))

    # 7 "source ended" is a trading-day distance, not an inequality: a vendor
    #   lag of one session must not delist ~1,700 symbols from the gate.
    off = official_calendar()
    chk("official_calendar_reads_future_day",
        bool(off) and "2026-10-26" in off)
    chk("td_between_weekend_lag_is_one",
        _td_between("2026-10-23", "2026-10-26", off) == 1)
    chk("td_between_same_day_zero",
        _td_between("2026-10-23", "2026-10-23", off) == 0)
    chk("one_session_lag_below_grace",
        _td_between("2026-10-23", "2026-10-26", off) < ENDED_GRACE_TD)
    chk("month_silence_above_grace",
        _td_between("2026-09-02", "2026-10-26", off) >= ENDED_GRACE_TD)

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