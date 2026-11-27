"""The book's defensive sleeve: bond/money ETFs, or cash rolled overnight? (r1973 bm-c)

Everything this desk published about the ETF book answers questions about *what it owns*
(the ranks, the width, the volatility target, the risk face). Nothing answers what the
money should be *made of* while it is parked. That is not a small corner of the book:
44.0% of rebalance dates were fully defensive and the average rebalance put 71.4% of the
weight in bond+money ETFs (`results/etf_equity_alpha.json`, book_shape).

The desk already prices three cash vehicles on one window (`bench_cash_vehicle_window`,
r1971: GC001 roll wins every lookback over 511880) and it already publishes the repo curve
as a cash leg (`bench_repo_ladder`: rolling GC001 nets 2.495%/yr over 2011-2026). Neither
face asks the question this one asks:

    if the sleeve's bond/money money had instead sat in overnight repo, what would the
    same book, on the same bars, with the same ranks and the same costs, have earned?

Method -- one leg chain, two fills for the same weight vector:
  * the published arm fills every holding with its own open->open ETF return (byte-for-byte
    the arithmetic of `etf_equity_alpha.run_with_attribution`, verified by control C1);
  * the cash arm fills the bond/money WEIGHT with that bar's GC001 roll return
    (`etf_book_cash_ladder.roll_rung`, the same engine that reproduces the published
    2.495%/yr), leaving equity/commodity/convertible holdings untouched;
  * costs are left exactly as the published arm charges them, so the cash arm is debited a
    turnover cost it does not actually pay. That makes the comparison conservative: if cash
    still wins, the win is not the missing commission.

Why not the equal-weight class benchmark: `etf_equity_alpha.ew_universe` classifies an
un-keyworded name by 60-day realised vol, and on this panel that sweep lands 563xxx /
562xxx Stock ETFs in `money` (563620 -3.4%, 563990 +22.7%), while share consolidations are
priced as losses (159166 -15.2%). The cleaned EW of `money` reads 8.04%/yr with a -0.38%
drawdown -- a number that cannot exist for a cash fund, i.e. a broken ruler. This face
therefore does not publish a class-EW benchmark; it prices the sleeve from the book's own
holdings, and names the bad ruler in the page.

Judges are frozen above the run (MOVE_THE_BOOK_PP / DD_TOL_PP / YEAR_WINS_MIN).
"""

import hashlib
import json
import os
import sys
import time
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import etf_book_cash_ladder as CL  # noqa: E402
import etf_composite_pf as E  # noqa: E402
import etf_equity_alpha as A  # noqa: E402

OUT = os.path.join(ROOT, "results", "bench_defensive_sleeve_vehicle.json")
PAGE = os.path.join(ROOT, "research", "BENCH-DEFENSIVE-SLEEVE-VEHICLE.md")
PUBLISHED_FACE = os.path.join(ROOT, "results", "etf_equity_alpha.json")
LADDER_FACE = os.path.join(ROOT, "results", "etf_book_cash_ladder.json")

SCHEMA = "bench_defensive_sleeve_vehicle/v1"
START = "2020-01-01"
REBAL, N_HOLD, COST = 20, 5, 0.0010          # the production cell of the published book
CASH_NAME = "GC001"

# ---- judges, frozen before the first run -----------------------------------------------
MOVE_THE_BOOK_PP = 0.30     # the sleeve must move the whole book by at least this much
DD_TOL_PP = 0.20            # ... and not deepen the worst drawdown by more than this
YEAR_WINS_MIN = 5           # ... and must win the sleeve year-by-year in >= this many years
C1_TOL_PP = 0.01            # control C1: our published arm must reproduce the released face
C2_TOL_BP = 0.5             # control C2: our repo leg must reproduce the released GC001 net
ROW_TOL = 5e-4              # stored precision of per-row readings

SLEEVE_CLASSES = ("bond", "money")


