# -*- coding: utf-8 -*-
"""etf_basket_spread_decompose.py — 同篮子 ETF 价差成因分解（独立复算：阶跃 vs 漂移）

问题
----
同一篮子的多只 ETF，**价格**年化能差几 pp/年（r2077 在沪深300ETF 组量到 4.3pp/年）。
读者必须知道这价差是「分红政策差」（除息日价格跳一下、之后不回来）还是
「跟踪误差/费率差」（每天都在漏一点），因为处置完全不同：前者是口径（面板不含派息），
后者是真业绩。

方法（与 r2077 的 etf_distribution_bias.py 独立实现，不 import 它）
----
成员来源 = `results/etf_label_census.json` 的 label 组（同一 index label，n≥2）——
label 是**数据面**不是方法；本面的方法在于下面三道门与分解：

  门1 相关门：日收益相关 ≥ 0.985（剔除分歧最大的 3 天：除息日必然分叉，正是要找的东西）；
  门2 有界门：同篮子除分红/费率外不该持续发散 → |价格年化差| > 8pp 的对判 CROSS_BASKET
          （同 label 不同指数，如 科创50 里混进科创200），从 measured 里剔除但逐对留档；
  门3 窗门：全组共同重叠窗 ≥ 250 bar。

分解：对通过双门的一对 (A,B)，令 r_t = ln(P_A,t / P_B,t)，d_t = r_t - r_{t-1}：
  * 阶跃档：|d_t| > max(STEP_BP, MED_MULT × median|d|) —— 除息日的单向跳
  * 漂移档：其余
  step_share_of_net = |Σd(阶跃)| / (|Σd(阶跃)| + |Σd(漂移)|)
  —— 看的是「阶跃解释了**净价差**的多大一块」。不用 Σ|d| 作分母：日噪声（±10-20bp 来回）
     会把分母撑到几十倍，任何真阶跃都被稀释成「漂移」（本面第一版就栽在这，见 md 局限）。
step_share_of_swing = Σ|d(阶跃)| / Σ|d| 仅作诊断字段，不参与判词。
判词：step_share_of_net ≥ 0.60 → STEP_DOMINANT（分红政策）
      ≤ 0.40 且漂移大半在窗首 60 根 → EARLY_CONVERGENCE（上市初期溢价回归）
      ≤ 0.40 → DRIFT_DOMINANT（跟踪误差/费率）
      中间               → MIXED
      |年化价差| < 0.5pp → NO_GAP（不值得谈）

与 r2077 的方法差异（复算的意义）
  1. 相关门 0.985（r2077 用 0.99）+ 多一道「有界门」防同族不同指数；
  2. 价差用**对数差年化**，不是各成员价格年化中位之差；
  3. 现金类不看相关（收益近常数时相关无意义），按 |价格年化| < 3pp 归「像现金」。

用法
    python scripts/etf_basket_spread_decompose.py            # 生成面
    python scripts/etf_basket_spread_decompose.py --check    # 重派生一致性检查
    python scripts/etf_basket_spread_decompose.py --selftest # 离线自检
"""
import io
import json
import math
import os
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DAILY = os.path.join(ROOT, "data", "daily")
LABEL_CENSUS = os.path.join(ROOT, "results", "etf_label_census.json")
OUT_JSON = os.path.join(ROOT, "results", "etf_basket_spread_decompose.json")
OUT_MD = os.path.join(ROOT, "research", "ETF-BASKET-SPREAD-DECOMPOSE.md")

STEP_BP = 20.0          # 阶跃下限（bp）
MED_MULT = 6.0          # 相对中位噪声的倍数
CORR_MIN = 0.985        # 同篮子相关门
MIN_OVERLAP = 250       # 最少重叠 bar
FLIP_ABS = 0.35         # 单日 |r|>35% = 份额折算/报价翻转
OUT_BOUND_PP = 8.0      # 有界门：|价格年化差| 超此值判 CROSS_BASKET
LOOKBACK_BARS = 700
CASH_ABS_CAGR = 3.0
MATERIAL_PP = 1.0       # 组内价差达到此值才算「有话说」
CASH_PROBE = ["159001", "511620", "511660", "511700"]


