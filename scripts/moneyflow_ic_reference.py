"""Does the order-flow panel know anything about the next five days?

The moneyflow collector has been landing per-stock main-force net inflow since
2026-05-14 (122 bars) and the LHB institution panel holds 58,815 rows.  Neither has ever
been priced: `results/watermark_red.json` has named "moneyflow/LHB IC reference batch" as
the next P2 candidate for weeks, and the only reason it never ran was the moneyflow panel
being source-blocked.  The panel is fresh now, so this face is the reference batch that
answers the question -- criteria frozen before the numbers, one run, no parameter search.

Reuse, not a second implementation: the cross-sectional IC is
`shortline_p1_ic._ic_series_fast` (rank-after-pairing spearman), the same function the
alpha191 / p1c / a158 batches use.

Nothing here promotes a factor.  ADMIT means "this panel carries information the book
does not already have", which buys a candidate row, not a sleeve.

    python scripts/moneyflow_ic_reference.py run [--limit N]
    python scripts/moneyflow_ic_reference.py selftest
"""
import glob
import io
import json
import os
import sys
from importlib import import_module

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

MF_DIR = os.path.join(ROOT, "data", "moneyflow", "per")
PX_DIR = os.path.join(ROOT, "data", "astock_daily", "per")
LHB = os.path.join(ROOT, "data", "lhb_inst", "lhb_inst.parquet")
OUT = os.path.join(ROOT, "results", "moneyflow_ic_reference.json")
FACTOR_IC = os.path.join(ROOT, "results", "factor_ic.json")

H = 5                      # forward horizon in trading days, the repo's IC convention
SMOOTH = 5                 # factor smoothing window (a single day's net inflow is noise)
MF_COLS = {
    "mf5": ("主力净流入-净占比", 1),      # main-force net inflow share, 5-day mean
    "xl5": ("超大单净流入-净占比", 1),    # extra-large order share, 5-day mean
    "sm5": ("小单净流入-净占比", 1),      # retail share, 5-day mean (expected sign: -)
    "mf1": ("主力净流入-净占比", 0),      # the daily reading, as the trivial reference
}

# Frozen before any IC was computed.  A factor is admitted only if all four hold; the
# thresholds are the ones BACKTEST_PLAN / D6 already use for a first-pass reference batch.
CRITERIA = {
    "C1_abs_ic_mean": 0.02,
    "C2_abs_t": 2.0,
    "C3_half_split_same_sign": True,
    "C4_max_abs_corr_vs_mom20": 0.70,
    "min_days": 60,
    "min_names_per_day": 200,
    "lhb_min_events": 300,
    "lhb_abs_t": 2.0,
}


# --------------------------------------------------------------------------- reading
def _mf_calendar(limit=0):
    files = sorted(glob.glob(os.path.join(MF_DIR, "*.csv")))
    if limit:
        files = files[:limit]
    first = pd.read_csv(files[0], usecols=["date"])
    cal = pd.to_datetime(first["date"])
    print("moneyflow files %d, calendar %s..%s (%d bars)"
          % (len(files), cal.min().date(), cal.max().date(), len(cal)), flush=True)
    return files, pd.DatetimeIndex(cal)


def build_panels(limit=0):
    """factor panels (dict name -> DataFrame dates x symbols) and forward returns."""
    files, cal = _mf_calendar(limit)
    fac = {k: {} for k in MF_COLS}
    px, cl = {}, {}
    missing_px = 0
    for i, f in enumerate(files):
        sym = os.path.basename(f)[:-4]
        try:
            d = pd.read_csv(f, usecols=["date"] + sorted({c for c, _ in MF_COLS.values()}))
        except Exception:
            continue
        d["date"] = pd.to_datetime(d["date"])
        d = d.set_index("date").reindex(cal)
        for name, (col, smooth) in MF_COLS.items():
            s = pd.to_numeric(d[col], errors="coerce")
            if smooth:
                s = s.rolling(SMOOTH, min_periods=SMOOTH).mean()
            fac[name][sym] = s
        p = os.path.join(PX_DIR, sym + ".csv")
        if not os.path.exists(p):
            missing_px += 1
            continue
        c = pd.read_csv(p, usecols=["date", "close"])
        c["date"] = pd.to_datetime(c["date"])
        s = pd.to_numeric(c.set_index("date")["close"], errors="coerce").dropna()
        s = s[~s.index.duplicated()].sort_index()
        if len(s) < H + 10:
            missing_px += 1
            continue
        fr = s.shift(-H) / s - 1.0
        px[sym] = fr.reindex(cal)
        cl[sym] = s.reindex(cal)
        if (i + 1) % 1000 == 0:
            print("  loaded %d/%d" % (i + 1, len(files)), flush=True)
    syms = sorted(px)
    panels = {k: pd.DataFrame(v).reindex(columns=syms) for k, v in fac.items()}
    fwd = pd.DataFrame(px).reindex(columns=syms)
    close = pd.DataFrame(cl).reindex(columns=syms)
    print("panel %d dates x %d symbols (no price file: %d)"
          % (fwd.shape[0], fwd.shape[1], missing_px), flush=True)
    return panels, fwd, close


