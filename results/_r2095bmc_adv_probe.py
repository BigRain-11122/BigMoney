# -*- coding: utf-8 -*-
"""r2095 probe 2: K1-shaped capacity for the carry book (1% of 20-bar median ADV).

Same rule shape as etf_book_capacity_edge: one day's own order <= 1% of the traded
thing's ADV; ADV = 20-bar median of volume; stability over the last 60 sessions
(print the weakest session, not just the median). Plus two carry-specific readings the
ETF book has no analog for: standing position vs open interest, and the roll day's
incoming-contract volume (you must move the whole book on/around that day).
"""
import glob
import io
import json
import os
import statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUT = os.path.join(ROOT, "data", "futures_contracts")
PRODUCTS = ("IC", "IM")
ADV_BARS = 20
WINDOW = 60
SHARE = 0.01


def load(prod):
    out = {}
    for p in sorted(glob.glob(os.path.join(FUT, prod + "[0-9]*.csv"))):
        name = os.path.basename(p)[:6]
        rows = {}
        with io.open(p, encoding="utf-8") as fh:
            head = fh.readline().strip().split(",")
            ix = {k: i for i, k in enumerate(head)}
            for line in fh:
                c = line.strip().split(",")
                if len(c) < 7:
                    continue
                try:
                    rows[c[ix["date"]]] = (float(c[ix["volume"]]), float(c[ix["hold"]]),
                                           float(c[ix["close"]]))
                except (KeyError, ValueError):
                    continue
        if rows:
            out[name] = rows
    return out


def main():
    for prod in PRODUCTS:
        cs = load(prod)
        front = {}
        for name, rows in cs.items():
            for d, (v, h, c) in rows.items():
                cur = front.get(d)
                if cur is None or h > cur[2]:
                    front[d] = (name, v, h, c)
        dates = sorted(front)
        win = dates[-WINDOW:]
        # 20-bar median ADV, readable on each session of the window
        advs, ois, vols = [], [], []
        for i, d in enumerate(win):
            hist = [front[x][1] for x in dates if x <= d][-ADV_BARS:]
            advs.append(st.median(hist))
            ois.append(front[d][2])
            vols.append(front[d][1])
        weakest = min(advs)
        wk_date = win[advs.index(weakest)]
        print("## %s window %s..%s" % (prod, win[0], win[-1]))
        print("   adv20 median=%s weakest=%s @%s  -> 1%% lots: %s / %s"
              % (format(int(st.median(advs)), ","), format(int(weakest), ","), wk_date,
                 format(int(st.median(advs) * SHARE), ","), format(int(weakest * SHARE), ",")))
        print("   vol/OI median=%.3f   OI median=%s  1%% OI lots=%s"
              % (st.median([v / o for v, o in zip(vols, ois) if o]), format(int(st.median(ois)), ","),
                 format(int(st.median(ois) * SHARE), ",")))
        # roll days: identity change inside window
        for i in range(1, len(win)):
            if front[win[i]][0] != front[win[i - 1]][0]:
                inc = front[win[i]][0]
                seq = [x for x in dates if (x >= win[i] and inc in cs and x in cs[inc])][:3]
                vols3 = [(x, cs[inc][x][0]) for x in seq]
                print("   roll %s -> %s  day vol=%s  first-3-as-front total=%s"
                      % (win[i], inc, format(int(cs[inc][win[i]][0]), ","),
                         format(int(sum(v for _x, v in vols3)), ",")))
                print("      1%% of one-day=%s lots ; 1%% of 3-day=%s lots"
                      % (format(int(cs[inc][win[i]][0] * SHARE), ","),
                         format(int(sum(v for _x, v in vols3) * SHARE), ",")))


if __name__ == "__main__":
    main()
