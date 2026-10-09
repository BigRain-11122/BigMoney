# r945 bm-a: PARKING-P1 §7.3 rolling 3y/5y worst-window descriptive readings.
# Reuses the frozen runner's own machinery (load_panels/stint_cell) -- zero new
# trials, zero judgment change; pure disclosure of already-census stint families.
import io
import json
import sys

sys.path.insert(0, "scripts")
import numpy as np
import parking_p1 as P

W = {"3y": 3 * 250, "5y": 5 * 250}   # trading-day windows per prereg spirit


def roll_worst(code, d):
    panels, rate = P.load_panels()
    p = panels[code]
    cell = P.stint_cell(p["close"], d, p["carry_prefix"], P.COST_RT_X1)
    if cell is None:
        return None
    dates = [str(x) for x in p["dates"][cell["entries"]]]
    u = cell["pickup_c2"]
    out = {}
    for name, w in W.items():
        best = None
        for i in range(len(u)):
            lo = dates[i]
            vals = [u[j] for j in range(i, len(u)) if dates[j] <= _add(dates[i], w)]
            if len(vals) < 12:      # skip degenerate short windows
                continue
            m = float(np.mean(vals))
            if best is None or m < best[0]:
                best = (m, lo, len(vals))
        out[name] = {"worst_window_mean_pickup": round(best[0], 6),
                     "window_start": best[1], "n_stints_in_window": best[2]}
    return out


def _add(day, n):
    # trading-day proxy: entries are every 5th bar; count bars via date index
    # map on the panel calendar instead of guessing -- simple string day math
    # is wrong across holidays, so reindex via panel dates.
    global _PANEL_DATES
    if "_PANEL_DATES" not in globals():
        return day  # fallback (unused path)
    return day


def main():
    panels, rate = P.load_panels()
    res = {}
    for code in ("511090", "511260", "511380"):
        p = panels[code]
        dates_all = [str(x) for x in p["dates"]]
        idx = {dd: i for i, dd in enumerate(dates_all)}
        cell = P.stint_cell(p["close"], 120, p["carry_prefix"], P.COST_RT_X1)
        ed = [str(x) for x in p["dates"][cell["entries"]]]
        u = cell["pickup_c2"]
        res[code] = {}
        for name, w in W.items():
            worst = None
            j0 = 0
            for i in range(len(u)):
                # window = panel bars [idx[ed[i]], idx[ed[i]]+w) -- entry dates inside
                hi_bar = idx[ed[i]] + w
                vals, j = [], i
                while j < len(u) and idx[ed[j]] < hi_bar:
                    vals.append(u[j])
                    j += 1
                if len(vals) < 12:
                    continue
                m = float(np.mean(vals))
                if worst is None or m < worst[0]:
                    worst = (m, ed[i], len(vals))
            res[code][name] = {
                "worst_window_mean_pickup": round(worst[0], 6),
                "window_start": worst[1],
                "n_stints_in_window": worst[2]}
    io.open("results/_r945bma_parking_rollwindow.json", "w",
            encoding="utf-8").write(json.dumps(res, indent=1, ensure_ascii=False))
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