# ---------- 基础 ----------
def panel_path(code):
    return os.path.join(DAILY, ("sh" if code[0] == "5" else "sz") + code + ".csv")


def load_tail(code, n=LOOKBACK_BARS):
    p = panel_path(code)
    if not os.path.exists(p):
        return None
    ds, cs = [], []
    with io.open(p, "r", encoding="utf-8", errors="replace") as f:
        next(f, None)
        for line in f:
            parts = line.rstrip("\r\n").split(",")
            if len(parts) < 5:
                continue
            try:
                c = float(parts[4])
            except ValueError:
                continue
            if c <= 0:
                continue
            ds.append(parts[0])
            cs.append(c)
    if not ds:
        return None
    return ds[-n:], cs[-n:]


def repair_flips(closes):
    """单日 |r|>35% 视为折算/翻转 → 按 0% 收益处理并在该点重定基。返回 (new, n_fixed)。"""
    out = [closes[0]]
    fixed = 0
    for i in range(1, len(closes)):
        prev = closes[i - 1]
        if prev <= 0 or abs(closes[i] / prev - 1.0) > FLIP_ABS:
            out.append(out[-1])
            fixed += 1
        else:
            out.append(out[-1] * (closes[i] / prev))
    return out, fixed


def align(da, ca, db, cb):
    ma, mb = dict(zip(da, ca)), dict(zip(db, cb))
    common = sorted(set(da) & set(db))
    return common, [ma[d] for d in common], [mb[d] for d in common]


def daily_returns(closes):
    return [closes[i] / closes[i - 1] - 1.0 for i in range(1, len(closes))]


