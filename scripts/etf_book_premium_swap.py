"""If the sheet refuses a stretched leg, what does it buy instead -- and what does that cost?

r1772 priced the friction on the 2026-11-16 ticket: one leg (159655) sat 6.746% over the
basket it tracks, i.e. 5,821 of the 86,286 CNY order was premium, while the other four sat
inside +-1%. The page could only say "stretched". The operator's next question is not a
label, it is a decision: **refuse that leg and buy what?** -- and the second half, which
keeps the first half honest: **what do we give up by refusing it?**

Both halves are derivable from data already on disk:

  * SUBSTITUTE -- for every stretched leg (premium > PREMIUM_SWAP_PP) walk the same decision
    bar's ranked names and offer the best same-class alternative that is not already a leg.
    Same class is load-bearing: swapping a cross-border fund for a domestic equity fund is
    not a substitution, it is a different bet wearing the same order form.
  * PRICE OF THE RULE -- the alternative always ranks lower, and that gap is measured in
    the book's own composite-score units, then converted with the panel's own
    cross-sectional slope of forward HORIZON-bar return on that score. The give-up is
    capped by a frozen constant; a swap that costs more expected return than the cap is
    refused even when it is much cheaper to buy.

Two currencies, never added: the premium saving is a ONE-OFF purchase discount (CNY at the
order), the give-up is an EXPECTED RETURN (pp per year). A face that summed them would be
inventing an exchange rate between them, so both are printed and neither is netted.

What this face deliberately does NOT do: answer "what would the rule have earned since
2020". Premium history on disk covers only the nine symbols that have disclosed-NAV files
(data/etf_premium/nav_history), so the historical arm cannot be priced without inventing
the very series it would be measured on. The verdict words therefore describe TODAY's
sheet, and the give-up is bounded by a measured slope rather than asserted.

  python scripts/etf_book_premium_swap.py sheet        # today's swap sheet (default)
  python scripts/etf_book_premium_swap.py --check      # re-derive the published verdicts
  python scripts/etf_book_premium_swap.py --selftest

Outputs:
  results/etf_book_premium_swap.json
  research/ETF_BOOK_PREMIUM_SWAP.md

Exploratory: not a verdict on the book, not investment advice, no ledger booking.
"""
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts import etf_composite_pf as F          # noqa: E402
from scripts.etf_asset_class import classify       # noqa: E402

RESULTS = os.path.join(ROOT, "results")
OUT_JSON = os.path.join(RESULTS, "etf_book_premium_swap.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_PREMIUM_SWAP.md")
ORDER_DIR = os.path.join(RESULTS, "etf_book_order")
SNAP_DIR = os.path.join(ROOT, "data", "etf_premium", "snap")

# --- frozen before the first run, echoed into the payload -------------------------------
PREMIUM_SWAP_PP = 3.0        # a leg is "stretched" above this premium vs its own basket
MIN_SAVING_PP = 1.0          # a twin has to be at least this much cheaper to be a twin
MAX_GIVEUP_PP_YR = 2.0       # expected-return give-up a substitution may spend, pp per year
HORIZON = 20                 # holding horizon of the book's decision grid (bars)
MIN_CROSS_SECTION = 30       # names required for a cross-sectional slope to count
MONTH_BARS = 252.0 / HORIZON

# Asset class is the coarse cut; for the cross-border complex it is NOT enough, because a
# US large-cap fund and a Japan fund are both "crossborder" and swapping one for the other
# is a different bet. This frozen token table is the second cut, applied only when both the
# leg and the candidate carry a name.
#
# Order matters, and two entries are traps the first run stepped into: `标普` alone is the US
# S&P 500, but `标普A股红利ETF华宝` (562060) holds A-shares under an S&P licence -- the naive
# table offered it at -0.43% as a twin for a US leg; and `中国互联` is offshore China (ADRs),
# not a domestic fund. Domestic markers are therefore checked BEFORE every foreign token,
# and the ADR / Hong Kong tokens before the generic `中国`.
DOMESTIC_TOKENS = ("A股", "沪深", "中证", "上证", "深证", "创业板", "科创", "红利低波")
MARKET_TOKENS = (
    ("中概", "cn_adr"), ("中国互联", "cn_adr"), ("海外互联", "cn_adr"),
    ("港股", "hk"), ("恒生", "hk"), ("香港", "hk"), ("H股", "hk"), ("国企", "hk"),
    ("日经", "jp"), ("日本", "jp"), ("东证", "jp"),
    ("标普", "us_sp500"), ("纳指", "us_nasdaq"), ("纳斯达克", "us_nasdaq"),
    ("道琼斯", "us_dow"), ("油气", "us_energy"),
    ("德国", "de"), ("法国", "fr"), ("越南", "vn"), ("印度", "in"), ("沙特", "sa"),
)


def market_of(name):
    """Underlying market token from a fund name, or None when no token fires."""
    if not name:
        return None
    s = str(name)
    for tok in DOMESTIC_TOKENS:
        if tok in s:
            return "cn_a"
    if "中国" in s and "互联" not in s:
        return "cn_a"
    for tok, mkt in MARKET_TOKENS:
        if tok in s:
            return mkt
    return None


