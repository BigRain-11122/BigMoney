"""Paper ledger for the bond-free ETF book (production candidate, staggered 5+5).

Production book (decided 2026-10-25 from the capacity/stagger study):
  * universe: equity + commodity + convertible ETFs (bond/money excluded -- the sleeve
    split showed the composite has no bond-selection skill)
  * two sleeves of 5 names each, 10-day clock, offset 5 days: on any given day only one
    sleeve turns over, which cut turnover from 1.22 to 0.74 and lifted Sharpe 1.16 -> 1.32
  * 10% per name (0.5 sleeve capital / 5 names), signal at close, fill next open
  * 8% volatility target as a scale on the combined book (de-lever only, never above 1)

Ledger contract: append-only JSONL, one row per signal date; re-running the same date
replaces that row (idempotent for a scheduled task). Each sleeve carries its own next-due
date, so a skipped run still rebalances on the next run instead of silently drifting.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_equity_alpha as A
from config import PATHS

LEDGER = os.path.join(PATHS.results_dir, "etf_paper", "ledger.jsonl")
REBAL = 10
SLEEVES = 2
PER_SLEEVE = 5
N_TOTAL = SLEEVES * PER_SLEEVE
TARGET_VOL = 0.08
BOND_FREE = ("equity", "commodity", "convertible")


def load_ledger():
    if not os.path.exists(LEDGER):
        return []
    rows = []
    with open(LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def save_ledger(rows):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    tmp = LEDGER + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, LEDGER)


def _iso(d):
    return d.strftime("%Y-%m-%d")


def due(st, today_iso, pos):
    """Is this sleeve due to rebalance?

    Date-anchored when the sleeve carries a next_due_date: the position index is only
    meaningful against one exact panel, and this panel's history window can grow or
    shrink between refreshes, which would silently slide every future rebalance (and
    with it the 5-day stagger that the whole book rests on). The date survives that.
    Position comparison stays only as a fallback for legacy rows that have no date.
    """
    d = st.get("next_due_date")
    if d:
        return today_iso >= d
    return pos >= int(st.get("next_due_pos", pos))


def anchor_sleeves(sleeve_state, dates, pos):
    """Give every sleeve a date anchor; derive one for legacy position-only rows."""
    for st in sleeve_state:
        st.setdefault("next_due_pos", pos)
        if not st.get("next_due_date"):
            p = int(st["next_due_pos"])
            st["next_due_date"] = _iso(dates[p]) if 0 <= p < len(dates) else None
        st.setdefault("schedule_anchor", "date" if st.get("next_due_date") else "pos")
    return sleeve_state


def load_calendar():
    """Official exchange trading days (data/exchange_calendar.csv, E136 face)."""
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "exchange_calendar.csv")
    if not os.path.exists(path):
        return []
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s and s[0].isdigit():
                out.append(s[:10])
    return out


def project_due_date(dates, due_pos, cal_days=None):
    """Turn a future bar position into a calendar date a human can act on.

    Inside the panel the index is the answer. Past the panel's last bar we count the
    official calendar's trading days instead of guessing, and return None rather than a
    made-up date when the calendar runs out.
    """
    if due_pos < len(dates):
        return _iso(dates[due_pos])
    cal_days = load_calendar() if cal_days is None else cal_days
    last = _iso(dates[-1])
    future = [d for d in cal_days if d > last]
    ahead = int(due_pos) - (len(dates) - 1)
    if ahead <= 0 or len(future) < ahead:
        return None
    return future[ahead - 1]


def book_vol(rets, weights, upto):
    if not weights:
        return np.nan
    window = rets.loc[:upto].tail(60)[list(weights)]
    if window.shape[0] < 20:
        return np.nan
    w = np.array([weights[k] for k in window.columns])
    cov = window.cov().to_numpy()
    return float(np.sqrt(w @ cov @ w) * np.sqrt(252))


def main_run():
    close, openp, amt, feats = E.build_panel()
    close, openp, _ = A.repair_flips(close, openp)
    cls = A.classify(close.columns, A.load_class_map(), close)
    cols = [c for c in close.columns if cls[c] in BOND_FREE]
    score = E.build_score(close[cols], amt[cols], feats)

    dates = [d for d in close.index if d in score.index]
    today = dates[-1]
    pos = len(dates) - 1

    rows = load_ledger()
    prev = rows[-1] if rows else None

    # initialise sleeves on first ever run; afterwards carry their own positions forward
    if prev:
        sleeve_state = prev.get("sleeves", [])
    else:
        sleeve_state = [{"leg": k, "next_due_pos": pos, "weights": {}, "picks": []}
                        for k in range(SLEEVES)]

    if len(sleeve_state) != SLEEVES:
        sleeve_state = [{"leg": k, "next_due_pos": pos, "weights": {}, "picks": []}
                        for k in range(SLEEVES)]
    sleeve_state = anchor_sleeves(sleeve_state, dates, pos)
    today_iso = _iso(dates[pos])

    s = score.loc[today].dropna()
    ranked = list(s.nlargest(N_TOTAL).index) if len(s) >= N_TOTAL else []

    # initialising both sleeves on the same day would make them rebalance together and
    # lose the stagger, so the first due position carries a half-period offset per sleeve.
    first_run = prev is None
    for st in sleeve_state:
        if ranked and due(st, today_iso, pos):
            leg = int(st["leg"])
            window = ranked[leg * PER_SLEEVE:(leg + 1) * PER_SLEEVE]
            if len(window) == PER_SLEEVE:
                st["weights"] = {p: round(0.5 / PER_SLEEVE, 6) for p in window}
                st["picks"] = window
                step = REBAL + (REBAL // SLEEVES) * leg if first_run else REBAL
                due_pos = pos + step
                st["next_due_pos"] = due_pos
                st["next_due_date"] = _iso(dates[due_pos]) if due_pos < len(dates) else None
                st["schedule_anchor"] = "date" if st["next_due_date"] else "pos"

    combined = {}
    for st in sleeve_state:
        for p, w in st["weights"].items():
            combined[p] = round(combined.get(p, 0.0) + w, 6)

    rets = close[cols].pct_change()
    v = book_vol(rets, combined, today) if combined else np.nan
    scale = float(min(1.0, TARGET_VOL / v)) if np.isfinite(v) and v > 0 else 1.0
    weights = {p: round(w * scale, 6) for p, w in combined.items()}

    nav = 1.0
    period_ret = None
    if prev and prev.get("as_of") != str(today.date()):
        a = pd.Timestamp(prev["as_of"])
        r = 0.0
        for p, w in prev["weights"].items():
            x, y = close.at[a, p], close.at[today, p]
            if np.isfinite(x) and np.isfinite(y) and x > 0:
                r += w * (y / x - 1.0)
        period_ret = round(float(r), 6)
        nav = round(float(prev["nav"]) * (1.0 + r), 6)

    row = {
        "as_of": str(today.date()),
        "config": "bond-free, staggered 5+5, R10, 8% vol target",
        "sleeves": sleeve_state,
        "weights": weights,
        "picks": [{"symbol": p, "class": str(cls[p]), "weight": weights[p],
                   "score": round(float(s[p]), 4) if p in s.index else None}
                  for p in weights],
        "realised_vol_60d": round(float(v), 4) if np.isfinite(v) else None,
        "vol_scale": round(scale, 4),
        "cash_weight": round(1.0 - sum(weights.values()), 6),
        "period_return": period_ret,
        "nav": nav,
        "next_actions": [{"leg": int(st["leg"]), "due_date": st.get("next_due_date"),
                          "due_date_estimate": project_due_date(dates, int(st["next_due_pos"])),
                          "due_pos": st.get("next_due_pos"),
                          "anchor": st.get("schedule_anchor")}
                         for st in sleeve_state],
    }

    rows = [r for r in rows if r.get("as_of") != row["as_of"]] + [row]
    rows.sort(key=lambda x: x["as_of"])
    save_ledger(rows)

    print("as_of", row["as_of"], "nav", nav, "period_ret", period_ret,
          "vol", row["realised_vol_60d"], "scale", row["vol_scale"])
    for p in row["picks"]:
        print("  ", p["symbol"], p["class"], p["weight"], p["score"])
    for st in sleeve_state:
        print("  sleeve", st["leg"], "next_due", st.get("next_due_date"),
              "est", project_due_date(dates, int(st["next_due_pos"])),
              "pos", st["next_due_pos"], "anchor", st.get("schedule_anchor"),
              "n", len(st["weights"]))


def selftest():
    """Offline legs for the schedule anchor (the face a human reads to know when to act).

    The regression this guards: on 2026-10-27 the ledger carried only position anchors
    (5274/5279), which no reader could turn into a date, and which would slide by however
    many bars the panel's history window happened to add or drop.
    """
    legs = []

    def leg(name, ok, extra=""):
        legs.append((name, bool(ok), extra))

    dates = pd.bdate_range("2026-10-01", periods=40)
    today = dates[20]

    st = {"leg": 0, "next_due_pos": 25, "next_due_date": _iso(dates[25])}
    leg("date anchor: not due before its date", not due(st, _iso(dates[24]), 24))
    leg("date anchor: due on its date", due(st, _iso(dates[25]), 25))
    leg("date anchor: still due after its date", due(st, _iso(dates[27]), 27))

    # panel grows by 5 bars at the front: the same sleeve now sits at a different index.
    shifted = dict(st)
    leg("panel shift: position no longer matches, date still holds",
        due(shifted, _iso(dates[25]), 30) and not due(shifted, _iso(dates[24]), 29))

    legacy = {"leg": 1, "next_due_pos": 33}
    anchor_sleeves([legacy], dates, 20)
    leg("legacy row anchored from its position", legacy["next_due_date"] == _iso(dates[33]),
        str(legacy.get("next_due_date")))
    leg("legacy row still falls back to pos when unmapable",
        not due({"next_due_pos": 33}, _iso(dates[20]), 20)
        and due({"next_due_pos": 21}, _iso(dates[20]), 21))

    # the reader's question is "when", not "which index": project past the panel's end
    # using the official calendar, and refuse to invent a date once it runs out.
    cal = [_iso(d) for d in pd.bdate_range("2026-10-01", periods=120)]
    inside = project_due_date(dates, 22, cal)
    leg("projection inside the panel is the panel's own date", inside == _iso(dates[22]), str(inside))
    outside = project_due_date(dates, (len(dates) - 1) + 3, cal)
    tail = [d for d in cal if d > _iso(dates[-1])]
    leg("projection past the panel counts calendar trading days",
        outside == tail[2], "%s vs %s" % (outside, tail[2]))
    leg("projection refuses to invent a date past the calendar",
        project_due_date(dates, len(dates) + len(tail) + 5, cal) is None)

    out = {"n": len(legs), "passed": sum(1 for _n, ok, _e in legs if ok), "legs": [
        {"leg": n, "ok": ok, "extra": e} for n, ok, e in legs]}
    for n, ok, extra in legs:
        print(("PASS " if ok else "FAIL ") + n + ((" | " + extra) if extra and not ok else ""))
    print("selftest %d/%d PASS" % (out["passed"], out["n"]))
    return 0 if out["passed"] == out["n"] else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    main_run()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
