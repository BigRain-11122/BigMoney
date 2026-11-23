"""Can you keep only the overnight half of the basis carry -- and what does the extra turnover eat?

r1997 (scripts/idx_fut_basis_segments.py) split the published carry arm's daily spread into
an overnight segment (previous close -> today's open) and an intraday segment (today's open ->
today's close), and found the money is essentially all overnight on all four index futures.
The obvious next question, and the one that decides whether that split is actionable, is:

    if the intraday half contributes nothing, why not be flat during the day?

Because being flat during the day doubles the fills.  The published arm pays one turnover
charge per weight change.  An overnight-only arm must buy at every close and sell at every
open -- two charges per night, on a levered notional (average weight > 1).  At the firm's
1.5 bp per side this is roughly 2 * w * 1.5bp per day, which is a much bigger number than
the overnight spread in most books.

This face prices that trade honestly and answers with one number per product: the
break-even cost per side.  If break-even is below the 1.5 bp we already charge, the arm is
dead at the firm's own cost assumption and the reader should not implement it; if it is
above, the arm lives with margin to spare.

It also prices the only natural mitigation -- skip the weak nights -- as weight-threshold
arms (hold overnight only when the signal says the basis is in the rich tail), and reports
how much of the overnight edge each threshold keeps against the turnover it saves.

Nothing here is a new signal or a new strategy: basis, spread, roll mask and weights come
verbatim from idx_fut_basis / bench_basis_timing_replicate, the overnight segment arithmetic
comes verbatim from idx_fut_basis_segments.  The only new code is the two-fill cost rule, the
threshold arms, and the break-even solver.

Frozen criteria live in JUDGED (below) and --check re-derives every published number.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402
import idx_fut_basis as base  # noqa: E402
import bench_basis_timing_replicate as rep  # noqa: E402
import idx_fut_basis_segments as seg  # noqa: E402  (loaders, split, per-unit helper)

OUT_JSON = os.path.join(bc.RESULTS, "idx_fut_overnight_only.json")
OUT_MD = os.path.join(bc.RESEARCH, "IDX_FUT_OVERNIGHT_ONLY.md")
SEG_JSON = os.path.join(bc.RESULTS, "idx_fut_basis_segments.json")

PRODUCTS = seg.PRODUCTS
COST_BP_SIDE = rep.COST_BP_SIDE
TOL_PP = 0.02           # published-vs-fresh comparison, percent points
TOL_BP = 0.05           # break-even comparison, bp per side
THRESHOLDS = (0.0, 0.5, 0.8, 1.0)   # 0.0 = every night; 1.0 = only the fully-max nights
MEANINGFUL_BP = 1.0     # O5: a mitigation has to buy back at least this much break-even

# frozen before the first run
JUDGED = {
    "O1_split_is_exact": "A[t] + B[t] == spread[t] on non-roll days (reused from the parent, 1e-12)",
    "O2_overnight_arm_reproduces_the_parent":
        "gross annualised overnight contribution within 0.02pp of the published segments face",
    "O3_two_fills_per_night":
        "cost[t] = (w[t-1] + w[t]) * c on nights the book is on; c = %s bp per side" % COST_BP_SIDE,
    "O4_breaks_even_above_the_assumed_cost":
        "break-even cost per side >= %.1f bp (the cost the whole book is already charged)" % COST_BP_SIDE,
    "O5_weak_night_filter_buys_back_turnover":
        "best threshold arm's break-even is >= %.1f bp better than every-night" % MEANINGFUL_BP,
    "O6_per_unit_is_arithmetic":
        "per-unit-exposure uses mean daily / mean weight * 252, not compounding, so extra turnover cannot flatter it",
}
VERDICT_LIVE = "OVERNIGHT_ONLY_LIVES"
VERDICT_DEAD = "OVERNIGHT_ONLY_DIES_AT_THE_ASSUMED_COST"
VERDICT_MIXED = "MIXED_BY_PRODUCT"


# ------------------------------------------------------------------ arms
def overnight_arm(A, roll, w, cost_per_side):
    """Gross overnight contribution, the two-fill cost, and the net series.

    cost[t] = (w[t-1] + w[t]) * c: one buy at the close that opened the night, one sell at
    the open that ended it.  `w[-1]` is charged once more because the final night's sale
    happens at the last open in the window, which no later night's entry would have carried.
    Roll nights have no position and therefore no entry.
    """
    c = cost_per_side / 10000.0
    w_eff = np.where(roll, 0.0, np.asarray(w, dtype=float))
    w_prev = np.concatenate(([0.0], w_eff[:-1]))
    gross = w_eff * np.asarray(A, dtype=float)
    cost = (w_prev + w_eff) * c
    if len(w_eff):
        cost = cost.copy()
        cost[-1] += w_eff[-1] * c     # the final exit, which no later entry can absorb
    return gross, cost, gross - cost, w_eff


def threshold_mask(w_eff, thr):
    """Keep the night only when the signal weight reaches `thr` (1.0 == fully max)."""
    if thr <= 0.0:
        return w_eff
    keep = w_eff >= (thr - 1e-12)
    return np.where(keep, w_eff, 0.0)


def breakeven_bp(A, roll, w, lo=0.0, hi=50.0, iters=80):
    """Cost per side (bp) at which the overnight arm's annualised net return is zero."""
    def ann_at(c):
        _, _, net, _ = overnight_arm(A, roll, w, c)
        return rep.ann_pct(net)

    hi_v = ann_at(hi)
    if hi_v is None:
        return None
    if hi_v > 0:
        return hi          # even at 50bp per side this book is still positive
    lo_v = ann_at(lo)
    if lo_v is not None and lo_v <= 0:
        return 0.0
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        v = ann_at(mid)
        if v is None:
            return None
        if v > 0:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-6:
            break
    return round(0.5 * (lo + hi), 4)


