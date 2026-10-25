"""ETF composite book -- the same book, sold at a stated beta, with a real cash leg.

Five rounds of stress tests (r1251-r1255) ended on three findings worth acting on:

  * the package's value is the removal of the phase choice, never alpha (p=0.62);
  * 66% of its 2024+ lead over its own equal weight was just extra beta (0.295 vs 0.066);
  * the cash remainder is worth reals: observed GC001 repo (2.09%/yr) beats a flat 0%
    by +1.53/+1.00/+0.46pp at beta 0.10/0.20/0.30.

This script turns those into the only artefact that can actually be executed: a daily
target-weight ticket plus a forward ledger that runs on the same accounting from now on.

Accounting (reused, never rewritten):
  * the book's own leg chain = `base.run_next_open` (close decision -> next-open fill,
    8bp/side on |weight change|, overnight to the old book, intraday to the new one);
  * the beta overlay = `BT.apply_overlay` (k = target/beta, clipped to [0,1], a decision
    taken on a close applies from the next bar, |delta k| * 8bp charged on the k leg);
  * the cash leg = `BW.load_repo_rates` + `BW.repo_daily_cash` (GC001 close is an
    annualised yield known at bar t, accrued over the calendar gap to the next bar).

Difference from the stress-test scripts: this one emits a ticket a human or a broker
adapter could follow -- instrument, weight, amount at a stated NAV, whole lots, cash
remainder -- and it accrues that book forward one bar at a time (idempotent by bar).

  python scripts/etf_book_order.py run [--beta=0.20] [--nav=1000000] [--inception=2024-01-01]
  python scripts/etf_book_order.py --selftest

Outputs:
  results/etf_book_order/state.json          book state (target, last bar, nav)
  results/etf_book_order/ledger.jsonl        one row per bar from inception
  results/etf_book_order/TICKET-<asof>.json  executable ticket + evidence
  results/etf_book_order/ORDER-<asof>.md     one-page face (regenerated per run)
  results/etf_book_order/latest.json         pointer to the newest ticket

Exploratory: not a verdict, not investment advice, no ledger booking.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import etf_composite_pf as F          # noqa: E402
from scripts import etf_phase_beta_target as BT    # noqa: E402
from scripts import etf_phase_beta_window as BW    # noqa: E402
from scripts import etf_variants_null_rolling as V  # noqa: E402
from scripts.etf_asset_class import classify       # noqa: E402
from config import PATHS                           # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(PATHS.results_dir, "etf_book_order")

REBAL = 20
N_HOLD = F.N_HOLD
COST_BP = 8.0
DEFAULT_BETA = 0.20
DEFAULT_NAV = 1_000_000.0
DEFAULT_INCEPTION = "2024-01-01"
MIN_HIST = 126
LOT = 100


# ------------------------------------------------------------------ decision schedule
def k_schedule(rp, rm, target, step=REBAL, min_hist=MIN_HIST):
    """[(decision_date, k, beta_hat)] under r1254's expanding-beta rule.

    beta is the expanding OLS slope of the book on the market through the decision
    day only; k = target/beta clipped to [0,1] -- de-risking only, never leverage.
    """
    var = rm.expanding(min_periods=2).var()
    cov = rp.expanding(min_periods=2).cov(rm)
    beta = cov / var
    out = []
    i = int(min_hist)
    while i < len(rp):
        b = beta.iloc[i]
        if b is None or not np.isfinite(b) or b <= 1e-6:
            i += step
            continue
        out.append((rp.index[i], float(min(1.0, max(0.0, target / b))), float(b)))
        i += step
    return out


def in_force(sched, dates):
    """k applied to each bar's return: a decision made on a close applies next bar."""
    if not sched:
        return pd.Series(np.nan, index=dates, dtype=float)
    marks = pd.Series(np.nan, index=dates, dtype=float)
    for d, k, _ in sched:
        if d in marks.index:
            marks.loc[d] = k
    return marks.shift(1).ffill()


