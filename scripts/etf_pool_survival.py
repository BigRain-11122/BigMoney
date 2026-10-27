#!/usr/bin/env python
"""Survivorship face of the ETF pool the production book ranks from (bm-c r1319).

WHY
---
Every write-up of this book carries the same caveat: "the pool is the ETFs that
exist today, so the backtest is survivorship-biased". The caveat has been copied
forward for a month without a number behind it, and it is not obviously true --
`data/daily/*.csv` keeps a symbol's whole history in its own file, so a fund that
died in 2023 is still visible to the ranking engine for the bars it traded. The
bias would only be real for names that were never collected at all, which is a
different (and much harder) question.

So this tool measures the half that is measurable from the panel bytes: which
symbols stop printing inside the sample, when they stop, and how much of the
eligible universe they are. Two shapes get separated because they mean opposite
things:

  * ``stale`` -- last bar a few sessions behind the panel edge: a source lag, the
    name is alive and the gate will pick it up next refresh;
  * ``dead``  -- last bar 10+ sessions behind the edge: a delisting, a merger, or
    a symbol the source stopped serving. Its history is still in the panel, so
    the backtest saw it while it traded.

Reading discipline: this is a census of what the panel holds, not a claim about
why a symbol stopped. A ``dead`` bucket also catches a collector that silently
gave up on a name, which is exactly why the per-symbol list is published rather
than only the counts.

Usage:
    python scripts/etf_pool_survival.py run        # census -> results JSON
    python scripts/etf_pool_survival.py selftest   # offline, hermetic

Exit: 0 = census published, 1 = panel directory missing, 2 = mechanism failure.
"""
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DAILY = ROOT / "data" / "daily"
BENCH = ROOT / "data" / "basic" / "csi300.csv"
OUT = ROOT / "results" / "etf_pool_survival.json"

MIN_ROWS = 60        # the floor the production panel loader applies (_load_prices)
STALE_SESSIONS = 10  # inside this window a late print is source lag, not a death
YOUNG_SESSIONS = 250 # listed inside the last year -> a "young" cohort name


def _scan_csv(path):
    """-> (first_date, last_date, n_rows). Text only: no pandas, no floats."""
    first = None
    last = None
    n = 0
    with open(path, "rb") as f:
        header = f.readline()
        if not header:
            return None, None, 0
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            date = line.split(b",", 1)[0].decode("ascii", "replace")
            if first is None:
                first = date
            last = date
            n += 1
    return first, last, n


def _dates_of(path):
    dates = set()
    with open(path, "rb") as f:
        f.readline()
        for raw in f:
            line = raw.strip()
            if line:
                dates.add(line.split(b",", 1)[0].decode("ascii", "replace"))
    return dates


def _calendar(daily_dir):
    """The PANEL's own session calendar: the union of every symbol's dates.

    The bench is deliberately not used as the calendar -- `data/basic/csi300.csv`
    lags the panel by weeks on this host (it is refreshed by a different lane),
    and judging panel freshness against it marked 1,655 live symbols as dead on
    the first run (the r1286 self-reference class: the yardstick has to be the
    thing being measured, and any *other* face is disclosed, not trusted)."""
    dates = set()
    for p in sorted(pathlib.Path(daily_dir).glob("*.csv")):
        dates |= _dates_of(p)
    return sorted(dates)


def _bench_last():
    if not BENCH.exists():
        return None
    d = sorted(_dates_of(BENCH))
    return d[-1] if d else None


def classify(first, last, n_rows, cutoff, sessions_behind):
    """One symbol -> one bucket. Order matters: the panel loader drops short
    series entirely, so a short series is never part of the ranked universe."""
    if n_rows < MIN_ROWS or not first:
        return "below-floor"
    if last == cutoff:
        return "alive"
    if sessions_behind <= STALE_SESSIONS:
        return "stale"
    return "dead"


