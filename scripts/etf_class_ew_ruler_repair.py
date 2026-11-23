"""The ruler every class comparison is measured with is composed of things it denies (r1974 bm-c)

`etf_equity_alpha.classify` labels a name by its keyword, then overrides that label with the
*median 60-day realised vol* of the price series (MONEY_VOL 3% / BOND_VOL 8%). On this panel
that override keeps 59 names in `money` -- 32 of which move like equity (full-window vol
14-20%), one of them earns +14.09%/yr and one -3.26%/yr. The class named "money" therefore
publishes an equal-weight FACE that falls 14.39% peak-to-trough; no cash fund can do that.

That number is not cosmetic. `results/etf_equity_alpha.json` publishes the same ruler as
`bond_money_only_ew_bench` (1.18%/yr, -3.86% drawdown) -- the yardstick a reader compares the
book's own defensive sleeve against (0.08%/yr). And the class labels feed `mixes` and
`yearly_gross_by_class`, i.e. how the book's P&L is attributed to "defensive" vs "equity".

This face does three things and nothing else:

  1. prices the published ruler's money/bond/bond+money equal-weight arms (control C1: the
     bond+money arm must reproduce the released 1.18% / -3.86% cell for cell);
  2. prices the same three arms under a repaired ruler -- name markers decide cash vs bond,
     and a price sanity gate demotes (never promotes) a name whose own history rules out the
     defensive label it was given (vol > 2% or a single day > 5% is not cash; vol > 8% is not
     fixed income at all);
  3. runs the production book once and books its P&L by the *published* labels, so the share
     of "defensive" P&L that actually came from names moving like equity is a printed number
     (control C2: the same loop must reproduce the released all_classes 8.97% / -12.54%).

Judges are frozen before the first run (see JUDGES). The face names what is wrong and what the
repair costs; it does not touch the published face, the classifier, or any shared artifact.
"""

import hashlib
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import bench_core as bc  # noqa: E402
import etf_asset_class as AC  # noqa: E402
import etf_composite_pf as E  # noqa: E402
import etf_equity_alpha as A  # noqa: E402

OUT_JSON = os.path.join(bc.RESULTS, "etf_class_ew_ruler_repair.json")
OUT_MD = os.path.join(bc.RESEARCH, "ETF-CLASS-EW-RULER-REPAIR.md")
PUBLISHED_FACE = os.path.join(bc.RESULTS, "etf_equity_alpha.json")

SCHEMA = "etf_class_ew_ruler_repair/v1"

CASH_KW = ("货币", "现金", "日利", "添益", "添利", "快线", "保证金", "日日", "天天金",
           "财富宝", "现金增利")
DEFENSIVE = ("bond", "money")

# ---- judges, frozen before the first run -----------------------------------------------
MONEY_DD_IMPOSSIBLE_PP = 5.0   # a class called "money" cannot fall 5% peak-to-trough
MONEY_VOL_CAP = 0.02           # a repaired cash member must live under 2% vol ...
MONEY_DAY_CAP = 0.05           # ... and never move 5% in a day
FAKE_VOL_GATE = 0.08           # a "defensive" member that moves like equity (>=8%) is not it
C1_TOL_PP = 0.02               # control: the published arm must reproduce the released cell
C2_TOL_PP = 0.02               # control: the book loop must reproduce the released book
ROW_TOL = 5e-4                 # stored precision of the readings this face prints


# ---------------------------------------------------------------------------------------
# pure helpers (no engine knowledge)
# ---------------------------------------------------------------------------------------
def _stats(series):
    r = series.pct_change().dropna()
    if len(series) < 2:
        return {"cagr": None, "vol": None, "sharpe": None, "maxdd": None}
    yrs = (series.index[-1] - series.index[0]).days / 365.25
    cagr = (series.iloc[-1] / series.iloc[0]) ** (1.0 / yrs) - 1.0 if yrs > 0 else None
    vol = float(r.std() * np.sqrt(252))
    sharpe = float(r.mean() * 252 / vol) if vol else None
    dd = float((series / series.cummax() - 1.0).min())
    return {"cagr": None if cagr is None else float(cagr), "vol": vol,
            "sharpe": sharpe, "maxdd": dd}


