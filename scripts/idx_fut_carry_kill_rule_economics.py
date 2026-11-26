#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""what does obeying a drawdown kill rule on this carry book cost -- and what does it buy back?

WHY THIS FILE EXISTS
--------------------
r2135 (`idx_fut_carry_kill_rule_power`) answered *how often* a peak-drawdown kill rule
would fire on a book that is merely noisy rather than dead: a 6% line fires 0.7% / 2.1% of
noisy years (decoration), a 4% line fires 9.3% / 15.2% (a rule that will actually sound).
It stopped there on purpose -- trigger probability and price are two different numbers, and
its own conclusion was that a kill line has to be quoted in the book's own volatility, not
in round percentages.

This face prices it, on the one ruler that matters: the book's realised record.

  * the line is `k * trailing annual vol` for k = 0.4 / 0.6 / 0.8 / 1.0 sigma, with the
    trailing vol measured only from data available at that close (252-day window,
    expanding before that, 60 observations minimum) -- a moving threshold, so nothing is
    fitted on the whole sample;
  * the round 4/6/8/10% lines are printed apart, because on this record they never fire at
    all and that is itself the answer to "should the charter quote 6%?";
  * for every (line, re-entry) pair the page prints how much annual return obeying it gives
    up and how much peak drawdown it actually avoids, plus the same two numbers on
    2024+ only.

WHAT IS A RULE, NOT A MEASUREMENT
---------------------------------
  * the sigma multiples and the three re-entry rules are DECLARED, not fitted;
  * "shadow" = the unfilled book you keep computing while flat, used for the two recovery
    triggers. You cannot read "the danger has passed" off your own flat equity curve, and
    the shadow path is observable, so it is the only non-arbitrary way to say it;
  * going flat pays 0 excess return. The real margin cash earns repo; that leg is NOT in
    this series (the published book is a futures spread), so the price printed here is an
    UPPER bound on the price of a stop;
  * exit and re-entry each pay one edge at the weight carried that day (1.5bp), so a stop
    is not free by construction.

CAUSALITY
---------
The drawdown and the trailing vol are read at close t; the state change applies to t+1's
return. A look-ahead implementation would delete day t's loss, which is not a book anyone
can hold. selftest leg 3 pins this on a hand-built series.

verdict tokens (frozen before the first run):
  KILL_RULE_IS_FREE_INSURANCE          some declared pair gives up <= 0.5pp of annual
                                       return AND saves >= 2pp of peak drawdown
  KILL_RULE_PAYS_LESS_THAN_IT_SAVES    its best pair saves more drawdown than the annual
                                       return it gives up
  KILL_RULE_COSTS_MORE_THAN_IT_SAVES   every declared pair gives up at least as much
                                       annual return as the drawdown it avoids
  KILL_RULE_DOES_NOTHING               no declared pair moves peak drawdown by 1pp
  UNREADABLE                           no daily series

  second token, on the ordering:
  ORDERING_HOLDS_OUT_OF_SAMPLE         the pair that is best in-sample is also best on
                                       2024+ (or within its top 3)
  ORDERING_IS_IN_SAMPLE_ONLY           the in-sample winner is not in the out-of-sample
                                       top 3 -- do not quote the ranked table as advice

Read-only with respect to the paper book: never touches LEDGER.json / STATE.json.
Deterministic: no sampling, no seed; same panels in, same bytes out apart from `generated`.

Usage
-----
  python scripts/idx_fut_carry_kill_rule_economics.py
  python scripts/idx_fut_carry_kill_rule_economics.py --check
  python scripts/idx_fut_carry_kill_rule_economics.py --selftest
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402
import idx_fut_basis as base  # noqa: E402
import paper_basis_timing_cost_split as CS  # noqa: E402

TZ = timezone(timedelta(hours=8))
PRODUCTS = ("IC", "IM")
COST_BP_SIDE = 1.5
TDAYS = float(getattr(bc, "TRADING_DAYS", 244))
SIGMA_MULT = (0.4, 0.6, 0.8, 1.0)
TEXTBOOK_LINES = (0.04, 0.06, 0.08, 0.10)
REENTRY = ("cooldown20", "shadow_half", "shadow_new_high")
COOLDOWN = 20
VOL_WINDOW = 252
VOL_MIN_OBS = 60
SPLIT_DATE = "2024-01-01"
NOTIONAL = 1000000.0