# ------------------------------------------------------------------ inputs
def latest_ticket():
    path = sorted(glob.glob(os.path.join(ORDER_DIR, "TICKET-*.json")))
    if not path:
        raise SystemExit("no ticket on disk under results/etf_book_order")
    with open(path[-1], "r", encoding="utf-8") as f:
        return json.load(f), path[-1]


def load_premium_snapshot(asof):
    """(symbol -> premium_pct in percent, symbol -> fund name, path) for the session."""
    path = os.path.join(SNAP_DIR, "%s.csv" % asof)
    if not os.path.exists(path):
        return {}, {}, path
    df = pd.read_csv(path, dtype={"code": str})
    if "code" not in df.columns or "premium_pct" not in df.columns:
        return {}, {}, path
    has_name = "name" in df.columns
    out, names = {}, {}
    for i, (code, prem) in enumerate(zip(df["code"], df["premium_pct"])):
        s = str(code).strip().zfill(6)
        if has_name:
            nm = df["name"].iloc[i]
            if isinstance(nm, str) and nm.strip():
                names[s] = nm.strip()
        try:
            v = float(prem)
        except (TypeError, ValueError):
            continue
        if np.isfinite(v):
            out[s] = v
    return out, names, path


def panel_rank():
    close, openp, amt, feats = F.build_panel()
    score = F.build_score(close, amt, feats)
    last = score.index[-1]
    classes = classify(list(close.columns))
    return close, score, last, classes


def score_slope(close, score, horizon=HORIZON):
    """Cross-sectional return per 1.0 composite-score unit over one horizon, pooled.

    Only non-overlapping decision bars are used (every h-th bar), so the slope is not the
    same move counted h times. Reported as the median across those bars.
    """
    px = close.ffill()
    fwd = px.shift(-horizon) / px - 1.0
    rows = []
    for d in score.index[::horizon]:
        if d not in fwd.index:
            continue
        s, r = score.loc[d], fwd.loc[d]
        m = s.notna() & r.notna()
        n = int(m.sum())
        if n < MIN_CROSS_SECTION:
            continue
        ss = s[m].to_numpy(dtype=float)
        rr = r[m].to_numpy(dtype=float)
        if ss.std() <= 0:
            continue
        slope = float(np.cov(ss, rr, bias=True)[0, 1] / np.var(ss))
        rows.append({"bar": str(pd.Timestamp(d).date()), "slope": slope,
                     "corr": float(np.corrcoef(ss, rr)[0, 1]), "n": n})
    if not rows:
        return {"status": "NO_CROSS_SECTION", "bars": 0}
    slopes = np.array([r["slope"] for r in rows], dtype=float)
    med = float(np.median(slopes))
    return {
        "status": "MEASURED",
        "bars": len(rows),
        "horizon_bars": horizon,
        "slope_median_per_horizon": med,
        "slope_annualised": float(med * MONTH_BARS),
        "corr_median": float(np.median([r["corr"] for r in rows])),
        "n_median": int(np.median([r["n"] for r in rows])),
        "sample_tail": rows[-5:],
    }


# ------------------------------------------------------------------ the rule
def _sym(s):
    """6-digit bare code for a real ticker; fixtures keep their own names."""
    t = str(s).strip()
    return t.zfill(6) if t.isdigit() else t