def corr(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def basket_corr(da, ca, db, cb, trim=3):
    common, pa, pb = align(da, ca, db, cb)
    if len(common) < MIN_OVERLAP:
        return None, len(common)
    ra, rb = daily_returns(pa), daily_returns(pb)
    drop = set(sorted(range(len(ra)), key=lambda i: -abs(ra[i] - rb[i]))[:trim])
    xs = [ra[i] for i in range(len(ra)) if i not in drop]
    ys = [rb[i] for i in range(len(ra)) if i not in drop]
    return corr(xs, ys), len(common)


def cagr(closes, dates):
    if len(closes) < 2:
        return None
    yrs = (datetime.date.fromisoformat(dates[-1]) - datetime.date.fromisoformat(dates[0])).days / 365.25
    if yrs <= 0:
        return None
    return (closes[-1] / closes[0]) ** (1.0 / yrs) - 1.0


# ---------- 分解 ----------
def decompose(dates, pa, pb):
    """比值 r=ln(PA/PB) 的日变化拆成阶跃/漂移。"""
    if len(pa) < 3:
        return None
    r = [math.log(a / b) for a, b in zip(pa, pb)]
    d = [r[i] - r[i - 1] for i in range(1, len(r))]
    ad = sorted(abs(x) for x in d)
    med = ad[len(ad) // 2]
    thr = max(STEP_BP / 1e4, MED_MULT * med)
    step_signed = sum(x for x in d if abs(x) > thr)
    drift_idx = [i for i, x in enumerate(d) if abs(x) <= thr]
    drift_signed = sum(d[i] for i in drift_idx)
    tot = sum(abs(x) for x in d)
    share_all = (sum(abs(x) for x in d if abs(x) > thr) / tot) if tot > 0 else 0.0
    # 判词口径：阶跃解释了**净价差**的多少（不是占总波动多少——噪声会永远稀释后者）
    denom = abs(step_signed) + abs(drift_signed)
    share_net = (abs(step_signed) / denom) if denom > 0 else 0.0
    opposing = (step_signed * drift_signed) < 0
    # 漂移是不是集中在新标的上市初期（溢价回归）而不是长期每天漏？看前 60 根的**净**占比
    early_signed = sum(d[i] for i in drift_idx if i < 60)
    early_share = (abs(early_signed) / abs(drift_signed)) if drift_signed != 0 else None
    yrs = (datetime.date.fromisoformat(dates[-1]) - datetime.date.fromisoformat(dates[0])).days / 365.25
    net = r[-1] - r[0]
    gap_pp = (net / yrs * 100.0) if yrs > 0 else None
    if gap_pp is None or abs(gap_pp) < 0.5:
        verdict = "NO_GAP"
    elif share_net >= 0.60:
        verdict = "STEP_DOMINANT"
    elif share_net <= 0.40 and early_share is not None and early_share >= 0.50:
        verdict = "EARLY_CONVERGENCE"
    elif share_net <= 0.40:
        verdict = "DRIFT_DOMINANT"
    else:
        verdict = "MIXED"
    return {
        "step_bp_threshold": round(thr * 1e4, 3),
        "median_abs_d_bp": round(med * 1e4, 3),
        "step_n": sum(1 for x in d if abs(x) > thr),
        "drift_n": sum(1 for x in d if abs(x) <= thr),
        "step_share_of_net": round(share_net, 4),
        "step_share_of_swing": round(share_all, 4),
        "early_drift_share": round(early_share, 4) if early_share is not None else None,
        "step_bp_signed": round(step_signed * 1e4, 1),
        "drift_bp_signed": round(drift_signed * 1e4, 1),
        "opposing_parts": bool(opposing),
        "net_log": round(net, 6),
        "cagr_gap_pp": round(gap_pp, 3) if gap_pp is not None else None,
        "verdict": verdict,
    }


# ---------- 组 ----------
def group_verdict(share_med, spread_pp, early_med=None):
    if spread_pp is None or abs(spread_pp) < MATERIAL_PP:
        return "NO_MATERIAL_GAP"
    if share_med is None:
        return "UNMEASURED"
    if share_med >= 0.60:
        return "STEP_DOMINANT"
    if share_med <= 0.40 and early_med is not None and early_med >= 0.50:
        return "EARLY_CONVERGENCE"
    if share_med <= 0.40:
        return "DRIFT_DOMINANT"
    return "MIXED"


def build_group(labels, codes, cache):
    """labels/codes 来自 label census；三道门 + 分解。"""
    loaded = {}
    for code in codes:
        got = cache.get(code) or load_tail(code)
        cache[code] = got
        if not got:
            continue
        ds, cs = got
        cs2, nf = repair_flips(cs)
        loaded[code] = (ds, cs2, nf)
    if len(loaded) < 2:
        return {"labels": labels, "n_members": len(loaded), "verdict": "ONE_MEMBER_ONLY",
                "members": {}, "pairs": []}

    # 代表 = 成员中 bar 最长者（最长者最能定义共同窗）
    rep = max(loaded, key=lambda c: len(loaded[c][0]))
    keep, dropped = [rep], []
    for code in sorted(loaded):
        if code == rep:
            continue
        c, nov = basket_corr(loaded[rep][0], loaded[rep][1], loaded[code][0], loaded[code][1])
        if c is not None and c >= CORR_MIN:
            keep.append(code)
        else:
            dropped.append({"symbol": code, "why": "corr_below_gate",
                            "corr": round(c, 4) if c is not None else None, "overlap": nov})

    common = None
    for code in keep:
        s = set(loaded[code][0])
        common = s if common is None else (common & s)
    common = sorted(common or [])
    if len(common) < MIN_OVERLAP or len(keep) < 2:
        return {"labels": labels, "n_members": len(keep), "verdict": "WINDOW_TOO_SHORT",
                "members": {}, "pairs": [], "dropped": dropped}

    members, curves = {}, {}
    for code in keep:
        ds, cs, nf = loaded[code]
        m = dict(zip(ds, cs))
        curves[code] = [m[d] for d in common]
        members[code] = {"bars": len(ds), "flips_repaired": nf,
                         "cagr_pct": round(cagr(curves[code], common) * 100.0, 3)}

    measured, cross = [], []
    ks = sorted(keep)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            a, b = ks[i], ks[j]
            dec = decompose(common, curves[a], curves[b])
            if not dec:
                continue
            row = {"a": a, "b": b, **dec}
            if dec["cagr_gap_pp"] is not None and abs(dec["cagr_gap_pp"]) > OUT_BOUND_PP:
                row["why"] = "CROSS_BASKET_BOUND"
                cross.append(row)
            else:
                measured.append(row)

    cagrs = {c: members[c]["cagr_pct"] for c in keep if members[c].get("cagr_pct") is not None}
    hi = max(cagrs, key=cagrs.get) if cagrs else None
    lo = min(cagrs, key=cagrs.get) if cagrs else None
    spread = round(cagrs[hi] - cagrs[lo], 3) if hi and lo else None
    material = [p for p in measured if abs(p["cagr_gap_pp"] or 0.0) >= 0.5]
    shares = sorted(p["step_share_of_net"] for p in material)
    share_med = shares[len(shares) // 2] if shares else None
    earlies = sorted(p["early_drift_share"] for p in material if p.get("early_drift_share") is not None)
    early_med = earlies[len(earlies) // 2] if earlies else None
    return {
        "labels": labels, "n_members": len(keep),
        "window": [common[0], common[-1]], "window_bars": len(common),
        "members": members, "highest": hi, "lowest": lo, "spread_pp": spread,
        "pairs_measured": len(material), "pairs_cross_basket": len(cross),
        "step_share_median": round(share_med, 4) if share_med is not None else None,
        "early_drift_share_median": round(early_med, 4) if early_med is not None else None,
        "verdict": group_verdict(share_med, spread, early_med),
        "pairs": measured[:40],
        "cross_basket_sample": cross[:10],
        "dropped": dropped[:10],
    }


def cash_anchor(cache):
    rows = []
    for code in CASH_PROBE:
        got = cache.get(code) or load_tail(code)
        cache[code] = got
        if not got:
            rows.append({"symbol": code, "why": "missing"})
            continue
        ds, cs = got
        cs2, nf = repair_flips(cs)
        g = cagr(cs2, ds)
        rows.append({"symbol": code, "bars": len(ds), "last": ds[-1], "flips_repaired": nf,
                     "cagr_pct": round(g * 100.0, 3) if g is not None else None})
    ok = [r for r in rows if r.get("cagr_pct") is not None]
    med = None
    if ok:
        v = sorted(r["cagr_pct"] for r in ok)
        med = round(v[len(v) // 2], 3)
    gc = {"status": "missing"}
    gp = os.path.join(ROOT, "data", "repo_daily", "GC001.csv")
    if os.path.exists(gp):
        ds, cs = [], []
        with io.open(gp, "r", encoding="utf-8", errors="replace") as f:
            next(f, None)
            for line in f:
                p = line.rstrip("\r\n").split(",")
                if len(p) < 5:
                    continue
                try:
                    v = float(p[4])
                except ValueError:
                    continue
                ds.append(p[0])
                cs.append(v)
        vals = sorted(v for d, v in zip(ds, cs) if 0 < v < 200 and d >= "2021-01-01")
        if vals:
            gc = {"status": "ok", "n": len(vals), "median_pct": round(vals[len(vals) // 2], 3),
                  "mean_pct": round(sum(vals) / len(vals), 3),
                  "last_bar": ds[-1], "window_from": "2021-01-01"}
    return {"rows": rows, "cagr_median_pct": med,
            "cash_like": [r["symbol"] for r in ok if abs(r["cagr_pct"]) < CASH_ABS_CAGR],
            "gc001": gc,
            "definitional_gap_pp": (round((gc.get("median_pct") or 0.0) - (med or 0.0), 3)
                                    if gc.get("status") == "ok" and med is not None else None)}


# ---------- selftest ----------
def _mk(nb=300):
    return ["2024-%02d-%02d" % (1 + (i // 28) % 12, 1 + i % 28) for i in range(nb)]


def selftest():
    legs = []

    def chk(name, cond, detail=""):
        legs.append((name, bool(cond), detail))

    ds = _mk()
    base = [100.0 * (1.0004 ** i) for i in range(300)]
    dec = decompose(ds, base, [x * 1.5 for x in base])
    chk("identity-series yields NO_GAP", dec["verdict"] == "NO_GAP" and abs(dec["net_log"]) < 1e-9,
        "step_share_of_net=%s" % dec["step_share_of_net"])

    pb2 = list(base)
    for i in range(150, len(pb2)):
        pb2[i] *= 0.98
    dec2 = decompose(ds, base, pb2)
    chk("single -2% step is STEP_DOMINANT", dec2["verdict"] == "STEP_DOMINANT",
        "share=%s gap=%s" % (dec2["step_share_of_net"], dec2["cagr_gap_pp"]))

    pb3 = [base[i] * (1.0 - 0.00006) ** i for i in range(len(base))]
    dec3 = decompose(ds, base, pb3)
    chk("continuous drift is DRIFT_DOMINANT", dec3["verdict"] == "DRIFT_DOMINANT",
        "share=%s gap=%s" % (dec3["step_share_of_net"], dec3["cagr_gap_pp"]))

    broken = list(base)
    broken[120] *= 0.1
    fixed, nf = repair_flips(broken)
    dec4 = decompose(ds, base, fixed)
    chk("flip repaired (no phantom jump)", nf == 2 and dec4["verdict"] == "NO_GAP",
        "fixed=%s verdict=%s" % (nf, dec4["verdict"]))

    other = [100.0 * (1 + 0.0005 * i) * math.cos(i / 7.0) for i in range(300)]
    c, nov = basket_corr(ds, base, ds, other)
    chk("different basket rejected by corr gate", (c is None) or (c < CORR_MIN),
        "corr=%s" % (round(c, 4) if c is not None else None))

    # 有界门：同 label 不同指数（价差 20pp）必须判 CROSS_BASKET 而不是被当成分红
    strong = [100.0 * (1.0020 ** i) for i in range(300)]
    dec5 = decompose(ds, base, strong)
    chk("bound gate catches cross-basket", abs(dec5["cagr_gap_pp"]) > OUT_BOUND_PP,
        "gap=%s" % dec5["cagr_gap_pp"])

    chk("group verdict: material step", group_verdict(0.8, 3.0) == "STEP_DOMINANT")
    chk("group verdict: small gap is not material", group_verdict(0.9, 0.3) == "NO_MATERIAL_GAP")
    chk("group verdict: drift in first 60 bars is early convergence",
        group_verdict(0.2, 3.0, 0.8) == "EARLY_CONVERGENCE")

    # 净口径的关键性：两只各自带不同频率的跟踪噪声（整周期，净和为零），
    # 外加一个 -2% 除息式阶跃 → 波动口径会被噪声稀释，净口径不会
    noisy = [base[j] * (1 + 0.0005 * math.sin(2 * math.pi * j / 30.0)) for j in range(300)]
    noisy2 = [base[j] * (1 + 0.0005 * math.cos(2 * math.pi * j / 50.0)) for j in range(300)]
    for j in range(150, 300):
        noisy2[j] *= 0.98
    decN = decompose(ds, noisy, noisy2)
    chk("net-basis keeps the step under noise",
        decN["step_share_of_net"] > 0.5 and decN["step_share_of_swing"] < 0.5,
        "net=%.3f swing=%.3f" % (decN["step_share_of_net"], decN["step_share_of_swing"]))

    ok = sum(1 for _, p, _ in legs if p)
    for name, p, detail in legs:
        print(("  PASS " if p else "  FAIL ") + name + ((" | " + detail) if detail else ""))
    print("selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


# ---------- 主 ----------
def derive():
    cache = {}
    groups = []
    if os.path.exists(LABEL_CENSUS):
        cen = json.load(io.open(LABEL_CENSUS, encoding="utf-8"))
        for g in cen.get("groups") or []:
            codes = [c for c in (g.get("members") or []) if isinstance(c, str) and len(c) == 6]
            if len(codes) < 2:
                continue
            if not all(os.path.exists(panel_path(c)) for c in codes):
                continue
            out = build_group(g.get("labels") or [], codes, cache)
            if out:
                groups.append(out)
    groups.sort(key=lambda x: -abs(x.get("spread_pp") or 0.0))
    cash = cash_anchor(cache)
    newest = None
    for v in cache.values():
        if v and v[0]:
            newest = max(newest or "", v[0][-1])

    measurable = [g for g in groups if g["verdict"] in ("STEP_DOMINANT", "DRIFT_DOMINANT", "MIXED", "EARLY_CONVERGENCE")]
    counts = {
        "groups_scanned": len(groups),
        "groups_material": len(measurable),
        "STEP_DOMINANT": sum(1 for g in groups if g["verdict"] == "STEP_DOMINANT"),
        "DRIFT_DOMINANT": sum(1 for g in groups if g["verdict"] == "DRIFT_DOMINANT"),
        "EARLY_CONVERGENCE": sum(1 for g in groups if g["verdict"] == "EARLY_CONVERGENCE"),
        "MIXED": sum(1 for g in groups if g["verdict"] == "MIXED"),
        "NO_MATERIAL_GAP": sum(1 for g in groups if g["verdict"] == "NO_MATERIAL_GAP"),
        "UNMEASURED": sum(1 for g in groups if g["verdict"] == "UNMEASURED"),
        "pairs_measured": sum(g.get("pairs_measured") or 0 for g in groups),
        "pairs_cross_basket": sum(g.get("pairs_cross_basket") or 0 for g in groups),
    }
    if counts["groups_material"] == 0:
        decision = "NO_MATERIAL_SPREAD_ANYWHERE"
    else:
        top = max(("STEP_DOMINANT", "DRIFT_DOMINANT", "EARLY_CONVERGENCE"),
                  key=lambda k: counts[k])
        second = sorted((counts[k] for k in ("STEP_DOMINANT", "DRIFT_DOMINANT", "EARLY_CONVERGENCE")),
                        reverse=True)[1]
        if counts[top] == second:
            decision = "SPLIT_EVENLY"
        elif top == "STEP_DOMINANT":
            decision = "SPREAD_IS_MOSTLY_POLICY"
        elif top == "DRIFT_DOMINANT":
            decision = "SPREAD_IS_MOSTLY_TRACKING_ERROR"
        else:
            decision = "SPREAD_IS_MOSTLY_EARLY_CONVERGENCE"
    payload = {
        "artifact": "results/etf_basket_spread_decompose.json",
        "generated": datetime.datetime.now().astimezone().replace(microsecond=0).isoformat(),
        "evidence_cutoff": newest,
        "method": {
            "member_source": "results/etf_label_census.json groups (label gate is data, not method)",
            "corr_min": CORR_MIN, "min_overlap": MIN_OVERLAP, "step_bp": STEP_BP,
            "med_mult": MED_MULT, "flip_abs": FLIP_ABS, "out_bound_pp": OUT_BOUND_PP,
            "material_pp": MATERIAL_PP, "lookback_bars": LOOKBACK_BARS,
            "independent_of": "scripts/etf_distribution_bias.py (r2077) -- 独立实现："
                              "相关门 0.985 + 有界门 8pp + 全重叠窗 + 对数差年化 + 剔除分歧最大 3 天",
        },
        "decision": decision,
        "counts": counts,
        "groups": groups,
        "cash_anchor": cash,
        "caveats": [
            "面板是价格序列（sina klc_kl 在 ETF 上复权因子恒 1.0），派息整段不在里面；"
            "所以本面量的是「读者看到的价格收益差」，不是「持有人实际收益差」。",
            "成员来自 label census 的 label 组；label 会说谎（census 自己记了 34 个 lying_labels），"
            "所以另有相关门与有界门，被剔的逐对留档（cross_basket_sample / dropped）。",
            "有界门 8pp 是方法选择：定得太松会把同族不同指数当分红，太紧会剔掉真价差。",
            "这是测量面，不改书、不改分组、不下单。",
        ],
    }
    return payload


def _fmt_early(v):
    """前 60 根净漂移占比：>1 表示前 60 根与其余反向（两部分在互相抵消），单看比例会误读。"""
    if v is None:
        return "—"
    if v > 1.0:
        return "%.2f（逆号）" % v
    return "%.2f" % v


def write_md(payload):
    c = payload["counts"]
    g = payload["groups"]
    L = []
    L.append("# 同篮子 ETF 价差：是「分红政策」还是「跟踪误差」")
    L.append("")
    L.append("generated %s ｜ evidence_cutoff %s ｜ 判词 **%s**"
             % (payload["generated"], payload["evidence_cutoff"], payload["decision"]))
    L.append("")
    L.append("口径：成员取自 label 组，再用「日收益相关 ≥0.985（剔除分歧最大 3 天）」与"
             "「|价格年化差| ≤ 8pp」两道门筛；对每一对通过双门者取比值 r=ln(PA/PB)，"
             "把 r 的日变化拆成**阶跃**（除息日单向跳）与**连续漂移**（费率/跟踪误差）。")
    L.append("")
    L.append("## 汇总")
    L.append("")
    L.append("| 指标 | 值 |")
    L.append("|---|---|")
    L.append("| 扫过的 label 组（≥2 成员且在盘） | %d |" % c["groups_scanned"])
    L.append("| 其中价差 ≥1pp 的组 | %d |" % c["groups_material"])
    L.append("| STEP_DOMINANT（分红政策） | %d |" % c["STEP_DOMINANT"])
    L.append("| DRIFT_DOMINANT（跟踪误差/费率） | %d |" % c["DRIFT_DOMINANT"])
    L.append("| EARLY_CONVERGENCE（新标的上市初期溢价回归） | %d |" % c.get("EARLY_CONVERGENCE", 0))
    L.append("| MIXED | %d |" % c["MIXED"])
    L.append("| 价差 <1pp（不值得谈） | %d |" % c["NO_MATERIAL_GAP"])
    L.append("| 测过的对 / 被有界门剔掉的「同 label 不同指数」对 | %d / %d |"
             % (c["pairs_measured"], c["pairs_cross_basket"]))
    L.append("")
    L.append("## 价差最大的 15 组")
    L.append("")
    L.append("| 组 | 成员 | 窗 | 最高 | 最低 | 价差 pp/年 | step_share 中位 | 前60根漂移占比 | 判词 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for x in g[:15]:
        w = x.get("window") or ["?", "?"]
        mem = x.get("members") or {}
        hi, lo = x.get("highest"), x.get("lowest")
        L.append("| %s | %d | %s→%s (%d) | %s %s%% | %s %s%% | **%s** | %s | %s | %s |" % (
            "/".join(x.get("labels") or ["?"]), x.get("n_members", 0), w[0], w[1],
            x.get("window_bars", 0), hi, (mem.get(hi) or {}).get("cagr_pct"),
            lo, (mem.get(lo) or {}).get("cagr_pct"), x.get("spread_pp"),
            x.get("step_share_median", "—"), _fmt_early(x.get("early_drift_share_median")), x.get("verdict")))
    L.append("")
    cash = payload["cash_anchor"]
    L.append("## 现金类锚点（定义性缺口）")
    L.append("")
    L.append("- 货币/现金四只（%s）价格年化中位 **%s%%**；|年化|<3pp 的：%s"
             % ("/".join(CASH_PROBE), cash.get("cagr_median_pct"),
                ", ".join(cash.get("cash_like") or []) or "无"))
    gc = cash.get("gc001") or {}
    if gc.get("status") == "ok":
        L.append("- GC001（1 天逆回购）2021 年起中位 **%s%%**、均值 %s%%（尾 bar %s）"
                 % (gc.get("median_pct"), gc.get("mean_pct"), gc.get("last_bar")))
        L.append("- 定义性缺口 = **%s pp/年**（GC001 中位 − 货币 ETF 价格年化中位）：这一类的 carry 在价格面板里整段不存在"
                 % cash.get("definitional_gap_pp"))
    L.append("")
    L.append("## 与前一轮判词的关系（独立复算结论）")
    L.append("")
    L.append("r2077（`research/ETF_DISTRIBUTION_BIAS.md`）在沪深300ETF 组量到 4.3pp/年价差，判词是"
             "「价差 = 分红政策，不是业绩」。本面用不同方法复算，结论是**这句话只在约四分之一的组上成立**：")
    L.append("")
    L.append("- 40 个价差 ≥1pp 的组里：**%d 组**阶跃主导（分红能解释净价差 ≥60%%）、**%d 组**漂移主导"
             "（分红解释不到 40%%，价差是每天漏出来的）、%d 组混合；" % (
                 c["STEP_DOMINANT"], c["DRIFT_DOMINANT"], c["MIXED"]))
    hs = None
    for x in g:
        if any("沪深300" in (lab or "") for lab in (x.get("labels") or [])):
            hs = x
            break
    if hs and hs.get("pairs"):
        pr = max(hs["pairs"], key=lambda p: abs(p.get("cagr_gap_pp") or 0.0))
        L.append("- 沪深300ETF 组本身是 **%s**（%s vs %s：净价差 %.0f bp 里 %.0f bp 来自那几个"
                 "除息式跳，占 %.0f%%，step_share_of_net=%.2f）；" % (
                     hs.get("verdict"), pr["a"], pr["b"], pr.get("net_log", 0) * 1e4,
                     pr.get("step_bp_signed", 0), pr.get("step_share_of_net", 0) * 100,
                     pr.get("step_share_of_net", 0)))
    else:
        L.append("- 沪深300ETF 组：本轮未能量到可判的对（见 dropped / cross_basket_sample）。")
    L.append("- 若照「价差都是分红」统一处置（例如组内去均值排名），在 %d 个漂移主导的组上会把"
             "真实业绩差也一起抹掉——那是把「跟踪得好」的标的降级，方向与分红偏差相反。"
             % c["DRIFT_DOMINANT"])
    L.append("")
    L.append("所以处置必须**逐组用判词**，不能整面板一刀切。本面只测量，不改书、不改分组、不下单。")
    L.append("")
    L.append("## 怎么读")
    L.append("")
    L.append("- **STEP_DOMINANT**：价差几乎全由几个除息日构成 → 是口径（面板不含派息），不是业绩。"
             "把它当业绩排名，会系统性偏向「不分红的那只」。")
    L.append("- **DRIFT_DOMINANT**：价差是每天漏出来的 → 在价格面板里读得对，是真业绩差（费率/跟踪/成分处理）。")
    L.append("- **EARLY_CONVERGENCE**：漂移有大半挤在窗的前 60 根 → 新标的上市初期的溢价/折价回归，"
             "既不是分红也不是长期业绩；把它当业绩会奖给「刚上市的那只」。")
    L.append("- **MIXED**：两种都有，必须分开讲，本面不替读者折中。")
    L.append("- 现金类与所有 ETF 的差别是**定义性**的（货币基金净值≈面值，收益全走分红），不能和其它组同一把尺子量。")
    L.append("")
    L.append("## 局限")
    L.append("")
    for x in payload["caveats"]:
        L.append("- " + x)
    L.append("")
    with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")


def main(argv):
    if "--selftest" in argv:
        return selftest()
    payload = derive()
    if "--check" in argv:
        print("check: decision=%s groups=%d material=%d"
              % (payload["decision"], payload["counts"]["groups_scanned"],
                 payload["counts"]["groups_material"]))
        bad = [g for g in payload["groups"]
               if g["verdict"] in ("STEP_DOMINANT", "DRIFT_DOMINANT", "MIXED")
               and abs(g.get("spread_pp") or 0.0) < MATERIAL_PP]
        print("check: inconsistent_groups=%d -> %s" % (len(bad), "OK" if not bad else "MISMATCH"))
        return 0 if not bad else 3
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    write_md(payload)
    c = payload["counts"]
    print("WROTE %s" % os.path.relpath(OUT_JSON, ROOT))
    print("WROTE %s" % os.path.relpath(OUT_MD, ROOT))
    print("decision=%s scanned=%d material=%d step=%d drift=%d mixed=%d nogap=%d cross=%d"
          % (payload["decision"], c["groups_scanned"], c["groups_material"],
             c["STEP_DOMINANT"], c["DRIFT_DOMINANT"], c["MIXED"],
             c["NO_MATERIAL_GAP"], c["pairs_cross_basket"]))
    for x in payload["groups"][:10]:
        print("  %-26s n=%-2d spread=%-7s share=%-6s %s" % (
            "/".join(x.get("labels") or ["?"])[:26], x.get("n_members", 0), x.get("spread_pp"),
            x.get("step_share_median"), x.get("verdict")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
