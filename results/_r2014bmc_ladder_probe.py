# -*- coding: utf-8 -*-
"""r2014 probe: how much does the repo term ladder pay over GC001-only?

Read-only sizing probe before committing to a full face.  Answers one question:
in the same 20-trading-day cash window r2013 priced with GC001, how much more
would a *pre-committed* term ladder have earned, using only quotes observable
on the entry day (no look-ahead, no rolling into unknown future quotes)?
"""
import math
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.join(ROOT, "data", "repo_daily")
TERMS = {"GC001": 1, "GC003": 3, "GC004": 4, "GC007": 7, "GC014": 14, "GC028": 28}
HOLD = 20


def load(code):
    p = os.path.join(REPO, code + ".csv")
    d, r = [], []
    with open(p, "r", encoding="utf-8") as fh:
        head = fh.readline().strip().split(",")
        ci, di = head.index("close"), head.index("date")
        for raw in fh:
            parts = raw.strip().split(",")
            if len(parts) <= max(ci, di):
                continue
            try:
                v = float(parts[ci])
            except ValueError:
                continue
            if not math.isfinite(v) or v <= 0 or v > 200:
                continue
            d.append(parts[di])
            r.append(v)
    return d, np.array(r)


def ladder_days(total_days):
    """Greedy longest-first split of a natural-day gap into repo terms."""
    left, plan = int(total_days), []
    for code in ("GC028", "GC014", "GC007", "GC004", "GC003"):
        n = TERMS[code]
        while left >= n and len(plan) < 8:
            plan.append(code)
            left -= n
    plan.extend(["GC001"] * left)
    return plan


def main():
    tapes = {c: load(c) for c in TERMS}
    cal, _ = tapes["GC001"]
    # d0 = every 20th trading day from 2020-01-02, same grid family as r2013
    start = next(i for i, d in enumerate(cal) if d >= "2020-01-02")
    idx = {}
    for c, (d, r) in tapes.items():
        idx[c] = {dd: i for i, dd in enumerate(d)}

    diffs, base_y, lad_y, ceil_y, spans = [], [], [], [], []
    for t in range(start, len(cal) - HOLD, HOLD):
        d0, d1 = cal[t], cal[t + HOLD]
        span = (np.datetime64(d1) - np.datetime64(d0)).astype(int)  # natural days
        # BASE: daily GC001 quotes over the panel window (r2013 booking)
        g = 1.0
        for k in range(t + 1, t + HOLD + 1):
            g *= 1.0 + tapes["GC001"][1][k] / 100.0 / 365.0
        base = g - 1.0
        # LADDER: one pre-committed plan bought on d0 at d0 quotes
        plan = ladder_days(span)
        g = 1.0
        for code in plan:
            i = idx[code].get(d0)
            if i is None:
                rate = None
                for j in range(len(tapes[code][0]) - 1, -1, -1):
                    if tapes[code][0][j] <= d0:
                        rate = tapes[code][1][j]
                        break
                if rate is None:
                    g = float("nan")
                    break
            else:
                rate = tapes[code][1][i]
            g *= 1.0 + rate / 100.0 / 365.0 * TERMS[code]
        lad = g - 1.0
        # CEILING (look-ahead, reference only): best single term per window
        best = None
        for code, n in TERMS.items():
            i = idx[code].get(d0)
            if i is None or n > span:
                continue
            v = tapes[code][1][i] / 100.0 / 365.0 * n
            best = v if best is None else max(best, v)
        ceil = best if best is not None else float("nan")
        if not (math.isfinite(base) and math.isfinite(lad)):
            continue
        diffs.append(lad - base)
        base_y.append(base)
        lad_y.append(lad)
        ceil_y.append(ceil)
        spans.append(span)

    d = np.array(diffs)
    ann = lambda xs: (float(np.mean(xs)) * (250.0 / (HOLD + 0.0)) * 100.0)  # pp per year
    print(json_dumps := "")
    print("periods=%d  span_days median=%.0f min=%.0f max=%.0f" % (
        len(spans), np.median(spans), min(spans), max(spans)))
    print("base mean per period = %.6f%%   ladder mean = %.6f%%" % (
        np.mean(base_y) * 100, np.mean(lad_y) * 100))
    print("ladder minus base (per period) = %.6f%%  -> %.3f pp/yr" % (
        d.mean() * 100, ann(d)))
    print("win rate (ladder>base) = %.1f%%" % (100.0 * np.mean(d > 0)))
    print("worst/ best = %.5f%% / %.5f%%" % (d.min() * 100, d.max() * 100))
    print("base annualised ~= %.3f pp/yr" % ann(base_y))


if __name__ == "__main__":
    main()