def decide_leg(leg, prem, legs, ranked, classes, slope_per_bar):
    """One leg -> one word plus the numbers behind it. Pure function, used by --check too."""
    sym = _sym(leg["symbol"])
    out = {
        "symbol": sym,
        "class": leg.get("class"),
        "amount_cny": float(leg.get("amount") or 0.0),
        "premium_pct": None if prem is None else float(prem),
        "premium_cny": None if prem is None else float(leg.get("amount") or 0.0) * float(prem) / 100.0,
        "stretched": None if prem is None else bool(float(prem) > PREMIUM_SWAP_PP),
        "verdict": None,
        "candidate": None,
    }
    out["leg_market"] = market_of(NAME_BY_SYMBOL.get(sym))
    if prem is None:
        out["verdict"] = "UNPRICED"
        out["note"] = "no premium row for this leg in the session snapshot -- cannot call it cheap or expensive"
        return out
    if not float(prem) > PREMIUM_SWAP_PP:
        out["verdict"] = "NOT_STRETCHED"
        out["note"] = "inside the %.1f pp threshold" % PREMIUM_SWAP_PP
        return out

    leg_class = leg.get("class")
    leg_market = market_of(NAME_BY_SYMBOL.get(sym))
    pool = []
    for cand, score in ranked.items():
        c = _sym(cand)
        if c == sym or c in legs:
            continue
        if classes.get(cand) != leg_class:
            continue
        pool.append((float(score), c))
    if not pool:
        out["verdict"] = "NO_CHEAPER_TWIN"
        out["note"] = "no same-class name outside the current legs at this decision bar"
        return out
    pool.sort(reverse=True)

    priced, other_markets = [], []
    for score, c in pool:
        cp = PREM_BY_SYMBOL.get(c)
        if cp is None or cp > float(prem) - MIN_SAVING_PP:
            continue
        cmkt = market_of(NAME_BY_SYMBOL.get(c))
        # second cut: when both sides carry a name, the underlying market has to be the same
        if leg_market is not None and cmkt != leg_market:
            other_markets.append((score, c, cp, cmkt))
            continue
        priced.append((score, c, cp, cmkt))
    if not priced:
        if other_markets:
            out["verdict"] = "NO_FAITHFUL_TWIN"
            other_markets.sort(key=lambda r: r[2])
            s2, c2, p2, m2 = other_markets[0]
            out["different_bet"] = {"symbol": c2, "market": m2, "leg_market": leg_market,
                                    "premium_pct": p2, "premium_saving_pp": float(prem) - p2}
            out["note"] = ("the only cheaper same-class names are in other markets (%s vs %s) -- "
                           "that is a different bet, not a substitution" % (m2, leg_market))
        else:
            out["verdict"] = "NO_CHEAPER_TWIN"
            out["note"] = ("nothing in the leg's own market is %.1f pp cheaper today: the whole "
                           "complex is paying the same premium" % MIN_SAVING_PP)
        out["pool_size"] = len(pool)
        out["pool_priced"] = 0
        out["pool_other_market"] = len(other_markets)
        return out

    score, cand, cprem, cmkt = priced[0]
    gap = float(ranked.get(sym, np.nan)) - score
    give_up = gap * slope_per_bar * MONTH_BARS * 100.0 if np.isfinite(gap) else None
    saving_pp = float(prem) - cprem
    out["candidate"] = {
        "symbol": cand,
        "class": leg_class,
        "market": cmkt,
        "premium_pct": cprem,
        "premium_cny": float(leg.get("amount") or 0.0) * cprem / 100.0,
        "premium_saving_pp": saving_pp,
        "premium_saving_cny": float(leg.get("amount") or 0.0) * saving_pp / 100.0,
        "score": score,
        "score_gap": None if not np.isfinite(gap) else float(gap),
        "giveup_pp_per_year": None if give_up is None else float(give_up),
        "pool_priced": len(priced),
        "pool_size": len(pool),
        "pool_other_market": len(other_markets),
    }
    if give_up is None:
        out["verdict"] = "UNPRICED"
        out["note"] = "leg has no score at this bar, so the give-up cannot be priced"
        return out
    if float(give_up) > MAX_GIVEUP_PP_YR:
        out["verdict"] = "HOLD_STRETCHED"
        out["note"] = ("the twin is %.2f pp cheaper to buy but ranks far enough below that the "
                       "expected give-up %.2f pp/yr exceeds the %.2f pp/yr cap -- paying the "
                       "premium is the cheaper mistake" % (saving_pp, give_up, MAX_GIVEUP_PP_YR))
        return out
    out["verdict"] = "SWAP_ADVISED"
    out["note"] = ("%.2f pp cheaper to buy (%.0f CNY on this order) for %.2f pp/yr of expected "
                   "return" % (saving_pp, out["candidate"]["premium_saving_cny"], give_up))
    return out


PREM_BY_SYMBOL = {}   # set by sheet(); kept module-level so decide_leg stays pure
NAME_BY_SYMBOL = {}   # same, for the market cut


def face_verdict(legs_out):
    words = [r["verdict"] for r in legs_out]
    if any(w == "SWAP_ADVISED" for w in words):
        return "SWAP_ADVISED"
    if any(w == "HOLD_STRETCHED" for w in words):
        return "HOLD_STRETCHED"
    if any(w == "NO_FAITHFUL_TWIN" for w in words):
        return "NO_FAITHFUL_TWIN"
    if all(w == "NOT_STRETCHED" for w in words):
        return "NO_STRETCHED_LEG"
    if any(w == "UNPRICED" for w in words):
        return "UNPRICED"
    return "NO_CHEAPER_TWIN"


# ------------------------------------------------------------------ sheet
def premium_complex_census(classes):
    """How wide is the premium? Per asset class, and per market inside the cross-border one.

    This is the number that decides whether a substitution exists at all: if a leg's own
    market is uniformly expensive, "buy the cheaper twin" is not an available action.
    """
    by_class, by_market = {}, {}
    for sym, prem in PREM_BY_SYMBOL.items():
        cls = classes.get(sym)
        if cls is None:
            continue
        d = by_class.setdefault(cls, [])
        d.append(prem)
        if cls == "crossborder":
            mkt = market_of(NAME_BY_SYMBOL.get(sym)) or "unmapped"
            by_market.setdefault(mkt, []).append(prem)

    def summarise(vals):
        a = np.asarray(vals, dtype=float)
        return {"n": int(a.size), "median_pct": round(float(np.median(a)), 3),
                "share_above_threshold": round(float((a > PREMIUM_SWAP_PP).mean()), 4),
                "p90_pct": round(float(np.percentile(a, 90)), 3),
                "min_pct": round(float(a.min()), 3), "max_pct": round(float(a.max()), 3)}

    return {
        "by_class": {k: summarise(v) for k, v in sorted(by_class.items())},
        "crossborder_by_market": {k: summarise(v) for k, v in sorted(by_market.items())},
    }