def census(daily_dir=None, bench=None):
    global BENCH
    daily_dir = pathlib.Path(daily_dir) if daily_dir else DAILY
    glob_bench = pathlib.Path(bench) if bench else BENCH
    saved, BENCH = BENCH, glob_bench
    try:
        cal = _calendar(daily_dir)
        bench_last = _bench_last()
    finally:
        BENCH = saved
    if not cal:
        raise RuntimeError("empty calendar: no panel dates found")
    index = {d: i for i, d in enumerate(cal)}
    files = sorted(pathlib.Path(daily_dir).glob("*.csv"))
    rows = []
    for p in files:
        first, last, n = _scan_csv(p)
        if not first:
            continue
        lag = index[cal[-1]] - index.get(last, -1)
        bucket = classify(first, last, n, cal[-1], lag)
        rows.append({"symbol": p.stem, "first": first, "last": last,
                     "rows": n, "sessions_behind_edge": lag, "bucket": bucket})
    cutoff = cal[-1]
    edge_i = index[cutoff]
    young_floor = cal[max(0, edge_i - YOUNG_SESSIONS)]
    eligible = [r for r in rows if r["bucket"] != "below-floor"]
    counts = {}
    for r in rows:
        counts[r["bucket"]] = counts.get(r["bucket"], 0) + 1
    for r in eligible:
        # strictly inside the window: a name whose first bar IS the floor is a
        # one-year-old fund, not a listing inside the last year
        r["young"] = r["first"] > young_floor
    young = [r for r in eligible if r["young"]]
    cohort = {}
    for r in eligible:
        cohort[r["first"][:4]] = cohort.get(r["first"][:4], 0) + 1
    dead = sorted([r for r in eligible if r["bucket"] == "dead"],
                  key=lambda r: r["last"])
    return {
        "tool": "scripts/etf_pool_survival.py",
        "evidence_cutoff": cutoff,
        "panel_dir": str(pathlib.Path(daily_dir)),
        "panel_files": len(files),
        "sessions": len(cal),
        "first_session": cal[0],
        "bench_last": bench_last,
        "bench_lag_sessions": (index[cutoff] - index[bench_last]
                               if bench_last in index else None),
        "young_floor": young_floor,
        "counts": counts,
        "eligible": len(eligible),
        "dead_share_of_eligible_pct": (100.0 * counts.get("dead", 0) / len(eligible)
                                       if eligible else None),
        "young_share_of_eligible_pct": (100.0 * len(young) / len(eligible)
                                       if eligible else None),
        "cohort_by_first_year": dict(sorted(cohort.items())),
        "dead": dead,
        "young": young,
        "reading": (
            "A dead symbol keeps its full history in the panel, so the ranking "
            "engine saw it while it traded -- the standing 'pure survivor pool' "
            "caveat over-states the bias by the dead share below. The residual "
            "bias (funds the source never served) is NOT measurable from these "
            "bytes."),
    }


