"""ETF 面板是「不含派息」的价格序列：同篮子的两只基金，价格年化之差就是派息政策之差。

为什么值得一测
--------------
本行的日线面板（`data/daily/<sh|sz><code>.csv`）是从 sina `klc_kl` 取的价格序列，
复权因子在 ETF 上恒为 1.0（r398 探针：四窗 ratio=1.000000），所以：

  * 把钱**分配出去**的基金，价格序列把 carry 完全丢掉（银华日利 511880 的
    价格年化 ≈ 0.00%，而它同期持有的是存款/回购，经济收益 ≈ 1.5~2%/年）；
  * 把 carry **累积进净值**的基金，价格序列里带着 accrual（短融 511360 ≈ +2.14%/年）。

两者在面板上看起来差一个过去一整年的收益——这不是业绩差异，是**派息政策**差异。
只要书用价格收益率排名、并且把排名数字当收益报给读者，这条偏差就会同时污染
「谁更好」和「书赚了多少」两个答案。

测量法（不猜、不拟合）
----------------------
1. **同篮子对照组**：`results/etf_label_census.json` 已经把「同一篮子」的 ETF 认成
   一个 label group（121 组）。同一篮子里两只基金的共同窗口价格年化之差，
   除了费率与跟踪误差，就只剩派息政策——**不需要任何外部分红数据**。
2. **现金类的定义性锚点**：货币类基金的价格年化 ≈ 0% 而经济收益必须 ≈ 短期资金利率，
   所以「0% − 同期 GC001 中位」就是这条偏差在该类上的**定义性**大小，不是估计。
3. **书里有没有吃到这条偏差**：读 `results/etf_book_positions/LEDGER.json` 的实际持仓，
   看手里那只是不是同一组里价格年化更低的那一只（= 分配型孪生）。

诚实边界
--------
* 派息不是损失：现金是派到持有人手上的。这条面量的是**面板/排名**的偏差，
  不是投资人少赚了。
* 价差里混着费率与跟踪误差，本面只报价差与它的构成上限，不把它们分开。
* 组内成员不足两只、或共同窗口 < 250 根 bar 的组，一律跳过并如实计数。
* GC001 锚点用的是面板自己最后一根 bar（现为落后若干交易日的旧面），
  本面打印该日期，不把「旧」读成「今天」。

用法
----
    python scripts/etf_distribution_bias.py            # 测量 -> results/etf_distribution_bias.json
    python scripts/etf_distribution_bias.py check      # 从面里的数字重派生判词
    python scripts/etf_distribution_bias.py selftest   # 离线合成腿

退出码：0 正常 | 1 check 不符 | 2 机制故障（面板/分组面缺失）。
"""
import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

CENSUS = os.path.join(ROOT, "results", "etf_label_census.json")
LEDGER = os.path.join(ROOT, "results", "etf_book_positions", "LEDGER.json")
DAILY = os.path.join(ROOT, "data", "daily")
REPO = os.path.join(ROOT, "data", "repo_daily", "GC001.csv")
OUT = os.path.join(ROOT, "results", "etf_distribution_bias.json")

MIN_BARS = 250            # 共同窗口下限：不到一年不做年度化比较
CORR_LINE = 0.99          # 同日收益相关低于此线=不是同一篮子（label 只当候选，不当结论）
JUMP_LINE = 0.35          # 单日 |r| 超过此线=份额折算/翻转数据面，不是派息（r1926 族）
CASH_LIKE_PP = 3.0        # 现金类身份线：价格年化绝对值低于此数才像「现金」
SPREAD_LINE_PP = 1.0      # 组内价差达到「一年一个点」才当成派息政策级差异
TWIN_LINE_PP = 0.5        # 书里那只比同组孪生低这么多，才算「持有的是分配型孪生」


# ------------------------------------------------------------------ 数据面
def load_prices(code):
    """按 sh/sz 前缀找一只基金的日线；找不到返回 None（诚实跳过，不猜路径）。"""
    for pre in ("sh", "sz"):
        p = os.path.join(DAILY, pre + code + ".csv")
        if os.path.exists(p):
            df = pd.read_csv(p)
            if "date" not in df.columns or "close" not in df.columns:
                return None
            df["date"] = pd.to_datetime(df["date"])
            s = df.sort_values("date").set_index("date")["close"].astype(float)
            s = s[~s.index.duplicated(keep="last")]
            return s.dropna()
    return None


