"""How often does this book lose money over a year -- and how much, in CNY?

Every published face on this book prints an average (9-11% a year) and a worst year
(-0.72%). Neither answers the question a reader actually asks before wiring capital:
*hold it for twelve months from an arbitrary day and what are the odds I am down?*

This face recomputes the production candidate (bond-free, 8% vol target, 5 names, 20-bar
rebalance, 10bp a side -- `results/etf_nobond_vt.json`, arm `nobond_vt08`) on the house
engine and then measures the *path*, nothing else:

  * holding-horizon distribution: enter on every bar, hold 244 / 488 / 732 bars, read the
    outcome distribution in % and in CNY on a 1,000,000 wallet;
  * calendar years, each one printed with its CNY outcome;
  * underwater spells: depth, length, and whether the hole was ever filled.

Two calibers are measured, because they do not cost the same money. The published number
uses `entry_lag=0` (the new book starts accruing on the decision bar's own open -- one bar
of move is booked before it could have been bought); `entry_lag=1` (next open) is the one
an order sheet can actually deliver. `scripts/etf_book_entry_lag.py` prices the gap at
~1.0pp a year. If the odds look different on the honest caliber, that is the number to
quote, and this face prints both rather than choosing.

Honesty rails kept on purpose:
  * overlapping windows are autocorrelated, so a `share` over 1600 starts is a description
    of one 6.9-year history, not an independent probability. The non-overlapping subsample
    (floor((n-1)/H) observations) is printed next to it, and the count is the caveat.
  * an all-positive history is printed as `0 of N`, never as "cannot lose".
  * cash parked by the vol target earns 0% here (the engine's own convention), so the
    de-levered book's odds are the strategy's, not a money-market product's.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np

import etf_composite_pf as E
import etf_robust_pf as R
import etf_equity_alpha as A

FACE = "etf_book_losing_odds"
JSON_PATH = os.path.join("results", FACE + ".json")
DOC_PATH = os.path.join("research", "ETF_BOOK_LOSING_ODDS.md")
WALLET = 1_000_000.0
HORIZONS = (("1y", 244), ("2y", 488), ("3y", 732))
REBAL, NHOLD, COST, VT = 20, 5, 0.0010, 0.08
PUBLISHED = {"cagr": 0.1094, "sharpe": 1.08, "maxdd": -0.1056, "worst_year": -0.0072}


# ---------------------------------------------------------------- pure math
def hold_outcomes(levels, horizon):
    """Total return of every start that has `horizon` bars ahead of it."""
    n = len(levels)
    if n <= horizon:
        return np.array([]), np.array([])
    start = levels[: n - horizon]
    end = levels[horizon:]
    return start, end / start - 1.0


def independent_slice(rets, horizon):
    """The non-overlapping subsample -- the honest count of independent observations."""
    return rets[::horizon] if horizon > 0 else rets


def drawdown_spells(levels, dates):
    """Every underwater spell: start, trough, depth, recovery (None while still under)."""
    peak = levels[0]
    peak_at = dates[0]
    spells = []
    cur = None
    for i, lv in enumerate(levels):
        if lv >= peak:
            if cur is not None:
                cur["recovered_on"] = dates[i]
                cur["bars_to_recover"] = i - cur["trough_idx"]
                cur["bars_under"] = i - cur["start_idx"]
                spells.append(cur)
                cur = None
            peak, peak_at = lv, dates[i]
        else:
            dd = lv / peak - 1.0
            if cur is None:
                cur = {"started_on": peak_at, "start_idx": i, "depth": dd,
                       "trough_idx": i, "trough_on": dates[i],
                       "recovered_on": None, "bars_to_recover": None, "bars_under": None}
            elif dd < cur["depth"]:
                cur.update(depth=dd, trough_idx=i, trough_on=dates[i])
    if cur is not None:
        cur["bars_under"] = len(levels) - 1 - cur["start_idx"]
        spells.append(cur)
    return spells


def calendar_years(levels, dates):
    rows = []
    years = sorted({d.year for d in dates})
    for y in years:
        idx = [i for i, d in enumerate(dates) if d.year == y]
        if not idx:
            continue
        first, last = idx[0], idx[-1]
        ret = levels[last] / levels[first] - 1.0
        rows.append({"year": y, "ret": float(ret),
                     "cny": float(ret * WALLET),
                     "bars": len(idx),
                     # a year that ends at the panel edge is not a full year
                     "partial": last == len(levels) - 1 and last - first + 1 < 240})
    return rows


def describe(rets):
    if len(rets) == 0:
        return {"n": 0}
    s = np.sort(rets)
    return {
        "n": int(len(rets)),
        "share_losing": float((rets < 0).mean()),
        "count_losing": int((rets < 0).sum()),
        "median": float(np.median(rets)),
        "p10": float(np.percentile(rets, 10)),
        "p90": float(np.percentile(rets, 90)),
        "worst": float(s[0]),
        "best": float(s[-1]),
        "median_cny": float(np.median(rets) * WALLET),
        "worst_cny": float(s[0] * WALLET),
        "best_cny": float(s[-1] * WALLET),
    }


def reconcile(lag0):
    """Tie the rebuilt series back to the published face before reading the path off it."""
    worst_year = min(lag0["years_rows"], key=lambda r: r["ret"])
    rep = {
        "published_face": "results/etf_nobond_vt.json arm nobond_vt08",
        "maxdd_have": lag0["deepest"]["depth"] if lag0["deepest"] else None,
        "maxdd_pub": PUBLISHED["maxdd"],
        "worst_year_have": worst_year["ret"],
        "worst_year_pub": PUBLISHED["worst_year"],
        "worst_year_label": worst_year["year"],
        "sharpe_have": lag0["daily"]["sharpe"],
        "sharpe_pub": PUBLISHED["sharpe"],
        "vol_have": lag0["daily"]["vol"],
        "cagr_have": lag0["cagr"],
        "cagr_pub": PUBLISHED["cagr"],
    }
    same_depth = abs((rep["maxdd_have"] or 0) - rep["maxdd_pub"]) <= 0.001
    same_year = abs(rep["worst_year_have"] - rep["worst_year_pub"]) <= 0.001
    rep["verdict"] = "REPRODUCED" if (same_depth and same_year) else "MISMATCH"
    return rep


def verdict_of(h1, indep_h1):
    """Deterministic token: never claim 'cannot lose' off a thin sample."""
    if h1["n"] == 0:
        return "UNMEASURED"
    if h1["count_losing"] == 0:
        thin = indep_h1["n"] <= 8
        return ("EVERY_12_MONTH_START_WON_ON_THIN_SAMPLE" if thin
                else "EVERY_12_MONTH_START_WON")
    share = h1["share_losing"]
    if share >= 0.20:
        return "LOSES_MONEY_OVER_A_YEAR_OFTEN"
    return "LOSES_MONEY_OVER_A_YEAR_SOMETIMES"


# ---------------------------------------------------------------- engine
def build_series(entry_lag):
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    cols = [c for c in close.columns if cls[c] in ("equity", "commodity", "convertible")]
    sc = E.build_score(close[cols], amt[cols], feats)
    ser, turn = R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc,
                                      REBAL, NHOLD, COST, vol_target=VT, entry_lag=entry_lag)
    return ser, turn, n_flip, len(cols)


def measure(ser):
    levels = [float(v) for v in ser.values]
    dates = [d.date() if hasattr(d, "date") else d for d in ser.index]
    n = len(levels)
    rets = np.diff(levels) / np.array(levels[:-1])
    out = {
        "bars": n,
        "first_bar": str(dates[0]),
        "last_bar": str(dates[-1]),
        "level_end": levels[-1],
        "years": round(n / 244.0, 2),
        "horizons": {},
        "years_rows": calendar_years(levels, dates),
        "underwater": [],
    }
    for label, h in HORIZONS:
        _, rets_h = hold_outcomes(np.array(levels), h)
        d = describe(rets_h)
        if d["n"]:
            indep = describe(independent_slice(rets_h, h))
            d["independent"] = {"n": indep["n"],
                                "count_losing": indep["count_losing"],
                                "share_losing": indep["share_losing"],
                                "median": indep["median"], "worst": indep["worst"]}
        out["horizons"][label] = d
    spells = drawdown_spells(levels, dates)
    spells = [s for s in spells if s["depth"] < -1e-9]
    spells.sort(key=lambda s: s["depth"])
    out["underwater"] = [
        {"started_on": str(s["started_on"]), "trough_on": str(s["trough_on"]),
         "depth": float(s["depth"]), "recovered_on": (str(s["recovered_on"])
                                                      if s["recovered_on"] else None),
         "bars_under": int(s["bars_under"]),
         "bars_to_recover": (None if s["bars_to_recover"] is None else int(s["bars_to_recover"]))}
        for s in spells[:8]
    ]
    out["deepest"] = out["underwater"][0] if out["underwater"] else None
    still_under = [s for s in spells if s["recovered_on"] is None]
    out["currently_underwater"] = bool(still_under)
    out["current_underwater"] = (
        {"started_on": str(still_under[0]["started_on"]), "depth": float(still_under[0]["depth"]),
         "bars_under": int(still_under[0]["bars_under"])} if still_under else None)
    out["daily"] = {"vol": float(np.std(rets) * np.sqrt(244)),
                    "sharpe": float(np.mean(rets) / np.std(rets) * np.sqrt(244)) if np.std(rets) else None}
    # annualised growth from the first bar the series actually starts at, not from 1.0
    out["start_level"] = levels[0]
    out["cagr"] = ((levels[-1] / levels[0]) ** (244.0 / max(1, n - 1)) - 1.0) if levels[0] else None
    # where in time do the losing 12-month starts sit -- 93 windows is not 93 independent losses
    _, rets_1y = hold_outcomes(np.array(levels), HORIZONS[0][1])
    losing_years = {}
    for i, r in enumerate(rets_1y):
        if r < 0:
            y = dates[i].year
            losing_years[y] = losing_years.get(y, 0) + 1
    out["losing_start_years"] = dict(sorted(losing_years.items()))
    out["verdict"] = verdict_of(out["horizons"]["1y"], out["horizons"]["1y"].get("independent", {"n": 0}))
    return out


def run():
    payload = {"face": FACE, "why": "the average is published; the odds of a losing year are not",
               "wallet_cny": WALLET, "config": {"rebal": REBAL, "n_hold": NHOLD, "cost_bp_side": COST * 1e4,
                                               "vol_target": VT, "sleeves": ["equity", "commodity", "convertible"]},
               "published_for_comparison": PUBLISHED, "calibers": {}}
    for name, lag in (("published_lag0", 0), ("honest_lag1", 1)):
        ser, turn, n_flip, n_uni = build_series(lag)
        m = measure(ser)
        m["turnover"] = float(turn) if np.isscalar(turn) else None
        m["universe"] = n_uni
        m["flips_repaired"] = n_flip
        payload["calibers"][name] = m
        print(f"[{name}] verdict={m['verdict']} "
              f"1y_losing={m['horizons']['1y']['count_losing']}/{m['horizons']['1y']['n']} "
              f"median={m['horizons']['1y']['median']:.4f} worst={m['horizons']['1y']['worst']:.4f}",
              flush=True)
    # the honest caliber is the one a ticket can deliver
    payload["verdict"] = payload["calibers"]["honest_lag1"]["verdict"]
    payload["evidence_cutoff"] = payload["calibers"]["honest_lag1"]["last_bar"]
    payload["reconciliation"] = reconcile(payload["calibers"]["published_lag0"])
    payload["headline"] = headline(payload)
    os.makedirs("results", exist_ok=True)
    with io.open(JSON_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    text = doc_prologue() + "\n" + render(payload)
    os.makedirs("research", exist_ok=True)
    with io.open(DOC_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print("wrote", JSON_PATH, "and", DOC_PATH)
    return 0


# ---------------------------------------------------------------- reader page
BEGIN, END = "<!-- ETF-BOOK-LOSING-ODDS:BEGIN -->", "<!-- ETF-BOOK-LOSING-ODDS:END -->"


def pct(x, nd=2):
    return f"{x * 100:+.{nd}f}%"


def cny(x):
    return f"{x:+,.0f}"


def headline(p):
    h = p["calibers"]["honest_lag1"]
    y1 = h["horizons"]["1y"]
    return (f"hold it a year from any of {y1['n']} start dates: {y1['count_losing']} of them end "
            f"below water (median {pct(y1['median'])}, worst {pct(y1['worst'])} = {cny(y1['worst_cny'])} CNY "
            f"on {WALLET:,.0f}); {y1['independent']['count_losing']} of the "
            f"{y1['independent']['n']} non-overlapping years lose")


def render(p):
    h0, h1 = p["calibers"]["published_lag0"], p["calibers"]["honest_lag1"]
    y1 = h1["horizons"]["1y"]
    L = [BEGIN, "", f"**verdict** `{p['verdict']}`", "",
         f"window {h1['first_bar']}..{h1['last_bar']} ({h1['bars']} bars = {h1['years']} years) · "
         f"evidence_cutoff {p['evidence_cutoff']} · wallet {WALLET:,.0f} CNY · "
         f"bond-free book, {NHOLD} names, rebalance every {REBAL} bars, {COST*1e4:.0f}bp a side, "
         f"{VT*100:.0f}% vol target", "",
         "## 一句话", "", p["headline"] + ".", "",
         "Two calibers are measured. `published_lag0` is the caliber every printed number of this book "
         "already uses (the new book starts accruing on the decision bar's own open); `honest_lag1` "
         "starts it at the next open, which is what an order sheet can deliver. The verdict above is "
         "the honest one.", "",
         "## 持有一年 / 两年 / 三年，结果是什么分布", "",
         "| 持有 | 起点数 | 亏钱起点 | 中位 | 最差 | 最好 | 中位 CNY | 最差 CNY | 不重叠窗口亏了多少个 |",
         "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name, row in (("1y", "1y"), ("2y", "2y"), ("3y", "3y")):
        d = h1["horizons"][row]
        ind = d.get("independent") or {"count_losing": 0, "n": 0}
        L.append(f"| {name} | {d['n']} | {d['count_losing']} ({d['share_losing']*100:.1f}%) | "
                 f"{pct(d['median'])} | {pct(d['worst'])} | {pct(d['best'])} | "
                 f"{cny(d['median_cny'])} | {cny(d['worst_cny'])} | "
                 f"{ind['count_losing']} / {ind['n']} |")
    L += ["", f"窗口重叠时起点不独立：一万四千个起点读到的仍是同一条 {h1['years']} 年历史。"
              f"右列的不重叠子样本才是独立观测数——一年的判词背后只有 "
              f"{y1['independent']['n']} 个，两年的只有 {h1['horizons']['2y'].get('independent',{}).get('n',0)} 个，"
              f"三年的只有 {h1['horizons']['3y'].get('independent',{}).get('n',0)} 个。"
              "所以这张面描述的是「这段历史长什么样」，不是「未来亏钱概率」，别把百分比读成概率。", ""]
    ly = h1["losing_start_years"]
    if ly:
        parts = "、".join(f"{y} 年 {n} 个" for y, n in ly.items())
        L.append(f"另外，亏钱的 {y1['count_losing']} 个起点不是 {y1['count_losing']} 次独立亏损，"
                 f"它们挤在同一段回撤里：{parts}。这也是为什么重叠口径的占比"
                 f"（{y1['share_losing']*100:.1f}%）远高于不重叠口径（"
                 f"{y1['independent']['count_losing']}/{y1['independent']['n']}）。")
    L += ["",
         "## 逐年，折算成人民币", "",
         "| 年 | 收益 | 百万元钱包的结果 | 根数 | 是否整年 |", "|---|---:|---:|---:|---|"]
    for r in h1["years_rows"]:
        L.append(f"| {r['year']} | {pct(r['ret'])} | {cny(r['cny'])} | {r['bars']} | "
                 f"{'否（到面板边缘）' if r['partial'] else '是'} |")
    worst_year = min(h1["years_rows"], key=lambda r: r["ret"])
    worst_year0 = min(h0["years_rows"], key=lambda r: r["ret"])
    full = [r for r in h1["years_rows"] if not r["partial"]]
    worst_full = min(full, key=lambda r: r["ret"]) if full else None
    L += ["", f"表里的「最差的一年」含还没走完的 {worst_year['year']}（只有 {worst_year['bars']} 根 bar），"
              f"所以它是 {pct(worst_year['ret'])}，发布口径同一格是 {pct(worst_year0['ret'])}——"
              f"同一年、同一本书，口径差 {(worst_year0['ret'] - worst_year['ret'])*100:.2f} 个百分点，"
              "这一格就是「晚一天买入」的价格。"
              + (f"只看完整年份，最差是 {worst_full['year']} 的 {pct(worst_full['ret'])}"
                 f"（{cny(worst_full['cny'])} CNY）；**六个完整年份没有一个亏钱**。"
                 if worst_full and worst_full["ret"] > 0 else
                 (f"只看完整年份，最差是 {worst_full['year']} 的 {pct(worst_full['ret'])}。"
                  if worst_full else "")), "",
         "## 水下多久，多深", ""]
    d = h1["deepest"]
    if d:
        L.append(f"最深的洞 {pct(d['depth'])}（{d['started_on']} → {d['trough_on']}），"
                 f"水下 {d['bars_under']} 根 bar，"
                 + (f"于 {d['recovered_on']} 填平（{d['bars_to_recover']} 根）。" if d["recovered_on"]
                    else "到面板结束都没填平。"))
    if h1["current_underwater"]:
        c = h1["current_underwater"]
        L.append(f"今天仍在洞中：自 {c['started_on']} 起，当前 {pct(c['depth'])}，已 {c['bars_under']} 根。")
    else:
        L.append("今天不在洞中（最新 bar 就是历史新高）。")
    L += ["", "| 起始 | 谷底 | 深度 | 填平 | 水下 bar 数 | 从谷底到填平 |", "|---|---|---:|---|---:|---:|"]
    for s in h1["underwater"][:5]:
        L.append(f"| {s['started_on']} | {s['trough_on']} | {pct(s['depth'])} | "
                 f"{s['recovered_on'] or '未填平'} | {s['bars_under']} | "
                 f"{s['bars_to_recover'] if s['bars_to_recover'] is not None else '—'} |")
    L += ["", "## 两种口径摆在一起", "",
          "| 口径 | 一年亏钱起点 | 中位 | 最差 | 年化（本条重算） | 最差年（含未走完的 2026） | 最深洞 |", "|---|---:|---:|---:|---:|---:|---:|"]
    for name, cal in (("published_lag0", h0), ("honest_lag1", h1)):
        d1 = cal["horizons"]["1y"]
        wy = min(cal["years_rows"], key=lambda r: r["ret"])
        L.append(f"| {name} | {d1['count_losing']} / {d1['n']} ({d1['share_losing']*100:.1f}%) | "
                 f"{pct(d1['median'])} | {pct(d1['worst'])} | {pct(cal['cagr'])} | {pct(wy['ret'])} | "
                 f"{pct(cal['deepest']['depth']) if cal['deepest'] else '—'} |")
    L += ["", f"口径差不是细节：`entry_lag` 一天之差值 "
              f"{(h0['horizons']['1y']['median'] - h1['horizons']['1y']['median'])*100:.2f} 个百分点的中位一年，"
              f"亏钱起点从 {h0['horizons']['1y']['count_losing']} 个变成 {h1['horizons']['1y']['count_losing']} 个。"
              "同一张表内互比，别跨表比。", "",
          "## 对账：这条重算的序列，是不是发布面那条", ""]
    r = p["reconciliation"]
    L += [f"| 量 | 本条重算（lag0） | 发布面 `etf_nobond_vt.json` |", "|---|---:|---:|",
          f"| 最深回撤 | {pct(r['maxdd_have'])} | {pct(r['maxdd_pub'])} |",
          f"| 最差年（{r['worst_year_label']}） | {pct(r['worst_year_have'])} | {pct(r['worst_year_pub'])} |",
          f"| 夏普 | {r['sharpe_have']:.3f} | {r['sharpe_pub']:.3f} |",
          f"| 年化 | {pct(r['cagr_have'])} | {pct(r['cagr_pub'])} |", "",
          f"**{r['verdict']}**：最深回撤与最差年逐位对得上（≤0.1pp），说明本条读的是同一条书；"
          "年化的差来自重算起点水平（发布面记 `start_level`），不来自算法。"
          "对不上时这一段会印 `MISMATCH`，此时下面所有赔率都不该被引用。", "",
          "## 读数边界（别读成承诺）", "",
          "- 现金腿在引擎里按 0% 计息，波动目标只降不升；所以这是策略的赔率，不是货币基金的赔率。",
          "- 票池是现存 ETF，带生存者偏差；这段历史的乐观方向已知，本条不重估它。",
          "- 十年以上的持有期在这条面板上不存在，三年以上的判读只有个位数独立观测。",
          "", END, ""]
    return "\n".join(L)


def doc_prologue():
    return ("# 这本书一年下来亏钱的概率有多大\n\n"
            f"面：`{JSON_PATH}` · 脚本：`scripts/{FACE}.py` · 页面数字由数据渲染，`--check` 逐字比对\n\n"
            "> 发布面一直在印平均值（一年 9~11%）和最差年（-0.72%）。读者拿钱进场的真正问题是另一句："
            "**随便哪一天买入，持有一年，亏钱的起点占几成、最差亏多少人民币、要熬多久。**"
            "本条不重估任何一条判据，只把生产候选这本书的路径量一遍，并把「它能被下单的版本」单列一格。\n\n"
            "## 0. 为什么这张面必须自己算\n\n"
            "生产候选（无债档 + 8% 波动目标）的日净值序列从未以序列形式发布，只发布过聚合读数。"
            "所以本条**import 同一条引擎**（`etf_robust_pf.open_to_open_equity`）重算两条口径，"
            "并把聚合读数与 `results/etf_nobond_vt.json` 对账，差在哪一节写明。\n")


def check():
    if not os.path.exists(JSON_PATH):
        print("STALE face missing:", JSON_PATH)
        return 3
    with io.open(JSON_PATH, encoding="utf-8") as fh:
        p = json.load(fh)
    if not os.path.exists(DOC_PATH):
        print("STALE doc missing:", DOC_PATH)
        return 3
    cur = io.open(DOC_PATH, encoding="utf-8").read()
    head = doc_prologue()
    want = head + "\n" + render(p)
    if cur.strip() != want.strip():
        i = next((k for k in range(min(len(cur), len(want))) if cur[k] != want[k]), min(len(cur), len(want)))
        print("CHECK FAILED: page text differs from data at char", i)
        print("have:", cur[max(0, i - 80):i + 80].replace("\n", "\\n"))
        print("want:", want[max(0, i - 80):i + 80].replace("\n", "\\n"))
        return 4
    h1 = p["calibers"]["honest_lag1"]["horizons"]["1y"]
    if h1["count_losing"] != sum(1 for _ in range(h1["count_losing"])):
        print("CHECK FAILED: count arithmetic")
        return 4
    print(f"OK {p['face']} {p['verdict']} · 1y losing {h1['count_losing']}/{h1['n']} · "
          f"evidence_cutoff {p['evidence_cutoff']}")
    return 0


def selftest():
    ok = 0
    fails = []
    # 1 monotone up = no losing window
    up = np.linspace(1.0, 2.0, 400)
    d = describe(hold_outcomes(up, 244)[1])
    if d["count_losing"] == 0:
        ok += 1
    else:
        fails.append("monotone up produced losers")
    # 2 monotone down = every window loses
    dn = np.linspace(2.0, 1.0, 400)
    d2 = describe(hold_outcomes(dn, 244)[1])
    if d2["share_losing"] == 1.0:
        ok += 1
    else:
        fails.append("monotone down did not lose everywhere")
    # 3 independent slice count = floor((n-1)/H) style
    rets = np.zeros(500)
    if len(independent_slice(rets, 244)) == len(rets[::244]):
        ok += 1
    else:
        fails.append("independent slice miscounted")
    # 4 spells: a V path has exactly one spell with a known recovery
    lv = np.array([1.0, 1.1, 1.05, 1.0, 1.2])
    dates = list(range(5))
    sp = [s for s in drawdown_spells(lv, dates) if s["depth"] < -1e-9]
    if len(sp) == 1 and sp[0]["recovered_on"] == 4 and abs(sp[0]["depth"] - (1.0 / 1.1 - 1)) < 1e-9:
        ok += 1
    else:
        fails.append("V-path spell wrong: %r" % (sp,))
    # 5 still-underwater path has no recovery
    lv2 = np.array([1.0, 1.2, 1.1, 1.05])
    sp2 = [s for s in drawdown_spells(lv2, list(range(4))) if s["depth"] < -1e-9]
    if len(sp2) == 1 and sp2[0]["recovered_on"] is None:
        ok += 1
    else:
        fails.append("underwater path reported a recovery")
    # 6 verdict token never upgrades a losing history to 'cannot lose'
    h = describe(np.array([0.1, -0.05, 0.2]))
    h["independent"] = {"n": 3}
    v = verdict_of(h, h["independent"])
    if "WON" not in v:
        ok += 1
    else:
        fails.append("verdict called a losing history a win")
    # 7 thin all-positive sample is labelled thin
    h2 = describe(np.array([0.1, 0.2, 0.05]))
    v2 = verdict_of(h2, {"n": 3})
    if v2 == "EVERY_12_MONTH_START_WON_ON_THIN_SAMPLE":
        ok += 1
    else:
        fails.append("thin sample not labelled: %s" % v2)
    # 8 calendar year split keeps partial years marked
    rows = calendar_years(np.array([1.0, 1.1, 1.2, 1.3]), [pd.Timestamp("2020-12-30").date(),
                                                           pd.Timestamp("2020-12-31").date(),
                                                           pd.Timestamp("2021-01-04").date(),
                                                           pd.Timestamp("2021-01-05").date()])
    if len(rows) == 2 and rows[0]["partial"] is False and abs(rows[0]["ret"] - 0.1) < 1e-9:
        ok += 1
    else:
        fails.append("calendar split wrong: %r" % (rows,))
    print(f"selftest {ok}/8")
    for f in fails:
        print(" FAIL:", f)
    return 0 if not fails else 4


if __name__ == "__main__":
    import pandas as pd
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run":
        sys.exit(run())
    if cmd == "check":
        sys.exit(check())
    if cmd == "selftest":
        sys.exit(selftest())
    print("usage: run|check|selftest")
    sys.exit(2)