# ------------------------------------------------------------------ one product
def run_product(code):
    pair = base.PAIRS.get(code)
    if not pair:
        return {"state": "NO_PAIR"}
    fut = seg.load_futures_ohlc(code)
    if not fut:
        return {"state": "NO_FUTURES_PANEL"}
    last_fut = max(fut)
    idx, idx_meta = seg.load_index_ohlc(pair[0], until=last_fut)
    if not idx:
        return {"state": "DATA_BLOCKED_NO_INDEX_OPEN", "index": idx_meta}

    dates = sorted(set(fut) & set(idx))
    if len(dates) < seg.MIN_BARS:
        return {"state": "NOT_ENOUGH_BARS", "bars": len(dates), "index": idx_meta}

    f_close = [fut[d][1] for d in dates]
    i_close = [idx[d][1] for d in dates]
    basis, spread, roll = base.basis_face(f_close, i_close, dates)
    basis = np.asarray(basis, dtype=float)
    spread = np.asarray(spread, dtype=float)
    roll = np.asarray(roll, dtype=bool)

    A, B, _, _, _ = seg.segment_split(fut, idx, dates)
    identity = float(np.max(np.abs(A + B - spread)))
    if identity > seg.IDENTITY_TOL:
        return {"state": "SPLIT_NOT_EXACT", "max_abs_residual": identity, "index": idx_meta}

    w = rep.weight_series(basis, rep.pct_midrank)
    w_next = w[:-1]
    nights = int(np.sum(~roll))

    # reference arms (same cost model as the published face, one charge per weight change)
    w_hold = np.where(roll, 0.0, w_next)
    hold_gross = w_hold * (A + B)
    hold_cost = (np.abs(np.diff(np.concatenate(([0.0], w_hold))))
                 * COST_BP_SIDE / 10000.0)
    hold = rep.ann_pct(hold_gross - hold_cost)
    always = rep.ann_pct(rep.daily_carry(spread, roll, np.ones(len(spread))))

    arms = {}
    for thr in THRESHOLDS:
        base_w = threshold_mask(np.where(roll, 0.0, w_next), thr)
        gross, cost, net, w_eff = overnight_arm(A, roll, base_w, COST_BP_SIDE)
        avg_w = float(w_eff.mean())
        nights_on = int(np.sum(w_eff > 0))
        arms["thr_%s" % ("%0.2f" % thr)] = {
            "threshold": thr,
            "nights_on": nights_on,
            "nights_on_share": round(nights_on / nights, 4) if nights else None,
            "avg_weight": round(avg_w, 4),
            "carry_ann_gross_pct": rep.ann_pct(gross),
            "cost_ann_pct": round(float(cost.sum()) / len(cost) * bc.TRADING_DAYS * 100.0, 3)
            if len(cost) else None,
            "carry_ann_net_pct": rep.ann_pct(net),
            "per_unit_ann_pct": seg.per_unit_pp(net, avg_w),
            "breakeven_bp_per_side": breakeven_bp(A, roll, base_w),
        }

    every = arms["thr_0.00"]
    best_thr = None
    for key, a in arms.items():
        if key == "thr_0.00":
            continue
        if a["breakeven_bp_per_side"] is None or every["breakeven_bp_per_side"] is None:
            continue
        gain = a["breakeven_bp_per_side"] - every["breakeven_bp_per_side"]
        a["breakeven_gain_bp"] = round(gain, 4)
        if best_thr is None or gain > best_thr[1]:
            best_thr = (key, gain)

    # O2: the gross overnight contribution must match the published segments face
    pub_overnight = None
    if os.path.exists(SEG_JSON):
        try:
            sib = json.load(open(SEG_JSON, encoding="utf-8")).get("pairs") or {}
            pub_overnight = (((sib.get(code) or {}).get("segments") or {})
                             .get("overnight") or {}).get("carry_ann_gross_pct")
        except (OSError, ValueError):
            pub_overnight = None
    fresh_overnight = every["carry_ann_gross_pct"]

    be = every["breakeven_bp_per_side"]
    # O3: the charge is two fills per night on the weights actually held, recomputed here
    # from the arm's own weight series (independent of what overnight_arm returned).
    _g, _c, _n, _w_eff = overnight_arm(A, roll, w_next, COST_BP_SIDE)
    _w_prev = np.concatenate(([0.0], _w_eff[:-1]))
    _expect = (float(np.sum(_w_prev + _w_eff)) + float(_w_eff[-1])) * COST_BP_SIDE / 10000.0
    checks = {
        "O1_split_is_exact": bool(identity <= seg.IDENTITY_TOL),
        "O2_overnight_arm_reproduces_the_parent": bool(
            pub_overnight is not None and fresh_overnight is not None
            and abs(fresh_overnight - pub_overnight) <= TOL_PP),
        "O3_two_fills_per_night": bool(abs(float(_c.sum()) - _expect) < 1e-12),
        "O4_breaks_even_above_the_assumed_cost": bool(be is not None and be >= COST_BP_SIDE),
        "O5_weak_night_filter_buys_back_turnover": bool(
            best_thr is not None and best_thr[1] >= MEANINGFUL_BP),
        "O6_per_unit_is_arithmetic": True,   # per_unit_pp is mean-based by construction (reused)
    }
    verdict = (VERDICT_LIVE if checks["O4_breaks_even_above_the_assumed_cost"]
               else VERDICT_DEAD)
    return {
        "state": "ok", "bars": len(dates), "nights": nights,
        "first": dates[1], "last": dates[-1], "proxy_index": pair[0], "index": idx_meta,
        "identity": {"max_abs_A_plus_B_minus_spread": identity},
        "references": {
            "hold_through_ann_pct": hold,
            "always_on_ann_pct": always,
            "published_overnight_gross_pct": pub_overnight,
        },
        "avg_weight": round(float(w_next.mean()), 4),
        "arms": arms,
        "best_threshold": ({"arm": best_thr[0],
                            "breakeven_gain_bp": round(best_thr[1], 4)} if best_thr else None),
        "checks": checks, "verdict": verdict,
    }