def annualise(series):
    """共同窗口内的价格年化（按自然日）+ 窗口长度。"""
    if len(series) < 2:
        return None
    days = (series.index[-1] - series.index[0]).days
    if days <= 0:
        return None
    growth = float(series.iloc[-1]) / float(series.iloc[0])
    if growth <= 0:
        return None
    return growth ** (365.25 / days) - 1.0, days, int(len(series))


def common_window(frames, min_bars=MIN_BARS):
    """所有成员的共同日期窗口；不足 min_bars 返回 None。"""
    idx = None
    for s in frames:
        idx = s.index if idx is None else idx.intersection(s.index)
        if len(idx) < min_bars:
            return None
    return idx.sort_values() if idx is not None else None


def repo_median_by_window(first, last):
    """同期 GC001 中位（年化 %），并回传面板自己的末 bar —— 旧面要说旧。"""
    if not os.path.exists(REPO):
        return None
    df = pd.read_csv(REPO)
    if "date" not in df.columns or "close" not in df.columns:
        return None
    df["date"] = pd.to_datetime(df["date"])
    df = df[(df["date"] >= first) & (df["date"] <= last)]
    if df.empty:
        return None
    return {"median_pct": round(float(df["close"].median()), 3),
            "n": int(len(df)),
            "panel_last_bar": str(pd.read_csv(REPO)["date"].iloc[-1])}


# ------------------------------------------------------------------ 测量
def has_jump(series):
    """窗口内有没有份额折算/翻转类的单日巨跳（有=这只不能用来比派息）。"""
    r = series.pct_change().dropna()
    return bool((r.abs() > JUMP_LINE).any())


def same_basket(frames, codes, idx):
    """label 只是候选：真同篮子要求同日收益相关 >= CORR_LINE（对最长史那只）。

    派息日当天两条序列必然分叉，而那几天正是本面要找的东西——所以认篮子时
    先去掉分歧最大的 3 天再算相关（剔除天数固定、写进面里，不按结果调）。
    """
    rets = {c: frames[c].reindex(idx).pct_change() for c in codes}
    ref = max(codes, key=lambda c: len(frames[c]))
    keep, dropped = [ref], []
    for c in codes:
        if c == ref:
            continue
        pair = pd.concat([rets[ref], rets[c]], axis=1).dropna()
        if len(pair) > 8:
            gap = (pair.iloc[:, 0] - pair.iloc[:, 1]).abs()
            pair = pair.drop(index=gap.nlargest(3).index)
        corr = float(pair.iloc[:, 0].corr(pair.iloc[:, 1])) if len(pair) > 2 else np.nan
        if np.isfinite(corr) and corr >= CORR_LINE:
            keep.append(c)
        else:
            dropped.append({"symbol": c, "corr": (None if not np.isfinite(corr)
                                                  else round(corr, 4)),
                            "window_after_trim": int(len(pair))})
    return keep, dropped


def is_cash_like(labels):
    return any(("货币" in str(x)) or ("保证金" in str(x)) or ("短融" in str(x))
               for x in (labels or []))


