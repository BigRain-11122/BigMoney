"""Institutional block trades on the 龙虎榜 (LHB): does the net buy predict anything?

The 30-minute kill test for the second candidate of O-20261114-2325-bm-c section 3
("资金流/龙虎榜 IC 参考批（20 分钟）").

Who pays: nobody pays you for following the institutions. The LHB is a *disclosure*
of the previous session's seats, printed after the close. The only reason a reader of
this tape could earn is that the disclosure is not yet fully absorbed by the crowd
that trades the open the next morning -- i.e. the edge would be an attention/flow
premium that decays within days, paid by whoever buys the same move later. If the
institutions' own buying is already the top of the move, the tape is a *reverse*
signal and the honest output is "close the line", not a report.

So the test is deliberately a within-day cross-section: on a given date every stock in
the panel is a LHB name (they are all extreme movers by construction), so we ask which
one to prefer *among today's names*, never "are LHB names good" (the level effect --
all LHB names mean-revert together -- is removed by demeaning inside the date).

Cold facts about this host: the stock daily panel (data/astock_daily/per) lives on
another machine's disk and is empty here, so prices are fetched from Tencent's
qfq kline endpoint into data/stock_daily_tx/per (machine-local, gitignored) --
0.11 s/symbol vs 11 s for the akshare/sina wrapper, which is what makes 3,500
symbols a two-minute job instead of a two-hour one.

Frozen criteria (written before the numbers were read, per the order's step 3):
  C1  information: |mean daily cross-sectional IC| of 机构净买额占总成交额比 at h=5
      must be >= 0.030 with |t| >= 3.0 over the sample's dates. Anything smaller is
      inside the noise of a 20-name cross-section.
  C2  monotone in the third: T3-T1 spread of the *demeaned* 5-day abnormal return
      must be >= 0.50% in absolute value and carry the same sign as the mean IC.
      0.50% is the size that survives 2x15bp round trip plus the bid-ask on the open.
  C3  persistence, not a one-day bounce: the same spread must keep its sign at h=10
      and h=20. A signal that only works for two days cannot be executed at 1M
      without paying the same cost twice.
  Verdict: OPEN only if C1, C2 and C3 all pass; otherwise CLOSE (关线) with no
  explanatory report -- the panel and this script stay for reuse.

Benchmark: 中证1000 (sh000852) close-to-close over the holding window, because the
LHB population is small/mid cap by construction. Abnormal return = stock open-to-open
(the executable side) minus that index return; the half-session mismatch is disclosed
rather than modelled away.
"""
import argparse
import json
import os
import statistics
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LHB = os.path.join(ROOT, "data", "lhb_inst", "lhb_inst.parquet")
PX_DIR = os.path.join(ROOT, "data", "stock_daily_tx", "per")
PX_PROGRESS = os.path.join(ROOT, "data", "stock_daily_tx", "_progress.json")
IDX_CSV = os.path.join(ROOT, "data", "index_daily", "sh000852.csv")
OUT = os.path.join(ROOT, "results", "lhb_inst_ic.json")

WINDOW_START = "2025-01-01"
HORIZONS = (1, 3, 5, 10, 20)
SIGNALS = {
    "inst_net_ratio": "机构净买额占总成交额比",
    "seat_diff": None,          # 买方机构数 - 卖方机构数
    "inst_net_over_mv": None,   # 机构买入净额 / (流通市值 * 1e8)
    # controls: these should NOT carry information at h=5/10 -- if they do, the
    # machinery is reading the event-day move itself rather than the seats.
    "turnover": "换手率",
    "event_return": "涨跌幅",
}
PRIMARY = "inst_net_ratio"
CRIT = {"ic_min": 0.030, "t_min": 3.0, "spread_min": 0.50, "h_main": 5}


def _tx_symbol(code6):
    c = str(code6).strip().zfill(6)
    if c[0] in "69":
        return "sh" + c
    if c[0] in "03":
        return "sz" + c
    return None  # 4/8/920 = 北交所, tencent path differs -> honest skip


# --------------------------------------------------------------------------- fetch
def _fetch_one(sym, start, end):
    q = urllib.parse.urlencode({"param": "%s,day,%s,%s,400,qfq" % (sym, start, end)})
    url = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?" + q
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=12) as r:
                j = json.loads(r.read().decode("utf-8"))
            d = j.get("data", {}).get(sym, {})
            rows = d.get("qfqday") or d.get("day") or []
            if not rows:
                return sym, []
            out = []
            for row in rows:
                if len(row) < 3:
                    continue
                out.append((row[0], float(row[1]), float(row[2])))
            return sym, out
        except Exception:
            if attempt == 2:
                return sym, None
            time.sleep(0.6 * (attempt + 1))
    return sym, None


