"""REPO term-ladder rate pulse detector (T11 + T11-EXT, P2 tech queue, pure
measurement -- ZERO backtest, ZERO strategy claims, no engine touch).

Why: GC001 pre-holiday spikes are an in-repo empirical fact (research/
shortline/REPO_PANEL.md: 2015-02-10 GC001 53.44% true pre-Spring-Festival
cash squeeze). This probe measures the PULSE STRUCTURE of the panel:
which days are pulses, how they align with month-end / long-holiday-eve
/ quarter-end calendar faces, and conditional frequencies. Descriptive
statistics only -- any strategy face is out of scope (T-67 style
freeze discipline: measurement first, prereg later, if ever).

T11-EXT (r806): full 11-member term-ladder extension. Same frozen
per-member pulse definitions (no re-tuning); NEW descriptive ladder
faces, all derived from panel bytes only:
  - members: per-member measurement face for every data/repo_daily
    member (GC001/GC003/GC004/GC007/GC014/GC028/GC091/GC182 +
    R-001/R-003/R-007), in canonical tenor order
  - ladder.month_end_win_table / quarter_end_table: conditional pulse
    rates across the whole ladder (month-end vs non-month-end lift)
  - ladder.gc001_pulse_days: co-pulse linkage (how many members pulse
    on the same day GC001 pulses; per-member co-pulse rate) and
    cross-tenor transmission (per-member mean robust z on GC001 pulse
    days vs all other shared days)
Top-level fields remain the GC001 anchor face (backward compatible with
the r805 single-member artifact).

Data face: data/repo_daily/*.csv (columns date,open,high,low,close,
volume; close = annualized %; 15:30 collect law, sina same-source,
update_repo.py owned). This script never writes the panel.

Pulse definition (frozen in T11, not re-tuned for the ladder):
  - robust z vs trailing 20-obs baseline: z = (close - med20) /
    (1.4826 * MAD20); pulse if z >= 5.0
  - absolute tiers: T1 >= 10% annualized, T2 >= 20% (extreme squeeze)
  - a day qualifies as PULSE if (z >= 5.0) OR close >= 10.0

Calendar faces (from each panel's own trading calendar):
  - month_end_win: within last 3 calendar days of the month
  - quarter_end: last trading day of Mar/Jun/Sep/Dec
  - pre_long_holiday: gap to next trading day >= 3 calendar days
    (Spring Festival / National Day eves)
  - pre_weekend: Friday (next trading day >= 2 calendar days away)

Usage:
    python scripts/repo_pulse_probe.py            # measure -> results/repo_pulse_probe.json
    python scripts/repo_pulse_probe.py selftest   # offline synthetic guard

Exit codes: 0 ok | 2 mechanism error (panel missing / malformed).
"""
import datetime as dt
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS

PANEL_DIR = os.path.join(PATHS.data_dir, "repo_daily")
PANEL = os.path.join(PANEL_DIR, "GC001.csv")
OUT = os.path.join(PATHS.results_dir, "repo_pulse_probe.json")
# canonical tenor order (short -> long, SH GC ladder then SZ R ladder)
LADDER_ORDER = ["GC001", "GC003", "GC004", "GC007", "GC014", "GC028",
                "GC091", "GC182", "R-001", "R-003", "R-007"]
ANCHOR = "GC001"
BASE_WIN = 20          # trailing baseline window (obs before current day)
Z_PULSE = 5.0          # robust z pulse line (frozen, not tuned)
ABS_T1 = 10.0          # annualized % absolute tier-1
ABS_T2 = 20.0          # annualized % absolute tier-2
ME_WIN_DAYS = 3        # last-N-calendar-days-of-month window
LONG_HOL_GAP = 3       # calendar-day gap to next bar = long-holiday eve


def load_panel(path=PANEL):
    df = pd.read_csv(path)
    need = {"date", "close"}
    if not need.issubset(df.columns):
        raise RuntimeError(f"panel columns {list(df.columns)} lack {need}")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    if df["close"].isna().any():
        raise RuntimeError("panel close has NaN rows")
    return df