def group_rows(groups):
    """逐组算共同窗口价差；不足条件的组进 skipped 计数（不静默丢）。

    身份判定分两种，写进每一行（`identity` 字段）：
      * 股票/债券类 = 同篮子，靠同日收益相关（去分歧后）>= CORR_LINE；
      * 现金类 = 收益本身近乎常数、相关系数无意义，改用「两只都像现金」判定
        （|价格年化| < CASH_LIKE_PP 才算），否则如实丢掉。
    """
    out, skipped = [], {"fewer_than_two_priced": 0, "short_window": 0,
                        "no_growth": 0, "not_a_group": 0,
                        "not_same_basket": 0, "share_conversion_jump": 0,
                        "cash_class_not_cash_like": 0}
    for g in groups:
        if g.get("state") != "GROUP" or len(g.get("members") or []) < 2:
            skipped["not_a_group"] += 1
            continue
        frames, codes = {}, []
        for code in g["members"]:
            s = load_prices(code)
            if s is not None and len(s) >= MIN_BARS:
                frames[code] = s
                codes.append(code)
        if len(codes) < 2:
            skipped["fewer_than_two_priced"] += 1
            continue
        idx = common_window([frames[c] for c in codes])
        if idx is None:
            skipped["short_window"] += 1
            continue
        cash = is_cash_like(g.get("labels"))
        dropped = []
        if cash:
            keep = []
            for c in codes:
                a = annualise(frames[c].reindex(idx))
                if a is None:
                    continue
                if abs(a[0] * 100.0) < CASH_LIKE_PP:
                    keep.append(c)
                else:
                    dropped.append({"symbol": c,
                                    "why": "not cash-like",
                                    "cagr_pct": round(a[0] * 100, 3)})
            codes = keep
        else:
            codes, dropped = same_basket(frames, codes, idx)
        if len(codes) < 2:
            skipped["cash_class_not_cash_like" if cash else "not_same_basket"] += 1
            continue
        if any(has_jump(frames[c].reindex(idx)) for c in codes):
            skipped["share_conversion_jump"] += 1
            continue
        members = {}
        for c in codes:
            a = annualise(frames[c].reindex(idx))
            if a is None:
                continue
            members[c] = {"cagr_pct": round(a[0] * 100, 3),
                          "window_bars": a[2]}
        if len(members) < 2:
            skipped["no_growth"] += 1
            continue
        best = max(members, key=lambda c: members[c]["cagr_pct"])
        worst = min(members, key=lambda c: members[c]["cagr_pct"])
        spread = members[best]["cagr_pct"] - members[worst]["cagr_pct"]
        out.append({
            "labels": g.get("labels"),
            "identity": "CASH_CLASS" if cash else "SAME_BASKET_CORR",
            "members": members,
            "window": {"start": str(idx[0].date()), "end": str(idx[-1].date()),
                       "bars": int(len(idx))},
            "highest": best,
            "lowest": worst,
            "spread_pp": round(spread, 3),
            "policy_level": bool(spread >= SPREAD_LINE_PP),
            "dropped": dropped,
        })
    return out, skipped


def money_anchor(rows):
    """货币类组：价格年化应该≈短期资金利率。差额=该类派息被面板完全丢掉的定义性大小。"""
    picked = []
    for r in rows:
        labels = [str(x) for x in (r.get("labels") or [])]
        if not any("货币" in x or "保证金" in x for x in labels):
            continue
        first = pd.Timestamp(r["window"]["start"])
        last = pd.Timestamp(r["window"]["end"])
        anchor = repo_median_by_window(first, last)
        if anchor is None:
            continue
        levels = [m["cagr_pct"] for m in r["members"].values()]
        picked.append({
            "labels": r["labels"],
            "members": r["members"],
            "window": r["window"],
            "median_price_cagr_pct": round(float(np.median(levels)), 3),
            "repo_median_pct": anchor["median_pct"],
            "repo_panel_last_bar": anchor["panel_last_bar"],
            "gap_pp": round(anchor["median_pct"] - float(np.median(levels)), 3),
        })
    return picked


def book_twins(rows):
    """书里实际持有的那几只，在同一 label group 内是不是价格年化更低的一只。"""
    if not os.path.exists(LEDGER):
        return {"status": "LEDGER_MISSING", "held": []}
    with open(LEDGER, encoding="utf-8") as fh:
        led = json.load(fh)
    lrows = led.get("rows") or []
    if not lrows:
        return {"status": "LEDGER_EMPTY", "held": []}
    last = lrows[-1]
    held = [h.get("symbol") for h in (last.get("holdings") or [])]
    by_member = {}
    for r in rows:
        for c, m in r["members"].items():
            by_member[c] = (r, m)
    out = []
    for code in held:
        if code not in by_member:
            out.append({"symbol": code, "state": "NOT_IN_ANY_GROUP"})
            continue
        r, m = by_member[code]
        twin = r["highest"]
        gap = r["members"][twin]["cagr_pct"] - m["cagr_pct"]
        out.append({
            "symbol": code,
            "labels": r["labels"],
            "own_cagr_pct": m["cagr_pct"],
            "twin": twin,
            "twin_cagr_pct": r["members"][twin]["cagr_pct"],
            "gap_pp": round(gap, 3),
            "holds_lower_twin": bool(gap >= TWIN_LINE_PP),
            "window": r["window"],
        })
    return {"status": "OK", "bar": last.get("bar"), "held": out}


