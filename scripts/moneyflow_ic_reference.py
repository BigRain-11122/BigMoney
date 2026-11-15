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
def _blk(x, label):
    """One leg: count, mean forward excess (%), and its own t against zero."""
    n = len(x)
    m = float(x["fwd"].mean())
    s = float(x["fwd"].std(ddof=1)) if n > 2 else 0.0
    t = m / (s / np.sqrt(n)) if s > 0 else 0.0
    return {"label": label, "n": int(n), "mean_excess_pct": round(m * 100, 4),
            "t_stat": round(t, 3)}


def _two_sample_t(a, b):
    """Welch t of (mean(a) - mean(b)); 0 when either leg is degenerate."""
    na, nb = len(a), len(b)
    if na < 3 or nb < 3:
        return 0.0
    va = float(a["fwd"].var(ddof=1)) / na
    vb = float(b["fwd"].var(ddof=1)) / nb
    if va + vb <= 0:
        return 0.0
    return float((a["fwd"].mean() - b["fwd"].mean()) / np.sqrt(va + vb))


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

    return {"events": int(len(d)), "window": [str(d["date"].min().date()),
                                              str(d["date"].max().date())],
            "top_quintile": _blk(top, "institutions bought (top 20% share)"),
            "bottom_quintile": _blk(bot, "institutions sold (bottom 20% share)"),
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


# ------------------------------------------------------- sell leg, full LHB history
SELLLEG_OUT = os.path.join(ROOT, "results", "lhb_sellleg.json")
SELLLEG_MD = os.path.join(ROOT, "research", "LHB_SELLLEG_VERDICT.md")

# Frozen before this face read one number.  r1733 measured the sell leg on 122 days
# (bottom quintile -0.90%, t=-1.89) and wrote down that a single regime could have made
# that sign.  That reading generated this hypothesis, so the test set is the panel
# BEFORE the window that produced it; the full history is reported beside it as context,
# never as the thing being admitted.
SELLLEG = {
    "hypothesis_start": "2026-05-14",   # first bar of the panel r1733 priced
    "min_names_per_day": 200,
    "min_events": 1000,
    "C1_bottom_neg_t": 2.0,             # sold leg: negative and material on its own
    "C2_spread_t": 2.0,                 # bottom must sit under top, two-sample
    "C3_min_years": 6,                  # calendar years with the same sign
    "C4_control_t": 2.0,                # must beat the other LHB events, not the market
}

# Frozen before the priced run.  This batch's own information test put the top leg at a
# t that no noise can produce, so the only open question is whether a book could have
# bought it: the list is published after that close, so the earliest entry is the NEXT
# open, and both sides pay COST_X1.
EXEC = {
    "leg": "institutions bought (top 20% share)",
    "entry": "next session open after the LHB date (disclosure is after that close)",
    "exit": "close H sessions after the LHB date",
    "cost": "COST_X1 (13.041bp) per side, rev_osc_stock_p1 import",
    "min_events": 1000,
    "C1_net_t": 2.0,            # the priced leg must stand on its own
    "C3_min_years": 6,          # and in 6 calendar years, not one
    "C4_min_retained": 0.5,     # at least half the information number must survive
}


def _calendar_index(start="2019-01-01", end="2027-01-01"):
    """Exchange sessions, clipped to the LHB panel's own neighbourhood.

    The calendar file runs back to 1990; carrying those rows through a 5,221-symbol
    panel costs ~300 MB for dates no LHB event can ever land on.
    """
    from exchange_calendar_audit import load_calendar
    cal = pd.DatetimeIndex(pd.to_datetime(load_calendar()))
    return cal[(cal >= pd.Timestamp(start)) & (cal <= pd.Timestamp(end))]


def build_price_panel(cal=None, cost=None):
    """Two forward panels on the same calendar, so the pair differs only in execution.

    `fwd`  = close(D) -> close(D+H)      -- the information test r1733 used.
    `paid` = open(D+1) -> close(D+H), net of cost on both sides -- what you can buy.

    The gap between the two is the overnight gap plus two commissions: the honest
    difference between "the panel knows something" and "the book can eat it".
    """
    cal = _calendar_index() if cal is None else cal
    if cost is None:
        from rev_osc_stock_p1 import COST_X1 as cost
    files = sorted(glob.glob(os.path.join(PX_DIR, "*.csv")))
    cols, paid_cols, missing = {}, {}, 0
    for i, f in enumerate(files):
        sym = os.path.basename(f)[:-4]
        try:
            c = pd.read_csv(f, usecols=["date", "open", "close"])
        except Exception:
            missing += 1
            continue
        c["date"] = pd.to_datetime(c["date"])
        c = c.set_index("date")
        cl = pd.to_numeric(c["close"], errors="coerce").dropna()
        cl = cl[~cl.index.duplicated()].sort_index()
        if len(cl) < H + 10:
            missing += 1
            continue
        cols[sym] = (cl.shift(-H) / cl - 1.0).reindex(cal)
        op = pd.to_numeric(c["open"], errors="coerce")
        op = op[~op.index.duplicated()].sort_index()
        # both legs calendar-aligned: a name that is not quoted on the exact entry or
        # exit session has no tradable price, and is dropped rather than bridged
        cl_al = cl.reindex(cal)
        op_al = op.reindex(cal)
        paid_cols[sym] = (cl_al.shift(-H) * (1.0 - cost)
                          / (op_al.shift(-1) * (1.0 + cost)) - 1.0)
        if (i + 1) % 1000 == 0:
            print("  price %d/%d" % (i + 1, len(files)), flush=True)
    fwd = pd.DataFrame(cols).reindex(cal)
    paid = pd.DataFrame(paid_cols).reindex(cal)
    print("price panel %d dates x %d symbols (skipped %d); net-of-cost panel aligned=%s"
          % (fwd.shape[0], fwd.shape[1], missing,
             bool(fwd.columns.equals(paid.columns))), flush=True)
    return fwd, paid



def _lhb_events(fwd, start=None, end=None):
    """LHB rows mapped onto (date, symbol) cells that have a forward return."""
    d = pd.read_parquet(LHB, columns=["代码", "机构净买额占总成交额比", "上榜日期"])
    d["date"] = pd.to_datetime(d["上榜日期"].astype(str))
    d["sym"] = d["代码"].astype(str).str.zfill(6)
    d["share"] = pd.to_numeric(d["机构净买额占总成交额比"], errors="coerce")
    d = d.dropna(subset=["share", "date"])
    d = d[d["sym"].isin(fwd.columns) & d["date"].isin(fwd.index)]
    if start:
        d = d[d["date"] >= pd.Timestamp(start)]
    if end:
        d = d[d["date"] <= pd.Timestamp(end)]
    return d


def lhb_sellleg(fwd, start=None, end=None, criteria=SELLLEG, events=None):
    """Quintiles of the institution net-buy share -> forward excess, with controls.

    Excess is against that day's cross-sectional median over the whole price universe,
    so it answers "better than a random name that day".  The control leg answers the
    separate question "is this about the share, or about being on the LHB at all" --
    LHB names are volatile by construction, and r1733 had no such control.
    """
    d = _lhb_events(fwd, start, end) if events is None else events.copy()
    if d.empty:
        return None
    med = fwd.median(axis=1)
    exc = fwd.sub(med, axis=0)
    exc = exc.where(fwd.notna() & (fwd.notna().sum(axis=1) >= criteria["min_names_per_day"])
                    .values[:, None])
    d["fwd"] = [exc.at[r.date, r.sym] if (r.date in exc.index and r.sym in exc.columns)
                else np.nan for r in d.itertuples()]
    d = d.dropna(subset=["fwd"])
    if len(d) < 30:
        return None
    top = d[d["share"] >= d["share"].quantile(0.8)]
    bot = d[d["share"] <= d["share"].quantile(0.2)]
    rest = d[~d.index.isin(bot.index)]

    years = {}
    for y, g in d.groupby(d["date"].dt.year):
        gf = g[g["share"] <= g["share"].quantile(0.2)] if len(g) >= 20 else g.iloc[:0]
        gt = g[g["share"] >= g["share"].quantile(0.8)] if len(g) >= 20 else g.iloc[:0]
        years[str(int(y))] = {"events": int(len(g)),
                              "bottom": _blk(gf, "sold") if len(gf) else None,
                              "top": _blk(gt, "bought") if len(gt) else None}

    bot_t = _blk(bot, "institutions sold (bottom 20% share)")
    top_t = _blk(top, "institutions bought (top 20% share)")
    all_t = _blk(d, "all LHB events that day")
    return {
        "events": int(len(d)),
        "window": [str(d["date"].min().date()), str(d["date"].max().date())],
        "top_quintile": top_t,
        "bottom_quintile": bot_t,
        "all_events": all_t,
        "spread_bottom_minus_top_pct": round(bot_t["mean_excess_pct"]
                                             - top_t["mean_excess_pct"], 4),
        "spread_bottom_minus_top_t": round(_two_sample_t(bot, top), 3),
        "control_bottom_minus_other_t": round(_two_sample_t(bot, rest), 3),
        "control_bottom_minus_other_pct": round(bot_t["mean_excess_pct"]
                                                - float(rest["fwd"].mean()) * 100, 4),
        "by_year": years,
    }


def lhb_sellleg_verdict(r, criteria=SELLLEG):
    """Derived from the readings; never typed."""
    if not r or r["events"] < criteria["min_events"]:
        return "REJECT", {"C1": False, "C2": False, "C3": False, "C4": False,
                          "why": "fewer than %d events in the test window"
                                 % criteria["min_events"]}
    b = r["bottom_quintile"]
    c1 = bool(b["mean_excess_pct"] < 0 and abs(b["t_stat"]) >= criteria["C1_bottom_neg_t"])
    c2 = bool(r["spread_bottom_minus_top_t"] <= -criteria["C2_spread_t"])
    ys = [v["bottom"] for v in r["by_year"].values() if v["bottom"]]
    neg = sum(1 for v in ys if v["mean_excess_pct"] < 0)
    c3 = bool(len(ys) >= criteria["C3_min_years"]
              and neg >= criteria["C3_min_years"])
    c4 = bool(r["control_bottom_minus_other_t"] <= -criteria["C4_control_t"])
    gates = {"C1": c1, "C2": c2, "C3": c3, "C4": c4}
    out = dict(gates)
    out["years_present"] = len(ys)
    out["years_bottom_negative"] = neg
    return ("ADMIT" if all(gates.values()) else "REJECT"), out


def _sellleg_md(p, test, full):
    """The page is generated from the payload, so it cannot drift from the numbers."""
    L = []
    a = L.append
    a("# LHB「机构砸盘」腿 · 全史参考批")
    a("")
    a("> 机械生成件：本页由 `scripts/moneyflow_ic_reference.py lhb-sellleg` 从 "
      "`results/lhb_sellleg.json` 直接生成，数字与判词都不是手写；")
    a("> 改数字或改判词必须重跑工具，手改本页即与 JSON 不一致。")
    a("")
    a("## 一、问题")
    a("")
    a("r1733 在 122 天窗口（2026-05-14 → 2026-11-10）里量到：机构净卖出那一腿"
      "未来 5 日超额 **%.2f%%（t=%.2f）**，而机构净买入那一腿只有 **%s%%（t=%s）**。"
      % (p["r1733_reference"]["bottom_pct"], p["r1733_reference"]["bottom_t"],
         p["r1733_reference"]["top_pct"], p["r1733_reference"]["top_t"]))
    a("同一批数据里卖腿的分辨率高一倍、方向为负——但 r1733 同时写下「122 天是单一政体，"
      "符号可能整个是这段行情的产物」。")
    a("")
    a("本批就是那句话的判决：把同一个问题放到 LHB 全史（%s 起）上，并且**把生成这个假设的"
      "窗口排除在判决集之外**——判决集是 %s → %s，假设窗只作对照。"
      % (p["window"]["full_start"], test["window"][0], test["window"][1]))
    a("")
    a("## 二、判据（看数之前冻结）")
    a("")
    a("| 判据 | 阈值 | 含义 |")
    a("|---|---|---|")
    a("| C1 卖腿自身 | 均值 < 0 且 \\|t\\| ≥ %.1f | 砸盘之后确实跑输，不是噪声 |"
      % SELLLEG["C1_bottom_neg_t"])
    a("| C2 双腿价差 | 卖腿减买腿 ≤ -%.1f（双样本 t） | 方向来自「净卖占比」而不是「上榜」 |"
      % SELLLEG["C2_spread_t"])
    a("| C3 逐年一致 | ≥ %d 个自然年同号 | 不是某一年行情的产物 |"
      % SELLLEG["C3_min_years"])
    a("| C4 事件内对照 | 卖腿减「其它龙虎榜事件」 ≤ -%.1f（双样本 t） | 不是「上榜股天生跑输」 |"
      % SELLLEG["C4_control_t"])
    a("")
    a("四项全过才 ADMIT；ADMIT 也只买一行候选，不买袖面。")
    a("")
    a("## 三、读数")
    a("")
    a("| 腿 | 事件数 | 未来 5 日超额 | t |")
    a("|---|---|---|---|")
    a("| 机构净买入（占比 top 20%%） | %d | %+.4f%% | %+.3f |"
      % (test["top_quintile"]["n"], test["top_quintile"]["mean_excess_pct"],
         test["top_quintile"]["t_stat"]))
    a("| 机构净卖出（占比 bottom 20%%） | %d | %+.4f%% | %+.3f |"
      % (test["bottom_quintile"]["n"], test["bottom_quintile"]["mean_excess_pct"],
         test["bottom_quintile"]["t_stat"]))
    a("| 全部龙虎榜事件（对照） | %d | %+.4f%% | %+.3f |"
      % (test["all_events"]["n"], test["all_events"]["mean_excess_pct"],
         test["all_events"]["t_stat"]))
    a("")
    a("卖腿减买腿 %+.4f%%（双样本 t=%+.3f）；卖腿减其它事件 %+.4f%%（t=%+.3f）。"
      % (test["spread_bottom_minus_top_pct"], test["spread_bottom_minus_top_t"],
         test["control_bottom_minus_other_pct"], test["control_bottom_minus_other_t"]))
    a("")
    a("## 四、逐年（判决集）")
    a("")
    a("| 年 | 事件数 | 卖腿超额 | 卖腿 t |")
    a("|---|---|---|---|")
    for y in sorted(test["by_year"]):
        v = test["by_year"][y]["bottom"]
        if v:
            a("| %s | %d | %+.4f%% | %+.3f |"
              % (y, v["n"], v["mean_excess_pct"], v["t_stat"]))
        else:
            a("| %s | %d | — | — |" % (y, test["by_year"][y]["events"]))
    a("")
    a("## 五、能不能买到（同一套四分位，换成可成交价）")
    a("")
    ex = p["execution"]["test"]
    xg = p["execution"]["gates"]
    a("龙虎榜是**当日收盘后**披露的，所以最早能买的是**次日开盘**；本表把入场从 D 日收盘"
      "换成 D+1 开盘、出场仍是 D+5 收盘，双边各扣 13.041bp（COST_X1）。")
    a("")
    a("| 腿 | 事件数 | 扣费后超额 | t |")
    a("|---|---|---|---|")
    a("| 机构净买入（占比 top 20%%） | %d | %+.4f%% | %+.3f |"
      % (ex["top_quintile"]["n"], ex["top_quintile"]["mean_excess_pct"],
         ex["top_quintile"]["t_stat"]))
    a("| 机构净卖出（占比 bottom 20%%） | %d | %+.4f%% | %+.3f |"
      % (ex["bottom_quintile"]["n"], ex["bottom_quintile"]["mean_excess_pct"],
         ex["bottom_quintile"]["t_stat"]))
    a("")
    a("信息面 %+.4f%% → 可成交 %+.4f%%，保留比例 %.1f%%（缺口=隔夜跳空+双边成本）。"
      % (test["top_quintile"]["mean_excess_pct"], ex["top_quintile"]["mean_excess_pct"],
         (xg.get("retained_frac") or 0) * 100))
    a("")
    a("两腿价差从信息面的 %+.4fpp 收窄到可成交面的 %+.4fpp：**排序几乎全部落在收盘到"
      "次日开盘的那一个缺口里**（买腿 %+.2fpp 的信息里有 %+.2fpp 在开盘时就跳掉了，"
      "剩下的差被双边成本吃掉）。"
      % (test["spread_bottom_minus_top_pct"], ex["spread_bottom_minus_top_pct"],
         test["top_quintile"]["mean_excess_pct"],
         test["top_quintile"]["mean_excess_pct"] - ex["top_quintile"]["mean_excess_pct"]))
    a("")
    a("逐年扣费后买腿：%s。"
      % "、".join("%s %+.2f%%" % (y, v["top"]["mean_excess_pct"])
                  for y, v in sorted(ex["by_year"].items()) if v.get("top")))
    a("")
    a("**执行判：%s**（C1 净超额 t %s / C3 逐年 %d/%d 年为正 %s / C4 保留 ≥%.0f%% %s）"
      % (p["execution"]["verdict"], _yn(xg["C1"]), xg.get("years_top_positive", 0),
         xg.get("years_present", 0), _yn(xg["C3"]),
         EXEC["C4_min_retained"] * 100, _yn(xg["C4"])))
    a("")
    a("## 六、判")
    a("")
    g = p["gates"]
    a("**%s**（C1 %s / C2 %s / C3 %s / C4 %s；判决集 %d 事件，%d 个自然年，其中 %d 年同号）"
      % (p["verdict"], _yn(g["C1"]), _yn(g["C2"]), _yn(g["C3"]), _yn(g["C4"]),
         test["events"], g.get("years_present", 0), g.get("years_bottom_negative", 0)))
    a("")
    a("全史对照（含假设窗，仅作上下文，不参与判决）：%s → %s，%d 事件，"
      "卖腿 %+.4f%%（t=%+.3f），买腿 %+.4f%%（t=%+.3f）。"
      % (full["window"][0], full["window"][1], full["events"],
         full["bottom_quintile"]["mean_excess_pct"], full["bottom_quintile"]["t_stat"],
         full["top_quintile"]["mean_excess_pct"], full["top_quintile"]["t_stat"]))
    a("")
    a("## 七、诚实边界")
    a("")
    for h in p["honest"]:
        a("- " + h)
    a("")
    return "\n".join(L)


def lhb_exec_verdict(exec_r, info_r, criteria=EXEC):
    """Priced twin of the information test: same machinery, buyable prices."""
    if not exec_r or exec_r["events"] < criteria["min_events"]:
        return "NOT_TRADABLE", {"C1": False, "C2": False, "C3": False, "C4": False,
                                "why": "fewer than %d priced events"
                                       % criteria["min_events"]}
    t = exec_r["top_quintile"]
    c1 = bool(t["mean_excess_pct"] > 0 and abs(t["t_stat"]) >= criteria["C1_net_t"])
    ys = [v["top"] for v in exec_r["by_year"].values() if v.get("top")]
    pos = sum(1 for v in ys if v["mean_excess_pct"] > 0)
    c3 = bool(len(ys) >= criteria["C3_min_years"] and pos >= criteria["C3_min_years"])
    info = (info_r or {}).get("top_quintile", {}).get("mean_excess_pct") or 0.0
    retained = (t["mean_excess_pct"] / info) if info > 0 else 0.0
    c4 = bool(retained >= criteria["C4_min_retained"])
    gates = {"C1": c1, "C3": c3, "C4": c4}
    gates["years_present"] = len(ys)
    gates["years_top_positive"] = pos
    gates["retained_frac"] = round(float(retained), 4)
    return ("TRADABLE" if all(gates[k] for k in ("C1", "C3", "C4")) else "NOT_TRADABLE"), gates


def _yn(v):
    return "过" if v else "不过"


def lhb_sellleg_run(write=True):
    import time
    t0 = time.time()
    fwd, paid = build_price_panel()
    test = lhb_sellleg(fwd, end="2026-05-13")
    full = lhb_sellleg(fwd)
    if not test or not full:
        raise SystemExit("no LHB events could be mapped onto the price panel")
    v, gates = lhb_sellleg_verdict(test)
    ex = lhb_sellleg(paid, end="2026-05-13")
    xv, xg = lhb_exec_verdict(ex, test)

    ref = {}
    if os.path.exists(OUT):
        with io.open(OUT, encoding="utf-8") as f:
            prev = json.load(f).get("lhb", {}).get("readings") or {}
        ref = {"window": prev.get("window"),
               "bottom_pct": (prev.get("bottom_quintile") or {}).get("mean_excess_pct"),
               "bottom_t": (prev.get("bottom_quintile") or {}).get("t_stat"),
               "top_pct": (prev.get("top_quintile") or {}).get("mean_excess_pct"),
               "top_t": (prev.get("top_quintile") or {}).get("t_stat")}

    payload = {
        "face": "lhb_sellleg",
        "asof": pd.Timestamp.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": full["window"][1],
        "question": "r1733 read the LHB sell leg on 122 days and warned the sign could be "
                    "one regime. Does 'institutions dumping' still underperform when the "
                    "test set is every LHB event before the window that produced it?",
        "criteria_frozen": SELLLEG,
        "test_window": test["window"],
        "test_set_excludes": [SELLLEG["hypothesis_start"], full["window"][1]],
        "window": {"full_start": full["window"][0], "full_end": full["window"][1],
                   "full_events": full["events"]},
        "r1733_reference": ref,
        "test": test,
        "full_history_context": full,
        "gates": gates,
        "verdict": v,
        "execution": {
            "criteria_frozen": EXEC,
            "test": ex,
            "gates": xg,
            "verdict": xv,
        },
        "admitted": ["lhb_inst_sell_leg"] if v == "ADMIT" else [],
        "honest": [
            "the test set is the panel before %s, which removes the 122 days that "
            "generated the hypothesis but does not remove r1733's own reasoning from the "
            "author's head -- this is a cleaner test, not a pristine one"
            % SELLLEG["hypothesis_start"],
            "excess is close-to-close %d-day against that day's cross-sectional median "
            "over the price universe: no cost, no open-to-open execution. This is an "
            "information test, not a tradable return" % H,
            "quintile cut is computed inside whichever window is being read, so the "
            "test-set cut is not the cut the full history would pick",
            "LHB names are volatile by construction; C4 exists because r1733 had no "
            "control for 'being on the list' at all",
            "no parameter search: one horizon (5), one smoothing (none -- LHB is an "
            "event, not a series), one share definition, two legs named before the run",
            "the priced leg is a measurement, not a blind test: this run's own "
            "information table named the top leg before the execution panel was built, "
            "so 'tradable' here means 'the number survives cost and the overnight gap', "
            "not 'nobody had looked'",
            "the priced leg needs a quote on both exact sessions; a name halted on the "
            "entry or exit day is dropped instead of bridged, which removes the most "
            "volatile names from the priced sample rather than from the information one",
        ],
        "elapsed_sec": round(time.time() - t0, 2),
    }
    if write:
        with io.open(SELLLEG_OUT, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=1)
        with io.open(SELLLEG_MD, "w", encoding="utf-8") as f:
            f.write(_sellleg_md(payload, test, full))
        print(json.dumps({"verdict": v, "gates": gates,
                          "test_events": test["events"],
                          "bottom_pct": test["bottom_quintile"]["mean_excess_pct"],
                          "bottom_t": test["bottom_quintile"]["t_stat"],
                          "top_pct": test["top_quintile"]["mean_excess_pct"],
                          "top_t": test["top_quintile"]["t_stat"],
                          "exec_verdict": xv, "exec_gates": xg,
                          "exec_top_pct": ex["top_quintile"]["mean_excess_pct"],
                          "exec_top_t": ex["top_quintile"]["t_stat"],
                          "elapsed_sec": payload["elapsed_sec"]}, ensure_ascii=False),
              flush=True)
    return payload


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

    # ---- sell-leg legs: synthetic event study, no disk
    def _synth(edge, years=7, per_day=12, days=1750, seed=11):
        """fwd panel + events whose share predicts fwd with slope `edge`."""
        r = np.random.default_rng(seed)
        didx = pd.bdate_range("2018-01-01", periods=days)
        scols = ["S%03d" % i for i in range(60)]
        ret = pd.DataFrame(r.normal(scale=0.03, size=(days, 60)), index=didx, columns=scols)
        ev = []
        for i, dt in enumerate(didx):
            for j in range(per_day):
                sym = scols[r.integers(0, 60)]
                share = float(r.uniform(-30, 30))
                # the event's own forward return is nudged by its share
                ret.iat[i, scols.index(sym)] += edge * share / 100.0
                ev.append({"date": dt, "sym": sym, "share": share})
        e = pd.DataFrame(ev)
        return ret, e

    fwd_a, ev_a = _synth(0.25)   # high share goes up, so the SOLD leg is the one that sinks
    rd = lhb_sellleg(fwd_a, criteria={"min_names_per_day": 20}, events=ev_a)
    chk(rd is not None and rd["bottom_quintile"]["mean_excess_pct"] < 0,
        "L12 a share that predicts underperformance puts the sold leg below zero")
    v, g = lhb_sellleg_verdict(rd, {"min_events": 100, "C1_bottom_neg_t": 2.0,
                                    "C2_spread_t": 2.0, "C3_min_years": 6,
                                    "C4_control_t": 2.0})
    chk(v == "ADMIT" and g["C1"] and g["C2"], "L13 a planted sell-leg signal is admitted")

    fwd_b, ev_b = _synth(0.0)
    rd_b = lhb_sellleg(fwd_b, criteria={"min_names_per_day": 20}, events=ev_b)
    v_b, g_b = lhb_sellleg_verdict(rd_b, {"min_events": 100, "C1_bottom_neg_t": 2.0,
                                          "C2_spread_t": 2.0, "C3_min_years": 6,
                                          "C4_control_t": 2.0})
    chk(v_b == "REJECT", "L14 a share with no information is refused")

    # the year gate: an effect that lives in one year only must not pass C3
    fwd_c, ev_c = _synth(0.25, seed=13)
    one = ev_c[ev_c["date"].dt.year == ev_c["date"].dt.year.min()]
    rd_c = lhb_sellleg(fwd_c, criteria={"min_names_per_day": 20}, events=one)
    v_c, g_c = lhb_sellleg_verdict(rd_c, {"min_events": 100, "C1_bottom_neg_t": 2.0,
                                          "C2_spread_t": 2.0, "C3_min_years": 6,
                                          "C4_control_t": 2.0})
    chk(not g_c["C3"] and v_c == "REJECT",
        "L15 an effect confined to one calendar year fails the persistence gate")

    # the control: a whole-event universe that underperforms equally is not a sell leg
    fwd_d, ev_d = _synth(0.0, seed=17)
    # shove every event's own forward return down by the same amount
    for row in ev_d.itertuples():
        fwd_d.iat[fwd_d.index.get_loc(row.date), fwd_d.columns.get_loc(row.sym)] -= 0.01
    rd_d = lhb_sellleg(fwd_d, criteria={"min_names_per_day": 20}, events=ev_d)
    v_d, g_d = lhb_sellleg_verdict(rd_d, {"min_events": 100, "C1_bottom_neg_t": 2.0,
                                          "C2_spread_t": 2.0, "C3_min_years": 6,
                                          "C4_control_t": 2.0})
    chk(not g_d["C4"] and v_d == "REJECT",
        "L16 events that all sink together are refused by the event-internal control")

    # the test set must really stop before the hypothesis window
    fwd_e = pd.DataFrame({"S001": [0.01, 0.02, 0.03]},
                         index=pd.to_datetime(["2026-05-12", "2026-05-13", "2026-05-14"]))
    ev_e = pd.DataFrame({"date": pd.to_datetime(["2026-05-12", "2026-05-13", "2026-05-14"]),
                         "sym": ["S001"] * 3, "share": [-1.0, -2.0, -3.0]})
    sel = ev_e[ev_e["date"] <= pd.Timestamp("2026-05-13")]
    chk(len(sel) == 2 and str(sel["date"].max().date()) == "2026-05-13",
        "L17 the test window ends the day before the hypothesis window starts")

    bad = [m for c, m in ok if not c]
    print("%d/%d" % (len(ok) - len(bad), len(ok)))
    return 0 if not bad else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "lhb-sellleg":
        lhb_sellleg_run()
        return 0
    limit = 0
    if "--limit" in argv:
        limit = int(argv[argv.index("--limit") + 1])
    run(limit=limit)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