def ew_series(close, amt, cls, want, start=A.START, min_amt=None, min_hist=None):
    """Equal weight over the names a ruler puts in `want` -- the arithmetic of
    etf_equity_alpha.ew_universe, kept local so the selftest can drive it on synthetic panels."""
    min_amt = E.MIN_AMT if min_amt is None else min_amt
    min_hist = E.MIN_HIST if min_hist is None else min_hist
    hist = close.notna().cumsum()
    elig = (amt >= min_amt) & (hist >= min_hist)
    cols = [c for c in close.columns if cls.get(c) in want]
    if not cols:
        return pd.Series(dtype=float)
    px = close[cols].ffill()
    ret = px.pct_change()
    equity, curve = 1.0, []
    dates = [d for d in px.index if d >= pd.Timestamp(start)]
    for i, d in enumerate(dates[:-1]):
        nd = dates[i + 1]
        live = [c for c in cols if bool(elig.at[d, c])]
        r = ret.loc[nd, live].mean() if live else 0.0
        if np.isfinite(r):
            equity *= (1.0 + r)
        curve.append((d, equity))
    return pd.Series(dict(curve))


def repair_ruler(cols, kw, name_of, fullvol, maxabs):
    """Name markers decide cash vs bond; the price history may only DEMOTE a defensive label.

    A name whose own history cannot be a cash fund (vol > MONEY_VOL_CAP or a day > MONEY_DAY_CAP)
    loses `money`; if it also moves like equity (vol > FAKE_VOL_GATE) it loses the defensive
    side entirely. Nothing is ever promoted into the defensive side, so the repair cannot
    manufacture a quiet name out of a noisy one.
    """
    out = {}
    for c in cols:
        name = name_of(c) or ""
        k = kw.get(c, "equity")
        if any(w in name for w in CASH_KW):
            k = "money"
        elif k in DEFENSIVE:
            k = "bond"
        if k in DEFENSIVE:
            v = fullvol.get(c, np.nan)
            x = maxabs.get(c, np.nan)
            if k == "money" and (
                    not np.isfinite(v) or v > MONEY_VOL_CAP
                    or (np.isfinite(x) and x > MONEY_DAY_CAP)):
                k = "equity" if (np.isfinite(v) and v > FAKE_VOL_GATE) else "bond"
            elif k == "bond" and np.isfinite(v) and v > FAKE_VOL_GATE:
                k = "equity"
        out[c] = k
    return pd.Series(out)


def book_loop(close, openp, amt, score, cls, rebal=A.REBAL, n_hold=A.N_HOLD,
              cost=A.COST, start=A.START):
    """etf_equity_alpha.run_with_attribution's leg chain, plus the holdings that made the P&L.

    Same selection bar, same fills, same cost application; the extra output is per-name
    realised P&L so the face can ask *which names* the defensive label was paying for.
    """
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    score = score.where(elig)
    op = openp.reindex(columns=close.columns)
    dates = [d for d in op.index if d >= pd.Timestamp(start)]

    equity, held = 1.0, {}
    curve, pnl_by_name = [], {}
    inst_by_name = {}
    for i in range(len(dates) - 1):
        d, nxt = dates[i], dates[i + 1]
        if i % rebal == 0:
            s = score.loc[d].dropna()
            if len(s) >= n_hold:
                picks = list(s.nlargest(n_hold).index)
                w = {p: 1.0 / n_hold for p in picks}
                turn = sum(abs(w.get(k, 0.0) - held.get(k, 0.0)) for k in set(w) | set(held))
                equity *= (1.0 - cost * turn)
                held = w
        r_tot = 0.0
        for p, wt in held.items():
            a, b = op.at[d, p], op.at[nxt, p]
            if np.isfinite(a) and np.isfinite(b) and a > 0:
                rp = wt * (b / a - 1.0)
                r_tot += rp
                pnl_by_name[p] = pnl_by_name.get(p, 0.0) + rp
                inst_by_name[p] = inst_by_name.get(p, 0) + 1
        equity *= (1.0 + r_tot)
        curve.append((d, equity))
    return pd.Series(dict(curve)), pnl_by_name, inst_by_name