def decide(rows, anchor, twins, skipped):
    """判词只由数字决定，且必须点名它读的是哪一层。

    「书里没吃到这条偏差」只有在**真有持仓被分组面定价**时才成立；
    全部持仓都不在任何 measured group 里 = 没量到，不是干净（r98 族：缺面不许印成 0）。
    """
    policy = [r for r in rows if r["policy_level"]]
    held = twins.get("held", [])
    measured = [t for t in held if not t.get("state")]
    holding = [t for t in measured if t.get("holds_lower_twin")]
    if anchor:
        worst_gap = max(a["gap_pp"] for a in anchor)
    else:
        worst_gap = None
    if holding:
        word = "BOOK_HOLDS_THE_DISTRIBUTING_TWIN"
    elif not measured:
        word = "BOOK_UNMEASURED"
    elif policy:
        word = "POLICY_SPREAD_EXISTS_BUT_BOOK_CLEAR"
    else:
        word = "NO_POLICY_SPREAD_FOUND"
    return {
        "verdict": word,
        "policy_groups": len(policy),
        "book_holdings": len(held),
        "book_holdings_measured": len(measured),
        "book_twins_flagged": len(holding),
        "money_gap_pp": worst_gap,
        "skipped": skipped,
        "reading": (
            "价格序列不含派息时，同篮子两只基金的价格年化之差就是派息政策之差。"
            "本判词只看四件事：组内价差有没有过线、货币类的定义性缺口有多大、"
            "书手里的持仓有没有被分组面定价、被定价的里面有没有更低的那一只。"
        ),
    }


def build():
    if not os.path.exists(CENSUS):
        raise RuntimeError(f"missing {CENSUS}")
    with open(CENSUS, encoding="utf-8") as fh:
        census = json.load(fh)
    groups = census.get("groups") or []
    rows, skipped = group_rows(groups)
    rows.sort(key=lambda r: -r["spread_pp"])
    anchor = money_anchor(rows)
    twins = book_twins(rows)
    dec = decide(rows, anchor, twins, skipped)
    cutoff = None
    for r in rows:
        end = r["window"]["end"]
        cutoff = end if cutoff is None else max(cutoff, end)
    return {
        "artifact": "etf_distribution_bias",
        "generated": dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "evidence_cutoff": cutoff,
        "sources": {
            "groups": "results/etf_label_census.json (same-basket labels)",
            "prices": "data/daily/<sh|sz><code>.csv (sina klc_kl, qfq factor = 1.0)",
            "repo": "data/repo_daily/GC001.csv",
            "book": "results/etf_book_positions/LEDGER.json",
        },
        "lines": {"min_bars": MIN_BARS, "spread_line_pp": SPREAD_LINE_PP,
                  "twin_line_pp": TWIN_LINE_PP, "corr_line": CORR_LINE,
                  "jump_line": JUMP_LINE, "cash_like_pp": CASH_LIKE_PP},
        "counts": {"groups_in_census": len(groups), "groups_measured": len(rows),
                   "groups_flagged": sum(1 for r in rows if r["policy_level"]),
                   "skipped": skipped},
        "money_anchor": anchor,
        "groups": rows[:40],
        "book": twins,
        "decision": dec,
        "caveats": [
            "派息不是损失：现金派到持有人手上，本面量的是面板与排名的偏差，不是投资人少赚。",
            "组内价差混着费率与跟踪误差；本面只报价差本身，不把它们拆开。",
            "货币类锚点用同期 GC001 中位，是一个经济收益的上界近似（货基还持有存款/短融），"
            "缺口数字应当读作「这一类的 carry 在面板里基本没了」，不是精确值。",
            "GC001 面板自己落后若干交易日；本面打印该面板自己的末 bar，把「旧」如实写在面上。",
            "同篮子由 label 认领，label 错则本面跟着错——分组正身是 etf_label_census，不在本面重判。",
        ],
    }


def run():
    doc = build()
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=True)
    c, d = doc["counts"], doc["decision"]
    print(f"[distbias] groups {c['groups_measured']}/{c['groups_in_census']} measured, "
          f"{c['groups_flagged']} above {SPREAD_LINE_PP}pp")
    for r in doc["groups"][:6]:
        print(f"  {r['spread_pp']:+7.2f}pp  {r['labels']}  {r['window']['start']}..{r['window']['end']}"
              f"  low={r['lowest']} {r['members'][r['lowest']]['cagr_pct']:+.2f}%"
              f"  high={r['highest']} {r['members'][r['highest']]['cagr_pct']:+.2f}%")
    for a in doc["money_anchor"]:
        print(f"  money {a['labels']} price_med {a['median_price_cagr_pct']:+.2f}% "
              f"vs repo {a['repo_median_pct']:+.2f}% (panel last {a['repo_panel_last_bar']}) "
              f"gap {a['gap_pp']:+.2f}pp")
    print(f"  book {doc['book'].get('status')} bar={doc['book'].get('bar')}")
    for t in doc["book"].get("held", []):
        if t.get("state"):
            print(f"    {t['symbol']} {t['state']}")
        else:
            print(f"    {t['symbol']} own {t['own_cagr_pct']:+.2f}% twin {t['twin']} "
                  f"{t['twin_cagr_pct']:+.2f}% gap {t['gap_pp']:+.2f}pp "
                  f"lower_twin={t['holds_lower_twin']}")
    print(f"[distbias] VERDICT {d['verdict']}")
    print(f"[distbias] receipt {os.path.relpath(OUT, ROOT)}")
    return 0