def mom20(close):
    """A 20-day momentum panel off the same close series, for the D6 correlation gate."""
    return close / close.shift(20) - 1.0


# --------------------------------------------------------------------------- stats
def ic_readings(factor, fwd, min_names=CRITERIA["min_names_per_day"]):
    from shortline_p1_ic import _ic_series_fast
    mask_n = (factor.notna() & fwd.notna()).sum(axis=1)
    f = factor.where(mask_n >= min_names, np.nan)
    ic = _ic_series_fast(f, fwd)
    if len(ic) < 10:
        return None
    mean, std = float(ic.mean()), float(ic.std(ddof=1))
    ir = mean / std if std > 0 else 0.0
    halves = [ic.iloc[: len(ic) // 2], ic.iloc[len(ic) // 2:]]
    return {
        "ic_mean": round(mean, 5),
        "ic_std": round(std, 5),
        "ic_ir": round(ir, 4),
        "t_stat": round(ir * np.sqrt(len(ic)), 3),
        "ic_pos_pct": round(float((ic > 0).mean()), 4),
        "n_days": int(len(ic)),
        "names_per_day_median": int(mask_n[mask_n >= min_names].median()),
        "half_ic_mean": [round(float(h.mean()), 5) for h in halves],
        "first_day": str(ic.index[0].date()),
        "last_day": str(ic.index[-1].date()),
    }


def corr_vs(panel, other):
    """Mean daily cross-sectional rank correlation with another panel."""
    mask = panel.notna() & other.notna()
    a = panel.where(mask).rank(axis=1)
    b = other.where(mask).rank(axis=1)
    a = a.sub(a.mean(axis=1), axis=0)
    b = b.sub(b.mean(axis=1), axis=0)
    num = (a * b).sum(axis=1)
    den = np.sqrt((a ** 2).sum(axis=1) * (b ** 2).sum(axis=1))
    c = (num / den).where(den > 0).dropna()
    return None if c.empty else round(float(c.mean()), 4)


def verdict_of(rd, corr, criteria=CRITERIA):
    """Derived, never typed: each gate is recomputed off the readings."""
    if not rd or rd["n_days"] < criteria["min_days"]:
        return "REJECT", {"C1": False, "C2": False, "C3": False, "C4": False,
                          "why": "too few usable days"}
    c1 = abs(rd["ic_mean"]) >= criteria["C1_abs_ic_mean"]
    c2 = abs(rd["t_stat"]) >= criteria["C2_abs_t"]
    h = rd["half_ic_mean"]
    c3 = bool(h[0] * h[1] > 0) and bool(min(abs(h[0]), abs(h[1])) > 0)
    c4 = corr is not None and abs(corr) < criteria["C4_max_abs_corr_vs_mom20"]
    gates = {"C1": bool(c1), "C2": bool(c2), "C3": bool(c3), "C4": bool(c4)}
    return ("ADMIT" if all(gates.values()) else "REJECT"), gates


# --------------------------------------------------------------------------- LHB
def lhb_reading(fwd, criteria=CRITERIA):
    """Institution net-buy share on the day it appears on LHB -> next-5-day excess.

    Excess is measured against that day's cross-sectional median forward return, so the
    number answers "better than a random name that day", not "up in an up market".
    """
    if not os.path.exists(LHB):
        return None
    d = pd.read_parquet(LHB, columns=["代码", "机构净买额占总成交额比", "上榜日期"])
    d["date"] = pd.to_datetime(d["上榜日期"].astype(str))
    d["sym"] = d["代码"].astype(str).str.zfill(6)
    d["share"] = pd.to_numeric(d["机构净买额占总成交额比"], errors="coerce")
    d = d.dropna(subset=["share", "date"])
    d = d[d["sym"].isin(fwd.columns)]
    d = d[d["date"].isin(fwd.index)]
    if d.empty:
        return None
    exc = fwd.sub(fwd.median(axis=1), axis=0)
    d["fwd"] = [exc.at[r.date, r.sym] if (r.date in exc.index and r.sym in exc.columns)
                else np.nan for r in d.itertuples()]
    d = d.dropna(subset=["fwd"])
    if len(d) < 30:
        return None
    top = d[d["share"] >= d["share"].quantile(0.8)]
    bot = d[d["share"] <= d["share"].quantile(0.2)]

    def blk(x, label):
        n = len(x)
        m = float(x["fwd"].mean())
        s = float(x["fwd"].std(ddof=1)) if n > 2 else 0.0
        t = m / (s / np.sqrt(n)) if s > 0 else 0.0
        return {"label": label, "n": int(n), "mean_excess_pct": round(m * 100, 4),
                "t_stat": round(t, 3)}

    return {"events": int(len(d)), "window": [str(d["date"].min().date()),
                                              str(d["date"].max().date())],
            "top_quintile": blk(top, "institutions bought (top 20% share)"),
            "bottom_quintile": blk(bot, "institutions sold (bottom 20% share)"),
            "spread_pct": round(float(top["fwd"].mean() - bot["fwd"].mean()) * 100, 4)}


def lhb_verdict(r, criteria=CRITERIA):
    if not r or r["events"] < criteria["lhb_min_events"]:
        return "REJECT", {"why": "too few events in the price window"}
    t = abs(r["top_quintile"]["t_stat"])
    ok = t >= criteria["lhb_abs_t"] and np.sign(r["spread_pct"]) == np.sign(
        r["top_quintile"]["mean_excess_pct"])
    return ("ADMIT" if ok else "REJECT"), {"C1_abs_t": bool(t >= criteria["lhb_abs_t"]),
                                           "C2_spread_sign": bool(
                                               np.sign(r["spread_pct"]) == np.sign(
                                                   r["top_quintile"]["mean_excess_pct"]))}


# --------------------------------------------------------------------------- run
def run(limit=0, write=True):
    import time
    t0 = time.time()
    panels, fwd, close = build_panels(limit)
    m20 = mom20(close)

    out = {}
    admitted = []
    for name, p in panels.items():
        rd = ic_readings(p, fwd)
        corr = corr_vs(p, m20)
        v, gates = verdict_of(rd, corr)
        out[name] = {"readings": rd, "corr_vs_mom20": corr, "gates": gates, "verdict": v}
        if v == "ADMIT":
            admitted.append(name)
        print("  %-4s IC %s t %s corr20 %s -> %s"
              % (name, rd and rd["ic_mean"], rd and rd["t_stat"], corr, v), flush=True)

    lhb = lhb_reading(fwd)
    lv, lg = lhb_verdict(lhb)
    print("  lhb  spread %s t %s -> %s"
          % (lhb and lhb["spread_pct"], lhb and lhb["top_quintile"]["t_stat"], lv), flush=True)
    if lv == "ADMIT":
        admitted.append("lhb_inst_top20")

    payload = {
        "face": "moneyflow_ic_reference",
        "asof": pd.Timestamp.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": str(fwd.index[-1].date()),
        "question": "the order-flow and LHB panels have been collected for months and "
                    "never priced -- do they know anything about the next %d days?" % H,
        "window": {"start": str(fwd.index[0].date()), "end": str(fwd.index[-1].date()),
                   "bars": int(len(fwd)), "symbols": int(fwd.shape[1])},
        "criteria_frozen": CRITERIA,
        "horizon_days": H,
        "factors": out,
        "lhb": {"readings": lhb, "gates": lg, "verdict": lv},
        "admitted": admitted,
        "verdict": "ADMIT" if admitted else "REJECT",
        "honest": [
            "the moneyflow panel starts 2026-05-14 (122 bars): this is a half-year "
            "reference batch, not a full-history verdict; the sign can still be a "
            "2026-regime artefact",
            "forward returns are the same close-to-close %d-day convention as factor_ic "
            "(no open-to-open, no cost) -- this is an information test, not a tradable "
            "return" % H,
            "net inflow share is the vendor's own order-size classification, not exchange "
            "tape; it is re-published values, so revisions are visible only on re-pull",
            "LHB events are priced against that day's cross-sectional median forward "
            "return; large-cap tilts inside the event set are not neutralised",
            "no parameter search: one smoothing window (5), one horizon (5), four named "
            "factors. A grid here would manufacture the answer",
        ],
        "elapsed_sec": round(time.time() - t0, 2),
    }
    if write:
        with io.open(OUT, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=1)
        print(json.dumps({"verdict": payload["verdict"], "admitted": admitted,
                          "elapsed_sec": payload["elapsed_sec"]}, ensure_ascii=False),
              flush=True)
    return payload


# --------------------------------------------------------------------------- selftest
def selftest():
    ok = []

    def chk(cond, msg):
        ok.append((bool(cond), msg))
        print(("PASS " if cond else "FAIL ") + msg)

    rng = np.random.default_rng(7)
    idx = pd.bdate_range("2024-01-01", periods=120)
    cols = ["A%03d" % i for i in range(260)]
    f = pd.DataFrame(rng.normal(size=(120, 260)), index=idx, columns=cols)
    fwd = f * 0.01 + pd.DataFrame(rng.normal(scale=0.002, size=(120, 260)), index=idx,
                                  columns=cols)
    rd = ic_readings(f, fwd, min_names=50)
    chk(rd["ic_mean"] > 0.5, "L1 a factor that is its own forward return reads IC ~ +1")
    rd2 = ic_readings(f, -fwd, min_names=50)
    chk(rd2["ic_mean"] < -0.5, "L2 the same factor against a negated return reads IC ~ -1")
    chk(ic_readings(f.iloc[:, :3], fwd.iloc[:, :3], min_names=50) is None,
        "L3 fewer names than the floor is not an IC")
    flat = pd.DataFrame(0.0, index=idx, columns=cols)
    chk(ic_readings(flat, fwd, min_names=50) is None, "L4 a zero-variance factor is NaN")

    v, g = verdict_of({"ic_mean": 0.03, "t_stat": 3.0, "n_days": 100,
                       "half_ic_mean": [0.02, 0.04]}, 0.1)
    chk(v == "ADMIT", "L5 four gates all true -> ADMIT")
    v, g = verdict_of({"ic_mean": 0.03, "t_stat": 3.0, "n_days": 100,
                       "half_ic_mean": [0.02, -0.01]}, 0.1)
    chk(v == "REJECT" and not g["C3"], "L6 halves disagree -> C3 fails, REJECT")
    v, g = verdict_of({"ic_mean": 0.03, "t_stat": 3.0, "n_days": 100,
                       "half_ic_mean": [0.02, 0.04]}, 0.9)
    chk(v == "REJECT" and not g["C4"], "L7 a factor that is 20-day momentum is refused")
    v, g = verdict_of({"ic_mean": 0.005, "t_stat": 1.0, "n_days": 100,
                       "half_ic_mean": [0.004, 0.006]}, 0.1)
    chk(v == "REJECT" and not g["C1"], "L8 a small IC is refused even when consistent")

    a = pd.DataFrame(rng.normal(size=(30, 40)), index=pd.bdate_range("2024-01-01", periods=30),
                     columns=["B%02d" % i for i in range(40)])
    chk(abs(float(corr_vs(a, a)) - 1.0) < 1e-9, "L9 a panel correlates 1.0 with itself")
    chk(abs(float(corr_vs(a, -a)) + 1.0) < 1e-9, "L10 a negated panel correlates -1.0")

    # forward returns must look forward: a series that only rises gives a positive fwd
    s = pd.Series(np.arange(1.0, 31.0), index=pd.bdate_range("2024-01-01", periods=30))
    fr = s.shift(-H) / s - 1.0
    chk(bool(fr.dropna().gt(0).all()) and np.isnan(fr.iloc[-1]),
        "L11 the forward return uses tomorrow, never today (last H bars are NaN)")

    bad = [m for c, m in ok if not c]
    print("%d/%d" % (len(ok) - len(bad), len(ok)))
    return 0 if not bad else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    limit = 0
    if "--limit" in argv:
        limit = int(argv[argv.index("--limit") + 1])
    run(limit=limit)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