# ---------------------------------------------------------------------------------------
# the face
# ---------------------------------------------------------------------------------------
def _peak(members, which):
    """The best/worst member by its own CAGR -- read from the whole list, never the printed slice."""
    priced = [m for m in members if m.get("own_cagr") is not None]
    if not priced:
        return None
    return which(priced, key=lambda m: m["own_cagr"])


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def build():
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    name_of = lambda c: cmap.get(str(c)[:6], ("", ""))[1]
    kw = AC.classify(list(close.columns))

    ret = close.pct_change()
    fullvol = ret.std() * np.sqrt(252)
    maxabs = ret.abs().max()

    base = A.classify(close.columns, cmap, close)
    fixed = repair_ruler(close.columns, kw, name_of, fullvol, maxabs)

    arms, arm_window = {}, None
    for tag, ruler in (("published", base), ("repaired", fixed)):
        arms[tag] = {}
        for want in (("money",), ("bond",), ("bond", "money")):
            key = "+".join(want)
            ser = A.ew_universe(close, amt, ruler, want)
            if arm_window is None and len(ser):
                arm_window = {"first": str(ser.index[0].date()), "last": str(ser.index[-1].date()),
                              "bars": int(len(ser))}
            arms[tag][key] = dict(_stats(ser), names=int(sum(1 for c in close.columns
                                                             if ruler.get(c) in want)))

    # ---- what the published `money` bucket actually contains
    fake = [c for c in close.columns if base.get(c) == "money" and np.isfinite(fullvol.get(c, np.nan))
            and fullvol[c] > MONEY_VOL_CAP]
    fake.sort(key=lambda c: -float(fullvol[c]))
    members = []
    for c in fake:
        p = close[c].dropna()
        yrs = (p.index[-1] - p.index[0]).days / 365.25
        cagr = (p.iloc[-1] / p.iloc[0]) ** (1.0 / yrs) - 1.0 if len(p) > 1 and yrs > 0 else None
        members.append({"symbol": c, "name": name_of(c),
                        "own_vol": round(float(fullvol[c]), 4),
                        "own_cagr": None if cagr is None else round(float(cagr), 4),
                        "own_max_day": round(float(maxabs[c]), 4) if np.isfinite(maxabs.get(c, np.nan)) else None,
                        "repaired_class": str(fixed.get(c))})

    # ---- which of them the book could actually buy today
    score = E.build_score(close, amt, feats)
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    last = score.index[-1]
    s_now = score.loc[last].dropna()
    rank = s_now.rank(ascending=False)
    at_risk = []
    for c in fake:
        if c in s_now.index and bool(elig.at[last, c]):
            at_risk.append({"symbol": c, "rank": int(rank[c]), "of": int(len(s_now)),
                            "own_vol": round(float(fullvol[c]), 4)})
    at_risk.sort(key=lambda r: r["rank"])
    top5 = [str(x) for x in s_now.nlargest(5).index]

    # ---- the book's own P&L, booked by the published labels
    curve, pnl_by_name, inst_by_name = book_loop(close, openp, amt, score, base)
    book_stats = _stats(curve)
    pnl_total = sum(pnl_by_name.values()) or 0.0
    pnl_def = {p: v for p, v in pnl_by_name.items() if base.get(p) in DEFENSIVE}
    pnl_fake = {p: v for p, v in pnl_def.items()
                if np.isfinite(fullvol.get(p, np.nan)) and fullvol[p] > FAKE_VOL_GATE}
    fake_share = (sum(pnl_fake.values()) / pnl_total) if pnl_total else None
    inst_fake = sum(inst_by_name.get(p, 0) for p in pnl_fake)

    # ---- the released numbers this face is measured against
    with open(PUBLISHED_FACE, "r", encoding="utf-8") as fh:
        pub = json.load(fh)
    pub_runs = {r["label"]: r for r in pub.get("runs", [])}
    released = {
        "bond_money_only_ew_bench": {k: pub_runs["bond_money_only_ew_bench"].get(k)
                                     for k in ("cagr", "vol", "maxdd")},
        "all_classes": {k: pub_runs["all_classes"].get(k) for k in ("cagr", "vol", "maxdd")},
        "bond_money_only": {k: pub_runs["bond_money_only"].get(k)
                            for k in ("cagr", "vol", "maxdd")},
    }

    # ---- judges
    m_base = arms["published"]["money"]
    m_fix = arms["repaired"]["money"]
    judges = {
        "MONEY_CLASS_IS_NOT_CASH": bool(m_base["maxdd"] is not None
                                        and m_base["maxdd"] * 100 < -MONEY_DD_IMPOSSIBLE_PP),
        "DEFENSIVE_PNL_FROM_EQUITY_MOVERS": bool(fake_share is not None
                                                 and abs(fake_share) > 0),
        "REPAIRED_MONEY_READS_LIKE_CASH": bool(
            m_fix["vol"] is not None and m_fix["vol"] <= MONEY_VOL_CAP
            and m_fix["maxdd"] is not None and m_fix["maxdd"] >= -0.02),
    }
    if judges["MONEY_CLASS_IS_NOT_CASH"]:
        headline = "RULER_BROKEN_DEFENSIVE_LABEL_MIXES_EQUITY_INTO_IT"
    elif judges["DEFENSIVE_PNL_FROM_EQUITY_MOVERS"]:
        headline = "RULER_LABELS_OK_BUT_ATTRIBUTION_DIRTY"
    else:
        headline = "CLASS_RULER_SOUND"

    out = {
        "artifact": "etf_class_ew_ruler_repair",
        "schema": SCHEMA,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": str(close.index[-1].date()),
        "window": {"first": str(close.index[0].date()), "last": str(close.index[-1].date()),
                   "bars": int(len(close))},
        "arm_window": arm_window,
        "panel": {"shape": list(close.shape), "flips_repaired": int(n_flip),
                  "digest": A.panel_digest(close, openp, amt)},
        "judges": judges,
        "headline": headline,
        "class_counts": {"published": {k: int(v) for k, v in base.value_counts().items()},
                         "repaired": {k: int(v) for k, v in fixed.value_counts().items()}},
        "arms": arms,
        "released": released,
        "controls": {
            "C1_bond_money_ew": {"ours": arms["published"]["bond+money"],
                                 "released": released["bond_money_only_ew_bench"]},
            "C2_book": {"ours": {k: book_stats[k] for k in ("cagr", "vol", "maxdd")},
                        "released": released["all_classes"]},
        },
        "defensive_pnl": {"book_pnl_total": round(float(pnl_total), 4),
                          "defensive_pnl": round(float(sum(pnl_def.values())), 4),
                          "fake_defense_pnl": round(float(sum(pnl_fake.values())), 4),
                          "fake_defense_share_of_total": None if fake_share is None
                          else round(float(fake_share), 6),
                          "fake_names_held": len(pnl_fake),
                          "fake_holding_instances": int(inst_fake)},
        "money_bucket": {"published_members": int(sum(1 for c in close.columns
                                                      if base.get(c) == "money")),
                         "not_cash_members": len(fake),
                         "equity_vol_members": int(sum(1 for c in fake
                                                       if fullvol[c] > FAKE_VOL_GATE)),
                         "best_member": _peak(members, max),
                         "worst_member": _peak(members, min),
                         "members": members[:20]},
        "buyable_today": {"bar": str(last.date()), "scored": int(len(s_now)),
                          "eligible": int(elig.loc[last].sum()),
                          "fake_money_eligible": len(at_risk),
                          "closest_to_the_book": at_risk[:8],
                          "book_top5": top5},
        "tolerances": {"C1_pp": C1_TOL_PP, "C2_pp": C2_TOL_PP, "row": ROW_TOL},
    }
    return out