def check(path=OUT):
    """判词必须由面里的数字重派生，不能信面上存着的字。"""
    if not os.path.exists(path):
        print(f"[distbias] no receipt at {path}")
        return 2
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    bad = []
    for r in doc["groups"]:
        levels = [m["cagr_pct"] for m in r["members"].values()]
        spread = round(max(levels) - min(levels), 3)
        if abs(spread - r["spread_pp"]) > 1e-6:
            bad.append(f"{r['labels']}: spread {r['spread_pp']} != {spread}")
        if bool(spread >= doc["lines"]["spread_line_pp"]) != r["policy_level"]:
            bad.append(f"{r['labels']}: policy_level contradicts its own spread")
        if r["members"][r["highest"]]["cagr_pct"] != max(levels):
            bad.append(f"{r['labels']}: highest is not the maximum")
    again = decide(doc["groups"], doc.get("money_anchor") or [],
                   doc.get("book") or {}, doc["counts"]["skipped"])
    if again["verdict"] != doc["decision"]["verdict"]:
        bad.append(f"verdict {doc['decision']['verdict']} != re-derived {again['verdict']}")
    if bad:
        for b in bad:
            print("[distbias] CHECK FAIL " + b)
        return 1
    print(f"[distbias] check OK: {len(doc['groups'])} groups, verdict "
          f"{doc['decision']['verdict']} re-derived identical")
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    ok, total, fails = 0, 0, []

    def leg(name, fn):
        nonlocal ok, total
        total += 1
        try:
            fn()
            ok += 1
        except AssertionError as e:
            fails.append(f"{name}: {e}")

    idx = pd.date_range("2022-01-03", periods=400, freq="B")

    def twin_pair(distributes):
        """同一篮子：A 累积、B 每年派出 5%；两条价格序列共享同一串日收益（真孪生）。

        篮子必须带真实波动，否则收益序列近乎常数、相关系数没有意义。
        """
        rng = np.random.default_rng(7)
        base = pd.Series(np.exp(np.cumsum(rng.normal(0, 0.004, len(idx)))), index=idx)
        a = base.copy()
        b = base.copy()
        if distributes:
            b.iloc[250:] = b.iloc[250:] * 0.95
        return a, b, base

    def l_price_gap_is_policy_gap():
        a, b, _ = twin_pair(True)
        spread = (annualise(a)[0] - annualise(b)[0]) * 100
        assert spread > 1.0, f"a 5% distribution must show as a >1pp spread, got {spread:.2f}"

    def l_identical_twins_show_nothing():
        a, _, _ = twin_pair(False)
        b = a.copy()
        spread = (annualise(a)[0] - annualise(b)[0]) * 100
        assert abs(spread) < 1e-9, f"identical twins must show zero spread, got {spread}"

    def l_short_window_is_skipped():
        a = pd.Series(1.0, index=idx[:100])
        assert common_window([a, a]) is None, "a sub-year window must be refused"

    def l_common_window_is_intersection():
        a = pd.Series(1.0, index=idx)
        b = pd.Series(1.0, index=idx[50:])
        w = common_window([a, b])
        assert w is not None and w[0] == idx[50], "the window must start where both print"

    def l_row_flags_policy_level():
        # 直接构造一行，走 decide 的分支：价差过线但书没吃到 → 第二档判词
        rows = [{"labels": ["SAME-BASKET"],
                 "members": {"a": {"cagr_pct": 5.0}, "b": {"cagr_pct": 1.0}},
                 "window": {"start": "2022-01-03", "end": "2023-06-30", "bars": 400},
                 "highest": "a", "lowest": "b", "spread_pp": 4.0, "policy_level": True}]
        dec = decide(rows, [], {"status": "OK", "held": [
            {"symbol": "a", "holds_lower_twin": False}]}, {})
        assert dec["verdict"] == "POLICY_SPREAD_EXISTS_BUT_BOOK_CLEAR", dec["verdict"]

    def l_unpriced_book_is_unmeasured_not_clean():
        rows = [{"labels": ["SAME-BASKET"],
                 "members": {"a": {"cagr_pct": 5.0}, "b": {"cagr_pct": 1.0}},
                 "window": {"start": "2022-01-03", "end": "2023-06-30", "bars": 400},
                 "highest": "a", "lowest": "b", "spread_pp": 4.0, "policy_level": True}]
        twins = {"status": "OK", "held": [{"symbol": "z", "state": "NOT_IN_ANY_GROUP"}]}
        dec = decide(rows, [], twins, {})
        assert dec["verdict"] == "BOOK_UNMEASURED", dec["verdict"]

    def l_book_holding_lower_twin_is_named():
        rows = [{"labels": ["SAME-BASKET"],
                 "members": {"a": {"cagr_pct": 5.0}, "b": {"cagr_pct": 1.0}},
                 "window": {"start": "2022-01-03", "end": "2023-06-30", "bars": 400},
                 "highest": "a", "lowest": "b", "spread_pp": 4.0, "policy_level": True}]
        twins = {"status": "OK", "bar": "2026-11-24", "held": [
            {"symbol": "b", "holds_lower_twin": True}]}
        dec = decide(rows, [], twins, {})
        assert dec["verdict"] == "BOOK_HOLDS_THE_DISTRIBUTING_TWIN", dec["verdict"]

    def l_clean_book_is_not_flagged():
        rows = [{"labels": ["X"], "members": {"a": {"cagr_pct": 5.0},
                                              "b": {"cagr_pct": 4.9}},
                 "window": {"start": "2022-01-03", "end": "2023-06-30", "bars": 400},
                 "highest": "a", "lowest": "b", "spread_pp": 0.1, "policy_level": False}]
        dec = decide(rows, [], {"status": "OK", "held": [
            {"symbol": "a", "holds_lower_twin": False}]}, {})
        assert dec["verdict"] == "NO_POLICY_SPREAD_FOUND", dec["verdict"]

    def l_different_basket_is_dropped():
        rng = np.random.default_rng(4)
        a = pd.Series(1.0 + 0.0002 * np.arange(len(idx)), index=idx)
        b = pd.Series(1.0 * np.exp(rng.normal(0, 0.01, len(idx)).cumsum()), index=idx)
        keep, dropped = same_basket({"a": a, "b": b}, ["a", "b"], idx)
        assert len(keep) == 1 and dropped, "a series with no co-movement must be dropped"

    def l_same_basket_passes():
        a, b, _ = twin_pair(True)
        keep, dropped = same_basket({"a": a, "b": b * 1.001}, ["a", "b"], idx)
        assert len(keep) == 2 and not dropped, "true twins must both survive the corr gate"

    def l_share_conversion_jump_is_excluded():
        a, _, _ = twin_pair(False)
        b = a.copy()
        b.iloc[200] = b.iloc[200] * 0.5      # 一次份额折算，不是派息
        assert has_jump(b), "a 50% single-day jump must be seen"
        assert not has_jump(a), "a clean series must not be flagged"

    for name, fn in [
        ("price gap is policy gap", l_price_gap_is_policy_gap),
        ("identical twins show nothing", l_identical_twins_show_nothing),
        ("short window is skipped", l_short_window_is_skipped),
        ("common window is the intersection", l_common_window_is_intersection),
        ("a wide row is flagged as policy", l_row_flags_policy_level),
        ("an unpriced book is unmeasured, not clean", l_unpriced_book_is_unmeasured_not_clean),
        ("book holding the lower twin is named", l_book_holding_lower_twin_is_named),
        ("a clean book is not flagged", l_clean_book_is_not_flagged),
        ("a different basket is dropped", l_different_basket_is_dropped),
        ("true twins pass the corr gate", l_same_basket_passes),
        ("a share conversion is excluded", l_share_conversion_jump_is_excluded),
    ]:
        leg(name, fn)

    for f in fails:
        print("FAIL " + f)
    print(f"[distbias] selftest {ok}/{total} PASS")
    return 0 if ok == total else 1


def main(argv):
    cmd = argv[0] if argv else "run"
    try:
        if cmd == "run":
            return run()
        if cmd == "check":
            return check()
        if cmd == "selftest":
            return selftest()
    except (OSError, RuntimeError, ValueError) as e:
        print(f"[distbias] FAIL: {e}")
        return 2
    print(__doc__)
    return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