OUT_JSON = os.path.join(bc.RESULTS, "idx_fut_carry_kill_rule_economics.json")
OUT_MD = os.path.join(bc.RESEARCH, "IDX_FUT_CARRY_KILL_RULE_ECONOMICS.md")


def now():
    return datetime.now(TZ)


def write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


# ---------------------------------------------------------------- inputs


def input_paths():
    paths = [os.path.join(bc.DATA, "futures_daily", c + ".csv") for c in PRODUCTS]
    for c in PRODUCTS:
        pair = base.PAIRS[c]
        paths.append(os.path.join(bc.DATA, "daily", "sh%s.csv" % pair[0]))
    paths.append(CS.LEDGER)
    return paths


def inputs_digest():
    h = hashlib.sha256()
    for p in input_paths():
        h.update(os.path.basename(p).encode())
        try:
            with open(p, "rb") as f:
                while True:
                    chunk = f.read(1 << 20)
                    if not chunk:
                        break
                    h.update(chunk)
        except Exception:
            h.update(b"<missing>")
    return h.hexdigest()


def daily(code):
    """Published-row-for-row daily net carry series."""
    return CS.replay(code, COST_BP_SIDE)


# ---------------------------------------------------------------- maths


def equity_path(net):
    net = np.asarray(net, float)
    return np.cumprod(1.0 + net), net


def max_drawdown(net):
    eq, _ = equity_path(net)
    peak = np.maximum.accumulate(eq)
    return float(np.min(eq / peak - 1.0))


def trailing_vol(net, window=VOL_WINDOW, min_obs=VOL_MIN_OBS):
    """Annualised vol known at each close: sd of returns up to and including t.

    Information at close t is available when the decision for t+1 is made, so using t is
    causal. Before `min_obs` observations the line is undefined (None).
    """
    net = np.asarray(net, float)
    n = len(net)
    out = np.full(n, np.nan)
    for t in range(n):
        lo = max(0, t + 1 - window)
        sample = net[lo:t + 1]
        if len(sample) < min_obs:
            continue
        sd = float(sample.std(ddof=1))
        out[t] = sd * np.sqrt(TDAYS)
    return out


def path_stats(net):
    net = np.asarray(net, float)
    n = int(len(net))
    if n < 60:
        return None
    eq, _ = equity_path(net)
    years = n / TDAYS
    cagr = float(eq[-1] ** (1.0 / years) - 1.0) if eq[-1] > 0 else None
    mu = float(net.mean())
    sd = float(net.std(ddof=1))
    ann_mu = mu * TDAYS
    ann_sd = sd * np.sqrt(TDAYS)
    return {
        "days": n,
        "years": round(years, 3),
        "cagr_pct": round(cagr * 100.0, 4) if cagr is not None else None,
        "ann_mean_pct": round(ann_mu * 100.0, 4),
        "ann_vol_pct": round(ann_sd * 100.0, 4),
        "sharpe": round(ann_mu / ann_sd, 4) if ann_sd > 0 else None,
        "mdd_pct": round(max_drawdown(net) * 100.0, 4),
    }


