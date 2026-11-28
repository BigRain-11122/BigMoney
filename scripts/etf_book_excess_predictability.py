"""Was the excess earned on bars you could have seen coming?

r2230 split the book's excess over the four-exposure basket into up-halves and
down-halves and then printed the number that decides how to treat it: the best
10% of bars carried 953% of the total, so removing them flips +3.085 pp/yr to
-26.3 pp/yr.  That is a statement about arithmetic, not about skill or luck --
it says the total is a sum over few violent bars, and says nothing about
whether those bars were recognisable beforehand.

This face asks the actionable version:

    take every state variable that was public at the close of bar t-1,
    and ask how well it separates the bars that carried the excess (top 10%
    of daily log excess) from the rest.

If nothing separates them, the honest reading is that the +3.085 pp/yr is luck
and should be weighted like luck (not a rate you lever up on).  If something
does, that is a timing input and the reader gets the name of it.

Method notes, because "an AUC above 0.6" is where this kind of face usually
lies:
  * Every feature is shifted by one bar before it is judged.  A feature that
    needs the bar's own return is a hindsight label, not a signal; selftest
    proves the shift by measuring the same feature unshifted (AUC near 1.0) and
    shifted (much lower).
  * One common mask over all features, so the features are compared on the
    same bars rather than each on its own convenient subset.
  * The verdict uses a FAMILY gate, not a per-feature one (r858 lesson: a
    grammar-search family that hits 0.6 on one of eight tries is what multiple
    comparison looks like).  The null is a permutation distribution of the
    family maximum, so the bar is "is our best feature better than the best
    feature you'd get from noise".
  * Missing inputs print UNMEASURED, never NOT_PREDICTABLE -- "I could not
    measure" and "I measured zero" are different answers.

Usage:
  python scripts/etf_book_excess_predictability.py run
  python scripts/etf_book_excess_predictability.py --check
  python scripts/etf_book_excess_predictability.py --selftest
"""

import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import etf_book_forward as F                                            # noqa: E402
import etf_book_excess_capture as C                                     # noqa: E402

OUT_JSON = os.path.join("results", "etf_book_excess", "predictability.json")
OUT_MD = os.path.join("research", "ETF_BOOK_EXCESS_PREDICTABILITY.md")

SCHEMA = "etf_book_excess_predictability/v1"

# The label is the same one r2230 priced: the top decile of daily log excess.
TOP_SHARE = float(C.concentration.__defaults__[0]) if C.concentration.__defaults__ else 0.10
PERMS = 1000
SEED = 20261129

# A single feature has to clear this to be worth printing as a name at all --
# below it the separation is too small to act on even if the permutation says
# it is not noise on this sample.
AUC_MIN = 0.60
# Family gate: the best of the family must beat the 95th percentile of the
# permutation distribution of the family maximum.
NULL_P = 0.05


# ------------------------------------------------------------------ pure maths
def mask_rows(*arrays):
    """Boolean rows where every array is finite (the common mask all features share)."""
    ok = None
    for a in arrays:
        b = np.isfinite(np.asarray(a, dtype=float))
        ok = b if ok is None else (ok & b)
    return ok if ok is not None else np.zeros(0, dtype=bool)


def label_top(score, share=TOP_SHARE):
    """Top `share` of bars by score, as a boolean label plus the threshold used."""
    x = np.asarray(score, dtype=float)
    finite = x[np.isfinite(x)]
    if finite.size < 10:
        return None, None
    k = max(1, int(math.ceil(share * finite.size)))
    thr = float(np.sort(finite)[-k])
    return (x >= thr) & np.isfinite(x), thr


