"""build_premium_panel.py -- T-16 ARB-1 deliverable-3: core48 ETF premium panel.

Pure-LOCAL panel builder, ZERO network (close=data/daily, NAV=fund_premium/nav,
dividends=fund_premium/dividends backfilled by update_fund_premium.py
backfill-dividends). Ticket T-2026-09-24-16 item 3; ARBITRAGE_PLAYBOOK sec.3.

Convention frozen here (data layer only -- factor spec belongs to P-A1 prereg):
  - As-of join, NO look-ahead: for close date T, nav_asof(T) = last NAV with
    nav_date < T (STRICT). Domestic funds carry NAV(T-1) published evening
    T-1 (known at close T); QDII members carry NAV(T-2) published on T-1
    (r52 finding, 513100) -- the strict join handles both conservatively and
    never uses NAV published after close of T.
  - premium_raw = close/nav_asof - 1.
  - Ex-div guard (playbook: premium series must be ex-div adjusted): on an
    ex-div date the exchange close drops by the distribution while nav_asof is
    still pre-ex-div -> one-day artificial negative spike. Adjusted series
    premium_adj = (close + div_per_unit)/nav_asof - 1 on ex-div dates,
    = premium_raw otherwise. Only the ex-div date itself is polluted under
    the T-1 convention (nav catches up next day). Dividend amounts diffed from
    the sina CUMULATIVE column; first-ever row = the event itself.
  - T-19 consolidation dates (share conversions): DISCLOSURE-ONLY columns
    cons_flag/cons_ratio -- empirically the NAV face restates at the same
    boundary so premium_raw is already unit-consistent (159928 evidence);
    multiply-back would corrupt (+300%). Div records coinciding with a cons
    date are skipped (cons mislabeled as dividend in the dividend face).
  - nav_lag_td = trading-day count in [nav_date, T) from the shared calendar
    (weekly NAV publications in early history -> honest large lag, disclosed).
  - premium_z = cross-sectional z of premium_adj across members valid on the
    date (ddof=0; <2 valid members -> NaN). premium_chg_5d = premium_adj
    minus its value 5 trading days earlier (same fund; window -> NaN).
  - Guard coverage: funds whose dividend file is absent get ex_div_flag=0
    everywhere and guard_coverage=0.0 in the summary (honest, never guessed).

Gates (zero-network, build computes them): members == core48 count, panel
span >= MIN_SPAN_TD trading days, premium non-NaN rate >= MIN_NONNULL,
per-fund rows >= MIN_FUND_ROWS. Verdict in summary; exit 0 ok / 2 gate fail.

Storage: data/fund_premium/panel/panel.csv (gitignored, regenerable) +
tracked summary results/shortline/fund_premium_panel.json (evidence_cutoff
top-level = last close date; ledger_trials_added=0: data engineering, zero
engine runs).

selftest: offline fixtures, every constant derived from the synthetic data
(J18 self-consistency law).
"""
from __future__ import annotations

import datetime as dt
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "fund_premium")
NAV_DIR = os.path.join(DATA_DIR, "nav")
DIV_DIR = os.path.join(DATA_DIR, "dividends")
PANEL_DIR = os.path.join(DATA_DIR, "panel")
DAILY_DIR = os.path.join(ROOT, "data", "daily")
SUMMARY_PATH = os.path.join(ROOT, "results", "shortline", "fund_premium_panel.json")

MIN_SPAN_TD = 1200       # ~5y of trading days; pool close history 2020-01.. == ~1740
MIN_NONNULL = 0.99       # premium non-NaN rate across panel rows
MIN_FUND_ROWS = 250      # ~1 trading year, NAV_ROW_FLOOR parity

PANEL_COLS = ["date", "code", "close", "nav", "nav_date", "nav_lag_td",
              "premium_raw", "ex_div_flag", "div_per_unit", "cons_flag",
              "cons_ratio", "premium_adj", "premium_z", "premium_chg_5d"]