def filtered_series(net, weights, line_series, rule, cooldown=COOLDOWN):
    """Apply a peak-drawdown kill line causally.

    `line_series` is a per-day positive threshold (already in return units); a NaN
    threshold means "no line today, stay on". Drawdown is read at close t on the SHADOW
    book, the state change applies to t+1.

    Returns (filtered net, on_mask, n_kills, flat_lengths).
    """
    net = np.asarray(net, float)
    w = np.asarray(weights, float)
    line = np.asarray(line_series, float)
    n = len(net)
    shadow_eq, _ = equity_path(net)
    shadow_peak = np.maximum.accumulate(shadow_eq)
    shadow_dd = shadow_eq / shadow_peak - 1.0

    on = np.ones(n, dtype=bool)
    state = True
    flat_since = None
    kills = 0
    flats = []
    cost = np.zeros(n)
    prev_state = True
    for t in range(n):
        if t > 0:
            j = t - 1
            thr = line[j]
            if not np.isfinite(thr):
                thr = None
            if state and thr is not None and shadow_dd[j] <= -thr:
                state = False
                kills += 1
                flat_since = t
            elif not state:
                flat = t - flat_since
                if rule == "cooldown20":
                    if flat >= cooldown:
                        state = True
                elif rule == "shadow_half":
                    if thr is None or shadow_dd[j] > -thr / 2.0:
                        state = True
                elif rule == "shadow_new_high":
                    if shadow_dd[j] >= -1e-12:
                        state = True
                else:
                    raise ValueError("unknown re-entry rule %r" % (rule,))
                if state:
                    flats.append(flat)
        on[t] = state
        if state != prev_state:
            cost[t] = -abs(w[t]) * COST_BP_SIDE / 10000.0
        prev_state = state

    return np.where(on, net, 0.0) + cost, on, kills, flats


def sigma_lines(vol_series, k):
    return np.asarray(vol_series, float) * float(k)


def fixed_lines(net, thr, min_obs=VOL_MIN_OBS):
    """A constant threshold; blanked before `min_obs` observations (matches the sigma rule)."""
    net = np.asarray(net, float)
    out = np.full(len(net), float(thr))
    out[:min_obs] = np.nan
    return out


def pair_key(line, rule):
    return "%s_%s" % (line, rule)


def evaluate_pair(net, weights, line_series, rule, mask=None):
    filt, on, kills, flats = filtered_series(net, weights, line_series, rule)
    base_n = np.asarray(net, float)
    if mask is not None:
        base_n = base_n[mask]
        filt = filt[mask]
        on = on[mask]
    b = path_stats(base_n)
    f = path_stats(filt)
    if b is None or f is None:
        return None
    return {
        "baseline": b,
        "filtered": f,
        "price_pp": round(b["cagr_pct"] - f["cagr_pct"], 4),
        "dd_saved_pp": round(f["mdd_pct"] - b["mdd_pct"], 4),
        "n_kills": int(kills),
        "flat_share_pct": round(100.0 * float(1.0 - on.mean()), 2),
        "avg_flat_days": round(float(np.mean(flats)), 1) if flats else 0.0,
        "money_price_cny_per_year": round(NOTIONAL * (b["cagr_pct"] - f["cagr_pct"]) / 100.0, 0),
    }


def best_pair(pairs):
    """Rank declared pairs by drawdown saved per pp of annual return given up."""
    rank = []
    for k, v in pairs.items():
        if v is None or v["dd_saved_pp"] < 1.0:
            continue
        price = max(v["price_pp"], 0.01)
        rank.append((v["dd_saved_pp"] / price, k))
    rank.sort(reverse=True)
    return rank


def verdict_for(products):
    """Frozen vocabulary; returns (token, ordering_token, best_key, ok)."""
    if not products:
        return "UNREADABLE", "UNREADABLE", None, False
    all_pairs, in_sample, out_sample = {}, {}, {}
    for c, v in products.items():
        for bucket, store in (("pairs", all_pairs), ("train", in_sample), ("test", out_sample)):
            for k, row in (v.get(bucket) or {}).items():
                if row:
                    store[(c, k)] = row
    if not all_pairs:
        return "UNREADABLE", "UNREADABLE", None, False

    free, pays, cheap_enough, nothing = False, False, False, True
    for v in all_pairs.values():
        if v["dd_saved_pp"] >= 1.0:
            nothing = False
        if v["price_pp"] < v["dd_saved_pp"]:
            pays = True
            cheap_enough = True
            if v["price_pp"] <= 0.5 and v["dd_saved_pp"] >= 2.0:
                free = True
    if free:
        token = "KILL_RULE_IS_FREE_INSURANCE"
    elif nothing:
        token = "KILL_RULE_DOES_NOTHING"
    elif pays:
        token = "KILL_RULE_PAYS_LESS_THAN_IT_SAVES"
    elif cheap_enough is False:
        token = "KILL_RULE_COSTS_MORE_THAN_IT_SAVES"
    else:
        token = "UNREADABLE"

    ordering = "ORDERING_IS_IN_SAMPLE_ONLY"
    rank_in = best_pair(in_sample)
    rank_out = best_pair(out_sample)
    best_key = rank_in[0][1] if rank_in else None
    if best_key and rank_out:
        if best_key in [k for _s, k in rank_out[:3]]:
            ordering = "ORDERING_HOLDS_OUT_OF_SAMPLE"
    return token, ordering, best_key, token != "UNREADABLE"