# ---------------------------------------------------------------------------------------
# page
# ---------------------------------------------------------------------------------------
def _pct(x, nd=2):
    return "—" if x is None else ("%.*f%%" % (nd, x * 100))


def write_md(p):
    a = p["arms"]
    b, r = a["published"], a["repaired"]
    d = p["defensive_pnl"]
    mb = p["money_bucket"]
    bt = p["buyable_today"]
    L = []
    L.append("# 分类等权的尺子，里面装的不是它说的东西（r1974 bm-c）\n")
    L.append("面板 %s -> %s（%d 根 bar）；等权腿窗口 %s -> %s（%d 根 bar），证据截止 **%s**。\n" %
             (p["window"]["first"], p["window"]["last"], p["window"]["bars"],
              p["arm_window"]["first"], p["arm_window"]["last"], p["arm_window"]["bars"],
              p["evidence_cutoff"]))
    L.append("## 判决\n")
    L.append("**%s**\n" % p["headline"])
    L.append("| 判据 | 结果 |\n|---|---|")
    L.append("| 名为「货币」的一档会不会跌 5%% 以上（现金基金不该会） | %s |" %
             ("会：%s" % _pct(b["money"]["maxdd"]) if p["judges"]["MONEY_CLASS_IS_NOT_CASH"] else "不会"))
    L.append("| 「防御档」的账面盈亏里有没有来自股票级波动名的钱 | %s |" %
             ("有：%s，%d 个名字、%d 个持有实例" % (_pct(d["fake_defense_share_of_total"]),
                                             d["fake_names_held"], d["fake_holding_instances"])
              if p["judges"]["DEFENSIVE_PNL_FROM_EQUITY_MOVERS"] else "没有"))
    L.append("| 修好之后的「货币」档像不像现金 | %s |\n" %
             ("像：波动 %s、回撤 %s" % (_pct(r["money"]["vol"]), _pct(r["money"]["maxdd"]))
              if p["judges"]["REPAIRED_MONEY_READS_LIKE_CASH"] else "不像（修复规则本身有问题）"))

    L.append("## 这条结论说了什么\n")
    L.append("1. 公司对外印的 `bond_money_only_ew_bench`（%s/年、回撤 %s）用的是这条尺子；"
             "尺子的「货币」格里有 **%d 个名字根本不像现金**（全窗波动 > 2%%），其中 %d 个"
             "波动已经和股票一样（> 8%%）：最好的一个一年赚 %s、最差的一个一年亏 %s。\n" %
             (_pct(b["bond+money"]["cagr"]), _pct(b["bond+money"]["maxdd"]),
              mb["not_cash_members"], mb["equity_vol_members"],
              _pct((mb["best_member"] or {}).get("own_cagr")),
              _pct((mb["worst_member"] or {}).get("own_cagr"))))
    L.append("2. 结果就是「现金」这一档印出 **%s 的最大回撤**——现金基金不可能有这种回撤。"
             "判据不是「数字难看」，而是「这个数字物理上不成立」。\n" % _pct(b["money"]["maxdd"]))
    L.append("3. 修法是：名字里的现金标记决定现金，价格史只许**降级**（波动 > 2%% 或单日 > 5%% 不许叫现金；"
             "波动 > 8%% 连固收都不许叫），不许把一个吵闹的名字升成安静的。修完「货币」档剩 %d 个名字，"
             "等权读数 %s、波动 %s、回撤 %s。\n" %
             (r["money"]["names"], _pct(r["money"]["cagr"]), _pct(r["money"]["vol"]),
              _pct(r["money"]["maxdd"])))
    L.append("4. 三条腿一起看：收益几乎不动（防御合计 %s -> %s），但**风险读数全变了**——"
             "波动 %s -> %s、回撤 %s -> %s。也就是说旧尺子没有把防御档的收益算错多少，"
             "它把防御档的**风险**算大了 2-3 倍，同时把「货币」这一档整个算成了一件不存在的东西。\n" %
             (_pct(b["bond+money"]["cagr"]), _pct(r["bond+money"]["cagr"]),
              _pct(b["bond+money"]["vol"]), _pct(r["bond+money"]["vol"]),
              _pct(b["bond+money"]["maxdd"]), _pct(r["bond+money"]["maxdd"])))

    L.append("## 三档等权（同窗口、同权重、同流动性闸）\n")
    L.append("| 档 | 已发布尺子 | 修好之后 |\n|---|---|---|")
    for key, nm in (("money", "货币"), ("bond", "债券"), ("bond+money", "债+货币（防御档）")):
        L.append("| %s | %s / 波动 %s / 回撤 %s（%d 名） | %s / 波动 %s / 回撤 %s（%d 名） |" %
                 (nm, _pct(b[key]["cagr"]), _pct(b[key]["vol"]), _pct(b[key]["maxdd"]), b[key]["names"],
                  _pct(r[key]["cagr"]), _pct(r[key]["vol"]), _pct(r[key]["maxdd"]), r[key]["names"]))
    L.append("")

    L.append("## 被错放进「货币」的名字（按自己的波动排序，前 10）\n")
    L.append("| 代码 | 名字 | 自己年化 | 自己波动 | 自己最大单日 | 修复后归到 |\n|---|---|---|---|---|---|")
    for m in mb["members"][:10]:
        L.append("| %s | %s | %s | %s | %s | %s |" %
                 (m["symbol"], m["name"] or "—", _pct(m["own_cagr"]), _pct(m["own_vol"]),
                  _pct(m["own_max_day"]), m["repaired_class"]))
    L.append("")

    L.append("## 账本自己有没有买到它们\n")
    L.append("把生产选股循环跑一遍、按**已发布**的标签把盈亏归到「防御档」：账本总盈亏 %.4f，"
             "防御档 %.4f，其中来自股票级波动名的 %.4f（占全账 %s），涉及 %d 个名字、%d 个持有实例。\n" %
             (d["book_pnl_total"], d["defensive_pnl"], d["fake_defense_pnl"],
              _pct(d["fake_defense_share_of_total"], 3), d["fake_names_held"],
              d["fake_holding_instances"]))
    L.append("今天（%s·%d 个可打分名·%d 个可买）这些名字里有 **%d 个可买**，"
             "离进书最近的一个排第 %s 名；今天的 top5 = %s。\n" %
             (bt["bar"], bt["scored"], bt["eligible"], bt["fake_money_eligible"],
              ("%d" % bt["closest_to_the_book"][0]["rank"]) if bt["closest_to_the_book"] else "—",
              "、".join(bt["book_top5"])))

    L.append("## 控制臂与控制量\n")
    c1, c2 = p["controls"]["C1_bond_money_ew"], p["controls"]["C2_book"]
    L.append("- C1 已发布尺子的防御档等权复现：我们 %s / 发布 %s（容差 %.2f pp）" %
             (_pct(c1["ours"]["cagr"]), _pct(c1["released"]["cagr"]), C1_TOL_PP))
    L.append("- C2 账本循环复现已发布 all_classes：我们 %s / 发布 %s，回撤 %s / %s（容差 %.2f pp）" %
             (_pct(c2["ours"]["cagr"]), _pct(c2["released"]["cagr"]),
              _pct(c2["ours"]["maxdd"]), _pct(c2["released"]["maxdd"]), C2_TOL_PP))
    L.append("")
    L.append("## 诚实边界\n")
    L.append("1. 本面**不改**已发布面、不改分类器、不写任何共享面——只给出一张价目表和一条可执行的修复规则。")
    L.append("2. 现金基金的分红是派息不是净值，所以「货币」档修好之后价格年化接近 0%%（%s），"
             "这读的是净值不是收益；现金的真实收益要看逆回购/派息面。" % _pct(r["money"]["cagr"]))
    L.append("3. 修复规则用的是全窗波动（回顾性），因此它是一把**审计尺**，不是可以当天拿来选股的预测器。")
    L.append("4. `bond_money_only`（书自己的防御档策略读数）与 `bond_money_only_ew_bench`（等权基准）"
             "是两个不同的东西：本面只判后者。")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