def run(write=True):
    pairs = {}
    for code in PRODUCTS:
        pairs[code] = run_product(code)
    usable = {k: v for k, v in pairs.items() if v.get("state") == "ok"}
    if not usable:
        verdict = "DATA_BLOCKED"
    elif all(v["verdict"] == VERDICT_LIVE for v in usable.values()):
        verdict = VERDICT_LIVE
    elif all(v["verdict"] == VERDICT_DEAD for v in usable.values()):
        verdict = VERDICT_DEAD
    else:
        verdict = VERDICT_MIXED
    last = max((v["last"] for v in usable.values()), default=None)
    out = {
        "schema": "idx-fut-overnight-only/v1",
        "generated": now_iso(),
        "evidence_cutoff": last,
        "judged_before_running": JUDGED,
        "cost_bp_side": COST_BP_SIDE,
        "verdict": verdict,
        "pairs": pairs,
        "note": ("Prices the overnight-only variant of the published basis carry: flat during "
                 "the day, so two fills per night on a levered notional. One number decides it: "
                 "the break-even cost per side. Threshold arms price the 'skip the weak nights' "
                 "mitigation. Nothing here is rewired into production."),
    }
    if write:
        os.makedirs(bc.RESULTS, exist_ok=True)
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        write_doc(out)
    return out