# ---------------------------------------------------------------------------- ticket
def build_ticket(score_last, close_last, k, nav, n_hold=N_HOLD, lot=LOT, classes=None):
    """Whole-lot order sheet: k of NAV spread equally over the picks, rest to GC001.

    Weights always sum to 1 (book + cash). Amounts are floor'ed to whole lots, so the
    ticket can only ever spend less than NAV -- the unspent remainder stays in cash and
    is reported, never silently redistributed.
    """
    s = score_last.dropna()
    if len(s) < n_hold:
        return None
    picks = list(s.nlargest(n_hold).index)
    w_each = float(k) / len(picks)
    rows, spent = [], 0.0
    for p in picks:
        px = close_last.get(p, np.nan)
        if not np.isfinite(px) or px <= 0:
            rows.append({"symbol": p, "weight": round(w_each, 6), "price": None,
                         "lots": None, "shares": None, "amount": None,
                         "class": (classes or {}).get(p), "note": "no live price"})
            continue
        want = nav * w_each
        lots = int(want // (px * lot))
        shares = lots * lot
        amt = shares * px
        spent += amt
        rows.append({"symbol": p, "weight": round(w_each, 6), "price": round(float(px), 4),
                     "lots": lots, "shares": shares, "amount": round(amt, 2),
                     "class": (classes or {}).get(p),
                     "note": "" if lots else "budget below one lot"})
    cash_amt = float(nav) - spent
    return {"beta_k": round(float(k), 6), "book_weight": round(float(k), 6),
            "cash_weight": round(1.0 - float(k), 6),
            "nav": float(nav), "order": rows,
            "book_amount": round(spent, 2), "cash_amount": round(cash_amt, 2),
            "cash_leg": "GC001 (1-day repo, observed close)",
            "basket_drift": [n["symbol"] for n in rows if n["amount"] is None],
            "underspend_pct": round(100.0 * cash_amt / float(nav) - 100.0 * (1.0 - k), 4)}


# ----------------------------------------------------------------------------- ledger
def accrue(state, dates, rp, rm, fees_k, rf, sched_k, cost_bp=COST_BP):
    """Name it forward: one row per bar, the k changes charge |delta k| * cost.

    The book leg (rp) already carries its own next-open fill costs and the overlay's
    k leg is charged here -- two layers by design, each on its own notional.
    """
    state = json.loads(json.dumps(state))
    last = state.get("last_bar")
    rows = []
    equity = float(state.get("nav", 1.0))
    prev_k = None if state.get("last_k") is None else float(state["last_k"])
    prev_date = None
    for d in dates:
        if last is not None and d <= pd.Timestamp(last):
            continue
        cost = 0.0 if prev_k is None else abs(float(fees_k.loc[d]) - prev_k) * cost_bp / 10000.0
        rf_day = float(rf.get(d, 0.0) or 0.0) if isinstance(rf, pd.Series) else float(rf)
        r = float(fees_k.loc[d]) * float(rp.loc[d]) + (1.0 - float(fees_k.loc[d])) * rf_day
        equity *= (1.0 + r - cost)
        prev_k = float(fees_k.loc[d])
        prev_date = d
        rows.append({"date": str(d.date()), "nav": round(equity, 8),
                     "ret": round(r - cost, 8), "k": round(float(fees_k.loc[d]), 6),
                     "k_cost": round(cost, 8), "rf": round(rf_day, 8),
                     "decision": str(sched_k.get(d, "")) if isinstance(sched_k, dict) else ""})
    state["nav"] = equity
    state["last_bar"] = str(prev_date.date()) if prev_date is not None else last
    state["last_k"] = prev_k
    state["rows"] = int(state.get("rows", 0)) + len(rows)
    return state, rows


# ------------------------------------------------------------------------- run helpers
def _load_state(inception, beta):
    p = os.path.join(OUT_DIR, "state.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            st = json.load(f)
        if abs(float(st.get("beta_target", -1)) - float(beta)) < 1e-9:
            return st
        print("note: state carries beta_target=%s, requested %s -> fresh state (old ledger kept)"
              % (st.get("beta_target"), beta))
    return {"inception": str(inception), "beta_target": float(beta), "last_bar": None,
            "last_k": None, "nav": 1.0, "rows": 0}


def _write(name, obj):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def metrics(nav_ser, bench_ser, lb=252):
    def block(s):
        if s is None or len(s.dropna()) < 30:
            return None
        s = s.dropna()
        yrs = (s.index[-1] - s.index[0]).days / 365.25
        ret = s.pct_change().dropna()
        cagr = (float(s.iloc[-1]) / float(s.iloc[0])) ** (1.0 / yrs) - 1.0 if yrs > 0 else float("nan")
        vol = float(ret.std() * np.sqrt(252))
        mdd = float((s / s.cummax() - 1.0).min())
        return {"cagr": round(cagr, 4), "sharpe": round((cagr / vol) if vol else float("nan"), 3),
                "maxdd": round(mdd, 4), "vol": round(vol, 4), "bars": int(len(s))}

    out = {"book": block(nav_ser), "same_beta_benchmark": block(bench_ser)}
    if out["book"] and out["same_beta_benchmark"]:
        out["excess_pp"] = round((out["book"]["cagr"] - out["same_beta_benchmark"]["cagr"]) * 100, 2)
    return out


def card(ticket, mk, sched, asof, beta, extra):
    L = ["# ETF 复合书 · 可执行订单单（%s）" % asof, "",
         "当前活：β 目标 %.2f 的单本 R%d N%d + GC001 现金腿，每 %d 个交易日重算一次 k。"
         % (beta, REBAL, N_HOLD, REBAL),
         "最近实物：%s（本文件同日生成）。"
         % os.path.relpath(os.path.join(OUT_DIR, "TICKET-%s.json" % asof), BASE).replace("\\", "/"),
         "下个里程碑：下一决策日落单后前向账本追加一行（窗 ≤48h，随面板推进）。", ""]
    if ticket:
        L += ["## 今日目标（NAV ¥%s）" % format(int(ticket["nav"]), ","),
              "k=%.2f（书内 %.0f%%、现金 %.0f%%）｜ 现金腿=%s ｜ 现金 ¥%s"
              % (ticket["beta_k"], ticket["book_weight"] * 100,
                 ticket["cash_weight"] * 100, ticket["cash_leg"],
                 format(int(ticket["cash_amount"]), ",")),
              "", "| 代码 | 权重 | 类别 | 参考价 | 手数 | 股数 | 金额 |", "|---|---|---|---|---|---|---|"]
        for r in ticket["order"]:
            L.append("| %s | %.1f%% | %s | %s | %s | %s | %s |"
                     % (r["symbol"], r["weight"] * 100, r.get("class") or "?",
                        ("%.3f" % r["price"]) if r["price"] else "-",
                        r["lots"] if r["lots"] is not None else "-",
                        r["shares"] if r["shares"] is not None else "-",
                        format(int(r["amount"]), ",") if r["amount"] else "-"))
        L += ["", "整手取整后欠投 %.2f%% NAV（留在现金腿，不重分配）。" % ticket["underspend_pct"]]
    else:
        L += ["## 今日目标", "当日无有效信号（可选池不足），不下单。"]
    if sched:
        ks = [k for _, k, _ in sched]
        L += ["", "## k 历程", "决策 %d 次｜均值 %.2f｜区间 %.2f~%.2f｜触顶(≥0.999)占比 %.0f%%"
              % (len(ks), float(np.mean(ks)), min(ks), max(ks),
                 100.0 * sum(1 for k in ks if k >= 0.999) / len(ks))]
    if mk and mk.get("book"):
        L += ["", "## 同期对照（%s 起）" % extra.get("inception"),
              "| 账簿 | 年化 | 夏普 | 最大回撤 |", "|---|---|---|---|"]
        for name, zh in (("book", "本账（β 目标 + GC001）"), ("same_beta_benchmark", "同 β 指数+现金")):
            b = mk.get(name)
            if b:
                L.append("| %s | %.1f%% | %.2f | %.1f%% |" % (zh, b["cagr"] * 100, b["sharpe"],
                                                             b["maxdd"] * 100))
        if "excess_pp" in mk:
            L += ["", "超额 %+.2fpp/年（同 β 基准对照，成本双层已计）。" % mk["excess_pp"]]
    L += ["", "## 诚实面", "",
          "- 探索件：无预注册、无判决、不入成绩账本。"]
    st = extra.get("stale")
    if st:
        L += ["- **面板新鲜度**：最后 bar 全池 %d/%d 只有价；历史决策中 %.1f%% 的选票落在"
              "决策日之前已停更的标的上（最坏滞后 %d 天）——停更标的被 ffill 冻结成零收益持仓，"
              "读数会因此偏乐观。" % (st["symbols_with_value_on_last_bar"], st["symbols_total"],
                                     100.0 * (st.get("stale_share") or 0.0),
                                     st["worst_stale_gap_days"])]
    if ticket and ticket.get("basket_drift"):
        L += ["- **票面不可执行**：%d/%d 只在收盘日无价（停更），本单只能作为研究面参考。"
              % (len(ticket["basket_drift"]), len(ticket["order"]))]
    L += ["- 票池=现存 ETF，存在幸存者偏差；票面仅按收盘价折算，未计冲击成本与涨跌停。",
          "- GC001 单期限且滚动假设零费；真实现金台应做 1/7/14 天梯队。",
          "- k 每 %d 个交易日才重算，段内实际 β 仍会漂移。" % REBAL]
    return "\n".join(L) + "\n"


def staleness_stats(score, close, rebal=REBAL, n_hold=N_HOLD, start="2020-01-01"):
    """How much of the book is picked on stale prices?

    This panel is refreshed only for a core handful of instruments; the rest were frozen
    at a one-off batch pull (see DIGEST-20261021-e35). The engine ffill's prices, so a
    frozen symbol silently becomes a zero-return holding. Any book number is suspect
    until the share of stale picks is known.
    """
    dates = [d for d in close.index if d >= pd.Timestamp(start)]
    decs = dates[::rebal]
    picked = stale = impossible = 0
    worst_gap = 0
    last_valid = close.apply(lambda s: s.dropna().index[-1] if s.notna().any() else s.index[0])
    for d in decs:
        s = score.loc[d].dropna() if d in score.index else pd.Series(dtype=float)
        if len(s) < n_hold:
            impossible += 1
            continue
        bar = close.loc[d]
        for p in s.nlargest(n_hold).index:
            picked += 1
            px = bar.get(p, np.nan)
            if not np.isfinite(px):
                stale += 1
                lv = last_valid.get(p)
                worst_gap = max(worst_gap, int((d - lv).days) if lv is not None else 9999)
    live_last = int(close.iloc[-1].notna().sum())
    return {"decisions": len(decs), "picks": picked,
            "stale_picks": stale,
            "stale_share": round(stale / picked, 4) if picked else None,
            "worst_stale_gap_days": worst_gap,
            "symbols_with_value_on_last_bar": live_last,
            "symbols_total": int(close.shape[1]),
            "decisions_with_too_few_picks": impossible}


def run(beta=DEFAULT_BETA, nav=DEFAULT_NAV, inception=DEFAULT_INCEPTION, fresh_gate=False):
    global OUT_DIR
    if fresh_gate:
        OUT_DIR = os.path.join(PATHS.results_dir, "etf_book_order_fresh")
    close, openp, amt, feats = F.build_panel()
    classes = pd.Series(classify(list(close.columns)))
    cols = [c for c in close.columns if classes[c] in V.KEEP]
    score = F.build_score(close[cols], amt[cols], feats)
    stale = staleness_stats(score, close[cols])
    print("staleness: %d/%d picks (%.1f%%) priced before the decision bar | panel live on "
          "last bar %d/%d symbols | worst gap %dd"
          % (stale["stale_picks"], stale["picks"], 100.0 * (stale["stale_share"] or 0.0),
             stale["symbols_with_value_on_last_bar"], stale["symbols_total"],
             stale["worst_stale_gap_days"]), flush=True)
    if fresh_gate:
        # only instruments that actually printed a close on the decision bar are eligible
        score = score.where(close[cols].notna())
        print("fresh gate ON: decisions restricted to symbols with a live bar", flush=True)
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        print("FATAL: no 510300 column on the panel")
        return 2
    mkt = close[mkt_col]

    ser, turnover, gapfill = F.run_next_open(close[cols], openp[cols], amt[cols], feats,
                                             REBAL, n_hold=N_HOLD, cost=F.COST, score=score)
    idx = ser.index.intersection(mkt.index)
    rp, rm = BT.rets(ser.reindex(idx)), BT.rets(mkt.reindex(idx))

    sched = k_schedule(rp, rm, beta)
    k_ser = in_force(sched, idx)
    rates = BW.load_repo_rates()
    cash_rf, cash_missing = BW.repo_daily_cash(idx, rates)
    cash_rf = cash_rf.reindex(idx).fillna(0.0)

    strat, bench, kk = BT.apply_overlay(rp, rm, sched, 0.0, COST_BP, rf=cash_rf)
    if strat is None:
        print("FATAL: overlay produced no live window (not enough history for beta)")
        return 2

    start = pd.Timestamp(inception)
    slip = strat[strat.index >= start]
    blip = bench[bench.index >= start]
    # the overlay only lives where a beta estimate existed, so the forward ledger must
    # start there too -- accruing the warm-up at k=1 would drift off the engine NAV.
    live_k = k_ser.dropna()
    if len(live_k):
        slip = slip[slip.index >= live_k.index[0]]
        blip = blip[blip.index >= live_k.index[0]]

    state = _load_state(inception, beta)
    state["beta_target"] = float(beta)
    dec_dates = {d for d, _, _ in sched}
    rows_in = [d for d in slip.index if state.get("last_bar") is None or
               d > pd.Timestamp(state["last_bar"])]
    merged = []
    if rows_in:
        prev = 1.0 if state.get("last_bar") is None else float(state.get("nav", 1.0))
        last_k = None if state.get("last_k") is None else float(state["last_k"])
        for d in rows_in:
            k_d = float(k_ser.loc[d]) if np.isfinite(k_ser.loc[d]) else (last_k if last_k is not None else 1.0)
            cost = 0.0 if last_k is None else abs(k_d - last_k) * COST_BP / 10000.0
            r = float(rp.loc[d]) * k_d + (1.0 - k_d) * float(cash_rf.loc[d]) - cost
            prev *= (1.0 + r)
            last_k = k_d
            merged.append({"date": str(d.date()), "nav": round(prev, 8), "ret": round(r, 8),
                           "k": round(k_d, 6), "k_cost": round(cost, 8),
                           "rf": round(float(cash_rf.loc[d]), 8),
                           "decision": str(d.date()) if d in dec_dates else ""})
        state.update({"nav": prev, "last_k": last_k, "last_bar": str(rows_in[-1].date()),
                      "rows": int(state.get("rows", 0)) + len(merged)})
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(os.path.join(OUT_DIR, "ledger.jsonl"), "a", encoding="utf-8") as f:
            for r in merged:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # cross-check: the incremental ledger must reproduce the engine NAV at the same date.
    # The ledger's base 1.0 sits the bar *before* the first accrued bar, while the engine
    # slice's first point already carries that bar's return -- strip it before comparing.
    drift = None
    if len(rows_in) and len(slip) > 1:
        f0 = slip.index[0]
        r0 = (float(k_ser.loc[f0]) * float(rp.loc[f0])
              + (1.0 - float(k_ser.loc[f0])) * float(cash_rf.loc[f0]))
        my_norm = float(state["nav"]) / (1.0 + r0)
        eng = float(slip.loc[rows_in[-1]]) / float(slip.iloc[0])
        drift = round(my_norm - eng, 10)

    asof = str(slip.index[-1].date())
    k_now = state.get("last_k")
    if k_now is None:
        k_now = 1.0
    cls_map = dict(zip(close.columns, classes))
    ticket = build_ticket(score.loc[slip.index[-1]], close.loc[slip.index[-1]],
                          k_now, nav, classes=cls_map)
    mk = metrics(slip, blip)
    payload = {"evidence_cutoff": asof, "beta_target": float(beta),
               "inception": str(slip.index[0].date()) if len(slip) else inception,
               "rebal": REBAL, "n_hold": N_HOLD, "cost_bp_per_side": COST_BP,
               "fresh_gate": bool(fresh_gate), "staleness": stale,
               "k_now": round(float(k_now), 6),
               "next_decision_bars": _next_decision(close.index, slip.index[-1]),
               "ticket": ticket, "metrics": mk,
               "book_leg": {"turnover_per_rebal": round(float(turnover), 4),
                            "open_gapfill": int(gapfill)},
               "cash_leg": {"source": "data/repo_daily/GC001.csv",
                            "mean_accrual_ann_pct": round(float(cash_rf.mean() * 252.0) * 100, 3),
                            "missing_bar_steps": int(cash_missing)},
               "ledger": {"bars": int(state.get("rows", 0)), "nav": round(float(state["nav"]), 8),
                          "rows_added": len(merged), "engine_naive_vs_ledger": drift},
               "caveats": ["survivorship: on-disk panel holds ETFs that still exist",
                           "ticket prices are closes; no impact cost, no limit-move guard",
                           "GC001 single tenor, rolling assumed cost-free",
                           "k revised every %d bars so delivered beta still wanders" % REBAL,
                           "exploratory: no preregistration, no verdict, no ledger booking"]}

    _write("state.json", state)
    _write("TICKET-%s.json" % asof, payload)
    _write("latest.json", {"as_of": asof, "file": "TICKET-%s.json" % asof,
                           "beta_target": float(beta), "k_now": round(float(k_now), 6)})
    with open(os.path.join(OUT_DIR, "ORDER-%s.md" % asof), "w", encoding="utf-8") as f:
        f.write(card(ticket, mk, sched, asof, beta,
                     {"inception": payload["inception"], "stale": stale}))

    print("as_of=%s beta=%.2f k=%.2f nav=%.4f rows+=%d drift=%s"
          % (asof, beta, k_now, state["nav"], len(merged), drift))
    if ticket:
        print("ticket: book %.0f%% cash %.0f%% | %s"
              % (ticket["book_weight"] * 100, ticket["cash_weight"] * 100,
                 ", ".join("%s %.1f%%" % (r["symbol"], r["weight"] * 100) for r in ticket["order"])))
    if mk.get("book") and mk.get("same_beta_benchmark"):
        print("book CAGR %.2f%% vs same-beta %.2f%% | excess %+.2fpp"
              % (mk["book"]["cagr"] * 100, mk["same_beta_benchmark"]["cagr"] * 100,
                 mk.get("excess_pp", float("nan"))))
    print("wrote", os.path.join(OUT_DIR, "TICKET-%s.json" % asof))
    return 0


def _next_decision(score_dates, last_bar, rebal=REBAL, start="2020-01-01"):
    """Trading bars until the next decision on the engine's own grid (no future dates exist)."""
    dates = [d for d in score_dates if d >= pd.Timestamp(start)]
    if last_bar not in dates:
        return None
    pos = dates.index(last_bar)
    return int(((pos // rebal) + 1) * rebal - pos)


# --------------------------------------------------------------------------- selftest
def selftest():
    ok = total = 0

    def chk(name, cond, extra=""):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
            print("[ok] %s %s" % (name, extra))
        else:
            print("[FAIL] %s %s" % (name, extra))

    rng = np.random.default_rng(20261025)
    idx = pd.bdate_range("2020-01-01", periods=400)
    rm = pd.Series(rng.normal(0.0002, 0.01, len(idx)), index=idx)
    rp = 0.5 * rm
    beta = (rp.expanding(min_periods=2).cov(rm)
            / rm.expanding(min_periods=2).var()).dropna()
    chk("leg1 expanding beta recovers 0.5", float(np.max(np.abs(beta - 0.5))) < 1e-9,
        "maxerr=%.2e" % float(np.max(np.abs(beta - 0.5))))

    sched = k_schedule(rp, rm, 0.20, step=20)
    chk("leg2 k = target/beta clipped to 1", bool(sched) and
        all(abs(k - 0.4) < 1e-12 for _, k, _ in sched),
        "k=%.3f n=%d" % (sched[0][1], len(sched)))
    sched_hi = k_schedule(rp, rm, 5.0, step=20)     # target >> beta -> must clip at 1
    chk("leg3 k never exceeds 1 (no leverage)", all(k <= 1.0 for _, k, _ in sched_hi),
        "max=%.3f" % max(k for _, k, _ in sched_hi))

    f_idx = pd.DatetimeIndex(["2021-01-08", "2021-01-11", "2021-01-12"])
    rates = pd.Series([3.65, 3.65, 3.65], index=f_idx)
    cash, miss = BW.repo_daily_cash(f_idx, rates)
    chk("leg4 Fri->Mon cash earns 3 calendar days",
        abs(float(cash.iloc[1]) - 3.65 / 100.0 * 3 / 365.0) < 1e-15 and miss == 0,
        "mon=%.8f" % float(cash.iloc[1]))

    # leg5: the incremental ledger reproduces the engine on a hand-built path
    d2 = pd.DatetimeIndex(["2021-01-04", "2021-01-05", "2021-01-06", "2021-01-07"])
    rp2 = pd.Series([0.0, 0.01, -0.02, 0.0], index=d2)
    rf2 = pd.Series(0.0, index=d2)
    k2 = pd.Series([0.5, 0.5, 0.2, 0.2], index=d2)
    st, rows = accrue({"inception": "2021-01-04", "nav": 1.0, "last_k": None},
                      list(d2), rp2, rp2 * 2, k2, rf2, {})
    want = 1.0 * (1.0 + 0.5 * 0.01) * (1.0 + 0.2 * -0.02 - 0.3 * COST_BP / 10000.0)
    chk("leg5 ledger matches hand path (incl |dk| cost)",
        abs(st["nav"] - want) < 1e-12, "got %.10f want %.10f" % (st["nav"], want))

    # leg6: k idempotent -- re-running the same bars adds nothing
    st2, rows2 = accrue(st, list(d2), rp2, rp2 * 2, k2, rf2, {})
    chk("leg6 accrual is idempotent by bar", len(rows2) == 0, "added=%d" % len(rows2))

    # leg7: idle capital earns the repo rate
    kz = pd.Series(0.5, index=d2)
    rfz = pd.Series(0.01 / 252.0, index=d2)
    st3, _ = accrue({"inception": "2021-01-04", "nav": 1.0, "last_k": None},
                    list(d2), pd.Series(0.0, index=d2), pd.Series(0.0, index=d2),
                    kz, rfz, {})
    # four bars (not three): the fixture has four dates, and the un-invested half is 1-k
    want3 = (1.0 + (1.0 - 0.5) * 0.01 / 252.0) ** len(d2)
    chk("leg7 cash leg accrues on the un-invested half",
        abs(st3["nav"] - want3) < 1e-12, "got %.10f want %.10f" % (st3["nav"], want3))

    # leg8: ticket weights sum to 1 and never overspend NAV
    sc = pd.Series({"AAA": 3.0, "BBB": 2.0, "CCC": 1.0})
    px = pd.Series({"AAA": 3.31, "BBB": 12.7, "CCC": 0.777})
    tk = build_ticket(sc, px, 0.20, 1_000_000.0, n_hold=3)
    tot_w = sum(r["weight"] for r in tk["order"]) + tk["cash_weight"]
    spent = sum(r["amount"] for r in tk["order"])
    chk("leg8 ticket weights sum to 1, spend <= NAV",
        abs(tot_w - 1.0) < 1e-4 and spent <= 1_000_000.0 + 1e-6 and
        abs(tk["book_amount"] + tk["cash_amount"] - 1_000_000.0) < 1e-6,
        "w=%.6f spent=%.2f cash=%.2f" % (tot_w, spent, tk["cash_amount"]))

    # leg9: whole lots only
    chk("leg9 ticket quantities are whole lots",
        all(r["shares"] is None or r["shares"] % LOT == 0 for r in tk["order"]))

    # leg10: a short universe yields no ticket rather than a partial one
    chk("leg10 insufficient picks -> no ticket",
        build_ticket(pd.Series({"AAA": 1.0}), px, 0.2, 1e6, n_hold=3) is None)

    # leg11: k in force lags the decision by exactly one bar
    sched2 = [(idx[5], 0.7, 0.3)]
    kv = in_force(sched2, idx)
    chk("leg11 decision applies from the next bar", bool(np.isnan(kv.iloc[5]))
        and abs(float(kv.iloc[6]) - 0.7) < 1e-12, "k5=%s k6=%.3f" % (kv.iloc[5], kv.iloc[6]))

    print("selftest:", "PASS %d/%d" % (ok, total) if ok == total else "FAIL %d/%d" % (ok, total))
    return 0 if ok == total else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()

    def arg(name, default, cast):
        for a in sys.argv:
            if a.startswith("--%s=" % name):
                return cast(a.split("=", 1)[1])
        return default

    beta = arg("beta", DEFAULT_BETA, float)
    nav = arg("nav", DEFAULT_NAV, float)
    inception = arg("inception", DEFAULT_INCEPTION, str)
    fresh = "--fresh-gate" in sys.argv
    if "--reset" in sys.argv:
        base_dir = (os.path.join(PATHS.results_dir, "etf_book_order_fresh") if fresh else OUT_DIR)
        for name in ("state.json", "ledger.jsonl"):
            p = os.path.join(base_dir, name)
            if os.path.exists(p):
                os.remove(p)
        print("reset: cleared state.json + ledger.jsonl in", base_dir)
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        return run(beta, nav, inception, fresh_gate=fresh)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())