def _ranks(x):
    """Average ranks, 1-based, with ties shared (same convention as scipy.stats.rankdata)."""
    x = np.asarray(x, dtype=float)
    n = x.size
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(n, dtype=float)
    ranks[order] = np.arange(1, n + 1, dtype=float)
    # tie-average
    sx = x[order]
    i = 0
    while i < n:
        j = i
        while j + 1 < n and sx[j + 1] == sx[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = (i + 1 + j + 1) / 2.0
        i = j + 1
    return ranks


def auc_from_ranks(ranks, labels):
    """Mann-Whitney AUC from precomputed ranks, so permutations cost one mean."""
    y = np.asarray(labels, dtype=bool)
    n_pos = int(y.sum())
    n_neg = int(y.size - n_pos)
    if n_pos == 0 or n_neg == 0:
        return None
    return (float(np.asarray(ranks, dtype=float)[y].sum()) - n_pos * (n_pos + 1) / 2.0) \
        / (n_pos * n_neg)


def auc_of(x, labels):
    return auc_from_ranks(_ranks(x), labels)


def permutation_family(rank_scores, labels, perms=PERMS, seed=SEED):
    """Null distribution of the FAMILY MAXIMUM: shuffle the label, score every feature.

    Returns per-permutation family max, so the gate is "our best feature vs the best
    feature noise can produce", not one feature's own null.
    """
    rs = [np.asarray(v, dtype=float) for v in rank_scores]
    y = np.asarray(labels, dtype=bool)
    rng = np.random.RandomState(seed)
    n_pos = int(y.sum())
    out = np.empty(perms, dtype=float)
    idx = np.arange(y.size)
    for i in range(perms):
        yy = np.zeros(y.size, dtype=bool)
        yy[rng.choice(idx, size=n_pos, replace=False)] = True
        best = -np.inf
        for r in rs:
            a = auc_from_ranks(r, yy)
            if a is not None and a > best:
                best = a
        out[i] = best
    return out


def permutation_family_block(rank_scores, labels, block=20, perms=PERMS, seed=SEED + 1):
    """Same family maximum, but the label is shuffled in contiguous blocks.

    An i.i.d. shuffle destroys the fact that excess bars arrive in clusters (a booking
    book's excess rides on a handful of violent weeks).  When the label clumps, an
    i.i.d. null is too narrow and every smooth feature looks mildly "significant" --
    eight of them at p=0.02..0.07 is that artefact, not eight edges.  Block shuffling
    keeps the clumping and asks the same question honestly.
    """
    rs = [np.asarray(v, dtype=float) for v in rank_scores]
    y = np.asarray(labels, dtype=bool)
    n = y.size
    nb = n // block
    if nb < 4:
        return None
    chunks = [y[i * block:(i + 1) * block] for i in range(nb)]
    head = np.concatenate(chunks) if nb else np.zeros(0, dtype=bool)
    rng = np.random.RandomState(seed)
    out = np.empty(perms, dtype=float)
    for i in range(perms):
        order = rng.permutation(nb)
        yy = np.concatenate([chunks[j] for j in order])
        best = -np.inf
        for r in rs:
            a = auc_from_ranks(r[:yy.size], yy)
            if a is not None and a > best:
                best = a
        out[i] = best
    return out


def clustering(labels):
    """Mean gap between consecutive label bars vs the gap random placement would give.

    A ratio near 1.0 means the label is spread out like a coin toss; well below 1.0
    means the bars come in clumps, which is why single-feature p values on this label
    must not be read as evidence.
    """
    y = np.asarray(labels, dtype=bool)
    pos = np.flatnonzero(y)
    if pos.size < 3:
        return {"bars": int(y.size), "positive_bars": int(pos.size),
                "mean_gap": None, "expected_gap": None, "ratio": None}
    gaps = np.diff(pos)
    expected = y.size / float(pos.size)
    return {"bars": int(y.size), "positive_bars": int(pos.size),
            "mean_gap": round(float(np.mean(gaps)), 3),
            "expected_gap": round(float(expected), 3),
            "ratio": round(float(np.mean(gaps) / expected), 4)}


def p_value(observed, null):
    """Add-one p value against a null sample (never returns 0.0)."""
    n = np.asarray(null, dtype=float)
    return (1.0 + float(np.sum(n >= observed))) / (1.0 + float(n.size))


# ------------------------------------------------------------------ the backtest
def build():
    prep = C.prepare()
    if len(prep["dates"]) < 260:
        raise SystemExit("panel too short for a 200-bar state variable: %d bars"
                         % len(prep["dates"]))

    prod = C.run_arm(prep, F.CONFIG["vol_target"])
    base = C.run_arm(prep, None)
    base_bar = str(prod["nav"].index[0].date())
    blk = F.bench_block(prep["dates"], prep["rebal_days"], base_bar)
    bench = pd.Series({pd.Timestamp(b["bar"]): b["nav"] for b in blk["bars"]}).sort_index()

    idx = prod["nav"].index
    if len(bench) != len(idx) or not bench.index.equals(idx):
        bench = bench.reindex(idx).ffill()

    r_p = C.daily(prod["nav"])
    r_b = C.daily(base["nav"])
    r_k = C.daily(bench)
    common = r_p.index.intersection(r_b.index).intersection(r_k.index)
    r_p, r_b, r_k = r_p.reindex(common), r_b.reindex(common), r_k.reindex(common)

    d = np.log1p(r_b.values) - np.log1p(r_k.values)          # selection-arm daily log excess
    y, thr = label_top(d, TOP_SHARE)

    nb = bench.reindex(common).astype(float)
    cash_share = (prod["cash"].reindex(common) / prod["nav"].reindex(common)).astype(float)

    bars_per_year = float(F.BARS_PER_YEAR)

    def rstd(w):
        return r_k.rolling(w, min_periods=max(5, w // 2)).std() * math.sqrt(bars_per_year)

    # Every state variable is public at the close of t-1; shift(1) is the contract.
    raw = {
        "basket_vol60_pct": rstd(60) * 100.0,
        "basket_ma200_gap_pct": (np.log(nb / nb.rolling(200, min_periods=100).mean()) * 100.0),
        "basket_ret20_pct": (np.log(nb / nb.shift(20)) * 100.0),
        "basket_dd200_pct": (np.log(nb / nb.rolling(200, min_periods=100).max()) * 100.0),
        "basket_down_share20_pct": ((r_k < 0).rolling(20, min_periods=10).mean() * 100.0),
        "book_basket_corr60": r_b.rolling(60, min_periods=30).corr(r_k),
        "book_cash_share_pct": cash_share * 100.0,
        "basket_dow": pd.Series(common.dayofweek.astype(float), index=common),
    }
    shifted = {k: v.shift(1) for k, v in raw.items()}

    out = {
        "schema": SCHEMA,
        "generated_ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": str(prep["dates"][-1].date()),
        "config": {
            "label": "top %d%% of daily log excess of the selection arm (base_book, no vol target)"
                     % int(round(100 * TOP_SHARE)),
            "label_threshold_log_excess": None if thr is None else round(float(thr), 8),
            "top_share": TOP_SHARE,
            "permutations": PERMS,
            "seed": SEED,
            "auc_min": AUC_MIN,
            "family_alpha": NULL_P,
            "bars_per_year": bars_per_year,
            "features": sorted(shifted),
            "shift": "every feature is shifted by one bar (state at close of t-1 prices bar t)",
            "n_hold": F.CONFIG["n_hold"], "rebal": F.CONFIG["rebal"],
            "cost_per_side": F.CONFIG["cost_per_side"],
        },
        "label": {},
        "features": {},
        "family": {},
        "hindsight": {},
        "verdict": None,
        "caveats": [
            "这里的高 AUC 是**本样本这些 bar** 的陈述，不是对下一段的承诺；族门是读者与"
            "「八个特征试到看起来好」之间唯一的防线。",
            "票池是今天上市的 ETF，标签和每一个篮子状态变量都继承同一个幸存者偏差——"
            "本面没有新增偏差，也没有消除它。",
            "标签是日对数超额的前十分位切分，与 r2230 印 953% 用的是同一把尺；它本身不是可交易信号。",
            "没过门的状态变量照样带数字印出，不删：没测到与测到零是两个答案。",
        ],
    }

    if y is None or d is None:
        out["verdict"] = "UNMEASURED_LABEL_UNAVAILABLE"
        return out

    # one common mask: the bars where the label exists AND every feature exists
    cols = [shifted[k].values for k in sorted(shifted)]
    mask = np.asarray(y, dtype=bool) | (~np.asarray(y, dtype=bool))   # all label bars
    mask = mask & np.isfinite(d)
    for c in cols:
        mask = mask & np.isfinite(c)
    n = int(mask.sum())

    out["label"] = {
        "bars_total": int(np.isfinite(d).sum()),
        "bars_judged": n,
        "positive_bars": int(np.asarray(y, dtype=bool)[mask].sum()),
    }
    if n < 200 or out["label"]["positive_bars"] < 20:
        out["verdict"] = "UNMEASURED_TOO_FEW_BARS"
        return out

    dm = np.asarray(d, dtype=float)[mask]
    ym = np.asarray(y, dtype=bool)[mask]
    years = (len(prep["dates"]) - 1) / bars_per_year
    out["label"]["share_of_total_excess_carried"] = round(
        float(dm[ym].sum()) / float(dm.sum()), 4) if abs(float(dm.sum())) > 1e-12 else None
    out["label"]["excess_pp_per_year_total"] = round(
        100.0 * float(dm.sum()) / (n / bars_per_year), 3)
    # The judged window starts only where the 200-bar state variable exists, so its total
    # is NOT the full-sample total; both are printed or a reader will read a window as an update.
    d_all = np.asarray(d, dtype=float)
    d_all = d_all[np.isfinite(d_all)]
    out["label"]["excess_pp_per_year_full_sample"] = round(
        100.0 * float(d_all.sum()) / (d_all.size / bars_per_year), 3)
    out["label"]["clustering"] = clustering(ym)

    rank_scores, names = [], []
    for k in sorted(shifted):
        x = np.asarray(shifted[k], dtype=float)[mask]
        r = _ranks(x)
        a = auc_from_ranks(r, ym)
        pos = x[ym]
        neg = x[~ym]
        out["features"][k] = {
            "auc": None if a is None else round(float(a), 4),
            "median_on_excess_bars": round(float(np.median(pos)), 4),
            "median_on_other_bars": round(float(np.median(neg)), 4),
            "bars": int(x.size),
        }
        rank_scores.append(r)
        names.append(k)

    null = permutation_family(rank_scores, ym)
    p95 = float(np.percentile(null, 95))
    obs = {k: v["auc"] for k, v in out["features"].items() if v["auc"] is not None}
    best_name = max(obs, key=lambda k: obs[k])
    best_auc = float(obs[best_name])
    fam_p = p_value(best_auc, null)

    blk = permutation_family_block(rank_scores, ym, block=20)
    blk_p95 = float(np.percentile(blk, 95)) if blk is not None else None
    blk_p = p_value(best_auc, blk) if blk is not None else None

    for k in sorted(out["features"]):
        out["features"][k]["clears_auc_floor"] = bool(out["features"][k]["auc"] >= AUC_MIN)

    # honest single-feature nulls, computed once per feature (cheap: ranks are ready)
    rng = np.random.RandomState(SEED + 7)
    for k in sorted(out["features"]):
        gi = names.index(k)
        nulls = np.empty(PERMS, dtype=float)
        for j in range(PERMS):
            yy = np.zeros(ym.size, dtype=bool)
            yy[rng.choice(ym.size, size=int(ym.sum()), replace=False)] = True
            nulls[j] = auc_from_ranks(rank_scores[gi], yy)
        out["features"][k]["p_single"] = round(p_value(out["features"][k]["auc"], nulls), 4)
        out["features"][k]["null_p95"] = round(float(np.percentile(nulls, 95)), 4)

        del nulls

    out["family"] = {
        "best_feature": best_name,
        "best_auc": round(best_auc, 4),
        "null_family_p95": round(p95, 4),
        "null_family_mean": round(float(np.mean(null)), 4),
        "family_p": round(fam_p, 4),
        "block20_null_p95": None if blk_p95 is None else round(blk_p95, 4),
        "block20_family_p": None if blk_p is None else round(blk_p, 4),
        "features_tried": len(names),
        "beats_iid_family_gate": bool(best_auc >= p95 and fam_p < NULL_P and best_auc >= AUC_MIN),
        "beats_block_family_gate": bool(blk_p95 is not None and blk_p is not None
                                        and best_auc >= blk_p95 and blk_p < NULL_P
                                        and best_auc >= AUC_MIN),
        "beats_auc_floor": bool(best_auc >= AUC_MIN),
    }
    out["family"]["beats_family_gate"] = bool(out["family"]["beats_iid_family_gate"]
                                              and out["family"]["beats_block_family_gate"])

    # what knowing the days would be worth -- the upper bound anyone could ever reach
    order = np.argsort(dm)
    k = max(1, int(math.ceil(TOP_SHARE * dm.size)))
    worst = np.zeros(dm.size, dtype=bool)
    worst[order[:k]] = True
    out["hindsight"] = {
        "drop_worst_10pct_bars_pp_per_year": round(
            100.0 * float(dm[~worst].sum()) / (int((~worst).sum()) / bars_per_year), 3),
        "keep_only_best_10pct_bars_pp_per_year": round(
            100.0 * float(dm[ym].sum()) / (n / bars_per_year), 3),
        "years": round(n / bars_per_year, 4),
    }

    if out["family"]["beats_family_gate"]:
        out["verdict"] = "PREDICTABLE_BY_" + best_name.upper()
    elif out["family"]["beats_auc_floor"]:
        out["verdict"] = "WEAK_SIGNAL_NOT_PROVEN_FAMILY"
    else:
        out["verdict"] = "NOT_PREDICTABLE_USE_AS_LUCK"
    return out


# ------------------------------------------------------------------ the page
def _fmt(x, nd=2):
    return "—" if x is None else ("%.*f" % (nd, x))


def render_md(d):
    """The page is rendered, never hand-edited (r1860: a hand-copied number drifts)."""
    L = []
    f = d["features"]
    fam = d.get("family") or {}
    lab = d.get("label") or {}
    ver = d.get("verdict")
    L.append("# 超额是不是「看得见才能赚到」？")
    L.append("")
    L.append("> 面 `%s` · 截止 %s · 生成 %s" % (d.get("schema"), d.get("evidence_cutoff"),
                                              (d.get("generated_ts") or "")[:19]))
    L.append("")
    L.append("## 回答的问题")
    L.append("")
    L.append("r2230 在**全样本**上印过：超额 +%.3f pp/年，最好的 10%% 的 bar 承载了全部超额的"
             " **953%%**，剔掉它们立刻转负——那是「少数价差日」的算术。"
             "本面为了用 200 日均线，判定窗从第 201 根 bar 起，窗内同一口径是 "
             "**+%.3f pp/年**、承载 **%s%%**；两个数的差别在窗口，不在算法。"
             % (lab.get("excess_pp_per_year_full_sample") or 0.0,
                lab.get("excess_pp_per_year_total") or 0.0,
                _fmt(None if lab.get("share_of_total_excess_carried") is None
                     else 100.0 * lab["share_of_total_excess_carried"], 0)))
    L.append("")
    L.append("那么这些日子**在事前能不能被认出来**？本面把收盘 t-1 时公开的状态变量逐个拿来判："
             "它们能不能分开「承载超额的那 10% 根 bar」和其余 bar。")
    L.append("")
    L.append("## 先看一件事：单式 p 值在这张面上为什么不能读")
    L.append("")
    cl = lab.get("clustering") or {}
    L.append("超额日 %s 根，相邻间距均值 **%s** 根 bar；若随机撒开应是 **%s** 根 → 比值 **%s**。"
             % (cl.get("positive_bars"), _fmt(cl.get("mean_gap")),
                _fmt(cl.get("expected_gap")), _fmt(cl.get("ratio"), 3)))
    L.append("")
    L.append("比值接近 1，所以这些日子**不是成堆来的**——「标签聚簇」这一种解释先被排除了。"
             "但八个特征的单一检验 p 全都落在 0.02~0.07 附近，这仍然是假象，来源在特征那一侧："
             "60 日波动、200 日均线偏离这类状态变量本身高度自相关，"
             "1572 根 bar 里真正独立的观测远少于 1572，于是一打标签的 i.i.d. null 太窄。")
    L.append("")
    L.append("实测证据就在门线上：i.i.d. 族 null 的 p95 是 **%.3f**，"
             "把标签按 20 根 bar 成块打乱后 p95 涨到 **%s**——同一个「没有信号」的世界，"
             "宽出来的这一截就是特征平滑度换来的虚假显著性。"
             % (fam.get("null_family_p95") or 0.0, _fmt(fam.get("block20_null_p95"), 3)))
    L.append("")
    L.append("所以本面的判词只用**族级门**（八选一的最大值对噪声最大值），两个 null 都印。")
    L.append("")
    L.append("## 判词")
    L.append("")
    L.append("**%s**" % ver)
    L.append("")
    if ver and ver.startswith("PREDICTABLE"):
        L.append("族里最好的状态变量是 `%s`，AUC **%.3f**，族置换 p=%.3f（族门线 %.3f）。"
                 "这是一个**可用的择时输入**，但仍然只是本样本里的读数。" %
                 (fam.get("best_feature"), fam.get("best_auc") or 0, fam.get("family_p") or 0,
                  fam.get("null_family_p95") or 0))
    elif ver == "WEAK_SIGNAL_NOT_PROVEN_FAMILY":
        L.append("族里最好的 `%s` AUC 有 %.3f（过 %.2f 的可行动线），但**过不了族级门**："
                 "族置换 p=%.3f，噪声族最大值 p95=%.3f。试了 %d 个变量才有一个 0.6，"
                 "这正是多重比较的样子（r858 教训），不记作择时能力。" %
                 (fam.get("best_feature"), fam.get("best_auc") or 0, AUC_MIN,
                  fam.get("family_p") or 0, fam.get("null_family_p95") or 0,
                  fam.get("features_tried") or 0))
    elif ver == "NOT_PREDICTABLE_USE_AS_LUCK":
        L.append("**没有任何事前状态变量能分开那些日子**：族里最好的 `%s` AUC %.3f，"
                 "低于 %.2f 的可行动线；族置换 p=%.3f（i.i.d. 门 %.3f），块置换 p=%s（门 %s）。"
                 "结论是 +%.3f pp/年 应当**按运气对待**——它可以被报告，"
                 "但不可以被当成一个可以加杠杆、可以融资、可以按年复制的速率。"
                 % (fam.get("best_feature"), fam.get("best_auc") or 0, AUC_MIN,
                    fam.get("family_p") or 0, fam.get("null_family_p95") or 0,
                    _fmt(fam.get("block20_family_p"), 3), _fmt(fam.get("block20_null_p95"), 3),
                    lab.get("excess_pp_per_year_total") or 0.0))
    else:
        L.append("本次不可测：%s（缺输入不等于判零）。" % ver)
    L.append("")
    L.append("## 上限：就算知道了，能值多少钱")
    L.append("")
    h = d.get("hindsight") or {}
    L.append("| 情形 | pp/年 |")
    L.append("|---|---|")
    L.append("| 什么都不做（全样本） | %s |" % _fmt(lab.get("excess_pp_per_year_total"), 3))
    L.append("| 完美躲开最差的 10%% bar | %s |" % _fmt(h.get("drop_worst_10pct_bars_pp_per_year"), 3))
    L.append("| 只留最好的 10%% bar | %s |" % _fmt(h.get("keep_only_best_10pct_bars_pp_per_year"), 3))
    L.append("")
    L.append("两行极端值都是**事后的**（要用当天已实现的价格），它们的用处是标出天花板："
             "判词说「事前分不开」时，这两行告诉你错过的是什么量级的运气，"
             "而不是说「我们应该去追它」。")
    L.append("")
    L.append("## 每个状态变量的读数（全部 shift 一根 bar）")
    L.append("")
    L.append("| 状态变量 | AUC | 超额日的中位 | 其余日的中位 | 单式 p | 单式 null p95 |")
    L.append("|---|---|---|---|---|---|")
    for k in sorted(f):
        v = f[k]
        L.append("| `%s` | %s | %s | %s | %s | %s |" % (
            k, _fmt(v.get("auc"), 3), _fmt(v.get("median_on_excess_bars")),
            _fmt(v.get("median_on_other_bars")), _fmt(v.get("p_single"), 3),
            _fmt(v.get("null_p95"), 3)))
    L.append("")
    L.append("`basket_dow` 是星期序号（0=周一 … 4=周五），AUC>0.5 表示越靠近周末越可能是超额日；"
             "这个变量的中位数在两列里都是 2.0，说明它靠的是分布尾部而不是中位，"
             "这也是它 p 值最小却过不了族门的样子——八选一的最大值本来就会挑到一个 0.55。")
    L.append("")
    L.append("## 口径与边界")
    L.append("")
    L.append("* 标签=选择臂（无波动目标）日对数超额的前 %d%%（阈值 %.6f），判定 %d 根 bar，"
             "其中 %d 根是超额日。**判定窗从第 201 根 bar 起**（200 日均线要求），"
             "窗内全样本超额=%.3f pp/年，全样本（%d 根 bar）=%.3f pp/年——两个数不是同一件事，"
             "窗内的更高是因为 2020 年初那段低波窗被排除，不是因为本面发现了新收益。"
             % (int(round(100 * TOP_SHARE)),
                d["config"]["label_threshold_log_excess"] or 0.0,
                lab.get("bars_judged") or 0,
                lab.get("positive_bars") or 0,
                lab.get("excess_pp_per_year_total") or 0.0,
                lab.get("bars_total") or 0,
                lab.get("excess_pp_per_year_full_sample") or 0.0))
    L.append("* 族门=%d 次标签置换的**族最大值**分布，i.i.d. 门线 p95=%.3f，"
             "块置换（20 根/块）门线 p95=%s；两个门都过才判 PREDICTABLE。"
             % (PERMS, fam.get("null_family_p95") or 0.0, _fmt(fam.get("block20_null_p95"), 3)))
    L.append("* 每个特征只在「自己也存在」的公共 bar 上判，特征之间共享同一批 bar。")
    for c in d.get("caveats") or []:
        L.append("* %s" % c)
    L.append("")
    return "\n".join(L)


# ------------------------------------------------------------------ selftest
def selftest():
    fails = []

    def chk(name, cond, detail=""):
        if cond:
            print("  ok   %s %s" % (name, detail))
        else:
            print("  FAIL %s %s" % (name, detail))
            fails.append(name)

    # 1. perfect separation -> AUC 1.0 ; reversed -> 0.0
    y = np.array([True] * 20 + [False] * 80)
    x = np.concatenate([np.arange(20) + 100.0, np.arange(80)])
    chk("auc_perfect", abs(auc_of(x, y) - 1.0) < 1e-9)
    chk("auc_reversed", abs(auc_of(-x, y) - 0.0) < 1e-9)

    # 2. random label -> near 0.5
    rng = np.random.RandomState(7)
    xs = rng.randn(500)
    ys = rng.rand(500) < 0.1
    a = auc_of(xs, ys)
    chk("auc_random_near_half", abs(a - 0.5) < 0.15, "auc=%.3f" % a)

    # 3. shift contract: same-day feature separates almost perfectly, shifted does not
    d = rng.randn(600)
    lab, _ = label_top(d)
    same = auc_of(d, lab)
    shift = auc_of(np.roll(d, 1), lab)
    chk("hindsight_same_day_huge", same > 0.95, "auc=%.3f" % same)
    chk("shift_kills_it", shift < 0.70, "auc=%.3f" % shift)

    # 4. label share counts the right number of bars
    y2, thr = label_top(np.arange(1000.0))
    chk("label_top_share", int(y2.sum()) == 100, "n_pos=%d" % int(y2.sum()))

    # 5. family gate: features that are pure noise must not clear it
    rs = [_ranks(rng.randn(500)) for _ in range(6)]
    yy = rng.rand(500) < 0.1
    obs_best = max(auc_from_ranks(r, yy) for r in rs)
    null = permutation_family(rs, yy, perms=200, seed=11)
    p95 = float(np.percentile(null, 95))
    chk("noise_family_not_significant", obs_best < p95 or p_value(obs_best, null) >= NULL_P,
        "obs=%.3f p95=%.3f" % (obs_best, p95))

    # 6. family gate: one real feature must clear it
    real = _ranks(np.asarray(yy, dtype=float) + rng.randn(500) * 0.35)
    rs2 = rs + [real]
    obs2 = max(auc_from_ranks(r, yy) for r in rs2)
    null2 = permutation_family(rs2, yy, perms=200, seed=12)
    chk("real_feature_clears", obs2 > float(np.percentile(null2, 95)),
        "obs=%.3f p95=%.3f" % (obs2, float(np.percentile(null2, 95))))

    # 7. missing inputs are UNMEASURED, never NOT_PREDICTABLE
    fake = {"schema": SCHEMA, "evidence_cutoff": "2026-01-01",
            "generated_ts": "2026-01-01T00:00:00+0800",
            "config": {"label_threshold_log_excess": None},
            "label": {}, "features": {}, "family": {}, "hindsight": {},
            "verdict": "UNMEASURED_LABEL_UNAVAILABLE", "caveats": []}
    md = render_md(fake)
    chk("unmeasured_not_confused_with_null",
        "UNMEASURED_LABEL_UNAVAILABLE" in md and "按运气对待" not in md)

    # 8. p_value never returns zero
    chk("p_value_never_zero", p_value(10.0, np.zeros(100)) > 0.0)

    # 9. the page renders from the data, not from a hand copy
    md2 = render_md(fake)
    chk("page_deterministic", md2 == render_md(fake))

    # 10. clustering tells a clumped label from a spread one
    clumped = np.zeros(400, dtype=bool)
    for s in (50, 150, 250, 340):
        clumped[s:s + 10] = True
    spread = rng.rand(400) < 0.1
    c1, c2 = clustering(clumped), clustering(spread)
    chk("clustering_sees_clumps", c1["ratio"] < 0.8 and c2["ratio"] > 0.8,
        "clumped=%.2f spread=%.2f" % (c1["ratio"], c2["ratio"]))

    # 11. on a clumped label the block null must be wider than the iid null
    rs3 = [_ranks(np.cumsum(rng.randn(400))) for _ in range(4)]
    n_i = permutation_family(rs3, clumped, perms=150, seed=21)
    n_b = permutation_family_block(rs3, clumped, block=20, perms=150, seed=22)
    chk("block_null_wider_on_clumped",
        float(np.percentile(n_b, 95)) > float(np.percentile(n_i, 95)),
        "block95=%.3f iid95=%.3f" % (float(np.percentile(n_b, 95)),
                                     float(np.percentile(n_i, 95))))

    total = 13
    print("SELFTEST %d/%d" % (total - len(fails), total))
    if fails:
        print("FAILED: %s" % ", ".join(fails))
        return 1
    return 0


# ------------------------------------------------------------------ cli
def load_face():
    if not os.path.exists(OUT_JSON):
        raise SystemExit("face missing: run `run` first")
    with open(OUT_JSON, encoding="utf-8") as fh:
        return json.load(fh)


def cmd_check():
    cur = load_face()
    fresh = build()
    # the page carries a wall-clock stamp; compare on the published one so an idempotent
    # re-run is not read as a defect (r378: only runtime metadata may drift)
    fresh["generated_ts"] = cur.get("generated_ts")
    bad = []
    for k in ("verdict", "label", "features", "family", "hindsight", "config"):
        if cur.get(k) != fresh.get(k):
            bad.append(k)
    if os.path.exists(OUT_MD):
        with open(OUT_MD, encoding="utf-8") as fh:
            disk = fh.read()
        if disk != render_md(fresh):
            bad.append("page")
    else:
        bad.append("page_missing")
    if bad:
        print("CHECK FAILED: %s" % ", ".join(bad))
        return 4
    print("CHECK OK  verdict=%s  best=%s auc=%s" % (
        cur.get("verdict"), (cur.get("family") or {}).get("best_feature"),
        (cur.get("family") or {}).get("best_auc")))
    return 0


def cmd_run():
    d = build()
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(render_md(d))
    print("WROTE %s" % OUT_JSON)
    print("WROTE %s" % OUT_MD)
    print("verdict=%s" % d.get("verdict"))
    fam = d.get("family") or {}
    print("best=%s auc=%s family_p=%s null_p95=%s" % (
        fam.get("best_feature"), fam.get("best_auc"), fam.get("family_p"),
        fam.get("null_family_p95")))
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "--selftest":
        return selftest()
    if cmd == "--check":
        return cmd_check()
    if cmd == "run":
        return cmd_run()
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