def sheet():
    global PREM_BY_SYMBOL, NAME_BY_SYMBOL
    ticket, tpath = latest_ticket()
    order = (ticket.get("ticket") or {}).get("order") or []
    if not order:
        raise SystemExit("ticket carries no order rows: %s" % tpath)
    asof = ticket.get("as_of") or ticket.get("evidence_cutoff")
    prem, names, snap_path = load_premium_snapshot(asof)
    PREM_BY_SYMBOL = prem
    NAME_BY_SYMBOL = names
    close, score, last, classes = panel_rank()
    ranked = score.loc[last].dropna()
    slope = score_slope(close, score)
    slope_per_bar = slope.get("slope_median_per_horizon")
    if slope_per_bar is None:
        slope_per_bar = 0.0

    leg_syms = set()
    for r in order:
        leg_syms.add(_sym(r["symbol"]))
    legs = [decide_leg(r, prem.get(_sym(r["symbol"])), leg_syms, ranked, classes,
                       slope_per_bar) for r in order]
    complex_census = premium_complex_census(classes)

    payload = {
        "face": "etf_book_premium_swap",
        "ticket": os.path.relpath(tpath, ROOT).replace("\\", "/"),
        "as_of": asof,
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "decision_bar": str(pd.Timestamp(last).date()),
        "snapshot": os.path.relpath(snap_path, ROOT).replace("\\", "/"),
        "snapshot_loaded": bool(prem),
        "snapshot_symbols": len(prem),
        "criteria": {
            "premium_swap_pp": PREMIUM_SWAP_PP,
            "min_saving_pp": MIN_SAVING_PP,
            "max_giveup_pp_per_year": MAX_GIVEUP_PP_YR,
            "horizon_bars": HORIZON,
            "min_cross_section": MIN_CROSS_SECTION,
        },
        "law": {
            "currencies": "premium saving = one-off CNY at the order; give-up = expected return pp/yr; never added",
            "class": "a twin must share the leg's asset class -- otherwise it is a different bet",
            "market": "when both sides carry a name the underlying market must match too; the token table is frozen",
            "history": "no historical arm: disclosed-NAV history covers 9 symbols only",
        },
        "score_slope": slope,
        "premium_census": complex_census,
        "legs": legs,
        "verdict": face_verdict(legs),
    }
    payload["totals"] = {
        "legs": len(legs),
        "stretched_legs": sum(1 for r in legs if r.get("stretched")),
        "net_premium_cny": round(sum(r["premium_cny"] or 0.0 for r in legs), 1),
        "swap_saving_cny": round(sum((r.get("candidate") or {}).get("premium_saving_cny") or 0.0
                                     for r in legs), 1),
        "swaps_advised": sum(1 for r in legs if r["verdict"] == "SWAP_ADVISED"),
        "faithful_twin_missing": sum(1 for r in legs if r["verdict"] == "NO_FAITHFUL_TWIN"),
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    write_md(payload, os.path.relpath(tpath, ROOT).replace("\\", "/"))
    print(json.dumps({k: payload[k] for k in ("verdict", "totals", "as_of", "decision_bar")},
                     ensure_ascii=False))
    return payload


def write_md(p, tpath):
    L = []
    A = L.append
    A("# ETF 复合书 —— 溢价换腿规则（%s）" % p["as_of"])
    A("")
    A("问题来自 r1772：票面上 159655 比它自己的篮子贵 6.75%，86,286 元的订单里 5,821 元是溢价，")
    A("页面只能说「stretched」。本轮把这句话变成一条有判据的规则，并且**同时量出这条规则的价钱**。")
    A("")
    A("## 判据（冻在代码常量里，随载荷回显）")
    A("")
    A("| 项 | 值 | 读法 |")
    A("|---|---|---|")
    A("| 溢价门槛 | %.1f pp | 超过才算 stretched，等于不算 |" % PREMIUM_SWAP_PP)
    A("| 最小省幅 | %.1f pp | 替代腿至少要便宜这么多，否则不叫替代 |" % MIN_SAVING_PP)
    A("| 放弃上限 | %.2f pp/年 | 换腿要付的预期收益代价超过这条线就不换 |" % MAX_GIVEUP_PP_YR)
    A("| 持有窗 | %d 根 bar | 与书的决策网格一致 |" % HORIZON)
    A("| 同类 | 资产类别 **且** 底层市场 | 同类别不够：标普腿换成日经腿不是替代，是换注 |")
    A("")
    A("**两种货币不相加**：省下的溢价是下单时的一次性 CNY，放弃的是每年 pp 的预期收益。")
    A("把它们加成「净值」等于凭空发明一个汇率，所以两面并排印、不合并。")
    A("")
    words = {
        "SWAP_ADVISED": "有同市场更便宜的腿，且换过去的预期代价在门槛内 —— 换。",
        "HOLD_STRETCHED": "同市场只找到便宜不多的腿，省下的溢价买不回放弃的分数 —— 付溢价是更便宜的错。",
        "NO_FAITHFUL_TWIN": "更便宜的同类腿全在别的市场 —— 那不是替代，是换注。",
        "NO_CHEAPER_TWIN": "同市场里没有便宜 %.1f pp 以上的同类腿。" % MIN_SAVING_PP,
        "NO_STRETCHED_LEG": "今日票面没有超过门槛的腿。",
        "UNPRICED": "有腿缺溢价读数，本面不对它下判断。",
    }
    A("**本轮判决：%s** —— %s" % (p["verdict"], words.get(p["verdict"], p["verdict"])))
    A("")
    A("## 今日票面逐腿")
    A("")
    A("| 腿 | 类别 | 市场 | 金额 | 溢价% | 溢价 CNY | 判定 |")
    A("|---|---|---|---|---|---|---|")
    for r in p["legs"]:
        prem = "—" if r["premium_pct"] is None else "%.3f" % r["premium_pct"]
        cny = "—" if r["premium_cny"] is None else "%.0f" % r["premium_cny"]
        A("| %s | %s | %s | %.0f | %s | %s | **%s** |"
          % (r["symbol"], r["class"], r.get("leg_market") or "—", r["amount_cny"], prem, cny, r["verdict"]))
    A("")
    A("## 溢价不是某只基金的意外，是整个跨境复合体（%s）" % p["as_of"])
    A("")
    cen = p.get("premium_census") or {}
    by_mkt = cen.get("crossborder_by_market") or {}
    if by_mkt:
        A("| 市场 | 只数 | 溢价中位 | 超门槛占比 | p90 | 最低 | 最高 |")
        A("|---|---|---|---|---|---|---|")
        for mkt, s in sorted(by_mkt.items(), key=lambda kv: -kv[1]["median_pct"]):
            A("| %s | %d | %.2f%% | %.0f%% | %.2f%% | %.2f%% | %.2f%% |"
              % (mkt, s["n"], s["median_pct"], s["share_above_threshold"] * 100.0,
                 s["p90_pct"], s["min_pct"], s["max_pct"]))
        A("")
        A("读法：如果某只腿所在市场整片都在门槛以上，「换一只更便宜的同类」就不是一个可执行的动作——")
        A("因为那只更便宜的腿不在同一个市场里。这正是本面今天的结论（见逐腿判定列与下表）。")
        A("")
    others = [(r["symbol"], r["different_bet"]) for r in p["legs"] if r.get("different_bet")]
    A("## 换腿候选")
    A("")
    if others:
        A("没有同市场的替代腿，但有**别市场**的便宜腿。它们被明确标成「换注」而不是「替代」：")
        A("")
        for sym, d in others:
            A("* %s（%s）→ %s（%s）：便宜 %.2f pp。**这不是替代**——底层标的不同，换过去是改赌注，"
              "要按新赌注重新过门（类别/宽基/因子分全部重算）。"
              % (sym, d["leg_market"], d["symbol"], d["market"], d.get("premium_saving_pp") or 0.0))
        A("")
    any_cand = False
    for r in p["legs"]:
        c = r.get("candidate")
        if not c:
            continue
        any_cand = True
        A("### %s → %s（同市场 %s）" % (r["symbol"], c["symbol"], c.get("market") or "—"))
        A("")
        A("* 买价：%.3f%% → %.3f%%，省 **%.2f pp = %.0f 元**（同类别 %s）"
          % (r["premium_pct"], c["premium_pct"], c["premium_saving_pp"],
             c["premium_saving_cny"], c["class"]))
        A("* 打分：%.3f → %.3f，差 %.3f；按面板自己的横截面斜率折成 **%.2f pp/年**"
          "（负值＝替代腿反而更靠前，不是放弃而是白捡）"
          % (c["score"] + c["score_gap"], c["score"], c["score_gap"], c["giveup_pp_per_year"]))
        A("* 同类候选 %d 只，其中 %d 只比现腿便宜 %.1f pp 以上（另外 %d 只在别的市场，不计入）"
          % (c["pool_size"], c["pool_priced"], MIN_SAVING_PP, c.get("pool_other_market") or 0))
        A("")
    if not any_cand:
        A("（今日没有可执行（同类别且同市场）的更便宜腿——理由见逐腿判定列。）")
        A("")
    sl = p["score_slope"]
    A("## 打分的价钱从哪来（面板自己的斜率）")
    A("")
    if sl.get("status") == "MEASURED":
        A("* 横截面斜率（1.0 个复合分 → %d 根 bar 的收益）：中位 %.5f，年化 **%.2f%%**，横截面样本中位 %d 只"
          % (sl["horizon_bars"], sl["slope_median_per_horizon"], sl["slope_annualised"] * 100.0, sl["n_median"]))
        A("* 用 %d 个不重叠决策 bar 估的（每 %d 根 bar 取一个，避免同一个动作被数 %d 遍）"
          % (sl["bars"], sl["horizon_bars"], sl["horizon_bars"]))
        A("* 中位秩相关 %.4f —— 分数与下一段收益的关系是弱的，所以「放弃多少分」必须乘这条斜率才成钱" % sl["corr_median"])
    else:
        A("* 斜率测不出来（%s），因此放弃值不印——不印比编一个强。" % sl.get("status"))
    A("")
    A("## 这张面没做的事")
    A("")
    A("* **没有历史臂**：盘上带披露净值的标的只有 9 只，`data/etf_premium/nav_history` 之外没有溢价序列，")
    A("  所以「这条规则 2020 年以来值多少钱」在这个面板上无法诚实回答。写一个从 7 天快照外推的数字，")
    A("  正是这本书一直拒绝的那种数。要答它，需要前向积累溢价历史，或把净值抓取扩到全宇宙（P1 级决定）。")
    A("* **没有把两种货币相加**，见上。")
    A("* **没有改票**：本面只印规则与候选，订单票的重定价归 `etf_book_order`。")
    A("* **市场 token 是一张冻结词表**，不是基金公司披露的底层指数；词表没命中的名字一律 `None`，")
    A("  那时判定退回到「只看类别」，宁可粗也不猜。")
    A("")
    A("数据面：告票 `%s`，溢价快照 `%s`（%d 只），决策 bar `%s`，证据截止 `%s`。"
      % (tpath, p["snapshot"], p["snapshot_symbols"], p["decision_bar"], p["evidence_cutoff"]))
    A("")
    A("探索性：不是对这本书的判决，不是投资建议，不记账。")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


# ------------------------------------------------------------------ check
def check():
    """Re-derive the published verdicts from the INPUTS (ticket + snapshot CSV).

    What it re-derives: premiums, premium CNY, stretched flags, and every verdict word the
    frozen rule can decide from those numbers plus the published score gaps. What it does
    NOT do: re-run the ranking (60 s of panel build). That boundary is printed rather than
    hidden -- a check that quietly skipped half the face and printed one green word would be
    the "self-consistent green" defect this book has already convicted twice.
    """
    if not os.path.exists(OUT_JSON):
        print(json.dumps({"ok": False, "problem": "no published face on disk"}))
        return 2
    with open(OUT_JSON, "r", encoding="utf-8") as f:
        pub = json.load(f)
    problems = []
    crit = pub.get("criteria") or {}
    for k, want in (("premium_swap_pp", PREMIUM_SWAP_PP), ("min_saving_pp", MIN_SAVING_PP),
                    ("max_giveup_pp_per_year", MAX_GIVEUP_PP_YR), ("horizon_bars", HORIZON)):
        if crit.get(k) != want:
            problems.append("criteria %s = %r but the code froze %r" % (k, crit.get(k), want))
    ticket, _ = latest_ticket()
    asof = ticket.get("as_of") or ticket.get("evidence_cutoff")
    # r2159: the ticket moving is drift, not a wrong number.  Without this word the chain
    # never buys the rebuild and this face freezes on the previous session (r1934 class).
    moved = []
    if pub.get("as_of") != asof:
        moved.append("the ticket moved to %s (this face was priced on %s)"
                     % (asof, pub.get("as_of")))
    prem, names, snap_path = load_premium_snapshot(asof)
    if not prem:
        problems.append("snapshot missing for %s (%s)" % (asof, snap_path))
    order = {_sym(r["symbol"]): r for r in (ticket.get("ticket") or {}).get("order") or []}
    for row in pub.get("legs") or []:
        sym = row["symbol"]
        src = order.get(sym)
        if src is None:
            problems.append("%s is not on the ticket any more" % sym)
            continue
        want = prem.get(sym)
        if (want is None) != (row["premium_pct"] is None):
            problems.append("%s premium availability drifted (snapshot %r vs face %r)"
                            % (sym, want, row["premium_pct"]))
        elif want is not None and abs(want - row["premium_pct"]) > 1e-9:
            problems.append("%s premium %.6f on the face but %.6f in the snapshot" % (sym, row["premium_pct"], want))
        if row["premium_pct"] is not None:
            want_cny = float(src.get("amount") or 0.0) * row["premium_pct"] / 100.0
            if abs(want_cny - (row["premium_cny"] or 0.0)) > 0.05:
                problems.append("%s premium CNY %.2f vs re-derived %.2f" % (sym, row["premium_cny"] or 0.0, want_cny))
            stretched = row["premium_pct"] > PREMIUM_SWAP_PP
            if bool(row.get("stretched")) != stretched:
                problems.append("%s stretched flag disagrees with the threshold" % sym)
            if not stretched and row["verdict"] != "NOT_STRETCHED":
                problems.append("%s is inside the threshold but the word is %s" % (sym, row["verdict"]))
        else:
            if row["verdict"] != "UNPRICED":
                problems.append("%s has no premium but the word is %s" % (sym, row["verdict"]))
        c = row.get("candidate")
        if c:
            if c.get("class") != row.get("class"):
                problems.append("%s twin class %s != leg class %s" % (sym, c.get("class"), row.get("class")))
            if c["symbol"] in order:
                problems.append("%s twin %s is already a leg of the same ticket" % (sym, c["symbol"]))
            if c["premium_pct"] > row["premium_pct"] - MIN_SAVING_PP + 1e-12:
                problems.append("%s twin is not %.1f pp cheaper" % (sym, MIN_SAVING_PP))
            if row.get("leg_market") and c.get("market") != row["leg_market"]:
                problems.append("%s twin market %r != leg market %r -- that is a different bet"
                                % (sym, c.get("market"), row["leg_market"]))
            if row["verdict"] == "SWAP_ADVISED" and c["giveup_pp_per_year"] > MAX_GIVEUP_PP_YR:
                problems.append("%s advised above the give-up cap" % sym)
            if row["verdict"] == "HOLD_STRETCHED" and c["giveup_pp_per_year"] <= MAX_GIVEUP_PP_YR:
                problems.append("%s held although inside the cap" % sym)
        if row["verdict"] == "NO_FAITHFUL_TWIN":
            d = row.get("different_bet") or {}
            if d and d.get("market") == row.get("leg_market"):
                problems.append("%s says no faithful twin but its different-bet is in the same market" % sym)
            if d and not (d.get("premium_saving_pp") or 0.0) > MIN_SAVING_PP:
                problems.append("%s prints a different-bet that is not actually cheaper" % sym)
    words = [r["verdict"] for r in pub.get("legs") or []]
    if pub.get("verdict") != face_verdict(pub.get("legs") or []):
        problems.append("face verdict %r does not follow from the legs %r" % (pub.get("verdict"), words))
    if moved and problems:
        problems = ["STALE " + m for m in moved] + [
            "these followed the ticket: " + p for p in problems]
    out = {"ok": not problems, "problems": problems, "verdict": pub.get("verdict"),
           "moved_inputs": moved,
           "re_derived_from_inputs": ["premium_pct", "premium_cny", "stretched", "verdict words", "face verdict"],
           "not_re_derived": ["ranking scores (panel build ~60s)", "score slope"]}
    print(json.dumps(out, ensure_ascii=False))
    return 0 if not problems else 2


# ------------------------------------------------------------------ selftest
def selftest():
    global PREM_BY_SYMBOL, NAME_BY_SYMBOL
    ok = 0
    total = 0

    def leg(verdict, cond, label):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL %s -> %r" % (label, verdict))

    classes = {"AAA": "equity", "BBB": "equity", "CCC": "crossborder", "DDD": "equity"}
    ranked = {"AAA": 0.90, "BBB": 0.70, "CCC": 0.95, "DDD": 0.40}
    legs = {"AAA"}
    slope = 0.002   # 0.2% of return per 1.0 score unit per horizon bar

    # L1 boundary: exactly at the threshold is NOT stretched (the threshold is >)
    PREM_BY_SYMBOL = {"AAA": PREMIUM_SWAP_PP}
    r = decide_leg({"symbol": "AAA", "class": "equity", "amount": 100000.0}, PREMIUM_SWAP_PP, legs, ranked, classes, slope)
    leg(r["verdict"], r["verdict"] == "NOT_STRETCHED", "L1 threshold is strict")

    # L2 a stretched leg gets a same-class twin, never a different class
    PREM_BY_SYMBOL = {"AAA": 8.0, "BBB": 0.5, "CCC": 0.1}
    r = decide_leg({"symbol": "AAA", "class": "equity", "amount": 100000.0}, 8.0, legs, ranked, classes, slope)
    leg(r, r["candidate"] and r["candidate"]["symbol"] == "BBB", "L2 twin is same class (CCC is cheaper but crossborder)")

    # L3 the twin must be at least MIN_SAVING_PP cheaper (BBB is half a pp cheaper; DDD,
    # the only genuinely cheaper equity name, carries no premium row -> unpriced, not free)
    PREM_BY_SYMBOL = {"AAA": 8.0, "BBB": 8.0 - MIN_SAVING_PP / 2.0}
    r = decide_leg({"symbol": "AAA", "class": "equity", "amount": 100000.0}, 8.0, legs, ranked, classes, slope)
    leg(r, r["verdict"] == "NO_CHEAPER_TWIN", "L3 half-saving twin is not a twin")

    # L4 an existing leg is never offered as its own substitute
    PREM_BY_SYMBOL = {"AAA": 8.0, "BBB": 0.0}
    r = decide_leg({"symbol": "AAA", "class": "equity", "amount": 100000.0}, 8.0, {"AAA", "BBB"}, ranked, classes, slope)
    leg(r, r["verdict"] == "NO_CHEAPER_TWIN", "L4 existing legs excluded")

    # L5 money math: 6.746% of 86,286 is 5,821 CNY
    PREM_BY_SYMBOL = {"AAA": 6.746, "BBB": 0.5}
    r = decide_leg({"symbol": "AAA", "class": "equity", "amount": 86286.0}, 6.746, legs, ranked, classes, slope)
    leg(r, abs(r["premium_cny"] - 5820.8) < 0.5, "L5 premium CNY = amount x premium%")
    leg(r, abs(r["candidate"]["premium_saving_cny"] - (6.746 - 0.5) * 86286.0 / 100.0) < 0.5,
        "L5b saving CNY uses the premium differential")

    # L6 give-up: gap 0.20 x 0.002 per bar x 12.6 bars/yr x 100 = 0.504 pp/yr -> advised
    gap = ranked["AAA"] - ranked["BBB"]
    give = gap * slope * MONTH_BARS * 100.0
    leg(r, abs(r["candidate"]["giveup_pp_per_year"] - give) < 1e-9, "L6 give-up = gap x slope x bars")
    leg(r, r["verdict"] == "SWAP_ADVISED" and give <= MAX_GIVEUP_PP_YR, "L6b inside the cap -> swap")

    # L7 the same saving with a much lower-ranked twin is refused
    ranked_low = dict(ranked, BBB=-1.0)
    r = decide_leg({"symbol": "AAA", "class": "equity", "amount": 100000.0}, 8.0, legs, ranked_low, classes, slope)
    leg(r, r["verdict"] == "HOLD_STRETCHED" and r["candidate"]["giveup_pp_per_year"] > MAX_GIVEUP_PP_YR,
        "L7 above the cap -> pay the premium instead")

    # L8 no premium row -> UNPRICED, never "not stretched"
    PREM_BY_SYMBOL = {}
    r = decide_leg({"symbol": "AAA", "class": "equity", "amount": 100000.0}, None, legs, ranked, classes, slope)
    leg(r, r["verdict"] == "UNPRICED" and r["stretched"] is None, "L8 missing premium is unpriced")

    # L9 face verdict precedence
    leg(None, face_verdict([{"verdict": "SWAP_ADVISED"}, {"verdict": "HOLD_STRETCHED"}]) == "SWAP_ADVISED",
        "L9 any swap wins the face word")
    leg(None, face_verdict([{"verdict": "NOT_STRETCHED"}, {"verdict": "UNPRICED"}]) == "UNPRICED",
        "L9b unpriced beats a quiet leg")

    # L11 the market cut: a cheaper crossborder name in ANOTHER market is a different bet,
    # never a substitution -- this is the case the 2026-11-16 sheet actually hits
    PREM_BY_SYMBOL = {"AAA": 6.746, "CCC": -1.489}
    NAME_BY_SYMBOL = {"AAA": "标普ETF", "CCC": "日本东证指数ETF南方"}
    cls2 = {"AAA": "crossborder", "CCC": "crossborder"}
    r = decide_leg({"symbol": "AAA", "class": "crossborder", "amount": 86286.0}, 6.746,
                   {"AAA"}, {"AAA": 0.30, "CCC": 0.44}, cls2, slope)
    leg(r, r["verdict"] == "NO_FAITHFUL_TWIN" and (r.get("different_bet") or {}).get("symbol") == "CCC",
        "L11 cheaper name in another market is a different bet, not a twin")
    leg(r, r.get("leg_market") == "us_sp500" and (r["different_bet"] or {}).get("market") == "jp",
        "L11b market tokens read from the names")

    # L12 the same saving in the SAME market is advised (and the give-up is signed)
    PREM_BY_SYMBOL = {"AAA": 6.746, "DDD": 0.5}
    NAME_BY_SYMBOL = {"AAA": "标普ETF", "DDD": "标普500ETF博时"}
    cls3 = {"AAA": "crossborder", "DDD": "crossborder"}
    r = decide_leg({"symbol": "AAA", "class": "crossborder", "amount": 86286.0}, 6.746,
                   {"AAA"}, {"AAA": 0.30, "DDD": 0.20}, cls3, slope)
    leg(r, r["verdict"] == "SWAP_ADVISED" and (r.get("candidate") or {}).get("market") == "us_sp500",
        "L12 same-market twin with a cheaper price is advised")
    NAME_BY_SYMBOL = {}

    # L10 slope reproduces a planted linear relation: the score is held for a whole horizon
    # block and each bar drifts 0.003/HORIZON * score, so the HORIZON-bar forward return is
    # 0.003 * score and the cross-sectional slope must come back as 0.003 (not 0.003/20,
    # which is what a score that changed every bar would produce)
    idx = pd.bdate_range("2024-01-01", periods=HORIZON * 6)
    n = 60
    cols = ["S%02d" % i for i in range(n)]
    rng = np.random.default_rng(7)
    blocks = rng.uniform(-1, 1, size=(6, n))
    score = pd.DataFrame(np.repeat(blocks, HORIZON, axis=0), index=idx, columns=cols)
    bar_ret = 1.0 + (0.003 / HORIZON) * score
    px = 100.0 * bar_ret.cumprod()
    sl = score_slope(px, score)
    leg(sl, sl.get("status") == "MEASURED" and abs(sl["slope_median_per_horizon"] - 0.003) < 3e-4,
        "L10 planted slope 0.003 recovered")

    print("premium-swap selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv):
    cmd = [a for a in argv[1:] if not a.startswith("-")]
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return check()
    if cmd and cmd[0] not in ("sheet",):
        print("usage: etf_book_premium_swap.py [sheet|--check|--selftest]")
        return 2
    sheet()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