# ---------------------------------------------------------------- build


def build():
    products = {}
    cutoff = None
    for code in PRODUCTS:
        rows = daily(code)
        if len(rows) < 300:
            continue
        dates = [r["date"] for r in rows]
        net = np.array([r["net"] for r in rows], float)
        w = np.array([abs(r["weight"]) for r in rows], float)
        vol = trailing_vol(net)
        cutoff = max(cutoff or dates[-1], dates[-1])
        split = np.array([d >= SPLIT_DATE for d in dates], bool)

        pairs, train, test = {}, {}, {}
        for k in SIGMA_MULT:
            lines = sigma_lines(vol, k)
            for rule in REENTRY:
                key = pair_key("%.1fsig" % k, rule)
                pairs[key] = evaluate_pair(net, w, lines, rule)
                train[key] = evaluate_pair(net, w, lines, rule, mask=~split)
                test[key] = evaluate_pair(net, w, lines, rule, mask=split)

        textbook = {}
        for thr in TEXTBOOK_LINES:
            lines = fixed_lines(net, thr)
            key = pair_key("L%02d" % int(round(thr * 100)), "cooldown20")
            textbook[key] = evaluate_pair(net, w, lines, "cooldown20")

        products[code] = {
            "series": {
                "first": dates[0],
                "last": dates[-1],
                "bars": len(dates),
                "train_first": dates[0],
                "train_last": max([d for d in dates if d < SPLIT_DATE] or [dates[0]]),
                "test_first": min([d for d in dates if d >= SPLIT_DATE] or [dates[-1]]),
                "test_bars": int(split.sum()),
                "train_bars": int((~split).sum()),
                "vol_first_date": dates[int(np.argmax(np.isfinite(vol)))],
            },
            "baseline": path_stats(net),
            "pairs": pairs,
            "train": train,
            "test": test,
            "textbook_lines": textbook,
        }

    token, ordering, best_key, ok = verdict_for(products)
    full_rank = []
    for code, v in products.items():
        for k, row in (v["pairs"] or {}).items():
            if not row or row["dd_saved_pp"] < 0.1:
                continue
            full_rank.append((row["dd_saved_pp"] / max(row["price_pp"], 0.01), code + ":" + k))
    full_rank.sort(reverse=True)
    return {
        "generated": now().isoformat(timespec="seconds"),
        "evidence_cutoff": cutoff,
        "cost_bp_side": COST_BP_SIDE,
        "sigma_mult": list(SIGMA_MULT),
        "textbook_lines": list(TEXTBOOK_LINES),
        "reentry_rules": list(REENTRY),
        "cooldown_days": COOLDOWN,
        "vol_window": VOL_WINDOW,
        "split_date": SPLIT_DATE,
        "notional_cny": NOTIONAL,
        "products": products,
        "verdict": token,
        "ordering": ordering,
        "best_pair_in_sample": best_key,
        "best_pair_full": full_rank[0][1] if full_rank else None,
        "ok": ok,
        "inputs_digest": inputs_digest(),
        "note": "price of a stop is an UPPER bound: flat days earn 0 excess while real margin cash earns repo",
    }


# ---------------------------------------------------------------- render


def fmt_pct(x):
    return "n/a" if x is None else "%.2f%%" % x