def render(p):
    lines = [
        "etf_pool_survival: cutoff=%s files=%d sessions=%d"
        % (p["evidence_cutoff"], p["panel_files"], p["sessions"]),
        "  bench csi300 last=%s (lag %s sessions behind the panel)"
        % (p.get("bench_last"), p.get("bench_lag_sessions")),
        "  buckets: %s" % json.dumps(p["counts"], sort_keys=True),
        "  eligible (>=%d rows): %d; dead %.2f%%; young %.2f%%"
        % (MIN_ROWS, p["eligible"], p["dead_share_of_eligible_pct"] or 0.0,
           p["young_share_of_eligible_pct"] or 0.0),
        "  cohorts by first year: %s"
        % ", ".join("%s:%d" % (k, v) for k, v in p["cohort_by_first_year"].items()),
    ]
    for r in p["dead"][:15]:
        lines.append("  DEAD %s last=%s rows=%d" % (r["symbol"], r["last"], r["rows"]))
    if len(p["dead"]) > 15:
        lines.append("  ... %d more dead symbols in the JSON" % (len(p["dead"]) - 15))
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# selftest
# --------------------------------------------------------------------------- #
def _selftest():
    import tempfile

    legs = []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    def write(dirpath, name, dates, cols="open,close"):
        with open(os.path.join(dirpath, name), "w", encoding="utf-8") as f:
            f.write("date,%s\n" % cols)
            for d in dates:
                f.write("%s,1.0,1.0\n" % d)

    with tempfile.TemporaryDirectory() as tmp:
        daily = os.path.join(tmp, "daily")
        os.makedirs(daily)
        basic = os.path.join(tmp, "basic")
        os.makedirs(basic)
        # 90 sessions -- the fixture must clear MIN_ROWS, or every name lands
        # in below-floor and the classification legs pass vacuously (r1261)
        cal = ["2026-%02d-%02d" % (m, d) for m in (7, 8, 9) for d in range(1, 31)]
        with open(os.path.join(basic, "csi300.csv"), "w", encoding="utf-8") as f:
            f.write("date,close\n")
            # the bench is deliberately SHORT: it lags on this host and must not
            # become the yardstick for panel freshness (first live run: a stale
            # bench marked 1,655 live symbols dead)
            for d in cal[:30]:
                f.write("%s,1.0\n" % d)
        full = cal[:]
        write(daily, "sh510300.csv", full)                              # alive
        write(daily, "sh511999.csv", cal[:-1])                          # stale-1
        write(daily, "sz159999.csv", cal[:70])                           # dead
        write(daily, "sh512000.csv", cal[:5])                            # below floor
        write(daily, "sh512001.csv", cal[25:])                           # young+alive

        p = census(daily_dir=daily, bench=os.path.join(basic, "csi300.csv"))
        dead_syms = {r["symbol"] for r in p["dead"]}
        young = {r["symbol"] for r in p["young"]} if "young" in p else set()
        rows = {r["symbol"]: r for r in p["dead"]}
        leg("cutoff comes from the PANEL, not from a lagging bench",
            p["evidence_cutoff"] == cal[-1] and p["bench_last"] == cal[29]
            and p["bench_lag_sessions"] == len(cal) - 30,
            "%s vs bench %s lag %s" % (p["evidence_cutoff"], p["bench_last"],
                                       p["bench_lag_sessions"]))
        leg("a name printing to the edge is alive", p["counts"].get("alive") == 2,
            str(p["counts"]))
        leg("one session behind is stale, not dead",
            p["counts"].get("stale") == 1 and "sh511999" not in dead_syms,
            str(p["counts"]))
        leg("a name that dies mid-sample is dead", "sz159999" in dead_syms,
            str(sorted(dead_syms)))
        leg("a short series is below-floor, not dead",
            p["counts"].get("below-floor") == 1 and "sh512000" not in dead_syms,
            str(p["counts"]))
        leg("eligible excludes exactly the below-floor name", p["eligible"] == 4,
            str(p["eligible"]))
        leg("dead share is published as a percent between 0 and 100",
            p["dead_share_of_eligible_pct"] is not None
            and 0 < p["dead_share_of_eligible_pct"] < 100,
            str(p["dead_share_of_eligible_pct"]))
        leg("a late listing is young, an early one is not",
            "sh512001" in young and "sh510300" not in young, str(sorted(young)))
        leg("render carries the cutoff and the bucket line",
            p["evidence_cutoff"] in render(p) and "buckets:" in render(p), "")
        leg("the reading states the caveat it can and cannot settle",
            "NOT measurable" in p["reading"], "")

    passed = sum(1 for _n, c, _d in legs if c)
    for name, c, detail in legs:
        print("[%s] %s%s" % ("PASS" if c else "FAIL", name,
                             ("  " + str(detail)) if detail else ""))
    print("etf_pool_survival selftest: %d/%d PASS" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return _selftest()
    if cmd != "run":
        sys.stderr.write("usage: etf_pool_survival.py [run|selftest]\n")
        return 2
    if not DAILY.is_dir():
        sys.stderr.write("etf_pool_survival: panel dir missing: %s\n" % DAILY)
        return 1
    try:
        p = census()
    except Exception as exc:
        sys.stderr.write("etf_pool_survival: mechanism failure: %r\n" % (exc,))
        return 2
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
    print(render(p))
    print("  -> %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))