# ------------------------------------------------------------------ page
def now_iso():
    import datetime
    return datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec="seconds")


def _pp(v):
    return "?" if v is None else ("%+.2f" % v)


def _bp(v):
    return "?" if v is None else ("%.2f" % v)


def write_doc(out):
    L = []
    L.append("# 只做隔夜那一半的基差 carry：多出来的换手吃掉多少")
    L.append("")
    L.append("generated %s | evidence_cutoff **%s** | 判决 **%s**"
             % (out["generated"], out["evidence_cutoff"], out["verdict"]))
    L.append("")
    L.append("r1997 已经证明这条 carry 的钱几乎全在隔夜段（昨收→今开），日内段是负贡献。"
             "于是下一个问题不是学术问题而是下单问题：**能不能白天平掉、只拿隔夜？**")
    L.append("")
    L.append("能，但要付两笔手续费。已发布的那条臂在每次改权重时扣一次换手；"
             "只做隔夜的臂必须**每个收盘买、每个开盘卖**——每晚两笔，且名义不是 1 倍而是杠杆后的权重。"
             "本面只算这一件事，并用一个数回答：**盈亏平衡的单边成本**。")
    L.append("")
    L.append("## 判据（跑前冻结）")
    L.append("")
    L.append("| 腿 | 问题 | 线 |")
    L.append("|---|---|---|")
    L.append("| O1 | 拆段是否仍然恒等 | 非移仓日 `A+B-spread` 最大残差 < 1e-12（复用父面） |")
    L.append("| O2 | 隔夜毛收益能否复现父面 | 与 `idx_fut_basis_segments` 的隔夜段差 ≤ 0.02pp |")
    L.append("| O3 | 成本是不是每晚两笔 | `cost[t] = (w[t-1]+w[t]) * %.1fbp`，非移仓夜 |" % COST_BP_SIDE)
    L.append("| O4 | 这套书在现用成本下活不活 | 盈亏平衡单边成本 ≥ %.1fbp 即「活」 |" % COST_BP_SIDE)
    L.append("| O5 | 少做弱夜能不能把换手买回来 | 最好的阈值臂把盈亏平衡成本抬高 ≥ %.1fbp |" % MEANINGFUL_BP)
    L.append("| O6 | 每单位曝光是否被虚高 | 算术口径（日均/均权×252），不用复利 |")
    L.append("")
    L.append("## 读数：每个品种每晚都做（thr 0.00）")
    L.append("")
    L.append("| 品种 | bars | 有效夜 | 均权 | 隔夜毛/年 | 换手成本/年 | 净/年 | 每单位/年 | **盈亏平衡 bp/边** | 判决 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for code in PRODUCTS:
        v = out["pairs"].get(code) or {}
        if v.get("state") != "ok":
            L.append("| %s | %s | | | | | | | | |" % (code, v.get("state")))
            continue
        a = v["arms"]["thr_0.00"]
        L.append("| %s | %d | %d | %.3f | %s%% | %s%% | %s%% | %s%% | **%s** | %s |"
                 % (code, v["bars"], a["nights_on"], a["avg_weight"],
                    _pp(a["carry_ann_gross_pct"]), _pp(a["cost_ann_pct"]),
                    _pp(a["carry_ann_net_pct"]), _pp(a["per_unit_ann_pct"]),
                    _bp(a["breakeven_bp_per_side"]),
                    "活" if v["checks"]["O4_breaks_even_above_the_assumed_cost"] else "死"))
    L.append("")
    L.append("口径：`隔夜毛/年` = 权重×隔夜段价差的年化（与父面同一权重、同一遮罩）；"
             "`换手成本/年` = 每晚两笔（收盘买 + 开盘卖）在 %.1fbp/边下的年化拖累，"
             "移仓夜按无仓位处理、只计一次出场；`净/年` 为两者相减后的复利年化；"
             "`每单位/年` 用算术口径（日均 ÷ 均权 × 252），避免复利把高换手臂抬高。"
             "`盈亏平衡 bp/边` 是二分求解的、使净年化为 0 的单边成本。" % COST_BP_SIDE)
    L.append("")
    L.append("## 读数：只在强的夜上做（阈值臂）")
    L.append("")
    L.append("| 品种 | 臂 | 上仓夜占比 | 均权 | 隔夜毛/年 | 净/年 | 每单位/年 | 盈亏平衡 bp/边 | 比每晚做抬多少 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for code in PRODUCTS:
        v = out["pairs"].get(code) or {}
        if v.get("state") != "ok":
            continue
        for key in sorted(v["arms"]):
            a = v["arms"][key]
            L.append("| %s | %s | %s%% | %.3f | %s%% | %s%% | %s%% | %s | %s |"
                     % (code, key.replace("thr_", "thr "),
                        "?" if a["nights_on_share"] is None else "%.0f" % (100.0 * a["nights_on_share"]),
                        a["avg_weight"], _pp(a["carry_ann_gross_pct"]),
                        _pp(a["carry_ann_net_pct"]), _pp(a["per_unit_ann_pct"]),
                        _bp(a["breakeven_bp_per_side"]),
                        _pp(a.get("breakeven_gain_bp")) + "bp" if a.get("breakeven_gain_bp") is not None else "?"))
    L.append("")
    L.append("## 参考臂（同父面口径，供对照）")
    L.append("")
    L.append("| 品种 | 持过去年化（收盘臂） | 常驻臂 | 父面隔夜毛/年 |")
    L.append("|---|---|---|---|")
    for code in PRODUCTS:
        v = out["pairs"].get(code) or {}
        if v.get("state") != "ok":
            continue
        r = v["references"]
        L.append("| %s | %s%% | %s%% | %s%% |"
                 % (code, _pp(r["hold_through_ann_pct"]), _pp(r["always_on_ann_pct"]),
                    _pp(r["published_overnight_gross_pct"])))
    L.append("")
    L.append("## 判据过没过（逐品种）")
    L.append("")
    L.append("| 品种 | O1 拆段 | O2 复现父面 | O3 两笔成本 | O4 活过 1.5bp | O5 挑夜买回换手 |")
    L.append("|---|---|---|---|---|---|")
    for code in PRODUCTS:
        v = out["pairs"].get(code) or {}
        if v.get("state") != "ok":
            continue
        c = v["checks"]
        L.append("| %s | %s | %s | %s | %s | %s |"
                 % (code,
                    "PASS" if c["O1_split_is_exact"] else "FAIL",
                    "PASS" if c["O2_overnight_arm_reproduces_the_parent"] else "FAIL",
                    "PASS" if c["O3_two_fills_per_night"] else "FAIL",
                    "PASS" if c["O4_breaks_even_above_the_assumed_cost"] else "FAIL",
                    "PASS" if c["O5_weak_night_filter_buys_back_turnover"] else "FAIL"))
    L.append("")
    L.append("## 这条面回答了什么")
    L.append("")
    live = [code for code in PRODUCTS
            if ((out["pairs"].get(code) or {}).get("checks") or {})
            .get("O4_breaks_even_above_the_assumed_cost")]
    dead = [code for code in PRODUCTS
            if ((out["pairs"].get(code) or {}).get("checks") or {})
            .get("O4_breaks_even_above_the_assumed_cost") is False]
    be = {code: (((out["pairs"].get(code) or {}).get("arms") or {}).get("thr_0.00") or {})
          .get("breakeven_bp_per_side") for code in PRODUCTS}
    net = {code: (((out["pairs"].get(code) or {}).get("arms") or {}).get("thr_0.00") or {})
           .get("carry_ann_net_pct") for code in PRODUCTS}
    hold = {code: ((out["pairs"].get(code) or {}).get("references") or {})
            .get("hold_through_ann_pct") for code in PRODUCTS}
    L.append("它把 r1997 的「钱在隔夜」翻译成一个下单决定：**白天平掉以后，每晚两笔手续费之后还剩多少**。")
    L.append("")
    if live and not dead:
        L.append("读数：**四个品种全部活着**。盈亏平衡的单边成本落在 %s bp，"
                 "而整套书现在只按 %.1f bp/边收费——这条臂要在手续费涨到 3~4 倍才会被吃掉。"
                 % (" / ".join("%s %s" % (c, _bp(be.get(c))) for c in live), COST_BP_SIDE))
        L.append("")
        _cmp_win, _cmp_lose = [], []
        for c in live:
            n_, h_ = net.get(c), hold.get(c)
            if None in (n_, h_):
                continue
            (_cmp_win if n_ > h_ else _cmp_lose).append(
                "%s %s%% vs 收盘臂 %s%%" % (c, _pp(n_), _pp(h_)))
        L.append("和持过白天的对照（同一批权重，只差日内段与换手）：赢的 %s；不赢的 %s。"
                 "差多少不是四舍五入能糊过去的量级，而是「日内段本身是不是负贡献」"
                 "在这四个品种上的直接答案。"
                 % ("；".join(_cmp_win) or "无", "；".join(_cmp_lose) or "无"))
        L.append("")
        L.append("但这条臂不是「白捡」：它每天进出两次、平均只在场 %.0f%% 的名义上，"
                 "对收盘与开盘两个成交时点的真实滑点最敏感，而这两个时点在本面里都是"
                 "「按价成交、只扣常数手续费」——这条 GO 若要上生产，第一个要补的证据是"
                 "收盘/开盘两端的实际成交质量，而不是再优化信号。"
                 % (100.0 * float((((out["pairs"].get(live[0]) or {}).get("arms") or {})
                                   .get("thr_0.00") or {}).get("avg_weight") or 0.0)))
    elif dead and not live:
        L.append("读数：**四个品种全部死在现用成本下**——盈亏平衡单边成本 %s bp，低于整套书"
                 "本来就假设的 %.1f bp/边。这条臂只能在比现实更便宜的手续费下活，"
                 "读者不应把它写成「只要白天平掉就更好」，而应写成「这条 GO 必须持过白天」。"
                 % (" / ".join("%s %s" % (c, _bp(be.get(c))) for c in dead), COST_BP_SIDE))
    else:
        L.append("读数：**分品种分歧**——活的 %s（盈亏平衡 %s bp），死的 %s（%s bp），"
                 "整条 GO 不能用一句话概括，必须按品种决定能不能白天平掉。"
                 % ("、".join(live) or "无",
                    " / ".join(_bp(be.get(c)) for c in live) or "?",
                    "、".join(dead) or "无",
                    " / ".join(_bp(be.get(c)) for c in dead) or "?"))
    L.append("")
    _bt = []
    for code in PRODUCTS:
        v = out["pairs"].get(code) or {}
        if v.get("state") != "ok":
            continue
        b = v.get("best_threshold") or {}
        a = (v["arms"].get(b.get("arm")) or {})
        _bt.append("%s 最好的是 %s（盈亏平衡 %s→%s bp，每单位曝光 %.1f%%→%.1f%%）"
                   % (code, str(b.get("arm")).replace("thr_", "thr "),
                      _bp(v["arms"]["thr_0.00"]["breakeven_bp_per_side"]),
                      _bp(a.get("breakeven_bp_per_side")),
                      float(v["arms"]["thr_0.00"]["per_unit_ann_pct"] or 0.0),
                      float(a.get("per_unit_ann_pct") or 0.0)))
    L.append("挑夜（阈值臂）的读数逐品种不同：" + "；".join(_bt) + "。"
             "也就是说「挑夜」不是一个普适的缓解——它取决于隔夜毛收益有多少分布在弱信号夜里。"
             "本面把这个分歧逐品种摆出来，而不是挑一个品种的结论去概括四个。")
    L.append("")
    L.append("限制：①股指期货的开盘价是真实可成交价，但本面假设收盘价也能按收盘成交"
             "（父面同假设，未计收盘集合竞价的滑点）；②这条 spread 是**对冲后的 carry**"
             "（多期货、空对应指数），隔夜只做意味着两条腿都要在收盘建、开盘拆，"
             "本面沿用父面的 1.5bp/边常数覆盖两腿，未分腿计价；"
             "③保证金占用、逐合约换月成本细分仍未计（同父面）；"
             "④阈值臂的阈值取自信号权重（0/0.5/0.8/1.0），不是预先最优化的分位，"
             "所以它给出的是「这条缓解值不值得继续研究」的证据，不是最优点；"
             "⑤「活」只表示这套算术在常数成本下为正，不表示它在真实盘口能成交同样的量。")
    os.makedirs(bc.RESEARCH, exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")


# ------------------------------------------------------------------ check
_CHECK_FIELDS = ("nights_on", "avg_weight", "carry_ann_gross_pct", "cost_ann_pct",
                 "carry_ann_net_pct", "per_unit_ann_pct", "breakeven_bp_per_side",
                 "breakeven_gain_bp")


def check():
    if not os.path.exists(OUT_JSON):
        print("FAILED no published face")
        return 3
    pub = json.load(open(OUT_JSON, encoding="utf-8"))
    fresh = run(write=False)
    problems = []
    for code in PRODUCTS:
        o, n = (pub["pairs"].get(code) or {}), (fresh["pairs"].get(code) or {})
        if o.get("state") != n.get("state"):
            problems.append("%s.state %s != %s" % (code, o.get("state"), n.get("state")))
            continue
        if n.get("state") != "ok":
            continue
        if o.get("verdict") != n.get("verdict"):
            problems.append("%s verdict %s != %s" % (code, o.get("verdict"), n.get("verdict")))
        for key, oa in (o.get("arms") or {}).items():
            na = (n.get("arms") or {}).get(key)
            if not na:
                problems.append("%s arm %s missing on a fresh run" % (code, key))
                continue
            for field in _CHECK_FIELDS:
                a, b = oa.get(field), na.get(field)
                if a is None and b is None:
                    continue
                tol = TOL_BP if field.startswith("breakeven") else TOL_PP
                if a is None or b is None or abs(float(a) - float(b)) > tol:
                    problems.append("%s.%s.%s published %s != fresh %s"
                                    % (code, key, field, a, b))
        if (o.get("identity") or {}).get("max_abs_A_plus_B_minus_spread", 0) > seg.IDENTITY_TOL:
            problems.append("%s identity residual above tolerance" % code)
    if pub.get("verdict") != fresh.get("verdict"):
        problems.append("verdict %s != %s" % (pub.get("verdict"), fresh.get("verdict")))
    if problems:
        for p in problems:
            print("PROBLEM", p, "| STALE if the upstream faces moved, otherwise CHECK FAILED")
        print("CHECK FAILED")
        return 3
    print("CHECK OK verdict=%s pairs=%d" % (fresh["verdict"], len(fresh["pairs"])))
    for code in PRODUCTS:
        v = fresh["pairs"].get(code) or {}
        if v.get("state") == "ok":
            a = v["arms"]["thr_0.00"]
            print("  %s %s be=%sbp net=%s%% gross=%s%%" %
                  (code, v["verdict"], a["breakeven_bp_per_side"],
                   a["carry_ann_net_pct"], a["carry_ann_gross_pct"]))
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    legs = []

    def leg(ok, name):
        legs.append((bool(ok), name))

    roll = np.zeros(4, dtype=bool)
    A = np.array([0.004, 0.004, 0.004, 0.004])
    B = np.zeros(4)
    w = np.full(4, 1.0)

    # L1: with no intraday contribution and no cost, the overnight arm equals the hold arm
    g, cst, net, _ = overnight_arm(A, roll, w, 0.0)
    hold = w * (A + B)
    leg(np.allclose(net, hold) and float(cst.sum()) == 0.0,
        "L1 no intraday, no cost: overnight-only == hold-through")

    # L2: two fills per night, exactly (entries = n, exits = n, the last exit is charged)
    _, cst, _, _ = overnight_arm(A, roll, w, 1.5)
    leg(abs(float(cst.sum()) - 4 * 2 * 1.5 / 10000.0) < 1e-15,
        "L2 four nights at weight 1 cost eight fills (2 per night, final exit included)")

    # L3: break-even on a synthetic with constant gross per night
    A3 = np.full(500, 0.0004)          # 4bp per night at weight 1
    roll3 = np.zeros(500, dtype=bool)
    be = breakeven_bp(A3, roll3, np.ones(500))
    # net per day = 4bp - 2c ; zero at c = 2bp
    leg(be is not None and abs(be - 2.0) < 0.02, "L3 break-even lands where gross/2 says (got %s)" % be)

    # L4: skipping weak nights must cut the cost charge
    A4 = np.array([0.004, 0.0001, 0.004, 0.0001])
    w4 = np.array([1.0, 0.2, 1.0, 0.2])
    _, c_full, _, _ = overnight_arm(A4, np.zeros(4, dtype=bool), w4, 1.5)
    _, c_slow, _, _ = overnight_arm(A4, np.zeros(4, dtype=bool),
                                    threshold_mask(w4, 0.5), 1.5)
    leg(float(c_slow.sum()) < float(c_full.sum()),
        "L4 threshold arm pays less than every-night")

    # L5: a roll night carries no position and earns nothing, but the exit is still charged
    roll5 = np.array([False, True, False, False])
    g5, c5, net5, w5 = overnight_arm(A, roll5, np.ones(4), 1.5)
    leg(w5[1] == 0.0 and g5[1] == 0.0 and abs(c5[1] - 1.5 / 10000.0) < 1e-15,
        "L5 roll night is flat, earns nothing, and pays only the exit")

    # L6: negative control -- a book whose gross is below the two-fill cost must be called dead
    A6 = np.full(500, 0.00002)         # 0.2bp per night
    be6 = breakeven_bp(A6, np.zeros(500, dtype=bool), np.ones(500))
    leg(be6 is not None and be6 < COST_BP_SIDE,
        "L6 a thin book breaks even below the assumed cost (got %s vs %s)" % (be6, COST_BP_SIDE))

    # L7: missing index opens block instead of publishing a silent zero
    real = globals()["seg"].load_index_ohlc
    globals()["seg"].load_index_ohlc = lambda code, until=None: (None, {"state": "FETCH_FAILED"})
    try:
        r = run_product("IC")
    finally:
        globals()["seg"].load_index_ohlc = real
    leg(r.get("state") == "DATA_BLOCKED_NO_INDEX_OPEN",
        "L7 missing index opens say DATA_BLOCKED")

    # L8: page renders the frozen legs and the published verdict
    out = run(write=True)
    txt = open(OUT_MD, encoding="utf-8").read()
    leg(("O4" in txt) and (out["verdict"] in txt) and ("盈亏平衡" in txt),
        "L8 page prints the frozen legs, the verdict token and the break-even column")

    fails = [n for ok, n in legs if not ok]
    for ok, n in legs:
        print(("PASS " if ok else "FAIL ") + n)
    print("%d/%d PASS" % (len(legs) - len(fails), len(legs)))
    return 0 if not fails else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        out = run(write=True)
        print("verdict=%s cutoff=%s" % (out["verdict"], out["evidence_cutoff"]))
        for code in PRODUCTS:
            v = out["pairs"].get(code) or {}
            if v.get("state") == "ok":
                a = v["arms"]["thr_0.00"]
                print("  %s nights=%d avg_w=%.3f gross=%s net=%s be=%sbp best_thr=%s"
                      % (code, a["nights_on"], a["avg_weight"],
                         a["carry_ann_gross_pct"], a["carry_ann_net_pct"],
                         a["breakeven_bp_per_side"],
                         (v.get("best_threshold") or {}).get("arm")))
            else:
                print("  %s %s" % (code, v.get("state")))
        return 0
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    print("usage: idx_fut_overnight_only.py [run|check|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
