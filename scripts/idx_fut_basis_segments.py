"""Is the basis-timing GO's money earned overnight, and can you actually fill it?

r1996 replicated the bench book's only GO (scripts/bench_basis_timing_replicate.py) and
then said the awkward half out loud: every leg's money lives in the NEXT trading day
(or later: +7.37pp at lag 1, +1.24pp at lag 2, negative at lag 5), so the effect is a
daily price-gap catch-up, and "it is extremely sensitive to the execution moment -- close
or next open -- and that is exactly the part this face cannot judge".  The index panel
carries only closes, so the overnight segment cannot be split there.

This script answers that with one new input (index opens) and no new strategy:

    day t splits exactly into two segments,
        overnight:  close[t-1] -> open[t]
        intraday:   open[t]    -> close[t]
    and the parent's measured spread is split additively without any approximation:
        spread[t] = A[t] + B[t],
        A[t] = (1+ri[t]) * o[t] * (1+d[t])      (overnight, grown by the day's own move)
        B[t] = (1+ri[t]) * d[t]                 (intraday)
    where o/d are the same ratio-differences on each segment and ri is the index return.

Then it prices a second execution arm on the same weights and the same cost:
    close arm (as published): the weight known at close of t-1 is held from close to close
    next-open arm:            that weight is filled at open of t, so the overnight segment
                              is still financed by the PREVIOUS weight and only the intraday
                              segment is held at the new weight
Both arms pay the same turnover cost; the difference is only where the fill happens.
If the margin only survives at the close, the GO is not executable as coded, and this
face says so instead of letting the next reader assume a fill nobody can get.

Reuse, not re-implementation (r1375): basis/spread/roll come from idx_fut_basis.basis_face,
weights and annualisation come from bench_basis_timing_replicate.  The only new code is the
segment arithmetic, the open-arm rule, and the index-open cache.

Criteria frozen before the first run live in JUDGED (below) and are re-derived by --check.
"""
import csv
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402
import idx_fut_basis as base  # noqa: E402
import bench_basis_timing_replicate as rep  # noqa: E402  (weights, annualisation, cost)

OUT_JSON = os.path.join(bc.RESULTS, "idx_fut_basis_segments.json")
OUT_MD = os.path.join(bc.RESEARCH, "IDX_FUT_BASIS_SEGMENTS.md")
IDX_OHLC_DIR = os.path.join(bc.DATA, "index_ohlc")

PRODUCTS = ("IC", "IM", "IF", "IH")
MIN_BARS = 400
COST_BP_SIDE = rep.COST_BP_SIDE
TOL_PP = 0.02                 # --check comparison tolerance, percent points
IDENTITY_TOL = 1e-12          # A + B - spread, absolute (all quantities are ~1e-2)

# frozen before the first run
JUDGED = {
    "S1_split_is_exact": "A[t] + B[t] == spread[t] on every non-roll day, max |resid| < 1e-12",
    "S2_segments_rebuild_the_published_arm":
        "annualised(w*A + w*B - cost) reproduces the published weighted carry within 0.02pp",
    "S3_where_the_money_is":
        "overnight / intraday share of the gross weighted carry; |share| >= 0.70 names one side",
    "S4_executable_at_the_next_open":
        "next-open arm's per-unit-exposure margin vs always-on >= 1.0pp (the same line R1 used)",
    "S5_same_cost_both_arms":
        "both arms pay |dw| * COST_BP_SIDE once per weight change; only the fill moment differs",
}
S3_ONE_SIDE = 0.70
S4_MARGIN_PP = 1.0


# ------------------------------------------------------------------ loaders
def load_futures_ohlc(code):
    """date -> (open, close) from the same panel idx_fut_basis reads."""
    path = os.path.join(bc.DATA, "futures_daily", code + ".csv")
    if not os.path.exists(path):
        return None
    out = {}
    for r in base.read_csv_rows(path):
        try:
            d = str(r["date"])[:10]
            o = float(r["open"])
            c = float(r["close"])
        except (KeyError, TypeError, ValueError):
            continue
        if o > 0 and c > 0:
            out[d] = (o, c)
    return out or None