def cmd_fetch(args):
    import pandas as pd

    d = pd.read_parquet(LHB, columns=["代码", "上榜日期"])
    d["上榜日期"] = pd.to_datetime(d["上榜日期"]).dt.strftime("%Y-%m-%d")
    d = d[d["上榜日期"] >= (args.start or WINDOW_START)]
    codes = sorted({_tx_symbol(c) for c in d["代码"].unique()} - {None})
    os.makedirs(PX_DIR, exist_ok=True)
    prog = {}
    if os.path.exists(PX_PROGRESS):
        prog = json.load(open(PX_PROGRESS, encoding="utf-8"))
    done = set(k for k, v in prog.items() if v.get("rows"))
    todo = [c for c in codes if c not in done]
    if args.limit:
        todo = todo[: args.limit]
    end = args.end
    start = args.px_start
    print("codes=%d already=%d todo=%d" % (len(codes), len(done), len(todo)))

    def work(sym):
        r = _fetch_one(sym, start, end)
        return r

    t0 = time.time()
    ok = bad = 0
    with ThreadPoolExecutor(max_workers=args.threads) as ex:
        for i, (sym, rows) in enumerate(ex.map(work, todo), 1):
            if rows is None:
                prog[sym] = {"rows": 0, "error": "fetch_failed"}
                bad += 1
            elif not rows:
                prog[sym] = {"rows": 0, "error": "empty"}
                bad += 1
            else:
                pd.DataFrame(rows, columns=["date", "open", "close"]).to_parquet(
                    os.path.join(PX_DIR, sym + ".parquet"), index=False
                )
                prog[sym] = {"rows": len(rows), "first": rows[0][0], "last": rows[-1][0]}
                ok += 1
            if i % 200 == 0:
                json.dump(prog, open(PX_PROGRESS, "w", encoding="utf-8"))
                print("  %d/%d ok=%d bad=%d %.0fs" % (i, len(todo), ok, bad, time.time() - t0))
    json.dump(prog, open(PX_PROGRESS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("FETCH done ok=%d bad=%d elapsed=%.0fs" % (ok, bad, time.time() - t0))
    return 0 if ok else 2


# ----------------------------------------------------------------------------- run
def _ranks(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    r = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(x, y):
    if len(x) < 3:
        return None
    rx, ry = _ranks(x), _ranks(y)
    n = len(rx)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my) ** 2 for b in ry) ** 0.5
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def build_events(start, min_events=8):
    """Return events: list of dicts with signal values and abnormal returns by horizon."""
    import pandas as pd

    d = pd.read_parquet(LHB)
    d["上榜日期"] = pd.to_datetime(d["上榜日期"]).dt.strftime("%Y-%m-%d")
    d = d[d["上榜日期"] >= start].copy()
    for c in ("买方机构数", "卖方机构数", "机构买入净额", "市场总成交额", "机构净买额占总成交额比",
              "换手率", "涨跌幅", "流通市值"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    # one row per (code, date): the same stock can be listed under several reasons in
    # one session -- summing the seats and keeping one turnover figure avoids counting
    # the same trade twice.
    g = d.groupby(["代码", "上榜日期"], as_index=False).agg({
        "买方机构数": "sum", "卖方机构数": "sum", "机构买入净额": "sum",
        "市场总成交额": "mean", "机构净买额占总成交额比": "mean",
        "换手率": "mean", "涨跌幅": "mean", "流通市值": "mean",
    })
    g["seat_diff"] = g["买方机构数"] - g["卖方机构数"]
    g["inst_net_over_mv"] = g["机构买入净额"] / (g["流通市值"] * 1e8)
    g = g[g["机构买入净额"].notna() & g["市场总成交额"].gt(0)]

    idx = {}
    with open(IDX_CSV, encoding="utf-8") as f:
        next(f)
        for line in f:
            p = line.strip().split(",")
            if len(p) >= 2 and p[1]:
                idx[p[0]] = float(p[1])

    events = []
    missing = 0
    for row in g.itertuples(index=False):
        sym = _tx_symbol(row.代码)
        if not sym:
            missing += 1
            continue
        p = os.path.join(PX_DIR, sym + ".parquet")
        if not os.path.exists(p):
            missing += 1
            continue
        px = pd.read_parquet(p)
        pos = {dt: i for i, dt in enumerate(px["date"].tolist())}
        i0 = pos.get(row.上榜日期)
        if i0 is None:
            continue
        opens = px["open"].tolist()
        dates = px["date"].tolist()
        ev = {"date": row.上榜日期, "code": row.代码}
        for s, col in SIGNALS.items():
            ev[s] = getattr(row, "机构净买额占总成交额比") if col == "机构净买额占总成交额比" else None
        ev[PRIMARY] = row.机构净买额占总成交额比
        ev["seat_diff"] = row.seat_diff
        ev["inst_net_over_mv"] = row.inst_net_over_mv
        ev["turnover"] = row.换手率
        ev["event_return"] = row.涨跌幅
        if i0 + 1 >= len(opens):
            continue
        entry = opens[i0 + 1]
        if not entry or entry <= 0:
            continue
        got = False
        for h in HORIZONS:
            j = i0 + 1 + h
            if j >= len(opens) or not opens[j] or opens[j] <= 0:
                continue
            d_in, d_out = dates[i0 + 1], dates[j]
            if d_in not in idx or d_out not in idx:
                continue
            stock = opens[j] / entry - 1.0
            bench = idx[d_out] / idx[d_in] - 1.0
            ev["ar_%d" % h] = (stock - bench) * 100.0
            got = True
        if got:
            events.append(ev)
    return events, {"lhb_rows": int(len(d)), "events": len(events), "no_price_panel": missing}


def _daily_ic(events, sig, h, min_events=8):
    by_date = {}
    for e in events:
        v = e.get(sig)
        a = e.get("ar_%d" % h)
        if v is None or a is None:
            continue
        by_date.setdefault(e["date"], []).append((v, a))
    ics = []
    for dt, pairs in sorted(by_date.items()):
        if len(pairs) < min_events:
            continue
        ic = spearman([p[0] for p in pairs], [p[1] for p in pairs])
        if ic is not None:
            ics.append(ic)
    if len(ics) < 5:
        return {"n_days": len(ics), "mean": None, "t": None, "pct_pos": None}
    m = statistics.fmean(ics)
    sd = statistics.pstdev(ics) if len(ics) > 1 else 0.0
    t = m / (sd / len(ics) ** 0.5) if sd > 0 else None
    return {"n_days": len(ics), "mean": round(m, 4),
            "t": round(t, 2) if t else None,
            "pct_pos": round(100.0 * sum(1 for x in ics if x > 0) / len(ics), 1)}


def _tercile_spread(events, sig, h):
    """T3-T1 spread of the within-date demeaned abnormal return."""
    by_date = {}
    for e in events:
        v = e.get(sig)
        a = e.get("ar_%d" % h)
        if v is None or a is None:
            continue
        by_date.setdefault(e["date"], []).append((v, a))
    pooled = []
    for dt, pairs in by_date.items():
        if len(pairs) < 8:
            continue
        m = statistics.fmean([p[1] for p in pairs])
        for v, a in pairs:
            pooled.append((v, a - m))
    if len(pooled) < 30:
        return None
    pooled.sort(key=lambda x: x[0])
    n = len(pooled)
    k = max(1, n // 3)
    t1 = statistics.fmean([p[1] for p in pooled[:k]])
    t3 = statistics.fmean([p[1] for p in pooled[-k:]])
    return {"n": n, "t1": round(t1, 3), "t3": round(t3, 3), "spread": round(t3 - t1, 3)}


def cmd_run(args):
    t0 = time.time()
    events, meta = build_events(args.start or WINDOW_START)
    if not events:
        print("no events -- run fetch first"); return 2
    table = {}
    for sig in [PRIMARY, "seat_diff", "inst_net_over_mv", "turnover", "event_return"]:
        table[sig] = {}
        for h in HORIZONS:
            ic = _daily_ic(events, sig, h)
            sp = _tercile_spread(events, sig, h)
            table[sig]["h%d" % h] = {"ic": ic, "tercile": sp}

    h = CRIT["h_main"]
    main = table[PRIMARY]["h%d" % h]
    ic_m, ic_t = main["ic"]["mean"], main["ic"]["t"]
    spread = main["tercile"]["spread"] if main["tercile"] else None
    c1 = bool(ic_m is not None and ic_t is not None and abs(ic_m) >= CRIT["ic_min"] and abs(ic_t) >= CRIT["t_min"])
    c2 = bool(spread is not None and abs(spread) >= CRIT["spread_min"]
              and ic_m is not None and (spread > 0) == (ic_m > 0))
    signs = []
    for hh in (10, 20):
        sp = table[PRIMARY]["h%d" % hh]["tercile"]
        if sp:
            signs.append(sp["spread"] > 0)
    c3 = bool(spread is not None and len(signs) == 2 and all(s == (spread > 0) for s in signs))
    verdict = "OPEN" if (c1 and c2 and c3) else "CLOSE"

    payload = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": max(e["date"] for e in events if e.get("ar_1") is not None),
        "window_start": args.start or WINDOW_START,
        "events": meta["events"], "lhb_rows": meta["lhb_rows"],
        "no_price_panel": meta["no_price_panel"],
        "benchmark": "sh000852 (CSI1000), close-to-close; stock leg open-to-open from t+1",
        "frozen_criteria": CRIT,
        "table": table,
        "verdict": {
            "verdict": verdict,
            "C1_information": c1, "C2_tercile": c2, "C3_persistence": c3,
            "primary_ic_h5": ic_m, "primary_t_h5": ic_t,
            "primary_spread_h5_pct": spread,
            "signs_h10_h20": signs,
            "rule": "OPEN only if C1 and C2 and C3; anything else = CLOSE the line",
        },
        "caveats": [
            "prices from Tencent qfq, collected today; a later qfq re-basing moves old bars "
            "with the same factor inside one response, so returns are internally consistent "
            "but not byte-identical to the sina panel.",
            "the index leg is close-to-close while the stock leg is open-to-open: the half "
            "session mismatch is disclosed, not modelled.",
            "北交所 codes (4/8/920) are skipped -- tencent path differs; count is in "
            "no_price_panel.",
            "LHB seats are disclosed after the close, so an entry at the next open is the "
            "earliest executable fill; no same-day use is claimed.",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(payload, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(payload["verdict"], ensure_ascii=False, indent=1))
    for sig in table:
        row = ["%-18s" % sig]
        for hh in HORIZONS:
            ic = table[sig]["h%d" % hh]["ic"]
            row.append("h%02d %+.3f(t%+.1f)" % (hh, ic["mean"] if ic["mean"] is not None else 0.0,
                                                ic["t"] if ic["t"] is not None else 0.0))
        print("  ".join(row))
    print("events=%d elapsed=%.0fs -> %s" % (meta["events"], time.time() - t0, OUT))
    return 0


# ------------------------------------------------------------------------ selftest
def cmd_selftest():
    ok = []
    # 1. spearman sanity: monotone -> 1.0, reversed -> -1.0, flat -> None
    ok.append(("spearman monotone", abs(spearman([1, 2, 3, 4], [10, 20, 30, 40]) - 1.0) < 1e-9))
    ok.append(("spearman reversed", abs(spearman([1, 2, 3, 4], [40, 30, 20, 10]) + 1.0) < 1e-9))
    ok.append(("spearman flat none", spearman([1, 1, 1, 1], [1, 2, 3, 4]) is None))
    # 2. daily IC: a signal that IS the return must read 1.0 on every date
    ev = []
    for d in range(6):
        for i in range(10):
            ev.append({"date": "2026-01-%02d" % (d + 1), PRIMARY: float(i),
                       "ar_5": float(i) * 0.1, "seat_diff": 0.0, "turnover": 1.0})
    ic = _daily_ic(ev, PRIMARY, 5)
    ok.append(("ic perfect", abs(ic["mean"] - 1.0) < 1e-9 and ic["t"] is None))
    # 3. tercile spread on demeaned returns: top third must beat bottom third
    sp = _tercile_spread(ev, PRIMARY, 5)
    ok.append(("tercile positive", sp is not None and sp["spread"] > 0))
    # 4. a constant signal cannot produce a spread (all ties -> one bucket dominates)
    ev2 = [dict(e) for e in ev]
    for e in ev2:
        e[PRIMARY] = 0.0
    sp2 = _tercile_spread(ev2, PRIMARY, 5)
    ok.append(("tercile flat signal has no spread", sp2 is not None and abs(sp2["spread"]) < 1e-9))
    # 5. tx symbol mapping
    ok.append(("tx symbol", _tx_symbol("600000") == "sh600000" and _tx_symbol("300750") == "sz300750"
               and _tx_symbol("830799") is None))
    passed = sum(1 for _, v in ok if v)
    for name, v in ok:
        print(("  PASS  " if v else "  FAIL  ") + name)
    print("selftest: %d/%d PASS" % (passed, len(ok)))
    return 0 if passed == len(ok) else 1


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    f = sub.add_parser("fetch"); f.add_argument("--start", default=None)
    f.add_argument("--px-start", default="2024-12-01"); f.add_argument("--end", default="2026-11-14")
    f.add_argument("--threads", type=int, default=8); f.add_argument("--limit", type=int, default=0)
    r = sub.add_parser("run"); r.add_argument("--start", default=None)
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "fetch":
        return cmd_fetch(a)
    if a.cmd == "run":
        return cmd_run(a)
    if a.cmd == "selftest":
        return cmd_selftest()
    ap.print_help(); return 2


if __name__ == "__main__":
    sys.exit(main() or 0)