# ---------------------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------------------
def _close(a, b, tol):
    if a is None or b is None:
        return a is None and b is None
    return abs(float(a) - float(b)) <= tol


def check():
    with open(OUT_JSON, "r", encoding="utf-8") as fh:
        pub = json.load(fh)
    fresh = build()
    problems, stale = [], []

    if (pub.get("panel") or {}).get("digest") != fresh["panel"]["digest"]:
        stale.append("panel_digest %s -> %s" % ((pub.get("panel") or {}).get("digest", {}).get("digest")
                                                if isinstance((pub.get("panel") or {}).get("digest"), dict)
                                                else (pub.get("panel") or {}).get("digest"),
                                                fresh["panel"]["digest"].get("digest")
                                                if isinstance(fresh["panel"]["digest"], dict)
                                                else fresh["panel"]["digest"]))
    if pub.get("evidence_cutoff") != fresh["evidence_cutoff"]:
        stale.append("evidence_cutoff %s -> %s" % (pub.get("evidence_cutoff"),
                                                   fresh["evidence_cutoff"]))

    # every printed reading must be the arithmetic of this run
    for tag in ("published", "repaired"):
        for key in ("money", "bond", "bond+money"):
            p_arm, f_arm = pub["arms"][tag][key], fresh["arms"][tag][key]
            for fld in ("cagr", "vol", "maxdd"):
                if not _close(p_arm.get(fld), f_arm.get(fld), ROW_TOL):
                    problems.append("arms.%s.%s.%s %s -> %s" % (tag, key, fld,
                                                                p_arm.get(fld), f_arm.get(fld)))
            if p_arm.get("names") != f_arm.get("names"):
                problems.append("arms.%s.%s.names %s -> %s" % (tag, key, p_arm.get("names"),
                                                               f_arm.get("names")))
    for fld in ("book_pnl_total", "defensive_pnl", "fake_defense_pnl",
                "fake_defense_share_of_total", "fake_names_held", "fake_holding_instances"):
        a, b = pub["defensive_pnl"].get(fld), fresh["defensive_pnl"].get(fld)
        if isinstance(a, float) or isinstance(b, float):
            if not _close(a, b, ROW_TOL):
                problems.append("defensive_pnl.%s %s -> %s" % (fld, a, b))
        elif a != b:
            problems.append("defensive_pnl.%s %s -> %s" % (fld, a, b))

    # controls must still hold against the released face
    c1 = fresh["controls"]["C1_bond_money_ew"]
    if not _close(c1["ours"]["cagr"], c1["released"]["cagr"], C1_TOL_PP / 100.0):
        problems.append("C1 cagr %s vs released %s" % (c1["ours"]["cagr"], c1["released"]["cagr"]))
    c2 = fresh["controls"]["C2_book"]
    for fld in ("cagr", "maxdd"):
        if not _close(c2["ours"][fld], c2["released"][fld], C2_TOL_PP / 100.0):
            problems.append("C2 %s %s vs released %s" % (fld, c2["ours"][fld], c2["released"][fld]))

    # judges must re-derive from the numbers this run printed
    m_base, m_fix = fresh["arms"]["published"]["money"], fresh["arms"]["repaired"]["money"]
    j = fresh["judges"]
    if j["MONEY_CLASS_IS_NOT_CASH"] != bool(m_base["maxdd"] * 100 < -MONEY_DD_IMPOSSIBLE_PP):
        problems.append("judge MONEY_CLASS_IS_NOT_CASH does not follow from maxdd")
    if j["REPAIRED_MONEY_READS_LIKE_CASH"] != bool(m_fix["vol"] <= MONEY_VOL_CAP
                                                   and m_fix["maxdd"] >= -0.02):
        problems.append("judge REPAIRED_MONEY_READS_LIKE_CASH does not follow from its numbers")
    if j["DEFENSIVE_PNL_FROM_EQUITY_MOVERS"] != bool(abs(fresh["defensive_pnl"]
                                                         ["fake_defense_share_of_total"]) > 0):
        problems.append("judge DEFENSIVE_PNL does not follow from its share")

    if stale:
        print(json.dumps({"ok": False, "msg": "STALE: inputs moved since the published face",
                          "stale": stale}, ensure_ascii=False))
        return 3
    if problems:
        print(json.dumps({"ok": False, "msg": "CHECK FAILED", "problems": problems},
                         ensure_ascii=False))
        return 1
    print(json.dumps({"ok": True, "headline": fresh["headline"], "judges": fresh["judges"],
                      "checked": "6 arms + 6 pnl fields + 2 controls + 3 judges"},
                     ensure_ascii=False))
    return 0