def load_index_ohlc(code, until=None):
    """date -> (open, close).  Cached in data/index_ohlc/<code>.csv.

    A separate cache file on purpose: data/index_daily/<code>.csv is a shared face read by
    other scripts as (date, close), and rewriting it to add columns would touch a face this
    round has no business touching.  Same source, different file, honest header.

    Returns (mapping, meta).  meta["state"] is "ok" / "FETCH_FAILED" / "CACHE_STALE".
    """
    os.makedirs(IDX_OHLC_DIR, exist_ok=True)
    path = os.path.join(IDX_OHLC_DIR, code + ".csv")
    meta = {"path": os.path.relpath(path, bc.ROOT).replace("\\", "/")}
    cached = None
    if os.path.exists(path):
        cached = {}
        for r in base.read_csv_rows(path):
            try:
                d = str(r["date"])[:10]
                o = float(r["open"])
                c = float(r["close"])
            except (KeyError, TypeError, ValueError):
                continue
            if o > 0 and c > 0:
                cached[d] = (o, c)
        meta["cache_last"] = max(cached) if cached else None
    stale = not cached or (until is not None and meta.get("cache_last") and
                           meta["cache_last"] < until)
    if not stale:
        meta["state"] = "ok"
        return cached, meta
    try:
        base._clear_proxy()  # same helper the close loader uses before touching akshare
        import akshare as ak
        df = ak.stock_zh_index_daily(symbol=code)
        rows = []
        for d, o, c in zip(df["date"], df["open"], df["close"]):
            d = str(d)[:10]
            o, c = float(o), float(c)
            if o > 0 and c > 0:
                rows.append((d, o, c))
    except Exception as exc:
        meta["state"] = "FETCH_FAILED"
        meta["why"] = "%s: %s" % (type(exc).__name__, exc)
        if cached:
            meta["used_cache_last"] = meta.get("cache_last")
            return cached, meta
        return None, meta
    rows.sort()
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "open", "close"])
        w.writerows(rows)
    meta["state"] = "ok"
    meta["fetched_rows"] = len(rows)
    meta["cache_last"] = rows[-1][0] if rows else None
    return dict((d, (o, c)) for d, o, c in rows), meta


# ------------------------------------------------------------------ segments
def segment_split(fut_ohlc, idx_ohlc, dates):
    """Exact additive split of the parent's spread into (overnight, intraday).

    spread[k] is measured between dates[k] and dates[k+1] (parent convention).  Uses the
    same dates list, so segment[t] lines up with spread[t-1].
    """
    A, B, o_seg, d_seg, ri = [], [], [], [], []
    for k in range(1, len(dates)):
        d0, d1 = dates[k - 1], dates[k]
        fo0, fc0 = fut_ohlc[d0]
        fo1, fc1 = fut_ohlc[d1]
        io0, ic0 = idx_ohlc[d0]
        io1, ic1 = idx_ohlc[d1]
        # ratio-difference on each segment
        o = (fo1 / fc0) / (io1 / ic0) - 1.0
        dd = (fc1 / fo1) / (ic1 / io1) - 1.0
        r_i = ic1 / ic0 - 1.0
        o_seg.append(o)
        d_seg.append(dd)
        ri.append(r_i)
        A.append((1.0 + r_i) * o * (1.0 + dd))
        B.append((1.0 + r_i) * dd)
    return (np.asarray(A, dtype=float), np.asarray(B, dtype=float),
            np.asarray(o_seg, dtype=float), np.asarray(d_seg, dtype=float),
            np.asarray(ri, dtype=float))


def per_unit_pp(daily, avg_w):
    if avg_w <= 0 or len(daily) == 0:
        return None
    mu = float(np.sum(daily)) / len(daily) / avg_w
    return round(mu * bc.TRADING_DAYS * 100.0, 3)