def annotate(df):
    """Calendar faces per row, derived from the panel's own calendar
    (no external holiday tables -- gap-based inference only)."""
    dates = df["date"]            # datetime64 dtype: keep for .dt math
    nxt = dates.shift(-1)
    df["gap_next"] = (nxt - dates).dt.days
    df["gap_prev"] = (dates - dates.shift(1)).dt.days
    df["pre_long_holiday"] = (df["gap_next"] >= LONG_HOL_GAP)
    df["pre_weekend"] = (df["gap_next"] >= 2)
    # month-end window: last ME_WIN_DAYS calendar days of the month
    dim = dates.dt.days_in_month
    df["month_end_win"] = dates.dt.day > (dim - ME_WIN_DAYS)
    df["quarter_end"] = (
        df["month_end_win"]
        & dates.dt.month.isin([3, 6, 9, 12])
        & (dates.dt.day + ME_WIN_DAYS >= dim)
    )
    # trailing robust baseline (previous BASE_WIN obs, current excluded):
    # single-pass sliding window -- a naive double-rolling MAD defers the
    # first valid z to 2*BASE_WIN-1 (first-attempt selftest red)
    arr = df["close"].to_numpy(dtype=float)
    med = pd.Series(arr).shift(1).rolling(BASE_WIN).median().to_numpy()
    mad = np.full(len(arr), np.nan)
    for p in range(BASE_WIN, len(arr)):
        w = arr[p - BASE_WIN:p]
        m = np.median(w)
        mad[p] = np.median(np.abs(w - m))
    scale = 1.4826 * mad
    with np.errstate(invalid="ignore", divide="ignore"):
        df["z"] = (arr - med) / scale   # NaN z (warmup rows) -> pulse_z False
    df["pulse_z"] = df["z"] >= Z_PULSE
    df["pulse_abs_t1"] = df["close"] >= ABS_T1
    df["pulse_abs_t2"] = df["close"] >= ABS_T2
    df["pulse"] = df["pulse_z"] | df["pulse_abs_t1"]
    return df


def cond_rate(df, mask):
    n = int(mask.sum())
    if n == 0:
        return {"n": 0, "rate": None}
    return {"n": n, "rate": round(float(df.loc[mask, "pulse"].mean()), 6)}


def measure(df, name=ANCHOR):
    total = int(len(df))
    pulses = df[df["pulse"]]
    other = ~df["month_end_win"]
    pre_lh = df["pre_long_holiday"]
    qe = df["quarter_end"]
    top = pulses.sort_values("close", ascending=False).head(10)
    top_rows = [
        {
            "date": d.strftime("%Y-%m-%d"),
            "close_pct": round(float(c), 3),
            "z": (round(float(z), 2)
                  if pd.notna(z) and np.isfinite(z) else None),
            "month_end_win": bool(m),
            "quarter_end": bool(q),
            "pre_long_holiday": bool(h),
            "pre_weekend": bool(w),
        }
        for d, c, z, m, q, h, w in zip(
            top["date"], top["close"], top["z"], top["month_end_win"],
            top["quarter_end"], top["pre_long_holiday"], top["pre_weekend"])
    ]
    return {
        "panel": name,
        "rows": total,
        "date_min": df["date"].min().strftime("%Y-%m-%d"),
        "date_max": df["date"].max().strftime("%Y-%m-%d"),
        "pulse_total": int(df["pulse"].sum()),
        "pulse_abs_t1": int(df["pulse_abs_t1"].sum()),
        "pulse_abs_t2": int(df["pulse_abs_t2"].sum()),
        "cond": {
            "month_end_win": cond_rate(df, df["month_end_win"]),
            "non_month_end": cond_rate(df, other),
            "pre_long_holiday": cond_rate(df, pre_lh),
            "quarter_end": cond_rate(df, qe),
            "pre_weekend": cond_rate(df, df["pre_weekend"]),
        },
        "top10_by_close": top_rows,
        "claim": ("pure measurement only: descriptive pulse frequencies; "
                  "no backtest, no strategy, no PnL, no admission face"),
    }


def member_files():
    found = {}
    for f in sorted(glob.glob(os.path.join(PANEL_DIR, "*.csv"))):
        found[os.path.splitext(os.path.basename(f))[0]] = f
    return found