# ------------------------------------------------------------------ loaders (pure)
def _core48_codes(daily_dir=DAILY_DIR) -> list:
    if not os.path.isdir(daily_dir):
        return []
    return sorted(f[:-4] for f in os.listdir(daily_dir)
                  if f.endswith(".csv") and f[:-4].isdigit())


def _load_close(code: str, daily_dir=DAILY_DIR):
    """sina close CSV -> list[(date, close)] ascending; date str validated."""
    p = os.path.join(daily_dir, f"{code}.csv")
    out = []
    with open(p, encoding="utf-8-sig") as f:
        hdr = f.readline()
        if "close" not in hdr:
            return out
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 5:
                continue
            d = parts[0]
            if len(d) != 10:
                continue
            try:
                c = float(parts[4])
            except ValueError:
                continue
            if c > 0:
                out.append((d, c))
    return out


def _load_nav(code: str, nav_dir=NAV_DIR):
    """NAV CSV -> list[(date, nav)] ascending."""
    p = os.path.join(nav_dir, f"{code}.csv")
    if not os.path.exists(p):
        return []
    out = []
    with open(p, encoding="utf-8-sig") as f:
        f.readline()
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 2:
                continue
            try:
                v = float(parts[1])
            except ValueError:
                continue
            if v > 0:
                out.append((parts[0], v))
    return out


def _load_dividends(code: str, div_dir=DIV_DIR):
    """dividends CSV -> dict{ex_date: per_event_div}；文件缺失=守卫缺面（诚实 0 覆盖）。
    列语义（r53 live probe 实证）：sina 面第二列=累计分红 -> per-event=逐行差分；
    **首行=基金首次派息事件本身**（累计值=单事件精确值）-> per-event(首)=cum(首)。
    注意：份额折算可能被分红面记作「分红」事件（159928 实证：2021-06-25 cum 0.9
    与折算日重合，0.9/1.26=71% 非现金派息）-> build_member 在 cons 日跳过加回。
    legacy 'div_per_unit' 列头（已迁移，防御兼容）= 每份派息直读。"""
    p = os.path.join(div_dir, f"{code}.csv")
    if not os.path.exists(p):
        return None
    rows, cumulative = [], False
    with open(p, encoding="utf-8-sig") as f:
        hdr = f.readline().strip()
        if "cum_div" in hdr:
            cumulative = True
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 2 or len(parts[0]) != 10:
                continue
            try:
                rows.append((parts[0], float(parts[1])))
            except ValueError:
                continue
    out = {}
    if not cumulative:
        for d, v in rows:
            out[d] = v
        return out
    prev = None
    for d, v in rows:
        out[d] = (v - prev) if prev is not None else v
        prev = v
    return out


CONS_REGISTRY_PATH = os.path.join(ROOT, "data", "consolidation", "registry.json")


def load_consolidations(path=CONS_REGISTRY_PATH):
    """T-19 折算登记册 -> {sym: {date: ratio}}。缺失=空 dict（面板不依赖，缺册=0 旗诚实）。
    份额折算日：close 按新单位报价、nav_asof 仍为旧单位 -> premium 面同型污染，
    乘回 ratio（implied_ratio_approx，登记册近似值如实沿用）。"""
    try:
        with open(path, encoding="utf-8-sig") as f:
            reg = json.load(f)
    except Exception:
        return {}
    out = {}
    for e in reg.get("events", []):
        sym, date = str(e.get("sym", "")), str(e.get("date", ""))
        ratio = e.get("implied_ratio_approx")
        if sym and len(date) == 10 and ratio:
            out.setdefault(sym, {})[date] = float(ratio)
    return out


def load_calendar(daily_dir=DAILY_DIR) -> list:
    """共享交易日历（update_fund_premium._load_trading_dates 同构）。"""
    cands = [os.path.join(daily_dir, "510300.csv")] + \
        sorted(glob.glob(os.path.join(daily_dir, "*.csv")))
    for p in cands:
        try:
            dates = set()
            with open(p, encoding="utf-8-sig") as f:
                for i, line in enumerate(f):
                    if i == 0:
                        continue
                    d = line.split(",")[0].strip()
                    if len(d) == 10 and d[4] == "-" and d[7] == "-":
                        dates.add(d)
            if dates:
                return sorted(dates)
        except Exception:
            continue
    return []


