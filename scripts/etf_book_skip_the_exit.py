"""Question this answers: the book's defence is an ACTION (a rebalance that moves into
bonds/cash). r2055 priced "defence instead of holding the equity sleeve". Nobody has
priced the third arm, which is what a human actually does when a stop fires:

    the signal fires, and the book simply does not trade -- it keeps the five names it
    already owns, pays no turnover, and lives with whatever those names do next.

That is not the same as the equity sleeve: the incumbent names are the previous top-5,
not the equal-weight universe. And it is not the same as the book: the book pays the
turnover and owns bonds.

Method: no fill maths of its own. `run_two` is the same leg chain as
`etf_equity_alpha.run_with_attribution` with one extra branch (skip the rebalance when
the new mix has equity weight <= 0 and the book already owns something). The self-test
pins the branch: with skip=False the curve must be bit-identical to the engine's.

Money is reported on the 1,000,000 ticket the rest of the book quotes.

Contract: `write` derives the face; `check` re-derives the cheap inputs and says STALE
when the panel bytes moved, CHECK FAILED when the same inputs give different numbers.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_equity_alpha as A
import etf_robust_pf as R
from config import PATHS

FACE = os.path.join(ROOT, "results", "etf_book_skip_the_exit.json")
DOC = os.path.join(ROOT, "research", "ETF_BOOK_SKIP_THE_EXIT.md")
PANEL_DIR = os.path.join(PATHS.daily_dir)
TICKET_CNY = 1000000.0
WHIPSAW_WINDOW = 20
SCHEMA = "etf-book-skip-the-exit/v1"


# ---------------------------------------------------------------- the one-branch chain
def run_two(close, openp, amt, score, cls, skip_defense_exit=False,
            rebal=None, n_hold=None, cost=None, start=None, _skip_log=None):
    """`etf_equity_alpha.run_with_attribution` plus one branch.

    skip_defense_exit=True: on a rebalance whose new pick set is fully defensive
    (equity weight <= 0) and the book already holds something, do nothing -- no
    turnover, no new mix, same five names as before.
    """
    rebal = A.REBAL if rebal is None else rebal
    n_hold = A.N_HOLD if n_hold is None else n_hold
    cost = A.COST if cost is None else cost
    start = A.START if start is None else start

    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    score = score.where(elig)
    op = openp.reindex(columns=close.columns)
    dates = [d for d in op.index if d >= pd.Timestamp(start)]

    equity, held, pending = 1.0, {}, None
    curve, contrib, turns, mixes = [], [], [], []
    skipped = []
    for i in range(len(dates) - 1):
        d, nxt = dates[i], dates[i + 1]
        cost_paid = 0.0
        if i % rebal == 0:
            s = score.loc[d].dropna()
            if len(s) >= n_hold:
                picks = list(s.nlargest(n_hold).index)
                w = {p: 1.0 / n_hold for p in picks}
                mix = {c: sum(wt for p, wt in w.items() if cls[p] == c)
                       for c in A.CLASSES}
                if skip_defense_exit and held and mix.get("equity", 0.0) <= 0.0:
                    prev = {c: sum(wt for p, wt in held.items() if cls[p] == c)
                            for c in A.CLASSES}
                    turn_saved = sum(abs(w.get(k, 0.0) - held.get(k, 0.0))
                                     for k in set(w) | set(held))
                    skipped.append({"date": str(d.date()),
                                    "prev_mix": prev, "refused_mix": mix,
                                    "turn_saved": round(float(turn_saved), 4),
                                    "cost_saved": round(float(cost * turn_saved), 8),
                                    "prev_names": sorted(held)})
                else:
                    turn = sum(abs(w.get(k, 0.0) - held.get(k, 0.0))
                               for k in set(w) | set(held))
                    cost_paid = cost * turn
                    equity *= (1.0 - cost_paid)
                    turns.append(turn)
                    held = w
                    mixes.append(mix)
        r_cls = {c: 0.0 for c in A.CLASSES}
        r_tot = 0.0
        for p, wt in held.items():
            a, b = op.at[d, p], op.at[nxt, p]
            if np.isfinite(a) and np.isfinite(b) and a > 0:
                rp = wt * (b / a - 1.0)
                r_tot += rp
                r_cls[cls[p]] += rp
        equity *= (1.0 + r_tot)
        curve.append((nxt, equity))
        contrib.append((nxt, r_tot, r_cls, cost_paid))

    ser = pd.Series(dict(curve)).sort_index()
    if _skip_log is not None:
        _skip_log.extend(skipped)
    return ser, contrib, (float(np.mean(turns)) if turns else 0.0), mixes, skipped


def logret_of(ser):
    return np.concatenate([[0.0], np.diff(np.log(ser.values))])


def maxdd_log(x):
    c = np.cumsum(np.asarray(x, dtype=float))
    if len(c) == 0:
        return 0.0
    peak = np.maximum.accumulate(np.concatenate([[0.0], c]))[1:]
    return float(np.max(peak - c))


# ---------------------------------------------------------------- inputs
def panel_dir_stat():
    names = [n for n in os.listdir(PANEL_DIR) if n.endswith(".csv")]
    mt = max(os.path.getmtime(os.path.join(PANEL_DIR, n)) for n in names) if names else 0.0
    return {"files": len(names), "max_mtime": mt}


def _inputs():
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    score = E.build_score(close, amt, feats)
    return close, openp, amt, feats, score, cls, n_flip


# ---------------------------------------------------------------- pricing
def spell_windows(skipped, dates):
    """Bars each skipped decision governs: from the bar after the decision until the next
    rebalance that actually traded (or the end of the curve)."""
    idx = {str(pd.Timestamp(d).date()): i for i, d in enumerate(dates)}
    out = []
    for k, s in enumerate(skipped):
        i = idx.get(s["date"])
        if i is None:
            continue
        stop = (idx.get(skipped[k + 1]["date"], len(dates)) if k + 1 < len(skipped)
                else len(dates))
        out.append((i, min(stop, len(dates))))
    return out


def derive(detail=False):
    close, openp, amt, feats, score, cls, n_flip = _inputs()

    ser_engine, contrib_e, turn_e, mixes_e = A.run_with_attribution(
        close, openp, amt, score, cls)
    ser_book, _, turn_b, _, _ = run_two(close, openp, amt, score, cls,
                                        skip_defense_exit=False)
    skip_log = []
    ser_skip, _, turn_s, _, _ = run_two(close, openp, amt, score, cls,
                                        skip_defense_exit=True, _skip_log=skip_log)

    # the branch must be dead when we say it is: engine == book, bar for bar
    same = (len(ser_engine) == len(ser_book) and
            bool(np.allclose(ser_engine.values, ser_book.values, rtol=0, atol=1e-12)))
    max_gap = float(np.max(np.abs(ser_engine.values - ser_book.values))) if len(
        ser_engine) == len(ser_book) else float("nan")

    m_book = R.stats(ser_book, "book_defence_on")
    m_skip = R.stats(ser_skip, "book_defence_skipped")
    oos_cut = pd.Timestamp("2023-12-31")
    o_book = R.stats(ser_book[ser_book.index > oos_cut], "book_oos")
    o_skip = R.stats(ser_skip[ser_skip.index > oos_cut], "skip_oos")

    lr_book, lr_skip = logret_of(ser_book), logret_of(ser_skip)
    dates = pd.DatetimeIndex(ser_book.index)

    # per-skip attribution: what the incumbent names did while the book was in bonds
    windows = spell_windows(skip_log, dates)
    per_skip = []
    for (a, b) in windows:
        if b <= a:
            continue
        d_book = float(np.nansum(lr_book[a:b]))
        d_skip = float(np.nansum(lr_skip[a:b]))
        per_skip.append({"start": str(dates[a].date()),
                         "bars": int(b - a),
                         "book_log": d_book,
                         "skip_log": d_skip,
                         "delta_log": d_skip - d_book})
    helped = [p for p in per_skip if p["delta_log"] > 0]

    total_delta = float(np.nansum(lr_skip) - np.nansum(lr_book))
    cost_saved = float(sum(s["cost_saved"] for s in skip_log))
    covered = float(sum(p["delta_log"] for p in per_skip))

    face = {
        "schema": SCHEMA,
        "evidence_cutoff": str(pd.Timestamp(close.index.max()).date()),
        "cell": "N%d_R%d_%dbp" % (A.N_HOLD, A.REBAL, A.COST * 1e4),
        "execution": "decision at close t, execute at open t+1 (entry_lag=0, the printed caliber)",
        "arms": {
            "book": "defence fires -> rebalance into bonds/cash (the published rule)",
            "skip": "defence fires and the book already owns something -> do not trade, keep the incumbent five",
            "not_the_same_as": ("r2055's counterfactual holds the eligible equity equal-weight "
                                "universe; this arm holds the previous top-5 names"),
        },
        "branch_is_dead_when_off": {"max_abs_gap_vs_engine": max_gap, "bit_identical": same},
        "panel": {"shape": list(close.shape), "flips_repaired": int(n_flip),
                  "first_bar": str(close.index.min().date()),
                  "last_bar": str(close.index.max().date()),
                  "class_counts": {k: int(v) for k, v in cls.value_counts().items()},
                  "dir_stat": panel_dir_stat()},
        "book": {"cagr": m_book.get("cagr"), "sharpe": m_book.get("sharpe"),
                 "maxdd": m_book.get("maxdd"), "cagr_oos": o_book.get("cagr"),
                 "sharpe_oos": o_book.get("sharpe"), "maxdd_oos": o_book.get("maxdd"),
                 "avg_turnover": round(float(turn_b), 4)},
        "skip": {"cagr": m_skip.get("cagr"), "sharpe": m_skip.get("sharpe"),
                 "maxdd": m_skip.get("maxdd"), "cagr_oos": o_skip.get("cagr"),
                 "sharpe_oos": o_skip.get("sharpe"), "maxdd_oos": o_skip.get("maxdd"),
                 "avg_turnover": round(float(turn_s), 4)},
        "delta": {
            "cagr_pp": round((m_skip.get("cagr", 0) - m_book.get("cagr", 0)) * 100, 3),
            "sharpe": round((m_skip.get("sharpe", 0) - m_book.get("sharpe", 0)), 3),
            "maxdd_pp": round((m_skip.get("maxdd", 0) - m_book.get("maxdd", 0)) * 100, 3),
            "total_log": round(total_delta, 6),
            "total_cny": round(total_delta * TICKET_CNY, 0),
            "turnover_pp": round((turn_s - turn_b) * 100, 2),
        },
        "skips": {
            "n": len(skip_log),
            "cost_saved_cum": round(cost_saved, 6),
            "cost_saved_cny": round(cost_saved * TICKET_CNY, 0),
            "rows": skip_log,
        },
        "attribution": {
            "windows": per_skip,
            "n_scored": len(per_skip),
            "n_helped": len(helped),
            "helped_cny": round(float(sum(p["delta_log"] for p in helped)) * TICKET_CNY, 0),
            "hurt_cny": round(float(sum(p["delta_log"] for p in per_skip
                                        if p["delta_log"] <= 0)) * TICKET_CNY, 0),
            "median_bars": (float(np.median([p["bars"] for p in per_skip]))
                            if per_skip else None),
            "coverage_log": round(covered, 6),
            "uncovered_log": round(total_delta - covered, 6),
        },
        "maxdd_walk": {"book": maxdd_log(lr_book), "skip": maxdd_log(lr_skip)},
        "verdict": ("SKIPPING_THE_EXIT_COSTS_MONEY" if total_delta < 0
                    else "SKIPPING_THE_EXIT_MAKES_MONEY"),
        "verdict_rule": "sign of the total log difference (skip minus book) over the whole sample",
        "caveats": [
            "The ETF pool is today's listed set (survivorship); early years read a thinner panel than was live.",
            "The skip arm holds whatever the book last bought, so its risk depends on the incumbent names -- that is the point of the arm, not a defect.",
            "This is the all-classes cell. The production candidate (nobond_vt08) has no bond slot and never prints a defensive rebalance, so this face prices a decision the production book does not make.",
            "Cost saved is measured in the same 10bp/edge convention the book uses; slippage on the names it refuses to sell is not modelled.",
        ],
    }
    return face, (ser_book, ser_skip)


# ---------------------------------------------------------------- write / check
def write():
    print("loading panel ...", flush=True)
    face, _ = derive()
    os.makedirs(os.path.dirname(FACE), exist_ok=True)
    with open(FACE, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    write_doc(face)
    d = face["delta"]
    print("WROTE", os.path.relpath(FACE, ROOT))
    print("branch dead when off: bit_identical=%s max_gap=%.3e"
          % (face["branch_is_dead_when_off"]["bit_identical"],
             face["branch_is_dead_when_off"]["max_abs_gap_vs_engine"]))
    print("book %.2f%%/%.3f/%.2f%%  skip %.2f%%/%.3f/%.2f%%  delta cagr %+.2fpp sharpe %+.3f mdd %+.2fpp log %+.4f (%+.0f CNY)"
          % (face["book"]["cagr"] * 100, face["book"]["sharpe"], face["book"]["maxdd"] * 100,
             face["skip"]["cagr"] * 100, face["skip"]["sharpe"], face["skip"]["maxdd"] * 100,
             d["cagr_pp"], d["sharpe"], d["maxdd_pp"], d["total_log"], d["total_cny"]))
    print("skips=%d cost saved %+.0f CNY; helped %d/%d windows, helped %+.0f / hurt %+.0f CNY"
          % (face["skips"]["n"], face["skips"]["cost_saved_cny"],
             face["attribution"]["n_helped"], face["attribution"]["n_scored"],
             face["attribution"]["helped_cny"], face["attribution"]["hurt_cny"]))
    print("verdict", face["verdict"])
    return 0


def write_doc(face):
    b, s, d, at, sk = (face["book"], face["skip"], face["delta"],
                       face["attribution"], face["skips"])
    L = []
    L.append("# ETF 书：防御这一单，不做会怎样\n")
    L.append("<!-- ETF-BOOK-SKIP-THE-EXIT:BEGIN -->\n")
    L.append("格 %s · evidence_cutoff %s · 面板 %d 只 × %d 根 bar（%s → %s）\n"
             % (face["cell"], face["evidence_cutoff"], face["panel"]["shape"][1],
                face["panel"]["shape"][0], face["panel"]["first_bar"],
                face["panel"]["last_bar"]))
    L.append("## 问题\n")
    L.append("这本书的防御是一个**动作**：信号一到，换仓进债/货币。r2055 已经量过「防御 vs 拿着"
             "合格权益等权袖」。还有第三条臂没量——**信号到了但什么都不做**：继续拿手里那五只，"
             "不付换手，承担它们接下来的涨跌。\n")
    L.append("这不是等权袖：手里那五只是上一期的 top5，不是全宇宙等权。\n")
    L.append("## 结果\n")
    L.append("| | 年化 | 夏普 | 最大回撤 | 2024+ 年化 | 2024+ 夏普 | 平均换手 |")
    L.append("|---|---|---|---|---|---|---|")
    L.append("| 本书（防御照做） | %.2f%% | %.3f | %.2f%% | %.2f%% | %.3f | %.3f |"
             % (b["cagr"] * 100, b["sharpe"], b["maxdd"] * 100,
                (b["cagr_oos"] or 0) * 100, (b["sharpe_oos"] or 0), b["avg_turnover"]))
    L.append("| 不换（继续持上一期五只） | %.2f%% | %.3f | %.2f%% | %.2f%% | %.3f | %.3f |"
             % (s["cagr"] * 100, s["sharpe"], s["maxdd"] * 100,
                (s["cagr_oos"] or 0) * 100, (s["sharpe_oos"] or 0), s["avg_turnover"]))
    L.append("")
    L.append("差值：年化 **%+.2fpp**、夏普 **%+.3f**、回撤 **%+.2fpp**、全样本 **%+.4f log**"
             "（**%+.0f 元** / 100 万票面）。\n"
             % (d["cagr_pp"], d["sharpe"], d["maxdd_pp"], d["total_log"], d["total_cny"]))
    L.append("判词 **%s**：%s。\n" % (face["verdict"], face["verdict_rule"]))
    L.append("## 被拒掉的单子\n")
    L.append("样本里防御信号触发了 **%d 次**，每次都被这条纪律拒掉；省下的换手成本累计"
             " **%+.0f 元**（%+.4f log）。\n"
             % (sk["n"], sk["cost_saved_cny"], sk["cost_saved_cum"]))
    L.append("逐次归因（跳过后的持有窗，%d 段可计价）：**%d 段帮上忙**（%+.0f 元）、"
             "其余 **%+.0f 元**；中位持有 **%s 根 bar**。\n"
             % (at["n_scored"], at["n_helped"], at["helped_cny"], at["hurt_cny"],
                ("%.0f" % at["median_bars"]) if at["median_bars"] is not None else "n/a"))
    if at["windows"]:
        L.append("最伤的一次：%s（%d 根，%+.4f log）。最好的一次：%s（%d 根，%+.4f log）。\n"
                 % (min(at["windows"], key=lambda w: w["delta_log"])["start"],
                    min(at["windows"], key=lambda w: w["delta_log"])["bars"],
                    min(at["windows"], key=lambda w: w["delta_log"])["delta_log"],
                    max(at["windows"], key=lambda w: w["delta_log"])["start"],
                    max(at["windows"], key=lambda w: w["delta_log"])["bars"],
                    max(at["windows"], key=lambda w: w["delta_log"])["delta_log"]))
    L.append("口径：%d 个窗口 = 防御区里的 rebalance 日（每 %d 根一个），不是 r2055 的 17 段 spell——"
             "一段防御里可以有好几次换仓。窗口覆盖 %+.4f log，未覆盖 %+.4f（应为 0）。\n"
             % (at["n_scored"], int(face["cell"].split("_R")[1].split("_")[0]),
                at["coverage_log"], at["uncovered_log"]))
    L.append("## 省得回来的成本，省不回来的下跌\n")
    L.append("这条纪律在 **%d/%d** 个窗口里帮了忙——接近抛硬币，所以不能说它「总是错」。"
             "它省下的 %+.0f 元换手成本（票面的 %.2f%%）几乎正好被拒换仓后那段下跌吃回去，"
             "净差 **%+.0f 元**（票面 %+.2f%%）。\n"
             % (at["n_helped"], at["n_scored"], sk["cost_saved_cny"],
                abs(sk["cost_saved_cny"]) / TICKET_CNY * 100, d["total_cny"],
                d["total_cny"] / TICKET_CNY * 100))
    L.append("所以「防御值不值」的答案不在收益表上，而在回撤上：最大回撤从 **%.2f%%** "
             "恶化到 **%.2f%%**（%+.2fpp）。防御买的不是收益，是过程——与 r2055「同一批防御 bar 里"
             "权益袖的峰谷 -29.8%% 对本书 -5.8%%」是同一句话的收益侧读法。\n"
             % (b["maxdd"] * 100, s["maxdd"] * 100, d["maxdd_pp"]))
    L.append("## 自证\n")
    L.append("- 关掉这条分支时，曲线与引擎 `run_with_attribution` **逐 bar 恒等**"
             "（max|gap|=%.2e，bit_identical=%s）；\n"
             % (face["branch_is_dead_when_off"]["max_abs_gap_vs_engine"],
                face["branch_is_dead_when_off"]["bit_identical"]))
    L.append("- 面板同款：未修翻转前先 `repair_flips`（本面修了 %d 处报价面翻转）；\n"
             % face["panel"]["flips_repaired"])
    L.append("- 三条局限照印（票池幸存者 / incumbent 风险随名单 / 生产候选 nobond_vt08 无债槽、"
             "永不打印防御单，所以这一面量的是全类书的决定）。\n")
    L.append("<!-- ETF-BOOK-SKIP-THE-EXIT:END -->\n")
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    with open(DOC, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    return DOC


def check():
    """STALE when the panel bytes/cutoff moved; CHECK FAILED when the same inputs give
    different numbers."""
    if not os.path.exists(FACE):
        print("STALE face missing", os.path.relpath(FACE, ROOT))
        return 3
    with open(FACE, encoding="utf-8") as f:
        old = json.load(f)
    close, openp, amt, feats, score, cls, n_flip = _inputs()
    now_cut = str(pd.Timestamp(close.index.max()).date())
    if old.get("evidence_cutoff") != now_cut:
        print("STALE evidence_cutoff %s -> %s" % (old.get("evidence_cutoff"), now_cut))
        return 3
    if list(close.shape) != old.get("panel", {}).get("shape"):
        print("STALE panel shape %s -> %s" % (old.get("panel", {}).get("shape"),
                                              list(close.shape)))
        return 3
    face, _ = derive()
    keys = [("book", "cagr"), ("book", "sharpe"), ("skip", "cagr"), ("skip", "sharpe"),
            ("delta", "total_log"), ("skips", "n")]
    bad = []
    for arm, k in keys:
        a, b = old.get(arm, {}).get(k), face.get(arm, {}).get(k)
        if a is None or b is None:
            bad.append("%s.%s %r != %r" % (arm, k, a, b))
            continue
        tol = 1e-9 if isinstance(a, float) else 0
        if abs(float(a) - float(b)) > tol:
            bad.append("%s.%s %r != %r" % (arm, k, a, b))
    if bad:
        print("CHECK FAILED", "; ".join(bad[:4]))
        return 1
    print("CHECK OK %d legs  skips=%d  delta %.0f CNY" %
          (len(keys), face["skips"]["n"], face["delta"]["total_cny"]))
    return 0


# ---------------------------------------------------------------- selftest
def _fixture(n_bars=300, crash=False, n_equity=6, n_bond=6):
    """Synthetic panel: equity names (EEE*) that either drift up or fall hard right after
    the defensive window opens, plus bond names (BBB*) that do not. Scores make the book
    pick EEE* until bar `switch`, then BBB* -- so a defensive rebalance really exists and
    the skip branch has something to refuse. Six bonds so the top-5 can be all bonds."""
    idx = pd.bdate_range("2021-01-04", periods=n_bars)
    eq = ["EEE%d" % (k + 1) for k in range(n_equity)]
    bd = ["BBB%d" % (k + 1) for k in range(n_bond)]
    cols = eq + bd
    close = pd.DataFrame(100.0, index=idx, columns=cols)
    switch = int(n_bars * 0.5)
    rng = np.random.default_rng(7)  # fixed seed: the fixture must be deterministic
    for i in range(1, n_bars):
        drift = -0.02 if (crash and i >= switch) else 0.002
        for c in eq:
            # the realised-vol gate would demote a constant-drift series to `money`;
            # real equity names carry noise, so the fixture carries it too
            step = drift + float(rng.normal(0.0, 0.012))
            close.loc[idx[i], c] = close.loc[idx[i - 1], c] * (1 + step)
        for c in bd:
            close.loc[idx[i], c] = close.loc[idx[i - 1], c] * (1 + 0.0002)
    openp = close.shift(1).fillna(close)
    amt = pd.DataFrame(1e9, index=idx, columns=cols)
    vals = np.zeros((n_bars, len(cols)))
    for k in range(n_equity):
        vals[:switch, k] = 1.0 - 0.01 * k
    for k in range(n_bond):
        vals[switch:, n_equity + k] = 1.0 - 0.01 * k
    score = pd.DataFrame(vals, index=idx, columns=cols)
    cmap = {c: ("equity" if c in eq else "bond", "") for c in cols}
    cls = A.classify(close.columns, cmap, close)
    return close, openp, amt, score, cls


def selftest():
    legs = []

    def leg(name, ok, extra=""):
        legs.append((name, bool(ok), extra))

    # 1. the branch is dead when off: skip=False == engine on the real synthetic scale
    close, openp, amt, score, cls = _fixture(crash=False)
    s_off, _, t_off, mixes_off, _ = run_two(close, openp, amt, score, cls, False,
                                            rebal=5, n_hold=5, cost=0.001)
    s_engine, _, t_e, mixes_e = A.run_with_attribution(close, openp, amt, score, cls,
                                                       rebal=5, n_hold=5, cost=0.001)
    leg("off-branch bit-identical to engine",
        len(s_off) == len(s_engine) and np.allclose(s_off.values, s_engine.values,
                                                    rtol=0, atol=1e-12),
        "len %d/%d" % (len(s_off), len(s_engine)))

    # 2. the branch actually fires when on (the fixture does switch to bonds)
    _, _, _, _, skipped = run_two(close, openp, amt, score, cls, True,
                                  rebal=5, n_hold=5, cost=0.001)
    leg("skip branch fires at least once", len(skipped) >= 1, "n=%d" % len(skipped))

    # 3. skipping is free of turnover: a skipped decision books cost_saved > 0
    leg("skipped decision saves cost",
        all(r["cost_saved"] > 0 for r in skipped) if skipped else False,
        "first=%.6f" % (skipped[0]["cost_saved"] if skipped else -1))

    # 4. in a crash after the defence signal, skipping must LOSE money
    close_c, openp_c, amt_c, score_c, cls_c = _fixture(crash=True)
    b_c, _, _, _, _ = run_two(close_c, openp_c, amt_c, score_c, cls_c, False,
                              rebal=5, n_hold=5, cost=0.001)
    s_c, _, _, _, _ = run_two(close_c, openp_c, amt_c, score_c, cls_c, True,
                              rebal=5, n_hold=5, cost=0.001)
    leg("skip loses in a crash", float(s_c.iloc[-1]) < float(b_c.iloc[-1]),
        "book %.4f skip %.4f" % (b_c.iloc[-1], s_c.iloc[-1]))

    # 5. determinism: two runs byte-identical
    r1, _, _, _, _ = run_two(close_c, openp_c, amt_c, score_c, cls_c, True,
                             rebal=5, n_hold=5, cost=0.001)
    r2, _, _, _, _ = run_two(close_c, openp_c, amt_c, score_c, cls_c, True,
                             rebal=5, n_hold=5, cost=0.001)
    leg("deterministic", np.array_equal(r1.values, r2.values))

    # 6. the face on disk must carry its own verdict as a token
    if os.path.exists(FACE):
        with open(FACE, encoding="utf-8") as f:
            face = json.load(f)
        leg("face carries verdict token",
            face.get("verdict") in ("SKIPPING_THE_EXIT_COSTS_MONEY",
                                    "SKIPPING_THE_EXIT_MAKES_MONEY"))
        leg("face says the branch is dead when off",
            bool(face.get("branch_is_dead_when_off", {}).get("bit_identical")))
    else:
        leg("face exists", False, "missing")

    # 7. behaviour leg: a stale cutoff must return 3 with the word STALE (r1934)
    if os.path.exists(FACE):
        tmp = FACE + ".selftest.json"
        orig_face = FACE
        try:
            with open(FACE, encoding="utf-8") as f:
                poison = json.load(f)
            poison["evidence_cutoff"] = "1999-01-01"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(poison, f)
            import io
            from contextlib import redirect_stdout
            globals()["FACE"] = tmp
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = check()
            out = buf.getvalue()
            leg("stale cutoff -> rc3 + STALE", rc == 3 and "STALE" in out, out.strip()[:60])
        finally:
            globals()["FACE"] = orig_face
            if os.path.exists(tmp):
                os.remove(tmp)
    else:
        leg("stale behaviour leg", False, "no face")

    # 8. behaviour leg: a same-inputs number change must be CHECK FAILED (no STALE word)
    if os.path.exists(FACE):
        tmp = FACE + ".selftest2.json"
        orig_face = FACE
        try:
            with open(FACE, encoding="utf-8") as f:
                poison = json.load(f)
            poison["delta"]["total_log"] = float(poison["delta"]["total_log"]) + 0.01
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(poison, f)
            import io
            from contextlib import redirect_stdout
            globals()["FACE"] = tmp
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = check()
            out = buf.getvalue()
            leg("number mismatch -> rc1 + CHECK FAILED, no STALE",
                rc == 1 and "CHECK FAILED" in out and "STALE" not in out,
                out.strip()[:60])
        finally:
            globals()["FACE"] = orig_face
            if os.path.exists(tmp):
                os.remove(tmp)
    else:
        leg("check-failed behaviour leg", False, "no face")

    bad = [l for l in legs if not l[1]]
    for n, ok, extra in legs:
        print("%s %s %s" % ("PASS" if ok else "FAIL", n, extra))
    print("selftest %d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="write",
                    choices=["write", "check", "selftest"])
    a = ap.parse_args(argv)
    if a.cmd == "write":
        return write()
    if a.cmd == "check":
        return check()
    return selftest()


if __name__ == "__main__":
    raise SystemExit(main())