def measure_ladder():
    """All-member faces + descriptive ladder linkage/transmission. Missing
    members and off-ladder files are reported honestly, never guessed."""
    files = member_files()
    members = {}
    frames = {}
    missing = [m for m in LADDER_ORDER if m not in files]
    extra = [m for m in files if m not in LADDER_ORDER]
    for m in LADDER_ORDER:
        if m not in files:
            continue
        df = annotate(load_panel(files[m]))
        members[m] = measure(df, m)
        frames[m] = df

    # --- month-end / quarter-end ladder tables (frozen cond faces) ---
    me_table, qe_table = [], []
    for m in LADDER_ORDER:
        if m not in frames:
            continue
        df = frames[m]
        me, non = cond_rate(df, df["month_end_win"]), cond_rate(df, ~df["month_end_win"])
        qe = cond_rate(df, df["quarter_end"])
        lift = (round(me["rate"] / non["rate"], 3)
                if me["rate"] and non["rate"] not in (None, 0) else None)
        me_table.append({"member": m, "month_end_win": me,
                         "non_month_end": non, "lift": lift})
        qe_table.append({"member": m, "quarter_end": qe})

    # --- GC001 pulse-day co-pulse + cross-tenor transmission ---
    gc = frames.get(ANCHOR)
    gc_face = {"anchor_pulse_days": 0}
    if gc is not None:
        gc_days = set(gc.loc[gc["pulse"], "date"].dt.strftime("%Y-%m-%d"))
        gc_face["anchor_pulse_days"] = len(gc_days)
        co_counts, per_rate, z_on, z_off, shared_n = {}, {}, {}, {}, {}
        z_drop_on, z_drop_off = {}, {}
        for m in LADDER_ORDER:
            if m == ANCHOR or m not in frames:
                continue
            df = frames[m]
            on = df["date"].dt.strftime("%Y-%m-%d").isin(gc_days)
            co_counts[m] = int((on & df["pulse"]).sum())
            per_rate[m] = (round(float(df.loc[on, "pulse"].mean()), 6)
                           if int(on.sum()) else None)
            # robust-z transmission means: drop NON-FINITE z (NaN warmup +
            # +/-inf from flat-baseline MAD=0 windows) and disclose counts
            # -- raw inf poisons means (GC091 -inf face, r806) and breaks
            # strict JSON
            v_on = df.loc[on, "z"].to_numpy(dtype=float)
            fin_on = v_on[np.isfinite(v_on)]
            v_off = df.loc[~on, "z"].to_numpy(dtype=float)
            fin_off = v_off[np.isfinite(v_off)]
            z_on[m] = (round(float(fin_on.mean()), 3) if fin_on.size else None)
            z_off[m] = (round(float(fin_off.mean()), 3) if fin_off.size else None)
            z_drop_on[m] = int(v_on.size - fin_on.size)
            z_drop_off[m] = int(v_off.size - fin_off.size)
            shared_n[m] = int(on.sum())
        if co_counts and gc_days:
            # mean co-pulsing members per anchor pulse day (co-count sum
            # over anchor days; exact when calendars are shared)
            gc_face["mean_copulse_members_per_anchor_day"] = round(
                sum(co_counts.values()) / len(gc_days), 3)
        gc_face["per_member_copulse_rate_on_gc001_pulse"] = per_rate
        gc_face["per_member_copulse_days_on_gc001_pulse"] = co_counts
        gc_face["per_member_shared_days"] = shared_n
        gc_face["per_member_mean_z_on_gc001_pulse_days"] = z_on
        gc_face["per_member_mean_z_other_shared_days"] = z_off
        gc_face["per_member_nonfinite_z_dropped_on"] = z_drop_on
        gc_face["per_member_nonfinite_z_dropped_off"] = z_drop_off

    ladder = {"ladder_order": LADDER_ORDER,
              "missing_members": missing,
              "off_ladder_files": extra,
              "month_end_win_table": me_table,
              "quarter_end_table": qe_table,
              "gc001_pulse_days": gc_face}
    return members, ladder