# ------------------------------------------------------------------ core join (pure)
def asof_nav(close_date: str, nav_rows: list, lo: int = 0):
    """strict as-of：最后一个 nav_date < close_date 的 NAV。返回 (date, nav, next_idx)
    或 (None, None, next_idx)。nav_rows 升序；next_idx=下次搜索起点（单调复用）。
    NAV(T) 同日永不用（无未来数据）；nav_date == close_date 也排除（未发布守卫）。
    指针耗尽（lo==len，selftest S3 抓出的尾段丢弃 bug）：末行 NAV 仍是有效候选，
    只要其日期严格早于 close_date——否则 QDII（NAV 止点早于 close 尾段）整段尾丢失。"""
    if lo >= len(nav_rows):
        if nav_rows and nav_rows[-1][0] < close_date:
            return nav_rows[-1][0], nav_rows[-1][1], lo
        return None, None, lo
    best, nxt = None, lo
    for i in range(lo, len(nav_rows)):
        nd, nv = nav_rows[i]
        if nd < close_date:
            best = (nd, nv)
            nxt = i + 1
        else:
            nxt = i
            break
    else:
        nxt = len(nav_rows)
    if best is None:
        return None, None, nxt
    return best[0], best[1], nxt


def trading_lag(nav_date: str, close_date: str, cal_index: dict) -> int:
    """[nav_date, close_date) 内交易日数（日历内双端索引差；端点不在日历=0 诚实）。"""
    a, b = cal_index.get(nav_date), cal_index.get(close_date)
    if a is None or b is None:
        return 0
    return b - a