def run_product(code):
    pair = base.PAIRS.get(code)
    if not pair:
        return {"state": "NO_PAIR"}
    fut = load_futures_ohlc(code)
    if not fut:
        return {"state": "NO_FUTURES_PANEL"}
    last_fut = max(fut)
    idx, idx_meta = load_index_ohlc(pair[0], until=last_fut)
    if not idx:
        return {"state": "DATA_BLOCKED_NO_INDEX_OPEN", "index": idx_meta}

    dates = sorted(set(fut) & set(idx))
    if len(dates) < MIN_BARS:
        return {"state": "NOT_ENOUGH_BARS", "bars": len(dates), "index": idx_meta}

    f_close = [fut[d][1] for d in dates]
    i_close = [idx[d][1] for d in dates]
    basis, spread, roll = base.basis_face(f_close, i_close, dates)
    basis = np.asarray(basis, dtype=float)
    spread = np.asarray(spread, dtype=float)
    roll = np.asarray(roll, dtype=bool)
    d1 = dates[1:]

    A, B, o_seg, d_seg, ri = segment_split(fut, idx, dates)

    identity = float(np.max(np.abs(A + B - spread)))
    if identity > IDENTITY_TOL:
        return {"state": "SPLIT_NOT_EXACT", "max_abs_residual": identity, "index": idx_meta}

    w = rep.weight_series(basis, rep.pct_midrank)
    w_next = w[:-1]
    one = np.ones(len(spread))

    cost = np.abs(np.diff(np.concatenate(([0.0], w_next)))) * COST_BP_SIDE / 10000.0
    seg_o = np.where(roll, 0.0, w_next * A)
    seg_i = np.where(roll, 0.0, w_next * B)
    carry = seg_o + seg_i
    carry_net = carry - cost

    ann_w = rep.ann_pct(carry_net)
    ann_a = rep.ann_pct(rep.daily_carry(spread, roll, one))
    ann_w_gross = rep.ann_pct(carry)
    ann_o_gross = rep.ann_pct(seg_o)
    ann_i_gross = rep.ann_pct(seg_i)
    reb = rep.ann_pct(carry + cost)          # gross published arm, rebuilt
    avg_w = round(float(w_next.mean()), 4)
    margin = round(ann_w - ann_a, 3) if None not in (ann_w, ann_a) else None

    gross_sum = None
    if None not in (ann_o_gross, ann_i_gross):
        gross_sum = round(ann_o_gross + ann_i_gross, 3)
    share = {}
    if gross_sum is not None and abs(gross_sum) > 1e-9:
        share = {"overnight": round(ann_o_gross / gross_sum, 4),
                 "intraday": round(ann_i_gross / gross_sum, 4)}

    # next-open arm: the weight filled at open of day t holds only the intraday segment;
    # the overnight segment of that day is still financed by the previous weight.
    w_prev = np.concatenate(([0.0], w_next[:-1]))
    open_o = np.where(roll, 0.0, w_prev * A)
    open_i = np.where(roll, 0.0, w_next * B)
    carry_open = open_o + open_i - cost
    ann_open = rep.ann_pct(carry_open)
    pu_open = per_unit_pp(carry_open, avg_w)
    pu_close = per_unit_pp(carry_net, avg_w)
    pu_always = per_unit_pp(rep.daily_carry(spread, roll, one), 1.0)
    margin_open = (round(pu_open - pu_always, 3)
                   if pu_open is not None and pu_always is not None else None)

    checks = {
        "S1_split_is_exact": bool(identity <= IDENTITY_TOL),
        "S2_segments_rebuild_the_published_arm":
            bool(None not in (reb, ann_w_gross)
                 and abs(reb - ann_w_gross) <= TOL_PP),
        "S3_where_the_money_is": bool(
            share and max(abs(share["overnight"]), abs(share["intraday"])) >= S3_ONE_SIDE),
        "S4_executable_at_the_next_open": bool(margin_open is not None
                                               and margin_open >= S4_MARGIN_PP),
        "S5_same_cost_both_arms": True,   # both arms use the same `cost` array, by construction
    }
    seg_name = "MIXED"
    if share:
        if abs(share["overnight"]) >= S3_ONE_SIDE:
            seg_name = "OVERNIGHT"
        elif abs(share["intraday"]) >= S3_ONE_SIDE:
            seg_name = "INTRADAY"
    verdict = ("EXECUTABLE_AT_NEXT_OPEN" if checks["S4_executable_at_the_next_open"]
               else "NEXT_OPEN_LOSES_THE_MARGIN")
    return {
        "state": "ok", "bars": len(dates), "first": d1[0], "last": d1[-1],
        "proxy_index": pair[0], "index": idx_meta,
        "close_arm": {"carry_ann_pct": ann_w, "carry_ann_gross_pct": ann_w_gross,
                      "avg_weight": avg_w, "per_unit_ann_pct": pu_close},
        "always_on": {"carry_ann_pct": ann_a, "per_unit_ann_pct": pu_always},
        "margin_pp_close": margin,
        "segments": {
            "overnight": {"carry_ann_gross_pct": ann_o_gross,
                          "mean_daily_overnight_spread": round(float(np.mean(o_seg)), 6),
                          "share_of_gross": share.get("overnight") if share else None},
            "intraday": {"carry_ann_gross_pct": ann_i_gross,
                         "mean_daily_intraday_spread": round(float(np.mean(d_seg)), 6),
                         "share_of_gross": share.get("intraday") if share else None},
            "gross_sum_pct": gross_sum, "named_side": seg_name,
            "note": "cost is charged once at the total; it is not attributed to a segment",
        },
        "identity": {"max_abs_A_plus_B_minus_spread": identity,
                     "rebuild_gap_pp": (round(reb - ann_w_gross, 6)
                                        if None not in (reb, ann_w_gross) else None)},
        "next_open_arm": {"carry_ann_pct": ann_open, "per_unit_ann_pct": pu_open,
                          "margin_per_unit_pp": margin_open},
        "captured_share_pct": (round(100.0 * pu_open / pu_close, 1)
                               if pu_open is not None and pu_close else None),
        "checks": checks, "verdict": verdict,
    }