def run():
    anchor_df = annotate(load_panel())
    res = measure(anchor_df, ANCHOR)
    members, ladder = measure_ladder()
    res["members"] = {m: members[m] for m in LADDER_ORDER if m in members}
    res["ladder"] = ladder
    res["generated"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    summary = {m: {"rows": members[m]["rows"],
                   "pulses": members[m]["pulse_total"],
                   "me_rate": members[m]["cond"]["month_end_win"]["rate"],
                   "non_me_rate": members[m]["cond"]["non_month_end"]["rate"]}
               for m in LADDER_ORDER if m in members}
    print(json.dumps({"anchor": res["panel"], "rows": res["rows"],
                      "pulse_total": res["pulse_total"],
                      "ladder_members": summary,
                      "gc001_pulse_days":
                      ladder["gc001_pulse_days"].get("anchor_pulse_days")},
                     ensure_ascii=False, indent=1))
    print(f"[repo_pulse_probe] saved {OUT}")
    return 0


def selftest():
    """Offline synthetic guards. Leg 1 (T11 canon): flat 2.0% baseline, one
    50% squeeze on a long-holiday eve inside the month-end window -> must
    flag pulse with all three calendar faces, flat tail day must NOT flag.
    Leg 2 (T11-EXT): two synthetic members sharing dates -- anchor pulses
    on the squeeze day, other member stays flat -> co-pulse 0, transmission
    z faces distinguishable (on-day z high for a second squeeze member)."""
    base = [2.0 + 0.01 * (i % 5) for i in range(BASE_WIN + 8)]
    df = pd.DataFrame({
        "date": pd.date_range("2025-01-02", periods=len(base), freq="D"),
        "close": base,
    })
    # carve a month-end + long-holiday-eve squeeze day (index BASE_WIN+2)
    d = df["date"].iloc[BASE_WIN + 2]
    df.loc[df.index[BASE_WIN + 2], "date"] = d.replace(day=30)
    df.loc[df.index[BASE_WIN + 2], "close"] = 50.0
    # next bar jumps 5 calendar days ahead -> pre_long_holiday for squeeze day
    df.loc[df.index[BASE_WIN + 3], "date"] = (
        df["date"].iloc[BASE_WIN + 2] + pd.Timedelta(days=5))
    df = df.sort_values("date").reset_index(drop=True)
    a = annotate(df)
    sq = a[(a["close"] == 50.0)].iloc[0]
    assert bool(sq["pulse"]) and bool(sq["pulse_abs_t1"]) \
        and bool(sq["pulse_abs_t2"]), "squeeze day must flag pulse tiers"
    assert bool(sq["z"] >= Z_PULSE), "squeeze day robust z must pass line"
    assert bool(sq["month_end_win"]), "day-28 must be in month-end window"
    assert bool(sq["pre_long_holiday"]), "5-day gap must flag long-holiday eve"
    flat = a[(a["close"] < 3.0) & (a["close"] > 1.0)]
    assert not bool(flat["pulse"].any()), "flat days must not flag"
    assert len(measure(a)["top10_by_close"]) >= 1, "top table must list squeeze"
    # --- leg 2: ladder join on shared dates ---
    m2 = df.copy()
    m2["close"] = 2.0 + 0.01 * (m2.index % 3)   # flat twin, same calendar
    a2 = annotate(m2)
    gc_days = set(a.loc[a["pulse"], "date"].dt.strftime("%Y-%m-%d"))
    on2 = a2["date"].dt.strftime("%Y-%m-%d").isin(gc_days)
    assert int((on2 & a2["pulse"]).sum()) == 0, "flat twin must not co-pulse"
    assert int(on2.sum()) == 1, "join must share exactly the squeeze day"
    # second squeeze member pulsing the same day -> co-pulse counted
    m3 = df[["date", "close"]].copy()
    m3.loc[m3.index[BASE_WIN + 2], "close"] = 30.0
    a3 = annotate(m3)
    on3 = a3["date"].dt.strftime("%Y-%m-%d").isin(gc_days)
    assert bool(a3.loc[on3, "pulse"].all()), "twin squeeze must co-pulse"
    print("[repo_pulse_probe] selftest PASS "
          "(pulse tiers + calendar faces + flat-reject + ladder join)")
    return 0


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    cmd = argv[0] if argv else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        try:
            return run()
        except (OSError, RuntimeError, ValueError) as e:
            print(f"[repo_pulse_probe] FAIL: {e}")
            return 2
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