def build_member(code: str, cal: list, cal_index: dict,
                 daily_dir=DAILY_DIR, nav_dir=NAV_DIR, div_dir=DIV_DIR,
                 cons=None):
    """单成员面板行构建。返回 (rows, stats) -- rows=list[dict] 升序。"""
    close_rows = _load_close(code, daily_dir)
    nav_rows = _load_nav(code, nav_dir)
    divs = _load_dividends(code, div_dir)
    cons_map = (cons or {}).get(code, {})
    guard_coverage = 1.0 if divs is not None else 0.0
    rows = []
    lo = 0
    for d, c in close_rows:
        nd, nv, lo = asof_nav(d, nav_rows, lo)
        if nv is None:
            continue
        prem = c / nv - 1.0
        flag, dpu = 0, None
        if divs and d in divs:
            flag, dpu = 1, divs[d]
        cflag, ratio = 0, None
        if d in cons_map:
            cflag, ratio = 1, cons_map[d]
        # 污染日修正（r53 实证定案）：
        # (a) 普通除息日：价格跌派息额、NAV 不跌 -> 加回 dpu（510300 2026-01-19
        #     raw -2.56% -> adj -0.03% 复原实证）。
        # (b) 折算日（T-19 登记）：**premium 面单位本就一致**（NAV 面与价格面同边界
        #     同步重述，159928 2021-06-25 raw +2.15% 健康），乘回 ratio 会毁数据
        #     (+300%) -> 折算=纯披露列；当日分红记录多为折算误记 -> 跳过加回防双计。
        if flag and not cflag:
            prem_adj = (c + dpu) / nv - 1.0
        else:
            prem_adj = prem
        rows.append({
            "date": d, "code": code, "close": c, "nav": nv, "nav_date": nd,
            "nav_lag_td": trading_lag(nd, d, cal_index),
            "premium_raw": prem, "ex_div_flag": flag, "div_per_unit": dpu,
            "cons_flag": cflag, "cons_ratio": ratio,
            "premium_adj": prem_adj,
        })
    n = len(rows)
    stats = {
        "rows": n,
        "close_first": close_rows[0][0] if close_rows else None,
        "panel_first": rows[0]["date"] if rows else None,
        "panel_last": rows[-1]["date"] if rows else None,
        "nav_first": nav_rows[0][0] if nav_rows else None,
        "nav_last": nav_rows[-1][0] if nav_rows else None,
        "median_lag_td": None, "max_lag_td": 0,
        "ex_div_count": sum(r["ex_div_flag"] for r in rows),
        "ex_div_on_cons_skipped": sum(1 for r in rows
                                      if r["ex_div_flag"] and r["cons_flag"]),
        "cons_count": sum(r["cons_flag"] for r in rows),
        "median_premium": None, "p95_abs_premium": None,
        "guard_coverage": guard_coverage,
    }
    if n:
        lags = sorted(r["nav_lag_td"] for r in rows)
        stats["median_lag_td"] = lags[n // 2]
        stats["max_lag_td"] = lags[-1]
        prems = sorted(abs(r["premium_adj"]) for r in rows
                       if r["premium_adj"] == r["premium_adj"])
        if prems:
            stats["median_premium"] = prems[len(prems) // 2]
            stats["p95_abs_premium"] = prems[int(0.95 * (len(prems) - 1))]
    return rows, stats


# ------------------------------------------------------------------ cross-sectional layers (pure)
def add_premium_z(rows_by_date: dict):
    """逐日横截面 z（premium_adj，ddof=0）；<2 有效成员=NaN。"""
    import math
    for d, members in rows_by_date.items():
        vals = [r["premium_adj"] for r in members if r["premium_adj"] == r["premium_adj"]]
        for r in members:
            r["premium_z"] = None
        if len(vals) < 2:
            continue
        mu = sum(vals) / len(vals)
        var = sum((v - mu) ** 2 for v in vals) / len(vals)
        sd = math.sqrt(var)
        for r in members:
            if sd > 0 and r["premium_adj"] == r["premium_adj"]:
                r["premium_z"] = (r["premium_adj"] - mu) / sd
            elif sd == 0:
                r["premium_z"] = 0.0 if r["premium_adj"] == mu else None


def add_premium_chg(rows: list, window: int = 5):
    """同基金 premium_adj 与 window 交易日前值之差；窗未满=NaN。rows 升序单成员。"""
    for i, r in enumerate(rows):
        r["premium_chg_5d"] = None
        if i >= window and rows[i - window]["premium_adj"] == rows[i - window]["premium_adj"] \
                and r["premium_adj"] == r["premium_adj"]:
            r["premium_chg_5d"] = r["premium_adj"] - rows[i - window]["premium_adj"]


# ------------------------------------------------------------------ gates + build
def panel_gates(codes: list, all_rows: list, per_fund: dict, cal: list) -> list:
    problems = []
    nav_have = [c for c in codes if os.path.exists(os.path.join(NAV_DIR, f"{c}.csv"))]
    if len(nav_have) < len(codes):
        problems.append(f"NAV files {len(nav_have)}/{len(codes)} -- run backfill-nav first")
    if len(cal) < MIN_SPAN_TD:
        problems.append(f"calendar span {len(cal)} < {MIN_SPAN_TD}")
    short = [c for c, s in per_fund.items() if s["rows"] < MIN_FUND_ROWS]
    if short:
        problems.append(f"{len(short)} funds below MIN_FUND_ROWS ({short[:5]}...)")
    n = len(all_rows)
    nn = sum(1 for r in all_rows if r["premium_adj"] == r["premium_adj"])
    if n and nn / n < MIN_NONNULL:
        problems.append(f"premium non-null {nn / n:.4f} < {MIN_NONNULL}")
    return problems


def cmd_build() -> int:
    import pandas as pd
    codes = _core48_codes()
    if not codes:
        print("no core48 codes (data/daily empty) -> honest exit 2")
        return 2
    cal = load_calendar()
    cal_index = {d: i for i, d in enumerate(cal)}
    cons = load_consolidations()
    all_rows, per_fund = [], {}
    for c in codes:
        rows, stats = build_member(c, cal, cal_index, cons=cons)
        add_premium_chg(rows)
        all_rows.extend(rows)
        per_fund[c] = stats
    if not all_rows:
        print("empty panel (no close x NAV overlap) -> honest exit 2")
        return 2
    by_date = {}
    for r in all_rows:
        by_date.setdefault(r["date"], []).append(r)
    add_premium_z(by_date)
    all_rows.sort(key=lambda r: (r["date"], r["code"]))

    os.makedirs(PANEL_DIR, exist_ok=True)
    out_path = os.path.join(PANEL_DIR, "panel.csv")
    tmp = out_path + ".tmp"
    df = pd.DataFrame(all_rows)[PANEL_COLS]
    df.to_csv(tmp, index=False, encoding="utf-8")
    os.replace(tmp, out_path)

    problems = panel_gates(codes, all_rows, per_fund, cal)
    dates = sorted(r["date"] for r in all_rows)
    # r52 QDII T-2 finding -> build-time availability disclosure: NAV 日期序列
    # 不含发布时间戳，无法从数据面证明 T-1 NAV 在 T 收盘前已发布；对尾端
    # freshness gap>0 的成员（QDII 嫌疑）如实点名，P-A1 prereg 冻结可用性口径。
    last_td = cal[-1] if cal else None
    qdii_suspects = []
    for c, s in per_fund.items():
        gap = None
        if last_td and s.get("nav_last"):
            i_nav, i_last = cal_index.get(s["nav_last"]), cal_index.get(last_td)
            gap = (i_last - i_nav) if (i_nav is not None and i_last is not None) else None
        s["nav_freshness_gap_td"] = gap
        if gap:
            qdii_suspects.append({"code": c, "gap_td": gap, "nav_last": s["nav_last"]})
    lag_med = sorted(s["median_lag_td"] for s in per_fund.values() if s["median_lag_td"] is not None)
    summary = {
        "built_at": dt.datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": dates[-1],
        "panel_path": "data/fund_premium/panel/panel.csv",
        "members": len(codes),
        "rows": len(all_rows),
        "span": {"first": dates[0], "last": dates[-1], "td_count": len(set(dates))},
        "lag_td": {"median_of_medians": lag_med[len(lag_med) // 2] if lag_med else None,
                   "max_of_max": max((s["max_lag_td"] for s in per_fund.values()), default=0)},
        "ex_div_events_total": sum(s["ex_div_count"] for s in per_fund.values()),
        "ex_div_on_cons_skipped": sum(s["ex_div_on_cons_skipped"] for s in per_fund.values()),
        "cons_events_total": sum(s["cons_count"] for s in per_fund.values()),
        "cons_registry_loaded": bool(cons),
        "guard_coverage_funds": sum(1 for s in per_fund.values() if s["guard_coverage"] > 0),
        "nav_freshness": {"calendar_last_td": last_td,
                          "gap_gt0_funds": qdii_suspects},
        "per_fund": per_fund,
        "gates": {"problems": problems,
                  "verdict": "PASS" if not problems else "FAIL"},
        "ledger_trials_added": 0,
        "note": "data-layer panel: as-of strict join (nav_date < close_date); ex-div guard = "
                "per-event dividend diffed from sina CUMULATIVE column (first-ever row = the "
                "event itself) added back to close; T-19 consolidation dates = DISCLOSURE-ONLY "
                "(empirical: NAV face restates in sync at the boundary so premium face is "
                "unit-consistent, 159928 raw +2.15% evidence; multiply-back would corrupt); "
                "div records coinciding with cons dates skipped (cons mislabeled as dividend); "
                "premium_z cross-sectional ddof=0; NAV series has no publication timestamps -> "
                "nav_freshness.gap_gt0_funds discloses build-time availability lags (QDII "
                "suspects, r52 finding); availability convention frozen at P-A1 prereg",
    }
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    tmp = SUMMARY_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    os.replace(tmp, SUMMARY_PATH)

    top_lag = sorted(per_fund.items(), key=lambda kv: -(kv[1]["max_lag_td"] or 0))[:3]
    qdii_like = [f"{c}(med {s['median_lag_td']})" for c, s in per_fund.items()
                if (s["median_lag_td"] or 0) >= 2]
    print(f"panel: {len(all_rows)} rows x {len(codes)} members, span {dates[0]}..{dates[-1]} "
          f"({len(set(dates))} td), ex_div events {summary['ex_div_events_total']}, "
          f"guard-covered funds {summary['guard_coverage_funds']}/{len(codes)}")
    print(f"lag: median-of-medians {summary['lag_td']['median_of_medians']} td, "
          f"max {summary['lag_td']['max_of_max']} td; lag>=2 funds: {qdii_like[:6]}")
    print(f"gates: {'PASS' if not problems else 'FAIL'}")
    for p in problems:
        print(f"  - {p}")
    return 0 if not problems else 2


# ------------------------------------------------------------------ selftest (offline, J18 law)
def selftest() -> int:
    fails = []

    def chk(name, cond):
        print(("PASS " if cond else "FAIL ") + name)
        if not cond:
            fails.append(name)

    import tempfile

    with tempfile.TemporaryDirectory() as td:
        daily = os.path.join(td, "daily"); os.makedirs(daily)
        nav = os.path.join(td, "nav"); os.makedirs(nav)
        divs = os.path.join(td, "dividends"); os.makedirs(divs)

        # fixture: calendar 2026-01-02..01-13 (8 td), fund A domestic lag-1,
        # fund B QDII-like (NAV stops two days earlier -> lag grows to 3)
        cal = ["2026-01-02", "2026-01-05", "2026-01-06", "2026-01-07",
               "2026-01-08", "2026-01-09", "2026-01-12", "2026-01-13"]
        with open(os.path.join(daily, "100001.csv"), "w", encoding="utf-8") as f:
            f.write("date,open,high,low,close,volume,amount\n")
            for d in cal:
                f.write(f"{d},1,1,1,2.0,100,100\n")     # close 2.0 flat
        with open(os.path.join(daily, "100002.csv"), "w", encoding="utf-8") as f:
            f.write("date,open,high,low,quantity,close\n")  # wrong header -> honest empty
        # fund A NAV: lag-1 chain at 1.0 -> premium_raw = 2.0/1.0 - 1 = 1.0
        with open(os.path.join(nav, "100001.csv"), "w", encoding="utf-8") as f:
            f.write("date,nav,acc_nav\n")
            for d in cal[:-1]:                            # NAV through 01-08 only
                f.write(f"{d},1.0,1.0\n")
        # fund B (QDII-like): NAV stops at 01-07 -> on 01-09 lag = 2 td
        with open(os.path.join(daily, "100003.csv"), "w", encoding="utf-8") as f:
            f.write("date,open,high,low,close,volume,amount\n")
            for d in cal:
                f.write(f"{d},1,1,1,2.0,100,100\n")
        with open(os.path.join(nav, "100003.csv"), "w", encoding="utf-8") as f:
            f.write("date,nav,acc_nav\n")
            for d in cal[:-2]:                            # NAV through 01-07
                f.write(f"{d},1.0,1.0\n")
        # dividends for 100001: CUMULATIVE face semantics (r53 live probe:
        # sina col = 累计分红). baseline 2019-12-31 cum 0.3 (outside panel span),
        # 01-06 cum 0.5 -> per-event 0.2; 01-12 cum 0.62 -> per-event 0.12
        with open(os.path.join(divs, "100001.csv"), "w", encoding="utf-8") as f:
            f.write("ex_date,cum_div\n2019-12-31,0.3\n2026-01-06,0.5\n2026-01-12,0.62\n")
        # fund D: single cumulative row -> per-event unknown -> NaN (S8)
        with open(os.path.join(daily, "100004.csv"), "w", encoding="utf-8") as f:
            f.write("date,open,high,low,close,volume,amount\n")
            for d in cal:
                f.write(f"{d},1,1,1,2.0,100,100\n")
        with open(os.path.join(nav, "100004.csv"), "w", encoding="utf-8") as f:
            f.write("date,nav,acc_nav\n2026-01-02,1.0,1.0\n2026-01-05,1.0,1.0\n")
        with open(os.path.join(divs, "100004.csv"), "w", encoding="utf-8") as f:
            f.write("ex_date,cum_div\n2026-01-07,0.9\n")

        g_cal = load_calendar(daily)
        chk("calendar from daily dir", g_cal == cal)
        gi = {d: i for i, d in enumerate(g_cal)}

        # S1 strict as-of: no same-day NAV, no future NAV
        rows_a, st_a = build_member("100001", g_cal, gi, daily, nav, divs)
        chk("S1 rows_a count 7 (first close date has no prior NAV -> dropped)",
            len(rows_a) == 7)
        chk("S1 first row uses nav 01-02 on 01-05 (strict <)",
            rows_a[0]["date"] == "2026-01-05" and rows_a[0]["nav_date"] == "2026-01-02")
        chk("S1 last row lag 1 (nav 01-12 < close 01-13)",
            rows_a[-1]["nav_date"] == "2026-01-12" and rows_a[-1]["nav_lag_td"] == 1)
        # S2 ex-div add-back: 01-06 close 2.0, per-event div 0.2 (cum diff), nav 1.0
        ex_row = next(r for r in rows_a if r["date"] == "2026-01-06")
        chk("S2 ex_div_flag set with diffed amount",
            ex_row["ex_div_flag"] == 1 and abs(ex_row["div_per_unit"] - 0.2) < 1e-12)
        chk("S2 premium_adj = (2.0+0.2)/1.0-1 = 1.2",
            abs(ex_row["premium_adj"] - 1.2) < 1e-12)
        chk("S2 premium_raw unadjusted = 1.0", abs(ex_row["premium_raw"] - 1.0) < 1e-12)
        normal = next(r for r in rows_a if r["date"] == "2026-01-07")
        chk("S2 non-event adj==raw", normal["premium_adj"] == normal["premium_raw"]
            and normal["ex_div_flag"] == 0 and normal["cons_flag"] == 0)
        chk("S2 stats ex_div_count 2 & guard 1.0",
            st_a["ex_div_count"] == 2 and st_a["guard_coverage"] == 1.0)

        # S9 consolidation = DISCLOSURE-ONLY: 01-08 cons ratio 2.0 -> adj == raw
        # (NAV face restates in sync; multiply-back would corrupt, 159928 law);
        # 01-06 ex-div + cons overlap -> div add-back skipped (cons mislabel guard)
        cons_fixture = {"100001": {"2026-01-06": 2.0, "2026-01-08": 1.5}}
        rows_a9, st_a9 = build_member("100001", g_cal, gi, daily, nav, divs,
                                      cons=cons_fixture)
        cons_row = next(r for r in rows_a9 if r["date"] == "2026-01-08")
        chk("S9 cons-only date: disclosure flag, adj==raw",
            cons_row["cons_flag"] == 1 and abs(cons_row["cons_ratio"] - 1.5) < 1e-12
            and cons_row["premium_adj"] == cons_row["premium_raw"])
        both_row = next(r for r in rows_a9 if r["date"] == "2026-01-06")
        chk("S9 ex-div x cons overlap: add-back skipped, adj==raw",
            both_row["ex_div_flag"] == 1 and both_row["cons_flag"] == 1
            and both_row["premium_adj"] == both_row["premium_raw"]
            and abs(both_row["premium_raw"] - 1.0) < 1e-12)
        chk("S9 stats: cons_count 2, skipped 1", st_a9["cons_count"] == 2
            and st_a9["ex_div_on_cons_skipped"] == 1)

        # S3 QDII-like lag: fund B on 01-13 -> nav 01-09, lag = idx(01-13)-idx(01-09) = 2
        rows_b, st_b = build_member("100003", g_cal, gi, daily, nav, divs)
        chk("S3 qdii-like lag 2 on last row (nav 01-09 < close 01-13)",
            rows_b[-1]["nav_date"] == "2026-01-09" and rows_b[-1]["nav_lag_td"] == 2)
        chk("S3 missing dividend file -> guard 0.0", st_b["guard_coverage"] == 0.0)
        chk("S3 no ex_div flags without guard", sum(r["ex_div_flag"] for r in rows_b) == 0)

        # S8 first-ever cumulative row = the event itself: fund D 01-07 cum 0.9
        # -> per-event 0.9 -> adj = (2.0+0.9)/1.0-1 = 1.9
        rows_d, st_d = build_member("100004", g_cal, gi, daily, nav, divs)
        d_ex = next(r for r in rows_d if r["date"] == "2026-01-07")
        chk("S8 first-ever row = event itself (per-event 0.9)",
            d_ex["ex_div_flag"] == 1 and abs(d_ex["div_per_unit"] - 0.9) < 1e-12
            and abs(d_ex["premium_adj"] - 1.9) < 1e-12)
        chk("S8 stats ex_div_count 1", st_d["ex_div_count"] == 1)
        d_norm = next(r for r in rows_d if r["date"] == "2026-01-06")
        chk("S8 non-event rows unaffected", d_norm["ex_div_flag"] == 0
            and d_norm["premium_adj"] == d_norm["premium_raw"])

        # S4 premium_chg_5d: first 5 rows NaN, row6 = adj - adj[0]
        add_premium_chg(rows_a)
        chk("S4 chg NaN before window", all(r["premium_chg_5d"] is None for r in rows_a[:5]))
        v6 = rows_a[5]["premium_adj"] - rows_a[0]["premium_adj"]
        chk("S4 chg window math", abs(rows_a[5]["premium_chg_5d"] - v6) < 1e-12)

        # S5 premium_z cross-sectional: 01-09 A prem 1.0 + B prem 1.0 -> sd 0 -> z 0.0
        by_date = {}
        for r in rows_a + rows_b:
            by_date.setdefault(r["date"], []).append(r)
        add_premium_z(by_date)
        z_09 = by_date["2026-01-09"]
        chk("S5 equal values -> sd 0 -> z 0.0", all(r["premium_z"] == 0.0 for r in z_09))
        # 01-06: A adjusted 1.2 vs B raw 1.0 -> mean 1.1 sd 0.1 -> z = +-1.0
        z_06 = by_date["2026-01-06"]
        za = next(r for r in z_06 if r["code"] == "100001")
        zb = next(r for r in z_06 if r["code"] == "100003")
        chk("S5 z divergence after ex-div add-back",
            abs(za["premium_z"] - 1.0) < 1e-12 and abs(zb["premium_z"] + 1.0) < 1e-12)
        # S8b: single member on its date -> z None (<2 valid members)
        by_date_d = {}
        for r in rows_d:
            by_date_d.setdefault(r["date"], []).append(r)
        add_premium_z(by_date_d)
        chk("S8b single-member date -> z None",
            all(r["premium_z"] is None for r in by_date_d["2026-01-07"]))

        # S6 malformed daily header -> honest empty rows, not crash
        rows_x, st_x = build_member("100002", g_cal, gi, daily, nav, divs)
        chk("S6 malformed close file -> 0 rows", len(rows_x) == 0)

        # S7 asof_nav purity: same-day excluded
        nav_rows = [("2026-01-05", 1.1)]
        nd, nv, _ = asof_nav("2026-01-05", nav_rows, 0)
        chk("S7 same-day NAV never used", nd is None and nv is None)
        nd, nv, _ = asof_nav("2026-01-06", nav_rows, 0)
        chk("S7 next-day uses it", nd == "2026-01-05" and abs(nv - 1.1) < 1e-12)

    print(f"selftest: {'ALL PASS' if not fails else 'FAILURES: ' + str(fails)}")
    return 0 if not fails else 1


def main(argv):
    if len(argv) < 2:
        print("usage: build_premium_panel.py build|selftest")
        return 2
    if argv[1] == "build":
        return cmd_build()
    if argv[1] == "selftest":
        return selftest()
    print(f"unknown subcommand: {argv[1]}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