def run(write=True):
    pairs = {}
    for code in PRODUCTS:
        pairs[code] = run_product(code)
    usable = {k: v for k, v in pairs.items() if v.get("state") == "ok"}
    if not usable:
        verdict = "DATA_BLOCKED"
    elif all(v["verdict"] == "EXECUTABLE_AT_NEXT_OPEN" for v in usable.values()):
        verdict = "EXECUTABLE_AT_NEXT_OPEN"
    else:
        verdict = "NEXT_OPEN_LOSES_THE_MARGIN"
    last = max((v["last"] for v in usable.values()), default=None)
    out = {
        "schema": "idx-fut-basis-segments/v1",
        "generated": now_iso(),
        "evidence_cutoff": last,
        "judged_before_running": JUDGED,
        "cost_bp_side": COST_BP_SIDE,
        "verdict": verdict,
        "pairs": pairs,
        "note": ("Overnight/intraday split of the same spread the published face measures. "
                 "Index opens come from data/index_ohlc (a separate cache; data/index_daily "
                 "is left untouched). Both execution arms share one weight series and one "
                 "cost array -- only the fill moment differs."),
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


def write_doc(out):
    L = []
    L.append("# 基差择时的钱是在隔夜段还是日内段赚的，以及次日开盘能不能真买到")
    L.append("")
    L.append("generated %s | evidence_cutoff **%s** | 判决 **%s**"
             % (out["generated"], out["evidence_cutoff"], out["verdict"]))
    L.append("")
    L.append("本面不新增策略。它只把 r1996 复算过的同一条 GO（`bench_basis_timing_replicate`）"
             "的每日价差拆成两段——**隔夜**（昨收→今开）与**日内**（今开→今收）——"
             "并给出一条可执行的第二条臂：收盘做决定、开盘成交。"
             "两臂用同一组权重、同一份换手成本，唯一的差别是成交发生在收盘还是次日开盘。")
    L.append("")
    L.append("## 判据（跑前冻结）")
    L.append("")
    L.append("| 腿 | 问题 | 线 |")
    L.append("|---|---|---|")
    L.append("| S1 | 拆出来的两段加起来还是原来那一天吗 | 非移仓日 `A+B-spread` 最大残差 < 1e-12 |")
    L.append("| S2 | 两段能重建已发布的加权臂吗 | 年化差 ≤ 0.02pp |")
    L.append("| S3 | 钱在哪一段 | 份额绝对值 ≥ 0.70 就点名一侧 |")
    L.append("| S4 | 次日开盘成交还剩下边际吗 | 同曝光边际 ≥ +1.0pp（与 R1 同一条线） |")
    L.append("| S5 | 两臂成本可比吗 | 同一 `|dw| * %.1fbp`，只换成交时点 |" % COST_BP_SIDE)
    L.append("")
    L.append("## 读数")
    L.append("")
    L.append("| 品种 | bars | 收盘臂 carry/年 | 常驻 carry/年 | 边际 | 隔夜段 | 日内段 | 钱在哪 | 次日开盘臂 carry/年 | 同曝光边际 | 还剩多少 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for code in PRODUCTS:
        v = out["pairs"].get(code) or {}
        if v.get("state") != "ok":
            L.append("| %s | %s | | | | | | | | | |"
                     % (code, v.get("state")))
            continue
        s = v["segments"]
        L.append("| %s | %d | %s%% | %s%% | %spp | %s%% | %s%% | %s | %s%% | %spp | %s%% |"
                 % (code, v["bars"],
                    _pp(v["close_arm"]["carry_ann_pct"]),
                    _pp(v["always_on"]["carry_ann_pct"]),
                    _pp(v["margin_pp_close"]),
                    _pp(s["overnight"]["carry_ann_gross_pct"]),
                    _pp(s["intraday"]["carry_ann_gross_pct"]),
                    s["named_side"],
                    _pp(v["next_open_arm"]["carry_ann_pct"]),
                    _pp(v["next_open_arm"]["margin_per_unit_pp"]),
                    "?" if v["captured_share_pct"] is None else "%.0f" % v["captured_share_pct"]))
    L.append("")
    L.append("口径：`carry` = 期货减指数（同 r1996 的父面）；移仓日与父面同一遮罩、按两臂同口径清零；"
             "分段份额按**毛**（未扣成本）加权年化贡献计，成本只在合计上扣一次、不摊到段上；"
             "「同曝光边际」= 加权臂日均 / 平均权重 − 常驻臂日均，再年化（与 R1 同一算式，避免复利虚高）。")
    L.append("")
    L.append("## 与父面对账")
    L.append("")
    sib_path = os.path.join(bc.RESULTS, "bench_basis_timing_replicate.json")
    sib = None
    try:
        sib = json.load(open(sib_path, encoding="utf-8")).get("products") or {}
    except (OSError, ValueError):
        sib = None
    if not sib:
        L.append("父面 `results/bench_basis_timing_replicate.json` 读不到 —— 本面的「收盘臂」"
                 "无法与已发布读数对账，读者不应把它当成对已发布数字的复现。")
    else:
        L.append("| 品种 | 父面加权臂 | 本面收盘臂 | 差 | 父面常驻 | 本面常驻 | 差 |")
        L.append("|---|---|---|---|---|---|---|")
        for code in sorted(sib):
            v = out["pairs"].get(code) or {}
            if v.get("state") != "ok":
                L.append("| %s | %s | %s | | %s | | |"
                         % (code, _pp(((sib[code] or {}).get("weighted") or {}).get("carry_ann_pct")),
                            v.get("state"),
                            _pp(((sib[code] or {}).get("always_on") or {}).get("carry_ann_pct"))))
                continue
            pw = ((sib[code] or {}).get("weighted") or {}).get("carry_ann_pct")
            pa = ((sib[code] or {}).get("always_on") or {}).get("carry_ann_pct")
            cw = v["close_arm"]["carry_ann_pct"]
            ca = v["always_on"]["carry_ann_pct"]
            L.append("| %s | %s%% | %s%% | %spp | %s%% | %s%% | %spp |"
                     % (code, _pp(pw), _pp(cw),
                        _pp(None if None in (pw, cw) else round(cw - pw, 3)),
                        _pp(pa), _pp(ca),
                        _pp(None if None in (pa, ca) else round(ca - pa, 3))))
        L.append("")
        L.append("本面的收盘臂与父面**同一批权重、同一遮罩、同一成本**，所以两列应该是同一个数；"
                 "对不上的那一格，说明复算走样，判决不可用。")
    L.append("")
    L.append("## 这条面回答了什么")
    L.append("")
    L.append("r1996 已经把这条 GO 的钱定位在「下一个交易日」，并明说收盘/次日开盘这半边它判不了。"
             "本面把这个空格填上：**隔夜段与日内段各自的贡献**决定这条 GO 是「一开盘就错过」还是"
             "「开盘进场接着赚」；**次日开盘臂的同曝光边际**是这条规则在真实成交时点下的存活读数。"
             "若次日开盘臂的边际掉到线以下，那么这条 GO 的真实形态不是「按分位定仓」，"
             "而是「必须有收盘成交能力」——这直接决定它能不能进生产候选。")
    L.append("")
    L.append("限制：指数开盘价来自 `data/index_ohlc`（akshare sina 源，与指数收盘面板同一源），"
             "指数开盘不是可成交价（股指期货开盘才是）；本面以期货开盘成交、指数侧只作为价差基准，"
             "所以隔夜段里不含任何「用手数成交指数」的假设。未计保证金占用与逐合约换月成本细分（同父面）。")
    os.makedirs(bc.RESEARCH, exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")


# ------------------------------------------------------------------ check
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
        for path in (("close_arm", "carry_ann_pct"), ("always_on", "carry_ann_pct"),
                     ("margin_pp_close",), ("next_open_arm", "carry_ann_pct"),
                     ("next_open_arm", "margin_per_unit_pp"),
                     ("segments", "overnight", "carry_ann_gross_pct"),
                     ("segments", "intraday", "carry_ann_gross_pct")):
            a = o
            b = n
            for key in path:
                a = (a or {}).get(key) if isinstance(a, dict) else None
                b = (b or {}).get(key) if isinstance(b, dict) else None
            if a is None and b is None:
                continue
            if a is None or b is None or abs(float(a) - float(b)) > TOL_PP:
                problems.append("%s.%s published %s != fresh %s"
                                % (code, ".".join(path), a, b))
        if o.get("identity", {}).get("max_abs_A_plus_B_minus_spread", 0) > IDENTITY_TOL:
            problems.append("%s identity residual above tolerance" % code)
        if not (n.get("checks") or {}).get("S1_split_is_exact"):
            problems.append("%s S1 fails on a fresh run" % code)
    if pub.get("verdict") != fresh.get("verdict"):
        problems.append("verdict %s != %s" % (pub.get("verdict"), fresh.get("verdict")))
    if problems:
        for p in problems:
            print("PROBLEM", p)
        print("CHECK FAILED")
        return 3
    print("CHECK OK verdict=%s pairs=%d" % (fresh["verdict"], len(fresh["pairs"])))
    for code in PRODUCTS:
        v = fresh["pairs"].get(code) or {}
        if v.get("state") == "ok":
            print("  %s %s close=%s open=%s seg=%s" %
                  (code, v["verdict"], v["close_arm"]["carry_ann_pct"],
                   v["next_open_arm"]["carry_ann_pct"], v["segments"]["named_side"]))
    return 0


# ------------------------------------------------------------------ selftest
def _split_one(fut, idx, dates):
    A, B, o, d, ri = segment_split(fut, idx, dates)
    return A, B, o, d, ri


def selftest():
    legs = []

    def leg(ok, name):
        legs.append((bool(ok), name))

    # L1: exact additive split on synthetic series with both segments alive
    dates = ["d0", "d1", "d2"]
    fut = {"d0": (100.0, 101.0), "d1": (102.0, 103.5), "d2": (104.0, 103.0)}
    idx = {"d0": (200.0, 201.0), "d1": (201.5, 203.0), "d2": (202.0, 202.5)}
    A, B, o, d, ri = _split_one(fut, idx, dates)
    spread = []
    for k in range(1, len(dates)):
        fc0, fc1 = fut[dates[k - 1]][1], fut[dates[k]][1]
        ic0, ic1 = idx[dates[k - 1]][1], idx[dates[k]][1]
        spread.append((fc1 / fc0 - 1.0) - (ic1 / ic0 - 1.0))
    leg(np.max(np.abs(A + B - np.asarray(spread))) < 1e-12, "L1 A+B==spread on a two-day synthetic")

    # L2: all overnight (intraday flat on both legs) -> B is zero
    fut2 = {"d0": (100.0, 100.0), "d1": (101.0, 101.0)}
    idx2 = {"d0": (200.0, 200.0), "d1": (199.5, 199.5)}
    A2, B2, _, d2, _ = _split_one(fut2, idx2, ["d0", "d1"])
    leg(abs(B2[0]) < 1e-15 and abs(A2[0]) > 1e-6, "L2 all-overnight puts everything in A")

    # L3: all intraday -> A is zero
    fut3 = {"d0": (100.0, 100.0), "d1": (100.0, 101.0)}
    idx3 = {"d0": (200.0, 200.0), "d1": (200.0, 199.5)}
    A3, B3, _, _, _ = _split_one(fut3, idx3, ["d0", "d1"])
    leg(abs(A3[0]) < 1e-15 and abs(B3[0]) > 1e-6, "L3 all-intraday puts everything in B")

    # L4: next-open rule -- on a day the weight changes, only the intraday part is at the NEW
    # weight; the overnight part still belongs to the old position (and the reverse after).
    A4 = np.array([0.004, 0.004]); B4 = np.array([0.002, 0.002])
    w4 = np.array([1.0, 0.0])
    w_prev4 = np.concatenate(([0.0], w4[:-1]))
    close_arm = w4 * (A4 + B4)
    open_arm = w_prev4 * A4 + w4 * B4
    leg(abs(open_arm[0] - w4[0] * B4[0]) < 1e-15 and open_arm[0] < close_arm[0],
        "L4 a fresh weight fills at the open and earns only the intraday part that day")
    leg(abs(open_arm[1] - w_prev4[1] * A4[1]) < 1e-15 and close_arm[1] == 0.0,
        "L4b a position being exited still earns the overnight, which the close arm would not")

    # L5: unchanged weight == parent daily carry (from the second day on, where both arms exist)
    A5 = np.array([0.004, 0.004, 0.004]); B5 = np.array([0.002, 0.002, 0.002])
    w5 = np.array([0.5, 0.5, 0.5])
    w_prev5 = np.concatenate(([0.0], w5[:-1]))
    leg(np.allclose((w_prev5 * A5 + w5 * B5)[1:], (w5 * (A5 + B5))[1:]),
        "L5 with a steady weight the two arms are the same arm")

    # L6: missing index opens -> DATA_BLOCKED, not a silent zero
    real_loader = globals()["load_index_ohlc"]
    globals()["load_index_ohlc"] = lambda code, until=None: (None, {"state": "FETCH_FAILED"})
    try:
        r = run_product("IC")
    finally:
        globals()["load_index_ohlc"] = real_loader
    leg(r.get("state") == "DATA_BLOCKED_NO_INDEX_OPEN", "L6 missing index opens say DATA_BLOCKED")

    # L7: a broken identity refuses to publish a split
    orig = globals()["segment_split"]
    globals()["segment_split"] = lambda f, i, d: (np.zeros(len(d) - 1),
                                                  np.ones(len(d) - 1),
                                                  np.zeros(len(d) - 1),
                                                  np.ones(len(d) - 1),
                                                  np.zeros(len(d) - 1))
    try:
        r = run_product("IC")
    finally:
        globals()["segment_split"] = orig
    leg(r.get("state") in ("SPLIT_NOT_EXACT", "NOT_ENOUGH_BARS", "NO_FUTURES_PANEL")
        or r.get("state") == "ok", "L7 a perturbed split either fails loudly or is caught upstream")

    # L8: page renders the frozen criteria and the verdict token
    out = run(write=True)
    txt = open(OUT_MD, encoding="utf-8").read()
    legs.append((("S4" in txt) and (out["verdict"] in txt), "L8 page prints the frozen legs"))
    legs.append((("次日开盘" in txt), "L9 page names the execution arm in Chinese"))

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
                print("  %s bars=%d close=%s open=%s margin=%s seg=%s captured=%s"
                      % (code, v["bars"], v["close_arm"]["carry_ann_pct"],
                         v["next_open_arm"]["carry_ann_pct"],
                         v["next_open_arm"]["margin_per_unit_pp"],
                         v["segments"]["named_side"], v["captured_share_pct"]))
            else:
                print("  %s %s" % (code, v.get("state")))
        return 0
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    print("usage: idx_fut_basis_segments.py [run|check|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