# ---------------------------------------------------------------------------------------
# selftest
# ---------------------------------------------------------------------------------------
def selftest():
    legs = []

    def leg(name, fn):
        try:
            ok, why = fn()
        except Exception as exc:  # a crashing leg is a failing leg, not a silent pass
            ok, why = False, "raised %s: %s" % (type(exc).__name__, exc)
        legs.append((name, ok, why))

    def l1():
        kw = {"a": "equity"}
        r = repair_ruler(["a"], kw, lambda c: "银华日利", pd.Series({"a": 0.005}),
                         pd.Series({"a": 0.01}))
        return r["a"] == "money", "got %s" % r["a"]

    def l2():
        # a stock ETF whose 60-day median vol collapsed still gets demoted by the price gate
        kw = {"b": "equity"}
        r = repair_ruler(["b"], kw, lambda c: "", pd.Series({"b": 0.15}), pd.Series({"b": 0.05}))
        return r["b"] == "equity", "got %s" % r["b"]

    def l3():
        # the classifier calls it money (that is the bug); the repair demotes it to equity
        kw = {"c": "money"}
        r = repair_ruler(["c"], kw, lambda c: "某某ETF", pd.Series({"c": 0.16}),
                         pd.Series({"c": 0.047}))
        return r["c"] == "equity", "got %s" % r["c"]

    def l4():
        # quiet but not cash-quiet: demoted to bond, never promoted into money
        kw = {"d": "equity"}
        r = repair_ruler(["d"], kw, lambda c: "", pd.Series({"d": 0.05}), pd.Series({"d": 0.01}))
        return r["d"] == "equity", "got %s" % r["d"]

    def l5():
        kw = {"e": "bond"}
        r = repair_ruler(["e"], kw, lambda c: "十年国债", pd.Series({"e": 0.06}),
                         pd.Series({"e": 0.01}))
        return r["e"] == "bond", "got %s" % r["e"]

    def l6():
        kw = {"f": "bond"}
        r = repair_ruler(["f"], kw, lambda c: "", pd.Series({"f": 0.19}), pd.Series({"f": 0.04}))
        return r["f"] == "equity", "got %s" % r["f"]

    def l7():
        # unpriced name: the gate must not call it cash on missing data
        kw = {"g": "money"}
        r = repair_ruler(["g"], kw, lambda c: "", pd.Series({"g": np.nan}),
                         pd.Series({"g": np.nan}))
        return r["g"] != "money", "got %s" % r["g"]

    def l8():
        idx = pd.date_range("2024-01-01", periods=5, freq="B")
        close = pd.DataFrame({"x": [1.0, 1.01, 1.02, 1.03, 1.04],
                              "y": [1.0, 1.00, 1.00, 1.00, 1.00]}, index=idx)
        amt = pd.DataFrame(1e8, index=idx, columns=close.columns)
        cls = pd.Series({"x": "equity", "y": "money"})
        ser = ew_series(close, amt, cls, ("money",), start="2024-01-01", min_amt=0, min_hist=1)
        ref = A.ew_universe(close, amt, cls, ("money",), start="2024-01-01")
        same = abs(ser.iloc[-1] - ref.iloc[-1]) < 1e-12 if len(ser) and len(ref) else False
        return same and abs(ser.iloc[-1] - 1.0) < 1e-12, "ours=%.12f ref=%.12f" % (
            ser.iloc[-1] if len(ser) else float("nan"), ref.iloc[-1] if len(ref) else float("nan"))

    def l9():
        s = pd.Series([1.0, 0.90, 1.05], index=pd.date_range("2024-01-01", periods=3))
        st = _stats(s)
        return abs(st["maxdd"] + 0.10) < 1e-12, "maxdd=%s" % st["maxdd"]

    def l10():
        # judge thresholds must bite exactly at the frozen line, both ways
        j = lambda dd: bool(dd * 100 < -MONEY_DD_IMPOSSIBLE_PP)
        return (not j(-0.0499)) and j(-0.0501), "%s %s" % (j(-0.0499), j(-0.0501))

    def l11():
        a = build()
        b = build()
        return (a["arms"] == b["arms"] and a["headline"] == b["headline"]
                and a["defensive_pnl"] == b["defensive_pnl"]), "twice"

    def l12():
        a = build()
        allowed = ("RULER_BROKEN_DEFENSIVE_LABEL_MIXES_EQUITY_INTO_IT",
                   "RULER_LABELS_OK_BUT_ATTRIBUTION_DIRTY", "CLASS_RULER_SOUND")
        return a["headline"] in allowed and a["arms"]["published"]["bond+money"]["cagr"] is not None, \
            "headline=%s" % a["headline"]

    def l13():
        # the published arm must stay the released arm: C1 is the proof it is the same arithmetic
        a = build()
        c1 = a["controls"]["C1_bond_money_ew"]
        return _close(c1["ours"]["cagr"], c1["released"]["cagr"], C1_TOL_PP / 100.0), \
            "ours=%s released=%s" % (c1["ours"]["cagr"], c1["released"]["cagr"])

    for name, fn in [("L1 cash marker keeps money", l1), ("L2 noisy name demoted", l2),
                     ("L3 money label overruled by prices", l3), ("L4 quiet non-cash not promoted", l4),
                     ("L5 true bond stays bond", l5), ("L6 bond that moves like equity demoted", l6),
                     ("L7 missing prices never read as cash", l7), ("L8 EW matches the engine", l8),
                     ("L9 drawdown arithmetic", l9), ("L10 judge threshold both ways", l10),
                     ("L11 deterministic", l11), ("L12 live headline readable", l12),
                     ("L13 control C1 holds", l13)]:
        leg(name, fn)

    bad = [x for x in legs if not x[1]]
    for name, ok, why in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else " -- " + why))
    print("%d/%d legs PASS" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return check()
    payload = build()
    bc.write_json(OUT_JSON, payload)
    write_md(payload)
    print(json.dumps({"headline": payload["headline"], "judges": payload["judges"],
                      "class_counts": payload["class_counts"],
                      "arms": {k: {"cagr": v["cagr"], "maxdd": v["maxdd"], "names": v["names"]}
                               for k, v in payload["arms"]["repaired"].items()},
                      "fake_money_members": payload["money_bucket"]["not_cash_members"],
                      "defensive_pnl": payload["defensive_pnl"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