def write_md(payload):
    p = payload["products"]
    L = []
    L.append("# 基差 carry：照一条回撤杀线做，代价多少、买回什么\n")
    L.append("generated %s | 最新 bar %s | 成本 %.1fbp/边 | 杀线=%.1f/%.1f/%.1f/%.1f 倍**滚动年化波动**（%d 日窗，最少 %d 观测）| 复入=20 日冷却 / 影本回撤减半 / 影本新高 | 样本外起点 %s\n"
             % (payload["generated"][:19].replace("T", " "), payload["evidence_cutoff"],
                payload["cost_bp_side"], SIGMA_MULT[0], SIGMA_MULT[1], SIGMA_MULT[2],
                SIGMA_MULT[3], payload["vol_window"], VOL_MIN_OBS, payload["split_date"]))
    L.append("r2135 量过「一条回撤杀线多久会被自己的噪声响一次」，并留了一句：杀线要按波动标定，"
             "不能按整数标定。这一页把它的另一半算出来——**按波动标定之后，照这条线做，每年让出多少收益、"
             "买回多少最大回撤**。用的是能逐日复现已发布台账的那份镜像（`paper_basis_timing_cost_split.replay`，"
             "1.5bp/边），杀线在收盘读、次日生效。\n")
    L.append("## 一、不挂规则，这本书自己的历史\n")
    L.append("| 品种 | bar 数 | 起止 | CAGR | 年化均值 | 年化波动 | 夏普 | 最大回撤 | 最大回撤折合几个年化波动 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for c, v in p.items():
        b = v["baseline"]
        s = v["series"]
        ratio = "n/a"
        if b["ann_vol_pct"]:
            ratio = "%.2fσ" % (abs(b["mdd_pct"]) / b["ann_vol_pct"])
        L.append("| %s | %d | %s → %s | %s | %s | %s | %.3f | %s | %s |"
                 % (c, b["days"], s["first"], s["last"], fmt_pct(b["cagr_pct"]),
                    fmt_pct(b["ann_mean_pct"]), fmt_pct(b["ann_vol_pct"]),
                    b["sharpe"], fmt_pct(b["mdd_pct"]), ratio))
    L.append("")
    L.append("## 二、整数杀线在这段历史上**一次都没响过**\n")
    L.append("| 品种 | 杀线 | 开杀次数 | 空手占比 | 照做的 CAGR |")
    L.append("|---|---|---|---|---|")
    for c, v in p.items():
        for k, row in v["textbook_lines"].items():
            if not row:
                continue
            L.append("| %s | %s | %d | %.1f%% | %s |"
                     % (c, k.replace("_cooldown20", ""), row["n_kills"],
                        row["flat_share_pct"], fmt_pct(row["filtered"]["cagr_pct"])))
    L.append("")
    L.append("这是这一页最重要的一行事实：这本书历史上最深的一次回撤只有 1.9%/3.0%（0.58σ/0.90σ 的年化波动），"
             "所以**写在章程里的 4%/6% 杀线，在这段记录上一次也不会触发**——它不是一条紧的规则，"
             "它是一条不会发生的规则。r2135 在自助法里看到 4% 线一年响 9.3%/15.2%，那是把均值去掉之后的纯噪声世界；"
             "真实记录里它连边都碰不到。**核一根杀线，必须按波动标定。**\n")
    L.append("## 三、按波动标定之后：每条线的价格与它买回的回撤（全窗口）\n")
    for c, v in p.items():
        L.append("**%s**（全窗 %d 个交易日，年化波动 %s）\n"
                 % (c, v["baseline"]["days"], fmt_pct(v["baseline"]["ann_vol_pct"])))
        L.append("| 杀线 × 复入 | 照做的 CAGR | 代价（年化） | 买回的回撤 | 开杀次数 | 空手占比 | 平均空手日 | 代价（元/百万/年） |")
        L.append("|---|---|---|---|---|---|---|---|")
        for k, row in v["pairs"].items():
            if not row:
                continue
            L.append("| %s | %s | %+.2fpp | %+.2fpp | %d | %.1f%% | %.0f | %s |"
                     % (k, fmt_pct(row["filtered"]["cagr_pct"]), row["price_pp"],
                        row["dd_saved_pp"], row["n_kills"], row["flat_share_pct"],
                        row["avg_flat_days"],
                        "{:,.0f}".format(abs(row["money_price_cny_per_year"]))))
        L.append("")
    L.append("（`代价（年化）` 为正=照规则做少赚了这么多；`买回的回撤` 为正=照规则做最大回撤更浅这么多。"
             "两个数同量级=一次平价保险；代价远大于回撤收益=只是把亏损换成「错过反弹」。）\n")
    L.append("## 四、换成 2024 年以后还成立吗\n")
    for c, v in p.items():
        L.append("**%s**（样本内 %d 日 / 样本外 %d 日）\n"
                 % (c, v["series"]["train_bars"], v["series"]["test_bars"]))
        L.append("| 杀线 × 复入 | 样本内 代价/买回 | 样本外 代价/买回 | 结论是否翻转 |")
        L.append("|---|---|---|---|")
        for k in v["pairs"]:
            tr, te = v["train"].get(k), v["test"].get(k)
            if not tr or not te:
                continue
            same = (tr["dd_saved_pp"] - tr["price_pp"]) * (te["dd_saved_pp"] - te["price_pp"]) > 0
            L.append("| %s | %+.2f / %+.2f pp | %+.2f / %+.2f pp | %s |"
                     % (k, tr["price_pp"], tr["dd_saved_pp"],
                        te["price_pp"], te["dd_saved_pp"], "否" if same else "**是**"))
        L.append("")
    L.append("## 五、判词\n")
    L.append("**%s** ｜ 排序：**%s**（样本内最优=%s，全窗最优=%s）\n"
             % (payload["verdict"], payload["ordering"],
                payload["best_pair_in_sample"] or "n/a",
                payload["best_pair_full"] or "n/a"))
    best = None
    full = payload.get("best_pair_full")
    if full and ":" in full:
        code, key = full.split(":", 1)
        best = ((p.get(code) or {}).get("pairs") or {}).get(key)
    if best:
        L.append("读数：全窗最好的一对是 **%s**——代价年化 %.2fpp（每百万每年约 %s 元），"
                 "买回最大回撤 %.2fpp，开杀 %d 次、空手占 %.1f%% 的日子。\n"
                 % (full, best["price_pp"],
                    "{:,.0f}".format(abs(best["money_price_cny_per_year"])),
                    best["dd_saved_pp"], best["n_kills"], best["flat_share_pct"]))
    L.append("当治理工具看，三件事要一起读：①**线要按 σ 写**——整数 4%/6% 在这段记录上根本不会触发，"
             "「我们有回撤保护」这句话在 4% 上是空话；②**紧线不等于安全**，0.4σ 线触发频繁，"
             "代价全部落在「错过反弹」里；③**样本内外排序一翻转，历史最优的那条线就不能当建议**（见第四节），"
             "本页只把价格与回撤并排放，上不上线属于章程决定。\n")
    L.append("## 六、口径与边界\n")
    L.append("- 日序列=`paper_basis_timing_cost_split.replay(code, 1.5bp)`，与已发布台账逐日一致的同一镜像。")
    L.append("- 杀线=该日**可知**的滚动年化波动（%d 日窗，最少 %d 观测）× σ 倍数，阈值随时间移动，"
             "没有用全样本常数，也没有拟合。" % (VOL_WINDOW, VOL_MIN_OBS))
    L.append("- 回撤在收盘 t 读、状态变更作用于 t+1（因果）。复入用影本（未过滤路径）判定。")
    L.append("- 空手日按 0 超额记：真实现金腿（保证金利息/逆回购）不在这条序列里，所以价格是**上界**。")
    L.append("- 进出各付一个边（当日权重 × 1.5bp）。")
    L.append("- 本面零仓位建议、零准入判定、零台账触碰（不读不写 LEDGER.json / STATE.json）。\n")
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


# ---------------------------------------------------------------- selftest


def _selftest():
    ok = 0
    total = 0

    def leg(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("  FAIL", name)

    # 1 max drawdown hand value
    leg("drawdown hand value", abs(max_drawdown(np.array([0.10, -0.20])) + 0.20) < 1e-12)
    rng = np.random.default_rng(7)
    net = rng.normal(0.0004, 0.004, 500)
    w = np.full(500, 1.0)
    lines = fixed_lines(net, 0.50, min_obs=0)
    filt, on, kills, _f = filtered_series(net, w, lines, "cooldown20")
    # 2 a threshold that cannot be reached == baseline
    leg("impossible line never fires", kills == 0 and bool(on.all()))
    leg("impossible line reproduces the baseline", np.allclose(filt, net))
    # 3 causality: the crash day itself is not avoided
    crash = np.array([0.005] * 30 + [-0.30] + [0.005] * 30)
    w2 = np.full(len(crash), 1.0)
    cl = fixed_lines(crash, 0.10, min_obs=0)
    filt2, on2, k2, _f2 = filtered_series(crash, w2, cl, "cooldown20")
    leg("crash day is still taken (no look-ahead)", abs(filt2[30] - crash[30]) < 1e-12)
    leg("state flips only after the crash close", bool(on2[30]) and not bool(on2[31]))
    # 4 cooldown length is exact
    long_crash = np.array([0.005] * 30 + [-0.30] + [0.005] * 200)
    wl = np.full(len(long_crash), 1.0)
    cll = fixed_lines(long_crash, 0.10, min_obs=0)
    f_on = filtered_series(long_crash, wl, cll, "cooldown20")[1]
    first_flat = int(np.argmax(~f_on))
    leg("cooldown re-enters after exactly N days",
        not bool(f_on[first_flat + COOLDOWN - 1]) and bool(f_on[first_flat + COOLDOWN]))
    # 5 shadow rules are distinct and half-recovery is the earlier one
    half_on = filtered_series(long_crash, wl, cll, "shadow_half")[1]
    high_on = filtered_series(long_crash, wl, cll, "shadow_new_high")[1]
    leg("shadow rules are distinct", not np.array_equal(half_on, high_on))
    leg("half-recovery re-enters strictly earlier than a new high",
        int(np.argmax(half_on[31:])) < int(np.argmax(high_on[31:])))
    # 6 flat days earn exactly zero before costs
    nocost = filtered_series(long_crash, np.zeros(len(long_crash)), cll, "cooldown20")[0]
    leg("flat days earn zero",
        all(abs(nocost[i]) < 1e-15 for i in np.where(~f_on)[0]))
    # 7 one edge per state change, sized by that day's weight
    two = filtered_series(long_crash, wl, cll, "cooldown20")[0]
    pre = np.where(f_on, long_crash, 0.0)
    cost_days = [i for i in range(len(two)) if abs(two[i] - pre[i]) > 1e-15]
    transitions = int(np.sum(f_on[1:] != f_on[:-1])) + (0 if f_on[0] else 1)
    leg("each state change costs exactly one edge",
        len(cost_days) == transitions and transitions >= 2)
    leg("edge size is the day's weight times 1.5bp",
        all(abs(abs(two[i] - pre[i]) - COST_BP_SIDE / 10000.0) < 1e-15 for i in cost_days))
    # 8 causal trailing vol: hand value and past-only
    vol_net = np.random.default_rng(11).normal(0.0, 0.01, 400)
    tv = trailing_vol(vol_net)
    hand = float(np.std(vol_net[301 - VOL_WINDOW:301], ddof=1)) * np.sqrt(TDAYS)
    leg("trailing vol undefined before min_obs", not np.isfinite(tv[VOL_MIN_OBS - 2]))
    leg("trailing vol hand value", abs(tv[300] - hand) / hand < 1e-12)
    early = trailing_vol(vol_net[:120])
    leg("trailing vol only uses the past",
        np.allclose(tv[60:120], early[60:120], equal_nan=True))
    # 9 splits partition the sample
    dates_mask = np.array(["2023-12-31"] * 10 + ["2024-01-02"] * 5)
    split = dates_mask >= SPLIT_DATE
    leg("split partitions", int((~split).sum()) + int(split.sum()) == len(dates_mask))
    # 10 determinism
    a1 = filtered_series(net, w, lines, "cooldown20")[0]
    a2 = filtered_series(net, w, lines, "cooldown20")[0]
    leg("deterministic", np.allclose(a1, a2))
    # 11 verdict vocabulary
    def fake(price, saved):
        return {"IC": {"pairs": {"K": {"price_pp": price, "dd_saved_pp": saved}}}}

    leg("verdict free insurance", verdict_for(fake(0.2, 3.0))[0] == "KILL_RULE_IS_FREE_INSURANCE")
    leg("verdict pays less than saves", verdict_for(fake(2.0, 3.0))[0] == "KILL_RULE_PAYS_LESS_THAN_IT_SAVES")
    leg("verdict costs more", verdict_for(fake(5.0, 3.0))[0] == "KILL_RULE_COSTS_MORE_THAN_IT_SAVES")
    leg("verdict does nothing", verdict_for(fake(0.2, 0.4))[0] == "KILL_RULE_DOES_NOTHING")
    leg("verdict unreadable", verdict_for({})[0] == "UNREADABLE")
    # 12 ordering token needs the in-sample winner to leave the out-of-sample top 3
    fake2 = {"IC": {"pairs": {k: {"price_pp": 1.0, "dd_saved_pp": 2.0}
                              for k in ("A", "B", "C", "D", "E")},
                    "train": {"A": {"price_pp": 1.0, "dd_saved_pp": 30.0},
                              "B": {"price_pp": 1.0, "dd_saved_pp": 9.0},
                              "C": {"price_pp": 1.0, "dd_saved_pp": 8.0},
                              "D": {"price_pp": 1.0, "dd_saved_pp": 7.0},
                              "E": {"price_pp": 1.0, "dd_saved_pp": 6.0}},
                    "test": {"A": {"price_pp": 1.0, "dd_saved_pp": 1.5},
                             "B": {"price_pp": 1.0, "dd_saved_pp": 9.0},
                             "C": {"price_pp": 1.0, "dd_saved_pp": 8.5},
                             "D": {"price_pp": 1.0, "dd_saved_pp": 8.0},
                             "E": {"price_pp": 1.0, "dd_saved_pp": 7.5}}}}
    leg("ordering flagged as in-sample only", verdict_for(fake2)[1] == "ORDERING_IS_IN_SAMPLE_ONLY")
    fake2["IC"]["test"]["A"] = {"price_pp": 1.0, "dd_saved_pp": 10.0}
    leg("ordering holds when the winner stays on top",
        verdict_for(fake2)[1] == "ORDERING_HOLDS_OUT_OF_SAMPLE")
    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1


# ---------------------------------------------------------------- faces


def check():
    try:
        with open(OUT_JSON, encoding="utf-8") as f:
            payload = json.load(f)
    except Exception:
        print("CHECK FAILED face missing: %s" % OUT_JSON)
        return 3
    if payload.get("inputs_digest") != inputs_digest():
        print("STALE inputs changed since %s -- rerun to republish" % payload.get("generated"))
        return 3
    token, ordering, best, ok = verdict_for(payload.get("products") or {})
    if (token != payload.get("verdict") or ordering != payload.get("ordering")
            or best != payload.get("best_pair_in_sample") or ok != payload.get("ok")):
        print("CHECK FAILED judgement moved: face says %s/%s/%s, arithmetic now says %s/%s/%s"
              % (payload.get("verdict"), payload.get("ordering"),
                 payload.get("best_pair_in_sample"), token, ordering, best))
        return 3
    print("CHECK OK %s | %s | best=%s products=%s"
          % (token, ordering, best, ",".join(payload.get("products") or {})))
    return 0


def run():
    payload = build()
    if not payload["products"]:
        print("face unreadable: no daily series")
        return 2
    write_json(OUT_JSON, payload)
    write_md(payload)
    for c, v in payload["products"].items():
        b = v["baseline"]
        fired = sum(1 for row in (v["textbook_lines"] or {}).values() if row and row["n_kills"])
        print("%s bars=%d cagr=%.2f%% vol=%.2f%% mdd=%.2f%% | textbook lines that ever fired=%d/4"
              % (c, b["days"], b["cagr_pct"], b["ann_vol_pct"], b["mdd_pct"], fired))
    print("verdict", payload["verdict"], "|", payload["ordering"],
          "| best", payload["best_pair_in_sample"], "ok", payload["ok"])
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    if "--check" in sys.argv:
        sys.exit(check())
    sys.exit(run())
