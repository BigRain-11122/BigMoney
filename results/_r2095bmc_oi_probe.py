# -*- coding: utf-8 -*-
"""r2095 probe: is the front contract's own liquidity ever the binding gate for this book?

Reads only data/futures_contracts/<PROD><YYMM>.csv (date, open, high, low, close,
volume, hold). Front contract per date = the one with the largest hold that date (the
same rule a trader applies intraday; no future data). Prints, per product:
  * trailing window length and the last date
  * front OI / volume: median, min, and the 1%/2%/5% lots
  * roll days (front identity change) and the incoming front's OI/volume that day
  * the desk's top published rung in lots, and the multiple of headroom
"""
import glob
import io
import json
import os
import statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUT = os.path.join(ROOT, "data", "futures_contracts")
PRODUCTS = ("IC", "IM")
WINDOW = 60


def load_contracts(prod):
    out = {}
    for p in sorted(glob.glob(os.path.join(FUT, prod + "[0-9]*.csv"))):
        name = os.path.basename(p)[:6]
        rows = {}
        with io.open(p, encoding="utf-8") as fh:
            head = fh.readline().strip().split(",")
            idx = {k: i for i, k in enumerate(head)}
            for line in fh:
                c = line.strip().split(",")
                if len(c) < 7:
                    continue
                try:
                    rows[c[idx["date"]]] = (float(c[idx["volume"]]), float(c[idx["hold"]]),
                                            float(c[idx["close"]]))
                except (KeyError, ValueError):
                    continue
        if rows:
            out[name] = rows
    return out


def front_by_date(contracts):
    """date -> (contract, volume, hold, close) with the largest hold that date."""
    best = {}
    for name, rows in contracts.items():
        for d, (v, h, c) in rows.items():
            cur = best.get(d)
            if cur is None or h > cur[2]:
                best[d] = (name, v, h, c)
    return best


def main():
    for prod in PRODUCTS:
        cs = load_contracts(prod)
        front = front_by_date(cs)
        dates = sorted(front)
        win = dates[-WINDOW:]
        oi = [front[d][2] for d in win]
        vol = [front[d][1] for d in win]
        # roll days inside the window: contract identity changes
        rolls = []
        for i in range(1, len(win)):
            if front[win[i]][0] != front[win[i - 1]][0]:
                rolls.append((win[i], front[win[i]][0], front[win[i]][1], front[win[i]][2]))
        print("## %s  contracts=%d  window=%s..%s (%d sessions)"
              % (prod, len(cs), win[0], win[-1], len(win)))
        print("   front OI   median=%s  min=%s  max=%s"
              % (format(int(st.median(oi)), ","), format(int(min(oi)), ","),
                 format(int(max(oi)), ",")))
        print("   front vol  median=%s  min=%s  vol/OI=%.3f"
              % (format(int(st.median(vol)), ","), format(int(min(vol)), ","),
                 st.median(vol) / st.median(oi)))
        for pct in (0.5, 1.0, 2.0, 5.0):
            lots = st.median(oi) * pct / 100.0
            print("   %.1f%% of median OI = %s lots" % (pct, format(int(lots), ",")))
        for r in rolls:
            print("   roll %s -> %s  vol=%s OI=%s" % (r[0], r[1], format(int(r[2]), ","),
                                                      format(int(r[3]), ",")))
        # the last 3 sessions detail
        for d in win[-3:]:
            n, v, h, c = front[d]
            print("   last %s front=%s vol=%s OI=%s close=%.1f" % (d, n, format(int(v), ","),
                                                                   format(int(h), ","), c))


if __name__ == "__main__":
    main()