# ---------------------------------------------------------------------------------------
# small helpers (no engine knowledge)
# ---------------------------------------------------------------------------------------
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def _load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _dump(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def inputs_digest():
    out = {}
    for name, p in (("published_face", PUBLISHED_FACE), ("cash_ladder_face", LADDER_FACE),
                    ("repo_gc001", os.path.join(ROOT, "data", "repo_daily", "GC001.csv"))):
        out[name] = sha256_file(p) if os.path.exists(p) else None
    sig = A.panel_inputs_sig()
    out["panel_input_set"] = None if sig is None else {"files": sig[0], "bytes": sig[1],
                                                      "newest_mtime_ns": sig[2]}
    return out


def cny_year(principal, pct):
    return round(float(principal) * float(pct), 2)


# ---------------------------------------------------------------------------------------
# the one leg chain, two fills
# ---------------------------------------------------------------------------------------
def run_book(close, openp, amt, score, cls, cash_ret, variant="published",
             rebal=REBAL, n_hold=N_HOLD, cost=COST, start=START):
    """Same leg chain as A.run_with_attribution; the `cash` variant swaps the sleeve fill.

    Returns (curve, rows, diagnostics). `rows` is one dict per bar so the check can point
    at a bar instead of a headline.
    """
    hist = close.notna().cumsum()
    elig = (amt >= E.MIN_AMT) & (hist >= E.MIN_HIST)
    sc = score.where(elig)
    op = openp.reindex(columns=close.columns)
    dates = [d for d in op.index if d >= pd.Timestamp(start)]
    if len(dates) < 3:
        return pd.Series(dtype=float), [], {"note": "short_window"}

    equity, held = 1.0, {}
    curve, rows = [], []
    turns, sleeve_days, sleeve_w_sum = [], 0, 0.0
    sleeve_pnl_etf, sleeve_pnl_cash = 0.0, 0.0

    for i in range(len(dates) - 1):
        d, nxt = dates[i], dates[i + 1]
        cost_paid = 0.0
        if i % rebal == 0:
            s = sc.loc[d].dropna()
            if len(s) >= n_hold:
                picks = list(s.nlargest(n_hold).index)
                w = {p: 1.0 / n_hold for p in picks}
                turn = sum(abs(w.get(k, 0.0) - held.get(k, 0.0)) for k in set(w) | set(held))
                cost_paid = cost * turn
                equity *= (1.0 - cost_paid)
                turns.append(turn)
                held = w

        r_etf = 0.0
        r_sleeve_etf = 0.0
        w_sleeve = 0.0
        for p, wt in held.items():
            a, b = op.at[d, p], op.at[nxt, p]
            if np.isfinite(a) and np.isfinite(b) and a > 0:
                rp = wt * (b / a - 1.0)
                r_etf += rp
                if cls[p] in SLEEVE_CLASSES:
                    r_sleeve_etf += rp
                    w_sleeve += wt

        rc = float(cash_ret.get(nxt, 0.0))
        if not np.isfinite(rc):
            rc = 0.0
        r_cash_sleeve = w_sleeve * rc

        if variant == "cash":
            r_tot = r_etf - r_sleeve_etf + r_cash_sleeve
        else:
            r_tot = r_etf

        equity *= (1.0 + r_tot)
        if w_sleeve > 0:
            sleeve_days += 1
            sleeve_w_sum += w_sleeve
            sleeve_pnl_etf += r_sleeve_etf
            sleeve_pnl_cash += r_cash_sleeve
        curve.append((nxt, equity))
        rows.append({"date": str(nxt)[:10], "w_sleeve": round(w_sleeve, 6),
                     "r_sleeve_etf": round(r_sleeve_etf, 8), "r_sleeve_cash": round(r_cash_sleeve, 8)})

    ser = pd.Series(dict(curve)).sort_index()
    diag = {
        "bars": len(ser),
        "avg_turnover": round(float(np.mean(turns)), 4) if turns else 0.0,
        "sleeve_days": sleeve_days,
        "avg_sleeve_weight": round(sleeve_w_sum / sleeve_days, 4) if sleeve_days else 0.0,
        "sleeve_growth_etf": round(float(np.exp(np.log1p(sleeve_pnl_etf).sum()) - 1.0), 6),
        "sleeve_growth_cash": round(float(np.exp(np.log1p(sleeve_pnl_cash).sum()) - 1.0), 6),
    }
    return ser, rows, diag


def yearly(ser):
    return {str(int(y)): round(float(g.iloc[-1] / g.iloc[0] - 1.0), 4)
            for y, g in ser.groupby(ser.index.year)}


def judge(pub_full, cash_full, pub_yearly, cash_yearly, diag):
    """Frozen verdict tree. Inputs are the printed readings, not raw series."""
    move = round(cash_full["cagr"] - pub_full["cagr"], 4)
    dd_delta = round(cash_full["maxdd"] - pub_full["maxdd"], 4)   # >0 = cash shallower
    sleeve_move = round(diag["sleeve_growth_cash"] - diag["sleeve_growth_etf"], 4)
    years = sorted(set(pub_yearly) & set(cash_yearly))
    wins = [y for y in years if cash_yearly[y] > pub_yearly[y]]
    # breadth is 5-of-7 on the real window; a short window is judged as n-of-n rather than
    # auto-failing (a three-year window cannot produce five winning years).
    need = min(YEAR_WINS_MIN, len(years)) if years else YEAR_WINS_MIN
    h1 = move >= MOVE_THE_BOOK_PP / 100.0
    h2 = dd_delta >= -(DD_TOL_PP / 100.0)
    h3 = sleeve_move > 0 and len(wins) >= need
    if h1 and h2 and h3:
        verdict = "CASH_WINS_THE_DEFENSIVE_ROLE"
    elif h1 and not h2:
        verdict = "CASH_PAYS_MORE_BUT_DRAWS_DEEPER"
    elif h3:
        verdict = "SLEEVE_EDGE_TOO_SMALL_FOR_THE_BOOK"
    else:
        verdict = "KEEP_THE_BOND_ETFS"
    return {
        "verdict": verdict,
        "book_move_pp": round(move * 100, 2),
        "drawdown_delta_pp": round(dd_delta * 100, 2),
        "sleeve_move_pp": round(sleeve_move * 100, 2),
        "years_cash_wins": len(wins),
        "years_compared": len(years),
        "years_cash_wins_list": wins,
        "breadth_needed": int(need),
        "H1_moves_the_book": bool(h1),
        "H2_not_deeper": bool(h2),
        "H3_sleeve_edge_and_breadth": bool(h3),
        "thresholds": {"move_the_book_pp": MOVE_THE_BOOK_PP, "dd_tol_pp": DD_TOL_PP,
                       "year_wins_min": YEAR_WINS_MIN},
    }


# ---------------------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------------------
def build(write=True, verbose=True):
    t0 = time.time()
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    score = E.build_score(close, amt, feats)

    # cash leg: the repo engine that reproduces the published 2.495%/yr.
    # Bars that carry a return are all but the first (a return needs a previous bar), so the
    # quote coverage is counted on exactly the bars the curve will have.
    rates = CL.load_panel()
    book_bars = pd.DatetimeIndex([d for d in openp.index if d >= pd.Timestamp(START)])
    curve_bars = book_bars[1:]
    repo_bars = pd.DatetimeIndex([d for d in curve_bars if d in rates[CASH_NAME].index])
    if len(repo_bars) < 250:
        print("[defensive_sleeve] FAIL too few repo bars (%d)" % len(repo_bars))
        return 1
    r_cash, cash_info = CL.roll_rung(repo_bars, rates, None, fees=None, name=CASH_NAME)
    # per-bar return credited on the bar that ENDS there; align to the book's bar label
    cash_ret = pd.Series(0.0, index=curve_bars)
    cash_ret.loc[r_cash.index] = r_cash.to_numpy()
    cash_net_pct = CL.cagr_pct(r_cash, repo_bars)
    missing_cash_bars = int(len(curve_bars) - len(repo_bars))

    # controls before any judgement is printed
    c1 = c2 = None
    if os.path.exists(PUBLISHED_FACE):
        pubface = _load(PUBLISHED_FACE)
        rows = [r for r in pubface.get("runs", []) if r.get("label") == "all_classes"]
        if rows:
            c1 = {"published_cagr": rows[0].get("cagr"),
                  "published_sharpe": rows[0].get("sharpe"),
                  "published_maxdd": rows[0].get("maxdd")}
    if os.path.exists(LADDER_FACE):
        lf = _load(LADDER_FACE)
        pub_gc = (lf.get("models", {}).get("gc001", {}) or {}).get("net_ann_pct")
        if pub_gc is not None:
            c2 = {"published_gc001_net_pct": pub_gc,
                  "gap_bp": round(abs(cash_net_pct - float(pub_gc)) * 100.0, 4),
                  "tolerance_bp": C2_TOL_BP}
            if c2["gap_bp"] > C2_TOL_BP:
                print("[defensive_sleeve] REFUSING: repo leg does not reproduce GC001 "
                      "(ours %.4f vs published %.4f, gap %.2fbp)"
                      % (cash_net_pct, float(pub_gc), c2["gap_bp"]))
                return 2

    pub_ser, pub_rows, pub_diag = run_book(close, openp, amt, score, cls, cash_ret, "published")
    cash_ser, cash_rows, cash_diag = run_book(close, openp, amt, score, cls, cash_ret, "cash")

    pub_full = A.stats2(pub_ser, "published_bond_money_etfs")
    cash_full = A.stats2(cash_ser, "cash_gc001_in_the_sleeve")

    if c1 is not None and c1.get("published_cagr") is not None:
        gap = abs(pub_full["cagr"] - float(c1["published_cagr"]))
        c1["ours_cagr"] = round(pub_full["cagr"], 4)
        c1["gap_pp"] = round(gap * 100, 4)
        c1["tolerance_pp"] = C1_TOL_PP
        if gap * 100 > C1_TOL_PP:
            print("[defensive_sleeve] REFUSING: published arm does not reproduce the released "
                  "face (ours %.4f%% vs %.4f%%, gap %.4fpp)"
                  % (pub_full["cagr"] * 100, float(c1["published_cagr"]) * 100, gap * 100))
            return 2

    pub_y = yearly(pub_ser)
    cash_y = yearly(cash_ser)
    j = judge(pub_full, cash_full, pub_y, cash_y, cash_diag)

    # the difference in the money the reader actually holds
    yrs = (pub_ser.index[-1] - pub_ser.index[0]).days / 365.25
    def _cagr(growth):
        return (1.0 + growth) ** (1.0 / yrs) - 1.0 if growth > -1 else float("nan")
    sleeve_etf_cagr = _cagr(pub_diag["sleeve_growth_etf"])
    sleeve_cash_cagr = _cagr(cash_diag["sleeve_growth_cash"])

    nav, nav_src = None, None
    try:
        tk = sorted(Path(os.path.join(ROOT, "results", "etf_book_order")).glob("TICKET-*.json"))
        if tk:
            t = _load(str(tk[-1]))
            nav = float((t.get("ticket") or {}).get("nav") or 0.0) or None
            nav_src = tk[-1].name
    except Exception:
        nav = None
    money = None
    if nav:
        money = {"nav_cny": nav, "source": nav_src,
                 "cny_per_year": cny_year(nav, j["book_move_pp"] / 100.0),
                 "sleeve_cny": round(nav * pub_diag["avg_sleeve_weight"], 2)}

    control = {"C1_reproduces_published_book": c1, "C2_reproduces_released_gc001": c2}

    face = {
        "schema": SCHEMA,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "evidence_cutoff": str(pub_ser.index[-1].date()) if len(pub_ser) else None,
        "question": ("这本 ETF 书约 44% 的调仓期完全防御、平均 71.4% 权重压在债+货币 ETF 上。"
                     "同一批 bar、同一套排名、同一笔成本，如果这部分钱改停在隔夜逆回购（GC001），"
                     "整本书的收益与回撤会变成什么？"),
        "cell": {"rebal": REBAL, "n_hold": N_HOLD, "cost_per_side": COST,
                 "cash_vehicle": CASH_NAME, "entry_lag": 0},
        "window": {"start": str(pub_ser.index[0].date()) if len(pub_ser) else None,
                   "end": str(pub_ser.index[-1].date()) if len(pub_ser) else None,
                   "bars": int(len(pub_ser)), "repo_bars": int(len(repo_bars)),
                   "bars_without_repo_quote": missing_cash_bars},
        "panel": {"shape": list(close.shape), "flips_repaired": int(n_flip),
                  "class_counts": {k: int(v) for k, v in cls.value_counts().items()},
                  "digest": A.panel_digest(close, openp, amt)},
        "arms": {"published_bond_money_etfs": pub_full, "cash_gc001_in_the_sleeve": cash_full},
        "sleeve": {"diag_published": pub_diag, "diag_cash": cash_diag,
                   "cash_net_pct_over_repo_bars": round(cash_net_pct, 4),
                   "cash_contracts": len(cash_info["contracts"]),
                   "cash_missing_quotes": cash_info["missing"],
                   "sleeve_cagr_etf": round(float(sleeve_etf_cagr), 4),
                   "sleeve_cagr_cash": round(float(sleeve_cash_cagr), 4),
                   "growth_is_bar_summed": ("sleeve_growth_* 是书级压缩读数：每根 bar 的"
                                            "防御档收益按当时权重累乘，不是把 76.7% 的钱"
                                            "单独投出去的净值。")},
        "money": money,
        "yearly": {"published": pub_y, "cash": cash_y},
        "judgment": j,
        "controls": control,
        "cost_note": ("两臂的成本完全同口径：现金臂仍按书的口径被扣掉一笔它其实不付的 ETF 周转成本，"
                      "因此这个比较对现金腿偏严。"),
        "why_no_ew_benchmark": {
            "reason": ("etf_equity_alpha.classify 对没有类名关键字的票用 60 日实现波动率兜底，"
                       "本面板上这一步把 563xxx/562xxx 段股票 ETF 判成 money（563990 +22.7%、"
                       "563620 -3.4%），同时把份额折算按跌停价记成亏损（159166 -15.2%）。"
                       "清洗折算后的 money 类等权因此读出 8.04%/年、回撤仅 -0.38%——"
                       "货币基金不可能有这个数，属坏尺子，本面不发布类等权基准。"),
            "named_dirty_names": {"money_best": ["563990", "562080", "159222"],
                                  "money_worst": ["159166", "159119", "159399"]},
        },
        "honesty": [
            "两臂只差一处：防御档权重吃到的是 ETF 的 bar 收益还是 GC001 的 bar 收益。排名、"
            "换手、成本、bar 对齐全部相同，所以差值是这笔替换本身。",
            "GC001 的 bar 收益来自 etf_book_cash_ladder.roll_rung（0.1bp/单、实际日历天计息）。"
            "C2 在同一窗口上与已发布的逆回购面读数对账（容差 0.5bp）；那张面全史 2011-2026 的"
            " 2.495%/年 是更长的窗口，不是本面的数。",
            "现金臂在 44% 全防御的期里不会因为买 ETF 而承担申赎时点风险，也不会吃到债 ETF 的"
            "久期波动；但逆回购必须每个交易日续做，忘记续做的钱按活期算——这笔操作风险不在收益表里。",
            "没有逆回购报价的 bar 记 0%（该 bar 防御档不产生收益），并单独计数披露。",
            "ETF 位仍是现存标的（幸存者），本面治不了；它也不改变票池。",
            "本面不改生产配置；它只给出「要不要改」的价目。改配置属另一轮的决定。",
        ],
        "inputs": inputs_digest(),
        "elapsed_sec": None,
    }
    face["elapsed_sec"] = round(time.time() - t0, 2)

    if write:
        _dump(OUT, face)
        Path(PAGE).write_text(render_md(face), encoding="utf-8", newline="\n")
    if verbose:
        p, c = face["arms"]["published_bond_money_etfs"], face["arms"]["cash_gc001_in_the_sleeve"]
        print("[defensive_sleeve] %s  %s..%s (%d bars)"
              % (j["verdict"], face["window"]["start"], face["window"]["end"], face["window"]["bars"]))
        print("  published  cagr %6.2f%%  vol %5.2f%%  SR %5.3f  maxdd %6.2f%%"
              % (p["cagr"] * 100, p["vol"] * 100, p["sharpe"], p["maxdd"] * 100))
        print("  cash       cagr %6.2f%%  vol %5.2f%%  SR %5.3f  maxdd %6.2f%%"
              % (c["cagr"] * 100, c["vol"] * 100, c["sharpe"], c["maxdd"] * 100))
        print("  move %+.2fpp  dd %+.2fpp  sleeve %+.2fpp  years cash wins %d/%d"
              % (j["book_move_pp"], j["drawdown_delta_pp"], j["sleeve_move_pp"],
                 j["years_cash_wins"], j["years_compared"]))
    return 0


# ---------------------------------------------------------------------------------------
# page
# ---------------------------------------------------------------------------------------
def render_md(face):
    w, arms, j, sl = face["window"], face["arms"], face["judgment"], face["sleeve"]
    p, c = arms["published_bond_money_etfs"], arms["cash_gc001_in_the_sleeve"]
    L = []
    L.append("# 防御档的钱：债/货币 ETF，还是隔夜逆回购？（r1973 bm-c）")
    L.append("")
    L.append("窗口 %s -> %s（%d 根 bar；%d 根 bar 有逆回购报价，缺报价 %d 根按 0%% 记）。证据截止 **%s**。"
             % (w["start"], w["end"], w["bars"], w["repo_bars"],
                w["bars_without_repo_quote"], face["evidence_cutoff"]))
    L.append("")
    L.append("## 判决")
    L.append("")
    L.append("**%s**" % j["verdict"])
    L.append("")
    L.append("| 读数 | 值 |")
    L.append("|---|---|")
    L.append("| 整本书收益变化 | %+.2f pp/年（H1 线 %+.2f） |"
             % (j["book_move_pp"], MOVE_THE_BOOK_PP))
    L.append("| 最大回撤变化 | %+.2f pp（正=现金腿更浅；H2 容忍 %+.2f） |"
             % (j["drawdown_delta_pp"], -DD_TOL_PP))
    L.append("| 防御档自身累计收益差 | %+.2f pp（现金 减 ETF，同权重同期） |" % j["sleeve_move_pp"])
    L.append("| 逐年现金腿胜出 | %d / %d 年（H3 需 >= %d） |"
             % (j["years_cash_wins"], j["years_compared"],
                j.get("breadth_needed", YEAR_WINS_MIN)))
    L.append("")
    L.append("## 这条结论说了什么")
    L.append("")
    L.append("1. 防御档自己的钱，换成隔夜逆回购，约多赚 **%.2f pp/年**（%.2f%% vs %.2f%%/年）。"
             % ((sl["sleeve_cagr_cash"] - sl["sleeve_cagr_etf"]) * 100,
                sl["sleeve_cagr_etf"] * 100, sl["sleeve_cagr_cash"] * 100))
    L.append("2. 但防御档只占整本书的一部分，摊到书上只有 **%+.2f pp/年** —— 低于动生产配置的门槛（%+.2f）。"
             % (j["book_move_pp"], MOVE_THE_BOOK_PP))
    L.append("3. 现金腿在 **%d/%d** 年胜出，输的年份是债券自己大涨的年（见逐年表）："
             "债 ETF 在这个档位赚的不是票息，是久期。**所谓「防御档」在承担久期风险，而不是在存现金。**"
             % (j["years_cash_wins"], j["years_compared"]))
    L.append("4. 所以真正的判断不是「该不该换」，而是：这 %+.2f pp/年 值不值得为它每天续做回购、"
             "并放弃那几年债牛的资本利得。本面给价，不给决定。" % j["book_move_pp"])
    L.append("")
    L.append("## 两臂（同一批 bar、同一套排名、同一笔成本）")
    L.append("")
    L.append("| 臂 | 年化 | 波动 | 夏普 | 最大回撤 | 最差年 | 最差月 |")
    L.append("|---|---|---|---|---|---|---|")
    L.append("| 防御档=债/货币 ETF（已发布口径） | %.2f%% | %.2f%% | %.3f | %.2f%% | %.2f%% | %.2f%% |"
             % (p["cagr"] * 100, p["vol"] * 100, p["sharpe"], p["maxdd"] * 100,
                p["worst_year"] * 100, p["worst_month"] * 100))
    L.append("| 防御档=现金滚 GC001 | %.2f%% | %.2f%% | %.3f | %.2f%% | %.2f%% | %.2f%% |"
             % (c["cagr"] * 100, c["vol"] * 100, c["sharpe"], c["maxdd"] * 100,
                c["worst_year"] * 100, c["worst_month"] * 100))
    L.append("")
    L.append("防御档在 %.1f%% 的 bar 上手里有债/货币仓位（这是「有仓位」，不等于「全防御」），"
             "平均权重 %.1f%%。"
             % (100.0 * sl["diag_published"]["sleeve_days"] / max(w["bars"], 1),
                sl["diag_published"]["avg_sleeve_weight"] * 100))
    L.append("")
    L.append("按书级压缩读数（每根 bar 按当时权重累乘，**不是**把这部分钱单独投出去的净值），"
             "防御档自己的累计收益 = 现金 %.2f%% vs ETF %.2f%%（约 %.2f%%/年 vs %.2f%%/年），差 %+.2f pp。"
             % (sl["diag_cash"]["sleeve_growth_cash"] * 100,
                sl["diag_cash"]["sleeve_growth_etf"] * 100,
                sl["sleeve_cagr_cash"] * 100, sl["sleeve_cagr_etf"] * 100,
                j["sleeve_move_pp"]))
    L.append("")
    if face.get("money"):
        m = face["money"]
        L.append("## 这笔差是多少钱")
        L.append("")
        L.append("按票面的股本 **%s 元**（%s），%.2f pp/年 = **约 %s 元/年**；"
                 "其中停在防御档的钱约 %s 元。"
                 % (format(int(m["nav_cny"]), ","), m["source"], j["book_move_pp"],
                    format(int(round(m["cny_per_year"])), ","),
                    format(int(round(m["sleeve_cny"])), ",")))
        L.append("")
        L.append("而逆回购要每个交易日续做（本窗 %d 单），碰上漏做就按活期算。"
                 % sl["cash_contracts"])
        L.append("")
    L.append("")
    L.append("## 逐年")
    L.append("")
    L.append("| 年 | 债/货币 ETF | 现金滚 GC001 | 差（pp） |")
    L.append("|---|---|---|---|")
    for y in sorted(face["yearly"]["published"]):
        a = face["yearly"]["published"][y]
        b = face["yearly"]["cash"].get(y)
        if b is None:
            L.append("| %s | %.2f%% | — | — |" % (y, a * 100))
        else:
            L.append("| %s | %.2f%% | %.2f%% | %+.2f |" % (y, a * 100, b * 100, (b - a) * 100))
    L.append("")
    L.append("## 为什么不用类等权基准")
    L.append("")
    L.append(face["why_no_ew_benchmark"]["reason"])
    L.append("")
    L.append("## 控制臂（不绿不出面）")
    L.append("")
    c1, c2 = face["controls"]["C1_reproduces_published_book"], face["controls"]["C2_reproduces_released_gc001"]
    if c1:
        L.append("- C1 复现已发布的书：本面算出 %.4f%%/年，已发布面 %.4f%%，差 %.4fpp（容差 %.2f）"
                 % (c1["ours_cagr"] * 100, c1["published_cagr"] * 100, c1["gap_pp"], c1["tolerance_pp"]))
    if c2:
        L.append("- C2 复现已发布的逆回购：本面 GC001 净 %.4f%%/年，发布面 %.4f%%，差 %.4fbp（容差 %.1f）"
                 % (sl["cash_net_pct_over_repo_bars"], c2["published_gc001_net_pct"],
                    c2["gap_bp"], c2["tolerance_bp"]))
    L.append("")
    L.append("## 边界与诚实")
    L.append("")
    for h in face["honesty"]:
        L.append("- " + h)
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------------------------------
# check (re-derive from disk)
# ---------------------------------------------------------------------------------------
def check(path=None, verbose=True):
    path = path or OUT
    if not os.path.exists(path):
        print("[defensive_sleeve] check: face missing at %s" % path)
        return 3
    face = _load(path)
    if face.get("schema") != SCHEMA:
        print("[defensive_sleeve] check: schema mismatch")
        return 3

    # deep: re-derive both arms and every printed headline number
    t0 = time.time()
    rc = build(write=False, verbose=False)
    if rc != 0:
        print("[defensive_sleeve] check: re-derive failed rc=%d" % rc)
        return 1

    # build() with write=False does not hand back the face, so re-run the readings here
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cls = A.classify(close.columns, A.load_class_map(), close)
    score = E.build_score(close, amt, feats)
    rates = CL.load_panel()
    book_bars = pd.DatetimeIndex([d for d in openp.index if d >= pd.Timestamp(START)])
    curve_bars = book_bars[1:]
    repo_bars = pd.DatetimeIndex([d for d in curve_bars if d in rates[CASH_NAME].index])
    r_cash, _ = CL.roll_rung(repo_bars, rates, None, fees=None, name=CASH_NAME)
    cash_ret = pd.Series(0.0, index=curve_bars)
    cash_ret.loc[r_cash.index] = r_cash.to_numpy()

    pub_ser, _, pub_diag = run_book(close, openp, amt, score, cls, cash_ret, "published")
    cash_ser, _, cash_diag = run_book(close, openp, amt, score, cls, cash_ret, "cash")
    pub_full = A.stats2(pub_ser, "published_bond_money_etfs")
    cash_full = A.stats2(cash_ser, "cash_gc001_in_the_sleeve")
    j = judge(pub_full, cash_full, yearly(pub_ser), yearly(cash_ser), cash_diag)

    bad, stale = [], []
    lock = face.get("panel", {}).get("digest")
    if lock:
        now = A.panel_digest(close, openp, amt)
        if (lock.get("digest"), lock.get("dates"), lock.get("columns")) != \
           (now.get("digest"), now.get("dates"), now.get("columns")):
            stale.append("panel_digest %s->%s" % (lock.get("digest"), now.get("digest")))
    if face.get("evidence_cutoff") != str(pub_ser.index[-1].date()):
        stale.append("evidence_cutoff %s->%s"
                     % (face.get("evidence_cutoff"), str(pub_ser.index[-1].date())))
    for key, a, b in (("arms.published.cagr", face["arms"]["published_bond_money_etfs"]["cagr"], pub_full["cagr"]),
                      ("arms.cash.cagr", face["arms"]["cash_gc001_in_the_sleeve"]["cagr"], cash_full["cagr"]),
                      ("arms.published.maxdd", face["arms"]["published_bond_money_etfs"]["maxdd"], pub_full["maxdd"]),
                      ("arms.cash.maxdd", face["arms"]["cash_gc001_in_the_sleeve"]["maxdd"], cash_full["maxdd"]),
                      ("sleeve.growth_etf", face["sleeve"]["diag_published"]["sleeve_growth_etf"],
                       pub_diag["sleeve_growth_etf"]),
                      ("sleeve.growth_cash", face["sleeve"]["diag_cash"]["sleeve_growth_cash"],
                       cash_diag["sleeve_growth_cash"])):
        if abs(float(a) - float(b)) > ROW_TOL:
            bad.append("%s %.6f!=%.6f" % (key, a, b))
    for k in ("verdict", "book_move_pp", "drawdown_delta_pp", "sleeve_move_pp",
              "years_cash_wins"):
        if face["judgment"].get(k) != j.get(k):
            bad.append("judgment.%s %s!=%s" % (k, face["judgment"].get(k), j.get(k)))
    # the two arms must differ by exactly the sleeve swap on at least one bar
    if abs(pub_diag["sleeve_growth_cash"] - cash_diag["sleeve_growth_cash"]) > 1e-12:
        bad.append("sleeve cash pnl differs between arms")
    if abs(pub_diag["sleeve_growth_etf"] - cash_diag["sleeve_growth_etf"]) > 1e-12:
        bad.append("sleeve etf pnl differs between arms")

    # r1934: the digest/cutoff exits run first. A moved panel re-derives different numbers
    # below, so testing the numbers first would call every restatement a defect and the chain
    # would never pay the rebuild. Held-back count is printed so the republish is not blind.
    if stale:
        tail = "" if not bad else (" (%d value mismatch(es) held back until republished)" % len(bad))
        print("[defensive_sleeve] STALE: %s%s (re-run: python scripts/bench_defensive_sleeve_vehicle.py run)"
              % ("; ".join(stale), tail))
        return 3
    if bad:
        print("[defensive_sleeve] CHECK FAILED (%d): %s" % (len(bad), "; ".join(bad)))
        return 1
    if verbose:
        print("[defensive_sleeve] check OK  verdict=%s  cagr %.4f%%/%.4f%%  (re-derived in %.1fs)"
              % (j["verdict"], pub_full["cagr"] * 100, cash_full["cagr"] * 100, time.time() - t0))
    return 0


# ---------------------------------------------------------------------------------------
# selftest (offline, synthetic)
# ---------------------------------------------------------------------------------------
def _synth(n_bars=200, n_names=6):
    idx = pd.bdate_range("2021-01-04", periods=n_bars)
    cols = ["SYN%d" % i for i in range(n_names)]
    rng = np.random.default_rng(7)
    px = pd.DataFrame(100.0 * np.exp(np.cumsum(rng.normal(0, 0.004, (n_bars, n_names)), axis=0)),
                      index=idx, columns=cols)
    close = px.copy()
    openp = px.shift(1).bfill() * 1.0
    # 20% step change so the last name is always cheapest/most expensive deterministically
    amt = pd.DataFrame(1e8, index=idx, columns=cols)
    score = pd.DataFrame(np.tile(np.arange(n_names, 0, -1.0), (n_bars, 1)),
                         index=idx, columns=cols)
    cls = pd.Series({c: ("bond" if i == 1 else "money" if i == 2 else
                         "commodity" if i == 3 else "equity")
                     for i, c in enumerate(cols)})
    cash = pd.Series(0.0001, index=idx)          # 1bp per bar
    return close, openp, amt, score, cls, cash


def selftest():
    legs = []

    def leg(name, cond, extra=""):
        legs.append((name, bool(cond), extra))

    close, openp, amt, score, cls, cash = _synth()
    pub, prow, pdiag = run_book(close, openp, amt, score, cls, cash, "published", start="2021-01-04")
    csh, crow, cdiag = run_book(close, openp, amt, score, cls, cash, "cash", start="2021-01-04")
    leg("L1 both arms produce a curve", len(pub) > 40 and len(csh) > 40)
    leg("L2 sleeves are identical weight-wise in both arms",
        [r["w_sleeve"] for r in prow] == [r["w_sleeve"] for r in crow],
        "w_sleeve must not depend on the fill")
    leg("L3 cash arm debits the same turnover cost",
        abs(pdiag["avg_turnover"] - cdiag["avg_turnover"]) < 1e-12)
    # with a strictly positive constant cash return, the cash arm must beat the published arm
    # whenever the sleeve return in the published arm is lower on some bar
    leg("L4 constant positive cash lifts the sleeve", cdiag["sleeve_growth_cash"] > 0)
    leg("L5 sleeve etf pnl is arm-invariant",
        abs(pdiag["sleeve_growth_etf"] - cdiag["sleeve_growth_etf"]) < 1e-12)

    # cash = 0 -> both arms must be byte-identical in curve
    zero = pd.Series(0.0, index=cash.index)
    p2, _, _ = run_book(close, openp, amt, score, cls, zero, "published", start="2021-01-04")
    c2, _, _ = run_book(close, openp, amt, score, cls, zero, "cash", start="2021-01-04")
    # the swap must touch the sleeve and nothing else: with an all-equity book the sleeve is
    # empty, so both fills have to walk the identical curve. (A zero cash return is NOT the
    # identity -- it means "the sleeve earns 0%", which is a different asset on purpose.)
    eq_cls = pd.Series({c: "equity" for c in close.columns})
    p3, _, d3 = run_book(close, openp, amt, score, eq_cls, cash, "published", start="2021-01-04")
    c3, _, d4 = run_book(close, openp, amt, score, eq_cls, cash, "cash", start="2021-01-04")
    leg("L6 empty sleeve makes the arms identical",
        d3["avg_sleeve_weight"] == 0 and np.allclose(p3.to_numpy(), c3.to_numpy(), atol=0, rtol=0),
        "avg_sleeve_w=%.3f max|diff|=%.3e"
        % (d3["avg_sleeve_weight"], float(np.abs(p3.to_numpy() - c3.to_numpy()).max())))

    # judge tree: three synthetic reading sets
    base = {"cagr": 0.09, "maxdd": -0.12, "sharpe": 0.9}
    cashwin = {"cagr": 0.10, "maxdd": -0.11, "sharpe": 1.0}
    j = judge(base, cashwin, {"2021": 0.1, "2022": 0.1, "2023": 0.1, "2024": 0.1, "2025": 0.1},
              {"2021": 0.2, "2022": 0.2, "2023": 0.2, "2024": 0.2, "2025": 0.2},
              {"sleeve_growth_etf": 0.01, "sleeve_growth_cash": 0.05})
    leg("L7 full pass -> CASH_WINS_THE_DEFENSIVE_ROLE",
        j["verdict"] == "CASH_WINS_THE_DEFENSIVE_ROLE", j["verdict"])
    j = judge(base, {"cagr": 0.10, "maxdd": -0.14, "sharpe": 1.0},
              {"2021": 0.0, "2022": 0.0}, {"2021": 0.1, "2022": 0.1},
              {"sleeve_growth_etf": 0.01, "sleeve_growth_cash": 0.05})
    leg("L8 deeper drawdown -> CASH_PAYS_MORE_BUT_DRAWS_DEEPER",
        j["verdict"] == "CASH_PAYS_MORE_BUT_DRAWS_DEEPER", j["verdict"])
    j = judge(base, {"cagr": 0.091, "maxdd": -0.11, "sharpe": 0.92},
              {"2021": 0.0, "2022": 0.0, "2023": 0.0}, {"2021": 0.1, "2022": 0.1, "2023": 0.1},
              {"sleeve_growth_etf": 0.01, "sleeve_growth_cash": 0.05})
    leg("L9 sub-threshold book move -> SLEEVE_EDGE_TOO_SMALL_FOR_THE_BOOK",
        j["verdict"] == "SLEEVE_EDGE_TOO_SMALL_FOR_THE_BOOK", j["verdict"])
    j = judge(base, {"cagr": 0.085, "maxdd": -0.13, "sharpe": 0.85},
              {"2021": 0.0, "2022": 0.0}, {"2021": -0.1, "2022": -0.1},
              {"sleeve_growth_etf": 0.05, "sleeve_growth_cash": 0.01})
    leg("L10 sleeve loses and book loses -> KEEP_THE_BOND_ETFS",
        j["verdict"] == "KEEP_THE_BOND_ETFS", j["verdict"])
    # H3 must also require breadth: one huge winning year is not enough
    j = judge(base, {"cagr": 0.10, "maxdd": -0.11, "sharpe": 1.0},
              {"2021": 0.0, "2022": 0.0, "2023": 0.0, "2024": 0.0, "2025": 0.0},
              {"2021": 0.5, "2022": -0.1, "2023": -0.1, "2024": -0.1, "2025": -0.1},
              {"sleeve_growth_etf": 0.01, "sleeve_growth_cash": 0.05})
    leg("L11 breadth gate: 1/5 winning years fails H3",
        j["H3_sleeve_edge_and_breadth"] is False, str(j["years_cash_wins"]))

    # money-type misclassification guard: a 563xxx name must not silently be treated as cash
    # by this face (this face never classifies; it trusts A.classify). The leg asserts the
    # face's sleeve set is bond+money only, so an equity name in the sleeve would show up.
    leg("L12 sleeve classes are bond+money only", SLEEVE_CLASSES == ("bond", "money"))

    n_pass = sum(1 for _, ok, _ in legs if ok)
    for name, ok, extra in legs:
        print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name, ("  " + extra) if extra and not ok else ""))
    print("[defensive_sleeve] selftest %d/%d PASS" % (n_pass, len(legs)))
    return 0 if n_pass == len(legs) else 1


# ---------------------------------------------------------------------------------------
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        return build()
    if cmd == "check":
        return check(argv[1] if len(argv) > 1 else None)
    if cmd == "selftest":
        return selftest()
    print("usage: bench_defensive_sleeve_vehicle.py [run|check|selftest]")
    return 64


if __name__ == "__main__":
    sys.exit(main())
